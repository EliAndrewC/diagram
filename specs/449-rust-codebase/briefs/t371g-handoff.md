# Handoff - feature 449 T371g (0097, 0096), session 1: write (cleanup)

- SECTION=0097 0096

## Items

- G1 DONE - the absence note `staff-rowhouses-and-barracks-nagaya` no longer says what the pages count; it now reads "None of the pages we read says how many unmarried men shared a dwelling." Its twin in the drawing page's notes (`how-our-maps-draw-staff-rowhouses-and-barracks-nagaya`) carried the same sentence and got the same fix. (The findings still cite `shibata-ashigaru-nagaya-71` for the households count.)
- G1 DONE - "Inside, a warriors' rowhouse was divided into dwellings, though the servants below the foot soldiers shared large rooms." now cites `mitamura-nagaya-tcpip-91` (partitioned house by house) on its first clause and `kotobank-chugen` (lived communally in large rooms) on its second. Both notes were read.
- G1 DONE - I restated the China lead so that each clause claims only what its note carries: "A Beijing courtyard house lodged its servants in the south range, one of the ranges of rooms around its courtyard,[daozuofang-91] and its family's north range shows the other form, several rooms behind one door.[qianggen-siheyuan-layout]". The old wording implied that the servants' rooms were behind one door, which absence note -6 says no page states. I also cut "not in a rowhouse", because no note carries it.
- G1 LEFT - the four `kochi-hantei-jstage` lines that `quote-verbatim` flagged (fn-25 to fn-28, notes -3, the base note, -2 and -4) are verbatim:
  - Two of them, -3 and -4, are exact substrings of the archived text layer (2026-10-02) once its left column is joined.
  - The base note and -2 differ from that layer only by its OCR. The layer reads ①1⑧, ⑨j⑭ and 土聞 for the page's ①～⑧, ⑨～⑭ and 土間. It also mixes figure noise ("，...L..") into 一室.
  - I checked these against the page image, p.48 (PDF page 19 of the archived served.pdf).
  - The tool missed them because the paper's two-column layout interleaves the columns in the text layer. The page has not changed, and I edited nothing.
- G2 LEFT - the "Yuki domain" / "Yūki domain" spelling: in the working tree, the note `boso-jinya-chiba-kiyo` (its quote and its gloss) and the body both already read "Yūki domain". No "Yuki domain" remains in any 0096 file, so there was nothing to make one.
- G2 DONE - the registry write-up of `boso-jinya-chiba-kiyo` now states the Iwaito limit in the source's own words, read from the PDF's p.92 (PDF page 47, `pdftotext`):
  - The survey infers both ends of the dates. The jin'ya "was presumably built" after the reassignment of 1853 (the 1853 is in the source), and "the jin'ya too, it seems, was abolished" when the land became shogunate land in Bunkyu 1. The bracketed [1861] is this project's conversion of Bunkyu 1.
  - Both passages are quoted with their originals. The outcome is recorded with `make source-outcome` (`cited:boso-jinya-chiba-kiyo`, Q 0096). The read of the archived kochi text is also recorded (`cited:kochi-hantei-jstage`, Q 0097).

## Files

- research/questions/0097-staff-rowhouses-and-barracks-nagaya.html
- research/questions/0097-staff-rowhouses-and-barracks-nagaya.notes.html
- research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.notes.html
- research/sources/010-works-cited/37350-boso-jinya-chiba-kiyo.html
- specs/449-rust-codebase/briefs/t371g-handoff.md (this file)
- `make record` also moved an inline original out of `research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.notes.html` into its `.originals.html`. That was another session's uncommitted 0059 work, which `make record CHECK=1` refused on. It was the build's own move, and I made no edit of my own there.

## Registry keys reserved

- none

## Sizes after

- 0097 findings: 19,505 bytes (cap for this brief 19,800)
- 0096 findings: 14,403 bytes (unchanged)

## Builds

- `make record CHECK=1`: clean after `make record` (4354 pages).
- `make glossary`: assembled.
- `make question-sizes`: 0 over.
- `make record` did not refuse on 0107's `mlit-kaga-ashigaru`.

## Open

- The record checks are owed for the next session:
  - 0097: quote-check on the new footnotes in the two lead paragraphs, and record-format on the changed absence notes and the lead.
  - 37350: source-applicability on the changed write-up.
- I ran no check here.
## Check session (t371g-checks)
CHECKED quote-check 0097 (daozuofang-91 kotobank-chugen mitamura-nagaya-tcpip-91 qianggen-siheyuan-layout staff-rowhouses-and-barracks-nagaya, drawing how-our-maps-draw-staff-rowhouses-and-barracks-nagaya, unfootnoted) round 1 - READABLE 4, VERBATIM 4, SUPPORTS 2, PARTIAL 2, ABSENCE 2, unfootnoted 0 - applied by hand: added passages daozuofang-91 #2-#4 (south range, southernmost row, Beijing) and qianggen-siheyuan-layout #2 (hall = family) and #3 (page title), originals copied verbatim from the 2026-10-02 archive captures
CHECKED record-format 0097 round 1 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY, 2 READER - applied its 2 EDITs ("usually" in both unmarried-men absence notes) via make apply-edits; 1 finding OPEN (below)
CHECKED source-applicability boso-jinya-chiba-kiyo (37350) - APPLICABLE-WITH-LIMITS 1, limits MISSING one - applied its EDIT (the Iwaito jin'ya's existence is itself an inference: 岩糸陣屋があったらしい, jail and rowhouses from the Maruyama town history)
CHECKED quote-check 0097 (daozuofang-91 qianggen-siheyuan-layout) round 2 - READABLE 2, VERBATIM 2, SUPPORTS 2 - nothing
CHECKED record-format 0097 round 2 - 0/0/0, the round-1 county-barracks finding repeated (EDIT none) - nothing
CHECKED translation-check 0097 (daozuofang-91 #2-#4, qianggen-siheyuan-layout #2-#3) - FAITHFUL 5 - nothing
CHECKED source-reader 0097#daozuofang-91 - READ 6 - nothing
CHECKED source-reader 0097#qianggen-siheyuan-layout - READ 3 - nothing
CHECKED modal-triage (whole tree, 174 units incl. other builders' pages 0009 0059 0090 0099 0103 0107 0113) - 102 sent on (TOUCHES), the rest triage: untouched - recorded with make modal-triaged
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.notes.html
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.drawing.notes.html
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.originals.html
CHANGED research/sources/010-works-cited/37350-boso-jinya-chiba-kiyo.html
CHANGED research/site/ (make record build output only)
OPEN record-format 0097 READER (rounds 1-2, EDIT none; a model choice, drawing page blocks not changed by the write session): the county plan's barracks is four dwellings in 48 ft at most three men each (12 men) against a staff of about fifteen; also the unchanged block 'As long as the bays its staff of about fifteen men needs' contradicts the fixed 48 ft. Needs five dwellings/60 ft, four men a dwelling, or where the other three lodge - pool/ county plan or the model, not this session's
OPEN pop-ups the triage sent on for 0096/0097 (not checked here, pop-ups are another builder's): modal-accuracy/gaps/references sheet/cell, sheet/door, sheet/hearing-court, sheet/karo-s-house, sheet/servants--quarters; modal-depiction sheet/cell, sheet/door, sheet/hearing-court
OPEN outside the change (source-reader): registry 4630-daozuofang calls the article 'a four-sentence encyclopedia stub'; the saved text has five body sentences
OPEN quote-verbatim 0097: fn-25..28 kochi-hantei-jstage NOT-CHECKED (archived text mismatch, the write session read them verbatim) and fn-10 sakai-bugyosho-kachu-nagaya-takaya NOT-CHECKED (PDF, no text layer); not owed this session
Builds: make record CHECK=1 clean (4354 pages), make record, make glossary (2829 terms), make question-sizes 0 over; make record-owed names nothing of these units but the pop-ups above. Claims not released.
CORRECTION to the OPEN pop-ups line: the triage reply named only sheet/door, sheet/karo-s-house and sheet/servants--quarters at 0097.html and sheet/hearing-court at 0096.drawing.html as TOUCHES; it cleared sheet/armory, sheet/gatehouse, sheet/granary and sheet/main-gate for 0097. sheet/cell is not in the triage reply: its modal-accuracy/gaps/references (0096.html) and modal-depiction (0096.drawing.html) units are still owed in their own right (sheet/cell also sits in the batched modal-research and modal-depiction lists) - another builder's
CORRECTION to round labels: this session's round 1 and round 2 are the 0097 checks' rounds 7 and 8. The record-format county-barracks finding has now repeated twice with no EDIT, so the next round on it goes to the round-arbiter (make arbiter-bundle)
CHANGED research/source-attempts.jsonl (in part, written by the check agents' fetches and make record-checked/source-outcome ledgers; other builders' rows are in the same uncommitted diff)
CHANGED l7r/diagram/interactive/assets/glossary.json (rewritten by make glossary; no glossary term of mine changed)
NOT MINE though newer than this session's start: 0059 notes/originals (make record's originals move or another builder), 0099, 0113, pool/, rust/, 4280-banfang-zhwiki, other handoffs and tasks.md - other builders' concurrent work
