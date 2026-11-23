# 449 T333 / T330 0116 pointer, session 1 (write) - handoff

- SECTION=0098 0088 0116 0113

- B1 DONE - no text change: the archived copy (66 -> 3f/3fa3d09e79e2/20261002T143742Z) carries all four quoted originals `takayama-onkura-heritage#1`-`#4` verbatim, so the citation stands as written; outcome recorded `cited:takayama-onkura-heritage` (Q 0098). Nothing added to the download list.
- B2 DONE - `how-our-maps-draw-storehouses-for-the-tax-rice-2` (0098 drawing notes) now links the Kawashiri database page (`kawashiri-komegura-kunishitei`) and the two Asakusa pages, Kotobank (`kotobank-asakusa-okura`, which gives the site and the storehouses' total floor area, 御蔵総建坪 8060坪) and ja.wikipedia 蔵前 (`kuramae-jawiki`, which gives the site area); the visible sentence now says the Asakusa pages give the ground's whole area (Kotobank its site and total floor area, Wikipedia its site) and no single building's size.
- B3 DONE - (a) passage #4 now renders the title in English, 「the "Record of the Route of the Tour of the Domain", ...」, followed by "(the page gives the title no reading; Okunimawari Gokoteiki is this project's reading)"; searched the archived page (served HTML and text) for furigana and found none, and no Yamaguchi Prefectural Archives catalog page is archived (comment in the note). (b) passage #2's 横線 is now "a horizontal line is drawn in partway along the road", with the gloss "(the page does not say which way the line lies against the road)"; the drawing page now says "a horizontal line drawn in partway along the road where there is a steep slope"; registry 37100's `Used for` now reads "the one mark found drawn on one, a horizontal line at a steep slope".
- B4 DONE - registry 37100: Bocho, Sanyodo (macrons dropped in its own prose); also "the domain lord's tour of his domain" -> "of the domain" (gender-neutral rule). No other macrons in prose in the 0088 files (grepped).
- B5 DONE - 0116 note `takayama-jinya-jawiki-6`, both notes files: "(as in the courtroom section)" -> "(the first is the sentence <a href="0099-the-hearing-court-shirasu.html">The hearing court (shirasu)</a> cites)" (0099's `takayama-jinya-jawiki-5` quotes the same 1816 sentence). 0116 claimed for 449 by this clone; its drawing.html untouched.
- B6 DONE - no change owed: 0113 (findings, notes, drawing page) no longer says the writing room is attested "only at Takayama"; brief A's text already gives Iijima's 1993 rebuild (findings bullets "Who worked in the writing room?" and "Did a small office have a writing room...", absence note `small-office-writing-rooms-absence` "the writing room appears only at Iijima's rebuild of 1993, and the binding room only at Takayama", drawing page's back-row bullet). 0113 claimed for 449 by this clone.
- B7 DONE - 0113 drawing page's clerks'-room bullet now reads "Our maps put the clerks' room inside the office hall, behind the dais band and beside the day office." Beside the day office keeps the Takayama cite; behind the dais is labeled a GUESS for a county office bounded by Edo's town magistracies: `edo-ashigaru-bugyosho` (eid=23, archived 66/6644a5eca0a2) quoted for the suits-and-examinations quarter, and "the plan of the North Town Magistracy of 1841 that the page reproduces shows, directly behind the saikyosho, ... a room whose name (調之間, read here shirabe no ma) makes it a working room for the examining officials; no page we read states its use"; a new absence note `how-our-maps-draw-the-office-hall-and-its-clerks-goyakusho-4` for the intendant's office (Takayama's 1851 plan unreadable); a new note `qing-yamen-tushuo-5` quoting 「从大堂正中再入一道大门，便是二堂。」 for the second hall behind the great hall. Evidence comment updated (guess list).
- B8 DONE - 0088 drawing page: the bullet is now "The road is drawn in one flat earth tone, a map drawing convention." ("The tone marks the ground as road, and our maps draw nothing on its bed"), the Evidence comment's convention is "the road's one flat earth tone", and the trailing convention comment describes one flat earth-tone stroke with no dashes or bands (449 T328). No quoted passage touched.

## Files
- research/questions/0098-storehouses-for-the-tax-rice.drawing.notes.html
- research/questions/0088-highways-and-what-lines-them-kaido.drawing.html
- research/questions/0088-highways-and-what-lines-them-kaido.drawing.notes.html
- research/sources/010-works-cited/37100-yamaguchi-hagi-road-maps.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.notes.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.originals.html (written by `make record`, the two new originals moved out of the notes)
- the claims sheet (claims for 0113, 0116 via `make research-claim`) and the sources-consulted ledger (four `make source-outcome` lines), both written by their tools
- specs/449-rust-codebase/briefs/t330b-handoff.md (this file)

## Open
- B7: the South Town Magistracy's 1842 plan (http://edo.ashigaru.net/?eid=20) is not archived and not keyed, so the drawing page cites only the 1841 North plan the archived eid=23 reproduces; the 1842 plan is named in the note's session comment and the Evidence comment only. A later session may key and archive eid=20 (and eid=21's 調役詰所 footnote) if the check wants the second plan cited.
- B7: "saikyosho" and "shirabe no ma" are new visible terms on 0113's drawing page; record-format may ask for glossary tooltips.
- `make record CHECK=1` clean (4333 pages); `make glossary` clean; `make question-sizes`: none of 0088/0098/0113/0116 over (0059 and 0009 are, not this brief's).
- Checks owed (next session): record-owed will name the 0088, 0098, 0113, 0116 notes/drawing units, registry 37100 (source-applicability), translation-check for the changed #2/#4 translations and the two new 0113 originals.
## Session 2 (checks)
CHECKED quote-check 0088.drawing#yamaguchi-hagi-road-maps - 2 READABLE, 2 VERBATIM, 2 SUPPORTS, 1 absence, 0 unfootnoted - nothing
CHECKED quote-check 0098.drawing#how-our-maps-draw-storehouses-for-the-tax-rice-2 - 1 absence note in form, 0 flags - nothing
CHECKED quote-check 0113.drawing (edo-ashigaru-bugyosho, -goyakusho-4, mapple-takayama-jinya-2, qing-yamen-tushuo-5) round 1 - 5 READABLE/VERBATIM/SUPPORTS, 1 absence, 1 unfootnoted - applied: footnote repeated after the plan sentence, the plan reading (吟味所 / 次之間 / 裁許所, 調之間 behind) put in the visible gloss
CHECKED quote-check 0113.drawing round 2 - 4 SUPPORTS, 1 absence, 1 wording - applied: 'directly behind the saikyosho, which faces the court, a room whose name'
CHECKED quote-check 0116#takayama-jinya-jawiki-6 + .drawing - 2 READABLE, 2 VERBATIM, 2 PARTIAL, 2 JOINED-WRONG - applied: headings 'the office's rooms were parts of one office' / 'as a real jin'ya gathered its office's rooms into one office', passages joined with '; '
CHECKED record-format 0088 - 26/26 words, 0/0/0 - nothing
CHECKED record-format 0098 - 48/48 words, 1 VOCABULARY - applied: 'the Asakusa storehouse ground, the shogun's rice store at Edo,'
CHECKED record-format 0113 rounds 1-3 - round 1 0/0/0; round 2 1 VOCABULARY + 1 reading defect - applied: readings for 吟味所 (ginmisho), 次之間 (tsugi no ma), 裁許所 (saikyosho), 調之間 (shirabe no ma); defect settled by quote-check's wording; round 3 (only for the new word tsugi, no round trigger raised) 0/0/0
CHECKED record-format 0116 rounds 1-2 - 8/8 words, 0/0/0 both rounds - nothing
CHECKED translation-check 0088.drawing#yamaguchi-hagi-road-maps - 2 pairs FAITHFUL - nothing
CHECKED translation-check 0113.drawing#qing-yamen-tushuo-5 rounds 1-2 - 11 pairs FAITHFUL - nothing
CHECKED source-applicability yamaguchi-hagi-road-maps (37100) - APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED source-reader 0113.drawing#edo-ashigaru-bugyosho - 3 READ (調之間 behind 裁許所 read from the detailed plan image the page links to, kita_te1210_m25x.jpg) - applied: 'reproduces' -> 'links to' in the drawing bullet and the gloss, 'the room facing the court' -> 'a room facing the court' (later reworded by quote-check round 2)
CHECKED source-reader 0113.drawing#qing-yamen-tushuo-5 - 2 READ (label too broad) - applied: gloss now 'of the Mayang county yamen in Hunan, as Chen Tianxi, once a private secretary in a county yamen, recalled it ...'; drawing sentence narrowed to 'in one Chinese county office, as a former county secretary recalled it'
CHECKED source-reader 0116#takayama-jinya-jawiki-6 + .drawing - 2 READ - nothing (its 'one building' point fixed by quote-check's heading edits)
CHECKED modal-triage (whole bundle, 65 units incl. other builders' 0101/0104/0123 pages) - 22 TOUCHES, 33 units sent on, the rest 'triage: untouched'
CHANGED research/questions/0098-storehouses-for-the-tax-rice.drawing.notes.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
CHANGED research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.html
CHANGED research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html
CHANGED research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.notes.html
CHANGED research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.notes.html
CHANGED the check ledger (make record-checked, apply-edits, modal-triaged) and the claims sheet (0088 0098 0113 0116 released, STATUS=done), by their tools
OPEN pop-ups (not checked here, another builder's): triage named sheet/road (0088 drawing), sheet/clerks--room, sheet/magistrate-s-dais, sheet/office-hall (0113 drawing and findings, 0116 both pages), sheet/hearing-court (0116 drawing); and modal-accuracy/gaps/references of sheet/clerks--room and sheet/office-hall owed directly by 0113's findings page moving
OPEN 0116 OUTSIDE THE CHANGE (quote-check): drawing page 'A schematic plan tends to scatter a dozen separate labeled pavilions' has no footnote - a grounds note if it means our own earlier maps, a citation if plans in general
OPEN 0116 takayama-jinya-jawiki-6 passage #2 (the storehouse list) supports neither sentence that cites it (quote-check, source-reader); left as is - drop it, or extend it to the surviving-buildings line, at the next edit
OPEN 0113: the 1842 South plan (edo.ashigaru.net/?eid=20) still not archived; source-reader notes the plan also labels a 調役詰所 beside the 内詮議所 (eid=23's footnote: 赦帳撰要方詰所 on the Tenpo 11 plan) - unused
OPEN tooling: translation-check reports every pair header in make translation-owed shows an empty source-language field '()'
NOTE make record / make glossary failed once on another builder's uncommitted rust/guard/shared/src/tree.rs (missing field head); passed on retry. Final: record CHECK=1 clean (4333 pages), record, glossary clean (2812 terms), question-sizes: 0088/0098/0113/0116 under (0009 and one other over, not this brief's), record-owed names nothing of these units
CHANGED specs/449-rust-codebase/briefs/t330b-handoff.md (this session's lines; nothing staged or committed, per the brief)
