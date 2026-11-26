# Brief - feature 449 T425 (0005), session 1: write (split the rice-paddy drawing page along its topics - a move - then record the half-row guess)

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
read by line range; send the lookups you know you need in one message. Touch no question but the one named in your
items (and a split page of one, if the size cap needs it).

**Claims.** The orchestrating session claimed 0005 for feature 449 before starting you; the new question you reserve is yours by reserving it. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass is needed for this brief.** It is a MOVE and then one fallback guess. No new registry key.

**Why a split.** The drawing page of the rice-paddy question has 97 bytes of prose under the 20,000-byte cap, and a guess
the field code makes must be recorded on it (the record rule: a guess is recorded on its page). A size edit never
changes or drops a claim-bearing word, and a split is a MOVE (feature 451 T184 and T185; the record's `CLAUDE.md`, "A
question has a size", about lines 80-90: read those lines first). `research/size-limits.json` is empty: no page has a
limit of its own, and this brief proposes none.

**What to move, and why that section.** The page has three topics: how big a basin is, what shape it takes, and how the
rice inside it is drawn. Move the THIRD, whole: the paragraph "Inside its bunds, the paddy shows its rice as shoots,
never in rows. ..." (about line 37), the HTML comment under it, and the list of four blocks under it - "The paddy is
drawn with an unruled scatter of shoots.", "The scatter is a sample of the planting, not each plant.", "The rice among a
polder's fish ponds takes a denser sample.", "Whether the ordinary paddies take the denser sample is left undecided."
It is the one section that carries NO item tag (the size and shape sections hold `patchwork-everywhere-even-western`,
`basin-smaller-than-parcel`, `allow-household-about-nine`, `town-paddies-without-small`, `point-refuse-cut-off`,
`point-refuse-cut-off-2`, which pop-ups cite by page and must not move), no engine claim states anything in it, and it
is a topic a reader asks on its own (about 2,600 bytes). Change NO word of the moved blocks.

**Sizes at the start**: 0005 drawing 19,903 bytes of prose (97 of room); its research page is not touched.

## Cascade expected (for the coordinator; not your work)

- 0005 drawing page (10 pop-ups, 34 claims). The move is followed by the `moved` pointer, so the moved blocks are NOT
  "removed" at triage. SHOULD re-check: `hamlet/paddy` - the one pop-up that states the moved section ("The rice is drawn
  as a loose scatter of shoots in no ruled rows: a sample of the plant[ing]"): its `Drawing:` line must gain the NEW
  page (a pop-up edit, the coordinator's), after which it reads IN-STEP; and the claim `field/lattice.rs`
  `cuts_counted#a half-row between counts` (it says the page is "silent on a row no whole count of such basins fills":
  restated afterward to cite `half-row-between-counts`), perhaps its neighbors `cuts_counted#the basin's length` and
  `ALONG_FT#the basin's length` (the block the new one stands beside). SHOULD clear: the other nine pop-ups
  (`choice/field_archetype--contour_terraces`, `--valley_paddy`, `choice/plot_regularity--grid`, `--organic`,
  `choice/plot_size--large_block`, `--medium`, `--small_irregular`, `--strip`, `hamlet/bund-beans`: none states the
  shoots or a half-row) and the other 31 claims (`driver.rs` x3, `field/build.rs` x1, `field/fan.rs` x6,
  `field/lattice.rs` x15 more, `field/rules.rs` x6: the fan, the comb, the triangles, the arrowhead - no block of
  theirs moves or changes).
- The NEW page: nothing cites it yet; its record checks are the check session's (a new question owes its intro check).

## Your items

- **H1 `0005` drawing page: move the rice-shoots section to a new drawing-only question, then record the half-row guess** (`research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html`; its notes `.drawing.notes.html`).
  1. THE MOVE. Reserve the new question: `make reserve KIND=question KEY="<heading>"` with a heading a reader asks from
     the map, for example "How our maps draw the rice inside a paddy". It is a drawing-only question, as the bund-bends
     question (0284, read its files for the form: a `.drawing.html`, a `.drawing.notes.html`, and no research page) is.
     The new page gets its own `<h2>`, its tags marker filled from `research/tags.json`, an opening account (the moved
     paragraph serves, or one sentence before it), and the four blocks unchanged. A note moves with the sentence that
     cites it; no note lives in two places (see how the record cites a note across pages:
     `grep -rn "data-note=" research/questions | head`). Where the section stood, leave the pointer in the one form the
     triage follows: `<a class="moved" href="<the new page's file name>">` with the new page's title as its text, in a
     short paragraph (the record's `CLAUDE.md` line 87 gives the form; a plain link is refused). If the page's opening
     paragraph or its `Evidence:` comment names the shoots, bring them in line and no further.
  2. THE GUESS, only after `make question-sizes` shows room. Find the block that gives a basin's length along its row
     (26 to 36 ft, a knob rolled for each basin; `grep -n "26 to 36\|36 ft" <the page>`). Add a NEW `<li>` after it:
     where the half of a row between its middle drain and its flank is of a breadth that no whole number of such basins
     fills, the map takes the count nearest the middle of that band and lets the basins run as long as the breadth makes
     them - a little outside 26 to 36 ft - the same count on both halves of the row. A GUESS: a drawing fallback of
     ours, the fan narrowing toward its drain as the page already says; no page read says how a row was divided where
     whole plots did not fit (GROUNDS note, `this project's decision`). Tag:
     `<span class="item" data-item="half-row-between-counts" data-label="GUESS" data-guess="How a row is divided where no whole number of basins 26 to 36 ft long fills it: no page read says; the map takes the nearest count and lets the basins run a little longer or shorter."></span>`.
     If you cannot find the 26 to 36 ft block, say so in the handoff, put the new block at the end of the size section,
     and state the length band in it.
  3. Report in the handoff the new question's number and file names, and the prose size of both pages.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p3b-paddy-split-write.md`: `- SECTION=0005`
   (plus any split page), one line per item `H<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
