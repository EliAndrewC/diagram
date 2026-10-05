# Brief - feature 319, H1: record conflicts the modal checks found - water widths: canals, ditches and drains. Session 1: write

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

Questions to edit: 0053, 0055, 0060, 0068 (read also: 0031, 0069)

The conflicts, as the checks reported them:

- irrigation-ditch | 250 | g3 | RECORD CONFLICT: 0055 drawing says the map stops at the ~3 ft lateral; 0068/0069 drawing say delivery ditches narrow to 1.2-1.5 ft
- farm-channel | 231 | g3 | gaps: lining, width, end | RECORD CONFLICT: 0031 drawing calls 2.5 ft the narrowest legible water; 0068 sets the floor at 1.5 ft
- pond | 230 | g1 | RECORD CONFLICT: 0053 calls the single outlet a GUESS, 0061's evidence comment a reading | convention: hamlet pond at the fields' foot fed by the drain (0053 drawing records it)
- drainage-ditch: 2/2; 5/5; 5/5; About 247 | RECORD CONFLICT: 0060 vs 0068 convert Hattori drain 0.5-1 m differently (~1.5-3 ft vs ~2-3 ft) | unapplied: Sources lacks keys for 0054, 0055 now on Entry
- bund: 1/1; 1/1; 2/1; About 247 | DRIFT: jori ruled plain a knob (0014 drawing), engine unrolled, no claim mentions jori | RECORD CONFLICT: 0073 says bund ~1 ft tall as history; 0014 says the 1 ft is modern only | RECORD CONFLICT: Hattori 80-150 cm as ~2.5-5 ft (0014) vs ~3-5 ft (0055)
- irrigation-ditch: 0/0; 4/4; 3/3; About 250 | RECORD CONFLICTS: 0053 evidence (ditch beside every paddy a guess) vs 0055 (around 1900, a finding); 0060.drawing (older over-bund form not drawn) vs 0053/0055 drawing (water passes plot to plot below the last ditch); 0060.drawing (supply canal one width) vs 0068/0069 drawing (narrowing 4.5->1.5); 0055.drawing (finest drawn = lateral ~3 ft, ends blunt) vs 0068 (delivery 2.5->1.2 at 1.5 floor) and 0053 (tail tapers to a thread)
- pond: 2/2; 3/3; 4/4; About 235 | DRIFT: 0061 drawing second bank form (mulberry, cudrania) unrolled - every bank bare | RECORD CONFLICT: 0053 drawing calls the foot-of-fields pond a convention; 0060 drawing calls a drain ending in a pond a guess | crop showed a field pond (wrong kind?)

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H1 in progress (0053, 0055, 0060, 0068) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h1-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H1:`), do not push. Your last message is one paragraph.
