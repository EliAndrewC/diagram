# Found-rows triage: 449 and 451's open findings, and the 30 true "outside the change" tasks

Read-only, clone diagram-backlog at HEAD 5eec349309 (2026-11-24); every tree check read HEAD's copy (`git show HEAD:`), so the
two builders' uncommitted edits are not in it. No make target was run. 452 has no found.jsonl.

## Summary

**Rule used for both jobs** (constitution XIV): DEFECT = a map or sheet that reads wrong, a check that passes bad work, or a
page / pop-up that tells its reader something false about the history or the drawing. RESTATEMENT = a claim, doc or why-text
that does not match while no reader is told anything false.

**Job 1 - 72 open rows read (449's 68 dated 11-20..23, 451's 4; 452 has no found.jsonl).**
- NOT NEEDED: **61**. 45 already fixed or moot at HEAD, 10 are copies of one row (the jizo's height, written 11 times), 4
  duplicate an open 452 task (195 -> T007, 198/199 -> T008, 207 -> T010), 2 say themselves "nothing to file" (200, 205).
- Still live: **11** = DEFECT 2, RESEARCH QUESTION 2, RESTATEMENT 3, WORDING/FORMAT 4.
- **Hamlet engine (rust/phases): 0 open defects.** Its rows are closed by done tasks: 137 (T240 measured the way out clear
  past every reed strip on Kuwabata and an oblique polder - no defect, claim restated, a cohort check added), 138 (T240/T250,
  bank bands read in driver/polder.rs), 150/151 (T293/T294, read in seat/margins.rs and driver.rs), 152 (T292).
- **Mode A code: 0 open defects that any drawn sheet shows; 1 latent audit gap.** Row 173, audit/armory.rs::drawn_end: an
  armory anywhere inside the office hall counts as its west or east end bay by the side of the hall's center it falls on
  (CONFIRMED, lines 89-101; no other audit found holding it to the end). No pool sheet draws one. 168-172 fixed or moot.
- The other open defect, 210, is a record one: the kitchen row says the door is recorded "often at the rear of the house",
  a frequency its cited pages do not give (AS REPORTED; still at docs/building-programs.md line 130).
- Unsure: 211 (which of two lines on the barracks' fifteen is right), 193 and 204 (closed as moot; see the table).

**Job 2 - the 30 true "outside the change" tasks: N = 19 defects, M = 11 not.**
- Hamlet engine 2: T293 (belt room past the field edge; its fix moved Kuwabata's belt 103 ft), T294 (band-end belt outside
  the kept ground).
- Mode A code 4: T271 (town card dropped farmhouses), T317 (card contradicts itself on a declared NW wind), T367 (armory
  always west - a knob not rolled, borderline), T397 (door_lane holds one end door - latent, no sheet declares two).
- Drawn Mode A sheets 8: T291, T300, T326, T339, T341, T359, T388, T408. Record states something false 5: T266, T310, T319,
  T344, T409.
- Not defects 11: research questions T296, T308, T327, T331, T358, T376, T381, T382, T401, T404; record item T323.
- So 6 of the 30 were code faults (2 hamlet; 4 Mode A, two of them latent or borderline), 13 sheet layout or record
  statements, 11 questions.

## Job 1 table

Status words: FIXED = the fault is gone at HEAD (what I read is named); DUP = a filed task carries it; CONFIRMED / AS REPORTED
as the brief defines them. Area in brackets.

| row | date | kind | note |
|---|---|---|---|
| 136 | 11-20 | NOT NEEDED [tooling] | bundle left out a cited page: T241 and T249, both done |
| 137 | 11-20 | NOT NEEDED [hamlet engine] | polder seat's track over the dike's reeds: T240 done - measured clear on Kuwabata and an oblique polder, ruled no defect, the claim restated and the cohort check `seat_walled_by_reeds` added (plan-done.md, T240's section) |
| 138 | 11-20 | NOT NEEDED [hamlet engine] | bank bands of denser reeds: T240/T250 done; FIXED, driver/polder.rs lines 102-105, 374-383 |
| 142 | 11-22 | NOT NEEDED [pop-up] | armory pop-up had no drawing page: T295 done; armory.md now has `Drawing:` 0093 |
| 143, 145 | 11-22 | NOT NEEDED [record] | 0090's hall 38 ft deep: T279 done; FIXED, 0090.drawing line 25 (118.5 by 38, others 28) |
| 144, 146 | 11-22 | NOT NEEDED [record] | 0116's Ochiba granary seat: T278 done; FIXED, 0116.drawing line 24 |
| 150 | 11-22 | NOT NEEDED [hamlet engine] | T293 done; FIXED, seat/margins.rs belt ground is the swept hull |
| 151 | 11-22 | NOT NEEDED [hamlet engine] | T294 done; FIXED, driver.rs::settlement_ground reaches the belt |
| 152 | 11-22 | NOT NEEDED [record] | 0072 did not name the polder: T292 done; FIXED, 0072.drawing line 11 |
| 153 | 11-22 | WORDING/FORMAT [record] | open: the gloss "en.wikipedia East Asian Monsoon gives ..." is still in 0072.drawing.notes, unlinked; no task found |
| 154 | 11-22 | NOT NEEDED [docs] | arch count off a map: T304 done; FIXED, building-programs.md line 173 |
| 155 | 11-22 | RESEARCH QUESTION [pop-up] | a stone jizo's real height; 0235 already records that no page gives it, so low value; near 452 T013 |
| 156-165 | 11-22 | NOT NEEDED | ten copies of row 155 |
| 166 | 11-22 | RESEARCH QUESTION [pop-up] | was a free-standing Edo stable's front closed; the pop-up already says "is not recorded" (line 8), low value |
| 167 | 11-22 | NOT NEEDED [docs] | gatekeepers' place: T308 done, then T398; the page side is 452 T016 |
| 168, 172 | 11-22 | NOT NEEDED [Mode A code] | moot: the granary has its own kind (types.json line 167), so HIERARCHY's "storehouse" pairs never rank it |
| 169, 171 | 11-22 | NOT NEEDED [Mode A code / record] | T321 done: the comparison is a plain less-than (program_rules.rs line 502) and 0116 no longer says "well below" |
| 170 | 11-22 | NOT NEEDED [Mode A code] | T317 done; FIXED, place.rs line 464 |
| 173 | 11-22 | **DEFECT [Mode A code], latent** | CONFIRMED: armory.rs::drawn_end reads only west or east of the hall's center, so a mid-hall or dais-band armory passes armory_site; no pool sheet draws one; no task found |
| 174 | 11-23 | NOT NEEDED [docs] | buildings.md's back row: FIXED, line 186 |
| 175, 176 | 11-23 | NOT NEEDED [record] | 0113 and the writing and binding rooms: FIXED, 0113.drawing line 11 (T330, T371) |
| 177 | 11-23 | NOT NEEDED [docs] | writing_rooms why: FIXED, line 119 now 6-13 by 10-20 ft, 100-210 sq ft |
| 178 | 11-23 | RESTATEMENT [docs] | open: the armory row's why names only the drawn hall size (line 123); the row itself says no map effect - could be settled |
| 179 | 11-23 | NOT NEEDED [record] | privy against a kura: T343 done; FIXED, 0116.drawing line 17 |
| 180 | 11-23 | NOT NEEDED [docs] | the 26-28 mat anchor: FIXED, lines 37 and 39 now call it a secondhand reading 0113 does not give |
| 181 | 11-23 | NOT NEEDED [docs] | study and day office optional: T347 done; line 39 "both items required" |
| 182, 183 | 11-23 | NOT NEEDED [Mode A code] | armory always west: T367 done; FIXED, armory.rs rolled_end |
| 184 | 11-23 | NOT NEEDED [docs] | dais optional: T368 done; line 121 no longer says optional |
| 185, 196 | 11-23 | NOT NEEDED [record / docs] | the shrine's tree: T369 done; FIXED, line 45 labels it GUESS |
| 186 | 11-23 | NOT NEEDED [record] | the second board: T370 done; FIXED, 0190.drawing lines 32-35 |
| 187, 192, 194, 197 | 11-23 | NOT NEEDED [record] | 0113's west-to-east row: FIXED, line 11 records Hayakawa's mirrored row (four copies of one finding) |
| 188, 191 | 11-23 | NOT NEEDED [record] | 0090's stale hall lengths: FIXED, line 25 |
| 189 | 11-23 | NOT NEEDED [record] | 0123's 50 by 36 granary: FIXED, now 50 by 26 |
| 190 | 11-23 | NOT NEEDED [docs] | divider gate behind or beside: FIXED, lines 32 and 101 give both |
| 193 | 11-23 | NOT NEEDED [tooling], unsure | "the official study's seat" claim neither owed nor checked: a later round judged it (T396 -> 452 T010, DRIFTED), so moot; I did not test the bundler |
| 195 | 11-23 | NOT NEEDED, DUP 452 T007 | the Kochi cart gate clause is still at buildings.md line 131 (CONFIRMED); a record defect, carried by T007 |
| 198, 199 | 11-23 | NOT NEEDED, DUP 452 T008 | inner_garden and latrine why-texts; the latrine's is still at line 137, the garden row (line 132) I did not compare; RESTATEMENT |
| 200 | 11-23 | NOT NEEDED | "nothing to file" |
| 201 | 11-23 | NOT NEEDED [record] | Yuki / Yūki: FIXED, the note's gloss now has the macron |
| 202 | 11-23 | NOT NEEDED [record] | the CLAIM-FROM-UNREAD sentence is gone from 0097's notes (T394's split) |
| 203 | 11-23 | NOT NEEDED [record] | FIXED, 0097 line 27 carries two footnotes |
| 204 | 11-23 | NOT NEEDED [record], unsure | the passage moved to 0334 with T394 "unchanged"; whether it now carries a footnote I did not verify, so this may still be a live WORDING/FORMAT row |
| 205 | 11-23 | NOT NEEDED | "I did not judge them" |
| 207 | 11-23 | NOT NEEDED, DUP 452 T010 | Knobs 5 option (c) against 0331 |
| 209 | 11-23 | NOT NEEDED [docs] | FIXED, buildings.md line 379 ("at the back of the office") |
| 210 | 11-23 | **DEFECT [record / pop-up], minor** | AS REPORTED: "often at the rear of the house" still at building-programs.md line 130; no task found |
| 211 | 11-23 | RESTATEMENT [docs], NOT CLASSIFIED with confidence | "the figure is this project's own" (line 127) against the staffing anchors' CANON (line 66); T320 set the fifteen apart from the anchor on purpose |
| 451-1 | 11-23 | WORDING/FORMAT [record] | a character check owed against an archived PDF (0009's two maff notes); no task found |
| 451-2 | 11-23 | WORDING/FORMAT [record] | 0009 introduces one survey twice; style only |
| 451-3 | 11-23 | WORDING/FORMAT [record] | en dash or hyphen in "pp. 80-261"; waits on the GM reading a scan |
| 451-4 | 11-24 | RESTATEMENT [record, hamlet] | CONFIRMED: 0031.drawing line 45 says "a table of its own" and gives none; plan.rs line 70 rolls small_irregular, medium, medium, large_block; fits T416 |

Counts: NOT NEEDED 61; DEFECT 2 (Mode A code 1, record 1; hamlet engine 0; sheets 0; tooling 0); RESEARCH QUESTION 2;
RESTATEMENT 3; WORDING/FORMAT 4. Total 72.

## Job 2 table (the audit's 30 verdict-C rows of mechanism OUT, filed 11-22..23)

How sure: "code read" = I read the fix at HEAD; otherwise the class rests on the task line and its landing commit's words.

| task | class | area | note |
|---|---|---|---|
| T293 | DEFECT | hamlet engine | belt room past the field edge on an oblique wind; code read; plan-done.md records Kuwabata's belt moved 103 ft north by the fix |
| T294 | DEFECT | hamlet engine | band-end belt outside the kept ground; code read; same caveat |
| T271 | DEFECT | Mode A code | town place card left out its farmhouses against 0004 |
| T317 | DEFECT | Mode A code | card says a NW wind departs from the NW wind; code read; only on a sheet declaring NW |
| T367 | DEFECT, borderline | Mode A code | armory always in the west bay; each sheet alone was attested, the fault is the knob not rolled |
| T397 | DEFECT, latent | Mode A code | door_lane took the first end door only; no pool sheet declares two |
| T291 | DEFECT, unsure | sheet | county hall with no formal entrance facing the gate ("drawn or recorded as a deviation" - I did not check which) |
| T300 | DEFECT | sheet | open band, the round trip's hall missing rooms, a bare strip |
| T326 | DEFECT | sheet | round trip: clerks' room as its own building, no rear door, no postern |
| T339 | DEFECT | sheet | Ubame's household door onto the alley; Ochiba's porch with no room behind |
| T341 | DEFECT, unsure | sheet | cart gates wider than the side gate band, a band T340 had recorded hours before; the gates were narrowed |
| T359 | DEFECT | sheet (and Mode A engine) | workshop drawn closed, with the shrine's mark |
| T388 | DEFECT | sheet (fixed in code) | stables' only door into the grooms' room |
| T408 | DEFECT | sheet | Ubame's garden bed 1.3 ft off the veranda; open as 452 T006 |
| T266 | DEFECT | record | 0222's notes and drawing page said what its corrected findings no longer did |
| T310 | DEFECT | record | 0113's "no page gives a hall's length" against 0104's measured hall |
| T319 | DEFECT | record | 0123's "faced south, by regulation" - the check found the page says otherwise; restated |
| T344 | DEFECT | record | one instance stated as the rule, two unsupported registry facts |
| T409 | DEFECT | pop-up | the official study's About stated a guess as history |
| T296 | RESEARCH QUESTION | pop-up | what the gate was built of, how many gatekeepers |
| T308 | RESEARCH QUESTION / restatement | docs | the gatekeepers' place as a knob |
| T327 | RESEARCH QUESTION | pop-up | what the road's banding stands for |
| T331 | RESEARCH QUESTION | sheet | privy 0.5 ft off the granary; settled by a GUESS recorded on 0116, the sheet kept |
| T358 | RESEARCH QUESTION | record | did a jin'ya hall keep a corridor |
| T376 | RESEARCH QUESTION | pop-ups | pond banks, kitchen walls |
| T381 | RESEARCH QUESTION | record | the official study's seat |
| T382 | RESEARCH QUESTION | record | a waiting shed by the hearing court |
| T401 | RESEARCH QUESTION | sheet | the stables' ridge: the search pass found the form "as drawn" and shrank no depth (emit.rs STABLE_DEPTHS comment, commit 03cc1514d1); follow-up 452 T005 |
| T404 | RESEARCH QUESTION / detail | sheet | the stalls' rear doors; open as 452 T004 |
| T323 | RECORD ITEM | record | two absence notes that may describe unread pages |

N = 19 (hamlet engine 2, Mode A code 4, sheets 8, record 5). M = 11 (research questions 10, record item 1).
Differences from the audit's kind column: T319 R -> record defect (its check found the sentence wrong); T331 and T401 Ds ->
research questions (each was a search pass, T331 ending in a recorded guess with the sheet kept); T323 Dr -> record item.

Against the list the GM was given on 2026-11-23 (request.md: 11 map or tool defects, three of them among these 30): T388
and T397 stand as defects (T397 latent); T401 turned out a question whose search pass found the sheet right as drawn. T398,
on that list, was ruled a choice of form by the arbiter and is not among the 30.

## Not covered

- 115 older open rows in 449's found.jsonl (2026-11-08..19, all but one impl-drift), 18 naming rust/phases files and 39
  rust/mode_a files, were not triaged. They bear on "is the hamlet code sound" as much as the 68 do.
- Two open 449 tasks are hamlet-engine items: T415 (a linear hamlet rolls a shelter belt against 0031's drawing page) and
  T416 (water flow DRIFTED plus three CANNOT-TELL). 451-4 fits T416.
