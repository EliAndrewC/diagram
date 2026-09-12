# Second pass, batch b2: Japanese and Chinese local sources (11 notes)

Reader: second-b2. Tooling: `curl` with a desktop browser user agent, `search.yahoo.co.jp`
fetched through curl, the MediaWiki API on `ja.wikipedia.org` and `zh.wikipedia.org`.

## Verdicts

| # | note | subject | verdict |
|---|---|---|---|
| 1 | `cities/fabric.html` fn-30 | jin'ya / daikansho town fire posture | **CITED** - bell, roof ladder, stored gear, water, fireproof kura all quoted; temple bell as alarm and the DAIKANSHO office itself still absent |
| 2 | `cities/government.html` fn-35 | compound at the crossing, bureaus on the avenues | **CITED** (compound in the middle of the city, Su Bai) / **STILL ABSENT** (offices lining the avenues) |
| 3 | `cities/government.html` fn-36 | wayside shrines between the temples | **PARTIAL** - several small shrines per town block CITED; the temple-quarter placement and the vermilion form still absent |
| 4 | `religion-and-death.html` fn-22 | ranked-torii spacing | Meiji Jingu **CITED**; Nagao **CONTRADICTED** (about 300 m, not 200 m); Kasuga 1.3 km **STILL ABSENT** |
| 5 | `religion-and-death.html` fn-38 | Chinese lamp-oil and incense income | **STILL ABSENT** + **FOR THE GM** (an unreadable PDF and two offline monographs); a readable page NARROWS it from sale to donation |
| 6 | `religion-and-death.html` fn-43 | funeral trades in a row by the burial ground | **STILL ABSENT** + **FOR THE GM** (Kinoshita 2001, offline) |
| 7 | `religion-and-death.html` fn-84 | pauper ossuary as a mound with one stupa | **CITED** (form); the position by a crematory outside the walls still absent |
| 8 | `towns.html` fn-24 | south as the formal and auspicious orientation | **CITED** for "formal" (Qing office regulation); "auspicious" not supported by the passage |
| 9 | `homesteads.html` fn-91 | area of a dooryard kitchen bed | **STILL ABSENT** + **FOR THE GM** (Kobayashi 2011, repository returns 406); and the entry's dooryard framing is contradicted |
| 10 | `homesteads.html` fn-92 | north-China courtyard house: animals along one wing | **CITED**, and the wing is NAMED (the east wing) |
| 11 | `vegetation.html` fn-87 | igune on north and west | **CITED** (Irie et al. 2020, quoting Nakajima 1963); the 1915 founding definition still absent and no longer needed |

**Headline for the dispatcher.** Six of the eleven moved: four to a quotable citation (1, 7, 8, 10,
plus 11 and half of 2 and 4), one to a CONTRADICTION that corrects a figure in the record (Nagao,
200 m -> about 300 m), and three to a named, identified document the GM could obtain (5, 6, 9). The
tooling claim in the brief held: every citation above came from a Japanese or Chinese page that the
earlier English passes could not reach - a prefectural cultural-resources page, a ward's
cultural-property listing, a MAFF repository PDF, a Jodo-shu dictionary, a Peking University
archaeologist's essay on a university site, a shrine's own access page, and the Japanese and Chinese
Wikipedias read through the MediaWiki API.

**One tooling failure to record.** Partway through this batch `search.yahoo.co.jp` began refusing
(returning only its own help and privacy links), and every other general engine was already
unusable from this host: DuckDuckGo lite served a CAPTCHA, Startpage a JavaScript challenge, Bing
returned results unrelated to the query, and Mojeek, goo and Ecosia returned nothing extractable.
What kept working was the MediaWiki API on both languages, direct `curl` of a known URL, and the
Japanese academic APIs - **J-STAGE** (`api.jstage.jst.go.jp/searchapi/do`), **CiNii**
(`cir.nii.ac.jp/opensearch/all?format=json` and `/crid/<id>.json`) and **NDL Search**
(`ndlsearch.ndl.go.jp/api/opensearch`). Those three found the exact paper for two of the three
remaining claims and are the tools the next pass should reach for FIRST, before any search engine.
`adeac.jp` - the full text of hundreds of Japanese municipal histories - refused to render for this
fetcher and is the highest-value host for a later pass to solve.

---

## 11. `vegetation.html` fn-87 - the igune stands on north and west, leaving south and east

**Verdict: CITED** (the substantive half - one-or-two-sided, north and west, south and east left
open). The 1915 founding definition itself is **STILL ABSENT**; see the note at the end of this
entry. The claim no longer needs it: a 2020 peer-reviewed paper states the rule directly and
attributes it to a 1963 monograph.

**Source.** Irie Akiteru, Harada Saki, Uchida Hitoshi, Takeuchi Masatoshi, "グリーンインフラとしての
屋敷林「居久根（いぐね）」の多面的機能性に関する研究" ("Research on the multifunctionality of the
homestead grove *igune* as green infrastructure"), 東京農業大学農学集報 (*Journal of Agricultural
Science, Tokyo University of Agriculture*) 65(1), pp. 9-18, June 2020. ISSN 0375-9202. Full text PDF
on the Ministry of Agriculture, Forestry and Fisheries' AgriKnowledge repository:

  https://agriknowledge.affrc.go.jp/RN/2010935166.pdf

Fetched 2026-09-12 with curl and a desktop user agent; read with `pdftotext`. The host serves the PDF
without restriction.

### Passage 1 - the two sides, and the two sides left open

VERBATIM (Japanese, from the paper's section on windbreak effect):

> (2) 居久根の防風効果について，仙台平野では冬季は主に北北西の風が多く強いことから，屋敷林が屋敷地に対して北または西側に形成され，南または東側を欠くことが多いとされている（中島 1963）。

*Translation from the Japanese, by this reader (Claude Opus 5); the original is quoted above as the
checker's anchor:*

> (2) As to the windbreak effect of the igune: because in the Sendai Plain the winter winds are
> mainly north-northwesterly and strong, the homestead grove is said to be formed on the north or
> the west side relative to the homestead plot, and often to lack the south or the east side
> (Nakajima 1963).

The work it attributes this to, from the paper's reference list: 中島道郎 (1963)『日本の屋敷林』
財団法人全国林業改良普及協会 - Nakajima Michiro, *Yashikirin of Japan*, National Forestry Extension
Association, 1963.

### Passage 2 - the grove built on north and west, maintained for centuries

VERBATIM (Japanese, from the paper's introduction):

> 奥羽山脈から吹きおろす冬の蔵王風（おろし）から屋敷を守るため北側と西側に幾重にも樹木が植えられ，数百年以上の間防風林として維持されてきたものである（七郷の今昔を記録する会 1993）。

*Translation from the Japanese, by this reader (Claude Opus 5); the original is quoted above as the
checker's anchor:*

> In order to protect the homestead from the winter Zao wind (*oroshi*) that blows down from the Ou
> Mountains, trees were planted in many layers on the north side and the west side, and have been
> maintained as a windbreak forest for more than several hundred years (Shichigo no konjaku o
> kiroku suru kai 1993).

**How it supports the claim.** fn-87 asserts (a) that the northeastern igune stands on the
homestead's north and west, the winter-monsoon-facing sides, and (b) that the rule leaves the south
and east for the entrance, the garden and the yard. Passage 1 states both halves - north or west,
often lacking south or east - and gives the reason the record gives (the north-northwesterly winter
wind), which is the reason fn-87 gives. Passage 2 independently states the north-and-west
construction and adds that these groves have been maintained for several hundred years, which is
what makes the rule usable for a premodern setting rather than a modern landscaping convention.

**Which half it does NOT support.** Passage 1 says "the north **or** the west side" (北または西側)
and "the south **or** the east side" (南または東側) - a disjunction. It supports "one or two
windward sides" exactly, and it supports "north and west" as the pair of sides in question; it does
not assert that every igune has both. That is the same shape fn-87's own heading takes ("it stands
on one or two windward sides"), so the entry is already narrow enough.

**A tension worth recording, not a contradiction.** The City of Sendai's own page on igune
conservation (https://www.city.sendai.jp/ryokuchihozen/kurashi/shizen/midori/hyakunen/hozen.html,
fetched 2026-09-12, updated 2023-12-07) defines the term with the trees **surrounding** the
homestead:

> 宮城県では,屋敷の周囲を取り囲むように植えられた樹木（屋敷林）を「居久根（いぐね）」と呼んでいます。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> In Miyagi Prefecture, trees planted so as to encircle the perimeter of the homestead (a homestead
> grove) are called *igune*.

This is a municipal definition of the WORD, not a survey of built form, and the same page says the
name settled in the mid-Edo period (「資料によれば,「居久根」という呼び方は江戸時代の中ごろには定着していたようです」-
"according to the sources, the name igune appears to have become established around the middle of
the Edo period"). The NPO Urban Design Works page for the Sendai Plain igune project
(https://www.udworks.net/igune/about-igune, fetched 2026-09-12) puts it the other way and agrees
with the paper:

> 主として屋敷の北西側に配置されスギ、ケヤキ、ハンノキ、クロマツの四種の高木が居久根の骨格。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> It is placed principally on the northwest side of the homestead, and four tall species - sugi,
> keyaki, hannoki and kuromatsu - are the skeleton of the igune.

So the encircling reading exists in a municipal blurb and the two-sided reading in the scholarly
work and in the practitioner project. The paper is the better source and is the one quoted above; if
the entry wants to acknowledge the other reading, the Sendai City sentence is the passage to hang it
on. Note that this is the opposite end of the change another reader found for the Izumo
*tsuijimatsu* (whole-house enclosure BEFORE Meiji, two-sided hook after): here the scholarly record
for the northeastern igune gives the two-sided form as the long-standing one and the encircling form
as the loose modern gloss.

### The 1915 definition - STILL ABSENT

The paper does not cite anything from 1915. Its literature review names 矢澤 1936 (scale, direction
and distribution), 辻村・伊藤 1937 (species, aspect and arrangement of Musashino Plateau homestead
groves, windbreak and insolation), 中島 1963, and 菊地 1999 - so the earliest work in its own chain
is 1936, not 1915.

Searches run for the founding definition, all through `search.yahoo.co.jp` via curl on 2026-09-12:

- `居久根 定義 北西 屋敷林 1915` - candidates: kikanchiiki.net/archives/6543 (a farming quarterly
  feature on communal igune maintenance, no definition or date); adaptation-platform.nies.go.jp
  (climate-adaptation page, modern framing); udworks.net (fetched, quoted above);
  city.sendai.jp (fetched, quoted above); 1073shoso.jp (Tonami *kainyo*, the WRONG region - Toyama,
  not the northeast); ja.wikipedia 屋敷林; agriknowledge PDF (fetched, quoted above).
- `屋敷林 定義 1915年 大正4年 北側 西側` - candidates: seikouminzoku.net/sub7-13.html (a folklore
  discussion-group page on laurel forest and homestead groves - not fetched, one host attempt was
  spent on the PDF that answered the claim and this page's title promises vegetation zones, not a
  definition's date); jumokukobe.blog.fc2.com (a tree-society blog); forest-tokyo.org;
  yashikirin.net (Tokyo homestead-grove network). None is a 1915 publication and none was reported
  by the search snippets as quoting one.

**Recommendation.** Drop the 1915 second-hand definition from the entry entirely and hang the rule
on the Irie et al. passage, which states it directly, attributes it to a named monograph, and is
readable by any reader who clicks the link. The sentence "the definition that founded the term is
reported to restrict the homestead grove to those same two sides" is then not needed and the
footnote stops resting on a work nobody has read.

---

## 1. `cities/fabric.html` fn-30 - the jin'ya / daikansho town's fire posture

**Verdict: CITED for most of the posture, with two named gaps.** The Japanese-language record
carries the whole apparatus in detail; it was invisible to the earlier passes because they searched
in English and around the surviving Takayama compound rather than around the town watch post that
actually held the bell. What is still unfound is the temple bell doubling as the alarm, and the
attachment of any of this to the DAIKANSHO OFFICE as opposed to the town's watch post.

### Passage 1 - the bell, the ladder on the roof, and the stored firefighting gear

Source: 自身番 ("jishinban", the Edo-period neighborhood watch house), Japanese Wikipedia, read via
the MediaWiki API on 2026-09-12: https://ja.wikipedia.org/wiki/%E8%87%AA%E8%BA%AB%E7%95%AA

VERBATIM (Japanese):

> 自身番は町内を見回り、不審者がいれば捕らえて奉行所に訴えた。また、火の番も重要な役割であり、自身番屋の多くには、屋根に梯子（小規模な火の見櫓）や半鐘が備えられていた。このため、捕り物道具や纏・鳶口・竜吐水・玄蕃桶（げんばおけ）・梯子・釣瓶といった火消道具が番屋内に用意され、半鐘が鳴らされると町役人・火消人足が自身番にかけつけて道具を持ち出し、勢揃いしてから火事場に赴いた。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> The jishinban patrolled the neighborhood and, if there was a suspicious person, seized them and
> reported them to the magistrate's office. Fire watch was also an important duty, and many watch
> houses were fitted with a ladder on the roof (a small-scale fire-watch tower) and a hansho bell.
> For this reason, arrest tools and firefighting tools - the matoi standard, the tobiguchi hook, the
> ryudosui pump, the genba bucket, ladders and well-buckets - were kept ready inside the watch
> house, and when the hansho was struck the town officers and firefighting hands rushed to the
> jishinban, took out the tools, assembled, and then went to the fire.

**How it supports the claim.** fn-30 asserts "a hansho bell on a ladder, a rooftop platform or a
simple frame at the office or the watch post". This passage gives exactly that: the ladder on the
roof described in the source's own words as a small-scale fire tower, with the hansho on it, at the
WATCH POST. It also gives the stored gear.

### Passage 2 - the ladder on the watch house IS the tower, and the tower's spread

Source: 火の見櫓 ("hinomiyagura", fire-watch tower), Japanese Wikipedia, same fetch:
https://ja.wikipedia.org/wiki/%E7%81%AB%E3%81%AE%E8%A6%8B%E6%AB%93

VERBATIM (Japanese):

> この町ごとに番屋（番所、自身番とも）を設置し番人（火番、番太郎・番太と呼ばれていた）を常駐させて24時間態勢で警戒にあたるのが一般的であった。このとき番人が町全体を見渡せるよう番屋に櫓を組んで一段高いところに見張台を置いたが、それが火の見櫓と呼ばれる。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> It was usual for a watch house (also called bansho or jishinban) to be set up in each such town
> and a watchman (called hiban, bantaro or banta) stationed there permanently, keeping guard around
> the clock. A frame was then raised on the watch house so that the watchman could look over the
> whole town, and a lookout platform was placed one level up; this is what is called a
> hinomiyagura.

The same article carries the sentence that fn-30's fourth assertion already states:

> 火の見櫓は江戸時代の江戸を皮切りに火消体制とともに整備されてゆき、昭和初期には全国ほぼ全ての地域に整備されていった。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> Fire-watch towers were built up together with the firefighting system, beginning with Edo in the
> Edo period, and by the early Showa period they had been built in almost all regions of the
> country.

**One caution on that last sentence** (raised here because fn-30 rests its whole "spread" reading on
it): a signed essay on the Fire and Disaster Prevention Museum's site puts the build-out later. 火の見
櫓からまちづくりを考える会 (the "Thinking about town-building from fire towers" association),
「火の見櫓は何を語るか」, https://www.bousaihaku.com/firetower/4293/, fetched 2026-09-12:

> 火の見櫓は江戸時代に起源を有するが、全国にくまなく建設されたのは昭和期、それも現在残っているものの多くは高度経済成長期に建設されたと推測される。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> The fire-watch tower has its origin in the Edo period, but its construction throughout the whole
> country came in the Showa era, and most of those that remain today are presumed to have been built
> during the high-growth period.

The two agree on the shape of the story - Edo origin, nationwide only much later - and differ on
whether "nationwide" is early Showa or the postwar boom. Since fn-30 uses the spread only to argue
that a country seat stands at the BEGINNING of the spread rather than at its end, the later dating
strengthens the entry's own reading rather than weakening it. Worth a clause; not a correction.

### Passage 3 - night patrols with clappers

Source: 拍子木 ("hyoshigi", clappers), Japanese Wikipedia, same fetch:
https://ja.wikipedia.org/wiki/%E6%8B%8D%E5%AD%90%E6%9C%A8

VERBATIM (Japanese), from the section headed 夜回り、夜警 (night rounds, night watch):

> 警防団や消防団などが夜、見回る時に、 「戸締り用心、火の用心」と声をあげながら、拍子木をカチカチッと打ち鳴らして歩く。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> When a keibodan or a fire brigade and the like make their rounds at night, they walk calling out
> "mind your locks, mind your fire" while striking the clappers together, clack-clack.

**Half-support, stated.** This gives the night patrol with clappers and its fire-watch call, but the
bodies it names (keibodan, shobodan) are modern. The practice is the one fn-30 describes; the
passage does not date it to the Edo period. If the entry wants the Edo dating it needs a second
source, and this reader did not find one - the targeted search for it was refused by the search host
(see "Searches still owed" below).

### Passage 4 - stored water

Source: 天水桶 ("tensuioke", rainwater barrel), Japanese Wikipedia, same fetch:
https://ja.wikipedia.org/wiki/%E5%A4%A9%E6%B0%B4%E6%A1%B6

VERBATIM (Japanese):

> 天水桶（てんすいおけ）とは、日本の伝統的な防火水槽である。雨水を貯めるための容器で、江戸時代には主に都市部の防火用水として利用された。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> The tensuioke is a traditional Japanese firefighting water cistern. It is a vessel for storing
> rainwater, and in the Edo period it was used mainly as firefighting water in urban areas.

### Passage 5 - the fireproof kura, and what it was for

Source: 土蔵 ("dozo", the plastered storehouse), Japanese Wikipedia, same fetch:
https://ja.wikipedia.org/wiki/%E5%9C%9F%E8%94%B5

VERBATIM (Japanese):

> 蔵は収納物によって、米蔵、味噌蔵、籾蔵、硝煙蔵、金蔵、経蔵などに分けられ、これらを火災、湿気、盗難等から守る機能をもつ。

and, from the section headed 耐火性能 (fire resistance):

> 壁厚は約300mm以上あることが多く、開口部の外戸なども土戸（土と漆喰で戸の外部表面を覆ったもの）とすることがある。古くは江戸時代の大火、近代では空襲による大火でも、内部に火が回らない事例が多かった。

*Translation from the Japanese, by this reader (Claude Opus 5); originals above:*

> Storehouses are divided according to what they hold - rice store, miso store, unhulled-rice store,
> gunpowder store, money store, sutra store and so on - and have the function of protecting these
> from fire, damp, theft and the like.

> The wall thickness is often about 300 mm or more, and the outer doors of the openings are
> sometimes made as earth doors (doors whose outer surface is covered with earth and plaster). In
> the great fires of the Edo period and, in modern times, in the great fires caused by air raids,
> there were many cases in which the fire did not get through to the interior.

And for the tax rice specifically, 郷倉 / 郷蔵 ("gogura", the village granary), reached through the
義倉 article, same fetch: https://ja.wikipedia.org/wiki/%E7%BE%A9%E5%80%89

> 郷倉（ごうぐら、郷蔵）は江戸時代、各地に設けられた倉庫である。年貢米を始めとする農作物を運び出す際の一時保管場所として、1か村ないし数か村ごとに1か所置かれ、厳重な警備体制を敷いていた。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> The gogura was a storehouse established in various places in the Edo period. It was placed one per
> village, or one per several villages, as a temporary storage place for carrying out tax rice and
> other farm produce, and was kept under strict guard.

**How these support the claim.** fn-30's "above all the plastered fireproof kura around the tax rice
and the ledgers, because losing the tax rice was the career-ending disaster" gets its two halves
from two passages: the dozo is the fire-resistant form, explicitly built for a rice store among
others, with a measured wall thickness and a record of surviving conflagrations; and the gogura is
the tax-rice store kept under strict guard. What no passage read here states is the CAUSAL claim -
that the storehouse was fireproofed rather than the horizon watched BECAUSE the tax rice was the
career-ending loss. That remains the record's own reading and should stay labeled as one.

### What is STILL ABSENT for fn-30

- **The local temple bell doubling as the fire alarm.** Not found. The 火の見櫓 article's list of
  related items names 半鐘 and 番屋 but no temple bell; the 自身番 article does not mention one.
- **Any of this attached to the daikansho OFFICE.** Every passage above attaches the bell, the
  ladder, the tools and the water to the TOWN and its watch house, not to the tax office. fn-30
  says "at the office or the watch post" - the watch-post half is now cited; the office half is
  not, and should be narrowed or marked.

### Searches still owed

Two searches for the remaining gaps were attempted on 2026-09-12 through `search.yahoo.co.jp` and
were refused by the host (the response carried only Yahoo's own help and privacy links - the
rate-limit shape), so they are recorded as unrun rather than as empty:

- `火の用心 拍子木 夜回り 江戸時代 町内 夜警 由来` (Edo-period dating of the clapper patrol)
- `郷蔵 年貢米 土蔵 防火 米蔵 陣屋 代官所 保管` (the tax-rice store at a jin'ya specifically)

A later pass should re-run these two, and should try 半鐘 and 寺 together for the temple-bell half.

---

## 2. `cities/government.html` fn-35 - the government compound at the crossing, the bureaus on the avenues

**Verdict: CITED for the first half (the compound stands in the middle of the city, where its main
streets cross); STILL ABSENT for the second half (the bureau offices lining the avenues around it).**

### Source

Su Bai (宿白), 「現代城市中古代城址的初步考查」 ("A preliminary investigation of ancient city sites
within modern cities"), published by the Peking University Institute of Humanities and Social
Sciences and reproduced with attribution by the Institute of Archaeology and Cultural Heritage,
Lanzhou University, 2024-04-22:

  https://whyc.lzu.edu.cn/index.php/portal/article/index.html?cid=22&id=259

Fetched 2026-09-12 with curl and a desktop user agent. Su Bai (1922-2018) was the founder of
Chinese historical-period archaeology at Peking University; this is his own survey method for
reading a Tang-and-later city's plan out of the modern street grid.

### Passage 1 - the square city and its great cross-street

VERBATIM (Chinese):

> 即方形城，每面各开一门，四门内街道相通，合组成一大十字街，大十字街四隅的每一隅，又都各设小十字街

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> that is, a square city, with one gate opened on each side, the streets inside the four gates
> running into one another and combining to form one great cross-street; and at each of the four
> corners of the great cross-street, a small cross-street is set in turn.

and, summarizing the rule he then applied across north China:

> 方形城、每面各一门，内以大小十字街划分大小区域。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> A square city, one gate on each side, divided internally into larger and smaller districts by
> great and small cross-streets.

### Passage 2 - the yamen and the market stood in the middle of the city

VERBATIM (Chinese), from the section on the Ming enfeoffment of imperial princes:

> 这种王城有不少建在城市中心区域，如成都蜀王城，长沙潭王城，北方如青州的齐王城和后来的衡王城。兴建这类王城都是把原来布置在城市中部的衙署、市场和一部分民居拆了，大小街巷也改了；迁到城内别处的地方衙署，又要重新布置街道和附属机构。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> Not a few of these princely cities were built in the central district of the city - such as the
> Shu Prince's city at Chengdu and the Tan Prince's city at Changsha, and in the north the Qi
> Prince's city at Qingzhou and the later Heng Prince's city. Building a princely city of this kind
> always meant demolishing the yamen, the market and part of the dwellings that had originally been
> laid out in the middle of the city, and the larger and smaller streets and lanes were altered too;
> and the local yamen, moved elsewhere inside the city, then required a fresh laying-out of streets
> and of its attached offices.

**How it supports the claim.** fn-35 asserts that "in a PLANNED seat the bureaus did not scatter:
the compound sat where the main streets crossed and the offices lined the avenues around it". Su Bai
states, as the thing a Ming prince's city had to demolish, that the yamen and the market "had
originally been laid out in the middle of the city" - and in the city form he has just defined, one
gate per side and a great cross-street, the middle of the city IS where the main streets cross. He
also states that a relocated yamen required the streets and its "attached offices" (附属机构) to be
laid out afresh, which is the nearest thing found to the second half: the offices are treated as
belonging with the compound and as something the street layout is arranged around. That is support
for the bureaus not scattering; it is NOT a statement that they lined the avenues.

Su Bai names the main yamen as one of the four things that define whether a city's plan has changed
at all, which is worth quoting for the weight it puts on the compound's position:

> 城市的主要布局有没有改变，主要是指城门和主要街道的位置有没有变化？还有主要衙署和宗教建筑的位置有没有变动？

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> Has the city's principal layout changed - meaning chiefly, have the positions of the city gates
> and the main streets changed? And have the positions of the principal yamen and of the religious
> buildings shifted?

### A second passage, bearing on fn-35's last sentence

fn-35 ends "The one office that sits apart is Rites, among the temples it oversees." Su Bai gives a
fixed position for ritual buildings, though not the Rites office:

> 一些坛庙在城内有了固定的方位，山西平遥和解县的文庙都是大定年间建于城的东南隅

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> Some altars and temples came to have fixed orientations within the city: the Confucian temples of
> Pingyao and Xie County in Shanxi were both built in the southeast corner of the city during the
> Dading era.

That supports "ritual buildings have their own fixed quarter, away from the compound" as a real
pattern with two named instances, and gives the quarter a compass corner. It does not put the
ministry of Rites there - that is the setting's own arrangement.

### What is STILL ABSENT

No page was found stating that the bureau offices lined the avenues around the compound. The nearest
is Su Bai's 附属机构 ("attached offices") above, which places them with the compound without saying
how they stood on the street. The entry should either narrow to what Su Bai says - the compound in
the middle, where the main streets cross, with its attached offices laid out around it - or keep the
avenue-lining sentence as the record's own extension and label it.

---

## 4. `religion-and-death.html` fn-22 - the spacing of ranked torii

**Verdict: split.** Meiji Jingu: **CITED**. Nagao Shrine: **CONTRADICTED** on the figure (the
official prefectural page says about 300 m, twice, not 200 m) while supporting the claim it is used
for. Kasuga Taisha's 1.3 km: **STILL ABSENT**.

### Meiji Jingu - CITED

Source: the shrine's own access page, https://www.meijijingu.or.jp/access/, fetched 2026-09-12.

VERBATIM (Japanese), the two notes on the page:

> ※境内のほぼ中央に御社殿があり、各入口から約10分かかります。

> ※各入口から御本殿まで徒歩で約10分かかります。

*Translation from the Japanese, by this reader (Claude Opus 5); originals above:*

> Note: the shrine buildings stand at roughly the center of the precinct, and it takes about 10
> minutes from each entrance.

> Note: it takes about 10 minutes on foot from each entrance to the main hall.

And for which torii those are, the Japanese Wikipedia article 明治神宮
(https://ja.wikipedia.org/wiki/%E6%98%8E%E6%B2%BB%E7%A5%9E%E5%AE%AE, read via the MediaWiki API
2026-09-12) gives the ranked sequence:

> 明治神宮には全部で8基の鳥居がある。南参道入口にある第一鳥居、北参道の入口にある北参道口鳥居、南参道と北参道の合流地点にある第二鳥居（大鳥居）、西参道の入口にある西参道口鳥居、拝殿の手前にある第三鳥居（南玉垣鳥居）、…

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> Meiji Jingu has eight torii in all: the first torii at the entrance of the southern approach; the
> north-approach-mouth torii at the entrance of the northern approach; the second torii (the great
> torii) at the junction of the southern and northern approaches; the west-approach-mouth torii at
> the entrance of the western approach; the third torii (the southern tamagaki torii) just before
> the worship hall; ...

**How these support the claim.** fn-22 asserts "Meiji Jingu's three span a ~10-minute walk". The
shrine's own page gives the ~10-minute walk from the entrance to the main hall, and the Wikipedia
article places the first torii at that entrance, the second at the mid-way junction of the
approaches and the third immediately before the hall - so the three DO span that walk, and they are
ranked landmarks along an approach rather than a corridor of gates. The parenthetical "(~250 m
apart)" in fn-22 is arithmetic done on the 10 minutes, not a figure any source states; it should be
marked as the record's own estimate.

### Nagao Shrine - CONTRADICTED on the number

Source: Nara Prefecture's official cultural-resources page for 長尾神社 (Nagao Shrine, Katsuragi
City), https://www.pref.nara.lg.jp/ikasu-nara/bunkashigen/main00275.html, fetched 2026-09-12.

VERBATIM (Japanese), twice on the page:

> これは鎌倉時代、流鏑馬（やぶさめ）が行なわれていた名残で、一ノ鳥居から境内入り口の二ノ鳥居まで約300メートル、幅は7メートル余り（4間）あります。

> 一ノ鳥居と二ノ鳥居との間の参道は約300メートルあります。鎌倉時代の古文書によると、例祭日にここで流鏑馬の神事が行われていました。

*Translation from the Japanese, by this reader (Claude Opus 5); originals above:*

> This is a remnant of the yabusame horseback archery performed in the Kamakura period: from the
> ichi-no-torii to the ni-no-torii at the entrance of the precinct is about 300 meters, and the
> width is a little over 7 meters (4 ken).

> The approach between the ichi-no-torii and the ni-no-torii is about 300 meters. According to
> Kamakura-period documents, the yabusame rite was performed here on the day of the annual
> festival.

**What this means for the entry.** fn-22 states "Nagao Shrine's ichi->ni is 200 m". The prefectural
government's own page gives about 300 m and gives it twice, in two separately worded sentences. Two
readings are open: the entry means a different Nagao Shrine (there are several; this is the
Engishiki-listed one in Katsuragi, Nara, and it is the one a search for the name returns), or the
figure is simply wrong. Either way the figure as written is not supportable and should be changed to
about 300 m with this link, or dropped.

The correction does not disturb the argument. fn-22 uses the pair to show that ranked gates are
landmarks strung along a whole approach and that "at 1-3 ft/px a ranked pair is off the map at every
settlement scale" - 300 m makes that point harder than 200 m does. The page also gives a figure the
entry does not have and could use: the approach between the two gates is **a little over 7 meters
(4 ken) wide**, dated by the same sentence to a Kamakura-period usage.

### Kasuga Taisha's 1.3 km - STILL ABSENT

Queries run through `search.yahoo.co.jp` via curl, 2026-09-12:

- `春日大社 一之鳥居 本殿 距離 km 参道`
- `春日大社 表参道 一之鳥居 二之鳥居 約 メートル 距離 歩く`

Candidates and what happened to each:

- https://www.kasugataisha.or.jp/guidance/morisanpo/ - the shrine's OWN page, titled
  「一之鳥居から二之鳥居へ」 ("From the ichi-no-torii to the ni-no-torii"). **Fetched and read.** It
  walks the reader from the first torii past the Yogo pine, the muku tree, the Tobihino meadow and
  the Umadome bridge to the second torii, and states that the approach was used as a horse ground -
  but it gives **no distance at all**, in meters or in minutes. This is the most likely page in
  existence to carry the figure and it does not.
- https://www.mlit.go.jp/tagengo-db/H30-00892.html - the Japan Tourism Agency's multilingual
  commentary database, entry 春日大社 一之鳥居. **Fetched and read.** It gives the gate's date (rebuilt
  1638), its Important Cultural Property status, its alignment ("directly west of Mt. Mikasa") and
  the Sanjo road running west from it to the center of Heijokyo - but **no distance to the shrine**.
- https://ja.wikipedia.org/wiki/%E6%98%A5%E6%97%A5%E5%A4%A7%E7%A4%BE - **read via the MediaWiki
  API.** Gives the first torii's height (7.75 m) and its 1638 rebuilding; **no distance**.
- https://www.naracity-guide.com/spots/58, https://coolnara.net/jp/kasugataisya-sando/,
  https://travel.navitime.com/ja/area/jp/spot/02301-1301154/ - not fetched. Each is a tourism or
  blog page, below the three official pages above that were fetched and that do not carry the
  figure; a blog's distance estimate would not be citable under this project's rule even if found.

So the 1.3 km stands unsourced. It is plausible on the ground (the first torii is by Sanjo-dori at
the west edge of Nara Park and the shrine is up against Mt. Mikasa) but no page read states it. The
honest options are to drop the number and say "over a kilometer, the gate standing at the park's
western edge with the shrine under Mt. Mikasa" with the shrine's own walk page as the support, or to
keep it as a labeled measurement off a map, which is a GUESS in this project's taxonomy.

---

## 7. `religion-and-death.html` fn-84 - the pauper ossuary as an earthen mound with one stupa

**Verdict: CITED.** A municipal cultural-property listing describes exactly this: bones of the
unconnected dead gathered up, a burial mound raised over them, and an image set on top - and it
names the temple a "throw-in temple" for having done it from the Edo period onward.

### Source

Shinagawa City (Tokyo), designated cultural property 海蔵寺無縁塔群 ("the group of muen stupas at
Kaizoji"), on the ward's official site:

  https://www.city.shinagawa.tokyo.jp/PC/sangyo/sangyo-bunkazai/sangyo-bunkazai-shitebunkazai/shina/20240108180212.html

Fetched 2026-09-12 with curl and a desktop user agent.

### Passages

VERBATIM (Japanese):

> 江戸時代、品川に溜牢が置かれていた時、そこで死亡した人々の遺体がこの寺に運ばれ埋葬されたが、その数は元禄四年(一六九一）から明和二年（一七六五)までの間に、七百人を超えると伝えられている。宝永五年(一七〇八)、土地の有力者がこれを改葬し、遺骨を集めて墳墓を築き、その上に観音像を安置した。この塚は「頭痛塚」と呼ばれている。他に、天保の大飢饉の際の犠牲者、二一五人を祀る「二一五人塚」は、この「頭痛塚」に合葬されている。

> 慶応元年(一八六五)、品川惣町によって建立された「津波溺死者供養塔」、同年建立の、元禄以降の獄死者の遺骨を集めて葬った「無縁塔」、明治六年(一八七三)建立の、無縁一二六八人の霊を祀る「無縁供養塔」があり…

> このように、江戸期から現在に至るまで、横死者の霊を供養して来たため品川の「投げ込み寺」と呼ばれ、その性格を後世まで残してきたものである。

*Translation from the Japanese, by this reader (Claude Opus 5); originals above:*

> In the Edo period, when the holding gaol was placed at Shinagawa, the bodies of those who died
> there were carried to this temple and buried; their number is said to have exceeded seven hundred
> between Genroku 4 (1691) and Meiwa 2 (1765). In Hoei 5 (1708) a local man of influence had them
> reinterred, gathered the bones and raised a burial mound, and installed a Kannon image on top of
> it. This mound is called the "Zutsu-zuka" (headache mound). Besides it, the "215-person mound",
> which enshrines the 215 victims of the great Tenpo famine, is interred together with this
> "Zutsu-zuka".

> There is a "memorial stupa for those drowned by the tsunami", erected in Keio 1 (1865) by the
> whole town of Shinagawa; a "muen stupa", erected the same year, in which the bones of those who
> had died in gaol since the Genroku era were gathered and buried; and a "muen memorial stupa",
> erected in Meiji 6 (1873), enshrining the spirits of 1,268 unconnected dead...

> In this way, because it has made offerings for the spirits of those who died violent deaths from
> the Edo period to the present, it is called the "throw-in temple" of Shinagawa, and has carried
> that character down to later ages.

**How it supports the claim.** fn-84 describes the pauper ossuary as "a low earthen mound with one
weathered stupa holding the communal bones of the poor and the unconnected dead". Every structural
element of that is in this listing: the bones of the poor and the unconnected gathered together
(遺骨を集めて, and 無縁 by name), a burial mound raised over them (墳墓を築き, 塚), and a single
marker set on top of it (その上に観音像を安置した), with the whole thing named a 無縁塔 - a stupa for
the unconnected dead. The Edo dates are on the record (1691-1765 for the gaol dead, 1708 for the
mound).

**The half it does NOT support, stated.** fn-84 also says the ossuary "stands outside the walls by
the crematory". Kaizoji is a temple in the Shinagawa post-town, not a structure by a crematory
outside a wall, and the listing says nothing about walls or a crematory. The FORM is now cited; the
POSITION is not, and remains the record's own reconstruction.

### Supporting context, if the entry wants the institution named

新纂浄土宗大辞典 (the New Compiled Jodo-shu Dictionary), entry 投げ込み寺 ("throw-in temple"),
signed article, https://jodoshuzensho.jp/daijiten/index.php/投げ込み寺, fetched 2026-09-12:

> 身寄りのない遊女や災害での被災者、行き倒れた者などが葬られた寺。災害被害者が穴に投げ込まれるように 埋葬 されたことから「 投げ込み寺 」と言われるようになったといわれる。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> A temple where courtesans with no relatives, victims of disasters, those who collapsed and died on
> the road and the like were buried. It is said to have come to be called a "throw-in temple"
> because disaster victims were buried as if thrown into a pit.

The same entry records that Jokanji's death register, kept from 1743, shows an estimated 25,000
people buried there - which is the order of magnitude the communal-bones claim needs, on a named
document.

---

## 8. `towns.html` fn-24 - south as the formal and auspicious orientation

**Verdict: CITED for "formal", with the auspicious half narrowed.** The rule is stated as a
regulation, not as folklore, by the article on the best-preserved Qing county yamen in China.

### Source

内乡县衙 (the Neixiang County yamen, Henan - the only surviving complete Qing county government
office in China, a National Key Cultural Relic Protection Unit), Chinese Wikipedia, read via the
MediaWiki API 2026-09-12: https://zh.wikipedia.org/wiki/%E5%86%85%E4%B9%A1%E5%8E%BF%E8%A1%99

### Passage

VERBATIM (Chinese):

> 它在整体布局上严格按照清代地方官署规制，表现了“坐北朝南、左文右武、前朝后寝、狱房居南”的传统礼制思想。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> In its overall layout it follows strictly the regulations for Qing-dynasty local government
> offices, expressing the traditional ritual-propriety conception of "sitting to the north and
> facing south, civil on the left and military on the right, the court in front and the sleeping
> quarters behind, the gaol lying to the south".

and, on the gaol:

> 坐北朝南的监狱位于内乡县衙的西南部，占地南北130丈，东西70丈。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> The gaol, which also sits to the north and faces south, lies in the southwestern part of the
> Neixiang yamen, occupying a site 130 zhang north-south and 70 zhang east-west.

**How it supports the claim.** fn-24 says "The fallback when nothing is said is south, the formal
and auspicious orientation". This passage gives south-facing as the FORMAL orientation in the
strongest available sense: not a preference but 规制, the regulation for a local government office,
and 礼制, ritual propriety - and it gives it as the first of a set of four paired rules that fix the
whole compound. It is a magistrate's office, which is what fn-24 is about. The word 礼制 carries
"proper" rather than "lucky": this passage supports **formal** and does not itself support
**auspicious**. Either narrow the entry to "the formal orientation, by the regulation for a
government office", or keep "auspicious" and mark that half as resting on general reading.

**A limit to state.** This is a Chinese yamen under Qing regulation, and fn-24 is about a
magistrate's manor in a setting modeled on both China and pre-Meiji Japan. The claim it supports is
the one fn-24 actually makes - what the fallback orientation IS when the ground says nothing - and
the setting's government is drawn from the Chinese side of the model, so the fit is good; but the
entry should say the rule is quoted from the Chinese office regulation rather than from Japanese
practice.

---

## 10. `homesteads.html` fn-92 - the north-China courtyard house ranges its animals along one wing

**Verdict: CITED, with the wing NAMED and a caveat about the source's tier.**

### Source

四合院 (siheyuan, the Chinese courtyard house), Chinese Wikipedia, read via the MediaWiki API
2026-09-12: https://zh.wikipedia.org/wiki/%E5%9B%9B%E5%90%88%E9%99%A2

### Passage

VERBATIM (Chinese), from the section 厢房 (the side wings):

> 然而，在中国华北地区，东厢房夏季西晒，冬季直接受到西北冷风吹袭，所以不宜居住，陕西四合院东厢房多被富户用来存储粮物，或作厨房、马厩。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> However, in the North China region the east wing takes the western sun in summer and is struck
> directly by the cold northwesterly wind in winter, so it is unsuitable for living in; in Shaanxi
> courtyard houses the east wing is often used by wealthy households to store grain, or as a kitchen
> or a horse stable.

**How it supports the claim.** fn-92 asserts that "the north-China courtyard house ranges its
animals along one wing" and flags that no source is cited for the Chinese half. This passage states
it, and states more than the entry does: it names the region (North China), names the wing (the EAST
wing), names the household type (wealthy - 富户, which matters because fn-92's knob turns on whether
a household OWNS its team), and gives the physical reason (the east wing is the unlivable one, so it
takes the stable, the kitchen and the grain store). The entry could be sharpened from "one wing" to
"the east wing, the one made unlivable by the summer sun and the winter wind, which takes the
stable, the kitchen and the grain store together" - which is a better map fact than the one it
currently carries, and it lands on the courtyard-map branch of fn-92's own knob, where the byres
follow the wealthiest households.

**The caveat, stated.** This is an encyclopedia article. Its own footnote for this sentence points at
福客民俗网 (`dict.folkw.com/Dict.asp?id=3258`, entry 陕西院落), which survives only as a Wayback
capture from 2007 and was not fetched - so the article's own reference is not a page a reader can
click today, and under this project's rule "an encyclopedia article's own references over the
article" cannot be followed here. The Chinese Wikipedia article itself IS readable at the URL above
and the quotation is on it, so the citation stands on the article; the entry should not claim a
scholarly source behind it. A later pass wanting a stronger footing should look for a Shaanxi or
Hebei vernacular-architecture survey.

---

## 3. `cities/government.html` fn-36 - the small wayside shrines between the temples of a temple quarter

**Verdict: PARTIAL - one half CITED, the other STILL ABSENT.** The existence and density of small
neighborhood shrines inside a town block is now on a readable page; their standing specifically in
the ground BETWEEN the temples of a temple quarter is not, and neither is the drawn form (vermilion
roof, its own little gate).

### The half that is CITED - small shrines, several to one town block, put up locally

Source: 秋葉神社 (Akiba shrines - the fire-preventing cult, the most widely distributed of the small
neighborhood shrines), Japanese Wikipedia, read via the MediaWiki API 2026-09-12:
https://ja.wikipedia.org/wiki/%E7%A7%8B%E8%91%89%E7%A5%9E%E7%A4%BE

VERBATIM (Japanese):

> 祠の場合は火伏せの神でもあるため、燃えにくい石造りの祠などが見かけられる。小さな祠であることが多く、一つの町内に何箇所も設置されている場合もある。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> In the case of a small shrine, because the deity is also a fire-quelling one, stone-built shrines
> that do not burn easily are seen. They are often small shrines, and in some cases several of them
> are set up within a single town block.

And, for one worked instance of "put up by whoever had reason to", the article 新宿二丁目 (Shinjuku
2-chome), same fetch, https://ja.wikipedia.org/wiki/%E6%96%B0%E5%AE%BF%E4%BA%8C%E4%B8%81%E7%9B%AE:

> 三社稲荷神社（16番2号） 新宿遊廓が移転した1921年（大正10年）頃、大変火事が多かったため稲荷神を祀るようになったといわれる。

*Translation from the Japanese, by this reader (Claude Opus 5); original above:*

> Sanja Inari Shrine (no. 16-2). It is said that around 1921, when the Shinjuku pleasure quarter
> moved here, fires were very frequent, and so the Inari deity came to be enshrined.

**How these support the claim.** fn-36 asserts "small wayside shrines - a vermilion-roofed shed with
its own little gate, put up by whoever had reason to and tended by the neighborhood around it". The
Akiba passage gives the small shrine as a type, gives its DENSITY in the terms a map needs - several
within one chonai, the town block - and gives the reason a block would have one (fire). The Shinjuku
passage gives an instance of a quarter putting one up for a reason of its own. Together they support
"several small shrines scattered through a town block, each put up locally for a local reason",
which is the substance fn-36 needs for the ground between buildings.

### What is STILL ABSENT

- **The temple-quarter placement.** Nothing read puts these shrines in the ground BETWEEN the
  temples of a teramachi. The teramachi itself is well attested - 新纂浄土宗大辞典, entry 寺町, signed
  by 伊藤真昭, https://jodoshuzensho.jp/daijiten/index.php/寺町, fetched 2026-09-12:

  > こうして成立した京極 寺町 には南北五キロ以上にもわたって九六箇寺が存在し、その中でも 浄土宗 寺院 （西山含む）が六〇箇寺と圧倒的な数を占めていた。

  *Translation from the Japanese, by this reader (Claude Opus 5); original above:*

  > In the Kyogoku Teramachi thus formed there were ninety-six temples over a stretch of more than
  > five kilometers north to south, of which Jodo-shu temples (including the Seizan branch) made up
  > an overwhelming sixty.

  That establishes the quarter (a forced relocation of temples into one strip by Hideyoshi in 1591)
  and its density, which fn-36's paragraph depends on. It says nothing about what stood between
  them.
- **The drawn form** - a vermilion-roofed shed with its own little gate. The Akiba passage actually
  cuts the other way for that cult: it says the small shrines are often STONE, chosen because stone
  does not burn. If the map draws a vermilion wooden shed, that is an Inari convention rather than a
  general one, and the entry should either say Inari or mark the form as a map drawing convention.

### Searches run and refused

Queries attempted through `search.yahoo.co.jp` on 2026-09-12, in this order:

- `寺町 小さな祠 稲荷 町内 路傍 朱塗り 屋根 小祠 江戸 町` - returned only commercial and unrelated
  pages (a butsudan retailer's outdoor-shrine catalog, a Tokyo tourism book, a bookshop, the
  Nichibunken yokai database, a Cabinet Library scan of 祠曹雑識); none fetched, none of them a
  description of a temple quarter's ground.
- `寺町 由来 寺院 集めた 城下町 小祠 稲荷 路傍 町` - returned the Jodo-shu dictionary entry (fetched,
  quoted above), a high-school field-study PDF, a magazine feature and a kimono-rental glossary.
- `町内 稲荷 小祠 路傍 祠 町内会 祀る 由来` and `寺町 通り 祠 地蔵 稲荷 点在` - **both refused by the
  host** (rate-limited: the response carried only Yahoo's own help and privacy links).

Wikipedia search on `ja` for `屋敷神 町内 祠 稲荷` produced the two articles quoted above. A CiNii
search on `町内社` returned urban-sociology work on the modern neighborhood association, not on its
shrines.

### For a later pass

The likely carrier is a municipal cultural-property survey of a named teramachi - the shape of source
that answered claims 7 and 11 here. `search.yahoo.co.jp` with a NAMED quarter (京都寺町, 金沢寺町台,
高岡寺町) plus 祠 or 小社 is the query to run when the host is available again.

---

## 5. `religion-and-death.html` fn-38 - a Chinese temple account booking annual lamp-oil and incense income

**Verdict: STILL ABSENT for the account; but a readable page NARROWS the claim in a way that makes
the Chinese half converge with the Japanese half the entry already has.**

### The narrowing finding

Source: 香油錢 (incense-and-lamp-oil money), Chinese Wikipedia, read via the MediaWiki API
2026-09-12: https://zh.wikipedia.org/wiki/%E9%A6%99%E6%B2%B9%E9%8C%A2

VERBATIM (Chinese):

> 古時信徒常以線香、蠟燭、燈油、金紙等物品，捐獻廟宇、寺院，以供祭祀之用。但後來逐漸不以實物捐贈，而以金錢替代，故稱香油錢、香火錢、香紙錢。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> In ancient times believers often donated objects such as incense sticks, candles, lamp oil and
> gold paper to temples and monasteries, for use in the offerings. But later they gradually ceased
> to donate goods in kind and substituted money, and so it is called incense-oil money,
> incense-fire money, or incense-paper money.

**What this does to the claim.** fn-38's opening asserts that "amulets, charms, talismans, incense
and lamp oil were temple-direct SALES and a major revenue stream", and flags the Chinese half - a
temple account booking an annual oil-lamp and incense income - as resting on general reading. This
passage says the Chinese flow of incense and lamp oil to a temple was a DONATION, in kind and then
in money, named for the two goods: not a sale. That is the same relation fn-38's own Japanese half
already states for the omamori ("viewed mainly as a donation to the place that issues it"). So the
two halves of the paragraph agree once the Chinese half is stated as donation rather than sale, and
the paragraph's conclusion - that no third-party religious-goods shop competes at the temple's own
gate - survives unchanged, since the goods reach the temple rather than leaving it as stock.

**What it does NOT do.** It is an encyclopedia article on a term, not a temple's account book, and it
gives no annual figure. The specific claim - an account booking an annual oil-lamp and incense
income - remains unsourced.

### FOR THE GM - the documents that would settle it

The genuine sources for a Chinese temple's accounts are the Dunhuang monastic account documents
(入破历, the receipts-and-disbursements registers of the Tang and Five Dynasties monasteries), in
which lamp oil is a standing line. Two editions exist and neither is readable online:

1. 『敦煌寺院會計文書研究』 - CiNii NCID **BA33354578**, record
   https://cir.nii.ac.jp/crid/1970023484973540763. Monograph; no digital text.
2. 『敦煌寺院会计文书整理研究』 (*The collation and research of the accounting manuscripts of
   Dunhuang temples*) - CiNii records https://cir.nii.ac.jp/crid/1971993809763724487 and
   https://cir.nii.ac.jp/crid/1971712334785924359. Monograph; no digital text.

One promising open-access essay was found and **could not be read**: 郝春文 (Hao Chunwen),
「唐後期五代宋初敦煌僧尼的生活方式」 ("The way of life of Dunhuang monks and nuns in the late Tang,
Five Dynasties and early Song"), PDF hosted by Northwestern University's Buddhist art project at
https://buddhist-art.arthistory.northwestern.edu/buddhistweb/essays/ho_chunwen9.PDF - the file
downloads (127 KB) but its font uses a non-standard character collection
(`Adobe-WinCharSetFFFF`), so `pdftotext` extracts nothing and `pypdf` extracts mojibake. **This is a
FOR THE GM item**: the paper is public, the blocker is purely the PDF encoding, and a reader who can
open it in a normal PDF viewer would settle whether it quotes a monastery's oil account. A later
pass could also try OCR on rendered pages.

### Searches run

Through `search.yahoo.co.jp` on 2026-09-12, before the host began refusing:

- `寺院 経済 香火钱 香油 收入 年 明清 账簿` - candidates: zh.wikipedia 香火錢/香油錢 (read, quoted
  above); baike.baidu.com 香油钱 (not fetched - Baidu Baike is an open wiki with no editorial
  provenance a reader can follow, below the bar this project sets); 10vows.com and thepaper.cn
  (modern Chinese journalism about present-day temple donation boxes, which is what the last pass
  also hit); airitilibrary.com, 「從香火到香油錢: 明清小說中女性宗教活動的信仰光環與塵俗世道」 - a
  scholarly article on Ming-Qing fiction, **paywalled at Airiti**, and on fiction rather than
  accounts.
- `敦煌 寺院 入破历 油 灯油 帐 收入 支出 研究` - candidates: baike.baidu.com 入破历 (not fetched, same
  reason); the Northwestern PDF (fetched, unreadable, above); a Kyoto University repository PDF on
  S.1519V, a 10th-century Dunhuang manuscript catalog (not fetched - it is about a document
  INVENTORY, not an income account); CiNii 敦煌寺院會計文書研究 (record read, book not online).
- `寺院経済 香火田 灯油 収入 唐代 敦煌 寺院 会計 文書` - candidates: the same CiNii book; a Hosei
  University bibliography record for 「晩唐・五代の敦煌寺院経済 - 収支決算報告を中心に」 (a
  bibliographic entry only, no full text); two modern temple-accounting business pages.

CiNii search on `敦煌寺院会計文書` returned the three monograph records listed above and nothing with
full text. A Chinese Wikipedia lookup of 寺院经济 returned an EMPTY article.

---

## 6. `religion-and-death.html` fn-43 - the funeral trades in a row of shops by the burial ground

**Verdict: STILL ABSENT.** Nothing read puts coffin-makers, grave-marker cutters or paper-goods
makers in a row of shops beside a burial ground. One SPECIFIC document that would answer the
Japanese half has been identified and cannot be opened - see FOR THE GM below.

### What WAS confirmed (the goods, not their shops)

Source: 紮作 (zhazuo / paper-craft effigies), Chinese Wikipedia, read via the MediaWiki API
2026-09-12: https://zh.wikipedia.org/wiki/%E7%B4%AE%E4%BD%9C

VERBATIM (Chinese):

> 給先人的祭品通常是些生活必需品及奢侈品，例如房子、汽車、僕人、紙衣等，並以實物呈現，不同於貨幣樣式的紙錢。有些人相信燃燒紙紮祭品可傳送到陰間給神明或先人。

*Translation from the Chinese, by this reader (Claude Opus 5); original above:*

> The offerings for the ancestors are usually necessities of life and luxuries - houses, cars,
> servants, paper clothes and the like - and they are presented as physical objects, unlike the
> paper money, which takes the form of currency. Some believe that burning paper-craft offerings
> sends them to the underworld for the deities or the ancestors.

This supports fn-43's description of the burned goods - and, usefully for the entry, states that the
paper HOUSES, SERVANTS and GOODS are a distinct trade from the spirit MONEY, which fn-43 lumps into
one phrase ("the makers of the spirit money and the paper replicas of houses, servants and goods").
Whether one maker or two stood in the row is a question the entry could now raise honestly.

It does not put the trade at a burial ground. The only shop it names is a present-day Hong Kong
one.

### What is STILL ABSENT

- **Coffin-makers and grave-marker cutters standing in a row by the burial ground** - Japanese or
  Chinese. Nothing found.
- **Any premodern clustering of funeral trades by a graveyard at all**, as opposed to the
  well-attested clustering of ordinary trades at a temple's front gate, which fn-43's earlier
  sentences already have.

### FOR THE GM - the document that would answer the Japanese half

木下光生 (Kinoshita Mitsuo), 「近世葬具業者の基礎的研究」 ("A basic study of early-modern funeral-goods
dealers"), 『大阪の歴史』 (*The History of Osaka*, ed. Osaka City History Compilation Office) no. 57
(2001), pp. 61-87, published by 大阪市史料調査会. ISSN 0388-6808, NCID AN0026826X, NDL bibliographic
id 5787865; CiNii record https://cir.nii.ac.jp/crid/1521699230921906944; NDL record
https://ndlsearch.ndl.go.jp/books/R000000004-I5787865.

This is precisely the subject - who the early-modern funeral-goods dealers WERE, as a trade - in a
city-history journal, by a historian of early-modern status and funerary practice. **It is not
online**: CiNii holds only the bibliographic record, there is no DOI, no repository copy and no
J-STAGE entry, and the journal is a local historical society's. A reader with access to a Japanese
research library (or NDL's in-library digital transmission) could settle the Japanese half of fn-43
from this one article. The same author's 『近世身分制社会と葬送の研究』
(https://cir.nii.ac.jp/crid/1910020910680053376) is the book-length companion.

### Searches run

Through `search.yahoo.co.jp` on 2026-09-12:

- `纸扎店 棺材铺 城门外 墓地 附近 街 旧时 丧葬 行业 聚集` - returned **only** YouTube and Bilibili
  fiction: serialized web-novels and audio dramas about paper-effigy shops and coffin shops. Nothing
  fetched; nothing was a source.
- `石屋 葬具屋 墓地 門前 軒を連ねる 寺町 江戸 商売` - candidates: a senbei shop's local-history column
  on Edo grave practice (kikaku-sembei.co.jp), ADEAC's Minato City history section 「(二) 門前町屋の
  形成」 (**fetched**: https://adeac.jp/minato-city/text-list/d100010/ht101430 - the page returns only
  its own headings, the text being delivered into a viewer this fetch does not execute, so nothing
  could be read), a Tokyo walking magazine on Yanaka, and an antiques dealer's glossary entry for
  陣屋.
- `棺屋 石塔屋 墓所 前 町 江戸 職業` and `石屋 石工 墓石 寺 門前 並ぶ 江戸` - **both refused by the
  host** (rate-limited).

Wikipedia searches: `ja` for `早桶 棺桶 葬具` returned only a novel; `ja` for `墓地 石材店 葬具 門前
商店` returned NOTHING; `zh` for `紙紮 店 喪葬` returned the 紮作 article quoted above plus modern
Taiwanese and Malaysian funeral-custom articles. CiNii `葬具` returned the Kinoshita article above.

**A note on the ADEAC host.** `adeac.jp` carries the full text of hundreds of Japanese municipal
histories and is very likely to hold the answer to this claim and to claim 3. Its pages did not
render to plain HTML for this fetcher. Finding the right request shape for ADEAC would be the single
highest-value tooling improvement for a later pass on this batch.

---

## 9. `homesteads.html` fn-91 - the area of a dooryard kitchen bed

**Verdict: STILL ABSENT for the area, and the second pass found something that should CHANGE the
entry's framing.** One SPECIFIC document that is exactly on the question has been identified and
cannot be opened - see FOR THE GM below.

### The framing finding - the yashikibatake is often NOT in the dooryard

Source: 家庭菜園 (household kitchen garden), Japanese Wikipedia, section 屋敷畑, read via the
MediaWiki API 2026-09-12: https://ja.wikipedia.org/wiki/%E5%AE%B6%E5%BA%AD%E8%8F%9C%E5%9C%92

VERBATIM (Japanese):

> 日本の家庭で自家消費するための作物を作る耕作地を屋敷畑という。地域によって「センザイバタ」「サエンバ」「カドノハタケ」など様々な呼称で呼ばれている。屋敷と地続きの土地の片隅や、換金作物を作る畑や田の隣の空いたスペース、河川敷などの片隅など、屋敷から離れた隙間的な土地で行われる場合も多い。農家に限らず、漁村などでも二次的な作業として行われている。

> 屋敷畑の起源は弥生時代にまで遡ることができ、江戸時代には農民だけでなく武士階級の屋敷内にも畑があった。柳田國男は『カイトの話』の中で、屋敷畑を家屋に付随した最も原初的な耕地として紹介した。宮本常一は、年貢米を作るための水田が「公的な感じ」のする耕作地であるのに対し、屋敷畑はより個人的な所有観念が強い土地であると指摘している。

*Translation from the Japanese, by this reader (Claude Opus 5); originals above:*

> Cultivated ground on which a Japanese household grows crops for its own consumption is called
> yashikibatake. Depending on the region it goes by various names - "senzaibata", "saenba",
> "kadonohatake" and others. It is often worked on a corner of land continuous with the homestead,
> or on empty space next to the fields and paddies where cash crops are grown, or on a corner of a
> riverbed - that is, on gap-like land AWAY from the homestead. It is not confined to farming
> households; in fishing villages too it is carried on as a secondary activity.

> The origin of the yashikibatake can be traced back as far as the Yayoi period, and in the Edo
> period there were plots not only inside farmers' homesteads but inside those of the warrior class
> as well. Yanagita Kunio, in "Kaito no hanashi", introduced the yashikibatake as the most primitive
> cultivated ground attached to a dwelling. Miyamoto Tsuneichi pointed out that whereas the paddy
> for growing tax rice is cultivated ground with "a public feel" to it, the yashikibatake is land on
> which the sense of private ownership is stronger.

**Three things the entry should take from this.** (1) It confirms the last pass's finding: this
article names the bed and gives NO area. (2) It contradicts fn-91's framing in one respect - the
entry treats the yashikibatake as the dooryard bed, and the article says the ground is often
gap-like land AWAY from the homestead, beside the fields or on a riverbank. If the map draws all of a
household's self-consumption ground in the dooryard, that is a simplification with a source against
it, and it should be labeled. (3) It gives the entry two things it does not have and could use: the
regional names (senzaibata, saenba, kadonohatake), and Miyamoto Tsuneichi's contrast between the
paddy as ground with a "public feel" and the homestead plot as private ground - which is exactly the
distinction fn-91 is drawing when it separates the bed from the household's hatake.

A second Japanese page adds a fact the entry may want: 村上忠喜 (Murakami Tadayoshi, Kyoto City
Cultural Property Protection Division), 「民家の屋敷地とニワ - その民俗的素描 -」, 日本庭園学会誌 18
(2007), pp. 41-42, open-access PDF on J-STAGE,
https://www.jstage.jst.go.jp/article/jgarden1993/2007/18/2007_18_41/_pdf/-char/ja - fetched and read
2026-09-12. Its outline lists, under the public/private gradation inside the homestead plot,
「屋敷畑の免租地」 - "the yashikibatake as tax-exempt land" - and, under the sexual division of
labor, 「屋敷畑での労働は女性が担う」 - "the labor in the yashikibatake is borne by women". It gives no
area either; it is a symposium outline of two pages.

### FOR THE GM - the document that would answer it

小林力 (Kobayashi Tsutomu), 「湖東地方における屋敷畑の機能と形態」 ("The function and form of the
yashikibatake in the Koto region"), 『人間文化: 滋賀県立大学人間文化学部研究報告』 (*Human Culture:
Bulletin of the School of Human Cultures, University of Shiga Prefecture*) vol. 29 (March 2011),
pp. 48-61. NCID AA11176128, NDL bibliographic id 11124374, NAID 40018854412; CiNii record
https://cir.nii.ac.jp/crid/1520572359297949696.

This is a fourteen-page study whose title is the question fn-91 asks - the FUNCTION AND FORM of the
homestead field, in a named region (Koto, the east shore of Lake Biwa) - and a study of form in a
university bulletin of that length would ordinarily tabulate areas. **It could not be opened.** The
CiNii page itself renders through JavaScript and returned no text to this fetcher; the University of
Shiga Prefecture's institutional repository (`usp.repo.nii.ac.jp`) answered **HTTP 406 Not
Acceptable** from nginx to both a plain request and one carrying full browser Accept and
Accept-Language headers, for its search endpoint and its OAI endpoint alike; the NDL holds only the
bibliographic record. University-bulletin articles of this vintage are usually deposited openly, so
the likeliest situation is that the PDF exists in that repository behind a request shape this reader
could not produce.

### Searches run

- `search.yahoo.co.jp`: `菜園 屋敷内 面積 何坪 家庭菜園 江戸 農家 自給 野菜 広さ` returned only modern
  gardening and farmland-price pages (maff.go.jp crop-area statistics, an asset manager's blog, a
  self-sufficiency how-to, a farmland valuation site). `屋敷畑 面積 坪 自家用 野菜 農家 調査 平均` -
  same shape of result. `屋敷畑 免租 面積` and `湖東地方における屋敷畑の機能と形態 小林力 人間文化` -
  **both refused by the host** (rate-limited).
- `kotobank.jp/word/屋敷畑` - fetched: **HTTP 404**, no such entry.
- Bing (`www.bing.com/search`) - returned results entirely unrelated to the query (English
  cover-letter pages for a Japanese query), i.e. bot-detection junk; DuckDuckGo lite served a
  CAPTCHA; Startpage served a JavaScript challenge; Mojeek returned no organic results; goo and
  Ecosia returned nothing extractable. **Every general search engine except Yahoo Japan was
  unusable from this host, and Yahoo Japan began refusing partway through this batch.**
- J-STAGE search API for `屋敷畑`: fifteen hits, of which the Japanese ones are the Murakami outline
  above, two homestead-GROVE papers (Tochigi and the Kanto plain) and a planning paper on village
  dwelling space; the rest are African and Indonesian agronomy using the word for a homegarden. A
  title search for `屋敷畑の機能と形態` returned nothing, confirming the Kobayashi paper is not on
  J-STAGE.
- CiNii `屋敷畑`: ten hits, of which the Kobayashi paper is the only study of Japanese form and
  function; the others are Edo-period cadastral registers held in archives (検地帳, 屋敷畠帳) and
  African homegarden work.
- NDL Search API `屋敷畑`: ten hits, all Edo-period land deeds and cadastral documents in archival
  collections, several marked 《制限あり》 (access restricted). These are the primary documents that
  would carry actual plot areas, but they are archival scans, not text.

**What this means for the entry as it stands.** fn-91's band - a few tsubo up to about 1.4 se,
roughly 10 to 140 sq m - is correctly labeled a GUESS today and must stay labeled one. The second
pass did not find a number; it found the paper that probably has one, and a framing problem that is
worth fixing regardless of whether the number ever arrives.

