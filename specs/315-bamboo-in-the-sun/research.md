# Research: bamboo held out of a yard's or bed's sun

## R0 Historical grounding (constitution XII, the opening bookend)

**What the reality was.** Farm households kept bamboo on the farmstead - in their own grove, low under the tall trees, on the
windward side, and as stands of their own (`research/questions/0075-bamboo-groves-chikurin.html`). The Tonami plain's
institute lists the grove's bamboo stands as madake, moso, hachiku and yadake (0075). A bamboo stand is a thicket, and the
record has it shading out almost everything under it (0075; `land/tiles.py` `BAMBOO_SHADE` cites it).

**How tall** (source-reader, 2026-10-02, the pages saved with `make source-pages` and grepped; READ on each):

| kind | height | page |
|---|---|---|
| madake (真竹) | culms 10-20 m: 「真竹（マダケ）は、稈の高さは10～20メートル、直径5～15センチ程度になる竹。」 | taketora.co.jp/c/special/bamboo |
| hachiku (淡竹) | 10-15 m: 「淡竹（ハチク）は、大きさは真竹と同じか少し小降り、高さ10～15メートル…」 | the same |
| moso (孟宗竹) | the largest in Japan, culms 10-20 m: 「国内の竹では最大の大きさで稈の高さは10～20メートル…」 | the same |
| yadake (矢竹) | culms 2-5 m (Nakai): 「稈は高さ2～5m、中空、直径5～15mm」; its life form 「ササ類」, a bamboo grass | mikawanoyasou.org/data/yadake.htm |
Read: observed 2026-10-02; method: each page saved with `make source-pages` and confirmed by source-reader.

Other pages give yadake 1-3 (to 5) m, 2-6 m or about 4 m (the same survey page's header, Kotobank's dictionaries); the
Nakai range is the one cited. That yadake is a bamboo grass is READ; why it is so classed is on no page read, and is not
claimed. The ministry's bamboo page refused the fetch (HTTP 403) and is not relied on. (Observed 2026-10-02; method: the same source-reader read.)

**What the record does not hold.** No page read measures how far a farm's bamboo stood from its yard or bed, as none does for
its trees (0038).

**What our maps draw** (one-shot count, observed 2026-10-02; method: stands from `bamboo_stands`, culm marks parsed from each
SVG by their culm stroke, each tested against every plot's sun ground at the canopy reach): 3 stands and 329 culm marks on
the five pool hamlets, none in a plot's sun ground.

**The decision it supports.** Bamboo is not low enough to exempt: the timber bamboos' least cited height, 10 m (madake,
hachiku and moso all reach it), is the height the canopy reach is worked out from, so the same derivation gives bamboo the
same reach. Yadake is shorter, but in the Tonami grove it stood beside the three timber bamboos, and our patches and marks
draw no kind, so the tall ones decide. (The heights as observed 2026-10-02 above; method: the R0 reading.)

## R1 Where bamboo is drawn (the inventory, read 2026-10-02)

| site | placed in | tested today against | recorded |
|---|---|---|---|
| culm marks in a clump (farm grove, windbreak, belt) | `homestead_parts/groves.py` `_draw_grove` | roofs and wellheads (`krect`, `kcirc`), crowns over it | no |
| a household's stand (22 x 16 ft) | `hamletgen/homesteads/bamboo.py` `household_bamboo` | footprints, lanes, paddy, marsh, pond, seats | `bamboo_stands` (role homestead) |
| a shared thicket | `hamletgen/hinterland/bamboo.py` `bamboo_seats`, drawn by `homestead_parts/stands.py` `bamboo_stand` | `BambooObstacles` (houses, yards, gardens, sheds, lanes, paddy, marsh, pond, belt, coppice) | `bamboo_stands` (role thicket) |
Read: observed 2026-10-02; method: the code read at the claim's commit.

Both stand placers run in `stage_hinterland`, after every plot stands, so a plot's sun ground is whole when they ask. The
culm marks are drawn with their clump, the same call that already holds its crowns to `_sun_keepouts` (feature 310).

## R2 The reach

The canopy reach (`tree_shade.CANOPY_SHADE_FT`, 50 ft) is the 3 pm late-autumn shadow of a 10 m (~33 ft) plant at 38
degrees north, east component (0038 drawing: about 64 ft long, about 50 ft of it east; the 9 am shadow mirrors it). A
bamboo stand reckoned at the timber bamboos' least height, 10 m, throws the same shadow, so `BAMBOO_SHADE_FT` comes to the
same 50 ft - a constant of its own, with its own derivation, so that if either height is ever revised the other does not
move with it. (Observed 2026-10-02; method: the 0038 drawing page's worked shadow, read.)
