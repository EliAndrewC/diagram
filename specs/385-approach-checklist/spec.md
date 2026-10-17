# Feature Specification: The approach checklist - the front of 384, worked one task at a time

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=385-approach-checklist`)

**Created**: 2026-10-17

**Status**: Filed - checklist v1 drafted (`checklist.md`) and refined by the audit (`audit.md`, 12 pitfalls); no task started

**Approved**: the GM, 2026-10-17, "the shape that you have proposed looks right. So please file it, draft checklist version 1, and start the cheap audit."

**Affects**: tooling, review process, hamlet, research record

**Input**: `request.md` - the GM, 2026-10-17, verbatim.

## Why

Feature 384 holds 325 ranking rows and five carried tasks. Its FR-003 says no wave is taken until the GM has decided how the
work should go faster; this feature is that decision. The GM's diagnosis (`request.md`): sessions hyper-focus on making an
algorithm conform to a rule or a number without stepping back to ask where the rule came from and what it is for. His two
examples:

- **The 700 ft reach.** A session spent hours seating every farmhouse of a nucleated settlement within 700 ft of the paddies;
  asked why 700, it found no reason - the number was recorded once as an implementation detail.
- **The lane angles.** The lane law refuses two lanes meeting at a sharp angle. Lanes met that way because an obstruction
  forced it, and the session never asked whether the rule should hold there. It proposed moving homestead features so the
  paths would meet more tidily - against why lanes are laid after homesteads at all (people walk round their houses; nobody
  moves a house for a path), and a packing search besides. Two principled answers existed: an exception (an obstruction may
  force a sharp meeting) and a new rule that dissolves the case (two lanes side by side become one path).

The rule that would have caught both already exists (CLAUDE.md, "Room before packing": a number set only to implement against
is a knob to move, never a target to defend). It is asked by the round arbiter - after a cap or a tripwire, after the hours.
The gap is WHEN the question is asked, and that it is asked of no one in particular. A judgment like this cannot be enforced
mechanically, but the moment it is asked can be, and so can the requirement that it is answered in writing.

Feature 374's report (`make feature-report F=374`) shows the cost is invisible today: "thinking" was 25 h 30 min (51%) and
Bash 8 h 12 min, with no way to tell time spent choosing an approach, and changing it, from time spent carrying one out.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A task opens with its approach questioned (Priority: P1)

The GM finds every task of this feature's plan opening with an **Approach** block that answers the checklist
(`checklist.md`) for the rules and numbers the task will work against: where each comes from (research, a GM ruling, or our
own implementation), whether it describes how the thing really came about, and which exits were weighed besides conforming
(refine the number, a principled exception, a rule that dissolves the case, more room). `make decide` hands that block to the
reviewer with the rest of the section.

**Independent Test**: `make tick` refuses a task of this feature whose plan section has no Approach block, or one with a
checklist question unanswered; the refusal names the questions missing.

### User Story 2 - The checklist comes back when the work resists (Priority: P1)

When the work resists - a seed or a cohort the change refuses, a second red gate, the hourly step-back - the session answers
the checklist again for what is resisting, before its next attempt, and the answer is recorded beside the task.

**Independent Test**: on each trigger the session is told to answer the checklist (the trigger's own message carries it); the
next `make tick` refuses until an answer dated after the trigger is recorded.

### User Story 3 - Each task is measured, and the process improved, before the next (Priority: P1)

After each task the GM finds a retro row: the task's time split at its decision points (before the approach settled, after
it, and how many times it changed), the checklist items that fired, any that should have, and the change made to the
checklist or the tooling because of it. The next task starts only after the row is written.

**Independent Test**: `make feature-report F=385` prints a per-task table with the split; `retro.md` has one row per closed
task; `checklist.md`'s history shows the changes the rows name.

### User Story 4 - The front of 384, done (Priority: P2)

The tasks moved from 384 are done under 384's rules: the lane law first (384's FR-000 and User Story 0, moved here whole), the
four cohort seeds failing at HEAD, T48 (the web carries a re-deal of the seats), T47's patch re-landed, then about five of the
ranking's rows chosen to be of different kinds, so the checklist is tried on more than lanes.

**Independent Test**: as 384 states for each (its User Stories 0 and 2, SC-004); each ranking row is marked with its wave in
328's `audit/waves.json`.

### Edge Cases

- **The checklist as a license.** An answer of "ours, not research" makes a rule movable, not disposable: a rule loosened,
  excepted or retired carries its reason at the point of change and in the research record's drawing page, and a research-
  backed rule is changed only by new research or the GM.
- **A task the checklist does not fit** (a pure tooling task with no rule worked against): its Approach block says so in one
  line; the retro row records whether that was right.
- **A checklist that grows without end.** A retro may also remove or merge items; an item that has fired on no task by the
  feature's end is cut or justified.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (checklist v1)**: `checklist.md` in this feature's directory: the questions, each with the incident it comes from.
  v1 is drafted from the project's own doctrine (CLAUDE.md, the constitution, the written lessons) and refined by the audit
  (FR-002) before the first task starts. Once this feature closes, the settled checklist moves to `docs/` and is loaded by
  every feature's task start.
- **FR-002 (the cheap audit)**: the evidence for the checklist is gathered without re-reading transcripts: the GM's own typed
  messages over the last 14 days (216 messages, about 26,000 words, against 2.5 GB of transcripts), the round arbiter's
  rulings other than routine round-cap accepts, the `make feature-report` output of features 374, 375 and 383, 374's GM-review
  rows, and the written lessons. Read by one Sonnet extractor (reading is Sonnet's tier); the result, `audit.md`, lists each
  pitfall with its evidence, its cost and the question that would have caught it.
- **FR-003 (asked at task start)**: each task's plan section carries an Approach block answering the checklist; `make tick`
  refuses this feature's tasks without it (tooling built under this feature, with its test).
- **FR-004 (asked when the work resists)**: the triggers of User Story 2 name the checklist in their messages and require a
  fresh answer before the next tick. The existing ones (the red-gate tripwire, the hourly step-back) are extended; a refused
  seed or cohort is added as a trigger.
- **FR-005 (the split, measured)**: `make feature-report` gains a per-task table: time from `make task-start` to the task's
  approach settling (its `make decide` verdict), time after, and the count of re-decides and checklist re-answers.
- **FR-006 (one task, then the retro)**: tasks run one at a time; each closes with its retro row in `retro.md` and any change it
  names made, before the next `make task-start`.
- **FR-007 (the moved work)**: 384's FR-000 and User Story 0 (the lane law), its four cohort seeds failing at HEAD, T48 and T47
  move here; 384 is amended to say so. The ranking rows taken here are chosen at the start of their task and recorded in 328's
  `audit/waves.json` with their wave. 384's FR-002 (374's rules as amended by 375 and 383) and FR-004 (the usage cap it sets)
  apply to them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-005, FR-006): every closed task has its retro row and its per-task split; the share of each task's time spent
  before its approach settled, and its count of re-decides, are compared across the tasks in the final report.
- **SC-002** (FR-001): the last two retro rows change nothing in the checklist (it has settled), or the report says why not.
- **SC-003** (FR-007): the lane law's success criteria as 384 states them (User Story 0's Independent Test), and 384's SC-004 for
  T48.
- **SC-004** (FR-003, FR-004): the refusals of FR-003 and FR-004 each have a test that is red without them.

## Decisions Recorded

- **D1 (a new feature, not 384 extended)**: CLAUDE.md prefers extending the feature the work came from. The GM asked for the
  split (`request.md`), and the cadence here - one task, a measurement, a process change - does not fit 384's waves and batches.
  Class: deliberate deviation, the GM's.
- **D2 (the checklist stays here until it settles)**: v1 lives in this feature's directory, not `docs/`, while the retros
  change it; it moves once SC-002 holds. Class: guess (a convenience), movable.
