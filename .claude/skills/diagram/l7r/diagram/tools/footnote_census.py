"""Count the record's footnotes BY KIND - the number that says what is owed (feature 235, GM 2026-09-12).

The GM, on finding that eighteen notes marked "no publicly readable source" were nothing of the kind:
*"if we're counting things that are not actually problems in a category that is meant to denote problems, then
we're just gonna keep getting confused."*

Nothing in this project counted footnotes before this. `make notes-census` counts MAP FEATURES and is a
different thing entirely; every footnote figure quoted while feature 232 ran was assembled by hand, and three
of those hand-built tables turned out to be wrong - which is the argument for a tool rather than a habit.

WHAT THE FOUR NUMBERS MEAN, and only one of them is a backlog:

- `citation`    - a key, a link and the quoted passage. Nothing owed.
- `grounds`     - `no source is owed: <reason>`. Nothing to find, so nothing owed.
- `absence`     - `no publicly readable source (searched ...)`. **THIS IS THE BACKLOG**, and the only number
                  anybody has to act on.
- `settled`     - an absence searched to exhaustion by two dated passes. Owed nothing further until something
                  changes what can be read.

The classifier is the engine's own `interactive.citations.footnote_form` - the one the gate reads - so the
census and the gate cannot drift into disagreeing about what a note is.
"""

from __future__ import annotations

import argparse
import collections
import sys
from collections.abc import Callable

from l7r.diagram.interactive.citations import footnote_form, is_settled
from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.sources import RESEARCH_DIR, canon_keys

KINDS = ("citation", "grounds", "absence", "settled")
#: What the census needs of a classifier: a note's body in, its form out. Passed in rather than reached for, so a
#: test can count a page of its own making without a registry behind it.
Classifier = Callable[[str], str | None]


def kinds_of(bodies: list[str], form: Classifier) -> collections.Counter[str]:
    """The kind of every footnote among `bodies`. `form` is the gate's own classifier."""
    counted: collections.Counter[str] = collections.Counter()
    for body in bodies:
        kind = form(body)
        if kind == "absence" and is_settled(body):
            kind = "settled"
        counted[kind if kind in KINDS else "malformed"] += 1
    return counted


def census(form: Classifier, research_dir: str = RESEARCH_DIR) -> dict[str, collections.Counter[str]]:
    """Per section of each half (feature 303: the record's sections, `research/contents.json`), and under the key
    `TOTAL`, how many footnotes of each kind the record carries."""
    record = store.load(research_dir)
    per: dict[str, collections.Counter[str]] = {}
    total: collections.Counter[str] = collections.Counter()
    for page in record.pages():
        home = record.question_of(page).home
        assert home is not None
        row = f"{page.half}: " + " / ".join(s.title for s in home.path())
        counted = kinds_of(list(store.page_notes(page.file, research_dir).values()), form)
        per.setdefault(row, collections.Counter()).update(counted)
        total.update(counted)
    per = dict(sorted(per.items()))
    per["TOTAL"] = total
    return per


def render(per: dict[str, collections.Counter[str]]) -> str:
    """The report, widest column first, with the backlog called what it is."""
    rows = [(name, c) for name, c in per.items() if name != "TOTAL"]
    width = max([len(n) for n, _ in rows] + [5])
    head = f"{'section':<{width}}  {'cited':>6}{'grounds':>9}{'ABSENT':>8}{'settled':>9}"
    lines = [head, "-" * len(head)]
    for name, c in rows:
        lines.append(f"{name:<{width}}  {c['citation']:>6}{c['grounds']:>9}{c['absence']:>8}{c['settled']:>9}")
    t = per["TOTAL"]
    lines += ["-" * len(head), f"{'TOTAL':<{width}}  {t['citation']:>6}{t['grounds']:>9}{t['absence']:>8}{t['settled']:>9}"]
    if t["malformed"]:
        lines.append(f"\nMALFORMED: {t['malformed']} footnote(s) match no form - the gate will name them")
    lines.append(f"\nThe backlog is ABSENT: {t['absence']}. The other three columns owe nothing.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="count the record's footnotes by kind; the ABSENT column is the backlog")
    ap.parse_args(argv)
    canon = canon_keys()
    print(render(census(lambda body: footnote_form(body, canon))))
    return 0


if __name__ == "__main__":  # pragma: no cover - the module is run through `make`
    sys.exit(main())
