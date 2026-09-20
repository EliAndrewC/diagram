#!/usr/bin/env python3
"""What a pattern can find on a research page, listed for `record-format` (feature 251, FR-005).

WHY. `record-format` reads a page as its casual reader does and reports three things that reader should
not meet: vocabulary the glossary does not define, visible text addressed to a session, and the
document's own history (feature 209, GM 2026-09-07). Two of those have a mechanical half - a `Grounds:`
field, a task id, a module path and a run of kanji are found by a regular expression, exactly and for
no tokens - and the census of feature 251 (research R1) measured `record-format` as the second most
expensive check per run, nearly all of it input re-read turn after turn. So the listing is done here
and handed over; the agent confirms or dismisses each line and keeps what no pattern can find: a
history passage, an instruction to a future session, a hard word in plain English.

WHAT IT READS. The page's VISIBLE text only - HTML comments are where session notes belong, so what is
inside one is already right and is never listed. A vocabulary candidate the glossary covers, as a term
or as a variant, is dropped: every occurrence of it is already a hover tooltip.

This decides nothing and never edits. A line here is a CANDIDATE: `<code>` holds source keys as well as
engine identifiers, and an `<em>` holds a quoted ruling as often as a Japanese word.

THE CANDIDATE WORDS (feature 260, the GM's choice of 2026-09-20). `record-format` was doing two jobs at
once - NOTICING which words a reader might not know, and JUDGING them - and the first is why its output
wandered: three runs on one entry agreed on eight terms and differed in the tail, in both conditions
(`specs/259-*/research.md` R5). The noticing is mechanical now that the glossary is an index, so it
happens here and the model rules on a list.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import functools
import re
from collections.abc import Mapping
import os
import sys

GLOSSARY = ".claude/skills/diagram/l7r/diagram/interactive/assets/glossary.json"
RESEARCH = ".claude/skills/diagram/research"

#: (label, pattern) over a section's visible text - the session-note shapes `record-format` names.
SESSION_NOTES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("field", re.compile(r"\b(?:Grounds|Evidence)\s*:")),
    ("feature number", re.compile(r"\b[Ff]eature\s+\d{2,3}\b|\bF\d{3}\b")),
    ("task id", re.compile(r"\bT\d{2,3}\b")),
    ("spec path", re.compile(r"\bspecs/\d{3}-[\w-]+")),
    # a hyphenated target, or one of the bare ones - "make sure" in a quoted ruling is not a make target
    ("make target", re.compile(r"\bmake\s+(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)+|quick|done|maps|map|audit|claim|tick|verify|soak)\b")),
    ("file path", re.compile(r"(?<![\w/.:-])(?:[\w.-]+/)+[\w.-]+\.(?:py|sh|json|md)\b|\b[\w-]+\.(?:py|sh)\b")),
    ("fetch verdict", re.compile(r"\b(?:SUMMARY-ONLY|UNFETCHABLE|NOT-FOUND|CONTRADICTED|NOT-READABLE|READ)\b|\bnot re-sourced\b|\bleftover\b")),
)
IDENTIFIER = re.compile(r"^[A-Za-z_][\w.]*(?:\(\))?$")
CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯]{2,}")
#: a Latin binomial is recognized only where the page italicizes it - as plain text the shape matches
#: any capitalized word followed by a lower-case one, and a noisy candidate costs the agent tokens.
BINOMIAL = re.compile(r"[A-Z][a-z]{3,} [a-z]{4,}")


def strip_comments(markup: str) -> str:
    return re.sub(r"<!--.*?-->", "", markup, flags=re.S)


def text_of(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def sections(markup: str) -> list[tuple[str, str]]:
    """(heading, body markup) per `<h2>`/`<h3>`; what precedes the first heading is `(top)`."""
    body = strip_comments(re.sub(r"<(script|style)\b.*?</\1>", "", markup, flags=re.S | re.I))
    parts = re.split(r"(<h[23]\b[^>]*>.*?</h[23]>)", body, flags=re.S | re.I)
    out, heading = [], "(top)"
    for part in parts:
        if re.match(r"<h[23]\b", part, re.I):
            heading = text_of(part)
        elif part.strip():
            out.append((heading, part))
    return out


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(". ", 0, start), text.rfind("? ", 0, start)) + 1
    right = text.find(". ", end)
    return text[left : right + 1 if right >= 0 else len(text)].strip()[:240]


def known_terms(glossary: dict) -> set[str]:
    """Every glossary term and variant, case-folded."""
    known: set[str] = set()
    for term, entry in glossary.items():
        known.add(term.casefold())
        known.update(str(v).casefold() for v in (entry.get("variants") or []))
    return known


def session_notes(markup: str) -> list[dict]:
    text = text_of(markup)
    found = [{"class": "SESSION NOTE", "label": label, "match": m.group(0), "sentence": sentence_around(text, m.start(), m.end())} for label, pat in SESSION_NOTES for m in pat.finditer(text)]
    for m in re.finditer(r"<code>([^<]+)</code>", markup):
        inner = html.unescape(m.group(1)).strip()
        linked = re.search(r"<a\b[^>]*>\s*$", markup[: m.start()]) is not None
        if not linked and IDENTIFIER.match(inner) and ("_" in inner or "." in inner or inner.endswith("()")):
            at = text.find(inner)
            found.append({"class": "SESSION NOTE", "label": "engine identifier", "match": inner, "sentence": sentence_around(text, max(at, 0), max(at, 0) + len(inner))})
    return found


#: HOW RARE A WORD HAS TO BE (feature 260, FR-002). Measured over the whole curve in specs/260 R2, and
#: counted the way the question demands: of the THREE terms whose presence VARIED between three recorded
#: `record-format` runs of one entry - the variance this pass exists to remove - a cutoff of 2 raises 2,
#: in a list of 34 words; it also raises 6 of the 8 terms every run proposed anyway. At 3 the list is 41
#: for the same catch, at 20 it is 101 for the same catch. The catch plateaus at once while the list
#: keeps growing, so 2 is the cheapest cutoff that catches what this filter can catch.
RARE_IN_AT_MOST = 2
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


def rare_words(text: str, defined: set[str], frequency: Mapping[str, int],
               cutoff: int = RARE_IN_AT_MOST, keys: set[str] | None = None) -> list[tuple[str, int]]:
    """The words of one entry that the glossary does not define and the record rarely uses.

    PURE, so its test needs no filesystem: the three things it knows - what is defined, how common a
    word is, and which tokens are citation keys - are passed in.

    WHY RARITY AND NOT "not in the glossary" (R1): the entry has 324 distinct words and 314 of them
    have no glossary line, because ordinary English is not in a glossary. Rarity in the record's OWN
    corpus separates the two without shipping a word list to maintain.

    WHAT IT CANNOT REACH, which its caller's contract has to say (R3): a MULTI-WORD term (`carried
    deck`), because this is word-level; and a word the record uses often though the glossary does not
    define it (`embankment`, 23 fragments). The list is a floor under the model's noticing, never a
    replacement for it.
    """
    out: dict[str, int] = {}
    for raw in _WORD.findall(text):
        word = raw.lower()
        seen = frequency.get(word, 0)
        # FAILS CLOSED. A word the corpus has never seen is not rare - it means the corpus does not
        # contain this entry, and then the filter cannot judge rarity at all. Raising everything in
        # that case is exactly R1's failure (314 of 324 words), so it raises nothing instead: a
        # candidate list is evidence, and a list built from no evidence is worse than none.
        if not seen or word in defined or word in (keys or set()) or seen > cutoff:
            continue
        out[word] = seen
    return sorted(out.items())


@functools.cache
def defined_words(record_dir: str) -> set[str]:
    """Every variant the glossary defines, from the index feature 259 derives."""
    try:
        with open(os.path.join(record_dir, "assets", "glossary-variants.txt"), encoding="utf-8") as fh:
            return {line.split("\t")[0] for line in fh if line.strip()}
    except OSError:
        return set()


@functools.cache
def registry_keys(record_dir: str) -> set[str]:
    """The source keys of `SOURCES.html` - identifiers, not words a reader is asked to know.

    A FLOOR, not a filter that fires today: measured over the whole record (specs/260 R3), the rarity
    cutoff and the word regex already keep every key off every list, so this removes nothing now. It is
    here for the key rare enough to survive the cutoff.
    """
    try:
        with open(os.path.join(record_dir, "SOURCES.html"), encoding="utf-8") as fh:
            return {m.group(1) for m in re.finditer(r'<h3 id="([a-z0-9][a-z0-9-]*)"', fh.read())}
    except OSError:
        return set()


@functools.cache
def corpus_frequency(record_dir: str) -> dict[str, int]:
    """How many of the record's question fragments each word appears in.

    The corpus is derived at run time from the fragments on disk - no file is shipped and none is kept
    in step. Measured cost is in specs/260 R4; the bar it is held to is FR-010's five seconds.
    """
    freq: dict[str, int] = {}
    for base, _dirs, names in os.walk(record_dir):
        if "citations" in base or base.endswith("assets") or base == record_dir:
            continue
        for name in names:
            if not name.endswith(".html") or name.startswith("_"):
                continue
            with open(os.path.join(base, name), encoding="utf-8") as fh:
                body = text_of(strip_comments(fh.read()))
            for word in {w.lower() for w in _WORD.findall(body)}:
                freq[word] = freq.get(word, 0) + 1
    return freq


def vocabulary(markup: str, known: set[str]) -> list[dict]:
    text = text_of(markup)
    seen: set[str] = set()
    found: list[dict] = []

    def add(label: str, term: str) -> None:
        key = term.casefold()
        if key in seen or key in known or not term:
            return
        seen.add(key)
        at = text.find(term)
        found.append({"class": "VOCABULARY", "label": label, "match": term, "sentence": sentence_around(text, max(at, 0), max(at, 0) + len(term))})

    for m in re.finditer(r"<(em|i)\b[^>]*>(.*?)</\1>", markup, flags=re.S | re.I):
        term = text_of(m.group(2))
        if 0 < len(term.split()) <= 3 and not re.search(r"[\"“”.:!?]", term):
            add("binomial" if BINOMIAL.fullmatch(term) else "italic term", term)
    for m in CJK.finditer(text):
        add("CJK term", m.group(0))
    return found


def prepass(markup: str, glossary: dict, record_dir: str | None = None) -> list[dict]:
    """Per section: its heading, the candidate lines, and the RARE WORDS the model must rule on.

    `record_dir` is what the rare-word pass needs (the variant index, the registry keys, the corpus);
    without it the section carries no `rare` list, which is what keeps this callable on a string.
    """
    known = known_terms(glossary)
    defined = defined_words(record_dir) if record_dir else set()
    keys = registry_keys(record_dir) if record_dir else set()
    freq = corpus_frequency(record_dir) if record_dir else {}
    notes = notes_index(record_dir)
    out = []
    for heading, body in sections(markup):
        # THE SAME TEXT THE CHECK READS (feature 260). `record-format` is handed the question fragment
        # AND its notes, so a candidate list drawn from the question alone would leave every term that
        # appears only in a quoted passage unraised - and those are the technical ones.
        scanned = without_code(body) + " " + notes.get(_slug(heading), "") if record_dir else ""
        out.append({
            "section": heading,
            "items": session_notes(body) + vocabulary(body, known),
            "rare": rare_words(scanned, defined, freq, keys=keys) if record_dir else [],
        })
    return out


def without_code(markup: str) -> str:
    """Visible text with `<code>` spans removed - they carry keys and identifiers, not words a reader
    is asked to know (FR-004). Measured on the entry this feature was built against, it removes
    nothing: the shards a key breaks into (`nrcs-ts`, `q-abutments`) are already over the rarity
    cutoff. It is a floor against a key rare enough to survive that cutoff, not a filter that fires
    today, and the spec says so rather than claiming a saving it does not make."""
    return text_of(re.sub(r"<code\b[^>]*>.*?</code>", " ", markup, flags=re.S))


@functools.cache
def notes_index(record_dir: str | None) -> dict[str, str]:
    """{question slug: the visible text of its notes}, built ONCE.

    Built once and asked per section, not walked per section (constitution X clause 15). The first
    version walked the record for every heading: measured, that made a sweep over all 321 entries take
    6.97 s where the index makes it 0.4 s - the same per-candidate-scan-of-unchanging-ground shape this
    engine's performance doc names as the only slow shape it has ever found.
    """
    if not record_dir:
        return {}
    out: dict[str, str] = {}
    for base, _dirs, names in os.walk(record_dir):
        if "citations" in base or base == record_dir:
            continue
        for name in names:
            if not name.endswith(".notes.html"):
                continue
            with open(os.path.join(base, name), encoding="utf-8") as fh:
                out[name.split("-", 1)[-1][: -len(".notes.html")]] = without_code(strip_comments(fh.read()))
    return out


def render(page: str, listing: list[dict]) -> str:
    total = sum(len(s["items"]) for s in listing)
    rare = sum(len(s.get("rare", ())) for s in listing)
    lines = [f"record-prepass: {page} - {len(listing)} sections, {total} candidates (each is for record-format to confirm or dismiss)"]
    for sec in listing:
        if not sec["items"]:
            continue
        lines.append(f"## {sec['section']}")
        for it in sec["items"]:
            lines.append(f"  {it['class']} [{it['label']}] {it['match']!r} - {it['sentence']}")
    if rare:
        lines.append("")
        lines.append(f"## WORDS TO RULE ON ({rare}) - feature 260")
        lines.append("")
        lines.append("Every word below is in this entry, is defined by no glossary term, and appears in at most")
        lines.append(f"{RARE_IN_AT_MOST} of the record's question fragments (the count is beside each one). `record-format` rules")
        lines.append("on EVERY one of them and says which verdict each got. The list is a floor, not the question:")
        lines.append("it cannot see a MULTI-WORD term, and it does not raise a word the record uses often though")
        lines.append("the glossary does not define it - so anything else you notice is reported too.")
        for sec in listing:
            if not sec.get("rare"):
                continue
            lines.append(f"### {sec['section']}")
            lines.append("  " + ", ".join(f"{word} ({n})" for word, n in sec["rare"]))
    return "\n".join(lines)


def _slug(heading: str) -> str:
    """A heading's own id, as the record writes it - which is what a fragment is named for."""
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", heading).lower())).strip("-")


def _fragments(page: str, section: str, root: str) -> list[str]:
    """The per-entry files a check should read (feature 258, spec FR-023).

    A recorded `record-format` run spent 88% of everything that entered its context on one research
    page, to check one entry (spec research R3). The prepass is what the dispatch is built from, so it
    is where the fragment paths belong.
    """
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _hm_record import fragments_for  # noqa: PLC0415 - one call, and only when the page is split

    return fragments_for(page, section, str(pathlib.Path(root).resolve()))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="a research page name: hamlets, cities/tango, citations/hamlets, SOURCES")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", default="")
    ap.add_argument("--section", default="", help="only the sections whose heading contains this text")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    name = args.page.removesuffix(".html")
    path = root / RESEARCH / f"{name}.html"
    if not path.is_file():
        print(f"record-prepass: no such page - wanted {path}", file=sys.stderr)
        return 2
    gloss_path = root / GLOSSARY
    glossary = json.loads(gloss_path.read_text(encoding="utf-8")) if gloss_path.is_file() else {}
    fragments = _fragments(args.page, args.section, args.root)
    # ONE flag, two matchers (feature 258): `--section` names a question the way it reads ("the bund
    # runs along...") or the way its file spells it ("040"). The heading filter alone answers the first
    # and finds nothing for the second, which is the form the fragment paths are in.
    wanted_ids = {pathlib.Path(f).name.split("-", 1)[1][: -len(".html")] for f in fragments
                  if not f.endswith(".notes.html")}
    listing = [s for s in prepass(path.read_text(encoding="utf-8"), glossary, str(root / RESEARCH))
               if args.section.casefold() in s["section"].casefold() or _slug(s["section"]) in wanted_ids]

    print(render(name, listing))
    if fragments:
        print("\n## What to hand the check (feature 258)\n")
        print("The fragments these sections are written in - read THESE, not the assembled page:\n")
        print("\n".join(f"  {f}" for f in fragments))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({"page": name, "sections": listing}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
