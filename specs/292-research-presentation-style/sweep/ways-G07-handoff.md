# 292 sweep ways G07 - handoff (session 1: write)

## Road bridges over rivers and canals (hashi)

- SECTION=ways/road-bridges-over-rivers-and-canals-hashi
- RENDERING=rendering/ways/how-our-maps-place-and-draw-road-bridges-hashi
- OLD=research/ways/ research/ways/ research/ways/
- MODALS=

## Ferries and fords (watashi)

- SECTION=ways/ferries-and-fords-watashi
- RENDERING=rendering/ways/how-our-maps-draw-ferries-and-fords-watashi
- OLD=research/ways/
- MODALS=

- BASE=14c62b4fe

Road bridges: no section was left out (269's X1C check on ways 050 is done and landed; 280's Y1 on ways 010 is done), and nothing was cut beyond the three `Sources:` rosters, 200's pointer sentences and 050's "Yes." with its GM quotation, which went to a comment in the rendering section. The four absence notes were converted and renamed to the section's id (-, -2, -3, -4); 050's ring-road grounds note moved to the rendering section as `-5`, and the rendering section gained one new grounds note, `-6` ("measured on our own maps"), for 050's deck measurement, which the old section cited only in its roster. The rendering title is the brief's "How our maps place and draw bridges" with "road" and "(hashi)" added so it mirrors the research title. The confusable pair already in `confusables.md` names the old title "What bridges does a town put over its river"; a new line with the new title was appended, and the old line wants deleting when the list is built. Two tooling tests named the deleted ways 010 fragment and were re-aimed: `test_check_bundle.py` uses ways 200 (and ways 140 for the two quote-check cases, since ways 200's notes now exceed the 12,000-byte batch size); `test_record_prepass_and_size_table.py` reads ways 200 and asserts on three abutment words, since "girder" and "stringers" are no longer rare and "obliquity" went to the rendering section. `fragments.py`'s docstring example names the new file. No modal, fixture or other fragment linked the old anchors. Ferries and fords: the brief said there was no rendering section, but ways 140 carried a map rule ("What this means for the map" and its spec), so I wrote `rendering/ways/140-how-our-maps-draw-ferries-and-fords-watashi` rather than leave the rule in the research section. A comment there notes that no ferry or ford placer was found in `l7r/`. The village ferry's "two or three boats" stays a labeled GUESS there. A confusable pair against "Wharves and landings" was appended.
