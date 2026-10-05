# Brief - feature 319, H5: record conflicts the modal checks found - groves, bamboo and reeds. Session 1: write

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

Questions to edit: 0075, 0057, 0077 (read also: 0036, 0039, 0046, 0071, 0074)

The conflicts, as the checks reported them:

- copse | 202 | g2 | RECORD CONFLICT: 0036 drawing says copse has bamboo and fruit trees, 0075 drawing says copse carries no bamboo; map draws crowns only
- copse: 3/3; 2/2; 3/3; About 205 | record conflict 0071/0036 vs 0075 drawing on copse bamboo (already DRIFTED groves.py dooryard mix)
- marsh: 2/2; 2/2; 4/4; About 248 | RECORD CONFLICT: 0057 calls reed cut from wet ground "held in common" a guess; 0074 records thatch fields used in common as accurate
- homestead-bamboo: 0/0; 4/4; 2/2; About 242 | RECORD CONFLICT: 0075 drawing 'the seat behind the house is one no page names' vs 0046 (Gifu bamboo grove behind a house, accurate) and 0039 Bu nongshu 'bamboo behind' | gap: 0075 lacks 0033's Musashino Ogawa south-side bamboo
- woodland-commons: 2/2; 1/1; 4/4; About 249 | DRIFT: 0077 drawing two undrawn forms (straight strip woods of planned dry-upland villages; abandoned-coppice brush) - no claim | RECORD CONFLICT: 0006 "every 10 to 20 years" uncited vs 0077 15-20 and 20-40
- choice bamboo--both: 1/1; 3/3; 2/2; About 206 | RECORD CONFLICT: 0075 "no page gives a share; common not universal" vs 0036 Kashima 1987 every homestead kept bamboo | DRIFT: HOUSEHOLD_BAMBOO_PREVALENCE 3 in 5 vs the record's only count (all) - claims IN-STEP against 0075 alone | labels "each farm"/"shared" overclaim

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H5 in progress (0075, 0057, 0077) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h5-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H5:`), do not push. Your last message is one paragraph.
