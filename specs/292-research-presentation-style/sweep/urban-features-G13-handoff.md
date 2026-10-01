# urban-features G13 - handoff (session 1: write)

## Straw bales of rice and charcoal (tawara)

- SECTION=urban-features/straw-bales-of-rice-and-charcoal-tawara
- RENDERING=rendering/urban-features/how-our-maps-draw-straw-bales-of-rice-and-charcoal-tawara
- OLD=research/urban-features/
- MODALS=TaxBarge CharcoalBales

## Iron refining forges (chao)

- SECTION=urban-features/iron-refining-forges-chao
- RENDERING=rendering/urban-features/how-our-maps-draw-iron-refining-forges-chao
- OLD=research/urban-features/
- MODALS=

## Pottery kilns (noborigama)

- SECTION=urban-features/pottery-kilns-noborigama
- RENDERING=rendering/urban-features/how-our-maps-draw-kiln-works
- OLD=research/urban-features/ research/urban-features/
- MODALS=

- BASE=8f75f8d49

No claim held any of the four sections, and all were folded.

Bales: the brief listed no rendering section, but 190's "rule the map follows" paragraph was a map rule, so it moved to a new rendering section. Both modals' Entry lines now name that section as well as the research one. The research section links to the granary topic (buildings, T18) and to the charcoal yards topic (T14). The charcoal section's link to the old bale anchor was re-aimed. The absence notes were renamed bale-size-absence and bale-scaling-absence. The classes_before_189.json fixture has no entry for either class.

Forges: the brief listed no rendering section here either. 160's map rules (the two-site design, no furnace on a town map, true size, the glyph notes) went to a new one. The 80% share of Japan's iron was cut because no page read supports it; the Japanese Wikipedia article on tatara ironmaking, read 2026-09-30, doesn't give it either. In its place is that article's statement that the gunsmiths' iron came almost all from the Chugoku Mountains (new note tatara-seitetsu-jawiki-2, whose original make record stored). The rest of the old absence note is kept as chugoku-iron-share-absence. The nitre-bed reading is now footnoted to Wagner's own words (new note wagner-ming-iron-8). The "GM setting canon overrides" sentence is now a comment in the rendering section. The trades.py docstring for refining_forge was re-aimed, but it still says the kiln ratio is "six parts wood to one" (the record says 4.5) and still says the Xuxiebian site is attested, which the record says it is not. Neither was changed here.

Kilns: the GM's two inciting questions, the shouted headings, the pointer paragraphs and the unsupported "Seto/Bizen/Jingdezhen pattern" were cut. They are named in the REMOVED comment. 052's measured kiln lengths and chambers stay in the research section. The glyph, the 60 ft gap, the sizes and the glyph-defect notes are in the rendering section. The rendering section gives the default caption as "kiln works", which is what s.kiln uses (the record had said "kiln"). The kiln docstring in trades.py and the shops section's link were re-aimed. The docstring still repeats the "Seto/Bizen" and "a tiled roof lasts generations" claims, which were not changed here. The absence note for the sheds' sizes was renamed kiln-works-size-absence.
