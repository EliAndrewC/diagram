# Feature 394: Seed regressions refuse a landing - a newly red seed on any form lands only with a filed row or a waiver

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=394-seed-regressions-refuse-a-landing`)

**Created**: 2026-10-19

**Status**: Filed - DEFERRED by the GM until the seeds are expected to pass: not to be planned or worked while many seeds
fail. Start it once the failing-seed work leaves every rolled form's seeds expected green.

**Approved**: the GM, 2026-10-19, "I would like to file a feature for option one, but I don't actually want to work it now."

**Affects**: tooling, hamlet

**Input**: `request.md` - the declined fix and the GM's words, verbatim.

## Why

Feature 374 row 68 (the round arbiter's tooling fix on ask `b10-w146-polder4-regression`, 2026-10-12): polder seed 4
went newly red in wave 146 and was waived under XIII because the polder form is not rolled. The arbiter asked that the
step measuring rolls (`m:w*-rolls`) diff every seed against HEAD and refuse a landing whose newly red seed has no
filed row or arbiter waiver, so a regression on a form the landing cohort does not roll cannot pass unrecorded. It was
declined because no such step exists: those figures come from ad-hoc `make hamlet` loops over archetype seeds, outside
`make cohort` / `make cohort-landing` (feature 386), which hold only the rolled forms. The GM wants it built, but only
once the failing seeds are fixed: while many seeds are red, a check that refuses each newly red one would block every
landing on noise.

## What it is

1. A recorded per-seed run over every archetype form's seeds - the unrolled forms (polder, dike-pond, and the rest held
   out of `ROLLED_ARCHETYPES`) as well as the rolled ones - stored per seed keyed on the engine, as the landing cohort
   stores its seeds.
2. A HEAD baseline of the same seeds, and a diff: each seed green at HEAD and red at the landing is NEWLY RED.
3. The gated push refuses a landing with a newly red seed unless a filed row (in an open feature) or an arbiter waiver
   names that seed; the refusal names the seed, the form and the compliant command.

## Requirements

- **FR-001**: every archetype form's seeds are run and recorded per seed, keyed on the engine (a cached seed is not rerun).
- **FR-002**: a landing's seeds are compared with HEAD's; newly red seeds are listed with their form and failure.
- **FR-003**: the GATED route refuses a newly red seed with no filed row or arbiter waiver naming it; the message carries
  the command to file the row or ask the arbiter.
- **FR-004**: a seed red at HEAD and still red is not refused (the check is for regressions, not the backlog).
- **FR-005**: the GM's deferral holds: this feature is not planned until the seeds are expected to pass (`Status` above).

## Edge cases

- A seed that is red at HEAD and green at the landing is reported as fixed, never refused.
- A form newly added to the archetypes has no HEAD baseline: its seeds are recorded, not judged, on the first landing.

## Success criteria

- **SC-001**: a seeded test landing that turns one unrolled-form seed red with no row is refused, naming the seed.
- **SC-002**: the same landing with a filed row naming that seed lands.
