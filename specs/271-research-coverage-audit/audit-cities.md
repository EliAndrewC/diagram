# Audit C - cities and capitals (feature 271 FR-001)

Domain: the legacy provincial cities (minami, nagahara, tango), `wip/shiro-daika`, and the `cities/*` and
`urban-features` pages. Tiers: T town (where a city question has a town rung), C provincial city, K capital.
Status against the record as of 2026-09-27 (measure/questions.json counts + a read of each named fragment):
COVERED = a question answers it with quoted, footnoted evidence; THIN = touched, but unquoted, a guess, a
calibration against our own maps, or clearly partial; NONE = nothing answers it. Owner: 269 Bnn / 267 Rnn / 268 when
claimed, else 271. Priority: 1 = drawn on a map already (a legacy city or Shiro Daika), 3 = town, 4 = city/capital
not yet drawn. Every city kind in kinds.json (`provincial-cities:*`) is drawn, so most rows are priority 1.

The city maps are frozen legacy exhibits with no modals (modals.json has no city registry), so no `Entry:` line
points at these questions yet; the questions will be the entries when the city tier is scripted.

## Walls, gates and moats

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C01 | city wall | Does the wall close a full ring, and how many gates does it have? | C,K | COVERED | cities/defenses/010 | 271 | 1 |
| C02 | city wall | What plan shape does the wall take (rectangle, terrain loop), and why keep corners? | C,K | COVERED | cities/capitals/150, 155 | 271 | 1 |
| C03 | city wall | How is the rampart built and how big is it in section - height, base and top width, rammed earth vs stone- or brick-faced vs Japanese earthwork (dorui, sogamae), parapet - and what of that shows from above? | T,C,K | THIN | cities/capitals/150, 155 and cities/defenses/060 mention materials and Xi'an's dimensions; towns/100 is cost only; no section for a provincial seat | 271 | 1 |
| C04 | city wall | How big is the walled area for the population inside it? | C,K | COVERED | cities/sizing/010 (population split owed) | 269 B41 | 1 |
| C05 | city wall | How much of the walled ground stood empty, and what claimed it? | C,K | COVERED | cities/sizing/020 | 271 | 1 |
| C06 | wall towers | How far apart do wall towers stand, what shape are they, and how many does a city carry? | C,K | COVERED | cities/defenses/060, 070 (tower count against wars fought is a guess) | 269 B38 | 1 |
| C07 | gate opening | How wide is the opening a road passes through? | T,C,K | COVERED | cities/defenses/030 | 271 | 1 |
| C08 | gate tower / gatepost | What are the real footprints of a city gate's tower, gateposts, guard house and inspection hall? | C,K | COVERED | cities/defenses/040 (tower and gatepost footprints thin) | 269 B38 | 1 |
| C09 | barbican | Did a provincial city gate have a barbican (wengcheng) or a Japanese masugata, how large, and in what form? | C,K | THIN | cities/defenses/050 names the wengcheng; nothing sizes it or says how common it was at a provincial seat | 271 | 1 |
| C10 | guard and inspection posts | Where do the guard house and inspection station stand at the gate throat, and do they face each other? | C,K | COVERED | cities/defenses/050 (facing arrangement a guess) | 269 B38 | 1 |
| C11 | patrol road | How far inside the wall does the patrol (ring) road run, how wide, and what may stand on it? | C,K | THIN | cities/defenses/080 | 269 B38 | 1 |
| C12 | ward fence at rampart | Where does a neighborhood fence stop when it reaches the rampart? | C,K | THIN | cities/defenses/090 | 269 B38 | 1 |
| C13 | moat | How wide and how deep is a city moat, and how far off the wall foot does it lie (berm)? | C,K | THIN | water/010, cities/capitals/220 (66 ft, our own drawing), cities/defenses/020 | 269 B38 | 1 |
| C14 | moat | What keeps the moat full? | C,K | THIN | cities/defenses/020 (1 quoted note); water/110, 120 cover drainage and diverted streams | 269 B38 | 1 |
| C15 | moat | Does a moat have a current? | C,K | THIN | water/100 | 269 B25 | 1 |
| C16 | moat | Is moat water standing or connected, and does it scum? | K | COVERED | cities/capitals/170 | 271 | 1 |
| C17 | moat crossing | How does a road cross the moat at a city gate - fixed timber bridge, earthen causeway, stone bridge, drawbridge - and how wide and long is it? | C,K | NONE | (cities/capitals/240 is the castle's two gates only) | 271 | 1 |
| C18 | water gates | Where a river or canal passes the city wall, what is the water gate - its form, width, grille or boom - and how many does a city carry? | C,K | THIN | cities/capitals/080 (aqueduct at the gate); cities/river-cities/030 is the canal's mouth on the river | 271 | 1 |
| C19 | sluice gates | What is a moat or canal sluice's frame, and how often is it open? | C,K | COVERED | cities/capitals/280, 310 | 271 | 1 |
| C20 | defensive marsh | Was an engineered wet belt kept outside a wall? | C,K | COVERED | water/180 | 271 | 1 |
| C21 | moat and river | When does a city get a moat ring and when a river-flank moat? | C,K | COVERED | cities/capitals/250 | 271 | 1 |

## Towers, fire and time

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C22 | bell-and-drum tower | Does every walled seat keep one bell-and-drum tower, where, and how big? | C,K | COVERED | urban-features/070 (fixed-per-seat in a capital a guess, cities/capitals/333) | 271 | 1 |
| C23 | fire-watch tower | How did a dense wooden city watch for fire, and how many towers per area? | T,C,K | COVERED | cities/fabric/140, 143, 146; towns/070 | 271 | 1 |
| C24 | firebreak | Why do these maps draw no firebreak (hiyokechi, hirokoji)? | C,K | COVERED | cities/fabric/150 | 271 | 1 |
| C25 | street fire equipment | Were fire cisterns, rain barrels (tenbo-oke) or ladders kept in the street, and are any big enough to draw? | C,K | NONE | (cities/fabric/140 is the watch, buildings/170 is a compound's tubs) | 271 | 4 |

## Government and justice

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C26 | governor's mansion | Where does the province's government stand in its city, and what clusters round it? | C | COVERED | cities/government/010 | 271 | 1 |
| C27 | governor's mansion | How big is a provincial governor's compound in absolute terms (acres, frontage, depth) - a Chinese prefectural yamen vs a Japanese domain jin'ya or castle-town office? | C | THIN | cities/government/010 gives only relative rules (3x a ministry, as large as a country estate); buildings/180, 190 are a county magistracy | 271 | 1 |
| C28 | governor's mansion | What stands inside a governor's compound (gate, office halls, courtroom, residence, granary, jail), in what order and at what sizes? | C | THIN | buildings/010-230 answer it for a COUNTY compound; nothing scales it to a province | 271 | 1 |
| C29 | governor's mansion | Which way does the governor's compound face, and is there a gate-to-yamen avenue in a city? | C | THIN | towns/010 (towns), cities/capitals/140 (capital's avenue) | 271 | 1 |
| C30 | six ministries | How big is a ministry office, and are the six equal? | C,K | THIN | cities/capitals/290 (1 quoted note; the ministries are canon) | 271 | 1 |
| C31 | six ministries | Where do the ministries stand relative to the governor's compound and the castle? | C,K | COVERED | cities/government/010, cities/capitals/140 | 271 | 1 |
| C32 | Rites ministry | Why does Rites stand in the temple neighborhood? | C | COVERED | urban-features/140 (canon) | 271 | 1 |
| C33 | jail | Is a city's jail inside the governor's compound or a separate prison, and how big and where? | C,K | THIN | buildings/040 (remand cells, a county compound); cities/government/010 names a jail within a yamen | 271 | 4 |
| C34 | city magistrate and police | Did a city keep a separate town magistrate's office (machi-bugyosho) and constables' quarters, where, and how large? | C,K | NONE | - | 271 | 4 |
| C35 | ward guard posts | Were ward guard boxes (jishinban, tsujiban) or Chinese patrol stations (xunpu) kept in the commoner wards, and how many? | C,K | THIN | cities/capitals/330 cites Kaifeng's patrol stations for fire only | 271 | 4 |
| C36 | kido / night gates | Were wards walled or closed by night-barred gates? | C,K | COVERED | cities/capitals/060 | 271 | 1 |
| C37 | ward gates | Which way does a ward gate face? | C,K | THIN | cities/government/050 (1 note) | 269 B39 | 1 |
| C38 | gate watch | Where does the gate watch stand? | C,K | THIN | cities/government/060 (1 note) | 271 | 1 |
| C39 | notice board | Where does a city's notice board stand? | T,C,K | COVERED | urban-features/010, 012 | 271 | 1 |
| C40 | execution ground | Why does a seat execute, where is the ground, and how big is it? | T,C,K | COVERED | urban-features/020, 022, 024 | 271 | 1 |
| C41 | punishment spot | What stands on the punishment ground in town? | T,C | COVERED | urban-features/026 | 271 | 1 |
| C42 | inspection and tariff | Are gate tariff and inspection stations real, and where did barriers stand historically? | C,K | COVERED | urban-features/140, cities/defenses/050 | 271 | 1 |
| C43 | garrison | Where does a provincial city's garrison live and muster, and is there a separate barracks or armory outside the castle? | C | THIN | cities/government/085 (foot soldiers' housing), cities/capitals/360 (armory in the castle) | 271 | 1 |
| C44 | drill ground | How large was a city's drill or muster ground, and where did it lie? | C,K | THIN | cities/sizing/020 (a calibration, not a source) | 271 | 1 |
| C45 | post station | Does a provincial city keep a post-horse office (tenma-sho) or relay station, and what does it need? | C | THIN | cities/fabric/130 (Tokaido post-horse quotas) | 271 | 4 |
| C46 | clan border | How is a clan border drawn? | T,C | COVERED | urban-features/170 | 271 | 1 |

## Granaries, warehouses and storehouses

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C47 | tax-rice granary | How big is a provincial city's tax-rice granary, how many buildings, and where does it stand (in the governor's compound, at the wharf, by a gate)? | C | THIN | buildings/080, 150 (county compound granary); cities/capitals/090, 360 (capital) | 271 | 1 |
| C48 | granary floor | How was a grain kura's floor raised? | T,C,K | NONE | - | 267 R18 | 1 |
| C49 | Emperor's granaries | Why are the Emperor's granaries separate? | K | THIN | cities/capitals/120 (1 note) | 271 | 1 |
| C50 | merchant storehouses | How many fireproof merchant kura does a city carry, how big is each, and where do they stand on the lot? | T,C,K | THIN | cities/fabric/130 (a floor calibrated on our maps); buildings/160 (fire discipline) | 271 | 1 |
| C51 | wharf warehouses | What stands at a capital's wharf (quay-side kura, stipend stores)? | K | COVERED | cities/capitals/090, 280, 300 | 271 | 1 |
| C52 | rice brokers | Who kept the brokers' row and what did it look like? | K | THIN | cities/capitals/110 (1 note) | 271 | 1 |

## Castle and capital

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C53 | castle | Is the castle centered or at the edge of its town? | K | COVERED | cities/capitals/020, 030 | 271 | 1 |
| C54 | castle | How big is a median castle? | K | COVERED | cities/capitals/040 | 271 | 1 |
| C55 | castle | How many gates does a castle have? | K | COVERED | cities/capitals/240 | 271 | 1 |
| C56 | castle | Why is the castle drawn blank inside, and what stands inside it vs outside? | K | THIN | cities/capitals/350, 360 (1 note each) | 271 | 1 |
| C57 | castle keep and baileys | How big were the keep (tenshu), the honmaru and ninomaru, and their stone walls (ishigaki) - footprint, height, batter - should the castle ever be drawn inside? | K | NONE | - | 271 | 4 |
| C58 | chancellery | Where does the council meet? | K | COVERED | cities/capitals/160 | 271 | 1 |
| C59 | lineage compounds | How big is each ruling-house lineage's compound in the capital? | K | THIN | cities/capitals/370 (1 note) | 271 | 1 |
| C60 | domain school | What is the domain school and where does it stand? | K | COVERED | cities/capitals/190, 333 | 271 | 1 |
| C61 | domain school | How big is a hanko's ground and what buildings (lecture hall, drill hall, archery range, Confucian shrine) does it hold? | K | NONE | (190 and 333 name the program, not its footprint) | 271 | 1 |
| C62 | capital internal walls | Which districts get internal walls? | K | COVERED | cities/capitals/270 | 271 | 1 |
| C63 | aqueduct | How did an aqueduct (josui) run, where is it open and buried, and whom does it supply? | K | COVERED | cities/capitals/080, 180, 230 | 271 | 1 |
| C64 | capital population outside walls | How much of a capital lives outside the walls? | K | COVERED | cities/capitals/320 | 271 | 1 |
| C65 | capital streets | How wide is the ote-suji and a capital's other streets? | K | COVERED | cities/capitals/210 | 271 | 1 |
| C66 | capital dimensions | Does the drawn capital match real dimensions? | K | COVERED | cities/capitals/220 | 271 | 1 |
| C67 | capital scaling | Which trades and funerary features multiply, consolidate, grow faster or stay one to a seat? | K | COVERED | cities/capitals/330, 333, 336 | 271 | 1 |
| C68 | clan capitals | Does a Scorpion capital look different from a Crane one? | K | THIN | cities/capitals/380 | 269 B45 | 1 |
| C69 | capital inversions | Which provincial rules turn upside down in a capital? | K | THIN | cities/capitals/390 | 269 B45 | 1 |
| C70 | Imperial magistrate | What is the Imperial Magistrate's compound, and how big? | K | THIN | cities/capitals/370 (program only) | 271 | 1 |

## Samurai quarter

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C71 | samurai quarter | Were samurai and commoner ground zoned apart, and where does the samurai quarter lie? | C,K | COVERED | cities/government/090, urban-features/130 | 271 | 1 |
| C72 | samurai quarter | Is the samurai quarter walled or only fenced and gated? | C,K | COVERED | cities/government/040 | 271 | 1 |
| C73 | samurai count | Where do a city's samurai live, and how many are drawn? | C | THIN | cities/government/030 | 269 B39 | 1 |
| C74 | samurai house | How big were a samurai residence's lot and house by rank (kind=samurai, samurai_large) - tsubo granted per stipend, frontage, house size? | C,K | THIN | cities/capitals/100 (the retainer terrace), buildings/180; the 67-tsubo mid-rank house is 267's | 271 (267 R15 related) | 1 |
| C75 | samurai house | What does a samurai residence look like from above - long-house gate (nagayamon), hedge or plastered wall, garden, kitchen yard? | C,K | NONE | - | 271 | 1 |
| C76 | samurai house | Did a samurai house have its own well and bath? | C,K | THIN | urban-features/120 (the well exception); the bath is 267's | 271 / 267 R09 | 1 |
| C77 | servants | Where did servants live - servant long-houses drawn as walls? | C,K | COVERED | cities/government/080, 081, 082 (6 guesses) | 269 B39 | 1 |
| C78 | foot soldiers | Where do a castle town's foot soldiers live? | C,K | COVERED | cities/government/085 | 269 B39 | 1 |
| C79 | capital samurai | Are a capital's samurai senior-heavy? | K | COVERED | cities/capitals/070 | 271 | 1 |
| C80 | country estates | Are gentry estates dispersed, how many does a city map draw, which way do their gates face? | C,K | THIN | cities/hinterland/010 COVERED, 015 THIN | 269 B41 | 1 |

## Commoner fabric, streets and wards

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C81 | commoner rows | Did urban commoners build in continuous street walls? | C,K | COVERED | cities/fabric/010 | 271 | 1 |
| C82 | machiya | What is a machiya's frontage and depth, and how continuous is a commercial street? | T,C,K | COVERED | cities/fabric/020 | 271 | 1 |
| C83 | merchant houses | How does wealth stratify commercial frontage and housing (merchant, merchant_house, merchant_large)? | T,C,K | COVERED | urban-features/100 | 271 | 1 |
| C84 | walled merchant compounds | How many walled merchant compounds does a city hold, and where may their walls stand? | C,K | COVERED | cities/fabric/090, 100 (100 has 1 note) | 271 | 1 |
| C85 | laborer housing | How big is a back-tenement (uranagaya) unit and its block, per household (kind=laborer, laborer_large)? | C,K | THIN | cities/fabric/010, cities/capitals/100 (ashigaru terrace only) | 271 | 1 |
| C86 | back lanes | How do you get through a packed commoner quarter, and why is the path not a street? | C,K | THIN | urban-features/110 | 271 | 1 |
| C87 | alleys | Where do the shops stand, where does poor housing go, and what surface do alleys have? | C,K | THIN | cities/fabric/080 | 269 B40 | 1 |
| C88 | street grid | How do a city's streets make a grid? | C,K | THIN | cities/fabric/070 | 269 B40 | 1 |
| C89 | street widths | How wide are a provincial city's main street, side streets and lanes? | T,C | THIN | cities/capitals/210 (capital), towns/090 (towns), ways/020 (village lanes) | 271 | 1 |
| C90 | street share | What share of a seat is street, open reserve and civic ground? | C | COVERED | cities/fabric/030 (anchors owed) | 269 B40 | 1 |
| C91 | block size | How big is a city block (cho, Chinese fang), and how many lots does it hold? | C,K | NONE | - | 271 | 1 |
| C92 | doors and row depth | Which way does a city house's door face, and how deep do rows stack? | C,K | COVERED | cities/fabric/110 | 271 | 1 |
| C93 | Imperial road | Where does the Imperial road run through a city, and what lines it? | C,K | COVERED | cities/fabric/040, 050 | 271 | 1 |
| C94 | caste zoning | How were castes zoned in a seat? | C,K | COVERED | urban-features/130 | 271 | 1 |
| C95 | population mix | Who lives in a provincial city, in what shares? | C | COVERED | settlements/090 | 271 | 1 |
| C96 | quarters | What quarters does a walled city declare, and how densely is each built? | C,K | COVERED | cities/sizing/020 | 271 | 1 |
| C97 | burakumin quarter | Does a burakumin quarter stand inside the walls? | C,K | THIN | cities/fabric/060 (1 note) | 271 | 1 |
| C98 | burakumin quarter | How big is the quarter, what are its dwellings like, and where does it lie relative to river, tannery and execution ground? | C,K | THIN | urban-features/066, 068 (tannery side only) | 271 | 1 |
| C99 | wells | How many wells, communal vs private, and the samurai exception? | T,C,K | COVERED | urban-features/090, 120 | 271 | 1 |
| C100 | privies and night soil | Where are a city's privies (the tenement's shared privy) and how was night soil collected? | C,K | THIN | cities/fabric/110 mentions; buildings/220 is a compound | 271 | 4 |
| C101 | street drains | Did city streets carry drains (dobu) or gutters, and how wide? | T,C,K | NONE | - | 271 | 4 |
| C102 | wards | What is a ward as a unit - its size, its headman, its gate - and how many does a city have? | C,K | THIN | cities/capitals/060 (the gates); nothing on ward size | 271 | 1 |

## Commerce and lodging

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C103 | shops | Which trades outgrow the shop glyph, and what is a shop's footprint? | T,C,K | COVERED | urban-features/030 | 271 | 1 |
| C104 | shops | How many shops does a city of a given size carry? | C,K | THIN | cities/fabric/050 (a floor calibrated on our maps) | 271 | 1 |
| C105 | gate market | What stands outside a city gate, and how big is the strip? | T,C,K | COVERED | cities/hinterland/040, towns/080 (strip size owed) | 269 B41 | 1 |
| C106 | market | Does a provincial city hold a main market - a Chinese walled market (shi), a market street, periodic market days (ichi) - and where, and how big? | C,K | NONE | (towns/080 is the gate market only) | 271 | 4 |
| C107 | fish market | Did a city keep a fish or produce market at the landing, and what did it look like? | C,K | NONE | - | 271 | 4 |
| C108 | trade streets | Were trades grouped into named streets or wards (kaji-machi, konya-machi, Chinese hang), and in a provincial city? | C,K | THIN | cities/capitals/336 (dyers' street, capital) | 271 | 4 |
| C109 | inns | How many inns does a city carry and where? | T,C | COVERED | cities/fabric/120, towns/050 | 271 | 1 |
| C110 | inns | How big is a city inn (hatago, Chinese kezhan), how many rooms and stories, with what yard? | T,C | THIN | towns/050 (two forms, rolled with no bias; no footprint quoted) | 271 | 1 |
| C111 | official inn | Did a seat on the highway keep a lords' inn (honjin, waki-honjin), and how big was it? | T,C | NONE | - | 271 | 3 |
| C112 | cheap lodging | How many cheap lodging houses did a city hold? | T,C | THIN | cities/fabric/120 (count a GM guess), towns/040 COVERED | 269 B40 | 1 |
| C113 | caravan cluster | What does a city keep for caravans, the market crowd and the festival? | C | COVERED | cities/fabric/130 | 271 | 1 |
| C114 | stable yards | What is a stable yard and how is it watered? | T,C | COVERED | urban-features/080 (THIN), 082 | 271 | 1 |
| C115 | stable stalls | How big is a stall, and a stable's building? | T,C | NONE | - | 267 R16 | 1 |
| C116 | teahouses | Did a city carry teahouses and eating houses as distinct buildings, and where (gate, temple, road)? | T,C | THIN | urban-features/030 (a null result: fits the shop glyph) | 271 | 4 |
| C117 | bathhouses | How many bathhouses (sento, Chinese yushi) per population, how big, what fuel yard, and where do they stand? | T,C,K | THIN | urban-features/030 (the rule), cities/capitals/330 (the Edo count); no footprint quoted | 271 | 1 |
| C118 | pawnshops | How many pawnshops, and what does the pledge court look like? | C,K | COVERED | urban-features/030, cities/capitals/330 (the court's size unquoted) | 271 | 1 |
| C119 | brewery | How big is a brewery compound, and how many per seat? | T,C,K | COVERED | urban-features/030 | 271 | 1 |
| C120 | dye yards | Where do dyers work, and how does a capital's dye trade change form? | C,K | COVERED | urban-features/030, cities/capitals/336 | 271 | 1 |
| C121 | oil press | How big is an oil press, how many, and where? | C,K | THIN | urban-features/030 (count a guess) | 271 | 1 |
| C122 | lumber yard | Where does a lumber yard stand? | C | COVERED | urban-features/030 | 271 | 1 |
| C123 | log boom | What is a log boom? | C | COVERED | urban-features/040 | 271 | 1 |
| C124 | kiln works | What is a kiln works and where does it stand? | T,C,K | COVERED | urban-features/050 | 271 | 1 |
| C125 | kiln works | What does a kiln works look like on the map? | T,C,K | THIN | urban-features/052 | 271 | 1 |
| C126 | tanning yards | Where do tanning yards stand and what do they need? | T,C | COVERED | urban-features/060, 062, 064, 066 | 271 | 1 |
| C127 | tanning yards | Which way out of town does a tanning yard stand? | T,C | THIN | urban-features/068 | 271 | 1 |
| C128 | farrier | What does a farrier draw on the map? | T,C | COVERED | urban-features/032 | 271 | 1 |
| C129 | blacksmith | How many ordinary blacksmiths and swordsmiths does a city carry, where, and is their smithy bigger than a shop? | T,C,K | THIN | urban-features/160 (refining forges), 032 (farrier), 030 (null list omits the smith) | 271 | 3 |
| C130 | refining forge | Where do refining forges go? | T,C | COVERED | urban-features/160 | 271 | 1 |
| C131 | charcoal yard | What is a charcoal yard? | T,C | COVERED | urban-features/150 | 271 | 1 |
| C132 | nuisance separations | How far must forge, charcoal, kiln and nuisance trades stand from dwellings? | T,C,K | COVERED | urban-features/030 | 271 | 1 |
| C133 | cloth and paper works | Did a city keep weaving, papermaking or other workshops whose premises break the shop glyph? | C,K | NONE | (urban-features/030 does not name them) | 271 | 4 |
| C134 | apothecary and physician | Did a city keep a physician's or relief house (Chinese huiminju, yangjiyuan) big enough to draw? | C,K | NONE | - | 271 | 4 |
| C135 | carts | Were carts confined to city streets, and what cart yards did a city need? | C | NONE | - | 267 R46 | 1 |

## Entertainment, training and schools

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C136 | theater stage | Where does the theater stage stand, which way does it open, how wide is its viewing ground? | T,C | COVERED | towns/060, cities/fabric/130 | 271 | 1 |
| C137 | playhouse | How big is a roofed playhouse, and does a capital carry several? | K | THIN | cities/capitals/333 (footprint a guess) | 271 | 4 |
| C138 | pleasure quarter | Did a provincial city or a capital have a licensed brothel quarter (yukaku, Chinese wazi / goulan), walled or open, where (edge, by the wharf), and how big? | C,K | NONE | cities/capitals/090 (next to the brokers is a guess), 333 (wazi counts, not form) | 271 | 4 |
| C139 | hirokoji | Did cleared fire strips double as amusement grounds? | C,K | COVERED | cities/fabric/150 | 271 | 1 |
| C140 | martial halls | How many state and private dojos does a city carry? | T,C,K | COVERED | cities/government/070, buildings/210 | 269 B39 | 1 |
| C141 | martial halls | How big is a dojo (hall, yard, the state drill hall), and what does it look like from above? | C,K | NONE | - | 271 | 1 |
| C142 | archery and riding grounds | Did a castle town keep an archery range or a riding ground (baba), how long, where? | C,K | NONE | - | 271 | 4 |
| C143 | commoner schools | How many writing schools (terakoya, Chinese sishu) did a city hold, and were they distinct buildings? | T,C | NONE | - | 271 | 4 |
| C144 | academies | Did a provincial city keep a Confucian academy or school-temple (shuyuan, wenmiao, a domain school's branch), and how big? | C | NONE | (cities/capitals/190 is the capital's hanko) | 271 | 4 |

## Religion and death in the city

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C145 | city temple | How big is a city temple, and how many monks? | C,K | COVERED | religion-and-death/010 (monk counts owed) | 269 B37 | 1 |
| C146 | city temples | How many temples per walled city? | C,K | COVERED | religion-and-death/020, 030 | 271 | 1 |
| C147 | clergy housing | Who lives inside a city temple's walls and who outside? | C,K | THIN | religion-and-death/040 (1 note) | 271 | 1 |
| C148 | temple-gate shops | What shops stand at a temple gate? | C,K | COVERED | religion-and-death/050 | 269 B37 | 1 |
| C149 | temple belt | Why do the temples belt the wall in a capital (teramachi)? | K | THIN | cities/capitals/200 (1 note) | 271 | 1 |
| C150 | temple approaches | Which way does a temple approach face, and who patrons modest temples? | K | COVERED | cities/capitals/260 | 271 | 1 |
| C151 | wayside shrines | What stands between the temples in a temple neighborhood? | C,K | COVERED | cities/government/020 | 271 | 1 |
| C152 | city shrine | Does a city keep a principal shrine (the town's ujigami, a Chinese city-god temple chenghuang miao), how big, and where? | C,K | NONE | (268's work is the village and country shrine) | 271 | 1 |
| C153 | torii in the city | Where do torii stand on a city street? | C,K | COVERED | religion-and-death/080, 090, cities/government/020 | 268 | 1 |
| C154 | city graveyards | How many graveyards does a city carry, and does the ceiling scale with temples? | C,K | COVERED | religion-and-death/070, cities/capitals/330 | 269 B37 | 1 |
| C155 | funerary ground | How far outside the wall does the funerary ground sit? | C,K | COVERED | cities/capitals/340 | 271 | 1 |
| C156 | crematory, ossuary, mausoleum | Where do they stand and how big are they? | T,C,K | COVERED | religion-and-death/190, 202, 204, 206 | 269 B36 / B37 | 1 |
| C157 | pauper ground | Is there one pauper ground per seat? | C,K | COVERED | cities/capitals/333 (its 10-30 ft size a guess) | 271 | 1 |

## Water, wharves and bridges

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C158 | river siting | Do most provincial cities sit on a river? | C,K | COVERED | cities/river-cities/010 | 271 | 1 |
| C159 | offtakes | Which way does an offtake leave a river? | C,K | COVERED | cities/river-cities/020 | 271 | 1 |
| C160 | city canals | Does a city's canal open its own mouth on the river? | C,K | THIN | cities/river-cities/030 | 269 B46 | 1 |
| C161 | city canals | How wide is a city canal, how is it revetted, and what lines its banks? | C,K | THIN | cities/capitals/300 (internal dock), water/010 | 271 | 1 |
| C162 | wharf | What is the wharf's working face - piers, quays, stepped landings? | C,K | COVERED | cities/river-cities/040 | 267 R42 (the gangi-vs-pier edit) | 1 |
| C163 | internal dock | When does a city get an internal dock and when a bank quay? | C,K | COVERED | cities/capitals/300 | 271 | 1 |
| C164 | jetty | How long is a jetty? | C,K | COVERED | cities/capitals/280 | 271 | 1 |
| C165 | towpath | Does a river get a towpath or a road? | C,K | COVERED | cities/capitals/130 | 271 | 1 |
| C166 | river watch | Was there a river guard post at a landing? | C | NONE | - | 267 R40 | 1 |
| C167 | city bridges | How many bridges does a city carry over its river and canals, of what type (plank, arched timber, stone), how wide and how long? | C,K | THIN | ways/010, 030 (village plank bridges) | 271 | 1 |
| C168 | ferry | When does a city cross its river by ferry rather than a bridge, and what does a ferry landing look like? | C,K | THIN | water/130 (mention) | 271 | 4 |
| C169 | bridge siting | Is the bridge where the road actually crosses the water? | T,C | THIN | ways/050 | 269 B46 | 1 |

## Hinterland

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| C170 | farmland ring | Why is a city ringed by farmland? | C,K | COVERED | cities/hinterland/020 | 271 | 1 |
| C171 | in-wall farming | Does a city farm inside its walls? | C,K | COVERED | cities/hinterland/050 | 271 | 1 |
| C172 | in-wall farmers | Who works the in-wall fields and where do they live, given a city has no farmer households (settlements/090)? | C | THIN | cities/hinterland/050, settlements/090 | 271 | 1 |
| C173 | moat and fields | Does the moat feed the fields, or do they drain into it? | C,K | THIN | cities/hinterland/030 | 269 B41 | 1 |
| C174 | suburban belt | What stood in the near hinterland - market gardens, suburban villages, tile and lime works, retreats - and how far out? | C,K | THIN | cities/hinterland/050 (in-wall only), urban-features/030 | 269 B41 (retreats); 271 (the rest) | 4 |
| C175 | approach roads | How wide are the roads into a city, and what lines them beyond the gate market (tree avenue, milestones, shrines)? | C,K | THIN | ways/020 (village lanes); 267 R47 is a compound's gates | 271 | 1 |
