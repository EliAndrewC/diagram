# Feature 390: Money foundation research (issue #1)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-18

**Status**: Done - every task ticked but the GM review (lands open); answer on EliAndrewC/diagram#1; impl-check nothing missing

**Affects**: research record

**Approved**: the GM, 2026-10-18, "I approve the Money Foundation research feature for issue one."

**Input**: `request.md` (gm-assistant's request on EliAndrewC/diagram#1, and the GM's approval)

## Why

The gm-assistant money skill converts Rokugani prices and keeps a ledger in which every figure carries a source. Four
questions underlie every other price, and the GM's notes leave them unsourced (request.md):
- **Land price against yield.** Rokugan's ~50-koku farm, at ~20 times its yearly profit, rests on nothing.
- **Unskilled day wages.** These give the laborer's year that the skill's "big deal" dollars divide by.
- **The koku of rice.** It is "about 40 gallons" in `l7r.md` but ~180 L in `budgets.md`, which moves a koku's PPP value by
  ~20%.
- **The Kyoto basket.** The PPP conversion re-prices it, and today the skill only has a copy of it.

This is the first request under `research/money-requests.md` (feature 389).

## User Scenarios & Testing

### User Story 1 - The skill can cite each foundation figure (Priority: P1)

The gm-assistant session opens the record's money section on diagram `main`. It finds one question for each of the four,
each answering with quoted, checked sources, and cites them in its ledger.

**Independent Test**: the four question files exist under the money section, and each has passed its checks.

**Acceptance Scenarios**:

1. **Given** the land question, **When** it is read, **Then** it gives what land sold for in years of its net yield, for
   Japan and for China separately, and how the multiple varied between irrigated rice land and dry land and between
   near-city and remote land, or what was searched and not found. It gives any attested interest or rate of return on
   land, set beside the canon's 15-20% city and ~25% countryside interest and the ~50-koku, ~20x farm.
2. **Given** the wage question, **When** it is read, **Then** it gives an unskilled laborer's day wage in rice and in
   coin, city against countryside, and the working days in a year, 18th-century Japan first and Qing China beside it;
   the laborer's year in koku of rice and the city/country ratio; and a verdict on each 2017 working figure: 1.33 zeni a
   day, 3.32 koku a year (~2 kg a day, 250 days), farm labor 3.5 koku a year.
3. **Given** the koku question, **When** it is read, **Then** it gives the koku's volume and its weight as brown,
   polished and unhulled rice, how that weight varied by period and domain, the weight of a liter of uncooked rice, and
   a person's yearly grain (budgets.md's ~1.5 koku) against l7r.md's "feeds a man for a year". It checks each
   `budgets.md` figure the request lists, each `l7r.md` figure, and the 2017 spreadsheet's 151.5 kg and the asker's
   ~120 kg (40 gallons at 0.8 kg/L).
4. **Given** the basket question, **When** it is read, **Then** it quotes Basket A's quantities and Kyoto 1745-54 silver
   prices verbatim from a public copy of the paper, quotes what any Basket B or "respectability" variant holds, and compares them with the 2017 snapshot.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#1 names each question's fragment FILE, a verdict per figure, and what is still open,
and flags every contradiction with canon for the GM.

**Independent Test**: the issue carries that answer, and gm-assistant closes the issue.

### Edge Cases

- **A figure no public page carries.** It gets an absence note saying what was searched. A source only the GM can read
  goes on the download list.
- **The two canon files disagree** (`l7r.md` against `budgets.md` on the koku). Both are reported to the GM as they
  stand; the record does not choose.
- **A wage or price is attested only for one city** (Kyoto, Edo). The verdict is ATTESTED ONLY FOR that city.

## Requirements

### Functional Requirements

- **FR-001**: Four questions MUST be written in the record, tagged `money` first, with no drawing pages: land price
  against yield, unskilled wages, the koku of rice, and the Kyoto basket.
- **FR-002**: Each MUST be researched with a search pass and pass the record's checks: `quote-check`, `source-reader`,
  and `source-applicability` on every new source.
- **FR-003**: The money section's `awaiting` line MUST be deleted with the first of these questions (feature 389).
- **FR-004**: The feature MUST close `make impl-check` with a "no code implements it - consumed by gm-assistant's money
  skill" line for each question.
- **FR-005**: The answer on EliAndrewC/diagram#1 MUST follow `research/money-requests.md`: fragment files, a verdict per
  figure, what is still open, and each contradiction with canon flagged for the GM.
- **FR-006**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

### Measurable Outcomes

- **SC-001** (FR-001, FR-003): The money section lists 4 questions, and `make record CHECK=1` builds cleanly.
- **SC-002** (FR-002): All 4 questions carry 0 open findings from their checks.
- **SC-003** (FR-004): `make impl-check F=390` reports nothing missing.
- **SC-004** (FR-005, FR-006): The issue's answer names all 4 fragment files and a verdict for every figure the request
  named.

## Decisions Recorded

This feature draws nothing on a map. Its findings are labeled in the record itself (accurate, deviation, guess).

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Japan first for wages, the koku and the basket; both regions for land | process decision (the asker's region order) | Tokugawa price and wage series are the richest data | `research/money-requests.md` |
| Canon contradictions reported, not resolved | process decision (CLAUDE.md: never contradict the GM's notes) | the canon is the GM's | the issue answer |

## Assumptions

- The four questions fit one write session, which is capped at four questions and ten new registry keys. If they run
  past ten keys, the session's continuation brief takes the rest.

## Review history

- **spec-fidelity round 1 (2026-10-18): CHANGES REQUIRED, 5 items.** Scenarios 1-4 gained the issue's dropped clauses
  (land by kind and distance with the canon's interest beside it; the 2017 wage figures; the koku by period and domain,
  the 2017 spreadsheet figures, yearly grain; what variant baskets hold); request.md now carries the issue verbatim.
- **spec-fidelity-verify round 2 (2026-10-18): FAITHFUL.**
