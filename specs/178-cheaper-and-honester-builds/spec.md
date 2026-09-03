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
  **The derivation may only ADD to what the stamp covers, never remove.** Git pathspec `*` crosses
  `/`, so `AREAS["diagram"] = (".claude/skills/diagram", ("*.py",))` today hashes every `.py` at any
  depth - measured, **37 files outside `l7r/` and `tests/`**, including every `pool` and
  `legacy-hand-authored-pool` `.gen.py` and all of `wip/`. Coverage measures only `l7r/`, so a literal
  "derive the surface from the coverage config" admits an implementation that silently drops those 37
  from the stamp `sync-with-main.sh` checks at push time. A test MUST pin that they stay in.

### Item 2 - the strongest local proof should count

- **FR-004** `make test-full` MUST record a green verification state, as `done`, `quick`, `reference`
  and `test-file` already do, so the paid route's `green-local-since-edit` can be satisfied by the
  most thorough local run rather than only by weaker ones.
- **FR-005** It MUST record only on success, and the recorded target MUST name `test-full` so an
  audit can tell which run vouched.

### Item 3 - perf-gate inside a build

- **FR-006** A build's `perf-gate` MUST compare against a PAST snapshot from the same environment and
  compute identity, using data the container already has.

  **AND THE SPEC MUST BE HONEST THAT THIS DOES NOT, BY ITSELF, MAKE A FULL BUILD GREEN.** The
  author's original diagnosis was wrong in two ways, both checked against code:
  - The in-build `-start` bookend is taken **in a detached worktree at `origin/main`** (the skill
    Makefile), so on a MERGE build it is already a real before/after - pre-merge main against the
    merged tree - not "a run compared to itself". It is self-comparison only on a `ci-measure` run,
    where no merge happened.
  - `tools/perf_bands.py` sets `band = 1` when `total_pct > 0 or any(p > 0 for p in seeds.values())`
    - **any positive delta on any seed**. Changing which snapshot is the baseline does not touch
    that. A past snapshot from a different commit on a different container carries code drift PLUS
    instance noise, so it is at least as likely to land in band 1 as the pairing it replaces.

  So 177's D5 defect survives this transport change, and item 3's own instruction covers the case:
  the GM wrote *"If so then please implement that; if not then let's talk more."* FR-006 therefore
  requires the transport to be implemented AND the residual to be put to the GM as a question with
  its cause named - the `> 0` threshold is theirs, set in feature 129, and relaxing it is the only
  thing that makes a remote FULL build capable of green.
- **FR-006a** Two consequences of pairing on compute identity MUST be stated where a reader meets
  them, not discovered. `machine_identity()` records `host = codebuild:<COMPUTE_TYPE>` and
  `image = <build image>`, so (a) every compute type item 5 introduces starts with NO comparable
  prior, and (b) a `make ci-image` rebuild retires every codebuild baseline at once. Combined with
  FR-009's do-not-fail rule, that makes the remote perf gate silently non-blocking in exactly those
  moments. A gate that goes mute must say it is mute.
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

- **FR-010a** The only renders that stay tracked are ones that are not generated output. Two classes,
  both enumerated rather than left for an implementer to rediscover by reddening the gate:
  - the **magistracy `.svg`** (measured: 122,647 bytes = **0.12 MB**, not the 0.4 MB an earlier draft
    of this FR asserted while its own last sentence demanded per-path evidence), which `.gitignore`
    already un-ignores with the reason
    *"its `.svg` IS the source"* - a Mode A plan is hand-drawn, so the SVG is the source file;
  - the **eight hand-authored negative fixtures** in `tests/fixtures/` (`*-red.svg`, ~0.3 MB), read
    at twelve call sites in `tests/tools/test_pack_audit.py`. They are test INPUTS, deliberately
    broken by hand to prove a check fires; nothing generates them and untracking them reds the gate.
  Membership MUST be shown per path, not asserted.
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
- **FR-010d** The replacement MUST cost kilobytes, not megabytes - measured, the eight exhibits'
  numbers are **503 bytes against 97.9 MB, a 204,000x ratio** - and MUST NOT be a tautology dressed
  as a check. **Asserting `h == round(w * vh / vw)` over numbers recorded FROM consistent files can
  never go red**; it is an arithmetic identity that passes forever. So either:
  (a) the always-runs assertion is against something still tracked and INDEPENDENTLY derived - each
  exhibit's `.json` manifest is tracked and the extent its viewBox encodes is computable from the
  manifest's own geometry, which is a real second source; or
  (b) the spec says plainly that in a renderless checkout nothing is verified and the recorded
  numbers are a RECORD rather than a check.
  One or the other, chosen and stated - never a tautology labeled "real verification".
- **FR-010e** What is LOST MUST be stated where the exhibits are documented: a frozen exhibit is
  write-once and no generator re-rolls it, so once its renders leave git, the mismatch the old check
  guarded against cannot be introduced by anything this repository does - the door it watched stops
  existing. That is the honest reason the replacement can be small, and it is not the same claim as
  "the replacement checks the same thing".
- **FR-010c** Any check THIS FEATURE turns into a skip MUST be named and accounted for at the point
  of change. (This was drafted as "pin the global skip count" and is narrowed: R17's 19-skip
  aggregate is feature 177's parked ruling for the GM, and their follow-up ruled on the 97.9 MB and
  nothing else - pinning it here would be scope this instruction does not carry. It is also the wrong
  premise, since FR-010d requires the replacement to assert ALWAYS.)
- **FR-011** The HISTORY purge MUST be REHEARSED in a throwaway clone before it is performed, and the
  rehearsal MUST report MEASURED before/after `.git` size, object count and fresh-clone time - not a
  sum of blob sizes. A rehearsal is not forbidden by anything: no push is involved and this
  repository's history is untouched by it.
- **FR-011a** The purge MUST then be PERFORMED, and **the route past the guard MUST NOT OUTLIVE THIS
  FEATURE.** The GM authorized an ACT - *"you can indeed handle the history rewriting yourself"* -
  and said nothing about guards. `repo-safety-hooks.sh` has no escape by design, and says so three
  times: its header (*"NO ESCAPE HATCH on the force push: 'never' is the rule and an escape is how
  never becomes sometimes"*), its refusal text, and its row in `CLAUDE.md`'s enforcement table. A
  standing token would convert a one-time authorization into a permanent doctrine change nobody
  asked for, and would drag that row and that header with it.
  So: the escape is added, used for the single force push, and **REMOVED inside this feature**, with
  the removal a numbered task of its own and `scripts/test-repo-safety-hooks.sh` proving at the end
  that the force-push refusal has no escape again. `gate-stamp` covers `scripts/*.sh`, so both states
  are verifiable rather than asserted.
- **FR-011a1** If the removal cannot be completed for any reason, the feature MUST NOT be reported as
  done. A temporary hole left open is the permanent hole this requirement exists to prevent.
- **FR-011b** Everything the purge invalidates MUST be **DERIVED by reading each consumer and stating
  what it keys on**, not listed from memory. The author's first list was wrong in both directions and
  is corrected here as the worked example of why: `verified/` records are keyed by
  `delta.engine_key`, a hash over the blob ids of ENGINE paths, and generated renders are not engine
  paths - **so every verified record SURVIVES the rewrite untouched**. `dev/perf-log/` entries carry a
  `commit` field as information only; `perf_snapshot.identity_of` pairs on
  `(environment, host, image)`. Meanwhile two things that genuinely break were missing: every
  checkout outside this container (the GM's laptop), and the working-tree deletions of FR-012.
  What must be enumerated, each with the consumer that proves it: the session clones in `.clones/`,
  the `/diagram` mirror, `gate-stamp` records, any record class keyed to commit identity, and every
  checkout the GM uses.
- **FR-011c** The purge MUST be verified after the fact, not assumed: a FRESH clone from GitHub, its
  `.git` size and clone time measured, and the gate run green in it. **And the spec MUST say what
  that measurement does NOT prove** - see FR-011d: a fresh clone is small even while a peer clone is
  still holding every purged object, ready to push them back.
- **FR-011d** **THE PURGE UNDOES ITSELF THROUGH ANY SURVIVING CLONE, and this is the requirement that
  prevents it.** There are **12 clones** under `/diagram/.clones/`. After the rewrite their history is
  disjoint from main's, so the moment any one of them merges and pushes, every purged object returns
  to main's history - and Principle VI forbids the rebase that would otherwise fix it. So BEFORE any
  clone pushes, every clone and the `/diagram` mirror MUST be re-created or reset onto the rewritten
  main, with dirty trees carried across as patches by the `format-patch` / `git am` procedure
  `CLAUDE.md` already prescribes for a stray mirror commit. Mid-task work is sacred; that is exactly
  why the patches come first and the reset second.
  This is not satisfiable by writing an accurate list - round 1 rejected that shape once already.
  It is satisfied by every clone being verifiably on the new history.
- **FR-012** `git rm --cached` and a `.gitignore` line, never `git rm` - **and the spec MUST NOT
  pretend that protects anyone but this clone.** It does not. Git deletes files that an incoming
  commit removes, so the `/diagram` mirror the GM browses, the GM's laptop checkout and every future
  clone lose the working copies on their next pull. FR-012a is the requirement that actually protects
  the bytes; this one only fixes the command used here.
- **FR-012a** **THE FROZEN EXHIBITS ARE TRACKED BECAUSE THEY CANNOT BE REBUILT, and that is recorded
  in this repository by the GM.** The root `.gitignore` states it: *"Their gens are never re-run, so
  once the engine drifted their renders stopped being reproducible: they are historical artifacts
  nothing can faithfully rebuild, and are therefore COMMITTED write-once (~195 MB, one time - they
  can never change again)."* Untracking them AND purging history therefore does not move those bytes
  anywhere - it destroys every copy git holds, in every checkout, permanently.
  So before the purge runs, the 171.5 MB of irreproducible exhibit renders MUST be preserved, and the
  destination MUST BE NAMED IN THIS SPEC rather than chosen in passing by an implementer. *"A durable
  location outside git"* is a gesture - satisfiable by a tarball in a container that gets rebuilt.
  Feature 177's D7 said where these bytes live *"is a content decision about the GM's own archive,
  not a tooling decision"*, and the GM's follow-up asked about the 97.9 MB without naming a home.
  The requirement is therefore: name the concrete destination, say how the GM RETRIEVES the bytes,
  and say what keeps it alive across a container rebuild. The candidates, to be chosen and recorded:
  the `/host-l7r-repo` mount (survives container rebuilds, the GM's own disk), or the CI S3 bucket
  under a prefix with its own lifecycle rule (survives everything, costs pennies, but is a new
  home for content that is not CI's). Preservation MUST be VERIFIED by reading the bytes back and
  comparing checksums against the pre-purge tree. The GM's stated backup is a recovery path for a
  mistake, not an archive strategy, and this feature must not rely on it.
- **FR-012b** After the purge, each checkout the GM actually uses MUST still hold the working copies:
  the `/diagram` mirror explicitly restored and confirmed present, and the procedure written down for
  the GM's laptop. A file that becomes gitignored persists once restored; the loss happens on the one
  pull that removes it, and that pull is foreseeable.
- **FR-012c** This is a DELIBERATE DECISION TO DESTROY a recorded artifact class, taken against a
  decision the GM themselves recorded on 2026-08-16, so it MUST be written down as one - what was
  destroyed, why, what it cost, and where the surviving copies are - in the place a future reader
  meets the exhibits. The `.gitignore` block above ceases to be true the moment this lands and MUST
  be rewritten rather than left to mislead.

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
  `XLARGE`. **Who changes the constant is decided here, not left blank**: the GM's verbs were
  *investigate*, *explore*, *see what kinds of performance we get* - which asks for numbers, not for
  a new default to be installed on their behalf. The default governs every future paid build, the
  merge gate included. So the constant changes inside this feature ONLY if the measurement meets a
  criterion stated in advance - **green on every row, and at least 50% cheaper per run at no worse
  wall clock** - and otherwise the numbers and the recommendation go to the GM and `XLARGE` stands
  until they say so. Either way the reasoning is recorded, not the choice alone.
- **FR-017** `make ci-measure` MUST accept `COMPUTE=` so the experiment runs through the sanctioned
  paid route rather than a hand-rolled dispatch. `ci-check` already has this knob (feature 130 T028).

### Not regressing anything

- **FR-018** Every refusal the CI dispatcher makes today MUST still be made and its suite MUST still
  pass, **except where this feature deliberately widens what a guard covers, which is enumerated HERE
  rather than discovered by an implementer.** Feature 177 learned this three times - a blanket
  "everything still passes" clause forbade three of its own requirements in turn - so the list is
  explicit and each widening becomes a CLOSED invariant, never a loosening:
  - **FR-001** adds a short-circuit key (`gate-stamp.py` AREAS/EXCLUDE and its tests) - and that same
    list has a SECOND consumer, the push-time stamp check in `sync-with-main.sh`, so after FR-001 a
    ci-only DIRECT push needs a green `make done` where `make quick` sufficed under the GM's
    feature-132 FR-025 ruling. That follows from item 1 and is correct; it is named here so it does
    not surface as a refused push;
  - **FR-004** adds a recording site (`$(STATE) green-local test-full`);
  - **FR-010/FR-010a/FR-010b** change the subject matter of
    `tests/tooling/ci/test_sparse_checkout.py`: `test_nothing_the_gate_runs_reads_an_excluded_path`
    and `test_only_three_places_reach_a_bundles_render` (whose pinned roster names
    `tests/test_villages.py`, the very check FR-010b retires), and the two sparse-exclude patterns
    for `wip/*.html` and `dev/placement-stages/`, which cease to describe anything git tracks.
    **The answer is stated here rather than left to an implementer**: with no generated render tracked
    at all, the checkout is already small and the sparse mechanism has nothing left to exclude, so
    feature 177's roster is RETIRED - `buildspec/sparse-excludes.txt` removed along with the `run.sh`
    block that reads it and the guard suite that pins it - and the INSTALL saving is re-measured to
    confirm the purge delivers it without them. If the re-measurement shows the mechanism still earns
    its place, it is kept with an honest roster and that is recorded instead. Either way the decision
    is made on a number, not left as a question, because
    `test_the_roster_exists_and_every_pattern_is_anchored` asserts a non-empty roster and would red
    the gate on an empty one;
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
- **SC-004** `git ls-files` shows no GENERATED `.html`, `.svg` or `.png` - the only survivors being
  the magistracy `.svg` (tracked source) and the eight `tests/fixtures/*-red.svg` (hand-authored test
  inputs); every working copy is still on disk in this clone AND restored in the mirror; the gate is
  green.
- **SC-004a** The stale-render property is handled at kilobyte cost by whichever branch of FR-010d is
  taken, and the criterion grades THAT branch: if (a), the always-runs assertion is shown to fail when
  the independently derived source disagrees; if (b), the spec and the code both say plainly that a
  renderless checkout verifies nothing. (Drafted as "asserted in a checkout with no renders present
  at all, and the skip count is pinned" - which forbade branch (b) and carried back the R17 global
  skip count round 2 had removed from FR-010c. The fix had landed in the requirement and not in the
  criterion that grades it, which is round 2's own item 7 one level down.)
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
- **D4** the untracked set with per-path evidence, the frozen exhibits INCLUDED (the carve-out the
  author proposed was declined by the GM twice - once in 177's D7 and again in their follow-up), what
  replaces the raster check and what that replacement does and does not verify, and the two classes
  that stay tracked because they are not generated output (FR-010 to FR-010e)
- **D5** the history purge: the rehearsal's measured before/after, the derived breakage list, where
  the irreproducible exhibit bytes went and how that was verified, the GM's authorization, and the
  guard route taken - added, used, and removed inside the feature (FR-011 to FR-012c)
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

**Round 2 - CHANGES REQUIRED (7).** A second agent confirmed five of round 1's six landed cleanly,
caught the sixth surviving in the decisions list, and then found the thing that matters most in this
feature.

1. **FR-011a made a PERMANENT hole in a guard whose design point is having none.** The GM authorized
   an ACT and said nothing about guards; a standing token would have dragged `CLAUDE.md`'s
   enforcement row and the guard's own header with it - doctrine changes nobody asked for, on a
   NON-NEGOTIABLE principle. Now: added, used, and REMOVED inside the feature, with the suite proving
   the refusal has no escape again at the end, and FR-011a1 saying the feature is not done if the
   removal is not.
2. **`git rm --cached` protects THIS CLONE AND NOTHING ELSE.** Git deletes files an incoming commit
   removes, so the mirror and the GM's laptop lose the working copies on their next pull - and the
   frozen exhibits are, in this repository's own recorded words, *"historical artifacts nothing can
   faithfully rebuild"*, committed write-once for exactly that reason. Untracking plus purging does
   not move those bytes, it destroys every copy git holds. Now FR-012a to FR-012c: preserve them
   outside git and VERIFY by checksum before the purge, restore the mirror after, and write the
   destruction down against the 2026-08-16 decision it reverses.
3. **FR-011b's breakage list was wrong in both directions.** `verified/` records are keyed by
   `engine_key`, a hash over ENGINE blob ids - renders are not engine paths, so every record
   SURVIVES; `perf-log`'s `commit` field is information nothing resolves. Missing were the checkouts
   outside this container. The list must now be DERIVED by reading each consumer.
4. **FR-010d prescribed a tautology.** Asserting `h == round(w * vh / vw)` over numbers recorded from
   consistent files can never go red. Now it must assert against an independently derived second
   source (the tracked `.json` manifest) or say plainly that a renderless checkout verifies nothing
   and the data is a record.
5. **FR-010a would have untracked eight test fixtures the gate reads** - `tests/fixtures/*-red.svg`,
   hand-authored broken SVGs read at twelve call sites. Now enumerated as retained.
6. **FR-010c was unrequested scope** - it pinned R17's global skip count, which is 177's parked
   ruling for the GM, on a premise FR-010d contradicts. Narrowed to the checks this feature changes.
7. **D4 and D5 still recorded the deleted carve-out and the two switches.** Rewritten.

**Round 3 - CHANGES REQUIRED (8).** A third agent confirmed rounds 1 and 2 had landed against code
(and reproduced the FR-010 table exactly, 91 tracked files, no residue), then found three pieces of
new substance and five concrete defects.

1. **The author's diagnosis for item 3 was WRONG, twice, and the fix does not cure the symptom.** The
   in-build `-start` bookend is taken in a detached worktree at `origin/main`, so a MERGE build is
   already a real before/after - self-comparison happens only on `ci-measure`. And
   `perf_bands.py` sets band 1 on `total_pct > 0 or any(p > 0 ...)`, so **any** positive delta trips
   it; changing the baseline cannot help, and a past snapshot from another commit on another
   container carries code drift PLUS instance noise. 177's D5 survives this spec. The GM's own
   instruction covers it - *"if not then let's talk more"* - so the transport is implemented AND the
   residual goes to them, with the `> 0` threshold named as the cause and theirs to relax.
2. **The purge undoes itself through any surviving clone.** There are 12 under `.clones/`; after the
   rewrite their history is disjoint, and the first one to merge and push restores every purged
   object - with Principle VI forbidding the rebase that would fix it. FR-011c's fresh-clone
   measurement is taken before that can happen, so it cannot catch it. Now FR-011d: every clone and
   the mirror reset onto the new history, dirty work carried as patches, BEFORE any of them pushes.
3. **FR-012a was a gesture** - *"a durable location outside git"* names no destination, no reader and
   no retention, and is satisfiable by a tarball in a container that gets rebuilt. Now it must name
   the concrete home, how the GM retrieves the bytes, and what survives a container rebuild.
4. **SC-004a carried back what round 2 deleted** - the R17 global skip count - and forbade FR-010d's
   option (b). Round 2's own item 7, one level down: the fix landed in the requirement and not in the
   criterion that grades it.
5. **FR-003's derivation, read literally, would NARROW the push stamp.** `*` crosses `/` in a git
   pathspec, so the `diagram` area hashes 37 `.py` outside `l7r/` and `tests/` that coverage does not
   measure. "Derive from the coverage config" admits dropping them. Now: the derivation may only ADD,
   with a test pinning the 37.
6. **FR-018 posed the sparse-roster outcome as a question.** With no generated render tracked, both
   patterns match nothing and `test_the_roster_exists_and_every_pattern_is_anchored` asserts a
   non-empty roster. The answer is stated: retire the mechanism and re-measure INSTALL to confirm the
   purge delivers the saving without it, or keep it with an honest roster if the number says so.
7. **The magistracy figure was wrong** in an FR whose own last sentence demands per-path evidence:
   measured 122,647 bytes = 0.12 MB, not 0.4 MB.
8. **FR-016 left the chooser of the new default unnamed** while mandating the change. Now an explicit
   criterion decides it automatically, or the numbers go to the GM.

The reviewer's aside, passed on as it stands: the `> 0` band rule *"looks like the real cost center
here - it is what makes every remote FULL run owe a subagent's paperwork - and it is a threshold the
GM set, so it is theirs to relax if they want green remote builds."*

**Round 4 - pending.**
