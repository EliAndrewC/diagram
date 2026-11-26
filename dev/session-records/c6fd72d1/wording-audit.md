# Wording audit: do the open "wording" found rows need any change at all?

Read-only, clone diagram-backlog at HEAD 7dbcd93ec1 (2026-11-24). Every page, claim and code line read from HEAD
(`git archive HEAD` into /tmp/head, never the working tree). No make target that writes was run; `make found-list` only.
Row numbers are found.jsonl line numbers, as `found-list` prints them. Standard: constitution XIV v2.36.0, the root
CLAUDE.md Research bullets, research/CLAUDE.md, and impl-drift.md / record-format.md as they read today.

## Summary

**The hypothesis holds: 66% to 83% of the 153 rows need no change, by how one judgment call (G) is counted; the rest is nine small edits.**

| | rows | FINE | G (page silent on a code-labeled guess) | ALREADY FIXED | REAL, SMALL | REAL, NOT SMALL | CANNOT TELL |
|---|---|---|---|---|---|---|---|
| research-page rows (444) | 89 | 41 | 24 | 5 | 17 (3 issues) | 0 | 2 (1 issue) |
| Rust hamlet code rows (444) | 34 | 19 | 0 | 11 | 4 (3 issues) | 0 | 0 |
| 449's rows in scope (30 of 37) | 30 | 16 | 1 | 9 | 4 (4 issues) | 0 | 0 |
| **all** | **153** | **76** | **25** | **25** | **25 (9 issues)** | **0** | **2** |

- Scope: the 89 page rows are the 86 WORDING-FORMAT plus 3 RESTATEMENT rows (220, 308, 395) the brief did not count. 449's 7 out: 6, 7, 23, 155, 166 (research questions), 26 (a guard misfire), 213 (a possible drawing fault).
- **G, 25 rows, about 13 figures** (bead spacing, crown sizes, the 30 ft cut, the 70 ft run...): live Rust labels the figure GUESS at its claim and says the page is silent; impl-drift passed each such claim IN-STEP on 2026-11-22; no page and no hamlet or choice pop-up (grepped) states one as fact. So no reader is told a guess is a finding: FINE by the checks as run. The root rule read literally ("recorded ... in `research/`") makes each one GUESS bullet on its page. FINE gives 83%, REAL gives 66%.
- No row needs research or a decision; none is a wrong map.

**The REAL issues, one pass a file (9 issues, 25 rows):**
1. 0068 drawing page line 25 (9 rows) + `field/channels.rs` 37, 170 (row 104): "supply canal along the far edge" is the 4.0 ft canal, which runs down the brook's flank; channels.rs 186 and 0053 line 20 call the other flank "far". -> "down the brook's flank".
2. 0022 drawing page line 12 (6 rows): "Our maps never draw the parcels as a grid of uniform rectangles"; one dike-pond hamlet in three is 0019's straight chessboard, which 0022 never names. -> "never draw a rice polder's parcels ...".
3. `field/brook.rs` 7 (rows 21, 234): cites 0054's drawing page for "a step over 22 ft led in over two"; the page has no such figure. -> a GUESS saying 0054 gives only the no-mitered-corner rule.
4. 0019 drawing page line 22 (449 row 212): "no channel runs outside the dike"; the map draws the feeder and the outfall's run. -> add "but for the feeder to the inlet sluice and the outfall's run".
5. `driver/plan.rs` 97 (449 row 22): "the page names no crop on the dikes"; 0026 line 8 records the very 3:2:1 shares as a GUESS. -> cite 0026.
6. `rust/mode_a/src/audit/sun.rs` 1, 49, 54, 59, 446 (449 row 31): prints "(research homesteads 044)", an id with no entry in `research/moved-303.json`. -> name 0038's drawing page.
7. 0072's two notes files (449 row 153): "en.wikipedia East Asian Monsoon gives ..." names a page unlinked and unquoted. -> drop the clause.
8. `field/dry.rs` 51 (rows 68, 280): "(64 bands, over two miles)" is 1.7 miles at two strips of 71.5 ft. -> "over a mile and a half".
9. `field/states.rs` 146 (row 80): points at `field_stage._polder`, a deleted Python name. -> `polder_states`.
- CANNOT TELL (220, 308): 0053 line 17 "On every hamlet map the second canal feeds at least one delivery ditch"; channels.rs 191 handles one with none. Needed: a count over the cohort's seeds. Any such fan: -> "On the pool's hamlet maps".

**What produced the FINE rows.** Every 444 row is an impl-drift line of 2026-10-31 to 11-04, before XIV's "a defect is a wrong outcome" reached the agent (449 T196, 53ffe24473, 2026-11-18). That check had no effect test and filed: (a) a claim's loose word against the code, literally (the 19 FINE code rows); (b) "the page should record this guess", though the claims already said "silent on" (ponds.rs since 10-31) - the G rows; (c) notes on code since deleted, rebuilt or unported (15 rows). **Still running?** Mostly not: impl-drift now writes no line "with no effect a reader of the map would see". Of 449's 6 in-scope rows dated after 11-19, 2 are REAL, 1 fixed, 3 FINE - one of them (178, 11-23) says "effect: none" itself, so the rule leaks a little.

## How each verdict was reached

- **FINE** = read today, nothing on the page or in the claim is false or misleading, and no rule the checks enforce is unmet. One test for a flat sentence with an exception: does a reader of that page alone come away believing something the map contradicts?
  Sub-kinds in the tables: `literal` (a literal-match or style note), `moot` (the code it names is deleted or unported, or the
  figure is gone), `covered` (the thing wanted is already there). **G** is its own verdict (page silent on a code-labeled live guess, above).
- **ALREADY FIXED** = the page, claim or code changed since the row and now satisfies it.
- `ci` = dev/claims-index.json at HEAD: the claim's last impl-drift verdict and date. Supporting evidence only.
- Not done: nothing was rendered or run, so 220/308 stay CANNOT TELL; the builder's uncommitted rust/phases and plan.md edits
  were not read.

## Table 1 - research-page rows (444), by page

| rows | verdict | what was read at HEAD |
|---|---|---|
| 394 (cluster.py -> driver.rs 417) | FINE, literal | the claim cites 0081 "A track keeps off wet ground"; 0035 line 12 holds the crossing rule too; a second pointer is a preference; ci IN-STEP 11-07 |
| 234, 21 (0054 / brook.rs 7) | **REAL, SMALL** | brook.rs line 7: "the brook bends - ...0054...drawing.html: a step over 22 ft led in over two"; 0054's drawing page has no 22 ft, no step rule (lines 21-23 give the sweep, 2.5 widths, the 35% cap). No unit inherits the module claim now, so no check sees it. The other three figures row 21 names (1.6 degrees, ten widths, 150 ft) are no longer cited to that page |
| 362 (sink_stage.py) | FINE, moot | no "a diked field lays no collector" claim is left in rust/phases |
| 35 (0005) | G | lattice.rs 189: "the bow's size a GUESS, up to 15% of a row"; page silent on the bow |
| 72, 86, 115, 146 (0005) | FINE, covered | lattice.rs 26-27 rolls 40, 48, 60 ft: the page's "some 40 to 60 ft across" (line 5) and "about 48 ft" (line 12); 115's 34 and 70 ft are gone; the sizes' weights are a stated GUESS (plan.rs 17); a page may name no engine identifier |
| 328 (0005) | G | lattice.rs 88: "a half-row between counts - GUESS: ...silent on a row no whole count of such basins fills"; a fitting fallback |
| 345 (0005) | FINE, literal | a suggestion ("would let the claim cite this page"); nothing on the page is false |
| 272 (0006) | G | dry.rs "off the water - GUESS: ...silent on how near the water a dry plot may come"; ci IN-STEP 11-22 |
| 318 (0006) | FINE, covered | page line 35 calls the 20 degrees "a drawing convention"; dry.rs "where none stands apart - GUESS" records the impossible case; XIV: a difference from a convention's own wording is no defect |
| 93, 320 (0008) | G | page line 19: "How much of it is open water and where the reeds stand is a GUESS: no page we read gives a dish pond's proportions"; the 2.2 ft bank (driver/polder.rs 235) and staged.rs "a four-sided host", "never a resting plot" are GUESS claims saying the page is silent; ci IN-STEP 11-22 |
| 108, 327 (0011) | G | page line 10 records the upslope order as a GUESS; dry.rs "the last band from the canal's start - GUESS"; ci IN-STEP 11-22 |
| 270, 306 (0011) | FINE, literal | "the hem along the whole canal" (line 12) and the barley remainder: the page is brief, not false |
| 120 (0013) | G | states.rs "a resting plot from the green - GUESS: ...silent on whether a wet plot rests"; ci IN-STEP 11-22 |
| 20, 95, 96, 221, 267 (0014) | G | beans.rs: spacing 8 ft, at most four, three bunds in eight, a drowned bead dropped - each "GUESS: ...silent on ..."; the page gives the 3 ft bead and "at least two beads" (line 27) and "Some bunds carry a row" (line 5); ci IN-STEP 11-22 |
| 313 (0014) | FINE, literal | an ink opacity of a stated convention (lines 25-28) |
| 349 (0014) | FINE, moot | the Rust polder calls no bean stage and carries no such claim |
| 9 (0017) | FINE, moot | no `FIELD_ACRE_BAND` in rust/phases |
| 39 (0017) | FINE, literal | line 8 gives both figures and where each comes from in the same paragraph |
| 79 (0017) | FINE, covered | field.rs 23 states the 1.3 gross against the page's quarter acre a head; 1.3 lies in the page's "1 to 2.5 acres"; 0011 line 11 names "its 1.3 acres of paddy" |
| 38, 70, 77, 143, 151 (0018) | G | ponds.rs "rounded corners - GUESS: ...silent on a pond's corners", "the least pond - GUESS: ...silent on a parcel too small"; landuse.rs 33 the same; ci IN-STEP 11-22 |
| 148 (0019) | G | polder.rs "the feeder - GUESS: ...the page is silent on its course"; ci IN-STEP 11-22 (the feeder outside the dike is 449 row 212, Table 3) |
| 144, 188 (0020) | FINE, literal | line 15: "about one parcel in ten left in standing rice among the ponds"; where they stand is unsaid, not mis-said |
| 73, 117, 147, 168, 189, 207 (0022) | **REAL, SMALL** | line 12: "Our maps never draw the parcels as a grid of uniform rectangles." 0019 line 30: the chessboard "on the rest" (one hamlet in three); polder.rs claims "the chessboard's ponds single", "drawn straight", and "the dike-pond's chessboard the one exception". 0022 never names the chessboard, and its line 21 ("most of them merged in pairs") is the mosaic's alone |
| 27, 66, 106 (0027) | G | dike.rs "the crowns - GUESS: ...silent on a crown's size", "the gap - GUESS: ...silent on the cut's width"; ci IN-STEP 11-22. The mulberry crown is a recorded GUESS on 0018 line 12 and 0026 line 16 (4.4 to 7 ft) |
| 4, 6, 8 (0031) | ALREADY FIXED | line 35: "Our hamlets take it wherever chance sets their fall, a deliberate deviation: the land falls away from the wind or across it, its high side windward or level" (449 T261) |
| 398 (0035) | FINE, literal | line 12: "A way crosses the water only at one of them"; the claim cites 0081, IN-STEP |
| 136, 204 (0053) | FINE, covered | line 17 "partway down its edge, narrowing to a thread" and line 19's two endings agree with channels.rs 194, 238 ("at the thread from its last offtake either way") |
| 173 (0053) | FINE, literal | "laid out first" and 0060's low line do not conflict |
| 220, 308 (0053) | CANNOT TELL | see the summary; 308's other half (canal A with no offtake) is a stated GUESS, channels.rs 190 |
| 201, 180 (0054) | FINE, literal | the brook's swing and wave are GUESS claims that say 0054 is silent (brook.rs 26, MEANDER_FT; ci IN-STEP 11-22); a gentler meander than a river's contradicts no finding |
| 97 (0054 research page) | FINE | a "not in the bundle" note |
| 359, 361 (0054) | FINE, covered | course.rs 33: "the page's 35% kept on the tangent run too, so neighbors leave at least 30% of a leg straight" |
| 395 (0058) | FINE, literal | line 13's "farmed and built on" is the wells' sentence ("Keeping wells off the whole drawn marsh would refuse every well standing there") |
| 60, 89 (0059) | FINE, literal | the lede's "on one side" is detailed by line 10 ("past one shoulder of the fan or straight into the middle"); "to leave the map or to take in the field's drain" is not two endings |
| 105 (0059) | ALREADY FIXED | channels.rs 238: "canal B, partway down its edge, stops at its last offtake" |
| 286, 335 (0059) | G | brook.rs 97 "the tap's stride - GUESS: ...silent on how far below a shoulder intake the brook keeps its line"; driver.rs BROOK_TAP_RUN the same; ci IN-STEP 11-22 |
| 23, 64, 135, 165, 184, 205, 218, 277, 307 (0068) | **REAL, SMALL** | table line 25: "supply canal along the far edge / 4.0 -> 1.5"; channels.rs 186 "canal A along the head to the far corner, swept, then down the far flank; canal B down the brook's flank", 189 "canal A the upper edge's ... canal B the other edge's, down the brook's flank". The page's "far edge" is the code's near (brook) flank. The map is right; the label is not |
| 162, 224, 310 (0068) | FINE, moot | no `DEFAULT_W`, no `DITCH_BANK_FT` in rust/ |
| 216 (0068) | FINE, moot | the footbridge code is deleted and unported; the Rust keeps widths in feet |
| 229 (0068) | ALREADY FIXED | line 42: "the cap bites ... at every offtake of a canal with only one or two" and "only the first canal's first delivery keeps the full rung" |
| 296 (0068) | FINE, covered | polder.rs "the widths": the polder's arms "as a fan's canals A and B"; a reading within the ladder; ci IN-STEP |
| 389 (0071) | FINE, covered | margins.rs "belt's distance upwind - GUESS ... this only asks for room on the canvas"; no grove is drawn by the Rust |
| 386 (0081) | FINE, literal | exit.rs's 20 ft is its search grid's cell, plumbing |
| 50, 127, 305, 322 (0084) | FINE, moot | footbridges are unported: no claim names these guesses (the reason commit 7dbcd93ec1 closed 24 like rows) |
| 290 (0087) | FINE, moot | the same: no bridge stage in the Rust |

## Table 2 - Rust hamlet code rows (444, "OLDER: wording"), by file

| rows | verdict | what was read at HEAD |
|---|---|---|
| 22 (brook.rs), 37 (polder.rs), 40 (rules.rs), 236, 319 (dry.rs), 31 (index.rs) | ALREADY FIXED | every plumbing unit has its own NONE claim (`local`, `file`, `clearance`; `Ditch`, `Frame`, `Plot`, `Polder`; `FieldRefused`; `Canal.*`); index.rs's module claim is NONE; no key in the index is inherited |
| 98, 181, 268 (brook.rs 149) | FINE, literal | the comment is past tense ("ran 110-160 ft straight ... T16's claims round"); "ten widths" is 0054's research page line 18, and MEANDER_WAVE_FT's claim cites it |
| 164 (brook.rs) | FINE, literal | "GUESS: <page> silent on ..." is the form impl-drift passes today (IN-STEP 11-22) |
| 102 (channels.rs 184) | FINE, literal | quotes 0053 line 11; the head race's constant 6.0 ft is claimed beside it (187 "at that width throughout") |
| 103 (channels.rs 186) | ALREADY FIXED | "...or swept along the head to its own corner from a middle one" |
| 104 (channels.rs 170, 37) | **REAL, SMALL** | "one along the far edge", "4.0 -> 1.5 along the far edge": the 0068 issue's copy in the code |
| 185 (channels.rs 192) | ALREADY FIXED | the steps now cite 0068 line 42 ("A canal narrows in equal steps from its head to 1.5 ft at its last offtake") |
| 68, 280 (dry.rs MAX_BANDS) | **REAL, SMALL** (trivial) | "a guard far past any canvas (64 bands, over two miles)": 1.7 miles at two strips; the point (far past any canvas) holds |
| 28, 29, 30 (fan.rs) | FINE, literal | "one point a 64 ft index cell" (a spacing equal to the cell); `Fan.at` is NONE; "its bunds converging" is the page's phrase |
| 243 (index.rs) | FINE, literal | NONE claims; the row itself says the label is right |
| 32 (landuse.rs 33) | ALREADY FIXED | "the rounding - GUESS: ...the bank's cut back 8 ft and the water's 16 ft"; the nursery inset is gone from it |
| 36 (polder.rs 60) | FINE, literal | the line above the claim states it: "of this many dike-pond modules, one stands alone" |
| 348 (polder.rs 50) | FINE, literal | lines 46-47 name the pairing exactly |
| 352 (polder.rs 44) | FINE | a date one day past the row's own; nothing rests on it |
| 357 (polder.rs 635) | FINE, literal | "a merged pair's gap its own bank": the pair's bank, as the code draws it |
| 152 (ponds.rs) | ALREADY FIXED | "the water a tenth of the parcel across" |
| 353 (ponds.rs 65) | FINE, literal | a past-tense note on a fixed fault |
| 80 (states.rs) | **REAL, SMALL** (trivial) | "a polder tints every low plot, at its own stage (`field_stage._polder`)": a deleted Python name; the unit is `polder_states` |
| 396 (seat/margins.rs) | FINE, covered | the quotation is 0035 line 8 word for word |
| 379 (sink/brook.rs 57) | FINE, covered | 0067 has no drawing page; its one page says "The band and the run are a guess" (line 24) |
| 3, 5, 7 (water_frame.rs 5) | FINE, literal | "the bearing and the fall rolled": a hamlet's bearing is its rolled fall; `roll_plan`'s own claim gives the split ("the drainage bearing is `plan_site`'s, declared or taken from the fall"), IN-STEP |
| 383 (water_frame.rs) | ALREADY FIXED | "each knob at even odds over its table ... the settlement form's 5, 3 and 2 of ten"; ci IN-STEP 11-22 |

## Table 3 - 449's 37 open rows

| row | date | verdict | what was read at HEAD |
|---|---|---|---|
| 2 | 11-08 | FINE, literal | two CONVENTION notes are comments; the inks they describe carry claims; nothing is false |
| 6 | 11-08 | out of scope | a research question (room for a scattered form); open 449 T417 |
| 7, 23 | 11-08 | out of scope (research questions; my read: fine) | 0031 line 45: a hamlet's lane pattern comes "from a table of its own"; line 47 gates the fifth form; plan.rs "the lane forms" IN-STEP 11-22; the Rust draws no lanes. (The triages called these research questions) |
| 10 | 11-08 | G | driver/polder.rs 100: "the strip's depth - GUESS: the page records no depth" |
| 11 | 11-08 | ALREADY FIXED | each ink has its own CONVENTION claim (driver/polder.rs) |
| 20 | 11-08 | ALREADY FIXED | driver.rs 71-74: "A basin's cell length along its canal (ft)" |
| 22 | 11-08 | **REAL, SMALL** | plan.rs 97: "the page names no crop on the dikes"; 0027 line 5 "willow on the water side and mulberry on the field side"; 0026 line 5 "mulberry, fruit or tea", line 8 "Half the hamlets plant mulberry, a third fruit and a sixth tea, a GUESS" - the very shares the table rolls |
| 26 | 11-12 | out of scope | a guard misfire, not wording |
| 31 | 11-18 | **REAL, SMALL** | sun.rs 446 prints "(research homesteads 044)"; the phrase resolves to nothing in the tree; the claims rest on 0038's drawing page |
| 32 | 11-18 | FINE, literal | two claims say their account twice; untidy, not untrue |
| 35, 36 | 11-18 | FINE | bundle notes; 0116 line 13 does read "About 30-42%" |
| 65 | 11-18 | FINE, literal | hits.rs holds the polygon's box clear, so the polygon is held clear, as the claim says |
| 66 | 11-18 | FINE, literal | the line above the claim names "a bead's radius factor" |
| 69 | 11-18 | ALREADY FIXED | the sentence is gone from docs/buildings.md |
| 72, 73 | 11-18 | FINE, moot | the placer T202 rebuilt has no long-band rule and no `extended_cands` |
| 74 | 11-18 | FINE, covered | search.rs 230 cites the page's own DEVIATION (0242 line 29) |
| 112, 116 | 11-18 | ALREADY FIXED | 0242 line 27: "or an outline holding the others ... turned to that block's or outline's angle, or level where that outline has no direction of its own" |
| 117 | 11-18 | ALREADY FIXED | 0330 line 9: "the leader goes to a closed outline before a stroke, and to the wider of two strokes" |
| 123 | 11-19 | FINE, moot | the claims that quoted the tie note went with the old placer |
| 125 | 11-19 | ALREADY FIXED | 0242 line 24: "A road or stream crossed counts as half a building: our calibration, not a finding" |
| 127, 128, 129 | 11-19 | FINE, covered (the general rule is on the same page, unlike 0022, whose exception is on another page) | 0242 line 8 "A feature large enough to hold its name ... is named on itself" and line 27 (beside the box) together are what captions.rs `holder` does: on itself where it fits, else beside the box; its claim says so |
| 130 | 11-19 | ALREADY FIXED | emit.rs's plumbing carries "the sheet's plumbing - NONE"; every key IN-STEP |
| 153 | 11-22 | **REAL, SMALL** | both 0072 notes files: "(...; en.wikipedia East Asian Monsoon gives the continental winter wind as northeasterly)" - a named page, no link, no quotation (research/CLAUDE.md: every reference is a link) |
| 155, 166 | 11-22 | out of scope | research questions |
| 178 | 11-23 | FINE, literal | building-programs.md 123 gives the drawn size "on the plan"; the row says "effect: none" |
| 193 | 11-23 | FINE | a note on the bundle; a later round judged the claim (452 T010) |
| 204 | 11-23 | ALREADY FIXED | the passage is 0334 line 18, with two footnotes |
| 211 | 11-23 | FINE, covered | ruled already (plan-done.md 8718): "the GM's ~15 are a county town's whole samurai ... not the barracks' lodgers, so the lodging count stays the project's" |
| 212 | 11-24 | **REAL, SMALL** | 0019 line 22: "no channel runs outside the dike"; polder.rs draws the feeder (a 3 ft line, driver/polder.rs 90) and the outfall off the map |
| 213 | 11-24 | out of scope | asks for a look at a rendered polder: a possible drawing fault |
