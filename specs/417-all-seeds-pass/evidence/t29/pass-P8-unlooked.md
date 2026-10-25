# Feature 417 T36: search pass on eight claims the record never researched

Of the eight claims, two are engine tolerances no source could speak to (3, 5) and none is cleanly attested. The record argues against two of them: the byre rule (6) and the master's house inside the martial hall compound (4b). The rest are attested only for a narrower case, or the record is silent.

Archived pages are cited by the URL the archive holds them under, at `/diagram/.specify/source-archive/<hash>/…/text.txt`. Nothing was edited. Ledger outcomes are recorded for the pages that did not bear: the Kurashiki PDF and the MLIT PDF (unreadable), the Matsushiro guide page, en.wikipedia Matsushiro, the Iwadeyama 有備館 jawiki (rejected: the wrong school), the Tonami databank, the Pingyao baike page and the bjd article.

## 1. plan.py::SitePlan.head_deg — "turned away from the brook's flank"

**The prompt describes this claim wrongly.** `head_deg` is not about which way houses face. It is the bearing of the **head race** (the ditch taking water off the brook) as it leaves the intake. The race turns off the land's fall by `OFFTAKE_DEG`, toward the side away from the flank the brook keeps running down, "so that the two never run alongside one another." This section researches that claim.

- **0059 originals** (shimane-toshuko-lecture, https://zoukou.life.shimane-u.ac.jp/ruraleng/shisetsuken/12kougisiryou/15.pdf). The evidence is a **modern** engineering lecture; nothing in it describes practice before 1868.
  「これには片岸取入と両岸取入がある．受益地が片岸にある場合は受益地側の取入に良好な地点に取入口を設ける．…渓流河川では片岸取入にする．急流河川においても片岸取入とする．緩流河川でも片岸取入を原則とする．」
  — "There are one-bank and two-bank intakes. Where the land served lies on one bank, the intake is set at a good point on that land's side… On torrents, one-bank intake; on steep rivers, one-bank intake; on gentle rivers too, one-bank intake is the principle." (translation)
- The 0059 passage quoting a treatise of 1902 (https://www.maff.go.jp/j/nousin/attach/pdf/tousyukou-3.pdf) says where the headworks stand, not which way the race turns, so it does not bear.

**ATTESTED ONLY FOR** the intake standing on the bank of the land it serves, and only from a modern engineering lecture, not premodern practice. Once the intake is on the fan's bank and the brook runs on down the far flank, the race turning away from the brook follows from the geometry; no source states it as a rule. Read the "turn away" as engine geometry, not a world claim.

## 2. plan.py::SEAT_STANDOFF — "standoff from the field" (12 ft)

The constant is the gap from the field's edge to the near edge of the band the houses are seated in, not to a house wall.

- **0247 notes** (wigmore-1892-servitudes, https://archive.org/stream/materialsforstu00japagoog/materialsforstu00japagoog_djvu.txt). Mino, Ono district; customs of the Tokugawa period as compiled in 1892. The page is in English:
  「No such proceedings are necessary in case of a house in a village, but a house must stand back about 3 feet from the」「of a road or of cultivated land ; this is called」「shade- withdrawal.」
- **Archived** http://www.m-sugi.com/75/m-sugi_75_otsubo.htm (Ōtsubo, a modern essay on traditional farmhouses in the Chiba hills; undated practice):
  「谷の底辺に最大限に水田を取った。さらに、畑での自給自足用の農作物が水はけの良い、水田より少し高い位置に必要になる。そして、母屋より日当たりが良い家の前の斜面に来ることになり、家屋はその後ろの高い位置に来る。」
  — "They took as much paddy as possible on the valley floor. The dry-field crops for home use needed well-drained ground a little above the paddy, so they came on the sunny slope in front of the house, and the house stood higher, behind them." (translation)

**ATTESTED ONLY FOR** a 3 ft setback from cultivated land in one Mino district (1892 compilation of Tokugawa custom). The Chiba case has a dry-field strip between paddy and house, but gives no distance. No source gives 12 ft. One Japanese web query found nothing.

## 3. wood_rank.py — "the median house"

**NOT-ABOUT-THE-WORLD.** 0077 says a wood stands "below the houses" without saying which house. Choosing the median house's height rather than the lowest one is how the engine turns that phrase into a number when the houses stand at different heights. No source could prefer one over the other, so nothing was searched.

## 4. castle_civic.py — "martial hall compound" (130 × 124 ft; hall across the north; master's house and archery lane south of it)

The claim has three parts, and each comes out differently.

**(a) A hall with an archery ground inside a state school compound.**
- **Archived** jawiki 文武学校 (Matsushiro; school opened 1855):
  「剣術所 柔術所 槍術所 弓術所 御役所 番所 総敷地3089m2（934坪）、建坪1500m2（455坪）。」
  — "Sword hall, jujutsu hall, spear hall, archery hall, office, guardhouse. Total site 3,089 m² (934 tsubo), built area 1,500 m² (455 tsubo)." (translation)
- **Archived** jawiki 弘道館 (Mito, 1841):
  「武館（北側の撃剣場、間の槍術道場、南の居合・柔術・長刀などの稽古場、計三棟からなる）を、南庭に武術訓練のための対試場を配している。」
  — "The martial wing (three buildings: the fencing hall on the north, the spear hall between, and the practice hall for iai, jujutsu, naginata and so on to the south), with a bout ground for martial training in the south garden." (translation)

**(b) The master's house.**
- **0165 originals** (kotobank-machidojo, https://kotobank.jp/word/町道場-137003):
  「日本の町道場の歴史は，江戸時代，流派武芸が盛んになり，師範の家で練習場を持つようになったころからの伝統がある。」
  — "The private dojo's tradition dates from the Edo period, when masters came to keep practice halls at their own houses." (translation)

  A practice hall at the master's own house is the form of the **private** dojo. For a state school, the Mito Kodokan site (https://kodokan-ibaraki.jp/about/, archived) has the domain taking masters into its service (「剣客を召し抱えて師範とし」), and names no master's house in the compound.

**(c) The size and the hall across the north.**
- **0165 originals** (hagi-meirinkan-guide, https://www.city.hagi.lg.jp/site/meiringakusha/annaizu.html):
  「桁行37.8ｍ、梁間10.8ｍの南北に長い建物である」 — "a building long north to south, 37.8 m along the ridge and 10.8 m across" (translation).
  The same page: 「敷地面積は約10万5千平方メートルあり」 — "the site is about 105,000 m²" (translation).
- At Mito the martial wing lies south of the administrative hall.
- The only hall standing at the north of its own ground is the Chinese one, at Chongming (0165).

**ATTESTED ONLY FOR** practice halls with an archery hall or bout ground inside a domain school compound (Matsushiro 1855, Mito 1841). The master's house inside a state compound is **NOT ATTESTED**: housing the hall with the master is the private dojo's form. The 130 × 124 ft size is **SILENT**. The Hagi hall runs north–south inside a far larger school ground, so "the hall across its north" has no Japanese support.

## 5. cover.py::_commons_keep — "off the treads" (4 ft verge)

**NOT-ABOUT-THE-WORLD.** The code comment says this margin was set so the trunk-versus-tread check and the planting code read the same number. It is a rule about collisions in the drawing. 0196's "curb within about 8 ft of the tread" is the engine's own seating rule, not evidence. The archive's only hits for 路肩 (road shoulder) are modern engineering standards (Shanghai, Aomori), which cannot count.

## 6. byres.py::household_byre_form — "household forms only on a nucleated seating"

The code draws no byre at a dispersed farm by any route (`homesteads/stages.py`: "no stall is laid beside a grove farm's house, so its lot keeps no beast").

- **0048 notes** (kotobank-umaya): the inner stable 「全国的には主屋の土間の一角を占める内厩が広く行われた」 — "nationally the inner stable, taking a corner of the main house's earth-floored work space, was widely practiced" (translation). The article gives no date and does not limit this to nucleated villages.
- **Archived** https://suido-ishizue.jp/nihon/04/07.html (Isawa plain, a dispersed settlement; a description of the surviving landscape, undated):
  「エグネ、キヅマに囲まれた屋敷には、母屋のほか、厩（馬小屋）、…が配置されている。」「この地方の厩は、母屋と屋根のついた渡り廊下のような棟をつないで、家畜の管理がしやすいように工夫されている。」
  — "The homestead within its grove and firewood wall holds, besides the main house, a stable (horse shed)… This district's stables are joined to the main house by a roofed, corridor-like wing, to make the animals easy to tend." (translation)
  The same page: 「散居集落とは、民家が点々と散在する集落のことで…砺波平野や出雲平野とともに」 — "A dispersed settlement is one whose houses stand scattered… [Isawa ranks] with the Tonami and Izumo plains." (translation)
- **Archived** https://www.jstage.jst.go.jp/article/jjhg1948/29/5/29_5_451/_article/-char/ja/ (Iwate farmsteads; 1974 data, quoting Murata on Shiwa):
  「馬屋,小屋等を建設するが……この際にも鉤形配置の方向がとられ……屋根は接するやうにして曲家の機能を持たせる。」
  — "When they build a stable or shed… they keep the hooked layout… with the roofs touching, to give it the function of an L-shaped house." (translation)

**NOT ATTESTED.** The evidence points the other way: dispersed farms on the Isawa fan kept a stable joined to the house. Caveat: both sources are modern descriptions of traditional farmsteads, and neither dates its evidence before 1868.

## 7. docs/buildings.md — "kura granary door on the apron" (where carts stand)

- **Archived** https://www.nta.go.jp/about/organization/ntc/sozei/tokubetsu/h14shiryoukan/01.htm (Edo period):
  「村では年貢米を俵に詰め、郷蔵に一時保管します。決められた期日になると、近距離の場合は人馬をつかって御蔵へ送ります。」
  — "The village bagged its tax rice in bales and kept it for a time in the village store; on the set day, over short distances, it was sent to the government storehouse by men and horses." (translation)
- **Archived** http://jds.cssn.cn/xscg/xslw/201605/t20160506_5252169.shtml (Qing Beijing capital granaries):
  「届时仓前车水马龙，人头攒动。为了运输与发放便利，领米时各旗多以佐领为单位雇觅民人车辆，凭米票到指定仓房领米。」
  — "On those days the front of the granary was thronged with carts and horses. For ease of carrying and issue, each banner mostly hired civilians' carts company by company and drew its rice at the assigned granary on its rice tickets." (translation)
- **Archived** https://kotobank.jp/word/%E8%94%B5%E5%B1%8B%E6%95%B7-58201: 「浅草御蔵では戸口(戸前（こまえ）と呼ぶ)を2～5ヵ所つけた大きな蔵が54棟も並び」 — "at Asakusa, 54 great storehouses stood in rows, each with 2-5 doors (tomae)" (translation). It says nothing of which face the doors were on.

**Door on the loading apron: SILENT.** No page says which face of an office granary carried its door.

**Carts: ATTESTED ONLY FOR** Qing capital granaries, where carts stood before the granary. For Japan the evidence points against carts: short-haul tax rice went by men and horses.

## 8. docs/buildings.md — "cell kept well under the barracks"

- **Archived** https://kotobank.jp/word/%E9%99%A3%E5%B1%8B-82659 (Edo intendants' offices). This is the one passage that puts both buildings in the same office:
  「代官陣屋は…手付(てづき)や手代(てだい)の官舎である小屋や長屋、牢屋(ろうや)を総称する。」
  — "An intendant's office comprises… the huts and rowhouses that lodged the officials' assistants, and the jail." (translation)
- **Archived** https://kotobank.jp/word/%E7%89%A2%E5%B1%8B-152554: 「法廷に呼出された囚を入れる仮牢が，奉行所内に設けられていた。」 — "a temporary cell for prisoners called before the court was kept inside the magistrate's office" (translation). No size is given.
- **0096 originals** (the 伝馬町牢屋敷 jawiki article): cell rooms of 15-18 mats (「奥揚屋は1部屋あたり広さ3間の部屋が3部屋（18畳相当）」) and Osaka's 6-mat cell. These are rooms of the city jails, not a magistracy's temporary cell.
- **0097 originals**: Omori's gate rowhouse 「幅約4m、総長33m」 ("about 4 m wide, 33 m long overall"), and Shibata 「桁行24間、梁間3.5間」 ("24 ken long, 3.5 ken across") (translation).
- **Archived** https://jinya.gifu.jp/highlight/: Takayama's interrogations 「実際は牢屋内［現在の上一之町・海老坂付近］で行われていた」 — "were actually held in the jail, near present-day Kami-Ichinomachi" (translation). Takayama's jail stood outside the office compound.
- **Archived** zh.wikipedia 内乡县衙 (Qing):
  「监狱…现存各类房舍二十余间，是一个独立的小院，分为内监、外监、女监，四周高墙环绕」
  — "The prison… has twenty-odd rooms surviving, a self-contained courtyard divided into inner, outer and women's prisons, walled all round." (translation)

**ATTESTED ONLY FOR** Japan, and only by putting together figures from separate sites. City jail cell rooms (6-18 mats) are far smaller than the measured office rowhouses (about 108 × 13 ft, 143 × 24 ft). No magistracy's temporary cell is measured anywhere, and no single office sets the two side by side. The Qing yamen points the other way: its jail is a walled compound of twenty-odd rooms, not a cell.

## Readings

| # | Claim | Reading |
|---|---|---|
| 1 | head race turned away from the brook's flank | ATTESTED ONLY FOR the intake on the served land's bank (modern lecture); the turn itself is the engine's geometry |
| 2 | 12 ft standoff from the field | ATTESTED ONLY FOR a 3 ft setback from cultivated land (Mino; 1892 compilation of Tokugawa custom); 12 ft SILENT |
| 3 | wood "below the houses" judged by the median house | NOT-ABOUT-THE-WORLD |
| 4 | martial hall compound 130 × 124 ft, hall north, master's house and archery lane south | ATTESTED ONLY FOR halls with archery inside a domain school (Matsushiro 1855, Mito 1841); master's house NOT ATTESTED; size and north siting SILENT |
| 5 | 4 ft bare verge off the treads | NOT-ABOUT-THE-WORLD |
| 6 | household byre only on a nucleated seating | NOT ATTESTED (dispersed Isawa farms kept a stable joined to the house; modern, undated descriptions) |
| 7 | kura door on the apron where carts stand | SILENT on the door; carts ATTESTED ONLY FOR Qing Beijing granaries, NOT ATTESTED for Japan (men and horses) |
| 8 | holding cell smaller than the barracks | ATTESTED ONLY FOR Japan, by figures from separate sites; the Qing yamen jail points the other way |

## Leads not followed

- The Settsu city PDF (https://www.city.settsu.osaka.jp/material/files/group/43/p126-127.pdf): a search snippet says peasants carried the tax rice to Takatsuki on carrying poles. Not read, so not evidence.
- The Kurashiki intendant's office exhibition PDF and the MLIT Matsushiro PDF (which a search summary gives a 5,288 m² site): neither has a readable text layer here.
- The Kaga domain's separate martial school, 経武館 (1792), may be a stand-alone martial compound; one web query found nothing.
- The Tonami azumadachi farmhouse's stable (ウマヤ) inside its earth-floored work space: one query, no page found.
- Plans of Qing county granaries (常平仓) giving the doors' facing: would need a local gazetteer's 仓廒 entry.