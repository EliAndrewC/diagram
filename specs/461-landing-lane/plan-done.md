# 461-landing-lane - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-27 -->
### T02 (D12's other figures, the night's concurrency and the likeness test, completing phase 0's baseline)

- **Approach**: A sibling script, `dev/measurements/2026-11-27/461-t01-night-tokens/night-figures.py`, sits beside T01's
  `night-tokens.py`. Tokens stay in T01's script, and this one gives the rest of D12's table. Its record is T02's section of
  that directory's `results.md`.
  - **Sources.** It reads, under the common git directory, the pool log (replayed from its start), the event log's `make land`
    rows and the sampler's samples.
  - **Kept extracts.** `extract` keeps no-content extracts of all three under `kept/`, so the figures re-derive after the
    sampler's file rotates.
  - **The likeness test.** `like` is D12's test, which phase 5 reruns. Its three GUESS knobs are at the script's head:
    `LIKE_MIN_H` 8, `LIKE_TREES_BAND` 0.5 and `LIKE_LOAD_BAND` 0.75,1.25.
  - **The silent point.** D12 does not say whether "eight hours or more of builder work" is a wall span or tree-hours. The
    script takes the wall span, the plain reading, and prints tree-hours beside it.
  - **The headline figures.** Over 04:30Z to 14:29Z, 120 tasks landed on 31.80 tree-hours held, 3.77 a tree-hour. Of 39
    landing attempts, 11 landed, 17 were refused before a gate, 8 gates were red and 3 were refused after a green gate. Trees
    held came to 3.19 time-weighted, and the median load was 14.1 on 22 cores (observed 2026-11-27, method: `night-figures.py
    figures` over the kept extracts, `output-figures-0430-1429.txt`).
  - **The whole window.** Over 02:00Z to 14:29Z the same figures are 130 tasks on 41.75 tree-hours, 49 attempts with 19
    refused before a gate, 3.34 trees held and a load of 12.6 (observed 2026-11-27, method: `output-figures-0200-1429.txt`).
  - **Checks.** Trees held agree with the sampler's `held` field, 3.18 and 3.34. The load medians are `make sampler-report`'s.
    Over 02:00Z to 15:00Z the refusals reproduce the update note's 50 / 18 / 19 / 10 / 3 exactly (observed 2026-11-27, method:
    the outputs' cross-check lines, `make sampler-report SINCE= UNTIL=` and a `figures` run ending 15:00Z).
  - **Four trees.** The pool held four trees, not D12's three, with b1 held 58% of the headline window (observed 2026-11-27,
    method: the same output). The likeness test reads trees held, so it is unaffected.
  - **R3's baseline.** `baseline-task-time.txt` is kept unchanged as the before figure. Its cross-blocking row moved after its
    window closed (Found and left).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement, no engine or tooling code | - | - | - | - |

### T02 Approach (checklist part A)

1. **The goal, in the world.** Every figure of D12's table has a before figure in the form phase 5 will take, with the night's
   concurrency read. A likeness test exists that the after-measurement (T31) runs as written.
2. **The constraints.** FR-006, FR-007 and FR-010; D12's table and its likeness rule; the plan's knob table; and R3's kept
   baseline.
3. **Where each comes from.** R: plan D12, research R3 and the update note in `specs/449-rust-codebase/`. O: T01's record and
   this task's runs. G: the three likeness knobs, from the plan's knob table.
4. **Do they describe the world here?** Yes, each checked by a second source.
   - Trees held: the sampler's own `held` count.
   - Load: `make sampler-report`.
   - Refusals: the update note's count, reproduced exactly over its own span.
   - Kept against live: the same output, by `diff`.
5. **The order.** After T01, the same directory. Before any phase 1 edit, and before T31's after-measurement.
6. **The exits.** Green: both windows' outputs written from the kept extracts, the likeness test shown LIKE and NOT LIKE.
   Red: what failed is recorded and the task set down. A claim that it cannot be done is ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Both `figures` runs re-derive from `kept/` to the same output as a live run, apart from the source
   line (observed 2026-11-27, method: `diff`). `output-like.txt` shows the night LIKE itself, a 06:00Z start LIKE, and three windows NOT LIKE, each with the band it
   missed (observed 2026-11-27, method: `diff` and the runs there).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing fixed here. A measurement changes no behavior.

**Found and left?**
- `make task-time`'s cross-blocking row for a closed window grows after the window ends. The 02:00Z window gave 32.3 min at
  7af15e21ab, run about 14:40Z, and 53.7 min at eb205722a4, run about 17:55Z (observed 2026-11-27, method: both runs'
  headers). The row counts a tree free until its next
  handout, and t271's and t270's next handouts came after the first run (observed 2026-11-27, method: both runs' headers, the
  pool log's take and release rows). Visible effect: phase 5's before and after cross-blocking differ by when each was run.
  This record gives both windows at one commit. Not fixed here: a measurement task changes no tooling. Filed as T33; lands
  before T31.

**Performance work?** Yes, as a `[perf]` measurement (451 FR-013). It measures where time goes in the landings and the pool, but
it changes no engine speed, so the performance checklist does not apply.


<!-- plan-archive: archived 2026-11-27 -->
### T05 (phase 1's first task: the XIII baseline, D3's no-commit form and its own verified end, D4's flight question)

- **Approach**: built in two builders (a build half and this closing half), in pool tree `diagram-backlog-t270` at base 054d48a41c.
  - **The XIII baseline** (observed 2026-11-27, method: the runs below in the pool tree itself, clean at 054d48a41c before any
    edit). DEPARTURE, accepted by the session: the line's `git worktree add --detach` was not made - the brief forbade making a
    worktree and a hand `git worktree add` is refused (451 T285) - so the clean pool tree stood in for the detached worktree.
    `make rust-test CRATE=rust/gate/crates/land` 175 passed, `.../task` 147, `.../tree` 59, `rust/guard` 616, each 0 failed, one
    crate a call (the line's one four-crate call exits 2 on a joined manifest path: T32). `make hooks-test HOOKS_ALL=1`: 64 guard
    suites green, guard-messages 366 wordings - run ONCE as the task's baseline measurement, against the CHECKS line's bar on it as a
    builder's check; the session accepted it as a measurement, not a check.
  - **The no-commit form** (`rust/gate/crates/land/src/land/carry/apply.rs`, new): `carry::apply::apply(root, sha) -> Applied`
    (`Verified { files, resolved }`, `Conflict`, `Refused`, `NotVerified`) runs `git cherry-pick -n` with the carry's rules whole
    (`resolve_all`), and `carry::apply::verified(root, sha, kept)` is its own verified end, askable alone: nothing in progress
    (`unfinished::refusals` but its staged and unmerged lines), nothing unmerged (in this form's words: "committing nothing", never the
    carry's "and commit", which would move HEAD off the base), and each non-spec file of `sha` held by the WORKING TREE - changed there
    against HEAD, or at the commit's blob (`git hash-object`), a file the commit deletes held where the tree lacks it too, a file a rule
    resolved held whatever its text. HEAD never moves; nothing calls `--continue`, `--skip` or `spent()`, so no done ref is deleted.
    A conflict no rule resolves leaves EVERY unmerged path in the tree (the rules' all or none), each named, those a rule would
    resolve marked so. In `carry.rs`: `enum Form { Commit, NoCommit }`, `missing(.., form)`, the failed page regeneration's hand step
    by form (`Form::then`), the commit lookup shared as `located()`.
  - **A defect of the new form fixed** (fixed here): `resolve_all` restored a cleanly merged tasks.md's boxes from
    `CHERRY_PICK_HEAD`, which a `-n` pick never writes (probed 2026-11-27, method: `git cherry-pick -n` in scratch repositories), and
    `git()` ignores exit codes, so the error text went in as a side and a bare box stayed bare. It now names the picked sha; in the
    commit form that sha is `CHERRY_PICK_HEAD`, so the carry is unchanged.
  - **The `--no-commit` flag is KEPT** (`l7r-gate land --carry --no-commit <tree> [<commit>]`, and `"" <sha>` for a commit the
    clone's objects hold): T07 is in the land crate and calls `apply` in process, but T09's handout is in the `task` crate, which
    `land` builds on, so `task` cannot call it in process. Moving the form below `task` would carry the carry's rules with it, which
    build on `cohort` (`make_docs::write`), a crate `task` does not build on; the command form is T09's door, and `task` already runs
    `l7r-gate` as a command (`builder_tree`'s `measure sampler start`). Tested through `carry::cli` in five of the form's tests, and by
    `a_commit_the_clone_holds_is_applied_by_its_sha_alone_and_its_done_ref_kept` (the sha-alone form T09 would call: applied, HEAD
    unmoved, the done ref kept). No Makefile target: none was asked for.
  - **D4's flight question, answered by a test**: YES - `land::inproc::tests::a_claims_round_marked_in_a_builder_s_tree_is_in_flight_from_the_lane_s_tree`
    writes the mark where `make claims-bundle` writes it from a pool tree (the tree's `--git-common-dir`/claims-in-flight) and
    `Inproc::Real.in_flight` sees it from a second linked worktree (the lane's) and from the clone; a separate clone does not. The pool
    trees and `diagram-backlog-land` are linked worktrees of the clone (observed 2026-11-27, method: `git worktree list`).
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land`, the form's tests `carry::tests::no_commit`):
    with the carry's own end, 3 passed and 5 failed (NotVerified on the staged paths); with the filter, 7 and 1 (the tasks.md read
    from `CHERRY_PICK_HEAD`); with the sha, 8 and 0. The conflict refusal naming only the paths no rule resolves: 7 and 1, then 8.
    The flight mark in the builder tree's private git dir: 2 and 1, then 3 with the common dir. The two tests written after their
    fix - the unmerged wording of `verified()` and the delete where the base already lacks the file - were shown red by breaking each
    line (the wording back to "and commit"; the absent file read as `(0, "")`): 6 passed, 2 failed, the two tests, then restored
    (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::carry::tests::no_commit"` on the broken lines).
    After: the land crate 185 passed (175 + 10); `make builder-checks CRATE=rust/gate/crates/land` green. The brief's CHECKS line also
    had this builder run the crate's coverage, which named no line; it is no exit of this task (FR-002, SC-002: a builder runs no
    coverage), the gate's coverage at the landing is.
  - **For T07** (left to T07, nothing of it built here):
    - T07 must `git add` EVERYTHING before its commit: the verified end reads the working tree, not the index, so an unstaged file
      would verify and then be left out of the commit.
    - At a resume `verified(root, sha, &[])` cannot tell a file a rule resolved back to the base's own text (a regenerated page, records
      the base already held) from one missing: both read as unchanged against HEAD at a blob not the commit's. The resume comes in two
      shapes. (a) After a verified apply whose first pass (step 4) refused: the apply's `resolved` list is gone with its process. T07
      writes it at the apply to a file in the tree's own git dir - `<git dir>/l7r-hand-in/<feature>-<task>.resolved`, one `path (rule)`
      line each, written beside the scratch ref and deleted with it at step 6 - and passes its lines as `kept` to `verified()`. (b) After
      a conflict: nothing was resolved (all or none), so there is no list yet; the paths the refusal marks "its rule would resolve it"
      need not be resolved by hand - T07 can run `resolve_all` at the resume on the paths still unmerged (its rules read the index's
      stages, which an unmerged path keeps), write what it resolved to the same file, and pass it as `kept`. If T07 takes (b), the
      Conflict wording ("resolve each") should then tell the builder to resolve only the paths with no rule.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the baseline, the no-commit form, the flight test | n/a - no map | n/a | none | n/a |

### T05 Approach (checklist part A)

1. **The goal, in the world.** A builder's scratch commit can be applied onto a base with the carry's rules and left uncommitted,
   with an end that says whether it held, so T07's hand-in can run the first pass and commit; T09 can reach it as a command; and a
   claims round marked from a builder's tree is seen from the lane's.
2. **The constraints.** D3 (the no-commit form and its own verified end), D4 (the flight question), D14 (a done ref superseded by its
   successor's hand-in, so the form deletes none), FR-002; constitution XIII (the baseline before the feature's first code edit).
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md); R: `carry.rs`'s own doc on its end; O: the scratch-repository
   probes of `git cherry-pick -n` and the tests above (2026-11-27).
4. **Do they describe the world here?** Yes: the probes ran on the container's git, and the flight test builds linked worktrees as
   the pool's are (observed 2026-11-27, method: `git worktree list` in the clone).
5. **The order.** First of phase 1, after the baseline; before T06-T10.
6. **The exits.** Green: the land crate's tests and `make builder-checks` as above; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/gate/crates/land` 185 passed, 0 failed, and `make builder-checks
   CRATE=rust/gate/crates/land` green (observed 2026-11-27, method: the two commands).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The `CHERRY_PICK_HEAD` read: a hand-in whose tasks.md merged cleanly beside another conflict would have left a
   box bare, its research line lost - the defect the test pins.

**Found and left?**
- `make rust-test CRATE="<several crates>"` exits 2 on a manifest path of the crates joined (observed 2026-11-27, method: T05's
  four-crate baseline call in pool tree `diagram-backlog-t270`), so any Verify line naming several crates fails as written.
  Not fixed here: a Makefile and `rustc` crate change outside the land crate, not this task's. Filed as T32; lands before T12.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-27 -->
### T06 (phase 1: the first pass in its hand-in mode, D4)

- **Approach**: built in pool tree `diagram-backlog-t270` on T05's commit 913c926a45. Only the land crate changes; nothing calls the
  hand-in mode outside its tests until T08 wires it into `hand_in.rs` step 4.
  - **The mode** (`rust/gate/crates/land/src/land/cheap.rs`): `pub enum Pass { Landing, HandIn { base } }`, re-exported as
    `land::Pass`. `cheap_refusals(d, tasks, note, pass, deferred)` takes it; the four gates' loop moved to its own
    `gate_refusals`, so the pass stays under clippy's 100-line bar. The base is the caller's, because the knob
    `HAND_IN_BASE` is T07's (the clone's HEAD in phase 1, `origin/main` from phase 2, D3). For the length of the pass the base sits
    in `Land::hand_in`, which three readers consult, so no signature below the pass changes:
    - `delta_names` reads `git diff --name-only <base>`, the working tree against the base, where the landing reads
      `origin/main...HEAD` (D4). `open_claims_refusal` and `others_in_progress` read the delta through it.
    - `named::held` reads `git ls-files -z -co --exclude-standard`, the tree as applied, where the landing reads `ls-tree HEAD`. At
      hand-in HEAD is the base, which lacks every file the work adds, so a task naming its new module would be falsely refused.
    - `record_commit` leaves a record uncommitted where the landing commits it. Six commit sites go through it (observed 2026-11-27, method: reading `cheap.rs` and `land.rs`): the ledger rows,
      the make-targets page, the claims' moved rows, the carries, the known drifts and the escape records. Two of them, the carries
      and the known drifts, ran `git commit` with no pathspec, so on a tree holding a staged `cherry-pick -n` they would have
      committed the builder's whole work. Their `git add` still runs; T07 adds everything before its commit (T05's note).
  - **D4's left column, asked at hand-in**: each task's tick check (`landed=false`, as today), the phase checklist, the open
    claims, the named files, the stale coverage-exempt entry, the ledger rows owed, the four gates and the push's table
    (`push-checks --every`). `review-gate.sh` and `plan-gate.sh` are given the base as their range argument (`RANGED`), since both
    default to `origin/main...HEAD`. The claims gate is routed through `claims_route` at hand-in, whether or not a `deferred` list
    is given. An owed claim with no check in flight is a stop carrying the cure, which names `make claims-bundle OWED=1`. An owed
    claim with a round in flight is the lane's: it goes to `deferred` when given and is otherwise quiet. Any other claims refusal,
    a form problem for example, is the builder's stop. At hand-in, every stop's "run make land again" reads "run make builder-done
    again".
  - **D4's right column, not asked at hand-in**: `writer_refusal`, the mark's hold (`ready.rs`'s `hold`) and the red-gate tripwire.
    The gate's stamp rows are skipped in both forms, as before (`AFTER_GATE`). No coverage runs, and the fixture's log shows that
    none is asked (FR-002).
  - **Kept in both forms, a choice**: `unrelated_history` and `others_in_progress` are in neither column. On the plain reading,
    the mode turns off only what the right column names, so both stay. `others_in_progress` reads the hand-in's delta.
  - **Closes 451 T307 part 2** (the push refusing after the gate; every push check also in the first pass). T307 part 2 put the
    push's table in the landing's first pass; T06 keeps it in the hand-in form too, so a builder meets the push's refusals at
    hand-in. A pointer is on 451 T307's box.
  - **Tests**: the new `land/cheap/tests/hand_in.rs` has six tests (observed 2026-11-27, method: the file).
    - Every left-column refusal fires at hand-in with its fixing command, and no coverage is asked.
    - An owed claim with a round in flight is the lane's, and a form problem is the builder's.
    - The right column refuses at landing and is quiet at hand-in.
    - The records are left in the tree with HEAD unmoved, and the landing still commits them.
    - A named file is held by the applied tree, not by the base.
    - A Rust stage's checklist and open claims are read from the staged work.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::cheap::tests::hand_in"`
    with each line below broken in turn and then restored, by `t06-mutate.py` in the scratchpad):

    | line broken | passed, failed of 6 | the test(s) red |
    |---|---|---|
    | the base not given to `review-gate.sh`/`plan-gate.sh` | 5, 1 | every_left_column_refusal |
    | the claims gate not routed at hand-in | 4, 2 | every_left_column_refusal, an_owed_claim_with_a_round_in_flight |
    | every routed claims refusal the lane's | 5, 1 | an_owed_claim_with_a_round_in_flight |
    | "run make land again" left as it is | 5, 1 | every_left_column_refusal |
    | `writer_refusal` asked at hand-in | 3, 3 | every_left_column_refusal, the_lane_s_checks_are_quiet, the_records_are_written |
    | the mark's hold asked at hand-in | 5, 1 | the_lane_s_checks_are_quiet |
    | the tripwire asked at hand-in | 5, 1 | the_lane_s_checks_are_quiet |
    | the records committed at hand-in | 5, 1 | the_records_are_written |
    | the named files read from HEAD | 5, 1 | a_named_file_is_held_by_the_applied_tree |
    | the delta read from `origin/main...HEAD` | 5, 1 | a_rust_stage_s_checklist_and_open_claims |
    | the tick refusal deleted | 5, 1 | every_left_column_refusal |
    | the phase checklist deleted | 5, 1 | a_rust_stage_s_checklist_and_open_claims |
    | the open claims deleted | 5, 1 | a_rust_stage_s_checklist_and_open_claims |
    | the named files deleted | 5, 1 | a_named_file_is_held_by_the_applied_tree |
    | the stale coverage-exempt entry deleted | 5, 1 | every_left_column_refusal |
    | the ledger rows owed deleted | 5, 1 | every_left_column_refusal |
    | the push's table deleted | 5, 1 | every_left_column_refusal |
    | `entry-gate.sh` not asked (its slot given to the claims gate again) | 4, 2 | every_left_column_refusal, an_owed_claim_with_a_round_in_flight |

    The mode is new, so on the old code these tests do not compile. Each line was broken, its tests were seen red, and the line was restored.

    After (observed 2026-11-27, method: the two commands): `make rust-test CRATE=rust/gate/crates/land` 191 passed, 0 failed (185 + 6),
    and `make builder-checks CRATE=rust/gate/crates/land` green in 16 s.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the first pass's hand-in mode | n/a - no map | n/a | none | n/a |

### T06 Approach (checklist part A)

1. **The goal, in the world.** At hand-in, a builder's tree gets every refusal the builder can cure, each with its command, and
   none that belongs to the lane. The pass leaves HEAD at the base and its records in the tree, so the hand-in's one commit takes
   them along with the work.
2. **The constraints.** D4's table and its "no coverage", FR-002, D3's base by phase (the knob is T07's), constitution XIII (the
   landing's pass is unchanged: every existing first-pass test passes as it did).
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: plan D4; `review-gate.sh` and `plan-gate.sh` both
   take `RANGE="${1:-origin/main...HEAD}"`. O: the tests above.
4. **Do they describe the world here?** Yes for the pass's own readers, whose tests run on a scratch clone holding staged work.
   For the gates that compute their own delta, see Found and left.
5. **The order.** After T05, beside T07, before T08, which calls this mode from `hand_in.rs` step 4.
6. **The exits.** Green: the land crate's tests and `make builder-checks`; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/gate/crates/land` 191 passed, 0 failed (185 + 6), and `make builder-checks
   CRATE=rust/gate/crates/land` green (16 s) (observed 2026-11-27, method: the two commands).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The pathspec-less commits of the carries and the known drifts. Run as they stood on a hand-in tree, they
   would have committed the builder's applied work as a "claims findings filed" commit on the base. `record_commit` prevents
   that, and the records test pins it.

**Found and left?**
- At hand-in, three checks compute their own delta from the merge base of HEAD with origin/main, not from the hand-in base: the
  push's table (`cohort`'s `push.rs` `delta()`), `record-owed` behind `entry-gate.sh` (`owed.rs` `merge_base`) and the claims gate.
  In phase 1 the tree stands on the clone's HEAD, which is ahead of origin/main by every staged batch, so a hand-in may be refused
  for another task's owed record, claim or push row (observed 2026-11-27, method: reading those functions against T06's pass). From
  phase 2 the base is origin/main and these checks judge the work alone. Not fixed here: the code is in crates outside the land crate,
  and phase 1 needs a ruling on whether to accept it. Filed as T34; lands before T10.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-27 -->
### T04 (plan, "Found and left": the land help and the gate line say a coverage run happens that does not)

- **Approach**: the Makefile's `land` help said the first pass ran "the changed modules' coverage", and `long_runs.rs`'s gate line said "(the changed modules' coverage beside it)", though `long_runs.rs`'s own doc says that check went with the Python tests (449 FR-001b). Both restated: the help says no coverage runs beside the gate, the gate line names the gate alone. The help's `[COVER_OK="<reason>"]` went with it, and the `land` recipe's `COVER_OK` export and its escape log: nothing reads `COVER_OK` in the land crate (a grep over `rust/`, 2026-11-27), so an escape that escapes nothing was being recorded. `docs/make-targets.html` regenerated by `make docs`. Red first: `long_runs/tests.rs`'s `the_gates_the_stamp_names_run_and_the_cohort_beside_make_done` now pins the gate line whole and no "coverage" in the output; on the old code 1 failed, 8 passed (`make rust-test CRATE=rust/gate/crates/land ONLY="land::long_runs::tests"`, 2026-11-27), green after.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the words | n/a: words only, pinned by the test above | n/a | n/a | n/a |

### T04 Approach (checklist part A)

1. **The goal, in the world.** A reader of `make help` and of `make land`'s output is told only of checks that run.
2. **The constraints.** XIV (a wrong statement is a defect fixed where found); `long_runs.rs`'s doc (449 FR-001b).
3. **Where each comes from.** R: `long_runs.rs` lines 1-3; O: the grep of `COVER_OK` and of "modules' coverage" over `rust/`, `scripts/` and the Makefile, 2026-11-27.
4. **Do they describe the world here?** Yes: no coverage step is in `long_runs.rs`, and `COVER_OK` is read by no Rust.
5. **The order.** Phase 0; before nothing.
6. **The exits.** Green: the test above green, `make builder-checks CRATE="rust/gate/crates/land"`, `make help` read back. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make help | grep 'land one task'` names no coverage; the land crate's tests green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of the help and the landing's output is no longer told a coverage run happens beside the gate.

**Found and left?**
- `scripts/land-alone.sh` line 573 still forwards `COVER_OK` to the inner landing, and the Makefile's `FREE_TEXT` still names it; both are harmless (it is empty and read by nothing) and go with land-alone in T30. Not a defect: no visible effect, so not filed.

**Performance work?** no.

<!-- plan-archive: archived 2026-11-27 -->
### T07 (phase 1: the hand-in's apply, its conflict stop and its resume, D3 steps 1-3, 5, 6)

- **Approach**: built in two builders (a build half and this closing half), in pool tree `diagram-backlog-t269`.
  - **What is built** (`rust/gate/crates/land/src/land/hand_in.rs`, new, its tests `land/hand_in/tests.rs`; the module doc lists
    the steps as built): `l7r-gate land --hand-in <tasks> <feature>`, `MSG`, `GUARD` and `HAND_IN_BASE` from the environment. In the
    builder's pool tree: the knob checked; `task`'s `builder_done::found` (the arguments, the pool tree) - a new `pub struct Found`
    in `rust/gate/crates/task/src/builder_done.rs` that `run` and `commit` are now rebuilt on, behavior unchanged (its 12 old tests
    pass, one new, 13 in all: observed 2026-11-27, method: `#[test]` counted in `builder_done/tests.rs` at HEAD and in the tree, the
    crate's run in item 9); the resume test (does `refs/l7r/hand-in/<feature>-<first task>` stand?); on a first run today's refusals
    (`Found::unready`), the base found, the sweep, `git add -A` and the SCRATCH commit, a scratch ref a task (a bundle `T=a,b` gets
    one each, as the done refs), `<git dir>/l7r-hand-in/<key>.base` written, the tree detached at the base, and T05's
    `carry::apply::apply`. Each outcome: Verified writes the rules' resolved list (`<key>.resolved`, one `path (rule)` line each)
    and goes on to commit; a Conflict leaves the tree with it, in the hand-in's own words (resolve only the paths not marked "its
    rule would resolve it"; `apply::told` is left for T09's command door); Refused puts the work back uncommitted on its old base,
    the refs and files deleted; NotVerified says so and leaves the tree for a resume. The RESUME reads the base file and requires
    the tree's HEAD to equal it (else a stale-ref refusal naming `git show` and `git update-ref -d` - another tree's ref, or a tree
    moved off its base, is never resumed), puts the still-unmerged paths through `resolve_all(.., Form::NoCommit)` (only the paths
    no rule resolves are named again; what the rules resolve is added to the list), and asks `verified` with the list as `kept`.
    The commit: `git add -A` (T05's note: the end reads the working tree), a conflict's markers in a staged file refused, the first
    pass (`FirstPass = &dyn Fn(&Path) -> Vec<String>`, `cli` passes none: T08 wires T06's hand-in mode there), `git add -A` again so
    the records a clear first pass writes go in with the work (D4), an empty staged delta "nothing to hand in" with the release
    named, else `git commit -C <scratch>` (its message and author, so MSG and GUARD given at a resume are not re-read and the guard
    check not asked twice), `Found::kept(sha, true)` (the done ref, the `done` line with `"handed_in": true`, the tree released, the
    next two commands - the `make land` line kept, since in phase 1 the session lands by hand; T08 replaces it), and the scratch
    refs and files deleted. `land.rs` gains the arm only (`mod hand_in;` and `Some("--hand-in")`, 873 to 875 lines, observed 2026-11-27, method: `wc -l`; D15).
    Visibility: `carry::Form` and `carry::resolve_all` `pub(super)`, `carry::apply::ended` `pub(crate)`. The knob's audit entry
    `dev/audits/hand-in-base.md` (`covers: HAND_IN_BASE`). `rust/gate/CLAUDE.md`'s land row names `hand_in.rs` and `--hand-in`.
  - **Decision: the base is found BEFORE the scratch commit** (the session's ruling (1), accepted). D3's step order makes the
    scratch commit (step 2) before the fetch (step 3). Finding the base first means a `git fetch origin` that fails refuses with
    nothing done - no scratch commit or ref to undo, the work still uncommitted in the tree
    (`a_fetch_that_fails_refuses_with_nothing_done`) - and changes nothing else: the base is read from outside the tree, so
    finding it before or after the tree's own commit gives the same sha. Label: deliberate deviation from the plan's step order,
    for a refusal that leaves nothing behind.
  - **Decision: `git fetch origin` runs only where `HAND_IN_BASE=origin`** (the session's ruling (2), for the plan review to rule
    on). The task line says "`git fetch origin`" with no condition. In phase 1 (`clone`, the default) the base is the clone's HEAD,
    nothing reads `origin/main`, and the clone's HEAD is already in the tree's object store (a pool tree is a linked worktree of the
    clone, observed 2026-11-27, method: `git worktree list` in the clone, as T05 found): a fetch there would cost a network round a
    hand-in and could only refuse a hand-in for a remote it does not use. D3's "The base by phase" reads the fetch as phase 2's,
    where `origin/main` is the base (`the_base_is_origin_main_after_a_fetch_where_the_knob_says_origin`); its words: "in phase 1 the
    coordinator still carries into its clone, so the clone's HEAD is where work lands ... the hand-in applies onto the clone's HEAD
    then (`clone`). From phase 2, when landings leave the clone, it is `origin/main` (`origin`)". Label: the literal line
    read through D3's phases; if the review holds to the literal reading, the fetch moves outside the `if`, nothing else changes.
  - **T39, red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::hand_in::tests"`):
    T05's test comment holds that no scratch apply reaches NotVerified on a FIRST apply (a `-n` pick that exits 0 leaves its files
    in the tree), but a resume drives the same `ended` line: `a_file_a_rule_resolved_back_to_the_base_s_text_stays_resolved_past_a_failed_end`
    conflicts on `rust/lib.rs` (no rule) and `docs/a.md` (the words rule, which merges the builder's "ONE two three" and the
    clone's "ONE TWO three" to the clone's own text); the builder takes the base's side on lib.rs, so the resume resolves docs/a.md
    by its rule and its end fails on lib.rs (NOT VERIFIED); mended, the third run must land. Before the fix: 15 passed, 1 failed -
    no `.resolved` after the NOT VERIFIED; with that assertion set aside, the third run itself red, `hand-in: NOT VERIFIED ... the
    working tree does not hold the applied commit's docs/a.md` (the visible effect: a hand-in that could never be resumed to its
    commit). After: green, with T07's other tests (the counts in item 9). `carry::tests::no_commit`'s `ended` test now asserts the list survives NotVerified;
    `apply::told`'s wording is unchanged.
  - **`handed()`'s Err path, driven** (the build half's untested branch): `a_git_step_that_fails_is_said_with_nothing_done` - an
    origin that fetches but holds no `main` (its branch renamed `trunk`), so `git rev-parse origin/main` fails before the scratch
    commit: `hand-in: git rev-parse origin/main failed in ...`, exit 2, no scratch ref, the work uncommitted. It passed on first
    write; shown red by breaking its line (`run`'s Err exit 2 changed to 0): 16 passed, 1 failed, that test, then restored
    (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::hand_in::tests"` on the broken line). A `git` step
    failing AFTER the scratch commit CAN be staged, and it was a defect, fixed here: a `reference-transaction` hook aborts
    `update-ref` (probed 2026-11-27, method: a vetoing hook in a scratch repository, git 2.53.0: `fatal: ref updates aborted by
    hook`, exit 128), and the scratch commit then stood on the tree's HEAD with no ref, so the next run found nothing to commit and
    the hand-in could not go on. Now every step past the scratch commit (`placed`: the refs, the base file, the detach, the apply)
    undoes it on failure as an apply Refused is undone (`Hand::undo`: the tree at the scratch commit's content, HEAD at its old
    base, the work uncommitted, the refs and files deleted). Red first:
    `a_git_step_that_fails_after_the_scratch_commit_puts_the_work_back_uncommitted` (a hook vetoing `refs/l7r/hand-in/`), 17 passed,
    1 failed on the code before (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land
    ONLY="land::hand_in::tests"`); green after, the hook removed and the next run landing the work.
  - **Red first, the build half** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land
    ONLY="land::hand_in::tests"`): with `run` a stub returning "not built", 0 passed, 13 failed; built, 13 and 0. Written after the
    build and each shown red: the markers refusal; the clear first pass's records committed with the work (14 passed, 1 failed -
    the done commit held only `rust/held.rs` - until the second `git add -A`). Two mutations each shown red, then restored: the
    resume's `resolve_all` replaced by a bare Conflict (12 passed, 1 failed, the conflict-and-resume test); the `git add -A` before
    the commit removed (12 passed, 1 failed, the unadded `rust/extra.rs` left out), observed 2026-11-27, method: the same command on
    each broken line.
  - **The tests** (`land/hand_in/tests.rs`, 18, observed 2026-11-27, method: `#[test]` counted): a clean hand-in onto a clone HEAD that moved on (one commit, parent the clone's
    HEAD, `handed_in: true`, the scratch ref and files gone, the tree free); a conflict with the base refused naming rust/lib.rs and
    marking tasks.md rule-resolvable, re-run unresolved naming only lib.rs, resolved and resumed with tasks.md resolved by its rule
    and an unadded file committed; a first-pass refusal committing nothing and its resume reading the `.resolved` list; a
    resolution that drops the work NOT VERIFIED; T39's above; a scratch commit a pre-commit hook refuses; the final commit refused
    and resumed; an apply Refused put back; a base already holding the work; a stale scratch ref; `origin`; a failed fetch; the
    two Err paths above; the knob, the arm's usage and today's guard-file refusal; `must()`'s error; markers in an added resolution; a
    clear first pass's records committed.

Built here: T39 - the no-commit apply's NotVerified keeps the rules' resolved list (`Applied::NotVerified { fails, resolved }`, `carry::apply::ended`), and the hand-in writes it to `<key>.resolved` on NotVerified as on Verified (`Hand::ruled`), so a resume's end still holds a file a rule resolved back to the base's own text

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in's apply, stop and resume; T39 | n/a - no map | n/a | none | n/a |

### T07 Approach (checklist part A)

1. **The goal, in the world.** A builder's `make builder-done` (once T08 points it here) lands the work as one commit on where
   work lands - the clone's HEAD in phase 1 - with the conflicts against work landed since answered in the builder's own tree,
   resumable after a stop, and nothing committed or rewritten on a refusal.
2. **The constraints.** D3 steps 1-3, 5, 6 and "The base by phase"; D15 (the arm only in `land.rs`); FR-002; T05's no-commit form
   and its notes for T07 (everything staged before the commit; the rules' list kept for the resume, shapes (a) and (b)); no
   history rewritten.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md); R: D3, T05's section; O: the scratch-clone tests above
   (2026-11-27).
4. **Do they describe the world here?** Yes: the tests build a clone with a pool tree as a linked worktree held in the pool's
   registry, as `make builder-tree` leaves one (observed 2026-11-27, method: `git worktree list` in the clone).
5. **The order.** After T05; beside T06; before T08 and T09.
6. **The exits.** Green: the land and task crates' tests and `make builder-checks` as below; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/land rust/gate/crates/task"` green, the land crate
   203 (185 before T07, +18) passed and the task crate 148 (147 + 1), 0 failed (observed 2026-11-27, method: that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T39: a hand-in whose resume follows a NOT VERIFIED could never commit - its end named a file a rule had
    resolved as missing (the red above); and a hand-in whose scratch ref git refused was left stuck with its work committed on the
    tree's HEAD and no ref, the next run finding nothing to commit (the red above).

**Found and left?** none - T39, filed by the build half, is fixed here (the `Built here:` line above); the failed step past the
scratch commit, fixed here.

**Performance work?** no - it moves the landing's conflict turns from the session to the builder (D3's cost line) but makes no
step faster and measures no time.


<!-- plan-archive: archived 2026-11-27 -->
### T34 (T06's plan reviewer, 2026-11-27: three hand-in checks read their own delta from the merge base with origin/main)

- **Approach**: built in pool tree `diagram-backlog-t270` on main's f412c319b7. The hand-in base reaches every check that reads its own
  delta through one variable, `L7R_DELTA_BASE`, read by one function.
  - **The reader** (new, `rust/gate/crates/core/src/delta_base.rs`): `named(root)` gives the commit the variable names, resolved by
    `git rev-parse --verify <base>^{commit}`. It gives None when the variable is unset, empty or names no commit; each check then
    falls back to its own merge base. So a base that cannot be read never narrows what is judged. A test build reads a thread-local
    value (`delta_base::with`) and never the process's, as `build::with` does.
  - **Where it is read**: each site keeps its old call as the fallback (`named(root).unwrap_or_else(<the merge base, as before>)`).
    - The push-gate's `delta()` (`cohort` `push.rs`). It serves `push-gate skip|pass` for the claims and entry gates. At hand-in
      a work holding no engine code or record now skips those gates ("nothing to judge"), where another task's staged code below the
      base had made them run.
    - `record-owed`'s base (`owed` `delta.rs` `Delta::merge`, which `merge_base`, `entry_base` and `translation_base` all read) and
      `owed.rs` `merge_base`.
    - The claims gate's sorting of introduced, pre-existing and carried findings (`claims` `carry.rs` `classified`).
  - **Who sets it**: only `make land`'s first pass. `gate_refusals` hands it to each of the four gates, and `push_refusal` hands it
    to `push-checks --every`. Each gets the hand-in base at hand-in, and an empty value at landing. The empty value makes an exported
    variable inert for the landing's own first pass.
  - **The task line's pointer, made precise**: the push's table is not judged through `push.rs` `delta()`. That function serves
    only the push-gate skip of the claims and entry gates. The table's delta-scoped rows (spec-lint, audit-register,
    gm-attributions, gm-questions, closing) each compute their own merge base in other crates. They now receive the variable but
    do not yet read it: see Found and left.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=<crate> ONLY=<module>` with each line below broken in turn and
    restored, by `t34-mutate.py` in the scratchpad):

    | line broken | crate, ONLY | passed, failed | red |
    |---|---|---|---|
    | `push.rs` `delta()` reads the merge base only | cohort, `push::tests::at_a_hand_in` | 0, 1 | at_a_hand_in_the_delta_is_read_from_the_base_it_names |
    | `Delta::merge` reads the merge base only | owed, `record::delta::tests::at_a_hand_in` | 0, 1 | at_a_hand_in_the_record_owed_is_read_from_the_base_it_names |
    | `owed::merge_base` reads the merge base only | owed, same | 0, 1 | the same |
    | `classified` reads the merge base only | claims, `claims::carry::more::at_a_hand_in` | 0, 1 | at_a_hand_in_a_finding_below_its_base_is_not_introduced |
    | the four gates not handed the base | land, `land::cheap::tests::hand_in` | 6, 1 | the_checks_that_read_their_own_delta_are_handed_the_hand_in_base |
    | `push-checks` not handed the base | land, same | 6, 1 | the same |
    | the landing handing a non-empty value | land, same | 6, 1 | the same |

    The reader is new, so on the old code these tests do not compile. Each line was broken, its test was seen red, and the line was restored.
    - Each fixture puts another task's staged commit between origin/main and the hand-in base.
    - The push-gate: from the merge base it judges that commit's code and runs the claims gate. From the base, it judges nothing.
    - `record-owed`: from the merge base it lists the commit's record units as owed. From the base, "no record check is owed".
    - The claims gate: a DRIFTED finding on that commit's code is "introduced" from the merge base and "pre-existing" from the base.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in base handed to the checks that read their own delta | n/a - no map | n/a | none | n/a |

### T34 Approach (checklist part A)

1. **The goal, in the world.** At hand-in, the checks that work out their own delta judge the builder's work alone. In phase 1 they
   do not judge every batch staged in the clone below it.
2. **The constraints.** FR-002 (a builder's tree meets the refusals the builder can cure), D3's base by phase, D4. Constitution XIII:
   with the variable unset, every check reads the merge base as before, and every existing test passes.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: plan D3, D4 and T06's section. O: the red-first table.
4. **Do they describe the world here?** Yes for the three checks named in the task line: each fixture stands as a phase-1 hand-in tree
   does, with a staged commit below the base and the work uncommitted on it. The claims gate's owed claims are not base-dependent: see
   FOR THE SESSION in the report.
5. **The order.** After T06, before T08, which wires the hand-in mode into `hand_in.rs`.
6. **The exits.** Green: the tests and `make builder-checks` of core, cohort, owed, claims and land. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first table above, and `make builder-checks` over core, cohort, owed, claims and land.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The checks judge less only where a hand-in names its base. With the variable unset or empty, as at every
   landing and push, nothing changes.

**Found and left?**
- The push table's delta-scoped rows still read the merge base with origin/main: spec-lint, audit-register, gm-attributions,
  gm-questions, the rows' `needs_run` gate, and closing's literal `origin/main...HEAD`. In phase 1 each may refuse a hand-in for another
  staged task's finding (observed 2026-11-27, method: reading each row's base). Not fixed here: those sites lie in the checks, reviews, tree and cohort crates beyond the task line's three (observed
  2026-11-27, method: grep of `merge-base` under `rust/gate/crates`); each is a one-line read of `delta_base::named`. Filed as T37; lands before T08.
- The first pass's in-process claims calls cannot see a variable handed to child processes: the carry's `touches_engine` and the
  open-claims report, both in `make land`'s own process. In phase 1 the carry may file another staged task's findings into the
  builder's tree (observed 2026-11-27, method: reading `cheap.rs`'s `self.claims` calls). Not fixed here: it needs the base passed
  through the in-process claims door, a change of its signature. Filed as T38; lands before T08.

**Performance work?** no.

<!-- plan-archive: archived 2026-11-27 -->
### T37 (T34's Found and left: the push table's delta-scoped rows read their own merge base at hand-in)

- **Approach**: built in pool tree `diagram-backlog-t270` on T34's 77423b3b2d. Each row T37 names now asks
  `l7r_gate_core::delta_base::named(root)` (T34's reader) first and keeps its old merge base as the fallback, its own empty-base
  handling unchanged. There is no second reader and no shared fallback.
  - spec-lint `--delta` (`checks` `spec_lint.rs`): `touched_spec_dirs`, and the base `introduced` is measured against.
  - audit-register `--delta` (`audit_register.rs` `base`).
  - gm-attributions (`gm_attributions.rs` `base_ids`): the baseline is held to the base's copy.
  - gm-questions (`reviews` `gm_review.rs` `owed_in_delta`).
  - The rows' `delta:` gate (`tree` `checks.rs` `needs`, which `needs_run` reads).
  - closing (`cohort`): the row drops its literal `origin/main...HEAD`, and `close-check --push` with no range asks `push_range`. That
    is the range named, else the base the hand-in names, else `origin/main...HEAD`. At hand-in the work stands uncommitted on the
    base, so the range is the bare base: the working tree against it, as `gate_refusals` hands the ranged gates. `<base>...HEAD`
    would be empty and pass everything.
  - The variable reaches every row: `push-checks` spawns its rows with the environment it was given (no `env_clear`, `push.rs`
    `row_command`), and `make land`'s hand-in pass hands it the base (T34).
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=<crate> ONLY=<test>` with the tests written and the old code in
    place). Each fixture puts another task's staged commit, holding a finding, between origin/main and the hand-in base. Each asserts
    that the old base still refuses it, that the hand-in base does not, and that the work's own finding, uncommitted on the base, is
    refused:

    | row | crate, ONLY | passed, failed | red at |
    |---|---|---|---|
    | the `delta:` gate | tree, `checks::tests::at_a_hand_in` | 0, 1 | the staged batch's file starting the row |
    | closing | cohort, `close_check::tests::at_a_hand_in` | 0, 1 | the staged batch's closed feature refused |
    | spec-lint, audit-register, gm-attributions | checks, the three `at_a_hand_in` tests | 0, 3 (observed 2026-11-27, method: the run above) | each the staged batch's finding refused |
    | gm-questions | reviews, `gm_review::tests::at_a_hand_in` | 0, 1 | the staged batch's owed question refused |

    After the fix each module's tests pass: tree `checks::tests` 3 of 3; cohort `close_check::tests push::tests` 30 of 30; checks, the
    three modules, 48 of 48; reviews `gm_review::tests` 12 of 12 (observed 2026-11-27, method: the same `make rust-test` runs).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the push table's delta-scoped rows read the hand-in base | n/a - no map | n/a | none | n/a |

### T37 Approach (checklist part A)

1. **The goal, in the world.** At hand-in, every delta-scoped row of the push's table judges the builder's work alone, not every batch
   staged in the clone below it.
2. **The constraints.** FR-002 (a builder's tree meets the refusals the builder can cure), D3's base by phase, D4. T34's one reader.
   Constitution XIII: with the variable unset or empty, every row reads the merge base as before, and every existing test passes.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: plan D3, D4 and T34's section. O: the red-first table.
4. **Do they describe the world here?** Yes: each fixture stands as a phase-1 hand-in tree does, a staged commit below the base and the
   work uncommitted on it. For closing the work is staged in the index, as T07's no-commit carry leaves it.
5. **The order.** After T34, before T08.
6. **The exits.** Green: the tests and `make builder-checks` of tree, cohort, checks and reviews. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first table above, and `make builder-checks` over tree, cohort, checks and reviews.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The rows judge less only where a hand-in names its base. At every landing and push the variable is unset or
   empty, and nothing changes. Before the fix, a hand-in could be refused for another staged task's spec-lint finding, audit entry,
   attribution, GM question or closing.

**Found and left?**
- The claims gate's form-problem delta still reads `origin/main...HEAD`: `claims` `report.rs` `delta_form_problems`, which
  `commands.rs` `gate_cmd` asks. The claims crate's `stale.rs` and `counters.rs` still read the merge base. In phase 1 the gate may
  refuse a hand-in for another staged task's form problem and miss the work's own uncommitted one (observed 2026-11-27, method: grep
  of `"merge-base"` and `origin/main...` under `rust/gate/crates` after this fix). Not fixed here: the claims crate is not one of
  this task's rows. Filed as T41; lands before T08.
- Two of the four gates still read the merge base below T34's reader. `review-gate.sh` asks `reviews owed`, whose `owed.rs`
  `base_of` reads it: the gate's range reaches only its own `git diff` lines. `entry-gate.sh` asks `record-owed`, whose entry half
  (`owed` `entry.rs` `base_of`) reads it too. In phase 1 a hand-in may be refused for another staged task's owed review unit or owed
  entry (observed 2026-11-27, method: reading each gate's calls after the grep above). Not fixed here: neither is a push-table row,
  and each needs a fixture of its own. Filed as T42; lands before T08.
- The sweep's other readers are not reached by the hand-in's first pass. `house-style-delta` and `question-size` run under
  `make quick` and `make static`. `speckit_todo` `unlanded` lists clones. `land`, `core` `build.rs` and `tree` `delta.rs` take a
  base of their own. Not a defect: none refuses a hand-in, so none is filed.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-27 -->
### T41 (T37's Found and left: the claims gate's form-problem delta, stale and counters read their own merge base at hand-in)

- **Approach**: built in pool tree `diagram-backlog-t269` on T07's ac41f0137b, beside T42. Each of the three claims-crate sites T41 names
  now asks `l7r_gate_core::delta_base::named(root)` (T34's reader) first, its old base kept as the fallback. Only the lines the task
  names change: `commands.rs` `gate_cmd` and the carry's `touches_engine` are untouched, as 461 T38 (with T40) builds in the claims
  crate in another tree.
  - `report.rs` `delta_form_problems`: at a hand-in its delta is `git diff --name-only <base>` plus the untracked files
    (`ls-files --others --exclude-standard`, as `push.rs` `delta()` reads them), since the work stands uncommitted on the base and
    `<base>...HEAD` would be empty. With no base named it reads `origin/main...HEAD` as before.
  - `stale.rs` `stale`: the old figure is read at the named base, else the merge base. It already diffs the working tree.
  - `counters.rs` `counters_clear`: the base version is read at the named base, else the merge base. `counter_only` holds the base's
    version to the recorded code, so at a hand-in the recorded row is the staged batch's, as it would be in the clone.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/claims ONLY=at_a_hand_in` with the tests
    written and the old code in place). Each fixture puts another task's staged commit between origin/main and the hand-in base. Each
    asserts that the old base still judges it (first assertion, green on the old code), that the hand-in base does not, and that the
    work's own change, uncommitted on the base, is judged:

    | site | test | red at |
    |---|---|---|
    | form problems | `report::tests::at_a_hand_in_the_form_problems_are_the_work_s` | the staged `a.rs` refused, the work's staged `b.rs` and untracked `n.rs` missed |
    | stale | `stale::tests::at_a_hand_in_the_old_figure_is_the_base_s` | the page stating the merge base's 23 named, not the one stating the base's 24 |
    | counters | `counters::tests::at_a_hand_in_the_clear_reads_the_base_s_version` | the work's counter-only change not cleared |

    The run: 1 passed (T34's carry test), 3 failed. The stale fixture was corrected after that run (its later page named no
    `0003-inset`) and seen red again alone, 0 passed and 1 failed (observed 2026-11-27, method: the fix reverted, the same run). After
    the fix the claims crate passes whole, 206 of 206 (observed 2026-11-27, method: `make builder-checks`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the claims gate's form problems, stale and counters read the hand-in base | n/a - no map | n/a | none | n/a |

### T41 Approach (checklist part A)

1. **The goal, in the world.** At hand-in, the claims gate's form problems, the stale-figure check and the counter-only clear judge the
   builder's work alone. They no longer judge every batch staged in the clone below it, and they no longer miss the work itself.
2. **The constraints.** FR-002 (a builder's tree meets the refusals the builder can cure), D3's base by phase, D4, T34's one reader.
   Constitution XIII: with the variable unset or empty, each site reads its old base, and every existing test passes.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: plan D3, D4, T34's and T37's sections. O: the red-first
   table.
4. **Do they describe the world here?** Yes: each fixture stands as a phase-1 hand-in tree does, with a staged commit below the base
   and the work on it, staged or untracked (T07's no-commit carry).
5. **The order.** After T37, before T08.
6. **The exits.** Green: the tests and `make builder-checks` of claims. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first table above, and `make builder-checks` over claims, owed and reviews (with T42).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The sites judge less only where a hand-in names its base. At every landing and push the variable is unset or
   empty, and nothing changes. Before the fix, a hand-in could be refused for another staged task's form problem and pass its own.

**Found and left?**
- The claims crate's other merge-base readers. The carry's `touches_engine` (`carry.rs` 52) is T38's. The impl-drift bundle's
  `changed_lines` (`bundle.rs` 52) is built by `make claims-bundle` in the session's claims round, not at hand-in. Not a defect at
  hand-in: neither is asked by the four gates here (observed 2026-11-27, method: grep of `"merge-base"` and `origin/main...` under
  `rust/gate/crates` after this fix, each caller read). None is filed.

**Performance work?** no.

<!-- plan-archive: archived 2026-11-27 -->
### T42 (T37's Found and left: two of the four gates read their own merge base below T34's reader at hand-in)

- **Approach**: built in pool tree `diagram-backlog-t269` on T07's ac41f0137b, beside T41. Each `base_of` asks
  `l7r_gate_core::delta_base::named(root)` (T34's reader) first, its old merge base, HEAD and no-commits fallbacks unchanged. A named
  base reads `the hand-in base (<8 hex>)` as its description.
  - `reviews` `owed.rs` `base_of`: behind `review-gate.sh`'s `reviews owed`. Every reader of the base asks it: `owed_discharged`,
    `all_owed`, `check_declared_as`, `deferred.rs` and `declared.rs`. Each diffs the working tree against the base (`renamed`,
    `touched_code`), so the work uncommitted on the base is judged.
  - `owed` `entry.rs` `base_of`: behind `entry-gate.sh`'s `record-owed`, whose entry half (`owed.rs` `entry_lines`) asks
    `entry::owed`. `moved_anchors` diffs the working tree against the base.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=<crate> ONLY=<test>` with the tests written and the old code in
    place). Each fixture puts another task's staged commit between origin/main and the hand-in base. Each asserts that the old base
    still owes it, that the hand-in base does not, and that the work's own change, staged on the base, is owed:

    | gate | crate, test | passed, failed | red at |
    |---|---|---|---|
    | `reviews owed` | reviews, `owed::tests::at_a_hand_in_the_units_owed_are_the_work_s` | 0, 1 | the staged batch's map `m` still owed its settlement-review and glyph-check |
    | `record-owed`'s entry half | owed, `entry::tests::at_a_hand_in_the_entries_owed_are_the_work_s` | 0, 1 | the staged batch's moved `0001-a.html` still owed |

    After the fix each crate passes whole: reviews 219 of 219, owed 143 of 143 (observed 2026-11-27, method: `make builder-checks`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `reviews owed` and `record-owed`'s entry half read the hand-in base | n/a - no map | n/a | none | n/a |

### T42 Approach (checklist part A)

1. **The goal, in the world.** At hand-in, `review-gate.sh` and `entry-gate.sh` owe the builder's work alone: no review unit or entry of
   another batch staged in the clone below it.
2. **The constraints.** FR-002 (a builder's tree meets the refusals the builder can cure), D3's base by phase, D4, T34's one reader.
   Constitution XIII: with the variable unset or empty, each `base_of` returns what it did, and every existing test passes.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: plan D3, D4, T34's and T37's sections. O: the red-first
   table.
4. **Do they describe the world here?** Yes: each fixture stands as a phase-1 hand-in tree does, with a staged commit below the base
   and the work staged on it.
5. **The order.** After T37, before T08.
6. **The exits.** Green: the tests and `make builder-checks` of reviews and owed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first table above, and `make builder-checks` over claims, owed and reviews (with T41).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The gates owe less only where a hand-in names its base. At every landing and push the variable is unset or
   empty, and nothing changes. Before the fix, a hand-in could be refused for another staged task's owed review unit or owed entry.

**Found and left?** none. The gates' other readers were checked (observed 2026-11-27, method: each `l7r-gate` call of
`review-gate.sh` and `entry-gate.sh` read). `plan-gate.sh`'s `plan push` and the ranged `git diff` lines take the range the hand-in hands
them. `reviews owed --undrawn` and `--check-declared` read `base_of` or no base. The cohort crate's `rust_landing` and
`counter_only_delta` (`cohort.rs` 486, 571) serve `make cohort-landing`, which runs at landing and not in the hand-in's first pass.

**Performance work?** no.

