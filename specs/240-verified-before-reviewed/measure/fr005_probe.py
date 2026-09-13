#!/usr/bin/env python3
"""SC-004 on a real pool map, both ways: FR-005's check on Inashiro in every state it judges, each state SET UP here.

    python3 specs/240-verified-before-reviewed/measure/fr005_probe.py [--record]

Precondition: Inashiro's pool folder is whole and current (`make map GEN=pool/hamlets/inashiro/inashiro.gen.py`);
the probe refuses otherwise rather than measure whatever state the clone happens to be in. It moves the renders
aside, writes its own snapshot, ages it, edits the generator - and restores every one of those on exit, the prior
snapshot included. `--record` writes the exit codes and the slowest wall time to this feature's measurements.json.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

CLONE = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
POOL = CLONE / ".claude/skills/diagram/pool/hamlets/inashiro"
GEN = POOL / "inashiro.gen.py"
SNAP = CLONE / ".git/review-snapshot/inashiro"
HERE = pathlib.Path(__file__).resolve().parent
MEASUREMENTS = HERE.parent / "measurements.json"
COMMAND = "python3 specs/240-verified-before-reviewed/measure/fr005_probe.py --record"
SOURCE = "the exit code and wall time of scripts/_review_prereq.py check on pool map inashiro, in states this probe sets up and restores"
ARTIFACTS = (".json", ".svg", ".png", ".html")


def check(prompt: str) -> tuple[int, float, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(prompt)
    t0 = time.monotonic()
    run = subprocess.run([sys.executable, str(CLONE / "scripts/_review_prereq.py"), "check", "--clone", str(CLONE), "--maps", "inashiro", "--prompt-file", f.name, "--gate-green", "yes"], capture_output=True, text=True)
    pathlib.Path(f.name).unlink()
    return run.returncode, time.monotonic() - t0, run.stdout.strip()


def main(argv: list[str]) -> int:
    missing = [ext for ext in ARTIFACTS if not (POOL / f"inashiro{ext}").is_file()]
    if missing or check("review inashiro")[0] != 0:
        print(f"fr005_probe: Inashiro's pool folder must be whole and current first (missing: {missing or 'none'}) - make map GEN=pool/hamlets/inashiro/inashiro.gen.py")
        return 2
    keep = pathlib.Path(tempfile.mkdtemp())
    shutil.copy2(GEN, keep / "gen.py")
    if SNAP.exists():
        shutil.copytree(SNAP, keep / "snapshot")
    unnamed, named = "review inashiro", "review inashiro from .git/review-snapshot/inashiro/clone/"
    rows: list[tuple[str, str, int, float, str]] = []

    def probe(key: str, quantity: str, prompt: str) -> None:
        rc, secs, out = check(prompt)
        rows.append((key, quantity, rc, secs, out))
        print(f"{key:40s} rc={rc} {secs:.2f} s {out}")

    try:
        probe("240-fr005-whole-pool-rc", "no snapshot named, pool folder whole and current", unnamed)
        for ext in (".png", ".html"):
            shutil.move(POOL / f"inashiro{ext}", keep / f"inashiro{ext}")
        probe("240-fr005-pool-without-renders-rc", "no snapshot named, the pool's .png and .html moved aside as a gate leaves them", unnamed)
        shutil.rmtree(SNAP, ignore_errors=True)
        (SNAP / "clone").mkdir(parents=True)
        for ext in (".json", ".svg"):
            shutil.copy2(POOL / f"inashiro{ext}", SNAP / "clone" / f"inashiro{ext}")
        for ext in (".png", ".html"):
            shutil.copy2(keep / f"inashiro{ext}", SNAP / "clone" / f"inashiro{ext}")
        probe("240-fr005-named-current-snapshot-rc", "a whole snapshot of the current map named, pool without renders", named)
        with open(SNAP / "clone" / "inashiro.svg", "a") as f:
            f.write("<!-- the map before a fix -->")
        probe("240-fr005-named-older-snapshot-rc", "a whole snapshot whose SVG differs from the pool's named", named)
        shutil.copy2(POOL / "inashiro.svg", SNAP / "clone" / "inashiro.svg")
        with open(GEN, "a") as f:
            f.write("\nSTALE_PROBE_240 = 1\n")
        probe("240-fr005-key-moved-rc", "the generator edited so its cache key moves, current snapshot named", named)
    finally:
        shutil.copy2(keep / "gen.py", GEN)
        for ext in (".png", ".html"):
            if (keep / f"inashiro{ext}").is_file():
                shutil.move(keep / f"inashiro{ext}", POOL / f"inashiro{ext}")
        shutil.rmtree(SNAP, ignore_errors=True)
        if (keep / "snapshot").exists():
            shutil.copytree(keep / "snapshot", SNAP)
        shutil.rmtree(keep, ignore_errors=True)
    probe("240-fr005-restored-rc", "everything restored, no snapshot named", unnamed)
    if "--record" in argv:
        data = json.loads(MEASUREMENTS.read_text())
        for old in [k for k in data if k.startswith("240-fr005-")]:
            data.pop(old)
        today = time.strftime("%Y-%m-%d")
        for key, quantity, rc, _secs, _out in rows:
            data[key] = {"value": rc, "unit": "exit code", "command": COMMAND, "taken": today, "quantity": quantity, "source": SOURCE}
        data["240-fr005-check-max-s"] = {"value": round(max(r[3] for r in rows), 2), "unit": "s", "command": COMMAND, "taken": today, "varies": True, "quantity": "slowest of the probe's six checks", "source": SOURCE}
        MEASUREMENTS.write_text(json.dumps(data, indent=1) + "\n")
        print(f"recorded {len(rows) + 1} figures in {MEASUREMENTS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
