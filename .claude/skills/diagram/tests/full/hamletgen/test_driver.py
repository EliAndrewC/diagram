"""THE FULL TREE (feature 135, GM 2026-08-27): the fan-out's pool branch on a stub producer (feature 215 - the only walk
of the pool branch) and the CLI's wiring over the pool's map of the reference (feature 214, 215). The
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
from tests import rolls
from tests.gate import _pool


@pytest.mark.rolls_map  # it reads the shared roll of the reference (no roll of its own since feature 214)
def test_the_cli_reports_a_single_hamlet(monkeypatch: pytest.MonkeyPatch) -> None:
    """`main()` parses its arguments into a spec, hands it to `generate`, and reports the map: the CLI's WIRING,
    proven for no roll (feature 214, GM 2026-09-08: *"not just some assertions we could add onto the existing tests
    where that same hamlet was already rolled elsewhere?!"*). `generate` is patched to serve the gate's shared roll
    of the reference and to write the artifacts from its manifest; `generate` itself is proven by every roll in
    the suite. What this no longer proves, stated (spec FR-007): `main` -> the real `generate` end to end.
    The RETURN CODE reports the gate's verdict on the map, which is not what this test is about."""
    plan, manifest = _pool.rolled_map(rolls.REFERENCE)
    rep = _pool.rolled_report(rolls.REFERENCE)
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
    # the CLI has no `--fixtures-min`, so what it can build is the reference's brief without the pool's forced shrine
    assert seen == [dataclasses.replace(rolls.REFERENCE, fixtures_min=None)], "the CLI built the reference spec from its arguments"
    assert "Inashiro" in buf.getvalue() and f"hh={plan.placed}/{plan.spec.households}" in buf.getvalue()


def stub_produce(spec: hg.HamletSpec) -> hg.Report:
    """A producer that rolls nothing: the plan and an empty verdict. Module-level, so the pool's children import it by name."""
    return hg.Report(plan=hg.plan_site(spec), failures=[])


def test_the_fan_out_agrees_with_the_serial_path() -> None:
    """THE POOL BRANCH, on a producer that rolls nothing (feature 215, FR-002): `roll_pool` fans the specs out
    across a `ProcessPoolExecutor`, brings the results back in seed order, and the branch is the same code
    `cohort()` runs. What this no longer proves, stated (spec FR-006 b): that the pool path produces the REAL
    map the serial path does - a map being a pure function of its spec is the immune test's claim, asserted
    there against the pool's committed manifest. The method when the fan-out landed (2026-08-16) still holds
    for anyone re-checking that: diff against the same code, never against an older log."""
    specs = list(rolls.COVERAGE)
    parallel = hg.driver.roll_pool(specs, jobs=2, produce=stub_produce)
    serial = hg.driver.roll_pool(specs, jobs=1, produce=stub_produce)
    assert [r.plan.spec for r in parallel] == specs == [r.plan.spec for r in serial], "in order, every spec, both paths"
    assert [r.line() for r in parallel] == [r.line() for r in serial]
    assert all(r.path is None and r.ok for r in parallel)
