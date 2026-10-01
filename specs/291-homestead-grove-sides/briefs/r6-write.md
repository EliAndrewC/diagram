# Brief - feature 291 (how many sides a homestead grove takes), group R6: how a row village was laid out, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**Why this question.** The generator rolls a hamlet's form - nucleated, dispersed or LINEAR - and every farm of a
dispersed or linear hamlet now carries its own homestead grove, which makes a farmstead some 240 ft across. The
linear form was drawn as a row along the field's edge; on a 20-household map that edge holds only 3 farms, and the rest
stood in ranks behind - a block, not a row. The GM (2026-09-29): what it should look like "should be based on our
research ... find out from our research what types of settlement layouts existed, and then have our settlements reflect
the range ... if our research is thin ... make a tunable knob for the various possibilities". So the engine will draw
the row forms the record finds, rolled per settlement where it finds more than one - and it needs the record to say
what they were.

**What the record already has** (read, do not repeat): the homesteads question "Why does one village look nothing like the next?" names the attested nucleated shapes - houses
in a lump, in a line along a natural levee or a spring line at a hill's foot, in a line along a road; the towns question on a town's built edge
defines the road village (路村, houses along a road living mainly by farming) against the street village (街村, living
by traffic); the archetypes question "Were most villages clustered or scattered?" says the Kanto and northeast villages were loosely clustered, each house on a wide lot
with its own grove, set well apart; the homesteads question "Does a hamlet have to be nucleated at all?" rests, in its LINEAR section, mostly on the German Reihendorf and calls
the Japanese evidence thin; the source `santome-shinden-jawiki` (sources page) gives the planned new-field colony -
farmhouses along both sides of a road, each farm's field and woodlot in an equal strip behind it, 40 ken of frontage
- but is a tertiary stub whose figures want a citing work.

## Your items (no more than ten new registry keys)

- R61 (new, homesteads page): **"How was a row village laid out?"** - see below.
- homesteads/150: one or two sentences in its LINEAR section pointing at R61 (below).

**R61, "How was a row village laid out?"** - for a Japanese farming settlement strung in a line (路村 rosen, 列村/列状村
retsujoson, 新田集落 shinden villages, levee and hill-foot lines; East Asian parallels where the Japanese record is
silent, marked as such):

1. **Along what** - a road, a natural levee, a spring line at a hill's foot, a canal or a field's edge - and whether
   the line or the houses came first.
2. **One side or both** - did the farms stand on one side of the line (the field on the other) or on both sides of a
   street, with their holdings behind them?
3. **Spacing and frontage** - how wide a farm's frontage along the line, how far apart the houses; the Santome 40 ken
   (and any other colony's figure) from a work that cites a source; whether the row was continuous or broken.
4. **Where the fields lay** - behind each house in a strip, across the line, or as one block beside the row.
5. **How long, how many** - a row's length or household count, and whether a long row doubled back or grew a second
   row.
6. **The homestead grove in a row** - did row-village farms keep their own yashikirin (the Musashino shinden's
   keyaki and kashi are the obvious case), on which side of the house relative to the line?

Run the search pass (Japanese and English: kotobank 路村, 列村, 新田集落, 三富新田, 武蔵野 新田 短冊, 自然堤防 集落,
Reihendorf/Waldhufendorf only as comparison); read what you cite through `source-reader`; record each finding with its
class (accurate / deviation / convention / guess), and where the record supports more than one FORM say so plainly -
those become a rolled knob. End the entry with **"What it means for a map"**: the forms a row village may take, each
with the numbers it rests on, and which numbers are GUESSes.

For homesteads/150, update its LINEAR section with one or two sentences pointing at the new question (its "thin"
verdict stands or falls with what you find).

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R6 in progress (homesteads: how a row village was laid out; 150) | 2026-09-29"`.
2. The search pass and the reads as the record's `CLAUDE.md` says (`make source-pages`, `source-reader` in the
   background, `make source-outcome`, `make reserve` for each new key, `source-applicability` before a figure becomes a
   rule). A source only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`.
3. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/291-homestead-grove-sides/briefs/r6-handoff.md`: one `- SECTION=<page>/<id>` line per entry touched,
   the new keys, and - most important - a short list **FORMS:** of the row layouts the record now supports, each with
   its numbers and class. Commit only your files (message beginning `291 R6:`), do not push. Your last message is one
   paragraph.
