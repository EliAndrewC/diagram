# Brief - feature 449 T425 (0284, 0014, 0008), session 1: write (guesses the paddy code makes that no page records: a comb bund's bow, the beans on a bund, and the rice-field pond's host plot and bank)

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

**Claims.** The orchestrating session claimed 0284, 0014 and 0008 for feature 449 before starting you; if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass was run for this brief**: its items record guesses the field code already makes and no page states.
Most are drawing fallbacks of ours (GROUNDS notes). THREE are physical figures about beans on a bund (item B2): for
those you search before writing GUESS (archive first, `make archive-find TERMS="畦豆|あぜ豆|azemame"`; then the web in
Japanese and Chinese if the archive is silent). No new registry key is expected unless that search finds a figure.

**Left alone on purpose.** 0014's RESEARCH page (12 bytes under the cap: write nothing on it - a finding the search
turns up goes on the drawing page with its citation, and the handoff says the research page is owed it). On 0008's
drawing page the tag `much-pond-open-water` keeps its `data-guess` exactly (it already records the pond's proportions
and its reed belt: add nothing about the reeds). The rice-paddy question's drawing page (0005) is another session's: its
half-row guess is NOT in this brief.

**Sizes at the start** (prose bytes of room under 20,000): 0284 drawing 9,574; 0014 drawing 8,271; 0008 drawing 12,549.

## Cascade expected (for the coordinator; not your work)

Every item ADDS a guess beside blocks that stand.

- 0284 drawing page (2 pop-ups, 0 claims). SHOULD clear: `choice/plot_regularity--organic` and `hamlet/bund` (neither
  states how far a bund bows). No claim cites this page today; afterward the claims `field/lattice.rs` `BOW#the bund's
  bow` and `Lines.new#the bund's bow` (which cite the rice-paddy drawing page) can cite the new item `comb-bund-bow`.
- 0014 drawing page (5 pop-ups, 13 claims). SHOULD re-check: `hamlet/bund-beans` (it says "how many beads the map sets
  along a bund is a guess" and "a round bead about 3 ft across, in a single row on some o[f the bunds]": IN-STEP
  expected, or a GAPS finding if the search FINDS a spacing); claims `field/beans.rs` `bean_runs#a run's most and its
  spacing`, `bean_runs#which bunds`, `bean_runs#how many`, `RUN_BEADS#a run`, `settle#a drowned bead alone` (then
  restated to cite the new items). SHOULD clear: `choice/lane_skeleton--none`, `choice/plot_regularity--organic`,
  `hamlet/bund`, `hamlet/village-lane`; the other eight claims (`BEAD_R_FT#the bead`, the three "no bead in the water",
  `bean_runs#a run's beads`, `bean_runs#the run on its bund`, `driver.rs` `draw_field#the bean beads`, `settled`).
- 0008 drawing page (5 pop-ups, 22 claims). SHOULD re-check: `hamlet/field-pond` (the pond's own pop-up: IN-STEP
  expected); claims `field/staged.rs` `rice_pond#a four-sided host`, `rice_pond#never a resting plot`,
  `field/features.rs` `pocket_pond#the pond's form` (the bank and the wet margin). SHOULD clear:
  `choice/grave_form--corner`, `--island`, `hamlet/field-grave`, `hamlet/field-rock`; the other 19 claims.

## Your items

- **B1 `0284` drawing page: how far a comb field's bund bows** (`research/questions/0284-how-our-maps-draw-a-bunds-bends-and-corners.drawing.html`; its notes `.drawing.notes.html`).
  The block "Each bund line wanders on its own." gives a POLDER's bow ("up to about a tenth of the grid's spacing") and
  says "no page we read says how far a bund's run bowed". The block "In a valley fan, no two rows of paddies carry the
  same shape." gives the valley fan's drift and no figure: on a valley fan a row's bund bows by up to about 15% of the
  spacing between rows. Add a NEW `<li>` after that block recording the figure as a GUESS - this project's setting, as
  the polder's tenth is, chosen so the wander shows; the same silence (the absence the polder block already rests on:
  cite it the way that block does, or a GROUNDS note `this project's decision` if the block rests on none). Tag:
  `<span class="item" data-item="comb-bund-bow" data-label="GUESS" data-guess="That a valley fan's bund bows by up to about 15% of the spacing between rows: no page read says how far a bund's run bowed."></span>`.
- **B2 `0014` drawing page: the beans on a bund - spacing, how many to a run, which bunds, a drowned bead** (`research/questions/0014-bunds-between-the-paddies-aze.drawing.html`; its notes `.drawing.notes.html`).
  The lead says "Some bunds carry a row of soybeans, drawn as dark green beads." and the block "Each bean plant is drawn
  as a round bead about 3 ft across, in a single row on the bund." gives the bead and "at least two beads". Four things
  the maps do are on no page:
  - the beads stand about 8 ft apart along the bund;
  - a run carries at most four beads;
  - about three bunds in eight carry beans;
  - a bead that would stand in water is dropped, and a run left with one bead is dropped with it (the page's own rule
    that one bead does not read as a row).
  The first three are about how bund beans were really planted: search first (how far apart azemame were sown; whether
  every bund or only some carried them; read this question's research page and the note `nabunken-azemame-4`'s source
  again for a spacing). For each: if a page read gives it, write the finding with its citation, say how the drawn figure
  sits against it, and report `FOUND`; if none, record the drawn figure as a GUESS with an absence note dated today (its
  search terms in the comment). The fourth is a drawing fallback of ours (GROUNDS note). One NEW `<li>` each, or the
  three planting guesses in one block if they share one absence - but then ONE tag for that block. Tags, as used:
  `data-item="bean-spacing-8-ft"`, `data-item="bean-run-at-most-four"`, `data-item="beans-three-bunds-in-eight"`,
  `data-item="drowned-bead-dropped"`, each `data-label="GUESS"` with its `data-guess`. The bead's 3 ft and its comment
  stand.
- **B3 `0008` drawing page: which plot a rice-field pond may take, and its bank** (`research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html`; its notes `.drawing.notes.html`).
  The block "Our maps sink each pond wholly inside one low plot." (tag `much-pond-open-water`) stands, `data-guess` and
  all. Still on no page: (a) on a polder's rice the pond takes only a FOUR-SIDED plot, and never a plot left to rest;
  (b) the bank is drawn about 2.2 ft wide and the wet margin inside it about 2.5 ft. Add one NEW `<li>` for (a), a GUESS
  and a fallback of ours (a dish pond's ring is drawn simply in a four-sided plot; a resting plot keeps its own state),
  tag `data-item="pond-host-four-sided"`, `data-label="GUESS"`; and one for (b), a GUESS - before writing it, grep this
  question's research page and the pond questions' pages for a small pond's bank width: cite what is there (`FOUND`), else
  a GROUNDS note as a drawing fallback and tag `data-item="pond-bank-and-margin-width"`, `data-label="GUESS"`. If (a)
  reads better as two blocks, the second's tag is `data-item="pond-never-resting-plot"`.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p3-paddy-write.md`: `- SECTION=0284 0014 0008`
   (plus any split page), one line per item `B<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
