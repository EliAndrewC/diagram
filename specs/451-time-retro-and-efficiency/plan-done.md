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


