"""Feature 278's AFTER figures, back to back with the base: the harness in the base worktree, then in the clone.

    python3 specs/278-second-hotspot-pass/measure.py

The base is `ac01ffe2d` in a detached worktree at `/tmp/base278` (created if missing). Seconds depend on the machine's load,
so the two runs are taken one straight after the other; the base run is written as `base-rerun-*` keys beside the recorded
`before-*`, and the clone's as `after-*`, each carrying this command. Counts do not depend on load.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = "ac01ffe2d"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WT = Path("/tmp/base278")
COMMAND = f"python3 {HERE.relative_to(ROOT)}/measure.py"


def run(tree: Path, out: Path) -> dict:
    if tree.resolve() != ROOT.resolve():  # the worktree has no copy of this feature's directory; the clone is its home
        (tree / "specs" / HERE.name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "harness.py", tree / "specs" / HERE.name / "harness.py")
    subprocess.run(["make", "-C", str(tree / ".claude" / "skills" / "diagram"), "--no-print-directory", "spec-harness", f"SPEC=specs/{HERE.name}", f"OUT={out}"], check=True)
    return json.loads(out.read_text())


def keys(prefix: str, res: dict, source: str) -> dict:
    out = {}
    for m, v in res.items():
        out[f"{prefix}-{m}-roll-s"] = {"value": v["roll_s"], "unit": "s", "quantity": f"one generate() of {m}, render off, the faster of two unprofiled rolls", "source": source, "command": COMMAND}
        for st, t in v["stages"].items():
            out[f"{prefix}-{m}-{st.replace('_', '-')}-s"] = {"value": t, "unit": "s", "quantity": f"{st} inside one generate() of {m} (summed over its builds)", "source": source, "command": COMMAND}
        for k, c in v["counts"].items():
            out[f"{prefix}-{m}-{k.replace('_', '-')}"] = {"value": c, "unit": "builds" if k in ("builds", "finishes") else "calls", "quantity": f"{k} over one generate() of {m}", "source": source, "command": COMMAND}
    out[f"{prefix}-pool-roll-s"] = {"value": round(sum(v["roll_s"] for v in res.values()), 3), "unit": "s", "quantity": "the five pool hamlets' roll times summed", "source": source, "command": COMMAND}
    return out


def main() -> int:
    if not WT.exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(WT), BASE], check=True, capture_output=True)
    base = run(WT, HERE / "harness-base-rerun.json")
    after = run(ROOT, HERE / "harness-after.json")
    path = HERE / "measurements.json"
    rec = json.loads(path.read_text())
    rec.update(keys("base-rerun", base, f"harness.py in the detached worktree of {BASE}, run just before the clone's"))
    rec.update(keys("after", after, "harness.py in the clone, run just after the base's"))
    path.write_text(json.dumps(rec, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
