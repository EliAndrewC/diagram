#!/usr/bin/env python3
"""Retire one gate check by name, completely (feature 166).

    python3 specs/166-retire-the-check-battery/retire_check.py <check> [<check> ...] [--dry-run]

WHY THIS EXISTS. Feature 146 established what "delete a check" actually means, the hard way: *"Stubbing
the call is not removing the check; the computation above it usually has no other consumer."* Doing that
147 times by hand is 147 chances to leave a segment body computing inputs for a check that no longer
exists, or to leave a name in the pin, or to leave a frozen fixture pinned to nothing. So the mechanical
half is written once and the judgment half - what replaces the rule - stays with a person.

WHAT IT TOUCHES, and it refuses rather than guesses if any of it looks unfamiliar:

  1. the `check("<name>", ...)` call, and the segment function if that call was its only live check;
  2. the name's row in `tests/fixtures/gate_check_names.json`;
  3. the segment's row in `tests/fixtures/registry_legacy_rows.json` (or its `checks` entry when the
     segment survives) - the frozen oracle feature 109 left, which is edited BY HAND per row and never
     regenerated, so this edits exactly the rows it must and says which;
  4. frozen negative fixtures in `pool/regressions/` whose `_regression.fires` names ONLY this check.

WHAT IT DOES NOT TOUCH: tests. A test that names a retired check is a judgment call - it may be testing
the check (delete it) or the placer through it (rewrite it) - and this tool will not decide that. It
prints them for the session to handle.
"""

from __future__ import annotations

import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram"))


def segment_of(check: str) -> tuple[str, str] | None:
    """(file, function name) of the segment that emits `check`, or None."""
    sys.path.insert(0, SKILL)
    from l7r.diagram.check_village import registry as reg

    for s in reg.GATE_SEGMENTS:
        if check in s.checks:
            for f in sorted(glob.glob(os.path.join(SKILL, "l7r/diagram/check_village/segments_*.py"))):
                src = open(f, encoding="utf-8").read()
                for node in ast.parse(src).body:
                    if isinstance(node, ast.FunctionDef) and node.name == s.fn.__name__:
                        return f, node.name
    return None


def plan_for(check: str) -> dict:
    """What retiring this check would touch. Read-only."""
    out: dict = {"check": check, "segment": None, "other_checks_in_segment": [], "fixtures": [], "tests": []}
    seg = segment_of(check)
    if seg:
        f, name = seg
        out["segment"] = (os.path.relpath(f, SKILL), name)
        sys.path.insert(0, SKILL)
        from l7r.diagram.check_village import registry as reg

        for s in reg.GATE_SEGMENTS:
            if s.fn.__name__ == name:
                out["other_checks_in_segment"] = sorted(set(s.checks) - {check})
    for p in sorted(glob.glob(os.path.join(SKILL, "pool/regressions/*.json"))):
        fires = (json.load(open(p, encoding="utf-8")).get("_regression") or {}).get("fires") or []
        if fires and set(fires) == {check}:
            out["fixtures"].append(os.path.relpath(p, SKILL))
    for dp, _dn, fn in os.walk(os.path.join(SKILL, "tests")):
        if "__pycache__" in dp:
            continue
        for f in fn:
            if f.endswith(".py") and check in open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read():
                out["tests"].append(os.path.relpath(os.path.join(dp, f), SKILL))
    return out


def apply_for(check: str) -> list[str]:
    """Do the mechanical retirement. Returns what changed. Refuses rather than guesses."""
    done: list[str] = []
    p = plan_for(check)
    if not p["segment"]:
        return [f"NO SEGMENT emits {check} - nothing to retire"]
    rel, fn_name = p["segment"]
    path = os.path.join(SKILL, rel)
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fn_name)
    lines = src.splitlines(keepends=True)

    if not p["other_checks_in_segment"]:
        # the whole function goes - it emits nothing else
        start = node.lineno - 1
        while start > 0 and lines[start - 1].startswith(("#", "@")):
            start -= 1
        end = node.end_lineno
        while end < len(lines) and lines[end].strip() == "":
            end += 1
        open(path, "w", encoding="utf-8").write("".join(lines[:start] + lines[end:]))
        done.append(f"deleted segment {fn_name} from {rel}")
    else:
        return [f"REFUSED: {fn_name} also emits {p['other_checks_in_segment']} - the check() call must be removed by hand, and so must whatever computes only its inputs (feature 146: stubbing the call is not removing the check)"]

    pin_path = os.path.join(SKILL, "tests/fixtures/gate_check_names.json")
    pin = json.load(open(pin_path, encoding="utf-8"))
    if check in pin:
        pin.remove(check)
        open(pin_path, "w", encoding="utf-8").write(json.dumps(sorted(pin), indent=2) + "\n")
        done.append(f"removed {check} from the name pin ({len(pin) + 1} -> {len(pin)})")

    leg_path = os.path.join(SKILL, "tests/fixtures/registry_legacy_rows.json")
    leg = json.load(open(leg_path, encoding="utf-8"))
    before = len(leg["rows"])
    leg["rows"] = [r for r in leg["rows"] if r["name"] != fn_name]
    if len(leg["rows"]) != before:
        open(leg_path, "w", encoding="utf-8").write(json.dumps(leg, indent=2) + "\n")
        done.append(f"removed the frozen legacy row for {fn_name}")

    for rel_fx in p["fixtures"]:
        os.remove(os.path.join(SKILL, rel_fx))
        done.append(f"deleted fixture {rel_fx} (it pinned this check and nothing else)")
    if p["tests"]:
        done.append(f"TESTS LEFT FOR YOU: {p['tests']}")
    return done


def main(argv: list[str]) -> int:
    names = [a for a in argv if not a.startswith("--")]
    if not names:
        print(__doc__)
        return 2
    for check in names:
        p = plan_for(check)
        print(f"\n=== {check} ===")
        print(f"  segment            : {p['segment']}")
        print(f"  segment also emits : {p['other_checks_in_segment'] or 'nothing - the whole function goes'}")
        print(f"  fixtures pinned    : {p['fixtures'] or 'none'}")
        print(f"  tests naming it    : {p['tests'] or 'none'}  (JUDGMENT - not touched)")
        if "--apply" in argv:
            for line in apply_for(check):
                print(f"    -> {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
