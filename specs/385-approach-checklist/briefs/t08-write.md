# Brief - feature 385 T08, a tail pond's bank, bare or planted. Session 1: write

You are a FRESH session for the record edits of one task. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What is asked** (feature 385 T08, a ranking row of feature 328: "add the pond bank knob: roll the Song manual's sparsely treed
bank (mulberry and cudrania) against the bare bank, drawing its trees"): the maps now roll a hamlet's tail pond's bank between the
two forms 0061 already records - bare, or planted sparsely with mulberry and cudrania (Chen Fu's *Nongshu*, already cited as
`chenfu-nongshu-juanshang`). Bring 0061's DRAWING page in step with what the maps now draw. No new research is asked; edit no
code, modal or sheet.

## What the maps now draw (from the code; the record states it, labeled)

- The bank form is a knob rolled per hamlet whose runoff ends in a pond: bare or planted, at even odds (GUESS: 0061 gives no share).
- A planted bank's trees stand on the bank beyond the reed fringe, about one every 30 ft of bank (GUESS: the manual says only
  "sparsely"), each crown about 12 ft across (GUESS), mulberry and cudrania in turn round the bank (GUESS: the manual names both,
  not their order), the cudrania drawn a shade darker (CONVENTION).
- A tree is left out where its crown would fall on a roof, a wellhead, or a yard's or bed's sun ground, or its trunk on a lane,
  the crop or the water - so a crowded bank carries fewer trees.
- A bare bank is drawn as open ground beyond the reeds, as before.

## Your items (one question)

- **0061** (`research/questions/0061-reservoir-ponds-tameike.drawing.html`): the bullet now headed "A bank with a few trees on
  it is not drawn yet." becomes the knob's own bullet (a heading a reader would ask, for example "Is a pond's bank bare, or
  planted with a few trees?"), stating both forms are rolled and each GUESS and CONVENTION above, labeled, keeping its existing
  footnote to `chenfu-nongshu-juanshang`. Update the page's `<!-- Evidence: ... -->` comment if it lists the bank. Nothing on
  the findings page (`0061-reservoir-ponds-tameike.html`) changes unless a sentence there says the maps draw every bank bare.

Keep the question under the 20,000-byte cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0061"`. If another session holds it, stop and say so in your handoff. Else
   `make research-claim Q="0061" FEATURE=385`.
2. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with a message opening `385: `.
3. Write `specs/385-approach-checklist/briefs/t08-handoff.md`: one `- SECTION=0061/<id>` line per changed heading, then a sentence
   naming what changed. Release the claim (`make research-claim Q="0061" FEATURE=385 STATUS=done`). Do not push. Your last
   message is one paragraph.
