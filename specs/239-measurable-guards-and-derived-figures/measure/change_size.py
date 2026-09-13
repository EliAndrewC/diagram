#!/usr/bin/env python3
"""How large a change actually was, from git rather than from memory.

    python3 specs/239-*/measure/change_size.py <from-ref> <to-ref> [--record]

Feature 239's summary called feature 236's second amendment "about 40 lines", which understated it
about sevenfold in the direction that made the argument stronger. A line count is a figure like any
other and git will produce it, so it is recorded rather than remembered.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import subprocess
import sys

MEASUREMENTS = pathlib.Path(__file__).resolve().parent.parent / "measurements.json"
ROOT = pathlib.Path(__file__).resolve().parents[3]


def diffstat(a: str, b: str, paths: list[str]) -> tuple[int, int]:
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "--shortstat", a, b, "--", *paths],
                         capture_output=True, text=True).stdout
    ins = int((re.search(r"(\d+) insertion", out) or [0, 0])[1] or 0)
    dels = int((re.search(r"(\d+) deletion", out) or [0, 0])[1] or 0)
    return ins, dels


def main(argv: list[str]) -> int:
    a, b = argv[0], argv[1]
    guard_ins, guard_del = diffstat(a, b, ["scripts/house-style-hooks.sh", "scripts/_hm_house.py"])
    all_ins, all_del = diffstat(a, b, ["scripts/"])
    print(f"{a}..{b}")
    print(f"  the hook and its module: +{guard_ins} -{guard_del}")
    print(f"  all of scripts/:         +{all_ins} -{all_del}")
    if "--record" in argv:
        now = datetime.date.today().isoformat()
        have = json.loads(MEASUREMENTS.read_text()) if MEASUREMENTS.is_file() else {}
        cmd = f"python3 specs/239-measurable-guards-and-derived-figures/measure/change_size.py {a} {b} --record"
        have["amendment-guard-lines-added"] = {"value": guard_ins, "unit": "lines", "taken": now, "command": cmd,
                                               "note": "feature 236 amendment 2: the hook and its new module"}
        have["amendment-scripts-lines-added"] = {"value": all_ins, "unit": "lines", "taken": now, "command": cmd,
                                                 "note": "the same window, all of scripts/"}
        MEASUREMENTS.write_text(json.dumps(have, indent=1, sort_keys=True) + "\n")
        print(f"recorded 2 figures in {MEASUREMENTS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
