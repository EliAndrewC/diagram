"""THE BRANCHES EIGHT COHORT SEEDS REACHED AND FOUR DID NOT (feature 147).

Feature 145 raised the full run's cohort from four seeds to eight for one reason, recorded in
`gate/hamletgen/test_driver.py`: *"the hamlet-path floor counts what these in-process rolls execute, and the
seed-dependent placer branches ... are reached by rolls, not by a fixture; four more seeds (~50 s in FULL)
reach what four did not."* Measured 2026-08-29, that is TEN lines across seven modules, bought for ~66 s of
every full sweep.

Buying coverage with seeds is also FRAGILE in a way a test is not: which lines eight particular seeds reach
is an accident of the roll, so a knob change that re-rolls them can drop a line the suite was relying on,
for reasons that have nothing to do with the code under test. Feature 146 established the alternative - reach
the branch directly - and these are that, one per line, so the cohort can go back to four seeds and keep its
pass-rate ratchet without carrying the coverage on its back.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _hamlet() -> Settlement:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, down_deg=90, water_flow=90)
    return s


def test_a_wellhead_may_not_be_sunk_in_the_reed_toe_below_the_crop() -> None:
    """`_well_ground_clear`'s wet-toe arm. The reeds are drawn LATE - after the structures - so by the time
    they exist the well is already in them; the band is therefore DERIVED at seat time from the same geometry
    the reeds will use. The arm only runs on a map that has a toe at all, which is hamlet and village scale."""
    s = _hamlet()
    s.field_polys.append([(300.0, 400.0), (1100.0, 400.0), (1100.0, 800.0), (300.0, 800.0)])
    s.M["fields"] = [{"name": "p", "kind": "paddy", "outline": [[300, 400], [1100, 400], [1100, 800], [300, 800]], "bbox": [300, 400, 1100, 800]}]
    toe, low, _dv, _uv, _u_lo, _u_hi = s._wet_toe_keepout()
    assert toe, "the fixture must actually have a toe band, or this proves nothing"
    assert not s._well_ground_clear(700.0, 850.0), "downslope of the collector, inside the toe: reed bog"


# RETIRED (feature 287 wave 5, FR-005/FR-007): `test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied` rolled
# the fit at an unreachable 500-acre target and asserted a fan came back - the closest miss `fit_field` no longer keeps. Such
# a site is refused (`FieldRefused`) after every aspect is searched in full: tests/hamletgen/test_fit_flanks.py, on stand-in
# carves; the best aspect's full re-search is `tests/hamletgen/test_water.py::test_fit_field_probes_saturation_and_rerolls_the_best_aspect_in_full`.
