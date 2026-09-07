"""The page's SPEED, on the page the GM reported: feature 199 (the tiled merge - the structural guard and the
pointer-move cap), 200 (raster mode - vector first, the id map, the switch, the raster-CPU caps) and 201 (text
as vector, the wash)."""

from __future__ import annotations

import statistics
from typing import Any

import pytest

from tests.full.interactive.page_browser._driver import Page, _sweep_ms


def _anchor_cells(d: str) -> set[tuple[int, int]]:
    """The TILE cells of a merged path's subpath anchors: a line subpath starts at its anchor, an arc
    subpath (circle, ellipse) starts a radius left of its center, which is the anchor."""
    import math
    import re

    from l7r.diagram.interactive.page import TILE

    cells: set[tuple[int, int]] = set()
    for m in re.finditer(r"M(-?[\d.]+),(-?[\d.]+)(a(-?[\d.]+))?", d):
        x, y = float(m.group(1)), float(m.group(2))
        if m.group(3):
            x += float(m.group(4))
        cells.add((math.floor(x / TILE), math.floor(y / TILE)))
    return cells


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_every_large_merged_path_on_the_reference_page_is_one_cell(inashiro: tuple[Page, dict[str, Any]]) -> None:
    """Feature 199 FR-007, the structural guard: on the real rolled page every `<path>` of TILE_MIN or
    more subpaths is confined to one TILE cell. Deterministic, whatever the machine is doing - untiled,
    the six giant scatter paths span 8 to 30 cells each, so a split that stops running fails here at
    once. Paths UNDER the threshold are exempt on purpose: the merge has gathered separated elements since
    feature 148, and spec-fidelity measured 280-289 sub-threshold merged paths spanning more than 400 px
    on the reference page - each a correct output of FR-001."""
    import re

    from l7r.diagram.interactive.page import TILE_MIN

    page, _m = inashiro
    with open(page.page.url[len("file://") :], encoding="utf-8") as fh:
        html = fh.read()
    large = [d for d in re.findall(r'<path [^>]*?d="([^"]*)"', html) if d.count("M") >= TILE_MIN]
    assert len(large) >= 10, f"the reference page has {len(large)} paths of {TILE_MIN}+ subpaths - the guard would be testing nothing"
    spanning = [(d.count("M"), sorted(_anchor_cells(d))) for d in large if len(_anchor_cells(d)) > 1]
    assert spanning == [], f"{len(spanning)} large merged paths span more than one cell: {spanning[:3]}"


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_kuwabata_pointer_moves_are_cheap_at_the_opening_view(kuwabata: Page) -> None:
    """Feature 199 FR-008: the GM's own symptom on the GM's own page. Research.md R2 measured 57.0 ms per
    real pointer move at Kuwabata's opening view before the tiling and 17.3 after; the cap sits between
    them - 2.3x over the tiled page for a loaded FULL run, 20 ms under the untiled one.

    ON THE MEAN, NOT THE MEDIAN (research.md R6, measured in this harness with the split switched off):
    untiled the moves are mean 59.5 / median 21.0 / p90 156 / max 183 ms, tiled 17.1 / 16.7 / 20.5 / 32.5.
    The cost lands on the one move in five that crosses into a map-spanning class and repaints the whole
    scrub; the median never sees those moves and PASSED the untiled page, so a cap on it could not fail.
    The mean is what a reader's hand feels, and a single scheduler stall under `-n auto` moves a mean of
    150 by a millisecond. The structural guard above is the deterministic half; this is the half that
    fails on what the GM felt."""

    times = _sweep_ms(kuwabata)
    mean = statistics.fmean(times)
    print(f"kuwabata opening view: mean {mean:.1f} ms per pointer move, median {statistics.median(times):.1f}, p90 {sorted(times)[int(len(times) * 0.9)]:.1f}, max {max(times):.1f}, n={len(times)}")
    assert mean < 40, f"mean {mean:.1f} ms per pointer move at Kuwabata's opening view (untiled measured 59.5, tiled 17.1)"


# ---- feature 200: raster mode below the vector (GM 2026-09-07: "all of the above feel slow") -------

TRACE_CATS = ("devtools.timeline", "disabled-by-default-devtools.timeline", "cc")


def raster_cpu_ms(page: Page, fn: Any) -> float:
    """The rasterizer CPU `fn()` costs, in ms summed over Chromium's worker threads, from a Chrome DevTools
    trace - feature 200 FR-011's instrument. A CPU sum moves by percent under machine load where wall time
    moves by multiples (feature 199 R6), which is why the gate can cap it."""
    cdp = page.page.context.new_cdp_session(page.page)
    buf: list[dict[str, Any]] = []
    done: list[int] = []
    cdp.on("Tracing.dataCollected", lambda ev: buf.extend(ev["value"]))
    cdp.on("Tracing.tracingComplete", lambda _ev: done.append(1))
    cdp.send("Tracing.start", {"categories": ",".join(TRACE_CATS), "transferMode": "ReportEvents"})
    fn()
    page.page.wait_for_timeout(250)  # the raster tasks the action queued
    cdp.send("Tracing.end")
    for _ in range(200):
        if done:
            break
        page.page.wait_for_timeout(25)
    cdp.detach()
    return sum(e["dur"] / 1000.0 for e in buf if e.get("ph") == "X" and e.get("name") == "RasterTask")


def _frame(page: Page) -> None:
    page.js("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def _raster_ready(page: Page) -> bool:
    return bool(page.settles(True, lambda: page.js("() => window.l7rMap.rasterReady()"), ms=8000))


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_kuwabata_paints_the_vector_first_and_then_enters_raster_mode(kuwabata: Page) -> None:
    """FR-010 (a) and (b), FR-016: the very first apply() chose vector - the first frame costs what it costs
    today - and once the picture and the id map are decoded the opening view is raster. `readyAt` is the
    ms after navigation raster mode became available; SC-003 asks 0.8 s on an idle box and the cap here is
    a loaded-run multiple of it."""
    page = kuwabata
    assert page.js("() => window.l7rMap.firstMode()") == "vector", "the first frame must be the vector page (FR-016)"
    assert _raster_ready(page), "the picture and the id map never decoded"
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    assert page.js("() => window.l7rMap.mode()") == "raster"
    assert page.js("() => document.getElementById('map').getAttribute('data-mode')") == "raster"
    ready_at = page.js("() => window.l7rMap.readyAt()")
    print(f"kuwabata: raster mode ready {ready_at:.0f} ms after navigation")
    assert ready_at < 4000, f"raster mode took {ready_at:.0f} ms to become available"


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_in_raster_mode_the_id_map_lights_a_class_and_a_click_opens_it(kuwabata: Page) -> None:
    """FR-010 (c): with every vector group hidden, a real pointer over the scrub still lights it (drawn lit
    as vector above the image) and a click opens its modal - both answered from the id map."""
    page = kuwabata
    assert _raster_ready(page)
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    pt = page.js(
        """() => { for (let y = 40; y < innerHeight; y += 15) for (let x = 40; x < innerWidth - 80; x += 15) { if (window.l7rMap.keyAtPoint(x, y) === 'scrub and rough grazing') return [x, y]; } return null; }"""
    )
    assert pt is not None, "no scrub under the opening view"
    page.page.mouse.move(pt[0], pt[1])
    lit = page.settles({"scrub and rough grazing": page.groups("scrub and rough grazing")}, page.on)
    assert lit == {"scrub and rough grazing": page.groups("scrub and rough grazing")}, f"the pointer lit {lit}"
    assert page.js("() => getComputedStyle(document.querySelector('g.f.on')).display") != "none", "the lit class is drawn"
    page.page.mouse.click(pt[0], pt[1])
    got = page.settles("scrub and rough grazing", lambda: page.dialog()["k"] if page.dialog()["open"] else None)
    assert got == "scrub and rough grazing", "the click opened the modal from the id map"
    page.page.keyboard.press("Escape")
    page.page.mouse.move(0, 0)
    page.settles({}, page.on)


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_the_id_map_agrees_with_the_dom_on_a_grid(kuwabata: Page) -> None:
    """FR-010 (d): the id map is the DOM's own hit-testing rule rendered once - painted geometry, draw
    order, the hit copies - so with the vector groups shown the two must name the same class almost
    everywhere. Measured 98.2% on the prototype; the rest are single-pixel boundaries. Points under the
    zoom buttons are skipped (the DOM hits the button)."""
    page = kuwabata
    assert _raster_ready(page)
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    agree = page.js("""() => {
        const svg = document.getElementById('map'); svg.setAttribute('data-mode', 'vector');
        let same = 0, n = 0;
        for (let y = 30; y < innerHeight; y += 25) for (let x = 30; x < innerWidth; x += 25) {
            const el = document.elementFromPoint(x, y);
            if (el && el.closest && el.closest('#zoom')) continue;
            const g = el && el.closest ? el.closest('g.f') : null;
            const dom = g ? g.getAttribute('data-k') : null;
            n++; if (dom === window.l7rMap.keyAtPoint(x, y)) same++;
        }
        svg.setAttribute('data-mode', window.l7rMap.mode());
        return [same, n];
    }""")
    print(f"kuwabata: id map agrees with the DOM on {agree[0]}/{agree[1]} points ({100 * agree[0] / agree[1]:.1f}%)")
    assert agree[1] > 1500 and agree[0] >= 0.97 * agree[1], f"the id map agrees with the DOM on only {agree[0]}/{agree[1]}"


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_zooming_past_the_switch_is_vector_and_fit_is_raster_again(kuwabata: Page) -> None:
    """FR-010 (e), FR-004: at DPR 1 Kuwabata's opening view (1.31 px per map px) and the first `+` (2.62)
    are under RASTER_R = 3; the second `+` (5.2) is not; `fit` comes back under it."""
    page = kuwabata
    assert _raster_ready(page)
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    assert page.js("() => window.l7rMap.mode()") == "raster"
    page.page.keyboard.press("+")
    _frame(page)
    assert page.js("() => window.l7rMap.mode()") == "raster", "the first + is still under the switch at DPR 1"
    page.page.keyboard.press("+")
    _frame(page)
    assert page.js("() => window.l7rMap.mode()") == "vector"
    assert page.js("() => document.getElementById('map').getAttribute('data-mode')") == "vector"
    page.js("() => window.l7rMap.fit()")
    _frame(page)
    assert page.js("() => window.l7rMap.mode()") == "raster"
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_kuwabata_raster_cpu_caps(kuwabata: Page) -> None:
    """FR-011, the gate's raster-CPU guards on the GM's page at the GM's view: hovering the scrub under
    100 ms of RasterTask CPU (prototype 32-38; the vector page 221-251), one wheel turn under 60 (12-14;
    163-178). Deliberately looser than SC-001's idle-box criteria (60 / 25): a loaded FULL run must clear
    them without flaking, and both still fail the vector page by 2x."""
    page = kuwabata
    assert _raster_ready(page)
    page.js("() => window.l7rMap.fitWidth()")
    page.page.mouse.move(0, 0)
    _frame(page)
    hover = raster_cpu_ms(page, lambda: (page.js("k => window.l7rMap.highlight(k)", "scrub and rough grazing"), _frame(page)))
    page.js("() => window.l7rMap.highlight(null)")
    _frame(page)
    page.page.mouse.move(700, 500)
    _frame(page)
    wheel = raster_cpu_ms(page, lambda: (page.page.mouse.wheel(0, 120), _frame(page)))
    page.page.mouse.move(0, 0)
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    print(f"kuwabata opening view: hover the scrub {hover:.0f} ms of raster CPU, one wheel turn {wheel:.0f} ms")
    assert hover < 100, f"hovering the scrub rasterized {hover:.0f} ms of CPU (raster mode 32-38, the vector page 221-251)"
    assert wheel < 60, f"a wheel turn rasterized {wheel:.0f} ms of CPU (raster mode 12-14, the vector page 163-178)"


# ---- feature 201: raster mode keeps the neighbors (GM 2026-09-07) ---------------------------------------


@pytest.mark.rolls_map
@pytest.mark.tiers("hamlet")
def test_in_raster_mode_text_is_vector_and_the_lit_class_is_a_wash(kuwabata: Page) -> None:
    """Feature 201 FR-006. Every <text> is displayed in raster mode (the picture carries none, so the scale
    reads once and the placard's name is one font lit or unlit); the only displayed leaf ink outside <defs>
    and the raster image is inside the lit group; a lit paddy's fill is the 0.45 wash so the bunds beneath
    show through; a lit class inside an opacity wrapper (the stream) still shows its ink. With feature 200's
    group rule restored, the text assertion fails (SC-003)."""
    page = kuwabata
    assert _raster_ready(page)
    page.js("() => window.l7rMap.fitWidth()")
    _frame(page)
    page.js("() => window.l7rMap.highlight(null)")
    r = page.js("""() => {
        const vis = sel => [...document.querySelectorAll(sel)].filter(e => e.checkVisibility());  // an ancestor's display:none counts; a computed display does not inherit
        const out = {};
        out.text = [vis('svg#map text').length, document.querySelectorAll('svg#map text').length];
        out.leaves_unlit = vis('svg#map :is(path,circle,ellipse,line,rect,polygon,polyline,image)').filter(e => !e.closest('defs') && !e.closest('g.raster')).length;
        window.l7rMap.highlight('place');
        const name = document.querySelector('g.f.on text'); const cs = getComputedStyle(name);
        out.place_lit = [cs.fill, cs.fillOpacity, cs.fontFamily, cs.fontSize];
        window.l7rMap.highlight(null);
        const cu = getComputedStyle(document.querySelector('g.f[data-k="place"] text'));
        out.place_unlit = [cu.fontFamily, cu.fontSize];
        window.l7rMap.highlight('paddy');
        out.paddy_wash = getComputedStyle(document.querySelector('g.f.on :is(polygon,path):not([fill="none"])')).fillOpacity;
        out.paddy_leaves = vis('g.f.on :is(polygon,path)').length;
        window.l7rMap.highlight('stream');
        out.stream_leaves = vis('g.f.on :is(path,line)').length;
        window.l7rMap.highlight(null);
        return out;
    }""")
    print(f"kuwabata raster mode: {r}")
    assert r["text"][0] == r["text"][1] > 0, f"every text element is displayed in raster mode: {r['text']}"
    assert r["leaves_unlit"] == 0, f"{r['leaves_unlit']} leaf ink elements displayed outside a lit group"
    assert r["place_lit"][0] == "rgb(45, 42, 36)" and r["place_lit"][1] == "1", "the lit placard's name keeps the ink at full opacity"
    assert r["place_lit"][2:] == r["place_unlit"], "the lit name is the unlit name's font and size"
    assert r["paddy_wash"] == "0.45" and r["paddy_leaves"] > 0, "a lit paddy is the wash"
    assert r["stream_leaves"] > 0, "a lit class inside an opacity wrapper still shows its ink"
