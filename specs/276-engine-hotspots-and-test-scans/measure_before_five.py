"""The five-layout house totals on the UNMODIFIED engine - the baseline SC-003's count clause is judged against.

    python3 specs/276-engine-hotspots-and-test-scans/measure_before_five.py

Checks the commit before this feature's first (`BASE`) out into a temporary detached worktree, runs the same five-layout
loop the harness runs, and writes `before-dense-{60,120,240}-{nucleated,dispersed}-houses-five` into measurements.json.
Re-runnable because the base is a fixed commit: `make figures` re-runs this and must read the same counts.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "9f28392f6"  # the parent of feature 276's first commit
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMMAND = f"python3 {HERE.relative_to(ROOT)}/measure_before_five.py"

PROBE = '''
import json, os, random
from l7r.diagram.settlement import Settlement

def total(n, form):
    out = 0
    for lay in range(5):
        side = int((n ** 0.5) * 95) + 400
        s = Settlement(side, side, seed=7)
        s.meta(name="D", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=form == "nucleated")
        s._nucleated = form == "nucleated"
        rng = random.Random(n * 1000 + lay)
        k = int(n ** 0.5) + 1
        for i in range(n):
            s.try_place(200 + (i % k) * 95 + rng.uniform(-20, 20), 200 + (i // k) * 95 + rng.uniform(-20, 20), "plain")
        out += len(s.M["houses"])
    return out

def test_five():
    res = {f"{form}-{n}": total(n, form) for form in ("nucleated", "dispersed") for n in (60, 120, 240)}
    open(os.environ["FIVE_OUT"], "w").write(json.dumps(res))
'''


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        wt = Path(tmp) / "base"
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(wt), BASE], check=True, capture_output=True)
        try:
            skill = wt / ".claude" / "skills" / "diagram"
            (skill / "tests" / "test_zz_five_tmp.py").write_text(PROBE)
            out = Path(tmp) / "five.json"
            r = subprocess.run(["make", "-C", str(skill), "--no-print-directory", "test-file", "FILE=tests/test_zz_five_tmp.py"], env={**__import__("os").environ, "FIVE_OUT": str(out)})
            if r.returncode != 0:
                return r.returncode
            res = json.loads(out.read_text())
        finally:
            subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], check=False, capture_output=True)
    path = HERE / "measurements.json"
    recorded = json.loads(path.read_text())
    for key, value in res.items():
        form, n = key.split("-")
        recorded[f"before-dense-{n}-{form}-houses-five"] = {
            "value": value,
            "unit": "houses",
            "quantity": f"houses seated from {n} seeds summed over five layouts, {form} path, on the UNMODIFIED engine ({BASE})",
            "source": f"measure_before_five.py - a detached worktree of {BASE}, the harness's five-layout loop",
            "command": COMMAND,
        }
    path.write_text(json.dumps(recorded, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
