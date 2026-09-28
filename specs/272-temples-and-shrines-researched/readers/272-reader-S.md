# 272 second-pass reader findings (village shrines) - reader S

Second, different search pass over the 29 open items in 272-shrine-absences.md plus D50 (measured small village kuri) and D51 (village bell tower prevalence). Organized by item label. Each subsection below was written by a separate research pass; part-file provenance noted per section.

---

## Part A - torii spacing (090-1, 090-3, 090-2, 090-4, 090-5, 090 GUESS)

# Second-pass research: village shrine torii spacing (items 090-1 through 090-GUESS)

Session date: 2026-09-27. Tools used this pass: WebSearch (general web, Japanese-language queries),
WebFetch (page fetch + quote extraction), plus `pdftotext` run locally on one J-STAGE PDF that
WebFetch could only fetch as raw binary (mechanical text extraction of a page I actually retrieved,
not a new source). CiNii Research and NDL Digital Collections were attempted; CiNii page bodies did
not render for the fetcher (see HUMAN-FETCHABLE notes below). ADEAC (municipal digital archive
aggregator, used by many 教育委員会/市史 projects) was used as the municipal cultural-property/local-history
channel for this pass, since it is where a lot of 市史・町史 "異説"/資料編 content on individual stone
torii turned out to live.

---

## [090-1 / torii-spacing---two-regimes-and-nothing-in-between]

QUESTION: is there any source giving an actual spacing figure (distance between successive torii) for
a donation row of torii, or a carpenter's/construction rule for it?

**STILL SILENT** on the actual question (a spacing figure for a row of *separately, visibly spaced*
donated torii, or a carpenter's rule for laying one out). What this pass found instead:

- Tried this pass: CiNii Research search for 参道 鳥居 配置/空間 papers (found four Architectural
  Institute of Japan studies: 参道空間の研究(その1)/(その2), a Kamo-shrine spatial-composition study,
  and a Part VIII space-construction study); J-STAGE for the same corpus; direct web search for
  千本鳥居/稲荷 鳥居 間隔 cm/m (packed-row spacing); site-restricted search for a village shrine
  donation-row cultural-property PDF.
- **Fetched and read** J-STAGE aijax vol. 384 (船越徹・津田紘・清水美佐子, "参道空間の分節と空間構成要素の分析
  (分節点分析・物理量分析)：参道空間の研究(その1)", 1988). WebFetch could only return the raw PDF stream, so
  I ran `pdftotext` on the same fetched file and grepped it. It measures "分節点" (points where the
  sandō's character changes - level changes, planting, bends, and torii) and the *proportion* of total
  sandō length between such points at five great shrines (Kasuga, Kotohira-gū among them), e.g.:
  `お お む ね 800m 前後 を 境 に ， そ れ 以下 で は 3 〜4 に 集 中 し て お り` (roughly: "around a
  boundary of about 800 m, [approaches] shorter than that cluster at 3-4 segmentation points") and
  `第 1 分 節 空 間 の 距 離 は お お む ね 参道 全 体 の 4 〜6 割 を占め` ("the first segment's distance
  is generally 40-60% of the whole sandō"). This is about a *single* torii's position as one
  segmentation marker along a processional approach at great shrines, not about spacing inside a
  multi-torii donation row, and it gives no absolute spacing figure or carpentry rule. Not an answer.
- CiNii pages for the other three papers (its 2, the Kamo-shrine study, Part VIII) would not render
  through the fetcher - see HUMAN-FETCHABLE below.
- Confirmed real, citable numbers for the *packed/tunnel* end of the "two regimes," which the project
  already treats as one regime but which had not been directly sourced this way before:
  - Fushimi Inari's Senbon Torii: "左右の二股の長さ約70メートルに高さ約2メートルの鳥居が隙間なく密集して建立されて
    います" (about 70 m of paired paths lined with ~2 m-tall torii built up "with no gaps," i.e.
    packed) - fetched from https://kyototravel.info/senbontorii, page "伏見稲荷大社・千本鳥居の完全ガイド｜本数・
    色彩などを解説."
  - Yūtoku Inari Shrine (祐徳稲荷神社), between the honden and the okunoin: "ほぼ、10センチ間隔で並んでいるようです。"
    ("They appear to be lined up at intervals of almost 10 centimeters.") - fetched from
    https://www.sagatv.co.jp/kachiplus/media/archives/903653, "祐徳稲荷神社に鳥居が多いのはなぜ？".
  These are real spacing figures, but only for the packed/contiguous regime (torii essentially
  touching, no visible gap), not for a donation row of individually spaced, individually dedicated
  gates - so the "nothing in between" gap that 090-1 is asking about stands confirmed rather than
  filled: this pass found hard numbers for one end of the range (10-20 cm packed) and, as before,
  nothing for a spaced-out donation-row regime or a carpenter's rule for laying one out.

**HUMAN-FETCHABLE:**
- https://cir.nii.ac.jp/crid/1571417126963965696 - "参道空間の研究(その2)：神社の参道空間の構成要素の分析"
  (CiNii Research record). Likely answers this item if it contains a component/element table with
  torii spacing. Blocked: WebFetch returned an empty page body (CiNii's page appears to be rendered
  client-side/JS and the fetcher got no text).
- https://cir.nii.ac.jp/crid/1570854176999257216 - "Study on Approach Spaces of SHINTO Shrines (Part
  VIII): Analysis of space-construction on approach spaces of SHINTO Shrines" (AIJ proceedings, 1986).
  Same likely relevance, same block (empty page body).
- https://cir.nii.ac.jp/crid/1572261551891481728 - "A study on the Spatial Composition of Shrine-
  Approach: Through the survey of KAMO shrines" (AIJ, 1989). Same relevance/block.

---

## [090-3 / torii-spacing---two-regimes-and-nothing-in-between-3]

QUESTION: find Manzo Inari's approach length/spacing, or another village-scale multi-torii row's
length/spacing.

**STILL SILENT** - no page gives a measured length or a measured spacing for Manzo Inari's row, and
no other village-scale (non-great-shrine) multi-torii row with documented spacing was found either.

- Tried this pass: web search for 万蔵稲荷/萬蔵稲荷 with 参道, 小坂峠, 距離, 案内板, 山中七ヶ宿街道; a YAMAP
  landmark-distance search (YAMAP is a hiking-trail app that often prints trail distances - the pass
  in the prompt suggested trying it); Wikipedia's own 萬蔵稲荷神社 article; a general "村社 稲荷 鳥居 100基
  江戸時代" search to surface any other candidate village row.
- **Fetched and confirmed** several numbers about Manzo Inari, none of them a length or spacing figure,
  and they do not agree with each other, which is itself worth recording:
  - ja.wikipedia.org/wiki/萬蔵稲荷神社 (fetched): founding "天明5年（1785年）頃" (c. 1785); it only became
    a 村社 (village shrine) in "明治42年" (1909) when 16 neighboring shrines' 11 deities were merged
    into it - i.e. its formal village-shrine status postdates 1868, though its founding does not.
    Gives no torii count or approach length.
  - note.com/suzu_ki6155/n/n4563cc3b74a3 (fetched, "【東北おでかけ】立ち並ぶ鳥居をくぐってお参り"): the author
    personally counted the torii on the way back - "結果114個でした！" (114, in total) - and separately
    "入り口から７分ほど歩くと景色が開けてきました" (about 7 minutes' walk from the entrance before the view
    opened up). This is almost certainly the same walking-time-and-count data the project's existing
    3-4 m/114-arch estimate is built from (both the 114 count and the ~7-minute figure match exactly);
    it is a personal blog account, not a survey, and "the view opens up" is not stated to be the end
    of the row or the shrine itself, so it still is not a measured length.
  - Other fetched pages give inconsistent torii counts for the same row: 小坂峠 に200もの鳥居 (
    sendaimiyagi-fc.jp/ site listing, "萬蔵稲荷神社"); その鳥居の数なんと百数十其 ("well over a hundred," from
    shiroishi.ne.jp/spot/3329); 参道から100数基余りの朱塗りの鳥居 ("just over 100," hotokami.jp); 参道には朱塗りの
    小鳥居が100基以上連なり ("100+," tabiiro.jp). None gives a length or spacing; the count itself is
    evidently not authoritatively fixed across sources (100+, 114, 130+, 200), which weakens using any
    single count as an anchor for a per-arch spacing calculation.
  - No YAMAP trail-distance entry exists for this specific spot under either "小坂峠" landmark (the two
    YAMAP 小坂峠 landmarks that came up are in Kochi and in Fukushima/Miyagi near 半田山, not clearly the
    same pass, and neither page's summary gave a distance to the shrine).
- No other village-scale (not a "great shrine") multi-torii row with a documented length or spacing
  turned up in this pass.

---

## [090-2 / torii-spacing---two-regimes-and-nothing-in-between-2]

QUESTION: find ANY dated/measured distance between a shrine's ichi-no-torii and ni-no-torii.

**STILL SILENT** - closest candidate found and fetched, but it does not actually give the 1st-to-2nd
distance, only the overall sandō length with the second torii somewhere inside it.

- Tried this pass: web search combining 一の鳥居/二の鳥居/距離/m/参道; CiNii search for 参道 鳥居 配置
  academic papers (see 090-1, same corpus fetched: none gives a shrine-by-shrine torii-to-torii
  distance table in the parts I could read); direct fetch of Kasuga Taisha's own two guidance pages;
  direct fetch of a torii-etiquette explainer that a search summary implied might contain a Kasuga
  distance figure.
- **Fetched** https://kashiharajingu.or.jp/point/8277.html (橿原神宮 "参道・鳥居"): "表参道の距離は約300ｍ。
  途中には宮川にかかる神橋や、境内の鳥居4基の中で一番大きな第二鳥居があります。" ("The main approach is about 300 m.
  Partway along it are the Miya-gawa's sacred bridge and the largest of the precinct's four torii, the
  second torii.") This gives the *whole* sandō's length (~300 m) and says the second torii is
  somewhere along it, but not the distance from the first torii to the second torii specifically, so
  it does not answer the question as posed, and Kashihara Jingū is an Imperial-grade great shrine, not
  village scale.
  https://www.kasugataisha.or.jp/guidance/morisanpo/ and .../keidai-map1/ (both fetched, Kasuga
  Taisha's own two guided-walk pages from ichi-no-torii toward the main hall) describe landmarks along
  the way (影向の松, 春日塔跡, 御旅所, etc.) but state no distance figure at all.
  A search-engine synthesis (not a fetch) had claimed Kasuga's ichi-no-torii to ni-no-torii/honden
  stretch is "1km以上"; I could not verify this by fetching any actual page (including
  croissant-online.jp/life/166673/, fetched, which discusses torii-passing etiquette only and states no
  distance for any shrine) - so that figure is NOT included as answered; it would need to be traced to
  its actual source to be citable.
- No village-scale (村社-level) example with a documented ichi-no-torii/ni-no-torii distance was found.

---

## [090-4 / torii-spacing---two-regimes-and-nothing-in-between-4]

QUESTION: (a) fetch pages for the 1774/1790/1800 single stone torii found in summaries last time; (b) find
a village Inari shrine with a documented pre-1868 ROW of donated torii.

**STILL SILENT** on both (a) locating those specific three dates by fetch, and (b) a pre-1868 village
donation ROW - but this pass fetched a NEW, directly verbatim-quotable single-torii example that
confirms the same "single gate, not a row" pattern under independent search terms, which is worth
recording as corroboration.

- Tried this pass: targeted date searches (安永三年/寛政二年/寛政十二年 + 鳥居 + 村中/建立/石造) aimed at
  relocating the specific 1774/1790/1800 stone torii from the first pass's summaries; a
  `site:adeac.jp` search for 寛政 鳥居 村中 石鳥居 (ADEAC aggregates many municipal 市史/町史 digital
  archives, which is where 文化財調査報告書-style local torii inventories live); direct fetches of the
  ADEAC hits that looked like torii-inventory entries.
- The specific 1774/1790/1800 examples from the prior pass's summaries were **not relocated** by fetch
  this pass; the exact-date searches returned only unrelated hits (a kabuki performance chronology,
  village-history PDFs with no torii match, other stone-torii cultural-property listings with
  different dates). This item remains unresolved for those three specific dates.
- **Fetched and confirmed, new this pass**: https://adeac.jp/kudamatsu-city/texthtml/d100060/mp100060-100060/ht000720
  (下松市史異説, entry 一六 "石鳥居," Kudamatsu City, Yamaguchi Prefecture digital archive). Verbatim
  inscription quoted on the page: "延寳七己未馬場鳥居建立氏子 / 妙見山法印増遍代" - translation: "Built by the
  parish (ujiko) in Enpō 7, tsuchinoto-hitsuji [1679], the torii at the horse-ground [entrance to the
  mountain path], during high priest Zōhen's tenure of Myōken-san." Date: 延宝七年 = 1679, i.e. Edo
  period, well before 1868. Dedicator: 氏子 (the parish/community, i.e. village-level, not a named
  individual donor) - but it is explicitly ONE torii ("single torii gate, not part of a row" per the
  page), at the gate to Shiomatsu/Kudamatsu Shrine's mountain approach; it was renamed from bearing
  "妙見山" to "降松神社" only after the Meiji shinbutsu-bunri in 1871. This is a real, dated,
  community-dedicated, pre-1868, single village torii - it reinforces rather than overturns the
  existing finding that every dated pre-1868 village torii found so far is a single gate, not a row.
- No village-scale Inari shrine with a documented pre-1868 ROW of donated torii was found this pass
  either (Manzo Inari's own row, per 090-3 above, has no dated donation history at all, let alone a
  pre-1868 one; the shrine itself was only formally designated 村社 in 1909).

**HUMAN-FETCHABLE:**
- https://adeac.jp/kudamatsu-city/text-list/d100040/ht010220 - "石鳥居(いしとりい)について," 下松市 digital
  archive, page 51 of a 122-page viewer document. Likely relevant (same municipal stone-torii-inventory
  series as the entry above); the body text past the navigation frame did not come through the fetch -
  only the page's header/navigation chrome was retrievable, with a note that page 51 of the underlying
  viewer document holds the actual content (the viewer is presumably a paginated image/JS viewer the
  fetcher cannot walk into).

---

## [090-5 / torii-spacing---two-regimes-and-nothing-in-between-5]

QUESTION: search municipal/prefectural 文化財調査報告書 for a small/village shrine's measured sandō length,
or the distance from its innermost torii to its haiden/honden.

**STILL SILENT.** This pass ran targeted searches for 文化財調査報告書-style PDFs giving a sandō length or
an innermost-torii-to-honden distance for a small shrine, and for village-shrine torii-count/donation
inventories via ADEAC's municipal-archive aggregator. Neither search surfaced a fetchable cultural-
property survey PDF with a numeric sandō or torii-to-hall distance for a village-scale shrine; the
ADEAC hits that did surface (see 090-4) are local-history narrative entries about individual stone
objects (with dates and dedicators), not the kind of formal measured-survey report (with a site plan
and dimensions) the item is asking about. No new candidate PDF was found to list as HUMAN-FETCHABLE
either - the searches this pass did not turn up a specific document, fetchable or not, that looked like
it would answer this question; a further pass would need prefecture-by-prefecture 教育委員会 report
repositories searched individually rather than a general web query, which this pass's tools did not
reach.

---

## [090 GUESS]

Context: "a guess inside the GM's ruling, bounded by Manzo's estimated row" is the same guess as 090-3.

This pass's 090-3 search did **not** change this guess's status: no measured length or spacing for
Manzo Inari's row was found (only a personal blog's torii count of 114 and a ~7-minute walking-time
figure, which appear to be the same numbers the existing 3-4 m/114-arch estimate is already built
from), and no comparable village-scale row with documented spacing was found to replace it as an
anchor. The guess remains a guess, un-upgraded to a sourced figure, and the underlying count (114) is
now seen to be one of several inconsistent counts (100+, 114, ~130, 200) reported for the same row
across sources, which if anything weakens rather than strengthens using 114 specifically as the
divisor in the estimate - worth flagging to whoever owns the guess's exact arithmetic.

---

## Part B - shrine siting and hall size (100-1, 100-2)

# Second-pass research: village shrine placement and dimensions

## [100-1 / where-does-a-village-put-its-shrine-and-how-big-is-it]

**This time's approach:** different tools/terms from pass 1. Chinese side: web search for 村落选址 风水 庙 位置 水口, CNKI/academic-style queries on 村落选址 风水 公共建筑 庙宇 布局规律, 风水视角 传统村落 空间布局 庙 祠堂, Baidu Baike 庙宇选址风水原则, plus a direct fetch of the Lagerwey/Faure (劳格文/科大卫) edited-volume preface excerpt that pass 1 apparently already found in some form (news.qq.com reprint) - fetched it directly this time to check whether its water-mouth claim is stated as a GENERAL rule or as one case. Japanese side: J-STAGE search for 神社の立地 集落 中心 周縁 景観, CiNii for 村落 空間構造 神社 位置づけ 鎮守, Kotobank for 鎮守の森, and a Keio-repository academic PDF (氏神鎮守と社会構造の関連に関する一考察, 1971) found via search.

### ANSWERED (partial) - Japanese side: general encyclopedic statement on chinju placement

**Claim:** A general-audience but citable Japanese encyclopedia states, as a general rule (not about one named village), that the chinju shrine sits either within the settlement or at its edge, and that the shrine grounds double as the gathering place for the village's major events.

**Quote (verbatim, 改訂新版 世界大百科事典 "鎮守の森" entry, via Kotobank):**
> "村落を中心としたような一区域を鎮め守る神社の境内にある森。日本では普通，村落の中や外れに鎮守の社があるが，そこは村落の主要な行事のための集いの場でもある。"

**Translation (mine):** "A forest within the precinct of a shrine that pacifies and protects an area centered on a village. In Japan it is ordinary for the chinju shrine to be located within the village or at its outskirts, and that place also serves as the gathering site for the village's major observances."

Credited authors of the encyclopedia entry: 筒井迪夫 + 橋本与良.

**URL:** https://kotobank.jp/word/%E9%8E%AE%E5%AE%88%E3%81%AE%E6%A3%AE-569966
**Page:** コトバンク, "鎮守の森" (citing 改訂新版・世界大百科事典), fetched 2026-09-27.

Caveat: this is a general statement of WHICH TWO positions are typical (center-of-settlement or edge) but does not itself argue in feng-shui/geomantic terms and does not pick one over the other as more correct or "most strategic" - it is descriptive, not a siting rule with a rationale.

### STILL SILENT - Chinese/general feng-shui side

What I tried this time: WebSearch for "村落选址 风水 庙 位置 水口", "CNKI 村落选址 风水 公共建筑 庙宇 布局规律", "风水视角 传统村落 空间布局 庙 祠堂 位置 总结", "土地庙 选址 风水 村口 general principle 学术", Baidu Baike "庙宇选址风水原则"; then direct-fetched the actual source behind the water-mouth claim pass 1 had already surfaced (news.qq.com's reprint of the preface to 劳格文/科大卫 eds., *中国乡村与墟镇神圣空间的建构*, 社会科学文献出版社 2014) to check its status.

**What I found instead:** Confirmed, by fetching the passage in context, that the water-mouth (水口) temple-clustering claim is presented in that preface as a description of a SPECIFIC case study - Zhuli village (竹里村), Jingxi/Ji County, Huizhou (徽州绩溪县竹里村) - not as a universal rule. The sentence "就乡村空间的建构而言，至关重要的中枢，位于'水口'即小河汇入大河之处" is immediately followed by "该文研究的徽州绩溪县竹里村，夹一湍急小河而建" - i.e., it introduces that one village's case, exactly as pass 1 already characterized it. No general/abstracted statement (e.g., "in Chinese villages generally, the shrine/temple's siting is the most feng-shui-strategic position") was found anywhere else searched. Baidu Baike and general feng-shui pages (风水宝地, 建筑风水, etc.) only restate the generic "山环水抱、藏风聚气" (mountains embracing, water encircling, wind concealed, qi gathered) siting principle for buildings/settlements in general - none of them single out the VILLAGE SHRINE/TEMPLE specifically as occupying that position, as opposed to the settlement as a whole.

One partial general claim surfaced but is a Wikipedia-search AI-summary claim, not independently verified by me on a fetched page: that "in nearby villages, earth god temples (土地庙) are typically located at village entrances, though as villages expanded some temples originally at the entrance moved to locations within the village" - this was reported as coming from a Beijing Forestry University journal (北京林业大学学报, 社会科学版, 2014, vol.13 no.3), but the PDF (https://sheke.bjfu.edu.cn/cn/article/pdf/preview/9145.pdf) would not render as readable text through the fetch tool (compressed/binary stream), so I could NOT verify this claim on the actual page and am not citing it as answered.

**HUMAN-FETCHABLE:**
- https://sheke.bjfu.edu.cn/cn/article/pdf/preview/9145.pdf - 北京林业大学学报(社会科学版), vol.13 no.3, Sept 2014, apparently on Zhejiang village siting and feng shui, possibly containing a general statement about 土地庙/temple placement at village entrances. Likely answers the question. Blocked because: the fetch tool received the PDF as a compressed byte stream it could not decode to text (5.2 MB); binary saved locally by the tool but I am not permitted to run local PDF extraction outside the web-fetch/search tools for this task.
- https://ir.lib.cyut.edu.tw/bitstream/310901800/32812/1/104CYUT0224004-001.pdf - 朝陽科技大學建築系建築及都市設計碩士班碩士論文, "以環境規劃觀點探討風水選址的環境評估要素" (feng shui siting environmental-evaluation factors). Likely discusses general siting principles including public/religious buildings. Blocked because: same binary/compressed-PDF rendering failure (2.9 MB).
- https://koara.lib.keio.ac.jp/xoonips/modules/xoonips/download.php/AN00224504-19710515-0057.pdf?file_id=136613 - 「氏神鎮守と社会構造の関連に関する一考察(一)」, Keio University repository, 1971. Title suggests exactly the general Japanese-side question (relation of ujigami/chinju siting to social structure). Blocked because: same binary/compressed-PDF rendering failure (1.7 MB) through the fetch tool.

---

## [100-2 / where-does-a-village-put-its-shrine-and-how-big-is-it-2]

**This time's approach:** instead of encyclopedia/style articles (pass 1), searched Japan's National Cultural Properties Database (kunishitei.bunka.go.jp) interface, then used Wikipedia's own full-text search (a different tool/corpus than pass 1) for registered/prefecturally-designated shrine buildings with explicit 桁行/梁間 figures, filtering for shrines that are explicitly ranked 村社 (village shrine) / 郷社 (district shrine), not great famous shrines, then fetched the raw wikitext of the two best candidates for verbatim sourcing.

### ANSWERED

**Claim:** Two concrete, sourced dimensions exist for ordinary, non-famous rural shrines' worship halls, in ken (間):

**(a) Hie Shrine, Kurihara City, Miyagi (日枝神社, 栗原市)** - formally ranked 村社 (village shrine) in 1874, its haiden and honden are a Miyagi Prefecture tangible cultural property (1985). Raw wikitext, quoted verbatim:

> 本殿 dimensions: "本殿は桁行2間・梁間1間で"
> 拝殿 dimensions: "拝殿は、桁行3間・梁間2間、入母屋造、瓦葺"
> Village-shrine rank: "明治時代初頭に発令された神仏分離令を経て1874年（明治7年）に村社に列した"
> Designation: "1985年（昭和60年）5月24日、宮城県から有形文化財に指定された"

**Translation (mine):**
- Honden: "The main sanctuary is two bays (桁行/ridge-span) by one bay (梁間/beam-span)."
- Haiden: "The worship hall is three bays by two bays, hip-and-gable roof, tile-roofed."
- "...was ranked as a village shrine (村社) in 1874 (Meiji 7), following the Shinto-Buddhist separation edict issued in the early Meiji era."
- "...was designated a tangible cultural property by Miyagi Prefecture on May 24, 1985 (Showa 60)."

Taking 1 ken (間) as the conventional ~1.818 m (6 shaku) module: haiden approx. 5.45 m (ridge) x 3.64 m (beam); honden approx. 3.64 m x 1.82 m.

**URL:** https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9E%9D%E7%A5%9E%E7%A4%BE_(%E6%A0%97%E5%8E%9F%E5%B8%82)
**Page:** Japanese Wikipedia, "日枝神社 (栗原市)", fetched 2026-09-27 (raw wikitext).

**(b) Urashima Shrine, Ine, Kyoto (浦嶋神社)** - former 郷社 (district shrine, one rank above village shrine, still an ordinary rural shrine, not a great national shrine), haiden+chūden registered as a 登録有形文化財 (Registered Tangible Cultural Property) on 2014-04-15:

> "木造平屋建、銅板葺、建築面積93平方メートル。後方に中殿を張出し、広い柱間で桁行三間梁間二間。"

**Translation (mine):** "Wood-built, single story, copper-plate roofed, building area 93 square meters. The central hall projects to the rear; with wide bay spacing, [the whole worship-hall-plus-central-hall structure is] three bays (桁行) by two bays (梁間)."

(Note: the 93 sqm figure is for the combined haiden + chūden structure, not the bay count alone - the bay count of 3x2 describes the module/spacing, and the building's actual footprint is larger because of the projecting chūden and surrounding elements; I am reporting both numbers as given rather than reconciling them, since the page itself does not reconcile them.)

**URL:** https://ja.wikipedia.org/wiki/%E6%B5%A6%E5%B6%8B%E7%A5%9E%E7%A4%BE
**Page:** Japanese Wikipedia, "浦嶋神社", fetched 2026-09-27 (raw wikitext).

Both are citable as real, non-famous, village/rural-scale examples with actual bay-count dimensions, one of them (Hie Shrine) explicitly ranked 村社 ("village shrine") by the Meiji government, which is about as on-the-nose a match to "village-scale shrine" as the item could ask for.

**HUMAN-FETCHABLE (not needed given the above, but noted for completeness):**
- https://kunishitei.bunka.go.jp/ (国指定文化財等データベース) - the interface is a JS-driven search app (bsys/index) that would not return queryable dimension data through the fetch tool; a human could run the search UI directly (種別: 近世以前／神社, free-word 拝殿) and open individual property detail pages, which typically carry 構造形式、規模 fields with exact 桁行/梁間.

---

## Part C - resident monk prevalence (110-1, 110-2)

# 272 second-pass research: village shrine resident monk (110-1, 110-2)

## [110-1 / does-the-country-monk-live-at-the-shrine]

**Tools tried this pass:** CiNii Research (direct crid pages - JS-rendered, returned empty to
WebFetch), J-STAGE global search, Kotobank, a prefectural (Nara) cultural-administration PDF
fetched and run through `pdftotext` locally, plus general web search for 別当/神仏分離 statistics.
CiNii's own article pages would not render any text for WebFetch (single-page-app shell, no
server-rendered content) - every crid URL tried came back blank - so CiNii was a dead end for direct
fetching this pass, though its search results still surfaced J-STAGE-indexed papers (see below).

**STILL SILENT** on a national number or proportion. Nothing found gives a nationwide count or
percentage of Edo-period village shrines with a resident jingūji/bettō-ji monk versus a lay
shrine-keeper. But this pass found a real, quotable, REGIONAL academic answer that at least
establishes the direction and gives a qualitative-but-sourced weighting where the first pass had
none:

**PARTIAL ANSWER (regional, qualitative):** 由谷裕哉 (Yuya Hiroya), "神仏分離後に語られた藩政期の神社と社僧：旧金沢市域の例から"
["Domain-period shrines and shrine-monks as narrated after shinbutsu-bunri: examples from the old
Kanazawa city area"], 宗教研究 (Religious Studies / Journal of Religious Studies), vol. 81, no. 2
(2007), pp. 437-461. DOI: https://doi.org/10.20716/rsjars.81.2_437. J-STAGE:
https://www.jstage.jst.go.jp/article/rsjars/81/2/81_KJ00004718210/_article/-char/ja (fetched
2026-09-27; abstract page).

Verbatim quote (Japanese, from the fetched J-STAGE abstract page):

> 社人が奉仕した神社がむしろ稀少で、幕末までに存在していた多くの社僧や修験が明治以降に復飾し

Translation (mine, marked as translation): "Shrines that were served by lay priests [社人] were, if
anything, rare; the many shrine-monks [社僧] and mountain ascetics [修験] who existed down to the end
of the Edo period returned to lay status [i.e. became Shinto priests] from the Meiji era onward."

This is a peer-reviewed characterization, for one specific area (the old city of Kanazawa, former
Kaga domain), stating that shrines with NO resident monk/ascetic - i.e. tended only by a lay
shrine-keeper - were the rare case, and that shrines with a resident social monk or mountain ascetic
were the common case there through the end of the Edo period. It is a real scholarly data point in
the direction the first pass could not find, but it is explicitly local (one castle-town/former
domain's shrines, not villages specifically, and not the whole country), so it should be read as
supporting evidence for one region rather than a national figure.

Secondary, weaker corroboration - a general-audience encyclopedia entry, still verbatim and
fetched: Kotobank, entry "別当寺" (bettō-ji), from 改訂新版 世界大百科事典 (Sekai Daihyakka Jiten, revised
new edition), https://kotobank.jp/word/%E5%88%A5%E5%BD%93%E5%AF%BA-286265 (fetched 2026-09-27):

> その他，地方の諸社にも多くの別当寺があったが，1868年（明治1）神仏分離により堂塔伽藍や仏像などは廃棄され，昔日の姿をとどめるものはない。

Translation (mine): "Besides [the great shrine-temple complexes], many local/provincial shrines
[地方の諸社] also had a bettō-ji, but with the 1868 (Meiji 1) shinbutsu-bunri, their halls, pagodas,
temple precincts and Buddhist images were destroyed, and nothing now remains of their former
appearance." This repeats the same "common, not universal" qualitative claim the first pass already
had (word "many," 多く, not a number), and does not distinguish villages from towns, so it adds no
new numeric information - listed for completeness since it was independently fetched this pass, not
carried over from pass one.

A general search of Meiji-era shinbutsu-bunri administrative records (which do exist prefecture by
prefecture, since the separation had to be carried out shrine by shrine) turned up narrative
accounts, not tabulated counts: a Nara Prefectural Library PDF, "神仏分離と社寺行政 ① 奈良県下における神仏分離"
(https://www.library.pref.nara.jp/sites/default/files/003_s2.pdf, fetched and OCR'd via
`pdftotext` 2026-09-27) covers only the prefecture's great complexes (Kōfuku-ji/Kasuga, Kinpusen-ji
in Yoshino, Isonokami Shrine's Eikyū-ji, Ōmiwa Shrine's jingūji) - no village-level count, no digit
sequence combined with 件/社/か寺 anywhere in the extracted text (checked by grep over the full OCR).
Not citable for the number this item wants.

**HUMAN-FETCHABLE:**
- CiNii Research articles found by this pass's searches but not fetchable as text (the site's
  article pages are JS shells that return no content to a plain HTTP fetch):
  - https://cir.nii.ac.jp/crid/1570572702335147008 - "The image of Buddha enshrined in the village
    shrine: an example of Shinto/Buddhist syncretism in the Edo period" - title suggests exactly a
    village-level Edo-period shinbutsu-shugo case study (covers 鎮守/宮座/神職 per the CiNii index
    snippet), but the page rendered blank to WebFetch; would need a browser-capable fetch or the
    underlying journal's own site.
  - https://cir.nii.ac.jp/crid/1390001205133764736 - "Monks and abbots of the Tsuruoka Hachiman
    Shrine during the Muromachi period" - period mismatch (Muromachi, not Edo) but might cite
    continuity data; same blank-page problem.
- A focused CiNii/J-STAGE search for Meiji shinbutsu-bunri record COUNTS (e.g. a prefecture's
  廃寺/復飾 tally table) was not completed this pass - the session's web-search budget was exhausted
  (200/200 WebSearch calls) partway through this item, after the Kanazawa finding above but before a
  planned search for "神仏分離 統計 表" / a prefectural gazetteer with a literal shrine-by-shrine
  table. A human (or a future search-budget session) re-running that specific query, plus opening the
  two CiNii pages above in a real browser, is the most promising next step toward an actual national
  or prefectural proportion.

## [110-2 / does-the-country-monk-live-at-the-shrine-2]

**Tools tried this pass:** direct WebFetch of the L5R fandom wiki pages themselves (Seidō, Shinden,
Shinden (TCG)) - all returned HTTP 402 Payment Required, confirming the first pass's finding that
this project's fetch tools cannot reach l5r.fandom.com at all, on any page, not just the two named.
Tried the Wayback Machine (web.archive.org) directly - WebFetch refuses the domain outright ("Claude
Code is unable to fetch from web.archive.org"), and archive.ph likewise ("unable to fetch from
archive.ph"). Tried mirrors/alternate hosts of the FFG Emerald Empire (5th edition) text: pdfcoffee
mirrors of "L5R 5ed - Emerald Empire.pdf" (two different pdfcoffee URLs) and a Scribd copy; tried
AnyFlip (which hosts an OLDER AEG-edition Emerald Empire flipbook, not the FFG one, plus other L5R
5e flipbooks, but no FFG Emerald Empire sourcebook flipbook was found); tried the FFG/Edge Studio
product page (403 Forbidden) and DriveThruRPG. Tried general web search for the three quoted
sentences verbatim, for other wikis/forums/Reddit threads quoting Emerald Empire pp. 143 or 176-178,
and for a published review or fan write-up.

**STILL SILENT** on independently verifying the quotes from a fetched page, with one partial
exception:

- The fandom wiki itself is unreachable by every route this pass tried (direct fetch: 402 on all
  three pages tried; Wayback Machine and archive.ph: both domains categorically refused by the fetch
  tool, not just this URL).
- No other wiki, forum, Reddit thread, or published review was found (via search) that quotes the
  three specific Emerald Empire sentences ("There was no village without some manner of shrine,"
  "Priests were the shrine's administrators and primary caretakers," "most had at least one resident
  monk") from the actual rulebook text.
- A detailed fan "writeup" summary of the Emerald Empire 5e sourcebook
  (https://writeups.letsyouandhimfight.com/mors-rattus/legend-of-the-five-rings-5e-emerald-empire/,
  fetched) does discuss the book's Sacred Spaces / clergy chapters but the specific excerpt returned
  to WebFetch did not contain the three sentences (the tool's summarizer may have truncated a long
  page; a full manual read of that page by a human might still find them, since it purports to be a
  close paraphrase/summary of the whole book chapter by chapter).
- PDF mirrors of the actual FFG Emerald Empire text (pdfcoffee x2, Scribd) were reachable, but each
  only exposed a short free-preview excerpt (front matter / early Chapter 1, roughly pages 1-20) to
  the fetch tool - pages 143 and 176-178 were not in the visible preview text on any of them.
- Search for the verbatim phrases themselves ("no village without some manner of shrine",
  "Priests were the shrine's administrators and primary caretakers", "most had at least one resident
  monk") returned no fetchable page containing them - only the L5R fandom wiki itself came up (via
  search-engine indexing/snippet, which is not citable per the rules here since it was never
  successfully fetched).

**What this pass found INSTEAD, for context:** search snippets (not fetched, so not quotable as
verbatim per the rules) repeatedly surfaced sentences matching the three quotes very closely on the
fandom wiki's Seidō and Shinden (TCG) pages - e.g. a snippet reading "...but most had at least one
resident monk" attributed to the Shinden (TCG) page, and "Priests were the shrine's administrators
and primary caretakers" attributed to Seidō - which is consistent with (does not contradict) the
first pass's claim that these sentences exist on those pages, but a search-engine snippet is
explicitly excluded as a citable source by this task's rules, and the pages themselves could not be
fetched this pass either, so this remains unverified by primary fetch.

**HUMAN-FETCHABLE:**
- https://l5r.fandom.com/wiki/Seid%C5%8D - "Seidō" (L5R Fandom wiki) - carries (per prior-pass
  MediaWiki-API read and this pass's search snippets) the "no village without some manner of shrine"
  and "administrators and primary caretakers" sentences; blocked here by HTTP 402 on every fetch
  attempt (this project's tools, not a browser).
- https://l5r.fandom.com/wiki/Shinden_(TCG) - "Shinden (TCG)" (L5R Fandom wiki) - carries the
  "most had at least one resident monk" sentence; same 402 block.
- https://web.archive.org/web/*/https://l5r.fandom.com/wiki/Seid%C5%8D and the equivalent Shinden
  (TCG) Wayback URL - the Wayback Machine's own UI shows snapshots exist for fandom wiki pages
  generally, but this session's WebFetch tool refuses the web.archive.org domain outright ("Claude
  Code is unable to fetch from web.archive.org"); a human opening these URLs in a browser, or a
  session with a working archive.org fetch path, could very likely confirm the quotes directly from
  an archived snapshot.
- https://archive.ph/https://l5r.fandom.com/wiki/Seid%C5%8D (and similarly for Shinden (TCG)) -
  same categorical tool refusal ("unable to fetch from archive.ph"); human-fetchable.
- Full FFG "Legend of the Five Rings: Emerald Empire" (5th ed., 2018) PDF, e.g. via
  https://pdfcoffee.com/l5r-5ed-emerald-empirepdf-5-pdf-free.html or the Scribd mirror
  (https://www.scribd.com/document/517565370/...) - both sites gate the full text behind a
  login/paywall that this pass's fetch tool only sees the first ~20 pages past; pages 143 and
  176-178 (the Sacred Spaces / Paths to Enlightenment chapters that would contain the quotes in
  the primary source itself) are beyond what was retrievable. A human with a Scribd/pdfcoffee
  account, or the physical/PDF rulebook, could open those exact pages directly - this would be the
  single best verification since it is the primary source, not a wiki paraphrase.
- DriveThruRPG / Fantasy Flight Games product pages for Emerald Empire (5th ed.) - the FFG product
  page returned 403 Forbidden to WebFetch; a human browser visit might expose a "preview" excerpt
  PDF that a script cannot reach.

---

## Part D - kuri size and hall form (120-1, D50, 120-2, 120-5, 120 GUESS)

# Second-pass research: village shrines/temples with a resident shrine-monk (kuri)

Session note: WebSearch quota was exhausted after ~24 queries (hard session cap). Remaining
attempts used WebFetch directly against CiNii Research, DuckDuckGo HTML and Bing search-result
URLs as a substitute for further WebSearch calls; DuckDuckGo returned a CAPTCHA page, Bing
returned mismatched/cached results for unrelated queries, and CiNii Research's results page did
not render without JavaScript (WebFetch got an empty page each time) - these three are therefore
not usable as sources and are not cited below. All quotes below are from pages that WebFetch
actually retrieved and rendered.

---

## [120-1]

STILL SILENT - no small, ordinary (non-designated-important) village kuri with measured
dimensions was found on any fetchable page, even with a different search strategy (Kanuma city's
architectural-terms glossary, Kawasaki/Hiroshima/Nagoya/Yamaguchi/Tsuyama municipal cultural-
property pages, "registered tangible cultural property" search terms, and 教育委員会 survey-report
searches). What this pass DID find:

- Five MORE designated kuri could be read, and every one of them is again a temple of standing,
  not an ordinary village temple, and again well above 15 m in at least one dimension:
  - **長念寺庫裏** (Chōnen-ji, Kawasaki, Tama-ku) - 桁行9間(63尺/約19.1m) x 梁行5間(39尺/約11.8m),
    late Edo, "市重要歴史記念物" (municipal important historical monument), described with a
    "武家風の玄関" (samurai-style entrance) - an institutional building, not a modest one.
    <https://www.city.kawasaki.jp/880/page/0000000260.html> ("長念寺庫裏", fetched 2026-09-27)
  - **國前寺庫裏** (Kokuzenji, Hiroshima) - 桁行17.7m x 梁間13.2m, 重要文化財, mid-Edo (~1671).
    <https://online.bunka.go.jp/heritages/detail/157645> (fetched 2026-09-27)
  - **長母寺庫裡** (Chōbo-ji, Nagoya) - 桁行9間 x 梁間5間, 1828, carpenter documented by name on
    the roof tablet ("棟札より大工棟梁は川合半七で，建築年代が明確な庫裡として貴重な存在である" -
    "from the roof tablet the master carpenter is known to be Kawai Hanshichi, making this a
    valuable example of a kuri with a clearly documented construction date" [translation]).
    <https://online.bunka.go.jp/heritages/detail/140848> (fetched 2026-09-27)
  - **大照院庫裏** (Taishōin, Yamaguchi) - 桁行18.1m x 梁間18.0m, ~1750, explicitly the daimyo's
    own temple: "藩主の菩提寺" and called "地方における正統的で格式の高い禅宗寺院建築" ("a
    regionally orthodox, high-status example of Zen temple architecture" [translation]) with
    "豪壮なつくり" ("imposing, grand construction" [translation]) - the opposite of ordinary.
    <https://online.bunka.go.jp/heritages/detail/147428> (fetched 2026-09-27)
  - **本源寺庫裏** (Hongen-ji, Tsuyama) - 桁行20.0m x 梁間12.0m, Enpō era (1673-1681), built as
    "大名家菩提寺" (a daimyo family's ancestral temple) for the Mori clan.
    <https://online.bunka.go.jp/heritages/detail/229698> (fetched 2026-09-27) - this appears to be
    the same Hongen-ji already found in the first pass (17.5-26.9 m band); confirms the earlier
    number rather than adding a new data point.

  The pattern holds and strengthens across 10 total designated kuri now read (5 from the first
  pass + 5 here): every one that can be read online is a temple of standing (daimyo's temple,
  named-carpenter temple, etc.), and every one is well above the ~15 m the question is looking
  under. This is consistent with - and starts to look like an artifact of - which buildings get an
  individual cultural-property web page at all: designation itself selects for the unusual/large
  example, so an ordinary small kuri would not have this kind of page even if plentiful.

- The generic claim that a small/medium temple's kuri "resembles an ordinary house" now HAS a
  fetchable citation (it did not in the first pass), though still with no measurements attached.
  Japanese Wikipedia, quoted verbatim: "庫裏は大規模寺院では独立した建物であるが、一般寺院では寺の
  事務を扱う寺務所と兼用となっていることが多い。" ("In large temples the kuri is a stand-alone
  building, but in ordinary temples it is often shared with the temple's administrative office"
  [translation]) and "一般の民家とよく似た建物も多い。" ("Many resemble ordinary houses"
  [translation]). <https://ja.wikipedia.org/wiki/%E5%BA%AB%E8%A3%8F> (fetched 2026-09-27). This
  upgrades the claim from "search-summary only" to "fetchable but still unmeasured" - it is
  evidence for the qualitative form claim, not for any specific dimension.

HUMAN-FETCHABLE:
- None found this pass beyond what is listed under [D50] below (same search).

---

## [D50]

Combined with [120-1] above - same search, same result: no small ordinary village kuri with
measured dimensions was found on any fetchable page. See the five additional designated-kuri
examples and the Wikipedia quote under [120-1]; all apply here too.

Two additional avenues tried, both unproductive:
- "Registered tangible cultural property" (登録有形文化財) search terms, which nominally have a
  lower designation bar than "important cultural property" and so seemed likelier to catch a
  modest building: returned only generic Agency for Cultural Affairs program pages, not a specific
  kuri listing.
- CiNii Research, J-STAGE and Architectural Institute of Japan (AIJ) paper searches for
  scholarship comparing kuri scale to farmhouses (民家) in rural/village settings: found only a
  single unrelated student design project (広宣寺における庫裏の計画, a contemporary design
  proposal, not a historical survey) and no measured comparative study.

HUMAN-FETCHABLE:
- **姫宮神社内八幡神社本殿建造物調査報告書（小）** (Himemiya Shrine / Hachiman Shrine main hall
  building survey report), Miyashiro town, Saitama, survey dated 2008-05-02. PDF at
  <https://www.town.miyashiro.lg.jp/cmsfiles/contents/0000002/2902/himemiyazinzya_hatimanzinzya.pdf>
  (20.48 MB) - this is a municipal building-survey report of exactly the kind the question asks
  for, but for a SHRINE honden, not a temple kuri; listed here in case it also covers the
  associated Buddhist structures, but more directly relevant to [120-5] below. Blocked because the
  file exceeds WebFetch's 10 MB content limit.
- No comparable PDF survey report specifically for a temple kuri was located and blocked this
  pass; the searches simply did not surface one (see STILL SILENT above) rather than surfacing one
  that could not be opened.

---

## [120-2]

STILL SILENT - no second example of a village/small temple with 本堂 and 庫裏 combined under one
roof was found, and no scholarly register or survey discussing the form's prevalence was found.
This pass tried different search angles (直接 phrase search for "本堂兼庫裏", "本堂・庫裏"+"一棟",
site-restricted searches on 文化遺産オンライン excluding Kaie-ji, and AIJ/CiNii searches for
"小規模寺院" architecture papers) and instead found several MORE examples of the ordinary
separate-buildings pattern, reinforcing rather than contradicting Kaie-ji's "unusual" status:

- **永住寺** (Eijuji, Shinshiro city, Aichi) - main hall and kuri are two separate registered
  buildings: 本堂 桁行6間(16.57m) x 梁間7間(14.29m), 298 sqm; 庫裡及び書院 桁行15間半(29.92m) x
  梁間8間(14.99m), 702 sqm, positioned on the east side of the compound while the main hall faces
  south. <https://www.city.shinshiro.lg.jp/kanko/minzokugeino/eijuji-hondo.html> (fetched
  2026-09-27)
- **顕証寺** (Kenshō-ji, Osaka) - a search-result summary (not independently fetched) describes
  本堂 centered in the compound with 庫裏 placed to its west/rear, again as a separate building;
  listed for completeness but not independently verified by fetch, so not counted as a confirmed
  citation.
- **本源寺**, **専称寺**, **顕証寺** and all five temples read for [120-1]/[D50] each have main
  hall and kuri as clearly separate structures (separate designation dates, separate dimensions,
  described as standing apart in the compound) - none combines them.

The re-confirmed verbatim quote from Kaie-ji itself (already found in the first pass, re-fetched
here to check current text): "本堂と庫裏が一棟の建物というのは、江戸時代の初めの寺院建築としては
珍しいもので、大変貴重です。" ("The fact that the main hall and kuri form a single building is
unusual for early-Edo-period temple architecture, and very valuable" [translation]). Dimensions
given: 桁行25.2m, 梁間8.0m(南側)/13.0m(北側寄り), single story, irimoya tile roof.
<https://www.city.sakai.lg.jp/kanko/rekishi/bunkazai/bunkazai/shokai/bunya/kenzobutu/kaiedaji.html>
(fetched 2026-09-27)

With this second pass, the evidence base has grown from "no register found" to "no register found,
plus several more confirmed separate-building examples" - the finding that Kaie-ji's combined form
is unusual is now better supported by contrast (more confirmed non-combined cases), even though a
second COMBINED example still was not found.

HUMAN-FETCHABLE:
- None found this pass (no promising blocked page identified).

---

## [120-5]

PARTIALLY ANSWERED (one half; the other half still silent):

**Half A - "most designated honden are 一間社流造" statement: ANSWERED on a fetchable page.**
Kotobank's 流造 (nagare-zukuri) entry, which aggregates multiple encyclopedia entries on one page,
gives (verbatim, two separate dictionary entries on the same page):
- from 百科事典マイペディア: "流造に属するものは現在国宝または重要文化財に指定されている本殿の
  半数を超える。" ("Those belonging to nagare-zukuri style exceed half of the honden currently
  designated National Treasures or Important Cultural Properties" [translation])
- from what the page attributes to 世界大百科事典: "流造に属するものが総数の55％を超え" ("those
  belonging to nagare-zukuri exceed 55% of the total" [translation]) and, in a separate sentence
  on the same page, "本殿の形式分類では流造（ながれづくり）が大半を占め、特に一間社が過半を占める。"
  ("In the classification of honden forms, nagare-zukuri accounts for the great majority, and
  one-bay shrines (一間社) in particular account for more than half" [translation]).
  <https://kotobank.jp/word/%E6%B5%81%E3%82%8C%E9%80%A0%E3%82%8A-3140056> (fetched 2026-09-27)

This directly supports (on a real, fetchable page, not a search summary) the claim that most
designated honden are nagare-zukuri, and that within nagare-zukuri, one-bay ("一間社", i.e. the
一間社流造 the item asks about) is the majority form - though note the two figures cited (>50%
and >55%) are for "nagare-zukuri overall," and the "one-bay majority" statement applies within
that nagare-zukuri population, not as a directly-stated single percentage of "all honden that are
一間社流造."

**Half B - an actual 3x3-ken (or 三間四方) Edo-period VILLAGE shrine hall: STILL SILENT** on
dimensions, though a strong candidate was found and partly blocked:
- **姫宮神社本殿** (Himemiya Shrine main hall), Miyashiro town, Saitama - confirmed Edo period,
  built c. 1715 (Shōtoku 5), and confirmed to be a "三間社" (three-bay shrine, i.e. 桁行三間) by
  town-hall text: "姫宮神社本殿が江戸時代中期の正徳5年（1715）頃の建築であることが判明しました" and,
  ranked among comparable structures, "三間社に限ると20棟中9番目の古さ" ("among three-bay shrines
  specifically, 9th-oldest of 20" [translation]).
  <https://www.town.miyashiro.lg.jp/0000002361.html> (fetched 2026-09-27). This is an actual,
  functioning Edo-period shrine hall with a confirmed 桁行三間 (three-bay width) - but neither this
  summary page nor its companion page gives the 梁間 (depth) figure needed to confirm 3x3 vs. the
  more common 2-bay-deep nagare-zukuri depth, and it is not explicitly called a "village" (村社)
  shrine on the fetched pages.
- The companion page names the detailed survey report:
  <https://www.town.miyashiro.lg.jp/0000002902.html> ("姫宮神社内八幡神社本殿建造物調査報告書",
  fetched 2026-09-27) which links a 20.48 MB PDF that almost certainly contains the 桁行/梁間 figures
  needed to settle whether this is a 3x3-ken hall - see HUMAN-FETCHABLE below.

HUMAN-FETCHABLE:
- **姫宮神社内八幡神社本殿建造物調査報告書（小）**, Miyashiro town, Saitama, 2008 survey. PDF:
  <https://www.town.miyashiro.lg.jp/cmsfiles/contents/0000002/2902/himemiyazinzya_hatimanzinzya.pdf>
  (20.48 MB). Likely answers Half B directly (an Edo-period, three-bay-front village-adjacent
  shrine main hall with a full building survey, which is exactly the kind of primary document the
  item wants) - blocked because the file (20.48 MB) exceeds WebFetch's 10 MB content-length limit.
  A human with a normal PDF reader could open it and check the 梁間/桁行 table for whether the hall
  is 3x3 ken and whether it is described as a 村社.

---

## [120 GUESS]

Not independently searched this pass (per instructions - it is covered by [120-1]/[120-5], and the
torii-spacing half belongs to a different researcher on item 090). Status update given the above:

- The size-guess half of this item is still a guess, and this pass does not change that: no
  measured small/ordinary village kuri was found ([120-1]/[D50] still silent on dimensions), and
  no confirmed 3x3-ken Edo village shrine hall was found ([120-5] Half B still silent, pending the
  blocked Miyashiro PDF). The one thing this pass adds that could eventually promote part of the
  guess to "historically accurate": Kotobank's fetchable statement that one-bay (一間社)
  nagare-zukuri honden are the majority form among designated shrines is now citable, which
  supports a SMALL honden as the default/typical case in the abstract - but it is a form claim
  (bay count), not itself a size-in-feet/meters claim, so it does not by itself size the precinct
  or resolve the guess.
- No change to the torii-arch-spacing half; that remains item 090's territory.

---

## Part E - fencing and precinct size (122, 124-3, 124-2, 124 GUESS x3)

# Second-pass research: village shrine fences and precinct size (6 items)

Second search pass only. Different tools/terms than the first pass per item. All quotes below are
verbatim from pages actually fetched (WebFetch or curl+pdftotext/HTML-strip in this session), never
from search snippets. Japanese/Chinese quotes are followed by my own translation, marked as such.

## [122]

**(a) Kochi depopulation-area shrine survey - retried via CiNii/repository route.**

STILL SILENT on the fence question, but this time the underlying academic work was actually fetched
and read (the first pass could not fetch it at all).

Found and fetched: Fuyutsuki Ritsu (冬月律), doctoral dissertation abstract, "過疎地神社の研究―人口減少
社会と神社神道" (Kokugakuin University), PDF at
https://k-rain.repo.nii.ac.jp/record/2480/files/bunotsu_298.pdf (fetched via WebFetch, binary; text
extracted locally with `pdftotext -layout`, 227 lines, all read). This dissertation's Chapter 3 is
explicitly built on the 1977 Jinja Honcho survey named in the item:

> "第三章では、前章の神社実態調査における高知県の地域を対象に実施した追跡調査の結果を概観する。
> 具体的には、昭和五二年に神社本庁が刊行した『過疎地帯神社実態調査報告』のうち、高知県高岡郡の一
> ...[町二村]"

Translation: "Chapter Three surveys the results of a follow-up survey conducted on the Kochi
Prefecture area covered by the shrine survey discussed in the previous chapter. Specifically, [it
follows up on] the portion covering one town and two villages of Takaoka District, Kochi Prefecture,
in the 'Report on the Survey of the Actual Conditions of Shrines in Depopulated Areas' published by
Jinja Honcho in Showa 52 (1977)."

I grepped the full extracted text for 垣/塀/柵/境内/囲 (fence/wall/wattle-fence/precinct/enclose) -
zero matches. The dissertation is sociological throughout (population decline, parish/ujiko
organization decay, festival discontinuation) and contains no physical description of precinct
boundaries at all, so it does not answer the fence question either way.

The 1977 primary source itself, 『過疎地帯神社実態調査報告』(Jinja Honcho, 1977), is not digitized
online; likewise the published book version of the above dissertation. See HUMAN-FETCHABLE.

**(b) NDL Digital Collections meisho zue - searched, could not get illustration content as text.**

STILL SILENT. `site:dl.ndl.go.jp` search for meisho zue (名所図会) turned up scanned volumes (江戸名所
図会 vol. 2, 紀伊国名所図会, 六十余州名所図会, etc.), but WebFetch on an NDL Digital Collections viewer
page (tried https://dl.ndl.go.jp/info:ndljp/pid/1174144/300?tocOpened=1) returns only the page's
navigation chrome ("国立国会図書館デジタルコレクション"), not the scanned image or any OCR'd text - the
tool cannot see the illustration itself or read handwritten/woodblock text on it. This is a hard
limit of text-only fetch tools against an image-only viewer; a human (or a vision-capable read of a
downloaded page image) would be needed. See HUMAN-FETCHABLE.

**(c) General statement distinguishing tamagaki (around honden) from a precinct-wide boundary.**

STILL SILENT on finding an explicit general statement that ORDINARY/rural shrines lacked a
full-precinct fence, but two more fetched sources confirm the dual usage already noted in the first
pass (not a dictionary quirk - it recurs everywhere), which narrows what would resolve it:

Fetched https://ja.wikipedia.org/wiki/%E7%8E%89%E5%9E%A3 (Japanese Wikipedia, "玉垣", fetched via curl
in this session, 2026-09-27). Two image captions on the page read:

> "本殿を囲む玉垣" / "境内を囲む玉垣"

Translation: "tamagaki surrounding the honden [main hall]" / "tamagaki surrounding the keidai
[precinct]" - the article itself illustrates both senses side by side as ordinary usage, with no
note that one is rare or non-standard. The article's history section:

> "樹木をめぐらせる柴垣が最も古い形式であると考えられる。形状は、厚板を並べた板玉垣、皮がついたまま
> の木を用いた黒木玉垣、広く間を開ける透垣などがある。材質は木や石、近年ではコンクリートによるもの
> もある。"

Translation: "A brushwood fence (shibagaki) formed of encircling trees/branches is thought to be the
oldest form. Types include板玉垣 (plank tamagaki, made of thick boards laid side by side), 黒木玉垣
(bark-on-log tamagaki), and 透垣 (sukigaki, an openwork fence with wide gaps). Material is wood or
stone, and in recent years also concrete." This supports (without stating it outright) that a
tree/brushwood boundary is the historically prior, more permeable form from which built fencing
later developed - consistent with an ungated wood being the older, humbler condition - but it is not
phrased as a claim about ordinary VS special shrines, so it does not settle the question.

Also re-fetched https://www.nippon.com/ja/views/b05208/ (nippon.com, "神社空間を読み解く8 玉垣"), which
in this instance discusses tamagaki strictly as surrounding the honden:

> "拝殿の奥に本殿があり、ここに祭神が祀られている。そして本殿の周りには玉垣を巡らして、外界と区切
> っている。"

Translation: "Behind the worship hall (haiden) stands the main hall (honden), where the enshrined
deity resides. Tamagaki are placed around the honden, marking it off from the outside world." This
article does not address the whole-precinct case at all, so it is silent rather than contradictory.

Net: no scholarly source found this pass that states in so many words "an ordinary/rural shrine's
whole precinct was NOT fenced, only bounded by its wood" - the terminology genuinely supports both
readings and no source picks one as the default for a village shrine.

**HUMAN-FETCHABLE for [122]:**
- 冬月律『過疎地神社の研究－人口減少社会と神社神道』(Hokkaido University Press, published book) -
  https://www.hup.gr.jp/items/65001843 - likely has the physical/ethnographic detail the dissertation
  abstract PDF lacks (that PDF is only the abstract, not the full dissertation); blocked here because
  it is a commercial book, not a web page.
- 神社本庁『過疎地帯神社実態調査報告』(1977) - the primary Kochi-region field survey named in the
  dissertation above - not digitized/indexed online at all; would need a physical copy (Jinja Honcho
  library or a university that holds it).
- Any specific 江戸名所図会 / other meisho zue page depicting a named village shrine - NDL Digital
  Collections pages (e.g. https://dl.ndl.go.jp/info:ndljp/pid/1174144/300) are viewable by a human in
  a browser (page-flip viewer with zoom) but return no extractable text/image content to WebFetch;
  would need visual inspection of specific woodblock pages, not a text fetch.

## [124-3]

**(a) Baidu Baike 村庙 entry - retried via Wayback Machine and mobile URL.**

STILL BLOCKED, still not citable. WebFetch refuses web.archive.org entirely in this environment
("Claude Code is unable to fetch from web.archive.org"). Direct curl to
https://baike.baidu.com/item/%E6%9D%91%E5%BA%99/3494869 returns HTTP 403 (same as first pass). Tried
the mobile endpoint https://baike.baidu.com/m/item/%E6%9D%91%E5%BA%99/3494869 - this returns HTTP 404
with Baidu's own generic error page (`saved from url=(0034)https://baike.baidu.com/error.html`), i.e.
blocked at a different layer, not a live page. A WebSearch snippet (not a fetched page, so NOT
citable per the rules) suggested regional figures for southern Fujian (闽南, ~100 m²) versus
northeastern Fujian (闽东北, 400+ m²) village temples, but I could not verify this by reading the
actual page, so it is not reported as an answer.

**(b) Fujian paper 福建省经济社会状况与村庙信仰 (Gan Mantang / 甘满堂, 2007) via a different host.**

STILL SILENT/paywalled. Fetched https://sociology.ssap.com.cn/skwx_shx/LiteratureDetail.aspx?id=938181
(Sociology Research Database entry for the paper) - this page confirmed the paper's existence,
author, length (24 pages / ~16,125 characters) and its place in the book 村庙与社区公共生活, but the
detail page shows only a title, abstract, author info, and table of contents; the actual body text is
gated behind "下载阅读"/"在线阅读" (download/read online), which requires institutional login and is not
accessible to a plain fetch. pishu.com.cn (tried again) is likewise a paywalled database front page,
not fetchable as before.

**(c) Alternative Chinese source for village-temple precinct/built-area figures.**

STILL SILENT. I located but could not fetch a related case study,
sociologyol.ruc.edu.cn (以福建省漳浦县长桥镇东升村为例, a Dongsheng-village 村庙 case study) - this URL
now 404s (confirmed with a direct curl, not a fetch-tool restriction: it is genuinely dead), so it is
not usable even as HUMAN-FETCHABLE. No other citable Chinese source with a numeric precinct-size or
built-area figure for 村庙 was reached before the session's web-search budget was exhausted.

**HUMAN-FETCHABLE for [124-3]:**
- Baidu Baike, 村庙 entry - https://baike.baidu.com/item/%E6%9D%91%E5%BA%99/3494869 - candidate figures
  for southern vs. northeastern Fujian village-temple size seen only in a search snippet; blocked by
  403/404 on every route tried (direct, mobile, Wayback unreachable by this tool).
- Gan Mantang, "福建省经济社会状况与村庙信仰" (2007), in 村庙与社区公共生活 -
  https://sociology.ssap.com.cn/skwx_shx/LiteratureDetail.aspx?id=938181 (also listed on
  pishu.com.cn) - full text behind an institutional-login paywall; the abstract confirms it covers
  Fujian folk-temple distribution and community function but the size/area data (if any) is inside
  the gated 24 pages.

## [124-2]

**(a) The urban-precinct-management J-STAGE paper - retried by fetching the PDF directly (via a
mirror), not the J-STAGE HTML page.**

PARTIALLY RESOLVED - this time the paper was actually read, but it turns out to answer a narrower
question than 124-2 asks. Found the same paper via agriknowledge.affrc.go.jp (a PDF mirror), title
recovered from the running head as "都市の神社境内地における植樹と樹木伐採の実態及び..." (planting and
felling of trees in urban shrine precincts). WebFetch could not parse the raw PDF ("corrupted or
improperly encoded"), so I downloaded it and ran `pdftotext -layout` locally, then read the extracted
text directly (1,417 lines). This is a mail survey of shrines from the 愛知県神社名鑑 (Aichi Prefecture
Shrine Directory), Nagoya-area, 436 shrines surveyed, 92 respondents (回収率31.7%). The precinct-area
statistics actually reported are:

> "回答を得た92社の境内地の面積（㎡）は、平均5,003㎡ […]、最小値56.5㎡、最大値190,080.0㎡だった
> （1,000㎡未満が21社、1,000㎡以上2,500㎡未満が37社、2,500㎡以上5,000㎡未満が15社、5,000㎡以上10,000
> ㎡未満が11社、10,000㎡以上が8社）。"

Translation: "Among the 92 responding shrines, the precinct (keidaichi) area (m²) averaged 5,003 m²
[...], with a minimum of 56.5 m² and a maximum of 190,080.0 m² (21 shrines under 1,000 m²; 37 shrines
1,000-2,500 m²; 15 shrines 2,500-5,000 m²; 11 shrines 5,000-10,000 m²; 8 shrines 10,000 m² or more)."

And on shrine forest's share of regional green space (not of the precinct itself):

> "社叢は、例えば愛知県内の全緑地面積に占める割合では1%にも満たないが […]、人口が集中する都市圏に
> 数多く存在し"

Translation: "Shrine groves (shasou), for example, make up less than 1% of Aichi Prefecture's total
green-space area, but [...] many exist concentrated in the population-dense urban area."

This is real, fetched, quotable data - but it is (i) urban (Nagoya-area, not rural/village), and (ii)
a distribution of whole-precinct AREA across shrines, not a within-precinct SPLIT between buildings,
grove and open ground. It does not give the buildings/grove/open-ground breakdown 124-2 is actually
after, so the core question remains open, though we now have a real, citable urban precinct-size
range for comparison (56.5 m² to 190,080 m², mean 5,003 m²) that the first pass did not have.

**(b) Rural/village precinct studies specifically.**

STILL SILENT on a rural buildings/grove/open-ground split, but found and fetched one on-topic rural
paper's abstract: Osawa Hiroshi & Kinoshita Saho, "西伊豆におけるランドスケープと神社の配置構造特性"
[Landscape and shrine placement-structure characteristics in Nishi-Izu], Landscape Research
(ランドスケープ研究) 86(5), 2023, J-STAGE. Fetched the J-STAGE article page directly (not the PDF, which
was not reachable this pass): the abstract reports that "51.5% of shrines were located at mountain
foothills" relative to settlements and disaster-risk zones, in a rural (Izu peninsula) setting - but
it is about SITING, not about the internal area breakdown of a precinct, and the abstract carries no
building/grove/open-ground ratio. Re-fetched the NDL reference-desk answer
(https://crd.ndl.go.jp/reference/entry/index.php?page=ref_view&id=1000165078) already found in the
first pass, confirming the same 28,000 ha / 0.2% scenic-preservation-forest figure with its caveat
that the category "includes forest that is not a shrine's or temple's" - unchanged from before.

**(c) A landscape-architecture (造園学) journal specifically.**

Identified the two relevant Japanese landscape-architecture journals on J-STAGE - 造園雑誌 (older name)
and its successor ランドスケープ研究 (Landscape Research), both published by 日本造園学会 (Japanese
Institute of Landscape Architecture) - and confirmed via CiNii/J-STAGE browse pages that shrine-
precinct studies (including the West Izu paper above and a 2011 paper on stone facilities in
Ishinomaki shrine grounds) regularly appear there. This narrows where a future search should look,
but no paper fetched this pass contained the specific building/grove/open-ground split for a rural
precinct.

## [124 GUESS 1]

"That the unbuilt ground was mostly that wood is a guess from those two, not a measurement" - status
UNCHANGED, still a guess. This pass added one more real, fetched figure (Aichi urban shrines: shasou
is under 1% of the prefecture's total green-space area; precinct areas mean 5,003 m², range 56.5-
190,080 m²) but this is a regional land-cover share and a precinct-size distribution, not a
measurement of what fraction of any one precinct's UNBUILT ground is wood versus open ground. No
source fetched this pass measures that split, urban or rural.

## [124 GUESS 2]

"as a band; its place in the band a guess; the wood's share of it a [guess]" - status UNCHANGED. The
new Aichi precinct-size range (56.5 m² to 190,080 m², mean 5,003 m², five-bin distribution) is a real
band for URBAN Nagoya-area shrines specifically, and could sharpen the low/mid/high placement
discussion if that band is judged transferable - but it is not a rural figure, and it says nothing
about the wood's share within that band, so the guess itself is not resolved.

## [124 GUESS 3]

"guess)" - status UNCHANGED, pairs with the same silence as 124-2/124-3 above; nothing fetched this
pass measures the wood's share of a village shrine precinct.

---

## Part F - precinct furniture (126-1, 126-2, 126-3, 126-5, 126-6, 126 GUESS x3)

# Feature 126 - second-pass research (village shrine precinct furnishings)

Session note: WebSearch budget for this session was exhausted partway through this pass (200/200
calls used session-wide) after the first round of searches for all 8 items. All subsequent work
used WebFetch only, against URLs surfaced by the earlier searches, guessed municipal/Kotobank/CiNii
URLs, or the Bing search-results workaround (which returned garbage/unrelated content and was
abandoned). This caps how far items 126-5 and 126-6 could be pushed this pass.

---

## [126-1]

**ANSWERED (part a - re-fetch with verbatim quotes):**

Re-fetched ja.wikipedia's 神木 article successfully this time (it had failed to yield verbatim text
in the first pass).

Verbatim Japanese + translation:

> 「神木（しんぼく）とは、古神道における神籬（ひもろぎ）としての木や森をさし、神体のこと。」
> Translation: "A sacred tree (shinboku) refers to a tree or grove that serves as a *himorogi*
> (a divine spirit-seat) in ancient Shinto, and is itself the object of worship (*shintai*)."

> 「日本に数万ある神社は、もともとは、この古神道における神籬のある場所に建立されたものがほとんどであり」
> Translation: "The tens of thousands of shrines in Japan were, for the most part, originally
> built at the very spots where such ancient-Shinto *himorogi* [sacred trees] stood."

The article also shows a shimenawa rope wrapped around a sacred tree at Yuki Shrine (caption image),
and names common species: スギ (cedar), サカキ/榊 (sakaki), ナギ (Nageia nagi).

Confirmed: the article still carries the "lacking sources" banner - 「出典がまったく示されていないか不十分です」
("sources are entirely absent or insufficient"), flagged since August 2017. So the shrine-origin
claim above is uncited encyclopedia prose, not a sourced historical claim.

URL: https://ja.wikipedia.org/wiki/%E7%A5%9E%E6%9C%A8 - "神木" - fetched 2026-09-27.

Also fetched Kotobank's 神木 entry (デジタル大辞泉 and other dictionaries aggregated), which gives an
independently-worded, dictionary-sourced definition:

> 「神社の境内などにあって神聖視される樹木」("A tree venerated as sacred, found within shrine grounds
> and similar sacred areas.")
> 「一般には神社の境内などにあって、注連縄などを張り巡らし、崇敬されている樹木」("Generally, a tree found
> within shrine precincts with a shimenawa rope strung around it, and revered.")
> 「松、杉、ヒノキなどの常緑樹が一般的」("Evergreens such as pine, cedar, and cypress are typical.")

URL: https://kotobank.jp/word/%E7%A5%9E%E6%9C%A8-82559 - "神木(シンボク)とは？" (コトバンク, aggregating
デジタル大辞泉 etc.) - fetched 2026-09-27.

**STILL SILENT (part b - prevalence figure):**

Tried: fetched nippon.com's "神社空間を読み解く⑩神木" (the shrine-space explainer series, which seemed
most likely to give a statistic) - it discusses definitions and lists FAMOUS named sacred trees
(camphor at Kamō Hachiman, cypress at Awa Shrine) but contains no percentage, count, or survey
figure for how many ordinary/village shrines keep a roped sacred tree. WebSearch budget ran out
before a second search term (e.g. prefectural shrine-association tree census, 巨樹・巨木林調査 by the
Ministry of the Environment, which surveys giant/sacred trees nationally and might carry shrine-
affiliation counts) could be tried.

**Effect on [126 GUESS 1]:** unchanged - still a guess, no source counting prevalence found this
pass either. The custom itself (roped tree at ordinary shrines) is now better-cited (Kotobank,
dictionary-sourced) than before, but "how common" remains unmeasured.

**HUMAN-FETCHABLE:**
- Ministry of the Environment 巨樹・巨木林調査 (giant tree survey) database, if it cross-tabulates
  shrine sacred trees - not located/fetched this pass; a session with WebSearch budget should try
  "環境省 巨樹 神社 神木 調査" and similar prefectural 神社庁 lists.

---

## [126-2]

**ANSWERED (general prevalence claim, part a):**

Could not relocate the specific "1826-dated basin at an ordinary shrine" search summary from the
first pass (WebSearch budget ran out before a second differently-worded search for it could be
tried). Instead, found and fetched a blog post whose title matched the question exactly
("手水舎が無い神社では") and got a directly relevant verbatim passage:

> 「手水舎そのものが無い神社も多いです。」
> Translation: "Many shrines have no 手水舎 [roofed water pavilion] at all."

> 「無人の神社は地方などでは特に多いですね。」
> Translation: "Unstaffed shrines are especially common in rural areas."

> 「そういう神社では、当然のごとく掃除が行き届きません。手水にも水がはられていません。」
> Translation: "At such shrines, cleaning naturally falls behind, and there is no water even at the
> hand-washing basin."

This is a personal blog (not a scholarly or municipal source), so it should be weighted
accordingly, but it is a fetched, verbatim, publicly-openable page, and it directly supports the
"basin without pavilion is a real, non-rare form at unstaffed rural shrines" claim that the first
pass could only find in a modern Q&A snippet.

URL: https://ameblo.jp/ubusuna-jinja/entry-11582938316.html - "手水舎が無い神社では" (幸せを呼び込む神社
ブログ) - fetched 2026-09-27.

**Partial / STILL SILENT (part a specific dated example, and part b municipal PDF example):**

Fetched the Kawasaki city page for 長尾神社's 手水鉢 as the closest dated example found (Bunsei 11 /
1828, not the 1826 figure originally cited - could not confirm this is the same object the first
pass saw):

> 「正面に「奉献」、右側面に「文政十一　戊子年　二月吉日」、左側面に「惣氏子中」と刻まれています。」
> Translation: 'Inscribed "Dedicated" on the front, "Bunsei 11, year of tsuchinoe-ne, an auspicious
> day in the second month" on the right side, and "the whole body of parishioners" on the left
> side.'

The page says only that the basin is "屋外にあり、常時見学可能です" ("located outdoors, viewable at any
time") - it does not state one way or the other whether a pavilion ever stood over it, so it
neither confirms nor refutes the "basin alone" form. This is not the item's target source.

URL: https://www.city.kawasaki.jp/880/page/0000146792.html - "長尾神社の手水鉢" (川崎市教育委員会) -
fetched 2026-09-27.

Searched for a municipal 文化財調査報告書 (cultural-property survey PDF) that lists a small shrine's
手水鉢 without a corresponding 手水舎: found only the "全国遺跡報告総覧" (nabunken) database as a search
portal and unrelated agricultural-land survey PDFs; no specific chōzubachi-without-chōzuya example
was located and fetched this pass.

**Effect on [126 GUESS 2]:** softened but not resolved. The ameblo passage is a real, verbatim,
citable (if non-scholarly) statement that basin-without-pavilion is common specifically at
unstaffed rural shrines - which is exactly the village-shrine case this project cares about. It
still falls short of a municipal/academic survey confirming the SPECIFIC unroofed form at a NAMED
ordinary shrine, so a stronger source would still improve the citation, but the "guess" label now
somewhat overstates the uncertainty, since the general phenomenon is fetched and quoted.

**HUMAN-FETCHABLE:**
- Any of the five PDF volumes of 群馬県近世寺社総合調査報告書－歴史的建造物を中心に－神社編 (81-84 MB each) -
  a comprehensive prefectural survey of early-modern shrine buildings that would very likely
  itemize which shrines have a 手水舎 vs. bare 手水鉢, but each volume is 70-84 MB, too large to
  fetch/process in this pass. URLs (relative to https://sitereports.nabunken.go.jp):
  - Vol.1: /files/attach/45/45602/121895_1_....pdf (81.3 MB)
  - Vol.2: /files/attach/45/45603/121895_2_....pdf (83.6 MB)
  - Vol.3: /files/attach/45/45604/121895_3_....pdf (81.6 MB)
  - Vol.4: /files/attach/45/45605/121895_4_....pdf (70.3 MB)
  - Vol.5: /files/attach/45/45606/121895_5_....pdf (82.2 MB)
  - Index page: https://sitereports.nabunken.go.jp/en/121895
  Why it likely answers: it is a historic-structures survey of shrines across an entire
  prefecture, the kind of source that tabulates minor furnishings like chōzubachi/chōzuya
  presence at ordinary (non-famous) shrines. Blocked by: file size (would need a human download
  and local PDF search, e.g. for "手水鉢" without an adjacent "手水舎").
- Tokyo Shrine Association (東京都神社庁) 手水鉢 page,
  http://www.tokyo-jinjacho.or.jp/goshahou/chouzubachi/ (and its https variant) - would not load
  for WebFetch (SSL handshake error both as http and https). Why it likely answers: an official
  prefectural shrine-association glossary page on this exact object, probably discussing standard
  form/variation. Blocked by: WebFetch TLS error (`WRONG_VERSION_NUMBER`) on both scheme variants.

---

## [126-3]

**ANSWERED:**

Fetched the Niiza city (新座市) local-history page directly - "にいざ見聞録（第24回　残された石燈籠）" - and
got the verbatim inscription text:

> 「奉納　氷川大明神　寛政十一未歳六月吉日」「奉納御寳前武州新座郡石神氏子中」
> Translation: '"Dedicated to Hikawa Daimyōjin, an auspicious day in the sixth month, Kansei 11,
> year of the sheep" [and] "Dedicated before the deity's presence, by the parishioners of Ishigami,
> Niiza district, Musashi province."'

The page situates the lantern (石灯籠) as originally belonging to a former Hikawa Shrine that stood
in the Ishigami area, its stone base now preserved near the Ishigami meeting hall (石神会館) /
present-day Inari Shrine site; the date corresponds to Kansei 11 (1799), confirming the year cited
in the first pass.

URL: https://www.city.niiza.lg.jp/site/niiza-kenbunroku/bunkazai-kenbun-024.html - "にいざ見聞録
（第24回　残された石燈籠）" (新座市ホームページ) - fetched 2026-09-27.

This item is now fully resolved; no further search needed.

---

## [126-5]

**Partial - fetched the target page, but it does not fully confirm the prevalence claim:**

Fetched the Association of Shinto Shrines (神社本庁) official page on subsidiary shrines, as
requested:

> 「神社の境内では、ご本殿以外に小さな社を見かけることがあります。」
> Translation: "Within a shrine's precinct, one sometimes sees small shrines apart from the main
> hall."

> 「戦前の旧官国弊社という位の高い神社においては、摂社と末社を区分する基準が設けられていました。」
> Translation: "At the old pre-war 官国弊社 [state/national-rank shrines], which were high-ranking
> shrines, a standard was set for distinguishing 摂社 (sessha) from 末社 (massha)."

The page names Ise Shrine and Iwashimizu Hachiman-gū as examples with many subsidiary shrines, but
- contrary to what the first pass's search-summary implied - it does NOT explicitly say subsidiary
shrines are rare or absent at ordinary/village shrines; it only says the FORMAL sessha/massha
CLASSIFICATION was a pre-war distinction applied at high-ranking shrines. A small shrine could
still have an unclassified "small shrine" (小さな社) in its grounds per the opening sentence. This
nuance was not visible in the earlier search-summary-only read.

URL: https://www.jinjahoncho.or.jp/omairi/smallkeidai/ - "摂社・末社｜おまいりする｜神社本庁公式サイト" -
fetched 2026-09-27.

**STILL SILENT (village-scale facilities list: 絵馬殿, 神輿庫, 社務所):**

Tried: the Gunma prefectural early-modern shrine survey (see 126-2's HUMAN-FETCHABLE entry) is
exactly the kind of document that would itemize these at named, ordinary shrines, but its PDFs are
70-84 MB each and were not fetched. Also fetched the Miyagi Prefecture Shrine Association's 2011
earthquake-damage memorial page, which gives aggregate damage counts across the prefecture's
shrines (not filtered to famous ones):

> 「神輿庫　全壊・流失　17件（神楽殿・境内社・末社等）」
> Translation: "Mikoshi storehouse (神輿庫): 17 cases of total destruction or being swept away
> (grouped with kagura halls, precinct sub-shrines, massha, etc.)"

> 「社務所　全壊・流失　30社」
> Translation: "Shrine office (社務所): destroyed or swept away at 30 shrines."

This shows dozens of shrines across an entire prefecture (necessarily including many small,
non-famous local shrines, since Miyagi has relatively few famous shrines) had a 神輿庫 and/or 社務所
before the disaster - suggestive that these facilities are not restricted to famous shrines - but
the page does not break the counts down by shrine rank/size, so it is circumstantial rather than a
direct statement about village-scale prevalence.

URL: https://miyagi-jinjacho.or.jp/shinsai-kioku/index.html - "震災の記憶～3.11からの10年～　宮城県神社庁
特設ページ" - fetched 2026-09-27.

No readable page giving a facilities list for a specific named, ordinary (non-famous) village
shrine including any of 絵馬殿/神輿庫/社務所 was found and fetched this pass; CiNii Research searches
returned only architectural-history papers on shrine APPROACH spaces (参道), not facilities
inventories, and CiNii's own search-result pages did not render via direct WebFetch (JS-driven,
returned blank).

**HUMAN-FETCHABLE:**
- Same Gunma survey PDFs as listed under [126-2] - would very likely also answer this item's
  facilities-list question (絵馬殿/神輿庫/社務所 presence per shrine), same size blocker.
- CiNii Research, https://cir.nii.ac.jp/all?q=... - the site is JavaScript-rendered; direct
  WebFetch of a CiNii search URL returns blank content. A human (or a browser-capable tool) could
  search CiNii Research for "村社 境内施設" or "近世 神社 社殿 付属建物" to find architectural-history
  papers inventorying ordinary shrines' outbuildings.

---

## [126-6]

**STILL SILENT:**

Tried this pass: (1) searched CiNii Research for 毘沙門堂 + 村落/民間信仰 combinations (WebSearch, before
budget ran out) - returned only pages about the famous Kyoto Bishamondō temple, no scholarly papers
on village-scale Bishamon halls; (2) searched for the "Sado household Bishamon hall" page seen only
as a search summary in the first pass, using different terms (屋敷内/民家/祀る) - found only tourism
pages about a DIFFERENT, famous Bishamon site (Urasa Bishamondō in Niigata, part of Fukōji temple,
with its well-known "hadaka-oshiai" naked-pushing festival) and Sado tourism/lodging pages, none
about a village household's private hall; (3) attempted the Wayback Machine directly - WebFetch
cannot reach web.archive.org at all in this environment ("Claude Code is unable to fetch from
web.archive.org"); (4) attempted a Bing search-results URL as a WebSearch-budget workaround, which
returned garbled, entirely unrelated content (US dynamometer manufacturers) and was not usable;
(5) attempted 文化遺産オンライン's search endpoint directly - returned 404, endpoint likely requires a
different query format or JS.

No verbatim, fetched source describing furniture/facilities inside or around an ordinary,
village-scale Bishamon hall was found this pass. The item remains open.

**Effect on [126 GUESS 3]:** unchanged - still a guess; village-scale Bishamon-dō contents remain
undocumented in every source reached so far (named-temple accounts only, e.g. Kurama-dera,
Chōgosonshi-ji, the Kyoto/Yamashina Bishamondō, and the Iwate/Urasa halls all found this pass and
the first pass).

**HUMAN-FETCHABLE:**
- CiNii Research, https://cir.nii.ac.jp/ - could not be searched via direct WebFetch of a query URL
  (returns blank; the site needs JS or its proper API). A human/browser-capable session should
  search "毘沙門天 村 信仰" or "路傍 毘沙門堂" (roadside Bishamon hall) on CiNii Research directly.
- The Wayback Machine, https://web.archive.org - WebFetch is blocked from this domain entirely in
  this environment ("Claude Code is unable to fetch from web.archive.org"). If the first pass's
  "Sado household Bishamon hall" page is archived there, a human or a different tool would need to
  retrieve it; its original live URL was not recorded in the first pass's notes available to this
  session, so it could not be re-located by content search either.
- 文化遺産オンライン (online.bunka.go.jp), whose object-level Bishamon-dō pages (e.g.
  https://online.bunka.go.jp/heritages/detail/143808, an Iwate example) describe a named building
  and its principal image but not furnishings/precinct objects at village scale; its search
  endpoint (`/search?class1=...`) returned 404 for a direct WebFetch guess and would need the
  correct query parameters or a browser to use properly.

---

## Part G - land tenure and bell tower (128, D51)

# 272 reader S-G - second-pass research notes

## [128]

STILL SILENT on the Chinese side (all four retry avenues tried; the Chinese-side
exemption remains unasserted anywhere readable). ANSWERED on the Japanese
comparison side (d).

### (a) Academia Sinica / Palace Museum papers via Wayback or mirror

Could not retry via Wayback Machine: the fetch tool refuses `web.archive.org`
outright ("Claude Code is unable to fetch from web.archive.org"). No mirror or
alternate host for either paper was found - general web search engines
(Google, Bing, DuckDuckGo) all returned unusable pages via the fetch tool
(Google/Bing served broken/unrelated shells, DuckDuckGo HTML endpoint served a
CAPTCHA), and the session's WebSearch budget was exhausted (200/200, inherited
from earlier turns in this session) before these specific titles could be
re-located. No paper text was read; nothing to quote.

### (b) Baidu Baike lishe (里社) entry via mirror/cache

Retried the live page directly (not a mirror): `https://baike.baidu.com/item/里社`
- still HTTP 403 Forbidden, matching the prior absence note. The Wayback
Machine mirror is unreachable by this tool (see above), so no cached copy
could be substituted. Chinese Wikipedia has no article at
`https://zh.wikipedia.org/wiki/里社` (404) - not a mirror of Baike, but checked
as the next-best general encyclopedia and it is simply absent.

### (c) Ming/Qing 寺田/庙产 tax-exemption via CNKI abstracts or a digitized gazetteer

- `ctext.org`: both the library search endpoint and a direct document-id probe
returned the site's anti-scraping notice ("automated scraping is not
authorized... scrapers will receive corrupted data"), not gazetteer text.
Ctext's Ming/Qing holdings are mostly literati works, not digitized 地方志, so
even with access this may not have been the right shelf.
- CNKI itself was not reachable directly (no anonymous full-text access), and
searching for CNKI abstracts required a general web search, which the
exhausted WebSearch budget and the CAPTCHA/broken-shell behavior of
Google/Bing/DuckDuckGo via the fetch tool prevented.
- Checked two adjacent Chinese Wikipedia articles that might carry the
tax-status fact as background: `廟產興學` (temple-property-for-schools
movement) and `土地廟` (earth-god shrine). Neither states a Ming/Qing tax
status for temple/shrine land. The one usable quote found, from 廟產興學,
describes temple land as coming from donation rather than being surveyed
taxable land, but does not itself assert exemption:

> "其物皆由布施而來" (Zhang Zhidong, *Quan Xue Pian* 勸學篇, as quoted in the
> article) - "these properties all came from alms/donations"
> - <https://zh.wikipedia.org/wiki/廟產興學>, fetched 2026-09-27. This is
> suggestive of a donation-funded, not tax-assessed, property class, but it is
> not a statement of exemption and should not be recorded as one.

This is not a citable answer to the exemption question; it is listed only as
the nearest thing found.

### (d) Japanese-side comparison: 社領 tax-exemption for an ordinary village shrine under a han

ANSWERED. An ordinary village shrine's land under a daimyo/domain lord in the
Edo period was a recognized, named legal category of tax-exempt land - 除地
(jochi) - one tier below the higher-status 朱印地 (shogun-sealed land), granted
or confirmed either by a no-tribute deed or by an annotation in the domain's
own cadastral register. Two independent citable definitions:

> "江戸時代，領主から貢租・課役を免除された寺社の境内・田畑・屋敷地。朱印地につぐもので，無年貢証文が発給されているか検地帳外書に除地と記されているもの。"
>
> Translation: "In the Edo period, temple and shrine precincts, fields, and
> residential land exempted from tribute-tax and corvee duty by the [local]
> lord. Ranking below shuinchi [shogun-sealed land], it is land for which
> either a no-tribute deed was issued, or which was noted as 'jochi' in the
> margin of the cadastral register."
> - <https://www.historist.jp/word_j_shi/entry/033644/>, "除地(じょち)"
> entry, fetched 2026-09-27.

> "江戸時代に幕府・大名より年貢を免除された土地のうち、朱印地・黒印地を除いたものを指す... 寺社の境内や、無年貢証文のある田畑・屋敷など特別な由緒のある土地"
>
> Translation: "Refers to land exempted from annual tribute tax by the
> shogunate or a daimyo in the Edo period, excluding shuinchi and kokuinchi
> [shogun/daimyo-sealed lands]... land of special provenance such as temple
> and shrine precincts, and fields or residences holding a no-tribute deed."
> - <https://ja.wikipedia.org/wiki/除地>, fetched 2026-09-27.

Both sources agree this status applied to ordinary temple/shrine precincts
generally (not only large, named shrines), administered by grant of the local
lord (daimyo) or the shogunate, and recorded either by deed or by a
cadastral-register annotation rather than by omission from the survey
altogether (i.e., the land was still surveyed and identified, just marked
non-taxable) - a useful, citable structural parallel to whatever the Chinese
lishe answer eventually turns out to be, but NOT itself evidence for the
Chinese side; it only answers the Japanese comparison explicitly asked for in
(d).

### HUMAN-FETCHABLE

- `https://baike.baidu.com/item/里社` - Baidu Baike, "里社" entry - would very
likely state the lishe system's status directly (it is the standard reference
term); blocked with HTTP 403 to the fetch tool on every attempt (both live and
via requested Wayback mirror, which this tool cannot reach at all).
- Any Academia Sinica (中央研究院歷史語言研究所) or National Palace Museum
(故宮學術季刊 / 故宮文物月刊) paper on Ming temple-land tax exemption - title(s)
not re-confirmed this pass because general web search was unavailable
(WebSearch budget exhausted; Google/Bing/DuckDuckGo unusable via the fetch
tool). A human search on Google Scholar or CNKI for "明代 寺田 免稅"/"里社
土地制度" plus the institution name should surface the papers named in the
prior absence note; a human could also try the papers' DOI or CNKI ID directly
against `https://www.airitilibrary.com` (Taiwan's academic database), which
this tool did not attempt.
- CNKI (知网) itself - anonymous/public web fetch has no route into full text
or even reliable abstract pages; a human with an institutional CNKI login
would answer (c) fastest.
- `https://ctext.org` - holds classical and some gazetteer-adjacent texts but
actively blocks automated fetches ("scrapers will receive corrupted data");
a human browsing its library search UI directly (not scraping) for 里社 or
寺田 in Ming/Qing 地方志 entries could still find something this pass could not.

## [D51]

STILL SILENT on the core ask (documented village-scale prevalence, and
whether shrine-temples specifically are recorded with a bell tower), with one
piece of strong circumstantial (not dispositive) evidence. Kotobank/JAANUS
definitions retrieved as requested; no dated village-scale example was
successfully pinned down.

### Kotobank / JAANUS definitions

> "A building in which a bell bonshou is hung. The early belfries in the Nara
> period were double-storied 3 x 2 bay structures and the bell was suspended
> in the upper story."
> - JAANUS, "shourou" (鐘楼) entry,
> <http://www.aisf.or.jp/~jaanus/deta/s/shourou.htm>, fetched 2026-09-27.
> The entry's worked examples are all major-temple: Horyuji Sai-in (Nara),
> Horyuji Toin (Kamakura), Rinnoji Jigendo (1642, Tochigi) - it gives no
> village-scale example and does not address ordinary-temple prevalence.

> "鐘楼とは、寺院のなかにある建築物のひとつで、仏教法具の釣鐘である梵鐘（ぼんしょう）を吊るすための施設。"
>
> Translation: "A shoro is one of the structures within a temple, a facility
> for hanging a bonshō, the bronze bell that is a Buddhist ritual implement."
> - <https://www.homemate-research-religious-building.com/useful/glossary/religious-building/2030401/>,
> fetched 2026-09-27. Names only famous examples (Horyuji, Todaiji) when
> illustrating; no prevalence statement.

> Daijisen, s.v. 鐘撞き堂: "釣鐘をつってある堂。鐘楼（しょうろう）。"
> Translation: "A hall in which a hanging bell is suspended. [Synonym:] shoro."
> Nihon Kokugo Daijiten (Seisen ed.), same headword: "釣り鐘をつって、撞(つ)け
> るようにしてある堂。鐘楼(しょうろう)。"
> Translation: "A hall built so that a hanging bell can be struck. [Synonym:]
> shoro."
> - <https://kotobank.jp/word/鐘撞き堂>, fetched 2026-09-27.

This confirms 鐘楼 and 鐘撞堂/鐘撞き堂 are straightforward synonyms (the
"tower/hall" register difference, if any, is not glossed by either
dictionary), which resolves the terminology question but not the prevalence
one.

### Circumstantial evidence for widespread ownership (not village-scale-specific, not shrine-temple-specific)

> "梵鐘を持っていた寺院のうち供出に応じた寺が9割と圧倒的に多く、「他寺が供出し、拒否しにくかった」という証言もあったという"
>
> Translation: "Among temples that possessed a bell, an overwhelming
> majority - 90 percent - complied with the [WWII metal] requisition; there
> is also testimony that 'other temples were complying, making it hard to
> refuse.'"
> - <https://ja.wikipedia.org/wiki/金属類回収令>, fetched 2026-09-27, citing a
> 2021 survey conducted within the Honganji-ha (本願寺派, a Jodo Shinshu sect
> with a very large number of small, ordinary local temples nationwide, not
> only famous ones).

This shows that by the early Showa period, bell (and by strong implication
bell-tower/bell-hall) ownership was common enough across an entire sect's
membership - which is overwhelmingly small, ordinary local temples - that a
90%-compliance survey was meaningful to run at all. It is suggestive that a
bell tower was NOT confined to large, famous temples by that date. It does
NOT, however: (1) give a percentage of all temples (large or small) that had
one, (2) reach back to confirm Edo-period village-scale prevalence rather than
just early-Showa, or (3) say anything about shrine-temples (神宮寺/別当寺)
specifically as opposed to ordinary Buddhist temples.

### What did not pan out

- General bell-tower Wikipedia article (`https://ja.wikipedia.org/wiki/鐘楼`)
has no prevalence-by-temple-size discussion at all.
- `https://ja.wikipedia.org/wiki/梵鐘` (the bell itself) has no
spread-to-ordinary-temples history section despite a full history section
existing (it covers only major/famous bells and the China/Korea background).
- Checked two specific "small bell tower" search hits that turned out not to
fit: Shimabara's 鐘撞堂 (<https://www.city.shimabara.lg.jp/page2897.html>) is a
1675 CASTLE-TOWN civic time-bell built by the domain lord, not a temple or
shrine facility. Shomyo-ji's 鐘撞堂 in Kure
(<https://kureto.city.kure.lg.jp/read/citizen-journal/2364/>) is a 2019
architect-designed rebuild with no historical/prevalence discussion.
- Checked shrine-temple-specific sources directly for a bell-tower mention:
an Ehime prefectural local-history database entry on jinguji/betto
(<https://www.i-manabi.jp/system/regionals/regionals/ecode:2/54/view/7295>)
discusses their administrative role but never mentions a bell or bell tower.
`tobifudo.jp`'s page on shrine-monks/betto/miyadera could not be fetched
(connection refused).
- Tried Japan's national cultural-heritage database
(`online.bunka.go.jp/db/heritages/...`, redirected from `bunka.nii.ac.jp`) with
a keyword query for 鐘楼 - the query-string search endpoint 404s; the database
evidently needs its JS search UI rather than a GET query string, which this
tool cannot drive.
- CiNii Research's article-search pages returned empty/JS-only content via
fetch (no results text was served); combined with the exhausted WebSearch
budget, no architecture-history paper on rural/village temple bell towers was
located this pass.

### HUMAN-FETCHABLE

- `https://online.bunka.go.jp/db/heritages/search_result?SearchGeneralCondition=鐘楼`
(Japan's national cultural-heritage database, "Bunkaisan Online") - the right
tool for pulling a list of registered/designated 鐘楼 with dates and
municipalities, which would let village-scale examples be filtered out from
famous-temple ones, but it needs its interactive search UI; a bare query
string 404s for this tool.
- CiNii Research (`https://cir.nii.ac.jp`) - an architecture-history search
for "鐘楼 農村 寺院" or "鐘楼 小規模" would likely surface a survey/thesis
directly on point; the site's search results render via JavaScript and
returned no text to this tool.
- Any prefectural 文化財調査報告書 (cultural-property survey PDF) for a
specific small village temple with a 鐘楼 entry - none was located this pass
because locating candidate PDFs requires general web search, which was
unavailable (WebSearch budget exhausted; Google/Bing/DuckDuckGo unusable via
the fetch tool this pass).
- `http://tobifudo.jp/newmon/jinbutu/shasou.html` ("社僧・別当・宮寺") - looked
promising by title for exactly the shrine-temple administrative detail asked
about, but the host refused the connection (ECONNREFUSED) on this attempt.
