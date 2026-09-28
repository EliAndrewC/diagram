# 271 V1 handoff - homesteads: the farmhouse (session 1, research and write)

- SECTION=homesteads/400
- SECTION=homesteads/410
- SECTION=homesteads/420
- SECTION=homesteads/430
- SECTION=homesteads/440
- SECTION=homesteads/130
- SECTION=homesteads/120
- KEY=nihonminkaen-kanto
- KEY=nihonminkaen-kanagawa
- KEY=kotobank-nihon-no-minka
- KEY=irimoya-jawiki
- KEY=sanheyuan-zhwiki
- KEY=minnan-architecture-zhwiki
- KEY=huipai-zhwiki
- KEY=sekkei-sya-sayama-kura
- KEY=bunka-sado-tsuchiya-dozo
- KEY=bunka-fujino-naya
- KEY=bunka-fujii-naya
- KEY=bunka-mori-naya

Changed registry entry: `kotobank-minka` (its limits and uses widened to the house-size count and the regional forms).
New glossary terms: sanheyuan (10740), chumon-zukuri (10750), bunto house (10760).

## Items

- A68 A69 D99 CONTRADICTION-RESOLVED - an eighteenth-century count of every house in villages near Utsunomiya found about 20 tsubo (66 m2, ~710 sq ft, ~35 x 20 ft) the commonest, many under 10 tsubo and few large ones (kotobank-minka, Nipponica); the measured survivors (Nihon Minka-en, 5 farmhouses, 3 of them headmen's) are 13.6-16.4 m by 7.3-9.1 m, 1.6-2.0 long to deep, a headman-class Chiba house 10 x 6 ken, the largest headman's house 30 m (homesteads/400; 130 now cites the measured ratios) - the drawn 46 x 28 ft farmhouse (~36 tsubo) is a headman's / well-off house, not an ordinary one: draw an ordinary household near 35 x 20 ft, poorer down to ~25 x 14 ft, and keep 46 x 28 ft and up for the headman and the better-off (the small houses' length-to-depth is a GUESS carried over from the survivors' 1.6-2.0). The 130 band (1.3-2.5, bar at 2.7) stays as a calibration; it contains every measured ratio.
- A70 D101 KNOB - three roof shapes (gabled, hipped, irimoya), the basic Edo farmhouse a rectangle under hip or gable; irimoya for ordinary houses mostly in the hills from Kyoto to Kai/Sagami/Musashi, gabled thatch around Enzan, Yamato-mune in Kawachi-Nara; the covers thatch, stone-weighted bark or board, two kinds of tile; headmen's houses thatched like the rest; south China white walls under dark tile (Huizhou), the swallowtail ridge for temples, mansions and halls (homesteads/410) - roll hip / gable / irimoya PER SETTLEMENT (share a GUESS; no page counts it); thatch for every Japanese farmhouse, headman included; tile on the kura; in a Chinese-leaning village tile on the houses, a thatch-or-tile split for the poor there a GUESS (silent: Baidu pages would not load). The from-above reading (gable = full-length ridge; hip = shorter ridge with diagonals to the corners; irimoya = hip with a small gable triangle at each ridge end) is a convention on grounds.
- A71 KNOB - straight house (sugoya) the plain form; L forms: magariya (N Miyagi - S Iwate, horse-breeding districts, stable wing forward of the doma, in Nanbu commoner among upper farmers as a mark of rank), chumon-zukuri (Yamagata/Akita/Fukushima), tsunoya (west Japan); bunto two-roof house (S Kumamoto - Kagoshima, and in the 18th c. many near Utsunomiya; museum examples from Ibaraki and Chiba); China: three-sided sanheyuan found all over China, with the single-range and L forms beside it (homesteads/420) - roll the plan per settlement: straight everywhere as the base; L in horse-raising northern country, weighted to the headman and better-off; two-roof bunto in the south of Kyushu and the Pacific side; three-sided court (or its single-range / L forms) in a Chinese-leaning village; shares a GUESS (no count read).
- A78 CONTRADICTION-RESOLVED - a farm kura was about 2.5 x 3 ken (~15 x 18 ft), two stories (the standard size in one surveyed Musashi district; a Sado farm grain kura 34 m2), earth-walled 20-30 cm under a separate tile roof; built when money accumulated (in that district probably only from the bakumatsu), standing free of the house in front of it or behind, rarely against its downwind side, on no fixed compass side (homesteads/430; 120 now flags its annex rule as a contradicted convention) - the generator draws the kura as an ANNEX on the WEST (scattered) / NORTH (cluster) wall: it should draw it freestanding at ~15 x 18 ft, tiled, in front of or behind the house on a side rolled per farm. The ~30% share in 120 is untouched.
- A79 ACCURATE (thin) - a naya is a freestanding storage shed for the crop and tools; three registered farm barns measure 6.9 x 3.9 m (~23 x 13 ft), 11.7 x 4.9 m (~38 x 16 ft) and 99 m2, all gabled and tiled, all late (1883-1926) and of well-off households near Osaka and in Kagawa, sited southeast of the house, between a detached room and the rice kura, and at the plot's east end; an ordinary Edo farm's naya size is SILENT (absence note) (homesteads/440) - draw the farm shed as a long narrow gabled freestanding building ~20-30 ft long and half as deep (the low end, a GUESS for an ordinary farm), on a side rolled per farm.

## Owed to other owners

- 269 (homesteads 140, 145): 140's storehouse and shed rows and 145's magariya passage should point at homesteads/430, /440 and /420 respectively (140 carries only counts; 145 carries the magariya's region, now answered as a plan-form knob at 420). Nothing in 140 or 145 is contradicted.
- 269 / the prefix ledger: the glossary loader refused five-digit prefixes; this clone carries the IDENTICAL patch from diagram-supplemental's d3449eda (glossary_source.py + its test), so the two merge clean - but it is engine code, so this clone's push is GATED. PREFIX COLLISION: diagram-supplemental's tree holds `10760-memorial.json` and `10770-four domestic carps.json`, while the ledger reserves 10760 to this clone (bunto house) and 10770 to diagram-research-5 (waki-honjin); `term_files` refuses a repeated position, so whichever lands second must renumber through `make reserve`.

## Left open

- Modal prose: the Farmhouse and StorageShed class docstrings (and the kura class) owe rewrites from 400-440 by the orchestrator; 120 and 130 bodies changed, so `_entry_owed.py` will name the classes whose `Entry:` cites them.
- The source pages are saved in /tmp/l7r-check/271-v1-pages (MANIFEST.txt). Two PDFs (kyoei repo "Kanto minka history", Shibaura IT "farmhouse-type minka") had no text layer and were not read; the Edo beam-span limit on peasant houses (梁間 restrictions) was searched and not found on a readable page - it would explain the depth cap, and is a candidate for TO-DOWNLOAD if a later pass wants it.
- source-applicability has not run on the 12 new keys (the check sessions do that).
