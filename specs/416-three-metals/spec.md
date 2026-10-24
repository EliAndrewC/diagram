# Feature 416: gold, silver and copper as separate monies (diagram#16)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files on this repository to be worked (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future"). The issue quotes the GM's own words of 2026-10-24.

**Input**: `request.md` (issue #16, verbatim), `passes/` (two search passes, 2026-10-24: `japan.md`, `china.md`)

## Why

Rokugan's coinage is decimal and fixed (1 koku = 10 bu = 100 zeni = 1,000 sen); history's was not. The GM wants the record to
know what the reality was - legal against market rates, who priced and paid in which metal, whether a price depended on the coin
paid, and who gained and lost when the rates moved - so he can decide how much of it to import into play (the request: "I want
our research to at least know what the actual reality was so we can decide how much of that to import").

## User Scenarios & Testing

### User Story 1 - each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue's four questions, Japan first and Qing (and Ming where found) beside it, the
fragment file, the verdict and what is still open: (1) per era, the legal rate between the metals, who set it, its enforcement,
the market range and the fixed-by-count ratios, with the dates of changes; (2) the pattern of which metal priced and paid which
transaction - wholesale against retail, Edo's gold against Osaka's silver, wages, rents, taxes, a samurai stipend, a shop
purchase - by kind and region, and the changers' fees as a percentage; (3) examples of a price depending on the coin paid, with
dates - a premium or discount for paying in gold, and for paying in debased coin - and how fast copper-quoted prices followed a
move in the rate; (4) who gained and who lost - wage earners paid in copper, taxpayers owing in silver, merchants, samurai on
rice stipends - the size of the effect on a laborer's real wage and on a tax burden in named episodes, and what people did.

**Acceptance scenarios**:

1. Each verdict is one of the four of `research/money-requests.md`; a figure no source gives (a retail cash shop's fee in China;
   how fast Edo's copper prices followed the rate outside 1842; a Meiwa-An'ei real wage in copper; a premium for paying in gold in
   Japan or in Qing China, if the write session's search finds none) is SILENT with the search.
2. What the record already holds is named, not repeated: 0277 (Japan's legal rates of 1700 and 1842, the Osaka and Edo market
   series, the 1843 floor); feature 412's coin questions (the chogin's fineness, the koban's gold, the nanryo and ichibu-gin's
   silver against their face; cash a tael by era); feature 414's (copper wages against the rate).
3. Each answer says how it stands against the canon its question names (question 1: Rokugan's fixed decimal coinage, `l7r.md`
   "Money"; question 2: who uses which coin, the money skill's "Coins and who uses them"; question 3: the conversion table's
   route through silver; question 4: none); where history contradicts the canon the reply says so, and the contradiction is
   put to the GM through `escalation-check` (`research/money-requests.md`) - here the point of the request: material for him
   to decide what to import, not a correction of the canon.
4. A percentage this project computes (a fee from a stated sum, a premium from two rates) is labeled as its arithmetic.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #16, its fragment file, its verdict and what is still open.
- **FR-002**: The findings are written into the record under the citation rules, checked by the record checks `make
  record-owed` names: two new money questions, (A) gold, silver and copper as monies in Edo Japan (the four questions), and (B)
  silver and copper as monies in Ming and Qing China (the four questions); 0277 and features 412 and 414's questions named, not
  repeated.
- **FR-003**: Each answer is set against its question's canon, a contradiction escalated through `escalation-check`.
- **FR-004**: The feature closes with `make impl-check F=416` (money questions: no code implements them).
- **FR-005**: The reply is posted on #16; gm-assistant verifies and closes it.

## Success Criteria

- **SC-001** (FR-001, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open in the reply
  on #16.
- **SC-002** (FR-002, FR-004): `make record-owed` shows no unanswered unit for A and B at landing; `make impl-check F=416` reports
  nothing missing.
- **SC-003** (FR-003): the reply names, per question, how the answer stands against its canon, and any escalation.

## Assumptions

- Japan first, Qing (and Ming) beside it (the issue's order).
- Two write sessions (A; B) and one check session, after features 412 and 414's sessions: about 18 new registry keys across the
  passes (counted 2026-10-24), against ten a write session.

## The findings, figure by figure (the passes, 2026-10-24; leads until read on the page)

- **Q1, Japan**: ATTESTED - legal rates set by shogunal order: 1609 (1 ryo = 50 monme = 4 kanmon), 1700 (60 monme = 4 kanmon,
  changers forbidden to deal at 58 monme or less, or 3,900 mon or less), 1842 (6,500 mon a ryo, the 1843 Osaka floor in 0277);
  each a revision to follow the market (jawiki 御定相場, 三貨制度; the Bank of Japan museum's catalog). Enforcement: orders to
  changers, Ooka's summons of 1736, the shogunate buying copper (1796) and selling it (1829), posted orders banning other
  provinces' copper (1813, 1842) with seizure and penalties reaching the town officials (Oishi 1966, the orders printed); a
  prosecution: SILENT. The market's straying: silver about 48-50 monme against the legal 60 (1695 to the Hoei recoinages);
  copper 2,800-3,700 mon against 4,000 (about 1700-1737), 5,000-7,000 from 1769, about 10,000 by the late 1860s against the legal
  6,500. Fixed by count: the gold ryo = 4 bu = 16 shu throughout; counted silver tied to gold units (the five-monme piece of
  1765, 12 to the ryo, which failed; the nanryo nishu of 1772, 8 to the ryo; the ichibu-gin of 1837, 4) - weighed silver drained
  out and survived in Osaka as a unit of account; the changers' resistance to the nanryo (a 25% premium demanded; the
  shogunate's fixed allowances and interest-free loans).
- **Q1, China**: ATTESTED - Qing: 1,000 cash a tael set by the court conference and the Board of Revenue in 1653 (after 700 in
  1645); the 1684 ban on fewer than 1,000 held only on paper (770-880 in the late Kangxi years); treasury cash released and
  official brokers appointed (1737); old light coin legally at 0.7 tael a thousand (1702); about 2,000 by 1837; the Xianfeng notes
  priced by the state at 2,000 cash a tael, redeemed at 70% in Beijing, about 3% of face by 1861; the ten-cash piece passing for
  two standard cash, and only inside Beijing (清史稿 卷124; Morse 1908). Ming: paper legally 1 guan = 1,000 cash = 1 tael of
  silver, gold 1:4 against silver (1375), fallen to 16% of face by the 1390s and below one cash by the Chenghua years, the silver
  ban relaxed in 1436 and lifted under Tianshun (明史 卷81).
- **Q2, Japan**: ATTESTED for the pattern - large sums in gold in the east and in silver in the Kinai and the west, the rice price
  quoted per koku in monme in Osaka and as rice per ryo in Edo; retail and small wages in copper everywhere; the Kanto upland tax
  reckoned in ei and paid in gold; tax assessed in koku and paid in rice and money in set shares; stipends paid in rice and
  turned into cash by the fudasashi at the day's price; domains settling outside trade in shogunal coin and inside trade in han
  notes and copper (Kano; Iwahashi 2010; the museum's catalog); rents both ways - Edo back-tenement rents in mon, a carpenter's
  house in monme (0265, named) and Minami-Denmacho's ground rents in monme (Washizaki 2012, in 414's pass). Changers' fees: ATTESTED ONLY FOR the 1859 copper recall
  (about 3.2%, this project's arithmetic), the nanryo allowances (about 0.7% and 1.3%), the fudasashi's 3 bu per 100 bales; the
  common "1-2%" carries no citation (jawiki 両替商): SILENT as a sourced figure.
- **Q2, China**: ATTESTED - silver for tax, salt levies, official pay and long-distance trade; copper for retail, household salt,
  hired labor and materials (明史 卷81 for 1436; 清史稿 卷123 for 1728; 朱嶟's memorial of 1846: seven or eight in ten farmers paid
  their silver tax in copper, converted by the county); the land tax in silver from the 1436 commutation and the Single Whip of
  1581 (明史 卷78); silver weight and fineness standards against the treasury tael (漕平 1.8%, 市平 4.1%, 京平 5.9% lighter;
  fineness 2-5.6% discounts; banks' two-weights spread 0.25-0.5%), Morse 1908, late Qing. Rents both ways - Beijing bays in
  taels in 1727 and in cash by 1871 (0265, named). A retail cash shop's fee: SILENT.
- **Q3, Japan**: ATTESTED ONLY FOR named cases - Edo 1842: the ordered price cuts of about 7-8% applied only to copper-priced
  goods, silver-priced goods exempt, and the cuts doubtful (Oishi); Tsugaru 1837-38: goods priced in coin and in han notes, the
  notes at two-thirds of face and then 28% (Iwahashi 2010); Edo 1854-1868: copper coins of one face value passing at different
  values, legalized in 1865 and raised in 1868 (jawiki 寛永通宝); the Tenpo coin at about 80 for its face 100; full-weight old
  coin passing only with a premium after recoinages; Sengoku bad coin at a discount (four bita to one good mon at one point;
  Nobunaga's grading of 1569). A premium or discount for paying in gold: not searched by the passes - the write session searches
  it (金払い 打歩, 小判 増歩, 金建て 値引), SILENT with the search if none. How fast copper prices followed the rate outside 1842:
  SILENT.
- **Q3, China**: ATTESTED - copper-quoted prices mostly sticky while the silver rate moved (salt 1728; rice about 1850, Zeng
  Guofan; Beijing wages, 414), one dissent (朱嶟, 1846: "prices dearer by the day"); prices depending on the means of payment in
  Xianfeng Beijing (sellers raising the price or hiding goods for notes; big cash refused or discounted); light coin legally at
  70% (1702); the salt price raised in silver about two years after the 1728 complaint. Paying in gold: Ming law banned trading
  in gold and silver (1375, renewed 1397) and set 4 guan of paper to a tael of gold (明史 卷81); for Qing a premium or discount
  for paying in gold was not searched by the passes - the write session searches it (金價 折算 交易, 黃金 兌換 銀 清代, 赤金
  市價), SILENT with the search if none.
- **Q4, Japan**: ATTESTED qualitatively, measured only for 1842 - commoners earning and spending copper and small copper-trading
  merchants losing when copper fell (the orders of 1796, 1813, 1842; Oishi linking the Tanuma-period fall to that period's
  risings); Edo craftsmen's copper wages not falling when rice fell after 1836 (ordered cut, 1842); the 1860s real wage falling
  more in the silver west than the gold east (Saito 1993); recoinage gains to the shogunate (5-5.5 million ryo in the Bunsei and
  Tenpo recoinages; 68% of the 1863 revenue) or, under Genbun's premium method, to holders of old coin (Kobayashi 2017); samurai
  on rice stipends losing in the Shotoku deflation and the cheap-rice years, made at the level of domain finances (Kobayashi
  2017; jawiki 三貨制度); merchants: the changers' gains and losses at the nanryo (above). What people did: hoarding good coin
  (Genroku; 1736), refusing or discounting coin (1854-1865; Sengoku coin sorting), the changers' resistance to the nanryo,
  riots (Oishi); a wage earners' petition: SILENT. A Meiwa-An'ei real wage in copper and a measured tax burden: SILENT.
- **Q4, China**: ATTESTED ONLY FOR taxpayers, officials, the state and soldiers - the land tax measured in rice doubled (3 dou to
  6 dou a mu as the rate went from 1,000 to 2,000, Zeng Guofan about 1852); a county's conversion adding 135% in Henan, 1905
  (Morse); local officials losing on remitting silver (1846); Jiangsu's grain tribute in arrears every year from 1836; soldiers
  paid at 2,000 against a market of 1,500 gaining (Hu Linyi); tax resistance and four named riots. Wage earners: only 414's
  inference (copper wages flat).

## Review history

- spec-fidelity round 1 (2026-10-24): CHANGES REQUIRED - rents, a premium for paying in gold, and question 4's samurai and
  responses had no verdict. Applied: User Story 1 names each kind and group; the findings carry rents (0265, both ways), the
  gold premium (to be searched), the samurai, the merchants and what people did.
- spec-fidelity round 2 (2026-10-24): CHANGES REQUIRED - the gold case had no China verdict. Applied: Q3 China names the
  Ming gold bans and rate and sends the Qing case to the write session's search (SILENT if none); acceptance 1 names both
  countries.
- spec-fidelity round 3 (2026-10-24): FAITHFUL.
