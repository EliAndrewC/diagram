#!/usr/bin/env python3
"""The measurements behind this spec - one subcommand each, re-runnable.

    python3 specs/260-mechanical-vocabulary-candidates/measure.py R1

R1 what "every word with no glossary line" actually raises on one entry (the shape the GM was offered)
R2 rarity within the record's own corpus: the candidate count at each cutoff, and what it catches
R3 what a word-level filter cannot reach - the multi-word terms and the record-common ones
"""

from __future__ import annotations

import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.normpath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram", "research"))
#: The entry all three of feature 259's runs checked, so this feature measures the same one.
ENTRY = ("ways", "010-how-far-past-the-bank-does-a-bridge-land")
#: What feature 259's three runs actually did with this entry (specs/259 R5), split the way the
#: question demands: the CORE every run proposed, the TAIL that varied between runs - which is the
#: variance this feature exists to remove - and the one term every run DISMISSED as defined inline.
#: The headline "n of 12" the first draft used counted the dismissal as a term to catch, and buried
#: the tail inside a core that was never the problem.
CORE = ("girder", "carried deck", "footplank", "stringer", "spread footing", "backwall", "wingwall",
        "superstructure")
TAIL = ("nrcs", "out-to-out", "embankment")
DISMISSED = ("obliquity",)
KNOWN = CORE + TAIL
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


def visible(markup: str) -> str:
    """What a reader meets: comments are for the session, tags are not words."""
    return re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", markup, flags=re.S))


def read(*parts: str) -> str:
    with open(os.path.join(RECORD, *parts), encoding="utf-8") as fh:
        return fh.read()


def entry_words() -> list[str]:
    text = visible(read(ENTRY[0], ENTRY[1] + ".html") + read(ENTRY[0], ENTRY[1] + ".notes.html"))
    return sorted({w.lower() for w in _WORD.findall(text)})


def defined() -> set[str]:
    return {line.split("\t")[0] for line in read("assets", "glossary-variants.txt").splitlines()}


def fragments() -> list[str]:
    """Every question fragment of the record - the corpus rarity is measured against."""
    out = []
    for base, _dirs, names in os.walk(RECORD):
        if "citations" in base or base.endswith("assets"):
            continue
        out += [os.path.join(base, n) for n in names
                if n.endswith(".html") and not n.startswith("_") and base != RECORD]
    return sorted(out)


def doc_frequency() -> collections.Counter:
    freq: collections.Counter = collections.Counter()
    for path in fragments():
        with open(path, encoding="utf-8") as fh:
            freq.update({w.lower() for w in _WORD.findall(visible(fh.read()))})
    return freq


def r1() -> None:
    """The shape as it was offered to the GM, measured on the entry it was offered about."""
    words, known = entry_words(), defined()
    undefined = [w for w in words if w not in known]
    print(f"  the entry's distinct words:            {len(words)}")
    print(f"  with no line in the variant index:     {len(undefined)}")
    print(f"\n  the first twenty: {undefined[:20]}")
    print("\n  A LIST OF THIS LENGTH IS NOT A LIST. Ordinary English is not in a glossary, so 'every")
    print("  word with no glossary line' is nearly every word. The filter has to be something else.")


def caught_by(term: str, candidates: set[str]) -> str | None:
    """The candidate that would put this term in front of the model - itself, or its plural.

    No lemmatizer: the record writes `stringers` and `wingwalls` in the prose and the term is the
    singular, so a coverage count that compares strings exactly under-reports what the list catches.
    """
    for form in (term, term + "s", term + "es", term.rstrip("y") + "ies" if term.endswith("y") else term):
        if form in candidates:
            return form
    return None


def r2() -> None:
    """Rarity within the record's own corpus - no shipped word list, nothing to maintain."""
    words, known, freq = entry_words(), defined(), doc_frequency()
    corpus = len(fragments())
    print(f"  corpus: {corpus} question fragments, {len(freq)} distinct words\n")
    for cut in (1, 2, 3, 5, 10, 20):
        cands = set(w for w in words if w not in known and freq[w] <= cut)
        core = sorted(k for k in CORE if caught_by(k, cands))
        tail = sorted(k for k in TAIL if caught_by(k, cands))
        print(f"  in <= {cut:>2} fragments: {len(cands):>3} candidates | core {len(core)}/{len(CORE)} "
              f"| TAIL {len(tail)}/{len(TAIL)} {tail} | dismissed-inline caught: "
              f"{sorted(d for d in DISMISSED if caught_by(d, cands))}")


def r3() -> None:
    """What a word-level rarity filter cannot reach, named rather than left to be discovered."""
    words, known, freq = entry_words(), defined(), doc_frequency()
    cands = {w for w in words if w not in known and freq[w] <= 2}
    print("  of the terms feature 259's three runs proposed:")
    for term in KNOWN:
        form = caught_by(term, cands)
        if form:
            if form != term:
                print(f"    {term:<16} raised as {form!r} - the prose's own form, which is what the model is handed")
            continue
        if " " in term:
            why = "MULTI-WORD - a word-level filter cannot see the phrase"
        elif term in known:
            why = "already defined in the glossary"
        elif term not in words and term.rstrip("s") + "s" in words or term + "s" in words:
            why = f"present only as a plural ({term}s) - no lemmatizer here"
        else:
            why = f"common in the record ({freq[term]} fragments) though not in the glossary"
        print(f"    {term:<16} not raised: {why}")


def main(argv: list[str]) -> int:
    which = {"R1": r1, "R2": r2, "R3": r3}
    if len(argv) != 2 or argv[1].upper() not in which:
        print(f"usage: {os.path.basename(__file__)} R1|R2|R3", file=sys.stderr)
        return 2
    which[argv[1].upper()]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
