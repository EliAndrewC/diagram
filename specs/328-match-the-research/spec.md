# Feature Specification: The implementation brought to the research, easiest first

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=328-match-the-research`)

**Created**: 2026-10-07

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: rank every finding `make claims-report` shows by how much
implementation work it takes to make the implementation match the research it cites, then fix them from easiest to
hardest, until the weekly usage reaches `85%`.

## Context (measured 2026-10-07)

`make claims-report` at `a52ff1bcd`: 5,893 claims in scope; IN-STEP 5,364; **DRIFTED 439, MISLABELED 50, UNCLAIMED 36,
NEEDS-RESEARCH 20, CANNOT-TELL 20 - 565 findings**; owed 0. The findings sit in two halves: the Mode A procedures
(`buildings.md`, `buildings/programs.md`, ~70 findings, several naming the hand-drawn sheets) and the hamlet engine
(`l7r/diagram/**`, the rest, spread over ~100 modules; the most in `overlap/taxonomy.py`, `settlement/fields/comb.py`,
`settlement/rolling/roll.py`). The report also lists 727 UNRESEARCHED claims; those are labeled honestly as open research
and are not findings (see Scope).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every finding ranked by the work it takes (Priority: P1)

The GM opens the ranking and sees all 565 findings ordered from the least implementation work to the most, each with its
effort tier, the one-line fix it needs, the files it touches, and anything it waits on.

**Why this priority**: the GM made it the first step; every later wave takes its order from it.

**Independent Test**: count the ranking's rows against `make claims-report`'s findings - every finding appears exactly
once, with a tier and a fix line; the order is by tier.

**Acceptance Scenarios**:

1. **Given** the report's 565 findings, **When** the audit completes, **Then** the ranking holds 565 rows, one per
   finding key, none missing, none doubled.
2. **Given** a row, **When** the GM reads it, **Then** it names the tier (E0-E4, defined in FR-003), the change that
   makes the implementation match, the files it touches, and any finding it must follow.

---

### User Story 2 - The fixes made, easiest first (Priority: P1)

The fixes are made in the ranking's order, wave by wave; a fixed claim re-checks IN-STEP and its maps are regenerated.

**Why this priority**: it is the point of the feature ("fix all of it").

**Independent Test**: after a wave, `make claims-report` shows each of the wave's findings IN-STEP (a fresh `impl-drift`
verdict at the new code), the gate is green, and the finding count fell by the wave's size with no new finding.

**Acceptance Scenarios**:

1. **Given** a finding whose implementation disagrees with its cited research, **When** it is fixed, **Then** the
   implementation (the code, or the Mode A procedure and the sheet it draws) is changed to what the research says, and
   `impl-drift` returns IN-STEP for it.
2. **Given** a MISLABELED finding (the implementation already matches; the claim's label or citation is wrong), **When**
   it is fixed, **Then** the claim line is corrected and nothing the map draws changes.
3. **Given** a wave touches what a map draws, **When** it lands, **Then** the affected pool maps are regenerated and any
   review occasion the change opens (a glyph redrawn or re-placed) is run.

---

### User Story 3 - The work stops at the GM's usage cap, cleanly (Priority: P1)

When the weekly usage reaches `85%`, no new work starts; the subagent checks already running finish and are recorded, the
work is committed and the stop-work step run, and the session waits for the GM.

**Independent Test**: the armed cap (`~/.claude/hooks/usage_cap.py`) refuses a new agent, edit or build at `85%`; the
session's last actions are recording the running checks, a commit, and `scripts/sync-with-main.sh done`.

**Acceptance Scenarios**:

1. **Given** usage reaches `85%` mid-wave, **When** checks are running, **Then** they complete and their verdicts are
   recorded; nothing new is dispatched and no gate runs; the clone is committed and its backup branch pushed by the
   stop-work step, which refuses the landing.

### Edge Cases

- **A finding whose fix contradicts another's**: the ranking names the dependency; the later one is fixed after the
  earlier, and a real conflict between two cited pages is a NEEDS-RESEARCH question, not a choice.
- **A finding the research cannot settle** (NEEDS-RESEARCH, CANNOT-TELL, or a fix needing a fact the record lacks): tier
  E4; the research pass runs first (archive, then the web), under the record's own checks; only then is the
  implementation changed.
- **A fix that seems to need the research changed instead** (recording a DEVIATION, or rewording a page to fit the code):
  this is "X except where Y" (constitution XVI). It goes to `spec-fidelity` with the GM's request verbatim; if it agrees,
  it is recorded and raised with the GM once the wave works. The GM's words: *"I'm not sure there's any reason for our
  implementation to not match for anything."*
- **A finding about a hand-drawn Mode A sheet**: the procedure is fixed, and the sheet the finding names is redrawn to
  it (the sheet is what contradicts the page); ranked E3 at least, and governed by FR-009.
- **A fix that changes many maps**: regenerate the pool; a map whose new layout fails the gate is fixed in the same wave -
  and where making the failing map pass takes more work than the row's tier, the row takes that work's tier and waits on a
  found row recorded in the ranking (SC-003); its claim stays as found.
- **A finding that disappears or changes when its neighbor is fixed**: the re-check records what it finds; the ranking is
  not re-sorted mid-wave.
- **New findings a fix exposes**: recorded in the ranking under the tier they take; a finding the wave introduced blocks
  the wave's push (the claims gate already holds this).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (the audit first)**: before any fix, every finding in `make claims-report` (DRIFTED, MISLABELED, UNCLAIMED,
  NEEDS-RESEARCH, CANNOT-TELL) is ranked. The ranking is committed in this feature's directory as a readable table and as
  data a script can count; a test (or a script check) holds one row per finding key at the time of the audit.
- **FR-002 (the measure is implementation work)**: the ranking estimates the work to make the IMPLEMENTATION match the
  cited research - not the work to change the research, and not the finding's importance.
- **FR-003 (tiers)**: each row takes one tier, easiest first:
  - **E0 - the claim alone**: the implementation already matches - `impl-drift` itself says so (MISLABELED), or a page
    already in the record, not edited for this purpose, already says what the code does - and only the claim's label,
    citation or wording is wrong. Any other rewrite of a DRIFTED row's claim is the exception path (FR-004).
  - **E1 - one value**: one number, size or count in the code or the procedure changes; the logic stands.
  - **E2 - one rule**: one function's logic, or one procedure paragraph, changes; one module or one section.
  - **E3 - a form or several places**: a new knob or element, a change across modules, or a hand-drawn sheet redrawn.
  - **E4 - research first**: the record does not yet say what the implementation should be.
  Within a tier, rows are ordered so that findings in the same module sit together (one re-check covers them), and a row
  follows any row it depends on.
- **FR-004 (the direction of a fix)**: a fix changes the implementation to match the research. A fix that would change
  the research instead follows the exception path in Edge Cases. A MISLABELED or E0 fix corrects the claim, which is the
  implementation's own statement of what backs it.
- **FR-005 (verification per fix)**: each fixed finding is re-checked by `impl-drift` (`make claims-bundle` ->
  dispatch -> `make claims-checked`) and is IN-STEP; the gate (`make done`) is green; maps a wave changes are regenerated;
  review occasions it opens are run (feature 294).
- **FR-006 (waves land, inside this one feature)**: the fixes land on main in waves, each a contiguous run of the
  ranking (lowest tier first) that is complete, verified and pushed before the next begins. Feature 328 stays the one
  feature: only the CURRENT wave's rows are task boxes in `tasks.md` (the rest of the ranking stays data in the ranking
  file), so the wave lands once its boxes are ticked (the open-task refusal reads only `tasks.md`'s boxes); the next
  wave's tasks are then appended as an amendment, reviewed on a reset counter.
- **FR-007 (the usage cap)**: the work runs until every finding is fixed or the account's weekly usage reaches `85%`. At
  the cap no new work starts (no agent, no edit in the repository, no build or gate run); the subagent checks already
  running complete and their verdicts are recorded (the reply saved under `/tmp`, then `make claims-checked` /
  `claims-triaged` / `record-checked`); the clone is committed and `scripts/sync-with-main.sh done` run, which at a
  mid-wave stop refuses the landing WITHOUT running the gate and pushes the clone's backup branch; the session waits
  for the GM's word to continue. The cap is enforced by the armed per-goal hook (`~/.claude/hooks/usage_cap.py`, whose
  self-test `test-usage-cap.sh` holds exactly that allow/deny set), not by memory.
- **FR-010 (scope: the code the kept maps execute - amendment 8, the GM 2026-10-07)**: the feature fixes every finding in
  a unit a kept map actually EXECUTES - the scripted hamlets, the magistracy sheets and the country shrine - measured by
  each kept map's own gen-cache entry on today's engine (each function that ran, by path and qualified name, the record
  `tools/hamlet_floor` reads; never a gate test's roll of the legacy village roller, a unit test's roll or a stale entry):
  a function or method a kept map's run executed, a class one of whose methods ran or which executed code constructs or
  names, a module-level constant an executed function reads or an in-use knob's registration reads, a knob in use (an
  executed function resolves the registry's knob by name - `resolve`, `resolve_knob`, `pin_knob`, `KNOBS[...]` - or its typing
  rule ran; a hamlet rolling its own `hamletgen/` table under the knob's name does not put the registry entry in use, that
  table being the kept unit) and a module-level claim on one, any unit under `hamletgen/`
  (the scripted hamlet's own code, which only a scripted hamlet runs, whatever seed or form), a check the gate runs against
  the kept maps' finished output (listed with its reason), and the Mode A procedures; a claim whose value no kept map reads
  though its unit runs is deferred with its measured reason. Every other
  claimed unit - code only the legacy hand-authored villages, towns and cities run - is DEFERRED: its rows stay ranked
  (`scope: deferred`) and no wave takes them, and every such unit is listed in `dev/claims-deferred.json` (derived over every
  claimed unit, not only today's findings, by `audit/scope.py`, re-run when a wave lands), so `make claims-report` shows and
  counts its findings DEFERRED, not DRIFTED, and the push's claims gate does not count them. The legacy settlements' own checks
  are not fixed. The cap rises to `85%` (the GM's words).
- **FR-008 (the record of decisions)**: every fix that changes what a map draws or states is recorded in its class
  (accurate, deviation, convention, guess) at the point of change and in this feature's `spec.md` under Decisions
  Recorded, added by the wave's amendment; the claim line is the pointer.

- **FR-009 (which hand-drawn maps are touched)**: the frozen hand-rolled settlement maps (Hoshigaoka and the other
  legacy villages) are never edited (GM 2026-09-28: *"I do not want you to modify hand-rolled maps"*). A Mode A building
  sheet is redrawn only where a fixed procedure's finding names it; each such sheet is listed by name in its wave's
  tasks and in the report to the GM.

### Key Entities

- **Finding**: a claim key (`<file>::<unit>#<claim>`), its verdict, and the reason `impl-drift` gave.
- **Ranking row**: a finding plus its tier, its one-line fix, the files it touches, what it depends on, and the wave
  that fixed it (blank until then).
- **Wave**: a contiguous run of ranking rows fixed, verified and landed together.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003): the ranking holds exactly the 565 findings of the audit's report, each once, each tiered.
- **SC-002** (FR-004, FR-005, FR-008): after each wave, every finding the wave took re-checks IN-STEP, and the report's finding count falls by
  at least that many with no new finding introduced.
- **SC-003** (FR-003, FR-006): waves are taken in tier order: no E(n+1) row is fixed while an E(n) row the session could fix stands open
  (an E(n) row may wait on a dependency, recorded in the ranking).
- **SC-004** (FR-007): at the GM's usage cap (FR-007), the clone holds no uncommitted work and no unrecorded check verdict.
- **SC-005** (FR-009, FR-010, spec-wide): the end state of the whole program is `make claims-report` with 0 DRIFTED, 0 MISLABELED, 0 UNCLAIMED,
  0 NEEDS-RESEARCH and 0 CANNOT-TELL outside the DEFERRED units; every finding in a deferred unit reads DEFERRED.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

Each wave's amendment adds its map decisions to this table. The program's decisions:

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The implementation moves to the research; the research moves only on the XVI exception path | GM's ruling | *"I'm not sure there's any reason for our implementation to not match for anything"* | FR-004 |
| A Mode A building sheet a finding names is redrawn to the fixed procedure; the frozen hand-rolled settlement maps are never touched | scope, within the GM's 2026-09-28 ruling | the sheet is what contradicts the page; the ruling asks a feature to say which maps it touches, and the settlement maps stay frozen | FR-009 |
| The 727 UNRESEARCHED claims are out of scope | scope | they are not findings: the claim honestly says no research backs it; closing them is research, not fixing a mismatch | Context, Assumptions |
| Sheet-redrawing procedure rows tiered E3, not E1 (wave 2's amendment) | process, FR-003's own definition | the rankers put nine rows that redraw Ubame, Hayakawa, Ochiba or Hoshigaoka in E1; FR-003 tiers a sheet redraw E3 | `audit/overrides.json`, plan D5 |
| The lane law's 32 rows of `ways/` are one wave (wave 4), with the lane rows found since | process, within FR-003's module grouping | one rule set (0081, 0246) across `hamletgen/ways/`; fixed apart, the network would be half under each law | plan D6 |
| Code only the legacy hand-authored settlements run is DEFERRED, not fixed (amendment 8) | scope, the GM's ruling of 2026-10-07 | the legacy settlements' checks go when they convert; the scripted hamlets and the permanently hand-drawn magistracies and country shrines are what the maps keep | FR-010 |
| Waves land inside this feature: only the current wave's rows are task boxes; the next wave is an amendment | process | the GM asked for one feature; the open-task refusal reads only `tasks.md`'s boxes, so a wave lands when its boxes are ticked | FR-006 |
| A row village's street runs on off the map; 0246's pull-back is not its rule | historically accurate as recorded: 0033's drawing page | 0033 is the page for a row village's street ("runs on off the map as the road into it"); 0246's pull-back to the last house served is a clustered settlement's lane rule | plan D7 |
| The village copse stands only among the houses; the against-the-belt form is retired (wave 16) | historically accurate as recorded: 0071's drawing page | 0071's drawing page draws the dooryard copse only in the gaps between the houses and no page shows a copse against the belt; it moved nothing drawn - Mizuguchi, the only map that declared it, is linear and draws no copse | `hamletgen/consts.py` `COPSE_SITINGS`, `hinterland/stages.py` `stage_windbreak` |
| The notice board stands on the busiest frontage; the drawing-water place is retired (wave 16) | historically accurate as recorded: 0190's drawing page | 0190's question page names the village center, entrance, officials' gates and bridge ends, its drawing page the busiest main road, and no page puts a board at a well; it moved nothing drawn - Kashikawa's and Sawada's boards stand where they stood | `hamletgen/consts.py` `KOSATSUBA_SITINGS`, `settlement/structures/fixtures/siting.py` |

## Assumptions

- The report at `a52ff1bcd` is the audit's input; findings that appear later (from other sessions' work) join the ranking
  at the next wave's start.
- "Implementation work" is estimated by reading the finding, the cited research and the code - an estimate, recorded per
  row; a wave that finds a row harder than ranked moves it down and says so.
- The ranking is a judgment (an Opus task); its tier per row is checked by a second reader on a sample before the first
  wave starts.
- UNRESEARCHED claims (727) and the open research list (`make open-questions`) stay outside this feature.

## Review history

- Round 1 (2026-10-07): REVISE - (1) waves as separate features not legitimate: waves become amendments to 328's
  `tasks.md` (FR-006); (2) the cap hook refused the recording the spec required: the hook now allows recording a running
  check (reply under `/tmp`, `make claims-checked` / `claims-triaged` / `record-checked`) and the stop runs no gate
  (FR-007, self-test 55/55); (3) hand-drawn maps: FR-009 names what is and is not touched; (4) E0 bounded to a match
  impl-drift or an unedited page already states (FR-003). Points 2 (UNRESEARCHED out of scope), 4 (tiers) and 5 (the
  stop's intent) passed.
- Round 2 (2026-10-07): REVISE - (1) FR-008 and the Decisions preamble still named a wave's own spec: both now say this
  feature's `spec.md`, added by the wave's amendment (and the plan's XIII line); (2) MEASURED that a subagent's tool call
  reaches the hook with the parent's session_id plus an `agent_id` (a probe agent's Bash call, logged): the hook now lets
  a running subagent's calls through and refuses only its dispatching more agents, and sends it no usage note
  (self-test 59/59); (3) the E0 bound copied into `ranking-brief.md`; the batches ran on the earlier wording, so the
  merge sends every E0 row that is not MISLABELED or UNCLAIMED to a bounded re-check.
- Round 3 (spec-fidelity-verify, 2026-10-07): FAITHFUL - the three round-2 items resolved; `tasks.md` (Phase 1 and
  wave 1) faithful; the aside (the plan's merge step to name the bounded E0 re-check) applied.
- Lint pass (2026-10-07, after acceptance, no change of meaning): `spec-lint` asked each SC to name its FRs and the
  cap figure to be named rather than asserted; the SCs now name their FRs, the cap is written as a named value, and SC-004
  points at FR-007 for it.
- Amendment 1, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - (1) main gate posts redraws three
  sheets: moved to E3, out of wave 2; (2) archery bank draws no sheet: back to E1, into wave 2 (the plan's D5b ruled NOT
  LEGITIMATE); (3) the count is nine, from `audit/overrides.json`; (4) `FOOTPATH_FABRIC_GAP`'s wait recorded in its
  `after`. The aside on XIII applied: the baseline is the clone at main's engine content before the first edit.
- Amendment 1, round 2 (spec-fidelity-verify, 2026-10-07): FAITHFUL; plan CLEAR (seven decisions within). Aside: the
  archery bank is fixed literally at `250 x 8 ft`; any move from it goes to the exception path first.
- Wave 2 measurement (2026-10-07, not a review round): the row pitch at 0038's `92 ft` Z'd a Kuwabata joint the engine
  cannot re-route (`test_no_zigzag_straddles_a_joint`); on the measured cause the row waits for a found E3 row that
  re-routes such a joint (SC-003's dependency), held at 100 meanwhile; `WEB_REACH_FT` stays 0246's `100 ft`, decoupled.
- Amendment 2, round 1 (spec-fidelity-verify, 2026-10-07): CHANGES REQUIRED - (1) the lane law renumbered wave 4 (spec,
  plan D6, tasks); (2) T12a tiers the 13 provisional non-E0 found rows by their work before any E1 wave; Phase 4 names its
  39 rows truly (38 found, wave 1's one unclosed); (3) Edge Cases carries the hold wave 2 made. The holds themselves were
  ruled faithful (no row dropped, no research moved).
- Amendment 2, round 2 (spec-fidelity-verify, 2026-10-07): FAITHFUL; plan CLEAR (seven decisions within).
- Amendment 3, round 1 (spec-fidelity-verify, 2026-10-07): CHANGES REQUIRED - (1) four E1 rows outside the lane code that
  rank ahead of it (T12a's cell, building size anchors, band on the canvas; the wave-3 basin row) join wave 4 ahead of the
  lane rows; (2) the counts: 33 held since amendment 1 and 4 found since; the Decisions row worded as such.
- Amendment 3, round 2 (spec-fidelity-verify, 2026-10-07): CHANGES REQUIRED - T15 and the Phase 5 heading name the four
  E1 rows ahead of the lane law, so no box can be ticked with them undone.
- Amendment 3, round 3 (spec-fidelity-verify, 2026-10-07): FAITHFUL.
- Amendment 4, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - (1) wave 5 must be the contiguous
  run of the ranking, not the homestead modules; (2) the row street settled now (0033 governs it, not 0246); (3) closed
  rows keep the tier they closed at (`audit/closed-tiers.json`).
- Amendment 4, round 2 (spec-fidelity, 2026-10-07): FAITHFUL; plan CLEAR (13 decisions within). Notes taken: the mill
  row re-tiered E3 when its fix proved a new element; `merge.py` records a newly closed row's tier itself.
- Amendment 5, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - DEVIATION offered as an ordinary
  claim label; it is written only after the exception path rules it LEGITIMATE, and the spur clip margin cites 0081
  against the code.
- Amendment 5, round 2 (spec-fidelity-verify, 2026-10-07): FAITHFUL.
- Amendment 6, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - four rows offered DEVIATION as a
  choice (now fixed toward their pages, DEVIATION only through the exception path); the occasions' reason (the water gate
  and boundary stones are drawn only on exempt legacy cities). Aside taken: row 93's value change split into an E1 row.
- Amendment 6, round 2 (spec-fidelity-verify, 2026-10-07): CHANGES REQUIRED - the follow-up record's wave-6 bullets
  carried the old wording; the plan verdict re-recorded for the run's new bounds (rows 180-231).
- Amendment 6, round 3 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - the run chosen on tiers set by
  verdict alone; T25a added (a fresh reader tiers the provisional rows by their work before the wave chooses its rows).
- Amendment 6, round 4 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR (22 decisions) - the follow-up record
  out of step with T25a's tiers.
- Amendment 6, round 5 (spec-fidelity-verify, 2026-10-07): FAITHFUL.
- Amendment 6 landed (wave 7, 2026-10-07): band 0; the lane clearance held with its reason.
- Amendment 7, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - four E0 claims stating a drift named no
  row that fixes it (D8); T29a's count. Round 2 (spec-fidelity, 2026-10-07): FAITHFUL; plan CLEAR (26 decisions).
- Amendment 8, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - the scope judged by module and name
  matches, not by what runs; the deferred list only today's findings; the plan's cap. Round 2 (spec-fidelity): CHANGES
  REQUIRED, plan BLOCKED - the records included the legacy roller's gate tests and stale rolls. Round 3 (spec-fidelity):
  CHANGES REQUIRED, plan BLOCKED - knobs, constructed classes and module-level claims missed. Round 4 (spec-fidelity):
  CHANGES REQUIRED, plan CLEAR (34 decisions) - FR-010's wording of a knob in use; the measure counts resolutions only.
- Amendment 8, round 5 (spec-fidelity, 2026-10-07): FAITHFUL; plan CLEAR (34 decisions).
- Amendment 9, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - 14 found rows tiered by verdict alone;
  three NEEDS-RESEARCH rows relabeled instead of E4; the annex row's named exception; wave 10 on the unpushed wave 9 and a gate
  "with one failure aside"; the GM's goal amendment not on record. Round 2 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan
  BLOCKED - round 1's items resolved; the exception split: wave 10 on wave 9 while it waits only for the GM's band-3 sign-off
  LEGITIMATE on conditions, the hold's cost on three scaling rolls NOT the GM's (bisect it by row) - done: the wood shed's
  step held.
- Amendment 9, round 3 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - the ranking not re-merged; shed_off_a_wall
  after the held shed step. Round 4 (spec-fidelity): FAITHFUL, plan CLEAR. Exception check (spec-fidelity, 2026-10-07): the
  four DEVIATION relabels NOT LEGITIMATE (floor and ceiling dropped; the bank's forms and the free-standing storehouse E3).
  Round 5 (spec-fidelity): wave 10 FAITHFUL, plan CLEAR, record CHANGES REQUIRED (Sawada's knot not main's; the berm not a
  cause; the knot row's fix text). Round 6 (spec-fidelity): FAITHFUL, plan CLEAR.
- Amendment 10, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - the fallback brook's width labeled 0068
  (option b taken: 0059, with 0068's conflict named). Round 2: FAITHFUL. Round 3: FAITHFUL, plan CLEAR (the push caution).
  Exception check for wave 11 on the unpushed waves 9 and 10: LEGITIMATE on six conditions (plan, Wave 10).
- Amendment 11, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR - the polder lattice claim false for every
  drawn map (corrected). Round 2: FAITHFUL.
- Amendment 12, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan BLOCKED - the seeded rolls never made (made: the
  second kami's two rolls land off the drawn form, so that row is E3). Round 2: CHANGES REQUIRED, plan CLEAR - one notes line
  left. Round 3: FAITHFUL.
- Amendment 13, round 1 (spec-fidelity-verify, 2026-10-07): FAITHFUL (the plan verdict left to spec-fidelity). Round 2
  (spec-fidelity): FAITHFUL, plan CLEAR - the two claims impl-drift's re-check moved (the tax-free fields on 0221's drawing
  page, the postern a GUESS saying what was searched); its aside fixed: the scope keeps the page path.
- Amendment 14, round 1 (spec-fidelity, 2026-10-07): FAITHFUL, plan CLEAR (8 decisions) - removing the seat's drain rule the
  literal reading of 0058 (keeping it at a dispersed seat would be "X except Y"); the stage and sumo defaults within the spec.
- Amendment 15, round 1 (spec-fidelity, 2026-10-07): CHANGES REQUIRED, plan CLEAR (8 decisions) - the retirements literal
  (neither form on any page), the 412/413 dependency LEGITIMATE; the Decisions Recorded rows owed (added). Measured since: the
  retirements moved nothing drawn, so the three placement occasions became `none`.
- Amendment 15, round 2 (spec-fidelity, 2026-10-07): FAITHFUL, plan CLEAR (8 decisions) - the Decisions Recorded rows; the occasions' none confirmed by its own measurement (each manifest differs from the base in meta only).
