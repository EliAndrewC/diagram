# Brief - feature 449 T431, T425 (0018, 0008, 0059), session 1: write (the feeder's and the outfall run's width on a dike-pond block, before T431's code; a pocket pond's bank and wet margin as drawn; how far the brook keeps an intake's line, scoped to the intake's siting)

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

**Claims.** The orchestrating session claimed 0018, 0008 and 0059 for feature 449 before starting you. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass was run for this brief.** Its three items restate what the map draws (W2, W3) or record a drawing
width the code will follow (W1, before 449 T431's code). Each is a GUESS of ours. W1 gives a physical width: before
writing it, search the archive once (`make archive-find TERMS="圩 进水 渠 宽|涵闸 河 宽|feeder canal polder width"`, and
any terms you add); if you FIND a width, write the finding and report `FOUND`. No new registry key is expected. Read the
code you restate at HEAD, read only (a builder is editing `rust/phases` in this clone):
`git -C /diagram/.clones/diagram-backlog show HEAD:<path>`.

**Left alone on purpose.** Every existing tag's `data-item`, `data-label` and `data-guess`, with TWO stated exceptions
below (W2's and W3's own tags; no pop-up cites either slug - grep at 7cb42eb6d1). 0019, 0060 and 0068 are READ ONLY:
link to them, edit none (0019's drawing page has 94 bytes of room and 0068's 15). On 0018's drawing page every block
P10 wrote stands (`creek-width-between-ponds`, `one-creek-width-a-block`, `least-pond` and the rest).

**Why W1 goes on 0018's drawing page.** The task's home would be 0019's drawing page (the polder's channels, where
`feeder-course` and `ring-canal-width-dike-pond` stand), but it has 94 bytes of room and a split costs a move of a section
that pop-ups and claims cite. 0018's drawing page (3,298 bytes of room) is the dike-pond question, holds the creeks'
own width (`creek-width-between-ponds`) that the ring canal's width is tied to, and is where a reader of a dike-pond map
looks; 0060's (4,681) is the paddy's field drains and does not speak of a dike-pond block. So W1 is a new `<li>` there,
linking 0019's blocks.

**What the record says on W1's widths, settled for the coordinator.** 0060's drawing page gives a field drain's CLASS
(the drainage-ditch class in its `Grounds:` comment) and that a drain widens to its outfall, with no figure. The 5.5 ft
is on 0068's drawing page, "a 1.2 ft head to a 5.5 ft outfall" (about line 33), for a fan's collector. 0019's drawing
page says only the feeder and "the outfall's short run below its sluice cross the ground outside" the dike, with no
width. So no page sizes a polder's feeder or its outfall run beyond the dike - 449 T431's plan is right, and
`driver.rs` `RUN_W#the drain's run drawn`, which cites 0060 for the 5.5 ft, is to be restated to cite 0068 for the
drain's outfall and W1's item for a dike-pond block's run. The claim is the coordinator's; write nothing of it here.

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment counts and a
tag's `data-guess` does not): 0018 drawing 3,298; 0008 drawing 11,134; 0059 drawing 5,054.

## Cascade expected (for the coordinator; not your work)

What cites the changed pages at 7cb42eb6d1, which of them STATE the thing changed, and which need a DIRECTED check
(`make claims-bundle UNITS=... REASON=... PAGES=...`). Claim paths are under `rust/phases/src/`.

- 0018 drawing page (18 pop-ups, 21 claims). SHOULD re-check: `field/polder.rs` `ditches#the widths` (cites 0018; states the
  ring's and the creeks' widths on a dike-pond block, not the feeder's or the run's: IN-STEP expected), `driver/polder.rs`
  `draw_channels#the pond canals named`; pop-ups `hamlet/sluice-gate`, `hamlet/pond-canal`,
  `choice/field_archetype--mulberry_dike_fishpond` (GAPS possible: the feeder's width). DIRECTED (state the feeder's or
  the run's width, cite another page or none): `driver.rs` `RUN_W#the drain's run drawn` (cites 0019, 0060),
  `driver/polder.rs` `FEEDER_W#the feeder's width` (cites 0068, "no page sizes a polder's feeder"), `field/polder.rs`
  `joins#the outfall's join` (cites 0060; "the run beyond the sluice keeps 5.5 ft"), `polder#the feeder` (cites 0019),
  `OUTFALL_LEG_FT#the outfall's first leg` (cites 0060), `driver/polder.rs` `sluice_channel#the channel it shuts` (cites
  0019, 0179) - each with `PAGES=<0018's drawing page>`; DRIFTED fix: code expected on the widths until T431.
  SHOULD clear: about 14 of the pop-ups and 19 claims. Not reached: `driver.rs` `draw_sink#the drain's run drawn` (a
  paddy's sink, 5.5 ft, cites 0060: unchanged).
- 0008 drawing page (5 pop-ups, 22 claims). DIRECTED (cite NO page, so nothing re-owes them): `driver.rs`
  `draw_field#the pocket pond's ring` and `driver/polder.rs` `draw_polder#the pocket pond's ring` ("flooded ground 2.5 ft
  wide round the pond inside a bund line 2.2 ft wide ... no page sizes the margin") with `PAGES=<0008's drawing page>`;
  then restated to cite `pond-bank-and-margin-width` as drawn. SHOULD re-check: `hamlet/field-pond` (Depiction "an
  earthen bank round its edge, the wet ground just inside it": IN-STEP), `field/staged.rs`
  `polder_stage#a rice polder's pocket pond`. SHOULD clear: `hamlet/field-grave`, `hamlet/field-rock`, `choice/grave_form--corner`,
  `choice/grave_form--island`, and about 20 claims.
- 0059 drawing page (16 pop-ups, 20 claims). SHOULD re-check: `field/brook.rs` `brook#the tap's stride` (says "silent";
  restate to cite `brook-line-below-intake`, scoped), `brook#the shoulder intake`, `brook#the intake's place`;
  pop-ups `choice/intake_place--shoulder`, `choice/intake_siting--straight`, `choice/intake_siting--bend` (IN-STEP
  expected; none holds "70 ft"). DIRECTED: `driver.rs` `BROOK_TAP_RUN#the brook's course` (cites 0054; it IS the 70 ft:
  MISLABELED since P2) and `field/brook.rs` `brook#outside the crop` (cites no page; "out at once below a shoulder
  intake" - the straight-sited case W3 records) with `PAGES=<0059's drawing page>`. SHOULD clear: the four `weir_form--*`,
  three `water_source_position--head_*`, two `intake--*` pop-ups, `choice/intake_place--center`, `hamlet/weir`,
  `hamlet/irrigation-ditch`, `hamlet/stream`, and about 16 claims.

## Your items

- **W1 `0018` drawing page: the feeder's and the outfall run's width on a dike-pond block**
  (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html`; its notes).
  What the map draws today (449 T427's handoff and T431's task line): the ring canal is drawn at the creeks' 6 to 8 ft,
  but the feeder entering it through the inlet sluice is 3 ft and the outfall's run beyond the outfall sluice 5.5 ft, so
  each steps DOWN from the ring under its sluice's board: the ring is drawn wider than the feeder that feeds it, against
  0068's rule ("A delivery ditch is never drawn wider than the canal feeding it."), and the run narrower than the ring it
  drains, against 0060's drain that widens to its outfall (0019's ring-canal block states the rule for a joining channel,
  "a channel is never drawn wider than the one it joins"). Add a NEW `<li>` after the block tagged
  `one-creek-width-a-block`: on a dike-pond block the feeder and the outfall's run beyond the dike are drawn at the ring
  canal's width, so no channel narrows under a sluice's board. A GUESS: the easier of the two routes where the record is
  silent (one width carried through each sluice, against a separate width for each), so that no channel is drawn wider
  than the one feeding it and a drain does not narrow toward its outfall; no page read sizes a polder's feeder or its
  run beyond the dike.
  Link 0019's drawing page (the ring canal's width; the feeder's course) and 0068's. A width of a channel is a physical
  figure: give it a dated ABSENCE note of its own in 0018's drawing notes (0019's `how-our-maps-draw-polders-weitian-waju-2`
  is that page's note and stays there), naming your archive search. Say nothing of a rice polder's feeder or run. Tag:
  `<span class="item" data-item="feeder-and-run-ring-width" data-label="GUESS" data-guess="That on a dike-pond block the feeder and the outfall's run beyond the dike are drawn at the ring canal's width: no page read sizes a polder's feeder or its run beyond the dike; one width is carried through each sluice, so no channel is drawn wider than the one feeding it and the drain does not narrow toward its outfall."></span>`.
  The page then states what 449 T431's code will draw, not what it draws today: write it in the present tense as the
  map's rule, as the other blocks are; the code follows this pair.
- **W2 `0008` drawing page: the pond's bank and wet margin, as drawn**
  (`research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html`).
  The block "The pond's bank is drawn about 2.2 ft wide, and the wet ground inside it about 2.5 ft wide." (line 22, tag
  `pond-bank-and-margin-width`) copies the old claim's words, not the drawing: both drawers fill the wet ground out to
  2.5 ft past the water's edge and center the 2.2 ft bank line ON that outer edge, with a 1.2 ft line at the water's
  edge, so about 0.8 ft of wet ground shows between them and the bank's outer edge stands about 3.6 ft from the water
  (P3's cascade; `specs/449-rust-codebase/found.jsonl`, the row on 0008 drawing §25). Confirm it in the code first (read
  only: `rust/phases/src/driver.rs` about lines 340-360, the pocket pond's two ellipses; and the pocket pond's ring in
  `rust/phases/src/driver/polder.rs`, `grep -n "pocket pond" ` - if the two differ, write both, or report `OPEN`).
  Restate the heading and the first sentence as drawn, for example: "The pond's bank is drawn about 2.2 ft wide, about
  2.5 ft out from the water's edge, with under a foot of wet ground showing inside it." Keep the label GUESS, the link
  to 0014 and the note. STATED EXCEPTION: rewrite the tag's `data-guess`, keeping `data-item` and `data-label`, to say the
  same ("That the pond's bank, about 2.2 ft wide, stands about 2.5 ft out from the water's edge with under a foot of wet
  ground inside it: drawing widths of this project's, which no page in the record sizes.").
- **W3 `0059` drawing page: how far the brook keeps the intake's line, scoped to what the code does**
  (`research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html`).
  The block "How far does the brook keep its line below an intake on a shoulder of the fan?" (line 12, tag
  `brook-line-below-intake`) says "About 70 ft on the maps: below an intake standing on a shoulder of the fan, the drawn
  brook holds the intake's line that far before it takes its own course down the flank." P2's cascade worked it from the
  code's constants (not measured on a map): where the intake is sited at a BEND it stands 46 to 75 ft outside the head's
  corner, outside the brook's keep-clear line past the fields (34 ft), so the brook holds its line for the 70 ft, as
  written; where it is sited on a STRAIGHT reach the angle is smaller and the intake stands only 14 to 22 ft outside the
  corner, INSIDE that line, so the brook steps out to the line at once and then does not move in toward the fields for
  the rest of the 70 ft. Read the code yourself (read only): `rust/phases/src/field/brook.rs` (`brook`, its tap stride
  and the outward step) and `rust/phases/src/driver.rs` (`BROOK_TAP_RUN`, `BROOK_SKIRT`, `HEAD_LEAD`, the offtake angle,
  `MEANDER_FT`, `MEANDER_WAVE_FT`), and redo the arithmetic. Write only what the code does: the sentence scoped to the
  two sitings, for example "below a shoulder intake the drawn brook does not move in toward the fields for about 70 ft:
  from an intake at a bend it holds the intake's line; from one on a straight reach, which stands nearer the corner, it
  first steps out to its keep-clear line past the fields". Name no engine identifier. Keep the label GUESS, the note and
  the HTML comment (bring the comment in line in a few words). STATED EXCEPTION: rewrite the tag's `data-guess` to match,
  keeping `data-item` and `data-label`. If your arithmetic differs from P2's, write what the code does and give your
  numbers in the handoff.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p13-polder-brook-write.md`: `- SECTION=0018 0008 0059`
   (plus any split page), one line per item `W<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
