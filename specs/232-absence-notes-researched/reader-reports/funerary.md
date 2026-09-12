# Feature 232 reader report: funerary-and-temple (29 notes)

Read 2026-09-12. Verdicts are about whether a PUBLICLY READABLE page carrying a supporting
passage exists - not about whether the record's assertion is true.

**Fetching method.** The default fetcher was tried first; where it refused or returned a JS
shell, `curl` with a desktop browser user agent was used through Bash, and PDFs were taken
down and run through `pdftotext`, with the page rendered to an image (`pdftoppm`) wherever the
text layer was OCR and therefore untrustworthy for a verbatim quote. Two pages this project had
previously recorded as blocked serve their full text to curl: **patheos.com** (recorded as
"403 Forbidden (refused)" under fn-16) returned HTTP 200 and the whole article. The
Association for Asian Studies (fn-38) was not retried - a different route was searched instead.

**Where a quote is not in English** it is given in this project's own English translation,
marked as a translation, with the original beside it as the checker's anchor.

## Verdict table

| note | subject | verdict |
|---|---|---|
| `cities/fabric.html` fn-39 | back alley surfaced with gravel or planks | **CITED** (planks only; gravel not found) |
| `cities/government.html` fn-36 | wayside shrines on the ground between temples | **STILL ABSENT** |
| `cities/sizing.html` fn-3 | a great temple's approach carried shops and inns | **CITED** |
| `religion-and-death.html` fn-16 | Zhengyi priests marry, live in households, inherit | **CITED** |
| fn-22 | Meiji Jingu's three torii span a ~10-minute walk | **STILL ABSENT** |
| fn-38 | a Chinese temple account booking oil-lamp and incense income | **STILL ABSENT** |
| fn-43 | coffin-makers and marker-cutters in a row by the burial ground | **STILL ABSENT** |
| fn-44 | fortune-tellers at the gate; retained temple artisans housed | **CITED** (diviners; artisans not found) |
| fn-45 | the temple forecourt's periodic market, stall space rented | **CITED** |
| fn-48 | the village shrine seated at the shuikou | **CITED** (shuikou siting; not the earth god, not "most strategic") |
| fn-49 | a village shrine's footprint | **STILL ABSENT** |
| fn-50 | the keidai's swept gravel or flagged surface and its upkeep | **STILL ABSENT** |
| fn-52 | grain drying, market and opera on the hall's plaza | **CITED** (grain drying and festival use; market and opera not found) |
| fn-54 | the path and the ground under each arch swept its whole length | **STILL ABSENT** |
| fn-57 | how wide the tended collar around a grave ran | **STILL ABSENT** |
| fn-61 | how common a village's own graveyard was | **CITED** (prevalence; household threshold and grandfathering not found) |
| fn-63 | Buck's survey, ~2% of farm area under graves | **FOR THE GM** |
| fn-65 | an area per body or a density of graves on the ground | **CITED** |
| fn-66 | a household is registered to the temple that buries it | **CITED** |
| fn-68 | the pyre set back from the road, off the ceremonial approach | **CITED** (a stated setback rule; the funeral path not found) |
| fn-72 | a cremation ground's cleared extent | **CITED** |
| fn-75 | the size of a pauper bone mound | **STILL ABSENT** |
| fn-76 | the base of Kyoto's ear mound | **CITED** |
| fn-78 | a mound raised at the great Edo execution ground | **STILL ABSENT** |
| fn-80 | area per body, the acreage ladder, the Chinese full-body multiple | **CITED** (the Chinese multiple; the Japanese ladder still the project's own) |
| fn-81 | a wayside shrine stood at a threshold | **CITED** (landing, crossing, gate; "a well" not found) |
| fn-82 | teahouses, eateries and sweet-sellers at the gate | **CITED** (eateries at the gate, sweets on the pilgrim road) |
| fn-83 | a souvenir trade at a PREMODERN gate | **CITED** |
| fn-84 | the pauper ossuary as an earthen mound with a stupa | **STILL ABSENT** |

**Totals: 17 CITED (9 of them partial, each limit named below), 11 STILL ABSENT, 1 FOR THE GM, 0 CONTRADICTED.**

---

## `cities/fabric.html` fn-39 - a back alley surfaced with unpaved gravel or planks

**CITED** (the plank half only).

URL: <https://ja.wikipedia.org/wiki/%E8%B7%AF%E5%9C%B0> (ja.wikipedia, 路地), section on the
Edo back-tenement alley. Read by curl with a browser user agent, full article text.

Passage, verbatim:

> 路地の中央には溝板（どぶいた）が並べられており、その下には幅が6寸から7寸（18センチメートルから21センチメートル）の小さなどぶが掘られていた

Translated from the Japanese by this project: "Down the middle of the alley plank gutter-covers
(dobuita) were laid in a row, and beneath them a small gutter 6 to 7 sun wide (18 to 21 cm) was
dug."

The same section fixes that this is the back-tenement alley and gives its width:

> 裏長屋の建物と建物の間の路地の幅は3尺から6尺ほど（0.9メートルから1.8メートルほど）だった

Translated: "The alley between one back-tenement building and the next was about 3 to 6 shaku
wide (about 0.9 to 1.8 m)."

**How it supports the claim.** The alley of an Edo back tenement carried a run of boards down
its centre - so a plank surface in a back lane is attested, and the alley's width is given as
well. **What it does NOT support:** gravel. Nothing read gives a back alley a gravel surface;
the one page that spoke to street surfacing put gravel on the Five Highways, not in a city's
back lanes. The gravel half should stay an absence, or the sentence should narrow to planks.

---

## `cities/government.html` fn-36 - small wayside shrines on the ground between the temples of a temple quarter

**STILL ABSENT.**

Searches run, query text exactly as issued:

- `祠 辻堂 町中 寺町 小祠 江戸 都市 民間信仰 建てられ`
- `道祖神 村境 辻 橋 峠 石仏 設置 場所`
- ja.wikipedia API search: `村落墓地 共同墓地 集落` (returned nothing on the temple quarter)

Candidates and what became of them:

| candidate | URL | outcome |
|---|---|---|
| ja.wikipedia 祠 | <https://ja.wikipedia.org/wiki/%E7%A5%A0> | Fetched. Defines the hokora as a small hall with no resident priest, put up on settlement or private land. Says nothing about a temple QUARTER or about ground standing between temples. |
| ja.wikipedia 寺町 | (via API extract) | Fetched. Carries nothing on 祠 / 小社 / 辻 / 地蔵 / 稲荷 - grepped for all five, no hits. It describes the temple quarter as a defensive and administrative arrangement. |
| 宮津市「寺町」 | <https://www.city.miyazu.kyoto.jp/site/citypro/17774.html> | Not fetched: a municipal tourism page about one town's temple row, judged from its title and search context to be a walking guide rather than a description of what stands between the temples. |
| まちづくりの沿革（江戸の防衛拠点、寺町から下町） | <https://www.reinet.or.jp/?page_id=13724> | Not fetched: the surrounding text is about the temple quarter as a defensive belt and the later merchant mixing, not about small shrines on the intervening ground. |

One adjacent finding that does NOT cover the claim: the 寺町 material describes temple land
being leased out to townspeople who opened shops, so the ground between temples in a city
filled with COMMERCE rather than with wayside shrines. That is a different picture from the
record's, and a session rewriting this entry should weigh it - but no page read states either
arrangement in a form that could be quoted at this assertion.

---

## `cities/sizing.html` fn-3 - the approach to a great temple carried the shops and inns that served it

**CITED.**

URL: <https://kotobank.jp/word/%E9%96%80%E5%89%8D%E7%94%BA-142614> (Kotobank, 門前町 - a page
that prints several signed reference works side by side). Read by the default fetcher.

Passages, verbatim, each with the work it comes from:

改訂新版 世界大百科事典:

> 寺社の参詣者を対象として商工業者が店舗を造営し、参詣道路の両側を中心に街村状に形成された集落。

Translated from the Japanese by this project: "A settlement formed in a street-village shape,
mainly along both sides of the pilgrimage road, where merchants and craftsmen built shops for
the worshippers coming to the temple or shrine."

日本大百科全書（ニッポニカ）:

> 参詣者を目当てとした旅籠（宿屋）や商店、手工業者の店が集まるようになった。

Translated: "Inns (hatago) aimed at worshippers, and shops, and the shops of craftsmen, came to
gather there."

精選版 日本国語大辞典:

> 参拝人・遊覧客を対象とする宿屋や商業が発達して、それらを主たる生業とする町

Translated: "A town where lodging houses and commerce serving worshippers and sightseers
developed, and where those are the principal livelihood."

**How it supports the claim.** Three independent reference works say the approach road to a
great temple or shrine was lined on both sides with shops and inns serving its worshippers -
exactly the record's sentence, including the point that the quarter is crowded rather than
quiet. The 街村状 ("street-village shape") is the map-relevant detail: the frontage follows the
approach.

---

## `religion-and-death.html` fn-16 - Zhengyi priests marry, reside in households, transmit hereditarily

**CITED.** The page the last pass recorded as "403 Forbidden (refused)" is readable: `curl` with
a desktop browser user agent returned HTTP 200 and 117 KB of article.

URL: <https://www.patheos.com/library/taoism/ethics-morality-community/leadershipclergy>
(Patheos Religion Library, Taoism: Ethics and Community - Leadership).

Passage, verbatim:

> In the Zhengyi Taoist tradition, the priest is almost always married, and marriage is a requirement to become a priest of the highest rank. The priest may be of any social class, and may be male or female, although most today are male. Often the role is passed down from generation to generation within a family.

And, on the contrast with monastic residence:

> Quanzhen clergy typically reside in monasteries.

> Throughout mainland China there are also unaffiliated Taoist priests who marry, live at home, and serve the local communities.

For the residence half specifically, a second readable work states it of Zhengyi priests
directly - URL: <https://contemporary_chinese_culture.en-academic.com/174/Daoism>
(*Encyclopedia of Contemporary Chinese Culture*, "Daoism"):

> Zhengyi priests do not usually live in a temple, although they are normally affiliated with one.

> they are members of families of hereditary priests and serve local communities.

**How it supports the claim.** The record's three assertions - almost always married, marriage
required for the highest rank, and hereditary transmission - are all three in the Patheos
sentence verbatim. The "RESIDE IN HOUSEHOLDS rather than a monastery" half is carried by the
encyclopedia's "do not usually live in a temple" plus Patheos's monastic contrast. **Limit to
state:** both works are written in the present tense about contemporary China and Taiwan, not
about a premodern period; neither is a primary source.

---

## `religion-and-death.html` fn-22 - Meiji Jingu's three torii span a ~10-minute walk (~250 m apart)

**STILL ABSENT.**

Searches and fetches:

| what | URL | outcome |
|---|---|---|
| Meiji Jingu official, precinct guide | <https://www.meijijingu.or.jp/guide/> | Fetched by curl, HTTP 200, full text. Gives the great torii's own dimensions - 鳥居の高さ12m、柱間9.1m、柱の径1.2m、笠木の長さ17m - and nothing on the distance between gates or on a walking time. |
| Meiji Jingu official, visit page | <https://www.meijijingu.or.jp/visit/> | Fetched by curl, HTTP 200. Grepped for 鳥居 / 分 / 参道: no hits in the served text. |
| ja.wikipedia 明治神宮 | <https://ja.wikipedia.org/wiki/%E6%98%8E%E6%B2%BB%E7%A5%9E%E5%AE%AE> | Fetched in full via the API. It ENUMERATES the eight torii and locates each - 南参道入口にある第一鳥居、北参道の入口にある北参道口鳥居、南参道と北参道の合流地点にある第二鳥居（大鳥居）… 拝殿の手前にある第三鳥居 - and gives the second gate's size (柱間が芯々30尺（約9.09m）で高さが39尺6寸（約12m）), but states no distance between any two of them and no walking time. |

So the positions of the three ranked gates are readable and their SEQUENCE is confirmed
(approach entrance, the junction of the two approaches, in front of the worship hall), but the
~10-minute walk and the ~250 m pitch are on no page read. A reader could pace it off a map;
that is a derivation, not a citation. The claim should stay an absence note, and the note can
usefully record that the gate positions ARE attested even though the spacing is not.

---

## `religion-and-death.html` fn-38 - a Chinese temple account booking an annual oil-lamp and incense income

**STILL ABSENT.**

Searches run, query text exactly as issued:

- `Chinese temple account books annual income lamp oil incense offerings Qing temple finance`
- `香油錢 香火田 廟產 收入 油香 清代 寺廟 經濟 來源 研究`

Candidates:

| candidate | URL | outcome |
|---|---|---|
| zh.wikipedia 香油錢 | <https://zh.wikipedia.org/zh-tw/%E9%A6%99%E6%B2%B9%E9%8C%A2> | Fetched in full via the API. Carries the PRACTICE - 古時信徒常以線香、蠟燭、燈油、金紙等物品，捐獻廟宇、寺院，以供祭祀之用 ("in old times believers often donated incense sticks, candles, lamp oil, paper money and such to temples and monasteries for use in the offerings") - and the merit box that receives it. It does NOT give a temple's ACCOUNTS, an annual figure, or a booked revenue line, which is what the assertion needs. |
| 從香火到香油錢（Airiti Library) | <https://www.airitilibrary.com/Article/Detail/1561378x-N202501220014-00001> | Not fetched past its landing page: an abstract page for a journal article about women's religious activity in Ming-Qing fiction. Its subject is the literary representation of offerings, not a temple ledger, and the full text is not on the open page. |
| Sixth Tone, "Faith in Finance?" | <https://www.sixthtone.com/news/1017275> | Not fetched: contemporary journalism about present-day temple commerce, which is what the last pass already rejected. |
| Chinascope, "temple economy" | <https://chinascope.org/archives/37925> | Not fetched: same - a 2020s business story. |
| 廟會與中國的民間社會 (Lin Rong-tse, 史耘 7, 2001) | <https://www.his.ntnu.edu.tw/publish03/downloadfile.php?issue_id=39&paper_id=249> | Fetched and read in full (see fn-45). It is about fairs and markets, and books no oil or incense income. |

The gap is specific and worth restating for whoever writes the next pass: what is missing is a
temple's own accounting, not the existence of incense and lamp-oil donation, which is amply
attested. A Chinese monastic or temple account book in a scholarly edition would settle it; no
such edition surfaced in a readable form here.

---

## `religion-and-death.html` fn-43 - coffin-makers and grave-marker cutters in a row of shops by the burial ground

**STILL ABSENT.**

Searches run:

- ja.wikipedia API search: `葬具屋 棺桶屋 石工 墓地` - **zero results**
- `祠 辻堂 町中 寺町 小祠 江戸 都市 民間信仰 建てられ` (returned the temple-quarter material above, nothing on funeral trades)
- `廟會 廟市 寺廟 空地 攤位 租金 定期市集 明清`

The Qing gazetteer passage recovered under fn-44/fn-45 does place the PAPER GOODS in the
faithful's hands at the temple - 執樂送經進駕(紙糊之宅第) ("with music they carry the sutras and
escort the palanquin - a paper-pasted mansion") - which is the burned paper house the record
describes. But it places it in the procession, not in a maker's shop, and nothing read puts
coffin-makers or marker-cutters in a row of shops beside a burial ground. The record's own
sentence already labels this "this project's reconstruction", and it should stay so labeled.

---

## `religion-and-death.html` fn-44 - fortune-tellers and diviners at the gate; retained temple artisans housed in the district

**CITED** for the first half. The second half is still absent.

URL: <https://www.his.ntnu.edu.tw/publish03/downloadfile.php?periodicalsPage=2&issue_id=39&paper_id=249>
- 林榮澤,「廟會」與中國的民間社會 - 以清代的華北、東北、西北為例, 史耘 no. 7 (July 2001), p. 57.
Open PDF on the National Taiwan Normal University history department's site; downloaded with
curl. **Its text layer is OCR and garbles characters**, so the quote below was transcribed from
the rendered page image (PDF page 5 = printed p. 57) rather than from the text layer.

The paper quotes 《新河縣志》 (16 juan, Qing Xuantong 1 supplementary printing), verbatim:

> 廟會，各村廟宇皆有年會。屆期，商販咸集，游人如織，豐收之年，輒演劇助盛。廟會者，農村一大交易場及娛樂場也。醫卜星相之流，及說書、幻術、技擊、西洋鏡、大興棚等雜技，亦搭棚獻藝。

Translated from the Chinese by this project: "Temple fairs: the temples of every village all
hold an annual gathering. When the day comes, traders assemble together and sightseers are as
thick as a weave; in a year of good harvest, plays are staged to swell the occasion. The temple
fair is the countryside's one great trading ground and pleasure ground. The sort that are
physicians, diviners, astrologers and physiognomists, and storytellers, conjurors, martial
performers, peep-show men, big-tent men and other variety acts, likewise put up sheds and offer
their arts."

**How it supports the claim.** 醫卜星相 is the standard Chinese four-character name for the
fortune-telling trades (physician, diviner, astrologer, physiognomist), and the gazetteer has
them putting up booths at the village temple's own fair. So diviners at the temple are attested
in a Qing source. **Limits to state:** this is the temple FAIR, not a permanent shopfront at
the gate, and it is a village temple rather than a great urban one.

**Not found:** nothing was read describing families of artisans retained by a temple for its
repair cycle and housed in its district. Searches: `門前町 茶屋 旅籠 土産物屋 参道 商店 江戸時代`
and the Kotobank 門前町 entry (fetched, five reference works, no craftsman-housing passage
beyond "手工業者の店が集まる" - craftsmen's SHOPS gathering, which is a shop and not a retained
household).

---

## `religion-and-death.html` fn-45 - the great temple's forecourt hosted the periodic market, the temple renting out the stall space

**CITED** - and the stall-renting half, which is the specific part, is attested.

URL: <https://www.his.ntnu.edu.tw/publish03/downloadfile.php?periodicalsPage=2&issue_id=39&paper_id=249>
- 林榮澤,「廟會」與中國的民間社會, 史耘 7 (2001), p. 83. Quote transcribed from the rendered page
image (PDF page 31 = printed p. 83), because the OCR text layer renders 租賃 as 租質.

Verbatim:

> 而隨著廟市流動的攤主，往往在一個廟會期結束後，再去趕另一個廟會，形成一批特殊的趕集商人，他們大都租賃廟中的房屋、地段，固定一段時間後回來設攤進行。

Translated from the Chinese by this project: "And the stall-holders who move with the temple
markets, once one fair's season has ended, go on to catch the next, forming a distinct body of
fair-going traders; most of them RENT the temple's buildings and plots of ground, and after a
fixed interval come back to set up their stalls."

The same paper establishes that the market is held at the temple itself, quoting 《東京夢華錄》
on the Xiangguo Temple (p. 57):

> 相國寺每月五次開放，百姓交易。

Translated: "The Xiangguo Temple opened five times a month for the common folk to trade."

**How it supports the claim.** The temple's own ground is let out to traders for their stalls,
and the temple is the market's site - both halves of the record's sentence. **Limit to state:**
the renting sentence is footnoted (n. 87) to 《民國社會大觀》 (Fujian renmin, 1991), a
Republican-era social survey, so the RENTING is attested for the Republican period within a
study of Qing fairs, while the fair-at-the-temple itself is attested from Tang through Qing in
the same paper's gazetteer quotations.

---

## `religion-and-death.html` fn-48 - the shrine at the shuikou, the water mouth

**CITED** for the water-mouth siting. Not for the earth god, and not for "the most strategic
feng shui position".

URL: <https://zh.wikipedia.org/wiki/%E5%AE%A2%E5%AE%B6%E8%A3%94%E8%87%BA%E7%81%A3%E4%BA%BA>
(zh.wikipedia, 客家裔臺灣人), section on deities. Read in full via the API.

Verbatim:

> 奉祀祂的廟宇，通常是建築在村落的水口。其中，較為有名者有：位在今日之新北市三芝區陳厝坑溪畔的水口民主公王宮。這座廟宇，即是由來自於汀州府永定縣的江氏家族，於乾隆二十五年（1760年）興建的。

Translated from the Chinese by this project: "The temples that enshrine him are usually built at
the village's water mouth (shuikou). Among the better known is the Shuikou Minzhu Gongwang
Temple, on the bank of the Chencuokeng stream in today's Sanzhi District, New Taipei City. This
temple was built in the 25th year of Qianlong (1760) by the Jiang family, who came from
Yongding county in Tingzhou prefecture."

**How it supports the claim.** A village's tutelary deity's hall is customarily sited AT the
shuikou, and a named surviving instance dates from 1760 - premodern, and on a stream bank,
which is the map-relevant geometry. So joining a village's tutelary shrine to the water mouth
is no longer the project's own invention. **What it does NOT support:** the deity here is
Minzhu Gongwang, a Hakka tutelary of Tingzhou and Zhangzhou origin, NOT the earth god (土地).
Nothing read calls the shrine's site "the most strategic feng shui position". Those two should
stay labeled as the project's own.

Supporting context found but not quotable at this assertion: the Huizhou water-mouth literature
(reached through the search `村口 水口 土地廟 風水 位置 傳統村落 選址 研究 社壇`) describes
temples, pavilions, dikes and bridges built at a village's water mouth, but the page that
carried it - <http://www.nopss.gov.cn/BIG5/n1/2019/1209/c417079-31497247.html>, fetched, a
project interim report - when read gives only village-by-village inventories
(在本村的風水塘邊上的土地神廟 - "the earth-god temple on the edge of this village's fengshui
pond") and no general statement about the shuikou.

---

## `religion-and-death.html` fn-49 - a village shrine's footprint

**STILL ABSENT.**

Searches:

| what | URL | outcome |
|---|---|---|
| ja.wikipedia 神社建築 | <https://ja.wikipedia.org/wiki/%E7%A5%9E%E7%A4%BE%E5%BB%BA%E7%AF%89> | Fetched in full via the API and grepped for 間 / 規模 / 尺 / 大きさ. It gives the STYLES and the relation of the parts - 拝殿は、一般に本殿よりも大きく建てられ ("the worship hall is generally built larger than the main sanctuary") - and no dimension for any of them. The one measured thing in the article is a component ritual, not a building. |
| ja.wikipedia 祠 | <https://ja.wikipedia.org/wiki/%E7%A5%A0> | Fetched. Describes the hokora as a small-scale hall with no resident priest; gives no size. |
| Meiji Jingu guide | <https://www.meijijingu.or.jp/guide/> | Fetched. Gives the great torii's dimensions only - a gate, not a hall, and a great urban shrine, not a village one. |

The relation "the worship hall is generally larger than the main sanctuary" is the one
size-shaped statement found anywhere, and it is relative, not absolute. The band stays this
project's calibration.

---

## `religion-and-death.html` fn-50 - the keidai's swept raked-gravel or flagged surface, and its upkeep

**STILL ABSENT.**

Searches run:

- `境内 玉砂利 掃き清める 参道 手入れ 神社 清浄 由来`
- `神社 境内 清掃 奉仕 氏子 当番 草取り 参道 掃き清め 慣習`

Candidates:

| candidate | URL | outcome |
|---|---|---|
| ja.wikipedia 参道 | <https://ja.wikipedia.org/wiki/%E5%8F%82%E9%81%93> | Fetched in full. Carries the tamajari and its MEANING (quoted under fn-54 below) - which is what the record already cites - and nothing on the precinct's surface, its raking, or who maintains it. |
| ja.wikipedia 境内 | (API extract) | Fetched. Grepped for 玉砂利 / 掃 / 砂利 / 舗装 / 白砂: **no hits**. The article defines the precinct as a legal and religious extent, exactly as the last pass reported. |
| soutoen.jp, 境内清掃の裏側 | <https://soutoen.jp/column/shrine-temple-garden/shrine-leaf-cleaning/> | Not fetched: a present-day landscaping contractor's marketing column about who cleans shrine grounds today. It would speak to modern upkeep by a paid contractor, which is not the assertion. |
| myouken.or.jp, 神主の最初の仕事 | <https://myouken.or.jp/post-3649/> | Not fetched: a shrine's own blog post about a priest's daily cleaning. Same objection - contemporary practice, self-published, and it would not carry the surface. |

The distinction that matters and that no page read closes: the tamajari's PURPOSE is attested;
the precinct's SURFACE and its sweeping regime are not.

---

## `religion-and-death.html` fn-52 - grain drying, market and opera on the plaza before the hall

**CITED** for grain drying and festival use. Not for market, not for opera, not for the earth-god
shrine.

URL: <https://zh.wikipedia.org/wiki/%E5%9B%B4%E9%BE%99%E5%B1%8B> (zh.wikipedia, 围龙屋), section
「禾坪、风水塘、伸手、水井和风水林」. Read in full via the API.

Verbatim:

> 在堂横屋门前有长方形的禾坪（或叫晒坪），可作晒谷物和其他农作物之用。亦可作为逢年过节和婚丧事宜的活动空间。禾坪的宽度十分讲究，一般与正屋高度一致

Translated from the Chinese by this project: "In front of the hall-and-wing house there is a
rectangular heping (also called a shaiping, a drying floor), which can be used for drying grain
and other crops. It can also serve as the space for activity at the turn of the year and at
festivals and for weddings and funerals. The width of the heping is a careful matter, generally
matching the height of the main hall."

And, on the pond that stands before it:

> 禾坪前有半月形的池塘，称为“风水塘”。池塘可用来蓄水防旱和养鱼灌溉，兼具一定的调节屋宇周围气温的作用以及蓄水灭火的功能。

Translated: "In front of the heping there is a half-moon pond, called the fengshui pond. The
pond can be used to store water against drought and to raise fish and to irrigate, and it also
serves somewhat to temper the air temperature around the building, and holds water for putting
out fire."

The same article states the arrangement is the rule rather than one instance, for the
hall-fronted forms:

> 半月形内环广场中间建有二堂或三堂式的祖祠，前面照例有禾坪、池塘。

Translated: "In the middle of the half-moon inner ring's plaza stands a two-hall or three-hall
ancestral shrine, and in front of it, as a matter of course, are the heping and the pond."

**How it supports the claim.** The open ground in front of the hall is a named, dimensioned
feature whose FIRST stated use is drying grain, and the pond before it is stated to serve
fengshui, irrigation and fire-fighting - the record's "read both as fengshui and as drainage and
fire protection", now with drying added. **Limits to state:** this is the Hakka 围龙屋 and its
kin (a walled house with the ancestral hall on its axis), not a free-standing Cantonese 祠堂;
and nothing in it gives a MARKET or OPERA on that ground, nor the same arrangement before a
village earth-god shrine. Those two stay the project's own.

A separate readable page confirms the assembly and the pond's purposes for the Guangfu hall
proper - <https://www.cssn.cn/ztzl/jzz/rwln/wh/whcy/202209/t20220923_5541419.shtml>
(中国社会科学网, 漫谈番禺广府祠堂), fetched:

> 祠堂最前端多为水域和广场，这既符合风水理念的设置，同时具备排水、防火、养鱼等实用价值。

Translated: "At the very front of the ancestral hall there is usually water and a plaza, which
both accords with fengshui thinking and has the practical value of drainage, fire protection and
fish-raising."

> 广场一方面可供族人聚会、举行各种庆典

Translated: "The plaza on the one hand serves for the clansmen to assemble and to hold
celebrations of various kinds."

That page too has no grain drying, no market and no opera.

---

## `religion-and-death.html` fn-54 - the path and the ground under each arch swept the whole length

**STILL ABSENT.**

The approach page carries the gravel and its meaning and nothing about sweeping, exactly as the
last pass found. URL: <https://ja.wikipedia.org/wiki/%E5%8F%82%E9%81%93>, fetched in full:

> また参道に敷かれる玉砂利は、玉が「たましい（魂）」「みたま（御霊）」「美しい」という意を持ち、砂利は「さざれ（細石）」の意を持ち、その場を清浄する意味を持っている。敷くことによってその場所を祓い清める意味があり

Translated from the Japanese by this project: "The tamajari laid on the approach - tama carrying
the senses of 'soul', 'august spirit' and 'beautiful', and jari the sense of 'sazare', small
stones - has the sense of purifying that place. Laying it carries the sense of purging and
cleansing that place."

That is the purification of the ground by the gravel, which the record already cites. It is not
sweeping, and it says nothing about the ground under an arch.

The nearest thing found to a sweeping statement is incidental and modern - ja.wikipedia 明治神宮,
on how the shrine forest is managed:

> これは参道を掃き清める際に集めた落ち葉を森に戻す以外は人為的な手を加えず、森の変化を自然淘汰に任せているためである。

Translated: "This is because, apart from returning to the forest the fallen leaves gathered when
sweeping the approach clean, no human hand is applied, and the forest's change is left to
natural selection."

It establishes that a shrine's approach IS swept - at a shrine founded in 1920, in a passage
about forest management, with no statement that the sweeping runs the whole length or reaches
under the gates. I report it as a pointer a session may judge too thin to cite; on the standard
this project uses ("a quote which actually backs up our assertion"), it does not back up the
assertion as written, and the note should stay an absence.

Searches run: `境内 玉砂利 掃き清める 参道 手入れ 神社 清浄 由来`;
`神社 境内 清掃 奉仕 氏子 当番 草取り 参道 掃き清め 慣習`. The second returned six pages, all
present-day blogs and contractor columns (hasegawa.jp on household god-shelves, ameblo and
yashiromusubi on volunteer cleaning, engeisyosinsya.com on weeding) - none fetched, because each
is a self-published modern how-to and none could speak to premodern practice.

---

## `religion-and-death.html` fn-57 - how wide the tended ground around a grave ran

**STILL ABSENT.**

Searches run:

- `墓地 面積 一基当たり 近世 埋葬 密度 発掘 調査 江戸 墓 平方メートル`
- ja.wikipedia API search: `両墓制 埋め墓 詣り墓`

Candidates and outcomes:

| candidate | URL | outcome |
|---|---|---|
| ja.wikipedia 両墓制 | <https://ja.wikipedia.org/wiki/%E4%B8%A1%E5%A2%93%E5%88%B6> | Fetched in full. Gives the burial ground's siting (人里離れた山林などが多く - "mostly in mountain forest away from human habitation"), its variety of markers, and the practice of carrying earth from the burial grave to the visiting grave. No distance, no cleared collar, no measure of the tended ground. |
| 墨田区みやこどり 33-2 | <https://www.city.sumida.lg.jp/…/miyakodori-33-2.pdf> | Downloaded with curl and read in full (see fn-65). Gives an excavated area and a grave count, and nothing about the ground kept clear around any grave. |
| かながわ考古学財団「近世の墓」 | <https://www.kaf2.org/josetsu/kinse/kinse_iko/kinse_grave> | Not fetched: the search context shows it describing grave-pit plan form and the reflection of status in the grave, i.e. the pit and the marker, which is the scale below the one the assertion asks about. |

The tomb-sweeping the record already cites establishes that the tomb itself is kept clear; how
far out that reaches is in nothing read, and the figure stays the project's own.

---

## `religion-and-death.html` fn-61 - how common a village's own graveyard was

**CITED** for prevalence and for the communal-per-settlement form. Not for the household
threshold, not for the grandfathering.

URL: <https://ja.wikipedia.org/wiki/%E4%B8%A1%E5%A2%93%E5%88%B6> (ja.wikipedia, 両墓制). Read in
full via the API.

On the form - verbatim:

> 集落ごとの共同墓地であることが多く、その埋葬地は家や年齢などによって区画分けされる場合もあれば、まったく決まりが無く空いた土地に埋めたり、古い墓地を掘り起こして追葬する場合など様々である。

Translated from the Japanese by this project: "It is most often a communal graveyard belonging to
each settlement, and its burial ground is in some cases divided into plots by household or by
age, while in others there is no rule at all and burial is made in whatever ground is free, or
an old grave is dug up and a further burial added."

On how common - verbatim:

> 民俗資料緊急調査による『都道府県民俗地図』によると調査時に確認された両墓制習俗を持つ集落は、滋賀県(60)、奈良県(59)、京都府(42)、兵庫県(39)など近畿地方に圧倒的に多い。その他の都道府県では三重県(45)、福井県(39)、静岡県(22)を除くと少ない。

Translated: "According to the *Prefectural Folklore Atlas* produced by the emergency survey of
folklore materials, the settlements confirmed at the time of survey as keeping the two-grave
custom were overwhelmingly concentrated in the Kinki region - Shiga (60), Nara (59), Kyoto (42),
Hyogo (39) - and outside those, apart from Mie (45), Fukui (39) and Shizuoka (22), few."

**How it supports the claim.** The graveyard the record draws - one ground held in common by a
settlement's own inhabitants - is stated to be the usual form, and the atlas gives a COUNT OF
SETTLEMENTS per prefecture, which is a measure of how common such patches were and comes from a
national survey rather than an impression. **Limits to state:** the counts are for the two-grave
custom specifically, not for a village graveyard in general; the unit counted is 集落 confirmed
at survey time in the 1950s-60s, so it is a floor rather than a historical rate; and the
settlements are concentrated in the Kinki region, which the same passage says plainly.

**Still not found:** whether a twelve- to fifteen-household hamlet kept one (no page read
attaches a household count to a graveyard), and the grandfathering of the disused ones.

A second per-settlement instance worth recording beside the Fukui one, from
<https://ja.wikipedia.org/wiki/%E8%8F%85%E6%B5%A6%E3%81%AE%E6%B9%96%E5%B2%B8%E9%9B%86%E8%90%BD>
(ja.wikipedia, 菅浦の湖岸集落), fetched in full:

> 菅浦は基本的に両墓制であり、門の内・外で明確に区切られ、遺体は西の門外の「サンマイ」という埋め墓に埋葬され、門内の寺院（阿弥陀寺・祇樹院）境内に「ハカワラ」と呼ばれる詣り墓（石碑群）が設けられている。

Translated: "Sugaura is fundamentally of the two-grave system, clearly divided by the inside and
outside of the gate: the body is buried in the burial grave called the 'sanmai' outside the west
gate, and the visiting graves called 'hakawara' - a group of stone monuments - are set within
the precincts of the temples inside the gate (Amidaji and Gijuin)."

That is the same geometry the record already cites from Fukui - the sanmai outside the
settlement's own gate, the visiting graves in temple precincts inside it - at a second named
settlement, and it is the map's own arrangement stated twice.

---

## `religion-and-death.html` fn-63 - Buck's survey and the ~2% of farm area under graves

**FOR THE GM.**

The document: **John Lossing Buck, *Land Utilization in China: A Study of 16,786 Farms in 168
Localities, and 38,256 Farm Families in Twenty-Two Provinces in China, 1929-1933*. Chicago:
University of Chicago Press, 1937. Three volumes (I text, II Atlas, III Statistics).** No DOI -
it is a 1937 book, so Unpaywall, OpenAlex and DOAJ have nothing to answer with, and that route
does not apply.

What was tried, and what blocked it:

1. **Internet Archive item `landutilizationi0000buck`** - <https://archive.org/details/landutilizationi0000buck>. A lending scan. Its full-text endpoint answers `{"error":"No hOCR or Abbyy file present"}`, so even the search-inside index does not exist for this item; reading it needs a logged-in borrow.
2. **Internet Archive advanced search**, `q=graves AND "land utilization in china"` over the full-text index: `numFound: 0`. The figure is not reachable through any Archive text index.
3. **HathiTrust catalog record 002351503** - <https://catalog.hathitrust.org/Record/002351503>. A 1937 US imprint is in copyright, so HathiTrust offers search-only, not full view.
4. **curl with a desktop browser user agent** on the Archive item: returns the details page, not the book text - the restriction is the licence, not the fetcher.
5. Web search (`Buck "Land Utilization in China" percentage of farm land occupied by graves grave mounds 2 percent`) returned only catalog records, bookseller listings and 1938 reviews (Nature, *AJAE*, *Annals*, JSTOR), none of which quotes a grave-area figure.

**What it would settle:** whether Buck's survey actually gives ~2% of farm area under graves,
and at what scale (all farm area, cultivated area, or crop area - the three differ materially in
Buck and the record's sentence says "ALL farm area"). **How much it would change:** the figure
is the record's only quantitative anchor for the Chinese contrast, and it is currently carried
as a guess. Confirming it converts a guess to a finding with a page number; finding a different
denominator would change the Chinese comparison the maps draw.

A person with a library card, or an Internet Archive account able to borrow the item, can settle
it in minutes. Volume I is the text volume; the land-utilization tables are in volume III.

**Note for whoever opens it:** the Chinese yizhong evidence recovered under fn-80 below gives an
independent, publicly readable measure of Chinese burial-ground area, so the record is no longer
wholly dependent on Buck for the Chinese side.

---

## `religion-and-death.html` fn-65 - an area per body, or a density of graves on the ground

**CITED.**

URL: <https://www.city.sumida.lg.jp/kosodate_kyouiku/tiiki_kyouiku_shien/bunkazai_hogo/maizoubunkazai/index.files/miyakodori-33-2.pdf>
- 墨田区 (Sumida City), 『みやこどり』 no. 33-2, the ward's buried-cultural-property bulletin,
on the graves of Honjo. Refused nothing; downloaded with curl and converted with `pdftotext`.

Verbatim:

> 墨田区における墓跡の発見は、昭和60 年に行われた普賢寺遺跡（東駒形一丁目）の発掘調査を端緒としています。普賢寺は浅草寺の末寺で東京大震災後の区画整理とともに転出した寺院です。調査面積はわずか40㎡でしたが10基の墓跡が見つかり、箱形木棺1基と早桶9基が掘り出されました。

Translated from the Japanese by this project: "The discovery of grave traces in Sumida ward began
with the 1985 excavation of the Fugenji site (Higashi-Komagata 1-chome). Fugenji was a branch
temple of Sensoji which moved away with the land readjustment after the Great Tokyo Earthquake.
The excavated area was a mere 40 m², yet traces of 10 graves were found, and one box-shaped
wooden coffin and nine barrel coffins were dug out."

And, on what that density means:

> 狭い同一墓域に数多くの墓が作られたことを意味しています。

Translated: "It means that a great many graves were made within one narrow burial ground."

**How it supports the claim.** Ten graves in 40 m² is a measured density of graves on the
ground - about 4 m² (roughly 43 sq ft) per grave - at an excavated Edo commoner temple
graveyard, which is exactly what the note says no excavation read reports. **Limits that must be
stated if this is used:** 40 m² is the TRENCH, not the graveyard, so this is a local density in
the densest part rather than a whole-ground figure; the graves are body burials in coffins, not
the packed urn plots the record's 10-20 sq ft band describes; and 43 sq ft sits above that band,
so the number corroborates the record's Chinese full-body figure rather than its Japanese urn
figure. The step from a grave's size to a plot's footing is no longer wholly unanchored, but the
anchor lands on the body-burial side.

A second, independent measure of the same kind, from the Chinese side, is under fn-80.

---

## `religion-and-death.html` fn-66 - a household is registered to the temple that buries it

**CITED.**

URL: <https://www.encyclopedia.com/religion/encyclopedias-almanacs-transcripts-and-maps/parish-danka-terauke-system-japan>
- "Parish (Danka, Terauke) System in Japan", from the *Encyclopedia of Religion* (Macmillan
Reference). Read by the default fetcher.

Verbatim, on the unit of affiliation:

> Temple membership was not an individual affair; rather, the unit of religious affiliation was the emergent unit of social organization, the "household" (_ie_).

Verbatim, on what the temple gave in return:

> For each household, the main benefit of membership was the funerary and ongoing memorial services that temples provided for all household members.

Verbatim, on the certification:

> Former Christians were certified by the local Buddhist temple and village officials as no longer Christians but as parish members of a Buddhist temple.

**How it supports the claim.** The record's parish-temple logic is stated in three parts: the
registered unit is the HOUSEHOLD, not the person; the registration is to a temple; and the
service the temple renders that household is its funerals and its continuing memorial rites. So
"a household is registered to the temple that buries it" is the encyclopedia's own sentence in
substance. **Limit to state:** this is the Tokugawa danka system, a state-mandated
anti-Christian registration apparatus, and the record's setting reaches the same arrangement by
a different route - worth a line, because the mechanism differs even where the outcome matches.

---

## `religion-and-death.html` fn-68 - the pyre set back from the road, reached by a minor way, never on a ceremonial approach

**CITED** for the setback and the siting rule. Not for the funeral path.

URL: <https://www.tama-100.or.jp/cmsfiles/contents/0000000/470/all.pdf> - 公益財団法人東京都
慰霊協会 / 東京の火葬場の history volume (6.9 MB PDF; downloaded with curl, text layer clean).
The passage quotes the Home Ministry's model detail standard issued with the 1884
「墓地及埋葬取締規則」.

Verbatim:

> 「火葬場は人家および人民の輻輳（ふくそう）※の地から 120 間（約 216ｍ）以上離し、風上とならない場所を選び、煙突を設け、臭煙を防ぐ装置を設け、周囲に塀を設ける。ただし林原野等で人家から離れた場所の時は除く」

Translated from the Japanese by this project: "A cremation ground shall be set at least 120 ken
(about 216 m) away from dwellings and from places of human congestion; a place that is not
upwind shall be chosen; a chimney shall be provided, a device to prevent foul smoke shall be
provided, and a wall shall be set around it. This is excepted where the place is in woodland or
open country away from dwellings."

The same volume glosses 輻輳 in its own footnote:

> ※物が１ヵ所に集中し混雑する様態をいう。

Translated: "The condition of things concentrating in one place and crowding."

And on the general siting:

> 東京府下は朱引外で、その他の地方は市街村落の外で人家からの遠隔地とし

Translated: "In Tokyo prefecture, outside the vermilion line; in other regions, outside the town
or village and remote from dwellings."

Earlier, on a pre-modern instance of the same logic, the same volume records the 1667
concentration of temple-precinct cremation grounds after the smoke reached the shogun:

> 寛文7年（1667年）には4代将軍徳川家綱が上野寛永寺へ墓参に赴いた際に、火葬の臭煙が及んだことが問題になって、浅草や下谷に散在していた20数ケ寺の境内火葬場を小塚原刑場近くに設けた幕府指定地へ集合移転させた

Translated: "In Kanbun 7 (1667), when the fourth shogun Tokugawa Ietsuna went to Kan'eiji at Ueno
to visit a grave, the foul smoke of cremation reaching him became a problem, and the
precinct cremation grounds of some twenty-odd temples scattered through Asakusa and Shitaya were
moved together to shogunate-designated ground laid out near the Kozukappara execution ground."

**How it supports the claim.** A stated, quotable rule requires a cremation ground to stand back
a fixed distance not only from dwellings but from places where people congregate and traffic
gathers - which is the road-frontage question the record reasons its way to - and to be walled
and not upwind. The 1667 removal is the premodern instance of the same hazard driving the same
decision, and it is the reason the record's "never between a temple and the road" has a real
mechanism behind it (the smoke reached a worshipper on his way to a grave). **Limits to state:**
the 216 m rule is Meiji 17 (1884), not premodern, and it measures from dwellings and crowded
ground rather than from a highway as such. **Still not found:** a minor funeral path serving the
pyre. Nothing read describes one.

---

## `religion-and-death.html` fn-72 - a cremation ground's cleared extent

**CITED.**

Same source: <https://www.tama-100.or.jp/cmsfiles/contents/0000000/470/all.pdf>. It gives site
areas for cremation grounds at several scales, which is the band the note says no survey read
supplies.

A village-scale permanent one, verbatim:

> 敷地は 42 坪で、建物は平家木造モルタル造であった。火葬炉は 1 基で燃料は薪を使用していた。

Translated from the Japanese by this project: "The site was 42 tsubo, and the building was a
single-storey wood-and-mortar structure. There was one cremation furnace and the fuel used was
firewood."

A smaller one, verbatim:

> 氷川村火葬場は東京都西多摩郡氷川村（現西多摩郡奥多摩町氷川）にあったもので、建設年は大正 11 年 12 月 13 日、敷地は 10 坪 5 合（34.65 ㎡）、建物は 6 坪（19.88 ㎡）の簡易な火葬場であった。

Translated: "The Hikawa village cremation ground stood in Hikawa village, Nishitama district,
Tokyo (now Hikawa, Okutama town, Nishitama district); its year of construction was 13 December
Taisho 11, the site was 10 tsubo 5 go (34.65 m²), and the building was a simple cremation ground
of 6 tsubo (19.88 m²)."

An emergency one made by renting ground, verbatim:

> 急いで川崎村宗禅寺の所有林武蔵野708 番地の40 坪を借りうけ、臨時の火葬場を作った

Translated: "In haste they rented 40 tsubo of Musashino lot 708, woodland owned by Sozenji temple
in Kawasaki village, and made a temporary cremation ground."

And the large urban one, verbatim:

> 敷地は 600 坪（1,980 ㎡）、火葬室は木造平屋建 36 坪（118.8 ㎡）で、木造平屋建 12 坪（39.6 ㎡）の附属建物があった。

Translated: "The site was 600 tsubo (1,980 m²), the cremation room a single-storey wooden
building of 36 tsubo (118.8 m²), with an attached single-storey wooden building of 12 tsubo
(39.6 m²)."

The volume also defines the open-air form the record describes, in its own glossary:

> 野焼き施設（のやきしせつ） 上屋を持たずに、石で組んだ簡易な炉で薪を組んで燃やす火葬場。野天火葬場。

Translated: "Open-burning facility (noyaki shisetsu): a cremation ground with no superstructure,
burning stacked firewood in a simple furnace built up of stone. An open-air cremation ground."

And records the per-settlement form the maps draw:

> また新潟では集落ごとの野焼き火葬場を葬礼場（ソウレバ）昇魂場（ショウコンジョウ）と呼んでおり

Translated: "And in Niigata the open-air cremation grounds of each settlement were called
soureba (funeral-rite ground) and shokonjo (soul-ascending ground)."

**How it supports the claim.** Village and town cremation grounds are recorded at 10.5 to 42
tsubo (35 to 139 m², roughly 19 to 38 ft across if square) and a rented emergency plot at 40
tsubo; the largest Edo-descended urban one at 600 tsubo (1,980 m², about 145 ft square). The
record's drawn band - 30 to 80 ft at village and town scale, 80 to 160 ft at city scale - sits
squarely across those. The stone-built, roofless, firewood-stacked form is defined in the same
volume, which is the record's pyre description. **Limits to state:** the dated examples are
Meiji through Showa municipal facilities, not Edo; the 900-tsubo Yoyogi figure the record
already carries from the Musashi gazetteer remains its one premodern extent; and the Niigata
per-settlement naming is a naming, not a measurement.

---

## `religion-and-death.html` fn-75 - the size of a pauper bone mound

**STILL ABSENT.**

Searches run:

- ja.wikipedia API search: `無縁塚 万人塚 骨` - returned 豊臣秀次, 善光寺, クジラ, 弥生時代, 歴史文化ライブラリー, もののけ姫. None is about a pauper bone mound; the Hidetsugu entry is a named execution mound and the Zenkoji entry a segaki rite. **Not one candidate was worth fetching**, and I say so rather than pad the list.
- `小塚原 刑場 火葬場 坪 面積 規模 江戸 回向院 埋葬 20万人` - returned the Kozukappara material used under fn-78; none of it gives a bone mound a size.
- `墓地 面積 一基当たり 近世 埋葬 密度 発掘 調査 江戸 墓 平方メートル` - the excavation material used under fn-65; grave pits, not mounds.

Nothing read gives a pauper bone mound a diameter, a height or a footprint. The 10 to 30 ft band
stays the project's own.

---

## `religion-and-death.html` fn-76 - the base of Kyoto's ear mound

**CITED.**

URL: <https://www.kyototuu.jp/Sightseeing/HistorySpotMimizuka.html> (京都通百科事典, 耳塚). Read
by the default fetcher.

Verbatim:

> 高さ４間（約７.２m）、石塔の高さ５間（約９m）、横幅３０間（約４９m）

Translated from the Japanese by this project: "Height 4 ken (about 7.2 m); the stone pagoda's
height 5 ken (about 9 m); width across 30 ken (about 49 m)."

**How it supports the claim.** The note says the encyclopedia article gives a height and no
measure of the base. This page gives the WIDTH ACROSS - 30 ken, about 49 m - beside the height,
which is the base dimension the record was guessing at. A monumental mound about 49 m across and
7.2 m high, carrying a 9 m five-ring pagoda, is a measured anchor rather than a guess.

**Limits to state:** 京都通百科事典 is a regional encyclopedia site, not a primary record or a
scholarly work, and it does not name its own source for the figures. Prefer, if one can be had,
the explanatory tablet standing beside the mound (several pages report one) or the national
historic-site designation record - 耳塚 is designated with 馬塚 as 「方広寺石塁および石塔」
(1969), so the designation file would carry the surveyed dimensions. I could not open the
designation file itself. Two other pages carrying the mound
(<https://kyotofukoh.jp/report35.html>, <https://www.kanshundo.co.jp/museum/kyotokanko/higashiyama/05mimizuka/index.htm>)
were not fetched, one host having already been read for this figure.

Checked and negative: <https://ja.wikipedia.org/wiki/%E8%80%B3%E5%A1%9A> (ja.wikipedia, 耳塚) was
fetched in full and gives the form -
「古墳状の盛り土をした上に五輪塔が建てられ周囲は石柵で囲まれている」 ("a five-ring pagoda is
built on a tumulus-like earthen mound, and the surround is enclosed by a stone fence") - but no
number of any kind except the count of the buried.

---

## `religion-and-death.html` fn-78 - a mound at the great Edo execution ground

**STILL ABSENT**, and now negatively confirmed on the fullest page.

URL read: <https://ja.wikipedia.org/wiki/%E5%B0%8F%E5%A1%9A%E5%8E%9F%E5%88%91%E5%A0%B4>
(ja.wikipedia, 小塚原刑場), reached by search and read. It corroborates both figures the record
already carries:

> 小塚原の刑場は、間口60間（108m）、奥行30間余（54m）、約1,800坪の敷地でした。

Translated from the Japanese by this project: "The Kozukappara execution ground was a site of 60
ken frontage (108 m) and rather more than 30 ken depth (54 m), about 1,800 tsubo."

> 明治初年に廃止されるまで、ここで処刑された人は約20万人と云われています。

Translated: "Until it was abolished in the first year of Meiji, those executed here are said to
have numbered about 200,000."

And it adds the figure the record did not have - **about 1,800 tsubo** for the plot, which is the
area the record's 108 m × 54 m implies and worth carrying beside it.

What the page does NOT carry: any mound. It describes what was done on the ground - 火罪・磔・
獄門 (burning, crucifixion, gibbeting) - and the burial of the executed and of unclaimed dead,
and the founding of the Jogyodo hall next to it in 1667 to bury and memorialize them. No mound of
bones, of any size, is described there or on
<https://tesshow.jp/arakawa/temple_ssenju_ekoin.html> (a temple-listing page whose Kozukappara
entry was read through search context and gives the same founding narrative). The record's own
sentence - "no page read describes one raised there" - is confirmed rather than overturned, and
the reasoning behind it (cremated bone takes almost no volume) is unaffected.

---

## `religion-and-death.html` fn-80 - area per body, the acreage ladder, and the Chinese full-body multiple

**CITED** for the Chinese full-body side. The Japanese acreage ladder remains the project's own
arithmetic.

URL: <https://www.sinoss.net/uploadfile/2010/1130/6012.pdf> - 冯贤亮,「坟茔义冢：明清江南的民众
生活与环境保护」(华东师范大学历史系). An open scholarly PDF; downloaded with curl, text layer
clean. This is the collection on the Chinese charity graveyard that the last pass found serving
only a table of contents - this copy serves the whole paper.

The key measurement, verbatim - a Kangxi-era endowment recorded in the Zhenze county gazetteer:

> 康熙九年六月十二日，太湖水决，平地丈余，浮尸盈万，额驸过而伤之，乃捐买北门外三里桥西位字圩田 4 亩，设义冢，埋棺 573

Translated from the Chinese by this project: "On the twelfth day of the sixth month of Kangxi 9,
the waters of Lake Tai burst, standing more than a zhang deep over the flat land, and floating
corpses filled the ten thousands; the imperial son-in-law passed by and was grieved at it, and so
donated the purchase of 4 mu of field in the Wei-character polder west of Sanli bridge outside
the north gate, established a charity graveyard, and buried 573 coffins there."

A second of the same kind, verbatim:

> 亩，设义冢，埋棺 244，捐买简进字圩田 7 亩，为祭田。

Translated: "…mu, established a charity graveyard, buried 244 coffins, and donated the purchase
of 7 mu of field in the Jianjin-character polder as sacrificial land."

And the scale of such grounds, verbatim:

> 崇明县义冢，除了城区东北部的 11 间殡舍、原置的 11 处义冢（共约 60 亩）外，还有新增的 28 座义冢（共约 123 亩

Translated: "The charity graveyards of Chongming county: besides the 11 mortuary sheds in the
north-east of the walled town and the 11 originally established charity graveyards (about 60 mu
in all), there were also 28 newly added charity graveyards (about 123 mu in all…"

> 每处义冢从 3 分到 10 亩不等

Translated: "Each charity graveyard ranged from 3 fen to 10 mu."

The paper's own table of Zhenze county's Qing charity graveyards lists individual areas of 1.3,
2, 1.28, 2.3, 3, 6.4, 11, 12.8, 19.3 and 19.7 mu.

**How it supports the claim.** 4 mu (about 2,667 m²) holding 573 coffins is about 4.7 m² - some
50 sq ft - per full-body grave; the 244-coffin entry gives about 5.5 m² (59 sq ft) on the same
reading. The record's Chinese full-body figure is "four to six times" its 10 to 20 sq ft urn
plot, i.e. 40 to 120 sq ft - and the measured 50 to 59 sq ft falls inside that band. So the
multiple is no longer arithmetic on nothing: two Qing endowments measure it. **Limits to state:**
these are charity graveyards for the unclaimed and the drowned, packed more tightly than a family
grave sited by fengshui would be, and they are Jiangnan, where the paper says land pressure was
acute (江南因土地利用一直十分紧张); mu is taken at the standard 666.7 m², which the gazetteer does
not itself state. **What remains the project's own:** the Japanese acreage ladder (0.15-0.30 acre
for a village district, 0.25-0.75 for a town, 0.75-2 for a city). Nothing read gives a Japanese
burial ground an acreage against a population served.

---

## `religion-and-death.html` fn-81 - a wayside shrine stood at a threshold: a landing, a crossing, a gate, a well

**CITED** for landing, crossing and gate. Not for the well.

URL: <https://ja.wikipedia.org/wiki/%E9%81%93%E7%A5%96%E7%A5%9E> (ja.wikipedia, 道祖神). Read by
the default fetcher.

Verbatim:

> 村落の出入口、峠、辻、橋のたもとなど、空間的・社会的な境界に祀られ

Translated from the Japanese by this project: "Enshrined at spatial and social boundaries - a
village's entrance and exit, a mountain pass, a crossroads, the foot of a bridge, and the like."

> 集落の境や村の中心、村内と村外の境界や道の辻、三叉路などに主に石碑や石像の形態で祀られる神で

Translated: "A deity enshrined mainly in the form of a stone monument or stone image at a
settlement's boundary or a village's centre, at the border between inside and outside the
village, at a road crossing, at a three-way junction and the like."

> 村境、峠などの路傍にあって外来の疫病や悪霊を防ぐ神である

Translated: "It is a deity standing by the roadside at a village boundary or a pass, warding off
epidemics and evil spirits coming from outside."

**How it supports the claim.** The record's "exactly at a threshold" is the source's own
organizing idea - 空間的・社会的な境界, spatial and social boundary - and three of the record's
four instances are named outright: a bridge's foot (the landing the record wants for a wharf
shrine), a crossroads (the crossing), and a village's entrance and exit (the gate). **What it
does NOT support:** a well. No page read puts a wayside shrine at a wellhead. Either drop the
well from the list or keep it separately labeled.

---

## `religion-and-death.html` fn-82 - teahouses, eateries and sweet-sellers at the gate

**CITED** for eating and drinking establishments at the gate, and for sweets sold at teahouses on
the pilgrim road. The sweet-seller AT THE GATE is not directly attested.

URL: <https://kotobank.jp/word/%E9%96%80%E5%89%8D%E7%94%BA-142614>, ブリタニカ国際大百科事典's
entry on 門前町, verbatim:

> 祭礼市が常設化し、それに飲食施設などが加わってできた経済集落

Translated from the Japanese by this project: "An economic settlement formed when the festival
market became permanent and eating-and-drinking establishments and the like were added to it."

URL: <https://ja.wikipedia.org/wiki/%E5%9C%9F%E7%94%A3%E8%8F%93%E5%AD%90> (ja.wikipedia, 土産菓子),
verbatim:

> 江戸時代に入ると街道での往来が増えていき、途中の茶店において売られていた菓子などが、様々な旅人からの話を元に独自の発展をしていった。また旅人が口伝えなどで、旅先において売られていた菓子の存在を広めていったことが、地方において菓子が発展する契機として最も大きい。

Translated: "Once the Edo period came in, traffic on the highways increased, and the sweets and
such that were sold at the teahouses along the way developed in their own directions out of what
various travelers said of them. And that travelers spread by word of mouth the existence of the
sweets sold at the places they traveled to was the greatest occasion for sweets developing in the
provinces."

**How it supports the claim.** Two of the record's three named trades are now attested in the
right economy: eating-and-drinking establishments are named as a constituent of the gate town
itself, and teahouses selling sweets are named as the Edo-period travel-and-pilgrimage trade that
developed the regional confection. **What is still an extension:** nobody read puts a
SWEET-SELLER at the temple gate specifically - the Wikipedia passage puts the teahouse 街道 (on
the highway), and the Britannica passage puts 飲食施設 at the gate without naming the sweet.
Narrowing the record's phrase to "eating houses at the gate, and teahouses selling sweets along
the pilgrim road" would put the whole sentence on quoted ground.

Checked and largely negative: <https://www.touken-world.jp/tips/112205/>
(刀剣ワールド, 時代によって変化する門前町) was fetched; its only shop list -
「参道に茶店が建ち並ぶようになり、伝統工芸品を扱う商店などが増えました」 ("teahouses came to
stand in rows along the approach, and shops dealing in traditional crafts increased") - is placed
in the Meiji-Taisho era, which is the same railway-era framing the last pass met.

---

## `religion-and-death.html` fn-83 - a souvenir trade at a PREMODERN gate

**CITED.** This is the note that changes most.

URL: <https://kotobank.jp/word/%E5%9C%9F%E7%94%A3-583333> (Kotobank, 土産), the
改訂新版 世界大百科事典 entry, signed 岩本通弥. Read by curl with a browser user agent, full text.

Verbatim:

> 熊野などでは近世になると修験者が半僧半俗化しみやげ物を販売するようになり，のちに需要が拡大すると専業のみやげ物屋も生まれて門前町を形成した。

Translated from the Japanese by this project: "At Kumano and elsewhere, in the early modern
period the shugenja became half-monk and half-layman and came to sell souvenir goods; later, as
demand expanded, specialist souvenir shops also came into being, and formed a gate town."

The same entry dates the whole practice and names what was sold:

> みやげの習慣が今日のように盛行するのは，その前提となる旅や交通の発達を抜きには考えられず，参勤交代の制が確立し街道が整備され，また先達（せんだつ）や御師（おし）の活躍で庶民の間にも社寺参詣の旅が普及する近世中期以降のことと思われる。

Translated: "That the souvenir custom flourished as it does today cannot be thought of apart from
the development of travel and transport that is its precondition, and is to be taken as a matter
of the middle of the early modern period onward, when the alternate-attendance system was
established and the highways were made up, and when, through the activity of pilgrimage guides
and oshi, journeys of temple and shrine pilgrimage spread among the common population."

> これにはもっぱら御札や御守をはじめ縁起物の人形や玩具・絵草紙類また神薬などが用いられた。

Translated: "For these, talismans and amulets above all were used, and lucky dolls and toys and
picture books and sacred medicines."

**How it supports the claim.** A signed encyclopedia entry places specialist souvenir shops at a
temple gate in the 近世 - the Edo period - and says they formed the gate town, which is precisely
what the record calls "this record's own extension" resting on nothing read. It also dates the
spread to mid-Edo, names the goods, and names the mechanism (pilgrimage guides and oshi bringing
commoner pilgrimage). The record's souvenir row at a premodern gate is a finding now, not an
extension.

**On the companion note about the word *meibutsu*:** the same Kotobank cluster gives
名産 ("the noted product of a place, the superior thing produced there") and dates the custom of
seeking out a place's 名産 as a gift to the late Muromachi -
「みやげに土産の字を当てるようになったのは室町末以降のこととされ，このころより土地の名産を強いて求めて贈る風が生まれた」
("it is held that the characters 土産 came to be applied to miyage from the end of the Muromachi
onward, and from about this time the fashion arose of going out of one's way to seek a place's
noted product and give it"). That supports the CONCEPT the record means by meibutsu, in the right
period, though the record should check whether it wants 名産 or 名物, which the Kotobank 名物 entry
shows was in Edo primarily a tea-utensil connoisseurship term (大名物・名物・中興名物).

---

## `religion-and-death.html` fn-84 - the pauper ossuary as a low earthen mound with one weathered stupa

**STILL ABSENT.**

Searches run:

- ja.wikipedia API search: `無縁塚 万人塚 骨` - the six results (豊臣秀次, 善光寺, クジラ,
  弥生時代, 歴史文化ライブラリー, もののけ姫) contain no pauper ossuary. Not fetched, for that
  reason.
- `義冢 漏澤園 面積 畝 清代 城外 埋葬 貧民 研究` - returned the Chinese charity-graveyard
  literature. The one paper fetched and read in full
  (<https://www.sinoss.net/uploadfile/2010/1130/6012.pdf>, see fn-80) describes the 义冢 and the
  漏泽园 as ground, with mortuary SHEDS (殡舍) attached at Chongming, and nowhere as a mound with a
  stupa on it.
- `小塚原 刑場 火葬場 坪 面積 規模 江戸 回向院 埋葬 20万人` - the Kozukappara material, which
  records burial of the unclaimed dead and a memorial HALL (常行堂, 1667) founded beside the
  ground, not a mound and not a stupa.

So the two things the drawn form asserts - that the pauper ossuary is a low earthen MOUND, and
that it carries ONE weathered stupa - are each unattested in anything read. Two adjacent facts
that do NOT close it, and that a session should not mistake for closing it: the Mimizuka IS an
earthen mound carrying a stone pagoda (fn-76), but it is a monumental war memorial, not a pauper
ossuary; and the Chinese charity graveyards had buildings beside them, but sheds for coffins, not
reliquary monuments. The drawn form stays general reading.

---

## Notes for the session that rewrites these entries

1. **Three sources here carry more than the note they were found for**, and are worth registering
   once and citing several times: the Tokyo cremation-ground history
   (`tama-100.or.jp/.../all.pdf`) covers fn-68 and fn-72 and glosses the open-air pyre form; the
   Jiangnan charity-graveyard paper (`sinoss.net/.../6012.pdf`) covers fn-80 and the Chinese half
   of fn-65 and bears on fn-61's China contrast; the Lin Rong-tse temple-fair paper covers fn-44
   and fn-45 and quotes the Qing gazetteers directly.
2. **Two quotes must be taken from the page IMAGE, not from a text layer.** The Lin Rong-tse PDF
   is a scan whose OCR garbles characters (it renders 租賃 as 租質 and 罷黜百家 as 罷旦出百家). Both
   quotes given above under fn-44 and fn-45 were transcribed from `pdftoppm` renders of printed
   pages 57 and 83. Anyone re-checking them should render the page rather than grep the text.
3. **Five of these are partial in a way that changes the sentence, not just its footnote** -
   fn-39 (planks yes, gravel no), fn-48 (the water mouth yes, the earth god no), fn-52 (drying yes,
   market and opera no), fn-81 (the well is the odd one out), fn-82 (the sweet-seller is not at the
   gate). Each needs the assertion narrowed to what is quoted, not just a key attached.
4. **fn-78 and fn-84 are now negatively confirmed** rather than merely unsearched: the fullest
   page on the Kozukappara ground was read and describes no mound. That is worth saying in the
   absence note, because it is a stronger statement than "nothing was found".
5. **`source-applicability` has not been run** on any of these works. Every one of them needs it
   before its numbers reach a map - particularly the tama-100 volume (its measured cremation
   grounds are Meiji to Showa municipal facilities, offered here as a scale anchor for a
   premodern setting) and the Sumida bulletin (a 40 m² trench standing in for a graveyard's
   density).
