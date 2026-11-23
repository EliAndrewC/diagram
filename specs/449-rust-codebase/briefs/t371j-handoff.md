# Handoff - feature 449 T371j, session 1 (write)

- SECTION=0090 0113

J1 DONE - 0090's block "Did Japanese offices put the office in front and the residence behind?" now answers "At Takayama the residence stood at the back of the office": the jin'ya's guide (new note `takayama-jinya-viewing-guide` in 0090, the 役宅 sentence of item 04) says the intendant worked in the residence at the back of the office; the city page (`takayama-jinya-city-2`, extended with its next sentence, 郡代役宅復元工事 1992-1995) places that residence on the lot immediately to the west; the restored residence follows a plan of 1830 (`takayama-jinya-jawiki-2`), so the arrangement is of about 1830; neither page says which way the office faces, so the "beside the office rather than behind it" reading is dropped; Takayama is named as the one case read with the residence at the back, and the Edo town magistracy's east-west division is pointed to at 0113. The two sources name the same residence (the city ties its dig to the restored residence the guide walks through), so no "different buildings" wording. 0113's block "Where did the magistrate's office stand against the residence?" gains one pointer sentence: where that residence stood on the site, and that no page gives the office's facing, is at 0090 (no new note on 0113). 0090's drawing line 17: the front-and-rear order in a Japanese compound now follows Takayama, the one Japanese office read with its residence at the back (guide cited), "One case is all it rests on", Edo pointed to at 0113; its `Evidence:` comment moves the item from deviation to accurate, ATTESTED ONLY FOR Takayama. The drawing page no longer cites `takayama-jinya-city-2`, so that note and its original were removed from the drawing notes/originals.

Sources: read on their archived copies (city page 58/581ecfc0c54f/20261003T043745Z line 73; guide PDF text 47/4794c7ca22eb/20261123T013345Z lines 80-81). Searched for the office's facing in the archived ja/en Wikipedia, jinya.gifu.jp highlight (ja, en), jinya.gifu.jp/en, mapple, the Gifu prefecture PDF: none states it. Ledger: cited outcomes for the city page, the guide and ja Wikipedia (Q 0090; ja Wikipedia was first recorded nothing-found for the facing, then cited for the 1830 plan); nothing-found for the six others. The ledger commands appended to `research/source-attempts.jsonl`. No new registry keys.

## Files

- research/questions/0090-magistrates-compounds-jinya-and-yamen.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.notes.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.originals.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html (already modified by another builder before this session; my change is line 17 and the Evidence comment)
- research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.notes.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.originals.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html (already modified before this session; my change is the end of the "Where did the magistrate's office stand" block)
- specs/449-rust-codebase/briefs/t371j-handoff.md
- research/source-attempts.jsonl (appended by `make source-outcome`; other builders' lines are in it too)

## Left open

- Which way the Takayama office faces: no readable source we hold says; the record now says so plainly rather than guessing.
- Owed checks (for the next session): 0090 and 0113 visible words changed (record-format, quote-check on `takayama-jinya-viewing-guide` and `takayama-jinya-city-2` in 0090, translation-check on their new originals); the office-hall pop-up and any pop-up citing 0090 may be re-owed by `make record-owed`. Any engine `Research:` claim citing 0090's front-and-rear deviation may now be DRIFTED (claim wording only; the drawing is unchanged) - not touched here, per the brief.
- Process slip: the first note edits were made with a short python script rather than Edit; the result was checked by `make record CHECK=1` (clean).
## Session 2 (checks), 2026-11-23
CHECKED quote-check 0090 (city-2, jawiki-2, viewing-guide; drawing machi-bugyo-jawiki-2, neixiang-yamen-zhwiki-4, viewing-guide) - 6 READABLE, 6 VERBATIM, 6 SUPPORTS, 0 in the change, 1 outside - nothing
CHECKED record-format 0090 - 30 of 30 words, 1 VOCABULARY - applied ("a detention branch" -> "a branch of a modern detention center")
CHECKED record-format 0113 - 26 of 26 words, 6 of 6 candidates, 0 VOCABULARY, 1 reading fix - applied (pointer sentence "is at" -> "are at")
CHECKED translation-check 0090#takayama-jinya-city-2, 0090.drawing#takayama-jinya-viewing-guide - 2 FAITHFUL - nothing
CHECKED source-reader 0090#takayama-jinya-city-2 - 2 claims READ (west lot = 役宅, dig 1991; restoration 1992-1995); page gives no facing - nothing
CHECKED source-reader 0090 and 0090.drawing #takayama-jinya-viewing-guide - 2 claims READ (item 04, 御役所の奥にある役宅); guide gives no facing - nothing
CHECKED modal-triage (39 page-moved pop-up units) - 23 TOUCHES sent on to their checks, 16 untouched - recorded with make modal-triaged
CHANGED research/questions/0090-magistrates-compounds-jinya-and-yamen.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html
OPEN pop-ups (not mine to check here): the triage sent on modal-depiction for sheet/court-divider, door, family-quarters, inner-court, nakamon, office-hall, outer-court, residence (residence's Depiction still says "beside"); modal-research (accuracy/gaps/references) for sheet/court-divider, day-office, family-quarters, inner-court, nakamon; also still owed and other builders': modal-depiction sheet/official-study, sheet/writing-rooms
OPEN OUTSIDE THE CHANGE (quote-check): 0090.notes takayama-jinya-jawiki-2 joins its two quoted passages with " and " instead of "; " (JOINED-WRONG); the note's words predate this work
OPEN source-reader aside: the viewing-guide note's comment cites lines 80-81 of the archived text; the bundle's saved text has the sentence at 81-82 (a different file; not changed)
OPEN claims not released (orchestrator holds them); no commit made, per the brief
