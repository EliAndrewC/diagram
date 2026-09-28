"""Feature 281's figures: the harness (stage seconds, one saved profile per hamlet), then the counts read from the profiles.

    python3 specs/281-third-hotspot-pass/measure.py before   # the clone at the base commit: before-* keys
    python3 specs/281-third-hotspot-pass/measure.py after    # the base worktree, then the clone, back to back

The base is `2a61d1488`, 278 landed with 261 merged, in a detached worktree at `/tmp/base281` (created if missing). Seconds
depend on the machine's load, so the after-run takes the base and the clone one straight after the other: the base as
`base-rerun-*` beside the recorded `before-*`, the clone as `after-*`. Counts (`counts.py`, from the profiles) do not.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = "2a61d1488"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WT = Path("/tmp/base281")
ENGINE = Path(".claude/skills/diagram/l7r/diagram")


def run(tree: Path, out: Path) -> tuple[dict, dict]:
    if tree.resolve() != ROOT.resolve():  # the worktree has no copy of this feature's directory; the clone is its home
        (tree / "specs" / HERE.name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "harness.py", tree / "specs" / HERE.name / "harness.py")
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(["make", "-C", str(tree / ".claude" / "skills" / "diagram"), "--no-print-directory", "spec-harness", f"SPEC=specs/{HERE.name}", f"OUT={out}"], check=True)
    counts = subprocess.run([sys.executable, str(HERE / "counts.py"), str(out), str(tree / ENGINE)], check=True, capture_output=True, text=True).stdout
    return json.loads((out / "times.json").read_text()), json.loads(counts)


def keys(prefix: str, times: dict, counts: dict, source: str, command: str) -> dict:
    out = {}
    for m, v in times.items():
        out[f"{prefix}-{m}-roll-s"] = {"value": v["roll_s"], "unit": "s", "quantity": f"one generate() of {m}, render off, the faster of two unprofiled rolls", "source": source, "command": command}
        out[f"{prefix}-{m}-full-s"] = {"value": v["full_s"], "unit": "s", "quantity": f"one generate() of {m} writing its svg and page, unprofiled", "source": source, "command": command}
        for st, t in v["stages"].items():
            out[f"{prefix}-{m}-{st.replace('_', '-')}-s"] = {"value": t, "unit": "s", "quantity": f"{st} inside that roll of {m} (summed over its builds)", "source": source, "command": command}
        for k, c in counts.get(m, {}).items():
            out[f"{prefix}-{m}-{k.replace('_', '-')}"] = {"value": c, "unit": "builds" if k == "builds" else "calls", "quantity": f"{k} over one full generate() of {m}, counted by cProfile (counts.py)", "source": source, "command": command}
    out[f"{prefix}-pool-roll-s"] = {"value": round(sum(v["roll_s"] for v in times.values()), 3), "unit": "s", "quantity": "the five pool hamlets' roll times summed", "source": source, "command": command}
    return out


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "after"
    command = f"python3 {HERE.relative_to(ROOT)}/measure.py {mode}"
    path = HERE / "measurements.json"
    rec = json.loads(path.read_text()) if path.exists() else {}
    scratch = Path("/tmp/m281")
    if mode == "before":
        t, c = run(ROOT, scratch / "before")
        rec.update(keys("before", t, c, f"harness.py in the clone at {BASE} (the unmodified engine)", command))
    else:
        if not WT.exists():
            subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(WT), BASE], check=True, capture_output=True)
        t, c = run(WT, scratch / "base")
        rec.update(keys("base-rerun", t, c, f"harness.py in the detached worktree of {BASE}, run just before the clone's", command))
        t, c = run(ROOT, scratch / "after")
        rec.update(keys("after", t, c, "harness.py in the clone, run just after the base's", command))
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
