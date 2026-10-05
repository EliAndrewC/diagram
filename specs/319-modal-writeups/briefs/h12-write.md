# Brief - feature 319, H12: drains, polder lines, the garden pond and the clerks. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
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

Questions to edit: 0060, 0022, 0103, 0113 (read also: 0068, 0014, 0091)

The conflicts, as the checks reported them:

- 0060 drawing: the drawn odds of the drain going off the map (about one time in three) and the sink pond's size (~3% of the paddy, hamletgen/sink.py lay_sink pond area) are on no drawing page; record both as guesses
- 0060 drawing draws a drain's head about 1.5 ft wide, 0068's table gives 1.2 ft - check whether 319 H1 (commit ef3d0b182) already settled it; make them agree
- 0022 drawing says a polder's module lines run straight and hold their line; 0014 drawing says each row and column line takes its own gentle bow up to a tenth of the grid's spacing (the engine's grid_lines wobble) - settle which the research supports and make both say it
- 0103 drawing treats a garden pond as the grander form because both offices known to have one were far grander than a county post, but 0091 records a pond at a 150-koku district magistrate's house (Yokota, Matsushiro) - re-price the reasoning
- 0113 classes three or four clerks as this project's guess, and its Evidence comment lists the figure under both setting-canon and guess; canon (budgets.md, Heimen clerks ~3-4) gives it - say it is canon

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H12 in progress (0060, 0022, 0103, 0113) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h12-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H12:`), do not push. Your last message is one paragraph.
