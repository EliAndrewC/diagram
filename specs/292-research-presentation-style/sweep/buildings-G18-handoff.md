# Handoff - feature 292 sweep, buildings G18 (write)

## Staff rowhouses and barracks (nagaya)

- SECTION=buildings/staff-rowhouses-and-barracks-nagaya
- RENDERING=rendering/buildings/how-our-maps-draw-staff-rowhouses-and-barracks-nagaya
- OLD=research/contents.json#compounds research/contents.json#compounds research/contents.json#compounds
- MODALS=Barracks RetainersQuarters

## Stables (umaya)

- SECTION=buildings/stables-umaya
- RENDERING=rendering/buildings/how-our-maps-draw-stables-umaya
- OLD=research/contents.json#compounds
- MODALS=Stables

- BASE=6b6c58b61

## Left open

Staff rowhouses and barracks: nothing was held by another feature and no claim was cut except the two pointer sentences between the old sections (REMOVED comment); the rendering section's rule (a barracks 12 to 24 ft deep) is contradicted by the county plan's drawn barracks (compound.py, 45 x 34 ft) and by the Barracks modal's "about 20 to 70 ft by 10 to 40 ft", recorded as OPEN in a comment in the rendering fragment and not changed by this restyle; the Mitamura note's untranslated book title was replaced by an English description (the characters kept in a comment) in both notes files to clear the prepass; the link from 0115 now points at the new section.

Stables: nothing held and nothing cut; 180's stall-width passage was already cut there and pointed here, and its link now reads 'Stables (umaya)'; cities/government 290's comment-only pointer was re-aimed to #stables-umaya (still a comment, as it was); the glossary term umaya, which defined only a farmhouse's stable, now covers a warrior's too.
