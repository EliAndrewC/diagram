"""THE FULL TREE (feature 135, GM 2026-08-27): the fan-out agreement (two real rolls of seed 41, one of them in a
process pool no cache can reach - and the only walk of the pool branch) and the CLI's artifact-writing roll. The
pool path and the CLI are exercised by every `make map` / regen; their gate-time value is the coverage they carry,
which only the full run enforces."""

import contextlib
import io
import os
import tempfile

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache


# ROLLED IN A CHILD (feature 213 FR-007): `main()` rolls through `generate` in the process that calls it, so the
# CLI test's roll runs in the roll cache's child by name. SEED 9, NOT 8 (FR-005): seed 8 took two attempts of the
# re-roll loop on every gate, and nothing here tests re-rolling.
def roll_cli() -> tuple[bool, bool, str]:
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "cli")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hg.main(["--name", "Clitest", "--seed", "9", "--households", "11", "--down-deg", "90", "--sink", "offmap", "--windward", "N", "--out", out, "--no-render"])
        return os.path.exists(out + ".json"), os.path.exists(out + ".svg"), buf.getvalue()


@pytest.mark.rolls_map
def test_the_cli_reports_a_single_hamlet() -> None:
    # the RETURN CODE reports the gate's verdict on this particular seed, which is not what this
    # test is about - it is about the CLI writing the artifacts and reporting the map. Asserting a
    # green gate here would pin one arbitrary seed's luck (see the cohort ratchet above for the rate).
    has_json, has_svg, out = rollcache.keyed_to(test_the_cli_reports_a_single_hamlet, roll_cli, child="tests.full.hamletgen.test_driver:roll_cli")[0]
    assert has_json and has_svg
    assert "Clitest" in out


@pytest.mark.rolls_map
def test_the_fan_out_agrees_with_the_serial_path() -> None:
    """The fan-out's entire safety claim, pinned: a map is a pure function of its spec, so rolling
    it in a worker must produce exactly the report rolling it here does. This is also the only test
    that walks the `ProcessPoolExecutor` branch (`jobs > 1` takes the pool path even for one map),
    which is why it rolls for real rather than stubbing `generate`.

    The method matters as much as the assertion. When the fan-out landed (2026-08-16) the parallel
    24-seed run differed from the session's serial baseline on 3 of 24 maps - which looked damning
    until the baseline turned out to predate a mid-task merge of another session's engine round.
    Re-rolling exactly those seeds serially on the SAME code reproduced the parallel verdicts.
    Diff against the same code, never against an older log."""
    (parallel,) = hg.cohort(1, first_seed=41, jobs=2)
    # THE SERIAL HALF IS THE SHARED ROLL (feature 213 FR-007): `report()` serves the one roll of seed 41 the gate
    # already made for the cohort test and the lane-rule fixtures - the same `generate`, in a child, so the
    # comparison stands and only the pool-child path rolls again here (a stated Duplicate in tests/rolls.py).
    serial, _how = rollcache.report(hg.driver.cohort_specs(1, first_seed=41)[0])
    assert parallel.line() == serial.line()
    assert parallel.failures == serial.failures
    assert parallel.path is None  # a cohort member is gated, then thrown away
