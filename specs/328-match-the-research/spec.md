# Feature Specification: The implementation brought to the research, easiest first

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=328-match-the-research`)

**Created**: 2026-10-07

**Status**: Draft

**Input**: the GM's request, verbatim in `request.md`: rank every finding `make claims-report` shows by how much
implementation work it takes to make the implementation match the research it cites, then fix them from easiest to
hardest, until the weekly usage reaches 75%.

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

When the weekly usage reaches 75%, no new work starts; the subagent checks already running finish and are recorded, the
work is committed and the stop-work step run, and the session waits for the GM.

**Independent Test**: the armed cap (`~/.claude/hooks/usage_cap.py`) refuses a new agent, edit or build at 75%; the
session's last actions are recording the running checks, a commit, and `scripts/sync-with-main.sh done`.

**Acceptance Scenarios**:

1. **Given** usage reaches 75% mid-wave, **When** checks are running, **Then** they complete and their verdicts are
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
- **A fix that changes many maps**: regenerate the pool; a map whose new layout fails the gate is fixed in the same wave.
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
- **FR-007 (the usage cap)**: the work runs until every finding is fixed or the account's weekly usage reaches 75%. At
  the cap no new work starts (no agent, no edit in the repository, no build or gate run); the subagent checks already
  running complete and their verdicts are recorded (the reply saved under `/tmp`, then `make claims-checked` /
  `claims-triaged` / `record-checked`); the clone is committed and `scripts/sync-with-main.sh done` run, which at a
  mid-wave stop refuses the landing WITHOUT running the gate and pushes the clone's backup branch; the session waits
  for the GM's word to continue. The cap is enforced by the armed per-goal hook (`~/.claude/hooks/usage_cap.py`, whose
  self-test `test-usage-cap.sh` holds exactly that allow/deny set), not by memory.
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

- **SC-001**: the ranking holds exactly the 565 findings of the audit's report, each once, each tiered.
- **SC-002**: after each wave, every finding the wave took re-checks IN-STEP, and the report's finding count falls by
  at least that many with no new finding introduced.
- **SC-003**: waves are taken in tier order: no E(n+1) row is fixed while an E(n) row the session could fix stands open
  (an E(n) row may wait on a dependency, recorded in the ranking).
- **SC-004**: at the 75% cap, the clone holds no uncommitted work and no unrecorded check verdict.
- **SC-005**: the end state of the whole program is `make claims-report` with 0 DRIFTED, 0 MISLABELED, 0 UNCLAIMED,
  0 NEEDS-RESEARCH and 0 CANNOT-TELL.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

Each wave's amendment adds its map decisions to this table. The program's decisions:

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The implementation moves to the research; the research moves only on the XVI exception path | GM's ruling | *"I'm not sure there's any reason for our implementation to not match for anything"* | FR-004 |
| A Mode A building sheet a finding names is redrawn to the fixed procedure; the frozen hand-rolled settlement maps are never touched | scope, within the GM's 2026-09-28 ruling | the sheet is what contradicts the page; the ruling asks a feature to say which maps it touches, and the settlement maps stay frozen | FR-009 |
| The 727 UNRESEARCHED claims are out of scope | scope | they are not findings: the claim honestly says no research backs it; closing them is research, not fixing a mismatch | Context, Assumptions |
| Waves land inside this feature: only the current wave's rows are task boxes; the next wave is an amendment | process | the GM asked for one feature; the open-task refusal reads only `tasks.md`'s boxes, so a wave lands when its boxes are ticked | FR-006 |

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
