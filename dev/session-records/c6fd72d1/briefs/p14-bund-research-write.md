# Brief - feature 449 T425 (0014, 0284), session 1: write (the Ishiguro bund-bean finding on 0014's research page - after a split of its section on why a hand-piled bund wavers to a new question - its registry entry's place-name, and how far a bund bowed reconciled across the pages)

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

**Claims.** The orchestrating session claimed 0014 and 0284 for feature 449 before starting you; the new question you reserve is yours by reserving it. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects none (one if the bow search finds a page). A page over the 20,000-byte prose cap is
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

**No research pass was run for this brief.** Item B1 carries a finding already on the record (the Ishiguro village
account, registry key `ishiguro-azemame-tool`, cited today only on 0014's drawing page) to the research page, after a
split that makes room; item B2 reconciles two pages on how far a bund bowed. Before labeling the bow figure, search the
archive once (`make archive-find TERMS="畦 曲が|畦畔 蛇行|bund straight|aze curve"` and any terms you add); if you FIND a
figure, write it as the finding, cite it, and report `FOUND`. No new registry key is expected (one if that search finds
a page). Read the code you quote at HEAD, read only (a builder is editing `rust/phases` in this clone):
`git -C /diagram/.clones/diagram-backlog show HEAD:<path>`.

**Why a split (item B1).** 0014's RESEARCH page has 12 bytes of prose under the 20,000-byte cap, and no pointer form
the rules allow costs nothing: the record's `CLAUDE.md` ("A question has a size", about lines 80-91: read them first)
gives one pointer form, `<a class="moved">`, and only for a section MOVED; a plain link to the drawing page would itself
cost bytes the page lacks, and a size edit never drops a claim-bearing word. So a split first, a MOVE (feature 451 T184,
T185); `research/size-limits.json` is empty and this brief proposes no limit.

**What to move, and why that section.** Move, whole, the section on why a hand-piled bund wavers: the paragraph "Why a
hand-piled bund wavers is written down nowhere we looked. What follows is this project's reading of how piled earth
behaves, each point a GUESS." (line 26 at 7cb42eb6d1) and its five blocks (lines 27-33: "Did a hand-piled bund's corners
wear round?", "Why did a hand-piled bund's line wander?", "On this project's reading, a bund junction was the most worked
point in a field.", "Did a bund step sideways and carry on?", "Where a real boundary did step, on this project's reading,
something stood at the corner."), about 3,500 bytes. Why that section: it holds no item tag (0014's research page holds
none) and no engine claim cites the research page (`dev/claims-index.json` at 7cb42eb6d1: all 13 claims on 0014 cite its
drawing page); it is a topic a reader asks on its own (this project's reading of piled earth, the grounds of 0284's
drawing page); and it leaves the bund-bean section, where B1's finding belongs, on 0014. The other sections are each
stated by a pop-up too, so no cheaper section exists. Change NO word of the moved blocks.
  - Notes: a note moves with the sentence that cites it. Three of the moved section's notes are ALSO cited by blocks that
    stay (`aze-jawiki-7`, `aze-jawiki-8`, `kotobank-aze-sekai-daihyakka-2`): those stay on 0014's notes, and the new
    page cites its own note on the same passage, in the form the record's `CLAUDE.md` gives (if it gives none, the key's
    next free suffix); say in the handoff which you did. The other seven (`aze-jawiki-9`, `aze-jawiki-11`,
    `bunds-between-the-paddies-aze-4`, `-5`, `-6`, `-9`, `-10`) move with their originals.
  - The new question is a RESEARCH page with no drawing page, as 0331 is (read its three files for the form): reserve it
    with `make reserve KIND=question KEY="<heading>"`, a heading a reader asks, for example "Why a hand-piled bund
    wavered, wore round and never stepped"; its own `<h2>`, its tags marker from `research/tags.json`, the moved
    paragraph as its opening account, its `Grounds:` and `Evidence:` comments in a few words each.
  - Where the section stood, a short paragraph with `<a class="moved" href="<the new page's file name>">` and the new
    page's title as its text. Bring 0014's `Evidence:` comment in line, no further.

**Left alone on purpose.** Every existing tag's `data-item`, `data-label` and `data-guess`, with ONE stated exception
below (B2's own tag; no pop-up cites `comb-bund-bow` - grep at 7cb42eb6d1). 0014's DRAWING page is not touched (the
Ishiguro blocks there, `bean-spacing-8-ft`, `bean-run-at-most-four`, `beans-three-bunds-in-eight`, stand); 0005 and 0346
are read only.

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment counts and a
tag's `data-guess` does not): 0014 research 12; 0284 drawing 9,172.

## Cascade expected (for the coordinator; not your work)

- 0014 research page (5 pop-ups, 0 claims). The move is followed by the `moved` pointer, so the moved blocks are NOT
  "removed" at triage. SHOULD re-check: `hamlet/bund-beans` (it says "How many plants a bund carried, or how far one
  spread, is not recorded": a GAPS finding likely - the holes a foot apart, two or three beans to a hole);
  `hamlet/bund` (its Guesses "a hand-piled bund's corners wore round and its line wandered a foot or two", its
  Depiction "corners are rounded and lines wander": its research line must gain the new page - a pop-up edit) and
  `choice/plot_regularity--organic` ("The banks are drawn bending and wandering": the same pop-up edit). SHOULD clear:
  `hamlet/village-lane`, `hamlet/soy`.
- 0284 drawing page (2 pop-ups, 0 claims): `hamlet/bund`, `choice/plot_regularity--organic` again (IN-STEP; neither
  states how far a bund bows).
- DIRECTED claim checks (no claim cites 0014's research page or 0284's, so nothing re-owes these): `field/beans.rs`
  `BEAD_STEP_FT#the beads' spacing` (cites no page; "the record silent on it ... not their spacing") and `bean_runs#a run's
  most and its spacing` (cites 0014's drawing page: "silent on ... how far apart") with `PAGES=<0014's research page>`;
  IN-STEP expected (the 8 ft is a CONVENTION, the drawing page's `bean-spacing-8-ft`), restated to cite the plants'
  spacing. `field/lattice.rs` `BOW#the bund's bow`, `Lines.new#the bund's bow`, `Lines.u#the bow's shape` (cite 0005 and
  0346; P3's cascade asked them restated to cite `comb-bund-bow`) with `PAGES=<0284's drawing page and the new page>`.
- The NEW question: no pop-up and no claim cites it yet.

## Your items

- **B1 `0014` research page: a split, then the Ishiguro finding; and the registry entry's place-name**
  (`research/questions/0014-bunds-between-the-paddies-aze.html` and its notes and originals; the registry entry
  `research/sources/010-works-cited/37820-ishiguro-azemame-tool.html`).
  1. THE MOVE, as above. Run `make question-sizes` after it.
  2. THE FINDING, only after the move shows room: a NEW `<li>` in the section "By high summer, the bund was no longer bare
     mud.", after "The beans on the bunds were soybeans, azemame.": in one village of terraced paddies, where every
     household grew them until the 1950s, the beans went into holes about 30 cm (~1 ft) apart, two or three to a hole, in
     one row down the middle of the bund. Read the archived page first (`make archive-find KEY=ishiguro-azemame-tool`) and
     quote it verbatim as you read it, the translation marked, the original after; the drawing page's notes
     `ishiguro-azemame-tool`, `-2`, `-3` stay where they are - the research page cites its own notes on the passages (the
     key's next free suffixes). Label it: ATTESTED ONLY FOR one terrace village in the mid-20th century (the entry's own
     limits). Name no drawing figure; the drawing page already says how the map draws it.
  3. THE ENTRY. Its `What it is:` names "Ishiguro, a village of terraced paddies in the snowy hills of Takayanagi,
     Kashiwazaki, Niigata", and the cited page does not give Takayanagi, Kashiwazaki or Niigata. Read the archived page
     and, if it links one, the same site's top page: if a page of that site you read names the place, keep it and add that
     page's URL to the entry with its READ date; else cut the entry's words to what the page states (and cut "snowy" or
     "terraced" too if the page does not give them). Say in the handoff which you did.
- **B2 `0284` drawing page: how far a bund bowed, reconciled with the moved reading**
  (`research/questions/0284-how-our-maps-draw-a-bunds-bends-and-corners.drawing.html`).
  The block "A valley fan's bund bows by up to about 15% of the spacing between its rows." (line 22, tag `comb-bund-bow`)
  says "no page we read says how far a bund's run bowed (link 0014's research page)", while the reading B1 moves says
  "So a straight hundred-foot bund bows by a foot or two", unfootnoted, under its section's "each point a GUESS". If your
  archive search FINDS a figure, cite it on the new page (a new sentence after the moved one, which stays word for word)
  and in 0284's block. Else: the moved sentence stays as it is (its section labels it a GUESS); restate 0284's clause to
  "no source we read says how far a bund's run bowed; the record's own reading of piled earth guesses a foot or two over
  a straight hundred feet" (link the NEW page), and, if the code lets you, one clause on how the drawn bow compares (read
  `rust/phases/src/field/lattice.rs`, `BOW` and the row spacing it scales, read only; if you cannot tell the spacing in
  feet, leave the comparison out). Repoint the page's other links to 0014's research page only where the linked content
  moved. Keep the label GUESS and "this project's setting". STATED EXCEPTION: rewrite the tag's `data-guess`, keeping
  `data-item` and `data-label`, to "That a valley fan's bund bows by up to about 15% of the spacing between rows: no
  source read says how far a bund's run bowed; the record's own reading of piled earth guesses a foot or two over a
  hundred feet."

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p14-bund-research-write.md`: `- SECTION=0014 0284`
   (plus any split page), one line per item `B<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
