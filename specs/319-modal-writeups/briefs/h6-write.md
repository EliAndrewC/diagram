# Brief - feature 319, H6: record conflicts the modal checks found - graves and burial grounds. Session 1: write

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

Questions to edit: 0236, 0235, 0226 (read also: 0008)

The conflicts, as the checks reported them:

- grave-island: 3/3; 2/2; 3/3; About 248 | RECORD CONFLICT: 0236 "every placement read is at the bund edge, corner or house plot" vs same page's Fukaya grave mid-field along a road | RECORD CONFLICT: 0235 drawing "never drawn in a flooded field" (burial ground) vs 0008/0236 grave island inside a flooded plot
- choice fry x2, grave x2, burial: ok | DRIFT: 0236 drawing says ~half of hamlet maps draw a farmstead's own grave; no generator draws one | RECORD CONFLICT: 0226 drawing (hamlet burial ground at its edge on a knob) vs 0236 drawing (no hamlet burial ground, GM 2026-09-28) - 0226 out of date

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H6 in progress (0236, 0235, 0226) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h6-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H6:`), do not push. Your last message is one paragraph.
