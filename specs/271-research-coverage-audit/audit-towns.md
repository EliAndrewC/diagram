# Audit B - TOWNS (county seats and post towns)

Feature 271 FR-001, domain B. Maps in scope: the legacy hand-drawn towns Hirameki (walled, no Imperial road), Hoshizora
(unwalled, Imperial road, post/relay town), Ubame (unwalled, no road, charcoal and iron town); the town tier is NOT
STARTED for scripted generation (`migration-plan.md`), so no town modal exists yet (`modals.json` carries none). Record
pages read: `towns/`, `urban-features/`, and the town-scale reach of `cities/fabric`, `cities/defenses`,
`cities/government`, `buildings/`, `religion-and-death/`, `homesteads/`, `fields/`, `ways/`, `water/`.

Status: COVERED = a question answers it with quoted, footnoted evidence; THIN = touched, but no quoted evidence, or
answered only at another tier (usually the city) with nothing on the town; NONE = nothing answers it. Priority 1 =
drawn on a town map already; 3 = a town map plainly needs it and none draws it yet; 4 = the town row's city/capital
counterpart where the answer is expected to scale. Owner: another feature's item id where it claims the question
(269 = `diagram-supplemental/specs/269-research-backfill/inventory.md`; 267 = `diagram-buildings/.../inventory.md`;
268 = religion-and-death 080-126), else 271.

## The town as a whole

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B01 | town census | Who lives in a county seat and in how many houses; how do the canon caste counts compare with a real Edo county town / Chinese county seat of ~1,200? | town | THIN | towns/020 (canon only, no footnotes) | 269 B43 | 1 |
| B02 | post town | What distinguishes a post/relay town (shukuba, Chinese yizhan town) from a market county seat: its length along the road, household count, what it must keep standing? | town | NONE | (towns/050 names the shukuba only for its inn) | 271 | 1 |
| B03 | town extent | How long and how deep is a town's built core: a road town's strip length (cho), a nucleated seat's acreage for ~80 non-farming households? | town | NONE | (cities/sizing/020 is the city's) | 271 | 1 |
| B04 | town density | How densely is a town's commercial core built versus its farm zone (households per acre, share of ground built)? | town, city | THIN | cities/sizing/020 (city only) | 271 | 1 |
| B05 | town plan form | Linear road town, crossroads town or planned rectangle: which forms did Japanese and Chinese county seats take, and how often (a knob)? | town | THIN | towns/010 (Chinese planned seat covered; Japanese road-town form absent) | 271 | 1 |
| B06 | walled vs unwalled | What share of county seats were walled (Chinese: most; Japanese: almost none), and what makes a town walled? | town | THIN | towns/100 (cost reasoning, no share) | 271 | 1 |
| B07 | town wall | How high and thick is a county town's rampart, of what material, and how many gates did one have? | town | THIN | towns/100 (length and irregularity only); cities/defenses/010-040 (city) | 271 | 1 |
| B08 | town gate | What is a walled town's gate: a gatehouse or a tower over the opening, its footprint and opening width? | town, city | THIN | cities/defenses/030, 040 (city footprints) | 271 (city side 269 B38) | 1 |
| B09 | town moat | Did a walled county town carry a moat or ditch, and how wide? | town | NONE | (water/110, 120 are city moats) | 271 | 3 |
| B10 | gate market (why) | Why does a walled town grow a market outside its gate? | town, city | COVERED | towns/080 | 271 | 1 |
| B11 | gate market (size) | How many buildings and which trades make up a county town's gate market, and how far does it run out the road? | town | THIN | towns/080 (no page describes who traded there); cities/hinterland/040 (city) | 271 | 1 |
| B12 | town by region | How does a Japanese county town differ on the ground from a Chinese one (courtyard houses vs machiya, wall vs none, yamen axis vs jin'ya at the edge)? | town | THIN | towns/010, cities/fabric/010 | 271 | 1 |
| B13 | clan border | How is a clan border drawn past a border town? | town | COVERED | urban-features/170 | 271 | 1 |

## Streets and ways

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B14 | main street width | How wide is a town's main street, and the Imperial or trunk road where it runs through a town? | town | NONE | (ways/020 village lane; cities/capitals/210 capital) | 271 | 1 |
| B15 | street surface | What was a town street's surface (beaten earth, gravel, stone in China), and did it carry roadside gutters? | town, city | NONE | (cities/fabric/080 says unpaved on general reading) | 271 | 1 |
| B16 | cross streets | How many cross streets does a town have, and in what pattern - T junctions, a defensive crank (masugata) at the town ends? | town | NONE | - | 271 | 1 |
| B17 | streets as access | Why is a street drawn only where buildings use it? | town, city | COVERED | towns/090 | 271 | 1 |
| B18 | back paths | How is a packed commoner quarter crossed - trodden footpaths or alleys, and how wide? | town, city | THIN | urban-features/110 (no source cited) | 271 | 1 |
| B19 | Imperial road in town | What lines the Imperial road through a town, and is it labeled? | town, city | THIN | cities/fabric/040, 050 (city) | 271 | 1 |
| B20 | town bridge | How large is the road bridge where a town's street crosses its stream, and of what (plank, earth-decked, stone)? | town | THIN | ways/010, 030 (village plank bridges) | 271 | 1 |
| B21 | town entrance | What marks where a town begins on its road - a gate post, a mitsuke, a boundary stone, a roadside tree? | town | NONE | (homesteads/140 village entrance stone) | 271 (village stone 269 B20) | 1 |
| B22 | carts in town | Did carts run in a town's streets, and did a town keep a cart yard? | town, city | THIN | (cities/defenses, urban-features/080) | 267 R46 | 1 |
| B23 | notice board | Where does a town's kosatsuba stand? | all | COVERED | urban-features/010, 012 | 271 | 1 |
| B24 | notice-board seat | How is the board's seat chosen on the map? | all | THIN | urban-features/015 | 271 | 1 |

## Frontage and houses

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B25 | zoning bands | What fronts a town's street and what sits behind it? | town | COVERED | towns/030 | 271 | 1 |
| B26 | wealth-stratified housing | Is housing stratified by wealth, and how? | town, city | COVERED | urban-features/100 | 271 | 1 |
| B27 | merchant shophouse size | What frontage and depth does a county town's merchant house take (Kyoto's 2-3 ken x 10-12 ken is a city's)? | town | THIN | cities/fabric/020 (Kyoto, city) | 271 | 1 |
| B28 | large merchant house | How big is a rich town merchant's house or walled compound, and how many does a town of 1,200 hold? | town, city | THIN | cities/fabric/090, 100 (city) | 271 | 1 |
| B29 | party walls in a town | Does a county seat build its street front in continuous party-wall rows or as detached houses with gaps? | town | THIN | cities/fabric/010 (city) | 271 | 1 |
| B30 | stories and roofs | One story or two, and thatch, board-and-stone or tile: what did a town's street front look like from above, and did fire law shape it? | town, city | NONE | - | 271 | 1 |
| B31 | merchant kura | How many fireproof storehouses stand behind a town's merchant houses, how big, and where on the lot? | town, city | THIN | cities/fabric/130 (asserts kura); urban-features/030 (pawnshop court) | 271 | 1 |
| B32 | Chinese courtyard house | Is the courtyard house (siheyuan / sanheyuan) the Chinese form of a town merchant's house, and its size (a knob against the machiya)? | town, city | NONE | - | 271 | 3 |
| B33 | laborer dwelling | What does a town laborer live in - a detached hut, a nagaya row unit - and how big? | town, city | THIN | cities/fabric/010, 110 (city nagaya) | 271 | 1 |
| B34 | large laborer house | What is the drawn "large laborer" house - an oyakata's (labor boss's) house, a porters' boarding house - and its size? | town | NONE | - | 271 | 1 |
| B35 | servant households | Where do a town's standalone servant households live, and what house? | town | THIN | towns/020 (convention) | 269 B43 | 1 |
| B36 | samurai houses | How big is a county town's samurai house, fenced or walled, and where does it stand relative to the manor? | town | THIN | towns/020 (canon count only); cities/government/030 (city, no footnotes) | 271 (city side 269 B39) | 1 |
| B37 | senior samurai house | What is a senior staff officer's (yoriki-rank) house in a county town, and how much larger? | town | NONE | - | 271 | 1 |
| B38 | door orientation | Which way does a town house's door face, and how deep do rows stack? | town, city | THIN | cities/fabric/110 (city) | 271 | 1 |
| B39 | town house gardens | Did a town house keep a garden (tsubo-niwa, rear plot, Chinese courtyard planting), and how big? | town | NONE | - | 271 | 3 |
| B40 | privies and night soil | Where are a town house's privy and cesspit, and how did night soil leave the town? | town, city | THIN | buildings/220 (compound, tenement) | 271 | 3 |
| B41 | town barns | What are the barns of a town's hayfield (Hoshizora's five): hay barns, ox sheds, their size? | town | NONE | - | 271 | 1 |

## Shops and crafts

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B42 | shop count | How many shops does a county seat of ~1,200 hold, and of which trades? | town | THIN | towns/020 (canon count); urban-features/030 (city) | 271 | 1 |
| B43 | shop footprint | How big is a town shop as premises distinct from its owner's house? | town | THIN | towns/020 (convention); urban-features/030 (the 48x32 ft glyph, city) | 271 | 1 |
| B44 | which trades outgrow the glyph | Which trades need premises larger than a shophouse? | city, town | THIN | urban-features/030 (city; many figures "this page's estimate") | 271 | 1 |
| B45 | long-tail trades | Which ordinary trades fit a shophouse at town scale (tofu, noodles, cooper, tatami, carpenter, apothecary, rice dealer)? | town, city | THIN | urban-features/030 (the null results, city) | 271 | 3 |
| B46 | sake brewery | Does a county town keep a brewery (canon names "the sake brewer" among a county's notables), how large, sited where? | town, city | THIN | urban-features/030 (city rule; 1-2 per ~3,000 is an estimate) | 271 | 3 |
| B47 | dyer | Does a town keep a dyer (canon's "dye-house owner"), with its drying yard and rinsing water? | town, city | THIN | urban-features/030 (city) | 271 | 3 |
| B48 | blacksmith | What is a town blacksmith's premises (forge, anvil shed, fire gap), where does it stand, and how many per town? | town | NONE | (Hirameki notes: "the smith shoes in his shop row"; canon names "the master smith") | 271 | 3 |
| B49 | farrier | Why does this setting shoe horses, and what does a farrier draw? | town, city | COVERED | urban-features/032 | 271 | 1 |
| B50 | oil press | Does a town keep an oil press, and where? | town, city | THIN | urban-features/030 (city) | 271 | 3 |
| B51 | pawnshop | Does a town keep a pawnshop, and what is its tell on a map? | town, city | THIN | urban-features/030 (city) | 271 | 3 |
| B52 | rice dealer and hulling | Where was a town's rice hulled and polished, and by whom (tsukigome-ya)? | town | THIN | urban-features/030 (null result) | 271 | 3 |
| B53 | timber dealer | Does a town keep a timber yard, and does it need a river? | town, city | THIN | urban-features/030, 040 (city, river port) | 271 | 3 |
| B54 | kiln works | What is a kiln works, and do the potters live at it? | town, city | COVERED | urban-features/050 | 271 | 1 |
| B55 | kiln works form | What does a climbing kiln look like on the map, and its fire gap? | town, city | THIN | urban-features/052 | 271 | 1 |
| B56 | charcoal yard | What is a charcoal depot at a town? | town | COVERED | urban-features/150 | 271 | 1 |
| B57 | refining forge | Where does iron refining happen, and what does the forge look like? | town | COVERED | urban-features/160 | 271 | 1 |
| B58 | tanning yard | Where does a tanning yard stand and what does it need? | town, city | COVERED | urban-features/060, 062, 064, 066 | 271 | 1 |
| B59 | tanning yard direction | Which way out of town does the tanning yard stand? | town, city | THIN | urban-features/068 | 271 | 1 |
| B60 | weavers and textile | Did a town hold weaving or textile workshops (canon lists weavers among the castes), and in what premises? | town | NONE | - | 271 | 3 |
| B61 | paper making | Does a town or its edge keep a paper maker, with vats and drying boards by water? | town | NONE | - | 271 | 3 |
| B62 | mills | Where was a town's grain milled - water mill, ox mill, hand quern - and did China and Japan differ? | town | NONE | - | 271 | 3 |
| B63 | eating houses and teahouses | Which eating and drinking houses did a town keep, and where did they stand? | town | THIN | religion-and-death/050 (temple gate); cities/fabric/050 (city roadside) | 271 | 3 |
| B64 | night-soil trade | Who collected a town's night soil (canon's owaiya), and does it leave a mark on the map? | town, city | THIN | buildings/220 | 271 | 3 |

## Inns and post-station facilities

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B65 | flophouse | Who stays in the market-day flophouse, and where does it stand? | town, city | COVERED | towns/040 | 271 | 1 |
| B66 | caravan inn | Where does a caravan inn stand, what does it need beside it, and what form (one or two stories)? | town | COVERED | towns/050 | 271 | 1 |
| B67 | inn count | How many inns did a county town or a post town keep (a Tokaido shukuba ran dozens of hatago)? | town | NONE | - | 271 | 1 |
| B68 | inn footprint | How big is a hatago or a wagon inn on the ground? | town | THIN | towns/050 (the Okabe hatago; yard size uncalibrated) | 271 | 1 |
| B69 | official lodging | Where did traveling samurai and officials lodge in a post town (honjin / waki-honjin; the Chinese guest house of the yamen), and how big? | town | NONE | - | 271 | 3 |
| B70 | Imperial waystation | Where does the setting's Imperial road waystation (canon: 25-30 staff, relay horses at a busy station) stand relative to a town, and what is its footprint? | town | NONE | - | 271 | 1 |
| B71 | post-horse office | What is a post station's toiya-ba (horse and porter office), with its horse yard, and where on the street? | town | NONE | - | 271 | 3 |
| B72 | relay horses | How many horses and porters did a post station keep, and where were they stabled? | town, city | THIN | cities/fabric/130 (the Tokaido obligation, city) | 271 | 1 |
| B73 | stables | How big is an inn's stable, and how is it laid out? | town | THIN | towns/050 (the wagon inn's long stable) | 271 | 1 |
| B74 | stable yard surface | What is a stable or cart yard's ground like? | town, city | THIN | urban-features/080 (one note) | 271 | 1 |
| B75 | stable yard water | How does a stable yard water its animals? | town, city | COVERED | urban-features/082 | 271 | 1 |
| B76 | roadside rest stops | Did teahouses and rest stops (tateba, chaya) stand at a town's ends on the highway? | town | THIN | cities/fabric/050 (city) | 271 | 3 |
| B77 | inspection station | Did a town on a road keep a barrier or inspection post, and what did it look like? | town, city | THIN | urban-features/140 (barriers on roads, passes); cities/defenses/050 (city) | 271 (city side 269 B38) | 3 |
| B78 | post-town entertainment | Did a post town keep serving women at its inns or a licensed quarter (meshimori onna), and does a map show it? | town | NONE | - | 271 | 3 |

## The magistrate's presence

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B79 | manor as a box | Why is the magistrate's manor drawn as a plain walled box? | town | THIN | towns/110 (GM ruling, no footnotes) | 269 B44 | 1 |
| B80 | manor siting | Where does a magistrate's manor stand in its town, and which way does its gate face? | town | THIN | towns/120 (one note) | 269 B43 | 1 |
| B81 | manor size | How large is a county magistracy's compound against the town around it? | town | COVERED | buildings/180, 190 | 271 | 1 |
| B82 | tax-rice granary | Where does a county seat keep its tax rice - inside the compound, or a storehouse row in a rice-transit town? | town | THIN | towns/110 (convention); buildings/080, 150 (compound) | 271 | 1 |
| B83 | bench's own board | Is the magistracy's board kept apart from the town's kosatsuba? | town | THIN | urban-features/010 | 267 R25 | 1 |
| B84 | punishment ground | What stands on the punishment ground in town? | town, city | COVERED | urban-features/026 | 271 | 1 |
| B85 | execution ground | Why does a county seat execute, where, and how big is the ground? | town, city | COVERED | urban-features/020, 022, 024 | 271 | 1 |
| B86 | drum tower | Does a walled seat keep a bell-and-drum tower? | town, city | COVERED | urban-features/070 | 271 | 1 |
| B87 | town elders' hall | Did the commoners of a town keep an office of their own (machi-kaisho, the town elders' hall; the Chinese guild hall), and where? | town | NONE | - | 271 | 3 |
| B88 | school | Did a county town keep a school (terakoya, a Chinese county school with its Confucian temple), and how big? | town | NONE | (cities/capitals/190 is the domain school) | 271 | 3 |
| B89 | dojo | Does a county town keep a dojo? | town, city | COVERED | buildings/210 | 271 | 3 |
| B90 | cells | Where are a town's prisoners held? | town | COVERED | buildings/040 | 271 | 3 |
| B91 | Confucian and City God temples | Does a county seat carry the Chinese state cult buildings (wen miao, City God temple, altars of soil and grain), and their setting analogue? | town | THIN | urban-features/070 (named beside the drum tower) | 271 | 3 |

## Markets

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B92 | periodic market | How often did a county town hold its market (Japanese rokusai-ichi, Chinese ji schedule), and how far was its catchment? | town | THIN | towns/040, 080 (catchment asserted; jishi-zhwiki) | 271 | 3 |
| B93 | market ground | Where was the market held - along the main street, on temple ground, in an open square - and how big was it? | town | NONE | - | 271 | 3 |
| B94 | stalls | What did market day put on the ground (stalls, mats, temporary sheds), and does a map show it on a non-market day? | town | NONE | - | 271 | 3 |
| B95 | market-day crowd and festival | What does a town keep for the market crowd and the festival? | town, city | THIN | cities/fabric/130 (city) | 271 | 3 |

## Temples and shrines in town

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B96 | monastery count | How many monasteries does a county seat keep (canon: one per patron Fortune), and how does that compare with real county towns? | town | THIN | religion-and-death/210 (one note) | 271 | 1 |
| B97 | monastery size | How big is a town monastery's precinct and hall, walled or fenced, and who lives in it? | town | THIN | religion-and-death/010, 040 (city temples) | 271 (city side 269 B37) | 1 |
| B98 | monastery layout | What stands in a town monastery's precinct (gate, main hall, bell, priests' quarters, graveyard)? | town | THIN | religion-and-death/040, 170 | 271 | 1 |
| B99 | theater stage | Where does a town's theater stage stand and which way does it open? | town | COVERED | towns/060 | 271 | 1 |
| B100 | temple-gate shops | What shops stand at a temple gate? | town, city | COVERED | religion-and-death/050 | 269 B37 (ratio) | 1 |
| B101 | town shrine | How big is a town's own shrine (the chinju of a county seat) and its precinct, against a village's? | town | THIN | religion-and-death/100-126 (village) | 271 | 1 |
| B102 | torii | Why are torii drawn where they are, and how many? | all | COVERED | religion-and-death/080, 090 | 268 | 1 |
| B103 | street shrines | Did a town's streets carry small roadside shrines, Jizo figures or Inari shrines, and how many? | town | NONE | - | 271 | 3 |

## Death and burial at town scale

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B104 | town graveyards | How much ground do a town's graveyards take, how many are there, and inside or outside the wall? | town | THIN | religion-and-death/160, 206 (village sizes); 210 (count) | 269 B36 | 1 |
| B105 | cremation ground | How large is a town's cremation ground and where does it stand? | town, city | COVERED | religion-and-death/190, 202 | 271 | 1 |
| B106 | ossuary | How large is a bone mound? | town, city | COVERED | religion-and-death/204 | 269 B37 | 1 |

## The burakumin quarter

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B107 | quarter siting | Where does a town's burakumin quarter stand, and how segregated is it? | town, city | COVERED | urban-features/130, towns/030 | 271 | 1 |
| B108 | quarter size and houses | How many households and what dwellings does a town's burakumin quarter hold, and does it keep its own well and shrine? | town | THIN | towns/020 (canon count only) | 271 | 1 |
| B109 | quarter and the works | Does the quarter stand by the tanning yard, and did the tanners sleep at the works? | town, city | COVERED | urban-features/066 | 271 | 1 |
| B110 | inside the wall | In a walled town, does the burakumin quarter stand inside or outside? | town, city | THIN | cities/fabric/060 (city; the siege reason is the record's own) | 271 | 1 |

## Fire watch, wells and baths

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B111 | fire-watch tower | Does a town keep a fire-watch tower, and only a walled one? | town | THIN | towns/070 (the unwalled-none reason is a guess) | 271 | 1 |
| B112 | fire tower form | How tall is a hinomi-yagura and how big its footprint? | town, city | THIN | cities/fabric/140 (city) | 271 | 1 |
| B113 | fire-fighting provision | What did a town keep against fire - water barrels, fire buckets, a watch house (jishinban), a fire pond? | town | NONE | (cities/fabric/140, 143 city) | 271 | 3 |
| B114 | night watch and kido | Did a town bar its streets at night (kido, a watchman's hut), or only a city? | town, city | THIN | urban-features/130 (city) | 271 | 3 |
| B115 | wells | How many wells does a town keep, and why the liberty? | all | COVERED | urban-features/090, 120 | 271 | 1 |
| B116 | wellhead form | What does a town's communal well look like from above - curb, frame, pulley, roof? | town, city | THIN | urban-features/090 (the size for the reader) | 271 | 1 |
| B117 | other town water | Did a town draw water besides its wells - street channels, a stream-fed runnel, a washing place at the brook? | town | NONE | - | 271 | 3 |
| B118 | bathhouse | Does a county town of ~1,200 keep a public bathhouse, and what does it draw? | town, city | THIN | urban-features/030 (city count rule, floored at one per city) | 271 | 3 |

## The town's edge and its fields

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| B119 | town farmstead | How is a town farmstead laid out? | town | COVERED | towns/130 | 271 | 1 |
| B120 | town paddy plot | How big is a town's paddy plot? | town | THIN | towns/150 (no footnotes) | 269 B43 | 1 |
| B121 | farmland around a town | What is the farmland around a town made of? | town, city | COVERED | fields/130 | 271 | 1 |
| B122 | shelter belt | Which way does a town's shelter belt lie? | town | THIN | towns/140 | 269 B43 | 1 |
| B123 | town commons | What grazing and common ground surrounds a town, and how much? | town | NONE | (town-checks-audit item 9 is a check, not research) | 271 | 1 |
| B124 | hayfield and pasture | Did a town keep a hayfield or pasture for its draft and relay stock (Hoshizora's hayfield), and how big? | town | NONE | - | 271 | 1 |
| B125 | Imperial flower field | What is the Imperial chrysanthemum field on Hirameki, and its size? | town | NONE | (settlements/080 names it) | 271 | 1 |
| B126 | temple glebe | Which plots belong to the temple, tax-free? | all | THIN | fields/150 | 269 B08 | 1 |
| B127 | threshing yards | How big was the work yard? | all | COVERED | homesteads/020 | 271 | 1 |
| B128 | market gardens | Did a town's edge carry vegetable plots supplying the town, fed by its night soil? | town | NONE | - | 271 | 3 |
| B129 | suburb along the road | Where does a town's built edge stop - does a ribbon of houses run out along the road past the last block (machi-hazure)? | town | NONE | - | 271 | 3 |
| B130 | landing | Does a town on a river keep a landing, and what form? | town | THIN | cities/river-cities/040 (city); ways/040 (village freight) | 271 | 3 |
| B131 | ferry | Where a town's road meets a river with no bridge, what does the ferry crossing draw? | town | NONE | - | 271 | 3 |
| B132 | edge woods | Why is a town's margin clothed and not left bare, and with what? | town | THIN | water/170 (no toe marsh); vegetation/030 | 271 | 1 |

## Counts

- By status: COVERED 31, THIN 66, NONE 35 (132 rows).
- By owner: 271 119; 269 10 (B43 x5, B44, B36, B37 x2, B08; and 269 B38/B39 hold the city side of three 271 rows, this audit's own B08, B36 and B77);
  267 2 (R25, R46); 268 1 (torii).
- By priority: 1 (drawn on a town map) 92; 3 (town tier, not yet drawn) 40.
