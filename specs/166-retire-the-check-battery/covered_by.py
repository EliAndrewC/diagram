#!/usr/bin/env python3
"""Is a placer guarantee ALREADY carried by a test outside the check battery? (feature 166)

    python3 specs/166-retire-the-check-battery/covered_by.py <file> <line> <old> <new> [<test paths>]

WHY. The battery's 147 rules have to land somewhere, and the assumption that each needs a NEW test is
expensive and often wrong: the placers have accumulated their own suites, and a rule the battery states
may already be guarded by a test of the code that guarantees it. The spec's destination list allows
exactly that - "deliberately dropped, with a recorded reason - redundant with a test the placer already
has" - but "already has" is a claim, and this is how it is checked rather than asserted.

THE METHOD IS MUTATION, because nothing else answers the question. Break the placer's guarantee, run the
suite WITHOUT the check battery's own tests, and see whether anything goes red. Red means some existing
test already carries the rule and the check can be dropped against it by name. Green means the rule is
carried by the battery alone, and retiring it needs a new test written first.

The battery's own tests are excluded deliberately: they are what is being retired, so a rule they alone
catch is exactly a rule with no home yet.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parents[2] / ".claude/skills/diagram"


def probe(rel: str, old: str, new: str, paths: list[str] | None = None) -> tuple[bool, str]:
    """(is the guarantee already covered, what went red). Restores the file whatever happens."""
    f = SKILL / rel
    orig = f.read_text()
    if old not in orig:
        return False, f"ANCHOR MISS in {rel}: {old[:70]!r}"
    if orig.count(old) > 1:
        return False, f"AMBIGUOUS ANCHOR in {rel} ({orig.count(old)} matches) - narrow it, or the mutation lands somewhere the test never calls"
    try:
        f.write_text(orig.replace(old, new, 1))
        cmd = ["python3", "-m", "pytest", "-x", "-q", "--no-header", "-p", "no:randomly", "--no-cov",
               *(paths or ["tests"]), "--ignore=tests/check_village", "--ignore=tests/gate"]
        r = subprocess.run(cmd, cwd=SKILL, capture_output=True, text=True, timeout=900)
        red = r.returncode != 0
        who = ""
        for ln in r.stdout.splitlines():
            if ln.startswith("FAILED") or "failed" in ln:
                who = ln.strip()[:160]
                break
        return red, who
    finally:
        f.write_text(orig)


if __name__ == "__main__":
    rel, old, new = sys.argv[1], sys.argv[3], sys.argv[4]
    covered, who = probe(rel, old, new, sys.argv[5:] or None)
    print(("COVERED    " if covered else "NOT COVERED") + f"  {who}")
