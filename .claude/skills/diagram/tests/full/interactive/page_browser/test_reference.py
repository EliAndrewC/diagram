"""The reference hamlet's real page (the gate) and the research pages (features 134, 145, 159, 194)."""

from __future__ import annotations

import os
import statistics
from typing import Any

import pytest

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.sources import RESEARCH_DIR, RESEARCH_PAGES
from tests.full.interactive.page_browser._driver import Page, _mechanics, _sweep_ms


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_reference_hamlet_page(inashiro: tuple[Page, dict[str, Any]]) -> None:
    page, m = inashiro
    assert m["unclassed_ink"] == [] and m["unregistered_classes"] == []
    present = [k for k in CLASSES if k in m["ink_classes"]]
    assert {
        "farmhouse",
        "storage shed",
        "byre",
        "windbreak",
        "copse",
        "woodland commons",
        "homestead bamboo",
        "bund",
        "bund beans",
        "millet",
        "buckwheat",
        "barley",
        "marsh",
        "scrub and rough grazing",
        "village lane",
        "notice board",
        "well",
        "paddy",
        "wet paddy",
    } <= set(present)
    _mechanics(page, present)


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_the_blue_plots_highlight_and_open_apart_from_the_green_ones(inashiro: tuple[Page, dict[str, Any]]) -> None:
    """The GM's own scenario (feature 159, 2026-08-29): "I should be able to highlight it and click on
    it separate from the rest of the fields, because that is its own type of thing, and it deserves its
    own explanation." Inashiro draws 2 blue plots against 573 green ones."""
    page, m = inashiro
    assert m["ink_classes"]["wet paddy"] == 2 and m["ink_classes"]["paddy"] > 100, "the reference hamlet draws both kinds"
    # A REAL POINTER MUST BE ABLE TO REACH IT, which `point_at` alone does not prove for a plot this
    # small: a blue plot is a wedge a few tens of pixels across, its bunds carry fat invisible hit
    # copies (`thin marks get a fat hit copy`), and the bbox center of a wedge is often outside the
    # wedge - so aiming at the center lit `bund` on the first run of this test. What the GM's request
    # needs is that SOME point a mouse can land on inside the plot lights it, so the test samples the
    # plot's own box and asserts the reachable fraction rather than one guessed pixel.
    # ...AND SINCE FEATURE 200 THE PAGE ANSWERS THE POINTER FROM ITS ID MAP WHILE IN RASTER MODE, the
    # vector groups being hidden there, so the probe asks the page's own hit-test in whichever mode it is in
    # (`l7rMap.keyAtPoint` in raster mode, the DOM in vector mode) and then lands a REAL pointer on a hit.
    reach = page.js(
        """() => {
            const g = document.querySelector('g.f[data-k="wet paddy"]');
            const svg = document.getElementById('map');
            const raster = window.l7rMap.mode() === 'raster';
            svg.setAttribute('data-mode', 'vector');  // a hidden group's box is empty: measure it shown
            const r = g.getBoundingClientRect();
            svg.setAttribute('data-mode', window.l7rMap.mode());
            let hit = 0, tried = 0, at = null;
            for (let i = 1; i < 10; i++) for (let j = 1; j < 10; j++) {
                const x = r.x + r.width * i / 10, y = r.y + r.height * j / 10;
                if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) continue;
                tried++;
                let k = null;
                if (raster) { k = window.l7rMap.keyAtPoint(x, y); }
                else { const el = document.elementFromPoint(x, y); const owner = el && el.closest ? el.closest('g.f') : null; k = owner ? owner.getAttribute('data-k') : null; }
                if (k === 'wet paddy') { hit++; if (at === null) at = [x, y]; }
            }
            return [hit, tried, at];
        }"""
    )
    assert reach[1] > 0, "the plot is off-screen at the opening view - the probe measured nothing"
    assert reach[0] > 0, f"no point inside the blue plot's box reaches it with a real pointer ({reach[0]}/{reach[1]})"
    # ...and landing on it lights the blue plots and no green one
    page.page.mouse.move(reach[2][0], reach[2][1])
    on = page.settles({"wet paddy": 2}, page.on)
    assert on == {"wet paddy": 2}, f"a pointer on a blue plot lit {on}"
    # ...and a green plot lights the green ones and no blue one
    lit = page.hover_class("paddy")
    assert set(lit) == {"paddy"} and lit["paddy"] == page.groups("paddy"), "the green paddy is its own kind now"
    page.clear()
    # the modal is about the blue plot, and it is not the paddy's modal
    blue, green = page.open("wet paddy"), page.open("paddy")
    assert blue["k"] == "wet paddy" and "shitsuden" in blue["name"]
    assert blue["name"] != green["name"] and blue["caveat"] != green["caveat"]
    # the disclosure the reader needs: the tint marks a SHARE of the wet ground on a comb field
    assert "share" in blue["caveat"] and "comb" in blue["caveat"], "the drawing liberty is disclosed in the modal"
    # ...and each links to the other, since both kinds are on this map
    assert "wet paddy" in green["siblings"] and "paddy" in blue["siblings"]
    page.page.keyboard.press("Escape")  # leave the fixture unpinned for the timings test that shares it


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_reference_hamlet_timings(inashiro: tuple[Page, dict[str, Any]]) -> None:
    """SC-004: the highlight within 100 ms; the load under 5 s. The numbers land in tasks.md T20."""
    page, _m = inashiro
    load_ms = page.js("() => performance.timing.loadEventEnd - performance.timing.navigationStart")
    worst = 0.0
    for key in ("farmhouse", "paddy", "bund", "bund beans", "scrub and rough grazing", "marsh"):
        ms = page.js("k => { const t0 = performance.now(); window.l7rMap.highlight(k); return performance.now() - t0; }", key)
        worst = max(worst, ms)
    page.clear()
    # feature 199 FR-008: the reference sweep is RECORDED, not capped - Inashiro was never the slow page
    # (19.5 ms per move before the tiling, 17.8 after; research.md R2), so no cap here could fail

    times = _sweep_ms(page)
    print(
        f"inashiro opening view: mean {statistics.fmean(times):.1f} ms per pointer move, median {statistics.median(times):.1f}, max {max(times):.1f}; highlight worst {worst:.1f} ms; load {load_ms} ms"
    )
    assert worst < 100, f"highlight took {worst:.1f} ms"
    assert load_ms < 5000, f"load took {load_ms} ms"


def test_a_research_page_shows_a_footnote_on_hover_and_its_links_open_locally(browser: Any) -> None:
    """Feature 194 (GM 2026-09-06): the record is HTML with ACOUP-style footnotes - hover a reference and the
    note (the source link and its quoted passage) appears beside it; move away and it goes; the page's own
    assets load from a relative path, so a file:// page is self-contained. The map's references modal links
    the same pages locally (RESEARCH_PAGES), never GitHub."""
    page = browser.new_page(viewport={"width": 1200, "height": 900})
    page.goto("file://" + os.path.join(RESEARCH_DIR, "homesteads.html"), wait_until="load")
    assert page.evaluate("() => getComputedStyle(document.querySelector('main')).maxWidth") != "none", "record.css loaded"
    first = page.locator("sup.fn a").first
    assert page.locator("sup.fn a").count() > 50, "the backfill left the page footnoted"
    first.hover()
    page.wait_for_timeout(50)
    shown = page.evaluate("() => { const t = document.getElementById('fntip'); return t && !t.hidden && t.querySelector('code') !== null && t.textContent.length > 20; }")
    assert shown, "the note appears beside the reference, with the source key and the passage"
    href = first.get_attribute("href")
    assert href and href.startswith("#fn-") and page.locator(f"li#{href[1:]} a.fnback").count() == 1, "the note carries its return link"
    page.mouse.move(5, 5)
    page.wait_for_timeout(300)
    assert page.evaluate("() => document.getElementById('fntip').hidden"), "moving away dismisses it"
    assert RESEARCH_PAGES.startswith("../../../research/")
    page.close()
