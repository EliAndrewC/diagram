<!-- page-load: kind=assertions -->
# Brief - feature 444 T16, the brook's drawn width. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** T16's claims round set a hamlet's brook at 5.25 ft (`BROOK_DRAWN_W` in
`l7r/diagram/hamletgen/water/brook_rules.py`; the Rust field draws it so), from 0068's drawing page: "a village creek at roughly
three and a half times the 1.5 ft floor", narrower than the 6.0 ft head race it feeds. Two other drawing pages, and two map
pop-ups, still give the brook as 7 ft wide - the old drawn width. Make them all state the one figure; and record one
figure on 0087's (item 5). Drawing pages and pop-ups
only - no finding page, no new research; the code stays as it is.

## Your items

1. 0059's drawing page (`research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html`):
   "at a brook 7 ft wide a weir reaching halfway across would be a pixel or two" - the brook about 5.25 ft wide (0068's drawn
   width); keep the sentence's point.
2. 0035's drawing page (`research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html`): "A brook 7 ft wide,
   which the hamlet draws its water from, is in between" - about 5.25 ft, as 0068 draws it.
3. The pop-up `l7r/diagram/interactive/assets/modals/hamlet/stream.md`, its guess "Its width, about 7 ft (2 m)" - about 5.25 ft
   (1.6 m), still a guess, drawn narrower than the 6.0 ft head race it feeds and about three and a half times the 1.5 ft floor
   (0068's drawing page).
4. The pop-up `l7r/diagram/interactive/assets/modals/hamlet/weir.md`: "across a brook about 7 ft wide" - about 5.25 ft.

5. 0087's drawing page (`research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html`), where it says a deck
   runs "about 10 ft past the water onto dry ground at each bank" and that the 10 ft is a GUESS: add the seat's floor the code
   holds a carried deck to (`CARRIED_LANDING_FLOOR_FT` in `l7r/diagram/settlement/_geom/ways.py`, read by
   `bridges.crossing_deck`): a deck sized for about 10 ft along it at each bank is seated where every corner stands at least
   6 ft clear of the water, the floor of that "about" - a GUESS, as the 10 ft is. (The round arbiter's ruling
   ask:444-T16-claims-round4: the page gives one figure and the code holds a second; the page states both.)

Check whether anything else on these four says 7 ft of the brook, and whether any other drawing page or hamlet pop-up does
(a search for `7 ft` near `brook` or `stream`), and fix those the same way; say in the handoff what you found.

## The procedure (session W: write)

1. `make research-claim Q="0059 0035 0087" FEATURE=444`.
2. Edit the fragments and pop-ups, then `make record && make citations` and the record tests; `make quick`'s question-size check
   passes (its one known failure, `tests/hamletgen/test_pool_261.py::test_every_bamboo_stand_is_on_the_sheet[kashikawa]`, is the
   field session's). Commit with messages opening `444 T16: `.
3. Append to `specs/444-work-budget-program/briefs/t16-brookw-handoff.md` (with `make append`) a `## Session W` section: each block
   or pop-up changed (`- SECTION=<NNNN>/<id>` or the pop-up's path) and its anchor.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
