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

<!-- plan-archive: archived 2026-11-27 -->
### T08 (phase 1: the first pass at hand-in wired, and `make builder-done` pointed at the hand-in, D3 step 4 and 6, D4)

- **Approach**: in pool tree `diagram-backlog-t269`, on T05-T07, T34/T37/T38/T40-T42 as landed there.
  - **The seam widened** (`rust/gate/crates/land/src/land/hand_in.rs`): T07's `FirstPass` took the tree's path only, and T06's
    `cheap_refusals` needs the spec directory, every task, a note and the base. It now takes `Asked { tree, base, feature, tasks,
    note }`, built in `committed` from the hand-in (`hand.base`, `Found::feature`, `Found::tasks` - a bundle's every task); the
    tests' three closures and `none` (now `#[cfg(test)]`) take it.
  - **The pass** (`pass`, `first_pass`): `cli` hands `first_pass` to `run`, which roots a landing at the builder's TREE, not at
    `cwd` (the registry finds the tree, so `make builder-done` may be run from the clone), its tools where a landing's are
    (`scripts_of`), finds the feature's spec directory in the tree and asks `cheap_refusals(.., &Pass::HandIn { base }, None)`.
    No `deferred` list: an owed claim with a round in flight is quiet (T06), the landing's to wait on - phase 1 has no lane to hand
    it to. The base reaches the gates as `L7R_DELTA_BASE` and the in-process claims as `--delta-base` through T06/T34/T38's own
    code, unchanged here. A pass that cannot be asked is a REASON, never a clear: no spec directory for the feature in the tree
    (said with `make builder-done T=<tasks> F=<feature>`), or a raise (`the first pass could not be asked: <why>`).
  - **Decision: the note is the commit's subject.** A hand-in takes no `NOTE=`, and the tick check refuses an empty note
    (`tick/text.rs` `tick`); it reads the note for nothing else at `landed=false` (`landed_refusal`, the only other reader, is
    asked only at `landed=true`; observed 2026-11-27, method: reading `tick.rs` `checks` and `tick/refusal.rs`). So MSG's subject
    (`Found::message`'s first line) stands in. Label: the algorithmically easier route, the record silent.
  - **The printed line** (`rust/gate/crates/task/src/builder_done.rs` `kept_in`): with `handed_in` the second item is
    `handed in to the lane (make lane for its place)` in place of the `make land` line (D3 step 6, `contracts/lane-cli.md`,
    the task line's words); a plain `builder-done`'s output is unchanged, its tests untouched.
  - **Decision: the literal line, though `make lane` is T11's.** Phase 1's own text says "The coordinator still runs `make land`
    by hand", and no `lane:` target exists until T11 (observed 2026-11-27, method: `grep -n "^lane:" Makefile`, none). The
    task line, the contract and D3 step 6 agree on the words, so they are printed as written (constitution XVI); the session's
    route in phase 1 is kept in `scripts/container/builder-brief.md`'s AT A BUILDER'S END, which now says the hand-in prints the
    lane's line and that the session still runs `make land F= T=` until the lane does. Label: the literal thing, the gap named for
    the session.
  - **The Makefile** (`builder-done`, through `make guard-edit`): the recipe runs `l7r-gate.sh land --hand-in "$(T)" "<F>"`,
    its help line says the hand-in (the apply, the conflict stop and resume, the first pass, `HAND_IN_BASE`), and
    `docs/make-targets.html` regenerated (`make docs`). `MSG`, `GUARD` and `HAND_IN_BASE` reach the binary as make's
    command-line variables, exported to the recipe. Doc rows: `hand_in.rs`'s module doc steps 6 and 8, `builder_done.rs`'s step 6,
    `rust/gate/CLAUDE.md`'s land row.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::hand_in::tests"`): with
    `pass`'s `cheap_refusals` call deleted (the pass returning no reason, as `none` did), 19 passed, 3 failed - the plan review
    owed (the hand-in landed, exit 0, where it must refuse), the ledger row owed (the same), and the pass that cannot be asked (no
    raise said); restored, 22 passed, 0 failed.
  - **The tests** (`land/hand_in/tests.rs`, 3 new; the fixture `at_hand_in` takes the landing's `fx` - its tools stubbed, its
    in-process asks faked - adds a pool tree off its clone held by 449 T1 and re-roots the landing at that tree, as `first_pass`
    roots it; each drives `run` end to end): a hand-in whose plan review is owed (`plan-gate.sh` at the base) refused with
    `make plan-delta F=449`, nothing committed, the tree held - then answered and landed on the base, one commit, parent the
    clone's HEAD; one whose ledger row is owed refused with `make ledger-owed WRITE=`, its stub log holding the push's table over
    the TREE and no coverage, `crate-checks`, `done` or `rust` run (FR-002); the real `first_pass` with no spec directory, alone and
    through the hand-in (nothing committed), and `pass` over a tasks.md that is not text (the raise said). The task crate's
    hand-in test asserts the lane's line and no `make land F=`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the first pass at hand-in, `make builder-done` pointed at it | n/a - no map | n/a | none | n/a |

### T08 Approach (checklist part A)

1. **The goal, in the world.** A builder's `make builder-done` applies the work onto the clone's HEAD, asks the landing's first
   pass there, and commits only work that pass clears, each refusal named with its fixing command (US2).
2. **The constraints.** D3 steps 4 and 6, D4 (the hand-in mode, T06's), FR-002 (no coverage), `contracts/lane-cli.md`'s row,
   D15 (`land.rs` untouched: the wiring is in `hand_in.rs`), constitution XVI (the literal printed line).
3. **Where each comes from.** G: FR-002's request (spec.md); R: D3, D4, T06's and T07's sections; O: the tests above
   (2026-11-27).
4. **Do they describe the world here?** Yes: the tests run the landing's own fixture with a pool tree as `make builder-tree`
   leaves one, the hand-in found through the registry.
5. **The order.** After T06, T07 and T40; before T09's door, T10 and T11.
6. **The exits.** Green: the land and task crates' tests and `make builder-checks`; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/land rust/gate/crates/task"` green: the land crate 214 passed
   (211 + 3), the task crate 148, 0 failed; lint and format clean (observed 2026-11-27, method: that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** none - a wiring of the existing mode, no defect fixed.

**Found and left?**
- The builder never meets its hand-in's refusals: `make builder-brief`'s block ("Do NOT stage, commit, land or push") and
  `builder-brief.md`'s AT A BUILDER'S END have the coordinating session run `make builder-done` after the builder has reported,
  so a conflict or a first-pass refusal at hand-in lands on the coordinator, not the builder with the context (US2's "A refusal a
  builder can answer is answered by the builder that has the context"; observed 2026-11-27, method: reading both).
  Not fixed here: it changes the builders' stop point and the brief's standing block, outside this task's wiring. Filed as T43; lands before T10.

**Performance work?** no - it moves the first pass's refusals from the landing to the hand-in (D4) but makes no step faster and
measures no time.

<!-- plan-archive: archived 2026-11-27 -->
### T43 (phase 1: the builder runs its own hand-in, US2; found by T08's builder)

- **Approach**: in pool tree `diagram-backlog-t269`, on T08 as landed there.
  - **The block** (`rust/gate/crates/task/src/builder_brief.rs` `block`): a `fix` or `closing-half` block gains one line before
    the FILE line - `HAND IN last, review CLEAR: make builder-done T=<task> F=<feature> MSG="<subject>" [GUARD="<why>"]`, a
    conflict resolved in the tree, its paths `git add`ed and the command rerun, a refusal answered and rerun or a claims one
    reported verbatim, the outcome and the done ref reported - and its last line reads `Commit only by make builder-done; never
    land or push; never rewrite history.` in place of `Do NOT stage, commit, land or push; never rewrite history.` Every other
    line of the old wording is kept, and the 2,000-character cap holds (the longest block 2,019 characters on the first wording,
    cut until the test passed; observed 2026-11-27, method: the test's count).
  - **Decision: the hand-in for a fix and a closing half only.** The hand-in's first pass asks each task's tick check
    (`hand_in.rs` step 6, `cheap.rs` `first_pass`), whose `approach_refusal` (`tick/refusal.rs` `refusal`) refuses a task whose
    Approach block is its stub - a build half's always is (its closing half writes it) and a measurement writes no plan section
    (observed 2026-11-27, method: reading those three files; not run). Their blocks keep `Do NOT stage, commit, land or push`, and
    the session hands them in, as before. Label: the algorithmically easier route, the gap filed (T44).
  - **The wrap-up band** (`rust/guard/src/guards/context_cap_hooks/band.rs` `MAKE`, through `make guard-edit`): `builder-done`
    added, so a builder past the 300k cap can still run its stop point's last step; a conflict there needs an edit the band
    refuses, so it goes to the handoff (the doc says so). The band's refusal text lists it (`context_cap_hooks/tests.rs`).
  - **The docs**: `scripts/container/builder-brief.md` - a new bullet, THE BUILDER HANDS IN ITSELF, with its why, the one hand
    `git add` a pool tree allows (a hand-in conflict's paths), the claims exit and the band; AT A BUILDER'S END now the session's
    steps where the builder has not handed in. `scripts/container/builder-report-format.md` - STATE carries the hand-in's outcome
    (`handed in: <ref> <commit>` | `refused:` | `conflict:`), COMMIT the next-dispatch line it printed. `builder_done.rs`'s step 6
    and `docs/efficiency-tooling.md`'s row (stale since T08: it still named `make carry` as printed) say who runs it.
  - **The guards, probed** (observed 2026-11-27, method: the real dispatcher `/diagram/scripts/hooks/l7r-guard.sh PreToolUse`
    fed a synthetic Bash event, cwd this pool tree, an `agent_id`, no transcript): `cd <tree> && export ... && make builder-done
    T=T43 F=461 MSG="..."`, the same with `GUARD="..."`, and `cd <tree> && git add <path>` - each exit 0, no output. The
    builder-brief guard judges only an Agent or Workflow dispatch, never a Bash call; the guard-file guard's shell route judges
    the files a command writes, and `make builder-done` names none (its own in-process copy of the list asks `GUARD=`); the
    repo-safety guard judges git at a command position, a force push, a rewrite or the mount, none of which `make builder-done`
    is. The one guard that refused it was the wrap-up band (above), past the cap only.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=... ONLY=...`): `builder_brief::tests` with the new
    assertions on the old code, 5 passed, 1 failed (`each_kind_s_block_opens_with_its_marker_and_stays_short`); after, 6 passed.
    `guards::context_cap_hooks` with `builder-done` asserted let through and listed, 27 passed, 2 failed
    (`each_stop_point_step_is_let_through`, `the_bands_answers_and_records`); after, 29 passed.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the builder's own hand-in | n/a - no map | n/a | none | n/a |

### T43 Approach (checklist part A)

1. **The goal, in the world.** A fix or closing-half builder ends by handing its own work in, so a conflict or a first-pass
   refusal meets the builder that has the context (US2), and the session carries and lands.
2. **The constraints.** US2, FR-002 (no coverage at hand-in), D3 and D4, T08's wiring; the block's 2,000-character cap
   (`agent-prefix-hooks`); the brief's other rules kept whole; the wrap-up band (451 T417).
3. **Where each comes from.** G: US2's words (spec.md); R: D3, D4, T08's section; O: the probes and tests above (2026-11-27).
4. **Do they describe the world here?** Yes: the probes ran the live dispatcher on this pool tree; the band's test drives its
   judge.
5. **The order.** After T08; before T10.
6. **The exits.** Green: the task and guard crates' tests and `make builder-checks`; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/task rust/guard"` green (observed 2026-11-27, method: that
   command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** the band refused a capped builder's `make builder-done`, its stop point's new last step: fixed here.

**Found and left?**
- A build half's or a measurement's hand-in is refused by its own first pass: the tick check's `approach_refusal` refuses a stub
  Approach block, which those kinds always have, so since T08 neither can hand in, whoever runs it (observed 2026-11-27, method:
  reading `hand_in.rs`, `cheap.rs` and `tick/refusal.rs`; not run). Not fixed here: it needs a hand-in mode of its own, a
  mechanism outside this task's one job. Filed as T44; lands before T10.

**Performance work?** no - it moves who meets a hand-in's refusals, and measures no time.


<!-- plan-archive: archived 2026-11-27 -->
### T44 (phase 1: a build half's and a measurement's hand-in passes its own first pass; found by T43's builder)

- **Approach**: in pool tree `diagram-backlog-t269`, on T43 as landed.
  - **What refused, measured** (observed 2026-11-27, method: `scripts/gates/l7r-gate.sh tick --land-check 461 "probe note" T44`
    on this task's own unfilled stub): TWO reasons, not the one the task line named - the tick's plan gate (`tick_gate_in`: "461's
    plan decisions have no current CLEAR review", the stub's two blocks unreviewed, since `status.rs`'s `written_only` keeps an
    unwritten stub owed at its own task's tick) and `approach_refusal` (part A item 12 unanswered). The other gates, asked the same
    way on the same stub: `scripts/gates/plan-gate.sh HEAD~3` with `L7R_LAND_TICKS=T44` exit 0, silent (its push form drops an
    unwritten stub); `l7r-gate push-checks <tree> --every` (the first pass's skips) exit 0.
  - **The mode** (`rust/gate/crates/task/src/tick/refusal.rs`): `Section { Owed, Later }` on the tick's `Ask`, `Owed` by default;
    at `Later` the plan gate's ask of the task and the Approach block's ask are put off, every other ask kept (the task line, the
    boxes, waits, the arbiter fix, the checkpoint, a task built inside another's - its host's CLEAR still asked - the wording, the
    closing check). `tick::checks` takes it; `l7r-gate tick --land-check` and `make tick`/`make land`'s tick ask `Owed`.
  - **Where the mode comes from**: `Pass::HandIn { base, section }` (`land/cheap.rs`), set by `land/hand_in.rs`'s `section_of` from
    `Found::kind` (`task/builder_done.rs`) - the last `brief` line of the pool's log for the tree and its holder since the take,
    whose `kind` `make builder-brief` writes; `entry_of` now reads the same lines (`briefs`). `build-half` and `measurement` give
    `Later`; `fix`, `closing-half` and a tree no brief names give `Owed`. `Pass::Landing` is always `Owed`.
  - **Decision: the kind from the pool's log, never an argument or the environment.** A `KIND=` on `make builder-done` would let a
    fix's builder skip its own review; `tick_env` falls through to the process's environment, so an exported mode would loosen
    `make land`. Label: the algorithmically easier route that cannot loosen the landing.
  - **Decision: a measurement's record stands in for its section** (`hand_in.rs` `record_refusal`): its hand-in is refused while the
    work staged against the base holds nothing under `dev/measurements/`, the fix printed. A file present, its content the
    reviewers' - the algorithmically easier stand-in. A build half gets none: its handoff lives in the git directory, not the work,
    and `make builder-brief` already notes a closing half briefed before it is written.
  - **The block** (`task/builder_brief.rs`): every kind carries the HAND IN line, worded after its stop point - `review CLEAR` (fix,
    closing half), `the handoff written` (build half), `the record written` (measurement) - with `your one commit`, and every
    block ends `Never land or push; never rewrite history.` (the hand-in line says what commits). To keep under the 2,000-character
    cap (`agent-prefix-hooks`; the build half with every option given measured 2,256 in the test on the first wording, observed
    2026-11-27, method: the test's count): the CHECKS line's coverage-repair exception is a fix's alone (a repair is briefed as a
    fix), "Report the outcome and the done ref" dropped (the report format's STATE carries it, T43), the LOAD line's "(451 T321)"
    dropped and the ORDER, build-half STOP POINT and coverage lines shortened - 1,982 after (the test's paths, a `ONLY=` run; the
    whole crate's run reads about 4 more, its directories' counters longer), the test passing.
  - **The docs**: `scripts/container/builder-brief.md`'s THE BUILDER HANDS IN ITSELF (the kinds, the two asks put off, the kind's
    source, the record, the cap) and AT A BUILDER'S END (the session hands in only a builder stopped short); `builder_done.rs`'s
    step 6 and `hand_in.rs`'s step 6. The Makefile's `builder-done` line is still true and is a guard file: left.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land ONLY="land::hand_in::tests"` with the new
    tests on the old code): 24 passed, 2 failed (`a_build_half_hands_in_with_its_section_still_to_come`,
    `a_measurement_hands_in_its_record_in_place_of_its_section`); the two that pin the strict side
    (`a_fix_a_closing_half_and_an_unbriefed_tree_still_owe_the_section_at_hand_in`,
    `a_build_half_s_tree_still_owes_its_section_at_the_landing`) passed on the old code, as they must. After: 27 passed, with
    `a_measurement_s_record_that_cannot_be_looked_for_is_a_reason` (its `git diff` given a `--`, so a bad base is a bad revision,
    never a path). `tick::tests::a_section_owed_later_puts_off_only_the_plan_gate_and_the_approach_ask` pins the mode at the tick's
    level, `builder_done::tests::the_kind_is_the_tree_s_last_brief_since_its_take` the kind's source. `make builder-checks
    CRATE="rust/gate/crates/task rust/gate/crates/land"`: task 150 passed, land 219, lint and format clean.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in's section mode | n/a - no map | n/a | none | n/a |

### T44 Approach (checklist part A)

1. **The goal, in the world.** Every kind of builder hands its own work in (US2): a build half with its section still to come, a
   measurement with its record in its place; the landing still owes every section.
2. **The constraints.** US2, FR-002 (no coverage at hand-in), D3 and D4 (the hand-in's first pass), T08's and T43's wiring; the
   block's 2,000-character cap; the tick at a landing unchanged.
3. **Where each comes from.** G: US2's words (spec.md); R: D3, D4, T43's section; O: the probes and tests above (2026-11-27).
4. **Do they describe the world here?** Yes: the probe ran the real tick check on this task's own stub; the tests run the real first
   pass end to end through the hand-in.
5. **The order.** After T43; before T10.
6. **The exits.** Green: the task and land crates' tests and `make builder-checks`; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"` green (observed 2026-11-27, method:
   that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** the cap's room given first: the block's lines shortened, nothing a builder needs cut (above).
12. **Before any fix.** a build half's or a measurement's hand-in refused whoever runs it, since T08: fixed here.

**Found and left?** none.

**Performance work?** no - it lets two kinds of builder hand in themselves, and measures no time.


<!-- plan-archive: archived 2026-11-27 -->
### T13 (D1: the lane's tree, the worktree kept and its warm cache the lane's)

- **Approach**: the registry's lane holder is one word, `builder_pool::LANE` (`lane`), written as the tree's only task with no feature
  (`Tree::lane()`, `holder()` printing `lane`): never free, so no handout takes it; naming no feature, so no landing's freeing step
  (`landed`) reads it; and it is what the cache sweep already keeps (`evict.rs`, 451 T526: `-land` name, or `lane` as feature or
  task). THE BUILDERS' READING LEAVES IT OUT: `builder_pool::read` is now the builders' trees and `read_all` the registry whole, read
  by its one writer (`builder_tree.rs`, every read there) and by the sweep's kept trees (one word in `evict.rs`). Why not a lane
  tree every reader sees, as the advisor first put it: every count of builders' trees would count it - an `alone` queue entry waits
  while any tree is held (`builder_queue.rs`, `f.held`), the pool-idle rule's `held >= L7R_BUILDERS`, the sampler's and
  `task-time`'s held counts, the brief guard's pool - so each reader would need its own fix; left out by `read`, all of them are
  right by construction, and the one writer is the one place that must not drop it (`builder_pool::write` has no other caller,
  read 2026-11-27 by grep). In `builder_tree.rs`: the cap counts `builders(&trees)`, the lane's not (take, adopt, the cold tree's
  `N of cap`, `list`'s header, which adds `, and the lane's tree`); the word is reserved - a take, release, landing (exit 0, said)
  or adoption naming task `lane` is refused, and `holds` never matches a lane tree; `adopt` of the lane's path (`L7R_LANE_TREE`, a
  path or a name beside the clone, else `<clone>-land`) passes the `-land` filter, writes the lane holder, ignores the cap, and is
  refused with a `T=` or a second lane; `builder-tree lane` - the runner's call at a batch's start through `cli` (T14), no make
  target (T12 holds the Makefile) - fetches `origin main` and brings the registry's lane tree to `origin/main` by land-alone.sh step
  4's literal rule (`reset -q --hard`, `clean -fdq`, `checkout -q --detach`), logging a `lane` line; none adopted is refused with
  the `make builder-tree-adopt TREE=` to run, never made (D1 priced a new tree cold and declined it), and a tree gone from disk with
  the drop and the adoption.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY=builder_tree::tests::lane` on the old code): 0 passed, 2
  failed - the `-land` adoption refused as "not a builder's worktree", and `lane` the usage. Green: 3 of 3 lane tests (a third,
  the knob's, needs the new `Env` field), task 154 of 154 (the old adoption test now refuses `repo-review` where it refused
  `repo-land`, which is the lane's), guard shared 602 of 602 (the registry test's lane case), guard 628 of 628 (the sweep's lane
  case, red under `read`, green under `read_all`); `make builder-checks CRATE="rust/gate/crates/task rust/guard/shared rust/guard"`
  clean; the builder-pool, pool-idle and builder-brief suites 17, 33 and 32 passed. The stopped carry case: a cherry-pick left
  conflicted in the lane's tree is gone after `lane` (`CHERRY_PICK_HEAD` cleared by `reset --hard`), tested.

### T13 Approach (checklist part A)

1. **The goal, in the world.** `<clone>-land` is in the pool as the lane's tree: no builder is handed it, the pool's four builder
   slots are all builders', its 39 GB cache (measured 2026-11-27 (du), D1's table) is kept warm for the lane's gates, and each batch starts it at `origin/main`.
2. **The constraints.** D1 (the tree, the holder, the cap, the knob, step 4's rule kept), 451 T526's note on T13's line (write the
   `lane` holder at adoption), the pool's rules in `builder_tree.rs`'s header (membership is the registry; a rename chills a cache).
3. **Where each comes from.** R: plan.md D1, tasks.md T13's line; O: the registry's readers and its one writer, read 2026-11-27
   by grep; `evict.rs`'s lane rule, read the same day.
4. **Do they describe the world here?** Yes: `land-alone.sh` makes and resets `<clone>-land` (its `WT`, lines 550-554), and the
   sweep's kept-tree rule already names both marks.
5. **The order.** After T11; beside T12 (the runner's files and the Makefile untouched); before T14, whose runner calls `lane`.
6. **The exits.** Green: the lane tests and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: every registry reader found by one grep, each judged left-out-is-right.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green; after the landing the session adopts the real tree once
   (`make builder-tree-adopt TREE=/diagram/.clones/diagram-backlog-land`) and `make builder-trees` lists it held by `lane`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: new behavior, no defect fixed.

**Found and left?**
- A hand `git worktree remove` of the lane's tree or an `rm` of its cache is not refused: `builder_pool_hooks` reads `pools`,
  which leaves the lane out (it was outside the pool before this task too); its visible effect, a cold rebuild of its 39 GB cache (measured
   2026-11-27 (du), D1's table) at the lane's next gate. Not fixed here: a guard's case and suite are a job of their own past this brief's one. Filed as T45; lands before T22.
- The root Makefile's `builder-tree-adopt` help line and `docs/make-targets.html` name neither the lane's adoption nor `builder-tree
  lane`; a reader of `make help` adopting `-land` is not told it becomes the lane. Not fixed here: T12 holds the Makefile. Filed as
  T46; lands before T22.

**Performance work?** no

<!-- plan-archive: archived 2026-11-27 -->
### T12 (D2: phase 2's runner, the process the lane's later tasks run their batches in; lands after T11)

- **Approach**: `rust/gate/crates/lane/src/runner.rs` (new, with `runner/tests.rs`): `start` probes the lock, spawns `setsid
  <exe> lane --work <common>` from the common directory with stdio on /dev/null and every inherited fd past 2 marked CLOEXEC
  (`pages`' runner's measured reason), and waits `START_WAIT_S` for the RUNNER to hold `l7r-lane/lane.lock`, printing its pid; a
  held lock is a no-op naming the holder's pid (the pid read only while the lock is held, so a killed runner's stale pid names
  nothing). `stop` writes `l7r-lane/stop-request` keyed by the runner's pid and waits `STOP_WAIT_S`; `NOW=1` sends TERM to the
  runner's process group, KILL past the wait, and the stopper writes the `stop` line. `work` is the loop with every seam injected
  (clock, sleep, hand-ins, resume, step): its own stop request, a hand-in commit not seen before or a batch run resetting the idle
  clock, `LANE_IDLE_S` ending it with `stop why "idle"`, a failing step or resume with `stop why "error: <e>"`; at start it writes
  `start {pid, why}` and resumes the log's last open batch (data-model.md, "Recovery"). `work_cli` is the detached runner with the
  production seams (hand-ins as `make lane` reads them; `step` and `resume` stand-ins T14 fills). `lane.rs` gains the verbs
  `start`, `stop`, `stop --now`, `--work <common>` (`make lane-start`, `make lane-stop [NOW=1]`); the binary's `land` arm calls
  `on_hand_in`. The stall watchdog (`stall_watchdog_hooks/pass.rs`) learns the runner's exact argv. `dev/audits/lane-runner.md`
  covers the knobs.
- **Decision 1 - the lock is the truth, the pid secondary.** The starter never holds the lock across the spawn: it probes, spawns
  and waits for the runner to take it; a racing second runner loses `flock -n` and leaves with exit 0. Label: convention (the
  project's runner pattern, `make page-session`'s).
- **Decision 2 - the runner's `start` and `stop` lines name no batch.** T11's `state_of` reads a `stop` naming a batch as
  `stopped`, which Recovery skips; a `NOW=1` kill mid-batch must leave the batch resumable. Pinned in two tests (observed 2026-11-27, method: the build half's `runner::tests`, read in the tree). Label: the easier
  route (T11's mapping kept, nothing moved in `state_of`).
- **Decision 3 - a stop request is keyed by pid**, and one naming another pid is dropped by the next runner at its start (a request
  a killed runner never read must not stop its successor). Label: convention.
- **Decision 4 - the idle clock runs from the newest NEW hand-in (or a batch run), never from "nothing waiting".** Before T14 a
  waiting hand-in would otherwise keep the runner up for ever. Hand-ins present at the start count as the first arrival. Label:
  GUESS beside `LANE_IDLE_S` (D2's knob, 3600 s).
- **Decision 5 - recovery names the open batch and hands `resume` the batch's own reading** (`remaining`: its changes less its
  own ejections and what `origin/main` holds); bringing the tree to `origin/main` and running the rest is T14's seam. Until T14 the
  open batch is named on the start line (`why: "resume <batch>"`) and left open. Label: the easier route (D2, data-model.md's
  Recovery, split at T14's seam).
- **Decision 6 - a hand-in starts the runner only from phase 2's base, `HAND_IN_BASE=origin`.** D2 says "every hand-in,
  idempotently"; read by phase, because in phase 1 the coordinator lands by hand and, once T14 lands, a runner batching the same
  hand-ins would race it. `on_hand_in` (wired in the binary's `land` arm, `land_or_hand_in` in `rust/gate/src/lib.rs`, not in
  `builder_done.rs` or `hand_in.rs`: `task` cannot depend on `lane`) passes through any verb but `--hand-in`, a refused hand-in and
  any base but `origin`; the start's failure never changes the hand-in's exit. T22 flips the base, which switches this on with no
  further edit. Label: deliberate deviation from D2's literal "every hand-in", for phase 1 only (the plan's own phase split, D3's
  base by phase).
- **Decision 7 - the stall watchdog leaves unjudged only the session that waits on the lane.** The plan says only that the
  watchdog "learns its argv"; the use made of it (`stall_watchdog_hooks/pass.rs`, `lane_works`): a session is not judged a stall
  while BOTH hold - the clone's runner lives (`runs_lane`, the EXACT argv `<dir>/l7r-gate lane --work <common>`, canonicalized,
  `<clone>/.git` as the common directory); and a `l7r-gate lane wait` (`waits_on_lane`, exactly that argv) that THIS session
  started runs with its working directory in the clone - the wait descends from the session's registry pid by its parents' `stat`
  (`descends`, bounded at 64 steps, a GUESS well past any shell's nesting). Why: D9 has the coordinator end its turn on a
  backgrounded `make lane-wait` while a batch runs, and a stall nudge is a wake FR-005 does not list. Another session of the same
  clone, whose process the wait does not descend from, is judged as before (tested: a second session of the clone judged while the
  first waits; an entry with no pid, a chain reaching init, a missing parent and a cycle exempt nothing). The wait is T20's command,
  so until T20 the exemption holds for no session; after it, it lasts while the session's wait runs, not while the runner idles.
  The build half's form (the runner alone exempting every session claiming the clone) was ruled NOT LEGITIMATE at this section's
  first plan review, and a clone-wide wait with page sessions left out at its second (2026-11-27: nothing tied the wait to the
  session judged); narrowed here to the session's own wait. Label: the easier route (the page-session retry exemption's form,
  `in_retry_wait`, beside it).
- **Decision 8 - the timing knobs** `POLL_S` 5 s, `START_WAIT_S` 5 s, `STOP_WAIT_S` 10 s and `TAKE_S` 1 s: GUESS, each beside its
  constant and in `dev/audits/lane-runner.md`; `LANE_IDLE_S` and `LANE_POLL_S` read from the environment, a non-number refused
  (exit 2).
- **Decision 9 - the runner takes its lock with a bounded retry, `flock_within(.., TAKE_S)`, not one try.** `held()`'s probe takes
  the lock for an instant when it is free, so a start polling `holder()` could beat the runner's single try and leave no runner.
  Measured after (2026-11-27, a scratch repository, 200 `lane start` / `lane stop --now` cycles in a loop): 200 started, 0 runners
  left. Label: GUESS (`TAKE_S`).
- **For T22 - the base must flip in one place.** `land_or_hand_in` reads the raw environment (`std::env::var("HAND_IN_BASE")`)
  while the land crate's `hand_in.rs` treats unset as `clone`; they agree today (unset is phase 1 in both). If T22 flips the base by
  changing `hand_in.rs`'s DEFAULT rather than setting the variable, the land crate hands in on `origin/main` while `on_hand_in`
  still sees unset and never starts the runner. T22 therefore flips both together - one public reading of the knob in the land
  crate that `land_or_hand_in` asks too - and its test asserts a hand-in with `HAND_IN_BASE` unset starts the runner. Written on
  T22's line in tasks.md.
- **For T14 - a runner started by a hand-in inherits that call.** It runs `current_exe()`, the POOL TREE's build of `l7r-gate`
  (rebuilt or recycled under it with the tree), and keeps `make builder-done`'s environment for its life (`MSG`, `GUARD`, `T`, `F`,
  `L7R_GATE_TREE`, which `gate_tree()` reads); T14 is the first task to run `make land` from the runner, where `T` and `F` from the
  environment would reach make's variables and `L7R_GATE_TREE` would point the gate at the pool tree. T14 clears it: `start`'s
  spawn removes those variables, and the runner runs the binary of the lane tree's `scripts/gates/l7r-gate.sh` rather than the
  caller's. Dormant until then: `make lane-start` from a session is the only start before T22's base (Decision 6). Written on T14's
  line in tasks.md.
- Red first (2026-11-27): the lane crate's `runner::tests` against signature stubs, 0 passed, 11 failed; after, 13 of 13 (with the
  later stop-hard and real-lane tests), the lane crate 25 of 25, the binary 10 of 10. The watchdog's `pass::tests` with
  `lane_works` stubbed false, 16 passed, 1 failed; after, 17 of 17 (the guard crate 627 of 627). Its narrowed form (Decision 7)
  against a wait not tied to the session (`descends` bypassed), 16 passed, 1 failed, at the second session's judgment; after, 17
  of 17, the guard crate 629 of 629. The lane verb test
  (`lane::tests::the_runner_s_verbs_are_asked_of_the_clone_s_common_directory`) with T11's refusals put back (the four verbs
  unmatched), 0 passed, 1 failed. Not run red: the binary's `land` arm (`land_or_hand_in`), which only reads the variable and calls
  `on_hand_in`, tested whole by `a_hand_in_starts_the_runner_only_from_phase_two_s_base_and_only_when_it_succeeded`; the stall
  watchdog's hook suite gained no shell case (an exact four-word argv ending in `l7r-gate` needs a compiled stand-in), the Rust
  unit test covering the matcher over a fake `/proc`. Live (2026-11-27, a scratch repository, the tree's binary through
  `scripts/gates/l7r-gate.sh`): a start read through a pipe returned at once (pid = process group = session); a second start named
  it; `LANE_IDLE_S=3` stopped it `idle` within one poll; a soft stop and `NOW=1` each ended one with its line; an open batch line
  made the next start's line `why: "resume 461-1"`, the batch still `carrying` in `make lane`. Nothing was run against the real
  clone's lane.

### T12 Approach (checklist part A)

1. **The goal, in the world.** One runner a clone, started by `make lane-start` (and, from phase 2's base, by each hand-in),
   that outlives the turn that started it, ends itself when idle or asked, survives a kill by its log, and is never mistaken by
   the stall watchdog for a stalled session; T14 fills its batch step.
2. **The constraints.** D2 (the detached runner, its lock, its idle stop, `make lane-stop`), D3 (the base by phase), D8 (a JSON
   line a transition), D9 (the coordinator waits in the background), FR-005 (the wakes allowed), data-model.md ("Recovery", the
   `start` and `stop` events), contracts/lane-cli.md (the verbs), rust/gate/CLAUDE.md (a crate's wiring, every line covered by its
   own tests).
3. **Where each comes from.** R: plan.md D2, D3, D8, D9; data-model.md; contracts/lane-cli.md; spec FR-005. O: the 200-cycle
   start/stop loop and the live scratch-repository runs above (2026-11-27); `pages`' runner's measured fd leak (the CLOEXEC).
4. **Do they describe the world here?** Yes: the common directory is the one `make lane` reads (T11), the hand-ins are read as it
   reads them, and the live runs above wrote and read `l7r-lane/` in a scratch clone's common directory.
5. **The order.** After T11 (the crate and its log); before T14 (the batch step and resume), T20 (the wake-up, `make lane-wait`)
   and T22 (the base flipped to `origin`, which switches Decision 6 on).
6. **The exits.** Green: the lane crate's tests (a second start a no-op, the idle stop, a killed runner's batch resumed from its
   log), the watchdog's tests, `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one runner, one lock; the start race found by the advisor was measured closed (Decision 9); the watchdog's exemption narrowed at review rounds 1 and 2 (Decision 7).
8. **The budget.** One landing.
9. **Done, measured.** The tests above green and the live start/stop/idle/resume runs above, 2026-11-27.
10. **Before moving a constant.** n/a: new knobs, each labeled GUESS beside its constant and audited.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: new code, no defect fixed.

**Found and left?**

- The stall watchdog's long-run warning (`LONG_RUN`, 1800 s, its GUESS knob in `pass.rs`) would still nudge the coordinator over
  its own backgrounded `make lane-wait` past 30 minutes, a wake FR-005 does not list, each one 540k-966k tokens (measured 2026-11-27 (the transcript's usage fields), D9; spec.md's night). Not fixed here: `make lane-wait` is
  T20's command and does not exist yet. Filed as T47; lands before T22 (with T20, whose `make lane-wait` it exempts, so no
  coordinator waits on the lane without it).

**Performance work?** no


<!-- plan-archive: T13 to T13 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-27 -->
### T09 (D14, the handout half: a closing half no longer waits for its build half's carry)

- **Approach**: built in pool tree `diagram-backlog-t271`, in the task crate only (`builder_tree.rs` keeps T13's edits whole: the
  call site in `take`, one `Env` field and its words).
  - **The handout builds on the commit** (`builder_done::build_on`, new): in `take`, after the hold is saved and the registry's
    turn given back (an apply can outlast a waiting command's 100 tenths), and before the pre-warm reads the tree, each of
    `to_carry`'s commits of the tasks (one a bundle, oldest first, the land's own reading) is applied onto the tree - just brought
    to the clone's HEAD - by T05's command door, `l7r-gate land --carry --no-commit "" <sha>` run IN the tree (`Env.apply`, the
    gate binary's words from `current_exe` as the sampler's are; `L7R_GATE_TREE` removed as the pre-warm removes it, since `land`
    reads its root from the working directory). Each applied commit writes a `builds-on` line to the pool's log (the tree, the
    holder, the commit), and the handout says `builder-tree: it builds on <ref> (<sha>, "<subject>"), not yet carried: applied onto
    the clone's HEAD uncommitted - the builder's done supersedes it`. Why a command and not in process: T05's section - `task`
    cannot build on `land`.
  - **The hand-in half: one ref.** `Found::unready` (so `make builder-done` and T07's hand-in alike) reads the hold's
    `builds-on` lines since its take (`built_on`, over the shared `since_held` that `briefs` now uses) and `waits` passes over a
    done commit so built on; `kept_in` then writes the hold's commit over that ref - one ref, its commit holding both halves on
    the handout's base. A done commit NOT built on by the tree's handout (a ref written by hand, a tree held some other way) is
    still refused, never written over (`a_done_commit_not_yet_carried_is_never_written_over`, unchanged). The `superseded` line
    of the lane's log, and the open-batch rule, are T14's (D14's other half).
  - **Decision: an apply that does not end verified refuses the handout** (exit 2, a conflict no rule resolves; exit 1, its end
    not verified; a program that does not start): the tree is put back clean at the clone's HEAD (`reset --hard`, `clean -fd`:
    the handout had brought it there with nothing held), the hold released, nothing logged as built on, and the refusal names the
    apply's own words and the carry to run first - today's wait. The record is silent on a handout's conflict; the algorithmically
    easier route is taken (the root CLAUDE.md's rule): a conflicted tree handed to a fresh builder, its pre-warm compiling markers,
    was the other. Label: the easier route.
  - **Decision: with no apply program known (`Env.apply` empty) the handout waits as before** (`handout_waits`, 451 T398's
    refusal kept): the live `Env` always has the binary, so this is the tests' fixture and a binary-less caller's backstop.
  - **Words that became false, restated**: `make builder-done`'s two NEXT lines (a closing half "is dispatched after the commit is
    carried" / "waits for this commit") now say its handout builds on the commit; `builder_done.rs`'s module doc step 1;
    `hand_in.rs`'s step 1; `rust/gate/CLAUDE.md`'s task row; `scripts/container/builder-brief.md`'s "THE ONE EXCEPTION to
    dispatch-first" paragraph.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/task ONLY="builder_done::tests"`, the new
    test `a_closing_half_handed_out_before_its_build_half_s_carry_builds_on_it_and_its_done_leaves_one_ref` written with only the
    `Env.apply` field added): 15 passed, 1 failed - the handout refused with 451 T398's carry line. After: green, with
    `a_handout_whose_apply_does_not_end_verified_is_refused_with_the_tree_put_back_free` (exit 2, exit 1 and a missing program,
    each: refused, the tree clean at HEAD and free, no `builds-on` line) and `apply_words` asserted beside `sampler_words`; the
    old handout test kept as `with_no_apply_program_...`. The door's words are asserted exactly (the tree it ran in, `land --carry
    --no-commit "" <sha>`), so the stand-in stays tied to T05's sha-alone test
    (`a_commit_the_clone_holds_is_applied_by_its_sha_alone_and_its_done_ref_kept`, the land crate).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the handout's apply and the done's supersede | n/a - no map | n/a | none | n/a |

### T09 Approach (checklist part A)

1. **The goal, in the world.** A task's closing half is handed its tree while its build half's done commit still waits on its
   carry, the build half's work in the tree uncommitted, and its done leaves one done ref whose commit holds both halves.
2. **The constraints.** D14 (the handout half), D3's no-commit form reused through T05's command door, T07's hand-in reading
   `Found::unready`, D15 (no lane code here), T13's `builder_tree.rs` edits kept whole; no history rewritten.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md); R: D14, T05's and T07's sections; O: the scratch-clone
   tests above (2026-11-27).
4. **Do they describe the world here?** Yes: the tests take a real pool tree, a linked worktree of the fixture's clone, as
   `make builder-tree` does (observed 2026-11-27, method: the crate's `world` fixture, as T07's).
5. **The order.** After T05 and T07; before T16 (a repair's handout applies its ejected commit the same way) and T14.
6. **The exits.** Green: the task and land crates' tests and `make builder-checks` as below; coverage is the gate's, at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"` green, the task crate 156 passed
   (154 + 2) and the land crate 219, 0 failed (observed 2026-11-27, method: that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - not a defect fix: a new behavior D14 decides (a closing half's tree idle until a carry).

**Found and left?**
- The queue still reads a closing half as `waiting` on its own task's carry (`rust/guard/shared/src/builder_queue.rs`, `state()`,
  item 5; observed 2026-11-27, method: reading `state()`), so `make builder-next`, `make builder-done`'s next dispatch and the
  pool-idle guard never name the entry this handout now serves: the visible effect, a closing half not offered until the carry.
  Not fixed here: a guard crate's edit, outside this task's one job and crate. Filed as T48; lands before T16.

**Performance work?** no - its line carries no `[perf]` tag; it removes a wait in the builders' loop as D14 decides, measured by
phase 5, not by this task.

<!-- plan-archive: archived 2026-11-27 -->
### T48 (T09's found-and-left: the queue read a closing half as waiting on its own task's carry)

- **Approach**: built in pool tree `diagram-backlog-t271`, in the guard's shared crate only. `builder_queue::state()` loses its
  item-5 branch that returned `waiting` on "the carry of <task>'s done commit (make builder-trees)" for an entry whose OWN task's
  done ref still stands: since T09 `make builder-tree` applies that commit onto the handout uncommitted and the entry's
  `make builder-done` supersedes the ref, so the wait guarded nothing. A `waits=` task's carry still holds an entry (the
  `waits` closure's `uncarried` test, unchanged): only the entry's own task's handout builds on the commit. The `built` state's
  words ("the carry of <task>'s done commit owed") are kept - the build half's own entry still owes its carry, and
  `make builder-trees` still lists it. `make builder-next`, `make builder-done`'s next-dispatch line and the pool-idle Stop
  guard all read `shared::builder_queue` (`next`, `idle`), so the one branch removed changes all three; no gate or guard file
  edited. The module doc's item 5 restated.
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/guard/shared ONLY="builder_queue::tests"` on the old
    `state()` with the tests below written): 17 passed, 2 failed -
    `a_task_just_done_and_the_two_halves_of_one_task_are_never_ready_too_soon` (its closing half asserted READY while T1's
    done commit is uncarried; beside it a `waits=T1` entry asserted still `waiting` on T1) and the new
    `a_closing_half_before_its_build_half_s_carry_is_what_a_free_tree_is_idle_over` (a real clone with the done ref standing
    and one `done` line: `idle` says the free tree is idle over `make builder-brief T=T3 F=451 KIND=closing-half ENTRY=2`; it
    said `Quiet`). After: 19 passed.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the queue's state of a closing half before its carry | n/a - no map | n/a | none | n/a |

### T48 Approach (checklist part A)

1. **The goal, in the world.** A closing half whose build half is done but not yet carried is READY in `make queue`, offered by
   `make builder-next` and `make builder-done`, and held over by the pool-idle guard; an entry that `waits=` on that task still
   waits for its carry.
2. **The constraints.** D14 (T09's handout half: a closing half no longer waits for its build half's carry); the queue's
   overlap rule and `waits=` semantics unchanged; no history rewritten.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md); R: D14 and T09's section; O: the tests above
   (2026-11-27).
4. **Do they describe the world here?** Yes: the idle test builds a real clone with a done ref under `refs/l7r/done/` and a
   pool log, as `facts` reads them (observed 2026-11-27, method: the crate's `world` fixture).
5. **The order.** After T09 (whose handout makes the wait needless); before T16.
6. **The exits.** Green: `make builder-checks CRATE="rust/guard/shared rust/guard"` and the pool-idle suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/guard/shared rust/guard"` green - shared 603 passed, guard 629, 0
   failed - and `tests/hooks/test-pool-idle-hooks.sh` 33 passed, 0 failed (observed 2026-11-27, method: those commands, their
   logs' tails).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A coordinator would see the closing half offered at once, where it was listed `waiting` until the
    carry and a free tree stood idle (the visible effect T09 named); no map changes.

**Found and left?** none.

**Performance work?** no - its line carries no `[perf]` tag; it removes a wait in the builders' loop as D14 decides.


<!-- plan-archive: archived 2026-11-27 -->
### T17 (D6 step 4: the red-gate tripwire stands down for the lane's own runs, and only for them; FR-008)

- **Approach**: `tree/src/state.rs`'s `write` now reads who runs the gate (`Run`: `L7R_LANE_BATCH` and the process id) and hands it
  to `record`, the old body; the second-red branch of `make done` calls `second_red_gate` unless `lane_run` holds. `lane_run` is
  true only when the variable is set AND the run's tree is the lane's tree - the pool registry's tree held by `builder_pool::LANE`
  (`<clone>-land`, or the one `L7R_LANE_TREE` named at its adoption, 461 T13), compared canonicalized, read from the git common
  directory by `checks::common_dir` (no git call) - AND either its batch is open in `l7r-lane/lane.jsonl` (`batch_open`: a `batch`
  line naming it with no `landed` or `stop` of it after, a torn line skipped - the lane's `Batch::open`, read here because the lane
  crate builds on this one through `task` and `claims`, so a dependency on it would be a cycle) or the runner holding
  `l7r-lane/lane.lock` started it (`runner_started`: the lock held - probed by `flock -n`, as the lane's `runner::held` - its pid
  the file's, and this process that pid or a descendant, walked up `/proc/<pid>/stat`). Every other run meets `second_red_gate`
  exactly as before, the variable set or not. THE GROUPING, labeled (the easier and stricter route where the plan is silent): D6
  reads "in the lane's tree AND its batch open, or started by the runner"; the tree is asked of the runner's branch too, which costs
  the lane nothing (its every attempt runs in its tree, D1) and keeps a by-hand run elsewhere that happens to descend from a runner
  (none can today) under the tripwire. The variable is required on every branch ("the variable alone stands nothing down" read as
  necessary, not sufficient).
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/tree ONLY="state::tests"`, the new tests against a stub `lane_run`
  returning false, today's behavior): 7 passed, 3 failed - the open-batch stand-down, the reopened batch, and the runner's run. The
  two fixtures the task names passed on the old code, as they must: a by-hand run outside the lane's tree carrying the variable
  (its batch open, and an id no log names) is stopped on its second red; a run in the lane's tree whose batch is not open (no such
  id, `landed`, `stop`, the variable unset) is stopped too; the runner's case is stopped with the lock free, held by a sibling's
  pid, or naming no pid, and when the runner's run is in another tree. Green: 10 of 10, the crate 64 of 64; `make builder-checks
  CRATE="rust/gate/crates/tree"` clean.

### T17 Approach (checklist part A)

1. **The goal, in the world.** A lane attempt's red `make done` in the lane's tree is left to the lane's tripwire by task (T18);
   every other second red - a by-hand `make land` in the clone with `L7R_LANE_BATCH` exported, or one in the lane's tree outside an
   open batch - still owes the round arbiter, so the variable is no unrecorded escape.
2. **The constraints.** D6 step 4 (the stand-down's three conditions), FR-008 (nothing escapes the gate unrecorded),
   `contracts/lane-cli.md`'s `L7R_LANE_BATCH` line, D1 (the lane's tree), T11's log and T12's lock.
3. **Where each comes from.** R: plan.md D6 step 4 and tasks.md T17's line; O: `lane/src/log.rs`'s `Batch::open` and
   `lane/src/runner.rs`'s `held`/`holder`, read 2026-11-27; the crate graph (`claims`, `plan`, `trials` depend on `tree`; `task`
   on them; `lane` on `task`), read the same day from the `Cargo.toml`s.
4. **Do they describe the world here?** Yes: the lane's log and lock live in the git common directory (`l7r-lane/`), and the
   registry holds the lane's tree under `lane` since T13.
5. **The order.** After T11 (the log) and T13 (the registry's holder); before T18, which builds the lane's own rule.
6. **The exits.** Green: the state tests and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one reader of the tripwire (`second_red_gate`, called from `write` alone), found by grep.
8. **The budget.** One landing.
9. **Done, measured.** The ten state tests green; in use, T14's runner sets `L7R_LANE_BATCH` and its attempts' second reds owe
   nothing here.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: new behavior, no defect fixed.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: archived 2026-11-27 -->
### T45 (T13's found-and-left: the lane's tree and its warm cache unguarded against a hand removal)

- **Approach**: `shared::builder_pool` gains `pools_all` - every clone's registry read whole (`read_all`), the lane's tree in its
  place - beside `pools`, which stays the builders' reading (`read`); both walk the clones directory through one private `across`.
  `builder_pool_hooks::refusal` reads `pools_all` for what it protects, so a hand `git worktree remove`/`move` of `<clone>-land`,
  an `rm` of it, or an `rm` of `~/.cache/l7r-cargo-target/<clone>-land` (39 GB, measured 2026-11-27 (du), D1's table) is refused
  with the guard's existing REMOVE message (unchanged). The other readers of `pools` - `builder_brief_hooks` (the brief's tree must
  be the pool's for its task) and `workflow_hooks` (the same verdict for a Workflow's agent) - count builders' trees and keep `pools`
  (observed 2026-11-27, method: `grep -rn "pools(" rust`, three callers, the guard the only one that protects). Membership stays the
  registry: a `-land` tree no clone's registry names still passes, as before.
- Red first (2026-11-27, on the old code): `make rust-test CRATE=rust/guard ONLY=guards::builder_pool_hooks::tests` 5 passed, 1
  failed (`the_lane_s_tree_and_its_warm_cache_are_not_removed_by_hand`: the lane tree's `worktree remove` passed); the suite
  `tests/hooks/test-builder-pool-hooks.sh` 17 passed, 2 failed (a lane tree's removal and its cache's `rm`, both rc=0). Green: 6 of
  6 and 19 of 19; the shared registry test asserts `pools_all` returns the lane and the held tree where `pools` returns the held one.

### T45 Approach (checklist part A)

1. **The goal, in the world.** The lane's tree and its warm cache are kept as a builder's tree is: no hand removal, move or `rm`
   passes the guard without its escape, while every count of builders' trees still leaves the lane out.
2. **The constraints.** D1 (the lane's tree kept, its cache warm); T13's split of `read` (builders) and `read_all` (the registry
   whole); the guard's rule that membership is the registry, never a name's shape (451 T285).
3. **Where each comes from.** R: plan.md D1, tasks.md T45's line, T13's found-and-left item; O: the readers of `pools`, by grep
   2026-11-27.
4. **Do they describe the world here?** Yes: the red tests above show the lane's tree passed the guard; T13 writes it held by
   `lane` (`Tree::lane`).
5. **The order.** After T13 (the `lane` holder and `read_all`); before T22.
6. **The exits.** Green: the guard's unit tests and its suite above, `make builder-checks CRATE="rust/guard/shared rust/guard"`.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one grep found the three callers of `pools` (observed 2026-11-27, method: `grep -rn "pools(" rust`), each judged.
8. **The budget.** One landing.
9. **Done, measured.** The lane test and the suite's two lane cases green; after the landing `git worktree remove` of the adopted
   `/diagram/.clones/diagram-backlog-land` is refused by the guard.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A cold rebuild of the lane's 39 GB cache (measured 2026-11-27 (du), D1's table) at its next gate after a hand
    removal, no longer possible without the escape, and no refusal message changed.

**Found and left?**
- The REMOVE message names `make builder-tree-drop TREE=<path>` as the way to remove a pool tree for real, but `drop_tree`
  (`rust/gate/crates/task/src/builder_tree.rs`) refuses any held tree with `make builder-tree-release T=lane first`, which T13
  refuses: a session retiring the lane's tree is sent to a dead end and left only the `BUILDER_TREE_OK` escape (observed 2026-11-27,
  method: read `drop_tree`'s held check). Not fixed here: a gate crate's command and its tests are a job past this brief's one.
  Filed as T49; lands before T22.

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T10 (phase 1's measurement on real work, US2 and SC-002: the hand-in in use since T43 landed)

- **Approach**: A measurement script, `dev/measurements/2026-11-27/461-t10-phase1/phase1.py`, reuses T02's `night-figures.py`
  for the landings, the pool replay and the load, so the after figures count as the night's did. Its record is that
  directory's `results.md`; nothing in the engine or the tooling changed.
  - **Windows.** 19:57:00Z (T08 and T43 landed, 19:56:47Z) to 23:03:20Z (before this task's take), 3.11 h, and 21:06:47Z (T44
    landed) to 23:03:20Z beside it (observed 2026-11-27, method: the event log's `make land` end rows and the pool log).
  - **Hand-ins.** 27 pool `done` rows, all `"handed_in": true`, all run by a builder and none by the coordinator, on 22 tasks or
    bundles; 21:06Z on, 22 on 18 (observed 2026-11-27, method: `phase1.py figures` over the kept extracts,
    `output-1957-2303.txt` and `output-2106-2303.txt`, each done row joined to the builder-done call that wrote it).
  - **Refused at hand-in.** Of 34 builder calls, 7 handed nothing in, on 7 of 23 tasks. 4 were conflicts and 3 first-pass
    refusals: a ledger row, a feature-close report, and a plan review owed. Each named its fixing command or its paths. 3 of 4
    conflicts were resolved by the builder that met them, the fourth by a fresh closing half from a handoff, and none by the
    coordinator. No hand-in ran a coverage step (observed 2026-11-27, method: the same outputs; the outcomes and reasons from
    the calls' own tool results in the subagent transcripts, found by call id, a second source the logs cannot give).
  - **What the logs cannot show.** The event log's foreground tool rows carry no exit code, and the pool log writes nothing on
    a refused or conflicted hand-in. So the logs show that a call handed nothing in, never why, and never a conflict resolved.
  - **Landings refused before a gate.** 0 of 7 attempts (5 landed, 2 gates red) over 19:57Z on, and 0 of 4 over 21:06Z on,
    against the night's 17 of 39. Trees held were 2.94 and 3.02 against 3.19, and the median load 9.4 and 10.3 against 14.1
    on 22 cores (observed 2026-11-27, method: `night-figures.py`'s `landings()` and replay through `phase1.py`, the night's
    from T02's record). The window is not LIKE the night, 3.11 h long with its load below 10.6, and seven attempts agree with
    US2's "well under" without establishing it: at an 11% rate, none in seven comes 44% of the time (observed 2026-11-27,
    method: 0.89^7, the likeness rule of `night-figures.py`).
  - **The one real hand-in.** This task's own, a measurement's under T44's rule. Its outcome is in the builder's report, since
    the record it commits cannot hold it.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement, no engine or tooling code | - | - | - | - |

### T10 Approach (checklist part A)

1. **The goal, in the world.** Phase 1's after figures (hand-ins, refusals at hand-in and their causes, conflicts a builder
   resolved, landings refused before a gate) recorded with their concurrency, re-derivable from kept extracts.
2. **The constraints.** US2 and SC-002; FR-010 (every figure beside its concurrency); T02's counting rule for landings.
3. **Where each comes from.** R: the spec's US2, SC-002 and FR-010; T02's record. O: this task's runs.
4. **Do they describe the world here?** Measured on the pool log, the event log, the sampler and the transcripts over the
   windows above (observed 2026-11-27, method: `phase1.py`; live and kept runs agree but for the transcript outcomes).
5. **The order.** After T08, T43 and T44 landed; before T31, which reads the like window.
6. **The exits.** Green: the record written and its counts re-derived from its outputs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the logs' gaps are named, and the transcripts fill them as a labeled second source.
8. **The budget.** One landing.
9. **Done, measured.** `results.md` with the outputs it cites, the figures re-derived by the commands it lists.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: a measurement, no fix.

**Found and left?**
- The likeness test's trees held counts the lane's own worktree, adopted `lane` at 21:08:09Z and never released, as a held
  builder tree: 3.55 against 2.94 over 19:57Z on, and the sampler's `held` lists `lane` in 215 of 1,065 samples (observed
  2026-11-27, method: `phase1.py` with and without the lane tree, and each sample's `held` against the replay). T31's like
  window would read about one tree high. Not fixed here: a measurement changes no tooling. Filed as T59; lands before T31.
- A build half's hand-in is refused for the feature-close ask, which only its closing half can answer: 451 T537's build half at
  22:06:03Z (observed 2026-11-27, method: that call's tool result). T44 puts off a build half's plan asks by its kind, but not
  this one. Not fixed here: a measurement changes no tooling. Filed as T60; lands before T31.

**Performance work?** yes - a measurement of where the landings' and the hand-ins' time and refusals go (451 FR-013: a
measurement task counts).

<!-- plan-archive: archived 2026-11-28 -->
### T14 (D5, D6 step 1, D8, D14: phase 2's batch, the runner's step and resume that T12 left as stand-ins; lands after T12 and T13)

- **Approach**: `rust/gate/crates/lane/src/batch.rs` (new, with `batch/tests.rs`) forms the batch; `runner/run.rs` (new, with
  `run/tests.rs`) runs it as the step and resume T12's `work_cli` calls; `runner.rs`'s spawn strips the caller's environment and
  runs the lane tree's own wrapper (T12's "For T14"). Built in two halves (2026-11-27); the build half's handoff is
  `<clone git dir>/l7r-handoffs/T14-build.md`. `dev/audits/lane-batch-cap.md` covers `LANE_MAX`; the lane crate's row in
  `rust/gate/CLAUDE.md` names the modules.
- **Decision 1 - D5's formation, literally.** `form(&World, LANE_MAX)` takes the `waiting` hand-ins in hand-in order, starts at
  the oldest, and takes the run of its feature straight after it, cut at the first hand-in of another feature, at one D14 holds,
  or at `LANE_MAX` changes. D14's open-batch half: a hand-in is held while an open batch carries another hand-in of its feature
  sharing one of its tasks; where the OLDEST waiting hand-in is held, no batch forms (none jumps ahead of it). `next_id` is
  `<feature>-<n>`, n one past the feature's highest `batch` line. A batch reads its changes' full shas once, on its `batch` line, so
  a later hand-in moves no batch. Label: the literal order (D5); the cut at a held hand-in the easier route (D5's own label).
- **Decision 2 - `LANE_MAX` = 6.** GUESS knob, beside its constant and in `dev/audits/lane-batch-cap.md` (seed: the two-tier
  threshold's "about six tasks", `docs/process-decisions.md`; trial 458's verdict resets it). `LANE_WAIT_S` = 0 has no constant: the
  step forms as soon as no batch is open. Label: GUESS.
- **Decision 3 - the run's four steps** (`run_batch`): (1) the lane's tree brought to `origin/main` by T13's `builder_tree::cli(["lane"])`,
  and the changes `origin/main` already holds dropped (a resume after the push lands with no run); (2) each remaining change carried
  by `make carry COMMIT=<sha>` in the lane's tree, oldest first, one `carry` line - the lane carries the batch's OWN shas, since
  `make land`'s `carry_done` reads the done refs live; (3) `make land F=<feature> T="<tasks>" NOTE="<subjects; ...> - landed by the
  lane, batch <b>"` there, its stdout and stderr the attempt's own file `l7r-lane/attempts/<b>-<n>.log`, n continuing from the
  batch's `run` lines (D6 step 1, never overwritten), one `run` line and a `push` line where it pushed; (4) each done ref deleted
  only where it still names the batch's sha (`update-ref -d <ref> <sha>`: a later hand-in keeps its ref; the linked tree's carry
  keeps the refs, 451 T404), then the `landed` line and ONE `owed` line, `lane: batch <b> landed - <feature> <tasks> (<k>
  change(s), <r> run(s), <m> minutes)`, which T20 prints. A carry that stops, or a landing that ends red or refused, writes its line
  (a red one also ONE `owed` line naming the attempt file) and returns an error: the runner stops with `error: ...` and the batch
  stays OPEN, so nothing re-runs each poll and the next `make lane-start` resumes it as attempt n+1. A make that cannot start counts
  as exit -1 on the same path. Label: the easier route (D6 step 1's green path; T15, phase 3 and T19 replace the red, the carry's
  and the push's branches).
- **Decision 4 - a non-zero exit is read against `origin/main`.** GNU make ends 2 for any failed recipe, so the landing's own exit 3
  (pushed, other sessions' edits merged) reaches the runner as 2, never 3 (observed 2026-11-27, a scratch Makefile under GNU Make
  4.4.1: a recipe's `exit 3` printed `Error 3` and make ended 2). On any exit but 0 the runner fetches `origin main` in the
  lane's tree and asks `held_by(tree, "refs/remotes/origin/main", <the batch's shas>)`: every change there is a push (a `push` line
  with the observed code), and the batch goes on to step 4; otherwise it is the red branch. The push's own code is not separable from
  make land's today (T19's). Label: the easier route (main's content is the truth, as Recovery already asks it).
- **Decision 5 - the stripped environment.** `run::STRIPPED`, removed from both the runner's spawn (`spawn_command`) and each
  `make` the run starts: T12's five (`MSG`, `GUARD`, `T`, `F`, `L7R_GATE_TREE`) and make's own `MAKEFLAGS`, `MAKEOVERRIDES`,
  `MFLAGS`, `MAKELEVEL`, because a runner a hand-in started inherits `make builder-done T= F= MSG=`'s environment and a variable on
  that make's command line reaches a grandchild make through `MAKEFLAGS`. Observed 2026-11-27, method: a scratch Makefile under GNU
  Make 4.4.1 (`make -f outer.mk T=T14 F=461`, its recipe running `sh -c "$(MAKE) -f inner.mk show"`): the grandchild printed
  `T=[T14] F=[461]`, and `env -u MAKEFLAGS -u MAKEOVERRIDES -u MFLAGS -u MAKELEVEL` left its child an empty `MAKEFLAGS`. Label:
  convention (GNU make's own variable passing, observed).
- **Decision 6 - the lane tree's own wrapper.** `runner_exe(common, fallback)` returns the registry's lane tree's
  `scripts/gates/l7r-gate.sh` when the lane's tree and that file exist, else `fallback` (`current_exe()`: phase 1, a scratch
  repository); both `lane start` and `on_hand_in` use it. The wrapper `exec`s `<target>/tool/l7r-gate lane --work <common>`, so the
  stall watchdog's `runs_lane` still matches. Label: the easier route (T12's "For T14"). Its rebuild may outlast `START_WAIT_S`:
  filed as T51 (Found and left).
- **Decision 7 - `NOTE=` on make's command line.** The Makefile's `land: export LAND_NOTE = $(NOTE)` overwrites an inherited
  `LAND_NOTE`, so the run passes `NOTE=` as a make argument; it reaches the binary as `LAND_NOTE`, as contracts/lane-cli.md names
  it. `SPECIFY_FEATURE`, `SPECIFY_FEATURE_DIRECTORY` and `L7R_LANE_BATCH` go in the environment. Label: convention (the Makefile's
  own route for the variable).
- **Decision 8 - `L7R_LAND_ALONE=1` and `SYNC_BACKUP=off`, as `land-alone.sh` sets them** for its own landing in this same `-land`
  worktree (its line 572). Their non-test readers (found by grep, 2026-11-27): `land/alone.rs`'s `INNER` (the tree is not sent to
  land alone again - it is the landing); `core/build.rs`'s `LANDING` (a claims answer from a mixed build owed again, right for a
  clean lane tree); `sync-with-main.sh` line 564 (no backup push from a worktree that is no clone). Both kept. Label: convention
  (`land-alone.sh`'s own settings for the same tree).
- **The flake the build half saw.** `runner::tests::a_second_start_is_a_no_op_naming_the_first_s_pid_and_stop_now_ends_it` failed
  once in the build half's first `make builder-checks` (its last `stop NOW` found a runner). Measured 2026-11-27, `make rust-test
  CRATE=rust/gate/crates/lane ONLY="runner"` ten times in a row at load 16-27 on 22 cores: 2 red of 10 - that test once (its last
  `stop NOW` reading `stopped at once` for the runner killed before) and `the_work_command_holds_the_lock_..._leaves_quietly` once
  (`held` true after `work_cli` returned). The cause: a `flock` lock belongs to the open file description, so a close frees it only
  once every copy is closed, and the test binary's other threads fork `git`, `make` and `sh` all the while, each child holding a
  copy of every descriptor until its `exec` - so the probe's own lock (`held` takes it for an instant where it is free) and the ended
  runner's lock outlived their close. Fixed in `runner.rs`: `free` (the probe) and `release` (the runner's end) let the lock go by
  `flock -u` before the close, which frees it whatever copies exist; `held`'s doc no longer says it is let go as the file closes. The
  wrong outcome fixed: `make lane-stop` or `make lane-start` reading a runner that has ended (a stop naming a dead pid, a start
  saying `already runs`) where the caller is a threaded process. Red first in
  `runner::tests::a_probe_and_an_ended_runner_leave_no_lock_behind_a_copy_of_their_descriptor`, which keeps a `try_clone` of the
  descriptor alive across the probe and across the release: on the old code 0 passed, 1 failed (at the probe's assertion); with only
  the probe fixed, 0 passed, 1 failed (at the release's); after both, 1 of 1, and `ONLY="runner"` 23 of 23. After the fix,
  the same `ONLY="runner"` run thirty times in a row at load 22-52 on 22 cores: 30 green of 30 (0 red, against 2 of 10 before).
  Label: convention (`flock(1)`'s `-u`; the lock's ownership by the open file description is `flock(2)`'s).
- **Two things the build half changed beside its own modules.** T12's test
  `the_work_command_sees_a_real_hand_in_and_resumes_an_open_batch_of_the_log` now expects, with no lane's tree in the pool, the
  resume to fail: the runner exits 1 with `stop why "error: lane: batch 461-1: builder-tree lane: ..."` and the batch stays open
  (T12's stand-in resume had succeeded). `log::names` became `pub(crate)` for `batch.rs`.
- **Phase 1's base.** A phase-1 hand-in's base is the clone's HEAD, so carried onto `origin/main` it may conflict; by design until
  T22, since in phase 1 the runner starts only by `make lane-start` (T12's Decision 6), and a conflict ends the step on the carry's
  seam above.
- Red first (2026-11-27, the build half): `batch::tests` against stubs, 0 passed, 3 failed; after, 3 of 3. `runner::run::tests`
  against stubs, 0 passed, 6 failed; after, 6 of 6; the exit-3-as-2 test under the old `code == 0 || code == 3` rule, 6 passed, 1
  failed; after, 7 of 7. `runner::tests::the_runner_runs_the_lane_tree_s_own_wrapper_...` with `runner_exe` returning the fallback
  and no stripping, 0 passed, 1 failed; after, 1 of 1. The lane crate 36 of 36, the land crate 219 of 219. Not run red: nothing
  against a real lane tree or a real `make land` (the end-to-end test's `make land` is a stand-in recipe in the scratch clone's
  Makefile that ticks and pushes); T23 is the real batch.

### T14 Approach (checklist part A)

1. **The goal, in the world.** A runner that, with no batch open, forms D5's batch from the waiting hand-ins, lands it in the
   lane's own tree with one gate run, each attempt's output kept, the landed done refs deleted and one status line owed; a killed
   or red batch left open and resumed as the next attempt.
2. **The constraints.** D5 (the formation and `LANE_MAX`), D6 step 1 (the attempt files), D8 (a JSON line a transition, the done
   refs deleted after the push), D14 (shas read once; a later hand-in waits), FR-003 ("in order"), US3, data-model.md ("Recovery"),
   contracts/lane-cli.md (`LAND_NOTE`, `L7R_LANE_BATCH`), T12's "For T14".
3. **Where each comes from.** R: plan.md D5, D6, D8, D14; data-model.md; contracts/lane-cli.md; T12's plan section; the Makefile's
   `land` recipe; `land-alone.sh` line 572. O: the red-first counts above; GNU make's documented `MAKEFLAGS` and exit 2.
4. **Do they describe the world here?** Yes for the scratch world: the end-to-end test builds a clone, a bare `origin` and two pool
   trees, hands in two changes, and sees one batch, one push, both ticked, both done refs deleted, one `owed` line. Not yet for the
   real clone's lane tree: T23 measures that.
5. **The order.** After T12 (the runner) and T13 (the lane's tree); before T15 (the red's attribution), T19 (the push), T20 (the
   wake-up), T22 (the base flipped) and T23 (the real batch); T52 before T22.
6. **The exits.** Green: the lane crate's tests, the end-to-end batch among them, and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Two: the exit-3-as-2 reading (Decision 4), found by reading make's exit rule after the first green, fixed
   red-first; and the lock's flake, 2 red in 10, traced to a descriptor copy and fixed red-first (above).
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27; the runner's tests' flake, 2 red of 10 before the lock fix, and the runs
   after it, above.
10. **Before moving a constant.** n/a: `LANE_MAX` is new, labeled GUESS and audited.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** One defect fixed: a probe or an ended runner leaving the lock held behind a copy of its descriptor, so a
   threaded caller read a runner that had ended (the flake above: 2 red runs in 10). The rest is new code.

**Found and left?**

- In the lane's tree `make land`'s `carry_done` reads the done refs live, so a task whose ref a later hand-in moved after the
  batch's `batch` line is carried again at the new sha on top: a hand-in lands inside a batch that never named it, against D14.
  Not fixed here: `make land`'s carry is the land crate's, and the stand-in `make land` of the end-to-end test carries nothing, so
  the fix needs its own red test there. Filed as T52; lands before T22.
- The runner's start waits `START_WAIT_S` for the lock while the lane tree's wrapper may first rebuild that tree's `l7r-gate`, so a
  start can report `holds no lock` while the runner comes up after the build. Not fixed here: the rebuild is unmeasured. Filed as
  T51; lands before T22.
- `make lane` shows an earlier hand-in of a task in an OPEN batch as `superseded`, not `in batch <b>`, once a later hand-in of the
  task exists (`log::state`, T11's order), though the batch's `batch` line names and lands the earlier sha (D14): the lane's view
  misstates what a batch carries (D8's states). Not fixed here: `log::state` is T11's reading and the batch's formation does not
  depend on it. Filed as T53; lands before T20.

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T15 (phase 2's red path: a red batch attributed from the gate's own record, its changes ejected as repair entries, the rest run again)

- **Approach**: `rust/gate/crates/lane/src/attribute.rs` (new, pure) reads a red attempt's units - its span's red `test`, `lint`, `cover-build`, `cover-run` and `build` Phase lines in the lane's tree, ONE UNIT A LINE over every crate it names; `HOOK TESTS FAILED:` lines and the first pass's `Every refusal:` rows of the attempt file - and maps each to the change whose delta touches it (D6 step 2). `repairs.rs` (new) is the one writer of `l7r-lane/repairs.jsonl`. `runner/run.rs`'s `run_batch` loops: a red attempt writes its `run` line's `red`, an `attribute` line, each entry BEFORE its `eject` lines, one `owed` line an entry, and runs the rest again on the tree brought to `origin/main` anew (D6 "By phase", D7). `wake::dead` (T20) narrowed: only the runner's own `"stopped": true` line tells a death. Measured 2026-11-27: the two readings the handoff left open, by reading the code and a test of each (below); every `Phase` line of the clone's `l7r-events/*.jsonl` counted by step and crate count (a Python count): 947 of 2,723 `cover-build` lines named 2 to 28 crates, every other step's line one.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **Several candidates in phase 2 are UNPLACED** - any red unit naming no change or more than one, or no unit read at all, ejects the batch as one entry (`why` `unplaced`). Label: the algorithmically easier route; D6 halves over candidates, phase 3's (T24 replaces `attribute()`).
2. **A crate is its directory; its dependents are not counted** (`dir/` matched with the slash). A change to `core` that reddens `lane`'s tests is unplaced; phase 3's halving places it. Label: D6's literal "a crate by its directory".
3. **A Phase line is one unit over all the crates it names**: the unit names every change under ANY of the line's crates, each of them read, however many - only its printed form is cut (`<dir> <dir> <dir> (+<k> more) <step>`, the first 3 shown, `NAMED` a GUESS knob of the owed line's length, no rule's). Label: deliberate deviation from the build half's unit a crate, a defect fixed here: a red `cover-build` is one compile of a family, so read a crate at a time it placed and ejected an innocent change under another crate of the family as `red`. Pinned by `attribute::tests::a_red_line_naming_several_crates_is_one_unit_over_all_of_them`.
4. **A suite maps** to a delta path whose file name is the guard file, `tests/hooks/test-<stem>.*`, and for a `*-hooks` stem `rust/guard/src/guards/<snake>*` and `rust/guard/shared/src/guards/<snake>*`. Label: D6's map; the shared crate the easier reading of "its guard's sources".
5. **A first-pass row maps** by a delta path its text contains, or by its leading task list (`T13, T14: ...`). Label: D6 "a row by its file"; the task head the first pass's own form.
6. **A non-zero exit not on `origin/main` is a red, except two that eject nothing.** Exit -1 (`make` could not start, or was killed): no failing change to name, and ejecting on no evidence would eject innocent ones. And a FIRST-PASS REFUSAL WITH A ROW NAMING NO CHANGE of the batch - a hold, a lock, an owed round of no task of it (`attribute::refusal`, `Refusal::Unnamed`): it blocks the whole batch and would refuse every repair too. Each stops the runner with the batch open, its `owed` line carrying `"stopped": true` (`lane: batch <b>: make land's first pass refused at attempt <n>, a row naming no change of the batch (<those rows>) - the runner stopped, the batch open, nothing ejected: <attempt>`), and the next `make lane-start` resumes it, as T14 did. Where such a row stands beside a row naming a change, the stop holds too: nothing lands while the hold stands, and the named change is ejected on the resume once it clears. A refusal whose every row names a change of the batch ejects what the rows name and runs the rest again: a row naming one change places it (`red`, Decision 5); a row naming several - `T13, T14: ...`, two hand-ins - ejects every change the rows name as ONE entry (`unplaced`, the rows its units), not the whole batch. Label: the GM's "ejects the failing change. The rest of the batch lands" read literally - a row naming a change names the failing one, a row naming none names no failing change; fixed on the plan review's rounds 1 (the build half ejected the whole batch for a refusal naming nothing, NOT LEGITIMATE) and 2 (round 1's stop also took a row naming two changes, NOT LEGITIMATE). Pinned red first by `runner::run::tests::a_first_pass_refusal_naming_no_change_ejects_nothing_and_one_naming_a_task_ejects_its_change` and `a_first_pass_row_naming_two_changes_ejects_both_and_the_rest_lands` (two changes of three ejected as one entry, the third lands; a named row beside a lock stops).
7. **A kill between filing an entry and its `eject` lines resumes as a new attempt.** The resume runs what the log has not ejected (`runner::remaining`); an entry of the same batch and the same set is filed once (`repairs::file` returns its id). Label: the algorithmically easier route (no repair of a half-written ejection). What it costs: the entry's `ejected` may list a change the resume then lands, or re-ejects under a second entry. So AN ENTRY IS A CHANGE'S REPAIR ONLY WHERE AN `eject` LINE NAMES IT - data-model.md, "A repair entry", states it for T16's queue (`log::repairs_open`, and the repair's changes the `eject` lines' `change`s). Priced: finishing the interrupted ejection at resume (the entry's unejected changes ejected before the next attempt) - a second writer of `eject` lines for a window of two appends; not taken. Pinned by `runner::run::tests::a_kill_between_a_repair_entry_and_its_eject_lines_resumes_what_the_log_has_not_ejected`. Chosen by the closing half, 2026-11-27, as the brief named it.
8. **T20's Decision 6 revisited: only the runner's own `"stopped": true` line tells a death** (`wake::STOPPED`), not any `owed` line of the open batch. WHY: T20 wrote the rule for T14's red stand-in, which owed one line and stopped; since T15 an ejection owes its line and the runner goes on, so a runner killed in the next attempt left an open batch no line said - the coordinator never woken. Red first: `wake::tests::an_ejection_s_line_tells_no_death_so_a_runner_killed_after_it_is_said` failed on T20's rule (the wait returned the sentinel line, no death line). T20's own test kept, its line now the real exit -1 form. A stopped carry writes no `owed` line, so the wait's death line says it, once.
9. **The attribution's record is found where the gate's writer files it** (the handoff's check 1): a check's `Phase` line carries no task and no feature (`rustc/phase.rs`, `append_row_with(root, None, ...)`), so `event_log_hooks/filed.rs`'s chain reaches the pool's holder - `builder_pool::read` drops the lane's tree - and then `feature_of`: `L7R_FEATURE_DIRECTORY` (stripped by the runner), then the runner's `SPECIFY_FEATURE`, which `make land` exports again as the same spec (`land.rs`). Pinned by `runner::run::tests::a_check_s_phase_line_in_the_lane_s_tree_is_filed_where_the_attribution_reads_it` (the real writer, a stale `feature.json` naming another feature). No lane-tree `Phase` line exists yet to observe - none in the clone's logs, observed 2026-11-27, method: the same Python count of every log's `Phase` lines by `clone` (the lane has run no real batch); T23's real batch measures it.
10. **One `owed` line a repair entry**, naming the entry, its units and the attempt file. Label: the algorithmically easier route, FR-005's wake for a red batch - each entry is a dispatch the coordinator owes (D7: a fresh builder by `make builder-next`); the `owed` lines of one attempt are written together, so one `make lane-wait` returns them as one wake.
11. **The suite and row readers read the attempt file** (the handoff's check 2): `long_runs.rs`'s `run_gate` and `loud` spawn `make done` and `make hooks-test` with inherited stdout and stderr, `make done` prints `HOOK TESTS FAILED:` in its foreground loop (the static phases' log is printed after), `LAND_RUN` has no pipe, and the runner points `make land`'s stdout and stderr at the attempt file. The `--src hooks` Phase lines stay the fallback, not built.

### T15 Approach (checklist part A)

1. **The goal, in the world.** A red batch in the lane costs the coordinator one line a repair: the change the gate's record names leaves the batch as a repair entry for a fresh builder, the rest lands without a human.
2. **The constraints.** FR-005 (one wake an event), D6 step 2 and "By phase", D7 (repairs by fresh builders), D14 (an ejected change's ref kept), data-model.md's repair entry and log lines.
3. **Where each comes from.** R: plan.md D6, D7, D14; data-model.md. O: the crate counts above, the code read for checks 1 and 2.
4. **Do they describe the world here?** The crate count and the two readings, each pinned by a test; the real lane tree's lines are T23's.
5. **The order.** After T14, T20, T53 (merged `log::state`: `in batch` before `superseded`, a `landed` line listing a change as ejected reads ejected, both tested in `log::tests`); before T16 (reads the entries by Decision 7's rule), T18, T19.
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The lane crate's tests all green, 69 of 69, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane`); the red-first counts in the report.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Three wrong outcomes fixed: an innocent change ejected by a family `cover-build` red (Decision 3); a whole batch ejected for a first-pass refusal no change caused (Decision 6); a runner killed after an ejection never said to the coordinator (Decision 8). And one test reached again: `step` over an open batch returns `Ok(false)` and writes nothing, now with a hand-in waiting (red with the guard removed).

**Found and left?** none

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T16 (phase 2's repairs taken by fresh builders: a change the lane ejects is the next dispatch, briefed with the gate's output)

- **Approach**: `rust/guard/shared/src/builder_queue/repairs.rs` (new) reads the lane's three files by name - `l7r-lane/repairs.jsonl`, `l7r-lane/lane.jsonl` and the pool's log - since the guard cannot reach the lane crate (the lane builds on `l7r_shared`): `open` (an entry an `eject` line names, unanswered, not superseded), `offer` (READY, or passed over with why) and the knob `first` (`LANE_REPAIR_FIRST`). `builder_queue.rs` gains its `mod` line and one call in `idle`, so the pool-idle Stop block names the repair's command. The task crate: `builder_queue.rs`'s `repairs_said` is said first by `make builder-next`, `make queue` and `dispatch` (`make builder-done`'s step 1); `builder_brief.rs` takes `REPAIR=<id>` (the Makefile passes it), refuses one no open entry has or one not this brief's, logs it on the `brief` line and prints one block line naming the ejected commit and the attempt file; `builder_done.rs` copies it to the done line as `repair_of`. The handout and the supersede are T09's, reused: D14 keeps the ejected done ref, so `build_on` applies it onto the handout uncommitted and the repair's done moves the ref. This also closes 451 T308 (the two-tier split): the first tier the builder's (T06-T08), the full gate the lane's (T14), its "repaired by whoever is cheapest" replaced here by a fresh builder on a repair entry, its builder coverage by none.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **A repair is offered before every queue entry, a performance entry's included** (`LANE_REPAIR_FIRST` = 1, the plan's GUESS knob; `0` offers it only where no queue entry is picked). Label: D7's literal "read these entries before `queue.txt`'s" - a performance entry is a `queue.txt` entry. The open performance tasks NO line names stay first in `make builder-done`'s step 1 and the Stop block, since they are a line to write, not a dispatch. `make builder-next` says the repairs before them. Pinned by `builder_queue::tests::an_open_repair_entry_is_named_before_the_queue_s_next_entry` and `repairs::tests::a_free_tree_is_idle_over_an_open_repair_before_a_ready_queue_entry`, both ways of the knob.
2. **Open is read from the lane's lines, never the entry alone**: an entry is offered only once an `eject` line carries its id, its changes those lines' `change`s, its tasks their done lines' tasks (the entry's `tasks` where no done line names one). Label: data-model.md, "A repair entry", as T15's Decision 7 states it. Pinned by `repairs::tests::an_entry_is_open_once_ejected_its_changes_and_tasks_the_eject_lines` (r4 never ejected; r2's second sha landed on a resume).
3. **Closed by its answer or by a later hand-in of its task**: a `done` line naming it in `repair_of` (any done line: the builder briefed for it has ended), or a hand-in of its feature sharing a task, later than its last `eject` line (`superseded`). Label: data-model.md's "the earlier one's repair entry then read as closed (`superseded`)"; the done line's `repair_of` the data model's field. Pinned by `a_repair_is_closed_by_its_answer_or_a_later_hand_in_of_its_task` (an earlier hand-in, a done not handed in, another feature's task: none close it).
4. **Passed over, with a line: in flight, and a kind no brief takes.** A pool tree held for one of its tasks would be handed back to its holder, and a repair is a fresh builder's; `integrate` (T19) is no kind `make builder-brief` takes, so no command that refuses is offered. Label: the algorithmically easier route; T19 makes `integrate` briefable or keeps the line. Pinned by `in_flight_and_a_kind_no_brief_takes_are_passed_over`.
5. **`REPAIR=` passes the brief's mechanism refusal**: the task's line was briefed and built once, so the repair is one fix whatever its line names. And it is refused, before any tree is taken, where no open entry has the id (answered, superseded, never ejected) or where the entry's feature, tasks or kind are not the brief's - naming the command as filed. Label: the algorithmically easier route (US4: one fresh builder a repair).
6. **The handout's base is the clone's HEAD until T22**: the pool's take applies the ejected commit onto the handout's base, which is the clone's HEAD today; T22 moves the base to `origin/main` (D13). Label: D3's base by phase, read as T22's line says.
7. **The knob is read by the commands and handed in**: `run_with` and `dispatch_with` take it, so the task crate's tests run both ways (the shared crate's environment map is not compiled into the task crate's tests).
8. **A fresh builder, never one kept past its report** (451 T308): the queue never offers a repair in flight, and both the command's line and the brief's `REPAIR` line say FRESH. Label: the reviewer's rule, D7's table. Red first: the shared crate's `repairs` tests, 1 of 5 failed on the old `idle` (it offered the queue's T3 over the repair); the task crate's loop test, 0 of 1 passed with `builder_done.rs` at HEAD (no `repair_of` on the done line); the queue test does not compile against the old `builder_queue.rs` (no `run_with`, `dispatch_with`).

### T16 Approach (checklist part A)

1. **The goal, in the world.** An ejected change costs the coordinator one dispatch: `make builder-next` (and the Stop block, and `make builder-done`'s next line) names the repair's `make builder-brief ... REPAIR=`, whose block names the gate's output and the change, the tree holds the change uncommitted, and the repair's hand-in closes the entry.
2. **The constraints.** US4 ("The repair goes to a FRESH builder given the gate's output; no builder is kept past its report"), D7, D14, data-model.md's repair entry, 451 T308's two tiers.
3. **Where each comes from.** R: plan.md D7, D14; data-model.md; T15's Decision 7. O: the tests named above.
4. **Do they describe the world here?** No real repair entry exists yet (the lane has run no real batch, observed 2026-11-27: no `l7r-lane/repairs.jsonl` in the clone); the fixtures write the lane's own line shapes, `runner/run.rs`'s `eject` line and `repairs.rs`'s entry.
5. **The order.** After T15 (the writer) and T09 (the handout that builds on a done commit); before T22.
6. **The exits.** Green: the shared and task crates' tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/guard/shared rust/gate/crates/task rust/guard"` clean, 2026-11-27; the red-first counts in Decision 8.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a defect fixed: a new route. An ejected change had no reader - the lane filed entries no command offered, so a repair waited on the coordinator remembering it.

**Found and left?**
- `make lane`'s status (`rust/gate/crates/lane/src/log.rs`, `repairs_open`) lists a repair superseded by a later hand-in as open, where the queue closes it (Decision 3): the status says a repair is owed that no command offers. Not fixed here: the lane crate is T15's and T18's, its reader one change away. Filed as T65; lands before T23.

**Performance work?** no


<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-28 -->
### T18 (D6 step 4, D7's table: the lane's own red-gate tripwire, keyed by task, with the arbiter and its repair entry; T17's stand-down leaves the lane's runs to it)

- **Approach**: `rust/gate/crates/lane/src/tripwire.rs` (new, pure) reads a task's PINS - the `eject` lines of `lane.jsonl` with `why` `red`, `inferred` or `unplaced`, any batch, whose change is a hand-in of that feature's task (the pool log's `done` lines) - ONE A BATCH. `runner/run.rs`'s `eject` reads every group's trips before writing any line of the ejection: a group with no task pinned in another batch is filed as T15 filed it; a group with one is held, and once the others are filed `trip` writes each held change's `eject` line (`repair` null, `arbiter` the trigger, `attempt`), runs `make arbiter-ask SUBJECT=lane-<task> WHY=... FILES="<the pin before's attempt> <this attempt>"` in the lane's tree under `SPECIFY_FEATURE=<spec>` (its output kept as `<attempt>.arbiter.log`), writes the batch's `stop` line (`why` `arbiter`, `trigger`, `spec`, `tasks`, `held`, `attempts`) and stops the runner through `stopped()` - the coordinator's ONE owed line, naming the trigger and the bundle (the `MANIFEST.md` the ask printed), or, the ask refused, the command to run by hand. `step` first runs `file_ruled`: each such hold whose ruling the clone's `specs/<spec>/arbiter.jsonl` records is filed as ONE repair entry (`why` `arbiter`, `units` `<ruling>: <what>`, `attempt` the trigger), an `eject` line naming it a held change, and one owed line. `log::state` reads a held change `ejected -> the round arbiter <trigger>`, so it forms no batch while it waits. Red first, 2026-11-27, `make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests::tripwire"` on the old run.rs: 0 passed, 2 failed (the second pin's step returned `Ok`, a second repair filed). Green: the crate 80 of 80; `make builder-checks CRATE="rust/gate/crates/lane"` clean.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **Pins are counted by batch and keyed by (feature, task).** A task ejected twice in one batch - a kill between an entry and its `eject` lines, 461 T15 Decision 7 - is one pin; `T01` of 451 never pins `T01` of 461; a bundle's change pins each of its tasks; a change no hand-in names pins nothing. Label: D6's "each batch ejects a task at most once" and "keyed by TASK", the feature the easier and stricter reading. Pinned by `tripwire::tests::a_task_s_pins_are_its_pinning_ejections_one_a_batch_keyed_by_feature_and_task`.
2. **The held change's `eject` line is the hold.** A `stop` line of the batch closes it, so its other changes read `waiting` and land in the next batch; the held one's own `eject` line (no repair, the trigger it waits on) keeps it off every batch until the ruling's repair. Label: the easier route; the `stop` line's changes are `held`, not `changes`, so `log::mentions` never reads them as the last line naming the change. Pinned by the end-to-end test (a step with no ruling forms nothing; an innocent hand-in lands meanwhile).
3. **The ruling is read in the clone's `specs/<spec>/arbiter.jsonl`**, where `make arbiter-ruled` run in the clone writes it, uncommitted until the coordinator's push; not the lane's tree, which each batch resets to `origin/main`. Label: the easier route.
4. **The runner stops at the trip, and its next start files the ruling's repair** (`make lane-start`, which the owed line names, or a hand-in's own start). Label: the task's "the lane stops" read literally; no runner waits on a ruling the coordinator dispatches.
5. **A third pin asks under `lane-<task>-<n>`**, n the pin: `arbiter-ask` refuses a ruled trigger (one ruling a trigger, binding), so the second ruling needs a trigger of its own, and the first ruling, read under its own trigger, files nothing for the new hold. A bundle's tasks are joined `lane-<task>-<task>`. Label: the plan is silent; the easier route. Pinned by `runner::run::tests::tripwire::the_held_task_waits_on_its_ruling_whose_repair_is_filed_once_and_a_third_pin_asks_anew`.
6. **The ruling's `eject` line carries `of_batch`, not `batch`.** The batch ended at its `stop`; `log::state_of`, `tree/state.rs`'s `batch_open` and `builder_tree.rs`'s open check would read a later `eject` of it as the batch reopened. Label: the easier route over three readers' edits; data-model.md's `eject` row says it.
7. **An ask the arbiter refuses still stops the batch and holds the change**, its line naming `make arbiter-ask SUBJECT= FILES=` to run by hand; the hold waits on the same trigger. Label: the easier route (no retry). Pinned by `an_ask_the_arbiter_refuses_still_stops_the_batch_and_its_line_names_the_ask_to_run_by_hand`.
8. **The WHY avoids the pool-route words** (`route`, `regress`), which `arbiter bundle --check-ask` would refuse without a pool result (`sections::pool_unstated`), read 2026-11-27. Label: convention.

### T18 Approach (checklist part A)

1. **The goal, in the world.** A task the lane ejects red a second time - its repair red again, or one task ejected from two batches - stops the lane with no second repair and one line for the coordinator: dispatch the round arbiter on the bundle the lane asked for; once ruled, the lane files the ruling's work as one repair a fresh builder takes.
2. **The constraints.** D6 step 4 (the pin rule, the second pin, `make arbiter-ask SUBJECT=lane-<task>` with the two attempt files, one owed line), D7's table (the arbiter's row: the repair `why` `arbiter` filed once `make arbiter-ruled` records the ruling), FR-005, FR-008, data-model.md's batch and repair entry.
3. **Where each comes from.** R: plan.md D6, D7; tasks.md T18's line; data-model.md. O: `arbiter.rs`'s `ask_cli` and `home.rs` (the ask's feature, its "already ruled" refusal), `sections.rs`'s `pool_unstated`, and the three readers of a batch's `stop` line, read 2026-11-27.
4. **Do they describe the world here?** Yes: the owed triggers live in the git common directory the lane's tree shares (`arbiter-owed.json`), and the ruling in the clone's feature directory where the coordinator's round arbiter records it.
5. **The order.** After T15 (the red path, the repairs writer, `stopped()`) and T17 (the stand-down); before T22 (T17's plan review) and T24 (the halving's `inferred` pins).
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The lane crate 80 of 80, 2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`); the red-first counts above.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: new behavior. One test defect fixed on the way: the T15 tests' stand-in Phase line had no newline, so a second red attempt's line was glued to the first and neither parsed - the new tests write it with its newline (`red()`); the old tests write it once and are unchanged.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T19 (phase 2's failed push: a green batch whose push fails runs again once on the new `origin/main`, and a second failure is one `integrate` repair entry)

- **Approach**: `rust/gate/crates/lane/src/runner/run.rs`. `land()` now returns an `Attempt` - `Pushed`, `PushFailed` or `Red` - and tells a failed push by the landing's own line `land: the push failed (exit ` (`PUSH_FAILED`, `land.rs`'s warning, which reaches the attempt file as its stderr) in the attempt's output, with the set not on `origin/main` once fetched; such an attempt runs no attribution, writes its `run` line (`red` empty) and a `push` line with `"failed": true` (data-model.md's `push` row amended). `run_batch` counts the batch's failed pushes, a resumed batch's earlier ones from its `push` lines: the first runs the same set again on the tree brought to the new `origin/main` (`bring`, which fetches); the second calls `integrate()`, which files ONE repair entry (`kind` `integrate`, `why` `push`, `tasks` every change's, `ejected` every sha, `units` the push line, `attempt` the second attempt file) before its `eject` lines (`why` `push`), and the batch ends with its `landed` line and ONE `owed` line, the entry's, never `stopped`. To keep `land` and `run_batch` under clippy's `too_many_lines` cap (102 and 117 lines measured 2026-11-27, `make builder-checks`'s lint), `note_of`, `attempt_file` and `ended` (the landed line's wording, unchanged) moved out. Measured 2026-11-27: red first, the three new tests of `runner::run::tests` failed on the old code - each push failure was read as a red the record could not place and the whole set ejected as an `unplaced` `fix` entry (which PINS its tasks, data-model.md) - and 19 of 19 of the module pass after (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests"`); `make builder-checks CRATE="rust/gate/crates/lane"` clean.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **A failed push is told by the landing's own line in the attempt's output** (`land: the push failed (exit `), not by the `push` Phase line of the event log. Label: the algorithmically easier route, the reading T15's Decision 11 already takes for the suites and the first pass's rows (the runner points the landing's stdout and stderr at the attempt file); the `push` Phase line's code also covers a tick commit that failed (`land.rs`, "the tick's commit failed"), which is no push. A landing whose push failed without that line (the land crate's wording changed) reads as an unplaced red, as before T19.
2. **"Once" is once a batch**, counted over the batch's `push` lines with `"failed": true`, so a runner killed after the first failure files the entry at the resumed batch's next failure rather than retrying again. Label: the literal reading of the plan's "runs the batch again once; a second failure files"; pinned by `a_resumed_batch_whose_push_had_failed_once_files_the_integrate_entry_at_its_next_failure`.
3. **One `owed` line for the integrate case, written after the `landed` line**: the entry's line stands in for the batch's end line, so the coordinator is woken once, after the batch is closed. Label: the task line's "one `integrate` entry and one owed line" read literally (FR-005, one wake an event); T15's red path keeps its line an entry plus the end line.
4. **`units` holds the push's own line**, the attempt file its full output. Label: GUESS, a reading aid for the fresh builder; data-model.md names only `attempt` for a `push` entry.

### T19 Approach (checklist part A)

1. **The goal, in the world.** A green batch that cannot push - main moved under it, as a DIRECT push from the coordinator can make it - lands on the second try without anyone, and where it still cannot, the coordinator gets one line and dispatches a fresh builder; it never pushes, carries or resolves it.
2. **The constraints.** plan.md Risks, "Two writers of main"; D7's table (the `integrate` entry for a fresh builder); data-model.md's repair entry (`push`: `tasks` every change of the set, `attempt` the push's output) and its states (a push failed twice is not `stopped`); FR-005.
3. **Where each comes from.** R: plan.md D7, Risks; data-model.md. O: the red-first counts above; `land.rs`'s push-failed warning read.
4. **Do they describe the world here?** The stand-in landing of the end-to-end tests fails its push as `land.rs` says it, and the once case pushes another writer's commit to `origin/main` meanwhile, so only a tree brought to the new main pushes (its stand-in push is not forced). A real failed push in the lane is T23's to observe.
5. **The order.** After T15 (the repairs writer, `eject` lines, the owed-line rule); beside T18 (the tripwire, another tree), this task's edits kept to the push path.
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `runner::run::tests` 19 of 19, the crate's builder checks clean, 2026-11-27.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome fixed: a green batch whose push failed was ejected whole as an `unplaced` `fix` repair, pinning its tasks toward the round arbiter's second-pin stop for no red, and was never retried on the new main.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T20 (D9, FR-005: phase 2's coordinator wake-up, the lines T14's runner owes printed once; lands after T14)

- **Approach**: `rust/guard/shared/src/lane_wake.rs` (new, with `lane_wake/tests.rs`) is the read mark; `rust/gate/crates/lane/src/wake.rs`
  (new, with `wake/tests.rs`) is `l7r-gate lane wait`, the verb `["wait"]` in `lane.rs` and the Makefile's `lane-wait` (its help
  line names the knobs; `docs/make-targets.html` regenerated); the prompt hook `clone_sync_hooks.rs` `prompt()` prints the unread
  lines. `log.rs`'s `DIR`/`FILE` now point at `lane_wake`'s; `runner::knob` became `pub(crate)`. `dev/audits/lane-wake.md` covers
  `WAIT_POLL_S`, `DEAD_GRACE_S` and `LOCK_S`; the lane crate's row in `rust/gate/CLAUDE.md` names `wake.rs`. Built in two halves
  (2026-11-27); the build half's handoff is `<clone git dir>/l7r-handoffs/T20-build.md`.
- **Decision 1 - one mark reader, in `l7r_shared::lane_wake`.** `take_unread(common)` returns the `line` of every `owed` event past
  `l7r-lane/read-mark` (a byte offset into `lane.jsonl`) and moves the mark past the last COMPLETE line (a torn tail is read again
  once whole), under `read-mark.lock` by flock, let go by `flock -u` before the close (T14's reason: a forked child holds a copy of
  the descriptor), the mark written by a rename; a mark past the log's end or no number reads from 0; with no log nothing is taken
  and nothing created; a lock not got within `LOCK_S` takes nothing (the holder is showing the lines). `unread(common)` is a
  lock-free length-against-mark test, so a poll with nothing new spawns no flock. Both `make lane-wait` and the prompt hook call it,
  so one rule says what is unread. Why here: the guard depends only on `l7r_shared` (the checks' `guard_deps`), and a hook shelling
  out to the gate binary would pay a launcher start each prompt. Label: the easier route.
- **Decision 2 - whichever reader comes first moves the mark, the hook included.** A hook that printed without moving it would have
  each re-armed wait print at once what the prompt already showed: a wake FR-005 does not list. The read, the take and the move are
  serialized by the mark's lock, so a line is shown once, by the prompt or by the wait, never both. Label: the easier route of D9's
  "prints any unread lane lines, so a wake-up command killed early loses nothing".
- **Decision 3 - the runner-dead line is written by the wait.** A killed runner writes nothing, and a runner stopped on an error
  (T14's stopped carry or refused landing) writes `stop` but owes nothing, so a wait reading only `owed` lines would block for ever
  over a stranded batch. Rule (`wake::dead`): no runner holds the lane's lock, the log's LAST batch is open, and no `owed` line with
  `why: "runner"` since the last `start` line (said once a death); held `LANE_DEAD_GRACE_S` continuously (reset whenever the runner
  is seen or nothing is stranded), so a runner a hand-in is starting is not called dead. The wait then appends ONE `owed` line
  `{"batch", "why": "runner", "line"}` naming the batch, its changes, the runner's last stop (or `killed`) and `make lane-start`,
  and loops, so it prints that line through the mark like any other. Quiet with no open batch: an `idle` end, `make lane-stop` after
  a landing, and phase 1's waiting hand-ins with no runner (landed by hand). Label: the easier route (a stranded batch is the one
  case in which no other line will come).
- **Decision 4 - the prompt hook prints before `solo::alone`'s return.** `prompt()` extends its lines with
  `take_unread(<clone>/.git)` after the feature.json notice and before the only-session return, because a coordinator whose
  builders are subagents IS the only session, and the return would otherwise drop the lane's lines for exactly the session they
  are owed to. This changes the hook's rendering: an unread lane line now appears among its prompt lines. Label: the easier route.
- **Decision 5 - the wiring and the knobs.** The verb takes no flags, its knobs from the environment, because the stall watchdog's
  `waits_on_lane` (T12) matches exactly `<dir>/l7r-gate lane wait` (confirmed live below). `wait_cli` exits 0 with each line
  printed, 2 on a knob that is no number, 1 on a dead line it cannot write. `WAIT_POLL_S` 5 s (the runner's own `POLL_S`),
  `DEAD_GRACE_S` 30 s (past `START_WAIT_S` and a short rebuild, T51), `LOCK_S` 5 s: all GUESS, each beside its constant and in
  `dev/audits/lane-wake.md`. No ceiling (D9's `LANE_WAIT_MAX`: none). Label: GUESS for the numbers; convention (the watchdog's
  argv) for the flagless verb.
- **Decision 6 - one red run wakes once: the runner's own line for the batch tells the death.** With T14's red stand-in a red run
  writes its ONE `owed` line (`... - the runner stopped, the batch open; ...: <attempt file>`), THEN the runner stops with `error:`
  and leaves the batch open. Under Decision 3 alone the coordinator's re-armed wait would see no runner over that open batch and,
  `DEAD_GRACE_S` after the re-arm, write and print a runner-dead line for the same batch: a second wake for one red, one FR-005 does
  not list (540k-966k tokens a wake, measured 2026-11-27 (the transcript's usage fields), as D9 records). So `wake::dead` counts any
  `owed` line naming the open batch since the last `start` - a `why: "runner"` line or the runner's own - as having told it. Nothing
  is lost: that red line already says the runner stopped; a runner started again (a new `start`) and killed is a new death, said.
  The rule can go with T15, whose red path no longer stops the runner. Label: the easier route. The build half's handoff had
  accepted the double wake until T15; the plan review (round 3, 2026-11-27) ruled that NOT LEGITIMATE under FR-005, so it is fixed
  here.
- **Not here.** T47 (the watchdog's long-run exemption of `make lane-wait`, `pass.rs`) and T21 (the Stop rule that keeps the wait
  armed) are their own tasks. T21's "the lane holds a waiting hand-in or an open batch" reading is not exposed by this task: the
  guard cannot reach the lane crate, so T21 needs its own reading in `l7r_shared` (as `lane_wake` is).
- Red first (2026-11-27, the build half): `l7r_shared` `lane_wake::tests` against stubs (`unread` false, `take_unread` empty), 1
  passed, 4 failed; after, 5 of 5. The lane crate's `wake::tests` against a stub `wait` returning no lines, 0 passed, 6 failed;
  after, 6 of 6 (a seventh, the command sleeping on the real clock until a thread writes the line, added after for `wait_cli`'s real
  sleep, written green). Decision 6 (2026-11-27, the closing half): `wake::tests::a_red_run_s_own_line_tells_the_death_so_one_red_wakes_once`
  under the old `dead`, 6 passed, 1 failed; after, 7 of 7. The guard's `clone_sync_hooks::tests::an_unread_lane_line_is_printed_once_and_marked` without the hook's
  line, 0 passed, 1 failed (left "", right the line); after, 1 of 1, the module 33 of 33. `tests/hooks/test-clone-sync-hooks.sh`
  68 ok with its two new cases (an unread line printed on the prompt, then not again); not run red (the Rust test is the red one).
  Live (2026-11-27, a scratch repository whose Makefile calls this tree's `scripts/gates/l7r-gate.sh lane wait`):
  `/proc/<pid>/cmdline` read `.../tool/l7r-gate|lane|wait|`, an appended owed line ended it printing `lane: live line`, exit 0,
  `read-mark` 42 = the log's 42 bytes, observed 2026-11-27, method: that live run. Nothing run against the real clone's lane (it has no `l7r-lane/`).

### T20 Approach (checklist part A)

1. **The goal, in the world.** A coordinator that runs `make lane-wait` in the background is woken once for each line the lane owes
   it - a landed batch's status, a repair, an arbiter owed, a stranded batch's dead runner - and never twice for one line, whether
   the wait or its next prompt shows it first; a wait killed early loses nothing.
2. **The constraints.** D9 (one background command, the mark, no ceiling, the prompt hook's unread lines), FR-005 ("once per landed
   batch with a short status, and otherwise only for US5's cases"), D8 (the log a JSON line a transition), T12's `waits_on_lane`
   argv, T14's owed line and its red stand-in, data-model.md ("The log line").
3. **Where each comes from.** G: FR-005's words. R: plan.md D8, D9; data-model.md; T12's and T14's plan sections; the build half's
   handoff. O: the red-first counts and the live run above.
4. **Do they describe the world here?** Yes for a scratch repository: the live run's real `l7r-gate lane wait` was matched by its
   argv and ended by an appended line, the mark at the log's end. Not yet for the real clone's lane, which has no `l7r-lane/`:
   T23 runs the real batch.
5. **The order.** After T14 (the owed lines) and T53; with T47 (the watchdog exemption); before T15 (which may drop Decision 6's red-line rule), T21 (the Stop rule), T22 (the base
   flipped, with T56) and T23.
6. **The exits.** Green: the changed crates' tests and `make builder-checks` clean, the clone-sync suite green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the runner dead has no writer (Decision 3), found by reading T14's stop path; and the double wake it
   left over a red, fixed red-first (Decision 6).
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27; the first tier green again at the closing half.
10. **Before moving a constant.** n/a: `WAIT_POLL_S`, `DEAD_GRACE_S` and `LOCK_S` are new, labeled GUESS and audited.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** New code; one wrong outcome of the build half fixed in it: a red run woke the coordinator twice (Decision 6).

**Found and left?**

- A WAITING hand-in that no runner serves (from phase 2's base, a runner start that failed past `START_WAIT_S`, T51's rebuild) is
  not called dead by `wake::dead`, which reads only an open batch, so the coordinator's wait - which T21's Stop rule keeps armed -
  blocks with nothing ever coming. Not fixed here: in phase 1 such hand-ins are landed by hand and must stay quiet, and the base
  flips in T22. Filed as T56; lands before T23 (with T22).

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T21 (D9, FR-005: the Stop rule that keeps the coordinator's `make lane-wait` armed; lands after T20)

- **Approach**: `rust/guard/src/guards/pool_idle_hooks.rs` gains a second rule beside the free-tree rule (`judge_lane`,
  `lane_refusal`, `Lane`), the lane's state read in `l7r_shared::lane_wake::holds` (`rust/guard/shared/src/lane_wake.rs`, its
  tests in `lane_wake/holds_tests.rs`), because the guard cannot reach the lane crate (T20's "Not here"). Tests:
  `pool_idle_hooks/tests.rs` (three new) and `tests/hooks/test-pool-idle-hooks.sh` (ten new cases).
- **Decision 1 - what the lane holds, read in `l7r_shared`, parallel to the lane crate's `log.rs`.** `holds(common)` says, in a few
  words, the lane's first open batch (a batch whose last state-moving line - `MOVES`, `state_of`'s events - is neither `landed` nor
  `stop`, its lines routed as `batches` routes them, so a batch resumed after a `stop` is open again), else its first waiting
  hand-in; none where the lane has no log. The waiting reading follows `log::state` with no batch open (in-batch cannot hold):
  the pool log's `handed_in` done lines, a commit's first, still the lane's (a done ref or a lane line names it), not landed by a
  `landed` line, not ejected (the last line naming it an `eject`, or a `landed` line listing it ejected), not superseded. "Landed"
  by `origin/main` (`held_by`) is not asked: a git walk a Stop hook would pay each turn; cost, a hand-in landed on `origin/main` by
  hand while its done ref still stands reads as waiting, which `make carry` (the ref deleted at its end) does not leave. Label: the
  easier route; the duplication is filed as T63 (one reading, `log.rs`'s pure readers moved to `l7r_shared` and re-exported).
- **Decision 2 - a waiting hand-in counts only while the runner lives.** A deliberate deviation from D9's literal "a waiting
  hand-in", for phase 1: until T22 flips `HAND_IN_BASE` no hand-in starts the runner (T12 Decision 6), the coordinator lands each by
  hand, and a wait over it could never wake (`wake::dead` is quiet there on purpose, T20 Decision 3) - so the rule would refuse
  every stop after a hand-in and arm a wait with nothing coming. The runner's lock (`lane.lock`, `RUNNER_LOCK`) is probed as
  `runner::held` probes it (`flock -n`, let go by `flock -u`). No second reading of the knob is made. From T22's base a waiting
  hand-in no runner serves (T56's case) holds no stop: Not fixed here: the base and its one reading are T22's. Filed as T64; lands
  with T22 and T56.
- **Decision 3 - "a `make lane-wait` of this clone runs": its `make` or the wait itself, any process of the clone.** A `/proc`
  process whose argv is `l7r-gate lane wait` (T12's `waits_on_lane`) or a `make` whose one target is `lane-wait` past its flags,
  a valued flag's value and `VAR=` words (`pass::lane_wait_make`, shared with T47), its working directory in the clone. The make
  counts from its start, while `l7r-gate.sh` may still build the binary (T54: 2 to 112 s, measured 2026-11-27 (T54's scratch-clone rebuilds)), so a stop in that gap is not refused.
  Any process of the clone, not only the session's own (as T12's `lane_works` asks): the plan's Scale is one session a clone,
  several sessions feature 459's, and a Stop hook has no registry pid to walk from. On the reviewer's note that T20's Decisions 2
  and 4 assume one session: not found in `plan-review.json` or the ledger; the same assumption is taken here, as D9's "of this
  clone" words it. `/proc` is `POOL_IDLE_PROC` in a suite. Label: the easier route.
- **Decision 4 - one block, and an escape of its own.** Where both rules hold, the free tree's block and the lane's are said in ONE
  Stop block (each refused stop is a wake, 540k-966k tokens, D9). `POOL_IDLE_OK` waives the tree rule only: a turn that keeps a
  tree free for the GM still owes its wait; the lane rule's escape is a line starting `LANE_WAIT_OK: <reason>`, checked first and
  recorded (rule `LANE_WAIT_OK`; a bare one `LANE_WAIT_OK-no-reason`; a held stop `lane-unwatched`). The block names the exact
  command, `make -C <clone> lane-wait`, with `run_in_background: true`. NEW GUARD MESSAGES: the lane block and the bare-escape block
  (the session runs their check). The escape parser is shared by both rules (`reason`). Label: convention (`POOL_IDLE_OK`'s form).
- Red first (2026-11-27): `l7r_shared` `lane_wake::holds_tests` against a stub `holds` returning none, 0 passed, 2 failed; after,
  `lane_wake` 7 of 7. The guard's `pool_idle_hooks::tests` against stub `judge_lane`/`lane_refusal` (quiet, none), 6 passed, 3
  failed; after, 9 of 9. `tests/hooks/test-pool-idle-hooks.sh` with `judge_lane` returning quiet at its top (the rule deleted), 37
  passed, 5 failed; restored, 42 of 42. `make builder-checks CRATE="rust/guard rust/guard/shared"`: 636 and 617 tests, lint and
  format clean, observed 2026-11-27, method: that run's log.

### T21 Approach (checklist part A)

1. **The goal, in the world.** A coordinator cannot end its turn while the lane holds work whose line will come and nothing would
   wake it; told the one command, it starts `make lane-wait` in the background and is woken once by the line. Phase 1's hand-ins,
   landed by hand, hold nothing.
2. **The constraints.** D9 (the Stop rule, its message the exact command with `run_in_background: true`, its suite case and quiet
   case, XVIII), FR-005 (no wake it does not list), D8 (the states computed from the logs), T12 Decision 6 (no runner before T22's
   base), T20's mark and Decision 3, the plan's Scale (one session a clone).
3. **Where each comes from.** G: FR-005's words. R: plan.md D8, D9; data-model.md; T12's and T20's sections. O: the red-first
   counts above.
4. **Do they describe the world here?** On fixtures: a scratch repository with done refs and the pool and lane logs, a fake
   `/proc`. Not on the real clone's lane, which has no `l7r-lane/`: T23 runs the real batch.
5. **The order.** After T20 (the wait it arms); with T47; before T22 (with T64 and T56) and T23.
6. **The exits.** Green: the changed crates' tests, `make builder-checks`, the pool-idle suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the literal rule refuses every stop in phase 1 (Decision 2), found by reading T12 Decision 6 and
   `wake::dead`.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27.
10. **Before moving a constant.** n/a: no constant moved; `RUNNER_LOCK` mirrors `runner::LOCK`.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** New rule: without it a coordinator ends its turn over an open batch with no wait armed and is woken by
   nothing until the GM prompts it.

**Found and left?**

- The lane's states read twice, in `log.rs` and `lane_wake` (Decision 1): a later change to either drifts the Stop rule.
  Not fixed here: the lane crate is outside this task's crates. Filed as T63; lands before T26.
- From T22's base a waiting hand-in no runner serves holds no stop (Decision 2). Not fixed here: the base's one reading is T22's.
  Filed as T64; lands before T23 (with T22 and T56).

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T32, T33 (bundle) (`make rust-test CRATE="<several>"` failed on one joined manifest path, found running T05's four-crate Verify line; `make task-time`'s cross-blocking row of a closed window grew after it ended, found reading phase 5's before and after)

- **Approach (T32)**: `rust/gate/crates/rustc/src/rustc.rs`'s `parse` splits each `--crate` value on white space, so `make rust-test CRATE="a b"` (whose recipe passes `--crate "$(CRATE)"`, one value) is each crate, as `make builder-checks`' `foreach` already passes them; a value naming no crate (`CRATE=" "`) is refused with the usage, where an empty list would have run every crate. Fixed at the parser, not the Makefile: it covers every caller that passes one joined value (`rust-test`, `test-times`), and a red test can live there. `ONLY=` across several crates was checked in `only.rs`: its words go to every crate's binaries, and a crate the filter misses is that crate's failure, as before.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions, T32** (each labeled):

1. **Split at the parser, not the recipe**: one fix for every `--crate` caller, tested in the crate. Label: the algorithmically easier route (the task line offers "split ... or refuse"; split is what `builder-checks` already does). A crate directory with a space in its name cannot be named; none exists under `rust/`, and cargo's package paths in this tree have none.
2. **A blank value refused**: `--crate " "` returns no parse (the usage), never "no crate named, so every crate". Label: the safe reading of an empty list.
3. **Red first**: `rustc::tests::the_arguments_are_parsed_and_each_failure_says_its_fix`, with `--crate " rust/a  rust/b " --crate rust/c` expected to be three crates and `--crate " "` refused, failed on the old code, 0 of 1 run (left `[" rust/a  rust/b ", "rust/c"]`), measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/rustc ONLY=the_arguments_are_parsed` in pool tree t270). The literal call of T05's line, `make rust-test CRATE="rust/gate/crates/land rust/gate/crates/task rust/gate/crates/tree rust/guard"`, exited 2 before ("manifest path `.../land rust/gate/crates/task rust/gate/crates/tree rust/guard/Cargo.toml` does not exist") and exits 0 after, "test clean on 4 crate(s)" (land 223, task 163, tree 64 passed, guard's kept green), measured 2026-11-28 (that call run in pool tree t270 before and after the fix, its `rust-checks:` lines).

- **Approach (T33)**: `rust/gate/crates/measure/src/measure/task_time/cross.rs`'s `gaps` gives each tree's last hold, where it was released, an open free span (to infinity), which `measure`'s cuts already clip at the window's end (`hi`: `UNTIL=`, else the last event read - the "or now"); a span before a later handout still ends at that handout. So a tree freed in the window counts to the window's end whether or not its next handout has been logged yet, and a closed window's figure no longer moves as later handouts reach `builder-pool.log`. The module doc and `said`'s paragraph restated (the old "a tree never handed out again is not counted" and "a tree handed out later is taken to have had work waiting" go; the upper bound now says a free tree is taken to have had work waiting).

**Decisions, T33** (each labeled):

4. **Counted to the window's end, not dropped**: of the task line's two rules (count an open span to the window's end, or not at all), the first, so a tree freed during a landing and not yet retaken counts during that landing. Label: the brief's reading ("a free span must end at the window's end (or now)"). Its cost: a tree freed and never handed out again (a retired or spare tree) now counts during every landing, bounded by the places left open (`L7R_BUILDERS` less the trees held); the record cannot tell a spare tree from one with work waiting, which was already the source's stated upper bound.
5. **A fixture figure moves, deliberately**: `cross_tests.rs`' tree `pc`, free from 03:00 with no handout after, now counts 03:00 to 04:00 of the landing, so the free-tree source moves 2.0 to 3.0 min and the row 2.5 to 3.5 min, measured 2026-11-28 (the fixture's report under the fix, matching a count by hand: two trees free 03:00-04:00 with two places open, the refusal's seconds beside them once). Its doc and both assertions say why.
6. **Red first**: `cross::tests::a_free_span_open_at_the_windows_end_counts_to_it_whatever_follows` (tree a freed at 30 inside a landing 20-80 of the window 0-100, read with and without a handout at 150 after the window) failed on the old code, 0 min read before the handout was logged against 50 after, 0 of 1 run, measured 2026-11-28 (`make rust-test CRATE=rust/gate/crates/measure ONLY=a_free_span_open_at_the_windows_end`). After: 311 of 311 of the measure crate's tests pass, measured 2026-11-28 (`make rust-test CRATE=rust/gate/crates/measure`).
7. **The night's window re-read**: `make task-time SINCE=2026-11-27T02:00:00Z UNTIL=2026-11-27T14:29:00Z` with the fix gives 53.7 min (164.5 tasks' side blocking), measured 2026-11-28 about 00:40Z (that run's report, its cross-blocking line and its tasks' side working row), equal to the old code's 17:55Z read: every tree freed in that window (t271, t270 and b1 included, b1 taken again 23:54Z) has been handed out since, so the old rule had caught up and the new one gives the same figure without waiting. T31 reads this figure.

### T32, T33 Approach (checklist part A)

1. **The goal, in the world.** T32: `make rust-test CRATE="<several>"` runs each crate named, as `make builder-checks CRATE=` does, so a Verify line naming several crates is one call. T33: a closed window's cross-blocking row reads the same whenever it is run, so phase 5's before and after (T31) compare like with like.
2. **The constraints.** T32: the task line; `only.rs`'s rule that a filter names its crate; the Makefile's `rust-test` recipe unchanged (a guard file; its `##` help still says `CRATE=<dir>`, the parser now taking several). T33: the free-tree and refused-handout sources of 451 T510 and their once-a-second rule, the task line's "one rule for both windows".
3. **Where each comes from.** O: the red runs (Decisions 3 and 6), the task line's two reads (32.3 then 53.7 min, observed 2026-11-27, method: both runs' headers, as the task line says) and the re-read (Decision 7). R: the task lines; `cross.rs`'s module doc.
4. **Do they describe the world here?** Yes: the four-crate call was run in this pool tree before and after; the night's window re-read on today's pool log.
5. **The order.** T32 before T05's Verify line is run again; T33 before T31. Independent of each other.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/rustc rust/gate/crates/measure"` clean (rustc 161, measure 311 passed; lint and format clean, 2026-11-28) and the four-crate call clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The four-crate call exits 0, "test clean on 4 crate(s)"; T33's red test green and the night's window at 53.7 min, measured 2026-11-28 (Decision 7's run).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T32: a builder following a several-crate Verify line got exit 2 and no test run; now the crates run. T33: a reader comparing two windows saw a difference made by when each was run (21.4 min of the night's 53.7, observed 2026-11-27, method: the task line's two reads), and now the figure is fixed when the window closes.

**Found and left?** None.

**Performance work?** Yes for T33, as a measurement of where time goes (451 FR-013): it corrects a figure of the task time breakdown; no engine speed, so no performance checklist. T32: no.


<!-- plan-archive: archived 2026-11-28 -->
### T46 (T13's found-and-left: the builder-tree help lines said nothing of the lane)

- **Approach**: three `##` help lines of the root Makefile (through `make guard-edit FILE=Makefile`, a guard file) restated to
  what the code does now, read 2026-11-27 in `rust/gate/crates/task/src/builder_tree.rs` and T13's, T49's and T50's sections:
  `builder-tree-adopt` - the lane's tree (`L7R_LANE_TREE`, else `<clone>-land`) joins as the lane's, held by the reserved holder
  `lane`, no handout takes it, the cap does not count it, a `T=` or a second lane refused; the runner's `l7r-gate builder-tree
  lane` (no make target) brings it to `origin/main` at each batch's start and makes it again at its path, its cache kept, when it
  is gone from disk (T13, T50); `builder-tree-drop` - takes the lane's tree too, refused while the lane's runner lives (`make
  lane-stop` first) or a batch of its log is open (`make lane-start` runs it to its landing or its stop) (T49); `builder-trees` -
  lists the lane's tree, held by `lane`, apart from the cap (T13, the list header's `, and the lane's tree`). `make docs`
  regenerated `docs/make-targets.html` (224 targets, 0 undocumented). No code changed. Red first: none applies - no test pins
  these help lines' words (grep of `tests/` and `rust/` for the three target names, 2026-11-27: only the builder-pool guard's
  REMOVE message and the crate's own stdout, both unchanged).

### T46 Approach (checklist part A)

1. **The goal, in the world.** A reader of `make help` or `docs/make-targets.html` adopting `<clone>-land` is told it becomes the
   lane's tree, how the lane brings it to `origin/main` and re-makes it, and how it is dropped.
2. **The constraints.** T13 (the lane holder, the cap, the reserved word, `builder-tree lane`), T49 (the lane's drop), T50 (the
   re-make), T12's hold on the Makefile (landed before this).
3. **Where each comes from.** R: tasks.md T46's line, T13's, T49's and T50's plan sections; O: `builder_tree.rs`, read 2026-11-27.
4. **Do they describe the world here?** Yes: each clause matches a message the crate's lane tests pin (`builder_tree/tests/lane.rs`).
5. **The order.** After T12, T13, T49 and T50; before T22.
6. **The exits.** Green: `make docs` writes the page with 0 undocumented. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the three targets found by one grep of the Makefile.
8. **The budget.** One landing.
9. **Done, measured.** `make help` and `docs/make-targets.html` carry the lane's adoption, `builder-tree lane`, the re-make and the
   lane's drop.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of the help lines is told the lane's rules; nothing else changes.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T49 (T45's found-and-left: the drop of the lane's tree was a dead end)

- **Approach**: `drop_tree` (`rust/gate/crates/task/src/builder_tree.rs`) takes the lane's tree itself: a tree held by
  `builder_pool::LANE` is asked `lane_busy` in place of the held refusal - refused while the lane's runner lives
  (`l7r-lane/lane.lock` held, probed by `flock -n` as the lane's `runner::held`; the refusal names `make lane-stop`) or while a
  batch of `l7r-lane/lane.jsonl` is open (the refusal names the batch and `make lane-start`, which runs it to its landing or its
  stop); otherwise removed as any free tree is - REASON owed, the worktree, its cache and its registry line gone, a `drop` line
  logged - and adoptable again. THE LOG'S READING mirrors the lane's own grouping, not T17's one-batch question (`lane/src/log.rs`,
  `batches` and `state_of`, read 2026-11-27): a batch's lines are those naming it after its `batch` line (a later `batch` line of
  the same id a new batch), `landed` or `stop` naming it ends it, `carry`/`eject`/`run`/`attribute`/`push` reopen it, and a line
  naming no batch - the runner's own `stop` (`runner.rs`, `{pid, why}`), whose batch is resumed at the next start - or a torn line
  changes nothing. Read here, as `tree`'s `state::lane_run` reads it (461 T17), because the lane crate builds on `task`; a third
  reader of the log beside the lane and T17 (kept private here rather than making `tree`'s helpers public, which asks a different
  question - one named batch - and would put a second crate in this task). Every builder tree's rules are as they were: the
  not-free branch and its message unchanged. No guard-rendered message changed: the builder-pool guard's REMOVE message (T45)
  already names `make builder-tree-drop TREE=<path>`, which now works for the lane's tree.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY="builder_tree::tests::lane"` on the old code): 3 passed,
  1 failed - `the_lane_s_tree_goes_by_the_drop_once_no_runner_lives_and_no_batch_is_open` answered `is held by lane - make
  builder-tree-release T=lane first`. Green: `builder_tree::tests` 13 of 13; `make builder-checks CRATE="rust/gate/crates/task"`
  clean, the crate 157 of 157. The test covers the REASON, the lock held (refused) and present but free (passes), a batch open
  beside a runner's batch-less `stop`, a batch-keyed `stop` and a torn line (refused, the tree and registry kept), a batch landed,
  reopened by a `run` and landed again (drops, tree and cache gone, the registry's `lane` line gone), and a re-adoption then a
  drop of the tree gone from disk.

### T49 Approach (checklist part A)

1. **The goal, in the world.** A session retiring `<clone>-land` runs `make builder-tree-drop TREE=<it> REASON=` once the lane is
   idle, and is told what to stop first while it is not, with no `BUILDER_TREE_OK` escape.
2. **The constraints.** D1 (the lane's tree and its holder), T13 (`lane` reserved: no release frees it), T45 (the REMOVE message
   names the drop), T17 (the log and lock read without depending on the lane crate), the brief: refused while the runner lives or a
   batch is open, every builder tree's rules kept.
3. **Where each comes from.** R: tasks.md T49's line, T45's found-and-left item; O: `drop_tree`'s held check, the lane's
   `log::batches`/`state_of` and `runner::held`/`stop`, read 2026-11-27.
4. **Do they describe the world here?** Yes: the red test shows the old drop refused the lane's tree with the release T13 refuses.
5. **The order.** After T13, T17 and T45; before T22.
6. **The exits.** Green: the lane test and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one caller of the held refusal (`drop_tree`), read.
8. **The budget.** One landing.
9. **Done, measured.** The lane drop test green; in use, `make builder-tree-drop TREE=/diagram/.clones/diagram-backlog-land
   REASON=...` with no runner and no open batch removes it.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session retiring the lane's tree is no longer left only the guard's escape; nothing else a reader sees
    changes.

**Found and left?**
- The lane's tree gone from disk mid-batch is still a dead end: `builder-tree lane`'s gone-from-disk refusal names the drop, which
  is refused while the runner lives (it made the call) and, after `make lane-stop`, while its batch stays open (resumed at the next
  start, which calls `lane` again). Not fixed here: the task's words refuse the drop while a batch is open, and the route a gone
  tree needs is a decision of its own. Filed as T50; lands before T22.

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T50 (T49's found-and-left: the lane's tree gone from disk mid-batch was a dead end)

- **Approach**: the task line's first route, a re-made worktree at the registry's path. `lane_start`
  (`rust/gate/crates/task/src/builder_tree.rs`), finding the registry's lane tree gone from disk, runs `git worktree prune` (a
  hand `rm -rf` leaves git's record of the path, and the add would refuse it) and `git worktree add -q --detach <path> <the
  clone's HEAD>` from the clone, logs a `remake` line, says `was gone from disk: made again there, its build cache kept` on
  stderr, and falls through to the fetch, reset, clean and detach at `origin/main` as before. WHY THIS ROUTE, not the drop: the
  drop's route was the loop itself - refused while the runner lives (the runner made the call) and, after `make lane-stop`, while
  the batch stays open (resumed at the next start, which calls `lane` again); a `stop` of the open batch written from here, the
  brief's example, would put a second writer of `l7r-lane/lane.jsonl` in the `task` crate beside the lane's own (T14 is building
  the batch run there) and still leave drop-then-adopt, whose adoption needs a worktree at the path that only a hand `git worktree
  add` (refused, 451 T285) would make. The re-make loses nothing: `lane` already throws away whatever the tree held (step 4's
  `reset --hard`, `clean -fdq`, detach), a resumed batch carries onto it from `origin/main` as every batch does, and the build
  cache lives beside the tree by its name (`builder_pool::cache`, `<cache root>/<tree name>`, read 2026-11-27), so D1's reason for
  never making the lane's tree - a new tree starts cold - does not hold for one made again at the same path: its cache is warm
  where it survived. T13's "refused, never made" stands for a lane tree never adopted; only the gone-from-disk case changes.
  Where git cannot make it there (something stands at the path), the refusal names that and the `git worktree add` that says what,
  and no longer the drop: the next batch start makes it once the path is clear. No lane-crate edit; the drop (T49) is unchanged.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY="builder_tree::tests::lane"` on the old code): 4 passed,
  1 failed - `a_lane_tree_gone_from_disk_is_made_again_at_its_path_and_its_cache_kept` answered `is gone from disk - make
  builder-tree-drop ...`, code 2. Green: the same run 5 of 5; `make builder-checks CRATE="rust/gate/crates/task"` clean, the crate 158 of 158. The test: a
  batch open, the tree removed with no prune, `lane` re-makes it at `origin/main` with the cache's `debug/` kept, the registry's
  lane line kept and a `remake` line logged; then a file at the path, refused naming what is in the way and not the drop. The old
  gone-from-disk assertion of T13's adoption test moved into it.

### T50 Approach (checklist part A)

1. **The goal, in the world.** A lane whose tree vanished mid-batch carries on at its next batch start, warm where the cache
   survived, with no hand step and no escape.
2. **The constraints.** D1 (the lane's tree, its cache kept, step 4's rule), T13 (`lane` at a batch's start), T49 (the drop refused
   while the runner lives or a batch is open), 451 T285 (no hand `git worktree add`), the brief: lane-crate edits narrow (none made).
3. **Where each comes from.** R: tasks.md T50's line, T49's found-and-left item; O: `lane_start`, `drop_tree`, `make_cold` and
   `builder_pool::cache`, read 2026-11-27.
4. **Do they describe the world here?** Yes: the red test shows the old `lane` refused a gone tree with the drop T49 refuses.
5. **The order.** After T13 and T49; before T22.
6. **The exits.** Green: the lane tests and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one gone-from-disk branch for the lane's tree (`lane_start`), read; the builders' own (`take`'s note
   naming the drop) is a free tree's, which the drop takes, and is left as it is.
8. **The budget.** One landing.
9. **Done, measured.** The lane test green; in use, a `rm -rf` of `<clone>-land` mid-batch is followed by a `remake` line in the
   pool's log at the next batch start and the batch's landing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session whose lane tree vanished is no longer sent round the drop's refusals; nothing else a reader sees
    changes.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T51 (T14's start through the lane tree's launcher could say "holds no lock" of a runner still building; filed at T14's build half)

- **Approach**: `rust/gate/crates/lane/src/runner.rs`: `start` runs `prebuild(exe)` before the spawn - where `exe` is the launcher
  (file name `l7r-gate.sh`, `LAUNCHER`, which `runner_exe` returns for the lane's tree), it is run once in the foreground as
  `L7R_GATE_PRINT_FRESH=1 <exe>`, with the spawn's environment (`run::STRIPPED` removed) and without `L7R_GATE_STALE_OK` or
  `L7R_GATE_NO_BUILD` (either would make it build nothing), and waited for whole; a non-zero exit returns code 1 with cargo's stderr
  and spawns nothing; any other `exe` (the caller's binary, `runner_exe`'s fallback) builds nothing. The spawned launcher then finds
  the binary fresh and `exec`s at once, so `START_WAIT_S` (unchanged, a GUESS knob) covers the spawn to the lock alone - its doc comment and
  `dev/audits/lane-runner.md` say so. `start`'s signature and both callers (`lane.rs`, `on_hand_in`) are unchanged; the tests are a
  module of their own (`runner/start_tests.rs`), away from T14's closing half's edits of `runner/tests.rs`.
- **Measured** (method for each figure below: a `git clone --shared` of the lane tree at its commit efc35ccc4f in the scratchpad, a
  copy of the lane tree's `tool/` build cache as `L7R_GATE_TARGET`, `/usr/bin/time` over `L7R_GATE_PRINT_FRESH=1
  scripts/gates/l7r-gate.sh`, under a load average of 27 to 46 on 22 cores, measured 2026-11-27 (uptime)):
  - at its own commit with every source's time new, as a tree made again by T50 is, a whole-workspace rebuild of 101.75 s, measured 2026-11-27 (the scratch timing), not the same-commit cost.
  - Again at once, 0.05 s, measured 2026-11-27 (the scratch timing): fresh, no build.
  - efc35cc to e343e50, a day's move of 401 files under `rust/`, 112.08 s, measured 2026-11-27 (the scratch timing).
  - Across single landed commits, 15.02 s to 6174b208b5 (12 files), measured 2026-11-27 (the scratch timing).
  - 2.25 s to 950b1ccd56 (10 files) and 2.24 s to e343e5021e (2 files), measured 2026-11-27 (the scratch timing).
  - A touched file with no change 1.09 s, measured 2026-11-27 (the scratch timing).
  - A comment added to the core crate 4.92 s, measured 2026-11-27 (the scratch timing).
  - So every move past the smallest outlasts `START_WAIT_S`.
- **Decision 1 - prebuild, not a wait on the spawned child.** The brief offered both. Waiting while the detached child lives would
  need a new ceiling knob and would hide a failed build: the child's standard streams are `/dev/null` (T12's measured reason), so
  the start could say only "it exited 1". The prebuild's stderr reaches the caller with the command that rebuilds it alone, and
  the wait is the build's own end. Its cost: a source moved between the prebuild and the spawn (a reset in that instant) reopens
  the `START_WAIT_S` window, which only the runner resets, and it resets after it holds the lock. Label: the algorithmically easier route,
  the record silent (tooling, no research question).
- **Decision 2 - the start's callers wait out the build in the foreground.** `make lane-start` and, from T22's base, a hand-in's
  `on_hand_in` now block for the rebuild (up to the 112 s measured 2026-11-27, the scratch timing) where before they returned at `START_WAIT_S` with a false failure; for
  `make builder-done` that sits near a builder's 2-minute tool timeout. Dormant until T22 (Decision 6 of T12). Not fixed here: a
  background start or a prebuild at the lane tree's reset is a design choice for the hand-in path, outside the start path this
  brief scopes. Filed as T54; lands before T22.
- Red first, measured 2026-11-27 (make rust-test): `runner::start_tests` against the old `start`, 0 passed, 2 failed - the stale launcher's start returned
  "lane: started `.../gates/l7r-gate.sh lane --work ...`, but it holds no lock after 0.3 s" (the bug's own words; measured 2026-11-27 (make rust-test), a 0.6 s fake
  build against a 0.3 s wait), and the failing build's start returned 0 (the runner came up regardless). After, measured 2026-11-27 (make rust-test): 2 of 2, the lane
  crate 38 of 38, and `make builder-checks CRATE="rust/gate/crates/lane"` clean (test, lint, format).

### T51 Approach (checklist part A)

1. **The goal, in the world.** `make lane-start` (and a hand-in's start) says "started" of a runner that comes up after the lane
   tree's rebuild, and says why when that build fails, never "holds no lock" of a healthy runner.
2. **The constraints.** T12's start (the lock the truth, the runner detached with `/dev/null` streams, `START_WAIT_S`), T14's
   runner program (the lane tree's `scripts/gates/l7r-gate.sh`, `run::STRIPPED`), the launcher's `L7R_GATE_PRINT_FRESH`, the
   crate's own-tests coverage (rust/gate/CLAUDE.md), the brief's scope (the start path in runner.rs).
3. **Where each comes from.** R: plan.md T12 and T14, tasks.md T51, `scripts/gates/l7r-gate.sh`. O: the rebuild timings above
   (2026-11-27).
4. **Do they describe the world here?** Yes: the timings ran the lane tree's own commit and build cache through the real launcher;
   the tests drive `start` through `setsid` with a launcher stand-in that builds and takes the lock as the runner does.
5. **The order.** After T14's build half (the launcher as the runner's program); before T22 (the base flipped, which makes every
   hand-in start the runner); beside T14's closing half, whose edits are in `runner/tests.rs` and `run.rs`.
6. **The exits.** Green: the tests above and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one branch before the spawn.
8. **The budget.** One landing.
9. **Done, measured.** `runner::start_tests` 2 of 2 after 0 of 2 on the old code, the lane crate 38 of 38, measured 2026-11-27 (make rust-test).
10. **Before moving a constant.** n/a: `START_WAIT_S` keeps its value (a GUESS), its doc saying what it now covers.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a lane start that reported a false failure (and a hand-in's start line saying so) now
    reports the runner it started, or the build's error.

**Found and left?**

- A hand-in's start (`on_hand_in`) now waits in `make builder-done`'s foreground for the lane tree's rebuild, up to the 112 s
  measured 2026-11-27 (the scratch timing), near a builder's 2-minute tool timeout (Decision 2). Not fixed here: the hand-in path's design (a background start, or
  a prebuild at the lane tree's reset) is outside this start-path fix and dormant until T22. Filed as T54; lands before T22.

**Performance work?** no
<!-- plan-archive: archived 2026-11-28 -->
### T52 (T14's build half, its decision 1: `make land`'s carry of the done refs read live carried a later hand-in into a lane batch)

- **Approach**: `carry_done` (`rust/gate/crates/land/src/land/carry_done.rs`) still reads the done refs live
  (`builder_done::to_carry`), but under `L7R_LANE_BATCH` (read through the landing's `Rooted`, so a test's own environment) it keeps
  only the commits whose sha starts with a change the batch's `batch` line in `l7r-lane/lane.jsonl` (the git common directory)
  names - the lane writes full shas, a short one matches too - and says the rest on one line, `land: lane batch <b>: left <n> done
  commit(s) its batch line does not name, for a later batch (461 T52, D14): <shas>`, their refs kept for the lane's next batch. The
  line is the LAST `batch` line naming the batch (a later `batch` line of the same id a new batch, as T49's reading and the lane's
  `log::batches` take it); a torn line is skipped, as the lane skips it. A `landed` line of the batch after it ends it: a by-hand
  `make land` with a done batch's id exported carries as before, never leaving its tasks' commits uncarried (round 2, the
  advisor's probe of "a landing outside the lane is unchanged"); a `stop` naming the batch ends nothing, since the lane resumes it
  - so T17's `"landed" | "stop"` rule is not copied, which would reopen the unbounded window on a resumed batch. Read in the land crate, not through the lane crate (which
  builds on `task`), as `tree`'s `state::batch_open` (461 T17) reads it - a fourth small reader of the log, kept private rather than
  making T17's helper public, which answers another question (open or not) and would put a second crate in this task. Of the
  brief's two fixes ("carries nothing" or "only the batch line's shas") the second: it holds D14 whether or not the lane carried
  first, and leaves `make land`'s carry the one that verifies a batch's commit is in HEAD. A batch no line names, or one a `landed` line
  ended (the variable exported by hand, no log), is no lane batch and carries as before; a landing outside the lane is unchanged (the variable unset,
  `batch_named` None before any read).
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/land ONLY="land::carry_done::tests"` on the old code): 5 passed,
  1 failed - `a_lane_batch_carries_only_the_commits_its_batch_line_names` carried both T1's named commit and T2's unnamed one
  (`notes/later.txt` in HEAD). Green: `land::carry_done::tests` 6 of 6; `make builder-checks CRATE="rust/gate/crates/land"` clean, the crate 221 of 221. The tests cover a short named sha carried beside an
  unnamed one left (its ref kept, the line said), a log holding another batch's line and a torn line, a batch whose every waiting
  commit is named (nothing said), and a batch no line names (both carried, nothing said). Round 2 (2026-11-27, the same
  command with the `landed` arm made a no-op): 5 passed, 1 failed - `a_batch_no_line_names_carries_as_before`'s landed batch
  carried only the named commit; after, 6 of 6, the batch line followed by a `stop` of it still filtering.

### T52 Approach (checklist part A)

1. **The goal, in the world.** A lane batch's landing lands exactly the hand-ins its `batch` line named; a task's later hand-in
   waits for the next batch with its done ref, whatever window a resumed batch spans.
2. **The constraints.** D14 (a batch takes its changes' shas when it forms; a later hand-in changes no open batch), D5 (the
   batch's changes), data-model.md's batch and log line, T17's rule (the log read in the land crate without the lane crate), the
   brief: a landing outside the lane unchanged; the land crate only (T14's closing half works in the lane crate).
3. **Where each comes from.** R: tasks.md T52's line, data-model.md ("A batch takes its changes' shas when it forms"), T14's
   build-half handoff decision 1; O: `carry_done` and `to_carry` read 2026-11-27, the red test.
4. **Do they describe the world here?** Yes: the red test shows the old landing carrying an unnamed done commit under the
   variable.
5. **The order.** After T14's build half; before T22 (as the task's line says).
6. **The exits.** Green: the carry_done tests and `make builder-checks CRATE="rust/gate/crates/land"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `carry_done` is `to_carry`'s one caller in the land crate; the lane's `runner/run.rs` sets
   `L7R_LANE_BATCH` and writes the `batch` line before `make land`, read 2026-11-27.
8. **The budget.** One landing.
9. **Done, measured.** The red test green; in use, the lane's first real batch (T23) with a later hand-in of a batched task left
   waiting, its `left` line in the attempt file.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A later hand-in landed under a batch that never named it, against D14: its gate run and NOTE are the
    batch's, and the lane's ref deletion keeps its ref, so the lane would carry it again as an empty pick in the next batch.

**Found and left?** none.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-28 -->
### T53 (found by 461 T14's build half: `make lane` misstates an open batch's change as superseded)

- **Approach**: `rust/gate/crates/lane/src/log.rs`, `log::state`: `in batch <b>` - an open batch's `batch` line names the sha and
  no `eject` is the last log line naming it - is asked right after `landed` and before `superseded`; `superseded`, `ejected` and
  `waiting` follow in their old order. The batch's commit is the one the lane lands (T52 carries only what the batch line names,
  D14), so the batch's own change reads `in batch`, and the later hand-in of its task stays `waiting` (data-model.md's prose: "That
  later hand-in is `waiting` until the batch ends"). An ejected change of an open batch, or a stopped batch's, is not in the batch,
  so with a later hand-in it reads `superseded` as before (the data model's "superseding it if the batch ejected it"). Moving
  `in batch` ahead of `superseded` departs from data-model.md's numbered list, which its own paragraph on a batch contradicts: a
  deliberate deviation, labeled in the module doc. Callers: `make lane`'s listing (`lane.rs`, which now shows the batch's change)
  and `batch::form`'s `waiting` filter (unchanged: an in-batch or superseded hand-in was never batched).
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/lane ONLY="log::tests"` on the old code): 7 passed, 1 failed -
  `an_open_batch_s_change_is_in_batch_though_a_later_hand_in_of_its_task_exists`, `Superseded` against `InBatch("461-4")`. Green:
  `make builder-checks CRATE="rust/gate/crates/lane"` clean, the crate 50 of 50; the test also pins the later hand-in `waiting`,
  and the earlier `superseded` once its batch ejects it or stops.
- **Test only, the coordinator's addition**: the session's pre-gate coverage named `runner.rs`'s `on_lane(common)` (its
  `.map(|h| h.commit)`, line 504) reached by no test; a new module `runner/on_lane_tests.rs` writes a pool log `handed_in` line
  and a done ref in a scratch git common directory and asserts `on_lane` returns that commit, and not a hand-in no ref or lane
  line names (2026-11-27, `make rust-test CRATE=rust/gate/crates/lane ONLY=runner::on_lane_tests`: 1 of 1). Not red first: no
  code changed, a coverage gap.

### T53 Approach (checklist part A)

1. **The goal, in the world.** `make lane` shows the change an open batch is landing as `in batch <b>`, and a later hand-in of
   its task as `waiting`, so the coordinator reads what the batch carries.
2. **The constraints.** D8 (states computed), D14 (a batch takes its shas when it forms; a later hand-in moves no open batch),
   data-model.md ("A hand-in"'s order, "A batch"'s paragraph on the later hand-in), T11's order, T52's carry; the brief: log.rs
   and its tests only (T15 edits runner/run.rs elsewhere).
3. **Where each comes from.** R: tasks.md T53's line, data-model.md, plan sections T11 and T52; O: the red test.
4. **Do they describe the world here?** Yes: the red test reproduces the misstatement on the old code; `log::state`'s callers
   read 2026-11-27 (`lane.rs`, `batch.rs`), none relying on a batch's change reading `superseded`.
5. **The order.** After T11, T14's build half and T52; before T20.
6. **The exits.** Green: the log tests and `make builder-checks CRATE="rust/gate/crates/lane"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `log::state` and its callers in `lane.rs` and `batch.rs`, read 2026-11-27 (`grep -n log::state`).
8. **The budget.** One landing.
9. **Done, measured.** The red test green; in use, `make lane` over the first lane batch with a later hand-in of a batched task.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The coordinator reading `make lane` sees the batch's change as superseded and no change `in batch`,
    against what the batch lands (D8's states misstated).

**Found and left?** none.

**Performance work?** no.

<!-- plan-archive: archived 2026-11-28 -->
### T54 (T51's Decision 2: a hand-in's runner start waits in `make builder-done`'s foreground for the lane tree's rebuild; filed at T51)

- **Approach**: `rust/gate/crates/lane/src/runner/run.rs`: `run_batch`, right after `builder-tree lane` brings the lane's tree to
  `origin/main` and before the changes to carry are read, runs T51's `prebuild` on the tree's own `scripts/gates/l7r-gate.sh` where
  that file exists (the run tests' worlds have none), its result ignored. The hand-in path (`on_hand_in`, `start`) is unchanged.
- **When a start can find the lane tree stale** (read from the code, 2026-11-27): the launcher's staleness is `find -newer` over the
  sources (`scripts/gates/l7r-gate.sh`'s `stale`). Two writers move the lane tree's sources. The runner's `run_batch` resets it, then
  carries (`make carry`, whose launcher builds) and lands (`make land`, whose `LAND_RUN` builds again after the carries).
  `scripts/land-alone.sh`'s reset step resets the same tree (`<clone>-land`), and its landing step runs `make land` there, which builds. So after
  either writer the binary is fresh, and the 2.2-112 s T51 measured (measured 2026-11-27, T51's scratch timing) reaches a start only
  where a reset was followed by no `make`:
  1. a batch whose every change `origin/main` already holds (`todo` empty: a resumed batch whose push went out, the Recovery case),
     T50's re-made tree included - the whole move since the last build, up to the 112 s of a day's move and 102 s for a re-made tree, measured
     2026-11-27 (T51's scratch timing). CLOSED HERE.
  2. a runner killed between the reset and the build - the rest of that build. Accepted (below).
  3. a stopped carry - the carried files' rebuild, up to the 15.02 s T51 measured for a 12-file commit (measured 2026-11-27, T51's scratch timing), but where the conflict is in
     a file the gate builds from, a failed build and no runner at all (Found and left, T55).
- **Decision 1 - the build at the reset (route B), not a background start (route A).** Priced 2026-11-27, by reading:
  - Route A, the prebuild inside a detached child of the hand-in. It needs a new detached path in `start` and its tests. Its
    failure must reach the coordinator as an `owed` line (data-model.md's event; T20's `make lane-wait` prints only `owed` lines).
    The hand-in would lose its `started (pid N)` line, and T51 Decision 1's reason (a build failure the caller sees) would come back
    as a deferred line. It covers cases 1-3's waits, but not case 3's failure.
  - Route B: a call after the reset, in the lane crate. In the common batch (a carry follows) it adds no build: it makes, earlier, the
    build `make carry`'s launcher would make, and the carry's moved files are rebuilt by `make land` as before. It closes case 1,
    the only unbounded case on a live runner. Cases 2 and 3 are left.
  - Chosen: B, the cheaper. It is sound for the hand-in's wait: the residual waits are bounded by one carry's files or one killed
    build. No log line is written, so nothing is added to data-model.md's events.
  - Label: the algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - a failed build at the reset stops no batch.** Where a carry follows, `make carry`'s own launcher fails on the same
  build and the carry's error (the `carry` line, the runner's `error:`) says so, as before. Where none follows, the next start's
  prebuild (T51) says why to its caller. Making it an error here would add a third route to the same report.
- **Accepted limitation (case 2)**: a runner killed between the reset and its build leaves the next start the rest of that build in
  the foreground, up to the 112 s above under the same load (measured 2026-11-27, T51's scratch timing). Its cost: one hand-in's wait, near the 2-minute tool timeout, after a
  `make lane-stop NOW=1` or a crash in that instant. Alternatives priced: route A covers it at the cost above. Chosen by: this
  builder, under T54's brief, which asks for the cheaper sound route.
- Red first, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests"`): the new test
  `a_reset_with_nothing_to_carry_leaves_the_lane_tree_s_launcher_built_so_the_next_start_builds_nothing` against the old
  `run_batch`, 7 passed, 1 failed (`left: None`, `right: Some("built <origin sha>")`: no build after the reset). After, measured
  2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`): the lane crate 40 of 40, lint and format clean. The test commits
  a stand-in launcher (it builds where the tree's HEAD moved since its last build, its marks in the git common directory, out of
  the reset's `clean`) and moves `origin/main` past a landed batch. It then resumes a batch `origin/main` already holds: one build
  at the new HEAD, and T51's `prebuild` after it builds nothing. Then, with the build failing, a further batch still lands.

### T54 Approach (checklist part A)

1. **The goal, in the world.** A hand-in's runner start from T22's base finds the lane tree's `l7r-gate` built, so `make
   builder-done` does not wait out a rebuild near a builder's tool timeout.
2. **The constraints.** T51's start (its prebuild and its error words), T12's start and lock, T14's batch run (`run_batch`, steps
   1-4), T50's re-made tree, data-model.md's events (none added), the crate's own-tests coverage (rust/gate/CLAUDE.md).
3. **Where each comes from.** R: plan.md T51, T12, T14; tasks.md T54; `scripts/gates/l7r-gate.sh` (`stale`), `scripts/land-alone.sh`
   (its reset and landing steps). O: T51's rebuild timings (2026-11-27).
4. **Do they describe the world here?** The staleness cases are read from the code above. The timings are T51's, on the lane
   tree's own commit and build cache. The test drives `step` and `resume` against a real bare `origin` and the pool's lane tree.
5. **The order.** After T51 and T14; before T22, which makes every hand-in start the runner.
6. **The exits.** Green: the new test, and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one call after the reset.
8. **The budget.** One landing.
9. **Done, measured.** The new test red then green, the lane crate 40 of 40, measured 2026-11-27 (make rust-test, make builder-checks).
10. **Before moving a constant.** n/a: `START_WAIT_S` is unchanged.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. A hand-in after a batch that carried nothing now starts its runner at once, where it waited
    out the whole move since the last build.

**Found and left?**

- A stopped carry leaves its cherry-pick in progress in the lane's tree (`rust/gate/crates/land/src/land/carry.rs`: "the stop leaves
  the pick in progress"). Where the conflict is in a file the gate builds from, the next start's prebuild (T51) fails on the
  conflict markers and starts no runner. Only the runner's resume resets that tree, so from T22's base every hand-in says "could
  not be built" and the open batch is never resumed. Found by reading, not run. Not fixed here: it is the start's handling of an
  open batch's tree, outside the build-at-reset this brief prices, and route B does not reach it. Filed as T55; lands before T22.

**Performance work?** no - it removes a foreground wait that does not yet happen (dormant until T22's base), and it times nothing.


<!-- plan-archive: archived 2026-11-28 -->
### T55 (T54's Found and left: a stopped carry's conflict in the lane's tree fails every later start's build, and only the runner's resume resets that tree; filed at T54)

- **Approach**: `rust/gate/crates/lane/src/runner.rs`: `start`, after its lock check (no runner lives) and before T51's `prebuild`,
  asks `stopped_carry`: the registry's lane tree has `CHERRY_PICK_HEAD` (`git -C <tree> rev-parse -q --verify`, which a linked
  tree answers for itself) AND the lane's log's last batch is open with its last `carry` line's code not 0. Where both hold,
  `reset_stopped` makes the resume's own call, `builder-tree lane` (`l7r_gate_task::builder_tree::cli`, as `run_batch` calls it),
  which fetches and brings the tree to `origin/main` (`reset --hard`, `clean -fdq`, `checkout --detach`), and says so in a stdout line
  before the start's own. A reset that fails is the reply's stderr and the start goes on, so the build's own words follow it. The
  rest of `start` moves unchanged into `start_built`. `start`'s signature and its callers (`lane.rs`, `on_hand_in`) are unchanged;
  `run.rs` is not touched (T15's).
- **Decision 1 - the reset first, not the prebuild skipped.** Read 2026-11-27 in `scripts/gates/l7r-gate.sh`: the launcher builds
  where stale in both modes (the `elif stale` branch runs whether or not `L7R_GATE_PRINT_FRESH` is set), and it never falls back to
  the binary it has. So a skipped prebuild only moves the failed build into the detached child, whose streams are `/dev/null`, and the
  start says "holds no lock". Spawning with `L7R_GATE_STALE_OK` instead would leave that variable in the runner's environment, and
  through it in every `make carry` and `make land` the runner runs. `run::STRIPPED` (run.rs, T15's file) does not remove it. The
  reset is what the resume does at once anyway (`run_batch`'s first step), so it removes nothing the runner needs. Label: the
  algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - both halves of the condition.** `state_of` reads any `carry` line as gating, so the code is asked of the line. The
  log half matters because `scripts/land-alone.sh` shares the lane's tree: a pick in progress there with no stopped carry open is
  not the lane's to discard, and is left alone (pinned by a test).
- **After the reset** the runner starts, resumes the batch and carries again. A conflict with `origin/main` still there stops the
  carry again, and the runner stops with the batch open as before. That repeat is T25's (phase 3: a carry conflict becomes a repair
  entry), not a deadlock: each start makes one more attempt and says why it stopped.
- Red first, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::start_tests"`), the three new tests
  against the old `start`: 3 passed, 2 failed. The stopped carry's start returned the deadlock's own words, "lane: the runner's
  program could not be built (exit 1), so no runner started ... error: this file contains an unclosed delimiter". The failing reset
  said nothing of the reset. The test world is a real one: a bare `origin`, a clone, and the lane's tree in the pool's registry with
  a hand-in's `rust/x.rs` cherry-picked onto a moved `origin/main` and stopped in conflict. The lane's log holds `batch`, `carry` (code
  2) and the runner's `stop`. A stand-in launcher fails on conflict markers under `rust/` in both modes, as cargo would. After,
  measured 2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`): the lane crate 43 of 43 (40 before), lint and format
  clean.

### T55 Approach (checklist part A)

1. **The goal, in the world.** After a batch's carry stops in a file the gate builds from, the next `make lane-start` (or, from
   T22's base, a hand-in's start) starts a runner that resumes the open batch, where every start had failed to build.
2. **The constraints.** T51's start (its lock check first, its prebuild and its words), T54's build at the reset, T14's batch run and
   Recovery (the resume brings the tree to `origin/main`), T13's `builder-tree lane`, `land`'s carry ("the stop leaves the pick in
   progress"), `land-alone.sh`'s shared use of the tree, the crate's own-tests coverage (rust/gate/CLAUDE.md), the brief's scope (the
   start path in runner.rs; T15 edits run.rs).
3. **Where each comes from.** R: plan.md T51, T54, T14, T13; tasks.md T55; `scripts/gates/l7r-gate.sh` (`stale`, both modes),
   `rust/gate/crates/land/src/land/carry.rs`, `rust/gate/crates/task/src/builder_tree.rs` (`lane_start`). O: the red and green runs
   above (2026-11-27).
4. **Do they describe the world here?** Yes: the tests drive `start` through `runner_exe` and `setsid` against a real conflicted
   cherry-pick in a registered lane tree, a bare origin, and the real `builder-tree lane`.
5. **The order.** After T51 and T54; before T22, which makes every hand-in start the runner; beside T15 (run.rs, untouched here).
6. **The exits.** Green: the three new tests and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one check and one call before the build.
8. **The budget.** One landing.
9. **Done, measured.** `runner::start_tests`: 3 of 5 on the old code, 5 of 5 after; the lane crate 43 of 43, measured 2026-11-27 (make rust-test, make builder-checks).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. A start after a stopped carry now resets the lane's tree and starts the runner, where it
    failed on the conflict markers and no batch was ever resumed.

**Found and left?** none - the resumed batch stopping again on the same conflict is T25's planned work (phase 3), not a defect left here.

**Performance work?** no
<!-- plan-archive: archived 2026-11-28 -->
### T58 (T51's stale-launcher start test red 2 of 30 under load, "holds no lock after 0.3 s", measured 2026-11-27 (T15's build half, 3x10 at once), filed there)

- **Approach**: the defect is the TEST's own bound, not the runner's start; `rust/gate/crates/lane/src/runner/start_tests.rs` alone
  changes, `runner.rs` not at all. The tests' starts take `WAIT_S` (3.0 s, a GUESS knob of the test module with its measured why) in
  place of 0.3 s and the stopped-carry tests' 2.0 s (each a GUESS of T51's and T55's), and the fake launcher's build is 3.5 s, so the build still outlasts the start's
  wait, as the lane tree's rebuild outlasts `START_WAIT_S`, and in its runner mode it sleeps 0.5 s before the lock, a loaded
  machine's slow spawn pinned. A lock seen ends the wait at once, so the longer bound costs a green run nothing; the build costs
  the one test 3.5 s, measured 2026-11-27 (make rust-test).
- **Measured** (method for each figure: the lane test binary run whole-crate, ten at once, under `uptime`'s load on 22 cores, the
  start's wait timed by a scratch `eprintln!` in `start_built`, removed after, 2026-11-27):
  - Before, 0 red of 30 at load 15-47, then 2 red of 60 at load 31-86, measured 2026-11-27 (the lane binary 6x10): this test 1 ("holds no lock after 0.3 s", 0.623 s with no lock) and one other, below.
  - Spawn to lock over the 419 starts that came up: median 0.066 s, 99th percentile 0.471 s, longest 0.749 s, measured 2026-11-27 (the timed wait), and at `START_WAIT_S` (5.0 s) not one of 300 real starts failed, measured 2026-11-27 (the timed wait).
  - The runner's own take against the probe (a scratch test: `work_cli` run 20 times beside a thread calling `held()` every 20 ms, the binary 3x10 at once, load 17-35): 0 quiet leaves of 600 takes, measured 2026-11-27 (the scratch race test, removed after), so `TAKE_S` (1.0 s) is not lost to `free()`'s brief lock.
- **Decision 1 - fix the test, not the start; no wait read against the child's state.** The task line offered the child's state.
  The measurements above show no production start failing: `START_WAIT_S` holds 6.7 times the longest spawn to lock at load 86,
  and the runner's take never lost to the probe. A wait on the child would add a ceiling knob and was priced and declined by T51
  (Decision 1) for hiding a failed build; with no wrong outcome in the start (constitution XIV) the test's bound is the defect.
  Label: the algorithmically easier route, the record silent (tooling, no research question).
- Red first, measured 2026-11-27 (make rust-test): the fake's spawn slowed 0.5 s against the old 0.3 s bound, 10 of 10 red, "holds
  no lock after 0.3 s". After, measured 2026-11-27 (make rust-test): `runner::start_tests` 5 of 5; the start without its prebuild
  still red ("holds no lock after 3 s", measured 2026-11-27 (make rust-test)), so the test still tells T51's fix, and the lane binary 6x10 at once at load 19-61, 0 red of 60, measured 2026-11-27 (the lane binary 6x10).

### T58 Approach (checklist part A)

1. **The goal, in the world.** The lane crate's start tests are green at load, and stay red against a start that skips its build.
2. **The constraints.** T51's start (the prebuild, `START_WAIT_S`), T14's lock probe (`free`, `TAKE_S`), the brief's scope
   (runner.rs's start path and start_tests.rs; T15's closing half edits `runner/run.rs`), the crate's own-tests coverage.
3. **Where each comes from.** R: tasks.md T58, plan.md T51 and T14. O: the load runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the runs used the crate's own test binary, whole, ten at once on the shared machine
   at the loads named.
5. **The order.** After T51 and T55 (their tests); before T23.
6. **The exits.** Green: the 6x10 run at load clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one constant and the fake's timings.
8. **The budget.** One landing.
9. **Done, measured.** 10 of 10 red before, 0 of 60 red after at load, measured 2026-11-27 (the lane binary 6x10).
10. **Before moving a constant.** `START_WAIT_S` unmoved; the tests' 0.3 s and 2.0 s were no claim's, now `WAIT_S` (a GUESS with its measured margin).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a red batch gate's false red from this test is gone; the start itself behaves as before.

**Found and left?**

- A start or a stop can name a dead runner's pid: `holder` reads the lock file while it is held, and a new runner holds the lock before `work_cli`'s `set_len(0)` and pid write, so the file still names the last killed runner; `runner::tests::a_runner_deaf_to_term_...` red 1 of 60 (pid 884049, the killed runner, against 887300), and a stop would signal that dead pid's group. Not fixed here: the race is in `work_cli` and `holder` and its test in `runner/tests.rs`, outside this brief's start path, and T15's closing half edits beside it. Filed as T62; lands before T23.

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T59 (phase 1: the likeness test counts the lane's tree as a builder's; found by T10's measurement)

- **Approach**: in pool tree `diagram-backlog-t271`, bundled with T60.
  - **Measured** (observed 2026-11-27, method: `night-figures.py`'s `concurrency` and `load_figures` over 19:57:00Z-23:03:20Z, the pool
    log from T10's kept extract and the live samples, a probe script in the scratchpad): trees held 3.55, the sampler's held mean 3.18 over
    1,065 samples, on the old script - the pool log's `adopt` of `/diagram/.clones/diagram-backlog-land` with detail `lane` (21:08:09Z, never
    released) replayed as a hold, and `len(held)` counting `lane`.
  - **The script** (`dev/measurements/2026-11-27/461-t01-night-tokens/night-figures.py`): `LANE = 'lane'`, the guard's
    `shared::builder_pool::LANE`; `held_spans` treats an `adopt` of `lane` as no hold and as the end of one (a tree adopted for the lane
    is no builder's from then), unless `lane=True` asks for it; `concurrency` passes that through; `sample_rows` counts `held` without
    `lane`. `phase1.py` (T10's) drops its own `-land` suffix filter and asks `concurrency(..., lane=True)` for its "with it" figure, so
    T10's outputs re-derive. After: trees held 2.94, the sampler's mean 2.98 (same method); T10's two kept figures runs, `phase1.py figures`
    over 19:57Z and 21:06:47Z with `--kept`, byte for byte their recorded outputs; T02's night, `figures` 04:30Z-14:29Z with `--kept`, its
    output and `ref-0430-1429.json` unchanged (no lane then); `like` over 19:57Z-23:03:20Z reads trees held 2.94 (observed 2026-11-27,
    method: those commands, diffed against the recorded files).
  - **The sampler** (`rust/gate/crates/measure/src/measure/sampler.rs`'s `sample`): already reads `shared::builder_pool::read`, which
    leaves the lane out since T13 (landed 20:52Z). The 215 samples naming `lane` (21:08:12Z to 21:43:55Z) came from pid 3387947, started
    09:44:04Z, before T13, which ran until its `L7R_SAMPLE_MAX_H` ended at 21:44:05Z; the sampler started 21:52:53Z lists no `lane`
    (observed 2026-11-27, method: `sampler.log` and each sample's `held` in `mem-samples.jsonl`). So no code change: the sampler test's
    fixture now holds a lane tree, and `a_sample_reads_the_cgroup_and_proc_and_leaves_out_what_its_file_does_not_give` pins `held`
    without it. Not red first: the code it pins was right from T13; the red is the script's, above.
  - **Decision: the lane told by its holder, not its path.** `lane` is the registry's reserved word (T13) and the pool log's adopt detail;
    the `-land` suffix is a naming habit. Label: the algorithmically easier route, one word shared with the guard.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement script and a test fixture | - | - | - | - |

### T59 Approach (checklist part A)

1. **The goal, in the world.** The likeness test's trees held, and its sampler cross-check, count builders' trees only, so T31's like window
   is judged against the night's 3.19 on the same footing.
2. **The constraints.** Plan D12 (the likeness test), FR-010 (every figure beside its concurrency), T13 (the lane's reserved holder), T10's
   record kept re-derivable.
3. **Where each comes from.** R: plan D12, T13's section; O: the runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the live pool log, the live samples and T10's kept extracts.
5. **The order.** After T10; before T31, which reads the like window.
6. **The exits.** Green: 2.94 and 2.98 from the script, T10's outputs re-derived. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The sampler's half was a stale process, not code: named above and filed.
8. **The budget.** One landing.
9. **Done, measured.** The probe's figures 2.94 and 2.98; `make builder-checks CRATE="rust/gate/crates/measure"` green (observed 2026-11-27,
   method: those commands).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T31's like window would read about 0.6 tree high against the night's 3.19, its band 0.5 (GUESS, plan D12),
   enough to pass or fail a window wrongly (observed 2026-11-27, method: the probe above): fixed here.

**Found and left?**
- The memory sampler runs the code it started with for its whole `L7R_SAMPLE_MAX_H` (12 h), so a change to what it reads reaches its
  samples only at its next start: 215 samples listed `lane` after T13 had left it out (observed 2026-11-27, method: `sampler.log` against
  T13's landing). Not fixed here: a restart-on-rebuild is a mechanism of its own, past this fix's size. Filed as T61; lands before T31.

**Performance work?** yes - a measurement script of where the builders' concurrency goes (451 FR-013: a measurement task counts).


<!-- plan-archive: archived 2026-11-28 -->
### T60 (phase 1: a build half's hand-in refused for the feature-close ask; found by T10's measurement)

- **Approach**: in pool tree `diagram-backlog-t271`, bundled with T59.
  - **What refused, measured** (observed 2026-11-27, method: T10's record, `dev/measurements/2026-11-27/461-t10-phase1/output-1957-2303.txt`,
    the call's own tool result): 451 T537's build half at 22:06:03Z, "this tick would close the feature, and: 451 has no report.md ... review
    passes with no ledger row" - the closing check `tick::checks`' `close_owed` joins to the last task's refusal where the tasks asked are the
    feature's last open boxes (451 T307 part 2). Its closing half answered both and handed in on the same tree at 22:44:14Z.
  - **The change** (`rust/gate/crates/task/src/tick/refusal.rs`, `Section`; `tick.rs`, `checks`; `land/hand_in.rs`, `section_of`): T44's
    `Later` splits in two - `Closing`, a build half's hand-in, puts off the section's two asks and the close (`close_owed` not asked);
    `Later`, a measurement's, puts off the section's two asks alone, its close still asked. A fix's or a closing half's hand-in
    (`Owed`), `make tick`, `l7r-gate tick --land-check` and the landing (`Pass::Landing`, always `Owed`) ask everything. The first
    pass's own ledger-row row (`land/cheap.rs`, a pass with no row) is not the close's and stands at every kind.
  - **Decision: the close put off for a build half alone, not for a measurement.** The close's reasons (a report, the close's ledger
    rows, the implementation check) are the closing half's work, and a closing half always follows a build half; nothing follows a
    measurement, so its builder answers its feature's close at hand-in, as before (the plan review's round 1, BLOCKED on the
    measurement limb, SC-002: a hand-in submitted once it is ready to land). This narrows the task line's "a build half and a
    measurement" to the half the reason covers. Label: the algorithmically easier route that cannot loosen the landing.
  - **The docs**: `refusal.rs`'s `Section` doc, `checks`' doc, `hand_in.rs`'s step 6 and `section_of`, and `scripts/container/builder-brief.md`'s
    THE BUILDER HANDS IN ITSELF (the close put off with the two asks, the landing asking all three).
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/task ONLY="tick::tests"` and `CRATE=rust/gate/crates/land
    ONLY="land::hand_in::tests"` with the new assertions on the old code): task 13 passed, 1 failed
    (`the_last_tick_closes_only_past_the_closing_check_and_the_archive_is_recorded`, its new `Section::Later` assertion); land 27 passed, 1
    failed (`a_build_half_of_the_feature_s_last_task_hands_in_with_its_close_still_to_come`, at the hand-in: the landing's half of it, the
    close still asked of `Pass::Landing`, passed on the old code, as it must, and so do the fix's and the measurement's hand-ins still
    refused, added after round 1). After: `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"`: task 160 passed,
    land 223, lint and format clean (`rust/gate/crates/measure` 307 for T59).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in's close put off | n/a - no map | n/a | none | n/a |

### T60 Approach (checklist part A)

1. **The goal, in the world.** A build half hands its own work in when its task is the feature's last open box; the closing half, a
   measurement's own hand-in and the landing still owe the close.
2. **The constraints.** US2 (a refusal a builder can answer is answered by the builder that has the context), T44's mode and its rule that the
   landing asks everything, FR-002 (no coverage at hand-in).
3. **Where each comes from.** R: US2 (spec.md), T44's section; O: T10's record (2026-11-27).
4. **Do they describe the world here?** Yes: the refusal is the real call's, and the tests run the real first pass through the hand-in.
5. **The order.** After T44 and T10; before T31.
6. **The exits.** Green: the task and land crates' tests and `make builder-checks`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"` green (observed 2026-11-27, method:
   that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A build half of a feature's last task refused at hand-in for work only its closing half does, 38 minutes and a second
   builder's run (451 T537, observed 2026-11-27, method: T10's record): fixed here.

**Found and left?** none.

**Performance work?** yes - it makes the builders' loop faster (451 FR-013): a build half of a feature's last task hands in without
waiting on its closing half.


<!-- plan-archive: archived 2026-11-28 -->
### T61 (the memory sampler runs the code it started with for its whole `L7R_SAMPLE_MAX_H`; found by T59)

- **Approach**: in pool tree `diagram-backlog-t271`. The sampler (`rust/gate/crates/measure/src/measure/sampler.rs`) re-runs itself
  when a build replaces its binary.
  - **Measured** (observed 2026-11-27, method: `sampler.log` and `mem-samples.jsonl` of the clone `diagram-backlog`, T59's section):
    pid 3387947 started 09:44:04Z, before T13 landed (20:52Z), and listed `lane` as held in 215 samples, 21:08:12Z to 21:43:55Z,
    until its hours ended at 21:44:05Z. The sampler running now, pid 3445329 (started 21:52:53Z), already runs a replaced binary:
    its `/proc/<pid>/exe` reads `.../tool/l7r-gate (deleted)` (observed 2026-11-27, method: `ls -la` of that link) - cargo writes a
    new file at the path, so the running inode is unlinked, not overwritten.
  - **D1. Re-exec, not a binary id a sample. Label: design decision.** Before each sample `rebuilt` compares the device and inode
    of `<proc>/self/exe` (the kernel's link, followed to the running file even once unlinked) with the path the sampler was
    started from (`Env::exe`, `current_exe` at its start); where they differ it `exec`s the path as `measure sampler run --common
    <dir> --first <its first start>`. Why not an id in each sample for the readers to drop stale ones: that leaves a hole in the
    window (21:08:12Z to 21:43:55Z above, inside T31's like window, observed 2026-11-27, method: that sampler's log) and puts a filter in every reader (`sampler-report`,
    `night-figures.py`, `slot-coincide.py`). Two `stat`s a sample, no stored state, and no race where the binary is replaced twice
    around a re-run: the cheap stand-in for the brief's "content id".
  - **D2. The re-run is the same process. Label: design decision.** `exec` keeps the pid and its start time, so the pid file is
    left as it is and still names the sampler - no concurrent `start` sees none and starts a second; the hours count from
    `--first`, so a sampler re-run at every landing still ends at its `L7R_SAMPLE_MAX_H`; `sampler.log` says `pid N runs its
    rebuilt binary` with its interval and its first start, pinned by the test below.
  - **D3. A re-run that fails samples on. Label: design decision.** The check can fire while cargo is still writing (the path
    missing, or `ETXTBSY`): a path not there is no rebuild, and an `exec` that returns is ignored - the sample is taken in the old
    code and the re-run asked again at the next sample; no log line a failed try. Ending there would stop sampling silently until
    the next handout, worse than the defect.
  - **The claim, exactly**: a sample reads with the BUILT binary at the sampler's path within one interval - not with the source:
    `scripts/gates/l7r-gate.sh` builds only at its next call after a landing. Recorded in the module note and
    `dev/audits/memory-sampler.md` ("A rebuilt binary is run again").
  - **Red first** (observed 2026-11-27, method: the new `Env` fields `exe`, `first`, `exec` landed inert, then the tests, `make
    rust-test CRATE=rust/gate/crates/measure ONLY="measure::sampler"`, its `test result` line): 11 passed, 3 failed -
    `a_rebuilt_binary_is_run_again_from_its_first_start_and_a_run_that_fails_samples_on` (no re-run asked),
    `a_run_again_says_so_and_counts_its_hours_from_the_first_start` (359 samples where 2), and
    `the_door_takes_the_first_start_and_the_real_re_run_says_why_it_failed` (`--first` dropped: ended by the pid file, not its
    hours). The door test's first version hung on the old code (a live loop of twelve hours) and was given a thread that takes the
    pid file away after a second, so the old code ends red at its next sample.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a rebuilt binary is re-run with the first start; a path not there is no rebuild; a failed re-run samples on | pinned by `a_rebuilt_binary_is_run_again_from_its_first_start_and_a_run_that_fails_samples_on` (measure) | n/a: tooling | none | n/a |
| a re-run logs itself and counts its hours from the first start, its pid file kept | pinned by `a_run_again_says_so_and_counts_its_hours_from_the_first_start` | n/a: tooling | none | n/a |
| the door reads `--first`; the real `exec` returns its error | pinned by `the_door_takes_the_first_start_and_the_real_re_run_says_why_it_failed` | n/a: tooling | none | n/a |

### T61 Approach (checklist part A)

1. **The goal, in the world.** A change to what the sampler reads reaches its samples within one interval of the binary's
   rebuild, so no window (T31's like window first) is read from code a landing replaced.
2. **The constraints.** T61's line in tasks.md; 451 T274's D3 (the pid file names the sampler), D13 (`L7R_SAMPLE_MAX_H` bounds a
   run), D5 (detached, no inherited descriptor); T59's section, which filed it.
3. **Where each comes from.** R: T59's and 451 T274's sections; O: the measurements above (2026-11-27).
4. **Do they describe the world here?** Yes: the live sampler's own log and its `exe` link, read 2026-11-27.
5. **The order.** After T59; before T31, which reads the like window.
6. **The exits.** Green: the three new tests and the crate's suite green in `make builder-checks CRATE="rust/gate/crates/measure"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red above turned green: `make builder-checks CRATE="rust/gate/crates/measure"` test, lint and format
   clean, the crate's 310 tests passed (observed 2026-11-27, method: its output; a first run's lint caught a binding named too
   like another, renamed). Live, after landing: the clone's sampler stopped and started once (it runs pre-fix code and
   cannot re-run itself), then its `sampler.log` shows `runs its rebuilt binary` after the next landing's build.
10. **Before moving a constant.** n/a: no constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a map defect: T31's like window, and any `make sampler-report` window after a landing, would read
   samples computed by code the landing replaced - 215 samples listing `lane` on 2026-11-27: fixed here.

**Found and left?** none.

**Performance work?** yes - the sampler measures where the builders' memory goes (451 FR-013: a measurement tool counts); not an
engine-speed task, so `docs/performance-checklist.md` does not apply.


<!-- plan-archive: archived 2026-11-28 -->
### T62 (T58's found-and-left: a lane start or stop could name a dead runner's pid, `runner::tests::a_runner_deaf_to_term_...` red 1 of 60 at load 31-86, measured 2026-11-27 (T58's lane binary 6x10))

- **Approach**: `rust/gate/crates/lane/src/runner.rs`'s `holder()` names the pid read from the lock file only where that process holds the lock itself (`holds`: one of `/proc/<pid>/fd` is the lock file by device and inode, and its `/proc/<pid>/fdinfo/<fd>` lists a `FLOCK` lock - the kernel lists a lock only on the open file holding it, observed 2026-11-27 (a shell holding `flock` on fd 9 beside a second open of the same file: the lock line on the first alone)); `stop` in the window, the lock held and no holder named, signals nothing and says so. Its tests in `runner/tests.rs`. With it, three lines the session's pre-gate coverage named (2026-11-27 about 23:40Z), tests only: `work_cli`'s real `sleep` (a new test, the idle a minute and a stop request ending it, since with the 0.05 s idle a slow first step outlasts the idle and the loop never sleeps), `wake/tests.rs`'s `n == 50` guard (one line, `assert!(n < 50)`, so the guard no right answer reaches runs no unrun line and a regression is still a red, not a hang on the fake clock), and `rustc/run.rs` line 205 - covered in `tested`'s instance of the generic `leak_checked`, but its instances for `side::run_built` and `cover::run_job` were never called with an entry inside `l7r-tmp/` (the lcov's `FNDA:0` on both, observed 2026-11-27 (the cover run's `lcov-rustc.info`)), so `tests/side.rs`'s and the cover world's leaks gain one there.
- **Decision 1 - the reader proves the pid, the writer's order unchanged.** The task offered writing the pid before the lock is seen held: a runner cannot write before it wins the lock without overwriting a live runner's pid when it loses, and the cited red went through the tests' shell stand-ins (`flock` then `echo $$`), which a `work_cli` reorder would not reach. So `holder()` refuses a pid not holding the lock - a dead pid, a zombie (descriptors closed) or a reused pid all hold none - rather than "a live child of" anything (the runner is in a session of its own, nobody's child). No retry knob: in the window `holder()` is `None`, which a start already polls through (`start_built`'s wait) and a stop already said before (the empty file after `set_len(0)`); a stop now says the lock is held and asks again. Label: the algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - Linux `/proc` read for the proof.** The lane runs only in the Linux container; the stall watchdog already reads `/proc` for the runner. Label: convention (the watchdog's own reading).
- Red first, measured 2026-11-27 (make rust-test): `runner::tests::a_pid_is_named_only_where_its_process_holds_the_lock_itself` - the lock held in process, the file naming a dead pid (a reaped child's), then a live pid holding no lock, then this process's own - 0 passed, 1 failed on the old code (`holder` returned the dead pid); after, `runner` and `wake` 48 of 48. The lane test binary whole, 6x10 at once at load 10-53 on 22 cores: 0 red of 60, measured 2026-11-27 (the lane binary 6x10).

### T62 Approach (checklist part A)

1. **The goal, in the world.** A lane start or stop names, and a `NOW=1` stop signals, only the process that holds the runner's lock - never a killed runner's pid or whatever reused it.
2. **The constraints.** T12 Decision 1 (the lock is the truth, the pid secondary) and Decision 9 (`TAKE_S`); T58's start bound; the crate's own-tests coverage; the brief's three named lines.
3. **Where each comes from.** R: tasks.md T62, plan.md T12, T14, T58. O: T58's 6x10 red; the fdinfo observation and the lcov above (2026-11-27).
4. **Do they describe the world here?** Yes: the red test forces the window in the crate's own test binary on this machine; the fdinfo lock line was observed on this kernel.
5. **The order.** After T58; before T22 and T23.
6. **The exits.** Green: the red test green, the lane binary 6x10 at load clean, and the cover run over `lane` and `rustc` naming no line. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one reader and its proof.
8. **The budget.** One landing.
9. **Done, measured.** 0 passed, 1 failed before; green after; 0 red of 60 at load 10-53, measured 2026-11-27 (the lane binary 6x10).
10. **Before moving a constant.** n/a: no constant moved or added.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a stop in the start's window says the lock is held and signals nothing, where it signalled the last runner's pid's group.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: T59 to T10 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
<!-- plan-archive: T60 to T10 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
<!-- plan-archive: T61 to T59 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-28 -->
### T65 (`make lane`'s status lists the repairs the queue's reader keeps open: found by T16)

- **Approach**: `rust/gate/crates/lane/src/log.rs`'s `repairs_open` becomes `repairs_open(common: &Path) -> Vec<String>`, the ids of `l7r_shared::builder_queue::repairs::open(common)` (T16's reader) - REUSED DIRECTLY: the lane crate already depends on `l7r_shared` (its `Cargo.toml`), so no route through `task` and no third copy of the rule. `lane.rs`'s `status` computes it from the clone's common directory and hands it to `report` as a third argument (`log::World` gains no field: `runner/run.rs` builds one, and T18 edits that file). The old in-memory reader (an `eject` line's id, answered by a hand-in's `repair_of`) is gone. Docs restated: `log.rs`'s and `lane.rs`'s, `rust/gate/CLAUDE.md`'s lane row, and the one line of `builder_queue/repairs.rs`'s module doc that said the lane read rule 2 alone. `runner/run.rs` untouched; one line of `runner/run/tests.rs` (its `repairs_open` call, now `&w.common`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **One rule, the queue's**: the status lists exactly the entries `make builder-next` may offer (open: filed, ejected, unanswered, not superseded), before the offer's in-flight and kind filters - those say who may take a repair, not whether it is owed. Label: data-model.md, "A repair entry" (`superseded` read as closed), as T16's Decision 3 states it.
2. **The status now needs the entry, not the `eject` line alone**: an `eject` line naming an id no `repairs.jsonl` line holds is listed by no one. Label: the algorithmically easier route, and the writer's own order - the runner files the entry before its `eject` lines (`repairs.rs`'s module doc), so the case arises in no real log; the status test's fixture now files its entry through `repairs::file`.
3. **Red first**: `lane::tests::status_closes_a_repair_a_later_hand_in_of_its_task_superseded_as_the_queue_does` (entries and `eject` lines written by the lane's own `repairs::file` and `log::append`; r1 handed in again after its ejection, r2 only before it, r3 answered by `repair_of`) failed on the old code, 1 of 6 `lane::tests` (the status said `repairs open: r1, r2, r3`; expected `r2`), 2026-11-27. After: 75 of 75 of the lane crate's tests pass.

### T65 Approach (checklist part A)

1. **The goal, in the world.** `make lane`'s `repairs open` line names the repairs the queue still offers, so the coordinator is never told a repair is owed that no command hands out.
2. **The constraints.** data-model.md's repair entry; T16's Decision 3; plan D7; the brief's keep-out of `runner/run.rs` (T18).
3. **Where each comes from.** R: data-model.md, T16's section. O: the red test above.
4. **Do they describe the world here?** No real repair entry exists yet (the lane has run no real batch); the fixtures write the lane's own line shapes through its writers.
5. **The order.** After T15 and T16; before T23.
6. **The exits.** Green: the lane crate's tests and `make builder-checks CRATE="rust/gate/crates/lane rust/guard/shared"` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/lane rust/guard/shared"` clean, 2026-11-27 (lane: 75 passed).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The status said a superseded repair was open, which no command offered: the coordinator would chase a repair the queue had closed.

**Found and left?** none.

**Performance work?** no



<!-- plan-archive: archived 2026-11-28 -->
### T67 (T18's arbiter repair entry briefed as a red one: its `attempt` is the trigger, which the brief and the offer named as the gate's output)

- **Approach**: `rust/guard/shared/src/builder_queue/repairs.rs`'s `open` reads, for an entry of `why` `arbiter`, its ruling's row - the last row of the clone's `specs/<spec>/arbiter.jsonl` holding the entry's trigger (its `attempt`), as `checks::arbiter::rulings_of` reads it last-wins, named `specs/<spec>/arbiter.jsonl line <n>` - and the attempt files of the batch's `stop` line (`why` `arbiter`, that batch and trigger; T18's `trip` writes them space-joined), kept on `Repair` as `ruling`, `attempts` and `clone`. The new `Repair::read` is the one phrase both print sites use: `the gate's output <attempt>` for any other entry, unchanged, and for an arbiter's `the ruling of <trigger> and the red attempts, in <clone>: specs/<spec>/arbiter.jsonl line <n>, <attempt> <attempt>`. `rust/gate/crates/task`'s `builder_brief.rs` (`Read first: <read>`) and `builder_queue.rs`'s offer line (`make builder-next`, `make queue`, `make builder-done`'s step 1) print it. All read in `l7r_shared`; the lane crate and `lane_wake.rs` untouched. Red first, 2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY="builder_done::tests::an_arbiter_repair_is_briefed_with_its_ruling_s_row_and_the_two_red_attempts builder_done::tests::a_repair_entry_is_dispatched_first"` on the old code: 1 passed, 1 failed (the offer read `CRATE="continue: fix the" ... the gate's output ask:lane-T01`). Green: those modules 36 of 36 and the shared `builder_queue::repairs` tests; `make builder-checks CRATE="rust/guard/shared rust/gate/crates/task rust/guard"`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **The ruling is named as a row, not copied.** The brief names `specs/<spec>/arbiter.jsonl line <n>` under the clone (the entry's `units` already carry `<ruling>: <what>`, and the row holds more than a line of a block can); the line is the last row holding the trigger, as `rulings_of` reads it, and the file alone where no row holds it. Label: the algorithmically easier route. Pinned by `repairs::tests::an_arbiter_s_repair_reads_its_ruling_s_row_and_the_stop_line_s_attempts`.
2. **Named from the clone, the second attempt by its file name in the first's directory.** The ruling is uncommitted in the clone (T18 Decision 3), so no pool tree has it at a relative path; three whole paths put the brief's block at 2,039 characters in the T16 test's form of a real tree, over the prefix guard's 2,000 (measured 2026-11-27, the new task-crate test); the clone named once and the attempts' shared directory once bring it under. A path outside the clone, or an attempt in another directory, is named whole. Label: convention (the prefix guard's cap). Pinned by both new tests.
3. **An arbiter's repair names no crate.** Its units are the ruling's words, so `crates()` read `continue: fix the test` as the red unit `<dirs> test` and offered `CRATE="continue: fix the"`; `crates()` now reads no unit of a `why` `arbiter` entry. Label: a found defect, fixed here (the item below). Pinned by both new tests.
4. **The stop line is found by batch AND trigger.** The runner writes `stop` lines of its own (`pid`, `why` `idle`), and a third pin asks under `lane-<task>-<n>` (T18 Decision 5); a batch no such line names reads no attempts. Label: the stricter reading. Pinned by the shared test's other stop lines and its r2.

### T67 Approach (checklist part A)

1. **The goal, in the world.** The fresh builder `make builder-brief ... REPAIR=` briefs for an arbiter's repair is pointed at the ruling it must carry out and the two red gates that tripped it, and `make builder-next` names the same, never a trigger as a file.
2. **The constraints.** T67's line; T16 (US4: a fresh builder given what it needs whole; the block under 2,000 characters); T18 (Decisions 3 and 5, the `stop` line's fields); the brief's rule that the guard and the task crate read the lane's files from `l7r_shared`.
3. **Where each comes from.** R: tasks.md T67, plan.md T16 and T18. O: `runner/run.rs`'s `trip` and `file_ruled`, `checks::arbiter::rulings_of`, read 2026-11-27; the red and cap figures above.
4. **Do they describe the world here?** No real arbiter repair exists yet; the fixtures write T18's own line shapes (`trip`'s `stop` line, `file_ruled`'s entry and `of_batch` eject line).
5. **The order.** After T16 and T18 (their code in this tree's base); before T23.
6. **The exits.** Green: the changed modules' tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The new tests green with the block under 2,000 characters; `make builder-checks CRATE="rust/guard/shared rust/gate/crates/task rust/guard"` clean, 2026-11-27.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The coordinator's `make builder-next` and the repair builder's brief named `ask:lane-<task>` as "the gate's output" - a file that does not exist - with a CRATE of the ruling's words; now they name the ruling's row and the attempt files.

**Found and left?**
- `crates()` read an arbiter repair's ruling words as a red unit when they end in a step's word (`continue: fix the test` -> `CRATE="continue: fix the"`), so the offered command named a crate that does not exist. Fixed here (Decision 3).

**Performance work?** no

