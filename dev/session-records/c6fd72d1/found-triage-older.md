# Found-rows triage, part 2: the older open rows (449's 115 dated 11-08..19, 444's 105 and 450's 2 that name rust/phases)

Read-only, clone diagram-backlog at HEAD dffc66dbf8 (2026-11-24; the first triage read 5eec349309). Every code and page check
read HEAD's copy (`git archive HEAD` into /tmp/head, `git show HEAD:`); the builder's uncommitted edits to rust/phases and 449's
plan.md are not judged and are named only where an open task says a fix is in them. No make target was run. The hamlets'
`*.driver.svg` and `*.driver.json` are untracked generated files, so they are evidence of what a build drew, not of HEAD: the
Kuwabata crops (/tmp/crop) were rendered with rsvg-convert from the file of 2026-11-22 17:01; all five were regenerated from the
builder's working tree at 09:50 today, so HEAD's knob rolls were recomputed from pyrand.rs's recipe instead (checked on three hamlets).

## Summary

**Rule**: constitution XIV as the first triage used it - a wrong map or sheet, a check that passes bad work, or a page or doc
that tells its reader something false about the drawing is a DEFECT; a code claim or why-text that does not match is a
RESTATEMENT; "the bundle did not show X" is a note on the check, not a finding.

**Rows read: 222** = 449's 115 older open rows (18 rust/phases, 45 rust/mode_a, 52 other) + 444's 105 naming rust/phases (104
open, row 403 with no status) + 450's 2. No other found.jsonl names rust/phases.

**The split:** NOT NEEDED 130 (fixed at HEAD, verified no fault, the Python or the placer it names deleted or rebuilt, carried by
open 449 T416-T418 or 444 T42, or one of 24 bundle notes whose figure reads right at HEAD). Live 92 = DEFECT 13 rows in 6
clusters, latent or unverified code faults 16, WORDING-FORMAT 46, RESTATEMENT 13, RESEARCH QUESTION 4.

**Hamlet engine defects - 3 clusters (8 rows), all in the polder or the winter-crop roll:**
1. 444 rows 61, 100, 228, 276, 298 - CONFIRMED, owned by open 449 T416/T418 (a rule lost in the port). A cleared middle with a
   bare winter paddy is rolled 1 valley hamlet in 8; 0011's page says it is never drawn. **Kashikawa (seed 3) rolls it at HEAD**,
   as its 11-07 record shows: 7.2 of 17.0 acres of grain ground.
2. 444 rows 26, 187 - CONFIRMED, no task found. The polder's dike band is painted unbroken over the feeder and the outfall;
   0027's page says the band is cut there. Kuwabata shows it.
3. 444 row 354 - CONFIRMED as drawn, wrong only on one page's reading. A dike-pond's channels are drawn at field-ditch widths;
   0018's page says "not as field ditches", 0019's calls them a lattice of ditches. Kuwabata shows it. No task found.
- Latent, no hamlet can draw it: 444 rows 226, 269, 299, 363 (several fields: a hamlet's 10.5 ha never passes the 45 ha cap),
  191, 1, 75/208, 116, 118. AS REPORTED, unverified: 387, 388 (the hem's line and its edge behind the seat).

**Mode A code: 0 open defects a sheet shows; 2 audit gaps, both latent.** 449 rows 50/55/60, CONFIRMED: the audit's size ranks
have no bath pair (the generator holds it). Rows 53/58/63: arch_on_approach still measures to the plan's bounds; whether that is
the shrine's ground was not read. The other 42 Mode A rows are fixed (449 T172-T195), name the placer T202 rebuilt, or are wording.

**Record and doc defects: 2, both CONFIRMED.** 449 row 124: building-programs.md gives the generated guest quarters as a room
beside the reception; the county example draws a detached 40 x 42 ft guest house. 444 row 74: 0019's page says canals have
rounded corners; the polder's ring canal is four straight trunks (minor).

**"Do the open findings give reason to believe hamlet generation is riddled with defects?" No.** Of 125 rows on the hamlet
engine, two clusters are confirmed wrong outcomes (one already being fixed) and a third depends on a reading; the rest are
claim wording, check notes or faults fixed since. Not seen: these rows are claims-against-code checks that never looked at a
map; the Rust driver draws only field, seat, hem and reeds, so nothing here judges houses, lanes or groves and the pool's full
hamlet pictures are the Python's of 11-07; 387, 388, 116 and 118 need geometry run; the builder's edits are unread.

## Table 1 - 449, rows naming rust/phases (18)

FIXED = gone at HEAD (what was read is named). All file paths under rust/phases/src/.

| row | kind | note |
|---|---|---|
| 1 | NOT NEEDED | FIXED: driver.rs's constants each carry their own claim above them (lines 60-90 read) |
| 2 | WORDING-FORMAT | the placeholder's ink has a claim (driver.rs 94); the reeds-under-field and placeholder notes at 612 and 763 are still inline comments; no map effect |
| 5 | NOT NEEDED | FIXED: DIKE_CROPS, LEFTOVER_FORMS, FRY_FORMS are bare GUESS claims with no pointer (driver/plan.rs 92-103) |
| 6 | RESEARCH QUESTION | band room not varied by settlement_form: the seat's side of this is open 449 T417; houses are not drawn by the Rust driver |
| 8 | NOT NEEDED | FIXED: svg.rs's module claim is NONE |
| 9 | NOT NEEDED | FIXED: ROW_FT's GUESS cites 0006's drawing page (svg.rs 66) |
| 11 | WORDING-FORMAT | driver/polder.rs's inks carry CONVENTION claims (24-66); the module claim still cites 0019; label only |
| 12 | NOT NEEDED | FIXED: check.rs 48 "on the canvas - CONVENTION" |
| 13 | NOT NEEDED | FIXED: the comment at lattice.rs 369 names the rules through `rules::held`; wording only in any case |
| 14 | NOT NEEDED | FIXED: staged.rs 37 states "never a resting plot" as a GUESS |
| 15 | NOT NEEDED | verified no fault: waterward.rs::flanks (45-52) leaves the head bare on purpose and its claim says why (the wild pond stands there as the water) |
| 17 | NOT NEEDED | verified: SeatIn.wind is "pointing to where it comes from" (seat.rs 39), so `wind = -fall` is the high side |
| 18 | NOT NEEDED | FIXED: fill's claim names five states (driver.rs 275) |
| 19 | NOT NEEDED | FIXED by 449 T294: settlement_ground sweeps the belt round the band's windward end (driver.rs 489-508) |
| 20 | WORDING-FORMAT | CELL_SHARE is 31 ft, a length, still named a share (driver.rs 71-75); no map effect |
| 22 | RESTATEMENT | still there: plan.rs 92 "the page names no crop on the dikes", while 0019's page names mulberry dikes; the roll is fine |
| 23 | RESEARCH QUESTION | lane_skeleton rolls four of 0031's five forms (plan.rs 46); the fifth needs water along the cluster (0031 line 47); lanes are not drawn by the Rust driver; pairs with row 7 |
| 24 | NOT NEEDED | the polder's center and landward siting are in open 449 T416 (stage_polder#the polder) |

## Table 2 - 444 (104 open + row 403) and 450 (2), rows naming rust/phases

| rows | kind | note |
|---|---|---|
| 61, 100, 228, 276, 298 | **DEFECT [hamlet engine]** CONFIRMED | cleared middle + bare winter rolled 1 in 8 (driver.rs 153-154, field/build.rs 232-268); 0011 drawing line 12 "such a hamlet is always drawn growing its barley on its paddy"; the map shows a bare winter paddy and a one-band hem holding under half the grain. Open 449 T416 (the cleared half, in the builder's uncommitted build.rs) and T418 (the wild half). Pool: Kashikawa - seed 3 rolls winter_crop none and fan_middle cleared at HEAD (recomputed from pyrand.rs's recipe, which reproduces Inashiro's, Mizuguchi's and Sawada's recorded rolls), as its 11-07 record has it; the untracked kashikawa.driver.json of today 09:50 reads barley, the builder's fix |
| 26, 187 | **DEFECT [hamlet engine, polder]** CONFIRMED | the dike band unbroken over the inlet and outfall: field/dike.rs builds `outer`/`inner` whole (rows cut only, 148), driver/polder.rs paints the band after the water (283-287). Pool: Kuwabata. No task found; T416's draw-order item is the sluice frame's, not the band's |
| 354 | **DEFECT [hamlet engine, polder]** CONFIRMED as drawn | the dike-pond's channels at field-ditch widths (field/polder.rs 517-596, 633-634) against 0018 drawing line 19; the claim cites 0019's "lattice of ditches", so the record's two pages need ruling. Pool: Kuwabata. No task found |
| 226, 269, 299, 363 | latent, NOT A HAMLET DEFECT | several fields: step taken from the first fan, hem facing field 1's brook, one unrounded channel start. fields_for gives 1 for any hamlet (20 households x 1.3 acres = 10.5 ha, cap 45-60 ha; field.rs 23-60). Belongs to the village tier (380). AS REPORTED |
| 191 | latent | two sluices fixed; right for a hamlet (0019 line 5) |
| 1 | latent | randbelow(0) shifts by 32 (pyrand.rs 225-233); every caller passes a constant or a table's length; no map effect |
| 75, 208 | latent, AS REPORTED | rest() stops after want x 8 tries (field/polder.rs 736-768), so a small rice polder could rest fewer than two; needs a roll to show; Kuwabata is a dike-pond block and rests none |
| 116 | AS REPORTED | a 1-2 row fan's row step; no hamlet's fan is that short |
| 118 | AS REPORTED | the last row's creep against the ring canal, a share of one gap; not seen on Kuwabata's crop |
| 387 | AS REPORTED | the wild-middle hem laid along the whole far flank: Inashiro's Rust drawing does hem the flank to the head, 12.75 acres held of 12.75; whether that is past 0006's toe ("two-thirds of the way down", a GUESS) is unruled |
| 388 | AS REPORTED | bands behind the seat after a push; Sawada's and Inashiro's drawings show a stepped outer edge, no gap seen at fit zoom |
| 74 | **DEFECT [record], minor** | CONFIRMED as drawn: the ring canal is four straight trunks with square corners (field/polder.rs 533-560) where 0019 line 23 says canals waver with rounded corners (a convention), and 0022 keeps the ring canal fixed at the block's edge; the pages disagree and the map reads fine, so the fix is the page's sentence |
| 76 | NOT NEEDED | the outfall runs through the foot's reed strip and off the map; its claim says so (field/polder.rs 701) |
| 190 | NOT NEEDED | FIXED: POND_FT's size is a stated GUESS (polder.rs 308) |
| 192 | NOT NEEDED | verified on Kuwabata: inlet and wild pond at the northwest corner, seat east |
| 200, 225 | NOT NEEDED | offtake_deg (35) and wander (10) are constants (driver.rs 37, 52), so the angle never goes negative |
| 62, 323 | NOT NEEDED | FIXED: resting plots taken out of the barley's ground (build.rs 535-550); states.rs 143 rests only a green plot |
| 34 | NOT NEEDED | FIXED: shrunk pushes each side in (landuse.rs 80-82) |
| 33 | NOT NEEDED | the hedge's 3 ft is drawn (driver/polder.rs 92-95, its own GUESS) |
| 111, 112, 237, 281, 260, 321, 210 | NOT NEEDED | verified in the callers: grave() only from the comb (build.rs 447), no pond on a dike-pond block (staged.rs 123-127), the polder's pond in a low plot (staged.rs 38-65) |
| 131 | NOT NEEDED | beads on the basin's own straight side (beans.rs 60-68) |
| 25 | NOT NEEDED | 0053 line 18's reach is the project's own figure and holds by construction (both flanks get a canal); no check, no claim - a label at most |
| 110 | NOT NEEDED | the hem is laid once a map (first field only) |
| 403 | NOT NEEDED | the hamlet's interactive page: carried by open 444 T42 |
| 63, 227, 300 | NOT NEEDED | FIXED: hem.rs 25 CLEAR_FT |
| 109, 142 | NOT NEEDED | FIXED: dry.rs 88 "a band's strips - GUESS ... rolled once a band" |
| 107, 138, 186, 230 | NOT NEEDED | FIXED: WIDTH_WAVES, GAP_HALF_FT and the offtake window are stated GUESSes (dike.rs 29, 34; channels.rs 138) |
| 59, 67, 71, 81, 99, 101, 113, 114, 132, 139, 141, 145, 169, 209, 238, 297, 316, 329, 182, 206 | NOT NEEDED | "not in the bundle" notes. Read at HEAD: BEAD_R_FT 1.5, RUN_BEADS (2, 4), FRY_SHARE 0.7, RICE_IN 10, TEA_FT (3.0, 7.5, 1.5), fence weir 1.5 ft, REST_PLOTS two to four, CAP_HA 45-60 - each as its claim says. 182 is not a finding |
| 3, 5, 7 | WORDING-FORMAT | three copies: water_frame.rs line 5 still says "the bearing and the fall rolled" |
| 22, 31, 37, 40, 236, 319, 383 | WORDING-FORMAT | a module claim inherited by plumbing units; labels only (383's shares are now claimed, water_frame.rs 116) |
| 28, 29, 30, 32, 36, 68, 80, 98, 102, 103, 104, 152, 164, 181, 185, 243, 268, 280, 348, 352, 353, 357, 379, 396 | WORDING-FORMAT / RESTATEMENT | claim or comment wording; spot-read still there: fan.rs 33 "index cell", polder.rs 60 "one in eight and one in six", states.rs 146 `field_stage._polder`, channels.rs 184 "every drawn canal", dry.rs 51 "over two miles", brook.rs 149 "0054's ten widths", polder.rs 635 "its own bank", sink/brook.rs 57 TWIN_RUN on the main page. None changes a map |
| 385 | RESEARCH QUESTION | the brook share as an exact-tie break; a reading of 0031's "otherwise equally good" |
| 450: 1 | WORDING-FORMAT | driver/spec.rs 236 still calls the 90-degree bound "0054's recorded deviation" |
| 450: 2 | NOT NEEDED | a bundle note; the claim stands a GUESS (spec.rs 218) |

## Table 3 - 449, rows naming rust/mode_a (45)

| rows | kind | note |
|---|---|---|
| 50, 55, 60 | **DEFECT [Mode A audit], latent** CONFIRMED | no bath pair in HIERARCHY (audit/program_rules.rs 478-490); 0116 drawing line 11 "No kitchen, bath or shrine hall out-sizes it" (a GUESS); the generator holds it. No pool sheet shows it; no task found |
| 27, 28 | NOT NEEDED | FIXED by 449 T172 (the splitter's raw strings) |
| 29, 30 | NOT NEEDED | FIXED: py.rs's module text names the arithmetic (lines 5-7) |
| 31 | WORDING-FORMAT | audit/sun.rs 446 still prints "(research homesteads 044)"; the figures rest on 0038 |
| 32 | WORDING-FORMAT | sun.rs 82, 91: each claim still says its account twice |
| 33 | NOT NEEDED | FIXED by T182 (relative path commands) |
| 34 | NOT NEEDED | FIXED: the claim says a court zone is not the open courtyard (program_rules.rs 314) |
| 35, 36 | WORDING-FORMAT | the report's printed bands (report.rs 100, 167, 216) unclaimed; 36's fire-gap text now reads 6-10 ft |
| 37, 38 | NOT NEEDED | FIXED by T176 (the audit's rules labeled) |
| 39 | NOT NEEDED | a bundle note |
| 40, 42, 44 | NOT NEEDED | FIXED by T182: gap_tag refuses a kura gap under 6 ft (checks/walls.rs 344-353) |
| 41, 43, 45 | NOT NEEDED | FIXED: GATE_MAX_FT names both 0093 and 0092 (shared.rs 71) |
| 51, 56, 61 | NOT NEEDED | FIXED by T182: RESIDENCE_PRIVIES = 2 (program_rules.rs 307, 340) |
| 64, 94 | NOT NEEDED | FIXED: "never under half the floor" (page/hits.rs 124) |
| 65, 66 | WORDING-FORMAT | hits.rs's claims: the box where it says polygon, the bead factor unnamed |
| 68, 95 | NOT NEEDED | FIXED: PER_HOUSEHOLD_F64 (place.rs 26-29, 339-345) |
| 70, 98, 99, 100 | NOT NEEDED | fixed by T188, then the placer rebuilt by T202: labels/hand_sheet/seat.rs and labels/obstacles.rs are gone; "never upside down" is claimed in caption_place/captions.rs 372-389. The rebuilt placer was not re-audited against these four here |
| 71, 107, 119, 120, 121, 122 | NOT NEEDED | moot: seat.rs, placer.rs and stroke_tests.rs deleted in T202's rebuild (T189-T195 fixed them first) |
| 130 | WORDING-FORMAT | compound/emit.rs's module claim inherited by plumbing; not re-read |
| 131 | NOT NEEDED | FIXED: "just inside the practice ground's edge" (compound/fixtures.rs 39) |
| 133 | NOT NEEDED | FIXED: the stale comment is gone from compound/parts.rs |
| 135 | NOT NEEDED | FIXED: RANKS holds the audit's eleven pairs and the bath (compound.rs 49-52) |

## Table 4 - 449, the other 52 rows

| rows | kind | note |
|---|---|---|
| 124 | **DEFECT [doc]** CONFIRMED (the first triage ruled row 210, the same doc, this way) | docs/building-programs.md 142 against pool/magistracies/county-magistracy-example/*.compound.json line 63; no 452 task carries it |
| 127, 128, 129 | RESTATEMENT, unsure | three copies: 0242 drawing line 27 still seats "an outline holding the others" beside the smallest box; the rebuilt placer names a holder on itself where it fits (caption_place/search.rs 408-429); the two may be the same rule for different sizes |
| 4 | NOT NEEDED | the winter crop's fixed odds: open 449 T416 (the builder's uncommitted build.rs adds barley_odds) |
| 7 | RESEARCH QUESTION | 0031's five lane shapes against the table's four; with row 23 |
| 3 | NOT NEEDED | FIXED: the brook's course is a GUESS that calls 0054 silent (driver.rs 42) |
| 10 | RESTATEMENT | 0019's page records no fringe width; the reeds were rewritten by 449 T236/T240/T250, their figures GUESSes in the code; not re-read on the page |
| 16 | NOT NEEDED | FIXED by 449 T261 (0031 records the fall into the wind) |
| 21, 25 | NOT NEEDED | bundle notes |
| 26 | tooling, AS REPORTED | make-only refuses `find -newer <gate binary>`; a guard misfire, worked round; not checked against 451's guard tasks |
| 46, 49, 54, 59, 79, 101, 102, 113, 118 | NOT NEEDED | moot: Python files deleted (no .py is left in the tree) |
| 47 | NOT NEEDED | FIXED in the Rust twin (T182) |
| 48 | NOT NEEDED | FIXED by T187 (lodging_entrances) |
| 53, 58, 63 | latent audit gap, part verified | three copies: the Rust twin still measures the first arch to `plan.bounds()` (audit/shared/grounds.rs 162-169) while its claim says "the ground's edge"; whether a plan's bounds are the shrine's ground or its wood was not read, so whether it passes a misplaced arch is AS REPORTED; the pool's shrine sheet passes |
| 52, 57, 62 | NOT NEEDED | FIXED by T182/T187 (0222's basin and 0196's well reconciled; 0222 line 15, 0196 lines 21-22) |
| 67 | NOT NEEDED | FIXED by T187: 0004 line 5 says declared households times five |
| 69 | WORDING-FORMAT | docs/buildings.md still reads "Nothing checks where a caption stands: the placer's unit tests do", and points at rust/mode_a/src/labels/ where the placer now lives in caption_place/ |
| 72, 73, 74, 112, 116, 117, 125 | RESTATEMENT | 0242's page silent on a rule the placer keeps (the long band, the fallback places, ties, the 500 figure); the placer was rebuilt by T202, so each needs reading against caption_place before any edit; not done here |
| 103, 104, 106, 115 | NOT NEEDED | FIXED: 0242 line 27 settles the turned square-cornered outline and the ellipse |
| 105, 108, 109, 110, 111, 114 | NOT NEEDED | moot: hand_sheet.py deleted and seat.rs rebuilt; 109-111 asked only for a citation of that line |
| 123 | RESTATEMENT | 0330's page no longer carries the measured tie note the claims quoted; the claims were in the deleted placer |
| 126 | NOT NEEDED | FIXED: 0223 line 8 "No fence is drawn along the approach" |
| 132 | NOT NEEDED | FIXED: 0090 line 19 records the middle gate beside the hall on generated plans |
| 134 | NOT NEEDED | not a fault: the Rust does roll with a port of `random.Random(zlib.crc32(...))` (compound/roll.rs 14-36) |

## What was and was not verified

- Read in code at HEAD: every row called CONFIRMED, FIXED or "verified" above, at the lines named.
- Seen on a drawing: rows 26/187, 354 and 74 on Kuwabata's untracked driver SVG of 11-22 17:01 (each also read in HEAD's code); Inashiro and Sawada at fit zoom for 387/388, rendered at 09:44 before the 09:50 regeneration.
- Not verified: the rows marked AS REPORTED; the wording rows beyond the spot-reads named; whether the rebuilt caption placer
  repeats the old placer's faults (449 rows 70, 98-100, 120).
- The split's counts are tallied from the tables: table 1 18 rows, table 2 107, table 3 45, table 4 52.
