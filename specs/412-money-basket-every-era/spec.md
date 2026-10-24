# Feature 412: the standard basket's prices, wages and coin rates in every era the record draws on (diagram#13)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files on this repository to be worked (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future").

**Input**: `request.md` (issue #13, verbatim), `passes/` (the census of the record's priced eras and the search passes,
2026-10-24)

## Why

gm-assistant converts every historical amount on the research site into goods dollars, wage dollars and Rokugani coin (feature
413 shows it). That needs one standard basket priced in each era and place the record cites, an unskilled day wage there, and
the era's coins in grams of pure silver. Two eras are built (Kyoto 1745-54, Tokyo 1882-86); salt, fuel and housing in the
reference era are guesses. The issue asks four questions to fill the rest.

## User Scenarios & Testing

### User Story 1 - each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue's four questions - (1) salt, fuel and a room in Kyoto or Osaka 1745-54, and salt
per person per year; (2) the basket's goods in every era and place the record cites; (3) an unskilled day wage in each; (4)
each era's coins in grams of pure silver - the fragment file, the verdict and what is still open.

**Acceptance scenarios**:

1. Each verdict is one of the four of `research/money-requests.md`. Question 1 asks for "the nearest dates found": a figure
   from outside 1745-54 or from another city is ATTESTED ONLY FOR <its place and years>, the gap stated - unlike feature 411,
   whose issue asked for each figure's own place and period (its FR-005).
2. The eras of question 2 are the record's own: a census of every price, wage and coin rate the record states - the money
   questions and every other fragment - by place and years (`passes/census.md`), names them; an era gets a row when at least
   rice is found; each era gets an id in gm-assistant's `<place>-<first year>` form.
3. An era priced from an official schedule (the Qing 物料價值則例) says so: its prices are ATTESTED ONLY FOR official rates.
4. Figures are laid out per era so gm-assistant can type them into its era files: place, years, coins in grams of pure
   silver, each good's price in the era's money with its unit and source, the day wage.

### Edge cases

- A price per bundle of firewood is converted to a price per million BTU only with the bundle's weight from a source; where the
  weight is this project's assumption, the per-BTU figure is labeled as its arithmetic.
- Japan's monme was a weight of chogin whose fineness changed at each recoinage: grams of pure silver per monme are given per
  recoinage, not computed from the copper rates of 0277.
- Nothing here moves the rice anchor (1.49 g a kg) or rules on the koku's weight; a source that bears on either is listed
  under what is still open.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #13, its fragment file, its verdict and what is still open.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names: question 1's figures in 0273 (salt), 0279 (fuel) and 0265 (rent); Japan's wages (question 3)
  in 0250; the basket by era in two new money questions, A (Japan) and B (China, with China's wages); the coins (question 4) in
  two new questions, C (Japan) and D (China), 0277's copper rates named, not repeated.
- **FR-006**: The reply on #13 accounts for every group of the census, in the money questions and outside them: each mapped to
  its row, or marked "no row" with its verdict and reason - the Nakasendo post stations by name.
- **FR-003**: Every amount in the record's fragments (not only the money questions) whose era this feature defines is marked
  for feature 413's tooltip with that era id; each era defined is added to `research/assets/money-eras-awaiting.json` (413
  FR-008) until gm-assistant's table carries its row.
- **FR-004**: The feature closes with `make impl-check F=412` (money questions: no code implements them).
- **FR-005**: Replies are posted on #13 at each landed batch; gm-assistant verifies and closes it.

## Success Criteria

- **SC-001** (FR-001, FR-005, FR-006): every figure of the issue carries a fragment file, a verdict and what is still open in a
  reply on #13, and every census group is mapped to a row or to none with its reason.
- **SC-003** (FR-003): `make money-candidates CHECK=1` exits 0; each era this feature defines is on
  `research/assets/money-eras-awaiting.json` or in gm-assistant's table; every amount of money (a sum paid or priced - not a rate
  between coins, a weight or an area) in the record's fragments within an era's years is marked with that era's id; only amounts
  outside every era this feature defines may be passed over with their reason.
- **SC-002** (FR-002, FR-004): `make record-owed` shows no unanswered unit for the touched questions at each landing, and
  `make impl-check F=412` reports nothing missing.

## Assumptions

- Japan first for prices and wages, China beside it (the issue's order).
- Three write sessions and one check session: the findings cite about 22 sources with no registry entry yet (counted from the
  passes, 2026-10-24), against a cap of ten new keys a write session. Session 1: question 1 into 0273, 0279 and 0265, and the
  Japanese wages of question 3 into 0250. Session 2: new questions A (the basket in Japan, era by era) and C (Japanese coins in
  silver). Session 3: new questions B (the basket and day wage in China, era by era) and D (Chinese money in silver), with
  China's wages beside them in B. Leads not followed are named, not chased; each is listed under what is still open.
- A spreadsheet the record cites (the GPIH files) is quoted cell by cell with its sheet and row (research/CLAUDE.md: a cell of
  a public spreadsheet is a readable page); the checks get row dumps.

## The findings, figure by figure (the passes, 2026-10-24; leads until read on the page)

**Which eras get a row (the issue's floor).** An era gets a row when at least rice is found for it, in the record or by the
passes: the issue, "a price per unit for each good found (at least rice)" and "rice alone is the floor". The census
(`passes/census.md`, the money questions and, in its addendum, every other fragment) names the record's priced groups; each
is mapped below to its row, or to none with its reason. The thirteen ids confirmed on #13 (issuecomment-6386690660) stand;
the rows the floor adds (`osaka-1700`, `osaka-1780`, `kyoto-1800`, `songjiang-1680`, a Song row, confirmed on #13 in
issuecomment-6386826304; `beijing-1500`, confirmed in issuecomment-6386920252) are marked once in the awaiting list.

| census group | row |
|---|---|
| 1 Kyoto 1745-54; 2 Kyoto wages; 10 Tama shrine work 1749-70 | `kyoto-1745` (the Tama work after 1770 by year below) |
| 9 Osaka 1620-28 | `osaka-1620` (1620-1650, as confirmed in issuecomment-6386920252) |
| 9 Kyoto 1652-56; 0185's 1611 and 1658 fees | none of their own: just outside `osaka-1620`; each may borrow it by the author's judgment |
| 8 Edo, Kyoto, Funai 1692-1737 | `osaka-1700` (1690-1739; Kumon's Osaka rice by decade) - new |
| 7 Ako, Edo, Nishinomiya 1781-91 | `osaka-1780` (1780-1789; Kumon) and `kyoto-1790` - new |
| 11 Kanto villages early 1800s; 0118's 1814 well | `kyoto-1800` (1800-1817; Mitsui Kyoto) - new |
| 3 Edo 1804-30; 14 Nada sake and Tosa charcoal | `edo-1818`, by year |
| 4 Morisada 1830s-53; 5 Edo and Kazusa 1842; 0185's 1843 | `edo-1830`, `edo-1850` |
| 13 Edo 1851-60 | `edo-1850`, `edo-1860` |
| 0216's 1897 yen; 0228's Meiji value (no year: no row borrowed) | `tokyo-1882` |
| 0115's servant wage of 2 ryo 2 bu a year; 0194's 4 mon a ken (no year: no row borrowed) | none |
| 6 Kashimo, Mino 1763-74 | none: rice for Kashimo SILENT; its amounts may borrow `kyoto-1745` by the author's judgment |
| 12 the Tokaido and Nakasendo post stations, 1611-1829 (official fares) | none of their own: no rice at the stations; each fare by its year above |
| 15 coin rates | none: rates, not prices (question 4 answers them) |
| 20 Ming 1397-1615 | `beijing-1615` (1573-1627); and `beijing-1500` (about 1490-1520, confirmed in issuecomment-6386920252: the official price table after the ruling of 1497, rice 25 guan a shi and a tael of silver 80 guan, 0272; ATTESTED ONLY FOR official prices); Ming before 1490: none, no rice found |
| 16 Beijing 1736; 17 Beijing rents 1727-31; 18 Qing provinces 1769 | `beijing-1736` (rice by Allen et al.'s reconstruction, labeled) |
| 21 Canton and the Yangzi delta 1700-1760s | `suzhou-1750` |
| 22 Songjiang 1630s-1688 | `songjiang-1680` (1670-1690; rice 2 taels a shi in 1680, cash rates) - new |
| 19 other Qing statutory prices 1646-1813 | by year to the rows above; none of their own |
| 23 rural Beijing wages 1807-1902; 24 Beijing 1821-1911 | `beijing-1820`, `beijing-1900` (an 1871 rent: none, no row between) |
| 25 tea and grain routes 1854-89; 26 Fujian, Yunnan, Fuzhou 1746-1902 | none: no rice with them |
| 27 Tang 764 | none: Tang rice not searched; listed open |
| Song (no amount in the record; the passes found rice by decade, Peng via Liu) | a Song row once question B writes its rice, its id proposed then |

- **Q1, salt in Kyoto 1745-54**: ATTESTED - Mitsui Bunko's Kyoto retail series as transcribed by Bassino (GPIH
  Japan_1710-1871.xls, sheet "Mitsui Bunko Kyoto T6"): 塩 per koku, 14.3-25.7 monme, the 20 seasons' mean 17.8. A sho's weight
  of salt: SILENT (searched; the per-kg figure is this project's arithmetic from a stated assumption, labeled).
- **Q1, fuel**: ATTESTED - the same sheet's 薪 per 10 kan (37.5 kg), 2.42-2.77 monme, mean 2.64: priced by weight, so no
  bundle weight is needed; a price per million BTU is this project's arithmetic with a wood energy figure labeled as assumed.
  Charcoal (炭): ATTESTED ONLY FOR Edo 1710-16 and 1818+ and Osaka 1818+ (no Kyoto column); the Osaka 1818-23 charcoal
  below firewood per 10 kan is flagged, checked against the sheet before it is cited.
- **Q1, a back-tenement room in Kyoto or Osaka**: SILENT (searched); the nearest, Edo 1804-30 at 300-500 mon a month (0265),
  named as the nearest.
- **Q1, salt per person a year**: ATTESTED ONLY FOR the Qing official reckoning - Huang Guoxin 2021, a little over 9 jin a
  year (1776-1850); Japan SILENT (searched).
- **Q2, Japan**: ATTESTED for the goods each series carries - Mitsui Bunko (Kyoto 1741-62 and 1791-1871; Edo and Osaka
  1818-71): white rice, wheat (麦, read as wheat by Bassino), salt, miso, sake, lamp oil, firewood, charcoal (Edo, Osaka);
  Kumon (GPIH Japanese Wages.xlsx): Osaka rice every decade 1610-1890, soybeans, barley, oils and cloth from the 1780s;
  Kimura (Osaka 1600-50): rice, soybeans, salt, oil, sake, cloth; Iwahashi: rice in 14 places 1620-1867. Fish, other beans,
  buckwheat and millets before 1880: SILENT. Rent beyond 0265: SILENT. Cautions carried: Kyoto salt from 1791 at a third of
  Edo's and Osaka's (a unit or grade change, flagged); Bassino and Ma's cloth (Osaka 1840s, ~19.9 monme a tan) against
  Kumon's 6-8.8.
- **Q3, Japan**: ATTESTED - Mitsui's 日雇賃 by year: Kyoto 0.72-1.31 monme in 1745-54, 0.85 in the 1790s, 0.94 in
  1804-29, 0.98 in 1830-44, 1.04 in the 1850s, 1.32 in 1860-67; Edo 0.90 flat 1818-59 (a book rate, said so), 1.14 in
  1860-67. Osaka 1620s 0.8-1.2 (0257, named). 1780s and 1872-79: SILENT.
- **Q4, Japan**: ATTESTED - chogin fineness by recoinage (jawiki's chogin articles citing 『旧貨幣表』 and the Meiji mint's
  assays): grams of pure silver a monme, Keicho 3.00, Genroku 2.40, Futatsuho 1.875, Eiji 1.50, Mitsuho 1.20, Yotsuho 0.75,
  Kyoho 3.00, Genbun 1.725, Bunsei 1.35, Tenpo 0.975, Ansei ~0.51; the koban's gold by recoinage; a ryo in silver by the market
  rate (0277's Osaka series from 1787; before it, a secondary chronology, labeled). Bassino and Ma's 3.11 g a monme: its basis
  SILENT in the paper - stated, with Bassino's own GPIH note that the content "is uncertain" (3.75 g in that file).
- **Q2-Q4, China**: ATTESTED ONLY FOR official prices in Beijing 1615 and 1736 (Gao 2022); ATTESTED for Canton 1835
  (Chinese Repository), Beijing 1900-1919 (Gamble 1921; Meng and Gamble via GPIH), the Lower Yangzi rice in cash (Qian Yong,
  履園叢話); ATTESTED ONLY FOR a modern reconstruction for Allen et al.'s Beijing database (its rice rescaled from the Yangzi,
  oils indexed to flour). Wages: Beijing 1736 75 cash, rural Beijing 1807-1902 (Allen, Gamble), Lower Yangzi 0.064-0.071
  tael (Liu 2022), Canton 0.1 tael, Beijing 1900s 19-27 cents. Money: the tael ~37 g (Allen; kuping 36.9-37.3 g, Liu), the
  dollar 0.72 tael, strings of 900-1,000 cash or fewer (Ma 2012), Beijing's jingqian counted double; cash a tael by point
  rates - Ming 700-800 (明史 卷81), 1737 800, 1760s-70s 720-900, 1796 1,300-1,400 (Qian Yong), 1820-30 1,159-1,329 (Allen).
  A market cash-a-tael series by decade: SILENT in any readable copy (Lin Man-houng, Peng, Yan Zhongping unread), listed open.

## Review history

- spec-fidelity round 1 (2026-10-24): NOT FAITHFUL - the row criterion against the issue's rice floor (Song, Songjiang); every
  census group to be accounted for, the Nakasendo by name; the census record-wide; FR-002 against the plan. All four applied
  (the row table, FR-006, the census addendum, FR-002).
- spec-fidelity round 2 (2026-10-24): CHANGES REQUIRED - group 20's reason false (0272's 1497 table: now `beijing-1500`); 0115 and
  0194 missing from the table (added); `osaka-1620`'s confirmed span widened (restored to 1620-1650, Kyoto 1652-56 and the fees of 1611 and 1658 mapped to none);
  FR-006 named by no task (T05 and D7 now name it).
- spec-fidelity round 3 (2026-10-24): CHANGES REQUIRED - request.md lacked the confirmation comment the spec cites (6386826304);
  request.md refreshed with the whole thread. The census's wrong date for the Takamiya fares corrected to 1665 (Kanbun 5).
- spec-fidelity round 4 (2026-10-24): CHANGES REQUIRED - `beijing-1500` still read as proposed, without its confirmed span;
  now confirmed, about 1490-1520, citing 6386920252.
- spec-fidelity round 5 (2026-10-24): FAITHFUL.
- Amended after round 5 (2026-10-24): SC-003 added for FR-003 (the spec linter: FR-003 was named by no success criterion).
- New pass, round 1 (2026-10-24): CHANGES REQUIRED - SC-003 let an amount inside an era's years be passed over; now every
  amount of money within an era's years is marked, pass-overs only outside every era; T06's verify line follows.
- New pass, round 2 (2026-10-24): FAITHFUL.
