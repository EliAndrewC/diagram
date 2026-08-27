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

**Highlight color - a rendering decision of the HTML target, class DEVIATION**: the map's palette
records the ground as parchment, rice as pale green, beans as pine, water as blue; the highlight
paints the hovered class a saturated warm gold (`#FFC83D`) with a dark amber stroke (`#7A4E00`).
It is a UI affordance, not a claim about the world, and the modal says nothing about it; it is a
deviation from the palette by design, chosen for legibility against every fill on the map
(FR-003). Recorded here and in `interactive/assets/page.css` at the rule.

**Hit targets**: a bean is a circle of r = 1.4 units; at page width the map draws at roughly 0.5
px per unit, so a bean is ~1.5 px across. Hovering one deliberately is hard at 100% zoom, and easy
at 300% (the browser's own zoom scales inline SVG losslessly). Recorded as an accepted limitation
in R4.

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
| no pan/zoom of our own | the browser's zoom is the zoom | a zoom widget - not asked for; the GM's request is hover, highlight, click, modal | the session; literal scope |
| one explanation per class, not per map | a map with an unusual instance of a class gets the general text | per-map text - not asked for; the request asks that the text reference the distinction between kinds, which the sibling paragraphs do | the spec (Assumptions), confirmed by the fidelity review |
| the hamlet vocabulary only | a town's page would report its unclassed ink through FR-009 until the town vocabulary is written | writing every tier's vocabulary now - the GM said "start with the reference hamlet" | the spec |
