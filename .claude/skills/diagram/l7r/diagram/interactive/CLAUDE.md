# interactive/ - the HTML target (feature 134)

The map as a page a player can use: hover a feature and every feature OF ITS KIND lights up; click
it and a modal says what it is, why it stands there, whether that is historically accurate, a
deliberate deviation or a guess (constitution XII), and which `research/` entries it rests on.
Written by `Settlement.finish()` beside the `.svg`, `.png` and `.json` of every Mode B map. The
GM's request, verbatim, and the spec: `specs/134-interactive-html-map/`.

**The SVG and the PNG are untouched** (spec FR-010). The class of a primitive rides in a SIDE LIST
beside the record streams (`Settlement.out_cls` etc., `core.py`), never in the SVG text, so the
PNG is byte-identical by construction; the page is a second serialization of the same strings.

| file | look here when |
|---|---|
| `tags.py` | you need the tag shapes: a `str` class, `Parts` (one string, several classes - a farmhouse and its shed), `Split` (one element, fill and stroke in different classes - a paddy and its bund), `"-"` (ruled not highlighted), `None` (nobody ruled) |
| `classes.py` | you are adding a KIND of feature, changing what a modal says, or adding a sibling distinction. The vocabulary is the spec's FR-007 table; every entry is written FROM a `research/` entry and carries its label; sibling text is per PAIR and symmetric; `NOT_HIGHLIGHTED_RULINGS` is the record of what was ruled out and by whom |
| `glossary.py` | you are adding a term the explanations use, or a definition reads wrong - every occurrence of a term in a modal is a hover tooltip; a test proves each term is used and each explanation's terms are defined |
| `sources.py` | a modal's references look wrong - they are READ FROM THE RECORD at page-write time: the class's research entry's `**Sources:**` keys and `research/SOURCES.md`'s citation text; the registry's own `sources` tuple is only the fallback |
| `page.py` - `merge_primitives` | the page draws too many elements, or a merge changed the picture. It gathers same-styled `<line>`/`<circle>`/`<ellipse>` into one `<path>` WHEREVER the reorder is invisible - an element joins an earlier bucket only if nothing it must pass overlaps it, and a TRANSLUCENT element never merges with one it overlaps (two blobs at 0.85 stack darker than one merged fill; that bug shipped with 134 and put every page 12-18% of pixels away from its own PNG - feature 148 R3). An extent it cannot compute counts as being in the way |
| `page.py` | `wrap()` (the HTML form of one stream string), `ink_census()` (the FR-009 data: elements per class, and the unclassed ones), `explanations()` (only present classes, only present siblings), `render_page()` / `write_html()` |
| `assets/page.css`, `assets/page.js` | the look and the behavior; inlined at write time. The highlight color is a recorded rendering decision (research.md R2) - change it there and here together |

## Tagging a new feature

At the emit site, either `with self.feature("<class key>"):` around the drawing, or `cls=` on the
one `add*()` call. A class key MUST be a row of `classes.py` - the gate check `all_ink_is_ruled_on`
fails a hamlet map on ink with no class and on a key the registry does not know. A feature the GM
rules NOT highlighted is tagged `"-"` and gets a row in `NOT_HIGHLIGHTED_RULINGS`.

A caption gets the class of the feature it names (`label(..., cls=...)`), which is all FR-006
needs: label and subject are one class, so hovering either lights both.

## Verifying

`tests/interactive/` - the registry (every entry complete, siblings closed and symmetric), the
page (wrap, census, self-containment, present-only data), and the browser test (Playwright +
Chromium, `rolls_map`: opens the reference hamlet's page from `file://` and drives hover, click and
the modal). `make map GEN=pool/hamlets/inashiro.gen.py` writes the real page; open it in a browser.
