# Brief - feature 449 T342, T343, T344, T349 (0116, 0101, 0093, 0123), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(including earlier, finished edits in 0101, 0116 and 0123: keep them; edit around them); the orchestrating session
commits your files by name. Touch only the files your items need, and list every file you changed in the handoff.
Never run `scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive
step does what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/`
file, any `docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a
short context, read by line range; send the lookups you know you need in one message. Do not touch any 0088 file.

**Claims.** The orchestrator claimed 0093, 0101, 0113, 0116 and 0123 for this clone (feature 449); `make
research-claims Q="0093 0101 0116 0123"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources say rather than invent.
Where the record is silent, the line says it is this project's GUESS or a map drawing convention, with an absence note
listing what was searched.

## Your items

- **A1 (T343) `0116` drawing page: the kura fire gap and an attached privy.** The bullet "Our maps keep a plaster
  storehouse (kura) about 6-10 ft from its neighbors, as a fire gap." (0116 drawing page, line ~17) says nothing of a
  privy, while the plans let a privy built onto a building's end back a kura or the granary (the county sheet's
  garrison privy backs its granary's south face 0.5 ft off). A research pass on whether a privy and its cesspit were
  kept off a storehouse came back SILENT: read it whole, `.git/l7r-handoffs/T331-pass-privy-storehouse.md` (its T331
  half, lines 3-33). Restate the bullet (or add one beside it) to say the 6-10 ft gap is kept between a kura and the
  buildings round it and does not bind a privy built onto a building, which may back a kura or a granary - this
  project's GUESS on the record's silence. Give it an absence note (`no publicly readable source`, the searches the
  pass lists in a comment, and a visible sentence saying what they found: no plan or rule puts a privy and a storehouse
  together with a distance or a reason). Cite the Zhaijing (宅經) passage the pass found ONLY if you read the page
  yourself and key it with `make reserve` (which archives it); otherwise name it only in the absence note's comment.
- **A2 (T343) `0101` drawing page: the same relation from the privy's side.** `docs/buildings.md` cites
  `0101-privies-setchin.drawing.html` for "privies beside stores - GUESS ... the record silent", but 0101's drawing page
  says nothing of stores. Add one bullet among the placement bullets: a privy built onto a building's end may back a
  storehouse or granary; no page we read keeps a privy or its cesspit off a storehouse's wall - a GUESS. Its footnote
  is the same absence note as A1 (a note key may be repeated in the other page's notes file, as the record does
  elsewhere) or a link to 0116's drawing page's bullet; do not write two different accounts of one search.
- **A3 (T344) `0101` findings heading "The collectors were farmers, who came with carts."** (0101's findings page,
  line ~27; quote-check PARTIAL twice): it makes one instance the general rule. Its passage (`guernica-night-soil-2`)
  says only that a local farmer regularly brought a cart and bought up all the night soil of one communal toilet.
  Restate the heading to what the passage carries (for instance "Collectors came from outside to buy the night soil,
  such as a local farmer with a cart."), and its body to match; change nothing the note quotes.
- **A4 (T344) `0116` drawing page: "A schematic plan tends to scatter a dozen separate labeled pavilions with loose
  ground between them"** (line ~15) has no footnote. Read the bullet and its section: if it means our own earlier
  maps, say so ("Our earlier plans scattered ...") and give it a grounds note (an HTML comment naming the earlier
  sheets or feature it means, as the page's other grounds comments do); if it means plans in general, it needs a
  citation, and with none the sentence goes. And the note `takayama-jinya-jawiki-6`: its passage #2 (the storehouse
  list) supports neither sentence that cites the note (quote-check and source-reader). Drop passage #2 from the note
  in both notes files where the note appears (and its original, if `make record` keeps one), unless one of the citing
  sentences is about the surviving buildings, in which case say which sentence it supports in the note's gloss.
- **A5 (T344) `0123` findings: the Pingyao bullet** (line ~20) names "the imperial encyclopedia" without a link at its
  first mention (UNLINKED-NAME). Link that first mention to the work as the page's notes link it (the Gujin tushu
  jicheng, 古今圖書集成: find its registry key in 0123's notes, e.g. `gujin-tushu-jicheng-juan338-zhwikisource`, and
  link as the page's other named works are linked), and give its romanized name once there.
- **A6 (T349) `0093` drawing page: how the plans draw gate posts.** The bullet "How wide is each form drawn?" (line ~8)
  says a one-bay gate's "posts are drawn about 2 ft square outside the passage, a map drawing convention". Measured
  2026-11-22 on the sheets (3 px = 1 ft): the hand-drawn sheets (ochiba, ubame) draw the main gate's posts 6 by 6 px,
  2 ft square; the generated sheets (county-magistracy-example, ochiba-roundtrip-test) draw every gate's posts 2 ft
  along the wall and about 4.3 ft across it (6 by 13 px), lengthened so they stand 2/3 ft past the 3 ft wall's ink on
  each face; the hand-drawn sheets draw a side gate's posts as dark blocks 4 by 2.7 ft (12 by 8 px), and the wider
  south service gates of ochiba and ubame 5.3 by 4.7 ft (16 by 14 px). Restate the main-gate sentence to the two forms
  (hand-drawn 2 ft square; generated 2 ft along the wall, about 4.3 ft across it, so it reads past the wall's ink), and
  add, beside it, that a side gate's posts are drawn as dark blocks about 2 to 2.7 ft along the wall and about 4 ft
  across it, standing past the wall's ink on both faces - larger than a post would be, so they read at the plan's
  scale: a map drawing convention, no page we read measuring a side gate's post (the page already says no page
  measures a one-bay gate's pillar). Do not state the 16 by 14 px gates' size as a side gate's (another feature is
  ruling on those gates). Update the page's Evidence comment's convention list to match.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t342a-handoff.md`: `- SECTION=0116 0101 0093 0123`, one line per
   item `A1|...|A6 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and
   anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.
