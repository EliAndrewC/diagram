"""gate tests split out of `tests.hamletgen.test_driver` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests import rolls
from tests.gate import _pool


@pytest.mark.rolls_map
def test_a_rolled_cohort_passes_the_whole_gate() -> None:
    """The experiment's actual claim, in miniature: hamlets rolled from the coverage specs come out correct.

    WHAT IS LEFT AFTER FEATURE 287 (specs/287-placer-guarantees/research.md R8), each KEPT for a correctness no placer
    unit test covers:
    - THE ACREAGE lands within 15% of the figure the household count implies, on EVERY member. The `ACREAGE_SHORT`
      excuse (seeds 45 and 47, neither a member here since feature 214) is removed (FR-006), but the rule is not yet
      guaranteed for a fan: `hamletgen/water/fit.py:fit_field` keeps its closest miss with no band and no refusal, and
      the canvas sized for the fan's square (`plan.py`) is a cohort measurement, not a decision. The polder's half is
      guaranteed (`fit_polder` returns only inside `polder_acres_in_band` or refuses).
    - THE ROLL'S OWN VERDICT is clean: `Report.failures` is the driver's self-report of `farmhouses_reach_a_way`, which
      spans the seating's corridors and the web's settle pass - a property no single placer owns, and one the driver
      reports rather than refuses. `GATE_COHORT_EXPECTED` (empty since feature 166) and its pins went with FR-006.
    The seating clause (`placed >= round(0.85 * households)`) was retired: every household is seated or the site refused
    (`homesteads/stages.py:seat_every_household`, `SiteRefused`, `tests/hamletgen/homesteads/test_capacity.py`).

    THE POPULATION IS THE ROSTER'S COVERAGE ROLLS (feature 214, GM 2026-09-08), read through the pool: the plain shared
    rolls every gate makes anyway, not a cohort of seeds rolled for this test alone."""
    specs = list(rolls.COVERAGE)
    reports = [_pool.rolled_report(spec) for spec in specs]
    assert len(reports) == len(specs)
    for report in reports:
        assert abs(report.plan.acres - report.plan.target_acres) / report.plan.target_acres < 0.15, (
            f"{report.plan.spec.name}: {report.plan.acres:.1f} acres against a {report.plan.target_acres:.1f} target"
        )
    failing = {r.plan.spec.name: list(r.failures) for r in reports if r.failures}
    assert not failing, f"a coverage roll reports failures: {failing}"
