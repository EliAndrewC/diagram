# Feature Specification: Which Automated Checks Still Earn Their Keep, and What the Corpus Is For

**Feature Branch**: none (`SPECIFY_FEATURE=141-checks-and-corpus-audit`)

**Created**: 2026-08-28

**Status**: APPROVED by `spec-fidelity` - round 3 verdict FAITHFUL in substance (2026-08-28): it found the requirement set faithful in both directions and only two stale headline figures (648 -> 636 names; 250 -> 231 measured), corrected; "the failure is a stale measured figure, not a misunderstanding of the request". Implementation proceeds.

**Input**: [`gm-request.md`](gm-request.md), verbatim. That file is the authority.

## The feature, in one sentence

Every gate check is audited against one question - *does any stage after the placer change what this
check reads?* - and a check that only re-measures what a correct placer guaranteed is retired, its
guarantee carried by a unit test of the placer instead; the frozen bad-map corpus is dismantled the same
way (a retired check's fixtures go with it; a kept check gets a SCRIPTED negative fixture where a
hand-placed one stood), a census of who reads each verdict comes before any retirement, the doctrine is
rewritten, and the feature closes when **the GM accepts**, after the session has explained what was cut
and what trade-offs remain - the GM may cut more.

## Why this exists (the GM's words)

- *"If our placement algorithm guarantees that a thing is correct, then I do not believe that there is
  value in running an automated check afterwards to ensure that that exact same thing is correct."*
- *"The automated checks were originally developed in order to deal with the fact that we were placing
  items by hand ... if our placement algorithm makes overlaps impossible, then checking for overlaps later
  in an automated check wastes time with no benefit."*
- *"in cases where, for example, we place a label and then later on things are added to the map, then an
  automated check to see whether the label's placement is still valid is an example of a useful automated
  check."*
- *"If the thing which fixes the wrongness of the map is an update to our placement algorithm, then I don't
  think that saving off that past map actually has value ... we can have one hundred percent unit test
  coverage and have a unit test which asserts that things are now correct without saving off the old map."*
- *"almost all of them were saved prior to our new scripted approach ... It might make sense to just throw
  all of it away. and then start fresh."*
- *"I will take acceptance of it before it lands on main as the final task of the feature after you have
  explained what you have done and what potential trade offs remain ... I might ask you questions which
  result in cutting even more tests than what you cut based on your initial audit"*
- The session's three points, which the GM confirmed as *"indeed my intent"*: same MEASURE vs same FACT is
  the test; the corpus is rebuilt from the placer's own tests; a census of who reads each verdict comes
  first (the generator's re-roll ladder reads `farmhouses_reach_a_way`; the cohort, the tripwire and the
  tests read names).

## The numbers the audit starts from (2026-08-28)

1,405 segment functions in `check_village` (checks and the derivations they share), 636 check names, of which
231 get a measured verdict from the reference hamlet and the seed-19 polder (126 keep, 80 retire-candidates,
25 vacuous on the scripted tier) and 405 a class verdict (no scripted executor); 841 frozen fixtures in `pool/regressions/`
by their own `meta.scale` - 96 hamlet, 139 village, 192 town, 352 city, 9 capital, and 53 that declare no
tier (synthetic manifests captured from unit tests, judged with the check they pin) - of which everything
but the hamlet tier pins checks on maps the FROZEN legacy pool drew by hand and no generator draws today.

## User Scenarios & Testing

### User Story 1 - the census, before anything moves (Priority: P1)

**Acceptance**: **Given** the registry's declared inputs per segment and a snapshot of the manifest after
every generator stage on the reference hamlet (and on one polder), **When** the census runs, **Then**
every check that runs on a scripted hamlet carries: the stage at which its inputs first exist, whether
any later stage changes those inputs, whether any consumer's BEHAVIOR branches on its verdict (today
one does: `hg.generate`'s re-roll ladder on `farmhouses_reach_a_way` - a tool that merely runs and
reports a check, the cohort audit, the tripwire, a test asserting it passes, is not a reader), and how
many fixtures pin it - a LEDGER, one row per check NAME in the registry (636), written before the first
retirement; a check with no scripted executor (the legacy tiers' town, city, capital and village
checks) carries a class-level verdict with its count - "no scripted placer exists for this tier; no
measured verdict is possible; the GM's choice at acceptance" - so the acceptance conversation sees the
whole population.

### User Story 2 - a check that re-measures a guarantee is retired (Priority: P1)

**Acceptance**: **Given** a check whose inputs no later stage changes and whose only reader is the
gate, **When** it is retired, **Then** a unit test of the PLACER asserts the same invariant at placement
(added where none exists), the check's segment, its unit tests and its fixtures are removed, and the
ledger names the placer test that carries the guarantee. **Given** a check whose inputs a later stage
changes (a label after the scatter, the lane web after clipping, the board after the yards), **Then** it
stays, and the ledger names the stage that can undo it. **Given** a check on whose verdict a consumer's behavior branches (the
re-roll ladder), **Then** it stays whatever the census says of its inputs. There is no category that
stays by name - the overlap matrix included, which is the GM's own example of a check that goes when the
placer makes overlaps impossible; a waiver-consistency check that reads registry state written after
placement survives on the measured test (a later-written input), named in the ledger, not on a label.

### User Story 3 - the corpus is rebuilt from what the engine draws (Priority: P1)

**Acceptance**: **Given** a kept check pinned only by hand-era fixtures, **When** the corpus is
rebuilt, **Then** a scripted negative fixture - a spec plus a deliberate break, regenerated by the engine
- proves the check fires on what the engine actually draws, and the hand-era fixture is deleted.
**Given** a retired check, **Then** its fixtures are deleted. **Given** the legacy tiers (village, town,
city, capital: 692 fixtures pinning checks no generator exercises) and the 53 fixtures declaring no tier
(handled with the check each pins - a retired check's go, a kept check's stay until its scripted
fixture exists), **Then** the session presents the
choice to the GM with the numbers at acceptance - delete now (the checks lose their only executor until
those tiers convert; the coverage floor on those segments then needs a decision), keep them, or keep
them only in the full run - and does what the GM rules; until the ruling they run exactly where they
run today.

### User Story 4 - the doctrine says what a bad map becomes now (Priority: P2)

**Acceptance**: `dev/gate.md`, `tests/CLAUDE.md` and the constitution's testing text no longer say
"every bad map becomes a fixture"; they say a bad map becomes a UNIT TEST OF THE PLACER first, and a
fixture only where a later stage can undo the placer - quoting the GM.

### User Story 5 - the GM accepts, after the explanation (Priority: P1)

**Acceptance**: the session explains what was retired, what was kept and why, and the trade-offs that
remain (with numbers: checks before/after, fixtures before/after, gate seconds before/after, what a
retired check would have caught that nothing now watches); the GM asks what they ask, cuts what they
cut; only their explicit acceptance, recorded verbatim, closes the feature; the feature does not land
before it.

### Edge Cases

- A check that reads inputs no stage changes but whose PLACER is shared with a tier not yet scripted
  (a town's houses): retiring the check is safe for the scripted tier only if the placer's unit test
  covers the same path; the ledger says so.
- A check whose "later stage" is the re-roll ladder itself (`farmhouses_reach_a_way`): a generator
  reader - stays.
- A fixture that pins two checks, one retired and one kept: it stays until the kept check has its
  scripted fixture.

## Requirements

- **FR-001**: A census MUST be produced before any retirement, one row per check NAME in the registry
  (636): its input keys (from the registry's dataflow), the first stage at which they exist and whether
  any later stage changes them (from per-stage manifest snapshots of the reference and one polder), its
  BRANCHING readers (consumers whose behavior depends on the verdict - the re-roll ladder; never a tool
  that only runs and reports it), its fixtures by tier; a check no scripted map exercises carries the
  class verdict of User Story 1. The census is a committed ledger.
- **FR-002**: A check MUST be retired when (a) no stage after its inputs' placer changes those inputs on
  either snapshot, (b) no consumer's behavior branches on its verdict, and (c) a unit test of the placer
  asserts the same invariant - added under this feature where missing, red-green; the check's segment,
  tests and fixtures are then removed. No check is exempt by category.
- **FR-003**: A check MUST stay when a later stage changes its inputs, or when a consumer's behavior
  branches on its verdict; the ledger names the reason, and a check kept for (c) being unmet is named
  as such (the GM may cut it).
- **FR-004**: For every kept check pinned only by hand-era fixtures, a scripted negative fixture MUST
  replace them, or the ledger MUST say why one cannot be made (and the hand-era fixture then stays, named).
- **FR-005**: The legacy tiers' fixtures and checks MUST be presented to the GM as a choice with numbers
  (User Story 3) and handled as the GM rules at acceptance; until the ruling they run exactly where they
  run today.
- **FR-006**: The doctrine MUST be rewritten (User Story 4), quoting the GM.
- **FR-007**: Zero regressions on the maps: every live map's verdict set (the checks it passes and fails)
  is unchanged for the kept checks before and after; `make done` green.
- **FR-008**: The feature MUST end with the explanation (User Story 5) and MUST NOT land before the GM's
  recorded acceptance; tasks the GM adds at acceptance are worked under this feature.

## Success Criteria

- **SC-001**: the ledger covers every check name in the registry (636): a measured verdict for the 231
  the scripted tier exercises, a class verdict with counts for the other 405; no retirement without its placer
  test named.
- **SC-002**: the gate's check count and corpus size before/after are reported, with the gate's
  test-phase seconds; every retired check's guarantee is named in a placer test.
- **SC-003**: `make done` green; no live map's kept-check verdicts change.
- **SC-004**: the GM's acceptance recorded verbatim.

## Assumptions

- "The placement algorithm guarantees" is read per STAGE: a guarantee holds from the stage that
  places the thing until a later stage touches its inputs; the per-stage snapshot is how that is measured
  rather than assumed.
- The scripted hamlet tier is the live path; the audit's retirements act on checks that run there. The
  legacy tiers are the GM's choice at acceptance (FR-005).
- Deleting a check deletes code; a check needed again when a tier converts is recovered from history,
  named in the ledger.
