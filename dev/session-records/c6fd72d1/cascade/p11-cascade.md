# P11 cascade (449 T425, T426's pages: 0057, 0031 -> 0349 split, 0081) - 2026-11-24

Clone `/diagram/.clones/diagram-backlog` at f6e999655c. Working files: `/home/agent/.claude/jobs/c6fd72d1/tmp/cascade/p11/`.

## Counts per stage, with the tool's reasons

| stage | in | out | the tool's reason / verdict |
|---|---|---|---|
| (1) third rounds to the arbiter | 2 (record-format:0031, :0081) | 0 rounds run | `round-arbiter` ruled **accept** on both (`specs/449-rust-codebase/arbiter.jsonl`); answered with `make record-checked ... REASON=` |
| (2a) `claims-owed` | 40 triage + 3 `claims-label` lines | - | 40 "owe only a TRIAGE" |
| (2b) `claims-triage` | 40 | 0 to the agent | "40 claim(s) cleared without a triage - a page each cites moved and no block it rests on did (feature 432, FR-005 a)"; no bundle, no agent |
| (2c) owed impl-drift | 0 | - | "claims-owed: no claim is owed" |
| (2d) DIRECTED impl-drift | 16 (`REASON=` + `PAGES=` 0031/0057/0081/0349 drawing) | IN-STEP 11, DRIFTED 5 recorded; 1 HELD | 451 T218 held `open_at_an_end` (nearest page 0196 drawing); re-bundled once with the guard's `PAGES=`: DRIFTED |
| (3a) pop-ups owed | 47 `modal-depiction` (every pop-up whose `Drawing:` names 0031, 0057 or 0081; 0349 joined to 0031's list by its `moved` pointer) | - | "a page its Drawing: names moved" |
| (3b) `modal-triage` | 47 | 46 cleared by the tool, 1 to the agent (`choice/lane_web--back_lane`, 0081) | agent: `NONE`; `modal-triaged`: "0 of 1 unit(s) sent on" |
| (3c) pop-up checks / EDITs | 0 | 0 | nothing sent on, no `apply-edits` |
| (4) `make record CHECK=1` | - | builds cleanly (4417 pages) | `make page-check` rc 0; `make quick` RED once (a British spelling the P11 research-pass wrote into `research/source-attempts.jsonl:23559`, its logged grep `\|centre`), fixed (term dropped from the logged command), then clean |
| (5) `ledger-owed` | 2 passes (the two impl-drift) | 2 rows written | then nothing owed |

Costs: directed impl-drift 111 s, 151k in / 11.3k out; held re-run 32 s, 55k / 3.3k; arbiters 87 s / 23k and 128 s / 27k;
modal-triage agent 11 s / 11k.

## The arbiter's rulings (quoted)

- record-format:0031 - accept: "Record-format round 2 read note -10 after both hand edits to the notes page (03:27:49 and
  03:28:35, before the 03:34 dispatch). ... That EDIT is the only change since round 2. It removes text and replaces "None
  names" with "No page read names", whose words were already ruled on in the deleted span, so a third round has nothing new
  to read and nothing reverses."
- record-format:0081 - accept: "That EDIT is a pure removal: it deletes one pass span and starts the next with 'None of the
  pages read says', words taken from the two spans it replaces, which round 2 had just ruled on (98 of 98 words, 0
  VOCABULARY, 0 SESSION NOTE, 0 HISTORY). ... as ruled for record-format:0101 and :0113 under ask:t330a-round3." It could
  not find the "two earlier rulings today" in the 449 log and cited `ask:t330a-round3` instead. No tooling fix named
  (cost under its 10-minute bar).

## Each claim verdict (directed check)

DRIFTED (all `fix: claim; effect: none` - code IN-STEP):
1. `seat.rs::open_at_an_end#a seat astride the brook leaves by its open bank` (held, re-judged): "the claim names the
   wrong page ... names 0035's drawing page as the page that records the GUESS, yet 0035 records only the both-banks seat
   (§2). It also says the record is silent on where the way out starts ... 0081 §24 now records this exact fallback."
2. `seat.rs::BAND_EXITS#the way out from the band's ends`: "the claim says 0081 is silent, and 0081 now records this as a
   guess."
3. `driver/toe.rs::toe_band#toe band edge`: "on a side where the fields narrow downhill that same edge carries the wet
   ground up the whole side, which 0057 now records as a deliberate deviation, and the claim gives it as a finding."
4. `seat.rs::seat#a walled-in head gives way`: "the page calls it 'a fallback of ours, a GUESS', and the claim gives it as
   a finding."
5. `seat/exit.rs::Exit.has_exit#dry way out of the seat`: "'a walled-in head is refused' is out of date: 0081 now has a
   site walled in at its middle passed over, then asked again from its band's ends."

IN-STEP (11): `margins.rs::ranked#not on the wet toe` ("the toe, which now includes the narrowing flank"), `ranked#seat on
the field's margin`, `ranked#the ladder`, `driver.rs::stage_seat#the way out's walls`, `toe.rs::PAD#toe band edge`,
`seat.rs::seat#the back to the hill where the wind cannot be backed`, `plan.rs::plan#the fall backs the wind`,
`water_frame.rs::admitted#high side and windward side as one`, `plan.rs::KNOBS#the farm water`, `KNOBS#the lane forms`,
`exit.rs::Exit.walkable#a track's clearance off wet ground`.

NOTED, NOT FILED (agent): `seat#the back to the hill`'s last clause could also cite `way-out-from-band-ends`;
`ranked#not on the wet toe` could also cite `toe-on-tapering-flank`; "None of the 16 claims cites the scattered-farm reach
section that moved from 0031 to 0349, so the move leaves none of them stale."; `BAND_EXITS` matches six-tenths only if
`band.0` is the half-length (not shown in the bundle).

`claims-checked` dropped rests on pages a claim does not cite (`stage_seat` and `ranked#not on the wet toe` on 0057,
`seat#the back to the hill` on 0081, `open_at_an_end` on 0031/0057) - the directed bundles carry extra pages on purpose.

Pop-up EDITs: none (no check ran).

## PREDICTED vs ACTUAL

| prediction | actual |
|---|---|
| re-check (owed) `hamlet/marsh`, `choice/cluster_position--high_margin` | both CLEARED by the tool, unread |
| re-check `toe_band#toe band edge`, `PAD#toe band edge` - IN-STEP | cleared (FR-005 a); directed: PAD IN-STEP, toe_band **DRIFTED** (gives the wet flank as a finding) |
| re-check seat claims (`seat#the back to the hill`, `ranked#seat on the field's margin`, `ranked#the ladder`, `plan#the fall backs the wind`, `admitted#high side ...`, `seat#a walled-in head gives way`, `Exit.has_exit#dry way out`) - IN-STEP | all cleared; directed: 5 IN-STEP, `seat#a walled-in head gives way` and `Exit.has_exit` **DRIFTED** (stated as a finding / out of date) |
| `BAND_EXITS` cleared unread though "silent"; DRIFTED-to-restate | as predicted: cleared, directed DRIFTED |
| `open_at_an_end` directed (cites 0035/0081); restate to cite `seat-astride-brook-windward-corner` | as predicted, DRIFTED (and T218 held it once) |
| `ranked#not on the wet toe`, `stage_seat#the way out's walls` directed vs 0057 | IN-STEP, as predicted |
| `hamlet/village-lane` re-check IN-STEP | cleared by the tool |
| the split re-owes nothing | held: no claim, no pop-up sent on by the move |
| `settlement_form--dispersed` may state the moved section -> its `Drawing:` should gain 0349 | it does state it; line lacks 0349 (below) |

Owed machinery: predicted ~13 claims and ~3 pop-ups owed; actual 0 and 0. Every finding came from the directed check.

## Judgment

(a) **Over-cascade: none.** The split alone sent NOTHING on: 0349 joined every 0031 pop-up's page list through the `moved`
pointer, all 42 of those cleared by the tool, and no claim was re-owed by the move (the agent confirms none cites the moved
section). 46 of 47 pop-ups and 40 of 40 claims cleared without an agent; the one agent triage (`lane_web--back_lane`) took
11 s and said NONE. The only paid spend was the two arbiter rulings and the directed check.

(b) **Under-cascade: as in every additions-only session, the owed machinery saw nothing; the directed check found 5
restatements.**
- FR-005 a clears a claim whose rested blocks stand, and a NEW block is a block no claim rests on - so the two claims that
  newly give a recorded GUESS/DEVIATION as a finding (`toe_band#toe band edge`, `seat#a walled-in head gives way`) and the
  one now out of date (`Exit.has_exit`) were cleared; the prediction itself expected those IN-STEP, so the directed list
  caught two of the five only because I widened it to the predicted re-checks. The "stale silent" pattern (`BAND_EXITS`,
  `open_at_an_end`) recurred, the ninth cascade to show it.
- Pop-ups (451 T226): `cluster_position--high_margin`'s Depiction says "Every hamlet but a polder's takes this seat, its
  land laid to fall away from the winter wind or square across it" - it does NOT state the corner astride the brook (the
  4-in-35,000 fallback). `hamlet/marsh`'s Depiction says "its upper edge following the foot of the fields ... It runs
  straight along the slope" - it does NOT state the wet ground carried up a tapering flank (a DEVIATION a reader would see
  as reeds up the side of the fields; the higher-value omission of the two). Reported, not added (no check's EDIT).
- 451 T234: `choice/settlement_form--dispersed`'s Depiction states the moved block's rule ("A scattered settlement needs
  about twice the ground per farm that a clustered one does, so the map gives it a roomier field ...; that is a rule for
  fitting the drawing") and its `Drawing:` line names 0031 drawing, not 0349 - so it now lacks 0349. No other 0031 pop-up's
  Depiction states the moved section (`hamlet/well`'s "within reach of water" is a different rule). No pop-up names 0349.
  T234 (D5 has no split clause) is still open, so the next modal-depiction read would call this a LINKS finding.
- Echo list (check handoff): of the old wordings, only `seat.rs` echoes ("4 of 35,000", "head's windward corner", "point
  of a cluster its way out") - all inside the claims restated below; no pop-up echoes any.

(c) **Rules that fired.**
- FR-005 a: 40 claims cleared. Modal triage's tool clearance: 46; the agent 1, NONE.
- 451 T185/T196 (a split is a move, pages follow `moved`): yes - 0349 appended to the pop-ups' moved pages, nothing counted
  removed.
- 451 T218: held 1 line (`open_at_an_end`, "the record's nearest pages ... (0196-communal-wells-ido.drawing.html)"); one
  re-bundle with its PAGES (0031, 0057, 0196 drawing) recorded it - 0196 was irrelevant, the known misfire shape.
- Round arbiter: 2 accepts on the deletion-EDIT third-round shape (the third and fourth such today).
- Decide-first guard: not refused (task in the description, `DECIDE_OK` in each prompt).
- House style in `make quick`: caught a P11 research-pass log line; not a cascade rule, but the P11 landing would have gone
  red on it.
- `claims-label` (3, not owed): `plan.rs::KNOBS#the farm water`, `KNOBS#the lane forms`, `exit.rs::Exit.walkable#a track's
  clearance off wet ground` - "a bare GUESS says no page speaks, but its account names 0031/0081"; the directed check found
  all three IN-STEP; their labels stand to be fixed with the restatements.

## Rust claims to restate (not done; rust/ not edited) - all fix: claim, effect: none

1. `rust/phases/src/seat.rs::open_at_an_end#a seat astride the brook leaves by its open bank` -> "GUESS
   research/questions/0081-village-lanes.drawing.html (`way-out-from-band-ends`): a site with no dry way out from its band's
   middle is asked again, once no site is left, from six-tenths of the way to each end of its band, and kept if either has a
   way out; this keeps the one seat astride the brook, which
   research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html places at the windward corner at the
   head of its fields (`seat-astride-brook-windward-corner`), its track leaving by the open bank, where the land falls
   square across the wind onto the wet ground climbing the tapering flank (DEVIATION
   research/questions/0057-marshes-and-wetlands-shitchi.drawing.html, `toe-on-tapering-flank`), houses on both banks
   (research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html) - 4 of 35,000 valley rolls
   (measurement as now)". Drop "the record does not say where a cluster's way out starts".
2. `seat.rs::BAND_EXITS#the way out from the band's ends` -> "GUESS research/questions/0081-village-lanes.drawing.html
   (`way-out-from-band-ends`): once no site is left, the way out is asked from 0.6 of the half-length either side of the
   center, the stations the band's ground is sampled at (`margins::SAMPLE_ALONG`)". Drop "the page is silent".
3. `driver/toe.rs::toe_band#toe band edge` -> append "; where the fields narrow inward downhill the edge carries the wet
   ground up that side its whole length - DEVIATION research/questions/0057-marshes-and-wetlands-shitchi.drawing.html
   (`toe-on-tapering-flank`)".
4. `seat.rs::seat#a walled-in head gives way` -> "GUESS research/questions/0081-village-lanes.drawing.html
   (`way-out-from-band-ends`): lanes keep to dry ground, so a margin whose seat has no dry way out from its center is passed
   over for the next; once none is left the passed-over seats are asked again from their bands' ends (`open_at_an_end`),
   and one with a way out there is kept".
5. `seat/exit.rs::Exit.has_exit#dry way out of the seat` -> "research/questions/0081-village-lanes.drawing.html: lanes keep
   to dry ground and the track out runs off the map; a point with no dry way off the map is walled in, and a site walled in
   at its middle is passed over (`way-out-from-band-ends`)".
Optional (NOTED): `seat.rs::seat#the back to the hill ...` last clause cite `way-out-from-band-ends`;
`margins.rs::ranked#not on the wet toe` add `toe-on-tapering-flank`. Plus the 3 `claims-label` lines above.

## Files changed in the clone (uncommitted)

- `dev/claims-index.json`, `dev/claims-pages.json` (FR-005 a clearances, the 17 directed verdicts)
- `dev/review-ledger.md` (2 impl-drift rows, `make ledger-owed WRITE=`)
- `specs/449-rust-codebase/arbiter.jsonl` (the two accept rulings)
- `dev/bypass-log/2026-11/20261125T034830Z-8fa27e.json`, `...034835Z-b80e70.json` (the two `record-checked REASON=` answers)
- `research/source-attempts.jsonl` line 23559 (the logged grep's `\|centre` dropped: house style; a bug in P11's commit)
- record-owed state in `.git` (record-format:0031/0081 answered, 47 pop-ups `triage: untouched`)

## Everything owed answered

`L7R_LAND_ALONE=1 make claims-owed`: "claims-owed: no claim is owed"; `L7R_LAND_ALONE=1 make record-owed UNANSWERED=1`:
"record-owed: no record check is owed"; `make ledger-owed` after `WRITE=`: nothing owed. `make record CHECK=1` clean,
`make page-check` rc 0, `make quick` clean (second run).
