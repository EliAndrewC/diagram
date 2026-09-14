# Quote check: `cities/river-cities.html`, `cities/defenses.html`, `towns.html` (feature 242 footnotes)

Files read: `/diagram/.clones/diagram-research/.claude/skills/diagram/research/cities/river-cities.html` + `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/cities/river-cities.html`; `.../research/cities/defenses.html` + `.../research/citations/cities/defenses.html`; `.../research/towns.html` + `.../research/citations/towns.html`.

Scope checked: river-cities fn-6, 17, 20-41; defenses fn-28-46; towns fn-27, 28, 29, 31, 32-45. 61 notes (51 citations, 10 absence notes). 54 distinct URLs, each fetched once by its own address. **No host refused.**

---

## FIRST: the findings that stop a footnote landing as a citation

**river-cities fn-20** - `shanghai-xiancheng-zhwiki` - READABLE - **NOT-ON-PAGE** - support unassessable
Link: `https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7%E8%80%81%E5%9F%8E%E5%8E%A2` (decodes to 上海老城厢). The fetch of that page returns neither the quoted original 「护城河与水门相通，以利航运，并通黄浦江潮汐，藉以为城内居民供应新鲜水源及排泄污水」 nor anything on the moat, the water gates or fresh-water supply. Note: the registry/works line names the article **上海县城**, while the link goes to **上海老城厢** - the passage may live on the other article, so this may be a mis-pointed link rather than a misquote. The assertion it carries ("Shanghai's county-seat moat connected to the Huangpu's tides") has no readable page at this address.

**river-cities fn-37** - `shanghai-xiancheng-zhwiki` - READABLE - **NOT-ON-PAGE** - support unassessable
Same page, same result: 「乾隆十八年（1753年），知县李希舜疏浚城濠，使舟楫得以同行」 is not on it. The assertion ("A silted moat is a maintenance failure rather than a hydraulic one") therefore rests on nothing readable at the linked address.

**river-cities fn-27** (second source) - `kotobank-takasebune` - READABLE - **NOT-ON-PAGE** - PARTIAL
The quoted 「利根川には長さが約27メートルという大型の高瀬舟があった。」 is not on the page. What the page says on the Tone is 「京・伏見間の高瀬川就航のものは箱造りの十五石積で小型を代表し、利根川水系の二百石積前後のものはきわめて長大で」 - the 200-koku Tone boat is there, **but no length in meters**. So the research page's "some 89 ft on the Tone" (= 27 m) is unsupported, while "73 ft in an Edo technical record" is verbatim-supported by the takasebune page (below). The note also prints the Tone sentence twice (quote and gloss).

**defenses fn-36, fn-37, fn-38** - `jah-song-military-cities` - public link, **NOT VERIFIABLE BY THIS TOOL**
`https://www.jgcm.ac.cn/jah/cn/article/pdf/preview/10.12329/20969368.2026.02011.pdf` served a 2.9 MB PDF as binary (FlateDecode streams); no text layer reached the reader. Not a paywall and not a refusal - the passages 「马面，旧制六十步一座…两边直觑城脚」, 「间隔上，《武经总要》所记载的马面间隔…」 and 「此时的"瓮城"多在边陲城池中使用…」 could not be checked either way. Reported as unverifiable, not as NOT-ON-PAGE.

**river-cities fn-39 - MISPLACED** - `xiangyang-cheng-zhwiki` - READABLE - VERBATIM - **DOES-NOT-SUPPORT**
The reference sits on *"the 1642 flood alone killing ~300k of 378k."* The note's quotes are Xiangyang's 「三面环水，一面靠山」 and 「汉水中游南岸」 - about a city on one bank of the Han, nothing about Kaifeng or a death toll. Both quotes are verbatim on the page and the translations are faithful; the note's own gloss ("the universal NEVER is this page's") shows it was written for the earlier assertion *"The trunk river NEVER runs through the walls"* / *"the city stands ON one bank"*, where it would SUPPORT.

**river-cities fn-31 - MISPLACED** - `matou-zhwiki` - READABLE - VERBATIM - **DOES-NOT-SUPPORT**
The reference sits on *"the kura standing directly behind the bank street"*; the quote 「碼頭又稱渡頭、渡口、埠頭，是一條由岸邊伸往水中的長堤，也可能只是一排由岸上伸入水中的樓梯」 is about the matou's two forms and says nothing of storehouses or a bank street. It would SUPPORT the same sentence's earlier clause (*"The Chinese matou is, in one of its two forms, a stepped landing"*), which currently carries no footnote. The page names no material and ranks neither form, exactly as the gloss says.

---

## `cities/river-cities.html`

```
fn-6  panmen-zhwiki          READABLE  VERBATIM (orig)  TRANSLATION-FAITHFUL  PARTIAL
      Page: 「水城门在陆门南侧，也有内外两重，纵深24米，前后分置水闸和木栅，两门之间有暗道通向城楼。」 - identical.
      Assertion is "a sluiced arch": the sluice and grating are in the quote, the ARCH is not
      (the page mentions an arch only of the separate 吴门桥 bridge). The note discloses it.
fn-17 xian-wall-zhwiki + hori-jawiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  PARTIAL
      Both originals identical on their pages (hori also carries the weir-sectioned moat,
      水戸違い, the gloss refers to). Not in either quote: "kept full by the river's own stage
      far more than it was ever flushed through" - the comparison, disclosed as this page's.
fn-20 shanghai-xiancheng-zhwiki  READABLE  NOT-ON-PAGE  (see above)
fn-21 ABSENCE note (searched 2026-09-14, Pan Gate / 苏州城墙 / 高瀬川) - nothing checked
fn-22 ABSENCE note (searched 2026-09-14, 河岸 / kotobank 河岸) - nothing checked
fn-23 gangi-kowan-jawiki   READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
fn-24 gangi-kowan-jawiki   READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      "a few weeks" and the two failure states are not in the quote; the note says so.
fn-25 floating-dock-enwiki READABLE  VERBATIM  SUPPORTS
      2nd quote is a prefix cut at a comma; the page continues "…, this type of platform can
      self-adjust to variations in water levels" - the clause that carries the assertion's own
      point ("a modern marina's answer to the same level problem") is just outside the quote.
fn-26 kashi-jawiki         READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      Tax rice supported; "seasonal" is on no page read, as the note states.
fn-27 takasebune-jawiki    READABLE  VERBATIM (excerpt)  TRANSLATION-FAITHFUL  PARTIAL
      Page: 「敷長12尋1尺（約22.20m）、横胴敷1丈3寸（約3.12m）、敷板厚1寸6分…」 - the quoted span is
      character-identical as a prefix. The Heian 約9.39m the gloss cites is also on the page.
      kotobank half: NOT-ON-PAGE (above).
fn-28 pier-enwiki          READABLE  VERBATIM  PARTIAL
      Reach supported; the page's cause is tidal range and it says nothing of a shelving river
      bank or a pier count by bank steepness - as the gloss states.
fn-29 gangi-hiroshima-jawiki READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
fn-30 xunqi-zhwiki         READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      Seasonal rise supported; the page gives no magnitude, so "many feet" is uncited (disclosed).
fn-31 matou-zhwiki         READABLE  VERBATIM  DOES-NOT-SUPPORT as placed (above)
fn-32 gangi-hiroshima-jawiki READABLE  VERBATIM (excerpt)  TRANSLATION-DIFFERS  PARTIAL
      Page: 「雁木の名のとおりかつては木材で造られていたが、水に浸かるため腐りやすいことから、江戸初期に
      石材が用いられるようになったと考えられている」. The quoted span is identical but stops one clause
      short: the page HEDGES ("…と考えられている", it is thought), and the English - "stone came to be
      used from the early Edo period" - asserts it flat. Accept instead: "…, and from the early Edo
      period stone is thought to have come to be used". Quote (b) 「川の斜面に造られた階段状の港湾施設
      および護岸」 is verbatim.
fn-33 pier-enwiki          READABLE  VERBATIM x2  PARTIAL
      Working/pleasure distinction supported (the page even has holidaymakers "promenade"); the
      universal "Nothing in a pre-modern working river port is built for that" is the page's own.
fn-34 water-gate-enwiki    READABLE  VERBATIM  SUPPORTS  (page carries premodern examples)
fn-35 ABSENCE note (searched 2026-09-14) - nothing checked
fn-36 kotobank-hori        READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      The 2nd sense is identical; the 1st sense 「土地を掘って水を通した所。掘り割り。」 is a channel that
      passes water, which the note discloses. Stage-vs-throughput is this page's reasoning.
fn-37 shanghai-xiancheng-zhwiki  READABLE  NOT-ON-PAGE (above)
fn-38 ABSENCE note (searched 2026-09-14) - nothing checked
fn-39 xiangyang-cheng-zhwiki READABLE  VERBATIM x2  DOES-NOT-SUPPORT as placed (above)
fn-40 pingyao-enwiki + xiangyang-cheng-zhwiki  READABLE  VERBATIM x3  PARTIAL
      All three identical (Pingyao's east bank of the Fen; the 4 m moat; Xiangyang's 250 m).
      Not in any quote: "tapping the river upstream and returning downstream so the current
      flushes it", which is the load-bearing half of the sentence the reference closes.
fn-41 shiliupu-zhwiki      READABLE  VERBATIM x2  PARTIAL
      Page: 「十六铺所在的区域位于县城的宝带门（小东门）与黄浦江之间」 (the quote is the identical tail) and
      the sand-junk sentence identical. The page has NO warehouses (仓库) - the assertion's
      "jetties, warehouses, market" keeps that on the page's silence, as the gloss admits; the
      48-wharf count is 1947, as stated.
```

## `cities/defenses.html`

```
fn-28 lijin-zhwiki + chaoguan-zhwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
      Both identical; the lijin page does not mention 鈔關, so "neither page names the other" holds.
fn-29 ditai-zhwiki   READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      Page: 「敌台正面的凸出部分、以及侧面的开窗，便于从两翼射击攻城人员。」 - identical. It carries
      TWO-FLANK FIRE and nothing about SPACING, while the assertion is "Spacing the towers a
      bowshot apart is the design purpose the record gives the projecting wall tower." The
      bowshot spacing lives in the Xi'an quote (fn-35/fn-12), not here. The page also shows
      round and semicircular forms, as the record says elsewhere.
fn-30 mengxi-bitan-wikisource  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
fn-31 pingyao-chengqiang-zhwiki  READABLE  DIFFERS  TRANSLATION-FAITHFUL  SUPPORTS
      The note quotes TRADITIONAL characters 「每隔50米有一馬面牆,上面有敌楼1座，用以減少守城方的射擊
      死角。馬面牆共有72座」, but the footnote's own link is the zh-hans page, which reads
      「每隔50米有一马面墙,上面有敌楼1座，用以减少守城方的射击死角。」 / 「马面墙共有72座」 (马面墙, 减少,
      射击). A reader opening the linked page cannot find the string as written. The 6.4 km
      perimeter the assertion uses is on the page (「周长6.4公里」).
fn-32 ABSENCE note (searched 2026-09-14, ten bow pages) - nothing checked
fn-33 tang-changan-zhwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  PARTIAL
      Four-sided ward wall + guarded gates and curfew supported; the page does NOT describe where
      a ward wall met the city wall (confirmed), which is the assertion's actual subject - disclosed.
fn-34 fortified-tower-enwiki + castle-enwiki  READABLE  VERBATIM x2  PARTIAL
      Europe's reason supported. "reached separately", "not a European signature" and "a round
      corner does not by itself say an older piece of wall" are inferences, disclosed.
fn-35 mengxi-bitan-wikisource + xian-wall-zhwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
fn-36 jah-song-military-cities  public link, NOT VERIFIABLE BY THIS TOOL (binary PDF)
fn-37 jah-song-military-cities  public link, NOT VERIFIABLE BY THIS TOOL (binary PDF)
fn-38 jah-song-military-cities  public link, NOT VERIFIABLE BY THIS TOOL (binary PDF)
fn-39 hakone-seki-jawiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
      Both identical. The page indeed says nothing about where the two stations stood relative
      to each other or the road - which is what fn-5/8/11 record as absent.
fn-40 city-gate-enwiki + defensive-wall-enwiki  READABLE  VERBATIM x2  PARTIAL
      Controlled access and tolls at the gates supported; the page never mentions single file
      (confirmed), and the note says "forced single-file" is this page's.
fn-41 ABSENCE note (searched 2026-09-14) - nothing checked
fn-42 ABSENCE note (searched 2026-09-14) - nothing checked
fn-43 xian-wall-zhwiki  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      One measured 6 m tunnel; the 13-23 ft BAND is this page's generalization and nothing read
      is as narrow as 13 ft - disclosed in the note.
fn-44 ABSENCE note (searched 2026-09-14) - nothing checked
fn-45 chinese-city-wall-enwiki  READABLE  VERBATIM  PARTIAL
      The enclosed excess ground supported; the DRILL GROUND and sheltering the countryside are
      this page's, the source's reasons being growth capacity and timber/farmland - disclosed.
fn-46 wujing-zongyao-wikisource + chengchi-zhwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  PARTIAL
      「作四門，二開二閉」 is a verbatim excerpt of 「如築於閑時，須稍寬闊，作四門，二開二閉。」; the gate
      counts identical. "every opening is a place the wall has to be held twice over" is the
      page's reasoning, disclosed.
```

## `towns.html`

```
fn-27 kaogongji-wikisource + chengchi-zhwiki + neixiang-xianya-zhwiki
      READABLE  VERBATIM x3  TRANSLATION-FAITHFUL  PARTIAL
      All three identical (the Kaogongji span is an excerpt of a longer run continuing
      「左祖右社，前…朝後市，市朝一夫。」; neixiang reproduces the page's own curly quotes).
      The assertion's core - an avenue running from the gate STRAIGHT to the yamen - is in no
      quote, and the note says so.
fn-28 ABSENCE note (searched 2026-09-14, 定期市/六斎市/集市) - nothing checked
fn-29 kichinyado-jawiki VERBATIM + kichinyado-kotobank DIFFERS  TRANSLATION-FAITHFUL  SUPPORTS
      kotobank reads 「屋根代として1日1人24文，布団借用者は別に16～24文を支払った」 with the FULLWIDTH
      LATIN comma ，; this note prints the ideographic 、 (fn-12, out of scope, prints ，
      correctly off the same page). One character.
fn-31 jishi-zhwiki  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      The teidian inn-and-warehouse supported; the page mentions no stable, no open ground and
      no trade route (confirmed) - which the gloss states.
fn-32 ABSENCE note (searched 2026-09-14, Windbreak / 防風林) - nothing checked
fn-33 chengchi-zhwiki + chinese-city-wall-enwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
      Defect, not a verdict: the Suzhou sentence is printed twice in the note - as the quote and
      again in the trailing "(with 「…」)".
fn-34 yashikirin-jawiki  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
fn-35 chinese-city-wall-enwiki  READABLE  VERBATIM  SUPPORTS
      Confirmed: the page prices no wall by length anywhere, which is what the note claims.
fn-36 machiya-shoka-jawiki  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      Frontage-as-wealth supported. The assertion that the poor "sit in the deep cores of the
      blocks" is CONTRADICTED by the page, which puts the 裏長屋 on the shop-house's own plot
      (「裏長屋は表店の主人が大家となり、店子に貸し出される借家である。」, and one or two rows by
      frontage) - the note discloses this.
      Marking defect: the gloss's 「the uranagaya was a rented house of which the master of the
      omotedana was the landlord」 is the project's English with NO "translated from the Japanese"
      marking and no original beside it.
fn-37 kotobank-uradana  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      The back-street row house supported; the lane-trimming rule it closes is a drawing decision.
      Same marking defect: 「petty traders, artisans, day laborers」 is unmarked English for the
      page's 「小商人・職人・日雇いなど下層庶民」.
fn-38 caoshi-zhwiki + lifang-zhwiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  PARTIAL
      Both identical. But the assertion is "late arrivals who find THE GATE shut at dusk", and
      the lifang quote is about 坊門 - the WARD gates opened and closed by the street drum, not
      the city gate. The note glosses only "the late arrival stranded outside is this page's
      inference"; the ward-for-city-gate substitution is not disclosed.
fn-39 kotobank-hinomi-yagura + jishinban-jawiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
      Main quotes identical (the kotobank sentence ends 。 on the page). UNCONFIRMED: the gloss's
      bell quote 「櫓には半鐘をつるし」 - the reader both asserted it appears and gave the page's
      wording as 「櫓上には半鐘が設置されており」. The kotobank page carries two reference works, so
      this may be an entry mix-up; worth one re-read before it is trusted.
fn-40 edo-no-kaji-jawiki  READABLE  VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      The packed core supported; "the rampart… traps the blaze inside with the town" is on no
      page read, as the note states.
fn-41 kotobank-miyaji-shibai DIFFERS + edo-sanza-jawiki VERBATIM  PARTIAL
      Note: 「江戸時代、臨時に許可を受けて、社寺の境内で小屋がけなどして興行した芝居」.
      Page (精選版 日本国語大辞典 section): 「江戸時代に、臨時に許可を受けて寺社の境内で小屋がけなどして
      興行した芝居」 - 時代に vs 時代、, 寺社 vs 社寺, and no comma before it. The page carries two
      dictionaries, so the note may be quoting the Daijisen entry the fetch did not surface;
      either way the string as printed is not findable in the section read.
      edo-sanza's yagura-restriction sentence is identical (屋根 as printed).
fn-42 edo-sanza-jawiki + shibaigoya-jawiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  SUPPORTS
      Both identical (大阪, 屋根 as printed). Defect: the shibaigoya sentence is printed twice in
      the note, as quote and again in the gloss.
fn-43 okabe-hatago-jawiki + shukuba-jawiki  READABLE  VERBATIM x2  TRANSLATION-FAITHFUL  PARTIAL
      Both identical. Confirmed: the okabe page mentions NO yard, stable, trough or grooms'
      quarters - so the stable-and-open-ground half of the assertion rests on nothing here,
      which the entry states and labels a guess.
fn-44 choninchi-jawiki DIFFERS + eta-jawiki VERBATIM  TRANSLATION-FAITHFUL  PARTIAL
      The choninchi quote prints 「…店を構える[ブルジョワ]階級である…」 - the square brackets are
      MediaWiki link markup, not characters the page shows; the page's visible text is
      「ブルジョワ階級」. Two characters the reader will not find.
      eta identical. The gap between merchants and laborers, and an outcast quarter in a TOWN
      (the page says a village's edge), are on no page read - disclosed.
fn-45 kotobank-omotedana  DIFFERS  TRANSLATION-FAITHFUL  PARTIAL
      Note: 「多くは地借・店借だが，裏店の民衆より一段高い層を象徴する呼称で，問屋・仲買商人層にほぼ相当する」.
      Page (山川 日本史小辞典 section): 「多くは地借・店借だが，裏店(うらだな)の民衆より一段高い階層を
      象徴する呼称」 - 階層 not 層, the reading (うらだな) present, and the 「で，問屋・仲買商人層に
      ほぼ相当する」 continuation not surfaced. Support: the page sorts by wealth and status; "the
      trades that need no frontage live where frontage is cheapest" is this page's mechanism,
      as the gloss says.
```

---

## Assertions with no footnote, by section

### `cities/river-cities.html`

**Most provincial cities sit on a river**
- "tapping the river upstream and returning downstream so the current flushes it" - no footnote of its own; fn-40, which closes the sentence, quotes only siting and moat width.
- spec 1: "the river IS the stronger defense on that flank" - a comparative claim about defense, footnoted nowhere on the page.
- spec 1: "the dead cross the river: the moat's water set-back leaves no dry landward fringe to put them on, so the funerary ground sits on the far bank, downstream of the city and clear of the bridge road" - siting of graves relative to water; no footnote and no cross-reference.
- spec 2: "a burial or cremation ground sits beside the farmland, never on a paddy body or on its ditches" - same class; presumably grounded on another page, but not pointed at from here.
- *Skipped as owing nothing*: the gate-post tangent and the map's stroke weights (drawing conventions); the two-patron-fortunes sentence (the GM's own notes, the documented canon exception).

**Which way does an offtake leave a river, and why?**
- "what the engineering literature appears to hold, on no page that could be read, is that a diversion draws its LEAST sediment at an intermediate angle rather than at the square, and that the often-quoted 90 to 120 degree rule for a headworks is measured from the WEIR's axis rather than from the river's own line" - two claims about engineering practice, disclosed in prose but carrying neither a footnote nor an absence note.
- *Skipped*: the 800 ft junction separation, the 22 and 10 degree tilts and the 10-degree inlet (measured on, or chosen for, this project's own drawings, and labeled a guess); the GM's 2026-07-24 ruling; "The near-square offtake therefore belongs to a distributary" (an inference from fn-15/fn-16).

**Does a city's canal open its own mouth on the river?**
- "the moat's downstream river junction is then the single navigation entrance" - the exclusivity is in neither fn-4 nor fn-7 (the entry it refers back to), and no footnote is attached here.
- *Skipped*: "a distinct mouth further downstream would have had to cross the moat's southern arc at grade" (geometry of this map).

**The wharf's working face**
- "The Chinese matou (碼頭) is, in one of its two forms, a stepped landing … set into a faced bank" - carries no footnote of its own; the note that would support it (fn-31) is attached to a later clause.
- "a port that also handles timber and stone wants at least one [pier]" - a claim about port practice, unfootnoted.
- *Skipped*: "its capacity is measured in feet of usable mooring, not in piers" and "a few hundred feet of faced bank moors four or five of the middling sort" (arithmetic on the quoted boat lengths); the stone band, coursing line, four treads and mooring posts (drawing conventions, so labeled).

### `cities/defenses.html`

**Does the city wall close a full ring - and why so few gates?**
- "weng is an urn and the name is the urn's" - a philological claim with no footnote (fn-19 beside it gives the square plan, not the etymology).
- "Setting the three of them against the European sally port as its nearest equivalents is this record's own comparison; no source makes it." - honestly labeled in prose, but it is a bare sentence with no absence note.

**What keeps the moat full?**
- "A wet ditch has to be fed, and a trickle cannot hold one full against seepage and evaporation: the channel that supplies a moat carries something like what the moat itself holds." - a physical claim; the Sources line says it "rests on this project's own reasoning about flow", but the sentence carries no footnote or absence note.

**Wall towers - the mamian system and bowshot ranges**
- spec 2: "a tower counts as reaching 36 ft past its recorded center, because an archer shoots from the bastion's parapet SPAN and not from a point" - the archery premise is unfootnoted.
- spec 2: "within 186 ft of a ward gate where a neighborhood fence meets the rampart, which is a manned chokepoint" - "manned" is unfootnoted.
- *Skipped*: "put towers a bowshot apart and every curtain point has two within a bowshot" (geometry); the three tier numbers, the 54 ft sampling, the 0.58-0.60 measured pairs and the 75-degree floor (this project's own calibration, and the spec says which figures are guesses).

**Why are the wall towers rectangular and never round?** - nothing unfootnoted; the Japanese *yagura* sentence carries its own absence note (fn-17).

**How far inside the wall does the patrol road run** - nothing unfootnoted; the follow-the-wall street carries an absence note (fn-18) and the 8% area cost is declared this project's own measurement.

**Where does a neighborhood fence stop** - nothing unfootnoted; the GM's 2026-07-27 words and the ink measurements are this project's own.

**How wide is the opening / Gate structures / Gate furniture** - nothing unfootnoted beyond what fn-41, 42 record as absent; the 105-135 ft seating and the 6-degree and 36 ft figures are declared unsourced in the spec's own text.

### `towns.html`

**Chinese towns were PLANNED** - nothing unfootnoted (every clause carries one; the axis is labeled a guess in the spec).

**Who lives in a town, and in how many houses?** - all counts are the GM's `budgets.md` (the documented canon exception); the three drawing conventions are labeled as such. Nothing owed.

**How is a town zoned** - nothing unfootnoted; "across a gap that is this page's own" is disclosed.

**The market-day flophouse**
- spec: "It is deliberately large, plain and barn-like - no awning, a long row of plain doorways - … it beds dozens on market eve." - the form and the capacity are claims about the building; no footnote.
- spec: "since the gate shuts at dusk and a peasant arriving late cannot get in at all" - the dusk closing has no footnote here (and where it is footnoted, fn-38, the source is about ward gates).

**Where does a caravan inn stand** - nothing unfootnoted; the trade-route premise and the cart yard are labeled this page's and a guess.

**Does a town keep a fire-watch tower?** - nothing unfootnoted; the fire-break claim carries its absence note (fn-23) and is labeled a guess.

**The gate market exists for TRAFFIC, not taxes**
- "the market-day chokepoint where the rural catchment trades" - the middle of the three named drivers, and the only one with no footnote (the first has fn-20, the third fn-38).
- *Skipped*: the tariff apparatus and the ~2,700 / ~14,400 counts (the GM's budget notes).

**A street is access infrastructure for the buildings it serves**
- "it is paved or worn into the ground by the foot traffic to and from them" - unfootnoted.
- "and a desire path forms only between real destinations" - unfootnoted (the record holds desire-path sources elsewhere; none is pointed at here).
- Observation rather than a missing footnote: the hutong sentence sets *"emerged as access routes lined by contiguous courtyard residences"* in quotation marks, and fn-14's own comment says those are not the page's words - my fetch confirms the page reads 「hutongs are alleys formed by lines of siheyuan…」 and 「Many neighbourhoods were formed by joining one siheyuan to another to form a hutong」. A quoted span that is a paraphrase.
- *Skipped*: the 450 ft avenue and the frontage-across-a-fence diagnosis (measured on this project's own map).

**A rampart's cost scales with its LENGTH**
- "its cost scales with its length" - disclosed in prose as "this page's reasoning; no page read prices a wall" (my fetch confirms it), but the clause carries no footnote or absence note.
- spec: "since a wall climbs or skirts a hill rather than leveling it" - unfootnoted.
- Observation: the spec-adjacent 「no empty ground」 in the finding uses the source-quotation brackets around this project's own phrase, which no source said.

**Why is the magistrate's manor drawn as a plain walled box / Where does it stand** - the GM's 2026-07-27 ruling and this project's calibration; nothing owed (fn-24 carries the southern fallback).

**How is a town farmstead laid out?**
- "because a farmer builds close to the ground they work (this page's reasoning)" - disclosed, no footnote or absence note.
- *Skipped*: the 14 ft error and the 44 ft house (this project's own measurement); the GM's 2026-07 direction.

**Which way does a shelter belt lie** - nothing unfootnoted; the bearing claim carries fn-32 (absence) and the two failed metrics are this project's own measurements.

**How big is a town's paddy plot?** - nothing unfootnoted; the 0.08 acre band is a cross-reference to `fields.html`, the comb grain a calibration, the flourish switch the GM's reading of the sheet and labeled a convention.

---

## Summary

| verdict | river-cities (24) | defenses (19) | towns (18) | total (61) |
|---|---|---|---|---|
| ABSENCE notes (nothing checked) | 4 | 4 | 2 | 10 |
| **Readability** READABLE | 20 | 12 | 16 | 48 |
| NOT-READABLE (paywall/login/refusal) | 0 | 0 | 0 | **0** |
| public link, NOT VERIFIABLE BY THIS TOOL (binary PDF) | 0 | 3 | 0 | 3 |
| **Quotation** VERBATIM | 17 | 11 | 12 | 40 |
| DIFFERS | 0 | 1 | 4 | 5 |
| NOT-ON-PAGE (whole note or one of its sources) | 3 | 0 | 0 | 3 |
| UNFETCHABLE / unverifiable | 0 | 3 | 0 | 3 |
| TRANSLATION-FAITHFUL (of the translated notes) | all but 1 | all | all | - |
| TRANSLATION-DIFFERS | 1 (fn-32) | 0 | 0 | 1 |
| **Support** SUPPORTS | 3 | 5 | 5 | 13 |
| PARTIAL | 13 | 7 | 11 | 31 |
| DOES-NOT-SUPPORT | 2 (misplaced) | 0 | 0 | 2 |
| unassessable (no readable passage) | 2 | 3 | 0 | 5 |

**Hosts that refused: none.** `jgcm.ac.cn` served the article as a 2.9 MB PDF with no reachable text layer (3 notes). One first attempt of mine at `zh.wikipedia.org/wiki/鈔關` used a mis-encoded path and 404'd; the footnote's own address was then fetched successfully and is fine.

**What the session has to decide on, shortest form:** three notes point at a page that does not carry their passage (river-cities fn-20, fn-37, and fn-27's kotobank half); three cannot be verified through this tool at all (defenses fn-36/37/38); two references are attached to the wrong assertion (river-cities fn-31, fn-39); five quotations do not match the linked page character for character (defenses fn-31's traditional-for-simplified, towns fn-29's comma, fn-41, fn-44's bracket markup, fn-45's 階層); one translation drops the source's hedge (river-cities fn-32); two glosses carry unmarked project English (towns fn-36, fn-37); and one support gap is undisclosed (towns fn-38 uses a ward-gate curfew for a city gate at dusk).