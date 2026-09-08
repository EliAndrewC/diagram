"""THE FULL TREE (feature 135, GM 2026-08-27): the fan-out agreement (a pool-child roll of the reference against the
gate's shared roll - the only walk of the pool branch) and the CLI's wiring over the same shared roll (feature 214). The
pool path and the CLI are exercised by every `make map` / regen; their gate-time value is the coverage they carry,
which only the full run enforces."""

import contextlib
import dataclasses
import io
import json
import os
import tempfile

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from tests import rolls


@pytest.mark.rolls_map  # it reads the shared roll of the reference (no roll of its own since feature 214)
def test_the_cli_reports_a_single_hamlet(monkeypatch: pytest.MonkeyPatch) -> None:
    """`main()` parses its arguments into a spec, hands it to `generate`, and reports the map: the CLI's WIRING,
    proven for no roll (feature 214, GM 2026-09-08: *"not just some assertions we could add onto the existing tests
    where that same hamlet was already rolled elsewhere?!"*). `generate` is patched to serve the gate's shared roll
    of the reference and to write the artifacts from its manifest; `generate` itself is proven by every roll in
    the suite. What this no longer proves, stated (spec FR-007): `main` -> the real `generate` end to end.
    The RETURN CODE reports the gate's verdict on the map, which is not what this test is about."""
    plan, manifest = rollcache.hamlet(rolls.REFERENCE)
    rep, _how = rollcache.report(rolls.REFERENCE)
    seen: list[hg.HamletSpec] = []

    def serve(spec: hg.HamletSpec, out_base: str | None = None, render: bool = True) -> hg.Report:
        seen.append(spec)
        assert out_base is not None and render is False
        with open(out_base + ".json", "w", encoding="utf-8") as fh:
            json.dump(manifest, fh)
        with open(out_base + ".svg", "w", encoding="utf-8") as fh:
            fh.write("<svg xmlns='http://www.w3.org/2000/svg'/>")
        return dataclasses.replace(rep, path=out_base)

    monkeypatch.setattr(hg.driver, "generate", serve)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "cli")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hg.main(["--name", "Inashiro", "--seed", "4", "--households", "15", "--down-deg", "90", "--sink", "pond", "--out", out, "--no-render"])
        assert os.path.exists(out + ".json") and os.path.exists(out + ".svg")
    assert seen == [rolls.REFERENCE], "the CLI built exactly the reference spec from its arguments"
    assert "Inashiro" in buf.getvalue() and f"hh={plan.placed}/{plan.spec.households}" in buf.getvalue()


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
    # THE POOL CHILD ROLLS THE REFERENCE (feature 214): `roll_pool` is `cohort()`'s body with explicit specs, so the
    # pool path rolls a spec the gate already shares instead of a cohort seed nothing else reads.
    (parallel,) = hg.driver.roll_pool([rolls.REFERENCE], jobs=2)
    # THE SERIAL HALF IS THE SHARED ROLL (feature 213 FR-007): `report()` serves the gate's one roll of the reference -
    # the same `generate`, in a child, so the comparison stands and only the pool-child path rolls again here (a
    # stated Duplicate of the reference in tests/rolls.py).
    serial, _how = rollcache.report(rolls.REFERENCE)
    assert parallel.line() == serial.line()
    assert parallel.failures == serial.failures
    assert parallel.path is None  # a cohort member is gated, then thrown away
