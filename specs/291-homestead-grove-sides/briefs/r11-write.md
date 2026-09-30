<!-- page-load: kind=assertions -->
# Brief - feature 291 (how many sides a homestead grove takes), group R11: vegetation/154's as-built lines, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** A settlement-review of Inashiro (2026-09-30) found vegetation/154 ("Did every farmstead keep its own
bamboo, and on which side?") saying the map does what it does not:
- It says the side is "weighted toward the back of the house and the shed's side", and its as-built note gives
  back 0.45 / shed side 0.30 / windward 0.15 / other flank 0.10. The engine's table
  (`hamletgen/homesteads/bamboo.py` `_HOUSEHOLD_BAMBOO_SIDES`) is back 0.35 / windward 0.30 / shed side 0.25 / other
  flank 0.10 - each weight a GUESS, as the entry already labels the roll.
- It says the strip stands "most often behind the house or beside the shed; on Inashiro 3 of 15 farmsteads keep one".
  The current Inashiro draws 8 of 15, 6 at the windward north-west corner and 2 on the far flank: every shed there stands
  on the house's north side, so the back and the shed seats are one place, and a strip refused there takes the windward
  corner next (measured on the pool map's manifest and render, 2026-09-30).
- New with feature 291: a farm with its own grove that rolled a stand keeps it IN its grove - a patch 22 x 16 ft of
  culms on the house side of each windward band (`settlement/homestead_parts/groves.py` `GROVE_BAMBOO_PATCH_FT`, the
  household strip's size, a GUESS; each windward band because the Tonami grove held bamboo "from the west round to the
  north", which the entry's sources may already carry).

## Your items (one question; no new registry key)

- vegetation/154: bring its map-facing lines in line with the engine as above - the weights, the as-built count on
  Inashiro, and the patch in a farm's grove - each value in its class. Change no finding.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="vegetation"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R11 in progress (vegetation 154) | 2026-09-30"`.
2. Read the fragment and its notes; edit the fragment (never the assembled page).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. Write `specs/291-homestead-grove-sides/briefs/r11-handoff.md` (one `- SECTION=vegetation/154` line and a sentence),
   commit only your files (message beginning `291 R11:`), do not push. Your last message is one paragraph.
