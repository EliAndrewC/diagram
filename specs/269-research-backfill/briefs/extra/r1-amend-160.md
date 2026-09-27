# Brief - feature 269, group R1 (burial), amendment: where a hamlet's dead lie is a KNOB (religion-and-death 160)

You are a FRESH session. Work in `/diagram/.clones/diagram-supplemental`; the research record's CLAUDE.md applies.
Read `/diagram/.clones/RESEARCH-CLAIMS.md` first. 160 is 269's; 540 is feature 273's (Diagram shrines), so do not edit 540.

## Why

Feature 273 (Diagram shrines, hamlet-graveyards) researched the GM's question of 2026-09-27, whether a hamlet keeps its
own graveyard. Its plan review found the evidence SPLIT: 160's own notes show burial per settlement (a hamlet's sanmai at
its edge; the graveyard a settlement's inhabitants hold in common) and graves on a household's or neighborhood's own
land common until the war; but 273's 540 quotes the danka (parish) obligation to a grave at the parish temple, 271's
500 finds households most often registered with temples OUTSIDE their village, and the two-grave split is mainly Kansai.
Under the GM's rule (two attested forms -> a knob) it is a KNOB per hamlet, at even odds (a guess), written by 273 in
religion-and-death 540 ("Where do a hamlet's dead lie?"): `own_ground` (a burial ground of its own at its edge) or
`village_ground` (its dead lie in the village's ground, by the shrine or apart as 280's knob says).

## What 160 owes

1. **The hamlet clause.** Replace "A hamlet draws none: its dead go to the village district's ground, just as it has no
   shrine and no headman" and the argument before it (the hamlet patch "below the resolution of these maps", "a hamlet
   that draws nothing stays honest") with: "A hamlet's dead lie either in a burial ground of its own at its edge or in
   the village's ground, rolled per hamlet", then the title as plain text with a comment, NOT a link (540 is not in
   this clone): `Where do a hamlet's dead lie? <!-- RELINK 273: religion-and-death/540 -->`. Do NOT write that a hamlet
   keeps its own ground. The 750-2,450 sq ft reckoning of a hamlet's own patch stays, labeled a GUESS as it is; it now
   sizes an `own_ground` hamlet's drawn ground, which is drawable at the hamlet tier (1 ft/px).
2. **The village ground's size, as a function of the population it serves.** It serves the village's own households
   plus those of the hamlets that roll `village_ground`, so it ranges between the village's own ~350 inhabitants and the
   district's ~800. State the band as a RULE in the population served P, by 160's own method (25-30 deaths per 1,000 a
   year, 30-year reuse, 10-20 sq ft a plot: area = P x 0.025-0.030 x 30 x 10-20 sq ft), checked against the 1934 household
   rule the section already cites (1 tsubo a household times 1.5-2 for paths, at ~5 a household). Give it worked at
   P = 350 and P = 800 so the two ends are visible. Remove "it is the district the ground serves" and "a ground sized
   only to the village itself is too small". Keep the ladder's order (village < town). Read 206; if it repeats the
   district band, restate that one sentence the same way.
3. Nothing else in 160 changes.

## Then

- `Read` 160, its notes and 206 in ONE message; `Edit`. In `.claude/skills/diagram`: `make record && make citations`,
  the four record tests (`tests/interactive/test_footnotes.py test_citations.py test_sources.py test_record_format.py`),
  and `python3 scripts/check-question-size.py` from the clone root.
- Check: `make check-bundle PAGE=religion-and-death SECTION=160 FOR=quote-check` and `... FOR=record-format` (and 206
  if edited), both agents in the background in one message; `make apply-edits FROM=<each output_file>`, then by hand
  what it refuses; re-check once what moved.
- Commit, with the message `269 R1 amend: where a hamlet's dead lie is a knob (273's 540); the village ground sized by the
  population it serves`. Do not push.
- Append to `specs/269-research-backfill/briefs/r1-handoff.md`: `B36 AMENDED - a hamlet's burial is a knob (273, 540);
  village ground = <the rule in P> - for 273's generator (funerary.py sizes the village ground by the population it
  serves)`. Your last message is one sentence giving the rule.
