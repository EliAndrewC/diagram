# Brief - feature 449 T426 (0057, 0031, 0081), session 1: write (the wet ground on a tapering flank, the seat astride the brook where a fall runs square across the wind - after a split of 0031's drawing page - and the point a cluster's way out is asked from)

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

**Claims.** The orchestrating session claimed 0057, 0031 and 0081 for feature 449 before starting you; the new question you reserve is yours by reserving it. If an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass was run for this brief.** Its items record what feature 449 T426 built or measured (the seat of a
hamlet whose fall runs square across its wind) and no page states. All three are drawing fallbacks of ours (GROUNDS
notes, `this project's decision`); none gives a physical figure. If, reading a page for an item, you find that the record
already answers it, write the finding and report `FOUND`. No new registry key is expected. The builder's measurements are
in `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T426-b1.md` (its "Causes (measured)" section, about 12 lines:
`make lines FILE=... KEY='^- |^Both|^T261'`); the quotations below are the pages at commit 9162aa3953.

**Why a split (item N2).** The drawing page of the clustered-and-scattered question (0031) has 2 bytes of prose under the
20,000-byte cap, and a seat the code now takes must be recorded on it. A size edit never changes or drops a claim-bearing
word, and a split is a MOVE (feature 451 T184 and T185; the record's `CLAUDE.md`, "A question has a size", about lines
80-90: read those lines first). `research/size-limits.json` is empty, and this brief proposes no limit.

**What to move, and why that section.** Move, whole, the section on a scattered farm's reach of its field: the paragraph
"A scattered farm fronts its own fields, so each house has to stand within reach of one." (about line 16), the list of
two blocks under it - "A scattered farm must stand within reach of the rice that is drawn, not of the field outline the
map claims." and "Two hand-drawn villages keep the empty ground between their field's outline and its last rice." - and
the paragraph after it, "The rule the map follows: a scattered settlement needs roughly twice the room per farm ..."
(about 2,100 bytes with their comments). It is the one section of the page with NO item tag (the others hold
`scattered-settlement-lanes-among`, `long-row-village`, the seven farm-water tags, `does-village-s-cluster` and the rest,
which pop-ups and claims cite by page and must not move); none of the 24 engine claims that cite the page states anything
in it, and no pop-up holds its words ("within reach of the rice", "twice the room", "420 ft": grep at 9162aa3953); and it
is a topic a reader asks on its own. Change NO word of the moved blocks. Confirm the claims first:
`grep -o '"claim": "[^"]*clustered-and-scattered[^"]*"' dev/claims-index.json | grep -i "reach\|twice\|planted"` (read
only). At 9162aa3953 it prints ONE line, which is harmless: "the belt's ground kept - shelter-belts-on-a-villages-...",
a claim on the shelter belt whose "reaches past the band" is not this section. If it prints any OTHER claim, and that
claim rests on the section, stop and report `OPEN`.

**Left alone on purpose.** Every existing tag's `data-item`, `data-label` and `data-guess`. On 0031: the block "Where
does a village's cluster sit?" stands word for word, its two tags (`does-village-s-cluster`, `does-village-s-cluster-2`)
with it - N2 ADDS a block after it. On 0057: the blocks "The marsh is as wide as the fields above it, with 90 ft more on
each side." and "The marsh runs straight across the slope as a whole ..." stand. On 0081: the block "A track keeps off
wet ground." (tag `track-keeps-off-wet`) stands. The stream-banks question (0035) and the too-wet-to-build question
(0058) are READ ONLY - link to them, edit neither (0058 was edited by another session today).

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment counts and a
tag's `data-guess` does not): 0057 drawing 9,179; 0031 drawing 2; 0081 drawing 3,798.

## Cascade expected (for the coordinator; not your work)

What cites the changed pages at 9162aa3953, which of them STATE the thing changed, and - since a claim is re-owed only by
a page it CITES, and a claim saying "the page is silent" is cleared by the tool unread when the page gains a NEW block -
which claims need a DIRECTED check (`make claims-bundle UNITS=... REASON=... PAGES=...`). Claim paths are under
`rust/phases/src/`.

- 0057 drawing page (3 pop-ups, 5 claims). SHOULD re-check: `hamlet/marsh` (its Depiction says "its upper edge following
  the foot of the fields": IN-STEP expected; a GAPS finding is possible, the wet flank); claims `driver/toe.rs`
  `toe_band#toe band edge` and `PAD#toe band edge` (they state the point-by-point rule N1 adds to: IN-STEP). SHOULD
  clear: `choice/cluster_position--on_rise`, `choice/cluster_position--valley_mouth`, the other three `toe.rs` claims.
  States the fact, cites ANOTHER page (directed check with `PAGES=<0057's drawing page>`): `seat/margins.rs` `ranked#not
  on the wet toe` (cites 0058's drawing page), `seat.rs` `open_at_an_end#a seat astride the brook leaves by its open
  bank` (cites 0035's and 0081's; it says "its windward flank on the wet toe"), `driver.rs` `stage_seat#the way out's
  walls` (cites 0081's).
- 0031 drawing page (42 pop-ups, 24 claims). The move is followed by the `moved` pointer, so the moved blocks are NOT
  "removed" at triage. SHOULD re-check: `choice/cluster_position--high_margin` (the one pop-up that states the seat's
  rule: "its land laid to fall away from the winter wind or square across it, so its houses keep their back to the
  wind"; a GAPS finding is possible, the corner astride the brook); claims `seat.rs` `seat#the back to the hill where the
  wind cannot be backed` (it states "a fall square across the wind ... is not one toward it"), `seat/margins.rs`
  `ranked#seat on the field's margin` and `ranked#the ladder`, `driver/plan.rs` `plan#the fall backs the wind`,
  `water_frame.rs` `admitted#high side and windward side as one` (IN-STEP expected on all: the block they rest on
  stands). SHOULD clear: the other 41 pop-ups and 19 claims. If a pop-up does state the moved section
  (`choice/settlement_form--dispersed` is the likeliest), its `Drawing:` line must gain the new page - a pop-up edit.
  States the fact, cites ANOTHER page: `seat.rs` `open_at_an_end#a seat astride the brook leaves by its open bank` (cites
  0035's and 0081's drawing pages, not 0031's: N3 re-owes it through 0081, but it is then judged without the block N2
  adds - a directed check with `PAGES=<0031's drawing page>`, after which it is restated to cite
  `seat-astride-brook-windward-corner`).
- 0081 drawing page (10 pop-ups, 11 claims). SHOULD re-check: `seat.rs` `BAND_EXITS#the way out from the band's ends`
  (says "the page is silent on which point of a cluster its way out leaves from": the tool will probably clear it
  unread - a DIRECTED check; IN-STEP, then restated to cite `way-out-from-band-ends`), `seat.rs` `open_at_an_end#...`,
  `seat#a walled-in head gives way`, `seat/exit.rs` `Exit.has_exit#dry way out of the seat`; pop-up `hamlet/village-lane`
  ("the track out runs off the edge of" the map: IN-STEP). SHOULD clear: the six `choice/lane_skeleton--*`,
  `choice/lane_web--alleys`, `choice/lane_web--back_lane`, `sheet/road`, and the other seven claims.
- The NEW question (the moved section): it starts with no pop-up and no claim citing it.

## Your items

- **N1 `0057` drawing page: the wet ground on a flank that tapers inward downhill** (`research/questions/0057-marshes-and-wetlands-shitchi.drawing.html`; its notes `.drawing.notes.html`).
  The block reads: "The marsh's upper edge follows the foot of the fields, point by point." - "Across the slope, at short
  steps, the edge is set 90 ft above the lowest field near that point, and smoothed, so the reeds begin at the fan's foot
  all along it and no reed is drawn on a field." What feature 449 T426 measured: where a field's flank tapers inward
  downhill (on its two seeds the windward flank, along the brook), each step across the slope finds its lowest field
  farther up, so the rule as written lays wet ground up the whole flank (the builder's handoff, named above: "lays wet
  ground along the whole flank: every tier-0 margin's center is on the toe"); the coordinator's report adds that at the
  outermost step it lands above the field's head corner, on the brook's far bank - that detail is NOT in the handoff, so
  write it only if you can confirm it (the code's account, read only: `rust/phases/src/driver/toe.rs`, the claims of
  `toe_band`), else write "up the whole flank" and say in the handoff which you wrote. The page says nothing of this. Add a NEW `<li>` after that block that
  SAYS WHAT THE MAP DRAWS TODAY: on a flank that tapers inward downhill the point-by-point edge carries the wet ground up
  that flank (as far as the head's corner, if confirmed); a house, a seat and a track keep off it as off the rest of the wet
  ground. Label it a deliberate DEVIATION, in those words: the record's springs come out along a fan's toe (the page's
  own first block), not up its flank, and the wet flank is a consequence of the rule as drawn - the easier of drawing it
  so or cutting the band off at the field's lower corners - not a finding. State its cost in one clause (a hamlet whose
  fall runs square across its wind finds its windward flank wet and takes the seat item N2 records). GROUNDS note. Tag:
  `<span class="item" data-item="toe-on-tapering-flank" data-label="DEVIATION" data-guess="That the wet ground climbs a flank tapering inward downhill: no page read says seepage rose along a fan's flank; the edge is set point by point above the local lowest field, and this is what that rule draws."></span>`
  (if the registry test refuses `data-guess` on a DEVIATION tag, drop the attribute and say so). Do NOT write that the
  toe SHOULD climb the flank, and do not reword the first block: whether the band is cut off at the field's corners
  instead is a code question listed for the coordinator - report it `OPEN` in the handoff in one line.
- **N2 `0031` drawing page: move a section, then record the seat astride the brook** (`research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`; its notes `.drawing.notes.html`).
  1. THE MOVE. Reserve the new question: `make reserve KIND=question KEY="<heading>"` with a heading a reader asks from
     the map, for example "How our maps keep a scattered farm within reach of its rice". It is a drawing-only question,
     as the bund-bends question (0284, read its files for the form: a `.drawing.html`, a `.drawing.notes.html`, and no
     research page) is. The new page gets its own `<h2>`, its tags marker filled from `research/tags.json`, an opening
     account (the moved paragraph serves, or one sentence before it), and the two blocks and the rule paragraph
     unchanged, their HTML comments with them. A note moves with the sentence that cites it; no note lives in two places.
     Where the section stood, leave the pointer in the one form the triage follows: `<a class="moved" href="<the new
     page's file name>">` with the new page's title as its text, in a short paragraph (the record's `CLAUDE.md` gives the
     form; a plain link is refused). If the page's `Grounds:` or `Evidence:` comment names what moved, bring it in line
     and no further.
  2. THE SEAT, only after `make question-sizes` shows room. The block "Where does a village's cluster sit?" says: "Our
     hamlets take it wherever chance sets their fall, a deliberate deviation: the land falls away from the wind or across
     it, its high side windward or level, so houses keep their back to the wind" and "Where a map declares a fall toward
     the wind, no margin is high and windward: the cluster takes the high, dry one, its back to the hill". It does not
     say what a fall SQUARE ACROSS the wind does when its windward flank is wet ground (item N1). What the map draws
     (feature 449 T426): such a cluster does not turn its back to the hill - that seat is only for a fall toward the
     wind - but, once every other margin is refused, sits at the head's windward corner astride the brook, its houses on
     both banks, and leaves by its open bank. Add a NEW `<li>` after that block saying so, labeled a GUESS: the stream
     question's drawing page already has "Where the site that faces the fields and has its back to the winter wind is
     crossed by the brook, the houses are built on both banks." (link
     that page: the drawing page of question 0035, its file name found by listing the questions directory), and that this corner is the site left to such a
     hamlet is this project's decision, no page read saying where a village sat when its windward side was wet (GROUNDS
     note). Link the marsh drawing page for the wet flank. Tag:
     `<span class="item" data-item="seat-astride-brook-windward-corner" data-label="GUESS" data-guess="That a hamlet whose fall runs square across its wind, its windward flank wet, sits at the head's windward corner astride the brook: no page read says where such a village sat; houses on both banks of a brook that crosses the best site are recorded on the stream question's drawing page."></span>`.
     The `data-guess` may add the measurement, taken from the code's own claim and not from this brief (read only:
     `grep -n -A3 "a seat astride the brook" rust/phases/src/seat.rs`; it counts the valley rolls that took this seat,
     measured 2026-11-24). Name no engine identifier
     in visible text. Add the item to the guess list of the page's `Evidence:` comment in a few words.
  3. Report in the handoff the new question's number and file names, and the prose size of both pages.
- **N3 `0081` drawing page: from which point of a cluster its way out is asked** (`research/questions/0081-village-lanes.drawing.html`; its notes `.drawing.notes.html`).
  The blocks "A track keeps off wet ground." and "The track out runs off the edge of the map." say where a track may
  run, not where in the cluster it starts when the map asks whether a site has a dry way out at all. What the map does
  (feature 449 T426): a site is asked from the CENTER of its cluster's ground; a site with no dry way out from there is
  passed over for the next; and only once no site is left are the passed-over ones asked again from two more points,
  six-tenths of the way from the center to each end of the cluster's band, a site with a way out from either being kept.
  Add a NEW `<li>` after "The track out runs off the edge of the map.", labeled a GUESS, a fallback of ours: no page read
  says from which point of a village its road out left; the six-tenths is where the band's ground is already sampled
  (GROUNDS note). Tag `data-item="way-out-from-band-ends"`, `data-label="GUESS"`, a `data-guess` in the standard form
  naming the 0.6 of the band's half-length. Link N2's block on 0031 for the one seat this keeps.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p11-seat-followups-write.md`: `- SECTION=0057 0031 0081`
   (plus any split page), one line per item `N<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
