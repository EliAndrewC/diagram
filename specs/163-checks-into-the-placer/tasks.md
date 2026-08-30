# Tasks: Retire the post-placement check battery into the placer

**Input**: [`spec.md`](spec.md), [`plan.md`](plan.md), [`research.md`](research.md)

**Feature**: 163-checks-into-the-placer

Every task carries `research: rendering | physical | procedure` (constitution v2.12.0). Nothing in this
feature decides a fact about how a place was built, farmed or lived in - it retires audit code - so every
task is `procedure`, with the one exception at T09, which checks that no deletion orphans a physical
finding and is therefore `physical` with its three boxes.

## Phase 0 - baseline (blocking)

- [x] **T01** Take the regression baseline and the opening perf bookend on UNMODIFIED code:
      `git worktree add --detach /tmp/base163 HEAD`, run `make done` there, and record the result in
      `research.md` R4. Check each worktree failure against the clone before calling it pre-existing -
      a fresh worktree carries no gitignored artifacts (the recorded 2026-08-24 trap). Then
      `make perf LABEL=163-start` and fill the plan's bookend table.
      research: procedure

## Phase 1 - the census (US1, P1)

- [x] **T02** Add the verdict journal to `check_village`'s `check()` emitter: under one environment
      variable, append `<check> <verdict> <source>` to a journal file; otherwise no behavior change at
      all. Shape it on `hamletgen/driver.py`'s `STAGE_PROFILE_ENV` - it changes what is RECORDED, never
      what a map rolls (feature 132), and a test asserts a manifest is byte-identical with it set and unset.
      verify: `make quick`
      research: procedure
- [x] **T03** Write `l7r/diagram/tools/firing_census.py`: drive the journal over the five live pool maps
      and every frozen fixture in `pool/regressions/`, union the verdicts, and emit
      `specs/163-checks-into-the-placer/firing-census.{md,json}` - one row per live check name with
      FIRES (naming the artifact) or NEVER-FIRES. Add it to pyproject's coverage exclusion list beside
      `check_census.py`, as a by-hand diagnostic, and say so in its docstring.
      research: procedure
- [x] **T04** Extend the census to the two sources a glob cannot see: the scripted negative fixtures, and
      the WHOLE pytest suite run once with the journal on (inline manifests in `tests/check_village/`
      are the reason - a check made to fail by a hand-built dict fires, and no artifact records it).
      research: procedure
- [x] **T05** Prove the instrument (FR-005). A test that (a) the census names a check independently known
      to fire, (b) it goes RED if the journal comes back empty, and (c) it goes RED if a name a frozen
      fixture pins is missing from the FIRES set. Prove each assertion fires by deleting the code under
      it and watching the test go red - a census that silently classifies nothing is indistinguishable
      from a clean bill of health (`dev/gate.md`).
      verify: `make quick`
      research: procedure
- [x] **T06** Add the `firing-census` target to the skill Makefile with its help line - because everything
      in this skill runs through `make` and it is enforced (feature 127), not because reusable tooling was
      requested; the spec review removed that requirement.
      research: procedure
- [x] **T07** Run the census and record the result. State the NEVER-FIRES set against R2's 9-to-57 floor;
      a result outside that band is a broken census and is diagnosed before anything is deleted.
      measure: `make firing-census`
      research: procedure

## Phase 2 - read the placer, then delete (US1, P1)

- [x] **T08** For every NEVER-FIRES candidate, read the placer that produces the feature it judges and
      grep `dev/`, `specs/` and the commit log for what the check has actually caught. **Two outcomes,
      no third** (FR-006): evidence that the CURRENT placer misses it reclassifies the check FIRING and
      routes it to T14's ledger; no such evidence and it is deleted. A placer that merely DECLINES is not
      evidence and does not save a check. Record the placer read and the outcome per candidate.
      research: procedure
- [x] **T09** Check every DELETE candidate against `research/`: if the check is the only operative
      statement of a historical finding, record where that finding still stands (the `research/` entry,
      the interactive map's modal, the operative doc) before the check goes. A deletion that would orphan
      a citation is not made until the finding has another home.
      research: physical
      - [x] research pass - the record already answers it: grepped `research/`, `settlements/`,
            `buildings/`, `SKILL.md` and `dev/` for all five retired names, zero hits, so no finding
            loses its only operative statement. No new pass needed.
      - [x] source-reader confirmed - nothing to confirm: no source is cited by any retired check, so
            there is no claim for a reader to read.
      - [x] recorded and cited - recorded in `research.md` R9 with the grep that establishes it.
- [x] **T10** Delete the confirmed checks the way feature 146 established: the segment BODY (not a stubbed
      call), any helper whose chain reaches no other live check, the row in
      `tests/fixtures/gate_check_names.json`, the tests, and any frozen fixture whose only purpose was
      that check. NOT a check whose only proof of teeth is a hand-era manifest - the GM's 2026-08-30
      amendment to FR-003 makes hand-era-only evidence a classification, never a deletion criterion. A
      segment file emptied by the sweep goes with its `__init__.py` star-import line and its
      `check_village/CLAUDE.md` row.
      verify: `make quick`
      research: procedure
- [x] **T11** READ THE GUARD of every candidate that looks legacy-tier and establish its actual tier from
      the segment body, never from its name or by subtracting one list from another - the spec review caught
      that error twice, and `ways_clear_of_castle_moat` (no scale guard at all) and `village_has_no_headman`
      (a scale `roll_village` still serves) are the two specimens. Only candidates whose guards have each
      been read AND whose tier no live generator reaches may be presented as a group; the grouping presents
      individually verified verdicts to the GM, it never substitutes for T08's read.
      research: procedure
      research: procedure

## Phase 3 - verify the maps did not move (US1, P1)

- [x] **T12** Regenerate the REFERENCE hamlet (`make maps` picks its own scope) and compare the manifest
      and the render byte-for-byte against before the deletions. Removing an audit should change nothing,
      so any diff is DIAGNOSED here in writing (FR-008) - and once the cause is understood the deletion
      stands and the map is allowed to move, per the GM's standing ruling that no map owes byte identity.
      research: procedure
- [x] **T13** Then the POOL: all five live hamlets, same comparison and the same diagnose-then-accept rule.
      This is the second of the two steps constitution VI requires and is its own task with its own
      verification.
      research: procedure

## Phase 4 - measure what survives (US2, P2 - EVIDENCE ONLY, no changes and no verdicts)

- [x] **T14** Build `surviving-checks.md`: one row per surviving check carrying the MEASUREMENT and no
      category - which stage last changes each input, what the placer guarantees, who besides the gate
      reads the verdict, and what the record shows it has caught. Reuse feature 141's `make check-census`
      for the stage measurement; do not restate it by hand.
      measure: `make check-census`
      research: procedure
- [x] **T15** Against each row, state the evidence for the GM's own two readings - **a bug in the placement
      algorithm**, or **fold it into a trial-and-error placer** - and record "neither, because X" where the
      measurement shows that. Where a later stage can invalidate an earlier one, NAME that stage, because
      that fact is what the discussion turns on; point at `hamletgen/driver.py`'s `farmhouses_reach_a_way`
      ladder as the worked precedent for the fold. **The ledger does not decide** - the spec review was
      specific that sorting the checks before the discussion IS deciding, and the decision is the GM's.
      research: procedure

## Phase 5 - gate, bookend, report

- [x] **T16** `make verify` (the gate and its paired review together, feature 151). Fix everything it
      lists, then re-run once. Then `make perf LABEL=163-end` and `make perf-report AGAINST=163-start`;
      diagnose in writing, with the number, any seed that got SLOWER - a deletion that slows a roll means
      something was removed that the roll depended on. (The constitution's regression bookend; the spec
      review removed the gate-cost REQUIREMENT, so the saving is reported, not required.)
      research: procedure
- [ ] **T17** Report to the GM: what the census found, what was deleted, what the deletion saved (gate
      seconds per map, lines, fixtures - reported because it is interesting, not because it was required),
      which checks the census called never-fires and the placer read RECLASSIFIED as firing with their
      evidence, and the `surviving-checks.md` ledger. **Then STOP.** The case-by-case work on firing checks is the GM's
      discussion, and no placer changes until they have had it (FR-010).
      research: procedure

## Blocked - NOT part of this feature

- **US3, the rearchitecture itself**: folding a check into a trial-and-error placer, converting one to a
  unit test of the placer, or fixing a placer bug a firing check reveals. The GM's request ends *"which is
  a discussion we should stop and have before any changes like that are made."* No task above changes a
  placer, and the feature is complete without one.
