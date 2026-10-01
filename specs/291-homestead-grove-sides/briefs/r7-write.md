# Brief - feature 291 (how many sides a homestead grove takes), group R7: what the maps draw for a row village and a farm's own well, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What moved.** The generator now draws the row village the record found (R6), and a dispersed farm's own well. The
record must say what the maps draw, each number in its class (accurate / deviation / convention / guess) with its reason.
No new research is asked for - these are the map's own values beside findings the entries already hold. What the engine
draws (feature 291; `hamletgen/homesteads/rows.py`, `ways/street.py`, `homesteads/wells.py`):

- **The line** a row follows is set by the ground where it can be: flood-prone ground (reclaimed low ground behind
  dikes, or houses on a dike) takes the DIKE line; elsewhere the two attested lines - a street laid first, drawn
  straight, and the dry edge, drawn curving with the field's margin, which stands for a levee, dike or fan foot (this
  project's reading) - are rolled at even odds (a GUESS: the record gives no count).
- **The sides**: one side of the street (the field across it) or both, rolled at even odds (a GUESS).
- **The spacing**: farms stand one farmstead frame apart - the farm's grove and ground plus the lane's room between two
  groves - lot against lot; a physical necessity, since a grove farm cannot stand on a narrower lot; its width a GUESS at
  or just past the top of the record's 9-40 ken range.
- **The street** runs about 24 ft off the dry edge (a map drawing convention: near enough that the field reads as the
  row's own, clear enough that the street is not on a bund), drawn a rank wider than the lanes off it (a 6 ft tread, a
  convention); the connector carries it on out of the map as the road the row stands on. It is placed on the stretch of
  the dry edge within a row's length of the settlement's seat that holds the most farms (the project's method).
- **More streets**: a row the line cannot hold grows further streets parallel to the first, each with its row, never
  ranks behind a row (homesteads/156); at most six (a GUESS).
- **The far row's holding** (both sides only): on a street laid first a strip behind the farm, one lot wide and three
  lots deep, cut in plots about 150 ft deep (the depth a GUESS - a paddy row borrows the planned row's form, not its 375
  ken; the plot size a convention); on the dry edge one lot deep, compact and near the house (accurate for a dike row,
  homesteads/156; carried to a levee or fan foot as this project's reading). Drawn as dry field (the crop a GUESS).
- **A row's water**: each farm its own well, or wells shared along the street - one at the middle of each stretch of the
  row no longer than 1.6 times the watering reach (760 ft), so every farm is within reach of one - rolled at even odds (a
  GUESS: the record rules on the dispersed farm only; Santome's few deep shared wells on a water-poor upland do not
  transfer).
- **A dispersed farm's own well** (homesteads/200) stands in its dooryard, inside its own lot, nearest its work yard
  and off its way in (where on the plot no page read says - a GUESS).

## Your items (three questions; no new registry key)

- 0033: in its map section, the line: set by the ground where the generator knows it (flood-prone ground takes
  the dike), otherwise the two attested lines rolled at even odds (a GUESS); the sides at even odds (a GUESS).
- homesteads/156: in its map section, the drawn values above - spacing, street offset and tread, the road it runs out on,
  the further streets and their cap, the far row's holding in each line's form with its depth and plots, the row's water
  knob and the shared wells' spacing - each in its class.
- homesteads/200: one or two sentences - where the map draws the dispersed farm's own well, a GUESS.

Keep every entry under the 20,000-byte question cap (split by topic if one would pass it). Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R7 in progress (0033 156 200) | 2026-09-29"`.
2. Read the three fragments and their notes in one message; edit the fragments (never the assembled pages).
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r7-handoff.md` (one `- SECTION=<page>/<id>` line per entry and a
   sentence each), commit only your files (message beginning `291 R7:`), do not push. Your last message is one paragraph.
