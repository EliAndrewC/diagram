# tests/full/interactive/page_browser/ - the Playwright browser test as a package

A package because one file passed the 1,000-line bar; `make page-check` and the gate collect the directory.

| module | look here when |
|---|---|
| `conftest.py` | the browser or the synthetic page will not open; the Playwright skip; and WHY there is no rolled page and no timing here (GM 2026-09-07) |
| `_driver.py` | the `Page` driver (`on`, `settles`, `center`, `point_at`, `hover_class`, `open`), `_mechanics` (what every tier proves), the synthetic map's strings |
| `test_synthetic.py` | the mechanics on the hand-built map: hover, click, the modal, zoom and scroll, the glossary, sibling links, hit boxes |
| `test_page_lit.py` | `tools/page_lit.measure` against a real page in raster mode: `rasterReady`, a class lit through `window.l7rMap.highlight`, `getScreenCTM` (its pure halves are `tests/tools/test_page_lit.py`) |

**Don't re-add a rolled-page or timing test here** (retired by the GM, 2026-09-07): every xdist worker rolled its own
Inashiro and Kuwabata and launched its own Chromium - 3.9 GiB at 8 workers in an 8 GiB container that had crashed twice -
and a timing cap cannot say whether a page FEELS slow. The ruling in full is in `conftest.py`.
