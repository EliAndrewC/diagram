"""tier city tests split out of `tests.settlement.test_water_ways` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _walled


@pytest.mark.tiers("city")
def test_mausoleum_yields_walls_to_abutting_ward_fences():
    # a wall that runs along a ward fence is re-stamped (the fence renders ON TOP - the wall runs
    # underneath); exercises both the horizontal- and vertical-fence branches of _ward_fence_cap
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="C", scale="city")
    s.ward("a", [(400, 600), (900, 600)], [])  # horizontal fence at y=600
    s.mausoleum(600, 627, 54, 40, gate_dir="south")  # north wall y0=607 runs along it -> yields north
    assert s.M["mausoleums"][-1]["ward_walls"] == ["north"]
    s.ward("b", [(1200, 400), (1200, 900)], [])  # vertical fence at x=1200
    s.mausoleum(1227, 650, 54, 40, gate_dir="east")  # west wall x0=1200 runs along it -> yields west
    assert "west" in s.M["mausoleums"][-1]["ward_walls"]
    # a fence that is parallel + aligned but does NOT overlap the wall's extent -> no yield (both axes)
    s.ward("c", [(100, 200), (200, 200)], [])  # horizontal fence far left of...
    s.mausoleum(700, 227, 54, 40, gate_dir="south")  # ...this north wall (no x-overlap)
    assert "north" not in s.M["mausoleums"][-1]["ward_walls"]
    s.ward("d", [(1500, 100), (1500, 250)], [])  # vertical fence high above...
    s.mausoleum(1527, 650, 54, 40, gate_dir="east")  # ...this west wall (no y-overlap)
    assert "west" not in s.M["mausoleums"][-1]["ward_walls"]


@pytest.mark.tiers("city")
def test_ward_fence_end_snaps_onto_the_wall_ALONG_ITS_OWN_AXIS():
    # GM 2026-07-27: "the neighborhood walls stick out the other side of the city walls". The end is
    # placed 20px past the north rampart (y200) on an OBLIQUE run, which is what separates the two
    # candidate fixes: trimming back along the fence's own terminal segment lands at x=556.8, while
    # a perpendicular snap to the nearest point on the wall would land at x=560 and kink the last
    # stretch off the line the gen drew. Same rule city_streets_meet_through_lanes states for a lane.
    s = _walled()
    s.ward("samurai", [(500, 560), (560, 180)], gates=[])
    end = s.M["wards"][-1]["boundary"][-1]
    assert end == pytest.approx([556.8, 200.0], abs=0.1)
    assert s.M["wards"][-1]["stroke"] == 5.0 and s.M["wall_stroke"] == 11.0


@pytest.mark.tiers("city")
def test_ward_fence_end_far_from_the_wall_is_left_exactly_where_the_gen_put_it():
    # an end nowhere near the rampart is not a junction at all but a fence that FAILS to reach it -
    # city_ward_fence_meets_wall's defect to report. Dragging it silently would hide that.
    s = _walled()
    s.ward("samurai", [(500, 700), (500, 400)], gates=[])
    assert s.M["wards"][-1]["boundary"][-1] == [500.0, 400.0]


@pytest.mark.tiers("capital")
def test_quarter_accepts_the_capital_zones():
    """021: "castle" and "samurai" are legal quarter zones (capital vocabulary) - the citadel
    and the senior bands tile the interior without entering the residential density body."""
    s = _crop_settlement()
    s.quarter([(100, 100), (400, 100), (400, 400), (100, 400)], "castle")
    s.quarter([(400, 100), (700, 100), (700, 400), (400, 400)], "samurai")
    assert [q["zone"] for q in s.M["quarters"]] == ["castle", "samurai"]


@pytest.mark.tiers("capital")
def test_kido_mesh_reserves_and_gates_every_machi_mouth():
    """kido_mesh derives its gates from the SAME machi_mouths source the validator reads and
    reserves each gate's ground before the packs (021; the wip capital was its only exerciser)."""
    s = Settlement(1000, 1000, seed=3)
    s.street([(200, 500), (800, 500)])
    s.district("test machi", "machi", [(300, 400), (700, 400), (700, 600), (300, 600)], rank_band=None)
    before = len(s.block_polys)
    n = s.kido_mesh()
    assert n == len(s.M.get("kido", []))
    if n:
        assert len(s.block_polys) > before  # each kido reserved its ground


@pytest.mark.tiers("city")
def test_a_dense_row_seats_shops_closer_than_a_default_row():
    """A machiya row is a CONTINUOUS street wall - shops share party walls and the frontage reads
    as one built edge. The default row measures its neighbors with the rotation-invariant collision
    circle, which forces a 46x28 shop 57.8 px from the next where the true touching distance is 28,
    so a commercial street comes out as a dotted line of boxes. dense=True measures row mates edge
    to edge along the row's own axis instead. Opt-in, because it re-rolls any map that takes it."""
    street = [(200, 100), (200, 900)]

    def run(dense):
        s = settlement.Settlement(1000, 1000, seed=7)
        s.meta(scale="city", ftpx=3)
        s.street(street, width=s.lw(18))
        # both=False puts every seat in ONE file, which is where the two rules differ: an 18x12
        # merchant needs 25.6 px of pitch under the collision circle and 19.5 px measured edge to
        # edge, so a 20 px pitch is refused by the first and accepted by the second.
        return s.frontage(street, ["merchant"] * 40, width=8, spacing=20, setback=14, both=False, dense=dense)

    loose, tight = run(False), run(True)
    assert tight > loose, f"a dense row should seat MORE shops on the same street ({tight} vs {loose})"


@pytest.mark.tiers("city")
def test_a_dense_row_sits_inside_the_band_of_the_way_it_lines():
    """The shops LINING a street stand inside that street's own cleared band - the band exists to
    keep OTHER things off the way. A dense row skips the fronted stretch even when the gen wrote it
    as its own two-point list rather than passing the registered street object (the identity match
    that silently cost the pool two thirds of its commercial frontage)."""
    street = [(200, 100), (200, 900)]

    def run(dense):
        s = settlement.Settlement(1000, 1000, seed=3)
        s.meta(scale="city", ftpx=3)
        s.street(street, width=s.lw(30))  # a wide way: its band reaches past a short setback
        return s.frontage([(200, 150), (200, 850)], ["merchant"] * 24, width=6, spacing=26, setback=2, both=False, dense=dense)

    assert run(True) > run(False), "a row must not be refused by the cleared band of the way it fronts"


@pytest.mark.tiers("city")
def test_a_dense_row_refuses_a_mate_that_would_overlap_it():
    """Measuring row mates edge to edge is a RELAXATION of the collision circle, not an abdication:
    two seats in one file still may not interpenetrate, or a tight commercial pitch draws shops
    through each other."""
    street = [(200, 100), (200, 900)]
    s = settlement.Settlement(1000, 1000, seed=5)
    s.meta(scale="city", ftpx=3)
    s.street(street, width=s.lw(18))
    n = s.frontage(street, ["merchant"] * 40, width=8, spacing=9, setback=14, both=False, dense=True)
    B = [b for b in s.M["buildings"] if b["kind"] == "merchant"]
    assert n < 40, "a pitch below the footprint width must refuse seats, not stack them"
    for i, a in enumerate(B):
        for b in B[i + 1 :]:
            assert not (abs(a["x"] - b["x"]) < (a["w"] + b["w"]) / 2 - 0.5 and abs(a["y"] - b["y"]) < (a["h"] + b["h"]) / 2 - 0.5), "row mates interpenetrate"


@pytest.mark.tiers("city")
def test_a_dense_row_still_leaves_the_mouth_of_a_crossing_street_clear():
    """The relaxation is scoped to the way being LINED. A street crossing the row is a different
    way with its own cleared band, and the row must break at the junction - a shop built across the
    mouth of a side street is exactly what the corridor rule exists to prevent."""
    spine = [(200, 100), (200, 900)]
    cross = [(60, 500), (940, 500)]  # long, so its midpoint is nowhere near the spine
    s = settlement.Settlement(1000, 1000, seed=13)
    s.meta(scale="city", ftpx=3)
    s.street(spine, width=s.lw(18))
    s.street(cross, width=s.lw(24))
    s.frontage(spine, ["merchant"] * 30, width=6, spacing=20, setback=4, both=False, dense=True)
    at_mouth = [b for b in s.M["buildings"] if b["kind"] == "merchant" and abs(b["y"] - 500) < 16]
    assert not at_mouth, f"the row built across the crossing street's mouth: {[(b['x'], b['y']) for b in at_mouth]}"
