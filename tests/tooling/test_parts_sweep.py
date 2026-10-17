"""The parts sweep finds a case that leans on another's state (feature 383 amendment 4; the round arbiter's tooling fix on
hour:383-tooling-caches-and-hourly-step-back@3)."""

from __future__ import annotations

import pathlib
import shutil
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
SUITE = """#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PASS=0; FAIL=0; T=$(mktemp -d)
ok() {{ if eval "$2"; then PASS=$((PASS+1)); else echo "FAIL $1"; FAIL=$((FAIL+1)); fi; }}
case_z() {{ ok z true; }}
case_x() {{ touch "$T/flag"; ok x true; }}
case_y() {{ ok y {y}; }}
CASES=(case_y case_x case_z)
declare -A WEIGHT=([case_z]=9 [case_x]=5 [case_y]=1)
source "$HERE/parts.sh"
run_parts ${{FAKE_PARTS:-2}}
echo "fake: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
"""


def _sweep(tmp: pathlib.Path, y_check: str) -> subprocess.CompletedProcess[str]:
    for f in ("parts.sh", "parts_sweep.sh"):
        shutil.copy(REPO / "tests" / "hooks" / f, tmp / f)
    (tmp / "test-fake-hooks.sh").write_text(SUITE.format(y=y_check))
    return subprocess.run(["bash", str(tmp / "parts_sweep.sh"), "test-fake-hooks.sh"], capture_output=True, text=True, check=False)


def test_a_case_leaning_on_another_s_state_is_found(tmp_path: pathlib.Path) -> None:
    # y passes alone and after z, but not after x in the same part: at 2 parts x and y share the lighter part
    r = _sweep(tmp_path, "'[ ! -e \"$T/flag\" ]'")
    assert r.returncode == 1 and "FAKE_PARTS=2" in r.stdout and "FAIL y" in r.stdout, r.stdout


def test_independent_cases_are_the_same_at_every_count(tmp_path: pathlib.Path) -> None:
    r = _sweep(tmp_path, "true")
    assert r.returncode == 0 and "the same at 1 2 3 8 parts (fake: 3 passed, 0 failed)" in r.stdout, r.stdout
