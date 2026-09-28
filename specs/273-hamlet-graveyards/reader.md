# Feature 273 reader: does a hamlet keep its own graveyard, or use the main village's?

**Tooling note:** `WebSearch` reported its session budget already exhausted (200/200) on the very
first call of this task, before this reader made any query itself - the budget is evidently shared
across the whole session (parallel readers on the same 273 queue). All searching below was done by
`WebFetch` against pages that do not require the `WebSearch` tool: Wikipedia and Kotobank articles
fetched directly, and J-STAGE's own site-search (`jstage.jst.go.jp/result/global/...`), which is not
a blocked search engine. Google, Bing and DuckDuckGo were tried via direct `WebFetch` and all three
were unusable (Google returned an error page, Bing returned stale/irrelevant cached results, DuckDuckGo
served a CAPTCHA). This narrowed what could be found; several SILENT entries below reflect that gap,
not necessarily an absence in the literature.

---

## JAPAN

### 1. Hamlet/settlement keeps its own graveyard (集落墓地, 部落, 小字 as the burial unit)

**FOUND, regional (Amami/Kikaijima, not mainland):**

Oikawa Takashi (及川高), "先祖へと収束する力―喜界島における墓制とその語りを貫くもの―," *文化人類学研究*
vol. 9 (2008), pp. 79-100. Free PDF: https://www.jstage.jst.go.jp/article/wsca/9/0/9_79/_pdf
(article page: https://www.jstage.jst.go.jp/article/wsca/9/0/9_79/_article/-char/ja)

A timeline table in the paper, tracking burial custom on each settlement (集落) of Kikaijima from
late Edo through Showa, gives (verbatim, from the "近世末〜明治" and "明治以降" rows):

> "衛生の観点により政府によって崖穴葬等への曝葬が禁止。土葬化される...引き続き崖穴前部に設置。一方崖穴
> 外にも、集落墓地の形成始まる。"

("On hygienic grounds the government banned exposed burial such as cliff-cave interment; burial
switched to earth-burial ... interment in front of the cliff cave continued, but alongside the
cave, the formation of *hamlet graveyards* [集落墓地] also began.")

> "設置後10年程度をかけて、完全に火葬に切り替わる...また全集落において、崖穴の放棄と、集落墓地の拡張進む。"

("Over roughly ten years after [the crematorium's] establishment, [burial] switched entirely to
cremation ... and in every settlement [全集落], the abandonment of the cliff-caves and the expansion
of the hamlet graveyard proceeded.")

This is a folklore/anthropology paper working from named 集落 (Sakane, Aden, Kamikachi, etc.) on one
island, each with its own burial history and, from the Meiji ban on exposed burial onward, its own
"集落墓地." It is explicitly regional: Kikaijima/Amami has a distinct cave-burial (ムヤ) culture unlike
mainland Japan, and the paper itself notes "喜界島は各集落の独立性が高く...民俗文化の集落間差異は大きかった"
(Kikaijima's settlements are highly independent of one another; folk-cultural differences between
settlements were large).

**FOUND, general (Japan-wide, not settlement-specific vocabulary):**

ja.wikipedia.org/wiki/墓, section "近代以降の墓":

> "第二次世界大戦前までは、自分の所有地の一角や、隣組などで墓を建てるケースも多かったが、戦後は、基本的に
> 「○○霊園」などの名前が付いた、地方自治体による大規模な公園墓地以外は、寺院や教会が保有・管理しているもの
> が多い。"

("Until before the Second World War, it was common to build a grave on a corner of one's own land,
or through a *tonarigumi* [neighborhood association, a sub-village unit] ...")

"Tonarigumi" is smaller than a hamlet, but the passage documents a sub-village burial unit as
normal practice into the twentieth century, general Japan-wide (not attributed to a single region).

### 2. 村墓地/共同墓地 explicitly held BY a hamlet (as opposed to the whole village)

**FOUND, general but undated/unclear period (reads as a modern administrative classification):**

ja.wikipedia.org/wiki/墓地, section "村落墓地":

> "村落墓地：村落の住民が共有して管理する墓地"

("Village-settlement graveyard: a graveyard that the residents of the settlement [村落] jointly own
and manage.")

The same article also states current law: "日本では、墓地の新設は許可が必要である。また現在は、村落墓地、
個人墓地は許可されない" (in Japan a new graveyard requires a permit, and at present neither a village
graveyard nor a private graveyard is permitted) - confirming 村落墓地 was a real, named category, but
the article gives no Edo/Meiji-era timeline and does not distinguish 村 from a hamlet within it
(村落 is ambiguous between the two in ordinary usage).

### 3. 屋敷墓 - a household's own grave on its own land

**SILENT for the term itself** - despite direct fetches, ja.wikipedia.org/wiki/屋敷墓 does not exist
(404), and a Wikipedia internal search for 屋敷墓 returns no dedicated article, only incidental hits
(祖先崇拝's mention of 屋敷神, unrelated ghost-story articles). kotobank.jp/word/屋敷墓 and
kotobank.jp/word/屋敷墓地 both 404. Queries tried: direct Wikipedia article fetch, Wikipedia internal
search, two Kotobank URL guesses, a Google fetch (blocked/empty).

**FOUND under a different heading, general:** see the ja.wikipedia.org/wiki/墓 quote under item 1
above ("自分の所有地の一角...墓を建てるケースも多かった") - the practice the term 屋敷墓 names is
attested, just not under that headword in what this reader could reach.

### 4. 両墓制 (two-grave system): where each grave lay against the settlement

**FOUND, general with a stated region of prevalence:**

kotobank.jp/word/両墓制:

> "遺体を葬る墓（埋め墓）と供養を営む墓（参り墓）を別に設ける風習"
>
> 埋め墓: "河川敷・山中・海浜などに設置される" ... "共有地の場合が多く、死亡順に埋葬していって、埋葬する場所が
> なくなれば、またもとの場所へもどる" ... "石などを置くくらいで永久的な施設を設けることがない"
>
> 詣り墓: "村内の寺・堂などの境内に設けられる" ... "墓石によって標示されることも多く"
>
> 地域分布: "関西地方を中心に分布し、九州や東北地方ではほとんどみられない"

("A custom of keeping separate the grave where the body is interred [umehaka] from the grave where
memorial rites are performed [mairibaka]." The umehaka sits on shared/common land - riverbank,
hillside, or beach - reused in order of death, unmarked. The mairibaka sits "within the village
[村内], in the precincts of a temple or hall," often marked by a stone. Distribution: centered on
the Kansai region, almost never seen in Kyushu or Tōhoku.)

This is directly on point for the question: it describes exactly the split the GM is asking about -
the corpse/bones stay near where they were buried (which for an outlying hamlet could be hamlet
land), while the *marker and rites* sit at a temple "within the village" (村内), i.e. the main
settlement that has the temple. It is regional (Kansai-centered per the source), not universal.

### 5. Folklore survey giving how many graveyards a multi-hamlet village had

**SILENT.** Queries tried: `共同墓地 村墓地 集落単位 江戸時代 民俗` (WebSearch, blocked by exhausted
budget before running), Bing/DuckDuckGo fetches for the same (blocked/captcha), J-STAGE site search
for 集落墓地 (returned 11 results, none a quantified multi-hamlet survey - see the source list below),
Kikaijima paper close-read (gives per-settlement histories on one island, not a count of graveyards
per multi-hamlet administrative village on the mainland).

### 6. Bones to the parish temple (檀那寺) in another village

**FOUND, general, does not address inter-village distance directly:**

ja.wikipedia.org/wiki/檀家:

> "檀家は特定の寺院に所属し、葬祭供養の一切をその寺に任せ、布施を払う。"
>
> "檀那寺に墓を作るということも半ば義務化されていたが、一般庶民でも墓に石塔を立てる習慣ができたのはこの頃で
> ある。"

("A danka household belonged to a specific temple and entrusted all funerary and memorial rites to
it, paying dues... Making one's grave at one's danna-dera [assigned parish temple] was also
semi-obligatory; it was around this time [Edo period, per the article's surrounding context] that
even commoners began the custom of erecting a stone monument at the grave.")

This documents the *binding* of a household to one specific temple, generally, without regard to
where that household actually lived - which is consistent with, but does not explicitly state, an
outlying hamlet's dead going to a temple in the main village. Danna-dera assignment in this period
was not necessarily the nearest temple.

---

## CHINA (Ming-Qing)

### 1. A natural village (自然村) keeps its own graves

**SILENT.** Queries tried (J-STAGE site search, since WebSearch was unavailable): `自然村 墓地`
(70 results, browsed top 20 - mostly Korean/Thai/Bengali/Japanese rural-settlement studies, one
Sichuan village-landscape paper with no graveyard content in its abstract), `宗族墓地` (zero results),
`新界 宗族 墓` (8 results, all about lineage ritual/politics generally, not village-vs-graveyard
specifics), en.wikipedia.org/wiki/Chinese_clan and /wiki/Ancestor_veneration_in_China (both checked,
neither states whether graves were per natural village).

### 2. Lineage graves on a hillside (墳山), corporately held, not obviously one-village-only

**FOUND, regional, primary-source-based:**

Nakajima Gakushō (中島楽章), "清代徽州の山林経営・紛争・宗族形成：祁門凌氏文書の研究" ["Mountain-forest
management, disputes and lineage formation in Qing-dynasty Huizhou: a study of the Qimen Ling clan
documents"], *社会経済史学* [Socio-Economic History] 72-1 (2006), pp. 3-25. Free PDF:
https://www.jstage.jst.go.jp/article/sehs/72/1/72_KJ00005697845/_pdf
(article page: https://www.jstage.jst.go.jp/article/sehs/72/1/72_KJ00005697845/_article/-char/ja)

General background statement in the paper (framing prior scholarship on China broadly, not just
Huizhou):

> "従来の研究では、伝統中国では兄弟が土地や家屋などの資産を均等分割するのが原則であり、未分割のまま残される
> のは墓地や祭祀用の土地などに限られると説かれることが多い。"

("Previous research has generally held that in traditional China, brothers dividing property such
as land and houses equally was the rule, and what was commonly left undivided was limited to things
like graveyard land and land for ancestral rites.")

The paper's own case (Qianlong 46 / 1781, Qimen county, Huizhou prefecture, Anhui):

> "葉家源にある凌氏の始祖の墳山の林木を伐採して、銭54,000文の収益を得た際には...一族の祠堂である「寄公祠」
> の収入となり、残りの収益は股分をもつ族人に分配された。始祖の墳山さえ、祠堂名義の族産は尾根部分だけで、斜
> 面部分は族人が股分を分有する共同経営地だったのである。"

("When trees were felled on the founding ancestor's grave-hill [墳山] at Yejiayuan, earning 54,000
cash, [most of] the proceeds became income for the lineage's ancestral hall, the 'Jigongci,' with
the rest distributed among lineage members holding shares. Even for the founding ancestor's own
grave-hill, the property held corporately in the ancestral hall's name was only the ridge; the slope
was land jointly managed and share-held by the descendants.")

This is a documentary (primary-source, contract/stele-based) case: the ancestor's grave-hill is
lineage-corporate property (held via the ancestral hall and shared among descendants), not simply
"the village's" land, and not framed as belonging to a single natural village - the Ling lineage
plausibly had members in more than one settlement. It is explicitly regional (Huizhou/Anhui, Qing),
which is the paper's whole point (Huizhou's mountain-economy lineages are presented as somewhat
distinctive within China).

### 3. Charity graveyard (义冢/義塚) shared by several villages

**FOUND, but urban/guild rather than rural/inter-village - caveat is load-bearing:**

Sato Manabu (佐藤学), "明末清初期一地方都市における同業組織と公権力：蘇州府常熟県「當官」碑刻を素材に"
["Trade organizations and public authority in a late-Ming/early-Qing local city: material from the
'Dangguan' stelae of Changshu county, Suzhou prefecture"], *史学雑誌* 96-9 (1987), pp. 1468-1487.
Article page: https://www.jstage.jst.go.jp/article/shigaku/96/9/96_KJ00003674361/_article/-char/ja

The article discusses outside (Xin'an/Huizhou) merchants resident in Changshu county town
establishing a 義塚 (charity graveyard) as a mutual-aid institution for their guild. This confirms
义冢/義塚 as a real Ming-Qing institution for burying the unclaimed/poor dead of a defined
membership - but the membership here is a sojourning merchant guild in a *county city*, not several
rural natural villages pooling a shared graveyard. Whether the same charity-graveyard model was used
between rural villages is not established by this source.

**HUMAN-FETCHABLE:** the article's own PDF (2114K) did not confirm as a free download when checked
(J-STAGE flagged possible institutional-access-only, unlike the two papers above that were
confirmed free); a companion result from the same 義冢 search, 帆刈浩之, "近代上海における遺体処理問題と
四明公所：同郷ギルドと中国の都市化" (*史学雑誌* 103-2, 1994) on a native-place guild's corpse-handling in
Shanghai, was not re-checked for free-PDF status either. Both would need a direct-PDF-fetch attempt
(as was done successfully for the Huizhou and Kikaijima papers above) to move past "abstract only."

### 4. General fengshui/hillside grave-siting pattern (supporting context, not settlement-unit-specific)

**FOUND, general:**

en.wikipedia.org/wiki/Fengshui:

> "In southern China, this often resulted in villages located on high hills safe from flooding and
> erosion, with pooling streams that allow for easy irrigation and drainage, fields downstream
> fertilized by sewage, and graves located on the highest hills far from water and on otherwise
> unvaluable farmland."

General pattern (siting logic, not who owns/shares a given hillside graveyard).

Also: ja.wikipedia.org/wiki/宗族, general/China-wide:

> "族長のもとに族譜を有し、宗祠を設け、族産をおくものが多く、特に華中・華南に普及した"
> (footnote) "祭田・義荘など同族の共有財産"

("[Lineages] typically had a genealogy under a lineage head, established an ancestral hall, and held
lineage-corporate property - especially widespread in central and southern China." Footnote: "such
as ritual-fields and charitable estates - the lineage's shared property.") Confirms 族産
(lineage-corporate land, of which grave-land is one common form per the Huizhou paper above) as a
general Central/South China institution, without itself naming graves specifically.

---

## Judgment

The evidence supports **more than one form** on both sides of the strait - this reads as a knob, not
a single answer, and the research gives a directional hint for Japan but not a clean frequency count
for China.

**Japan:** the strongest, most directly-on-point single source is the 両墓制 entry: the corpse/bones
were commonly kept in an *unmarked* grave on shared/waste land near where the settlement actually
was (river flat, hillside, beach - land a hamlet, not just the seat village, would have at hand),
while the *marked, visited* memorial sat "within the village" (村内) at a temple - which for an
outlying hamlet without its own temple would be the main village's temple. That is a real middle
form the GM's three options don't quite name: the bones stay local (functionally "hamlet burial"),
but the enduring, visitable marker and the funerary rites sit at the main village. Layered onto that:
the Kikaijima paper shows unambiguous per-settlement graveyards (集落墓地) once cremation and the
crackdown on exposed burial arrived, and the general Wikipedia 墓 passage shows sub-village
(tonarigumi-level, i.e. smaller than even a hamlet) private/neighborhood graves were normal
nationwide into the 20th century. The danka/danna-dera material shows the *memorial and ritual* side
was temple-bound regardless of the household's hamlet. Put together: Japan looks like a knob between
"hamlet has a physical burial plot on its own land" (attested generally and, concretely, on
Kikaijima) and "the marker/rites sit at the main village's temple" (attested via 両墓制 and 檀家) -
with the two NOT mutually exclusive, since 両墓制 is precisely that combination. Regional variance is
explicit in the sources themselves (両墓制 is Kansai-centered; Kikaijima is its own Amami culture), so
per-settlement variance rolled from the map's seed, as the CLAUDE.md's knob doctrine wants, fits the
evidence well.

**China:** thinner. What is solidly documented (Nakajima's Huizhou paper, from primary contracts) is
that grave land was routinely held as undivided lineage-corporate property (族産) rather than by
individual households or, apparently, by a single natural village as a civic unit - the grave-hill
belonged to the *lineage* (via its ancestral hall and share-holding descendants), which in a region
of dispersed single-surname settlement could span more than one natural village of the same lineage.
The charity-graveyard (义冢) form is real but the only citable case found here is an *urban guild's*
graveyard, not a rural multi-village one, so it cannot be used to support "several villages pooled a
common graveyard" without that caveat attached or better sourcing. No source found states outright
that an ordinary natural village, on its own, kept a village graveyard as a civic (non-lineage)
institution the way Japan's 村落墓地 is described - that remains SILENT despite multiple searches, and
should be flagged to the GM as an open gap rather than guessed.

## Counts

- Japan: 4 FOUND (集落墓地/hamlet graveyard - regional; 両墓制 umehaka/mairibaka split - regional with
  stated distribution; danka/danna-dera temple burial - general; own-land/neighborhood grave via
  ja.wikipedia 墓 - general), 1 SILENT (quantified multi-hamlet graveyard-count survey), 1 mixed
  (屋敷墓 as a headword is SILENT/unreachable, but the underlying practice is FOUND under a different
  heading).
- China: 2 FOUND (Huizhou lineage grave-hill as corporate property - regional/primary-source; general
  fengshui hillside-siting and 宗族/族産 background - general), 1 FOUND-with-caveat (义冢 charity
  graveyard - confirmed as an institution but only in an urban/guild case, not rural/multi-village),
  1 HUMAN-FETCHABLE-unconfirmed (a second guild-corpse-handling paper, Shanghai, PDF status not
  checked), 1 SILENT (natural village keeping its own civic, non-lineage graveyard).
