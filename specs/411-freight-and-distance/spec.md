# Feature 411: how far goods traveled, and what distance did to their price (diagram#12)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-22

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-22, "Thanks.  Now please check out issue #12."

The GM asked for issue #12 to be worked (his words, quoted above); a money research request gm-assistant opens for him is
approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (issue #12 as widened at the GM's request, verbatim), `passes/` (four search passes, 2026-10-22:
water freight; how far goods went; tea; named goods far from home)

## Why

gm-assistant's money skill prices goods carried far by its own guesses: a pack horse ~4-7 sen a ri, a porter ~1 sen a ri,
long-haul charcoal ~0.5-1 sen a bale a ri, and a bale of Fox white charcoal 35-60 sen near the kilns against 250-600 at Ryoko
Owari, about 500 miles overland (E0167-E0168). The record already holds land carriage (0260: Japan's post-station fares;
Qing official cart, porter, pack-animal and Hunan boat rates; 0278: Yunnan and Gansu carts and porters), one second-hand
account of salt's price rising with distance (0273), Osaka against Edo sake (0262) and Kumano against Tama charcoal in Edo
(0279). It holds no water freight beyond Hunan's official boat rate, no haul lengths, no tea route and no rule from the
literature.

## User Scenarios & Testing

### User Story 1 - Each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue's four questions - (1) freight per weight per distance by mode, land and water,
beside a laborer's day, and the land-to-water ratio; (2) typical and maximum hauls by good and mode, the distance at which
carriage doubled a price, and any rule in the literature; (3) tea's route lengths, packing, load per animal, and price at
origin against destination; (4) a named good's price where made against a distant city, with the distance and the mode -
the fragment file, the verdict and what is still open.

**Acceptance Scenarios**:

1. Each figure is written into a money question beside the craftsman's and the unskilled laborer's day wage of the same
   place and period, or, where no source gives one, that wage is SILENT with the nearest in the record named and labeled
   as the nearest.
2. What the record already holds (0260, 0262, 0273, 0278, 0279) is named by file, not repeated.
3. Each verdict is one of the four of `research/money-requests.md`. A figure for which only a nearest exists is SILENT, the
   nearest named under "what is still open" with the leads not tried, and the search in the absence note; a ratio or a
   combined figure computed by this project is labeled as its arithmetic and says what it covers.

### Edge Cases

- An official reimbursement rate (the Qing 物料價值則例) is not a fare: it is reported as ATTESTED ONLY FOR official rates.
- A rule stated by a modern historian is reported as that historian's statement, quoted, not as a fact of the period.
- No price is converted to koku; between coins only by a rate the source gives or 0277's, labeled.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #12, its fragment file, its verdict and what is still open.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names, in new money questions tagged as the money section's are (China first, then Japan, in
  each).
- **FR-003**: The feature closes with `make impl-check F=411` (money questions: no code implements them).
- **FR-004**: The reply is posted on #12; gm-assistant verifies and closes it.
- **FR-005**: A nearest figure is not an answer: each verdict is one of the four of `research/money-requests.md`; a figure
  the record holds only a nearest for is SILENT, the nearest and the leads not tried named under "what is still open".
- **FR-006**: Each price or rate sits beside the same place and period's day wage (craftsman and laborer); where no source
  gives one, the nearest in the record is named and labeled as the nearest (the issue: "each figure beside the same place
  and period's day wages").

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open
  in the reply on #12.
- **SC-002** (FR-002, FR-003, FR-006): `make record-owed` shows no unanswered unit for the touched questions at landing, and
  `make impl-check F=411` reports nothing missing.

## Assumptions

- China first for routes and transport, Japan beside it (the issue's order).
- Low priority (the issue): one write session and one check session; leads not followed are named, not chased.

## The findings, figure by figure

(Filled from the passes before the spec review.)
