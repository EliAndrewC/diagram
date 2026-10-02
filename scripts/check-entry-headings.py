#!/usr/bin/env python3
"""Every feature class's `Entry:` heading still RESOLVES - the half of feature 234 that is decidable.

WHY THIS IS GATED WHERE THE REPORT IS NOT. A modal that has drifted from its section is a judgment about
prose; a class pointing at a heading that no longer exists is not. It has no legitimate form, so it
fires on exactly the thing it names, which is this project's bar for gating a rule at all.

WHAT IT CATCHES. `interactive/sources.py` `research_questions()` lists the questions an `Entry:` names - since feature
301 by their FRAGMENT paths, since feature 303 `research/questions/NNNN-<slug>[.drawing].html` - and drops one that is not there, silently (before 301 it matched quoted headings by
prefix, with the same silence). The consequence is a "See references" list that goes
quietly empty on every map carrying that feature. `research/CLAUDE.md` already requires a rename to fix
its inbound class entries; this is the mechanism that sentence never had.

PROPHYLACTIC, AND SAYS SO. Measured 2026-09-12: 0 of 51 entries are broken - 50 resolve and one is the
declared silence. This enforces a rule with no current violation rather than fixing a live defect, and a
later audit should not read it as a bug fix.

THE ONE LEGITIMATE NON-MATCH is a section deliberately not written, in the form `fallow` already uses:
`research/contents.json#fields (no dedicated entry - recorded as silent)`. It is recognized EXPLICITLY, never by
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
    """The engine's registry and resolver, or None when this repository has no diagram skill.

    A repository without the skill has no class entries, so there is nothing for this check to be
    right or wrong about - that is a no-op, not a failure. The distinction matters because this runs
    at PUSH time against whatever tree it is given, including the fixture repositories
    `scripts/test-sync-with-main.sh` builds, which are a bare main and a clone and nothing else. A
    skill directory that EXISTS but will not import is a different thing and still raises.
    """
    if not (root / SKILL / "l7r").is_dir():
        return None
    skill = str(root / SKILL)
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive.classes import CLASSES
    from l7r.diagram.interactive.sources import RESEARCH_DIR, entry_fragments

    def unresolved(entry: str) -> list[str]:
        """The fragments an entry names that the record does not hold - or the entry itself, when it names none."""
        named = entry_fragments(entry)
        if not named:
            return [entry]
        return [f"research/questions/{n}" for n in named if not (Path(RESEARCH_DIR) / "questions" / n).is_file()]

    return CLASSES, unresolved


def broken(root: Path) -> list[str]:
    """Every class whose `Entry:` resolves to no research question and is not a declared silence."""
    loaded = _load(root)
    if loaded is None:
        return []
    classes, unresolved = loaded
    bad = []
    for key, fc in sorted(classes.items()):
        if SILENT.search(fc.entry):
            continue
        missing = unresolved(fc.entry)
        if missing:
            bad.append(f"{key}: Entry names {', '.join(missing)}")
    return bad


def selftest() -> int:
    """Prove the check still BITES - a checker that cannot fail is worth nothing, which is why all three
    of its siblings at the push call site run one. Fires on a heading that does not exist; stays quiet on
    a real one; and does NOT let the declared-silence form swallow a broken heading."""
    root = Path(__file__).resolve().parent.parent
    real = "research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html"
    # the FORM half always runs: telling a declared silence from a broken heading is this file's own
    # logic and owes nothing to the engine
    assert SILENT.search("research/contents.json#fields (no dedicated entry - recorded as silent)"), "the declared silence must be recognized"
    assert not SILENT.search(real), "a real entry must not read as a declared silence"
    assert not SILENT.search("research/questions/0999-not-there.html"), "a broken pointer must not read as a declared silence"
    loaded = _load(root)
    if loaded is None:
        print("check-entry-headings selftest ok (form only - no diagram skill in this tree to resolve against)")
        return 0
    _classes, unresolved = loaded
    assert not unresolved(real), "the checker cannot see a question that exists - its matching surface is dead"
    assert unresolved("research/questions/0999-a-question-that-does-not-exist.html"), "a broken pointer must be named"
    assert unresolved("research/contents.json#field-archetypes - 'a page and a heading, the form retired by feature 301'"), "an entry naming no fragment is broken"
    print("check-entry-headings selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    root = Path(argv[0] if argv else ".").resolve()
    bad = broken(root)
    if bad:
        print("a class entry names a research question the record does not hold:", file=sys.stderr)
        for line in bad:
            print(f"  {line}", file=sys.stderr)
        print("\nRename an anchor and you owe its inbound links - `research/CLAUDE.md` says so and this is what\nchecks it. Fix the `Entry:` tag (`make fragment-move` rewrites it for you), or restore the question. A section deliberately not written is written\nas `research/contents.json#<section> (no dedicated entry - recorded as silent)`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
