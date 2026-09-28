"""Feature 284's figures (281's driver, re-based): the harness (stage seconds, one saved profile per hamlet), then the counts read from the profiles.

    python3 specs/281-third-hotspot-pass/measure.py before   # the clone at the base commit: before-* keys
    python3 specs/281-third-hotspot-pass/measure.py after    # the base worktree, then the clone, back to back

The base is `f52ed6aa8`, main when this work began (281 landed), in a detached worktree at `/tmp/base281` (created if missing). Seconds
depend on the machine's load, so the after-run takes the base and the clone one straight after the other: the base as
`base-rerun-*` beside the recorded `before-*`, the clone as `after-*`. Counts (`counts.py`, from the profiles) do not.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = "f52ed6aa8"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WT = Path("/tmp/base284")
ENGINE = Path(".claude/skills/diagram/l7r/diagram")
# the named callee of each entry bucket (plan C's table); every bucket also records its TOTAL
BUCKET_CALLEES: dict[str, tuple[str, ...]] = {
    "router": ("_route.<locals>.is_free", "_route.<locals>.in_band", "heapq.heappop"),
    "field": ("carve_comb", "_carve_sector", "close_seams"),
    "notice": ("_fits", "label_seat_clear", "place"),
    "bamboo": ("bamboo_blocked",),
    "page": ("merge_primitives", "drop_offmap"),
    "edge_scan": ("edge_dist",),
    "clip": ("seg_dist",),
    "fabric": ("RingIndex.__init__",),
    "toll": ("dict.get",),
    "handover": ("seg_dist",),
    "departures": ("math.hypot",),
    "home_bank": ("segments_cross",),
    "stream_rect": ("seg_dist",),
    "caption_lanes": ("seg_dist",),
    "carve": ("_carve_sector.<locals>.edge", "StrokeIndex.clearance"),
    "grove": ("GroveBlocks.inside", "GroveBlocks.hard"),
    "marsh": ("KeepoutGrid.hit",),
}


def run(tree: Path, out: Path) -> tuple[dict, dict, str]:
    if tree.resolve() != ROOT.resolve():  # the worktree has no copy of this feature's directory; the clone is its home
        (tree / "specs" / HERE.name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "harness.py", tree / "specs" / HERE.name / "harness.py")
    out.mkdir(parents=True, exist_ok=True)
    load0 = os.getloadavg()[0]
    subprocess.run(["make", "-C", str(tree / ".claude" / "skills" / "diagram"), "--no-print-directory", "spec-harness", f"SPEC=specs/{HERE.name}", f"OUT={out}"], check=True)
    load = f"{load0:.1f} -> {os.getloadavg()[0]:.1f} (1-minute load average at the run's start and end)"
    counts = subprocess.run([sys.executable, str(HERE / "counts.py"), str(out), str(tree / ENGINE)], check=True, capture_output=True, text=True).stdout
    return json.loads((out / "times.json").read_text()), json.loads(counts), load


# COUNTS THAT MOVE BETWEEN RUNS OF THE SAME CODE, and why they stay plain counts: the fabric index's work depends on how
# often `hamletgen.clearance._MEMO` hits, and that memo is keyed on object identities, so its hit rate moves with the
# reuse of ids - the base's Sawada ring builds read 8792 and 9098 on one commit (feature 281 Amendment 1's review). A count
# may not carry `varies` (FR-011b: a count repeats exactly or the thing counted changed - and here it did: the memo's
# hits), so `make figures` reports them as moved and the spec's Amendment 1 names them.


def keys(prefix: str, times: dict, counts: dict, source: str, command: str, load: str = "") -> dict:
    out = {}
    for m, v in times.items():
        out[f"{prefix}-{m}-roll-s"] = {"value": v["roll_s"], "unit": "s", "quantity": f"one generate() of {m}, render off, the fastest of three unprofiled rolls", "source": source, "command": command, "varies": True, "load": load}
        out[f"{prefix}-{m}-full-s"] = {"value": v["full_s"], "unit": "s", "quantity": f"one generate() of {m} writing its svg and page, unprofiled", "source": source, "command": command, "varies": True, "load": load}
        for st, t in v["stages"].items():
            out[f"{prefix}-{m}-{st.replace('_', '-')}-s"] = {"value": t, "unit": "s", "quantity": f"{st} inside that roll of {m} (summed over its builds)", "source": source, "command": command, "varies": True, "load": load}
        for k, c in counts.get(m, {}).items():
            out[f"{prefix}-{m}-{k.replace('_', '-')}"] = {"value": c, "unit": "builds" if k == "builds" else "calls", "quantity": f"{k} over one full generate() of {m}, counted by cProfile (counts.py)", "source": source, "command": command}
        for bucket, calls in v.get("buckets", {}).items():
            for callee in BUCKET_CALLEES.get(bucket, ()) + ("TOTAL",):
                out[f"{prefix}-{m}-b-{bucket.replace('_', '-')}-{re.sub('[^a-z0-9]+', '-', callee.lower()).strip('-')}"] = {
                    "value": int(calls.get(callee, 0)),
                    "unit": "calls",
                    "quantity": f"calls to {callee} made beneath the {bucket} entries over one roll of {m} (render off), counted by sys.monitoring (harness.py, plan C)",
                    "source": source,
                    "command": command,
                }
    out[f"{prefix}-pool-roll-s"] = {"value": round(sum(v["roll_s"] for v in times.values()), 3), "unit": "s", "quantity": "the five pool hamlets' roll times summed", "source": source, "command": command, "varies": True, "load": load}
    return out


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "after"
    command = f"python3 {HERE.relative_to(ROOT)}/measure.py {mode}"
    path = HERE / "measurements.json"
    rec = json.loads(path.read_text()) if path.exists() else {}
    scratch = Path("/tmp/m284")
    if not WT.exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(WT), BASE], check=True, capture_output=True)
    if mode == "before":  # the BASE, wherever the clone has moved since (first taken in the clone while it stood at BASE)
        t, c, load = run(WT, scratch / "before")
        rec.update(keys("before", t, c, f"harness.py in the detached worktree of {BASE} (the unmodified engine)", command, load))
    else:
        t, c, load = run(WT, scratch / "base")
        rec.update(keys("base-rerun", t, c, f"harness.py in the detached worktree of {BASE}, run just before the clone's", command, load))
        t, c, load = run(ROOT, scratch / "after")
        rec.update(keys("after", t, c, "harness.py in the clone, run just after the base's", command, load))
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
