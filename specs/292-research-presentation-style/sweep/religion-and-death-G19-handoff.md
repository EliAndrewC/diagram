# Handoff - feature 292 sweep, religion-and-death G19 (write)

## Ground swept clear around shrines and graves

- SECTION=religion-and-death/ground-swept-clear-around-shrines-and-graves
- RENDERING=rendering/religion-and-death/how-our-maps-draw-the-swept-ground-around-shrines-and-graves
- OLD=research/contents.json#religion-and-the-dead research/contents.json#religion-and-the-dead research/contents.json#religion-and-the-dead
- MODALS=SweptClearing ShrineGrove

## Salt heaps at doorways (morijio)

- SECTION=religion-and-death/salt-heaps-at-doorways-morijio
- RENDERING=rendering/religion-and-death/how-our-maps-draw-salt-heaps-at-doorways-morijio
- OLD=research/contents.json#religion-and-the-dead
- MODALS=

- BASE=0bfdb1aba

## Open

Swept ground: no claim was cut (only the two pointer sentences between 130 and 720, in a REMOVED comment), and no section was held by another feature. 140 went wholly to the rendering section. Its ragged-edge reasoning is now tied to the precinct's cleared ground, the one clearing that still runs past a feature's footprint: since feature 280 M66 the arches and grave plots clear only their own ground (extra 0 in `_clear_ground`), so no notches are drawn there. The rendering section also states the hall's 58 px reach as a GUESS, as `shrines.py` does. The shrine.py SweptClearing and grounds.py ShrineGrove `Entry:` lines now name the new research and rendering titles; neither class is in `classes_before_189.json`. The link in rendering 122 (ruled edges) now points at the new rendering section. The code comments in cover.py, core.py and funerary.py name the new headings. The ryobosei-jawiki-2 note's gloss of the kanji for the burying grave took the `(umebaka, "burying grave")` form for the prepass. The research section keeps the setting's equinox grave cleaning (canon, l7r.md Haru and Aki Higan) with no footnote, as the old 720 did.

Salt heaps: the old section's decision (no salt at an official's compound, no cone or pair on any map) became a one-paragraph rendering section. No claim was cut. The research section has one lead line with a year, 1838-40, that has no glossary tooltip and is tied to "late in the Edo period" in the line.
