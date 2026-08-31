"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/captions.py`."""

from l7r.diagram.settlement import Settlement
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


def test_pull_caption_toward_leaves_a_seat_that_already_sits_on_its_subject_center():
    """The pull runs along the line from the caption's block to the subject's; when the two centers
    coincide there is no line to run along, so the seat is handed back. A concave subject is how that
    happens on a map - the caption sits in the notch of a C-shaped footprint, clear of every arm of it
    while sharing its center."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    c_shape = [(0.0, 0.0), (200.0, 0.0), (200.0, 40.0), (60.0, 40.0), (60.0, 160.0), (200.0, 160.0), (200.0, 200.0), (0.0, 200.0)]
    seat = (115.0, 100.0 + 9 * 0.275)  # the block's own center lands exactly on the subject's
    assert s.pull_caption_toward(seat, "Kura", 9, "middle", 0.0, c_shape) == seat


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
    s.field_name_label("Higashi-da", 400.0, 620.0)
    assert len(s.M["labels"]) == n_before, "not drawn before the phase"
    assert s._label_queue[-1] == ("field_name", ("Higashi-da", 400.0, 620.0))
    s.place_labels()
    rec = s.M["labels"][-1]
    assert rec[5] == "Higashi-da"
    assert any("letter-spacing" in ln and "Higashi-da" in ln for ln in s.toplabels), "the markup it always drew"
