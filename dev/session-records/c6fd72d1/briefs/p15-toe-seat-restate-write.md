# Brief - feature 449 T436 (0057, 0031), session 1: write (the wet ground at a fan's foot and the cross-wind seat, restated to what 449 T432 draws; wording only, no search)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or
tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command;
`git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your files
by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file, the `Makefile` or any pop-up
(`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
read by line range; send the lookups you know you need in one message. Touch no question but the two named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0057 and 0031 for feature 449 before starting you. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects none: no new registry key, no search pass. A page over the 20,000-byte prose cap is
SPLIT along its topics, never trimmed (`make question-sizes`); a size edit never drops a claim-bearing word. Every finding
is labeled; no guess is given as a finding. A GUESS about the physical world owes a citation or a dated ABSENCE note
(never a GROUNDS note); a drawing fallback of ours may take a GROUNDS note (`this project's decision`,
`a drawing convention`). Before writing GUESS for a physical figure, search (archive first); if you FIND a figure, write
the finding and report `FOUND` in the handoff.

**An item tag** is EMPTY, inside its `<li>`, just before `</li>`:
`<span class="item" data-item="<slug>" data-label="ATTESTED|GUESS|CONVENTION|DEVIATION" data-guess="<what is guessed>: <why no page says>"></span>`.
The block's own visible words must carry the label (a GUESS block holds the word GUESS; a convention the word convention).
Each new GUESS below takes its OWN `<li>` and its own tag: never fold a guess into a block that already carries a tag.
Do NOT change any existing tag's `data-item`, `data-label` or `data-guess` (the pop-ups that cite it would owe checks).

## Why this session

449 T432 (landed 2026-11-25) changed the code these pages describe: the drawn wet ground at a fan's foot now runs
between the fields' two lower corners (plus 90 ft each side, the shoulder past a corner held at that corner's level) and no
longer climbs a side of the fields that narrows downhill; a hamlet whose land falls square across its wind now finds that
windward side DRY and seats on it, back square to the wind, as any hamlet does. Over 41,000 swept rolls none takes the
band's-end exit; one valley roll (seed 508, 20 households) still takes the windward corner at the head of its fields
(the head's tier). The claims round found these pages now say what the code no longer draws. This is wording only: NO
search pass, no new source, no new registry key. The code is the authority for what is drawn: read the T432 handoff
`/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T432-add2f1cd653fd388a.md` (its "Rule as built" and the four
formerly refused rolls) and the claims in `rust/phases/src/driver/toe.rs` (`toe_band`, `span`, `Corners`) and
`rust/phases/src/seat.rs` (`open_at_an_end`) - read only, never edit them.

**Stated exceptions to the tag rule above** (mirrored in the check brief): in S1 you change the `data-label` and the
`data-guess` of the existing tag `toe-on-tapering-flank` (keep its `data-item`: `toe.rs` cites it), and in S4 the
`data-guess` of `seat-astride-brook-windward-corner` (keep its `data-item` and its label: `seat.rs` cites it). Nothing
else's tag changes.

## Your items

- **S1 `0057` drawing page: the narrowing side** (`research/questions/0057-marshes-and-wetlands-shitchi.drawing.html`,
  line 13, the block "Where the fields narrow inward downhill, the wet ground climbs their side.", tag
  `toe-on-tapering-flank`, now DEVIATION). Rewrite it to what is drawn: where the fields narrow inward downhill, the wet
  ground does NOT climb their side - it runs between the fields' two lower corners, its upper edge just below the lowest
  field at each point between them, as the pages read put a fan's springs at its toe and its sides among the ground
  cleared early (keep that sentence's existing footnote and link). Its label becomes the label of a finding followed: the
  block's visible words and `data-label` say so (ATTESTED, the citation it already carries; if you judge the drawing rule
  itself to be our reading of that finding rather than the finding, CONVENTION with a GROUNDS note - say which in the
  handoff). Restate the `data-guess` to match, or drop the attribute if the label no longer guesses. Drop the sentences
  that describe the climbing side and "drawing it so is easier than cutting the marsh off"; keep "A house, a cluster and
  a track keep off it as off the rest of the marsh" and its link to 0031 only if S4's wording still matches it.
- **S2 `0057` drawing page: past a corner** - a NEW `<li>` after S1's, its own tag
  `data-item="toe-shoulder-past-corner" data-label="UNRESEARCHED" data-guess="<what>: not yet searched (449 T432)"`:
  past each lower corner the marsh runs on 90 ft more, its edge held at that corner's level. UNRESEARCHED is the fifth
  label (451 T236; `research/CLAUDE.md`): a choice not yet searched, no source or absence note owed; the block's visible
  words say "unresearched".
- **S3 `0057` drawing page: the width** (line 6, the opening account, "It is as wide as the fields above it, with 90 ft
  more on each side"; line 8, the block heading "The marsh is as wide as the fields above it, with 90 ft more on each
  side." and its body): say the marsh is as wide as the fields' foot, from one lower corner to the other, with 90 ft more on
  each side; if a sentence of that block says the dry fields round the fan's plots set the width, restate it to the fields'
  foot (the paddy fan's own corners - T432's code takes the width from the paddy fan alone). Keep every footnote and tag;
  the tag on that block keeps its id and label.
- **S4 `0031` drawing page: the seat on a cross-wind fall**
  (`research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`, line 31, the block "Where the
  land falls square across the wind and its windward side is wet, the cluster sits astride the brook.", tag
  `seat-astride-brook-windward-corner`, GUESS). Its premise (a wet windward side) no longer happens on a fan: restate it
  so that a hamlet whose land falls square across its wind seats on its dry windward side, back square to the wind, like
  any other, and only where every site beside its fields is refused takes the windward corner at the head of its fields,
  its houses on both banks of the brook, its track leaving by the open bank (the GUESS stays a GUESS, its reasons kept;
  restate its `data-guess` without "its windward flank wet"). Update the trailing comment's figure to T432's (0 of 41,000
  rolls take the band's-end exit; the head corner taken by one valley roll, seed 508 at 20 households, measured
  2026-11-25). Also bring line 3's Evidence comment in line ("the seat astride the brook on a wet windward side" -> "the
  seat astride the brook where every site is refused").
- **S5 `0031` drawing page: a fall into the wind** (line 30, the block "Where does a village's cluster sit?", the
  sentence on a declared fall INTO the wind and the back to the hill). The round arbiter's wording, 2026-11-25
  (`specs/449-rust-codebase/arbiter.jsonl`, subject `449-T432-plan-round3`): the cluster turns its back to the hill only
  "once no margin facing the wind is left" - a wind-facing margin comes first (the seat order of 449 T261/T423). Add that
  clause where the sentence says the back goes to the hill; change nothing else in the block.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p15-toe-seat-restate-write.md`: `- SECTION=0057 0031`
   (plus any split page), one line per item `S<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
