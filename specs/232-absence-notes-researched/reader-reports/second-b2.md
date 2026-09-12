# Second pass, batch b2: Japanese and Chinese local sources (11 notes)

Reader: second-b2. Tooling: `curl` with a desktop browser user agent, `search.yahoo.co.jp`
fetched through curl, the MediaWiki API on `ja.wikipedia.org` and `zh.wikipedia.org`.

## Verdicts

| # | note | subject | verdict |
|---|---|---|---|
| 1 | `cities/fabric.html` fn-30 | jin'ya / daikansho town fire posture | IN PROGRESS |
| 2 | `cities/government.html` fn-35 | government compound at the crossing, bureaus on the avenues | IN PROGRESS |
| 3 | `cities/government.html` fn-36 | wayside shrines between the temples of a temple quarter | IN PROGRESS |
| 4 | `religion-and-death.html` fn-22 | ranked-torii spacing (Nagao, Meiji Jingu, Kasuga) | IN PROGRESS |
| 5 | `religion-and-death.html` fn-38 | Chinese temple accounts booking lamp-oil and incense income | IN PROGRESS |
| 6 | `religion-and-death.html` fn-43 | coffin-makers and paper-goods makers in a row by the burial ground | IN PROGRESS |
| 7 | `religion-and-death.html` fn-84 | pauper ossuary as an earthen mound with one stupa | IN PROGRESS |
| 8 | `towns.html` fn-24 | south as the formal and auspicious orientation | IN PROGRESS |
| 9 | `homesteads.html` fn-91 | area of a dooryard kitchen bed | IN PROGRESS |
| 10 | `homesteads.html` fn-92 | north-China courtyard house: animals along one wing | IN PROGRESS |
| 11 | `vegetation.html` fn-87 | igune on north and west; the founding definition | IN PROGRESS |

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

