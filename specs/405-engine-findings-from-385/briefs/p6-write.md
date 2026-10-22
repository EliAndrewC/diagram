# Brief - feature 405, page session 6: write (0035, 0246, 0084, a new house-lot question)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The research record's
`CLAUDE.md` applies to you above all. Research only: edit no engine code, modal, sheet or canon. Commit each change with a
message opening `405: `. Do not push. Sessions 1-5 edited 0246, 0081, 0014, 0284 before you (`p-handoff.md`).

**What is asked.** Items the engine's claims checks found silent or ambiguous on drawing pages, and one finding to put in
the record. Every statement you add is labeled as the drawing pages label (historically accurate, deliberate deviation, map
drawing convention, guess). Where an item needs a fact the record does not hold, run a search pass (the `research-pass`
agent) first; where it stays silent, write a GUESS and say what was searched. Keep edits to the paragraphs an item touches.

## Your items

- **`0035`** (`research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html`):
  1. (405 T123) The page implies but never states that a way crosses water only at a crossing place (its plank bridges; a
     crossing place every 160 ft or so). Several engine claims cite it for exactly that: state it in one sentence.
  2. (405 T122) Say what a track running past the settlement (the track out, a field spur) does where no crossing place
     lies on its line: the engine drops the spur (recorded), takes the dry exit for the track out, or keeps the far part of
     the track - label it (a map drawing convention, or a GUESS).
  3. (405 T122) The page sets what a crossing costs (about 150 ft of walk) but not how many crossings one way may make; the
     engine lets a fallback route make no more crossings than the run it replaces - record that as the page's GUESS.
- **`0246`** (its drawing page):
  4. (405 T122) The 7 ft gap is measured from another household's garden fence; say whether a track passing outside the
     cluster keeps the same 7 ft off a house wall, a byre or a threshing yard (the engine applies it to every homestead
     part: a map drawing convention, or a GUESS).
- **`0084`** (its drawing page) with 0035:
  5. (405 T110) 0084 says how a way's deck is drawn but not whether a way prefers going round a ditch to crossing it, while
     0035 prices a brook crossing at about 150 ft of walk: run a search pass on when a farm path crosses a ditch rather
     than going round it, and record what it finds (or a GUESS); and reconcile the two pages where 0035 draws a way's brook
     crossing as the board bridge a farm ditch takes (about 4 ft) while 0084 gives a way a timber deck as wide as the way -
     say which applies where.
- **A new question** (405 T112) - how big a clustered village's house lot was: `make reserve` its number (tag it beside 0031,
  the clustered and scattered villages page), with its intro. Write the findings of the spacing pass of 2026-10-22 from
  `specs/405-engine-findings-from-385/spacing-research.md` (its sources are archived: read each passage on its page before
  citing it), with the SILENT lines and their leads. Do not change the engine's figures; say on the drawing side, labeled,
  where the engine's homestead ground (104 ft square, about 305 tsubo) and seating ground (162 ft, about 735 tsubo with the
  wood floor) stand against the lots found.

## When you are done

Run `make record` and the record tests once, fix what fails, and commit. Append one line per item to
`specs/405-engine-findings-from-385/briefs/p-handoff.md` with `make append`, then a last line `STILL OWED:` naming
anything left. Your last message is one paragraph.
