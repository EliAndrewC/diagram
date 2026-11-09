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

## The findings, figure by figure (the passes, 2026-11-08; leads until read on the page)

**Question 1, Japan** (`passes/a-japan-cotton.md`):
- First record: cloth shipped in during the Nara period (Shosoin fragments); the 799 Mikawa seed landing, which did not take. ATTESTED.
- Cloth mainly an import: from Kamakura; mainly Korea in the 15th century; Ming China from the mid-16th (Tenbun 1532-55 against the
  1570s, both given). ATTESTED.
- First cultivation on any scale: end of the 15th to start of the 16th century, nearly everywhere but the cold Tohoku (Nagahara,
  read through Yajima); earliest dated traces 1494 Echigo and 1510 Mikawa. ATTESTED ONLY FOR those traces and that summary.
- Regular commercial crop: 16th century in Mikawa and Tokai; concentrated on the Kinai by the 1620s-30s; Kawachi's great growth in
  Genroku; the San'in and Setouchi after about 1760. ATTESTED.
- Normal clothing of commoners: sources point to the early 17th century in the warm regions (the 1628 order, Adams) and disagree
  between early and late Edo for cotton as the main fiber; Hirosaki peasants had hemp as the rule to 1790, cotton mostly as old
  clothes from the late 18th century; Akita about 1810 still shows hemp and used cloth. ATTESTED ONLY FOR the areas named.
- Share: no share of households wearing cotton for any region or century. SILENT; Akita 1808-10's supply table and Aomori's
  1850-51 landings named as the nearest, shares this project's arithmetic.
- Low-ranking samurai: sumptuary ceilings only (Hirosaki 1661, below 100 koku cotton; Morioka, low retainers hemp-type cloth and
  cotton). ATTESTED ONLY FOR what those rules allowed, not what men owned.
- The GM's direct question, Japan: a century by region, each named with who wore it, and the disagreement stated.

**Question 1, China** (`passes/b-china-cotton.md`):
- First record: Han texts and Xinjiang finds; the first unambiguous plant-woven-into-cloth statement is the Liang shu on Turfan,
  6th century. ATTESTED.
- Import or tribute: Han to Song; commercial Indian import by Southern Song. ATTESTED.
- First cultivation: Turfan by the 6th century, Yunnan under Tang, Fujian-Guangdong-Hainan by the late 11th, the Yangzi by the 12th
  (a modern reading of poems) and firm by the 1270s-80s; the frontier and the Yangzi kept separate. ATTESTED.
- Regular commercial crop and the state's part: Fujian and Guangdong by the 11th century; 1289 superintendencies, 1296 summer tax,
  the early Ming planting order; Songjiang commercial by the late 15th century. ATTESTED. Qiu Jun's "not yet levied" against the Yuan
  shi, both given.
- Normal clothing of commoners: "rich and poor" (Qiu Jun, 1480s), "high and low" (Song Yingxing, 1637), winter wear; the north's own
  weaving only in the last Ming decades; the far south still in kudzu, banana and ramie for summer in the late 17th century.
  ATTESTED ONLY FOR those general statements. Share of households or clothing: SILENT before Buck (1930, outside the window, named);
  acreage for Songjiang and southern Jiangsu only.

**Question 2** (`passes/c-species-india-korea.md`):
- The premise fails: Old World cotton in India from the 6th millennium BCE (Mehrgarh, genus only), cultivation by about 2500 BCE;
  G. arboreum and G. herbaceum in China before 1492; G. arboreum in Korea and Japan. ATTESTED. The identifications changed over time
  (Fortune and EB 1911 against Hutchinson 1947); said so.
- American species: India trials from 1788-90, a foothold at Dharwar from 1843; China from 1865; Korea from 1904, 93% of the southern
  crop by 1918 and 70% nationally by 1936. Japan: imported raw cotton only, cultivation of an American species SILENT. Any India
  share rests on one modern essay and is ATTESTED ONLY FOR it.
- India stages and Korea stages as the pass reads them; "cloth arriving mainly as an import" is not a stage India had; commoners'
  cotton in India SILENT.
- Korea and Japan: cloth, from about 1400 through the So-controlled trade, up to 500,000-odd bolts in one year of the 1480s by
  one figure. ATTESTED ONLY FOR cloth; the plant reaching Japan through Korea NOT ATTESTED, the one source naming a seed route says Ming.
- The GM's point: the roughly 100 years from Columbus to the Tokugawa restrictions have no bearing on Japanese cotton through American
  seed, on these findings. Whether the 16th-century spread of Old World seed fell inside those years is stated from the dates in
  question 1.

**Question 3** (`passes/d-tobacco-potatoes.md`, and the tomato in `passes/e-tomato-spread-factors.md`): per crop and country as the
pass's table reads; tobacco about 10 years in Japan and Korea, about 30-50 in China and India; the sweet potato more than a century,
and regional; the white potato marginal almost everywhere before the 19th century; the tomato first recorded 1617-21 in China, 1668 in
Japan, 1614 in Korea (identity the modern writers'), and common food only in the 20th century. Much of the dating is tertiary; each
verdict says what it stands on. India's sweet potato SILENT on arrival, cultivation and commonness.

**Question 4** (`passes/e-tomato-spread-factors.md`): the GM's two tomato positions hold on these dates. Factors named with author
and crops (Li Xinsheng; Crosby on Ho; Li Hua), their disagreement on speed given; Japan has no historian's comparative explanation read.
That the Tokugawa restrictions stopped new plants arriving is NOT ATTESTED: dated arrivals continue through Nagasaki, Tsushima and
Ryukyu-Satsuma (Isono 2007). No source outside the four countries was used, so nothing is marked COMPARATIVE.

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
- **FR-007**: Two sources that disagree are both given. A draft marked not for citation is cited with that said, a work read only
  through another is cited as read through it, and a figure from one source only says so.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open in the
  reply on #22.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make impl-check
  F=450` reports nothing missing.

## Assumptions

- Japan and China equally for question 1; the issue's own region order for the others.
- Questions 1 and 2 are worked first; questions 3 and 4 may follow in a later write session, as the issue allows.
