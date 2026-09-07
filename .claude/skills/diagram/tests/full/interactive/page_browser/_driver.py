"""The driver over one open page, the mechanics every tier runs, and the synthetic map (feature 134)."""

from __future__ import annotations

import time
from typing import Any

from l7r.diagram.interactive.classes import CLASSES, PLACE
from l7r.diagram.interactive.tags import Split


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


def _sweep_ms(page: Page) -> list[float]:
    """Wall time of each of 150 REAL pointer moves over a grid across the viewport - research.md R1's
    instrument. Each move fires `pointerover`, the page restyles the hovered class and Chromium repaints
    before the driver accepts the next move, so the number is what a reader's hand feels."""

    times: list[float] = []
    for y in range(50, 1000, 95):
        for x in range(50, 1400, 90):
            t0 = time.perf_counter()
            page.page.mouse.move(x, y)
            times.append((time.perf_counter() - t0) * 1000)
    page.page.mouse.move(0, 0)
    return times
