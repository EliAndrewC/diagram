# Brief - feature 269, group R1 (burial), amendment: a hamlet keeps its own burial ground (religion-and-death 160)

You are a FRESH session. Work in `/diagram/.clones/diagram-supplemental`; the research record's CLAUDE.md applies.
Read `/diagram/.clones/RESEARCH-CLAIMS.md` first. 160 is 269's; 540 is feature 273's (Diagram shrines), so do not edit 540.

## Why

Feature 273 (Diagram shrines, hamlet-graveyards) researched the GM's question of 2026-09-27, whether a hamlet keeps its
own graveyard, and found every source pointing one way: a hamlet buries at its OWN edge. The GM's rule for that case
(as 273 reports it): "if everything points in one direction ... go with the one that is correct". The evidence is
largely already in 160's own notes: Edo Japan buried per settlement (a hamlet's sanmai at its edge; the graveyard a
settlement's own inhabitants hold in common); the two-grave system put the burial grave on common land by the
settlement; ja.wikipedia's 墓 has graves on one's own land or a neighborhood group's as common until the war; and Ming-Qing
China scattered family graves through the farmland. Nothing read sends a hamlet's dead to a central ground. 273 writes
religion-and-death 540, "Where do a hamlet's dead lie?", and its generator draws a burial ground at every hamlet's edge.

## What 160 owes

1. **The hamlet clause.** Replace "A hamlet draws none: its dead go to the village district's ground, just as it has no
   shrine and no headman" and the argument before it (the hamlet patch "below the resolution of these maps", "a
   hamlet that draws nothing stays honest") with: a hamlet keeps its own burial ground at its edge, citing the notes
   160 already holds. Name 273's question as a plain title with a comment, NOT a link (540 is not in this clone yet):
   `Where do a hamlet's dead lie? <!-- RELINK 273: religion-and-death/540 -->`. The 750-2,450 sq ft reckoning of a
   hamlet's own patch stays, labeled a GUESS as it is. It now sizes the hamlet's drawn ground, and it is drawable at
   the hamlet tier (1 ft/px).
2. **The village ground's size.** It no longer serves the district, only the village's own households. Restate the
   band from the village's own ~350 inhabitants by 160's own method (25-30 deaths per 1,000 a year, 30-year reuse,
   10-20 sq ft a plot), and check it against the 1934 household rule the section already cites (1 tsubo a household
   times 1.5-2 for paths). Remove "it is the district the ground serves" and "a ground sized only to the village itself is
   too small". Keep the ladder's order (village < town), stated as it now runs. Also restate 206's figure if 206
   repeats the district band (read 206; edit only the band sentence).
3. Nothing else in 160 changes.

## Then

- `Read` 160, its notes and 206 in ONE message; `Edit`. In `.claude/skills/diagram`: `make record && make citations`,
  the four record tests (`tests/interactive/test_footnotes.py test_citations.py test_sources.py test_record_format.py`),
  and `python3 scripts/check-question-size.py` from the clone root.
- Check: `make check-bundle PAGE=religion-and-death SECTION=160 FOR=quote-check` and `... FOR=record-format` (and 206
  if edited), both agents in the background in one message; `make apply-edits FROM=<each output_file>`, then by hand
  what it refuses; re-check once what moved.
- Commit, with the message `269 R1 amend: a hamlet keeps its own burial ground (273's finding); the village ground sized
  to the village`. Do not push.
- Append to `specs/269-research-backfill/briefs/r1-handoff.md`: `B36 AMENDED - hamlet keeps its own ground (273, 540);
  village band now <new band> - for 273's generator (funerary.py sizes the village ground by it)`. Your last message is
  one sentence giving the new band.
