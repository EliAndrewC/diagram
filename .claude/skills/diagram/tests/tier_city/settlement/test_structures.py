"""tier city tests split out of `tests.settlement.test_structures` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _cap020, _city, _town


@pytest.mark.tiers("city")
def test_fill_declares_a_capacity_budget_and_stays_silent(capsys):
    # fill=True marks the request as "place up to N" (the city district-fill idiom), so an
    # under-fill is intended, not drift - no warning
    s = _town()
    s.pack((100, 100, 130, 130), ["merchant"] * 3, fill=True)
    s.frontage([(100, 500), (160, 500)], ["merchant"] * 8, fill=True)
    assert "SHORTFALL" not in capsys.readouterr().out


@pytest.mark.tiers("city")
def test_rowpack_lays_touching_terraces():
    # the GM row-packing doctrine: city commoner housing goes down as CONTIGUOUS terraces -
    # most units share a party wall (hairline seam <= 1.2px), never the old detached scatter
    s = _city()
    n = s.rowpack((200, 200, 600, 330), ["laborer"] * 40)
    assert n >= 25
    bs = s.M["buildings"]

    def egap(a, b):
        dx = abs(a["x"] - b["x"]) - (a["w"] + b["w"]) / 2
        dy = abs(a["y"] - b["y"]) - (a["h"] + b["h"]) / 2
        return max(dx, dy)

    gaps = [min(egap(a, b) for j, b in enumerate(bs) if j != i) for i, a in enumerate(bs)]
    assert sum(1 for g in gaps if g <= 1.2) >= 0.55 * len(bs)


@pytest.mark.tiers("city")
def test_rowpack_respects_canvas_edge_and_bound():
    # rows must not spill off the canvas margins (title/edge zone) or outside a bounding
    # ring (the city's ring road) - both rejections clip the terrace, they don't crash it
    s = _city()
    s.rowpack((20, 200, 200, 260), ["laborer"] * 30)  # zone hangs past the x<55 edge margin
    assert all(b["x"] - b["w"] / 2 >= 55 for b in s.M["buildings"])
    s2 = _city()
    s2.bound = [(300, 100), (700, 100), (700, 500), (300, 500)]
    s2.rowpack((200, 200, 600, 300), ["laborer"] * 30)  # zone's west half lies outside the bound
    assert all(b["x"] - b["w"] / 2 >= 299 for b in s2.M["buildings"])


@pytest.mark.tiers("city")
def test_ministry_auto_label_side_prefers_empty_ground():
    # the GM label doctrine (2026-07): a label that CAN sit in empty ground, should. With no
    # label_below override the ministry scores both spots against what is already placed and
    # takes the clearer; the default (unpassed) size is the real ~224x148 ft compound.
    s = Settlement(1000, 1000, seed=4)
    s.meta(name="C", scale="city", ftpx=3)
    s.building(500, 462, 90, 24, "civic")  # crowd the ABOVE label spot
    s.ministry(500, 510, "Ministry of Test")
    assert s.M["ministries"][0]["w"] == s.px(224)
    lab = next(lb for lb in s.M["labels"] if lb[5] == "Ministry of Test")
    assert (lab[1] + lab[3]) / 2 > 510  # the label went BELOW, into the open ground


@pytest.mark.tiers("city")
def test_merchant_estates_rolls_seats_and_records_the_target():
    import random as _rr

    from l7r.diagram.settlement import roll_merchant_estate_count

    s = Settlement(1200, 1200, seed=11)
    s.meta(name="c", scale="city", ftpx=3)
    expect = roll_merchant_estate_count("city", _rr.Random(11 * 1201 + 89))  # the method's dedicated stream
    n = s.merchant_estates([(300, 300, "south"), (600, 300, "south"), (300, 600, "east")])
    assert n == expect
    assert len(s.M["merchant_estates"]) == n
    assert s.M["meta"]["merchant_estate_roll"] == n


@pytest.mark.tiers("city")
def test_merchant_estates_pin_overrides_the_roll():
    s = Settlement(1200, 1200, seed=11)
    s.meta(name="c", scale="city", ftpx=3)
    n = s.merchant_estates([(300, 300, "south"), (600, 300, "south"), (300, 600, "east")], count=2)
    assert n == 2
    assert len(s.M["merchant_estates"]) == 2
    assert s.M["meta"]["merchant_estate_roll"] == 2


@pytest.mark.tiers("city")
def test_merchant_estates_raises_when_seats_run_short():
    s = Settlement(1200, 1200, seed=11)
    s.meta(name="c", scale="city", ftpx=3)
    with pytest.raises(ValueError, match="vetted seats"):
        s.merchant_estates([(300, 300, "south")], count=3)


@pytest.mark.tiers("city")
def test_place_punishment_spot_declines_when_no_verge_is_within_the_siting_band():
    # At a very coarse grain the ~60-real-ft band is narrower than the road's own tread plus the
    # feature, so no candidate offset is legal at all - the siter must return None, not guess.
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="C", scale="city", ftpx=30)
    s.road([(100, 500), (900, 500)])
    assert s.place_punishment_spot() is None


@pytest.mark.tiers("city")
def test_martial_hall_caption_takes_the_emptier_side():
    # "martial hall" is wide relative to a 43x33 px compound, so the caption side is a real
    # decision: a hall seated beside the yamen would otherwise drop its label on the governor.
    s = Settlement(1200, 1200, seed=3)
    s.meta(name="C", scale="city", ftpx=3)
    s.building(400, 440, 120, 40, kind="samurai")  # a neighbor directly BELOW the hall's seat
    s.martial_hall(400, 400)
    lab = [L for L in s.M["labels"] if len(L) > 5 and L[5] == "martial hall"][0]
    assert lab[1] < 400  # pushed ABOVE the compound, away from the occupied side


@pytest.mark.tiers("city")
def test_servant_ranges_is_a_noop_without_a_ward():
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="W", scale="city", ftpx=3)
    s.building(600, 600, *s._dims("samurai"), "samurai", 0.0)
    assert s.servant_ranges() == 0


@pytest.mark.tiers("city")
def test_manor_label_inside_fits_the_court():
    """A city estate's caption lives INSIDE the blank court (GM 2026-08-09), sized to clear the
    walls - and a small estate gets a smaller face rather than an overflowing one."""
    s = _cap020()
    s.manor(700, 700, 150, 118, "Hazama Estate", label_inside=True)
    lines = [L for L in s.M["labels"] if len(L) > 5 and L[5] in ("Hazama", "Estate")]
    assert len(lines) == 2  # split over two lines so the face runs bigger (GM 2026-08-09)
    for box in lines:
        assert box[0] > 625 and box[2] < 775 and box[1] > 641 and box[3] < 759  # fully inside the court
    s2 = _cap020()
    s2.manor(700, 700, 70, 54, "Lone", label_inside=True)  # a one-word label keeps the single line
    assert any(len(L) > 5 and L[5] == "Lone" for L in s2.M["labels"])


@pytest.mark.tiers("capital", "city")
def test_a_dense_row_lines_a_way_that_bends_inside_the_fronted_stretch():
    """The fronted stretch and the way's own corridor segments rarely coincide: a road runs the
    height of the map and a shop row lines 500 px of it, and the road BENDS inside that stretch.
    Matching a segment only when the whole stretch lies on it left the way's cleared band refusing
    the shops meant to line it - 325 refusals on the capital's Imperial road. A dense row counts a
    segment as running along the stretch if EITHER contains the other."""
    # a real road is a polyline of SHORT segments with a slight drift, so no one segment contains
    # the whole stretch a shop row lines - which is the case that used to match nothing at all
    road = [(300, 100), (300, 400), (305, 700), (310, 1000)]

    def run(dense):
        s = settlement.Settlement(1000, 1000, seed=11)
        s.meta(scale="city", ftpx=3)
        s.road(road, width=s.lw(30))
        # the row is written as its OWN two-point stretch spanning several road segments, which is
        # how a gen writes a sub-stretch - not the road object the corridor was registered with
        return s.frontage([(300, 150), (308, 950)], ["merchant"] * 24, width=6, spacing=26, setback=2, both=False, dense=dense)

    assert run(True) > run(False), "a dense row must not be refused by the band of the way it lines"
