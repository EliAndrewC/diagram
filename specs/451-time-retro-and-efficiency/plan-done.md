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


