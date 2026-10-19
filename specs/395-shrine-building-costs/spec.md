# Feature 395: What a small forest shrine cost to build (issue #6)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future." (gm-assistant filed #6 at the GM's request: "he asked for it, so it is pre-approved".)

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

**Acceptance Scenarios**:

1. **Given** the sanctuary question, **When** it is read, **Then** it gives what a new small one-bay sanctuary cost (the
   1841 Shibasaki contract and its bids), the craftsman-days and cost shares of the 1749 and 1805 Kasuga repairs and the
   1764-70 Mitake repair, and the day wages of the same district and period, or what was searched and not found
   (hokora: SILENT).
2. **Given** the roof question, **When** it is read, **Then** it gives the 1749 copper re-roofing's cost and shares, and
   the copper roof tiles' price, and states cypress bark, shingle, roofer-days and persimmon tannin as SILENT.
3. **Given** the torii, stone and earthwork question, **When** it is read, **Then** it gives the 1620s Osaka earthwork rates
   and day wages, stone-hauling wages, the pack-horse load of stone, and the one large stone torii's cost as an upper
   bound, and states a wooden torii, posts, stepping stones and mason-days as SILENT.
4. **Given** the rites question, **When** it is read, **Then** it gives the Fushimi Inari installation fee schedules (before
   1864 and from 1864) and which grade most buyers chose, and states the ground rite, the deposit of remains, the bell,
   the plaque and the offering table as SILENT.

Each figure is set beside the craftsman's and laborer's day wage of the same place and period, where the record has one.

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
