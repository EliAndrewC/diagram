"""The crop frames CONTENT, and nothing holds it open (feature 166).

Carries `map_frame_hugs_its_content`, `crop_not_held_open_by_one_feature` and
`no_caption_holds_the_frame_open`, which the retired battery re-measured on finished maps. All three are
one guarantee seen from three sides: the frame is the bounding box of the HARD features plus a margin, so
it is exactly as large as the settlement and its fields - and nothing soft, distant or incidental drags
it wider.

THE GM'S RULE (recorded in `crop_to_content` itself): the frame is tight to the real content - a
graveyard, the pond - and NEVER held open by empty back-slope grazing. An earlier version extended the
frame to preserve two thirds of a trailing commons, and that produced maps with a band of nothing down one
side. So the BLEED features and the linear RUNNERS - streams, channels, lanes, the commons scrub - are
drawn and simply CLIP at the edge, trailing off as "more wild ground this way".
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._knobs import crop_boxes


def _s() -> Settlement:
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="Cropton", scale="hamlet", ftpx=1, down_deg=90)
    return s


def _view(s: Settlement):
    return s.M["meta"].get("view")


def _seat(s: Settlement, x: float, y: float, w: float = 60.0, h: float = 40.0) -> None:
    """Record a farmhouse the way PLACEMENT does, not the way `house()` does.

    `Settlement.house` is a DRAW primitive - it emits the glyph and records the shed, and it does not
    append to `M["houses"]`; the placement layer does that separately. The crop reads the MANIFEST, so a
    test that calls `house()` frames an empty map. (I wrote that test first and it failed with a
    TypeError on a null view, which is how the distinction got found.)"""
    s.M.setdefault("houses", []).append({"x": x, "y": y, "w": w, "h": h, "kind": "plain", "rot": 0})


def test_the_frame_is_the_content_plus_the_margin() -> None:
    """`map_frame_hugs_its_content`. A frame larger than its content is a map with dead space; a frame
    smaller than it cuts the settlement off."""
    s = _s()
    _seat(s, 900.0, 900.0)
    _seat(s, 1100.0, 1100.0)
    s.crop_to_content(margin=30)
    v = _view(s)
    assert v, "the crop recorded a view"
    x0, y0, w, h = v
    assert x0 <= 870.0 + 1 and y0 <= 870.0 + 1, "the frame reaches the first house plus the margin"
    assert x0 + w >= 1130.0 - 1 and y0 + h >= 1130.0 - 1, "and the last"
    assert w < 600.0 and h < 600.0, f"the frame is tight, not the whole canvas ({w:.0f}x{h:.0f})"


def test_a_trailing_runner_does_not_hold_the_frame_open() -> None:
    """`crop_not_held_open_by_one_feature`, and the GM's own ruling. A lane running off toward the next
    village must CLIP at the edge rather than drag the frame out after it and leave a band of empty
    ground down one side."""
    tight = _s()
    _seat(tight, 900.0, 900.0)
    _seat(tight, 1100.0, 1100.0)
    tight.crop_to_content(margin=30)
    before = _view(tight)

    trailing = _s()
    _seat(trailing, 900.0, 900.0)
    _seat(trailing, 1100.0, 1100.0)
    trailing.lane([(1100.0, 1100.0), (1980.0, 1980.0)], width=12.0)  # a runner heading off-map
    trailing.crop_to_content(margin=30)
    after = _view(trailing)

    assert after[2] <= before[2] + 1 and after[3] <= before[3] + 1, f"the lane dragged the frame from {before[2]:.0f}x{before[3]:.0f} to {after[2]:.0f}x{after[3]:.0f}"


def test_a_set_apart_hard_feature_IS_included() -> None:
    """The other side of the same rule, and the reason it is not simply 'ignore distant things'. An
    outlying shrine or a back-slope graveyard is real content and must be framed - which is why the
    docstring insists such features are placed BEFORE the crop. A rule that merely ignored distance
    would cut them off."""
    s = _s()
    _seat(s, 900.0, 900.0)
    near = _s()
    _seat(near, 900.0, 900.0)
    near.crop_to_content(margin=30)
    _seat(s, 1600.0, 1600.0)  # a set-apart steading, still HARD content
    s.crop_to_content(margin=30)
    assert _view(s)[2] > _view(near)[2], "a set-apart hard feature must widen the frame, not be cut off"


# ---- feature 174: the two crop_boxes branches no roll reaches -------------------------------------
# Sixteen of the 89 statements in the 2026-08-31 hamlet-path baseline were here: the `add` helper's
# RAW-POLYGON branch and the whole `if city:` block. Both are unreachable by a hamlet roll - the
# first because no hamlet records an area key as a bare ring, the second because no generator
# produces a city - so both take a hand-built manifest. `crop_boxes` is a pure function of one, which
# is what makes that cheap.

_FT = 1.0
_W = _H = 1000.0


def test_crop_boxes_frames_an_area_key_recorded_as_a_bare_RING() -> None:
    """Some area keys (forest_patches, pastures) record a raw polygon rather than a dict.

    The branch exists because such a record is drawn ground and sets the frame like any other; it
    had no test because the scripted hamlets record every one of their areas as a dict.
    """
    ring = [(10.0, 20.0), (60.0, 20.0), (60.0, 90.0), (10.0, 90.0)]
    got = crop_boxes({"groves": [ring]}, False, _FT, _W, _H)
    assert (10.0, 60.0, 20.0, 90.0, "groves[0]") in got, "the ring's own extent, labeled by key and index"


def test_crop_boxes_city_frames_its_satellites_its_moat_and_its_labels() -> None:
    M = {
        "flophouses": [{"x": 100.0, "y": 200.0, "w": 20.0, "h": 10.0}],
        "moat": [(0.0, 0.0), (500.0, 0.0), (500.0, 500.0)],
        "labels": [[10.0, 12.0, 90.0, 30.0, 5, "Hirokoji"]],
    }
    got = crop_boxes(M, True, _FT, _W, _H)
    assert (90.0, 110.0, 195.0, 205.0, "flophouses[0]") in got, "a w/h record becomes a centered box"
    assert (0.0, 0.0, 0.0, 0.0, "moat") in got and (500.0, 500.0, 0.0, 0.0, "moat") in got, "every moat vertex holds the frame"
    assert (10.0, 90.0, 12.0, 30.0, "label 'Hirokoji'") in got, "a placed label box is framed and named by its text"


def test_crop_boxes_city_excludes_the_extramural_shop_string_but_keeps_one_inside_the_wall() -> None:
    """The slice doctrine (GM 2026-07-24): the gate-market / wharf stall string CLIPS at the frame.

    Excluding it is conditional on the wall - a shop with no wall recorded, or one standing inside
    the wall, still frames. All three cases are asserted, because the branch that skips is one line
    and the branch that does not is the rest of the function.
    """
    wall = [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]
    outside = {"x": 900.0, "y": 900.0, "w": 10.0, "h": 10.0, "kind": "shop"}
    inside = {"x": 200.0, "y": 200.0, "w": 10.0, "h": 10.0, "kind": "shop"}
    kura = {"x": 950.0, "y": 950.0, "w": 10.0, "h": 10.0, "kind": "kura"}

    labeled = [b[4] for b in crop_boxes({"buildings": [outside, inside, kura], "wall": wall}, True, _FT, _W, _H)]
    assert "buildings[0]" not in labeled, "the extramural shop clips at the edge rather than holding the frame"
    assert "buildings[1]" in labeled, "a shop INSIDE the wall frames like anything else"
    assert "buildings[2]" in labeled, "only a shop is excluded - an extramural kura still frames"

    no_wall = [b[4] for b in crop_boxes({"buildings": [outside]}, True, _FT, _W, _H)]
    assert "buildings[0]" in no_wall, "with no wall recorded there is nothing to be outside of"
