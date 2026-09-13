"""THE FULL TREE (the GM, 2026-08-28: a 15 s browser test belongs with the lengthy tests - *"I agree that that is where it belongs"*; feature 135's three-tree rule): collected by the FULL run and the AWS check, never by quick.

The page in a real browser (feature 134, spec FR-012 - a page that was never opened has not been
verified). Playwright drives headless Chromium over a plain `file://` open.

ONE tier since 2026-09-07. The SYNTHETIC page is a hand-built map of a dozen classed primitives: it proves
the mechanics - hover lights every group of a class and none of another, a label and its subject
are one class, a click opens the modal with the label words and the present siblings only, Escape
/ the close button / the backdrop close it, zero console errors, zero network requests - and every
behavior ruling the GM has made about the page since. The REFERENCE HAMLET tier (a rolled Inashiro, the
same mechanics on the real page, the SC-004 timings) and the Kuwabata speed tier (features 199-203's caps)
were retired by the GM on 2026-09-07 - the reason and the ruling are in conftest.py.

Skipped with a reason when Playwright or its Chromium is absent (`setup-dev-env.sh` installs both).
"""

from __future__ import annotations

import pytest

from l7r.diagram.interactive.classes import CLASSES, PLACE
from l7r.diagram.interactive.sources import RESEARCH_PAGES
from tests.full.interactive.page_browser._driver import Page, _mechanics

pytestmark = pytest.mark.renders  # tests OF the page's raster / the plates: they render tiny synthetic pictures on purpose (feature 213)


def test_synthetic_page_mechanics(synthetic: Page) -> None:
    present = ["farmhouse", "storage shed", "byre", "windbreak", "copse", "marsh", "paddy", "bund", "notice board", "village lane", "scrub and rough grazing"]
    _mechanics(synthetic, present)


def test_a_real_pointer_lights_the_kind_and_clicking_opens_its_modal(synthetic: Page) -> None:
    x, y = synthetic.center("farmhouse", 1)
    synthetic.point_at("farmhouse", 1)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"farmhouse": 2}, "both farmhouses, disconnected, light as one kind (US1)"
    synthetic.page.mouse.click(x, y)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "farmhouse"
    synthetic.js("() => document.getElementById('x-close').click()")
    assert not synthetic.dialog()["open"]
    synthetic.page.mouse.move(1, 199)  # the bare sheet
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {}, "the not-highlighted sheet lights nothing"


def test_the_label_and_its_subject_are_one(synthetic: Page) -> None:
    x, y = synthetic.center("notice board", 1)  # the <text> label
    synthetic.page.mouse.move(x, y)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"notice board": 2}, "hovering the label lights the board too (US5)"
    synthetic.page.mouse.click(x, y)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "notice board"
    synthetic.page.mouse.click(2, 2)  # the backdrop
    synthetic.page.wait_for_timeout(50)
    assert not synthetic.dialog()["open"], "a click outside the modal closes it"


def test_the_lit_placard_keeps_its_name_readable(synthetic: Page) -> None:
    """Feature 176 (GM 2026-09-02): "I should be able to see and read the name of the hamlet while the
    title card is highlighted." The card goes gold like any lit class; the name stays in the ink."""
    assert synthetic.hover_class(PLACE) == {PLACE: 2}, "the card and its name light together"
    card = synthetic.js(f"() => getComputedStyle(document.querySelector('g.f[data-k=\"{PLACE}\"] rect')).fill")
    name = synthetic.js(f"() => getComputedStyle(document.querySelector('g.f[data-k=\"{PLACE}\"] text')).fill")
    # The gold arrives as `fill: var(--hl)`, so an unresolved `--hl` computes to the INHERITED fill - the
    # card's own parchment, which is what a lit card that never lit would also read as. This failed once
    # under a loaded page-check on 2026-09-13 and reproduced in none of seven runs after, so the next
    # occurrence carries the property's resolved value and says which of the two it was.
    hl = synthetic.js("() => getComputedStyle(document.documentElement).getPropertyValue('--hl').trim()")
    assert card == "rgb(255, 200, 61)", f"the lit card is the highlight gold, got {card} (--hl resolved to {hl!r})"

    assert name == "rgb(45, 42, 36)", f"the name on the lit card is the map's ink, got {name}"
    synthetic.clear()
    assert synthetic.js(f"() => getComputedStyle(document.querySelector('g.f[data-k=\"{PLACE}\"] rect')).fill") == "rgb(247, 240, 220)", "and the card is its own parchment again"


def test_the_split_fill_and_stroke_highlight_apart(synthetic: Page) -> None:
    assert synthetic.hover_class("paddy") == {"paddy": 1}
    assert synthetic.hover_class("bund") == {"bund": 1}
    fill_none = synthetic.js("() => getComputedStyle(document.querySelector('g.f[data-k=\"bund\"] rect')).fill")
    assert fill_none == "none", "the bund's stroke copy keeps an empty body when highlighted - hovering the bund never floods the paddy"
    synthetic.clear()


def test_the_map_fits_the_viewport_at_load_and_zooms_between_fit_and_the_ceiling(synthetic: Page) -> None:
    """FR-013: the page opens at the view the GM saw (the map as wide as the viewport); fit-the-whole-map
    is the floor; the ceiling is MAX_ZOOM times fit."""
    synthetic.js("() => window.l7rMap.fitWidth()")
    r = synthetic.js("() => { const r = document.getElementById('map').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom, innerWidth, innerHeight]; }")
    assert abs(r[0]) < 0.5 and abs(r[2] - r[4]) < 0.5, "the opening view is the map at the viewport's width"
    assert synthetic.js("() => window.l7rMap.zoom()") >= 1.0
    synthetic.js("() => document.querySelector('#zoom [data-z=fit]').click()")
    r = synthetic.js("() => { const r = document.getElementById('map').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom, innerWidth, innerHeight]; }")
    assert r[0] >= -0.5 and r[1] >= -0.5 and r[2] <= r[4] + 0.5 and r[3] <= r[5] + 0.5, "fit: the whole map is inside the viewport"
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9
    synthetic.js("() => document.querySelector('#zoom [data-z=in]').click()")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 2.0) < 1e-9
    for _ in range(8):
        synthetic.js("() => document.querySelector('#zoom [data-z=in]').click()")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - synthetic.js("() => window.l7rMap.maxZoom")) < 1e-9, "the ceiling holds"
    synthetic.js("() => document.querySelector('#zoom [data-z=out]').click()")
    assert synthetic.js("() => window.l7rMap.zoom()") < synthetic.js("() => window.l7rMap.maxZoom")
    synthetic.js("() => document.querySelector('#zoom [data-z=fit]').click()")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9, "fit is the floor"
    synthetic.js("() => document.querySelector('#zoom [data-z=out]').click()")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9, "cannot zoom out past the whole settlement"


def test_the_wheel_scrolls_and_a_press_is_only_a_click(synthetic: Page) -> None:
    """The wheel SCROLLS the map and never zooms (GM 2026-08-28: "I still want scrolling to scroll"); there is
    no drag-to-pan and the cursor is the normal pointer (GM 2026-08-28: "I don't need to click and drag")."""
    synthetic.js("() => window.l7rMap.fit()")
    synthetic.js("() => document.querySelector('#zoom [data-z=in]').click()")
    zoom_before = synthetic.js("() => window.l7rMap.zoom()")
    ty_before = synthetic.js("() => window.l7rMap.view().ty")
    synthetic.page.mouse.move(700, 500)
    synthetic.page.mouse.wheel(0, 120)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js("() => window.l7rMap.zoom()") == zoom_before, "the wheel does not zoom"
    assert abs((ty_before - synthetic.js("() => window.l7rMap.view().ty")) - 120) < 2, "the wheel scrolled the map by its own travel"
    for _ in range(3):
        synthetic.page.mouse.wheel(-2000, -2000)
    synthetic.page.wait_for_timeout(30)
    x2, y2 = synthetic.center("farmhouse", 0)
    before = synthetic.js("() => window.l7rMap.view()")
    synthetic.page.mouse.move(x2, y2)
    synthetic.page.mouse.down()
    synthetic.page.mouse.move(x2 - 60, y2 - 40, steps=5)
    synthetic.page.mouse.up()
    synthetic.page.wait_for_timeout(50)
    assert synthetic.js("() => window.l7rMap.view()") == before, "a drag moves nothing"
    assert synthetic.js("() => getComputedStyle(document.getElementById('stage')).cursor") == "auto"
    assert synthetic.js("() => getComputedStyle(document.querySelector('g.f')).cursor") == "auto", "a normal pointer over the features"
    synthetic.page.mouse.click(x2, y2)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "farmhouse"
    synthetic.page.keyboard.press("Escape")
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_the_wheel_scrolls_the_map_when_the_pointer_is_not_over_the_open_modal(synthetic: Page) -> None:
    """The GM (2026-08-29): with an explanation open, "when my mouse is not over top of the actual modal
    itself ... the map, which is in the background, will then scroll". The shade is a sibling of the stage
    covering the whole viewport, so every wheel turn outside the dialog landed on it and reached nothing."""
    synthetic.js("() => window.l7rMap.fit()")
    synthetic.js("() => document.querySelector('#zoom [data-z=in]').click()")
    synthetic.open("farmhouse")
    assert synthetic.js("() => !document.getElementById('shade').hidden"), "the shade is up"
    zoom_before = synthetic.js("() => window.l7rMap.zoom()")
    ty_before = synthetic.js("() => window.l7rMap.view().ty")
    synthetic.page.mouse.move(80, 940)  # over the shade, well clear of the centered dialog
    synthetic.page.mouse.wheel(0, 120)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js("() => window.l7rMap.zoom()") == zoom_before, "the wheel still does not zoom"
    moved = ty_before - synthetic.js("() => window.l7rMap.view().ty")
    assert abs(moved - 120) < 2, "the wheel over the shade scrolled the map behind it by its own travel"
    held = synthetic.js("() => window.l7rMap.view()")
    synthetic.page.mouse.move(700, 500)  # over the dialog itself - the wheel is its text's, not the map's
    synthetic.page.mouse.wheel(0, 120)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js("() => window.l7rMap.view()") == held, "the map does not move under the modal"
    synthetic.page.keyboard.press("Escape")
    assert synthetic.js("() => document.getElementById('shade').hidden")
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_bare_ground_inside_a_footprint_lights_its_class_and_drawn_ink_above_it_still_wins(synthetic: Page) -> None:
    """The GM (2026-08-28): hovering the scrub only worked over a blade; now the footprint takes the pointer."""
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.js("() => { const r = document.querySelector('polygon.hit').getBoundingClientRect(); return [r.x + r.width * 0.5, r.y + r.height * 0.9]; }")
    synthetic.page.mouse.move(x, y)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"marsh": 3}, "bare ground inside the marsh footprint lights the marsh - both patches and the region's own group"
    assert synthetic.js("() => getComputedStyle(document.querySelector('g.f.on polygon.hit')).fill") == "none", "the region itself paints nothing when highlighted"
    synthetic.page.mouse.move(1, 199)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {}


def test_ctrl_zoom_keys_and_ctrl_wheel_drive_the_page_zoom(synthetic: Page) -> None:
    """The GM (2026-08-28): one way of zooming - Ctrl + / - / 0 and Ctrl+wheel are ours."""
    synthetic.js("() => window.l7rMap.fit()")
    synthetic.page.keyboard.press("Control+=")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 2.0) < 1e-9
    synthetic.page.keyboard.press("Control+-")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9
    synthetic.page.mouse.move(700, 500)
    synthetic.page.keyboard.down("Control")
    synthetic.page.mouse.wheel(0, -300)
    synthetic.page.keyboard.up("Control")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js("() => window.l7rMap.zoom()") > 1.5, "Ctrl+wheel zooms (a plain wheel scrolls)"
    synthetic.page.keyboard.press("Control+0")
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9
    assert synthetic.js("() => window.devicePixelRatio") == 1, "the browser's own zoom did not change"
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_a_thin_mark_is_hit_from_a_few_pixels_away(synthetic: Page) -> None:
    """The GM (2026-08-28): the bunds, beans, ditches and lanes are too thin to hover; a fat invisible copy takes the pointer."""
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.js("() => { const r = document.querySelector('g.f[data-k=\"village lane\"] path.hit').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }")
    synthetic.page.mouse.move(x, y + 8)  # 8 screen px off the 1 px line, inside its hit stroke
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"village lane": 1}
    synthetic.page.mouse.move(1, 199)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {}


def test_cleared_ground_inside_the_scrub_polygon_lights_nothing(synthetic: Page) -> None:
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.js("() => { const r = document.querySelector('g.f[data-k=\"scrub and rough grazing\"] rect').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }")
    synthetic.page.mouse.move(x, y)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"scrub and rough grazing": 2}, "a cell with a blade in it lights the scrub"
    assert synthetic.js("() => getComputedStyle(document.querySelector('g.f.on rect')).fill") == "none", "the region never paints, highlighted or not"
    synthetic.page.mouse.move(x + 200, y)  # inside the recorded polygon, no blade within two cells
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {}, "cleared ground inside the scrub's polygon lights nothing"


def test_the_clicked_class_stays_highlighted_while_its_modal_is_open(synthetic: Page) -> None:
    """The GM (2026-08-28): while the modal explaining the highlighted thing is active, it stays highlighted."""
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.center("farmhouse", 1)
    synthetic.page.mouse.move(x, y)
    synthetic.page.mouse.click(x, y)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "farmhouse" and synthetic.on() == {"farmhouse": 2}
    bx, by = synthetic.center("byre", 0)
    synthetic.page.mouse.move(bx, by)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"farmhouse": 2}, "the pointer does not move the highlight while the modal is open"
    synthetic.page.mouse.move(1, 199)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {"farmhouse": 2}
    synthetic.page.keyboard.press("Escape")
    synthetic.page.wait_for_timeout(30)
    assert not synthetic.dialog()["open"] and synthetic.on() == {}, "closing the modal releases the highlight"
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_glossary_terms_carry_their_definition_and_the_references_open_on_top(synthetic: Page) -> None:
    """GM 2026-08-28: hover a term for its definition; "See references" opens a second modal above the first."""
    synthetic.js("() => window.l7rMap.fit()")
    synthetic.open("bund")
    spans = synthetic.js("() => Array.from(document.querySelectorAll('#explain .gl')).map(s => [s.textContent, s.getAttribute('data-def').slice(0, 30)])")
    assert any(t.lower() in ("bund", "bunds", "aze", "azenuri") and d for t, d in spans), spans
    assert synthetic.js("() => !document.getElementById('x-refs').hidden")
    synthetic.js("() => document.getElementById('x-refs').click()")
    synthetic.page.wait_for_timeout(30)
    # THE REFERENCES REPLACE THE EXPLANATION (feature 181, GM 2026-09-05): the explanation stays OPEN (its
    # close event would release the pin and the shade) but is not DISPLAYED while the references are up
    shown = "() => ({ refs: document.getElementById('references').open, explain: document.getElementById('explain').open, visible: getComputedStyle(document.getElementById('explain')).display !== 'none', shade: !document.getElementById('shade').hidden })"
    assert synthetic.js(shown) == {"refs": True, "explain": True, "visible": False, "shade": True}, "the explanation disappears behind the references; the shade and the pin stay"
    assert synthetic.js("() => window.l7rMap.pinned()") == "bund"
    assert synthetic.js("() => document.getElementById('r-list').children.length") >= 1
    # the title is "<Name> references", the name a link that does what the button does
    name = CLASSES["bund"].name
    title = f"{name[0].upper()}{name[1:]}"
    assert synthetic.js("() => document.getElementById('r-name').textContent") == f"{title} references"
    assert synthetic.js("() => { const a = document.querySelector('#r-name a#r-back'); return a && a.textContent; }") == title
    # NO DOTTED UNDERLINE ON A LINK (feature 186, GM 2026-09-05): the title link, a question link and (below,
    # on the windbreak) a sibling link render with no underline at all; color and hover color are the style
    assert synthetic.js("() => ['#r-name a#r-back', '#r-list a.q'].map(s => getComputedStyle(document.querySelector(s)).textDecorationLine)") == ["none", "none"]
    synthetic.js("() => document.getElementById('r-back').click()")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js(shown) == {"refs": False, "explain": True, "visible": True, "shade": True}, "the title link brings the writeup back"
    synthetic.js("() => document.getElementById('x-refs').click()")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js(shown)["visible"] is False
    synthetic.js("() => document.getElementById('r-close').click()")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js(shown) == {"refs": False, "explain": True, "visible": True, "shade": True}, "so does the button"
    synthetic.js("() => document.getElementById('x-refs').click()")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js(shown)["visible"] is False
    # THE REFERENCES ARE QUESTIONS (feature 180, GM 2026-09-05): every line is a link into the research
    # record's local page (feature 194), the button says where it returns to, and the explanation carries no "Record:" line
    links = synthetic.js("() => Array.from(document.querySelectorAll('#r-list a.q')).map(a => [a.textContent, a.getAttribute('href'), a.getAttribute('target')])")
    assert links and all(t and h.startswith(RESEARCH_PAGES) and "#" in h and tg == "_blank" for t, h, tg in links), links
    assert synthetic.js("() => document.getElementById('x-refs').textContent") == f"See references ({len(links)})"
    name = CLASSES["bund"].name
    assert synthetic.js("() => document.getElementById('r-close').textContent") == f"Return to {name[0].upper()}{name[1:]} writeup"
    assert synthetic.js("() => document.getElementById('x-entry')") is None and "Record:" not in synthetic.js("() => document.getElementById('explain').textContent")
    synthetic.page.keyboard.press("Escape")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js(shown) == {"refs": False, "explain": True, "visible": True, "shade": True}, "Escape closes only the references, and the writeup comes back"
    synthetic.page.keyboard.press("Escape")
    assert not synthetic.dialog()["open"]


def test_a_glossary_tooltip_escapes_the_modal_and_stays_on_the_page(synthetic: Page) -> None:
    """Feature 182 (GM 2026-09-05): a definition box at the modal's edge "gets cut off, and the modal gains a
    horizontal scroll bar" - the box must be OUTSIDE the modal, free to cross the modal's edge, and inside
    the page. Run in a viewport narrow enough that a 22rem box at the rightmost defined word would cross
    the window's edge, so the clamp is exercised rather than assumed; the viewport is restored after."""
    was = synthetic.page.viewport_size
    synthetic.page.set_viewport_size({"width": 420, "height": 640})
    try:
        synthetic.js("() => window.l7rMap.fit()")
        synthetic.open("bund")
        word = synthetic.js(
            "() => { let best = null; for (const s of document.querySelectorAll('#explain .gl')) { const r = s.getBoundingClientRect(); if (r.width && (!best || r.left > best.left)) best = { left: r.left, x: r.left + r.width / 2, y: r.top + r.height / 2, def: s.getAttribute('data-def') }; } return best; }"
        )
        assert word and word["def"], "the bund's explanation carries a defined term"
        synthetic.page.mouse.move(word["x"], word["y"])
        synthetic.page.wait_for_timeout(50)
        got = synthetic.js(
            "() => { const t = document.getElementById('tip'); const r = t.getBoundingClientRect(); const d = document.getElementById('explain'); return { hidden: t.hidden, text: t.textContent, left: r.left, right: r.right, top: r.top, bottom: r.bottom, W: innerWidth, H: innerHeight, overflow: d.scrollWidth > d.clientWidth, inside: !!t.closest('dialog') }; }"
        )
        assert not got["hidden"] and got["text"] == word["def"], got
        assert not got["inside"], "the box is a sibling of the dialogs, not a child of the word"
        assert word["left"] + (got["right"] - got["left"]) > got["W"], "the box placed AT the word would have crossed the page's edge - the clamp had work to do"
        assert got["left"] >= 0 and got["right"] <= got["W"] and got["top"] >= 0 and got["bottom"] <= got["H"], got
        assert not got["overflow"], "the dialog gained no horizontal scroll bar"
        synthetic.page.mouse.move(2, 2)
        synthetic.page.wait_for_timeout(30)
        assert synthetic.js("() => document.getElementById('tip').hidden"), "gone when the pointer leaves the word"
        synthetic.page.mouse.move(word["x"], word["y"])
        synthetic.page.wait_for_timeout(30)
        synthetic.page.keyboard.press("Escape")
        synthetic.page.wait_for_timeout(30)
        assert not synthetic.dialog()["open"] and synthetic.js("() => document.getElementById('tip').hidden"), "gone when the dialog closes"
    finally:
        synthetic.page.set_viewport_size(was)
        synthetic.js("() => window.l7rMap.fitWidth()")


def test_a_sibling_link_lights_the_other_class_on_hover_and_replaces_the_modal_on_click(synthetic: Page) -> None:
    """GM 2026-08-28: "Not to be confused with the X" - hover lights X, click opens X's modal in place."""
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.center("windbreak", 0)
    # CLICK THE ELEMENT, not its bounding-box center (feature 146): a windbreak group is a scatter of clumps
    # and its bbox center can fall on bare ground between them, which is why this flaked under a loaded run.
    synthetic.page.locator('g.f[data-k="windbreak"]').first.click(force=True)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "windbreak" and synthetic.settles({"windbreak": 1}, synthetic.on) == {"windbreak": 1}
    assert "Not to be confused with the copse" in synthetic.dialog()["siblings"]
    assert synthetic.js("() => getComputedStyle(document.querySelector('#explain a.sib')).textDecorationLine") == "none", "feature 186: no dotted underline on a sibling link"
    lx, ly = synthetic.js("() => { const r = document.querySelector('#explain a.sib[data-k=\"copse\"]').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }")
    synthetic.page.mouse.move(lx, ly)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.settles({"copse": 1}, synthetic.on) == {"copse": 1}, "hovering the link lights the copse instead of the windbreak"
    synthetic.page.mouse.move(lx, ly + 200)
    synthetic.page.wait_for_timeout(30)
    assert synthetic.settles({"windbreak": 1}, synthetic.on) == {"windbreak": 1}, "leaving the link restores the pinned windbreak"
    synthetic.page.mouse.click(lx, ly)
    synthetic.page.wait_for_timeout(50)
    synthetic.page.mouse.move(lx, ly + 200)  # off the new modal's own link, which the pointer would otherwise be peeking
    synthetic.page.wait_for_timeout(30)
    d = synthetic.dialog()
    assert d["open"] and d["k"] == "copse" and synthetic.on() == {"copse": 1}, "clicking the link opens the copse's modal in place of the windbreak's"
    assert "Not to be confused with the windbreak" in d["siblings"]
    synthetic.page.keyboard.press("Escape")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.on() == {}
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_scrolling_stops_at_the_edge_of_the_map(synthetic: Page) -> None:
    """The GM (2026-08-28): scroll to the edge of the map, but not beyond it."""
    synthetic.js("() => window.l7rMap.fit()")
    for _ in range(3):
        synthetic.js("() => document.querySelector('#zoom [data-z=in]').click()")
    synthetic.page.mouse.move(700, 500)
    for _ in range(40):
        synthetic.page.mouse.wheel(-2000, -2000)
    synthetic.page.wait_for_timeout(50)
    v = synthetic.settles((0, 0), lambda: tuple(round(c) for c in (synthetic.js("() => window.l7rMap.view()")["tx"], synthetic.js("() => window.l7rMap.view()")["ty"])))
    assert v == (0, 0), "the map's top-left corner stops at the viewport's corner"
    for _ in range(40):
        synthetic.page.mouse.wheel(2000, 2000)
    synthetic.page.wait_for_timeout(50)
    r = synthetic.js("() => { const r = document.getElementById('map').getBoundingClientRect(); return [r.right, r.bottom, innerWidth, innerHeight]; }")
    assert abs(r[0] - r[2]) < 0.5 and abs(r[1] - r[3]) < 0.5, "the map's bottom-right corner stops at the viewport's corner"
    synthetic.js("() => window.l7rMap.fit()")
    synthetic.page.mouse.wheel(0, 500)
    synthetic.page.wait_for_timeout(30)
    assert abs(synthetic.js("() => window.l7rMap.zoom()") - 1.0) < 1e-9 and synthetic.js(
        "() => { const r = document.getElementById('map').getBoundingClientRect(); return r.top >= -0.5 && r.bottom <= innerHeight + 0.5; }"
    ), "at fit the whole map stays in view"
    synthetic.js("() => window.l7rMap.fitWidth()")


def test_the_record_page_defines_its_terms_on_hover_in_the_footnote_box(record: Page) -> None:
    """Feature 209 (GM 2026-09-07): "apply the same kind of tooltip rules to our research sections that we have
    in our diagram HTML pages." The glossary term in the heading, the prose and the quoted footnote is wrapped;
    the one in a code span is not; hovering shows the definition in the footnote box, and leaving hides it."""
    spans = record.js("() => Array.from(document.querySelectorAll('span.gl')).map(s => s.textContent)")
    assert spans == ["yashikirin", "kainyo", "sugi", "yashikirin"], "heading, prose (two terms), the footnote's quote - and never the code span"
    assert record.js("() => document.querySelector('code span.gl')") is None
    assert record.js("() => document.getElementById('fntip').hidden") is True
    record.page.hover("h2 span.gl")
    record.page.wait_for_timeout(30)
    shown = record.js("() => { const t = document.getElementById('fntip'); return t.hidden ? null : t.textContent; }")
    assert shown and shown.startswith("A homestead grove:"), shown
    box = record.js("() => { const r = document.getElementById('fntip').getBoundingClientRect(); return [r.left, r.right, window.innerWidth]; }")
    assert box[0] >= 0 and box[1] <= box[2], "the box stays inside the viewport"
    record.page.mouse.move(1, 1)
    record.page.wait_for_timeout(300)
    assert record.js("() => document.getElementById('fntip').hidden") is True
    record.page.hover("sup.fn a[href='#fn-1']")
    record.page.wait_for_timeout(30)
    note = record.js("() => document.getElementById('fntip').textContent")
    assert "a quoted passage" in note, "the footnote hover uses the same box"
    # FEATURE 211: a note that is NOT in the page - it lives on the citations page, and reaches this page as the
    # derived script's table - shows in the same box, with its glossary term marked and carrying its definition
    record.page.mouse.move(1, 1)
    record.page.wait_for_timeout(300)
    record.page.hover("sup.fn a[href$='#fn-2']")
    record.page.wait_for_timeout(30)
    note = record.js("() => document.getElementById('fntip').textContent")
    assert "a derived note naming a tameike" in note, f"a note from window.RECORD_CITATIONS shows in the box ({record.errors})"
    assert record.js("() => document.querySelector('#fntip span.gl').getAttribute('title')").startswith("An irrigation reservoir")
    assert record.errors == [] and record.requests == []
