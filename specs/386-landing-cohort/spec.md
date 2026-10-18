# Feature Specification: The landing cohort - 48 seeds when engine work lands, and a fresh-seed rate

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=386-landing-cohort`)

**Created**: 2026-10-17

**Status**: In progress - filed

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

1. **"Keep the 10-seed cohort per fix."** Nothing changes: `make cohort` keeps its default of ten (the GM's own ruling, 2026-10-12,
   feature 375 amendment 8, FR-038). This feature adds a landing-time cohort beside it; it does not move the default.
2. **"Run 48 seeds when a feature or batch lands."** Engine work lands only on the GATED route (`sync-with-main.sh done`, engine code
   in the delta), so that is where the 48 seeds are required. A DIRECT landing (docs, specs, tests, tooling) changes no map and rolls
   nothing.
3. **"A block of fresh seeds that rotates each run, recorded as a failure rate rather than a pass/fail."** The fresh block rides
   with the landing cohort - each landing run gets its own block - and is a RATE: printed and recorded, never a refusal. "Each run"
   is read as each landing run, not every `make cohort`: the per-fix loop stays the 48 s ten-seed cohort bullet 1 keeps. (A fresh block
   on any cohort is still one command away - `make cohort N=48 SEED=<n>` - and the rotation's seed is printed so it can be asked for.)

## User scenarios

### User story 1 - a landing rolls 48 seeds and refuses a regression (P1)

A session that changed engine code runs `make cohort-landing` before its push. The gated push refuses until a 48-seed cohort record
exists rolled on exactly the engine being landed, and refuses a seed of those 48 that passed on main's engine and fails now, or
fails worse - with the seeds and the command that answers it.

**Acceptance**:
1. A gated push with no such record is refused, and the refusal names `make cohort-landing`.
2. A gated push whose record shows a seed NEWLY FAILING or WORSENED against main's baseline is refused, naming the seed and its rules.
3. A gated push whose record's failing seeds were failing the same way on main (PRE-EXISTING) goes ahead (constitution XIII: a
   pre-existing failure is not a regression).
4. A DIRECT push is not asked for a cohort.
5. `COHORT_OK="<reason>"` discharges the refusal, to the guard log and `dev/bypass-log/`.

### User story 2 - each landing rolls a fresh block and reports its rate (P1)

`make cohort-landing` also rolls 48 seeds no fixed run uses, from a start that rotates with the engine being landed, and prints
how many failed, as a rate. The push prints that rate; it never refuses on it. `make cohort-seeds` shows the rate over every landing,
so the trend is visible.

**Acceptance**:
1. Two different engines get different fresh blocks; the same engine gets the same block (a re-run is served from the roll cache).
2. The gated push requires a fresh-block record on the landed engine to exist (bullet 3: each landing run records one) and prints
   its rate; a failing fresh seed never refuses it.
3. `make cohort-seeds` prints each fresh record's rate and the pooled rate, and leaves fresh seeds out of its fewest-first-seeds count.

## Requirements

- **FR-001** `make cohort` keeps its default of ten seeds (bullet 1).
- **FR-002** `make cohort-landing` rolls the 48-seed cohort (48 seeds from seed 1, plus the pinned rows) and a fresh block of 48
  seeds, and prints whether the push would take it. Where a failing seed has no baseline on main's engine, it rolls main's 48 in a
  detached worktree (the baseline procedure `docs/spec-kit-and-reviews.md` already prescribes) so the session does not have to.
- **FR-003** The gated route of `sync-with-main.sh done` refuses unless a 48-seed record (first seed 1, 54 maps or more, no
  uncommitted engine diff) was rolled on the engine being landed (`git diff --quiet <its commit> HEAD -- l7r pool`).
- **FR-004** It refuses a seed of that record that is NEWLY FAILING or WORSENED against its baseline on main's engine, and one that
  fails with no baseline; it uses `scripts/measure/cohort_known.py`'s own baseline and standing, not a second reading of them.
- **FR-005** The fresh block's first seed is derived from the engine's content (the `l7r` and `pool` trees and any uncommitted engine
  diff), at or above 10000 so it never meets the fixed seeds or the pinned rows, and is printed.
- **FR-006** The gated route requires a fresh-block record on the landed engine and prints its rate; the rate never refuses.
- **FR-007** `make cohort-seeds` reports each fresh record's rate and the pooled rate, and counts fixed seeds only in its fewest-first-seeds line.
- **FR-008** The refusal is a guard: a `tests/hooks/` suite, its text naming the compliant command, the escape with a reason, a
  row in `docs/guards.md`.
- **FR-009** The docs that say when to roll a cohort (the engine dev loop, the tools index, `docs/guards.md`) say this.

## Out of scope

- **The six failing fresh seeds** (403, 404, 408, 409, 425, 439: two `lane_knots`, two `WebRefused`, one `OverlapRefused`, one
  `SiteRefused`) are generator defects of kinds feature 384 already tracks (its lane-law and web-settle rows). This is a tooling
  feature; they are reported to the GM for 384, not fixed here, and the rate this feature records is how their kind is watched.
- No gate on the rate, no change to the pinned rows, no change to what `make done` runs.

## Success criteria

- **SC-001** A gated push on a clone with no landing record is refused naming `make cohort-landing`; with one, it proceeds.
- **SC-002** A landing record with a seed newly failing against main is refused (shown on a fixture).
- **SC-003** `make cohort N=48 SEED=400` still reproduces the six failures; `make cohort-seeds` prints the fresh rate.
- **SC-004** This feature's own landing goes through the landing cohort if it is gated.
