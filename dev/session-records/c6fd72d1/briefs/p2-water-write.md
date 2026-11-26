# Brief - feature 449 T425 (0068, 0058, 0072, 0059), session 1: write (four small corrections on the water pages: a table cell, "built on", an unquoted page in a note, and the brook's line below its intake)

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
read by line range; send the lookups you know you need in one message. Touch no question but the four named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0068, 0058, 0072 and 0059 for feature 449 before starting you (0059 was already this clone's); if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects none. A page over the 20,000-byte prose cap is
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

**No research pass is needed for this brief**: three small restatements and one guess the code already makes. No new
registry key is expected.

**Sizes at the start** (prose bytes of room under 20,000) - two of these pages are FULL, so count every byte: 0068 drawing
19; 0058 drawing 11,164; 0072 drawing 14 and research 32 (you touch neither page's prose, only the two notes files, which
are not counted); 0059 drawing 5,765.

## Cascade expected (for the coordinator; not your work)

- 0068 drawing page (7 pop-ups, 15 claims). One table cell changes ("along the far edge" to "down the brook's flank").
  SHOULD re-check: `hamlet/irrigation-ditch` (states "two supply canals, one along each high flank") and the claim
  `field/channels.rs` `SUPPLY_W#supply canals`; at most also `field/polder.rs` `ditches#the far flank`. SHOULD clear:
  `choice/intake--open`, `choice/settlement_form--dispersed`, `choice/water_sink--offmap`, `choice/water_sink--pond`,
  `hamlet/drainage-ditch`, `hamlet/stream`, and the other 13 claims (the widths' ladder is unchanged).
- 0058 drawing page (7 pop-ups, 3 claims). SHOULD re-check: the claim `seat/margins.rs` `ranked#not on the wet toe` (the page will now agree with it: IN-STEP).
  SHOULD clear: `hamlet/marsh` (it states the 90 ft, which does not change, and not "built on"), the six `choice/cluster_position--*` pop-ups (`flank`, `high_margin`, `mid_margin`, `on_rise`,
  `valley_head`, `valley_mouth`: none holds "built on") and `ranked#not in the reed fringe`,
  `ranked#no drain rule at the seat`.
- 0072 (notes files only, both halves; pop-ups 8 + 7, claims 1 + 14). No pop-up holds "northeasterly" or "East Asian
  Monsoon": ALL should clear at triage, and no claim should be owed (the pages' prose does not change).
- 0059 drawing page (16 pop-ups, 20 claims). SHOULD re-check: the claim `field/brook.rs` `brook#the tap's stride` (it says
  the page is "silent on how far below a shoulder intake the brook keeps its line": restated afterward to cite the new
  item) and perhaps `brook#the shoulder intake`; pop-ups `choice/intake_place--shoulder` and `hamlet/stream` (they
  describe the brook below a shoulder intake; neither gives a distance, so IN-STEP is expected). SHOULD clear: the other
  14 pop-ups (`choice/intake--open`, `--weir`, `choice/intake_place--center`, `choice/intake_siting--bend`, `--straight`,
  the three `choice/water_source_position--head_*`, the four `choice/weir_form--*`, `hamlet/irrigation-ditch`,
  `hamlet/weir`) and the other 18 claims.

## Your items

- **W1 `0068` drawing page: the supply canal runs down the brook's flank** (`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html`).
  One table row reads `<tr><td>supply canal along the far edge</td><td>4.0 -&gt; 1.5</td><td>branch dwindling to lateral</td></tr>`.
  The canal that starts 4.0 ft wide is the one down the BROOK's flank (the head race's side); the other flank is the one
  the valley-floor ditch question calls far. Change the first cell to "supply canal down the brook's flank". THE PAGE HAS
  19 BYTES OF ROOM: this reword costs 4. Add no comment, no tag, no sentence. If `make question-sizes` lists the page,
  undo nothing: report it and the count.
- **W2 `0058` drawing page: the strip under the lowest fields is farmed, not built on** (`research/questions/0058-ground-too-wet-to-build-on.drawing.html`).
  The block "A well is kept off the ground below the fields' lowest point, not off the whole drawn marsh." says: "The
  drawn marsh reaches about 90 ft up the slope from the foot of the fields, its reeds tucked under the lowest fields (...),
  so that strip is farmed and built on, with no reeds showing. Keeping wells off the whole drawn marsh would refuse every
  well standing there." "Built on" is untrue: the maps treat a wet band reaching about 90 ft above the lowest field as too
  wet to build on, and refuse the settlement's seat where its center lies inside it. Restate "farmed and built on" to
  "farmed". Then read the block's last sentence and its lead against that fact and against the page's other blocks: keep
  the wells' rule as the page's rule, but leave no sentence asserting that the strip is built on. Write no new rule for wells or houses that the page
  does not already give. Change as
  few words as do it; no new source; say in the handoff exactly which sentences moved.
- **W3 `0072` notes files: the unquoted page named in a parenthesis** (`research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.notes.html` and `.drawing.notes.html`).
  In BOTH files the note `kisetsufu-jawiki` ends its closing parenthesis with "; en.wikipedia East Asian Monsoon gives
  the continental winter wind as northeasterly)" - a page named, not linked, not quoted. Either drop that clause (the
  default), or cite the page properly: find it in the registry or the archive (`make archive-find`), read it, and quote
  the sentence verbatim under its key in the record's form. Do not touch either PAGE's prose (14 and 32 bytes of room).
- **W4 `0059` drawing page: how far the brook keeps its line below a shoulder intake** (`research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html`; its notes `.drawing.notes.html`).
  The block "Does the brook bend or run straight where it is tapped?" records the bend-or-straight knob only. The maps
  also hold the brook to the intake's line for about 70 ft below an intake standing on a shoulder of the fan, before the
  brook takes its own course down the flank; no page records that. Add a NEW `<li>` after that block, labeled a GUESS: a
  figure of ours for the drawing, since no source read says how far below an intake a brook kept its line (a GROUNDS
  note, `this project's decision`, unless your grep of this question's research page finds a passage on the reach below an
  intake - then cite it and report `FOUND`). Tag:
  `<span class="item" data-item="brook-line-below-intake" data-label="GUESS" data-guess="That the brook keeps the intake's line for about 70 ft below a shoulder intake: no page read says how far below an intake a brook held its course."></span>`.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p2-water-write.md`: `- SECTION=0068 0058 0072 0059`
   (plus any split page), one line per item `W<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
