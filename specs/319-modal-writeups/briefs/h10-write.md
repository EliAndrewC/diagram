# Brief - feature 319, H10: record conflicts the modal checks found - the monk's house, the copse, manure jars and heaps. Session 1: write

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

Questions to edit: 0221, 0071, 0023, 0042 (read also: 0229, 0038)

The conflicts, as the checks reported them:

- 0221 (body and drawing) says no small village kuri was measured; 0229 gives one ~12x15 ft (onga-choshi-jiin-4) - read 0229
- 0221 drawing calls keeping the district's registers in the monk's house "this project's choice"; canon (l7r.md, via make canon) makes the country monk responsible for births, deaths, marriages and travel - it is canon, say so (canon needs no citation)
- 0071 drawing says the copse is not held back from yards' and gardens' sun; 0038 drawing keeps every canopy tree, the copse included, 50 ft off; the code follows 0038 - make 0071.drawing agree with 0038
- the fengshui-wood edge planting (afcd-hkbio-8) is only on 0071's drawing page; it belongs on the 0071 question page with its note
- 0023 says no page gives a manure jar's size (and its drawing calls 3.5 ft a guess on that basis); 0042 cites jawiki-koedame for a buried Japanese jar's mouth of 1 to 1.5 m - 0023 says no CHINESE jar's size was found and points to 0042's Japanese figure
- 0042: no absence note for a manure heap's size on the question page; only its .drawing.html says "no page we read measures a heap" - add the absence (what was searched) to 0042's Evidence

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H10 in progress (0221, 0071, 0023, 0042) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h10-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H10:`), do not push. Your last message is one paragraph.
