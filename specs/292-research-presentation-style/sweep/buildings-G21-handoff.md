# 292 sweep - buildings G21 handoff (session 1: write, 2026-09-30)

- BASE=b5e0e4c9b

## Border posts and their crossing court (kuchidome bansho)

- SECTION=buildings/border-posts-and-their-crossing-court-kuchidome-bansho
- RENDERING=rendering/buildings/how-our-maps-draw-a-border-crossing-court
- OLD=research/contents.json#compounds
- MODALS=BorderCourt

Nothing cut; the old "What this means for a plan" (the court accurate as crossing ground, the reception room accurate, the delegations' court a deviation) is the rendering section. The town barrier post (0133) and the clan border (0083) are logged as confusables and kept apart.

## Rooms for a parley across a border

- SECTION=buildings/rooms-for-a-parley-across-a-border
- RENDERING=rendering/buildings/how-our-maps-draw-a-parley-room-on-a-border
- OLD=research/contents.json#compounds
- MODALS=ParleyRoom ParleyMats

The room astride the line and its mats are labeled a deliberate deviation in the rendering section; the old "GM's ruling that the door which receives the Kitsune is the border" is told as the project's choice, with the ruling in a comment (610 kept no date for it).

## Doorways and doors (to)

- SECTION=buildings/doorways-and-doors-to
- RENDERING=rendering/buildings/how-our-maps-draw-doors
- OLD=research/contents.json#compounds
- MODALS=Door

The history went to the research section and the drawn widths to the rendering section, which also carries the 6 ft DOOR_W_FT of generated lodgings (from compound_model.py's comment, now re-aimed) and buildings 200's door-on-a-wall check. That check's full text stays in 0090's comment, and 010's bullet now links here. The shipped pool maps (e.g. county-magistracy-example.html) still embed the old question title in their classes JSON until they are regenerated.

## Samurai country manors (bushi yakata)

- SECTION=buildings/samurai-country-manors-bushi-yakata
- RENDERING=rendering/buildings/how-our-maps-draw-a-samurais-country-manor
- OLD=research/contents.json#compounds
- MODALS=

770 stated a drawn size (about 1 acre) and a map rule, so a rendering section was made, carrying the rule as a spec. OPEN: no generator code was found rolling the moated form. Cut under STYLE.md 4: the absence note's visible Mu family estate figure (20,000 m2, from a heritage page that could not be fetched), now in the note's comment. The "What stands inside" pointer is now a closing paragraph linking the house, stable, garden and bath sections. The capitals/100 link was re-aimed, and the gentry estates of 0173 are logged as a confusable.
