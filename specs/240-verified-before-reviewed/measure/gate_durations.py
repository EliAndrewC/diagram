"""Feature 240 R1: how long feature 230's own `make done` gates took, from the gates' own run log.

THE SAMPLE IS FEATURE 230'S GATES, AND ONLY THEM. The run log is committed and arrives with every merge from
main, so a time window over it holds EVERY session's gates, not this clone's. The first version of this
harness selected by window alone, and ten of the thirty-six gates it counted belonged to features 229, 231,
232, 233 and 236 - including the longest run and five of the nine green ones. A record is therefore selected
by its own `commit` field being one of feature 230's commits (a subject starting "230", or a merge INTO the 230
clone), and
the window is closed at the landing so the next gate recorded anywhere cannot change the answer.

Re-runnable from a clean checkout: it reads only the committed run log and `git log`. Prints one JSON object.
"""

import json
import pathlib
import subprocess
import sys

repo = pathlib.Path(__file__).resolve().parents[3]
log = repo / ".claude" / "skills" / "diagram" / "dev" / "run-log"
START, END = "2026-09-12T13:27", "2026-09-13T03:46"  # feature 230's claim, and its landing
# feature 230's commits, and the MERGES INTO its clone: a gate run at "Merge main ... into the 230 clone" is this
# feature's gate too, and selecting on the subject prefix alone dropped one (a spec-fidelity round found it)
ours = set(subprocess.run(["git", "-C", str(repo), "log", "--format=%h", "-E", "--grep=^230", "--grep=into (the )?230"], capture_output=True, text=True, check=True).stdout.split())
ran = []
for f in sorted(log.glob("*.json")):
    d = json.loads(f.read_text())
    s, utc, commit = float(d.get("seconds") or 0), str(d.get("utc", "")), str(d.get("commit", ""))[:8]
    if d.get("target") != "done" or s <= 0 or not (START <= utc <= END) or str(d.get("result", "")).startswith("already"):
        continue
    if not any(commit.startswith(c) or c.startswith(commit) for c in ours):
        continue
    ran.append((s, str(d.get("result", ""))))
green = [s for s, r in ran if r == "green"]
json.dump(
    {
        "quantity": "wall seconds of feature 230's own `make done` gates that actually ran (short-circuits excluded), claim to landing",
        "sample": {"gates": len(ran), "green": len(green), "selected_by": "record commit in feature 230's commits", "window": [START, END]},
        "total_s": round(sum(s for s, _ in ran)),
        "max_s": max(s for s, _ in ran),
        "green_min_s": min(green),
        "green_max_s": max(green),
    },
    sys.stdout,
    indent=1,
)
print()
