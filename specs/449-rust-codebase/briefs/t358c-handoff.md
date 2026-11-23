# Handoff - feature 449 T358c, session 1: write (2026-11-23)

- SECTION=0190 0082 registry-4950 glossary

C1 DONE - note `gmw-tianxia-yamen` (0190 findings notes and drawing notes) now joins its five passages with "; " (the record's dominant form, 2,386 notes); nothing quoted changed; the originals files needed no change (each passage keeps its own #1-#5 placeholder).
C2 DONE - registry `4950-tokushima-yashikigami` now says "a persimmon tree about 20 m east of the house" and "one persimmon about 20 m east of a homestead", from the archived PDF's 「屋敷の東方20ｍ位の柿の木」. (0218's drawing page and note already say "about 20 m east": no change.)
C5 DONE - the kotobank page does give period and place: the same World Encyclopedia passage says, just before the dimensions, 「近世には江戸の大八車と大坂のべか車が著名である。」. That sentence is now a second passage of note `kotobank-daihachiguruma-4` (both 0082 notes files, originals as `kotobank-daihachiguruma-4#2`), and the lines read "Edo's hand cart, the daihachiguruma, had a bed 8 shaku long and 2 shaku 5 sun wide (a sun being a tenth of a shaku), about 8 by 2.5 ft" (drawing page) and "Edo's hand cart had a bed about 8 by 2.5 ft." (findings page line 18, which carried the same wording on the same note). `docs/buildings.md`'s "the Edo hand cart's bed" still holds as a place attribution (the page ties the cart to Edo, archive text lines 158 and 187); not edited.
C6 NARROWED - `beka-guruma` added to `25040-beka cart.json`'s variants (`make glossary` rewrote `glossary-variants.txt` and `glossary.json`). The `sun` TERM is LEFT: the record's matcher (`research/site/assets/record.js` line 64, case-insensitive, per text node; `cased` only separates case) would wrap every English "sun" - about 214 lines of the record, e.g. "the afternoon sun", "the sun side", plus the map pop-ups that share the glossary - with "a tenth of a shaku". The definition does read on a public page (archived ja.wikipedia 尺貫法, registry `shakkanho-jawiki`: 「1 尺 = 10 寸」, 「寸≒ 30.30303 mm」), so the term can be added once the matcher can scope a variant (italic only, or an opt-in). Instead both 0082 pages now define it inline ("a sun being a tenth of a shaku"). The `make reserve` placeholder `28350-sun.json` was deleted; the prefix 28350 is free again. The same collision already exists for the term `go` (a tenth of a tsubo): it wraps the English word "go" today.

## Files

- research/questions/0190-notice-boards-kosatsuba.notes.html
- research/questions/0190-notice-boards-kosatsuba.drawing.notes.html
- research/sources/010-works-cited/4950-tokushima-yashikigami.html
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.html
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.notes.html
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.originals.html (written by `make record`)
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.html
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.notes.html
- research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.originals.html (written by `make record`)
- l7r/diagram/interactive/assets/glossary/25040-beka cart.json
- l7r/diagram/interactive/assets/glossary.json (written by `make glossary`)
- research/assets/glossary-variants.txt (written by `make glossary`)
- the sources-consulted ledger (three `make source-outcome` rows: kotobank-daihachiguruma cited, tokushima-yashikigami cited, ja.wikipedia 尺貫法 nothing-found for 0082, meaning nothing new cited)

## Open

- The checks owed (next session): quote-check, source-reader and translation-check on 0082's `kotobank-daihachiguruma-4` (new passage #2) and on the claim lines at 0082 findings line 18 and drawing line 10; quote-check on 0190 `gmw-tianxia-yamen` (join only); record-format on both 0082 pages; source-reader on registry 4950's two restated lines.
- `make record CHECK=1` builds cleanly; `make question-sizes` lists 2 questions over 20,000 bytes, neither 0082 nor 0190 (0009 at 20,044 among them, not this bundle's).
- The `sun` glossary term waits on a matcher change (record.js and the map's page.js, outside this brief's files): a way to keep a variant to italic text or to make it opt-in. The `go` term has the same false matches today.
## Session 2 (checks)
CHECKED quote-check 0082 (kotobank-daihachiguruma-4, both pages; cart-lane self-notes) - 3 READABLE 3 VERBATIM 3 SUPPORTS, 2 absence, 0 unfootnoted - nothing
CHECKED record-format 0082 - 0 VOCABULARY 0 SESSION NOTE 0 HISTORY, 16/16 words and 3/3 candidates ruled - nothing
CHECKED source-reader 0082 kotobank-daihachiguruma-4 (both pages) - 2 READ - nothing
CHECKED translation-check 0082.drawing kotobank-daihachiguruma-4 #2 - 1 FAITHFUL - nothing
CHECKED source-applicability registry 4950 tokushima-yashikigami - 1 APPLICABLE-WITH-LIMITS, limits HONEST - applied 4 EDITs (house -> homestead; "overwhelmingly east and southeast" -> "most often east or southeast (eight of fifteen houses)" twice, from the agent's count of the table; citation line now names 阿波学会紀要 and the title 美郷村の屋敷神について, as the PDF masthead and What it is say)
CHECKED quote-check 0190 gmw-tianxia-yamen round 1 - 5 READABLE 5 VERBATIM 5 SUPPORTS, 2 absence - nothing; round 2 the same - nothing
CHECKED source-reader 0190 gmw-tianxia-yamen round 1 - 8 READ, 1 dropped hedge - applied by hand: the question-page claim now reads "carried most of the emperor's edicts, which the county's inhabitants could receive in front of the office every month outside the slack farming season at the turn of the year", and passage #2 (both notes files and both originals) now starts at 除了年头岁末农闲时外 so the restored limit is quoted; round 2 - 4 READ - nothing
CHECKED record-format 0190 round 1 and round 2 - 0 VOCABULARY 0 SESSION NOTE 0 HISTORY, 80/80 words - nothing
CHECKED translation-check 0190.drawing gmw-tianxia-yamen #2 (widened) - 1 FAITHFUL - nothing
CHECKED modal-triage 0082 moved (24 units) - 9 TOUCHES (cart-yard, side-gate, road), 15 untouched; 0190 moved (18 units) - 6 TOUCHES (choice/kosatsuba_siting--frontage, hamlet/notice-board), 12 untouched
CHANGED research/sources/010-works-cited/4950-tokushima-yashikigami.html
CHANGED research/questions/0190-notice-boards-kosatsuba.html
CHANGED research/questions/0190-notice-boards-kosatsuba.notes.html
CHANGED research/questions/0190-notice-boards-kosatsuba.drawing.notes.html
CHANGED research/questions/0190-notice-boards-kosatsuba.originals.html
CHANGED research/questions/0190-notice-boards-kosatsuba.drawing.originals.html
OPEN pop-ups the triage names (another builder's, not checked here): sheet/cart-yard and sheet/side-gate (modal-accuracy, modal-gaps, modal-references, modal-depiction), sheet/road (modal-depiction) from 0082; choice/kosatsuba_siting--frontage and hamlet/notice-board (modal-accuracy, modal-gaps, modal-references) from 0190
OPEN source-reader on 0190, minor and not edited: the source's 大多 covers the edicts "all the people needed to know", so "most of the edicts meant for the people" would match it more exactly than "most of the emperor's edicts"
OPEN the sun glossary term still waits on the matcher change (session 1's note stands)
make record CHECK=1, make record, make glossary, make question-sizes all clean (2 questions over 20,000 bytes, neither 0082 nor 0190); make record-owed names nothing of these units but the pop-ups above; claims not released
CHECKED escalation-check on the closing summary - cut the 大多 OPEN as a fix to apply: the 0190 claim now reads "most of the emperor's edicts meant for all the empire's subjects" (source-reader round 2's scope point, applied; the OPEN line above on it is settled)
CHECKED record-format 0190 round 3 - 0 VOCABULARY 0 SESSION NOTE 0 HISTORY - nothing; record-owed then named no non-pop-up unit of 0190 (quote-check and source-reader not owed by the narrowing)
