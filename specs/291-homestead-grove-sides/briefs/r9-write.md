# Brief - feature 291 (how many sides a homestead grove takes), group R9: one relabel in homesteads/200, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** R8 wrote homesteads/200's map paragraph, and in it: "A later farm's channel may be led off one already
drawn, a map drawing convention: it is still the irrigation water, carried on." The feature's review ruled that the wrong
class: whether a household's water came off a neighbor's channel is a claim about the world, not a way of drawing - a
GUESS, since no page read says whether neighbors shared a channel. Why the map does it, measured 2026-09-30: on a hamlet
whose only irrigation water is the field's head, the farms drew 1 channel in 11 without it and 11 in 11 with it (the
first channel walls the head off from the rest).

## Your items (one question; no new registry key)

- homesteads/200: relabel that sentence a GUESS, with the reason (no page read says whether neighbors shared a channel)
  and why the map does it (a farm the first channel walls off would otherwise go without). Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R9 in progress (homesteads 200) | 2026-09-30"`.
2. Read the fragment; edit the fragment (never the assembled page).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. Write `specs/291-homestead-grove-sides/briefs/r9-handoff.md` (one `- SECTION=homesteads/200` line and a sentence),
   commit only your files (message beginning `291 R9:`), do not push. Your last message is one paragraph.
