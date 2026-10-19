# Brief - feature 385 T10, round 2: all five recorded splits, and what T10 made stale. Session 1: write

You are a FRESH session for the record edits of one task. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What changed in the maps since the last session** (feature 385 T10, D74b): the dike-pond split knob now rolls all FIVE forms
0018 records, not three - six of water to four of dike, six of dike to four of pond, seven of water to three of dike, one to one
(the modern working paper, where the mulberry alone feeds the fish), and the gazetteer office's three-to-seven read in the order it
names (three parts water to seven of dike) - at even odds (GUESS). Each pond's inset is derived from the rolled share on the
village's median parcel (GUESS: one inset to a village). Kuwabata now rolls three parts water to seven of dike: its inset is about
42 ft. Edit no code. The five title-card pop-ups (`l7r/diagram/interactive/assets/modals/choice/dikepond_split--*.md`) were
written from the checked six-to-four text and are in step with this.

## Your items (two questions, and the pop-ups the round arbiter named)

- **0018** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html`): the account the
  last session wrote names three rolled splits; it names all five now, labeled, with the 1:1 and three-to-seven forms' own sources
  and the page's caveat that a split written water-to-dike does not by itself fix which side comes first.
- **0027** (`research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html`): its "23 ft
  crop dikes" (and any other sentence fixing a dike-pond bank at 23 ft) is stale - the bank is now whatever the rolled split leaves.
  Restate it from 0018. **Settle the bank-width finding** the last check left: the manual 0027 cites gives 5-10 m only to dikes that
  carry sheds or traffic, and Kuwabata's banks carry pig sties. Say, from 0018 and 0027, whether a bank seating a sty falls under
  that wider dike - and if the drawn bank (now about 42 ft on Kuwabata, about 15 ft at the seven-to-three split) falls outside what
  the record gives, write that plainly as a finding (it is for the engine to follow, not for you to fix).
- **The pop-ups whose Guesses still say "six in ten" or "23 ft"** (the round arbiter named `field_archetype`, `land_use_overlay`
  and the fish pond; find each with `grep -rln "six in ten\|23 ft" l7r/diagram/interactive/assets/modals/`): rewrite each such
  Guess from 0018 to the rolled split. Edit only those sentences.

Keep each question under the 20,000-byte cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0018 0027"`. If another session holds one, stop and say so in your handoff. Else
   `make research-claim Q="0018 0027" FEATURE=385`.
2. Edit the fragments (never a built page) and the pop-ups, then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with a message opening `385: `.
3. Write `specs/385-approach-checklist/briefs/t10b-handoff.md`: one `- SECTION=<q>/<id>` line per changed heading, the pop-ups you
   edited, and a sentence on the bank-width finding. Release the claims (`make research-claim Q="0018 0027" FEATURE=385
   STATUS=done`). Do not push. Your last message is one paragraph.
