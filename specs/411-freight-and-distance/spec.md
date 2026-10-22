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
- Two write sessions (A+B, then C+D) and one check session: the findings cite 16 sources with no registry entry yet
  (counted 2026-10-22), against a cap of ten new keys a write session. Leads not followed are named, not chased; each is
  listed under what is still open.
- The issue names three cases the passes did not reach - a Japanese rule from the literature (question 2), Shizuoka tea
  reaching Edo (question 3) and Tosa white charcoal (question 4): each gets a verdict and its search, or is listed as not
  searched under what is still open.

## The findings, figure by figure (the passes, 2026-10-22; leads until read on the page)

Four new money questions, numbers reserved at writing: **A "What did carrying goods cost by water, against by land?"**
(question 1), **B "How far did goods travel before carriage priced them out?"** (question 2), **C "How did tea travel,
and what did it cost at the end of the road?"** (question 3), **D "What did a famous good cost far from where it was
made?"** (question 4). China first in each, Japan beside it.

- **A. Freight by water, China**: ATTESTED ONLY FOR official rates - Jiangsu's Qianlong-era 物料價值則例 (Bochum .xls):
  a boat of 10,000 jin at 0.006-0.012 tael a li around Suzhou, Taicang, Changzhou, Songjiang, porters at the landing
  0.002-0.003 tael per 100 jin a li, beside a laborer's 0.04 and a craftsman's 0.05-0.06 tael; Hunan 1769 already in 0260
  (named, not repeated). Grain freight, 清史稿 卷122: Tianjin lighters 1695, 1.32 tael per 100-shi boat per 100 li; the
  sand-junk rate Shanghai-Tianjin 0.55 tael a shi (restated 1868), the sea route "over 4,000 li" (1826); a later ceiling of
  0.7 rising to about 1 tael a shi.
- **A. The land-to-water ratio**: ATTESTED ONLY FOR historians' statements and official rates - Cheng 2024 (LSE WP 371):
  water about one-tenth of mule-pack land carriage in the early-to-mid Qing Yangzi; 1:10 to 1:37.5 in an 1890 survey; Qiu
  Jun 1487 (大學衍義補 卷34): the canal saves 30-40 percent on land carriage, the sea 70-80. The Jiangsu porter-to-boat rates
  give 25-50 to 1, and Hunan's in 0260 about 19 to 1 (this project's arithmetic, labeled).
- **A. Japan**: ATTESTED ONLY FOR a late-Edo standard of about 60 monme of silver per 10 da of sake, Nishinomiya/Nada to
  Edo (Kato 2007, citing Yunoki), no distance or wage; Hagi domain's sea freight on tax rice as a share of the rice: 3.4
  percent to Osaka in 1652, about 4 to 1763, 6-7 from 1764 (Kibe). Pack horses: 0260's post-station fares (named); the
  chuma carriers' 100 kan a trip with 3-4 horses (kotobank, already a registry source). An Edo land-to-water ratio: SILENT.
- **B. How far goods went, and a rule**: ATTESTED ONLY FOR a Han proverb and modern statements - Shiji 129, 「百里不販樵，
  千里不販糴」; Xu Tan (already registered) that Ming-Qing everyday goods broke it, and that hubs lay along waterways; Skinner
  (already registered): a marketing area's farthest villager 3.4-6.1 km from the town, modal about 4.5 km. Carriage as a
  share of the good: the Ming surcharge of 1431 by distance, 0.5-0.8 shi per shi of tax grain to Beijing by province, later
  0.25-0.6 (明史 卷79); Qiu Jun's Han and Tang extremes, 10 to 190 units spent per unit delivered (卷33). The distance at
  which carriage equaled the price: SILENT in the sources; this project's arithmetic from Cheng's official land rates and
  his 1680 grain price, about 300-900 li by land against thousands by river, labeled as arithmetic. Hauls: firewood
  head-loads of 30-40 kg about 15 km into Kyoto by the Ohara women (modern, "it is said"); Luopang firewood rafted hundreds
  of li (廣東新語 卷25, already registered); salt doubling within 2 ri inland (0273, named). Tea, cloth and silk distances:
  SILENT beyond Xu Tan's destinations.
- **C. Tea**: Ya-chou to Ta-chien-lu, ATTESTED (Rockhill 1891, of 1889): about 150 miles in 17-18 days, porters with 9
  packages of 18-23 lb (190-200 lb), up to 17; 0.2 tael a package; repacked into rawhide cases of about 45 lb, two a yak
  load; best brick 2 taels a package at Ya-chou; Desgodins' 1883 ladder Ta-chien-lu - Batang - Lhasa about fourfold. Ming
  tea-horse rates: ATTESTED ONLY FOR official rates (明史 卷80): 1,800 jin a horse, then 120/70/50; 5,000-odd li of tea
  country. Kalgan to Kyakhta, ATTESTED (Parkes 1854, of about 1850): 804 miles in 40-50 days, camels up to 300 catties,
  freight usually 2.5 taels per 100 catties; chests 40-90 catties; no price pair (money banned at Kyakhta). Uji to Edo:
  ATTESTED ONLY FOR the tea-jar procession's route and season; prices, freight, weights SILENT.
- **D. A named good far from home**: China, ATTESTED ONLY FOR Wuyi Congou c. 1800-1834 (Ball 1848): 12 taels a picul at
  origin, carriage to Canton 3.92 taels (about a third of origin cost) over six weeks to two months by river with two
  porter stages, about 27 taels to the Company at Canton, 60 at London sale; wages of the region beside it. Japan, ATTESTED
  ONLY FOR Nada sake's Edo price and freight, not a brewery price the same year: 15-20 ryo per 10 da (20 casks) normally in
  1804-1830, 13.5-23 ryo in the Shibata accounts of 1858 (Kobe City Archives), freight about 60 monme per 10 da, 10-14
  days by ship. 0279's Kumano/Tama pair and 0262's Osaka/Edo sake named. Kumano charcoal at Tanabe, Uji tea, Shaoxing wine,
  Jingdezhen porcelain: SILENT.
- **Wages beside them**: where the source gives none, the nearest in the record (0250, 0255, 0260, 0275, 0278) named and
  labeled.

## Review history

- spec-fidelity round 1 (2026-10-22): CHANGES REQUIRED - the session count was put in the issue's mouth and was false
  against the ten-key cap; fixed (two write sessions, 16 keys counted). Its note on three cases the passes did not reach
  (a Japanese rule, Shizuoka tea, Tosa charcoal) added to the Assumptions and the write briefs.
- spec-fidelity round 2 (2026-10-22): FAITHFUL - the session count and the three cases resolved.
