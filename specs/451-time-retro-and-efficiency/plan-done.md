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

