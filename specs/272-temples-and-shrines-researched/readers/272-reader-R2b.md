# R2b: town/county-seat shrine precinct research (feature 272, 2026-09-27)

Baseline given: village (murashiro) shrine precinct 150-650 tsubo, mostly wood.
All quotes below fetched live (WebFetch, cross-checked with curl+pdftotext / regex verbatim search where noted). English translations are mine unless marked otherwise; originals kept as anchor per house doctrine.

---

## Q1. County-seat/market-town tutelary shrine (郷社/県社) vs village shrine (村社)

**Best source: the Meiji shrine-rank ordinance, quoted on ja.wikipedia.org/wiki/神社合祀** (fetched and VERIFIED verbatim by direct curl+regex against the live page, not just the model's extraction).

URL: https://ja.wikipedia.org/wiki/%E7%A5%9E%E7%A4%BE%E5%90%88%E7%A5%80
Section: 社格制度

Japanese (verbatim, from the article's quotation of the ordinance):

> 第一条　左項の一に当り、境内地六百坪以上にして、本殿、拝殿（但し同一建物にして本殿、拝殿を区画したるものを含む）、鳥居及社務所（社殿の構造、境内の風致等、其府県内の壮観にして最も有名なるもの）を具へ、現金五千円以上若くは之に相当する国債証書又は土地、及弐千戸以上の氏子を有する神社は府社若くは県社に列することを得。
> 第二条　左項の一に当り、境内地五百坪以上にして、……現金参千円以上若くは……、及千戸以上の氏子を有する神社は郷社に列することを得。
> 第三条　無格社にして境内地参百坪以上を有し、……現金弐千円以上若くは……、及弐百戸以上の氏子を有する神社は村社に列することを得。

English translation (mine, marked as translation):
"Article 1: A shrine that has a precinct of 600 tsubo or more, possesses a main hall, worship hall (including a single building housing both, partitioned), torii, and shrine office (its structure and precinct scenery being among the finest in the prefecture), cash holdings of 5,000 yen or more (or equivalent government bonds/land), and 2,000 or more parishioner households, may be ranked as a prefectural shrine (fu-sha/ken-sha).
Article 2: A shrine with a precinct of 500 tsubo or more, ... cash of 3,000 yen or more ..., and 1,000 or more parishioner households, may be ranked as a district shrine (gō-sha).
Article 3: An un-ranked shrine with a precinct of 300 tsubo or more, ... cash of 2,000 yen or more ..., and 200 or more parishioner households, may be ranked as a village shrine (mura-sha)."

**This is the load-bearing number for Q1**: village-shrine floor is 300 tsubo (matches our 150-650 tsubo band as the working range around/above that statutory floor); a market town's own tutelary shrine (郷社) had to clear a 500-tsubo floor - roughly 1.7x the village floor; a full county-seat/provincial-town shrine of 県社/府社 rank had to clear 600 tsubo, plus a torii, shrine office and (usually) a distinctly grander 本殿+拝殿 complex, and double the parishioner-household count of a 郷社. These are statutory *floors*, not averages - the actual precinct of a given town shrine likely runs well above the floor (by the same logic our village shrines run above their 300-tsubo floor).

**Concrete village-shrine comparison example**, Kokubunji's Hachiman Shrine (村社 rank), from Tokyo Metropolitan Archives' explainer on how to read a 神社明細帳:
URL: https://www.soumu.metro.tokyo.lg.jp/01soumu-archives/07edo_tokyo/0703kaidoku/0703kaidoku_03/0703kaidoku_03_2
- Rank: "社格は「村社」"; "辛未（明治4年）10月に村社に列せられた" (designated village shrine, Meiji 4/Oct = 1871)
- Precinct: "境内坪数...513坪（約1700m2）" (513 tsubo, ~1,700 m2) - sits comfortably inside our 150-650 band, confirming the band against a primary-record transcription.
- Main hall: "間口が2間3尺（約4.5m）、奥行が4間（約7.2m）" (frontage 2 ken 3 shaku [~4.5 m], depth 4 ken [~7.2 m])

I could not find a Wikipedia/municipal page for a specific 郷社- or 県社-ranked town shrine that states BOTH its actual precinct tsubo AND its 本殿/拝殿 ken dimensions (checked 品川神社 and 千住神社, both ex-郷社 and both post-town tutelary shrines - see below; neither article gives measurements). The statutory floors above are the only hard, sourced comparison figures obtained in the time available.

**Checked but no usable numbers**:
- 品川神社 (ex-郷社, Tokaiji's/Shinagawa-juku's shrine) - https://ja.wikipedia.org/wiki/品川神社 - no precinct tsubo, no building ken given in the article.
- 千住神社 (ex-郷社, "区内唯一の郷社と定められる" 1874, tutelary of Senju-juku) - https://ja.wikipedia.org/wiki/千住神社 - no precinct tsubo, no building ken given.
- 郷見神社 (a 村社, not 郷社 despite the name) - https://ja.wikipedia.org/wiki/郷見神社 - "境内面積 251坪"; "社殿は、間口二間、奥行三間" - useful only as another village-tier data point (251 tsubo, main hall 2 ken x 3 ken), not a town-tier one.

---

## Q2. Did a castle town / provincial city keep a principal shrine, how big, where

**Primary source, fetched as PDF and run through pdftotext (verbatim, plain-text extraction, not a model summary):**
篠田明恵・福井恒明・中井祐・篠原修「江戸城下町における神社の配置とその傾向」土木史研究論文集 Vol.23 (2004)
URL: https://www.jstage.jst.go.jp/article/journalhs2004/23/0/23_0_157/_pdf

This is exactly the case the questions ask about: Edo's own castle-town tutelary shrine, Sannō-sha (山王社, now Hie Jinja).

Verbatim (OCR'd Japanese, spacing artifacts of the PDF extraction left as-is):

> 山王 社 は江 戸 の 惣 鎮 守 で あ り、 江 戸 の神 社 の最 高 峰 と い っ て も過 言 で は な い 。

Translation: "Sannō-sha was Edo's grand tutelary shrine (sōchinju) - it is no exaggeration to call it the pinnacle of Edo's shrines."

History of its siting (verbatim, translated):
> 戸 郷 の守 護 神 と して 江 戸 館 に 祀 って い た も の を、 文 明 十 年 (1478) 太 田 道 灌 が 江 戸 城 築 城 に 際 し、 江 戸 居 館 跡 地 (山 上) に 鎮 護 の 神 と して 勧 請 した

"It had been enshrined at the Edo residence as guardian deity of Edo district; in Bunmei 10 (1478), when Ota Dokan built Edo Castle, he invoked it as a protective deity at the site of the former Edo residence, ON A HILLTOP (山上)."
- 1590: moved from Umebayashi-zaka inside the castle to Momijiyama (still inside the castle) when Tokugawa Ieyasu arrived.
- 1607: moved outside the castle, to Kōjimachi Hayabusa-chō (outside Hanzō-mon), for the honmaru works.
- After the Meireki fire, 1659: moved to Nagata-chō Hoshigaoka, on rising ground above the former Tameike pond.

The paper explicitly notes the pattern held even for the grand tutelary shrine itself:
> そ の 神 社 で も江 戸 城 整 備 に 当 た り、 外 側 へ と移 転 させ られ た が 、 移 転 地 の 立 地 条 件 は 前 の 立 地 と同 様 に小 高 い 場 所 が 確 保 され て い る様 子 が 分 か る。

"Even this shrine was moved outward as Edo Castle was developed, but at each relocation a slightly elevated site (小高い場所) was secured, just as at the previous site."

General siting-pattern findings for Edo's ~110 shrines overall (verbatim):
> 神 社 の 立 地 は 台 地 上 、そ の 中 で も台 地 端 、 山 上 な どの 崖 上 の よ う な 場 所 か ら、 平 地 へ の 立 地 へ と傾 向 が 変 わ っ て き た

"Shrine siting shifted over time from highland sites - plateau tops, and especially plateau edges and hilltop/cliff-edge sites - toward flat-land siting." Early on (pre-Ota Dokan, through the castle-town-expansion period) 5-6/10 of newly founded shrines sat on plateau/hill high ground, 2-3/10 on flat land; only in the "settled castle-town" period (1688-1865) did flat-land siting (especially "町中や裏 通り沿い" - amid the town, along back streets) become dominant.

**Answer to Q2**: Yes - a castle town's principal shrine (Edo's case: Sannō-sha, its 総鎮守/sōchinju) was kept, and its siting rule was NOT "inside the castle forever" but "on rising/elevated ground, moved outward step by step as the castle was built up" - starting on a hilltop inside the pre-Edo-castle compound, staying on high ground through two more moves, ending on a low hill (Hoshigaoka - literally "star hill") outside the castle at the town's edge. This directly supports treating a settlement's principal shrine as belonging on a hill/high point near but outside the fortified core, consistent with the "on a hill" option in the question.

Comparison case at the county/provincial level, Bicchu-no-kuni Sōja-gū (備中国総社宮), the shrine that gave 総社市 (Soja City, Okayama) its name:
URL: https://ja.wikipedia.org/wiki/備中国総社宮
- Role: "国司は各国内の全ての神社を一宮から順に巡拝していた。これを効率化するため、各国の国府近くに国内の神を合祀した総社を設け" - "the provincial governor used to make pilgrimage rounds to every shrine in the province starting from the ichi-no-miya; to make this efficient, a sōsha enshrining all the province's deities together was established near the provincial capital (kokufu)."
- Location: "岡山県南部、総社市の中心部に鎮座する" - "enshrined in the center of present Soja City, in southern Okayama Prefecture" - i.e., a sōsha sits near the provincial administrative seat, not inside a castle.
- Town formed around it: "周辺は門前町・宿場町として発展し" - "the surrounding area developed as its monzen-machi (shrine-gate town) and post-station town."
No precinct-area figure (坪/m²) was found on this page.

---

## Q3. China: county-seat and prefectural-city 城隍庙 (City God Temple)

Three fetched, all verified with area + layout numbers:

### 三原城隍庙 (Sanyuan City God Temple), Sanyuan COUNTY, Shaanxi
URL: https://zh.wikipedia.org/zh-hans/三原城隍庙 (fetched via WebFetch only; NOT independently curl-verified this session - Licheng, below, was the one spot-checked by direct curl+regex)
- Area: "占地13390平方米" - 13,390 m2 (about 2.01 mu / roughly 3.3 acres)
- Layout (verbatim): "其中轴线纵贯分布有三道门、四重牌坊、五座楼阁、六个院落" - "along its central axis run three gates, four memorial archways (paifang), five pavilions/towers, and six courtyards."
- Fuller building list (verbatim): "现存建筑群由南向北依次为照壁、木牌坊、山门、东西廊房、木牌坊、东西廊房、石牌坊、戏楼、东西庑、钟楼和鼓楼、木牌坊、东西陪殿、月台、大殿、明禋亭和寝宫" - "from south to north: spirit-wall, wooden paifang, mountain gate, east/west corridor-rooms, wooden paifang, east/west corridor-rooms, stone paifang, opera stage (戏楼), east/west side-halls, bell tower and drum tower, wooden paifang, east/west side-shrines, moon terrace, main hall, Mingyin pavilion, and sleeping/rear hall (寝宫)."
- Location: "三原县城关街道东渠岸街中段" - mid-section of East Canal Bank Street, Chengguan (county-seat) subdistrict, Sanyuan.
- Current use: "三原县博物馆所在地" - now houses the Sanyuan County Museum.
- Status: listed 2001, 5th batch national-level 文物保护单位.

### 黎城城隍庙 (Licheng City God Temple), Licheng COUNTY, Shanxi - VERIFIED verbatim by direct curl+regex
URL: https://zh.wikipedia.org/zh-hans/黎城城隍庙
- Area: "占地面积1892平方米" - 1,892 m2 (a single-courtyard county-level temple, far smaller than Sanyuan's multi-courtyard one)
- Layout: "一进院落布局，东西36.23米、南北52.65米" - "single-courtyard layout, 36.23 m east-west by 52.65 m north-south"; "中轴线上由南至北依次遗有山门、正殿，山门两侧遗存有掖门" - "surviving on the central axis, south to north: mountain gate, main hall; flanking side-doors survive beside the mountain gate."
- History: founded Northern Song Tianshu era (1023-1031); burned in Yuan Zhizheng wars (1341-1368); rebuilt Ming Hongwu 2 (1369); repaired 1537, 1701, 1911. "现山门为明代遗构，正殿为清代遗构" - surviving gate is Ming-era fabric, main hall Qing-era.
- Location: inside the county seat, "黎侯镇城内村河下东街95号" (a street address within the walled town, not tied to the yamen in the text found).

### 彰德府城隍庙 (Zhangde Prefecture City God Temple), Anyang, Henan - a PREFECTURAL-city example
URL: https://zh.wikipedia.org/zh-hans/彰德府城隍庙
- Area: "占地面积6773平方米，建筑面积2792平方米" - 6,773 m2 total footprint, 2,792 m2 built floor area (a prefectural temple sitting between the county-seat Licheng example and the larger Sanyuan example in scale - consistent with rank correlating with size, though Sanyuan is nominally only a county seat, so scale is not purely rank-determined).
- History: traditionally founded early Jin dynasty; rebuilt Ming Hongwu 2 (1369) and Jingtai 5 (1454); restored 1982 by Anyang municipal government, now Anyang Folk Art Museum.
- Location: "河南省安阳市文峰区鼓楼东街6号" - No. 6 Drum Tower East Street, Anyang - i.e., sited by the city's drum tower (a traditional yamen-district landmark), consistent with the expected "near the yamen/administrative core" siting, though the article does not spell out the yamen relationship explicitly.
- The WebFetch pass could not find explicit 几进/layout-gate-stage-hall enumeration for this one; only Sanyuan and Licheng yielded full layout lists.

**Role** (general, drawn from all three pages plus background knowledge of 城隍 worship, flagged as NOT independently quoted for role/function specifically - see gap below): the city god (城隍) was the walled settlement's own tutelary/guardian deity for the living administrative jurisdiction, paired with the magistrate's authority; the temple was a civic-religious building, typically with a public opera stage for annual processions, distinguishing it functionally from a village earth-god shrine.

**Not obtained in time**: an explicit statement, quoted verbatim from a public page, of the city-god temple's siting RULE relative to the yamen (e.g., "always built facing/beside the yamen"). The three pages give street addresses but none states the yamen relationship in so many words. This should be treated as an open sub-question, not answered by guess.

---

## Q4. Small city shrines in a townsmen's ward (Edo Inari, hokora, ward shrines)

**Blocked on primary numeric sources (see blocked list). What was recovered:**

The saying itself, widely attested but I could not fetch a public page that quotes it with a primary-source citation and a real Inari-count number attached (see blocked list - the dedicated book by 仁科邦男 is not on an open web page). WebSearch summary (NOT independently verbatim-fetched, flagged as such) renders the saying as "江戸に多いもの、伊勢屋稲荷に犬の糞" ("What Edo has a lot of: Iseya [shops], Inari shrines, and dog droppings") - cited across several secondary pages (Tokyo Shimbun, note.com, rakugo-fan blogs) as reflecting Edo's genuinely dense population of small Inari shrines, one per block/ward being unremarkable. None of these were fetched verbatim in time; treat this section as UNCONFIRMED pending a direct fetch.

I was unable to retrieve usable body text from either adeac.jp archive page attempted (Minato City's 【江戸の稲荷】, Tama City's 【屋敷稲荷】) - both returned only navigation/metadata to WebFetch, not the article body (see blocked list; adeac uses a JS-driven text viewer that WebFetch cannot penetrate). The Edogawa Ward PDF (2-11.pdf) and a second PDF from the same city domain both downloaded but as corrupted/non-extractable text via WebFetch; I did not have time in this session to retry them with pdftotext as I did successfully for the jstage PDF (see next-step note below - this is a promising retry, not a dead end).

**No verbatim quotes obtained for Q4.** This question should be treated as OPEN / needs a follow-up pass, ideally: (a) pdftotext retry on the Edogawa and Edogawa-adjacent PDFs already downloaded to this scratchpad (jypyy1... and y9kx4t... paths logged by WebFetch, though those were tool-cache paths, not scratchpad - re-download and pdftotext directly), (b) a source-reader dispatch aimed specifically at adeac.jp's rendered text via a headless-browser-capable tool rather than WebFetch, (c) direct search for 仁科邦男『伊勢屋稲荷に犬の糞』 reviews/excerpts that quote actual shrine-count figures for named Edo wards.

---

## Blocked sources (URL, title/author/year, why it matters)

1. **江戸川区 解説シート No.2-11「区内の稲荷神社」** (Edogawa Ward educational PDF, ward local-history series, n.d., updated 2014-10-21) - https://www.city.edogawa.tokyo.jp/documents/9202/2-11.pdf - WebFetch received the PDF but could not extract readable text (reported as corrupted/binary by the fetch-and-summarize model, unlike the jstage PDF which pdftotext handled cleanly - this one likely needs the same direct pdftotext treatment, not yet retried). Matters directly for Q4 (per-ward Inari shrine counts).

2. **Minato City Digital Archive, 【江戸の稲荷】** ("Inari of Edo"), adeac.jp local-history text series - https://adeac.jp/minato-city/text-list/d110021/ht002380 - WebFetch returned only page chrome/navigation, no article body; adeac serves its text through a JS viewer WebFetch cannot render. Matters directly for Q4 (ward-level counts, siting, sayings).

3. **Tama City Library Digital Archive, 【屋敷稲荷】** ("Yashiki Inari") - https://adeac.jp/lib-city-tama/text-list/d100030/ht060690 - same adeac JS-viewer problem as #2. Matters for Q4 (yashiki-gami counts per household, referenced elsewhere as "566件" in Musashi-Fuchu but not independently verified from this page or any other in this session).

4. **Second Edogawa-domain PDF fetched via WebFetch** (same failure mode as #1; URL not separately recorded because it was fetched as part of the same batch call and only the cache path was returned) - matters for Q4, same reason as #1.

5. **仁科邦男『伊勢屋稲荷に犬の糞: 江戸の町は犬だらけ』(草思社, 2016)** - the monograph most likely to carry an actual per-ward Inari count or density figure behind the proverb; it is a commercial book (Amazon/Kinokuniya/HMV listing pages only, no open full text) - https://www.amazon.co.jp/dp/479422222X - not fetchable as a public page; would need the GM's TO-DOWNLOAD.md route if judged worth pursuing.

6. **彰德府城隍庙's internal layout enumeration** - not a blocked URL per se, but the fetched zh.wikipedia article (https://zh.wikipedia.org/zh-hans/彰德府城隍庙) does not contain a 几进/gate-stage-hall breakdown the way the Sanyuan and Licheng articles do; a Baidu Baike article on the same temple might carry more architectural detail but was not attempted this session.

7. **A named 郷社/県社-rank town shrine with BOTH precinct tsubo AND 本殿/拝殿 ken given together** - no blocked URL (nothing 403'd), simply not found within the search budget; 品川神社 and 千住神社 Wikipedia articles were checked and confirmed to lack these figures. A 神社明細帳 transcription site (e.g. a prefectural archive scan, per the "収蔵公文書／千葉県" and "神奈川県神社明細帳断簡" hits) would likely have it but requires a follow-up pass through primary-document viewers, which are often JS-gated like adeac.
