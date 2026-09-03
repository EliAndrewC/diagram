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

**Out**: what the gate verifies - **EXCEPT where item 4 reaches inside it, which it does**. In 175
and 177 that line governed caching and checkout and cost nothing; here the GM's instruction untracks
artifacts a check reads, so the check must change. That is in scope, deliberately, and FR-010b/FR-010d
govern what replaces it. The line is not available as a reason to decline part of this instruction.

**IN, and it was blocked until the GM unblocked it** - purging the tracked renders from git HISTORY
(the second half of item 4). The session found two hard stops and reported them; the GM removed the
first and authorized past the second in their follow-up (`request.md`):

1. **GitHub refused it.** The `remember-the-main` ruleset on the default branch carried
   `deletion` and `non_fast_forward` with `bypass_actors: []`. **The GM has now disabled it**, and
   taken a backup of the repository *"in case anything goes wrong"*.
2. **The constitution still says never.** Principle VI, NON-NEGOTIABLE (GM 2026-08-25): *"no
   `git rebase` ... no force push"*, and `scripts/repo-safety-hooks.sh` enforces it with **no escape
   token**, deliberately - *"'never' stops meaning never the moment one exists"*. The GM has
   authorized this specific act (*"you can indeed handle the history rewriting yourself"*), which is
   a waiver of their own rule and is theirs to give. It is NOT a session's to take, so FR-011a
   governs how the guard is passed: deliberately, logged, and narrowly.

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

- **FR-010** Generated renders MUST stop being tracked - **`.html`, `.svg` AND `.png`** - and
  `.gitignore` MUST say so. This is the GM's general rule, which names all three: *"the generated
  html pages should not be tracked just like the generated svg and png files should not be tracked."*
  The measured set, every row of which this covers:

  | class | MB | files |
  |---|---|---|
  | `wip/*.html` | 190.8 | 15 |
  | frozen hamlet exhibits `.svg`/`.png` | 97.9 | 16 |
  | `dev/placement-stages/*.html` | 73.2 | 14 |
  | legacy NON-hamlet `.svg`/`.png` | 73.6 | 20 |
  | `dev/placement-stages/*.png` | 5.2 | 13 |

- **FR-010a** The ONLY renders that stay tracked are ones that are tracked **SOURCE** rather than
  generated output - the magistracy `.svg` (0.4 MB), which `.gitignore` already un-ignores with the
  reason *"its `.svg` IS the source"*. Membership MUST be shown per path, not asserted.
- **FR-010b** **The frozen hamlet exhibits are IN, and the check that reads them is a COST this
  feature pays rather than a reason to carve them out.** `tests/test_villages.py` walks hamlets-tier
  bundles, asserts each PNG's height against its own SVG viewBox and ends on `assert checked`, so
  untracking all eight fails it by name. That is a cost, not an impossibility. **The author proposed
  exactly this exception to the GM in feature 177's D7** - *"do not untrack the frozen exhibits'
  renders - they are the archive"* - and the GM read it and answered *"I don't see why we should be
  tracking those renders."* An exception whose whole case was put to the GM and not adopted is not one
  a session may re-take (Principle XVI). It is also the largest non-HTML item in the set, so keeping
  it would defeat the stated purpose, *"to clean up the size of our git repo"*.
  So the stale-render property MUST be preserved by a means that needs no tracked raster - the GM
  asked for exactly that (*"there's probably a cheaper way to do this"*) - and FR-010d sets the bar.
  And because untracking makes that check SKIP in a container rather than fail, FR-010c applies.
- **FR-010d** The replacement MUST cost kilobytes, not megabytes, and MUST keep real verification
  rather than becoming a comment. The property under test is a handful of integers per exhibit (an
  SVG viewBox and a PNG's pixel dimensions), so it MUST be recorded as tracked DATA and asserted
  from that always - including in a container where no render exists - AND, wherever the actual
  files ARE present, they MUST be checked against the recorded numbers so a re-render that changes
  them is still caught. What is lost and what is kept MUST be stated: a frozen exhibit is write-once
  and no generator re-rolls it, so once it is out of git the thing the old check guarded against - a
  raster from a different roll than its manifest - can no longer be introduced by anything this
  repository does.
- **FR-010c** A check that becomes a SKIP in a clean checkout MUST NOT become invisible. Feature
  177's R17 already measured 21 skips remotely against 2 locally and recorded that nobody counts
  them; this feature ADDS to that number, so it MUST land the cheapest of R17's options - assert the
  skip count, so the next drift is caught rather than accumulated.
- **FR-011** The HISTORY purge MUST be REHEARSED in a throwaway clone before it is performed, and the
  rehearsal MUST report MEASURED before/after `.git` size, object count and fresh-clone time - not a
  sum of blob sizes. A rehearsal is not forbidden by anything: no push is involved and this
  repository's history is untouched by it.
- **FR-011a** The purge MUST then be PERFORMED, and the guard MUST be passed deliberately rather than
  worked around. `repo-safety-hooks.sh` has no escape token by design, so this feature MUST add one
  that is narrow (the force push alone), requires a written reason like every other escape since
  feature 170, records to the firing log, and carries the GM's authorization quoted at the point of
  change. **The spec states plainly what this costs**: a "never" that now has an exception is a
  weaker "never", and the guard's own comment says so. The alternative - the GM running one command
  at a terminal, as they do for `perf-signoff` - was available and they chose otherwise
  (*"you can indeed handle the history rewriting yourself"*).
- **FR-011b** Everything the purge invalidates MUST be enumerated and handled before it runs: every
  session clone in `.clones/` becomes unmergeable and must be re-cloned; every `verified/` record in
  S3 and every perf bookend in `dev/perf-log/` is keyed to commits that will cease to exist; the
  mirror at `/diagram` must be reset to the rewritten main. A list written after the fact is not a
  plan.
- **FR-011c** The purge MUST be verified after the fact, not assumed: a FRESH clone from GitHub, its
  `.git` size and clone time measured, and the gate run green in it. The GM's backup is the recovery
  path if it is not.
- **FR-012** Untracking MUST NOT delete the working copies. The renders are how the GM looks at maps;
  `git rm --cached` and a `.gitignore` line, never `git rm`.

### Item 5 - what a smaller server costs

- **FR-013** The gate MUST be measured on smaller compute types with REAL builds - at minimum
  `BUILD_GENERAL1_MEDIUM` (4 vCPU) and `BUILD_GENERAL1_LARGE` (8 vCPU) - and **every row of the
  comparison MUST be measured on the SAME COMMIT**, the `XLARGE` baseline included. Feature 177's own
  D4 says in bold *"THE TOTALS ARE NOT COMPARABLE"* about exactly this mistake, made across a recipe
  change; reusing 177's `XLARGE` figures against a different tree would repeat it. If a row must come
  from another commit it MUST be marked as such and no saving may be computed from it.
- **FR-014** Each row MUST carry wall clock, billed minutes and dollars, and MUST state whether the
  gate went green. A cheaper instance that cannot finish is not cheaper.
- **FR-015** Every per-minute rate in `config.RATES` MUST be VERIFIED against AWS's published price
  list, with the source and the date recorded. The constant already lists all four types, so
  "RATES must cover them" is true today and satisfiable by doing nothing; the requirement is the
  check. Its own comment is dated `2026-08`, and every cost figure this feature reports is computed
  from it - a stale rate makes every conclusion wrong in the same direction.
- **FR-016** The recommendation MUST name a default and say what it saves per run against today's
  `XLARGE`. If a smaller type is chosen, the change of default is a one-line constant and belongs to
  this feature; if the measurement does not support one, that is the finding and the default stands.
- **FR-017** `make ci-measure` MUST accept `COMPUTE=` so the experiment runs through the sanctioned
  paid route rather than a hand-rolled dispatch. `ci-check` already has this knob (feature 130 T028).

### Not regressing anything

- **FR-018** Every refusal the CI dispatcher makes today MUST still be made and its suite MUST still
  pass, **except where this feature deliberately widens what a guard covers, which is enumerated HERE
  rather than discovered by an implementer.** Feature 177 learned this three times - a blanket
  "everything still passes" clause forbade three of its own requirements in turn - so the list is
  explicit and each widening becomes a CLOSED invariant, never a loosening:
  - **FR-001** adds a short-circuit key (`gate-stamp.py` AREAS/EXCLUDE and its tests);
  - **FR-004** adds a recording site (`$(STATE) green-local test-full`);
  - **FR-010/FR-010a/FR-010b** change the subject matter of
    `tests/tooling/ci/test_sparse_checkout.py`: `test_nothing_the_gate_runs_reads_an_excluded_path`
    and `test_only_three_places_reach_a_bundles_render` (whose pinned roster names
    `tests/test_villages.py`, the very check FR-010b retires), and the two sparse-exclude patterns
    for `wip/*.html` and `dev/placement-stages/`, which cease to describe anything git tracks. The
    roster becomes: what does the build not check out, now that git carries no generated render at
    all;
  - **FR-011a** adds an escape token to `repo-safety-hooks.sh`, whose companion suite MUST prove the
    escape works AND that every other refusal it makes is unchanged.
- **FR-019** The tree MUST stay at 100% coverage with all three floors, and every new branch MUST be
  covered by a test that does not depend on ambient state - the failure mode 177 fixed twice
  (an ambient `GITHUB_TOKEN`, a gitignored `.html`) and once more in a race (`rollcache`).

## Success criteria

- **SC-001** A ci-only edit makes `make done` RUN rather than answer "already verified", and still
  routes DIRECT with no build dispatched. Both observed, not reasoned.
- **SC-002** A green `make test-full` satisfies the paid route's `green-local-since-edit`.
- **SC-003** A build's `perf-gate` names the past snapshot it compared against, and a build with no
  comparable prior says so without failing.
- **SC-004** `git ls-files` shows no generated `.html`, `.svg` or `.png` anywhere except the
  magistracy `.svg` that is tracked SOURCE; every working copy is still on disk; the gate is green.
- **SC-004a** The stale-render property survives at kilobyte cost, asserted in a checkout with no
  renders present at all, and the skip count is pinned so the next drift is caught.
- **SC-005** The purge is REHEARSED with measured before/after figures, then PERFORMED, then VERIFIED
  from a fresh clone whose `.git` size, clone time and green gate are all recorded.
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

Constitution XVI: reviewed against the GM's own words by an agent that did not write it.

**Round 1 - CHANGES REQUIRED (6).** The reviewer verified every load-bearing claim against code and
found the author's own suspected item to be the real one.

1. **The frozen-exhibit carve-out was NOT a faithful reading, and is deleted.** The decisive argument
   is one the author did not make: *"D7 put this exact exception to the GM, with its full argument,
   as its own recommendation ... The GM read that and answered 'I don't see why we should be tracking
   those renders.' An exception whose entire case was placed before the GM and not adopted is not one
   a session may re-take."* It also failed the purpose test - item 4's stated purpose is to shrink the
   repo, and the carve-out kept the largest non-HTML item in the set. **The GM's own follow-up,
   arriving while this was being applied, confirmed it independently**: *"Do we actually need to keep
   the 97.9 MB?"*
2. **FR-010 was under-scoped even on the narrow reading** - it named HTML only, leaving 78.8 MB of
   generated `.svg`/`.png` tracked against a GM sentence that names all three extensions. Now a
   measured table covering every class.
3. **FR-011 was satisfiable by writing prose** - three of its four deliverables were sentences. Now:
   rehearse in a throwaway clone with MEASURED before/after, then perform, then verify from a fresh
   clone. (The GM has since removed the platform blocker, so it is performed rather than priced.)
4. **FR-013's baseline was cross-code** - it would have compared new smaller-instance rows against
   feature 177's `XLARGE` figures from a different tree, which is precisely the mistake 177's own D4
   flags in bold. Every row is now the same commit.
5. **FR-015 was half-satisfied by doing nothing** - `config.RATES` already lists all four types, so
   the requirement is the VERIFICATION against AWS's price list, dated and sourced.
6. **FR-018 forbade FR-010**, the same shape that bit feature 177 three times: a blanket
   no-regression clause sanctioning only two widenings while a third requirement needed a third. Now
   enumerated, including the `test_sparse_checkout.py` roster whose pinned call sites name the very
   check FR-010b retires.

**Round 2 - pending.**
