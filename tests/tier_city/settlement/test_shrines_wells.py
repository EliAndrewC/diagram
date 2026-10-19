"""tier city tests split out of `tests.settlement.test_shrines_wells` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("city")
def test_open_seat_refuses_a_seat_whose_FOOTPRINT_crosses_the_bound():
    """The martial-hall bug, as a unit test (GM 2026-07-25). s.bound is the ring-road loop a city
    packs inside, and `_fits` tests only a candidate's CENTER against it - so open_seat handed back
    a compound seat whose SE corner lay across Tango's patrol bed. open_seat now tests the whole
    footprint against the bound (and ONLY the bound: block polys and corridors are soft
    reservations a footprint may legitimately overhang, and tightening those cost two pool maps a
    feature apiece when it was tried)."""
    s = Settlement(1200, 1200, seed=3)
    s.meta(name="C", scale="city", ftpx=3)
    s.bound = [[100, 100], [700, 100], [700, 700], [100, 700]]
    over = (665, 300, 695, 320)  # every candidate here keeps its CENTER inside x=700 but its right edge past it
    assert s.open_seat(over, 80, 20) is None
    assert s.open_seat(over, 80, 20, footprint=False) is not None  # the old center-only behavior
    assert s.open_seat((300, 300, 400, 320), 80, 20) is not None  # well inside the bound: fine


@pytest.mark.tiers("city")
def test_open_seat_disc_uses_the_true_radius_of_a_round_candidate():
    """A wellhead is a DISC, so its reach is its radius - not the half-diagonal of the probe box
    around it, which is the documented over-restriction in this skill's CLAUDE.md. Exact rather
    than a relaxation, and opt-in: the derived well grid leans on the conservative radius as its
    padding, and making it exact there put a wellhead on a building."""

    def seat(disc):
        s = settlement.Settlement(600, 600, seed=9)
        s.meta(scale="city", ftpx=3)
        s.placed.append((300.0, 300.0, 40.0, 40.0))  # one standing footprint in the middle
        return s.open_seat((296, 330, 340, 372), 16, 16, step=2.0, footprint=False, disc=disc)

    loose, exact = seat(False), seat(True)
    assert exact is not None, "the exact disc reach must find the gap the half-diagonal refuses"
    assert loose is None or math.hypot(exact[0] - 300, exact[1] - 300) <= math.hypot(loose[0] - 300, loose[1] - 300)


# ---- feature 174: the three shrine glyphs no hamlet draws ----------------------------------------
# 56 of the module's 116 statements. A hamlet has no shrine at all (the kind follows settlement
# scale: villages have shrines, towns monasteries, cities temples), so these three had never run.
# Each is a direct drawing call, and each carries a REAL rule worth pinning rather than a line count.


def test_a_village_shrine_is_drawn_in_REAL_FEET_not_pixels() -> None:
    """GM 2026-07-21. The old signature took fixed PIXELS with a 104x68 default - a latent footgun
    that would have drawn a 208x136 ft monastery-sized hall on any village taking the default
    civic_shrine path. The defaults are ~62x42 REAL FEET now, converted through `px()`.

    Asserted at two scales, because a test at one ftpx cannot tell feet from pixels.
    """
    one = Settlement(1000, 1000, seed=1)
    two = Settlement(1000, 1000, seed=1)
    two.meta(ftpx=2)  # the scale is declared through meta(), not the constructor
    assert one.px(62) == 62.0 and two.px(62) == 31.0, "the same real hall is drawn smaller on a coarser map"
    one.shrine(500.0, 500.0)
    two.shrine(500.0, 500.0)
    assert one.out and two.out, "and both draw their hall"
