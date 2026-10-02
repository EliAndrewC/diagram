# Feature 301 - the pointers the sweep could not resolve alone (FR-013)

`scripts/_pointer_sweep.py` resolves a pointer only when it is certain: an id in exactly one fragment, a quoted heading
that exactly one question carries (exactly, by the record's anchor rule, by the prefix rule `Entry:` lines used, or
verbatim inside exactly one question). These are the rest, resolved by hand on 2026-10-01, each read against the record
as it stands. Almost every one names a heading that feature 292 retired: its research went into a question of the same
page, and its drawing rule into the page's rendering counterpart - so a pointer from engine code that described how a
map draws a thing lands on the rendering question, and one that described what history did lands on the research
question. The sweep reads this table (`--map`); a row's target is a fragment path (a unique prefix is enough).

| page | quoted heading or anchor | target | why |
|---|---|---|---|
| water.html | Drawn width is RANK | research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html- | the drawn-width rule went to the rendering of channel widths |
| water.html | what-drawing-at-true-size-left-open | research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html- | the true-size width limitation it named is recorded with the drawn widths |
| water.html | Water-width ladder - the real-world tiers | research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html- | the real-world ladder of channel widths |
| water.html | The head-race forks - supply commands both flanks | research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html- | how the maps lay out the head-race |
| water.html | Does a hamlet stand on one bank of its stream, or around it? | research/questions/0035-villages-beside-their-stream-one-bank-or-both.html- | villages beside their stream: one bank or both |
| water.html | Where does the brook stop being a brook and become the ditch | research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html- | where the ditch leaves the brook |
| water.html | Is there a weir at the intake? | research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html- | the intake and its weir |
| water.html | Why does every ditch turn on a curve? | research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html- | how the maps draw bends and junctions |
| water.html | Where two watercourses meet, how is the junction drawn? | research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html- | how the maps draw bends and junctions |
| water.html | The wet toe is as wide as the FAN | research/questions/0057-marshes-and-wetlands-shitchi.drawing.html- | how the maps draw the marsh at the fan's toe |
| water.html | the wet toe is as wide as the fan | research/questions/0057-marshes-and-wetlands-shitchi.drawing.html- | the same rule |
| water.html | the marsh follows the fan's toe | research/questions/0057-marshes-and-wetlands-shitchi.drawing.html- | the same rule |
| water.html | What ground is too wet to build on? | research/questions/0058-ground-too-wet-to-build-on.html- | ground too wet to build on |
| water.html | A reservoir's shore is reeded, and its EMBANKMENT is mown | research/questions/0061-reservoir-ponds-tameike.html- | reservoir ponds, their shore and embankment |
| cities/defenses.html | wall-towers-the-mamian-system-and-bowshot-ranges | research/cities/defenses/060- | towers along the city wall (mamian) |
| rendering/cities/defenses.html | How our maps keep the strip inside the wall clear | research/rendering/cities/defenses/080- | the street along the inside of the wall |
| vegetation.html | forest-density-and-crown-size | research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.html- | how thickly trees stood, and how wide their crowns |
| buildings.html | How big was a samurai's house, and what rank is a 67-tsubo house? | research/cities/government/280- | samurai house lots and houses by rank - where the 67-tsubo house is |
| buildings.html | How wide was the main gate of a magistrate's post? | research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html- | the main gate and its gatekeepers |
| buildings.html | Where did the gatekeepers sit - in the gate range, or a gatehouse beside it? | research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html- | the main gate and its gatekeepers |
| buildings.html | Was the hearing court open white sand, or roofed? | research/questions/0099-the-hearing-court-shirasu.html- | the hearing court (shirasu) |
| buildings.html | How big was a holding cell? | research/questions/0096-holding-cells-agariya-and-roya.html- | holding cells |
| buildings.html | Did a granary stand on posts, and why raise its floor away from a river? | research/questions/0098-storehouses-for-the-tax-rice.html- | storehouses for the tax rice |
| buildings.html | Were a residence's wings joined by corridors and set in echelon? | research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html- | samurai residences and their rooms |
| buildings.html | Where is the formal entrance, and how does a guest reach it? | research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html- | the formal entrance (genkan) |
| buildings.html | Did a residence have its own bath, and was it a building apart? | research/questions/0105-baths-furo.html- | baths (furo) |
| buildings.html | The shady rear is the service strip | research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html- | how the maps lay out the residence |
| buildings.html | Guest doors feed courts, not flanks | research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html- | how the maps draw the formal entrance and a guest's arrival |
| rendering/buildings.html | Historical grounding: martial training in a provincial city | research/questions/0165-martial-training-grounds-and-dojo.drawing.html- | how the maps draw practice grounds and dojo |
| fields.html | Why do neighboring dry plots run their furrows different ways? | research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html- | how the maps draw dry fields, their furrows among them |
| fields.html | Where dry (hatake) crops go | research/questions/0006-dry-fields-and-their-crops-hatake.html- | dry fields and their crops - the catena is there |
| fields.html | Where dry (hatake) crops go - the topographic catena | research/questions/0006-dry-fields-and-their-crops-hatake.html- | the same |
| fields.html | Are there really graves out in the middle of the fields? | research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.html- | ponds, rocks and graves in the middle of the fields |
| fields.html | Plot sizes, pond sizing and acreage from population | research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html- | how much farmland a settlement works, and in what tracts |
| fields.html | Tract sizes - no settlement-class cap | research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html- | the same |
| fields.html | What is the farmland around a town or a city made of? | research/questions/0010-farmland-around-towns-and-cities.html- | farmland around towns and cities |
| fields.html | What a bund bean actually looks like | research/questions/0014-bunds-between-the-paddies-aze.html- | bunds between the paddies, the bund beans among them |
| homesteads.html | The garden's sun | research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html- | how the maps keep yards and gardens in the sun |
| homesteads.html | The threshing yard's sun | research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html- | the same |
| homesteads.html | How deep is the stand? | research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html- | how the maps draw the farmhouse grove, its depth among it |
| homesteads.html | Homestead groves (yashikirin) - the real scale and prevalence | research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html- | groves of trees around farmhouses |
| archetypes.html | The three overlays a village may carry | research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html- | how the maps lay cash crops over a village's rice land |
| archetypes.html | Grid vs mosaic | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | how the maps draw parcels and bunds inside a polder |
| archetypes.html | Polder mosaic | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | the same |
| archetypes.html | Polder mosaic vs grid | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | the same |
| archetypes.html | Polder fifth pass | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | the same |
| archetypes.html | Polder edge wander | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | the same |
| archetypes.html | The perimeter dike followed the natural water edge | research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html- | polders: fields diked against the fluctuating water |
| archetypes.html | Polder siting - full enclosure, fluctuating water and where the village sits | research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html- | the same |
| archetypes.html | What stands on a dike-pond hamlet that a paddy hamlet lacks? | research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html- | the dike-pond hamlet: its houses, boats and manure jars |
| archetypes.html | The 6:4 water-to-dike ratio and coppiced mulberry | research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html- | dike-ponds: fish ponds ringed by mulberry dikes |
| archetypes.html | The bank is a ring | research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html- | how the maps draw dike-ponds |
| settlements.html | What are the five kinds of settlement, and how big is each? | research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html- | the five sizes of settlement |
| settlements.html | Is every household in a hamlet actually drawn? | research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html- | how the maps draw and state each size of settlement |
| rendering/urban-features.html | How our maps draw shops, and the trades that outgrow the shop glyph | research/questions/0183-shops-and-trades-in-towns-and-villages.drawing.html- | how the maps draw shops and trades |
| rendering/cities/government.html | How our maps place and count a city's samurai households | research/rendering/cities/government/030- | how the maps draw the samurai quarter and count its households |
| rendering/cities/fabric.html | How our maps draw ward walls and ward gates | research/rendering/cities/fabric/210- | how the maps draw city wards and their gates |
| cities/capitals.html | Street widths | research/rendering/cities/capitals/010- | how the maps size and lay out a domain capital |
| cities/capitals.html | Dimensional audit | research/rendering/cities/capitals/010- | the same |
| cities/capitals.html | A river gets a TOWPATH, not a road | research/rendering/cities/capitals/130- | how the maps draw a towpath along a river |
| cities/capitals.html | A castle has TWO gates | research/rendering/cities/capitals/020- | how the maps draw the castle in a capital |
| cities/capitals.html | How a josui actually ran | research/cities/capitals/080- | the capital's aqueduct (josui) |
| cities/capitals.html | Placements that change | research/rendering/cities/capitals/390- | how the maps draw a capital differently from a provincial city |
| cities/capitals.html | a different program, not a scaled precinct | research/rendering/cities/capitals/390- | the same |
| buildings.html | Cells are remand, not punishment | research/questions/0096-holding-cells-agariya-and-roya.html- | holding cells |
| vegetation.html | Scrub stays off open water | research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.drawing.html- | how the maps keep scrub off fields, channels and open water |
| vegetation.html | The cut bank | research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.html- | scrub and rough grass at the edges of fields and channels - the cut bank among them |
| vegetation.html | How did a lane get through a belt? | research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html- | how the maps draw the shelter belt, where the lanes cross it |
| rendering/vegetation.html | Village windbreak | research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html- | the same |
| towns.html | The market-day flophouse | research/questions/0185-travelers-inns-and-cheap-lodging-houses-hatago-dian-kichin-yado.html- | travelers' inns and cheap lodging houses |
| urban-features.html | Caste geography | research/questions/0156-burakumin-quarters-and-caste-zoning.html- | burakumin quarters and caste zoning |
| fields.html | Bunds are shared, and the fabric is continuous | research/questions/0014-bunds-between-the-paddies-aze.html- | bunds between the paddies |
| fields.html | Minimum basin SIZE | research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html- | how the maps draw paddies and their plots, the smallest basin among it |
| fields.html | A basin never tapers to a point - the fan toe truncates | research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html- | how the maps draw the wet plots at the fan's toe |
| fields.html | A basin never tapers to a point | research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html- | the same |
| fields.html | The wettest plots are their own kind of ground | research/questions/0007-wet-paddies-that-never-drain-shitsuden.html- | wet paddies that never drain (shitsuden) |
| fields.html | In-field features | research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.html- | ponds, rocks and graves in the middle of the fields |
| rendering/fields.html | How our maps draw dry fields and their furrows | research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html- | how the maps draw dry fields and their crops |
| homesteads.html | Which farmhouses have a storehouse? | research/questions/0040-farm-storehouses-kura.html- | farm storehouses (kura) |
| homesteads.html | Was the homestead grove there before 1868, and what size and shape was it? | research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html- | groves of trees around farmhouses |
| homesteads.html | Which side of the house did the windbreak stand on | research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html- | the same - the grove's sides |
| homesteads.html | How does a village lane bend? | research/questions/0081-village-lanes.html- | village lanes |
| cities/capitals.html | How much of a capital lives OUTSIDE the walls | research/rendering/cities/capitals/010- | how the maps size and lay out a domain capital |
| cities/capitals.html | The sluice's lifting frame, the quay-side kura, and the boat-length jetty | research/cities/capitals/090- | rice storehouses and the brokers' row on the water |
| cities/capitals.html | The government ward | research/rendering/cities/capitals/010- | how the maps size and lay out a domain capital, its wards among it |
| cities/fabric.html | Machiya row density | research/cities/fabric/010- | the street front's continuous rows of shophouses |
| cities/defenses.html | Historical grounding | research/cities/defenses/250- | the guardhouse and inspection hall it sizes: barriers and inspection posts at a town's entrance |
| archetypes.html | Polder fourth pass | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html- | how the maps draw parcels and bunds inside a polder |
| archetypes.html | Why is a hand-piled bund never straight - and never square at the corners? | research/questions/0022-parcels-and-bunds-inside-a-polder-aze.html- | parcels and bunds inside a polder |
| archetypes.html | A dike-pond is fed and drained through sluice gates | research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html- | dike-ponds: fish ponds ringed by mulberry dikes |
| archetypes.html | The 6:4 water-to-dike ratio, and coppiced mulberry | research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html- | the same |
| archetypes.html | The three overlay values | research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html- | how the maps lay cash crops over a village's rice land |
| archetypes.html | The scripted dike-pond hamlet - the rules | research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.drawing.html- | how the maps furnish a dike-pond hamlet |
| water.html | The wet toe is as wide as the fan, not as wide as the valley | research/questions/0057-marshes-and-wetlands-shitchi.drawing.html- | how the maps draw the marsh at the fan's toe |
| water.html | What drawing at TRUE SIZE left open | research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html- | the true-size width limitation, with the drawn widths |
| water.html | a plank is laid only over water you cannot stride across | research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html- | plank bridges over farm ditches |
| ways.html | How far past the bank does a bridge land? | research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html- | how the maps place and draw road bridges |
| settlements.html | ASK THESE THREE BEFORE DRAWING ANYTHING | research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html- | the five sizes of settlement |

Edited by hand rather than swept: `.specify/templates/spec-template.md` (its example pointer `research/contents.json#water`
becomes the fragment form).
