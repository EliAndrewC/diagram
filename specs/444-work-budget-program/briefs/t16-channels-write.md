<!-- page-load: kind=assertions -->
# Brief - feature 444 T16, the comb's deliveries and their last head. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** The round arbiter's binding ruling on ask:444-T16-channels-claims (`specs/444-work-budget-program/arbiter.jsonl`,
route b): two of our DRAWING pages disagree, so the code's claims cannot close. Edit the drawing pages - no finding page, no new
research - so they state one rule, as below. The code (`rust/phases/src/field/channels.rs`) stays as it is.

## Your items

1. In 0054's drawing page (`research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html`), one block
   qualifying its branch angle (the "A branch is drawn leaving at 35 degrees" passage, about its paragraphs 99-100): the 35 degrees
   is for a branch where no lattice sets the angle, such as the head race off the brook. A delivery ditch leaving a supply canal in
   the comb runs along its row's bund, nearly square to its canal, and is taken only where that bund leans downstream off the flank
   - the lattice's bund sets its angle. Label it as the record labels a drawing decision (a map drawing convention).
2. In 0053's drawing page (`research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html`), point its
   "at right angles" (about its paragraph 4, deliveries leaving the supply canals) at that new 0054 block: nearly square, along the
   row's bund, leaning downstream as the bund does.
3. In 0068's drawing page (`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html`),
   one sentence beside its paragraph 53 ("the cap bites only low in the net, where the canal has already dwindled"): where a canal
   stops at its last offtake, narrowed to its 1.5 ft thread, that last delivery leaves at the 1.2 ft floor and runs flat. Labeled
   a map drawing convention.

## The procedure (session W: write)

1. `make research-claim Q="0053 0054 0068" FEATURE=444`.
2. Edit the fragments, then `make record && make citations` and the record tests; `make quick`'s question-size check passes. Commit
   with messages opening `444 T16: `.
3. Append to `specs/444-work-budget-program/briefs/t16-channels-handoff.md` (with `make append`) a `## Session W` section: each block
   changed (`- SECTION=<NNNN>/<id>`) and its anchor, so the code's claims can cite it.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
