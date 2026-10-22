#!/usr/bin/env python3
"""`make set-down F=<feature> WHY="<reason>"` - the feature's work is set down (feature 385 T70, plan D89).

Writes one row to `<git dir>/set-downs.jsonl`, which `set-down-hooks.sh` reads: a turn may then end with the feature's tasks open,
until the next `make task-start`. The reason is two words or more, as every escape's is (CLAUDE.md, "What is enforced").

WORK THAT RESISTED IS SET DOWN ON THE ARBITER'S RULING (feature 405, the GM 2026-10-21). While an open task of the feature owes a
part B (`approach-owed.json`) and the round arbiter has ruled on nothing since, the set-down is refused and names `make
arbiter-ask`: a process stop goes to the arbiter (CLAUDE.md), whose rules ask first whether more room, within the research,
settles it. T26 was set down "for the GM to see T107 first" when the arbiter would have ruled the farms wider apart. The escape
is `SET_DOWN_OK="<reason>"` (the usage cap's wind-down, say), logged by the make target.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def _utc(text: str) -> str:
    """A `%Y-%m-%dT%H:%M:%SZ` stamp's sortable form; '' where none."""
    return str(text or "")[:19]


def unruled(root: Path, feature: str) -> str | None:
    """Why the feature may not be set down yet - an open task owes a part B the round arbiter has not ruled on since - or None."""
    gd = Path(subprocess.run(["git", "-C", str(root), "rev-parse", "--absolute-git-dir"], capture_output=True, text=True).stdout.strip() or root / ".git")
    try:
        owed = json.loads((gd / "approach-owed.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    d = root / "specs" / feature
    tasks = (d / "tasks.md").read_text(encoding="utf-8") if (d / "tasks.md").is_file() else ""
    open_ = [r for r in owed if isinstance(r, dict) and r.get("feature") == feature and str(r.get("part") or "B") == "B"
             and f"- [ ] {r.get('task')} " in tasks]
    if not open_:
        return None
    last = max(open_, key=lambda r: _utc(str(r.get("utc"))))
    ruled = []
    for raw in (d / "arbiter.jsonl").read_text(encoding="utf-8").splitlines() if (d / "arbiter.jsonl").is_file() else []:
        try:
            ruled.append(_utc(str(json.loads(raw).get("utc"))))
        except ValueError:
            continue
    if any(u >= _utc(str(last.get("utc"))) for u in ruled):
        return None
    return (f"set-down: refused - {last.get('trigger')} at {last.get('utc')} owes {last.get('task')} a part B, and the round arbiter "
            f"has ruled on nothing since. Work that resisted is set down on its ruling, which asks first whether more room within "
            f"the research settles it: make arbiter-ask SUBJECT=set-down-{last.get('task')} WHY=\"<what resisted, the routes "
            f"measured, the room knob and its ceiling>\" FILES=\"<the cohort record>\", then make set-down again "
            f"(escape: SET_DOWN_OK=\"<reason>\", e.g. the usage cap's wind-down)")


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
    if not os.environ.get("SET_DOWN_OK", "").strip() and (why_not := unruled(root, hits[0])):
        print(why_not, file=sys.stderr)
        return 2
    gd = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, check=True).stdout.strip())
    utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (gd / "set-downs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"feature": hits[0], "why": why, "utc": utc}) + "\n")
    print(f"set-down: {hits[0]} set down ({why}); a turn may end with its tasks open until the next make task-start")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
