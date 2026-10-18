# Feature Specification: The landing cohort - 48 seeds when engine work lands, and a fresh-seed rate

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=386-landing-cohort`)

**Created**: 2026-10-17

**Status**: In progress - filed; spec-fidelity round 1 CHANGES REQUIRED (5 items), round 2 CHANGES REQUIRED (2 items); round 3 verdict FAITHFUL (spec-fidelity, 2026-10-18)

**Approved**: the GM, 2026-10-17, "Sounds good, please implement your recommendation as a feature - file it and then implement it now, thanks."

**Affects**: tooling, hamlet

**Input**: `request.md` - the GM's question, the session's measurements and its three-point recommendation, and the GM's
approval, verbatim. "Your recommendation" is the three bullets quoted there.

## Why

The cohort (`make cohort`: N seeds plus the six pinned rows 901-906) is the strongest test bed the hamlet generator has, and
nothing runs it: no target of the gate or the push asks for one. Sessions roll it by hand, nearly always at the 10-seed default.
Two measurements from `dev/cohort-log/` (in `request.md`):

- **Ten seeds let regressions through to the next 48-seed run.** About 30 ten-seed cohorts passed on 2026-10-12/13; the next
  48-seed run failed on seeds 17, 21, 40 and 45, none of which a ten-seed run rolls.
- **The fixed seeds no longer measure the generator.** Seeds 1-48 all pass on main; 48 seeds nobody had rolled (400-447) failed
  6 times (12%). Fixes aimed at whichever fixed seed failed, so a green 1-48 says more about those seeds than about the generator.

## The three bullets, read literally

The approved text also says what the recommendation changes: *"That would change the cohort default and the landing route, so it's
a feature."* Bullet 2 is the landing route; bullet 3 is the change to the cohort default.

1. **"Keep the 10-seed cohort per fix."** `make cohort` keeps its ten fixed seeds and the pinned rows (the GM's ruling, 2026-10-12,
   feature 375 amendment 8, FR-038). What it rolls by default gains the fresh block of bullet 3.
2. **"Run 48 seeds when a feature or batch lands."** Engine work lands only on the gated route of `sync-with-main.sh done` - route
   `GATED`, or `GATED-LOCAL` while remote is off, as it is today (`dev/switches.json`) - so that is where the 48 seeds are required.
   This is a NARROWING of "when a feature or batch lands": a DIRECT landing carries no engine change (`l7r/diagram/ci/delta.py`
   `is_engine`), so 48 seeds would only re-roll main's own result, and the bullet's purpose ("would have caught 17/21/40/45 the same
   day") cannot be served there.
3. **"A block of fresh seeds that rotates each run, recorded as a failure rate rather than a pass/fail."** Every `make cohort` run
   rolls a fresh block beside its fixed seeds: seeds no fixed run uses, from a start that rotates with the engine. The block is a
   RATE: printed and recorded, it never changes the run's pass count or exit code. Its size on the per-fix run is set by measurement
   so the ten-seed loop of bullet 1 stays as fast as it is (plan); the landing cohort's block is 48.

## User scenarios

### User story 1 - a landing rolls 48 seeds and refuses a regression (P1)

A session that changed engine code runs `make cohort-landing` before its push. The gated push refuses until a 48-seed cohort record
exists rolled on exactly the engine being landed, and refuses a seed of those 48 that passed on main's engine and fails now, or
fails worse - with the seeds and the command that answers it.

**Acceptance**:
1. A gated push (`GATED` or `GATED-LOCAL`) with no such record is refused, and the refusal names `make cohort-landing`.
2. A gated push whose record shows a fixed seed NEWLY FAILING or WORSENED against main's baseline is refused, naming the seed and its rules.
3. A gated push whose record's failing seeds were failing the same way on main (PRE-EXISTING) goes ahead (constitution XIII: a
   pre-existing failure is not a regression).
4. A DIRECT push is not asked for a cohort.
5. `COHORT_OK="<reason>"` discharges the refusal, to the guard log and `dev/bypass-log/`.

### User story 2 - every cohort rolls a fresh block and reports its rate (P1)

Every `make cohort` also rolls seeds no fixed run uses, from a start that rotates with the engine, and prints how many failed, as a
rate; its exit code and pass count read the fixed seeds and the pinned rows alone. The landing cohort's block is 48 seeds. The push
prints the landed engine's rate; it never refuses on it. `make cohort-seeds` shows the rate over every record, so the trend is visible.

**Acceptance**:
1. Two different engines get different fresh blocks; the same engine gets the same block (a re-run is served from the roll cache).
2. A failing fresh seed never fails `make cohort` and never refuses a push.
3. The gated push requires the landed engine's landing record to carry its 48-seed fresh block, and prints its rate.
4. `make cohort-seeds` prints each record's fresh rate and the pooled rate, and leaves fresh seeds out of its fewest-first-seeds count.
5. A printed fresh first seed reproduces its block: `make cohort N=<k> SEED=<that seed> FRESH=0`.

## Requirements

- **FR-001** `make cohort` keeps its ten fixed seeds and the pinned rows by default (bullet 1).
- **FR-002** `make cohort` rolls a fresh block by default (`FRESH=<k>` sets its size), in the same run and the same record as its
  fixed seeds, each fresh seed marked so; the run's pass count and exit code read only the fixed seeds and the pinned rows, and the
  fresh block's failures print as a rate (bullet 3). The default size on the per-fix run is set by a recorded measurement, so that a
  cold default `make cohort` stays within the band of the same run at `FRESH=0` - bullet 1's "at 48 s it's the right inner loop" (observed 2026-10-17; method: the session's timed uncached `make cohort` on seeds 300-309, `request.md`).
- **FR-003** The fresh block's first seed is derived from the engine's content (the `l7r` and `pool` trees and any uncommitted engine
  diff), at or above 10000 so it never meets the fixed seeds or the pinned rows, and is printed.
- **FR-004** `make cohort-landing` rolls 48 fixed seeds from seed 1, the pinned rows and a 48-seed fresh block. BEFORE that roll, when
  main's engine has no 48-seed record, it rolls main's in a detached worktree (the baseline procedure `docs/spec-kit-and-reviews.md`
  prescribes), so the baseline is earlier than the record it judges, as `cohort_known.baselines` requires. It ends by printing what
  the push will say.
- **FR-005** The gated route of `sync-with-main.sh done` (`GATED` and `GATED-LOCAL`) refuses unless a landing record (first seed 1,
  48 fixed seeds or more, the pinned rows, a 48-seed fresh block, no uncommitted engine diff) was rolled on the engine being landed
  (`git diff --quiet <its commit> HEAD -- l7r pool`).
- **FR-006** It refuses a fixed or pinned seed of that record that is NEWLY FAILING or WORSENED against its baseline on main's engine,
  or that fails with no baseline; it uses `scripts/measure/cohort_known.py`'s own baselines and standing, which leave fresh seeds out
  (a fresh seed has no baseline by construction).
- **FR-007** The push prints the landing record's fresh rate and never refuses on it.
- **FR-008** `make cohort-seeds` reports each record's fresh rate and the pooled rate, and counts fixed seeds only in its
  fewest-first-seeds line.
- **FR-009** The refusal is a guard: a `tests/hooks/` suite, its text naming the compliant command, the escape with a reason, a row in
  `docs/guards.md`.
- **FR-010** The docs that say when to roll a cohort (the engine dev loop, the tools index, `docs/guards.md`) say this.

## Out of scope

- **The six failing fresh seeds** (403, 404, 408, 409, 425, 439: two `lane_knots`, two `WebRefused`, one `OverlapRefused`, one
  `SiteRefused`) are generator defects of kinds already tracked: the lane law and the web's settle are feature 385's front since
  2026-10-17 (its T12 carries the side-by-side merge and seeds 49, 55, 57's residue), and the seating and overlap rows stay in
  feature 384. This is a tooling feature; they are reported to the GM, not fixed here, and the rate this feature records is how
  their kind is watched.
- No gate on the rate, no change to the pinned rows, no change to what `make done` runs.

## Success criteria

- **SC-001** (FR-005, FR-007, FR-009) A gated push on a clone with no landing record is refused naming `make cohort-landing`, and
  `COHORT_OK` with a reason discharges it; with a landing record it proceeds and prints the fresh rate.
- **SC-002** (FR-004, FR-006) A landing record with a fixed seed newly failing against main is refused and a pre-existing one passes
  (shown on a fixture); `make cohort-landing` rolls main's baseline first when main's engine has none.
- **SC-003** (FR-001, FR-002, FR-003, FR-008) A plain `make cohort` rolls its ten fixed seeds and the pinned rows, prints its fresh
  rate, and its exit code is unchanged by a failing fresh seed; a cold default `make cohort` with its block, measured and recorded
  under an `m:` key, stays within the band of the same run at `FRESH=0`; `make cohort-seeds` prints the pooled rate; a printed
  fresh first seed reproduces its block.
- **SC-004** (FR-005, FR-010) This feature's own landing goes through the landing cohort, and the docs that say when to roll a cohort
  say it.
