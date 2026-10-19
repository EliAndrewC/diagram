# Pass - copper-silver exchange rate (lead for #3/#4) (research-pass, 2026-10-18; its reply verbatim)

**Verdict: ATTESTED ONLY FOR** Osaka market rates from 1787 to 1867 and for the official rates. There is a daily Osaka series for 1787–1867: 金相場 is silver monme per ryō and 銭相場 is silver monme per 1 kanmon. For Edo, and for Osaka before 1787, I found only a chart (Iwahashi 1998, figs. 2–3), which I read by eye, plus a few single-year values.

## Sources and verbatim passages

**1. Kobe University RIEB / Mitsui Bunko, 近世経済データベース** (https://www.rieb.kobe-u.ac.jp/project/kinsei-db/about.html; Excel at …/data/data_180301.xlsx). The figures come from the Osaka exchange-office diary (大坂両替店「日記録」) for 1787–1871.
- 「銭相場銭１貫文につき、銀がいくら（○匁○分○厘）であるかを示す。…本両替仲間の立てた北濱相場立会所、特に当日の最終値段である引方相場を記している。」 — "The copper rate gives how many silver monme 1 kanmon of coin is worth… we record the rate set by the main money-changers' guild at the Kitahama trading floor, specifically the day's closing price." (translation)
- 「金相場金一両につき、銀いくら（○匁○分○厘）であるかを示す。…元禄13年（1700）、幕府は金１両を銀60匁と定めたが…相場は日々変動していた。」 — "The gold rate gives how many silver monme 1 ryō is worth… In 1700 the shogunate set 1 ryō = 60 monme, but the market rate moved daily." (translation)
- 「安政6年（1859）6月1日からは、…補助貨幣である有合金…により、金相場を立てることになった。」 — "From 1859/6/1 the gold rate was quoted in the subsidiary coins in circulation, not in koban." (translation)
- 1843/4/12 note column: 「近來上方筋錢相庭下直ニ而…錢壹貫文ニ銀拾匁内之相庭を以賣買致間敷尤拾匁已上之相庭者不苦候」 — "Copper has lately been cheap in the Kamigata, which affects all prices; trading at under 10 monme per kanmon is forbidden; 10 monme or more is permitted." (translation)
- 1842/6/10 event column: 「…銭のお買い上げを仰せつけられたので、「銭相場気配」が宜しくなった」 — "…an official purchase of coin was ordered, so the copper market firmed." (translation)

**The table below is my calculation, not a quoted passage.** For each year I averaged the daily midpoints (each day's minimum and maximum, or the single value given). Each year rests on about 290–370 trading days. The mon-per-ryō column is derived as 1000 × 金相場 ÷ 銭相場, taken on the same day. The script is /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/scripts/agg.py, the annual output is /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/scripts/annual.txt, and the data file is /tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/rieb-xlsx/data.xlsx.

Osaka, decade means:

| Period (years with data) | 金相場 (monme per ryō) | 銭相場 (monme per kanmon) | mon per monme | mon per ryō |
|---|---|---|---|---|
| 1787, 1789 | 55.6 | 9.48 | 106 | 5,870 |
| 1790s (6 years) | 60.7 | 9.36 | 107 | 6,490 |
| 1800s (7) | 64.3 | 9.20 | 109 | 6,990 |
| 1810s (7) | 64.6 | 9.14 | 109 | 7,065 |
| 1820s (7) | 63.4 | 9.23 | 108 | 6,870 |
| 1830s (5) | 61.8 | 9.10 | 110 | 6,790 |
| 1840s | 63.6 | 9.76 | 103 | 6,530 |
| 1850s | 67.5 | 10.04 | 100 | 6,720 |
| 1860s (to 1867) | 92.5 | 13.19 | 77 | 6,950 |

- **Rows needing a note:**
  - 1802–04: 9.22 monme per kanmon, about 108 mon per monme.
  - 1844–49: exactly 10.000 every year. That is the administered floor, not a market price. A note in the diary for 1843/11/15 gives the actual price after the 切賃 deduction as 「9.40 9.60」.
  - 1855–59: 93–98 mon per monme.
  - 1863–67: 66–77 mon per monme.
  - 1866–67: the mon per ryō (7,900 and 8,900) rests on gold quoted in subsidiary coins, as above.
- **Years missing from the diary:** 1788, 1790–91, 1795–96, 1802–03, 1807, 1815, 1818–19, 1821, 1826, 1829, 1831, 1833–35, 1839.
- **After 1867:** the 1868 and later rows switch units when silver accounting was abolished, so I left them out.

**2. 岩橋勝「江戸期貨幣制度のダイナミズム」『金融研究』1998.7** (inside the conference volume https://www.imes.boj.or.jp/research/papers/japanese/kk17-3-1.pdf, printed p. 70; the PDF has no text layer the ledger can read, so I read it from a rendered page).
- Figure captions: 「図２ 大坂金相場・銀相場、1750〜1860 …出所：新保［1978］」 and 「図３ 江戸銭相場（金１両に付）…注：1695年までは会津銭相場の動き 出所：岩橋［1996］」
- Text: 「明和−天明期（1760〜80年代）の約20年間に鉄銭と四文銭という新種銭貨を、従前発行累計額の２倍近くが供給された…この間の銭相場の下落は当然である」 — "In the roughly 20 years of the 1760s–80s, iron and four-mon coins nearly doubling all earlier issues were put into circulation… the fall of copper in this period is to be expected." (translation)
- **My readings of the charts, all approximate (≈):**
  - Edo, fig. 3 (mon per ryō):
    - 1700: ≈3,900–4,200
    - 1706: ≈4,800
    - 1714–15: ≈2,900, the low
    - 1720: ≈4,500
    - 1729: ≈5,150
    - 1736–37: ≈2,950
    - 1740s: ≈3,800 rising to 4,600
    - 1750s: ≈4,250
    - 1762: ≈4,100
    - 1770: ≈4,800
    - 1773: ≈5,400
    - 1778–80: ≈6,050
    - 1790: ≈5,600
    - 1795: ≈6,450
    - 1800: ≈6,650
    - 1810–30: ≈6,650–6,900
    - 1840s: ≈6,550–6,800
    - 1850s: ≈6,450–6,850
    - 1863: ≈7,400
  - Osaka, fig. 2 (monme per kanmon → mon per monme):
    - 1750: ≈13.7 → ≈73
    - 1752: ≈13.0 → ≈77
    - 1755: ≈14.4 → ≈69
    - 1760–69: ≈15.3–15.5 → ≈65
    - 1772: ≈13 → ≈77
    - 1776: ≈11.3 → ≈88
    - 1780–86: ≈9.7–9.8 → ≈102

**3. 江戸時代の三貨制度, ja.wikipedia** (https://ja.wikipedia.org/wiki/三貨制度). These are exact single-day figures.
- 「明和3年3月27日（1766年）、大坂における物価…金1両：銀63匁8分2厘銭1貫文：銀15匁1分9厘（金1両=銭4201文）」 — "Osaka, 1766: 1 ryō = 63.82 monme; 1 kanmon = 15.19 monme (1 ryō = 4,201 mon)." (translation) That is about 66 mon per monme.
- 「慶應3年正月（1867年）、京都…金1両：銀107匁1分銭1貫文：銀12匁6分6厘（金1両=銭8460文）」 — "Kyoto, 1867: 1 ryō = 107.1 monme; 1 kanmon = 12.66 monme (1 ryō = 8,460 mon)." (translation)
- 「元禄13年（1700年）に金1両=銀60目=銭4貫文と改訂した御定相場を公布した。明和期に…銭相場は次第に下落し金1両が銭6貫文程度となり」 — "In 1700 the official rate was revised to 1 ryō = 60 monme = 4 kanmon; from the Meiwa era copper fell until 1 ryō was about 6 kanmon." (translation)

**4. 寛永通宝, ja.wikipedia** (https://ja.wikipedia.org/wiki/寛永通寳)
- 「元禄7年（1694年）に金一両＝4800文前後であったものが元禄13年（1700年）には一両＝3700文前後となった」 — "about 4,800 mon per ryō in 1694 became about 3,700 in 1700." (translation)
- 「元文2年（1737年）には…銭相場が一両＝2800文前後まで急騰」 — "In 1737 copper rose sharply to about 2,800 mon per ryō." (translation)
- 「安永7年（1778年）ごろには一両＝6000文前後を付けるに至った」 — "around 1778 it reached about 6,000 mon per ryō." (translation)
- 「慶應元年（1865年）閏5月、ついに天然相場を容認し…銅小銭、真鍮銭に対し増歩通用を認めるに至った…鉄一文銭を基準として…寛永通寳銅一文銭：4文寛永通寳真鍮當四文銭：12文」 — "In the intercalary 5th month of 1865 the shogunate let the market set the rates and allowed copper and brass coins to pass at a premium; taking the iron 1-mon coin as the base, a copper 1-mon coin was worth 4 mon and a brass 4-mon coin 12 mon." (translation)

**5. 御定相場, ja.wikipedia** (https://ja.wikipedia.org/wiki/御定相場)
- 「元禄13年11月…金1両＝銀60目と御定相場を改定し、両替商らには…金1両＝銭3900文以下の銭高で取引することを禁じた。」 — "In 1700/11 the official rate was revised to 1 ryō = 60 monme, and money-changers were forbidden to trade copper dearer than 3,900 mon per ryō." (translation)
- 「天保13年（1842年）に金1両＝銭6貫500文に改め」 — "in 1842 it was changed to 1 ryō = 6 kanmon 500 mon." (translation)
- 「江戸における銭相場は金一両＝銭○貫文、大坂における銭相場は銭一貫文＝銀○匁（目）で表示された。」 — "In Edo the copper rate was quoted as mon per ryō; in Osaka as monme per kanmon." (translation)

**6. kotobank 銭相場** (https://kotobank.jp/word/銭相場-87683; 日本国語大辞典 and 世界大百科事典)
- 「…向後彌金壱両に銀は五拾八匁替、銭は三貫九百文替之積より高値に仕間敷候」(御触書寛保集成, 1701.12) — "henceforth do not trade silver dearer than 58 monme, or copper dearer than 3,900 mon, to the ryō." (translation)
- 「1700年（元禄13）11月には金1両＝銀60匁＝銭4貫文と改定され，これが幕府の法定相場として幕末まで維持された。」 — "In 1700 the rate was revised to 1 ryō = 60 monme = 4 kanmon, and this stayed the legal rate until the end of the shogunate." (translation)
- 「幕末期の銭相場は一両=七貫文前後まで低落した」 — "By the late Edo period copper had fallen to about 7 kanmon per ryō." (translation)

## Reading

The official rate never moved off 1 ryō = 60 monme = 4,000 mon, which works out to 66.7 mon per monme. The one exception was the 1842 Edo decree of 6,500 mon per ryō. Market rates moved well away from the official one:

- **Before about 1765:** in Osaka copper was dear. One monme bought about 65–77 mon (1750s chart reading; 1766 exact figure 66). In Edo a ryō bought roughly 2,900–5,150 mon, swinging with each recoinage.
- **1765–1785:** the flood of iron and four-mon coins pushed copper down.
- **1787–1840s:** a stable plateau. In Osaka one monme bought 103–112 mon. In Edo a ryō bought about 6,500–6,900 mon.
- **1855–1867:** silver weakened against copper again. One monme bought 94 mon, falling to 66–69 by 1865–67.

**For the record's two anchors:**
- **Bassino and Ma, 1745–54:** only chart precision exists. Osaka is about 13.5–14 monme per kanmon, so roughly 70–75 mon per monme; 0.91 monme then comes to about 65–68 mon. The nearest exact figure is the 1766 one, 66 mon per monme.
- **Saito, 1802–04:** the Mitsui figure for 1804 is 9.22 monme per kanmon, about 108 mon per monme. So 0.92 monme is about 100 mon. (Saito's archived text, D03-02, gives no conversion rate of its own.)

**Caveats:**
- The 1844–49 values are a legal floor, not market prices.
- After 1859 the mon-per-ryō figures rest on gold quoted in subsidiary coins.
- From 1865 the "kanmon" depends on which coin was paid, so late-1860s mon prices are ambiguous unless the type of coin is known.
- All the Edo figures are my readings from Iwahashi's chart, not quoted numbers.

## Leads not followed
- 新保博 1978 『近世の物価と経済発展』: the appendix tables behind fig. 2 should give Osaka figures for 1725 onward.
- 『校註両替年代記』 (1932): the likely primary source for the Edo rates.
- 『読史備要』「金銀米銭相場一覧」 (758–1825).
- Iwahashi 1996, the source behind fig. 3 (title not identified).
- 草野正裕 on the Kyoto gold rate, Kobe repository: https://da.lib.kobe-u.ac.jp/da/kernel/81008452/81008452.pdf

On the ledger, I recorded outcomes for two pages that did not bear: Commons File:Zeni-rate.png (the uploader's own chart, with no data source) and imes kk17-3-2.pdf (the wrong paper).

Sources:
- [RIEB 近世経済データベース, about page](https://www.rieb.kobe-u.ac.jp/project/kinsei-db/about.html)
- [RIEB Excel data](https://www.rieb.kobe-u.ac.jp/project/kinsei-db/data/data_180301.xlsx)
- [金融研究 1998.7, Iwahashi 1998](https://www.imes.boj.or.jp/research/papers/japanese/kk17-3-1.pdf)
- [江戸時代の三貨制度, ja.wikipedia](https://ja.wikipedia.org/wiki/三貨制度)
- [寛永通宝, ja.wikipedia](https://ja.wikipedia.org/wiki/寛永通寳)
- [御定相場, ja.wikipedia](https://ja.wikipedia.org/wiki/御定相場)
- [銭相場, kotobank](https://kotobank.jp/word/銭相場-87683)