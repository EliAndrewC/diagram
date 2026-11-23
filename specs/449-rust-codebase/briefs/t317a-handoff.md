# T322 / T323 (t317a) - session 1 handoff

- SECTION=0098 0113 0164 0170

- T322.1 DONE - 0098's `kawashiri-komegura-kunishitei` note (notes and drawing.notes) now follows the tojo-gura passage with a gloss from the page alone: "(the tojo-gura, 外城蔵, is one of the stores the page names; the page does not say what it was)" (archived copy 20261002T122659Z names 外城蔵 and never explains it). No glossary term: the page gives no meaning to define.
- T322.2 DONE - `28280-archery strip.json` takes "arrow lane" and "arrow lanes" as variants (no other term owned them), so the uses in 0164 (body bullet and the `mancheng-zhwiki-21` note) and 0170 (body and both notes files, `mancheng-zhwiki`) link to it; the quotations keep their own words. The definition is widened beyond a county office: "The jiandao: a ground for practice archery kept inside the walls of a Chinese county office, as at Jiexiu with an archery hall built for it; also listed among the buildings of a Qing banner garrison quarter."
- T322.3 DONE - `10850-hongawara.json` takes "full tile" and "full-tile" (no other term owned them in glossary-variants.txt).
- T323 DONE (0098) - the login sentence in `how-our-maps-draw-storehouses-for-the-tax-rice` (drawing.notes) and in the same text in `storehouses-for-the-tax-rice` (notes) now says only "a dictionary page that turned up in search was behind a subscription and was not read". The ledger has the page as JapanKnowledge `introduction/keyword.html?i=1463` (outcome unknown; source-filter NOT KEPT 2026-10-02, "sample-pages listing ... behind a subscription"). The work it excerpts cannot be identified from the ledger, so no `download-add`. I also checked the note's other pages: its search comment now names them. The Omori page is `omori-daikansho-kunishitei` (kunishitei 911/64) and the Kaibara page is `kaibara-jinya-tamba` (the ledger shows no national-database Kaibara page). Both were re-read from the archive and give no storehouse size. The Echigo three-village clause is backed by the note `sagami-2012-gogurasho-2`, cited on the same page.
- T323 DONE (0113) - the absence notes `the-office-hall-and-its-clerks-goyakusho` (notes) and `how-our-maps-draw-the-office-hall-and-its-clerks-goyakusho` (drawing.notes) now say: the Gifu prefectural list gives the Takayama office a floor area and no length or depth (already cited, `takayama-jinya-gifu-3`); the Takayama city page and the Japanese Wikipedia article give the office no size (both read and archived; I grepped the archived text for ㎡/平方メートル/坪 and the 御役所 lines; the city page's only areas are the site's lots); the Tamba city page on the Kaibara jin'ya lists its surviving front hall's rooms and gives the hall no size; the Fuchu pamphlet gives tsubo only (already cited, `fuchu-joge-jinya-2`). The Kaibara page (read, archived 20261002T152928Z) is now CITED in a new note `kaibara-jinya-tamba-2`, in both notes files, with two translated passages (the hall's form and its rooms), originals moved by `make record`. Its footnote sits beside the absence footnote in both the findings and the drawing page. The outcome is recorded (`cited:kaibara-jinya-tamba`, Q 0113).

## Files

- research/questions/0098-storehouses-for-the-tax-rice.notes.html
- research/questions/0098-storehouses-for-the-tax-rice.drawing.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.originals.html (written by make record)
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.originals.html (written by make record)
- l7r/diagram/interactive/assets/glossary/28280-archery strip.json
- l7r/diagram/interactive/assets/glossary/10850-hongawara.json
- l7r/diagram/interactive/assets/glossary.json (written by make glossary)
- research/assets/glossary-variants.txt (written by make glossary/record; my rows: arrow lane, arrow lanes, full tile, full-tile)
- research/source-attempts.jsonl (already dirty at start; my lookups and the one source-outcome row appended)
- this handoff

Not mine, though they are dirty in the clone: dev/claims-index.json, research/to-download.md, assets/modals/sheet/official-study.md,
the three pool magistracy SVGs and the files dirty at the start. I made no `download-add`.

## Open

- The checks owed (session 2): record-format on 0098, 0113, 0164 and 0170 (visible words and glossary links); quote-check and
  source-reader on `kaibara-jinya-tamba-2` (new); translation-check on its two originals; quote-check on the edited 0098/0113
  absence notes and the 0098 kawashiri note.
- The glossary edits owe `make page-check` (not run here).
- `kaibara-jinya-tamba-2` backs the absence note's Kaibara clause. In the 0113 body it sits after "- only a floor area" beside the absence footnote, so quote-check should read it as support for the silence only.
- `14040-kaibara-jinya-tamba.html`'s `Used for:` names only the rowhouse gate (compounds section). Its new use for 0113's office hall is not named there. The source-applicability / record-format check should say whether that line owes a clause.
- `make question-sizes`: 0059 and 0009 are over 20,000 bytes. Neither is mine.
- `make record CHECK=1` builds cleanly.
## Session 2 (checks)
CHECKED quote-check 0098 r1 - 5 READABLE, 5 VERBATIM, 3 SUPPORTS, 2 PARTIAL ("great domain" not on the Kawashiri page), 2 note-form flags (JOINED-WRONG, UNLINKED-NAME) - applied: 6 EDITs (passages joined with "; "); by hand: "great domain's" -> "the Kumamoto domain's" at all four Kawashiri uses (0098 body x2, drawing x2), Omori/Kaibara/Echigo names linked in both absence notes
CHECKED record-format 0098 r1 - 0 VOCABULARY, 1 SESSION NOTE (the subscription-page clause), 0 HISTORY - applied: 2 EDITs (clause dropped from both absence notes)
CHECKED source-reader 0098 kawashiri-komegura-kunishitei - 6 READ (1 scope) - applied: 1 EDIT ("the domain's office beside it" -> "in the same port", drawing knob)
CHECKED quote-check 0113 r1 - 4 READABLE, 4 VERBATIM, 4 SUPPORTS, 1 CLAIM-FROM-UNREAD (absence notes stated what the Gifu list and Fuchu pamphlet contain) - applied by hand: both absence notes cut to silences; the body's "- only a floor area" now carries takayama-jinya-gifu-3 and fuchu-joge-jinya-2
CHECKED record-format 0113 r1 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED translation-check 0113.drawing kaibara-jinya-tamba-2 - 2 FAITHFUL - nothing
CHECKED source-reader 0113 kaibara-jinya-tamba-2 - 2 READ - nothing
CHECKED modal-triage r1 (28 units) - 8 sent on, 20 untouched - nothing (recorded with make modal-triaged)
CHECKED quote-check 0098 r2 - 9 READABLE, 1 UNFETCHABLE (outside the change), 8 VERBATIM, 10 SUPPORTS, 0 PARTIAL, 0 flags - nothing
CHECKED quote-check 0113 r2 - 10 READABLE, 10 VERBATIM, all SUPPORTS, 0 flags - nothing
CHECKED record-format 0098 r2 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0113 r2 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED modal-triage r2 (36 units) - 21 sent on, 15 untouched - nothing
CHANGED research/questions/0098-storehouses-for-the-tax-rice.html
CHANGED research/questions/0098-storehouses-for-the-tax-rice.drawing.html
CHANGED research/questions/0098-storehouses-for-the-tax-rice.notes.html
CHANGED research/questions/0098-storehouses-for-the-tax-rice.drawing.notes.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.notes.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
CHANGED specs/449-rust-codebase/briefs/t317a-handoff.md (these lines); make record / make glossary rewrote their generated outputs (originals, glossary.json, glossary-variants.txt, site)
OPEN pop-ups the triage sent on (owed by the 0098/0113 page changes; not checked here, pop-ups are out of this brief's scope): modal-accuracy/gaps/references on sheet/granary, granary-stilts, office-hall, river, river-landing, tally-office; modal-depiction on sheet/granary, office-hall, river-landing, tally-office. The triage also sent on 0116-owed ones (tax-archive, barracks, storehouse, granary) - another builder's.
OPEN 0164 and 0170 were never named by record-owed (the glossary-link edits owed no check), so nothing ran on them; make page-check for the glossary edits still not run.
OPEN 14070-kawashiri-komegura-kunishitei registry limits say "Kumamoto was one of the largest domains", which the page does not say (source-reader); the record now says only "the Kumamoto domain's". Either cite a page for its size (about 540,000 koku) or drop the clause - not a unit of this session.
OPEN quote-check 0098 outside the change: takayama-onkura-heritage is UNFETCHABLE (Japan Heritage portal maintenance notice, culturalproperties/result/2060) - recheck or add to the download list; how-our-maps-draw-storehouses-for-the-tax-rice-2 names the Kawashiri database page and the Asakusa pages without links (UNLINKED-NAME).
OPEN source-reader suggestion (no EDIT): the Kaibara page's 御用所 (office hall, not standing, two-storied in Meiji photos, unsized) is a closer case for 0113's absence than the front hall; a later pass could quote it in kaibara-jinya-tamba-2.
OPEN still owed and not mine: record-format 0116; 0088's units (quote-check, record-format, source-reader, translation-check, source-applicability yamaguchi-hagi-road-maps); sheet/official-study and writing-rooms pop-up checks.
OPEN process note: this session's hand fixes were applied with one small python replace script rather than the Edit tool (each replacement asserted to match exactly once).
