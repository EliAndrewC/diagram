# Feature 292 sweep - buildings G04 handoff (session 1: write)

## The main gate and its gatekeepers (nagaya-mon)

- SECTION=buildings/the-main-gate-and-its-gatekeepers-nagaya-mon
- RENDERING=rendering/buildings/how-our-maps-draw-the-main-gate-and-gatehouse
- OLD=research/contents.json#compounds research/contents.json#compounds
- MODALS=MainGate Gatehouse
- BASE=5d99461aa

No section was left out, since no claim held 0093 or 420 in progress. The only cuts were the two `Sources:` rosters. Both old
sections quoted the Kaibara gate range's length, depth and rooms, so 480's `tamba-kashiwara-jinya-2` is merged into 420's
`tamba-kashiwara-jinya`, and its second passage (the jin'ya's front gate of Shotoku 4) became that note's third, with
`data-orig` renamed `tamba-kashiwara-jinya#3`. The four absence notes are in the new form. Their keys were not
section ids, so they were not re-keyed. `takayama-jinya-city-14`'s gloss lost the bare `熨斗葺` for the kanji prepass,
in both notes files. The "What this means for a plan" paragraphs (the gate's forms and the gatekeepers' two places as knobs, the
yamen gate's 18-24 ft GUESS, the 2-ken depth and the 40 ft freestanding gatehouse GUESS) moved to the rendering section.
The 2-ken depth is also stated in the research section as a finding. Links were re-aimed in 0090 (a link and a
comment), 0092 (a comment), 0092 (two links) and cities/government 290. That last one was a
pending comment-link, now a live link to the new section. The `compound_model.py` code comment was re-aimed too. The
MainGate `Entry:` also still named religion-and-death's 'How large are the gates, walls and funerary features drawn?',
which G03 folded, so it now names G03's rendering title 'How our maps draw compound walls (neribei and tsuijibei)' in
its place. Neither class is in `classes_before_189.json`. Both modals' prose is unchanged and owes an entry-drift check.
