# Sweep water G09 - handoff (session 1: write)

## Washing places at the water's edge

- SECTION=water/washing-places-at-the-waters-edge
- RENDERING=rendering/water/how-our-maps-draw-washing-places-at-the-waters-edge
- OLD=research/water/430-where-did-a-village-wash-its-vegetables-and-clothes-and-where-did-a-town-get-water-besides-its-wells.html
- MODALS=

## Villages beside their stream: one bank or both

- SECTION=water/villages-beside-their-stream-one-bank-or-both
- RENDERING=rendering/water/how-our-maps-place-a-hamlet-on-its-stream
- OLD=research/water/270-does-a-hamlet-stand-on-one-bank-of-its-stream-or-around-it-it-depends-on-the-size-of-the-water.html research/water/275-does-siting-doctrine-say-whether-a-village-may-straddle-its-water-no---it-puts-the-water-on-one-side-and-says-nothing-of-a-site-the-water-divides.html research/homesteads/250-does-a-farmstead-stand-whole-on-one-bank-of-the-brook.html
- MODALS=

- BASE=6fccdf4b1

Washing places: the brief listed no rendering section, but water 430 held a knob decision and a spec rule, so they moved to a new rendering section (430). The title carries no native term, because the sources use different names (araiba and kawado at Gujo, shikko at Hirosaki, kabata at Harie); the reasoning is in a comment. The cross-link to urban-features T2 points at that page's current anchor, `communal-wells-and-the-samurai-exception`, because "Communal wells (ido)" does not exist in this clone yet. That sweep's re-aim should pick it up. The cross-link to homesteads 200 points at its current anchor. Two kanji in copied note glosses (野 in harie-syozu-3, Yajima's book title in ndl-yajima-shuraku) were given their gloss so the prepass passes. Nothing was cut except the inciting question and the Sources roster.

Villages beside their stream: homesteads 250 folded here, with its map rule in the rendering section. Its mizu-no-bunka-60 note, the superset with two passages, replaces water 270's one-passage note of the same key. 275's inline search parenthetical became the absence note `villages-beside-their-stream-one-bank-or-both`. 270's "a brook seven feet wide" sentence moved to the rendering section because it is about the map's brook. Code comments naming the old heading were re-aimed in `hamletgen/cluster.py` and `hamletgen/consts.py`. No modal named any folded section. Nothing was cut except the inciting question, 275's pointer paragraph and the Sources rosters.
