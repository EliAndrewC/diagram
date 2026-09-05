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

from l7r.diagram.interactive.classes import CLASSES, PLACE
from l7r.diagram.interactive.page import render_page
from l7r.diagram.interactive.sources import RESEARCH_URL
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
            "() => { const d = document.getElementById('explain'); return { open: d.open, k: d.getAttribute('data-k'), label: d.getAttribute('data-label'), name: document.getElementById('x-name').textContent, labeltext: document.getElementById('x-label').textContent, caveat: document.getElementById('x-caveat').textContent, siblings: document.getElementById('x-siblings').textContent, sources: document.getElementById('x-refs').textContent }; }"
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
        # THE HEADING RENDERS THE CLASS'S DECLARED NAME, WHICH IS NOT THE KEY (feature 153, GM
        # 2026-08-29: the modal should "actually say 'Windbreak forest' instead of just 'windbreak'").
        # This asserted `name == key`, which held only while every name happened to equal its key -
        # so the first class given a fuller name turned a correct change red. Same-source doctrine:
        # the test reads the registry the page reads. The KEY is still pinned separately, above,
        # because that is what the ink carries and what `all_ink_is_ruled_on` reads.
        assert d["open"] and d["k"] == key and d["name"].lower() == CLASSES[key].name.lower()
        assert d["label"] == CLASSES[key].label, "the classification still reaches the page (constitution XII)"
        # THE PRESUMPTION OF ACCURACY (feature 156): an accurate class says nothing about accuracy at
        # all - the lead line is empty and hidden - while a deviation or a guess still opens with its
        # liberty. The caveat, where the record discloses one, sits below the why instead.
        if CLASSES[key].label == "accurate":
            assert d["labeltext"] == "", f"{key}: an accurate class announced itself"
        else:
            assert CLASSES[key].label_note[:30] in d["labeltext"]
            assert any(w in d["labeltext"] for w in ("deliberate deviation", "a guess", "Note: we have"))
        assert "historically accurate" not in d["labeltext"]
        assert (CLASSES[key].caveat[:30] in d["caveat"]) if CLASSES[key].caveat else (d["caveat"] == "")
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
    # the title placard the way finish.py emits it: the card, then the name over it, both `place`.
    # ON EMPTY GROUND (feature 174, 2026-09-02): it was first placed at x=150 y=10, which is exactly
    # where the windbreak rect sits (150-180, 10-30) - and being appended last it is drawn ON TOP of
    # it. `test_a_sibling_link_lights_the_other_class...` force-clicks the windbreak group, the event
    # lands on whatever is topmost there, and the map answered with a neighbouring class instead. The
    # band y=105..145 is clear of the feature row (y 10-30), the paddy and notice board (y 60-95), the
    # lane (y 150) and the scrub blades (y ~180).
    strings.append('<g><rect x="150" y="105" width="120" height="40" rx="7" fill="#F7F0DC" stroke="#8C7A55" stroke-width="1.6"/></g>')
    tags.append(PLACE)
    strings.append('<text x="210" y="131" text-anchor="middle" font-size="16" font-weight="bold" fill="#2D2A24">Synthetic</text>')
    tags.append(PLACE)
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


def test_the_lit_placard_keeps_its_name_readable(synthetic: Page) -> None:
    """Feature 176 (GM 2026-09-02): "I should be able to see and read the name of the hamlet while the
    title card is highlighted." The card goes gold like any lit class; the name stays in the ink."""
    assert synthetic.hover_class(PLACE) == {PLACE: 2}, "the card and its name light together"
    card = synthetic.js(f"() => getComputedStyle(document.querySelector('g.f[data-k=\"{PLACE}\"] rect')).fill")
    name = synthetic.js(f"() => getComputedStyle(document.querySelector('g.f[data-k=\"{PLACE}\"] text')).fill")
    assert card == "rgb(255, 200, 61)", f"the lit card is the highlight gold, got {card}"
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
    # record on GitHub, the button says where it returns to, and the explanation carries no "Record:" line
    links = synthetic.js("() => Array.from(document.querySelectorAll('#r-list a.q')).map(a => [a.textContent, a.getAttribute('href'), a.getAttribute('target')])")
    assert links and all(t and h.startswith(RESEARCH_URL) and "#" in h and tg == "_blank" for t, h, tg in links), links
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
    reach = page.js(
        """() => {
            const g = document.querySelector('g.f[data-k="wet paddy"]');
            const r = g.getBoundingClientRect();
            let hit = 0, tried = 0;
            for (let i = 1; i < 10; i++) for (let j = 1; j < 10; j++) {
                const x = r.x + r.width * i / 10, y = r.y + r.height * j / 10;
                if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) continue;
                tried++;
                const el = document.elementFromPoint(x, y);
                const owner = el && el.closest ? el.closest('g.f') : null;
                if (owner && owner.getAttribute('data-k') === 'wet paddy') hit++;
            }
            return [hit, tried];
        }"""
    )
    assert reach[1] > 0, "the plot is off-screen at the opening view - the probe measured nothing"
    assert reach[0] > 0, f"no point inside the blue plot's box reaches it with a real pointer ({reach[0]}/{reach[1]})"
    # ...and landing on it lights the blue plots and no green one
    page.js(
        """() => {
            const g = document.querySelector('g.f[data-k="wet paddy"]');
            const r = g.getBoundingClientRect();
            for (let i = 1; i < 10; i++) for (let j = 1; j < 10; j++) {
                const x = r.x + r.width * i / 10, y = r.y + r.height * j / 10;
                const el = document.elementFromPoint(x, y);
                const owner = el && el.closest ? el.closest('g.f') : null;
                if (owner && owner.getAttribute('data-k') === 'wet paddy') { owner.dispatchEvent(new PointerEvent('pointerover', {bubbles: true})); return; }
            }
        }"""
    )
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
    assert worst < 100, f"highlight took {worst:.1f} ms"
    assert load_ms < 5000, f"load took {load_ms} ms"
