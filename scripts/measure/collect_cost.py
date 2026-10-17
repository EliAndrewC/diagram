#!/usr/bin/env python3
"""Where a test run's time goes before any test runs (feature 383 amendment 3, plan D25): collection, per runner shape.

    collect_cost.py [--tree quick|tooling] [--json <out>]

Times, back to back on this tree: the run as `make quick` makes it (testmon selecting, xdist workers), the same with no workers,
and a collection alone (`--collect-only`), each `--no-cov`, and prints how many tests each selected and ran. The GM, 2026-10-17:
*"I do really like the thing that you said about not importing tests that we are not planning on running. So I guess the quick
tests, for instance, really could probably save a good percentage of their current runtime"*.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TREES = {
    "quick": ["-m", "not rolls_map and not tooling", "tests", "--ignore=tests/tier_town", "--ignore=tests/tier_city", "--ignore=tests/gate", "--ignore=tests/full", "--ignore=tests/tooling"],
    "tooling": ["tests/tooling"],
}


def timed(args: list[str], env: dict[str, str] | None = None) -> tuple[float, str, dict[str, dict]]:
    """Seconds, pytest's last line, and per process (controller, each worker) the test modules it imported and the items it
    collected (`collect_probe.py`)."""
    probe = Path(tempfile.mkdtemp(prefix="l7r-collect-"))
    path = os.pathsep.join([str(HERE), *([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else [])])
    t = time.monotonic()
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-cov", "-p", "no:randomly", "-p", "collect_probe", *args],
        cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "L7R_VIA_MAKE": "1", "PYTHONPATH": path, "L7R_COLLECT_PROBE": str(probe), **(env or {})},
    )  # fmt: skip
    s = round(time.monotonic() - t, 2)
    procs = {f.stem: json.loads(f.read_text()) for f in sorted(probe.glob("*.json"))}
    shutil.rmtree(probe, ignore_errors=True)
    out = (p.stdout + p.stderr).strip()
    return s, out.splitlines()[-1] if out else "", procs


def counts(line: str) -> str:
    return ", ".join(m for m in re.findall(r"\d+ (?:passed|failed|deselected|selected|tests? collected|skipped)", line)) or line[-80:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--tree", choices=sorted(TREES), default="quick")
    ap.add_argument("--json", default="")
    a = ap.parse_args(argv)
    tree = TREES[a.tree]
    select = ["--testmon-forceselect"] if a.tree == "quick" else []
    shapes = {
        "as make runs it (6 workers)": ["-n", "6", "--dist", "worksteal", *select, *tree],
        "no workers": ["-n", "0", *select, *tree],
        "collection only, no workers": ["-n", "0", "--collect-only", *select, *tree],
        "collection only, no testmon": ["-n", "0", "--collect-only", *tree],
    }
    rows = {}
    for name, args in shapes.items():
        s, last, procs = timed(args)
        rows[name] = {"s": s, "result": counts(last), "processes": procs}
        per = ", ".join(f"{k} {v['test_modules_imported']} modules/{v['items']} items" for k, v in procs.items())
        print(f"{s:7.2f} s  {name}: {rows[name]['result']}\n           {per}")
    rows["load"] = round(os.getloadavg()[0], 1)
    print(f"load {rows['load']}")
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
