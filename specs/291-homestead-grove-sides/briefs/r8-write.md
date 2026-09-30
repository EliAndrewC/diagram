# Brief - feature 291 (how many sides a homestead grove takes), group R8: what the map draws for a dispersed farm's own water, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** The R7 check rewrote homesteads/200 on the Tonami museum's finding (a small channel led into the
house's grounds "in many areas") and left its map paragraph saying the map draws a well and not the channel. The
generator now draws both, as a knob (feature 291 amendment 5; `hamletgen/homesteads/farm_water.py`, `wells.py`):

- **The knob** `farm_water`, rolled per dispersed settlement at even odds (a GUESS), pinnable, recorded on the map:
  `channel` or `well`. The channel is ACCURATE (the museum); that the other areas dug a well is this record's reading, a
  GUESS (the entry already says so).
- **The channel**: led off the nearest drawn supply ditch (a main or a branch, never the drain), or the brook where that
  is nearer - the nearest a map drawing convention; the brook standing for the irrigation water the ditches are fed from,
  this project's reading, a GUESS. A later farm's channel may be led off one already drawn (a map drawing convention: it
  is still the irrigation water, carried on). It runs round the buildings, yards, gardens and the other farms' groves,
  through the farm's own grove into its grounds, and ends in the dooryard a step off the threshing yard (where in the
  dooryard no page read says - a GUESS). Its return to the field is not drawn (a deliberate deviation: no page read says
  where it left the lot). Drawn at the field channel's 2.5 ft bed (a map drawing convention, the legibility floor).
- **The well**, under `well`: in the dooryard, inside its own lot, nearest its work yard and off its way in (as the entry
  now says, a GUESS). A farm no channel can reach draws its own well instead, and the check reports it.

## Your items (one question; no new registry key)

- homesteads/200: rewrite the "On the map" paragraph to say what the map now draws - the knob and its odds, the channel's
  source, course and end, and the well - each value in its class, as above. Change nothing else in the entry.

Keep the entry under the 20,000-byte question cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R8 in progress (homesteads 200) | 2026-09-30"`.
2. Read the fragment and its notes in one message; edit the fragment (never the assembled page).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r8-handoff.md` (one `- SECTION=homesteads/200` line and a sentence),
   commit only your files (message beginning `291 R8:`), do not push. Your last message is one paragraph.
