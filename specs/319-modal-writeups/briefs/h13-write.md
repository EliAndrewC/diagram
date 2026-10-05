# Brief - feature 319, H13: the court hall, the archive, wells at a samurai house and the first torii. Session 1: write

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

Questions to edit: 0090, 0118, 0220, 0091 (read also: 0099, 0163, 0196, 0222, 0223)

The conflicts, as the checks reported them:

- 0090 drawing says the maps borrow from the yamen the court hall with the litigants' kneeling places because the Japanese record does not describe them, but 0099 records the Edo mats and who sat where, and the sheets follow that Edo arrangement - correct 0090.drawing
- 0090 (and drawing) calls a yamen's records archive a GUESS; 0163 states it as fact citing qing-yamen-tushuo-2 - make 0090 point to 0163
- 0118 calls the Iwahashi house at Kakunodate a middle-ranking samurai family's, 0196 a senior retainer's - settle from the sources
- 0091 says no page places a well in a samurai house's grounds; 0118 places the Aoyagi house's roofed well just inside its gate - correct 0091
- 0220 drawing says the first arch stands at the edge of the shrine's wood; 0222 drawing says where the approach enters the shrine's ground and 0223 drawing says the wood covers only part of the precinct (the Hoshigaoka sheet follows 0222/0223) - correct 0220.drawing

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H13 in progress (0090, 0118, 0220, 0091) | 2026-10-05"`.
2. Read the fragments and their notes; re-read any source you rely on with `make source-pages` and the source-reader agent
   from a bundle, in the FOREGROUND, before a quoted passage changes.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/h13-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 H13:`), do not push. Your last message is one paragraph.
