# Feature 232 reader report: buildings-and-houses (20 notes)

Reader relaunch, 2026-09-12. One attempt per host; a refused host is not retried.

## Verdict table

| # | page / footnote | verdict | in one line |
|---|---|---|---|
| 1 | `archetypes.html` fn-87 | **FOR THE GM** | Miles 2003, *Ming Studies*, closed at Unpaywall - no open copy anywhere |
| 2 | `archetypes.html` fn-88 | **FOR THE GM** | Kinoshita 1995, *Journal of Family History*, closed at Unpaywall; the claim it supports is setting canon anyway |
| 3 | `buildings.html` fn-71 | **FOR THE GM** | the 1992 Gifu report is in the open Nara site-report archive, which returned 429 twice |
| 4 | `cities/defenses.html` fn-16 | **CITED** + **CONTRADICTED** | Xi'an's 6 m tunnel confirms "about 20 ft"; Nanjing's four gates measure 4.8-5.35 m, not the record's 23 ft |
| 5 | `cities/defenses.html` fn-18 | **STILL ABSENT** | the street name 順城街 is attested; the clear-lap-for-troops rule is not |
| 6 | `cities/fabric.html` fn-17 | **STILL ABSENT** | and correctly so - the assertion is the GM's setting ruling, which is exempt |
| 7 | `cities/fabric.html` fn-20 | **CITED** + **CONTRADICTED** | mune-wari pairs, the one gate off the street, the idobata widening - all cited; the roji was 0.9-1.8 m, not 12 ft |
| 8 | `cities/government.html` fn-22 | **CITED** | the daozuofang's windowless street wall and its servants, off zh.wikipedia rather than Baidu |
| 9 | `cities/government.html` fn-37 | **CITED** + **STILL ABSENT** | ward areas cited (27-94 ha, wider than the record's 30-80); no date found for the system's end |
| 10 | `cities/hinterland.html` fn-4 | **CITED** | the guanxiang half, from two described places rather than a dictionary entry |
| 11 | `cities/hinterland.html` fn-8 | **CITED** | road-driven suburb, market and inns, and 48 horse inns at one Beijing gate; one sub-clause runs the other way |
| 12 | `homesteads.html` fn-36 | **CITED** | the "minimize turns" GUESS is supported verbatim in the open-access copy of the very DOI that 403'd |
| 13 | `religion-and-death.html` fn-12 | **CITED** | Inexhaustible Treasury and the 713 liquidation as fraudulent banking |
| 14 | `religion-and-death.html` fn-13 | **CITED** | monastic pawnbroking before the Tang, and the 1202 ju of ten men |
| 15 | `towns.html` fn-24 | **STILL ABSENT** | south is readable for a BUILDING; for a gate the nearest passage gives the southeast corner instead |
| 16 | `urban-features.html` fn-62 | **STILL ABSENT** | fining in Han China is cited; chao, Song Yingxing's hearth and Xuxiebian are not - donwagner.dk is down |
| 17 | `urban-features.html` fn-74 | **FOR THE GM** | the kabu-ido paper is CC-BY and still unreadable - Springer serves a bot stub to every fetcher |
| 18 | `urban-features.html` fn-83 | **CITED** + **STILL ABSENT** | 523 sento cited (dated 1810, not 1808); no readable figure for the 1.1 million denominator |
| 19 | `urban-features.html` fn-84 | **CITED** | narrow single-track roji, and "nearly all roads were unpaved" until 1899 |
| 20 | `vegetation.html` fn-91 | **CITED** | flat ground gives rectangles on 10 cm bunds, slope gives contour-following strips |

---
## Tooling note (read this before the verdicts)

This relaunch lost the `WebSearch` tool at its fourth call: the session's web-search budget
(200/200) was already spent by the agent that stalled. Everything after that point was done with
`WebFetch` and with `curl` under a browser user agent, plus the MediaWiki, OpenAlex and J-STAGE
search APIs. Two general engines were tried as a substitute and are recorded here once rather than
under every note: `html.duckduckgo.com/html/` and `lite.duckduckgo.com/lite/` return HTTP 202 with
an anomaly page and zero results; `www.mojeek.com/search` returns HTTP 200 with no organic results;
`www.bing.com/search` returns results for English queries but ranks them badly and DROPS a CJK query
entirely (a query of `西安城墙 永宁门 门洞 宽 米` came back with French job adverts). So where a
note below says STILL ABSENT, read it as "not found without a general search engine" - several of
them would be worth one more pass by a reader that has `WebSearch`.

---

### `cities/defenses.html` fn-16

**CITED** for Xi'an, and **CONTRADICTED** for the Nanjing number.

Xi'an - zh.wikipedia 西安城墙, read through the MediaWiki extracts API
(https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89%E5%9F%8E%E5%A2%99):

> Translated from the Chinese by this project: "Except beneath the archery tower of the south gate,
> beneath each of the other towers is set an arched gate tunnel; the tunnel is 6 meters in both
> height and width, and 19.5 meters deep."

Original: 「除南門箭樓外，其餘各樓下都設拱形門洞，門洞高、寬各6米，深19.5米。」 (the API serves the
simplified form: 「除南门箭楼外，其余各楼下都设拱形门洞，门洞高、宽各6米，深19.5米。」)

6 m is 19.7 ft, so "Xi'an about 20 ft" is exactly right, and the tunnel is 19.5 m deep - a real
tunnel, not an opening.

Nanjing - en.wikipedia "Zhonghua Gate, Nanjing"
(https://en.wikipedia.org/wiki/Zhonghua_Gate,_Nanjing), confirmed by a browser-UA `curl` of the same
page (the four figures are in one paragraph):

> "In the middle of the lower step was constructed an arched gate leading to barbican. It was 52.60
> m long, 5.35 m wide and 8.7 m high."

> "Erdaomen (the second gate) was 16.14 m away from Toudaomen. Its hole was 8.20 m long, 4.97 m wide
> and 8.10 m high. The hole of Sandaomen (the third gate) 15.18 m away from Erdaomen was 8.32 m
> long, 4.82 m wide and 8.1 m high. Sidaomen (the fourth gate) was 19.3 m away from Sandaomen. Its
> hole was 8.8 m long, 4.8 m wide and 8.1 m high."

The four clear widths are 5.35, 4.97, 4.82 and 4.80 m - 15.7 to 17.6 ft. The record says "Nanjing's
Zhonghua gate about 23 ft" (7.0 m), which no passage on the page supports and these four figures
contradict. The BAND the paragraph draws - "about 13-23 ft clear" - survives: every measured width
above sits inside it, and Xi'an's 6 m sits near its top. What the map's rule needs (a gate narrows
the road) is supported by both cities; the Nanjing number wants correcting to about 16-18 ft.

Not found: any readable page giving the clear width of an Edo castle-town koraimon. Attempts are
under the tooling note - no general engine was available to look for one.

---

### `cities/government.html` fn-22

**CITED** for the daozuofang, the part the last pass lost to Baidu's 403.

zh.wikipedia 四合院 (https://zh.wikipedia.org/wiki/%E5%9B%9B%E5%90%88%E9%99%A2), fetched
successfully; Baidu Baike was NOT retried, per the one-attempt rule.

> Translated from the Chinese by this project: "Its eaves wall faces the hutong, and it generally
> has no windows."

Original: 「其檐墙临胡同，一般不开窗。」

> Translated from the Chinese by this project: "Its easternmost room was the private school and its
> westernmost the privy; the rooms between them were generally occupied by servants."

Original: 「其最东为私塾，最西为厕所，其间的房子一般为仆人居住。」

Together these support both halves of the assertion the footnote hangs on: the south row's
windowless back IS the compound's street wall, and the row between its end rooms is where the
household servants lived. The same article gives the orientation contrast the paragraph assumes -

> Translated from the Chinese by this project: "The rear building is usually the house of the
> innermost courtyard, near the boundary of the compound, and usually the owner's daughters lived
> there."

Original: 「后罩房通常是最里一进院子的，靠近院落边界的房子，通常主人的女儿居住。」

- which supports the paragraph's "the inner wings house family, not servants" for the REAR row
specifically (it houses daughters), and is worth noting because the record currently marks the
houzhaofang clause "(unsourced)".

Still absent on this note: the Pingyao clerks' lodging (lishe / gongxiefang) built 1619 behind the
west three chambers, and the Neixiang west line. Baidu Baike carries them and refuses automated
fetches; it was not retried.

---

### `urban-features.html` fn-83

**CITED** for the bathhouse count; **STILL ABSENT** for the population it is divided by, and the
year differs.

nippon.com, "The Story of "Sentō": A History of Public Bathhouses in Japan"
(https://www.nippon.com/en/views/b07302/):

> "Records show that by 1810 there were 523 _sentō_ in the city, demonstrating just how much Edoites
> loved a good soak."

That is the 523 the map's one-per-2,000 ratio was calibrated on, on a page anyone can open. Two
things it does NOT give: the year in the record is 1808 and the page says 1810, and the page carries
no population figure at all.

For the denominator I read en.wikipedia "Edo" (https://en.wikipedia.org/wiki/Edo), which gives "1
million by the early 18th century" and a figure of 1,000,000 cited to 1721 - neither is "some 1.1
million residents in 1808". So the RATIO as the record states it is not yet citable end to end: the
count is, the population is not. A reader with a search engine should look for the bakufu's own
machikata population returns for Bunka-era Edo.

---
### `cities/fabric.html` fn-20

**CITED** for the back-to-back pair, the single entrance onto the roji and the widening at the
idobata; **CONTRADICTED** for the roji's width.

All three passages are on ja.wikipedia pages that open for anyone; they were read through the
MediaWiki extracts API rather than the rendered page.

(a) The pair. ja.wikipedia タウンハウス (https://ja.wikipedia.org/wiki/%E3%82%BF%E3%82%A6%E3%83%B3%E3%83%8F%E3%82%A6%E3%82%B9):

> Translated from the Japanese by this project: "The ura-nagaya were ridge-split along the roji, of
> nine shaku by two ken (3.6 m x 2.7 m), with a four-and-a-half-mat room and a one-and-a-half-mat
> earth floor (stove, sink), and the great majority of the common inhabitants lived in them as
> rented houses. The shared well and privy are situated at the far end of the roji."

Original: 「裏長屋は、路地に沿って棟割りされて四畳半の部屋に一畳半の土間（竈、流し）のついた九尺二間（3.6m×2.7m）の広さで、大多数の庶民が借家として暮らしていた。共用の井戸、便所は路地の奥に位置する。」

棟割 (mune-wari, "ridge-split") IS the back-to-back pair: one roof, one shared rear wall, the units
of each half opening to opposite sides. That is the record's "back-to-back PAIRS with both fronts
outward", named as the standard form rather than deduced.

(b) The single entrance, and the depth. ja.wikipedia 町屋 (商家)
(https://ja.wikipedia.org/wiki/%E7%94%BA%E5%B1%8B_(%E5%95%86%E5%AE%B6)):

> Translated from the Japanese by this project: "One entered and left the ura-nagaya through a
> wooden gate set between two front shops, and through the roji."

Original: 「裏長屋へは、2軒の表店の間に設けられた木戸と路地から出入りした。」

> Translated from the Japanese by this project: "Every unit of the ura-nagaya had the same plan;
> where a front shop's frontage was about three ken they stood along one side, and where about five
> ken, along both sides."

Original: 「裏長屋の各戸は同じ平面で、表店の間口が3間程度なら片側、5間程度なら両側に並んでいた。」

The second is the depth rule from the other end: what a plot's frontage buys is ONE row or TWO
facing rows on the roji, never a third rank behind them.

(c) The idobata widening. ja.wikipedia 路地 (https://ja.wikipedia.org/wiki/%E8%B7%AF%E5%9C%B0):

> Translated from the Japanese by this project: "The place immediately inside the back of the
> merchant house, or the middle of the roji and so on, was made wider, and a shared well or a shared
> water supply was installed there."

Original: 「商家の裏側に入ってすぐの場所あるいは路地の中央などは幅が広くなっており、共同井戸や共同の水道が設置されていた。」

(d) The width, which the record has wrong. Same 路地 article:

> Translated from the Japanese by this project: "The width of the roji between one ura-nagaya
> building and the next was about three to six shaku (about 0.9 to 1.8 meters)."

Original: 「裏長屋の建物と建物の間の路地の幅は3尺から6尺ほど（0.9メートルから1.8メートルほど）だった。」

0.9 to 1.8 m is 3 to 6 ft. The record's "a walkable roji of about 12 ft" is two to four times that,
and the same page says the roji was so private that nobody but the residents of the houses on it
used it - which is what a 3 ft path between two eaves is. Whether the drawn 12 ft is a map drawing
convention (a path this narrow cannot carry a label or read as a way at 1 px = 1 ft) or a number
that was simply never checked is for the session to decide, but it is not the historical width and
the page that gives the historical width is public.

---

### `urban-features.html` fn-84

**CITED** in part - the width and the single track - and **STILL ABSENT** for "packed earth,
unpaved".

ja.wikipedia 路地 (https://ja.wikipedia.org/wiki/%E8%B7%AF%E5%9C%B0) carries the width quoted at
fn-20(d) above - 3 to 6 shaku, 0.9 to 1.8 m - and this, on who used it:

> Translated from the Japanese by this project: "It is a narrow passage caught between one house and
> the next. That it is not the main street resembles a yokocho, but the roji is narrower still than
> a yokocho, a narrow passage which almost nobody but those connected with the adjoining buildings
> uses."

Original: 「家屋と家屋の間に挟まれた細い通路である。表通りではないことは「横丁」と似ているが、路地のほうは横丁よりも更に狭く、隣接する建物の関係者以外はほとんど利用しない細い通路である。」

That supports "narrow", "single-track" and "not a street" - the record's own three adjectives - on a
public page. What it does not carry is the SURFACE. The nearest the page comes is drainage rather
than paving:

> Translated from the Japanese by this project: "Down the middle of the roji were laid gutter boards
> (dobuita), and beneath them was dug a small gutter six to seven sun wide (18 to 21 centimeters).
> The drainage from the well-side water point and the rainwater from the nagaya roofs both flowed
> into this gutter."

Original: 「路地の中央には溝板（どぶいた）が並べられており、その下には幅が6寸から7寸（18センチメートルから21センチメートル）の小さなどぶが掘られていた。井戸端の水場からの排水も長屋の屋根からの雨水も、このどぶに流れ込んでいた。」

A plank-covered ditch down the center of an otherwise bare path is consistent with an unpaved
surface and inconsistent with a paved one, but the page never says "unpaved", so this is evidence
around the claim rather than the claim. A reader with a search engine should look for the history of
road surfacing in pre-Meiji Japanese towns, which is where this sentence will be found if it is
anywhere.

---
### `religion-and-death.html` fn-12 and fn-13

**CITED** for the Inexhaustible Treasury and for the monastic pawnshop, which are the two
assertions these footnotes hang on; the mills, oil presses and dependent labor in the same paragraph
are still uncited.

Both footnotes sit in the same sentence chain, so the evidence is reported once.

(a) The Inexhaustible Treasury and its liquidation. en.wikipedia "Chang'an"
(https://en.wikipedia.org/wiki/Chang%27an):

> "In 713, Emperor Xuanzong liquidated the highly lucrative Inexhaustible Treasury, which was run by
> a prominent Buddhist monastery in Chang'an."

> "Although the monastery was generous in donations, Emperor Xuanzong issued a decree abolishing
> their treasury on grounds that their banking practices were fraudulent, collected their riches,
> and distributed the wealth to various other Buddhist monasteries, Taoist abbeys, and to repair
> statues, halls, and bridges in the city."

That is the record's "the Chang'an one liquidated by Xuanzong in 713 as fraudulent banking", almost
word for word, including "banking practices were fraudulent". The article attaches the passage to
its footnote 36, keyed "Benn_55" - Charles Benn, p. 55 - which is the work to cite if the record
would rather not rest on an encyclopedia.

(b) The pawnshop, before the Tang and in the Song. en.wikipedia "History of pawnbroking"
(https://en.wikipedia.org/wiki/History_of_pawnbroking):

> "The earliest Chinese pawnbrokers, in the 5th century, were established, owned, and operated by
> Buddhist monasteries; only later were they more widely seen."

> "During the Southern Song dynasty, wealthy lay people sometimes formed partnerships with Buddhist
> monasteries and opened pawnshops (avoiding property taxes from which monasteries were exempt)."

> "A 1202 document records ten people forming a _ju_ (局), which would support the establishment of
> a pawnshop in a monastery."

Three assertions of the paragraph, verbatim: pawnbroking before the Tang confined to monasteries;
lay investors partnering INTO the monastic tax exemption; and the 1202 ju of ten men. The article
cites Michael J. Walsh, *Sacred Economies: Buddhist Monasticism and Territoriality in Medieval
China* (Columbia University Press, 2009), p. 62 - again the work to prefer over the encyclopedia.

What is NOT covered: "their land and dependent labor funded mills, oil presses and other
enterprises". Neither page carries it, and the Tandf article the last pass was blocked on
(10.1080/23729988.2019.1639463) was not retried - it is the same host and the same 403.

---

### `towns.html` fn-24

**STILL ABSENT** for a gate, though the orientation preference itself is readable.

What was searched, with no general engine (see the tooling note): en.wikipedia "Chinese
architecture" and "Siheyuan" were read in full, and zh.wikipedia was asked for an article at 坐北朝南
(the Chinese name of the very principle), which does not exist.

en.wikipedia "Chinese architecture" (https://en.wikipedia.org/wiki/Chinese_architecture) does carry
the orientation:

> "Aligning a building along a north–south axis, with the building facing south (in the north where
> the wind is coldest in winter)."

> "Northern courtyards are typically open and face south to allow the maximum exposure of the
> building windows and walls to the sun while keeping out the cold north winds."

en.wikipedia "Siheyuan" (https://en.wikipedia.org/wiki/Siheyuan) gives the same for the principal
building:

> "The building positioned to the north and facing the south is considered the main house (正房,
> _zhèngfáng_)."

So "south is the formal orientation a BUILDING takes" is readable and the reason given is sunlight
and the winter wind rather than auspiciousness. The record's claim is about a GATE, and on that the
same Siheyuan article cuts the other way:

> "The gate was made at the southeast corner which was the "wind" corner, and the main house was
> built on the north side which was believed to belong to "water", an element to prevent fire."

A compound whose HALL faces south commonly puts its GATE at the southeast corner, not on the axis -
which is a different rule from the one the record states, and the record's fallback ("the fallback
when nothing is said is south") is about the gate. Nothing read says a gate's auspicious default is
due south. Verdict STILL ABSENT, with the caution that the nearest readable passage describes a
different convention rather than this one.

---
### `homesteads.html` fn-36

**CITED** - the sentence the record labels "A GUESS - no readable page supports it" now has a
readable page behind it, and it is the very DOI the last pass was refused.

The last pass tried https://doi.org/10.1177/23998083231184884 and got a 403 from SAGE. Unpaywall
(https://api.unpaywall.org/v2/10.1177/23998083231184884) reports the article as open access
(`is_oa: true`, hybrid) with a full-text copy in the University of Gavle repository, and that copy -
the published version of record - downloads and reads:

https://hig.diva-portal.org/smash/get/diva2:1773446/FULLTEXT01

Ma, L., Brandt, S. A., Seipel, S. and Ma, D. (2023), "Simple agents - complex emergent path systems:
Agent-based modelling of pedestrian movement", *Environment and Planning B: Urban Analytics and City
Science*.

> "Hillier and Iida (2005) used a representation of street segment-based graphs and found a good
> correlation between the angular weighted ‘choice’ (betweenness centrality) and observed pedestrian
> movement in four areas of London, where pedestrians are believed to have angular preferences of
> fewest turns or least angle changes."

"angular preferences of fewest turns or least angle changes" is exactly the record's "consciously or
unconsciously minimize the number and severity of turns", in a peer-reviewed paper, on a page anyone
can open. The claim can stop being labeled a guess. The same paper states its own agent's rule in
terms the lane-bending rule can use directly:

> "The global conception that is kept in mind in each agent is the aim to ‘Go straight!’ all along to
> its destination. This means that an agent has an OD plan from the beginning and continues facing
> straight towards its destination while searching for the next patch to step on. In this way, the
> agent can end up with a path with the least detoured distance from the straight line."

Note for the session: the turn preference is reported here as Hillier and Iida's finding, so the
primary to cite alongside is Hillier, B. and Iida, S. (2005), "Network and psychological effects in
urban movement" - this paper is where it can be READ and quoted, which is what the rule requires.

---

### `cities/government.html` fn-37

**CITED** for the ward areas; **STILL ABSENT** for the date the ward system was pulled down.

en.wikipedia "Chang'an" (https://en.wikipedia.org/wiki/Chang%27an), "Legacy":

> "Its grid of more than one hundred walled wards culminated a centuries-old tradition of Chinese
> capital planning."

> "Chang'an's walled and gated wards were much larger than conventional city blocks seen in modern
> cities, as the smallest ward had a surface area of 68 acres, and the largest ward had a surface
> area of 233 acres (0.94 km2). The walls enclosing each ward averaged 9 to 10 ft (3.0 m) in
> height."

68 acres is 27.5 ha and 233 acres is 94.3 ha, so the record's "30 to 80 hectares apiece" is the
middle of the real range rather than its ends - the true spread is about 27 to 94 ha, which makes
the record's point MORE strongly, not less: the largest ward really is larger than a whole
provincial city at the scale these maps draw. Consider restating it as "roughly 27 to 94 hectares"
and citing this passage. The ward wall's height, 9 to 10 ft, is a bonus the record does not
currently carry and would want if it ever drew one.

Not found: a readable page dating the abolition or breakdown of the ward system. en.wikipedia "Song
dynasty" was read in full through the extracts API and matches nothing on "ward system", "walled
ward", "curfew", "marketplace" or "night market"; the Chang'an article's own note that night markets
"thrive[d] ... despite government efforts in the year 841 to shut them down" is evidence that the
curfew was already failing in the late Tang, but it is not a date for the system's end. The
secondary that would settle it - Heng Chye Kiang, *Cities of Aristocrats and Bureaucrats* - was not
reachable without a search engine.

---

### `archetypes.html` fn-87

**FOR THE GM.** The work the claim rests on exists, is exactly on point, and is not open.

- Title: "FROM SMALL FRY TO BIG FISH: REPRESENTING THE RISE OF JIUJIANG TOWNSHIP, NANHAI COUNTY,
  1395-1657"
- Author: Steven B. Miles
- Year: 2003
- Journal: *Ming Studies*
- DOI: 10.1179/014703703788762953
- URL tried: https://api.unpaywall.org/v2/10.1179/014703703788762953 (the DOI resolver itself was
  tried by the previous pass and redirects to Taylor & Francis, paywalled)
- What blocked it: Unpaywall answers `is_oa: false`, `oa_status: "closed"`, `best_oa_location:
  null`, and lists NO open location at all - no repository copy, no author manuscript, no preprint.
  So this is not a fetcher problem: there is nothing on the public web to read.
- What it would settle: Jiujiang township's rise between 1395 and 1657 on fry collected from the
  Xijiang, which is the whole of the record's "the delta's fry center from the Ming".

The other half of the paragraph - the Sangyuanwei proverb about the men trading fry and the women
feeding the silkworms - was not reached: the FAO GIAHS page for the dike-pond system is the obvious
place for it and the URL the record's registry points at returns 404, and finding the current one
needs a search engine.

---

### `archetypes.html` fn-88

**FOR THE GM.** Same shape as fn-87: the right work, closed everywhere.

- Title: "Household Size, Household Structure, and Developmental Cycle of a Japanese Village:
  Eighteenth to Nineteenth Centuries"
- Author: Futoshi Kinoshita
- Year: 1995
- Journal: *Journal of Family History*, vol. 20 no. 3
- DOI: 10.1177/036319909502000302
- URL tried: https://api.unpaywall.org/v2/10.1177/036319909502000302; the previous pass tried
  https://journals.sagepub.com/doi/abs/10.1177/036319909502000302 and was given 403, and SAGE was
  NOT retried here under the one-attempt rule.
- What blocked it: Unpaywall answers `is_oa: false`, `oa_status: "closed"`, no OA locations. The
  403 was therefore not the fetcher - the article is closed by license as well.
- What it would settle: the mean household size of one Tohoku village rising "from about five to six
  persons" over 1760-1870, the nearest historical figure to the setting's canonical five.

Worth saying plainly, because the record already says it: this footnote supports a SETTING number
(the GM's "median household size is generally assumed to be 5"), which is canon and exempt from the
citation rule. The absence note costs the page nothing; it is the historical gloss that is
unciteable, and the record already presents it as support rather than as the basis.

---
### `cities/hinterland.html` fn-8

**CITED** for the pattern and for a real structure count; one sub-clause points the OTHER way.

Two zh.wikipedia articles carry the gate suburb as a described place rather than as a dictionary
word, which is what the last pass could not find (zdic gives only the definition, Baidu Baike
refuses automated fetches and was not retried).

(a) A road-driven suburb with a market and lodging, and a COUNT. zh.wikipedia 马甸清真寺
(https://zh.wikipedia.org/wiki/%E9%A9%AC%E7%94%B8%E6%B8%85%E7%9C%9F%E5%AF%BA):

> Translated from the Chinese by this project: "After the Ming built the city of Beijing, Madian was
> the trunk road running north from Deshengmen to Qinghe, Shahe, Changping, the Thirteen Tombs,
> Gubeikou, Yanqing and Zhangjiakou. In the Ming and Qing, the horse trains that came each year from
> the north and northwest to render tribute to the court had their best horses chosen as imperial
> horses and offered to the imperial house, their second grade distributed among the civil and
> military officials, and the horses culled from them sold on the spot for common use. Travelling
> merchants trading in horses, cattle, sheep and camels also commonly lodged at Madian. Madian
> naturally formed a market."

Original: 「明朝建北京城后，马甸便是从德胜门北通清河、沙河、昌平、十三陵、古北口、延庆、张家口的要道。明清时期，每年从北方和西北来为朝廷进贡的马队，将马中的上等选为御马进贡皇家，次等分赠文武百官，淘汰下来的马匹作为民用就地出售。贩运马、牛、羊、骆驼的客商也常在马甸住宿。马甸自然形成交易市场。」

> Translated from the Chinese by this project: "Because the horse, cattle, sheep and camel trades
> expanded, the horse market moved to the guanxiang outside Deshengmen (at its height there were 48
> horse inns), the cattle inns moved to Beixiaoguan, and the sheep inns gathered at Madian."

Original: 「因马、牛、羊、骆驼行业扩大，马市迁到德胜门外关厢（鼎盛时期有马店48家），牛店迁到北小关，羊店集中在马甸。」

This is the record's paragraph almost item by item: a gate that carries a long-distance route, a
market on the ground immediately outside it, and lodging for travelers and traders. And it carries
the thing the record says is a guess - a NUMBER. Forty-eight horse inns in one Beijing gate's
guanxiang at its height is one trade's premises at the busiest gate of a capital; the map's "ten to
forty structures at a busy gate" for a provincial seat sits sensibly below it and can now be argued
from something rather than asserted. It remains a calibration rather than a measurement of a
provincial gate, and should be labeled that way.

(b) A guanxiang as an overflow quarter, formally established and streeted. zh.wikipedia 张家口堡
(https://zh.wikipedia.org/wiki/%E5%BC%A0%E5%AE%B6%E5%8F%A3%E5%A0%A1):

> Translated from the Chinese by this project: "The guanxiang came about because the population
> inside Zhangjiakou Fort increased and it could not but expand outward to solve the living space of
> the added population."

Original: 「关厢是由于张家口堡内人口增加，不得不向外扩展以解决新增人口居住的空间。」

> Translated from the Chinese by this project: "Within the guanxiang there gradually formed
> crossroads such as Wucheng Street and Dongguan Street, Xiaonanguan Street and Dongguan Street, and
> Xiguan Street, as well as roads such as Beiguan Street."

Original: 「关厢内逐渐形成武城街和东关街、小南关街和东关街、西关街等十字街以及北关街等道路。」

The same article dates the establishment - 「成化十六年（1480年），张家口堡经过扩建，设关厢」,
"In the sixteenth year of Chenghua (1480) Zhangjiakou Fort was enlarged and a guanxiang was set up"
- and notes that the historical disagreement about the fort's size "may be related to whether the
record includes the guanxiang" (「此差距可能是和记载是否包含关厢有关」), which is a nice sign that a
guanxiang was a substantial piece of settled ground rather than a fringe.

The sub-clause that this evidence does NOT support: "at the busiest gates the suburb commonly filled
before the walled ground inside it had". Zhangjiakou's guanxiang formed for the opposite reason -
the walled ground filled FIRST and the overflow went outside. One case is not a refutation of a
general pattern, but the record currently asserts the pattern with no source and the one readable
case runs against it, so it should be softened or dropped unless a reader with a search engine finds
the pattern stated somewhere.

---

### `cities/hinterland.html` fn-4

**CITED** for the guanxiang half - the one the last pass lost when Baidu Baike refused it.

The footnote hangs (twice) on "the belt hugging the gates was the COMMERCIAL commoner suburb
(guanxiang)". The two passages quoted at fn-8 above are the evidence, and they are exactly that: a
livestock market and forty-eight inns outside Deshengmen, a streeted overflow quarter outside
Zhangjiakou. Neither page is Baidu Baike and neither was refused. The record's reading - "close to
the gate describes the wrong land use" for a genteel quarter - follows from them directly.

The rest of this footnote's paragraph (fragmented elite holdings, the individually fortified rural
estate, the absentee landlord pulled inward by exam and office, the 2-15 mile distance) is
separately marked "(unsourced)" in the record and was NOT searched here - it needs a general search
engine and the batch's budget was spent.

---

### `cities/defenses.html` fn-18

**STILL ABSENT.**

The word is real and the street exists; the RULE the footnote states - a deliberately kept clear lap
of ground inside the rampart, for moving troops along the wall - was not found on any readable page.

What was searched, and what came back:

1. `順城街 城墙 内侧 马道 环城 街道 清代 城市` (WebSearch, before the budget ran out). Candidates
   returned: sohu.com "带你逛城墙-登城马道" (a blog aggregator, not worth fetching as a source);
   thepaper.cn "盘点：细数中国的古城墙"; zh.wikipedia 城墙; zh.wikipedia 明清北京城; zhihu.com
   "北京城门"; baike.baidu.com 西安城墙 (the host that refused the last pass, not fetched);
   blog.sina.com.cn "城墙内的城市?"; archcollege.com. None is a source this project would cite and
   none was reported to carry the clear-lap rule; what the search summary DID report is the 登城马道,
   the ramp up onto the wall, which is a different object.
2. zh.wikipedia article search for 顺城街 (MediaWiki API). Eight hits, every one a modern street
   NAMED 顺城街 rather than an article about the type - 昆明顺城街清真寺, 吕祖宫 (on 复兴门北顺城街),
   怀远门站 (on 西顺城街), 金城坊街, 兵马司胡同, 方亭街道, 广安门南街, 郑州市第三人民医院.
3. zh.wikipedia 广安门南街, read in full. It gives the naming rule and nothing else:

> Translated from the Chinese by this project: "In 1965 the stretch from Guang'anmennei Avenue to
> Baizhifang West Street was named "Guang'anmen South Shunchengjie", so named because it lies beside
> the city wall south of Guang'anmen in Beijing's outer city."

Original: 「1965年，广安门内大街至白纸坊西街段定名“广安门南顺城街”，因位于北京外城广安门以南的城墙旁边而得名。」

That establishes that 顺城街 means "the street that follows the wall" and that such streets ringed
Beijing - but it is a 1965 naming decision, not a statement that the ground was kept clear for
troops.
4. zh.wikipedia 北京城墙 and 西安城墙, both read in full through the extracts API. Neither contains
   顺城 at all. 西安城墙 gives the wall's own dimensions and the ten 登城马道 (ramps up onto the
   wall, "城墙的内侧有十条登城马道，其中四座城门处各有一条") - again the ramp, not the lap.

So the mechanism is attested only by the street name. A reader with a search engine should look for
the military-manual side of this (the Ming 守城 literature on keeping the foot of the wall clear),
which is where the rule will be if it is anywhere.

---

### `cities/fabric.html` fn-17

**STILL ABSENT, and correctly so** - nothing was searched, and the note itself says why.

Reported for completeness rather than as a failure: the assertion this footnote hangs on is the GM's
2026-07-23 ruling about the SETTING (a gated merchant compound is a granted right, of a piece with
the New Year audience and the hereditary surname), and the GM's campaign notes are the documented
exception to the citation rule (GM 2026-09-07). There is no historical claim here to read a source
against, and a citation attached to it would misrepresent a ruling as a finding.

One thing a reader could add if the record ever wants it: the surname privilege in the paragraph has
a real Japanese counterpart, myoji-taito, the grant of a surname and the right to wear a sword to
non-samurai. It was not read for this batch because the claim it would support is not the one the
footnote makes.

---

### `vegetation.html` fn-91

**CITED.**

en.wikipedia "Paddy field" (https://en.wikipedia.org/wiki/Paddy_field) draws the contrast the record
needs - flat-ground paddies against terraced ones - in one sentence, and gives the riser height that
makes the record's "imperceptible" quantitative:

> "Some Mumun paddy fields in flat areas were made of a series of squares and rectangles, separated
> by bunds approximately 10 cm in height, while terraced paddy fields consisted of long irregular
> shapes that followed natural contours of the land at various levels."

A flat area gives squares and rectangles divided by bunds four inches high; a slope gives long
irregular shapes following the contours at different levels. That is the record's rule almost word
for word - "long narrow curved strips following the contour with a riser between them" on a slope,
"a flat patchwork whose level steps are imperceptible" on a gently tilted floor - and at 1 px = 1 ft
a 10 cm bund is a tenth of a pixel, which is what "imperceptible" means on the sheet.

The same article ties terracing to steepness twice:

> "Fields can be built into steep hillsides as terraces or adjacent to depressed or steeply sloped
> features such as rivers or marshes."

> "Steep terrain on Bali resulted in complex irrigation systems, locally called subak, to manage
> water storage and drainage for rice terraces."

What it does NOT give is a slope THRESHOLD - a gradient above which terracing appears - so the map's
decision about which settlements get risers is still a judgment rather than a number. The Mumun
observation is Korean Bronze Age rather than Chinese or Japanese; it is being used for the geometry
of wet-rice ground on flat versus sloping land, which does not turn on the period, and that limit
should be stated where it is cited.

---

### `urban-features.html` fn-62

**STILL ABSENT** for the chao process as the record describes it; partially cited for the outline.

What is readable. en.wikipedia "Finery forge" (https://en.wikipedia.org/wiki/Finery_forge):

> "Fining was practiced in ancient China by the mid-3rd century BC, although Wagner notes that its
> precise chronology and geographical origins are uncertain. During the Han dynasty (202 BC-AD 220),
> cast iron was converted into wrought iron by several methods; solid-state decarburization is
> securely attested, while fining also appears to have been practiced. Small hearths excavated at
> several Han-period iron production sites, including Tieshenggou, have been interpreted as fining
> hearths."

en.wikipedia "History of metallurgy in China"
(https://en.wikipedia.org/wiki/History_of_metallurgy_in_China):

> "In China, blast furnaces produced cast iron, which was then either converted into finished
> implements in a cupola furnace, or turned into wrought iron in a fining hearth."

Between them these support the paragraph's frame - blast-furnace cast iron converted to wrought iron
by fining, the practice running back to the Han - on pages anyone can open, and they name Donald
Wagner as the authority, which is the right primary to chase.

What is NOT supported by anything read: the name chao 炒 and the "stir-frying" gloss; Song
Yingxing's rectangular hearth set a few chi from the blast-furnace outlet and a few cun lower; the
workers on the protective wall; the willow poles burning down 2-3 cun per cycle; wuchaoni; and the
site the record names, Xuxiebian in Sichuan - the Finery forge article names a DIFFERENT Han fining
site, Tieshenggou in Henan, and Xuxiebian appears on nothing read.

Hosts tried and what happened: muse.jhu.edu was the last pass's block and was NOT retried.
donwagner.dk - Donald Wagner's own open site, which carries his translations of the Tiangong Kaiwu
iron chapter and would settle most of the list - returned HTTP 454 from a hosting error page
(splash.simply.com), i.e. the site is down rather than refusing me. web.archive.org was tried once
for it and returned HTTP 429 (rate limited). That is the single most promising route for this note
and it is worth one clean attempt by the next reader: an archived capture of donwagner.dk.

---

### `urban-features.html` fn-74

**FOR THE GM** - with the unusual twist that the paper IS open access by license and still cannot be
read by any fetcher available here.

- Title: "The Kabu-ido system and factors affecting local groundwater extraction control: case study
  of a customary groundwater management in Japan"
- Year: 2022
- Journal: *Water History*
- DOI: 10.1007/s12685-022-00302-1
- License: **CC-BY**, confirmed twice - Unpaywall
  (https://api.unpaywall.org/v2/10.1007/s12685-022-00302-1) answers `is_oa: true`, `oa_status:
  "hybrid"`, `license: "cc-by"`, and the Semantic Scholar graph API
  (https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s12685-022-00302-1) answers
  `openAccessPdf: {status: "HYBRID", license: "CCBY"}`.
- The one location either index knows:
  https://link.springer.com/content/pdf/10.1007/s12685-022-00302-1.pdf
- What blocked it: every request to link.springer.com returns HTTP 200 with a 3,038-byte HTML stub
  rather than the PDF - the article landing page does the same (303 to `idp.springer.com/authorize`)
  - so the block is a bot wall in front of an openly licensed paper, not a paywall. OpenAlex
  (https://api.openalex.org/works/doi:10.1007/s12685-022-00302-1) lists no second location; a
  fatcat/scholar.archive.org lookup returned nothing parseable; the Wayback Machine has no capture of
  the PDF URL (HTTP 404 on `web/2024id_/`).
- What it would settle: the kabu-ido finding itself - villages capping their own well numbers to
  limit conflict - which is the whole of this footnote and the one piece of evidence that cuts
  against the project's deliberate 2-3x well liberty.
- What the GM can do that this reader cannot: open the Springer PDF in a browser. It is CC-BY, so
  once read it can be quoted at length with no rights question at all.

---

### `buildings.html` fn-71

**FOR THE GM** - the primary is named, it is in an open national repository, and the repository rate
limited me.

- Title: 「史跡高山陣屋跡」 (translated from the Japanese by this project: "Historic Site: the Remains
  of the Takayama Jinya")
- Author: 上嶋善治 (Ueshima Zenji)
- Year: 1992
- Series/publisher: 『岐阜県文化財保護センター調査報告書1』, 財団法人岐阜県文化財保護センター
  (Gifu Prefecture Cultural Property Protection Center, Survey Report 1)
- Where it should be readable: 全国遺跡報告総覧 (Comprehensive Database of Archaeological Site
  Reports), Nara National Research Institute for Cultural Properties -
  https://sitereports.nabunken.go.jp/ - which hosts scanned excavation reports in full and free.
  ja.wikipedia 高山陣屋 links this report there by name, which is how it was identified.
- URL tried:
  https://sitereports.nabunken.go.jp/ja/search?SEARCH_STRING=%E9%AB%98%E5%B1%B1%E9%99%A3%E5%B1%8B
- What blocked it: HTTP 429 (Too Many Requests), twice, several minutes apart. This is a rate limit,
  not a refusal - the report is almost certainly there and downloadable.
- What it would settle: the 3,000 tsubo site / 1,000 tsubo built figures, and with them the 37-42%
  coverage band that the record currently carries as a GUESS "pending that report".

Also tried and empty: the official site https://jinya.gifu.jp/ and https://jinya.gifu.jp/about/,
which carry the history, the opening hours and the 1996 restoration (「1830年（天保元年）の絵図を基に
約20億円を掛けて」 - based on an 1830 drawing, at a cost of about 2 billion yen) but no area in tsubo
or square meters; ja.wikipedia 高山陣屋, read in full, which lists the surviving buildings by name
and gives no area either; and a guessed query URL at kunishitei.bunka.go.jp (the Agency for Cultural
Affairs' designated-property database, which records a designated AREA for every historic site),
which returned 404 - the right database, the wrong URL, and finding the right one needs a search
engine.

---

### Addendum to `urban-features.html` fn-84 - upgraded to CITED

After the entry above was written, the surface half of the claim was found. ja.wikipedia 舗装
(https://ja.wikipedia.org/wiki/%E8%88%97%E8%A3%85), "日本":

> Translated from the Japanese by this project: "However, until the automobile appeared in Japan in
> 1899, it may be said that nearly all roads were unpaved. And even after motor traffic began to be
> seen, any road off the trunk roads, even in central Tokyo, was entirely unpaved."

Original: 「ただし、日本に自動車が登場する1899年までは、ほぼ全ての道路は非舗装といってもよい状況であった。また、自動車の通行が見られるようになった後も、東京都心ですら幹線道路から外れた道路となれば、全て非舗装という状態であった。」

The same section lists what WAS paved before that, which is the cost argument the record makes:

> Translated from the Japanese by this project: "In the Edo period, stone paving was made at Hirado
> and Nagasaki around its beginning, and in 1680 stone paving was made on the Hakone mountain road at
> a cost of over 1,400 ryo; and in Kyoto in 1805, between Sanjo Ohashi and Otsu Hatcho on the Tokaido
> (the Sanjo highway, the Otsu highway), a stone-paved road was made that separated the ox-and-horse
> way from the man-and-horse way."

Original: 「江戸時代には、初期ごろに平戸や長崎で石畳舗装が造られており、1680年に箱根の山越え道に1400両あまりをかけて石畳が造られたほか、1805年の京都では、東海道（三条街道・大津街道）の三条大橋 - 大津八丁間において、牛馬道と人馬道を分けた石畳道（大津街道軌道舗装）がつくられている。」

Three named projects in two and a half centuries, one of them costing over 1,400 ryo for a single
mountain pass, against "nearly all roads were unpaved" - that is the record's "packed earth,
unpaved, paving being far beyond a quarter's means", evidenced. So fn-84 is CITED: the width and the
single track from ja.wikipedia 路地, the unpaved surface and its cost from ja.wikipedia 舗装.

---

---

## Closing note

Sections below the table are in the order they were worked, not batch order; every one of the 20 has
a section. Counting the compound verdicts once each: **11 CITED** (three of them with a
contradiction or a gap named beside the citation), **5 STILL ABSENT**, **4 FOR THE GM**.

Three findings the session should act on before anything else, because they change what the record
SAYS rather than only what it cites:

1. `cities/fabric.html` fn-20 - the roji is drawn at 12 ft and was 3 to 6 ft. Either a map drawing
   convention to declare, or a number to correct.
2. `cities/defenses.html` fn-16 - Nanjing's Zhonghua gate tunnels are 4.8 to 5.35 m, about 16 to 18
   ft, not the 23 ft the record gives. The 13-23 ft band itself survives.
3. `homesteads.html` fn-36 - a sentence currently labeled "A GUESS - no readable page supports it"
   has a peer-reviewed open-access page supporting it word for word. The guess label is now wrong,
   and an unlabeled guess is the failure this project names; a guess label on a finding is the same
   error pointed the other way.

Two hosts refused the last pass and were deliberately NOT retried here, per the one-attempt rule:
baike.baidu.com (fn-22's Pingyao yamen, fn-4's 关厢) and muse.jhu.edu (fn-62). journals.sagepub.com
was not retried either - Unpaywall answered the question about it instead, twice, and in one of the
two cases (fn-36) that is how the citation was found.

