<!-- page-load: kind=assertions -->
# Brief - feature 444 T16, the delivery cap at a canal's first offtake. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** The claims round's impl-drift found `rust/phases/src/field/channels.rs::channels#the delivery's head` DRIFTED
against one sentence of 0068's drawing page. The code holds the page's RULE (a delivery's head capped at 0.8 of its canal's local
width where it leaves it), but the page's description of where the cap bites is wrong. Edit the drawing page only - no finding
page, no new research. The code stays as it is.

## Your item

In 0068's drawing page (`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html`),
the bullet "A delivery ditch is never drawn wider than the canal feeding it." says: "The cap bites only low in the net, where the
canal has already dwindled; at the first offtake the delivery keeps its full rung." That is not so. Each canal tapers in equal
steps from its head to the 1.5 ft thread at its last offtake, so the cap bites wherever the canal is under about 3.1 ft (2.5 ft
over 0.8): low in the net, and at every offtake of a canal that has only one or two. Restate it so, and restore the measured
ranges a comment there says were cut, from this measurement of Inashiro as now generated (`pool/hamlets/inashiro/inashiro.json`,
`field_ditches`, read 2026-11-01):

- canal A, 4.5 ft at its head, in three legs 4.5 -> 3.5 -> 2.5 -> 1.5; its deliveries' heads 2.5 ft (parent 3.5), 2.0 ft (parent 2.5)
  and 1.2 ft (parent 1.5, flat to 1.2 ft);
- canal B, 4.0 ft at its head, one leg 4.0 -> 1.5, stopping at its one offtake; that delivery 1.2 ft flat (parent 1.5);
- so every delivery head 1.2-2.5 ft against a parent of 1.5-3.5 ft, and only canal A's first keeping the full 2.5 ft rung.

Replace the HTML comment that owes the re-measure with the measured sentence. The page sits about 10 bytes under the
20,000-byte prose cap, so trim elsewhere in the same block or bullet to keep it under, or `make quick` refuses the page.

## The procedure (session W: write)

1. `make research-claim Q="0068" FEATURE=444`.
2. Edit the fragment, then `make record && make citations` and the record tests; `make quick`'s question-size check passes (its one
   known failure, `tests/hamletgen/test_pool_261.py::test_every_bamboo_stand_is_on_the_sheet[kashikawa]`, is the field session's).
   Commit with messages opening `444 T16: `.
3. Append to `specs/444-work-budget-program/briefs/t16-offtake-handoff.md` (with `make append`) a `## Session W` section: the
   block changed (`- SECTION=0068/<id>`) and its anchor, so the code's claim can cite it.
4. Release the claim (`STATUS=done`). Do not push. Your last message is one paragraph.
