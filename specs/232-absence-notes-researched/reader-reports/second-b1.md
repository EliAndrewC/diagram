# Second pass, batch b1 - on-hand sources and agronomy (11 notes)

Reader: source-reader agent, 2026-09-12. One fetch attempt per host. Nothing cited that was not read.

| # | note | claim in one line | verdict |
|---|---|---|---|
| 1 | `vegetation.html` fn-4 | Fujian villages keep ~2 fengshui forests each (Xu, Qiu & Wang 2012, via Forests 2020) | **CITED** |
| 2 | `vegetation.html` fn-6 | no readable source counts a Chinese grove's trees | *pending* |
| 3 | `water.html` fn-48 | a distribution lateral is ~1 m wide | **CITED** (a Guangzhou farmland design, not the Jiangsu guideline) |
| 4 | `archetypes.html` fn-84 | 6:4 water-to-dike split; 0.4-0.6 ha ponds, 6-10 m dikes (Ruddle & Zhong) | **RETIRE THE NOTE** - every figure is already quoted from a readable page |
| 5 | `fields.html` fn-35 | village tanks command tens of hectares, well under 200 | *pending* |
| 6 | `fields.html` fn-82 | a village transplants together, on one schedule | *pending* |
| 7 | `fields.html` fn-86 | the ring nearest a market town is worked hardest | *pending* |
| 8 | `fields.html` fn-87 | dense near-city plain ~70-75% paddy, 1.5-2 farming households/ha | *pending* |
| 9 | `fields.html` fn-88 | a dry field beside a canal is surveyed TO the canal | *pending* |
| 10 | `water.html` fn-73 | the crew re-digs the bend rather than the corner | *pending* |
| 11 | `cities/river-cities.html` fn-18 | a moat wants STAGE, a canal wants FLOW; and the four other unsourced spans | *pending* |

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
