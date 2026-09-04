# Feature 179 - eight cores, and a band-1 noise floor per environment

**Status**: draft, pre-implementation
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessor**: feature 178, which measured both numbers and deliberately changed neither

## Summary

Two constants move, each answering an open question feature 178 refused to close on its own
authority. Neither is a new mechanism: the compute type and the band thresholds are both existing
knobs, and this feature sets them to values the GM chose from measurements already taken.

1. **`COMPUTE_TYPE` becomes `BUILD_GENERAL1_LARGE`** (8 vCPU), with `RATE_PER_MIN` 0.08 -> 0.02.
2. **Band 1 gets a per-environment noise floor**, 0.0% for `local` (today's behavior, unchanged) and
   2.0% for `codebuild`.

## Why each, from the record

**Eight cores.** Feature 178's table, one commit, sequential, all green:

| compute | vCPU | wall clock | billed | $/min | cost |
|---|---|---|---|---|---|
| `BUILD_GENERAL1_MEDIUM` | 4 | 913 s | 16 min | 0.0100 | $0.16 |
| `BUILD_GENERAL1_LARGE` | 8 | 553 s | 10 min | 0.0200 | **$0.20** |
| `BUILD_GENERAL1_XLARGE` | 36 | 418 s | 7 min | 0.0798 | $0.56 |

2.8x cheaper for 1.32x the time. 4 vCPU is rejected on evidence rather than on price: it saves only
$0.04 more and is where `kuwabata`'s CPU-TIME budget tripped on two of three attempts (178 R7),
because `GEN_TIME_BUDGETS` counts CPU seconds and those RISE on a slower core - flaky, which in a
merge gate is worse than slow. **8 vCPU showed no such failure**, and that is the fact this feature
rests on; it is a measurement of one commit, not a proof for all future workloads.

**The noise floor.** Feature 129's three noise snapshots - IDENTICAL code (commit 7303684) on
`codebuild:BUILD_GENERAL1_XLARGE`, three consecutive builds:

| baseline -> run | total | seeds slower | worst seed | band 1 fires |
|---|---|---|---|---|
| a -> b | +0.76% | 4 of 4 | +1.03% | YES |
| a -> c | +0.55% | 2 of 4 | +1.16% | YES |
| b -> a | -0.75% | 0 of 4 | -0.41% | no |
| b -> c | -0.21% | 2 of 4 | +0.23% | YES |
| c -> a | -0.55% | 1 of 4 | +0.31% | YES |
| c -> b | +0.21% | 2 of 4 | +0.73% | YES |

**Band 1 fired on 5 of 6 comparisons of code that did not change.** The measured noise is about
+-1%; the threshold is `> 0`, so noise clears it nearly every time. The single pair that escaped did
so only because all four seeds happened to land faster - a coin flip, not a passing grade. 2.0% is
the GM's own number; it is about 1.7x the worst measured seed (+1.16%) and about 2x the ~1% noise
band. **And every one of those six comparisons is `codebuild:BUILD_GENERAL1_XLARGE`** - all eight
codebuild snapshots on record are - which is the instance type FR-001 retires. See D2.

## Functional requirements

### The compute type

- **FR-001** `config.COMPUTE_TYPE` MUST be `BUILD_GENERAL1_LARGE` and `config.RATE_PER_MIN` MUST be
  `0.02`, with the comment above them recording the measurement that chose it (the table above, this
  feature, this date) and replacing the 2026-08-24 XLARGE rationale it supersedes.
- **FR-002** **The Lambda mirror MUST move with it.** `config.py`'s own docstring states that
  `RATE_PER_MIN` "is mirrored in exactly one other place: the `gm-assistant-ci-monthly-alert`
  Lambda's `RATE_PER_MIN` environment variable ... Change the compute type and both move together."
  Leaving it at 0.08 would make the live 20%-steps spend email overstate every future bill by 4x.
  If the update cannot be performed, that is REPORTED to the GM as an outstanding action, never
  silently skipped - the docstring's instruction is not this feature's to waive.
- **FR-003** `tests/tooling/ci/test_config.py` pins both constants; it MUST be updated to the new
  values, which is the mechanism that makes this change deliberate rather than accidental.
- **FR-004** Two figures that this change falsifies MUST move with it:
  - the `PARK_TIMEOUT_S` comment's worst-case cost, which states "~$0.16" computed at $0.08/min; at
    $0.02/min the same 120 s is $0.04. The same figure is duplicated at `ci/CLAUDE.md:94` and moves
    with it.
  - `ESTIMATE_MINUTES["reference"]` MUST be set to the MEASURED 8-vCPU figure: **10 minutes**
    (`dev/run-log/20260904T001453005229-3306563.json` - `scope: "reference"`, build `545da8e1`,
    569 s, 10 billed min, $0.20).
    **`full` and `operation` MUST be left alone**, and the comment MUST say they are unmeasured
    placeholders. They are not XLARGE calibrations to be scaled: `git log -S ESTIMATE_MINUTES` finds
    exactly one commit (`ed13cd61`, feature 130 wip), the constant's own comment says "Replaced by
    measurement as timings.md fills in", and the measured XLARGE reference run billed 7 minutes
    against its `5.0`. Multiplying a placeholder by the measured 1.32x and labeling the result
    "scaled" would dress a guess as a derivation - the one failure this project names as fatal.
- **FR-005** Forward-looking statements of the CURRENT default MUST be updated. **Records of runs
  that actually happened MUST NOT be**, and the distinction is the requirement: `timings.md`'s tables,
  `dev/run-log/*.json` and specs 130/177/178 describe real XLARGE runs at $0.08/min, and rewriting
  them would falsify the record. The live sites, named so this is checkable rather than open-ended:
  - `l7r/diagram/ci/CLAUDE.md:7` (the rate and the type), and `:94` (the park figure, per FR-004)
  - the skill `Makefile:621` ("the default stays xlarge") and `:1033` ("it takes `auto` (36 vCPU on
    the xlarge)") - the second states the WORKER COUNT the remote run takes, which changes with the
    box
  - `config.py:22-25`, covered by FR-001
  A stale number in an index is a failure mode this project has hit repeatedly (feature 162's guard
  message; 178's `.gitignore` comment).
- **FR-005a** The AWS-side CodeBuild projects need NO edit. `dispatch.py:397` passes
  `computeTypeOverride=ctx.compute` on the one `start_build` both routes use, so the constant IS the
  whole of "going forward". Stated so that an implementer doing FR-002's Lambda work does not also
  "lock in" the project defaults in the console, which would be an unrequested and invisible change.
- **FR-006** The change MUST NOT touch the `COMPUTE=` knob, `RATES`, or any dispatch condition. This
  is a default, and the ability to measure another type on demand is what produced the table above.

### The band-1 noise floor

- **FR-007** `perf_bands` MUST carry a per-environment band-1 threshold as a named module constant
  beside `BAND2_*`/`BAND3_*`, so all four lines are read in one place and a drift is a deliberate
  change. `local` is `0.0` and `codebuild` is `2.0`.
- **FR-008** An environment with no entry MUST default to `0.0` - the strict, current behavior. A
  new environment must not silently arrive with a floor nobody chose.
- **FR-009** The floor applies to the TOTAL and to EACH SEED, by the same comparison band 1 uses
  today (`>`, so a delta exactly equal to the floor does not fire - matching `BAND2`'s existing
  "exactly 5% is not over the line" behavior, which a test already pins).
- **FR-010** **Bands 2 and 3 MUST be untouched.** The floor mutes the "explain any increase" rung
  only; a real regression still escalates on the same lines it does today. This is the property that
  makes the change safe, and it MUST be proved by a test, not asserted.
- **FR-011** `OWES[0]` reads "nothing - no increase on the total or on any seed". Under a floor,
  band 0 becomes reachable on a POSITIVE delta, so that sentence becomes a printed falsehood about
  what was measured, and it MUST be corrected: the band-0 text must not claim there was no increase
  when a floor muted one.
  **No further disclosure machinery is required, and none is to be added.** `render()` already prints
  every seed's percentage and the TOTAL unconditionally (`perf_bands.py:130-135`) and annotates a
  grown stage on `p > 0` regardless of band (`:133`), so a +1.9% run under the floor is already fully
  visible on the page. The only thing the floor makes untrue is this one string.
- **FR-012** **THE TWO CHANGES IN THIS FEATURE INTERACT, AND THE SPEC MUST SAY SO - AS MEASURED.**
  `perf_snapshot.machine_identity()` records `host = f"codebuild:{COMPUTE_TYPE}"`
  (`tools/perf_snapshot.py:144`), and feature 178's FR-008/FR-009 pair a baseline on that identity.
  The consequence is NOT that the remote gate goes mute:
  - **The 2.0% floor is LIVE on the FIRST remote FULL build after this change.** `perf-gate` takes
    the `-start` bookend IN-BUILD, from `origin/main` in a detached worktree (skill `Makefile:504-508`),
    so the `-end` taken at `:521` has a same-machine partner produced in that same build. This is
    confirmed on the last two remote FULL runs: `20260903T052107Z-177-start-base177.json` and
    `20260903T052247Z-177-end-repo.json`, 100 seconds apart, BOTH `codebuild:BUILD_GENERAL1_XLARGE`.
  - **What the change does retire is the eight stored XLARGE snapshots as CROSS-FEATURE baselines**,
    since `perf_review.pairs()`/`machine_of` key on `host`. A mute remains POSSIBLE - an `-end` on the
    new box whose `-start` was taken locally or on the old one - and `NO COMPARABLE BASELINE ... MUTE`
    lives in `perf_review.check()` (`perf_review.py:171`, push time, `make perf-review`), NOT in
    `perf-gate`.
  The disclosure written at the point of change MUST say this and not the opposite. An earlier draft
  of this requirement asserted the gate would go mute and "self-heal after two remote runs"; that was
  never measured and is false. Writing it would have put a false disclosure at the point of change,
  which is the exact failure a disclosure requirement exists to prevent.

- **FR-013** The module docstring's band matrix - which today says band 1 is "any increase" - MUST
  be updated to state the floor, with the 5-of-6 noise measurement as the recorded WHY at the point
  of change, per the project's research-grounding rule. The existing sentence about the matrix
  applying "to each ENVIRONMENT independently" concerns PAIRING (a local pair never compares to a
  codebuild pair) and remains true; the docstring must not conflate the two, since this feature adds
  a second, different per-environment property.

### What this feature does not do

- **FR-013a** **The band-1 rule is stated in prose at eight live sites; FR-013 covers one.** The
  rest MUST be updated, bounded exactly as FR-005 is - forward-looking statements of the CURRENT
  rule change; ACCOUNTS of what was decided or measured do not:
  - `CLAUDE.md:272` (this repository's enforcement-table row)
  - `.claude/skills/diagram/CLAUDE.md:144` and `:160`
  - `.claude/skills/diagram/dev/performance.md:187-188` (the band matrix, `1 explain > 0% > 0%`)
  - `.claude/agents/perf-audit.md:3` and `:32` - **the agent that ADJUDICATES band 1**. Note its
    band-1 section already reasons about a "1.7% per-seed noise floor" as an acceptable cause; under
    this floor a sub-2.0% codebuild seed no longer reaches the agent at all, so its instructions must
    match the rule it is being asked to apply.
  - the constitution, per FR-013b
  **MUST NOT be rewritten**: `specs/129/*`, `specs/178/*`, both `request.md` files and the review
  records. They are accounts of what was decided or measured at the time.
- **FR-013b** **The constitution MUST be amended in this feature**, because it states the rule the GM
  has just changed and it is the authority that wins on conflict (*"Where this document conflicts
  with other guidance, this document wins"*). This is the project's own mechanism, not a session
  widening its remit: Governance says the GM approves amendments and the implementing session makes
  the edit, and **v2.1.0 (2026-08-25, feature 129) is the amendment that wrote this very three-band
  matrix in**, by the session implementing it. Required: bump **2.15.0 -> 2.16.0** (MINOR - an
  existing principle materially expanded, the same class as 2.1.0), a Sync Impact Report entry
  quoting the GM's request verbatim, the live matrix at `:745` and the Principle VI prose around it,
  the **Version** footer at `:1988`, and the dependent artifacts listed as prior entries do.
  **`.specify/memory/constitution.md:123` MUST NOT be edited**: it sits inside the
  `PRIOR (2.0.0 -> 2.1.0)` block and is a RECORD of what amendment 2.1.0 did. Rewriting it would
  falsify the amendment history, for the same reason FR-005 protects `timings.md` and the run logs.
  The new 2.16.0 entry supersedes it; the old entry stays as written.

### A defect found while doing this (constitution Principle XIV)

- **FR-017** **The in-build bookend guard can NEVER match, so every remote FULL build re-takes the
  `-start` bookend it already has.** Skill `Makefile:504` guards on
  `ls dev/perf-log/*"$$n"-start*codebuild*.json`, but `perf_snapshot.record` names files
  `{stamp}-{label}-{clone}.json` where `clone` is a clone name - **0 of the 44 snapshots on record
  have `codebuild` anywhere in the filename**, so the test is always false and the branch always
  fires. The cost is a full `make perf` run against pre-merge main on every remote FULL build,
  roughly half of `perf-gate`'s time, paid every time.
  The guard MUST ask the SNAPSHOT rather than the filename - is there a `-start` for this feature
  whose recorded machine identity matches THIS build's - which is the same `(environment, host,
  image)` predicate feature 178 already implemented and which `perf_review.machine_of` already
  computes. Fixed here rather than filed, per Principle XIV: it is a defect found in the exact
  mechanism this feature changes, and it is a guard predicate, not an overhaul.
  **This is the one thing in this feature the GM did not ask for**, and it is disclosed as such.
- **FR-014** It does NOT change how a band is enforced, who may write a perf record, or the push
  refusal. `perf_review --check` keeps its behavior; only which verdict it is handed changes.
- **FR-015** It does NOT re-measure the compute types. The table is feature 178's, taken on one
  commit sequentially, and is cited rather than reproduced.
- **FR-016** It costs NO paid remote run. Both changes are constants with local tests; the first
  build to use 8 vCPU will be whichever real dispatch happens next, and its actual billing line is
  the confirmation. **No `ci-measure` may be dispatched to "verify" this**, which would spend money
  to re-learn a number feature 178 already bought.

## Decisions Recorded

- **D1 - 8 vCPU over 4** is a decision to ACCEPT a higher price ($0.20 vs $0.16) to avoid a flaky
  gate, on measured evidence (2 of 3 red on CPU-time budgets). The declined alternative is recorded
  because it is the cheaper one and a future reader will ask why it was passed over: making 4 vCPU
  viable means either raising `GEN_TIME_BUDGETS` - weakening on EVERY machine a guard that caught a
  real 45-minute perf bug - or making the budget machine-relative, which is a feature of its own.
- **D2 - 2.0% is the GM's number, supported by noise measured on a machine this feature retires.**
  Two qualifications the record needs, because overstating either would make a labeled guess look
  like a finding:
  - **The arithmetic.** 2.0 / 1.16 = **1.7x** the worst measured seed, about 2x the ~1% noise band.
    Not "double the worst case".
  - **The provenance.** Every one of the six comparisons - and all eight codebuild snapshots on
    record - is `BUILD_GENERAL1_XLARGE`, which FR-001 retires. **The noise of the 8-vCPU box is
    unmeasured.** A smaller, more contended instance could plausibly be noisier. So this is a
    MEASURED finding on the old machine plus a chosen safety factor, carried across to a new machine
    on the assumption that its noise is not worse - and that assumption is the guess, labeled here
    rather than buried. FR-012's mute means the first two 8-vCPU runs will produce the snapshots that
    can check it; if the floor turns out to be too low there, the number moves, and this is the entry
    that says so.
- **D3 - the floor is a MUTE, not a re-definition.** Band 1 still means "any increase worth
  explaining"; on a noisy machine "any" is operationalized as "any above the noise". The cost is
  accepted and stated: a genuine +1.9% regression on codebuild will not be escalated to band 1. It
  remains VISIBLE either way - `render()` prints every seed percentage and the total unconditionally,
  and annotates a grown stage whenever `p > 0`, neither of which consults the band - and bands 2 and
  3 still fire on their own lines. What is lost is the mandatory written explanation, not the number.
- **D4 - local stays at 0.0, on the recommendation the GM answered.** The load-bearing ground is
  NOT "they exempted nothing local" - that argument cuts both ways, since they exempted nothing from
  the 2% either. It is the recommendation their "yes" answered, recorded verbatim in
  [`request.md`](request.md): *"a per-environment floor of about 2% (double the measured ~1% noise),
  keeping `> 0` locally"*. Their phrase "per environment" tracks it: a per-environment mechanism
  carrying one value everywhere does nothing, so the phrase only does work if the environments
  differ. **`request.md` is the SOLE record of that recommendation** - feature 178's own artifacts
  carry only the residual, not the 2%/local proposal - so it is cited rather than assumed.
  **The GM named no per-environment values.** If they meant 2% in both, this is the one line to
  change, and it is one line: the `local` entry in `BAND1_PCT`. The supporting reasons remain -
  the laptop is quiet, feature 129 designed the rule for it, and it has produced real findings.
