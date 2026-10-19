#!/usr/bin/env python3
"""`make set-down F=<feature> WHY="<reason>"` - the feature's work is set down (feature 385 T70, plan D89).

Writes one row to `<git dir>/set-downs.jsonl`, which `set-down-hooks.sh` reads: a turn may then end with the feature's tasks open,
until the next `make task-start`. The reason is two words or more, as every escape's is (CLAUDE.md, "What is enforced").
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    why = os.environ.get("SET_DOWN_WHY", "").strip()
    if len(argv) != 1 or len(why.split()) < 2:
        print('usage: make set-down F=<feature> WHY="<why it stops here, two words or more>"', file=sys.stderr)
        return 2
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    hits = sorted(d.name for d in (root / "specs").glob(f"{argv[0]}*") if d.is_dir() and (d.name == argv[0] or d.name.startswith(f"{argv[0]}-")))
    if len(hits) != 1:
        print(f"set-down: no single specs/{argv[0]}* directory", file=sys.stderr)
        return 2
    gd = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, check=True).stdout.strip())
    utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (gd / "set-downs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"feature": hits[0], "why": why, "utc": utc}) + "\n")
    print(f"set-down: {hits[0]} set down ({why}); a turn may end with its tasks open until the next make task-start")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
