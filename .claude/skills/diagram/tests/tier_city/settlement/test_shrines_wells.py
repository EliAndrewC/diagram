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


# ---- feature 174: the three shrine glyphs no hamlet draws ----------------------------------------
# 56 of the module's 116 statements. A hamlet has no shrine at all (the kind follows settlement
# scale: villages have shrines, towns monasteries, cities temples), so these three had never run.
# Each is a direct drawing call, and each carries a REAL rule worth pinning rather than a line count.


def test_the_hill_records_its_own_footprint_and_its_summit_separately() -> None:
    """The keep-outs downstream code reads: `M['hill']` is the whole mound (the not-hill predicate
    inflates it), `M['summit']` the crown a shrine may stand on. They are different ellipses, and
    the hill is also pushed onto `ellipses`, which is what makes it block placement."""
    s = Settlement(1200, 1200, seed=3)
    s.hill(600.0, 600.0, 200.0, 150.0)
    assert s.M["hill"] == [600.0, 628.0, 200.0, 150.0], "the base ring, offset south of the center"
    assert s.M["summit"][2] < s.M["hill"][2], "the summit is the small crown, not the mound"
    assert (600.0, 628.0, 200.0, 150.0) in s.ellipses, "and the mound blocks placement"


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


def test_a_small_shrine_is_recorded_as_RELIGIOUS_and_not_as_a_dwelling() -> None:
    """A wayside shrine is non-residential: it goes to `M['religious']` as kind `small_shrine`, so
    it is neither housing nor a full temple owed a torii avenue."""
    s = Settlement(1000, 1000, seed=5)
    s.small_shrine(400.0, 400.0)
    rec = s.M["religious"][-1]
    assert rec["kind"] == "small_shrine"
    assert (rec["w"], rec["h"]) == (s.px(32), s.px(24)), "~32x24 ft, converted at the map's ftpx"
    assert not s.M.get("houses"), "and it is not counted as a dwelling"


def test_a_halls_caption_is_kept_out_of_its_OWN_sando() -> None:
    """GM 2026-07-27: an arch must "never be covered by the 'temple of X' label".

    A hall's caption and its approach both want the ground at the hall's face, so they collided -
    three times in the shipped pool before this rung existed (Minami's 'Temple of Bishamon' and
    Hoshizora's 'Monastery of Bishamon' each sat on their own arch, Kikuta's 'Shrine to Benten' on
    its sando).

    THREE candidate baselines in a STRICT ORDER, and each rung is asserted separately, because a
    ladder tested only at its top is a ladder with one rung:
      1. the side the gen asked for, when nothing is there;
      2. that same side pushed clear PAST the far end of the avenue;
      3. the opposite side.
    And when all three are fouled the REQUESTED side stands - the engine does not get to hide a map
    that has no room for both.
    """
    s = Settlement(1200, 1200, seed=6)
    s.meta(name="C", scale="city")
    x, y, w, h = 600.0, 600.0, 120.0, 82.0

    free = s._hall_caption_y(x, y, w, h, "Temple of Bishamon", label_below=False, seats=[])
    assert free < y, "rung 1: with no avenue at all, the gen's own side stands"

    # an avenue marching AWAY below the hall: the requested side (above) is clear, so it still wins
    below_seats = [(x, y + 120.0), (x, y + 180.0), (x, y + 240.0)]
    assert s._hall_caption_y(x, y, w, h, "Temple of Bishamon", label_below=False, seats=below_seats) == free

    # ...and when the gen asks for the side the arches are ON, the caption must move off them
    moved = s._hall_caption_y(x, y, w, h, "Temple of Bishamon", label_below=True, seats=below_seats)
    fouls = [ty for _, ty in below_seats]
    assert not (min(fouls) - 30 < moved < max(fouls) + 30), f"the caption cleared the sando ({moved})"


def test_a_canvas_filling_forest_records_its_TREE_LINE_apart_from_its_polygon() -> None:
    """The two are recorded separately because the frame reveals only a shallow band of wood past
    the tree line - deeper in it is undifferentiated canopy, i.e. wasted image (`crop_to_content`,
    and `forest_reveal_x` is the shared rule).

    Also asserted: the litter floor is pushed a crown's width BACK from the tree line, so its
    straight edge lies UNDER the canopy and the trees alone make the wood's edge - without that, a
    ruler-straight litter line gives the wood a drawn border no forest has.
    """
    s = Settlement(1400, 1400, seed=12)
    s.meta(name="C", scale="city")
    edge = [(800.0, 100.0), (820.0, 500.0), (790.0, 900.0), (810.0, 1300.0)]
    before = len(s.block_polys)
    s.forest(edge)

    assert s.M["forest_edge"] == [[round(x, 1), round(y, 1)] for x, y in edge], "the tree line, as given"
    assert s.M["forest"] != s.M["forest_edge"], "and the filled polygon, which runs on to the canvas"
    assert max(p[0] for p in s.M["forest"]) > 1400.0, "the wood is drawn PAST the canvas edge"
    assert len(s.block_polys) == before + 1, "and it blocks houses"


def test_a_forest_is_DETERMINISTIC_so_it_never_perturbs_house_placement() -> None:
    """Its RNG is saved and restored, which is what lets a wood be drawn mid-map without moving
    everything placed after it. Asserted by drawing the same wood twice and by checking the stream
    that follows is unchanged - the property a saved/restored RNG actually buys."""
    edge = [(800.0, 100.0), (820.0, 700.0), (810.0, 1300.0)]
    a = Settlement(1400, 1400, seed=12)
    a.meta(name="C", scale="city")
    a.forest(edge)

    b = Settlement(1400, 1400, seed=12)
    b.meta(name="C", scale="city")
    b.forest(edge)
    assert a.M["forest"] == b.M["forest"], "the same wood twice, identically"
