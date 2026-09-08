# 219 - no roll of our own

**Status**: FAITHFUL at round 2 (implementation in progress) - `spec-fidelity` round 1 required two changes, applied: FR-001 records the retirement in
`dev/placement.md`'s "RANDOMNESS IS POSITIONAL OR SCOPED" and the skill CLAUDE.md line, which stated the requirement as
live law (the engine's practice stays; the rule that a draw-count change must not move a map is what goes); FR-002's
audit covers every roll a gate makes, the five shipped generators included, with the reason each stays. Round 2: FAITHFUL.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - the audit the GM asked for (R1),
the count after (R2).
**Predecessors**: 217 (a roll earns its lines: the verdict fails a rostered roll with none), 216 (the floor as doctrine),
215, 214, 213.

## Summary

Two things the GM asked for. First, retire the 2026-08-08 requirement that an upstream change in the number of random
draws must not move a map: *"I am actually okay with an upstream change in the number of random draws moving a map"*.
The immune experiment is the gate's roll of the perturbed reference, and its seventeen unique lines are the perturbation
machinery itself, so retiring the requirement retires the roll, the test and the machinery together. Second, an AUDIT of
every remaining gate roll for the same move - *"assert behavior rather than coverage ... maintaining our one hundred
percent coverage but asserting behavior without doing another full map roll"* - and the cuts it justifies.

The audit (research R1, off feature 217's landed census) finds exactly one remaining roll of the gate's own: Polder
seed 12, eight unique lines, three of them polder engine (`hamletgen/water.py` 414, 475, 574) and five the spec-roll
machinery in `rollcache.py` that exists only because a spec is rolled. Each of the three is a unit test of the function
that owns it, the machinery is unit-tested on a stub, and the polder's behavior assertions move to the soak tier. The
roster then holds NO `Roll` row: a warm gate rolls nothing of its own, and a cold gate rolls only the five shipped maps.
That is the floor the GM's criterion describes, and it is where the packing question ends for the hamlet tier.

## Functional requirements

- **FR-001 The immune requirement is retired.** `test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws`
  is deleted, with `rollcache.extra_draws` and `rollcache._perturbed_manifest` (dead once it is gone; a line nothing
  executes is deleted, never parked - constitution X). The reference's `Roll` row leaves the roster. The 2026-08-08 rule
  is recorded as RETIRED by the GM on 2026-09-08 everywhere it is stated: the roster's docstring, `tests/CLAUDE.md`,
  the `gencache` docstring that still names it, `dev/placement.md`'s "RANDOMNESS IS POSITIONAL OR SCOPED" (which states
  the requirement as live law - *"a feature's randomness must depend on the feature, not on how much randomness the
  map has drawn before it"* - and carries the 2026-08-08 measurement and a probe recipe, both of which become history),
  and the skill `CLAUDE.md`'s always-on line for it. What stays is the ENGINE'S PRACTICE - `_hjit` and `rng_scope`
  exist and every current draw site uses them - described from here as how the engine's randomness is structured and
  why, not as a requirement a gate proves or a rule a new draw must satisfy: the GM retired the requirement, and a
  doc that still reads as one would preserve what they asked to change. No draw site is refactored.
- **FR-002 The audit, recorded.** research R1 lists EVERY roll a gate makes - the two rostered rolls and the five
  shipped generators a cold gate re-rolls - with its unique lines from feature 217's verdict printout, classifies each
  line as engine or machinery, and states for each roll whether it converts under the GM's criterion and why. For the
  five shipped generators, one class: the audit names the Inashiro cold roll's measured ZERO lines of its own (217 R2)
  as exactly the shape the GM asked about, and states the reason the class stays - a shipped map is rolled because it
  ships, and the pool's membership is the GM's exhibit decision (217 FR-001a), so the lever on those five rolls is the
  pool's contents, which this feature does not touch. The GM's question is answered for all seven, not for two.
- **FR-003 Polder 12 leaves the gate.** (a) `water.py` 414 and 475 are inside `stage_polder`; the two loops that own
  them - the reservoir walking uphill until its rim clears the crop, and the perimeter dike gapped wherever a channel
  crosses it - are LIFTED to module-level functions (the feature-146 doctrine) with `stage_polder` delegating, and each
  is a unit test on plain geometry. (b) `water.py` 574, `fit_polder`'s stop when the solved grid lands inside the
  acreage tolerance, is a unit test of `fit_polder` (with `build_polder` stood in for if a real solve costs more than a
  second). (c) The spec-roll machinery - `rollcache._roll_payload`, `hamlet`, `report`, and `tests/gate/_pool.py`'s
  non-pool branches - is unit-tested with `hamletgen.generate` stood in for, on the roll cache's toy fixture. (d) The
  polder's behavior assertions move to `tests/soak/test_polder_fall_0.py` unchanged: the reservoir walk, the grid and
  dike and reservoir, the keep-outs (from `tests/gate/hamletgen/test_water.py`), the lane rules on the polder (the
  `Polder-12` member of `test_the_clean_cohort_seeds_bend_like_paths`) and the polder member of the fan-out ratchet
  (`test_a_rolled_cohort_passes_the_whole_gate`); `rolls.COVERAGE` becomes the two shipped maps. (e) The hamlet-path
  floor's subjects drop Polder 12; the measured module set is compared before and after in R2 (the floor's docstring
  records that every subject has zero modules unique to it, so the set should not move; if it does, the modules that
  leave are named). (f) The `Roll` row leaves the roster; `POLDER_FALL_0` stays as the spec the soak tests read.
- **FR-004 The roster with no rolls.** `tests/rolls.py` states ZERO `Roll` rows: the gate rolls no map of its own; its
  coverage is the five shipped generators (rolled cold when their key moved, served warm with their coverage replayed)
  plus unit tests; a `Roll` row added from here is judged by 217's rule like any other. The census verdict, the roster
  tests and the guard are unchanged in mechanism; a warm gate's census reads 0 rolls of 0 specs, a cold gate's 5 of 5.
- **FR-005 The doctrine's count.** The constitution VI clause's count line, the root `CLAUDE.md` bullet, `tests/CLAUDE.md`,
  `tests/soak/CLAUDE.md` (the new residents), `dev/loop.md`'s packing record and the hamlet floor's docstring say what the
  gate rolls now. Upkeep, no version bump.
- **FR-006 Measured after.** research R2: the census on the landed gate (warm and cold), the gate time, the hamlet-path
  floor's module set before and after.

## What proves less

Two sites, for the GM - the first is the one they asked for, the second follows from the audit they asked for.

1. **The immune property.** An upstream change in the number of random draws moving a map is no longer detected
   anywhere - not at the gate and not in the soak tier, since the GM retired the requirement itself rather than moving
   it. The 2026-08-08 measurement that motivated it (13 of 71 manifest keys moved, a shed drawn 700 px from the change)
   stays in the record as history.
2. **The polder grid is rolled by no gate run.** The pool ships no `polder_grid` map (Kuwabata is the dike-pond archetype
   built on the polder's substrate), so once Polder 12 leaves, the polder-grid archetype's behavior - the reservoir walk
   on a seed that needs it, the grid solved to its acreage, every household seated, the perimeter dike and its gates,
   the keep-outs, the lane rules on a polder - is proved only when the soak tier runs, which is never today. Its
   coverage holds (three unit tests; every other polder line was already reached by unit tests and Kuwabata). If the
   GM wants a polder-grid map rolled at every cold gate, the lever is a polder-grid hamlet in the POOL - an exhibit
   decision, which this feature does not make.

## Success criteria

- **SC-001** `make done` green at 100% on both floors; a warm census reads 0 rolls of 0 specs; a cold census 5 of 5.
- **SC-002** `rollcache.extra_draws` and `_perturbed_manifest` do not exist; no test rolls the reference or a polder in
  the gate tree; the soak tier holds the moved assertions and `make test-file FILE=tests/soak/test_polder_fall_0.py`
  passes by hand.
- **SC-003** The hamlet-path floor's module set is unchanged, or the change is named in R2.

## Decisions Recorded

- **D1 - the machinery goes with the requirement.** `extra_draws`/`_perturbed_manifest` are deleted rather than kept for
  a soak test, because the GM retired the REQUIREMENT, not the roll's place in the gate: a soak test would assert a
  property the GM has said may fail.
- **D2 - the polder converts on the GM's audit ask, not on a new ruling.** The GM asked for every place where behavior
  can be asserted without a roll while keeping 100%; Polder 12 is the only such place left, and its conversion is the
  same move as 216's five sites and 217's seatings. The archetype-level loss (site 2 above) is stated for them.
- **D3 - the two loops are lifted, not tested through `stage_polder`.** Running the stage needs a planned site with a
  solved polder net; the loops need a pond, a ring and a few channels. Feature 146's doctrine: lift, delegate, test on
  plain data.
- **D4 - zero rows is a legitimate roster.** The mechanism does not special-case it: the verdict's stale-row rule is
  vacuous, the audit-pointer test loops over nothing, and a new row is judged by 217. Stated so nobody reads the empty
  tuple as a bug.
