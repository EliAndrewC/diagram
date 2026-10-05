"""Feature 287: what `settlement/finish.py` guarantees where it decides - the title placard over nothing (labels L14), the
scatter re-thrown into what the final view shows past its frame (water W52), and the water block's order (labels L17,
L18) - each on a constructed settlement that includes the violating case."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.finish import neatline_clip, scatter_overhang
from tests.settlement._builders import _crop_settlement


def _placard_clear(s: Settlement) -> bool:
    return s.title_clear()


def test_the_title_band_scans_for_blank_ground_along_it() -> None:
    """Labels L14: every corner hides a plot and a lane runs off the north edge at the band's first seat; the placard is
    scanned along the band to the blank ground past the lane - clear of it, not over it at `vx0 + 30`."""
    s = _crop_settlement()
    s.set_view(0, 400, 2000, 700)
    s.M["fields"] = [{"outline": [[-10, 390], [2010, 390], [2010, 1110], [-10, 1110]]}]
    s.M["lanes"] = [{"pts": [[60, 100], [60, 700]]}, {"pts": [[120, 100], [120, 700]]}]
    s.title("Bandton")
    band = s.M["meta"]["title_band"]
    x0, y0, _x1, y1 = s.M["title"]["placard"]
    assert y1 <= 400 and y0 >= 400 - band, "in the band over the map"
    assert x0 > 120, "past the lanes running off the frame"
    assert _placard_clear(s) and "neatline" not in s.M["meta"] and "title_band_side" not in s.M["meta"]


def test_the_title_band_is_not_grown_on_a_flank_a_reed_strip_runs_off() -> None:
    """Water W43, the violating case: every corner hides a plot and the north band is blank, but a waterward reed strip runs
    off the north edge - a band there would leave the strip stopping inside the frame. The band is grown under the map,
    and the strip still reaches the view's edge; a strip that never reached it constrains nothing."""
    from l7r.diagram.hamletgen.frame import strip_reaches_view
    from l7r.diagram.settlement.finish import band_keeps_the_strips

    s = _crop_settlement()
    s.set_view(0, 400, 2000, 700)
    s.M["fields"] = [{"outline": [[-10, 390], [2010, 390], [2010, 1110], [-10, 1110]]}]
    strip = [[200.0, 380.0], [1800.0, 380.0], [1800.0, 520.0], [200.0, 520.0]]
    s.M["marshes"].append({"role": "waterside", "poly": strip})
    s.M["meta"]["waterward"] = ["N"]
    assert not band_keeps_the_strips(s.M, (0, 400, 2000, 700), (0, 300, 2000, 800)), "the north band would strand the strip"
    assert band_keeps_the_strips(s.M, (0, 400, 2000, 700), (0, 400, 2000, 800))
    s.title("Reedton")
    assert s.M["meta"]["title_band_side"] == "south" and _placard_clear(s)
    assert strip_reaches_view(strip, s.M["meta"]["view"], ["N"])
    s.M["marshes"][-1]["poly"] = [[200.0, 450.0], [1800.0, 450.0], [1800.0, 520.0], [200.0, 520.0]]
    assert band_keeps_the_strips(s.M, (0, 400, 2000, 700), (0, 300, 2000, 800)), "a strip short of the edge already is not this rule's"


def test_the_band_under_the_map_is_tried_before_the_neatline() -> None:
    """Labels L14: ways cross the whole north band; the band under the map is blank and takes the placard."""
    s = _crop_settlement()
    s.set_view(0, 400, 2000, 700)
    s.M["fields"] = [{"outline": [[-10, 390], [2010, 390], [2010, 1110], [-10, 1110]]}]
    s.M["lanes"] = [{"pts": [[x, 100], [x, 700]]} for x in range(40, 2000, 60)]
    s.title("Bandton")
    assert s.M["meta"]["title_band_side"] == "south"
    assert s.M["title"]["placard"][1] >= 1100 and _placard_clear(s)
    assert s.M["meta"]["view"][3] == pytest.approx(700 + s.M["meta"]["title_band"], abs=0.1)


def test_where_ways_cross_both_bands_the_map_is_clipped_at_its_neatline(tmp_path: Path) -> None:
    """Labels L14's terminal: a way crosses the whole of both bands, so the map's ink is clipped at the frame it had (a
    title panel outside the map's neatline) and the placard, outside it, covers nothing drawn - by construction."""
    s = _crop_settlement()
    s.set_view(0, 400, 2000, 700)
    s.M["fields"] = [{"outline": [[-10, 390], [2010, 390], [2010, 1110], [-10, 1110]]}]
    s.M["lanes"] = [{"pts": [[x, 100], [x, 1400]]} for x in range(40, 2000, 60)]
    s.title("Clipton")
    assert s.M["meta"]["neatline"] == [0, 400, 2000, 700]
    x0, y0, x1, y1 = s.M["title"]["placard"]
    assert y1 <= 400 and _placard_clear(s)
    base = os.path.join(str(tmp_path), "t")
    s.finish(base, render=False)
    svg = Path(base + ".svg").read_text()
    assert '<clipPath id="neatline"><rect x="0" y="400" width="2000" height="700"/></clipPath>' in svg
    assert svg.index('clip-path="url(#neatline)"') < svg.index("Clipton"), "the placard is not clipped"


def test_a_title_with_no_view_is_framed_by_its_canvas() -> None:
    """Labels L14: a map with no view is framed by its whole canvas (a town's canvas IS its view) and takes the same
    rungs; the canvas-center fallback that set the placard over whatever stood there is gone."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[-10, -10], [2010, -10], [2010, 1510], [-10, 1510]]}]
    s.title("Y")
    assert s.M["title"]["placard"][3] <= 0 and "title_band" in s.M["meta"] and _placard_clear(s)


def test_the_neatline_wraps_the_map_ink_and_nothing_else() -> None:
    ink, cls = neatline_clip(["<svg>", "a", "b"], [None, "x", "y"], [0, 0, 10, 20])
    assert ink[0] == "<svg>" and 'clip-path="url(#neatline)"' in ink[1] and ink[-1] == "</g>" and ink[2:4] == ["a", "b"]
    assert cls == [None, None, "x", "y", None]
    assert neatline_clip(["<svg>", "a"], [None, "x"], None) == (["<svg>", "a"], [None, "x"])


def test_a_scatter_frame_of_the_decided_view_holds_the_title_band_on_either_side(tmp_path: Path) -> None:
    """Water W52 / M6, cohort seed 8's violating case: the view is decided, the scatter thrown within its frame
    (`scatter_frame_for`), and then every seat in the band above the map is crossed, so the title's band is grown UNDER
    it. The frame carries the band's allowance below as well as above, so the finished map records no breach; the same
    view grown by the band with the north-only frame it used to have would have breached it."""
    from l7r.diagram.hamletgen.hinterland.frame import SCATTER_PAD, TITLE_BAND_ALLOWANCE, scatter_frame_for

    s = _crop_settlement()
    s.set_view(0, 400, 2000, 700)
    s.M["fields"] = [{"outline": [[-10, 390], [2010, 390], [2010, 1110], [-10, 1110]]}]
    s.M["lanes"] = [{"pts": [[x, 100], [x, 700]]} for x in range(40, 2000, 60)]
    frame = scatter_frame_for((0, 400, 2000, 700))
    assert frame == (-SCATTER_PAD, 400 - SCATTER_PAD - TITLE_BAND_ALLOWANCE, 2000 + SCATTER_PAD, 1100 + SCATTER_PAD + TITLE_BAND_ALLOWANCE)
    s._scatter_frames.append((frame, (-500.0, -500.0, 2500.0, 2000.0)))
    s.title("Bandton")
    assert s.M["meta"]["title_band_side"] == "south", "non-vacuity: the band went under the map"
    north_only = (frame[0], frame[1], frame[2], 1100 + SCATTER_PAD)
    assert max(scatter_overhang(north_only, (-500.0, -500.0, 2500.0, 2000.0), s.M["meta"]["view"])) > 0, "the old frame breached"
    s.finish(os.path.join(str(tmp_path), "a"), render=False)
    assert "scatter_frame_breach" not in s.M["meta"] and max(s.M["meta"]["scatter_frame_overhang"]) < 0


def test_a_scatter_the_view_breaches_is_recorded(tmp_path: Path) -> None:
    """The finish's record: a scatter thrown within a frame the view reaches past is recorded as the breach it is (a caller
    whose scatters kept no decided view's frame)."""
    t = Settlement(1000, 1000, seed=1)
    t.meta(name="T", scale="hamlet", ftpx=1)
    t.set_view(70, 50, 800, 900)
    t._scatter_frames.append(((100.0, 100.0, 900.0, 900.0), (0.0, 0.0, 1000.0, 1000.0)))
    t.finish(os.path.join(str(tmp_path), "b"), render=False)
    assert t.M["meta"]["scatter_frame_breach"] == [30.0, 50.0, -30.0, 50.0]


def _watery() -> Settlement:
    s = Settlement(400, 400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    return s


def test_no_bed_is_painted_above_a_sheen_and_the_pond_fill_over_every_mouth(tmp_path: Path) -> None:
    """Labels L17, L18: every watercourse's bed goes in one group and every sheen in a later one, from one counter - so
    the lowest sheen stands above the highest bed; and the pond's fill is the last bed, over every course joining it,
    even when it is registered FIRST."""
    s = _watery()
    pond: dict = {}
    s._water('<ellipse cx="200" cy="200" rx="40" ry="30" fill="#6C9CBE"/>', pond, sheen=None, edge='<ellipse cx="200" cy="200" rx="41" ry="31"/>', pond_fill=True)
    s._pond_entry = s.water[-1]
    channel: dict = {}
    s._water('<path d="M100,200 L190,200" stroke="#6C9CBE"/>', channel, sheen='<path d="M100,200 L190,200" stroke="#9CC"/>')
    brook: dict = {}
    s._water('<path d="M0,0 L400,400" stroke="#6C9CBE"/>', brook, sheen='<path d="M0,0 L400,400" stroke="#9CC"/>', late=True)
    s.finish(os.path.join(str(tmp_path), "w"), render=False)
    assert s.M["water_sheen_zmin"] > s.M["water_bed_zmax"]
    assert all(r["bedz"] < min(channel["sheenz"], brook["sheenz"]) for r in (pond, channel, brook))
    assert pond["bedz"] > channel["bedz"] and pond["bedz"] > brook["bedz"], "the fill over the mouths that join it"


def test_the_title_band_is_clothed_as_the_view_was() -> None:
    """Woods W11 over the view as it ends, the violating case: a hamlet fills its holes over the view it decided, and then
    the title's band is grown over the map - blank canvas the rule counts. The band is filled again where it is grown, so
    the ground nothing covers over the final map window (`map_window`) stays within the share; a map that never filled its
    holes is not filled for it, and a band outside a neatline is sheet, not map."""
    from l7r.diagram.settlement.land.cover import BARE_SHARE_CAP, bare_cells, map_window

    s = Settlement(2000, 1500, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1)
    s.set_view(0, 400, 2000, 700)
    # field strips with a bare strip every third row: a third of the view is bare, just inside the share, in strips too thin
    # for any placard - so the fill lays nothing and the title takes the band over the map
    rows = [k for k in range(28) if k % 3]
    s.M["fields"] = [{"outline": [[-10, 400 + 25 * k], [2010, 400 + 25 * k], [2010, 425 + 25 * k], [-10, 425 + 25 * k]]} for k in rows]
    s.fill_the_holes((0, 400, 2000, 700))
    before = len(s.M["commons"])
    s.title("Bandton")
    band = s.M["meta"]["title_band"]
    assert band and s.M["meta"]["view"][1] == pytest.approx(400 - band), "the band grew over the map"
    bare, total = bare_cells({**s.M, "commons": s.M["commons"][:before]}, map_window(s.M))
    assert len(bare) / total > BARE_SHARE_CAP, "non-vacuity: the band's canvas takes the map past the share"
    bare, total = bare_cells(s.M, map_window(s.M))
    assert len(s.M["commons"]) > before and len(bare) / total <= BARE_SHARE_CAP
    t = Settlement(2000, 1500, seed=1)
    t.meta(name="V", scale="hamlet", ftpx=1)
    t.set_view(0, 400, 2000, 700)
    assert t.refill_the_view() == 0 and not t.M["commons"], "a map that never filled its holes"
    assert map_window({"meta": {"view": [0, 0, 10, 10], "neatline": [0, 5, 10, 5]}}) == [0.0, 5.0, 10.0, 5.0]
    assert map_window({"meta": {"view": [0, 0, 10, 10]}}) == [0.0, 0.0, 10.0, 10.0]


def test_the_scatter_overhang() -> None:
    """Water W52's one predicate: the overhang per side where the view shows a parcel past the scatter's frame; a parcel the
    view never reaches is no breach."""
    frame = (100.0, 100.0, 900.0, 900.0)
    view = (70.0, 50.0, 800.0, 900.0)  # 30 past the frame's left, 50 past its top, 50 past its bottom
    assert scatter_overhang(frame, (0.0, 0.0, 1000.0, 1000.0), view) == [30.0, 50.0, -30.0, 50.0]
    assert scatter_overhang(frame, (2000.0, 2000.0, 2100.0, 2100.0), view) is None


def test_the_placard_text_is_set_for_reading_and_the_bar_keeps_its_scale() -> None:
    """Feature 319 (GM 2026-10-03: "the same thing with the title card as well. At least the text on it - obviously the map
    scale of one pixel per foot will not change"): the name and the bar's two captions are 1.5 times their old 30, 12 and
    10 px, the card is sized from them by the one formula the hamlet's pocket and band also read, and the bar is still 100
    map-px."""
    import re

    from l7r.diagram.settlement.title import PLACARD_TEXT_SCALE, placard_height

    s = _crop_settlement()
    s.title("Bandton")
    svg = " ".join(s.toplabels)
    sizes = sorted(float(v) for v in re.findall(r'font-size="([0-9.]+)"', svg))
    assert PLACARD_TEXT_SCALE == 1.5 and {45.0, 18.0, 15.0} <= set(sizes), sizes
    x0, y0, x1, y1 = s.M["title"]["placard"]
    assert round(y1 - y0) == round(placard_height()) and (x1 - x0) == s.placard_size("Bandton")[2]
    bx0, _by0, bx1, _by1 = s.M["scalebar"]["bbox"]
    assert bx1 - bx0 == 100.0 and s.M["scalebar"]["ft"] == 100 * s.ftpx, "the scale bar keeps its 100 map-px"
