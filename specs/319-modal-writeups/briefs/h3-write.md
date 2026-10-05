# Brief - feature 319, H3: record conflicts the modal checks found - dike-ponds and polders. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**Why.** Feature 319's modal checks (2026-10-05) compared every map modal with the research record and found places where two
pages of the record - or one page and its own evidence comment or drawing page - say different things. A modal can follow
only one; the record must stop contradicting itself (constitution XIV). Your job is to settle each conflict below IN THE
RECORD: read both sides and their sources, decide what the sources support, and make every page involved say that (a
drawing page states the map's rule and must not contradict its question page; an `Evidence:` comment must match the
assertion it classes; a figure converted twice must convert the same way). Where the sources truly differ, the page says so
plainly; where one side was simply stale, it is corrected. Do NOT change what any map draws, any engine code or any modal
file; where a drawing page's rule turns out to be contradicted by the research, the page says what the research supports and
leaves "how the maps draw it" as a guess or a known gap - never invent a new drawing rule.

## Your items (at most four questions; no new registry key expected)

Questions to edit: 0018, 0019, 0020, 0027 (read also: 0024)

The conflicts, as the checks reported them:

- DRIFT: POND_LAYOUTS=("mosaic",) - grid never rolled, though 0024's Qu Dajun 1678 chessboard supports a premodern grid (record conflict with 0019 drawing; research decides: grid is an attested form the engine does not roll)
- fish-pond: 1/1; 1/1; 3/3; About 236 | RECORD CONFLICT: 0019 drawing says a uniform chessboard of ponds is found only today; 0024 cites Qu Dajun 1678 describing Jiujiang as a chessboard
- mulberry-dike: 1/1; 3/2; 1/1; About 249 | RECORD (like G4): 0018 drawing calls the 6:4 water-heavy split a deliberate deviation though 0018 records both ways round + 7:3 (no GM ruling) -> fix the label; an unrolled two-form knob, DRIFT | gap: 0025 modern dike <=16 ft vs 0018 modern 20-33 ft
- perimeter-dike: 2/2; 2/2; 2/2; About 248 | RECORD CONFLICT: 0027 drawing says no page gives a village polder dike breadth and >18 ft is a convention; 0027 gives Lake Tai margin 10-30 m (33-98 ft) - Depiction "drawn so on purpose" waits on the record fix | no crop
- choice land_use_overlay x4: ok | DRIFT: bund tea a second attested tea form (0020 drawing says knob); no knob rolls it; no claim | RECORD CONFLICT: 0020 bullet calls many small hillside gardens a reading; its Evidence says guess
- 0020's drawing page does not record the `leftover` knob (pond or rice at even odds; `pond` converts every parcel, `rice` keeps about one in ten) that the engine rolls (`hamletgen/consts.py` LEFTOVER_FORMS) - record it as the knob it is, its odds a GUESS

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H3 in progress (0018, 0019, 0020, 0027) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h3-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H3:`), do not push. Your last message is one paragraph.
