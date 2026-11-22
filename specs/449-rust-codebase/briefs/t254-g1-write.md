# Brief - feature 449 tasks T254, T255, T256, T257, group G1 (households, the farmstead, the headman's house), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, Makefile, docs/ and Python deletions); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit `docs/building-programs.md`, any `Research:` claim, `dev/claims-index.json`, any `pool/` file,
or any pop-up but `hamlet/farmhouse.md` - the orchestrator does the claims and the other pop-ups. Do not run `make claims-*`.
Read narrowly: grep with `-o` and a short context, `make notes Q=<NNNN> KEYS=<k,k>`, read by line range; send the
lookups you know you need in one message.

First: `make research-claim Q="0004 0028 0030" FEATURE=449` (release with `STATUS=done` at the end).

## Your items

No new registry key should be needed; if one is, `make reserve` it.

- G1.1 (T255) **0004's main page** (`research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html`):
  (a) line 7 opens "The median household (*ie*) in the setting these maps are drawn for is five people" - a demographic
  count, where the house style's caste rule wants "five inhabitants" or "five members" (only samurai are "people"; the
  quotation of the GM's notes keeps its own words). Reword it. Then grep all of 0004's pages (main, drawing, their notes)
  for any other demographic "people" and fix each the same way.
  (b) the bullet "A retired couple often kept their own meals and purse" says "the two households often kept separate
  meals and purses - one family living as two households", where its note `kotobank-inkyo-2` says "meals and economy are
  often separate as well, forming several households within one family". Restate the sentence to what the note says.
- G1.2 (T254) **0028's findings page** (`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html`): the
  sizes of a retirement house stand only on the drawing page's bullet "How big was a retirement house, and where did it
  stand?" (`...0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html` line 23, notes `kakimochi-inkyo-share`,
  `kakimochi-inkyo-size`, `kakimochi-inkyo-rows`, `bunka-yokota-jutaku`, `nagano-shishi-yokota-inkyo`,
  `inkyo-gap-absence`). Move the findings (the 1885 count, the 3 to 15 tsubo, the middling 9 tsubo, the table's rows,
  the 1820 Yokota retirement house, where it stood, and the absence of a distance) onto the findings page as a bullet of
  its own, with their notes in its `.notes.html` (copy each note entry exactly; the originals follow by `make record`).
  The drawing page keeps only what the map draws from it, pointing to the findings bullet in a short sentence (a
  drawing page states the map's rules; read its neighbors). The findings page's prose is near the 20,000-byte cap
  (`make question-sizes`): if it goes over, tighten the moved bullet first, then the page's own wording, never dropping a
  finding. The two retirement-house pop-ups already name the findings page in their `Entry:`; do not edit them.
- G1.3 (T257) **0030's tsubo note** (`research/questions/0030-the-headmans-house-and-the-rich-farmers-homestead-shoya-gono.notes.html`,
  note on `shakkanho-jawiki`): `make quote-verbatim Q=0030 NOTES=shakkanho-jawiki` reports DIFFERS on its original
  「1坪（歩）= 10合 = 400/121平米 ≒ 3.305785 m²」. The archived page (`make archive-find KEY=shakkanho-jawiki`, its
  `served.html`) reads 「1坪（歩）」 in one cell and 「= 10 合」, 「= 400/121平米[5]」, 「≒ 3.305785 m<sup>2</sup>」 in the
  next; the "1" was there (the report's window cut it), and the orchestrator has made the checker fold a superscript
  digit to its digit. What is left is the page's space before the first "=". Restate the original to the page's text
  (「1坪（歩） = 10合 = ...」; leave out the reference marker [5], which the record's quotations never carry) and its English
  translation to match if it changes; run `make quote-verbatim Q=0030 NOTES=shakkanho-jawiki` until it reads VERBATIM
  (or DIFFERS with only `[only the page's reference markers differ]`). Check the same note on 0030's drawing notes too.
- G1.4 (T256) **The farmhouse pop-up** (`l7r/diagram/interactive/assets/modals/hamlet/farmhouse.md` line 13) says the old
  couple, "once they had handed the farm to their heir, often moved out to a retirement house of their own". No page
  in the record (0004, 0028, 0029; grep shows no "headship" or 家督) says the farm was handed over. Narrow the clause
  to what 0004's paragraph "A household did not always keep to one roof" now says (moving out was the main form of
  retirement; most retirement houses stood within the house plot, with an entrance of their own), keeping the regions
  sentence. Follow `dev/modals.md` (read only its About rules). Do not run the modal checks; session 2 does.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="median household|five|retire"` (the GM's quotation keeps its words).
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>` for every source before any
   fetch. A page read goes through `make source-pages OUT=/tmp/l7r-check/t254-g1-pages URL=<u> QUESTION=<NNNN>
   SOUGHT="<what>"` and its outcome through `make source-outcome`. These items should need no new source.
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and the four labels by the
   record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no page of yours over 20,000 bytes of prose).
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t254-g1-handoff.md`: one line per changed question as
   `- SECTION=<NNNN>`, one per changed pop-up as `- MODAL=<kind>/<name>`, one line per item
   `G1.<n> <DONE|NARROWED|LEFT> - <what the record now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph
   saying what you wrote.
