# T254 G3 handoff - session 1 (research and write)

- SECTION=0227

G3.1 DONE - 0227's `kuri-jawiki-3` note (findings notes and drawing notes, the same note on both) restated to the live
ja.wikipedia 庫裏 page (oldid 111301952, last edited 2026-10-07, read 2026-11-22 from the page cache through `make
source-pages`, outcome `cited:kuri-jawiki`). Originals now 「寺院の僧侶が居住する場所であり、寺内の食事を調える台所を兼ねる場合もある。」
and 「大規模な寺院では独立した建物であるが、一般の寺院では寺の事務を扱う寺務所と兼用されていることが多く」 (the second cut at
the clause, the page's sentence going on 「一般の民家によく似た建物も多い。」). The second translation dropped "the kuri"
as its subject (the page's sentence no longer opens 庫裏は) and its closing period; the first translation still fits the
new wording unchanged. No supported sentence's meaning moved, so the prose files (`0227-...garan.html`,
`.drawing.html`) are untouched and 0227's prose size did not grow. `make quote-verbatim Q=0227 NOTES=kuri-jawiki`:
VERBATIM 2 on each page, no DIFFERS or NOT-ON-PAGE. The registry entry `7630-kuri-jawiki.html` quotes
「寺院の僧侶が居住する場所」, still on the page verbatim, so it is not changed (no KEY= line). `make record CHECK=1` and `make
record` clean.

## Files

- research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.notes.html
- research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.originals.html
- research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.drawing.notes.html
- research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.drawing.originals.html
- specs/449-rust-codebase/briefs/t254-g3-handoff.md

## Open

- The record checks (translation-check on the two changed originals, quote-check or its FIXED_BY settlement) are for
  the next session, per the brief; none was run here.
## Session 2 (checks)
CHECKED quote-check 0227#kuri-jawiki-3 + 0227.drawing#kuri-jawiki-3 - 3 READABLE, 3 VERBATIM, 3 SUPPORTS, 0 unfootnoted - nothing
CHECKED record-format 0227 - 12 of 12 prepass words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED translation-check 0227.drawing#kuri-jawiki-3 - 2 pairs FAITHFUL 2 - nothing
CHECKED source-reader kuri-jawiki (0227#kuri-jawiki-3, 0227.drawing#kuri-jawiki-3; also settled 0221's three kuri notes) - 4 READ, 0 NOT-FOUND, 0 CONTRADICTED - nothing
CHECKED modal pop-ups - none owed only because 0227 moved; the sheet/* modal-depiction and triage units record-owed lists come from 0222/0223 (G1/G2) or their own edits - not mine, left
CHANGED none (no edits; make record, make glossary rebuilt generated output only)
OPEN not mine, left: quote-check:0222.drawing#unfootnoted, record-format:0222, 18 sheet/* modal-depiction units (triage or batched bundle) - G1/G2's or another builder's
OPEN none for 0227/kuri-jawiki: record-owed names none of them; quote-verbatim Q=0227 NOTES=kuri-jawiki VERBATIM 2 on each page; claim 0227 released
OPEN correction to the line above: 19 sheet/* modal-depiction units, not 18 (14 triage-first from 0222/0223 drawing pages, 5 batched for their own edits: compound-shrine, hall-and-dwelling, sanctuary, the-monk-s-rooms, wood-kami-altar)
