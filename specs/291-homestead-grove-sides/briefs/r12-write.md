# Brief - feature 291 (how many sides a homestead grove takes), group R12: a row farm's holding depth and its grove's face, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** A settlement-review of Kashikawa (2026-09-30), a row village with farms on both sides of a street laid
first, raised two questions the record does not yet answer. Run the research pass on each (search, `make
source-pages`, `source-reader` in the background) before writing anything; where the record stays silent, say what was
searched in an absence note.

1. **How much dry field a row farm held beside its paddy.** The map draws each far-row farm a dry-field strip behind
   it, one lot wide and three lots deep (homesteads/156, the depth a GUESS borrowed from the planned row's form); on
   Kashikawa that is 28.7 acres of dry field against 27.5 of paddy, so the far farms hold about 2.6 acres of dry field
   each on top of their paddy share and the near farms none. What share of a paddy-plain row village's land was dry
   field (hatake) beside the rice, and did it lie behind the house lots? A figure, or a described proportion, from a
   readable page.
2. **Which way a farm's grove faced when its street ran on its windward side.** The map keeps each farm's grove on the
   windward north and west and its open front to the south, whatever side its street is on; a near-row farm with the
   street to its north reaches it by a path round its grove. Did a row farm keep its south front and its windward
   grove with the road behind it, or open the grove to the road? If the record attests both, say so plainly (the
   project makes two attested forms a knob).

## Your items (two questions; new registry keys only for sources you cite, at most ten)

- homesteads/156 (or a new question beside it if the cap requires): what the research found on each point, each claim
  footnoted to a page read, and what the map now draws beside it in its class. Name in your handoff any finding the
  engine should follow (a depth the record supports, a second form of the grove's face).

Keep every entry under the 20,000-byte question cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R12 in progress (homesteads 156) | 2026-09-30"`.
2. The research pass, then read the fragment and its notes; edit fragments (never the assembled page); `make reserve` for a new key.
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r12-handoff.md` (one `- SECTION=<page>/<id>` line per entry, a sentence
   each, and the engine consequence if any), commit only your files (message beginning `291 R12:`), do not push. Your
   last message is one paragraph.
