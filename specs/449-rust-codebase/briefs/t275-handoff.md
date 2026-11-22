# T275 handoff - session 1 (research and write), 2026-11-22

- SECTION=0093
- SECTION=0097
- SECTION=0123

## Items

- T275.1 DONE - 0093's guardroom bullet now adds that the horse-viewing room comes first, beside the gate, and the gun store follows beyond it toward the south end (footnotes `tamba-kaibara-nagayamon`, the city's gate page, quoted with its original, and `tamba-kashiwara-jinya` for the south side), and that no source we read says whether the gun store took one of the three rooms or two (absence note `kaibara-gun-store-absence`).
- T275.2 DONE - the archived site page (26/262777be7b79) puts the 桁行十三間半 ... 八畳三間 text under 指定理由 of the 1971 national historic-site designation (文部省告示第2号), not under the gate's prefectural listing. 0097 now says "the text of the site's designation as a national historic site" (the 13.5-ken bullet, which made the same mislabel) and "the national designation text" (the rooms bullet), and its `kaibara-jinya-tamba` note's gloss says the same. The rooms bullet adds "How many of the three rooms the gun store took is not recorded" (the order is 0093's, so only the count is a silence here) (`kaibara-gun-store-absence`).
- T275.3 DONE - 0123's heading softened from "inside the great hall" to "at the two sides of the great hall". The end-bay sentence is now marked as a modern account's (`pingyao-yamen`); added that the oldest account, the imperial encyclopedia of the 1720s, says only east / west of the great hall, words that fit a room at the hall's end or a building beside it (`gujin-tushu-jicheng-juan338-zhwikisource`, original then translation), and that no source gives how deep the armory ran (absence note `pingyao-armory-depth-absence`).

## New keys and notes

- NEW registry key `tamba-kaibara-nagayamon` (37020; archive ff/ff370533931b), tags period=premodern; region=japan; kind=institutional.
- The 古今圖書集成 juan 338 page already had a KEPT uncited write-up, `gujin-tushu-jicheng-juan338-zhwikisource` (30600), so instead of a duplicate key it was moved to the works cited with `make cite-uncited` and given its Used for: line. A key `gujin-pingyao-yamen` was reserved first by mistake; its stub (37030) and its archive row (research/archive/9b/9b915a7f9f9e.json) were deleted, but its copy already pushed to the private diagram-research archive at 9b/9b915a7f9f9e stays orphaned (harmless; the unencoded-URL copy 5a/5a06a30df294 is the cited row), and research/source-attempts.jsonl holds its reserve line.
- New notes: 0093 `tamba-kaibara-nagayamon`, `kaibara-gun-store-absence`; 0097 `kaibara-gun-store-absence`; 0123 `gujin-tushu-jicheng-juan338-zhwikisource`, `pingyao-armory-depth-absence`. Changed note: 0097 `kaibara-jinya-tamba` (its gloss only; the link, quoted passages and claim are unchanged).
- Owed by the next session (not run here): quote-check / source-reader on the new notes, translation-check on the two new originals, record-format on the three pages, source-applicability on the two write-ups (37020 new, 30600 newly cited with a new Used for: line). The `Research:` claims citing 0093 / 0097 / 0123 (pingyao armory, Kaibara gate rooms) are the orchestrator's.

## Files

- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html
- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.notes.html
- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.originals.html
- research/questions/0097-staff-rowhouses-and-barracks-nagaya.html
- research/questions/0097-staff-rowhouses-and-barracks-nagaya.notes.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.originals.html
- research/sources/010-works-cited/37020-tamba-kaibara-nagayamon.html (new)
- research/sources/010-works-cited/30600-gujin-tushu-jicheng-juan338-zhwikisource.html (moved here by `make cite-uncited`; Used for: written, pointing at Towns, the section 0123 sits in; a limits sentence and a READ date added)
- research/sources/040-uncited-works/30600-gujin-tushu-jicheng-juan338-zhwikisource.html (DELETED by the move; commit the deletion)
- research/archive/ff/ff370533931b.json (new)
- research/source-attempts.jsonl (appended by reserve / source-outcome: the new keys' cited outcomes, and nothing-found for the pass's cmeg, sekimeitiko, akiou, mlit (0093) and Sina blog, szzy ch. 16-18 (0123) pages)
- specs/449-rust-codebase/briefs/t275-handoff.md

## Left open

- Whether the gun store took one room or two stays a recorded silence; the kojodan signboard's 三室 does not settle it. The nabunken site reports (68743, 68744) returned 503 in the pass and might hold a survey plan of the gate; worth one retry by a later pass.
## Check session (session 2)
CHECKED quote-check 0093 (tamba-kaibara-nagayamon, kaibara-gun-store-absence, tamba-kashiwara-jinya) - 2 SUPPORTS, 1 absence, 0 flags - nothing
CHECKED quote-check 0097 (kaibara-jinya-tamba, kaibara-gun-store-absence) - r1: 4 VERBATIM, 1 PARTIAL, 1 CLAIM-FROM-UNREAD; r2: 1 SUPPORTS, 1 absence, 0 flags - applied the absence-note EDIT; PARTIAL (20,000-koku seat) fixed by hand: passage 1 swapped for the page's opening sentence (original replaced in originals.html), gloss now says the second passage is the designation text, the others the city's
CHECKED quote-check 0123 (gujin-tushu-jicheng-juan338-zhwikisource, pingyao-armory-depth-absence, pingyao-yamen) - r1: 4 SUPPORTS, 1 absence flag, 1 unfootnoted; r2: 4 SUPPORTS, 0 flags - applied the absence-note EDIT; dropped the unsourced 'of the 1720s' from the encyclopedia sentence
CHECKED record-format 0093 - 16/16 words, 0/0/0 - nothing
CHECKED record-format 0097 - r1: 1 VOCABULARY, 1 reader finding; r2: 1 VOCABULARY - applied the side-swap EDIT; glossary 'horse-viewing room' written by hand (the checker's draft was unsourced; kept to the name's literal meaning); r2 GLOSSARY 'abolition of the domains' applied
CHECKED record-format 0123 - r1 and r2: 18/18 words, 0/0/0 - nothing
CHECKED translation-check 0093#tamba-kaibara-nagayamon - FAITHFUL 1 - nothing
CHECKED translation-check 0123#gujin-tushu-jicheng-juan338-zhwikisource - FAITHFUL 1 - nothing
CHECKED translation-check 0097#kaibara-jinya-tamba (the new passage 1) - FAITHFUL 1 - nothing
CHECKED source-applicability tamba-kaibara-nagayamon - APPLICABLE-WITH-LIMITS (limits MISSING one) - applied the limits EDIT (one gate, one small domain's seat)
CHECKED source-applicability gujin-tushu-jicheng-juan338-zhwikisource - APPLICABLE-WITH-LIMITS (HONEST) - nothing
CHECKED source-applicability kaibara-jinya-tamba - r1: MISSING one (unit, city figure, drawing); r2: HONEST - applied the unit and figure EDITs; the drawing point settled by source-reader's wording
CHECKED source-reader 0093#tamba-kaibara-nagayamon - 3 READ - nothing
CHECKED source-reader 0097#kaibara-jinya-tamba - r1: 10 READ, 1 CONTRADICTED; r2: 13 READ - applied the registry EDITs ('two different room layouts' -> one layout described twice; 'the domain's drawing' -> 'a drawing of the jin'ya')
CHECKED source-reader 0123#gujin-tushu-jicheng-juan338-zhwikisource - 2 READ - nothing
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.html
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.notes.html
CHANGED research/questions/0097-staff-rowhouses-and-barracks-nagaya.originals.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html
CHANGED research/sources/010-works-cited/37020-tamba-kaibara-nagayamon.html
CHANGED research/sources/010-works-cited/14040-kaibara-jinya-tamba.html (not in the write session's list; was clean before)
CHANGED l7r/diagram/interactive/assets/glossary/28240-horse-viewing room.json (new)
CHANGED l7r/diagram/interactive/assets/glossary/28250-abolition of the domains.json (new)
CHANGED l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt (make glossary)
OPEN pop-ups sheet/gatehouse, sheet/main-gate, sheet/servants--quarters: triaged TOUCHES by another session's modal-triage (not run here); owed modal-research (accuracy, gaps, references) - not checked here, per the brief
OPEN sheet/armory's own About/Depiction change (modal-form, -research, -depiction) is another builder's, left alone
OPEN outside the change: 0093 drawing note kitain-bansho is NOT-READABLE/DIFFERS (quoted 山門右側に接し is not on the page; re-quote or re-point)
OPEN outside the change: 0097 'The junior officials ... lived in rowhouses (nagaya), which served as their barracks' - kaibara-jinya-tamba supports only long, narrow, single-story; the gate's rooms are not dwellings
OPEN for the orchestrator's claims: per source-applicability, 錢糧庫 in the Gujin juan 338 Pingyao entry is the tax treasury (the county granary is listed separately), so a map should not draw grain storage east of the great hall from it; bears on the Pingyao armory Research: claims
OPEN 0031/0072 units in record-owed are other builders', not touched
CHANGED research/source-attempts.jsonl (the check agents' reads appended; also in the write session's list)
CHANGED l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt are tracked and modified (make glossary); 37020 is untracked (new, the write session's)
OPEN the modal triage that answered this session's pop-ups (/tmp/l7r-check/triage-t259f, another session's) read the page text after round 1's 0097 side-swap fix but BEFORE the 0123 'of the 1720s' removal and the 0097 passage swap; make modal-triage now reports nothing owed, so its untouched answers (barracks, door, karo-s-house, nakamon, retainers--quarters, road, side-gate) stand on the earlier text - the later edits drop an unsourced date and change a note's quote, not what a block states
OPEN glossary edits owe make page-check at the push (not run here: a shared clone)
OPEN the 'abolition of the domains' definition (1871, domains replaced by prefectures) is record-format's draft, applied as written; see the grep check in the next line
OPEN (cont.) grep of research/questions for 廃藩置県 / abolition of the domains / 1871 finds no passage of the record that states the 1871 date: the definition is unconfirmed against the record and rests on the checker's general knowledge
