# Feature 232 reader report: fields-and-crops (27 notes)

Read 2026-09-12. Nothing in `research/` was edited; this file is the only output.

## How the reading was done

Every candidate below was FETCHED and read, not taken from a search summary. Where the default
fetcher was refused I followed the three-step escalation before calling anything unreadable:

1. `curl` with a browser user agent. This recovered two hosts the record had written off:
   **asianstudies.org** (the AAS "Rice, Technology, and History" article, previously logged as 403,
   redirects to `https://www.educationaboutasia.org/article/id/595/` and serves the whole article)
   and **sizes.com** (200, read in full - it simply does not carry the claim it was cited for).
2. Open-access check by license. Unpaywall answered for every DOI I put to it; it is how I found
   that the MDPI fengshui review is CC-BY (`is_oa: true`) even though MDPI 403s a fetcher, and that
   the Tai Lake polder paper has a public repository copy at `https://edepot.wur.nl/583354`.
3. Repository / mirror copies: PMC, `edepot.wur.nl`, Project Gutenberg, and a text-extraction proxy
   (`r.jina.ai`) for the MDPI page that refuses both `curl` and WebFetch.

**A fifth verdict is used: NOT SEARCHED - budget exhausted.** STILL ABSENT means "searched and
nothing readable was found". Three of these notes never got a search pass at all, because the
session-wide WebSearch budget ran out before I reached them, and one more got a pass on only half of
what it asserts. Marking those STILL ABSENT would hand the project a verdict that looks complete and
is not, so they carry NOT SEARCHED instead, with the exact query text a later reader should run.

Two limits on this pass, stated because they shape several verdicts:

- **The session's WebSearch budget (200 calls) was exhausted partway through**, by this and other
  agents. After that I searched with `curl` against html.duckduckgo.com (HTTP 202 challenge, no
  results), mojeek.com (no parseable results), bing.com (returned unrelated spam for Japanese
  queries) and **search.yahoo.co.jp, which worked** and produced the two best leads of the pass
  (the Tonami archive detail page and the Kodaira digital archive). Where a note got fewer queries
  than it deserved, the section says so.
- One fetch attempt per host, as instructed. Hosts that refused and were not retried: web-japan.org
  (403), tandfonline.com (403), preprints.org (403), mdpi.com (403 to curl AND to WebFetch),
  sfcs.fao.org (serves a Sitefinity login page), urbanauapp.org (403), wgly.hangzhou.gov.cn
  (connection failed).

## Verdicts at a glance

| # | page and footnote | verdict |
|---|---|---|
| 1 | `archetypes.html` fn-89 | CITED |
| 2 | `archetypes.html` fn-90 | CITED |
| 3 | `archetypes.html` fn-92 | CITED (partial - second mechanism only) |
| 4 | `cities/defenses.html` fn-13 | CITED (source-type limit: specialist blog) |
| 5 | `cities/fabric.html` fn-19 | **NOT SEARCHED - budget exhausted** |
| 6 | `cities/fabric.html` fn-22 | STILL ABSENT |
| 7 | `cities/fabric.html` fn-23 | CITED (tertiary) |
| 8 | `cities/fabric.html` fn-24 | **NOT SEARCHED - budget exhausted** (and it is an own estimate) |
| 9 | `cities/fabric.html` fn-29 | STILL ABSENT (near miss quoted) |
| 10 | `cities/hinterland.html` fn-12 | **CONTRADICTED** |
| 11 | `fields.html` fn-33 | FOR THE GM (Buck) + a citable substitute found |
| 12 | `fields.html` fn-51 | **CONTRADICTED** (the anecdote is ONE paddy, not two) |
| 13 | `fields.html` fn-86 | STILL ABSENT |
| 14 | `homesteads.html` fn-7 | STILL ABSENT (I read the page; the figure is not on it) |
| 15 | `homesteads.html` fn-16 | FOR THE GM (page-image viewer, no text layer) |
| 16 | `homesteads.html` fn-91 | STILL ABSENT (Japan) / **NOT SEARCHED** (the Chinese half) |
| 17 | `homesteads.html` fn-92 | STILL ABSENT |
| 18 | `homesteads.html` fn-96 | CITED |
| 19 | `homesteads.html` fn-98 | CITED (jori and caoshi); strip tenancy **NOT SEARCHED** |
| 20 | `towns.html` fn-23 | STILL ABSENT (same question as #9) |
| 21 | `urban-features.html` fn-59 | CITED (with a counterweight on the same page) |
| 22 | `vegetation.html` fn-84 | CITED (partial - fruit and bamboo, not "ringed") |
| 23 | `vegetation.html` fn-87 | STILL ABSENT + a caution the session should see |
| 24 | `water.html` fn-16 | CITED |
| 25 | `water.html` fn-17 | CITED (modern ecology, about the process not the period) |
| 26 | `water.html` fn-18 | CITED - **the 403 was the fetcher, the page is public** |
| 27 | `ways.html` fn-8 | STILL ABSENT (the Chinese half) / **NOT SEARCHED** (the Japanese half) |

Totals: 12 CITED (3 of them partial), 7 STILL ABSENT, 2 FOR THE GM, 2 CONTRADICTED, and 5 notes
carrying a NOT SEARCHED verdict or half-verdict (2 whole, 3 on half of what the note asserts).

The five a later reader must actually search are notes 5, 8, 16 (the Chinese half), 19 (strip
tenancy) and 27 (the Japanese half). Their queries are written out verbatim in their sections.
Notes 9 and 20 were searched, but in Japanese only; their untried English queries are listed too.

---

## 1. `archetypes.html` fn-89 - the stepped hill terrace where there is no valley floor

**CITED.**

**Source.** F. H. King, *Farmers of Forty Centuries; or, Permanent Agriculture in China, Korea and
Japan* (Madison, 1911), Project Gutenberg ebook 5350. Read in full as plain text at
<https://www.gutenberg.org/cache/epub/5350/pg5350.txt> (reader-facing page:
<https://www.gutenberg.org/ebooks/5350>). King was a US soil physicist who traveled China, Korea
and Japan in 1909 and describes hand cultivation as he found it - primary observation of the
practice, pre-mechanization.

**Passage, verbatim:**

> If the country was not level then the slopes have been graded into horizontal terraces varying in
> size according to the steepness of the areas in which they were cut.

and, two sentences later in the same paragraph:

> The next two illustrations, Figs. 151 and 152, give a good idea both of the small size of the rice
> fields and of the terracing which has been done to secure the water level basins.

**Second source**, corroborating the same mechanism for China. Francesca Bray, "Rice, Technology,
and History: The Case of China," *Education About Asia*, published by the Association for Asian
Studies, readable at <https://www.educationaboutasia.org/article/id/595/>:

> Other common forms of irrigation included the channeling of small streams into hillside terraces,
> and the construction of diversion canals from larger rivers, in which case the water usually had
> to be pumped up into the fields (fig. 3).

**How it supports the assertion.** The paragraph's argument is that wet rice needs a level basin and
that where the ground will not give one the basin is cut into the slope. King states exactly that
conditional - terracing is what is done *if the country was not level* - and names the purpose as
securing the water-level basin, which is the paragraph's own reasoning.

**Limit to state honestly.** Neither source says terracing is "the standard answer" or "the defining
alternative, not a rarity". They establish the mechanism and that it is ordinary; they do not
quantify how usual it is. If the entry wants the frequency claim it is still unsupported and should
be softened or separately marked.

---

## 2. `archetypes.html` fn-90 - a confined valley's rice as a chain of small fields down the floor

**CITED.**

**Source.** 「山ふところに拓かれた谷地田」 ("Yachida opened in the mountain's bosom"), from
*水土の礎* (Suido no Ishizue), the land-and-water history reference published by the Japanese
agricultural-engineering sector, at
<https://suido-ishizue.jp/daichi/part2/01/08.html>.

**Passage, English translation by this reader** (the note names the language and the translator per
the project's rule; the Japanese follows as the checker's anchor):

> Everywhere in Japan one sees paddy fields made by opening up the small valleys among the
> mountains, and to our eyes these paddies cradled in the mountain's bosom have become something
> nostalgic.

Original: 「日本のいたるところで、山あいの小さな谷を拓いてつくられた水田が見られ、我々の目には山のふところに抱かれた水田は懐しいものとなっている。」

> As late as the late Heian period the paddy fields were almost without exception yachida opened up
> valley by valley in the small valleys, using spring water and rainwater, while in the somewhat
> more open alluvial lowland downstream development had not advanced.

Original: 「平安後期には水田はほとんど例外なく小さな谷ごとに拓けた谷地田で、湧水や雨水などを利用しており、下流のやや開けた沖積低地では開発は進んでいなかった」

> Matching this scattered condition of the paddy fields, the homesteads too were scattered, and the
> landscape is thought to have been one in which small villages or dispersed settlements of one to
> a few farm households, paired with a narrow area of yachida, lay dotted about valley by valley
> along the branching narrow valleys.

Original: 「このような水田の分散状況に応じて屋敷も分散し、１戸ないし数戸の農家が狭い面積の谷地田とセットになった小村ないしは散村の形が、枝分かれした細い谷ごとにポツンポツンと散らばっているような景観を呈していたものと考えられる。」

The same page, on the form of those plots:

> seen from modern farming conditions, the farm tracks are poor and the plots are narrow and
> irregular in shape

Original: 「現代の営農条件からみると、農道が不備で区画も狭いうえに不整形で」

**Second source.** King, *Farmers of Forty Centuries* (URL as in note 1), travelling by rail through
western Japan:

> At 10:37 we are running along a narrow valley with its terraced rice paddies where many of the
> hills show naked soil among the bamboo, scattering pine and other small trees

**How it supports the assertion.** Both sources carry the core of the claim: where a valley is too
narrow to spread across, the rice runs *with* the valley as a series of small, narrow, irregular
basins opened valley by valley, rather than as one sheet.

**Limit.** Neither source says the brook threads *between* the fields. The yachida page says the
opposite of a brook in one respect worth knowing: it describes these fields as watered by
「周辺高地からの流入水、伏流水の湧水や雨水」 (inflow from the surrounding high ground, spring water
from subsurface flow, and rainwater) with poor drainage, i.e. seepage-fed rather than
stream-threaded. The chain-of-fields half is supported; the brook-between-them half is not.

---

## 3. `archetypes.html` fn-92 - why a hand-piled bund is never straight or square

**CITED (partial).** The paragraph makes two mechanisms. The second (a bund is re-made every year
and its line is re-set, so runs wander) is now quotable. The first (corners round because they slump
and are walked across) is still unfound.

**Source.** 「畦」 (aze, the paddy bund), Japanese Wikipedia,
<https://ja.wikipedia.org/wiki/%E7%95%A6>. A tertiary source; flagged as such below.

**Passages, English translation by this reader:**

> The aze is, in rice farming, earth piled from the mud inside the paddy at the boundary between one
> paddy and the next so that water does not leak out. The aze forms the paddy's plots and is at the
> same time a means of preventing water leakage through the fineness of the mud. ... among the
> processes of rice cultivation there is "bund-making" or "bund-plastering", a repair carried out
> every year before the water is let in

Original: 「畦（あぜ）は、稲作農業において、水田と水田の境に水田の中の泥土を盛って、水が外に漏れないようにしたものである。畦は、水田の区画を成すと同時に、泥土のきめ細かさによって水漏れを防ぐ方法でもある。畦畔（けいはん）や泥畦とも言われ、稲作の工程には、水を張る前に毎年修理を行う「畦作り」または「畦塗り」があり」

> Because the aze crumbles between the rice harvest and the start of spring farm work, and the grass
> that withers in winter alone leaves the boundary ambiguous, low shrubs - low enough not to cast
> shade - are sometimes planted and used as boundary markers.

Original: 「イネの収穫から春の農作業開始までの間に畦が崩れ、冬に枯れる草だけでは境界が曖昧となるのを防ぐため、木陰を作らない程度の低い潅木を植え、これを境界の目印とすることもある。」

> Where the landowners on the two sides of the aze differ, the boundary is in many cases divided by
> setting a bund there.

Original: 「畦の両側の地主が異なる場合、その境界に畦畔を設ける事によって区切られる場合が多い。」

**How it supports the assertion.** It carries the entry's own chain: the bund is piled from the
paddy's own mud (hence soft), it *crumbles* over the winter, it is re-made by hand every spring, and
the line it marks between two owners is ambiguous enough that a physical marker is sometimes needed.
That is the "re-cut a little differently every time it is re-plastered, so a straight run bows"
half.

**What is still absent.** No page was found stating that a right-angled corner is the weakest point,
that it is walked across rather than walked out to, or that corners therefore converge on a curve.

**Searches run for the corner mechanism** (query text verbatim):
- `paddy bund construction "levee" earthen ridge repaired annually erosion corners rounded puddled mud`

Candidates that search returned, and what happened to each:
- *Bunds | SSWM* <https://sswm.info/.../bunds> - not fetched: modern sanitation/water-management
  teaching material on contour bunds for erosion control, a different structure from a paddy rim.
- *Contour Bunding* <https://indiaagronet.com/indiaagronet/Agri%20engineering/contents/Bunding.htm>
  - not fetched: same reason (contour bunding as a soil-conservation technique).
- *Slope Instability of the Earthen Levee in Boston, UK* <https://arxiv.org/pdf/1401.7631> - not
  fetched: numerical simulation of a modern flood levee, nothing about hand-piled paddy rims.
- *Earth structure - Wikipedia* <https://en.wikipedia.org/wiki/Earth_structure> - not fetched:
  general building-material article.
- four US patents on levee gates - not fetched: irrelevant.
- *Paddy field - Grokipedia* - **deliberately not used**: the constitution forbids AI-generated
  encyclopedias.

I then fetched `ja.wikipedia.org/wiki/畦` directly on the reasoning that the Japanese term would
carry the maintenance practice, which is what produced the passages above.

---

## 4. `cities/defenses.html` fn-13 - the sortie is made from the wengcheng, not through a sally port

**CITED, with a source-type limit the session must weigh.**

**Source.** "Chinese fortification: an overview of parts and terminology - Part 2: Gate and moat",
*Great Ming Military*, <https://greatmingmilitary.blogspot.com/2019/06/chinese-fortification-p2.html>.
This is a specialist blog on Ming military technology, not peer-reviewed scholarship. It is careful
and well illustrated, but it is a self-published secondary source, and the project's ladder puts
primary and scholarly work first. Offered on that basis.

**Passages, verbatim:**

> The neck prevents enemy troops from storming the gate en masse, as moving a large body of troops
> across such a narrow passage in a short time is all but impossible, although this also prevents
> the defenders from sortie out to meet their enemies head on.

> On the other hand, the Weng Cheng is an enclosing wall designed to delay enemy assault and,
> whenever a chance presents itself, lure a portion of enemy troops inside, separate them from the
> main body of the army, and annihilate them. As such, it is much more spacious than barbican,
> allowing more troops to get in or out at once. It can also serve as a protected staging ground
> for the defenders that want to engage their enemies outside the walls.

**How it supports the assertion.** The entry says the sortie a European curtain makes through a sally
port is made here from the wengcheng. This page makes exactly that contrast, and in the same
direction: the European barbican's neck *prevents* the defenders sallying, while the wengcheng is
roomy enough to pass a body of troops in or out and serves as "a protected staging ground for the
defenders that want to engage their enemies outside the walls."

**Search run:** `wengcheng barbican Chinese city gate sortie sally port comparison European curtain wall`.
Other candidates from that search: Yabla dictionary entries (dictionary glosses, not fetched);
chinatravel.com Xi'an guide (tourist copy, not fetched); military-history.fandom.com (a wiki mirror
of Wikipedia, not fetched); baike.baidu.com Wengcheng (fetched nothing new - Baidu Baike is a
user-edited encyclopedia and I did not rely on it); architecturasinica.org keyword page (a term
index, no prose); en.wikipedia Deshengmen and Sally port (read in passing; neither carries the
comparison); en.wikipedia *Chinese city wall* (fetched in full for note 10 - it describes the
wengcheng's trapping function but says nothing about sorties).

---

## 5. `cities/fabric.html` fn-19 - a city house's door opens onto ground a person can walk on

**NOT SEARCHED - budget exhausted.**

**Searches run: none.** The session-wide WebSearch budget was spent before I reached this note, and
the `curl`-driven engines that still answered (search.yahoo.co.jp) are Japanese-language and poorly
suited to an English-language question about Chinese urban house access. This note has NOT had its
pass, and must not be read as "searched and nothing found".

**Queries a later reader should run, verbatim:**
- `Chinese city house entrance street lane alley access courtyard "back wall" urban fabric Ming Qing`
- `Beijing hutong house entrance onto lane every dwelling street access urban morphology study`
- `Japanese machiya roji alley access rear tenement nagaya entrance onto passage Edo townscape`
- `late imperial Chinese city residential block plot access lane network morphology open access`
- `urban morphology China traditional city "every house" access lane plot pattern research article`

**What I did read, as a near miss.** King, *Farmers of Forty Centuries*
(<https://www.gutenberg.org/cache/epub/5350/pg5350.txt>), on a Japanese port city's streets:

> Back of the rows of small stores and shops fronting on the clean narrow streets were the dwellings
> whose exits seemed to open through the stores, few or no open courts of any size separating them
> from the market or shop.

This is an observation that the dwellings behind a shop row reach the street *through* the shop -
which is consistent with the entry's rule (an entrance must open onto ground a person can walk on,
never into the back wall of the next house) but is a single city's observation and does not state
the rule. It is not enough to hang the footnote on.

---

## 6. `cities/fabric.html` fn-22 - the ruling class did not count the lodging of the poor; gazetteers foreground post-stations

**STILL ABSENT.**

**Search run** (verbatim):
`Ming Qing gazetteers inns lodging travelers post station yidi lüdian scholarship travel late imperial China`

Candidates and disposition:
- *Posthouses and Postal Delivering Services in Ancient China*, Academy of Chinese Studies
  <https://chiculture.org.hk/en/china-five-thousand-years/2243> - not fetched: a general-audience
  culture portal; even if it describes post-stations it cannot support a claim about what the
  gazetteers omit.
- *Ming Qing Studies 2021* (preview PDF) <https://www.writeupbooks.com/wp-content/uploads/2021/12/MQS21-preview.pdf>
  - not fetched: a journal front-matter preview, contents unrelated.
- *Ming dynasty - Wikipedia* <https://en.wikipedia.org/wiki/Ming_dynasty> - not fetched: a general
  survey that will not carry a claim about a documentary silence.
- *The Art of Compromise: New Maps in Local Gazetteers of the Late Qing Dynasty*, *Isis* 113(4)
  <https://www.journals.uchicago.edu/doi/full/10.1086/722360> - not fetched: about cartography in
  gazetteers, not about lodging.
- *Studies on the Lingyin Monastic Gazetteers* <https://escholarship.org/content/qt19f1n1hf/qt19f1n1hf_noSplash_99a2dacb29bc34056182f0f5a46e112a.pdf>
  - not fetched: monastic gazetteers of one temple.
- *MING QING STUDIES* site and an arXiv NLP paper - not fetched: irrelevant.

**Assessment for the session.** This is a claim about an ABSENCE in the record (nobody counted the
poor's lodging). Absences of that kind are rarely asserted in so many words even by specialists, so
a later pass may do better by looking for the positive form - a study of Ming-Qing inns that says
what sources exist and what they cover - than by looking for the negative. Until then the entry's
own "rests on general reading; no source is cited" is the honest statement.

---

## 7. `cities/fabric.html` fn-23 - the dusk ward gate is a Tang institution, relaxed well before the modeled period

**CITED, tertiary.**

**Source.** "Society of the Song dynasty", English Wikipedia,
<https://en.wikipedia.org/wiki/Society_of_the_Song_dynasty>. Tertiary; its own footnotes (to the
Song urban-history literature) would be the better citation if a later pass can reach them, per the
project's "an encyclopedia article's own references beat the article".

**Passages, verbatim:**

> After the curfew was abolished in 1063, marketplaces in Kaifeng were open every hour of the day,
> whereas a strict curfew was imposed upon the two official marketplaces of Tang era Chang'an
> starting at dusk; this curfew limited its commercial potential.

> Kaifeng's wealthy, multi-story houses and common urban dwellings were situated along the streets
> of the city, rather than hidden inside walled compounds and gated wards as they had been in the
> earlier Tang capital.

**How it supports the assertion.** Both halves of the entry's claim are there: the dusk curfew
belongs to the Tang city, and it was gone by the eleventh century - "well before the later period
these cities are modeled on".

**Searches run:**
- `Song dynasty end of ward system curfew fangshi abolished night markets Kaifeng scholarly article`
- `Song dynasty ward wall system breakdown curfew "night market" Kaifeng scholarly "ward system" Heng Chye Kiang open access`

Candidates not used and why: *Transformation of Capital City in Tang and Song China*
<https://urbanauapp.org/index.php/urbana/issue/download/16/54> - **fetch attempted, HTTP 403**, not
retried per the one-attempt rule; this looks like the best scholarly candidate and is worth one more
try from a different client. Heng Chye Kiang, *Cities of Aristocrats and Bureaucrats* - the standard
monograph on exactly this transition; the only full copy search surfaced is on dokumen.pub, a
document-piracy mirror, which I did not fetch or cite. newhanfu.com, theworldofchinese.com,
fridayeveryday.com, ezhejiang.gov.cn and several trip.com listings - popular or promotional copy,
not fetched.

---

## 8. `cities/fabric.html` fn-24 - eight to fifteen lodging houses in a highway seat of ~3,000

**NOT SEARCHED - budget exhausted**, though this is the one note where that matters least.

**Searches run: none.** The budget was gone before I reached it. The note itself says "the counts
are this record's own estimate, offered as one", so what a search could add is a calibration rather
than a citation - but it has still not had its pass, and is recorded as not searched rather than as
searched and empty.

**Queries a later reader should run, verbatim:**
- `Edo period post town hatago number of inns population shukuba honjin waki-honjin count`
- `江戸 宿場 旅籠 軒数 人口 比率 宿場町 統計`
- `Ming Qing county seat number of inns lüdian per population commercial establishments gazetteer`
- `Tokaido shukuba hatago count 1843 shukumura taigai-cho inns per town`

**Assessment.** This footnote is not a citation failure. It is an explicit own-estimate, labeled as
such in the entry text, which is what the project's guess discipline asks for. Nothing found in this
pass changes it, and I would not expect a source to exist for a synthetic per-settlement count. The
only thing that would improve it is a readable figure for inns per head of population in a
Ming-Qing county seat or an Edo post town, which would turn the estimate into a calibrated one; that
is a research question, not an absence to close.

---

## 9. `cities/fabric.html` fn-29 - an open town's field gaps are its fire break

**STILL ABSENT** for the claim as written, with a near miss worth recording.

**Near miss, read in full.** 「火除地」 (hiyokechi, fire-break ground), *kotobank*,
<https://kotobank.jp/word/%E7%81%AB%E9%99%A4%E5%9C%B0-864189>, which reprints entries from
*精選版 日本国語大辞典*, *世界大百科事典* (entry by 鈴木理生) and *日本大百科全書* (entry by 南和男).

English translation by this reader:

> Open ground left vacant as a fire break. In the Edo period it was provided to prevent fire
> spreading from one building to the next and as a place to take refuge during a fire, and in
> ordinary times it was used for various entertainments.

Original: 「火除けとしてあけておく空地。江戸時代、類焼を防ぎ、また、火事の際、避難する場所として設けられ、ふだんは種々の興行に利用された。」

> A general term for the fire-prevention zones which the shogunate, troubled by Edo's frequent
> fires, provided in order to prevent fire spreading.

Original: 「江戸の多発する火事に悩んだ幕府が，延焼防止のため設けた防火地帯の総称。」

**Why this is not the citation.** It establishes that open ground was the recognized instrument
against fire spread in a Japanese town, which is the mechanism the entry relies on. It does not say
that the incidental gaps between holdings in an unwalled country town do that work, and it is about
deliberately cleared urban ground in the shogunal capital. Using it would be over-reading. What it
does do is move the entry's claim from "a guess with nothing behind it" to "an application of an
attested mechanism to a settlement class the record does not discuss", which is a materially
different and more defensible thing to say in the entry.

**Search run:** `江戸 火除地 広小路 延焼 防止 空地 効果 都市 火災 歴史 研究`. That query was aimed at
this question, but only from the Japanese urban-firebreak side; the budget was gone before I could
come at the settlement-class claim from the other direction. Queries a later reader should still run,
verbatim: `open town fire spread firebreak gaps between buildings rural settlement density history`;
`在町 在郷町 火事 延焼 集落 密度 防火 研究`; `village fire spread thatch roof spacing firebreak
premodern Japan China study`. Other candidates from the search I did run:
karuchibe.jp essay on Edo vacant ground (a magazine column summarizing a paper - a pointer, not
fetched), weblio (dictionary mirror of the same kotobank entries), ja.wikipedia 火除地 and 江戸の火事
(not fetched once kotobank gave the encyclopedia text directly), homes.co.jp property-portal article
(promotional), a hatena blog (personal).

---

## 10. `cities/hinterland.html` fn-12 - a city does not farm inside its walls

**CONTRADICTED.** This is the most consequential finding in the batch and the session should read it
before the others.

**Source.** "Chinese city wall", English Wikipedia,
<https://en.wikipedia.org/wiki/Chinese_city_wall>. Tertiary, but it attributes the passage, and I
have named the attribution below.

**Passage, verbatim:**

> Long-term strategic considerations meant that the walls of important cities often enclosed an area
> much larger than existing urban areas in order to ensure excess capacity for growth, and to
> secure resources such as timber and farmland in times of war. The city wall of Quanzhou in Fujian
> still contained one quarter vacant land by 1945. The city wall of Suzhou by the Republic of China
> era still enclosed large tracts of farmland. The City Wall of Nanjing, built during the Ming
> dynasty, enclosed an area large enough to house an airport, bamboo forests, and lakes in modern
> times.

The article's footnote 24, carrying the Quanzhou and Suzhou statements, reads:

> Chen Zhengxiang (陈正祥). Chinese Cultural Geography (《中国文化地理》)，Joint Publishing, Beijing
> 1983, pp 68, 74

The same article also quotes the geographer Sen-Dou Chang:

> At later dates, an outer wall was often erected to enclose settlement that had spread outside the
> city, and in many cases "multiple cities" were developed at the same locality.

**What it says instead.** The entry's default - "walling ground is expensive and farmland is the
first thing left outside", with an intramural agricultural district treated as uncharacteristic and
particular to one drawn city - is the reverse of what this passage describes for important Chinese
cities: walls were routinely drawn wide of the built-up area *precisely* to enclose farmland and
timber against a siege, and two named cities still had farmland or vacant land inside the wall in
the twentieth century.

**What I could not do.** Chen Zhengxiang's *Chinese Cultural Geography* (1983) is the underlying
work and I found no readable copy; Sen-Dou Chang's urban-geography papers are the other obvious
route. Either would let the record state the wide-wall pattern properly rather than as a Wikipedia
paraphrase.

**Recommendation.** Do not simply close this absence note. The entry's stated default, and the
framing of the agricultural-district city as an exception, both need re-examining against this. If
the GM's density canon is to stand as a setting decision, it should be marked as a deliberate
deviation rather than presented as what the record shows.

**Search run:** `Chinese city wall cost labor construction "walled area" farmland left outside suburbs guanxiang scholarship`.
Other candidates: *Walled cities and urban density in China*, *Papers in Regional Science* 98(3)
<https://www.sciencedirect.com/science/article/pii/S1056819023017104> - not fetched (ScienceDirect;
a later pass should put its DOI to Unpaywall, it is the one quantitative study on exactly this
question); en.wikipedia *City Wall of Nanjing* (not fetched; the Nanjing figures appear in the page
I did read); travelchinaguide and hobblecreek (promotional); *Chinese city wall - Grokipedia* -
deliberately not used.

---

## 11. `fields.html` fn-33 - Buck's surveys corroborate that a holding was scattered over several parcels

**FOR THE GM** for Buck himself; **a citable substitute was found** for the proposition.

**The document that would settle it.**
- Title: *Land Utilization in China: A Study of 16,786 Farms in 168 Localities, and 38,256 Farm
  Families in Twenty-Two Provinces in China, 1929-1933*
- Author: John Lossing Buck
- Year: 1937 (University of Nanking; 1964 Paragon reprint is the scanned edition)
- Identifier: Internet Archive item `landutilizationi0000buck`
- URL tried: <https://archive.org/details/landutilizationi0000buck>, and the full-text file
  `https://ia801005.us.archive.org/16/items/landutilizationi0000buck/landutilizationi0000buck_djvu.txt`
- What blocked me: the item is lending-restricted. The metadata API lists a `_djvu.txt`, but
  fetching it returns HTTP 403 with an "Item not available" page. A person with an Internet Archive
  account can borrow it and read the pages; the text is not on a public page that a footnote could
  link a quote to.
- What it would settle: Buck's own parcel counts per farm (the variation between localities in the
  average number of parcels per farm, and his statement of the disadvantages of fragmentation), and
  the ~10 mu per farmer figure the paragraph attributes to Li Bozhong.
- How much it would change: it would convert the China half of this paragraph from an uncited
  attribution to a quoted one. It would not change any drawn geometry.

**The substitute, readable and quotable now.** King, *Farmers of Forty Centuries*
(<https://www.gutenberg.org/cache/epub/5350/pg5350.txt>), on Japan:

> These small areas do not represent the amount of land worked by one family, the average for Japan
> being more nearly 2.5 acres. But the lands worked by one family are seldom contiguous, they may
> even be widely scattered and very often rented.

> The people generally live in villages, going often considerable distances to their work.
> Recognizing the great disadvantage of scattered holdings broken into such small areas, the
> Japanese Government has passed laws for the adjustment of farm lands which have been in force
> since 1900.

King also gives, on the same page, the officially reported average paddy:

> The average area of the paddy field in Japan is officially reported at 1.14 se, or an area of but
> 31 by 40 feet.

**How that helps.** The sentence the footnote hangs on is "a holding was scattered over several
parcels". King states it outright for Japan, from the official land-consolidation law that was
passed to fix it, and gives the Japanese household average as 2.5 acres total - which sits directly
against the entry's "~1 cho (~2.45 ac) TOTAL, paddy plus dry" and is an independent readable
corroboration of that number. The China attribution to Buck remains uncited.

**Searches run:**
- `John Lossing Buck "Land Utilization in China" full text archive.org farm fragmented parcels average size`
- `江戸時代 農家 一戸あたり 耕地面積 平均 一町歩 田畑 石高 研究`

Other candidates: Google Books record for Buck (snippet view only, not a readable page); Springer
chapter *John Lossing Buck and Land Utilization in China* <https://link.springer.com/chapter/10.1007/978-3-030-12688-9_2>
- not fetched (paywalled chapter; a later pass should try Unpaywall on its DOI, since the book's
microdata volume would carry the parcel statistics); dokumen.pub copy of that book - a piracy
mirror, not fetched; an Internet Archive advanced-search query I ran by API returned only two Buck
items, both restricted (`landutilizationi0000buck`, `threeessaysonchi0000buck`), so there is no
public-domain Buck volume on that host to fall back to. For the Edo figure: crd.ndl.go.jp reference
case, two Yahoo Chiebukuro answers (user Q&A, not fetched), a MAFF budget PDF, a UTokyo OCW course
page, and aric.or.jp - the last is the page the entry already records as not carrying the figure.

---

## 12. `fields.html` fn-51 - two paddies found under a straw raincoat

**CONTRADICTED.** Every readable source gives the anecdote with ONE paddy, not two.

**Source.** 「千枚田について」, the official site of the Shiroyone Senmaida preservation council
(公益財団法人白米千枚田景勝保存協議会, secretariat in the Wajima city tourism section),
<https://wajima-senmaida.jp/about/>.

**Passage, English translation by this reader:**

> Because a single paddy is small enough to be hidden even under a straw raincoat, it has been sung
> since long ago in an old song: "nine hundred and ninety-nine were planted; the last one is under
> the straw raincoat."

Original: 「一枚の田が蓑の下にも隠れてしまうほど小さいことから、古くより「田植えしたのが九百九十九枚あとの一枚蓑の下」といった古謡にも歌い継がれてきました。」

The same page, on the figures in the neighboring sentences of the entry:

> On a slope of about 4 hectares facing the sea, 1004 small paddies run in succession

Original: 「海に面した約4ヘクタールの斜面に1004枚もの小さな田が連なる棚田」

> The area of a single paddy is about 18 square meters, and the smallest paddy is roughly 50
> centimeters square.

Original: 「一枚の面積は18平方メートルほどで、最小の田は50センチ四方程度です。」

**Corroborating source for the same figures**, a technical journal rather than a tourism site:
「世界農業遺産「能登の里山里海」を代表する棚田「白米の千枚田」」, *水土の知* (Journal of the Japanese
Society of Irrigation, Drainage and Rural Engineering) 90(1), PDF at
<https://www.jsidre.or.jp/wordpress/wp-content/uploads/2022/02/90-1-18.pdf>:

> The area per paddy is about 18 m2, extremely small ... 1,004 terraced paddies spread over a range
> of about 4 ha in all.

Original: 「水田1枚当たりの面積は約18 m2 と非常に小さく，... 全体で約4 ha の範囲に1,004枚の棚田が広がっている。」

**What this means for the entry.** The record's "two paddies once reported missing turned up under a
straw raincoat that had been laid on the ground" is not the attested anecdote. The attested one is a
counting song in which 999 are planted and the *last one* is under the mino. The previous pass found
the same thing at two independent sites and recorded it in the absence note; this pass confirms it
at the source and adds a second reading of the one-paddy form. The sentence should be corrected to
the one-paddy song rather than left as an absence, and the correction carries its own quote.

The JSIDRE article is also a better citation than a tourism page for the 1,004 / 4 ha / 18 m2
figures in the same paragraph, and it is a peer-facing engineering journal - worth swapping in
wherever those numbers are footnoted.

**Search run:** `"千枚田" 蓑 の下 二枚 隠れていた 田 逸話 九百九十九`. Candidates: bunka.go.jp cultural
heritage record (already read by the prior pass), ja.wikipedia 白米千枚田 (already read by the prior
pass, same one-paddy song), okuminavi / kankomie / kotobank / a personal motorcycle blog - tourism
or personal pages, not fetched; the JSIDRE PDF and the official council site, both fetched and
quoted above.

---

## 13. `fields.html` fn-86 - the ring nearest a market town is worked hardest

**STILL ABSENT.**

**Search run** (verbatim):
`China manure night soil "distance from the village" fields near village more heavily manured intensity gradient premodern agriculture`

Candidates and disposition:
- *"Treasure Nightsoil As If It Were Gold:" Economic and Ecological Links between Urban and Rural
  Areas in Late Imperial Jiangnan* <https://www.researchgate.net/publication/236803486_...> - not
  fetched: ResearchGate serves a login wall to fetchers. **This is the single best lead in the
  batch for this claim** and a later pass should chase it by its journal of record (*Journal of
  Urban History*, Xue Yong) through Unpaywall or a library copy. It is precisely about the
  city-to-field manure flow the gradient rests on.
- *The Utilization of Night-Soil as a Manure in China*, *Agronomy Journal* 38(7), 1946
  <https://acsess.onlinelibrary.wiley.com/doi/abs/10.2134/agronj1946.00021962003800070001x> - not
  fetched: Wiley abstract page; worth an Unpaywall check by a later pass.
- *Land Use and Soil Organic Carbon in China's Village Landscapes* <https://anthroecology.org/wp-content/uploads/2020/09/jiao_2010.pdf>
  - not fetched: modern soil-carbon study; would at best support a modern nutrient gradient, not a
  premodern practice.
- *The manuring principles in ancient China from the perspective of the San Cai theory*,
  *Humanities and Social Sciences Communications* <https://www.nature.com/articles/s41599-025-05815-7>
  - not fetched, and I regret it: it is open access and about premodern Chinese manuring doctrine.
  A later pass should read it first.
- schistosomiasis and swine-manure epidemiology papers, and a Slate column - not fetched,
  irrelevant or popular.

**What I did read and why it is not enough.** King, *Farmers of Forty Centuries*, describes the
night-soil traffic out of cities in detail ("Among the most common sights on our rides from Yokohama
to Tokyo, both within the city and along the roads leading to the fields, starting early in the
morning, were the loads of night soil carried on the shoulders of men and on the backs of animals,
but most commonly on strong carts drawn by men"), and records that fertilizer was hauled by water
fifteen miles from Shanghai. That establishes that manure moved from town to countryside at cost.
It does not state that the near ring was worked hardest and the fallow retreated outward, which is
the assertion. I searched King's text for "nearest", "near the city" and "distance" and found no
statement of a gradient.

---

## 14. `homesteads.html` fn-7 - a large homestead of 200+ trees across 31 species

**STILL ABSENT.** I reached and read the Tonami archive page that carries the 1987 Kashima survey,
and the 200-tree figure is not on it. The absence note is correct and is now confirmed by reading
rather than by inference.

**Page read in full.** 「２屋敷林の外観と植生」, from 『砺波平野の屋敷林』 (砺波散村地域研究所, 1996),
in the 砺波正倉 (Tonami Shoso) digital archive of the Tonami City Board of Education,
<https://1073shoso.jp/www/sankyo/detail.jsp?id=18666>. (The page is Shift_JIS; per the project's own
note it must be fetched with `curl` and decoded, which is what I did - WebFetch garbles it.)

**What the page does carry**, English translation by this reader - reproduced here because it is the
whole evidential basis of the surrounding entry and a later pass should not have to re-fetch it:

> According to a survey in Kashima, Tonami City (46 households) in 1987, of a total of 1,542 trees
> of 10 cm diameter or more, 735 were cedar, about half the total at 48 percent, an average of 16
> per household. The remaining roughly 50 percent were 83 species beginning with pine and
> persimmon.

Original: 「昭和６２年の砺波市鹿島（世帯数４６戸）での調査によると、直径１０センチ以上の全樹木数１，５４２本の内、スギは７３５本で全体の約半数の４８パーセントを占め、１戸当たり平均１６本であった。残りの約５割はマツやカキをはじめとする８３種であった。」

> The number of species per household averages about 6, ranging from 1 to 14. Tree heights run from
> 11 meters to 28 meters, averaging about 15 meters.

Original: 「１戸平均樹種数は１種から１４種で平均６種程度である。樹高は１１メートルから２８メートルで平均１５メートルくらいである。」

> Dividing the species occurring in the homestead grove into a tall-tree layer (10 meters and over),
> a middle layer (5 to 10 meters), a low layer (1 to 5 meters) and a shrub layer (1 meter and
> under), the species occurring are 44 in the tall layer, 76 in the middle, 80 in the low and 153
> in the shrub layer - truly abundant.

Original: 「屋敷林に入っている樹種を高木層（１０メートル以上）中木層（５〜１０メートル）、低木層（１〜５メートル）、小低木層（１メートル以下）に区分し観察すると、発生している樹種は、高木層４４種、中木層７６種、低木層８０種、小低木層１５３種と実に豊富である。」

> There is always a bamboo stand within the homestead, and it has served its purpose as a practical
> species. Madake, moso, hachiku, yadake, medake and so on.

Original: 「また屋敷内には必ずタケ林があって実用種としての役目を果たしてきた。マダケ、モウソウ、ハチク、ヤダケ、メダケなどである。」

And - directly relevant to note 23 below, on which faces the belt takes:

> Until now the homestead grove has had, centered on the house, tall trees of cedar together with
> oak and zelkova arranged from the south face round to the west; from the west face round to the
> north, hackberry and alder with some bamboo mixed in; and on the east face flowering trees and
> persimmon, fig and the like planted.

Original: 「今までの屋敷林は、家屋を中心に南面から西面にかけてスギを主体にカシ、ケヤキの高木が配置され、西面から北面にはエノキ、ハンノキに加え若干のタケが入り、東面には花木やカキ、イチジク等が植えられていた。」

> The garden is concentrated on the east to south faces where the front yard lies, and many
> ornamental trees are in it.

Original: 「庭園は東〜南面で前庭となるところに集中し多くの園芸木が入っている。」

**On the 200-tree homestead specifically.** A search summary asserted that one household (the
Shindō family) has "over 200 trees of 31 species", and I could not run that claim to ground: a
search summary is a pointer, never a source, so it is not found. I fetched the Tonami Shoso article
above (not there), the Tonami Kainyo Club's explainer page
<https://tonami-kainyoclub.com/カイニョとは-2/> (read in full - no tree counts at all), and a MAFF
landscape case-study PDF <https://www.maff.go.jp/j/nousin/keityo/kankyo/attach/pdf/keikan_jirei-6.pdf>
(fetched and converted; no such figure). Unfetched leads for a later pass: 砺波市 page
<https://www.city.tonami.lg.jp/info/7389p/>, the Nikkei feature
<https://www.nikkei.com/article/DGXMZO88953620W5A700C1TBP000/> (likely paywalled), and 金田章裕
『散村と屋敷林』 (Nakanishiya, a book).

**Searches run:** `砺波平野 カイニョ 屋敷林 本数 樹種 調査 スギ 一戸あたり` (WebSearch), then
`砺波 屋敷林 200本 31種 樹木` via search.yahoo.co.jp with `curl`, which is what surfaced the archive
detail page above. A third WebSearch (`砺波 屋敷林 "31種" OR "三十一種" "200本" 樹木 一戸`) was refused:
the session's search budget had run out.

---

## 15. `homesteads.html` fn-16 - a directly measured yard at Kodaira of 70 tsubo

**FOR THE GM.**

**The document that would settle it.**
- Title: 『小平市史 地理・考古・民俗編』 (*Kodaira City History: Geography, Archaeology and Folklore
  volume*), the 屋敷林 (homestead grove) text
- Publisher: 小平市 (Kodaira City), held by 小平市立図書館
- Where it is: こだいらデジタルアーカイブ on the ADEAC platform,
  <https://adeac.jp/kodaira-lib/text-list/d100010/ht002070> (a sibling text at
  `.../ht002170` also exists)
- What blocked me: the page is a JavaScript page-image viewer. Fetched at 567 KB, it decodes to a
  navigation shell - headings, a "521 pages" counter and the viewer chrome - with no article text
  in the HTML. This is the same wall the previous pass hit ("the Kodaira archive page loads a viewer
  shell with no article text"); I can now say precisely what it is. A person with a browser CAN read
  the page images; a fetcher cannot, and no OCR text layer is served.
- What it would settle: whether the 70 tsubo (231 sq m) yard is a measured figure in the city
  history, and what exactly was measured (the whole homestead lot, or the work yard).
- How much it would change: it is the upper anchor of the work-yard size band, so if the figure is
  the whole lot rather than the yard, the band's top end is wrong. Worth the GM opening the viewer.

**Searches run:** `"小平市" 農家 庭 70坪 屋敷 作業 面積 武蔵野 民俗` (WebSearch; returned only
current-day city pages, green-space plans and community-garden notices), then
`小平 農家 庭 70坪 屋敷 民俗` via search.yahoo.co.jp with `curl`, which found the two ADEAC texts.
I also fetched <https://www.city.kodaira.tokyo.jp/kurashi/072/072098.html> (Kodaira Furusato Village)
and read it: it describes the relocated farmhouses and the historic landscape of homesteads ringed
by groves with strip fields north and south of the roads, but gives no yard area.

---

## 16. `homesteads.html` fn-91 - how big a dooryard garden was

**STILL ABSENT** for the Japanese bed; **NOT SEARCHED - budget exhausted** for the Chinese
rice-south dooryard plot, which got no query of any kind.

**Japanese side - what was actually done.** One WebSearch was attempted and REFUSED - the budget was
exhausted at that moment:
`"屋敷菜園" OR "家庭菜園" 農家 屋敷地 面積 坪 自給 野菜 民俗 研究`. I then ran
`屋敷畑 菜園 面積 坪 農家` through search.yahoo.co.jp with `curl`. Its results were
agri.mynavi.jp (a modern farming-media article), four YouTube videos, kuniumi-am.co.jp, suikou-saibai.net,
asuguri.jp and chibanian.info (all modern allotment/land-price pages keyed to 坪 and 反 conversions),
sumsum.jp and bepal.net (modern self-sufficiency lifestyle pages). None of these is a source on a
premodern homestead bed and none was fetched.

I also put `屋敷畑 菜園 農家` to the MediaWiki search API (which is not WebSearch and still answers),
which returned 「家庭菜園」 as the one relevant article. I fetched it -
<https://ja.wikipedia.org/wiki/%E5%AE%B6%E5%BA%AD%E8%8F%9C%E5%9C%92> - and read its 屋敷畑 section in
full. It confirms the absence note exactly: it names the bed and its regional names, traces it to the
Yayoi period, and cites Yanagita Kunio and Miyamoto Tsuneichi on what kind of land it is, but **gives
no area at all**. English translation by this reader:

> In Japan, cultivated ground on which a household grows crops for its own consumption is called
> yashikibatake. Depending on the region it goes by various names such as "senzaibata", "saenba" and
> "kadonohatake". It is often carried on in a corner of land continuous with the homestead, in space
> left free beside a field or paddy growing cash crops, or on gap land away from the homestead such
> as a corner of a river bed.

Original: 「日本の家庭で自家消費するための作物を作る耕作地を屋敷畑という。地域によって「センザイバタ」「サエンバ」「カドノハタケ」など様々な呼称で呼ばれている。屋敷と地続きの土地の片隅や、換金作物を作る畑や田の隣の空いたスペース、河川敷などの片隅など、屋敷から離れた隙間的な土地で行われる場合も多い。」

That is worth having in the entry for a different reason than size: it says the household's own bed
was not necessarily beside the house at all, which is a constraint on where the map may put it.

**Chinese side - NOT SEARCHED.** No query was run for the rice-south farmhouse dooryard plot.
Queries a later reader should run, verbatim:
- `中国 农村 宅旁 菜地 面积 传统 民居 庭院 自给 研究`
- `Chinese farmhouse dooryard vegetable plot size homegarden area south China rice region survey`
- `home garden area square meters rural China traditional courtyard vegetable subsistence study`
- `江南 农家 宅院 菜畦 面积 传统 农书`
- and for the Japanese figure that would close the band: `屋敷畑 面積 坪 民俗調査 報告 農家 自給`

**Assessment for the session.** The entry already labels the band and the Chinese comparison as
GUESSES, which is the right treatment and this pass does not disturb it. The most promising
unexplored route is the Japanese folklore-survey literature that produced the work-yard figures in
fn-16 (a city or prefectural 民俗編 volume), since a volume that records the yard in straw mats is
the kind of source that also records the kitchen bed. The Tonami archive passage quoted under note
14 above is a useful secondary hint for the Japanese side: it places the garden and its ornamental
trees on the east-to-south front yard, i.e. it locates the bed without sizing it.

---

## 17. `homesteads.html` fn-92 - the north-China courtyard house ranges its animals along one wing

**STILL ABSENT.**

**Searches run:**
- `traditional north China farmhouse courtyard livestock kept in side wing donkey ox stable rural dwelling study`
- `華北 四合院 農家 家畜 牛 ロバ 厢房 飼う 配置 民居 研究`
- `華北 農家 家畜 厢房 牛舎 中庭 配置` (via search.yahoo.co.jp / `curl`, after the budget ran out)

Candidates and disposition:
- *The modification of North China quadrangles in response to rural social and economic changes in
  agricultural villages: 1970-2010s*, *Land Use Policy* <https://www.sciencedirect.com/science/article/abs/pii/S0264837714000295>
  - not fetched (ScienceDirect abstract page). **This is the right paper for the question** - it is
  specifically about the rural, agricultural North China quadrangle rather than the Beijing
  gentry siheyuan - and a later pass should try Unpaywall on its DOI before anything else.
- *5. Residential Buildings*, in *Chinese Culture* (an open textbook)
  <https://raider.pressbooks.pub/chineseculture/chapter/5-residential-buildings/> - **fetched and
  read.** It carries only "The ground floor houses dining rooms, kitchens, and spaces for raising
  poultry and livestock, with wells dug for water", which is about a different dwelling type
  (a multi-story earthen house), not the north-China courtyard wing. Not usable.
- ja.wikipedia 四合院 and baike.baidu 四合院 - not fetched: both describe the Beijing gentry courtyard
  house, which is the type least likely to stable animals, so they would mislead.
- lilysunchinatours.com, odynovotours.com, skjtravel.net, Pinterest boards - tourism and image
  aggregators, not fetched.
- *Pit courtyard - Grokipedia* - deliberately not used.

**What I read that is adjacent.** King, *Farmers of Forty Centuries*, in Shantung: "Such farmers
usually keep two cows, two donkeys and eight or ten pigs", and in Kiangsu he describes a farm
homestead that "consists of a compound in the form of a large quadrangle surrounding a court closed
on the south by a solid wall eight feet high". So a north-Chinese farm household keeping a team and
pigs, and a farm homestead as a walled quadrangle around a court, are both attested in a readable
primary source. Where in that quadrangle the animals stood is not stated, and that is the whole of
the claim.

---

## 18. `homesteads.html` fn-96 - the headman's storehouse holds the ledgers, the registers and the waiting tax rice

**CITED.**

**Source.** 「郷蔵」 (gogura, the village granary), *kotobank*,
<https://kotobank.jp/word/%E9%83%B7%E8%94%B5>, reprinting entries from *精選版 日本国語大辞典*,
*山川 日本史小辞典* and *ブリタニカ国際大百科事典*.

**Passages, English translation by this reader:**

> A storehouse set up in the villages in the Edo period for the storage of tax rice, or for storing
> grain against a crop failure, and the like. Not every village had one; several villages might use
> one jointly, or the nanushi's (headman's) earthen-walled storehouse might be used in its place.

Original: 「江戸時代、年貢米の保管、または凶作に備えての貯穀のためなどに村々に設置された蔵。すべての村にあったわけではなく数か村が共同使用をしたり、名主の土蔵を準用することもあった。」

> A grain store established in a rural village. It began in the Edo period as a building for storing
> tax rice. After the harvest the tax rice was delivered into each village's gogura, and thence
> forwarded to the shogunal granaries at Edo and Osaka in shogunal lands, or to the domain store or
> the market in domain lands. ... At first the village officials' private storehouses were often
> used, but because fraudulent removals of grain came to light the shogunate in 1789 (Kansei 1)
> ordered gogura to be built at the villages' own expense. The management of the storehouse was
> entrusted to the village officials, and the state of the stored and issued grain was recorded in
> ledgers.

Original: 「郷村に設置された穀物倉庫。江戸時代，年貢米の保管用に建てられたのがはじまり。年貢米は収穫後，各村の郷蔵に納められたのち，幕領では江戸・大坂の幕府蔵へ，藩領では藩庫や市場へ回送された。... はじめ村役人の私蔵を利用することが多かったが，不正な出穀が発覚したため，幕府は1789年(寛政元)村負担による郷蔵の建造を命じた。蔵の管理は村役人にゆだねられ，貯穀・出穀の状況は帳簿に記帳された。」

**How it supports the assertion.** The entry says the office needs fireproof storage because the
village's tax rice waits for collection, and that the headman therefore always has a kura. The
encyclopedia states that the tax rice was collected into a village store before forwarding, and -
the load-bearing sentence - that the headman's own dozo was used as that store, and that before 1789
it was normally the village officials' private storehouses that served.

**Nuance the entry should carry.** The same passage dates a shift: after 1789 the shogunate ordered
purpose-built village granaries because private storage invited fraud. So "the headman has the kura
and the tax rice waits in it" is best read as the earlier-Edo arrangement, with a separate village
gogura the later one. For a settlement map this is a genuine two-form case in the sense the
constitution means - it is a candidate KNOB (headman's storehouse versus a separate village
granary), not a fact to pick once.

**Not supported by this source:** that the village's land registers (検地帳) and ledgers were kept in
the kura. The related search (`"庄屋" OR "名主" 土蔵 村方文書 年貢米 保管 検地帳 蔵 歴史`) returned
kotobank 庄屋文書, ja.wikipedia 検地帳 and 庄屋, komonjyo.net and a genealogy site; of these I fetched
only kotobank 郷蔵. A later pass wanting the document half should read kotobank 庄屋文書 and the
JSTAGE archival-science review at
<https://www.jstage.jst.go.jp/article/archivalscience/29/0/29_134/_pdf/-char/ja>, which is an open
PDF on the management of early-modern village documents.

---

## 19. `homesteads.html` fn-98 - jori grid, strip tenancy, and the grass market

**CITED** for two of the three groundings; the third is still absent.

### The jori grid

**Source.** 「地形に応じた地割、条理制」, *水土の礎*, <https://suido-ishizue.jp/daichi/part2/03/02.html>.

**Passage, English translation by this reader:**

> The jori system is a system that organizes land parcels regularly and gives coordinate expression
> to tsubo of one cho (about 109 m) square. The tsubo is so conceived that it adjoins a road and a
> watercourse and can be fully equipped as a working field.

Original: 「条里制は、土地の区画を規則的に編成し、１町(約109m)方格の坪を座標表示するシステムである。坪は道路および水路に接し、圃場機能を十分備え得るように考えられている。」

> In the advanced regions such as Yamato and Yamashiro, the jori parcelling overcomes a certain
> amount of topographic constraint and covers the region continuously on true east-west and
> north-south bearings. ... In peripheral regions its spread rather loses continuity, and its
> direction deviates from the true bearings.

Original: 「条里地割は、大和・山城などの先進地域では、多少の地形上の制約を克服して東西～南北の正方位に連続的に地域をおおっている。... 周辺地域ではその広がりもやや連続性を失い、方向も正方位よりずれている。」

**How it supports the assertion.** The entry says plots take their regularity from how land was
divided, "rectilinear blocks where a survey had laid a grid over them (the 条里 jori system in
Japan)". That is this passage exactly, and the second quote is a bonus for the entry's neighboring
claim that the grain of the paddy drifts off true because real valleys let it.

**Search run:** `条里制 遺構 方格 地割 水田 歴史地理 論文 pdf`. Other candidates: Shiga prefecture PDF,
Nabunken site-report database, Heguri town PDF, Owariasahi city page, ja.wikipedia 条里制, a Gunma
archaeology FAQ, a Yurihama town history - municipal and archaeological pages, none fetched once the
水土の礎 page gave a clean statement of the system.

### The grass market (草市)

**Source.** 「草市」, *kotobank*, <https://kotobank.jp/word/%E8%8D%89%E5%B8%82-55085>, reprinting
*精選版 日本国語大辞典*, *ブリタニカ国際大百科事典 小項目事典*, and *日本大百科全書(ニッポニカ)* whose
China entry is signed by 斯波義信 (Shiba Yoshinobu, the historian of Song commerce).

**Passages, English translation by this reader:**

> soshi: a trading place established outside the walls of a prefecture or county seat in China. It
> developed in the Tang and Song periods as a center of the rural economy, and many became small
> commercial towns called zhen or shi.

Original: 「そう‐し　【草市】 中国、州県城外におかれた交易場。唐宋時代、農村経済の中心として発達し、鎮、市と呼ばれる小商業都市になるものが多かった。」

> A market established outside the walls of a prefectural or county seat in China. The name appears
> in the Eastern Jin period, but it developed most in the Tang and Song. At first it meant a place
> outside the city wall where fodder was traded, and because a fodder market was a crude market, a
> crude market came to be called a caoshi regardless of its distance from the wall or whether fodder
> was involved.

Original: 「中国において州県治の城外に設けられた市場。東晋代にその名がみえるが，最も発達したのは唐・宋時代。最初城壁外で秣(まぐさ)を取引する場所をいったが，秣市が粗末な市場であったところから，城外の遠近や秣の有無とは関係なく，粗末な市場が草市と呼ばれるようになった。」

> A name for local village markets in China. "Cao" means, as in caoqiao, "local" or "crude". In the
> Han period a local market meant little more than the market of the county seat, but in the Six
> Dynasties local commerce arose, and as against the officially established market of the county,
> markets outside the city gates and in remote villages were called caoshi. From the late Tang
> through the Song, with the development of the commercial economy, countless markets arose in the
> rural villages, and these were collectively called caoshi.

Original: 「中国で地方の村落市場の名称。草(そう)とは草橋などと同じく「地方の」「粗末な」という意味。漢代では地方市場といえば県城の市(いち)ぐらいであったが、六朝(りくちょう)時代に地方商業がおこり、県の官設の市に対し、城門外や僻村の市を草市とよんだ。唐末から宋(そう)代にかけては、商業経済の発達によって地方農村に無数の市が発生し、総称して草市といったが...」 ［斯波義信］

**How it supports the assertion.** The entry glosses the caoshi as "the informal periodic country
market that grew up away from the walled towns". All three encyclopedia entries say precisely that:
outside the walls, informal ("crude"), rural, and set against the county's official market.

**Search run:** `"草市" 唐宋 農村 定期市 起源 城外 研究 論文`. Other candidates: zh.wikipedia 草市 and
baike.baidu 草市 (user-edited, not fetched once kotobank gave signed encyclopedia entries); a Wuchang
district government news page; a Zhihu column (user content); y-history.net (a Japanese school
reference site); an economic-history forum page. Note for the record: the Japanese and Chinese
encyclopedias both name 加藤繁 (Kato Shigeru), *On the caoshi of the Tang and Song*, as the founding
study, which is the primary scholarly citation if a later pass can reach it.

### Strip tenancy

**NOT SEARCHED - budget exhausted.** No query was run for this sub-claim; it was folded into the jori
and caoshi searches above, which were aimed elsewhere, and nothing came back on it incidentally. The
entry's long-strip plot form has not had a pass.

**Queries a later reader should run, verbatim:**
- `strip fields tenancy long narrow plots China village land division tenant morphology history`
- `短冊型 地割 短冊状 耕地 新田村落 屋敷 畑 江戸時代`
- `条播 佃租 长条田 地块 形状 租佃 传统 农村 土地 分割 研究`
- `long strip parcels rural landscape East Asia land tenure plot shape historical geography`

One incidental pointer found while reading for note 15: the Kodaira city page describes its Edo
new-field villages as farmhouses ringed by groves along the road with 短冊型の畑 - "strip-shaped
fields" - running north and south of it (<https://www.city.kodaira.tokyo.jp/kurashi/072/072098.html>).
That is a readable Japanese instance of the strip plot, though it is a new-field settlement pattern
rather than a tenancy.

---

## 20. `towns.html` fn-23 - an open town's field gaps act as natural fire breaks

**STILL ABSENT.** Same question as note 9, same evidence, same verdict. The 火除地 passages quoted
under note 9 are the nearest readable thing and support the mechanism (open ground was the
recognized check on fire spread in a Japanese town) without supporting the application (that the
incidental gaps of an unwalled country town do that work and therefore buy it out of a watch tower).

One further consideration for the session, from a source I read for another note. The Tonami Kainyo
Club's page <https://tonami-kainyoclub.com/カイニョとは-2/> quotes 宮永正運『私家農業談』(1789), an Edo
agricultural treatise, on what the homestead grove is for, and the list includes 「隣家の火災の難を
防ぐ」 - "it wards off the calamity of fire from a neighboring house". That is an eighteenth-century
Japanese farmer's own statement that a *planted* barrier between holdings checks fire between
houses. It is not the field-gap claim, but it is the same reasoning attested in period, and it is a
better foundation for the entry than nothing. I did not chase a readable scan of 『私家農業談』 itself;
that is the obvious next step.

---

## 21. `urban-features.html` fn-59 - the charcoal bale had no standard weight

**CITED**, with a counterweight on the same page that the entry must carry.

**First, the correction to the record's own pointer.** The absence note says
`https://www.sizes.com/units/koku.htm - 403 Forbidden`. That 403 was the fetcher. With a browser user
agent the page returns 200 and I read it in full. It is about the koku only - capacity, the samurai
stipend, the modern standardized weights of rough, brown and milled rice, and twentieth-century koku
for lumber, shipping and fish. **It says nothing whatever about charcoal or the charcoal bale.** So
the right correction is not "unreadable" but "readable and does not support the claim": that pointer
should be dropped from the registry for this assertion whatever else happens.

**Source that does carry it.** 「俵 (単位)」 (the hyo as a unit), Japanese Wikipedia,
<https://ja.wikipedia.org/wiki/%E4%BF%B5_(%E5%8D%98%E4%BD%8D)>. Tertiary, and its statement about
charcoal is footnoted to 菅原昭二『穂別高齢者の語り聞き史（昭和編）大地を踏みしめて 上』(穂別高齢者の
語りを聞く会, 2014), p. 271 - a local oral-history volume, which is the better citation if anyone can
reach it.

**Passages, English translation by this reader:**

> The hyo is a unit used for the trading and distribution of rice and other products. It is a
> special unit independent of the shakkanho system, and the concrete quantity differs for each item
> to which it is applied.

Original: 「俵（ひょう）は、米穀などの産品の取引や流通のために使用される単位である。尺貫法の体系から独立した特殊単位で、具体的な量は対象品目ごとに異なる。」

> The hyo from the Sengoku through the Edo period was generally between two and five to, differing
> by period and by place: the shogunate, for instance, set one hyo at three to five sho, while the
> Kaga domain's hyo was five to. And the tawara itself came in various sizes such as the four-to
> bale and the six-to bale, so the standard was not fixed.

Original: 「戦国時代から江戸時代の1俵はおおむね2斗から5斗の間で時代・土地ごとに異なり、例えば幕府は1俵を3斗5升としたが、加賀藩の1俵は5斗であった。またそもそも俵自体にも、四斗俵や六斗俵などいろいろなサイズがあって、規格が一定していなかった。」

> In the case of charcoal, in the Iburi region of Hokkaido the weight per bale differed by the grade
> of the charcoal. The finest grade was packed at four kanme (about 15 kg), the good grade at ten
> kanme (37.5 kg), and lower grades, rolled up in straw matting, at eight kanme (30 kg).

Original: 「木炭の例では、北海道胆振地方においては、木炭の等級別に一俵当たりの重量が異なっていた。最上級品が四貫目詰め（約15kg）、上物は十貫目詰め（37.5kg）、さらに下の等級ではむしろで丸めた八貫目詰め（30kg）とされていた。」

**How it supports the assertion.** The entry's claim is that the charcoal hyo had no standard weight
unlike rice, so charcoal must be weighed at the point of sale. The page gives the general principle
(the quantity of a hyo differs by commodity, and the bale itself was not of fixed specification) and
one concrete charcoal case in which the weight per bale varied by a factor of two and a half - from
15 kg to 37.5 kg - across grades in a single district.

**The counterweight, on the same page.** A sentence above the charcoal example reads
「木炭の1俵は15 kgである」 - "one hyo of charcoal is 15 kg" - in a list of modern nominal bale weights
(soy and wheat 60 kg, potatoes and barley 50 kg, buckwheat 45 kg). So the same page that documents
the variation also records a modern nominal figure. The entry must not quote the first without the
second, or it will be quoting selectively. The honest statement is: the bale had no *legally* fixed
weight and in practice varied by grade and district; a nominal modern figure exists.

**A second correction to the entry's own reasoning.** The entry parenthesises "a kan is 3.75 kg".
The Hokkaido example is stated in 貫目 (kanme), and 4 kanme = about 15 kg checks out exactly at
3.75 kg per kan, so that conversion is right and is now anchored to a worked example.

**Search run:** `"炭俵" 重量 統一されていない 一定ではない 地域によって 炭 計量 歴史`. Note the trap I
hit: 「炭俵」 is also the title of a famous 1694 haikai anthology from Basho's circle, and the
ja.wikipedia article under that exact title (which I fetched) is about the poetry collection, not the
charcoal bale. The unit article is the one to cite. Other candidates: Tohoku History Museum object
record, Sakai and Osaka prefecture pages on the history of weights and measures, a kigo dictionary,
a Basho text site, ToMuCo museum collection, en.wikipedia Japanese units of measurement - none
fetched once the unit article answered.

---

## 22. `vegetation.html` fn-84 - the southern village's scattered bamboo and dooryard fruit

**CITED (partial).** The fruit trees and the bamboo are supported; "effectively ringed in bamboo" and
three of the five named fruits are not.

**Source.** "A Review of Fengshui Forests: Ecological Functions, Humanistic Values, and Potential
Applications to Enhance Biodiversity in Urban Green Landscapes and Achieve Sustainable Development
Goals", *Sustainability* 17(8), 3314 (2025), <https://www.mdpi.com/2071-1050/17/8/3314>.

**How I read it, stated for the record.** MDPI returns 403 to both `curl` with a browser user agent
and to WebFetch. Unpaywall confirms the article is open access at the publisher
(`is_oa: true`, CC-BY), so the page is freely readable by any person in a browser; the refusal is of
the automated client only. I read the text through the `r.jina.ai` text-extraction proxy against
that same URL. A reader following the footnote link will be able to read the passage; I have simply
not read it from the publisher's own server.

**Passages, verbatim:**

> In addition to timber, certain fruit trees, such as apricot, jujube, pear, plum, longan, and
> litchi, are commonly found in fengshui forests, serving as significant economic sources for local
> villagers.

> The database indicates that 36.8% (440 species) of the recorded plant species are trees, 27.4%
> (328 species) are shrubs, 27.9% (334 species) are grasses, 6.1% (73 species) are lianas, and 1.8%
> (21 species) are bamboos.

> As distinctive landscapes, fengshui forests offer aesthetic values, encompassing color, form,
> sound, and fragrance, which create enchanting environments within villages.

**How it supports the assertion.** The entry says the southern village was leafy, with houses among
scattered bamboo and dooryard fruit, and names litchi, longan, persimmon, citrus and mulberry. This
paper supports that the village groves of southern China carry fruit trees grown for villagers'
income, and names longan and litchi among them; and that bamboos are a real component of the
recorded flora.

**Limits.** (a) persimmon, citrus and mulberry are not on this list - apricot, jujube, pear and plum
are; (b) the paper is about fengshui forests, the village's structured groves, not the dooryard
specifically, so it supports "there is fruit growing in the village's trees", not "fruit trees stood
in the dooryards"; (c) nothing in it supports "some villages were effectively ringed in bamboo". A
search summary attributed a statement about Chaoshan settlement windbreaks evolving from thatched
cottages surrounded by bamboo groves to a different paper; I searched this article's text for
"Chaoshan", "windbreak" and "bamboo grove" and it is not there, so that statement remains a pointer
I could not run down.

**Search run:** `fengshui forest village South China bamboo litchi longan species composition survey paper`.
Other candidates: two ResearchGate records and one academia.edu record (login walls, not fetched);
the preprints.org review <https://www.preprints.org/frontend/manuscript/2ad1079b6b4ed5487728b91c42355664/download_pub>
- **fetch attempted, HTTP 403**, not retried, and it is the likely home of the Chaoshan statement, so
it is the first thing a later pass should try; *Conserving Large Old Trees in Guangxi*, *Ecology and
Evolution* (Wiley, open access by license - not fetched, and a good candidate for the village-tree
question).

---

## 23. `vegetation.html` fn-87 - the 1915 definition restricting the homestead grove to two sides

**STILL ABSENT**, plus a caution that bears on the section heading itself.

**On the 1915 definition.** No page carrying its words was found, and I ran one search for it:
`"居久根" 1915 定義 北西 屋敷林 西と北 防風林 起源`. The results were takakatsu.co.jp (a design
competition PDF), city.sendai.jp 居久根の保全や再生 (**fetched**; a municipal conservation-program
page with no definition or history in the body), weblio and ja.wikipedia 屋敷林, udworks.net (an NPO
explainer), tsuijimatsu.com, and a mirror encyclopedia. None carries a 1915 text. The founding
definition reaches the record only at second hand through a later paper said to quote it, exactly as
the absence note says, and that remains true after this pass.

**What IS now quotable - the north and west placement.** 「屋敷林」, Japanese Wikipedia,
<https://ja.wikipedia.org/wiki/%E5%B1%8B%E6%95%B7%E6%9E%97> (its statement footnoted to a cited
work):

English translation by this reader:

> The homestead groves of the rural districts of Iwate, Miyagi, Fukushima and Tochigi prefectures
> are called igune. "Kune" means a land boundary, and the igune is what divides the inside of the
> property from the outside. At the same time, many igune stand on the north and west sides of the
> homestead and serve as windbreak and snow-break woods.

Original: 「岩手県、宮城県、福島県、栃木県の農村部における屋敷林は「居久根（いぐね）」と言われている。「くね」は地境を意味し、居久根は敷地の内外を分けるものである。それと同時に、多くの居久根は屋敷の北側と西側に存在し、防風林や防雪林の役割を果たしている。」

> Where the arrangement of the homestead grove relative to the house is concerned, a commonality and
> a systematic pattern can often be recognized within a region, and that direction indicates the
> wind direction which must be guarded against in that region.

Original: 「家屋に対する屋敷林の配置方向には地域における共通性、系統性が認められる事が多く、その方向は当該地域において防ぐべき強風の風向を示している。」

That supports the entry's igune sentence (north and west, the winter-monsoon-facing sides) and its
per-map windward knob. It does not support the "leaving the south and east for the entrance, the
garden and the yard" half - for which see the Tonami passage quoted under note 14, which puts the
front yard and the ornamental garden on the east-to-south faces and the tall cedar from south round
to west. That is Tonami, not the igune country, and the two are windward-mirrored, which is exactly
the entry's point.

**THE CAUTION.** The same Wikipedia article, on the Izumo plain's tsuijimatsu, states the opposite
of the section heading for one named region, and says the change is recent:

English translation by this reader:

> Before the Meiji period it enclosed the entire perimeter of the house, but with the decrease in
> flood damage and changes in building style it changed into a hook shape covering only the north
> and west sides.

Original: 「明治時代以前には家の全周を囲っていたが、水害の減少と建築様式の変化から北と西側だけをカバーする鉤型の形状へと変化した。」

The heading this footnote sits under is "Does a shelter belt wrap the settlement? No - it stands on
one or two windward sides". For the Izumo tsuijimatsu the readable statement is that the belt DID
wrap the homestead in full until the Meiji period, and that the two-sided hook is the modern form -
which, for a pre-Meiji setting, is the wrong end of the change. This does not contradict the
question as asked about the village-scale Chinese grove system, and it is about a homestead rather
than a settlement, but it should be reconciled in the entry rather than left for a reader to find.
(The same article's Tonami passage independently says the tall trees run south-to-west there - a
third arrangement - which strengthens the entry's decision to make the windward side a knob.)

---

## 24. `water.html` fn-16 - the lower-Yangzi paddies are embanked polders diked out into marsh and lake

**CITED.** And the first thing to record: **the source the record gave up on is readable.**

**The pointer correction.** The absence note reads
`https://www.asianstudies.org/publications/eaa/archives/rice-technology-and-history-the-case-of-china/ - 403 Forbidden`.
Fetched with a browser user agent, that URL returns 200 and **redirects** to the article's current
home, <https://www.educationaboutasia.org/article/id/595/>, which serves the full text. The article
is Francesca Bray, "Rice, Technology, and History: The Case of China", *Education About Asia*,
published by the Association for Asian Studies. All three of the water.html notes (fn-16, fn-17,
fn-18) were closed on a 403 that was an artifact of the fetcher.

**Passage, verbatim:**

> Poldered fields were large areas of land reclaimed from a swamp or lake by the construction of a
> high, solid dyke. Houses were built on the wider parts of the dyke, which was usually planted with
> trees to prevent erosion. Inside, the polder was divided into blocks of fields with drainage
> channels running down the middle (fig. 4).

**Corroborating source**, for the conversion of marsh to paddy as a regional fact, from a
peer-reviewed open-access paper: Cao, Zhu and Okuro, "Vegetation dynamics of abandoned paddy fields
and surrounding wetlands in the lower Tumen River Basin, Northeast China", *PeerJ* (2019),
<https://pmc.ncbi.nlm.nih.gov/articles/PMC6459177/> (CC-BY):

> On the temperate lowland plain of the lower Tumen River, agricultural development has converted
> most marshland into paddy fields.

**How it supports the assertion.** The entry's claim is that wet rice is reclaimed FROM marsh and
that the lower-Yangzi polders were diked out into marsh and lake. Bray states the polder mechanism
in exactly those terms - reclaimed from a swamp or lake by a high solid dyke, with its internal
drainage - and her figure is captioned from Wang Zhen's *Nongshu* of 1313, so it is the historical
form and not a modern one.

**Limit.** Bray does not name Tai Lake or the 圩田/围田 characters; she describes the poldered field
as a Chinese type. If the entry wants the Tai Lake attribution specifically, the open-access
repository copy of "The water heritage of China: the polders of Tai Lake Basin as continuing
landscape" is waiting at <https://edepot.wur.nl/583354> (Unpaywall reports the Wageningen repository
copy as public domain; the Taylor and Francis page 403s a fetcher and I did not retry that host).
I did not read the Wageningen copy - it is the obvious next fetch and I flag it rather than claim it.

---

## 25. `water.html` fn-17 - where reclamation stops it stays reed wetland; abandoned paddy reverts to marsh

**CITED**, with the kind of source stated plainly.

**Source.** Cao, Zhu and Okuro, "Vegetation dynamics of abandoned paddy fields and surrounding
wetlands in the lower Tumen River Basin, Northeast China", *PeerJ* (2019), open access under CC-BY,
<https://pmc.ncbi.nlm.nih.gov/articles/PMC6459177/>.

**Passages, verbatim:**

> On the temperate lowland plain of the lower Tumen River, agricultural development has converted
> most marshland into paddy fields.

> Abandoned paddy fields provide opportunities to restore wetlands and serve as substitute habitats
> for wetland species.

> Plant species composition and dominance in the abandoned fields changed markedly during natural
> secondary succession. Initially, the annual weeds Echinochloa crus-galli and Bidens tripartita
> were dominant. Later, communities gradually became dominated first by Polygonum thunbergii and
> then by tussock-forming Carex rostrata.

> Our results suggest that the vegetation of abandoned paddy fields could be restored effectively
> through natural succession, although there were some differences in plant functional group traits.
> Abandoned paddy fields may be good sites for restoration of wetland species and conservation of
> wetland habitat.

**How it supports the assertion.** The entry says paddy is reclaimed from wetland and that where
reclamation stops or the ground is too wet to manage it stays reed wetland, abandoned paddy
reverting to marsh. This paper measures that reversion directly: a chronosequence of abandoned
paddies at under 5, 5 to 15 and over 15 years, on ground that was marshland before it was paddy,
returning by natural secondary succession to a wetland herb community against a natural-wetland
reference.

**What kind of claim this supports - state it in the entry.** This is a **modern ecology paper about
the plant process**, not a historical source about the period. It establishes that an abandoned
paddy in a temperate East Asian lowland reverts to wetland vegetation on a decadal timescale, which
is a fact about the plants and the hydrology and therefore transfers. It does not establish anything
about how often premodern farmers abandoned paddy or what the resulting ground looked like to them.
Do not let the footnote imply otherwise.

**Search run:** `abandoned paddy field succession reed wetland marsh revert vegetation study Japan`.
Other candidates: *Paddy fields located in water storage zones could take over the wetland plant
community*, *Scientific Reports* (open access, not fetched - a second citable option); "Vegetation
dynamics of abandoned paddy fields and their levee slopes in mountainous regions of central Japan",
*Japanese Journal of Ecology* 46(3) on J-STAGE (not fetched; Japanese-language, and would be the
better Japan-side citation); ScienceDirect abstracts for the Tama Hills and seed-bank studies
(abstract pages); a Springer chapter on a flood-control pond; a Chinese-language Jingxin wetland
paper. I fetched the PMC copy because it is the one that is fully readable and covers both halves of
the entry's sentence in one paper.

---

## 26. `water.html` fn-18 - the AAS "Rice, Technology, and History" sources line

**CITED. The 403 was the fetcher; the page is public.**

**Source.** Francesca Bray, "Rice, Technology, and History: The Case of China", *Education About
Asia*, Association for Asian Studies. The URL in the record redirects to, and the article is read at,
<https://www.educationaboutasia.org/article/id/595/>.

**Passages, verbatim,** matching each element the sources line claims:

Rice domesticated in naturally marshy areas:

> The earliest finds of domesticated rice in China (some of which may date back as far as 10,000
> BCE) are in naturally marshy areas close to rivers.

Paddy as a leveled, bunded basin, and why the basins are small - which also underwrites the
neighboring size claims in `archetypes.html`:

> However, a good rice field or paddy is one in which the water supply can be accurately regulated
> and drained, which means leveling the field and surrounding it by low dykes or bunds; this type of
> field dates back well over two thousand years in the Jiangnan and Canton regions. Since the depth
> of water throughout the field must be even, paddies were usually small by Western standards: a
> field twenty yards square would be considered large (fig. 2).

Polders diked from swamp or lake:

> Poldered fields were large areas of land reclaimed from a swamp or lake by the construction of a
> high, solid dyke.

Hillside terraces fed by channeled streams:

> Other common forms of irrigation included the channeling of small streams into hillside terraces,
> and the construction of diversion canals from larger rivers

**What is NOT on the page.** The sources line also claims "abandoned paddies reverting to wetland".
I searched the full text for "abandon", "revert", "return" and "waste" and that statement is not in
the article. That element must come from the PeerJ paper under note 25, not from Bray. The sources
line should be corrected accordingly.

**One more thing worth taking from this page**, since the record is paying for the citation anyway -
it is the readable primary-facing statement that a paddy gains rather than loses fertility, which
several other entries assert:

> So it is not surprising that rice farmers have often preferred intensifying production in their
> existing fields to extending the cultivated area, especially since unlike dry fields, rice paddies
> gain rather than lose fertility over the years.

---

## 27. `ways.html` fn-8 - Chinese stone-slab causeways against Japanese highway-only paving

**STILL ABSENT** for the Chinese half, which was searched; **NOT SEARCHED - budget exhausted** for
the Japanese half of the contrast, which got no query of its own.

**Search run for the Chinese half** (verbatim): `石板路 江南 水乡 村道 铺石 古道 挑夫 独轮车 泥泞 研究`

Candidates and disposition:
- ctrip and thepaper.cn travel features on Wuzhen and the Jiangnan water towns - not fetched:
  travel writing.
- *石板路*, China National Geography <https://www.dili360.com/index.php/ch/article/p5350c3d968dc604.htm>
  - not fetched. In hindsight this was the best candidate in the list (a serious popular-geography
  magazine, on the stone-slab road as a form) and a later pass should read it.
- shqp.gov.cn planning commentary, nju.edu.cn heritage-listing news - not fetched: planning and news
  copy.
- a ResearchGate PDF on modern rural road pavement condition, an arXiv paper on tourist-attraction
  congestion, a drainage paper on Jiangnan water towns, and an unrelated LLM benchmark - not fetched:
  modern engineering or irrelevant.

**What I read that bears on it.** King, *Farmers of Forty Centuries*
(<https://www.gutenberg.org/cache/epub/5350/pg5350.txt>), on Chinese land transport:

> For adaptability to the worst road conditions no vehicle equals the wheelbarrow, progressing by
> one wheel and two feet. No vehicle is used more in China, if the carrying pole is excepted

> It is only in northern China, and then in the more level portions, where there are few or no
> canals, that carts have been extensively used, but are more difficult to manage on bad roads.

> There are Government courier or postal roads which connect Peking with the most distant parts of
> the Empire, some twenty-one being usually enumerated. ... In the plains regions these roads may be
> sixty to seventy-five feet wide, paved and occasionally bordered by rows of trees.

And, on a Japanese port city's streets:

> our course led through streets paved with long, thick and narrow stone blocks, having deep open
> gutters on one or both sides close along the houses

**Queries a later reader should run for the Japanese half, verbatim:**
- `江戸時代 街道 石畳 箱根 峠 舗装 なぜ 峠だけ 理由`
- `Edo period highway paving stone pavement Hakone pass ishidatami only steep sections history`
- `旧街道 石畳 現存 区間 一覧 峠 舗装 街道史`
- and to finish the Chinese half properly: `中国 古道 石板路 铺设 乡村 道路 历史 研究 泥泞`

**Why what I read is not the citation, and a warning.** King supports the entry's neighboring claim that the
Chinese countryside moved goods by barrow and carrying pole rather than by cart, and that China's
*trunk* roads were paved. He does not describe narrow stone-slab causeways through the wet rice
south. Worse for the entry as drafted, his Japanese observation is of a *city street* paved with
stone blocks, which sits awkwardly beside "Japan paved only its highways and only on steep passes" -
it does not contradict it (a city street is neither a highway nor a village lane) but it shows how
easily that sentence over-reaches. The contrast as written should stay marked as resting on general
reading until a source describes both sides.

---

## Things found for the record that are outside these 27 notes

Recorded here because they were read in this pass and a later session should not have to find them
again.

1. **`sizes.com` is readable** with a browser user agent, and the koku page does not support the
   charcoal claim it was attached to (note 21). Two corrections in one.
2. **`asianstudies.org`'s EAA archive redirects to `educationaboutasia.org`** and serves full text
   (notes 24 to 26). Any other EAA citation in the registry marked 403 should be re-tried.
3. **The JSIDRE journal article on Shiroyone Senmaida** (<https://www.jsidre.or.jp/wordpress/wp-content/uploads/2022/02/90-1-18.pdf>)
   is a technical-journal source for the 1,004 paddies / ~4 ha / ~18 m2 figures, better than the
   tourism page those figures are currently taken from (note 12).
4. **The Tonami Shoso article** behind the Kashima 1987 survey is at
   <https://1073shoso.jp/www/sankyo/detail.jsp?id=18666> and must be fetched with `curl` and decoded
   from Shift_JIS. Note 14 quotes the whole of its evidential content, including the four-layer
   species counts and the "there is always a bamboo stand within the homestead" sentence.
5. **Two-form candidates surfaced by this pass**, in the sense the constitution means by "two
   supportable answers become a knob": the headman's private kura versus a purpose-built village
   gogura after 1789 (note 18), and the pre-Meiji full-perimeter tsuijimatsu versus the modern
   two-sided hook (note 23).
6. **The Tai Lake polder paper has a free repository copy** at <https://edepot.wur.nl/583354>
   (unread by me), which would let `water.html` name Tai Lake directly rather than resting on Bray's
   general description of the poldered field (note 24).
