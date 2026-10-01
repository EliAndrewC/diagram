# 292 sweep - buildings G07 handoff (session 1: write)

## The hearing court (shirasu)

- SECTION=buildings/the-hearing-court-shirasu
- RENDERING=rendering/buildings/how-our-maps-draw-the-hearing-court-shirasu
- OLD=research/buildings/090-the-courtroom-is-a-room-of-the-office-hall-not-a-freestanding-stage.html research/buildings/440-who-sat-where-at-a-hearing-and-on-what.html research/buildings/450-was-the-hearing-court-open-white-sand-or-roofed.html
- MODALS=ClerksSeats DayOffice HearingCourt KneelingPositions LordsQuarters MagistratesDais OfficeHall OfficialStudy
- BASE=9c5659018

No section was held by another feature; all three folded. Nothing cut but the three `Sources:` rosters (every key
cited by a footnote) and the plan paragraphs, moved to the rendering section; the duplicate notes
takayama-jinya-jawiki-7 and takayama-jinya-city-15 were merged into takayama-jinya-jawiki-5 and takayama-jinya-city-5
(city-15's second passage is now city-5#2). The note glosses' unglossed encyclopedia names (マイペディア, 世界大百科事典)
were rendered in English ("MyPedia", "Heibonsha's World Encyclopedia") for the kanji rule. The rendering section adds,
from the engine and the modals rather than the folded prose, the roofed court's outline and 12 ft post bay
(compound_model.py), the mats' sizes (compound_parts.py _mats) and the clerks' seats set beside the dais (the
ClerksSeats and MagistratesDais modals); each is labeled a GUESS or a deviation, and entry-drift should confirm the
modals against it. Code comments that named buildings 440/450 now name the new section (compound_model.py,
compound_parts.py, compound.py, labels/hand_sheet.py); no inbound fixture entry existed for these classes. The
confusables file's line 22 names the old 090 title; a replacement pair was appended. `make quick` (not part of this
brief) fails on two mizuguchi pool-map tests (notes census, brook axis) unrelated to this change;
`make test-file FILE=tests/interactive` is green.
