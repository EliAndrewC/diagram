# Research: The Interactive HTML Map (feature 134)

Phase 0 of [`plan.md`](plan.md). R1 and R2 are engineering findings about the mechanism; R3 is the
constitution XII opening bookend - which `research/` entry each class explanation is drawn from,
with its label; R4 records the limitations accepted and the alternatives declined (root
`CLAUDE.md`, "Record a decision to ACCEPT a limitation").

## R1. Where the class rides - a side list, not the SVG (FR-010)

**Question**: how does an SVG primitive learn which feature class it belongs to without changing
the SVG?

**Measured**: Inashiro's SVG is 16,379,741 bytes and ~175,000 elements (11,921 circles, 160,059
lines, 1,419 polygons, 861 ellipses, 227 groups, 171 rects, 67 paths, 4 texts), emitted by ~250
`self.add*()` call sites across 40 engine files. But the unit of emission is far coarser than the
element: a whole bead run (~12,000 circles) is ONE `add()` string, a dry plot's furrows are one,
a tree stand's crowns are one. So the number of `add()` calls per map is in the low thousands,
and tagging the CALL, not the element, is both sufficient and cheap.

**Decision**: the four record streams take `cls`, kept in parallel lists aligned with the string
lists; `finish()` writes the SVG from the string lists exactly as before. The class never enters
the SVG text, so the PNG is byte-identical by construction (SC-005). The deferred ground and water
blocks carry `cls` on their entries and the splice builds a class block beside the string block.

**Declined**: (a) `class="..."` attributes in the SVG itself - would change the SVG and every
stamp, and resvg would carry the attributes for nothing; (b) reconstructing classes from the
manifest by hit-testing coordinates in the browser - fragile (the manifest records extents and
centers, not paint), and it would make the page depend on a geometry library it cannot load
(FR-001, no external asset); (c) a second, parallel emit API - two ways to draw one thing.

## R2. The highlight mechanism, and the 100 ms budget (SC-004)

**Question**: can a browser highlight "all farmhouses" on a 175,000-element inline SVG inside
100 ms, from a `file://` open?

**Options priced**:

| mechanism | cost | verdict |
|---|---|---|
| a state attribute on the `<svg>` root + descendant selectors (`svg[data-hl=X] .f-X *`) | one attribute change triggers a style recalculation over the entire tree; on a 175k-element tree Chromium's recalc is tens to hundreds of ms | declined - it is the whole-tree restyle that SC-004 cannot afford |
| `filter: drop-shadow(...)` on the highlighted groups | filters rasterize each group to a bitmap; a group of 12,000 circles is re-rasterized on every hover | declined |
| toggle a class on each group of the hovered class (JS: `for g of index[cls] g.classList.add('on')`) with a flat descendant rule `.f.on, .f.on * { fill; stroke }` | restyle limited to the affected subtrees - a few hundred groups; no filter, no bitmap | **chosen**; measured on Inashiro in the browser test (T-measure) and the number recorded in `tasks.md` |

**Measured (2026-08-27, headless Chromium 151, the 16 MB Inashiro page from `file://`)**: 1,777
class groups across 31 classes; load 2.1 s; the highlight toggle 0.2-2.3 ms of script time per
class (`bund`, 627 groups, the slowest) - two orders of magnitude inside SC-004's 100 ms. The unit
of grouping is the `add()` string, so a bead run of ~12,000 circles is ONE group and the furrows
of one plot are one; that is why the count is 1,777 and not 175,000.

**Highlight color - a rendering decision of the HTML target, class DEVIATION**: the map's palette
records the ground as parchment, rice as pale green, beans as pine, water as blue; the highlight
paints the hovered class a saturated warm gold (`#FFC83D`) with a dark-goldenrod stroke
(`#B8860B`). It is a UI affordance, not a claim about the world, and the modal says nothing about
it; it is a deviation from the palette by design, chosen for legibility against every fill on the
map (FR-003). Recorded here and in `interactive/assets/page.css` at the rule. **The fill rule
skips elements drawn with `fill="none"`**: a paddy's bund is the polygon's STROKE copy, and
painting its empty body gold would flood the paddies whenever the bund was hovered - the first
draft did exactly that, and the fix (`:not([fill="none"])`) is the reason the bund highlights as a
gold line and the beans as gold beads over a paddy that keeps its green.

**Hit targets**: a bean is a circle of r = 1.4 units; at fit the map draws at roughly 0.5 px per
unit, so a bean is ~1.5 px across - hard to hover deliberately at fit, easy zoomed in. The page's
own zoom (FR-013, added 2026-08-28 at the GM's request) makes this a non-issue: at 16x a bean is
~20 px across.

**The explanation dialog is NOT modal (measured 2026-08-28).** `dialog.showModal()` makes the rest
of the document inert, and on the reference page Chromium re-styled all ~175,000 elements on every
open and close: 1.1 s and +50 MB per cycle (five cycles: 894 -> 1,149 MB RSS), which crashed the
renderer under the browser test's 31 cycles on a machine with ~3.4 GB free. Five CSS variants of
the zoom stage (no overflow clip, no absolute SVG, no fixed nav, `contain: strict`, `will-change`)
changed nothing - it was the modal, not the stage. A non-modal `dialog.show()` over the page's own
shade: 0.3 s and +1 MB per cycle. Escape, the shade and the close button close it; the keys the
zoom uses are ignored while it is open.

**Zoom is a LAYOUT, not a transform (measured 2026-08-28).** The first draft zoomed by
`transform: translate() scale()` on the `<svg>`; Chromium rasterizes a transformed SVG as one
layer at its scaled size, which at 16x on Inashiro is a ~28,000 px square texture. Resizing the
SVG's width and height instead paints it per visible tile like any document; pan and zoom stay
composites of the viewport.

## R3. Where each explanation comes from - the opening bookend (constitution XII, FR-008)

This feature draws nothing; it states. Each class explanation is written FROM the entry below and
carries that entry's label; where the record is silent the class is labeled **guess** and the text
says so. The closing bookend (plan task T-close) reads each explanation on the rendered page
against its entry.

| class | drawn from | label |
|---|---|---|
| farmhouse | `research/homesteads.md` "What stood on a farmstead - the inventory, with numbers"; "How close does a farmhouse stand to the paddy"; `homesteads.md` groves entry for the yashikirin | accurate |
| storage shed | `homesteads.md` "What stood on a farmstead" (the naya / kura inventory - `sugiura-1973-fuzoku`) | accurate |
| byre | `homesteads.md` "May a byre stand beside a wellhead?"; `settlements/homesteads.md` byre form knob (`byre_form`) | accurate |
| threshing yard | `homesteads.md` "The threshing yard's sun, and how far a farmhouse shades" | accurate |
| garden | `homesteads.md` "The garden's sun, and how far the windbreak shades" | accurate |
| privy, woodpile, manure heap, bathhouse, hen coop, household shrine, persimmon | `homesteads.md` "The farmstead's fixtures" (T53-T59; per-fixture READ / SUMMARY-ONLY verdicts inline) - the sizes are stated there as GUESSES unless a source is named | accurate for presence and seat; **guess** for size, said so per fixture |
| homestead bamboo, shared bamboo grove | `research/vegetation.md` "Bamboo: how common, where it stood, and how to show it" (the household-vs-common distinction; the drawn stand is a legibility glyph) | accurate for presence; **deviation** for the drawn size (a culm cannot be drawn at true scale) |
| windbreak | `vegetation.md` "The fengshui forest - real scale, and why ours is honest"; `homesteads.md` "The garden's sun, and how far the windbreak shades"; `archetypes.md` "Why dike willows do NOT replace the village windbreak" | accurate |
| copse | `vegetation.md` "How is a coppice lot bounded?"; "Does scrub stand under a village wood?" | accurate |
| woodland commons | `vegetation.md` "How is a coppice lot bounded?" (the iriai commons); "Forest density and crown size" | accurate |
| scrub and rough grazing | `vegetation.md` "The crop margin"; "Scrub stays off open water"; "The cut bank" | accurate |
| marsh | `research/water.md` "Marsh - wet rice is reclaimed FROM wetland"; "The wet toe is as wide as the FAN"; `vegetation.md` "The marsh margin" | accurate |
| paddy | `research/fields.md` "Paddy plots - irregular patchwork, and why the grid is anachronistic"; "Nitrogen - a flooded paddy makes its own"; "Plot sizes" | accurate |
| bund | `fields.md` "Bunds are SHARED, and the fabric is continuous"; "A bund runs on, or it turns for a reason"; `water.md` "The bund runs along the channel bank" | accurate |
| bund beans | `waterfields/palette.py` `BEAN_GREEN` comment (azemame); `fields.md` bund entries - the practice is attested, the drawn color is a legibility departure ("real soybean foliage is lighter") | accurate for the practice; **deviation** for the color, said so |
| millet, buckwheat, barley | `fields.md` "Where dry (hatake) crops go - the topographic catena"; "Why ruled rows waited for Meiji" (the furrows) | accurate for placement; the crop MIX per map is a rolled knob - **guess** for the proportions, said so |
| fallow | `fields.md` (fallow patches; `fallow` pattern) - the record here is thin | **guess**, said so |
| stream | `water.md` "Water-width ladder - the real-world tiers"; "Drawn width is RANK, not discharge" | accurate for the type; **deviation** for width (rank, not discharge - the GM's ruling), said so |
| field ditch | `water.md` "The comb net is drawn at TRUE SIZE"; "Where the drawn net STOPS"; "The head-race forks"; "Irrigation topology" | accurate |
| pond | `fields.md` "Water-first v2 - pond, distribution and the three layout modes"; `SOURCES.md` `kagawa-tameike` | accurate |
| village lane | `homesteads.md` "Is every farmhouse reached by a lane, and in what FORM?"; "How does a village lane bend?"; the width note in `SOURCES.md` re-sourcing queue (no numeric source - the widths are drawing conventions) | accurate for form; **guess** for width, said so; the connector's provenance (predates the settlement) from `dev/placement.md` |
| footbridge | `water.md` "What drawing at TRUE SIZE left open" (footplanks); the spec template's own worked example names the footplank rule a GM-ruled guess | **guess**, said so |
| well | `research/urban-features.md` "Wells - the research, and the deliberate liberty"; "Communal wells and the samurai exception"; `homesteads.md` "Does a DISPERSED hamlet's outlying farm have its own well?" | accurate for presence; **deviation** for the drawn size (the oversized well for legibility - the constitution's own example) |
| notice board | `urban-features.md` "The notice board (kosatsuba) - siting is a TRAFFIC decision" | accurate |

**Sibling text** (FR-005) is written from the same entries: windbreak vs. copse vs. woodland
commons from the vegetation entries (purpose - shelter vs. fuel and timber vs. the commons' shared
take; regulation - a planted belt kept by the households it shelters vs. the coppice cycle vs.
iriai rules; use); the dry crops from the catena entry; beans vs. bund from the bund entries;
household vs. shared bamboo from the bamboo entry; storage vs. animals from the inventory entry.
Where an entry does not actually make the distinction the text is labeled guess.

**No new historical research is opened by this feature.** Every explanation is a reading of an
existing entry; a class whose entry proves thinner than the table above claims is written as a
guess, not researched further under this feature (the GM's scope is the page, and a thin entry
is a finding for the record, listed in `tasks.md` at the closing bookend).

## R4. Accepted limitations, and the alternatives declined

| accepted | costs | alternatives priced | who chose |
|---|---|---|---|
| tiny hit targets at 100% zoom (a bean is ~1.5 px; a furrow line ~0.4 px wide) | a reader must zoom the browser to hover a bean deliberately; hovering a bund between beans is easy | (a) invisible hit halos around small marks - doubles the element count on the heaviest classes and is exactly the whole-tree cost R2 avoids; (b) `pointer-events: stroke` with a fat transparent stroke - changes what the SVG-derived page draws vs. the PNG; (c) our own pan/zoom - not asked for | the session, under the plan; the GM may reopen |
| ~~no pan/zoom of our own~~ SUPERSEDED 2026-08-28: the GM asked for zoom (spec FR-013) - fit as the minimum and initial view, 16x fit as the maximum (the GM's own words leave the maximum open; recorded as a judgment) | - | - | the GM |
| one explanation per class, not per map | a map with an unusual instance of a class gets the general text | per-map text - not asked for; the request asks that the text reference the distinction between kinds, which the sibling paragraphs do | the spec (Assumptions), confirmed by the fidelity review |
| the hamlet vocabulary only | a town's page would report its unclassed ink through FR-009 until the town vocabulary is written | writing every tier's vocabulary now - the GM said "start with the reference hamlet" | the spec |

## R5. Performance: where the elements are, and why the fix is a merge, not raster layers (GM 2026-08-28)

**The GM's question**: every blade and crown is its own element - *"many, many thousands"* - and
the GM proposed prerendered raster layers per class (a normal and a highlighted image each, swapped
on hover, every layer the full map's size with transparency), asking whether that was the best way.

**Measured first (headless Chromium, 1400 x 1000, the real Inashiro page)**: 292,186 elements, of
which the scrub scatter is 225,163 and the marsh 57,089 - 97% in two classes, one `<line>` per
blade. Costs: load 2.4 s; a scroll frame 200-270 ms until Chromium's tiles were cached, then 32 ms;
a zoom step 100-300 ms; highlighting the scrub 553 ms (a restyle of 225k elements) and the marsh
566 ms.

**Raster layers, priced**: 37 classes x 2 images. A layer must be drawn at the resolution the zoom
reaches or the zoom blurs: at 16x the map is ~46,000 px square - 8 GB of RGBA per layer; at 4x
~540 MB per layer decoded, x 74 layers. At any size that fits in memory the 16x zoom the GM asked
for two hours earlier turns to mush, and hit-testing (which class is under the pointer) has to be
rebuilt from per-layer alpha reads instead of the SVG's own. The idea is the right one for a game
engine drawing at one scale; it fights the zoom here.

**What was built instead**: `page.merge_primitives` - a run of consecutive `<line>`s (or
`<circle>`s) whose attributes other than their coordinates are identical becomes ONE `<path>` with
those attributes and a `d` of M/L (or arc) segments. Same ink, one element per run instead of
thousands, vector, crisp at 16x, hit-tested by the class group as before. HTML target only - the
SVG and PNG never see it (FR-010).

**Measured after**: 11,682 elements (25x fewer); page 16.4 -> 8.9 MB; load 0.4 s; first scroll
frame 58 ms then 29; zoom step 46-113 ms; the scrub highlight 39 ms (14x). Look: 162 of 1,400,000
pixels differ by more than 8/255 at 4x zoom - anti-aliasing at path joins, nothing a reader sees.

**Left on the table, if the GM wants more**: the remaining ~11k elements are the crowns of the
woods and belt (different radii and two-tone conifers, so a run breaks every crown) and the plots;
a next step would merge circles with differing radii into one path (arcs carry their own radius)
and, only if still needed, rasterize the two ground-cover classes at the PNG's resolution as a
background with the vector glyphs above - the hybrid form of the GM's proposal.
