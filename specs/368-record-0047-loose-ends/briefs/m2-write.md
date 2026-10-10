# Brief - feature 368, the privy record's loose ends and two of 0006's. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What the GM asked** (2026-10-10): take up a filed research feature and fix five defects the record checks found.
Research features annotate the record; they change no map and no code.

## Your items (two questions; no new registry key expected)

- **0047** (`research/questions/0047-farm-privies-and-their-night-soil-benjo.*`):
  1. **The privy figures** (`.drawing.html`). Replace the page's figures with today's, from
     `specs/368-record-0047-loose-ends/measure/privy-reach.txt` (read it; do not re-run). Today, at the `48 ft` reach,
     the five pool hamlets seat 72 privies: 34 (47.2%) in the sunny-side sector, none nearer another house than its own,
     19 beyond 45 ft. State the method as the script does: privies only, not manure pits; distance center to center,
     which is NOT the engine's own reach (that runs from the privy's far corner to the house's walls); the bearing in the
     house's own frame, from its front, not the compass; the sector 112.5 to 202.5 degrees with a half-degree tolerance
     at its edges. Keep the August table (48, 58 and 66 ft, its 48 ft row included) WHOLE, as one dated set (feature
     152's acceptance review, 2026-08-29) apart from today's figures, as the history of why the reach is 48 ft; do not
     set it beside today's rows. The 72 ft run behind "15 of 86" has no surviving record: mark it an unrecorded August
     run, or drop it. Every statement of the share - the lead paragraph's "fewer than half", the table, the paragraph
     and the "how often on the sunny side" bullet - agrees with today's figures.
  2. **One quotation spelled two ways.** `wang-ochiai-2022-5` reads "earthfloored" in `.drawing.notes.html` and
     "earth-floored" in `.notes.html`. Read the paper (Kyoto repository PDF, p.2242; `make archive-find` first) and set
     both copies to the paper's own spelling.
  3. **"Type V1"** (`.notes.html`, `wang-ochiai-2022-2`). Gloss it from the paper's own definition where it stands, or
     cut the quotation at its "..." so the label drops out.
- **0006** (`research/questions/0006-dry-fields-and-their-crops-hatake.html` and `.drawing.html`):
  4. **Point to the row village's holdings.** Its visible text tells every dry plot as the hem and says "No grain plot
     is drawn beside a house"; add a visible clause pointing to 0033's holdings
     (`research/questions/0033-row-villages-resson.html`), so a reader following the farm-holding modal's link is not
     told the holding is ruled out.
  5. **The dry plot's outline** (`.drawing.html`). Every dry plot is drawn with a tan-brown stroke (`#A98C58`, 1.4 px:
     `l7r/diagram/settlement/fields/comb.py`, the dry-crop polygon), the seam between two plots included. Read that code
     and the plot builder (`l7r/diagram/waterfields/carve.py`, `_dry_fields`) and record what the stroke stands for at
     the outer edge (a field edge) and at the seam between two plots (a balk, or a path), and whether it is drawn wider
     than real - a map drawing convention, labeled as one.

Keep each question under the 20,000-byte cap. Change nothing else, and edit no modal, sheet or code.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0047 0006"`. If another session holds either, stop and say so in your handoff. Else
   `make research-claim Q="0047 0006" FEATURE=368`.
2. Read each page and its notes; for the paper, `make archive-find URL=<u>` first (the archive before the web; ask it one
   term at a time), then `make source-pages`, then the `source-reader` agent from a bundle on the passages you change.
3. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit each item or pair of items with a message opening `368: `.
4. Write `specs/368-record-0047-loose-ends/briefs/m2-handoff.md`: one `- SECTION=0047/<id>` or `- SECTION=0006/<id>` line
   per changed question, then a sentence. Release the claim (`make research-claim Q="0047 0006" FEATURE=368 STATUS=done`).
   Do not push. Your last message is one paragraph.
