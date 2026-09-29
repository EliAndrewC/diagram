"""Feature 287: what `settlement/finish.py` guarantees where it decides - the title placard over nothing (labels L14), the
scatter re-thrown into what the final view shows past its frame (water W52), and the water block's order (labels L17,
L18) - each on a constructed settlement that includes the violating case."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.finish import neatline_clip, scatter_overhang, scatter_strips
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


def test_the_scatter_overhang_and_its_strips() -> None:
    """Water W52's one predicate: the overhang per side where the view shows a parcel past the scatter's frame; the
    strips are that ground, which a re-throw fills; a parcel the view never reaches is no breach."""
    frame = (100.0, 100.0, 900.0, 900.0)
    parcel = (0.0, 0.0, 1000.0, 1000.0)
    view = (70.0, 50.0, 800.0, 900.0)  # 30 past the frame's left, 50 past its top, 50 past its bottom
    assert scatter_overhang(frame, parcel, view) == [30.0, 50.0, -30.0, 50.0]
    strips = scatter_strips(frame, parcel, view)
    assert strips == [(70.0, 50.0, 100.0, 950.0), (70.0, 50.0, 870.0, 100.0), (70.0, 900.0, 870.0, 950.0)]
    assert scatter_overhang(frame, (2000.0, 2000.0, 2100.0, 2100.0), view) is None and scatter_strips(frame, (2000.0, 2000.0, 2100.0, 2100.0), view) == []
    assert scatter_strips((0.0, 0.0, 800.0, 800.0), parcel, (100.0, 100.0, 750.0, 750.0))[0][0] == 800.0, "the right strip"


def test_a_scatter_the_view_breaches_is_re_thrown_into_the_strips(tmp_path: Path) -> None:
    """Water W52: where the final view shows a parcel past the frame its scatter was thrown within, the scatter's
    registered re-throw fills exactly those strips, and no breach is recorded; a scatter with no re-throw registered is
    still recorded as the breach it is."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.set_view(70, 50, 800, 900)
    s._scatter_frames.append(((100.0, 100.0, 900.0, 900.0), (0.0, 0.0, 1000.0, 1000.0)))
    thrown: list[tuple[float, float, float, float]] = []
    s._scatter_rethrows = {0: thrown.append}  # type: ignore[attr-defined]
    s.finish(os.path.join(str(tmp_path), "a"), render=False)
    assert len(thrown) == 3 and "scatter_frame_breach" not in s.M["meta"] and max(s.M["meta"]["scatter_frame_overhang"]) <= 0
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
