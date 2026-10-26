"""m:triage-price (feature 432 T05, D7): what clearing a page-edit's triage-owed claims mechanically would have let through.

Replays every commit that changed `dev/claims-index.json` since 2026-10-04 against its first parent. A claim whose verdict went
from IN-STEP (or none) to DRIFTED or MISLABELED in a commit, with its code fingerprint and its `rests` (the blocks its verdict
rests on) unchanged while its `pages` snapshot changed, is a finding only the TRIAGE route could have produced: a page it
cites moved, no block it rests on did, and the triage named it TOUCHES. Those are what D7's mechanical clearing would no longer
catch. Also counted: the triage-route claims re-judged with no change of verdict (the clearing's saving), and the findings that
came by a changed rested-on block (the route D7 keeps).

    python3 specs/432-gm-review-signal/measure/triage_price.py
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FINDING = {"DRIFTED", "MISLABELED"}


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout


def at(c: str) -> dict:
    raw = git("show", f"{c}:dev/claims-index.json")
    try:
        return json.loads(raw) if raw else {}
    except ValueError:
        return {}


def main() -> int:
    commits = [ln.split() for ln in git("log", "--since=2026-10-04", "--format=%h %p", "--", "dev/claims-index.json").splitlines()]
    c = Counter()
    found = []
    for cur, *parents in commits:
        if not parents:
            continue
        a, b = at(parents[0]), at(cur)
        for k, row in b.items():
            was = a.get(k)
            if not was or row.get("code") != was.get("code"):
                continue
            moved_page = row.get("pages") != was.get("pages")
            same_rests = row.get("rests") == was.get("rests")
            if not moved_page:
                continue
            new, old = row.get("verdict"), was.get("verdict")
            route = "triage" if same_rests else "rests"
            if new in FINDING and old not in FINDING:
                c[f"{route}: new finding"] += 1
                if route == "triage":
                    found.append((cur, k, new))
            elif new == old:
                c[f"{route}: re-judged, same verdict"] += 1
    print(dict(c))
    for cur, k, v in found:
        print(f"  {cur} {v:10} {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
