# Handoff - feature 449 T371h, session 1: write (cleanup 2)

- SECTION=0009 0103 0107

H1 DONE - 0009 findings, "Was the drain also confined to well-watered places": the footnote on the Edo-period clause now cites `horikawa-2011-nakaboshi-6` (the note that quotes "before the war its spread was limited to some regions"), in place of `horikawa-2011-nakaboshi`.
H2 DONE - 0103 note `kotobank-ishidoro` (in both `.notes.html` and `.drawing.notes.html`): the two non-continuous passages (Britannica's, then Daijisen's) are now joined with `; ` as research/CLAUDE.md and STYLE.md require, not " and ". `kotobank-ishidoro-2` was not flagged and was left as it was.
H3 DONE - 0107 drawing page: the bullet heading "Where the kamado stands is a knob between two forms." now reads "Our plans set the kamado in one of two places, chosen for each map."; its closing "Each plan takes one." is dropped because the heading now says it. The `kitchen-walls-absence` comment now says the Kakunodate report (sitereports.nabunken.go.jp article 127894) refused us (HTTP 429) and is on the GM's download list (entry 337), not "Unreadable". `make download-add` appended entry 337; `make source-outcome` recorded a re-attempt (still 429, 2026-11-23, outcome unreadable, Q 0107).
H4 DONE - registry `37320-mlit-kaga-ashigaru`: "one domain's lowest warrior rank" now reads "one domain's foot soldiers".

## Files

- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.notes.html
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.drawing.notes.html
- research/questions/0107-kitchens-daidokoro.drawing.html
- research/questions/0107-kitchens-daidokoro.notes.html
- research/sources/010-works-cited/37320-mlit-kaga-ashigaru.html (untracked: another builder added it and has not committed it)
- research/to-download.md (entry 337, written by `make download-add`)
- research/source-attempts.jsonl (the ledger row, written by `make source-outcome`)
- research/site/ (rebuilt by `make record`), glossary assets (by `make glossary`)

## Sizes after (bytes of prose)

- 0009: 19,795 (was 19,793; under the 20,000 cap)
- 0103: 13,061
- 0107: 14,195

`make record CHECK=1`, `make record`, `make glossary` were clean; `make question-sizes` reported none over the cap.

## Open

- None. No new registry keys were reserved, and no passage was added or re-quoted. The record checks were not run; per the brief, the next session runs them.
## Checks (session 2, t371h-checks)
CHECKED quote-check 0103 (kotobank-ishidoro, both pages) - 10 VERBATIM, 10 SUPPORTS, 2 absence, 0 findings (owed note judged; the rest carried from round 3; record-checked answered 12 units) - nothing
CHECKED quote-check 0107.drawing (cleanup-edo-hettsui, liq-takayasu-daidokoro-2) - 2 READABLE, 2 VERBATIM, 2 SUPPORTS, 0 findings (only the 2 owed notes judged; the other units carried from round 3; record-checked answered 30 units) - nothing
CHECKED source-reader 0103 + 0103.drawing kotobank-ishidoro - 3 READ, 0 CONTRADICTED, 0 NOT-FOUND - nothing
CHECKED record-format 0009 - 54 of 54 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0103 - 25 of 25 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0107 - 16 of 16 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY (round 5's knob finding confirmed settled) - nothing
CHECKED source-applicability mlit-kaga-ashigaru (37320) - APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED quote-check 0009 (horikawa-2011-nakaboshi, -6) - 2 READABLE, 2 VERBATIM, 1 PARTIAL (H1 moved the Edo-period clause's note to -6, which does not carry it), 1 EDIT - applied (make apply-edits: -6 now follows the prewar clause, horikawa-2011-nakaboshi the Edo clause); both units settled with the round
CHECKED record-format 0009 round 2 (after the quote-check EDIT) - 54 of 54 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED modal-triage (whole bundle, 114 units across 0009 0059 0090 0097 0103 0104 0107) - 79 sent on (TOUCHES), the rest triage: untouched - recorded with make modal-triaged
CHECKED modal-triage round 2 (21 units re-owed by the 0009 EDIT and a 0106 change) - 9 sent on (TOUCHES winter_crop--none, hamlet/paddy, sheet/inner-rooms), the rest untouched - recorded
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html (quote-check EDIT: footnotes of the confinement block split between -6 and horikawa-2011-nakaboshi)
CHANGED the check ledger (make record-checked, make apply-edits, make modal-triaged) and research/site/ + glossary assets (make record, make glossary); make record CHECK=1 clean, 0 questions over 20,000 bytes
OPEN pop-ups the triage named against 0009/0103/0107 (not checked here, another builder's): modal-research (accuracy/references/gaps) for choice/winter_crop--none, hamlet/paddy, hamlet/farmhouse, sheet/door, sheet/garden, sheet/hearth, sheet/residence, sheet/inner-rooms (0106 + 0107); modal-depiction for sheet/door, sheet/garden, sheet/kitchen, sheet/residence. The triage also sent on 0059, 0097 and 0104 pop-ups (intake, weir_form, water_source_position, intake_place, intake_siting, hamlet/weir, stream, irrigation-ditch) - other builders'.
OPEN nothing else: make record-owed names no non-pop-up unit of 0009, 0103, 0107 or 37320. Claims not released, as the brief says.
