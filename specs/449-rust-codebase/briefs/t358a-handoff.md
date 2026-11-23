# Handoff - feature 449 T358a session 1 (write)

- SECTION=0106 0101 0218 0190

A1 DONE - 0106 drawing: the program-drawn county plan's senior retainers' long-house is 22 by 60 ft on the outer court's west wall, partitioned into three dwellings each with a door on the court, the karō's quarters its north 24 ft (sizes a GUESS); the Grounds comment names `pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json` (22 x 60, bays at 24 and 42, karo's bay 22 x 24); the gloss bullet now says the hand-drawn plans (Ochiba, Hayakawa, Ubame) label the karō's house "the house elder", a map drawing convention, and the program-drawn plans caption the karō's quarters without it; Evidence comment matched.
A2 DONE - 0101 note `tajima-2007-night-soil`: new glossary term `Kōka shunjū` (variants Kōka shunjū, Kôka Shunjû, Koka Shunju, 耕稼春秋), which the tooltip wraps inside the quoted passage too (record.js skips only CODE/PRE/SCRIPT/STYLE); and a gloss outside the quotation quoting the Digital Daijisen entry on Kotobank (a seven-volume Edo farming book by Tsuchiya Matasaburō of Kaga, completed Hōei 4 (1707)), new registry key `kotobank-koka-shunju`. The quoted passage itself is untouched.
A3 NARROWED - 0218 drawing: the corner follows the record; the tree beside the shrine is now our maps' GUESS (the record gives the god's seat as a small shrine, or an old tree or a stone, not the two together). The one readable pairing found - one farm household's stone shrine at the foot of a persimmon about 20 m east of its house, a 2004 Shikoku village survey - is cited (`tokushima-yashikigami`, new note on this page) for exactly that, with a new absence note `shrine-tree-absence`. Evidence comment: the tree moved from accurate to guess. The bullet's other sentences kept; the opening paragraph's guess list adds the tree.
A4 DONE - 0190 drawing: lead sentence now "the one at a magistrate's gate, with a second beside it where the seat has a bounty out"; new bullet: where a seat has a bounty out our maps draw a second board beside the gate's notice board - a GUESS; the canon's bounty of 100 koku on the hermit Shoda (new canon registry key `l7r-bounties`, "Registering a bounty" and "Example bounties", Used for the trades-and-services section, where 0190 lands); Ubame's plan making it its magistrate's stated as the plan's choice (the canon names no seat); the Chinese office's wanted notices on the gate's walls among its other notices (`gmw-tianxia-yamen`), not on a board of their own. `bench-board-absence` extended (visible: no page keeps a board apart for wanted notices or a bounty; comment: the 2026-11-23 search). Grounds and Evidence comments updated (setting-canon added; the bounty board to the guess list).

## Files

- research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html
- research/questions/0101-privies-setchin.notes.html
- research/questions/0101-privies-setchin.originals.html (written by `make record`, the original moved out)
- research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html
- research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.notes.html
- research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.originals.html (written by `make record`)
- research/questions/0190-notice-boards-kosatsuba.drawing.html
- research/questions/0190-notice-boards-kosatsuba.drawing.notes.html
- research/sources/010-works-cited/37200-l7r-bounties.html (new, reserved)
- research/sources/010-works-cited/37210-kotobank-koka-shunju.html (new, reserved)
- l7r/diagram/interactive/assets/glossary/28340-Kōka shunjū.json (new, reserved)
- l7r/diagram/interactive/assets/glossary.json (written by `make glossary`)
- research/assets/glossary-variants.txt (written by `make glossary`)
- research/archive/9d/9dcb65ed450d.json (the Kotobank page archived by `make source-outcome`)
- research/source-attempts.jsonl (shared ledger: this session's source-pages and source-outcome lines appended; it was already modified by others)

## Searches

- `make archive-find TERMS="耕稼春秋"`: one archived text, the National Tax Agency's museum page (author and what the book covers, no date); Kotobank 耕稼春秋 read via `make source-pages` (QUESTION=0101) -> `cited:kotobank-koka-shunju`; ja.wikipedia 耕稼春秋 404 -> `unreadable`.
- `KEY=t369-shrine-tree` (make research-search, the brief's Q/Q_JA/TERMS): record 0219/0236 and the archive; read the archived Kotobank and ja.wikipedia yashikigami entries (shrine OR old tree/stone), `tokushima-yashikigami` (one household's stone shrine under a persimmon 20 m east of the house - cited), `yuasa-nishida-2006` (a household's Benten at the foot of a large tree in a grove west of the house, form not stated), the Minka-en page. Plus one WebSearch, 屋敷神 祠 傍ら 神木 屋敷の隅 (summaries only, nothing cited).
- `KEY=t370-bounty-board` (make research-search: "Was a separate board for wanted notices or bounties set up at a Japanese magistrate's office gate, or a Chinese yamen's?" / 陣屋 門前 手配書 人相書 高札; terms 人相書, 手配 高札, 懸賞 布告, wanted notice board yamen, bounty notice gate): nothing records a separate board; the archived `makishima-2016-village-courier` has wanted descriptions relayed post town to post town. Recorded in `bench-board-absence`'s comment.
- Record 0236's notes (`nireyama-yashiki-bochi-3`): a household god in the house grove, behind which the dead were buried - a grove, not a shrine beside a tree; the 0218 wording avoids counting pairings.
- Ledger: `cited:kotobank-koka-shunju`, ja.wikipedia 耕稼春秋 `unreadable`, `tokushima-yashikigami` PDF `cited:tokushima-yashikigami`, `yuasa-nishida-2006` and `makishima-2016-village-courier` PDFs `nothing-found` (archive copies read).
- `make canon TERMS="Shoda|bounty"`.

## Open

- `tokushima-yashikigami`'s registry `Used for:` line already says "one persimmon 20 m east of a homestead" but names no section link; left as it was (not this brief's).
- `make archive-inbox` lists two WAITING downloads (堺市史 copies) and four REFUSED oversized PDFs in the GM's inbox; not this brief's, left alone.
- `make question-sizes`: two questions over 20,000 bytes (0059, 0009), neither touched here.
- Checks not run (the next session's): the new notes (0218 `tokushima-yashikigami`, `shrine-tree-absence`; 0190 `l7r-bounties`; 0101's Kotobank gloss) owe quote-check and translation-check; the two new registry entries owe source-applicability; record-format on the four pages.
## Checks (session 2, t358a-checks)
CHECKED quote-check 0101#tajima-2007-night-soil - 4 READABLE, 4 VERBATIM, 4 SUPPORTS, 0 unfootnoted - nothing
CHECKED quote-check 0106.drawing#jinya-kotobank,#unfootnoted - 1 VERBATIM, 1 SUPPORTS, 0 unfootnoted - nothing
CHECKED quote-check 0190.drawing#l7r-bounties,#gmw-tianxia-yamen,#bench-board-absence,#unfootnoted - round 1: l7r-bounties NOT-CHECKED (canon not in bundle), PARTIAL (hermit, Imperial magistrates rested on the gloss), 1 JOINED-WRONG - applied its 2 EDITs, and by hand added the quotes 「it is Imperial magistrates who are responsible for notifying other jurisdictions about a fugitive on the run.」 and 「Shoda the hermit」; round 2: l7r-bounties VERBATIM 7/7 (read against setting/l7r.md 6876-6999), gmw-tianxia-yamen VERBATIM, 3 SUPPORTS, 0 unfootnoted - nothing
CHECKED quote-check 0218.drawing (fuchu-joge-pamphlet-6, henan-neixiang-2, kotobank-yashikigami, shrine-tree-absence, tokushima-yashikigami) - 4 READABLE, 4 VERBATIM, 3 SUPPORTS, 1 PARTIAL ("farm" household not in the source), 1 absence - applied 3 EDITs ("farm" dropped on the page and in shrine-tree-absence; "the record gives" -> "the encyclopedia gives")
CHECKED record-format 0101 - 29 of 29 words, 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0106 - 1 of 1 words, 0/0/0 - nothing
CHECKED record-format 0190 - round 1: 1 VOCABULARY ("seat") - applied 2 EDITs (lead sentence and bullet heading say magistrate); round 2: 1 VOCABULARY ("seat" in the l7r-bounties gloss) - applied 1 EDIT ("names no magistracy")
CHECKED record-format 0218 - round 1 and round 2: 2 of 2 words, 0/0/0 - nothing
CHECKED translation-check 0218.drawing#tokushima-yashikigami - 3 pairs FAITHFUL - nothing
CHECKED source-applicability kotobank-koka-shunju - APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED source-applicability l7r-bounties - APPLICABLE, limits OVERSTATED 1, RESTATES 1 - applied 1 EDIT (limits now name the waystations and the bulletin to local authorities, and that a gate board is these maps' placing)
CHECKED source-reader 0101#tajima-2007-night-soil - 5 READ - nothing
CHECKED source-reader 0190.drawing#l7r-bounties - 6 READ - nothing
CHECKED source-reader 0218.drawing#tokushima-yashikigami - 3 READ, 1 NOT-FOUND ("farm") - applied (the same EDIT as quote-check's)
CHECKED modal-triage (twice, after each round's fixes moved the pages) - round 1: 4 TOUCHES (karo-s-house, notice-board, compound-shrine, sacred-tree); round 2: 3 TOUCHES (notice-board, compound-shrine, sacred-tree), the rest untouched - recorded with make modal-triaged
CHANGED research/questions/0190-notice-boards-kosatsuba.drawing.html
CHANGED research/questions/0190-notice-boards-kosatsuba.drawing.notes.html
CHANGED research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html
CHANGED research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.notes.html
CHANGED research/sources/010-works-cited/37200-l7r-bounties.html
CHANGED (written by make record / make glossary / make record-checked) the record's built outputs and check ledger, as in session 1's list
OPEN modal-depiction sheet/karo-s-house, sheet/notice-board, sheet/compound-shrine, sheet/sacred-tree - triage says TOUCHES (the 0106, 0190 and 0218 drawing changes); pop-ups are another builder's, not checked here
OPEN modal-depiction sheet/armory and the sheet/official-study modal checks - owed before this session (their own text changed), another builder's
OPEN (outside the change) 0190 gmw-tianxia-yamen note, drawing.notes.html and notes.html: JOINED-WRONG, its five passages joined with " and " instead of "; "
OPEN (outside the change) 0218 fuchu-joge-pamphlet-6's HTML comment says the PDF has no text layer; the archived copy has one with both passages and the caption; also fn-1 caption: whether 『』 around 上下町史 is printed needs the rendered PDF
OPEN (outside the change) research/sources/010-works-cited/4950-tokushima-yashikigami.html drops the source's 位 ("about") in "20 m east" twice; source-reader offered "about 20 m east of the homestead"
OPEN (outside the change) 0106 quote-verbatim marks l7r-budgets NOT-READABLE (a link into this project) - the known l7r-* misfire, nothing to fix in the note
