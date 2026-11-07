"""THE REAL TREE's half of `tests/tooling/test_open_questions.py`: `open_questions.py` over the real tree, within its CPU bound.

Moved here by feature 444 T36 (the GM 2026-11-07: "any single test which takes even 100 milliseconds is fairly suspect"; then "please
proceed with all 3 of those things"): it checks a TOOL's behavior over the whole repository, and a scan of the whole repository reads
every file, so the gate's recorded reads selected it for every edit, a Rust one included. It is the tool's property, not the edited
file's: `tests/tooling/real_tree/` runs when the gate plans full (any `scripts/`, gate-configuration or tooling change - the tool's
own) and on `FULL=1`, never for an engine or a Rust increment (`pool_readers.rust_readers`, `tests/CLAUDE.md`).
"""

from __future__ import annotations

import resource
import subprocess
import sys

from tests.tooling.test_open_questions import CALIBRATION_QUIET, REPO, SKILL, _calibration_cpu, oq


def test_the_real_tree() -> None:
    # ...ITS CPU TIME, NOT THE WALL CLOCK (feature 315): the gate runs it beside four other sessions under one 10 GB cap, and a
    # 2.3 s run read 12.4 s while the machine stalled on memory - the bound is on the work.
    # BUT CPU TIME IS NOT IMMUNE TO CONTENTION EITHER (2026-10-04): the GM's laptop is a hybrid Core Ultra 7 155H (P- and
    # E-cores, two threads a core), and with every core busy the same 3.4 s of work read 8-13 s of CPU - it failed a
    # test-full at 10.0003 s, and ran 9-11 s in every full run measured that day. So the CPU time is SCALED by a
    # calibration loop run beside it: `CALIBRATION_QUIET` s of CPU on a quiet machine, and its lesser reading of the
    # two around the run says how much slower this machine is right now. Measured under 22 busy loops: the scaled
    # reading was 3.4 / 2.5 / 3.9 s against 3.4 s quiet - the 10 s bound (SC-003, a quiet-machine target) still
    # catches a 3x regression and no longer flakes on a loaded gate.
    calibrated = _calibration_cpu()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = subprocess.run([sys.executable, str(REPO / "scripts/record/open_questions.py"), "--root", str(REPO)], capture_output=True, text=True, check=True).stdout
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    took = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    slowdown = max(1.0, min(calibrated, _calibration_cpu()) / CALIBRATION_QUIET)
    took /= slowdown
    rack = out[out.index("## How our maps draw rice-drying racks (hasa, hasagi)") :]
    rack = rack[: rack.index("\n## ")]
    assert "map features: threshing yard" in rack
    assert "GUESS: A rack by the house runs from the yard's edge to its middle." in rack
    outside = out[out.index("GUESSES MARKED OUTSIDE THE RECORD") :]
    # the county program, its postern among it, moved to compound_example.py (feature 374 wave 125: compound.py past 1,000 lines)
    compound = outside[outside.index("\nl7r/diagram/compound_example.py\n") :].split("\n\n")[0]
    assert any("postern" in line and "GUESS" in line for line in compound.splitlines()), "the postern's GUESS, marked only in code (SC-004)"
    # every visible label in the record falls in a listed sentence (SC-001)
    labels = 0
    for frag in (SKILL / "research" / "questions").glob("*.html"):
        if frag.name.endswith(".notes.html") or not oq._FRAGMENT.match(frag.name):
            continue
        labels += len(oq._GUESS.findall(oq.visible(frag.read_text(encoding="utf-8"))))
    listed = sum(len(oq._GUESS.findall(line)) - 1 for line in out.splitlines() if line.startswith("   - GUESS: "))
    assert labels > 100 and listed == labels, f"{listed} labels listed of {labels} in the record"
    assert took < 10, f"make open-questions took {took:.1f} s (SC-003)"
