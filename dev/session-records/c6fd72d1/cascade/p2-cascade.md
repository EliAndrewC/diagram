# P2 cascade (449 T425: 0068, 0058, 0072, 0059 - the hamlet water pages)

Clone /diagram/.clones/diagram-backlog at 025b979544 (P2's commit; 10 changed lines). Coordinated 2026-11-24. Bundles and
replies: /tmp/p2c/ (claims-owed, directed-a, directed-b, arbiter; `<bundle>.reply.md` beside each). No rust/ file edited; nothing
staged, committed, landed or pushed.

## Stage 1 - claims

| step | count |
|---|---|
| `make claims-owed` before | 38 claims: 34 "triage", 4 "rests changed"; plus one standing `claims-label` notice (polder.rs `ditches#the ring canal on a dike-pond block`, not P2's) |
| `make claims-triage` | the TOOL cleared all 34 ("a page each cites moved and no block it rests on did", 432 FR-005 a). No bundle, no `claims-triage` agent, no `claims-triaged` |
| `make claims-owed` after | 4 owed, all "rests changed" (no triage for them: known rule iii) |
| impl-drift, owed (1 dispatch, 37k tokens, 35 s) | 4 verdicts: 2 IN-STEP, 2 DRIFTED (both fix: claim, effect: none); `claims-checked`: 4 of 4 recorded |
| directed A (1 dispatch, 52k tokens, 54 s; PAGES 0068 + 0058 drawing) | 6 verdicts: 6 IN-STEP; `claims-checked`: 6 of 6 recorded, one rest on an uncited page dropped |
| directed B (1 dispatch, 34k tokens, 56 s; PAGES 0059 drawing) | 5 verdicts: 2 IN-STEP, 1 DRIFTED (fix: claim), 1 MISLABELED, 1 CANNOT-TELL; `claims-checked`: prints "5 of 5 recorded" but recorded 4 - the CANNOT-TELL line HELD (451 T218), exit 3 |
| `make claims-owed` at the end | "no claim is owed" |

Dispatch refusals on the way (each named its compliant command):
1. decide-first (375 FR-003a): "449-rust-codebase T425: its plan section carries no current CLEAR verdict". Repeated with
   `DECIDE_OK="the coordinator's brief directs this claims check of a page session's cascade; T425 is a page correction worked
   from a brief, with no plan decisions to rule"` (the check session used the same escape).
2. tripwire `cascade@1`: "11 check dispatches over 10 changed lines" (the 11 are P2's own record checks). `make arbiter-bundle
   TRIGGER=cascade@1`, `round-arbiter` (1 dispatch, 29k tokens, 128 s): ruling **continue** - "The 11 record checks over 10
   changed lines are the floor for four pages edited, not a cascade ... One round of exactly three dispatches, each once ...
   Sort each verdict that is not IN-STEP by constitution XIV ... anything they catch that claims-owed missed is the under-reach
   result to report". Recorded by the agent in specs/449-rust-codebase/arbiter.jsonl.

### The owed round's verdicts (bundle /tmp/p2c/claims-owed)

- `rust/phases/src/field/channels.rs::SUPPLY_W#supply canals` **DRIFTED** - "(4.5, 4.0) matches the page ... But the claim still
  quotes the page as "4.0 -> 1.5 along the far edge" and adds a note that "the page's 'far edge' is the brook's flank here". The
  page now says "supply canal down the brook's flank", so the claim misquotes it. fix: claim (restate as "4.0 -> 1.5 down the
  brook's flank" and drop the note); effect: none [§14, §15, §17, §18]"
- `rust/phases/src/field/channels.rs::channels#the widths by role` **IN-STEP** - "canal A on the upper edge, canal B down the
  brook's flank, as the page has them"
- `rust/phases/src/field/channels.rs::division#the fork` **DRIFTED** - "the fork code is right ... But the claim quotes the page's
  split as "one along the far edge" and calls canal B "the page's far-edge canal". The page now names that canal "supply canal
  down the brook's flank". fix: claim (restate as "a supply canal along the upper edge and one down the brook's flank" and drop
  "the page's far-edge canal"); effect: none [§14, §17, §26]"
- `rust/phases/src/seat/margins.rs::ranked#not on the wet toe` **IN-STEP** - "a margin is refused when the seat center or its
  anchor falls inside the marsh polygon below the fields, so the houses keep off the drawn marsh as the page requires"

### The directed check (known gap i) - labeled DIRECTED: each prompt said the bundle carried changed pages the claims do not cite

Picked by grep of dev/claims-index.json (claims stating where a supply canal runs, the wet band, the brook below an intake),
excluding the 4 owed. Bundle A, PAGES = 0068 + 0058 drawing - all six IN-STEP:
- `channels.rs::channels#the canals' courses` (cites 0053) - "the uncited 0068 drawing page's table names them the same way
  (upper edge, brook's flank)". `claims-checked` dropped its rest on 0068 ("a page it does not cite - dropped").
- `channels.rs::channels#the comb` (cites 0053, 0054); `polder.rs::ditches#the far flank` (cites 0068, tool-cleared).
- `margins.rs::ranked#not in the reed fringe`, `ranked#no drain rule at the seat` (cite 0058, tool-cleared) - "the edited 0058
  page still does not count the fringe as marsh"; "still scopes that rule to dispersed farmsteads".
- `driver/toe.rs::PAD#toe band edge` (cites 0057) - "the edited, uncited 0058 page agrees".

Bundle B, PAGES = 0059 drawing:
- `field/brook.rs::brook#the tap's stride` (cites 0059, TOOL-CLEARED) **DRIFTED** - "the cited drawing page now records that
  figure ("About 70 ft on the maps ... The figure is a GUESS, ours for the drawing"), so it is no longer "silent"; fix: claim
  (GUESS: 0059 drawing page §7 records the ~70 ft hold below a shoulder intake as our guess; no source gives the distance);
  effect: none [§7]"
- `driver.rs::BROOK_TAP_RUN#the brook's course` (cites 0054 only) **MISLABELED** - "the 70 ft is exactly the figure the 0059
  drawing page §7 records as a GUESS ... The claim points instead to 0054's drawing page and to the deleted `consts_water.py`,
  and it lists slew, skirt and wander, which this constant does not set. The label should be GUESS question 0059 (abbreviated in the session record)
  drawing.html (the tap's stride, ~70 ft)"
- `field/brook.rs::brook#outside the crop` (cites no page) **CANNOT-TELL**, HELD by T218 (not recorded, not filed) - ""out at
  once below a shoulder intake" applies inside the tap stride too (`want` outward sets `x = want` before the `tap_run` test),
  while the 0059 drawing page now says the brook "holds the intake's line that far". To judge this I need `BROOK_SKIRT` and the
  range of `lead` and `offtake_deg`".
  MY READ of the code, with its constants (no dispatch; the arbiter allowed three). The intake stands `lead * sin` outside
  the head's corner and `run * cos` above the head line; `HEAD_LEAD` is 80/105/130 ft, `BROOK_SKIRT` 34 ft, the angle 35 degrees.
  - BEND-sited (sin 35 = 0.574): the intake is 46 to 75 ft outside the corner against a skirt line 34 ft (times the flank's
    secant) outside it, so the brook starts at least about 10 ft OUTSIDE its line and holds there; the stride (70 ft from 65,
    86 or 106 ft above the head) ends within 5 ft below the head line or above it, where the flank is the corner's. The page's
    "holds the intake's line that far" is true.
  - STRAIGHT-sited (`intake_siting = straight`): the angle is less the wave's lean, atan(6 * tau / 80) = 25.2 degrees
    (`MEANDER_FT` 12, `MEANDER_WAVE_FT` 80), so sin(9.8) = 0.170 and the intake is only 14 to 22 ft outside the corner - INSIDE
    the 34 ft skirt line. `(want - x) * side > 0` is then true at the first station and the course's base line steps OUT 12 to
    20 ft at once, inside the stride. For a straight-sited shoulder intake the page's new sentence is literally untrue; the
    claim's "out at once below a shoulder intake" is the true one there.
  Arithmetic from the constants, not measured on a drawn map. No wrong outcome is shown (the brook steps away from the
  fields, as the skirt asks), so by XIV this is a restatement: of 0059's item ("does not move in toward the fields for about
  70 ft; from a straight-sited intake it steps out to its margin first"), offered to the coordinator as a possible page
  restatement, and of the claim (below).
- `brook#the shoulder intake`, `brook#on past the intake` (cite 0059, tool-cleared): IN-STEP.
- NOTED, NOT FILED by the agent: brook.rs's comment "a straight stride at the tap, measured on 120 rolls, ran 110-160 ft straight
  against 0054's ten widths" predates the 70 ft hold; a stale comment.
- No hamlet claim places a WELL against the wet strip (grep of the index: none under rust/phases), so 0058's well sentence has
  no claim to re-check.

## Stage 2 - pop-ups

| step | count |
|---|---|
| `make record-owed` | 38 units by the delta: 11 record units `[answered]` (P2's), 27 `modal-depiction` unanswered. None of the 27 names a 0072 page |
| `make modal-triage` | "27 unit(s) cleared by the tool (no claim-bearing change); no agent is owed". No `modal-triage` agent, no `modal-triaged` |
| checks sent on | 0. No modal-form, modal-research or modal-depiction dispatch; no `record-checked`; no `apply-edits`; no EDIT; no second round |
| `make record-owed UNANSWERED=1` | "no record check is owed" |

The 27: by page - 0058: six `choice/cluster_position--*`, `hamlet/marsh` (7); 0059: 16; 0068: 7; `choice/intake--open`,
`hamlet/irrigation-ditch`, `hamlet/stream` name two of the pages (7 + 16 + 7 - 3 = 27).

## Stage 3 - gates

`make record CHECK=1`: "builds cleanly (4380 page(s))", exit 0. `make quick`: "quick: clean", exit 0.

## Stage 4 - ledger

`make ledger-owed`: printed nothing, exit 0. `make ledger-owed WRITE="<this file>"`: "0 row(s) written for c6fd72d1-...". So
the four dispatches of this round (3 impl-drift, 1 round-arbiter) have NO row in dev/review-ledger.md (P1's round wrote 9, P7's
11). Cause not found. Checked: the dispatches ARE in the clone's log (.git/l7r-events/449-rust-codebase.jsonl and
.git/l7r-agent-prompts hold the directed-a prompt), so they were not logged to the /diagram mirror. A stated hole, not fixed.

## Final readings

`L7R_LAND_ALONE=1 make claims-owed`: "no claim is owed". `L7R_LAND_ALONE=1 make record-owed UNANSWERED=1`: "no record check is
owed". "other builders' uncommitted code" lines: 0. `make claims-report` now lists the four new findings (2 DRIFTED on
channels.rs, DRIFTED `brook#the tap's stride`, MISLABELED `BROOK_TAP_RUN`).

## PREDICTED vs ACTUAL

| predicted | actual |
|---|---|
| 0068: re-check `hamlet/irrigation-ditch` | tool-cleared, unread. Right outcome (it says "one along each high flank", never "far edge") |
| 0068: claim `SUPPLY_W#supply canals` | owed (rests changed), DRIFTED fix: claim - the prediction's point |
| 0068: at most `polder.rs ditches#the far flank` | tool-cleared; directed read IN-STEP |
| 0068: the other 13 claims clear | 11 cleared; TWO MORE were owed: `channels#the widths by role` (IN-STEP) and `division#the fork` (DRIFTED - it quotes "far edge" itself, so the prediction missed it, not an over-cascade) |
| 0068: six other pop-ups clear | cleared (tool) |
| 0058: claim `ranked#not on the wet toe`, IN-STEP | owed, IN-STEP |
| 0058: `hamlet/marsh`, six cluster pop-ups, two other claims clear | all cleared (tool) |
| 0072: all 15 pop-up units and 15 claims clear at triage | better: 0072 sent NOTHING on - no 0072 pop-up unit was ever listed, and no 0072 claim appears in the 38 |
| 0059: claim `brook#the tap's stride` re-checked | NOT owed - tool-cleared (its "silent" rests on no block; the NEW block is no block it rests on). The directed read: DRIFTED fix: claim |
| 0059: perhaps `brook#the shoulder intake` | tool-cleared; directed IN-STEP |
| 0059: pop-ups `intake_place--shoulder`, `hamlet/stream` re-checked, IN-STEP expected | tool-cleared, unread. My read: both agree (below) |
| 0059: 14 other pop-ups, 18 other claims clear | cleared |
| (not predicted) | `driver.rs BROOK_TAP_RUN` MISLABELED (the constant that IS the 70 ft, citing 0054); `brook#outside the crop` CANNOT-TELL; the cascade@1 tripwire |

Cost: 4 dispatches, about 152k subagent tokens, under 5 minutes of agent time; 0 EDITs to any pop-up or page.

## Judgment

(a) Over-cascade: essentially none - the leanest of the three watched cascades.
- 0072's notes-only edit sent NOTHING on: no claim and no pop-up unit named a 0072 page at any step (not even a tool-cleared
  listing). Correct.
- The owed round read 4 claims; 2 held the changed words and were rightly found, 1 was the predicted IN-STEP confirmation
  (`ranked#not on the wet toe`), and 1 (`channels#the widths by role`, IN-STEP) was sent on only because the block it rests on is
  the changed table row (rule iii: no triage for "rests changed"). One spare claim inside a bundle that was going anyway.
- No pop-up was read by an agent, so chain (iv) (research EDIT -> whole-pop-up form read) had no occasion; nothing was reworded
  beyond the change.
- The one cost with no yield was the `cascade@1` tripwire: it counted P2's own 11 record checks against its 10 lines and held the
  FIRST claims dispatch for a ruling (29k tokens, 2 min, "continue"). Four pages owe at least three checks each; a floor of that
  kind always exceeds 1.0 a changed line on a small wording fix. The guard fired as written and named its command; the rule is
  miscalibrated for page sessions (dispatches per changed PAGE or unit would not have fired).
- The directed check (11 claims, 86k tokens) was mine by the brief, not the tooling's: 8 of 11 IN-STEP.

(b) Under-cascade: two real misses on the claims side, none on the pop-ups' truth.
- CLAIMS. The owed round found the two "far edge" claims but missed everything about the NEW 0059 item:
  1. `brook#the tap's stride` cites the changed page and says it is "silent on how far below a shoulder intake the brook keeps
     its line"; the page now answers exactly that, and the tool CLEARED the claim, because a GUESS-silent claim rests on no block
     and a new block is not "a block it rests on". This is P1's "stale silent" pattern, here the one claim the page change was
     written for.
  2. `driver.rs BROOK_TAP_RUN#the brook's course` - the constant that holds the 70 ft - cites 0054 and could never be re-owed by
     0059 (known gap i). MISLABELED.
  3. `brook#outside the crop` cites no page; its "out at once below a shoulder intake" now sits beside a page sentence that says
     the line is held. CANNOT-TELL, see my read above: a wording matter, no wrong map.
  For 0068 and 0058 the owed round's reach was SUFFICIENT: the six directed claims are IN-STEP.
- POP-UPS, read by me (all 27 were cleared unread):
  - `hamlet/irrigation-ditch`: "forks at the head of the paddies into two supply canals, one along each high flank". No "far
    edge" anywhere; agrees with 0068 as corrected.
  - `hamlet/stream`: "passing the head of the paddies on one side and running on down that flank"; gives no distance. Agrees.
    Its Guesses tab holds only the 5.25 ft width.
  - `choice/intake_place--shoulder`: Depiction "the brook running on down that flank outside the fields"; Guesses "That the brook
    runs on down the flank of the fields below the intake's shoulder: no source describes the brook's course past the fields" and
    `{0054#head-race-leaves-brook}`. Agrees; no distance.
  - `hamlet/marsh` (the wet-band pop-up): "builds nothing on it, the ground being too wet". The six `cluster_position--*`
    pop-ups each say "off any drawn marsh". NONE says the wet strip is built on; the page's old "farmed and built on" was the odd
    one out, and the correction brought the page to the pop-ups. `hamlet/well` and `choice/well_siting--cluster` do not name
    0058's drawing page and say nothing of the wet strip.
  - grep over all hamlet and choice pop-ups and docs/*.md for built on / build on / builds beside marsh, wet, toe, reed,
    lowest: one hit, hamlet/marsh's "builds nothing on it". "far edge" in the record's 0053, 0054, 0059, 0068 pages: 0 hits.
  - grep over every modal: "far edge" 0 hits; "70 ft" / `brook-line-below-intake` / "holds the intake" 0 hits.
- KNOWN GAP (ii), 451 T226, CONFIRMED a third time: the new GUESS item `brook-line-below-intake` (70 ft) reaches NO pop-up.
  Neither `hamlet/stream` nor `choice/intake_place--shoulder` states it on its Guesses tab, and here not even a check read them
  (the tool's "no claim-bearing change" treats a new GUESS item as bearing on nothing). Candidate, NOT added (no check's EDIT
  proposed it): a Guesses bullet `{0059#brook-line-below-intake}` on `choice/intake_place--shoulder` (the pop-up of the knob the
  guess belongs to), perhaps on `hamlet/stream`.
- 0059's new sentence is literally untrue for a STRAIGHT-sited shoulder intake (my read under stage 1): found only because the
  directed check read a claim that cites no page.
- The check handoff's open item stands: the absence note on the 70 ft rests on a grep of 0059's own pages only; no search pass.

(c) Rules that fired.
- 432 FR-005 a (claims cleared by the tool where no rested block moved): fired on 34 of 38; right on 33 by the directed
  evidence, wrong in effect on `brook#the tap's stride` (see b1). The rule cannot see a claim whose "silent" a new block ends.
- Rule (iii) ("rests changed" skips triage): fired on 4; one spare IN-STEP read. Behaved, cheap.
- Modal-triage's tool pass: cleared 27 of 27 with no agent. Right on the facts (nothing in any pop-up contradicts the pages);
  it is also why T226 stays invisible.
- 375 FR-003a decide-first: fired on T425's own missing CLEAR verdict (not "the clone's other task" as the brief expected);
  escape DECIDE_OK used with a stated reason, as the check session did. A page-session task has no plan section to rule, so
  this refusal is noise for every page session's checks.
- The cascade tripwire `cascade@1`: fired, arbiter ruled continue; see (a).
- 451 T218 (hold a "pages are silent" finding): FIRED for the first time in the three cascades, on the CANNOT-TELL line, and
  named 0060's drawing page (field drains) as the record's nearest page. Misdirected: the line does not say the pages are
  silent on a finding - it asks for code constants (`BROOK_SKIRT`, `lead`, `offtake_deg`) the bundle did not carry; 0060 would
  not settle it. `claims-checked` printed "5 of 5 recorded" (4 were) AND "no verdict for ... - it stays owed" AND exit 3, while
  `make claims-owed` then reads "no claim is owed" (a REASON= re-check is never owed): three statements that do not agree. Not
  re-dispatched: the arbiter's ruling allowed three dispatches, each once, and the question was answered by reading the code.
- 451 T219 (outside notes listed, not filed): the NOTED, NOT FILED comment line filed nothing (found.jsonl unchanged, 6 rows).
- "rests on a page it does not cite - dropped": fired once (`channels#the canals' courses`, 0068), as in P1.
- 451 T220/T221: no occasion in the owed round. The three corrected-claim verdicts (2 DRIFTED + 1 from the directed read) and
  the MISLABELED now stand in the index until the restatements land.
- T188, T195/T228, apply-edits: no occasion (no pop-up check ran).
- `make ledger-owed`: wrote 0 rows for 4 dispatches (stage 4) - a hole, if the ledger is meant to hold every pass.

## Rust claims to restate (for the one builder; none done here)

1. `rust/phases/src/field/channels.rs::SUPPLY_W#supply canals` (DRIFTED, fix: claim) - say "4.5 -> 1.5 along the upper edge,
   4.0 -> 1.5 down the brook's flank - the 4.5 ft canal A's, along the head and down the far flank; the 4.0 ft canal B's"; drop
   "(the page's "far edge" is the brook's flank here)". Cite 0068 drawing, the ladder's table row "supply canal down the brook's flank".
2. `rust/phases/src/field/channels.rs::division#the fork` (DRIFTED, fix: claim) - "the head race splits into a supply canal along
   the upper edge and one down the brook's flank - canal A along the head and down the far flank, canal B (the 4.0 ft one) down
   the brook's flank"; drop "the page's far-edge canal". Same 0068 row.
3. `rust/phases/src/field/brook.rs::brook#the tap's stride` (DRIFTED, fix: claim) - no longer "silent": "GUESS
   question 0059 (abbreviated in the session record): the brook holds the intake's line about 70 ft below a shoulder intake, the page's
   guess; the plan's tap stride, none in toward the flank's line across it". Cite 0059 drawing item `brook-line-below-intake`.
4. `rust/phases/src/driver.rs::BROOK_TAP_RUN#the brook's course` (MISLABELED) - relabel `GUESS question 0059 (abbreviated in the session record)
   drawing.html` for the 70 ft (item `brook-line-below-intake`); the slew, skirt, wander and station constants' "as
   `BROOK_TAP_RUN`'s" then need their own account (0054 silent on them), since the lead claim no longer speaks for them.
5. `rust/phases/src/field/brook.rs::brook#outside the crop` (CANNOT-TELL, held, unrecorded) - make "out at once below a shoulder
   intake" agree with the stride: "never in for the tap's stride; out at once where the skirt's line passes it". Cites no page;
   could cite 0059 drawing `brook-line-below-intake` for the stride. True as written for a straight-sited intake.
6. Comment only, brook.rs: "a straight stride at the tap, measured on 120 rolls, ran 110-160 ft straight" is stale beside the
   70 ft (NOTED, NOT FILED).

Also for the coordinator, not rust: the Guesses bullet for the 70 ft (b, gap ii); a possible restatement of 0059's item for
the straight-sited case; the missing ledger rows.

## Is everything owed answered?

Yes: `make claims-owed`, `make record-owed UNANSWERED=1` (plain and L7R_LAND_ALONE=1) and `make ledger-owed` read nothing owed;
`make record CHECK=1` and `make quick` are green. Answered is not closed: `make claims-report` lists the 4 new findings, and
the held CANNOT-TELL is in no record but this file.

## Files changed (uncommitted, unstaged; no rust/ file)

dev/claims-index.json (14 verdicts recorded: 4 + 6 + 4; the held line left `brook#outside the crop` at its IN-STEP of 2026-11-01), dev/claims-pages.json, specs/449-rust-codebase/arbiter.jsonl (1 ruling, written
by the round-arbiter). No pop-up, page or ledger file changed.
