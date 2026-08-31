# Feature 174 - One Hundred Percent, Enforced

**Status**: Draft - specified 2026-08-31, after the measurements in [`research.md`](research.md) and
partway through the closures they made possible. [`request.md`](request.md) is the authority.

## The feature, in one sentence

The coverage floor becomes a hard 100% that a merge cannot get past, on a run that deselects nothing.

## Why this exists (the GM's words)

> I think the time has come to begin once again enforcing one hundred percent code coverage ... moved
> back up to one hundred percent with the standard `fail_under = 100` configuration option set so
> that in the future, we literally cannot complete our make done in order to merge back into main,
> and there will no longer be any mechanism by which this can be accomplished.

They exempted `make quick` themselves, and gave the reason: it exists to run the things iteration
needs, which is less than all of the code.

## What the measurement changed about the request (R1-R4, and one correction to the GM)

**The GM's "close to one hundred percent" is RIGHT, and the session's first reading of it was wrong.**
A full run measures **99.28%** on the hamlet path - **89 statements** across 11 modules. The session
initially reported that ~60% of the engine sat outside the hard floor; that is true of the global
`--fail-under=100` check and misleading, because the derived hamlet-path floor covers those same
trees by a different rule. The correction was issued unprompted and is recorded here because the
wrong figure would have made this feature look structural when it is arithmetic.

**Two premises did not survive** (R2, R3):

- the 94% ratchet is NOT refactor debris. Its own comment, dated the day it was set, says the frozen
  pool maps leave "the above-hamlet wings of settlement.py (towns, cities, the capital) ... exercised
  by nothing until those tiers convert to scripted generation". **You cannot cover code no generator
  produces**, so this feature does not try to; that is the migration plan's work.
- **`fail_under = 100` cannot sit on `make done` as scoped today.** It deselects three ways - the
  scope lock's `-m "not rolls_map"`, `--tier hamlet`, and the whole of `tests/tooling/` when the
  tooling stamp is fresh - and a deselected test takes its coverage with it. The Makefile says so:
  the floor was removed rather than "leaving a floor in place that could never be met".

**And there is nothing to restore to** (R4): 5 FULL runs are recorded, all failed. This floor has
never been met in this repository's history. The feature establishes it rather than re-enabling it.

## Scope, stated exactly

**IN**: closing the 89, and putting a hard 100% on a run that deselects nothing, with the push
requiring that run. **OUT**: the town/city/capital wings (no generator produces them); `make quick`
(the GM exempted it); converting any tier.

## Requirements

### FR-001 - the 89 are closed BY TESTS, and by unit tests wherever one will do

Not by pragmas, not by omissions, not by the `PARKED` mechanism in `hamlet_floor.py` - which exists,
which the constitution's own note calls "an invitation", and which this feature deliberately does not
use. Where a line needs a map roll to reach, that is stated and the roll is justified; where a
function is hard to test, it is LIFTED (GM 2026-08-28), not exempted.

**Status: 64 of 89 closed, none needing a roll.** `convex_hull` 16; the `_knobs` town/city branches
and `crop_boxes`' city block 24; `_geom/walls.py` 5; `ways/checks.py` 2, `ways/clearance.py` 2,
`ways/sweeps.py` 1; `finish.py` 3; `plan.py` 2, `wet.py` 2, `_seg_x` 1, `place.py` 1,
`nearer_own_house` 1, `kosatsuba_anchor` 2; and 2 by a peer session in `ways/touch.py`.

**The 25 that remain are a different class** and are listed so the cost is visible rather than
implied: `ways/serve.py` 9 (the fold fallback inside a 400-line straggler search), `ways/touch.py` 8
(the orphan-link rungs), `ways/smooth.py` 1 (a knot collapse), `structures/fixtures/boards.py` 7 (a
caption-placement fallback ladder). Each needs constructed geometry or a testability refactor.

### FR-002 - a census is MEASURED, never tallied

Every count in this feature comes from a full run against a pushed tree. Two sessions working the
same floor produced two wrong numbers within an hour by adding up claims: the peer's summary said
minus six where its own posted rows said minus two (repairs of its own damage counted as gains), and
this session's own tally said 61 closed where the measurement said 60 - a test that passed while
covering nothing, because the function returned at an earlier guard. **The floor rests on the
measurement; the arithmetic is only ever a plan.**

### FR-003 - the floor is hard, and sits on a run that deselects nothing

`fail_under = 100`, no ratchet, no per-module exemption list. It runs where nothing is deselected,
and the PUSH requires that run - which is what makes "no mechanism by which this can be accomplished"
true, since `make done` at reference scope is what gates merging today and it cannot carry the floor.
`make quick` keeps no floor at all.

### FR-004 - what the floor MEASURES is stated, not implied

The measured set is the hamlet path as `tools/hamlet_floor.py` already derives it - every module the
scripted rolls execute - plus the modules already held at a hard 100%. The town/city/capital wings
are outside it because no generator produces them; that exclusion is DERIVED from the roll records,
never a hand-maintained list, so it shrinks by itself as tiers convert.

## Success criteria

1. A full run reports 100% on the measured set, with no ratchet and no parked lines.
2. A run below the floor cannot complete, and the push cannot land without that run.
3. Every one of the 89 is closed by a test that asserts the behaviour, not by an exemption.
4. `make quick` is unchanged.

## Decisions recorded

| # | decision | class |
|---|---|---|
| D1 | the 94% ratchet's gap is unconverted TIERS, not refactor debris - so this feature does not chase it | measured |
| D2 | the floor cannot sit on `make done` at reference scope; it goes where nothing is deselected | measured |
| D3 | no `PARKED`, no pragma, no omit list for the 89 | decided |
| D4 | counts are measured against a pushed tree, never tallied across sessions | decided, after two wrong tallies |
| D5 | the search heuristic: where a function can DECLINE as well as act, coverage usually has the acting - assert the decline beside the action | method |
