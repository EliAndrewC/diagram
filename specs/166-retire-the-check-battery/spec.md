# Feature Specification: Retire the post-placement check battery

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=166-retire-the-check-battery`)

**Created**: 2026-08-30

**Status**: Draft

**Input**: The GM's requests, verbatim, in [`gm-request.md`](gm-request.md). Summarized: *"Get rid of check
village."* Feature 163 asked which checks still fire; its ledger forced the conclusion that the battery
should not exist. The GM's test - *"can you describe to me a single category of automated check which
should still exist?"* - could not be answered.

## Why this is not a judgment call

The measurement that settles it, taken before the GM ruled: **116 of the 116 checks feature 163 classified
"fold into a trial-and-error placer" have a NAMED last-touching stage. Zero are ownerless.** That bucket's
whole justification had been *"no unit test of the placer can carry the guarantee"*, and it was false - the
placer feature 163 NAMED could not, but the stage that last writes a feature can, and that stage is a
placer. As the GM put it: *"if a canopy is in the wrong place, that definitionally means that a placer put
it in the wrong place."*

And **17 of the 20 checks in the "neither" bucket read no manifest key at all** - they are assertions about
the CODE (a feature type added without a registry entry), testable without drawing anything.

So every one of the 147 has a destination that is not a per-map check. What separates a check from a test
here is not content but WHEN IT RUNS: once per code change over a representative seed set, instead of once
per map generated, for ever.

## What the GM's premise got wrong, and why it matters here

The GM asked *"check village is performed for both hamlets and villages, and, therefore, this is the one
that we will get rid of now. Right?"* Measured: **`check_village` is the ONLY Mode B checker, for every
tier. 307 of its 353 segments carry no scale guard at all**; 9 are city/capital-only, 2 town-and-up. The
live pool is 5 hamlets and ZERO villages. There is no separate town or provincial-city battery to retire
later - when those tiers are scripted their rules are written directly as placer tests, and a battery is
never built again.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The generator stops depending on the gate (Priority: P1)

`hamletgen.generate` runs `gate()` in-process on every roll and the re-roll ladder READS ITS VERDICT: it
parses the printed output for `farmhouses_reach_a_way` failures to learn which seats stranded a farmhouse,
and its accept criterion is that the whole failure list got no longer. Nothing can be deleted until that is
cut, so this is first and it is the only part that can change what a map looks like.

**Why this priority**: it is the one dependency that makes deletion possible, and the one place where
getting it wrong moves maps.

**Independent Test**: the generator rolls every live hamlet with no import of `check_village`, and the five
manifests are compared byte-for-byte against before.

**Acceptance Scenarios**:

1. **Given** `hamletgen`, **When** the re-roll ladder runs, **Then** it obtains stranded seats from a
   predicate it owns, not by parsing gate output, and imports nothing from `check_village`.
2. **Given** the ladder's accept criterion (today: the gate's failure list got no longer), **When** it is
   replaced, **Then** what replaces it is stated in the code with its reasoning, because a global quality
   proxy is being exchanged for a local one and that is a real change, not a refactor.
3. **Given** the five live hamlets, **When** they are re-rolled, **Then** each manifest is compared
   byte-for-byte and any difference is DIAGNOSED before the feature proceeds - maps are allowed to move
   (the GM's standing ruling), but not silently.

---

### User Story 2 - Every rule reaches its destination before its check dies (Priority: P1)

Each of the 147 live checks is classified to a destination, its replacement is WRITTEN and PROVEN TO FIRE,
and only then is the check deleted. The destinations:

- **a unit test of the placer that owns it** - the bulk; the owning placer is the stage that last writes
  the feature, which feature 163 measured for all 147;
- **a seed-sweep integration test** - whole-map properties no single placement can carry (acreage against
  households, no large empty space);
- **a static test over the code** - the 17 completeness ratchets, which read no manifest key;
- **deliberately dropped, with a recorded reason** - redundant with a test the placer already has, or
  belonging to a tier no generator can produce.

**Why this priority**: this is the feature. Deleting 147 rules and keeping nothing is the failure mode, and
the ordering (replacement first, proven, then deletion) is the only thing that prevents it.

**Independent Test**: for any deleted check, the record names either the test that now carries its rule and
the run in which that test was seen to FAIL without the fix, or the reason it was dropped.

**Acceptance Scenarios**:

1. **Given** a check with a placer, **When** its replacement unit test is written, **Then** that test is
   proven to FAIL against the unfixed placer before the check is deleted - the project's standing rule that
   a guard is proven by watching it go red.
2. **Given** a check whose rule is already covered by an existing placer test, **Then** it is dropped with
   the covering test named, not silently.
3. **Given** a check for a tier no generator can produce, **Then** its RULE is preserved as a record and
   its code is deleted - the trade feature 158 already took.
4. **Given** the finished migration, **When** the record is read, **Then** every one of the 147 has exactly
   one recorded destination and none is unaccounted for.

---

### User Story 3 - The battery and its apparatus are gone (Priority: P2)

`l7r/diagram/check_village/` (14,483 lines, 353 segments), `tests/check_village/` and `tests/gate/`
(7,464 lines), the 105 frozen negative fixtures in `pool/regressions/`, the gate's Makefile targets and
its `_invocation` registration all go, along with the pool sweep that runs the battery over every map.

**Independent Test**: nothing in the tree imports `check_village`; `make done` is green; the gate's phases
are gone from it.

**Acceptance Scenarios**:

1. **Given** the tree after deletion, **When** it is searched, **Then** no module, test, generator, tool or
   Makefile target references `check_village`.
2. **Given** `make done`, **Then** it no longer runs a per-map battery.

---

### Edge Cases

- **The re-roll ladder's accept criterion is a GLOBAL proxy.** Today a re-roll is kept only if the gate's
  whole failure list got no longer - so the ladder is using the battery as a general quality signal, not
  just as a reach test. Replacing it with the reach predicate alone is a behavior change and may move maps.
  It is US1's central question and must be answered in writing, not slipped in.
- **A check whose rule the placer cannot enforce because it cannot SEE the constraint.** If found, it is a
  finding about the placer's inputs, not a reason to keep a check: the fix is to give the placer what it
  needs. Any instance is recorded, because it is the one shape that would genuinely argue against this
  feature and none was found in feature 163's ledger.
- **A research finding whose only operative statement is a check body.** The finding is written into
  `research/` before the code goes. The rule survives; the runtime check does not.
- **The 105 frozen fixtures are bad MAPS, not tests.** They exist to prove checks have teeth. When the
  checks go they have nothing to prove, and feature 158 already set the precedent for deleting a corpus
  whose tier no generator can produce.
- **Coverage floors.** `check_village` is currently exempt from the global 100% floor and its deletion
  removes ~14,000 lines from the denominator. The floors must be re-derived, not merely observed to pass.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `hamletgen` MUST NOT import or call `check_village`. The re-roll ladder MUST obtain stranded
  seats from a predicate it owns.
- **FR-002**: The replacement for the ladder's accept criterion MUST be stated in the code with its
  reasoning, and the five live hamlets MUST be re-rolled and compared byte-for-byte, with any difference
  diagnosed in writing before the feature proceeds.
- **FR-003**: Every one of the 147 live checks MUST be assigned exactly one destination - placer unit test,
  seed-sweep test, static code test, or deliberately dropped - with none unaccounted for.
- **FR-004**: A check MUST NOT be deleted before its replacement exists and has been PROVEN TO FIRE against
  the unfixed code. A check dropped without a replacement MUST record the covering test or the reason.
- **FR-005**: Where a check body is the sole operative statement of a research finding, that finding MUST be
  written into `research/` before the check is deleted.

  **This binds hardest on the URBAN rules, and per rule rather than per class** (the GM's 2026-08-30
  question, `gm-request.md`). Measured: 39 segments carry an `if URBAN:` branch, 544 lines of code and 163
  of prose, and NONE of the 39 cites where its finding is recorded. Spot-checks show the knowledge is in
  `settlements/` and `research/` and is fuller there than in the check - but one spot-check (`wall
  thickness`) came back empty, so **each urban rule MUST be confirmed to have a documented home before its
  check goes, and the confirmation recorded**. A class-level assumption is exactly what this requirement
  exists to prevent. Unlike a hamlet rule, an urban rule has no placer to migrate INTO, so the document is
  the only thing that will carry it until those tiers are scripted.
- **FR-006**: `check_village/`, its tests, the frozen fixture corpus, the gate's Makefile targets and its
  `_invocation` registration MUST be removed, and no file in the tree may reference them.
- **FR-007**: The coverage floors MUST be re-derived after the deletion, not assumed to hold. **Re-derived
  is not lowered**: the carriers that vanish covered `check_village` modules vanishing with them, so a drop
  is not expected - and if one appears anyway it is a coverage loss on code that is STAYING, which is a
  sentence to the GM, never a quiet floor reduction.
- **FR-008**: `make done` MUST be green at the end.
- **FR-009**: The feature MUST record, per deleted check, where its rule now lives - so that "what happened
  to rule X" is answerable after the code is gone.
- **FR-010**: The doctrine the GM stated for future tiers - *"I guess the same thing will later apply to
  other similar automated checks for towns and provincial cities and capital cities when we eventually
  begin to script those as well"* - MUST be recorded in an OPERATIVE doc a future session will meet when it
  goes looking for how to add a check (`dev/gate.md`, rewritten or replaced), quoting the GM's own words:
  when those tiers are scripted, their rules are written directly as tests of the placer that owns them,
  and a post-placement battery is not rebuilt.

  **Why this needs its own requirement.** The GM was picturing a LATER feature that retires a town/city
  battery. The premise correction establishes there will be no such battery - those segments die here - so
  their stated policy has no future feature to live in, and FR-006 deletes the one operative doc that
  currently teaches the opposite (`dev/gate.md`'s whole subject is "adding a check", and it instructs a
  session to write a new segment into `check_village/segments_*`). Without this, the correction quietly
  deletes the GM's forward policy along with the code.

- **FR-011**: The documentation sweep MUST remove every place the docs describe or instruct the Mode B
  post-placement battery as part of the SCRIPTED process, and MUST NOT remove Mode A's check doctrine.
  Mode A compounds are hand-authored SVG placed by a person, so their automated checks (`tools/pack_audit.py`,
  `tools/scatter_audit.py`, the 8 frozen red SVG fixtures in `tests/fixtures/`) survive on exactly the
  reasoning that retires the Mode B battery, and the GM said so: *"for nonscripted diagrams such as the
  magistracy diagrams, there still are automated checks and those serve a valuable purpose because those
  maps are generated by hand rather than by a scripted process."*

  **The sweep is per MENTION, never per file or per word.** Measured: Mode A's apparatus references
  `check_village` zero times, so no code change is implied - the whole risk is in prose, and the doc split
  is uneven enough that a blanket search on "automated check" would strip live doctrine (`dev/gate.md` is
  pure Mode B; `buildings.md` is 35 Mode A mentions to 1 battery mention; `SKILL.md` is mixed).

### Key Entities

- **Check**: one of the 147 live named rules in the battery.
- **Owning placer**: the stage that last writes the feature a check judges - measured for all 147 by
  feature 163's ledger.
- **Destination**: placer unit test, seed-sweep test, static code test, or dropped-with-reason.
- **Migration record**: one row per check - name, owning placer, destination, and the proof (the run in
  which the replacement was seen to fail without the fix, or the covering test, or the drop reason).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `l7r/diagram/check_village/` does not exist, and no file in the tree references it.
- **SC-002**: All 147 checks have a recorded destination; zero unaccounted for.
- **SC-003**: Every replacement test written for this feature has been seen to FAIL without the fix it
  guards, and that run is recorded.
- **SC-004**: The five live hamlets roll without the gate, and each manifest is either byte-identical or
  its difference is diagnosed in writing.
- **SC-005**: `make done` is green, the coverage floors are re-derived (not lowered), and the gate's
  phases are gone.
- **SC-007**: Mode A's check doctrine and its apparatus are INTACT after the sweep - `pack_audit`,
  `scatter_audit` and the 8 frozen red SVG fixtures still exist and are still documented, and no Mode A
  check mention was removed.
- **SC-006**: A session searching the tree for how to add a check finds the successor doctrine - rules go
  to the placer that owns them - not instructions for writing a new segment.

## Decisions Recorded

This feature changes no drawn output by intent - it retires audit code. The ONE place a map can move is the
re-roll ladder's accept criterion (US1), which is a genuine behavior change and is why FR-002 requires the
byte comparison and a written diagnosis rather than an assumption.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| the re-roll ladder's accept criterion changes from "the gate's failure list got no longer" to a local reach predicate | deviation - a priced trade-off, not a historical claim | the global proxy cannot survive the battery it reads; the local predicate is what the ladder was always about (`hamletgen/driver.py` records the reach measure being wrong on 5 of 6 seeds when hand-rolled, which is why it reads the gate today) | `hamletgen/driver.py` at the point of change; FR-002; US1 scenario 2 |

## Assumptions

- **"Get rid of check village" means the whole Mode B battery**, since that is what `check_village` is -
  307 of 353 segments are tier-agnostic. The GM's "hamlets and villages" premise is corrected in
  `gm-request.md`.
- **The town / city / capital rules are preserved as RECORDS, not as code.** No generator can produce those
  tiers; when they are scripted their rules become placer tests directly. This is feature 158's trade.
- **Maps may move**, per the GM's standing ruling, but only through US1 and only with the cause diagnosed.
- **This is large.** 147 rules, ~22,000 lines of code and tests, and 105 fixtures. The ordering in US2 -
  replacement first, proven, then deletion - is what makes it safe to do incrementally with the tree green
  throughout, and the feature is not complete until SC-002 shows zero unaccounted for.

## Review history

### Round 1 - `spec-fidelity`, 2026-08-30: CHANGES REQUIRED, both applied

The reviewer confirmed the scope is the target's size and not the spec's invention (*"`check_village` really
is 14.5k lines and 353 segments"*), confirmed the premise correction is faithful handling rather than a
widened mandate (*"the instruction names an artifact, not a tier set... Deleting only the hamlet/village-guarded
part would leave `check_village` in existence, which is the opposite of the instruction"*), and confirmed
US1 is forced rather than chosen (*"once the battery is gone that criterion is not merely undesirable, it is
uncomputable"*). Two findings:

| # | finding | change made |
|---|---|---|
| 1 | **FR-008's cost clause and SC-006 were unrequested - and are the SAME requirement feature 163's round-1 review already struck** (its FR-011, *"gate-cost recording was unrequested"*). The justification was also false: feature 162 removed every duration from every guard message the day before, and `tests/tooling/test_guard_message_durations.py` fails the gate if one reappears, so no guard quotes a number to update. The measurement is automatic anyway - the Makefile writes a `dev/run-log` row with `seconds` on every gate run. | FR-008 trimmed to "must be green"; SC-006 cut. The new cost, if wanted, is `scripts/_gatecost.py done` after the fact - no requirement needed. |
| 2 | **The GM's forward clause had no home, and the premise correction is what removed it.** They said the same treatment *"will later apply to other similar automated checks for towns and provincial cities and capital cities"* - picturing a later feature retiring a town/city battery. The correction establishes there will be no such battery, so the policy has no future feature to live in; and FR-006 deletes `dev/gate.md`, the one operative doc a session meets when looking up how to add a check, which currently teaches the opposite. | New FR-010 and SC-006: the successor doctrine is recorded where a future session will meet it, quoting the GM. |

**The repeat is the part worth carrying.** Finding 1 is not a new mistake - it is the identical unrequested
requirement, struck in one feature and re-added in the next by the same session, with a rationale that had
been made false by a feature that landed the previous day. Writing a requirement because it feels
responsible, rather than because it was asked for, is evidently a habit rather than a slip; the check
against it is to walk the GM's words and ask of each FR which clause it serves, before the reviewer does.

### Round 2 - `spec-fidelity`, 2026-08-30: CHANGES REQUIRED, applied

Round 2 confirmed FR-010 does not overreach (*"the doc is not new... FR-006 already forces that doc to
change, so FR-010 adds no work item, it constrains what the already-required rewrite must say"*), confirmed
every clause of the GM's two messages has a carrier and every requirement serves a clause, and found ONE
defect - the same one, in its purest form:

> US3's Acceptance Scenario 2 still reads *"...and what it costs is re-measured and recorded rather than
> assumed."* That trailing clause is the exact requirement struck in round 1 here and struck again as
> feature 163's FR-011. Acceptance scenarios in this template are operative... an implementer walking US3
> to acceptance will do the re-measurement.

**The habit, now named precisely, because three features have paid for it.** It is not "I forget to
propagate" in general. It is specifically: **when a requirement is struck, the FR and the SC get fixed and
the USER STORY'S ACCEPTANCE SCENARIO does not.** Feature 163 hit it at rounds 2 (US2 entirely), 4 (US1
scenarios) and 5 (US1 scenario 3); feature 166 hit it at round 2. The scenarios are where an implementer
actually works, so the one place the correction fails to reach is the one place it most needed to.

The countermeasure is mechanical and costs seconds: **after striking a requirement, grep the WHOLE spec for
its distinctive words - not the FR section - and assert zero hits outside quotations and the Review
history.** That sweep is now run as part of applying any finding, and its result is stated with the fix. It
would have caught all four instances.

### Round 3 - `spec-fidelity`, 2026-08-30: **FAITHFUL**

Verdict: FAITHFUL - *"Implement it. No further round is needed."* The reviewer swept the whole file rather
than the FR list for the struck cost requirement and found **zero operative hits**, confirming round 2's
fix independently of this session's own claim; walked both GM messages clause by clause and found every one
carried and every requirement serving a clause; and verified the three figures the scope rests on
(`check_village/` at 52 files / 14,575 lines, and exactly 105 `.json` fixtures in `pool/regressions/`).

**Two changes were made AFTER this verdict, and are flagged rather than folded in silently**, since a
FAITHFUL verdict is on the text that was read:

1. The GM sent a third message - recorded verbatim in `gm-request.md` - confirming the town and city checks
   should go now, and asking whether any logic in them needs converting into placement algorithms first.
   The spec already deleted them, so nothing in the mandate changed.
2. **FR-005 gained an urban clause**, driven by the measurement that answered that question: 39 segments
   carry an urban rule and none of them cites where its finding is recorded, and while spot-checks show the
   knowledge is in `settlements/`/`research/` and fuller there, one came back empty. So the confirmation is
   per rule and recorded, never per class. This narrows an existing requirement rather than adding one.

The reviewer's own aside, left as an implementation call: `pool/regressions/` also holds two non-fixture
files (`city_density_broken_nagahara.notes.md`, `mode-a-forbidden-apparatus.svg`) that "the 105 frozen
negative fixtures" does not name; whether they go with the corpus is decided at implementation.
