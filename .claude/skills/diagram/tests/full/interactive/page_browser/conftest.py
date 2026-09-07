"""The Playwright browser and the three pages the tests drive (feature 134; split into a package on
2026-09-07 when the one file passed the 1,000-line bar - constitution X clause 13). Skipped with a reason
when Playwright or its Chromium is absent (`setup-dev-env.sh` installs both)."""

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


@pytest.fixture(scope="module")
def kuwabata(browser: Any) -> Iterator[Page]:
    """The page the GM reported (feature 199): the pool's own declaration, generated the way `inashiro` is."""
    from l7r.diagram import hamletgen as hg

    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "kuwabata")
        hg.generate(
            hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"), out_base=base, render=False
        )
        page = Page(browser, base + ".html")
        yield page
        page.close()
