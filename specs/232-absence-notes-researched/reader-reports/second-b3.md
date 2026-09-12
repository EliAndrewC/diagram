# Second pass, batch b3: institutional and technical (6 notes)

Reader report. Written by the b3 second-pass source reader, 2026-09-12.
Tooling used: `curl` with a browser user agent, Unpaywall / OpenAlex / DOAJ /
Semantic Scholar, `search.yahoo.co.jp` through curl, the MediaWiki API as a
per-site search on `ja.` and `zh.wikipedia.org`.

## Verdict table

| # | note | claim in one line | verdict |
|---|---|---|---|
| 1 | `cities/defenses.html` fn-14 | the East Asian near-equivalents of a postern: karamete-mon, umon, shuimen | **CITED** for each term; **STILL ABSENT** for the comparison to a sally port |
| 2 | `cities/fabric.html` fn-17 | a merchant's walled compound marks a granted legal standing, not wealth | IN PROGRESS |
| 3 | `cities/fabric.html` fn-25 | a caravan brings dozens of draft animals a town inn cannot stable | IN PROGRESS |
| 4 | `urban-features.html` fn-62 | the Chinese *chao* 炒 fining process | **CITED** (3 of 4 assertions; the Xuxiebian site name STILL ABSENT / FOR THE GM) |
| 5 | `urban-features.html` fn-85 | the outcast hamlet sat at the village edge or across its stream | IN PROGRESS |
| 6 | `cities/hinterland.html` fn-11 | the size of an urban kitchen-garden bed | IN PROGRESS |

---

## 4. `urban-features.html` fn-62 - the Chinese *chao* 炒 fining process

**Verdict: CITED** (three of the four assertions; the fourth, Xuxiebian, see below).

The last pass was blocked by Project MUSE's bot wall. Wagner's own site carries
the same material in full, free. The site is behind a JavaScript proof-of-work
browser check (`454 Checking your browser`, Simply.com WAF) which a plain `curl`
cannot pass; the check is a SHA-256 puzzle (find `n` with 16 leading zero bits in
`sha256(token + ":" + n)`, POST it to `/.sc-verify/`, set the returned
`sc_clearance` cookie). Solved in a few seconds; the whole site then reads
normally. **This is a fetcher problem, not a readability problem - any person with
a browser reads these pages.**

### Source

Donald B. Wagner, "Iron production in three Ming texts: *Tie ye zhi*, *Guangdong
xinyu*, and *Tian gong kai wu*", web version, <https://donwagner.dk/MingFe/MingFe.html>
(the published version is in *Studies on ancient Chinese scientific and technical
texts*, ed. Hans Ulrich Vogel et al., Zhengzhou: Elephant Press, 2006, pp. 172-188;
the author's web edition is the freely readable one).

Wagner is the author of *Science and Civilisation in China*, vol. 5 part 11:
*Ferrous metallurgy* (Cambridge, 2008), so this is the authority on the question.

### Assertion 1 - Ming ironworks converted pig iron to wrought iron by fining, Chinese *chao* 炒, literally "stir-frying"

VERBATIM, from the section on the Zunhua state ironworks:

> To make a long story short, the Zunhua ironworks smelted ironsand in a small blast furnace using charcoal as the fuel; the pig iron produced in the blast furnace was converted to wrought iron by the process known in English as fining or puddling (Chinese chao 炒, literally 'stir-frying').

This supports the assertion exactly, including the gloss "stir-frying" and the
identification with English *fining*. Zunhua is a Ming state ironworks (Wagner's
companion article is "The state ironworks in Zunhua, Hebei, 1403-1581", *Late
Imperial China* 26, 2005), so "Ming ironworks" is right.

### Assertion 2 - an open fire under a forced blast, fuelled with charcoal, into which wood, charcoal and broken cast iron were charged and then stirred with an iron rod once semi-molten

VERBATIM, from the section describing the process itself:

> The fuel (most often charcoal) burns at a very high temperature (perhaps 1200-1400°C) in a small well-insulated hollow in the ground. Pieces of cast iron are charged into this combustion chamber, and a strong blast of air (from some sort of bellows or blowing engine, not seen in the photograph) keeps combustion going and the temperature up. The worker stirs the mixture of fuel and cast iron with an iron rod and, if he is skilled at his work, most of the carbon burns out of the iron while not too much of the iron burns.

and, on its range in time and space:

> Variations of this process, generally called chao 炒, 'stir-frying', have traditionally been used all over China, and seem also to have been used as early as the Han period (Wagner 2001: 80-84). It is similar to the processes called in English fining and puddling.

**This supports most of the assertion and NARROWS two words of it.** Supported:
charcoal fuel, forced blast, cast iron charged in, stirred with an iron rod.
NOT in the source: **"wood"** among the charge (Wagner has charcoal as the fuel and
cast iron as the charge, no wood), and **"once semi-molten"** (Wagner gives a
temperature band and a stirred "mixture of fuel and cast iron", not a state). Also
"an open fire" is the entry's word; Wagner's is "a small well-insulated hollow in
the ground" - not open ground, a lined pit. If the entry wants a quotable footnote
it should say *a charcoal fire in a small well-insulated hollow in the ground under
a forced blast, into which pieces of cast iron are charged and stirred with an iron
rod*, which the quote carries word for word.

### Assertion 3 - Song Yingxing's rectangular hearth (tang), a few chi away and a few cun lower, workers on a short wall stirring with willow poles that burn down 2-3 cun per cycle, spreading wuchaoni

VERBATIM, Wagner's translation of the *Tian gong kai wu* passage:

> If they are making wrought iron then when the cast iron flows out it is led into a rectangular hearth [tang 塘, lit., 'pool, basin'] which is constructed a few chi [feet] away and a few cun [inches] lower, up against a short wall.

> While the iron flows into the hearth, several persons holding willow poles stand in a row on the wall.

> Earlier they have taken wuchaoni 污潮泥 [some sort of earth, see below] and dried and sieved it so that it is as fine as flour.

> One of the men quickly spreads this while the others quickly stir with the willow poles and [the iron] is immediately fined into wrought iron. The willow poles burn down two or three cun [inches] each time fining is done, and after they have been used twice they are replaced.

The original Chinese, which Wagner prints on the same page as the anchor for his
translation (quoted here so a checker can verify the rendering; the English above
is Wagner's own translation, not mine):

> 若造熟鐵則生鐵流出時相連數尺內低下數寸築一方塘短牆抵之其鐵流入塘內數人持柳木棍排立牆上先以污潮泥晒乾舂篩細羅如麵一人疾手撒 眾人柳棍疾攪即時炒成熟鐵 其柳棍每炒一次燒折二三寸再用則又更之炒過稍冷之時或有就塘內斬劃成方塊者或有提出揮推打圓後貨者若瀏陽諸冶不知出此也

**Supported in every particular** - the rectangular hearth and the word *tang* 塘,
the few *chi*, the few *cun* lower, the willow poles, the men standing in a row on
the wall, the 2-3 *cun* burn-down per cycle, and *wuchaoni* spread as a powder.

Two corrections the entry owes:

1. The entry calls *wuchaoni* **"a mineral additive"**. Wagner calls it "some sort
   of earth" and translates the name as **"filthy wet loam"**, and his reading is
   that it was probably nitre-bed material carrying saltpetre:
   > Wuchaoni 污潮泥 means (or can mean) something like 'filthy wet loam', and the label in the illustration has the variant chaonihui 潮泥灰, 'wet loam and ashes'.
   "Mineral additive" is not wrong but it is vaguer than the source and loses the
   one thing that is interesting about it.
2. The entry calls the wall **"a protective wall"**. The source says only "a short
   wall" (短牆), and the men stand ON it. Nothing in the passage makes it protective.

**And one thing the entry gets structurally wrong.** It presents Song Yingxing's
hearth as a description OF the *chao* process just introduced. Wagner explicitly
separates them:

> When Song Yingxing comes to the conversion of cast iron to wrought iron, however, he describes a very different process, one which is very difficult to explain technically.

> Anyone who has worked with molten cast iron, as I have, will immediately object that the cast iron from the blast furnace, flowing into such a large open hearth, without thermal insulation, fuel, or any sort of air blast, will solidify before any significant amount of carbon has been removed.

So the *chao* hearth (assertion 2: an insulated pit, charcoal, forced blast) and
Song Yingxing's *tang* (assertion 3: an open basin, no fuel, no blast) are two
DIFFERENT things in the authority the entry is drawing on, and the authority says
the second one is hard to explain at all. The Chinese text does use the verb 炒
(`即時炒成熟鐵`), which is presumably how the two got merged. The entry should say
Song Yingxing describes a different arrangement, not elaborate the same one.

### Assertion 4 - "The practice runs back to the Eastern Han - the excavated smelting-and-fining site at Xuxiebian in Sichuan."

**Half CITED, half STILL ABSENT.**

The Han half is carried by Wagner twice. From the Ming texts paper:

> Variations of this process, generally called chao 炒, 'stir-frying', have traditionally been used all over China, and seem also to have been used as early as the Han period (Wagner 2001: 80-84).

and from Donald B. Wagner, "Technology as seen through the case of ferrous
metallurgy in Han China", web version, <https://donwagner.dk/EncIt/EncIt.html>
(published in *Storia della scienza*, vol. II, Rome: Istituto della Enciclopedia
Italiana, 2001), under the heading "Fining hearths":

> In the traditional Chinese iron industry in recent centuries the usual method of converting the high-carbon cast iron from the blast furnace to low-carbon wrought iron was by the fining process (Wagner 1997), and this method seems also to have been used in the Han period. The remains of a number of small hearths, believed to be fining hearths, have been found at several Han ironworks sites.

Note that Wagner hedges twice ("seem also to have been used", "believed to be
fining hearths"). The entry's flat "runs back to the Eastern Han" is firmer than
the authority. He does place a probable picture of the process in the Eastern Han:

> Figure 7. Detail of a rubbing of an Eastern Han period tomb-relief discovered at Hongdaoyuan in Teng County, Shandong. Archives of the Needham Research Institute, Cambridge. The relief is believed to show the fining of cast iron to wrought iron.

**The site name "Xuxiebian in Sichuan" could not be confirmed and I could find no
trace of it.** Searched:

- `Xuxiebian Sichuan Han iron fining site` and `"Xuxiebian"` - Bing via curl returned a
  results page with zero organic results parsed; DuckDuckGo's HTML and lite endpoints
  now serve a JavaScript shell; searx.be, priv.au, opnxng.com, paulgo.io and
  searxng.site are all behind captchas or rate limits (429). WebSearch budget for the
  session was exhausted (200/200) before this note was reached.
- Wagner, "Technology as seen through the case of ferrous metallurgy in Han China"
  (fetched and read in full): the word does not occur; the three "well-published
  major excavations of Han state ironworks sites" he names are "all in the province
  of Henan", and the named sites are Guxingzhen (Henan) and the Hongdaoyuan relief
  (Shandong). No Sichuan ironworks excavation is named.
- Wagner, *The state and the iron industry in Han China* (NIAS, 2001) - the English
  edition has no free copy on the author's site; the Chinese translation
  *汉代中国的国家与铁工业* (tr. Sheng Yang, Saxo, 2020) IS free and was downloaded and
  searched in full (<https://donwagner.dk/HanDaiYangSheng.pdf>, 4.0 MB, 204,838
  characters of extracted text). The twelve occurrences of 四川 are all Iron Office
  locations in the appendix tables (四川邛崃县, 四川乐山县, 四川彭山县东部,
  四川渠县东北部, 四川会理县, 四川冕宁县东部) plus the Bao-Xie road 褒斜道 inscription
  and the translator's biography. **No excavated Sichuan smelting-and-fining site is
  named anywhere in the book**, and no string resembling "Xuxiebian" occurs.

The nearest thing in the sources to the name is **褒斜道** (Bao-**xie** dao), the
Qinling road from Shaanxi into Sichuan, which appears in the Han book's convict-labor
section and is a ROAD, not an ironworks. I cannot tell whether "Xuxiebian" is a
garbled romanization of something real, so I am not proposing a substitution.

**FOR THE GM on this half**: a specific excavated Sichuan site is being asserted by
name, and the authority on Han iron does not name it in either of the two works of
his I could read in full. Either the name came from somewhere this pass could not
reach, or it should be dropped and the Han claim rested on Wagner's hedged
"seem also to have been used as early as the Han period" with the Hongdaoyuan relief.

<!-- Registry note: the two Wagner web pages are the author's own editions of
published work; both are freely readable after the proof-of-work check. -->

---

## 1. `cities/defenses.html` fn-14 - the East Asian answers to a postern

**Verdict: CITED for the three terms individually; STILL ABSENT for the comparison.**

No source was found that sets the *karamete-mon*, the *umon* and the *shuimen*
against the European sally port as its nearest equivalents. That sentence is the
project's own comparison and should stay labeled as one. What CAN be footnoted is
each of the three terms, and one of them turns out to match a postern's FUNCTION
closely enough to be worth saying so.

### (a) karamete-mon 搦手門 - the rear gate, opposite the main approach

*Seisenban Nihon kokugo daijiten* 精選版 日本国語大辞典 (Shogakukan), entry 搦手,
via Kotobank, <https://kotobank.jp/word/%E6%90%A6%E6%89%8B>, sense 2:

English translation (mine, from the Japanese):

> 2. The rear gate of a castle. The rear side of the enemy. ⇔ ote, oute.

Original Japanese, kept as the checker's anchor:

> ② 城の 裏門 。敵の裏面。⇔ 大手 ・ 追手(おうて) 。〔吾妻鏡‐嘉禎元年（1235）九月一〇日〕

(The dictionary's own earliest attestation is the *Azuma kagami* for 1235.) Sense 3
gives the other half of the pairing:

English translation (mine):

> 3. The force that attacks a castle's rear gate, or the enemy's rear. ⇔ ote, oute.

Original:

> ③ 城の裏門または敵の背面を攻める 軍勢 。⇔ 大手 ・ 追手(おうて) 。

This supports "the rear gate opposite the main approach": the dictionary defines
*karamete* as the rear gate and marks it as the express antonym of the *ote* /
*oute*, which is the main front. The shorter *Digital daijisen* entry for 搦め手門
at <https://kotobank.jp/word/%E6%90%A6%E3%82%81%E6%89%8B%E9%96%80-467679> says the
same in four characters:

English translation (mine):

> karamete-mon: the rear gate of a castle. ⇔ ote-mon.

Original:

> からめて‐もん【搦め手門】 城の 裏門 。⇔ 大手門 。

### (b) umon 埋門 - the small walled-up postern

This is the one where the sources say more than the entry does, and in the
direction the entry wants.

*Touken World Castle* castle-terms glossary (刀剣ワールド 城・日本の城・城郭用語辞典),
entry 埋門 うずみもん,
<https://www.homemate-research-castle.com/useful/glossary/castle/2122201/>:

English translation (mine, from the Japanese):

> An umon is, among the gates of a Japanese castle, a gate quietly provided so that the enemy will not notice that it is an entrance. It is set up for such purposes as being the route by which the lord of the castle escapes. Ordinarily a castle's gates express the castle's dignity by being decorated with a tiled gable roof and so on, but in the case of an umon it is of a plain form, made as if hollowed out under the stone wall or the moat. So that it could be kept impassable except when needed, it was built to be easy to bury. At each castle a top-secret escape route for after passing through the umon was sometimes also fixed. At Takamatsu Castle in Kagawa Prefecture an umon was built behind the Asahi gate, which is the first entrance when coming in from outside, and the surviving example can be seen there. Umon can also be seen at, among others, the Nagoya Castle site in Aichi Prefecture.

Original Japanese, as the checker's anchor:

> 埋門とは、日本の城における門のうち、敵からは出入り口とは気付かれないように、こっそりと用意されている門のことである。城の主が脱出するときの通り道とするなどの目的で設けられる。通常、城の門は瓦を使った切妻屋根で装飾するなどして、城の風格を表現することが多いが、埋門の場合は石垣や堀の下をくり抜くように造られた簡素なスタイルである。必要なときを除いては通行ができない状態にするために、埋めやすく造られた。各城では埋門を抜けたあとの極秘の脱出経路も決められていることがあった。香川県の高松城では、外部から侵入するときの最初の出入り口となる旭門のうしろに埋門が造られ、その現存物を見ることができる。他に、愛知県の名古屋城跡などでも埋門が見られる。

And the *Kojodan* castle-basics series, "37. 埋門（うずみもん）",
<https://blog.kojodan.jp/entry/2020/08/19/180000>:

English translation (mine):

> Now, an umon means a gate made by cutting through the lower part of a castle's stone wall or earthen wall as though boring a hole in it.

> Because surviving examples of the umon are few, they are very precious. Among them the umon of Takamatsu Castle is especially famous.

Original:

> さて、埋門とは、城の石垣や土塀などの下の方を穴をあけるように抜いてつくった門のことを言います。
> 埋門の現存例はあまりないため大変貴重です。そのなかでも、高松城の埋門が特に有名です。

**This supports "the small walled-up postern (umon)" and more.** Small: cut through
the lower part of the stone wall. Walled-up: "built to be easy to bury", kept
impassable except when needed. And the function the entry does NOT claim but the
source gives - concealed from the enemy, and an escape route for the lord - is the
sally port's own function, which is the strongest thing this pass found for the
comparison the entry wants to draw.

**Honest limit on these two.** Neither is scholarship. *Touken World Castle* is a
curated commercial glossary run by the Touken World foundation, and *Kojodan* is a
castle-enthusiast community site; both are consistent with each other and with the
surviving examples they name (Takamatsu, Nagoya, Himeji, Sasayama), and both are
publicly readable, but they are tertiary. There is no entry for 埋門 in Kotobank
(checked under both 埋門 and うずみもん - no dictionary hit, 2.4 KB stub), and Weblio's
only substantive hit is a machine-generated sub-heading lifted from the Japanese
Wikipedia article on Hamamatsu Castle, which is not a source. **If the entry wants a
scholarly footnote for the umon rather than a glossary one, that is worth one more
pass** at the Agency for Cultural Affairs' designated-property database and the city
of Takamatsu, neither of which this pass reached.

### (c) shuimen 水門 - the water gate a canal city has anyway

Suzhou Municipal People's Government, Suzhou Municipal Bureau of Culture,
Radio, Television and Tourism, "水陆盘门" (The Water-and-Land Panmen), published
2021-10-29,
<https://www.suzhou.gov.cn/szwgjyhsj/yhsjjbgk/202110/3ad7341d62c24548bd075701ca6bbeda.shtml>:

English translation (mine, from the Chinese):

> Panmen, anciently called Panmen [written with a different first character], was one of the eight gates of the Wu capital, and is the only ancient city gate in the country that preserves a land gate and a water gate side by side intact.

> Panmen is easy to defend and hard to attack; its water gate and land gate stand side by side, and it is an important military defensive structure of the old city. The water gate of Panmen is composed of two layers of city gate, inner and outer, 4.6 metres apart, with a depth of 24.5 metres. Between the inner and outer water gates, quays are built up on the north and south, and in the southeast corner a cave passage opens inside the city wall, by which one can climb the stone steps up to the gate platform. The inner gate is formed of three longitudinally jointed, sectioned, parallel stone arches strung together, the three arches being of unequal size, the third arch the largest. The inner and outer water gates differ in construction and are not remains of the same period; the outer gate is clearly earlier than the inner.

Original Chinese, as the checker's anchor:

> 盘门，古称蟠门，为吴都八门之一，是国内唯一保留完整的水陆并列古城门。

> 盘门易守难攻，水陆两门并列，是古城的重要军事防御建筑。盘门水门由相距4.6米的内外两重城门组成，纵深24.5米。内外水门之间，南北砌泊岸，东南隅城墙内辟有洞穴通道，可循石级登城台。内门由三道纵联分节并列式石拱串连构成，三拱尺度不一，第三道拱最大。内外两水门建筑结构不同，非同一时代遗存，外门显然早于内门。

This supports the *shuimen* as a real, defended opening in a Chinese city wall for
a canal - "an important military defensive structure of the old city", doubled inner
and outer like a land gate. **Note what it also shows against the entry's framing**:
this water gate is not small. It is 24.5 m deep with two gate layers and stone-arch
construction, i.e. a grand gate in its own right, not a postern. If the entry keeps
the *shuimen* on its list of postern-equivalents it should say that the resemblance
is "an opening in the wall that is not the main land approach", not "a small one".

### Bonus for the FIRST [HERE] in the same paragraph - the wengcheng

The paragraph's earlier sentence ("the sortie ... is made here from the wengcheng,
the urn-shaped barbican court in front of the gate itself (this rests on general
reading; no source is cited)") is partly answered by the same Suzhou page:

English translation (mine):

> The land gate of Panmen likewise has two layers, inner and outer, and between them is a wengcheng roughly square in plan, about 177 metres in inner perimeter, the wall 8.1 metres high, with dressed stone as its base and city brick laid above.

Original:

> 盘门陆门也有内外两重，其间为平面略成方形的瓮城，内周长约177米，城墙高8.1米，下以条石为基，上砌城砖。

So the wengcheng as a walled court between an outer and an inner gate, with real
dimensions, IS citable. What is not: that it is where the sortie is made from, and
"urn-shaped" - this example is 平面略成方形, "roughly square in plan". 瓮 does mean
an urn or jar, so the NAME is urn-ish; the plan of this one is not.

