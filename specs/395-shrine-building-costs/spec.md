# Feature 395: What a small forest shrine cost to build (issue #6)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future." (gm-assistant filed #6 at the GM's request, and announced it on #3 as pre-approved because the GM asked for it.)

**Input**: `request.md` (EliAndrewC/diagram#6 and its comments, verbatim)

## Why

The GM's players are commissioning a small forest shrine, and the GM's session on Monday 2026-10-19 at 7 pm needs grounded
prices for it (request.md). gm-assistant's shrine builder priced it from estimates. The four search passes (`passes/`)
found Edo-period figures for the sanctuary, the roof, the stone and earthwork, and the rites, and those figures were posted
on the issue as interim findings on 2026-10-18. This feature writes them into the record, with checks, so the skill can
cite them.

## User Scenarios & Testing

### User Story 1 - The skill can cite each shrine figure (Priority: P1)

The gm-assistant session finds four money questions answering #6's four questions, each with quoted, checked sources.

**Acceptance Scenarios** (for each figure the request names: ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or
SILENT):

1. **Given** the sanctuary question, **When** it is read, **Then** it gives:
   - **A new build's cost:** ATTESTED ONLY FOR a larger sanctuary. The 1841 Shibasaki one-bay sanctuary had a 6-shaku
     bay, a cusped gable and carved panels; its contract went for over 30 ryō against bids of 50-80, with timber and
     carvings paid outside it.
   - **A new build's carpenter-days:** SILENT.
   - **Its materials share:** SILENT. The repairs' shares (1749, 1805, Mitake 1764-70) are ATTESTED ONLY FOR repairs.
   - **Repair craftsman-days:** ATTESTED ONLY FOR the 1749 Kasuga repair (187 carpenter and sawyer days, plus 24 roofer
     days).
   - **Hokora:** SILENT.
2. **Given** the roof question, **When** it is read, **Then** it gives:
   - **Copper:** ATTESTED ONLY FOR one 1749 re-roofing within a larger repair (43 ryō 1 bu, materials 53.1%) and for
     copper roof tiles on a daimyo mansion.
   - **SILENT:** cypress bark, shingle, roofer-days per tsubo, persimmon tannin, and the roof area of a ~4-shaku-bay
     sanctuary.
3. **Given** the torii, stone and earthwork question, **When** it is read, **Then** it gives:
   - **Clearing and earthwork:** ATTESTED ONLY FOR castle-scale earthwork, Osaka 1620s (per tsubo of earth, beside day
     wages). Felling and a burial mound are SILENT.
   - **Stone-hauling wages:** ATTESTED ONLY FOR 1620 Osaka.
   - **Porterage of stone per load per ri:** SILENT for a stone-specific rate. The pack-horse load of stone is attested;
     the record's pack-horse (dachin) rates may apply, which no source says.
   - **A torii:** a wooden torii is SILENT; a great stone torii is ATTESTED ONLY FOR one case, as an upper bound.
   - **SILENT:** posts, stepping stones and mason-days.
4. **Given** the rites question, **When** it is read, **Then** it gives:
   - **Consecration:** ATTESTED ONLY FOR installing a branch Inari spirit (the Fushimi Inari schedules, before 1864 and
     1864, and the grades chosen). A local priest's or monk's payment for a shrine transfer, an eye-opening or a
     consecration is SILENT.
   - **SILENT:** the ground rite, depositing remains, the bell and rope, the plaque, and the offering table.

Each figure is set beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them. Where none does, the question says that wage is SILENT and names the nearest wage it has, with its
place and its gap in years. A figure the project computed (a per-day equivalent, a reading of a contract as days) is
labeled as the project's arithmetic. It does not stand as the answer to a question the asker has since re-priced.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#6 names each question's fragment FILE, a verdict per figure, and what is still open.

## Requirements

### Functional Requirements

- **FR-001**: Four questions MUST be written in the money section, tagged `money` first, with no drawing pages.
- **FR-002**: Each MUST pass the record's checks: source-reader, quote-check, translation-check, record-format,
  intro-check, and source-applicability on each new source.
- **FR-003**: The feature MUST close `make impl-check` with a "no code implements it" line per question.
- **FR-004**: The answer on EliAndrewC/diagram#6 MUST follow `research/money-requests.md`.
- **FR-005**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The four questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004, FR-005): The issue's answer names all four fragment files and a verdict for every figure.

## Assumptions

- The interim findings already posted on the issue cover the GM's Monday session; this feature makes them citable.
- #7 (the builder's other options) is a separate feature.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 3 items.**
  - The four scenarios now list every figure the request names, each with its verdict and limit.
  - The wage line holds every figure to a matched wage, or to a stated silence and the nearest wage.
  - The approval note no longer quotes words that are not on #6.
- **spec-fidelity-verify round 2 (2026-10-19): FAITHFUL.**
