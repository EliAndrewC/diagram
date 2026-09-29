# Brief - feature 291 (how many sides a homestead grove takes), group R3: the drawn depth of the windward stand, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What is wrong.** The R1 check of this feature left one item open: `homesteads/010` ("Homestead groves (yashikirin) -
the real scale and prevalence") says "How DEEP the belt is has no firm number in the record, so the drawn arm depth
(13 ft, one to two crowns) is a GUESS", and `homesteads/715` says the thinner band on the sides away from the wind is
one tree deep, 17 ft - so the record now has the windward stand drawn SHALLOWER than the thin band, and 13 ft is less
than one crown (a crown is ~17 ft across). What the maps actually draw, from the engine:

- On a scripted map (every map the generator makes now), the windward stand is **1.57 house depths deep** - about
  44 ft at the pool's median farmhouse, which is 28 ft deep - sized so the whole grove is about six times the house's
  footprint. The ~6:1 figure is the one the grove's "Historical scale" arithmetic gives in `homesteads/010` itself
  (check what the entry says before relying on it; if it does not state the ratio, state it as the drawing's calibration
  and label it a GUESS resting on that entry's tree counts and crown sizes).
- 13 ft is only the LEAST a crowded farm's windward arm may shrink to on the old house-first drawing path, which no
  scripted map uses.

## Your items

- **homesteads/010**: rewrite the depth sentence to say what the maps draw - the windward stand 1.57 house depths deep
  (about 44 ft at a 28 ft-deep farmhouse, several crowns), sized so the grove is about six times the house; still a
  GUESS, since no page read gives a grove's depth - and that the sides away from the wind, where a settlement's grove
  takes them, are the thinner one-tree band (pointing at "Which sides of the house did a homestead grove take?"). Drop
  the 13 ft figure from the visible text (a code-side floor is not a finding; an HTML comment may keep it for the next
  session). Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R3 in progress (homesteads 010) | 2026-09-29"`.
2. Read the fragment and its notes in one message; edit the fragment (never the assembled page). No new source.
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r3-handoff.md` (`- SECTION=homesteads/010` and a sentence), commit only
   your files (message beginning `291 R3:`), do not push. Your last message is one paragraph.
