"""`tools/page_lit.py` - the pure halves: reading a page's class id map, and attributing a screenshot
pair's changed pixels to the classes they lie on (feature 231). The browser half is
`tests/full/interactive/page_browser/test_page_lit.py`, which drives a real page."""

from __future__ import annotations

import types
from typing import Any

import numpy as np
import pytest
from PIL import Image

from l7r.diagram.interactive.page import render_page
from l7r.diagram.interactive.tags import ClsTag
from l7r.diagram.tools import page_lit

pytestmark = pytest.mark.renders  # the page fixture renders a 40x40 picture and its id map (feature 213)


def _page_text() -> str:
    """A page of two classes side by side, carrying the real raster payload."""
    strings = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">',
        '<rect width="40" height="40" fill="#EFE3C2"/>',
        '<rect x="0" y="0" width="20" height="40" fill="#A6C398"/>',
        '<rect x="20" y="0" width="20" height="40" fill="#6C9CBE"/>',
        "</svg>",
    ]
    tags: list[ClsTag] = [None, "-", "paddy", "fish pond", None]
    return render_page(strings, tags, "Tiny", {"ftpx": 1.0}, {})


def _screens(changed: tuple[int, int, int, int] | None = None, size: tuple[int, int] = (40, 40)) -> tuple[Image.Image, Image.Image]:
    """(before, after) - `after` differs inside the rectangle, which is given in screen pixels."""
    before = Image.new("RGB", size, (10, 10, 10))
    after = before.copy()
    if changed:
        x0, y0, x1, y1 = changed
        for x in range(x0, x1):
            for y in range(y0, y1):
                after.putpixel((x, y), (250, 250, 250))
    return before, after


IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def test_the_id_map_is_read_off_the_page_with_its_palette() -> None:
    decoded = page_lit.decode_idmap(_page_text())
    assert decoded is not None
    red, palette, step = decoded
    assert red.shape == (40, 40) and step > 0
    assert sorted(palette.values()) == ["fish pond", "paddy"]
    left = {int(red[20, 5]), int(red[5, 5])}
    assert len(left) == 1 and palette[left.pop()] == "paddy"


def test_a_page_with_no_raster_decodes_to_nothing() -> None:
    assert page_lit.decode_idmap("<html>no payload here</html>") is None


def test_every_changed_pixel_is_attributed_to_the_class_beneath_it() -> None:
    decoded = page_lit.decode_idmap(_page_text())
    assert decoded is not None
    red, palette, _step = decoded
    before, after = _screens((20, 0, 40, 40))  # the right half - the pond's ink
    shares = page_lit.attribute(before, after, red, palette, IDENTITY)
    assert shares["fish pond"] == (800, 800)
    assert shares["paddy"] == (0, 800)


def test_the_screen_transform_is_inverted_rather_than_assumed() -> None:
    """The page is panned and zoomed; a screen pixel is answered at its MAP coordinate, not its own."""
    decoded = page_lit.decode_idmap(_page_text())
    assert decoded is not None
    red, palette, _step = decoded
    before, after = _screens((0, 0, 80, 80), size=(80, 80))
    ctm = (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)  # 2x, no pan: the whole 40x40 map fills an 80x80 screen
    shares = page_lit.attribute(before, after, red, palette, ctm)
    assert shares["paddy"] == (3200, 3200) and shares["fish pond"] == (3200, 3200)
    # panned left by half the map: the pond fills the left half of the screen, the right half is off the map
    shares = page_lit.attribute(before, after, red, palette, (2.0, 0.0, 0.0, 2.0, -40.0, 0.0))
    assert shares["fish pond"] == (3200, 3200) and shares["paddy"] == (0, 0)


def test_a_change_under_the_threshold_is_not_a_lit_pixel() -> None:
    decoded = page_lit.decode_idmap(_page_text())
    assert decoded is not None
    red, palette, _step = decoded
    before = Image.new("RGB", (40, 40), (100, 100, 100))
    after = Image.new("RGB", (40, 40), (100, 100, 105))
    assert page_lit.attribute(before, after, red, palette, IDENTITY)["paddy"][0] == 0
    assert page_lit.attribute(before, after, red, palette, IDENTITY, threshold=1)["paddy"][0] == 800


def test_the_report_ranks_by_share_and_names_the_view() -> None:
    out = page_lit.report({"key": "fish pond", "mode": "raster", "zoom": 2.86, "classes": {"fish pond": (800, 800), "paddy": (8, 800)}})
    assert "lit: fish pond" in out and "mode: raster" in out and "2.86x" in out
    body = [ln for ln in out.splitlines() if ln.strip().endswith(("paddy", "fish pond"))]
    assert body[0].endswith("fish pond") and "100.0%" in body[0]
    assert body[1].endswith("paddy") and "1.0%" in body[1]


def test_the_report_says_when_the_lit_class_is_not_on_screen() -> None:
    out = page_lit.report({"key": "byre", "mode": "vector", "zoom": 6.0, "classes": {"paddy": (0, 10)}})
    assert "no pixels of 'byre' are on screen" in out


def test_a_page_without_an_id_map_is_refused_by_name(tmp_path: Any) -> None:
    p = tmp_path / "bare.html"
    p.write_text("<html>nothing</html>")
    with pytest.raises(SystemExit, match="carries no class id map"):
        page_lit.measure(str(p), "paddy")


def test_the_tool_launches_its_own_browser_when_none_is_lent(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """`measure` without a browser opens one and closes it; the real launch is exercised by the browser test."""
    closed: list[str] = []

    class _Browser:
        def close(self) -> None:
            closed.append("closed")

    class _PW:
        chromium = types.SimpleNamespace(launch=lambda: _Browser())

        def __enter__(self) -> _PW:
            return self

        def __exit__(self, *_a: object) -> None:
            closed.append("stopped")

    monkeypatch.setitem(__import__("sys").modules, "playwright.sync_api", types.SimpleNamespace(sync_playwright=lambda: _PW()))
    with page_lit._chromium() as b:
        assert isinstance(b, _Browser)
    assert closed == ["closed", "stopped"]


def test_main_prints_the_report(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(page_lit, "measure", lambda *_a, **_k: {"key": "paddy", "mode": "raster", "zoom": 1.0, "classes": {"paddy": (4, 4)}})
    assert page_lit.main(["page.html", "paddy", "--vector", "--out", "lit.png"]) == 0
    assert "lit: paddy" in capsys.readouterr().out


def test_the_lut_tolerates_the_rounding_the_page_itself_tolerates() -> None:
    """`page.js keyAtPoint` accepts a red value within 1 of a palette entry; so does this."""
    red = np.array([[3, 4, 5, 7]], dtype=np.int64)
    before, after = _screens((0, 0, 4, 1), size=(4, 1))
    shares = page_lit.attribute(before, after, red, {4: "paddy"}, IDENTITY)
    assert shares["paddy"] == (3, 3)  # 3, 4 and 5 answer paddy; 7 answers nothing


def test_the_id_map_is_read_at_the_viewbox_the_page_carries() -> None:
    """Feature 200 crops the page's viewBox to the drawn ink, so the id map is the VIEWBOX: a map
    coordinate is shifted by its origin before the image is asked. Without this every sample on
    Kuwabata's page (`viewBox="1792 326 955 1954"`) landed outside the image and every class read zero."""
    red = np.zeros((4, 4), dtype=np.int64)
    red[:, 2:] = 4  # the right half of the id map is the class
    before, after = _screens((2, 0, 4, 4), size=(4, 4))
    shifted = page_lit.attribute(before, after, red, {4: "paddy"}, (1.0, 0.0, 0.0, 1.0, -100.0, -200.0), viewbox=(100.0, 200.0, 4.0, 4.0))
    assert shifted["paddy"] == (8, 8)
    assert page_lit.attribute(before, after, red, {4: "paddy"}, (1.0, 0.0, 0.0, 1.0, -100.0, -200.0))["paddy"] == (0, 0)


def test_a_viewbox_at_a_different_scale_than_the_image_is_carried_too() -> None:
    """The id map is rendered at 1 px per user unit today; the arithmetic does not assume it."""
    red = np.zeros((8, 8), dtype=np.int64)
    red[:, 4:] = 4
    before, after = _screens((2, 0, 4, 4), size=(4, 4))
    out = page_lit.attribute(before, after, red, {4: "paddy"}, IDENTITY, viewbox=(0.0, 0.0, 4.0, 4.0))
    assert out["paddy"] == (8, 8)  # 8 px of image per 4 units of map: the right half is still the right half
