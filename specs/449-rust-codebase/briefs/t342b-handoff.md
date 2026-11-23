# Handoff - feature 449 T342b (T344), session 1: write

- SECTION=0113
- REGISTRY=9971 (fuchu-joge-pamphlet); also new 37190 (edo-ashigaru-minami-plan) and 25200 (fuchu-joge-daikansho-ato, moved from the uncited works by `make cite-uncited`)

B1 DONE - registry 9971 no longer credits the pamphlet with "Iwami Ōmori" or "from 1717". Both rendered pages and the text layer were read (archived 97/97ff685ad836), and neither page carries 1717, 享保, 大森 or 石見. The pamphlet gives only 出張陣屋 and 「代官所から離れた支配地に設けられた役所で、支所みたいなものでござる。」. The facts are kept and sourced to Fuchū city's designation record for the site, `fuchu-joge-daikansho-ato` (archived ee/ee6ee8026d71): 「享保2年（1717年）、…上下代官所は廃止され、石見大森代官所の出張陣屋と改められて、…幕末まで存続した。」. That page was already a KEPT uncited entry. It was moved to the works cited with `make cite-uncited` and given a Used for line (compounds). The 9971 entry links it as `<a href=...><code>fuchu-joge-daikansho-ato</code></a>`, and its READ comment says where each fact comes from. No question note repeats either fact: a grep of research/questions/ for Ōmori|Omori|Iwami|大森 found only unrelated pages and two search comments in 0116.
B2 DONE - the 0113 drawing page's clerks'-room bullet now reads "the plans of the North Town Magistracy of 1841 and the South of 1842 show, directly behind the saikyosho, ... 調之間 ...". The sentence carries the footnotes edo-ashigaru-bugyosho and edo-ashigaru-minami-plan. The new note quotes the page's own text verbatim: the caption 「天保13年2月 南町奉行所平面図」 and the NDL attribution 「（旧幕府引継書『南北御番所住居向絵図面』、国立国会図書館デジタルコレクションより）」, both translated and with their originals moved to the originals file. The room order was read off the linked full-size image and is labeled as read from the plan, not the text: court, board veranda, 裁許所 with 入側 beside it, 調之間, corridor, 用達詰所. This session confirmed it on a crop of the court quarter. The 1841 note's session comment no longer says "not archived"; it names the archived copy e1/e1aa32c4a281. The Evidence comment had no "not archived" wording and is unchanged.

## Files
- research/sources/010-works-cited/9971-fuchu-joge-pamphlet.html (edited)
- research/sources/040-uncited-works/25200-fuchu-joge-daikansho-ato.html (deleted by the move)
- research/sources/010-works-cited/25200-fuchu-joge-daikansho-ato.html (new by the move; Used for line written)
- research/sources/010-works-cited/37190-edo-ashigaru-minami-plan.html (new, `make reserve`)
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.originals.html (written by `make record`)
- research/archive/e1/e1aa32c4a281.json (new, the archive row for ?eid=20, by `make reserve`)
- research/archive/cf/cf3650d70bdc.json (new, the archive row for the plan image, by `make source-outcome`)
- research/source-attempts.jsonl (lines appended by the tools)

## Open
- The move of 25200 is not staged (the brief forbids staging). `make cite-uncited` asks for `git add -A` of the move, so commit the deletion and the new file together.
- The plan image URL (https://www.ashigaru.net/archives/edo/minami_te1302_m25x.jpg) is named only in the notes' session comment and in the registry entry's READ comment. It is not on the entry's citation line, and the visible note says "the full-size plan the page links to", in the same form as the 1841 note. Reason: `make record` refused the citation line while the image was unarchived. `make source-outcome OUTCOME=cited:edo-ashigaru-minami-plan` has since archived it (cf/cf3650d70bdc), so a later session may put the URL back on the citation line if wanted.
- Outside this brief, not touched: registry 14050 `fuchu-joge-jinya` (the same PDF under a second key) says "three officials sent from the intendant's seat". The pamphlet says only that they 「来ていた」 ("had come"), so "from the intendant's seat" may be an inference to check.
- Owed checks for the next session: source-reader and source-applicability on 9971, 25200 and 37190; quote-check, translation-check and record-format on 0113's drawing page.
## Session 2 (checks)
CHECKED quote-check 0113 (21 units incl. 0113.drawing#edo-ashigaru-bugyosho, #edo-ashigaru-minami-plan) - 22 READABLE, 22 VERBATIM, 22 SUPPORTS, 4 absence notes in form, 0 unfootnoted - nothing
CHECKED record-format 0113 round 1 - 22 words ruled, 1 VOCABULARY - applied (reading and gloss of the plan title 南北御番所住居向絵図面 in the edo-ashigaru-minami-plan drawing note)
CHECKED record-format 0113 round 2 - 25 words ruled, 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED translation-check 0113 round 1 - 13 pairs, 13 FAITHFUL - nothing
CHECKED translation-check 0113 round 2 (re-owed by the record-format edit) - 13 pairs, 13 FAITHFUL - nothing
CHECKED source-reader 0113.drawing#edo-ashigaru-minami-plan - 4 claims, 4 READ (room order read off the linked image) - nothing
CHECKED source-applicability edo-ashigaru-minami-plan (37190) - APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED source-applicability fuchu-joge-daikansho-ato (25200) - APPLICABLE, What it is INACCURATE (a city cultural-property page for a prefecture-designated site, not a municipal designation record), 1 limits wording fix - applied (2 EDITs)
CHECKED source-applicability fuchu-joge-pamphlet (9971) - APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED modal-triage 3 units - TOUCHES sheet/clerks--room, sheet/office-hall; sheet/magistrate-s-dais untouched - recorded with make modal-triaged
CHANGED research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
CHANGED research/sources/010-works-cited/25200-fuchu-joge-daikansho-ato.html
CHANGED research/site/ and the glossary build (make record, make glossary)
OPEN modal-depiction sheet/clerks--room and sheet/office-hall - the triage says the 0113 drawing page's new 1842 South Magistracy evidence touches them; pop-ups are another builder's, not checked here
OPEN the other owed pop-up checks record-owed names (modal-accuracy/gaps/references/form/depiction on day-office, genkan, inner-court, latrine, official-study, side-gate, writing-rooms, armory, town_nearness, granary, main-gate, outer-court, rear-yard, residence, storehouse, tax-archive) - from other questions' changes, other builders'
OPEN source-applicability on fuchu-joge-pamphlet could not confirm from the text layer that the two shrines, the main gate and the entrance are labeled on the drawing; that rests on the write session's re-read of the rendered pages (449 T344)
OPEN registry 14050 fuchu-joge-jinya "three officials sent from the intendant's seat" may overstate the pamphlet's 「来ていた」 - outside this brief, carried from session 1
OPEN nothing is staged or committed (the brief forbids it); the 25200 move needs the deletion and the new file committed together
