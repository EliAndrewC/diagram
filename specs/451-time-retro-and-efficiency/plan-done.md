# 451-time-retro-and-efficiency - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-20 -->
### T01 (the plan review the tick and the push require, feature 243)

- **Approach**: `spec-fidelity` reads `request.md`, `spec.md` and this plan and rules on each decision that narrows what was asked -
  D4, D8, D11, D12 and D14 named for it - recorded with `make plan-verdict F=451 FILE=<json> AS=spec-fidelity`.

### T01 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the plan does what the GM approved, no less and no more.
2. **The constraints.** The spec's FR-001 to FR-012; the GM's words in `request.md`; constitution XVI.
3. **Where each comes from.** G: `request.md`'s approval; O: `research.md`.
4. **Do they describe the world here?** The reviewer reads the plan against the request, not against itself.
5. **The order.** Before any other task is ticked.
6. **The exits.** Green: a CLEAR `plan-review.json`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One review round, at most five.
9. **Done, measured.** `plan-review.json` CLEAR for this `plan.md`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - a review, not a fix.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T02 (FR-001: two make detectors that disagree, so a timed or subshelled make run logs no target - research R1)

- **Approach**: D1, in the guard crate. Held: `rust/guard/src/shared/make.rs`, `rust/guard/src/guards/event_log_hooks.rs` (`make
  guard-edit` on each first). Red first: `timeout 2400 make static`, `flock /tmp/x make rust-test`, `(make hooks-test > log) &`, `{
  make static; } &`, `VAR=x make static &` and `env X=1 make static &` each yield their target; `echo make static` and a heredoc's `make` yield none; the guards reading `shared::make` keep their suites'
  verdicts.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the detector | n/a - no map | n/a | none | n/a |

### T02 Approach (checklist part A)

1. **The goal, in the world.** No map changes; one reading of which make targets a command runs, shared by the log and every guard.
2. **The constraints.** FR-001; D1; the guards that read `shared::make` (gate, make-only, measure, shell-check) unchanged in verdict on their suites; constitution XVIII (a mention is not an invocation).
3. **Where each comes from.** G: the GM's approval of "maps make targets to tests, compile, gate, land, review and docs"; O: research R1.
4. **Do they describe the world here?** R1's join of the log to the transcripts shows which commands carried no target and why.
5. **The order.** First: the table, the readers and the new guards all read this detector.
6. **The exits.** Green: the red cases pass, `make rust-test CRATE=rust/guard` and `make hooks-test` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The red cases green; the XIII baseline (`make hooks-test HOOKS_ALL=1`, `make rust-test`) taken in a detached worktree before the first edit and matched after.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** `timeout 2400 make static` is today booked "other tool" and `(make static) &` is invisible to every guard reading `shared::make` - a tool answering wrongly.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T03 (FR-001: 210 of the window's tool-minutes booked "other tool", observed 2026-11-20, method: the `ms` of the log's PostToolUse lines since 14:00Z summed by `cat` - research R1)

- **Approach**: D2, in the writer. Held: `rust/guard/src/guards/event_log_hooks.rs` (`make guard-edit` first). The table's rows are
  `data-model.md`'s, finished from the Makefile's targets, `format`, `render-sync` and `map` among them (R1's largest after the tests),
  each row commented with why. Red first: `make static`, `make rust-test`, `make hooks-test` and `l7r-gate.sh rust test --crate
  rust/guard` class as tests, `make land` as land, `make frobnicate` as other; a subagent's call carries its meta file's task, a `make
  land T=T05` line carries `T05`, a main-session call the clone's active task.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the table, the task field | n/a - no map | n/a | none | n/a |

### T03 Approach (checklist part A)

1. **The goal, in the world.** No map changes; every make run of a window is booked under its bucket and its task.
2. **The constraints.** FR-001; D2; the hook never refuses and never prints; one meta-file read a subagent call at most.
3. **Where each comes from.** G: the approved categories; O: research R1 (the targets and their minutes), R2 (the meta file).
4. **Do they describe the world here?** R1's minutes by target name the rows that matter most.
5. **The order.** After T02; before T07, T08 and T14, which read the table and the task field.
6. **The exits.** Green: the red cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The red cases green; a real `make static` in the clone logs `cat` tests and its task.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new rows and a new field.

**Found and left?**
- The bundle crate's coverage depends on the caller's environment. With `SPECIFY_FEATURE` exported, `make static` fails cover on
  `rust/gate/crates/bundle/src/record/helpers.rs` line 537: `consulted::context`'s error arm, which a test reaches only when no
  feature is set. Without the export the crate's cover is clean (observed 2026-11-20, method: `make static` with and without the
  export, then `l7r-gate.sh rust cover --crate rust/gate/crates/bundle`). Not fixed here because the crate is outside T03's files; filed as T24 (the test given its own
  environment), which lands before T08 reads the columns.
- Two features' lanes share this clone, and `.specify/feature.json` names 449. So the hook writes this clone's lines to the 449 log,
  whichever feature's work they are. A 451 builder's `T03` in the 449 log then reads as 449's T03: the `task` field names the task but
  not its feature. Not fixed here because the line's feature is chosen where the line is filed, the same field T26 corrects: filed as T26 (each line
  filed under the feature of the task it carries), which lands before T07, T08 and T14, the readers of the task field. The lines written
  between T03's landing and T26's are re-filed by T26 itself: a line whose task names no task of its log's feature but one of another
  feature's is moved to that feature's log - the two features' ids never collide (451's are two digits, `T03`; 449's three, `T003`;
  observed 2026-11-20, method: the task ids of both features' tasks.md and tasks-done.md) - so no reader books one feature's time to the other's.
- An Agent dispatch line with no `T=` carries the clone's active task (its dispatcher's) until T07 reads the task from its
  `description` (D6).
- The live hooks run the mirror's guard binary, so lines written before this lands still say `other tool`. "Done, measured" was
  replayed through the clone's hook shim: this session's `make static` call logged `cat` `tests` and `task` `T03` (observed
  2026-11-20, method: the call's payload piped to `tests/hooks/event-log-hooks.sh` with `L7R_EVENTS_DIR` pointed at a scratch
  directory). It is owed again on a live line after landing.
- `T="T1,T2"` books only `T1` (T18).
- The readers still book by the frozen `cat`, and `where_time.rs` only learned the new `tests` word. Booking by `make` through
  `bucket_of` is T08's.
- `data-model.md`'s rows `push-checks` and `make-docs` are not make targets. They are kept as rows that never match.

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T26 (the event log filed every line under `.specify/feature.json`, which `make task-start` rewrites to the feature started last: 50 lines of 451's T26 and T03 sat in 449's log as 449's, observed 2026-11-20, method: the 449 log's lines whose `task` is no 449 task, matched to `task-starts.jsonl`)

- **Approach**: the writer files a line by the feature of the task it carries, in a new module
  `rust/guard/src/guards/event_log_hooks/filed.rs` (held: `make guard-edit` first, as was `event_log_hooks.rs`, which now calls it):
  - the FEATURE, first that says: a make command's `F=` (one `specs/<F>` or `specs/<F>-*`); else the dispatch's brief - an Agent
    call's own `description`, else the subagent's meta file's (D2's read) - through `brief_feature`; else the feature whose task-start
    in force names the line's task (else the latest that started it); else the FALLBACK, `feature_of` as before (`L7R_FEATURE_DIRECTORY`,
    then `SPECIFY_FEATURE` in the hook's own environment, then feature.json), the line marked `"fallback": true` unless the
    environment declared it (a page session's `L7R_FEATURE_DIRECTORY` is that session's feature, not a guess).
  - `brief_feature`: the number before a task id (`451 T26: ...`, `spec-fidelity on 451 T03's section`); else a number standing
    alone, not inside a hyphenated word, naming a feature this clone has started a task of. Without that hold a plain-number rule moved
    2,707 lines, 545 of them to `008-mode-a-composition` on "FR-008", measured 2026-11-20 (`make events-refile DRY=1`, the plain rule).
  - the TASK: the command's `T=` (`line`, unchanged); else the brief's `T<n>`; else the task-start in force for the line's own
    feature - D2's fallback, now of the line's feature, not of feature.json's. No `tasks.md` is read on a hook: one `task-starts.jsonl`
    read and at most one meta read a line, as D2 had, and the `specs/` listing only when an `F=` or a brief's number asks.
  - Red first, `two_features_builders_in_one_clone_each_line_in_its_own_log` (the guard's `event_log_hooks/tests.rs`): one clone,
    feature.json naming `449-b`, a `451 T26` builder, a `449 T236` builder, briefs naming only a task or only a feature, the main
    session's `make land F=451 T=T03` and `make task-start F=451 T=T26` (both halves of each call), a dispatch's own line, a subagent's
    stop, a brief whose numbers are counts and `FR-` ids, and calls nothing names.
    - before: the 451 builder's `make static` filed under `449-b` carrying `T26`.
    - before: 617 passed and that 1 failed, measured 2026-11-20 (`make rust-test CRATE=rust/guard`).
    - after: 619 passed, the case split in two for clippy's function length (`a_line_nothing_names_is_filed_by_feature_json_and_marked`
      the fallback half), measured 2026-11-20 (`make rust-test CRATE=rust/guard`).
    - the new lines of both crates 100% covered, measured 2026-11-20 (`l7r-gate.sh rust cover --crate`).
  - The re-file, `make events-refile [DRY=1]` (`l7r-gate measure event-log refile`, new
    `rust/gate/crates/measure/src/measure/event_log/refile.rs`, its tests `refile/tests.rs`; not held): the writer's chain run backwards
    over every log of the clone, in two rules - BY BRIEF (a subagent's line, a dispatch's own line, its brief naming another feature
    through the same `brief_feature`, unless the line carries its own `T=` of its log's feature; its task its own carried `T=` where the
    new feature has it, else the brief's, else kept where it is the new feature's, else that feature's start in force at the line's
    time) and BY TASK ID (T26's line: a task no task of its log's
    feature, `tasks.md` and `tasks-done.md`, moves to the feature whose start of that id was in force at the line's time, when that
    feature has the id). The second rule needs the time: `T03` is a task of 16 features and `T01` of 21, observed 2026-11-20, method:
    the ids of every feature with a log in the clone, so "names one of another feature" is read as the start this clone made of it.
  - BY BRIEF IS AN EXTENSION of T26's stated re-file rule, which names only the task id; it is the writer's own brief rule applied to
    the past lines that rule cannot reach (the lines with no task, or a fallback task, below), and it made most of the moves (item 9),
    so the plan review rules on it. Without it the re-file moves only the by-task-id lines and leaves every untasked builder line where
    feature.json put it.
  - The moves are appended to their targets (`O_APPEND`, as the hooks write; both readers sort by `t` and `reversal` reads a log as a
    set), a line already there skipped; the source is rewritten through a temporary file, bytes a live hook appended meanwhile carried
    over before the rename.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the line's feature, the re-file | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T26 Approach (checklist part A)

1. **The goal, in the world.** No map changes; each event-log line is in the log of the feature whose task it served, so
   `where-time` and `feature-report` book each feature's own time when two features are worked in one clone.
2. **The constraints.** T26's line (the brief, the task-start in force for that feature, the make target's `F=`; feature.json only where
   nothing else says; red first with two features' builders in one clone; the re-file by task id; a plan for the lines with no task);
   D2 (the task field, its meta read); the hook never refuses, never prints, and stays cheap; T03's red cases stay green.
3. **Where each comes from.** O: the misfiled lines (the title's figure); O: the dry runs below; the task as filed (T26's line, T03's
   plan review rounds 1 and 3).
4. **Do they describe the world here?** The briefs and the starts were read, not assumed:
   - of the main session's 30 latest dispatches, measured 2026-11-20 (their subagent meta files' descriptions):
     - 12 name feature and task (`451 T26: ...`), measured 2026-11-20 (as above).
     - 7 a task only (`T226: polder counters`, resolved by its start), measured 2026-11-20 (as above).
     - 6 a feature only, measured 2026-11-20 (as above).
     - 5 neither, filed by the fallback, measured 2026-11-20 (as above).
   - the clone's starts resolve every task-id line to one feature, 0 left, measured 2026-11-20 (`make events-refile`).
5. **The order.** After T03 (the task field); before T07, T08 and T14, the readers of the task field.
6. **The exits.** Green: the red case, `make rust-test` on `rust/guard` and `rust/gate/crates/measure`, `make quick`, `make static`,
   `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: a brief's plain numbers are mostly counts and source ids (the `brief_feature` hold above).
8. **The budget.** One landing.
9. **Done, measured.** The re-file on this clone's logs:
   - 212,481 lines read in 28 logs, measured 2026-11-20 (`make events-refile DRY=1`).
   - 1,734 lines moved, 0 left unresolved, measured 2026-11-20 (`make events-refile`).
   - 449 -> 451: 818 lines, 813 by brief and 5 by task id, measured 2026-11-20 (`make events-refile`).
   - 451 -> 449: 187 lines, 186 by brief and 1 by task id, measured 2026-11-20 (`make events-refile`).
   - older features, the same defect: 729 lines across 16 pairs, 13 by task id, measured 2026-11-20 (`make events-refile`).
   - among them 415 -> 405: 7 lines of 405's T106, measured 2026-11-20 (`make events-refile`), the case `task_start.rs` names.
   - all moves: 1,715 by brief and 19 by task id, measured 2026-11-20 (`make events-refile`).
   - a second run: 0 lines moved, measured 2026-11-20 (`make events-refile`).
   - the moved lines' tasks: 872 added, 3 changed, 0 removed, measured 2026-11-20 (the backup against the logs, line by line).
   - a carried `T=` replaced: 0, measured 2026-11-20 (the same comparison, lines whose `make` is a tick, task-start, decide or land).
   - no line lost: 212,435 lines before, 212,488 after, 0 missing and 53 new (live hooks), measured 2026-11-20 (a script comparing a
     copy of the logs taken first with the logs after, the `task` field set aside).
   - replayed through the clone's hook shim: a 451 builder's `make static` and the main session's `make land F=451 T=T26` filed in
     451's log, a bare `git status` in 449's with `fallback`, observed 2026-11-20, method: three payloads piped to
     `tests/hooks/event-log-hooks.sh` with `L7R_EVENTS_DIR` pointed at a scratch directory.
10. **Before moving a constant.** n/a - one new knob, labeled GUESS beside it: the re-file's slack for a start's own lines
    (`START_SLACK`), 60 s, a GUESS bounded by the calls it must cover:
    - 322 of 335 `task-start` calls took 60 s or less, measured 2026-11-20 (the `ms` of every log's `task-start` `PostToolUse` line).
    - their p90 9.4 s, measured 2026-11-20 (the same lines).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of `make where-time F=451` or `F=449` sees each feature's own builders' time; nothing on a map.

**The lines with no task, or whose task came from D2's fallback** (T03's plan review, round 3). The re-file by task id cannot reach
them: a fallback task is the log's own feature's start, so it always names a task of its log. They are filed so:
- A SUBAGENT's line with no `T=` is filed by its dispatch's brief where it names a feature, or a task whose start does; the re-file
  reaches the past ones by the same brief (item 9's by-brief counts), its task re-derived. A brief naming neither is filed as the next
  bullet says.
  - such briefs: 25 of the 30 in item 4, observed 2026-11-20, method: item 4's count.
- A line nothing names - the main session's own calls with no `F=`, a brief naming neither feature nor task - is filed under the
  fallback, feature.json's feature, its task that feature's start in force, and marked `"fallback": true`, so T07, T08 and T14 can keep
  that time apart rather than book it to whichever task feature.json named. A past such line carries no mark; its shape is the same
  (no `by`, a `task`, no carried `T=`), which a reader can test.
  - such lines: 154 of the two logs' 1,555 since 451's first start, measured 2026-11-20 (the logs after the re-file: no `by`, no Agent or subagent event, no carried `T=`).
- D2's text ("the clone's last `task-starts.jsonl` entry for the feature") stands, read as the line's feature.

**Found and left?**
- The live hooks run the mirror's guard binary, so lines written until T26 lands are still filed by feature.json. `make
  events-refile` is owed once more after the landing; it is idempotent, so a re-run moves only those lines.
- The re-file also moved older, closed features' lines (item 9's older pairs, 716 of them by brief); their feature reports, if
  regenerated, now book that time where the briefs put it. Two are judgment calls the plan review may rule the other way: "Classify
  427's call-cutting hunks" (435's log to 427's) and "Check the 405 per-claim draft" (443's to 405's) may have been the dispatching
  feature's own work. A copy of the logs from before the re-file is at `/tmp/t26/backup/` (a wholesale restore would drop the lines
  appended since).
- `make static` stopped at `rust lint` on `rust/phases`, another builder's uncommitted work in this clone (still red on its own
  `rust lint --crate rust/phases`); T26's crates passed every step of the recipe run per crate (lint, format, cover, dead) and the
  tree-wide steps (file-scale, claims coverage, spec-lint, conflict, make-docs after `make docs` regenerated the targets page).
- `rust/guard/CLAUDE.md`'s `event_log_hooks` row does not name `filed.rs`, nor `rust/gate/CLAUDE.md`'s `measure` row `event_log/refile.rs`;
  both indexes are outside T26's files.
- An Agent dispatch line now carries its brief's task where the brief names one; T07 (D6) still owes the prompt's first line where the
  description names none, and the agent's tokens.

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T25 (`make decide`'s lint stopped at its first finding: a section with four findings took four runs and four turns to clear, found writing T23's section, 2026-11-20)

- **Approach**: each rule of the plan lint (`rust/gate/crates/plan/src/plan/lint.rs`) now runs to the section's end and returns
  every finding with its span in the section, where it returned its first. `lint::findings` gathers them in the rules' order, and
  `lint::render` reports them in one refusal: the number first, then each rule's words once with its findings beneath, each placed
  by its plan.md line. `make decide` (`plan.rs`' `decide`) adds the approach gate's refusal to that report, where the lint's first
  finding used to stop the run before the gate was asked. `make plan-delta` reports every changed block's findings and the open
  tasks with no approach block the same way. A finding is placed through the rewrites the rules read (a fenced block blanked, a
  code span replaced) by `Rewritten`, which keeps each rule's text exactly as before and maps the offsets back on the side.
  `lint::plan_lines` places a section joined from several headings of one task line by line, in the plan's order.
  A label rule's finding is merged into an earlier one only where both found the very same span, since one label clears both. A
  clause inside a longer finding stays, because its own label is owed.
  Each rule's refusal now states its unit and where its label must sit:
  - the unit figure's unit is the clause, cut at `;` too and even inside a code span, so a label at a sentence's end does not
    cover a clause before its `;`;
  - the GM quote's unit runs to a sentence's end or a blank line, so a bullet list with no blank line and no full stop is one;
  - item 4's unit is the sentence, cut after `. ` and at each unindented line, and only `measured <date> (<method>)` or `m:` pass
    there, the observed form and a research label refused there though they pass elsewhere;
  - the count's and the differential's unit is the sentence, cut outside code spans and not at `;`;
  - the red exit's unit is item 6 of each Approach block.
  The item-4 rule now reads item 4 of every Approach block (part A or B) in the section, and one under no heading, where it read
  only the first `4. **` item (`ITEM4.find`): a re-answered block's unlabeled figure reached its plan review unrefused. A
  performance checklist's item 4 is not read, because that block prompts and never gates. Read unrestricted, it would have
  refused 444's T26 and T27 on theirs.
  Red first: `a_second_approach_blocks_item_4_is_read_too`, with an unlabeled figure in a second Approach block's item 4:
  - before: 0 of 1 found, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t25/red2.log`).
  - after: 1 of 1 found, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`).
  The fix's reach over 949 sections of every `specs/*/plan.md` and `plan-done.md`: 0 verdicts moved and 51 item-4 findings appear in 28 sections, every one already refused for another finding, measured 2026-11-20 (the throwaway dump, `/tmp/t25/before2.tsv` against `/tmp/t25/after3.tsv`).
  The 28 sections, measured 2026-11-20 (the same dump): 385's plan-done T03, T08, T10 and T41; 405's plan T16, T17, T27, T131, T133
  and T147; 405's plan-done T09, T16, T18, T19, T20, T26, T29, T43, T53, T55, T57, T96, T107, T116, T118, T119, T134 and T135.
  The reporting change moved no rule's verdict, measured 2026-11-20 (a throwaway test dumping `lint::refusal` over every task section of every `specs/*/plan.md` and `plan-done.md` before and after the change, then deleted).
  Over 946 sections, 0 verdicts moved and each old first finding is in the new report, measured 2026-11-20 (the same dump, `/tmp/t25/t25-before.tsv` against `/tmp/t25/t25-after.tsv`).
  Of the 492 refused sections, 353 hold more than one finding, which today's lint reports in one run, not one each, measured 2026-11-20 (the same dump, its finding counts).
  Red first: `decide_reports_every_finding_of_the_section_in_one_run` - a fixture section with a unit figure, a GM quote that
  request.md does not hold and an unlabeled item-4 figure, run through `decide`:
  - before: 1 of 3 findings reported, the GM quote alone, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t25/t25-red-kept.log`).
  - after: 3 of 3 in one refusal, each with its plan.md line, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| every finding reported | n/a - no map | n/a | none | n/a |

### T25 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A plan author meets every finding of a section in one `make decide` run, each
   with its line and its fix, and with the unit that its rule reads.
2. **The constraints.** T25's line (every finding of the section together, each with its line, red first with a fixture of
   three); its brief (no rule's verdict changes, only how it reports; a rule whose unit surprises its author says so in its
   refusal); a verdict moves only where a bug is fixed (the item-4 rule's first match); every line of the crate covered by
   its own tests; the edits held to `rust/gate/crates/plan/`.
3. **Where each comes from.** O: the task as filed (T25's line, found writing T23's section). O: the brief's ground rules for this task.
4. **Do they describe the world here?** Yes - measured 2026-11-20 (the verdict dump above): before the change each rule returned its first finding and `refusal` returned the first rule's, and 353 of 492 refused sections held more than one.
5. **The order.** Independent of T03-T24. It touches the plan crate alone, beside T23's `rustc` and the builder in `rust/phases/`.
6. **The exits.** Green: the red-first test green, `make rust-test CRATE=rust/gate/crates/plan`, `make quick`, `make static`,
   `make hooks-test`, and the verdict dump moving no verdict but where a bug is fixed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The two red-first tests and four new lint tests green, 135 of the crate's tests, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`).
10. **Before moving a constant.** n/a - no constant moves and no rule's pattern changes; the item-4 rule gains a filter by its
    block's heading (`APPROACH_BLOCK`).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** An author sees every finding of a section in one run, not one a run, and is told each rule's unit, and a
    re-answered Approach block's unlabeled item-4 figure is refused before its review. The plan lint is the check it puts right. Nothing on a map.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: T26 to T03 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T26 to T26 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

<!-- plan-archive: archived 2026-11-20 -->
### T27 (T25: the item-4 rule read only a section's first Approach block)

- **Approach**: no change of its own: withdrawn, its fix folded into T25 by T25's plan review (2026-11-20), which ruled the deferral NOT LEGITIMATE; the item-4 rule now reads every Approach block's item 4 there, red first.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| none of its own | n/a | none | none | none |

<!-- plan-archive: archived 2026-11-20 -->
### T27 Approach (checklist part A)

1. **The goal, in the world.** Every Approach block's item 4 is read by the lint.
2. **The constraints.** T25's plan review.
3. **Where each comes from.** R: T25's plan review.
4. **Do they describe the world here?** Yes: T25's red-first test reads a second block's item 4 (measured 2026-11-20 (T25's test)).
5. **The order.** With T25.
6. **The exits.** Green: T25 ticked. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** No landing of its own beyond the tick.
9. **Done, measured.** T25 ticked with the fix.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** Nothing of its own: its fix landed in T25.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: archived 2026-11-20 -->
### T04 (FR-002: no line marks a background run's end, so a wait cannot be booked to the run behind it - research R2)

- **Approach**: D3's writer half: `bg` on a backgrounded PostToolUse, the `BgEnd` line from a notification prompt, `inflight` on Stop
  and SubagentStop; D4's `append_row`, public for the gate's tools; and the one reader's guard against the new kinds:
  `rust/gate/crates/measure/src/measure/events.rs::load_events` sets `BgEnd` and `Phase` lines aside from the time-gap stream (else a
  `Phase` line inside a `make static` call would book the rest of the call "thinking", and a line of no session would form a session of
  its own, the T207 failure) and returns them for T08 and T09. Held: `rust/guard/src/guards/event_log_hooks.rs` (`make guard-edit`
  first); the tool fields move to `event_log_hooks/fields.rs` if the file would pass the file cap. Red first: a fixture notification
  prompt (R2's observed shell form) writes a `BgEnd` with its tool-use id, status and exit code; an agent notification writes none; a
  Stop payload with two `background_tasks` writes both under `inflight`; a log holding a `BgEnd` and a `Phase` line gives `make
  where-time` and `make feature-report` the tables the log without them gives.
- **As built (2026-11-20), where it departs from the approach above**:
  - **An agent's notice names its `<tool-use-id>` too**: 3,801 of 3,986 agent notices carry one, beside all 1,992 shell notices, measured 2026-11-20 (the `-diagram` and clone transcripts' enqueued `<task-notification>` rows tallied by summary and by a `<tool-use-id>` before any `<result>`). R2's "an agent's carries `<task-id>` ... `<usage>`" omits it. So the id alone would write a `BgEnd` for every agent. A notice writes none where its summary opens `Agent "` or its launch line is an Agent call. Only the tags before a `<result>` are read, and the prompt must open with the notice. Each check was deleted alone and its case seen red.
  - **A workflow's and a Monitor's notice write their end.** Each names its launch: 46 workflow notices and 128 Monitor notices ("stream ended", "script failed", a task stopped) carry an id, measured 2026-11-20 (same tally). Each is a background run the session can wait on, so it is booked like a shell's, a fixture pinning each. This is wider than data-model's "a background shell ended".
  - **A `BgEnd`'s `t` is when the notice reached the session, not when the run ended.** A notice waits in the queue while the session is mid-turn. One run was enqueued at 11:44:08 and delivered at 11:47:41, observed 2026-11-20 (the queue's enqueue and remove rows of one notice). So the `t` is right for the end of a wait, but late for the run's span when the session was busy. T08 can take the end from the queue's enqueue row where it needs the span.
  - **The end is filed beside its launch.** It goes in the log that holds the launching call's line, not feature.json's fallback log where the prompt's line goes (a notice names no command or brief, so T26's chain has nothing to file it by). It copies that line's `make`, `cat`, `task` and `fallback` mark, and its `t` as `t0`: the run's span. A launch no log holds ends beside the prompt, under its task and mark. Its fields are data-model's: `id`, `bg` (the task id; `task` stays the spec task), `status`, and `exit`, the summary's last `exit code N`, absent where the run was stopped or its session ended.
  - **The lookup's cost**: 3.7 ms a notice whose launch is in the newest log, measured 2026-11-20 (20 replays through the clone's `l7r-guard`, beside the 15.7 MB 449 log). It is 15.4 ms where no log holds the launch and the whole 449 log is read, measured 2026-11-20 (same method). A prompt that is no notice takes 3.3 ms, measured 2026-11-20 (same method).
  - **`append_row`** stamps `t` where the row has none. It takes `sid` from `CLAUDE_CODE_SESSION_ID` where the row names none, files the row by its `task` through T26's chain, and writes nothing for a row with no `ev`.
  - **The reader**: `events::load_all` returns `Loaded { stream, aside }`, the `ASIDE` kinds kept apart, a line repeated whole kept once, and `load_events` returns the stream. The tool fields moved to `event_log_hooks/fields.rs` with `bg`, `inflight` and the notice's parse.
  - **The live `BgEnd` was replayed, not seen live.** The hooks run the mirror's binary until this lands, and a subagent's own notice never reaches a hook (R2). So R2's shell notice was replayed through this clone's built `l7r-guard` with a launch and a scratch `L7R_EVENTS_DIR`, and wrote its `BgEnd` with `make`, `cat` and `t0`. The first real one is read off the main session's log after the landing.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the end line and the in-flight runs | n/a - no map | n/a | none | n/a |

### T04 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a background run's start and end are both in the log.
2. **The constraints.** FR-002; D3, D4; the hook never refuses and never prints; today's readers unchanged by the new kinds until T08 and T09 read them.
3. **Where each comes from.** G: the GM's approval of "logs that end from its completion notice"; O: research R2 (the schema, the notification texts).
4. **Do they describe the world here?** The notification's `<tool-use-id>` was read from the window's own transcript queue rows (observed 2026-11-20, method: research R2).
5. **The order.** After T03; before T05 and T06 (`append_row`) and T09, which reads the lines.
6. **The exits.** Green: the fixture cases pass. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The three red cases green; one real background run in the clone writes its `BgEnd` (read off the log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new lines, no defect.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T05 (FR-003: a make run's compile, tests and coverage are one span in the log - research R6)

- **Approach**: D4's rust half in `rust/gate/crates/rustc` (not held): a `Phase` line at each step's end through `append_row`, its
  fields the data model's row (`src` `rust`, `step`, `crates` the crate directories from the tree's root, `t0` and `t1` in the hooks'
  stamp, `code`) and the two D4 adds - `make`, the outermost `make`'s first target (the run lock's `run_what`, read through
  `shared::make::invoked`; `rust-<cmd>` with no `make` above, D1's reading of the gate's own form), and `clone`, the tree's root - which
  the data model's row gains. The sites:
  - `build`: `kept.rs`'s `binary_key`, the `cargo test --no-run` a test run's moved key builds, one line a crate (a binary that
    already passed writes its `build` and no `test`).
  - `test`: `side.rs`'s `run_built`, one line a crate; and the one-crate-at-a-time `cargo test` in `answer`'s loop, its compile
    booked `build` apart from its tests in all three of its cases (the plan review, 2026-11-20: the GM asked how much time goes to
    recompiling):
    - a fresh run (`FRESH=1`, or no key to ask): a `cargo test --no-run` with the run's own words first, booked `build`, then the
      `cargo test`, booked `test`; the added call costs 0.044-0.047 s on a warm tree, measured 2026-11-20 (`cargo test --no-run --quiet`
      on `rust/gate/crates/rustc`, five runs in the clone's target directory after a build).
    - `test-no-counters` (`make counters-inert`): the same split, both calls with its features (every one but `counters`).
    - a build that named no binary: the binary key's `--no-run` build already wrote its `build` line and passed, so no build is asked
      again and the `cargo test` is booked `test` alone - it compiles nothing: no `Compiling` line, `Finished` in 0.03 s, measured
      2026-11-20 (`cargo test` without `--quiet` on `rust/gate/crates/rustc` straight after the binary key's `--message-format=json`
      build, its output grepped). A binary key's build that FAILED is asked again plain, booked `build`, and nothing runs after it,
      so the failure reads as cargo's words and not as JSON.
  - `cover-build`: `cover.rs`'s `build`, around its cargo call, one line a family's group (a failed group's crates asked again one
    at a time each write their own).
  - `cover-run`: `cover.rs`'s `run_one`, a crate's tests and report; a crate whose build failed ran nothing and writes none.
  - `lint` and `format`: one line a crate, in `answer`'s loop, never inside `check` (`check("cover")` runs `uncovered_each`, which
    writes its own).
  - none: a kept green result (it ran nothing), `dead` (reads source text, no cargo), `hamlet` (a stage run, the work budget's, not a
    check's compile or tests), `test-times` (`make test-times`'s repeated timing runs, its own report).

  The readers: every reader of the log outside `measure`'s `load_events` that reads a line's time skips the kinds no hook wrote
  (`BgEnd`, `Phase`) first - `reviews/glyph.rs`'s `first_event` (the feature's start: a `Phase` line written first would become it) and
  `reviews/checkpoint.rs`'s `events` (`idle` books the gaps between lines: a `Phase` line inside an idle stretch would split it), by
  one list in `reviews` beside `measure`'s `ASIDE`, which `reviews` cannot import (`measure` builds on `reviews`); and, by `ASIDE`
  itself, `measure`'s `stepback_bundle.rs`'s `sessions_of` (a `Phase` line's `sid`, the process's, would add a session to the
  step-back bundle, or rank one by a run's steps) and `tool_yield/records.rs`'s `tally_events` (it branched on `ev` before it used the
  time, so no such line was counted: a pin). Read and left alone: the arbiter's `flow_sections` and the guard's `read::reversals` (`PreToolUse` first), `speckit_todo`'s `active` (the files'
  modified times). Red first: a fixture crate's `rust test`, `rust cover`, `rust lint` and `rust format` runs in a scratch tree write
  `build`, `test`, `cover-build`, `cover-run`, `lint` and `format` lines whose spans nest inside the call's, and a kept result
  writes none; a fresh run's and a counting-free run's `cargo test` write a `build` line before their `test` line, and a build that named no
  binary writes one `build` line; a log opening on a `Phase` line starts the feature at its first event; a `Phase` line inside an idle stretch leaves it
  whole; a `Phase` line's `sid` adds no session to the step-back bundle.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the rust checks' phase lines | n/a - no map | n/a | none | n/a |

### T05 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a `make static` run's compile and test time are told apart.
2. **The constraints.** FR-003; D4; a kept green result writes no phase (it ran nothing); a reader of a line's time reads the hooks' events, never a `Phase` or `BgEnd` line.
3. **Where each comes from.** G: the GM's "how much time are we spending on recompiling things"; O: research R6 (family builds, side-by-side runs).
4. **Do they describe the world here?** The build and run sites read in `cover.rs`, `side.rs`, `kept.rs`'s `binary_key` and `answer`'s loop (read 2026-11-20); the run lock's `run_what` is the outermost `make`'s command line (`runlock.rs`, T23).
5. **The order.** After T04 (`append_row`, the split of `measure`'s reader).
6. **The exits.** Green: the fixture's phase lines and the four readers' cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture cases green; one real `make rust-test CRATE=rust/gate/crates/rustc` writes its phases in the clone's log (read off the log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new lines and two readers' filters, red first.

**Found and left?** none - the two `measure` readers first found here were fixed in T05 (the coordinator, 2026-11-20).

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T06 (FR-003: a landing's cheap pass, gate, claims round and push are one span - the spec's User Story 1)

- **Approach**: D5 in `rust/gate/crates/land` (not held), and the writer's feature in `rust/guard/src/guards/event_log_hooks.rs`
  and `event_log_hooks/filed.rs` (held: `make guard-edit` on each first). A new `land/phase.rs` writes each line through
  `append_row_for`, in T05's row
  form (`ev` `Phase`, `src` `land`, `step`, `t0`, `t1`, `t` its `t1`, `code`, `make`, `clone`), each carrying the first task landed as
  `task`; `land.rs` wraps each step, `long_runs.rs` the cohort. The steps TILE the
  landing, every part of it booked to one:
  - `cheap`: the first pass, every cheap refusal; code 2 when one refuses.
  - `gate`: the second pass whole - the delta's engine and counter-only reads, the green-gate stamp, the gates it names (`make done`,
    `make hooks-test`, `make page-check`) or a machinery delta's guard suites, a landing cohort run alone, the records and `pool/` maps
    they regenerated committed, the work-budget review.
  - `cohort`: `make cohort-landing`, beside the gate (from its start to its wait, or to its stop by a red gate, its code then minus the
    signal) or alone after a covered gate; NESTED in the `gate` line's span, never past it, so a reader books it inside the gate.
  - `claims`: the wait for the claims round and the ledger rows its passes owe; code 2 when the wait refuses.
  - `push`: the ticks, their commit, the one push carrying both, a failed push's revert.
  - `end`: from the arguments read to the landing's verdict, with `tasks` (the ids asked, split as `main` splits them, D16's commas
    T18's) and `landed`. THE PUSH IS THE LANDING (the plan review's T06-stop-after-push): the `end` is written the moment the push
    goes out (exit 0, or 3), `landed` true and its code the push's, so no later stop leaves a pushed landing reading unlanded; a
    landing that never pushed writes its `end` at its exit, `landed` false. A step that raises writes code 1, as the landing's raise
    exits; a step that did not run writes no line.
  - `after-push`: the push's tail, after the `end` - the fresh block's start and the work-budget view after an engine landing; a
    raise there is its own line's code, the `end` standing at the push's (the process still exits 1).
  - `main`'s own refusals (no `NOTE=`, no feature directory) are refused landings of the tasks they name and write an `end`; a usage
    refusal names no task and writes none.
  - `landed` is the push gone out - exit 0, or 3 (`MERGED`: other sessions' edits merged, the ticks standing) - so a landing whose
    push went out and whose tail raised, or that exited 3, is still a landing: its code alone would read it refused. D7's
    rework, D10's and D11's landing, T13's and T14's lines and the data model's Landing read `landed`, restated with this task.
  - THE LINE'S FEATURE: `append_row_for(root, feature, row)` beside `append_row` (T05's callers unchanged) files a line in the
    feature its word names - a `specs/` directory or the one `specs/<word>-*`, read first as a make command's `F=` is - before T26's
    chain asks a task's start; a blank word or one naming no feature leaves the chain as it was. The landing names `d`'s directory,
    `main`'s refusals the `F=` word, so a landing of a task never started in the clone is filed in its own feature's log, not
    feature.json's marked `fallback`, where T13 and T14 would not see its `end`.
  - `make` is the outermost `make`'s first goal, read from `/proc` as T05's lines read theirs (`land-batch` runs the same command),
    `land` with no `make` above.
  - A stopped landing (`make land-stop`, TERM) writes no line past its last finished step: the guard's handler exits at once, and a
    file write is no signal handler's work. Stopped before its push went out, it reads as no landing, never as refused; stopped in
    the push's tail, its `end` is already written, `landed` true. The one window left is a stop while `sync-with-main.sh done` runs,
    after the remote took the push but before the script exits: the landing cannot know the push went out until the script says
    so, and the push's own tick commit on main records it.

  Red first: the land tests' fake world writes `cheap`, `gate`, `claims`, `push`, `end` and `after-push` in order, each span
  inside the end's but the tail's, after it; a tail that raises after the push `end` at 0, `landed` true, before `after-push` at 1;
  a refused first pass `cheap` and `end` at code 2, a raising one at code 1; a red gate `gate` and `end` at code 1; a claims wait run out
  `claims` at 2; a failed push `push` at 1, `landed` false; a push that merged `end` at 3, `landed` true; a landing of `T1 T2` an `end`
  whose `tasks` is both ids (T13 and T14 read a landing from this line); `main`'s refusals an `end`; the cohort beside the gate, stopped
  by a red gate, and alone, each its own line; an unstarted task's lines, and `main`'s refused `end`, filed in the landed feature's
  log, not feature.json's; the writer's own case (`a_gate_tools_row_names_its_feature`: a feature named over the chain, a number
  naming its one directory, a word naming none or blank left to the chain) seen red first; the make target from a fake `/proc`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the landing's phase lines | n/a - no map | n/a | none | n/a |

### T06 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a landing's time is split by step - every step of it booked, the cohort inside the
   gate - and a refused landing is counted from its own `end` line.
2. **The constraints.** FR-003; D5; a failed, refused or raising landing still writes its `end`; the lines are T05's form, through
   the one writer (`append_row_for`); the held writer is edited under `make guard-edit`, its other callers unchanged.
3. **Where each comes from.** G: the approved "make land its phases' seconds"; O: `land.rs`'s and `long_runs.rs`'s pass order read
   2026-11-20; the push's exit 3 (`MERGED`) read in `tick_and_push`.
4. **Do they describe the world here?** The steps are `land.rs`'s own passes.
   The clean landing's fixture writes 5 lines, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/land`, its clean case).
   The crate's 74 tests run in 0.35 s with the lines written, measured 2026-11-20 (that run's `test result` line).
5. **The order.** After T04 (`append_row`); beside T05 (another crate); before T10, T13 and T14, which read the `end` line.
6. **The exits.** Green: the land tests, the crate's lint, format and coverage. Red: what failed recorded and the task set down, a
   claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fake-world cases green, seen red first.
   13 of 71 failed on the skeleton, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/land` before the writer).
   The writer's feature case failed before the writer read it, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, 1 of 627).
   The end-at-the-push cases failed first, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/land`, 2 of 74).
   This task's own landing writes its phases (read off the log after it).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new lines, red first.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-20 -->
### T24 (a gate test read the real environment: with `SPECIFY_FEATURE` exported, `make static`'s coverage of the bundle crate went red, observed 2026-11-20, method: T02's `make static` log)

- **Approach**: the guard's `consulted::context` gains `context_from(root, var)`, the same body with its environment handed in
  (`context` delegates to it with the guard's own `var`, so every other caller is unchanged). The bundle crate's `source_pages` asks
  `context_from(&here, &env)`, where `env` is the process's (`consulted::var`) in the binary and, under `cfg(test)`, a thread-local
  map of the crate's own (`helpers::VARS`), empty unless a test names a variable - the guard's own `VARS` seam is compiled out of a
  dependent crate's tests, so the bundle needs its own. The test at `helpers/tests.rs` asserts the one outcome it means (code 1 and
  the exact `AttributeError` on a `[1]` pointer), then names `SPECIFY_FEATURE` in its own map and asserts the pointer skipped (code 0),
  so the seam, not the shell, decides the branch.
  - red first, the assertion made exact and run with `SPECIFY_FEATURE` exported: 77 passed, 1 failed (`tests.rs:389`, left 0, right 1), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/bundle`, `/tmp/t24/red-exported.log`).
  - the same test, `SPECIFY_FEATURE` unset: 78 of 78 passed, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/bundle`, `/tmp/t24/red-unset.log`).
  - after the fix, exported, run first so no kept result stood in: 78 of 78 passed, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/bundle`, `/tmp/t24/green-exported.log`).
  - the guard's suite after `context_from`: 627 of 627 passed, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t24/guard-test.log`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the ledger context's environment | n/a - no map | n/a | none | n/a |

### T24 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the bundle crate's tests reach the same lines whatever the builder's shell exports,
   so `make static`'s coverage of it is the code's, never the session's environment.
2. **The constraints.** T24's line (the test given its own environment, asserting the one outcome it means, red first with
   `SPECIFY_FEATURE` exported; lands before T08); 100% line coverage of each crate by its own tests; no process-environment mutation
   in a test (it races the other tests on the thread pool).
3. **Where each comes from.** O: T02's `make static` red on the bundle crate's coverage, observed 2026-11-20, method: T02's
   `make static` log; O: the red-first run above, measured 2026-11-20 (`make rust-test`, exported); the task as filed (T24's line).
4. **Do they describe the world here?** Yes: `l7r_guard::shared::consulted::var` is `std::env::var` outside `cfg(test)`, and a gate
   crate's tests build the guard without it, read 2026-11-20 (`rust/guard/src/shared/consulted.rs`); the exported run reached code 0,
   the unset run code 1, measured 2026-11-20 (the two logs above).
5. **The order.** Before T08 (T03's plan review); independent of the land crate's work in this clone.
6. **The exits.** Green: the exact assertions green with `SPECIFY_FEATURE` exported, `make rust-test` on the bundle crate and the
   guard, `make quick`, `make static` (exported, once: the bundle crate's coverage clean), `make hooks-test`. Red: what failed recorded
   and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The sweep for tests that read a real variable and accept either outcome: `arbiter/tests.rs:579` (0 or 1;
   its ask names feature 999, resolved by `asked_feature` before either environment pointer), `gate/src/lib.rs:309` (`github-token`,
   the real repository's secrets), `record/tests.rs:301` (`money-conversions --check`, the real tree), `measure/spec/tests.rs:54`
   (`<= 1`), `owed/.../answer_modes.rs:149` - none reads `SPECIFY_FEATURE`, so none flips with it; named in the report, outside
   T24's edit scope. `bundle/.../modal.rs:866` reads `CHECK_ORDER_OK` raw, but its tests hand the escape to `bundle` directly:
   78 of 78 passed with it exported, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/bundle FRESH=1`, `/tmp/t24/probe-order-ok.log`).
8. **The budget.** One landing.
9. **Done, measured.** The exact test green with `SPECIFY_FEATURE` exported, 78 of 78, measured 2026-11-20
   (`make rust-test CRATE=rust/gate/crates/bundle`, `/tmp/t24/green-exported.log`), and `make static` exported with the bundle
   crate's coverage clean.
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a builder who exports `SPECIFY_FEATURE` no longer sees `make static` red on the bundle
    crate's coverage.

**Found and left?** none - the either-outcome tests the sweep found (item 7) read no variable this task's defect turns on, and
each passes or fails the same with `SPECIFY_FEATURE` exported or not; they are named in the report, not filed.

**Performance work?** no


<!-- plan-archive: T25 to T23 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T27 to T25 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T27 to T27 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

<!-- plan-archive: archived 2026-11-20 -->
### T28 (FR-013, the GM 2026-11-20: "can we in general priotitize performance improvements going forward?" - nothing ordered the work by it, observed 2026-11-20, method: `make task-start`'s source and the Stop hook's, read)

- **Approach**: one reader of performance work, in the set-down guard (`rust/guard/src/guards/set_down_hooks.rs`), which the task gate
  already builds on: `performance(id, title, plan)` - the `[perf]` tag among the bracketed tags right after a task's id (never a
  `[perf]` its prose quotes: T28's own line does), or `make task-add ... PERF=1`'s one mark, the `### T<n> Performance checklist`
  heading it writes into the task's plan section. The Stop hook's active test comes out of `verdict()` as `active()` - an open box but
  the GM's, not set down since the feature's last task-start, not closed by its status line - and `next_performance(root, git dir,
  prefer)` picks the open performance task to start next: of `prefer` first (counted active whatever was set down, since its start ends
  that), then of each other feature started in this clone, the latest start first. Both the Stop hook's "start the next" and `make
  task-start`'s refusal ask that one picker, so the hook never names a task the start refuses. `task_start.rs`'s `perf_first` reads
  `PERF_LATER_OK` first (a reason of two words, refused short; both recorded in the guard log under `perf-first`), then refuses a task
  that is not performance work naming the picked task and `make task-start F= T=` for it. The specs are read under the clone's
  toplevel, where `resolve_feature` found the feature, never `L7R_GATE_TREE`.
  - red first, the tests before the code: the guard's suite 4 failed of 631, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t28-guard-red-kept.log`); the task crate's 2 failed of 58, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/task`, `/tmp/t28-task-red-kept.log`).
  - green: the guard's 631 of 631 passed, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t28-guard-green.log`); the task crate's 59 of 59 with the task-add pin, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/task`, `/tmp/t28-task-green.log`).
  - each check deleted: the guard's 2 failed of 631 (the picker replaced by none), measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t28-guard-deleted.log`); the task crate's 2 failed of 59 (the refusal's return dropped), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/task`, `/tmp/t28-task-deleted.log`).
  - the Stop hook on this clone after the tags names T12 with its `make task-start F=451 T=T12`, at 36 to 38 ms a run past its first build, measured 2026-11-20 (`tests/hooks/set-down-hooks.sh stop` with `SET_DOWN_ROOT`, three runs, `/tmp/t28-stop.err`).
  - `make task-add` with a `[perf]` title writes `- [ ] T<n> [perf] ...` and the reader calls it performance work with no change to the tool, as it does PERF=1's checklist, measured 2026-11-20 (the task crate's `perf_1_and_a_perf_title_each_file_a_task_the_reader_calls_performance_work`, `/tmp/t28-task-green.log`).
- **The tags** (the list measured: every open box of `specs/*/tasks.md`, 248 in 24 features, of which 4 features are not closed by their status line - 417, 444, 449, 451 - measured 2026-11-20, method: `grep '^- [ ] T'` per tasks.md and each spec's `**Status**` line). Tagged, each a task whose stated outcome is less time: 451's T12-T21 (the six cheap fixes and the suite split, the GM 2026-11-20: "doing those first makes everything after them faster"), T28 and T29 (tagged when filed); 444's T34 (`make done` and `make land` without the map-rolling tests and the landing cohort), T36 (the gate's wall time against its goal of well under a minute, as 444's T36 line records it) and T43 (the crate split, a one-line edit's build time). Already performance work by PERF=1's checklist, untagged: 444's T27 and T30. Considered and left: 451's T07-T11 (they measure where the time goes; they cut none) and T22 and T24 (a close; a coverage fix); 444's T29, T32 and T33 (a stage drawn in Rust, the Python it replaced deleted, so no live time is cut), T24, T25, T28, T31 (budgets and placements), T35 (which tests the gate runs), T39 (the engine's deletion, its trees already gone) and T42 (the driver); 449's T158 (a deletion), T203, T216 and T241 (checks that pass the bad), T197, T228, T235 and T240 (record, constitution, budget and drawing); 417's open boxes, whose engine (`l7r/diagram/hamletgen/`) is deleted, so tagging them would hold every start for work that speeds nothing; and every open box of the 20 features closed by their status line (Done, Withdrawn or Superseded), which no start reaches.
- **"Performance work?", squared**: the question asks whether the task is performance work in FR-013's sense - yes for a `[perf]`
  task; `PERF=1` is the other mark of one and the one that adds docs/performance-checklist.md's questions, which measure an engine
  stage's counted operations and time. T12-T19 answered no in the checklist's sense; tagged, they are yes in FR-013's (found and left
  below: the lines themselves).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| performance work first | n/a - no map | n/a | none | n/a |

### T28 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a builder starting work in a clone is sent to the open performance task first, by
   `make task-start` and by the Stop hook alike, unless a recorded reason says why this task goes first.
2. **The constraints.** FR-013 (the reader, the refusal, its escape, the Stop hook's order, the active test shared), FR-012 (red
   first, the check deleted and red, a reason of two words recorded, the message naming the compliant command), SC-006, T28's line;
   100% line coverage of each crate by its own tests.
3. **Where each comes from.** G: the GM 2026-11-20, request.md ("can we in general priotitize performance improvements going
   forward?  I thought that was already a rule."); G: the order of the same day ("doing those first makes everything after them
   faster"); O: the reds and greens above, measured 2026-11-20 (`make rust-test`).
4. **Do they describe the world here?** PERF=1's only mark is the checklist heading, 6 headings across every plan.md, measured 2026-11-20 (`grep '^### T[0-9]* Performance checklist' specs/*/plan.md`); this clone's start log names 21 features, of which 451 and 417 are active (417 with 29 open boxes and none tagged), 444 and 449 set down since their last start, measured 2026-11-20 (`.git/task-starts.jsonl` and `.git/set-downs.jsonl` read against each tasks.md and status line).
5. **The order.** Right after T18 (the task line); with T29, which the same set-down tool carries.
6. **The exits.** Green: the reds above green, the checks deleted and red again, `make rust-test` on the guard and the task crate,
   `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Every reader that anchors on the text right after a task's id was searched before the tags went in: none
   reads it (the `phase:` key is an indented line of its own; `[lands-open]` ends a line), measured 2026-11-20 (`grep -F -- '- \['` over `rust/`).
8. **The budget.** One landing.
9. **Done, measured.** The Stop hook names an open performance task first on this clone, measured 2026-11-20 (`tests/hooks/set-down-hooks.sh stop`, `/tmp/t28-stop.err`), and `l7r-gate task-start 451 T07` over 451's own spec, tasks and plan refuses it naming `make task-start F=451 T=T12`, starts it under `PERF_LATER_OK`, and starts T12, both records listed by the guard log's reader, measured 2026-11-20 (a scratch repository, the gate's binary and `measure guard-log --guard perf-first`, `/tmp/t28-replay.H4wq/`).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a builder sees `make task-start` refuse a task that is not performance work, naming the
    performance task to start or `PERF_LATER_OK`.

**Found and left?** Each of (a) to (c) is fixed by the session before T28 lands, outside this builder's brief: (a) the root Makefile (held) lists
no `PERF_LATER_OK` in `FREE_TEXT`, so a `$` in its reason is expanded by make, and `task-start`'s help line does not name the escape -
the word added to `FREE_TEXT` and the escape named in the help (the tool records the escape itself, as `plan.rs` records
`PLAN_REVIEW_OK`, so no `$(LOGESCAPE)` line, which would record it twice - a departure from D15's and D16's make-side form); (b)
`rust/gate/crates/plan/src/plan/template.rs`'s "Performance work?" placeholder still reads yes as the checklist's - restated to "yes
for a `[perf]` task; `PERF=1` adds the checklist"; (c) T12-T19's sections answer "Performance work? no" - each one line flipped to
yes after T18 lands, through one `make plan-delta F=451` round, since changing T18's decided block now would hold its landing.

**Performance work?** yes - a `[perf]` task in FR-013's sense: it orders the work so the tasks that speed the rest land first. Not
filed with `PERF=1`: the checklist's questions measure an engine stage's counted operations and time, and a refusal's order has neither.

<!-- plan-archive: archived 2026-11-20 -->
### T30 (the shared shell readers' gaps)

- **Approach**: no change of its own: withdrawn, its fix folded into T15 by T15's plan review (2026-11-20), which ruled leaving the shared readers' defects NOT LEGITIMATE; T15 fixed strip_heredocs, strip_quotes and make::invoked, red first, and replayed the corpora through every guard.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| none of its own | n/a | none | none | none |

### T30 Approach (checklist part A)

1. **The goal, in the world.** The shared shell readers read every form T15 found.
2. **The constraints.** T15's plan review.
3. **Where each comes from.** R: T15's plan review.
4. **Do they describe the world here?** Yes: T15's shared tests failed before its fix (measured 2026-11-20 (T15's red-first run)).
5. **The order.** With T15.
6. **The exits.** Green: T15 ticked. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** No landing of its own beyond the tick.
9. **Done, measured.** T15 ticked with the fix.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** Nothing of its own: its fix landed in T15.

**Found and left?** none

**Performance work?** yes - a `[perf]` task (FR-013), folded into T15


<!-- plan-archive: archived 2026-11-20 -->
### T14 (FR-007: `make static` was the edit loop - the spec's User Story 3)

- **Approach**: D11, a new guard `static_runs_hooks` (PreToolUse Bash, registered before `shell_check_hooks`). Held:
  `rust/guard/src/guards/static_runs_hooks.rs` (new) and its `tests.rs`, `rust/guard/src/guards.rs`, `rust/guard/src/lib.rs`, and two
  edits to the event log's writer, `event_log_hooks.rs` (`filed_at`: where a payload's line is filed - clone, feature, log, task - by
  the writer's own chain, nothing written) and `event_log_hooks/fields.rs` (`makes`, below) (`make guard-edit` on each first); the link
  `tests/hooks/static-runs-hooks.sh` and its suite `tests/hooks/test-static-runs-hooks.sh`.
  - **The count, as built.** The call's feature and task are `filed_at`'s - the chain that files the call's own line - so the main
    session's lines (a `fallback` line among them) and its builders' share one count by task, keyed on (feature, task) by reading only
    that feature's log through `event_log_hooks::read::read_jsonl`. A RUN is a `PreToolUse` line of the task whose `make` is `static` or
    whose `makes` holds it, and whose call RAN - a `PostToolUse` or `PostToolUseFailure` line carries its `id`. Deliberate deviation from
    D11's "PreToolUse lines": a call another guard refused (`make static &`, refused by `no_poll_hooks`) leaves a `PreToolUse` line and
    no other and ran nothing, and counting it would spend a run; 1 of 33 such lines in 451's log and 8 of 340 in 449's, measured
    2026-11-20 (the logs' `make: static` `PreToolUse` lines with no line of their `id`, `jq`), and a call known refused - this builder's
    own `sed -i` refused by `guard_file_hooks`, 2026-11-20T14:35:13Z - left its `PreToolUse` line and no line after it in any feature's
    log, measured 2026-11-20 (every `.git/l7r-events/*.jsonl` searched for its `id`). The cost: a foreground run still in flight
    in another session of the same task is not yet counted. The call being judged is never counted: in the whole chain
    `event_log_hooks` writes its line first, and its `id` is set aside (and has no result line yet).
  - **Since.** The task's last landing that went out - an `end` line whose `landed` is true and whose `tasks` (not `task`, which is its
    first id) names it, whatever its `code` - strictly after; else its FIRST `task-starts.jsonl` entry for the feature, from that second
    on (a start's `utc` is to the second, a line's `t` to the millisecond: a second's stamp is compared as `.000Z`); else every line.
  - **A compound command** (writer fix, found here): a line's `make` is its call's first target alone, so `make rust-test CRATE=x &&
    make static` logged no `static` while D11's trigger (`invoked` holds `static`) fires on it; the writer now adds `makes`, every
    target, where a call runs more than one, and the count reads both.
  - **The refusal** names, per crate the delta changes (`git diff --name-only` of `origin/main`'s merge base plus `git ls-files --others
    --exclude-standard`, each `rust/` path mapped to the nearest `Cargo.toml` holding `[package]`): `make rust-test CRATE=<c>` and
    `scripts/gates/l7r-gate.sh rust lint --crate <c>`, `rust format --check --crate <c>`, `rust cover --crate <c>` (only `rust-test`
    takes `CRATE=` in the Makefile); with no crate in the delta, `make quick`. Then `make static` once before `make land`, and
    `STATIC_OK="<reason>"` (recorded `escaped`/`static-ok`; a bare token refused). Each named command passes the guards that read a Bash
    command (`gate`, `measure`, `no-poll`, `make-only`, `shell-check`), pinned by a test. A call whose line carries no task passes,
    written to the guard log as `passed`/`no-task` (D10's precedent).
  - **Red first**, each case in the unit tests and the suite: two runs of T06 after its start refuse a third, naming the crates' checks;
    a landing with `landed` true resets it at exit 0, at exit 3 and as the second of a batch's `tasks`; a refused landing (`landed`
    false, exit 1 and exit 0) and another task's landing reset nothing; a run before the first start is not counted; two runs, a second
    T06 start, a third: refused; another task's run, another target's, a refused call and the call's own id are not counted, a
    `makes` run and a failed run are; `STATIC_OK` with a reason passes and is recorded; a mention passes; the main session's call and
    the builder's (its meta file's brief) share the count; the event log's `append` writing the call's own line and then this guard's
    answer, both handed no process environment (an exported `L7R_FEATURE_DIRECTORY` would refile them), the call's own line is no run.
  - **Left to the landing** (outside this builder's brief, which named the guard, its registration, tests and suite and this section):
    the `docs/guards.md` row and the `STATIC_RUNS_A_TASK` knob in its knob table (D14), and the `rust/guard/CLAUDE.md` mention - T14's
    own, owed before it is ticked.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the count | n/a - no map | n/a | none | n/a |

### T14 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the crate-scoped checks are the edit loop, `make static` the check before landing.
2. **The constraints.** FR-007, FR-012; D2 (the task field), D11.
3. **Where each comes from.** G: the approved "a crate-scoped check while iterating, with make static once at the end"; O: research R6.
4. **Do they describe the world here?** R6 timed the log read the guard makes. On 451's log (1,297,362 bytes, 5,372 lines) a `make
   static` call takes the guard about 0.06 s and any other Bash call about 0.011 s, measured 2026-11-20 (`l7r-guard.sh --only
   static-runs-hooks PreToolUse` on a `make static` and a `make quick` payload in this clone, `$EPOCHREALTIME` around each, the warm
   runs). Replayed on the same log, 6 of its 22 `make static` calls carrying a task would have been refused - T03's third and fourth,
   T25's third and fourth, T06's third, T18's third - measured 2026-11-20 (a Python mirror of the guard's `runs()`, applied to each such
   call over the log's earlier lines and the clone's `task-starts.jsonl`).
5. **The order.** In lane A after T18 and T28 (the GM 2026-11-20 order, FR-013); it needs no other refusal, only T03's `task` on each line and T06's landing `end` line naming its tasks.
6. **The exits.** Green: the cases above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** With the refusal's condition switched off (`runs < usize::MAX`), 8 of the 11 new count tests failed (the other
   three: the time compare, the crates of a delta, and a mention or no task, which pass with it off) and the suite 9 of 17 checks, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `tests/hooks/test-static-runs-hooks.sh`); with the
   writer's `makes` switched off, its test failed, 1 of 656, measured 2026-11-20 (`make rust-test CRATE=rust/guard`). Green after:
   656 of 656 and 17 of 17, measured 2026-11-20 (the same runs); the crate's lint and line coverage clean, measured 2026-11-20
   (`l7r-gate.sh rust lint --crate rust/guard` and `rust cover --crate rust/guard`, `L7R_RUST_FRESH=1`).
10. **Before moving a constant.** n/a - a new knob, labeled GUESS.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?**
- T14's own, written before its tick (the session wrote them, 2026-11-20): the `docs/guards.md` row, the `STATIC_RUNS_A_TASK` row of its knob
  table (D14), the `rust/guard/CLAUDE.md` mention, and D11's text restated to what is built (a run is a call that ran; `makes`) with
  the event log's field list in `data-model.md`.
- The guard crate's tests read the process's environment: with `L7R_FEATURE_DIRECTORY` exported (a page session exports it), 17 to
  20 tests of other guards fail (`checks_hooks`, `check_bundle_hooks`, `pair_hooks`, `review_round_hooks`, `shared::checks::arbiter`,
  `no_poll_hooks`), measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1` with it exported; with `L7R_EVENTS_DIR` alone, green).
  Not fixed here: it is in six other guards' tests, outside T14's files. How every instance was found: the crate's whole test run under
  the export. Filed as T32; lands before T22 (SC-005 is measured on work that runs these tests).
- `guard_file_hooks` refused this builder's `sed -i` on a guard file but let a Python heredoc write the same files (each under a
  `make guard-edit` permit, so no edit went unpermitted). Not fixed here: `guard_file_hooks` is outside T14's files. Filed as T33; lands
  before T22.
- No make target formats one file: `make format` formats every crate, which would have rewritten T16's files in flight, so the new test
  file was formatted with the toolchain's `rustfmt` alone. Not fixed here (a Makefile change, outside T14's files). Filed as T34; lands
  before T22.

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: archived 2026-11-20 -->
### T16 (FR-008: the main session's waits checked every 420 to 600 s, observed 2026-11-19, method: the wait commands of the main session's transcript - the spec's User Story 4, research R5)

- **Approach**: D13 in `no_poll_hooks`. Held: `rust/guard/src/guards/no_poll_hooks.rs` (`make guard-edit` first). Red first: R5's
  observed POLL_OK loop with `sleep 60` then `sleep 420`, from the main session, refused naming the knob's form; the same loop at
  `sleep 60` throughout passes; the same slow loop from a subagent (`agent_id` set) passes; a file-watching wait from the main
  session sleeping past the knob refused; `SLOW_POLL_OK="..."` passes and is recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the slow wait | n/a - no map | n/a | none | n/a |

### T16 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the main session learns of an idle agent within a minute.
2. **The constraints.** FR-008, FR-012; D13; the existing no-poll cases unchanged.
3. **Where each comes from.** G: the approved "a shorter poll loop on my side", made a refusal by the GM's "real enforcement"; O: research R5.
4. **Do they describe the world here?** R5's loops are the session's own.
5. **The order.** After T15 (the same file).
6. **The exits.** Green: the five cases, grown in the unit tests to 12 firing loops each judged foreground and backgrounded (24 refused: R5's loop, a POLL_OK file test, a `while sleep 480` head, the file wait at `480`, `8m`, `60.5`, `1m 30s`, `2h`, `1d`, a second sleep of `90s`, a nested loop's `120`, a `/bin/sleep 300`), 7 quiet loops each both ways (14 passing: the 60 s loops, `1m`, `0.5`, a quoted `"sleep 480"`, a POLL_OK sleep with no loop, a sleep after the loop's `done`), a subagent's slow loops both ways answered as before T16 (4), and a loop inside `bash -c "..."` refused - measured 2026-11-20 (the case arrays of `no_poll_hooks/tests.rs`, counted). The plan reviews' notes: 12 more firing loops each both ways (24 refused: 6 whose `sleep` takes a variable the command sets past the knob - `N=480;`, `export N=8m;`, `"$N"`, a later `N=480` over `N=30`, `N=480 bash -c '...'`, `N="480"` - and 6 whose length is still unreadable - `$N` set nowhere, `$WAIT`, `$N` beside an unrelated `M=480`, `"$((N * 2))"`, `$(cat /tmp/n)`, `infinity`), 2 quiet both ways (`N=30`, `N=5` quoted), a subagent's `until curl -s x; do sleep $N; done` refused as a busy-wait, and 4 thin `SLOW_POLL_OK` reasons (empty, one word quoted or bare, one word after the colon) refused for their reason - measured 2026-11-20 (the case arrays of `no_poll_hooks/tests.rs`, counted); the no-poll suite 136 of 136, 12 of them T16's - measured 2026-11-20 (`tests/hooks/test-no-poll-hooks.sh`, one logged run). The R5 fixture is the main session's own wait, verbatim (its `sleep 60`, then `sleep 420`), and every main-session Bash call of the transcripts with `POLL_OK` and a `sleep` of 300 or more, replayed through the built guard with its own backgrounding: 47 commands, the 45 waits among them all refused naming the 60 s form, the 2 others heredocs writing a test file and passing, after the unreadable length was refused as before it - measured 2026-11-20 (a Python reader over `~/.claude/projects/-diagram*/*.jsonl`, no sidechain, each command piped through `tests/hooks/no-poll-hooks.sh pretool`, HEAD's guard beside it). Every verdict of the four corpora, HEAD's guard against T16's, foreground, from the main session: 0 of 1,134 moved - measured 2026-11-20 (the same reader over `tests/hooks/fixtures/*.json`, both binaries). The four frozen corpora through the pace check: 1,134 commands, each judged foreground and backgrounded from the main session, 0 refused; a raw grep finds 3 with a loop word and a `sleep` over 60, each a heredoc's payload - measured 2026-11-20 (`the_frozen_corpora_through_the_pace_check`, and a Python grep over `tests/hooks/fixtures/*.json`, read by hand). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Red first: before the check, 24 of 24 firing judgments unrefused, and the escape test red because a lone `SLOW_POLL_OK` read as a reasoned `POLL_OK` (the escape reader matches a token anywhere, so the longer token held the shorter) - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, one logged run). The check deleted (`slow_poll` returning None): 24 of 24 firing judgments red, with the escape and the self-trip tests - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, one logged run); the suite's 6 firing and escape cases red on a binary without the check - measured 2026-11-20 (`tests/hooks/test-no-poll-hooks.sh`, one logged run). The build: `slow_poll` in `no_poll_hooks/pace.rs`, the pace check split out of `no_poll_hooks.rs` when it passed the 1,000-line bar (constitution X clause 13), called first in the POLL_OK-escaped branch (ahead of the bracketing and the ceiling) and before `file_wait`; a payload with an `agent_id` passes untouched. The pace is the longest `sleep` at a command position inside a loop, from its keyword to its matching `done`, the head counted (a `while sleep` loop), the units `s`, `m`, `h`, `d` read and several numbers summed, as GNU `sleep` reads them; a `sleep` given a variable the command sets (`N=480`, `export`, quoted, an env prefix) is read at the largest value it is set to, and any length still unreadable after that (a variable set nowhere, an arithmetic, a substitution, `infinity`) is refused as endless, naming the literal `sleep 60` form - the plan-blocks review's ruling, as D12 refuses an unreadable `wait $P`; a redirection after a `sleep` is no length; a `-c` string a shell runs is read too, since the sanitized form blanks it while the ceiling reaches it. The refusal names the command with every `sleep` over the knob at `sleep 60`; `SLOW_POLL_OK` is masked before `POLL_OK` is asked for, so a lone `SLOW_POLL_OK` grants nothing `POLL_OK` grants. Red first for the reviews' notes: the 6 set-variable loops and the 6 unreadable ones, 24 judgments, unrefused before the reader worked them out - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, two logged runs); the thin `SLOW_POLL_OK` reasons are a plain pin, the shared escape reader refusing each before the change - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, one logged run). Found on the way and fixed: a loop whose `sleep` takes a variable never reached the loop branch, since `SLEEP_RE` and `sleep_in_loop` ask for a digit, so `until curl -s x; do sleep $N; done` passed even the busy-wait refusal; HEAD's guard lets it through - observed 2026-11-20, method: the command piped through the mirror's `tests/hooks/no-poll-hooks.sh pretool`, rc 0; the branch is now entered where the pace reader finds a `sleep` in a loop. Self-trip: the guard's rewrites (the file wait's proof and ceiling, the POLL_OK ceiling, the bracketed pattern, the scoped make wait) and each form at the knob it offers, fed back from the main session, are never refused for their pace; the offers and the POLL_OK rewrites are refused for nothing - measured 2026-11-20 (`the_guards_own_rewrites_and_offer_pass_its_pace_check`). The ceiling adds `-ge 5400` and no `sleep`, so it cannot raise the pace.
10. **Before moving a constant.** n/a - a new knob, `POLL_CHECK_S` 60 s, labeled GUESS at its point of change.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The guard refused its own file-wait rewrite when run again (as its ceiling's "wait again if it is still working" invites), as a busy-wait: `shared::wait`'s condition grammar did not read the proof-of-life clause `proof_of_life` adds, so the wait stopped being a file watch. It was not caused by T16: HEAD's guard refused the same command at `sleep 5` - observed 2026-11-20, method: the rewrite piped through the mirror's `tests/hooks/no-poll-hooks.sh pretool`. The fix: the grammar drops the guard's own clause (plain, and fitted inside double quotes) as it drops the ceiling's, and `proof_of_life` reads the condition as given, so it adds no second clause. Red first: 3 tests red before the fix (the guard's rewrite fed back, the file wait's own test now asking for no answer at all, and `wait`'s unit test over the until, while and quoted forms), green after - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, two logged runs). The file wait's test had hidden it, since `rewritten()` reads a refusal as no rewrite; it now asks that the fed-back wait get no answer, and the suite replays the rewrite through `untouched`.

**Found and left?**
- `POLL_CHECK_S` goes into D14's knob table with T22, which lands before the close (T22 is the close).

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: archived 2026-11-20 -->
### T12 (FR-006: builders past a large context slowed the window's critical path - the spec's User Story 2, research R3)

- **Approach**: D8 and D9, a new guard `context_cap_hooks`, PreToolUse `*`, in `guards()` after `event_log_hooks` (`protocol::run`
  calls every guard whatever another answers, so a refused call's line is written either way). Held: `rust/guard/src/guards/context_cap_hooks.rs` (new), `rust/guard/src/guards.rs`, `rust/guard/src/lib.rs`
  (`make guard-edit` on each first); its unit tests `context_cap_hooks/tests.rs`, its fixture `context_cap_hooks/payloads.json`, its
  link `tests/hooks/context-cap-hooks.sh` -> `guard-shim.sh` and its suite `tests/hooks/test-context-cap-hooks.sh`.
  - THE FIRST STEP, done another way: settings run the mirror's `/diagram/scripts/hooks/l7r-guard.sh`, so a dump in the clone sees no
    live call. The capture is from Claude Code itself: measured 2026-11-20 (Claude Code 2.1.325, `claude -p` from a scratch directory, a PreToolUse hook writing its stdin to a file; the main session dispatching a general-purpose builder, then a defined agent of the scratch directory's `.claude/agents/`, each one Bash call).
    Pinned as `payloads.json`. A builder's call carries `agent_id` and `agent_type` `general-purpose`, and a defined agent's its
    own name (`probe-check`). The main session's carries neither key. `transcript_path` is the session's, and
    `<it without .jsonl>/subagents/agent-<agent_id>.jsonl` exists beside it (same capture).
  - WHO (D8): no `agent_id` passes, before any read. An `agent_type` naming the clone's `.claude/agents/<type>.md` passes on a stat.
    So does an `agent_id` that is not a plain name (letters, digits, `-`, `_`), since it cannot be joined into a path.
  - THE CONTEXT (D9): the own transcript read backwards in 64 KiB steps (GUESS), at most 16 MiB (GUESS: the window's largest builder
    transcript, 50 MB, scanned whole in 0.07 s, measured 2026-11-20 (`time` on a Python line scan of it, research R2)), to the last `type: assistant` row whose
    `message.usage` sums above zero (`input_tokens + cache_read_input_tokens + cache_creation_input_tokens`).
    - Only an `assistant` row counts: in the same capture, 2 `user` rows holding Agent results carried the child's `usage`, measured 2026-11-20 (`jq` over the probe's two transcripts, rows not `assistant` holding `usage`).
    - A row of zero is a synthetic message, not a model call.
    - Nothing read (no file, no such row in the tail) passes.
  - Past `CONTEXT_CAP_TOKENS` (GUESS, 300,000; at the cap passes), every tool call is refused but a Write, Edit or Read of
    `<git common dir>/l7r-handoffs/<task>-<agent id>.md`, or `<agent id>.md` where the call's line carries no task. The task is
    the event log's own chain (`filed_at`). Any file there whose name ends `<agent id>.md` is the agent's, so the named file and the
    Write agree even if the chain's task moves between them, and no two builders share one. The Read lets a written handoff be
    overwritten (the Write tool refuses a file it has not read). The refusal names the file and the next step: write what is done
    and left, stop, reply with the path, and the main session dispatches a fresh builder with it.
  - A call outside any clone passes.
  - A Write there from a background builder passed the live chain, observed 2026-11-20, method: this task's builder writing `.git/l7r-handoffs/probe-<its id>.md` in its clone, then removing it.
  - THE ESCAPE: `CONTEXT_OK="<reason>"` in a Bash command, recorded (`context-ok`); a bare one refused. D9's `make context-ok`
    permit is NOT built (see Found and left).
  - Red first, measured 2026-11-20 (`make rust-test CRATE=rust/guard` and the suite against a stub `judge` returning None): 4 of the guard's 7 unit tests failed, and 8 of the suite's 14 cases.
    Green: 666 of 666 and 16 of 16, measured 2026-11-20 (the same two runs with the real `judge`, after the coverage cases and the
    task-named handoff's whole-chain case).
    With the check deleted, 9 of 15 suite cases were red, measured 2026-11-20 (the suite with `tokens <= cap || true`).
  - The cases: a builder past the cap refused (Bash, Edit, Grep) naming its handoff; its handoff's Write, Edit and Read passing;
    another agent's handoff refused; a builder under or at the cap passing; the main session passing; a defined agent past it passing;
    `CONTEXT_OK` passing and recorded, and a bare one refused. The handoff's Write runs through the WHOLE chain and passes, while the
    chain refuses any other Write past the cap.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the cap | n/a - no map | n/a | none | n/a |

### T12 Approach (checklist part A)

1. **The goal, in the world.** No map changes; no builder works on with a context past the cap.
2. **The constraints.** FR-006, FR-012; D8, D9; constitution XVIII (fires and stays quiet, escape first).
3. **Where each comes from.** G: the approved "a fresh builder per stage, with a handoff file"; R: none; O: research R2, R3; the cap a GUESS knob (spec FR-006).
4. **Do they describe the world here?** R3 counted which agents pass the cap by type.
5. **The order.** In the performance lane (the GM 2026-11-20, FR-013), after T15 and T16 in lane B and before T13; it needs nothing T07-T11 make (D9 reads the builder's transcript itself).
6. **The exits.** Green: the five cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases, 16 of 16, and the unit tests; the check deleted, the 9 firing cases red (the Approach's figures).
10. **Before moving a constant.** n/a - a new knob, labeled GUESS.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - a new refusal.

**Found and left?**
- T12's own, written before its tick by the session (T14's precedent): the `docs/guards.md` row and the `CONTEXT_CAP_TOKENS` row of its
  knob table (D14), the `rust/guard/CLAUDE.md` mention, and D9 restated to what is built. That means the handoff's name
  `<task>-<agent id>.md`, its Edit and Read let through, and no permit. The builder's brief held it to the guard's files and this section.
- D9's second escape, the `make context-ok AID= WHY=` per-agent permit, is not built: a builder resumed past the cap under D10's
  escape meets this cap on its next call. Not fixed here: it needs a root `Makefile` target and `guard_file_hooks::cli`'s `grantable`
  widened, outside this task's files, and it serves D10's resume (the session's ruling, 2026-11-20). Filed as T13; lands before T22.
  Until then `CONTEXT_OK` in a Bash call is the recorded escape (FR-012).

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: archived 2026-11-20 -->
### T17 (FR-009: two of the window's first-round plan-review blocks were deferrals with no order - the spec's User Story 5)

- **Approach**: D15 in `rust/gate/crates/plan`, not held: the rule in `plan/lint/deferral.rs` (its kinds and words in `lint.rs`), the
  escape in `plan/defer.rs`, threaded through `plan.rs`'s `decide` and `plan_delta`; the template's placeholder states the form
  (`plan/template.rs`). The Makefile is not touched: `DEFER_FORM_OK` set on `make decide` or `make plan-delta` reaches the binary's
  environment (make exports a command-line variable to its recipes), and the tool reads it and records it itself, in the guard log
  (rule `defer-form-ok`, detail `<feature> <task>: <reason>`) and `dev/bypass-log/` - T28's form for `PERF_LATER_OK`, a departure
  from D15's `$(LOGESCAPE)` line, which would record it twice. It is recorded only on a run that passes: `make decide` once the section
  is decided (a refused run is not "decided under the escape"), `make plan-delta` only where it excused a finding. `make decide F=451
  T=T17 DEFER_FORM_OK=x` through make refused for its thin reason, observed 2026-11-20, method: the logged run, `/tmp/t17/decide-thin.log`.
- **The rule.** The answer is read from `**Found and left?**` to the next bold line, heading, comment or rule; each `- ` item is one
  item, and an answer with no list is one item. An answer opening with `none` (the template's `<none - ...>` among them) passes. An item
  passes when it says it is fixed in the task (`fixed here`, `fixed in this task`, `before its tick`, `before T<own> lands`; never `not
  fixed here`) or no defect (`not a defect`, `no wrong outcome`, constitution XIV) - unless it names an id it is filed as or lands
  before, when it is judged as the deferral it holds. A deferral owes `Not fixed here` with a colon, dash, parenthesis or "because" and
  two words of reason; `filed as T<n>` (or `added to`, `folded into`); `lands before T<m>` (a list `T07, T08 and T14` read whole);
  no order id equal to a filed id; and each id a box of `tasks.md` or `tasks-done.md` - the timeless half, which `make plan-delta` runs
  on a changed block. `make decide` alone adds the OPEN test: each id an unticked box of `tasks.md` now. A found-and-left item or an
  item 12 naming a class (`every` or `all the` before writer, reader, form, file, caller, instance, copy, site or guard; `each of the`)
  owes `observed <date>, method: ...` or a `measured <date> (<method>)` label. Every finding joins T25's one report, placed by its
  plan.md line, with the form to write in its rule's words.
- **The escape on the plan-delta path.** `make plan-delta` reads the guard log only for a changed block with a deferral finding, and
  then once a run: the live log held 90,507 files, read in 0.31 s warm and about 11 s cold, measured 2026-11-20 (`find | xargs grep -l`
  over `~/.claude/guard-log`, and a cold `xargs cat`), so a run whose blocks are formed never reads it. A file is parsed only when its
  text holds the rule's name.
- **Red first**: 10 of 148 tests red before the rule was written, its functions returning nothing, measured 2026-11-20 (`make
  rust-test CRATE=rust/gate/crates/plan`, `/tmp/t17/red-first.log`); each refused form and each passing form is a case - no task id, no
  reason, no order, all three missing, T16's real answer, a task id filed nowhere (`T999`), an order id filed nowhere (`T998`), "T123
  lands before T123", a filed id or an order id ticked or in `tasks-done.md` (refused at `make decide`, passed by the timeless half), a
  bare `Not fixed here.`, one bad item among good ones placed by its own span; passing: `none`, the old and new placeholders, the whole
  template, a formed deferral (a reason, `T123`, "lands before T124" and a list), `fixed here`, `before its tick`, `before T17 lands`,
  `not a defect`, `no wrong outcome`, T14's real answer; the class fix with and without its line, in an item and in item 12; through
  the command line, `make decide` passing the formed section and refusing five unformed ones with their plan.md line, the decided
  section passing `make plan-delta` once T124 is ticked, an id filed nowhere refused by `make plan-delta`, a section decided under
  `DEFER_FORM_OK` passing `make plan-delta` after its block changed while the same block undecided is refused, `DEFER_FORM_OK` on `make
  plan-delta` passing and recorded, a thin reason refused on both verbs, the escape leaving the section's other findings, and an
  archived section never judged.
- **Green, and the check deleted**: 151 of 151, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`,
  `/tmp/t17/green4.log`), the crate's line coverage, dead code and format clean, measured 2026-11-20 (`l7r-gate.sh rust cover|dead
  --crate rust/gate/crates/plan`, rustfmt's check). The rule's three functions returning nothing again: 10 tests red, measured
  2026-11-20 (the same, `/tmp/t17/deleted.log`). The escape's two effects removed: 2 tests red, measured 2026-11-20 (the same,
  `/tmp/t17/escape-deleted.log`). The escape recorded before the refusal: 1 test red, measured 2026-11-20 (the same, `/tmp/t17/record-early.log`).
- **The replay** over every task section of every `specs/*/plan.md` and `plan-done.md` (T25's method, a throwaway test calling the
  rule's three functions on each section with its feature's boxes, then deleted): 959 sections, 28 refused with 50 findings, every one
  a ticked section of a `plan-done.md` (24 of 449, 4 of 451) and none of any `plan.md`, measured 2026-11-20 (`/tmp/t17/replay.tsv`). The
  timeless half alone refuses the same 28, measured 2026-11-20 (the same dump: the open test's findings fall only in sections already refused).
- **History.** `make decide` reads the task's section of `plan.md` and `make plan-delta` only the changed blocks of `plan.md`; neither
  reads `plan-done.md`, and the tick and the landing call neither (D15), so an archived section's old form never holds a landing - pinned
  by `an_archived_section_is_never_judged`. A section still in `plan.md` whose deferral's task has since landed is not refused when its
  block changes, since `make plan-delta` asks only that its ids are filed.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the deferral's form | n/a - no map | n/a | none | n/a |

### T17 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a deferral is fixed in the task by default, and a class fix is complete up front.
2. **The constraints.** FR-009, FR-012; D15; constitution XIV.
3. **Where each comes from.** G: the approved "briefs that default to fixing in the task, and that ask for full coverage up front"; O: research R9.
4. **Do they describe the world here?** Yes: no section of any `plan.md` is refused by the rule, and the refused sections are archived ones, measured 2026-11-20 (the throwaway replay, `/tmp/t17/replay.tsv`).
5. **The order.** After T16.
6. **The exits.** Green: the plan crate's cases and the replay. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The plan crate green, the check deleted, the escape removed and the early record each red, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, four logged runs).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - a new refusal; no section of a live plan is refused by it.

**Found and left?**
- The root Makefile (held) names `DEFER_FORM_OK` nowhere: it is not in `FREE_TEXT`, so a `$` in its reason is expanded by make, and
  neither `decide`'s nor `plan-delta`'s help line names the escape. Fixed by the session before T17 lands (outside this builder's
  brief), as T28's `PERF_LATER_OK` was: the word added to `FREE_TEXT` and the escape named in both help lines.
- D15's text, `docs/guards.md` and `rust/gate/CLAUDE.md` do not say what is built: D15 names a `$(LOGESCAPE)` line and neither the pass
  forms (`fixed here`, `not a defect`) nor `added to` and `folded into`; `docs/guards.md` has a row for `PLAN_REVIEW_OK` and none for
  this refusal or `DEFER_FORM_OK`; the `plan` row of `rust/gate/CLAUDE.md` names neither `plan/defer.rs` nor `plan/lint/deferral.rs`.
  Fixed by the session before T17 lands (outside this builder's brief): D15 restated to this section, the guards row, and the index.

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: archived 2026-11-20 -->
### T13 (FR-006: a SendMessage resuming a builder past the cap, or one whose task has landed)

- **Approach**: D10 in `context_cap_hooks`. Held: `rust/guard/src/guards/context_cap_hooks.rs` (`make guard-edit` first). Red first:
  a SendMessage to a builder fixture past the cap refused; to one whose task is ticked refused; to one whose meta `description` names
  NO `T<n>` (its task found through D2's chain, the `task-starts.jsonl` entry in force at its dispatch) and whose task landed after its
  dispatch refused, while a later `task-starts.jsonl` entry for another, open task stands in the log and the builder's later lines
  carry that open task (its first line's task is the one read); to one whose task landed in a background `make land` (its `end` line
  after the land call returned) refused; to one whose task's only landing
  after its dispatch was refused (`end` `landed` false) passes; to one under the cap with no task found anywhere passes and writes its `no task`
  record; to one past the cap with no task found refused (the cap check needs no task); to a
  defined agent passes; to a builder under the cap with its task open passes; `CONTEXT_OK` in the summary passes and is recorded.
  And D9's permit (T12's found-and-left): `make context-ok AID= WHY=`, and the end-to-end resume - escaped, the permit granted, the
  builder's next call past the cap passing.
- **Built** (2026-11-20). `judge` runs the sender's own cap first (a builder past its cap is refused its SendMessage like any call),
  then `resume()` on a SendMessage: `to` a plain id; its meta `agent-<to>.meta.json` beside its own transcript (none: pass); a defined
  `agentType` passes; the cap from its own transcript; its feature and log from `filed_at` on a payload built as the agent's own (its
  task never read from that, whose last rung is the latest start); its task by D2's chain (the brief's `T<n>`, its FIRST line by `by`
  or `aid`, the start in force at its dispatch); its dispatch the Agent line whose `id` is the meta's `toolUseId`, else its first
  line, else its transcript's first `timestamp`; landed = an `end` line, `landed` true, naming it, after the dispatch, or ticked in
  `tasks.md`/`tasks-done.md`. Rules logged: `resume-past-cap`, `resume-landed`, `resume-no-task`, `resume-no-meta`, `context-ok`, `context-ok-permit`.
  The permit: the Makefile keys it `$(git rev-parse --show-toplevel)/context-cap:<AID>` (a bare `context-cap:<AID>` would put
  `git -C .` at `/` and find no store), `grantable` takes a `/context-cap:<plain id>` key, and the hook reads it past the cap after
  the handoff check (`permit_reason`, an hour). Facts it rests on:
  - a SendMessage's input is `{to, summary, message}`, `to` the agent id - measured 2026-11-20 (the session transcript's SendMessage tool_use rows);
  - the main session's SendMessage is filed in the clone's own log, so its payload's `cwd` is the clone - measured 2026-11-20 (grep of the clone's 451 log for `"tool":"SendMessage"`);
  - the meta file is `<session transcript without .jsonl>/subagents/agent-<id>.meta.json` = `{agentType, isBuiltIn, description, toolUseId}` - measured 2026-11-20 (the c6fd72d1 session's meta files read);
  - the Agent call's PreToolUse line carries `id` == the meta's `toolUseId`, its PostToolUse and SubagentStart `aid`, the builder's own lines `by` - measured 2026-11-20 (grep of the 451 log for a toolUseId and its agent id).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the resume | n/a - no map | n/a | none | n/a |
| the permit | n/a - no map | n/a | none | n/a |

### T13 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a builder serves one task and stays small.
2. **The constraints.** FR-006, FR-012; D10.
3. **Where each comes from.** G: the approved "one task a builder"; O: research R2 (`to` is the agent id).
4. **Do they describe the world here?** R2 read the window's SendMessage inputs.
5. **The order.** After T12, and after T03 (the `task` on each line) and T06 (the landing's `end` line naming its tasks).
6. **The exits.** Green: the ten cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases; the check deleted, the firing cases red. Red first: 6 new unit tests failing on stubs
   - measured 2026-11-20 (`make rust-test CRATE=rust/guard`: 666 passed, 6 failed); green 672 passed; the resume call deleted, the
   same 6 red, and the permit check deleted, the end-to-end test red - measured 2026-11-20 (the same run each time). The shell suite
   28 passed - measured 2026-11-20 (`tests/hooks/test-context-cap-hooks.sh`, its D10 and permit cases through the real binary and `make context-ok`).
   The two fixes below, red first: 670 passed, 2 failed and the suite 28 passed, 2 failed, then 672 passed and the suite 30 passed -
   measured 2026-11-20 (`make rust-test CRATE=rust/guard` and the suite, before and after).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?**
- `make context-ok`'s grant printed guard-edit's words, `guard-edit: <clone>/context-cap:<id> may be edited until <time>`, naming no
  file anyone edits: `guard_file_hooks::cli` now prints `context-ok: agent <id> may pass the context cap until <time> - <reason>` for a
  `context-cap:` key (pinned in the end-to-end unit test and the suite). Fixed here.
- A `SendMessage` to an agent with no meta file passed with no guard-log record, unlike `resume-no-task`, so such passes could not be
  counted: it now passes as `ResumeNoMeta`, logged `resume, no meta file: <id>` under the rule `resume-no-meta` (the unit test and the
  suite). Fixed here.

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: T14 to T14 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-20 -->
### T19 (FR-011: a task-add line that `make quick` refuses was found only at the landing - research R8)

- **Approach**: D16's second half in `rust/gate/crates/task/src/task_add.rs` and `task_add/quick.rs` (not held). After the box and the
  section are written, task-add reads `make -n quick` (the recipe stays the one list; a backslash-continued line read as one) and runs
  each line it keeps by `sh -c` to its own end, side by side; on a red it puts both files back to their bytes before the filing (a
  plan.md it created removed), runs them again and compares: a failure is a check's `failed (exit N)` and each non-blank line it
  prints, line and column numbers masked (`:12`, `:12:3`, `line 12` - never other digits, so FR-023 and FR-024 stay apart), as a
  multiset. A failure only the with-line run has: the files stay as they were, refused (exit 2) naming those failures, recorded
  `blocked/quick-red`. None: the line is put back and the red reported as already there. A `make -n quick` that cannot list (no
  Makefile) refuses before anything is written. **Set aside**, as D16 says, only the stamp (`state write green-local`, `STAMP` in
  `quick.rs`) and the closing `printf`: every other line of quick is run, all seven checks, so a check added to quick is run here
  with nothing to update. No list of the checks that cannot read what task-add writes (ruff, house-style-delta's selftest,
  question-size, file-scale and partial-citations read no `specs/` box or section): all seven side by side cost 0.12 s against 0.10 s
  for the two that do, measured 2026-11-20 (`date +%s%N` around `sh -c`, shell `&` and `wait`, three runs), and such a list goes
  stale silently when a check's inputs change (the lead's ruling, 2026-11-20). **Not the Makefile** (a deviation from D16's `$(LOGESCAPE)`, made because this
  builder's files exclude the held Makefile): `QUICK_OK="<reason>"` is read from the environment and recorded by the tool (two words and eight characters, else refused
  `blocked/QUICK_OK-no-reason` before anything is written; taken: `escaped/quick-ok`, `make guard-log GUARD=task-add`), as
  `PERF_LATER_OK` is by `make task-start` (T28's precedent: no `$(LOGESCAPE)` line, which would record it twice); a command-line
  variable reaches the binary without a `FREE_TEXT` entry, measured 2026-11-20 (`make task-add F=451 TITLE="... (FR-023)"
  QUICK_OK="..."` run once, its one `escaped/quick-ok` row read in `make guard-log GUARD=task-add`, the files then put back). Red
  first, the four cases on a fixture quick (an EARLY check red as a ruff failure reads, a LINT red on each `FR-4nn` as spec-lint's
  check 4 reads a bare id): a line citing a bare id withdrawn and refused, both files byte-identical; a clean line stays; the early
  check red plus the line's own lint failure: refused naming the lint failure alone (the case a sequential `make quick` hides); a
  finding already there below the box, its line number shifted, keeps the line and reports it. Before the code all four were red, measured 2026-11-20 (`make rust-test
  CRATE=rust/gate/crates/task`, 60 passed, 4 failed); with the check deleted (`checked`'s first run made empty) five were red, measured 2026-11-20 (the same command). Every line run (the
  lead's ruling): the fixture's ruff line leaves a file, asserted present, red with the old skip of the ruff line put back, measured
  2026-11-20 (the same command, 69 passed, 1 failed: "the ruff line did not run"). The tests' guard log: a test asserts the log is the
  crate's scratch census BEFORE anything records, then takes `QUICK_OK` and finds the row there and in no file this process wrote in
  `$HOME/.claude/guard-log`; a pin, since every recording test already goes through `repo()`, which sets `GUARD_LOG_DIR` - a mutation
  red, not red first: with `repo()`'s `quiet_census()` taken out and the test run alone under a scratch `GUARD_LOG_DIR`, it failed on
  the first assertion, measured 2026-11-20 (the test binary run alone, `left: "/tmp/t19b/scratch-log"`, the assertion then an
  `assert_eq!`, since folded into one `assert!` over the same comparison for coverage); in the full suite the mutation passed, another
  test having set the variable first, so the pin catches a leak only where nothing else sets it.
- **The cost** of a template filing in 451 (`[perf] a timing probe`): 15-20 ms before T19 and 156-168 ms after, all seven checks
  run, so about +0.15 s a filing, and a refused filing (a bare `FR-999`, the checks run twice) 321-573 ms, measured 2026-11-20 (a quiet
  tree: a detached scratch worktree of HEAD, its delta against `origin/main` empty, "before" the `l7r-gate` built from it and "after"
  the one built from the clone's tree, each run directly as `TASK_TITLE=... l7r-gate task-add 451` in that worktree, `date +%s%N`
  around it, one warm-up and five timed runs, both files checked out after each; the machine shared with other builders' cargo
  runs, load average 18-19 on 22 cores, which the refused figure's spread shows). Each quick line with a line filed, measured
  2026-11-20 (`date +%s%N` around `sh -c`, three runs, the T19 diff in the delta): ruff 34-40 ms, house-style-delta's selftest
  90-106, house-style-delta 98-109, question-size 43-46, file-scale 89-98, spec-lint --delta 68-88, partial-citations 58; all seven
  one after another about 0.50 s and side by side 0.12 s, measured 2026-11-20 (the same method, shell `&` and `wait`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the quick check | n/a - no map | n/a | none | n/a |

### T19 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a task line that would refuse a landing never lands in `tasks.md`.
2. **The constraints.** FR-011, FR-012; D16.
3. **Where each comes from.** G: the approved "run make quick after task-add"; O: research R8.
4. **Do they describe the world here?** R8 read the crates task-add builds on.
5. **The order.** After T18.
6. **The exits.** Green: the four cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The task crate's cases; the check deleted, the firing case red.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?**
- `QUICK_OK` was not on `make task-add`'s help line nor in `FREE_TEXT`: fixed here, by the lead's Makefile half of this task.
- The two `task-add` rows for T37 in `~/.claude/guard-log` (`blocked/quick-red` and `escaped/quick-ok`, "a probe of the escape for
  T19"): not a defect - they are the real-tree probe's own records (the measurement above), not a test's; no test row reached the log
  (none names `9001-x`), and the log is no tracked file.
- `rust/gate/CLAUDE.md`'s `task` row names `task_add.rs` but not `task_add/quick.rs`: not a defect - no wrong outcome, an index line
  outside this builder's files, reported to the lead.

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: archived 2026-11-20 -->
### T20 (FR-010: three suites set the floor of every `make hooks-test` - research R10)

- **Approach**: D17's runner, proved on one small real suite; the three slow suites' splits are T21's. Held: the root `Makefile`
  (`make guard-edit FILE=Makefile` first); not held: `tests/hooks/hookrun.sh`, and `tests/hooks/test-parts.sh` (`parts.sh`'s suite,
  13 cases) split into `test-parts.1.sh` (run_parts, 6 cases) and `test-parts.2.sh` (hookrun.sh, 7 cases and the 16 new pins),
  observed 2026-11-20, method: each suite run alone, its `passed` line (13 before; 6 and 23 after).
  - **A shard** is `tests/hooks/test-<name>.<k>.sh`, `k` all digits (`test-x.notes.sh` is no shard), run in `k`'s numeric order with
    gaps allowed: every shard on disk is a job. Its job is `<guard>.<k>`: its own
    `.rc`, `.log`, `.s` (kept as `.git/hooks-test/<guard>.<k>.s`, which the longest-first order reads) and `.reads`; it stamps nothing.
  - **The stamp**: after the fan-out, `hookrun.sh --close` stamps the suite - its sha, its trace from every shard's reads, and its shard
    list `.git/hooks-test/<guard>.jobs` - only when every shard's job is ok; one red or missing shard leaves it unstamped. One stamp a
    suite, because `trace stamp` rewrites the suite's trace whole (a shard stamping its own would drop the others' reads).
  - **The key**: `l7r-guard deps` seeds a guard's key from `test-<name>.sh`, which a split suite no longer has, so the recipe keys each
    shard as a name of its own (`deps --keys <roster> <shards>`) and hashes the guard's key with its shards' keys; an edited shard reruns
    the suite. A traced suite is skipped only while its shard list matches the kept `.jobs`, so an added shard reruns it. No change to
    `rust/guard`.
  - **The companion check** (`hooks-test`'s GUARD WITHOUT A TEST) takes `hookrun.sh --jobs`, one call for every suite before the loop
    (one call a suite cost 6.9 s for 57 suites on a loaded host, measured 2026-11-20 (57 single-suite calls timed beside a full run)):
    a guard's suite or its shards. A suite beside its own shards (D17's "beside nothing else of that name") fails the run as SUITE AND
    SHARDS BOTH, with the fix. A lone shard - one
    whose `test-<name>.sh` no guard on the roster owns, so nothing would ever run it - fails the run as SHARD WITHOUT ITS SUITE
    (`hookrun.sh --orphans`), with the fix. A guard with a single shard is accepted (one job, as its suite was).
  - **Red first**: `test-parts.2.sh` against HEAD's `hookrun.sh` - a green shard stamped its suite, no shard job of its own, `--close`,
    `--jobs` and `--orphans` unknown; the 3 new cases that passed are the ones an all-green or all-owned run would pass anyway:
    13 of its 23 cases failed, measured 2026-11-20 (`test-parts.2.sh` beside a copy of `git show HEAD:tests/hooks/hookrun.sh`).
    After: `test-parts.2.sh` 23 of 23 and `test-parts.1.sh` 6 of 6 green, measured 2026-11-20 (each shard run alone).
  - **The recipe, end to end** on the batched recipe, each case one `make hooks-test` in the clone, observed 2026-11-20 (its summary
    lines and exit, logs `/tmp/t20-recipe2.log` and `/tmp/t20-recipe3.log`; other suites in a "ran" line are T32's Rust edits and
    `tests/hooks/` changes rekeying them): `test-nosuch.1.sh` alone, SHARD WITHOUT ITS SUITE and the run red; `test-parts.sh` beside its
    shards, SUITE AND SHARDS BOTH and the run red; a third shard added, `parts.sh.1`, `.2` and `.3` ran; back to two, both ran; a shard
    edited, `parts.sh.1` and `.2` ran, and again when the edit was reverted; a red third shard, `HOOK TESTS FAILED: parts.sh.3` and the
    kept `.git/hooks-test/parts.sh.jobs` still the two green shards; back to two after it, `parts.sh` skipped (its sha and shard list
    those kept), the run green.
  - **Case 2b of `tests/hooks/test-land-tooling.sh`** (not held; T35's land-tooling half, folded in at the launcher's word): its
    overlap check bounded the checks step's seconds, which load breaks. Each job now marks its start and waits up to 20 s (GUESS: a cap far past
    any start delay, short enough that a serial run fails soon) for the other's mark, and the case asserts both saw the other; that each job and the checks step are timed stays, as numbers recorded.
    Red first, case 2b alone in a harness at nice 10 beside 44 busy loops - the old `.checks < 1.8` with two `sleep 1` jobs:
    3 of 3 failed, measured 2026-11-20 (the harness, its FAIL lines), and 2 of 3 in an earlier try, measured 2026-11-20 (the same).
    The proposed `.checks < guard-suites + tooling-tests - 0.5` with two `sleep 2` jobs fared no better:
    at least 2 of 3 failed in each of two tries, measured 2026-11-20 (the same harness and load).
    The barrier form under that load: 5 of 5 green, measured 2026-11-20 (the same harness and load).
    With the two jobs run one after the other (a scratch `land-tooling.sh` with the `&` removed): 2 of 2 red, measured 2026-11-20 (the harness, unloaded).
    The suite alone after: 52 of 52 green, measured 2026-11-20 (`bash tests/hooks/test-land-tooling.sh`, its `passed` line).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the shard form, parts.sh's suite | n/a - no map | n/a | none | n/a |

### T20 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a suite can be split so that no one suite holds the run's wall time.
2. **The constraints.** FR-010, SC-004; D17; every case of the split suite still runs (13 before, 6 + 7 after, and 16 new).
3. **Where each comes from.** G: the approved "Split the three slowest hook suites"; O: research R10.
4. **Do they describe the world here?** R10 read the kept seconds of a full run; the before run below reads the same.
5. **The order.** After T19; before T21, which splits the three slow suites in this form.
6. **The exits.** Green: the shard form runs, stamps and pairs as above, and `make hooks-test` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test HOOKS_ALL=1` before and after on the same tree, its `WALL` and "ran" lines; `.git/hooks-test/parts.sh.*.s` read.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?**
- The entry-gate split this section named (`test-entry-gate.sh` by its two cases). It still holds the run's wall time:
  `entry-gate.sh` 34.0 s of a 40.8 s full run, measured 2026-11-20 (`HOOKS_ALL=1 make hooks-test`, its "ran" line).
  Not fixed here: the launcher's brief narrowed T20 to the shard form, proved on a small suite, and moved the entry-gate split to T21,
  which carries it with l7r-gate and sync-with-main. Filed as T21; lands before T22.
- `test-land-tooling.sh` case 2b ("they overlapped: the checks took less than the two jobs one after the other") failed once and
  passed on the next run with nothing changed, observed 2026-11-20 (two `make hooks-test` runs at load about 16): a wall-clock
  assertion that load can break. Fixed here (T35's land-tooling half folded in): the overlap is met, not timed - see "Case 2b of
  `test-land-tooling.sh`" above.

**Performance work?** yes - its answers below.

### T20 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** One suite's cases run one after another inside its job: l7r-gate.sh 38.3 s, entry-gate.sh 34.0 s, sync-with-main.sh 24.0 s of a 40.8 s wall, measured 2026-11-20 (`HOOKS_ALL=1 make hooks-test`, its "ran" line, load 5.5 on 22 cores).
2. **Removes work, or only moves it?** Moves it onto idle jobs; the cases are unchanged.
3. **What do you expect it to save, and why?** Nothing in T20: parts.sh's suite was never on the critical path, so the wall stays where it was; the saving is T21's, the wall falling toward the next slowest suite's once the three are split.
   parts.sh 1.6 s and idle-tests-hooks.sh 18.1 s of a 40.8 s full run, measured 2026-11-20 (`HOOKS_ALL=1 make hooks-test`, its "ran" line).
4. **How does the work grow with the settlement?** n/a - no settlement.
5. **What did the before and after show, and under what conditions?** Equal within noise, as item 3 expected: entry-gate.sh's one job set the wall in all four runs, and parts.sh's shards ran beside it.
   Before (HEAD's Makefile, hookrun.sh and test-parts.sh): WALL 54.65 s and 55.50 s, measured 2026-11-20 (`/usr/bin/time make hooks-test HOOKS_ALL=1`, alternated with the after runs back to back, load 10.3 and 21.3 at their starts).
   After (this tree): WALL 56.24 s and 56.36 s, measured 2026-11-20 (`/usr/bin/time make hooks-test HOOKS_ALL=1`, alternated with the before runs back to back, load 21.1 and 21.2 at their starts).
   The critical suite: entry-gate.sh 51.7 s and 51.7 s before, 51.9 s and 53.9 s after, measured 2026-11-20 (the same four runs, their "ran" lines).
   The new startup step: the one `hookrun.sh --jobs` call 12-15 ms and its 56 per-guard awk lookups 85-123 ms, measured 2026-11-20 (five reps of the recipe's prelude alone, `date +%s%N` around each, load 10.9) - under 0.2 s of a 55 s wall, so the lookups stay out of the sha awk.
   The host was loaded by another builder's Rust work throughout, far above item 1's run, so only the back-to-back pairs compare.
6. **Did any map move, and does it still keep the research?** No map.

<!-- plan-archive: archived 2026-11-20 -->
### T32 (the guard's own tests read the real environment: with `L7R_FEATURE_DIRECTORY` exported, as a page session exports it, 17-20 tests of the check state and its guards failed, found by T14, observed 2026-11-20, method: T14's `make rust-test` log)

- **Approach**: one reader of the environment for the guard crate, `shared::env` (`opt`, `var`; a test build's `set`, `unset`): outside
  `cfg(test)` the process's variable, under it the test thread's own map, empty until a test names one (`HOME` the process's where a
  test names none), so no test reads a session's exports and none mutates the process environment. `consulted::var` and its `VARS`
  become re-exports of it (T24's seam, one map, not two). Each read the sweep moved goes through it, and each test that set the
  process environment sets its own instead; `arbiter/tests.rs` pins the seam (empty, then each pointer named, then unset).
  - red first, `L7R_FEATURE_DIRECTORY=specs/451-time-retro-and-efficiency` exported: 655 passed, 17 failed (checks_hooks 1, check_bundle_hooks 1, pair_hooks 2, review_round_hooks 2, shared::checks::arbiter 5, fixloop 1, handle 4, rounds 1), measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1`, `/tmp/t32-red.log`).
  - every failure traced to `arbiter::feature_env`'s `std::env::var("L7R_FEATURE_DIRECTORY")` (the feature the check state is kept under), read 2026-11-20 (`rust/guard/src/shared/checks/arbiter.rs`); after the fix, exported: 673 of 673 passed, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1`, `/tmp/t32-sweep/rep-1.log`), and the same in two more runs (`rep-2.log`, `rep-3.log`) with `L7R_PAGE_SESSION` and `L7R_CONTINUE` exported beside it as `runner/work.rs` exports them.
  - the sweep, before the fix: 79 variables the crate reads (every `std::env::var`, `var_os` and `from_env` key and `consulted::var`, 78 at a plausible value, then 12 of them again at a value off their default, and `HOME`), 91 runs, each variable exported alone: 5 moved a test - `RECORD_CHECKS_DIR` 1 (rounds), `L7R_GUARD_TREE` 1 (session), `SET_DOWN_ROOT` 1 (set_down_hooks), `L7R_PERMIT_NOW` 2 (guard_file_hooks, context_cap_hooks), `L7R_DISPATCHER` 1 (clone_sync_hooks) - measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1` per variable, `/tmp/t32-sweep/per-var.tsv`, `per-var2.tsv`).
  - a read no pass or fail shows: with `L7R_EVENTS_DIR` exported the event-log tests wrote 3 fixture logs (`450-c`, `451-a`, `_unassigned`) into the exported directory, stamped with the real session's id, measured 2026-11-20 (`find /tmp/t32-sweep -newer vars.sh`); after the fix, none (the directory held only the gate's own `Phase` lines), measured 2026-11-20 (the same `find`, after `/tmp/t32-sweep/all-after.log`).
  - the 7 tests that set the process environment (`PAIR_NOW`, `L7R_LAND_TICKS`, `AGENT_WATCH_TICKS`/`AGENT_TICK_S`, `AGENT_STALE_S`, `BATCH_THRESHOLD`/`BATCH_STATE_DIR`, `STALL_SESSIONS_DIR`/`STALL_STATE_DIR`, `L7R_SELF_CHECK` twice) set the test thread's own, their reads converted with them, measured 2026-11-20 (`grep set_var rust/guard/src`); left: `log::quiet`'s `GUARD_LOG_DIR`, set once for the whole process by design (T009), and the binary's own `main.rs` and `bench.rs`.
  - after the fix, the 78 exported at once: 673 of 673 passed, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1`, `/tmp/t32-sweep/all-after.log`); each alone: 91 of 91 runs green, 673 of 673 each, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1` per variable, `/tmp/t32-sweep/per-var-after.tsv`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the guard's environment reader | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T32 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the guard crate's tests reach the same lines whatever the builder's shell exports, and write nothing into a session's real logs, measured 2026-11-20 (the 79-variable sweep above).
2. **The constraints.** T32's line (each test its own environment, no process-environment mutation, the one outcome it means, red first with the variable exported, every other variable swept); T24's seam (`consulted::context_from`, the thread-local map); 100% line coverage of the crate by its own tests, measured 2026-11-20 (`l7r-gate.sh rust cover --crate rust/guard`: clean).
3. **Where each comes from.** O: T14's red run, measured 2026-11-20 (T14's `make rust-test` log); O: the red-first run, 17 failed, measured 2026-11-20 (`make rust-test`, `/tmp/t32-red.log`); R: T24's section in plan-done.md (the seam); the task as filed (T32's line).
4. **Do they describe the world here?** Yes: a page session's runner exports `L7R_FEATURE_DIRECTORY=specs/<NNN-slug>` with `L7R_PAGE_SESSION` and `L7R_CONTINUE`, read 2026-11-20 (`rust/gate/crates/pages/src/runner/work.rs`, `runner.rs`'s `brief_feature`), and that export alone turned 17 tests, measured 2026-11-20 (`/tmp/t32-red.log`).
5. **The order.** After T24 (its seam, reused); independent of T20 (the hooks-test recipe and `hookrun.sh`, untouched here).
6. **The exits.** Green: 673 of 673 plain and exported, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1`, `/tmp/t32-plain.log`, `rep-1.log`; the final runs `/tmp/t32-final-plain.log`, and `/tmp/t32-final-exported.log` with `L7R_FEATURE_DIRECTORY` and `L7R_EVENTS_DIR` exported, the exported directory holding only the gate's own 2 `Phase` lines); the crate's lint and cover clean, measured 2026-11-20 (`l7r-gate.sh rust lint|cover --crate rust/guard`); `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** `no_poll_hooks`, named by T14's run, was not reproduced: it failed in none of 4 exported runs nor the sweep's 91, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1`, `/tmp/t32-red.log`, `rep-1..3.log`, `per-var.tsv`); named in the report.
8. **The budget.** One landing.
9. **Done, measured.** 0 of 673 failed with the 78 variables exported at once, measured 2026-11-20 (`/tmp/t32-sweep/all-after.log`), and each alone, measured 2026-11-20 (`/tmp/t32-sweep/per-var-after.tsv`).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a page session's builder no longer sees 17 guard tests red, and a builder with `L7R_EVENTS_DIR` exported no longer gets test lines in a real feature's event log (which `make where-time` and T13/T14 read), 3 logs before and 0 after, measured 2026-11-20 (`find` over the exported directory).

**Found and left?**
- The 6 tests the sweep moved (`RECORD_CHECKS_DIR`, `L7R_GUARD_TREE`, `SET_DOWN_ROOT`, `L7R_PERMIT_NOW` 2, `L7R_DISPATCHER`): fixed here, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1` per variable, `/tmp/t32-sweep/per-var-after.tsv`).
- The event-log tests' writes into an exported `L7R_EVENTS_DIR` (3 fixture logs stamped with the real session's id): fixed here, 0 after, measured 2026-11-20 (`find` over the exported directory).
- The 7 tests that set the process environment: fixed here, measured 2026-11-20 (`grep set_var rust/guard/src`).
- `log::quiet`'s set-once `GUARD_LOG_DIR`: not a defect (set once for the whole process by design, T009).
- A `MEASURE_STATE_DIR` exported to a fresh path: not a defect - a test created it empty, nothing written in it, measured 2026-11-20 (`ls /tmp/t32-sweep/measure`).
- The reads the sweep moved no test with: not a defect, each named in `/tmp/t32-sweep/per-var.tsv`.
- The gate crates' tests read the real environment through the guard: with `L7R_FEATURE_DIRECTORY` and `L7R_EVENTS_DIR` exported, 49 tests of 7 crates fail (arbiter 12, bundle 2, land 17, measure 1, owed 1, reviews 10, rustc 6) and 23 crates plus `gate`, `browser`, `embed` and `mode_a` pass, measured 2026-11-20 (`make rust-test CRATE=<crate> FRESH=1` per crate, both exported, `/tmp/t32-sweep/all2/summary.txt`); each red crate green with neither exported, measured 2026-11-20 (`make rust-test CRATE=<crate> FRESH=1` per crate, `/tmp/t32-sweep/plain-{arbiter,bundle,land,measure,owed,reviews,rustc}.log`). Not fixed here: the guard's test map is `cfg(test)` of the guard alone, so the fix is an environment reader threaded to 17 call sites in 7 crates (`feature_dir`, `log_path`, `append_row`, `append_row_for`), measured 2026-11-20 (`grep -rE` over `rust/gate`, `rust/browser`, `rust/embed` and `rust/mode_a` outside tests), each crate owing its own test, lint and cover - a task's worth of work outside the guard. Filed as T38; lands before T22.

**Performance work?** yes (a `[perf]` task, 451 FR-013: a builder's `make rust-test` on the guard is green whatever the session exports, so no round is spent on a red that is the shell's); not engine speed.


<!-- plan-archive: archived 2026-11-20 -->
### T21 (FR-010: the other two of the three slowest suites)

- **Approach**: the goal is a faster `make hooks-test` (improvement 5, the GM 2026-11-19), and D17's split of
  `tests/hooks/test-l7r-gate.sh`, `tests/hooks/test-sync-with-main.sh` and `tests/hooks/test-entry-gate.sh` was its sketch; each split
  was measured against HEAD and kept only where it lowered the wall. Kept: the l7r-gate split. Put back whole from HEAD: sync-with-main
  and entry-gate, since their shards lowered no wall in a full run or an incremental one (the measurement below). `HOOKS_JOBS` stays 8.
  - **l7r-gate** (55 checks before; 41 + 9 + 5 after, measured 2026-11-20 (each run alone, its `ok` lines)): `.1` the stamp, the
    no-build seam, the fresh binary, the Mode A and hamlet launchers, `.2` the browser and the archive, `.3` the embedder and the
    research search. Alone they take 1.3 s, 7.5 s and 5.7 s, measured 2026-11-20 (each shard run alone, `EPOCHREALTIME` around it, `L7R_GATE_FRESH` set as the recipe sets it).
    The groups read state an earlier group left, so each shard makes its own: `.2` and
    `.3` export the git identity the stamp fixture exported; `.3` makes its own empty secrets file (it read the archive group's
    `$A/no-secrets.ini`) and exports the dead proxy the archive group exported, so the embedder still never reaches the network; the
    fresh-binary and hamlet groups stay in `.1` after the no-build seam whose fake `cargo` they call.
  - **The helpers are copied, not sourced.** `l7r-guard deps` reads no `test-*` file as a helper (`rust/guard/src/suite_tools/deps.rs`,
    its `helper` filter, observed 2026-11-20, method: the filter read), so a sourced `test-<name>.lib.sh` would be an edge the key
    never sees; a copy in each shard is keyed with it. The copies are the parts.sh shards' form (T20).
  - **The pointers**: `rust/embed/src/lib.rs` line 8, `rust/embed/src/model.rs` line 6 and `rust/gate/CLAUDE.md` line 43 named
    `tests/hooks/test-l7r-gate.sh` and now name `test-l7r-gate.3.sh`; the other seven (`docs/guards.md` rows 35, 40, 72, 78, 83, 100 and
    `scripts/sync-with-main.sh` line 469) name `test-sync-with-main.sh`, which stays, observed 2026-11-20, method: `git grep` of the three names.
  - **Two suites failed at `PARTS_MAX=1`, fixed here** (the runner sets it to `CPU_COUNT / HOOKS_JOBS`: 1 at `HOOKS_JOBS` 12 or more on 22
    cores, or at 8 on an 8-core host): `test-parts.1.sh` built fixture suites that must split in two and inherited the cap, and
    `test-pair-hooks.sh` ran its cases in its own shell when it had one part, leaving fixture state its trailing blocks read. Both
    failed in every such run, measured 2026-11-20 (eight `make hooks-test HOOKS_ALL=1` runs at HOOKS_JOBS 12 and 16, CPU_COUNT 22).
    `test-parts.1.sh` now unsets `PARTS_MAX`; `test-pair-hooks.sh` runs one part as a process of its own, as it runs each part.
    Both pass at `PARTS_MAX` 1 and 2 (6 and 100 checks), measured 2026-11-20 (each suite run alone at both values).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the l7r-gate split, two suites put back | n/a - no map | n/a | none | n/a |

### T21 Approach (checklist part A)

1. **The goal, in the world.** A faster `make hooks-test`, full and incremental; no map changes.
2. **The constraints.** FR-010, SC-004; D17; every case of each suite still runs (l7r-gate's 55 checks before and after).
3. **Where each comes from.** G: improvement 5 and its sketched split; O: research R10; the bar `SHARD_BAR_S` about 20 s is a GUESS, never a gate.
4. **Do they describe the world here?** Measured on two scratch clones of HEAD, one with the split, back to back (performance item 5).
5. **The order.** After T20; before T22.
6. **The exits.** Green: a split kept only where the wall falls; HEAD's suites where nothing beats them. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test HOOKS_ALL=1` and incremental runs, HEAD against each split, the wall timed around make.
10. **Before moving a constant.** `HOOKS_JOBS` measured at 6, 8, 12 and 16; 8 kept.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?**
- `sync-with-main`'s suite, kept whole, is past the 20 s bar in a full run too: 26.8-40.2 s at jobs 8, measured 2026-11-20
  (`/tmp/t21m/r*-head-j8-c22.log` and `rm*-head-j8-c22.log`, each run's "ran" line). Not a defect: no wrong outcome - it does not set
  the wall (entry-gate's chain finishes about 10 s after it in every run, same logs), and its split saved nothing (the incremental
  rows above), so the 20 s figure, a GUESS never a gate (D17), is not a target to hold it to.
- `entry-gate.sh` stays past the 20 s bar in a full run: 41.7 s, 44.4 s, 38.6 s, 44.2 s, 40.8 s, 41.7 s and 38.7 s, measured 2026-11-20 (seven `make hooks-test HOOKS_ALL=1` runs of HEAD at HOOKS_JOBS 8, their "ran" lines).
  Not a defect: no wrong outcome (constitution XIV), a GUESS bar missed. Splitting it by its two cases lowered neither wall: full runs
  equal (performance item 5), and after an edit of `entry-gate.sh` 23.1 s and 23.3 s split against 22.4 s and 22.8 s whole, measured 2026-11-20 (incremental `make hooks-test`, `EPOCHREALTIME` around it).
  The full run's wall is set by entry-gate's suite, its case-4 chain of record gates: in every HEAD run the wall was entry-gate's
  seconds plus 2-3 s, about 10 s ahead of the next suite, measured 2026-11-20 (each run's "ran" line against its wall). Splitting it
  by its two cases did not shorten it, nor did more job slots; the chain itself is the lever, filed as its own task.

**Performance work?** yes - its answers below.

### T21 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In a full run, into CPU the host cannot supply faster: 482-566 CPU-seconds a run in 41.6-46.7 s, 11.6-12.5 cores busy on average, measured 2026-11-20 (`/usr/bin/time` around `make hooks-test HOOKS_ALL=1`, HEAD at HOOKS_JOBS 8, seven runs).
   No wait on disk, memory or the run queue: CPU pressure 2.2-2.7 s, I/O pressure 0.1 s or less, memory pressure 0, no OOM kill, measured 2026-11-20 (the container's `cpu.pressure`, `io.pressure`, `memory.pressure`, `memory.stat` and `memory.events` read around each run).
   The host is a Core Ultra 7 155H, 16 cores and 22 threads (6 performance cores with two threads each, 10 efficiency cores), so about 12 busy threads is near its sustained throughput: more jobs added CPU-seconds and no speed (item 5).
   In an incremental run after an edit of `l7r-gate.sh` or `sync-with-main.sh`, into the l7r-gate suite: 15.1-16.5 s of a 16.7-17.9 s wall, measured 2026-11-20 (HEAD, incremental `make hooks-test` at HOOKS_JOBS 8, eight runs, their "ran" lines).
2. **Removes work, or only moves it?** Moves it: the l7r-gate shards run side by side; no case is removed.
3. **What do you expect it to save, and why?** About 5 s of an incremental run that reruns l7r-gate's suite (a GUESS from its shards' figures alone), its three shards side by side, and nothing in a full run, whose wall entry-gate's chain sets.
4. **How does the work grow with the settlement?** n/a - no settlement.
5. **What did the before and after show, and under what conditions?** Two scratch clones of HEAD 7d685821b6, one with the split
   staged, each run back to back on a host nothing else loaded (`ps` at 12:56 and 13:11 showed no other hook run), load 6-23 from the runs themselves.
   Full runs, HOOKS_JOBS 8 (PARTS_MAX 2):
   HEAD 44.0, 46.7, 42.0, 46.7, 42.7, 43.6 and 41.6 s (mean 43.9 s), measured 2026-11-20 (`EPOCHREALTIME` around `make hooks-test HOOKS_ALL=1`).
   All three split 44.1, 44.5, 43.0 and 44.2 s (mean 44.0 s), measured 2026-11-20 (the same method, each run beside a HEAD run).
   l7r-gate alone split 43.6, 44.5, 43.9 and 43.3 s (mean 43.8 s), measured 2026-11-20 (the same method; a fourth pair replaced one HEAD run that overlapped another of these measurements).
   Other job counts, HEAD then all three split:
   HOOKS_JOBS 6 (PARTS_MAX 3): 49.8 and 50.5 s, then 48.7 and 49.0 s, measured 2026-11-20 (the same method).
   HOOKS_JOBS 12 (PARTS_MAX 1): 52.6 and 53.4 s, then 49.7 and 49.4 s, all red on the two PARTS_MAX=1 defects, measured 2026-11-20 (the same method).
   HOOKS_JOBS 16 (PARTS_MAX 1): 53.3 and 51.8 s, then 47.2 and 47.4 s, all red the same way, measured 2026-11-20 (the same method).
   HOOKS_JOBS 12 (PARTS_MAX 2, CPU_COUNT=24): 46.8 and 47.7 s, then 44.9 and 45.0 s, measured 2026-11-20 (the same method).
   HOOKS_JOBS 16 (PARTS_MAX 2, CPU_COUNT=32): 49.3 and 48.6 s, then 46.6 and 47.1 s, measured 2026-11-20 (the same method).
   CPU-seconds rose with the job count: 482-566 at 8, 722-733 at 12 and 790-798 at 16 for HEAD, measured 2026-11-20 (`/usr/bin/time` around each run), with no wall gained, so 8 stays.
   Incremental runs, HOOKS_JOBS 8, after a comment-only edit of one guard (reverted and restamped after each):
   `sync-with-main.sh` edited, HEAD: 16.7, 17.6, 17.7 and 17.9 s, measured 2026-11-20 (incremental `make hooks-test`, `EPOCHREALTIME` around it).
   `sync-with-main.sh` edited, all three split: 12.7 and 12.1 s, measured 2026-11-20 (the same method).
   `sync-with-main.sh` edited, l7r-gate alone split: 11.8 and 11.8 s, measured 2026-11-20 (the same method).
   `l7r-gate.sh` edited, HEAD: 17.3, 17.7, 17.8 and 17.8 s, measured 2026-11-20 (the same method).
   `l7r-gate.sh` edited, all three split: 12.3 s, measured 2026-11-20 (the same method; its second run overlapped another measurement and was dropped).
   `l7r-gate.sh` edited, l7r-gate alone split: 11.6 and 11.9 s, measured 2026-11-20 (the same method).
   Whole, sync-with-main took 5.0-7.7 s in those HEAD runs and its shards 8.7, 7.7 and 4.0 s, measured 2026-11-20 (their "ran" lines): with few suites running its own parts already fill the cores (PARTS_MAX up to 8), so its split only added the template three times.
   In this clone with the kept split: 39.6 and 44.5 s, green, measured 2026-11-20 (two `make hooks-test HOOKS_ALL=1` runs back to back, `EPOCHREALTIME` around them, load 5.1 and 9.5 at their starts).
   So the l7r-gate split saves about 6 s of an incremental run and makes no measurable difference in a full one (paired runs had it
   0.3-1.7 s slower, inside HEAD's 41.6-46.7 s spread), measured 2026-11-20 (the runs above), and the other two splits save nothing and were put back.
6. **Did any map move, and does it still keep the research?** No map.

<!-- plan-archive: archived 2026-11-20 -->
### T35 (rustc's `another_runs_holder_is_waited_for_named_and_past_the_ceiling_refused` asked for two waiting lines inside a 60 ms ceiling at a 10 ms poll of the wall clock and saw one under `make static`'s load, a red gate on correct work, observed 2026-11-20, method: T12's `make static` log; its land-tooling half folded into T20)

- **Approach**: the wait reads its time through a clock seam, `runlock::Clock` (`now`, `sleep`) on the `Taker`: a run's is `Wall`
  (`Instant` and `thread::sleep`, the behavior unchanged); the test's is `Stepped`, which moves only when slept on, by the poll, so
  the wait's lines are counted against the ceiling over the poll (an event count), not against how long the host took. The test
  asserts exactly 6 lines (waited 0 to 50 ms, refused at 60, read 2026-11-20 from `take`'s loop and the test's 60 ms ceiling and
  10 ms poll), where it asked `>= 2`, and a wait that never ends reads the stepped clock past 100 times (the test's `READS`, a cap
  far above the 8 reads the wait takes, measured 2026-11-20 (the loop's reads counted by hand: one before it, one per pass)) and
  panics rather than hangs. The other runlock tests keep the wall clock, so `Wall` stays covered by them.
  - the old test idle: 20 passed of 20, measured 2026-11-20 (its test binary run `--exact` 20 times, `/tmp/t35/`).
  - the old test beside 44 busy loops on 22 cores: 6 failed of 20, then 0 of 20 on a rerun, measured 2026-11-20 (`/tmp/t35/load.sh`, `/tmp/t35/old-*.log`, `/tmp/t35/old2.log`).
  - the old test beside 88 busy loops: 0 failed of 20; beside 22 fork loops and 11 fsync'd write loops: 0 failed of 20, measured 2026-11-20 (`/tmp/t35/old3.log`, `/tmp/t35/load2.sh`, `/tmp/t35/old4.log`).
  - red first, the old test sharing a core with 16 busy loops (`taskset -c 0`): 10 failed of 10, each on the waiting-lines assertion with one line, measured 2026-11-20 (`/tmp/t35/load3.sh`, `/tmp/t35/old5-*.log`) - the red is reliable only when the test shares a core.
  - green: the new test 5 passed of 5 on the shared core and 5 of 5 beside 44 busy loops, measured 2026-11-20 (`/tmp/t35/new-pinned.log`, `/tmp/t35/new-loops.log`); every runlock test 5 runs of 5 green on the shared core, measured 2026-11-20 (`/tmp/t35/all-pinned.log`); the crate 68 passed of 68, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/rustc`, `/tmp/t35/green1.log`).
  - the behavior broken, the test red: a line said once rather than each poll, 1 failed of 68 (`left: 1, right: 6`), measured 2026-11-20 (`/tmp/t35/broken-say.log`); the ceiling never reached, 1 failed of 68 ("the wait read the clock 100 times: it never ended"), measured 2026-11-20 (`/tmp/t35/broken-ceiling.log`); each break reverted.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the wait's clock a seam, the test on a stepped clock | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T35 Approach (checklist part A)

1. **The goal, in the world.** No map changes; `make static` is not turned red by the run lock's wait test on a loaded host.
2. **The constraints.** T35's line (the timing taken from what the test measures - an event, a count, an injected clock - never a
   bare wall-clock bound; red first under induced load; still red with the behavior broken); the run lock's behavior in a run
   unchanged (`L7R_RUST_LOCK_CEILING` still seconds of the wall clock); 100% line coverage of the rustc crate by its own tests.
3. **Where each comes from.** O: T12's `make static` log, observed 2026-11-20, method: the failing assertion's one line; O: T20's
   finding that a wall-clock bound fails under load even with headroom (`tests/hooks/test-land-tooling.sh` case 2b's comment); O: the
   induced loads above, measured 2026-11-20 (`/tmp/t35/`).
4. **Do they describe the world here?** The old test failed 10 of 10 sharing a core with 16 busy loops, measured 2026-11-20
   (`/tmp/t35/old5-*.log`), the same assertion and the same one line as T12's log.
5. **The order.** Independent of the other lanes; its land-tooling half is T20's.
6. **The exits.** Green: the new test 5 of 5 under the load that failed the old one 10 of 10, red with the behavior broken, `make
   rust-test` on the crate, its lint, format and cover, `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The crate's other wall-clock waits were read: `two_runs_in_one_target_directory_take_turns` (a 60 s
   ceiling against two 0.1 s fake cargo calls, read 2026-11-20 from the test, measured 2026-11-20 (its `taker` and `OVERLAP`)) and `a_refusal_is_the_checks_reply...` (asserts a refusal only, which more load makes
   no less certain); both stayed green 5 runs of 5 on the shared core, measured 2026-11-20 (`/tmp/t35/all-pinned.log`).
8. **The budget.** One landing.
9. **Done, measured.** The new test 5 passed of 5 on the shared core, measured 2026-11-20 (`/tmp/t35/new-pinned.log`).
10. **Before moving a constant.** n/a - no constant moved (`CEILING_S`, `SAY_EVERY`, `POLL` as they were).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; the finding it breaks is a red gate on correct work (T12's `make static`).

**Found and left?** none.

**Performance work?** yes - a `[perf]` task in FR-013's sense: a gate turned red on correct work costs a builder a rerun of `make
static`. Not filed with `PERF=1`: no engine stage's counted operations or time.


<!-- plan-archive: archived 2026-11-20 -->
### T37 (the plan-review bundle cut a decision at its list: `spec-cited.md` stopped D16 at "Two things make the comparison real:" and D15 at its colon, so the reviewer judged each without its bullets, observed 2026-11-20, method: T19's and T17's plan reviews and T18's bundle rebuilt, `/tmp/t37-before/T18/spec-cited.md`)

- **Approach**: the one writer of a cited text is `paragraphs` in `rust/gate/crates/plan/src/plan/bundle.rs`, which `build` (this
  feature's decisions), `foreign` (another feature's decisions and requirements) and `requirements` (the bulleted requirements) share;
  it ended each match at the first blank line, which is where a decision's list begins. Now each match runs to the next match or the
  next heading; one written as a list item (a bulleted requirement or decision) stops sooner, at a blank line its own indented lines
  do not follow (`item_end`), so an item keeps its nested table or list and no longer takes a heading with no blank line before it.
  A requirement written as a heading is read as before, to the next heading. `spec-cited.md` has no size cap, today or after, and none is added.
  - the writer's two limits are untouched, read 2026-11-20 (`bundle.rs`): `TOO_LONG` bounds a written-out id range, the name's character limit the directory.
  - red first, the tests before the code: 2 failed of 153 (`a_decision_is_carried_whole_with_its_lists` on the fixture `bundle/fixtures/451-d14-d17.md`, this plan's decisions from the knobs' to the shards' verbatim at 07cc8f2cd1, D15 missing "Both ids name an OPEN task"; `a_list_item_runs_on_into_its_indented_lines_only`, a requirement cut before its table), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t37-red.log`).
  - green: 153 of 153, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t37-green.log`); the crate's format, lint and cover clean, measured 2026-11-20 (`l7r-gate.sh rust format|lint|cover --crate rust/gate/crates/plan`, `/tmp/t37-lfc.log`).
  - the real bundle: T18's (`plan decide 451 T18`, which cites D16) `spec-cited.md` 2,078 to 2,999 bytes and the whole bundle 13,783 to 14,704 bytes (+6.7%), D16's bullets and its `QUICK_OK` line now in it, measured 2026-11-20 (`wc -c` over `/tmp/l7r-check/plan-451-time-retro-and-efficiency-T18/` before and after).
  - every plan: 141 of 1,310 decisions grow, their text 829,259 to 875,706 characters over all of them (+5.6%), measured 2026-11-20 (a Python reading of both rules over `specs/*/plan.md` + `plan-done.md`, `/tmp/t37-scripts/survey.py`).
  - the largest, 6,648 characters (a decision of feature 317 with seven bullets), measured 2026-11-20 (the same reading).
  - D15 257 to 2,666 characters and D16 583 to 1,504, measured 2026-11-20 (the same reading).
  - 38 of 4,658 bulleted requirements change, measured 2026-11-20 (the same reading over `specs/*/spec.md`, `/tmp/t37-scripts/fr.py`).
  - every decision or requirement that shrinks loses only a heading line the old cut carried (43 decisions, of features 383, 385, 405, 415, 417, 420, 429 and 433, and 3 requirements, of 179 and 383), measured 2026-11-20 (the same reading: each shrunk text is the old one less a tail holding a heading line).
  - no new text holds an odd number of code-fence lines, so no heading stop falls inside a fenced block: 0 of 5,968, measured 2026-11-20 (the same reading).
  - observed 2026-11-20, method: every writer of a cited text found by reading `bundle.rs`'s callers of `DECISION`, `ITEM` and `paragraphs` and grepping `rust/gate/crates` for `paragraphs(` and the decision pattern - `paragraphs` is the one; the arbiter's `marks.rs` names a decision only as a verdict's subject.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a cited decision or requirement carried whole | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T37 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a plan reviewer reads every decision and requirement the blocks cite whole, its lists and tables included, so it asks no round for the text.
2. **The constraints.** T37's line (every cited decision carried whole, its lists included; red first on D15 and D16); the lean plan bundle of feature 375's amendment 11 (the bundle stays the cited text, not the plan); 100% line coverage of the plan crate by its own tests.
3. **Where each comes from.** O: T19's plan review (D16 cut) and T17's (D15 cut), observed 2026-11-20, method: their reviews' asks; O: T18's bundle before the fix, measured 2026-11-20 (`/tmp/t37-before/T18/spec-cited.md` ending at "Two things make the comparison real:").
4. **Do they describe the world here?** Yes: every decision of this plan is a bold paragraph, its bullets after a blank line, read 2026-11-20 (plan.md's Decisions); the grown decisions read as their own text (bullets, a table, a decision's layers), read 2026-11-20 (`/tmp/t37-scripts/survey.py`).
5. **The order.** Independent of the other lanes; beside T39 (another crate, `rustc`).
6. **The exits.** Green: the two red tests green, `make rust-test` on the plan crate, its lint, format and cover, `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - one writer, its three callers read 2026-11-20 (the grep above).
8. **The budget.** One landing.
9. **Done, measured.** T18's rebuilt bundle carries D16 whole, both bullets and `QUICK_OK`, measured 2026-11-20 (`grep` over its `spec-cited.md`).
10. **Before moving a constant.** n/a - no constant moves; no cap is added.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a plan reviewer no longer judges a decision cut at its colon, nor reads a heading carried under a requirement as its text.

**Found and left?**
- A bulleted requirement or decision with no blank line before the next heading carried that heading into the bundle (43 decisions and 3 requirements), a reviewer reading a heading as a requirement's text: fixed here (`item_end` and the heading stop, pinned by `a_list_item_runs_on_into_its_indented_lines_only`).

**Performance work?** yes - a `[perf]` task in FR-013's sense: a decision cut at its list costs a plan review a round to ask for it (T17's and T19's). Not an engine stage: no counted operations, no performance checklist.

<!-- plan-archive: archived 2026-11-20 -->
### T39 (a FRESH=1 run queued behind the target-directory lock might replay the holder's kept result: T32's two `make rust-test CRATE=rust/guard FRESH=1` runs both said "finished in 4.21s", found by T32, observed 2026-11-20, method: T32's transcript, `/tmp/t32-final-plain.log` and `/tmp/t32-final-exported.log` at 17:30-17:31 UTC)

- **Approach**: measure, then close. **Not a defect**: a FRESH run that waits on the lock runs its own tests. Nothing changes in
  the code; the claim "a waiter replays the holder's result" is withdrawn (constitution XIV).
  - Two FRESH runs started together each ran both guard test binaries once, the second after the first ended (run1 at
    +0.30-2.94 s, run2 at +5.81-8.33 s from the start, libtest 2.60 s and 2.48 s), measured 2026-11-20 (cargo's target runner
    `CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUNNER` set to a script logging each test-binary execution, `/tmp/t39/execs.log`, since
    `strace` is refused here with no `CAP_SYS_PTRACE`).
  - The second run printed the lock's waiting line ("waiting 0 s for the target directory, held by" the first run's pid),
    measured 2026-11-20 (`/tmp/t39/run2.log`).
  - Three FRESH runs started together made 6 executions, 2 a run, one run at a time, libtest 2.46 s, 2.49 s and 2.70 s, measured
    2026-11-20 (the same runner log).
  - A non-FRESH run after them said `test unchanged on rust/guard - its last green result stands` and printed no `test result:`
    line, measured 2026-11-20 (`/tmp/t39/control.log`). The runner sees only what cargo launches, so this control rests on that
    stdout line, not on the empty runner log.
  - T32's own incident: the guard's `Phase` rows show two separate builds and two test runs, 17:30:29.095-17:30:34.279 and
    17:31:00.858-17:31:06.044 UTC (5.18 s and 5.19 s), one per run, measured 2026-11-20 (the `Phase` rows of
    `.git/l7r-events/451-time-retro-and-efficiency.jsonl`, where a `test` row is written only by `stepped` or `side::run_built`,
    which execute, never on the "stands" path, read 2026-11-20 in `rustc.rs`).
  - The code agrees. `locked_dispatch` takes the lock before `answer` asks any kept result. `runlock.rs` holds membership only, no
    result. `Verdict::ask` returns "does not stand" on `world.no_reuse` (`L7R_RUST_FRESH`) before it compares any kept key
    (`kept.rs`). The kept store holds keys, never output (`keep_line`). Read 2026-11-20.
  - So a `finished in` line comes only from a binary that ran. libtest's `finished in` is the first binary's own wall time, and it
    varies a lot between runs that all ran, 2.46-4.21 s over runs whose test phase spans 5.14-5.19 s, measured 2026-11-20 (the runs
    above, T32's logs and the `Phase` rows). The two 4.21 s values matching to the hundredth is unexplained (a GUESS: chance under
    the sweep's load). It is no sign of replay, since both runs executed.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the measurement (no code change) | n/a - no map, no code | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T39 Approach (checklist part A)

1. **The goal, in the world.** A `FRESH=1` run always executes its crates' tests, even when it waits behind another run's lock, and reports its own result. Measured 2026-11-20: it already does (runner log `/tmp/t39/execs.log`, 2 executions per run in 5 of 5 FRESH runs).
2. **The constraints.** Feature 451 T23 (the run lock) and 449 T93 (kept results, `FRESH=1` "every crate fresh"); constitution XIV (a defect is a wrong outcome).
3. **Where each comes from.** O: T32's two 4.21 s lines, observed 2026-11-20 (T32's transcript); O: the runner log, measured 2026-11-20 (`/tmp/t39/execs.log`); O: the `Phase` rows of T32's two runs, measured 2026-11-20 (`.git/l7r-events/451-time-retro-and-efficiency.jsonl`); R: `rustc.rs`, `runlock.rs`, `kept.rs`, read 2026-11-20.
4. **Do they describe the world here?** Yes. The concurrent runs went through the lock's wait, its waiting line in 3 of 5 runs' stderr, measured 2026-11-20 (`/tmp/t39/run2.log`, `run3.log`, `run4.log`). This is the path T32 saw, whose run waited 0 s and then 30 s, measured 2026-11-20 (the waiting lines in T32's transcript).
5. **The order.** After T23 (the lock) and T32 (the finding); no task waits on this one.
6. **The exits.** Green: every FRESH run, waiter or holder, logs its own test-binary executions, measured 2026-11-20 (2 runs then 3 runs together, 10 executions, `/tmp/t39/execs.log`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The matching 4.21 s figures were the only signal, and the `Phase` rows show two executions behind them, measured 2026-11-20 (`Phase` rows at 17:30:29 and 17:31:00 UTC).
8. **The budget.** One landing.
9. **Done, measured.** Not a defect: 5 of 5 concurrent FRESH runs executed both guard test binaries (10 of 10 executions, one run at a time), measured 2026-11-20 (cargo target-runner log, `/tmp/t39/execs.log`). T32's two runs each wrote their own build and test `Phase` rows, measured 2026-11-20 (the 451 event log).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: not a defect. No run reported green without running, measured 2026-11-20 (the runner log and the `Phase` rows). The task's claim is restated: a waiter takes the holder's kept result only when it is not FRESH and its key matches, which is the kept-result design (449 T93). A FRESH waiter runs. Existing pin: `a_moved_binary_or_a_failed_build_runs_and_a_fresh_run_runs_every_crate` (`rust/gate/crates/rustc/src/rustc/tests/kept.rs`), where a fresh run over kept green results runs all 5 crates, measured 2026-11-20 (read in the test's `test_runs(&fresh)` assertion).

**Found and left?**
- The rust-checks summary line quotes only the first `test result:` line of a crate's `cargo test`, so the guard's second test binary's result is not shown, observed 2026-11-20 (`/tmp/t39/run1.log` against the 2 executions in `/tmp/t39/execs.log`). Not a defect: a failure in any binary turns the crate's code and prints cargo's full output, so no wrong outcome.
- The matching hundredths (4.21 s twice): not a defect, unexplained (GUESS: chance under load); both runs executed, measured 2026-11-20 (the `Phase` rows).

**Performance work?** yes (a `[perf]` task, 451 FR-013: it asked whether a builder's FRESH run could report green without running). It closes with no change; not engine speed.


<!-- plan-archive: archived 2026-11-20 -->
### T34 (found by T14, 2026-11-20: four builders formatted with a bare `rustfmt` outside make, because `make format` rewrites every crate and another builder's in-progress files with them)

- **Approach**: `make format FILE=<path>` (several: `FILE="a.rs b.rs"`) formats only the files named, `make format CRATE=<dir>` only that crate; bare `make format` is unchanged. The Makefile hands `--file` and `--crate` to `l7r-gate rust format` (`rust/gate/crates/rustc/src/rustc.rs`); the one-file path is `rustc/fmtfile.rs`, the toolchain's rustfmt (`~/.cargo/bin/rustfmt`, `cargo_exe`'s rule) fed the file on standard input, run from the file's directory (where rustfmt finds a `rustfmt.toml`, as `cargo fmt` does), `--edition` the owning crate's `Cargo.toml` literal (2015, cargo's default, where it names none; a non-literal refused), the file written only where rustfmt passed and changed it. Standard input, not a path: measured 2026-11-20 (a scratch crate whose `main.rs` declared `mod k;`, rustfmt 1.8.0-stable): `rustfmt --edition 2021 main.rs` rewrote `k.rs`, the same file on standard input left `k.rs` byte for byte. It builds nothing, so it takes no run lock and never waits on another run's tests. `FILE=` with `CRATE=` is refused (exit 2); the `format` failure's tip names `CRATE=` and `FILE=` instead of bare `make format`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `make format FILE=` / `CRATE=` | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T34 Approach (checklist part A)

1. **The goal, in the world.** A builder formats its own file, or its own crate, through make, and nothing of another builder's in-progress work moves.
2. **The constraints.** T34's line in tasks.md (FILE= or CRATE= formats only what it names, red first); feature 449's make-only rule (`dev/rust-tooling.md`: the crates are formatted through make); the gate crates' 100% line coverage; `make format` alone unchanged.
3. **Where each comes from.** O: T14's finding, four builders on 2026-11-20 formatting with bare rustfmt; O: the children measurement above; R: `dev/rust-tooling.md` "format"; G: none beyond the task line.
4. **Do they describe the world here?** Yes, measured 2026-11-20 (`make -n format FILE=rust/gate/crates/rustc/src/rustc.rs`): the recipe before the change was `l7r-gate.sh rust format` with no file word, so a FILE= run formatted all 33 crates under `rust/` (measured 2026-11-20, `find rust -name Cargo.toml` holding `[package]`).
5. **The order.** After T17 (the deferral form below); beside T31 (rust/guard, untouched here).
6. **The exits.** Green: the new tests pass, the crate's lint, format and cover clean (every line, the crates' floor), `make quick`, `make static`, `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one read of the format step (`check`'s `cargo fmt --manifest-path`) and one scratch measurement settled the design.
8. **The budget.** One landing.
9. **Done, measured.** Red first, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/rustc` with `tests/fmtfile.rs` written before `fmtfile.rs`): 7 of 75 failed, among them `a_file_run_formats_that_file_alone_with_its_crates_edition`, which asserts another crate's unformatted file and the named file's own `mod` child keep their bytes; green, measured 2026-11-20 (the same command): 78 passed. On the real tree, measured 2026-11-20 (`make format FILE=rust/gate/crates/rustc/src/rustc.rs`, wall clock): 0.06 s, its unformatted child `rustc/fmtfile.rs` and every other file byte for byte (sha1 of `git status --porcelain`, of `git diff -- rust/guard` and of the child, before and after), and `make format CRATE=rust/gate/crates/rustc` ran in 1.15 s, `rust/guard`'s diff unchanged, measured 2026-11-20 (wall clock, the same sha1s), after the FILE= runs `l7r-gate rust format --check --crate rust/gate/crates/rustc` was clean, so the one-file path formats as `cargo fmt` does, measured 2026-11-20 (that command).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a - no room.
12. **Before any fix.** A builder sees `make format FILE=` and `CRATE=` in `make help` and the failure tip, and the wrong outcome it fixes is another builder's in-progress files rewritten by a whole-tree format; no map changes.

**Found and left?**
- The make-only guard does not refuse a bare `rustfmt` (T34's line; four builders on 2026-11-20), and its block message advertises bare `make format`, which rewrites every crate. Not fixed here: the guard is `rust/guard`, where T31's builder works now, and the class is T33's (a held write through a route the guard does not read). Filed as T33; lands before T22.

**Performance work?** Yes (a `[perf]` task, 451 FR-013: the builders' loop) - a one-file format in 0.06 s, measured 2026-11-20 (wall clock of `make format FILE=rust/gate/crates/rustc/src/rustc.rs`), where a whole-tree format ran rustfmt over 33 crates and waited on the run lock; not an engine-speed task, so no performance checklist.

<!-- plan-archive: T35 to T20 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T35 to T35 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-20 -->
### T31 (found by T15's corpus replay, 2026-11-20: main-tree refused `python3 -c "data = open('$SP/x.html','rb').read() ..."` - a read - as a write where the shell stands, with no escape, the same before and after T15's shared-reader fix; observed 2026-11-20, method: T15's replay of the main-tree refusals corpus)

- **Approach**: the cause is feature 204's D5, `rust/guard/src/shared/tree.rs` `writes_in` reading every `python3 -c` as a write where the
  shell stands. D5 (feature 204 spec): *"`python3 -c` remains a write. It was a false positive on read-only diagnostics, but its cost is
  now zero: from the clone it is allowed; from main it is moved. Narrowing the write list would reopen the false-allow direction for no
  saving."* Its "zero cost" fails where the clone cannot be resolved: the move becomes the refusal `clone-unresolved`. And a read moved
  to the clone is still a model-visible rewrite. Refusing a read is a wrong outcome (constitution XIV; the session's ruling,
  2026-11-20), so D5 is NARROWED here: a `-c` program that a denylist of known writers judges read-only is not a write, unless the
  same command also runs a Python program from stdin.
  - `shared/tree/py_c.rs` (new): `reads(body, quote, dir)` judges a program a read only when no known writer appears in it (a
    DENYLIST of calls and modules: `write`, `remove`, `shutil`, `subprocess`, `.dump(`, `save*(`, `getattr(`, `urlretrieve`, ...;
    `replace(` only with `os`/`Path` in the program); every `open(` is in a read mode (no `*`/`**` argument, no non-literal mode);
    no command substitution, and no shell expansion outside a Python literal (a `#` comment's quotes opening none), in a
    double-quoted body; no relative import; and no import that the directory it runs in could answer (the tree's own code, which
    can write anything), with any import a write where the directory is unknown. Anything else stays D5's write.
  - `tree.rs`: `sanitize` carries each `-c` program out beside the text, `__py_c_<n>__` standing in its place, so the program's own
    `;`, `(` and `|` do not split the walk. `writes_in` finds the `-c` past the interpreter's flags (`python3 -I -c`, `-Ic`,
    `-W x -c`) and a minor version (`python3.12`), and keeps a read program in the walk as a target MARKED `how = "read"`. `judge`'s
    write tests and its re-judge (`lands_in_main`) skip that mark, so house style still sees where the command lands, as before.
    `walk` marks no `-c` a read where any segment of the command runs Python from stdin (`python3 -`, `python3 <<BODY`,
    `python3 < p.py`, `| python3`; `python_stdin`): the walk judges no stdin program, and D5's write of the `-c` beside it was what
    refused the heredoc writers parse#72 and window#61. The heredoc itself gets no target, and a `-c` program's own stdin is data.
  - `gm_tree_hooks.rs` `offending` skips the mark too, so a read standing in gm-assistant's tree is no longer refused.
  - red first, the tests before the code, each in `/tmp/t31/`, all `make rust-test CRATE=rust/guard`, 2026-11-20:
    - the read refused: 673 passed, 1 failed (`red-first.log`);
    - the classifier's gaps: 15 of 18 new write cases judged reads (`red3.log`);
    - gm-tree refusing a read: 676 passed, 1 failed (`gmred.log`);
    - the stdin rule and the comment: 674 passed, 3 failed (`red4.log`) - window#61's shape allowed by main-tree with no clone,
      the walk's stdin cases marked `read`, `# don't\n$CODE` judged a read; parse#72 and window#61 themselves allowed by the
      stage-1 binary's replay (`after1.nobody.main-tree-hooks.tsv`) and refused by the final one (`after3`);
    - green: 677 of 677 (`green4.log`); 678 of 678 once the walk's Python cases became their own test, for its length
      (`final-test.log`).
  - replays (the four corpora, 1,134 rows, measured 2026-11-20 (`/tmp/t31/scripts/replay.sh`); before = HEAD's binary, after =
    the final one; SID `t` resolves a clone, `nobody` resolves none):
    - house-style, gm-tree, make-only alone (`t`), gm-tree alone (`nobody`): 0 moved, 0 outputs changed each, measured 2026-11-20 (`replay.sh`, `cmp.sh`);
    - main-tree alone, measured 2026-11-20 (`replay.sh`, `cmp.sh`), `nobody`: 80 refused -> allowed; `t`: 79 rewrote -> allowed and window#308 refused -> allowed; 0 other
      outputs changed;
    - all guards, measured 2026-11-20 (`replay.sh`, `cmp.sh`), `t`: 79 rewrote -> allowed and window#308 refused -> allowed; `nobody`: 80 refused -> allowed; a second `t` run
      0 differences (no noise);
    - against the stage-1 binary (no stdin rule), measured 2026-11-20 (`cmp.sh` after1 vs after3): exactly 5 moved back - parse#72, window#61 (heredoc writers), main-tree#147,
      window#339, window#361 (heredoc reads beside a `-c` read) - the same 5 an independent scan of the 85 stage-1 moves for a
      stdin Python program predicted. Under all guards window#61 stays refused by guard-file-hooks and its output is back to
      HEAD's.
    - the final source rebuilt and all eight runs replayed again, measured 2026-11-20 (`cmp.sh` against the previous build's):
      0 verdicts and 0 outputs changed.
  - fixture: `tests/hooks/fixtures/main-tree-refusals-2026-09.json` relabeled, measured 2026-11-20 (its verdicts against the
    main-tree replay, `t`), 57 rows rewrote -> allowed (expected 167 allowed, 6
    rewrote), exactly the replay's main-tree# moves; main-tree#147 stays rewrote.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a `python3 -c` read is no write (main-tree, gm-tree) | n/a - no map | n/a | none | n/a |

### T31 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A builder's read-only `python3 -c` diagnostic standing in the mirror or in
   gm-assistant's tree runs as typed: it is neither refused nor rewritten. Every write is still moved or refused as before.
2. **The constraints.** T31's line (measure on the corpora, fix the refusal of correct work, red first); feature 204 D5, quoted above
   and narrowed here (a read judged by a denylist of known writers is no write, unless the command also runs a stdin program); D6
   (unknown resolves toward main) untouched; the guards that read a walk's targets (house style, gm-tree, the bench) see the same
   targets; 100% line coverage of the guard crate.
3. **Where each comes from.** G: the session's ruling, 2026-11-20 - refusing a read is a wrong outcome (constitution XIV), so
   narrowing D5 is right, and the stdin rule's cost (3 reads refused again) is within D5's scope as the session set it. R: feature
   204 spec D5 and D6. O: the replays above, measured 2026-11-20.
4. **Do they describe the world here?** Measured on the four corpora by replay, and each moved row hand-read as a WHOLE command,
   not its `-c` program alone: every head of every segment listed (`/tmp/t31/scripts/heads.py`) and each one that is not a known
   read judged. That read found the two heredoc writers (parse#72, window#61) the `-c` write had been covering, measured 2026-11-20 (`heads.py`
   and a hand-read). The `curl -o`
   writes the walk does not judge were measured 2026-11-20 (a hand-read of the moved rows) at 0 rows to cover: their targets
   (main-tree#112, #122; window#416 has none) are absolute scratch paths outside the mirror. The script runs were measured
   2026-11-20 (the same hand-read) at 4 rows left under the walk's standing policy that a script run is no write (`python3 x.py`
   pinned empty), not shown to write nothing: main-tree#103 runs a scratch script, window#60, #62 and #308 run the mirror's own
   test suites and hooks, and in each the `-c` write was the only thing that moved or refused it, so each now runs as typed.
5. **The order.** After T15 (its replay found this); beside T33 (the guard-file guard, a different file).
6. **The exits.** Green: the red tests green; the replays; `make rust-test CRATE=rust/guard` and the crate's lint, format and cover;
   `make quick`; `make static` (once); `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be
   done ruled through `make arbiter-ask`.
7. **The search smell.** Every reader of a walk's targets was found: `judge` (`named`/`shell`, and the re-judge), `explain`
   (`named` only), `Verdict::context` (logs `how`), `gm_tree_hooks::offending`, `house_style_hooks::lands_outside` (paths only) and
   `suite_tools/bench.rs` (paths only); no script or test reads the logged `how`. Read 2026-11-20 (`grep '\.targets\|\.how'` over
   `rust/guard/src`, `grep '"how"'` over `scripts/ tests/ Makefile`).
8. **The budget.** One landing.
9. **Done, measured.** The read refused with no clone is allowed (`red-first.log` -> `green4.log`); 80 corpus rows refused with no
   clone and 79 rewritten with one now run as typed, every move accounted above; 0 moves on the other guards alone; the heredoc
   writers parse#72 and window#61 refused as before.
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. The fix is not a restatement: refusing a read is the wrong outcome (constitution XIV), so
    D5's claim *"python3 -c remains a write"* is narrowed in the code, the session ruling it. A builder sees its read run where it
    was refused (`clone-unresolved`) or rewritten into the clone. The narrowing stops where the walk stops seeing: a command that
    also runs a Python program from stdin keeps its `-c` a write, because the walk judges no stdin program and D5's write was the
    only thing refusing such a heredoc's writes in the mirror (parse#72, window#61); its cost is 3 heredoc reads refused or
    rewritten again (main-tree#147, window#339, window#361), as before T31.

**Found and left?**
- The stdin rule keeps three real reads refused or rewritten: main-tree#147, window#339 and window#361 (each runs a `-c` read beside
  a stdin Python program that only reads), observed 2026-11-20, method: the replays of item 9, the rows that moved back against the
  earlier build, each hand-read. Not fixed here: telling those programs' bodies from a writer's needs the stdin reader T31 does not
  build, and lifting the rule without it lets parse#72's and window#61's writes through. Filed as T42 (which retires the rule once
  stdin bodies are judged); lands before T22.
- A Python heredoc (or other stdin program) that writes, standing in the mirror, is judged by no one: measured 2026-11-20
  (`heredoc_writers.py` over the replays), in the four corpora 331 rows
  run a stdin Python program whose body holds a known writer standing in the mirror; main-tree with no clone resolvable allows 301
  of them before and after T31 and refuses 30 (28 for another write in the command, parse#72 and window#61 by T31's
  stdin rule); of the 301, 85 have no `cd` in the command and 42 of those name a
  relative path. Not fixed here: judging a heredoc body is a new reader with its own replay and moves, past T31's `-c` scope, and
  T31's stdin rule keeps every row it refused before refused. Filed as T42; lands before T22. observed 2026-11-20, method: every
  corpus row's heredocs after a `python3` scanned for a known writer (`/tmp/t31/scripts/heredoc_writers.py`) against the before and
  after main-tree replays.

**Performance work?** yes - a `[perf]` task in FR-013's sense (the builders' loop): each refused or rewritten read cost a model
round trip; the corpora hold 80 such refusals and 79 such rewrites. Not filed with `PERF=1`: no engine stage's counted operations
or time.


<!-- plan-archive: T32 to T14 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T32 to T32 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-20 -->
### T40 (T21's finding: `make hooks-test`'s full-run wall is entry-gate's suite plus 2-3 s, measured 2026-11-20 (T21's full runs), its case-4 chain of record gates the last thing running)

- **Approach**: measured first, then two cuts in `tests/hooks/test-entry-gate.sh` alone; no gate command's code changed.
  - **Where the chain's time goes.** Case 4 (`case_answers`) is one clone and six computations of the tree's owed units, one after
    another: the listing `answer_all` reads, its three `--answer` calls (quote-check, record-format, modal-research), and two gates.
    Alone, the clone took 1.66-1.70 s (0.79 user, 0.87 sys) and each computation 1.40-1.64 s of wall and 2.4-3.4 CPU-seconds, the first on a
    fresh clone 2.1 s, measured 2026-11-20 (`/usr/bin/time` and `EPOCHREALTIME` around each, a scratch clone of HEAD with case 3's reword, load 0.6-14).
    Of a computation, 0.63-1.13 s is one `git cat-file --batch` of 1,951 base blobs (the record's pages at the merge base, read whole for a one-page
    delta), the rest the binary's own work, measured 2026-11-20 (a `git` shim first on PATH timing each call and teeing `cat-file`'s input).
    A gate run is one `entry-gate.sh`, three launcher and binary pairs (`push-gate skip` 0.30 s, its unscoped `git diff --name-only HEAD`
    0.24 s of it, `record-owed --unanswered`, `log guard`) and 23 git processes, measured 2026-11-20 (`bash -x` with `EPOCHREALTIME` in PS4, the shim).
    What repeats: the owed units, computed six times on states that differ by one sentence, each reading the same 1,951 base blobs again,
    and a checkout of all 28,472 tracked files when the gate reads the record's pages and the pop-ups' files.
    Under a full run's load the same steps stretch: the clone 6.7-17.5 s, `answer_all` 28.5-32.0 s, a gate 12.6-21.1 s, measured
    2026-11-20 (the suite's steps timed by a `tick` line in an instrumented copy, run alone at load 22-43, the host loaded by other builders' replays and builds).
    No profiler reaches the binary here (`perf` opens no event and `strace` cannot attach in this container, observed 2026-11-20), so the binary's
    own share is read from the git calls' gaps.
  - **Cut 1, the answers side by side.** The three `--answer` calls write different units' records (one file a unit in the answers'
    store; the dispatch state they touch is taken under its lock), so `answer_all` starts them together and waits: the chain's six computations
    in series become four. This moves work, it removes none.
  - **Cut 2, a sparse clone.** `fixture` clones with `--no-checkout` and checks out `research/questions`, `research/sources` and
    `l7r/diagram/interactive` (cone mode, so the top-level files too), 8,499 of the 28,472 tracked files: 0.59-0.61 s against 1.61-1.67 s alone, measured
    2026-11-20 (`/usr/bin/time`, four alternated pairs of a full and a sparse clone of the clone, load 2.6-2.8), and a smaller index for every gate's `git diff` and `git status`. Held to the full clone's behavior: both clones driven through the
    eight states the suite drives (clean, comment, reword, `ENTRY_DRIFT_OK`, answered, stale, `RECORD_CHECKS_OK`, restored), the gate's output and
    exit code and `record-owed`'s listings diffed, identical, 175 lines each, measured 2026-11-20 (a script driving both). Case 7 counts the bypass
    records under `dev/bypass-log/`, absent from the sparse clone, so its `find` now says nothing when the folder is not there; the count is
    still the before and after of one gate.
  - **Rejected, measured.** A single-pack shallow clone (`--depth 1`): 6.96 s and 14.3 CPU-seconds to make, and a computation on it 1.45 s
    against 1.44 s on the plain clone, measured 2026-11-20 (`/usr/bin/time`, the same delta) - the base reads cost the same in one pack or 38.
    A fixture shared by the two cases: each edits its own page in place and the clone is under a second, so a copy saves nothing a sparse
    clone does not.
  - **Kept the same.** Every case, every assertion, the cases' order and the two parts; still red where its behavior breaks: with
    `entry-gate.sh` asking `record-owed` without `--unanswered` (answers ignored), the new suite fails `answered units ship` (12 passed,
    1 failed), measured 2026-11-20 (a scratch clone with that one-line change and the new suite).
  - **The wall.** Two scratch clones of HEAD c71c168ebe, `after` carrying the new suite, `make hooks-test HOOKS_ALL=1` alternated, HOOKS_JOBS 8,
    `L7R_MODEL_CACHE` set (a clone has no model cache of its own).
    Before 43.8 and 44.0 s, entry-gate's suite 39.7 and 41.9 s, measured 2026-11-20 (`EPOCHREALTIME` around make, each run's "ran" line, load 19.7 and 16.0 at their starts).
    After 44.4 and 44.2 s, entry-gate's suite 32.4 and 34.2 s, measured 2026-11-20 (the same method, load 16.8 and 15.1 at their starts, `after` dirty in the suite and `before` clean).
    A third pair, 52.2 s and 72.5 s, overlapped another builder's replays and is dropped, measured 2026-11-20 (the same method).
    So the suite fell about 7.5 s and the wall did not move, sync-with-main's suite the longest at 33.7 and 35.7 s and the wall ending 8-11 s after it, measured 2026-11-20 (the same runs).
  - **The equal-dirt pair** settles that confound: both scratch suites carry the same inert `tick` lines, run before, after, after,
    before, `/usr/bin/time` around make, each suite's end read from its `.git/hooks-test/<suite>.s` mtime against make's start.
    Before 41.3 s and 491 CPU-seconds at load 17.1, entry-gate's suite 39.2 s ending at 40.3 s, measured 2026-11-20 (`/tmp/t40/s2/run.sh`).
    Before again 62.3 s and 729 CPU-seconds at load 20.4, the suite 59.1 s ending at 61.0 s, measured 2026-11-20 (the same script).
    After 37.0 s and 461 CPU-seconds at load 12.0, the suite 27.7 s ending at 28.8 s, sync-with-main 27.3 s ending at 28.4 s, the last suite ending at 35.6 s, measured 2026-11-20 (the same script).
    After again 55.0 s and 634 CPU-seconds at load 14.2, sync-with-main 39.0 s ending at 40.0 s, the suite 36.5 s ending at 37.5 s, the last suite ending at 52.6 s, measured 2026-11-20 (the same script).
    So the chain no longer sets the full run's wall: before, the wall was the suite's end plus 1 s, and after, the short suites dealt last end 7-15 s past it, the wall the run's whole work over its eight jobs, measured 2026-11-20 (the four runs above).
    The walls' 4.3 and 7.3 s are not read as a saving, the loads differing by 3-5 between the pair's runs, measured 2026-11-20 (the same runs).
  - **The incremental run, the common case** (the session's ruling: keep the cuts if the suite is measurably faster alone and in an
    incremental run that reruns it). Each run appends a comment line to `scripts/gates/entry-gate.sh` in its scratch clone and runs
    `make hooks-test`, which reruns entry-gate's suite, l7r-gate's three shards and sync-with-main's, alternated before, after, after,
    before, twice.
    Before 29.4, 24.5, 24.2 and 23.5 s, entry-gate's suite 27.6, 23.0, 22.7 and 22.0 s, measured 2026-11-20 (the same script, load 9.9-20.1).
    After 23.5, 21.5, 20.9 and 21.3 s, the suite 21.8, 20.0, 19.4 and 19.8 s, measured 2026-11-20 (the same script and loads).
    The wall is the suite's end plus 0.4-0.5 s in every run, so here the suite still sets it, and each back-to-back pair fell 2.2-5.9 s, about 3 s at the lower loads, measured 2026-11-20 (the eight runs).
    CPU-seconds did not fall, 158-182 before and 171-190 after, system time down about 3 s and user time up about 12 s, measured 2026-11-20 (`/usr/bin/time`).
  - **Alone.** The old and new suites alternated (old, new, new, old, twice).
    Old 13.3, 15.1, 15.5 and 16.9 s, new 10.5, 11.7, 12.3 and 11.4 s, CPU-seconds 41.7-48.7 against 44.0-47.6, measured 2026-11-20 (`/usr/bin/time` around `/tmp/t40/run1.sh`, load 4.5-6.8).
    One part at a time, old 22.4 and 24.9 s, case 4 12.1 and 13.3 s, the rest 9.5 and 10.8 s, measured 2026-11-20 (`PARTS_MAX=1`, alternated, each case's first and last `tick`, load 2.6-3.3).
    New 17.7 and 17.4 s, case 4 9.6 and 9.3 s, the rest 7.8 and 7.8 s, so `WEIGHT` is now 9 and 8, measured 2026-11-20 (the same method).
    The landed suite passes 13 of 13 at `PARTS_MAX=1` in 16.6 s and at `PARTS_MAX=2` in 9.5 s, measured 2026-11-20 (`tests/hooks/test-entry-gate.sh` run alone).
    So the cuts save about 3.7 s of wall alone and about 3 s in an incremental run, and no CPU, measured 2026-11-20 (the figures above).
    The sparse clone's system time saved is spent again as user time, likely the three computations sharing the cores (a GUESS, unmeasured: no profiler here).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the answers side by side, a sparse clone | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T40 Approach (checklist part A)

1. **The goal, in the world.** A faster `make hooks-test`: the suite measurably faster alone and in an incremental run that reruns it, the
   common case (the session's ruling, 2026-11-20, once the full run's wall proved set by other suites); no map changes.
2. **The constraints.** FR-010, FR-013; the suite checks what it checked (every case and assertion, each red when its behavior breaks); only
   the suite and this section edited (T31 works in `rust/guard`).
3. **Where each comes from.** G: improvement 5 (the GM 2026-11-19, a faster `make hooks-test`); O: T21's full-run figures and this task's step timings.
4. **Do they describe the world here?** Measured on scratch clones of HEAD, the git calls by a shim, the suite's steps by an instrumented copy, the wall back to back.
5. **The order.** After T21 (its finding); beside T31 (different files).
6. **The exits.** Green: the suite faster alone and in an incremental run that reruns it, the suite green at `PARTS_MAX` 1 and 2 and red on a broken gate. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite alone, old and new alternated; an incremental `make hooks-test` after an edit to `entry-gate.sh` and a
   full `HOOKS_ALL=1` run, on two scratch clones of HEAD equally dirty, alternated, wall and CPU-seconds by `/usr/bin/time`, each suite's end, the load noted.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a reader of a map sees; no check's verdict changes (the gate's output identical at every state). Not a defect: a speed change.

**Found and left?**
- Every computation of the owed units reads the record's pages at the merge base whole, 1,951 blobs by `git cat-file`, though a page the
  delta does not touch reads the same in the working tree: 0.63-1.13 s of each 1.4-1.6 s computation, measured 2026-11-20 (the shim's
  `cat-file` timing). Not fixed here: a change to the `owed` crate's `Delta::fetch`, outside this task's files, and it cuts every gate
  run, the push's too, not this suite alone. Filed as T43; lands before T22.
- `push-gate skip`'s `git diff --name-only HEAD` walks the whole index, 0.24 s a gate run on the full clone, observed 2026-11-20 (the shim).
  Not a defect: no wrong outcome, a cost, and not filed: a real gate pays it once a push, and this suite's sparse clone already
  shrinks the index it walks.

**Performance work?** yes - a `[perf]` task (451 FR-013: the guard suites' wall). Its answers:

1. **Where does the time go?** Into six computations of the owed units in series and a full checkout (the approach's figures).
2. **Removes work, or only moves it?** The sparse clone removes work (about 20,000 fewer files checked out and indexed per case); the answers
   side by side only move it, three computations at once where they ran in turn.
3. **What do you expect it to save, and why?** About two computations and most of a clone off the chain, 3-4 s alone and more under a full run's
   load, where each step stretched 4-10x (a GUESS from the step timings).
4. **How does the work grow with the settlement?** n/a - no settlement; with the record it grows as its pages do.
5. **What did the before and after show, and under what conditions?** The approach's figures.
   Alone 13.3-16.9 s before and 10.5-12.3 s after, measured 2026-11-20 (load 4.5-6.8).
   An incremental run after an edit to `entry-gate.sh` 23.5-29.4 s before and 20.9-23.5 s after, each pair 2.2-5.9 s faster, CPU-seconds unchanged or higher, measured 2026-11-20 (load 9.9-20.1).
   In a full run the suite fell 7.5-12 s but stopped setting the wall, now the run's whole work over eight jobs, 41.3 and 62.3 s before against 37.0 and 55.0 s after, measured 2026-11-20 (the equal-dirt pair, loads 12-20).
6. **Did any map move, and does it still keep the research?** No map.

<!-- plan-archive: archived 2026-11-20 -->
### T41 (T34's reading of `scripts/gates/l7r-gate.sh`: the launcher rebuilds `l7r-gate` when `rust/guard` changes and the gate links the guard, so one builder's uncompiling guard edit fails every other builder's gate command in a shared clone - read, not measured, until this task)

- **Approach**: measured first, then one change to the launcher's build-failure path; no gate crate changed.
  - **The measurement.** A scratch clone of the clone at d6d242ec5b in `/tmp`, its own target (a copy of the clone's `tool/` profile), every launcher arm built, then `fn t41_broken( {` appended to `rust/guard/src/shared.rs`.
    `l7r-gate.sh --version`, `make decide F=451 T=T41`, `make format FILE=...`, `make speckit-todo`, `l7r-gate.sh rust lint` and `l7r-gate.sh mode-a` each failed, exit 1 (make's 2), in 0.1-0.2 s, measured 2026-11-20 (each run timed by `date +%s.%N` in the scratch clone).
    A type error in the same file failed the same way in 0.48 s, measured 2026-11-20 (the same method).
    `browser`, `embed` and `hamlet` ran: none of them depends on `l7r_guard`, measured 2026-11-20 (`cargo tree -p <pkg> -e normal`, which finds the guard under `l7r_gate`, `l7r_gate_rustc` and `l7r_mode_a` alone).
    `L7R_GATE_STALE_OK=1` ran the old binary, as T129 means it to (the Makefile's parse-time goals line).
    Every failure printed cargo's report, `--> guard/src/shared.rs:36:18` (relative to `rust/`), and then `l7r-gate: the build failed - fix what cargo names above`: an order to edit the neighbor's file.
    A broken `rust/gate/crates/owed/src/lib.rs` (T43's crate) fails `l7r-gate` the same way in 2.7 s, and `rust lint`, whose `l7r-rust` does not link `owed`, ran clippy for 130 s to a red, measured 2026-11-20 (the same method).
    A guard edit that compiles cost the next `l7r-gate` call 2.6 s of rebuild, measured 2026-11-20 (the same method), so the compiling side is not this task's cost.
  - **The fix: the refusal names the file and what to do, and nothing falls back.** On a failed build the launcher keeps cargo's report and adds two lines: each file cargo points at, once, from the tree's root (`rust/guard/src/shared.rs`; an absolute path kept), and `yours? fix what cargo names above. Not yours? another builder in this tree is mid-edit: leave it alone and re-run once it compiles`, with the `git status` that shows the uncommitted edits. A failure naming no file keeps the old line. It holds for any uncompiling source, the guard's or a gate crate's.
  - **Why not the last good binary (the rule).** A command may run on a binary older than the tree only if it renders no verdict and writes no record a later gate or push trusts, because the old binary is behind every source newer than it - the caller's own compiling gate-crate edits too - and the gate links the guard's shared code into nearly every command (`shared::speckit`, `regex`, `log`, `checks`, `guards::house_style_hooks`, 28 modules, measured 2026-11-20 (`grep -o 'l7r_guard::...'` over `rust/gate` and `rust/mode_a`)).
    `make decide` lints a plan section and records a deferral escape that `make plan-delta` reads, so it fails the rule; so do `task-start` (its hold), every `check`, `rust lint|test|cover|dead`, `rust format --check`, `speckit-todo --check|--holding|--closed-by-status` (the push's route), `mode-a` and `hamlet` (the generation cache's engine identity).
    What passes it - `rust format` writing, a bare `speckit-todo` listing, `coord lines` - was 787 of the week's 12,700 make targets, 6%, measured 2026-11-20 (`.git/tool-usage.jsonl`, `kind: target`, 2026-11-13 to 20).
    A fallback for that 6% leaves `make decide` (449 runs) and `rust-test` (2,414 runs) failing, measured 2026-11-20 (the same log and window), and adds a path where an old binary runs, so it is not built.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the refusal names the uncompiling files and what to do | `tests/hooks/test-l7r-gate.1.sh`, "a neighbor's uncompiling file": red on the unfixed launcher (2 FAIL lines: the named files, the advice), green after, measured 2026-11-20 (the shard run in the scratch clone) | n/a: no engine code | none: no engine code | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T41 Approach (checklist part A)

1. **The goal, in the world.** A builder whose gate command fails because another builder's file does not compile is told which file and that it is not theirs to fix, and no gate verdict comes from a binary older than the code it judges.
2. **The constraints.** FR-013 (a `[perf]` task makes the builders' loop faster); the launcher fails closed (feature 449 T061); `L7R_GATE_PRINT_FRESH` names no stale binary (T205); the ground rule from the dispatch: a gate check over a changed guard uses the new code.
3. **Where each comes from.** R: tasks.md T41 and the launcher's header; O: the scratch-clone runs above.
4. **Do they describe the world here?** Yes: the failure reproduced on the real launcher with real cargo, measured 2026-11-20 (the scratch clone, a broken `shared.rs`, then a broken `owed/src/lib.rs`).
5. **The order.** After T40 (independent of T43, which edits `rust/gate/crates/owed` and not the launcher).
6. **The exits.** Green: the shard's new cases pass and the real `make decide` against a broken guard prints the two lines. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one failure path, read whole.
8. **The budget.** One landing.
9. **Done, measured.** `make decide F=451 T=T41` against the scratch clone's broken guard: exit 2 in 0.23 s with `rust/guard/src/shared.rs does not compile, so l7r-gate is not built ...` and the advice line, measured 2026-11-20 (the scratch clone, fixed launcher); the shard green, measured 2026-11-20 (`tests/hooks/test-l7r-gate.1.sh` in the scratch clone).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder reading the refusal sees the neighbor's file named and is told to leave it alone, where before it was told to fix it; no map, finding or check changes.

**Found and left?** none.

**Performance work?** yes (a `[perf]` task, 451 FR-013: the builders' loop - a builder no longer edits, reverts or debugs a neighbor's file on the launcher's word); not an engine-speed task, so no performance checklist.

<!-- plan-archive: archived 2026-11-20 -->
### T43 (T40's finding: every owed computation read the record's pages at the merge base whole, 1,951 blobs by one `git cat-file --batch` for a one-page delta, 0.63-1.13 s of each 1.4-1.6 s computation, measured 2026-11-20 (T40's `git` shim))

- **Approach**: one change in the `owed` crate's `Delta::fetch` (`rust/gate/crates/owed/src/record/delta.rs`), which every base read of the record, translation and pop-up families goes through; no caller changed but a doc comment (`owed.rs`'s `prefetch`).
  - **The rule.** A name `rev` lists that the working tree holds unchanged is read from the tree as the same bytes; every other name still goes to `cat-file`. Unchanged means: no line of the computation's cached `git diff --name-status --no-renames rev -- WATCHED` names it (the diff `changed_sources` already asks, so the common path pays no new diff), `git ls-files -v -- LISTED` does not flag it (assume-unchanged or skip-worktree, whose diff is silent whatever the file holds; one new `git` call, 6 ms on the real clone, measured 2026-11-20 (the shim below)), it is a plain file (not a link, not absent as a sparse checkout leaves it) and holds no carriage return (an end-of-line conversion could make its blob differ). It is decoded as `cat_blobs` decodes a blob (`from_utf8_lossy`, no newline conversion), so `Delta::texts(rev, names)` gives what `cat_blobs(rev:names)` gives, string for string, and every owed unit downstream is the same.
  - **Holds for any revision**, so `--between`'s two reads shrink too wherever the tree matches either side.
  - **Rejected: keying the base read by the merge base and reusing it.** It would keep state between computations, which `delta.rs` rules out (each computation's reads are its own), and still pay one full read per merge base; the tree's copies cost a file read each.
  - **Red first, on a cost counter.** `Delta::blobs_asked` counts the objects handed to `cat-file`. `a_one_page_delta_asks_git_for_that_page_alone` (one page reworded on the owed fixture, every family) asked 11 before the fix and asserts 1: `left: 11, right: 1`, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed` with the counter and the test, before the change to `fetch`); green after. `a_file_read_from_the_tree_is_the_blob_git_would_give` holds `texts` equal to `cat_blobs` over every listed file in each state - edited, deleted, staged then reverted, skip-worktree and absent, a link, a carriage return, untracked, assume-unchanged and edited - and red with the `ls-files -v` guard taken out (the assumed file read as `edited`), measured 2026-11-20 (the same target).
  - **Failing closed** (the session's ruling on this section's found-and-left, 2026-11-20). A `git diff` that fails printed nothing, which read as "nothing changed": every listed page would read from the tree, edits and all, and the record family owe nothing where before it compared whole pages. Now the cached diff, and `ls-files -v`, carry git's error where it failed (`ran`), and where either failed nothing is called unchanged and every name goes to `cat-file`, as before T43; no new `git` call on the success path. `a_diff_git_cannot_run_reads_every_base_file_from_git` corrupts the fixture's index (which fails the diff and `ls-files -v` alike while `cat-file` still reads the base) over an edited page and holds `texts` equal to `cat_blobs` and every name asked: red before the change (`texts` gave the tree's `A long way apart.` where the blob holds `A short way apart.`, log `/tmp/t43/red-diff-fails.log`), green after (84 passed), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). On the real record, the reword's state with the scratch clone's index corrupted, the HEAD build and this one owe the same 5 units (`record-owed --unanswered --slugs`, sorted, identical) of the 11 the state owes with its index whole, measured 2026-11-20 (`/tmp/t43/scripts/corrupt.sh`): the six missing, the next bullet's. A failed `ls-files -v` alone (the diff good) rides the same rule and is not tested by itself: no state was found that fails one and not the other.
  - **A failed diff refused, not read as "nothing changed"** (the session's second ruling, 2026-11-20). `Delta::changed`, the narrow diff before it alike, read a failed `git diff` as an empty delta, so the pop-up family (`modals.rs`'s `changed_pages`), the write-ups' (`owed.rs`'s `changed_sources`) and entry-drift's start (`entry_drift_owed`) owed nothing for a moved page: on the reword's state with the index corrupted, the six modal-research units of `sheet/parley-mats` and `sheet/parley-room` (accuracy, references, gaps) went unowed. Now `changed` returns git's error and every owed computation reading it refuses with it: `cannot tell what changed: git diff failed: <git's stderr>; repair the index, e.g. git -C <tree> reset -q` - never owing everything, which a corrupt index would turn into a flood. A tree with NO repository at all is nothing to judge, as before T43: where the diff fails and `git rev-parse --git-dir` fails too (asked only after a failed diff, so the common path pays nothing), `changed` is empty, and `others` (`ls-files --others`) still reads a failure as no untracked files - the command-line tests pin it (`modals::tests::the_command_line`, `triage::tests::the_command_line_s_refusals`, red when `others` refused, measured 2026-11-20) and `land`'s `replay_owing::tests::the_counts_are_the_python_s` runs the triage in a bare directory (red at the T41 and T43 landing's `make static` when `changed` refused there, the session's report 2026-11-20); a repository whose diff fails (a corrupt index) is refused by `changed`, which every family asks first wherever there is a base. `a_tree_with_no_repository_has_nothing_changed` holds the first: red before the split (`left: Err("cannot tell what changed: git diff failed: warning: Limiting comparison with pathspecs is only supported if both paths are directories. ...")`, `right: Ok("")`, log `/tmp/t43/red-norepo.log`), green after, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). `a_diff_git_cannot_run_is_refused_not_read_as_nothing_changed` owes modal units on the edited fixture with its index whole, then corrupts it and holds the refusal: red before the change (`called Result::unwrap_err() on an Ok value: ["quote-check:0094#k", "record-format:0094"]`, the modal units gone, log `/tmp/t43/red-refused.log`), green after (85 passed), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). On the real record, the reword's state with the scratch clone's index corrupted: `record-owed` and `modal-owed` refuse, exit 1, `cannot tell what changed: git diff failed: fatal: .git/index: index file smaller than expected; repair the index, e.g. git -C /tmp/t43/w reset -q`; with the index whole this build owes the HEAD build's 11 units, identical, measured 2026-11-20 (`/tmp/t43/refused.real`, `/tmp/t43/whole.after`).
  - **The counter on the real record.** A `git` shim first on PATH teeing `cat-file`'s input, one computation (`record record-owed`, every family) on a full scratch clone of HEAD d6d242ec5b with one sentence of `0094-rooms-for-a-parley-across-a-border.html` reworded: before 2,249 objects (1,951 by `Delta`'s base read - 1,654 question pages and the 297 pop-up files - then the same 297 pop-up files by entry-drift's own reader, 1 page by entry-drift's moved anchors), after 299 (1, 297, 1), 16 and 17 `git` calls, measured 2026-11-20 (the shim).
  - **The computation alone.** The same clone and delta, the HEAD build and this build run directly (not through the launcher T41 edits), before, after, after, before, five times, `RECORD_CHECKS_DIR` an empty store: before 3.89 (the first, cold), 2.78, 2.14, 2.21, 2.25, 2.20, 2.45, 1.90, 2.20 and 1.80 s of wall (median 2.21 s), 2.94-6.13 user CPU-seconds, after 1.82, 1.58, 1.18, 1.20, 1.45, 1.23, 1.31, 1.25, 1.31 and 1.38 s (median 1.31 s), 2.54-3.67 user CPU-seconds, load 4.1-4.8, measured 2026-11-20 (`/usr/bin/time` around each, `/tmp/t43/scripts/time.sh`). So about 0.9 s off each computation, the size of T40's `cat-file` share, measured 2026-11-20 (the medians above).
  - **The owed output, the same.** Eight real commits that touched the record, its notes, the write-ups or the pop-ups (76221da67f, 13407d397c, 085847d541, 3cb07dd2ba, 94f514f15f, a650df3cb7, 7ec3bb6396, ed88a709e2), each put in the scratch clone as its parent checked out with origin/main at the parent and the commit's tree restored over the working tree (its delta uncommitted, its new files untracked), and the reword above: `record-owed`, `modal-owed`, `modal-owed --ids` (every pop-up's fingerprints), `translation-owed` and `modal-triage bundle`, and `record-owed --between <parent> <commit>`, each by both builds on an empty store - 53 listing pairs (nine states by five verbs, and eight `--between`) and three triage bundles: every listing and exit identical but the three triage outputs, which differ only in the `--out` path each side printed, and the bundles identical file for file (`diff -r`, checked on 13407d397c), measured 2026-11-20 (`/tmp/t43/scripts/diff.sh`). The record units' fingerprints, which the listing does not print: on five of those states each build answered the units it listed into an empty store (the entry-gate suite's `answer_all`; 11, 18, 4, 114 and 26 listed, 0, 1, 2, 21 and 0 left unanswered even by the answering build, the script not answering every kind), and the other build then left as many unanswered, measured 2026-11-20 (`/tmp/t43/scripts/fp.sh`); and line by line on four of them (the reword, 76221da67f, 085847d541, 13407d397c), each build answering and both listing what was left, sorted: the lists identical, all eight (0, 1, 2 and 21 lines), with this section's fail-closed build, measured 2026-11-20 (`/tmp/t43/scripts/fp.sh`, log `/tmp/t43/fp-lists.log`). The leftovers' fingerprints are held by `a_file_read_from_the_tree_is_the_blob_git_would_give` (the base text each fingerprint is taken of, equal to `cat-file`'s) and, for the pop-ups, by `modal-owed --ids` above.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| unchanged base files read from the working tree | n/a - no map | n/a | none | n/a |
| a failed `git diff` or `ls-files -v` reads every base file from git | n/a - no map | n/a | none | n/a |
| a failed `git diff` refused with git's error, not owed as nothing changed | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T43 Approach (checklist part A)

1. **The goal, in the world.** Each owed computation asks git at the base only for what the delta names, so every gate run, push, landing and the entry-gate suite's chain is faster; no map changes and the owed units come out the same.
2. **The constraints.** FR-010, FR-013; the task line's hold (the owed units the same, red first on a cost counter); `delta.rs`'s rule that nothing is kept between computations; only the `owed` crate and this section edited (T41 works on `scripts/gates/l7r-gate.sh`).
3. **Where each comes from.** O: T40's shim figures (1,951 blobs, 0.63-1.13 s, measured 2026-11-20 (T40's `git` shim)), and this task's counter, shim and timings; the task line for the hold.
4. **Do they describe the world here?** Measured on a full scratch clone of HEAD with the real record (1,654 question pages and 297 pop-up files at the base), by a `git` shim and `/usr/bin/time`, and on eight real commits from history, measured 2026-11-20 (the approach's methods).
5. **The order.** After T40 (its finding); before T22 (as filed); beside T41 (different files).
6. **The exits.** Green: the one-page delta's base read at 1 object, the computation faster on the same delta, the owed output identical on real commits. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The counter's test red then green; the shim's object count on the real record before and after; the computation alone, the two builds alternated on the same delta, the load noted; the differential and the fingerprint cross-check above.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a reader of a map sees; no check's verdict changes (every listing identical on the real commits). Not a defect: a speed change; the fail-closed rule restores what a failed diff owed before T43, and a failed diff now refuses where it owed nothing, each red first on its own test.

**Found and left?**
- A failed `git diff` (a corrupt index fails it) printed nothing, so every listed page read from the tree, edits and all, and the record family would owe nothing where before T43 it compared whole pages: fixed here (failing closed, the approach's bullet above, the session's ruling 2026-11-20); no state short of a corrupt index was found that fails it.
- With a failed `git diff`, `Delta::changed` (the narrow diff before it alike) read the delta as empty, so the pop-up family owed nothing for a moved page: on the reword's state with the index corrupted, the six modal-research units of `sheet/parley-mats` and `sheet/parley-room` (accuracy, references, gaps) went unowed by the HEAD build, measured 2026-11-20 (`/tmp/t43/scripts/corrupt.sh` against the same state whole): fixed here (the approach's refusal bullet, the session's second ruling 2026-11-20).
- Entry-drift's report reads every pop-up file at the base by its own reader (`entry.rs`'s `read_at`, a `RevReader` with its own `cat-file`), 297 objects in 0.025 s of each computation, measured 2026-11-20 (the shim). Not a defect: no wrong outcome, a cost, and not filed: about 2% of the computation, measured 2026-11-20 (the shim against the timings above).

**Performance work?** yes - a `[perf]` task (451 FR-013: every gate run's owed computation). Its answers:

1. **Where does the time go?** Into one `cat-file --batch` of 1,951 base blobs, 0.63-1.13 s of each 1.4-1.6 s computation, the rest the binary's own work, measured 2026-11-20 (T40's `git` shim).
2. **Removes work, or only moves it?** Removes it: 1,950 fewer blobs inflated a computation on a one-page delta; the tree's copies cost a file read each, from the page cache.
3. **What do you expect it to save, and why?** Most of the `cat-file` share, 0.6-1.1 s a computation (a GUESS from T40's shim figures before measuring).
4. **How does the work grow with the settlement?** n/a - no settlement; with the record, the base read now grows with the delta, not with the record's pages.
5. **What did the before and after show, and under what conditions?** On a one-sentence delta, median 2.21 s before and 1.31 s after of wall, user CPU 2.94-6.13 against 2.54-3.67 s, ten alternated pairs at load 4.1-4.8, measured 2026-11-20 (`/usr/bin/time`); the base objects asked 2,249 before and 299 after, measured 2026-11-20 (the shim).
6. **Did any map move, and does it still keep the research?** No map.
<!-- plan-archive: archived 2026-11-20 -->
### T38 (the gate crates' tests read the real environment through the guard: with `L7R_FEATURE_DIRECTORY` and `L7R_EVENTS_DIR` exported, 49 tests of 7 gate crates failed, found by T32, observed 2026-11-20, method: T32's per-crate sweep, `/tmp/t32-sweep/all2/summary.txt`)

- **Approach**: the guard's explicit-environment variants made public, and each gate crate hands them the environment its root
  carries. The seam is `shared::env::Rooted`, a root and an environment reader together, which derefs to the root, so a
  `&Rooted` goes where a `&Path` went. `Rooted::process` reads the process's environment and `Rooted::with` a test's own map.
  Beside it are `shared::env::Reader` and the guard's `_in` functions: `checks::arbiter::{feature_dir_in, rulings_in, aside_in,
  blocking_in, batch_triggers_in, trip_in, try_trip_in}` and `event_log_hooks::{log_path_in, append_row_with, record_in}`. The old
  names are wrappers over `shared::env::opt`; `try_trip` had no caller left and is gone. No cargo feature is used and no test
  sets the process's environment.
  - red first, both variables exported: arbiter 12, bundle 2, land 17, measure 1, owed 1, reviews 10, rustc 6 failed (49), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/<crate> FRESH=1` per crate, `/tmp/t38/red-*.log`); and land's `main_s_refusal_is_filed_by_its_feature_word` wrote `449-x.jsonl` into the exported events directory, measured 2026-11-20 (`find /tmp/t38/events-red`).
  - per crate, the fix: owed - `cli_in`, `run_in`, `file_outside_in`, `triage::bundle_in` and `triage::refusal_in` taking its store, and `answers::store_in`, the answer store a root's own environment names (`RECORD_CHECKS_DIR` read through `Rooted::opt`; the computation's own `store_in` renamed `store_named`); reviews - `glyph`, `checkpoint` (`state_in`, `hold_in`, `cli_in`, its `SPECIFY_FEATURE` read through the root) and `owed_in`; rustc - `World.root` a `Rooted`; measure - `event_log::cli_in` and `refile::cli_in` with a `&Reader`, step-back's `Env.base`; bundle - `earlier::section_in`, and `modal`'s chain (`cli_in`, `main`, `bundles`, `bundle`, `held_back`) on a `Rooted`, its answer store from `owed::store_in` handed to `triage::refusal_in` and `order_hold`, and `CHECK_ORDER_OK` read through the root; record - `apply_edits::cli_in`, `round::run` and `Round::settle` on a `Rooted`, the round settling into `owed::store_in`; land - `Land.root` a `Rooted`, `main` given its base, `phase::end` through it; arbiter - every function holding a guard read takes `&Rooted`, `cli_in` and `bundle::cli_in` built from `Rooted::process`. Each crate's tests shadow the readers with their own environment (`own()`), and one test asks each process wrapper on a path that reads nothing.
  - red first, `RECORD_CHECKS_DIR` exported alone into an empty store (`make rust-test CRATE=rust/gate/crates/<crate> FRESH=1`, record once, then bundle twice): record 3 failed (the three `rounds` settling tests); bundle 0 on the empty store and 1 on the second run (`modal::tests::an_answered_check_holds_nothing`, the first run's answer read back); and the exported store gained 3 answer files the tests wrote (`modal-form%3Ahamlet%2Fwell`, `quote-check%3A0094%23k`, `record-format%3A0094`), measured 2026-11-20 (`/tmp/t38/rcd/red-summary.txt`, `red-*.log`, `ls /tmp/t38/rcd/store-red`). Owed's own reads are none in its tests (`answers::record_checks_dir`), but a dependent links owed's normal build, so its tests read and wrote the process's store through `owed::store` and `triage::refusal`; record's `a_store_that_cannot_be_written_and_a_ledger_held_or_unreadable` ran `remove_dir_all` on that store to make it unwritable - with it exported, a session's real answer records, read 2026-11-20 (`apply_edits/tests/rare.rs`).
  - the sweep before the fix: the 78 variables T32 swept exported at once moved 12 tests more than the two named, owed 11 and land 1, measured 2026-11-20 (`make rust-test` per crate, `/tmp/t38/sweep/before-all`); the 75 left with `L7R_FEATURE_DIRECTORY`, `L7R_EVENTS_DIR` and `RECORD_CHECKS_DIR` taken out moved none (7 crates green), measured 2026-11-20 (`/tmp/t38/sweep/before-rest/summary.tsv`). The 12 were owed's own `std::env::var_os("RECORD_CHECKS_DIR")` (3 reads, now `answers::record_checks_dir`, none in the crate's tests) and land's replay, which set `RECORD_CHECKS_DIR` in the process around `triage::bundle`; the replay now hands `bundle_in` its store, and its test of the `restore` helper that set and removed a process variable went with the helper.
  - the cargo-feature route, checked before ruling it out: a dev-dependency feature (core's `testkit`, the precedent) reaches no normal build - `cargo tree -p l7r_gate -e normal,build,features -i l7r_gate_core` and the same for `-p l7r_gate_rustc` name `default` alone - but reaches every target of that package's test build, its binary included (`-e features` names `testkit`), measured 2026-11-20 (`cargo tree`, 4 runs). So T32's claim is narrower than stated: the tool binaries (`cargo build --profile tool`) never get the feature, but a test build's `l7r-rust` would. The route stays out because the task line forbids it (T38's words: "never a cargo feature turning the guard's test map on for dependents").

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the gate crates' environment reader | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T38 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A gate crate's tests reach the same lines whatever the builder's shell exports, and write nothing into a session's real logs; before the fix, 49 failed and one fixture log landed in the exported directory, measured 2026-11-20 (`make rust-test` per crate, `/tmp/t38/red-*.log`, `find /tmp/t38/events-red`).
2. **The constraints.** T38's line: each read handed an environment reader carried with the crate's root, the guard's explicit-env variants made public, never a cargo feature, never a test's `remove_var`, red first with both exported, every gate crate swept. T32's seam (`shared::env`, the guard's own test map), which stays as it is. 100% line coverage of each changed crate by its own tests, measured 2026-11-20 (`l7r-gate.sh rust cover --crate <crate>`, `/tmp/t38/final/cover-*.log`, `/tmp/t38/cover-*.log`).
3. **Where each comes from.** O: T32's sweep, measured 2026-11-20 (`/tmp/t32-sweep/all2/summary.txt`); O: the red-first run, 49 failed, measured 2026-11-20 (`/tmp/t38/red-summary.txt`); R: T32's section in plan-done.md (the seam it built and why it stops at the guard); the task as filed (T38's line).
4. **Do they describe the world here?** Yes. A page session exports `L7R_FEATURE_DIRECTORY` (`rust/gate/crates/pages/src/runner/work.rs`, read 2026-11-20), and that export with `L7R_EVENTS_DIR` reproduced T32's 49 exactly, crate by crate, measured 2026-11-20 (`/tmp/t38/red-summary.txt`).
5. **The order.** After T32 (its seam, reused). Independent of T42, which edits `shared/tree*` and the main-tree and gm-tree guards in the same clone; none of those files is touched here. Lands before T22.
6. **The exits.** Green: each of the 7 crates and the guard green plain and exported, and the sweep of every gate crate green, the store's dependents twice against one store and the store left empty, measured 2026-11-20 (`/tmp/t38/final/plain.tsv`, `/tmp/t38/sweep/after3/summary.tsv`, `per-var.tsv`, `twice.tsv`, `store-files.txt`); each changed crate's lint and cover clean, measured 2026-11-20 (`/tmp/t38/final/lintcover.tsv`, `/tmp/t38/lintcover.tsv`, `/tmp/t38/rcd/lc/summary2.tsv`: lint owed, bundle, record, land, arbiter and cover owed, bundle, record after the store fix, `summary.tsv`: lint reviews, measure and cover reviews); `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The 17 call sites T32 counted were the direct ones, observed 2026-11-20, method: T32's count in its section of plan-done.md. The reds also reached the environment through `event_log_hooks::record` (measure's hook), `arbiter::try_trip` (reviews' checkpoint), and `rulings`, `aside`, `blocking` and `batch_triggers` (arbiter, bundle), each reading the feature pointer inside the guard, measured 2026-11-20 (the red tests' panics traced to their calls, `/tmp/t38/red-*.log`). Each got its `_in`.
8. **The budget.** One landing.
9. **Done, measured.** 0 failed in the 7 crates with both variables exported, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/<crate> FRESH=1`, `/tmp/t38/fix{1..7}-summary.txt`); every gate crate (27), the gate and the guard green with T32's variables exported at once (77, `L7R_GUARD_CARGO` out, below), the 7 and record green with each of the 3 movers exported alone (24 runs), owed and 6 of the 7 crates that link it (bundle, record, arbiter, land, claims, trials; the seventh, `rust/gate`, was not in the twice run, and was green against the seeded store below) green twice each against one exported store, and bundle green with all 78, measured 2026-11-20 (`/tmp/t38/sweep/after3.sh`: `after3/summary.tsv`, `per-var.tsv`, `twice.tsv`); the exported answer store held no file after the sweep, 3 before the fix, measured 2026-11-20 (`after3/store-files.txt`, `/tmp/t38/rcd/store-red`); the exported events directory held only the runner's own `Phase` lines, one file, `451-time-retro-and-efficiency.jsonl`, measured 2026-11-20 (`after3/events-files.txt`, `grep -v Phase` empty).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. A builder in a page session no longer sees 49 gate tests red that are only its shell's exports, and a builder with `L7R_EVENTS_DIR` exported no longer gets a test's `end` line in a real feature's log, which `make where-time` and T13 and T14 read: 1 log before, 0 after, measured 2026-11-20 (`find` over the exported directory, `/tmp/t38/events-red`, `/tmp/t38/sweep/after2/events-files.txt`).

**Found and left?**
- The sweep's 12 more (owed 11, land 1: `RECORD_CHECKS_DIR`, the crates' own reads, and land's replay setting it in the process around a call): fixed here, measured 2026-11-20 (`/tmp/t38/sweep/before-all`, `/tmp/t38/sweep/after2/per-var.tsv`).
- `checks`' file-scale test: `owed/answers.rs` passed the 1,000-line bar at 1,012 lines with this task's `_in` functions, measured 2026-11-20 (`/tmp/t38/sweep/after-all/rust_gate_crates_checks.log`). Fixed here: its command-line half was split into `answers/cli.rs`, leaving 807 lines with `store_in`, measured 2026-11-20 (`wc -l`). The same test names `rust/guard/src/shared/tree.rs` at 1,064 lines, measured 2026-11-20 (the same log). Not fixed here: the file is T42's, mid-edit in this clone by another builder and outside T38's files. Filed as T42; lands before T22. T42's split has since left it at 673 lines, and `make quick` was clean, measured 2026-11-20 (`wc -l`, `/tmp/t38/rcd/quick.log`).
- The bundle crate's `check` and `keys` bundles reach `earlier::section` through its process wrapper (`modal`'s now hands `section_in` its root). Not a defect: the read is the active feature and its rulings, so no test outcome moved with any variable exported (`/tmp/t38/sweep/before-rest`, `after3`) and nothing is written. This bullet first said the same of `modal` for every variable, which was wrong for `RECORD_CHECKS_DIR`: `modal`'s order hold and triage refusal read the process's answer store, and record's round settled into it, measured 2026-11-20 (the red first above); fixed here.
- `L7R_GUARD_CARGO=cargo`: the handoff read 19 bundle reds (`depiction` and `modal`, each `key must be a string at line 1 column 2`) in the 78-variable run as its, since the 77 without it left 1, measured 2026-11-20 (`/tmp/t38/sweep/after2/rust_gate_crates_bundle.log`, `bundle-nocargo.log`). Not borne out: exported alone it moved none, and with all 78 after the store fix bundle was green, measured 2026-11-20 (`/tmp/t38/rcd/guard-cargo-bundle.log`, `after3/bundle-78.log`). The cause of the 19 is a GUESS, not measured: the shared exported store, which earlier crates' tests had filled; `after3.sh` deleted that store before anyone read it, so it cannot be checked now. Read only by the hook launcher (`scripts/hooks/l7r-guard.sh`) and the guard's bench, it is a runner variable, so the sweep's list drops it as T32's runner names were dropped: 77 swept in `after3`, measured 2026-11-20 (`wc -l /tmp/t38/sweep/vars77.list`, 78 in `vars.list`). Not a defect: no test outcome moves with it, measured 2026-11-20 (the two logs above).
- `Delta::store` and `sibling_stores` still read the process's `RECORD_CHECKS_DIR` (`owed/answers.rs`, `record_checks_dir()`), reached from other crates through arbiter's `owed_units` -> `owed::unanswered` and record's `record-owed` -> `owed::cli`. Checked, no read: with `RECORD_CHECKS_DIR` pointing at a store seeded with the red run's 3 answer files, owed, bundle, record, arbiter, land, claims, trials and `rust/gate` were each green once (0 failed; 86, 78, 86, 32, 77, 161, 129, 8 passed), and `diff -r` of the store against its untouched copy was empty, measured 2026-11-20 (`make rust-test CRATE=<c> FRESH=1` per crate, `/tmp/t38/seededrun/run.sh`, `summary.txt`, `diff.txt`). Why, read 2026-11-20: arbiter's tests hand `owed_units` their units through `sections::GIVEN`, and no record test dispatches `record-owed`. Not a defect: a test reaches neither read, so `Delta` is not given the store at construction; the binary's reads are the real ones.
- T32's cargo-feature claim: narrower than stated - a dev-dependency feature reaches a package's test build, its binary included, but never the tool binaries - measured 2026-11-20 (`cargo tree`, the Approach above); not a defect, the route stays out by the task's words.

**Performance work?** yes (a `[perf]` task, 451 FR-013: a builder's `make rust-test` on the gate crates is green whatever the session exports, so no round is spent on a red that is the shell's); not engine speed.

### T38 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In a builder's rounds, not in a stage: a page session's builder met 49 reds that were its shell's, measured 2026-11-20 (`/tmp/t38/red-summary.txt`); no hamlet or Mode A stage is touched.
2. **Removes work, or only moves it?** Removes it: the round spent reading a red that the code did not cause; the read itself costs the same (a map or the process's `getenv` behind one indirect call).
3. **What do you expect it to save, and why?** One red round a page-session builder would spend per gate-crate run, the 49 reds of `/tmp/t38/red-summary.txt`, measured 2026-11-20 (that log); no stage time.
4. **How does the work grow with the settlement?** It does not: no settlement code changes, measured 2026-11-20 (`git diff --stat`, no `rust/phases` or `rust/mode_a` file).
5. **What did the before and after show, and under what conditions?** 49 failed before, 0 after, both exported, the host shared with T42's builder, measured 2026-11-20 (`/tmp/t38/red-summary.txt`, `/tmp/t38/fix{1..7}-summary.txt`).
6. **Did any map move, and does it still keep the research?** No map: no engine or pool file changes, measured 2026-11-20 (`git diff --stat`).


<!-- plan-archive: T39 to T32 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T39 to T39 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T40 to T21 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T41 to T34 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T41 to T41 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-20 -->
### T42 (found by T31, 2026-11-20: a Python program run from stdin that writes, standing in the mirror, was judged by no one, and T31's stdin rule kept three real reads refused or rewritten - main-tree#147, window#339, window#361; observed 2026-11-20, method: T31's replays and `heredoc_writers.py`)

- **Approach**: a Python program run from stdin is judged by T31's denylist reader (`shared/tree/py_c.rs` `reads`) as a `-c` program is, and T31's stdin rule is retired for every program the walk can read.
  - `shared/tree/python.rs` (new, split from `tree.rs` with `tree/verdict.rs` for the file-scale bar, `tree.rs` 1,064 lines measured 2026-11-20 (`make task-add`'s `make quick`, check file-scale), 673 after, measured 2026-11-20 (`wc -l`)): `carry_heredocs` carries each heredoc's body out beside the text, `<<__py_h_<n>__` standing in its place (`shape::strip_heredocs`' span and opener words, with an index), its quote recorded - a quoted delimiter (`'PY'`, `"PY"`, `\PY`) literal, an unquoted one `'h'`, which the shell expands. `stdin_program` finds what a Python segment runs from stdin (`python_stdin`'s shapes): its own heredoc, its own `< file` (resolved where the shell stands, a regular file only - a device such as `/dev/tty` would wait), or, through a pipe, what an upstream `cat` prints (one heredoc or one readable file). Anything else - a variable, a here-string, a missing file, a directory, any other upstream - is a program the walk cannot read.
  - `tree.rs` `walk_in`: a readable program that `reads` judges a writer is a write where the shell stands (`how = "shell"`, D5's form for `-c`), first among the segment's writes; one that only reads is no target, as no stdin program was before; one the walk cannot read keeps every `-c` read of the command D5's write (T31's rule, now that case alone, as the task keeps it: "a program fed from a variable or a file outside the command stays judged as T31 left it"). `segments` marks a segment a single `|` feeds (a pipe at a line's end feeds the next line). A target's segment shows `<<BODY`, as before.
  - Two walks: `walk_judged` (the tree guards: `judge`, its re-judge, `gm_tree_hooks::offending`) judges stdin programs; `walk` (house style, make-only, the bench) sees none, as before - house style's D11 holds a program heredoc's writes unknowable, and its case table pins `python3 - <<'PY' > /tmp/gate.log` with a `write_text` body left alone: the first build's single walk failed that case, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t42/green1.log`).
  - `py_c.rs`: the quote `'h'` - an unquoted heredoc's body undoes the shell's `\\`, `\$` and `` \` `` but not `\"` (two characters there), and a command substitution in it is a write as in a double-quoted `-c`. And `re.compile(` is read past before the writers are sought (`RE_COMPILE`): it builds a pattern, never code; the builtin `compile` and any other name's `.compile(` stay a write. Found by the replay's hand-read: window#307's first heredoc, a read, was judged a writer on it.
  - red first, each in `/tmp/t42/`, all `make rust-test CRATE=rust/guard`, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, the logs named): the rows and shapes before the code, 677 passed, 3 failed (`red-first.log`) - main-tree#147 refused (window#339 and #361 behind it in the same test; all three refused by HEAD's binary in the replay, `ihead.nobody.main-tree-hooks.tsv`), the heredoc writer with no `-c` beside it allowed, the walk's stdin forms; `re.compile` 680 passed, 1 failed (`red2-compile.log`); green 681 of 681 (`green3.log`, `final-test.log`, `split-test.log` after the split).
  - replays: the four corpora, 1,134 rows, through all guards and main-tree, gm-tree and house style alone, SID `t` (a clone resolves) and `nobody` (none), measured 2026-11-20 (`/tmp/t42/scripts/replay.sh`, `runall.sh`, `cmp.sh`). Before = HEAD's source built alone (`git archive`), after = HEAD plus T42's files alone, since a second builder's edits shared the clone; HEAD's isolated binary against the clone's build before any edit, 0 differences, and a second HEAD run, 0 (no noise), measured 2026-11-20 (`cmp.sh`):
    - main-tree alone, measured 2026-11-20 (`replay.sh`, `cmp.sh`): `nobody` 93 allowed -> refused, 3 refused -> allowed (main-tree#147, window#339, window#361); `t` 93 allowed -> rewrote, the same 3 rewrote -> allowed; 0 other outputs changed;
    - all guards, measured 2026-11-20 (`replay.sh`, `cmp.sh`): `nobody` 58 allowed -> refused, 28 rewrote -> refused (house style's rewrite now beside main-tree's refusal), 3 refused -> allowed, 7 refused by another guard before and after with output changed; `t` 58 allowed -> rewrote, 3 rewrote -> allowed, 28 rewrote with output changed (main-tree's rewrite joined to house style's); the changed rows are exactly main-tree's 96 moves (`t`: 89, the 7 refused by another guard unchanged);
    - gm-tree alone and house style alone, measured 2026-11-20 (`replay.sh`, `cmp.sh`), `t` and `nobody`: 0 moved, 0 outputs changed;
    - the `re.compile` fix alone, measured 2026-11-20 (`cmp.sh`, the build before it against the build after): 0 moved.
    - the final source (after the split and the lint fixes) rebuilt and all eight runs replayed again, measured 2026-11-20 (`cmp.sh` against the previous build's): 0 verdicts and 0 outputs changed.
  - the 93 moves by class, measured 2026-11-20 (`/tmp/t42/scripts/classify.py` and a hand-read of each body): 78 a writer now caught (a write call - `write_text`, `open(..., 'w')`, `mkdir`, `rename`, `shutil`, `.save(`, `.dump(`); 12 run the tree's own code standing in the mirror (`l7r` modules, `_hm_house`, `covered_by` and a `specs/` module by `sys.path` or `importlib`, the mirror's house-style hook by `subprocess`), a writer now caught - from the clone they run the clone's code. They are caught by the denylist's names (`sys.path`, `importlib` with its `exec`, `subprocess`), not by T31's import rule: a replay with the mirror seeded with the tree's top-level names moved 0 rows against the unseeded one, HEAD's build and T42's, `t` and `nobody`, measured 2026-11-20 (`/tmp/t42/scripts/replay-seeded.sh`, `cmp.sh`); 2 run a module the walk cannot see (window#260's scratch `style_fix`, window#315's `measure_geom`, both through `sys.path`), the denylist's closed side as for `-c`; 1 a read now refused or rewritten (window#307: `subprocess.run(["git", "-C", root, "ls-files"])`), below.
  - against T31's 331 (`heredoc_writers.py`), measured 2026-11-20 (`heredoc_writers.py` over the replays, a cd classifier and a hand-read): 80 moved; 30 refused before and after; 221 allowed before and after, each standing in a clone or outside the mirror where its heredoc runs - 189 after a `cd` into a clone, 12 inside `( cd <clone> && ...` (the script's cd test misses a subshell's), 16 after a `cd` outside, parse#184, refusals#26 and window#301 after a `cd` into a clone first (refusals#26's Python is a `cat` heredoc's text, never run), main-tree#150 a relative `cd` inside a clone - and none of the 221 names a mirror path in its body. The 13 moves outside the 331 are 11 of the 12 tree-code runs (`sys.path` or `importlib`) and window#260's and window#315's bodies, whose names the script's narrower list does not hold; the twelfth tree-code run (window#299, the house-style hook by `subprocess`) and window#307 are among the 80, measured 2026-11-20 (`/tmp/t42/moved93.cls`). A correction to T31's line: its "301 allowed" counted by the recorded cwd, not by where the shell stands at the heredoc, so a heredoc run after a `cd` into a clone was counted as standing in the mirror; placed by where the shell stands, the 221 above stand in a clone or outside the mirror.
  - parse#72 and window#61 stay refused, each now by its own heredoc's target (the test asserts every `shell` target is a `python3 -` heredoc segment), measured 2026-11-20 (`a_python_program_run_from_stdin_is_judged_by_its_body`).
  - fixture: `tests/hooks/fixtures/main-tree-refusals-2026-09.json` relabeled from the `t` replay, measured 2026-11-20 (`cmp.sh` over its `main-tree#` rows): rows 16, 43, 44, 144 and 169 allowed -> rewrote, row 147 rewrote -> allowed (expected 163 allowed, 10 rewrote); the main-tree suite gains a heredoc writer standing in the mirror -> rewritten.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a stdin Python program judged by its body (main-tree, gm-tree) | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T42 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A builder's Python heredoc that writes, standing in the mirror, is moved to the clone (or refused where none resolves), as a `-c` writer is; one that only reads runs as typed, and so does a `-c` read beside it. Every write caught before is still caught.
2. **The constraints.** T42's line (judge a heredoc body through py_c, red first on parse#72's shape and the three rows, the replay's moves accounted, T31's stdin rule retired); feature 204 D5 as T31 narrowed it (a read judged by the denylist is no write); D6 (unknown resolves toward main) untouched; house style's D11 (a program heredoc's writes unknowable) kept by its own walk; 100% line coverage of the guard crate; the file-scale bar.
3. **Where each comes from.** R: feature 204 spec D5, D6; house style's D11 at its case table (`case_tables/house_style_cases.rs`). G: the session's ruling of 2026-11-20 that T31 records - refusing a read is a wrong outcome (constitution XIV). O: the replays above, measured 2026-11-20.
4. **Do they describe the world here?** Measured on the four corpora by replay, each of the 93 moved bodies hand-read for what it writes or runs, and the 221 unmoved writers each placed by where the shell stands at its heredoc, measured 2026-11-20 (`classify.py`, `heredoc_writers.py`, the cd classifier and a hand-read).
5. **The order.** After T31 (its reader and its stdin rule); before T22; beside T38 (the gate crates' env reads, other files).
6. **The exits.** Green: the red tests green; the replays, every move accounted; `make rust-test CRATE=rust/guard` and the crate's lint, format and cover for its own files; `make quick`; `make static` (once); `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Every reader of a walk was found: `judge` and its re-judge, `gm_tree_hooks::offending` (now `walk_judged`), `house_style_hooks::lands_outside`, `make_only_hooks::walked_write` and `suite_tools/bench.rs` (`walk`, their view unchanged: 0 moves, measured 2026-11-20 (`cmp.sh`), under house style and the guards together beyond main-tree's), read 2026-11-20 (`grep 'tree::walk\| walk('` over `rust/guard/src`); no other guard carries a heredoc's body into the walk.
8. **The budget.** One landing.
9. **Done, measured.** The three reads run as typed (`red-first.log` -> `final-test.log`; the replays' 3 moves); parse#72 and window#61 refused by their own heredocs; 93 stdin programs standing in the mirror now judged, 92 of them writers or runs of code the walk cannot see, every move accounted above, measured 2026-11-20 (`cmp.sh`, `classify.py`).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. A builder sees its heredoc writer moved to the clone, or refused with no clone, where it ran in the mirror unjudged; its heredoc read and a `-c` read beside it run where T31 refused or rewrote them. The fix is not a restatement: a write in the mirror judged by no one and a read refused are both wrong outcomes (constitution XIV).

**Found and left?**
- window#307 runs two heredocs that only read and is refused with no clone, rewritten with one: its second lists tracked files with `subprocess.run(["git", "-C", root, "ls-files"])`, and `subprocess` is on T31's denylist, observed 2026-11-20, method: every moved body hand-read for what it writes or runs. Not fixed here: telling a read-only `git` argv from any other command is an argv reader past the denylist, which judges a call by its name; the same program as a `-c` is refused so since T31. Filed as T44; lands before T22.
- `re.compile` judged a writer (the same row's first heredoc, and any `-c` read that builds a pattern): fixed here.
- house style's verdict varied under load: one house-style-alone replay with no clone resolvable (`nobody`), run under load on the build before the split, flipped 8 rows rewrote -> allowed (parse#87, window#125, #343, #369, #395, #417, #418, #462) and changed 3 rows' output (window#344, #396, #402); a rerun of the same build and the split build's run gave 0 moves, observed 2026-11-20, method: `cmp.sh` over every replay pair (`/tmp/t42/cmp-final.txt`, `cmp-noise.txt`, `cmp-split.txt`). Not fixed here: T42 leaves house style's walk and verdict as they were (0 moves in every steady replay), and the timing dependence is not yet found - it is measured first, under induced load. Filed as T45; lands before T22.

**Performance work?** yes - a `[perf]` task in FR-013's sense (the builders' loop): each refused or rewritten read costs a model round trip; the corpora hold 3 such reads now allowed and 93 stdin programs standing in the mirror now judged, measured 2026-11-20 (`cmp.sh`). Not filed with `PERF=1`: no engine stage's counted operations or time.


<!-- plan-archive: T43 to T40 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T43 to T43 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

<!-- plan-archive: archived 2026-11-20 -->
### T44 (found by T42, 2026-11-20: window#307's second heredoc, a read, runs `subprocess.run(["git","-C",root,"ls-files"])` and main-tree refused it with no clone resolvable and rewrote it with one, since `subprocess` is on T31's denylist of known writers; observed 2026-11-20, method: T42's replay and a hand-read of each moved body)

- **Approach**: `shared/tree/py_c.rs` (406 lines, measured 2026-11-20 (`wc -l`)) accounts for every mention of `subprocess` before the writers are sought; one it cannot account for stays a write, so the denylist's closed side holds.
  - Accounted: a plain `import subprocess` (alone or in a comma list, no `as`), the constants `subprocess.PIPE`, `DEVNULL`, `STDOUT`, and a `subprocess.run`, `check_output`, `check_call` or `call` whose first argument is ONE list display, nothing past its bracket (`list_items`, on `call_args`' new `split_args`, which also returns where the call closes), and whose other arguments are only the keywords `capture_output`, `text`, `check`, `cwd`, `encoding`, `errors`, `timeout`, `input`, `universal_newlines`, `stdout`, `stderr`, `stdin`. Only the name is masked (`subprocess_masked`): the call's arguments stay in the text the denylist reads, so `input=os.remove(...)` and `stdout=open('o','w')` are still writes.
  - The argv (`argv_reads`): its command an exact literal, `git` or one of `TOOLS`; for git, any `-C <expression>` pairs (the directory alone may be any expression - window#307's `root`) and then a subcommand of `GIT_READS`; every other element a literal (`argv_literal`: no quote of its own delimiter, so `'log' if c else 'push'` is none; no `$`; an f-string only where its text opens with neither `{` nor `-`, so window#112's `f"HEAD:{path}"` is one and `f"{flag}"` is not), naming no option that writes or runs a program, in any abbreviation (`writes_flag`: git's `--output`, `--ext-diff`, `--textconv`, `--filters`; this container's `grep`, which is ugrep, `--filter`, `--pager`, `--view`, `--save-config`, `--query` or `-Q` in a short cluster, and `--config`/`---FILE`, which load options from a file).
  - How the option screen was found, observed 2026-11-20: the search space is each admitted git subcommand's full long-option list as git's parser prints it (`git <sub> --git-completion-helper`, the `-all` form where it exists: `ls-files` 46, `log` 18, `show` 18, `rev-parse` 1, `cat-file` 23, `ls-tree` 12 options; `log` and `show` also take the diff options, `git diff --git-completion-helper`, 99) and `grep`, `ls`, `cat`, `head`, `wc --help`, each searched for an option naming an output file, a command, a program, a pager, an editor, a tool, a hook, a filter, a config or a write (`grep -iE` over the lists). Found: `--output=`, `--ext-diff`, `--textconv` (diff's), `--textconv`, `--filters`, `--filter=`, `--batch-command` (cat-file's; `--batch-command` reads object queries from stdin and writes nothing), and ugrep's above; none for `ls`, `cat`, `head`, `wc`, `ls-files`, `ls-tree`, `rev-parse` or log's own. The completion helper does not list the revision walker's options `log` and `show` also take; `git rev-list -h` (41 lines) was searched the same way and names none, measured 2026-11-20 (`git rev-list -h | wc -l` and the same `grep -iE`). Its usage is a summary, not every option, so that part of the screen is a reading of git's own list, labeled as such. `rg` is not admitted: its `--pre` and `--hostname-bin=COMMAND` run a program (the second found by spec-fidelity's round 2, 2026-11-20), and no corpus row runs it. Side-effect writes measured 2026-11-20 (a scratch repository: a tracked file touched, `.git/index`'s hash before and after each subcommand): `ls-files`, `log`, `show`, `rev-parse`, `cat-file`, `ls-tree` left it unchanged; `diff` and `status` rewrote it. A filter or textconv the repository's own config names runs on `log -p`/`show` without a flag, as it does for the same command typed in the shell, which main-tree judges a read (`tree.rs` `git_write`); the mirror's config and `.gitattributes` name none (`git config --get-regexp`, read 2026-11-20).
  - The list, from the corpora, measured 2026-11-20 (`/tmp/t44/scripts/subp.py`, every `subprocess.<fn>(` of the four corpora's 1,134 rows): git `ls-files` (window#307), `show` (window#112), `rev-parse` (parse#173, refusals#27), `log` (parse#229), and `grep` (refusals#42); with `cat-file` and `ls-tree` (T44's line) and `ls`, `cat`, `head`, `wc` (the brief), which no corpus row runs; the brief's `rg` left out, above. `git status` and `git diff` are left out, each by the same rule - they rewrote the index, measured above - and no corpus row runs either from Python (window#328's `git diff` is a `cat >` heredoc's text, never run). `git grep` is not admitted (its `-O` runs a program, spec-fidelity's T44-6, 2026-11-20), pinned with `-O` and `--open=` as writes. Everything else stays a write: a shell string, `shell=True` (or any keyword not listed: `env`, `executable`), a non-literal or starred argv or element, `args=`, a second positional, a writing git subcommand, git's `-c`, `make`, `./git`, an unknown command, `Popen`, `getoutput`, `from subprocess import run`, `import subprocess as sp`, and the module bound to another name.
  - Red first, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t44/red-first.kept.log`): the tests before the code, 682 passed, 2 failed - `a_subprocess_call_with_a_read_only_argv_is_a_read` (window#307's heredoc body verbatim, judged a write) and `window_307_runs_as_typed` (the corpus row through `walk_judged`: one `shell` target, `python3 -  <<BODY`). `a_subprocess_call_that_can_write_stays_a_write` (39 shapes) passed before, as a pin; green 684 of 684, measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t44/green1.log`). After spec-fidelity's T44-6 (BLOCKED, 2026-11-20): `diff` dropped and the screen widened, the pin 49 shapes (`git diff`, `git grep -O`/`--open=`, `cat-file --textconv`/`--filters`, ugrep's five), green measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t44/green2.log`). After round 2 (BLOCKED, 2026-11-20, `rg --hostname-bin`): `rg` dropped, the pin 51 shapes (`rg --hostname-bin=`, `rg -n`), green measured 2026-11-20 (`make rust-test CRATE=rust/guard`, `/tmp/t44/green3.log`).
  - Replays: the four corpora, 1,134 rows, through all guards and main-tree, gm-tree and house style alone, SID `t` (a clone resolves) and `nobody` (none), 9,072 verdicts a side, measured 2026-11-20 (T42's `/tmp/t42/scripts/replay.sh` and `cmp.sh`, `/tmp/t44/scripts/runall.sh`). Before = HEAD 212266c482 built alone (`git archive`), after = the same plus T44's two `py_c` files, since T46's builder shares the clone. Noise: HEAD's build against T42's recorded after-build, 0 verdicts and 0 outputs changed in all eight runs, measured 2026-11-20 (`cmp.sh`).
    - main-tree alone, measured 2026-11-20 (`cmp.sh`): `nobody` 1 refused -> allowed, `t` 1 rewrote -> allowed, both window#307; 0 other outputs changed.
    - all guards, measured 2026-11-20 (`cmp.sh`): `nobody` 1 refused -> rewrote, `t` 1 rewrote with its output changed, both window#307: house style's own rewrite of the row stands alone, its output the same as house style alone (`b2d7d8f799` in all four runs).
    - gm-tree alone and house style alone, `t` and `nobody`, measured 2026-11-20 (`cmp.sh`): 0 moved, 0 outputs changed.
    - the final source (after both review rounds' narrowing: `diff` and `rg` dropped, the screen widened) rebuilt the same way and all eight runs replayed again, measured 2026-11-20 (`cmp.sh`, `/tmp/t44/cmp-after2.txt`, `/tmp/t44/cmp-after3.txt`): against HEAD the same 1 move a run, against the first after-build 0 verdicts and 0 outputs changed.
  - The subprocess rows that did not move, measured 2026-11-20 (the after replay's main-tree verdicts for the other 31 of the 32 rows `subp.py` lists): 26 allowed before and after, standing in a clone or outside the mirror where their Python runs, or never run (window#328 is a `cat >` heredoc's text); 5 held before and after, each running the tree's own code by `subprocess` - window#56, #68, #69 and #299 the house-style hook (`str(d / ...)` or a script path, not a listed command) and refusals#149 `python3 scripts/hooks/lib/hookmatch.py` - a writer the closed side keeps, as T42 classed #299.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a subprocess call with a read-only literal argv read as a read (main-tree, gm-tree) | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T44 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A builder's Python that only reads - listing tracked files, showing a blob, a log, a revision - through `subprocess` with a literal argv runs as typed in the mirror; every subprocess call that can write or run unknown code is still moved to the clone, or refused with none.
2. **The constraints.** T44's line (a read-only git argv told from any other command, red first on window#307, the replay's moves accounted); feature 204 D5 as T31 narrowed it (a read the denylist judges is no write); T31's closed side (a shape the reader does not know is a write); D6 untouched; 100% line coverage of the guard crate; the file-scale bar.
3. **Where each comes from.** R: feature 204 spec D5; T31 and T42 in plan-done.md. G: the session's ruling of 2026-11-20 that T31 records - refusing a read is a wrong outcome (constitution XIV). O: the corpus scan and the replays above, measured 2026-11-20.
4. **Do they describe the world here?** Every `subprocess.<fn>(` of the four corpora listed and its row's verdict read before and after, measured 2026-11-20 (`subp.py`, the replays): 32 rows, 1 moved, 31 unmoved and placed above.
5. **The order.** After T42 (its stdin reader); before T22; beside T46 (`rust/gate/crates/plan`, other files).
6. **The exits.** Green: the red tests green; the replays, every move accounted; `make rust-test CRATE=rust/guard` and the crate's lint, format and cover; `make quick`; `make static` (once); `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: Python's `subprocess` is judged in the guard only by `py_c`'s denylist (`grep -rln subprocess rust/guard/src`, read 2026-11-20: `py_c.rs`, its tests, and a comment in `shared/tool.rs` on the guard's own child processes); the shell-level git reader (`tree.rs` `git_write`) judges a shell command's git, not Python's, and is untouched.
8. **The budget.** One landing.
9. **Done, measured.** window#307 runs as typed (`red-first.kept.log` -> `green1.log`; main-tree's replays 1 refused -> allowed and 1 rewrote -> allowed), 0 other verdicts or outputs moved in 9,072 a side, measured 2026-11-20 (`cmp.sh`).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. A builder sees window#307's shape - a Python read listing tracked files through `git ls-files` - run where it was refused with no clone or rewritten into the clone; a refused read costs a model round trip and is a wrong outcome (constitution XIV), so this is a fix, not a restatement.

**Found and left?** none.

**Performance work?** yes - a `[perf]` task in FR-013's sense (the builders' loop): each refused or rewritten read costs a model round trip; the corpora hold 1 such read now allowed, measured 2026-11-20 (`cmp.sh`). Not filed with `PERF=1`: no engine stage's counted operations or time.

<!-- plan-archive: archived 2026-11-20 -->
### T46 (T42's plan review was handed the wrong decisions: `spec-cited.md` carried 451's own D5, D6 and D11 for T42's "feature 204 D5", "feature 204 spec D5, D6" and "house style's D11", and `spec-index.md` cut FR-009 at "unless it states why the defect is not", observed 2026-11-20, method: T42's plan review and its bundle)

- **Approach**: the cited text's one reader is `cited_text` in `rust/gate/crates/plan/src/plan/bundle.rs`, with `answered` (which amendment the blocks answer) the other reader of the same ids. It read an id as another feature's only in the one form `QUALIFIED` matched - one id, after the number, `plan` allowed between - and looked a decision up only in that feature's plans, dropping it without a word when not found. Now each block is read by `named`: a number qualifies a run-on list (`, D6`, `and D6`, a range written out first), the `spec` form and a task's possessive after the number ("444 T20's FR-043", that feature's); a possessive that is no number (`house style's D11`) names another source unless its name is the feature's own (`OWN_NAMES`: the spec's, the plan's, the GM's, this feature's, a task's, ...); an id so named is looked up in that feature's plans, then its spec (a requirement the other way round), or named `NOT FOUND` with why, and never carried from the reviewed feature. A BARE mention of an id the blocks also name as another's carries this feature's text under a line saying the bare id may mean either. `answered` reads the blocks with every other feature's ids taken out. The index line is the requirement's first sentence, its hard-wrapped lines joined (ending at a `.` before a space or the line's end, outside a code span and never before a lowercase word, since a real sentence starts with a capital, a digit, a backtick or a bold mark (the coordinator, 2026-11-20); never past a nested list, table or fence), past `INDEX_CAP` (420 characters) it is cut at a word, and any line shorter than its lead paragraph ends ` [...]` - an explicit mark, not a silent cut (the coordinator, 2026-11-20).
  - red first, the tests before the code: 4 failed of 156 on HEAD's `bundle.rs`, and 2 of 157 on the first-sentence index before the abbreviation and task-possessive rules (`an_index_line_is_carried_whole` on "(e.g. a well)", "... of things" and "vs. none"; `a_number_then_a_task_s_possessive_names_that_feature_s_id` on "444 T20's FR-043", "433 T01's D3b" and "449 T233's FR-023 and FR-024", `/tmp/t46-red4.log`), and 1 of 157 before `runs_on` (a plain word's ". then", `/tmp/t46-red5.log`), and 2 of 157 before round 2's rules (`an_index_line_is_carried_whole` on "Kinds (e.g. `well`)" and "A thing (it runs. Here", 132 FR-023's and 246 FR-002's shapes; `a_number_then_a_task_s_possessive_names_that_feature_s_id` on "449 T233's FR-005, and D1 and D3 in 999's sections", `/tmp/t46-red6.log`) (`another_feature_s_decisions_are_carried_from_it_never_from_this_one` on the fixture `bundle/fixtures/451-t42.md`, T42's section verbatim from plan-done.md at 212266c482, carrying 451's D5, D6 and D11; `an_index_line_is_carried_whole` on FR-009's text and a marked long line; `another_feature_s_id_answers_no_amendment_of_this_one`; the not-found lines of `a_requirement_cited_as_another_feature_s_is_bundled_from_that_feature`), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t46-red3.log`).
  - green: 157 of 157, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t46-g9.log`); the crate's format, lint and cover clean, measured 2026-11-20 (`l7r-gate.sh rust format|lint|cover --crate rust/gate/crates/plan`, `/tmp/t46-lfc5.log`).
  - every plan: of 2,160 sections, 6 stop carrying 8 of their own ids, each one the section names with another feature's number or name (433 T01's D3b, a finding's label 433 never defines, so a reading of nothing either way; 444 T20's FR-043, 449 T233's FR-023 and FR-024, and D5 and D11 in 451's sections of T42 and T44), measured 2026-11-20 (a Python reading of both rules over `specs/*/plan.md` + `plan-done.md`, `/tmp/t46-scripts/survey2.py`).
  - 15 sections cite 17 ids bare beside the same id named as another's, now marked, this section among them, measured 2026-11-20 (the same reading). The bare one meant the other feature's in 449 T231 and 451 T31 and T42, and the section's own in 417 T37 ("FR-013 (speed first)" beside "(385 FR-013)"), read 2026-11-20 (`/tmp/t46-scripts/ctx.py`).
  - 56 distinct (feature, id) pairs are named over every plan, this section's included, 49 found and 7 named not found, 3 of the found decisions in a spec with no plan.md (feature 204's kind), measured 2026-11-20 (`/tmp/t46-scripts/foreign_idx.py`).
  - the index over every spec: 569,487 to 960,569 bytes, measured 2026-11-20 (a Python reading of the rule over every `specs/*/spec.md`, `/tmp/t46-scripts/marked.txt`, with `runs_on` and the mark).
  - index lines cut at a `.` before a lowercase word: 22 under the first-sentence rule (13 at an ellipsis, 2 at "e.g.", 1 each at "vs.", "etc." and "incl.", 4 at a plain word), 0 under `runs_on`, measured 2026-11-20 (`/tmp/t46-scripts/lower.py` over every `specs/*/spec.md`).
  - a number then a task's possessive ("444 T20's FR-043") is read as that feature's: 3 such mentions over every plan, measured 2026-11-20 (a grep of `specs/*/plan*.md` in `/tmp/t46-scripts/abbr.py`'s run).
  - 1,531 of 4,686 index lines are cut and marked ` [...]` and 0 are cut unmarked, measured 2026-11-20 (`/tmp/t46-scripts/marked.txt`: a line shorter than its lead paragraph, by the sentence rule or the cap).
  - 449's index 11,272 to 6,284 bytes (its long one-line requirements now cut and marked), measured 2026-11-20 (the same reading).
  - 451's index 2,571 to 4,454 bytes, measured 2026-11-20 (the same reading).
  - 267 of 4,686 index lines are cut and marked at 420 characters, 315 at 400, measured 2026-11-20 (the same reading at each cap); FR-009's sentence is 418 characters whole, measured 2026-11-20 (the same reading), so the cap is 420.
  - 7 of 4,686 lead paragraphs stop at a numbered line, each a list under its requirement (`foreign_idx.py` lists the seven), measured 2026-11-20 (`/tmp/t46-scripts/foreign_idx.py`).
  - observed 2026-11-20, method: every reader of a cited id found by grepping `rust/gate/crates` for `IDS`, `QUALIFIED`, `DECISION` and `ITEM` - `cited_text` and `answered` in `bundle.rs` are the two; `sections.rs`'s decision patterns cut and digest blocks, and carry no cited text.
  - **Labeled conventions.** A possessive is the feature's own by its name, `OWN_NAMES`, a CONVENTION read from every plan's possessives (2026-11-20); a name misread as another's costs a `NOT FOUND` line, never a wrong text. A bare id beside the same id named as another's is carried marked, not withheld, because the survey found it meaning either; the task line does not decide it, a bare mention not being "named with another feature's number".
  - **The index line's length, chosen** (the coordinator, 2026-11-20: the index is for grepping, and the defect was the SILENT mid-sentence cut, not the length): the first sentence, capped and marked, not the whole lead paragraph, which grew 449's index from 11,272 to 53,007 bytes, measured 2026-11-20 (`/tmp/t46-scripts/foreign_idx.py`), about 10k tokens more in each of its plan reviews (a GUESS: the 41,735 bytes at about four characters a token, not counted by a tokenizer). What it costs: 1,531 lines end ` [...]`, measured 2026-11-20 (`/tmp/t46-scripts/marked.txt`); no cut is unmarked, by construction - a line shorter than its lead paragraph always ends ` [...]`, whatever ended it (the sentence rule or the cap), the coordinator's round 2 (2026-11-20); the requirement's whole text is a grep of the spec away. `INDEX_CAP` is a CONVENTION ("about 400"), a knob.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a cited id read by whose it is, and an index line whole | n/a - no map | n/a | none | n/a |

<!-- plan-archive: archived 2026-11-20 -->
### T46 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a plan reviewer reads, for each decision or requirement the blocks name with another feature's number, that feature's text or a line saying it was not found, never the reviewed feature's same-numbered one; and every other requirement's index line its first sentence whole or ending ` [...]` - by construction, every line shorter than its lead paragraph ends marked.
2. **The constraints.** T46's line (carried from that feature's spec or plans or named as not found, never from the reviewed one; an index line whole; red first on T42's section and FR-009's line); T37's whole-decision reading (`paragraphs`, untouched); the lean plan bundle of feature 375's amendment 11; 100% line coverage of the plan crate by its own tests.
3. **Where each comes from.** O: T42's plan review, its bundle carrying 451's D5, D6 and D11, observed 2026-11-20, method: T42's review; O: feature 204's D5 and D6 in its spec, with no plan.md, read 2026-11-20 (`specs/204-guards-that-move-the-shell/`); O: FR-009 wrapped over four lines, read 2026-11-20 (`spec.md`).
4. **Do they describe the world here?** Yes: the plans write another feature's ids in the forms read (a number, `spec` or `plan`, a run-on list, a possessive), measured 2026-11-20 (`/tmp/t46-scripts/survey2.py`: 56 pairs, 6 sections changed); the requirements wrap their lead paragraphs, measured 2026-11-20 (3,463 of 4,686 run past one line, `/tmp/t46-scripts/foreign_idx.py`), and end their first sentence at ". ", measured 2026-11-20 (`/tmp/t46-scripts/idx2.py`).
5. **The order.** Independent of the other lanes; beside T44 (another crate, `rust/guard`).
6. **The exits.** Green: the four red tests green, `make rust-test` on the plan crate, its lint, format and cover, `make quick`, `make static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - two readers of a cited id, both in `bundle.rs`, found by the grep above, read 2026-11-20.
8. **The budget.** One landing.
9. **Done, measured.** This section's own bundle (`make decide F=451 T=T46`) carries feature 204's D5 and D6 from its spec and names house style's D11 as not found, measured 2026-11-20 (`grep` over its `spec-cited.md`). It carries 451's D5, D6 and D11 too, because this section names them as 451's ("carrying 451's D5, D6 and D11").
10. **Before moving a constant.** No constant moves; one is added, a CONVENTION labeled beside it in `bundle.rs`: `INDEX_CAP` (420 characters, the index line's cap, the coordinator's "about 400").
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a plan reviewer no longer judges a block against the reviewed feature's decision of the same number, nor an index line cut mid-sentence.

**Found and left?**
- A decision named with another feature's number was dropped without a word when that feature keeps its decisions in its spec (feature 204, 3 such pairs over every plan): fixed here (`lookup`, pinned by `another_feature_s_decisions_are_carried_from_it_never_from_this_one`).
- An id named as another feature's that the bundle could not find was dropped without a word (7 pairs): fixed here (`not_found`, pinned by the same test and `a_requirement_cited_as_another_feature_s_is_bundled_from_that_feature`).
- A number then a task's possessive ("444 T20's FR-043") read its id as the reviewed feature's and, not found there, dropped it without a word (found by T46's plan review, 2026-11-20): fixed here (`QUALIFIED`, pinned by `a_number_then_a_task_s_possessive_names_that_feature_s_id`).
- An index line could stop unmarked (at a `.` before a lowercase word, an "e.g." before a backtick, inside an open parenthesis; found by T46's plan reviews, 2026-11-20): fixed here by construction - a line shorter than its lead paragraph always ends ` [...]`, whatever ended it; `runs_on` only moves where a cut falls (pinned by `an_index_line_is_carried_whole`).
- A feature number's run of ids ran on into a clause naming another source ("449 T233's FR-023 and FR-024, and D5 and D11 in 451's sections" carried 449's D5; found by T46's plan review, 2026-11-20): fixed here (`own_run`: the run stops at its last comma, or before its last id, when the text after it opens "in N's", "of feature N" or another possessive; pinned by `a_number_then_a_task_s_possessive_names_that_feature_s_id`).
- `answered` read "444 FR-023" as the reviewed feature's FR-023 and could trim `request.md` to its amendment: fixed here (pinned by `another_feature_s_id_answers_no_amendment_of_this_one`).

**Performance work?** yes - a `[perf]` task in FR-013's sense: a decision handed to a plan reviewer under the wrong feature costs the review a round to undo (T42's). Not an engine stage: no counted operations, no performance checklist.


