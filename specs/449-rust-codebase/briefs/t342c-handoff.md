# Handoff - feature 449 T342c, session 1: write

- SECTION=0093 0116 (registry keys 5220 takayama-jinya-jawiki, 14050 fuchu-joge-jinya)

- C1 DONE - 0093's findings page now gives the one-bay gate as "about 6 to 8.5 ft across" (the paragraph and the findings bullet) and the widest example as "2.6 m (~8.5 ft)"; no other `6 to 9 ft` or `~9 ft` remains in 0093's files; no quoted passage changed.
- C2 NARROWED - the absence note `how-our-maps-size-a-compound-and-its-buildings-2` (0116 drawing notes) now says the Japanese Wikipedia articles on the earthen storehouse (土蔵), on jin'ya (陣屋) and on the town fire brigades (町火消), each linked at its mention, were searched and give no spacing between buildings; the wall-thickness and fire-survival claims are dropped rather than quoted. Read from the archived copies (keys dozo-jawiki, jinya-jawiki, machibikeshi-jawiki); its HTML comment records the reread, and the three pages are on the ledger as nothing-found for 0116. Note for the checker: the 町火消 article mentions the firebreak grounds (火除地) set aside after the Meireki fire, an open-ground measure with no distance between buildings; the note does not mention it. The 陣屋 link uses the unencoded URL because that is the form the archive holds (the encoded form was refused by `make record CHECK=1`).
- C3 DONE - 5220's "What it is" and "Used for" now say "the 1816 rebuild of the office's parts - 玄関・吟味所・御役所・大広間"; no `takayama-jinya-jawiki*` note in `research/questions/*.notes.html` quotes 番蔵 or 書物蔵, so the storehouse rows are dropped from "Used for" (kept in "What it is"'s description of the article).
- C4 DONE - 14050's "Why it applies" now says the branch office was "staffed in 1867 by three officials who had come there"; "What it is" likewise says "the number of officials who had come there" (was "sent there"). 14050 has no "1717", "Ōmori" or "Omori".

## Files

- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.notes.html
- research/sources/010-works-cited/5220-takayama-jinya-jawiki.html
- research/sources/010-works-cited/14050-fuchu-joge-jinya.html
- research/source-attempts.jsonl (three `make source-outcome` rows)
- research/site/ and the glossary build output (`make record`, `make glossary`)

## Left open

- Nothing in the items. `make question-sizes` lists 2 questions over 20,000 bytes (0059 and 0009); neither is 0093 or 0116.
CHECKED quote-check 0093 (bunka-adachi/fujioka/omi-yakuimon, page and drawing) - 17 notes: 16 VERBATIM, 1 NOT-CHECKED (fuchu-joge-pamphlet-3, image-only labels, as before); 15 SUPPORTS, 2 GROUNDS, 0 unfootnoted - nothing
CHECKED quote-check 0116.drawing#how-our-maps-size-a-compound-and-its-buildings-2 - 1 absence note, a stated silence (not CLAIM-FROM-UNREAD); round 3's two findings settled - nothing
CHECKED record-format 0093 - 22 of 22 words ruled on, 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0116 - 9 of 9 words ruled on, 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED source-applicability fuchu-joge-jinya (14050) - APPLICABLE-WITH-LIMITS, limits MISSING 1 (first Joge intendant, so the buildings may be inherited from a full seat; the three are only the officials), RESTATES 1 (popular pamphlet) - 2 EDITs applied (make apply-edits; settled, not re-owed)
CHECKED source-applicability takayama-jinya-jawiki (5220) - APPLICABLE-WITH-LIMITS, What it is INACCURATE (one reference, not two), limits MISSING 2 (gundai rank from 1777 with branch offices; the text gives no layout, the parts list ends in nado) - 3 EDITs applied, its British spelling of center Americanized (make apply-edits; settled, not re-owed)
CHECKED modal-triage (12 page-moved units: armory, gatehouse, main-gate, nakamon) - main-gate TOUCHED by 0093 (yakuimon width now 6-8.5 ft), armory TOUCHED by 0123 (Pingyao armory block); gatehouse and nakamon untouched - recorded with make modal-triaged
CHANGED research/sources/010-works-cited/14050-fuchu-joge-jinya.html
CHANGED research/sources/010-works-cited/5220-takayama-jinya-jawiki.html
CHANGED research/site/ and the glossary build output (make record, make glossary); dev review records written by make record-checked / modal-triaged
OPEN modal-accuracy/gaps/references sheet/main-gate - triage TOUCHES it (0093's yakuimon width): a pop-up, not checked here
OPEN modal-accuracy/gaps/references sheet/armory - triage TOUCHES it via 0123 (not this session's question): a pop-up, not checked here
OPEN modal-depiction granary, inner-court, main-gate, office-hall, outer-court, rear-yard, residence, storehouse, tax-archive - owed because 0093/0116 drawing pages moved (modal-depiction is not triaged): pop-ups, another builder's; the other owed modal units (day-office, genkan, latrine, side-gate, writing-rooms, official-study, clerks--room, town_nearness, inner-court modal-form) predate this session
OPEN nothing else; record-owed names no quote-check, record-format or source-applicability unit of 0093, 0116, 5220 or 14050; claims released (research-claim STATUS=done); question-sizes lists only 0059 and 0009 over 20,000 bytes
