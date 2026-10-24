<!-- 414 pass: Japan price stability: the research-pass agent's report, 2026-10-24, filed verbatim by the session -->

I ran one search pass for feature 414 (Japan first). Nothing was written to any repository. Each page I read is on the ledger:
- **Outcome `pending`**: every page below that bears on the question, left for the session to cite.
- **Outcome `rejected`**: Akashi 1989 (`keizaikenkyu4001042.pdf`) and Takatsuki DP 07-44R.
- **Outcome `unreadable`**: ISS f-141 and the hermes wp2018-18 PDF.
- **Ledger error to clean up**: I first marked the Uemura 1989 review (keizaikenkyu4004371.pdf) `nothing-found` by mistake, then re-recorded it as `pending`. Make sure the session's ledger keeps the later entry.

`make source-pages` will not fetch PDFs, so I downloaded them with curl. The hook logged each download. Three papers are scans with no text layer: Miyamoto 1975, Shinbo 1975 and the Kato thesis. I quote those from page images I rendered myself, not from the OCR.

## Q1. How much did the overall price level move at each time scale?

**Shinbo Hiroshi 1975, 「幕末期の物価変動／1830～67年」, 『経済研究』26-4, pp. 289-301.** URL: https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1975/keizaikenkyu2604289.pdf. Evidence covers 1802-1867.
- **What the series is (p. 290):** an Osaka wholesale index. Table 1 is a 5-year moving average with 1840-44 = 100. For sake and soy sauce only, it uses Kyoto retail prices.
- **Table 1 values (p. 291), new index:** 1804 82.7; 1810 85.7; 1820 72.3; 1830 89.5; 1836 122.7; 1840 110.0; 1850 115.1; 1858 130.7; 1860 160.2; 1863 244.7; 1865 514.7.
- **p. 293:** 「一般物価のI期の平均は80.9であったが，II期は110.3となり，36%の物価上昇であった。さらにIII期には362.3となり，II期の平均にくらべて実に239%という異常な騰貴が生じているのである。」 (translation) "The general price level averaged 80.9 in period I [1802-29] and 110.3 in period II [1830-58], a 36% rise. In period III [1859-67] it was 362.3, a truly abnormal rise of 239% over period II."
- **p. 297:** 「物価の短期変動は，物価が比較的安定していたI期よりも，物価の上昇傾向にあったII期のほうが大きく，物価の急騰しているIII期にいたっていちじるしく大きくなっているのである。」 (translation) "Short-run price movement was larger in period II, when prices trended up, than in the relatively stable period I, and became remarkably large in period III, when prices soared."
- **Table 5, general price level (p. 297):**
  - Within-year coefficient of variation (CV, the standard deviation over the mean, in percent): 7.4 / 8.1 (7.4) / 16.1 for periods I / II / III.
  - Within-period CV of the annual averages: 7.9 / 13.7 (10.1) / 103.7.
  - Values in parentheses leave out 1836-38.

**Miyamoto Matao 1975, 「近世後期大阪における米価変動と米穀取引機構」, 『経済研究』26-4, pp. 359-368.** URL: https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1975/keizaikenkyu2604359.pdf. Evidence covers 1756-1859, Osaka rice.
- **Appendix table (p. 368):** column (1) is the within-year CV of monthly spot rice prices (正米), year by year. The data come from Tsuruoka 1972, an Otsu merchant's record of Osaka prices.
  - Quiet years: 1.0 to 5%.
  - Famine years: 天明4 (1784) 15.8; 天明6 (1786) 19.0; 天明7 (1787) 20.1; 寛政5 (1793) 18.1; 嘉永3 (1850) 16.5; 嘉永4 (1851) 24.2.
  - Miyamoto's own note 1 warns that the rice brand changes from year to year, so comparing years is somewhat uncertain.
- **My arithmetic, not the source's:** I copied the 88 printed values of column (1) by hand. Median 5.05%, quartiles 3.3% and 8.5%, 90th percentile 11.3%. The session should re-derive these from p. 368.
- **p. 364:** 「天明期を除いて，宝暦-文政期では両米価の乖離率は，上下とも4%以内におさまっているのに対して，天保後期以降は5%以内がまれであり，10%を超えることがしばしばであった。」 (translation) "Apart from the Tenmei years, the spot-futures gap stayed within ±4% from Hōreki to Bunsei. From late Tenpō on it was rarely within 5% and often above 10%."

**Takatsuki Yasuo 2007, DP 07-19-Rev. (Osaka University).** URL: https://www2.econ.osaka-u.ac.jp/econ_society/dp/0719R.pdf. Evidence covers 1798-1864 at daily frequency.
- **Abstract:** 「寛政10(1798年)から安政6(1859)年に渡る，日次の米価系列を用いることとした。既存の，年次，月次といった頻度の米価系列では…不適切であったからである。」 (translation) "We use a daily rice-price series for 1798-1859; the existing annual and monthly series were unsuitable."
- **What the paper measures:** informational efficiency only. It gives no size of daily changes.

**Kato Keiichirō 1998, 『近世後期における米穀・金融市場の展開』 (doctoral thesis, Kobe).** URL: https://da.lib.kobe-u.ac.jp/da/kernel/D2002225/D2002225.pdf. The repository's own text layer is garbled, so I read pp. 63 and 69 from page images.
- **Table 2-3 (p. 69), Osaka Higo rice in 嘉永6-安政元 (1853-54), monme per koku:**
  - July: 90 to 114
  - August: 114 to 97
  - mid-November: 94 to 115
  - Jan.-Mar.: 114 to 98
  - late July-Dec.: 108 to 80
- **Reading:** in a non-famine year, single-month swings of 15-27% occurred.

**Bank of Japan Currency Museum FAQ (IMES).** Archived copy: `/diagram/.specify/source-archive/28/280522866266/20261019T134155Z/text.txt`. Century scale.
- 「江戸の各時期に1両で買えた量をみると、目安としては江戸初期で約350kg、中〜後期で約150kg、幕末の1867（慶応3）年頃で約15〜30kg」 (translation) "Rice one ryō bought: about 350 kg early Edo, about 150 kg mid-to-late Edo, about 15-30 kg around 1867."
- 「幕末の開港後には、輸出の増大などでモノの値段は１年のあいだでも大幅に上昇しました。」 (translation) "After the ports opened, prices rose sharply even within a single year."
- On money: 「公定相場がありましたが、実際には毎日変動しました」 (translation) "There were official rates, but in practice they changed daily."

**Named shocks**
- **Kyōhō famine, 1732.** Kotobank, quoting 草間伊助筆記 inside 『改訂新版世界大百科事典』 (entry by 斎藤洋一). URL: https://kotobank.jp/word/%E4%BA%AB%E4%BF%9D%E3%81%AE%E9%A3%A2%E9%A5%89-53042.
  - 「米価古銀ニテ五六月頃ゟ七月中旬迄ハ壱石六拾四五匁，追々高直ニ相成り，九十月之頃百弐三十匁ニ成候」 (translation) "Rice was 64-65 monme per koku through mid-7th month, then rose to 120-130 monme by the 9th-10th month." That is roughly double in 3-4 months.
  - The 日本大百科全書 entry (辻達也) on the same page: 「連年低落を続けてきた米価が数倍に暴騰し」 (translation) "rice, which had fallen year after year, jumped several-fold."
- **Tenpō famine, 1836-37.** Kobe University press release, 30 March 2026, for Ichino, Masuda, Mikami and Takatsuki, *Scientific Reports* 2026. URL: https://www.kobe-u.ac.jp/sites/default/files/doc-article/2026-03/20260330_press_takatsuki-draft.pdf.
  - 「米価は平年の3～4倍（50～70匁から約200匁）に達し、高値の状態が1837年夏頃まで続いていました。」 (translation) "Rice reached 3-4 times normal (from 50-70 monme to about 200) and stayed high until about summer 1837."
- **1818-29 recoinage and the Tenpō famine.** Saito Osamu 2003, Hi-Stat DP D03-02, archived at `/diagram/.specify/source-archive/29/29b24c306697/20261018T232804Z/text.txt`.
  - "The next two decades saw extremely volatile movements caused by the shogunate's debasement of currencies between 1818 and 1829 and by the so-called Kyoho [sic: Tenpō] famine of 1833-38."
- **Recoinages of 1695, 1706-11, 1714 and 1736: SILENT.** I ran one query (元禄改鋳 物価 上昇率 米価 元文改鋳 …) and read nothing that measures them.

**Reading: ATTESTED ONLY FOR the month and year scales and up, Osaka, 1756-1867.**
- **Within a year:** monthly rice prices typically varied with a CV of about 3-8%, rising to 15-24% in famine years (Miyamoto). The general level's within-year CV was about 7-8% before 1859 and about 16% after (Shinbo).
- **Trend:** the price level fell gently from 1802 to 1820 (82.7 to 72.3, about 13%). From the 1818 recoinage it rose: +36% from period I to period II, roughly flat in the 1840s-50s, then about 4x between 1858 and 1865 (Shinbo Table 1).
- **Shocks that came back:** famine spikes of 2x (1732) and 3-4x (1836) reversed within 1-3 years.
- **Day and week scales:** SILENT on size. Daily series exist, but no literature figure for daily change was found.
- **Within a day:** ATTESTED ONLY FOR the structure of trading, with no size. Takatsuki 0719R notes 24, 25 and 28 record opening (寄附) and closing (大引) prices, trading halts (立用), and trading that went on after the official close.

## Q2. Which goods were steady and which swung?

**Shinbo 1975, Table 5 (p. 297).** Osaka wholesale prices. Within-year CV for periods I / II / III, then within-period CV for I / II / III. Values in parentheses leave out 1836-38.

| Good | Within-year CV (I / II / III) | Within-period CV (I / II / III) |
|---|---|---|
| Rice | 6.9 / 11.3 (9.9) / 19.0 | 11.6 / 22.6 (16.1) / 100.4 |
| Soybeans | 8.0 / 9.6 / 20.3 | 10.5 / 18.0 / 71.3 |
| Wheat | 7.8 / 10.3 / 18.7 | 11.1 / 21.3 / 82.8 |
| Firewood | 8.3 / 10.0 / 16.1 | 7.8 / 14.0 / 70.8 |
| Charcoal | 6.1 / 7.9 / 16.7 | 8.7 / 12.7 / 66.0 |
| Salt | – / 14.4 / 12.0 | – / 22.0 / 98.1 |
| Seed oil | 6.6 / 7.3 / 13.8 | 12.6 / 17.1 / 63.8 |
| Lamp oil (白油) | 6.0 / 7.3 / 15.1 | 12.9 / 17.3 / 64.1 |
| Cotton cloth (木綿) | 1.7 / 3.7 / 8.5 | 3.3 / 11.8 / 75.6 |
| Soy sauce | – | 4.8 / 12.3 / 73.9 |
| Sake | – | 6.6 / 20.1 / 79.8 |
| Silk cloth | – / 6.4 / 9.4 | – / 22.0 / 33.2 |
| Sugar | 12.6 / 6.9 / 17.4 | 26.6 / 14.3 / 47.0 |

- **p. 298:** 「農産物の年内変動係数・期間内変動係数が，工産物のそれよりも一般に大きいことである。」 (translation) "Farm products' within-year and within-period CVs were generally larger than those of manufactures."
- **p. 298:** 「1859年以降における米価の短期変動がはげしいものであったことを明らかにしている。」 (translation) "It shows that rice's short-run movement after 1859 was violent."
- **p. 293:** 「1820年以前において米の価格変動が小さく安定的であったことをわれわれは別稿(新保[17])で指摘した」 (translation) "As we noted elsewhere, before 1820 rice price movement was small and stable."

**Saito 2003 (archived copy above).** "Given the fact that the rice price fluctuated more wildly than the prices of other consumer goods…"

**Seasonal pattern.** Kato 1998, p. 63, summarising Miyamoto 1988, pp. 265-307 (read from the page image).
- 「月内変動では、7～10月の変動が大きく、12～4月に縮小する傾向が見出せる…季節変動をみると、それは1月から7～9月にかけて上昇したのち反落し、ふたたびもとの水準へもどる動きをしめすというパターンが確認されている」 (translation) "Within-month movement is large in July-October and shrinks in December-April. Seasonally, prices rise from January to July-September, then fall back to the earlier level."
- No percentage amplitude was found.

**Wages.** Saito Osamu 1993, 「幕末－明治の賃金変動再考」, 『経済研究』44-4. Archived at `/diagram/.specify/source-archive/d9/d9a8d821ea4f/20261019T050437Z/text.txt`. Evidence covers 1818-1894.
- 「三井京本店のように貨幣賃金が固定的で，物価上昇とともに実質賃金が直線的に低下する極端なケースは他にはみられないものの，全体として実質賃金の低下傾向は確認されている（新保・斎藤1989）」 (translation) "No other case is as extreme as the Mitsui Kyoto head store, where money wages were fixed and real wages fell in a straight line as prices rose; but overall a falling real wage is confirmed."
- 「商家の日雇とサービス業の下男・下女はともに都市の不熟練労働力群に属し，彼らの賃金は伸縮的かつ連動して動いていたからであろう」 (translation) "Merchant-house day labourers and service-trade menservants and maids both belonged to the urban unskilled pool; their wages were flexible and moved together."
- 「三井京本店に雇用された職人の貨幣賃金がインフレにもかかわらずあれほどまでに固定的であったのも，固定給以外の特別給付の額が増大したからかもしれない」 (translation) "That the money wages of Mitsui Kyoto's craftsmen stayed so fixed despite inflation may be because special payments outside the fixed wage grew."
- Same text: spot-market day labourers could not expect such allowances.

**Rents.** Washizaki Shuntarō 2012, 『經濟學研究』79-4. Archived at `/diagram/.specify/source-archive/d7/d74d51dc7f44/20261019T092707Z/text.txt`.
- **Minami-Denmachō, Kansei to Tenpō (about 40 years):**
  - Monthly ground rent per front tsubo went from 3.8-4.0 and 3.8-4.5 monme to 4.0-4.5 and 4.0-5.0 monme.
  - Back-lot house rent went from the 3-monme range to the 4-monme range.
  - 「表坪地代は５〜９ポイント､ 裏坪店賃は11〜18ポイント上昇」 (translation) "Front-lot ground rent rose 5-9 points, back-lot house rent 11-18 points."
- **Mitsui's 40 properties, rent receipts (1791 = 100):** 1836 116, 1839 112, 1843-45 113 / 107 / 110.
- **My juxtaposition, not the source's:** over 1820-1858 Shinbo's general index rose from 72 to 131, while these rents rose about 10-20%.
- **Keep separate:** the source's Table 6 tracks ward dues (町入用), not rents. Those tracked the cost of living.

**Reading: ATTESTED.**
- Food and farm goods swung most (rice, soybeans, wheat, rapeseed). Manufactures swung least (cotton cloth's within-year CV was 1.7-8.5).
- Fuel and oil sat in between. Salt sat in between to high (data only from 1830).
- Rents were sticky: about +10-20% over decades in which the price level nearly doubled.
- **Wages: ATTESTED ONLY FOR** retained (お抱え) craftsmen at Mitsui Kyoto. Market day-labour and service wages were flexible and moved with prices.

## Q3. How far did prices differ between places?

- **Shinbo 1975, p. 290 (page image):** 「同一品目について大阪卸売価格と京都小売価格の両者が知られるものからみるかぎり，京都と大阪の物価はほぼパラレルに動いており，また卸売価格と小売価格のひらきが時期によって大きく異なるということもなかった。」 (translation) "Where both Osaka wholesale and Kyoto retail prices are known for the same item, Kyoto and Osaka prices moved nearly in parallel, and the wholesale-retail gap did not change much over time."
- **Takatsuki 2012, RIEB DP2012-22.** URL: https://www.rieb.kobe-u.ac.jp/academic/ra/dp/English/DP2012-22.pdf.
  - "the Otsu market had reflected the rice prices in Osaka within two days in the early 19th century, and within a day in the mid-19th century."
  - "letters from Edo to Osaka, which were approximately 500 kilometers apart, were delivered within about six days."
- **Kato 1998, p. 69 (page image):**
  - 「大坂米価を基準にすると、大津米価は大坂米価との連動性が高い…江戸と兵庫の両米価は…時期によってはちがいが目立つ場合もしばしば見受けられる」 (translation) "Against Osaka, Otsu's price moved closely with it; Edo's and Hyogo's often diverged noticeably at times."
  - Note 30: two Hyogo brands differed by 「0.4%ほど」 (translation) "about 0.4%", with a correlation of 0.962.
- **Bassino and van der Eng, CEI WP 2018-18**, abstract via https://ideas.repec.org/p/hit/hitcei/2018-18.html. Covers 1720-1857.
  - "It analyses rice prices for 13 markets across Japan during 1720-1857 and finds that Japan had relatively well-integrated rice markets, particularly western Japan."
  - "In eastern Japan market integration was partially impeded by distance to Osaka…"
  - "Relatively well-integrated markets did not prevent major famines during 1732-1733, 1783-1786, and 1833-1838."
- **Uemura Masaharu 1989, review of Miyamoto 1988**, 『経済研究』40-4. URL: https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1991/keizaikenkyu4004371.pdf.
  - 「大坂・広島・加賀米価の変動係数が寛文5年（1665）頃から低下している様子が図示され」 (translation) "It is shown that the CV across Osaka, Hiroshima and Kaga rice prices fell from about 1665."
  - The reviewer disputes the cause that Miyamoto gives for this.
- **Abe Shinya 2021**, 『社会経済史学』87-1. Archived at `/diagram/.specify/source-archive/ec/ec2ad94265e3/20261002T122640Z/text.txt`.
  - 「大坂米価は全国の基準米価として機能した」 (translation) "The Osaka rice price served as the national benchmark."
- **Saito 2003, town against country:** "In the base period of 1802-4… Kami-Kawarabayashi farm workers was 1.0 monme while the corresponding spring rate in Kyoto's casual labour market was on average 0.92 monme." Also: "the city indices were more volatile than the rural ones."

**Reading: ATTESTED ONLY FOR the direction of co-movement, not spread sizes.**
- Kyoto and Osaka moved in parallel. Otsu followed Osaka within 1-2 days.
- Edo, Hyogo and eastern Japan diverged more, more so with distance and in famines.
- No literature figure was found for the typical level spread between cities by good. The session's own figures from the Iwahashi 14-place series will be the measure.

## Where daily and half-yearly data can be read

- **RIEB 近世経済データベース.** About page archived at `/diagram/.specify/source-archive/be/bee016d28ebe/20261019T161327Z/text.txt`. The spreadsheet is archived at `/diagram/.specify/source-archive/d2/d2aae944e8db/20261019T161020Z/served.xlsx`.
  - 「三井家大坂両替店の記録「日記録」より、18世紀中期から明治初年にわたる、日々の米価、金銭比価、そして天候を採録する」 (translation) "From the Mitsui Osaka exchange office's diary, it records daily rice prices, gold-copper rates and weather from the mid-18th century to early Meiji."
  - The rates run from 天明7 (1787) to 明治4 (1871).
- **Printed daily series:**
  - 三井家編纂室 1916, 『自天明七年至明治四年大阪金銀米銭并為替日々相場表』
  - 鈴木直二 1935, 『大阪に於ける幕末米価変動史』
  - 鶴岡実枝子 1972, 『史料館研究紀要』5
  - 「万相場日記」 (Takatsuki's daily source)

## Q4. A closeness rule

**SILENT.** No source states a rule. The inputs above are what the session has to derive one from.

## Leads not followed

- Takatsuki 2008, ISS F-141 (Osaka-Otsu): unreadable because the server's TLS certificate chain is incomplete. The 2012 RIEB version was read instead.
- Bassino and van der Eng, full PDF: the hermes-ir host no longer resolves, so only the abstract was read.
- 宮本又郎 1988, 『近世日本の市場経済』, ch. 5 (pp. 265-307): the within-month CVs and seasonal indices themselves.
- 宮本又郎 1981, 「江戸時代における諸地方米市場間の連関性について 1651-1850」, 『大阪大学経済学』31-2/3: correlations across regional rice markets.
- 岩橋勝 1981 and 新保博 1978: the books themselves.
- Wakita 2001, *Journal of Banking and Finance*, on seasonality: paywalled.
- Recoinage effects: Murai Atsushi's 荻原重秀 book (a J-CAST review cites a rise of "年3%弱" in the 11 years after 1695), and Suzuki Atsuko, Osaka WP 2306, on 1718 (full text at http://www2.econ.osaka-u.ac.jp/econ_society/dp/2306.pdf).
- Takeya 1999 on Osaka building-trade guilds, which bears on how guilds set wages: archived at `/diagram/.specify/source-archive/c1/c1f9de54732c/` but not read.
- Allen et al. 2009 (LSE wp123, archived) and Bassino and Ma: grepped, no measured figure on Japanese price volatility.

Sources:
- [Shinbo 1975](https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1975/keizaikenkyu2604289.pdf)
- [Miyamoto 1975](https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1975/keizaikenkyu2604359.pdf)
- [Uemura 1989 review](https://econ-review.ier.hit-u.ac.jp/wp-content/uploads/files/1991/keizaikenkyu4004371.pdf)
- [Takatsuki DP 07-19R](https://www2.econ.osaka-u.ac.jp/econ_society/dp/0719R.pdf)
- [Takatsuki RIEB DP2012-22](https://www.rieb.kobe-u.ac.jp/academic/ra/dp/English/DP2012-22.pdf)
- [Kato 1998 thesis](https://da.lib.kobe-u.ac.jp/da/kernel/D2002225/D2002225.pdf)
- [Bassino and van der Eng abstract](https://ideas.repec.org/p/hit/hitcei/2018-18.html)
- [Kotobank 享保の飢饉](https://kotobank.jp/word/%E4%BA%AB%E4%BF%9D%E3%81%AE%E9%A3%A2%E9%A5%89-53042)
- [Kobe 2026 press release](https://www.kobe-u.ac.jp/sites/default/files/doc-article/2026-03/20260330_press_takatsuki-draft.pdf)
- [Suzuki, Osaka WP 2306](https://ideas.repec.org/p/osk/wpaper/2306.html)
- Archived copies: Saito 1993, Saito 2003, Washizaki 2012, Abe 2021, the IMES FAQ, and the RIEB about page and spreadsheet (paths above).
