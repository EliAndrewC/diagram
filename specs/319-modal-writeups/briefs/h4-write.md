# Brief - feature 319, H4: record conflicts the modal checks found - the farmstead's fixtures. Session 1: write

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

Questions to edit: 0023, 0028, 0045, 0006 (read also: 0042, 0043, 0049, 0039, 0077)

The conflicts, as the checks reported them:

- manure-heap | 244 | g5 | gaps: heap size, place, share of farms | RECORD CONFLICT: 0023 says no page gives a manure jar's size; 0042 cites jawiki-koedame for a mouth of 1-1.5 m
- manure-heap: 3/3; 2/2; 2/2; About 227 | RECORD CONFLICT: 0042 jar mouth 1-1.5 m vs 0023 "no page gives its size"
- hen-coop: 0/0; 4/4; 1/1; About 227 | RECORD CONFLICT: 0045 drawing 'accounts before 1912 agree chickens were that common' vs 0045 'Probably' | 0045 drawing coop place a guess vs 0049 Hakka rear ring
- soy: 2/2; 3/3; 1/1; About 249 | RECORD CONFLICT: 0006 "no page puts grain or beans in a plot at its house" vs 0039 Kanto front field grew soybeans
- wood-shed: 3/3; 1/1; 2/2; About 206 | RECORD CONFLICT: 0028 drawing fixtures bullet "the firewood stack", 14 of 15 woodpiles vs 0043 and 0028's first bullet: ~4 farms in 10 a wood shed, no stack drawn
- woodland-commons: 2/2; 1/1; 4/4; About 249 | DRIFT: 0077 drawing two undrawn forms (straight strip woods of planned dry-upland villages; abandoned-coppice brush) - no claim | RECORD CONFLICT: 0006 "every 10 to 20 years" uncited vs 0077 15-20 and 20-40

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H4 in progress (0023, 0028, 0045, 0006) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h4-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H4:`), do not push. Your last message is one paragraph.
