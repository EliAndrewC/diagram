# Handoff - feature 449 T278, T279, session 1: write

- SECTION=0116
- SECTION=0090

- T278.1 DONE - 0116's drawing page, "Ochiba's jail cell and barracks are one guard building.": "It stands in the compound's southeast corner, below the granary at the head of the office court's east column, with a 16 ft loading apron between them." Heading kept; an HTML comment records the 2026-11-22 rect measurements (granary 820-970 x 490-568 px beside the hall's east end 420-780 x 478-562; guard building 894-966 x 616-716; 48 px apron).
- T279.1 DONE - 0090's drawing page: heading now "At that scale an office hall runs about 110 to 127 ft long."; text "The generated county example's office hall is 127 by 38 ft, and the hearing court before it is 80 by 26 ft. The hand-drawn sheets' halls are 28 ft deep: Hayakawa's is 113 by 28 ft, Ochiba's 120 by 28 ft and Ubame's 110 by 28 ft." then the cell and wall sentence unchanged; the comment's measurement updated (county example 127 x 38 and the three hand halls, 2026-11-22). Line 26 now reads "Hayakawa's office hall 85 ft long instead of 113."

## Files

- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html
- specs/449-rust-codebase/briefs/t278-handoff.md

## Open

- Nothing for these items. `make record CHECK=1`, `make record`, `make glossary` all clean; `make question-sizes` lists two questions over 20,000 bytes (0009 and one other), neither 0090 nor 0116 and neither touched here. The record checks (record-owed) are left for the next session, as the brief asks.
## Checks (session 2, 2026-11-22)
- CHECKED quote-check 0116.drawing (unfootnoted) - 0 notes in change, 0 unfootnoted owed - nothing
- CHECKED record-format 0116 - 8 of 8 ruled, 0/0/0 in change - nothing
- CHECKED quote-check 0090.drawing (takayama-jinya-city-10, unfootnoted) round 1 - 1 READABLE, 1 VERBATIM, 1 SUPPORTS, 0 owed - nothing
- CHECKED record-format 0090 round 1 - 30 of 30 ruled, 1 inconsistency ('both of our drawn compounds' vs Ubame named next) - applied by hand: 'all three ... and Ubame at 290 by 200 ft' (walls x 200..1070, y 150..750 px), quote-check fuchu-joge-pamphlet-9 settled FIXED_BY
- CHECKED record-format 0090 round 2 - 30 of 30 ruled, 1 CLARITY - applied (make apply-edits): 'the same plan' -> 'Hayakawa's plan'
- CHECKED quote-check 0090.drawing round 2 (takayama-jinya-city-10, fuchu-joge-pamphlet-9) - 2 READABLE, 2 VERBATIM, 2 SUPPORTS, 0 owed - nothing
- CHECKED modal-triage (pages 0090/0116 moved) - two rounds; touched: sheet/barracks, cart-yard, granary, office-hall, outer-court, rear-yard, residence, stables, storehouse; the rest answered untouched
- CHANGED research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html
- OPEN modal-depiction on the 9 touched pop-ups (sheet/barracks, cart-yard, granary, office-hall, outer-court, rear-yard, residence, stables, storehouse) - triage names them; the brief reports them, not checks them (pop-ups are the orchestrator's)
- OPEN outside the change, 0116: japan-heritage-takayama-onkura NOT-READABLE on both pages (re-point or absence note); fuchu-joge-jinya fn-8 2 NOT-CHECKED quotations; takayama-jinya-gifu note on both pages carries a SESSION NOTE (cache-match / text-layer statement, move into a comment)
- OPEN outside the change, 0090: 'the divider' (engine word) in 'The generated plans open the middle gate beside the office hall'; fuchu-joge-pamphlet-6 'the Meiji 2 drawing' lacks 1869; fuchu-joge-pamphlet-9 originals use half-width punctuation that a re-run may read DIFFERS
- OPEN not mine, left: record-owed still names 0031, 0072 and sheet/armory, gatehouse, main-gate, servants--quarters units (other builders')
- make record CHECK=1, make record, make glossary clean; make record-owed names no 0090/0116 record check; claims 0090 0116 released
