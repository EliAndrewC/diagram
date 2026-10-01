# 292 sweep - buildings G11 handoff (session 1: write)

## The compound's own shrine (yashikigami)

- SECTION=buildings/the-compounds-own-shrine-yashikigami
- RENDERING=rendering/buildings/how-our-maps-draw-the-compounds-shrine
- OLD=research/buildings/ research/buildings/
- MODALS=CompoundShrine ShrineAltar CompoundGarden
- BASE=1c31f6885

No other feature held 030 or 550 (a claims check on 2026-09-30), so nothing was left out of the fold. What changed besides the two folded sections:

- The shrine rule of buildings 510 (a modest shrine down to the smallest post, Inari by default) moved out of 'How our maps draw a magistrate's compound (jin'ya and yamen)' into the new rendering section. Its three notes (fuchu-joge-pamphlet-5, fuchu-joge-pamphlet-6, henan-neixiang-2) went with it and were taken out of that section's notes and originals, so that section changed (its feature comment, Grounds and Evidence too).
- The silence of the Joge excavation is copied from 010's joge-shrines-absence as the-compounds-own-shrine-yashikigami. 010 keeps its own account of the post.
- Nothing was cut except the two Sources: rosters (every key they named is footnoted), 550's pointer to 030 (the two are merged now), and the map rules, which moved to rendering. The REMOVED comment lists them.
- The two absence notes are converted to the new form.
- The fixture classes_before_189.json holds no compound kinds, so no fixture entry changed.
- Things the check should look at:
  - The rendering bullet "Ochiba's shrine hall has two altars" states the setting's priest-magistrate from 030's own sentence, with no canon lookup.
  - 030's "the rule does not depend on the count" is now the rendering bullet "The rule is that a compound has a shrine, not how many".
- Process note: the clone-sync hook's automatic sync-in started a merge of origin/main on the first Write (the clone had diverged: 200 local commits against 99 on origin) and left 38 conflicted paths. Committing in that state would have made a broken merge commit, so the session ran `git merge --abort`, which put the clone back at BASE with its edits intact. It did not run scripts/sync-with-main.sh. The clone is still behind main, so whoever drives the sweep must bring it up to date.
