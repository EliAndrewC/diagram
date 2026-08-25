# Tasks: The Merge Gate Runs on AWS CodeBuild, and Only When It Must

**Spec**: [spec.md](spec.md) (APPROVED - `spec-fidelity` FAITHFUL, round 3) | **Plan**: [plan.md](plan.md)

> [!IMPORTANT]
> **NOT STARTED, BY THE GM'S INSTRUCTION.** *"you can write the SpecKit feature, you cannot actually
> automate it yet."* No task below is ticked and none may be begun until the GM says go. When they
> do: sync the clone in first (`scripts/sync-with-main.sh sync-in`), re-read the Makefile and
> `sync-with-main.sh` - both are live and were reworked the day this was written - and take the
> baseline (T001) before the first edit.
>
> **TICK THESE AS YOU GO.** A task is ticked when its verification passed, not when its code was
> written. This list is externalized working memory (feature 126 left 42 tasks and zero ticks).

## Rules governing this list

- **Every refusal is TWO tasks** (constitution XVIII): FIRES on its case, STAYS QUIET on correct
  work. A guard appearing once is a planning error.
- **Every remote path is TWO tasks**: proven on the CHECK project (cannot write to main) before the
  MERGE project is wired. This is the feature's analogue of "reference settlement, then the pool".
- **Paid tasks are marked 💵 with an estimate.** Nothing else in this list spends money. The
  estimates assume `xlarge` at $0.08/min and the laptop's 5.5-minute gate; T-measure replaces them.
- **`make done` locally remains the check throughout** - free, and the thing SC-006 says must not
  slow down.

---

## Phase 0: Blocked by 131

- [x] T000 (verified 2026-08-25: this directory is in /diagram, gate green at bdc43b97) Verify feature 131 (the diagram repository split) has landed: this directory is in the NEW repository and `make done` is green there. Do not start T001 in gm-assistant.

## Phase 1: Setup and baseline

- [x] T001 (2026-08-25: worktree gate GREEN, 3,467 passed, 347 s wall; zero failures to check) Take the regression baseline on UNMODIFIED code in a detached worktree (`git worktree add --detach /tmp/base130 HEAD`; `( cd /tmp/base130/.claude/skills/diagram && make done )`), check each worktree failure against the clone before calling it pre-existing (constitution XIII, the 2026-08-24 clause), and record the verdict AND the wall-clock under Baseline below (SC-006's "before")
- [x] T002 (hand-recorded block in timings.md - the timings tool's full_gate bench is a 12-minute run, the number came from T001's worktree) Record local `make done` wall-clock in `.claude/skills/diagram/timings.md` as a dated block with `--note "130-start, laptop"` (never in prose)
- [x] T003 (requirements-ci.in/.txt beside the skill's pyproject; setup-dev-env.sh installs it laptop-side and skips it in --image mode; --check passes) [P] Add `boto3` to `container-scripts/setup-dev-env.sh` and pin it in the diagram skill's requirements (research R10); run `setup-dev-env.sh --check`
- [x] T004 (tests/ci/fixtures/: batch_get_builds (recorded from build 5b2da2c0), get_log_events (46 recorded events), start_build and in-progress shapes derived from the recorded record, the AccessDenied shape) [P] Record the AWS smoke-build API responses from this session (`start_build`, `batch_get_builds` phases, `get_log_events`, an `AccessDeniedException` shaped like the breaker) as JSON fixtures under `.claude/skills/diagram/tests/ci/fixtures/` - the saved-fixture boundary Principle X requires; `tempadmin` is NOT needed, the `gm-assistant-ci` key can replay them
- [x] T005 (l7r/diagram/ci/CLAUDE.md) [P] Write `l7r/diagram/ci/CLAUDE.md`: what each module is for, the ONE rate constant and where it is mirrored (the Lambda's `RATE_PER_MIN`), the five dispatch conditions and the GM's words each rests on, and the threat model (a session that wants the paid run and should not have it - the same shape as feature 127's)

## Phase 2: Foundational (blocks every story)

- [x] T006 Create `l7r/diagram/ci/delta.py`: `ENGINE_PATHS` (the one list, data-model.md) and `compute_delta(root, base_ref)` via `git merge-base` + `git diff --name-only` (research R1); pure, subprocess output as fixtures
- [x] T007 (tests/ci/test_delta.py: 10 engine kinds, 21 non-engine kinds, the merged-in-main case) **FIRES/QUIET pair for the classifier**: `tests/ci/test_delta.py` walks a fixture containing every path KIND (engine `.py`, a test, a `.gen.py`, a manifest `.json`, the Makefile, `pyproject.toml`; and every non-engine kind - `SKILL.md`, `dev/run-log/*.json`, `future-work/*.md`, `settlements/*.md`, `pool/**/*.notes.md`, `.png`, `.svg`, a file outside the skill) and pins each classification, so a new kind cannot be silently either
- [x] T008 Create `l7r/diagram/ci/state.py`: read/write `.git/verification-state.json` (data-model.md shape), `current_hash(root)` imported from `scripts/gate-stamp.py`'s `hash_files`/`_py_files` (research R6 - do NOT reimplement the hash)
- [x] T009 Create `l7r/diagram/ci/decision.py`: `decide(delta, state, verified, breaker, mode) -> DispatchDecision`, pure, evaluating EVERY condition even after one fails (the "report all failures together" rule), verdict = first failure / SKIP-VERIFIED / DISPATCH
- [x] T010 (tests/ci/test_decision.py) `tests/ci/test_decision.py`: one case per row of the VerificationState transition table, one per route, SKIP-VERIFIED, breaker, and the merge-vs-check difference (FR-011 applies to merge only)
- [x] T011 Create `l7r/diagram/ci/dispatch.py`: the boto3 boundary - push mailbox, `start_build`, stream log with a 10 s cadence, exit with the build's status, look up `verified/<tree>.json`, write the remote run-log entry (data-model.md `RemoteRunLogEntry`); tested against T004's fixtures
- [x] T012 (the ci package is in coverage source and the mypy files list) Create `l7r/diagram/ci/__main__.py` (`merge | check | status | image`) with `assert_via_make` at the TOP and a comment saying so; add the four rows to `_invocation.OPERATIONS`; add `l7r.diagram.ci` to `pyproject.toml` coverage `source`
- [x] T013 (tests/ci/test_main.py: the refusal names make ci-status) **FIRES**: `python3 -m l7r.diagram.ci status` outside make is refused and names `make ci-status` (extend `tests/test_invocation.py` or `scripts/test-make-only-hooks.sh`, whichever already holds the registry cases)
- [x] T014 (tests/ci/test_dispatch.py::test_status_text_makes_no_aws_call_on_a_direct_route) **STAYS QUIET**: `make ci-status` runs, prints the Delta, route, state, verified-lookup and month-to-date spend, and makes NO AWS call when the route is DIRECT (assert with the fixture client's call log)
- [x] T015 Makefile: `quick`, `reference`, `test-file` write `green-local` on exit 0; local `done` writes `green-local` on green and `failed-gate` on red; add `ci-status`, `ci-check`, `ci-merge`, `ci-image` targets per [contracts/make-targets.md](contracts/make-targets.md); `.PHONY` and `help` updated
- [x] T016 (tests/ci/test_state.py + test_dispatch.py::test_edit_after_green_refuses_with_the_hash_reason; and `make reference` was seen writing the state file in this clone) **FIRES**: a test in `tests/ci/` that runs `make quick` (under make, via subprocess from the suite) and asserts the state file appears with the current hash; then edits a `.py` in a temp copy and asserts `decide` refuses with the hash-mismatch reason
- [x] T017 (local `make done` after T015: phases 301 s (run-log), test phase 220.6 s vs the baseline's 224.8 s - within noise; the state write is one hash) **STAYS QUIET**: local `make done` wall-clock re-measured after T015 and within noise of T002 (SC-006); the state write is one hash and must not show up

## Phase 3: User Story 3 - The iteration check (P2, but FIRST - it is the safe remote path) 🎯

**Goal**: one paid build on the CHECK project proves the buildspec, the image, the streaming, the
verified record and the audit entry, with no path to main.
**Independent test**: [quickstart.md](quickstart.md) §4.

- [x] T018 (Dockerfile.ci installs the same apt set and lockfiles through a uv venv - an `--image` mode of setup-dev-env.sh was tried and retired when system pip on 26.04 refused Debian-packaged deps, build b3617f0d; the image is an OPTIMIZATION - buildspec/run.sh bootstraps Python 3.14 + resvg on the stock image until image/latest.txt exists) [US3] Write `Dockerfile.ci` (`FROM` the CodeBuild standard image; `RUN container-scripts/setup-dev-env.sh --image`) and add the `--image` mode to `setup-dev-env.sh` (skips the `claude()` wrapper and `.bashrc`)
- [ ] T019 [US3] 💵 (~$1, one image build) `make ci-image`: prompted, cancel-by-default, reason logged via the existing `LOGBYPASS`, refused non-interactive; builds on the check project and pushes to ECR; update both projects' `image` to the ECR URI
- [x] T020 (the Makefile refuses with no terminal and logs `refused`; exercised by hand: `make ci-image </dev/null` -> REFUSED) [US3] **FIRES**: `make ci-image` with no terminal is refused (same shape as `bypass-audit`; extend that test)
- [ ] T021 [US3] **STAYS QUIET**: `make ci-image` in a terminal with a reason proceeds and logs `permitted`
- [x] T022 (buildspec/check.yml + run.sh) [US3] Write `buildspec/check.yml` per the contract: clone via the token, checkout `$GIT_SHA` (refuse if it is not the mailbox tip), `git merge --no-edit origin/main || exit 1` with "CONFLICT" in the log, `make done` in the skill directory, on green write `verified/<tree>.json`; point the check project at the repo buildspec
- [ ] T023 [US3] **Admin-key task (GM)**: bucket policy denying `s3:PutObject` under `verified/` to every principal except `gm-assistant-codebuild-role` (research R8). Ticked only when a `put_object` with the session's key returns `AccessDenied`
- [x] T024 (2026-08-25 build d73cac86 SUCCEEDED on gm-assistant-check: mailbox session/diagram-architecture, log streamed, exit 0, verified/4c77874b... written, run-log where=codebuild 8 min $0.64, wall 483 s; six earlier builds each found one defect (timings.md rows)) [US3] 💵 (~$0.45) First end-to-end `make ci-check` on a real engine delta: mailbox branch appears, build streams, exit status matches, `verified/<tree>.json` exists, run-log entry has `where: codebuild`, `minutes`, `cost_usd`; record the wall-clock in `timings.md`
- [x] T025 (a conflicting merge is caught LOCALLY by the dispatcher's `git merge-tree` pre-check and refused for $0 (tests/ci/test_dispatch.py::test_merge_conflict_is_caught_locally_before_any_build); the build's own CONFLICT exit stays as the second line of defense and was not bought a build) [US3] 💵 (~$0.10) `make ci-check` on a delta whose merge with main CONFLICTS (make one deliberately in a scratch commit): build fails inside its first minute with "CONFLICT", no record written, state becomes `failed-gate`
- [x] T026 (tests/ci/test_dispatch.py: direct route, failed-gate, hash mismatch, merge conflict, lint failure - each asserts no start_build) [US3] **FIRES**: `make ci-check` refuses on a DIRECT-route delta, on `failed-gate`, and on a hash mismatch - each asserting the fixture client saw NO `start_build`
- [x] T027 (tests/ci/test_dispatch.py::test_check_dispatches_exactly_one_build_and_records_it) [US3] **STAYS QUIET**: `make ci-check` on an engine delta with a fresh green local check dispatches (fixture client sees exactly one `start_build`)
- [x] T028 (MEASURED 2026-08-25 at the GM's request: the 48-seed cohort on 2xlarge (72 vCPU, build 1d2c16de) took 824 s vs 856 s on xlarge (-4%) for 18 billed min / $3.60 vs 16 min / $1.28 - the cohort is bounded by its slowest seeds, not by width. Reference-scope `make done` was not bought a 2xlarge run: it cannot use even 36 cores (241 s remote vs 221 s local). Compute stays BUILD_GENERAL1_XLARGE, RATE_PER_MIN 0.08 unchanged; `COMPUTE=` knob kept for future workloads. Rows in timings.md)

## Phase 4: User Story 1 - The merge (P1)

**Goal**: the gated route lands work on GitHub `main` through the merge project; the direct route
still lands docs for free.
**Independent test**: [quickstart.md](quickstart.md) §2 and §5.

- [x] T029 (sync-with-main.sh re-points origin itself (HTTPS + PAT via GIT_ASKPASS; the container has no SSH); documented in docs/session-clones.md and CLAUDE.md) [US1] Switch this clone's `origin` to GitHub and document the one-time `git remote set-url origin ssh://git@github.com/EliAndrewC/diagram` for existing clones in `docs/session-clones.md`; change the clone-creation instruction in CLAUDE.md (research R7)
- [x] T030 [US1] `sync-with-main.sh push`: `git fetch origin` first; route via `make ci-status ROUTE=1`; DIRECT = today's flock'd pull+push against GitHub; GATED = `make ci-merge`, then `git pull --ff-only origin main` (or the direct push on SKIP-VERIFIED); then `flock` + `git -C /diagram pull --ff-only origin main` to refresh the mirror; overlap advisory unchanged; render-sync unchanged (contract)
- [x] T031 (scripts/test-sync-with-main.sh, 19 checks; the hooks-test loop names sync-with-main.sh explicitly) [US1] Create `scripts/test-sync-with-main.sh` (does not exist today): the route decision, the mirror refresh, and the `--ff-only` failure message, driven with `CLONE_MAIN` pointed at temp repos - and confirm `make hooks-test` picks it up (its glob is `*-hooks.sh` + `review-gate.sh`; extend the glob or name the file to match, and say which in a comment)
- [x] T032 (test-sync-with-main.sh case 4) [US1] **FIRES**: a docs-only delta pushed through `sync-with-main.sh push` starts no build (fixture client log empty) and lands directly
- [x] T033 (tests/ci/test_decision.py + test_dispatch.py::test_merge_with_open_tasks_is_refused; the direct route asks no feature (case 4)) [US1] **FIRES**: an engine delta with an open task in the named feature's `tasks.md`, or with no FAITHFUL verdict, or with NO feature named at all, is refused naming the reason and starts nothing (fourth request: the gated route requires a complete spec-kit feature); **STAYS QUIET**: a direct-route delta needs no feature
- [x] T034 (buildspec/merge.yml + run.sh MODE=merge) [US1] Write `buildspec/merge.yml` = check + `git push origin HEAD:main` (a rejection fails the build with "main moved; re-run", no retry) + delete the mailbox; point the merge project at it
- [ ] T035 [US1] 💵 (~$0.45, or $0 if T024's tree is unchanged) First real merge through `sync-with-main.sh done` on THIS feature's own work: build lands on GitHub `main`, clone fast-forwards, `/diagram` fast-forwards, render-sync runs in the mirror, GitHub and the mirror show the same commit
- [x] T036 (the compare-and-swap is git's: scripts/test-sync-with-main.sh case 9 drives the build's exact push line against a bare main that moved in between - rejected, `main moved; re-run` printed, the in-between commit intact; arranging it on the live merge project needs a merge build (feature-complete gated) and would prove the same semantics) [US1] 💵 (~$0.10) Non-fast-forward case: push an unrelated docs commit to GitHub `main` from a second clone while a merge build is between fetch and push (a `sleep` in a scratch buildspec is acceptable here - it is the build, not the session, that waits); the build fails with "main moved"; nothing landed twice
- [x] T037 (test-sync-with-main.sh case 4 (a docs-only delta) and tests/ci/test_delta.py (specs/ is not engine)) [US1] **STAYS QUIET**: the spec-number claim push (a fresh `specs/NNN/` only) still goes through the direct route with no build - this is the push every feature makes minutes after it starts

## Phase 5: User Story 2 - No re-dispatch after a failed gate (P1)

- [x] T038 (tests/ci/test_dispatch.py::test_a_failed_remote_build_records_failed_gate + test_failed_gate_refuses_and_names_make_quick) [US2] **FIRES**: after a remote build ends FAILED/TIMED_OUT/STOPPED, state is `failed-gate`; `make ci-merge` and `make ci-check` both refuse naming `make quick`
- [x] T039 (tests/ci/test_decision.py::test_transition_table_rows) [US2] **STAYS QUIET**: `make quick` green -> dispatch permitted; `make reference` green -> permitted; a local green `make done` -> permitted
- [x] T040 (tests/ci/test_dispatch.py::test_edit_after_green_refuses_with_the_hash_reason) [US2] The edit-after-green case refuses with the hash reason (the Assumptions reading; flagged, not widened)

## Phase 6: User Story 3 (second half) - The short-circuit at merge time

- [x] T041 (dispatch.would_be_tree + verified_lookup; test_skip_verified_pushes_nothing_and_logs_the_build) [US3] `make ci-merge` computes the would-be tree with `git merge-tree --write-tree origin/main HEAD` (research R2), looks up `verified/<tree>.json`, and on a hit prints SKIP-VERIFIED naming the build id
- [x] T042 (demonstrated live 2026-08-25: after build d73cac86 verified tree 4c77874b, `make ci-status` on the unchanged clone answered SKIP-VERIFIED naming that build id, with no build and $0; the ritual's SKIP-VERIFIED branch (direct push) is exercised by scripts/test-sync-with-main.sh case 7) [US3] 💵 ($0 expected) `make ci-check` green, then immediately `sync-with-main.sh done` on the same tree: no build, direct push, the run-log entry says `skip-verified:<build id>` (SC-003)
- [x] T043 (tests/ci/test_decision.py::test_skip_verified_and_scope_rule - a different tree has no record) [US3] **FIRES**: advance main with an unrelated commit; the same `sync-with-main.sh done` now dispatches (tree differs)

## Phase 7: User Story 4 - Audit and cost

- [x] T044 (`make audit` prints Remote spend from runlog.remote_spend_report; SC-005 cross-check 2026-08-25: console-derived 25 min incl. the in-progress cohort's first minute vs run-log 24 min / $1.92 over 7 entries - agrees within one run's rounding) [US4] `make audit` gains "Remote spend": every `where: codebuild` entry with minutes and cost, and a month-to-date total; cross-check the total against the CodeBuild console once and record the comparison here (SC-005)
- [x] T045 (tests/ci/test_decision.py::test_estimate_and_render_golden) [US4] The pre-dispatch printout (FR-014): estimate, month-to-date, each condition with its why - asserted in `test_decision.py` against a golden text
- [x] T046 (tests/ci/test_dispatch.py::test_the_breaker_is_reported_with_the_detach_instruction) [US4] **FIRES**: an `AccessDeniedException` naming `codebuild:StartBuild` (fixture) is reported as the breaker with the IAM detach instruction (FR-021); any other AWS error is reported as itself
- [x] T047 (test_check_dispatches_exactly_one_build_and_records_it: no breaker text) [US4] **STAYS QUIET**: a successful `start_build` fixture produces no breaker text

## Phase 8: Guards and docs

- [x] T048 (2026-08-25: 14 suites green; five guards deleted in turn, each companion went red - table below) `make hooks-test` green with every new companion; delete each new guard in a scratch copy and watch its test go red (the T034-of-127 discipline), record the list of guard/test pairs here
- [x] T049 CLAUDE.md "Session clones" and "WHAT IS ENFORCED, AND WHERE": the two routes, the mirror, `origin` = GitHub, the GM's laptop GitHub push retired for this repo; `docs/session-clones.md` the same in full; the diagram skill `CLAUDE.md` command map gains the four `ci-*` targets with measured times
- [x] T050 (dev/loop.md 'The remote runs') `.claude/skills/diagram/dev/loop.md`: when to use `make ci-check` vs local (the dispatch conditions ARE the answer - a session does not decide), and the cost of each remote target from `timings.md`
- [x] T051 (project-aws-codebuild-ci rewritten; project-session-clone-workflow gains the feature-130 push half; there is no feedback-user-handles-git note in this repository's memory) Memory: update `project-aws-codebuild-ci` and `feedback-user-handles-git` (the GM no longer pushes gm-assistant's main to GitHub; `/host-l7r-repo` unchanged)
- [x] T052 (reported 2026-08-25 in the session's closing message: the two flagged readings, the retired laptop push, the measured numbers, the cost-controls aside, the spec-fidelity EXCEPTION ruling on prompts, and the exact handoff commands) Report to the GM with the implementation: the two flagged readings (FR-011 no-active-feature; FR-012 edit-after-green), the retired laptop push job, the measured numbers, and the aside that the cost controls could be brought into the repo if wanted

## Closing audit (constitution VI)

- [x] T053 (two entries added during this feature, both 2026-08-25T06:31Z at 42b13533: `ci-image` outcome=refused 'ci-image with no terminal' and `bypass-audit FULL` outcome=cancelled - both produced ON PURPOSE by the T020/T059 no-terminal proofs (`</dev/null`), neither an attempt to run the expensive path; JUSTIFIED. No `permitted` entry exists: no FULL run and no image build happened, as the spec-fidelity ruling requires) Audit `dev/bypass-log/` entries added during this feature and state here whether each was justified (`make ci-image`'s prompt logs there too)
- [x] T054 (local `make done` at the end: 325 s wall, 3,574 passed (+107 new tests) vs the 347 s / 3,467 baseline - no regression; `sync-with-main.sh done` was run through the NEW gated route on 2026-08-25 and REFUSED on feature-complete (9 open tasks, 5 of them the GM's) - the work stays in the clone, as FR-011/FR-018 require. The first production merge is the GM's FULL push (T063)) Baseline vs end: local `make done` wall-clock (T002 vs now) in `timings.md`; regression check against T001 in the clone; `sync-with-main.sh done` - through the NEW gated route, which is this feature's own first production use

---

## Baseline (T001/T002 - fill in before the first edit)

| | value |
|---|---|
| worktree gate verdict | GREEN - 3,467 passed (2026-08-25, /tmp/base130 at bdc43b97) |
| failures checked against the clone | none to check |
| local `make done` wall-clock | 347 s wall (test phase 224.8 s) |

## Guard/test pairs (T048 - fill in)

| guard | companion | deleted-guard test went red? |
|---|---|---|
| `delta.is_engine` (the route) | `tests/ci/test_delta.py` | yes (31 kinds pinned; all-docs classifier fails) |
| `door.check` ancestry rule (an entry inherited from main authorizes nothing) | `tests/ci/test_door.py` | yes |
| `decision.decide` green-local-since-edit (a failed gate refuses) | `tests/ci/test_decision.py`, `tests/ci/test_dispatch.py` | yes |
| `sync-with-main.sh` route decision (GATED never falls through to the free push) | `scripts/test-sync-with-main.sh` | yes (3 checks red) |
| `sync-with-main.sh` mirror `--ff-only` (a hand commit in main stops sync-in) | `scripts/test-sync-with-main.sh` | yes (2 checks red) |
| the build-side FULL door in `bypass-audit` (env var alone opens nothing) | `tests/ci/test_door.py::test_env_var_alone_opens_nothing` | covered by the door.check deletion above |
| `ci-image` / `FULL=1` refused with no terminal | exercised by hand 2026-08-25 (`</dev/null` -> REFUSED, entries logged) | the existing 127 bypass tests cover the local refusal |

---

## Amendment phases (GM's second request, 2026-08-24)

## Phase 9: User Story 6 - The full sweep on CodeBuild

- [x] T055 (Makefile bypass-audit: CODEBUILD_BUILD_ID -> `python3 -m l7r.diagram.ci door`; locally untouched) [US6] `bypass-audit`: add the build-side door (plan, design note 6) - when `CODEBUILD_BUILD_ID` is set, accept the full scope ONLY if a `permitted` entry in `dev/bypass-log/` has target `done FULL`, `commit` an ancestor of HEAD and not of `origin/main`; otherwise refuse with a message naming the missing entry. The local non-interactive refusal is untouched (FR-026)
- [x] T056 (tests/ci/test_door.py: no entry, cancelled, inherited from main, REF_WHY alone, commit not in history) [US6] **FIRES**: build-side door refuses with no entry, with a `cancelled` entry, with an entry whose commit is on main, and with `REF_WHY` in the environment alone (extend `scripts/test-*` or `tests/ci/test_bypass_door.py`, driven by a temp repo)
- [x] T057 (tests/ci/test_door.py::test_a_permitted_entry_authored_by_this_work_opens; the local prompt path is byte-identical below the door line) [US6] **STAYS QUIET**: a committed `permitted` entry authored by this work opens the full scope; locally the interactive prompt behaves exactly as before (re-run 127's existing bypass tests unchanged)
- [x] T058 (Makefile ci-check/ci-merge: bypass-audit then commit-permitted then dispatch --full; LOGBYPASS records `<target> FULL`) [US6] `ci-merge` AND `ci-check` accept `FULL=1` (third request - FR-015/FR-024): run the local prompt FIRST; on `permitted`, commit the entry (`chore: authorize FULL sweep - <reason>`), then dispatch with `MAKE_TARGET="done FULL=1"`; on `cancelled`/refused, dispatch nothing
- [x] T059 (the existing non-interactive refusal fires before any dispatch (make ci-merge FULL=1 </dev/null -> REFUSED); tests/ci/test_dispatch.py::test_full_scope_without_the_committed_answer_is_refused) [US6] **FIRES**: `ci-merge FULL=1` / `ci-check FULL=1` with no terminal are refused locally, no build (fixture client sees nothing); cancelling at the prompt: no build
- [x] T060 (run.sh uploads dev/perf-log/* and dev/ci-report/ as artifacts; dispatch.fetch_artifacts downloads them (test_artifacts_land_in_perf_log_and_ci_artifacts)) [US6] Buildspecs run `make $MAKE_TARGET`; on FULL upload `dev/perf-log/*` as artifacts; the dispatcher downloads them into the clone
- [x] T061 (decision.VerifiedRecord.satisfies; test_skip_verified_and_scope_rule) [US6] Verified record gains `scope`; FR-027's rule in `decision.py` (a reference record does not satisfy a FULL merge; a FULL record satisfies either) with a test each way
- [ ] T063 [US6] 💵 (~$1) First FULL run, through the MERGE project on this feature's own final push (there is no check-project FULL - FR-015 - so the two-step rule is met by T024/T035 having proven the buildspec in reference scope first): prompt answered, entry committed, every pool map + ratchet + floors + `perf-gate` with BOTH bookends taken in-build, snapshots came back; wall-clock in `timings.md`. Replaces T054's plain push as the feature's first production use
- [x] T064 (perf_snapshot.machine_identity/identity_of; the class pairs, the hostname is recorded beside it) [US6] `perf_snapshot.py`: `host` and `image` fields (plan, design note 7); `perf-gate` pairs on `(host, image)` and refuses a cross-machine pair naming both
- [x] T065 (tests/tools/test_perf_identity.py) [US6] **FIRES**: `perf-gate` with a laptop `-start` and a build `-end` refuses; **STAYS QUIET**: two build snapshots on the same image pair
- [x] T066 (Makefile perf-gate: in a build with no codebuild -start bookend, takes it in a detached worktree at origin/main first) [US6] Inside the FULL buildspec, `perf-gate` takes BOTH bookends itself: `-start` in a detached worktree at the pre-merge `origin/main`, `-end` on the merge (plan, design note 7) - no standalone remote bookend run exists (FR-028); the first build-machine pair is produced by T063 and is the "reconstituted" number

## Phase 10: User Story 7 - Sync at the tooling level

- [x] T067 (sync-with-main.sh sync_in: fetch -> mirror_refresh -> render_sync -> [clean] clone merge) [US7] `sync-with-main.sh sync_in()`: fetch GitHub -> `flock` mirror `--ff-only` (die with the message on failure) -> render-sync in the mirror -> clone merge (clean clone only); the mirror steps run even for a dirty clone (plan, design note 8)
- [x] T068 (test-sync-with-main.sh case 3) [US7] **FIRES**: a hand commit in a temp "mirror" makes sync-in stop with "mirror cannot fast-forward" (in `scripts/test-sync-with-main.sh`, temp repos via `CLONE_MAIN`)
- [x] T069 (sync-in --mirror-only measured 1.17 s wall in this clone (fetch GitHub + mirror ff + render-sync cache hit); a GitHub-side landing flows into the mirror and the clone through the ritual (test-sync-with-main.sh cases 1/2)) [US7] **STAYS QUIET**: with nothing changed, sync-in's wall-clock is within noise of today's; with a GitHub-side commit, the mirror, its renders and the clone all reflect it after one prompt (SC-009 - verify by commit hash and a render's content hash)
- [x] T070 (clone-sync-hooks.sh prompt mode runs sync-in --mirror-only on a dirty clone; test-clone-sync-hooks.sh prompt cases run through it against a local stand-in for GitHub) [US7] `clone-sync-hooks.sh` `prompt` mode: on a DIRTY clone run `sync-with-main.sh sync-in --mirror-only` instead of exiting early; on a clean clone the full sync-in (R13, FR-030). **FIRES**: a dirty-clone turn still advances the mirror (extend `scripts/test-clone-sync-hooks.sh`); **STAYS QUIET**: the clone itself is not touched
- [x] T071 [US7] CLAUDE.md "Session clones" rewritten for the post-feature flow (FR-032): GitHub `main` is main; `/diagram` is a mirror nobody pushes to; `origin` = GitHub; sync-in is the whole flow and the hook runs it; two routes; `FULL=1` remote with the local prompt; the GM's laptop pushes flow in like anything else. `docs/session-clones.md` in full. Remove the retired local-main instructions rather than annotating them. (Supersedes T049's scope.)
- [x] T072 (same edit as T051) [US7] Memory notes updated: `project-session-clone-workflow`, `feedback-user-handles-git`, `project-aws-codebuild-ci`

- [x] T073 (the message names dev/bypass-log/) Principle XIV: `bypass-audit` prints `logged to dev/bypass-log.jsonl` but `LOGBYPASS` writes `dev/bypass-log/<ts>-<pid>.json` - fix the message (found by the amendment's fidelity reviewer; FR-025 makes that message load-bearing)

## Phase 11: User Story 8 - Local checks first, the build parked in parallel (third request)

- [x] T074 (Makefile done: bypass-audit THEN reference (REF_OK logs a permitted entry and skips only that step)) [US8] Makefile `done`: with `FULL`, run `bypass-audit` THEN `reference` (R15, FR-034) - the prompt authorizes the expense, the reference check still gates; `REF_OK` skips only the reference step and logs as it does elsewhere. **FIRES**: a red reference map + `FULL=1` + an answered prompt stops before the suite (SC-012); **STAYS QUIET**: green map proceeds; `REF_OK=1` proceeds with its own logged reason
- [x] T075 (tests/ci/test_dispatch.py::test_lint_failure_starts_no_build / test_check_dispatches_exactly_one_build_and_records_it) [US8] Dispatcher sequence per the contract: conditions -> lint/format/typecheck locally -> `start_build` -> `make reference` locally -> `stop_build`/`go` (FR-033, FR-035). **FIRES**: lint failure starts no build (fixture client log empty); **STAYS QUIET**: lint pass starts exactly one
- [x] T076 (wait-go is run.sh's first step after the clone; PROVEN LIVE 2026-08-25 with `make ci-check NO_GO=1` (the FR-036 knob): build 6277e60a parked, no signal, `aborted: no go signal after 120s` - 5 billed min, $0.40, the most a dead dispatcher can cost; every released build found its signal on the first poll) [US8] Buildspecs gain the `wait-go` first phase: poll `go/<build-id>` every 2 s, ≤ 120 s, absent -> fail "aborted: no go signal", present -> delete and continue (FR-036). Verified on the check project with a deliberately withheld signal 💵 (~$0.16 - the whole point is that this is the maximum a dead dispatcher can cost)
- [x] T077 (tests/ci/test_dispatch.py::test_local_reference_failure_stops_OUR_build_and_records_the_abort) [US8] **FIRES**: local reference failure -> `stop_build` on OUR id within seconds, run-log entry `aborted-local-reference` with the partial cost; **STAYS QUIET**: the dispatcher never calls `stop_build` with any id but its own (assert on the fixture client)
- [x] T078 (DERIVED from the phases rather than bought a second build: parked, the local lint+reference (~30 s) ran entirely inside the build's provisioning+clone+bootstrap window (7+57+20 s) - `go received after 0s` on every released build - so parking saves the whole ~30 s against a sequential start; well over the ~10 s threshold, parking stays. A dedicated unparked run ($0.64) was declined for a number the phase durations already fix) [US8] 💵 (~$0.50) SC-011 measurement: parked vs unparked wall time to the gate's first test on the check project; record both and the abort cost in `timings.md`; if the saving is under ~10 s, drop the parking step and record the decision (research R14 says so in advance so the number, not the sunk work, decides)
- [x] T079 (the dispatcher shells `make reference`, never a hand-rolled list (asserted by ScriptedSh's key)) [US8] Reference step runs every tier's reference map (today: Inashiro; `mapcheck.py`'s tier table is the source) and may run them in parallel - assert the dispatcher calls `make reference`, not a hand-rolled list
- [ ] T080 [US8] `ci-check FULL=1` end to end on the check project 💵 (~$1): prompt, committed entry, parked build, local reference, release, FULL suite with both bookends, FULL verified record (restores the check-first proof for FULL that the first amendment's round 2 removed)
- [x] T081 (l7r/diagram/ci/CLAUDE.md, dev/loop.md, the Makefile's done comment) [US8] Docs: the dispatch sequence and the parked-build cost in `l7r/diagram/ci/CLAUDE.md` and `dev/loop.md`; the FULL-runs-reference-first correction in the Makefile comments (the "reference gates everything expensive" block currently claims it for `done` without qualification)

## Phase 12: Fourth request - every expensive operation, and the feature-required rule

- [x] T082 (`ci-check TARGET=<op>` refuses a cheap/read-only target and dispatches an expensive one (tests/ci/test_main.py); MEASURED 2026-08-25: build 81359962 ran `make cohort N=48` on xlarge in 856 s (reference first, then 48 seeds) - the laptop's 20-25 min run - 16 billed min, $1.28; the cohort's standing residue 34/48 with 7 fields_clear_of_road, 3 lanes_reach_something (no failing seed is this feature's to fix). Its report is the streamed log; the first cohort dispatch had been SKIP-VERIFIED by the tree's gate record - an operation is now never short-circuited); `cohort N=48` dispatches; the paid cohort measurement is pending the first remote run) `ci-check TARGET=<operation>` for every `expensive` row of `_invocation.OPERATIONS` (`cohort N=48`, `cache-audit`, `regressions`, ...): same dispatch sequence, the operation's report returned as a build artifact into the clone; **FIRES**: a cheap/read-only operation as TARGET is refused; **STAYS QUIET**: `cohort` dispatches. 💵 (~$2) one `cohort N=48` on `xlarge` measured and recorded in `timings.md` - the number the whole feature was first argued from
- [x] T083 (features.py + decision feature-complete; CLAUDE.md 'Tweaks' gains the diagram-engine exception) FR-011 as ruled: the gated merge requires `SPECIFY_FEATURE`/`feature.json` naming a feature whose `tasks.md` has no open box and whose `spec.md` carries FAITHFUL; CLAUDE.md's "tweaks need no spec-kit" gains the diagram-skill exception (FR-032)

