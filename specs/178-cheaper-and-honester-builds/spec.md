# Feature 178 - Cheaper and honester builds

**Status**: DRAFT - not yet reviewed (constitution XVI)
**Request**: `request.md` (the GM's words, verbatim, with the four findings they answer)
**Predecessor**: `specs/177-finish-warming-the-remote-build/` - this feature acts on the four things
177 recorded and left for the GM, plus the compute question their measurement provoked.

## Why

Feature 177 warmed the remote build and then measured it honestly. Four of its findings were rulings
rather than edits, and the GM has now ruled on all four; the fifth item is theirs.

Two of the five are small and unambiguous (items 1 and 2). One is a design question the GM answered
correctly (item 3 - the timing data already travels; what is wrong is which pair is compared). One is
half-doable and half-BLOCKED at the platform level (item 4). One is an experiment (item 5).

## Scope

**In**: the gate's short-circuit keys, what records a verification state, what `perf-gate` compares
inside a build, what generated artifacts git tracks, and what a build costs on smaller compute.

**Out**: what the gate VERIFIES. As in 175 and 177: this feature removes false signals and wasted
money, never checks.

**BLOCKED, not out** - purging the tracked renders from git HISTORY (the second half of item 4). Two
independent hard stops, both verified rather than assumed on 2026-09-03:

1. **GitHub refuses it.** The `remember-the-main` ruleset on the default branch carries rules
   `deletion` and `non_fast_forward` with **`bypass_actors: []`** - nobody, including the GM's own
   PAT, can force-push main. A history purge is a non-fast-forward push by definition.
2. **The constitution forbids it.** Principle VI, NON-NEGOTIABLE (GM 2026-08-25): *"no `git rebase`,
   no `pull --rebase`, no `merge --squash`, no `commit --amend`, no force push. Every landing is a
   real merge commit with its parents intact."* `scripts/repo-safety-hooks.sh` enforces it with **no
   escape token**, deliberately - *"'never' stops meaning never the moment one exists"*.

So this feature MUST prepare and price the purge and MUST NOT perform it (FR-011). The GM asked for a
thing their own rules and their own repository forbid, and the honest response is the measurement plus
the two switches only they can throw - not a session quietly doing it, and not a session quietly
dropping it.

## Functional requirements

### Item 1 - the measured-but-not-engine short-circuit

- **FR-001** A change confined to a surface the coverage floor MEASURES but the engine key EXCLUDES
  (today `l7r/diagram/ci/`) MUST re-open `make done`. The gate that enforces a floor cannot be
  short-circuited by a change to code that floor measures.
- **FR-002** It MUST NOT re-open the PAID route. The GM's feature-132 FR-025 ruling stands - *"isn't
  it actually test code? ... the ci/ directory should join the list of exempted things"* - so a
  ci-only delta still routes DIRECT and still starts no build. The two questions ("does this owe a
  local gate?" and "does this owe a paid build?") stop sharing one answer.
- **FR-003** The measured surface MUST be DERIVED from the coverage configuration rather than
  re-listed by hand. `source = ["l7r"]` is the authority (constitution X clause 5: *"if you add a file
  under `l7r/`, it is measured"*), and a second hand-kept roster would drift from it exactly as the
  roster that clause replaced did.

### Item 2 - the strongest local proof should count

- **FR-004** `make test-full` MUST record a green verification state, as `done`, `quick`, `reference`
  and `test-file` already do, so the paid route's `green-local-since-edit` can be satisfied by the
  most thorough local run rather than only by weaker ones.
- **FR-005** It MUST record only on success, and the recorded target MUST name `test-full` so an
  audit can tell which run vouched.

### Item 3 - perf-gate inside a build

- **FR-006** A build's `perf-gate` MUST compare against a PAST snapshot from the same environment,
  not against a start bookend it took minutes earlier in the same container. Comparing a run to
  itself makes ordinary noise read as "any increase", which is why both of feature 177's FULL builds
  reported band 1 while every test passed at 100% coverage.
- **FR-007** The baseline MUST come from data the container ALREADY has - `dev/perf-log/` is tracked
  and travels with the clone, which is the GM's own answer (*"we pass it along in the same manner we
  pass along our latest code"*). No new transport, no S3 fetch, no GitHub API call.
- **FR-008** The pairing MUST stay within one environment AND one compute identity. `perf_snapshot`
  already refuses a cross-environment comparison (*"a cross-environment percentage is
  indistinguishable from a regression"*, FR-014 of feature 129); a 4-vCPU build compared against a
  36-vCPU one is the same error one level down, and item 5 is about to make that a live case.
- **FR-009** With NO prior snapshot for that environment and compute identity, `perf-gate` MUST say
  so and MUST NOT fail the gate. A first run on a new instance type has nothing to regress against.

### Item 4 - what git tracks

- **FR-010** Generated HTML MUST stop being tracked, and `.gitignore` MUST say so, on the same
  footing as the generated `.svg`/`.png` of a live map. This is the GM's general rule: *"the
  generated html pages should not be tracked just like the generated svg and png files should not be
  tracked."*
- **FR-010a** Every artifact this untracks MUST be one the gate does not read, and that MUST be shown
  per path rather than asserted. **The frozen hamlet exhibits' `.svg`/`.png` (97.9 MB) are the known
  exception**: `tests/test_villages.py` asserts each one's PNG height against its own SVG viewBox and
  ends on `assert checked`, so untracking them turns a real check into a skip and then a failure.
  Feature 177's D7 named them as the part of the 441 MB the gate DOES read, and the GM's instruction
  answered the part read by nothing. If the ruling is meant to cover the exhibits too, that is a
  change to what the gate verifies and belongs to its own feature with a replacement for that check.
- **FR-011** The HISTORY purge MUST NOT be performed, and MUST be prepared: the measured size it
  would recover, the exact procedure, what it would break (every clone re-cloned; every
  `verified/` record and perf bookend keyed to commits that would cease to exist), and the two
  switches only the GM can throw - the `remember-the-main` ruleset and a waiver of Principle VI.
- **FR-012** Untracking MUST NOT delete the working copies. The renders are how the GM looks at maps;
  `git rm --cached` and a `.gitignore` line, never `git rm`.

### Item 5 - what a smaller server costs

- **FR-013** The gate MUST be measured on smaller compute types with REAL builds against the current
  code - at minimum `BUILD_GENERAL1_MEDIUM` (4 vCPU, $0.01/min) and `BUILD_GENERAL1_LARGE` (8 vCPU,
  $0.02/min) - and reported beside the `XLARGE` ($0.08/min) figures 177 measured.
- **FR-014** Each row MUST carry wall clock, billed minutes and dollars, and MUST state whether the
  gate went green. A cheaper instance that cannot finish is not cheaper.
- **FR-015** `config.RATES` MUST cover every compute type the feature dispatches, and the per-minute
  rates MUST be checked against AWS's published price list rather than carried over on trust.
- **FR-016** The recommendation MUST name a default and say what it saves per run against today's
  `XLARGE`. If a smaller type is chosen, the change of default is a one-line constant and belongs to
  this feature; if the measurement does not support one, that is the finding and the default stands.
- **FR-017** `make ci-measure` MUST accept `COMPUTE=` so the experiment runs through the sanctioned
  paid route rather than a hand-rolled dispatch. `ci-check` already has this knob (feature 130 T028).

### Not regressing anything

- **FR-018** Every refusal the CI dispatcher makes today MUST still be made and its suite MUST still
  pass. Where this feature deliberately widens what a guard covers - FR-001 adds a short-circuit key,
  FR-004 adds a recording site - the widening is stated HERE and its test updated to a CLOSED
  invariant, never loosened. (Feature 177 learned this three times: a blanket "everything still
  passes" clause forbade three of its own requirements in turn.)
- **FR-019** The tree MUST stay at 100% coverage with all three floors, and every new branch MUST be
  covered by a test that does not depend on ambient state - the failure mode 177 fixed twice
  (an ambient `GITHUB_TOKEN`, a gitignored `.html`) and once more in a race (`rollcache`).

## Success criteria

- **SC-001** A ci-only edit makes `make done` RUN rather than answer "already verified", and still
  routes DIRECT with no build dispatched. Both observed, not reasoned.
- **SC-002** A green `make test-full` satisfies the paid route's `green-local-since-edit`.
- **SC-003** A build's `perf-gate` names the past snapshot it compared against, and a build with no
  comparable prior says so without failing.
- **SC-004** `git ls-files` shows no generated HTML; the working copies are still on disk; the gate is
  green with the frozen exhibits still tracked.
- **SC-005** The history purge is priced and NOT performed, with both blockers evidenced.
- **SC-006** A table of measured builds across at least three compute types, each with time, cost and
  green/red, and a named recommendation.

## Assumptions

- **A1** `dev/perf-log/` is tracked and therefore already present in a build's checkout. VERIFIED:
  58 snapshots, and feature 177's own two codebuild bookends were committed from build artifacts.
- **A2** Smaller compute types can run the gate at all - memory as well as cores. `XLARGE` is 36 vCPU
  / 72 GB; `MEDIUM` is 4 vCPU / 7 GB. The suite runs 8 workers on a laptop, so 4 is a real reduction
  in parallelism and the memory headroom is the risk. FR-014 makes "it did not finish" a legitimate
  and reportable outcome rather than a failure of the experiment.
- **A3** The sparse checkout and both caches from feature 177 are live, so these measurements are of
  the warmed build rather than the one 177 replaced.

## Decisions Recorded

Per constitution XII, each as **accurate**, **deliberate deviation** or **guess**:

- **D1** the second short-circuit key: what it covers, how it is derived, and why it does not reach
  the paid route (FR-001 to FR-003)
- **D2** `test-full`'s recording site (FR-004, FR-005)
- **D3** what a build's `perf-gate` compares and how the baseline is chosen (FR-006 to FR-009)
- **D4** the untracked set, with per-path evidence, and the frozen-exhibit carve-out (FR-010, FR-010a)
- **D5** the history purge: measured saving, procedure, breakage, and the two switches (FR-011)
- **D6** the compute measurements and the recommended default (FR-013 to FR-016)

## Review history

To be completed - constitution XVI: reviewed against `request.md` by an agent that did not write it,
before implementation, up to five rounds.
