# Second pass, batch b3: institutional and technical (6 notes)

Reader report. Written by the b3 second-pass source reader, 2026-09-12.

**Tooling actually used** (as against what was suggested): `curl` with a browser
user agent throughout; a Python solver for the SHA-256 proof-of-work browser check
in front of `donwagner.dk`; `search.yahoo.co.jp` through curl (which worked, then
rate-limited this session to a 3.7 KB throttle page after about eight queries);
the OpenAlex API, which is what found the one open-access monograph in this batch;
the J-STAGE search API for Japanese scholarship; the MediaWiki API against
`zh.wikisource.org` (not Wikipedia - the primary text itself); and `pdftotext` over
two downloaded PDFs. **What did NOT work**, so nobody repeats it: the session's
WebSearch budget was already spent (200/200) before this batch began;
`html.duckduckgo.com` and `lite.duckduckgo.com` now serve a JavaScript shell;
Bing via curl returns a results page with no organic results parsed; `searx.be`,
`priv.au`, `opnxng.com`, `paulgo.io` and `searxng.site` are behind captchas or
return 429; `ctext.org`'s web pages are behind Cloudflare Turnstile, though its
**API at `api.ctext.org` answers normally**.

**A note on transcription.** Kotobank renders some readings as ruby and marks
non-joyo kanji with a small superscript `×`; it also puts spaces around words it
hyperlinks. The Japanese originals below are transcribed as a READER sees the
running text - ruby readings and the `×` marker dropped, hyperlink spacing closed
up - and every one was re-checked character for character against the live page
with ruby stripped. Parenthesized readings that the dictionary itself prints in the
text, as Nipponica does (庄屋(しょうや)), are kept. The *Qimin yaoshu* originals are
given in the Wikisource WIKITEXT form, where Jia Sixie's interlinear notes are
wrapped in `{{*|` ... `|}}`; on the rendered page at the URL given, the same
characters appear as inline notes without the braces, and each passage quoted below
was confirmed present on that rendered page.

## Verdict table

| # | note | claim in one line | verdict |
|---|---|---|---|
| 1 | `cities/defenses.html` fn-14 | the East Asian near-equivalents of a postern: karamete-mon, umon, shuimen | **CITED** for each term; **STILL ABSENT** for the comparison to a sally port |
| 2 | `cities/fabric.html` fn-17 | a merchant's walled compound marks a granted legal standing, not wealth | **CITED** for the mechanism (nagayamon by rank/office; myoji-taito in perpetuity to purveyor merchants); the "wealth cannot buy it" half is a **deviation** the record contradicts for late Edo |
| 3 | `cities/fabric.html` fn-25 | a caravan brings dozens of draft animals a town inn cannot stable | **CITED** for the scale (100 horses + 100 porters standing per Tokaido station, overflow to 10 ri) and for oxen as freight animals; **STILL ABSENT** for the town-inn-versus-city contrast |
| 4 | `urban-features.html` fn-62 | the Chinese *chao* 炒 fining process | **CITED** (3 of 4 assertions; the Xuxiebian site name STILL ABSENT / FOR THE GM) |
| 5 | `urban-features.html` fn-85 | the outcast hamlet sat at the village edge or across its stream | **CITED** (Abele 2018, open access: "a clear separation" inside one village territory, peasants nearer two OTHER villages than their own kawata); the stream half rests on the kawaramono etymology |
| 6 | `cities/hinterland.html` fn-11 | the size of an urban kitchen-garden bed | **CITED** - *Qimin yaoshu* gives the bed as 2 x 1 paces with its reason, and a 30-mu ten-well market garden backing on the city wall; the entry's 55 ft is a PARCEL, not a bed |

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

### Assertion 2 - the entry's words: "an open fire under a forced blast, fuelled with charcoal, into which wood, charcoal and broken cast iron were charged and then stirred with an iron rod once semi-molten"

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

> ② 城の裏門。敵の裏面。⇔大手・追手(おうて)。〔吾妻鏡‐嘉禎元年（1235）九月一〇日〕

(The dictionary's own earliest attestation is the *Azuma kagami* for 1235.) Sense 3
gives the other half of the pairing:

English translation (mine):

> 3. The force that attacks a castle's rear gate, or the enemy's rear. ⇔ ote, oute.

Original:

> ③ 城の裏門または敵の背面を攻める軍勢。⇔大手・追手(おうて)。

This supports "the rear gate opposite the main approach": the dictionary defines
*karamete* as the rear gate and marks it as the express antonym of the *ote* /
*oute*, which is the main front. The shorter *Digital daijisen* entry for 搦め手門
at <https://kotobank.jp/word/%E6%90%A6%E3%82%81%E6%89%8B%E9%96%80-467679> says the
same in four characters:

English translation (mine), of the definition under the headword
からめて‐もん【搦め手門】:

> The rear gate of a castle. ⇔ ote-mon.

Original:

> 城の裏門。⇔大手門。

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

> Panmen is easy to defend and hard to attack; its water gate and land gate stand side by side, and it is an important military defensive structure of the old city. The water gate of Panmen is composed of two layers of city gate, inner and outer, 4.6 meters apart, with a depth of 24.5 meters. Between the inner and outer water gates, quays are built up on the north and south, and in the southeast corner a cave passage opens inside the city wall, by which one can climb the stone steps up to the gate platform. The inner gate is formed of three longitudinally jointed, sectioned, parallel stone arches strung together, the three arches being of unequal size, the third arch the largest. The inner and outer water gates differ in construction and are not remains of the same period; the outer gate is clearly earlier than the inner.

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

> The land gate of Panmen likewise has two layers, inner and outer, and between them is a wengcheng roughly square in plan, about 177 meters in inner perimeter, the wall 8.1 meters high, with dressed stone as its base and city brick laid above.

Original:

> 盘门陆门也有内外两重，其间为平面略成方形的瓮城，内周长约177米，城墙高8.1米，下以条石为基，上砌城砖。

So the wengcheng as a walled court between an outer and an inner gate, with real
dimensions, IS citable. What is not: that it is where the sortie is made from, and
"urn-shaped" - this example is 平面略成方形, "roughly square in plan". 瓮 does mean
an urn or jar, so the NAME is urn-ish; the plan of this one is not.

---

## 2. `cities/fabric.html` fn-17 - the merchant's wall marks legal standing, not money

**Verdict: CITED for the historical mechanism the setting rule is modeled on**
(with one honest limit that cuts against it, below). The GM's ruling about the
setting is canon and needs no citation; what CAN now be footnoted is that the rule
has a real Tokugawa analogue, and that the analogue runs through the GATE
specifically.

### The gate itself was a permission, and its form was fixed by rank

This is the closest historical thing to "a gated compound is a right the daimyo
explicitly grants to a particular family". The *nagayamon* 長屋門, the gatehouse
with flanking wings, is the form in question.

*Sekai daihyakka jiten* 世界大百科事典（旧版）(Heibonsha), in the passage on 長屋門
within its article on the *nagaya*, via Kotobank,
<https://kotobank.jp/word/%E9%95%B7%E5%B1%8B%E9%96%80>
(Kotobank labels this block 世界大百科事典（旧版）内の 長屋門 の言及):

English translation (mine, from the Japanese):

> The nagayamon, made by putting a door in part of this row-house and placing a watchman's (chugen's) room beside it for a lookout, was what expressed the formal rank of a warrior residence. In the villages, this nagayamon was permitted to be built only by the upper stratum of farmers who served as village officials such as nanushi and shoya.

Original Japanese, as the checker's anchor:

> この長屋の一部に扉をつけて出入口にし，その脇に見張り番人(中間)部屋を置いたのが長屋門で，武家屋敷の格式を表すものであった。この長屋門は農村においては名主，庄屋など村役人を務める上層の農民だけに建てることが許されていた。

*Nihon daihyakka zensho (Nipponica)* 日本大百科全書, article 長屋門 by Kudo Keisho
工藤圭章, same page:

English translation (mine):

> As a gate of a warrior residence the yakui-mon and the heichu-mon were also used, but the nagayamon is distinguished by having guard posts projecting on either side of the gate, and its form and structure were laid down according to the house rank of the daimyo or hatamoto. ... In time, besides warrior residences, there appeared farmhouses whose owners had served as shoya or nanushi, townhouses such as those of the machi-doshiyori, and temples too, that took the nagayamon form. These have no guard post, and the rooms on either side of the doorway were used as men's rooms, attendants' rooms, sheds, stables and so on.

Original:

> 武家屋敷の門としては薬医(やくい)門・屏中(へいちゅう)門なども用いられたが、長屋門は門の両わきに突出する番所(ばんしょ)を設けるのが特徴で、大名や旗本の家格によってその形や構造が定められていた。 ... やがて武家屋敷のほか、庄屋(しょうや)・名主を勤めた農家や、町年寄などの町家や寺院にも、長屋門形式をとるものが現れる。これらには番所はなく、扉口両わきの部屋は男部屋、伴部屋(ともべや)、納屋(なや)、厩(うまや)などに利用された。

*Britannica kokusai daihyakka jiten* ブリタニカ国際大百科事典 小項目事典, same page:

English translation (mine):

> Its form was laid down according to the koku yield. Also, local notables and old houses and the like were permitted to have a nagayamon.

Original:

> 石高(こくだか)によってその形式が定められていた。また地方の名士や旧家などにも長屋門をもつことが認められた。

**This supports the entry's rule closely.** The gate is not a thing a householder
simply builds: its form follows the holder's rank, and outside the warrior class it
belongs to an OFFICE - *nanushi* and *shoya* in the villages, *machi-doshiyori* (town
elder) among townsmen - and is described in the sources with the verbs of permission
(許されていた, 認められた). A rich commoner who was not one of those did not have one.
Note also the last sentence of the Nipponica quote for the map: on the commoner
version there is no guard post, and the flanking rooms are men's rooms, sheds and
STABLES - which is what a merchant compound's gate range would actually hold.

### The companion privilege: the surname carried down the generations

The entry's parallel ("permission to carry a surname down the generations without
being samurai") is *myoji-taito* 苗字帯刀, and it is attested in exactly that shape.

*Nihon daihyakka zensho (Nipponica)*, article 苗字帯刀 by Kitahara Akio 北原章男, via
Kotobank, <https://kotobank.jp/word/%E8%8B%97%E5%AD%97%E5%B8%AF%E5%88%80>:

English translation (mine):

> In the Edo period, one of the privileges permitted to warriors, along with kirisute-gomen and the like. But it was at times permitted to the common people of farmer, artisan and merchant as well. Most of these were goshi, and shoya (nanushi) of special pedigree, town elders, purveyor merchants and so on, and besides these there were filial sons and persons of special merit. However, it was rare to be permitted both the surname and the wearing of swords; there were those with the surname only, those with the sword only, and among them some for a single generation only and some in perpetuity, and so on in various forms.

Original:

> 江戸時代、切捨御免(きりすてごめん)などとともに武士に許された特権の一つ。しかし、ときとして農工商の庶民にも許された。その多くは郷士をはじめ特別の由緒をもつ庄屋(しょうや)（名主(なぬし)）、町年寄、御用商人などであり、ほかに孝行者や特別に功労のあったものなどがあった。だが、苗字と帯刀をともに許されるのはまれであり、苗字だけのもの、帯刀だけのもの、それも一代限りのもの、永代にわたるものなどさまざまであった。

**"Purveyor merchants" (御用商人), "in perpetuity" (永代), and "the surname only" are
the entry's sentence almost word for word.** The same article adds the point the
entry's "one to three of them have one" depends on - that a domain could grant it
only inside its own territory:

English translation (mine):

> The shogunate permitted it without regard to whether the land was shogunal or private, and in that case the privilege was valid throughout the country. In the case of a daimyo or hatamoto, however, the privilege could be permitted only to those within the domain, and its validity too was limited to the domain.

Original:

> 幕府は御領・私領のいかんを問わずにそれを許したが、その場合、特権は全国に通用した。しかし、大名・旗本の場合、特権は領内のものにしか許すことができず、その有効範囲も領内に限られた。

And *Kaitei shinpan Sekai daihyakka jiten* 改訂新版 世界大百科事典, article 苗字帯刀, by
Mizubayashi Takeshi 水林彪, same page, on the political point of granting it - which IS the entry's
point about privilege as an instrument of rule:

English translation (mine):

> Entering the early modern period, by a series of state policies such as the separation of warrior from peasant and the sword hunt, it was institutionally settled that myoji-taito was in principle a privilege proper to the warrior status. There were, however, exceptions, and the shogunate and the domains in special cases permitted myoji-taito to persons not of warrior status, giving them an authority equivalent to the warrior status. ... Such a policy of specially licensing myoji-taito constituted one powerful means by which early modern power penetrated the localities.

Original:

> 近世に入って兵農分離，刀狩等の一連の国家の政策によって，苗字帯刀が原則として武士身分に固有の特権であることが制度的に確定される。しかし，例外があり，幕府，藩は特別の場合に士身分以外の者に苗字帯刀を許し，士身分に準ずる権威を与えていた。 ... このような苗字帯刀の特許の政策は，近世権力が在地に浸透してゆくための一つの有力な手段をなしていた。

### The honest limit - the record says money often DID buy it

The entry's load-bearing sentence is "a gated compound is not something wealth can
buy". For the surname-and-sword privilege the record contradicts that for the later
Edo period, and the entry should know it is departing:

*Hyakka jiten Mypaedia* 百科事典マイペディア (Heibonsha), article 苗字帯刀, same page:

English translation (mine):

> From the middle of the early modern period onward, in line with the various domains' financial distress, they issued the qualification indiscriminately to peasants and townsmen as well, in exchange for monetary contributions and the like.

Original:

> 近世中期以降は百姓・町人に対しても諸藩の財政窮乏に従い献金などと引換えにその資格を乱発。

and *Yamakawa Nihonshi shojiten* 山川 日本史小辞典 改訂新版, article 苗字帯刀, same page:

English translation (mine):

> The shogunate and the domains gave this privilege as a favor even to the ruled statuses other than the warrior status - to those who had rendered special social service, those who made large monetary contributions, and those who performed auxiliary duties connected with rule, such as ogashoya and machi-doshiyori.

Original:

> しかし幕府や諸藩は，武士身分以外の被支配身分にも，特別の社会的功績があった者，多額の献金をした者，大庄屋・町年寄などの統治に関わる補助的業務を行う者には，この特権を恩典として与えた。

So: it was always the lord's GRANT and never simply a purchase - which is the
entry's structural point and it stands - but by late Edo a large enough contribution
was one of the three recognized grounds for the grant, so "not something wealth can
buy" is a **deliberate deviation** from the record's later phase rather than a
finding. Nothing was found stating that a WALL or GATE could be bought this way;
the gate sources above tie it only to rank and office. **The cleanest form for the
entry**: the gate follows rank and office (cited, *nagayamon*), the surname is
granted and can be perpetual (cited, *myoji-taito*), and the setting's refusal to
let money alone buy the grant is the GM's ruling, marked as a deviation.

### What was NOT found

- No source setting a numerical ratio of walled to unwalled merchant compounds in a
  settlement of any size, so "one to three of them have one" out of "a dozen or so"
  remains uncited and should stay a setting figure.
- No sumptuary edict text naming a wall or gate among the things forbidden to
  townsmen was reached in this pass. Searched Kotobank for 長屋門 (hit, used above)
  and 苗字帯刀 (hit, used above); a Yahoo Japan search for
  `苗字帯刀 御免 町人 豪商 特権 藩 許可` was returned as a 3.7 KB throttle page
  (Yahoo rate-limited this session after about eight queries) and was not retried.
  **Worth one more pass** at the shogunal edict collections (*Ofuregaki kanpo
  shusei* and the domain codes) for a clause on 門構え, which is where a direct
  prohibition would be if it exists.

---

## 3. `cities/fabric.html` fn-25 - what a caravan's animals need at a city

**Verdict: CITED for the scale of animals a settlement on a trade road had to
hold, and for oxen as goods-carrying animals; STILL ABSENT for the town-inn versus
city contrast.**

### The standing requirement was a hundred horses and a hundred porters, and it rose with traffic

Ministry of Land, Infrastructure, Transport and Tourism, Kanto Regional Development
Bureau, Yokohama National Highway Office, *Tokaido e no izanai*, Tokaido Q&A Q17,
"人馬の「継ぎ送り」とはどういうことですか？",
<https://www.ktr.mlit.go.jp/yokohama/tokaido/02_tokaido/04_qa/index2/a0217.htm>:

English translation (mine, from the Japanese):

> For this reason each post station was placed under an obligation to keep permanently on hand porters and horses for carrying the baggage. At first each station on the Tokaido was made to keep 36 horses, but from Kan'ei 15 (1638) onward the stationing and relaying of 100 post horses and 100 post porters was made obligatory.

Original:

> このため各宿では、荷物を運ぶための人足と馬を常備することが義務づけられていました。はじめ東海道の各宿には３６疋の馬を備えさせましたが、寛永１５年（１６３８）以降、１００疋の伝馬と１００人の伝馬人足の設置および継立が義務づけられました。

Same source, Q5, "宿駅伝馬制度って、なんのこと？",
<https://www.ktr.mlit.go.jp/yokohama/tokaido/02_tokaido/04_qa/index1/a0105.htm>,
for the fact that the number tracked traffic:

English translation (mine):

> The post horses were at first fixed at 36, but subsequently, as the volume of traffic increased, were raised to 100.

Original:

> 伝馬は当初36疋と定められていましたが、その後交通量が増えるとともに100疋に増えています。

Yokkaichi City Museum, exhibition guide 3411, "東海道伝馬制度",
<http://guidance.city.yokkaichi.mie.jp/hakubutsukan/jp/3411.html>, which adds the
spacing and the word "every day":

English translation (mine):

> On the Tokaido, post stations were set up at intervals of roughly 2 to 3 ri (about 10 km), and the shogunate had each post station make ready 100 horses and 100 porters every day. ... This is because it was laid down that the horses and porters were to be made ready by the post station and the surrounding villages (sukego).

Original:

> 東海道にはおよそ２～３里（10km前後）ごとに宿場が設置され、幕府は各宿場に馬100匹と人足100人を毎日用意させました。 ... これは馬や人足は、宿場と周辺の村々（助郷）で用意すると決められているからです。

**This supports the entry's "many dozens of draft animals ... with their guards,
porters and drivers" as the real order of magnitude**, and supports the entry's
core idea that the requirement is a matter of SCALE fixed by the traffic the place
carries - 36 rising to 100 as the road got busier.

### And a hundred was routinely not enough - the overflow ran out to ten ri

*Nihon daihyakka zensho (Nipponica)*, article 助郷 by Maruyama Yasunari 丸山雍成, via
Kotobank, <https://kotobank.jp/word/%E5%8A%A9%E9%83%B7>:

English translation (mine):

> In the Edo period, the villages in the neighborhood of a highway post station that supplied men and horses supplementarily when the station's permanently kept men and horses alone were insufficient for the relay; or the levy or system itself.

Original:

> 江戸時代、街道宿駅の常備人馬だけでは継ぎ送りに支障をきたす場合、補助的に人馬を提供する宿駅近傍の郷村、またはその課役・制度をいう。

Same article, on the 1694 settlement and on the burden running away:

English translation (mine):

> In 1694 (Genroku 7) the shogunate newly laid down the sukego system ... designating the villages in the neighborhood of each post station as attached sukego, and setting the men-and-horses duty at 2 men and 2 horses per 100 koku of assessed yield. ... The Genroku-period standard for the men-and-horses burden acted as no brake at all, and by the late Edo period it had reached several hundred times that.

Original:

> 幕府は1694年（元禄7）新たに助郷制を画定したが、それは従来の助郷が封境・国郡を限界としたのを改めて、各宿駅近傍の村々を付属助郷に指定し、高100石につき2人・2疋(ひき)の人馬役負担とした。
> 元禄(げんろく)度の人馬負担基準はなんら歯止めとならず、江戸後期にはその数百倍に達した。

*Britannica kokusai daihyakka jiten* 小項目事典, article 助郷, same page, for the
catchment:

English translation (mine):

> At first the extent of the sukego villages was 2 to 3 ri around the station, but it was gradually widened to more than 10 ri, and when the supply of men and horses was impossible it was commuted into money, becoming a kind of tax.

Original:

> 最初，助郷村の範囲は宿の周囲2～3里であったが，次第に10里以上にも拡大され，人馬提供が不可能の場合，金銭で代納し，一種の租税となった。

**This is the strongest thing found for the entry's underlying idea.** A post
station keeping a hundred horses standing was still regularly swamped, and the
answer was to draw animals from a ring of villages that started at 2-3 ri and grew
past 10 ri. The bottleneck the entry describes - a settlement that cannot absorb
what arrives at it - is documented, and the historical solution was to widen the
catchment rather than to enlarge the yard.

### Oxen did carry goods

Michael Thomas Abele, *Peasants, skinners, and dead cattle: the transformation of
rural society in western Japan, 1600-1890*, PhD dissertation, University of Illinois
at Urbana-Champaign, 2018, p. 177,
<https://www.ideals.illinois.edu/items/107042>
(PDF: <https://www.ideals.illinois.edu/items/107042/bitstreams/349107/data.pdf>):

> During the off season, the kawata rented their animals out to cattle drivers, who used the oxen to transport goods for local peasants (niushi).

(a footnote reference number stands here in the original, between the two sentences)

> The cattle owners themselves did not handle these animals, but assigned this work to subordinates, usually a younger male in their household. Kawata cattle drivers collected fees from their customers, ensuring the cattle of the village remained profitable even when not working in agriculture.

This carries the entry's "oxen and packhorses" against a reader who thinks Japanese
overland freight was horses only. **Its limit**: this is the Kinai, the herd is
small (Abele counts "roughly fourteen kawata households in Saraike held draft
animals" and "never more than fifteen"), and it is local hire, not a caravan.

### What was NOT found

**Nothing supports the contrast itself** - "A town inn can absorb that into a small
stable yard and a city cannot." No source was found that compares the stabling a
town inn holds with what a city needs, or that puts a number on either. The
Tokaido evidence above is all about POST STATIONS, which are towns, and it says
they too failed to absorb the load; it does not say a city succeeded where a town
failed. As written, the sentence should stay labeled a guess, or be rewritten to
the thing the record does say: that even a hundred horses standing at a station was
not enough, and the overflow was pushed out into a ring of villages up to ten ri
deep. Searched: `宿場 人馬 常備 百人百疋 東海道 伝馬 問屋場` (Yahoo Japan, hit, gave the
three sources above) and `助郷 制度 宿場 人馬 不足 近隣 村 補う` (Yahoo Japan, returned
a 3.7 KB throttle page; answered instead from Kotobank's 助郷 article, used above).

---

## 5. `urban-features.html` fn-85 - the outcast hamlet at the village edge

**Verdict: CITED.** This is the one that had "no work named" and it turns out to be
well documented, with an open-access monograph-length treatment.

### A separate residential cluster inside the same village territory - not a fixed distance

Michael Thomas Abele, *Peasants, skinners, and dead cattle: the transformation of
rural society in western Japan, 1600-1890*, PhD dissertation, University of Illinois
at Urbana-Champaign, 2018,
<https://www.ideals.illinois.edu/items/107042>. Abele's case study is Saraike
village, Kawachi province (now Matsubara, Osaka), which held both a peasant and a
*kawata* community.

> Though the kawata lived within the territory of Saraike, there was a clear separation between their residential plots and those of the peasants, while the Saraike peasants were geographically much closer to Higashi-Dai and Mukai villages.

> Though they were in the same village territory, these were separate communities (Figure 4).

> Figure 4: Saraike Village in 1690. The Circle on the left is the peasant village, and the kawata are on the right. In reality, the kawata community was much larger, and the peasant community much smaller, than is depicted here.

**This supports the entry's sentence almost exactly, and improves it.** The outcast
settlement is a distinct residential cluster with "a clear separation" from the
peasant plots, standing in the same village territory - so it is at the village's
edge rather than a separate place. And the second clause is the direct support for
"rather than at any fixed distance out": the peasants of Saraike were physically
NEARER to two OTHER villages than to the *kawata* of their own. The gap is a local
arrangement, not a standard.

Abele also gives the case where the cluster sits on an administrative boundary:

> Ōji village was located in Shinoda-gō, in Izumi District, Izumi Province. In the late sixteenth century, the kawata community that would become Minami-Ōji Village lived within the boundaries of Ōji village, on the border between Shinoda-gō and Kami-Izumi-gō.

> By the late seventeenth century “Minami-Ōji” (South-Ōji) was appearing on shogunal registers as a separate village. The kawata even had their own headman (shōya) and village elder (toshiyori). However, the residential plots of the kawata still lay within the boundaries of Ōji Village, placing them under the jurisdiction of the Ōji headman.

and, on the QUALITY of the ground the cluster stood on - which matters to a map
deciding where to put it:

> As with other kawata communities, the land that the Ōji Village kawata initially occupied was of poor quality, reflecting their status as relatively recent arrivals.

and, in his own summary of the chapter, the general rule behind it:

> the same process in the early Tokugawa period, and explain why most kawata communities were never recognized as independent villages.

### The stream half

Abele, on the status name itself:

> That status was not always “kawata,” but could also be “kawara” or kawaramono; that is, “people of the riverbank.”

and *Yamakawa Nihonshi shojiten* 山川 日本史小辞典 改訂新版, article 穢多, via Kotobank,
<https://kotobank.jp/word/%E7%A9%A2%E5%A4%9A>:

English translation (mine, from the Japanese):

> In the later medieval period, through the differentiation of the hinin-yado, groups of kawaramono specializing in the disposal of dead cattle and horses and in the carrying out of punishments were formed. These kawaramono connect to the early modern eta status. ... Generally they constituted a branch village (edamura) of a main village (honmura) made up of peasants, and carried out the disposal of dead cattle and horses within the territories called kusaba, dannaba and shokuba that spread around it.

Original:

> 中世後期には非人宿の分化により，斃牛馬処理や行刑を専業とする河原者(かわらもの)の集団が形成されていく。この河原者が近世の穢多身分につながった。 ... 一般的には百姓からなる本村の枝村を構成し，その周辺に展開する草場・旦那場・職場などとよばれる縄張り(権域)で斃牛馬処理を行った。

**The "across its stream" half is supported obliquely, not directly.** The medieval
antecedent is literally "people of the riverbank", which is where marginal untaxed
ground was, and 枝村 / *edamura* - "branch village of a main village" - is exactly
the relation the entry's map draws. I found no source stating that the Tokugawa
outcast hamlet characteristically stood across a stream from the main village. **If
the entry wants to keep "or across its stream" it should rest it on the kawaramono
etymology and say so**, which the two quotes above will carry; the "branch village
of the main village" formulation is the better-evidenced half.

### The residence restriction itself

*Seisenban Nihon kokugo daijiten* 精選版 日本国語大辞典, article 穢多, sense 2, same
Kotobank page:

English translation (mine):

> Their places of residence too were collectively isolated and set apart in inferior areas, and down to their children and grandchildren they could not leave that status.

Original:

> 居住地も劣悪な地域に集団的に隔離疎外され、子々孫々までその身分から離れることができなかった。

and *Digital daijisen* デジタル大辞泉, same page:

English translation (mine):

> In the Edo period, together with the people called hinin, they were placed below the shi-no-ko-sho and suffered unjust discrimination, their places of residence among other things being restricted.

Original:

> 江戸時代には非人とよばれた人々とともに士農工商の下におかれ、居住地も制限されるなど、不当な差別を受けた。

This carries the entry's framing of the standoff as "a zoning statement about who
lives beside whom": the restriction the record attests is on WHERE, not on how far.

**Nothing was found giving a distance in any unit**, so the entry's 60 ft remains
correctly labeled a calibration against the drawn maps rather than a finding. The
record positively supports that labeling - Abele's Saraike, where the peasant
village was closer to two neighbors than to its own *kawata*, is a case in which no
fixed collar existed at all.

---

## 6. `cities/hinterland.html` fn-11 - the size of an urban kitchen-garden bed

**Verdict: CITED, and it changes the number.** This note "never got a search of its
own"; the record is not silent. A sixth-century Chinese agricultural treatise gives
the bed, gives the reason for the size, and gives the size of the market garden
outside a city wall as well.

### The source

Jia Sixie 賈思勰, *Qimin yaoshu* 齊民要術 (Essential techniques for the common people),
Northern Wei, c. 540, juan 3, chapter 17 "Planting kui [mallow]" 種葵第十七, full text
at Chinese Wikisource,
<https://zh.wikisource.org/wiki/%E9%BD%8A%E6%B0%91%E8%A6%81%E8%A1%93/%E5%8D%B7%E7%AC%AC%E4%B8%89>.
(The main text is given first; Jia Sixie's own interlinear notes are in {{*| |}} in
the wikitext and are marked "author's note" below.)

### The bed, and why it is that size

English translation (mine, from the Chinese):

> In spring one must plant in beds and water them. [author's note: In spring there is much wind and drought, so without beds it cannot be done. Moreover with beds the ground is economized and the vegetables are many; one bed supplies one mouth.] The bed is two paces long and one pace wide. [author's note: If it is larger the water is hard to spread evenly, and also one does not want a person's foot to go into it.]

Original Chinese, as the checker's anchor:

> 春必畦種、水澆。{{*|春多風、旱，非畦不得。且畦者地省而菜多，一畦供一口。}}畦長兩步，廣一步。{{*|大則水難均，又不用人足入。}}

and the generalization a few lines later:

English translation (mine):

> For all things planted in beds, the making of the bed is in every case as in the method for planting kui; I shall not set it out again at tiresome length.

Original:

> 凡畦種之物，治畦皆如種葵法，不復條列煩文。

**This is the exact answer to "the size of an urban kitchen-garden bed", with its
reason, and the reason is the one the entry already guessed at.** The entry says "A
kitchen garden is hand-worked ground, so its parcels are smaller than a grain
field's"; Jia Sixie says the bed is kept small because beyond a certain size water
cannot be spread evenly over it by hand and because nobody should have to step into
it. And the note "one bed supplies one mouth" gives the unit a demographic meaning
a map can use: beds per household, not an arbitrary tiling.

**The number, and the caution on it.** The text gives 2 *bu* 步 by 1 *bu*. Converting
a Northern Wei *bu* needs a metrology source I did not read, and the two common
reckonings (a *bu* of 5 or of 6 *chi*, with a *chi* of roughly 28-30 cm) put the bed
somewhere in the region of 1.4-1.8 m wide by 2.8-3.6 m long, i.e. very roughly 5-6 ft
by 9-12 ft. **I am flagging that conversion as mine and unverified** - the figure
that is actually sourced is "two paces by one pace". **Before this reaches a map it
needs a metrology citation**, which is a short pass at a history of Chinese weights
and measures.

**What this does to the entry's 55 ft.** A bed of about 5 ft by 10 ft is not 55 ft
across; 55 ft is roughly five to eleven beds wide. So the entry's 55 ft figure is
not a BED, it is a garden PARCEL made of many beds, and the word "beds" in "a
vegetable tract's beds are the SMALLEST dry parcels on the map" is doing the wrong
work. The entry can now say something better than a guess: that the hand-worked
bed itself is a documented ~2 x 1 paces sized so the waterer's foot stays out of it,
and that the drawn parcel is a block of them.

### And the treatise sizes the market garden outside the city wall

The same chapter, on the winter crop, describes a commercial vegetable garden sited
at a city - which is the entry's actual subject, "Does a city farm inside its walls?"

English translation (mine):

> Also, the method for winter-planting kui: near a prefectural or commandery town or city where there is a market, thirty mu of good land backing onto the city wall; after taking the vegetables in the ninth month, plow it at once, and by the middle of the tenth month get three passes done. ... In the middle of it, sink ten wells along its length. [author's note: The wells must correspond to one another; set at a skew angle they waste the ground. If the shape of the ground is narrow and long, the wells must be made in a single row; if the shape of the ground is a true square, making two or three rows is not objectionable either.] For each well make a well-sweep and a windlass. [author's note: For a deep well use a windlass, for a shallow well a well-sweep.] A willow bucket, made to take one shi.

Original:

> 又冬種葵法：近州郡都邑有市之處，負郭良田三十畝，九月收菜後卽耕，至十月半，令得三遍。每耕卽勞，以鐵齒杷耬去陳根，使地極熟，令如麻地。於中逐長穿井十口。{{*|井必相當，斜角則妨地。地形狹長者，井必作一行；地形正方者，作兩三行亦不嫌也。}}井別作桔橰、轆轤。{{*|井深用轆轤，井淺用桔橰。}}柳鑵，令受一石。

**This is worth more to the map than the bed figure.** It gives, for a garden
serving a city with a market: the siting (*fu guo* 負郭, backing onto the city wall),
the extent (30 *mu* of good land), the well density (ten wells in that tract), and
the rule for laying the wells out by the shape of the plot - one row if the ground
is long and narrow, two or three if it is square, and never skew, because a skew
line wastes ground. A map drawing a city vegetable tract has a sourced layout rule
here, including how many wells to put in it and how to line them up. The 30 *mu*
figure carries the same conversion caution as the bed.


---

## What is still open after this pass

1. **fn-62, the Xuxiebian site name.** FOR THE GM. A named excavated Sichuan
   smelting-and-fining site is asserted, and it appears in neither of the two
   Wagner works readable in full (his Han metallurgy article, and the free Chinese
   translation of *The state and the iron industry in Han China*, searched
   character by character). The Han claim itself is safe on Wagner's own hedged
   wording plus the Hongdaoyuan tomb relief; the site name is not. Either the GM
   knows where it came from, or it should go.
2. **fn-14, the comparison itself.** The three terms are now each citable. That the
   three of them are "the nearest East Asian equivalents of a postern" is a
   comparison no source makes, and it should stay labeled as the project's own. The
   *umon* sources do, however, describe a concealed gate built to be filled in and
   used as the lord's escape route, which is close enough to a sally port's
   function that the entry could say so and footnote it.
3. **fn-14, a better source for the *umon*.** The two used are a curated commercial
   glossary and a castle-enthusiast site - publicly readable, mutually consistent,
   and tertiary. Kotobank has no entry for it. One more pass at the Agency for
   Cultural Affairs' designated-property database and the city of Takamatsu (which
   holds the famous surviving example) would likely upgrade it.
4. **fn-17, a sumptuary text.** The *nagayamon* material shows the gate followed
   rank and office. A direct prohibition on a townsman's gate or wall, if one
   exists, would be in the shogunal edict collections (*Ofuregaki kanpo shusei*) or
   a domain code, and this pass did not reach them - the Yahoo Japan query for it
   came back throttled and was not retried.
5. **fn-25, the contrast.** Nothing found supports "a town inn can absorb that into
   a small stable yard and a city cannot", and the Tokaido evidence cuts slightly
   against it, since the post STATIONS are towns and the sources say they too were
   swamped. The sentence should be rewritten to what the record does say or kept
   labeled a guess.
6. **fn-11, the metrology.** The *Qimin yaoshu* figures are in *bu* and *mu*.
   Turning "two paces by one pace" and "thirty mu" into feet needs a history of
   Chinese weights and measures that this pass did not read, and my arithmetic in
   that section is flagged as unverified. That is a short, well-defined next search.

## One thing worth flagging beyond the six

The Suzhou Panmen page reached for fn-14's *shuimen* also carries measured
dimensions for a **wengcheng**, which is the FIRST `[HERE]` in the same
`cities/defenses.html` paragraph and is currently marked "this rests on general
reading; no source is cited". That footnote was not in this batch, but it is now
answerable from a source already fetched and quoted here, and the same page shows
that this wengcheng is 平面略成方形 - roughly square in plan - which the entry's
word "urn-shaped" does not survive.
