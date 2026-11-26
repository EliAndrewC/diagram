# P1 cascade (dike-pond pages 0018, 0019, 0022; 449 T420, T425) - clone diagram-backlog at 8c37200fa9, 2026-11-24

Dispatch route: no Workflow tool in this agent's tool list (ToolSearch select:Workflow: none; the check-wave skill only names
it). Arbiters and impl-drift went as single Agent calls (the 4th impl-drift after the wave guard refused it); the pop-up checks
went as BATCHED bundles, one agent per check type, as the batch guard required.

## Start

- `make record-owed UNANSWERED=1`: 90 units = 87 pop-up units (modal-accuracy 20, modal-gaps 20, modal-references 20,
  modal-depiction 27) + 3 third-round units.
- `make claims-owed`: 21 claims "rests changed" in 4 files (straight to impl-drift), 55 owed a triage. Also one `claims-label`
  notice: `rust/phases/src/field/ponds.rs::rounded#the bank's inset` - a bare GUESS whose account names 0018 (a rust/ edit: T420's).
- The 21 direct claims against the brief's re-check list: 11 predicted (check.rs RING_CANAL; field/polder.rs DRIFT_SHARE,
  MOSAIC_WAVES, RING_FT, Warp.at#the mosaic's drift, ditches#the dike-pond's interior ditches, ditches#the ring canal,
  polder#never uniform rectangles, polder#the feeder, polder#the ring canal's place, row_ditches#the lattice both ways) and 10 the
  brief expected to CLEAR (check.rs ground_on_polder, polder_checks#the settlement's ground; plan.rs POLDERS, POND_LAYOUTS,
  plan#no brook knobs; driver/polder.rs roll_polder#the village off, stage_polder; field/polder.rs plots#every pond four-sided,
  polder#the chessboard, polder#two sluices).
- 8 predicted re-checks sit in the TRIAGE pool: ponds.rs rounded#rounded corners, rounded#the bank's inset, LEAST_SHARE#the least
  pond; landuse.rs REACH_FT#the rounding; driver/polder.rs sluice_channel, stage_waterward#the reed strips, roll_polder#the strips
  after the seat; waterward.rs fringe.
- NOT OWED AT ALL: `field/polder.rs::ditches#the widths` - the claim that carries the 1.2-2.5 ft delivery width - cites 0068 only,
  so 0018's new "about 6 to 8 ft" item cannot reach it through the claims index.

## Stage 1 - the three third-round units (round-arbiter, 3 dispatches, none of the checks run)

`make arbiter-bundle BATCH=1`: "no round trigger is owed a ruling". Named @3, each trigger was refused: "the counter holds 1
round(s)" though each check had run TWO rounds today in P1's sessions (the same per-feature counter gap as P7's record-format:0097);
the bundles were built at `round:<check>|q:<NNNN>@2`. `BATCH=1 TRIGGERS="a,b,c"` does not split on commas (it read the list as one
trigger): three single bundles.

| trigger | ruling | effect |
|---|---|---|
| round:record-format\|q:0018@2 | ACCEPT | unit answered; two reworded phrases, both ordinary English, round 2 was clean |
| round:translation-check\|q:0018@2 (chen-2021-foshan-jitang-2) | ACCEPT | unit answered; the EDIT moved the English toward the check's own suggestion |
| round:translation-check\|q:0019@2 (wuhurec-wanchun) | ACCEPT | unit answered; a glossary-term swap, not a translation change |

Cost: 35k + 35k + 55k subagent tokens, 69 s / 88 s / 183 s. After: 87 units unanswered (the pop-ups only).

Follow-ups the rulings named, and what was done:
- 0018 note `wuhurec-wanchun-5` "the fiscal commissioner of Jiangdong" -> "transport commissioner" (the 0019 ruling's route was
  "in the record-format:0018 third round", which the other ruling then closed). MEASURED, then put back by the inverse edit: the
  one-phrase hand edit re-owed three units (quote-check:0018#wuhurec-wanchun-5, record-format:0018,
  translation-check:0018#wuhurec-wanchun-5), each a third round, i.e. three more arbiter dispatches for a synonym. Left OPEN: the
  same office is named two ways on 0018 and 0019.
- "Each square qing" may take the Qing-dynasty tooltip (glossary case-matching): not filed here; OPEN for the parent.
- 0019 drawing's "rebuilt in 1061" against 0018's "whose rebuilding was pressed for in 1061": quote-check's, untouched.

## Stage 2 - claims

- `make claims-triage`: TOOL-CLEARED 55 of 55 ("a page each cites moved and no block it rests on did"); 0 to the claims-triage
  agent (never dispatched). This includes all 8 claims the brief said SHOULD re-check from the triage pool (ponds.rs
  rounded#rounded corners, rounded#the bank's inset, LEAST_SHARE#the least pond; landuse.rs REACH_FT#the rounding; driver/polder.rs
  sluice_channel, stage_waterward#the reed strips, roll_polder#the strips after the seat; waterward.rs fringe).
- impl-drift on the 21 "rests changed" claims, 4 bundles by file (UNITS=; `MODULE=` refuses a file with unowed claims unless
  REASON=). The 4th launch was refused by the wave guard (no Workflow tool here); it went out after the first returned.

| bundle | claims | verdicts | tokens / wall |
|---|---|---|---|
| driver/check.rs | 3 | IN-STEP 3 | 28k / 22 s |
| driver/plan.rs | 3 | IN-STEP 2, DRIFTED 1 (fix: claim) | 24k / 29 s |
| driver/polder.rs | 2 | IN-STEP 2 | 28k / 18 s |
| field/polder.rs | 13 | IN-STEP 13 | 44k / 49 s |

The one non-IN-STEP verdict, verbatim:
`VERDICT rust/phases/src/driver/plan.rs::POLDERS#the polder archetypes DRIFTED - the constant puts two kinds of field under
"polder": the rice polder and the dike-pond block. The page treats both as diked against the water ("a rice polder and a dike-pond
block lay out their insides differently"). But the claim calls the class "a surveyed grid", and the page draws the dike-pond as "a
mosaic or as a chessboard of ponds", not a grid. fix: claim (e.g. "the rice polder and the dike-pond block, both diked out of
standing water"); effect: none [§3, §22, §23, §24]` - a rust/ doc-comment restatement: left for T420's builder.

Notes from the field/polder.rs reply: `polder#the feeder` "says the page is silent on the feeder's course, but §18 now draws it
straight and records that as a GUESS. That still counts as IN-STEP." (the claim's wording is stale; a restatement for T420's
builder). `make claims-checked` printed, recording `polder#never uniform rectangles`: "rests on 0019-...drawing.html, a page it
does not cite - dropped" (the verdict's [§24] is 0019's; the claim cites 0022; recorded all the same, 13 of 13).

All four `make claims-checked` exited 0; no T218 hold. After: `make claims-owed`: no claim is owed.

THE T420 RESULT: NO claim came back DRIFTED fix: code on the channel widths. `ditches#the dike-pond's interior ditches` and
`row_ditches#the lattice both ways` were judged against 0019's drawing page alone (the page they cite), where no width is stated;
both IN-STEP. The width item lives on 0018's drawing page, which neither cites, and the claim that carries the figures
(`ditches#the widths`: "a delivery 2.5 to 1.2 down each column") cites 0068 only and was never owed. So a SUPPLEMENTARY re-check
was run, outside what the tooling owed: `make claims-bundle UNITS="<those three>" REASON=... PAGES=<0018 drawing page>` (see below).

### The supplementary width re-check (NOT owed by the tooling; 3 claims, 35k tokens, 58 s; recorded, exit 0)

DRIFTED fix: code - for T420's builder, verbatim:
`VERDICT rust/phases/src/field/polder.rs::ditches#the widths DRIFTED - for a rice polder the widths match 0068's table and caps
(4.5->1.5, 4.0->1.5, a delivery 2.5->1.2 with its head capped at 0.8 of the local width, a drain 1.2->5.5). But `ditches` takes no
field form, so a dike-pond block's column ditches get the same delivery rung, `head = 2.5_f64.min(0.8 * local)` tapering to
`1.2_f64.min(head)`, which is 1.2 to 2.5 ft. 0018 says a canal between ponds is "About 6 to 8 ft, a GUESS", "drawn as the
waterways the ponds lie among, not as field ditches", and 0019 calls the channels between ponds "the creeks that boats used". The
row ditches, set at 0.75 of this head, follow it down to 0.9-1.9 ft (drawn at the 1.5 ft floor at the low end); fix: code (a
dike-pond block's column and row channels drawn at 6 to 8 ft, with the delivery ladder kept for the rice polder); effect: map - on
Kuwabata the channels between the ponds read as hairline field ditches 1.2-2.5 ft wide in a 22 ft gap, not the 6-8 ft creeks the
drawing page records, and the 0018 §96 decision is contradicted`

OUTSIDE THE CHANGE (filed by `make claims-checked` to specs/451 found.jsonl, "filed, not fixed"):
`row_ditches`, claim `the row ditch's width` - its width is 0068's sub-ditch cap, `0.75 * head(...)`, 0.9-1.9 ft, against 0018's
"About 6 to 8 ft"; the claim cites 0068 alone. effect: map - the row channels between Kuwabata's ponds draw at or near the 1.5 ft
floor.

`ditches#the dike-pond's interior ditches` and `row_ditches#the lattice both ways`: IN-STEP again (place and warp; "width is judged
under the widths claim"). Both still SAY "ditches" where the pages now say channels/creeks - wording for T420's builder.
`claims-checked` again printed "rests on ... a page it does not cite - dropped" for `ditches#the widths` (the verdict rests on
0018, 0019, 0022, which the claim does not cite: T420's builder should add the 0018 drawing citation, or the DRIFTED verdict's
grounds will not be re-owed when 0018 moves).

## Stage 3 - pop-ups

- `make modal-triage`: TOOL-CLEARED 6 of 87 units (all modal-depiction: choice/cluster_position--high_margin,
  choice/pond_layout--grid, choice/settlement_form--dike_top, choice/settlement_form--nucleated, hamlet/bund, hamlet/windbreak);
  81 to the modal-triage agent (1 dispatch, 47k tokens, 62 s).
- The agent: 24 TOUCHES lines over 13 kinds. `make modal-triaged`: 40 of 81 units sent on, 41 answered `triage: untouched`.
  Sent on: modal-accuracy/-references/-gaps for 9 kinds (27 units: the five choice/dikepond_split--0.3..0.7,
  choice/field_archetype--mulberry_dike_fishpond, choice/pond_layout--mosaic, hamlet/mulberry-dike, hamlet/pond-canal) and
  modal-depiction for 13 kinds (those 9 + choice/field_archetype--polder_grid, choice/water_source_position--corner_high,
  hamlet/fruit-dike, hamlet/fry-pond).
  The triage's reasons: the splits, mulberry-dike, fruit-dike, fry-pond for "least pond in a parcel too small for its bank" (rule
  A, 0018 drawing) and "creek on every side of a pond not recorded" (rule B, 0018); pond-canal for the 6-8 ft width, the boat
  creeks, the feeder and the channel on every pond edge; mosaic for "lattice of ditches now creeks"; corner_high for the ring
  canal straight and square; polder_grid for the reed strip block.
- Dispatch: nine single modal-research launches were refused by the guard ("9 pop-ups owe modal-research together - send ONE
  agent on them all"); the compliant route is `make modal-bundle KIND="<all>" FOR=...`, one batched bundle, one agent, each
  pop-up recorded from its own sub-bundle. (So "one unit per agent" is not what the tooling wants for pop-ups.)

### modal-research, round 1 (one agent, 9 pop-ups, 143k tokens, 345 s) - all 27 units recorded, exit 0

| pop-up | verdict | EDITs |
|---|---|---|
| choice/dikepond_split--0.3 .. 0.7 (five) | ACCURACY 0; REFERENCES 0; GAPS 0 | none |
| hamlet/mulberry-dike | ACCURACY 0; REFERENCES 0; GAPS 0 | none |
| choice/field_archetype--mulberry_dike_fishpond | ACCURACY 1; REFERENCES 0; GAPS 0 | 1 |
| choice/pond_layout--mosaic | ACCURACY 1; REFERENCES 0; GAPS 0 | 1 |
| hamlet/pond-canal | ACCURACY 3; REFERENCES 0; GAPS 1 | 4 |

EDITs applied (`make apply-edits FROM=<transcript>`: 6 blocks, 0 refused), all under l7r/diagram/interactive/assets/modals/:
1. choice/field_archetype--mulberry_dike_fishpond.md: "their dikes from under 16 ft to about 33 ft wide," -> "their dikes
   usually about 20 to 33 ft wide," (the manual's under-16 ft figure had been given as the delta's; NOT a P1 change - old text
   of 0018 the whole-pop-up read found).
2. choice/pond_layout--mosaic.md: "and a district's ponds lay as a mosaic among its winding creeks rather than in planned rows."
   -> "and across the delta the ponds lay as a mosaic among its winding creeks, though in 1678 one township's pond land was
   likened to a chessboard, its lines the dikes and its squares the ponds." (the 1678 chessboard is on 0019's research page from
   an EARLIER change, not P1's).
3. hamlet/pond-canal.md: "How wide or deep the canals between the ponds ran is not recorded." -> "How wide or deep the canals
   between the ponds ran before modern times is not recorded." (P1's new finding).
4. hamlet/pond-canal.md: "natural water blurred. On the Lake Tai plain, by contrast," -> "natural water blurred, though in 1678
   one delta township's pond land was likened to a chessboard, its lines the dikes and its squares the ponds. On the Lake Tai
   plain, by contrast," (not P1's).
5. hamlet/pond-canal.md: "communities set their intakes at the upstream head and their outlets at the downstream tail," ->
   "communities set their intakes at the head of the ring and their outlets at its tail, most likely its upstream and downstream
   ends," (not P1's).
6. hamlet/pond-canal.md: "reworking ponds to raise fish. Around Lake" -> "reworking ponds to raise fish. The creeks among the
   delta's ponds carried boats: in 1678 the fry raised in its ponds were carried off by boat, and late in the Qing one village
   built 58 landings along little more than a mile of its waterway. Around Lake" (P1's new finding).

Notes the reply left for modal-depiction: the splits' "the planted bank fills the ring between the pond and the canal" against
0018's "how many of a pond's sides met a creek ... is not recorded"; pond-canal's "No boat or landing is drawn: not every
dike-pond hamlet need have had water a boat could travel" against 0018's "The channels among the ponds were creeks that carried
boats."

After the EDITs: 13 modal-depiction units still owed, and 3 modal-form units RE-OWED by the research EDITs
(field_archetype--mulberry_dike_fishpond, pond_layout--mosaic, pond-canal) - the known chain.

### modal-form (owed by the research EDITs; one agent, 3 pop-ups, 36k tokens, 60 s) - 3 units recorded

| pop-up | verdict | EDITs |
|---|---|---|
| choice/field_archetype--mulberry_dike_fishpond | 2 findings (0 FIX, 2 NOTE) | 3 |
| choice/pond_layout--mosaic | 1 finding (1 FIX) | 2 |
| hamlet/pond-canal | 2 findings (1 FIX, 1 NOTE) | 0 ("EDIT: none - ..." line) |

EDITs applied (`make apply-edits`: 5 blocks, 0 refused; the "EDIT: none - <reason>" line did NOT make the parser refuse, so no
copy was needed - 451 T228 did not bite on this form of the line):
1-2. field_archetype--mulberry_dike_fishpond.md: the sentence "In the delta in modern times most ponds are about 1 to 1.5 acres
   (0.4 to 0.6 ha) and 7 to 10 ft deep, their dikes usually about 20 to 33 ft wide, standing 2 to 3 ft above the water." MOVED from
   the look paragraph to the end of the how-much paragraph, wording unchanged (a NOTE, M2/M7).
3. same file, Depiction: "where a Ming river manual set such rows on the ground off its foot." -> "where in the Ming such rows
   were to be set on the ground off its foot." (a NOTE, M16).
4-5. pond_layout--mosaic.md: "deep. Before modern times only the largest are measured: in 1678 the bigger ponds" -> "deep. In 1678
   the bigger ponds" (FIX M16).
None of the five rewords anything P1 changed: they are form defects found because the research EDITs re-owed a form read.

THE T226 CASE, RAISED BY A CHECK THIS TIME - pond-canal, FIX M8/M11, verbatim: "About says "How wide or deep the canals between
the ponds ran before modern times is not recorded." M8 then requires the width (and depth, if one is drawn) that the map uses to
appear as a guess bullet. The Guesses tab only covers the inlet and the outfall. The drawn figure is not in the bundle, so the
session has to supply it. EDIT: none". NOT applied (no EDIT; and the figure to write is 6 to 8 ft per the page but 1.2-2.5 ft as
drawn until T420's code lands). The unit was recorded with the FIX stated in its RESULT; it reads answered. OPEN for T420's
builder: a Guesses bullet `{0018#creek-width-between-ponds}` on hamlet/pond-canal once the code draws 6 to 8 ft.

`make apply-edits` then settled modal-accuracy/-gaps/-references of the two choice pop-ups "with its answer - a wording round's
EDITs alone moved it, no fact changed (451 T188)": no second research round.

### modal-depiction, first batch (one agent, 10 pop-ups, 157k tokens, 405 s) - 10 units recorded

| pop-up | verdict | EDITs |
|---|---|---|
| choice/dikepond_split--0.3, 0.4, 0.6, 0.7 | COVERAGE 0; TRUTH 0; LINKS 1 each | 1 each |
| choice/dikepond_split--0.5 | clean | 0 |
| choice/field_archetype--polder_grid | COVERAGE 1; TRUTH 0; LINKS 0 | 1 |
| choice/water_source_position--corner_high | COVERAGE 0; TRUTH 1; LINKS 0 | 1 |
| hamlet/fruit-dike | COVERAGE 0; TRUTH 0; LINKS 1 | 1 |
| hamlet/fry-pond | clean | 0 |
| hamlet/mulberry-dike | COVERAGE 0; TRUTH 1; LINKS 1 | 3 |

EDITs applied (10 blocks, 0 refused):
- dikepond_split--0.3.md, --0.4.md, --0.6.md, --0.7.md, hamlet/fruit-dike.md, hamlet/mulberry-dike.md: the `Drawing:` line gains
  `research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html` (six LINKS edits; 0027
  is not a P1 page - an older omission).
- choice/field_archetype--polder_grid.md: "runs round its foot, a convention: a polder had channels inside its dike, but a single
  ring at the dike's foot is not recorded." -> "runs straight along its foot, turning square where the dike turns, a convention:
  ..." (P1's new item `ring-canal-straight-square`).
- choice/water_source_position--corner_high.md: "It and the channels inside are drawn in long, gently wavering reaches with
  rounded corners, also the map's convention for a dug canal." -> "That canal is drawn straight along the dike's foot, turning
  square where the dike turns, and the channels inside it in long, gently wavering reaches with rounded corners; both lines are
  the map's convention." (P1's; the pop-up was WRONG before - a real catch).
- hamlet/mulberry-dike.md (two blocks): "Each settlement's ponds are drawn at one of five splits of water to bank: six parts to
  four either way, seven of water to three of bank, one to one, or three of water to seven of bank; the title card says which split
  this one takes." -> "Each settlement's ponds are drawn at one split of water to bank; the title card says which split this one
  takes." (D4; not P1's).
NOTED, NOT FILED by the agent: the least-pond fallback is covered by no split tab ("every pond ... by the same distance") - a
GUESS, not a convention, so no finding. (This is the reason the triage sent the five splits on: it produced no finding on it.)

### modal-depiction, second batch (the three that waited on form; one agent, 181k tokens, 365 s) - 3 units recorded

| pop-up | verdict | EDITs |
|---|---|---|
| choice/field_archetype--mulberry_dike_fishpond | COVERAGE 0; TRUTH 2; LINKS 0 | 2 |
| choice/pond_layout--mosaic | COVERAGE 0; TRUTH 2; LINKS 0 | 3 |
| hamlet/pond-canal | COVERAGE 1; TRUTH 1; LINKS 0 | 4 |

EDITs applied (9 blocks, 0 refused):
- field_archetype--mulberry_dike_fishpond.md: "...or as a straight chessboard of ponds." -> "...or as a straight chessboard of
  ponds; the title card says which." (D4; not P1's).
- same: "A single canal runs round the inside of its foot: canals ran inside a polder's dike, but the one ring at its foot, and the
  gentle waver of the canals' line, are the map's convention." -> "A single canal runs round the inside of its foot, straight along
  it and square at the corners: canals ran inside a polder's dike, but the one ring at its foot and its line are the map's
  convention." (P1's `ring-canal-straight-square`; the old "gentle waver" was wrong for this block).
- pond_layout--mosaic.md: "The map lays the block out on a lattice of ditches" -> "... a lattice of canals"; "so the interior
  ditches meander like creeks" -> "so the canals between the ponds meander like creeks" (P1's: the page no longer calls the
  channels ditches - the brief's predicted re-check, caught).
- same: "its parcel is about 1.2 acres" -> "most stand in a parcel of about 1.2 acres" (0022; not P1's).
- hamlet/pond-canal.md: "A canal is drawn round the inside foot of the dike:" -> "..., straight along it and square at the
  corners:"; "so that ring is a drawing" -> "so that ring and its line are a drawing" (P1's).
- same (two blocks, D4): the sentence "block's canals take one of the two layouts dike-pond blocks had, which differs by
  settlement: on about one hamlet in three ... how strongly they bend is a degree chosen to read well." -> "block's canals between
  the ponds run straight or wind like creeks, by the settlement's pond layout; the title card says which this one has." (not P1's).

After: `make record-owed UNANSWERED=1`: no record check is owed. The depiction EDITs re-owed nothing (each unit "settled with its
answered round"). NO pop-up check ran a second round; no arbiter was needed in stage 3.

Pop-up totals: 87 units = 6 tool-cleared + 41 agent-cleared + 40 checked (27 research units on 9 pop-ups, 13 depiction units),
plus 3 modal-form units re-owed by EDITs. 5 check dispatches (triage 1, research 1, form 1, depiction 2). 30 EDIT blocks applied
to 11 pop-up files, 0 refused.

## Stage 4

`make page-check` exit 0; `make record CHECK=1` exit 0 ("builds cleanly (4380 page(s))"); `make quick` exit 0 ("quick: clean").

## Stage 5 - ledger

`make ledger-owed`: 9 passes without a row (5 impl-drift, modal-research, modal-form, 2 modal-depiction; the arbiter and triage
dispatches were not listed); `make ledger-owed WRITE=<this file>`: 9 rows written. Measured input: the three big pop-up batches
read 1.18M, 1.33M and 1.15M tokens in, summed over their turns (about 88% cached; the stage tables' 143k / 157k / 181k are the
notifications' subagent_tokens, a different measure of the same runs) - a 9- or 10-pop-up batch in one agent is the costly unit of this round.

## PREDICTED vs ACTUAL

Pop-ups (R = re-checked, C = cleared):

| pop-up | predicted | actual | result of the check |
|---|---|---|---|
| hamlet/pond-canal | R | R (research, form, depiction) | 8 EDITs; boats, the width's silence scoped, the ring's line |
| choice/pond_layout--mosaic | R | R (research, form, depiction) | 6 EDITs; "ditches" -> "canals" |
| choice/field_archetype--mulberry_dike_fishpond | R | R (research, form, depiction) | 6 EDIT blocks; the ring's line, no waver |
| choice/field_archetype--polder_grid | R | R (depiction only) | 1 EDIT; the ring's straight square line |
| choice/water_source_position--corner_high | R | R (depiction only) | 1 EDIT; the pop-up had the ring canal wavering - wrong |
| choice/pond_layout--grid | R (expected IN-STEP) | C (depiction by the TOOL, the rest by the agent) | unread; I read it: agrees |
| hamlet/fish-pond | R | C (agent) | unread; I read it: agrees, but silent on the rounded corners and the least pond |
| hamlet/sluice-gate | R | C (agent) | unread; I read it: agrees (it never names the feeder's course) |
| choice/leftover--pond, --rice | R | C (agent) | unread; both say "creeks", neither says ditch: agree |
| hamlet/perimeter-dike | R only if the strip's depth lands | C (agent; one depiction unit) | its one reed line states no depth: agrees |
| choice/dikepond_split--0.3..0.7 (five) | C | R (research + depiction) | research clean x5; depiction: 4 LINKS edits (0027), none on P1's change |
| hamlet/mulberry-dike | C | R (research + depiction) | research clean; depiction 3 EDITs, none on P1's change |
| hamlet/fruit-dike | C | R (depiction) | 1 LINKS edit (0027), not P1's |
| hamlet/fry-pond | C | R (depiction) | clean |
| dike_crop--mulberry, fry_form--*, land_use_overlay--mulberry_fishpond, tea-dike, cluster_position--high_margin, settlement_form--*, windbreak, bund | C | C | - |

Predicted "about 21 pop-ups clear"; the 87 units name 29 kinds, of which 13 were checked and 16 cleared outright (47 of 87 units
cleared, 40 checked). Of the
10 kinds predicted for re-check, 5 were checked and 5 cleared; 8 kinds predicted to clear were checked.

Claims:

| group | predicted | actual |
|---|---|---|
| 0018 drawing: ponds.rs rounded#rounded corners, rounded#the bank's inset, LEAST_SHARE; landuse.rs REACH_FT (4) | re-check, then restated to cite the new item | TOOL-CLEARED unread (they say the page is silent; the new item is a new block they do not rest on) |
| 0019 drawing: 9 in field/polder.rs + check.rs RING_CANAL (10) | re-check | impl-drift, all IN-STEP |
| 0019 drawing: sluice_channel, stage_waterward#the reed strips, roll_polder#the strips after the seat, waterward fringe (4) | re-check | TOOL-CLEARED unread |
| 0022: polder#never uniform rectangles (1) | re-check | impl-drift, IN-STEP |
| the other claims (predicted to clear; "about 56") | clear | 47 tool-cleared; 10 went to impl-drift as "rests changed" (9 IN-STEP, plan.rs POLDERS DRIFTED fix: claim) |
| ditches#the widths (cites 0068 only) | not named | never owed; re-checked on a REASON: DRIFTED fix: code |

Predicted 19 re-checks and about 56 clears of 76; actual 21 impl-drift (11 of the predicted 19) and 55 tool-cleared.

## Judgment

(a) Over-cascade.
- Claims, the direct group: 21 claims went straight to impl-drift as "rests changed" with no triage; 20 came back IN-STEP and
  the one DRIFTED (plan.rs POLDERS, "a surveyed grid", fix: claim, effect: none) is a wording fault that predates P1. Ten of the 21
  were ones the brief expected to clear (the settlement's ground, the archetype tables, two sluices, the chessboard, every pond
  four-sided): the block each rests on was reworded (no "ditch", the restated ring-canal blocks), and the rule sends that on
  whatever the claim says. A triage on the brief's reading would have sent 11. Cheap all the same: 4 dispatches, 124k subagent
  tokens together, under a minute each. (P1's commit touches no rust/ file, so the POLDERS wording does predate it.)
- Pop-ups, the triage's "least pond" reading: the five dikepond_split pop-ups, mulberry-dike, fruit-dike and fry-pond were sent
  on for "least pond in a parcel too small for its bank" (rule A) and "creek on every side of a pond not recorded" (rule B). 23
  units (15 research + 8 depiction). On P1's change they produced NOTHING: research clean on all six, depiction's only remark on
  the least pond was NOTED, NOT FILED (a guess, not a convention). What they did produce is six `Drawing:` links to 0027 and the
  mulberry-dike D4 trim - real, older defects, fixed correctly once found, but found only because a whole-pop-up read was owed.
  That is the round's largest over-cascade: roughly half of the two big batches (about 1.2M tokens in each, mostly cached).
- Edits beyond the change, on the three pop-ups rightly re-checked: of pond-canal's 8, mosaic's 6 and the mulberry archetype's 6
  EDIT blocks, those on P1's change are: pond-canal's width silence scoped, the boats sentence, the ring's line (4 blocks);
  mosaic's ditches -> canals (2); the archetype's ring line / no waver (1); plus polder_grid (1) and corner_high (1). The other
  21 blocks reword text P1 never touched (the 1678 chessboard twice - from an earlier change to 0019's research page that no
  round had carried to these pop-ups; the manual's 16 ft; head-and-tail as a reading; three D4 title-card trims; "most stand in a
  parcel"; the 0027 links; the moved sentence; two M16 voice fixes). None is wrong. All come from the known chain: no "change
  since" scope, so each check read the whole pop-up.
- The chain research EDIT -> form round fired again on three pop-ups (5 EDIT blocks, none on P1's words). T188 then stopped a
  second research round, and depiction's EDITs re-owed nothing. No pop-up check ran twice.
- Second and third rounds: none run. The three third-round units were ruled ACCEPT without a check (3 arbiter dispatches, 125k
  tokens - dearer than the three one-phrase checks would have been, but the rule's point is the loop, not the cost). Each was
  caused by another check's one-phrase EDIT landing after the unit's round 2. The measured case of the same thing: making 0018's
  "fiscal commissioner" agree with 0019 re-owed three units a third round each; it was put back and left OPEN.
- The supplementary width re-check (3 claims, 35k tokens) was mine, not the tooling's: see (b). Its prompt NAMED the width
  question and the added page, so its DRIFTED is a directed read, not an independent discovery.
- The "not P1's" labels were checked against `git show 8c37200fa9 -- research/questions`: its added lines hold none of "within
  5 m", "likened the pond land", "most ponds stand", "head of the ring", "calibrated liberty"; they do hold the landings and
  `ring-canal-straight-square`.

(b) Under-cascade.
- THE HEADLINE: the claims cascade did not reach the code the page change was about. 0018's drawing page now says a canal
  between ponds is "About 6 to 8 ft, a GUESS"; the claim that carries the drawn width (`ditches#the widths`, 1.2-2.5 ft) cites
  0068 only, and the two dike-pond channel claims cite 0019's drawing page, which states no width. So the round as owed returned
  21 verdicts with no finding on the widths, and `make claims-owed` read "no claim is owed". Only a REASON= re-check with
  PAGES=<0018 drawing> produced the DRIFTED fix: code. A new item on a drawing page reaches a claim only if the claim already
  cites that page and rests on a block that moved - the claims twin of 451 T226.
- The 8 predicted claims the tool cleared unread: the four 0018 ones (ponds.rs rounded x2, LEAST_SHARE; landuse.rs REACH_FT)
  each say the page is silent, and the page now has `pond-corners-rounded` and `least-pond` items; nothing owes their
  restatement (and `claims-label` already flags `rounded#the bank's inset`). The four 0019 ones (sluice_channel, the reed strips
  x2, waterward fringe) were cleared though 0019 gained `reed-strip-depth` (280 ft); `polder#the feeder` (which WAS checked)
  shows the pattern: "says the page is silent on the feeder's course, but §18 now draws it straight and records that as a
  GUESS. That still counts as IN-STEP." Not wrong outcomes, but stale "the page is silent" wording the tooling will not surface.
- Pop-ups read by me, as they finally stand:
  - hamlet/pond-canal: agrees with the pages on the creeks, the boats, the ring's line and "not as a rice field's irrigation
    ditches". Two gaps: (1) nothing gives the drawn width - About says the old width is not recorded, the Guesses tab has only the
    inlet/outfall bullet; modal-form raised it as FIX M8/M11 with no EDIT (see stage 3) - OPEN for T420's builder. (2) Depiction
    still ends "No boat or landing is drawn: not every dike-pond hamlet need have had water a boat could travel", which now sits
    against its own About ("The creeks among the delta's ponds carried boats") and 0018; modal-research flagged it for depiction,
    and modal-depiction did not rule on it. OPEN. Its `Covers:` line says "the laterals between the ponds" (engine vocabulary,
    not shown as prose).
  - hamlet/fish-pond (cleared unread): agrees on what P1 changed - "A pond lay among the polder's creeks and canals"; no "ditch", no width. It
    does not say the corners are rounded or name the least pond (its Guesses tab holds only `{0018#hamlet-s-ponds-take}`): the
    T226 gap, two new GUESS items about its own glyph on no pop-up. SIBLING INCONSISTENCY the round's edits created: it still
    says "in the Pearl River delta they lay in a mosaic among winding rivers", the flat mosaic claim modal-research ruled a
    defect (M8, the 1678 chessboard) and fixed in mosaic and pond-canal. OPEN; no EDIT exists for it.
  - hamlet/sluice-gate (cleared unread): agrees on what P1 changed; says nothing of the feeder's course or the channels' kind.
    SIBLING INCONSISTENCY: it still states "the intake stood at the ring's upstream head and the outlet at its downstream tail"
    as fact, the M12 reading modal-research fixed in pond-canal ("most likely its upstream and downstream ends"). OPEN; no EDIT.
  - choice/pond_layout--mosaic: now "a lattice of canals" and "the canals between the ponds meander like creeks"; agrees. It
    still says "How strongly the lattice bends is set by eye" (0019: "a calibrated liberty ... set on the Kuwabata map").
  - choice/pond_layout--grid (cleared unread, its depiction unit by the tool): "never a grid of uniform rectangles" is already
    said of "A rice polder", and the chessboard is the dike-pond's: agrees with 0022 as scoped.
  - No pop-up among the dike-pond set calls the channels ditches any more (grep "ditch" over every modal naming dike-ponds: only
    pond-canal's "not as a rice field's irrigation ditches" and its Covers key `field_ditches`), and none implies a narrow width.
- The three new figures on the Guesses tabs: NONE arrived. No modal holds `creek-width-between-ponds`, "6 to 8 ft",
  `reed-strip-depth`, "280 ft" or the item id `ring-canal-straight-square` (grep). The ring canal's straight line did arrive as
  PROSE on four Depiction tabs (pond-canal, the mulberry archetype, polder_grid, corner_high) because modal-depiction reads
  CONVENTION items; the two GUESS items (width, reed depth) and 0018's corners and least pond reached nothing. T226 confirmed,
  with one advance: modal-form now names the missing width bullet as a FIX.
- hamlet/perimeter-dike WAS among the 87 (one modal-depiction unit) and the triage agent cleared it: its one reed line ("with
  reeds below") states no depth, so the clear is right; the 280 ft GUESS reaches no pop-up.

(c) The new rules.
- T218 (hold a "pages are silent" finding): did not fire; all five `claims-checked` exited 0. Near case as in P7: the feeder
  claim's own text says the page is silent while the verdict is IN-STEP, recorded without a hold.
- T219 (outside notes listed, not filed): the "NOTED, NOT FILED" lines (impl-drift, modal-depiction) filed nothing. The
  supplementary reply's "OUTSIDE THE CHANGE" row WAS filed by `claims-checked` ("filed, not fixed", one row in specs/451
  found.jsonl) - that is a finding with an effect on the map, so filing it looks right; the row is T420's.
- T220 / T221: not exercised by the owed round (no known-departure mark, no corrected claim). `ditches#the widths` now holds a
  DRIFTED verdict resting on pages it does not cite (`claims-checked`: "rests on ... a page it does not cite - dropped"), so
  until the claim cites 0018's drawing page a later move of that page will not re-owe it: worth a look under T221.
- T223-T225 (stamps): behaved. `L7R_LAND_ALONE=1 make claims-owed`: "no claim is owed"; `L7R_LAND_ALONE=1 make record-owed
  UNANSWERED=1`: "no record check is owed"; neither prints an "other builders' uncommitted code" line (grep count 0).
- T188 fired on two pop-ups after the form EDITs and behaved. T228 ("EDIT: none"): modal-form wrote "EDIT: none - <reason>"
  despite being asked not to, and `apply-edits` took the reply without refusing (5 blocks, 0 refused). That is ONE line of one
  form, and the prompts had asked the agents to omit such lines, so T228 is not shown fixed.
- The round counter again held 1 where 2 rounds had run (three triggers); the wave guard and the batch guard both fired and each
  named its compliant command (the batch one worked; the wave one names a Workflow tool this agent does not have).
- `arbiter-bundle BATCH=1 TRIGGERS=a,b,c` reads the comma list as one trigger.

## Is everything owed answered?

Yes: `make claims-owed`, `make record-owed UNANSWERED=1` (plain and with L7R_LAND_ALONE=1) and `make ledger-owed` all read
nothing owed; page-check, `make record CHECK=1` and `make quick` are green. Answered is not closed: `make claims-report` lists
the two new DRIFTED verdicts (ditches#the widths, fix: code; plan.rs POLDERS, fix: claim) as open findings, and
modal-form's FIX on hamlet/pond-canal (the drawn width owes a Guesses bullet) is recorded but NOT applied.

OPEN, for T420's builder or the parent:
1. Code: dike-pond column and row channels at 6 to 8 ft (ditches#the widths DRIFTED; the filed row_ditches width row); add the
   0018 drawing citation to the widths claim(s); reword "ditches" in `ditches#the dike-pond's interior ditches` / `row_ditches`.
2. Claim restatements in rust/: plan.rs POLDERS ("a surveyed grid"); polder#the feeder ("the page is silent"); the four 0018
   claims that say the page is silent (rounded x2, LEAST_SHARE, REACH_FT) and the `claims-label` notice on rounded#the bank's inset.
3. Pop-ups: fish-pond's flat "lay in a mosaic" and sluice-gate's "upstream head ... downstream tail" (siblings of sentences
   this round fixed elsewhere); a Guesses bullet for the canal width on hamlet/pond-canal (modal-form FIX, no EDIT); pond-canal's "not every
   dike-pond hamlet need have had water a boat could travel"; the corners / least pond on fish-pond; the reed strip's depth.
4. Record: 0018 note wuhurec-wanchun-5 "fiscal commissioner" (0019 says "transport commissioner"); the `qing` tooltip; 0019
   drawing's "rebuilt in 1061"; the P1 check handoff's other OPEN lines stand.

## Files changed (uncommitted, unstaged; no rust/ file)

dev/claims-index.json, dev/claims-pages.json, dev/review-ledger.md (9 rows),
l7r/diagram/interactive/assets/modals/choice/{dikepond_split--0.3,dikepond_split--0.4,dikepond_split--0.6,dikepond_split--0.7,
field_archetype--mulberry_dike_fishpond,field_archetype--polder_grid,pond_layout--mosaic,water_source_position--corner_high}.md,
l7r/diagram/interactive/assets/modals/hamlet/{fruit-dike,mulberry-dike,pond-canal}.md,
specs/451-time-retro-and-efficiency/arbiter.jsonl (3 rulings), specs/451-time-retro-and-efficiency/found.jsonl (1 row).
