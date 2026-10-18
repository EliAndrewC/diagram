# Feature 391: Comparative money sources, and The Complete Servant (issue #2)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-18

**Status**: Draft

**Affects**: research record, research process

**Approved**: the GM, 2026-10-18, "I do approve the second feature as well, not just the first feature. So yes, please work both of them given that guidance."

**Input**: `request.md` (gm-assistant's request on EliAndrewC/diagram#2, and the GM's guidance and approval, verbatim)

## Why

The record takes only sources that fit a premodern East Asian setting. That is on purpose: European farming was so
different that European sources must not shape the maps (request.md). Money is different. Part of the money research's
job is to tell players what things cost, and players know shillings from Austen and Dickens. A Regency wage converted by
the same purchasing-power method as a koku gives a player a yardstick. The GM: *"not because we will use it to establish
the actual value of a koku, but because ... that can serve as a useful way for our real-life players to get a sense of
what these wages were like relative to the wages of ... characters in stories that they have read."*

So the record gains a COMPARATIVE category, defined in the research guidelines with why it exists and what it may not
be used for. Its first question is *The Complete Servant* (Adams, London, 1825), asked for because one of the GM's players
has read it and worked on it. In general such sources are not sought out (request.md).

## User Scenarios & Testing

### User Story 1 - The guidelines name the comparative category (Priority: P1)

A session meets a European or other non-East-Asian source on money. The research guidelines tell it the following:
- **The category exists.** It is for comparative money questions.
- **Why it exists.** Players can compare a Rokugani wage or price with one they know from fiction they have read.
- **Its limits.** A comparative source NEVER sets a koku's value, a Rokugani price or wage, or anything on a map; it is
  never cited for how a place was built, farmed or lived in; and it is not sought out unless the GM asks for it or approves it.

**Independent Test**: the guidelines carry the definition. A comparative question and its sources are marked as
comparative where a reader meets them. The source check judges such a source against the comparative purpose, and a
comparative source cited outside a comparative question is refused or flagged.

**Acceptance Scenarios**:

1. **Given** a comparative source, **When** `source-applicability` judges it, **Then** it judges it against the
   comparative purpose and the limits, not as a source on East Asia.
2. **Given** a comparative source cited by a question that is not comparative, **When** the record is checked, **Then**
   that citation is caught.

### User Story 2 - The Complete Servant answered (Priority: P1)

gm-assistant gets the following:
- **The text, archived.**
- **A check of its 25 extracted servant-wage rows** against the text. Each misquote, wrong post or wrong section is
  named, and the absence of any wage line for the housekeeper and the house steward is confirmed or corrected.
- **A question file** on what a Regency English household paid its servants and how it divided its income: the expense
  table and the servants-by-income list.
- **The book's provision and household-goods prices**, verbatim with units, or what is missing.

**Independent Test**: the issue's answer names the question files and the check of the 25 rows, and gm-assistant closes
the issue.

### Edge Cases

- **A row quotes the text correctly but files it under the wrong post.** It is reported as a wrong post.
- **The book gives no price for something asked** (fuel, cloth). The answer says so, as SILENT.
- **A later request wants Dickens-era or other comparative figures.** The same category takes them, under the same
  limits, only when the GM asks for it or approves it.

## Requirements

### Functional Requirements

- **FR-001**: The research guidelines MUST define the comparative category: what it is (a SOURCE on another society's money, not a cross-cultural method), why it exists (in the GM's
  words), and its limits. Its limits are these:
  - it is for MONEY questions only;
  - a comparative source never sets a koku's value, a Rokugani price or wage, or anything on a map;
  - it is never cited for how a place was built, farmed or lived in;
  - it is not sought out unless the GM asks for it or approves it (as for *The Complete Servant*, which one of his
    players has read).

  Wherever the record already describes the source tag that marks such a source, the description MUST agree with the
  category. Today the `region=europe` explanation says Europe is used "only for constraints that cross cultures".
- **FR-002**: A comparative question and each comparative source MUST be marked as such where a reader meets them.
- **FR-003**: `source-applicability` MUST judge a comparative source against the comparative purpose and the limits.
- **FR-004**: A comparative source cited by a question that is not comparative MUST be caught by the record's checks.
- **FR-005**: *The Complete Servant* MUST be archived, and every `complete-servant` row of gm-assistant's ledger (25 at
  gm-assistant 9459638a, 2026-10-18) checked against it, each discrepancy named. The check MUST also confirm or correct
  that the book has no wage line for the housekeeper or the house steward.
- **FR-006**: The record MUST hold one or more comparative money questions answering the issue's items:
  - servants' wages by post, as checked under FR-005;
  - the income division and the servants by income;
  - the provision and household-goods prices the book quotes (food, candles, fuel, cloth, keeping a horse), verbatim with
    their units, with each item the book does not price reported as SILENT.

  Each question MUST be checked like any other.
- **FR-007**: The answer on EliAndrewC/diagram#2 MUST follow `research/money-requests.md`, and MUST give the edition and
  page of each figure.
- **FR-008**: Nothing in this feature changes a map or the GM's canon.

## Success Criteria

### Measurable Outcomes

- **SC-001** (FR-001, FR-003): The guidelines' definition names the category, its reason and every limit FR-001 lists,
  and the `source-applicability` contract carries the comparative judgment.
- **SC-002** (FR-002, FR-004): A test proves that a comparative source cited from a non-comparative question is caught,
  and that the comparative marking reaches the built page.
- **SC-003** (FR-005): All 25 rows carry a verdict, and the finding on the housekeeper and the house steward is stated.
- **SC-004** (FR-006, FR-007, FR-008): The issue's answer names every question file and a verdict for every item asked,
  and the questions carry 0 open check findings.

## Decisions Recorded

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Sources such as *The Complete Servant* (another society's money, read for a player's yardstick) are admitted as COMPARATIVE only, under stated limits; cross-cultural METHOD (the purchasing-power method) is not this category | process decision (the GM, 2026-10-18) | players compare against fiction they know; such sources must never set a Rokugani value or shape a map | the research guidelines (FR-001) |
| Comparative sources are not sought out unless the GM asks for it or approves it | process decision (the GM: "in general we should not target sources like The Complete Servant") | keep the record East Asian | the same |

## Assumptions

- gm-assistant's `ledger.jsonl` on its `main` can be read from GitHub with diagram's token or from the host mount.

## Review history

- **spec-fidelity round 1 (2026-10-18): CHANGES REQUIRED, 6 items.** The following were applied:
  - FR-005 now covers the housekeeper and house steward, and the row count is measured.
  - FR-006 is the narrowed request (the in-kind research is dropped; household goods are listed and quoted verbatim;
    SILENT is reported).
  - FR-001 now says money only, adds the built/farmed limit and the europe tag's explanation, and makes the GM the one
    who asks.
  - FR-007 now gives the edition and page.
  - request.md now carries the issue verbatim.
- **spec-fidelity-verify round 2 (2026-10-18): FAITHFUL.** Its asides applied: "asked for" names the GM throughout;
  FR-001 says the category is a source, not a method.
