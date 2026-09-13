# Second pass, batch b1 - on-hand sources and agronomy (11 notes)

Reader: source-reader agent, 2026-09-12. One fetch attempt per host. Nothing cited that was not read.

| # | note | claim in one line | verdict |
|---|---|---|---|
| 1 | `vegetation.html` fn-4 | Fujian villages keep ~2 fengshui forests each (Xu, Qiu & Wang 2012, via Forests 2020) | **CITED** |
| 2 | `vegetation.html` fn-6 | no readable source counts a Chinese grove's trees | **STILL ABSENT** - confirmed against all five on-hand fengshui documents |
| 3 | `water.html` fn-48 | a distribution lateral is ~1 m wide | **CITED** (a Guangzhou farmland design, not the Jiangsu guideline) |
| 4 | `archetypes.html` fn-84 | 6:4 water-to-dike split; 0.4-0.6 ha ponds, 6-10 m dikes (Ruddle & Zhong) | **RETIRE THE NOTE** - every figure is already quoted from a readable page |
| 5 | `fields.html` fn-35 | village tanks command tens of hectares, well under 200 | **STILL ABSENT** - the national tank register has no command-area column |
| 6 | `fields.html` fn-82 | a village transplants together, on one schedule | **CITED IN PART** - the schedule and the 7-10 day window yes, the labor-exchange mechanism no |
| 7 | `fields.html` fn-86 | the ring nearest a market town is worked hardest | **CITED** (the fallow half stays unsourced) |
| 8 | `fields.html` fn-87 | dense near-city plain ~70-75% paddy, 1.5-2 farming households/ha | **STILL ABSENT** - one precise lead named (e-Stat 本地・けい畔 series) |
| 9 | `fields.html` fn-88 | a dry field beside a canal is surveyed TO the canal | **CITED IN PART** - the orthogonal grid yes, which frame is the parent no |
| 10 | `water.html` fn-73 | the crew re-digs the bend rather than the corner | **STILL ABSENT** - but a readable alignment maxim should replace the clause |
| 11 | `cities/river-cities.html` fn-18 | a moat wants STAGE, a canal wants FLOW; and the four other unsourced spans | **SPLIT**: (a) CITED for the engineered half, (b)(c)(d) STILL ABSENT; (c) is FOR THE GM (GB 50288) |

---

## 1. `vegetation.html` fn-4 - Fujian villages keep about two fengshui forests each

**CITED.** The passage is in the Forests 2020 paper itself, on its page 3, attributed there to
reference [40] = Xu, Qiu and Wang 2012. The last pass read the GM's downloaded copy for grove AREAS
(Table 1) and did not look at the study-site description, which is where the count sits.

Read from `/host-l7r-repo/academic-sources/forests-11-01286.pdf`, §3.1 "Study Sites", **page 3 of 15**,
verbatim:

> The strong influence of fengshui culture in this area can be demonstrated by the fact that most villages feature two fengshui forests on average and that 80.4% of the fengshui forests have not been damaged [40]. There are more village fengshui forests in the province's mountainous areas than in its plains and coastal areas, and these are mainly located near a villages' entrances, ancestral halls, and temples.

(The apostrophe in 「a villages' entrances」 is the paper's own; the em-dash-free wording above is
transcribed exactly. The sentence continues the paragraph that opens 「Fujian Province is located in
the south of China」.)

The paper's reference [40], verbatim from its reference list, page 15:

> Xu, F.; Qiu, E.F.; Wang, C. Tree species structure of Fengshui forest in Fujian Province. J. Jiangxi Agric. Univ. 2012, 34, 99-106.

**How it supports the claim:** this is the record's assertion word for word - the province-wide
average of two fengshui forests per village, reported by the Forests 2020 paper from Xu, Qiu and
Wang 2012 - and the same sentence independently carries the second half the record quotes elsewhere
in the same paragraph (「are mainly located near a villages' entrances, ancestral halls, and
temples」), so one footnote can serve both.

**Which URL to put on the footnote.** The publisher page is 403 to every fetcher this pass tried
(`https://www.mdpi.com/1999-4907/11/12/1286/pdf`, curl with a browser user agent, HTTP 403, 410-byte
HTML body). Unpaywall (`https://api.unpaywall.org/v2/10.3390/f11121286`) reports `is_oa: true` with
four OA locations:

| location | result |
|---|---|
| `https://www.mdpi.com/1999-4907/11/12/1286/pdf?version=1606712706` (publisher) | 403 to curl with a browser UA |
| `https://doaj.org/article/cc7401428b034b668bf6c243e2664196` (DOAJ) | metadata record, not fetched - DOAJ serves abstracts, not full text |
| `http://hdl.handle.net/20.500.12000/47505` (U. of the Ryukyus, handle) | not fetched - resolves to the record below |
| `https://u-ryukyu.repo.nii.ac.jp/records/2011293` (U. of the Ryukyus repository) | fetched, **HTTP 406**, 558-byte body |

The paper is genuinely gold open access (MDPI, CC BY), so a human browser reads it at the MDPI URL;
only the automated fetchers are refused. **Recommendation: cite
`https://www.mdpi.com/1999-4907/11/12/1286` with the passage above.** The 403 is a bot-block, not a
paywall, and the same journal's articles are already cited elsewhere in this record. If the project
insists on a URL that a *fetcher* can read, the Ryukyus repository record is the fallback to try
from a browser (`https://u-ryukyu.repo.nii.ac.jp/records/2011293`) - it is the co-author's
institutional deposit and Unpaywall lists it as a full-text location, but this agent could not
confirm the PDF link from it.

---

## 4. `archetypes.html` fn-84 - can the entry stop leaning on Ruddle & Zhong?

**Verdict: YES - fn-84 can be retired, and no figure is lost.** Every number the parenthetical
attributes to the monograph is already quoted, verbatim, from a page that this agent fetched and
read today. The monograph is not the carrier of anything in the entry; it is the ISIS page's own
reference [1].

**Who carries what.** All five footnote texts below are read from
`research/citations/archetypes.html` as they stand:

| figure in the entry | footnote | source | the quoted passage |
|---|---|---|---|
| the 6:4 water-to-dike area ratio | fn-32 | `fao-ac241e` | 「A 6-mu (0.4 ha) fish pond with 3.6 mu (0.24 ha) water area and 2.4 mu (0.16 ha) dike surface area.」 ... 「The water/ dike ratio is 6:4.」 |
| the 7:3 variant | fn-33 | `fao-ac241e` | 「the ratio of water surface and dikes can be reduced to 6:4 or 7:3. However, in actual practice, the ratio of water area to dike surface area is more complicated and generally, governed by traditional practice.」 |
| 1:1 where the worms alone feed the fish | fn-34 | `fao-ac241e` | 「According to the experience of farmers from Pearl River delta, each mu of mulberry plants can yield worm dregs, pupae and waste water to provide feeds and fertilizers sufficient for 1 mu of fish ponds. Hence, the ratio of areas of dike and water surface is 1:1.」 |
| the 3:7-to-4:6 split (水基比) | fn-83 | `gd-gazetteer-sangji` | 「桑基鱼塘基面和水面的"水基比"，大致为三七至四六开...」 |
| 「基六塘四」, the contested order | fn-39 | `cssn-sangji-yutang` | 「虽然今天在珠江三角洲已经寻找不到那种"基六塘四"的桑基鱼塘」 |
| **the 0.4-0.6 ha ponds and the 6-10 m dikes** | **fn-37** | **`isis-dykepond`** | **「Most ponds are rectangular, 0.4 to 0.6 ha in area and 2 to 3 m deep. The dykes are usually 6 to 10 m wide, and extend 0.5 to 1.0 m above the pond surface.」** |

The last row is the only one the monograph was ever invoked for, and it is a direct quotation of the
ISIS page, not of Ruddle & Zhong.

**Confirmed live today.** `https://www.i-sis.org.uk/DykePondSystem.php`, fetched with curl and a
browser user agent, HTTP 200, 28,576 bytes. The passage is on the page verbatim, in the paragraph
beginning 「The pond is the heart of the system.」:

> Most ponds are rectangular, 0.4 to 0.6 ha in area and 2 to 3 m deep. The dykes are usually 6 to 10 m wide, and extend 0.5 to 1.0 m above the pond surface.

The same page's reference list, also verbatim, shows where ISIS got them - so the record's provenance
remark is *accurate*, it is simply not load-bearing:

> Ruddle R and Zhong F. Integrated agriculture-aquaculture in South China. The dike-pond system of Zhujiang Delta, Cambridge University Press, Cambridge, 1988.

**What to do with the entry.** Drop the parenthetical clause 「carrying Ruddle & Zhong's figures -
the monograph itself has no publicly readable copy[84] -」 and let the `isis-dykepond` entry read
「(the 0.4-0.6 ha ponds and 6-10 m dikes)」 on fn-37 alone. fn-84 then has nothing to hang from and
goes with it. What is genuinely lost is nothing the map draws; what stays open is the
CONTRADICTED-order question already recorded in the entry's own HTML comment, for which Ruddle &
Zhong 1988 remains the authority if the GM ever wants it resolved - and that belongs in
`for-the-gm.md`, not in a footnote on a figure that three readable sources already carry.

*(The one on-hand candidate that might have added a further readable reading,
`/host-l7r-repo/academic-sources/Seeing from Above Observation of Contemporary Dike-Pond
Landscape.pdf`, is an image-only scan: `pdftotext` extracts 0 characters and `pdfinfo` returns
nothing. It carries no text layer to quote and has no public URL recorded here.)*

---

## 3. `water.html` fn-48 - a distribution lateral is about 1 m

**CITED, with a better source than the one the note was looking for.** The Jiangsu guideline turns
out NOT to carry canal widths by grade (see the negative finding below); an openly published
Guangzhou municipal farmland design does, as a schedule of built cross-sections, tier by tier - and
its lateral is 1.0 to 1.2 m.

URL: <http://nyncj.gz.gov.cn/attachment/8/8037/8037125/10854794.pdf> - 「2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿）」
(*Preliminary design report for the 2026 high-standard farmland improvement and upgrading
construction project, Conghua District, Guangzhou* - client 广州市农业农村局, the Conghua District
Bureau of Agriculture and Rural Affairs; designer 中联合创设计有限公司; dated 二〇二六年六月).
Fetched with curl and a browser user agent: **HTTP 200, 23,291,315 bytes, `application/pdf`**, text
layer intact.

**Passage A - the works schedule** (the 灌溉与排水工程 / 输配水工程 / 明渠 rows of the project
summary table, near the head of the report), verbatim:

> 斗渠          km         0.84      宽 1.2m×高 1.2m
> 斗渠          km         1.27      宽 1.0m×高 1.0m
> 农渠          km         1.41      宽 0.6m×高 0.6m
> 农渠          km         8.91      宽 0.4m×高 0.4m

English translation by this agent (original above kept as the checker's anchor):

> lateral (dou) canal   km   0.84   width 1.2 m x height 1.2 m
> lateral (dou) canal   km   1.27   width 1.0 m x height 1.0 m
> farm (nong) canal     km   1.41   width 0.6 m x height 0.6 m
> farm (nong) canal     km   8.91   width 0.4 m x height 0.4 m

**Passage B - the design clause that sets those sections** (§7.2.2, "灌溉渠道横断面设计"), verbatim:

> 本项目灌溉渠道采用矩形浆砌砖、浆砌石断面，净宽40～120mm ，净高400～1200mm ，侧墙厚度18～36cm，底板厚度10～15cm ... 各渠道断面尺寸如下：
> （1）整修农渠：设计底宽0.4m，设计渠深0.4m，侧墙厚度24cm ，底板厚度10cm，混凝土强度C25。
> （2）整修斗渠：设计底宽1.2m ，设计渠深1.2m ，侧墙厚度36cm，底板厚度15cm，混凝土强度C25，配构造钢筋。

English translation by this agent (original above kept as the checker's anchor): "The irrigation
canals of this project use a rectangular section of mortared brick or mortared stone, clear width
40 to 120 [the document's own typo for cm - the same numbers are 0.40 to 1.20 m everywhere else],
clear height 400 to 1200 mm, side-wall thickness 18 to 36 cm, floor-slab thickness 10 to 15 cm ...
The section dimensions of each canal are as follows: (1) Rehabilitated farm (nong) canal: design
bottom width 0.4 m, design canal depth 0.4 m, side-wall thickness 24 cm, floor slab 10 cm, concrete
grade C25. (2) Rehabilitated lateral (dou) canal: design bottom width 1.2 m, design canal depth
1.2 m, side-wall thickness 36 cm, floor slab 15 cm, concrete grade C25, with structural
reinforcement."

**Passage C - the same four sections as a table**, 表 7-2 「矩形灌溉渠道断面尺寸统计表」, 单位：m,
verbatim (columns: 渠道名称 / 施工纵坡 I / 糙率 n / 底宽 B(m) / 设计侧墙高 H墙(m)):

> 整修灌排渠Ⅰ     0.001             0.014       0.40    0.40
> 整修灌排渠Ⅱ     0.001             0.014       0.60    0.60
> 整修灌排渠Ⅲ     0.001             0.014       1.00    1.00
> 整修灌排渠Ⅳ     0.001             0.014       1.20    1.20

**How it supports the claim.** The record's ladder places a stroke by the grade it serves: 「a field
ditch watering one paddy ~0.3 m, a distribution lateral ~1 m (unsourced), a district main (yosui)
~5 m」. In the Chinese five-grade ladder the record itself quotes (干渠 / 支渠 / 斗渠 / 农渠 / 毛渠,
main / branch / lateral / farm / field), the **distribution lateral is the 斗渠**, and this project
builds its 斗渠 at **1.0 and 1.2 m** - the record's ~1 m, on the nose, measured off a built
schedule rather than assumed. The tier below it, 农渠, comes out at 0.4 and 0.6 m, which brackets
the record's ~0.3 m field ditch from above and is consistent with it (the record's 0.3 m tier is the
毛渠, one grade finer again, which this project does not build).

**The limits, stated.** This is a **modern, concrete- and masonry-lined** works schedule (2026,
rectangular mortared sections on a 1/2000 grade), not a premodern earthen channel; what it fixes is
the **grade ladder's proportions** - roughly 3:1 between successive tiers - rather than the material
or the construction. It is a district design report, not a national standard, and it declares itself
subordinate to the national standard the record originally wanted: it cites GB 50288-2018 by number
for its scour and siltation velocities (「根据《灌溉与排水工程技术规范》（GB 50288-2018），混凝土衬砌渠道的允许不冲流速小于8.0m/s，清水小型渠道不淤流速为0.3—0.5m/s。」 - English
translation by this agent: "According to the *Technical code for irrigation and drainage engineering*
(GB 50288-2018), the permissible non-scouring velocity of a concrete-lined canal is less than
8.0 m/s, and the non-silting velocity of a small clear-water canal is 0.3 to 0.5 m/s."). So it is a
readable application of GB 50288 in the same way T/JSSLKX 002-2021 is.

**The negative finding on T/JSSLKX 002-2021.** The Jiangsu guideline was re-fetched for this note -
<http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf>, curl with a browser user
agent, **HTTP 200, 622,748 bytes**, read in full - and it does **not** give canal widths by grade.
Its whole §9.3 「渠道断面设计」 is procedural (satisfy the design conveyance, keep the side slopes
stable, approach the hydraulically optimal section, calculate the grade), and the only two numbers
in it that touch a width are minima, not tier sizes:

> 9.3.7 斗渠、农渠岸顶宽度不宜小于 1.0m，渠道岸顶兼作交通道路时，其宽度应满足车辆通行要求。

English translation by this agent (original above kept as the checker's anchor): "The **bank-crest**
width of lateral (dou) and farm (nong) canals should not be less than 1.0 m; where a canal's bank
crest doubles as a traffic road, its width shall satisfy the requirements of vehicle passage."

> 9.4.3 ... 为便于建后运行管护，渠道底宽应不小于 0.3 m。

English translation by this agent (original above kept as the checker's anchor): "... so as to
facilitate operation and maintenance after construction, the canal bottom width shall be not less
than 0.3 m."

**Do not cite §9.3.7 for the lateral's width.** Its 1.0 m is the width of the **bank crest** (岸顶),
the earth you walk on beside the channel, not the channel - a coincidence of number that would read
as a match and is not one. §9.4.3's 0.3 m *is* a channel bottom width, and it is a floor for canals
of every grade, so it corroborates the record's ~0.3 m field-ditch tier as a minimum without fixing
any tier's typical size. The guideline's Appendix C, which the earlier pass may have hoped would
carry sections, is hydraulic calculation for **pressurized** systems (低压管道输水, 喷灌, 微灌) and
has no open-canal geometry at all.

---

## 6. `fields.html` fn-82 - a village transplants together, on one schedule

**CITED IN PART, and the part that fails is worth knowing.** A 1977 field survey of *customary*
transplanting across Wakayama Prefecture carries both halves of the record's picture - a hamlet-unit
communal transplanting whose whole schedule was settled in advance, and a transplanting window
narrow enough to put a district's basins at one growth stage - but it puts them in **different
zones**, and in the zone with the agreed schedule the window is the LONGEST, not the shortest.

URL: <https://www.jstage.jst.go.jp/article/jsfwr1966/1977/29/1977_29_24/_pdf/-char/en> - 小畑晃男
(Teruo Obata), 「和歌山県における慣行田植法の地域性とその成立要因に関する研究」 ("Studies on the
Traditional Transplanting Methods of Rice in Wakayama Prefecture"), *農作業研究 (Farm Work
Research)* 29: 24-29, 1977. Fetched with curl and a browser user agent: **HTTP 200, 834,972 bytes**,
free to all on J-Stage. It reports part of a **nationwide** survey of customary transplanting
practice carried out in 1975-76 (「1975年〜1976年の2ケ年にわたり，全国的に実施された慣行田植法に
関する調査結果の一部であり」).

*A note on the text, for the checker:* the J-Stage file is a **scan with an OCR text layer**, and the
OCR mangles a few characters (it renders な as 左, お as 夢, あ as め). Every passage below was
**confirmed against the rendered page image** at 200 dpi before it was transcribed, so what follows is
what is PRINTED, not what `pdftotext` returns. Where the journal's own typesetting is unusual - it
prints 「勢んな」 where modern Japanese would print 「盛んな」 - the page's spelling is kept.

**Passage A - the communal schedule, page 28, right column** (§4「作業組織」, (1)「共同作業」),
verbatim:

> 受けられ，所によっては，その年の田植に関するすべての作業スケジュールが事前に相談の上決定され，また，期間中の食事の献立までも決定していた所もあった。

English translation by this agent (original above kept as the checker's anchor): "... were found, and
in some places **the entire work schedule for that year's transplanting was settled in advance by
consultation**, and there were places that even settled the menu of the meals for the period."

**Passage B - who agrees it, page 28, right column**, verbatim:

> 紀中，紀南の山間避地といわれる地帯では，近隣共同意識が強く，各農家の経営規模に関係なく相互扶助の精神が旺盛で，20〜30戸にもおよぶ大型の共同作業（部落単位や垣内‑カイト‑5〜10戸が1ケ所に固まって家を造り，共同で扶助し合う生活の場，同族が多い。）が多数見受けられ

English translation by this agent (original above kept as the checker's anchor): "In the zones called
the mountain refuges of Kichū and Kinan, neighborly communal consciousness is strong and the spirit
of mutual aid is vigorous regardless of each farm household's operating scale, and large-scale
communal work reaching **20 to 30 households** (at the hamlet unit, or the *kaito* - five to ten
houses built together in one place, a living unit that supports one another communally, often of one
lineage) was found in great numbers."

**Passage C - the mountain zone's window, page 27, right column** (ロ「紀南・紀中の山間地帯」),
verbatim:

> 田植に関しては，部落単位（20〜30軒）で行う大型共同作業の勢んな地帯である。従って，田植期は6月上〜中旬が中心であるが，対象地域が広く，しかも，谷水を何時でも引けるため田植期間は長く，20日を超えることも少くない。

English translation by this agent (original above kept as the checker's anchor): "As to transplanting,
this is a zone where large-scale communal work carried out **at the hamlet unit (20 to 30
households)** is vigorous. Accordingly the transplanting season centers on the first to middle third
of June, but because the area concerned is wide and, moreover, **valley water can be drawn at any
time, the transplanting period is long, and not seldom exceeds 20 days.**"

**Passage D - the plains zone's window, page 27, right column** (ハ「紀中・紀北の平野地帯」),
verbatim:

> この地帯の田植期は，前作との関係から6月下旬（夏至中心）に集中し，適期が短かいため田植期間も7日〜10日と短かく，しかも面積が大きいため，共同作業は比較的少く雇用労働を主体とした田植作業が多い。

English translation by this agent (original above kept as the checker's anchor): "This zone's
transplanting season, on account of its relation to the preceding crop, **concentrates in the last
third of June (centered on the summer solstice), and because the suitable window is short the
transplanting period too is short, seven to ten days**; and because the areas are large, communal
work is comparatively little and transplanting carried out mainly with hired labor is common."

**What is supported and what is not.**

*Supported:* that a village transplants on ONE agreed schedule (Passage A, explicitly: the whole
year's transplanting schedule settled in advance by consultation), at the **hamlet unit of 20 to 30
households** (Passages B and C - which is also, incidentally, an independent attestation of the
project's hamlet size), and that the whole of a district's transplanting can fall inside **7 to 10
days** (Passage D), which is short enough for the record's conclusion - the basins are at one growth
stage at any moment - to follow.

*NOT supported, and mildly cut against:* the record's stated **mechanism**. It writes 「the water is
released on one schedule and the labor is exchanged between households - so at any moment its basins
are largely at a single growth stage」, i.e. communal water + exchanged labor -> one growth stage. In
this survey the two do not coincide. Where the labor is exchanged and the schedule agreed (the
mountain zone), **water is unconstrained and the window runs past 20 days**; where the window is 7 to
10 days (the plains), the paper attributes the concentration to **the preceding crop's calendar**
(前作との関係) and says communal work there is comparatively LITTLE. And the paper's account of *yui*
names the opposite of synchrony as its enabling condition - 「田植期の違いを利用して手伝いあうと
いった「ゆい」」 (English translation by this agent: "*yui*, in which they help one another by
**making use of the difference in transplanting dates**") - because households whose dates coincide
exactly cannot lend each other hands.

**The narrowing this suggests.** The record's *observable* claim survives and is now sourced: a
village's transplanting falls inside a window of a week to ten days where the calendar is tight, and
it is settled as one schedule for the whole hamlet. The *causal* clause should stop naming labor
exchange as the synchronizer - on this evidence exchanged labor is what a SPREAD of dates makes
possible - and should name the cropping calendar and the water regime instead, with the honest note
that the same survey found a 20-day-plus window where water was free at any hour. That is a better
sentence than the one it replaces, and it is one source rather than none.

**Limits, stated.** One prefecture, surveyed in 1975-76 for practice *remembered as customary*
(慣行) rather than observed in a premodern century; Wakayama is mountainous (山地の割合... 80%に
も達する) and its plains are small, so the plains zone here is a modest one. The survey is
nonetheless the Japanese record's own instrument for this question - it is a slice of a national
customary-practice survey - and it is free to read.

---

## 7. `fields.html` fn-86 - the ring nearest the town is worked hardest

**CITED.** An open-access article on the early-modern Edo/Tokyo night-soil trade quotes a
**premodern Japanese source** that states the intensity gradient directly, as a ladder of fertilizer
regimes by distance from the castle town.

URL: <http://journals.openedition.org/eue/1039> - Kayo Tajima, "The Marketing of Urban Human Waste in
the Early Modern Edo/Tokyo Metropolitan Area", *Environnement Urbain / Urban Environment*, Volume 1,
2007. Read in full from the GM's downloaded copy of the article PDF,
`/host-l7r-repo/academic-sources/eue-1039.pdf`.

**The passage** (§39; the article's translation of 土屋『鹿角春秋』(*Kōka Shunjū*) as quoted in
Watanabe 1983), verbatim:

> Within one ri [approximately 4 km] from Kanazawa in any direction they fertilize fields with urine and abundant manure. Within about three ri they use manure, rapeseed cake and dried sardine. Beyond four ri, manure, ash, dried sardine, and raw sardine are used. In remote areas they also use bushes and grasses (Translated by author. Tsuchiya, Kôka Shunjû quoted in Watanabe, 1983).

**The article's own reading of it** (§40), verbatim:

> From this writing we learn that farmers who lived near the city heavily relied on the use of urine. It also says that urine was the primary fertilizer for farmers within one ri from the city; every morning they brought vegetables to exchange for urban households' urine.

**And the mechanism that produces the gradient** (§38 and §43), verbatim:

> As a fertilizer, a very important property of human night soil is that it contains large amount of water and is heavy in weight. For this reason, the cost of transportation became a limiting factor for its use.

> With ground transportation, the cost of labor was critical; traveling to the city with farm products and bringing fertilizers back was a half day of work for someone in a village located 1.5 ri (5.9 km) from the city. In villages farther afield, it required a full day just to make a trip to carry 1-2 ka of night soil.

**How it supports the claim.** The record asserts 「the ring worked hardest is the one closest in」
around a town or county seat. This is that assertion as a *measured ladder in a premodern text*: the
innermost ring (within one ri, about 4 km) gets the heaviest and most labor-intensive fertilizer
regime there is - daily-collected urine plus abundant manure, fetched and paid for every morning -
the next ring (to about three ri) drops to manure and purchased cakes and dried fish, beyond four ri
the regime thins again, and 「in remote areas they also use bushes and grasses」, which is gathered
green manure, the cheapest input of all. The gradient is explicitly a **transport-cost** gradient
(§38, §43), which is the same mechanism the record's paragraph relies on, and it runs the direction
the record says it does - down, outward.

**What this does NOT support, stated plainly.** The record's sentence continues 「the labor-limited
fallow retreating to the far margins」. **No passage read here mentions fallow at all.** This source
establishes the intensity gradient and nothing about where fallow sits; the fallow clause remains
unsourced and should say so, or be dropped, rather than shelter under this footnote.

**Limits, stated.** The gradient is around **castle towns** (Kanazawa, and Edo) and is measured in
*fertilizer regime*, not in the share of ground cultivated; a county seat is smaller than Kanazawa,
so the ladder's distances are an upper bound rather than a scale to copy. The article is
open-access, but both of its hosts bot-gate an automated fetcher: `journals.openedition.org` answered
HTTP 200 with an "Anubis ... verifying that you're not a robot" interstitial (5,299 bytes), and the
Érudit mirror answered HTTP 200 with "Making sure you're not a bot!" (7,806 bytes). A human browser
reads it at the URL above; this agent read the same article from the GM's downloaded PDF, which is
the publisher's own file.

---

## 9. `fields.html` fn-88 - a dry parcel beside a canal is surveyed TO the canal

**CITED IN PART.** No source was found that states the record's sentence as such - "one edge runs
along the canal, the other perpendicular to it, running upslope". But the Jiangsu guideline states
the same geometry as three separate design rules that compose into it, and it states them for
irrigated **dry** land as well as paddy.

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> - T/JSSLKX 002-2021,
「小型農田水利工程規劃設計導則」 (*Guideline for the planning and design of small farmland water
conservancy works*, Jiangsu Society for Water Resources), §7.4 「田間渠道設計布置要求」. Fetched
with curl and a browser user agent, **HTTP 200, 622,748 bytes**, read in full. It declares itself
subordinate to the national standard GB 50288 (§9.1.6, and §7.6.4 requires canal works to conform
to GB 50288).

**Clause A - the grid is orthogonal**, §7.4.5, verbatim:

> 田间渠道可布置 2～3 级固定渠道，平原圩区上下级渠道宜相互垂直，丘陵山区结合山坡地形布置。

English translation by this agent (original above kept as the checker's anchor): "Field canals may be
laid out in two or three grades of fixed canal; **in plain polder districts the canals of successive
grades should be mutually perpendicular**, while in hilly and mountainous districts they are laid
out to suit the hill-slope terrain."

**Clause B - the parcel and the canal are set out from each other**, §7.4.3 and §7.4.9, verbatim:

> 7.4.3 田间渠道应结合水利设施、耕作田块、道路及自然界线确定 ...

> 7.4.9 末级固定渠道的适宜长度及控制的面积应根据耕作田块的长度确定，一般为 200m。

English translation by this agent (original above kept as the checker's anchor): "7.4.3 Field canals
shall be fixed **in combination with the water works, the cultivated field blocks, the roads and the
natural boundaries** ... 7.4.9 The suitable length of the last-grade fixed canal, and the area it
commands, **shall be determined according to the length of the cultivated field block**, generally
200 m."

**Clause C - and the direction of watering runs down the fall**, §7.4.8, verbatim:

> 田间渠道的灌溉方向应与田面纵坡方向一致，灌溉水田、水浇地末级渠道纵坡宜为 1/1000～1/2000。

English translation by this agent (original above kept as the checker's anchor): "The irrigation
direction of a field canal shall **coincide with the direction of the field surface's longitudinal
slope**; the longitudinal grade of the last-grade canal irrigating **paddy fields and irrigated dry
land** should be 1/1000 to 1/2000."

**How they support the claim.** Taken together these are the record's rule in its constituent parts:
the canal grid is orthogonal to itself on flat ground (A); the parcel grid and the canal grid are
set out from one another, the canal's length taken from the block's length (B); and the watering
direction - which is the direction the plot's long axis runs, since water is led along it - **runs
down the field's fall** (C). A parcel laid out that way against a canal along its edge comes out a
rectangle with one side on the canal and the other down the slope, which is what the record draws.
Clause C's 「水浇地」 (irrigated dry land, as opposed to 水田, paddy) is the record's DRY field
explicitly.

**What is NOT supported.** The guideline never says the parcel's frame is taken **from the canal
rather than from the surrounding fields** - the record's actual point, which it reached after
finding plots sheared into parallelograms because they had been built in the paddy's frame. The
guideline makes the canal grid and the field grid one grid without saying which one is the parent.
It also treats a plain polder district; on 丘陵山区 (hills and mountains) clause A explicitly hands
the alignment back to the terrain, which is a limit worth carrying, since a head-race running
diagonally to the fall - the case the record's paragraph is about - is exactly the terrain case.

**Limits, stated.** A 2021 provincial design guideline for modern consolidated farmland, not a
description of a premodern survey; the 200 m block length and the 1/1000-1/2000 grade are modern
machinery-era figures and should not be carried over as premodern numbers. What carries is the
ORTHOGONALITY rule, which is a consequence of gravity and of how a plot is watered rather than of
the machinery.

---

## 10. `water.html` fn-73 - the crew re-digs the bend rather than the corner

**STILL ABSENT on the sentence as written - but a readable standard states the underlying rule, and
the record would be better citing that.** No source was found that describes a maintenance crew's
choice between re-digging a bend and re-digging a corner. The assertion is a plausible inference
from the scour-and-silt half already cited at fn-72, and this pass could not find anyone who writes
it down.

**What a readable standard does say.** T/JSSLKX 002-2021 (fetched, HTTP 200, 622,748 bytes, read in
full), §7.4.1, verbatim:

> 田间渠道宜考虑有利于机械化生产，有利于田间管理的原则进行布置；平原圩区宜结合格田化布置，丘陵山区宜顺山坡地形，大弯就势，小弯取直。

English translation by this agent (original above kept as the checker's anchor): "Field canals should
be laid out on the principle of favoring mechanized production and favoring field management; in
plain polder districts they should be laid out in combination with the gridding of the fields, and
in hilly and mountainous districts they should **follow the hill-slope terrain: let the large bends
take the lie of the land, and straighten the small bends** (大弯就势，小弯取直)."

**How that bears on the record.** 「大弯就势，小弯取直」 is the standing Chinese canal-alignment
maxim, and it describes an alignment made of **sweeps and straights** - large curvature is accepted
and followed, small curvature is taken out - which is exactly the record's opening assertion
(「water turns on a SWEPT BEND and never on a mitered corner」) said from the design side. It does
not say anything about maintenance, and it does not mention a corner.

**Recommendation.** Replace the maintenance clause with the alignment maxim, footnoted to
T/JSSLKX 002-2021 §7.4.1, and let the paragraph read: a hand-dug ditch turns on a sweep because a
sharp corner scours outside and silts inside (fn-72), and because the alignment rule for an earthen
canal is to follow the large bends and straighten the small ones rather than to introduce a corner.
That is two sourced statements in place of one sourced and one not. If the GM wants the maintenance
claim itself kept, it should stay marked as a guess.

**What was searched, and what came back.**

| query | engine | outcome |
|---|---|---|
| 土水路 屈曲部 洗掘 内側 堆積 維持管理 浚渫 曲がり | search.yahoo.co.jp (curl) | returned only Japanese river-revetment and sabo design manuals (長野県 床固工の設計; 国交省中部地方整備局 護岸; JICE 河道計画検討の手引き) - all about a RIVER's bend, none about a dug ditch's maintenance; not fetched, since the record's fn-72 already cites the bend's scour-and-silt mechanics |
| earthen irrigation ditch bend curve scour outside deposition inside maintenance re-dig canal alignment avoid sharp corners | search.brave.com (curl, HTTP 200, 204,985 bytes) | eight results, all modern North American design standards or explainer pages: USDA NEH Part 624 Ch. 5 Drainage; USDA NRCS Irrigation Ditch Lining 428; USDA CA Irrigation Water Conveyance Ditch and Canal standard; Indiana DNR Ditch Relocation/Construction and Transitions; WisDOT FDM 13-30; theconstructor.org; engineeringoal.com "Curves in Irrigation Canals"; NZDL Irrigation Reference Manual Ch. 5. Not fetched: each is a design standard for a NEW channel, so at best it would restate the alignment rule the Jiangsu guideline already gives above in a non-East-Asian voice, and none of them is about a maintenance crew's practice, which is the unsourced clause |
| (documents already in hand) | - | T/JSSLKX 002-2021 read in full for 弯 / 转弯 / 半径 / 顺直 / 急弯 / 转角: the only alignment clause is §7.4.1 above, and there is no minimum bend radius for a canal in it. The Conghua design report carries the same maxim in the form 「放线应大弯随弯、小弯取直、分叉转弯自然」 but in its **road**-construction section (§8.3.5 道路工程施工), not its canal section, so it is not quoted for a ditch |

---

## 5. `fields.html` fn-35 - a village tank commands tens of hectares, well under 200

**STILL ABSENT.** No source was found that gives a typical range or an upper bound for the area a
traditional East Asian village tank commands. The Kunisaki case the record already has (5 systems,
50 ha, 11 farmers - about 10 ha per system) remains the only case read, so 「tens of hectares, well
under 200」 stays a GUESS. One useful negative was established, and it closes the most obvious route.

**The concrete negative: Japan's national tank register carries no command-area column.** MAFF
publishes the whole 農業用ため池データベース as nine spreadsheets at
<https://www.maff.go.jp/j/nousin/bousai/bousai_saigai/b_tameike/ichiran.html>. This agent downloaded
`tameike_ichiranR8_1.xlsx` (curl, **HTTP 200, 1,612,660 bytes**) and read its header row directly
from the workbook XML. The full column list is:

> 名称 / 都道府県 / 市区町村 / 町域名、番地 / 緯度 / 分 / 秒 / 経度 / 分2 / 秒2 / 堤高(m) / 堤頂長(m) / 総貯水量(千m3) / 満水面積(km2)

English translation by this agent (original above kept as the checker's anchor): name / prefecture /
municipality / address / latitude (deg, min, sec) / longitude (deg, min, sec) / **dam height (m) /
crest length (m) / total storage (thousand m3) / full-pool surface area (km2)**.

There is **no 受益面積 (command area) field**. The register that would settle this question at
national scale records the pond and not the land it waters, so the distribution cannot be computed
from it. (Converting storage to command area would need an assumed seasonal duty, which would make
the answer a dressed-up guess rather than a measurement - so it was not done.)

**What was searched, and what came back.**

| query | engine | outcome |
|---|---|---|
| ため池 受益面積 平均 ha 統計 農林水産省 | search.yahoo.co.jp (curl) | eight results. FETCHED: <https://www.maff.go.jp/j/nousin/bousai/bousai_saigai/b_tameike/gaiyou.html> (HTTP 200, 39,723 bytes) - gives the national count 「農業用ため池は全国約15万か所存在し」 and nothing on command area; and its linked 「農業用ため池とは」 PDF <https://www.maff.go.jp/j/nousin/bousai/bousai_saigai/b_tameike/tameiketoha_R8.pdf> (HTTP 200, 471,989 bytes) - a prefecture-by-prefecture count totalling **148,345** ponds as of March of Reiwa 8, again with no command area. NOT fetched: the e-Stat survey-item page and two MAFF council PDFs, which are pond-AREA statistics rather than command area |
| ため池 受益面積 2ha未満 割合 全国 統計 防災重点 | search.yahoo.co.jp (curl) | FETCHED: <https://www.soumu.go.jp/main_content/000953736.pdf> (HTTP 200, 512,969 bytes), the MIC administrative evaluation of tank disaster works. Its only 受益面積 is a **subsidy eligibility threshold** - 「総事業費 800 万円以上、受益面積 2ha 以上 等」 (English translation by this agent: "total project cost 8 million yen or more, command area 2 ha or more, etc.") - which is a floor for a grant, not a typical size. NOT fetched: prefectural FAQ pages and a commercial explainer, none of which would carry a national range |
| tank irrigation command area average hectares traditional village tank statistics | search.yahoo.co.jp (curl) | results are South Asian (IWMI Walawe small-tank cascade report; Andhra Pradesh tank performance; MDPI tank cascade systems; a Satoyama Initiative Sri Lanka case). NOT fetched: they are Sri Lankan and South Indian tanks, a different agrarian order from the East Asian settlements these maps depict, so a range taken from them would need a limit larger than the finding |
| ため池データベース 受益面積 一覧 エクセル 県 ha 貯水量 ため池台帳 | search.brave.com (curl, HTTP 200, 182,145 bytes) | ten prefectural database pages. FETCHED: <https://web.pref.hyogo.lg.jp/nk11/tameikedetabase.html> (HTTP 200, 16,939 bytes), Hyogo being the prefecture with the most ponds (21,162) - the string 受益面積 does not occur on it and the data itself is behind an external GIS viewer with no downloadable file. NOT fetched: the other nine prefectures, since they publish the same law-mandated database whose national schema was just shown to have no command-area column |
| ため池 かんがい面積 全国 水田 割合 万ha 農業用ため池 役割 | search.brave.com (curl) | **rate-limited** - HTTP 200 with a 73,894-byte body carrying no organic results. Not retried (one attempt per host) |

**For a third pass.** The one route not exhausted is the 「ため池台帳」 (the prefectural tank
ledgers, which the 1983 白井・成瀬 study cited in the J-Stage paper below analyzed **for 受益面積 and
scale**): 森洋・三浦恵祐, 「GISを用いた北海道・東北・関東地域での農業用ため池分布特性の分析」,
農業農村工学会論文集 320 (93-1), 2025 - fetched (HTTP 200, 1,434,706 bytes) and read; it names 白井・
成瀬 1983 as having analyzed 「ため池台帳」に載っている受益面積や規模等 but reports no command
area of its own. **白井・成瀬 1983 is the specific document to chase**, and it is not obviously
online.

---

## 2. `vegetation.html` fn-6 - no readable source counts a Chinese grove's trees

**STILL ABSENT, confirmed against every fengshui-forest document on this machine.** The absence note
is correct as written, and this pass makes it firmer rather than softer: the five on-hand fengshui
documents were re-read end to end and none of them counts a grove's stems, crowns or canopy trees.

| file on this machine | what it is | does it count trees? |
|---|---|---|
| `forests-11-01286.pdf` | Chen, Lin, Zhang, Dai & Chen, "Village Fengshui Forests as Forms of Cultural and Ecological Heritage", *Forests* 11(12):1286, 2020 - the seven-village Youxi County field survey | **No**, and it says so: 「The data collected are qualitative data except for the list of famous and ancient trees (or groves).」 (page 5). Its Table 1 gives per-village grove AREAS (「A forest over three hectares」, 「A forest over six hectares」) and its species table counts INDIVIDUALS OF NAMED SPECIES ON THE FAMOUS-TREE REGISTER (Taxus chinensis 101, Ginkgo biloba 53, Altingia gracilipes 8 ...), which is a register of protected specimens across the county and not a census of any one grove |
| `FenshuiForests.txt` | a scrape of the ScienceDirect landing page for Chen, Coggins, Minor & Zhang, "Fengshui forests and village landscapes in China", *Urban Forestry & Urban Greening*, doi 10.1016/j.ufug.2017.12.011 | **No** - the file is the abstract and the first two paragraphs only, and its own first line says 「This is paywalled but here is what is public」. The public text is a quantitative review of 57 Chinese-language papers and a 57-village field study; it reports 「very high floristic diversity」 and no stem counts |
| `MoreFenshuiForests.txt`, `FenshuiForestManagement.txt` | two scrapes of the same ScienceDirect landing page for Yuan & Liu, "Fengshui forest management by the Buyi ethnic minority in China", doi 10.1016/j.foreco.2009.01.040 | **No** - both are navigation shells ("Purchase PDF", "Article preview", "Cited by (52)") with no body text at all |
| `中山市风水林的药用植物资源.pdf` | 孙红梅・张冬冬・修小娟, 「中山市风水林的药用植物资源」, 熱帯生物学報 7(3):368-372, 2016 | **No** - it is a MEDICINAL FLORA inventory. Its counts are of taxa, not of trees: 「共计 131 科 324 属 451 种」 (English translation by this agent: "a total of 451 species and varieties in 324 genera of 131 families"), surveyed over 「66 villages of Zhongshan city」. No stem count, no basal area, no canopy census |
| `Seeing from Above Observation of Contemporary Dike-Pond Landscape.pdf` | checked in passing while working note 4 | irrelevant here, and in any case an image-only scan with a zero-character text layer |

**So the record's sentence stands**: no readable source counts a Chinese grove's trees, the
Pearl-delta stem density (note 2) and the Korean per-grove counts (note 73) remain the bracket, and
the 100-300 mature canopy trees drawn for the belt remain a GUESS.

**One thing the record could tighten for free.** The count it *can* now assert - that most Fujian
villages keep two fengshui forests - is on the same page of the same paper, quoted in full under
note 1 above, which also carries 「are mainly located near a villages' entrances, ancestral halls,
and temples」 that the entry already quotes. That is a second footnote closed off one read.

**What was searched for a tree count, and what came back.** Two web searches were run before the
on-hand re-read (`search.yahoo.co.jp` via curl, the engine that answers when WebSearch is
exhausted), and neither surfaced a candidate that counts stems in a named Chinese grove:
中山市风水林 (returns the medicinal-flora paper already on this machine) and the general
fengshui-forest survey literature (returns the Chen/Coggins review and MDPI pages, both already
read). No new candidate was found to fetch. This is the third pass over this question and the third
null; the entry should be left as a disclosed GUESS rather than searched a fourth time.

---

## 8. `fields.html` fn-87 - 70-75% paddy in a near-city plain, at 1.5-2 farming households per hectare

**STILL ABSENT on both numbers, with one precise lead for a third pass.** Neither the paddy share of
a dense near-city plain nor the farming households per hectare of paddy was found stated in a
readable source. Note that the surrounding sentence's other two figures - the 12% and 28%
cultivated-ground floors - the record already discloses as calibrated against its own drawn maps
rather than taken from a source, so those are not at issue here.

**The lead, named precisely.** Japan's national cultivated-area statistic splits paddy into
**本地 (hon-chi, the growing surface)** and **けい畔 (keihan, the bunds)** and publishes the split as
a long time series - which is the paddy-versus-bund half of the record's 70-75% figure, measured
nationally and annually rather than guessed:

- e-Stat, 作物統計調査 面積調査, 「長期累年 耕地及び作付面積統計 1 **本地・けい畔別耕地面積累年統計**」, <https://www.e-stat.go.jp/dbview?sid=0003320704>

This agent did not read it: the e-Stat `dbview` page renders its table through JavaScript and its
data API wants a registered `appId`, so no number can be quoted from it here, and quoting one from
a search result would be exactly what this project forbids. It is a straightforward read for a
session with a browser or an e-Stat key, and it is the right instrument.

**Two cautions on using it when someone does.** First, the DENOMINATORS differ: the record's
70-75% is paddy as a share of the whole near-city plain, whose remainder it lists as 「bunds,
ditches, lanes and farmsteads」, while the Japanese series measures 本地 against けい畔 *within
cultivated land*, with lanes and farmsteads excluded from 耕地 altogether. The series will therefore
give a bund share much smaller than the record's 25-30% remainder, and it will answer only the
bund part of it. Second, the series is modern and post-consolidation for its recent decades;
the useful years are the early ones, before 圃場整備 regularized the bunds.

**What was searched, and what came back.**

| query | engine | outcome |
|---|---|---|
| average farm size China Qing dynasty hectares per farm household paddy plain Perkins agricultural development | search.brave.com (curl, HTTP 200, 245,584 bytes) | eight results, none a readable primary figure: three Wikipedia articles (*Agriculture in China*, *Economy of the Qing dynasty*, *History of agriculture in China*), a Britannica topic page, a Harvard Kennedy School CATALOG entry for Perkins, *Agricultural Development in China: 1368-1968* (the book itself, not readable), a University of Utah course PDF on modern Chinese agriculture, a PMC article on China's land-use change over 300 years, and a ResearchGate FIGURE page giving a **modern** 0.60 ha average. Not fetched: the encyclopedia articles are tertiary and this project cites an encyclopedia's own references rather than the article, the Harvard page is a catalog entry, and the modern 0.60 ha is the wrong century. **Perkins 1969 is the work that would answer this**, and it is not openly readable |
| 耕地面積 畦畔 本地 割合 定義 農林水産省 耕地及び作付面積統計 | search.brave.com (curl, HTTP 200, 193,408 bytes) | eight results. FETCHED: <https://www.maff.go.jp/j/tokei/kouhyou/sakumotu/menseki/gaiyou/> (HTTP 200, 116,021 bytes), the survey's methodology page - it defines a 筆ポリゴン as 「けい畔等で区切られた現況一枚のほ場」 (English translation by this agent: "one field as it currently stands, bounded by bunds and the like") and states the survey's sampling design, but publishes no ratio. The e-Stat series above is the one row that carries the number, and it is JS-gated |
| 耕地面積 畦畔 本地 割合 定義 農林水産省 耕地面積調査 | search.yahoo.co.jp (curl) | **rate-limited** - HTTP 200 with a 3,668-byte body carrying only a Yahoo help-center link. Not retried (one attempt per host) |

---

## 11. `cities/river-cities.html` fn-18 - the four unsourced spans around the offtake

The footnote number in the batch file hangs on the LAST of five unsourced spans in this paragraph.
They are separable claims with separable answers, so they are reported separately. Nothing here
changes what the map draws.

### (a) "Natural tributaries curve to join pointing downstream, and engineered drainage returns are cut to do the same"

**CITED for the engineered half; STILL ABSENT for the natural half.**

URL: <https://en.wikipedia.org/wiki/Confluence>, §"Engineering", fetched with curl and a browser user
agent (**HTTP 200, 272,040 bytes**), verbatim:

> The velocities and hydraulic efficiencies should be meticulously calculated and can be altered by integrating different combinations of geometries, components such a gradients, cascades and an adequate junction angle which is sympathetic to the direction of the watercourse's flow to minimise turbulent flow, maximise evacuation velocity and to ultimately maximise hydraulic efficiency.

(「components such a gradients」 is the article's own wording, not a transcription slip.)

**How it supports the claim.** This is the record's engineered half in the engineering literature's
own terms: a junction is cut at an angle **sympathetic to the direction of the receiving
watercourse's flow**, and the reason given is the record's reason - less turbulence, faster
evacuation. The context is a culverted or artificially buried watercourse, which is a narrower case
than the open drainage return the record draws; that limit should be carried. The record already
cites `meander-enwiki` in this same area, so an English Wikipedia footnote is within this record's
existing practice - but it is a tertiary source, and the article's own reference [10] is the better
target if anyone re-reads this.

**The natural half - that tributaries curve to join pointing downstream - was not found stated** on
any page read this pass. The Confluence article does not say it. The nearest literature surfaced was
a body of work on stream junction ANGLES as a landscape variable (OpenAlex, query "tributary junction
angle confluence acute downstream orientation drainage network", 36 hits) - e.g. "The length and
spacing of river tributaries", *PNAS* 2024, <https://www.pnas.org/doi/pdf/10.1073/pnas.2313899121>,
and "The Role of Dykes in Shaping Stream Junction Angles", *IJG* 2025,
<https://www.scirp.org/pdf/ijg_2802723.pdf> - both openly readable and neither fetched, because both
treat the junction angle's CONTROLS (spacing, lithology, tectonics) rather than asserting the
downstream-pointing rule the record wants, and a paper fetched to see whether it happens to contain
a sentence is a fishing trip rather than a read.

### (b) "an offtake swallows a share of the river's bedload in proportion to how well it is aligned ... and a silted moat is a maintenance failure rather than a hydraulic one"

**STILL ABSENT.** Not found. Note that the entry's own closing paragraph already records the
opposite-signed finding from summaries it could not read - that a diversion draws its LEAST sediment
at an INTERMEDIATE angle rather than at the square - so this span is not merely unsourced, it is
unsourced in a place where the searchable literature may point the other way. It should stay a
disclosed guess and should not be quietly upgraded.

### (c) "Classical headworks therefore kept the offtake itself near square, controlling the flow with a gate instead, siting the intake on the outer bank of a bend and skimming the cleaner upper water"

**STILL ABSENT.** Three searches for the bend-siting rule in Chinese (取水口 / 凹岸 / 弯道 / 环流 /
防沙 / 引水) were attempted and none returned usable results: `search.yahoo.co.jp` was rate-limited
(3,669-byte help-center body), `www.so.com` answered once with 376,757 bytes and then with an empty
body on the next request, and `search.brave.com` was rate-limited (73,894-byte body with no organic
results). One attempt per host was taken and none retried.

**What was checked in the documents already in hand, so that a third pass need not repeat it.**
T/JSSLKX 002-2021 (read in full) was grepped for 取水 / 引水 / 凹岸 / 凸岸 / 泥沙 / 含沙 / 沉沙 /
冲沙 / 防沙 / 弯道. It carries the intake TYPOLOGY the record's own knob uses -

> 3.31 无坝引水 - 利用河道地形、河流水文－水力学特点布置分水导流堤、溢流堰等设施，从河道分流引水。
> 3.32 有坝引水 - 通过在河流上筑坝，壅水入渠，引水灌溉的一种工程形式。

English translation by this agent (original above kept as the checker's anchor): "3.31 Barrage-less
diversion - diverting water from a river channel by laying out works such as a dividing training
dyke or an overflow weir, making use of the channel's terrain and the river's hydrological and
hydraulic characteristics. 3.32 Barrage diversion - a form of works in which a dam is built across
the river, ponding the water up into the canal, to divert water for irrigation."

- but it states **no rule about where on a bend an intake is sited and no sediment-exclusion clause
at all**. Its §8.4 「引水工程」 is about the dam type and the flood standard. So the readable Jiangsu
guideline, which has closed a good many notes on this record, does **not** answer this one, and that
is worth writing down.

**The specific document a third pass should chase** is the national standard the guideline defers to,
**GB 50288 (*Technical code for irrigation and drainage engineering*)**, whose 2018 edition the
Conghua design report cites by number and quotes for its scour and siltation velocities. That is a
FOR-THE-GM item rather than a search: the earlier pass recorded antpedia's index shell at HTTP 200
with no standard text and its PDF mirror at HTTP 403, and this pass found nothing better.

### (d) "a moat wants STAGE - the height of the water surface - rather than throughput"

**STILL ABSENT.** No work was found distinguishing a moat's demand for water level from a canal's
demand for flow. One search was run (`search.brave.com`, curl, HTTP 200, 311,676 bytes: "moat water
level stage not flow through fed from river castle town maintain level sluice") and every organic
result was off-target - a construction-blog piece on British castle moats, a content-farm article,
and six Reddit threads about water mechanics in the video game *Timberborn*. None was fetched;
none is a source.

**A note for whoever takes this next.** The claim is close to a definition rather than a finding -
a moat is a standing body whose function is its level, a canal a conveyance whose function is its
discharge - and the literature that would state it is castle- and city-engineering history rather
than hydraulics. The likeliest readable body is Japanese: 堀 / 水堀 maintenance and 城郭 water-supply
studies, and the 「水堀の水位維持」 vocabulary. That was not searched this pass, because every
Japanese-language engine available had rate-limited by the time this note was reached.

---

## Closing: what this pass produced

### Verdicts, counted

Of the 11: **3 CITED** (1, 3, 7), **3 CITED IN PART** (6, 9, and the engineered half of 11a),
**5 STILL ABSENT** (2, 5, 8, 10, and 11b/11c/11d), **1 note that can simply be retired** (4).
Nothing was CONTRADICTED.

### New sources this pass introduces, which owe registry write-ups and a `source-applicability` read

Per the constitution's fifth research box, each of these needs "What it is" / "Why it applies, and
its limits" write-ups and a `source-applicability` verdict **before** its numbers reach a map or a
rule. This agent's own limits notes are written into each entry above and are a starting draft, not
a substitute.

| proposed key | work | what it is asked for | the limit to argue |
|---|---|---|---|
| `conghua-2026-design` | 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿）, Conghua District Bureau of Agriculture and Rural Affairs, June 2026 | canal widths by grade: 斗渠 1.0-1.2 m, 农渠 0.4-0.6 m (note 3) | a modern concrete- and masonry-lined district works schedule; what it fixes is the ladder's PROPORTIONS, not premodern materials |
| `obata-1977-taue` | 小畑晃男, 「和歌山県における慣行田植法の地域性とその成立要因に関する研究」, 農作業研究 29: 24-29, 1977 | the hamlet-unit agreed transplanting schedule, the 20-30 household unit, the 7-10 day window (note 6) | one prefecture, surveyed 1975-76 for practice remembered as customary; the scan's OCR layer is unreliable and every quote here was read off the page image |
| `tajima-2007-nightsoil` | Kayo Tajima, "The Marketing of Urban Human Waste in the Early Modern Edo/Tokyo Metropolitan Area", *Environnement Urbain / Urban Environment* 1, 2007 | the fertilizer-intensity gradient by distance from a castle town (note 7) | a CASTLE-TOWN gradient measured in fertilizer regime, not in cultivated share; a county seat is smaller, so the ri distances are an upper bound. Open access, but both hosts bot-gate a fetcher |
| `confluence-enwiki` | English Wikipedia, "Confluence", §Engineering | the engineered junction cut sympathetic to the receiving flow (note 11a) | tertiary, and the passage is about CULVERTED watercourses; the article's own reference [10] is the better target |
| `jsslkx-002-2021` (already registered) | T/JSSLKX 002-2021 | §7.4.1 the alignment maxim (note 10); §7.4.3/7.4.5/7.4.8/7.4.9 the orthogonal field grid (note 9); §9.3.7 and §9.4.3 as NEGATIVE findings (note 3) | already carried |

### FOR THE GM

- **GB 50288**, *Technical code for irrigation and drainage engineering*. Wanted for note 11(c) - the
  siting of a headworks intake on a bend, and sediment exclusion - and it is the standard both
  readable Chinese documents in this pass defer to by number. Neither of its two known online
  locations serves the text: `https://www.antpedia.com/standard/7931413-1.html` answered HTTP 200
  with an index/navigation shell only, and
  `https://img.antpedia.com/standard/files/pdfs_ora/20200926/GB%2050288-2018.pdf` answered HTTP 403.
  This pass found no third location. A purchased or library copy would close note 11(c) and would
  firm up note 3.
- **白井・成瀬 1983**, the study of 「ため池台帳」 for 受益面積 and scale that 森・三浦 2025 cites.
  Wanted for note 5 - the command area of a village tank - which no national dataset carries. Not
  obviously online.
- **Perkins, *Agricultural Development in China: 1368-1968* (1969)**. Wanted for note 8 - farm
  households per hectare in a premodern Chinese paddy plain. Only a Harvard Kennedy School catalog
  entry surfaced.

### Every host contacted, and what it answered

One attempt per host, per the brief; where a host answered and a second file from it was clearly
needed, that is noted.

| host / URL | result |
|---|---|
| `https://api.unpaywall.org/v2/10.3390/f11121286` | 200, JSON; `is_oa: true`, four OA locations listed |
| `https://www.mdpi.com/1999-4907/11/12/1286/pdf` | **403**, 410-byte HTML body (bot block, not a paywall) |
| `https://u-ryukyu.repo.nii.ac.jp/records/2011293` | **406**, 558-byte body |
| `http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf` | 200, 622,748 bytes, read in full |
| `http://nyncj.gz.gov.cn/attachment/8/8037/8037125/10854794.pdf` | 200, 23,291,315 bytes, text layer intact, read |
| `http://xxgk.jccq.gov.cn/.../t20240914_2035112.shtml` | 200, 105,751 bytes; the 干支斗农毛 hierarchy explained with no dimensions |
| `https://www.i-sis.org.uk/DykePondSystem.php` | 200, 28,576 bytes; the pond and dike figures verbatim, and Ruddle & Zhong as its reference [1] |
| `https://www.maff.go.jp/j/nousin/bousai/.../gaiyou.html` | 200, 39,723 bytes; national pond count, no command area |
| `https://www.maff.go.jp/j/nousin/bousai/.../tameiketoha_R8.pdf` | 200, 471,989 bytes; 148,345 ponds by prefecture, no command area |
| `https://www.maff.go.jp/j/nousin/bousai/.../ichiran.html` | 200, 36,911 bytes; the nine dataset files located |
| `https://www.maff.go.jp/j/nousin/bousai/.../tameike_ichiranR8_1.xlsx` | 200, 1,612,660 bytes; header read from the workbook XML - **no 受益面積 column** |
| `https://www.maff.go.jp/j/tokei/kouhyou/sakumotu/menseki/gaiyou/` | 200, 116,021 bytes; methodology only, no bund ratio |
| `https://www.soumu.go.jp/main_content/000953736.pdf` | 200, 512,969 bytes; 受益面積 appears only as a subsidy threshold |
| `https://www.jstage.jst.go.jp/article/jsfwr1966/1977/29/1977_29_24/_pdf/-char/en` | 200, 834,972 bytes; read, and the quoted passages confirmed against the page images |
| `https://www.jstage.jst.go.jp/article/jsidre/93/1/93_IV_1/_pdf/-char/ja` | 200, 1,434,706 bytes; read, names 白井・成瀬 1983 but gives no command area |
| `http://www.knowledgebank.irri.org/ericeproduction/V.1_Pest_and_IPM_.htm` | 200, 16,924 bytes; a course outline, nothing on synchronous planting to quote |
| `https://journals.openedition.org/eue/1039` | 200, 5,299 bytes - an **Anubis** anti-bot interstitial, not the article |
| `https://www.erudit.org/en/journals/eue/2007-v1-eue3020/016245ar/` | 200, 7,806 bytes - "Making sure you're not a bot!" |
| `https://web.pref.hyogo.lg.jp/nk11/tameikedetabase.html` | 200, 16,939 bytes; data behind an external GIS viewer, no 受益面積 on the page |
| `https://en.wikipedia.org/wiki/Confluence` | 200, 272,040 bytes; read |
| **search engines** | `search.yahoo.co.jp` answered three queries with real organic results and then rate-limited to a 3,668-byte help page; `search.brave.com` answered five and then rate-limited to 73,894 bytes; `www.bing.com` answered but degraded a long query to its first word; `lite.duckduckgo.com` and `html.duckduckgo.com` returned the homepage; `www.mojeek.com`, `www.ecosia.org` (403), `www.baidu.com`, `www.sogou.com`, `searx.be`, `search.disroot.org`, `yandex.com` returned nothing usable; `www.so.com` answered once and then returned an empty body. The OpenAlex API answered every query; the Semantic Scholar API returned empty results for all three (no key) |

### Tooling notes for the next pass

1. **`search.yahoo.co.jp` and `search.brave.com` both work through curl and both rate-limit hard** -
   about three and five queries respectively before they start returning a stub body. Plan the
   queries before spending them, and check the response SIZE: a 3.6 KB Yahoo body or a 74 KB Brave
   body means blocked, not "no results".
2. **A J-Stage scan's OCR layer lies.** `pdftotext` on the 1977 Wakayama paper rendered な as 左,
   お as 夢 and あ as め. Confirm any CJK quote from a scanned PDF against
   `pdftoppm -r 200 -png -x -y -W -H` output before transcribing it - and note that the journal's own
   typesetting may be the odd thing (it really does print 「勢んな」).
3. **A two-column Japanese PDF interleaves under `pdftotext -layout`.** Crop the columns with
   `pdftotext -x <half width> -W <half width>`, and read the page size off `pdfinfo` first - guessing
   A4 when the page is 487 x 731 pt silently mixes the columns back together.
4. **An `.xlsx` can be read without `openpyxl`** (which `pip` refuses to install into this
   environment): `zipfile` + `xml.etree` over `xl/worksheets/sheet1.xml` and `xl/sharedStrings.xml`
   is a dozen lines and was enough to prove the tank register has no command-area column.
5. **A Chinese district design report is a better source for built dimensions than a standard is.**
   A standard states procedure and minima; a 初步设计报告 states what is actually being built, tier
   by tier, with a works schedule. They are published openly on municipal `.gov.cn` sites and they
   cite the national standard they follow, which is how note 3 got its number after two passes had
   failed against the standards themselves.
