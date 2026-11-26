# Brief - feature 449 T425 (0038, 0090, 0001), session 1: write (the small roofed thing's shadow, the notice board's distance from its gate, and a provincial city's count restated to the GM's ruling)

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
read by line range; send the lookups you know you need in one message. Touch no question but the three named in your
items (and a split page of one, if the size cap needs it).


**Claims.** The orchestrating session claimed 0038, 0090 and 0001 for feature 449 before starting you (0090 was already this clone's); if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass is needed for this brief**: its three items record a guess the code already makes, correct a figure
to the one the maps use, and restate a sentence to the GM's ruling. No new registry key is expected.

**Sizes at the start** (prose bytes of room under 20,000): 0038 drawing 1,779; 0090 drawing 2,436; 0001 research 4,448.

**How the record carries a GM ruling** (the record's `CLAUDE.md`, "Written for the reader", rule 2, and the precedent on
the domain-capital drawing page's notes, note `how-our-maps-size-and-lay-out-a-domain-capital`): the visible sentence
states the setting's rule as the setting's, never "the GM ruled"; the ruling, its date and his words go in an HTML
comment beside the sentence; the footnote is a GROUNDS note, `no source is owed: this project's decision<!-- the GM's
ruling of <date>, quoted in the comment beside the sentence that rests on it -->`. The GM's campaign notes are canon and
keep their registry link where they still support the sentence they stand under.

## Cascade expected (for the coordinator; not your work)

- 0038 drawing page (19 pop-ups, 15 claims). No pop-up states the six-hour check or a shadow's height (grep: none holds
  "six hours", "six-hour" or "hours of sun"): all 19 SHOULD clear - `choice/bamboo--both`, `choice/bamboo--homestead`,
  `choice/copse_siting--among_the_houses`, `choice/grove_sides--2`, `--3`, `--4`, `choice/harvest_weather--changeable`,
  `choice/row_shelter--sheltered`, `choice/windbreak_belt--conifer_led`, `choice/windbreak_belt--mixed_broadleaf`,
  `hamlet/copse`, `hamlet/garden`, `hamlet/homestead-bamboo`, `hamlet/homestead-grove`, `hamlet/persimmon`,
  `hamlet/pond-bank-tree`, `hamlet/threshing-yard`, `hamlet/windbreak`, `sheet/vegetable-garden`. Claims SHOULD
  re-check, in `rust/mode_a/src/audit/sun.rs`: `SMALL_BUILDING_FT#small roofed thing height` and
  `SMALL_BUILDING_SQFT#small roofed thing area` (they are then restated to cite the page's item `small-roofed-thing-6-ft`),
  and perhaps `BUILDING_FT#building shadow height` (the block beside the new one). SHOULD clear: the other nine `sun.rs`
  claims (`DECL_DEG`, `LAT_DEG`, `SUN_BED_H`, `HALF_SHADE_BED_H`, `LIT_SHARE`, `NOT_STANDING`, `TREE_FT`, `WALL_FT`,
  `lit_areas`), `compound/fixtures.rs` x1 and the two docs claims.
- 0090 drawing page (12 pop-ups, 28 claims). SHOULD re-check: `sheet/notice-board` (the board's own pop-up; it states no
  distance today, so it should come back IN-STEP or gain the 40 ft) and the claim `rust/mode_a/src/compound.rs`
  `NOTICE_BOARD_MAX_FT#board by the gate` (its text quotes the page's "within about 15 ft": it MUST be restated after
  this lands, to `GUESS ...#notice-board-within-40-ft`). SHOULD clear: the other 11 pop-ups (`sheet/compound-wall`,
  `court-divider`, `door`, `family-quarters`, `inner-court`, `kneeling-positions`, `nakamon`, `office-hall`, `outer-court`,
  `residence`, `tax-archive`) and the other 27 claims (plan scale, the two courts, the divider gate, the drawing order).
- 0001 research page (1 pop-up, 2 claims). `choice/cluster_shape--split` cites only: SHOULD clear. Claims in
  `rust/mode_a/src/place.rs`: `kinds#what each tier is` SHOULD re-check (it states what a provincial city's figure
  counts, CANON, feature 156: it should come back IN-STEP, the page now agreeing with it);
  `lane_default#connector leads to the district's village` SHOULD clear. The note `l7r-budgets-4` is also cited from
  0001's drawing page and from three other questions' pages, each through its OWN notes file: none of those files
  changes, so nothing there is owed.

## Your items

- **S1 `0038` drawing page: the small roofed thing in the six-hour check** (`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`; its notes `.drawing.notes.html`).
  The block "The six-hour check casts each shadow at the least height the record gives each thing." (tag
  `six-hour-check-casts`, GUESS: keep the block and its tag as they are) names three heights: a building at the
  farmhouse ridge's 20 ft, a compound wall at about 5 ft, a tree at about 33 ft. The check has a fourth class no page
  records: a roofed thing under 100 sq ft on the plan (a privy, a small wayside shrine, a covered way) casts its shadow
  from 6 ft, taken as the least height a person stands under. Add a NEW `<li>` after that block saying so, labeled a
  GUESS. It is a guess about a built thing's height, so look first: grep the record (the farm-privy question 0047 and the
  small-shrine pages, read only) and the archive (`make archive-find`) for a privy's or a hokora's eave or ridge height;
  if a page read gives one, write the finding with its citation and report `FOUND`; if none, an absence note dated today.
  Tag: `<span class="item" data-item="small-roofed-thing-6-ft" data-label="GUESS" data-guess="That a roofed thing under 100 sq ft casts its shadow from 6 ft: no page read gives the height of a privy, a small shrine or a covered way, and 6 ft is the least a person stands under."></span>`
  (reword the `data-guess` if you find a height).
- **S2 `0090` drawing page: the notice board stands within about 40 ft of a gate, not 15** (`research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html`; its notes `.drawing.notes.html`).
  The block reads "The notice board stands within about 15 ft of a gate in the wall. Our maps put it where people
  pass.", and item 4 of the checklist lower on the page says "it must sit within ~15 ft of a wall gate opening". The maps
  have allowed 40 ft since the boards moved from against the wall to beside the road: a board on the road's far side
  faces its gate across the Imperial road's 30 ft. Restate BOTH places to about 40 ft, give the reason in the block (a
  board beside the road may stand across it from its gate, and the highway is 30 ft wide), and label the figure a GUESS:
  no source read gives how far from a gate a board stood. Write no history ("was 15", "since feature ...": rule 3; a
  feature number belongs in an HTML comment if anywhere). Before writing GUESS, grep this question's research page and
  the highway question 0088's pages (read only) for where a kosatsu stood relative to a gate or a road; cite what is
  there. Tag at the end of the block's `<li>`:
  `<span class="item" data-item="notice-board-within-40-ft" data-label="GUESS" data-guess="That a notice board stands within about 40 ft of a gate: no source read gives the distance; 40 ft lets a board beside the road face its gate across a 30 ft highway."></span>`.
  The distance is a rule of our drawing: a GROUNDS note (`this project's decision`) serves unless you cite a source.
- **S3 `0001` research page: a provincial city's 3,000 include the samurai country estates around it** (`research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html`; its notes `.notes.html`).
  The finding reads: "**A provincial city is a governor's seat of 2,000 to 4,000 inhabitants inside its walls.** That is
  the setting's figure for a provincial city, about 3,000 inhabitants in 600 households in the ordinary case, and it
  counts only those living within the walls." with note `l7r-budgets-4`, which quotes the GM's budget notes: 「counts
  ONLY the population living within the city walls / on the city's footprint proper.」 The GM has since ruled otherwise.
  `docs/gm-rulings.md`, its last section ("A provincial city's 3,000 include the samurai country estates around it
  (2026-11-24)": read it, about ten lines) gives his words: "Yes, the provincial cities 3,000 include the samurai country
  estates around it." Do this:
  - Restate the bold lead and the sentence to the ruling, as the setting's rule: the figure counts the city's
    inhabitants and the samurai country estates around it, and no farmers. Drop "inside its walls" and "counts only
    those living within the walls". Put the ruling - its date, 2026-11-24, and his words verbatim - in an HTML comment
    beside the sentence, and in the same comment say that the two notes files (the campaign notes and the budget notes)
    still carry the older sentence and are the GM's to change. Nothing visible says "the GM ruled", and nothing visible
    tells the page's history.
  - The footnote: the restated clause must NOT rest on `l7r-budgets-4` (its quoted passage says the opposite; a
    quote-check would rightly fail it). Give the clause a GROUNDS note of this page's own, in the form above (this
    project's decision, the GM's ruling of 2026-11-24 in its comment). Keep `l7r-median-domain-6` on the figure if its
    passage still supports "2,000 to 4,000 ... about 3,000" (read the note).
  - The next finding, "A provincial city counts no farmers.", also cites `l7r-budgets-4`, and there the note's third
    passage (the farmers live in the surrounding county) supports it: keep that citation. In THIS page's notes file you
    may narrow the note `l7r-budgets-4` to the passages the farmers finding rests on (the heading and the farmers
    passage), each still verbatim from the budget notes, so the note no longer offers "within the city walls" in support
    of anything; if the finding's HTML comment beside it quotes the walls sentence, bring the comment in line. Do NOT
    edit the drawing page (its block "A walled estate, samurai or merchant, counts as a household like any other."
    already counts "the samurai estates outside a city's wall") nor its notes file.
  - NEVER edit `/host-l7r-repo/setting/l7r.md` or `budgets.md`, nor the registry entry `l7r-budgets`: they are the GM's
    files and a faithful entry on them. This is not a put-back of a check's wording: the evidence is the GM's words.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p5-sheet-write.md`: `- SECTION=0038 0090 0001`
   (plus any split page), one line per item `S<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
