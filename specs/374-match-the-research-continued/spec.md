# Feature Specification: Match the research - continued (the rows feature 372 left open)

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=374-match-the-research-continued`)

**Created**: 2026-10-10

**Status**: Draft (specified 2026-10-10 from its filed form) - the open work of feature 372 (itself 328's remainder), moved here at the GM's word for a fresh session

**Affects**: hamlet, magistracy, research record

**Waits on**: 375 (`make tick` refuses a task here while 375 is open - 375's plan D18)

**Input**: `request.md` - the GM, 2026-10-10: wind 372 down and *"move everything we haven't done yet into a differnt feature so
we can resume it in a fresh session"*; feature 328's request and feature 372's carry over unchanged (the usage cap with them,
quoted in `request.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The fixes go on where 372 stopped (Priority: P1)

The GM, back from a fresh start, finds the next rows of 328's ranking being fixed in ranking order, each wave verified as 372's
were, and each batch landing on main as it closes.

**Independent Test**: the ranking's open rows fall wave by wave (`audit/waves.json` marks each with its wave); `make
claims-report` shows their findings gone and no new one; each closed batch's commits are on main.

### User Story 2 - 375's process, in its first real use, measured (Priority: P1)

The waves run under 375's enforced process (decide first, the freeze, the tripwires, the preflight). Where one of its guards
refuses correct work, the guard is fixed here with its test; the first three tasks are measured against 375's SC-003 and SC-004.

**Independent Test**: `make feature-report F=374` shows the first three tasks' red gates, re-checks and BLOCKED reviews;
`measurements.json` holds both carried keys.

### User Story 3 - The GM's decisions are gathered, not waited on (Priority: P2)

What only the GM can decide is collected and put to the GM through `escalation-check` at this feature's end, once every row
the session can fix is done, never blocking the work in between.

**Independent Test**: every held item names what was searched and found; no task waits on an answer while other rows stand open.

### Edge Cases

328's and 372's edge cases hold unchanged: a fix that would change the research instead; a hand-drawn Mode A sheet; a fix that
changes many maps; a newly failing cohort seed is a regression, reverted with its measurement. And from 375: a guard that refuses
correct work is fixed, not escaped (an escape only for a genuinely exempt case, its reason saying why).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (the starting point)**: the work list is everything listed under "What it carries" below - 328's ranking's open
  in-scope rows at 372's close (`specs/328-match-the-research/ranking.json`, rows with no wave and in scope), the held rows, the
  carried items and tooling gaps, the nitpicks. 328's tiers and order stand; a row fixed here is marked with its wave in 328's
  ranking (`audit/waves.json`), waves numbered on from 372's (the first is wave 112), so one ranking stays the one record.
- **FR-002 (the rules carried)**: 372's FR-002 (328's FR-002, FR-003, FR-004, FR-005, FR-008, FR-009 and FR-010) and FR-003
  apply here as written there. 372's FR-003 reads: *"a batch of 4-5 waves closes as 328's did (the gate, the occasions, one
  timing pair and its `perf-audit`) and LANDS when it closes: this feature's tasks are the current batch's, so the open-task
  refusal clears at each close. A batch is never stacked unpushed behind another (the GM's reason for the split). The GM's
  pre-approval of band 3 covered 328's landing only: a batch whose pair reads band 3 is put to the GM for sign-off at once, as
  its own question outside FR-005's hold, and the work goes on to the next wave meanwhile; that batch lands on the sign-off."*
  Amended (2026-10-12) by 375's amendment 5, whose approval reads: *"if it looks like the performance is slowing down to a
  meaningful degree, that's something you can mention when you say that the work has landed on main, but it doesn't need to
  be a gate anymore."* From then on a batch's pair band is a flag stated in its landing message: no `perf-audit` is owed and
  no band-3 sign-off holds the landing (375 FR-023).
  A batch whose pair would time unchanged code records that in its plan section, reviewed as a plan decision, as 372's batches did.
- **FR-003 (the usage cap)**: 328's FR-007 at the cap the GM last set for this work, `90%` of the weekly window (`request.md`:
  *"Let's raise the cap on this work from `85%` to `90%`."*, 2026-10-09), armed with `~/.claude/hooks/usage_cap.py`.
- **FR-004 (decisions)**: a question for the GM is recorded with what was searched and found, and work moves to the next row;
  the held list (below, "Every decision still owed to the GM") is put to the GM through `escalation-check` at the feature's
  end, once every row the session can fix is done (328's goal amendment: defer it to the end of the feature).
- **FR-005 (375's tooling)**: no wave is taken until 375 has landed (its status line opens `Done`). When one of 375's guards
  refuses correct work, the guard is fixed in this feature with its test (constitution XIV), never escaped to keep going; an
  escape is for a genuinely exempt case and its reason says why.
- **FR-006 (375's carried measurements)**: SC-003 and SC-004 of 375 (below, SC-004 and SC-005 here) are measured over this
  feature's first three tasks, each by a named task of `tasks.md` that is not among the three; the feature cannot close until
  both keys are in its `measurements.json`.
- **FR-007 (the carried tooling gaps)**: each tooling gap under "What it carries" is fixed with a test that is red on the old
  code, no later than the first wave whose work it would affect (the glyph-check keying before the first batch whose occasions
  check one element on two sheets), or recorded as already fixed with the evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): after each wave, every row it took re-checks IN-STEP under `impl-drift`, and `make claims-report`'s
  count of in-scope findings falls by at least that many with no new one.
- **SC-002** (FR-002): every closed batch is on main, its gate green, its pair band recorded (audited before 375 amendment 5; after it, stated at landing) (or its plan section's
  reviewed record that the pair would time unchanged code).
- **SC-003** (FR-001, FR-003, FR-004): at the end, `make claims-report` shows 0 in-scope findings outside the DEFERRED units; the held
  list goes to the GM once every row the session can fix is done, the feature closes after the answers are applied, and a row the
  GM rules should stay as it is becomes a Decisions Recorded row, not a DRIFTED one. At the cap, the clone holds no uncommitted
  work and no unrecorded verdict.
- **SC-004** (FR-006; 375's SC-003, key `sc003-375-first-three-tasks`): in this feature's first three tasks, no red gate from a
  cause 375's preflight checks, no page re-checked while a check on it was outstanding, no plan-review BLOCK on a decision the
  decision preflight had ruled on.
- **SC-005** (FR-006; 375's SC-004, key `sc004-375-dispatches-per-row`): the dispatches per closed row of those three tasks,
  measured beside 372's ~10 - 375's spec, "Why": about 120 dispatches for about a dozen ranked rows in 372's waves 105-111,
  counted from that session's record (2026-10-10), an estimate, not a measurement key.
- **SC-006** (FR-007): every carried tooling gap is closed by a test red on the old code, or recorded as already closed with
  its evidence.
- **SC-007** (FR-005): every refusal of correct work by one of 375's guards in this feature ends in a fix of the guard with a test
  red on the old guard, and every escape this feature passes carries a reason naming why its case is genuinely exempt (`make
  guard-log`).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Doors keep their drawn sizes (the hand sheets' doors and the generated door, as 0117's drawing page records them); no door band in `types.json` | drawing convention | the GM, 2026-10-12: *"for the door band question, I am okay with what is currently implemented."* | `research/questions/0117-doorways-and-doors-to.drawing.html`; the ranking row `types.json#door band` (wave 122) |
| A spec's household-shrine floor stands over 0219's share: the share is a countryside rate, so one shrine in a small hamlet is within it | historically accurate (the share read as a rate) | the GM, 2026-10-12: *"it is fine for a floor to take precedence over the cap. So if we say this hamlet has one shrine, then that is okay. And that's not even a deviation"* | `research/questions/0219-household-shrines-yashikigami.drawing.html`; `fixtures.py::fixture_quota` (wave 122) |

| Niigata's living-tree rack posts and Ehime's racks standing all year are not drawn (wave 137) | historically accurate (no premodern record of either) | two search passes (the archive, Japanese and Chinese sources, 280's D1 cutoffs) found both only in undated modern records; the GM's rule of 2026-09-28 draws no form attested only in modern times | research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html; `hamletgen/consts.py` HARVEST_WEATHERS |
| A brook running along the cluster offers the fifth lane shape, the lane along the water, rolled among five (wave 138) | guess (the five shapes, and "along" as a brook within `WATER_ALONG_FT` of a flank over `WATER_ALONG_SHARE` of it) | 0031's drawing page gives five shapes, the fifth needing water along the cluster, and names no band | research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html; `hamletgen/consts.py` WATER_ALONG_FT; `hamletgen/ways/web.py` |
| A dike-pond hamlet rolls its ponds' layout, the mosaic two in three, the chessboard one in three (wave 139) | historically accurate (both attested), the odds a guess | Qu Dajun's Guangdong xinyu (1678) records the chessboard of ponds at Jiujiang; the mosaic is the delta's accreted form | research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html; `hamletgen/consts.py` POND_LAYOUTS |
| A dike-pond hamlet with no grow-out pond in a household's reach keeps no sty and records why (wave 140) | historically accurate | 0025: a sty stands within a household's reach, and a household with no pond within reach keeps none; the floor of one sty was the code's own | research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html; `hamletgen/pondstock.py` |
| The polder and the dike-pond stay out of the roll (wave 141): the dike-pond with one seed still refused after the fixes, the polder with two; row 771 open, T33 lands open | deliberate deviation, held by the round arbiter (route B) | the constant's own bar: no form rolled with open failures; the rolls are in measurements.json | research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html; `hamletgen/consts.py` ROLLED_ARCHETYPES |
| A web lane's no-build room is read as a half-width, half the lane room each side of its middle (wave 142) | map drawing convention | 0246's lane room, a garden fence's room each side of a tread, halved for each side of the middle | research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html; `hamletgen/consts.py` WEB_CLEARANCE |
| A web lane runs on the bund against the crop, kept half the widest tread laid there off it, and a wider gap off the toe and marsh (wave 143) | historically accurate (the crop), unresearched (the toe and marsh gap) | 0081: a lane may touch a plot's boundary, never crosses row crops; the record gives no distance off wet ground | research/questions/0081-village-lanes.drawing.html; `hamletgen/consts.py` WEB_CROP_GAP, WEB_HARD_GAP |
| A hamlet whose fields reach the far edge of its map draws no wood; the wood's bearing is recorded off the sheet (wave 145) | map drawing convention | 0077 puts the wood beyond the fields, the frame stays tight to the settlement (feature 287 D11, the GM's approval), and every open seat left inside such a frame stands on the houses' side | research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html; `hamletgen/hinterland/stages.py` woodland_on_the_sheet |
| A grove farm's fixtures keep off its way in and its door's room; a door path or a street join closing a sliver is refused (wave 146) - with polder seed 4 newly refused, a known regression waived by the round arbiter (ask:b10-w146-polder4-regression) on the unrolled polder form | historically accurate (the way in at the open front); the regression a recorded deviation | 0036: the way in by the open front; the polder is not rolled until every seed is green | research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html; `settlement/homestead_parts/fixture_seats.py`; `tests/soak/test_row_village_doors.py` |
| Now and then a hamlet on a grass-hill map draws a small grass hill above one paddy, the tazuke kusayama (wave 148) | historically accurate (the form), guess (how often) | 0078: sometimes a small grass hill was set aside for one paddy; the rate is one hamlet in three, a guess the page names | research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html; `hamletgen/hinterland/paddy_grass.py` PADDY_GRASS_ODDS |
| The paddy's grass hill is about one plot's own area, seated just above a plot at the field's top, none where no such ground is free (wave 148) | guess (the size); the seat from the page's rule | 0078's drawing page: about the paddy's own size, on the slope above it; measured seated on every map that rolled it | research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html; `hamletgen/hinterland/paddy_grass.py` seat_paddy_grass |
| The paddy's grass hill goes above the first of the field's top plots with room, as an unturned square (wave 148) | guess (which paddy; its shape) | 0078 says neither which paddy keeps one nor its shape; both labeled UNRESEARCHED at the code | research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html; `hamletgen/hinterland/paddy_grass.py` seat_paddy_grass |
| The paddy's grass hill is drawn as a cut sward on a fresh-green ground (wave 148) | map drawing convention (the tint and the thinned tufts) | on the scrub's own tile it could not be told from the scrub (the glyph check of Inashiro); the real slope shows only its shorter grass | `settlement/land/tiles.py` cut_grass_tile, CUT_GRASS_TINT |
| A farm's bamboo strip is seated after the web, as before; seating it with the sheds and gardens is deferred (wave 149) | deferred (a measured wait), not a ruled deviation - the order still owed, the claim left DRIFTED, row 777 on the held list for the GM | five routes ahead of the ways each moved a refusal into the pool or the cohort (`m:w149-route-matrix`); the round arbiter (ask:b13-w149-route-matrix) kept the order, the row waiting on the web settle | research/questions/0075-bamboo-groves-chikurin.drawing.html; `hamletgen/homesteads/bamboo.py` seat_strips |
| A strip is tested against each seated part, not its own farm's whole bundle, and offered stepped out along its side, three strip depths at most (wave 149) | guess (the reach); a defect fixed (the bundle box refused every strip, the pool drawing none) | no page gives how far a farm's bamboo stood from its house; the farms with no room are filed for the bundle packer (`m:w149-strips`) | `hamletgen/homesteads/bamboo.py` STRIP_STEPS_OUT, seat_strips |

(Each wave adds its rows, as 372's did.)

## Assumptions

- 328's records (`ranking.json`, `measurements.json`, `audit/`, `claims-followup.md`) are the starting state and stay in
  328's directory; this feature's measurements are its own `measurements.json`.
- The cohort baseline is 328's 52 of 54 (`make cohort N=48`, seeds 10 and 20 refused; m:wave95-overrun-floor in 328's
  `measurements.json`), re-measured before the first engine edit of the hamlet's stages.
- The ranking's order is the work's order; a row whose `after` is open waits for it, and a `Held` row waits for the GM.

## What it carries

- **The open rows of 328's ranking** (`specs/328-match-the-research/ranking.json`, rebuilt by `audit/merge.py`): 198 rows in
  scope at 372's close - 153 E3, 43 E4 (a research pass under the record's own checks before any code change), 2 E2 - in
  ranking order. The found rows 372's waves filed (`audit/found-wave105.jsonl` to `found-wave108.jsonl`) are among them.
  Every easy row (E0, E1) is done; what is left is redraw and research work.
- **Three rows held for the GM**, flagged `Held` in the ranking (`audit/overrides.json`): the door band (0117 records the hand
  sheets' 8-8.7 ft doors as a convention, against the GM's true-size rule); `fixture_quota`; and `one tub per wooden building`
  (waiting on `#senior retainers housed apart`).
- **Every decision still owed to the GM**: 372's spec, "What it carries" (328's held section, the Mode A wells as markers,
  wave 97's charcoal store), and ranking row 777 (wave 149: the farm's bamboo strip seated after the web, its order with the
  sheds and gardens deferred behind the web settle's found row by the round arbiter, ask:b13-w149-route-matrix - the GM's
  question whether 0075's drawing page binds the order or only its result) - put to the GM at this feature's end, through
  `escalation-check` (FR-004).
- **Carried from 372's spec unchanged**: the claims-gate findings counted as introduced at 328's landing; Sawada's zigzag
  (waived for landing, an open E3 row); the 40-household seed 25 knot; Ochiba's garrison privy haul (a research item on 0101
  and 0090).
- **Tooling gaps**:
  - a glyph-check verdict is keyed by element alone, so a second sheet's check overwrites the first's (372's spec);
  - `make modal-bundle FOR=modal-depiction`'s crop on a Mode A sheet paints the page's highlight, not the drawn fill (372);
  - `pack_audit`'s `passage_blockers` misses a tub 0.2 px outside a gate passage's rect (wave 106, Ubame's gate-range tub);
  - the claims-triage reply parser counts the word "TOUCHES" anywhere in a reply as a touched claim (wave 108);
  - a `yosui-oke` glossary entry would keep the `yosui` tooltip off that word in 0100's notes (record-format, wave 106).
- **Nitpicks left at 372's reviews**: Ochiba's bath steam arcs drawn for the old 13 x 11 room (wave 108); Ubame's reception
  tubs mirrored about the shoe stone (wave 106).

## How it starts

**Feature 375 first** (`specs/375-enforced-wave-process/spec.md`): the wave process this feature runs on is enforced by the
tooling there - content-scoped record checks, line-scoped claims, decide-then-freeze, a preflight inside the gate. Take no wave
here until 375 has landed.

375's tooling is in its first real use here. When one of its guards refuses correct work, fix the guard in this feature
(with its test), as constitution XIV asks; never escape it just to keep going. An escape is for a case that is genuinely
exempt, and its reason says why (the GM, 2026-10-10).

**Carried from 375** (its FR-014; this feature cannot close until both keys are in its `measurements.json`): SC-003 -
in this feature's first three tasks, no red gate from a cause 375's preflight checks, no page re-checked while a check on it
was outstanding, no plan-review BLOCK on a decision the decision preflight had ruled on (key `sc003-375-first-three-tasks`);
SC-004 - the dispatches per closed row of those three tasks, beside 372's ~10 (key `sc004-375-dispatches-per-row`). Each is a
named task of this feature's `tasks.md`, and those two measuring tasks are not among the three measured.

`make claim` is done (this directory). Next: `/speckit-specify` over this file and `request.md`, then plan and tasks in
waves, as 372 did (`specs/372-match-the-research-remaining/` is the worked example). Re-arm the usage cap with the GM's
current figure before the first wave.

## Review history

- Round 1 (spec-fidelity MODE 2, 2026-10-10): CHANGES REQUIRED - (1) FR-002 said "as written there" yet added a condition to
  372's FR-003's timing pair: 372's FR-003 now quoted verbatim, "none owed" a reviewed plan decision; (2) FR-004 asked the GM at
  the start too: at the feature's end only (328's goal amendment), User Story 3 and "What it carries" matched; (3) `85%`
  backticked in FR-003's quote (spec-lint check 5); (4) SC-005's ~10 labeled as 375's "Why" estimate. Asides left as asides:
  no country-shrine Affects tag (328's FR-010 carries the scope); the filed guard rule's "(the GM, 2026-10-10)" is the filed
  spec's record, not verbatim words.
- Round 2 (spec-fidelity, verify, 2026-10-10): FAITHFUL - all four items confirmed in the diff; spec-lint exits 0.
- Amendment 1 (2026-10-10, at the plan): spec-lint found FR-003 and FR-005 named by no success criterion - SC-003 now cites
  FR-003 (its at-the-cap clause), and SC-007 is FR-005's (a guard fixed with its test, an escape's reason naming its exemption).
  Put to the plan review with the plan.
- Amendment 2 (2026-10-12, at batch 3's close): the plan review of that date found FR-002 still quoting 372's band-3 sign-off,
  which 375's amendment 5 replaced - FR-002 now records the replacement with the GM's words, and SC-002 says a band is stated
  at landing after it.
- Exception check (spec-fidelity MODE 1, 2026-10-12, wave 149): LEGITIMATE as a deferral, not as an exception - deferring
  row 777's order behind the web settle's row rests on 328's accepted edge cases (a newly failing cohort seed is reverted; a
  fix that changes many maps waits on a found row with its claim as found), measured (`m:w149-route-matrix`) and ruled by the
  round arbiter (ask:b13-w149-route-matrix); not put to the GM now. Owed with it, done: the found rows in 328's ranking
  (`audit/found-wave149.jsonl`), row 777 held behind the settle row (`audit/overrides.json`, E4), the row's class worded as a
  wait, and row 777 among the decisions owed to the GM.

**Implementation check** (feature 378): owed at its close - each question whose findings this feature changes is cited by a checked `Research:` claim of the code that decides it, or recorded in `implementation-check.md` as implemented nowhere; `make impl-check F=374` says what is owed. The code is fixed only where this spec asks.
