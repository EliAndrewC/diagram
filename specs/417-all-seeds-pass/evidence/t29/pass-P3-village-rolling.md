**Pass P3: village seating and ways (`settlement/rolling/`)**

Of the 45 claims, the record already answers or bears on about 15. One premodern source was found on the web, for the water-town claim. Most of the rest are the engine's own settings, not claims about the world. I did not edit any file. Three figures go against the record:

- **The dispersed-farm slide** goes against 0031 and 0285, which say a scattered farm keeps its own spacing.
- **The 22 ft sun and shade strips** are smaller than every figure the record has: the Qimin Yaoshu's shade of one tree's height (about 33 ft), and 0038's own 39 ft and 50 ft.
- **The "alternate banks" seating in `waterfront_seeds`** is not supported. The sources have houses lining both banks continuously.

The house-off-the-water keep-outs also run against the record's direction: channels run beside the houses or into their grounds.

## Sources that bear on the claims

**1. Ruan Yisan, 周庄 (Zhouzhuang, in the "Jiangnan old towns" series).** Saved at /tmp/l7r-pass/p3-zhouzhuang/01-appbook.qq.com.txt. The book is modern (24 pages). It describes the town as it survives: founded in the Song, with the Zhang hall of the Ming.
- 「古镇四面环水，镇内由"井"字形的河道构成骨架，前街后河，河街相依，傍水建房，架桥津渡。」 (translation) "The old town is ringed by water. Inside it, canals in a 井-shaped grid form its frame. Streets in front, river behind; river and street lean on each other. Houses are built along the water, and bridges cross it."
- 「这些乡镇依河而建，因水成街，因水成市」 (translation) "These towns were built along the rivers. Streets formed because of the water, and markets formed because of the water."
- 「张厅为明代修建，船自家中过，水在窗下流」 (translation) "The Zhang hall was built in the Ming. Boats pass through the house itself, and the water flows under the windows."

**2. Zhang Song (Tongji University), People's Daily, 2023-12-21.** Saved at /tmp/l7r-pass/p3-zhangsong/01-paper.people.com.cn.txt. The article is modern and quotes a classical line.
- 「"人家尽枕河""水巷小桥多"，是江南人居环境的独特魅力。」 (translation) "'Every house pillows on the river' and 'many little bridges over the water lanes' are the special charm of Jiangnan living."
- 「城镇多为外湖环绕、内河构架、临水成街、依水筑屋。」 (translation) "The towns are mostly ringed by lakes outside and framed by canals inside. Streets form at the water's edge, and houses are built against the water."
- The article does not name the poet. I identify 「人家尽枕河」 as Du Xunhe's Tang poem on Suzhou (9th century); that is my identification, not the page's.
- It also says 「古镇内分别保留有公元15世纪以来的民居建筑」 (translation) "the old towns keep houses from the 15th century on."

**Reading:** ATTESTED ONLY FOR houses built continuously along the water, with a street on one side and the river on the other. There is a Tang line and Ming-to-Qing town fabric described by modern authors. Neither source has houses alternating bank to bank, or at an even, fixed spacing. The record agrees: 0035 has Likeng's houses facing each other across the stream, Xidi built along both banks, and Hongcun's channel led to every household. 0065 has a landing at nearly every door in the Jiangnan water towns.

## Record passages reused (already in /diagram/research/questions)

- **0285:** "No page we read measures how far apart neighboring houses stood in a clustered village." For scattered farms on the Tonami plain: "the farmhouses stand about 100-200 m apart."
- **0031 drawing:** "each homestead carries its own grove and keeps its own spacing." Also: "a small channel was led into the house's grounds" (Tonami).
- **0029 drawing:** "A thatched roof's eaves are taken to reach about 3 ft past the wall. No page we read gives the projection, so 3 ft is a GUESS." It also has each house turning with its lane, within about 34 degrees, from the Okinawan survey.
- **0038:** no source measures plot-to-tree distance. Its 39 ft and 50 ft are worked out from the sun, by the project. The Qimin Yaoshu (6th century) gives a tree's shade to the east, west and north "equal to the tree." On Tonami the east front held "little grove … flowering trees and persimmon."
- **0035:** at Harie "the channel that flows alongside the house." Nothing places a household's buildings across a channel from its house.
- **0048:** in the Tono L-shaped farmhouse, "the stable joins the lower end of the house and projects off its south side," and both mirror-image forms are recorded.
- **0039:** the bed lay "in the yard before the house, all round the house, or on spare ground away from it … none says which was usual." Imabari, 1924: the "drying yard, which was also the work yard," was 20% of the lot.
- **0037:** the Cantonese village's main lane was "sometimes widened into a drying ground." A house "with its own drying floor in front of the house" (Hunan).
- **0081 drawing:** the meeting "as a T" is "a GUESS, since no page we read says how a path was worn where two met."
- **0196:** no well spacing. A well could stand indoors, in the doma (the earth-floored work space).
- **0046:** the persimmon's crown stands within about 30 ft of the house (a GUESS).
- **Earlier passes today:**
  - pass-D: the gable margin is 3 ft (from 0081 drawing), and paths go round groves, not across them (0072, 0036).
  - pass-A1: `span_walkable`, from 0037.
  - pass-B: `FOOTPATH_DOOR_OUT_FT`.

## Searched this pass and found nothing

- **Archive:** 雨落ち, 滴水, 江南水乡, T-junction, water town. The hits were the archived Zhouzhuang wiki page, a shop page on landings, and unrelated pages; none bears. 一河两街 and 前街后河 had 0 hits.
- **Web queries:**
  - 江南水乡 一河两街 一河一街 前街后河 空间形态
  - "一河两街" "一河一街" "有河无街"
  - 茅葺 民家 軒の出 尺 農家
  - "軒の出" 茅葺 民家 "尺" 調査報告
  - 滴水 习惯 房屋 地界 清代
  - "滴水为界" 契约 清代 房屋
- **Results:** no premodern figure for how far a thatched eave projected, or for a gap between two farmhouses, in Japan or China. The shplanning.com.cn review could not be read (HTTP 503); I recorded it as unreadable.

## One row per claim

| key | status |
|---|---|
| access.py::EXIT_TURNS_DEG#bearing out turns | NOT-ABOUT-THE-WORLD |
| access.py::_house_candidates#path leaves its own yard | NOT-ABOUT-THE-WORLD (0.5 ft tolerance) |
| access.py::_standing_clear#path refused over reserved grove seats | ANSWERED in direction, 0072 / 0036 notes via pass-D (a path goes round a grove; none crosses one) |
| access.py::house_gap#the corridor's margin | NOT-ABOUT-THE-WORLD |
| access.py::leaves_its_yard#path leaves its yard once | RECORD-SILENT-BEFORE 0037; nothing forbids crossing a yard (0037 has a lane widened into a drying ground); "once" is NOT-ABOUT-THE-WORLD |
| access.py::past_the_yard#path not drawn on its own yard | RECORD-SILENT-BEFORE 0037 (yard in front of the house, so the way runs over it); otherwise NOT-ABOUT-THE-WORLD |
| access.py::round_the_gable#flank path round the gable | ANSWERED by 0081 drawing via pass-D: 3 ft from the wall. The engine's half-width + 1 ft matches 3 ft only if the half-width is 2 ft (not checked) |
| bearing.py::FOLLOW_FULL_PX | NOT-ABOUT-THE-WORLD |
| bearing.py::FOLLOW_HALF_SPAN_PX | NOT-ABOUT-THE-WORLD |
| bearing.py::FOLLOW_REACH_PX | NOT-ABOUT-THE-WORLD |
| bearing.py::MarginBearing#turn with the field margin | ANSWERED for the lane, 0029 (houses turn with their lane, within about 34 degrees, Okinawan survey); the field margin standing in for the lane is NOT-ABOUT-THE-WORLD |
| bearing.py::MarginBearing.__call__#folded square and faded | as the row above; the fading is NOT-ABOUT-THE-WORLD |
| bundle.py::_bundle_layout#byre's flank | ATTESTED ONLY FOR the Tono L-shaped house, 0048 (stable at the lower end, off the south side, both mirror forms); the claim text undersells the page. "Away from the garden" is RECORD-SILENT-BEFORE 0048 / 0039 |
| bundle.py::_bundle_layout#dispersed well pocket | NOT-ABOUT-THE-WORLD; RECORD-SILENT-BEFORE 0196 |
| bundle.py::_bundle_layout#forecourt kept on a no-rice farm | ANSWERED in part, 0039 (Imabari 1924: the drying yard was also the work yard, 20% of the lot); no source ties the yard to rice alone |
| bundle.py::_bundle_layout#house-to-part gap | RECORD-SILENT-BEFORE 0285 / 0029; SEARCHED-SILENT (this pass) |
| bundle.py::_bundle_layout#south band off an unkept yard | RECORD-SILENT-BEFORE 0038. FLAG: 22 ft is under 0038's 39 ft |
| bundle.py::_garden_beds#bed split forms | ATTESTED ONLY FOR beds "all round the house" (Ehime, 0039); the forms and the 6 ft width are NOT-ABOUT-THE-WORLD |
| bundle.py::_garden_beds#bed split share | RECORD-SILENT-BEFORE 0039 ("none says which was usual") |
| bundle.py::_lay_fixtures#the door's room past the yard | NOT-ABOUT-THE-WORLD (as pass-B `FOOTPATH_DOOR_OUT_FT`) |
| dispersed.py::YARD_SUN_STRIP#yard drying strip width | RECORD-SILENT-BEFORE 0038. FLAG: 22 ft is under both 39 ft and the Qimin Yaoshu's one tree height |
| dispersed.py::canonical_farmstead#south strip off an unkept yard | as the row above |
| dispersed.py::canonical_farmstead#wellhead off the house's front wall | NOT-ABOUT-THE-WORLD; RECORD-SILENT-BEFORE 0196 (a well could stand indoors in the doma) |
| farmsteads.py::_east_trees#east shade band width | ANSWERED in part, Qimin Yaoshu in 0038 (shade about one tree height, about 33 ft for a 10 m tree). FLAG: 22 ft is under it, and under 0038's 50 ft |
| fit.py::_fixtures_in_bands#no fixture in a grove band | NOT-ABOUT-THE-WORLD |
| fit.py::_garden_sun_conflict#bed's morning-sun reach | as `_east_trees`. FLAG |
| fit.py::_house_too_near_a_neighbor#roofs shed apart | RECORD-SILENT-BEFORE 0285 / 0029 (the 3 ft eave is a GUESS); SEARCHED-SILENT (eave projection and eave-drip boundary, Japanese and Chinese) |
| fit.py::_parts_fit#beds off every ditch | NOT ATTESTED in direction (0035, 0031: water beside the house and into its grounds); the corridor is NOT-ABOUT-THE-WORLD |
| fit.py::_parts_fit#persimmon held off the paddy by its trunk | RECORD-SILENT-BEFORE 0046; NOT-ABOUT-THE-WORLD |
| fit.py::_rect_blocked#grove may hug a paddy bund | RECORD-SILENT-BEFORE 0036 / 0038; not searched |
| fit.py::_rect_on_water#solid parts off running water | NOT ATTESTED as a keep-out. FLAG: 0035 Harie (channel alongside the house), 0031 Tonami (into the grounds), 0065 and this pass (Jiangnan houses on the water, boats through the Zhang hall) |
| fit.py::_water_obstacles#water line keep-out | NOT-ABOUT-THE-WORLD for the pixel figures; direction as the row above |
| fit.py::_yard_sun_conflict#yard's drying strip width | as `YARD_SUN_STRIP`. FLAG |
| fit.py::stream_segment_index#stream keep-out | NOT-ABOUT-THE-WORLD |
| gap_ways.py::JOIN_FAR_FT#a farther join | RECORD-SILENT-BEFORE 0081 drawing (the T is a GUESS); 45 ft is NOT-ABOUT-THE-WORLD |
| gap_ways.py::JOIN_FT#ways join at a T | RECORD-SILENT-BEFORE 0081 drawing; 25 ft is NOT-ABOUT-THE-WORLD |
| gap_ways.py::flood#how hard it keeps the middle | NOT-ABOUT-THE-WORLD |
| gap_ways.py::lay_the_ways#a later way's join reach | as `JOIN_FT` |
| gap_ways.py::trace#join reach | as `JOIN_FT` |
| passage.py::reserve_way#the walk reserved as it is seated | NOT-ABOUT-THE-WORLD |
| place.py::_place_bundle_nucleated#left or right garden | RECORD-SILENT-BEFORE 0039 / 0038 (a bed may stand SE, SW, E or W); even odds are NOT-ABOUT-THE-WORLD |
| place.py::_slide#dispersed farm packed against its nearest neighbor | ANSWERED, against the engine. FLAG: 0031 ("keeps its own spacing") and 0285 (Tonami farms 100-200 m apart) |
| route.py::_route_from#path leaves its own yard once | as `leaves_its_yard`; off the neighbors' homesteads, RECORD-SILENT-BEFORE 0246 (cutting through a neighbor's yard by custom, via pass-A1) |
| seeds.py::waterfront_seeds#water town fronting a canal | ATTESTED ONLY FOR houses continuous along the water, street in front and river behind (Ruan, Zhouzhuang; Zhang Song; the Tang line; 0065; 0035 Likeng and Xidi on both banks). FLAG: alternating banks at an even spacing is NOT ATTESTED |

## Leads not followed

- The town typology 「一河两街 / 一河一街」: the shplanning review (HTTP 503) and Ruan's 《江南古镇》 (1998) might define it.
- 「人家尽枕河」: check it at the source (Du Xunhe, 《送人游吴》) before citing it as Tang evidence.
- Eave projection: Japanese repair reports (修理工事報告書) and the Tokushima Sanagouchi thatched-house survey PDF (library.tokushima-ec.ed.jp) give section drawings that may show it.
- Edo-period disputes over trees shading paddies (日陰伐り) would bear on the grove-and-bund and persimmon claims.

Sources:
- [Ruan Yisan, 周庄 (appbook.qq.com)](https://appbook.qq.com/read/1035091114/3)
- [Zhang Song, People's Daily 2023-12-21](https://paper.people.com.cn/rmrbwap/html/2023-12/21/nw.D110000renmrb_20231221_1-20.htm)
- [shplanning.com.cn review (unreadable)](https://www.shplanning.com.cn/archive/detail/id/1517.html)