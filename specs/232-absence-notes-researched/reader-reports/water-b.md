# Reader report: batch `water-b-moats-ponds-and-flow` (19 notes)

Read 2026-09-12. Every fetch below was made from this container with `curl` using a desktop
browser user agent, or with the WebFetch tool; PDFs were converted with `pdftotext -layout` and
read as text. Where a publisher refused an automated fetcher I also asked Unpaywall, OpenAlex,
DOAJ, Semantic Scholar, HathiTrust and Open Library whether an open copy exists, and followed
repository copies where they did. Quotations reproduce the source's own characters, spellings and
dashes. Japanese and Chinese passages are given in English translation (translated by this
reader), with the original after the translation as the checker's anchor.

**How searching was done, and what that costs this report.** This session's WebSearch budget (200
calls, session-wide across all readers) ran out partway through this batch. Every note below has
had a search pass - none is marked absent for want of one - but the later notes were searched
through `curl` against search endpoints and scholarly APIs rather than through WebSearch, and the
query text is recorded either way. What works from this container: **search.yahoo.co.jp** fetched
with a browser user agent (real organic results, in English, Japanese and Chinese - this is the
one general search engine that answers), Crossref, OpenAlex, Unpaywall, Semantic Scholar, Europe
PMC (which searches FULL TEXT, not just abstracts), NCBI E-utilities over PMC, the MediaWiki API
on any Wikipedia, the J-STAGE search API, Open Library and the Internet Archive advanced search.
What does not: DuckDuckGo (HTTP 202 CAPTCHA on both `html.` and `lite.` endpoints), Bing (a shell
with no organic results in the HTML), Mojeek (a challenge page), and the Google Books API (empty
body).

## Verdicts at a glance

| Page / note | Claim in one line | Verdict |
|---|---|---|
| `archetypes.html` fn-81 | Pearl delta as "mosaic-like ... boundary blurred" | **FOR THE GM** |
| `archetypes.html` fn-82 | ponds grew while dikes shrank; ~20 m to under 4 m | **CITED** (different period and one village) |
| `archetypes.html` fn-84 | Ruddle & Zhong monograph has no publicly readable copy | **STILL ABSENT** (the absence holds) |
| `cities/fabric.html` fn-25 | a wagon train brings many dozens of draft animals | **STILL ABSENT** |
| `cities/fabric.html` fn-30 | jin'ya-town fire posture: bell, patrols, stored water, kura | **STILL ABSENT** for the posture; the "one of more than fifty still standing" half is now **CITED** |
| `cities/hinterland.html` fn-6 | ground below the drain is wettest and nobody builds there | **CITED** (the principle, from alluvial geomorphology) |
| `cities/hinterland.html` fn-9 | in-wall vegetable tracts, wells and night soil | **CITED** (two sources, one per half) |
| `fields.html` fn-84 | a contour drain meeting the stream at a right angle is ordinary side drainage | **CITED** (geometry yes, "valley stream" not in the source) |
| `towns.html` fn-22 | two-story caravan inn, stable beside it, standing yard | **CITED** for stable and yard; **CONTRADICTED** on the second story |
| `urban-features.html` fn-68 | north China, 400-800 mm, concentrated in the summer monsoon | **CITED** |
| `urban-features.html` fn-69 | the jiegao and the lulu | **CITED** |
| `urban-features.html` fn-73 | kabu-ido regulated well numbers, run by residents | **CITED** |
| `vegetation.html` fn-4 | no readable Chinese source measures a water-mouth grove | **STILL ABSENT** (the absence holds) |
| `vegetation.html` fn-6 | no readable source counts a Chinese grove's trees | **STILL ABSENT** (the absence holds) |
| `vegetation.html` fn-22 | Kushiro Mire: reed invaded by alder where it dries | **CITED** (second half of the sentence not supported; see below) |
| `vegetation.html` fn-23 | Otanoshike: reed swamp, Carex marsh, Calamagrostis grassland with Spiraea | **FOR THE GM** (a true paywall) |
| `vegetation.html` fn-89 | Izumo tsuijimatsu enclosed the whole house before Meiji | **CITED** |
| `water.html` fn-71 | a draw-well wants a water table under dry ground | **CITED** (modern well-construction guidance) |
| `ways.html` fn-1 | a timber bridge lands 5-15 ft of deck past the water | **STILL ABSENT** |

---

## `archetypes.html` fn-81

**Claim**: the Pearl-delta "mosaic-like ... boundary blurred" description.

### Verdict: FOR THE GM

The sentence the record paraphrases is the opening of the abstract of a specific, free-to-read
article, and this container cannot reach the publisher's host at all.

**The document**

- Title: *Seeing from Above: Observation of Contemporary Dike-Pond Landscape*
- Author: Tian, M. (Meng Tian)
- Year: 2019. Journal: *Landscape Architecture Frontiers*, 7(4), pp. 130-138
- Publisher: Higher Education Press
- DOI: 10.15302/J-LAF-1-050004
- Open-access status: Semantic Scholar reports `"status": "BRONZE"` - free to read at the
  publisher, no license stated. So a person with an ordinary browser should be able to open it.

**URLs tried, and what blocked me**

| URL | Result |
|---|---|
| `https://journal.hep.com.cn/laf/EN/10.15302/J-LAF-1-050004` | curl, default TLS: exit 35, SSL connect error, 0 bytes |
| same, `curl --tlsv1.2 --ciphers DEFAULT@SECLEVEL=1` | exit 35 again, 0 bytes |
| `https://doi.org/10.15302/J-LAF-1-050004` | 301 to the above host, then 0 bytes |
| same landing page via WebFetch | `Socket is closed` |
| `https://journal.hep.com.cn/laf/EN/article/downloadArticleFile.do?attachType=PDF&id=25614` (the PDF link Semantic Scholar gives) | curl: exit 28, timed out at 25 s, 0 bytes |
| `https://scispace.com/pdf/seeing-from-above-observation-of-contemporary-dike-pond-4bmqnwf39t.pdf` (third-party mirror) | HTTP 202, 0 bytes |

This is a network-level failure to `journal.hep.com.cn`, not an HTTP refusal, so none of the three
recovery routes applies: there is no Unpaywall/OpenAlex repository copy (OpenAlex lists only the
DOI location), and the one mirror serves nothing.

**What it would settle.** OpenAlex's record of the article's own abstract - a metadata
aggregator, which is a POINTER and not a read of the source - carries the sentence:

> A dike-pond landscape is characterized by asymbiotic and interacted relationship between water
> and land and considered an integration of human settlements with an aquacultureagriculture
> system. The Pearl River Delta has historically enjoyed a rich river network and been shaped by
> the mosaic-like constructed ponds with the meandering natural river systems, where the boundary
> of the constructed and the natural blurred and a resilient dike-pond landscape prevailed.

Two things follow if the GM can open the page. First, the description stops being a GUESS. Second,
**the record's current quotation does not match the source's wording**: the record has
"mosaic-like constructed ponds with meandering natural river systems, [with] the boundary between
constructed and natural blurred", where the article has "the mosaic-like constructed ponds with
the meandering natural river systems, where the boundary of the constructed and the natural
blurred". The quotation would need correcting whichever way this goes.

The same abstract also names "the shrinking dike surfaces and imbalanced ratio of dike to pond" as
one of its three findings, which bears on fn-82.

---

## `archetypes.html` fn-82

**Claim**: ponds grew at the dikes' expense (the record frames it 1967-2016), and the ~20 m to
under 4 m magnitude.

### Verdict: CITED - with a scope caveat the record must carry

**Source read**: Chi, W., Plieninger, T., Lin, G., & Chowdhury, K. (2024). *Governing Landscape
Simplification in Rapid Commercialization Contexts - the Case of the Dike-Pond System in the Pearl
River Delta, China*. International Journal of the Commons, 18(1), pp. 260-275.
DOI: https://doi.org/10.5334/ijc.1300

- Landing page (public): https://thecommonsjournal.org/articles/10.5334/ijc.1300
- PDF I read (public, HTTP 200, 2.1 MB): https://thecommonsjournal.org/articles/1300/files/66151cd3a6d55.pdf

**Passage, verbatim**:

> During the commercialization process, croplands that were integrated with fish farming were
> gradually transformed into ponds in pursuit of higher income. At the same time, the water bodies
> expanded and arable dikes, which used to be 20 meters wide, were eroded to less than 4 meters.

and, on the mechanism:

> For instance, farmers cultivate fish, which narrows the dike's width—an outcome of biophysical
> conditions.

**How it supports the claim.** It gives, in one sentence, both halves the record calls unsourced:
ponds expanding at the dikes' expense, and the 20 m to under 4 m magnitude. The mechanism sentence
says why - fish cultivation eats the dike.

**What it does NOT support, and must be said if it is used.** The period is wrong for the record's
present wording. The paper's frame is "following the reform and opening-up" (i.e. post-1978 to the
present), not 1967-2016, and the case is one village - Ruxi, in Shunde - not the delta at large.
The paper's preceding sentences set that scene: "According to Zhong (1987), only 52.4% of the
agricultural land at the town level, where Ruxi village is located, corresponded to pond
landscapes at that time."

The 1967-2016 framing comes from Liu & Li, *Tracking dike-pond landscape dynamics in a core region
of the Guangdong-Hong Kong-Macao Greater Bay Area based on topographic maps and remote sensing
data during 1949-2020*, Aquaculture (2021), DOI 10.1016/j.aquaculture.2021.737741. I checked its
access: Unpaywall returns `is_oa: false`, `oa_status: closed`, and an empty `oa_locations` array;
OpenAlex holds no abstract for it and Semantic Scholar's `abstract` is null. There is no open copy
to find. So the honest repair is to cite the IJC paper for the magnitude and the direction, and
drop or attribute the 1967-2016 date range separately.

---

## `archetypes.html` fn-84

**Claim**: "the monograph itself has no publicly readable copy" - Ruddle, K. & Zhong, G. (1988),
*Integrated Agriculture-Aquaculture in South China: The Dike-Pond System of the Zhujiang Delta*,
Cambridge University Press.

### Verdict: STILL ABSENT - the record's own absence statement holds

**Searches run (query text verbatim)**

1. WebSearch: `Ruddle Zhong "Integrated agriculture-aquaculture in south China" dike-pond system Zhujiang Delta full text archive`
2. Open Library search API: `https://openlibrary.org/search.json?q=Integrated+Agriculture-Aquaculture+in+South+China+dike-pond&limit=3`
3. Internet Archive advanced search: `https://archive.org/advancedsearch.php?q=title:("dike-pond") OR title:("dike pond")&rows=8&output=json`
4. Internet Archive advanced search: `q=title:(dike pond Zhujiang)`
5. HathiTrust volumes API by ISBN: `https://catalog.hathitrust.org/api/volumes/brief/json/isbn:0521341930`
6. Google Books API: `q="dike-pond" Zhujiang Ruddle`

**Candidates returned, and what happened to each**

| Candidate | URL | Outcome |
|---|---|---|
| Cambridge University Press catalog page | https://www.cambridge.org/us/academic/subjects/life-sciences/natural-resource-management-agriculture-horticulture-and/integrated-agriculture-aquaculture-south-china-dike-pond-system-zhujiang-delta | Not fetched: a publisher catalog page for an out-of-print book carries no text of the monograph. |
| *Experimental Agriculture* review of the book, Cambridge Core | https://www.cambridge.org/core/journals/experimental-agriculture/article/abs/integrated-agricultureaquaculture-in-south-china-the-dike-pond-system-of-the-zhujang-delta-.../234A53413CB0B9E5D4A1DD6FCFEC5D92 | Not fetched: an abstract of a REVIEW, not the monograph, and Cambridge Core's abstract pages would not carry Ruddle & Zhong's pond and dike figures. |
| Amazon / AbeBooks listings | (sales pages) | Not fetched: listings, no text. |
| academia.edu upload | https://www.academia.edu/56156603/... | Not fetched: the title shows it is the same one-page journal REVIEW, not the book, and academia.edu requires a login to download. |
| ResearchGate entry | https://www.researchgate.net/publication/258212339_... | Not fetched: ResearchGate refuses automated fetchers and its "full-text" entries for monographs are routinely request-only; the project has recorded it as unreadable before. |
| Open Library record | (from the API) | Returned `"ia": None, "ebook_access": "no_ebook"` - Internet Archive holds no scan, borrowable or otherwise. |
| Internet Archive | - | `numFound: 0` on both queries. |
| HathiTrust | - | `{"isbn:0521341930":{"records":[],"items":[]}}` - not digitized. |

The related Zhong Gongfu article that carries some of the same figures, *The mulberry dike-fish
pond complex: A Chinese ecosystem of land-water interaction on the Pearl River Delta*, Human
Ecology, DOI 10.1007/BF01531240, is also closed: Unpaywall returns `is_oa: false`,
`oa_status: closed`, no OA locations.

So the record is right: the pond sizes (0.4-0.6 ha) and dike widths (6-10 m) can be cited only at
one remove, through the ISIS dyke-pond page that already carries them.

---

## `cities/fabric.html` fn-25

**Claim**: a wagon train arriving at or passing through a city brings many dozens of draft animals
- oxen and packhorses - with their guards, porters and drivers.

### Verdict: STILL ABSENT

**Searches run (query text verbatim)**

1. WebSearch: `大车店 车马店 客栈 马厩 院子 骡马 旅店 历史 北方 商队`
2. WebSearch: `Chinese walled city agricultural land inside walls vegetable gardens market gardening enclosed area Ming Qing city wall farmland` (swept up caravan and gate traffic material)
3. Google Books API: `caravan inn stable courtyard China mules carts inn yard travellers` (the API returned no items at all from this container)
4. Yahoo Japan: `隊商 荷駄 牛馬 数十頭 宿場 城下町 到着`

**Candidates, and what happened to each**

| Candidate | URL | Outcome |
|---|---|---|
| 维基百科 「大车店」 | https://zh.wikipedia.org/zh-hans/大车店 | FETCHED and read in full. It describes the inn type, its 40-li spacing, its sign, its sleeping platforms and its clientele. It gives no count of animals in any single train, and no count of animals at an inn. |
| 吉林日报, 王爽, 「消失的大车店」, 2026-04-25 | http://jlrbszb.dajilin.com/pad/paper/c/202604/25/content_1049361.html | FETCHED and read in full. Describes the yard, the well, the long stable and the feeding trough in detail (quoted under `towns.html` fn-22 below), but counts no animals and describes no arriving train. |
| 中国社会科学网, 「丝绸之路上的商队与商队旅馆」 | http://hrczh.cass.cn/lszg/lszg_wscl/202308/t20230830_5682469.shtml | Not fetched: a Silk Road caravanserai piece; the setting here is a domestic wagon route into a provincial city, not a long-distance desert caravan, so its numbers - if it carries any - would be about a different object. Worth a look by someone with a search budget left. |
| 163.com / 知乎 reposts of 大车店 material | https://m.163.com/dy/article/G0CMNJRU0543UEWY.html ; https://zhuanlan.zhihu.com/p/129763610 | Not fetched: content-farm reposts of the newspaper material above; a re-post is not a source. |
| 维基百科 「商队驿站」 | https://zh.wikipedia.org/zh-hans/商隊驛站 | Not fetched: it is the caravanserai article (Near East and Central Asia), the wrong institution for a Chinese or Japanese provincial city. |

| 『福井県史』通史編3 近世一, 第四章第三節 「江戸幕府の宿駅制度」 | https://www.library-archives.pref.fukui.lg.jp/fukui/07/kenshi/T3/T3-4-01-03-01-01.htm | FETCHED and read. The best readable anchor found for animals at scale on a road - see below. |
| 関東地方整備局, 「宿駅伝馬制度って、なんのこと？」 | https://www.ktr.mlit.go.jp/yokohama/tokaido/02_tokaido/04_qa/index1/a0105.htm | Not fetched: a ministry FAQ page covering the same institution the Fukui prefectural history states in full and with better provenance. |
| ADEAC 「助郷出入」 (Nagara town archive) | https://adeac.jp/nagara-town/text-list/d100010/ht041220 | Not fetched: a transcribed local document about a sukego dispute - about the corvée obligation, not about a merchant train's animals. |

Nothing read gives a number of draft animals per wagon train, at a city gate or anywhere else.
The claim stays general reading.

**The nearest readable anchor, offered as a substitute rather than as support.** If what the
record wants is "a trunk-road settlement had to absorb draft animals by the dozen", the Japanese
post-station standing requirement is a documented number, from a prefectural history. 『福井県史』
通史編3 近世一 (*History of Fukui Prefecture*, narrative volume 3, Early Modern I), published by
the prefecture and readable at the address above; translated from the Japanese by this reader:

> From the Kan'ei period onward, the Tokaido was required to keep 100 men and 100 horses per day
> on hand, the Nakasendo 50 men and 50 horses, and the other highways 25 men and 25 horses. Any
> amount in excess of that number was met by paying the ordinary fare, or was laid on the
> assisting man-and-horse villages or the sukego.

Original: 「寛永期以降には、一日に東海道は一〇〇人・一〇〇匹、中山道は五〇人・五〇匹、他の街道は二五人・二五匹を常備することとされた。その数を超過する分は通常の賃銭を払ったり、助人馬村または助郷などに負担させたりした。」

That is the STATION'S standing obligation, not one train's animals, and it is the Japanese post
system rather than a Chinese wagon route - so it cannot be used for the record's sentence as
written. It does establish that a settlement on a trunk road kept animals in the hundred range,
which is the order of magnitude the record's "many dozens" is reaching for, and it is quotable.

---

## `cities/fabric.html` fn-30

**Claim** (reading the note as the second `[HERE]`, the one the previous pass's own note is about):
the jin'ya / daikansho town's fire posture - a hansho bell on a ladder, a rooftop platform or a
simple frame at the office or the watch post, the temple bell doubling as the alarm elsewhere,
night patrols with clappers, stored water, and the plastered fireproof kura around the tax rice.

### Verdict: STILL ABSENT for the posture as stated

What I did find is the same posture described for an ordinary Edo-period TOWN rather than for a
jin'ya or its town, which is close but is not the assertion.

**Searches run (query text verbatim)**

1. WebSearch: `陣屋 代官所 火災 対策 半鐘 火の見 土蔵 年貢米 夜回り 拍子木`
2. MediaWiki API, ja.wikipedia, extracts for `高山陣屋`, `火の見櫓`, `半鐘`, `旅籠`
3. MediaWiki API search, ja.wikipedia: `srsearch=高山陣屋`
4. Yahoo Japan: `陣屋 代官所 火災 対策 半鐘 火の見 土蔵 年貢米 夜回り 拍子木`
5. Yahoo Japan: `代官所 陣屋 火の用心 夜回り 拍子木 半鐘 防火 江戸時代`
6. Yahoo Japan: `陣屋 郡代 代官所 火災 焼失 御蔵 防火 用水桶 火の見`

**Candidates, and what happened to each**

| Candidate | URL | Outcome |
|---|---|---|
| ja.wikipedia 「火の見櫓」 | https://ja.wikipedia.org/wiki/火の見櫓 | FETCHED and read. Carries the watch-post arrangement, for towns generally - quoted below. |
| ja.wikipedia 「半鐘」 | https://ja.wikipedia.org/wiki/半鐘 | FETCHED and read. Carries the bell on the tower and the coded strikes - quoted below. |
| ja.wikipedia 「高山陣屋」 | https://ja.wikipedia.org/wiki/高山陣屋 | FETCHED and read. Carries the survival and the storehouse - quoted below. Says nothing about fire, a bell, patrols, stored water or a pond. |
| 内閣府 防災情報, 1657 明暦の大火 報告書 第3章 | https://www.bousai.go.jp/kyoiku/kyokun/kyoukunnokeishou/rep/1657_meireki_edotaika/pdf/1657-meireki-edoTAIKA_05_chap3.pdf | Not fetched: it is the Cabinet Office's report on the improvement of fire defenses in EDO after 1657 - the shogunal capital, expressly the case the record's own reasoning treats as the opposite end of the spread from a country seat. A serious source, but for the wrong settlement. |
| kotobank 「陣屋」 | https://kotobank.jp/word/陣屋-82659 | Not fetched: a dictionary aggregation of definitions of the institution; nothing in the search listing suggested fire practice. |
| worldfolksong.com, 「火の用心 夜回り 掛け声」 | https://www.worldfolksong.com/calendar/japan/hinoyojin.html | Not fetched: a hobbyist song-lyrics site, below the bar for a source. |

**What the readable pages DO say** (offered so the record can use it where it fits, not as support
for the jin'ya claim):

From ja.wikipedia 「火の見櫓」, translated from the Japanese by this reader:

> The fire-fighting organization of the Edo period was run around the machi-bikeshi, formed by a
> large town on its own or by neighboring small towns in an association; it was usual for each of
> these towns to set up a banya (also called bansho or jishinban) and to station a watchman there
> permanently, keeping watch around the clock. At this time a frame was built on the banya so that
> the watchman could look out over the whole town, and a lookout platform was placed one level
> higher; that is what is called a hinomi-yagura.

Original: 「江戸時代の消防体制は大きな町ならば単独で小さな町ならば近隣で組合を設けて結成された町火消を中心に運営されていたが、この町ごとに番屋（番所、自身番とも）を設置し番人（火番、番太郎・番太と呼ばれていた）を常駐させて24時間態勢で警戒にあたるのが一般的であった。このとき番人が町全体を見渡せるよう番屋に櫓を組んで一段高いところに見張台を置いたが、それが火の見櫓と呼ばれる。」

and

> A hansho was generally provided at the top of a hinomi-yagura.

Original: 「火の見櫓には一般に、その上部に半鐘が設けられた。」

From ja.wikipedia 「半鐘」:

> In the Edo period it was attached at the top of a hinomi-yagura and the like and was struck when
> a fire or a flood occurred, summoning the local fire company and warning the neighboring
> residents of the danger. For that reason it is also called a keisho (alarm bell). [...]
> Originally it was used at temples to tell the monks in the precinct the time, and it is still
> used today as a signal for the start of a service.

Original: 「江戸時代には、火の見櫓の上部などに取り付け火災・洪水発生時などに鳴らし、地域の消防団を招集するとともに近隣住民に危険を知らせた。そのため、警鐘とも呼ばれる。」「もとは寺院で時間を境内の僧侶に知らせるために使用されているもので、現在も法要開始などの合図用として使用している。」

That second sentence is the closest readable thing to the record's "local temple bell doubling as
the alarm elsewhere" - it establishes that the hansho IS a temple object repurposed, which is a
weaker statement than the record's.

For the Takayama half of the paragraph, ja.wikipedia 「高山陣屋」 carries:

> After the prefectural office moved out in 1969, a policy of preserving it as a cultural property
> was set out, on the grounds that it is the only extant jin'ya.

Original: 「1969年（昭和44年）に県事務所が移転した後、現存する唯一の陣屋であることから文化財として保存する方針が示された。」

> The earthen storehouse on the grounds was originally built inside Takayama castle in the Keicho
> era (around 1600) and was moved to its present site in 1695.

Original: 「敷地内の土蔵は、元々慶長年間（1600年前後）に高山城内に建設され、1695年（元禄8年）に現在地に移築されたものである。」

**One half of the paragraph IS now sourced, from the office's own site.** 高山陣屋 official site,
Gifu Prefecture (Takayama Jinya Administration Office), 「高山陣屋について」,
https://jinya.gifu.jp/about/ - fetched (HTTP 200, 34 KB) and read. Translated from the Japanese by
this reader:

> Among the daikan and gundai offices, of which there are said to have been some sixty-odd across
> the country at the end of the Edo period, Takayama Jinya is the only one where the main
> buildings of the time remain.

Original: 「幕末には全国に60数ヶ所あったと言われている代官・郡代所の中で、当時の主要建物が残っているのは、この高山陣屋のみです。」

and, on the storehouse's origin:

> It then moved to the site where the Kanamori family's shimo-yashiki had stood, and the rice
> storehouse was moved there from the third bailey of Takayama Castle.

Original: 「その後、金森家の下屋敷があった場所に移転し、そこに高山城三之丸より米蔵が移されました。」

That gives the record, from the operator of the site itself, both "more than fifty" (sixty-odd)
and "the one such office still standing", and the rice storehouse's provenance. It does not
mention fire, a bell, patrols, stored water, or a pond - and it is the page most likely to, so its
silence is itself worth recording.

No page read mentions a bell on a ladder at a jin'ya, night patrols with clappers, water stored
against fire at a jin'ya, or a water-supply pond on the Takayama grounds.

---

## `cities/hinterland.html` fn-6

**Claim**: the ground below a field's drainage collector is the wettest in the valley, and nobody
builds there. (The rule it grounds: farmsteads stand upslope of the drain.)

### Verdict: CITED - for the principle, from alluvial geomorphology rather than from drainage engineering

No page says "below a field's drainage collector" in those words. What IS readable, and states the
same physical rule in the form the landscape actually takes, is the standard Japanese
geomorphological account of where an alluvial lowland's settlements sit: on the micro-high ground,
with the wet ground behind it left to paddy.

**Searches run (query text verbatim)**

1. WebSearch: `FAO drainage collector drain perpendicular to field drains land drainage design layout singular parallel`
2. Yahoo Japan: `水田 排水路 下手 湿田 宅地 微高地 集落立地 低湿地 避ける`
3. MediaWiki API, ja.wikipedia, extracts for `自然堤防` and `後背湿地`
4. Full-text greps for `waterlog|lowest part|low-lying|ponding|wettest` across the three FAO
   drainage PDFs listed below, after fetching them

**Source read (1)**: 日本語版ウィキペディア 「自然堤防」 (*natural levee*),
https://ja.wikipedia.org/wiki/自然堤防 - fetched through the MediaWiki API and read in full.

Translated from the Japanese by this reader:

> The natural levee forms a slight rise relative to the back marsh that spreads on the channel
> side and behind it, and within the low, wet alluvial lowland it is well drained. For that
> reason, in an alluvial lowland, long-established settlements are sited first of all on the
> natural levee, and it is also used as dry field.

Original: 「自然堤防は流路側および背後（流路と反対側）に広がる後背湿地に対してわずかな高まりとなり、低湿な沖積低地の中では水はけが良い。そのために沖積低地において、古くからの集落はまず自然堤防上に立地し、また畑として利用される。」

> The difference in height from the surrounding low ground, such as the back lowland, is in most
> cases less than a few metres, and it is difficult to read off the contour lines of a topographic
> map. It can also be estimated from the state of land use, by contrast with the back lowland,
> which is used mainly as paddy.

Original: 「後背低地などの周囲の低地との比高は、多くの場合数 mに満たないものであり、地形図の等高線から読み取ることは難しい。土地利用の状況から、主に水田として利用されている後背低地との対比によって推定することも可能である。」

**Source read (2)**: 日本語版ウィキペディア 「後背湿地」 (*back marsh*),
https://ja.wikipedia.org/wiki/後背湿地 - fetched and read in full.

> Because micro-high ground is distributed along the channel, the flood water drains away poorly,
> and mud is deposited by standing for long periods. [...] As the deposition of mud in the back
> lowland proceeds, it becomes land with poor drainage and gradually turns into wetland.

Original: 「流路沿いには微高地が分布するため氾濫水は排水しづらく、長期間にわたり湛水することにより泥の堆積が生じる。[...] 後背低地への泥の堆積が進行すると、排水不良の土地となり、次第に湿地化する（狭義の後背湿地）。」

> In regions where wet-rice cultivation predominates, as in Japan, it has been reclaimed and
> traditionally used as paddy.

Original: 「日本のように水稲栽培の卓越する地域では、開墾され伝統的に水田として利用されてきた。」

**How this supports the claim.** Between them these two articles state the whole of the record's
rule in geomorphic terms: within a lowland, the ground that drains badly is the LOW ground behind
the micro-high ground; that badly drained ground is what becomes paddy; and the houses go on the
rise, which is where they have gone since antiquity. The record's version - measure the farmstead
against the drain LINE, and do not put a house below it - is the same rule expressed against the
feature the map actually draws.

**Its limits, which the record should carry.** The source's low ground is a natural back marsh
behind a natural levee, not the strip immediately below a dug collector; the record is applying
the principle across a scale and a feature the source does not name. And both are encyclopedia
articles; their own shared reference is 鈴木隆介『建設技術者のための地形図読図入門 第2巻 低地』
古今書院、1998年 (Suzuki Ryusuke, *An introduction to reading topographic maps for construction
engineers, vol. 2: Lowlands*), a printed textbook with no online copy I could find.

**Partial support from the drainage side, for the first clause.** FAO, *Drainage of irrigated
lands* (Irrigation Water Management Training Manual), Chapter 3,
https://www.fao.org/4/ai587e/ai587e01.pdf - fetched (810 KB) and read:

> The main drain is the principal drain of an area. It receives water from collector drains,
> diversion drains, or interceptor drains (= drains intercepting surface flow or groundwater flow
> from outside the area), and conveys this water to an outlet for disposal outside the area. The
> main drain is often a canalized stream (i.e. an improved natural stream), which runs through the
> lowest parts of the agricultural area (Figure 9).

Chapters 6 (https://www.fao.org/4/ai587e/ai587e03.pdf, 976 KB) and the whole manual
(https://www.fao.org/4/ai587e/ai587e.pdf, 4.2 MB) were also fetched and grepped for
`waterlog|lowest part|low-lying|ponding|wettest`; they define waterlogging and list its signs, and
say nothing at all about settlement siting. Candidates I judged not worth fetching: FAO w7224e
Chapter 1 (a drainage-MATERIALS introduction, about pipe and envelope materials); FAO r4082e
Chapter 6 (the same field-drain/collector material already read in ai587e); and the ScienceDirect
"Surface Drainage" Topics page (a machine-assembled digest, and ScienceDirect refuses this
container - confirmed again under `vegetation.html` fn-22).

## `cities/hinterland.html` fn-9

**Claim**: some of the in-wall ground goes down as vegetable tracts rather than rice - intensively
worked garden ground, fed from wells and from night soil, of the kind that filled the surplus
inside a real walled seat.

### Verdict: CITED - in two halves, from two sources, with the join between them unsourced

**Half one: a real walled seat enclosed farmland, not just city.**

Source read: English Wikipedia, *Chinese city wall*, https://en.wikipedia.org/wiki/Chinese_city_wall

> Long-term strategic considerations meant that the walls of important cities often enclosed an
> area much larger than existing urban areas in order to ensure excess capacity for growth, and to
> secure resources such as timber and farmland in times of war. The city wall of Quanzhou in
> Fujian still contained one quarter vacant land by 1945. The city wall of Suzhou by the Republic
> of China era still enclosed large tracts of farmland.

I pulled the article's wikitext through the MediaWiki API to get that sentence's own reference,
since this project prefers an encyclopedia's source to the encyclopedia. It is:

> Chen Zhengxiang (陈正祥). ''Chinese Cultural Geography'' (《中国文化地理》)，Joint Publishing,
> Beijing 1983, pp 68, 74

That is a printed book with no online copy I could find, so the Wikipedia page is the readable
witness. The article's adjacent block quotation of Sen-Dou Chang (1970, p. 63) on walled-city
morphology is a second, better-provenanced anchor in the same paragraph if the record wants one.

**Half two: the garden ground itself - intensive, night-soil fed, hand watered.**

Source read: F. H. King (1911), *Farmers of Forty Centuries; or, Permanent Agriculture in China,
Korea and Japan*, Project Gutenberg (public domain, full text):
https://www.gutenberg.org/cache/epub/5350/pg5350-images.html

> Among the most common sights on our rides from Yokohama to Tokyo, both within the city and along
> the roads leading to the fields, starting early in the morning, were the loads of night soil
> carried on the shoulders of men and on the backs of animals, but most commonly on strong carts
> drawn by men, bearing six to ten tightly covered wooden containers holding forty, sixty or more
> pounds each.

> Here, too, the night soil of the city was being removed in closed receptacles on the shoulders
> of men, on the backs of horses and cattle and on carts drawn by either. Other men and women were
> hurrying along with baskets of vegetables well illustrated in Fig. 21, some with fresh cabbage,
> others with high stacks of crisp lettuce, some with monstrous white radishes or turnips, others
> with bundles of onions, all coming down from the terraced gardens to the markets.

> Expense is incurred to provide such receptacles as are seen in Fig. 37 for receiving not only
> the night soil of the home and that which may be bought or otherwise procured, but in which may
> be stored any other fluid which can serve as plant food.

> Generally the liquid manures must be diluted with water to a greater or less extent before they
> are "fed", as the Chinese say, to their plants, hence there is need of an abundant and convenient
> water supply.

On watering from a well specifically, King's nearest passage is about a field rather than a city
garden, and should be used as such:

> a Shantung farmer had just dug a temporary well to irrigate his little field of barley

**The gap, stated plainly.** Nothing I read says that the surplus ground inside a walled city was
worked as vegetable tracts fed from wells and night soil. The two halves are each sourced; the
join is the record's own inference and should be labeled as one.

---

## `fields.html` fn-84

**Claim**: a contour drain meeting a valley stream at about a right angle is ordinary side
drainage.

### Verdict: CITED - the geometry is standard practice; the phrase "valley stream" is not in the source

**Source read**: FAO, *Drainage of irrigated lands* (one of the FAO Irrigation Water Management
training manuals; "The manuals are intended for use by field assistants in agricultural extension
services and irrigation technicians at the village and district levels").

- Whole manual: https://www.fao.org/4/ai587e/ai587e.pdf
- Chapter 3, "Drainage systems": https://www.fao.org/4/ai587e/ai587e01.pdf
- Chapter 6, "Surface drainage systems": https://www.fao.org/4/ai587e/ai587e03.pdf

**Passages, verbatim.** From Chapter 3, on the bedding system:

> The beds are separated by parallel shallow, open field drains, oriented in the direction of the
> greatest land slope (Figure 13). The water drains from the beds into the field drains, which
> discharge into a collector drain constructed at the lower end of the field and at right angles
> to the field drains.

From Chapter 3, on regular subsurface patterns:

> This pattern can be either a parallel grid system, in which the field drains join the collector
> drain at right angles (Figure 20B), or a herringbone system, in which they join at sharp angles
> (Figure 20C).

From Chapter 6, on laying out a bedding system:

> During the first ploughing, care should be taken to make beds of uniform width throughout the
> field and to have the field drains running in the direction of the greatest slope. Any
> obstructions or low points in the field drains should be eliminated because they will cause
> standing water and loss of crops. The collector drain should be laid out in the direction of the
> lesser field slope, and should be properly graded towards the main drainage system.

And, joining the collector to the stream, from Chapter 3:

> The main drain is often a canalized stream (i.e. an improved natural stream), which runs through
> the lowest parts of the agricultural area (Figure 9).

**How this supports the claim.** Between them these say exactly what the record's paragraph says
about the geometry: the drains that carry water off the crop run down the fall; the collector sits
at the LOW END of the field, runs along the lesser slope (i.e. across the fall), and takes the
downslope drains at right angles; and the thing the collector discharges into is typically the
valley's own stream, canalized, running in the lowest ground.

**What it does not say.** It never uses the phrase "valley stream", and it does not state the
angle at which the collector meets the main drain. The right angles it names are between the FIELD
drains and the COLLECTOR. If the record wants to keep "meeting a valley stream at about a right
angle", it should either say that the right angle is the field-drain-to-collector angle (which is
what the source gives), or keep the stream-junction angle as a separate, unsourced inference from
the two facts.

FAO is a modern extension manual, not a premodern source; but the layout rule it states is a
consequence of where water runs downhill, which holds for a hand-dug ditch exactly as for a
machine-cut one. Nothing in the passages quoted depends on modern equipment.

---

## `towns.html` fn-22

**Claim**: one prominent two-story caravan inn for the wagon-train merchants, with a large stable
beside it and open ground beside that for the oxen and horses.

### Verdict: CITED for the stable and the standing yard - and CONTRADICTED on the second story

**Source read**: 王爽, 「消失的大车店」(The vanished dachedian), 吉林日报 (Jilin Daily), 25 April 2026,
http://jlrbszb.dajilin.com/pad/paper/c/202604/25/content_1049361.html (fetched, HTTP 200, read in
full). Jilin Daily is the Jilin provincial party newspaper; the piece is a descriptive account of
the wagon-inn as an institution and of one the author stayed in as a child.

Translated from the Chinese by this reader; the original follows each.

On what the institution is and where it stands:

> The dachedian was the shop that received passing carts and animals. It was generally set up on
> the main thoroughfares and in the belt around a city's outskirts, and provided simple board and
> lodging at relatively low cost.

Original: 「大车店便是接待过往车马的店铺，一般设置于交通要道和城郊一带，提供简单的食宿，费用也相对低廉一些。」

On the yard and the stable - the two features the record wants:

> The open ground of the back yard was for parking the carts, and there was also a long stable.
> The fittings were simple: one very long wooden feeding trough, above it a horizontal round
> timber, which was for tying the halters to. The stable stank, and in summer flies and mosquitoes
> flew about everywhere. Beside the stable was a small lean-to, where the grooms lived.

Original: 「后院的空地供停放马车用，还有长长的马厩，设施简单，有一个很长的木制喂马槽，上边一根横着的圆木，是拴马缰绳用的。马厩里臭气熏天，夏季里苍蝇、蚊子乱飞。马厩旁边有一个小偏厦子，住的是马夫。」

On the yard's well and its wall - useful for the map even though the note does not ask:

> The rammed-earth yard wall of a dachedian was very high, and many sharp-cornered shards of glass
> were set into its top, to stop thieves climbing over.

Original: 「大车店的土垒院墙很高，墙顶插了许多带尖角的碎玻璃片，以此防贼越墙。」

> In the yard there was a well, with several wooden buckets standing beside it.

Original: 「院里有一口水井，旁边放着几只木桶。」

**The contradiction.** The same paragraph, one sentence before the yard wall, says of the
buildings:

> In the yard, uniformly single-story buildings; likewise built of mud brick and reed thatch.

Original: 「院里清一色平房，同样是用土坯和苇草盖成。」

「平房」 means a single-story building, explicitly as against a multi-story one. So for this
building type - the north-Chinese wagon inn, which is the closest attested analogue to what the
record draws - the source says the opposite of a second story. The spacing detail from the
companion encyclopedia article, 维基百科 「大车店」
(https://zh.wikipedia.org/zh-hans/大车店, fetched and read), agrees on the institution and adds
that they stood "at intervals of about 40 li along the route" (「沿线约40里间隔」), i.e. half a
day's haul for a loaded wagon - which matches the newspaper's "about 20 kilometres, the distance a
loaded horse cart walks in half a day".

I also read ja.wikipedia 「旅籠」 (https://ja.wikipedia.org/wiki/旅籠) to see whether the Japanese
post-town inn would supply the second story instead. It does not: the article covers the hatago's
grades, its food, its meshimori-onna and its guilds, and says nothing about stories or stables.

The honest repair is either to drop the second story, or to keep it as an explicit map drawing
convention - a taller building so the inn reads from the road - and say that the one attested
analogue was single-story.

---

## `urban-features.html` fn-68

**Claim**: the north-China plain is dryland farming on loess with 400-800 mm of annual rain
concentrated in the summer monsoon.

### Verdict: CITED

**Source read**: *Drought characteristics and their impact on vegetation net primary productivity
in the climate-sensitive transition zone*, PLOS ONE (2026), DOI 10.1371/journal.pone.0343746,
PMC12935246. Read in full through NCBI E-utilities against PMC; the article is open access and the
public reading page is https://pmc.ncbi.nlm.nih.gov/articles/PMC12935246/

**Passage, verbatim**:

> Its geographical scope extends south to the Qinling Mountains and Huai River, west to the
> Wushaoling-Qilian Mountains, and covers Beijing, Tianjin, the entire province of Shandong, most
> of Hebei, Shanxi, Shaanxi, and Henan, as well as parts of Gansu, Ningxia, Anhui, and Jiangsu
> (Fig 1a). The climate is distinguished by annual precipitation of 400–800 mm and concentrated
> summer showers, and the geography differs between the mountainous northwest (grassland or
> woodland dominated) and the lowlands in the southeast (primary agricultural production areas).

**How it supports the claim.** It gives the 400-800 mm figure the record calls unsourced, for a
named northern-China region, together with the summer concentration, in one sentence.

**Its honest limits, which the record should carry.**

- The region is the climate-sensitive transition zone of northern China, defined by isotherms and
  isohyets. It CONTAINS the North China Plain (Beijing, Tianjin, Shandong, most of Hebei, Henan)
  but also the Loess Plateau provinces (Shanxi, Shaanxi, parts of Gansu and Ningxia). The record's
  own sentence conflates the plain with loess, so this source in fact fits its wording better than
  it fits the strict geography.
- It is a modern instrumental climatology (the paper's analysis runs over recent decades), not a
  historical one.

A second reading, if a tighter North-China-Plain figure is wanted: the meta-analysis *Effects of
fertilization measures on soil fertility and crop yields in drylands of the North China Plain*,
Frontiers in Plant Science (2026), DOI 10.3389/fpls.2026.1768991, PMC12932431, read in full,
classifies its North-China-Plain dryland sites by "annual average precipitation ... based on 500
and 800 mm" - i.e. it treats 500 and 800 mm as the meaningful breaks for dryland farming there,
which brackets the record's number from inside.

---

## `urban-features.html` fn-69

**Claim**: the jiegao (桔槔, a shadoof - pile, lever, rod and counterweight, the operator standing
on beams at the well mouth) and the lulu (辘轳, a windlass on a support frame over the well); and,
in the following sentence, the Ming-Qing history of the lulu.

### Verdict: CITED

**Source read**: Yannopoulos, S. et al. (2015), *Evolution of Water Lifting Devices (Pumps) over
the Centuries Worldwide*, Water 7(9), 5031-5060. DOI 10.3390/w7095031. Unpaywall reports
`oa_status: gold`, `license: cc-by`.

- Article landing page (public, open access): https://www.mdpi.com/2073-4441/7/9/5031
- The landing page returns HTTP 403 to this container's fetcher, both via WebFetch and via curl
  with a desktop user agent. That is MDPI's bot filter; a person's browser opens it. I therefore
  read the full text from MDPI's own file host, which serves the same PDF and returned HTTP 200
  and 3.6 MB:
  https://res.mdpi.com/d_attachment/water/water-07-05031/article_deploy/water-07-05031.pdf
  (the Universidad de Chile repository copy Unpaywall names,
  https://repositorio.uchile.cl/handle/2250/135740, sits behind a bot challenge and served HTML
  instead of the PDF.)

**Passages, verbatim**:

> The shaduf in China is known as Jiégāo and was locally called Diaogan, as well. According to the
> Agricultural Books of Ancient China written by Wang Zhen (1271–1368), Yi Yin invented the Jiégāo
> in the first year of the Shang Dynasty (ca. 16th–11th centuries BC) [38]. A wooden pole with a
> 2.6 m long, tapering body and circular ends was found at the site of an ancient copper mine in
> Ruichang of Jiangxi Province in 1988. There is a round arch groove at a distance of 1.66 m from
> the thin end of the pole. The pole was considered as the beam of Jiégāo and the groove would be
> the notch or mortise, cut into the beam to articulate the upright post like a hinge.

> The Lùlu was a groundwater lifting device in ancient China. It consisted of a wooden stand, a
> wheel an axle, a hand crank, and ropes. The wheel axle was the most important component.

> The Lùlu solved the problem of water lifting from deep wells. This marked a new epoch in the
> development and utilization of groundwater. With a series of technical innovations during the
> Ming and Qing Dynasties (1368–1911), the Lùlu gradually became the most usual groundwater
> lifting device in the north of China. Innovations included replacement of manpower by
> horsepower, the introduction of multiple containers and an increase in the depth of the well.
> The Lùlu is still used nowadays in rural areas.

**How it supports the claim.** The second and third passages carry the record's sentence about the
Ming and Qing almost word for word, including the three innovations (animal power, multiple
containers, deeper wells). The first carries the jiegao's identification as the Chinese shadoof
and its lever-and-fulcrum construction.

**Two details the record asserts that this source does NOT carry**, and which should be softened
or separately sourced:

- "the operator standing on beams at the well mouth" - the paper describes the beam and the hinge,
  not where the operator stands.
- "wells driven to tens of meters" - the paper says only "an increase in the depth of the well".
  No figure.

The irripro.net page the previous pass tried (http://www.irripro.net/en/nd.jsp?id=113) is gone; I
did not re-try it, since a 404 recorded twice by two methods is settled.

---

## `urban-features.html` fn-73

**Claim**: the kabu-ido system was a set of community rules regulating the number of wells per
village, administered by the residents rather than by any authority, specifically to de-escalate
conflict over groundwater.

### Verdict: CITED

**Source read**: Endo, Takahiro (2013), *The Kabu-ido System: Innovations in an Indigenous
Groundwater Management Institution*, Digital Library of the Commons, Indiana University (author at
the College of Sustainable System Sciences, Osaka Prefecture University).

- Record page (public): https://dlc.dlib.indiana.edu/dlc/handle/10535/8876
- PDF I read (public, HTTP 200, 618 KB):
  https://dlc.dlib.indiana.edu/dlc/bitstream/handle/10535/8876/ENDO_0894.pdf

This replaces the Springer article the previous pass could not open
(https://link.springer.com/article/10.1007/s12685-022-00302-1, a bot challenge and a login
redirect). It is a different paper by the same scholar on the same institution.

**Passages, verbatim**:

> Kabu-ido was developed to mitigate the conflict of interests associated with the drainage water.
> This system was essentially built on permit systems in which the total number of wells was
> restricted and the residents who desired wells were required to pay a fee to obtain Kabu (i.e.
> the right) to drill a well. The revenue generated from these fees was then used to build and
> maintain drainage gates

> Kabu-ido was a self-organized institution that was created through negotiation between the upper
> and lower villages.

> The core problem of self-organized common-pool resources management is how to undertake
> monitoring and sanctioning not by external government but by the resource users themselves
> (Ostrom 1990: 93-100). It is said that the lower villages conducted monitoring activities by
> providing patrolmen for each other

> Although the local government had a policy of managing water problems outside of a ring-levee
> (i.e. flood control), it did not interfere with water issues inside a ring-levee (i.e. drainage
> problems)

and, from its Table 1 (Development of the Kabu-ido in the Takasu ring-levee):

> 1854 A survey was conducted to determine the number of wells.
> 1854 The upper and lower villages agreed on well restrictions and adopted a three-year adaptive
> management plan.
> 1861 The number of authorized wells was 388.
> 1876 The maximum number of authorized wells increased to 806.

**How it supports the claim.** Every element of the record's sentence is here: rules regulating
the number of wells (a cap, a permit, a fee, a survey, a number), administered by the residents
rather than by any authority (self-organized, negotiated between villages, monitored by the
villages' own patrolmen, with the local government expressly declining to interfere inside the
ring-levee), and created to settle a conflict.

**One nuance worth carrying.** The conflict was not competition for the water itself: the upper
villages' artesian wells dumped drainage into the lower villages' paddy and flooded it, and the
cap was the remedy. "Conflict over groundwater" is true but reads as scarcity; the paper's conflict
is over the water the wells produced. The cap was also on the TOTAL across the ring-levee,
allotted to villages, rather than a per-village rule in the abstract.

---

## `vegetation.html` fn-4

**Claim**: no readable Chinese source measures a water-mouth grove.

### Verdict: STILL ABSENT - the record's absence statement holds

**Searches run (query text verbatim)**

1. Europe PMC full-text search: `"fengshui" AND ("water mouth" OR "shuikou") AND forest`
2. Crossref bibliographic: `shuikou forest fengshui village area hectares China`
3. Yahoo Japan (Chinese): `水口林 面積 公顷 风水林 村落 测量`
4. OpenAlex search: `mosaic-like constructed ponds meandering natural river` (run for fn-81; it
   returned nothing on groves)

**Candidates, and what happened to each**

| Candidate | URL | Outcome |
|---|---|---|
| Europe PMC | - | Zero results for the fengshui/shuikou query. Europe PMC searches full text, not just abstracts, so a measured area in a body table of an indexed open-access paper would have surfaced. |
| *Values of village fengshui forest patches in biodiversity conservation in the Pearl River Delta, China*, Biological Conservation | https://doi.org/10.1016/j.biocon.2011.01.023 | Not re-fetched: this is the source the record already cites for stem density and basal area, and its transects are 1200 m² plots inside patches, not whole-grove areas by grove type. It measures no water-mouth grove. |
| *The Complexity of Rural Migration in China* (Routledge) and its chapters | https://doi.org/10.4324/9781003125464 | Not fetched: a migration monograph; Crossref matched it on "China" and "village", not on groves. |
| OECD and FAO figure records returned by Crossref | (various) | Not fetched: figure captions about forest area in Brazil and SDG indicators. False matches on "forest area" and "hectares". |
| 香港植物標本室, "An overview of fung shui woods in Hong Kong" | https://www.herbarium.gov.hk/sc/special-topics/fung-shui-woods/an-overview-of-fung-shui-woods-in-hong-kong/index.html | Not re-fetched: this is the Herbarium summary the record already quotes ("The average area of a fung shui wood is 1 hectare"). It is about the BACK grove, and measures no water-mouth grove. |
| 福建省人民政府 / 福建日报 pieces on planting fengshui woods | https://www.fujian.gov.cn/zwgk/ztzl/sxzygwzxsgzx/sdjj/lsjj/202303/t20230321_6133874.htm ; https://www.fjdaily.com/app/content/2023-03/21/content_1817215.html | Not fetched: op-ed pieces urging more planting, from their titles and snippets; a newspaper editorial is not a measurement. |

Nothing measured turned up. The Korean entrance-grove analogues and the single Huangshan Daily
Jiekou figure that the record already carries remain the only numbers, and the ~0.1-0.5 ha
water-mouth cluster stays a labeled GUESS. That is the right label.

---

## `vegetation.html` fn-6

**Claim**: no readable source counts a Chinese grove's trees.

### Verdict: STILL ABSENT - the record's absence statement holds

Same search pass as fn-4 (the two claims sit in the same sentence pair and any paper carrying one
would carry the other): Europe PMC full text `"fengshui" AND ("water mouth" OR "shuikou") AND
forest`; Crossref `shuikou forest fengshui village area hectares China`; Yahoo Japan (Chinese)
`水口林 面積 公顷 风水林 村落 测量`. No candidate returned a
per-grove stem or canopy-tree count, and the one plausible paper (Biological Conservation 2011,
DOI 10.1016/j.biocon.2011.01.023) reports stems per hectare from fixed 1200 m² transects, which is
a density and not a grove's tree count - exactly as the record already says.

The record's bracketing arithmetic - Pearl-delta density times the drawn belt area - is the right
way to express it, and the GUESS label is correct.

---

## `vegetation.html` fn-22

**Claim**: the Kushiro Mire, mainly reed, is being invaded by alder where it dries, and the
reed-sedge community with a fluctuating water table is what resists that invasion.

### Verdict: CITED for the first half - and the second half is NOT supported by what I read

The Elsevier article the previous pass could not open is replaced by a freely readable Japanese
civil-engineering paper on the same question and the same mire.

**Source read**: 羽石嵩・中津川誠・工藤俊 (Takashi Haneishi, Makoto Nakatsugawa, Shun Kudo), 2011,
「釧路湿原におけるハンノキ林の拡大に及ぼす地下水の影響についての研究」 (Study of influences of
ground water on spread of the alder swamp forest area in Kushiro Mire), 土木学会論文集B1（水工学）
/ Journal of Japan Society of Civil Engineers Ser. B1 (Hydraulic Engineering) 67(4), I_1357-I_1362.
DOI 10.2208/jscejhe.67.I_1357.

- Article page (public): https://www.jstage.jst.go.jp/article/jscejhe/67/4/67_4_I_1357/_article/-char/ja
- PDF I read (public, HTTP 200, 1.1 MB): https://www.jstage.jst.go.jp/article/jscejhe/67/4/67_4_I_1357/_pdf/-char/ja

**Passage, verbatim, from the English abstract on the article page** (the authors' own English):

> This study aims to clarify the causes of the expansion in alder forest in Kushiro Mire by
> analyzing the relationships among ground height, groundwater level and vegetation. In recent
> years, Kushiro Mire has been drying as a result of basin development, including river
> improvement, and the main vegetation has been rapidly shifting from reed communities to alder
> forest.Observation data analysis revealed that the area of alder forest is increasing at
> locations where the groundwater is -0.4 m or more underground.

**Passages from the Japanese body**, translated by this reader, original after each:

> In 1977 the vegetation of the Kushiro Mire was 19,590 ha of reed community, about 87% of the
> whole mire's area, and alder forest existed only at the upstream edge of the mire. By 1996,
> however, along with the decrease in the mire's area, alder forest had expanded rapidly, coming
> to occupy about 35% of the whole mire, and about 45% in 2004.

Original: 「1977 年では釧路湿原の植生状況はヨシ群落が 19,590ha と湿原全体面積の約 87%を占めており，ハンノキ林は湿原上流端部に存在しているにすぎなかった．しかし，1996 年には湿原面積の減少とともにハンノキ林が急速に拡大し，湿原全体の約 35%，2004 年には約 45%を占めるようになっている．」

> At the points where reed community grows, almost all were points that are permanently inundated.
> Also, unlike the points where alder forest grows, there were points where the frequency of a
> relative water level of 0.4 m or more was high, so it is highly likely that alder finds it
> difficult to grow of itself at points where the relative water level is 0.4 m or more.

Original: 「ヨシ群落が生育している地点では常時冠水している地点がほとんどであった．また，ハンノキ林が生育している地点とは異なり，相対水位が 0.4ｍ以上の発生頻度が高い地点も存在しており，ハンノキは相対水位が 0.4ｍ以上となる地点では自生が困難となる可能性が高い．」

**How this supports the claim.** The mire is mainly reed (87% in 1977); it is drying because of
basin development; alder is taking it over, from 0% of the sheet to 45% in under thirty years; and
the boundary condition is standing water - reed sits under permanent inundation, alder cannot
establish where the water stands 0.4 m or more above the ground. That is the record's "invaded by
alder where it dries", with numbers.

**Where it does not support the record, and this matters.** The record says the resisting
condition is "the reed-sedge community with a fluctuating water table". This paper says the
opposite about fluctuation: the places where alder is expanding are precisely the places where the
water table is BELOW ground level and fluctuates strongly.

> Around rivers and former river channels, compared with the points other than those, the
> groundwater tends to be lower than the ground height and the fluctuation of the water level
> tends to be large.

Original: 「河川・河川跡周辺では，後述する河川・河川跡周辺以外の地点(図-5 参照)と比べ地下水位が地盤高より低く水位の変動が大きい傾向にある」

So on this source the resisting condition is permanent inundation, not fluctuation. The record's
second clause should be re-checked against whatever the Ecohydrology & Hydrobiology 2014 paper
actually says - and that paper is
https://doi.org/10.1016/j.ecohyd.2014.09.001 (*Hydrological influences on the distribution of
vegetation and tree height of Alnus japonica (Thunb.) Steud. in the Kushiro Mire, Japan*), which
Unpaywall reports as `is_oa: false`, `oa_status: closed`, with no OA locations. ScienceDirect
refuses this container. Since the claim cannot be quoted from a public page, the honest course is
to state the clause from the J-STAGE paper instead, which contradicts it, or to drop it.

---

## `vegetation.html` fn-23

**Claim**: a northern-Japan wetland classified into reed swamp, Carex lyngbyei marsh, and
reed/Calamagrostis grassland with Spiraea shrubs (Otanoshike, Ecological Research 2004).

### Verdict: FOR THE GM - but see the warning below

**The document**

- Title: *Effects of scale-dependent factors on herbaceous vegetation patterns in a wetland,
  northern Japan*
- Journal: Ecological Research, 2004 (volume 19)
- DOI: 10.1111/j.1440-1703.2004.00644.x
- Publisher: Wiley on behalf of the Ecological Society of Japan
- URL tried: https://doi.org/10.1111/j.1440-1703.2004.00644.x (not fetched after the access check
  below returned closed; the previous pass recorded an institutional login on the Springer
  presentation of the same journal)

**What blocked me, and why this is weaker than the usual FOR THE GM.** I ran all three recovery
routes before naming it:

1. Unpaywall (`https://api.unpaywall.org/v2/10.1111/j.1440-1703.2004.00644.x`): `is_oa: false`,
   `oa_status: "closed"`, `oa_locations: []`.
2. OpenAlex and Semantic Scholar: no open location, no repository copy.
3. Repository hunt: Crossref bibliographic search
   (`wetland vegetation classification reed swamp Carex lyngbyei Spiraea Kushiro Otanoshike`,
   filtered 2003-2006) surfaced no author manuscript, preprint or institutional copy; CiNii's
   search endpoint returns a 301 to a form this container cannot drive.

So this is a real paywall rather than a bot block. A person without a library subscription cannot
read it either. **Do not treat this as a quick win**: unless the GM has institutional access, the
right outcome is to keep the absence note, or to find a substitute. A likely substitute in the same
place and period, open on J-STAGE, is worth someone's next pass: J-STAGE's search API returns
several Japanese wetland-zonation papers for `湿原 植生 ヨシ スゲ ハンノキ 帯状分布`, including
`https://www.jstage.jst.go.jp/article/vegsci/35/2/35_67/_article` (植生学会誌, 2018) and
`https://www.jstage.jst.go.jp/article/seitai/30/3/30_KJ00001775890/_article` (日本生態学会誌,
1980), neither of which I had budget to read.

**What it would settle, and how much it would change.** It is one of five parallel citations in a
sentence establishing the hydrosere ladder, and the Japanese woody stage is already carried by the
Kushiro paper above and by the MLIT classification. Losing it costs the record the Carex lyngbyei
/ Spiraea rung specifically. That is the smallest stake of the three FOR THE GM items in this
batch.

---

## `vegetation.html` fn-89

**Claim**: the Izumo tsuijimatsu enclosed the entire circumference of the house before Meiji and
was later reduced to a hook covering only the north and west sides as flood risk fell and building
styles changed.

### Verdict: CITED

**Source read**: 日本語版ウィキペディア 「屋敷林」 (ja.wikipedia, *Yashikirin*), section 「築地松」,
https://ja.wikipedia.org/wiki/屋敷林 - fetched and read in full. This is the same encyclopedia
article the page already quotes for the sides a homestead grove stands on, so citing it here adds
no new work to the registry.

**Passage, verbatim** (Japanese original first here, because the sentence is the whole finding):

> 明治時代以前には家の全周を囲っていたが、水害の減少と建築様式の変化から北と西側だけをカバーする鉤型の形状へと変化した。

Translated from the Japanese by this reader:

> Before the Meiji era it enclosed the entire circumference of the house, but because of the
> decrease in flood damage and changes in building style it changed into a hook shape covering
> only the north and west sides.

The surrounding sentences give the reason the grove existed at all, which is the record's own
account:

> Its purpose is to keep off the winter monsoon and blown sand, rain and snow, and the summer
> western sun, but its original function was to strengthen the earthen bank built around the house
> for flood defense. For that reason the trees planted are mainly black pine, which puts down
> strong roots.

Original: 「冬の季節風や砂粒、雨や雪、夏の西日を防ぐ目的があるが、本来の機能は水防のために築かれた家の周囲を囲む土居を強化するためにあった。そのため、植えられた樹木は強い根を張るクロマツが主体となっている。」

**Two provenance points to record with it.**

- The key sentence carries no inline footnote marker of its own. The sentences immediately before
  and after it in the same paragraph cite footnote [2], which the article's reference list gives
  as 森隆男（編）『住の民俗事典』柊風舎、2019年、ISBN 978-4-86498-061-6、pp.291-297 - a printed
  Japanese folklore-of-dwelling dictionary with no online copy I could find. So the encyclopedia
  is the readable witness and its own source is a book.
- I also read the preservation council's own page, 築地松景観保全対策推進協議会, 「築地松とは」,
  https://www.tsuijimatsu.com/55 - the body that exists to conserve these groves, and therefore
  the better source if it carried the claim. **It does not.** It says only that the black pines
  are planted on the west and north sides of the residence, with no before/after history and no
  reason. Worth recording so the next pass does not re-try it.

The GM's 2026-08-29 ruling for the hook is unaffected either way; what changes is that the
"both forms are reported" premise the ruling answered is now sourced rather than general reading.

---

## `water.html` fn-71

**Claim**: you do not dig a draw-well in standing surface water; a well wants a water table
beneath dry ground you can stand a well rim and a windlass on.

### Verdict: CITED - from modern hand-dug-well construction guidance, which is the same object

No premodern East Asian source states this; it is the kind of thing nobody writes down because
nobody does otherwise. What exists, and is readable, is modern guidance for exactly the same
artifact - a hand-dug, hand-lined, bucket-drawn village well - where the siting rule is written
out because contractors have to be told.

**Source read (1)**: RWSSHP Resource Manual #3a, *Hand Dug Well Construction Manual*, Ethiopia
`Rural Water Supply, Sanitation and Hygiene Programme`, 2007 (the PDF's own running head is
"HDW & SD Construction Manual PTB 2007").
URL read (public, HTTP 200, 336 KB):
https://www.fhdesigns.com.au/wp-content/uploads/2023/01/Manual-3a-HDW-Construction.pdf

From its table comparing a traditional well with an improved one, the "Site Issues" row,
improved-well column, verbatim:

> At least 10m from any latrines or rubbish pits
> Not located in cemeteries, swampy or flood prone areas

and the "Headworks" row, traditional column against improved column, verbatim:

> Open / No concrete apron or drainage channel / May not have raised headwall / Nothing to prevent
> surface water entering the well / No protection against animals

> Closed / Apron, drainage and soakage pit / Raised headwall / Top 3 metres of shaft sealed to
> prevent surface water entering well / Diversion ditch to stop surface water flowing near well /
> Fenced

**Source read (2)**: WaterAid, *Hand-dug wells*, Technical brief, January 2013.
URL read (public, HTTP 200, 369 KB):
https://www.wateraid.org/us/sites/g/files/jkxoof291/files/technical-brief-hand-dug-wells.pdf

Verbatim:

> Create apron or install concrete slab and drain to prevent ponding of water at well

and, on the shaft itself:

> When construction has finished, the joints between the rings which are above the water table
> should be sealed with cement mortar.

> Top three metres of rings should be grouted with concrete to create a sanitary seal

**How this supports the claim.** Two independent manuals state the same two things: a hand-dug
well is NOT sited in swampy or flood-prone ground, and the whole detailing of its top - raised
headwall, sealed upper shaft, apron, drain, diversion ditch - exists to keep surface water OUT of
the shaft and to keep water from ponding at the mouth. A well standing in a reed bed fails both at
once. That is the record's assertion, arrived at from the other end.

**Its honest limits.** These are modern rural water-supply documents from Ethiopia and from an
international NGO, not historical East Asian sources, and their stated reason is sanitary
(pathogens entering the shaft) where the record's stated reason is practical (somewhere to stand
the rim and the windlass). The practical half - that the rim and the lifting gear need dry
standing - is implied by the raised headwall and apron rather than stated. If the record wants the
practical reason specifically, it is still unsourced and should say so.

---

## `ways.html` fn-1

**Claim**: a modest timber bridge lands roughly 5 to 15 real feet of deck past the water on each
side; the abutment sill is set back from the channel edge for scour, and the seat needs a length
of timber to bear on.

### Verdict: STILL ABSENT

The mechanism is stated in the engineering literature; the DISTANCE is not, in anything I could
open. Note that the two PDFs the previous pass listed as "PDFs that would not open to a reader of
text" both opened here and were read in full - so the previous absence note's reason was a tooling
limit, not a real one, and the verdict nevertheless stands on the content.

**Searches run (query text verbatim)**

1. WebSearch: `timber bridge abutment bearing length scour setback from channel bank small bridge design`
2. Yahoo Japan: `Timber Bridges Design Construction Inspection Maintenance EM 7700-8 Ritter pdf`
3. Direct fetches of the four engineering documents below
4. `pdftotext` greps across them for `setback|set back|bearing length|length of bearing|minimum bearing|scour|bank|distance|crest of|top of slope|stringer|streambank|behind the bank`

**Candidates, and what happened to each**

| Candidate | URL | Outcome |
|---|---|---|
| NRCS, *Technical Supplement 14Q: Abutment Design for Small Bridges*, National Engineering Handbook Part 654 (2007) | https://directives.nrcs.usda.gov/sites/default/files2/1712931168/7375.pdf | FETCHED (432 KB) and READ IN FULL as text. Gives the mechanism and a worked example, but no landing distance - see below. |
| Montana DOT, *Hydraulics Manual*, Chapter 17 "Bridges" | https://www.mdt.mt.gov/other/webdata/external/hydraulics/manuals/Chapter-17-Bridges.pdf | FETCHED (2.6 MB) and READ as text. One qualitative setback instruction, no number - see below. |
| WisDOT *Bridge Manual*, Chapter 12 "Abutments" | https://wisconsindot.gov/dtsdManuals/strct/manuals/bridge/ch12.pdf | Not fetched: a highway-bridge abutment chapter; its "bearing" material is bearing-device seat detailing in inches for steel and concrete girders, not a bridge's landing past a stream. |
| Maryland SHA, *Evaluating Scour at Bridges*, Chapter 11 | https://roads.maryland.gov/OBD/CH11-Evaluating-Scour-at-Bridges-April-2016.pdf | Not fetched: scour EVALUATION procedure (computing scour depth at an existing abutment), not layout guidance for where a small bridge lands. |
| CDOT *Bridge Design Manual* Section 11 | https://www.codot.gov/programs/bridge/bridge-manuals/design_manual/bdm_section-11_2025.pdf | Not fetched: the previous pass recorded this address as dead; the 2025 section the search returned is the structures section for state highway bridges, a different scale of structure. |
| Ritter, M. A. (1990), *Timber Bridges: Design, Construction, Inspection, and Maintenance*, USDA Forest Service (EM 7700-8), 944 pp. - the document most likely to carry a timber bearing length | https://www.ltrc.la.gov/ltap/pdf/timber_bridges_design_construction_inspection_maintenance.pdf | FOUND AND FETCHED (17.4 MB) and READ IN FULL as text. It settles the bearing-length half - in inches. See below. (The `research.fs.usda.gov/treesearch/6469` id that search engines point at is a DIFFERENT publication: I downloaded `6469.pdf`, 3.2 MB, and it is *The Forests of Connecticut*, Resource Bulletin NE-160. `fpl.fs.usda.gov/documnts/misc/em7700_8.pdf` 301s to a landing page and `fs.usda.gov/rm/pubs_journals/.../rmrs_1990_ritter_m001.pdf` 404s. The Louisiana Transportation Research Center hosts the real thing.) |

**What the two documents I read actually say.**

NRCS TS14Q, on the mechanism the record gives (scour reaching the bearing):

> Bridge abutments consisting of soil or other erodible material must be protected against the
> effects of scour. Either the footing should be embedded below the maximum anticipated scour
> depth or adequate scour protection must be provided. The embedment approach is generally not
> applicable with the shallow strip footings normally used with NRCS-designed bridges. Therefore,
> scour protection, such as rock riprap or gabions, should be provided, as necessary, to prevent
> erosion of the slope and possible undermining of the footings.

> The U.S. Forest Service recommends that bridges with shallow strip footings be used primarily in
> stream channels that are straight and stable, have low scour potential, and will not accumulate
> significant debris or ice.

and it describes exactly the bridge type the maps draw:

> Bridges installed under NRCS programs are generally single-span, single-lane structures and use
> various simple structural systems including rail cars, steel I-beams, and timber stringers.
> Timber decking is often used to provide the driving surface. The entire bridge structure is
> normally supported by simple strip footings of timber or concrete on either abutment.

The nearest thing to a number in it is its worked example, where the setback is expressed as a
ratio b/B from the CREST OF THE SLOPE rather than as a distance past the water:

> Compute b/B = D/B = 3 ft / 3 ft = 1

with the schematic labeling `b=3 ft`, `D=3 ft`, `B=3 ft`, on a 2H:1V slope. So a real small-bridge
abutment in the NRCS's own example has a 3 ft wide footing standing 3 ft back from the top of the
bank slope. That is a data point in the right neighborhood for the record's 10 ft a side, but it is
measured from a different origin (slope crest, not water's edge) and it is one illustrative example
rather than a stated rule, so it does not convert the GUESS.

Montana DOT Chapter 17 gives the only explicit setback instruction I found, and it carries no
number and is conditioned on ice:

> Where ice buildup is expected to be a problem, set the toe of spill-through slopes or vertical
> abutments back from the edge of the channel bank to facilitate the passage of ice.

**What Ritter 1990 settles - and it is not what the record expects.** The record gives two reasons
for the 5-15 ft landing, and the second is that "the seat itself needs a length of timber to bear
on". Ritter's manual is where that length is computed, and it is an amount in INCHES, not feet:

> Bearing area at beam reactions must be sufficient to limit stress to an allowable level. [...]
> For a given beam width, the minimum bearing length must not be less than that computed by
> (7-8) [...] Minimum required bearing lengths for the usual = 650 lb/in are given in Figure 7-10.

In its own worked designs the selected bearing lengths are:

> A bearing length of 10 inches is selected and applied stress is computed by

> A bearing length of 18 inches is selected. For an out-to-out beam length of 95-1/2 feet,
> reactions are revised

> A bearing length of 24 inches will be used for an out-to-out beam length

Those are highway-loaded glulam beams on spans up to 94 feet - far heavier than anything on these
maps - and they bear on 10 to 24 inches. So the bearing seat cannot be what makes a modest timber
bridge land 5 to 15 feet past the water; one to two feet of timber is the whole of it. Whatever
justifies the drawn 10 ft a side, it is the scour setback and the embankment, not the seat.

Ritter also describes the abutment types, which is what actually occupies the landing:

> Abutments support the bridge ends and contain roadway embankment material. The simplest timber
> abutment is a sawn lumber or glulam spread footing placed directly on the surface of the
> embankment (Figure 2-30). This type of abutment is used only when foundation material is of
> sufficient quality to support loads without excessive settlement, erosion, or scour.

> Post abutments are used to elevate the superstructure and are provided with a backwall and
> wingwalls for retaining fill embankment.

Nowhere in 944 pages does it give a distance from the water's edge to the abutment; greps for
`set back`, `setback`, `streambank` and `behind the bank` return nothing on that question.

**Summary for the record.** Both of the record's REASONS are now attested from public pages - the
scour mechanism from NRCS TS14Q, the bearing seat from Ritter 1990 - and the 5-15 ft distance is
attested by neither. Worse, Ritter shows the bearing-seat reason is worth about a foot, not five,
so the record's sentence over-credits it. The honest revision is to cite TS14Q for scour, cite
Ritter for the seat while saying the seat is inches, and keep the 5-15 ft band as a GUESS whose
real justification is the embankment and the scour setback.
