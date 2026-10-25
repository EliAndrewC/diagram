I found little that answers these claims directly. Almost every figure in the group (30 ft, 20 ft, 14 ft, 12 ft, 4 ft, 60 deg, 25 deg, 4x chord, "two ends") is a drawing tolerance that the record already says it chose and did not measure. Only four claims touch the world: paths to graves, the doorstep, the household-way rule, and paths to the commons. The first three now have partial sources; I couldn't read anything on the commons.

## The record first

- **0081 drawing** already says, in its closing bullet: "Every turn limit and distance in these bullets is chosen at the scale of a dozen paces, not measured." It also already has these rules as "this project's own, a map drawing convention" (both quoted from the page):
  - "Two paths running side by side are drawn as one."
  - "A household's own way is cut at its far end, never at its door."
  - The door-side T is one path from the door, not two ends that nearly meet.

  Its one cited source for path shape is desire-path-enwiki: 「The path usually represents the shortest or the most easily navigated route」. It also cites ma-2024-desire-paths, a modern simulation whose walkers are told to 'Go straight!'.
- **0081 notes** record searches that found nothing on lanes as the gaps between plots, and nothing on "how far a lane runs past its last house, or where it ends".
- **0246 notes** say "None of the pages we read gives how far a lane runs past its last house, or where it ends". They also carry Mencius 14.21 (a hill path "walked without a break, becomes a road; left unwalked ... the thatch grass chokes it") and the Tang code on lanes as places "where the public passes".
- **0033 drawing** says a row's street "runs on off the map as the road into it", and that it is laid before the farms.
- **0224** (in its notes) already holds 「七月七日をボンハジメ、ナヌカボンといい、墓や墓への道を清掃する。」 ("the seventh of the seventh month is called Bon-hajime or Nanuka-bon, and the graves and the paths to the graves are cleaned", translation). That is from a 2021 book, a modern popular account.
- **0238** says nothing it read describes a funeral path to a cremation ground.
- **Archive:** "desire path" and "social trail" find only the pages above. "丁字路" and "三叉路" find castle-town and dōsojin (roadside guardian-stone) pages, nothing on village lanes. "墓道" finds Chinese tomb spirit-ways, which are not village paths.

## Web sources that bear

1. **https://kotobank.jp/word/野辺送り** (the Britannica Japan entry). It describes traditional burial in Japan, before cremation spread; the account is undated, and 0081/0224 elsewhere put the procession's end in late Shōwa.
   「葬列は出立ちから墓地へ到着する間，わざわざ回り道をしたり，ぐるぐる回りをしたりするが，これは死霊が迷い戻らないための呪法と説明されている。」 (translation) "Between setting out and arriving at the graveyard, the funeral procession deliberately takes a roundabout way or goes round in circles, which is explained as magic to keep the dead spirit from straying back."
   Also: 「土葬では喪家から墓場まで…遺体を運ぶための行列をいう」 (translation) "In burial, it means the procession carrying the body from the house of mourning to the graveyard."

2. **https://projects.mcah.columbia.edu/jaanus/node/1897** (JAANUS, ōdoguchi). Evidence from the Edo period.
   "The main entrance to traditional vernacular houses *minka* … In cases where the earth-floored area had more than one entrance, the most prominent one was referred to as the ōdoguchi. In most Edo period minka, the ōdoguchi was the entrance generally used by household members."

3. **https://m.sohu.com/a/166996636_226858** (Longli, Guizhou). It describes a Ming garrison fort, founded 1385, with its Ming-Qing layout surviving.
   「往东西南开三条主街，形成丁字街道结构…街道的错接具有"固气"、"避灾去邪"和利于防御的意义。城中不开"十"字」 (translation) "Three main streets open east, west and south, forming a T-street structure … the staggered joining of streets means 'holding the qi', 'avoiding disaster' and serving defence. No cross-shaped junction is opened in the town."
   This is a fort-town's main streets, not a village's lanes.

## Reading

**Graves: ATTESTED ONLY FOR** the burial ground being something a path leads to from the house. 0224 has paths to the graves being cleaned, and kotobank has the procession going from the house to the graveyard, in Japan. The procession's route was deliberately roundabout, so a ritual route is not evidence for a direct lane. Nothing found says a lane ends at the burial ground's edge.

**Door: ATTESTED ONLY FOR** a single main door that the household used, sometimes with a second doma (earth-floor) entrance, in Edo minka. That fits the rule that a household's own way leaves its door. It says nothing about the 4 ft step, the 10-20 ft first leg, or "at most two free ends".

**T-joins: ATTESTED ONLY FOR** a Ming fort-town's main streets, with no crossroads; nothing found for village lanes.

**Everything else: SILENT or not about the world.** The side-by-side and bundling distances, the 25 deg and 30 ft tail, directness (4x chord, 200 ft), and the minimum path length are all searched-silent or drawing tolerances.

## Searches run this pass (all silent except the pages above)

- 野辺送り 葬列 墓への道 葬式道: gave kotobank, used above.
- Pedestrian route directness / detour factor: only modern figures. WSDOT's Route Directness Index uses 2 as its threshold, and Boeing's arXiv 1708.00836 compares walking and driving circuity in modern cities. Neither is premodern, so neither is fetched as evidence.
- 農家 カド 前庭 大戸口: gave JAANUS, used above.
- 传统村落 巷道 丁字路口 (twice): gave Longli. I fetched and rejected news.ifeng.com/c/8c0j1wcFOrS; it gives Wangnao village's lane-width custom, not lane form.
- 入会地 秣場 通う道: the Azumino 烏川山入会絵図 PDF has no text layer, so it is unreadable (recorded).

Ledger outcomes recorded: ifeng rejected, Azumino unreadable. Kotobank, JAANUS and sohu are left for you to cite. The earlier junction-angle pass was not repeated.

## Per claim

| claim key | status |
|---|---|
| fabric.py::_WEB_MIN_FT#shortest way | NOT-ABOUT-THE-WORLD (0081: distances "chosen at the scale of a dozen paces, not measured"; Mencius in 0246 says only that an unwalked path is lost) |
| fabric.py::_draw_web#shortest way | NOT-ABOUT-THE-WORLD (same) |
| geom.py::_trim_to_service#not the way it left | NOT-ABOUT-THE-WORLD |
| geom.py::steading_footprints#ground cover is no destination | SEARCHED-SILENT (commons paths; Azumino map unreadable) |
| law.py::DOORSTEP_MAX#ends one house may absolve | ANSWERED only in part: JAANUS, one main door used by the household and sometimes a second doma entrance (Edo); "two" is not given |
| law.py::FRAGMENT_FT#shortest way | NOT-ABOUT-THE-WORLD |
| law.py::NEEDLE_FT#needle leg | NOT-ABOUT-THE-WORLD |
| law.py::TARGET_REACH_FT#a way target reached | NOT-ABOUT-THE-WORLD |
| law.py::breaks_through#a leg long enough to break | NOT-ABOUT-THE-WORLD |
| law.py::dangling_lane_ends#a burial ground's edge… | ANSWERED only in part: 0224 (paths to the graves cleaned) and kotobank 野辺送り (procession from the house to the graveyard, by a deliberately roundabout way); nothing on the edge as a lane end |
| law.py::dangling_lane_ends#a way reached only where the lane walked to it | NOT-ABOUT-THE-WORLD |
| law.py::doorstep_ends#no fan of stubs at a door | ANSWERED only in part: JAANUS, as for DOORSTEP_MAX; 80 ft is a tolerance |
| law.py::field_unreached#asked on brook maps only | NOT-ABOUT-THE-WORLD |
| law.py::near_misses#a blocked join is no short join | NOT-ABOUT-THE-WORLD |
| law.py::near_misses#a connector's ends | NOT-ABOUT-THE-WORLD |
| law.py::near_misses#which ends count | NOT-ABOUT-THE-WORLD (the angle was already searched-silent today) |
| law.py::needle_ends#needle leg | NOT-ABOUT-THE-WORLD |
| law.py::short_fragments#debris | NOT-ABOUT-THE-WORLD (0246 Tang code: lanes are where the public passes) |
| serve.py::DOOR_SHIFT_FT#door step | SEARCHED-SILENT (JAANUS gives a one-bay door, no step depth) |
| serve.py::_lay_web_lane#a healing link kept | NOT-ABOUT-THE-WORLD |
| serve.py::_lay_web_lane#link reach | SEARCHED-SILENT (directness search; modern only) |
| serve.py::_lay_web_lane#no way drawn twice | RECORD-SILENT-BEFORE 0081 drawing ("Two paths running side by side are drawn as one", its own convention); Helbing already read today |
| serve.py::_lay_web_lane#the nearer end joined | NOT-ABOUT-THE-WORLD |
| serve.py::joined_link#a detour link's reach | NOT-ABOUT-THE-WORLD |
| serve.py::route_from_door#a first leg out of the door's cell | SEARCHED-SILENT (door search) |
| serve.py::runs_beside#no way drawn twice | RECORD-SILENT-BEFORE 0081 drawing |
| serve.py::shadowed_by#no way drawn twice | RECORD-SILENT-BEFORE 0081 drawing |
| settle/ends.py::JOIN_BACK_PAD_FT#a deferring end taken back | NOT-ABOUT-THE-WORLD |
| settle/ends.py::settle_ends#no fan of stubs at a door | ANSWERED only in part: JAANUS, as for DOORSTEP_MAX |
| settle/ends.py::settle_fragments#debris | NOT-ABOUT-THE-WORLD |
| settle/ends.py::settle_joins#a join taken back | NOT-ABOUT-THE-WORLD |
| settle/ends.py::settle_shadows#no doubled band | RECORD-SILENT-BEFORE 0081 drawing |
| settle/shapes.py::reaimed#an end within a hand's width | NOT-ABOUT-THE-WORLD |
| settle/shapes.py::settle_shapes#a fouling segment cut out | NOT-ABOUT-THE-WORLD |
| sweeps.py::_LINK_DIRECTNESS#network link directness | SEARCHED-SILENT (only modern-city circuity: WSDOT RDI threshold 2, Boeing 2017; not premodern) |
| sweeps.py::_join_orphan_ways#orphan link directness | SEARCHED-SILENT (same) |
| sweeps.py::_sweep_dangling_ends#a whittled lane emptied | NOT-ABOUT-THE-WORLD |
| tails.py::_ALONG_DEG#running with the way | RECORD-SILENT-BEFORE 0081 drawing (its 20 deg is a convention); angle searched-silent today |
| tails.py::_ALONG_MIN_FT#tail run length | NOT-ABOUT-THE-WORLD |
| tails.py::_sweep_doubled_tails#doubled tail cut | RECORD-SILENT-BEFORE 0081 drawing ("cut it where it comes alongside", a convention) |
| tails.py::_sweep_doubled_tails#narrower tail cut | NOT-ABOUT-THE-WORLD |
| tree.py::admits#free ends at a house | ANSWERED only in part: JAANUS, as for DOORSTEP_MAX |
| tree.py::alongside_points#beside, as the map reads it | RECORD-SILENT-BEFORE 0081 (the claim itself says 0081 gives no distance) |
| tree.py::cut_alongside#each end walked, the nearer point first | NOT-ABOUT-THE-WORLD |
| tree.py::prune_the_tree#redundant tree lane pruned | ANSWERED in part by the record: 0246 Tang code on lanes as public passage; 0081 Ushijima's Manchu "small paths leading to farms, which are not often used"; the pruning count itself is NOT-ABOUT-THE-WORLD |
| tree.py::tree_shadow_cuts#no doubled band | RECORD-SILENT-BEFORE 0081 drawing |
| tree.py::tree_shadows#no doubled band | RECORD-SILENT-BEFORE 0081 drawing |
| tree.py::walked_shadows#no doubled band | RECORD-SILENT-BEFORE 0081 drawing |
| web/skeleton.py::_lay_skeleton#no skeleton under two houses | NOT-ABOUT-THE-WORLD |
| web/skeleton.py::served_arm#shortest arm | NOT-ABOUT-THE-WORLD |
| web/tidy.py::tidy_lane_ends#a row's street not dropped… | ANSWERED by 0033 drawing (the street is the road the row stands on, laid before the farms, running on off the map) |
| web/tidy.py::tidy_lane_ends#shortest lane kept | NOT-ABOUT-THE-WORLD |

## Leads not followed

- Yanagita's 『葬送習俗語彙』 and local folk records under 葬式道 / 葬道, for a fixed funeral path in a village.
- The Xi Songbi village paper (defensive village lanes, analysed by "交叉节点", junction nodes), for counts of T against cross junctions; I only had its abstract.
- The Azumino 「岩原山澤付道程覚」 (a late-Edo record of routes into the commons mountain), behind the unreadable map PDF.
- Chinese 出殡 不走回头路 (a funeral not returning by the same road), the Chinese side of the roundabout procession.

Pages saved under /tmp/l7r-pass/a2-odoguchi, /tmp/l7r-pass/a2-nobeokuri, /tmp/l7r-pass/a2-longli2 and /tmp/l7r-pass/a2-longli (the rejected page).

Sources:
- [kotobank 野辺送り](https://kotobank.jp/word/野辺送り)
- [JAANUS ōdoguchi](https://projects.mcah.columbia.edu/jaanus/node/1897)
- [Sohu, Longli](https://m.sohu.com/a/166996636_226858)
- [ifeng, Wangnao (rejected)](https://news.ifeng.com/c/8c0j1wcFOrS)
- [Azumino PDF (unreadable)](https://www.city.azumino.nagano.jp/uploaded/attachment/58810.pdf)
- [Boeing, arXiv 1708.00836](https://arxiv.org/pdf/1708.00836)
- [WSDOT RDI](https://data.wsdot.wa.gov/arcgis/rest/services/Shared/ActiveTransportationData/MapServer/4)