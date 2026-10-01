# 292 sweep fields A01 - handoff

- SECTION=fields/where-a-farming-hamlet-grew-its-coarse-grain
- RENDERING=rendering/fields/how-our-maps-draw-dry-fields-and-their-crops-hatake
- OLD=research/contents.json#fields research/contents.json#fields research/contents.json#fields
- MODALS=
- ALSO CHANGED: fields/dry-fields-and-their-crops-hatake (one pointer sentence at the end of its alluvial-fan bullet); rendering/fields/how-our-maps-show-the-paddy-through-the-rice-year (the winter-crop bullet, feature 291's change carried)
- BASE=be345c9f9

Fields 165 was folded into 0006 'Dry fields and their crops (hatake)' as the brief asked, but that put 160 at 24,459 bytes against the 20,000 cap (scripts/check-question-size.py), so, as the G05 check did for the paddy's rows (0012), 165 stands as its own topic at the same prefix, 'Where a farming hamlet grew its coarse grain', with 160 left as checked except for a sentence pointing to it; the checks owe the new section a full pass (record-style, quote-check, record-format) and 160 only that sentence. Its map rules went into the existing rendering section of 0006 as the brief asked. The only claim cut was 165's house-plot sentence, already said in 160's house-plot bullet; its senjochi-kotobank-3 and shizen-teibo-jawiki-3 are cited as 160's senjochi-kotobank and shizen-teibo-jawiki (same passages). One gloss changed: kokumori-jawiki-2's '(a to, 斗, is ...)' lost its unglossed kanji, in both notes files. Feature 291's winter-crop sentence is carried into the rendering section of 0009; its lead line no longer says the knob is 'for the seasonal maps', since the roll now moves the dry band on today's maps. The code comments in grain.py also re-aim the stale fields/300 references to 0009. No other section was claimed IN PROGRESS by another feature.
