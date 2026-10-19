# Brief - feature 385 T10, a dike-pond village's water and dike split, rolled. Session 1: write

You are a FRESH session for the record edits of one task. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What is asked** (feature 385 T10, a ranking row of feature 328: "roll the dike-pond inset per village between the recorded
splits (water-heavy, dike-heavy, 7:3)"): the maps now roll a dike-pond village's split between the three forms 0018 already
records, and derive each pond's inset from it. Bring 0018's DRAWING page in step with what the maps now draw. No new research
is asked; edit no code, modal or sheet.

## What the maps now draw (from the code; the record states it, labeled)

- The split is a knob rolled per village: six parts water to four of dike, four of water to six of dike, or seven of water to
  three of dike - at even odds (GUESS: no share given).
- Each pond is set in from its parcel's edge so that a parcel of the village's middling size (the median by area) is the rolled
  share water - one inset for the whole village (GUESS: a smaller parcel runs a little drier, a larger a little wetter). On
  Kuwabata, which rolls seven to three, the median parcel draws 0.70 water, the parcels 0.56 to 0.80.
- The planted bank fills the ring between pond and canal at the inset the split gives; the mulberry rows and the pig sty on the
  bank follow it.

## Your items (one question)

- **0018** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html`): the bullet
  headed "A pond's parcel is drawn about six parts in ten water." (each pond set 23 ft in) and the sentence "With more than one
  form recorded, the split would be rolled village by village; our maps draw only the water-heavy order, so the dike-heavy order
  and the seven-to-three split are a known gap." become the knob's own account: the three splits rolled, the inset derived from the
  rolled share on the village's median parcel, each GUESS labeled. Keep every existing footnote that still applies; update the
  page's `<!-- Evidence: ... -->` comment if it lists the split. The findings page changes only where it says the maps draw one
  split.

Keep the question under the 20,000-byte cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0018"`. If another session holds it, stop and say so in your handoff. Else
   `make research-claim Q="0018" FEATURE=385`.
2. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with a message opening `385: `.
3. Write `specs/385-approach-checklist/briefs/t10-handoff.md`: one `- SECTION=0018/<id>` line per changed heading, then a sentence
   naming what changed. Release the claim (`make research-claim Q="0018" FEATURE=385 STATUS=done`). Do not push. Your last
   message is one paragraph.
