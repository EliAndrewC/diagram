# Feature Specification: The approach checklist - the front of 384, worked one task at a time

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=385-approach-checklist`)

**Created**: 2026-10-17

**Status**: In progress - T01-T06 and T13-T30 landed by 2026-10-18 (their retros in `retro.md`); amendments 1-6 FAITHFUL or landed, amendment 7 (T31-T40, ten more ranking rows) filed 2026-10-18; Spec FAITHFUL (round 2); checklist v1 drafted (`checklist.md`) and refined by the audit (`audit.md`, 13 pitfalls) and by the tasks' retros

**Approved**: the GM, 2026-10-17, "the shape that you have proposed looks right. So please file it, draft checklist version 1, and start the cheap audit."

**Amendment 1 approved**: the GM, 2026-10-17, "Yes, please append the spec to include those four items."

**Amendment 2 approved**: the GM, 2026-10-17, "yes please make the blind approach T03's first step."

**Amendment 3 approved**: the GM, 2026-10-17, "Yes, please lock in option three. Thanks." (option 3 of the claims-gate question the round arbiter raised at T03's landing, `ask:t03-claims-at-landing`)

**Amendment 4 approved**: the GM, 2026-10-18, "Yesa please implement the proposals you made for what to do before task 4, as amendment 4."

**Amendment 5 approved**: the GM, 2026-10-18, "Either way, I do want you to file amendment 5 for the 3 tooling fixes"

**Amendment 6 approved**: the GM, 2026-10-18, "Please make sure to implement any obvious performance / tooling / process improvements along the way." (the overnight run through the rest of the feature; each improvement its own task, one goal a task)

**Amendment 7 approved**: the GM, 2026-10-18, "I would like to amend the feature to pull in 10 more claims." (ten more of 328's ranking rows, worked one task at a time as T06-T10 are)

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
Bash 8 h 12 min, with no way to tell time spent choosing an approach, and changing it, from time spent carrying one out (observed 2026-10-17, method: `specs/374-match-the-research-continued/report.md`, "Where the time went", written by `make feature-report F=374 WRITE=1`).

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

When the work resists - a seed or a cohort the change refuses, a second red gate, the hourly step-back, a change of approach (the task's plan section re-decided) - the session answers
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
  (FR-002) before the first task starts. Once this feature closes, the settled checklist moves to `docs/`, and the refusals of
  FR-003 and FR-004 extend from this feature's tasks to every feature's, 384's first among them.
- **FR-002 (the cheap audit)**: the evidence for the checklist is gathered without re-reading transcripts: the GM's own typed
  messages over the last 14 days (216 messages, about 26,000 words, against 2.5 GB of transcripts - observed 2026-10-17, method: `du -ch` over the `.jsonl` transcripts under `~/.claude/projects/-diagram` modified in the last 14 days, and `jq` over the 23 top-level ones for user messages that are typed text, not meta, compaction summaries or tool notices, counted by `wc -l -w`), every
  ruling of the round arbiter (`specs/*/arbiter.jsonl`, the round-cap accepts included), the `make feature-report` output of
  features 374, 375 and 383, 374's GM-review rows, and the written lessons. Read by Sonnet extractors (reading is Sonnet's
  tier); the result, `audit.md`, lists each pitfall with its evidence, its cost and the question that would have caught it, and
  says in a line where a source added none.
- **FR-003 (asked at task start)**: each task's plan section carries an Approach block answering the checklist; a plan section
  re-decided (a changed approach) carries the block answered afresh. `make tick` refuses this feature's tasks without it (tooling
  built under this feature, with its test).
- **FR-004 (asked when the work resists)**: the triggers of User Story 2 name the checklist in their messages and require a
  fresh answer before the next tick. The existing ones (the red-gate tripwire, the hourly step-back) are extended; a refused
  seed or cohort, and a re-decide of the task's plan section, are added as triggers.
- **FR-005 (the split, measured)**: `make feature-report` gains a per-task table. Every `make decide` verdict and every checklist
  re-answer is a decision point; the table gives each task's total time, the time up to its last decision point and the time
  after it, each segment between decision points, and the counts of re-decides and checklist re-answers.
- **FR-006 (one task, then the retro)**: tasks run one at a time; each closes with its retro row in `retro.md` and any change it
  names made, before the next `make task-start`.
- **FR-007 (the moved work)**: 384's FR-000 and User Story 0 (the lane law), its four cohort seeds failing at HEAD, T48 and T47
  move here; 384 is amended to say so. The ranking rows taken here are chosen at the start of their task and recorded in 328's
  `audit/waves.json` with their wave. 384's FR-002 (374's rules as amended by 375 and 383) and FR-004 (the usage cap it sets)
  apply to them.

### Amendment 1 - T02 takes the check costs T01 measured (the GM, 2026-10-17)

T01 took about 3 h 22 min (`retro.md`), about 50 min of it - the session's estimate, as given to the GM - the checks two bullets on one
research page owed. T02 adds four
items to FR-003 to FR-005, each measured on T01's own record (observed 2026-10-17, method: `retro.md`'s T01 row, timed by hand from its
decision points, and the record checks' own counts in `dev/review-ledger.md`):

- **FR-008 (a re-check reads against what the last check read)**: a pop-up or claim re-owed by a page change is triaged against
  the page version its last check READ, not an older baseline - T01's one-word vocabulary fix re-owed ten pop-ups and 229 claims
  (`make claims-owed` after the fix: "229 claim(s) owe only a TRIAGE of the blocks that changed on their pages")
  already checked against the page with that word in it.
- **FR-009 (one check where several are spent today)**: a page-wide record unit (quote-check's `#unfootnoted`) is answered by one
  batch, and the pop-ups a changed page re-owes for one check kind are judged by one agent, not one agent each.
- **FR-010 (a guard, not a reminder)**: a write to the working tree while the session's own gate runs is refused, naming the
  verdict wait (`make verify-wait`) - checklist C6 made a guard; T01 voided two gates this way.
- **FR-011 (the cost measured)**: T02 records what each check cost per changed line (dispatches, tokens, wall time), so the next
  task shows whether FR-008 to FR-010 paid.

### Amendment 2 - T03 opens with a blind Approach (the GM, 2026-10-17)

- **FR-012 (the blind Approach)**: T03's first step, before the session writes anything of T03's own, is its Approach block
  (checklist part A) written by a FRESH agent that has not seen this session's conversation: it is given T03's task text, the
  checklist, and the code and the record to read, and nothing of what the session concluded about T03's rules - nor the GM's
  own questions on them. Inside this feature's directory it reads only `checklist.md` and T01's record (`lane-law-table.md`,
  `retro.md`) - checking the rules T01 kept against the research is the very question the checklist exists to ask - and T03's
  task text is copied into its prompt; every other file there (`request.md`, `spec.md`, `plan.md`, `tasks.md`, `arbiter.jsonl`,
  `gm-review.jsonl`, `audit.md`) is closed to it, and its prompt names no question the GM or the session raised. The session's
  own conclusions were sealed before amendment 2, outside the repository, where that agent cannot read them; once the blind
  block is written they are compared, rule by rule, in T03's retro row: which questions the checklist raised without hindsight,
  which it missed, and the checklist change a miss calls for. The session then writes T03's plan section from the blind block
  and its own, saying where they differ.

### Amendment 3 - a finding on unchanged code is carried, not refused (the GM, 2026-10-17)

At T03's landing the claims gate refused three findings that a one-paragraph edit to page 0246 surfaced on code T03 did not
change (`settle.py::theirs`, the doubled tail's angle, `clearance.py::_clear_link`): the gate counts a finding as INTRODUCED when
its code changed OR the research it cites changed (`scripts/record/claims.py`, `classify`), so a page edit makes every finding on
unchanged code that cites the page block the landing. The round arbiter let T03 land under `CLAIMS_OK`, carried the three to
T12 by hand, and put the rule to the GM, who chose option 3 of three (keep it strict; block only on findings about the edited
block; never block on unchanged code, the finding filed as an open task):

- **FR-013 (carried, not refused)**: a finding that did not stand at the merge base, on a unit whose code and claim are unchanged
  since it - surfaced because a page it cites changed, or because the claim was judged again - is CARRIED: it does not refuse the push once it is filed as an open task of the feature
  being landed (the active task's feature), so that feature cannot close until the finding is fixed or re-checked clean. A carried finding not yet filed refuses, naming
  the one command that files it (`make claims-carry F=<feature>`), which writes the task box and its record; the open-task
  refusal honors that box. A finding on changed code or a changed claim is still introduced and still refuses, as before; a
  finding that stood at the base still only warns.
- **FR-013, amended 2026-10-26 (the GM: *"Yes, a finding carried by a landing that changes no engine code should go to 405
  instead. Please make that the standing rule and move 422's 5 [findings] into 405 now so that 422 can close."*)**: when the
  landing's delta holds no engine path (`l7r/**/*.py`, `pool/*.gen.py`, `pool/*.json`), the carried finding is filed as an
  open task of feature 405, the claims feature, instead of the feature being landed (`claims_carry.target`, `CLAIMS_FEATURE`).
  A research-record or tooling landing cannot fix engine code; feature 422 had been held open on five such findings.

### Amendment 4 - T03 measured again, before T04 (the GM, 2026-10-18)

The GM asked for T03's 2 h 25 min broken down before T04. Read from the event log by hand (2026-10-18, `retro.md`'s T03 rows):
about 50 min went to the four seeds (37 min diagnosing and fixing, 14 min on seed 57, which the fixes worsened), 21 min to the
side-by-side merge, a second goal that failed and was carried, 24 min to the front (11.5 min of it the one-time blind Approach),
and 50 min to checks and landing. The report's own table could not show this: it put 64% under "thinking", because a
subagent's tool calls are logged under the session's id with no marker - 202 of the 549 calls in T03's window were
subagents' (matched against the subagent transcripts' tool ids, 2026-10-18). And T03's decision log was first written from
memory, up to an hour off.

- **FR-014 (whose time)**: `make feature-report` tells the session's own tool calls from its subagents' - exactly where the
  transcripts show it, the window an estimate only where they do not - and splits each task's time into the session working,
  the session waiting (on a subagent, a background run, the GM) and the subagents' own work; and prints, per task, a table of
  its phases between decision points: each phase's span, what ended it, the session's calls and working time, the time spent
  waiting, and the subagents that ran in it.
- **FR-015 (one goal a task)**: the checklist's "done" names ONE goal; a second goal found in a task becomes its own task before
  work on it starts.
- **FR-016 (the decision log, printed)**: `make feature-report` prints each task's decision-log skeleton from the event log and
  the plan - its start, every agent returned (type, verdict, duration), every cohort and gate run, every part B or re-answered
  Approach stamp, its tick - in time order, so a retro's decision log is filled in from it, not reconstructed.

### Amendment 5 - three landing frictions T04 measured (the GM, 2026-10-18)

T04's last 6 min (02:51-02:57, its phase table) were four refusals in a row, each mechanical:

- **FR-017 (the make-targets page, checked on every route)**: a push checks that `docs/make-targets.html` is current
  (`make-docs.py --check`), as the gate's `test_make_docs` does - T13 landed a target by the direct route, which runs no gate, and
  the stale page failed T16's `make land-tooling` a task later.
- **FR-018 (an arbiter's fix landed, settled and its task ticked in one command)**: `make arbiter-fix-done` takes the fix's files
  (`LAND=`) and the task it holds (`F=` `TICK=`): it lands them with its test by `make land-tooling`, settles the fix, then ticks
  the task; the refusals that name the three-step order name this instead (spec-fidelity, amendment 5 round 1: "One command could
  do all three").
- **FR-019 (a ledger row written from the record)**: the push's and the hook's ledger refusal names the command that writes each
  owed row from the agent's own reply (`make ledger-owed WRITE="<where the session recorded what it did>"`, the form page sessions
  already use), not "add the row printed, its ?s filled" by hand.

The GM also asked whether the session was batching. Measured (2026-10-18, the session transcript, each assistant turn's tool
calls): 346 of T03's 354 tool turns made one call, but only 18 of those were a bare lookup the batching hook blocks; 143 were
folded lookups, 127 scripts, 43 make steps, the rest agents and edits - dependent steps, not batchable lookups. No batching
change is made: the lever is fewer rework round trips, two of which FR-017 and FR-018 remove.

### Amendment 7 - ten more ranking rows (the GM, 2026-10-18)

- **FR-020 (ten more claims)**: ten more of 328's ranking's open rows (`ranking.json`, `audit/waves.json`) are taken, as T31 to
  T40, each chosen at its task's start - a row of a kind not yet tried where one is left, the checklist answered for it, and
  marked with its wave - and worked one task at a time under FR-006 (its retro row) and 384's FR-002, as T06-T10 are. They run
  after T07-T10 and before T12 and T11, the close, which stays last.
  *Read so by the round arbiter's ruling on ask:t33-ranking-pick (2026-10-19):* the rows are taken from open rows whose code a
  scripted (live) map runs - a kind not yet tried where one is left, else the top-ranked live row of any kind, said so in the task's
  Approach; a row whose code was removed with no live successor is marked retired in 328's `audit/waves.json` with its reason
  (133 so marked, wave 165, each checked for a successor first); `settlement/` rows that serve only frozen exhibit maps stay open
  and are skipped.
  *Moved by amendment 11 (the GM, 2026-10-19):* the rows not yet worked (T35-T40, and T144 in place of T32's dead row) moved to
  feature 405 with the rest of 385's non-process tasks; T31-T34 stand as 385's.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-005, FR-006): every closed task has its retro row and its per-task split, and across the tasks each task's total
  time, its share before its last decision point and its count of re-decides fall, or the final report says why not (tasks of
  different kinds are compared within their kind where the report can).
- **SC-002** (FR-001, FR-002): the checklist v1 drafted from the audit, and the last two retro rows change nothing in it (it has
  settled), or the report says why not.
- **SC-003** (FR-007): the lane law's success criteria as 384 states them (User Story 0's Independent Test), and 384's SC-004 for
  T48.
- **SC-004** (FR-003, FR-004): the refusals of FR-003 and FR-004 each have a test that is red without them.
- **SC-005** (FR-008, FR-009, FR-010, FR-011): on the next task, the checks owed per changed line - dispatches, tokens and wall time - are below
  T01's, measured by FR-011's record; or the report says why not.
- **SC-007** (FR-013): replayed on T03's landing, the three findings are carried, not refused, and the push goes ahead without
  `CLAIMS_OK` once `make claims-carry` has filed them; a finding on changed code still refuses (each a test red without it).
- **SC-008** (FR-014, FR-015, FR-016): replayed on T03, the report attributes its 202 subagent calls to the subagents and shows the
  phase table and decision-log skeleton the hand count above found; T04's retro row is written from them and compared with
  T03 phase by phase.
- **SC-009** (FR-017, FR-018, FR-019): each refusal names its one command, and each has a test red without it.
- **SC-010** (FR-020): ten more ranking rows marked with their waves in 328's `audit/waves.json`, each task with its retro row.
- **SC-006** (FR-012): T03's retro row compares the blind Approach with the sealed conclusions rule by rule, and names the checklist
  change each miss calls for, or that there was none.

## Decisions Recorded

- **D1 (a new feature, not 384 extended)**: CLAUDE.md prefers extending the feature the work came from. The GM asked for the
  split (`request.md`), and the cadence here - one task, a measurement, a process change - does not fit 384's waves and batches.
  Class: deliberate deviation, the GM's.
- **D2 (the checklist stays here until it settles)**: v1 lives in this feature's directory, not `docs/`, while the retros
  change it; it moves once SC-002 holds. Class: guess (a convenience), movable.
