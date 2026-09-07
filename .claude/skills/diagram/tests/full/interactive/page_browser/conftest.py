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
