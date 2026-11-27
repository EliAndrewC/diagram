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


