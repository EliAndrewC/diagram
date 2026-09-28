"""Feature 276's AFTER figures: run the harness through make and write them into measurements.json.

    python3 specs/276-engine-hotspots-and-test-scans/measure.py

This is the `command` the after-entries carry, so `make figures` re-runs it. The BEFORE entries (`before-*`,
`rescue-*`, `perf-start-*`) are one-time observations of the unmodified code and carry no command: re-running
them on the changed code would report a moved count that is the whole point of the feature.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SKILL = ROOT / ".claude" / "skills" / "diagram"
COMMAND = f"python3 {HERE.relative_to(ROOT)}/measure.py"


def after_entries(b: dict) -> dict[str, dict]:
    """The after-keys from one harness run, in the same shape as the before-keys."""
    src = "measure.py -> make spec-harness SPEC=specs/276-engine-hotspots-and-test-scans, best of 3 unprofiled"
    out: dict[str, dict] = {}

    def add(k: str, v: float, u: str, q: str, varies: bool = True) -> None:
        out[k] = {"value": v, "unit": u, "quantity": q, "source": src, "command": COMMAND}
        if varies:
            out[k]["varies"] = True

    t = b["tests"]
    ast_ids = [k for k in t if not k.startswith("group:") and any(x in k for x in ("test_memory", "test_driver", "test_package_surfaces", "test_water_ways"))]
    rec_ids = [k for k in t if not k.startswith("group:") and "interactive/" in k]
    add("after-ast-four-together-s", t["group:ast-four-together"], "s", "the four AST-scanning tests together in one process (SC-001)")
    add("after-record-five-together-s", t["group:record-five-together"], "s", "the five named record tests together in one process (SC-001a)")
    add("after-ast-tests-max", max(t[k] for k in ast_ids), "s", "the slowest of the four AST-scanning tests alone (setup + call)")
    add("after-record-tests-sum", round(sum(t[k] for k in rec_ids), 2), "s", "the five named record tests alone, summed")
    h = b["homesteads"]
    add("after-rescue-s", h["rescue-20"]["s"], "s", "stage_homesteads on the rescue-rounds scenario")
    add("after-rescue-fits", h["rescue-20"]["fit_tests"], "fit tests", "full fit tests on the rescue-rounds scenario", varies=False)
    add("after-rescue-houses", h["rescue-20"]["houses"], "houses", "houses seated on the rescue-rounds scenario", varies=False)
    for n in (60, 120, 240):
        add(f"after-dense-{n}-per-house", h[f"dense-{n}"]["s_per_house"], "s", f"try_place cost per seated house, {n} seeds at constant density")
        add(f"after-dense-{n}-houses", h[f"dense-{n}"]["houses"], "houses", f"houses seated from {n} seeds at constant density", varies=False)
    add("after-dense-240-s", h["dense-240"]["s"], "s", "try_place total, 240 seeds at constant density")
    s = b["seams"]
    add("after-close-seams-max", max(v["close_seams_s"] for v in s.values()), "s", "close_seams inside one build_comb, the slowest of seeds 5/11/17")
    tr = b["track"]
    add("after-track-stage-s", tr["stage_s"], "s", "stage_track on Inashiro seed 4")
    add("after-track-checks-s", tr["path_checks_s"], "s", "the path checks inside stage_track on Inashiro seed 4")
    return out


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "after.json"
        r = subprocess.run(["make", "-C", str(SKILL), "--no-print-directory", "spec-harness", f"SPEC={HERE.relative_to(ROOT)}", f"OUT={dest}"])
        if r.returncode != 0:
            return r.returncode
        run = json.loads(dest.read_text())
    (HERE / "harness-after.json").write_text(json.dumps(run, indent=2) + "\n")
    path = HERE / "measurements.json"
    recorded = json.loads(path.read_text())
    recorded.update(after_entries(run))
    path.write_text(json.dumps(recorded, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
