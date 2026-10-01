"""Feature 297's figures (284's driver, re-based): the harness (stage seconds, one saved profile per hamlet), then the counts read from the profiles.

    python3 specs/297-placement-by-construction/measure.py before   # the clone at the base commit: before-* keys
    python3 specs/297-placement-by-construction/measure.py after    # the base worktree, then the clone, back to back
    python3 specs/297-placement-by-construction/measure.py after-main   # main as merged into the clone (MAIN), then the clone

The base is `c5a631f9b`, main when this feature was claimed (295 landed), in a detached worktree at `/tmp/base297` (created if missing). Seconds
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

BASE = "c5a631f9b"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WT = Path("/tmp/base297")
# MAIN AS MERGED (if main moves while this runs): the timing that says what
# this feature buys over the main it lands on, beside the base the counts were set against
MAIN = "c5a631f9b"  # re-pointed if main moves during the work
MAIN_WT = Path("/tmp/main297")
ENGINE = Path(".claude/skills/diagram/l7r/diagram")
# the named callee of each entry bucket (plan C's table); every bucket also records its TOTAL
BUCKET_CALLEES: dict[str, tuple[str, ...]] = {
    "seats": ("HousesMixin.try_place",),
    "corridor": ("access_corridor",),
    "bundle": ("BundleMixin._bundle_geom",),
    "mats": ("point_in_poly",),
    "marsh": ("random.uniform",),
    "grove": ("GroveBlocks.static_clear", "GroveBlocks.too_near"),
    "open_ground": ("RingIndex.near",),
    "commons": ("grass_scatter",),
    "web": ("seg_dist",),
    "law": ("lanes_breaking",),
    "field": ("carve_comb", "close_seams"),
    "hem": ("drain_bank_clearance",),
    "seams": ("_absorb",),
    "page": ("drop_offmap",),
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


def regen_times(tree: Path) -> dict[str, float]:
    """`make map` itself on Inashiro - the child, the stages, the finish WITH its renders (the harness's test node rolls render-off,
    the gate's policy) - uncached, the fastest of three, as the REGENERATED line reports it."""
    best: dict[str, float] = {}
    for _ in range(3):
        out = subprocess.run(["make", "-C", str(tree / ".claude" / "skills" / "diagram"), "--no-print-directory", "map", "GEN=--no-cache pool/hamlets/inashiro/inashiro.gen.py"], check=True, capture_output=True, text=True).stdout
        m = re.search(r"REGENERATED\s+inashiro\s+([0-9.]+)s", out)
        assert m, out[-800:]
        best["inashiro"] = min(best.get("inashiro", 1e9), float(m.group(1)))
    return best


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "after"
    command = f"python3 {HERE.relative_to(ROOT)}/measure.py {mode}"
    path = HERE / "measurements.json"
    rec = json.loads(path.read_text()) if path.exists() else {}
    scratch = Path("/tmp/m297")
    if not WT.exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(WT), BASE], check=True, capture_output=True)
    if mode in ("regen-before", "regen-after"):
        load0 = os.getloadavg()[0]
        tree = WT if mode == "regen-before" else ROOT
        for m, v in regen_times(tree).items():
            rec[f"{mode.split('-')[1]}-{m}-regen-s"] = {"value": v, "unit": "s", "quantity": f"`make map` of {m} uncached (svg, png, page), the fastest of three, as REGENERATED reports it", "source": str(tree), "command": command, "varies": True, "load": f"{load0:.1f} -> {os.getloadavg()[0]:.1f}"}
    elif mode == "before":  # the BASE, wherever the clone has moved since (first taken in the clone while it stood at BASE)
        t, c, load = run(WT, scratch / "before")
        rec.update(keys("before", t, c, f"harness.py in the detached worktree of {BASE} (the unmodified engine)", command, load))
    elif mode == "after-main":
        if not MAIN_WT.exists():
            subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(MAIN_WT), MAIN], check=True, capture_output=True)
        t, c, load = run(MAIN_WT, scratch / "main")
        rec.update(keys("main-rerun", t, c, f"harness.py in the detached worktree of {MAIN} (main as merged), run just before the clone's", command, load))
        t, c, load = run(ROOT, scratch / "after")
        rec.update(keys("after", t, c, "harness.py in the clone, run just after main's", command, load))
    else:
        t, c, load = run(WT, scratch / "base")
        rec.update(keys("base-rerun", t, c, f"harness.py in the detached worktree of {BASE}, run just before the clone's", command, load))
        t, c, load = run(ROOT, scratch / "after")
        rec.update(keys("after", t, c, "harness.py in the clone, run just after the base's", command, load))
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
