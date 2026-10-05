# Brief - feature 319, H9: record conflicts the modal checks found - cells, gatehouse, byre, lanes. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html-3`); the project's CLAUDE.md files apply to you, the research record's
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

Questions to edit: 0090, 0093, 0048, 0081 (read also: 0096, 0116)

The conflicts, as the checks reported them:

- 0090 drawing scale bullet still says "A cell is 23 by 17 ft"; 0096 and compound.py give 12x10 (stale) - read also 0096
- 0093 says Takayama's gatehouse size "was not found"; 0116's takayama-jinya-gifu note lists the gatehouse at 36.98 m2 (~400 sq ft); 0093's ~40 ft guess to re-price against it
- 0048 drawing keeps every byre ~16x11 ft ("a beast or two") but has one shared shed serve four or five households - make the drawing page consistent (a shared shed's size is then a guess, or larger)
- 0081 says no page gives a measured lane width, yet it cites the Manchu village's 2-4 m alleys - say what was measured and where (and that no wet-rice village lane was measured)
- 0081 drawing says only that a back lane "runs behind the plots, parallel to the main lane"; record how the hamlet engine lays the back lane since feature 318's gap-laid ways (read hamletgen/ways for lane_web=back_lane; describe, do not change it)

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H9 in progress (0090, 0093, 0048, 0081) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h9-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H9:`), do not push. Your last message is one paragraph.
