#!/usr/bin/env python3
"""Every feature class's `Entry:` heading still RESOLVES - the half of feature 234 that is decidable.

WHY THIS IS GATED WHERE THE REPORT IS NOT. A modal that has drifted from its section is a judgment about
prose; a class pointing at a heading that no longer exists is not. It has no legitimate form, so it
fires on exactly the thing it names, which is this project's bar for gating a rule at all.

WHAT IT CATCHES. `interactive/sources.py` `research_questions()` matches an `Entry:` heading by prefix
and returns `[]` when nothing matches - silently. The consequence is a "See references" list that goes
quietly empty on every map carrying that feature. `research/CLAUDE.md` already requires a rename to fix
its inbound class entries; this is the mechanism that sentence never had.

PROPHYLACTIC, AND SAYS SO. Measured 2026-09-12: 0 of 51 entries are broken - 50 resolve and one is the
declared silence. This enforces a rule with no current violation rather than fixing a live defect, and a
later audit should not read it as a bug fix.

THE ONE LEGITIMATE NON-MATCH is a section deliberately not written, in the form `fallow` already uses:
`research/fields.html (no dedicated entry - recorded as silent)`. It is recognized EXPLICITLY, never by
the absence of a match, so a BROKEN heading and a DECLARED silence cannot be confused - and `make audit`
enumerates every entry taking it, because a carve-out nobody can list is one nobody revisits.

RUN AT THE GATE AND AT THE PUSH, like `check-file-scale.py`. The gate alone would not do: a heading
breaks when a research page is renamed, and a research-page-only delta owes no gate at all
(`gate-stamp.py` SKIP_ONLY_AREAS), so a gate-only check would surface the breakage as an inherited red
on the next session's unrelated work.

Usage: check-entry-headings.py [ROOT] | --selftest
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL = ".claude/skills/diagram"
#: the declared-silence form - a section deliberately not written, recognized rather than inferred
SILENT = re.compile(r"\(no dedicated entry\s*-\s*recorded as silent\)", re.I)


def _load(root: Path):  # noqa: ANN202
    skill = str(root / SKILL)
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive.classes import CLASSES
    from l7r.diagram.interactive.sources import research_questions

    return CLASSES, research_questions


def broken(root: Path) -> list[str]:
    """Every class whose `Entry:` resolves to no research question and is not a declared silence."""
    classes, research_questions = _load(root)
    bad = []
    for key, fc in sorted(classes.items()):
        if SILENT.search(fc.entry):
            continue
        if not research_questions(fc.entry):
            bad.append(f"{key}: Entry: {fc.entry}")
    return bad


def selftest() -> int:
    """Prove the check still BITES - a checker that cannot fail is worth nothing, which is why all three
    of its siblings at the push call site run one. Fires on a heading that does not exist; stays quiet on
    a real one; and does NOT let the declared-silence form swallow a broken heading."""
    root = Path(__file__).resolve().parent.parent
    _classes, research_questions = _load(root)
    real = "research/archetypes.html - 'What stands on a dike-pond hamlet that a paddy hamlet lacks?'"
    assert research_questions(real), "the checker cannot see a heading that exists - its matching surface is dead"
    assert not research_questions("research/archetypes.html - 'A heading that does not exist at all'"), "a broken heading must resolve to nothing"
    assert SILENT.search("research/fields.html (no dedicated entry - recorded as silent)"), "the declared silence must be recognized"
    assert not SILENT.search(real), "a real entry must not read as a declared silence"
    assert not SILENT.search("research/fields.html - 'A heading that does not exist at all'"), "a broken heading must not read as a declared silence"
    print("check-entry-headings selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    root = Path(argv[0] if argv else ".").resolve()
    bad = broken(root)
    if bad:
        print("a class entry names a research heading that no longer resolves:", file=sys.stderr)
        for line in bad:
            print(f"  {line}", file=sys.stderr)
        print("\nRename an anchor and you owe its inbound links - `research/CLAUDE.md` says so and this is what\nchecks it. Fix the `Entry:` tag, or restore the heading. A section deliberately not written is written\nas `research/<file>.html (no dedicated entry - recorded as silent)`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
