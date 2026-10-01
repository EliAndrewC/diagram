# Handoff - feature 292 sweep, homesteads group G01 (session 1: write)

## Groves of trees around farmhouses (yashikirin) - additions to the finished pilot

- SECTION=homesteads/groves-of-trees-around-farmhouses-yashikirin
- RENDERING=rendering/homesteads/how-our-maps-draw-the-groves-around-farmhouses
- OLD=research/vegetation/
- MODALS=Copse
- BASE=efbd6eb95

Vegetation 210's findings went in as five additions to the pilot's scale and prevalence bullets, and the rest of the
pilot text was left as accepted: a sentence on the 2004 Tonami species study added to the cedar bullet, and new bullets
for the 1684 Mito register's homestead woods (about 6,000-28,000 sq ft), the encyclopedia's "form, size and species
varied", the absence of any wood shared by a whole village among its houses, and the 1910 Musashino account. Its map
rule (grove and copse counted as one wood, the size rolled within the register's range, the copse filled to what the
groves and windbreak leave, the 90 ft dooryard reach) went to the rendering section as three bullets and a "Each farm's
wood" spec item. The roll's shape (log-uniform) and the 90 ft reach / copse drawn short were taken from the code and
the Copse modal, not from 210's text. Nothing was cut and no section was held by another feature. Keys renamed to be
unique on the homesteads page: yashikirin-jawiki-7 to -13, miura-2019-yashikiyama to -2, miura-2019-yashikiyama-2 to
-3, shakkanho-jawiki to -3, and the absence note how-big-was-the-villages-dooryard-copse to
groves-of-trees-around-farmhouses-yashikirin-11 (converted to the new form). The miura-2019-yashikiyama-3 note's own
trailing gloss "(the reading of 近野 is not given)" was reworded without the kanji, which the prepass failed; its quoted
passage is unchanged. Links re-aimed: vegetation/020's dooryard-copse bullet, the Copse modal's Entry and its fixture,
and the code comments in hinterland/stages.py, homestead_parts/groves.py, stands.py, wood_share.py and the
test_homestead_woods.py docstring (now rendering/homesteads/010). The confusable pair grove / dooryard copse is
appended to confusables.md (the table's earlier "NOT YET READ" row for it can now take this line's difference).
