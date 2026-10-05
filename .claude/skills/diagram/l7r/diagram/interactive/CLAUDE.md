# interactive/ - the HTML target (feature 134)

The map as a page a player can use: hover a feature and every feature OF ITS KIND lights up; click
it and a modal opens on its TABS (feature 319, GM 2026-10-03): **About** - what the thing was, written to the guidelines in
`dev/modals.md` (a deviation told where it applies); **Guesses** - a bulleted list of what this
project guessed, absent when nothing was; **Depiction** - how the map draws it, its conventions and the "how our maps draw
it" pages (plan D13); **References** - the QUESTIONS the research asked that the write-up rests on, each
linking to its answer, since feature 301 the question's own small page in the record's built site, `research/site/` (feature
180; local since feature 194 - see below). **Every tab is the same size** (GM 2026-10-03: *"it is disorienting to see it resized when clicking between tabs"*): the panels share one grid cell and a hidden one is invisible, not removed (`page.css` `#x-panels`), and the browser test pins the dialog's box across tabs.
Written by `Settlement.finish()` beside the `.svg`, `.png` and `.json` of every Mode B map. The
GM's request, verbatim, and the spec: `specs/134-interactive-html-map/`.

**The SVG and the PNG are untouched** (spec FR-010). The class of a primitive rides in a SIDE LIST
beside the record streams (`Settlement.out_cls` etc., `core.py`), never in the SVG text, so the
PNG is byte-identical by construction; the page is a second serialization of the same strings.

| file | look here when |
|---|---|
| `tags.py` | you need the tag shapes: a `str` class, `Parts` (one string, several classes - a farmhouse and its shed), `Split` (one element, fill and stroke in different classes - a paddy and its bund), `"-"` (ruled not highlighted), `None` (nobody ruled) |
| [`classes/`](classes/CLAUDE.md) | you are adding a KIND of feature (a class in its family module), changing what a modal SAYS (its FILE, `assets/modals/<hamlet|sheet>/<kind>.md`, in the About form since feature 319; an edit owes `make page-check`, not the gate), or adding a sibling distinction (`siblings.py`). The vocabulary is the spec's FR-007 table; every entry is written FROM a `research/` entry; `NOT_HIGHLIGHTED_RULINGS` is the record of what was ruled out and by whom, and `NOT_HIGHLIGHTED_OVERTURNED` of what was ruled out and later let back in (`_base.py`) |
| `notes.py` | a fact you wrote into a map's `.notes.md` is not reaching its page, or you are adding a key the block understands. The reader has no error path ON PURPOSE - see below |
| `place.py` and `assets/place.json` | the title card says something wrong, or you are describing a new tier. The per-tier text, the crop table and the basis the card owes its reader are the JSON (feature 207); the sentence builders and the demographic constants are the module |
| `assets/glossary/NNNN-<term>.json`, one file per term (feature 259) - never the assembled `assets/glossary.json` (about 420 KB, written by `make glossary`, loaded by `glossary.py`; find a word with a grep of `research/assets/glossary-variants.txt`) | you are adding a term the explanations use, or a definition reads wrong - every occurrence of a term in a modal is a hover tooltip; a test proves each term is used and each explanation's terms are defined. A content edit owes `make page-check`, not the gate (feature 207). **It is the research record's glossary too** (feature 209, GM 2026-09-07: the same tooltip rules on the research pages): `record_glossary_js()` is the derived asset `research/assets/glossary.js`, written by `make glossary`, that `research/assets/record.js` wraps over every page's visible text; a term may live in the record alone, and `tests/interactive/test_record_format.py` proves the asset is in sync and every term used somewhere |
| `content.py` and `assets/*.json` | you are wondering WHY the page's prose is JSON rather than Python constants - the why is in `content.py`'s docstring (feature 207: a wording edit must not be an engine change). `glossary.json`, `siblings.json`, `place.json`, `page-text.json`; the registry's data went into its modal files (`assets/modals/`) |
| `citations.py` | the WORKS a question's notes cite (feature 211, GM 2026-09-07; its per-page citations pages retired with the page directories, feature 303): the works block at the foot of each question's page of the site, derived from the registry's two write-ups per work (citation line; what it is; why it applies, and its limits), and the footnote classifier (`footnote_form`) the gate and `make footnote-census` share. The site carries each question's notes at its own foot (`record/site_notes.py`). Look here when a works list is wrong or a new key is refused for want of a write-up |
| `sources.py` | a modal's references look wrong - they are READ FROM THE RECORD at page-write time: `research_questions()` resolves the class's `entry` - since feature 301 a list of FRAGMENT paths (`entry_fragments`) - to the questions it names, each linking its small page in the record's site (`SITE_PAGES + q/<heading id>.html`, flat whatever section the question is in - feature 303); `research_sources()` / `registry()` read the keys a question's footnotes cite and the registry. `record_text()` is THE reader of a page of the record - the registry assembled, a question's page with its cross-link and confusables written in - because nothing built is committed (every reader in the engine, the tools and the tests asks it). It also holds the ONE body of feature 190's link classifier (`citation_lines`, `not_read`, `link_target`) and `registry_entries()` |
| `page.py` - `merge_primitives` | the page draws too many elements, or a merge changed the picture. It gathers same-styled `<line>`/`<circle>`/`<ellipse>` into one `<path>` WHEREVER the reorder is invisible - an element joins an earlier bucket only if nothing it must pass overlaps it, and neither a TRANSLUCENT nor an OUTLINED element merges with one it overlaps (0.85 blobs stack darker than one merged fill - feature 148 R3; and a path paints every subpath fill before its stroke, so merged crowns show each other's outlines - feature 153 R5). A line has no fill and so is never outlined - getting that wrong un-merges every scatter. An extent it cannot compute counts as being in the way, and a circle's is tested as a circle. **A merged scatter is written as ONE PATH PER 400 px CELL, not one path** (feature 199, GM 2026-09-07: Kuwabata's page "a lot more noticeably sluggish"): a bucket of `TILE_MIN` (200) or more members is split by the cell of each member's anchor at emit time - Chromium replays every display item whose box touches a screen tile, and one 87,000-subpath path whose box spans the map was replayed for every tile on every hover; measured 57 ms per pointer move on Kuwabata's opening view against 17 tiled, 99-129 ms on Kashikawa and Sawada zoomed (`specs/199` research.md R1-R3). Which elements join a bucket is untouched, so the picture is unchanged (0-17 px of 1.4 M, R4). The guards it shipped with - every 200+-subpath path on the reference page in one cell, Kuwabata's mean pointer-move cost under 40 ms (on the MEAN, because the cost lands on the one move in five that crosses into the scrub and the median cannot see it, R6) - were RETIRED by the GM on 2026-09-07 with every browser test over a rolled page ("Verifying", below); the measurements stand in `specs/199` research.md |
| `page.py` | `wrap()` (the HTML form of one stream string), `ink_census()` (the FR-009 data: elements per class, and the unclassed ones), `explanations()` (only present classes, only present siblings), `render_page()` / `write_html()` |
| `raster.py` | **the page is TWO MODES** (feature 200, GM 2026-09-07: *"all of the above feel slow"* - hover, scroll, zoom, load, in Chrome). Below a screen scale (`RASTER_R` = 3 px per map px, against `view.s x devicePixelRatio`) the map is ONE IMAGE of the whole picture, rendered here by resvg - the PNG's own renderer - as lossless WebP, and every class group is hidden except the lit one, drawn as vector above it; above the scale the page is feature 199's vector page. The pointer in raster mode is answered from the CLASS ID MAP: the same SVG recolored one flat color per class, hit geometry painted as the DOM hits it, opacities stripped, no anti-aliasing, read from a canvas (`page.js` `keyAtPoint`; 98.2% agreement with the DOM, the rest single-pixel edges). And the OFF-MAP INK is dropped first (`drop_offmap`): 90% of a hamlet page's subpaths lay outside the viewBox - the hinterland scatter the crop never shows - and dropping them is what holds the first load near today's once the image's decode is added (0.36 s today, 0.83 kept, 0.58 dropped). The page paints the vector first and switches when both images are decoded. **Feature 201** (GM 2026-09-07): the picture carries NO TEXT (`without_text`) and raster mode hides LEAF INK outside the lit group rather than class groups, so every `<text>` is the browser's in both modes (one scale, one placard name in one font); and a lit class's filled shapes are a 0.45 WASH over the image, so the bunds, beans and ponds beneath a lit paddy show through - the exact stacking was priced at 223 ms per paddy hover and a mask at 300-1,100 ms (`specs/201` research.md R2, R3). **Feature 245** (GM 2026-09-13: *"the bund beans don't visible light up when highlighted while zoomed out"*): the lit BEADS take no wash - a fill-only mark a few screen pixels across under a 0.45 gold wash is an olive dot the eye never reads as lit (measured, `specs/245` research.md R1) - named by class in the stylesheet after the wash rule, and a second class measured the same way is added there. **Feature 203**: the PLACARD is the one thing never hidden in raster mode - its card and name (`place`) and its scale bar (`g.scale`, a marker `finish.py` sets; still not highlighted) stay vector in both modes, drawn last, because a lit class beneath the card (the scrub has blades under it) was painting over the image's card. Look here when: the raster looks wrong (the render), a hover in raster mode names the wrong class (the id map), a mark near the map's edge is missing (the margin), or a page has no raster at all (resvg absent - `r: 0`, the page never leaves vector mode). Numbers and the priced alternatives: `specs/200-raster-mode-below-the-vector/research.md`. **Feature 208 (GM 2026-09-07: *"a whole lot of rasterizing that is completely pointless and not actually needed for the tests"*): the raster is a RENDER** - `finish()` passes the PNG's own condition (`render` and no `DIAGRAM_SKIP_RENDER`) as `with_raster`, so a test roll writes the vector-only page (`"r": 0`) and never pays the picture: measured, one test roll's page write went from 9.2 s and a 598 MB peak to 1.6 s and 153 MB. And when the picture IS made, `webp_lossless` runs PIL's decode and libwebp's encode in a child Python (`_WEBP_CHILD`, PIL only): the 400 MB of C buffers live and die there, the parent rests where the roll left it (125 MB against the roll's 121), and `malloc_trim` was not needed. The generation cache treats a skip-render page as it treats a skip-render PNG. Bytes unchanged: Kuwabata's payload through `make map` is identical before and after |
| `assets/page.css`, `assets/page.js` | the look and the behavior; inlined at write time. The highlight color is a recorded rendering decision (research.md R2) - change it there and here together. **The cursor** (GM 2026-09-26): the link hand over every clickable kind, the arrow over bare ground and over the broad kinds listed in `page-text.json` `plain_cursor` (grassland, marsh, both paddies, copse, windbreak, woodland commons - `page.py` `PLAIN_CURSOR`, carried per class as `plain`); `page.js` `cursorFor` sets it from the key under the pointer, so raster mode's id map drives it too |

## A hand-drawn sheet's page (feature 262)

The GM, 2026-09-26, asking for clickable magistracy maps: *"the main important thing is that the labels and the
features on the building diagram for each magistracy have a common source, such that changing that source in one
place is enough to change it downstream."* A Mode A sheet has no generator to hand the page its (string, class)
pairs, so they are read back out of the drawing:

| file | look here when |
|---|---|
| `sheet.py` | a magistracy page lights the wrong thing, or the census names ink with no kind. Every element or group carries `data-kind="<key>"` (the nearest one wins; `"-"` rules it out); the reader tokenizes the sheet (never an XML round trip - the page carries the sheet's own bytes) and re-opens a group's opening tag around each differently-tagged piece, so a transform or inherited fill still applies. `element_kinds` is what the pack audit reads to find a program item by its tag |
| [`compound_kinds/`](compound_kinds/__init__.py) | a magistracy modal says something wrong, or a new kind is drawn. The hamlet form exactly (one About-form file per kind under `assets/modals/sheet/`), a SEPARATE registry (`COMPOUND_CLASSES`, passed as `render_page(registry=)`) because a compound's well is written about a compound. Every kind is written from an existing finding; a kind no research section covers says `(no dedicated entry - recorded as silent)` and so lists no references - the gap the GM can see. The magistracies program in `buildings/types.json` names these kinds and states no class or why of its own: `programs.md` and the audit read the kind's guesses (`buildings.types.classification`) |

**A part is its own kind and lights with its parent** (feature 264, GM 2026-09-27: *"individual features inside of
buildings or other features to get their own individual highlighting"*). A hearth, a pond, a genkan, a labeled room,
a door carries its own `data-kind` inside its parent's group; `sheet.pieces()` hands the page, beside each fragment's
kind, the kinds it is part of (its tagged ancestors, plus `data-part-of="<kind>"` on a part drawn elsewhere for paint
order), `render_page(within=)` writes them as `data-in` AFTER `data-k` (the id map's `_GROUP` pattern reads `class`
then `data-k`), and `page.js` files the part under its parents too, so the kitchen lights its hearth and the hearth
lights no kitchen. A room is drawn as its own floor - the building's fill, one same-color rect per room, then the
outline with `fill="none"` (0 px changed) - and the pack audit folds such a rect into its building
(`pack_audit/parse.py` `rooms_folded`). The id map holds past 63 kinds on one page (green counts the rows,
`raster.palette_rgb`), and a sheet page's id map draws text unblended (`crisp_text`, set when `within=` is given),
so a label never answers as its neighbor in the palette; hamlet id maps are untouched.

Each pool magistracy's `.gen.py` calls `write_sheet_page(svg, COMPOUND_CLASSES)` after its PNG and fails if the census
is not clean; the placer's `emit_svg` writes the kinds itself (`BuildingSpec.feature`). A map's own facts go in its
notes' "Map notes / Features" block keyed by kind, as for a hamlet. `tests/interactive/test_compound_kinds.py` holds
every sheet complete, the registry closed over the five maps, and the GM's two examples (the threshold stones say
they are the setting's; the hearing court lists its questions).

## No class-level label, lead or caveat (features 156, 183, 319)

The page never tells a reader that a feature is historically accurate. The GM, 2026-08-29: *"I want the presumption to be
that things are always historically accurate unless stated otherwise. In other words, we should call out liberties that we
have taken."* Feature 319 retired the label lead ("This is a guess - ...", "Note: we have rendered ...") and the caveat with
the old `What:`/`Why:`/`Note:`/`Caveat:` form: the classification is per statement in the About text (`dev/modals.md`
M11-M13) - a guess is a bullet on the Guesses tab, a deviation (the SETTING differing from history) is said in About where it
applies, and a map drawing convention (a glyph scaled or colored for the eye - the GM's line, feature 183) is told on the
Depiction tab with its real counterpart. Don't re-add a lead: a "This is a guess" opening on a modal that is mostly record read
as the whole modal being a guess (the GM, 2026-10-03: *"extremely misleading"*). The title card keeps its own basis line
(`place.BASIS_LEAD`, `x-basis`), which says where the card's claims come from.

## The references are QUESTIONS, not sources (feature 180)

The References tab of the one dialog (feature 319) lists the questions the write-up rests on - `dev/modals.md` M14, held by
`modal-research`. The GM, 2026-09-05: *"instead of listing individual sources on the references modal, we will list the
questions which we asked and researched - those pages are themselves sourced with links, so a user who wants to follow
through and read the original sources can do so."* The audience is a casual RPG enthusiast, and *"they are not immediately
presented with an overwhelming amount of third party sources."* The sensibility is `research/CLAUDE.md`, "Who the record is
for"; this section is the mechanics.

| on the page | where it comes from |
|---|---|
| NO `Record: research/...` line (the GM: *"I don't think we need lines like [that] on our main modal"*) | `FeatureClass.entry` stays in the registry as the record |
| the References tab, hidden when the entry resolves to none | `page.js` `open()`, off `d.questions` |
| one link per question, no lead-in line (retired 2026-10-05: the GM, *"the links are self-explanatory"*), opening in a new tab | `sources.research_questions(entry)` - the questions the entry's FRAGMENT paths name (feature 301), in the ENTRY's order (the author's primary question first), text = heading less its dated `(researched ...)` parenthetical, URL = `SITE_PAGES + "q/<heading id>.html"` |

**The anchor rule is GitHub's, reproduced** (`github_anchor`): lowercase, drop everything but letters,
digits, combining marks, spaces, hyphens and underscores, spaces to hyphens (so ` - ` is `---`), and a
repeated heading in one file numbered `-1`, `-2` in order of appearance - counted over EVERY heading
level and outside code fences, as GitHub counts. Checked against the live site on seven headings before
it shipped (spec D7) and pinned by `test_page.py`, so a divergence fails a test that states the expected
string. The heading id is also the slug of the question's file (`NNNN-<heading id>.html`, feature 303) and its small page's file name (feature 301): a
renamed heading moves all three, which `make fragment-move` does with every pointer to it, and every pool page
re-renders at each landing so its links follow.

**A class naming a question nobody can find shows no link and no error** - `research_questions` is quiet
like everything else here, and `scripts/check-entry-headings.py` is what refuses it at the push. So when you add a class, open its page and click its References tab once.

## The blue plot is its own class (feature 159)

A paddy plot drawn with the FLOODED fill (`#93B7AC`) carries `wet paddy`, not `paddy`. The GM,
2026-08-29: *"that is its own type of thing, and it deserves its own explanation."* It is the
**shitsuden** - ground too poorly drained to dry out, which holds water even out of season, takes no
winter crop and yields unreliably - against the **kanden**, the paddy that empties to a dry field.
The research is `research/questions/0007-wet-paddies-that-never-drain-shitsuden.html`.

Decided at ONE emit site, `settlement/fields/comb.py` `_comb_draw_paddies`, from the fill about to be
drawn, so the class and the color cannot disagree. Every field engine reaches that site, so every
tint rule gets the class.

**THERE ARE TWO TINT RULES, and the shared explanation must be true under both.** This is the thing
to know before editing the class's prose:

| engine | rule | measured |
|---|---|---|
| comb (`waterfields/carve.py:356`) | a random 45% of the closing rank - the plots on the drain collector - less the pointed slivers `carve.py:361` demotes back to green | inashiro 2/24, kashikawa 3/24, mizuguchi 2/20, sawada 0/19 |
| terrace and polder (`hill.py:75`, `hill.py:191`, `polder.py:328`) | every `low` plot, no sample | **kuwabata 5/5** (the only LIVE one); enokida 22/22, tanada 40/40, yatsuda 18/18 are frozen legacy exhibits and never re-roll |

So blue is a SAMPLE of the wet ground on a comb map and the WHOLE of it on the others, and the
modal's disclosure is written conditionally ("on a comb field...") for that reason. A flat "only a
sample" is false on kuwabata, which a reader can open today; a flat "the wet ground" is false on
the comb maps. The
`low` / `fill` split is the engine's own (`carve.py`: *"`low` is the TOPOGRAPHY; `fill` is only the
PICTURE"*), and the land-use overlays still key off `low`, never off the class.

## The map-notes block: facts a `.notes.md` hands its page (feature 156)

A settlement's own `<name>.notes.md` may carry a `## Map notes` section, and the page reads it.
Optional everywhere, and absent from most of the pool.

**Nothing from the GM-only notes of an Obsidian Portal record ever reaches a page** (the GM, 2026-09-28: *"magistracy
pages should not show GM only Obsidian portal notes. Not now and not ever. If I have notes that I want to be shown that
are in the GM only section, then I will move them somewhere else that is visible"*). A record's `game_master_info` is
not a source for a map note, a caption, a drawn particular or a kind's prose; its public `bio` and the canon
(`make canon`) are. Before a particular goes on a sheet, check which field holds it; one only the GM-only field holds
stays off - no inference that it is probably fine. The first audit (feature 267 follow-up) took the Fox-Fire Lantern,
the fox relics, Hayakawa's salt wards and several Ubame notes off their pages.

```markdown
## Map notes

### Place

- **district**: Hoshigaoka
- **district direction**: east
- **imperial road**: directly south
- **county**: Hayakawa
- **town**: Hayakawa
- **town direction**: further south, beyond the Imperial road
- **also**: anything else worth a sentence on the card

### Features

- **village lane**: A sentence true of THIS map's lanes, shown under "On this map".
- **windbreak**: ... any class key from `classes.py` works. That generality is the point
  (GM: "in general, the kind of thing that we want to be able to do for any kind of map feature").
```

`### Place` feeds the title card (`place.py`; `PLACE_KEYS` is what it understands, and an
unrecognized key is simply unused rather than wrong). `### Features` is keyed by CLASS KEY and
appears in that class's modal on that map only.

**The reader has no error path, and that is the requirement rather than a shortcut** (GM: *"we should
not presume that such sections exist and our code that parses the notes file to find these special
notes should be resilient against that formatting not being present, and should default to simply
not pulling anything in if the parsing fails"*). A missing file, a missing section, a bullet with no
colon, a nested list, a truncated line, a class key nobody knows - each contributes nothing, silently.
`read_map_notes()` cannot raise. The cost of that, accepted deliberately: a typo in a key produces
silence rather than a complaint, so check a new block by regenerating the map and opening its page.

**One default is synthesized rather than authored**: a hamlet's `village lane` with no annotation of
its own says where the lanes lead, naming the district's main village when the notes name the
district. A district takes its main village's name (`l7r.md`, "Place Names"), which is what makes the
one key enough - and it is why the class is a VILLAGE lane rather than a hamlet lane.

## Tagging a new feature

At the emit site, either `with self.feature("<class key>"):` around the drawing, or `cls=` on the
one `add*()` call. A class key MUST be a row of `classes.py` - `all_ink_is_ruled_on` (now
`tests/gate/test_map_vocabulary.py`)
fails a hamlet map on ink with no class and on a key the registry does not know. A feature the GM
rules NOT highlighted is tagged `"-"` and gets a row in `NOT_HIGHLIGHTED_RULINGS`.

A caption gets the class of the feature it names (`label(..., cls=...)`), which is all FR-006
needs: label and subject are one class, so hovering either lights both.

`place` is a RESERVED key rather than a row of `classes.py`: it tags the title placard and its name,
and its modal is built per map by `place.py` instead of being written once in the vocabulary. The
census and the ruling both know it, so the placard is highlightable and is never reported as
unruled ink. The scale bar beside it keeps `cls="-"`.

## Verifying

`tests/interactive/` - the registry (every entry complete, siblings closed and symmetric), the
page (wrap, census, self-containment, present-only data); and `tests/full/interactive/page_browser/`,
the browser test (Playwright + Chromium): a hand-built SYNTHETIC map of one element per class, opened from
`file://`, over which every behavior ruling is proved - hover, click, the modal's text against the
registry, zoom and scroll, the hit boxes, the glossary, the sibling links.
`make map GEN=pool/hamlets/inashiro/inashiro.gen.py` writes the real page; open it in a browser.

**NO BROWSER TEST LOADS A ROLLED PAGE, AND NONE TIMES ANYTHING (GM 2026-09-07).** Thirteen tests did - the
reference hamlet's mechanics and timings, the blue plots, the footnote hover, and features 199-203's
pointer-move and raster-CPU caps on Kuwabata - and were retired the day the container crashed twice under
the gate. Measured: the package alone peaked at 3.9 GiB at 8 workers (2.9 GiB of Chromium, 3.6 GiB of Python
writing eight Kuwabata rasters at once) against the container's 8 GiB cap, and its wall time was setup-bound
at 83 s whatever the worker count, because every worker rebuilt every module-scoped fixture. The GM:
*"the performance tests are never really going to be good enough to detect whether a human feels that the
page is too sluggish. that is fundamentally a matter of judgment and vibes. So while having that kind of
timing test was useful in speeding the page up, and while I would expect the future requests to speed the
pages up might implement a similar test as a temporary measure, we should avoid having browser based tests
which load the full pages and do things of this nature simply because it takes up too much RAM and CPU in
order to be worthwhile. the juice is not worth the squeeze."* So the rule: **a request to make a page faster
is measured BY HAND while it is worked** - open the page in a browser, take the numbers (the instruments are
recorded in `specs/199` and `specs/200` research.md: a Playwright pointer sweep on the MEAN, a DevTools
trace summing raster CPU), write them into that feature's research.md - and the measurement is retired with
the feature. **Never a repeatable test that runs at the gate, or even when the HTML content changes**: the
GM's words, *"that simply adds too much to the time that it takes to make small changes."* The synthetic
tests stay because they are cheap (one Chromium, a page of fifteen elements) and are the only record of
the page's behavior rulings.

**...AND THEY ARE SKIPPED WHILE NOTHING THEY READ CHANGED (feature 206, GM 2026-09-07: *"Do we have logic in
place to skip them if the content which they are testing has not changed? ... this is about saving memory,
not saving time"*).** `gate-stamp.py` keeps a `browser` key over everything the synthetic tests read - every
module here, the two assets, the test package, `research/*.html` (the References tab's links), and the
installed Playwright and Chromium - and the gate's test phase leaves the package out while the stamp matches,
saying so in one line. The stamp is earned only by a run that ran the package green: `make page-check`, or a
`make done` whose test phase included it. It is a skip key, never a push obligation: the push's `--check`
ignores it. Measured: what a gate saves is one Chromium at ~430 MB for under 9 s (the 3.9 GiB was the
retired rolled-page tests); the floor cannot be loosened by a skip (`specs/206` research.md R3).

**An edit to `assets/page.css` or `page.js` owes `make page-check`** (feature 188) - the interactive tests
and the browser test, about a minute, stamping the `page` area the push demands - and nothing else: no
spec-kit feature, no review, no full gate. The pages regenerate on landing (feature 187).
