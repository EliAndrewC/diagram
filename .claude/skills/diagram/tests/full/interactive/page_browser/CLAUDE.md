# tests/full/interactive/page_browser/ - the Playwright browser test as a package

Split from `test_page_browser.py` on 2026-09-07 (feature 201 pushed it to 1,020 lines; constitution X
clause 13 is gated). Collection is unchanged: `make page-check` and the gate collect the directory.

| module | look here when |
|---|---|
| `conftest.py` | the browser or the synthetic page will not open; the Playwright skip; and WHY there is no rolled page and no timing here (GM 2026-09-07) |
| `_driver.py` | the `Page` driver (`on`, `settles`, `center`, `point_at`, `hover_class`, `open`), `_mechanics` (what every tier proves), the synthetic map's strings |
| `test_synthetic.py` | the mechanics on the hand-built map: hover, click, the modal, zoom and scroll, the glossary, sibling links, hit boxes (features 134-186) |

**Retired 2026-09-07 by the GM**: `test_reference.py` (the reference hamlet's real page, the blue plots, the
SC-004 timings, the research footnote hover) and `test_speed.py` (features 199-203's pointer-move and raster-CPU
caps on Kuwabata). Every xdist worker rolled its own Inashiro and Kuwabata and launched its own Chromium, so the
package cost 3.9 GiB at 8 workers in an 8 GiB container that had crashed twice; and a timing cap cannot say
whether a page FEELS slow. The ruling, in full, is in `conftest.py` and `l7r/diagram/interactive/CLAUDE.md`.
