"""tier town tests split out of `tests.settlement.test_structures` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _ground_points, _town


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
def test_commons_keeps_scrub_off_the_road_bed():
    # the old skip knew only LANES, so scrub drew on the Imperial Road bed (Hoshizora); the
    # corridor set now covers lanes + town streets + the road
    s = _crop_settlement()
    s.road([(100, 300), (700, 300)])
    before = len(s.out)
    s.commons([(150, 150), (600, 150), (600, 450), (150, 450)], role="pasture")
    lim = s.M["road_width"] / 2 + 3 * s.bscale - 0.06  # 0.1-rounding slack, as in the halo test
    pts = _ground_points(s, before)
    assert pts and all(abs(py - 300) > lim for px, py in pts if 100 <= px <= 700)


# ---- feature 174: the bell-and-drum tower, which only a WALLED SEAT has -------------------------


def test_a_LABELLED_road_defers_its_caption_to_the_finish_pass() -> None:
    """The GM's label doctrine: "a label that can sit in empty ground, should; otherwise cover as
    little as possible". A road is drawn FIRST, when the map is still empty, so it cannot yet know
    which side of itself is free - the caption is deferred to `finish()`, which sees the built map.

    Only the Imperial road is labelled at all (the project's own rule: an ordinary road's course is
    already visible), which is why this path exists on `road` and nowhere else.
    """
    s = _town()
    s.road([(0.0, 500.0), (1000.0, 500.0)], label="the Imperial road")
    assert getattr(s, "_road_label", None), "the caption is held for the finish pass"
    assert s._road_label[0] == "the Imperial road"

    plain = _town()
    plain.road([(0.0, 500.0), (1000.0, 500.0)])
    assert not getattr(plain, "_road_label", None), "an unlabelled road holds nothing"


def _queued_label_seat(s: object, text: str) -> tuple[float, float]:
    """A caption's seat, read off the label QUEUE. Captions are seated at finish time, so `M["labels"]`
    is empty until then and a test that reads it passes while asserting nothing."""
    return next((args[0], args[1]) for kind, args in s._label_queue if kind == "text" and args[2] == text)
