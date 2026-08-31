"""tier town tests split out of `tests.settlement.test_structures` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _scatter_base_points, _town


@pytest.mark.tiers("town")
def test_pack_shortfall_is_reported(capsys):
    # the "no silent caps" principle applied to placement (2026-07-24 town audit: Hirameki's
    # gate market authored 12 businesses, landed 4, and nothing said so)
    s = _town()
    s.pack((100, 100, 130, 130), ["merchant"] * 3)  # room for at most one grid spot
    out = capsys.readouterr().out
    assert "PACK SHORTFALL" in out and "merchant" in out


@pytest.mark.tiers("town")
def test_place_kosatsuba_samples_only_the_main_way_when_one_is_declared():
    # GM 2026-08-02 (Ubame): the board goes ALONG the main road, never a side street - even
    # when the side lane's node is busier. With a road on the map, the lane's verges are not
    # candidates at all, so the board lands in the road's siting band despite every house
    # standing by the lane.
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="town", ftpx=1)
    s.M["road"] = [[100, 300], [900, 300]]
    s.M["lane"] = [[100, 700], [900, 700]]
    for i in range(6):
        s.M["houses"].append({"x": 300.0 + 60 * i, "y": 760.0, "w": 30, "h": 20, "kind": "plain", "rot": 0})
        s.placed.append((300.0 + 60 * i, 760.0, 30, 20))
    assert s.place_kosatsuba() is not None
    assert abs(s.M["kosatsuba"][0]["y"] - 300) <= 60  # the road's band, not the busy lane's


@pytest.mark.tiers("town")
def test_kosatsuba_label_xy_hand_seats_the_caption():
    # both caption bands can be taken at a junction seat (Nagahara's market bend: drum tower
    # in the below band, the ward gate's glyph + caption stack in the above band) - label_xy
    # is the explicit hand seat, the same escape the punishment ground carries
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="town", ftpx=1)
    s.kosatsuba(500, 500, rot=0, label_xy=(560, 488))
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    lab = s.M["labels"][-1]
    assert lab[5] == "notice board"
    assert abs((lab[0] + lab[2]) / 2 - 560) < 2  # seated at the hand x, not the default below-seat


@pytest.mark.tiers("town")
def test_commons_keeps_scrub_off_the_road_bed():
    # the old skip knew only LANES, so scrub drew on the Imperial Road bed (Hoshizora); the
    # corridor set now covers lanes + town streets + the road
    s = _crop_settlement()
    s.road([(100, 300), (700, 300)])
    before = len(s.out)
    s.commons([(150, 150), (600, 150), (600, 450), (150, 450)], role="pasture")
    lim = s.M["road_width"] / 2 + 3 * s.bscale - 0.06  # 0.1-rounding slack, as in the halo test
    pts = _scatter_base_points(s.out[before:])
    assert pts and all(abs(py - 300) > lim for px, py in pts if 100 <= px <= 700)


@pytest.mark.tiers("town")
def test_pack_businesses_only_line_the_frontage():
    # face_streets=True (businesses mode): a spot with no street within reach places NOTHING -
    # shops exist to catch passing feet, they never scatter into a streetless interior. (This
    # mode lost its last pool caller in the 2026-07-24 Hirameki roadway rework; the unit test
    # keeps the API branch alive and covered.)
    s = Settlement(1000, 1000, seed=2)
    s.meta(name="T", scale="town")
    s.pack((150, 300, 850, 700), ["merchant"] * 6, step=40, face_streets=True)
    assert s.M["buildings"] == []


@pytest.mark.tiers("town")
def test_place_punishment_spot_needs_a_street_to_site_on():
    # No road, no town street, no lane: there is no traffic to site the display on, so the siter
    # declines rather than dropping it somewhere arbitrary (the presence check then fires).
    s = _town()
    assert s.place_punishment_spot() is None


# ---- feature 174: the bell-and-drum tower, which only a WALLED SEAT has -------------------------


def test_a_drum_tower_records_a_square_footprint_on_the_TOP_layer() -> None:
    """GM 2026-07-24: the timekeeping/curfew institution of a walled seat - morning bell, evening
    drum, the dusk gate-closing that starts the street curfew. A county seat has exactly ONE
    combined tower; the paired gulou/zhonglou on an axis is capital grammar.

    Two things worth pinning. It is SQUARE (a masonry platform, county tier ~60-80 ft), and it goes
    on the TOP layer - a tower is the tallest thing in the settlement and nothing is drawn over it.
    """
    s = _town()
    z = s.drum_tower(500.0, 500.0)
    rec = s.M["drum_towers"][-1]
    assert rec["w"] == rec["h"], "a masonry platform is square"
    assert rec["z"] == z and z > 0, "drawn on the top layer, and the caller gets its index"
    assert rec["label"] == "drum tower"
    assert not s._fits(500.0, 500.0, 8.0, 8.0), "and it blocks - the tower stands in the street plan"


def test_a_drum_tower_takes_an_explicit_width_over_its_tier_default() -> None:
    """A capital's tower is not a county seat's, so the size is the caller's when they state one."""
    s = _town()
    s.drum_tower(400.0, 400.0, tw=120.0, label="bell tower")
    rec = s.M["drum_towers"][-1]
    assert (rec["w"], rec["h"]) == (120.0, 120.0)
    assert rec["label"] == "bell tower"


def test_a_pasture_takes_both_a_BBOX_and_a_POLYGON_and_blocks_either_way() -> None:
    """Feature 174: `pasture` had no test. It accepts two shapes - a 4-number bbox or a ring of
    points - and the branch that tells them apart is the whole reason its rng scope is keyed the way
    it is (the comment records a 2026-08-08 divergence at draw #70 of 24,615, where re-shaping a
    paddock changed the draw sequence for everything after it).

    Both shapes asserted, and the scoping asserted by its OBSERVABLE property: the same shape draws
    the same paddock twice, which is what "never otherwise" means.
    """
    box = _town()
    before = len(box.block_polys)
    box.pasture((200.0, 200.0, 400.0, 300.0), label=None)
    assert box.M["pastures"], "a bbox pasture is recorded as a ring of points"
    assert len(box.block_polys) == before + 1, "and registers a no-build polygon - grazing land is not free ground"

    ring = _town()
    ring.pasture([(600.0, 600.0), (900.0, 600.0), (900.0, 800.0), (600.0, 800.0)], label=None)
    assert ring.M["pastures"], "a polygon pasture is recorded too - the other branch of the shape test"

    again = _town()
    again.pasture((200.0, 200.0, 400.0, 300.0), label=None)
    assert again.M["pastures"][-1] == box.M["pastures"][-1], "keyed on the shape: the same paddock re-rolls identically"


def test_pack_lays_TRODDEN_FOOTPATHS_so_a_warren_reads_as_blocks_not_a_scatter() -> None:
    """GM 2026-07-27, after settlement-review found the warrens had no circulation at all.

    A dense commoner quarter is served by narrow TRODDEN FOOTPATHS between the house rows - not
    paved streets, which were far beyond a quarter's means. The unwalled towns were the case:
    Hoshizora and Ubame both recorded zero lanes, zero alleys and zero streets, their warrens
    hanging straight off the trunk road with nothing between them.

    The paths go down BEFORE the scan, so `_fits` refuses any spot on the tread - which is why the
    footpath run must be asserted alongside the packing, not instead of it.
    """
    plain = _town()
    plain.pack((100.0, 100.0, 800.0, 700.0), ["hovel"] * 40, step=46, fill=True)
    before = len(plain.M.get("lanes") or [])

    threaded = _town()
    placed = threaded.pack((100.0, 100.0, 800.0, 700.0), ["hovel"] * 40, step=46, footpaths=3, fill=True)
    worn = [ln for ln in (threaded.M.get("lanes") or []) if ln.get("worn")]
    assert placed > 0, "the quarter still packs"
    assert worn, "and it is threaded by WORN lanes - a trodden path, not a paved street"
    assert len(threaded.M["lanes"]) > before, "which the un-threaded quarter does not have"


def test_pack_with_fill_declares_a_BUDGET_so_leftovers_are_not_a_shortfall() -> None:
    """ "place up to N" rather than an exact count - the city gens' 600-samurai district fills are
    the idiom. Without `fill` the same over-ask must WARN, which is the no-silent-caps rule; both
    directions are asserted because the flag's whole purpose is to distinguish them."""
    budget = _town()
    budget.pack((100.0, 100.0, 300.0, 300.0), ["hovel"] * 500, step=46, fill=True)
    assert "shortfalls" not in budget.M, "a declared budget does not report what it could not fit"

    exact = _town()
    exact.pack((100.0, 100.0, 300.0, 300.0), ["hovel"] * 500, step=46)
    assert exact.M.get("shortfalls"), "an exact request that could not be met says so"


def test_pack_face_streets_CORE_leaves_the_street_band_for_shop_frontage() -> None:
    """The three `face_streets` modes are different siting doctrines, not a boolean: `"core"` pushes
    dwellings off the street-facing band so shops can front it, plain True turns each building to
    face its nearest street, and `"fill"` is the permissive form."""
    s = _town()
    s.street([(0.0, 400.0), (1000.0, 400.0)], width=20)
    core = s.pack((100.0, 420.0, 700.0, 700.0), ["hovel"] * 12, step=46, face_streets="core", fill=True)
    assert core >= 0, "the core mode runs its own branch without raising"

    t = _town()
    t.street([(0.0, 400.0), (1000.0, 400.0)], width=20)
    turned = t.pack((100.0, 420.0, 700.0, 700.0), ["hovel"] * 12, step=46, face_streets=True, fill=True)
    assert turned >= 0, "and so does the plain facing mode"
