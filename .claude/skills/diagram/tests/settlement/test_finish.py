"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import os
import tempfile

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _town


def test_finish_writes_svg_json_and_renders_png():
    # finish() must pair a .png with the .svg automatically (the render step that used to be a
    # forgettable manual command); render=False writes only the source files.
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        s = _town()
        s.finish(base, render=False)
        assert os.path.exists(base + ".svg") and os.path.exists(base + ".json")
        assert not os.path.exists(base + ".png")
        s.finish(base)  # default render=True -> resvg produces the PNG
        assert os.path.exists(base + ".png")


def test_set_view_records_meta_and_crops_viewbox():
    # a city map crops tight to the walls: set_view records the window in meta (the checks read
    # it as the map edge) and finish() rewrites the SVG viewBox to that window. The title follows
    # the view so it stays on-canvas.
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        s = Settlement(3000, 2000, seed=1)
        s.set_view(500, 400, 1000, 800)
        assert s.M["meta"]["view"] == [500, 400, 1000, 800]
        s.title("Edo")
        s.finish(base, render=False)
        with open(base + ".svg") as _f:
            svg = _f.read()
        assert 'viewBox="500 400 1000 800"' in svg and 'viewBox="0 0 3000 2000"' not in svg


def test_box_clear_detects_rect_poly_and_line_obstacles():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 40, "h": 30}]  # rect obstacle
    s.M["dry_plots"] = [{"poly": [[300, 300], [340, 300], [340, 340], [300, 340]]}]  # poly -> bbox'd into rects
    s.M["fields"] = [{"outline": [[600, 600], [800, 600], [800, 800], [600, 800]]}]  # polygon obstacle
    s.M["village_groves"] = [{"poly": [[1000, 1000], [1050, 1000], [1050, 1050], [1000, 1050]], "role": "copse"}]
    s.M["commons"] = [{"poly": [[50, 50], [80, 50], [80, 80], [50, 80]]}]
    s.M["streams"] = [{"poly": [[900, 100], [900, 900]]}]  # line obstacle
    s.M["lanes"] = [{"pts": [[1200, 100], [1200, 500]]}]
    obs = s._title_obstacles()
    assert s._box_clear(150, 150, 200, 180, obs) is True  # a blank patch
    assert s._box_clear(485, 490, 515, 510, obs) is False  # on the house (rect)
    assert s._box_clear(650, 650, 750, 750, obs) is False  # inside the field (poly)
    assert s._box_clear(880, 400, 920, 440, obs) is False  # across the stream (line)


def test_title_lands_over_blank_space_avoiding_the_field():
    s = _crop_settlement()
    s.set_view(0, 0, 2000, 1500)
    s.M["fields"] = [{"outline": [[200, 200], [1800, 200], [1800, 1300], [200, 1300]], "vis_bbox": [200, 200, 1800, 1300]}]
    s.M["houses"] = [{"x": 100, "y": 100, "w": 40, "h": 30}]
    s.title("Testville")
    tb = s.M["title"]["bbox"]
    assert tb[2] <= 200 or tb[0] >= 1800 or tb[3] <= 200 or tb[1] >= 1300  # clear of the field blob


def test_title_falls_back_to_the_corner_when_no_blank_space():
    s = _crop_settlement()
    s.set_view(0, 0, 200, 150)  # a tiny window...
    s.M["fields"] = [{"outline": [[-10, -10], [210, -10], [210, 160], [-10, 160]]}]  # ...covered entirely
    s.title("X")
    assert s.M["title"]["bbox"][0] == 30  # fell back to view left + 30


def test_title_without_a_view_centers_on_the_canvas():
    s = _crop_settlement()  # no set_view -> self.view is None
    s.M["fields"] = [{"outline": [[-10, -10], [2010, -10], [2010, 1510], [-10, 1510]]}]  # full-canvas cover -> no gap
    s.title("Y")
    tb = s.M["title"]["bbox"]
    assert abs((tb[0] + tb[2]) / 2 - 1000) < 2  # centered on W/2 = 1000


def test_text_width_measures_the_render_font_and_falls_back(monkeypatch):
    # the placard pads symmetrically because the width is MEASURED in the render font (DejaVu Serif
    # Bold, what resvg substitutes for serif) - 'Akagahara' measured ~180px where the old estimate
    # said 167 and ran off the card edge (GM 2026-07-21). Without PIL/the font, a generous estimate.
    s = _crop_settlement()
    w = s._text_width("Akagahara", 30)
    assert 170 < w < 195
    import PIL.ImageFont

    def _boom(*a, **k):
        raise OSError("no font")

    monkeypatch.setattr(PIL.ImageFont, "truetype", _boom)
    assert s._text_width("Akagahara", 30) == 9 * 30 * 0.62


def test_text_width_is_pinned_to_the_basic_layout_engine():
    # A title placard is sized from this measurement and RECORDED in the manifest, so the pool is
    # only byte-reproducible if the measurement depends on the font file alone. PIL otherwise picks
    # its layout engine by what the container has installed - RAQM where libraqm is present, BASIC
    # where it is not - and the two disagree in both directions at the sub-pixel level. A container
    # rebuild after a laptop crash (2026-07-25) gained libraqm and thereby dirtied all 16 titled pool
    # manifests with no code change behind it. These exact numbers are the BASIC ones the committed
    # manifests were built with; a failure here means the pin came loose (or PIL changed BASIC), and
    # it must be resolved deliberately - regenerating the pool - not by editing the expectations.
    s = _crop_settlement()
    assert s._text_width("Honda", 30) == 110.0
    assert s._text_width("Hoshizora", 30) == 170.0
    assert s._text_width("Tango", 30) == 103.953125


def test_late_water_block_carries_sheens_and_splices_after_plots():
    """field_channel(late=True) defers into the SECOND water block (spliced at its own first-call
    position so a city's comb net draws OVER the field's plots); a late course with a sheen records
    its sheenz above every late bed, mirroring the main block's contract."""
    s = Settlement(300, 300, seed=1)
    s.meta(name="T", scale="village", ftpx=2)
    rec: dict = {}
    s._water('<path d="M0,0 L10,10" stroke="#6C9CBE"/>', rec, sheen='<path d="M0,0 L10,10" stroke="#9CC"/>', late=True)
    with tempfile.TemporaryDirectory() as td:
        s.finish(os.path.join(td, "t"), render=False)
    assert rec["sheenz"] > rec["bedz"]


def test_label_carries_the_subjects_own_angle_for_lines_and_boxes_alike():
    """GM 2026-08-27 (feature 133 T38): one alignment rule. This test used to pin the 45-degree
    clamp (a 72-degree road kept a level caption) and the mod-90 fold (a 72-degree box read at -18);
    both are superseded - the caption lies at exactly the subject's angle."""
    s = _town()
    s.label(500, 500, "Imperial Road", 12, rot=-26.6, linear=True)
    s.label(500, 600, "Imperial Road", 12, rot=72, linear=True)  # a near north-south road tilts with it
    s.label(500, 700, "tanning yard", 9, rot=72)  # ...and the same angle on a BOX subject is the same caption
    recs = s.M["labels"]
    assert recs[0][7] == -26.6
    assert recs[1][7] == 72.0
    assert recs[2][7] == 72.0


def test_label_wraps_onto_two_lines_only_when_that_clears_the_sheet():
    """GM 2026-08-27 (feature 133 T39): one line if it clears; else the first of two or three lines
    that does; else one. A house standing where the one-liner's ends would fall, but not where a
    two-line block falls, makes the caption wrap; open ground keeps it on one line; a house under the
    whole seat leaves it on one line ("we can just pick one"). Three seats, because a caption already
    placed is itself a blocker for the next."""
    s = Settlement(W=1000, H=1000, seed=1)  # a bare sheet: nothing near a seat but what the test puts there
    s.label(500, 300, "notice board", 8)  # open ground: one line, the record exactly as before
    L = s.M["labels"][-1]
    assert len(L) == 6 and "<tspan" not in s.toplabels[-1] and abs((L[2] - L[0]) - 12 * 8 * 0.55) < 0.01
    s.M["houses"].append({"x": 470, "y": 497, "w": 20, "h": 30, "rot": 0})  # under the one-liner's left end only
    s.label(500, 500, "notice board", 8)  # the wrapped block (26 wide) clears the house; the one-liner (53 wide) does not
    L = s.M["labels"][-1]
    assert s.toplabels[-1].count("<tspan") == 2
    assert abs((L[2] - L[0]) - 6 * 8 * 0.55) < 0.01 and L[3] - L[1] > 8 * 1.05  # narrower, taller
    s.M["houses"].append({"x": 500, "y": 797, "w": 20, "h": 30, "rot": 0})  # under the middle: nothing clears
    s.label(500, 800, "notice board", 8)
    assert "<tspan" not in s.toplabels[-1], "when no layout clears, the one-liner is drawn"


def test_pull_caption_toward_closes_half_the_air_and_refuses_a_collision():
    """Feature 133 T40 (GM 2026-08-27: "move the label fifty percent of the way toward the thing that
    it is labeling"): a level caption 20 px below a 40x20 board is pulled ~10 px up; a caption whose
    pulled block would land on another footprint keeps its seat."""
    s = Settlement(W=1000, H=1000, seed=1)
    board = [(480.0, 490.0), (520.0, 490.0), (520.0, 510.0), (480.0, 510.0)]
    seat = (500.0, 510.0 + 20.0 + 8 * 0.8)  # the one-line box's top edge 20 px under the board's bottom
    pulled = s.pull_caption_toward(seat, "notice board", 8, "middle", 0.0, board)
    assert abs(pulled[0] - 500.0) < 1e-6 and abs((seat[1] - pulled[1]) - 10.0) < 0.5
    s.M["houses"].append({"x": 500, "y": 525, "w": 60, "h": 6, "rot": 0})  # a sliver across the pulled block's path
    assert s.pull_caption_toward(seat, "notice board", 8, "middle", 0.0, board) == seat


def test_label_never_leaves_a_short_word_on_its_own_line():
    s = Settlement(W=1000, H=1000, seed=1)  # a bare sheet: nothing near the seat but what the test puts there
    s.M["houses"].append({"x": 452, "y": 497, "w": 20, "h": 30, "rot": 0})  # blocks the 16-char one-liner's left end
    s.label(500, 500, "Shrine of Benten", 9)
    body = s.toplabels[-1]
    assert body.count("<tspan") == 2
    lines = [t.split(">", 1)[1].split("<")[0] for t in body.split("<tspan")[1:]]
    assert "of" not in lines and lines in (["Shrine of", "Benten"], ["Shrine", "of Benten"])


def test_label_rot_emits_a_center_rotation_and_appends_the_tilt():
    s = _town()
    s.label(500, 500, "tilted", 9, rot=150)  # a caller passes the FEATURE rotation; label() folds it
    L = s.M["labels"][-1]
    assert len(L) == 8 and L[6] is None and L[7] == -30.0
    assert any('transform="rotate(-30.0' in t for t in s.toplabels)
    s.label(500, 550, "level", 9, rot=90)  # a square rotation folds level: record format unchanged
    assert len(s.M["labels"][-1]) == 6


def test_pull_caption_toward_keeps_its_seat_when_the_block_already_touches_or_overlaps_its_subject() -> None:
    """Feature 145: the two early returns - the caption's block already ON the subject, and a gap under
    half a pixel (there is nothing to close, and a pull would only jitter the seat)."""
    s = Settlement(W=1000, H=1000, seed=1)
    board = [(480.0, 490.0), (520.0, 490.0), (520.0, 510.0), (480.0, 510.0)]
    on_it = (500.0, 505.0)  # the block lands ON the board
    assert s.pull_caption_toward(on_it, "notice board", 8, "middle", 0.0, board) == on_it
    touching = (500.0, 510.0 + 8 * 0.8 + 0.2)  # the block's top edge a fifth of a pixel under the board
    assert s.pull_caption_toward(touching, "notice board", 8, "middle", 0.0, board) == touching


def test_title_obstacles_gather_the_long_lines_a_placard_must_miss() -> None:
    """Feature 146: the title's obstacle set includes the map's long POLYLINES - the wall, the moat, the ring
    road and the road - not only its rectangles and polygons."""
    s = Settlement(W=1000, H=1000, seed=1)
    s.M["road"] = [[0, 500], [1000, 500]]
    s.M["moat"] = [[100, 100], [900, 100]]
    _rects, _polys, lines = s._title_obstacles()
    assert len(lines) >= 2, lines
