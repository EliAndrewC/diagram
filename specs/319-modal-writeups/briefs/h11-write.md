# Brief - feature 319, H11: graves, wells, the dike-top row and the water town. Session 1: write

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

Questions to edit: 0236, 0028, 0019, 0082 (read also: 0008, 0238, 0033)

The conflicts, as the checks reported them:

- 0236/0008 drawing pages: the corner field grave is drawn clear of any ditch or path along its edge, and the bund is carried round the mound to the corner (the code does both, claims IN-STEP) - neither drawing page records either; add both to how our maps draw it
- 0236/0238: the hamlets' dead burned at the main village's cremation ground is on the drawing pages only (from canon); add it to the question page 0236 (canon, no citation)
- 0028 drawing says the maps' wells are shared ones, not one to a farm; 0033 drawing rolls a row's water own (a well at every farm) or shared at even odds - make 0028.drawing say the shared well holds except where a row village rolls its own
- 0019 drawing: the dike-top row's three rules the engine follows (each house on a widened stretch of crest, no house over a sluice notch, no yard or garden on the crest - settlement/land/dikes.py dike_top_houses, UNRESEARCHED) are on no drawing page; record them as how our maps draw it, each a guess where no source says so
- water town: no drawing page records how a water town is drawn (houses alternating bank to bank, evenly spaced, beside their fields - settlement seeds waterfront_seeds, UNRESEARCHED); add a section to 0082.drawing stating it, as a guess
- 0236: the country monk performing a hamlet's funerary rites (canon) is on 0236's drawing page only; put it on the question page (canon, no citation)

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H11 in progress (0236, 0028, 0019, 0082) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h11-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H11:`), do not push. Your last message is one paragraph.
