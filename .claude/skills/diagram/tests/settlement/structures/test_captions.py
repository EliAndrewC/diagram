"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/captions.py`."""

import pytest

from tests.settlement._builders import _town


def test_clear_label_seat_walks_out_and_gives_up_when_nothing_is_clear():
    # a verge-hugging feature puts its DEFAULT below-label on the frontage it hugs, so the seat is
    # probed: below, above, then left/right, walking outward. On a frontage packed solid there is
    # no clear box at all, and the siter must be told so rather than handed a seat on a shopfront.
    s = _town()
    assert s.clear_label_seat(500, 500, 30, 12, "notice board") == (500, 517)  # the default below-seat, when it is clear
    s.M["buildings"] = [{"x": 500, "y": 500, "w": 2000, "h": 2000, "rot": 0, "kind": "merchant"}]
    assert s.clear_label_seat(500, 500, 30, 12, "notice board") is None
    assert not s.label_seat_clear(500, 517, 26.0)


def test_compound_and_marker_captions_tilt_with_their_glyphs():
    s = _town()
    s.manor(500, 300, 120, 90, "Manor", sublabel="the bench", rot=-30)
    s.place_labels()  # feature 157: every caption is queued and drawn in the LABEL PHASE
    recs = {L[5]: L for L in s.M["labels"]}
    assert recs["Manor"][7] == -30.0 and recs["the bench"][7] == -30.0
    s._labels_pending = True  # the phase above drained; re-open it for the second feature
    s.kosatsuba(200, 700, rot=-29)
    s.place_labels()
    assert s.M["labels"][-1][7] == -29.0
    s.fire_tower(800, 700, rot=150)
    assert s.M["labels"][-1][7] == -30.0
    s.boundary_marker(850, 200, rot=-16)
    assert s.M["labels"][-1][7] == -16.0


def test_label_seat_clear_probes_the_tilted_reach():
    s = _town()
    s.M["houses"].append({"x": 300, "y": 262, "w": 40, "h": 24})
    tw = s.label_caption_hw("a long caption here", 9)
    assert s.label_seat_clear(300, 300, tw, 9)  # the level box clears under the house
    assert not s.label_seat_clear(300, 300, tw, 9, tilt=-30.0)  # the tilted reach swings up into it


def test_the_label_phase_defers_every_caption_and_drains_once():
    """THE LABEL PHASE (feature 157, GM 2026-08-29): *"after the final map feature is added ... a final
    phase in which we add labels for whatever map features get labels."* Nothing draws a caption before
    the phase runs, and the phase is idempotent so a hamlet whose pipeline names it as a stage is not
    labeled a second time by `finish()`."""
    s = _town()
    n_before = len(s.M["labels"])
    s.label(500, 500, "gate market", 9)
    assert len(s.M["labels"]) == n_before, "a caption must not be drawn before the label phase"
    assert s._label_queue[-1][0] == "text"
    s.place_labels()
    assert len(s.M["labels"]) == n_before + 1, "the phase draws what was queued"
    assert s._label_queue == [] and not s._labels_pending
    s.place_labels()  # ...and a second run is a no-op, which is what lets finish() always call it
    assert len(s.M["labels"]) == n_before + 1


def test_a_withdrawn_feature_drops_its_queued_caption():
    """`discard_queued_label` is the undo for a feature placed and then withdrawn - `stage_notice`
    re-seats a board the frame cannot hold. It drops the MOST RECENT request of that kind, and asking
    for a kind that was never queued is a no-op rather than an error (feature 157)."""
    s = _town()
    s.label(500, 500, "first", 9)
    s._label_queue.append(("kosatsuba", (1.0, 2.0, 0.0, 12.0, 5.0, "notice board", False, None)))
    s._label_queue.append(("kosatsuba", (3.0, 4.0, 0.0, 12.0, 5.0, "notice board", False, None)))
    s.discard_queued_label("kosatsuba")
    assert [k for k, _ in s._label_queue] == ["text", "kosatsuba"]
    assert s._label_queue[-1][1][0] == 1.0, "the MOST RECENT request is the one withdrawn"
    s.discard_queued_label("field_name")  # never queued - nothing to drop, and nothing to raise
    assert len(s._label_queue) == 2


def test_a_field_name_caption_goes_through_the_phase_too():
    """`paddy_field(label=...)` and `water_field(label=...)` emit their own `<text>` rather than calling
    `label()`, so the general deferral does not reach them; `field_name_label` carries that exact markup
    into the phase instead (feature 157, found by the round-2 spec review). Dormant on every pool map -
    which is why the caption is queued as-is rather than the primitive being changed to suit it."""
    s = _town()
    n_before = len(s.M["labels"])
    s.field_name_label("Higashi-da", (300.0, 560.0, 500.0, 680.0))
    assert len(s.M["labels"]) == n_before, "not drawn before the phase"
    assert s._label_queue[-1] == ("field_name", ("Higashi-da", (300.0, 560.0, 500.0, 680.0)))
    s.place_labels()
    rec = s.M["labels"][-1]
    assert rec[5] == "Higashi-da"
    assert rec[0] >= 300.0 and rec[2] <= 500.0 and rec[1] >= 560.0 and rec[3] <= 680.0, "an area caption: inside its field (feature 266)"
    assert any("letter-spacing" in ln and "Higashi-da" in ln for ln in s.toplabels), "the markup it always drew"


def test_the_one_placers_index_sees_every_family_the_map_draws():
    """Feature 266, FR-006/FR-009/FR-014: the settlement's obstacle index, built once per label phase - the wall and the
    moat as obstacles, the road, a stream and a drawn channel as ways, a torii, the title placard, a caption already
    drawn, and a named ministry marked civic; ground cover is not indexed at all."""
    s = _town()
    s.M["wall"] = [[100, 100], [300, 100], [300, 300], [100, 300]]
    s.M["moat"] = [[80, 80], [320, 80], [320, 320], [80, 320]]
    s.M["moat_width"] = 10
    s.M["road"] = [[0, 400], [600, 400]]
    s.M["streams"] = [{"poly": [[0, 450], [600, 450]], "w": 6}, {"poly": [[1, 1]]}]
    s.M["drawn_channels"] = [{"pts": [[0, 480], [600, 480]], "w": 4}, {"pts": []}]
    s.M["torii"] = [[500, 200, 1]]
    s.M["title"] = {"bbox": [10, 10, 60, 30]}
    s.M["ministries"] = [{"x": 400, "y": 150, "w": 40, "h": 30, "name": "Ministry of Works"}]
    s.M["wells"] = [{"x": 450, "y": 250, "vr": 4}, {"x": 460, "y": 250}]
    s.M["commons"] = [{"x": 300, "y": 300, "w": 900, "h": 900}]
    s.M["labels"] = [[10, 40, 60, 50, 1, "old caption"]]
    idx = s.label_obstacles()
    assert len(idx.ways) >= 3, "the road, the stream and the drawn channel are ways"
    assert any(o.group == "ministry" and o.named for o in idx.obstacles), "a named ministry is marked civic"
    assert any(o.group == "torii" for o in idx.obstacles)
    assert not any(o.poly and max(q[0] for q in o.poly) - min(q[0] for q in o.poly) > 800 for o in idx.obstacles), "ground cover is free space"
    walls = [o for o in idx.obstacles if abs(o.poly[0][1] - o.poly[1][1]) < 1e-6 and 90 < o.poly[0][1] < 110]
    assert walls, "the rampart's runs are obstacles"


def test_the_index_holds_every_crown_and_every_caption_still_queued():
    """Feature 287, labels L7 and L4: every drawn tree crown is an obstacle, measured as a disc and waived for a caption
    naming trees - from `tree_crowns`, or the grove clumps where no crown is recorded; and every caption still QUEUED
    (a fixed-seat `text` caption, a proved board caption) is one, so a probe made before the label phase sees what the
    phase will draw. During the phase the queue is drained, and it adds nothing."""
    from l7r.diagram.labels import Placement

    s = _town()
    s.M["tree_crowns"] = [100.0, 100.0, 12.0, 200.0, 100.0, 9.0]
    s.label(400, 400, "a fixed seat", 9, rot=30.0)
    s.label(400, 300, "a line", 9, rot=72.0, linear=True)
    s.label(400, 200, "a full tilt", 9, rot=72.0, linear=True, full_tilt=True)
    s.label(400, 100, "placed", 9, lines=["placed"], angle=10.0)
    proved = Placement(600.0, 600.0, 0.0, ("notice board",), ((590.0, 595.0), (610.0, 595.0), (610.0, 605.0), (590.0, 605.0)), 0, 0, "upper right", 0.0, None)
    s._label_queue.append(("kosatsuba", (0.0, 0.0, 0.0, 12.0, 5.0, "notice board", proved)))
    s._label_queue.append(("kosatsuba", (0.0, 0.0, 0.0, 12.0, 5.0, "notice board", None)))
    s.field_name_label("Higashi-da", (0, 0, 10, 10))
    idx = s.label_obstacles()
    crowns = [o for o in idx.obstacles if o.circle is not None]
    assert [(o.circle, o.group) for o in crowns] == [((100.0, 100.0, 12.0), "grove"), ((200.0, 100.0, 9.0), "grove")]
    pending = [o for o in idx.obstacles if o.circle is None and o.group is None and not o.named]
    assert any(abs(sum(q[0] for q in o.poly) / 4 - 400.0) < 1 and abs(sum(q[1] for q in o.poly) / 4 - (400.0 - 9 * 0.275)) < 1 for o in pending), "the fixed seat's own box"
    assert any(o.poly == proved.block for o in pending), "the proved board caption"
    g = _town()
    g.M["village_groves"] = [{"clumps": [[50, 60]], "r": 14}, "not a record"]
    assert [o.circle for o in g.label_obstacles().obstacles if o.circle is not None] == [(50.0, 60.0, 14.0)], "the clumps, where no crown is recorded"


def test_a_caption_with_no_seat_goes_in_the_key_on_a_card_or_in_a_band():
    """Feature 287, D10: the placer found no seat - its number is drawn on what it names, its words in the sheet's key:
    on a card over blank ground inside the view where there is room, else in a band grown under the map, outside the
    neatline its ink is clipped at."""
    from l7r.diagram.labels import Subject
    from l7r.diagram.labels.geom import rect

    s = _town()
    s.set_view(0, 0, 1000, 1000)
    s.M["buildings"] = [{"x": 500, "y": 500, "w": 20, "h": 20, "kind": "merchant"}]
    s.M["fire_towers"] = [{"x": 500, "y": 500, "w": 400, "h": 400}]  # ink every seat within the hug covers (the title's search does not read it)
    s._captions.append(("a warehouse & store", Subject("point", tuple(rect(500.0, 500.0, 10.0, 10.0))), 9, False, "normal", "#333"))
    s.place_labels()
    assert s.M["caption_key"] == [[1, "a warehouse & store"]]
    assert any(lb[5] == "1" and lb[6] for lb in s.M["labels"]), "the mark, recording what it names"
    card = s.M["caption_key_card"]
    assert card[2] <= 1000 and card[3] <= 1000 and "key_band" not in s.M["meta"], "a card inside the view"
    assert any("1  a warehouse &amp; store" in t for t in s.toplabels)
    full = _town()
    full.set_view(0, 0, 200, 200)
    full.M["fields"] = [{"outline": [[-10, -10], [210, -10], [210, 210], [-10, 210]]}]
    full.M["buildings"] = [{"x": 100, "y": 100, "w": 20, "h": 20, "kind": "merchant"}, {"x": 100, "y": 100, "w": 190, "h": 190, "kind": "yard"}]
    full._captions.append(("stores", Subject("point", tuple(rect(100.0, 100.0, 10.0, 10.0))), 9, False, "normal", "#333"))
    full.place_labels()
    assert full.M["meta"]["key_band"] > 0 and full.M["meta"]["neatline"] == [0, 0, 200, 200]
    assert full.M["meta"]["view"][3] == pytest.approx(200 + full.M["meta"]["key_band"], abs=0.1) and full.M["caption_key_card"][1] >= 200
