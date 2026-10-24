# Feature 414: how stable prices were, over what spans and for which goods, and when a borrowed price needs a note (diagram#15)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files on this repository to be worked (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future"). The issue quotes the GM's own request of 2026-10-24.

**Input**: `request.md` (issue #15 and its thread, verbatim, including the GM's addition on question 2, issuecomment-6386761232),
`passes/` (four search passes, 2026-10-24: `japan.md`, `qing.md`, `modern-yardstick.md`, `salt-periods.md`), and
`measure/mitsui_stability.py` with its output (this project's arithmetic from the Mitsui Bunko series).

## Why

The tooltip of feature 413 converts an amount at an era's rates, and names a borrowed era. How far an era may be borrowed was
first set at "about 25 years" with no basis; the GM withdrew it and asked for it to be measured: how much prices moved at every
time scale, which goods were steady and which swung, how far places differed, and from those a closeness rule. He added that
each good's price should be shown across periods (dynasties, Edo sub-periods) with what drove the differences - salt and the
reach of its monopoly first.

## User Scenarios & Testing

### User Story 1 - each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue's four questions and the GM's addition, the fragment file, the verdict and what is
still open: (1) the overall price level's movement at each scale from within a day to a century, trend against swing, the shocks
dated, a modern fiat yardstick beside it; (2) per good or class, its swings at those scales, seasonality, and - per the GM's
addition - its price in each period the record reaches in a common measure, how far apart the periods were, and what drove the
difference; (3) the spread between places at one time, and what drove it; (4) a closeness rule with its basis.

**Acceptance scenarios**:

1. Each verdict is one of the four of `research/money-requests.md`, at EVERY scale the request names: within a day, day to
   day, week to week, month to month, year to year, decade to decade, century to century. A scale no source measures is SILENT,
   with the search and with what the sources do say about it (the trading structure, a daily series that exists unread); month
   to month gets its own verdict (the sources' monthly figures, and this project's arithmetic from the daily Osaka series where
   it can be read).
2. Every figure this project computes from a series is labeled as its arithmetic, names the series, the city and the measure
   (the standard deviation of log changes, or a coefficient of variation where the source uses one), says how many pairs or
   years it rests on, and is reproducible from a script in `measure/`. The long-run drift - the mean change per decade and per
   century - is given beside the swing wherever a series allows (the request: "the long-run drift per decade and per century").
3. The modern fiat-era yardstick (US and Japanese CPIs, a staple's modern retail price, and Rolnick and Weber's commodity against
   fiat inflation) is a COMPARATIVE source (research/CLAUDE.md, "Comparative money sources"), written in a question of the
   Comparative money section and set beside the Japan and China figures in the reply. A premodern European series (England's
   price level, Clark's goods) is not written unless the GM approves it, asked through `escalation-check` (comparative sources are
   "not sought out unless the GM asks for it or approves it").
4. The closeness rule (question 4) gives BOTH bounds the request asks: how far in time and in place an amount may be converted at
   another era's or place's rates before the conversion must say so, and how far before it should not be made at all; it answers
   whether either differs by good class and by the size of the amount (or says the measurements give no basis to); it is split
   by period only where the measurements force it (the 1859 break); it states its derivation and the pairs it rests on, and is
   labeled as this project's derivation (no source states such a rule: the passes searched and found none).
5. Every good the request and its basket name gets a verdict at the scales its sources allow, SILENT at worst: rice, soybeans,
   other grains (barley and wheat, buckwheat and millets), other beans, fish, edible oil, cloth (cotton, and other cloth where the
   sources price it), lamp oil, salt, fuel, housing (rents),
   crafted goods, services, and the unskilled day wage.
6. The GM's addition is answered in a common measure the sources support: days of an unskilled wage per local unit - per jin for
   the Song, Ming and Qing, per sho for Edo - the Song's resting on a second-hand wage (ATTESTED ONLY FOR that wage, the rice
   measure beside it); Japan and China side by side, not converted (no source gives a sho of Edo salt's weight).
7. Each answer says how it stands against the canon its question names (question 1: the conversion table treats an era as one
   price level; question 2: the standard basket and the day wage; question 3: one place per era; question 4: 413's marking);
   where history contradicts it, the reply says so and the contradiction goes to the GM through `escalation-check`.

### Edge cases

- Two currencies, two drifts: Qing rice rose about fourfold in copper cash over the 1700s while its silver price showed no marked
  trend; the record states both and does not pick.
- A series with a unit break (Kyoto salt from 1791) or a book rate (Edo's flat day wage of 0.90 monme, 1818-1859) is named as
  such beside any figure computed from it, and left out of a rule it would distort.
- An administered price (Changlu salt, fixed by decree for decades) is not a market price: ATTESTED ONLY FOR the administered price.

## Requirements

- **FR-001**: Every figure of the issue and of the GM's addition gets, in the reply on #15, its fragment file, its verdict and
  what is still open.
- **FR-002**: The findings are written into the record under the citation rules, checked by the record checks `make record-owed`
  names: new money questions on (A) how steady prices were at each time scale, good by good, in Japan and China; (B) how far
  prices differed from place to place; (C) how each good's price moved from one period to the next and why (the GM's addition,
  salt first); (D) when a price borrowed from another year or place needs a note, and when it should not be borrowed at all (the
  closeness rule); and (E) a comparative question, the modern fiat-era yardstick. Existing questions are named, not repeated (0273 salt, 0277 copper, 0280-0283
  carriage and distance, 0250 wages).
- **FR-003**: The closeness rule, once written, is offered to feature 413's marking as the author's guide and to gm-assistant as
  the tooltip's disclaimer rule; whether it becomes a record check is put to the GM through `escalation-check` (the GM asked that
  the number rest on something; he did not ask for a check).
- **FR-004**: The feature closes with `make impl-check F=414` (money questions: no code implements them).
- **FR-005**: Replies are posted on #15; gm-assistant verifies and closes it.
- **FR-006**: Each answer is set against the canon its question names, and a contradiction is escalated to the GM through
  `escalation-check` (`research/money-requests.md`).

## Success Criteria

- **SC-001** (FR-001, FR-005): every figure of the issue and its addition carries a fragment file, a verdict and what is still
  open in a reply on #15.
- **SC-002** (FR-002, FR-004): `make record-owed` shows no unanswered unit for the touched questions at landing; `make impl-check
  F=414` reports nothing missing; `measure/` reproduces every computed figure the questions cite.
- **SC-003** (FR-003): the rule's offer to 413 and to gm-assistant, and the question of a check put to the GM, are in the reply.
- **SC-004** (FR-006): the reply names, per question, how the answer stands against its canon, and any contradiction's
  escalation.

## Assumptions

- Japan first, Qing alongside, the modern figure beside both (the issue's order).
- Write sessions: about 30 new registry keys across the passes (counted 2026-10-24), against ten a write session: three write
  sessions (A and B; C; D and E) and one check session, after feature 412's sessions in this clone.

## The findings, figure by figure (the passes and this project's arithmetic, 2026-10-24; leads until read on the page)

- **Q1, within a day, day to day, week to week**: SILENT on size in both countries. Japan: daily Osaka rice series exist (the
  Mitsui exchange office's diary, RIEB database 1787-1871; Takatsuki 2007 uses a daily series 1798-1859 for efficiency, not size);
  the Dojima market's opening, closing and halts are described (Takatsuki). China: nothing finer than monthly reports.
- **Q1, within a year and year to year**: ATTESTED. Japan: Osaka spot rice's within-year coefficient of variation about 3-8%,
  15-24% in famine years (Miyamoto 1975); the general level's within-year CV 7-8% before 1859, 16% after (Shinbo 1975). This
  project's arithmetic from Mitsui (to 1858): rice's SD of log change over half a year 12.0% in Kyoto (173 pairs), 14.4% in Edo
  (80), 13.6% in Osaka (77); over a year 15.2%, 17.3% and 17.1%. China: 18th-century rice's half-year SD about 9% (Europe 13%), the year-to-year CV about 0.12 (Shiue 2002; Shiue and
  Keller).
- **Q1, month to month**: ATTESTED ONLY FOR the within-year spread - Osaka spot rice's monthly prices within a year, CV about
  3-8%, 15-24% in famine years (Miyamoto 1975); China, 1770-1860, a mean monthly grain-price change of 1.1% with an SD of 2.4 in
  storage months (Keller, Shiue and Wang, appendix Table A.4). This project's arithmetic from the daily Osaka rice series (the
  RIEB database, archived) is to be computed in `measure/`, or the scale stays at the sources' figures.
- **Q1, decade to century, trend against swing**: ATTESTED. Japan: Mitsui rice's SD of log change, to 1858, at 5, 10 and 25
  years: Kyoto 25.4%, 27.6% and 28.6% (80, 70 and 43 pairs) - scarcely larger at 25 years than at 5 (28.6% against 25.4%), a level prices swung around; Edo
  33.9%, 37.5% and 15.9% and Osaka 27.5%, 33.3% and 18.1% (the 25-year figures on 16 pairs each). Drift, nominal monme, first to
  last yearly mean to 1858, each first point a lone early observation before a long gap: Kyoto rice -0.5% a decade (1713, then
  1741-1762 and 1791-1858), Osaka +0.1% (1713, then 1818-1858), Edo +3.9% (1710-1716, then 1818-1858) (this project's
  arithmetic); Shinbo's index down 13%
  1804-1820, up 36% from 1802-29 to 1830-58, then about fourfold 1858-1865; the Bank of Japan's 350 kg of rice a ryo early Edo,
  150 kg mid-to-late, 15-30 kg in 1867. China: in copper, Suzhou rice about fourfold over the 1700s (Qian Yong; 全漢昇 1957); in
  silver, about +0.06 tael a shi a decade, "not marked" (Lu and Peng 2004); cash a tael about 1,000 to 2,000 by 1850, then 5,000-
  8,500 in 1856-1880 (Allen et al.'s Beijing series).
- **Q1, shocks**: ATTESTED - Kyoho famine 1732 (rice about doubled in 3-4 months), Tenmei 1783-87, Tenpo 1833-38 (3-4 times
  normal), the recoinage of 1818-29, the 1859 opening and its inflation; China 1642, 1651, 1669-70, 1680-81, 1707, 1755, 1785, the
  Taiping years. The recoinages of 1695-1736: SILENT (searched).
- **Q1, the modern yardstick**: ATTESTED (COMPARATIVE) - US CPI 3.9% a year since 1971, annual SD 1.1 in 1983-2019; Japan 2.3% a
  year since 1971, SD 0.86 in 1995-2019; commodity-standard inflation 1.0% a year against 13% under fiat (Rolnick and Weber 1995);
  US rice and flour's 12-month SD about 9% today (BLS average prices). England's premodern series (the Bank of England's
  millennium dataset, Clark) was found and waits on the GM's approval (FR-002 E).
- **Q2, goods without a lead yet**: fish, other beans, buckwheat and millets, crafted goods and services - each gets a verdict
  from the Mitsui and Shinbo series where they carry it, SILENT with the search where none does.
- **Q2, goods**: ATTESTED - Shinbo's Table 5: farm goods (rice, soybeans, wheat) swung most, cotton cloth least (within-year CV
  1.7-8.5), fuel and oil between; this project's arithmetic from Mitsui matches (year SD to 1858: firewood 3.2% in Kyoto and 6.6%
  in Osaka, soy sauce 3.9% and 6.9%, rice 15.2% and 17.1%); rents sticky (+10-20% over decades in which the price level nearly doubled, Washizaki 2012); wages: Mitsui's retained
  craftsmen fixed, the market's day laborers flexible (Saito 1993); Qing copper wages flat 1807-1853 while cash a tael doubled, then
  catching up in steps (Allen; Liu 2022). Seasonality: Japan's rice rose from the first month to the seventh to ninth and fell back
  (Miyamoto via Kato); Mitsui's autumn over spring about +2-4% for rice (this project's arithmetic); China +12-14% from the 2nd to
  the 8th lunar month (Shiue 2002), +60% in the crisis of 1651 (閱世編).
- **Q2, across periods, and what drove it (the GM's addition)**: salt ATTESTED in days of an unskilled wage per local unit (the
  pass's arithmetic): Song about 1.2-1.75 days a jin (ATTESTED ONLY FOR a second-hand wage of 40-50 cash), Ming about 0.2 (Wanli,
  a Board of Works wage), Qing about 0.13 at Beijing in 1736 and 0.35-0.8 days a jin in the far Huai markets about 1830 (ATTESTED
  ONLY FOR a rural Beijing wage, a different region), Edo 0.14-0.5 days a
  sho (0273); and in each period's own terms:
  Song - a jin of salt about a dou of rice before 1068, about a fifth of one by 1122 as rice rose and the decreed price stood
  (宋史 卷182); official retail 40-120 cash a jin against 4-8 paid the producer, "profit up to tenfold"; Hebei's price doubled when
  the monopoly reached it in 1084; private salt a third under official in Sichuan in 1086 (宋史 卷183). Ming - the license price
  tenfold the founders' by 1534, which a censor blamed for smuggling (明史 卷80); Beijing retail 0.006-0.007 tael a jin under
  Wanli, about a fifth of a laborer's day a jin (高壽仙 2022; the pass's arithmetic). Qing - 12-16 cash a jin at the administered
  Changlu price (1688-1736) against 60-70+ in the far Huai markets about 1830, private salt about half the official there (吳海波,
  citing Tao Shu); 2-cash cuts "to beat the smugglers" (1791, 1848); the ticket reforms of 1832 and 1849 more than halved the
  license's cost and prices "fell abruptly" (清史稿 卷123). Japan - no shogunate-wide monopoly, but domain monopolies in Kanazawa
  and Sendai through the period and Ako in 1680- and 1809-1821 (kotobank); the record's Edo prices 0.14-0.5 days a sho (0273).
  Japan and China are given side by side, not converted: no source gives a sho of Edo salt's weight. Other goods, Beijing
  official prices 1615 against 1736: food and fuel about doubled in silver, cotton cloth flat, pig iron down, silver's long fall
  in purchasing power the driver named (高壽仙 2022, citing 彭信威); 17th-century Songjiang cotton swinging while cloth held
  (閱世編).
- **Q3, places**: ATTESTED ONLY FOR co-movement, not level spreads, in the literature - Kyoto and Osaka in parallel (Shinbo); Otsu
  following Osaka within 1-2 days (Takatsuki 2012); Edo and eastern Japan diverging more (Bassino and van der Eng); Qing rice
  correlations 0.8 within 150 km on waterways, near zero beyond 1,000 km between provincial capitals (Shiue and Keller). Level
  spreads, this project's arithmetic from Mitsui, 1818-1858: rice in Osaka about 1% above Kyoto (SD 4%), Edo about 3% (SD
  10%); firewood in Edo a third below Kyoto and in Osaka 43% above; Kyoto salt three to four times below the other two, read as a
  unit change in the series from 1791 and left out of any rule (`measure/mitsui_stability.out.md`).
- **Q4, a rule**: SILENT in every source searched; to be derived (FR-002 D), labeled as this project's derivation.

## Review history

- spec-fidelity round 1 (2026-10-24): CHANGES REQUIRED, eight findings - month to month without a verdict; drift not a figure;
  the rule's two bounds and the size of the amount; the Song salt measure; figures without their city; the canon lines; the
  goods with no lead; England unrequested. All applied (acceptance 1-7, FR-002, FR-006, SC-004, the findings; the script
  computes drift).
- spec-fidelity round 2 (2026-10-24): CHANGES REQUIRED - the eight items resolved; four clauses: cloth not only cotton and
  other grains as the category; "scarcely larger" at 25 years; the Huai wage caveat; each drift figure's span. All applied.
- spec-fidelity round 3 (2026-10-24): FAITHFUL.
