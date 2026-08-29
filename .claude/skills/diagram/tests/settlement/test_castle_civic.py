"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import os
import tempfile

import pytest

from l7r.diagram import settlement
from tests.settlement._builders import _cap020, _castle_map, _crop_settlement, _ladder_map, _town


def test_forest_patch_uses_default_label_position():
    s = _town()
    s.forest_patch([(100, 100), (300, 120), (320, 300), (110, 280)], label="copse")  # no label_xy -> default
    assert s.M["forest_patches"]


def test_wall_with_a_label():
    s = _town()
    s.wall([(100, 100), (200, 300), (150, 500)], label="rampart")
    assert s.M["wall"]


def test_flower_field_from_a_polygon_base():
    s = _town()
    s.flower_field([(100, 100), (300, 120), (320, 300), (110, 280)], "chrysanthemums", amp=10)
    assert s.M["flower_fields"]


def test_label_hits_counts_a_grove_under_the_label():
    # the _label_hits grove_rects arm: a label box centered on a homestead grove counts it as an
    # obstacle (a label should not sit over a grove canopy).
    s = _crop_settlement()
    s.grove_rects = [(500, 500, 40, 40)]
    assert s._label_hits(500, 500, "Ministry of Test", 12) >= 1


def test_label_ladder_seats_a_caption_at_the_minimum_standoff_when_the_ground_is_clear():
    s = _ladder_map()
    box = (400.0, 400.0, 500.0, 440.0)  # wider than tall -> below/above are the primary seats
    lx, ly = s._best_label_spot(box, "market", 10)
    assert settlement.box_gap(s._label_box(lx, ly, "market", 10), box) == pytest.approx(settlement.LABEL_MIN_AIR)


def test_label_ladder_steps_outward_past_an_obstacle_and_stops_at_the_first_clear_rung():
    s = _ladder_map()
    box = (400.0, 400.0, 500.0, 440.0)
    clear = s._best_label_spot(box, "market", 10)
    assert settlement.box_gap(s._label_box(*clear, "market", 10), box) == pytest.approx(settlement.LABEL_MIN_AIR)
    for cy in range(370, 476, 7):  # ring the subject so the first rungs are blocked on every side
        for cx in range(330, 576, 12):
            if not (395 < cx < 505 and 395 < cy < 445):
                s.building(cx, cy, 10, 6)
    lx, ly = s._best_label_spot(box, "market", 10)
    gap = settlement.box_gap(s._label_box(lx, ly, "market", 10), box)
    assert gap > settlement.LABEL_MIN_AIR  # the near rungs were blocked...
    assert s._label_hits(lx, ly, "market", 10, pad=0.0, linepad=0.0) == 0  # ...and it kept climbing to clear ground


def test_label_ladder_slides_along_the_long_axis_only():
    # A subject much taller than wide (a road segment, a stall row) is captioned BESIDE it. Sliding
    # ACROSS such a box walks the caption diagonally away while its nominal standoff still reads as
    # small - the first cut of this put "Imperial Road" 43px out at a nominal 5px of air.
    s = _ladder_map()
    tall = (500.0, 200.0, 510.0, 800.0)
    for sl in (-200.0, 200.0):
        seat = s._best_label_spot(tall, "road", 12, slides=(sl,))
        # a slide runs ALONG the subject, so the seat stays tight against it however far it slides;
        # an across-axis slide walked the caption out to 43px at a nominal 5px of air
        assert settlement.box_gap(s._label_box(*seat, "road", 12), tall) <= settlement.LABEL_AIR_CAP * 12


def test_label_ladder_refuses_a_seat_outside_the_cropped_view():
    # a clipped label is unreadable (labels_within_image), so out-of-frame candidates are DISCARDED
    s = _ladder_map()
    box = (100.0, 100.0, 200.0, 140.0)
    free = s._best_label_spot(box, "market", 10)
    assert free[1] > box[3]  # unconstrained, a wide subject is captioned BELOW
    s.M["meta"]["view"] = [60, 60, 400, 90]  # ...but the frame now ends just under the subject
    framed = s._best_label_spot(box, "market", 10)
    assert framed[1] < box[1]  # so the caption moves ABOVE rather than out of the picture


def test_label_ladder_falls_back_to_the_least_covered_seat_when_nothing_is_clear():
    s = _ladder_map()
    box = (400.0, 400.0, 500.0, 440.0)
    for cy in range(320, 540, 10):  # blanket every rung on every side
        for cx in range(300, 620, 10):
            s.building(cx, cy, 14, 8)
    lx, ly = s._best_label_spot(box, "market", 10)
    assert s._label_hits(lx, ly, "market", 10, pad=0.0, linepad=0.0) > 0


def test_place_caption_defers_to_finish_and_records_its_subject_box_for_the_gate():
    # DEFERRED on purpose: a caption seated at call time is judged against half a map (see
    # place_caption's note - Tango's north market caption landed on an execution ground that did
    # not exist yet). Nothing is in M["labels"] until finish() flushes them.
    s = _ladder_map()
    box = (400.0, 400.0, 500.0, 440.0)
    s.place_caption("market", box, 10)
    s.place_caption("ferry", (700.0, 200.0, 720.0, 600.0), 10, slides=(0.0, 40.0))  # explicit slides
    assert not [L for L in s.M["labels"] if L[5] in ("market", "ferry")]
    with tempfile.TemporaryDirectory() as d:
        s.finish(os.path.join(d, "t"), render=False)
    rec = next(L for L in s.M["labels"] if L[5] == "market")
    assert rec[6] == [400.0, 400.0, 500.0, 440.0]
    assert any(L[5] == "ferry" for L in s.M["labels"])


def test_place_caption_refuses_an_empty_subject():
    # s.frontage_box is None when the row placed nothing - captioning it is a gen-script bug
    s = _ladder_map()
    with pytest.raises(ValueError, match="no subject box"):
        s.place_caption("market", None, 10)


def test_place_caption_rot_threads_through_finish(tmp_path):
    s = _town()
    s.place_caption("caravan inn", (100, 100, 180, 160), rot=-16)
    s.finish(str(tmp_path / "t"), render=False)
    L = next(x for x in s.M["labels"] if x[5] == "caravan inn")
    assert len(L) == 8 and L[7] == -16.0 and L[6] == [100.0, 100.0, 180.0, 160.0]


def test_a_castle_caption_can_be_hand_seated():
    """label_xy moves the caption off the court's center - the same escape s.martial_hall keeps."""
    s_def, _ = _castle_map(label="Keep")
    s_hand, _ = _castle_map(label="Keep", label_xy=(1150, 1050))
    s_def.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    s_hand.place_labels()
    assert s_def.M["labels"][-1] != s_hand.M["labels"][-1]


def test_hanko_records_into_the_martial_halls_family():
    """The domain school is the hanko - a school of letters WITH the martial wing - so it draws
    with the martial-hall vocabulary and records into the same family the checks read."""
    s = _cap020()
    s.hanko(700, 700)
    mh = s.M["martial_halls"][0]
    assert mh["kind"] == "hanko" and mh["label"] == "Domain School"
    assert mh["w"] == 133.3 and mh["h"] == 86.7  # 400 x 260 ft (~1 ha) at 3 ft/px - mid-band vs Meirinkan/Nisshinkan
    assert "range_ft" not in mh  # the court is BLANK (sync doctrine) - a dense real hanko belongs to its Mode A sheet
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    caption = [L for L in s.M["labels"] if len(L) > 5 and L[5] in ("Domain", "School")]
    assert len(caption) == 2  # the two-line caption sits inside the court, like an estate's
    s2 = _cap020()
    s2.hanko(700, 700, label="Hanko")  # a one-word name keeps the single line
    s2.place_labels()  # feature 157: the LABEL PHASE
    assert any(len(L) > 5 and L[5] == "Hanko" for L in s2.M["labels"])
