# Handoff - feature 449 task T197, group G2 (the village shrine), session 1: research and write

- SECTION=0221
- SECTION=0222
- SECTION=0223
- KEY=sakai-kaieji
- KEY=irori-jawiki
- KEY=liq-takayasu-daidokoro

No new registry key was reserved. The three KEY= lines are entries whose `Used for:` line changed: `irori-jawiki` and `liq-takayasu-daidokoro` now also name Religion and the dead, and `sakai-kaieji` names the kuri's earth floor; `hie-jinja-kurihara-jawiki` is unchanged in the registry (its note copied from 0215). `sakai-kaieji` has a NEW passage (note `sakai-kaieji-4` on 0221's drawing page: the kuri's wide earth floor and matted rooms), read by source-reader 2026-11-22 as READ from the page cache; its outcome is recorded `cited:sakai-kaieji` for 0221. `hie-jinja-kurihara-jawiki` (from 0215), `irori-jawiki` and `liq-takayasu-daidokoro` (from 0107) are existing notes, now copied with the same passages into 0222's notes and 0221's drawing notes. No glossary term was added: doma, kamado, irori, kuri, honden, plinth and tamagaki already have one.

G2.1 DONE - 0222's opening paragraph now says the Edo-period halls we found measured run from about 13 ft square (Chikusei's side hall, `chikusei-saishoji-yakushido-2`) to about 32 by 35 ft (the Ehime worship hall, `ehime-pref-honden-56-4`). The "How big" answer gives 18 to 35 ft long by 12 to 35 ft deep, which matches the drawing page's band, with Hie Shrine's 3-by-2-bay hall footnoted (`hie-jinja-kurihara-jawiki`) and the 18 by 12 ft labeled as our conversion at a 6-shaku bay, linked to 0215. (b) is NARROWED: "a subsidiary hall, not one where a village gathered" is gone, and the side hall now "stands part-way along the approach to a temple's main hall, so it is not the main hall itself" (`chikusei-saishoji-yakushido`, its passage #2). (c) "ridge plaque" is now "ridge tag" in 0222's notes, the same as the drawing page's; `make quote-verbatim Q=0222` matches Chikusei and Hie VERBATIM on both pages (the one DIFFERS, jawiki-goshi, is a reference marker that was already there).
G2.2 DONE - 0223's drawing page has a new bullet, "No fence is drawn along the approach", labeled a GUESS. It cites Yasuda Hachiman's late-Edo approach fence as the only one found at an ordinary shrine, and a new absence note (`how-our-maps-draw-shrine-woods-and-fences-chinju-no-mori-tamagaki-3`, searched 2026-11-22 plus the page's earlier searches). It gives the why (one example does not show how common the form was) and the cost (the one form attested before 1868 never appears on a map). The alternative it names is a knob between a fenced and an open approach, waiting on a second example or a count. The Evidence comment is updated.
G2.3 DONE - (a) 0221's drawing page has a new bullet. The kitchen end is a doma (**accurate**: the minka's floored and earth-floored parts, `irori-jawiki`, and Kaie-ji's one-building kuri with its wide earth floor, `sakai-kaieji-4`). The hearth on it is a kamado: **accurate** for Edo houses, on the doma as the rule (`liq-takayasu-daidokoro-2`), its reach to a village kuri resting on the dwelling's farmhouse form. Kaie-ji is named a city temple. The irori is left off, a map drawing convention. The stipple and the hearth glyph are map drawing conventions (a grounds note). An absence note says no page we read describes a village kuri's kitchen. (b) 0222's drawing page has a new bullet. The sanctuary's vermilion fill is a map drawing convention, not a finish found: the one village sanctuary described, Ehime's, has plain squared timber pillars (`ehime-pref-honden-56`), and an absence note covers the finish of village sanctuaries in general. The gray strip is the plinth's edge in front, a map drawing convention, and the stone plinth itself a GUESS (the same absence note, searched 2026-11-22).

## Files

- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.notes.html
- research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.originals.html (written by `make record`, the originals moved out of the new notes)
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.notes.html
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.originals.html (written by `make record`)
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
- research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.notes.html
- research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.html
- research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.notes.html
- research/sources/010-works-cited/9890-irori-jawiki.html, 9900-liq-takayasu-daidokoro.html and 7800-sakai-kaieji.html (their `Used for:` lines)
- research/source-attempts.jsonl (the source-pages and source-outcome lines of this session, appended by the tools; other sessions' lines may also be in it)
- specs/449-rust-codebase/briefs/t197-g2-handoff.md (this file)

The other modified research files in the clone (0004, 0030, glossary-variants.txt, 7180-l7r-median-domain.html) are not this session's.

## Left open

- 0222's main page is at 19,997 bytes, just under the 20,000-byte cap (`make question-sizes`). To fit, I shortened three of its sentences: "Two temple halls agree", "No Edo village hall three bays square was found measured", and Hie "thought late Edo". Anything more added there will need a split.
- Off-limits files still give the old range, for the orchestrator:
  - The pop-ups `l7r/diagram/interactive/assets/modals/sheet/compound-shrine.md` and `sheet/hall-and-dwelling.md` say "about 21 to 35 ft on a side", which the findings no longer say (they now say 13 to 35 measured, and 18 to 35 by 12 to 35 for worship halls). Both are owed an update and their checks.
  - So do the built pool pages: ochiba, ubame, hayakawa, the county example, the roundtrip test and hoshigaoka `.html`.
  - `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.notes.md` line 25 says "the village-hall band of about 20 to 35 ft on a side", which should read 18 to 35 by 12 to 35.
- G2.2: an approach-fence KNOB would need the country-shrine program (`l7r/diagram/buildings/types.json`) to change. That is the GM's or orchestrator's call; the record now says GUESS, which matches the procedure's claim as it stands.
- G2.3(b): the record calls the strip the edge of the sanctuary's plinth, following the sheet's own SVG comment ("on its plinth") and notes item 9. If the sheet's author meant a stone step instead, the bullet's one sentence on the strip changes.
- The irori is left off although `irori-jawiki` puts one in most minka (at the middle of the floored part). The record labels the omission a map drawing convention; whether the sheet should draw one is the GM's call.
- Hoshigaoka's notes and SVG say "hearth" for the kitchen glyph, where the record now says kamado; the notes are off-limits here.
- A lead not read: a search of 2026-11-22 returned Shōkō-ji's temple kitchen (MLIT's multilingual description, https://www.mlit.go.jp/tagengo-db/R6-00032.html), a great temple's of 1863 with a doma of kamado and a raised floor with an irori. It could ground a kuri's hearths if read.
- `make quote-verbatim Q=0221` matches the new notes (irori differs only by the page's reference markers). It also shows `kuri-jawiki` DIFFERS (the Wikipedia sentence has been reworded since it was quoted) and a `kuri-jawiki` passage NOT-ON-PAGE on 0221's main page; both were there before and are not this group's items.
- `make archive-inbox` lists the GM's downloads 堺市史 (two WAITING copies) and four files too big to archive. None bears on these items, so I left them alone.
## G2 checks (session 2, 2026-11-22)
CHECKED quote-check 0221.drawing (5 notes) - 3 READABLE, 1 SUPPORTS 2 PARTIAL (sakai-kaieji-4 one-building, liq-takayasu-daidokoro-2 scope), 1 JOINED-WRONG - applied (doma rule narrowed, gloss narrowed, joiner; sakai-kaieji-3 footnote added at 'a city temple' by hand)
CHECKED quote-check 0221.drawing round 2 (6 notes) - 4 SUPPORTS, 0 findings - nothing
CHECKED quote-check 0221.drawing#liq-takayasu-daidokoro-2 round 3 (after source-reader's narrowing) - PARTIAL ('where most of the Edo period's common people lived' unquoted) - applied (clause dropped: 'in the Edo period's row-houses (nagaya)')
CHECKED quote-check 0222 (17 notes) - 15 VERBATIM SUPPORTS, 1 CLAIM-FROM-UNREAD (drawing ...-keidai-6), 1 contradiction ('No Edo village hall three bays square') - applied (-6 cut to its silence; sentence now 'No Edo village worship hall three bays square was found measured.', shortened from the agent's wording for the byte cap)
CHECKED quote-check 0222 round 2 (17 notes) - 14 SUPPORTS, 1 JOINED-WRONG (hie-jinja-kurihara-jawiki) - applied
CHECKED quote-check 0223.drawing (2 notes) - 1 VERBATIM SUPPORTS, 1 absence - nothing
CHECKED record-format 0221 - 1 VOCABULARY (stipple) - applied (glossary 28230-stipple.json); rounds 2 and 3 - 0 findings - nothing
CHECKED record-format 0222 - 2 reading defects - applied ('Other Edo-period halls measured run from'; 'The gray strip is the front of the plinth'); next round 1 (side-hall heading contradicted the opening) - applied ('A temple's Edo-period side hall is about 13 ft square.'); last round 0 findings
CHECKED record-format 0223 - 0 findings in the change - nothing
CHECKED translation-check 0221.drawing#sakai-kaieji-4 - FAITHFUL 1 - nothing
CHECKED source-reader 0221.drawing#sakai-kaieji-4 - 3 READ - nothing; 0222#hie-jinja-kurihara-jawiki - 3 READ - applied ('Hie Shrine, ranked a village shrine in 1874,' by hand, with 'halls we found sized' -> 'halls sized' and 'our conversion of its bays' -> 'our conversion' to stay under the 20,000-byte cap: 0222 is 19,954 bytes)
CHECKED source-reader 0221.drawing#irori-jawiki - 2 READ - nothing; #liq-takayasu-daidokoro-2 - READ with scope finding - applied (rule said of row-houses, the kuri a carry-over)
CHECKED source-applicability irori-jawiki, sakai-kaieji - APPLICABLE-WITH-LIMITS, limits MISSING one each - applied; liq-takayasu-daidokoro - MISSING one, applied; round 2 OVERSTATED one (Myohoin kuri) - applied
CHECKED modal-triage (60 units) - 12 TOUCHES, 19 units sent on - recorded; BUT the 0221/0222 pages were edited after the triage bundle was built, so record-owed still lists every page-moved pop-up unit: re-run make modal-triage / modal-triaged once, now that the pages are final
CHECKED modal-form sheet/compound-shrine - 0 FIX 2 NOTE - applied (sizes moved to the 'how large' paragraph; 'is' -> 'was'); round 2 - 0 findings
CHECKED modal-form sheet/hall-and-dwelling - 2 FIX 1 NOTE - applied the M13 retense ('In Rokugan ... holds'); M5.2 sent to modal-research
CHECKED modal-research sheet/compound-shrine + sheet/hall-and-dwelling (one batch) - CS: ACCURACY 1, GAPS 2; HD: ACCURACY 3, REFERENCES 1, GAPS 3 - recorded; applied only partly, see the collision below
OPEN - pop-up collision: while the gate was down (another builder's uncommitted rust/gate/crates/tree and core/src/codeid.rs did not compile, about 13 min), ANOTHER SESSION edited compound-shrine.md and hall-and-dwelling.md (its own research-style fixes: 'seems to have kept', 'some thatched', 'The shrine held two things', the 1841 doors sentence, the Fukuoka 12 by 15 ft dwelling, Sources +chikusei-saishoji-yakushido +kawakami-1992-shrine-headman, Entry +0268), and it now runs modal-depiction on both (/tmp/l7r-check/modal-batch-modal-depiction, 04:39), which freezes them. My modal-research apply then landed on top and left three DUPLICATES that I could not remove (frozen): compound-shrine.md 'some under a thatched roof, some thatched,' (drop 'some under a thatched roof,'); hall-and-dwelling.md look paragraph, my sentence 'A worship hall was a timber building ... is not recorded.' duplicates the other session's doors sentence (drop mine, or keep only its walls-not-recorded clause); hall-and-dwelling.md size sentence carries the 12 by 15 ft dwelling twice (drop 'the one small monk's dwelling measured, at a Kōshin hall in a country town, was about 12 by 15 ft;'). Mine that landed cleanly: CS torii clause + Entry +0220; HD 'often much like ... even at temples of standing'. Refused (text already changed): CS ACCURACY opening, HD ACCURACY 1 opening.
OPEN - pop-ups: modal-form, modal-research, modal-depiction are owed again on both pop-ups, and depiction on every kind the triage touched (sanctuary, wood-kami-altar, shrine-altar, precinct-clearing, approach, the-monk-s-rooms); I left them to the session that holds them rather than race it.
OPEN - hall-and-dwelling's acolytes sentence: modal-research found no Entry page carrying it; it is canon (setting/l7r.md:707, 'What is a village, and who lives there?': 'The monk may have a few acolytes to help farm the land ... on loan from larger families'), so it stays; 0229 or 0221 should carry that passage.
OPEN - declined: modal-research HD GAPS 3 (a temple's clergy from 0227's 1872 Tokyo registers) - city-temple evidence for a country shrine's monk; HD GAPS 1's Kaie-ji earth floor is on 0221's drawing page only, so a pop-up cannot cite it until it moves to 0221's main page.
OPEN - OUTSIDE THE CHANGE: 0222.notes absence note inside-a-village-shrines-...-keidai still says 'No village hall three bays square of the Edo period was found.' (contradicts the Saitama hall; should say a village shrine's worship hall) and carries CLAIM-FROM-UNREAD text on the Himemiya pages and the town survey (move to its search comment or cite); 0222.drawing 'the one village sanctuary we found measured' calls the Ehime shrine a village shrine where its page gives no rank; 0222.notes nara-byakugoji-hondo-2 roofing terms (hongawarabuki, sangawara) have no glossary term; 0223 'ordinary shrine' for Yasuda Hachiman is nowhere explained; 0223 kotobank-tamagaki fn-7 'jeweled' NOT-ON-PAGE; 0223.notes 'igaki' undefined; 0223.notes fujita-2007-shaso-slopes-3 shows an untranslated Japanese tail.
OPEN - escapes used: DECIDE_OK on every round-2+ dispatch (the guard demanded a plan verdict for 449 T250, another builder's polder budget task, unrelated to these record checks); POLL_OK on one wait loop for the other builder's Rust compile.
CHANGED research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html
CHANGED research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.notes.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.notes.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
CHANGED research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.notes.html
CHANGED research/sources/010-works-cited/9890-irori-jawiki.html, 9900-liq-takayasu-daidokoro.html, 7800-sakai-kaieji.html
CHANGED l7r/diagram/interactive/assets/glossary/28230-stipple.json (new) and the assembled glossary.json (make glossary)
CHANGED l7r/diagram/interactive/assets/modals/sheet/compound-shrine.md, hall-and-dwelling.md (shared with the other session, see the collision line)
CHANGED research/source-attempts.jsonl and the record ledgers the make targets append to (record-checked, apply-edits, modal-triaged)
DONE - make record CHECK=1 clean, make record built, record-owed names no quote-check/record-format/source-*/translation unit of 0221-0223 or the three keys; make research-claim Q='0221 0222 0223' STATUS=done recorded.
OPEN - guard bug, for the orchestrator: set_down_hooks.rs LAUNCHED reads a FOREGROUND Agent result's agentId as a launch, and no task-notification ever ends it, so running() is never empty after a page session's foreground checks and the Stop hook loops on 'a builder slot is free' (this session refused four times). Fix: an agentId in a synchronous Agent result is an end, not a launch; pin it with a replay of this session's transcript. I left T252 unstarted and 449 not set down: both are the orchestrator's.
