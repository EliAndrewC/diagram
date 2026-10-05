# Research - feature 319

## R1 - the checks proved on the old text (T07, plan D7), 2026-10-03

The farmhouse and garden modals as they stood, converted mechanically into the About form (old What/Why as About, the garden's
"This is a guess - " lead kept, the old Note as one guess bullet), bundled from a scratch root
(`scripts/_modal_bundle.py --root`), each check dispatched ad hoc on Opus with its contract (the defined agent types load only
at session start). Every required finding fired:

| run | counts | the required finding | tokens |
|---|---|---|---|
| modal-form, farmhouse | 14 (13 FIX, 1 NOTE) | M5 q2 materials, walls, floor, doors; M5 q3 residents - both FIX | 59,325 |
| modal-form, garden | 11 (9 FIX, 2 NOTE) | M11 the guess-led opening - FIX 1 | 57,683 |
| modal-research, farmhouse | ACCURACY 10, REFERENCES 3, GAPS 6 | G1: 0004 "averages five, across two or three generations" | 117,785 |
| modal-research, garden | ACCURACY 6, REFERENCES 1, GAPS 2 | A1: the record calls the bed's existence accurate; G1: 0109's measured 100 m2 plot | 88,468 |

What the runs taught the tooling: the first research bundle was 380 KB (each Entry page's notes and the top ten candidates
inlined); notes dropped (accuracy is judged against what a page tells its reader - the footnotes are quote-check's) and the
candidates made files to open on demand: 140 KB. 0004 ranked 43rd of 156 farmhouse candidates (it meets 0029 on `households`
alone, one term hit) and was still found - the ranking orders, never cuts (the plan review's D5 ruling).

## R2 - the farmhouse's standard questions in the record (T08 input), 2026-10-03

A sonnet reader over 0029, 0028, 0004, 0030, 0048 and a grep of the questions: purpose, size, household and roof answered; the
walls and whether the house closed silent. The research pass (sonnet, archive first) found: the Nipponica "minka" entry's
east-west split of shinkabe and okabe outer walls; the Miyoshi museum's Ikegami farmhouse - the big door shut and barred at
night and in wind and rain, storm shutters and paper screens on its veranda; Morse (1886) on bark-slab walls of poorer houses
in the south and amado closing a house at night. Written to the record by the F1 page sessions (`briefs/f1-*.md`).
