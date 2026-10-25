I went through all 77 claims in `pass-P7-other.txt`. The record already answered 8 of them; 4 of those answers contradict the engine (flagged below) and a fifth was half-answered. Five more I checked against new pages this pass. About 45 are drawing or algorithm tolerances no source could speak to, and five world questions were neither in the record nor searched this pass. I edited no file.

## Flags: a source contradicts the claim

1. **The moat against the rampart** (`taxonomy._MATRIX_ALLOWED_KEYS#moat against the rampart`), from the record, 0151. The Northern Song military compendium (*Wujing Zongyao*, 11th c.): 「門外築甕城，城外鑿壕，去大城約三十步，上施釣橋。」 "Outside the gate build an enclosure wall; outside the city dig the moat, about thirty paces from the main wall, with a drawbridge over it." (translation). Measured today, by the thepaper-surviving-walls page cited in 0151: 「城外护城河宽、深约3.3米，城墙与护城河的距离7至10米不等」 "Outside the city the moat is about 3.3 m wide and deep; the distance between wall and moat varies from 7 to 10 m." (translation; this is Qufu, and 0151 also gives Guide at 3.5 m). China's evidence puts a strip of ground between wall and moat; it does not put the moat at the wall's foot. The rule only permits the overlap, but the claim's wording ("lying against the rampart's foot") is contradicted.
2. **Suburb wards get no ward-gate mouths** (`city/knobs.py::machi_mouths`), from the record, 0160 (key beijing-zhalan, Ming, 1488): 「明弘治元年（1488年），孝宗皇帝下令在京城内及关厢地区的大街小巷设立栅栏，早启晚闭，用于维护京城的治安。」 "In 1488 the Xiaozong emperor ordered barriers set up in the great streets and small lanes within the capital and in the gate suburbs (guanxiang), opened early and shut late, to keep the capital's order." (translation). So the suburbs outside the gates were barred too. This is NOT ATTESTED: the evidence points the other way.
3. **A flower bed flush inside the rampart** (`taxonomy#flower bed against the town wall`). Two archived pages put a street along the inside of the wall:
   - zh.wikipedia, 西顺城街 (Tongzhou): 「明代已经形成，原本为巡城马道，称为西马道」 "Formed by the Ming; originally the wall-patrol horse road, called the West Horse Road." (translation; Ming).
   - kepuchina (Tang Chang'an, excavated): 「…25米（东顺城街）」 "…25 m (the East Shuncheng Street)." (translation; a street running along the inside of the east wall).
   - The record's own 0087 drawing already runs a ring road just inside the rampart, and 0015 calls Hirameki's chrysanthemum field a deliberate departure from history.

   NOT ATTESTED: ground at the wall's inner foot was a road.
4. **The water-mouth pavilion, a hexagon of 22 ft radius** (`town_ways.py::water_mouth#pavilion size`; the unit is ft, since `pr = self.px(r)`). This is not contradicted, but no source supports it. The record's 0071 attests a grove at the water mouth and no pavilion at all. Three searches found no measured village pavilion. A 44 ft-wide hexagon is far larger than an ordinary pavilion; that comparison is my judgment, not something a page gave me.

## Sources read this pass

- **Kitakyushu, Yasaka shrine stone torii** — https://www.city.kitakyushu.lg.jp/contents/02100290.html, saved at `/tmp/l7r-pass/torii/01-www.city.kitakyushu.lg.jp.txt`. The page gives no build date; it is a prefecture-listed old torii. 「高さ4.51m、笠木の長さ5.87m、柱間3.61m、柱径0.47m。」 "Height 4.51 m, top beam (kasagi) 5.87 m long, post span 3.61 m, post diameter 0.47 m." (translation). The posts stand at 3.61/5.87 = 0.615 of the beam's length. The engine uses 12/19 = 0.632. I have not recorded an outcome for this page; that is the session's to record when it cites it.
- **Kato city, Kawataka Sumiyoshi shrine stone torii** — archived copy `/diagram/.specify/source-archive/03/0304f5f3ba07/20261002T152653Z/text.txt`, late Muromachi to early Edo. 「柱間が2.5m、高さが2.8mを測る」 "Post span 2.5 m, height 2.8 m." (translation). 「室町時代末期～江戸時代初期の石鳥居と考えられています」 "Thought to be a stone torii of the late Muromachi to early Edo period." (translation). The page says its squat shape came from the local stone, which could not be cut into long posts.
- **Miyagi, Kameoka Hachiman torii, 1683** — https://www.pref.miyagi.jp/soshiki/bunkazai/15kameoka.html. 「門の幅は柱下部で柱心間5.53m」 "The gate's width at the post feet, centre to centre, is 5.53 m." (translation). This is a domain lord's large city-shrine torii, so it is an upper bound. I logged it as rejected on the ledger but report it here as the upper bound.
- **Record 0247, the drip strip** (Qing deeds and customs surveys, north China):
  - 「嘉祥县第二滴水地建筑房屋，须留滴水地二、三尺」 "In Jiaxiang county, building a house, one must leave 2 or 3 chi of drip ground." (translation)
  - 「北院北房后有滴水三尺」 "Behind the north building of the north court is a drip of 3 chi." (translation; a Baoding deed of 1884)
  - The record also gives an eaves overhang of 2.2 chi.

  Two drip strips of 2–3 chi each come to about 4.4–6.6 ft. A path between them brings that to about 8 ft. ATTESTED ONLY FOR north-China Qing custom; no source gives the footpath.
- **Record 0080, tree spacing** (Morioka domain, Tenpō era, 1830s–40s): 「天保年代スギは「成木早伐取之ため一間四方へ九本位」植立てられた」 "In the Tenpō era, sugi were planted 'about nine to the square ken, to fell them early once grown'." (translation). The same record has the Qimin Yaoshu (6th c.) setting trees "two paces apart each way". ATTESTED ONLY FOR planted woods.
- **Record 0050, the ancestral hall.** The hall faces its pond, and the drying floor (heping) between them is left open. ATTESTED in part for a reserved forecourt; no source gives the 6 px.

## Verdicts on the searched claims

- **Torii:** ATTESTED for the posts' set-in, but only from an undated torii. ATTESTED ONLY FOR the middle of the range on the 16 ft span. If "span" means the beam's length, 16 ft (4.9 m) lies between the early-Edo village torii (about 13 ft of beam implied, 8 ft between posts) and Kokura's 19.3 ft. If it means the gap between the posts, it is twice the dated village example. Beam width: SILENT. Only a post diameter of 0.47 m (1.5 ft) was found, which could stand in for it.
- **Gatehouse door:** SILENT. Two Japanese searches for guardroom windows and doors facing the gate passage found that guardrooms flanked the doorway (Saitama, Takayama house, Ikeda gate) but nothing on which way the door faced.
- **Scrub pine height and reach, and trees cut back from fields:** SILENT. I tried four queries (陰伐/蔭切/日陰伐 田畑; 日影伐 地方凡例録; 草山 柴山 アカマツ 樹高; 六角亭 is under the pavilion). The Kyoto prefecture page on the Kizugawa hills gives Edo-period pine woods and grass hills but no heights.
- **Pavilion size:** SILENT. Three Chinese searches (徽州 水口 亭 边长; 水口 亭 面阔 进深; 六角亭 "边长" 村口).

## One row per claim

Key prefix `l7r/diagram/` is dropped.

| key | verdict |
|---|---|
| compound_example::county_magistracy_program#cell door | RECORD-SILENT-BEFORE 0096 (cell in the outer court, door side not given); the rest is a layout choice |
| compound_example::county_magistracy_program#gatehouse door | RECORD-SILENT-BEFORE 0093 (Kaibara 「門戸を挟んで北側に番所・土間」: the guardroom flanks the doorway); SEARCHED-SILENT (this pass) |
| compound_model::NOTICE_BOARD_MAX_FT#board by the gate | RECORD-SILENT-BEFORE 0190 drawing ("a freestanding board … at the office's own gate … a GUESS"; Chinese notices were posted on the walls flanking the gate) |
| hamletgen/consts::BAMBOO_FORMS#the forms' odds | NOT-ABOUT-THE-WORLD |
| hamletgen/consts::BUNDLE_PITCH#the along-row span | NOT-ABOUT-THE-WORLD (grid pitch; the row step is 0038's) |
| hamletgen/consts::CLUSTER_SPAN_FACTOR#cluster's reach | NOT-ABOUT-THE-WORLD |
| hamletgen/consts::FAN_ASPECTS#fan aspect | NOT-ABOUT-THE-WORLD |
| hamletgen/consts::REF_CANAL_A#reference fan's canal A | NOT-ABOUT-THE-WORLD (calibration to the project's own Ikegami map) |
| hamletgen/consts::REF_CANAL_B#reference fan's canal B | NOT-ABOUT-THE-WORLD (same) |
| hamletgen/consts::REF_FIELD_FALL#reference fan's fall | NOT-ABOUT-THE-WORLD (same) |
| hamletgen/consts_fields::LEFTOVER_FORMS#dike-pond leftover parcels | NOT-ABOUT-THE-WORLD (knob odds) |
| hamletgen/driver::STAGES#pond-bank trees after the wells | NOT-ABOUT-THE-WORLD |
| hamletgen/driver::STAGES#the ground's cover after every built thing | NOT-ABOUT-THE-WORLD |
| hamletgen/driver::STAGES#track before the wells | RECORD-SILENT-BEFORE 0196 (lane-side well "attested for wayside wells in general, its use in a village a GUESS"); the ordering itself is NOT-ABOUT-THE-WORLD |
| hamletgen/driver::STAGES#waterward fringe before the houses | NOT-ABOUT-THE-WORLD |
| hamletgen/frame::stage_crossings#ditch footbridge spacing | RECORD-SILENT-BEFORE 0084 notes ("none says what crossed a paddy ditch, at what width, or how often") |
| hamletgen/frame::stage_crossings#polder crossing caps | NOT-ABOUT-THE-WORLD (copied from the hand-authored maps) |
| hamletgen/plan::HamletSpec#default households | ANSWERED 0001: a hamlet is 10–20 households, the setting's (GM canon) figure; 15 is its midpoint |
| hamletgen/plan::SEAT_STANDOFF#standoff from the field | Not looked into: the record is silent with no absence note (0029, 0055, 0037, 0038 grepped); not searched this pass |
| hamletgen/plan::SitePlan.head_deg#turned away from the brook's flank | Not looked into: 0035 gives "faces the fields, back to the winter wind" and nothing on the brook; not searched |
| hamletgen/plan::band_extent#band area | NOT-ABOUT-THE-WORLD |
| hamletgen/plan::band_extent#band aspect by shape | NOT-ABOUT-THE-WORLD |
| hamletgen/plan::band_extent#band floors and caps | NOT-ABOUT-THE-WORLD |
| hamletgen/plan::offtakes_for#delivery-ditch count and fractions | NOT-ABOUT-THE-WORLD (0053 drawing: its flank figures are "this project's choice, not a source") |
| hamletgen/pondbank::stage_pond_bank#after the houses, ways and wells | NOT-ABOUT-THE-WORLD |
| hamletgen/pondstock::stage_pond_stock#at least one sty | RECORD-SILENT-BEFORE 0025 ("no page we read gives the share of households that kept a pig") |
| hamletgen/washing::each_house_places#slid at most 16 ft | RECORD-SILENT-BEFORE 0065 (its shared-place slide is 32 ft, a project figure; 16 ft is not a contradiction); NOT-ABOUT-THE-WORLD |
| hamletgen/washing::shared_places#its nearest water | RECORD-SILENT-BEFORE 0065 drawing (the number of places is a GUESS) |
| hamletgen/washing::stage_washing#after the ways and crossings | NOT-ABOUT-THE-WORLD |
| labels/placer::moved_inward#moved inward | NOT-ABOUT-THE-WORLD |
| labels/placer::place#caption clearance | NOT-ABOUT-THE-WORLD |
| labels/placer::place#no seat in the frame | NOT-ABOUT-THE-WORLD |
| overlap/taxonomy::_MATRIX_ALLOWED_KEYS#flower bed against the town wall | **CONTRADICTED**: zh.wikipedia 西顺城街 (Ming patrol road inside the wall), kepuchina 东顺城街 (Tang), the record's 0087 ring road; 0015 calls the field a departure |
| overlap/taxonomy::_MATRIX_ALLOWED_KEYS#moat against the rampart | **CONTRADICTED** (record already answered): 0151, about 30 paces (*Wujing Zongyao*); 7–10 m at Qufu, 3.5 m at Guide |
| overlap/taxonomy::_MATRIX_PERMISSIVE#house or field on cover | NOT-ABOUT-THE-WORLD |
| settlement/_geom/curves::winding#winding path | NOT-ABOUT-THE-WORLD |
| settlement/_geom/village::FARMHOUSE_EAVE_GAP_FT#wall-to-wall | ANSWERED 0247: drip ground 2–3 chi a house, eaves 2.2 chi (north-China Qing); consistent with 8 ft, the footpath unsourced |
| settlement/_geom/walls::torii_glyph_dims#post set-in | ANSWERED (this pass), Kitakyushu: posts at 0.615 of the beam's length against 12/19 = 0.632 (undated torii) |
| settlement/_geom/walls::torii_glyph_dims#top beam width | SEARCHED-SILENT (only a post diameter of 0.47 m, a stand-in) |
| settlement/_geom/walls::torii_glyph_dims#torii span | ANSWERED ONLY FOR the mid range: Kato post span 2.5 m (early Edo), Kitakyushu beam 5.87 m, Kameoka post span 5.53 m (1683) |
| settlement/_geom/walls::torii_seat_on_wall#torii clear of every wall | NOT-ABOUT-THE-WORLD |
| settlement/_geom/ways::PLANK_VILLAGE_REACH#footplank reaches the village | NOT-ABOUT-THE-WORLD (0084 drawing: "both ends land on ground worth crossing to") |
| settlement/_knobs::<module>#hamlet default values | NOT-ABOUT-THE-WORLD |
| settlement/_knobs::skeleton_layout#gateway at the low foot | RECORD-SILENT-BEFORE 0057 drawing ("every … map leaves dry ground for a road out downhill", a project rule) |
| settlement/_knobs::skeleton_layout#headman at the focal point | RECORD-SILENT-BEFORE 0030 ("No page we read places the house … oldest cluster - a GUESS") |
| city/bridges::_plank_reaches_useful_ground#bank and village reach | NOT-ABOUT-THE-WORLD |
| city/bridges::channel_footbridges#assumed channel width | NOT-ABOUT-THE-WORLD |
| city/bridges::channel_footbridges#feeder left unplanked | RECORD-SILENT-BEFORE 0084 (no page says when a path crossed a ditch) |
| city/bridges::channel_footbridges#off groves | NOT-ABOUT-THE-WORLD |
| city/bridges::channel_footbridges#polder crossings by side | NOT-ABOUT-THE-WORLD |
| city/bridges::channel_footbridges#short stub stepped over | NOT-ABOUT-THE-WORLD |
| city/knobs::machi_mouths#suburb wards outside the mesh | **CONTRADICTED** (record already answered): 0160 beijing-zhalan, 1488 barriers 「京城内及关厢」 |
| city/moat::inwall_drain_outfall#conduit corridor | NOT-ABOUT-THE-WORLD |
| farm_fixtures::pond_fixture_fits#sty clearance | NOT-ABOUT-THE-WORLD |
| hard_ground::_hard_ground#crop and ditches are no-build | NOT-ABOUT-THE-WORLD |
| houses::_fits#building spacing | NOT-ABOUT-THE-WORLD |
| houses::_in_blocked#seat set-back from dry plots and hills | NOT-ABOUT-THE-WORLD |
| land/cover::FARMSTEAD_NEIGHBOR_FT#shared ground | NOT-ABOUT-THE-WORLD (the record has nothing on it) |
| land/cover::_commons_keep#off the treads | Not looked into: no record of a bare verge along lanes (0196 has a well curb within 8 ft of the tread); not searched |
| land/cover::_stock_woodland#crowns and pines clear of the crops | RECORD-SILENT-BEFORE 0073 drawing (a project rule, the 6 ft a GUESS); SEARCHED-SILENT for shade-cutting customs |
| land/cover::_stock_woodland#crowns thin to the wood's edge | NOT-ABOUT-THE-WORLD |
| land/cover::_stock_woodland#woodland stocked to read | NOT-ABOUT-THE-WORLD |
| land/cover::commons#a scrub pine's height | SEARCHED-SILENT (this pass) |
| land/cover::commons#a scrub pine's reach | SEARCHED-SILENT (0080's 17 ft crowns are for canopy trees) |
| land/cover::commons#woodland no-build | NOT-ABOUT-THE-WORLD |
| land/cover::fill_the_holes#bare-share cap | NOT-ABOUT-THE-WORLD |
| land/cover::woodland_room#crowns on a lattice | ANSWERED ONLY FOR planted woods: 0080, Morioka 「一間四方へ九本位」, Qimin Yaoshu two paces each way |
| land/cover::farmstead_keepouts#no scrub among the farmsteads | NOT-ABOUT-THE-WORLD |
| land/dikes::DIKE_GAP_HW#cut width | NOT-ABOUT-THE-WORLD (the record gives no sluice width) |
| land/dikes::dike_top_houses#house platform | RECORD-SILENT-BEFORE 0019 drawing (14 by 10 ft "is a GUESS") |
| land/dikes::dike_top_houses#no homestead bundle | RECORD-SILENT-BEFORE 0019 drawing ("drawing none on the crest is a GUESS") |
| land/dikes::dike_top_houses#off the sluice notch | RECORD-SILENT-BEFORE 0019 drawing ("no page we read says where on a dike the houses stood relative to its sluices") |
| land/dikes::dike_top_houses#spacing along the crest | NOT-ABOUT-THE-WORLD |
| land/wet::marsh#reeds off the dooryards | NOT-ABOUT-THE-WORLD |
| land/wet::marsh#tread keep-out width | NOT-ABOUT-THE-WORLD |
| town_ways::ancestral_hall#focal keep-out | ANSWERED in part, 0050 drawing: the open heping between hall and pond; the 6 px is the project's |
| town_ways::water_mouth#pavilion size | SEARCHED-SILENT (this pass); 0071 attests a grove and no pavilion; 44 ft across is likely oversized |

## Leads not followed

- Five world questions are still open, neither in the record nor searched: the 12 ft house-to-field standoff, a house's turn away from the brook, the 4 ft bare verge along lanes, and the cell's and the gatehouse's door sides (beyond the two gatehouse searches).
- funes.world "Jiangyong Mingfeng pavilion": the search summary called it an octagon with 6 m sides, but it is a three-story tower and may not be a water-mouth pavilion. Not read.
- funes.world "road pavilion in Jiaohu village, Shanggao": might give a village pavilion's size. Not read.
- Kitakyushu torii's build date: try the Fukuoka prefecture designation register.
- Japan's side of the moat question: the ja.wikipedia 堀 and 総構 pages are already in 0151's notes; the berm between castle wall and moat (inukashiri) was not checked.

Pages saved this pass are under `/tmp/l7r-pass/torii/` and `/tmp/l7r-pass/pine/`. Every page read has an outcome on the ledger except Kitakyushu, which is left for the session to record as cited.

Sources:
- [Kitakyushu, Yasaka shrine stone torii](https://www.city.kitakyushu.lg.jp/contents/02100290.html)
- [Miyagi, Kameoka Hachiman stone torii](https://www.pref.miyagi.jp/soshiki/bunkazai/15kameoka.html)
- [Kashiwa, Shinmei shrine stone torii](https://www.city.kashiwa.lg.jp/bunka/about_kashiwa/culture/rekishi/shiteibunkazai/yuu/2875.html) (gives only a height)
- [Kato city stone torii](https://www.city.kato.lg.jp/kakukanogoannai/kyouikushinkoubu/shogaigakushuka/bunkazai/siteibunkazai/kensiteibunkazai/1510384600965.html) (archived)
- [zh.wikipedia 西顺城街 (Tongzhou)](https://zh.wikipedia.org/wiki/西顺城街_(北京市通州区)) (archived)
- [kepuchina, Tang Chang'an](https://www.kepuchina.cn/wiki/ct/201903/t20190323_1029448.shtml) (archived)
- [Kyoto prefecture, human and environment article](https://www.pref.kyoto.jp/kankyo_red/2026/static/04_ecosystem/02_human-environment/02_article.html) (nothing found)
- [funes.world, Jiangyong Mingfeng pavilion](https://funes.world/entities/jiangyong-mingfeng-pavilion) (lead, not read)
- [funes.world, Jiaohu road pavilion](https://funes.world/entities/road-pavilion-in-jiaohu-village-mengshan-town-shanggao-county) (lead, not read)
- [MLIT, features of the nagaya gate](https://www.mlit.go.jp/tagengo-db/R1-00073.html) and [Saitama city PDF](https://www.city.saitama.lg.jp/004/005/006/002/002/p042771_d/fil/51.pdf) (search results only, not read)