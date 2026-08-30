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
or a code-completeness test. That is the GM's proposal restated in this engine's terms. **The three-way
reading above is this session's opinion, offered because it was asked for - it is NOT the axis this feature
sorts checks on.** The GM asked to decide the firing checks case by case, and the requirements below keep
that decision theirs (FR-009).

**One caution, stated once and then built around.** "Never fires" is not by itself a safe retirement test,
and this repository has been burned by it twice in recorded incidents: an *"EXCUSE clause keyed on PRESENCE
cannot fire on ABSENCE"* (four instances in one day), and *"the check PASSES on the very artifact it was
written for"*. A check that never fires is what a working check looks like AND what a neutered check looks
like. So the census's own answer is VERIFIED before it is acted on: FR-006 puts one read of the placer and
the record behind each candidate, and that read can only correct the census (evidence that the current
placer is missed reclassifies the check FIRING) or confirm it. It does NOT substitute a different test for
the one the GM named - the test stays "does it fire against the current implementation", which is exactly
what was asked for. Feature 141's `make check-census` measures a related but different thing (which stage
last changes an input), and it earns its place in the FR-009 ledger rather than in the deletion decision.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete the checks that never fire (Priority: P1)

The GM wants the dead weight gone first, before any architectural argument. A session runs a census over
every live gate check and asks, by EXECUTION rather than by reading, whether anything the engine can
PRODUCE TODAY makes that check emit a FAIL - a live pool map, a map the current generators can roll, a
scripted negative fixture built from today's placers, or a recorded miss of the current placer. Evidence
that exists only as a frozen hand-era manifest of a shape no generator can produce is not the current
implementation firing (FR-003). A check for which the answer is "no" is deleted, along with its segment
body, its tests, its fixture entries and its pin.

**Why this priority**: It is the GM's stated first task, it is self-contained, and it needs no ruling from
anyone - a check that cannot be shown to fire anywhere is not load-bearing by construction.

**Independent Test**: Run the census, delete the named checks, and confirm the gate is still green on all
five live hamlets and every pool render compared byte-for-byte. Removing an audit should change no
geometry, so any render diff is diagnosed before the deletion lands.

**Acceptance Scenarios**:

1. **Given** the 152 live check names, **When** the census runs, **Then** every name is classified as
   FIRES (with the artifact or test that makes it fire named) or NEVER-FIRES, with no name unclassified.
2. **Given** a NEVER-FIRES check, **When** its segment, tests, fixture entries and pin are deleted,
   **Then** `make done` is green and every pool render is compared byte-for-byte, any diff diagnosed.
3. **Given** a check the census calls NEVER-FIRES, **When** its placer is read and the record grepped,
   **Then** either evidence is found that the CURRENT placer misses it - in which case it is reclassified
   FIRING with that evidence and routed to the ledger - or it is deleted. A placer that merely declines
   rather than guarantees is not evidence and does not save the check.
4. **Given** the census output, **When** a reader asks why a specific check was deleted, **Then** the
   ledger names the evidence that was looked for and not found.

---

### User Story 2 - Measure every surviving check for the GM's discussion (Priority: P2)

With the dead checks gone, every check that DOES fire is MEASURED - which stage last changes each of its
inputs, what its placer guarantees, who besides the gate reads its verdict, what the record shows it has
caught - and the evidence is stated against the GM's own two readings: a bug in the placement algorithm, or
fold it into a trial-and-error placer. The ledger assigns no category and reaches no verdict, so the GM can
hold the case-by-case discussion they asked for against evidence rather than against a session's sort.

**Why this priority**: The GM explicitly named this as the step after the deletion, and explicitly said it
is *"a discussion we should stop and have before any changes like that are made"*. So the deliverable here
is EVIDENCE, not a change and not a decision.

**Independent Test**: The ledger exists, covers every surviving check, and each row carries the measurement
and the evidence for each of the GM's two readings rather than an assertion or a category.

**Acceptance Scenarios**:

1. **Given** the surviving checks, **When** the measurement runs, **Then** every one of them has a row
   carrying its measurement, and no row assigns the check to a category.
2. **Given** a check whose measurement shows a later stage can invalidate an earlier stage's work, **Then**
   the ledger NAMES that stage, because that is the fact the GM's discussion turns on.
3. **Given** a check the measurement fits neither of the GM's two readings, **Then** the ledger records
   "neither, because X" as an observation for the discussion rather than forcing it into a reading.
4. **Given** the finished ledger, **When** the session reports to the GM, **Then** no placer has been
   changed, no check has been folded into one, and no check has been assigned a disposition.

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

- **A check that looks legacy-tier.** Some checks read as belonging only to town / city / capital /
  village maps, and feature 158 deleted the frozen exhibits that were the only artifacts at those tiers -
  *"there is no reason to see what would happen if we encountered a type of map, which is literally
  impossible to produce any longer"*. **A check's tier is ESTABLISHED BY READING ITS GUARD, never by
  inference from its name or by subtracting one list from another**, and this spec got that wrong twice
  before the review caught it: `ways_clear_of_castle_moat` carries NO scale guard at all (it is DATA-gated
  on castle-moat records and iterates lanes, so any manifest with a moat and a way fires it - the classic
  `dev/gate.md` "a check that never RUNS looks exactly like a check that passes" shape), and
  `village_has_no_headman` is a VILLAGE-scale check that `roll_village` is a live mixin for, whose sibling
  `village_has_kosatsuba` is already made to fire by a three-line hand-built manifest in the tree today.
  So there is no pre-approved class deletion: every candidate takes the FR-006 placer read, and a group is
  formed only from candidates whose guards have each been read and whose tier has no live generator.
- **A check whose only firing evidence is a frozen manifest of a map no generator can produce.** The
  fixture proves the check has teeth against a shape the engine can no longer make - which is not the
  current implementation firing, and the census classifies it apart on exactly that ground. Under the GM's
  2026-08-30 amendment to FR-003 that classification does NOT delete it: the row goes to the FR-009 ledger
  for the case-by-case discussion, like every other check that still fires.
- **A check that fires only inside another check's fixture** (a fixture pinned to check A also trips
  check B). Incidental firing IS firing under FR-001 and the check is not a deletion candidate: whether it
  EARNS ITS KEEP is FR-009's question and therefore the GM's, in the discussion. The census records the
  firing as incidental so the ledger can say so; it never converts "incidental" into "delete".
- **A meta check that cannot be run in isolation.** `META_CHECKS` (`waivers_are_live`,
  `waivers_are_documented`) raise rather than run under `gate(M, only=...)`, so the census must reach them
  through a full gate run or they will be silently unmeasured - the exact failure mode `dev/gate.md`
  records under "A check that never RUNS looks exactly like a check that passes".
- **The census returning an empty set.** A census that finds nothing is indistinguishable from a clean bill
  of health. It must assert it found something, and must be shown to name a check that is known to fire.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The census MUST define "fires" against the CURRENT implementation, per the GM's own
  qualifier (*"do not appear to ever actually fire with our current implementation"*, *"not catching
  anything in this exact moment"*): a check FIRES when something the engine can PRODUCE TODAY makes it
  emit a FAIL (or a WAIVE, which is a suppressed FAIL) - a live pool map, a map the current generators can
  roll, a scripted negative fixture built from today's placers, or a recorded miss of the current placer.
  Passing on every map is not firing. **A hand-BUILT manifest in a test is recorded as evidence too, and
  classified apart**: this repository's established way of exercising a check no live generator reaches is
  a small hand-built manifest (`dev/gate.md`), so a check that only such a manifest makes fail has proven
  TEETH without proving the current implementation produces the fault. It is not deleted on the census's
  word; it goes to the FR-006 placer read like every other candidate.
- **FR-002**: The census MUST establish each verdict by EXECUTION - running the gate against the artifact
  and reading the verdict - not by grepping for the check's name. A name appearing in a test file is not
  evidence that the test makes the check fail.
- **FR-003**: The census MUST cover all five sources of a verdict: the live pool maps, the frozen negative
  fixtures in `pool/regressions/`, the scripted negative fixtures, waivers declared on shipped maps, and
  any test that asserts a check fires. **A frozen manifest of a shape the current generators cannot
  produce is not the current implementation firing**, and the census must CLASSIFY it apart from evidence
  that is - the repository has already ruled this way on this exact subject: `bridges_align_with_their_way`
  was retired because *"every scrap of evidence for it was two decks a person placed BY HAND on maps no
  generator can produce"* (`dev/gate.md`).

  **AMENDED BY THE GM, 2026-08-30 (`gm-request.md`): hand-era-only evidence is NOT a deletion criterion.**
  This clause used to end "...is NEVER-FIRES and is deleted WITH that fixture". Measured, that would have
  put 103 of the 152 checks on the block, and the session's recommendation - which the GM accepted with
  *"go"* - was that "has anything made this fail lately" is the right test for finding DEAD code and the
  wrong test for everything else. The classification stays, because it is a real distinction the ledger
  reports; the DISPOSITION changes: a `FIRES-HAND-ONLY` check goes to the FR-009 ledger for the GM's
  case-by-case discussion, exactly like a `FIRES` one. Only a check nothing at all makes fail is a
  deletion candidate, and even that one takes the FR-006 placer read first.
- **FR-004**: The census MUST classify every live check name, leaving none unclassified, and MUST fail
  loudly rather than return an empty or partial result.
- **FR-005**: The census MUST be proven to work by naming at least one check that is independently known
  to fire, and by a guard that goes red if the census silently classifies nothing.
- **FR-006**: Before a NEVER-FIRES check is deleted, its placer MUST be read and the record grepped for
  what the check has actually caught, and the finding recorded per check. This is VERIFICATION OF THE
  CENSUS, not an appeal against the deletion, and it has exactly **two** outcomes:
  - **Evidence found** that the check has caught, or can be made to catch, the CURRENT placer - a recorded
    miss in the code or the record, a live map, a scripted negative fixture, a waiver. The census verdict
    was WRONG: the check is reclassified **FIRING**, the evidence recorded, and it goes to the FR-009
    ledger for the GM's discussion. (The worked precedent is `bridges_span_their_water`, which the
    mechanical census called retire and `hamletgen/ways.py` records catching the scripted placer four
    separate times.)
  - **No such evidence** - it is deleted, per the GM's first task.

  There is no third outcome. In particular, a placer that fails SOFTLY - declining a placement rather than
  guaranteeing correctness - does NOT by itself save a check that has never caught anything: a runtime
  safety net standing behind a placer that might be wrong is precisely the architecture the GM says does
  not need to exist. (Feature 158's "the census's verdict is a candidate, not a ruling" licenses the
  investigation; it does not license a keep.)
- **FR-007**: Deleting a check MUST remove its segment body, any helper whose chain reaches no other live
  check, its entry in the name pin, its tests, and any frozen fixture whose only purpose was that check.
  (Feature 146: stubbing the call is not removing the check.)
- **FR-008**: After the deletions, the gate MUST be green on all five live hamlets, and every pool render
  MUST be compared byte-for-byte against before. Removing an audit should change no geometry, so a render
  diff MUST be DIAGNOSED before the deletion lands. Once its cause is understood the deletion stands and
  the map is allowed to move - the GM's standing ruling is *"I do not require any of these maps to
  maintain bite identity now or at any time"* (feature 141).
- **FR-009**: The feature MUST produce a ledger covering every SURVIVING check that RECORDS THE
  MEASUREMENT rather than assigning a category: which stage last changes each of its inputs, what its
  placer actually guarantees, who besides the gate reads its verdict, and what it is recorded as having
  caught. Against that measurement the ledger states the GM's own two readings - **a bug in the placement
  algorithm**, or **fold it into a trial-and-error placer** - with the evidence for each, and may record
  "neither, because X" as an observation where that is what the measurement shows. The DECISION is the
  GM's, case by case, in the discussion they asked for; this feature supplies the evidence, not the
  verdict.
- **FR-010**: The feature MUST NOT change any placement algorithm, fold any check into one, or convert any
  check into a unit test of a placer. Those changes are blocked on the GM's discussion, per the request.
*(FR-011 and FR-012 were removed at spec review: recording the gate's wall-cost, and building the census
to a reusable standard, are both things the GM did not ask for - and FR-012's justification rested on User
Story 3, which this spec correctly declares blocked. If the cost number falls out for free it is reported
in the wrap-up; if the census extends `make check-census` rather than a throwaway script, that is an
implementation note in the plan.)*

### Key Entities

- **Check**: one named rule in the gate battery (152 live names today), implemented by one or more
  registry segments.
- **Firing evidence**: an artifact-plus-verdict pair showing a named check emitting FAIL or WAIVE.
- **Census ledger**: one row per check - name, firing evidence (or its absence), the placer read, and
  the outcome (FIRING with its evidence, or DELETED).
- **Measurement row**: for a surviving check - which stage last changes each input, what the placer
  guarantees, who reads the verdict, what it is recorded as having caught - and the evidence for each of
  the GM's two readings. It carries no verdict; the verdict is the GM's.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the 152 live check names carries a census verdict with named evidence; zero are
  unclassified.
- **SC-002**: Every check the census calls NEVER-FIRES is either deleted, or reclassified FIRING with the
  recorded evidence that the CURRENT placer misses it - none survives on the strength of a placer that
  merely declines, and none is left in the battery unexamined.
- **SC-003**: After the deletions the gate is green on all five live hamlets, and every pool render is
  either byte-identical or its diff is diagnosed in writing with the cause.
- **SC-004**: The ledger covers 100% of surviving checks; each row states the measurement and the evidence
  for the GM's two readings, and no row asserts a decision.
- **SC-005**: No placement algorithm changed in this feature; the diff touches checks, their tests, their
  fixtures and the census tooling only.

## Decisions Recorded

This feature changes no drawn output - no glyph, size, placement rule, distance or density. Deleting a
check removes a rule from the AUDIT, not from the map: FR-008 requires every pool render to be compared
byte-for-byte and any diff diagnosed, which is the proof. The section is kept rather than deleted so the spec review
can see the judgment was made rather than skipped.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| none - no rendering decision is made or changed | n/a | the feature retires audit code; FR-008 compares every render byte-for-byte and diagnoses any diff | this row |

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
- **The GM's discussion gates User Story 3.** This feature is complete, and lands, with the measurement
  ledger delivered and no placer touched.
- **No map is expected to move**, because removing an audit should not change what a generator draws -
  the one check that steers a generator is `farmhouses_reach_a_way`, which drives the re-roll ladder and
  is not a deletion candidate. If a map moves anyway the cause is diagnosed (FR-008) and then the map is
  allowed to move, per the GM's standing ruling.

## Review history

### Round 1 - `spec-fidelity`, 2026-08-30: CHANGES REQUIRED, all six applied

Reviewed against [`gm-request.md`](gm-request.md) verbatim (constitution XVI). The reviewer confirmed the
blocked-User-Story-3 boundary as the most faithful part of the spec, and found six ways the draft
preserved what the GM asked to remove or added what they did not ask for. Every one is accepted:

| # | finding | change made |
|---|---|---|
| 1 | **FR-006's keep-clause was a carve-out contrary to the request.** *"A soft-failing placer with no recorded catch is a check that catches nothing"* - and preserving it on the grounds that the placer might be wrong is exactly the runtime safety net the GM says need not exist. Word-plausible, purpose-fatal, and the branch a session under deletion pressure reaches for. | FR-006 keeps its INVESTIGATION and loses its disposition: two outcomes only - evidence of the current placer being missed reclassifies the check FIRING, otherwise it is deleted. US1 scenario 3 and SC-002 rewritten to match. |
| 2 | **FR-001/FR-003 dropped the GM's qualifier "with our current implementation".** A frozen hand-era manifest is not today's engine firing, and `bridges_align_with_their_way` was already retired on that exact reasoning. | FR-001 defines firing against what the engine can produce today; FR-003 makes frozen-fixture-only evidence NEVER-FIRES and deletes the fixture with the check. The edge case becomes a rule applied rather than a question parked. |
| 3 | **FR-009 substituted a session taxonomy for the GM's case-by-case decision.** Sorting checks into three invented dispositions - and removing a whole class as "not about a map" - decides before the discussion the GM asked to have. | FR-009 now records the MEASUREMENT and states the GM's own two readings with their evidence; no check is assigned a category. The three-way reading stays in "The session's view" as opinion, explicitly labeled as not the axis the feature sorts on. Key Entities and SC-004 updated. |
| 4 | **FR-011 (gate-cost recording) was unrequested.** | Removed with SC-005. The number is reported in the wrap-up if it falls out for free. |
| 5 | **FR-012 (reusable census tooling) was unrequested**, and its justification rested on blocked User Story 3. | Removed. Reuse is an implementation note in the plan, not a requirement. |
| 6 | **FR-008's "a render diff is not an accepted change" contradicted a standing GM ruling** - *"I do not require any of these maps to maintain bite identity now or at any time"* (feature 141). | The byte comparison stays as a diagnostic that must be explained; the absolute is dropped. Maps may move once the cause is understood. |

The reviewer also passed on an aside for the GM: the three-way reading of the battery is *"a genuinely
useful frame and worth hearing at the discussion - it just should not be built into the specification as
the axis the checks get sorted on before that discussion happens."*

### Round 2 - independent re-review, 2026-08-30: CHANGES REQUIRED, all applied

Round 2 was pointed at the exact failure this project's review procedure exists to catch: *"a Review
history that claims a change the FRs do not carry"*. It confirmed all six round-1 changes landed **in the
FR bodies** and found that three sections had been skipped when they were propagated, plus a factual slip.

| # | residue | change made |
|---|---|---|
| C1 | **User Story 2 was entirely un-updated** and still required the sort FR-009 forbids - its acceptance scenario 1 still read *"each is in exactly one of the three dispositions"*, the precise phrase round 1 ordered dropped. *"An implementer works from acceptance scenarios. As it stands the spec's scenarios require the sort its FR forbids."* | US2 retitled and rewritten end to end onto the measurement frame, with a fourth scenario for the "neither, because X" case and a scenario asserting no check is assigned a disposition. |
| C2 | US1 acceptance scenario 2 still carried the byte-identity absolute. | Restated as compared byte-for-byte with any diff diagnosed. |
| C3 | The US1 body still defined firing as *"anything in the repository"*, without the current-implementation qualifier. | Aligned with FR-001/FR-003, naming the frozen-hand-era case explicitly. |
| C4 | The rationale paragraph in "The session's view" now argued AGAINST the corrected requirements - it said the distinguishing question *"is not 'has it fired'"*, when after correction that is exactly the spec's test. *"This is the paragraph a future session reads for the why."* | Reworded: the placer read VERIFIES the census (FR-006's two outcomes), it does not replace its test. `make check-census` earns its place in the FR-009 ledger, not in the deletion decision. |
| C5 | **A factual slip that would have licensed deleting three live-tier checks unverified.** The edge case said NINE legacy-tier checks cannot be made to fire; `research.md`, `plan.md` and T11 all say six. The other three - `farmhouse_aspect_in_range`, `stream_end_anchored`, `stream_source_anchored` - are HAMLET-tier and the live generators run them on every roll. | Corrected to six, and the three hamlet-tier names routed through the ordinary FR-006 placer read like any other candidate. |
| plan | Two residues of the same defect one level down: the Summary's *"by anything in this repository"* and the Constitution Check's *"FR-008's byte-identical render check"*. | Both corrected. |

Round 2 also answered the two questions it was asked to press on: the corrections did NOT over-swing
(*"FR-003 is faithful, not over-broad"* - FR-006's first branch is a real escape hatch and the cited
precedent runs both ways), and the stop holds (*"FR-010, US3, US2 scenario 3, SC-005, tasks T17 and the
'Blocked' section all close the same door. Faithful."*).

### Round 3 - independent re-review, 2026-08-30: CHANGES REQUIRED, all applied - AND ESCALATED

Round 3 confirmed every round-2 item landed, confirmed the GM-facing contract (census by execution,
delete what does not fire, measure the rest, stop before touching a placer) has held since round 1 and
survived two adversarial passes, and found four more defects. All four are applied:

| # | finding | change made |
|---|---|---|
| F1 | **The "six legacy-tier checks" group was obtained by ARITHMETIC, never by reading a guard - and it was wrong in composition and in claim.** `ways_clear_of_castle_moat` carries NO scale guard at all: it is DATA-gated on castle-moat records and iterates lanes, so any manifest with a moat and a way fires it - the classic `dev/gate.md` "a check that never RUNS looks exactly like a check that passes" shape, not a tier casualty. And `village_has_no_headman` sits at a scale `roll_village` still serves, whose sibling `village_has_kosatsuba` is already made to fire by a three-line hand-built manifest in the tree. T11 would have deleted a check under a false premise, bypassing FR-006. | The pre-approved class deletion is GONE. A check's tier is established by READING ITS GUARD; a group may be formed only from candidates whose guards have each been read and whose tier no live generator reaches, and the grouping presents individually verified verdicts rather than substituting for T08's read. Applied in the spec's edge case, `plan.md` Phase 2 and T11. |
| F2 | **FR-001 and FR-003 disagreed about the hand-BUILT manifest.** FR-001's list omitted it while FR-003 counted "any test that asserts a check fires" - so the census could call NEVER-FIRES a check a test in the tree demonstrably makes FAIL. | FR-001 now records a hand-built manifest as evidence and classifies it APART: proven teeth, unproven that the current implementation produces the fault, so it goes to the FR-006 read rather than to deletion. |
| F3 | `research.md` still cited FR-011 and the old SC-005, both removed at round 1. Neither earlier round read that file. | Corrected. |
| F4 | The "incidental firing" edge case read as a route to delete a check that demonstrably fired - *"the mirror of round 1's finding 1"*. | Separated: incidental firing IS firing under FR-001 and is never a deletion candidate; whether it EARNS ITS KEEP is FR-009's question and therefore the GM's. |

**ESCALATION RESOLVED BY THE GM, 2026-08-30.** Asked what was waiting on them, the GM answered *"go"* -
which covered both the escalation and the FR-003 deletion criterion (`gm-request.md`). The feature
proceeded from T09. The record of what the procedure cost and bought is below, unchanged.

**ESCALATED, per constitution XVI.** The procedure is three rounds, then stop and escalate rather than
attempt a fourth. That is what this feature is doing: the fixes above are applied, and **implementation of
the DELETION (T08-T13) is held until the GM rules.** The reviewer's own qualification is recorded here
because it is what the GM is being asked to weigh: *"F1-F4 are not a persistent misunderstanding of the
request. The GM-facing contract ... has been faithful since round 1's corrections and survived two
adversarial passes. F1 is a factual error about the codebase, discoverable by reading four segment guards;
F2 an internal inconsistency between two FRs; F3 a stale cross-reference; F4 a clause. All four are
mechanical corrections with no judgment call in them, and none reopens a decision either earlier round
settled."*

What the three rounds cost, and what they bought, since that is the honest measure of the procedure: they
caught one carve-out contrary to the GM's instruction (round 1, FR-006 - which this session had itself
flagged as a suspected carve-out), one whole user story left carrying the requirement its own FR forbade
(round 2, C1), and two factual claims about the codebase that would each have deleted a live check on a
false premise (round 2 C5, round 3 F1). Every one of the four would have reached the implementation.
