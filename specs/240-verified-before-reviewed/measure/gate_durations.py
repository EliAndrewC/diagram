"""Feature 240 R1: how long a `make done` gate takes on this clone, from the gate's own run log.

Re-runnable from a clean checkout: it reads only `.claude/skills/diagram/dev/run-log/*.json`, the records the
gate itself writes. Prints one JSON object - the quantity, the sample it measured, and the range.
"""

import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[3] / ".claude" / "skills" / "diagram" / "dev" / "run-log"
runs = []
for f in sorted(root.glob("*.json")):
    d = json.loads(f.read_text())
    s = float(d.get("seconds") or 0)
    if d.get("target") == "done" and s > 0 and str(d.get("utc", "")) >= "2026-09-12T13:27":
        runs.append((s, str(d.get("result", ""))))
ran = [s for s, r in runs if not r.startswith("already")]
green = [s for s, r in runs if r == "green"]
json.dump(
    {
        "quantity": "wall seconds of a `make done` gate that actually ran (short-circuits excluded), feature 230's span",
        "sample": {"gates_that_ran": len(ran), "green": len(green)},
        "total_s": round(sum(ran)),
        "min_s": min(ran),
        "max_s": max(ran),
        "green_min_s": min(green),
        "green_max_s": max(green),
    },
    sys.stdout,
    indent=1,
)
print()
