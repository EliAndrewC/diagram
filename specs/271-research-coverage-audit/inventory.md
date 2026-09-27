# Inventory - feature 271, the research coverage audit and backfill

Built 2026-09-27 from the four audits beside this file: `audit-farming.md` (A01-A155), `audit-towns.md` (B01-B132),
`audit-cities.md` (C01-C175) and `audit-buildings.md` (D01-D158). Each audit row carries a status (NONE, THIN,
COVERED) and an owner. This inventory keeps every row 271 owns whose status is THIN or NONE, and the COVERED rows where
the audit named a part still thin. The same thing asked at several tiers (inns, smiths, bathhouses, markets, bridges,
streets) is ONE row here, its question spanning the tiers and listing every source id. Page paths are under
`.claude/skills/diagram/research/`. Sizes S/M/L. Priority: P1 = drawn on a map already (the scripted pool, the
hand-drawn pool, the magistracies, `wip/`); P2 = village tier, not drawn yet; P3 = town tier; P4 = city or capital
tier. A merged row takes the highest priority of its ids.

Rows are packed into write groups of 4-7 related rows that land on ONE research page. Each group owns a range for NEW
questions on its page, counted by ten. The range is above every fragment number on that page in this clone and in
`diagram-supplemental`, `diagram-buildings` and `diagram-shrines` (listed 2026-09-27), and outside the ranges 267 and
269 reserve. A group may also edit the EXISTING sections its rows name, unless another feature owns that section (see
below); then the new question cites it. Group prefixes: V = village tier on the farming pages, W = ways, U =
urban-features, T = towns, K = cities/*, G = buildings, R = religion-and-death. W is added here because the ways page
carries two groups. No new page was needed.

## Owned elsewhere (not this feature's)

Rows below are left to their owner. A 271 row that touches one of these sections cites it and does not edit it.

- **Feature 267** (diagram-buildings): `future-work/compounds.md` "Research owed" R01-R53, the magistracy and compound
  buildings, and the in-field grave island (R52). Its reserved ranges: buildings 240-640, vegetation 170-200,
  religion-and-death 220-260, fields 220-240, cities/river-cities 050-080, urban-features 190-220, ways 060-090. Rows:
  A19 (R52); B22 and C135 (R46, carts); B83 and D35 (R25, the bench's own board); C48 and D14 (R18, the grain kura's
  raised floor); C115 and D16 (R16, stalls); C162 (R42, the wharf's face); C166 (R40, the river watch); D06-D10,
  D17-D34, D37-D42 (R01-R53); D86 (R52). The bath part of C76 (R09) and the 67-tsubo house of C74 (R15) are 267's; the
  rest of those rows is 271's.
- **Feature 268** (Diagram shrines, landed): religion-and-death 080-126 and 128 - torii, the village and country
  shrine, its dwelling, land and festival ground. Rows: A134, A136, A155, B102, C153, D48, D55, D57.
- **Feature 270** (Diagram shrines, "the shrine hall sized from the research"): the village and country shrine HALL's
  size and the shrine precinct rows. Rows: A133 (the shrine's size), A135, D49, D50 (the kuri), D51 (the bell tower),
  D52, D53, D54, D56. A town's or a city's own shrine (B101, C152) is not a village shrine and stays 271's.
- **Feature 269** (Diagram supplemental), its inventory B01-B46. Its reserved ranges: fields 250-360, homesteads
  250-360, water 290-360, vegetation 210-290, archetypes 200-270, religion-and-death 270-330, cities/defenses 100-140,
  cities/government 100-140, cities/fabric 160-190, cities/hinterland 060-090, cities/sizing 030-050, settlements
  090-110; and edits to the thin sections on 265's pages (towns 020, 110, 120, 140, 150; buildings 110; cities/capitals
  380, 390; cities/river-cities 030; ways 050). It owns cities/defenses' gate towers, guard and inspection stations,
  moat, patrol road and rampart fence (B38), and cities/government's servant nagaya, martial training, ashigaru plots,
  samurai count and ward gates (B39). Rows: A02, A04, A06, A09, A11, A13, A14, A16, A20, A23, A28, A29, A33, A34,
  A38, A40, A41, A42, A43, A44, A53, A57-A60, A64, A67, A72, A73, A81, A85-A89, A91, A92, A98-A103, A106-A111,
  A113-A115, A123, A141, A142; the terrace section archetypes/040 of A12, the headman section homesteads/110 of A74,
  the fuel-wood siting of A120 (vegetation 220), the entrance stone of A128; B01, B35, B79, B80, B100 (the ratio),
  B104, B106, B120, B122, B126; the city side of B08, B36 and B77; C04, C06, C08, C10-C15, C37, C68, C69, C73, C77,
  C78, C80, C87, C88, C90, C105, C112, C140, C145, C148, C154, C156, C160, C169, C173, the retreats of C174; D43, D46,
  D47, D59, D60, D67, D71, D74, D81-D85, D89-D92, D94, D98, D100, D105, D106, D119, D122, D123, D131, D132, D141,
  D142, D155.

## Passed over, and why

- D156, D158 and the convention part of D157 (`presentation/010-070`): map drawing conventions, the GM's rulings; no
  source is owed.
- A45 (`water/200`, how a junction is drawn): a drawing convention.
- COVERED rows with nothing named as thin: nothing is owed on them.

## V1 - homesteads: the farmhouse (new: homesteads 400-450)

- A68 A69 D99 **Farmhouse size and proportion**: how big is an ordinary farmhouse (the drawn 46 x 28 ft), how does it
  vary with the household's standing, and within what proportions is it longer than deep? (homesteads/130). M. P1.
- A70 D101 **Farmhouse roof from above**: thatched hip, half-hip, gable, shingle or tile, by region and wealth, Japan
  against south China, and how it reads from above? (none). M. P1.
- A71 **Farmhouse plan form by region**: the straight minka, the L-shaped magariya, the south-China three-sided
  courtyard house - which regions, and which should the maps draw? (homesteads/145, homesteads/130). M. P1.
- A78 **Farm storehouse size and siting**: how big is a farm kura, what is it built of, and where on the plot does it
  stand? (homesteads/120, homesteads/140). S. P1.
  > COORDINATION (A78): 267 R18 (granary stilts, the raised floor) is the magistracy granary, a different building - cite it for the raised floor if it comes up
- A79 **Farm shed (naya) size**: how big is a farm shed, and where on the plot? (homesteads/140). S. P1.

## V2 - homesteads: the yard and its animals (new: homesteads 460-510)

- A82 **Draft animals**: ox or horse, by region, and what share of households kept one? (homesteads/070,
  homesteads/145). M. P1.
  > COORDINATION (A82): read 269 B16 (homesteads 300, in diagram-supplemental) first; if it answers the share of households, cite it and keep only ox against horse by region
- A83 **Pigs and poultry in a paddy hamlet**: did an ordinary south-China paddy hamlet keep pigs, poultry and ducks, and
  where (the sty is drawn only on dike-pond hamlets)? (archetypes/171). M. P1.
  > COORDINATION (A83): narrow to pigs and ducks on a PLAIN paddy hamlet; chickens are answered by 269 B13 (homesteads 250/218, Buck: 82% of farms) and dike-pond sties and pens by 269 B32 (archetypes, group A1) - cite both, read them in /diagram/.clones/diagram-supplemental
- A95 **Farmstead boundary**: a hedge (ikegaki), a stone wall, an earth bank or nothing, and how does it show?
  (homesteads/145). M. P1.
  > COORDINATION (A95): 269's vegetation 270 windbreak grove is the boundary planting on many farmsteads - cite it; the hedge, wall and bank question is ours
- A148 **Communal threshing floor**: did a south-China village thresh and dry on a shared floor (a stone roller, the
  drying ground before the hall) rather than each dooryard, and how big? (homesteads/020). M. P1.
  > COORDINATION (A148): 269 B05 (fields 290-310) covers the straw rick - cite it; the threshing floor is ours
- A17 **Drying racks (hasa)**: where were rice-drying racks put up - along bunds, by the lane, in the yard - how long,
  and how many per household? (homesteads/145). M. P2.
  > COORDINATION (A17): 269 B05 (fields 290-310, in diagram-supplemental) covers nimosaku and the straw rick - cite it for the rick; the racks are ours

## V3 - fields: bunds, crops and field features (new: fields 400-450)

Also edits fields/010, 022, 050, 100.

- A05 **Bund course**: does a bund run on or turn, never stepping sideways and carrying on? (fields/022, no
  footnotes). S. P1.
- A07 **Lowest bund**: is the lowest bund of a paddy laid with the drain or across it? (fields/100, no footnotes). S. P1.
- A15 **Dry crops from above**: what do millet, buckwheat, barley and soy look like from above in season (rows, color,
  height)? (fields/050, fields/160; 269 B07 owns 160's placement). M. P1.
- A18 **In-field ponds and rocks, the rates**: how often a flooded paddy keeps an in-field pond or rock (fields/010,
  thin on rates). S. P1.
- A27 B125 **Flower field**: what is the Imperial chrysanthemum field on Hirameki, and did a town's ring grow flowers
  for the market or the shrine, in plots of what size? (none; settlements/080 names it). S-M. P1.

## V4 - water: village water works (new: water 400-450)

- A37 **Division works**: how was a ditch split between users (a division weir, a notched board, bunsuiban), and what
  shows of it? (water/240, fields/070). M. P1.
  > COORDINATION (A37): 269 B22 (water 300, 310, in diagram-supplemental) covers the village weir forms and the intake mouth - cite them; the division between users is ours
- A46 **Water-lifting devices**: the treadle wheel (fumiguruma), swing bucket (hanetsurube) and the Chinese chain pump
  (longgu che) - did a village lift water onto its fields, with how many, and what shows on a map? (none). M. P2.
- A47 B62 **Mills**: did a village have a water mill (suisha) for polishing rice or grinding, how many, where on the
  stream, how big and whose; and where was a town's grain milled - water mill, ox mill, hand quern, China against
  Japan? (none). M. P2.
- A48 B117 **Washing places and other water**: where did a village or town wash vegetables and clothes (araiba,
  kawabata - steps down to a stream or ditch), how many, and did a town draw water besides its wells (street channels,
  a stream-fed runnel)? (none). M. P2.
- A49 **Flood works**: the village ring levee (wajū), the flood-refuge storehouse on a mound (mizuka), a raised house
  base - what did a river-plain village build, and where? (none). M. P2.

## V5 - archetypes: terraces, overlays and polders (new: archetypes 300-350)

Also edits archetypes/020, 080, 150, 160.

- A12 **Terraced paddy**: the riser height and the terrace plot size on a slope (archetypes/040 is 269 B35's; cite it;
  fields/024). M. P1.
- A21 **Overlay crop extent**: how much of a village a cash-crop overlay covers (mulberry fishpond, lotus, tea fringe)
  (archetypes/020, no footnotes). S. P1.
  > COORDINATION (A21): 269 B33 (mulberry density and crown width, group A1) is density, not extent - no overlap; cite it once written
- A24 **Plot tenure in the pattern**: scattered strips per household, warichi redistribution, tenant plots - does it
  show in the plot pattern? (archetypes/050; 269 B35 owns 050/060's edits, so this is a new question). M. P2.
- A62 **Polder perimeter dike dimensions**: how high and wide is a polder's dike? (archetypes/080). S. P1.
- A66 **Polder drainage**: a sluice at low tide, a lifting pump - how did a polder get rid of its water, and what
  shows? (archetypes/150, archetypes/160). M. P1.

## V6 - vegetation: farmstead trees, landmark trees, meadows and kilns (new: vegetation 300-340)

- A93 **Other farmstead trees**: plum, chestnut, loquat, a mulberry or tea hedge - which stood on a farmstead, and how
  many? (none). M. P1.
  > COORDINATION (A93): vegetation 260 (bamboo), 270 (the grove's species) and homesteads 218 (persimmon), all 269's in diagram-supplemental, already name grove trees - take only fruit and hedge trees they do not list
- A25 A26 B123 B124 **Fodder meadow, hayfield and grazing commons**: did a village keep a cut meadow or common for
  fodder and green manure (kusakariba, magusaba), how large against its paddy, and where; where does a hayfield or
  grazing ground stand and how is it bounded (the hand-drawn towns label "hayfields & grazing"); and what grazing,
  common and hayfield ground surrounds a town for its draft and relay stock (Hoshizora's hayfield)? (none; the commons
  tiling is open, fc:1421). M. P1.
- A117 **Landmark tree**: did a village keep a great old tree at a crossroads, the entrance or a well (enoki,
  zelkova; China's village-mouth tree), and where? (none; the shrine's sacred tree is 268's). S. P2.
- A120 **Village charcoal kiln**: did a village burn charcoal (sumigama) in its hill ground, and did a kiln show?
  (none; the fuel-wood siting is 269's vegetation 220 - cite it). S. P2.

## V7 - homesteads: the headman and the village's households (new: homesteads 520-580)

Also edits homesteads/180.

- A74 D95 **Headman's house as a building**: what did a headman's (shoya, nanushi) homestead carry that others did
  not - a gate (nagaya-mon), a genkan, an office room, a wall or hedge (against the GM's no-wall ruling), how many
  kura - and how big was its plot? (homesteads/110 is 269 B19's; cite it; homesteads/145). M. P1.
- A75 **Headman's house siting**: the center, the oldest spot, by the shrine, on the road? (none). S. P1.
- A76 D97 **Poor and tenant houses**: were landless and tenant households (mizunomi) housed in smaller huts, how
  small, and where in the village? (none). M. P2.
- D96 **Wealthy farmer's house**: how did a well-off farmer's or landlord's (gōnō) house differ from a plain farmhouse
  in size and outbuildings? (homesteads/120, kura only). M. P2.
- A146 **Village meeting place**: where did a village meet (yoriai) - the headman's house, the shrine, a hall of its
  own - and how big and where was it? (none; D104 asks it with the granary, which is U4's). M. P2.
- A147 **Lineage ancestral hall**: did a south-China village's lineage hall (citang) front the crescent pond, and how
  big was it? (homesteads/180, no footnotes; 269 B19 owns 180's packing claims, so this is a new question). M. P2.

## W1 - ways: village roads, entrances and crossings (new: ways 100-150)

- A124 **Lane surface**: bare earth, gravel, stone steps on a slope - what was a village lane surfaced with, and does it
  show? (none). S. P1.
- A128 B21 **Where a settlement begins**: how is a village's or town's entrance marked - a wayside deity (dōsojin), a
  rope across the road (kanjō-nawa), a gate post, a mitsuke, a roadside tree - and how many? (religion-and-death/210;
  the entrance stone is 269 B20's; cite it). M. P1.
- A129 **Village boundary**: how was the line between two villages marked (mura-zakai stones, a ridge or stream), and
  does a village map show it? (none). S. P2.
- A126 A154 B76 **Roadside teahouses, inns and rest stops**: how does a village lay itself along a highway it straddles
  (kaidō-zoi), and what fronts the road - teahouses, an inn, a rest stop (tateba, tatebazaki), a milestone mound
  (ichirizuka); did rest stops stand at a town's ends? (cities/fabric/050, city). M. P2.
- A127 B131 C168 **Ferry landings**: where a village's, town's or city's road met a river with no bridge, when was it a
  ferry, how was the landing (watashiba) laid out, and how many kept one? (water/130, a mention). M. P2.
  > COORDINATION (A127): 267 R42 (stepped landings or a pier, gangi, on river-cities) and R40/R41 (the river guard post, the boatmen's altar) are landing features - cite them; keep A127 to the ferry crossing itself

## U1 - urban-features: public fixtures and works on the map (new: urban-features 250-300)

Also edits 015, 052, 068, 090.

- A131 B24 **Notice-board seat**: how does the map choose the board's seat, and may it stand under a tree?
  (urban-features/015, no footnotes). S. P1.
- A132 **Notice-board form**: how big was a village or town board, and what did it look like from above (roofed,
  fenced, on a stone base)? (urban-features/010). S. P1.
  > COORDINATION (A132): 267 R25 kept the magistracy bench's own board apart from the town's kosatsuba - cite it for the distinction
- A51 **Rural well siting**: where does a village's communal well stand - a dooryard, a lane side, the commons (the
  Inashiro south well, fc:2063) - and was there a well house? (urban-features/090, 120; homesteads/145). M. P1.
- B116 **Wellhead form**: what does a town's communal well look like from above - curb, frame, pulley, roof?
  (urban-features/090). S. P1.
- B55 C125 **Kiln works form**: what does a climbing kiln look like on the map, and its fire gap? (urban-features/052).
  S. P1.
- B59 C127 **Tanning-yard direction**: which way out of a town or city does the tanning yard stand?
  (urban-features/068). S. P1.

## R1 - religion-and-death: swept ground, graves and the tier program (new: religion-and-death 400-440)

Also edits 140, 210.

- A137 D88 **Swept ground**: is the ground round a shrine or grave swept clear, and why the ragged edge?
  (religion-and-death/140, no footnotes). S. P1.
- A143 **Hamlet burials**: where does a hamlet bury its dead - household plots beside the farmstead (yashiki-baka), a
  shared hillside, the district's ground? (religion-and-death/210; field graves are 267's R52). M. P1.
- C157 **Pauper ground**: one per seat, and its size (the 10-30 ft is a guess)? (cities/capitals/333). S. P1.
- D63 **The tier program**: what religious and funerary features does each size of settlement carry?
  (religion-and-death/210, 1 note, 1 absence). M. P1.

## T1 - towns: the town as a whole (new: towns 200-250)

- B02 **Post town**: what distinguishes a post or relay town (shukuba, Chinese yizhan town) from a market county seat
  - its length along the road, household count, what it must keep standing? (towns/050 names the shukuba). M. P1.
- B03 **Town extent**: how long and deep is a town's built core - a road town's strip length (chō), a nucleated seat's
  acreage for ~80 non-farming households? (none). M. P1.
- B04 **Town density**: how densely is a town's commercial core built against its farm zone (households per acre, the
  share of ground built)? (cities/sizing/020, city only). M. P1.
- B05 **Town plan form**: linear road town, crossroads town or planned rectangle - which did Japanese and Chinese county
  seats take, and how often (a knob)? (towns/010). M. P1.
- B06 **Walled or unwalled**: what share of county seats were walled (Chinese most, Japanese almost none), and what
  makes a town walled? (towns/100). M. P1.
- B12 **Town by region**: how does a Japanese county town differ on the ground from a Chinese one (courtyard houses
  against machiya, wall or none, the yamen axis against a jin'ya at the edge)? (towns/010, cities/fabric/010). M. P1.

## T2 - towns: houses on the street (new: towns 260-310)

- B27 D109 **Shophouse size**: what frontage and depth does a merchant's shophouse take by wealth in a county town and
  a city, Japan against China (Kyoto's 2-3 by 10-12 ken is a city's; the 48 x 32 ft glyph)? (cities/fabric/020,
  urban-features/100). M. P1.
- B29 **Party walls in a town**: does a county seat build its street front in continuous party-wall rows, or as
  detached houses with gaps? (cities/fabric/010, city). S. P1.
- B30 D113 D114 **Stories and roofs**: one story or two, and thatch, board-and-stone or tile - what did a town's and a
  city's street front look like from above (machiya, inn, merchant kura), and did fire law shape it? (towns/050, the
  inn only). M. P1.
- B33 C85 **Laborer dwelling**: what does a laborer live in - a detached hut, a nagaya row unit, a back tenement
  (uranagaya) - and how big is a unit and its block, per household, in a town and a city? (cities/fabric/010,
  cities/capitals/100). M. P1.
- B34 **Large laborer house**: what is the drawn "large laborer" house - a labor boss's (oyakata) house, a porters'
  boarding house - and its size? (none). S. P1.
- B38 **Town door orientation**: which way does a town house's door face, and how deep do rows stack?
  (cities/fabric/110, city). S. P1.

## T3 - towns: inns and the post station (new: towns 320-370)

- B67 B68 C110 D135 **Inns, count and size**: how many inns did a county town, a post town (a Tōkaidō shukuba ran
  dozens of hatago) and a city keep, how big is a hatago, a wagon inn or a Chinese kezhan on the ground, with how many
  rooms and stories and what yard? (towns/050; cities/fabric/120 has the city count). M. P1.
- B70 **Imperial waystation**: where does the setting's Imperial road waystation (canon: 25-30 staff, relay horses at
  a busy station) stand against a town, and what is its footprint? (none). M. P1.
- B71 B72 D138 C45 **The post-horse office**: what did a post station keep - the toiya-ba (horse and porter office)
  with its horse yard, the relay horses and porters (how many), their stables and quarters - and does a provincial
  city keep one (tenma-sho)? (cities/fabric/130, urban-features/080). M. P1.
- B73 B74 D139 C114 **Stables and stable yards**: how big is an inn's or a relay's stable and how is it laid out, and
  what is its yard's ground like? (towns/050, urban-features/080, 1 note; 082's watering is covered). S-M. P1.
- B69 C111 D137 **Official lodging**: where did traveling lords and officials lodge in a post town or a seat on the
  highway (honjin, waki-honjin; the yamen's guest house), and how big was it? (267's buildings/330 mentions it). M. P3.

## T4 - towns: the town's edge (new: towns 380-430)

- B11 **Gate market size**: how many buildings and which trades make up a county town's gate market, and how far does
  it run out the road? (towns/080; the city strip is 269 B41's, cities/hinterland/040; cite it). M. P1.
- B41 **Town barns**: what are the barns of a town's hayfield (Hoshizora's five) - hay barns, ox sheds - and their
  size? (none). S. P1.
- B132 **Edge woods**: why is a town's margin clothed and not left bare, and with what? (water/170,
  vegetation/030). S. P1.
- B129 **Suburb along the road**: where does a town's built edge stop - does a ribbon of houses run out along the
  road past the last block (machi-hazure)? (none). S. P3.
- B128 C174 **Market gardens and the suburban belt**: did a town's or city's edge carry vegetable plots supplying it,
  fed by its night soil, and what else stood in a city's near hinterland (suburban villages, tile and lime works), how
  far out? (cities/hinterland/050; the retreats are 269 B41's). M. P3.

## W2 - ways: streets, bridges and approach roads by tier (new: ways 160-230)

- B14 C89 **Street widths**: how wide is a town's and a provincial city's main street, side street and lane, and the
  Imperial or trunk road where it runs through? (ways/020 village; cities/capitals/210 capital; towns/090). M. P1.
- B15 C101 **Street surface and drains**: beaten earth, gravel or stone (China), and did town and city streets carry
  drains or gutters (dobu), how wide? (cities/fabric/080 says unpaved on general reading; 269 B40 owns 080 - cite it).
  M. P1.
- B16 **Cross streets**: how many cross streets does a town have, in what pattern - T junctions, a defensive crank
  (masugata) at the town's ends? (none). M. P1.
- B18 C86 **Back paths**: how is a packed commoner quarter crossed - trodden footpaths or alleys, how wide, and why is
  the path not a street? (urban-features/110, no source cited). S. P1.
- B19 **The Imperial road in a town**: what lines it, and is it labeled? (cities/fabric/040, 050, city). S. P1.
- B20 C167 **Town and city bridges**: how many bridges does a town or city carry over its river and canals, of what
  type (plank, earth-decked, arched timber, stone), how wide and how long? (ways/010, 030, village). M. P1.
- C175 **Approach roads**: how wide are the roads into a city, and what lines them past the gate market (a tree
  avenue, milestones, shrines)? (ways/020; 267's R47 is a compound's gate). M. P1.

## U2 - urban-features: shops, counts and premises (new: urban-features 310-360)

Also edits 030.

- B42 C104 **Shop count**: how many shops does a county seat of ~1,200 and a city of a given size carry, of which
  trades? (towns/020 canon; cities/fabric/050, a floor calibrated on our maps). M. P1.
- B43 **Shop footprint**: how big is a town shop as premises apart from its owner's house? (urban-features/030, the
  48 x 32 ft glyph). S. P1.
- B44 **Trades that outgrow the glyph**: which need premises larger than a shophouse (many figures are "this page's
  estimate")? (urban-features/030). M. P1.
- B50 C121 **Oil press**: does a town or city keep an oil press, how big, how many (the count is a guess), and where?
  (urban-features/030). S. P1.
- B51 C118 **Pawnshop**: does a town keep a pawnshop, what is its tell on a map, and how big is the pledge court (its
  size unquoted)? (urban-features/030, cities/capitals/330). S. P1.
- B118 C117 D147 **Bathhouse**: how many public bathhouses (sentō, Chinese yushi) per population, does a county town
  of ~1,200 keep one, and how big is the bathhouse with its furnace and fuel yard? (urban-features/030,
  cities/capitals/330). M. P1.

## U3 - urban-features: quarters, fire and the night (new: urban-features 370-420)

Also edits cities/fabric/060, towns/070.

- B108 C98 **Burakumin quarter size and houses**: how many households and what dwellings does a town's or city's
  quarter hold, its own well and shrine, and where does it lie against river, tannery and execution ground? (towns/020
  canon count; urban-features/066, 068). M. P1.
- B110 C97 **Inside or outside the wall**: in a walled town or city, does the burakumin quarter stand inside?
  (cities/fabric/060, 1 note; the siege reason is the record's own). S. P1.
- B111 B112 **Fire-watch tower**: does a town keep one, only a walled one (the unwalled-none reason is a guess), and
  how tall is a hinomi-yagura and how big its footprint? (towns/070, cities/fabric/140). S-M. P1.
- B113 C25 **Fire-fighting provision**: water barrels (tenbō-oke), fire buckets, ladders, a fire pond, a watch house
  (jishinban) - what did a town or city keep in the street, and is any of it big enough to draw? (cities/fabric/140,
  143; buildings/170 is a compound's tubs). M. P3.
- B114 C35 **Night watch, guard boxes and kido**: did a town bar its streets at night, and did a city keep ward guard
  boxes (jishinban, tsujiban) or Chinese patrol stations (xunpu), how many? (urban-features/130, cities/capitals/330).
  M. P3.

## R2 - religion-and-death: town monasteries and town and city shrines (new: religion-and-death 450-490)

Also edits 040, 210.

- B96 D66 **Town monastery count**: how many monasteries does a county seat keep (canon: one per patron Fortune),
  against real county towns, and who lives in one? (religion-and-death/210, 020). M. P1.
- B97 B98 D65 **Town monastery size and layout**: how big is a town monastery's precinct and hall, walled or fenced,
  what stands in it (gate, main hall, bell, priests' quarters, graveyard), and its footprint on the town map?
  (religion-and-death/010, 040, 170; the city temple's size is 269 B37's - cite it). M. P1.
- B101 C152 **Town and city shrine**: how big is a county seat's own shrine (its chinju) and precinct against a
  village's, and does a city keep a principal shrine (the town's ujigami; the Chinese city-god temple, chenghuang
  miao), how big and where? (religion-and-death/100-126 are the village's, 268/270's - cite them). M. P1.
- C147 D70 **Clergy housing**: who lives inside a city temple's walls and who outside? (religion-and-death/040, 1
  note). S. P1.

## G1 - buildings: the magistracy's buildings (new: buildings 700-750)

Also edits buildings/060, 080, 090, 160, 180.

- D04 **Building hierarchy**: do the compound's buildings rank in size (office hall, residence, barracks, stable), and
  is there a readable source for it? (buildings/180, 1 cited, 5 absence). M. P1.
- D05 **Office hall size**: how long and deep was a county office hall (the 80-150 by 20-45 ft band is the project's
  reading)? (buildings/090, 180). M. P1.
- D11 **Tax archive**: how big was a records kura or strongroom at an office (the 32-36 ft is the vocabulary's)?
  (buildings/160). S. P1.
- D13 B82 C47 **Tax-rice granary**: how big was an office's grain kura (drawn 43-50 by 25-27 ft) and how many per
  posting; where does a county seat keep its tax rice (in the compound, or a storehouse row in a rice-transit town);
  and how big is a provincial city's granary, how many buildings, and where (the governor's compound, the wharf, a
  gate)? (buildings/080, 150; towns/110; cities/capitals/090, 360). M. P1.
- D15 **Barracks size**: how big was the working platoon's nagaya (the band is a guess)? (buildings/060). S. P1.

## G2 - buildings: houses and halls as buildings (new: buildings 760-810)

- D115 B32 **Japan or China house form**: when does a house take the Chinese courtyard form (siheyuan, sanheyuan)
  rather than the minka or machiya, by tier and class, and is the courtyard house the Chinese form of a town merchant's
  house (a knob), and its size? (buildings/010, compound interiors only). M. P1.
- D133 **Samurai country manor**: how big is one (~1 acre), and what does it hold (house, kura, gate, grove, fields)?
  (cities/capitals/100, in passing). M. P1.
- C141 D143 **Dojo as a building**: how big was a dojo's floor, hall and yard (raised board floor, spectator gallery,
  shrine shelf; the state drill hall), and what does it look like from above? (buildings/210, absence notes). M. P1.
- D110 **Merchant house as a plan**: shop front, doma passage, living rooms, rear court, kura - one or two stories?
  (towns/030, form only). M. P3.
- D136 **Inn as a plan**: guest rooms, kitchen, bath, stable yard, Japan against China? (none). M. P3.

## K1 - cities/fabric: blocks, wards and merchant estates (new: cities/fabric 200-250)

Also edits cities/fabric/100, 130.

- C91 **Block size**: how big is a city block (chō, the Chinese fang), and how many lots does it hold? (none). M. P1.
- C102 **Wards**: what is a ward as a unit - its size, its headman, its gate - and how many does a city have?
  (cities/capitals/060, the gates only). M. P1.
- B28 D117 D118 **Merchant estates**: how big is a rich merchant's house or walled compound in a town and a city, how
  many kura and what gate, as a footprint and a plan, how many per town of 1,200, and where may its wall stand?
  (cities/fabric/090, 100, 1 note, 1 absence). M. P1.
- B31 C50 D152 **Merchant storehouses**: how many fireproof kura stand behind a town's or city's street, how big, how
  far apart, and where on the lot? (cities/fabric/130, a floor calibrated on our maps; buildings/160;
  urban-features/030; 267's urban-features/210). M. P1.
- C172 **In-wall farmers**: who works the fields inside a city's wall, and where do they live, given a city has no
  farmer households? (cities/hinterland/050, settlements/090). S. P1.

## K2 - cities/government: the governor, the ministries and the urban magistracies (new: cities/government 200-270)

- C27 D125 **Governor's compound size**: how big is a provincial governor's compound in absolute terms (acres,
  frontage, depth; "a whole city block" is the page's reading) - a Chinese prefectural yamen against a domain jin'ya
  or castle-town office? (cities/government/010). M. P1.
- C28 D126 **Inside the governor's compound**: gate, office halls, courtroom, residence, treasury, granary, jail,
  shrine - in what order and at what sizes, and how does it scale from the county magistracy? (buildings/010-230, a
  county compound). L. P1.
- C29 **Governor's compound facing**: which way does it face, and is there a gate-to-yamen avenue in a city?
  (towns/010, cities/capitals/140). S. P1.
- C30 D128 **Ministry offices**: how big is a ministry office, are the six equal, and what does one hold inside
  (rooms, archive, staff)? (cities/capitals/290, 1 note). M. P1.
- C38 **The gate watch**: where does it stand? (cities/government/060, 1 note). S. P1.
- C33 **City jail**: inside the governor's compound or a separate prison, how big and where? (buildings/040,
  cities/government/010). M. P4.
- C34 D45 **Urban magistracies**: did a city keep a separate town magistrate's office (machi-bugyōsho) and constables'
  quarters, and how do the capital-stationed Imperial, Clan and Family magistrates' urban compounds differ from a
  county one (yoriki rooms, staff living out) in size and program? (none; programs.md knob 1). M. P4.

## K3 - cities/government: samurai houses and the garrison (new: cities/government 280-340)

- B36 B37 C74 D120 **Samurai house by rank**: how big were a samurai residence's lot and house by rank in a county town
  and a city (tsubo granted per stipend, frontage, house size; the senior staff officer's, yoriki-rank, house), fenced
  or walled, and where against the manor? (cities/capitals/100, buildings/180; 267's buildings/380 is the 67-tsubo
  house, and 269 B39's government/030 the count - cite both). M. P1.
- C75 **Samurai house from above**: the long-house gate (nagayamon), hedge or plastered wall, garden, kitchen yard?
  (none). M. P1.
- C76 **Samurai house well**: did a samurai house have its own well? (urban-features/120; the bath is 267's R09). S. P1.
- C43 **Garrison**: where does a provincial city's garrison live and muster, and is there a barracks or armory
  outside the castle? (cities/government/085 is 269 B39's; cities/capitals/360). M. P1.
- C44 **Drill ground**: how large was a city's drill or muster ground, and where? (cities/sizing/020, a calibration).
  S. P1.
- C142 **Archery and riding grounds**: did a castle town keep an archery range or a riding ground (baba), how long, and
  where? (none). M. P4.

## K4 - cities/defenses: town walls, crossings and barbicans (new: cities/defenses 200-250)

- B07 C03 **Rampart in section**: how high and thick is a county town's and a provincial city's rampart, rammed earth,
  stone- or brick-faced or a Japanese earthwork (dorui, sōgamae), with what parapet, how many gates, and what of it
  shows from above? (towns/100; cities/capitals/150, 155; cities/defenses/060, 269 B38's - cite it). M. P1.
- B08 **Town gate**: a gatehouse or a tower over the opening, its footprint and opening width, at a walled county town?
  (cities/defenses/030, 040 are the city's, 269 B38's). M. P1.
- C09 **Barbican**: did a provincial gate have a barbican (wengcheng) or a Japanese masugata, how large, and how
  common? (cities/defenses/050, names it). M. P1.
- C17 **Moat crossing**: fixed timber bridge, earthen causeway, stone bridge, drawbridge - how does a road cross the
  moat at a city gate, and how wide and long? (cities/capitals/240 is the castle's gates only). M. P1.
- B09 **Town moat**: did a walled county town carry a moat or ditch, and how wide? (water/110, 120 are city moats).
  S. P3.
- B77 **Town inspection post**: did a town on a road keep a barrier or inspection post, and what did it look like?
  (urban-features/140; the city's is 269 B38's). S. P3.

## K5 - cities/capitals: granaries, brokers, the castle and the lineages (new: cities/capitals 400-450)

Also edits 110, 120, 350, 360, 370.

- C49 **Emperor's granaries**: why are they separate? (cities/capitals/120, 1 note). S. P1.
- C52 **Rice brokers**: who kept the brokers' row, and what did it look like? (cities/capitals/110, 1 note). S. P1.
- C56 D129 **Inside the castle**: what stands inside the castle and what outside, and why is it drawn blank?
  (cities/capitals/350, 360, 1 note each). M. P1.
- C59 **Lineage compounds**: how big is each ruling-house lineage's compound in the capital? (cities/capitals/370, 1
  note). M. P1.
- C70 **Imperial Magistrate's compound**: what is it, and how big? (cities/capitals/370, program only). M. P1.

## K6 - cities/capitals: the domain school, the temple belt, the bell tower and the keep (new: cities/capitals 460-500)

Also edits 200, 333.

- C61 **Domain school ground**: how big is a hankō's ground, and what does it hold (lecture hall, drill hall, archery
  range, Confucian shrine)? (cities/capitals/190, 333 name the program). M. P1.
- C149 D73 **Temple belt**: why do temples belt the wall in a capital (teramachi) instead of clustering?
  (cities/capitals/200, 1 note, 1 absence). S. P1.
- C22 **Bell-and-drum tower in a capital**: one fixed per seat (a guess)? (cities/capitals/333, urban-features/070). S.
  P1.
- C57 D130 **The keep and the goten**: how big were the keep (tenshu), the honmaru and ninomaru and their stone walls
  (ishigaki - footprint, height, batter), and the daimyo's goten as a plan (courts, the council room), should the
  castle be drawn inside? (cities/capitals/160, siting only). L. P4.

## K7 - cities/river-cities: canals, water gates and landings (new: cities/river-cities 100-140)

- C161 **City canals**: how wide is a city canal, how is it revetted, and what lines its banks? (cities/capitals/300,
  water/010). M. P1.
- C18 **Water gates**: where a river or canal passes the city wall, what is the water gate - its form, width, grille
  or boom - and how many does a city carry? (cities/capitals/080; cities/river-cities/030 is 269 B46's - cite it). M.
  P1.
- B130 **Town landing**: does a town on a river keep a landing, and in what form? (cities/river-cities/040, city;
  ways/040). S. P3.
- C107 **Fish and produce market at the landing**: did a city keep one, and what did it look like? (none). S. P4.

## U4 - urban-features: the village's trades and public buildings (new: urban-features 430-490)

- A149 B48 C129 **Smiths**: did a village have its own smith (or an itinerant one); what is a town blacksmith's
  premises (forge, anvil shed, fire gap), where does it stand, how many per town; how many ordinary blacksmiths and
  swordsmiths does a city carry, and is the smithy bigger than a shop? (urban-features/160, 032, 030 omit it). M. P2.
- A150 **Village trades**: a general shop, a sake brewer (often the headman), an oil presser, a carpenter, a cooper -
  which trades did a village of 350 hold, and how many? (none). M. P2.
- A145 D104 **Village granary**: the tax-rice gokura, the relief granaries (gisō, shasō), China's charity granary -
  did a village keep a communal granary, how many, how big, and where? (cities/fabric/143, buildings/080, in passing).
  M. P2.
- A151 D145 B88 C143 **Schools below the capital**: where were village and town children taught to read (a temple
  school, terakoya; the headman's house; a Chinese county school, sishu), how many did a city hold, and were they
  distinct buildings? (none; cities/capitals/190 is the domain school). M. P2.
- A152 **Village fire watch**: a fire bell on a ladder (hanshō), a watch hut, a fire-water pond - did a village keep
  them, and where? (towns/070, the town's tower). S. P2.
- A153 **Village watch**: did a village keep a watch hut (bansho) or a night watch, and where? (none). S. P2.

## R3 - religion-and-death: the village temple and wayside shrines (new: religion-and-death 500-540)

- A138 D64 **Village temple**: did a village of 40-100 households keep a parish temple (danna-dera) of its own, beside
  or instead of its shrine (the Edo parish-temple system put one in or near most villages; the canon gives a village
  only a shrine), and how many villages shared one? Research FOR the GM's ruling. (religion-and-death/210). M. P2.
- A139 **Village temple precinct**: if drawn, how big is it, what stands in it (hall, priest's quarters, bell), and
  where does it sit against the houses and the graves? (none). M. P2.
- A140 D61 B103 **Wayside shrines**: jizō, dōsojin, a stone kami, a street-side Inari - how many does a village or a
  town's streets carry, how big, at which thresholds (entrance, crossroads, bridge foot)? (religion-and-death/210, 1
  note). M. P2.
- A144 **Village cremation and ossuary**: does a village cremate or bury, and where do its crematory and bone mound
  go? (religion-and-death/190, 202, 204, the town's and city's). M. P2.

## T5 - towns: markets and the commoners' town (new: towns 440-490)

- B92 **Market days**: how often did a county town hold its market (the Japanese rokusai-ichi, the Chinese ji
  schedule), and how far was its catchment? (towns/040, 080). M. P3.
- B93 B94 C106 **Market ground and stalls**: along the main street, on temple ground, in an open square, or a Chinese
  walled market (shi) - where was a town's or city's main market held, how big, and what did market day put on the
  ground (stalls, mats, temporary sheds) that shows on a non-market day? (towns/080, the gate market only). M. P3.
- B95 **The market crowd and the festival**: what does a town keep for them? (cities/fabric/130, city). S. P3.
- B87 **Town elders' hall**: did a town's commoners keep an office of their own (machi-kaisho; the Chinese guild
  hall), and where? (none). M. P3.
- B40 C100 B64 **Privies and night soil**: where are a town house's and a city tenement's privy and cesspit, who
  collected the night soil (owaiya), and does it mark the map? (buildings/220, cities/fabric/110). M. P3.
- B39 **Town house gardens**: did a town house keep a garden (tsubo-niwa, a rear plot, Chinese courtyard planting),
  and how big? (none). S. P3.

## U5 - urban-features: town trades (new: urban-features 500-570)

Also edits 030.

- B45 **Long-tail trades**: tofu, noodles, cooper, tatami, carpenter, apothecary, rice dealer - which fit a shophouse
  at town scale? (urban-features/030, the null results). M. P3.
- B46 **Sake brewery in a town**: does a county town keep one (canon names "the sake brewer" among a county's
  notables), how large, where (1-2 per ~3,000 is an estimate)? (urban-features/030). S. P3.
- B47 **Dyer in a town**: does a town keep a dyer (canon's "dye-house owner"), with its drying yard and rinsing water?
  (urban-features/030). S. P3.
- B52 **Rice hulling**: where was a town's rice hulled and polished, and by whom (tsukigome-ya)? (urban-features/030,
  a null result). S. P3.
- B53 **Timber dealer**: does a town keep a timber yard, and does it need a river? (urban-features/030, 040). S. P3.
- B60 B61 C133 **Textile and paper works**: did a town or city hold weaving or textile workshops (canon lists weavers)
  or a paper maker with vats and drying boards by water, and in what premises? (none). M. P3.
- B63 C116 D150 **Eating houses and teahouses**: which eating and drinking houses did a town or city keep, did they fit
  the shop glyph as distinct buildings, and did they cluster (gate, bridge, temple, road)? (religion-and-death/050,
  cities/fabric/050, urban-features/030). M. P3.

## R4 - religion-and-death: the state cult and temple plans (new: religion-and-death 550-590)

- B91 D78 **State cult buildings**: does a county seat or a city carry the Chinese state cult's buildings (the
  Confucian temple, wen miao; the City God temple; the altars of soil and grain), their setting analogue, where and how
  big? (urban-features/070, religion-and-death/020, named only). M. P3.
- C144 **Provincial academies**: did a provincial city keep a Confucian academy or school-temple (shuyuan, wenmiao, a
  domain school's branch), and how big? (none). M. P4.
- D75 **Temple as a building plan**: what does a temple precinct hold - main hall, gate (sanmon), bell tower, lecture
  hall, kuri, cloister, cemetery - at what sizes, Japan against China? (none). L. P4.
- D76 D77 **Temple bell tower and pagoda**: does a city temple keep a bell tower (apart from the civic bell-and-drum
  tower) and a pagoda, and how tall and wide? (none). M. P4.

## U6 - urban-features: the city's trade streets, relief houses and pleasure quarters (new: urban-features 580-620)

- B78 C138 D151 **Pleasure quarters and serving women**: did a post town keep serving women at its inns (meshimori
  onna), and did a provincial city or a capital have a licensed quarter (yūkaku; the Chinese wazi, goulan), walled or
  open, where (the edge, the wharf), and how big? (cities/capitals/090, next to the brokers a guess; 333, counts only).
  M. P3.
- C108 **Trade streets**: were trades grouped into named streets or wards (kaji-machi, kon'ya-machi, the Chinese
  hang), and in a provincial city? (cities/capitals/336, the capital's dyers). M. P4.
- C134 **Physician and relief house**: did a city keep a physician's or relief house (the Chinese huiminju,
  yangjiyuan) big enough to draw? (none). S. P4.
- C137 **Playhouse**: how big is a roofed playhouse, and does a capital carry several (the footprint is a guess)?
  (cities/capitals/333). S. P4.

## Queue order

P1 groups first (things already drawn), farming pages before the town and city pages because the scripted hamlets
carry live modals: V1, V2, V3, V4, V5, V6, V7, W1, U1, R1, T1, T2, T3, T4, W2, U2, U3, R2, G1, G2, K1, K2, K3, K4,
K5, K6, K7. Then P2 (village): U4, R3. Then P3 (town): T5, U5, R4, U6 (R4 and U6 also carry P4 rows). A group whose
rows EDIT an existing section syncs from main first, since 269's and 267's edits may have landed there.

## State

| group | rows | state |
|---|---|---|
| V1 | 5 | todo |
| V2 | 5 | todo |
| V3 | 5 | todo |
| V4 | 5 | todo |
| V5 | 5 | todo |
| V6 | 4 | todo |
| V7 | 6 | todo |
| W1 | 5 | todo |
| U1 | 6 | todo |
| R1 | 4 | todo |
| T1 | 6 | todo |
| T2 | 6 | todo |
| T3 | 5 | todo |
| T4 | 5 | todo |
| W2 | 7 | todo |
| U2 | 6 | todo |
| U3 | 5 | todo |
| R2 | 4 | todo |
| G1 | 5 | todo |
| G2 | 5 | todo |
| K1 | 5 | todo |
| K2 | 7 | todo |
| K3 | 6 | todo |
| K4 | 6 | todo |
| K5 | 5 | todo |
| K6 | 4 | todo |
| K7 | 4 | todo |
| U4 | 6 | todo |
| R3 | 4 | todo |
| T5 | 6 | todo |
| U5 | 7 | todo |
| R4 | 4 | todo |
| U6 | 4 | todo |
