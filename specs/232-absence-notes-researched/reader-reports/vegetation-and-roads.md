# Reader report: batch `vegetation-roads-and-the-rest` (14 notes)

Read 2026-09-12. Verification only - this report does not edit the record.

**A note on the batch assignment.** The dispatch pointed at two notes resting on US
bridge-engineering manuals (an NRCS technical supplement on abutment design, and state bridge
manuals). No note in this batch is about bridge landings or abutments; the `ways.html` note here is
about road WIDTH. Those two notes are in a different batch, and nothing was spent on them.

**Method.** Every verdict below rests on a page actually fetched and read in this pass. Where the
default fetcher was refused I retried with `curl` under a browser user agent, and for journal
articles I asked Unpaywall and OpenAlex whether an open copy exists. Two hosts (Wiley, DOAJ, SAGE)
sit behind a Cloudflare interstitial that refuses every automated client; those are reported as FOR
THE GM with the three routes named.

**One budget limit, stated plainly:** this session's WebSearch allowance (200 calls) ran out before
a dedicated search pass could be run for `cities/hinterland.html` fn-11. That note is reported as
STILL ABSENT with no searches of its own, which is a gap in this report rather than a finding about
the record.

## Verdicts at a glance

| # | Page and footnote | Verdict |
|---|---|---|
| 1 | `buildings.html` fn-47 | **CITED** (partial - the "away from the wells" clause is not supported) |
| 2 | `cities/government.html` fn-35 | **STILL ABSENT** |
| 3 | `cities/hinterland.html` fn-11 | **STILL ABSENT** (no search budget remained) |
| 4 | `fields.html` fn-81 | **CITED** (partial - spacing yes, "two to six seedlings" no) |
| 5 | `fields.html` fn-89 | **CONTRADICTED** |
| 6 | `homesteads.html` fn-32 | **FOR THE GM** (gold OA, Cloudflare-blocked) |
| 7 | `homesteads.html` fn-97 | **CITED** (weak - two figures, one house type) |
| 8 | `religion-and-death.html` fn-11 | **CITED** (on the very page the last pass called silent) |
| 9 | `urban-features.html` fn-64 | **CITED** (mounds) + **FOR THE GM** (the linear-borders article) |
| 10 | `urban-features.html` fn-75 | **CITED** |
| 11 | `urban-features.html` fn-85 | **STILL ABSENT** (one near miss, named) |
| 12 | `vegetation.html` fn-88 | **CITED**, with a correction: the attested remedy is not the one the record states |
| 13 | `vegetation.html` fn-90 | **CITED** (partial - the "thousand years" figure is still unsourced) |
| 14 | `ways.html` fn-7 | **CITED** (partial), with a correction to which number is which |

---

### `buildings.html` fn-47

**CITED** (partial)

**URL:** <http://paper.people.com.cn/rmzk/html/2017-07/16/content_1798546.htm> (People's Daily,
*Renmin Zhoukan*, "紫禁城的消防史", 2017-07-16)

Passage verbatim (Chinese):

> 在紫禁城中，几乎所有建筑旁都有大小不同的铁缸、铜缸，其中太和殿、保和殿和乾清门前还有18口鎏金铜缸。整个紫禁城内共有缸308口，这些大大小小的缸称为“门海”或“吉祥缸”，每尊大缸可贮水接近3000升，如同一座座小水库。这些大缸，由十几个太监专门负责管理，每天派杂役从井内取水把缸打满，还要保证水质干净，没有异味。

English translation (mine, from the Chinese):

> In the Forbidden City, beside almost every building there are iron vats and bronze vats of
> differing sizes, and in front of the Hall of Supreme Harmony, the Hall of Preserving Harmony and
> the Gate of Heavenly Purity there are a further 18 gilt-bronze vats. Within the whole Forbidden
> City there are 308 vats in all; these vats large and small are called "men hai" or "jixiang gang",
> and each large vat can store close to 3,000 liters of water, like so many small reservoirs. These
> large vats were managed by a dozen or so eunuchs specially charged with them, who each day sent
> menial workers to draw water from the wells and fill the vats, and had also to keep the water
> clean and free of any odor.

Second URL, for the grading by rank: <https://www.thepaper.cn/newsDetail_forward_4257673>

> 据《大清会典》记载，宫中共有大缸308口。但随着岁月的消逝，如今只剩下了231口。

> 鎏金铜缸等级最高，陈设在太和殿、保和殿和乾清门两边的即是这种鎏金大铜缸，共有18口

> 在后宫的各个院落安放的是一般的铜缸或铁缸。

English translation (mine): "According to the *Da Qing Huidian*, there were 308 large vats in the
palace in all. With the passing of the years only 231 remain today." / "The gilt-bronze vats are of
the highest grade; those set out on either side of the Hall of Supreme Harmony, the Hall of
Preserving Harmony and the Gate of Heavenly Purity are of this gilt-bronze kind, 18 in all." / "In
the various courtyards of the rear palaces, ordinary bronze or iron vats were placed."

**How it supports the claim.** It carries four of the footnote's assertions directly: the figure 308;
distribution per building rather than in one cluster ("beside almost every building"); the name
men hai 门海, which the record currently marks "unsourced"; and the grading by importance (gilt
bronze at the three highest-ranked halls and gates, ordinary bronze or iron in the rear courtyards).

**What it does NOT support, and a tension.** The clause "deliberately placed to fill coverage gaps
away from the wells" is carried by neither page. The People's Daily passage in fact says the vats
were filled daily with water drawn FROM the wells, which does not contradict siting them away from
wells but gives no support for it either. A search summary asserting the "far from water sources"
placement was seen and deliberately not used, per the read-what-you-cite rule. That clause should
stay an absence note or be dropped.

---

### `cities/government.html` fn-35

**STILL ABSENT**

**Searches run (exact query text):**

1. `Chinese county seat yamen located center walled city main streets crossing morphology`

**Candidates returned, and what became of each:**

- *Yamen* - Wikipedia (en), <https://en.wikipedia.org/wiki/Yamen> - **FETCHED and read** (curl,
  HTTP 200). The article is about yamen runners, their pay and their corruption. It carries nothing
  about where a yamen stood in its city, no mention of the main streets crossing, and no mention of
  bureau offices lining avenues.
- *Walled Cities in Late Imperial China*, Ioannides and Zhang,
  <https://wordpress.clarku.edu/wp-content/uploads/sites/423/2016/03/WalledCitiesJUEFinal.pdf> -
  **FETCHED and read** (curl, HTTP 200, 111 kB of text). It is an economics paper on wall
  circumference and city size using Skinner's ChinaW dataset. "Yamen" appears only as the unit of
  observation in that dataset ("every administrative yamen at the prefectural and county levels").
  Nothing on siting within the walls.
- *Yamen* - **Grokipedia**, <https://grokipedia.com/page/Yamen> - **NOT fetched, deliberately.** This
  is the one candidate whose search snippet carried the record's exact claim ("sited at the center of
  the city at the point where the main east-west street crossed the main north-south street").
  Grokipedia is an AI-generated encyclopedia and is forbidden as a source by the project's own rule.
  **This is worth flagging**: the phrasing now in the record is very close to that snippet, so if
  the claim entered from a search summary, its apparent corroboration is a forbidden source rather
  than a finding.
- *Ancient Chinese urban planning* - Wikipedia, *Pingyao* - Wikipedia, *Yexian Yamen* - Baidu Baike,
  *Urban morphology and conservation in China* - ScienceDirect: judged not worth the one fetch each
  after the two above came back empty - the first three are general or place-specific articles with
  no siting rule, and the ScienceDirect page is an abstract behind a paywall.

The honest state: the claim may well be true (it is a commonplace of Chinese city-planning
literature, and the likely real sources are Sen-dou Chang's work on walled capitals or Skinner's
*The City in Late Imperial China*), but no page a reader can open was found carrying it, and the one
page that did is disqualified.

---

### `cities/hinterland.html` fn-11

**STILL ABSENT**

**Searches run:** none of its own. The session's WebSearch allowance (200 of 200) was exhausted on
the preceding notes, and the one query drafted for this note -
`vegetable garden bed width traditional hand cultivation raised bed size reach arm premodern China Japan` -
was refused by the budget and never executed.

No candidates were therefore returned and none was fetched. The 55 ft guess stands exactly where it
stood; this report adds nothing to it and should not be read as confirming that the record is silent.
This note needs a fresh reader with search budget.

---

### `fields.html` fn-81

**CITED** (partial)

**URL:** <http://www.knowledgebank.irri.org/training/fact-sheets/crop-establishment/manual-transplanting>
(International Rice Research Institute, Rice Knowledge Bank, "Manual transplanting". Refused the
default fetcher with ECONNREFUSED; read via curl under a browser user agent, HTTP 200.)

Passage verbatim:

> Transplant 2 – 3 seedlings per hill at shallow depth at optimum spacing (20 cm x 20 cm or 22.5 cm
> x 22.5 cm).

And, on the practice being the ordinary Asian one rather than a modern innovation:

> Transplanting is the most common and elaborative method of crop establishment for rice in Asia.

> Manual transplanting does not require costly machines and is most suited for labor-surplus areas
> and for small rice fields.

**How it supports the claim.** It establishes the HILL as the unit (seedlings set in clumps, not
singly), and it puts the centers at 20 to 22.5 cm, which sits inside the footnote's "roughly 20-30
cm". The arithmetic the footnote draws from it - about one hill per square foot - follows: 20 cm is
7.9 in, so a hill occupies about 0.43 sq ft, and 22.5 cm about 0.55 sq ft.

**What it does NOT support.** The footnote says "clumps of two to six seedlings". IRRI says two to
three. Nothing read in this pass carried the upper end. A dedicated search for it -
`traditional rice transplanting "seedlings per hill" farmers 4 to 6 Japan hand transplanting practice` -
returned only the same IRRI fact sheet, a Yanmar corporate page on *mitsunae*, two Oregon State
extension pieces on the invention of the rice transplanter, and Web Japan children's pages; the
search's own summary stated it did not find the 4-to-6 range. So "two to six" should be narrowed to
"two to three" on this source, or the wider band kept as an explicit guess.

**One limit to state if this is used.** IRRI's figure is a modern agronomic RECOMMENDATION, not a
measurement of premodern practice. It is evidence that hills at roughly this spacing are the normal
form of hand transplanting in Asia; it is not evidence of what an Edo-period or Ming-period field
measured.

---

### `fields.html` fn-89

**CONTRADICTED**

**URL:** <https://www.fao.org/4/t1696e/t1696e02.htm> (FAO, "Rainfall runoff management techniques for
erosion control and soil moisture conservation", P.O. Aina, Department of Soil Science, Obafemi
Awolowo University)

Passage verbatim:

> Ridge and Mound Tillage The ridge-furrow system is a commonly used physical conservation practice.
> Ridge-and-furrow systems when aligned parallel to the contour lines have the dual purpose of
> erosion control and surface drainage. Their advantages are greater, the less steep the terrain and
> the more permeable the soil.

And:

> Generally, for small landholders with only hand implements or animal traction and low-value
> subsistence crops, the ridge-furrow system used along the contour is a satisfactory method of
> enhancing infiltration and reducing runoff.

> Tying ridges or mounds to permit more rainwater to infiltrate is an effective system in drier areas
> (< 1000 mm annual rainfall) on gentle slopes (< 7%) but not in wet years or more humid areas.

**What the source says instead.** The footnote asserts that the reasoning behind contour ridging
"belongs to a STEEP slope: it is an erosion measure, not a general rule, and on a gentle valley
margin it is not forced". The FAO chapter says the opposite of the first half: contour ridging's
advantages are GREATER the LESS steep the ground, and the contour ridge-furrow system is named as
the satisfactory general method precisely for small hand-and-animal holdings. What the chapter
assigns to steep ground is a different family of measures - terraces, contour bunds, contour hedges,
straw barriers and grass buffer strips ("often suggested for use on steep cultivated lands"), with
contour bunds and terraces called "of secondary importance in runoff management for small-scale
farmers".

**What survives, and what does not.** The footnote's first clause is supported verbatim: ridging
along the contour IS an erosion-control measure ("the dual purpose of erosion control and surface
drainage"). The clause that fails is the inference - that this therefore belongs to steep ground and
is "not forced" on a gentle valley margin. On this source a gentle margin is where contour ridging
works BEST.

**What this does and does not cost the map.** The map's decision - letting neighboring dry plots run
their furrows different ways so family strips read as distinct - is a legibility and variety
decision, and nothing here forbids it: the source says contour alignment is advantageous, not that it
was universal, and it addresses conservation performance rather than what Chinese or Japanese
farmers actually did. But the REASON currently written into the record is wrong as stated and should
be rewritten. The honest form is that contour alignment is one supportable option whose benefit is
real on gentle ground too, and that varying the direction is a drawing choice made for legibility,
not a correction of a misapplied erosion rule.

---

### `homesteads.html` fn-32

**FOR THE GM**

**The document:** Ushijima, M. et al., "Spatial composition and premise arrangement of traditional
Manchu village in Northeast China", *Japan Architectural Review*, 2020 (Architectural Institute of
Japan / Wiley). DOI **10.1002/2475-8876.12146**.

**It is open access by license.** Unpaywall reports `is_oa: True`, gold, with the publisher location
<https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/2475-8876.12146> under **CC-BY-NC-ND**.
Semantic Scholar agrees (`openAccessPdf`, status GOLD, license CCBYNCND). DOAJ lists it under CC-BY-SA
at <https://doaj.org/article/74fb75a47d834c68b3a8b196d8c2a4aa>. So a person opening it in a browser
should get the full text.

**All three recovery routes were tried, and what blocked each:**

1. **curl with a browser user agent** on <https://onlinelibrary.wiley.com/doi/full/10.1002/2475-8876.12146>
   - HTTP **403**, body is a Cloudflare interstitial ("Just a moment... Enable JavaScript and cookies
   to continue"). Same on the `pdfdirect` URL with a Referer header: HTTP **403**, 5,844 bytes of
   Cloudflare challenge, `content_type: text/html`. This is a JavaScript challenge, not a paywall.
2. **Open-access-by-license check** - done, and it is open access (above). The license is not the
   obstacle; the bot challenge is.
3. **Repository copy** - DOAJ returns the same Cloudflare challenge (HTTP 403). Semantic Scholar's
   only location is the Wiley URL. OpenAlex lists no second location. No author manuscript,
   preprint, university repository or government mirror surfaced.

**What it would settle.** The footnote's final clause - "Rear-access ground behind the housing lots
is separately documented in traditional Manchu villages in northeast China, so this is not a purely
European shape." This is the load-bearing half of the note: the back-lane form is otherwise
documented only from European planned-village literature, and this article is what makes the shape
East Asian rather than an import. The search summary describes the paper analyzing Shengli Village
lot orientation and gate placement ("More than two-thirds of the housing lots face south. Gates on
the south side of the street have gates located in the north"), which is exactly the kind of
premise-arrangement material that would confirm or refute rear access - but that is a summary, and
it is not being treated as evidence.

**How much it would change.** If the GM can open it and it documents rear-access ground, the note
loses its absence marker and the back-lane form gains its one non-European attestation. If it does
not, the sentence should be cut back to the European evidence and labeled as such.

---

### `homesteads.html` fn-97

**CITED** (weak - the limits matter more than usual)

**URL:** <https://habitatio.epitesz.bme.hu/en/portfolio/gassho-type-minka/> (Budapest University of
Technology and Economics, Faculty of Architecture, "Gassho type Minka")

Passage verbatim:

> The floor area of the house can range from 3.5×7 ken to 7×12 ken.

And, for the bay-by-bay growth the footnote describes:

> The posts of the framework are typically set one ken apart (this is a traditional Japanese unit of
> measurement, 1 ken = 1.82 m) and the beams span 5-7 metres.

**How it supports the claim.** The two stated plan sizes give length-to-depth ratios of 7/3.5 = **2.0**
and 12/7 = **1.71**. Both sit inside the footnote's band of "about 1.3 to 2.5 long to deep", and both
sit well below the "past about 2.7 to 1 the house is drawn wrong" bar. The posts-one-ken-apart
sentence supports the footnote's mechanism - that a minka is a bay-count on a module, so it grows in
whole bays along the ridge.

**Limits, which should be stated wherever this is used.**

- It describes the **gassho-zukuri** type specifically (the steep-roofed Shirakawa-go silk-rearing
  farmhouse), which is one regional type and an unusually large one, not minka in general.
- It is a **university course portfolio page**, not a survey of measured plans. Two size figures are
  not a distribution, and nothing on the page says these are the extremes of a measured sample.
- It therefore supports the band as **plausible and not contradicted**; it does not establish 1.3 and
  2.5 as the edges. If the record wants the band as a finding rather than a calibration, a measured
  survey of minka plans is still owed.

---

### `religion-and-death.html` fn-11

**CITED** - and note that this is the page the previous pass recorded as carrying nothing.

**URL:** <http://www.chinaknowledge.de/History/Tang/tang-econ.html> (Ulrich Theobald,
ChinaKnowledge.de, "Tang-Period Economy")

Passage verbatim:

> Many manors were owned by members of the imperial family, and by high officials, but also by
> monasteries. Manors did not only produce grain or lettuce but also every kind of fruits or animals,
> and mulberry trees and tea bushes could be found there, as well as oil mills, spinneries and
> breweries. The employees at these large estates ( zhuangke 莊客, zhuanghu 莊戶, or kehu 客戶) were
> slaves, craftsmen, and tenant farmers.

Supporting passages on the same page:

> Among the large estate owners were many Buddhist monasteries, a fact that caused the state guided
> persecutions of Buddhism .

> Many great clans, the imperial family and the monasteries owned large land estates ( zhuangyuan
> 莊園) that could not be taxed directly by the state.

**How it supports the claim.** The footnote asserts that monastic "land and dependent labor funded
mills, oil presses and other enterprises". The first passage gives all three elements in one
sentence: the manors were owned by monasteries among others; they carried oil mills, spinneries and
breweries; and the labor on them was slaves, craftsmen and tenant farmers - dependent labor by any
reading. The tax-exemption passages support the surrounding sentence about monastic tax exemption
being the thing lay investors wanted a share of.

**Correcting the previous pass.** The last pass recorded this URL as "200, page is reachable and
discusses Tang monasteries/land estates in general terms, but carries no sentence matching the
footnote's assertion". That verdict was wrong: the sentence is on the page, in the paragraph on
manors rather than the paragraph on monasteries, which is presumably why a search for "monastery"
plus "mill" in one place missed it. The absence note on this footnote can be retired.

**One limit.** ChinaKnowledge.de is a single-author reference site (Theobald is a sinologist), so it
is a serious reference rather than primary or peer-reviewed scholarship. The underlying authority for
this material is Gernet's *Buddhism in Chinese Society: An Economic History from the Fifth to the
Tenth Centuries* and Twitchett's "The Monasteries and China's Economy in Medieval Times"; neither
was readable in this pass.

---

### `urban-features.html` fn-64

**CITED** for the border mounds; **FOR THE GM** for the linear-borders assertion.

#### The Nanbu-Date border mounds - CITED

**URL:** <http://www.bunka.pref.iwate.jp/archive/hist114> (Iwate Prefecture, *Iwate no Bunka Joho
Daijiten*, "南部領伊達領境塚")

Passage verbatim (Japanese):

> 寛永19年（1642）、徳川幕府の裁定により、南部・伊達の両領境界が決定されたことを受け、奥羽山脈駒ヶ岳（おううさんみゃくこまがたけ）山頂から太平洋唐丹湾（とうにわん）に到るおよそ130kmに及ぶ境界線上に築かれた境塚。 塚は、大塚（おおづか）と小塚（こづか）があり、寛永19年に大塚が築かれたのち、元禄（1688〜）までに大塚の間に小塚が築かれたようである。 他に、特に重要な地域では相対する挾塚（はさみづか）も築かれている。 境塚そのものは各地にみられるが、全国に類を見ない大規模な境界施設であり、徳川幕府草創期からの東北地方の政治的緊張状況を示す貴重な遺跡である。

English translation (mine, from the Japanese):

> Boundary mounds built along the boundary line running approximately 130 km from the summit of Mount
> Komagatake in the Ou mountain range to Toni Bay on the Pacific, following the determination of the
> boundary between the Nanbu and Date domains by adjudication of the Tokugawa shogunate in Kan'ei 19
> (1642). The mounds comprise large mounds (ozuka) and small mounds (kozuka); after the large mounds
> were built in Kan'ei 19, small mounds appear to have been built between the large ones by the
> Genroku era (1688-). In addition, in particularly important districts, facing mounds (hasamizuka)
> were also built. Boundary mounds themselves are seen in many places, but this is a boundary
> installation of a scale unparalleled in the country, and a valuable site showing the politically
> tense situation of the Tohoku region from the founding period of the Tokugawa shogunate.

**How it supports the claim.** It carries the worked example exactly as the footnote states it: a
series of earth mounds, the ~130 km length, the Nanbu (Morioka) and Date (Sendai) parties, and the
shogunate's 1642 action. One correction of nuance: the record says "re-confirmed by the shogunate in
1642", while the source says the boundary was DETERMINED by shogunal adjudication (裁定) in 1642 and
the mounds built in consequence. The sentence "such markers were common under the Tokugawa" is
supported in the weaker form the source gives - "boundary mounds themselves are seen in many places"
- while the source simultaneously calls this particular installation unparalleled in scale.

#### The linear-borders assertion - FOR THE GM

**The document:** Koyama, Naomu, "The Eastern cousins of European sovereign states? The development
of linear borders in early modern Japan", *European Journal of International Relations*, 2022. DOI
**10.1177/13540661221133206**.

**It is open access by license.** Unpaywall reports `is_oa: True`, publisher location
<https://doi.org/10.1177/13540661221133206>, license **CC-BY**. OpenAlex confirms `is_oa: True` and
lists no alternative location or PDF.

**Routes tried:**

1. **curl with a browser user agent** on <https://journals.sagepub.com/doi/full/10.1177/13540661221133206>
   - HTTP **403**, 5,811 bytes, Cloudflare interstitial ("Just a moment... Enable JavaScript and
   cookies to continue"). A JavaScript challenge, not a paywall.
2. **Open-access-by-license check** - done; it is CC-BY. The license is not the obstacle.
3. **Repository copy** - OpenAlex lists only the publisher location. The previous pass already checked
   the author's personal site (sites.google.com/site/naomukoyama) and found no PDF; nothing new
   surfaced.

**What it would settle.** The footnote's opening assertion - that early modern Japanese domains were
building a territorial order with agreed boundaries and mutual exclusion, evidenced by boundary
disputes, boundary markers and map-making. This is the general claim that makes the Nanbu-Date mounds
an instance of a pattern rather than a curiosity, and it is what licenses drawing a linear clan
border at all. Given the article is CC-BY, a browser should render it in full.

**Also still absent on this footnote:** the kuniezu clause. The record already discloses its own
problem there ("unsourced: the page lists mountains, rivers, roads, landmarks, village names, rice
yields and castle towns, not boundaries"), and nothing in this pass changed it. The claim that
kuniezu carried the boundaries drawn on them remains unsupported by any page read.

---

### `urban-features.html` fn-75

**CITED**

**URL:** <https://kotobank.jp/word/%E9%AB%98%E6%9C%AD%E5%A0%B4-495282> (Kotobank, quoting
*Sekai Daihyakka Jiten* / Heibonsha World Encyclopedia, old edition, s.v. 高札)

Passage verbatim (Japanese):

> 高札は通常，人々の目をひきやすい市街の中心の辻や出入口，橋詰めなどに掲げられ，〈札の辻〉の地名は今日も各地に残っている。江戸では日本橋南詰，常盤橋外，浅草橋内，筋違橋（すじかいばし）内，高輪（たかなわ）大木戸，半蔵門外の6ヵ所が大高札場とされ，さらに35ヵ所の高札場があった。

English translation (mine, from the Japanese):

> Kosatsu were usually posted at the crossroads at the center of the town, at entrances and exits, at
> bridge-ends and so on - places that readily catch the eye - and the place name "Fuda no tsuji"
> (notice-board crossroads) survives in many places to this day. In Edo, six places were designated
> great notice-board grounds - the south end of Nihonbashi, outside Tokiwabashi, inside Asakusabashi,
> inside Sujikaibashi, the Takanawa Okido, and outside Hanzomon - and there were a further 35
> notice-board grounds.

**Second URL** for the fuller list including barriers, ports and village entrances:
<https://ja.wikipedia.org/wiki/%E9%AB%98%E6%9C%AD> (Wikipedia (ja), 高札)

> 幕府は人々の往来の盛んな地点や関所や港、大きな橋の袂、更には町や村の入り口や中心部などの目立つ場所に高札場（制札場）と呼ばれる設置場所を設けて、諸藩に対してもこれに倣うように厳しく命じた。

English translation (mine, from the Japanese):

> The shogunate established sites called kosatsuba (seisatsuba) at conspicuous places - points where
> the coming and going of inhabitants was heavy, barriers and ports, the foot of large bridges, and
> further the entrances and central parts of towns and villages - and strictly ordered the domains to
> follow this example as well.

And, on the post stations:

> なお高札場は宿場にも多く設置されたが、各宿村間の里程測定の拠点ともされたため、領主の許可なく移転することはできなかった。

English translation (mine): "Notice-board grounds were also set up in large numbers at post
stations; because they were also used as the reference points for measuring road distances between
post villages, they could not be moved without the lord's permission."

**How it supports the claim.** The footnote's central assertion - that the bakufu set kosatsuba at
points of heavy passage, at barriers and ports, at the foot of large bridges, and at the entrances
and centers of towns and villages - is the Wikipedia sentence almost item for item. The
Heibonsha encyclopedia entry independently gives the same siting logic in the form that matters most
to the map: the crossroads, the entrance, the bridge-end, all of them ON the way. The distance-datum
sentence is a bonus that strengthens the footnote's conclusion: a board that serves as the survey
reference between post villages is necessarily fixed to the road itself, not to a plot of ground
beside it.

**Source ranking note.** The Kotobank entry reproduces the Heibonsha *Sekai Daihyakka Jiten*, a
publisher-edited encyclopedia, which outranks the Wikipedia article; both are given because the
Wikipedia sentence is the one that enumerates barriers, ports and village entrances together. The
footnote's "6 ft from tread edge to board edge" decision is a map calibration and is correctly
marked as not a finding - nothing read gives a standoff distance.

---

### `urban-features.html` fn-85

**STILL ABSENT**

**Searches run (exact query text):**

1. `eta outcast hamlet Tokugawa village located edge periphery riverbank separate settlement burakumin geography`
2. `被差別部落 立地 村はずれ 川沿い 集落 近世 位置 研究`

**Candidates returned, and what became of each:**

From search 1:

- *Japan's outcasts* - delanceyplace.com - not fetched: a book-extract mailing-list page, a
  third-hand excerpt with no locational claim in the snippet, below the bar for a siting rule.
- *Burakumin Definition, History & End* - Study.com - not fetched: a commercial homework site,
  tertiary, not a usable source under the project's rules.
- *"Not Even Human": The Birth of the Outcaste in Tokugawa Japan*, Hohonu (University of Hawaii at
  Hilo undergraduate journal), <https://hilo.hawaii.edu/campuscenter/hohonu/volumes/documents/NotEvenHumanTheBirthoftheOutcasteinTokugawaJapan.pdf>
  - not fetched: an undergraduate journal paper; it was the best of a weak list but the search budget
  ended before it could be read. **This is the one candidate a follow-up pass should fetch first.**
- Daruma Museum blog, two Tokiotours blog posts, thesevenworlds blog - not fetched: personal blogs.
- *Burakumin* - **Grokipedia** - not fetched, deliberately: forbidden source class.

The search's own summary stated plainly that its results did not contain the riverbank or
village-edge siting.

From search 2:

- 小早川明良, "他者の他者の創出 - 不安定化する地域と少数点在型の被差別部落の分析", J-Stage,
  <https://www.jstage.jst.go.jp/article/istd/6/0/6_05/_pdf/-char/ja> - **FETCHED and read** (curl,
  HTTP 200, 73 kB PDF, full text extracted). It is a modern sociological study of one seven-household
  buraku near Fukuyama and its neighborhood association. It contains no instance of 村はずれ, 村外れ,
  河原 or 川原. **One near miss**, quoted here because it is the closest thing found:

  > A部落は、「傾斜地に住む」という、被差別部落に特有の立地条件にあった［内閣同和対策審議会1965：10］。

  English translation (mine): "Hamlet A was subject to the siting condition characteristic of
  discriminated buraku, namely 'living on sloping ground' [Cabinet Dowa Policy Deliberation Council
  1965: 10]."

  This attests that a **characteristic marginal-land siting** is a documented thing, and it names the
  document that actually asserts it - the 1965 Cabinet Dowa Policy Deliberation Council report
  (内閣同和対策審議会答申), p. 10. But "sloping ground unfit for cultivation" is not "the village edge
  or across its stream", and a 1965 government report on modern conditions is not evidence about the
  Tokugawa village. It does not support the footnote as written.

- 斎藤洋一, "江戸時代の被差別部落の歴史を見直す", Gakushuin University Faculty of Economics,
  <https://www.gakushuin.ac.jp/univ/eco/gakkai/pdf_files/keizai_ronsyuu/contents/4203/4203saito.pdf>
  - **FETCHED and read** (curl, HTTP 200). It is a three-page lecture summary by a historian, and it
  is about the ORIGINS debate (whether buraku discrimination must be traced back to the late ancient
  period), not about where hamlets stood. It contains no siting claim. Its one substantive passage
  concerns the four characteristics of early modern buraku - exclusion from "sacred" places,
  exclusion from social intercourse, the handling of dead cattle and horses, and the holding of
  danaba - none of which is locational.
- 部落問題 - Wikipedia (ja), Tokushima Prefectural Museum page, U-Tokyo DESK PDF, bunanomori blog,
  tottoriloop PDF - not fetched: the budget ended. The Tokushima museum page (a prefectural museum,
  on medieval status and discrimination) is the second one a follow-up should try.

**Summary for the record.** The footnote's parenthetical is currently "the historical outcast hamlet
sat at the village edge or across its stream rather than at any fixed distance out (this rests on
general reading; no source is cited)". Nothing read in this pass supports it, and nothing contradicts
it. The absence note should stand. The 60 ft collar is correctly labeled a calibration rather than a
finding, so the map rule is not at risk either way.

---

### `vegetation.html` fn-88

**CITED** - with a correction the record should take.

**URL:** <https://centerforagroforestry.org/wp-content/uploads/2024/04/06_Windbreaks_TrainingManual_2024Master_0410_Digital-7.pdf>
(University of Missouri Center for Agroforestry, *Training Manual for Applied Agroforestry Practices*,
2024 Edition, Chapter 6: Windbreaks. The default fetcher returned unusable binary; read via curl plus
`pdftotext`, HTTP 200, 3.05 MB.)

Passage verbatim (from "Windbreak Continuity", p. 73):

> Windbreak Continuity. Continuity influences efficiency. Gaps in a windbreak become funnels that
> concentrate wind flow, creating areas on the downwind side of the gap in which wind speeds often
> exceed open field wind velocities. Gaps will decrease the windbreak's effectiveness. Access lanes
> through a windbreak should be avoided or minimized.

**How it supports the claim.** The footnote's first half is carried exactly: air passing through a
constriction in the belt speeds up, and downwind of the gap it moves FASTER than it would in the open
field. That is the strongest possible form of the record's point that a bare gap in an occupied run
is actively harmful rather than merely neutral, and it is the reason the drawn belt must not carry a
bare 40 ft hole.

**The correction.** The footnote goes on to say that "where a belt must be crossed for access the
crossing is built to the same height and porosity as the rest of it rather than left as a bare
opening". **The source does not say this, and what it does say is different.** From "General Design
Considerations" (p. 77):

> • Avoid creating gaps with access roads cut through a windbreak. Wind flow increases through gaps
> decreasing windbreak effectiveness. Where needed, design the opening at an angle to prevailing
> winds. Lanes or roads through single-row barriers should be avoided; where necessary, locate them
> 100 to 500 feet from the ends of the windbreak.

And from the farmstead-windbreak guidance (p. 80):

> • Locate access roads from 100 to 500 feet from the ends of the windbreak. If a lane must cut a
> windbreak, it should cut through the windbreak at an angle to prevailing winds to prevent funneling
> of wind and snow drifting.

So the attested remedy for a necessary crossing is **geometric** - angle the opening to the prevailing
wind, and put the lane near the END of the belt rather than its middle - not "build the crossing to
the same height and porosity as the rest of it", which would close the opening and defeat the access.
The record's stated remedy is not supported and, read literally, is not buildable. The finding to
record is: a bare gap accelerates the wind and is a defect; where a crossing is unavoidable it is
angled to the prevailing wind and placed toward the belt's end.

**Applicability limit.** This is a modern US extension manual, so it is evidence about the physics of
air moving through a constriction in a tree barrier - which holds regardless of period - and about
current design practice. It is not evidence that Chinese or Japanese planters angled their crossings.
The physics half is safe to cite; the design-practice half should be labeled as a modern rule being
borrowed, or as a drawing convention.

---

### `vegetation.html` fn-90

**CITED** (partial)

**URL:** <https://www.fao.org/4/x5347e/x5347e04.htm> (FAO, *Unasylva* Vol. 2, No. 6, "Forestry in
China")

Passages verbatim:

> However, there are large amounts of "public land" upon which the people graze their livestock and
> gather fuelwood. It is estimated that 40 percent of the land area of China is unsuitable for
> agriculture but suitable for forest crops. Much of this land is hills and mountain slopes near
> densely populated areas. Much of it is unproductive now, except for poor-quality shrubs and grasses
> cut by fuel gatherers, and for poor-quality fodder grazed by livestock.

> Not only is organic matter removed from the soil and none returned, but the bare soil is exposed to
> erosion by wind and water, and soils that were fertile are rapidly being rendered incapable of
> supporting plant growth.

> Denuded mountain and waste lands suitable for reforestation purposes cover some additional 300
> million hectares.

> Pressure of people on the land has forced the unwise clearing of hill forests for crops

On the two species, and that they are the southern-China low-elevation trees:

> Cunninghamia lanceolata generally grows in the area extending from the Yangtze River southward to
> the Nanling Range at elevations not exceeding 1,000 meters. Pinus massonia grows throughout central
> and southern China at altitudes not exceeding 1,000 meters.

On the long-run direction:

> the population increased, the forest area diminished.

**How it supports the claim.** The footnote's picture of the hinterland - hills near settlement
stripped for fuel, carrying only poor scrub, bare soil, severe erosion - is carried directly, and by
a source describing China before industrialization reached these slopes (this is a 1948 report,
predating the Great Leap fuelwood clearances). The two species the footnote names are confirmed as
the trees of southern China at the elevations in question. The footnote's operative direction -
protected band lush, degraded hinterland beyond it - is supported.

**What is NOT supported.** The specific figure "roughly a thousand years". This FAO report gives the
direction (forest area diminishing as population rose, across dynasties) but no such span, and it
frames the clearance as ongoing rather than dating its start. The footnote already labels the extent
a guess ("How far that stripping went is a guess, pending a source"), and that label should stay -
but the "roughly a thousand years" phrase in the body is itself the unsourced part and should be
marked as such, not just the extent.

**A FOR THE GM candidate for the thousand-year figure.** "History of human disturbance to vegetation
in the Southeast Hills of China over the last 2900 years: Evidence from a high resolution pollen
record", *Palaeogeography, Palaeoclimatology, Palaeoecology*, DOI **10.1016/j.palaeo.2022.111028**.
Unpaywall reports `is_oa: False` - there is no open copy, so this one is genuinely paywalled rather
than bot-blocked, and it was not fetched. It would date the onset of the stripping directly from a
pollen core (a search summary put the sharp decline of evergreen broadleaved trees at 1180 CE, about
850 years, which is close to the record's "roughly a thousand" - but that is a summary and is not
being treated as evidence). If the GM has institutional access, this would convert the figure from a
guess to a finding.

A second, fully readable candidate exists but does not fit: "Maize cultivation and forest collapse
over five centuries in southern China", *Communications Earth & Environment*, 2026,
<https://www.nature.com/articles/s43247-026-03224-5> - **fetched and read**, open access. It is
rigorous and directly on topic, but it dates the collapse to the introduction of maize from the 18th
century ("prior to the 18th century, dense forests dominated the region under minimal human
influence"), i.e. **five centuries and a different mechanism**, in the karst landscapes of Southwest
China. It is closer to contradicting the thousand-year span than supporting it, for its region. It is
flagged here rather than filed as CONTRADICTED because its study area (Guizhou/Guangxi karst) is not
the southeastern hill country the footnote describes, and the pollen record above reports a much
earlier decline in that other region. The honest reading is that the onset date varies by region and
the record should not assert one figure without the regional source.

---

### `ways.html` fn-7

**CITED** (partial) - with a correction to which figure means what.

**URL 1:** <https://www.ctie.co.jp/service/publishing/img/michi-nazenaze/1-4.pdf> (CTI Engineering
Co., Ltd. / 株式会社建設技術研究所, *道のなぜなぜ* 1-4, "江戸時代の道路はどのようなものだったのですか？")

Passage verbatim (Japanese):

> このころの五街道の道幅は、山道を除いておおむね 3～4 間（約 5.4～7.2m）で、江戸に近いところでは 5 間（約 9m）確保されていました。

English translation (mine, from the Japanese):

> The road width of the Five Highways at this period was, excluding mountain roads, generally 3 to 4
> ken (about 5.4 to 7.2 m), and in places close to Edo 5 ken (about 9 m) was secured.

**URL 2:** <https://www.nippon.com/ja/japan-topics/c08604/> (nippon.com, 大名行列が通った道: 五街道と脇往還)

> 五街道の道幅は四間（一間＝1.8ｍとして7.2ｍ）から、所によっては七〜八間（12.6〜14.4ｍ）と、かなり広かったという。軍用道として活用することを計画したゆえ、道幅が広いのも当然だった。

English translation (mine, from the Japanese):

> The road width of the Five Highways is said to have been quite broad - from 4 ken (7.2 m, taking 1
> ken = 1.8 m) up to, in places, 7 to 8 ken (12.6 to 14.4 m). Since they were planned to be usable as
> military roads, it was only natural that the roads were wide.

**How this supports the claim, and the correction it forces.** The footnote says the trunk highways
were "about 9 m, narrowing to 4 to 7 m in the mountains and to 2 ken at the Hakone barrier". Two of
those three numbers can now be attached to a readable page, but **not in the roles the footnote gives
them**:

- **9 m is real but is the near-Edo figure**, not the general trunk width. CTIE gives 5 ken (~9 m)
  specifically "in places close to Edo".
- **The 5.4 to 7.2 m band is the GENERAL width, not the mountain narrowing.** CTIE gives 3 to 4 ken
  as the ordinary width of the Five Highways and explicitly **excludes mountain roads from that
  figure** (山道を除いて). So the footnote has taken the general-width number and re-labeled it as the
  mountain number. The mountain roads are precisely what the source declines to give a figure for.
- nippon.com disagrees with CTIE on the ordinary width, putting it at 4 ken (7.2 m) rising to 7-8 ken
  (12.6-14.4 m) in places. The two readable sources bracket rather than agree, which is itself worth
  recording.
- **"2 ken at the Hakone barrier" was found on no page read.** It remains entirely unsupported.

The footnote's own hedge ("a GUESS, since no page a reader can open was found to carry those
figures") is now half-wrong in the helpful direction - pages carrying trunk-highway widths do exist
and are quoted above - and half-right: the mountain narrowing and the Hakone figure are still
unsourced. The sentence should be rewritten so that 9 m is the near-Edo width, roughly 5.4 to 7.2 m
(or 7.2 m, per nippon.com) the ordinary width, the mountain width an acknowledged blank, and Hakone a
guess.

**Not addressed in this pass.** The footnote's other clauses - carts effectively absent from the
Japanese countryside, the daihachiguruma confined to Edo, Owari and Sunpu, the 2.7 m ox-cart stone
route, and the China/Japan paving split - were not the target of this note's absence marker and were
not researched here. The "wheeled carts were close to absent in the countryside" clause is still
marked "this rests on general reading; no source is cited" and nothing in this pass changed that.

---

## Things the record should change, gathered

Three of these are corrections rather than new citations, and they matter more than the new keys:

1. **`fields.html` fn-89 is backwards.** FAO says contour ridging's advantages are greater the LESS
   steep the ground. The record says the reasoning "belongs to a steep slope". Rewrite the reasoning;
   the map decision survives as a legibility choice.
2. **`vegetation.html` fn-88's remedy is not the attested one.** The source says angle the crossing to
   the prevailing wind and put it near the belt's end; it does not say rebuild the crossing to the
   same height and porosity.
3. **`ways.html` fn-7 has two numbers in the wrong roles.** 9 m is the near-Edo width; 5.4-7.2 m is
   the general width with mountain roads explicitly excluded.

And one absence note can simply be retired:

4. **`religion-and-death.html` fn-11** - the supporting sentence is on the page the last pass read and
   declared silent; it is in the paragraph on manors, not the one on monasteries.

Finally, **`cities/government.html` fn-35 deserves a second look by a person**: the only text found
anywhere matching the record's claim was on Grokipedia, a forbidden source, which raises the question
of where the claim entered the record from.
