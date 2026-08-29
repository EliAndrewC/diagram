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
