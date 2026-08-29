"""tier city tests split out of `tests.settlement.test_shrines_wells` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _caption_size


@pytest.mark.tiers("city")
def test_avenue_at_threshold_leaves_a_degenerate_avenue_alone():
    # nothing to seat, and an arch drawn ON the hall is torii_clear_of_shrine's defect to report -
    # this method translates a sando, it does not paper over a broken one
    s = Settlement(600, 600, seed=1)
    s.meta(name="T", scale="city", ftpx=3, down_deg=90)
    assert s._avenue_at_threshold(300, 300, 40, 30, []) == []
    on_the_hall = [(300.0, 300.0), (300.0, 320.0)]
    assert s._avenue_at_threshold(300, 300, 40, 30, on_the_hall) == on_the_hall


@pytest.mark.tiers("city")
def test_a_hall_caption_is_the_same_size_as_a_ministry_caption():
    # GM 2026-08-08: a caption is sized by its GLYPH, not by the institution's rank. A city temple
    # hall and a ministry office are the same size class of building (96-140 ft against 114-140),
    # so their captions match; the temple's greater standing shows in red and bold, not in points.
    s = Settlement(1400, 1400, seed=5)
    s.meta(name="C", scale="city", ftpx=3)
    s.shrine_hall(400, 400, "Temple of Benten", w=s.px(130), h=s.px(84), kind="temple")
    s.ministry(900, 400, "Ministry of Rites")
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    temple = next(lb for lb in s.M["labels"] if lb[5] == "Temple of Benten")
    ministry = next(lb for lb in s.M["labels"] if lb[5] == "Ministry of Rites")
    assert _caption_size(temple) == _caption_size(ministry) == settlement.HALL_CAPTION_FS
    # per CHARACTER the two now advance identically - the defect was a temple caption ~44% wider
    # per character than the ministry caption standing 500px away from it
    assert (temple[2] - temple[0]) / len(temple[5]) == pytest.approx((ministry[2] - ministry[0]) / len(ministry[5]), abs=0.01)


@pytest.mark.tiers("city")
def test_shrine_hall_guard_refuses_unscaled_pixels_at_coarse_scales():
    # the latent-footgun guard (2026-07-21): four city temples shipped as fixed 100x64 px = 300x192 real ft.
    # At any ftpx > 1, raw-pixel dims implying an impossible hall must raise; s.px(real_ft) passes.
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="G", scale="city", ftpx=3, toscale=True, households=600)
    with pytest.raises(ValueError, match="pass s.px"):
        s.shrine_hall(500, 500, "Temple", w=100, h=64, kind="temple")
    s.shrine_hall(500, 500, "Temple", w=s.px(130), h=s.px(84), kind="temple")
    assert any(r["kind"] == "temple" for r in s.M["religious"])


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
