# Feature 397, session 1 (write) - handoff

- SECTION=0263/what-did-arrows-cost
- SECTION=0264/what-did-paper-and-ink-cost
- SECTION=0265/what-did-it-cost-to-rent-a-room-or-a-house

A4 (0266, `what-did-a-play-or-a-show-cost-to-see`) is reserved and claimed by feature 397 but NOT written: session 1 used
its ten new registry keys on A1-A3, so A4 went to the continuation brief (`$L7R_CONTINUE`), which appends its own lines here.

Every figure below went through a source-reader from its bundle, answered with `make record-checked`; the findings were
applied (commits `397: ... source-reader round applied`). The applied fixes have not had a second source-reader round.

## 0263 What did arrows cost?

- Late Ming, Jintan county (Zhenjiang): 0.0135632 tael an arrow, the old fiscal book's price for a levy of 9,000, plus
  69.894 taels of matting money on the levy - ATTESTED ONLY FOR an accounting price (`zhifangdian-zhenjiang-arrows`).
  The 1646 commutation at 0.1 tael an arrow is a tax rate, not a cost.
- Late Ming, Jizhou: under 0.033 tael an arrow within a 1-tael set of bow, string, 30 arrows and quiver - ATTESTED ONLY
  FOR an estimate Tan Lun forwarded; the per-arrow share is the project's arithmetic and an upper bound
  (`tan-lun-memorials-07`).
- Qing 1650, all provinces: 0.04 tael an arrow (bow 1, sabre 0.92, musket 1.3) - ATTESTED ONLY FOR a state allowance
  (`daqing-huidian-zeli-130`).
- Qing 1727: arrows sold by the hundred 0.05-0.08 tael (only the 0.08 sesame-eagle kind is called a war arrow); fine
  arrows priced by the five 0.12-0.36 tael - ATTESTED ONLY FOR fixed prices; per-arrow figures are the project's
  arithmetic; the city is not named (that it was Beijing is a GUESS) (`daqing-huidian-zeli-122`).
- Beijing 1736: bow 1.2 taels, a large arrow 0.2, a pot of 17 arrows 0.6 (about 0.035 each, the project's arithmetic),
  a birch shaft 0.006 - ATTESTED ONLY FOR official purchase prices (`gao-shouxian-jiuqing-wuliao`).
- Wages beside them: Ming unskilled SILENT; nearest craftsmen's, a musket costing in a Ming compendium (no place or year,
  compiler d. 1560): ordinary smiths 0.03 tael a day, tongs-man 0.04, carpenter 0.03 (`wubian-qianji-05`). Qing 1650/1727
  SILENT; nearest Beijing 1736, laborer 75 cash, craftsmen 154 cash (9 years after 1727; same list as the 1736 arrows).
  Units not converted.
- Japan, any arrow or arrowhead price: SILENT. Kawato's arrowhead at about a spear's value (a spear about 1 kanmon) is a
  historian's GUESS, labeled as one (`kawato-2020-sengoku-weapons`). Sengoku wage of either class: SILENT; nearest in the
  record is Kyoto's laborer of 1745-1754 (0250), two centuries later.
- Fletcher's output per day: SILENT (China and Japan); the Qing Board of War kept ten arrowsmiths, no quota.
- Recovery after battle: NOT ATTESTED; the Qing Code writes battle losses off and requires the owner's name on each
  arrow (`daqing-luli-yejin`, entry widened to the arms article).

## 0264 What did paper and ink cost?

- Beijing 1736, paper by the sheet (62 kinds): 0.0003 tael (sanbai) to 0.3 (yellow-and-white deer paper, 1.2 zhang by 5
  chi); maobian and placard paper 0.01; liansi 0.0055-0.0085 (flowered 0.01); lianqi 0.0015; Jiangnan 0.027; No. 1
  Korean 0.08 - ATTESTED ONLY FOR official purchase prices (`gao-shouxian-jiuqing-wuliao`). Sizes given for two kinds only.
- Beijing 1736, ink by the jin: top-soot Hui 3.6 taels, Hui 0.6, blue 0.342, green-soot 0.04 - ATTESTED (same list).
- Wage beside them: same list, laborer 75 cash, craftsmen 154 cash - ATTESTED, same place and year; units not converted.
- An ink stick (China or Japan): SILENT. Edo paper and ink in mon: SILENT; the two web figures (coin-walk J078, a
  self-described private draft; an anonymous Chiebukuro answer) disagree about tenfold and neither is citable - said in
  the absence note's comment.
- What a notice was made of: not here; it points at 0190 (session 2 extends it).

## 0265 What did it cost to rent a room or a house?

- Edo, Bunsei era: a carpenter's household rent 10 monme a month beside his 5.4 monme a day (meals included), house type
  not stated - ATTESTED ONLY FOR one period account read by a historian (`tanigama-2014-edo-sumo`). A street peddler's
  takings about 400 mon a day, same account (takings, not a wage).
- Edo back tenement 300-500 mon a month (1804-1830), 500-600 for 9 shaku by 2 ken in the closing years of the shogunate -
  a popular page naming no source, labeled as such (`muraoka-edo-nagaya-life`).
- Edo unskilled wage in the Bunsei years: SILENT; nearest Kyoto day laborer 4.17 g of silver, 1823 (unskilled, Kyoto,
  grams of silver, same years; `bassino-ma-2005`), with 0250's "Edo about the same level from 1818".
- Rent against value, Edo: Mitsui's forty lots (with their houses) about 4% a year 1770s-90s, nearly 4.5% in the 1800s;
  the historian's earlier study of other Edo lots 6% early 1700s, then 3-5%; Mitsui's 1811 survey 4 rin a month on value
  (4.8% a year gross, 2.4% net by the historian's working) - ATTESTED for a lot with its houses
  (`washizaki-2012-edo-lot-yields`). Against the building alone: SILENT. Points at 0251 for the land multiple.
- Edo street-front shop, small house, samurai residence, storehouse by the month; castle-town rents; any rent by the
  week: SILENT (storehouses were let on Mitsui's waterside lots, storage fees in the income, no rate).
- Qing Beijing government houses, 1727, per bay a month: 7 purlins 0.2 tael, 6 0.15, 5 and 4 0.1, 3-purlin veranda (and
  house) 0.05 - ATTESTED (`wu-liping-2017-beijing-rents`, `teng-2014-neiwufu-houses`); let to Han officials only; monthly
  or by quarterly salary deduction.
- Qing shops: government shop-fronts 0.3-0.4 to 3-4 taels a bay by site (regulations, undated); a Daoguang-era (1821-50)
  contract 1 diao 600 wen for two rooms, the historian inferring 800 wen-2 diao a room nearby; 1871-1911 file 8, 8 and 10
  diao for 4, 3 and 4 rooms - ATTESTED ONLY FOR those contracts and files (`wu-liping-2017-beijing-rents`).
- Li Ciming, 1871: a 15-16-bay house at 36,000 wen a month, deposit 10,000 (count of cash not stated) - ATTESTED.
- Rent against value, Beijing: 4.0-6.0% a year (pre-1731 sale schedule against the 1727 rents) - the project's arithmetic
  on two administrative schedules (`teng-2014-neiwufu-houses`).
- Wages beside Beijing: 1727 SILENT, nearest 1736 laborer 75 / craftsmen 154 cash; Daoguang and 1870s SILENT, nearest a
  rural fuel store's 1865 laborer's wage (0260), which its authors use only for trend. Units not converted.

## New registry keys (10)

`zhifangdian-zhenjiang-arrows`, `daqing-huidian-zeli-130`, `daqing-huidian-zeli-122`, `tan-lun-memorials-07`,
`wubian-qianji-05`, `kawato-2020-sengoku-weapons`, `tanigama-2014-edo-sumo`, `washizaki-2012-edo-lot-yields`,
`teng-2014-neiwufu-houses`, `wu-liping-2017-beijing-rents`.

Existing entries whose write-ups changed (each owes `source-applicability`): `daqing-luli-yejin` (widened to the arms
article; title characters now as the page prints them), `gao-shouxian-jiuqing-wuliao` (Used for and limits widened to
paper, ink, arms and the craftsman's wage).

## Still open

- A4 (0266) - the continuation brief.
- The GM's download 類聚近世風俗志 (433 MB) is refused by `make archive-inbox` as over GitHub's file limit (split or Git LFS
  is the GM's call); it is one of the works behind A4's kabuki prices.
- Leads not followed (from the passes): the Tenpo 13 (1842) survey of Edo ground and house rents (Tokyo shishi ko,
  shigai hen 39); Ono's Edo bukka jiten and Koyaizu's Kinsei chingin bukkashi shiryo for Edo paper; 雑兵物語 for arrow
  resupply; 工部廠庫須知 (1615) for a Ming arrow price; Zhang Dechang on Li Ciming's income.
## 0266 What did a play or a show cost to see? (continuation session, A4)
- SECTION=0266/what-did-a-play-or-a-show-cost-to-see
- Edo kabuki, list prices from the Kyowa era (1803): pit 132 mon, the floor behind it 100 mon, one act at the back of the house 16 mon; a bay of boxes 25-35 monme of silver - ATTESTED ONLY FOR list prices Hattori drew from Gekijo kinmo zui and Kinsei fuzokushi, as Bjork reports them (`bjork-2013-edo-kabuki-theatre`); Britannica gives the same for 1803 with seven to a box (`kotobank-sajiki`). A seat in a box 3.6-5 monme is the project's arithmetic.
- Edo kabuki actually charged: 1714 a box 1,200 mon (16 monme) a bay and the pit 64 mon (half the list); 1737 Nakamura theater 2 bu of gold a bay and 164 mon a head in pit and standing room (25% above) - ATTESTED (`bjork-2013-edo-kabuki-theatre`). Box seating: 6 a bay (Hattori, 1720), 7 (1803), 8 at Edo sumo (reported). Bakumatsu kabuki boxes 40-60 monme a bay - ATTESTED ONLY FOR a report Tanigama takes from Ono's Edo bukka jiten (`tanigama-2014-edo-sumo`).
- Standing single-act view: ATTESTED ONLY FOR the 16 mon at the back of the house (the oikomi), Kyowa era.
- Noh: ATTESTED ONLY FOR fund-raising noh - 30 mon a head in a jokebook of about 1614-24 (`kotobank-kanjin-no`); boxes at one gold piece each in the novel Eitaigura, fiction, not converted (`kotobank-sajiki`); the once-in-a-lifetime Kanze show's tickets allotted by force to Edo's wards, the 1848 Hosho show's 15 days and 52,500 tickets (`kotobank-kanjin-no`). Seat-class list, ordinary noh sold to the public: SILENT.
- Sumo (new, from `tanigama-2014-edo-sumo`): Kyoto Okazaki 1700 a bay of boxes 35 monme, the ground 3 monme; Osaka 1702 a box 43 monme (reported); Aizu-Wakamatsu touring tournaments 130 mon (1787), 135 mon (1789) (reported) - ATTESTED ONLY FOR period records a historian reports; Edo sumo prices SILENT (the paper found none).
- Temple-fair plays and sideshows: SILENT. Japanese street performer's takings: SILENT (that they asked onlookers for coin is ATTESTED, `kotobank-daidogei`). Village gifts (hana, shugi): SILENT.
- Rural and provincial troupes: village plays a day or three days at festivals by the youth, or a troupe bought in (`japanknowledge-jishibai`) - ATTESTED. Funai's Hamanoichi 1690-1737: 7 recorded kabuki runs took 839-6,530 monme, 2,709.6 average, 43 players, 54.5 monme each a run - ATTESTED ONLY FOR the shows' takings, the troupe's fee being the historian's hypothesis; 285.2 monme a performance and 5.7 a player are her averages on an assumed 9.5-day run; 1728 Nakatsu troupe, nine days agreed, fifteen shows, ticket money 2 kan 392 mon - ATTESTED (`bjork-2021-troupe-fees`). Per seat: SILENT.
- Troupe composition: kabuki troupes at Hamanoichi averaged 43 players, puppet theater 26 (`bjork-2021-troupe-fees`); the geza offstage music played by the theater's own musicians, its corner from late Kyoho (`kotobank-geza`); noh, kyogen, kabuki and acrobats formed troupes until early in the early modern period (`bjork-2021-troupe-fees`) - ATTESTED. Acrobats or jugglers inside a kabuki troupe: SILENT.
- Qing: Beijing theaters charged the pit by the head and the gallery by the table, 130 cash a seat fixed before 1900 (which count of cash: SILENT); a Kaifeng (Henan) troupe for village god festivals no more than ten-odd thousand cash for three days, undated; a Hangzhou toad act asked 3 cash in Yuan Zicai's childhood (about the 1720s, the decade in a comment only); conjurors called to household celebrations, no fee (`qingbai-leichao-xiju`) - ATTESTED.
- Wages beside them: Edo unskilled 1803 SILENT; nearest Kyoto casual laborer 0.92 monme 1802-04 (unskilled, Kyoto, silver, same years; `saito-2003-wages`): a box for seven 27-38 days, a seat 4-5.4 days (the project's arithmetic). Nearest craftsman: Edo carpenter 5.4 monme, Bunsei era (Edo, silver, 15-27 years later; `tanigama-2014-edo-sumo`). Kyoto 1700, Aizu, Funai: SILENT either class; nearest unskilled Kyoto 0.91 monme 1745-54 (0250; about 45 years after Okazaki), nearest craftsmen Nogami 1749 carpenters and sawyers 1-1.67 monme (0256). Beijing beside the 130 cash: SILENT; nearest the 1865 fuel-store laborer, trend only (0260). Hangzhou and Kaifeng: SILENT; nearest Beijing 1736 laborer 75 cash, craftsmen 154 (`gao-shouxian-jiuqing-wuliao`), another city. Copper prices and silver wages not converted.
- English traveling players: not written here (session 2's comparative question).
- Checks: every 0266 note went through a source-reader from its bundle (all READ, 0 CONTRADICTED), answered with `make record-checked`; the wording fixes are applied in 56e440ac9 and have not had a second round. The Gao note is word for word 0265's (hash d63b62d717bcd889) and was recorded with REASON=, since its bundle carries 0263's capped third round.
- New registry keys (7): `bjork-2013-edo-kabuki-theatre`, `bjork-2021-troupe-fees`, `kotobank-sajiki`, `kotobank-kanjin-no`, `kotobank-daidogei`, `kotobank-geza`, `qingbai-leichao-xiju`.
- Existing entries whose write-ups changed (each owes `source-applicability`): `tanigama-2014-edo-sumo` (widened to sumo prices and the Bakumatsu kabuki report), `japanknowledge-jishibai` (Used for widened to the money section).
- Still open: the GM's 433 MB download of 類聚近世風俗志 (a work behind Hattori's 1803 prices) is refused by `make archive-inbox` as over GitHub's file limit, splitting it or Git LFS is the GM's call. Leads not followed: Iida's illustrated Edo kabuki dictionary and Iwanami's Edo no misemono for temple-fair and sideshow admission; kotobank 小芝居; the Saitama paper's tables 4 and 5 (pp. 42-45); Gamble's Beijing copper-cash wages of 1870-1900 and the doubled-count question for the 130 cash; an Edo mon-to-monme rate of 1803; the Edo-Tokyo Museum's 1848 noh handbill. Source-reader units still unanswered from session 1 (not 0266's): 0263 tan-lun-memorials-07 and zhifangdian-zhenjiang-arrows, 0265 teng-2014-neiwufu-houses.
- Second pass on 0266 (after the source-reader round): the wage section now states every gap in years - Funai against Kyoto 1745-54 (8-64 years) and Nogami 1749 (12-59); Aizu-Wakamatsu paired with the Kyoto laborer of 1802-04 (unskilled, another region, about 15 years later; Bassino and Ma's yearly Kyoto series has no rows for 1763-1790); Beijing's 1865 wage at an unknown distance, the 130 cash being dated only before 1900; Hangzhou and Kaifeng undated. No new source or note; no source-reader unit is owed by it.
