"""THE FULL TREE (the GM, 2026-08-28: a 15 s browser test belongs with the lengthy tests - *"I agree that that is where it belongs"*; feature 135's three-tree rule): collected by the FULL run and the AWS check, never by quick or the gate.

The page in a real browser (feature 134, spec FR-012 - a page that was never opened has not been
verified). Playwright drives headless Chromium over a plain `file://` open.

Two tiers. The SYNTHETIC page (quick) is a hand-built map of a dozen classed primitives: it proves
the mechanics - hover lights every group of a class and none of another, a label and its subject
are one class, a click opens the modal with the label words and the present siblings only, Escape
/ the close button / the backdrop close it, zero console errors, zero network requests. The
REFERENCE HAMLET page (`rolls_map`, the gate) generates Inashiro and proves the same on the real
16 MB page for every class and every sibling pair present, and records the timings SC-004 asks for.

Skipped with a reason when Playwright or its Chromium is absent (`setup-dev-env.sh` installs both).
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.page import render_page
from l7r.diagram.interactive.tags import Split

playwright = pytest.importorskip("playwright.sync_api", reason="playwright is not installed (pip install -r requirements-dev.txt)")


@pytest.fixture(scope="module")
def browser() -> Iterator[Any]:
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # noqa: BLE001 - the launch error is the reason to skip, whatever its type
            pytest.skip(f"Chromium is not installed for Playwright (python3 -m playwright install --with-deps chromium): {e}")
        yield b
        b.close()


class Page:
    """A thin driver over one open page: the checks every tier runs."""

    def __init__(self, browser: Any, path: str) -> None:
        self.errors: list[str] = []
        self.requests: list[str] = []
        self.page = browser.new_page(viewport={"width": 1400, "height": 1000})
        self.page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("request", lambda r: self.requests.append(r.url) if not r.url.startswith("file://") else None)
        self.page.goto("file://" + path, wait_until="load")

    def js(self, script: str, *args: Any) -> Any:
        return self.page.evaluate(script, *args)

    def on(self) -> dict[str, int]:
        """How many groups of each class carry the highlighted state right now."""
        return self.js("() => { const o = {}; for (const g of document.querySelectorAll('g.f.on')) { const k = g.getAttribute('data-k'); o[k] = (o[k] || 0) + 1; } return o; }")

    def settles(self, want: Any, read: Any, ms: int = 2000) -> Any:
        """Poll `read()` until it equals `want`, up to `ms` (feature 145). A fixed `wait_for_timeout(30)`
        after a mouse move is enough on an idle box and not enough under a loaded FULL run - these two
        assertions (the sibling-link hover, the scroll clamp) failed there on 2026-08-28 and passed alone
        in two trees a minute later. Waiting for the STATE, bounded, keeps the assertion exactly as strict."""
        got = read()
        for _ in range(max(1, ms // 25)):
            if got == want:
                return got
            self.page.wait_for_timeout(25)
            got = read()
        return got

    def groups(self, key: str) -> int:
        return self.js("k => window.l7rMap.count(k)", key)

    def center(self, key: str, nth: int = 0) -> tuple[float, float]:
        return tuple(
            self.js(
                "([k, n]) => { const g = document.querySelectorAll('g.f[data-k=\"' + k + '\"]')[n]; const r = g.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }", [key, nth]
            )
        )

    def point_at(self, key: str, nth: int = 0) -> None:
        """Put a REAL pointer on the nth group of `key` - on the element, not on its bounding-box center.

        `center` returns the middle of the group's bbox, and a group is not its bbox: a farmhouse's ink is a
        roof block and a ridge line, so the bbox center can land on bare parchment between them and light
        nothing. That is intermittent by construction (it depends on the drawn geometry), and it failed a
        parallel FULL run on 2026-08-28 and again alone a few minutes later on identical code. Playwright's
        own hover picks a point INSIDE the element, which is what "a real pointer on the farmhouse" means."""
        self.page.locator(f'g.f[data-k="{key}"]').nth(nth).hover(force=True)

    def hover_class(self, key: str) -> dict[str, int]:
        self.js("k => window.l7rMap.highlight(k)", key)
        return self.on()

    def clear(self) -> None:
        self.js("() => window.l7rMap.highlight(null)")

    def open(self, key: str) -> dict[str, Any]:
        self.js("k => window.l7rMap.open(k)", key)
        return self.dialog()

    def dialog(self) -> dict[str, Any]:
        return self.js(
            "() => { const d = document.getElementById('explain'); return { open: d.open, k: d.getAttribute('data-k'), label: d.getAttribute('data-label'), name: document.getElementById('x-name').textContent, labeltext: document.getElementById('x-label').textContent, siblings: document.getElementById('x-siblings').textContent, sources: document.getElementById('x-refs').textContent }; }"
        )

    def close(self) -> None:
        self.page.close()


def _assert_only(on: dict[str, int], key: str, page: Page) -> None:
    assert set(on) == {key}, f"hovering {key!r} lit {sorted(on)}"
    assert on[key] == page.groups(key), f"hovering {key!r} lit {on[key]} of {page.groups(key)} groups"


def _mechanics(page: Page, present: list[str]) -> None:
    """The checks both tiers share, for every present class and every present sibling pair."""
    for key in present:
        _assert_only(page.hover_class(key), key, page)
    page.clear()
    assert page.on() == {}
    for key in present:
        for other in CLASSES[key].siblings:
            if other in present:
                on = page.hover_class(key)
                assert other not in on, f"hovering {key!r} lit its sibling {other!r}"
    page.clear()
    for key in present:
        d = page.open(key)
        assert d["open"] and d["k"] == key and d["name"].lower() == key
        assert d["label"] == CLASSES[key].label
        assert CLASSES[key].label_note[:30] in d["labeltext"]
        assert any(w in d["labeltext"] for w in ("historically accurate", "deliberate deviation", "a guess"))
        for other in CLASSES[key].siblings:
            assert (("the " + CLASSES[other].name) in d["siblings"]) == (other in present), (key, other)
        page.page.keyboard.press("Escape")
        assert not page.dialog()["open"]
    assert page.errors == [], page.errors
    assert page.requests == [], page.requests


# ---- the synthetic page (quick)

R = '<rect x="{x}" y="{y}" width="30" height="20" fill="#abc" stroke="#123"/>'
T = '<text x="{x}" y="{y}" font-size="8">{t}</text>'


def _synthetic() -> tuple[list[str], list[Any]]:
    strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">', '<rect width="300" height="200" fill="#EFE3C2"/>']
    tags: list[Any] = [None, "-"]
    for i, key in enumerate(("farmhouse", "farmhouse", "storage shed", "byre", "windbreak", "copse", "marsh", "marsh")):
        strings.append(R.format(x=10 + 35 * i, y=10))
        tags.append(key)
    strings.append(R.format(x=10, y=60))
    tags.append(Split("paddy", "bund"))
    strings.append(R.format(x=60, y=60))
    tags.append("notice board")
    strings.append(T.format(x=60, y=95, t="notice board"))
    tags.append("notice board")
    strings.append('<path d="M20,150 L120,150" fill="none" stroke="#C9AE79" stroke-width="1.0"/>')  # a thin lane
    tags.append("village lane")
    strings.append('<g stroke="#A7A860" stroke-width="0.8"><line x1="20" y1="180" x2="21" y2="184"/><line x1="30" y1="182" x2="31" y2="186"/></g>')  # two scrub blades in one corner
    tags.append("scrub and rough grazing")
    strings.append("</svg>")
    tags.append(None)
    return strings, tags


@pytest.fixture(scope="module")
def synthetic(browser: Any) -> Iterator[Page]:
    strings, tags = _synthetic()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "synthetic.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                render_page(
                    strings,
                    tags,
                    "Synthetic",
                    {"ftpx": 1.0},
                    {"marshes": [{"role": "toe", "poly": [[220, 100], [290, 100], [290, 190], [220, 190]]}], "commons": [{"role": "grazing", "poly": [[0, 120], [300, 120], [300, 200], [0, 200]]}]},
                )
            )
        page = Page(browser, path)
        yield page
        page.close()


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
    assert synthetic.js("() => document.getElementById('references').open && document.getElementById('explain').open"), "the references modal opens ON TOP of the explanation, which stays open"
    assert synthetic.js("() => document.getElementById('r-list').children.length") >= 1
    synthetic.page.keyboard.press("Escape")
    synthetic.page.wait_for_timeout(30)
    assert synthetic.js("() => !document.getElementById('references').open && document.getElementById('explain').open"), "Escape closes only the top modal"
    synthetic.page.keyboard.press("Escape")
    assert not synthetic.dialog()["open"]


def test_a_sibling_link_lights_the_other_class_on_hover_and_replaces_the_modal_on_click(synthetic: Page) -> None:
    """GM 2026-08-28: "Not to be confused with the X" - hover lights X, click opens X's modal in place."""
    synthetic.js("() => window.l7rMap.fit()")
    x, y = synthetic.center("windbreak", 0)
    synthetic.page.mouse.click(x, y)
    synthetic.page.wait_for_timeout(50)
    assert synthetic.dialog()["k"] == "windbreak" and synthetic.settles({"windbreak": 1}, synthetic.on) == {"windbreak": 1}
    assert "Not to be confused with the copse" in synthetic.dialog()["siblings"]
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


# ---- the reference hamlet (the gate)


@pytest.fixture(scope="module")
def inashiro(browser: Any) -> Iterator[tuple[Page, dict[str, Any]]]:
    from l7r.diagram import hamletgen as hg

    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "inashiro")
        hg.generate(hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}), out_base=base, render=False)
        with open(base + ".json") as fh:
            import json

            m = json.load(fh)
        page = Page(browser, base + ".html")
        yield page, m
        page.close()


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
    } <= set(present)
    _mechanics(page, present)


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
    assert worst < 100, f"highlight took {worst:.1f} ms"
    assert load_ms < 5000, f"load took {load_ms} ms"
