# Handoff - feature 292 sweep, buildings G20 (write)

## Martial training grounds and dojo

- SECTION=buildings/martial-training-grounds-and-dojo
- RENDERING=rendering/buildings/how-our-maps-draw-practice-grounds-and-dojo
- OLD=research/buildings/ research/buildings/ research/buildings/ research/cities/government/ research/cities/government/
- MODALS=PracticeGround StrikingPosts WeaponRack

- BASE=3bc521397

## Left open

Martial training grounds and dojo: nothing was held by another feature. cities/government 320 (the city's drill ground as a reserve quarter) was NOT folded - it is a city-layout topic, recorded as a confusable pair - and its link and 310's to the old martial-training anchor now point at `../buildings.html#martial-training-grounds-and-dojo`. Cut (REMOVED comment): 070's quotation of the question on a one-per-100 ratio and its "There is none" (the finding, that the ratio is a calibration, is in the rendering section, the ratio's history in a comment), and the pointer sentences between the five old sections. Four notes of 070 were merged into 210's and 780's notes quoting the same passages (hanko-jawiki, dojo-jawiki, dojo-jawiki-2, edo-three-dojos-jawiki, edo-three-dojos-jawiki-2); the hagi-meirinkan-guide note's gloss on the page's misprint now keeps the kanji in a comment, to clear the prepass. The rendering section records as OPEN (a comment, not changed by this restyle) that castle_civic.py draws the state hall 60 x 36 ft in a 130 x 100 ft compound and the private dojo on 76 x 44 ft lots, against the rule's 124 x 35 ft and 44 x 24 ft; that `_dojo_hall`'s docstring calls the hall's head "the shrine alcove", against the kamidana finding; and that the StrikingPosts modal's "about 4.5 ft" post is a little over 1.3 m (~4 ft) on the source's figures - entry-drift should look at that modal. The glossary gained `tategi`; `program item` and `anchor culture`, used only by 070, are now used by the rendering section. Code comments in castle_civic.py and citybudget.py that named "Martial training is an urban institution" or "A dojo is a city institution" now name the rendering section.
