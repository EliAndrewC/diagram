# Handoff - feature 292 sweep, fields G04 (write)

- BASE=95f489b22

## Wet paddies that never drain (shitsuden)

- SECTION=fields/wet-paddies-that-never-drain-shitsuden
- RENDERING=rendering/fields/how-our-maps-draw-wet-paddies-shitsuden
- OLD=research/fields/190-the-wettest-plots-are-their-own-kind-of-ground---shitsuden-and-why-they-read-blue.html
- MODALS=WetPaddy

Cut under STYLE.md 4, with a REMOVED comment: the IRRI 5-10 cm depth "reached only in a search summary" (its search kept as the silence on a season-long depth) and the "5-20 cm once credited to FAO" figure with its absence note; the silence on water showing between the plants, unfootnoted in 190, is now a grounds note (`the record's own silence`) in the rendering section. The water page's marsh topic (T14) is linked from the opening at its current anchor, `water.html#marsh---wet-rice-is-reclaimed-from-wetland`; when T14 folds, that link is re-aimed by its session. Open for an engine session (already noted by the G03 check): a FLOODED fill is classed wet paddy at the comb emit site, so the few rice plots paddy.py draws still flooded share the wet paddy's color.

## Paddies left to rest (kataarashi)

- SECTION=fields/paddies-left-to-rest-kataarashi
- RENDERING=rendering/fields/how-our-maps-place-paddies-left-to-rest-kataarashi
- OLD=research/fields/250-is-any-paddy-left-to-rest---and-where-does-a-resting-plot-lie.html
- MODALS=Fallow

The setting's canon paragraph moved to the rendering section and now cites `l7r-budgets` (the "Total rice production" passage, checked with `make canon` 2026-09-30) - a new note, not a new registry key; the old section had it uncited. The rule's "a few plots" is now stated as the engine's two to four, a GUESS.

## Ponds, rocks and graves in the middle of the fields

- SECTION=fields/ponds-rocks-and-graves-in-the-middle-of-the-fields
- RENDERING=rendering/fields/how-our-maps-place-ponds-rocks-and-graves-in-the-fields
- OLD=research/fields/010-in-field-features---flat-flooded-paddy-hosts-obstacles-least.html
- MODALS=FieldPond FieldRock GraveIsland

Water T3 has not folded yet, so the plains-pond evidence (tameike-jawiki, inamino-saraike, kagawa-tameike-data) stays here in full rather than be lost, and links the current reservoir section (`water.html#a-reservoirs-shore-is-reeded-...`); T3 may take it and leave a pointer. The fengshui-enwiki note was split: its second passage, a part of tameike-jawiki#1, and the original stored under fengshui-enwiki#1 are dropped (REMOVED comment). The grave evidence links religion-and-death T16 (280); that section's link to this one was re-aimed with shorter link text, since the full title put 280 5 bytes over the 20,000-byte cap. The town and city exemption in the rendering section comes from the code comment in features.py, and the crescent-pond pointer (homesteads 180) moved to the rendering section.
