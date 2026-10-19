# Feature 397: Campaign costs II - arrows, notice boards and paper, rents, plays (issue #4)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "Yes, I approve features for 3 and 4, and in fact, you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future."

**Input**: `request.md` (EliAndrewC/diagram#4 and its comments, verbatim, and the GM's approval, including the English
traveling players' footnote)

## Why

The second half of the GM's campaign questions (request.md): arrows, notice boards and paper, rents, and plays. Each price
sits beside the same place and period's unskilled day wage. The English traveling players are a COMPARATIVE footnote the
GM approved ("Yes, the English traveling player's footnote is in as well"). The record already holds the notice board
itself (0190, from the maps), so that question extends 0190, and the paper and ink prices go in the money section, as the
asker agreed. The comment on #4 also asks for two books on `research/to-download.md`, each naming 0251.

## User Scenarios & Testing

### User Story 1 - The skill can cite each cost (Priority: P1)

**Acceptance Scenarios** (for each figure the request names: ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or
SILENT):

1. **Arrows.**
   - **Price per arrow, ordinary and fine:** ATTESTED ONLY FOR Ming and Qing China. Late Ming was about 0.0136 tael, or
     under 0.033 within a set; 1650, 0.04; 1727 Beijing, war arrows 0.05-0.08 and fine arrows 0.12-0.36.
   - **Japan:** SILENT.
   - **Fletcher output per day:** SILENT.
   - **Recovery after battle:** NOT ATTESTED. The Qing code writes battle losses off.
2. **Notice boards and paper.**
   - **What a notice was made of and who could post:** ATTESTED for Edo. Official notices were wooden plaques in ink;
     pasted paper went only on structures the magistrate permitted. This goes on 0190, the existing notice-board
     question.
   - **Paper and ink prices:** ATTESTED ONLY FOR Qing Beijing (1736), per sheet by grade and ink per jin, beside the wage.
   - **Edo paper and ink:** SILENT. The two web figures disagree and neither is a citable source.
3. **Rents.**
   - **A back-tenement room:** ATTESTED ONLY FOR one Bunsei-era carpenter's rent (10 monme a month).
   - **The rent-to-value ratio:** ATTESTED for Edo lots (3-5% net, 4.8% gross by Mitsui's rule) and for Qing government
     houses (about 4-6%).
   - **A street-front shop, a small house, a samurai residence and a storehouse by the month:** SILENT.
4. **Plays and entertainers.**
   - **Edo kabuki seats by class:** ATTESTED (1803, pit 132 mon to boxes of 25-35 monme for seven). The single-act view
     at 16 mon is ATTESTED ONLY FOR the oikomi.
   - **Noh:** ATTESTED ONLY FOR fund-raising performances.
   - **Temple-fair shows:** SILENT.
   - **Rural troupes:** ATTESTED at troupe-hire level.
   - **Troupe composition:** ATTESTED.
   - **Qing seats:** ATTESTED.
   - **The English traveling players:** ATTESTED ONLY FOR gathering at the door. Passing a hat mid-play is NOT ATTESTED by
     any period source. This is written as a comparative question under the record's comparative category.

Each figure is set beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them. Where none does, the question says that wage is SILENT and names the nearest wage it has, with its
place and its gap in years. A figure the project computed is labeled as the project's arithmetic.

### User Story 2 - The asker gets its answer, and the two books are listed (Priority: P1)

The answer on EliAndrewC/diagram#4 names each fragment FILE, a verdict per figure, and what is still open. Takeyasu 1966 and
Uemura 1987 are on `research/to-download.md`, each naming 0251 as what rests on it.

## Requirements

### Functional Requirements

- **FR-001**: The arrows, paper-and-ink, rents and plays questions MUST be written in the money section, tagged `money`
  first, with no drawing pages. The notice board's material and who could post MUST extend 0190.
- **FR-002**: The English traveling players MUST be a comparative question (subject `comparative,money`), its source of
  the comparative kind.
- **FR-003**: Each new or changed question MUST pass the record's checks.
- **FR-004**: The feature MUST close `make impl-check` (0190's change checked against the code that draws notice boards).
- **FR-005**: The answer on EliAndrewC/diagram#4 MUST follow `research/money-requests.md`. Takeyasu 1966 and Uemura 1987
  MUST be on `research/to-download.md`, each naming 0251.
- **FR-006**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-003): The questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-004): `make impl-check` reports nothing missing.
- **SC-003** (FR-005, FR-006): The issue's answer names every fragment file and a verdict for every figure, and the
  download list carries both books.

## Assumptions

- Four new money questions, one comparative question and one extended question exceed one write's cap, so the write runs
  as two sessions.
