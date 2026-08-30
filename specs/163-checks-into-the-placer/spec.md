# Feature Specification: Retire the post-placement check battery into the placer

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=163-checks-into-the-placer`)

**Created**: 2026-08-30

**Status**: Draft

**Input**: The GM's request, verbatim, in [`gm-request.md`](gm-request.md). Summarized: the automated
checks that run after the placement algorithm are unit tests wearing the wrong clothes - paid once per
map generated instead of once per code change. A check that catches something means the PLACER is
bugged. So: census which checks never actually fire under today's implementation and delete them with
their tests; then, case by case and only after a discussion with the GM, decide which of the remaining
ones are placer bugs and which must be folded into a trial-and-error placer.

## The session's view, as asked

The GM asked *"What do you think about this rearchitecture that I am proposing? Does this make sense to
you conceptually?"* - recorded here because it is part of the record, and because feature 141's spec set
the precedent.

**Yes, and the repository has already half-conceded it.** Feature 141 acted on the GM's own earlier
ruling - *"if our placement algorithm makes overlaps impossible, then checking for overlaps later in an
automated check wastes time with no benefit"* - and cut the battery from ~1,405 segments to 595; feature
146 cut it again to 385. This request is the general form of that: not "which checks earn their keep"
but "should a post-placement audit be part of map generation at all". The answer that falls out of the
141/146/158 evidence is that it should not, and that the battery is really three different things wearing
one coat:

1. **Re-measurement of a placer guarantee.** `bridges_seat_on_water` asks whether a bridge the placer
   seated on water is on water. Nothing between the placer and the gate can move it - feature 141's census
   measured exactly that and marked it RETIRE-CANDIDATE. This is the GM's case, and the disposition is a
   unit test of the placer.
2. **A property no single placer can guarantee**, because it is a function of the finished map: a caption
   seated before the scatter crowds it, a lane web clipped after the houses land, acreage against
   household count. The GM already carved this out (*"we place a label and then later on things are added
   to the map"*). The honest reading is that this is not an audit either - it is the ACCEPT CONDITION of a
   trial-and-error placer, and it belongs inside the loop. The engine already has exactly one instance
   built this way and it works: `farmhouses_reach_a_way` drives `hamletgen/driver.py`'s re-roll ladder,
   which converges in two rounds.
3. **Engine-completeness ratchets that are not about a map at all** - `every_feature_classified_for_overlap`,
   `all_ink_is_ruled_on`, `waivers_are_live`, `matrix_debts_still_owed`. These fire when a NEW FEATURE TYPE
   is added to the engine without a registry entry. They are static properties of the code, and they are
   currently discovered by drawing a map and looking at it, which is the most expensive possible way to ask.

So the end state this feature aims at is that `check_village` stops being a validator and its 152 checks
land in one of three places: a unit test of the placer, an in-loop feasibility predicate the placer calls,
or a code-completeness test. That is the GM's proposal, and the three-way split is the thing worth agreeing
on before any of it is built.

**One caution, stated once and then built around.** "Never fires" is not by itself a safe retirement test,
and this repository has been burned by it twice in recorded incidents: an *"EXCUSE clause keyed on PRESENCE
cannot fire on ABSENCE"* (four instances in one day), and *"the check PASSES on the very artifact it was
written for"*. A check that never fires is what a working check looks like AND what a neutered check looks
like. The distinguishing question is not "has it fired" but "can anything after the placer change what it
reads" - which feature 141 already built the tool for (`make check-census`) and feature 158 already
qualified (*"the census's verdict is a CANDIDATE, not a RULING"*). This spec therefore builds the census
the GM asked for LITERALLY, and adds one read of the placer per candidate before the deletion lands
(FR-006) rather than substituting a different test for the one the GM named.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete the checks that never fire (Priority: P1)

The GM wants the dead weight gone first, before any architectural argument. A session runs a census over
every live gate check and asks, by EXECUTION rather than by reading, whether anything in the repository
can make that check produce a FAIL: a live pool map, a frozen negative fixture, a scripted negative
fixture, a waiver on a shipped map, or a test that asserts it fires. A check for which the answer is "no"
is deleted, along with its segment body, its tests, its fixture entries and its pin.

**Why this priority**: It is the GM's stated first task, it is self-contained, and it needs no ruling from
anyone - a check that cannot be shown to fire anywhere is not load-bearing by construction.

**Independent Test**: Run the census, delete the named checks, and confirm the gate is still green on all
five live hamlets with every pool render byte-identical. Deleting a check changes no geometry, so any
render diff is a defect in the deletion.

**Acceptance Scenarios**:

1. **Given** the 152 live check names, **When** the census runs, **Then** every name is classified as
   FIRES (with the artifact or test that makes it fire named) or NEVER-FIRES, with no name unclassified.
2. **Given** a NEVER-FIRES check, **When** its segment, tests, fixture entries and pin are deleted,
   **Then** `make done` is green and no pool render changes by a byte.
3. **Given** a check the census calls NEVER-FIRES whose placer is read and found to fail SOFTLY (it
   declines rather than guarantees), **Then** the check is KEPT and the reason is recorded in the ledger -
   the census produced a candidate, not a ruling.
4. **Given** the census output, **When** a reader asks why a specific check was deleted, **Then** the
   ledger names the evidence that was looked for and not found.

---

### User Story 2 - Classify every surviving check for the GM's discussion (Priority: P2)

With the dead checks gone, every check that DOES fire is classified into the three dispositions above -
placer-guaranteed, emergent-across-stages, engine-completeness - with the measurement behind each
classification, so the GM can hold the case-by-case discussion they asked for against evidence rather than
against a session's opinion.

**Why this priority**: The GM explicitly named this as the step after the deletion, and explicitly said it
is *"a discussion we should stop and have before any changes like that are made"*. So the deliverable here
is a REPORT, not a change.

**Independent Test**: The classification ledger exists, covers every surviving check, and each row carries
the measurement (which stage last changes each input; who reads the verdict; what the placer actually
guarantees) rather than an assertion.

**Acceptance Scenarios**:

1. **Given** the surviving checks, **When** the classification runs, **Then** each is in exactly one of the
   three dispositions with its measurement recorded.
2. **Given** a check classified emergent-across-stages, **Then** the ledger names the stage that can
   invalidate the earlier stage's work, because that is the fact that makes it emergent.
3. **Given** the finished ledger, **When** the session reports to the GM, **Then** no placer has been
   changed and no check has been folded into one.

---

### User Story 3 - The rearchitecture itself (Priority: P3 - OUT OF SCOPE, blocked)

Folding a check into the placer, converting one to a unit test of the placer, or fixing the placer bug a
firing check reveals. **This feature specifies none of it.** The GM's request ends by requiring a
discussion before any such change is made, so the work is named here only so the boundary is explicit.

**Acceptance Scenarios**:

1. **Given** this feature's tasks, **Then** none of them changes a placer, and the feature is complete
   without any placer change.

---

### Edge Cases

- **A check with no scripted executor at all.** Nine legacy-tier checks (`capital_has_kosatsuba`,
  `*_has_no_headman`, ...) run only on town / city / capital / village maps, and feature 158 deleted the
  frozen exhibits that were the only things at those tiers - *"there is no reason to see what would happen
  if we encountered a type of map, which is literally impossible to produce any longer"*. These cannot fire
  and cannot be made to fire; they are NEVER-FIRES.
- **A check whose only firing evidence is a frozen manifest of a map no generator can produce.** The
  fixture proves the check has teeth against a shape the engine can no longer make. The census records this
  distinction; the disposition is the GM's at acceptance, not a silent deletion.
- **A check that fires only inside another check's fixture** (a fixture pinned to check A also trips
  check B). Incidental firing is recorded as such and does not by itself count as evidence that B earns
  its keep.
- **A meta check that cannot be run in isolation.** `META_CHECKS` (`waivers_are_live`,
  `waivers_are_documented`) raise rather than run under `gate(M, only=...)`, so the census must reach them
  through a full gate run or they will be silently unmeasured - the exact failure mode `dev/gate.md`
  records under "A check that never RUNS looks exactly like a check that passes".
- **The census returning an empty set.** A census that finds nothing is indistinguishable from a clean bill
  of health. It must assert it found something, and must be shown to name a check that is known to fire.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The census MUST define "fires" as: some artifact or test in this repository causes the check
  to emit a FAIL (or a WAIVE, which is a suppressed FAIL) verdict. Passing on every map is not firing.
- **FR-002**: The census MUST establish each verdict by EXECUTION - running the gate against the artifact
  and reading the verdict - not by grepping for the check's name. A name appearing in a test file is not
  evidence that the test makes the check fail.
- **FR-003**: The census MUST cover all five firing sources: the live pool maps, the frozen negative
  fixtures in `pool/regressions/`, the scripted negative fixtures, waivers declared on shipped maps, and
  any test that asserts a check fires.
- **FR-004**: The census MUST classify every live check name, leaving none unclassified, and MUST fail
  loudly rather than return an empty or partial result.
- **FR-005**: The census MUST be proven to work by naming at least one check that is independently known
  to fire, and by a guard that goes red if the census silently classifies nothing.
- **FR-006**: Before a NEVER-FIRES check is deleted, its placer MUST be read and the record grepped for
  what the check has actually caught, and the finding recorded per check. A placer that fails SOFTLY -
  declining a placement rather than guaranteeing correctness - keeps its check, with the reason written
  down. (Feature 158: the census's verdict is a candidate, not a ruling.)
- **FR-007**: Deleting a check MUST remove its segment body, any helper whose chain reaches no other live
  check, its entry in the name pin, its tests, and any frozen fixture whose only purpose was that check.
  (Feature 146: stubbing the call is not removing the check.)
- **FR-008**: After the deletions, the gate MUST be green on all five live hamlets and every pool render
  MUST be byte-identical to before. A render diff is a defect in the deletion, not an accepted change.
- **FR-009**: The feature MUST produce a classification ledger covering every SURVIVING check, assigning
  each to exactly one of: **placer-guaranteed** (nothing after the placer changes what it reads),
  **emergent-across-stages** (a later stage can invalidate it - the ledger names that stage), or
  **engine-completeness** (it tests a registry or a declaration, not a map).
- **FR-010**: The feature MUST NOT change any placement algorithm, fold any check into one, or convert any
  check into a unit test of a placer. Those changes are blocked on the GM's discussion, per the request.
- **FR-011**: The feature MUST record what it cost the generator - the per-map wall time spent in the gate
  before and after - so the discussion in User Story 2 is held against a number rather than an impression.
- **FR-012**: The census tooling MUST be reusable, not a one-shot script that is thrown away, because the
  same question is asked again after every disposition in User Story 3 lands.

### Key Entities

- **Check**: one named rule in the gate battery (152 live names today), implemented by one or more
  registry segments.
- **Firing evidence**: an artifact-plus-verdict pair showing a named check emitting FAIL or WAIVE.
- **Census ledger**: one row per check - name, firing evidence (or its absence), the placer read, the
  disposition, and the reason.
- **Disposition**: placer-guaranteed, emergent-across-stages, or engine-completeness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the 152 live check names carries a census verdict with named evidence; zero are
  unclassified.
- **SC-002**: Every check the census calls NEVER-FIRES is either deleted or kept with a written reason
  naming the soft-failing placer that saves it - none is left in the battery unexamined.
- **SC-003**: After the deletions the gate is green on all five live hamlets and every pool render is
  byte-identical, so the change is provably behavior-preserving for the maps.
- **SC-004**: The classification ledger covers 100% of surviving checks and each row states the
  measurement, not an assertion.
- **SC-005**: The per-map gate cost is recorded before and after, so the saving from the deletion is a
  number.
- **SC-006**: No placement algorithm changed in this feature; the diff touches checks, their tests, their
  fixtures and the census tooling only.

## Decisions Recorded

This feature changes no drawn output - no glyph, size, placement rule, distance or density. Deleting a
check removes a rule from the AUDIT, not from the map: FR-008 requires every pool render to be
byte-identical afterwards, which is the proof. The section is kept rather than deleted so the spec review
can see the judgment was made rather than skipped.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| none - no rendering decision is made or changed | n/a | the feature retires audit code; FR-008 pins the renders byte-identical | this row |

Historical rules a deleted check ENCODED are a separate matter and are not lost by the deletion: the
research finding and its sources live in `research/` and in the interactive map's modals (constitution XII),
not in the check body. Any deletion that would orphan a `research/` citation records where the finding still
stands.

## Assumptions

- **"Automated checks" means the `check_village` gate battery** - the 152 live named checks over the JSON
  manifest. It does not mean the pytest suites, the guard hooks, or the review subagents.
- **The live Mode B pool is the five scripted hamlets.** The 18 frozen exhibits in
  `legacy-hand-authored-pool/` are not regenerated and are not gated (features 158/161), so a check that
  only ever fired on one of them has no live executor.
- **A deleted check's research finding survives in `research/`**, so deleting the check does not delete the
  historical rule or its sources.
- **The GM's discussion gates User Story 3.** This feature is complete, and lands, with the classification
  ledger delivered and no placer touched.
- **No map is expected to move.** Feature 141's ruling that maps may move does not apply here, because
  removing an audit cannot change what a generator draws - unless the check drives the re-roll ladder, and
  `farmhouses_reach_a_way` (the only such check) is not a deletion candidate.
