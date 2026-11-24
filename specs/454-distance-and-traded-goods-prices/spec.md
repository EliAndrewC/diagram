# Feature 454: what distance did to the price of traded goods - both ends' prices, sea freight, traders' margins and coastal ships (diagram#24)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future"

The GM asked this session to work the research requests filed as issues (2026-11-24: "Please take a look at our GitHub issues because there are a number of research requests which I would like for you to handle."); a money research request
gm-assistant opens for him is approved by his asking.

**Input**: `request.md` (issue #24 verbatim), `passes/` (five search passes, 2026-11-24: `a-ratios-japan.md`, `b-ratios-china.md`,
`c-margins.md`, `d-sea-freight.md`, `e-ships.md`)

## Why

gm-assistant's price ledger holds one low-high range per item with no place in it, so it cannot say how much dearer a good is far from
where it is made. The GM is pricing a smuggler's coastal cargoes (tea, sugar, raw silk, iron) sold in ports far from where they were
produced, and needs the historical gap between the producing region and the consuming city, the cost of carrying goods by sea, and what a
trader kept. The record holds land and river freight (0280), how far goods traveled (0281), how tea traveled (0282) and a famous good far
from home (0283); it has neither the price at both ends at one date, nor the sea leg, nor a trader's margin, nor the ships.

This feature records only the history. What the gap is in Rokugan stays with the money skill and the GM.

## User Scenarios & Testing

### User Story 1 - Each question and figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per question and per figure of the issue, the fragment file, the verdict and what is still open, in the issue's
priority order (question 1, then 3, then 2 and 4):

- **Question 1**, per good: the price where it was made (farm gate, producer's market or regional wholesaler) against the price in the city
  where it was consumed, at the same date; how far apart the two places were and how the good traveled (sea, river, land); the ratio of
  consuming-city price to producing-region price as a plain number with the distance; and each end's price per unit weight in silver (grams
  per kg). Japan first: tea (Uji or Suruga against Edo or Osaka), sugar (Satsuma, Ryukyu, or the Sanuki and Awa white sugar against Osaka or
  Edo), raw silk (the Joshu, Shinshu or Fukushima districts against Kyoto's Nishijin weavers), iron (Izumo or the Chugoku tatara iron against
  Osaka). Then China: tea (Fujian or Anhui against Beijing or Canton), raw silk (Jiangnan against the north), sugar (Guangdong or Fujian
  against the Yangzi or Beijing). Spices, incense woods and medicinal roots where a source turned up.
- **Question 3**: the share of the selling price a merchant kept after costs, for a wholesaler between producer and city and for a
  shipowner who bought at one port and sold at another on their own account (against carrying freight for hire); what one round voyage
  returned on the cargo's value; how many voyages a year; and China's coastal and Yangzi merchant houses where records exist. The figures: net
  margin as a percent of selling price per kind of trader, return per voyage as a percent of cargo value, voyages a year.
- **Question 2**: what carrying goods by sea along a coast cost per weight and distance and how long the voyage took - the Higaki and Taru
  ships on the Osaka-Edo run, the Kitamaebune on the Sea of Japan route, the rice-transport rates; China's coastal junk trades (the sand
  junks north of the Yangzi, the Fujian junks); and how sea freight compared with the river and pack-horse rates of 0280-0283. The figures:
  silver per 100 kg per 100 km (or per koku of burthen per voyage, with the distance), and voyage days for a named run.
- **Question 4**: how large ordinary coastal trading ships were in koku of burthen, how many crew each size carried and what they were paid,
  what a ship cost to build and how long it lasted, and what chartering one cost - the bezaisen classes (the 1,000-koku ship and the smaller
  coasters) and China's coastal junks. The figures: burthen, crew, crew pay in silver per month, build cost, working life, charter per voyage
  or month.

**Acceptance Scenarios**:

1. Each good, each kind of trader, each route and each figure carries one of the four verdicts of `research/money-requests.md` (ATTESTED,
   ATTESTED ONLY FOR, NOT ATTESTED, SILENT). A figure for a neighboring good, place, trader or century is not an answer to the figure asked:
   that figure is SILENT, the nearest named under what is still open.
2. Each price is given first in its source's own units; a conversion to grams of silver per kg, to silver per 100 kg per 100 km, or to a
   percent the source does not state is this project's arithmetic, labeled, with what it rests on (the coin's silver from 0287 and 0289, the
   unit's weight, the distance and where the distance comes from).
3. What the record already holds (0280, 0281, 0282, 0283, and 0279's charcoal far from home) is named by file, not repeated; the comparison of
   sea freight with river and pack-horse rates is drawn against 0280's own figures.
4. The canon beside each question is quoted beside the history, never altered: the 15% gate tariff, the charcoal rows' model of kiln price
   plus freight, tariff and margin, and the Sparrow's tea (`setting/l7r.md`) (question 1); the river freight row and the Yasuki harbor (question 2); interest of 15-20% a year in cities
   and about 25% in the countryside, and the 15% gate tariff (question 3); the Imperial koku (question 4).
5. Where the history contradicts the canon or the ledger's model, the answer says so, and the contradiction goes to the GM through
   `escalation-check`.

### Edge Cases

- A producer paid in kind (Satsuma's islanders, paid in rice for sugar): the ratio is given in the terms the source gives, and a silver
  ratio only as labeled arithmetic or a named author's figure; two figures that disagree are both given.
- A producer's COST against a city price (an ironworks' estimate, a shipper's cost) is that, never a producer's selling price.
- A pair whose two ends are of different dates, teas, or units that cannot be put on one basis from the sources (a bolt against a weight), is not a pair: no ratio is stated from it, and the figure is SILENT.
- A consuming city other than those the issue names for that good (Taiwan sugar sold at Yokohama, tea at London) is ATTESTED ONLY FOR that route.
- A figure after the premodern window (Japan after 1868, China after 1912) or from a modern summary without a date is given with its date
  and what it is, and carries no verdict for the period asked.
- A text read through machine reading of a scan is cited only where the passage was read on the page image.
- A source on another society's money is not sought; none of the passes used one.

## The findings, figure by figure (the passes, 2026-11-24; leads until read on the page)

**Question 1, Japan** (`passes/a-ratios-japan.md`):
- Raw silk: ATTESTED. Kyoto against Maebashi (Joshu), 1830-49, per kan in ryo (1836: 6.028 against 5.844); Kyoto over Maebashi 1.01-1.28,
  mostly 1.03-1.15 (this project's division of the two series); Kyoto over the Fukushima district 0.98-1.43, mostly 1.20-1.43, from the
  source's own index. Shinshu: SILENT in the pass. Grams of silver per kg as arithmetic (about 362 against 351 in 1836).
- Sugar: Satsuma black sugar ATTESTED ONLY FOR the rice-exchange terms - in 1830 islanders needed 4.2-6.4 times the Osaka-rate amount of
  sugar to buy a koku of rice (the source's own figure); a 2018 paper's Tenpo figures work out to about 9 in silver while the paper says 6.2,
  both given. Ryukyu apart from the Satsuma islands: SILENT. Sanuki and Awa white sugar: SILENT (the Kagawa paper unreadable, a lead).
- Iron: ATTESTED ONLY FOR Harima (Shiso), 1736-41, an ironworks operator's annual estimate of production cost against the Osaka sale -
  split iron 72.74 against 83.90 monme per 32-kan load, long bar 60 against 68.4, carriage to Osaka 7 monme a load; 1.15 and 1.14 by this
  project's division. Izumo and Iwami (1830s): producer-end figures only, about 38-40 monme a load of pig iron, so SILENT as a pair.
- Tea: SILENT. Uji has the shogunate's fixed price for its own tea (78, 52 and 26 monme a kin by grade from 1642), never resold; Edo has
  1842 retail prices (88-500 mon per 200-me kin); different teas, not a pair. Suruga against Edo: SILENT. Three leads untried (the 1852
  handbill, the Kyoto tea-industry history, the Suruga producers' dispute with the Edo tea wholesalers), tried once in the write session.
- Neighbors: safflower, Mogami to Kyoto, 1737-63, the shipper's cost against the Kyoto sale 0.92-1.33, ATTESTED ONLY FOR that; rice, Osaka
  over Fukui about 1.1-1.25 in the 1780s-1830s, ATTESTED. Spices, incense woods, medicinal roots: SILENT for Japan.
- Distance and how each traveled: as each source says, else SILENT with the route named; a distance from a map is this project's and labeled.

**Question 1, China** (`passes/b-ratios-china.md`):
- Tea: ATTESTED ONLY FOR the hills against the export port. Wuyi Congou to Canton, 1824-26 (Ball 1848, Appendix): 11.91 taels a picul in the
  hills, 20.50 delivered at Canton, 1.72; the gap itemized (carriage and duties 3.92, interest 2.40 and 0.36, chests and packing 1.31, the
  factor's profit 0.60). To Shanghai, 1846-49 (Fortune 1852): the farmer 4 taels, about 11 at Shanghai, about 2.75, about 2.1 without the
  export duty. Fujian or Anhui against Beijing: SILENT (Beijing-end prices only: Songluo 0.2 tael a jin in 1736, black tea 1 liang a jin in 1821).
- Raw silk: SILENT (far-end prices only: Canton 1756-74, Ningbo 1757, Beijing 1736; no Huzhou price of the same date).
- Sugar: ATTESTED ONLY FOR Taiwan (then of Fujian), 1723 - white sugar 1.3-1.4 taels per 100 jin, freight to Suzhou about 0.11-0.12, 8-9%
  of the price, no Suzhou price of that date, so the ratio is SILENT; and ATTESTED ONLY FOR Takow to Yokohama, 1871, bought at $2.43 a picul
  and sold at $4.30, 1.77 by the source's count, a Japanese port. Guangdong sugar against the Yangzi or Beijing: SILENT.
- Spices, incense woods, medicinal roots: SILENT as pairs (sandalwood, aloeswood and rhubarb priced at one end only). Songjiang cloth: no
  ratio (different units, 52 years apart). The Hunan-Suzhou rice benchmark: a lead, not read.
- The Ball, Fortune and Timkowski tables were read from scrambled scans: cited only once read on the page images.

**Question 3** (`passes/c-margins.md`):
- A consignment wholesaler's commission: ATTESTED - Kyoto silk thread 1% from each side, Osaka cotton 1.3%, Osaka oil bound for Edo 0.8%
  (arithmetic), Edo down-sake 3%; Osaka fresh fish 1795 a net 11.5-12.2% of the auction price; dried fish 1841 9%, the wholesaler keeping 4%.
- A buying wholesaler's markup: ATTESTED ONLY FOR one house - Mitsui's Edo cotton shop 2.1-5.8% (1789-1840s), its buying agent 1% in 1795.
- Net margin as a percent of selling price, per kind of trader: SILENT as a net figure for any house (no house's net profit on sales or
  capital read); the commissions and the Mitsui gross rates above are the nearest.
- The shipowner trading on their own account: return per voyage ATTESTED in ryo - the Kocho-maru, 1863, about 830 ryo net, 932 of the 1,046
  ryo trading gain on the southbound herring leg; "1,000 ryo a voyage" as a saying, real voyages 10-20% short by Makino's reckoning. As a
  percent of cargo value: SILENT (the 1876 account, outside the window: 2.96% northbound, under 1% southbound). Against carrying for hire:
  the Kitamaebune NOT ATTESTED as a freight trade; a for-hire carrier's margin SILENT.
- Voyages a year: ATTESTED - Kitamaebune Osaka-Hokkaido 1; Shanghai bean junks to Guandong 3-4; Amoy coasters several, Nanyang junks 1.
  Higaki and Taru ships: SILENT.
- Loss to wreck: SILENT as a rate. Profit split: the captain's private cargo a tenth, the crew's about a tenth; Chinese junk crews as
  shareholders with their own goods.
- Interest on cargo money (the canon beside it): voyage loans 1626-38 at 25-40% and 50-80% a voyage; Edo's legal rate 15-18% a year;
  Lianghuai salt merchants about 1830 at 1.5% a month.
- China: ATTESTED ONLY FOR single cargoes and one Canton margin - a junk at Tianjin, 1831, over 100% on sapanwood and pepper and 50% on
  calicoes; the Hong merchants about 30% on cost on tea. Brokerage: SILENT for the Qing. Coastal and Yangzi merchant houses' accounts: SILENT.
- Gutzlaff's passages were rebuilt from garbled machine text: cited only once read on the page images.

**Question 2** (`passes/d-sea-freight.md`):
- Osaka or Nishinomiya to Edo, freight: SILENT beyond 0280's sake rate (60 monme per 10 da, no year). Higaki ships: SILENT. Voyage days:
  ATTESTED - the new-sake race of 1866, 9 and 12 days, 1868 about 14-15; modern summaries of 3-4 days, a 58-hour record of 1790 and an
  ordinary 12 days, given as what they are.
- The Inland Sea to Osaka, Hagi domain rice, 1838-56: ATTESTED - freight on 100 koku worth 489.6-983.9 monme (the author's conversion);
  about 1855, 6.4% of the rice on a 330-koku ship, a 30-day round trip; another province's ship at about 1.5 times the domain's rate.
- The Sea of Japan route: ATTESTED ONLY FOR castle and exchange rice, 1835-60 - Sakata to Osaka 9 monme a koku net; Sakata to Edo loaded 58
  days on average (32-104) over 15 runs; Osaka to Sakata empty 52 (29-173); Niigata to Edo 81 in 1860. The Kitamaebune's own freight: NOT
  ATTESTED as a freight trade. The shogunate's rates by port under Kawamura Zuiken: SILENT.
- China: north of the Yangzi ATTESTED ONLY FOR one charter (Niuzhuang to Jiangnan, 1862, 630 shi of beans and some oil for 535 taels) and
  0280's tribute rate; a commercial sand-junk rate per shi SILENT. Fujian: ATTESTED - the 1787 official grain rate across the strait (0.036
  tael a shi a stage, Amoy to Tainan 0.432); the 1891 Amoy customs survey (about 30 cents a picul to Tainan, 150 cash to Quanzhou, 40-50
  cents a bag of sugar north). Voyage days: Jinjiang to Tianjin 15 days (1861); Guangdong to Tianjin 18-70; Ningbo to Tianjin 6-10, three
  voyages a year (1882-91).
- Silver per 100 kg per 100 km: no source gives a distance for a Japanese route, so each figure is this project's arithmetic on a labeled
  distance, or SILENT. Against river and pack horse: ATTESTED ONLY in words (water several times cheaper than land); a ratio against 0280's
  rates is this project's arithmetic.

**Question 4** (`passes/e-ships.md`):
- Burthen: ATTESTED, Japan (about 250 koku early; 1,000 koku for higaki ships about 1800; 1,600-1,800 for late taru ships; domain coasters
  150-330; Kitamae ships 300-800; a koku of burthen about 150 kg by the source's own conversion) and China (sand junks 400-2,000 shi in
  1825, 965 shi of grain on average in 1826; Fujian ships 1,600-3,000 shi).
- Crew: ATTESTED, Japan (16 for 1,000 koku under the 1735 rule; 10-12 for 800 koku in 1781; 5 for 330 and 3 for 150 at Hagi) and China
  (16-22 aboard, 1727-1841).
- Crew pay in silver per month: Japan ATTESTED ONLY FOR Hagi about 1840-56 (0.77 koku of rice a hand per 30-day round trip, about 55 monme
  by arithmetic); Kitamae pay scales from undated pages, with the private-cargo shares. China ATTESTED ONLY FOR Amoy 1897 (2-3 dollars a
  month) and Zhenjiang 1597 (1.6 taels a month); sand-junk wages SILENT.
- Build cost: ATTESTED, Japan (a 900-koku ship, 53 kan 480 monme of silver, 1789; about 1,000 ryo for 1,000 koku in 1844) and China (a
  sand junk 7,000-8,000 taels about 1824-26, the essay's author disputed).
- Working life: Japan ATTESTED from modern works (about 20 years, a major refit midway); China SILENT for sea junks.
- Charter: Japan SILENT (hire paid as freight per koku; Hagi 1764 at 1.5 times the fixed rate). China ATTESTED ONLY FOR one Shandong junk
  chartered whole, 1862, 400-odd taels Ninghai to Niuzhuang and 535 taels Niuzhuang to Jiangnan (Matsuura, in `passes/d-sea-freight.md`),
  not a sand junk; per month SILENT; the state's sand-junk hire of 1825-26 paid as freight per shi, its two rates fourteen times apart and
  unreconciled, both given.

## Requirements

- **FR-001**: Every question, good, kind of trader, route and figure of the issue gets, in the reply on #24, its fragment file, its verdict
  and what is still open.
- **FR-002**: The findings are written into the record under the citation rules (`research/CLAUDE.md`), checked by the record checks `make
  record-owed` names, in new money questions tagged as the money section's are, with `subject=money` first, pointed at from 0280 and 0283.
- **FR-003**: The feature closes with `make impl-check F=454`. No engine code decides a traded good's price, a freight or a ship (`grep
  -rnIi -E 'freight|kaisen|kitamae|sea junk|price ratio|wholesaler' l7r pool rust`, run in each write session and recorded in
  `implementation-check.md`).
- **FR-004**: The work and the reply follow the issue's priority: question 1, then 3, then 2 and 4. gm-assistant verifies and closes it.
- **FR-005**: A nearest figure is not an answer: each verdict is one of the four; a figure the record holds only a nearest for is SILENT, the
  nearest and the leads not tried named under "what is still open".
- **FR-006**: Findings state the history as found. No fragment says what a good costs, what a trader keeps or what a voyage costs in Rokugan.
- **FR-007**: Source units first; every conversion, division and distance not in the source is labeled as this project's with what it rests
  on. Two sources that disagree are both given; a figure from one source only says so.
- **FR-008**: The canon quotations of the issue stand beside the history in the reply, and a contradiction between them goes to the GM
  through `escalation-check`. Nothing here edits the canon.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005, FR-008): every question and figure of the issue carries a fragment file, a verdict and what is still
  open in the reply on #24, question 1 first, with the canon beside each.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make impl-check F=454`
  reports nothing missing.
- **SC-003** (FR-006, FR-007): no fragment states a Rokugani figure, and each conversion, disagreement and reading from a scan is stated as
  such, as the check rounds read them.

## Review history

- spec-fidelity round 1 (2026-11-24, MODE 2): CHANGES REQUIRED - two of the issue's canon quotations missing from scenario 4; the charter verdict for China contradicted by pass D; two edge cases worded past their cases. All four applied.
- spec-fidelity round 2 (2026-11-24, verify): FAITHFUL - all four round-1 items resolved.

## Assumptions

- The questions are split by country and by topic so that none passes 20,000 bytes of prose; the count is the plan's.
- The parts land one by one in priority order, and a partial reply on #24 may go out when question 1 has landed.
