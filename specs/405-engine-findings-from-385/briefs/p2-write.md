# Brief - feature 405, page session 2: write (0014, 0043, 0196, the glossary)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The research record's
`CLAUDE.md` applies to you above all. Research only: edit no engine code, modal, sheet or canon. Commit each change with a
message opening `405: `. Do not push. Session 1 (`p1-write.md`) edited 0246 and 0081 before you; leave those alone.

**What is asked.** Small fixes the record's own checks and the engine's claims checks found. Every statement you add is
labeled as the drawing pages label (historically accurate, deliberate deviation, map drawing convention, guess). Keep the
edits small: change only the paragraphs an item touches.

## Your items

- **`0014`** (its `.drawing.html`):
  1. (405 T92) The page states its 6 ft "drawn as joining" for the paddy's edge only; say whether it holds for the dry hem's
     edge too (0081 §56 draws the dry hem; the engine reads the 6 ft the same way for both). If the sources are silent,
     record the engine's reading as the page's GUESS.
  2. (405 T21) The page says "a sector's first and last rows" (the valley fan) with no gloss: add a glossary entry for
     sector, or an inline gloss, from the valley-fan page's own words.
- **`0043`** (its `.drawing.html`):
  3. (405 T25) "How many farmsteads have a wood shed?": "the share chosen at random for each hamlet from its seed" - seed is
     the generator's word; reword it for a reader (the glossary lists a `seed` variant: check its sense first).
- **`0196`** (its notes and drawing notes) and the glossary:
  4. (405 T70) 0196's drawing notes' absence note says the kabu-ido paper "describes the system's documents and their
     dates", a claim from a work it did not read: say only what was read, or cut it. The glossary variant mapping "isotherm"
     to isohyet is wrong, and 0196's notes say "temperature isotherm": fix both so each word means what it says.

## When you are done

Run `make record` and the record tests (`make test-file FILE=tests/research`) once, fix what fails, and commit. Append one
line per item to `specs/405-engine-findings-from-385/briefs/p-handoff.md` with `make append`, then a last line `STILL OWED:`
naming anything left. Your last message is one paragraph.
