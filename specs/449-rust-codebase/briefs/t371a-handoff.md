# Handoff - feature 449 T371 group a, session 1: write

- SECTION=0104 0123 0090 0009

- A1 DONE - 0104's drawing page, the door bullet: the county magistracy example draws the porch in its hall's own fill, about 12 by 9 ft (the one shikidai found measured), its door block 6 ft wide and about 1.3 ft deep; Ochiba's hand sheet draws a smaller porch, about 10 by 6 ft, in a fill darker than its hall's, its door block about 5 ft wide - the size a GUESS, the darker fill a map drawing convention; Hayakawa's and Ubame's hand sheets "and another, generated plan" (ochiba-roundtrip-test, named only in the comment, as 0123 does) take the no-genkan form and draw no porch (confirmed in each plan's notes: Hayakawa and Ubame "NO genkan" roji form, the round-trip "the roji form's bare door, no genkan porch"). The door-glyph convention sentence and its note kept. Evidence comment (line 4) gains the measurement (2026-11-23, SVG rects by data-kind="genkan" at 3 px to the foot) and the guess / convention labels for Ochiba's porch; the Grounds comment names no size and was left as it was.
- A2 DONE - 0123's drawing page: the county seat's store is "about 50 by 26 ft"; the comment beside it records the measurement (2026-11-23, 150 x 78 px at 3 px to the foot; 50 x 36 until 449 T364). The bullet's closing comment, which still gave the granary as 50 x 36 and the hall as 127 x 38, restated to 50 x 26 and 118.5 x 38.
- A3 DONE - 0090's drawing page, the hall bullet: "an office hall runs about 110 to 119 ft long"; the county example's hall about 118.5 by 38 ft, the court 80 by 26 ft; Hayakawa about 113 by 28, Ochiba 112 by 28, Ubame 110 by 28, "another generated plan" 112 by 28 (ochiba-roundtrip-test, named in the comment only); a cell 12 by 10 ft on the three hand sheets, 10 by 12 on the county example, 18 by 15 on that other generated plan (link to 0096's drawing page kept). Its comment carries the 2026-11-23 measurement and method; its stale `b("cell", ... 12.0, 10.0)` code reference cut. Grep of all 0090 files for `127` and `120 by 28` found no other line.
- A4 DONE - 0009 now 19,704 bytes (was 20,044). Cuts, no finding, footnote, figure or label dropped: the bullet on a hamlet settling its year's transplanting schedule in advance no longer repeats the survey's date and place from the paragraph above it; "the transplanting period was long and not seldom exceeded" -> "transplanting not seldom exceeded"; the Qimin Yaoshu bullet's restatement of the calendar's three parts (already in the opening paragraph) cut to "That is the shape of today's calendar."; the pre-modern-depth bullet's "So every depth above is modern extension guidance." (restates the opening paragraph and the bullet's own "None was found") cut; the drain-week bullet's body tightened to "It varies by region, ... and is not an Edo figure."; the wet-paddy bullet's body no longer repeats its heading ("Barley is weak to damp."); the nimosaku bullet's "then the water was let off in winter and it was worked" -> "then drained in winter and worked".

## Files

- research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.html
- research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html
- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
- specs/449-rust-codebase/briefs/t371a-handoff.md

## Searches

None (no web or archive search: every change restates our own sheets, read-only from pool/magistracies/*/ .svg, .notes.md and .compound.json).

## Open

- `make record CHECK=1`, `make record`, `make glossary` clean; `make question-sizes` lists only 0059 (20,065, the other brief's question, not touched).
- The genkan-door-glyph-convention note in 0104's drawing.notes.html has a session comment naming "the porch is layout::GENKAN, 12 x 9 ft" (the generator's porch, true of the county example); left as it is - it describes the code, not every plan.
- 0104's new Ochiba sentence labels its porch size a GUESS with no footnote of its own; quote-check may list it as an unfootnoted assertion (it is our own drawing choice; a `measured on our own maps` / guess note could be added if the check asks).
- Record checks not run, as the brief says; the next session runs them.
## Checks (session 2, 2026-11-23)
CHECKED quote-check 0009 (8 notes) - 7 READABLE, 7 VERBATIM, 6 SUPPORTS, 1 PARTIAL (obata-1977-taue-3: heading "often"), 1 UNLINKED-NAME (Qimin Yaoshu), 1 absence - applied both EDITs (heading "not seldom ran past twenty days"; first Qimin Yaoshu linked to enwiki)
CHECKED quote-check 0090.drawing#unfootnoted - 0 notes owed, 0 unfootnoted assertions owing a source (figures are own-map measurements, conversions verified) - nothing
CHECKED record-format 0009 round 1 - 1 VOCABULARY (Kichu / Kinan) - applied: "central and southern Wakayama" in both obata notes of 0009.notes.html
CHECKED record-format 0009 round 2 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED source-reader 0009#obata-1977-taue-2, obata-1977-taue-3 (owed by the gloss) - 2 READ (paper's own Kihoku / Kichu / Kinan three-region division, text.txt line 53) - nothing
CHECKED record-format 0090 - 0 / 0 / 0 - nothing
CHECKED record-format 0104 - 1 SESSION NOTE ("and another, generated plan" names a test fixture no reader meets) - applied: dropped; the sentence reads "Hayakawa's and Ubame's hand-drawn sheets take the form with no genkan and draw no porch." (the fixture stays named in the comment)
CHECKED record-format 0123 - 0 / 0 / 0 - nothing
CHECKED modal-triage two rounds (39 then 51 units) - recorded with make modal-triaged; the TOUCHES pop-ups are below as OPEN
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.notes.html
CHANGED research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html
CHANGED specs/449-rust-codebase/briefs/t371a-handoff.md
OPEN pop-ups the triage named TOUCHES from our pages (not checked here, per the brief): 0009 -> choice/winter_crop--barley, choice/winter_crop--none, hamlet/barley, hamlet/paddy (modal-accuracy, modal-gaps, modal-references); 0090 -> sheet/office-hall, sheet/residence; 0104 -> sheet/genkan, sheet/door, sheet/residence; 0123 -> sheet/granary (round 1) (modal-depiction)
OPEN sheet/garden, garden-pond, inner-court, kneeling-positions, outer-court are still owed, but also by 0103's and 0099's moves (other builders); 173 triage units are now pending repo-wide, most of them not ours
OPEN OUTSIDE THE CHANGE (record-format and source-reader): 0009.drawing.notes.html obata-1977-taue-2 still says "mountain zone of Kichu and Kinan" without the "central and southern Wakayama" gloss its twin now has (source-reader confirms the source supports it)
OPEN OUTSIDE THE CHANGE (quote-check): 0009.html opening block "a Chinese farm manual of 544" cites only qimin-yaoshu-juan2, which does not give the date; the drawing page cites qimin-yaoshu-enwiki for it
OPEN make record CHECK=1 refuses on other builders' inline originals (0107, 0331, earlier 0113 notes.html); make record would move them, which would touch 0107 / 0113 (forbidden), so not run here. make glossary clean; make question-sizes lists only 0059 (20,065, not ours); 0009's prose is now a little over 19,704 bytes (the link added)
OPEN quote-check and record-format dispatches needed DECIDE_OK: T371's plan section has no current CLEAR verdict (make decide F=449 T=T371)
