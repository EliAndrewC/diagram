# Brief - feature 291 (how many sides a homestead grove takes), group R5: what the maps now draw round a grove farm, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Once the dispersed and linear forms rolled again, the engine had to make a grove farm workable: lanes
must reach every door, and the farm's own sheds and rooms must stand on its plot, not in its grove. Four things the
record says, or does not say, no longer match what the maps draw. Every figure below is the engine's
(`settlement/rolling/dispersed.py`, `hamletgen/homesteads/`), each a physical necessity at a width no page gives, so
each is a GUESS and says why:

- **The way in through a four-sided grove is about 36 ft wide, not about 12.** A lane is routed, and the router keeps
  a footpath's clearance plus most of its planning cell off each band; at 12 ft no route fit through (cohort seed 12:
  14 of 17 farms left with no way to their door). No old page gives an opening's width.
- **Neighbors' groves stand at least 32 ft apart** - a lane's room between two farms. Packed tighter, the bands walled
  off every front and the lanes could reach no door. No page gives the gap between two groves.
- **The windward stand stands about 24 ft off the house** - off its back wall and off its windward end - a service strip
  where the wood shed stands a step off the wall and the bath room is joined at the stable end. Hard against the walls,
  the stand took those seats (on one map every bath room stood inside the grove). Where on the plot a wood shed stood no
  page says; the strip is sized to the shed.
- **A farm with its own grove carries its household bamboo in that grove** (no separate bamboo strip beside the house),
  and **no village belt is drawn where the farms carry their own groves** (the GM's ruling of 2026-09-29, already
  recorded in `vegetation/030`); a **linear** hamlet's farms front a street laid along the road, the row as long as its
  households.

## Your items (four questions; no new source, no new registry key)

- **homesteads/715** ("Which sides of the house did a homestead grove take?"): change the way in from "about 12 ft" to
  about 36 ft, with the reason (a routed lane's clearance; still a GUESS); add, as GUESSes with their reasons, the 24 ft
  service strip off the back wall and the windward end, and the 32 ft between two farms' groves. Keep the 17 ft thin
  band as it stands.
- **vegetation/620** ("How did a lane get through a belt?"): the same way-in figure, "about 12 ft" to about 36 ft, the
  reason in a clause, pointing at homesteads/715.
- **homesteads/150** ("Does a hamlet have to be nucleated at all?"): one or two sentences - where the farms carry their
  own groves (the dispersed and linear forms) no village belt is drawn, pointing at `vegetation/030`; and in the LINEAR
  section, that the farms front a street laid along the road, the row as long as its households (the drawn length a
  GUESS).
- **vegetation/154** ("Did every farmstead keep its own bamboo, and on which side?"): one sentence - a farm drawn with
  its own grove carries its bamboo inside that grove rather than in a strip of its own, which is what the entry's own
  Tonami passage describes (bamboo mixed into the grove); cite that existing note rather than adding one.

Keep every entry under the 20,000-byte question cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"` and `KEY="vegetation"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R5 in progress (homesteads 715 150, vegetation 620 154) | 2026-09-29"`.
2. Read the four fragments and their notes in one message; edit the fragments (never the assembled pages).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r5-handoff.md` (one `- SECTION=<page>/<id>` line per entry and a
   sentence each), commit only your files (message beginning `291 R5:`), do not push. Your last message is one paragraph.
