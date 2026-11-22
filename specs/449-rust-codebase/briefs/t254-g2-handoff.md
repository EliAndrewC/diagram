# Handoff - feature 449 T262, T266, T270, T272, group G2 (the village shrine), session 1

- SECTION=0221
- SECTION=0222
- SECTION=0229
- MODAL=sheet/approach
- MODAL=sheet/sanctuary

G2.1 DONE - (a) 0222's absence note `inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai` now ends "No Edo-period village worship hall three bays square was found measured.", matching the findings sentence that cites it; what the Himemiya Shrine pages and the town's survey report give is removed (they are not archived, and the ledger has them unreadable since 2026-10-02), and the note's search comment says only what was searched and when. (b) The drawing page's sanctuary bullets now say "the sanctuary at the one rural shrine we found measured" and "The sanctuary of the one rural shrine we found described", and the Evidence comment says "the one rural shrine's sanctuary read". (c) `kuri-jawiki` restated to the live page (fetched 2026-11-22; the archived copy of 2026-10-02 had the old wording): fn-8's original is now 「寺院の僧侶が居住する場所」 (translation unchanged, "The place where a temple's monks live"), and the -2 note on 0221's main and drawing notes is 「大規模な寺院では独立した建物であるが、一般の寺院では寺の事務を扱う寺務所と兼用されていることが多く、一般の民家によく似た建物も多い。」, translated "In large temples it is a separate building, but in ordinary temples it often doubles as the temple office that handles the temple's business, and many are buildings much like ordinary houses." The meaning did not move, so the sentences it supports are unchanged. `make quote-verbatim Q=0221` and `Q=0222` now show only reference-marker DIFFERS.
G2.2 DONE - 0222's drawing page has a new bullet in the compound-shrine list: a second kami's altar inside the hall is drawn a square about 5 ft across in plain wood color, larger than life so it can be seen, a map drawing convention; what it costs is that the mark reads larger than a real altar, against the one measured household shrine of about 16 in (40 cm), linked to 0219's drawing page. A sheet comment gives the pixels (16 px at 3 px = 1 ft, #C9A57A). The Evidence comment lists it under convention. `sheet/wood-kami-altar.md`'s Depiction already says the same (about 5 ft, larger than life, plain wood color) and already names 0222's drawing page in `Drawing:`, so it was not edited.
G2.3 DONE - `sheet/approach.md` Guesses: "That no fence runs along the approach: one stone fence from before 1868 lined an ordinary shrine's approach, the only one found, which is not enough to say how common such fences were."
G2.4 DONE - `sheet/sanctuary.md` Guesses: "That the sanctuary stands on a stone plinth: no page read describes what a village sanctuary stood on."
G2.5 DONE - 0229's canon comment now quotes l7r.md's next sentence ("The monk may have a few acolytes to help farm the land, which they may do on a part-time basis on loan from larger families in the village.", verified with `make canon`, l7r.md:707), and the paragraph adds the visible sentence "The monk may have a few acolytes, lent part-time by the village's larger families, to help farm the monk's land." inside the paragraph that opens "The setting our maps are drawn for ...".

## Files

- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.notes.html
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.notes.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.originals.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.notes.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.originals.html
- research/questions/0229-village-temples-tera.html
- l7r/diagram/interactive/assets/modals/sheet/approach.md
- l7r/diagram/interactive/assets/modals/sheet/sanctuary.md
- specs/449-rust-codebase/briefs/t254-g2-handoff.md
- the sources-consulted ledger (`make source-outcome` for the kuri-jawiki page, QUESTION=0221), and the claims sheet through `make research-claim`

`make record`, `make glossary` and `make question-sizes` ran clean. The 3 questions over 20,000 bytes are not this group's (0059, 0009 and one other already over).

## Left open

- `kuri-jawiki` has the same old wording outside this brief's scope: 0227's `kuri-jawiki-3` originals (main and drawing originals, 「寺院の僧侶の居住する場所、また寺内の時食を調える…」 and the 庫裏は大規模寺院… sentence) and the registry entry `research/sources/010-works-cited/7630-kuri-jawiki.html`. Neither was touched; 0227 needs the same restatement to the live page.
- No source-reader dispatch: no new passage was cited. The kuri passages are the same passages, restated to the page's current wording; quote-check on 0221's notes is owed in session 2.
- The live kuri page was read through `make source-pages` but not re-archived. The archived copy still has the old wording.
## Session 2 (checks, T254)
CHECKED quote-check 0221 - r1 9 notes, 6 SUPPORTS 1 PARTIAL; r2 12 notes, 9 SUPPORTS 0 PARTIAL - applied r1's EDIT (drawing page "Many an ordinary temple's kuri")
CHECKED quote-check 0222 - 16 notes, 12 SUPPORTS 1 PARTIAL, 2 CLAIM-FROM-UNREAD - applied 3 EDITs (chikusei-saishoji-yakushido footnote added to the 13 ft side hall; Muromachi sentence moved into the absence note's comment; -6 sub-passage trimmed)
CHECKED quote-check 0229 - 16 notes, 15 SUPPORTS, 1 PARTIAL outside the change, 0 unfootnoted (acolytes sentence is canon) - nothing
CHECKED record-format 0221 (x2), 0222 (x2), 0229 - all 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED translation-check 0221 - 3 FAITHFUL - nothing
CHECKED source-reader kuri-jawiki (0221 main and drawing) - 3 READ - applied registry original の->が and the drawing page's "Many" hedge
CHECKED source-applicability kuri-jawiki - APPLICABLE-WITH-LIMITS, 2 limits missing - applied the limits EDIT (stub with no sources; temple not shrine)
CHECKED modal-triage (2 rounds) - 7 TOUCHES (approach, wood-kami-altar x2, shrine-altar, the-monk-s-rooms), rest untouched - sent on
CHECKED modal-form sheet/approach - 0 findings; sheet/sanctuary - 1 NOTE (doors/materials, sent to research); sheet/the-monk-s-rooms - 6 FIX 3 NOTE, 6 EDITs applied; sheet/wood-kami-altar - 1 FIX (canon) 1 NOTE, NOTE EDIT applied
CHECKED modal-research sheet/approach - ACCURACY 1 (research step, open) - nothing; sheet/compound-shrine - clean; sheet/hall-and-dwelling - acolytes rest on 0229, 1 EDIT applied (shrine's land -> monk's land); sheet/sanctuary - 5 EDITs applied (plinth guess, 0269 reference, 1841 stone base, door per bay); sheet/the-monk-s-rooms - 2 rounds, 9 EDITs applied (earth-floored kitchen dropped, hedges, 0232 village kuri ~39 ft, records sentence, walls/roof/doorways not recorded); sheet/wood-kami-altar - 2 rounds, 3 EDITs applied then clean
CHECKED modal-depiction sheet/approach, compound-shrine, hall-and-dwelling, shrine-altar, the-monk-s-rooms - clean; sheet/sanctuary - TRUTH 1, EDIT applied (approach on the hall's line); sheet/wood-kami-altar - clean, its drawn size rests on 0222's drawing page
CHANGED research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.notes.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.notes.html
CHANGED research/sources/010-works-cited/7630-kuri-jawiki.html
CHANGED l7r/diagram/interactive/assets/modals/sheet/hall-and-dwelling.md
CHANGED l7r/diagram/interactive/assets/modals/sheet/sanctuary.md
CHANGED l7r/diagram/interactive/assets/modals/sheet/the-monk-s-rooms.md
CHANGED l7r/diagram/interactive/assets/modals/sheet/wood-kami-altar.md
OPEN research step: the Rokugan rules sheet/approach (arches one, three or seven) and sheet/sanctuary (the deity is a Fortune) state rest only on drawing pages; carry each canon sentence onto 0220's and 0222's text, as 0229's acolytes were (modal-research M8/M13, a repeat). Not done here: 0220 is not this brief's, and a 0222 text edit owes another round of its checks.
OPEN sheet/wood-kami-altar About lacks why a wood kami has an altar in Ubame's Inari shrine, whose hand keeps it, and when it is used (modal-form P4): canon only, for the GM's notes or the GM.
OPEN 0222's drawing-page bullet on a second kami's altar (5 ft wood square) reads as if for every compound shrine, but Hayakawa draws its altars as white emblems (modal-depiction note); narrow it to the wood-kami altar or file a sheet drift. Also shrine-altar's emblem marks are recorded as a convention on no drawing page (OUTSIDE THE CHANGE).
OPEN outside the change: 0229 opening paragraph "with a small house for its monk" generalizes onga-choshi-jiin-4 (one temple) - PARTIAL; 0229 drawing page "The village's shrine is its parish temple." item ends with no period; 0229 onga-choshi-jiin-4 "200 prayer households" may want a tooltip; 0222 nara-byakugoji-hondo-2 roofing terms (hongawarabuki, sangawara) have no glossary term (raised every round since 2).
OPEN tamamuro-2009-terauke (0229): quote-verbatim marks 2 passages NOT-CHECKED for line-end hyphens; quote-check read them VERBATIM. homemate-shichido-garan-5 and koshoji-jiin-zoka were unfetchable today (archive VERBATIM).
OPEN 0227's kuri-jawiki-3 originals still carry the old wording (from session 1's list); the registry entry's original is now fixed.
OPEN not mine, left: the 0031-driven choice/* and hamlet/windbreak depiction units, and 0123/sheet/main-gate; modal-triage cleared main-gate as untouched in its batch. record-owed now names 0 unanswered.
