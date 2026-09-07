# tests/full/interactive/page_browser/ - the Playwright browser test as a package

Split from `test_page_browser.py` on 2026-09-07 (feature 201 pushed it to 1,020 lines; constitution X
clause 13 is gated). Collection is unchanged: `make page-check` and the gate collect the directory.

| module | look here when |
|---|---|
| `conftest.py` | the browser or one of the three pages (`synthetic`, `inashiro`, `kuwabata`) will not open; the Playwright skip |
| `_driver.py` | the `Page` driver (`on`, `settles`, `center`, `point_at`, `hover_class`, `open`), `_mechanics` (what every tier proves), the synthetic map's strings |
| `test_synthetic.py` | the mechanics on the hand-built map: hover, click, the modal, zoom and scroll, the glossary, sibling links, hit boxes (features 134-186) |
| `test_reference.py` | the reference hamlet's real page and the blue plots (134, 159), feature 134's SC-004 timings, the research pages' footnotes (194) |
| `test_speed.py` | the page's speed on the GM's own page: the tiled merge's structural guard and pointer-move cap (199), raster mode - vector first, the id map, the switch, the raster-CPU caps (200), text as vector and the wash (201) |
