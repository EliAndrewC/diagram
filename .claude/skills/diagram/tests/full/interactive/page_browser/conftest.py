"""The Playwright browser and the ONE page the tests drive - the synthetic map (feature 134; split into a
package on 2026-09-07 when the one file passed the 1,000-line bar - constitution X clause 13). Skipped with
a reason when Playwright or its Chromium is absent (`setup-dev-env.sh` installs both).

THERE IS NO ROLLED PAGE HERE, AND NO TIMING (GM 2026-09-07). The `inashiro` and `kuwabata` fixtures - a real
hamletgen roll and, for Kuwabata, its 18.6-megapixel raster, rebuilt by EVERY xdist worker - and the thirteen
tests over them (the reference mechanics and timings of feature 134, the blue plots of 159, the footnote hover
of 194, the pointer-move and raster-CPU caps of 199-203) were retired the day the container crashed twice
under them: the package alone cost 3.9 GiB at 8 workers against an 8 GiB cap. The GM: *"the performance tests
are never really going to be good enough to detect whether a human feels that the page is too sluggish. that
is fundamentally a matter of judgment and vibes ... the juice is not worth the squeeze."* A speed request is
measured by hand in a browser while it is being worked and the numbers go in its research.md - never a
repeatable test that runs at the gate or on a page edit (`l7r/diagram/interactive/CLAUDE.md`, "Verifying")."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest

from l7r.diagram.interactive.page import render_page
from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests.full.interactive.page_browser._driver import Page, _synthetic

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


#: A synthetic RESEARCH page (feature 209): the record's three assets by absolute file URL, a heading and a
#: sentence that use a glossary term, the same term in a code span (never wrapped), one footnote in the page and
#: - feature 211 - one whose note is only in `window.RECORD_CITATIONS` (the shape `make citations` derives from a
#: citations page, inlined here so the page needs no second file) - enough to prove the glossary hover and both
#: footnote hovers share one box, on a page of fifteen elements rather than a real record page (the GM's ruling
#: of 2026-09-07: no browser test loads a rolled or real page).
RECORD_PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Synthetic record</title>
<link rel="stylesheet" href="file://{assets}/record.css">
<script src="file://{assets}/glossary.js" defer></script>
<script src="file://{assets}/record.js" defer></script></head><body><main>
<h2 id="homestead-groves-yashikirin">Homestead groves (yashikirin)</h2>
<!-- Grounds: a comment the reader never sees; yashikirin -->
<script>window.RECORD_CITATIONS = {{"fn-2": "<a href='https://example.invalid/'><code>b-key</code></a> - 「a derived note naming a tameike」"}};</script>
<p>The kainyo of the Tonami plain is a stand of sugi,<sup class="fn"><a id="fnref-1" href="#fn-1">1</a></sup> and <code>yashikirin</code> is the knob.<sup class="fn"><a id="fnref-2" href="citations/record.html#fn-2">2</a></sup></p>
<section class="footnotes"><ol><li id="fn-1"><a href="https://example.invalid/"><code>a-key</code></a> - 「a quoted passage about a yashikirin」 <a class="fnback" href="#fnref-1">back</a></li></ol></section>
</main></body></html>"""


@pytest.fixture(scope="module")
def record(browser: Any) -> Iterator[Page]:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "record.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(RECORD_PAGE.format(assets=os.path.join(RESEARCH_DIR, "assets")))
        page = Page(browser, path)
        yield page
        page.close()
