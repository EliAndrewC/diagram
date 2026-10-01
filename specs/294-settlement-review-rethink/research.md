# Research - feature 294, rethinking the settlement review

## R0 - the ledger census (observed 2026-10-01)

Observed 2026-10-01; method: an Opus agent read every `settlement-review` row of `docs/review-ledger.md` (135 lines, 133 rows
after two `spec-fidelity` rows mislabeled) and classified each finding by hand, deduplicating rows that carry several. The spec's
R0 table is its summary. Approximate: about 260 agent runs; about 360 distinct findings - ~160 geometric (~117 since guaranteed
by feature 287's placer rules, ~45 still caught only by the reviewer, in the 14 classes FR-003 lists), ~70 judgment, ~110
paperwork, ~20 nothing or declined; ~100 author-missed-and-fixed (rows 1-79 only - the column is empty from 2026-09-27), of
which ~55 geometric, ~15 judgment, ~30 paperwork; ~36 runs NOT-REVIEWABLE. Cost per run from `specs/251-*/research.md`: 43
turns, 6.63 M input tokens. Wall time on 7 rows only (27.1 min total, 2026-08-26/27); tokens on none. FR-013 re-takes this as a
script (R4).

## R1 - the audit of the three map-review contracts (FR-001)

The table below is the audit User Story 1 asks for: every section, sweep, protocol step and validated example of
`settlement-review.md`, `building-review.md` and `size-audit.md`, with a verdict, the occasion or the test that replaces it, and
the ledger fire count. Drafted by an Opus agent; the session's rulings on the points it raised are R2, and the plan's
decisions (plan.md) settle each row's fate. Where a row and R2 disagree, R2 governs.

Observed 2026-10-01 in `/diagram/.clones/diagram-review` at a4db393bf. Method: every section, sweep, protocol step and
validated example of the three agent files read whole; ledger counts are a hand classification of the
`settlement-review` (135 lines), `building-review` (43 rows) and `size-audit` (5 rows) rows of `/diagram/docs/review-ledger.md`
by keyword grep plus reading each row's "found" column, so approximate (+-30%); several rows carry many findings. Coverage from
`specs/287-placer-guarantees/research.md` R12 (175 rules: 162 guaranteed, 11 recorded decisions, 2 gaps) and
`design/design-*.json`, `l7r/diagram/tools/pack_audit/registry.py` (the Mode A checks run by
`tests/test_mode_a_sheets.py::test_every_mode_a_sheet_passes_its_checks`), `tools/pack_audit/mapmatch.py` (feature 257), and
named tests under `.claude/skills/diagram/tests/`.

Verdicts: CUT / MOVED / STRUCK / TRIGGERED on <occasion> / WHOLE-MAP on <occasion> / PROCESS (survives | tooling | goes).
"L" = line in the agent file.

### settlement-review.md (Opus high; owed today for every pool map whose manifest moved)

| # | check | what it judges | verdict | occasion or replacing test/rule | ledger fires (~n) | note (figures observed 2026-10-01; method: the ledger rows named) |
|---|---|---|---|---|---|---|
| S1 | When to dispatch (L10-12) | the review's remit statement | PROCESS - rewrite | occasions from this audit (FR-005) | - | lists Mode A agreement, generic annotations: both struck |
| S2 | Tier pin (L18-24) | Opus/high pinned | PROCESS - survives per check | US8 re-tests per check | - | |
| S3 | Batch reads (L26-27) | one message per known lookups | PROCESS - survives | - | - | |
| S4 | Narrow job + "gate can see / you must see" table (L32-51) | the gate/judgment boundary | PROCESS - rewrite (FR-002) | rows 3, 5, 6 STRUCK; row 1 -> glyph check; row 2 CUT (woods W16-W19); row 4 -> cover check (C5) | - | cites `town_margins_clothed`, which survives only as a comment in `homestead_parts/keepouts.py:140` |
| S5 | WHEN YOU ARE DISPATCHED, feature 231 (L53-64) | owed when a manifest moved | PROCESS - goes | FR-005 retires the trigger | - | "review what moved" is the trigger US3 retires |
| S6 | FIRST STAGE 1 - paired gate alive (L76-79) | gate green before judging | PROCESS - tooling | US6: refused before dispatch | ~10 rows NOT-REVIEWABLE seen (R0: ~36 runs) | 269 B30/B42, 279 r2, 280 r2/r5, 293 r1 |
| S7 | FIRST STAGE 2 - record can bear the finding (L80-94) | measurement read the ink, not a proxy | PROCESS - tooling for existence; adequacy stays in the one verification round (FR-009) | `make review-paired-gate`, `_review_prereq` | ~3 (279 r2, 269 Kuwabata r3, 240 canopy) | the only first-stage item needing judgment |
| S8 | FIRST STAGE 3 - re-read gate before verdict (L95-101) | gate still green at the end | PROCESS - tooling (already: `make review-verdict` re-reads the gate) | - | 1 (280 r5, gate red mid-review) | drop from the contract |
| S9 | Measure independently (L103-106) | distrust handed numbers | PROCESS - survives | - | - | |
| S10 | Inputs; a missing notes file is a finding (L108-121) | inputs; notes exist | PROCESS survives; "notes missing" MOVED | existence test over every pool map (today only the five via `test_notes_census.py::test_the_pool_hamlets_all_carry_a_census_block`) | 0 | |
| S11 | Review the snapshot (L123-129) | use the pre-gate copies | PROCESS - survives as check input | `.git/review-snapshot/` | - | |
| S12 | Tooling: `page-lit`, `picture-diff` (L131-149) | measuring tools | PROCESS - `page-lit` goes with MOVED class 7; `picture-diff` kept only as a triggered check's input | FR-006 | - | picture-diff is a what-moved report |
| S13 | Tooling: `scatter-bases`; adjudicator retired (L151-169) | scatter parse | PROCESS - survives as input to the glyph/in-place check | feature 298 tiles leave keep-outs out by construction | - | |
| S14 | Scope FULL or DELTA (L171-199) | which sweeps run | PROCESS - goes | replaced by occasions; DELTA item 2 ("whatever the change MOVED") is the retired trigger; item 3 (caption ranking) is label -> STRUCK | - | |
| S15 | One map per agent (L201-209) | dispatch shape | PROCESS - survives (pair guard) | extends to one map per element (US3) | - | |
| S16 | Protocol 1 - read the scale (L213-217) | ft/px from manifest | PROCESS - survives (dispatch can pass it) | - | - | |
| S17 | Protocol 2a - PNG first; answer the GM's complaint at fit zoom first (L218-226) | did the GM's visual complaint go away | TRIGGERED on a fix to a GM-reported visual defect (the one verification round, FR-009) | - | ~4 (T12, 157 board caption, 228 dike, T54 marsh) | own occasion, not a glyph-check occasion |
| S18 | Protocol 2b - manifest-free pixel count "X inside Y" (L226-238) | glyph bases on the wrong ground | MOVED (ink-on-ground class: bases vs ground color, FR-003 classes 1/5) | the motivating case is CUT: woods W06, W03, W10 + feature 298 tiles | ~5 | the count is a script; nothing in it needs judgment |
| S19 | Protocol 3 - drawing matches docstring/notes/knobs (L239-241) | notes and knobs agree with drawing | MOVED | FR-004 (typed counts) + a new declared-knob-vs-drawn test; homes H32 guaranteed, H33/H34/H35 recorded decisions | ~45 (stale notes and typed counts, rolled-not-drawn kizuma/baths) | the largest class in the ledger |
| S20 | Protocol 4-5 - read manifest; enumerate sweeps (L242-244) | method | PROCESS - survives | - | - | |
| C1 | Glyph legibility and the mirror rule (L248-264) | mark reads as itself, not confusable, not a face | TRIGGERED on a glyph added, redrawn, or its placement rule substantially changed (US4) | the glyph check | ~22 (forge face, manure heap/bush, persimmon fruit, banana/fruit, cane/grass, grave face, drain vs supply ink x2, flooded plot as pond x2, mats as paving and rack as woodpile (282, 9 rounds), privy vs wood shed x2, coppice discs, belt bamboo, burial ground as ornament, cremation eye, fry fill, missing sluice glyph) | the highest-yield judgment check |
| C2a | FORM - windbreak belt not blob (L271-272) | belt long and narrow on a fringe | CUT (residual TRIGGERED with the glyph check on a new belt form/knob value) | woods W16 depth, W17 holes, W18 side, W19 shelters houses; `trim_receding_ends`, `settle_the_belt` | ~5 (227 0% cover, Sawada SW arm, 269 B30 rows x2, founding) | |
| C2b | FORM - quarter/warren fabric with grain (L273-274) | rows, lanes, frontage | TRIGGERED on a new tier (town/city generator) | - | 0 | no generator draws a quarter |
| C2c | FORM - channel widths are rank, not discharge (L275-280) | a do-not-report convention | PROCESS - travels with the glyph check for water inks | research/water "Drawn width is RANK" | 0 (prevents false findings) | |
| C2d | FORM - street blocks; field as water-ordered grain (L281-282) | fabric reads | streets TRIGGERED on a new tier; field CUT + TRIGGERED on a new field archetype | water W18-W25, W35 | ~3 (brick lattice knob, staircase walls) | |
| C2e | FORM - a precinct reads as one composed group (L283) | temple/shrine/market grounds composed | TRIGGERED on a new compound/precinct element or its placement rule (glyph check occasion) | - | ~4 (268 r1-r3, 272) | most 268 findings were ruled edges (C2g) |
| C2f | FORM - do not report belt BEARING (L284-289) | exclusion | PROCESS - goes | woods W18 (within 45 deg of NW) guarantees the side | 0 (1 false, Ubame, pre-ledger) | |
| C2g | (FORM sweep, as fired) ruled/plumb edges, staircases, spikes | non-natural edges | MOVED (FR-003 class 2); brook forms CUT | water W01-W04 (brook turn, level run, straight run, axis) | ~15 | |
| C3 | Agreement with a Mode A sheet of the same place (L291-311) | addressing face, gate direction, where the compound sits | STRUCK | 257 `matches_map` (registry, `test_every_mode_a_sheet_passes_its_checks`) | ~1 (founding: road through compound) + 1 confirmation (270 r2) | GAP: mapmatch compares positions and per-side footprint only, not gate direction or which face addresses the town, and only `hoshigaoka-shrine` declares `**On map**`; the five magistracies declare none |
| C4a | Annotations - instance-specific or generic (L315-317) | label wording | STRUCK | captions declared per element in code (286) | 0 | |
| C4b | Annotations - labels restating the drawing (L318-319) | label wording | STRUCK | 286 | 0 | |
| C4c | Annotations - only Imperial roads labeled (L320-321) | road captions | STRUCK | 286; no test asserts it -> give it one (a declared-caption test) or record it on the town/city tier | 0 | rule has no home today |
| C4d | Annotations - terms mean what they say (L322-324) | caption terms vs canon | STRUCK | 286; a triggered check on a new caption type if it slips (GM) | 0 | |
| C4e | Annotations - caption aligned with its subject (L325-344) | caption tilt | STRUCK | labels L8; `tests/labels/test_placer_287.py::test_a_caption_is_drawn_at_its_subjects_own_angle_through_every_fallback`; `linear_tilt` | 2 false (Inashiro 84.8, Sawada 80.9) + 1 (the contract carried a retired rule) | fired only wrongly |
| C4f | (Annotation sweep, as fired) caption collisions and association | caption on a roof, lane, crown, naming the wrong thing; title placard | STRUCK | caption placer 266/289, design-labels L1-L18 (18/18 guaranteed), L14 title, water W58 | ~14 | |
| C5 | Feature or slack (L346-355) | cover exists for a reason, not to pass a check | TRIGGERED on a cover/open-ground element added or its fill rule substantially changed (glyph-check occasion) | woods W11 (open ground <=35%), W13 (stocking) CUT the measurable half | ~4 (stocking 50% bare, copse of 2, copse of 5, belt crowns off-page) | |
| C6a | Nuisance siting on the right axis (L361-363) | smoke downwind, filth downstream | MOVED for the hamlet privy/heap (FR-003 class 9) + TRIGGERED on a new nuisance element or its placement rule (the GM's tannery case) | - | ~2 (Sawada privies 12/12 upwind; 272 cremation vs wells) | see contradiction 3: the privy seat is rolled over four attested seats with no wind term |
| C6b | Outcast and funerary geography (L364-366) | segregated trades on the margin | outcast STRUCK -> town/city generator obligation; funerary CUT for hamlets + TRIGGERED on a new funerary element | 273 burial seat keeps out of the houses' hull; homes H36 (recorded decision) | ~1 (273 Kuwabata) | |
| C6c | Status zoning (L367-368) | who sits near authority | STRUCK -> town/city tier obligation | migration plan status table | 0 | |
| C6d | Declared economy appears on the map (L369-370) | canon trade drawn | WHOLE-MAP on a map new to the pool (or MOVED: the gen declares its trades, a test finds the kinds) | - | 0 | |
| C7 | Traffic-sited features (L372-432) | board/well/stage where the feet are, per declared seat | CUT for the hamlet board; TRIGGERED on a traffic-sited element added (public well, punishment ground, gate market, stage) or its siter changed, or a new tier | labels L1, L2, L11, L12; `siting.py` objective; `test_board_seat.py::test_an_entrance_seat_stands_where_every_way_out_passes`, `::test_the_board_and_its_caption_stand_inside_the_view`; `test_fixtures.py::test_an_entrance_board_stands_on_the_approach_and_not_on_a_straggler_at_its_join` | ~6 (Ubame founding, Sawada 13->7, Mizuguchi 3 of 12, Sawada board off sheet, anchored board, 269 board caption) | 2 false (the 250 ft count) motivated O3 |
| C8 | Twin detector (L434-438) | distinct from siblings | WHOLE-MAP on a map new to the pool or a new settlement form | - | 0 | never fired; keep for the tier growth the GM names |
| C9a | Spelling and dashes (L440-444) | British spellings on the sheet | CUT | `house-style-hooks.sh` + `check-house-style-delta.py` (captions are declared in code, 286) | ~5, all in engine comments, docstrings or notes; 0 on a drawn sheet | |
| C9b | "people", "domain", they/their on drawn strings (L445) | caste/pronoun wording | STRUCK (wording) | 286 | 0 | |
| C9c | Convention vs defect (L447-449) | off-scale glyph is a convention | PROCESS - travels with the glyph check | research/presentation | - | |
| I1 | What to ignore (L451-461) | exclusions | PROCESS - survives, trimmed | - | - | |
| O1 | Verdict record (L465-475) | `make review-verdict` | PROCESS - survives; FR-010 adds cost | - | - | |
| O2 | Report format and mandatory sweep sections (L477-559) | output shape | PROCESS - rewrite per check | CROSS-ARTIFACT, ANNOTATION, SPELLING, NUISANCE, TRAFFIC sections leave the whole-map form | - | |
| O3 | Every finding names its norm (L536-552) | no invented thresholds | PROCESS - survives in every judgment contract | - | 2 (the 250 ft count, twice) | |
| O4 | Never ask the GM what history answers; knobs; degree vs form (L566-581) | escalation discipline | PROCESS - survives | - | - | |
| O5 | Do not edit files (L583) | - | PROCESS - survives | - | - | |
| V1 | Validated: pixel-count rule, Inashiro T12 (L591-604) | - | CUT (case guaranteed) | woods W06 + 298; becomes the red case of S18's MOVED test | - | |
| V2 | Validated: traffic siting, Ubame (L606-628) | - | example for the triggered traffic-sited check; the board itself CUT | as C7 | - | "a label much larger than its glyph drifts to empty ground" is now the board siter's caption scoring |
| V3a | Founding run: forge face (L635-640) | - | glyph check example | - | - | |
| V3b | Founding run: belt vs blob (L641-645) | - | CUT | woods W16-W19 | - | |
| V3c | Founding run: road through compound (L646-650) | - | CUT | the overlap matrix (`overlap/taxonomy.py` "manors"); `manor_walls_clear_of_ways`, which the contract names, no longer exists | - | stale name |
| V3d | Founding run: building on the neighbor's soil (L651-655) | - | no home: `structures_stay_on_their_side_of_a_border` no longer exists, and the taxonomy says a border blocks nothing | town/city tier obligation | - | rule has no home |
| V3e | Founding run: caption pierced by its feature (L656-657) | - | STRUCK (placement) | caption placer | - | |
| V3f | Founding run: scrub on the stage roof; verify ink in the SVG (L658-675) | - | case CUT (woods W10, occlusion); the lesson PROCESS survives | - | - | |
| X1 | (not in the contract, as fired) engine and tooling defects found while verifying a fix (husks, no-op fixes, `classify` filter, isort order, the remnant sweep) | - | PROCESS: belongs to the one verification round (FR-009) | - | ~20 | real value, but not a map check |
| X2 | (as fired) page hit regions and lit appearance | - | MOVED (FR-003 class 7) | `tests/interactive/test_page_hits.py` covers only the layer order and widths | ~6 (153 rounds 1-4, 230 pass 5) | |
| X3 | (as fired) page prose: place card, modals (156 rounds 1-7, 269/273 card text) | - | out of this contract: entry-drift/record checks, or TRIGGERED on a new page-text type | - | ~25 | needs a ruling: the spec scopes the record checks out |

Counts (settlement-review, 62 rows, primary verdict of mixed rows): CUT 8, MOVED 5, STRUCK 11, TRIGGERED 7, WHOLE-MAP 2,
PROCESS 27, no home 1 (V3d), out of contract 1 (X3).

### building-review.md (Opus high; dispatched by hand when a Mode A sheet is drawn or revised - no script owes it; `pair-hooks.sh:463` only refuses a multi-subject dispatch)

| # | check | what it judges | verdict | occasion or replacing test/rule | ledger fires (~n) | note (figures observed 2026-10-01; method: the ledger rows named) |
|---|---|---|---|---|---|---|
| B1 | When to dispatch (L10-12) | before any Mode A sheet is done | PROCESS - rewrite to occasions; give it a scripted owed-answer | a sheet drawn, its layout revised, a new program | - | ledger also shows it run on interactive-page text deltas (262, 264) |
| B2 | Tier pin, batching (L18-27) | - | PROCESS - survives | - | - | |
| B3 | Inputs (L33-46) | - | PROCESS - survives | - | - | |
| B4 | Protocol 1-3 (L48-52) | read program, notes, PNG first | PROCESS - survives | - | - | |
| B5 | Protocol 4 - SVG geometry in feet (L53) | scale sanity | CUT here (size-audit owns it) | size-audit + `size_bands` registry | - | duplicate of size-audit |
| B6 | Protocol 5 - annotation and terminology sweeps (L54) | - | STRUCK (wording) | 286 | - | |
| B7 | The map, when the notes declare one (L58) | sheet agrees with its map | CUT (the sheet side of what the GM struck from the map side) | `matches_map`, `trees_overlap`, `test_every_mode_a_sheet_passes_its_checks` | ~3 (257 three geometries, 268 approach missing) | only one sheet declares a map |
| B8 | Program completeness (L59) | required items present | CUT; residual TRIGGERED on a new building program | `program_complete` from `buildings/types.json` | ~5 (no service gate, no dais, office rooms, guests' privy, latrine per zone) | |
| B9 | House style beyond spelling (L60) | dashes, domain, they, people | dashes CUT (hooks); the rest STRUCK (wording) | house-style hooks; 286 | 0 | |
| B10 | American spellings (L61) | British spellings | CUT | `house-style-hooks.sh`, `check-house-style-delta.py` | 0 | |
| B11 | Notes-vs-drawing consistency (L62) | notes state what is drawn | MOVED (FR-004 extended to sheets: typed counts and knob lines vs the `data-kind` census) | `tests/interactive/test_sheet.py::test_the_census_names_untagged_ink_and_unknown_kinds` is the census half | ~15 (stale notes in most rows) | staffing story stays prose |
| B12 | Circulation (L63) | doors feed courts, service routes, guest route | TRIGGERED on a sheet drawn or its layout revised (already its occasion) | - | ~20 (genkan in grain alley/lane x2, servants cut off, middle gate off route, carts no way in, 7 ft pinch, kitchen door, rear alley sealed) | highest-yield BR check |
| B13 | Sanitation and privies (L64) | privy count per zone; residence privy attached | count CUT/MOVED (program per-zone count); attachment MOVED (privy rect abuts residence); siting vs well TRIGGERED with B12 | `program_complete` | ~10 | |
| B14 | Entrance completeness (L65) | every residence block has a door | MOVED (a door glyph on each residence/lodging block's wall) | `floating_doors` is the neighbor check | ~8 (sealed dwelling, family block x2, rowhouse bays, zashiki, door per bay) | |
| B15 | Fire-water provisioning (L66) | tub count and placement | placement CUT; count MOVED (tubs per wooden building, kitchen >= 2) | `fire_water_adrift`, `tubs_in_buildings`, `tubs_on_wells` | ~6 (tubs not at kitchen x2, tubs spread, tub under roof, tub on practice ground) | |
| B16 | Realistic unless the GM says otherwise (L67) | narrowest supported reading | PROCESS - survives | - | - | |
| B17 | Internal dead-space (L68) | bare bands inside the walls | TRIGGERED on a sheet drawn or its layout revised | `pack_audit` vacant rectangles, `coverage_band` | ~8 (rear bands 74x25, 129x29, rear pocket, cart-yard void, bare patches) | duplicates size-audit's packing sweep - merge |
| B18 | Nothing standing inside a wall (L69) | structures clear wall ink | CUT | `structures_on_walls`; homes H29a | 0 | |
| B19 | Scale (L70) | ~2x off reality | CUT here (size-audit) | `size_bands` | ~1 (house twice research 380) | duplicate |
| B20 | Historical plausibility (L71) | Edo-first plausibility | TRIGGERED on a new program or a sheet drawn | - | ~10 (hearth on axis, kitchen apart, gate range not nagaya-mon, shrine in bank street, torii mid-grove) | |
| B21 | Annotation sweep; gates need no label (L72) | generic or restating text | STRUCK (wording) | 286 | ~3 (generic caption, "first"/"innermost", header) | |
| B22 | Terminology sweep (L73) | terms vs canon | STRUCK (wording) | 286; triggered check on a new caption type if it slips | 0 | validated example pre-ledger |
| B23 | Interior and occupancy (L74-75) | rooms, idiom, occupancy, massing | TRIGGERED on a new program or a building's interior drawn/revised | - | ~10 (room order, occupant labels, karo lodging, one-room-deep bar x2) | |
| B24 | Text containment (L76) | text inside its box | STRUCK (placement) | caption placer: labels L13, homes H29c | ~15 (254 four overruns; 267 rounds 3-5 caption seats on every sheet) | dominant BR load in 267 |
| B25 | Explanatory entries traceable; no key box (L77) | key boxes | MOVED (a forbidden key-box registry check like `scale_bar_present`) | - | 0 | |
| B26 | Crop / whitespace (L78) | viewBox hugs content; road stubs reach edge | crop CUT; road-stub MOVED | `viewbox_cropped` | ~4 (frame cropped, scale bar strip x2, title strip) | scale bar seat is placement |
| B27 | Required furniture (L79-85) | scale bar, no compass, no key, title block | scale bar CUT; compass/key/title MOVED; "other boxes" STRUCK (wording) | `scale_bar_present` | ~2 | |
| B28 | Conventions: kanji, palette roles, label precision (L86) | fill matches kind; precise names | palette MOVED (`data-kind` vs fill table); kanji/precision STRUCK (wording) | - | ~1 | |
| B29 | (as fired, under first impressions L52) glyphs reading as something else | posts as doors, rack as door, slab storehouses, steam | TRIGGERED - the glyph check (Mode A glyphs) | - | ~5 | the same occasion as C1 |
| B30 | Coherence (L87) | one consistent story | WHOLE-MAP (whole-sheet) on a new sheet | - | ~2 | |
| B31 | What to ignore (L89-93) | - | PROCESS - survives | - | - | |
| B32 | Output and mandatory sweep sections (L95-153) | - | PROCESS - rewrite; ANNOTATION, TERMINOLOGY, SPELLING sections go; CROP and FURNITURE become registry relays | - | - | |
| BX | (as fired, not in the contract) interactive-page modal text, 262/264 | - | out of contract (record checks) | - | ~30 across 5 rows | needs a ruling |

Counts (building-review, 33 rows, primary verdict of mixed rows): CUT 10, MOVED 5, STRUCK 4, TRIGGERED 5, WHOLE-SHEET 1,
PROCESS 7, out of contract 1 (BX).

### size-audit.md (Opus high; "when a diagram is drawn or revised, or a size looks off" - already narrow, but no script owes it)

| # | check | what it judges | verdict | occasion or replacing test/rule | ledger fires (~n) | note (figures observed 2026-10-01; method: the ledger rows named) |
|---|---|---|---|---|---|---|
| Z1 | When to dispatch (L10-12) | drawn or revised plan | PROCESS - survives; narrow to a sized element added/resized or a new program | - | - | occasion already narrow; leave it |
| Z2 | Tier pin; arithmetic scripted (L18-24) | - | PROCESS - survives | `make size-table` | - | |
| Z3 | Independence rule; direction is not magnitude (L34-67) | tolerances are claims | PROCESS - survives | - | - | |
| Z4 | Inputs; pack-audit (L69-87) | - | PROCESS - survives | - | - | |
| Z5 | Method 1 - enumerate every sized feature from the table (L91-103) | complete size list | CUT (the table); residual MOVED | `make size-table`; untagged ink in `test_sheet.py::test_the_census_names_untagged_ink_and_unknown_kinds` | - | paths/circles/glyphs not in the table: extend the script |
| Z6 | Method 2 - historical anchor per feature (L104-110) | what the real thing measured | TRIGGERED on a new kind (or a kind given a new function) or a new program | once anchored, the band lives in `types.json` | ~10 (burial ground quarter band, writing room, arch posts, rope on trunk, kitchen end, sacred tree crown, arch depth, hall depth) | |
| Z7 | Method 3 - ratio verdict ok/oversized/wrong (L111-118) | drawn/real ratio | CUT once a band exists | `size_bands` registry | (counted in Z6) | point-glyph exemptions stay with Z6 |
| Z8 | Method 4 - proportion/hierarchy pairs (L119-132; output L216-226) | ordering inversions | MOVED (pairwise area ordering on `data-kind`: kitchen < residence, stable < barracks, kura < residence, shrine < residence, cell < barracks) | - | ~3 (forecourt order, writing room vs living end, well marker vs sanctuary) | the pairs are a fixed table |
| Z9 | Method 5 - coverage band (L135-141) | 37-42% jin'ya band | CUT | `coverage_band`; homes H29b for generated sheets | 0 | |
| Z10 | Method 5 - composition, perimeter hugging, backing voids (L142-168; output L232) | buildings ring the walls; floaters | hugging % CUT; backing voids TRIGGERED on a sheet drawn or layout revised | `perimeter_hugging` | ~2 (25 ft gravel behind sanctuary, 7,800 sq ft behind) | the file records a geometric detector was tried and reverted |
| Z11 | Method 5 - top-N vacant rectangles quantified (L169-181) | feature vs slack, sized | TRIGGERED on a sheet drawn or layout revised | `pack_audit` lists them | ~1 | merge with B17 |
| Z12 | Method 5 - per-region density (L182-191) | sparse pockets | TRIGGERED, as Z11 | - | 0 | |
| Z13 | Method 5 - aligned gaps (L192-199) | abut vs fire-gap | TRIGGERED, as Z11 | - | 0 | |
| Z14 | Output - spelling sweep (L206-211) | British spellings | CUT | house-style hooks | 0 | |
| Z15 | Output - tubs adrift (L235) | relay | CUT | `fire_water_adrift` | 0 | already a relay |
| Z16 | Output - LAYER section (L236) | relay of occlusion, board, doors, tub on well | CUT; caption placement STRUCK | `occluded_foreground`, `notice_board_adrift`, `floating_doors`, `tubs_on_wells` | ~1 (arch posts in approach - `passage_blockers`) | |
| Z17 | Findings/confirmations format (L239-246) | - | PROCESS - survives | - | - | |
| Z18 | Validated: gate opening, duty room, cart gate vs lane (L252-259) | - | gate opening CUT (`gate_widths`, `main_gate_passage_ft`); duty room CUT (`size_bands`); cart gate vs lane MOVED (opening width vs the route it feeds) | - | - | |
| Z19 | Validated: proportion examples (L261-277) | - | MOVED with Z8 | - | - | |
| Z20 | Validated: packing example (L279-294) | - | coverage CUT; gaps TRIGGERED | - | - | |

Counts (size-audit, 20 rows, primary verdict of mixed rows): CUT 8, MOVED 2, STRUCK 0, TRIGGERED 5, PROCESS 5.

### Proposed TRIGGERED checks, grouped by occasion

1. **Element-in-place check (the glyph check, generalized)** - occasion: an element added to a map or sheet, its glyph redrawn,
   its placement rule substantially changed, or a new form of it rolled. Carries: C1 glyph legibility/mirror rule, B29 Mode A
   glyph reads, C2a residual belt form, C2c widths convention, C2e precinct composition, C5 feature-or-slack (a cover element),
   C6a nuisance axis for a new nuisance element (the tannery), C6b a new funerary element, C7 a traffic-sited element or its
   siter. One agent, one contract, a per-element-kind section; looks at one map where the element stands.
2. **GM-complaint fix verification** - occasion: a feature closing a GM-reported visual defect. Carries S17 (answer at fit
   zoom) and S7 (the record can bear the finding) and X1 (the fix fired). One round (FR-009). Cannot share (1): its question
   is the GM's, not the element's.
3. **Mode A layout check** - occasion: a sheet drawn, its layout revised (already building-review's/size-audit's occasion).
   Carries B12 circulation, B13 privy siting, B17 + Z10-Z13 dead space/vacancies/gaps (merge the two agents' duplicate
   sweeps), B23 interior when a building is drawn/revised.
4. **New program check** - occasion: a new building program (a type in `types.json`) or a new kind. Carries B8 what the
   program requires, B20 plausibility, B23 room programs, Z6 anchors (bands then enforced by `size_bands`), Z8's pair list.
5. **New tier** - occasion: the town/city generator. Carries C2b fabric, C2d streets; and records the struck items as placer
   obligations (C6b outcast, C6c status, V3d border, C4c Imperial road caption).
6. **New caption type** - not built (GM: only if wording is seen to slip).

WHOLE-MAP, on a map new to the pool or a new settlement form: C8 twin detector, C6d declared economy, "reads as a place";
WHOLE-SHEET on a new sheet: B30 coherence.

### MOVED items not in FR-003's 14 classes

1. Declared knobs/rolled forms drawn as declared (S19; homes H33/H34/H35 are recorded decisions, not guaranteed) - beside FR-004.
2. Every pool map has a notes file (S10).
3. Page prose stating counts (place card/modals) agrees with the manifest - FR-004 covers notes only (X3).
4. Mode A notes typed counts vs the sheet's `data-kind` census (B11) - FR-004 extended to sheets.
5. Mode A: every residence/lodging block has a door on its wall (B14).
6. Mode A: residence privy attached; privy count per functional zone (B13).
7. Mode A: tub count per wooden building, kitchen >= 2 (B15).
8. Mode A: proportion/hierarchy pair table on `data-kind` areas (Z8).
9. Mode A: no compass rose, no key box, title block present (B25, B27).
10. Mode A: a road stub runs off the viewBox edge (B26).
11. Mode A: palette role (fill) matches `data-kind` (B28).
12. Mode A: gate opening width agrees with the route it feeds (Z18).
13. 257 `matches_map`: add gate direction / addressing face, and require `**On map**` on every sheet whose subject stands on a
    pool map (C3) - the home US5 names lacks what the review actually checked.
14. Optional: the gen declares its trades and a test finds their kinds (C6d).
15. Page hit regions (X2) is FR-003 class 7 - listed only because `test_page_hits.py` covers order and widths, not area won.

### Where the evidence contradicted the spec (ruled in R2)

1. US5 says Mode A agreement lives in 257's sheet-matches-map check. But `mapmatch.py` compares positions and the per-side
   footprint only. It does not compare gate direction or which face addresses the town, which are the only things the
   contract still asked. And only `hoshigaoka-shrine` declares `**On map**`, so for the five magistracies nothing checks
   agreement at all.
2. The contract cites checks that no longer exist: `manor_walls_clear_of_ways` (now covered by the overlap matrix) and
   `structures_stay_on_their_side_of_a_border`. The border rule has no home, because the taxonomy says a border blocks
   nothing. The table also cites `town_margins_clothed`, which survives only as a comment.
3. FR-003 class 9 (a privy seated without the wind): the privy seat is rolled per hamlet over four attested seats
   (research/homesteads/260, `test_homesteads.py::test_the_privy_seat_weights_are_rolled_per_hamlet_over_the_four_attested_seats`),
   and that roll has no wind term. Making wind a rule needs a research pass first. It may come back through the audit as a
   recorded decision or a knob.
4. R0's "never fired" list leaves out two items: spelling on a drawn sheet (all ~5 spelling finds were in code or notes) and
   caption alignment (it fired only falsely, twice). R0's "Mode A agreement confirmed once" also misses the founding run's
   road-through-compound catch (pre-ledger).
5. Building-review and size-audit are owed by no script. A Mode A sheet is not a pool map to `_review_owed.py`, and the pair
   guard only refuses a multi-subject dispatch. So US3/US4's scripted owed-answer must be built for them too. Their occasion
   is nominally narrow ("drawn or revised"), but the ledger shows 267 ran building-review for 7 rounds on one sheet. Rounds
   3-5 were almost entirely caption seats, the struck label placement, so FR-009's cap and US5 bite hardest on
   building-review, not on settlement-review.
6. Building-review rows 262/264 (~30 findings) reviewed interactive-page modal text, which is not in its contract.
   Settlement-review rounds on feature 156 did the same for the place card. The spec puts the record checks out of scope
   but does not say who owns page prose.

## R2 - rulings on the audit's six contradictions (2026-10-01)

1. **Plan-sheet agreement's home is thinner than US5 says.** `mapmatch.py` compares positions and per-side footprint only, and
   only `hoshigaoka-shrine` declares `**On map**`. Ruled: the home is extended (plan B24) - gate side and width, roads under
   every key, and the `**On map**` line required where a map records the sheet's subject. US5's "any rule that check lacks is
   added there".
2. **Stale names in the contract** (`manor_walls_clear_of_ways`, `structures_stay_on_their_side_of_a_border`,
   `town_margins_clothed`). Ruled: the contract is rewritten (plan C) and names only live tests; the border rule has no home
   today and is recorded as an obligation on the town/city tier in the migration plan (the taxonomy says a border blocks
   nothing at hamlet scale).
3. **FR-003 class 9 (privy and wind) is decided by research.** Research homesteads/220 searched for a wind rule and found none;
   the privy seat is a researched sun-side roll (`PRIVY_SUNNY_SHARE = 0.727`, `test_the_privy_seat_weights_are_rolled_per_hamlet_over_the_four_attested_seats`).
   A wind rule would contradict the record. Ruled: CUT (plan D5).
4. **R0's never-fired list was incomplete** (spelling on a drawn sheet; caption alignment fired only falsely). Recorded here;
   both are already CUT/STRUCK in R1. Broadleaf over conifer (FR-003 class 5's last case) is ruled: the crown records carry their
   species and a gate test refuses a broadleaf crown drawn over a conifer it overlaps (plan B5b).
5. **No script owes `building-review` or `size-audit`.** Ruled: the occasion script covers Mode A sheets (plan D1), and the round
   cap applies to every check.
6. **Page prose has no owner.** Ruled: a modal is written from a research section and `entry-drift` already judges the pair;
   the place card's counts are generated from the manifest. No map review carries page prose (plan D9).

## R3 - the rules (FR-003, FR-004, the audit's MOVED rows)

Observed 2026-10-01; method: an Opus agent read the engine, the tests and the pool manifests/SVGs read-only and measured each
proposed predicate on the pool with scratch scripts. The full record, one section per rule with the data it reads, the
threshold and its source, the seeded fault and the pool's measurement, is [`rules-recon.md`](rules-recon.md). The plan's B
section carries the decisions; the pool fails today on B1 (to be measured: Kuwabata's supply run), B4 (comb branches), B6 (hit
regions), B10 (fixtures drawn short of their roll), B17 (`ochiba-roundtrip-test`), B23 (Ochiba's road), B24 (Ubame's missing
`**On map**`). Covered already: reed gaps (feature 298), the sheen cap (`test_finish_287`), acute merges and hairpins (placer
guarantees `NEEDLE_DEG`, `_HAIRPIN_DEG`, gate test to add). Broadleaf over conifer: the scout found no species on a crown record; plan B5b adds it and rules it.

## R4 - the census by a script (FR-013, SC-006; observed 2026-10-01)

Observed 2026-10-01; method: an Opus agent classified each of the ledger's 181 map-review rows once, as data
(`docs/review-ledger-r0.json`: per row its runs, NOT-REVIEWABLE runs, findings by class, author-missed-and-fixed, wall time),
and `make review-census` totals it with the measured table's rows. Settlement-review: 312 runs, 40 NOT-REVIEWABLE, findings
270 geometric / 77 judgment / 174 paperwork / 14 nothing (535), 315 author-missed-and-fixed, 27 minutes of recorded wall time.

Against R0 (the hand census): the COUNTS are higher because the data takes a cell's stated totals ("8 errors, 6 questions") as
that many findings where R0 deduplicated by hand - 535 findings against ~360, 312 runs against ~260. The SHARES agree within
R0's own error (observed 2026-10-01; method: `make review-census` over the ledger and `docs/review-ledger-r0.json`): geometric 50% (R0 44%), judgment 14% (R0 19%), paperwork 33% (R0 31%), nothing 3% (R0 6%); NOT-REVIEWABLE runs
40 against ~36. SC-006 is read on the shares, which is what R0 was used for (the judgment-vs-geometric argument), and the counts
are the script's from here on.
