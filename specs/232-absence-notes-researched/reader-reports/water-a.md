# Reader report: water-a-canals-and-ditches (37 notes)

Read 2026-09-12. Every fetch below was made by this agent; nothing is reported from a
search-result snippet. Where a host refused the default fetcher, the page was retried with
`curl -sL -A "Mozilla/5.0 ... Chrome/120.0 Safari/537.36"`, and open-access status was asked of
Unpaywall / OpenAlex before any document was called blocked. Five hosts that this project or the
default fetcher had written off - `chinaknowledge.de`, `knowledgebank.irri.org`,
`engr.colostate.edu`, `egyankosh.ac.in`, `zjw.sh.gov.cn` - all serve their full content to curl.

**Session limit reached.** The WebSearch budget (200 calls) was exhausted partway through, by this
session as a whole. Eight planned queries were refused and are listed at the end; the work
continued through direct fetches. Those eight gaps are flagged in the notes they affect.

## Verdicts at a glance

| # | page / footnote | verdict |
|---|---|---|
| 1 | `archetypes.html` fn-91 | CITED |
| 2 | `archetypes.html` fn-93 | STILL ABSENT |
| 3 | `cities/capitals.html` fn-65 | CITED |
| 4 | `cities/defenses.html` fn-14 | STILL ABSENT (one leg supported) |
| 5 | `cities/defenses.html` fn-15 | CITED |
| 6 | `cities/fabric.html` fn-18 | STILL ABSENT |
| 7 | `cities/hinterland.html` fn-10 | STILL ABSENT |
| 8 | `cities/river-cities.html` fn-14 | FOR THE GM |
| 9 | `cities/river-cities.html` fn-15 | CITED |
| 10 | `cities/river-cities.html` fn-16 | CONTRADICTED (in part) |
| 11 | `cities/river-cities.html` fn-17 | STILL ABSENT |
| 12 | `cities/river-cities.html` fn-18 | STILL ABSENT |
| 13 | `fields.html` fn-25 | CITED |
| 14 | `fields.html` fn-35 | STILL ABSENT |
| 15 | `fields.html` fn-47 | CITED |
| 16 | `fields.html` fn-80 | CITED |
| 17 | `fields.html` fn-82 | STILL ABSENT |
| 18 | `fields.html` fn-83 | CITED |
| 19 | `fields.html` fn-85 | STILL ABSENT |
| 20 | `fields.html` fn-87 | STILL ABSENT |
| 21 | `fields.html` fn-88 | STILL ABSENT |
| 22 | `homesteads.html` fn-41 | CITED |
| 23 | `homesteads.html` fn-99 | CITED (part of the paragraph only) |
| 24 | `vegetation.html` fn-83 | CITED (part of the sentence only) |
| 25 | `vegetation.html` fn-92 | CITED |
| 26 | `water.html` fn-1 | CITED |
| 27 | `water.html` fn-2 | STILL ABSENT |
| 28 | `water.html` fn-25 | CITED |
| 29 | `water.html` fn-28 | CITED (replacement passage) |
| 30 | `water.html` fn-29 | CITED |
| 31 | `water.html` fn-30 | CITED |
| 32 | `water.html` fn-38 | CITED |
| 33 | `water.html` fn-48 | STILL ABSENT |
| 34 | `water.html` fn-49 | CITED |
| 35 | `water.html` fn-70 | CITED |
| 36 | `water.html` fn-73 | STILL ABSENT |
| 37 | `ways.html` fn-11 | CITED |

Totals: 21 CITED, 14 STILL ABSENT, 1 FOR THE GM, 1 CONTRADICTED.

## The four documents that carry most of this batch

Named once here because a dozen notes below point at them.

**A. T/JSSLKX 002-2021, 小型農田水利工程規劃設計導則 (Guideline for the planning and design of
small farmland water-conservancy works), Jiangsu Provincial Water Conservancy Survey and Design
Association, draft for comment, 2021.** Openly readable PDF, no paywall, no login:
<http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (curl, HTTP 200, 622 KB;
the default fetcher was never tried on it). Text layer is clean. Its own §9.1.6 says its canal
designs must also satisfy GB 50288, which makes it the nearest openly readable carrier of the GB
50288 numbers this record has been trying to reach. **Limit to state in any registry entry:** a
modern (2021) Chinese design standard for concrete-lined and machine-worked schemes; it is
evidence for the geometry and the stated reasons, not for what a premodern earthwork measured.

**B. IGNOU / eGyanKosh, "Unit 10: Silt Control" (Irrigation Engineering course unit), Indira
Gandhi National Open University.** <https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf>
- HTTP 200 with curl, 540 KB. **Two caveats the GM should see.** (i) The host's TLS chain is
broken: curl needs `-k` and the default fetcher reports "unable to verify the first certificate".
A person in a browser gets a certificate interstitial and can click through, so the page is
readable by a human but not cleanly. (ii) It is a scan, and its text layer is OCR-damaged: the
degree sign renders as an apostrophe (`30'` for 30 degrees) and stray letters appear (`rl` for
`a`). Quotations below reproduce the text layer exactly, damage included; a quote-check against
the rendered PDF will see the clean form.

**C. Ulrich Theobald, "caoyun 漕運, transport of tribute grain", ChinaKnowledge.de, 21 Dec 2015.**
<http://www.chinaknowledge.de/History/Terms/caoyun.html> - the default fetcher fails with an SSL
handshake error; curl returns the whole article (HTTP 200, 44 KB). A signed scholarly reference
work by a Tübingen sinologist, with a bibliography - serious reference, not an AI encyclopedia.

**D. ja.wikipedia.org 「畦」** <https://ja.wikipedia.org/wiki/畦> - readable, HTTP 200. Tertiary,
and it says so of itself: 「畦の形状や寸法には、近現代の工事によって設けられた畦畔を除いては定型がなく、
その寸法も地域や土質によって様々である。」(English translation by this agent: "Apart from bunds built
by modern works, aze have no standard shape or dimensions, and their dimensions vary by region and
by soil.") That sentence is the honest limit on every bund figure in this batch and should travel
with them.

---

### `archetypes.html` fn-91

**CITED.**

URL: <https://ja.wikipedia.org/wiki/畦>

Passage, verbatim (Japanese):

> ほ場整備によって新たに築かれる畦の場合、天端幅はおおむね300mmから600mm程度で、高さが1m未満の法面では勾配を縦1:横1（45度）とすることがある。

English translation by this agent (original above kept as the checker's anchor): "In the case of an
aze newly built by field consolidation, the crown width is roughly 300 mm to 600 mm, and where the
batter is under 1 m high the slope is sometimes taken as 1 vertical to 1 horizontal (45 degrees)."

Second passage, same page, verbatim:

> 水田を回る際の道としての役割も持っているもののことを、畦道（あぜみち）

English translation by this agent: "One that also serves as a path when going round the paddy is
called an azemichi."

Third passage, same page, verbatim:

> 畦道と言われるものは幅が広く、私的な「畦」兼農作業のための通路または私的な農道と考えてよい場合がある。

English translation by this agent: "What is called an azemichi is wide, and may in some cases be
thought of as a private aze that doubles as a passage for farm work, or as a private farm road."

How it supports the claim: it gives the bund a measured crown (300-600 mm) and 45-degree batters,
and it names the form in which the ridge carries a footpath along its top. The record's "about
three feet all told" is then arithmetic on those numbers - a 30-60 cm crown plus two 45-degree
batters over a 20-50 cm ridge gives a 70-160 cm footprint, inside which 3 ft (91 cm) sits - and the
arithmetic is the record's own, not the page's. **No page read states three feet.** State the crown
and the batter, and label the total a derivation.

---

### `archetypes.html` fn-93

**STILL ABSENT.**

Queries run: `azemame 畦豆 soybean planted on paddy levee aze`;
`paddy field drainage ditch along lowest side bund embankment top of bank layout terrace`;
`earthen channel bend erosion outside deposition inside sharp corner rounds itself maintenance`.

Candidates and what happened:

- ja.wikipedia 「畦」 <https://ja.wikipedia.org/wiki/畦> - FETCHED and read in full. It confirms the
  bund is re-worked annually and that it slumps between harvest and spring
  (「稲作の工程には、水を張る前に毎年修理を行う「畦作り」または「畦塗り」があり」 - "the rice-growing
  cycle includes an annual repair before the field is flooded, called azetsukuri or azenuri";
  「イネの収穫から春の農作業開始までの間に畦が崩れ」 - "between the rice harvest and the start of
  spring farm work the aze collapses"). **Neither passage distinguishes the junction from the rest
  of the bund**, which is the whole of the assertion. Nothing read says a crossing is the most
  worked point, that four basins push water at it, or that it is the first place to be re-piled.
- PMC7538448 (paddy levee grasslands, below) - FETCHED and read. Levee maintenance is mowing; no
  junction.
- FAO "Irrigation water management: Irrigation methods", ch. 5
  <https://www.fao.org/4/r4082e/r4082e06.htm> - FETCHED (HTTP 200). Covers canal erosion, drop
  structures, division boxes, turnouts, checks. Nothing on bund junctions.

Assessment: this is a plausible physical argument that the record appears to have reasoned out
itself. It should stay a labeled guess unless someone finds a field-maintenance study of bund
repair - the shape of source that would carry it is an agricultural-engineering survey of
labor-hours by bund element, and nothing of that kind surfaced.

---

### `cities/capitals.html` fn-65

**CITED.**

URL: <https://en.wikipedia.org/wiki/Hori_River_(Nagoya)>

Passage, verbatim:

> The river is a man-made canal excavated in 1610 during the construction of Nagoya Castle by order of Fukushima Masanori to allow ships to bring goods to the city.

Corroborating passage, second page, verbatim
(<https://centrip-japan.com/spot/743.html>, Centrip Japan, Chubu Centrair International Airport's
tourism site - a promotional page, weaker provenance, offered only as corroboration):

> The Hori River runs from Nagoya Castle to Nagoyakō (Port of Nagoya).

How it supports the claim: together they carry "Nagoya cut the Horikawa from the castle to the
sea" - man-made, dug 1610 for Nagoya Castle, running from the castle to the port.

**Two discrepancies to record rather than hide.** (i) The English Wikipedia article gives the river
16.2 km of total length; the ja.wikipedia page the previous pass read gives the original canal as
6 km, and the modern river includes reaches the 1610 cut did not. (ii) The previous pass's note
says the ja page gave "not width", implying the record wanted a canal width here. **No page read in
this pass gives the Horikawa a width.** If fn-65 is carrying a width, it is still unsupported and
should be split off.

---

### `cities/defenses.html` fn-14

**STILL ABSENT** for the assertion as written - but one leg of it now has a passage, and the record
could be narrowed onto that leg instead of dropped.

Query run: `karamete-mon rear gate Japanese castle otemon main gate defense`.

What was found and READ:

- Japanese Wiki Corpus, "Karamete-mon Gate"
  <https://www.japanesewiki.com/building/Karamete-mon%20Gate.html> - FETCHED, HTTP 200. Verbatim:

  > one of the castle gates located at the karameteguchi (back gateway), as opposed to Ote-mon Gate (main gate) being at the front

  and, verbatim:

  > was very securely designed to be adequately guarded by a small number of people, in contrast to a large koguchi (castle entrance), such as the Ote-mon Gate

  and, verbatim:

  > allowed people, including the feudal lord, to escape from a castle or escape to outside the walls surrounding a castle

  This supports the karamete-mon leg: a rear gate opposite the main approach, deliberately small,
  held by few, used to get people out. Provenance note: the Japanese Wiki Corpus is a
  translation of Japanese Wikipedia produced under a Japanese government project - tertiary,
  and a translation of a tertiary source at that.

What is still unsupported: **nothing read mentions the umon (small walled-up postern) or the
shuimen (water gate) at all, and nothing read sets any of the three against the European sally
port.** The comparison is the assertion, and the comparison has no source. A registry entry could
honestly say "the karamete-mon is attested as a small, lightly held rear gate opposite the main
approach" and leave the three-way comparison labeled as the record's own.

Not fetched, and why: the tourism and hobbyist pages the query returned (japan-travel-note.com,
followingtheshogun.com, samurai-castles.hatenablog.jp) are secondary-at-best travel writing and
would not have carried a comparative fortification argument.

---

### `cities/defenses.html` fn-15

**CITED.**

URL: <https://en.wikipedia.org/wiki/Fortifications_of_Xi%27an>

Passage, verbatim:

> There are four watch towers, located at the corners and the moat that surrounds the wall has a width of 18 metres (59 ft) and depth of 6 metres (20 ft).

How it supports the claim: Xi'an's Ming wall is the standing example of a Chinese provincial-capital
enceinte, and its moat is measured at 18 m / 59 ft across. The record takes a provincial seat's moat
at about 66 ft; 59 ft is the same order and the same tier of place, which is what the claim needs.

**Say the number honestly:** 18 m is 59 ft, not 66. If the record wants to keep 66 ft it should say
that the drawn figure sits a little above the one measured example read, or move to 59-60 ft.

Tertiary source; the article's own citation for the figure was not chased (the search budget ran
out before that could be done).

Two further moat widths appeared in a search summary (Kaifeng ~16.66 m, Jingzhou 30 m). **Neither
page was read, so neither is cited** - they are recorded here only as evidence that the 15-30 m
band is where a Chinese walled-city moat sits.

---

### `cities/fabric.html` fn-18

**STILL ABSENT.**

No query was run for this note and the reason is the note's own: the last pass recorded "none was
sought - the doctrine is the GM's, and the reasoning given for it ... is this record's own." That is
correct. The assertion has two halves, and neither is a research question this reader can settle:

- "a wall footed in water is undermined" is a statement of engineering common sense the record
  states in its own voice;
- "a canal or a dock edge is working waterfront ... a private wall may come up to the quay but never
  stand in it" is a GM ruling of 2026-07-19 about what these maps draw.

A citation would not improve either. If the GM wants the first half grounded, the searchable
question is scour and undermining of masonry founded in a watercourse, and that is a different
batch. The WebSearch budget was exhausted before it could be attempted here, so this is recorded as
not searched rather than searched-and-empty.

---

### `cities/hinterland.html` fn-10

**STILL ABSENT.**

No dedicated query was run: the search budget was exhausted before this note was reached, and the
planned query (`irrigation fan handedness left right asymmetric distributary layout`) was refused.
Said plainly so the record is not misread as a completed search.

What is nonetheless known from pages read for other notes: T/JSSLKX 002-2021 §7.4.3 says field
canals are set 「應結合水利設施、耕作田塊、道路及自然界線確定」(English translation by this agent:
"shall be determined in combination with the water-conservancy facilities, the cultivated plots, the
roads and the natural boundaries"), which is consistent with a fan taking whatever hand its pocket
gives it, but does not assert handedness and cannot be cited for it.

The claim remains an unlabeled guess and should be labeled.

---

### `cities/river-cities.html` fn-14

**FOR THE GM.**

The claim - natural tributaries curve to join pointing downstream - is a textbook geomorphology
statement, and the document that states it quantitatively is paywalled.

- **Title:** The occurrence of obtuse junction angles and changes in channel width below tributaries
  along the Mekong River, south-east Asia
- **Journal:** Earth Surface Processes and Landforms (Wiley)
- **DOI:** 10.1002/esp.2165
- **URL tried:** <https://onlinelibrary.wiley.com/doi/abs/10.1002/esp.2165>
- **What blocked it:** not open access. This was not assumed from a 403 - Unpaywall was asked
  (`https://api.unpaywall.org/v2/10.1002/esp.2165?email=unpaywall@impactstory.org`, HTTP 200) and
  answered `"is_oa": false` with `"best_oa_location": null`. No repository copy, preprint or author
  manuscript is registered.
- **What it would settle:** it is the paper that counts junction angles on a real large river -
  the figure quoted in search results is 284 junctions, 66.2% acute - which would turn "tributaries
  curve to join pointing downstream" from a general reading into a measured majority with a named
  exception class (obtuse junctions from meander extension and bedrock deflection).
- **How much it would change:** nothing the map draws. It would let the record state the rule with
  a proportion and an honest exception, instead of asserting it flat.

Also tried, and why they did not serve:

- en.wikipedia "Drainage system (geomorphology)" <https://en.wikipedia.org/wiki/Drainage_system_(geomorphology)>
  - FETCHED and read. It describes dendritic patterns but states junction angles only for the
  RECTANGULAR pattern, and there at right angles: "tributaries join larger streams at right
  angles". Nothing there supports the acute-and-downstream rule; quoting it would misrepresent it.
- en.wikipedia "Confluence" <https://en.wikipedia.org/wiki/Confluence> - FETCHED and read. Junction
  angle appears only in a passage about designing artificial watercourses, not about natural ones.

Engineered drainage returns being cut to point downstream: **nothing read says it.** That half has
no source at all.

---

### `cities/river-cities.html` fn-15

**CITED.**

URL: <https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf> (document B above - read
the TLS and OCR caveats there before quoting)

Passage, verbatim as the PDF's text layer gives it:

> The sediment withdrawal by the offtaking channel is also affected by the alignment of the offtaking channel as pointed out earlier. The alignment of the offtaking canal should be kept such that its center line is at an angle of 60' to 80' to the center line of the main canal in the direction of flow to prevent excess sediment being drawn into the offtaking canal.

Second passage, same page, verbatim:

> Lower layers of water are more easily diverted into the offtaking channel as compared to the upper layers, because the lesser velocities prevail in the lower layers. Moreover, near the bed, the sediment concentration is generally very high.

How it supports the claim: the first passage makes sediment withdrawal a function of the offtake's
alignment and prescribes turning the offtake TOWARD the square (60-80 degrees) specifically to keep
sediment out - which is the record's "the more smoothly it faces the current, the more of the
river's sediment load it drinks", stated from the other end. The second gives the mechanism: the
sediment rides in the slow bottom layer, which is the layer a diversion takes preferentially.

Note for the entry: the `60'` and `80'` are degree signs mangled by the scan.

---

### `cities/river-cities.html` fn-16

**CONTRADICTED, in part.** Two of the four things this footnote asserts are supported by the page;
one is directly denied by it.

URL: <https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf> (document B)

**Denied - "classical headworks therefore kept the offtake itself near square".** Verbatim:

> A canal taking off at 90' to the main flow is the most objectionable orientation of the regulator. The regulator should be so oriented as to produce a suitable curvature of flow lines through the canal regulator; and rl diversion angle of 30' to 45' (with respect to the river flow) is normally recommended to achieve this effect.

What it says instead: for a canal leaving a RIVER, a square offtake is the worst orientation, and
30-45 degrees is the normal recommendation. The record's "near square" is the opposite of the
engineering rule for this case.

**The resolution, and why the record is not simply wrong.** The same document prescribes 60-80
degrees for a distributary leaving a parent CANAL (quoted under fn-15 above). The two prescriptions
are for different junctions: near-aligned off a river, near-square off a canal. Whichever the map
is drawing, the record currently states the canal rule and attributes it to river headworks.

**Supported - the intake on the outer bank of a bend.** Verbatim:

> The bottom layers of the flow around a bend are diverted towards the inside (convex bank) and so the the ideal location of a regulator (to prevent or, at least minimise the entry of bed load into the canal) is the outer bank (concave bank). The regulator is located towards the downstream end of the bend for better effect.

(The doubled "the the" is in the source.)

**Supported - skimming the cleaner upper water.** Verbatim:

> By causing the sediment to further concentrate in the lower layers of the flowing water (that is, near the bed of the main canal upstream of the offtaking point) and allowillg only silt free upper layers of water to enter the distributary channel, sediment entry into the offtaking channel can be minimised.

(`allowillg` is the scan's damage.) The same page adds, verbatim: "The raised inlet sill prevents the
entry of bedload into the canal while the skimmer wall at the inlet prevents the entry of floating
matter into the canal."

**Untested - "controlling the flow with a gate instead."** Gates and regulators are throughout the
document, but no passage read says the gate is what the near-square offtake trades against.

---

### `cities/river-cities.html` fn-17

**STILL ABSENT.**

Query run: `castle moat water supply river sluice maintain water level stagnant not flushed Japanese Chinese` - **REFUSED, search budget exhausted.**

Nothing was read that speaks to a river moat being held full by the river's own stage rather than
flushed through. Pages read for neighboring notes that might have carried it and do not:

- en.wikipedia "Fortifications of Xi'an" - FETCHED. Gives the moat's dimensions and its 1983
  restoration; says nothing about how it was fed or whether it circulated.
- zh.wikipedia 「護城河」 <https://zh.wikipedia.org/zh-hans/護城河> - FETCHED, HTTP 200, read. The
  article is a short general description; no passage on feeding, stage, circulation or stagnation
  survived extraction.

This is the note where the record itself is doing the honest thing already - it states the
stagnation is accepted and names the observable cost. It should keep saying so with the guess
label, because the search for it has now failed twice.

---

### `cities/river-cities.html` fn-18

**STILL ABSENT.**

Same refused query as fn-17; same pages read, same result. Nothing read distinguishes a moat's
demand for water LEVEL from a canal's demand for FLOW.

One page read does support the neighboring physical half, and is worth knowing about even though it
is not this claim: en.wikipedia "Canal" says, verbatim, "Canals need to be level" (quoted in full
under water.html fn-70 below) - a navigation canal's want of a held level, not a moat's. It would be
a misquotation to attach it here.

---

### `fields.html` fn-25

**CITED.** Two halves of this footnote are now carried, by two different documents.

**Chinese canal doctrine** - URL:
<http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.1.1(1),
verbatim:

> 各级渠道应选择在各自控制范围内地势较高地带。干渠、支渠宜沿等高线或分水岭布置，斗渠宜与等高线交叉布置。

English translation by this agent (original above kept as the checker's anchor): "Canals of every
grade shall be sited on the higher ground within their own command area. Main canals and branch
canals should be laid out along the contour lines or the watershed divides; lateral (dou) canals
should be laid out crossing the contour lines."

And §7.4.5, verbatim:

> 田间渠道可布置 2～3 级固定渠道，平原圩区上下级渠道宜相互垂直，丘陵山区结合山坡地形布置。

English translation by this agent: "Field canals may be laid out in 2 to 3 grades of fixed canal;
in plain polder districts successive grades should be mutually perpendicular, and in hill country
they follow the hillslope terrain."

How they support the claim: this is the comb, stated as design law - supply on the high margins,
the next grade down crossing the contours at right angles to it.

**The Minuma / Kishu-school half** - URL: <https://www.jsidre.or.jp/tabata5-a/> (Japanese Society
of Irrigation, Drainage and Rural Engineering, 農業農村工学会), verbatim:

> 建設には将軍吉宗の命をうけた紀州流の井沢弥惣兵衛が当たった。

English translation by this agent: "Construction was undertaken by Isawa Yasobei of the Kishu
school, under orders from Shogun Yoshimune."

and, same page, verbatim:

> もとの溜井（見沼）の縁辺に用水路、中央に排水路を設ける干拓方式もとられた。

English translation by this agent: "A reclamation method was also adopted in which irrigation canals
were placed on the margins of the former reservoir (Minuma) and a drainage channel in the center."

**This settles the "the NAME less so" caveat in the record's own parenthesis**: a learned society
page attaches 紀州流 to Isawa Yasobei AND to Minuma-dai in the same paragraph as a reclamation
LAYOUT - margins for supply, center for drainage - not only as a river-channelization method.

`wiki.mbalib.com`, which blocked the last pass, was not retried: the standard above is better
provenance than a wiki and carries the same doctrine.

---

### `fields.html` fn-35

**STILL ABSENT.**

Queries run: `tameike irrigation pond Japan command area hectares traditional village reservoir statistics`; `ため池 受益面積 平均 ヘクタール 全国 約 万箇所 農林水産省` - **the second was REFUSED, search budget exhausted.**

Candidates and what happened:

- ja.wikipedia 「ため池」 <https://ja.wikipedia.org/wiki/ため池> - FETCHED, HTTP 200, read. It gives
  COUNTS, not command areas: 「2020年時点で全国に約16万か所あり」("as of 2020 there are about
  160,000 nationwide"), Hyogo the most at about 24,000, and an earlier estimate of 十数万から約20万
  ("a hundred and some tens of thousands to about 200,000"). The only area figure is a legal
  threshold, not a typical value: 「灌漑農地面積が0.5ha未満の小規模なため池（特定外ため池）」("small
  ponds with an irrigated-farmland area under 0.5 ha - non-specified ponds"), which are exempt from
  notification. **That threshold is interesting in the other direction**: it implies a large
  population of ponds commanding under half a hectare, which cuts against "typically tens of
  hectares" as a central value.
- The first query returned only individual Tameike dam articles on en.wikipedia (Myoei, Kanezawa,
  Sakura, Shin, Yoshida ...). Not fetched: each is a one-line stub about a single modern dam's
  impounded area, and a handful of stubs is not a range - it would be the same one-case problem the
  record already has with the Kunisaki paper.

Assessment: "tens of hectares, well under 200" remains a GUESS and the record already labels it
one. The ja.wikipedia threshold suggests the true distribution has a long tail BELOW the record's
band, which is worth a sentence.

---

### `fields.html` fn-47

**CITED.** Same passages as fn-25's first half, from document A, T/JSSLKX 002-2021 §9.1.1(1) and
§7.4.5, quoted in full there.

Two further passages from the same standard tighten it, both verbatim:

> 田间渠道应布置在其控制范围内地势较高处，满足自流灌溉要求。

English translation by this agent: "Field canals shall be laid out on the higher ground within their
command area, so as to satisfy the requirement of gravity irrigation." (§7.4.2)

> 灌溉渠系工程设计除满足本标准外，尚应符合 GB 50288、GB/T 50600、GB/T 50363、GB/T 50509、GB 50599、SL18、SL482 的规定。

English translation by this agent: "Beyond satisfying this standard, the design of irrigation canal
systems shall also conform to the provisions of GB 50288, GB/T 50600, GB/T 50363, GB/T 50509, GB
50599, SL18 and SL482." (§9.1.6)

The second is why this document is the right substitute for the 灌溉渠道 references the record could
never reach: it is an openly readable standard that declares itself subordinate to GB 50288.

---

### `fields.html` fn-80

**CITED.** Both halves - the grass and the bund beans - now have passages.

**Grass.** URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC7538448/> (Earthworm species and density
in semi-natural grasslands on rice paddy levees in Japanese satoyama). Verbatim:

> Farmers generally maintain levee grasslands by periodic mowing or herbicide application.

and, verbatim:

> In the studied paddies, farmers managed grasses on the levees by mowing two to five times per year and no herbicide was used.

and, verbatim:

> Various grass species were found on the levees, such as

(the sentence continues into a species list). The paper's own frame is that paddy levees carry
semi-natural GRASSLANDS - it is titled that way - which is the strongest possible form of the
claim that a bund greens over. Mowing two to five times a year is what it takes to keep it down.

**Bund beans.** URL: <https://ja.wikipedia.org/wiki/畦>, verbatim:

> 畦道や人が通れない単なる畦の場合でも、古来から細い狭い面積の土地ではあるが、枝豆などその土地に合った農作物を植え、僅かな収穫でも得ようとしている場合もあり、有効利用されている。

English translation by this agent (original above kept as the checker's anchor): "Whether an azemichi
or a plain aze that people cannot walk on, although it is a narrow strip of land, since ancient
times crops suited to that ground - edamame and the like - have in some cases been planted on it to
win even a small harvest, so it is put to good use."

Corroborating, from a grower's own page - <https://azemameya.com/about/> - verbatim:

> 「あぜ豆」とはその名の通り、畦(あぜ)で育てる豆のことです。

English translation by this agent: "Azemame, as the name says, are beans grown on the aze."

and, verbatim:

> せっかくなので、そこに豆の種を蒔きました。

English translation by this agent: "Since they were at it anyway, they sowed bean seed there." (The
preceding sentences describe farmers plastering mud onto the crumbly paddy bund to firm it.)

Provenance note: azemameya.com is a farm business's own about-page - a practitioner's account, not
scholarship. The ja.wikipedia sentence is the one to lead with.

How they support the claim: the record asserts a bund greens over with grass and bund beans by high
summer. Grass on levees is the subject of a peer-reviewed paper; beans on bunds are attested as a
named practice. **What is still not sourced is the visual consequence** - that the bund "very nearly
disappears into the field". Nothing read says that. The record should keep that half in its own
voice.

---

### `fields.html` fn-82

**STILL ABSENT.**

Query run: `Japanese village rice transplanting communal schedule water rotation banjiku same day labor exchange yui`.

Candidates and what happened:

- en.wikipedia "Yui (behavior)" <https://en.wikipedia.org/wiki/Yui_(behavior)> - FETCHED, HTTP 200,
  read in full. It is a stub. It establishes labor exchange - verbatim: "Yui (Japanese/Okinawan:
  結,ゆい) involves a system of collaborative work in small settlements and autonomous units. It
  consists of mutual aid that helps and cooperates within the residents' village" - and notes the
  concept is "more particular to Okinawan life". **It says nothing about transplanting on one
  schedule, nothing about water being released together, and nothing about growth stages.** Labor
  exchange is only half the claim and the weaker half; the load-bearing half is the shared WATER
  schedule.
- factsanddetails.com "Rice farming in Japan" - NOT FETCHED: a compiled-content site that reprints
  other sources without attribution, which is the exact shape this project's rules exclude (a
  pointer, not a source).
- plenus.co.jp Rice Library, web-japan.org Kids Web Japan - NOT FETCHED: corporate and
  children's-education pages; neither would carry a statement about growth-stage spread across a
  village's basins.

Assessment: the claim has two parts and the searchable one is the water. The query that would settle
it is about 番水 (banmizu, rotational water turns) and 水利慣行 (customary water rights) in a
Japanese irrigation association - that was the intended second query and the budget was gone. Worth
one attempt in a later pass before the claim is left as a guess.

---

### `fields.html` fn-83

**CITED.** This is the closest match in the batch: the record reasons to about a foot of bottom
width from hand-cleaning, and an openly readable standard sets exactly that floor for exactly that
reason.

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.4.3,
verbatim:

> 为便于建后运行管护，渠道底宽应不小于 0.3 m。

English translation by this agent (original above kept as the checker's anchor): "So as to facilitate
operation and maintenance after construction, the canal bottom width shall be not less than 0.3 m."

How it supports the claim: 0.3 m is 11.8 inches - the record's "a bottom a hoe fits into, call it a
foot" - and the standard gives the same reason the record gives, maintenance access, in the clause
itself. It is a floor, stated as a floor, for the same cause.

On the side slopes and the resulting 1.5 ft top: the same standard leaves the side-slope coefficient
to case-by-case stability analysis rather than fixing a number - §11.2.7, verbatim:
「土质排水沟边坡系数应根据开挖深度、沟槽土质及地下水情况等，经稳定分析计算后确定。」(English
translation by this agent: "The side-slope coefficient of an earthen drainage ditch shall be
determined by stability analysis according to the excavation depth, the soil of the trench and the
groundwater conditions.") **So the 1.5 ft top width is still the record's arithmetic**, resting on a
side slope the standard declines to fix. Cite the 0.3 m floor; label the top width a derivation.

Limit to state: a 2021 standard for lined canals in Jiangsu. It is evidence that 0.3 m is the width
below which a channel cannot be maintained by a person, which is a physical fact about hands and
tools and does hold across periods - but it is not a measurement of a premodern ditch.

---

### `fields.html` fn-85

**STILL ABSENT.**

Query run: `paddy field drainage ditch along lowest side bund embankment top of bank layout terrace`.

Candidates and what happened:

- FAO Soil Bulletin, "Terraces for gentle slopes" <https://www.fao.org/4/ad083e/ad083e10.htm> and
  "Diversions and cut-off ditches" <https://www.fao.org/4/ad083e/AD083e11.htm> - NOT FETCHED beyond
  the search stage: both are about hillside conservation terraces on sloping land, a different
  object from the collector at the toe of a flat paddy block, and the search return showed the
  drain "on inner side" of an inward-sloping bench, which is the opposite geometry.
- T/JSSLKX 002-2021 (document A) - FETCHED and read for this. The nearest it comes is §7.4.2,
  verbatim: 「渠（沟）水位按照灌排水位进行设计，确定渠堤顶高程」(English translation by this agent:
  "The canal or ditch water level is designed according to the irrigation and drainage water levels,
  which fixes the bank-top elevation of the canal") and 「宜做到灌排分开，采用灌排相邻布置或相间布置」
  (English translation by this agent: "Irrigation and drainage should be kept separate, using an
  adjacent or an alternating layout"). That establishes that a ditch HAS a designed bank top and
  that supply and drainage are laid out beside one another - it does **not** say the paddy's lowest
  bund IS that bank top, which is the assertion.

Assessment: this is a geometric identity the record reasons out - two things cannot occupy the same
ground - and no page read states it. It should stay labeled. The reasoning is sound enough that
this is a low-value gap.

---

### `fields.html` fn-87

**STILL ABSENT.**

No dedicated query was run; the search budget was exhausted before this note. Said plainly rather
than dressed up.

Nothing read in this batch bears on the paddy share of a near-city plain or on farming households
per hectare of paddy. The record already states that both percentage figures are calibrated against
its own drawn maps rather than derived from a source, which is the honest position; the 70-75%
paddy share and the 1.5-2 households per hectare are the two numbers that would need a source, and
they would come from a village-level cadastral study (Tokugawa 検地帳 analysis, or a Ming-Qing land
survey), not from anything in this batch's reach.

---

### `fields.html` fn-88

**STILL ABSENT.**

No dedicated query was run (budget exhausted). What was read that touches it, from document A:

- §7.4.3, verbatim: 「田间渠道应结合水利设施、耕作田块、道路及自然界线确定」(English translation by
  this agent: "Field canals shall be determined in combination with the water-conservancy
  facilities, the cultivated plots, the roads and the natural boundaries") - canals and plots are
  laid out together, which is consistent with the claim but does not state its direction: it does
  not say the PLOT is surveyed to the CANAL.
- §7.4.5, verbatim: 「平原圩区上下级渠道宜相互垂直」("in plain polder districts successive canal
  grades should be mutually perpendicular") - perpendicularity between canal grades, not between a
  dry plot and the canal it borders.

Assessment: the claim is about survey practice for dry fields specifically, and nothing read
addresses dry fields at all. It should stay labeled as a guess.

---

### `homesteads.html` fn-41

**CITED.** The page the last pass found empty is not empty - it refuses the default fetcher and
serves its body to curl.

URL: <http://www.knowledgebank.irri.org/step-by-step-production/pre-planting/land-preparation/how-to-construct-bunds>

Fetch record: the default fetcher returns a bare Joomla template shell (the last pass's finding,
reproduced). `curl -sL -A "Mozilla/5.0 ... Chrome/120.0 Safari/537.36"` returns HTTP 200 with the
body present. A Wayback capture (<http://web.archive.org/web/2023/http://www.knowledgebank.irri.org/step-by-step-production/pre-planting/land-preparation/how-to-construct-bunds>)
was fetched as a cross-check and carries the identical text.

The page's complete body, verbatim, all four lines of it:

> Construct no wider and taller than 50 cm x 30 cm bunds, around the field.
> Make sure that bunds are well compacted and properly sealed, with no cracks, holes, etc. This will minimize water losses through seepage (particularly in sloping lands).
> Adjust the spillway height to 3−5 cm for storing the same depth of water. Maintain this height to ensure sufficient water storage capacity especially during rainy or wet season.
> For rat control, construct 30 cm x 30 cm bunds.

(The dash in "3−5 cm" is the source's own minus sign; it is reproduced rather than normalized.)

How it supports the claim: "bunds should be constructed no wider and taller than 50 cm x 30 cm" is
on the page, near enough verbatim - the page's own word order is "Construct no wider and taller than
50 cm x 30 cm bunds, around the field."

**One correction the record needs.** The record's footnote continues the quotation as
`... high enough (at least 20 cm) to avoid overflowing`. **That sentence is NOT on this page.** The
page has nothing about 20 cm and nothing about overflowing; its water-depth line is the 3-5 cm
spillway. Either that fragment came from a different IRRI page or it is a misattribution, and it
should be removed from the footnote or re-sourced before the entry lands.

The record's own framing of fn-41 as "a GUESS - no readable page supports it" can now be softened
for the 50 x 30 cm figure, which IS readable. The competing FAO dry-bund section the record cites
against it is unaffected.

---

### `homesteads.html` fn-99

**CITED, for part of the paragraph only.** The half-moon pond has a peer-reviewed study; it carries
about half of what the paragraph asserts and is silent on the rest.

URL: <https://koreascience.kr/article/JAKO201425749459945.page>
Wang, Qiao and Sim, Woo-Kyung, "Basic Studies on Banwoldang(Half-moon shaped Pond) at the
Traditional Chinese Villages", Journal of the Korean Institute of Traditional Landscape
Architecture, 2014.

Abstract, verbatim (reproduced complete; its spellings and its inconsistent "Bamwoldang" are the
source's own):

> This study was carried out to research the locations and comprehensive functions of Chinese unique Banwoldang(half-moon shaped pond) appeared at the traditional Chinese villages. Based on the research, the time of Banwoldang being introduced into Chinese traditional culture could date back to Yuan Dynasty and villages that have Banwoldang mainly distributed in the south of the Yangtze River of China where wealthy and high class have lived. Bamwoldangs were mostly built at the front of the village clan halls for the prosperity of the whole clan, The main reason of Banwoldang construction was to complete Feng Shui functions and its goal from the point of Feng Shui in Chinese ancient villages was replenishing the power of location, including increasing the probability of passing the imperial examination for villagers, multiplying riches, minimizing the fire accident and perfecting the geomantic pattern 'leaning against the hill and facing the water(背山臨水)' of villages. Other functions of Banwoldang were found as the place for the community meeting, fish farming and protection of village from enemy. In this research, the reasons of Banwoldang location and values of its various functions were found. But Banwoldang is disappearing rapidly at the Chinese modern villages because there is no interest in traditional culture. Banwoldang is one of unique elements of Chinese culture that must be preserved, so its meaning and value should be lasted well as the Chinese traditional cultures.

**What it carries:** the pond is dug at the FRONT of the village (before the clan hall); it is
built for feng shui purposes, not religious ones; it completes the 背山臨水 backing-hill-facing-water
pattern; it is fire water ("minimizing the fire accident"); it is fish water ("fish farming"); and
its bank is a gathering place ("the place for the community meeting"). That is five of the
paragraph's assertions, sourced.

**What it does NOT carry, and the record must keep in its own voice:**

- that still water gathers and keeps a lineage's fortune where running water carries it away;
- that the HALF shape is deliberate because a complete thing can only wane - the abstract explains
  the pond's purpose but never explains its shape;
- that the pond is deliberately NOT connected to the irrigation;
- that it is washing water, duck water, or a threshing forecourt.

One divergence worth recording: the paper adds a function the record does not mention -
"protection of village from enemy" - and it writes the geomantic formula 背山臨水 (linshui,
overlooking water) where the record writes 背山面水 (mianshui, facing water). Both formulas are in
use; the source's own characters are reproduced above.

---

### `vegetation.html` fn-83

**CITED, for one leg of the sentence.** The "only forest remnants" claim is sourced from a
peer-reviewed review. The taboo is not.

URL: <https://scholarworks.umf.maine.edu/facscholarship/17/>
Coggins et al., "Fengshui forests and village landscapes in China: Geographic extent,
socioecological significance, and conservation prospects", Urban Forestry & Urban Greening.
The University of Maine at Farmington repository serves the full abstract openly (HTTP 200 to
curl; the publisher copy at ScienceDirect is closed - OpenAlex on doi:10.1016/j.ufug.2017.12.011
returns `"oa_status": "closed"`, so the repository landing page is the readable location).

Passage, verbatim from the abstract (the hyphenation breaks are the PDF abstract's own and are
reproduced):

> Our own field research in 57 villages in five provinces shows that these locally protected woodlands are components of common property regimes (CPRs) that have been better preserved than the other forests in southern China and usually represent the only forest remnants adjacent to villages and other settle- ments.

and, verbatim:

> Fengshui forests, also known as fengshui woods or fengshui woodlands, are culturally preserved remnant groves of natural forest or small plantations that are common in southern China.

How they support the claim: "the most mature forest in the region" and "the dominant southern
Chinese pattern" are both carried - 57 villages across five provinces, southern China, these woods
the only forest remnants next to settlements, and better preserved than the surrounding forest.
"Locally protected woodlands ... components of common property regimes" is the sourced form of what
the record calls protection.

**Not carried: the taboo, and the one-wood-per-village count.** The abstract says "culturally
preserved" and "common property regimes"; it does not say taboo, and it does not say each village
has exactly one such wood rather than several. A search summary returned vivid taboo material
(prohibitions on collecting fallen fengshui timber at Dongshang, seven tree commandments in the
Lingtou clan pedigree, fines of one pig in Jiangsu) - **none of those pages was read, so none of it
is cited**, and it must not enter the record on the strength of a snippet. The likely carrier is
Coggins's ASIANetwork Exchange article "Village Fengshui Forests of Southern China - Culture
History and Conservation Status"; its host <https://www.asianetworkexchange.org/article/id/7755/>
is behind an Anubis anti-bot challenge that returns HTTP 200 with a JavaScript interstitial instead
of the article. That is a bot wall, not a paywall - the journal is open access and a person will
read it in a browser - so it is not raised as a FOR THE GM item; a later pass with a JS-capable
fetch should get it.

---

### `vegetation.html` fn-92

**CITED.**

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §7.4.2,
verbatim:

> 田间渠道应布置在其控制范围内地势较高处，满足自流灌溉要求。根据地形条件，灌排渠系协调布置，宜做到灌排分开，采用灌排相邻布置或相间布置。

English translation by this agent (original above kept as the checker's anchor): "Field canals shall
be laid out on the higher ground within their command area, so as to satisfy the requirement of
gravity irrigation. According to the terrain conditions, the irrigation and drainage canal systems
shall be laid out in coordination; irrigation and drainage should be kept separate, using an
adjacent or an alternating layout."

Corroborating, the same standard devotes a whole chapter (11.2 排水沟设计, Design of drainage
ditches) to the drainage side, and §11.2.1 opens, verbatim:
「排水沟设计流量应根据排水区面积、排水模数、产流与汇流历时等，通过计算分析确定。」(English
translation by this agent: "The design discharge of a drainage ditch shall be determined by
calculation from the area of the drainage district, the drainage modulus, and the runoff and
concentration times.")

How they support the claim: a wet-rice scheme is designed as TWO coordinated canal systems, supply
and drainage, laid adjacent or alternating, with the drainage side carrying its own design
discharge. That is "wet rice needs water in AND water out", stated as design law rather than as
general reading.

**Not carried:** that the drain leaves the LOW CORNER specifically. The standard puts supply on the
high ground and requires the two systems to be coordinated; it does not name a corner. That half is
a reasonable consequence and should be labeled as the record's own.

---

### `water.html` fn-1

**CITED.**

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.4.3,
verbatim:

> 为便于建后运行管护，渠道底宽应不小于 0.3 m。

English translation by this agent (original above kept as the checker's anchor): "So as to
facilitate operation and maintenance after construction, the canal bottom width shall be not less
than 0.3 m."

How it supports the claim: the ladder's bottom rung - a field ditch watering one paddy at ~0.3 m -
now rests on a standard that fixes 0.3 m as the minimum width a canal may be built to, for the
reason that anything narrower cannot be maintained.

**State the shape of the support honestly:** this is a FLOOR, not a measurement of a field ditch.
The standard says no canal shall be narrower than 0.3 m; the record says a field ditch is about
0.3 m. Those agree only because a field ditch is the narrowest thing in the system, which is itself
the record's argument. That is a fair use of it, but the entry should say "the design minimum" and
not "the measured width".

GB 50288 itself was still not obtained - see the FOR THE GM block at the end.

---

### `water.html` fn-2

**STILL ABSENT.**

The assertion - a field ditch is about 1/300 of the 1-cho (~100 m) paddy it feeds - is arithmetic
on fn-1's 0.3 m, not an independent finding, and nothing read states the ratio. Pages read that
could have carried it and do not:

- T/JSSLKX 002-2021 (document A) - FETCHED and read in full for canal dimensions. It fixes the
  0.3 m minimum and the 1.0 m bank top; it never expresses a channel width as a fraction of the
  plot it serves.
- 上海市土地開發整理工程建設技術標準 <https://zjw.sh.gov.cn/shsd/userfiles/255土地开发整理工程建设技术标准.pdf>
  - FETCHED (HTTP 200 to curl, 2.0 MB) and searched for 底宽 / 边坡 / 毛渠. Same: grades, gradients
  and discharges, no width-to-plot ratio.

Assessment: leave it as the record's own arithmetic, stated as such. It needs no source if fn-1 is
cited and the division is shown.

---

### `water.html` fn-25

**CITED.**

URL: <https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf> (document B - read its
TLS and OCR caveats before quoting)

Passage, verbatim as the PDF's text layer gives it, from §10.4 ORIENTATION OF CANAL OFFTAKE:

> A canal taking off at 90' to the main flow is the most objectionable orientation of the regulator. The regulator should be so oriented as to produce a suitable curvature of flow lines through the canal regulator; and rl diversion angle of 30' to 45' (with respect to the river flow) is normally recommended to achieve this effect.

How it supports the claim: the record asserts an acute downstream-pointing offtake with a studied
optimum of 15-45 degrees, "explicitly 30 or 45 instead of 90". This passage is that sentence: 90
degrees named as the most objectionable orientation, 30 to 45 degrees named as the normal
recommendation.

Two things to carry into the entry: the apostrophes are degree signs mangled by the scan, and `rl`
is a scanned `a`; and the recommendation is for a canal leaving a RIVER - the same document
prescribes 60 to 80 degrees for a distributary leaving a parent CANAL (quoted under fn-15), so the
record should say which junction it is drawing.

The record's lower bound of 15 degrees is not in this passage and has no source read here.

---

### `water.html` fn-28

**CITED, with a replacement passage.** The exact string the record quotes could not be found on any
readable page; the doctrine it states is in an openly readable standard, in slightly different
words.

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.1.1(1),
verbatim:

> 各级渠道应选择在各自控制范围内地势较高地带。干渠、支渠宜沿等高线或分水岭布置，斗渠宜与等高线交叉布置。

English translation by this agent (original above kept as the checker's anchor): "Canals of every
grade shall be sited on the higher ground within their own command area. Main canals and branch
canals should be laid out along the contour lines or the watershed divides; lateral (dou) canals
should be laid out crossing the contour lines."

How it supports the claim: the record's point is the placement law - a canal commands only what is
below it, so canals go on the high ground. The standard states exactly that, for every grade.

**The record's quoted string must change.** It currently quotes
「干渠主要布置在灌区较高的地带，以便自流控制较大的灌溉面积」 and attributes it to a page
(wiki.mbalib.com) that no longer answers. The nearest readable wording of that specific sentence is
on a Sina personal blog (<https://blog.sina.com.cn/s/blog_77ef94fb0101333f.html>, FETCHED, HTTP 200,
read), which has 「干渠应布置在灌区的较高地带，尽可能自流控制较大的灌溉面积」 - **a blog, with no
attribution, and not worth citing when a standard says the same thing.** Replace the string with the
standard's, or state the doctrine in the record's own words and footnote the standard.

---

### `water.html` fn-29

**CITED.**

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.1.1(1),
verbatim:

> 各级渠道应选择在各自控制范围内地势较高地带。

English translation by this agent (original above kept as the checker's anchor): "Canals of every
grade shall be sited on the higher ground within their own command area."

How it supports the claim: this is the record's own quoted fragment
「布置在各自控制范围内较高地带」 almost word for word, now on a readable page - each canal on the
high ground of its OWN command area, at every tier of the hierarchy. The record should adopt the
standard's exact wording, which differs by the two characters 选择 and 地势.

A second passage in the same standard repeats it for the field tier, §7.4.2, verbatim:
「田间渠道应布置在其控制范围内地势较高处，满足自流灌溉要求。」(English translation by this agent:
"Field canals shall be laid out on the higher ground within their command area, so as to satisfy the
requirement of gravity irrigation.") - which is the "repeats it at every tier" the record asserts.

---

### `water.html` fn-30

**CITED.**

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.1.1(1),
verbatim:

> 干渠、支渠宜沿等高线或分水岭布置，斗渠宜与等高线交叉布置。

English translation by this agent (original above kept as the checker's anchor): "Main canals and
branch canals should be laid out along the contour lines or the watershed divides; lateral (dou)
canals should be laid out crossing the contour lines."

How it supports the claim: this is precisely "mains and branch canals along contours and ridge
lines, field channels across them" - one sentence, both halves, in a standard.

---

### `water.html` fn-38

**CITED.**

URL: <https://zjw.sh.gov.cn/shsd/userfiles/255%E5%9C%9F%E5%9C%B0%E5%BC%80%E5%8F%91%E6%95%B4%E7%90%86%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE%E6%8A%80%E6%9C%AF%E6%A0%87%E5%87%86.pdf>
- 上海市土地開發整理工程建設技術標準 (Shanghai Municipal technical standard for land development and
consolidation works), served openly by the Shanghai Municipal Housing and Urban-Rural Development
Commission. HTTP 200 to curl, 2.0 MB.

Passage, verbatim as the PDF's text layer gives it (see the caveat below):

> 渠道布置。明渠 输 水 的 灌 溉 渠 道 系 统 包 括 干、支、斗 渠 3 级,田间配水渠 道 为 农、毛 渠 2 级。

Reading (the spacing is an artifact of the PDF's embedded font, not of the document; a person opening
the PDF sees 「渠道布置。明渠输水的灌溉渠道系统包括干、支、斗渠3级，田间配水渠道为农、毛渠2级。」).

English translation by this agent (original above kept as the checker's anchor): "Canal layout. An
open-channel irrigation canal system comprises three grades - main, branch and lateral (gan, zhi,
dou); the in-field distribution channels are two grades, farm and field (nong, mao)."

Second passage, same page, verbatim as the text layer gives it:

> 毛渠的长度和 间 距 根 据 格 田 规 格 布 置,毛 渠 也 可 以 是 农 民 自 行 修 筑。

English translation by this agent: "The length and spacing of the maoqu are laid out according to the
specification of the basin (getian); the maoqu may also be dug by the farmers themselves."

How they support the claim: the record asserts "China names five fixed grades - 干渠 / 支渠 / 斗渠 /
农渠 / 毛渠 (main / branch / lateral / farm / field), the maoqu being the last grade of fixed
channel". The standard names all five in that order and puts the maoqu at the bottom of the ladder,
sized to the individual basin, and adds - usefully, for a map of a hamlet - that the maoqu is the
one the farmer digs.

**Caveat the entry must carry:** this PDF's text layer inserts spaces between characters and a
filler glyph (暋) at clause starts, so a machine reading it and a person reading it see different
strings. Quote it as rendered, and say where the quotation comes from.

Not supported: the Japanese half of the footnote (幹線用水路 → 支線用水路 → 末端用水路 and its
drainage mirror) - the record already marks it unsourced, and nothing read here changes that.

---

### `water.html` fn-48

**STILL ABSENT.**

Query run: `用水路 幹線用水路 幅 5メートル 末端用水路 規模 農業用水路 断面` - **REFUSED, search budget exhausted.**

Candidates fetched anyway, on a direct guess at the article:

- ja.wikipedia 「用水路」 <https://ja.wikipedia.org/wiki/用水路> - FETCHED, HTTP 200, read. It
  describes canal types, history and named examples; the only widths in it are archaeological
  (moat-and-channel finds "幅や深さが各々 1 m" - about 1 m in width and depth each) and a passage
  about widening a shallow warming channel. **No district-main width, and nothing near 5 m.**
- T/JSSLKX 002-2021 (document A) - read for this. It gives design discharges by grade
  (§9.2) and the 1.0 m bank top (§9.3.7), never a water-surface width for a main canal.

Assessment: the record already marks "a district main (yosui) ~5 m" as the sourced rung it was
leaning on; this pass could not confirm it, and the 5 m figure should be treated as unsourced along
with the ~1 m lateral the record already labels that way.

---

### `water.html` fn-49

**CITED.**

URL: <http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf> (document A), §9.3.7,
verbatim:

> 斗渠、农渠岸顶宽度不宜小于 1.0m，渠道岸顶兼作交通道路时，其宽度应满足车辆通行要求。

English translation by this agent (original above kept as the checker's anchor): "The bank-top width
of lateral (dou) and farm (nong) canals should not be less than 1.0 m; where the canal bank top also
serves as a traffic road, its width shall satisfy the requirements for vehicle passage."

How it supports the claim: the record's dry-hem stand-off rests on "a ~1 m embankment top, which is
GB50288's minimum for a lateral/farm canal". This standard sets exactly 1.0 m as the minimum bank
top for exactly the lateral and farm grades - and §9.1.6 of the same document declares that its
canal designs must also conform to GB 50288, which is why the number matches.

**Attribution correction.** The record attributes the figure to GB 50288 directly. GB 50288's own
text was not obtained (see the FOR THE GM block). The entry should either cite T/JSSLKX 002-2021
§9.3.7 for the number - which is readable, and whose own §9.1.6 points at GB 50288 - or say that
the GB 50288 attribution is second-hand. It should not keep quoting a standard nobody has read.

The record's second component, "plus room to stand for the annual dredging", is the record's own
addition; the standard's stated reason for the bank top is vehicle passage where it doubles as a
road, and it gives no reason where it does not.

---

### `water.html` fn-70

**CITED.**

URL: <https://en.wikipedia.org/wiki/Canal>

Passage, verbatim:

> Canals need to be level, and while small irregularities in the lie of the land can be dealt with through cuttings and embankments, for larger deviations other approaches have been adopted. The most common is the pound lock, which consists of a chamber within which the water level can be raised or lowered connecting either two pieces of canal at a different level or the canal with a river or the sea.

How it supports the claim: the record asserts that a cargo canal is cut at the level of the water it
joins, that its gradient is nil, and that a water gate holds it at river level. This passage carries
the first two flat out ("Canals need to be level") and the third in the form of the pound lock -
a gated chamber "connecting ... the canal with a river or the sea", which is exactly the structure
that holds a cut at the level of the water it joins.

Two corroborations worth keeping, both from pages read here:

- the same article dates the double-gated pound lock to 10th-century China, verbatim: "Prior to the
  development of the (double-gated) pound lock in 10th-century China" - so the device is in period
  for this setting, not an anachronism;
- the Japanese Society of Irrigation, Drainage and Rural Engineering page on Minuma-dai
  (<https://www.jsidre.or.jp/tabata5-a/>) names a real Edo example, verbatim:
  「東西縁用水と芝川を結ぶ閘門式運河（通船堀）」(English translation by this agent: "a lock-gate
  canal - the Tsusenbori - connecting the east and west edge canals with the Shiba River").

Limit: en.wikipedia is tertiary. The claim is a physical one about levels and gates, which is why a
general reference serves; if the entry wants better, the Minuma 通船堀 is the period example to
chase.

---

### `water.html` fn-73

**STILL ABSENT** for the maintenance claim.

Query run: `earthen channel bend erosion outside deposition inside sharp corner rounds itself maintenance`.

Candidates and what happened:

- geo.libretexts "Meandering Rivers", ck12.org flexi answers, rangelandsgateway.org - NOT FETCHED.
  All are about natural meanders, which would source the record's FIRST half (a corner scours
  outside and silts inside) but say nothing about a maintenance crew; and the record already
  footnotes that first half separately. Fetching them would have answered a question that was not
  asked here.
- FAO "Irrigation water management", ch. 5 <https://www.fao.org/4/r4082e/r4082e06.htm> - FETCHED and
  read. Its canal-erosion section is about slope and velocity, verbatim: "Soil particles along the
  bottom and banks of an earthen canal are then lifted, carried away by the water flow, and
  deposited downstream where they may block the canal and silt up structures." Nothing about bends
  or corners.
- T/JSSLKX 002-2021 (document A) - FETCHED and read. The nearest passage is an alignment maxim,
  §7.4.1, verbatim: 「平原圩区宜结合格田化布置，丘陵山区宜顺山坡地形，大弯就势，小弯取直。」
  (English translation by this agent: "In plain polder districts the layout should follow the basin
  pattern; in hill country it should follow the hillslope terrain - large bends follow the lie of
  the land, small bends are straightened.") That is a real and useful finding about canal geometry -
  a channel is aligned in sweeps, and only small kinks are taken out - but it is about SETTING OUT a
  channel, not about a crew re-digging a bend after the water has rounded it.

Assessment: the assertion as written is about maintenance behavior and nothing read carries it. The
「大弯就势，小弯取直」 maxim is worth adding to the record on its own merits, under the claim it
does support: a worked channel turns on sweeps by design.

---

### `ways.html` fn-11

**CITED.**

URL: <http://www.chinaknowledge.de/History/Terms/caoyun.html> (document C; the default fetcher fails
on this host's TLS, curl reads it in full)

Passage, verbatim:

> Tribute grain transport ( caoyun 漕運) in imperial times supplied the officialdom and the military garrisons in the capital with staple food, and the grain was also shipped to other destinations, mainly border garrisons. The grain formed part of a local tax levied in the provinces of the lower Yangtze region and was transported along a vast canal system, the Grand Canal or Imperial Canal ( yunhe 運河, da yunhe 大運河).

(The spaces inside the parentheses are the page's own formatting.)

Second passage, from the Ming section, verbatim:

> Each year, about 1 million shi of rice were transported by sea, whereas four times that amount was shipped along the Grand Canal in later periods.

Third passage, same section, verbatim:

> Yet as demand for grain in Beijing increased, sea transport became infeasible and was ultimately fully replaced by canal transport.

Fourth passage, same section, verbatim:

> In 1472, it was decreed that the provinces of Jiangsu, Zhejiang, Anhui, Hunan, Hubei, Jiangxi, Henan and Shandong should produce yearly 4 million shi of rice, to be transported to Tongzhou 通州 (today's Tongxian 通縣), the terminal of the Grand Canal close to the northern capital Beijing.

How they support the claim: the record asserts that in Ming China bulk goods, above all the tribute
rice, moved by canal and river boat, and that the Grand Canal was central to that. All four
passages carry it, and the last two carry the "above all" - four million shi a year by canal, with
sea transport abandoned in favor of it. The fleet's scale is on the same page for anyone who wants
it: 11,700 boats and 127,600 transport troops.

Not carried by this page: the Japanese half of the footnote's paragraph ("Japan's heavy freight
likewise went by water"), which the record already marks unsourced, and the "dense net of
artificial canals" beyond the Grand Canal itself - the article names many feeder canals
(Huitong, Qingjiang, Tonghui, Jizhou, Jiaolai) but does not characterize the net as dense.

---

## FOR THE GM: the one document that would settle four notes at once

**GB 50288-2018, 灌溉與排水工程設計標準 (Design Standard for Irrigation and Drainage Engineering)**

- **Issued by:** Ministry of Housing and Urban-Rural Development of the People's Republic of China
- **Publisher:** China Planning Press, Beijing, 2018 (superseding GB 50288-1999, Code for design of
  irrigation and drainage engineering)
- **Identifier:** GB 50288-2018. National standards carry no DOI, so Unpaywall and OpenAlex have
  nothing to say about them - both were checked and neither indexes it.
- **URLs tried, and what blocked each:**
  - <https://img.antpedia.com/standard/files/pdfs_ora/20200926/GB%2050288-2018.pdf> - HTTP 403 to
    the default fetcher AND to curl with a browser user agent. Genuinely refused, not a bot wall
    this agent could pass.
  - <https://www.antpedia.com/standard/7931413-1.html> - HTTP 200, but a cookie-setting navigation
    shell with no standard text (the previous pass's finding, confirmed).
  - <https://gf.cabr-fire.com/article-61195.htm> - a page that a search result showed carrying
    §6.4 渠道纵横断面设计 (Design of canal longitudinal and cross sections) of GB 50288-2018.
    Connection failed outright, HTTP 000, no response at all. **This is the most promising single
    URL in the batch** - a Chinese building-code mirror that appears to host the section with the
    canal dimensions in it - and it is worth one attempt from a normal browser.
  - <https://www.transcustoms.com/GB_standards/GB_standards_english.asp?code=GB+50288-2018> and
    <https://gbstandards.org/GB_standard_english.asp?code=GB+50288-2018> - commercial translation
    vendors selling an English PDF. Not fetched past the search stage: these sell the document, they
    do not publish it, so no quotable text is behind them without a purchase.
  - <https://www.scribd.com/document/778031816/> - a Scribd upload of the Chinese text. Not
    fetched: Scribd requires an account and is a third-party upload of a copyrighted standard, so a
    citation to it would not be a public readable page in the sense this project means.
- **What it would settle:** four notes rest on it - `water.html` fn-1 (the ~0.3 m field ditch),
  fn-38 (the terminal channel's designed section and its -5 to +10 cm bed setting against the paddy
  surface), fn-48 (the ~5 m district main), and fn-49 (the ~1 m embankment top). Three of those four
  now have a readable substitute in T/JSSLKX 002-2021, which declares itself subordinate to GB 50288
  and carries the same 0.3 m and 1.0 m numbers. **fn-38's bed-setting figure and fn-48's 5 m main
  are the two that nothing readable carries**, and GB 50288 is where they would be.
- **How much it would change:** nothing the maps draw. It would convert three attributions from
  second-hand to first-hand, and would either confirm or retire two numbers currently unsourced.

**Also worth a person's browser, and NOT a paywall:** Coggins et al., "Village Fengshui Forests of
Southern China - Culture History and Conservation Status", ASIANetwork Exchange,
<https://www.asianetworkexchange.org/article/id/7755/>. The journal is open access; the host runs an
Anubis JavaScript anti-bot challenge that serves an interstitial to every automated fetcher. A
browser opens it. It is the likely carrier of the fengshui-forest taboo material that `vegetation.html`
fn-83 needs and that no page read here supplies.

---

## Every search this pass ran

WebSearch queries, in order, exact text:

1. `Grand Canal Ming dynasty tribute rice transport grain boats`
2. `fengshui wood village grove taboo south China mature forest remnant`
3. `half-moon pond banyuetang 半月塘 village feng shui front pond`
4. `azemame 畦豆 soybean planted on paddy levee aze`
5. `tributary junction angle confluence joins downstream acute angle geomorphology`
6. `GB 50288 irrigation and drainage engineering design code English translation`
7. `canal intake outer bank of river bend sediment exclusion headworks traditional`
8. `Horikawa canal Nagoya castle to sea 1610 Fukushima Masanori`
9. `fengshui forest taboo prohibition cutting trees village rules southern China oldest forest`
10. `毛渠 农渠 斗渠 支渠 干渠 灌溉渠道系统 五级 固定渠道`
11. `wet rice paddy requires both irrigation inlet and drainage outlet each field drainage essential`
12. `IRRI Rice Knowledge Bank "how to construct bunds" 50 cm 30 cm land preparation`
13. `karamete-mon rear gate Japanese castle otemon main gate defense`
14. `Chinese city wall moat width meters Ming prefectural city Xi'an Pingyao moat`
15. `tameike irrigation pond Japan command area hectares traditional village reservoir statistics`
16. `Japanese village rice transplanting communal schedule water rotation banjiku same day labor exchange yui`
17. `farm irrigation ditch bottom width side slope hand cleaning minimum earthen channel design`
18. `navigation canal level reach no gradient lock gate holds water at river level barge poled both directions`
19. `earthen channel bend erosion outside deposition inside sharp corner rounds itself maintenance`
20. `護城河 寬度 明代 府城 城牆 米 護城河寬`
21. `船入堀 江戸 運河 掘割 江戸城 堀川 舟入堀`
22. `見沼代用水 東縁 西縁 台地 縁 芝川 排水 享保`
23. `干渠 布置 灌区 较高地带 自流 控制 较大 灌溉面积 渠道规划`
24. `paddy field drainage ditch along lowest side bund embankment top of bank layout terrace`

Eight further queries were composed and **REFUSED by the session's exhausted WebSearch budget**
(200 of 200 used). They are listed so a later pass can run them rather than re-derive them:

25. `畦 あぜ 幅 30センチ 歩く 田んぼ 畦道 幅員` (archetypes fn-91, fn-93)
26. `ため池 受益面積 平均 ヘクタール 全国 約 万箇所 農林水産省` (fields fn-35)
27. `Xi'an city wall moat width 20 meters UNESCO Ming fortification description` (defenses fn-15)
28. `drainage network dendritic tributaries join acute angle pointing downstream textbook geology` (river-cities fn-14)
29. `castle moat water supply river sluice maintain water level stagnant not flushed Japanese Chinese` (river-cities fn-17, fn-18)
30. `"Village Fengshui Forests of Southern China" ASIANetwork Exchange Coggins full text pdf` (vegetation fn-83)
31. `用水路 幹線用水路 幅 5メートル 末端用水路 規模 農業用水路 断面` (water fn-48)
32. `canals built level pounds summit level no current two-way navigation Wikipedia canal` (water fn-70 - resolved anyway by fetching the article directly)

Direct fetches made without a search, by URL guess or by following a search result, with outcome:

| URL | outcome |
|---|---|
| `http://www.chinaknowledge.de/History/Terms/caoyun.html` | default fetcher SSL handshake failure; **curl 200, read in full** |
| `https://en.wikipedia.org/wiki/Hori_River_(Nagoya)` | 200, read |
| `https://centrip-japan.com/spot/743.html` | 200, read |
| `https://koreascience.kr/article/JAKO201425749459945.page` | 200, abstract read complete |
| `https://scholarworks.umf.maine.edu/facscholarship/17/` | 200, abstract read complete |
| `https://www.engr.colostate.edu/.../Hardee%20&%20Du.pdf` | default fetcher 403; **curl 200**, read - sediment exclusion on the concave bank confirmed but in slide-bullet form, superseded by document B |
| `https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf` | default fetcher certificate error; **curl -k 200**, read (see document B caveats) |
| `https://azemameya.com/about/` | 200, read |
| `https://en.wikipedia.org/wiki/Edamame` | 200, read - contains nothing about aze cultivation |
| `https://pmc.ncbi.nlm.nih.gov/articles/PMC7538448/` | 200, read |
| `http://www.cawater-info.net/bk/4-2-1-2-2_e.htm` | 200, read - headworks overview, nothing on bend siting or offtake angle |
| `https://www.canr.msu.edu/resources/Fengshui-forests-...` | 200 but an empty content shell |
| `https://gf.cabr-fire.com/article-61195.htm` | **HTTP 000, connection failed** (GB 50288 §6.4 mirror) |
| `https://img.antpedia.com/standard/files/pdfs_ora/20200926/GB%2050288-2018.pdf` | **403 to curl with a browser user agent as well as to the default fetcher** |
| `https://baike.baidu.com/item/灌溉渠道系统` | 403, Anubis anti-bot challenge |
| `https://www.asianetworkexchange.org/article/id/7755/` | 200 but an Anubis anti-bot interstitial, no article |
| `https://www.southcivil.com/13382.html` | HTTP 000, connection failed |
| `https://zjw.sh.gov.cn/shsd/userfiles/255土地开发整理工程建设技术标准.pdf` | **200, 2.0 MB, read** |
| `http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf` | **200, 622 KB, read** |
| `https://scjgj.beijing.gov.cn/.../P020240806625271323353.pdf` | HTTP 000, connection failed |
| `https://www.jsidre.or.jp/tabata5-a/` | 200, read |
| `https://ja.wikipedia.org/wiki/見沼代用水` | 200, read |
| `https://www.mizu.gr.jp/kikanshi/no57/09.html` | 200, read - Edo canal district, no funairi-bori count |
| `http://www.ymf.or.jp/wp-content/uploads/68-04.pdf` | 200, downloaded (Edo water transport research note); not needed once fn-65 resolved |
| `https://www.japanesewiki.com/building/Karamete-mon%20Gate.html` | 200, read |
| `https://www.britannica.com/technology/canal-waterway/Locks` | **403 to the default fetcher AND to curl**; superseded by en.wikipedia "Canal" |
| `https://www.nrcs.usda.gov/.../Irrigation_Field_Ditch_388_CPS_10_2020.pdf` | fetch timed out at 60 s; superseded by document A |
| `https://www.nzdl.org/cgi-bin/library?...` | 403 |
| `https://www.fao.org/4/r4082e/r4082e06.htm` | 200, read |
| `http://www.knowledgebank.irri.org/.../how-to-construct-bunds` | default fetcher returns an empty template; **curl 200, body present** |
| `http://web.archive.org/web/2023/...how-to-construct-bunds` | 200, identical text, used as cross-check |
| `https://en.wikipedia.org/wiki/Canal` | 200, read |
| `https://en.wikipedia.org/wiki/Drainage_system_(geomorphology)` | 200, read |
| `https://en.wikipedia.org/wiki/Confluence` | 200, read |
| `https://en.wikipedia.org/wiki/Fortifications_of_Xi%27an` | 200, read |
| `https://en.wikipedia.org/wiki/Paddy_field` | 200, read |
| `https://en.wikipedia.org/wiki/Yui_(behavior)` | 200, read |
| `https://ja.wikipedia.org/wiki/畦` | 200, read |
| `https://ja.wikipedia.org/wiki/ため池` | 200, read |
| `https://ja.wikipedia.org/wiki/用水路` | 200, read |
| `https://zh.wikipedia.org/zh-hans/護城河` | 200, read |
| `https://www.mdpi.com/1999-4907/11/11/1286` | 403 to curl with a browser user agent |
| `https://blog.sina.com.cn/s/blog_77ef94fb0101333f.html` | 200, read - blog, not cited |
| `https://api.unpaywall.org/v2/10.1002/esp.2165` | 200, answered `is_oa: false` |
| `https://api.openalex.org/works/doi:10.1016/j.ufug.2017.12.011` | 200, answered `oa_status: closed` |
