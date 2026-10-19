# Feature 398: The rest of the shrine builder's options (issue #7)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future."

gm-assistant filed #7 at the GM's request ("Also from the GM: #7, the rest of the shrine builder's options"), so it is approved by his asking.

**Input**: `request.md` (EliAndrewC/diagram#7 and its comments, verbatim)

## Why

gm-assistant's shrine builder prices every option from a money-skill estimate made before research. #6 (feature 395)
covered the options in the GM's player's design. #7 asks for the alternatives so the whole catalog can be graded:
- sanctuary forms, halls and finishes;
- stone work;
- metal furnishings;
- rites for the dead.

Each figure sits beside the craftsman's and the laborer's day wage of the same place and period. Where 0255-0258 already
cover an item, the question says so rather than repeating it (request.md). Four search passes ran on 2026-10-19
(`passes/`), and their findings were posted on #7 as interim.

## User Scenarios & Testing

### User Story 1 - The builder can grade each option (Priority: P1)

**Acceptance Scenarios** (for each figure the request names: ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or
SILENT; or "covered by NNNN" where 0255-0258 give it):

1. **Sanctuary alternatives, halls and finishes.**
   - **Kasuga- and shinmei-zukuri sanctuaries:** SILENT.
   - **A stone hokora:** SILENT.
   - **A cover-shed:** covered by 0255.
   - **A worship pavilion:** covered by 0255 for the hall. Its fittings and doors (Shibasaki 1841) are ATTESTED ONLY FOR a
     deposit and a final payment. An offering hall is SILENT.
   - **Hinoki, keyaki and sugi timber:** SILENT.
   - **Thatch:** ATTESTED ONLY FOR quantity and the helpers' labor (Shibasaki 1840-41).
   - **Shingle:** ATTESTED ONLY FOR one purchase of roof boards (Shibasaki 1840).
   - **Copper:** covered by 0256.
   - **Vermilion, bengara and black lacquer:** SILENT.
   - **Carving:** ATTESTED (Tanashi 1858, 147 pieces on a 4.3-shaku-bay sanctuary, 135 ryo). Kawagoe Hikawa is an upper
     bound only.
   - **Openwork transoms:** SILENT.
2. **Stone work.**
   - **A stone torii:** covered by 0257.
   - **A pair of stone lanterns:** ATTESTED (Shibasaki 1841, 4 ryo 3 bu delivered).
   - **A tall lantern:** SILENT.
   - **Mason-days:** ATTESTED ONLY FOR the 1841 payment for four extra men.
   - **A stairway:** ATTESTED ONLY FOR the plinth stones and the curb.
   - **Komainu or foxes, a basin, a stele, a gorinto, a coffer:** SILENT.
3. **Metal and furnishings.**
   - **A mirror, a gong, hanging lanterns, a reliquary, an offering chest with its lock, a lacquered chest:** SILENT.
   - **The nearest figure:** raw copper by the kin (Osaka 1774), ATTESTED, as a materials floor. Qing copper ware by the
     jin is ATTESTED ONLY FOR coarse ware sold by weight.
4. **Rites and the dead.**
   - **A night enshrinement:** the cost share is covered by 0255/0256. The priests' fee is SILENT.
   - **A goryo festival:** ATTESTED ONLY FOR one Hakata ward's Gion float duty (1838).
   - **Eitai kuyo, a portion to Koyasan, washing bones:** SILENT.
   - **A calligrapher's plaque fee:** SILENT in Japan. ATTESTED ONLY FOR a Chinese price list (Zheng Banqiao, 1759).

Each figure is set beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them. Where none does, the question says that wage is SILENT and names the nearest wage, with its class, its
place, its unit and its gap in years. A craftsman's wage is never shown as the unskilled wage. A figure the project
computed is labeled as the project's arithmetic.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#7 names each question's fragment FILE, a verdict per figure (or the question it is
covered by), and what is still open.

## Requirements

### Functional Requirements

- **FR-001**: Four questions MUST be written in the money section, tagged `money` first, with no drawing pages:
  sanctuary alternatives and finishes, stone work, metal and furnishings, rites and the dead.
- **FR-002**: Each MUST pass the record's checks: source-reader, quote-check, translation-check, record-format,
  intro-check, and source-applicability on each new source.
- **FR-003**: The feature MUST close `make impl-check` with a "no code implements it" line per question.
- **FR-004**: The answer on EliAndrewC/diagram#7 MUST follow `research/money-requests.md`.
- **FR-005**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The four questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004, FR-005): The issue's answer names all four fragment files, a verdict for every figure, and what is
  still open.

## Assumptions

- Four questions fit one write session.
- The verdicts above are the search passes'. The write may narrow them; it may not widen them without a source.
