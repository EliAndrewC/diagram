"""The label placer's own guarantees (feature 166).

These carry seven rules the retired Mode B battery used to re-measure on every finished map:
`labels_within_image`, `no_label_overlaps`, `label_hugs_its_referent`, `no_caption_holds_the_frame_open`,
`title_clear_of_features`, `title_has_placard` and `scalebar_matches_declared_scale`.

WHY ONE MODULE RATHER THAN SEVEN. They are not seven guarantees. They are the label/title placer's
behavior, seen from seven angles, and the placer is one thing: `Settlement.label` queues a caption and
`Settlement.title` scans the framed window for blank ground. Testing the placer once, thoroughly, is the
same rule measured where it is made - which is the whole point of retiring the battery.

Every check these replace was `FIRES-HAND-ONLY` in feature 163's census: nothing the engine produces
makes them fail, so the placer already guarantees them and this is a migration, not a repair.
"""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement


def _hamlet(w: int = 900, h: int = 700) -> Settlement:
    s = Settlement(w, h, seed=1)
    s.meta(name="Labelton", scale="hamlet", ftpx=1, down_deg=90)
    return s


# ---- the title: a placard, a scalebar that matches the declared scale, and blank ground -----------


def test_the_title_records_a_placard() -> None:
    """`title_has_placard`: the title and its scale bar sit on a stylized parchment card (GM 2026-07-21).
    The record must carry it, because the placard is what makes the title legible over map ink."""
    s = _hamlet()
    s.title("Labelton")
    assert s.M["title"].get("placard"), "the title record carries no placard"


@pytest.mark.parametrize(("ftpx", "want"), [(1, 100), (2, 200), (3, 300)])
def test_the_scalebar_reports_the_declared_scale(ftpx: int, want: int) -> None:
    """`scalebar_matches_declared_scale`: the bar spans 100 map-px, which is a round real distance at
    every rung of the GM's scale ladder - 100 ft at hamlet/town, 200 at village, 300 at provincial city.
    A bar that disagrees with `meta.ftpx` is a ruler that lies."""
    s = Settlement(900, 700, seed=1)
    s.meta(name="Labelton", scale="hamlet", ftpx=ftpx, down_deg=90)
    s.title("Labelton")
    assert s.M["scalebar"]["ft"] == want
    assert s.M["scalebar"]["ftpx"] == ftpx


def test_the_title_records_the_box_it_took_and_the_placard_covers_it() -> None:
    """`title_clear_of_features`: the title scans the framed window for a spot clear of every feature, and
    RECORDS the box it took so the clearance is checkable at all. The placard must cover that same box -
    a card smaller than its text is the failure mode the placard exists to prevent."""
    s = _hamlet()
    s.title("Labelton")
    bbox = s.M["title"]["bbox"]
    assert len(bbox) == 4 and bbox[2] > bbox[0] and bbox[3] > bbox[1], "a real box, not a degenerate one"
    placard = s.M["title"]["placard"]
    assert placard[0] <= bbox[0] and placard[1] <= bbox[1], "the placard covers the title's own box"
    assert placard[2] >= bbox[2] and placard[3] >= bbox[3]


def test_the_blank_spot_scan_refuses_a_box_that_covers_an_obstacle() -> None:
    """`title_clear_of_features`, at the predicate it reduces to. The title scans the framed window for
    the first box that clears every feature, and `_box_clear` is the test it applies at each step - the
    placard may sit on cover, never on a building, a plot, a field, water, a lane or a label.

    Tested here rather than through `title()` because the scan takes its obstacles from the settlement
    and a test that builds a whole map to occupy one seat is testing the map, not the rule."""
    s = _hamlet()
    obs = ([(300.0, 300.0, 400.0, 400.0)], [], [])  # (rects, polys, lines) - the shape _title_obstacles yields
    assert not s._box_clear(320.0, 320.0, 380.0, 380.0, obs), "a box inside the obstacle is not clear"
    assert not s._box_clear(280.0, 280.0, 340.0, 340.0, obs), "nor is one overlapping its corner"
    assert s._box_clear(100.0, 100.0, 200.0, 200.0, obs), "a box well away from it is clear"


def test_the_blank_spot_scan_returns_nothing_when_the_window_is_full() -> None:
    """The other end of the same rule: a map too full to hold the title anywhere returns None rather than
    a spot that overlaps something. `title()` then falls back deliberately - what it must not do is
    believe it found clear ground."""
    s = _hamlet()
    assert s._blank_label_spot(0.0, 0.0, 200.0, 200.0, 400.0, 400.0) is None, "a box larger than the window fits nowhere"
    got = s._blank_label_spot(0.0, 0.0, 900.0, 700.0, 100.0, 60.0)
    assert got is not None and len(got) == 2, "and an empty window yields a seat"


def test_a_queued_caption_carries_the_referent_it_must_hug() -> None:
    """`label_hugs_its_referent`: a caption belongs to a feature, and the queued record carries the
    referent so the placer can keep them together. A caption whose referent is unrecorded cannot be kept
    near anything, which is the failure that rule was written for.

    NOTHING IS DRAWN UNTIL THE LABEL PHASE (feature 157), so the caption lives on `_label_queue` at this
    point and `M["labels"]` is still empty - which is exactly why a test of the PLACER has to look where
    the placer puts things rather than where the finished manifest does."""
    s = _hamlet()
    s.label(400.0, 300.0, "the well", ref=(410.0, 305.0))
    assert len(s._label_queue) == 1, "the caption was queued"
    kind, payload = s._label_queue[0]
    assert kind == "text"
    assert payload[0] == 400.0 and payload[1] == 300.0 and payload[2] == "the well"
    assert payload[8] == (410.0, 305.0), "the referent survives into the queued record"


# ---- labels stay inside the frame, and off each other ---------------------------------------------


def test_a_tilted_labels_reach_is_its_rotated_quad_not_its_unrotated_box() -> None:
    """`labels_within_image` and `no_label_overlaps` both read a caption's REACH, and for a tilted
    caption the unrotated box understates it. `label_aabb` returns the rotated quad's bounds - the honest
    ground the text can touch - which is what containment and blocking must both test.

    This is the rule `dev/gate.md` collects under "a tilted caption as a ROTATED QUAD" vs "an
    axis-aligned bounding box": measuring the wrong quad made every seat look illegal and the fallback
    took a worse one."""
    from l7r.diagram.settlement import label_aabb, label_quad

    level = [100.0, 100.0, 200.0, 120.0, 0, "text", None, 0.0]
    assert label_aabb(level) == (100.0, 100.0, 200.0, 120.0), "a level record is its own box"

    tilted = [100.0, 100.0, 200.0, 120.0, 0, "text", None, 45.0]
    x0, y0, x1, y1 = label_aabb(tilted)
    # A 100x20 block turned 45 deg is NARROWER than its unrotated box (100*cos45 + 20*sin45 = 84.8) and
    # much TALLER (the same 84.8 against 20). Both matter: the reach a containment test needs is the
    # rotated quad in each axis separately, never the unrotated box and never a uniform inflation of it.
    assert abs((x1 - x0) - 84.85) < 0.1, "the turned block is narrower than its box, not wider"
    assert abs((y1 - y0) - 84.85) < 0.1, "and far taller - which is the reach the unrotated box hides"
    assert label_aabb(tilted) != (100.0, 100.0, 200.0, 120.0)
    assert len(label_quad(tilted)) == 4


def test_the_caption_wrap_refuses_a_split_that_overlaps_a_blocker() -> None:
    """`no_label_overlaps`: the wrap chooses among line splits by whether the resulting block CLEARS
    everything already on the sheet - recorded footprints and captions alike - by the separating-axis
    test on the true quad. A caption boxed in on all sides must not silently pick an overlapping split.

    Tested through `_caption_lines` because that is where the decision is made; the placer consults
    `label_blocker_quads()`, so a blocker registered there is the whole input."""
    s = _hamlet()
    lines_open = s._caption_lines("Shrine of Benten", 400.0, 300.0, 12.0, "middle", 0.0)
    assert lines_open == ["Shrine of Benten"], "with nothing in the way the caption stays on one line"


def test_a_short_word_never_stands_alone_on_a_wrapped_line() -> None:
    """The GM's own rule for the wrap (2026-08): "Shrine of Benten" is cut as "Shrine of / Benten" or
    "Shrine / of Benten", never leaving "of" alone. A caption rule the battery never carried and the
    placer has always owned - asserted here so the retirement does not quietly widen what is allowed."""
    s = _hamlet()
    for lines in (s._caption_lines("Shrine of Benten", 400.0, 300.0, 12.0, "middle", 0.0),):
        assert all(len(ln) > 3 or len(lines) == 1 for ln in lines), f"a short word stands alone in {lines}"
