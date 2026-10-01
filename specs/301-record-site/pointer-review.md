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
| water.html | Drawn width is RANK | research/rendering/water/010- | the drawn-width rule went to the rendering of channel widths |
| water.html | what-drawing-at-true-size-left-open | research/rendering/water/010- | the true-size width limitation it named is recorded with the drawn widths |
| water.html | Water-width ladder - the real-world tiers | research/water/010- | the real-world ladder of channel widths |
| water.html | The head-race forks - supply commands both flanks | research/rendering/water/005- | how the maps lay out the head-race |
| water.html | Does a hamlet stand on one bank of its stream, or around it? | research/water/270- | villages beside their stream: one bank or both |
| water.html | Where does the brook stop being a brook and become the ditch | research/water/250- | where the ditch leaves the brook |
| water.html | Is there a weir at the intake? | research/water/250- | the intake and its weir |
| water.html | Why does every ditch turn on a curve? | research/rendering/water/190- | how the maps draw bends and junctions |
| water.html | Where two watercourses meet, how is the junction drawn? | research/rendering/water/190- | how the maps draw bends and junctions |
| water.html | The wet toe is as wide as the FAN | research/rendering/water/140- | how the maps draw the marsh at the fan's toe |
| water.html | the wet toe is as wide as the fan | research/rendering/water/140- | the same rule |
| water.html | the marsh follows the fan's toe | research/rendering/water/140- | the same rule |
| water.html | What ground is too wet to build on? | research/water/160- | ground too wet to build on |
| water.html | A reservoir's shore is reeded, and its EMBANKMENT is mown | research/water/280- | reservoir ponds, their shore and embankment |
| cities/defenses.html | wall-towers-the-mamian-system-and-bowshot-ranges | research/cities/defenses/060- | towers along the city wall (mamian) |
| rendering/cities/defenses.html | How our maps keep the strip inside the wall clear | research/rendering/cities/defenses/080- | the street along the inside of the wall |
| vegetation.html | forest-density-and-crown-size | research/vegetation/060- | how thickly trees stood, and how wide their crowns |
| buildings.html | How big was a samurai's house, and what rank is a 67-tsubo house? | research/cities/government/280- | samurai house lots and houses by rank - where the 67-tsubo house is |
| buildings.html | How wide was the main gate of a magistrate's post? | research/buildings/480- | the main gate and its gatekeepers |
| buildings.html | Where did the gatekeepers sit - in the gate range, or a gatehouse beside it? | research/buildings/480- | the main gate and its gatekeepers |
| buildings.html | Was the hearing court open white sand, or roofed? | research/buildings/090- | the hearing court (shirasu) |
| buildings.html | How big was a holding cell? | research/buildings/040- | holding cells |
| buildings.html | Did a granary stand on posts, and why raise its floor away from a river? | research/buildings/080- | storehouses for the tax rice |
| buildings.html | Were a residence's wings joined by corridors and set in echelon? | research/buildings/380- | samurai residences and their rooms |
| buildings.html | Where is the formal entrance, and how does a guest reach it? | research/buildings/300- | the formal entrance (genkan) |
| buildings.html | Did a residence have its own bath, and was it a building apart? | research/buildings/320- | baths (furo) |
| buildings.html | The shady rear is the service strip | research/rendering/buildings/380- | how the maps lay out the residence |
| buildings.html | Guest doors feed courts, not flanks | research/rendering/buildings/300- | how the maps draw the formal entrance and a guest's arrival |
| rendering/buildings.html | Historical grounding: martial training in a provincial city | research/rendering/buildings/210- | how the maps draw practice grounds and dojo |
| fields.html | Why do neighboring dry plots run their furrows different ways? | research/rendering/fields/160- | how the maps draw dry fields, their furrows among them |
| fields.html | Where dry (hatake) crops go | research/fields/160- | dry fields and their crops - the catena is there |
| fields.html | Where dry (hatake) crops go - the topographic catena | research/fields/160- | the same |
| fields.html | Are there really graves out in the middle of the fields? | research/fields/010- | ponds, rocks and graves in the middle of the fields |
| fields.html | Plot sizes, pond sizing and acreage from population | research/fields/110- | how much farmland a settlement works, and in what tracts |
| fields.html | Tract sizes - no settlement-class cap | research/fields/110- | the same |
| fields.html | What is the farmland around a town or a city made of? | research/fields/130- | farmland around towns and cities |
| fields.html | What a bund bean actually looks like | research/fields/260- | bunds between the paddies, the bund beans among them |
| homesteads.html | The garden's sun | research/rendering/homesteads/040- | how the maps keep yards and gardens in the sun |
| homesteads.html | The threshing yard's sun | research/rendering/homesteads/040- | the same |
| homesteads.html | How deep is the stand? | research/rendering/homesteads/010- | how the maps draw the farmhouse grove, its depth among it |
| homesteads.html | Homestead groves (yashikirin) - the real scale and prevalence | research/homesteads/010- | groves of trees around farmhouses |
| archetypes.html | The three overlays a village may carry | research/rendering/archetypes/030- | how the maps lay cash crops over a village's rice land |
| archetypes.html | Grid vs mosaic | research/rendering/archetypes/050- | how the maps draw parcels and bunds inside a polder |
| archetypes.html | Polder mosaic | research/rendering/archetypes/050- | the same |
| archetypes.html | Polder mosaic vs grid | research/rendering/archetypes/050- | the same |
| archetypes.html | Polder fifth pass | research/rendering/archetypes/050- | the same |
| archetypes.html | Polder edge wander | research/rendering/archetypes/050- | the same |
| archetypes.html | The perimeter dike followed the natural water edge | research/archetypes/160- | polders: fields diked against the fluctuating water |
| archetypes.html | Polder siting - full enclosure, fluctuating water and where the village sits | research/archetypes/160- | the same |
| archetypes.html | What stands on a dike-pond hamlet that a paddy hamlet lacks? | research/archetypes/170- | the dike-pond hamlet: its houses, boats and manure jars |
| archetypes.html | The 6:4 water-to-dike ratio and coppiced mulberry | research/archetypes/140- | dike-ponds: fish ponds ringed by mulberry dikes |
| archetypes.html | The bank is a ring | research/rendering/archetypes/140- | how the maps draw dike-ponds |
| settlements.html | What are the five kinds of settlement, and how big is each? | research/settlements/010- | the five sizes of settlement |
| settlements.html | Is every household in a hamlet actually drawn? | research/rendering/settlements/010- | how the maps draw and state each size of settlement |
| rendering/urban-features.html | How our maps draw shops, and the trades that outgrow the shop glyph | research/rendering/urban-features/310- | how the maps draw shops and trades |
| rendering/cities/government.html | How our maps place and count a city's samurai households | research/rendering/cities/government/030- | how the maps draw the samurai quarter and count its households |
| rendering/cities/fabric.html | How our maps draw ward walls and ward gates | research/rendering/cities/fabric/210- | how the maps draw city wards and their gates |
| cities/capitals.html | Street widths | research/rendering/cities/capitals/010- | how the maps size and lay out a domain capital |
| cities/capitals.html | Dimensional audit | research/rendering/cities/capitals/010- | the same |
| cities/capitals.html | A river gets a TOWPATH, not a road | research/rendering/cities/capitals/130- | how the maps draw a towpath along a river |
| cities/capitals.html | A castle has TWO gates | research/rendering/cities/capitals/020- | how the maps draw the castle in a capital |
| cities/capitals.html | How a josui actually ran | research/cities/capitals/080- | the capital's aqueduct (josui) |
| cities/capitals.html | Placements that change | research/rendering/cities/capitals/390- | how the maps draw a capital differently from a provincial city |
| cities/capitals.html | a different program, not a scaled precinct | research/rendering/cities/capitals/390- | the same |

Edited by hand rather than swept: `.specify/templates/spec-template.md` (its example pointer `research/water.html#...`
becomes the fragment form).
