# Brief - feature 449 T420 and T425 (0018, 0019, 0022), session 1: write (the channels among the dike-ponds, the ring canal's line, and the guesses the pond code makes that no page records)

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

**Claims.** The orchestrating session claimed 0018, 0019 and 0022 for feature 449 before starting you; if an edit is
refused as unclaimed, stop and report it in the handoff, use no escape.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read yourself (translation
marked as one, the original after); an unreadable source is not cited. Look in the archive first (`make archive-find KEY=<k>`
or `URL=<u>`) and put every page read on the ledger (`make source-pages`, `make source-outcome`). A new registry key is
`make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` only after grepping `research/sources/010-works-cited/` for the URL
(percent-decoded); at most ten new keys, and this brief expects two or three. A page over the 20,000-byte prose cap is
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

**The research pass.** A pass of 2026-11-24 is saved at
`/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/pass-449-t420-dike-pond-channels.md` (15 KB: sources A-L, the ring-canal
section, the verdicts, the leads). Its passages are LEADS: read each on the archived copy or the URL yourself before
quoting it. Registry keys that already exist: `guangdong-xinyu-22` (Qu Dajun, 1678), `minle-dou-people` (the Jiancun
landings), `king-forty-centuries` (the entry that holds the gutenberg 5350 text URL; `king-1911-farmers-forty-centuries`
is a second entry on the same book - use the one whose citation line shows your passage), `wuhurec-wanchun` (Shen Kuo,
1061), `ihns-bunongshu` (c.1640), `tian-dike-pond` (Tian 2019), `fei-1939`, `fao-ac264e-ch10`. NEW keys expected: Jia Dan
c.1070 in the Wujun zhi, chapter 19 (https://zh.wikisource.org/wiki/吳郡志/卷19 - the existing `wujunzhi-wikisource` entries
hold chapters 12, 31 and 32; a chapter-19 entry in their form) and Chen Caixia et al. 2021
(https://www.resci.cn/CN/lexeme/showArticleByLexeme.do?articleID=49240). The pass's modern pages (Ruddle 1980s, FAO, the
newspapers) are not needed.

**Left alone on purpose.** One sentence is a placeholder of feature 449 T422, whose builder is still working: on
0018's drawing page the block "The bank is drawn as planted ground: mottled earth under rows of mulberry bushes." (about
line 11). Do NOT touch it; a later brief carries it if T422 reports a page correction. (An earlier plan had the
coordinator fill it first: superseded.) Also NOT to change: 0018's drawing-page block "Each bush is drawn a few feet
across" (the mulberry crown is already recorded there); 0019's RESEARCH page (48 bytes under the cap: write nothing on
it); 0022's drawing-page block "The module lines bow gently ... while the dike and the ring canal at the block's edge
stay put" (it stands as written); the reed belt's width, if you look for one, is on the marsh question 0057's pages
(read only).

**Sizes at the start** (prose bytes of room under 20,000): 0018 research 5,768, drawing 5,721; 0019 drawing 5,631 (its
research page 48); 0022 drawing 11,524.

## Cascade expected (for the coordinator; not your work)

What cites the changed pages, and which of them STATE the thing changed (so should be re-checked) against which merely
cite the page (so should clear at triage).

- 0018 research page (20 pop-ups, 0 claims). SHOULD re-check: `hamlet/pond-canal` (states "the network the ponds lie
  among, not ... irrigation ditches" and would gain the boats and the creeks), `choice/leftover--pond` and
  `choice/leftover--rice` (speak of creeks; `leftover--pond` of boats), `choice/pond_layout--mosaic` (creeks),
  `choice/field_archetype--mulberry_dike_fishpond`, `hamlet/fish-pond` (creeks). SHOULD clear: the five
  `choice/dikepond_split--*`, `choice/dike_crop--mulberry`, `choice/fry_form--fry_village`, `choice/fry_form--none`,
  `choice/land_use_overlay--mulberry_fishpond`, `hamlet/fry-pond`, `hamlet/fruit-dike`, `hamlet/mulberry-dike`,
  `hamlet/tea-dike`, `hamlet/sluice-gate` (a new finding on channels; none of them states the channels' kind or width).
- 0018 drawing page (18 pop-ups, 9 claims). SHOULD re-check: `hamlet/pond-canal` (the canal's own pop-up: the width),
  `choice/field_archetype--mulberry_dike_fishpond` ("ponds of uneven shape", "the lattice of canals"), `hamlet/fish-pond`
  (uneven shape; the rounded corners and the least pond are new guesses about its glyph). Claims SHOULD re-check:
  `field/ponds.rs` `rounded#rounded corners`, `rounded#the bank's inset`, `LEAST_SHARE#the least pond`,
  `field/landuse.rs` `REACH_FT#the rounding` (each says the page is silent; each is then restated to cite the new item
  id). SHOULD clear: the other five `field/landuse.rs` claims and every other pop-up of the 18.
- 0019 drawing page (14 pop-ups, 45 claims). SHOULD re-check: `hamlet/pond-canal` (states "the lattice is bent out of
  line", "A canal is drawn round the inside ...", "starts at a pond outside the dike"),
  `choice/pond_layout--mosaic` ("a lattice of ditches", "the interior ditches meander like creeks"),
  `choice/field_archetype--mulberry_dike_fishpond` ("the lattice of canals bent out of line"),
  `choice/field_archetype--polder_grid` ("Inside the dike a ring canal runs round its foot, a convention"; "long, nearly
  straight reaches that waver gently"), `choice/water_source_position--corner_high` ("gently wavering reaches with rounded
  corners"; "the open water that feeds it just outside the dike"), `choice/pond_layout--grid` ("nearly straight, wavering
  gently"), `hamlet/sluice-gate` (the feeder and the inlet), `hamlet/perimeter-dike` (the reed fringe: only if the strip's
  depth lands). Claims SHOULD re-check, all in `rust/hamlet/crates/phases/src/`: `field/polder.rs` `RING_FT#the ring
  canal`, `ditches#the ring canal`, `polder#the ring canal's place`, `polder#the feeder`, `ditches#the dike-pond's interior
  ditches`, `row_ditches#the lattice both ways`, `Warp.at#the mosaic's drift`, `DRIFT_SHARE#the mosaic's drift`,
  `MOSAIC_WAVES#the mosaic's waves`; `driver/polder.rs` `sluice_channel#the channel it shuts`, `stage_waterward#the reed
  strips`, `roll_polder#the strips after the seat`; `driver/check.rs` `RING_CANAL#the ring canal`; `waterward.rs`
  `fringe#reed fringe on the waterward flanks`. SHOULD clear: the other 31 claims (the sluices' count and places, the
  village's ground, the dike-top houses, the chessboard's rolls) and `choice/cluster_position--high_margin`,
  `choice/settlement_form--dike_top`, `choice/settlement_form--nucleated`, `hamlet/fish-pond`, `hamlet/fry-pond`,
  `hamlet/windbreak`.
- 0022 drawing page (3 pop-ups, 21 claims). SHOULD re-check: `choice/pond_layout--grid` (it says "never a grid of uniform
  rectangles" of a RICE polder: it should come back IN-STEP), claim `field/polder.rs` `polder#never uniform rectangles`.
  SHOULD clear: `choice/pond_layout--mosaic`, `hamlet/bund`, the other 20 `field/polder.rs` claims.

## Your items

- **A1 `0018` research page: the channels among the ponds were creeks that boats used** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html`; its notes `.notes.html`).
  The page names creeks only in passing (the Sangyuan sentence of its opening and the dou finding, note
  `minle-dou-people-2`). ADD one bold-opened finding. What it says, each part from the source named, read by you:
  - The ponds lay among creeks that boats used, not among field ditches. Pearl delta: Qu Dajun 1678 (fry raised in the
    ponds and carried out by boat; on his chessboard the LINES are dikes, the squares ponds); the Jiancun landings (58
    landings on under two kilometers of creek, Guangxu reign, as a 2021 newspaper tells it); Chen 2021 (farmers went to
    work the ponds and sold the fish by small boat - informant memory of practice before the reforms, so after 1912: say
    so). Lake Tai and Jiangnan, which is rice-polder country and is said to be: Jia Dan c.1070 (households cut the dikes
    to make small creeks for moving and mooring boats); Shen Kuo 1061 (the field ditch against the larger channel that
    floats a boat); the Shen family's farm book c.1640 (mud dredged and manure carried by boat); King, seen in 1909 (mud
    stacked for removal by boat to the mulberry).
  - How wide such a channel was: NO premodern source gives the width of a channel between ponds. An absence note dated
    2026-11-24, its searches (the pass's, and yours) in its comment. The nearest measured figures, each with what it
    measures: King's gate canals in the Pearl delta, six to eight feet wide, in diked cane and rice fields, not ponds
    (1909); his side canals off the Kashing-Hangchow route, 22 and 19 ft on average. A designed creek of 6 to 8 m after
    1998 is modern consolidation and is not a finding.
  - Whether a channel ran along every pond's edge: NOT attested. Qu Dajun's lines are dikes, Tian's broad borders are
    dikes; the 1950s creeks are described as winding (Tian). Say what is and is not recorded; do not say ponds shared
    banks as a finding.
- **A2 `0018` drawing page: the canal's width, the ponds' corners, the least pond** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html`; its notes `.drawing.notes.html`).
  - The block "The canals are drawn as the waterways the ponds lie among, not as field ditches." STANDS: keep it. Add a
    NEW `<li>` after it for the width: a canal between ponds is drawn about 6 to 8 ft wide, a GUESS; no source gives a
    premodern width for a channel between ponds; King's gate canals of 1909 (6 to 8 ft, in diked cane and rice fields,
    not ponds) are the nearest measured figure. Cite King, and the absence note of A1 (a like note on this page's notes
    file). Tag:
    `<span class="item" data-item="creek-width-between-ponds" data-label="GUESS" data-guess="The width of a channel between ponds, about 6 to 8 ft: no source gives a premodern width for one; King's gate canals of 1909, 6 to 8 ft wide in diked cane and rice fields, are the nearest measured figure."></span>`.
    (The engine's code will be made to follow this figure by feature 449 T420 and will cite this item id: keep the slug.)
    The widths-ladder question's drawing page (0068, read only, FULL: 19 bytes of room) states no width for a channel
    between ponds today; if your grep of it finds one, do not edit that page - report it `OPEN` in the handoff.
  - A NEW `<li>`: a pond's corners are drawn rounded - the bank's corner cut back about 8 ft, the water's about 16 ft.
    The page's opening says only "ponds of uneven shape"; no page read gives a pond's corner. A GUESS, a drawing fallback
    of ours (GROUNDS note). Tag `data-item="pond-corners-rounded"`, `data-label="GUESS"`, a `data-guess` in the form above.
  - A NEW `<li>`: the least pond - where the bank's share asks more than a parcel holds, the water is still drawn, a
    tenth of the parcel across. A GUESS, a fallback of ours (GROUNDS note). Tag `data-item="least-pond"`,
    `data-label="GUESS"`.
- **A3 `0019` drawing page: the mosaic's channels, the ring canal's line, the feeder outside the dike, the reed strip's depth** (`research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html`; its notes `.drawing.notes.html`).
  - The paragraph that opens the layouts section says "the dike-pond block as a mosaic, its lattice of ditches bent out of
    line so that its four-sided ponds skew to uneven shapes", and the block "The mosaic bends the lattice but keeps every
    pond four-sided." says "the interior ditches become meandering creeks". Between ponds the channels are the creeks of
    the dike-pond question (item A1), not ditches: reword both so no dike-pond channel is called a ditch (a `<p>` takes no
    tag). Then a NEW `<li>`: a channel is drawn along every pond's edge, a GUESS - Qu Dajun's chessboard has dikes for
    its lines, and no source read says a creek ran on every side of a pond. Tag
    `data-item="channel-every-pond-edge"`, `data-label="GUESS"`, its `data-guess` saying that. It is a guess about the
    physical world: it owes the citation (Qu Dajun, already cited on this page by `guangdong-xinyu-22-4`) or an absence
    note.
  - The block "The canals are drawn in long, nearly straight reaches that waver gently, with rounded corners." (tag
    `canals-long-nearly-straight`, CONVENTION: keep the tag as it is) is untrue of the ring canal, which the maps draw
    straight along the dike's foot with square corners. Restate the block's words so they except the ring canal, and
    give the ring canal's line a NEW `<li>` of its own: straight along the dike's inside foot, square at the corners, a
    drawing CONVENTION (no source read names a canal at a dike's inside foot at all: Jia Dan c.1070 puts the bounding
    channels OUTSIDE the dike, cut straight; Fei 1936 puts the drain at the middle). Tag
    `data-item="ring-canal-straight-square"`, `data-label="CONVENTION"`. The page's Evidence comment (line 4) says
    "convention (the ring canal's place and its gently wavy line)": correct it to match.
  - The block "A ring canal is drawn round the inside foot of the dike, on the field side." (tag
    `ring-canal-round-inside`, CONVENTION: keep the tag) says "and no channel runs outside the dike". The maps do draw
    two: the feeder, from the wild water to the inlet sluice, and the outfall's short run below its sluice. Restate that
    clause truthfully (no canal RINGS the dike outside; the feeder and the outfall cross to it). Then a NEW `<li>`: the
    feeder's course is a GUESS - drawn straight from the wild pond to the inlet, as the wild water's own reach; no page
    read gives a feeder's course. Jia Dan's bounding channels outside the dike may be cited as what IS recorded there.
    Tag `data-item="feeder-course"`, `data-label="GUESS"`.
  - The block "Both polders carry a reed fringe along their west flank." gives no depth. The strip is drawn about 280 ft
    deep, a figure no page records. First read the marsh question's pages (0057, read only) for a reed belt's width: if
    one is recorded there, cite it and say how the 280 ft sits against it; if none, a NEW `<li>` (do not fold it into the
    GM-ruled block) recording the depth as a GUESS, with an absence note or the citation. Tag
    `data-item="reed-strip-depth"`, `data-label="GUESS"`.
- **A4 `0022` drawing page: "never ... uniform rectangles" is a rice polder's rule** (`research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html`).
  The block "Our maps never draw the parcels as a grid of uniform rectangles." conflicts with the polder drawing page's
  block "A dike-pond block is drawn as a mosaic or as a chessboard of ponds, rolled for each hamlet." (the chessboard,
  recorded in 1678, on about one hamlet in three). Restate the lead and the sentence to a RICE polder's parcels, and name
  the exception in one sentence with a link to that drawing page
  (`0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html`). The chessboard is ponds, recorded
  premodern: say nothing that makes it "only modern". No new source.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p1-dikepond-write.md`: `- SECTION=0018 0019 0022`
   (plus any split page), one line per item `A<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
