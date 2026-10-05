# Brief - feature 319, H14: drawing conventions on the sheets - wall stroke, latrine fill, the boatmen's altar. Session 1: write

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

Questions to edit: 0092, 0218

The conflicts, as the checks reported them:

- 0092 drawing: the compound wall's dark stroke color has no convention line; record it as a map drawing convention (the record gives no earth wall's color)
- the sheets' latrine glyph is a gray-filled square with a dark outline; no drawing page records the gray as a convention or what it stands for - record it on the drawing page that covers a compound's latrine (find it: grep the drawing pages for latrine/privy at a compound; 0092 if none)
- the Hayakawa boatmen's altar's red fill (#A03020) is described on no drawing page as a convention or as the real color - record it on 0218.drawing (the compound shrine and its altars)

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H14 in progress (0092, 0218) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h14-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H14:`), do not push. Your last message is one paragraph.
