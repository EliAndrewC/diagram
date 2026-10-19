# Feature 396: Campaign costs I - inns, transport, cloth and sake (issue #3)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "Yes, I approve features for 3 and 4, and in fact, you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future."

**Input**: `request.md` (EliAndrewC/diagram#3 and its comments, verbatim, and the GM's approval)

## Why

The GM's campaign keeps asking what everyday things cost: a night at an inn, a hired horse, a kimono, a cup of sake.
gm-assistant's money skill has guesses for each, and #3 asks for cited figures. Each price is to sit beside the unskilled
day wage of the same place and period, because the skill converts prices to laborer-days (request.md). The four search
passes (`passes/`) found the prices mostly in copper mon. The record's wage series is in silver (0250), so a fifth question
gives the copper-to-silver exchange by period. Without it, no mon price can be set beside a silver wage.

## User Scenarios & Testing

### User Story 1 - The skill can cite each everyday cost (Priority: P1)

**Acceptance Scenarios** (for each figure the request names: ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or
SILENT):

1. **Inns.**
   - **A hatago night with two meals:** ATTESTED, about 120-200 mon on the Tokaido and Ise roads, 1790 to the 1850s.
   - **A kichin-yado night:** ATTESTED. The regulated rates were 3-16 mon (1611-1686). By the 19th century it was about
     50 mon; in Edo in 1843, 24 mon for the roof plus 16-24 for bedding.
   - **A horse for the night:** ATTESTED ONLY FOR the regulated firewood charge per horse; feed and stabling are SILENT.
   - **The Qing inn:** SILENT.
2. **Transport.**
   - **The official stage rates per ri for a pack horse, a light horse and a porter:** ATTESTED (1665, 1711, the 1820s
     surcharge). The negotiated rate is ATTESTED ONLY FOR "about twice" (hedged).
   - **The return:** ATTESTED, paid stage by stage, one way.
   - **A hired horse with its driver by the day, and a cart by the day:** SILENT.
   - **The Qing rate:** ATTESTED ONLY FOR one 1863 private mule hire.
3. **Cloth.**
   - **A tan's length:** ATTESTED.
   - **Cotton per tan:** ATTESTED (1781-91, Akō and Edo).
   - **Plain silk:** ATTESTED ONLY FOR one 1692 figure from fiction.
   - **The silk-to-cotton ratio:** ATTESTED ONLY FOR Qing Beijing's official prices (1736).
   - **SILENT:** pongee, used kimono, sewing and silk bedding.
   - **Bassino and Ma's linen price:** set beside the recorded cotton prices, as the pass found (0249).
4. **Sake.**
   - **Edo shop prices per sho and per go, Edo tavern and soba-shop prices per go, and the 1842 Kazusa list (rural
     ceilings):** each ATTESTED for its case.
   - **The Edo shop-to-tavern markup:** SILENT.
   - **The Qing markup:** ATTESTED ONLY FOR bought wine against home-brewed (twice) and retail spirit against bulk (25%).
     The Qing tavern price is SILENT.
5. **The copper-to-silver rate.** Mon per monme (and per ryō) by period, as attested. This lets each mon price above sit
   beside the silver wage series.

Each figure is set beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them. Where none does, the question says that wage is SILENT and names the nearest wage it has, with its
place and its gap in years. A figure the project computed (a per-ri or per-day equivalent, a conversion) is labeled as
the project's arithmetic.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#3 names each question's fragment FILE, a verdict per figure, and what is still open.

## Requirements

### Functional Requirements

- **FR-001**: Five questions MUST be written in the money section, tagged `money` first, with no drawing pages: inns,
  transport, cloth, sake, and the copper-to-silver rate.
- **FR-002**: Each MUST pass the record's checks: source-reader, quote-check, translation-check, record-format,
  intro-check, and source-applicability on each new source.
- **FR-003**: The feature MUST close `make impl-check` with a "no code implements it" line per question.
- **FR-004**: The answer on EliAndrewC/diagram#3 MUST follow `research/money-requests.md`.
- **FR-005**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The five questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004, FR-005): The issue's answer names all five fragment files and a verdict for every figure.

## Assumptions

- Five questions exceed one write session's cap of four, so the write runs as two sessions.
