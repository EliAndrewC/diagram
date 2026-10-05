# Brief - feature 319, H8: record conflicts the modal checks found - knobs, plot grain and water reach. Session 1: write

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

Questions to edit: 0031, 0005, 0196, 0033

The conflicts, as the checks reported them:

- farm-channel | 231 | g3 | gaps: lining, width, end | RECORD CONFLICT: 0031 drawing calls 2.5 ft the narrowest legible water; 0068 sets the floor at 1.5 ft
- RECORD vs ENGINE: 0031 drawing says "A hamlet leaves none of these to chance" but hamletgen/plan.py rolls lane_skeleton, cluster_shape, plot_size, grain_drift for every hamlet
- STALE: 0005 drawing gives a hamlet basin ~39 ft (1,488 sq ft); plot_texture docstring (settlement/houses.py) says hamlets stay on the old pixel grain (medium 48 px)
- homestead-bamboo: 0/0; 4/4; 2/2; About 242 | RECORD CONFLICT: 0075 drawing 'the seat behind the house is one no page names' vs 0046 (Gifu bamboo grove behind a house, accurate) and 0039 Bu nongshu 'bamboo behind' | gap: 0075 lacks 0033's Musashino Ogawa south-side bamboo
- well: 1/1; 4/4; 4/4; About 245 | RECORD CONFLICT: 0196 drawing ~380 ft vs 0033 drawing 760 ft water reach (claims DRIFTED already)
- choice footbridge x3 + grain_drift: depiction 2/2 each | DRIFT: grain_drift 0031 drawing tilts the paddy grain; code turns only dry rows (claims IN-STEP misses it) | RECORD CONFLICT: 0084 drawing (one planked deck, convention) vs 0087 drawing (road-bridge form a knob) - DRIFTED already
- 0005 drawing (the patchwork drawn everywhere, never a grid, a deviation) vs 0031 drawing (rectilinear blocks where a survey laid a grid) - settle which the research supports
- 0005 (Shiroyone Senmaida 1,004 paddies ~18 m2) vs 0021 (~800 paddies 18-20 m2) - read also 0021

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H8 in progress (0031, 0005, 0196, 0033) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h8-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H8:`), do not push. Your last message is one paragraph.
