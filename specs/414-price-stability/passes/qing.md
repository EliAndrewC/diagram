<!-- 414 pass: Qing price stability: the research-pass agent's report, 2026-10-24, filed verbatim by the session -->

# Search pass, feature 414: how much Qing and late-Ming prices moved, at each time scale, by good and by place

**Overall:** only the middle scales are well covered: half-year, season and year, from the 18th-century grain reports. Within-day, day-to-day and week-to-week movement is **SILENT**. Nothing I read gives prices finer than one month, and the official grain-price reports (糧價清單) give each prefecture's monthly high and low. Century drift appears in two sources that disagree, one counting in copper cash and one in silver; both are below. The gap in price between places is shown only as how closely prices moved together, not as how far apart they were.

I wrote nothing in any repository. Pages read are on the ledger. PDFs that `make source-pages` could not read were fetched with curl and pdftotext into the scratchpad; the hook logged those attempts.

## Q1. How much did the overall price level move, at each scale?

**Shiue 2002, AER 92(5)** (archived: https://spot.colorado.edu/~shiue/p1406_s.pdf). Evidence: 1742–1795, 121 prefectures in ten provinces, rice.
- Year to year: "The annual coefficient of variation, taken at 20-year intervals for all prefectures and averaged, is equal to 0.12, with a maximum of 0.17 for the entire sample. Selecting the one prefecture from each of the ten provinces with the maximum coefficient of variation, and averaging, gives a value of 0.24. These figures are similar to the coefficient of variation on wheat prices taken at 20-year intervals in southern England for the years 1800–1825 (0.26), or in New York for 1825–1914 (0.16–0.34), and lower than those in England from 1245–1350 (0.20–0.43)"
- The data used: "I use the average [(highest + lowest)/2] price in the second month and the eighth month, according to a lunar calendar."

**Shiue & Keller, NBER w10778** (https://www.nber.org/system/files/working_papers/w10778/w10778.pdf; this is the working-paper version of AER 2007). Evidence: 1742–1785.
- Spread of price levels: "During the period 1742 to 1785, the average coefficient of variation for 15 European markets for which there is data is equal to 0.188, with a standard deviation of 0.051. For the 121 markets in Chinese prefectures during the same period, the average coefficient of variation is equal to 0.131 (standard deviation of 0.029)." This measures spread around the period mean, so it includes any trend.
- Half-year changes: "On average, this volatility in the 15 European markets is 0.127 … For the 121 Chinese markets, the volatility is on average 0.092". The measure is the standard deviation of the residual of log price changes, seasonally adjusted. The period length is stated as "We use prices at semi-annual frequency (one period lasts six months)."

**Keller, Shiue & Wang, "Capital Markets in China and Britain, 1770–1860", online appendix** (https://topcat.aeaweb.org/articles/materials/14932). Evidence: 1770–1860. I read only the appendix, not the paper.
- Table A.4, "Average monthly grain price changes, 1770 to 1860": "China All grains 15,152 1.114 2.446 13.373". That is a mean of 1.114% per month and an SD of 2.446, during storage months only, annualized to 13.4%. Britain wheat: "0.854 2.577 10.248".
- Table A.3 contradicts itself:
  - Column header: "One-month Δ non-zero Mean". China wheat 0.344, millet 0.456, rice 1st quality 0.517, rice 2nd quality 0.464; Britain 0.994.
  - Notes to the same table: "Last column gives the fraction for which the one-month price difference is zero".
  - I have not settled which reading is right. Either way, about half of China's reported month-to-month figures did not change. That may reflect how the reports were compiled rather than the market.

**閱世編 (Ye Mengzhu)** (archived: https://zh.wikisource.org/wiki/閱世編, 食貨一). Evidence: Songjiang and Shanghai, 1630s–1680s. Prices in silver unless marked 文 (copper cash).
- 1642: "白米每石紋銀五兩" (translation: white rice 5 taels of fine silver per shi).
- Between bad years: "自此以往，米價以二三兩為常" (translation: thereafter rice prices of 2–3 taels were normal).
- 1669 low: "九年，新米每石紋銀六錢" (translation: in [Kangxi] 9 [1670], new rice 0.6 tael of fine silver per shi). Before that: "未有如八年己酉之賤者" (translation: none was as cheap as [Kangxi] 8 [1669]).
- So within about 30 years the price moved roughly eightfold between peak and trough.
- 1680–81: "康熙十九年庚申春，因米價騰貴…至次年辛酉，米價頓減" (translation: spring 1680 rice prices soared … the next year, 1681, rice prices fell abruptly).

**履園叢話 (Qian Yong), 米價** (archived: https://zh.wikisource.org/wiki/履園叢話/01). Evidence: Suzhou, Songjiang, Changzhou and Zhenjiang, 1707 to about 1800. Prices in copper cash per sheng.
- "康熙四十六年…米價每升七文，竟長至二十四文…雍正、乾隆初，米價每升十餘文。二十年蟲荒…長至三十五六文…後連歲豐稔，價漸復舊，然每升亦祇十四五文為常價也。至五十年大旱，則每升至五十六七文。自此以後，不論荒熟，總在廿七八至三十四五文之間為常價矣。"
- (translation): In 1707 rice went from 7 cash per sheng to as much as 24. In the Yongzheng and early Qianlong years it was 10-odd cash. In the 1755 insect famine it rose to 35–36. After several good harvests it gradually returned, but 14–15 cash became the normal price. In the great drought of 1785 it reached 56–57. From then on, harvest good or bad, the normal price stayed between 27–28 and 34–35 cash.

**全漢昇 1957, 〈美洲白銀與十八世紀中國物價革命的關係〉, 史語所集刊 28下: 517–550** (https://www1.ihp.sinica.edu.tw/storage/w2_file/4232vsthcJJ.pdf). I transcribed this from page images, because the PDF has no text layer and Chinese OCR is not installed.
- p. 548: "十八世紀的中國，除如歐洲過去那樣受美洲白銀的影響以外，又要受人口增加的影響，故物價波動得特別利害，就米價來說，在整個十八世紀約上漲四倍有多。"
- (translation): Eighteenth-century China, besides feeling American silver as Europe once had, also felt population growth, so prices moved especially violently. For rice, over the whole 18th century the price rose about "四倍有多".
- **Translation flag:** the phrase 上漲四倍有多 can mean "more than fourfold" or "rose by more than four times", that is, more than fivefold. I give it literally.
- The examples on p. 549–550 are in copper cash. Hong Liangji, 1793: "米之以升計者錢不過六七…今則…昔之以升計者，錢又須三四十矣" (translation: rice by the sheng was no more than 6–7 cash; now it takes 30–40). Wang Huizu, Xiaoshan, 1794: "夏間米一斗錢三百三四十文。往時米價至一百五六十文，即有餓殍" (translation: this summer a dou of rice cost 330–340 cash; formerly, at 150–160, people starved).

**Lu Feng & Peng Kaixiang 2004, 我国长期米价研究（1644-2000）, CCER C2004009** (https://nsd.pku.edu.cn/attachments/e0f218104a1f41bba495f50835b5d4af.pdf). Evidence: Suzhou and Qing prices in silver.
- "清代前中期两百多年间名义米价虽有不小波动，但是上升趋势并不明显" (translation: over the 200-odd years of the early and middle Qing, nominal rice prices fluctuated considerably, but the upward trend is not marked).
- Table 2-1 gives the linear time trend of 5-year average prices, 1700–1800, in taels per shi per decade: 苏州 0.067, 广东 0.061, 湖北 0.056, 湖南 0.049. The note reads "时间趋势系数代表每十年的平均变化量" (translation: the trend coefficient is the average change per decade).
- Copper and silver: "18世纪银钱比价虽有缓慢上升趋势，但与1000文/两比率还相距不远。嘉庆后转而急速攀升，直至道光年间都是银贵钱贱，在1850年前后达到2000文/两以上。随后银钱比价急剧跌落…到19世纪末年，银钱比价降至约1200文/两水平。"
- (translation): In the 18th century the cash-per-tael rate rose slowly but stayed near 1,000. After the Jiaqing reign it climbed fast; through the Daoguang reign silver was dear and cash cheap, passing 2,000 cash per tael around 1850. It then fell sharply … to about 1,200 by the end of the century.

**Allen et al., LSE WP 123, Appendix Table I** (`allen-2009-china-wages`, archived wp123.pdf; the data come from `gamble-burgess-1921-peking-survey` / Gamble 1943). Evidence: rural Beijing, 1807–1902. Copper cash per silver tael:

| Year | Cash per tael |
|---|---|
| 1807 | 979 |
| 1827 | 1,265 |
| 1838 | 1,553 |
| 1846 | 2,010 |
| 1853 | 2,205 |
| 1854 | 2,723 |
| 1856 | 4,970 |
| 1880 | 8,510 |
| 1902 | 6,079 |

- The table counts 1 tiao as 1,000 cash. Gamble reports that the local tiao was 500 cash before 1860 and 100 after, so the series runs on the paper's stated convention.

**Liu Ziang 2022, LSE WP 339** (https://www.lse.ac.uk/asset-library/information/liu-updated-wp-339.pdf). Evidence: 1530–1840.
- "In the Qing period, the nominal wage exhibited three major rises in the 1680s, the 1720s, and the 1790s along with a temporary surge in the early decades of the nineteenth century."
- Late Ming: "hyperinflation during the Ming-Qing transition".

**Reading: ATTESTED** for the scales from half-year to century; **SILENT** below one month.
- Half-year: 18th-century grain moved by about a 9% SD of seasonally adjusted change in China, against about 13% in Europe.
- Year to year: prefecture CV about 0.12, rising to 0.24 in the most volatile prefectures.
- Swings that came back are dated: 1642, 1651, 1669–70, 1680–81, 1707, 1755, 1785.
- Century drift is contested by currency, and the dispatching session should see the split unresolved:
  - In copper cash, Suzhou rice rose about 4–5 times, from 7 to 27–35 cash per sheng, over 1700–1800 (Qian Yong, Hong Liangji, 全漢昇).
  - In silver, the trend was about +0.06 tael per shi per decade, "not marked" (Lu & Peng).
  - The cash-per-tael rate roughly doubled from 1807 to 1850, jumped again in 1854–56 (Taiping war years), and reached about 8,500 in 1880 in the Beijing series.
- I read no grain price for 1853–64 itself.

## Q2. Which goods were steady and which swung?

**Seasonal (the spring hunger gap).**
- Shiue 2002, footnote 18 (1742–1795): "the average rate of change in prices between single-cropping (1.12) and multiple-cropping provinces (1.14) over the same six-month period are similar". This is the price in the 8th lunar month over the 2nd, a rise of about 12–14% before the harvest.
- Wang Yeh-chien & Huang Ying-chueh 1999, 史語所集刊 70.2, Chinese abstract (https://www1.ihp.sinica.edu.tw/Publications/Bulletin/982/Article/359). Evidence: 1741–1760.
  - "蘇、杭米價大抵於七、八月達高峰，十月、十一月最低；泉、廣二府高峰均為五月，谷底分別為九月、十一月。" (translation: Suzhou and Hangzhou rice peaks in the 7th–8th month and is lowest in the 10th–11th; Quanzhou and Guangzhou peak in the 5th month, with lows in the 9th and 11th months respectively).
  - "各府糧價也呈現大致四年的週期性波動" (translation: each prefecture's grain price also shows a roughly four-year cycle).
- 閱世編, Songjiang 1651, month by month:
  - "八年辛卯，二月，白米每石三兩。三月，每石三兩五錢。四月，每石四兩。六月，長至四兩八、九錢…七月，新穀石價二兩。"
  - (translation): 1651: 2nd month white rice 3 taels per shi; 3rd month 3.5; 4th month 4; 6th month up to 4.8–4.9; 7th month new grain 2 taels.
  - That is about +60% across the gap, then a halving at the harvest. This was a bad year.

**Other grains.** Lu & Peng: "海州…表2-2报告它们之间一阶差分值的相关系数，在0.73-0.95的较高水平" (translation: for Haizhou's different grains, the correlations of first differences are high, 0.73–0.95). Grains moved together within one place.

**Beans (閱世編).** "黃豆之價，常年較米稍減，大約豆一石可準米八、九斗" (translation: in a normal year soybeans are a little below rice, about 1 shi of beans for 8–9 dou of rice). In bad years the ratio broke, from 2:1 one way to parity.

**Cotton and cloth (閱世編).** Songjiang, 1620s–1684.
- Raw cotton swung wildly. "木棉百斤一擔，值銀一兩六七錢。崇禎初，漸至四、五兩。甲申以後…不過值錢二千文，準銀五六錢…八年三月，九兩一擔" (translation: raw cotton was 1.6–1.7 taels per 100 jin; early Chongzhen up to 4–5; after 1644 only 2,000 cash, about 0.5–0.6 tael; 1651 3rd month 9 taels).
- Cloth was steadier. 標布 "每疋約值銀一錢五六分…今大概以二錢為上下也" (translation: 標布 cloth was about 0.15–0.16 tael per bolt … now generally about 0.2 tael).
- **ATTESTED ONLY FOR** 17th-century Songjiang. In 1793 Hong Liangji gives cloth per zhang at 30–40 cash, now 100–200 cash (全漢昇 p. 550).

**Fuel (閱世編, 食貨六).** "大約百斤之擔，值新米一斗" (translation: roughly 100 jin of firewood is worth one dou of new rice). The ratio broke repeatedly: "七年二月，米價賤而柴價貴" (translation: 1650, 2nd month, rice cheap and firewood dear).

**Salt (清史稿 卷123, archived).** This is the Changlu administered price, not a market price.
- "長蘆鹽價，自康熙二十七年定每斤銀一分四毫至一分二釐六毫不等。雍正六年…「康熙時，銀一兩換制錢千四五百，每鹽一斤，錢十六文。今每兩合錢二千，而鹽價如故…」至十年，題准每斤加銀一釐。"
- (translation): The Changlu salt price was fixed in 1688 at 0.0104–0.0126 tael per jin. In 1728 a memorial said: under Kangxi a tael bought 1,400–1,500 cash and salt was 16 cash per jin; now a tael is 2,000 cash but the salt price is unchanged … in 1732 an increase of 0.001 tael per jin was approved.
- Further step increases: "嘉慶…每斤加價二文" (translation: 2 cash per jin added for river works), and late Guangxu additions of 2 and 4 cash. Jiaqing 5 [1800], the emperor: "今計食鹽者每日止一二文" (translation: a salt-eater now spends only 1–2 cash a day).
- On smuggling: "官鹽價貴，私鹽乘之" (translation: official salt was dear and private salt exploited it).
- **ATTESTED ONLY FOR** the administered price, which held for decades and moved by decree. I read no market or private-salt series.

**Wages.**
- Allen Appendix Table I, Beijing copper wages in cash per day: 81 (1807), 88 (1827), 91 (1838), 96 (1846), 93 (1853), 110 (1856), 255 (1860), 470 (1902).
- Over 1807–1853 the copper wage was nearly flat while cash per tael more than doubled, so the silver wage fell from 0.041 to 0.021 tael.
- Allen's own warnings apply:
  - "we view our wage series is more reliable as indications of long-term trend than short-term fluctuations".
  - Li's Zhili grain prices "are five-year moving averages, so annual fluctuations are suppressed".
  - "for meat, edible oil, lamp oil, candles, the price of wheat flour was applied". So the Beijing series for those goods are proxies, not independent prices.
- Liu WP 339:
  - "wages (cash payments and in-kind rewards) could be sticky in the short-term, but tended to respond and adjust to commodity and currency prices on the market in the long-term" (citing Peng, 近代北京價格).
  - "nominal wages moved in tandem with prices, but not as quickly as the increase in prices."
- 閱世編, 1642 famine: "雇募工作，惟求一飽" (translation: hired workers asked only to be fed).

**Reading:**
- **ATTESTED** for grain: about +12–14% from the 2nd to the 8th lunar month in normal 18th-century years, and +60% in the 1651 crisis; grains moved together.
- Wages were sticky in copper over years to decades, then caught up in steps.
- **ATTESTED ONLY FOR** 17th-century Songjiang for cotton, cloth, fuel and beans.
- Salt is the administered price only.

## Q3. How far did prices differ from place to place?

Shiue & Keller name the limit of their own method: "One reason for studying price correlations instead of absolute price gaps lies in the multitude of currencies". What follows is mostly about how closely prices moved together, not how far apart they were.

- **Shiue & Keller, Table 2a (1770–1794), average correlation of rice prices by distance band:**

  | Distance | Yangzi Delta | Yangzi River prefectures | Provincial capitals |
  |---|---|---|---|
  | <150 km | 0.83 | 0.81 | none |
  | 150–300 km | 0.81 | 0.74 | 0.59 |
  | 450–600 km | — | 0.66 | 0.38 |
  | >1,050 km | — | — | 0.08 |

  For comparison, England was 0.87 under 150 km and 0.71 at 450–600 km.
- **Keller, Shiue & Wang, Table A.6 (1770–1860):** a different measure, correlations of grain interest rates (storage-month price gradients), not of price levels. China rice 1st quality: 0.65 at 0–100 km, 0.20 at 400–500 km, 0.11 at 500–600 km. Britain wheat: 0.80, 0.70 and 0.70.
- **Wang & Huang 1999, English abstract:** "the weak correlation in prices between Suzhou and Guangzhou implies that the two key economic areas, the Yangzi Delta and the Canton Delta, remained poorly integrated in the eighteenth century."
- **Lu & Peng, Table 2-1:** first-difference correlations of 5-year averages, Suzhou with 广东 0.58, 湖北 0.79, 海州 0.83; 海州 with 湖南 −0.69.
- **Bernhofen et al. 2017, Nottingham GEP 2017/12** (https://nottingham.ac.uk/gep/documents/papers/2017/2017-12.pdf): "uncovers a secular decline in market integration across all bilateral distance categories of Southern China" over 1740–1820.
- **Price levels (Allen WP 123):**
  - Wages: "the wage level for Beijing and Canton was set in 1700, based on the predicted values in the regression of 0.0897 and 0.0835 taels … For Suzhou, 0.09 taels".
  - Baskets: "The figure shows very little difference between the two consumer price indices for both Beijing and Suzhou/Shanghai (or Canton not shown in the figure) for the eighteenth century."
- **Within the year, by geography (Shiue 2002):** "Within the harvest year, prices fluctuate more as one moves from prefectures closer to waterways to those further inland".

**Reading: ATTESTED ONLY FOR** co-movement of grain prices with distance. It is high within about 300 km on waterways, and close to zero beyond about 1,000 km between provincial capitals. Level spreads are **SILENT** apart from Allen's wage and basket lines, which show Beijing, Canton and Suzhou at about the same level in silver.

## Q4. Material for a closeness rule (not a rule)

- Normal 18th-century noise, per half year: about 9% SD (seasonally adjusted).
- Year to year: CV about 0.12.
- Seasonal: about 12–14%.
- Famine spikes: 2–3×, and up to 5–8× on the 17th-century Songjiang peak-to-trough figures.
- Drift in silver: about +0.05–0.07 tael per shi per decade in the 18th century (Lu & Peng).
- Drift in copper: about 4–5× over the 18th century (Qian Yong, 全漢昇).
- Cash per tael: about 1,000 to 2,000 over 1807–1850, then about 5,000–8,500 in 1856–1880.

A conversion made in copper cash must therefore carry the rate's date in a way a silver conversion need not. Prices more than about 500 km apart moved largely independently.

## Where machine-readable series can be had
- **Academia Sinica 清代糧價資料庫:** https://mhdb.mh.sinica.edu.tw/foodprice/about.php returned 403, so I could not read it; access appears to need a login. I reached no free bulk download.
- **openICPSR 116285:** Shiue & Keller replication data (https://www.openicpsr.org/openicpsr/project/116285/version/V1/view). URL only; I did not open it.
- **Keller, Shiue & Wang appendix:** describes the data but contains no data files.
- **Lu & Peng and Liu:** graphs only, no tables.
- **Allen et al. WP 123:** Appendix Table I is the only tabulated series I read (Beijing copper wages and cash per tael, 1807–1902).

## SILENT, with what blocked it
- **Within-day, day-to-day, week-to-week:** no source read is finer than monthly.
- **Taiping-era grain prices for 1853–64:** none read; only the exchange-rate route above.
- **Wang Yeh-chien 1992 and Lillian Li 1992 chapters:** both copies at works.swarthmore.edu were blocked by Cloudflare (403).
- **Salt pages:** two NUS pages on Zhao Yiling's salt-trafficking paper came back empty; a UBC thesis on the Lianghuai salt monopoly (c. 1800) hit a captcha.
- **Snippet-only claims dropped:** the 1838 黃爵滋 "一千六百多文" figure and the Academia Sinica access terms appeared only in search snippets, so they are not reported as evidence.

## Leads not followed
- 全漢昇 1957 pp. 519–545: the regional price tables.
- Chuan & Kraus 1975, *Mid-Ch'ing Rice Markets*: chapter on seasonal variation in the Lower Yangzi, 1713–19.
- Chen Chunsheng 陳春聲 1992, 市場機制與社會變遷 (Guangdong rice prices).
- Perdue on Hunan grain prices.
- Cheung Sui-wai 2008, *The Price of Rice*. Only the CUHK review (https://www.cuhk.edu.hk/ics/journal/articles/v53p330.pdf) was read. The reviewer summarizes Cheung as explaining the 1788–95 Suzhou price fall by dear silver ("蘇州米價的低落…反映的是銀價高漲", translation: the fall in Suzhou rice prices … reflects the high price of silver) and by the East India Company's halt in silver imports, 1793–95.
- 彭凱翔《清代以來的糧價》 and 彭信威《中國貨幣史》 p. 497 (the decadal rice index).
- 林滿紅《銀線》 on the 1820s–50s silver outflow.
- Studies of the Xianfeng 大錢 and paper-money inflation.
- The Keller, Shiue & Wang main text.
- Salt retail and private-salt prices: 陳鋒, Ho Ping-ti, Metzger.

Scratch copies are in /tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/ (nber, ksw, wp339, pku, chuan, cuhk, bern) and /tmp/l7r-pass/ (ihp982, ihp99).

Sources:
- [Shiue & Keller, NBER w10778](https://www.nber.org/system/files/working_papers/w10778/w10778.pdf)
- [Keller, Shiue & Wang online appendix](https://topcat.aeaweb.org/articles/materials/14932)
- [Liu, LSE WP 339](https://www.lse.ac.uk/asset-library/information/liu-updated-wp-339.pdf)
- [Wang & Huang 1999, Chinese abstract](https://www1.ihp.sinica.edu.tw/Publications/Bulletin/982/Article/359)
- [Wang & Huang 1999, English abstract](https://www1.ihp.sinica.edu.tw/en/Publications/Bulletin/99/Article/359)
- [全漢昇 1957](https://www1.ihp.sinica.edu.tw/storage/w2_file/4232vsthcJJ.pdf)
- [Lu & Peng 2004](https://nsd.pku.edu.cn/attachments/e0f218104a1f41bba495f50835b5d4af.pdf)
- [Bernhofen et al. 2017](https://nottingham.ac.uk/gep/documents/papers/2017/2017-12.pdf)
- [CUHK review of Cheung](https://www.cuhk.edu.hk/ics/journal/articles/v53p330.pdf)
- [openICPSR 116285](https://www.openicpsr.org/openicpsr/project/116285/version/V1/view)
- Archived: spot.colorado.edu/~shiue/p1406_s.pdf, lse.ac.uk wp123.pdf, zh.wikisource 閱世編, 履園叢話/01, 清史稿/卷123
