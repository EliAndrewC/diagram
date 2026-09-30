# Feature Specification: The effort-level experiment (a pilot)

**Feature Branch**: none (the project works on `main`; `SPECIFY_FEATURE=293-effort-level-experiment`)

**Created**: 2026-09-29

**Status**: Accepted (spec-fidelity FAITHFUL, round 2, 2026-09-29)

**Input**: the GM's request, `request.md` (the handoff `~/.claude/handoffs/effort-experiment.md`, copied verbatim, and
the GM's answers of 2026-09-29 that settled the tasks, the arms and the replication).

## Summary

Which effort level should this project's sessions default to? Opus 5.5 defaults to `medium`; Anthropic's advice for the
model is to "run an effort sweep on your own evals rather than carrying settings over from an earlier model." This
feature is that sweep in its smallest useful form: a **pilot**, one run per arm per task, **`medium` against `xhigh`**
(the GM: "medium vs xhigh to start with, and we can test more if there is a big difference between medium and xhigh"),
on two real, wanted tasks:

- **Research (R)**: the Ubame servants' quarters - was a servants' nagaya one dormitory behind sliding partitions, or did
  each household have a door of its own? (`future-work/compounds.md`, "Ubame: the servants' quarters have one door for four
  bays").
- **Implementation (I)**: the storehouse annex goes to the larger houses first (`future-work/farming-communities.md`, "Found by
  feature 280's settlement-reviews": the annex is rolled per house by position, not by size, against homesteads/720), scripted
  hamlets only - the GM ruled out every settlement type not yet scripted. (The GM's first pick, a footpath to the hamlet's own
  burial ground, was found impossible by its first run: feature 280 M68 had removed the hamlet's own ground the day after the
  future-work entry was written. The GM replaced it, 2026-09-30.)

Each run is a separate top-level headless session at its arm's effort, in its own clone, from one starting commit, given
a byte-identical prompt. The runs are measured (tokens including subagents, wall-clock, tool calls, rework), their
outputs are graded blind against rubrics written before each task's first run, and a short report gives a recommendation per task
type under a decision rule fixed in this spec. The better output of each task lands; the other is discarded.

The working hypotheses the experiment tests (from the handoff, reasoning not measurement): (1) the project's checks catch
mistakes after the fact and effort prevents them, so lower effort may show up as more rework rather than worse final
output, and higher effort may cost LESS in total; (2) effort matters most where checks are weakest - research - and least
in implementation that tests and guards cover; (3) so the answer may differ by task type.

## User Scenarios & Testing

### User Story 1 - The GM learns which effort level to default to, per task type (Priority: P1)

The GM reads one short report and can set the project's default effort (or a per-task-type habit) on evidence rather than
on the model's shipped default.

**Why this priority**: it is the point of the feature.

**Independent Test**: the report exists in the repository with the per-task table, the qualitative differences, and a
recommendation for research and for implementation that follows from the decision rule as written here, applied to the
measured numbers.

**Acceptance Scenarios**:

1. **Given** the four runs are complete and graded, **When** the GM opens the report, **Then** they see, per task, a row per
   arm with total tokens (input, output, cache-read, cache-creation, with subagents included and also shown apart), wall-clock,
   tool calls, the rework counts, and the blind quality score, plus how the two outputs differ in words.
2. **Given** the numbers, **When** the decision rule is applied, **Then** the report states the outcome per task type
   (adopt `xhigh`, keep `medium`, or inconclusive) and whether the rule calls for expanding the experiment, and the reader can
   check the arithmetic from the table.
3. **Given** the report is a pilot at n=1 per cell, **When** it is read, **Then** it says so in its first lines and treats every
   difference as directional.

---

### User Story 2 - Each arm is a fair test of a session's default effort (Priority: P1)

The only thing that differs between two runs of the same task is the main session's effort level.

**Why this priority**: an unfair comparison answers nothing; its cost is the whole experiment.

**Independent Test**: the run log shows, for the two runs of a task, the same starting commit, the same prompt (a hash), the same
model, the same hooks and agent files, and different `--effort` values; and the checker subagents in both ran at the same pinned
tiers.

**Acceptance Scenarios**:

1. **Given** a task, **When** its two runs start, **Then** each starts from the same recorded commit in a fresh clone of its own,
   with a prompt whose hash is identical, and with the effort level set for the whole session at launch.
2. **Given** the defined review and check agents pin their own model and effort, **When** a run dispatches one, **Then** it runs at its
   pinned tier in both arms, and the report names the tiers that ran.
3. **Given** an ad-hoc agent (one with no agent file) that checks or judges, **When** a run dispatches one, **Then** it runs at one
   fixed effort in both arms. Counting per arm instead is allowed only for ad-hoc reading, fetching, translating or extracting. If the
   implementing session MEASURES that an ad-hoc dispatch's effort cannot be set, it records that, and the report lists the control as unmet
   for those dispatches with their count per arm.
4. **Given** a run starts headless sessions of its own (a research page's write and check-and-apply sessions run as fresh headless
   sessions), **When** it does, **Then** every one of them runs at the run's arm effort, and the run log records each session's effort.
5. **Given** the container memory cap (the GM, 2026-09-29: run the tests "sequentially rather than in parallel for memory reasons ...
   I don't want too many things running to be a problem for the container"), **When** the experiment executes, **Then** it is strictly
   SEQUENTIAL end to end: one run at a time, never two at once; a run starts only when the container's memory is under a stated
   headroom threshold, and waits (logged, not counted in its wall-clock) otherwise; while a run is live the implementing session starts
   nothing else memory-heavy of its own - no gate, no test run, no grading, no measurement of another run - so measuring, blinding and
   grading happen BETWEEN runs, one at a time; and a run killed by the memory limit (exit 137) is void and re-run.
6. **Given** the order could favor one arm (a warmer page cache, a shared ledger the first run writes), **When** the runs are scheduled,
   **Then** the arms alternate - which arm goes first on the first task is drawn from a recorded seed, and the other arm goes first on the
   second task, so at n=1 neither arm runs first on both, and anything a run writes outside its clone that a later
   run would read is listed in the run log.

---

### User Story 3 - Quality is judged blind, against criteria fixed beforehand (Priority: P1)

The grader cannot tell which arm produced which output, and the criteria it grades against existed before any output did.

**Why this priority**: token counts alone cannot say whether the extra effort bought anything; an unblinded or post-hoc grade would
be worthless.

**Independent Test**: each task's rubric is committed to the repository before that task's first run starts (the commit's timestamp is
the proof; a replaced task's rubric before the replacement's first run); the graded outputs carry only labels A and B; the key mapping labels to arms is written by a step the grader does not read
and is opened only after both grades are recorded.

**Acceptance Scenarios**:

1. **Given** the rubric for a task, **When** it is written, **Then** it is committed before that task's first run - a replaced task's rubric
   before the replacement's first run (see the edge case) - and never edited afterwards; a later wish to grade something else is noted in the report as an observation, not scored.
2. **Given** two outputs of a task, **When** they are prepared for grading, **Then** anything naming the effort level or the run (session
   names, clone paths, the prompt's arm line, commit trailers) is stripped, and the outputs are labeled A and B in a random order.
3. **Given** the blinded outputs, **When** they are graded, **Then** a fixed grader agent (one agent file, its model and effort pinned)
   scores both against the rubric, and the GM grades them too; for research the GM's judgment is final, and for implementation the
   GM's judgment breaks a tie or a disagreement with the grader.
4. **Given** the grades are recorded, **When** the key is opened, **Then** the report records both graders' scores per arm and says how
   the outputs differ (depth, correctness, missed items, a better approach found), not only which one won.

---

### User Story 4 - The better output lands; the other is discarded (Priority: P2)

The experiment's work is real work: the winning research entry and the winning implementation land on main by the project's own procedure.

**Why this priority**: the handoff asks that the tasks be genuinely wanted so the experiment is not waste; landing is how that value is
kept.

**Independent Test**: after grading, the winning output of each task is on main through the normal stop-work route (a green `make done`
for the engine change; the research page's checks for the entry), the losing clones are discarded unmerged, and the future-work entries
each task closes are closed.

**Acceptance Scenarios**:

1. **Given** the research winner, **When** it lands, **Then** its entry has passed the checks every research entry passes (source-reader,
   quote-check, record-format, source-applicability), and the Ubame sheet itself is NOT edited by this feature (the entry says what the
   record found; changing the sheet is a follow-up left in `future-work/compounds.md`).
2. **Given** the implementation winner, **When** it lands, **Then** on every scripted hamlet the houses that carry the storehouse annex are
   the largest ones, at the share the record supports, the tests say so, the moved maps are regenerated and reviewed as the project reviews a moved map, and the
   gate is green.
3. **Given** main has moved since the starting commit (other features touch the hamlet generator), **When** the implementation
   winner lands, **Then** it is merged onto current main by the session that lands it, and the post-merge result, not the run's, is what the
   gate passes; the extra work of that merge is recorded in the report and not counted against either arm.
4. **Given** neither output of a task meets its rubric's pass line, **When** grading ends, **Then** neither lands, the report says so, and the
   task stays open in future-work with what both runs found.

---

### User Story 5 - The experiment can be repeated cheaply later (Priority: P3)

A later session can re-run a reduced version when the model or the scaffolding changes, or expand this pilot, without re-deriving the
procedure.

**Why this priority**: the handoff's caveat - the result is specific to Opus 5.5 and this tooling in late 2026.

**Independent Test**: the launcher, the measurement script and the blinding step take the task, the arm and the seed as inputs, and the report
says how to add an arm (`high`) or a second run per cell.

**Acceptance Scenarios**:

1. **Given** the pilot shows a large difference, **When** the GM asks for the next round, **Then** adding `high` as an arm or a second run per
   cell needs no new tooling, only new runs.

### Edge Cases

- **A run asks the GM a question.** No human help during a run. If a run cannot proceed without an answer, both runs of that task are given the
  identical answer, logged with the time it was given; a run that stops and waits is measured up to its stop and resumed with the same answer.
- **A run fails outright** (does not finish, cannot pass its checks, exhausts a budget). It is scored as it stands - failure is data - and its
  counts stand in the table. It is re-run only if the failure was the environment (exit 137, a host outage, a network loss), which is recorded.
- **Both outputs are equally good.** The rule below decides on cost; a tie in quality is a legitimate result.
- **The task turns out already done or impossible at the starting commit** (e.g. another feature removes what the task
  changes - as feature 280 M68 did to task I's first pick). Found by the pre-flight check, which confirms on the code or the maps that the
  defect exists, not only that its future-work entry is open; the task is replaced after asking the GM, and its prompt and rubric are
  rewritten and frozen again (their hashes recorded) before its next run, and its runs still start from the experiment's one start commit,
  the launcher supplying the frozen files. A new start commit is allowed only when the replacement cannot be done at the original start,
  measured and recorded; even then the run's clone holds no record linking a run id to an arm (FR-003). A run of the replaced task stays in
  the record, set aside, and is not graded.
- **The prompt names its arm by accident** (e.g. a clone path containing "xhigh"). The clone names and session names use neutral run ids; the arm
  is recorded only in the run log.
- **Usage-limit exhaustion mid-run.** The run is paused, not voided; its wall-clock excludes the pause, which is logged.
- **A shared resource differs between runs** (the host page cache, the sources-consulted ledger, the research claims file). The run log records
  what each run found there at start; a research run's cache hits are counted separately so a later run's advantage from an earlier one's fetches
  is visible.

## Requirements

### Functional Requirements

- **FR-001 Arms and runs**: the pilot is four runs - task R and task I, each at `medium` and at `xhigh` - with Opus 5.5 (`claude-opus-5-5`) as the
  model in every run. Adding `high`, or a second run per cell, is the expansion the decision rule may call for, not part of this pilot.
- **FR-002 Tasks**: task R is the Ubame servants' quarters question written as one research question on the record (at most one new question plus
  the registry keys it needs, within the page-session write cap), carried through its check-and-apply session. Task I is the storehouse annex ranked
  by size in the hamlet generator, carried to a green local `make done` with the moved maps regenerated. Each run stops short of landing: it commits in its
  own clone and does not push.
- **FR-003 Launch**: each run is a top-level headless session started by one command that takes the task, the arm and the seed, creates a fresh clone
  from the recorded starting commit under a neutral run id, leaves out of it every record linking a run id or position to an arm (the run
  records, the order, the interventions), sets the effort level for the whole session at launch, and logs the command line. Every
  headless session the run itself starts (a research page's write and check-and-apply sessions included) runs at the run's arm effort, and
  the run log records each session's effort; the project's existing headless runner, which today passes a model and no effort, is extended
  to carry it, rather than a second runner being written.
- **FR-004 The prompt**: one prompt file per task, identical across arms (byte-identical; its hash is in the run log), committed with the rubrics. It
  gives the task, where its future-work entry is, the stop point (FR-002), the no-human-help rule, and nothing about effort.
- **FR-005 Controls**: same model, same starting commit, same hooks, agent files and settings in every run; the defined check agents run at their pinned
  tiers in both arms; an ad-hoc dispatch that checks or judges runs at one fixed effort in both arms, and only reading, fetching, translating or
  extracting dispatches may instead be counted per arm (US2 AS3); every headless session a run starts runs at the arm's effort (US2 AS4); the experiment is
  strictly sequential - one run at a time, each launched only under the memory headroom threshold, and nothing else of the experiment
  running beside a live run (US2 AS5); the arms alternate which goes first, the first task's order drawn from a recorded seed.
- **FR-006 Measurement**: per run, from the session transcripts - the main session's and every subagent's: input, output, cache-read and cache-creation
  tokens, main and subagents shown apart and summed; wall-clock from first to last event, excluding logged pauses; tool calls by tool; subagent
  dispatches by agent type. Usage-limit share is recorded when it can be observed and said to be unobserved when it cannot.
- **FR-007 Rework signals**, per run, from what the project already logs: guard firings by guard and rule (refusals and corrections separately), check
  and review verdicts that were not a pass and the rounds each needed, test and gate runs that failed before the last green one, the number of commits
  that revert or fix the run's own earlier work, and escalations - `escalation-check` verdicts and any question the run put to the GM.
- **FR-008 Rubrics before runs**: one rubric per task, each with scored criteria and a stated pass line, committed before that task's first run starts (a
  replaced task's rubric before the replacement's first run) and not edited afterwards. The research rubric scores at least: the answer to the question and whether the sources read support it; the breadth of the search
  (languages, kinds of source) and whether an absence is stated as one; citation correctness as the checks judge it; and clarity for the casual reader.
  The implementation rubric scores at least: the acceptance criteria met (on every scripted hamlet the annex sits on the largest
  houses, at the record's share; no new failure elsewhere); the regression and gate results; the review findings on the moved maps; the size and shape of the diff;
  and the decisions recorded in the four classes. Defects found in the implementation winner AFTER grading - at the landing merge, the post-merge
  gate, the moved-map reviews, and any later review before the report closes - are recorded in the report as their own section, not re-scored.
- **FR-009 Blinding**: a step the grader does not read strips arm-identifying text from each output, labels the two outputs of a task A and B in a random
  order, and writes the key to a file opened only after both grades are recorded.
- **FR-010 Grading**: one grader agent file, model and effort pinned, which does not inherit the project's instructions (as every defined agent here), grades
  both outputs of a task against its rubric; the GM grades them too. The GM's grade is final for research; for implementation it breaks a tie or a
  disagreement.
- **FR-011 Decision rule** (fixed now, before any run; applied per task type):
  - **Adopt `xhigh`** if its blind quality is clearly better - both graders prefer it, or the GM does with a stated reason on a rubric criterion - OR if
    quality is not worse and BOTH its total tokens and its wall-clock are at most 1.25x `medium`'s (rework having paid for the extra thinking).
  - **Keep `medium`** if `xhigh`'s quality is worse, or if quality is the same and `xhigh` costs more than 1.25x in total tokens or in wall-clock.
  - **Inconclusive** otherwise - the two graders disagree and the GM declines to decide.
  - **Expand** (add `high`, or a second run per cell) when the graders find a clear quality difference in EITHER direction, or when total tokens or
    wall-clock differ by more than 2x between arms in either direction - the GM's "if there is a big difference between medium and xhigh". The expansion
    is proposed to the GM, not started.
- **FR-012 Report**: a short report in the repository with the per-task table (arm x run: tokens by kind, main vs subagents, wall-clock, tool calls, rework counts,
  both quality scores), the qualitative differences, the defects found later in the implementation winner (FR-008), the decision rule's outcome per task type with its arithmetic, the pinned tiers that ran (and any control listed as unmet), every logged
  intervention, and the caveats (pilot, n=1; specific to Opus 5.5 and this tooling as of 2026-09; re-run a reduced version when either changes significantly).
- **FR-013 The setting**: if the rule's outcome changes a default, the recommended setting is written for `.claude/settings.local.json` (the effort level,
  or the model-scoped form), not the committed, guarded `settings.json`, unless the GM prefers otherwise; sessions can still override it. This feature
  recommends; the GM applies it.
- **FR-014 Landing**: the winning output of each task lands per US4; the losing clones are deleted unmerged; the run artifacts that the report cites (run log,
  measurement output, grades, key) are kept in the feature directory.

### Key Entities

- **Run**: task, arm, seed, run id, starting commit, clone path, prompt hash, start and end times, pauses, exit status, void or valid.
- **Run log**: every run's entry and every intervention (a question answered, a pause, a re-run with its reason).
- **Measurement**: per run, the counts of FR-006 and FR-007.
- **Rubric**: per task, criteria, weights, pass line; frozen at commit.
- **Blinded pair and key**: per task, outputs A and B and the sealed mapping to arms.
- **Grade**: per grader per output, per-criterion scores and a note.
- **Report**: the table, the differences, the outcome per task type, the recommendation.

## Success Criteria

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003, FR-006, FR-007) all four runs complete (or fail on their own merits) with every count of FR-006 and FR-007 filled from the transcripts and logs, and none
  counted by hand.
- **SC-002** (FR-004, FR-008) each task's rubric is committed before that task's first run starts (a replaced task's before the replacement's
  first run), and neither changes after it.
- **SC-003** (FR-009, FR-010) the grader agent grades each pair without access to the key; the key is opened after both grades per task are recorded.
- **SC-004** (FR-011, FR-012, FR-013) the report states an outcome under FR-011 for research and for implementation, and the arithmetic can be re-done from its table.
- **SC-005** (FR-014) the better output of each task that meets its pass line is on main; the other is discarded; the future-work entries they close are closed.
- **SC-006** (FR-005) no run was killed by the memory limit and left counted; no two runs overlapped in time; every run's record shows the
  container's memory under the headroom threshold at its launch; no measurement, grading or gate of the experiment overlapped a live run.

## Decisions Recorded

This feature is an experiment on process; it decides nothing about what a map draws. The rendering decisions of task I (how the houses are ranked, the tie
rule, the share) and task R's findings are made and recorded by the winning run in its own work, in the four classes, as
every change to a map is; the report links them.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Arms `medium` vs `xhigh`, one run per cell | GM ruling | "medium vs xhigh to start with"; "Pilot: 1 per arm per task" | `request.md` |
| Tasks R and I, hamlets only for I | GM ruling | "anything involving settlement types which have not yet been scripted" ruled out | `request.md` |
| Decision rule thresholds (1.25x, 2x) | GUESS - a process choice with no measured basis | no measurement of one session's run-to-run spread exists here, and the handoff warns "the same effort level run twice can differ a lot"; the figures are round numbers picked so that "comparable" and "big" have a fixed meaning before any run, and the report says they are guesses | FR-011 |
| Arm order alternates between tasks | process choice (the handoff allows alternate or randomize) | at n=1, independent randomization can put one arm first on both tasks | US2 AS6 |
| Task R stops at the record, not the Ubame sheet | process choice | the GM's rule: no hand-map edits inside other work (2026-09-28); keeps the task inside one research session pair | US4 AS1 |

## Assumptions

- `claude -p --effort <level>` sets the effort for the whole headless session and overrides the settings files (the handoff; the CLI lists the flag).
- Session transcripts under `~/.claude/projects/` carry `message.usage` on each assistant message, and subagent transcripts are findable from the session's; the
  measurement reads them, not the terminal.
- The defined check agents already pin their own model and effort (twelve agent files: eight at `high`, four at `medium` today), so the checker control
  holds for them without change.
- The runs are billed to the GM's subscription; the pilot's cost is roughly four sessions of 30-60 minutes plus grading, which the GM accepted by choosing the pilot.
- Other features may touch the hamlet generator while the runs are made; the implementation runs start from a fixed commit regardless, and the
  landing merges onto whatever main is then (US4 AS3).
- The runs are the implementing session's to launch; writing this spec, the plan and the tasks does not run them.

## Out of scope

- A `high` arm, a second run per cell, other models, other task types - the expansion, proposed to the GM when the rule calls for it.
- Changing the Ubame sheet from task R's finding.
- The storehouse annex at any tier above the hamlet.
- Applying the recommended setting; the GM does that.

## Review history

- Round 1 (spec-fidelity, 2026-09-29): CHANGES REQUIRED - seven items: FR-011's adopt and keep clauses overlapped and left a
  gap; expansion fired in one direction only; ad-hoc checkers were countable instead of fixed; the page-session runner would
  run the research at the default effort in both arms; escalations and defects found later were missing; the thresholds' reasons
  were unmeasured claims. All seven applied; the aside (alternate the arms) taken.
- Round 2 (spec-fidelity-verify, 2026-09-29): FAITHFUL - all seven items resolved; the alternation within the request.
- After acceptance, 2026-09-29: formatting only - each success criterion's FR list moved beside its id, where spec-lint reads it; no wording changed.
- Amendment, 2026-09-29 (the GM: "change the plan so that you will instead run these tests sequentially rather than in parallel for memory
  reasons"): US2 AS5, FR-005 and SC-006 make the experiment strictly sequential end to end - one run at a time, each launched under a memory
  headroom threshold, and nothing else of the experiment beside a live run; research R5 D7 carries the threshold. The review counter resets.
- Amendment review, 2026-09-29: round 1 NOT-REVIEWABLE (two unlabeled figures, labeled); round 1 CHANGES REQUIRED (the gate read raw
  `memory.current`, page cache included - now the working set); round 2 CHANGES REQUIRED (a quiet-host memwatch figure is never published
  - now an offset measured at a warning); round 3 FAITHFUL. Its two asides applied after: the offset re-derived with the gate's own
  subtraction (`inactive_file`, 0.9 GB - looser than the 1.5 GB it replaces, which had subtracted all page cache where the gate subtracts only the inactive part), and a leftover sentence reworded.
- Amendment, 2026-09-30 (the GM, on task I's premise found gone): "Replace the task (Recommended)" and "Storehouse by house size". Task
  I becomes the storehouse annex ranked by size; its prompt and rubric are rewritten and re-frozen at their own start; the edge case now
  says the pre-flight confirms the defect on the code or the maps. The review counter resets.
- Amendment review round 1 (spec-fidelity, 2026-09-30): CHANGES REQUIRED - the re-freeze gave task I its own start commit, which the
  one-start-commit control does not allow when the task can be done at the original start (it could: the engine is the same at both); the
  clones carried records naming the arms; four passages still froze the rubrics before the FIRST run of either task; the new premise check
  was unrecorded. All four applied: one start commit, the frozen files supplied by the launcher, the feature directory left out of every
  run clone (sparse checkout), the rubric passages per task, the premise check in interventions.md.
