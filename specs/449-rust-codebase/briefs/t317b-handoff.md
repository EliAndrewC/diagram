# t317b handoff - session 1: write

- SECTION=0220 0088
- T318 DONE - in 0220's drawing notes, the `hokora-jawiki` note's session comment now says only "the ~90%+ mode, hokora vastly outnumbering shrines and three as a ceiling are on no page read". I checked each of the three against 0220's notes and drawing notes, and none is quoted on either; the main page's notes say the same. No visible text changed.
- T327 NARROWED - after "The road at a compound's front gate is the road the compound stands on, at that road's width.", 0088's drawing page has a new bullet: "The light and dark bands drawn across the road are a map drawing convention." It says the bands are texture that marks the ground as road and stand for no ruts, paving or steps. A Japanese road was trodden earth with gravel only on main roads (`jarimichi-jawiki`). No page read gives a level road or a town street any feature across its bed (absence note `how-our-maps-draw-and-label-the-highway-4`, searched 2026-11-22). The shogunate's provincial maps drew the main highways as red lines, and the one cross-mark found, on the Hagi domain's 1742 road map, marks a steep slope (new key `yamaguchi-hagi-road-maps`, with three verbatim passages that cover the red lines, the map's 1742 date and the slope line). The Evidence comment gains "convention (the light and dark bands across the road)", and a session comment beside the bullet describes the strokes. It is NARROWED because the brief's general "period plans drew a road in a flat color" is stated only as the provincial maps' red lines: the Edo kiriezu's yellow roads and hist-geo.jp 209_001.pdf were not read here, so they are not cited.

## Files

- research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.notes.html
- research/questions/0088-highways-and-what-lines-them-kaido.drawing.html
- research/questions/0088-highways-and-what-lines-them-kaido.drawing.notes.html
- research/questions/0088-highways-and-what-lines-them-kaido.drawing.originals.html (originals moved here by `make record`)
- research/sources/010-works-cited/37100-yamaguchi-hagi-road-maps.html (new, through `make reserve`)
- research/archive/39/3994e342ee47.json (new, written by `make reserve`'s archive step)
- research/source-attempts.jsonl (four outcome rows: cited:yamaguchi-hagi-road-maps, cited:jarimichi-jawiki, and nothing-found for the two Shizuoka Hakone pages)

The pool `.notes.md`, modal `.md` and rust files that changed in this clone during the session were written by other builders, not by this session's edits or `make` runs.

## Open

- The kiriezu and hist-geo pages are not cited. No passage from either was read here: the minato-rekishi PDF is NOT-CHECKED with no text layer, and the saved hist-geo PDF gave no text. Citing them owes a readable copy.
- `make reserve` archived the Yamaguchi page to the source archive and printed a diagram-research GitHub tree URL. Afterward `git status -sb` in /diagram/.specify/source-archive shows `main...origin/main` with nothing ahead, so the reserve step itself pushed that copy to the archive's remote. I ran no push. The brief forbids writing the archive's real remote, and this was the tool's automatic step.
- Checks owed for the next session:
  - quote-check and source-reader on `jarimichi-jawiki`, `yamaguchi-hagi-road-maps` and `-4` in 0088's drawing notes;
  - translation-check on the four new originals;
  - source-applicability on the new registry entry;
  - record-format on 0088's drawing page.
- `make record CHECK=1` is clean. `make question-sizes` lists only 0059 and 0009 over 20,000 bytes, neither touched here.
## Session 2 (checks)
CHECKED 0220 - nothing owed (T318 changed only a session comment) - nothing
CHECKED quote-check 0088.drawing (jarimichi-jawiki, yamaguchi-hagi-road-maps, -4) - r1: 1 SUPPORTS, 1 PARTIAL (Hagi, 1742 not in the quotes), 1 absence; r2: 2 SUPPORTS, 1 absence - applied: new passage #4 naming the Hagi lord's tour map (original added), drawing sentence now 'a road map the Hagi domain made for its lord's tour of 1742 ... a line drawn across the road partway along it where it climbs a steep slope' (r2 EDIT)
CHECKED record-format 0088 - r1/r2/r3: 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - applied: long-vowel marks dropped in the note (Kanpo, Mori) for the record's style
CHECKED translation-check 0088.drawing yamaguchi-hagi-road-maps - r1: FAITHFUL 1, LOOSE 2; r2: FAITHFUL 3, CANNOT-TELL 1 - applied: 'ninth month', 'tour of the domain'
CHECKED source-reader 0088.drawing yamaguchi-hagi-road-maps - r1: 4 READ; r2: 6 READ, 1 CONTRADICTED (registry dated all Hagi-Edo maps 1764) - applied via source-applicability's EDIT
CHECKED source-applicability yamaguchi-hagi-road-maps - r1/r2: APPLICABLE-WITH-LIMITS, limits HONEST - applied: What it is rewritten (catalog origin, two road maps and the village maps, dates differ by route), Why it applies (red line on provincial and village maps)
CHECKED quote-check 0123 neixiang-xianya-zhwiki (T319) - r1: 2 VERBATIM, 2 PARTIAL: the page says the layout follows the Qing regulation and the facing expresses a ritual-propriety idea, not that regulation required south; r2: 4 SUPPORTS, 1 unfootnoted (EDIT applied: 'sat inside the town instead, on its main street')
CHECKED source-reader 0123 neixiang-xianya-zhwiki (T319) - r1: 2 READ (on the looser reading); r2: 6 READ - applied: bullet's colon fixed, registry 8500's two 'by regulation' wordings restated
CHECKED record-format 0123 - r1: 1 SESSION NOTE, 1 self-contradiction; r2: clean - applied: bullet keeps layout and facing apart, note's wording clause moved to a comment
CHECKED translation-check 0123.drawing gloss (礼制思想) - FAITHFUL 1 - nothing
CHECKED source-applicability neixiang-xianya-zhwiki - APPLICABLE-WITH-LIMITS, limits HONEST - nothing
CHECKED modal-triage - side-gate TOUCHES (0088 bands); armory, main-gate, office-hall, road, granary TOUCHES (0123 facing; 0098/0113/0116 by other builders) - recorded with make modal-triaged
CHANGED research/questions/0088-highways-and-what-lines-them-kaido.drawing.html
CHANGED research/questions/0088-highways-and-what-lines-them-kaido.drawing.notes.html
CHANGED research/questions/0088-highways-and-what-lines-them-kaido.drawing.originals.html
CHANGED research/sources/010-works-cited/37100-yamaguchi-hagi-road-maps.html
CHANGED research/sources/010-works-cited/8500-neixiang-xianya-zhwiki.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.notes.html
CHANGED the review ledger and owed-state files the record-checked, apply-edits and modal-triaged commands write (not edited by hand)
OPEN pop-ups (not edited here): the road, main-gate, family-quarters, inner-court, residence and outer-court pop-ups repeat 0123's 'faced south by regulation'; triage sent on modal-accuracy/gaps/references for sheet/road, main-gate, armory, office-hall and modal-depiction for main-gate, granary, side-gate (side-gate's Depiction draws landing steps across the bank street, against 0088's 'no steps across a road')
OPEN translation-check CANNOT-TELL on 0088 yamaguchi-hagi-road-maps #4: the romanization 'Okunimawari Gokoteiki' of 御国廻御行程記 (go- or o-koteiki) needs the archives' own reading
OPEN 0123's quote-check round 1 bundle recorded 41 units of 0123 answered (the tool answers every unit in the bundle); only the neixiang-xianya-zhwiki ones were judged
OPEN 0088 record-format went to a third round (one word from quote-check's EDIT); no guard named a round trigger, so no arbiter was run; the only owed arbiter trigger, round:quote-check|q:0031@4, is another builder's
CHECKED quote-check 0123 neixiang-xianya-zhwiki r3 (the bullet as record-format's EDIT left it) - 2 VERBATIM, 2 SUPPORTS - nothing. source-reader's last read of 0123 was the colon wording before that EDIT; its own EDIT proposed the same fix
OPEN 0088's 'across': source-reader r1 said the page does not confirm the 横線 runs across the road (the road runs horizontally on the scroll); quote-check r2 and translation-check r2 read 横線 as a cross line and 'across' was put back. The two checks disagree; source-reader's last read was the version without 'across'
OPEN style: 0088's note dropped long-vowel marks (Kanpo, Mori), but registry 37100 still has Bōchō and gained Sanyōdō from source-applicability's EDIT; not changed here to avoid re-owing source-applicability
OPEN the brief's six pop-ups (road, main-gate, family-quarters, inner-court, residence, outer-court) cite neixiang-xianya-zhwiki, confirmed by grep; no other question repeats 'by regulation' for the facing
NOTE nothing committed, staged or stashed: the brief forbids it (the launch prompt's commit instruction was overridden by the brief)
