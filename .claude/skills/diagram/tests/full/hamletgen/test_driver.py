"""THE FULL TREE (feature 135, GM 2026-08-27): the fan-out agreement (two real rolls of seed 41, one of them in a
process pool no cache can reach - and the only walk of the pool branch) and the CLI's artifact-writing roll. The
pool path and the CLI are exercised by every `make map` / regen; their gate-time value is the coverage they carry,
which only the full run enforces."""

import os

import pytest

from l7r.diagram import hamletgen as hg


@pytest.mark.rolls_map
def test_the_cli_reports_a_single_hamlet(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    out = str(tmp_path / "cli")
    # the RETURN CODE reports the gate's verdict on this particular seed, which is not what this
    # test is about - it is about the CLI writing the artifacts and reporting the map. Asserting a
    # green gate here would pin one arbitrary seed's luck (see the cohort ratchet above for the rate).
    hg.main(["--name", "Clitest", "--seed", "8", "--households", "11", "--down-deg", "90", "--sink", "offmap", "--windward", "N", "--out", out, "--no-render"])
    assert os.path.exists(out + ".json") and os.path.exists(out + ".svg")
    assert "Clitest" in capsys.readouterr().out


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
    (serial,) = hg.cohort(1, first_seed=41, jobs=1)
    assert parallel.line() == serial.line()
    assert parallel.failures == serial.failures
    assert parallel.path is None  # a cohort member is gated, then thrown away
