"""`tools/page_lit.measure` against a REAL page in the browser (feature 231).

The pure halves - reading the id map, attributing the pixels - are `tests/tools/test_page_lit.py`. What
only a browser can show is that the tool's three page facts hold: the page reaches `rasterReady`, the class
lights through `window.l7rMap.highlight`, and `getScreenCTM` carries a screen pixel to its map coordinate.
It reuses the package's ONE Chromium (the GM's memory ruling, 2026-09-07) and opens a page of its own on it.

THE PAGE OPENS IN RASTER MODE (feature 245). The 200-unit map in the package's 1400-wide viewport opened in
vector mode already, so the `--vector` zoom loop never ran in a browser - and it turned the wheel, which the
page scrolls, so on a real map `VECTOR=1` reported `mode: raster`. A 300 by 300 viewport puts the same map at
one and a half screen pixels per map unit against the picture's two, which is raster mode; one doubling of the
page's own zoom key reaches vector. The zoom buttons sit fixed over the top-right corner, on the pond's half,
and what they cover never changes - so the class lit in the share test is the PADDY, the left half, and the
pond is the half that must not move. (A 100-unit viewport was tried first: the buttons covered most of the
pond, and its lit share read 43%.)
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest

from l7r.diagram.interactive.page import render_page
from l7r.diagram.interactive.tags import ClsTag
from l7r.diagram.tools import page_lit

pytestmark = [
    pytest.mark.renders,  # the page carries a rendered picture and id map (feature 213)
    pytest.mark.xdist_group("chromium"),  # ONE Chromium per run: the whole package on one worker (conftest.py says why)
]

#: a viewport small enough that the 200-unit map below opens in RASTER mode, and large enough that the fixed
#: zoom buttons cover only a corner of it (feature 245)
SMALL = (300, 300)

#: a map of two classes, each a solid half - so a share is an exact number rather than a judgment
STRINGS = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">',
    '<rect width="200" height="200" fill="#EFE3C2"/>',
    '<rect x="0" y="0" width="100" height="200" fill="#A6C398"/>',
    '<rect x="100" y="0" width="100" height="200" fill="#6C9CBE"/>',
    "</svg>",
]
TAGS: list[ClsTag] = [None, "-", "paddy", "fish pond", None]


@pytest.fixture(scope="module")
def page_path() -> Iterator[str]:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "halves.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_page(STRINGS, TAGS, "Halves", {"ftpx": 1.0}, {}))
        yield path


def test_lighting_a_class_changes_that_class_and_not_the_other(browser: Any, page_path: str) -> None:
    result = page_lit.measure(page_path, "paddy", browser=browser, viewport=SMALL)
    assert result["mode"] == "raster" and result["zoom"] > 0, "the opening view is raster mode - the view a reader meets"
    pond_changed, pond_total = result["classes"]["fish pond"]
    paddy_changed, paddy_total = result["classes"]["paddy"]
    assert pond_total > 1000 and paddy_total > 1000, result["classes"]
    assert paddy_changed / paddy_total > 0.95, result["classes"]
    assert pond_changed / pond_total < 0.02, result["classes"]
    assert "lit: paddy" in page_lit.report(result)


def test_the_vector_page_is_measured_when_it_is_asked_for(browser: Any, page_path: str) -> None:
    """`--vector` zooms past the raster switch first: the same question of the page a reader zooms into. The
    page OPENS in raster mode (the small viewport), so reaching vector is the loop's work and not the page's."""
    result = page_lit.measure(page_path, "paddy", vector=True, browser=browser, viewport=SMALL)
    assert result["mode"] == "vector" and result["zoom"] > 1, result
    changed, total = result["classes"]["paddy"]
    assert total > 0 and changed / total > 0.95, result["classes"]


def test_the_lit_screenshot_is_written_where_it_is_asked_for(browser: Any, page_path: str, tmp_path: Any) -> None:
    out = tmp_path / "lit.png"
    page_lit.measure(page_path, "paddy", browser=browser, out=str(out), viewport=SMALL)
    assert out.is_file() and out.stat().st_size > 0
