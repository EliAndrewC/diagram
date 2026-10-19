# Pass - fruit (#5 question 1) (research-pass, 2026-10-19; its reply verbatim)

I found only one Japanese fruit price, and it is for the countryside, not Edo. A persimmon cost 6 mon in rural Kanto in the early 1800s, from a secondary source. Pears, native apples, dried persimmons, and prices in Edo itself or in castle towns are SILENT. The Chinese comparison is well attested in two official texts, with silver or paper-money prices for persimmons, pears, apples and crabapples.

**Archive.** I ran `make archive-find` from `/diagram/.clones/money` for 柿, 干柿, 梨, 林檎, 和林檎, 水菓子, persimmon, pear, apple, 守貞謾稿, 物価書上, 御定直段, 青物, 蘋果, 九卿议定, 物料价值 and 會典則例. No archived text gives a fruit price. Two archived texts did give the wages paired below:
- **Gao Shouxian's paper** on the 1736 Qing price list (dpm.org.cn u63e60647c73ae.pdf).
- **The Okayasu family documents** (Miyashiro town, okayasukebunsyo.pdf).

## 1. Sources that bear on the question

**A. Japan, rural Kanto, first half of the 19th century (secondary).** Bank of Japan Currency Museum handout, "江戸時代の１両は今のいくら？", https://www.imes.boj.or.jp/cm/history/historyfaq/mod/1ryou.pdf
- `make source-pages` found no text layer, so I downloaded it and ran pdftotext.
- Price table: 「柿　1個　6文」 (translation: "persimmon, 1 piece, 6 mon")
- Its own caveat: 「ここで挙げたような個数・量も判明する事例を同じ史料から拾うのは困難なため、いくつかの異なる史料から掲げています（関東農村19世紀前半）」 (translation: "since it is hard to find cases where the count and quantity are both known in a single document, these are taken from several different documents (Kanto villages, first half of the 19th century)")
- Wages on the same sheet, from different times and places than the persimmon:
  - 「料理人の賃金　１日　300文」 (translation: "cook's wage, 1 day, 300 mon")
  - 「江戸時代に１両で1日2３人の大工が雇えたという事例があります。（18世紀後半）」 (translation: "there is a case in which one ryō hired 23 carpenter-days (late 18th century)")
  - 「町方奉公人　１年　男性2両　女性1両」 (translation: "town servants, per year: men 2 ryō, women 1 ryō")

**Nearest craftsman wage, same region (archived).** okayasukebunsyo.pdf, document 31, the 1818 crafts rule for 武州埼玉郡久米原村 (a Musashi village):
- 「一、弐百文　大工手間代」 (translation: "200 mon, carpenter's day wage")
- 「一、百八拾文　木挽手間代」「一、百八拾文　車力手間代」 (translation: "180 mon, sawyer's day wage; 180 mon, carter's day wage")
- Three graded lines read 116, 100 and 80 mon (「手間代壱番／弐番／三番」), but the trade name above them is unreadable in the archived text. I found no unskilled wage.
- At these figures a persimmon is about 1/33 of a carpenter's day.

**B. Qing, Beijing, court purchase prices (Qianlong).** 欽定大清會典則例 (Siku edition) 卷154, 光祿寺 掌醢署, https://zh.wikisource.org/wiki/欽定大清㑹典則例_(四庫全書本)/卷154
- Purpose clause, showing these are court purchase prices, not market retail: 「園地毎畝嵗徴銀一錢貯庫以充和買鮮果之用設行户一人承辦」 (translation: "each mu of orchard land pays 0.1 tael a year into the treasury to fund the court's purchase of fresh fruit; one licensed supplier is appointed to handle it")
- Prices: 「橙價銀五分橘柑四分朱橘白桃紅桃石榴二分李杏花紅三釐柿八釐蘋果三分㯽五釐黄梨波梨一分五釐紅梨棠梨一分三釐」 (translation: "orange 0.05 tael; tangerine 0.04; … plum, apricot, 花紅 [Chinese crabapple] 0.003; persimmon 0.008; 蘋果 [apple] 0.03; 㯽 0.005; yellow pear and 波梨 0.015; red pear and 棠梨 0.013")
- The unit is not written for these items. Per piece is my inference, because the list only names units (毎片, 毎斤) from the next items on.
- I have not identified the fruit 㯽.
- Dried persimmon: 「柿餅毎斤二分二釐」 (translation: "dried persimmon, 0.022 tael per jin")
- Date: an undated standing rule in the Qianlong 會典則例 (compiled 1764). The nearest dated entry before it is 乾隆十三年 (1748).

**Nearest wage (archived, Gao Shouxian on the 1736 九卿议定物料价值).** 「木石砖瓦油画等匠…不论长、短给钱154文」「壮夫…不论长、短给钱75文」 (translation: "wood, stone, brick, tile and painting craftsmen: 154 cash a day; able-bodied laborers: 75 cash a day")
- Gao converts at 「银1两兑钱800文」 (translation: "1 tael of silver = 800 cash"), his figure for 1736. That is 12–28 years before the fruit list.
- Converted at that rate:

| Item | Price | In cash | A laborer's day (75 cash) buys | A craftsman's day (154 cash) buys |
|---|---|---|---|---|
| Persimmon | 8 釐 | ≈ 6.4 cash | ≈ 12 | ≈ 24 |
| 花紅 crabapple | 3 釐 | ≈ 2.4 cash | ≈ 31 | — |
| Yellow pear | 1分5釐 | ≈ 12 cash | ≈ 6 | — |
| Red pear / 棠梨 | 1分3釐 | ≈ 10.4 cash | ≈ 7 | — |
| 蘋果 apple | 3分 | ≈ 24 cash | ≈ 3 | — |

**C. Qing, Shengjing (Mukden) and Guangning orchards, tax-offset valuations.** Same work, 卷162, https://zh.wikisource.org/wiki/欽定大清㑹典則例_(四庫全書本)/卷162
- These value fruit delivered in place of tax; they are not purchase prices.
- Under the 康熙四十五年 (1706) entry: 「香水梨每箇一分」 (translation: "香水 pear, 0.01 tael each")
- Under 雍正七年 (1729): 「甜桃二十筐…〈舊例每筐二十箇價銀二錢〉」 (translation: "sweet peaches, 20 baskets … [old rule: each basket of 20 valued at 0.2 tael]")
- Gift rule for 康熙五十八年 (1719): 「蘋果柿子各二百梨三百」 (translation: "apples and persimmons 200 each, pears 300"). These are quantities, with no price.

**D. Ming, valuation table for stolen goods (計贓時估), in paper money (鈔).** 明會典 (Siku edition, i.e. the Zhengde edition) 卷136, https://zh.wikisource.org/wiki/明㑹典_(四庫全書本)/卷136
- Rule: 「凡計𧷢者皆㨿犯處當時物價」 (translation: "stolen goods are always valued at the price current where the crime occurred")
- Fruit: 「棗栗柿餅每一斤一貫…桃棃每一百箇二貫杏李林禽每一百箇一貫…柿子每三十箇一貫」 (translation: "jujubes, chestnuts, dried persimmons: 1 guan per jin … peaches and pears: 2 guan per 100 … apricots, plums, 林禽 [= 林檎, small apple]: 1 guan per 100 … persimmons: 1 guan per 30")
- Same table: 「稉糯米每一石二十五貫」「銀一兩八十貫」 (translation: "rice, 25 guan per shi"; "silver, 80 guan per tael")
- Undated: the list follows the 弘治十年 (1497) entry. I found no wage in the same currency. The Wanli Board of Works wages in Gao (0.03–0.07 tael a day, 1615) are in silver and a century later, so they don't compare. I give only ratios inside the table:

| Fruit | Pieces per shi of rice | Pieces per tael of silver |
|---|---|---|
| Persimmon | 750 | 2,400 |
| Pear | 1,250 | 4,000 |
| 林禽 small apple | 2,500 | 8,000 |

## 2. Reading

**ATTESTED ONLY FOR** a fresh persimmon in rural Kanto in the first half of the 19th century: 6 mon a piece, about 1/33 of a village carpenter's 200-mon day in 1818 Musashi. The figure comes from a secondary Bank of Japan teaching sheet that does not name its source document. The rest of the Japan question is **SILENT**: Edo city, castle towns, pears, wa-ringo/林檎 and dried persimmons.

The 1842 Edo price report (物価書上) has no fruit entries at all. It covers manufactured staples, which is one likely reason fruit prices are thin in the official record.

In China the evidence agrees across 1497–1764:
- Persimmons and pears are cheap goods, but not the cheapest.
- The native small apple is the cheapest fruit by count (花紅 at 3 釐; 林禽 at 1 guan per 100).
- The western-type 蘋果 cost ten times the 花紅 in the Qing court list. That gap is the closest evidence for where wa-ringo would sit.
- At Qing court prices a laborer's day bought about 12 persimmons or 31 crabapples.

**What I searched for Japan without result:**
- Search queries (about 14), including: 柿 一個 文 値段 水菓子, 守貞謾稿 水菓子売 柿 梨, 江戸時代 梨 値段, 和りんご 江戸時代 値段, 酒井伴四郎 日記 梨/西瓜 (twice), 鸚鵡籠中記 柿, 梨子代/柿代 日記, 天保 直段 書上 梨, 文久2年 麻疹 諸色 値段, 江戸の物価 一覧, and English queries.
- ja.wikisource phrase searches (水菓子 直段, 柿 直段 文, 梨 直段, 梨子 一つ 文, 林檎 文 江戸, and the 浮世の有様 volumes): no fruit price.
- Pages read that did not bear:
  - benricho 守貞謾稿 vendor page: no fruit prices.
  - benricho 守貞謾稿 index: lists 生柿 and 水菓子 but gives no text.
  - Handa 1842 price report: no fruit.
  - Ozu's 1839–40 Edo diary: only a gift of pears, no price.
  - Ōishi's 1842 物価書上 paper (Gakushuin): no fruit.
  - komonjyo.net: a list of foods, no prices.
  - coin-walk.site: no fruit.
  - Arcadia article on the 1862 measles diet: no prices.

I recorded outcomes for those pages. I left the four pages that bear (卷154, 卷162, 卷136, the BOJ PDF) unrecorded for you to cite. The Ōishi, Ozu and Handa PDFs were read from direct downloads, since `make source-pages` could not read them.

## 3. Leads not followed
- 酒井伴四郎日記 (Edo, 1860), itemized purchases: only the printed edition (影印と翻刻, Edo-Tokyo Museum 2010) and Aoki's 『幕末単身赴任 下級武士の食日記』; nothing quoted online.
- 小野武雄『江戸物価事典』 and 三井文庫「江戸日用品小売物価表」: likely sources for Edo fruit prices and the Mitsui Edo day-laborer wage; no copy online.
- 守貞謾稿 entries for 生柿 and 水菓子: exist in the NDL scans; no text online.
- 宛署雜記 (Wanping county, Beijing, 1593), expense lists: the wikisource page redirects to ctext res=545777, which I did not read.
- 會典則例 卷152, 盛京 tomb offerings of 蘋果, 梨, 柿, 420 each: quantities only, page not read.
- The full 1736 九卿议定物料价值: Gao's summary has no fruit rows.

Sources:
- [BOJ Currency Museum, 江戸時代の１両は今のいくら？](https://www.imes.boj.or.jp/cm/history/historyfaq/mod/1ryou.pdf)
- [欽定大清會典則例 卷154](https://zh.wikisource.org/wiki/欽定大清㑹典則例_(四庫全書本)/卷154)
- [欽定大清會典則例 卷162](https://zh.wikisource.org/wiki/欽定大清㑹典則例_(四庫全書本)/卷162)
- [明會典 卷136](https://zh.wikisource.org/wiki/明㑹典_(四庫全書本)/卷136)
- Archived: https://www.dpm.org.cn/Uploads/File/2023/02/10/u63e60647c73ae.pdf (`/diagram/.specify/source-archive/d7/d7234ae5c7ec/20261019T074210Z/text.txt`)
- Archived: https://www.town.miyashiro.lg.jp/cmsfiles/contents/0000002/2922/okayasukebunsyo.pdf (`/diagram/.specify/source-archive/53/539d0fda2d5b/20261002T162356Z/text.txt`)