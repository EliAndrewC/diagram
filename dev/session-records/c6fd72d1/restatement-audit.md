# Restatement audit: do the open restatements need any change at all?

Read-only, clone diagram-backlog at HEAD 7dbcd93ec1 (2026-11-24). Every doc, page, claim and code line was read from HEAD's
copy (`git archive HEAD` into /tmp/rh), so the builder's uncommitted edits in rust/phases and 449's files are not judged.
Run: `make claims-report`, `make claims-owed`, `make gm-review` (read-only). No generator or audit was run, so "what a sheet
shows" is read from the sheet's svg, notes and spec, not re-measured by a tool.

## Summary

| group | items | REAL, small | ALREADY FIXED | FINE | DEFECT | DECISION |
|---|---|---|---|---|---|---|
| 1. Feature 452's restatement tasks (T007-T017, T21, T22) | 13 | 11 | 0 whole (3 sub-items) | 2 | 0 | 0 |
| 2. `make claims-report` findings | 17 | 9 | 4 | 3 | 0 | 1 |
| 2b. GM-review "known drifts" (405: 1, 417: 5 - six, not three) | 6 | 0 | 0 | 6 (moot) | 0 | 0 |
| 3. Found rows classed RESTATEMENT (444: 3, 449: 17, 451: 1) | 21 | 5 | 4 | 12 | 0 | 0 |

**The hypothesis holds for the found rows and the claims report, not for 452's tasks.**
- Need nothing: 16 of 21 found rows, all six GM-review rows (deleted Python), 7 of 17 claims-report findings.
- 452's tasks: 11 of 13 name a sentence untrue of its page or sheet today - one-line edits, no map changes.
- **No item is a wrong outcome on a map or sheet.** The one arguable case is T012 (below).
- The error runs the other way: **all six "known (417 T33) ... fix: code" drifts are mislabeled as code fixes** (table below).
- **T012 and T013 were ruled to change a DRAWING; the record does not support either.** T013 has no drawing: no sheet draws a
  burial ground. T012's shrines are drawn 77 to 780 sq ft with doors, the "hall" of 0220's sentence, not its stone-or-wood
  hokora; a reviewer applying the knob rule strictly could still ask for one DEVIATION line on 0218's drawing page.

**The REAL edits, deduplicated (22)**
- `docs/buildings.md` (8): l.131, l.162, l.205 + l.222, l.152 + l.188, l.327 + l.343, l.334, l.347, l.313.
- `docs/building-programs.md` (3): l.77, l.137 + l.274, l.142.
- `pool/magistracies/` (2): county example's compound.json l.24-25 and notes l.108, 113, 156, 160; round-trip notes l.45.
- `rust/` claims (5): sun.rs l.82, l.91; compound.rs l.200; phases driver/plan.rs l.97; phases field/channels.rs l.191.
- Research pages, a page session each (4): 0093, 0090, 0038 and 0058's drawing pages. 0053's waits on a seed count.

**One decision for the GM** (canon): the city card follows his feature-156 words (a city's ~3,000 "includes samurai country
estates"); `l7r.md` l.177 tallies those estates under the nearest village district, and 0001 says "within the walls".

**What produced the FINE and ALREADY FIXED ones - all five still run; 452's items were filed 11-23/24, after XIV v2.36.0, so an old filter does not explain them**
1. impl-drift judges from its bundle only, so "the cited pages do not say it" is filed where the record does (T22, place.rs).
2. impl-drift.md l.123-133 files every OUTSIDE THE CHANGE note as a task or found row, page-silent ones included.
3. The filed-departure rule (impl-drift.md l.80) forbids re-judging a "known (417 T33)" claim, so `fix: code` outlived the fix.
4. The index keeps a verdict after its claim is corrected (the shrine-tree trio, palette.rs; `owed 0`).
5. Dated log entries are judged as present-tense statements (T015).

## The six "known (417 T33)" drifts, plainly

417 T33 is still an open task in a Draft feature whose Python is deleted; nothing else carries these fixes.

| drift | a wrong outcome sitting accepted? | what fixing it touches |
|---|---|---|
| genkan porch size | NO - already fixed. `layout.rs` l.66 `GENKAN = (12.0, 9.0)`; 0104.drawing: "the porch is drawn ... about 12 by 9 ft, the one shikidai found measured". Ochiba's 10 by 6 ft is the page's recorded GUESS | docs/buildings.md l.205 (claim) and l.222 ("~40x14") only |
| tax archive strongroom role | NO ink anywhere: one kura captioned "tax archive" is drawn. The role is one doc sentence (l.188 "doubles as the strongroom for ... the coin the county holds") and an Ubame svg comment (l.181). It is an unlabeled guess, and 0100 has two offices keeping coin elsewhere | label it a GUESS or cut the clause; no code exists to fix |
| arch posts | NO. 1.2 ft against one measured 1.5 ft post is 3.6 px against 4.5 px; no reader sees it, and one measured post is not a range | nothing a reader needs. The claim at docs/buildings.md l.330 is true as written; relabeling the 1.2 ft a GUESS only takes it off the report and out of 417 T33 |
| kitchen garden siting | NO - already fixed on the one sheet. Hoshigaoka's notes l.46: moved "to the open ground below the forecourt ... where it gets 9.5" hours (feature 283, 2026-09-28); `garden_sun` holds it. No generator draws a country shrine | docs/buildings.md l.327 (claim) and l.343 ("the kitchen garden and the privy at its back corner") |
| small roofed thing height / area | NO. Casting a privy or hokora from 6 ft is the better outcome; 20 ft would refuse good sheets. The page (0038.drawing, "The six-hour check casts each shadow at the least height ...": "A building at the farmhouse ridge's 20 ft") lacks the small class | one bullet on 0038.drawing (a page session), then sun.rs l.82 and l.91 -> `GUESS <that page>` |
| notice board (also listed "known", not in the brief) | NO. 40 ft was chosen in feature 372 so a board across the road can face its gate. 0090.drawing's "within about 15 ft" is the project's own stale figure | 0090.drawing's notice-board bullet and its checklist item 4 (a page session), then compound.rs l.200 |

## Per-item table

Standard: constitution XIV v2.36.0, the root CLAUDE.md research bullets, impl-drift.md's verdicts. "REAL" means a reader is
told something untrue of the page, the sheet or the code. Confidence is CONFIRMED by reading unless marked.

### Group 1 - feature 452's restatement tasks

| task (from) | filed by | verdict | evidence at HEAD and the one-line edit |
|---|---|---|---|
| T007 (449 T374; found 195) | impl-drift 11-23 | REAL, small | docs/buildings.md l.131 still: "a cart gate is named as its own form only at a Kochi domain residence of about 1790-1800 and at Himeji castle"; 0082.drawing ("How wide is a cart gate?") names Himeji's Kurumamon alone. Edit: "only at Himeji castle (its Kurumamon), unsized" |
| T008 (449 T390; found 198, 199) | impl-drift 11-23 | half ALREADY FIXED, half REAL | Garden row l.132 now: "Both forms are taken as accurate ... each plan takes one of the two" - fixed. Latrine rows l.137 and l.274 still: "so it takes the smallest farm privy counted"; 0101.drawing ("A privy is drawn 5 ft square"): "No source we read gives a privy's size; this is this project's choice". Edit: "so 5 ft square is this project's choice" |
| T009 (449 T393) | session 11-23 | REAL, small (no map reader) | compound.json l.24: "research-pass 2026-11-23 - not yet on a page" - false, 0331 and 0097.drawing hold Sakai's doshin dwelling; l.25 and notes l.108, 113, 160 and l.156 likewise. pool/*.json is gated engine code, so this lands through the gate with no drawing change |
| T010 (449 T396; found 207) | impl-drift 11-23 | 2 of 3 ALREADY FIXED, 1 REAL | "the official study's seat" (l.75) and "office hall" (buildings.md l.142) now carry the mirror and the GUESS and are IN-STEP in the index. Staff housing knob l.77 still cites 0097 alone; 0097 ("Where an office's staff lived ... is at Where an office's staff lived") sends the question to 0331. Edit: cite 0331 for the three forms, 0097 for the rowhouse. Option (c) is supported: 0331 has Sano's staff in the towns and Omori's official in a house of his own |
| T011 (449 T411) | impl-drift 11-23 | REAL, small | l.334 "0235.drawing: rows of ~2x1 ft markers"; the page: "The markers are a map drawing convention", 9 ft spacing, no size. Edit: `CONVENTION <0235.drawing>: rows of markers; ~2 by 1 ft a GUESS` |
| T012 (449 T412) | impl-drift 11-23 | REAL, small - the DRAWING ruling is NOT supported | 0218 gives an office's shrine no material. 0220 ("Did a household shrine have an arch?"): "Most household guardian shrines are small shrines of stone or wood; one that is carefully kept may be given a hall the size of a subsidiary shrine". Our compound shrines are that hall: drawn 11 x 7 ft (Hayakawa), 18 x 14 (county), 24.7 x 17.3 (Ubame) and 30 x 26 (Ochiba), with doors, altars and arches, in a 40-1,150 sq ft band. A stone hokora is the sentence's other, smaller thing, not a second material for this one. Wood is attested and no sheet reads wrong. Edit l.313: "small shrine - 0218; its wooden hall a GUESS (0218 gives no material)". No research pass or five boxes needed. A reviewer applying the knob rule strictly could ask for a recorded DEVIATION on 0218.drawing instead - also one line |
| T013 (449 T413) | impl-drift 11-23 | REAL, small - there is NO drawing to change | 0235.drawing does put "a taller memorial stone or two" and "six small stone jizo ... at the entrance". But no Mode A sheet draws a burial ground (Hoshigaoka's is "430 ft west, outside the frame"; no `data-kind="burial ground"` in pool/; the legacy pool is Mode B maps, not this procedure's) and no Mode A code draws one. Edit l.347: add the memorial stones and the six jizo to the Grave markers bullet. The five boxes are already answered by 0235 |
| T014 (449 T414) | impl-drift 11-24 | REAL, small | Measured from the county spec: barracks `w 22, h 60`; junior retainers' quarters `w 48, h 24`, as 0097.drawing says. l.162 "the county example's range 24 x 67 ft" is stale. Edit: "the county example's barracks 22 x 60 ft" |
| T015 (449 T380) | building-review 11-23 | mostly FINE; 1 REAL, small | Hayakawa T276/T299/T312 and round-trip l.100-118 are dated log entries, true when written, with the T367 entry above them; several already carry "since mirrored" / "superseded by the T392 entry". Hayakawa's svg comment l.690 already says "Since 449 T367 rolled the armory into the east end bay". Ubame's "room behind the dais" is a 2 ft nit. The workshop colonnade is labeled a GUESS at docs/buildings.md l.321. REAL: round-trip notes l.45 "Coverage 36%, perimeter-hugging 61%" in a present-tense Result paragraph, against l.129 "coverage 33%" |
| T016 (449 T406) | session 11-23 | REAL, small (a page session) | 0093.drawing ("Where the gatekeepers sit follows the gate's form"): "a one-bay gate has a gatekeepers' house of its own beside it"; layout.rs l.673 rolls `["beside the gate", "behind the gate"]`. A reader of the page is told one seat where the maps roll two |
| T017 (449 T410) | record-format 11-24, arbiter accepted | FINE - no change | Nothing false: an office name in a translated quotation has no gloss, and 0097 ("Who lived in the Shibata domain's foot soldiers' row?") already says "rope men". A gloss is optional research with five boxes for a post no map draws |
| T21 (found 124) | impl-drift 11-19 | REAL, small | l.142: "a generated plan gives it the front row's room left beside the reception"; the county spec draws `"guest house", "kind": "guest quarters", "w": 40, "h": 42`, a building of its own. Edit: "a generated plan draws the size its spec gives (the county example a guest house of 40 by 42 ft)" |
| T22 (found 210) | impl-drift 11-23 | FINE - no change | The sentence is the record's own: 0107 "The kitchen door often stood at the back of the house", JAANUS verbatim "the kitchen entry often tucked away at the rear". The finding looked only at the pages the section cites (0104, 0091). Optional: add 0107 to the kitchen claim |

Not restatements, left alone: T001-T006 (research and drawing), T18-T20 (latent audit gaps).

### Group 2 - `make claims-report`'s 17 findings

| claim | verdict in the report (date) | my verdict | evidence and edit |
|---|---|---|---|
| building-programs.md staff housing knob | MISLABELED 11-24 | REAL, small | = T010 |
| buildings.md genkan porch size | DRIFTED known 11-22 | ALREADY FIXED in code; REAL doc edit | see the six-drifts table |
| buildings.md tax archive strongroom role | DRIFTED known 11-23 | REAL, small (doc; no ink) | see above |
| buildings.md arch dimensions | DRIFTED known 11-23 | FINE - no change | see above: nothing untrue is told and nothing is visible |
| buildings.md grave markers | MISLABELED 11-23 | REAL, small | = T011 |
| buildings.md kitchen garden at the dwelling | DRIFTED known 11-23 | ALREADY FIXED on the sheet; REAL doc edit | see above |
| buildings.md modest compound shrine | MISLABELED 11-23 | REAL, small | = T012 |
| palette.rs ROLE_NAMES the palette's table | MISLABELED 11-17 | ALREADY FIXED | palette.rs l.42-44 now carry "the tax archive drawn as a kura - 0100.drawing", "a storehouse drawn as a kura - GUESS", "the granary's two forms - 0098.drawing" - the three claims the finding asked for, each IN-STEP in the index dated 11-18, a day after this verdict |
| grounds.rs shrine_tree | MISLABELED 11-23 | ALREADY FIXED | l.494 now "GUESS research/questions/0218-...drawing.html#shrine-tree"; the index still holds the old text, and the report says `owed 0` |
| fixtures.rs tree | MISLABELED 11-23 | ALREADY FIXED | l.201 now "GUESS ...#shrine-tree" |
| layout.rs TREE_ROOM | MISLABELED 11-23 | ALREADY FIXED | l.71 now "GUESS ...#shrine-tree" |
| sun.rs SMALL_BUILDING_FT | DRIFTED known 11-17 | REAL, small (page + claim) | see above |
| sun.rs SMALL_BUILDING_SQFT | DRIFTED known 11-17 | REAL, small (page + claim) | see above |
| compound.rs NOTICE_BOARD_MAX_FT | DRIFTED known 11-17 | REAL, small (page + claim) | see above |
| place.rs a city's figure takes in its samurai country estates | MISLABELED 11-18 | NEEDS A DECISION (canon); the claim itself is fine | CANON is the right label: 156's request.md, the GM's own words, "a provincial city has a population of ~3,000 ... this includes samurai country estates". But l7r.md l.177 says "samurai country estates, get tallied under the nearest village district", and 0001 ("A provincial city is a governor's seat ...") says the figure "counts only those living within the walls". Which holds is his to say; then 0001's sentence or the card's parenthesis is restated. 156 T52 already made the card hedge ("this map does not yet state that larger number"), and docs/gm-rulings.md has nothing on it |
| place.rs what each tier is | CANNOT-TELL 11-18 | FINE - no change | place.json's four tier texts read against 0001: hamlet no headman, no shrine, 1,296 / 216 / 40%; village the headman, shrine and tax-free plot; town 238 households, two in three farming, the lowest tier with samurai; city the governor's seat, no farmers. All match |
| hand.rs run a sheet with untagged ink fails | MISLABELED 11-18 | FINE - no change | CONVENTION against NONE on a validation exit code: a taxonomy point, nothing untrue, no reader affected. A one-word relabel if wanted |

The nine UNRESEARCHED claims the report lists are open research, not restatements, and were not judged.

### Group 2b - the GM-review rows (make gm-review: 405 row 12; 417 rows 20-24)

All six name units under `l7r/diagram/hamletgen/ways/` (`geom.py`, `settle/ends.py`, `tree.py`, `lay.py`). That tree is
deleted (l7r/diagram holds only buildings, interactive, tools), and rust/phases has no ways module and no hit for "doubled
tail", "doubled band", "one network" or `off_the_needle`. Verdict: FINE - moot, nothing to change. The lane rules they
describe are carried by 417's open T06, T16 and T32 for when lanes are ported.

### Group 3 - found rows classed RESTATEMENT

| row | filed | verdict | evidence |
|---|---|---|---|
| 444 #220, #308 (one finding twice) | impl-drift 11-01 | REAL, small (claim) + a count owed before the page moves | 0053.drawing ("The head race forks into two supply canals"): "On every hamlet map the second canal feeds at least one delivery ditch". channels.rs l.191 cites that page for "half way, where its fractions leave it no offtake", which the page does not say; its sibling l.190 is correctly a GUESS. Edit: l.191 -> `GUESS: <page> silent on a second canal with no offtake; drawn half way`. Whether any map draws that case was not measured: count the seeds whose canal B gets no offtake; if any, that bullet's "every" is false and takes one clause |
| 444 #395 | impl-drift 11-04 | REAL, small (page) - AS REPORTED | 0058.drawing ("A well is kept off the ground below the fields' lowest point"): "so that strip is farmed and built on"; margins.rs l.418, l.485 refuse a seat or anchor on the toe. I did not confirm that `toe_band` covers the tucked 90 ft strip. Edit: "so that strip is farmed, and a well may stand on it" |
| 449 #10 | impl-drift 11-08 | FINE - no change | 0019.drawing is silent on the fringe's width, and nothing it says is false. Not re-read against the builder's polder work |
| 449 #22 | impl-drift 11-08 | REAL, small (claim) | driver/plan.rs l.97: "GUESS: the page names no crop on the dikes" - untrue of the record (0019.drawing "grew vegetables under the mulberry"; 0038.drawing's two canopy-tree bullets name mulberry, tea and fruit trees on a dike-pond's banks). Edit: "the pages name mulberry, tea and fruit on the banks; the shares a GUESS" |
| 449 #72, #73, #74, #125 | impl-drift 11-18/19 | FINE - moot | Each names a rule of the placer T202 deleted (the elongated band, `extended_cands`, the tie to a neighbor, the 500 figure); none is in rust/mode_a/src/caption_place/ at HEAD |
| 449 #112, #116 | impl-drift 11-18 | ALREADY FIXED | 0242.drawing ("A turned outline whose every corner is square ...") now: "A block named among loose parts, or an outline holding the others, is seated beside the smallest box holding them all, turned to that block's or outline's angle, or level where that outline has no direction of its own" |
| 449 #117, #123 | impl-drift 11-18/19 | ALREADY FIXED | 0330.drawing ("Where two drawn parts stand exactly as near"): "the leader goes to a closed outline before a stroke, and to the wider of two strokes ... between two like parts equally near, the one drawn first"; leader.rs l.300 claims exactly that |
| 449 #127, #128, #129 (one finding three times) | impl-drift 11-19 | FINE - no change (medium confidence) | 0242.drawing's rule for a caption's place already says "a feature large enough to hold its name is named on itself"; the turned-outline bullet's "beside the smallest box" is the case where it is not. The placer tries on the holder first (search.rs `on_it`), then beside. Not traced through every branch |
| 449 #178 | impl-drift 11-23 | FINE - no change | The armory row's why gives the drawn hall size; the row itself says "effect: none on the map". Nothing false |
| 449 #211 | impl-drift 11-23 | FINE - no change (medium confidence) | l.127's "the figure is this project's own" is about how many men the barracks LODGES, which no page gives; the CANON anchor (l.66) is the staff of about fifteen samurai. Two different statements |
| 449 #124 | impl-drift 11-19 | REAL, small | = T21 |
| 449 #210 | impl-drift 11-23 | FINE - no change | = T22 |
| 451 #4 | impl-drift 11-24 | FINE - no change | 0031.drawing (the village rule) "each from a table of its own" is true. The table's sizes and weights are labeled at the code since T415: driver/plan.rs l.17 "`plot_size`'s three sizes and their weights" a GUESS, and lattice.rs cites 0005.drawing's 40 to 60 ft |

Rows 195, 198, 199 and 207 are settled duplicates of T007, T008 and T010 and are counted there.

## What was not verified

- No audit or generator was run: the county's 22 x 60 ft barracks is its spec's figure, and Hoshigaoka's 9.5 hours is its notes'.
- 444 #395's toe band and 449 #127-129's holder branch were not traced to the end.
- 444 #220/#308: whether any hamlet draws a second canal with no ditch needs a seed count.
- 449 #10 was not re-read against the builder's uncommitted polder edits.
- The sibling agent's WORDING rows were not read.
