# Feature 414 - handoff between sessions

## Session 1

- SECTION=0290/how-steady-were-prices-in-edo-japan-and-qing-china-from-one-day-to-the-next-century
- SECTION=0291/how-steady-are-prices-today-under-paper-money

### Verdicts, per figure the issue asks (diagram#15 questions 1 and 2), all in `research/questions/0290-how-steady-were-prices-in-edo-japan-and-qing-china-from-one-day-to-the-next-century.html` unless named

- Japan, within a day: ATTESTED ONLY FOR how a trading day ran (opening and closing price, a halt rule, trading after the close; Takatsuki 2007); size SILENT.
- Japan, day to day and week to week: SILENT in the sources; this project's arithmetic on the RIEB daily Osaka rice, 2.0% and 3.8% (SD of log change, 1787-1858).
- Japan, month by month within a year: ATTESTED for Osaka rice (Miyamoto 1975: CV under 10% in most years, 15.8-20.1% in the Tenmei famine years, 24.2% in 1851); arithmetic 9.0% a month.
- Japan, half year and year: ATTESTED (Shinbo 1975 within-year CV, general 7.4% / 8.1%, rice 6.9% / 11.3%; Mitsui rice 12-14% a half year, 15-17% a year, arithmetic).
- Japan, 5-50 years and drift: arithmetic (Mitsui rice 25-34% at 5 yr, 28-38% at 10, Kyoto 20% at 50; drift to 1858 Kyoto -0.5%/decade, Osaka +0.1%, Edo +3.9%, spans and early years named; first years in debased-coin years); Shinbo +36% from 1802-1829 to 1830-1858, +239% in 1859-1867.
- Japan shocks dated: 1732, 1783-1786, 1836-1837 (coin-walk rows, RIEB cells), 1818-1829 recoinage (Saito 2003), 1859 (Shinbo; coin-walk 1858 against 1866).
- China, within a month: SILENT (monthly high-low reports only; Keller-Shiue-Wang appendix).
- China, month: ATTESTED ONLY FOR the rise between harvests, 1.1% a month (KSW Table A.4).
- China, half year and year: ATTESTED (Shiue and Keller 9.2% against Europe 12.7%; Allen baskets Suzhou 9.6%, Canton 8.1% a year, arithmetic).
- China, decades and century: arithmetic (Suzhou basket 22% at 10 yr, drift +5.6%/decade 1730-1833; Canton +9.4%); silver trend "not marked" with Suzhou +0.067 tael/shi/decade (Lu and Peng); copper kept apart: Qian Yong 7 cash (1707) to 27-35 normal after 1785, Quan "about fourfold or more"; cash per tael near 1,000 to over 2,000 by 1850 (Lu and Peng).
- China shocks dated: 1642, 1651, 1669-1670, 1680 (Ye Mengzhu), 1707, 1755, 1785 (Qian Yong), Taiping years by cash per tael 2,205 (1853) to 4,970 (1856) (Allen Table I); grain price 1853-1864 SILENT.
- Per good (table in 0290): rice ATTESTED; soybeans ATTESTED ONLY FOR Osaka 1802-1867 and 17th-century Songjiang; other grains ATTESTED ONLY FOR wheat, barley/buckwheat/millets SILENT; other beans and fish SILENT; edible oil ATTESTED ONLY FOR Osaka seed oil; cloth ATTESTED ONLY FOR Osaka cotton/silk and Songjiang; lamp oil ATTESTED (Japan), SILENT (China); salt ATTESTED ONLY FOR Edo and Osaka 1818-1858 and the Qing set price (Kyoto's 1791 unit change named, no Kyoto figure used); fuel ATTESTED; rents ATTESTED ONLY FOR Mitsui's 40 Edo properties; crafted goods ATTESTED ONLY FOR Osaka's manufactures; services SILENT; unskilled day wage ATTESTED (Saito 1993 sticky at Mitsui Kyoto, flexible for day laborers; Mitsui Edo 1.1% a year; Beijing copper wage flat 1807-1853, Allen).
- Against the canon (one price level per era): the Mitsui 5-year spread (rice 25-34%, lamp oil 17-19%, firewood 5-11%, Edo wage 8%) is the size of that simplification.
- Modern yardstick, `research/questions/0291-how-steady-are-prices-today-under-paper-money.html` (COMPARATIVE): US CPI x7.74 Aug 1971-Dec 2024, 3.9%/yr; Japan x3.30 1971-2024, 2.3%/yr; SD month / 12 months 0.38% / 2.8% (US 1972-2024), 0.31% / 1.3% (1984-2019), Japan 0.58% / 3.9% and 0.33% / 1.0% (1995-2019); BLS rice 2.2% / 9.3%, flour 3.3% / 9.1%, eggs 6.9% / 21%; Japan cereals 1.1% / 5.4%; CBOT rough rice futures 1.7% a trading day, 4.1% over five (2016-2026); Rolnick and Weber 1.0% commodity against 13% fiat. Within a day: SILENT.

### Searches

- Japan, Qing and modern passes: `specs/414-price-stability/passes/japan.md`, `qing.md`, `modern-yardstick.md` (leads; each cited passage re-read on its page or page image).
- Daily staple series: stooq.com (ZR.F, ZW.F) and cmegroup.com refused this host; Yahoo Finance's chart (ZR=F) read and cited.
- The size of a within-day move (Edo and today), barley/buckwheat/millets, other beans, fish, services, Qing oils, rents and crafted goods, Qing grain 1853-1864: searched, absence notes in 0290 and 0291.

### New keys (ten)

shinbo-1975-bakumatsu-prices, miyamoto-1975-osaka-rice-prices, takatsuki-2007-osaka-daily-rice, shiue-keller-2004-nber-markets, keller-shiue-wang-appendix, lu-peng-2004-rice-prices, quan-1957-silver-price-revolution, dbnomics-bls-statjp-cpi, rolnick-weber-1995-commodity-fiat, yahoo-cbot-rough-rice-daily. (Shiue 2002 and the RIEB database were already registered: `shiue-2002`, `rieb-kinsei-db-data`; the 1732, 1783 and 1836 famines were cited from the existing `coin-walk-edo-kahei-nenpyo` rows, so Kotobank and the Kobe 2026 press release needed no key.)

### Checks done this session

- source-reader on the ten new keys' notes (recorded with `make record-checked`); fixes in commit 33fa93353. Still owed for session 4: source-reader on the new notes citing EXISTING keys (bassino-2006-gpih-mitsui, rieb-kinsei-db-data, coin-walk-edo-kahei-nenpyo, saito-2003-wages, saito-1993-bakumatsu-wages, washizaki-2012-edo-lot-yields, shiue-2002, allen-2009-china-wages, allen-2010-gpih-beijing-prices, ye-mengzhu-yueshibian, qian-yong-lvyuan-conghua, qingshigao-123-yanfa), and every quote-check, record-format, intro-check, translation-check and source-applicability unit `make record-owed` names for 0290, 0291 and the ten keys. Page images for the scans: Shinbo, Miyamoto, Quan p. 548, Rolnick-Weber (re-render with pdftoppm from the archived PDFs).
- New script: `specs/414-price-stability/measure/modern_yardstick.py` and `.out.md`.

### Leads not followed

- Liu Ziang 2022, LSE WP 339 (Qing wages sticky in the short run): no key left this session; Allen's Table I carries the China wage verdict.
- Bassino and van der Eng (13 markets, famines named), Kato 1998 thesis (monthly swings, seasonality), Kotobank on the Kyoho famine, the Kobe 2026 press release on the Tenpo famine.
- Miyamoto 1988 ch. 5 (within-month CVs, seasonal indices), Wakita 2001 (paywalled), Murai on the 1695 recoinage, Suzuki Osaka WP 2306 on 1718.
- KSW Table A.3: its header and notes disagree on whether the last column is the share of one-month changes that are zero or non-zero (0.344-0.517 for China); not used.
- Lu and Peng call the 18th-century regional trends significant while concluding the early-middle Qing trend is "not marked"; 0290 quotes the conclusion and the Suzhou coefficient.
## Session 2
- SECTION=0292/how-far-apart-were-prices-from-one-city-or-village-to-the-next
- SECTION=0293/how-did-a-goods-price-change-from-one-dynasty-or-era-to-the-next-and-why
### Verdicts, per figure the issue asks (diagram#15 question 3, and the GM's addition to question 2)
- 0292 (`research/questions/0292-how-far-apart-were-prices-from-one-city-or-village-to-the-next.html`): co-movement ATTESTED (Shinbo: Kyoto and Osaka in parallel; Takatsuki 2012: Otsu within 2 days, then 1; Bassino and van der Eng abstract: west integrated, east impeded by distance and cold; Shiue and Keller Table 2a: 0.83 under 150 km to 0.08 beyond 1,050 km; Wang and Huang abstract: Suzhou and Guangzhou poorly integrated).
- 0292 level spreads, this project's arithmetic: Mitsui 1818-1858 rice Osaka +1%, Edo +3%; firewood Edo -33%, Osaka +43%; miso, vinegar, sake, soy sauce, lamp oil, candles, Edo wage -10%; Kyoto salt named and left out. Iwahashi 14 places (new script measure/iwahashi_spread.py): west highest/lowest 1.31x (1701-1800), 1.25x (1801-1858); Otsu 3-6% below Osaka; castle towns 3-13% below; Edo 6-8% and Nagoya 13-18% above; Shinshu, Aizu, Dewa 21-34% below. China levels: Allen's statement (very little difference) and measure/qing_levels.py (Canton -10%, Beijing -8% of Suzhou in 1730-1799).
- 0292 town against country: ATTESTED ONLY FOR wages (Saito 2003: village 1.0 against Kyoto 0.92 monme, 1802-1804; city indices more volatile); a good's village and city prices side by side SILENT (absence note); Qing level spreads by good SILENT.
- 0293 (`research/questions/0293-how-did-a-goods-price-change-from-one-dynasty-or-era-to-the-next-and-why.html`): salt in days of a laborer's wage - Song 1.2-1.75 a jin (ATTESTED ONLY FOR a second-hand wage), Ming Wanli 0.2, Qing 1736 0.13, 1830s Jiangxi/Huguang official 0.7-0.8 and private 0.35 (ATTESTED ONLY FOR a rural Beijing wage), Edo 0.14-0.55 a sho (0273 named); Japan and China not converted (absence note on a sho's weight). Song salt in rice: about a dou a jin before 1068, a fifth by 1122.
- 0293 drivers ATTESTED: Song buying 4-6 cash, profit up to tenfold, Hebei doubled (1085 report), Sichuan official 120 against 70-80 (1086), Fujian by 1181; Ming merchants' price tenfold by 1534; Qing Changlu 1688/1732, 2-cash cuts 1791 and 1848 (restored 1858), Tao Shu's 60-70 against 30-odd, tickets 1832-1833 (over 10 taels to a little over 5) and 1849 (cost halved, prices fell); Japan's domain monopolies (Kanazawa from about the Kan'ei years, Sendai, Ako 1680 and 1809-1821) with no price effect given (SILENT). Edo salt in days of the Edo wage per koku 23 / 17 / 31 / 68 (1710-1716, 1818-1829, 1830-1858, 1859-1871); why it doubled after 1830 SILENT.
- 0293 other goods: Gao 2022 (Beijing 1615 against 1736: flour 175%, glutinous rice 252%, coal over double, cloth flat, pig iron down; wages rose more than flour; Peng's index 100 to 17.37); Quan (more than fourfold, American silver and population); Song rice x4 by 1122; Songjiang cotton and cloth (Ye); Mitsui sub-periods in days of the city wage (new script measure/mitsui_periods.py) with the drivers named (Saito: recoinage 1818-1829 and famine 1833-1838; Shinbo: +36%, +239%).
### Searches
- The salt-periods, Japan and Qing passes (`passes/salt-periods.md`, `japan.md`, `qing.md`); each cited passage re-read on its page (宋史 181-183, 明史 80, 清史稿 123 in the archive, kotobank, The Paper, the RePEc and IHP abstracts, Takatsuki 2012 PDF) or page image (Shinbo p. 290, Wu Haibo pp. 44 and 46: his note 5 is 陶澍集, so the wu-haibo write-up now names it).
### New keys (nine)
songshi-181-yanfa-shang, songshi-182-yanfa-zhong, songshi-183-yanfa-xia, kotobank-han-senbaisei, kotobank-ako-enden, takatsuki-2012-osaka-otsu, bassino-van-der-eng-2018-rice-markets, thepaper-2022-song-prices, wang-huang-1999-southeast-grain. Existing keys reused (Used-for lines extended): mingshi-80-chafa (title now names the salt laws too), wu-haibo-qing-sishi, gao-shouxian-jiuqing-wuliao, iwahashi-1981-gpih-rice-prices, bassino-2006-gpih-mitsui, qingshigao-123-yanfa, shiue-keller-2004-nber-markets, shinbo-1975-bakumatsu-prices, allen-2009-china-wages, allen-2010-gpih-beijing-prices; also cited unchanged: saito-2003-wages, ye-mengzhu-yueshibian, quan-1957-silver-price-revolution.
### Checks done this session
- source-reader on the nine new keys' notes and write-ups, recorded; every finding applied by hand (Fujian dated "by 1181", "a third or more", Kanazawa "about", Ako on the Harima coast and its one 1820 value, the Bassino-van der Eng question, The Paper's wage attribution, Wang and Huang's title). Still owed for session 4: source-reader on the notes citing EXISTING keys (above), and every quote-check, record-format, intro-check, translation-check and source-applicability unit `make record-owed` names for 0292, 0293, the nine keys and the ten edited write-ups.
### Leads not followed
- Metzger and Ho Ping-ti on Lianghuai; 郭正忠 and 戴裔煊 on Song salt; 劉淼 on Ming salt; 程民生 for the Song wage's original text; 全漢昇 1948 on the Song rice rise; 西川・石部 1987's table of domain monopolies; the weight of a sho of Edo salt; 宮本又郎 1981 on regional rice markets; 全漢昇 1957's regional price tables; Chuan and Kraus 1975.
