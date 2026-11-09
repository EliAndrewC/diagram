# Feature 450: when cotton and other cash crops spread to China, Japan, India and Korea (diagram#22)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-08

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-11-08, "Please watch Github for research tasks which might be filed as issues."

The GM asked this session to work the research tasks filed as issues (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future").

**Input**: `request.md` (issue #22 verbatim), `passes/` (five search passes, 2026-11-08: Japan cotton; China cotton; species,
India and Korea; tobacco and the potato plants; the tomato, what set the pace, and the Tokugawa restrictions)

## Why

gm-assistant's money skill prices a plain cotton kimono as the ordinary dress of a low-ranking samurai, from cloth prices of a
period when cotton was already established (Ako 1781-90, Osaka in the 1840s). The GM will decide how common cotton is in Rokugan
from the history of when it became common. The record holds what cloth cost (0261, 0274), how long it took to make (0313) and the
trades (0209), and dry-field and cash crops on rice land (0006, 0020), but nothing on when any of these crops arrived or spread.

This feature records only the history. The decision about Rokugan stays with the GM.

## User Scenarios & Testing

### User Story 1 - Each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue, the fragment file, the verdict and what is still open: for cotton in Japan and China
(priority first), a dated stage for each of the five stages the issue names and the century cotton clothing became widespread, with
who wore it; for cotton in India and Korea, the same stages, and each species' date of arrival and importance; for tomatoes,
potatoes and tobacco, dated stages and the lag from arrival to common use, per crop and country; and the factors historians name,
with author and the crops they apply to.

**Acceptance Scenarios**:

1. Each dated stage is one of the four verdicts of `research/money-requests.md` (ATTESTED, ATTESTED ONLY FOR, NOT ATTESTED,
   SILENT). A date for a neighboring place, century or plant is SILENT, the nearest named under "what is still open".
2. What the record already holds (0261, 0274, 0313, 0209, 0006, 0020) is named by file, not repeated.
3. The GM's premises are tested and answered either way: that cotton is a post-Columbian crop; that the roughly 100 years between
   Columbus and the Tokugawa restrictions bear on Japanese cotton; that tomatoes were not a big part of Japanese cuisine when
   available; that China did not cultivate them on a large scale for centuries.
4. The potato plants stay separate throughout: white potato, sweet potato and native yam or taro, each date saying which plant
   it concerns.

### Edge Cases

- A source that uses a loose plant word (薯, 芋, 甘藷): the date is given as that word, with how the plant is identified; where it
  cannot be, the date is ATTESTED ONLY FOR the word and says so.
- A source from outside the four countries, on what set the pace of a crop's spread, is marked COMPARATIVE and answers question 4
  only. Under `research/CLAUDE.md` the source kind `comparative` is for another society's MONEY; a non-money comparison is labeled
  in prose and takes no such kind.
- Where the history contradicts the canon (cotton as an ordinary low-tariff good; tobacco among the cash crops), the answer says so
  and it goes to the GM through `escalation-check`. Nothing here edits the canon.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #22, its fragment file, its verdict and what is still open.
- **FR-002**: New findings are written into the record under the citation rules (`research/CLAUDE.md`), checked by the record checks
  `make record-owed` names, in new money questions tagged as the money section's are, with `subject=money` first.
- **FR-003**: The feature closes with `make impl-check F=450`. No engine code decides cotton, tobacco or any of these crops
  (`grep` over `l7r/` and `pool/` on 2026-11-08 found glossary terms and one pool note only).
- **FR-004**: The reply is posted on #22 with questions 1 and 2 first; gm-assistant verifies and closes it.
- **FR-005**: A nearest figure is not an answer: each verdict is one of the four; a figure the record holds only a nearest for is
  SILENT, the nearest and the leads not tried named under "what is still open".
- **FR-006**: Findings state the history as found. No fragment says how common cotton is in Rokugan.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open in the
  reply on #22.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make impl-check
  F=450` reports nothing missing.

## Assumptions

- Japan and China equally for question 1; the issue's own region order for the others.
- Questions 1 and 2 are worked first; questions 3 and 4 may follow in a later write session, as the issue allows.
