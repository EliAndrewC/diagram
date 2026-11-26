# Brief - feature 449 T420 and T427 (0018, 0019), session 1: write (the ring canal's width on a dike-pond block, what the creeks' code does that no page says, the least pond's second case, and one office named two ways)

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

**Claims.** The orchestrating session claimed 0018 and 0019 for feature 449 before starting you; if an edit is refused as unclaimed, stop and report it in the handoff, use no escape.

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

**No research pass was run for this brief.** Its items record what feature 449 T420 built and T427 will build, which no
page states; four are drawing fallbacks of ours (GROUNDS notes). ONE touches a physical figure - the ring canal's width
on a dike-pond block - and its dated search already exists: the pass of 2026-11-24 at
`/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/pass-449-t420-dike-pond-channels.md` (its ring-canal section found no source
for a canal at a dike's inside foot at all), recorded on 0019's drawing notes as the absence note
`how-our-maps-draw-polders-weitian-waju-2` (at 9162aa3953 it ends "None of the pages read gives the course of a channel
leading to a polder's inlet sluice, or names a canal along the inside foot of a polder's dike."). Read that note; cite it
if its words cover the width (no source names such a canal, so none gives it a width), or add a like absence note dated
today that names the pass. If your own reading finds a
width for a canal at a dike's inside foot, write the finding and report `FOUND`. No new registry key is expected.

**Both pages were edited today by an earlier pair (P1) and its checks.** Read each block again before you edit it; the
quotations below are the pages at commit 9162aa3953.

**Left alone on purpose.** On 0018's drawing page: the block "The bank is drawn as planted ground: mottled earth under
rows of mulberry bushes." (a placeholder of feature 449 T422); the block "How wide is a canal between ponds drawn?" -
its figure "About 6 to 8 ft", its slug `creek-width-between-ponds` and its `data-guess` stay as they are (the engine's
claims cite them); every other existing tag. On 0019's drawing page: the blocks "A ring canal is drawn round the inside
foot of the dike, on the field side.", "The ring canal is drawn straight along the dike's inside foot, square at the
corners.", "The feeder is drawn straight from the wild pond to the inlet sluice." and "A channel is drawn along every
pond's edge." stand, tags and all - you ADD beside them. 0018's RESEARCH page is not edited (948 bytes of room): only one
phrase of its NOTES file (item K6). 0019's research page: nothing. The widths-ladder question (0068) is READ ONLY, and
another session edited its drawing page today: read the sentence you lean on again before you link to it (it read, at
9162aa3953, "A delivery ditch is never drawn wider than the canal feeding it."); if it has changed, report `OPEN`.

**Sizes at the start** (prose bytes of room under 20,000; the file less its item tags, so an HTML comment COUNTS and a
tag's `data-guess` does not): 0018 drawing 4,007; 0019 drawing 1,868. The 0019 page is tight: items K1 to K3 together
must stay under that. Put a measurement or a reason in the tag's `data-guess`, not in a comment, and keep each new block
to two or three sentences. If `make question-sizes` lists 0019 after K1 and K2, do NOT split the page for K3: write K3 on
0018's drawing page instead, after the block K4 adds (the engine's claim for it cites both pages), and say so in the
handoff. If K1 and K2 alone do not fit, stop, report `OPEN` with the sizes, and write neither.

## Cascade expected (for the coordinator; not your work)

What cites the changed pages at 9162aa3953, which of them STATE the thing changed, and - since the last pair showed that a
claim is re-owed only by a page it CITES, and that a claim saying "the page is silent" is cleared by the tool unread when
the page gains a NEW block - which claims need a DIRECTED check (`make claims-bundle UNITS=... REASON=... PAGES=...`).

- 0018 drawing page (18 pop-ups, 21 claims). Claims that state it, SHOULD re-check, all in `rust/phases/src/field/`:
  `ponds.rs` `LEAST_SHARE#the least pond` and `rounded#the least pond` (K5 rewords the block both quote; `rounded`
  already states the sliver: IN-STEP expected on both); `polder/creeks.rs` `creek_width#one width a block` (says "the page
  giving a range and no figure within it": IN-STEP, then restated to cite `one-creek-width-a-block`), `CREEK_FT#the
  creek's width`, `eased#room for the creeks`; `polder.rs` `ditches#the ring canal on a dike-pond block` (below),
  `ditches#the creeks' width`, `row_ditches#the row ditch's width`. Pop-ups SHOULD re-check: `hamlet/pond-canal` (the
  canal's own pop-up), `hamlet/fish-pond` (the least pond is its glyph's: it states nothing of it, a GAPS finding is
  possible). SHOULD clear: the other 16 pop-ups and 13 claims. Expect the triage to send on, as it did for P1, the five
  `choice/dikepond_split--*`, `hamlet/mulberry-dike`, `hamlet/fruit-dike` and `hamlet/fry-pond` for the least pond's
  reworded block: they returned clean then and should again.
- 0018 research NOTES (20 pop-ups cite the research page, no claim). One phrase of one note: no pop-up holds
  "commissioner" (grep at 9162aa3953). All 20 SHOULD clear.
- 0019 drawing page (14 pop-ups, 49 claims). Claims that state it: `field/polder.rs` `ditches#the ring canal on a
  dike-pond block` (cites 0018, 0019 and 0068's drawing pages; it says the pages give the ring canal "no width of its own"
  and that its trunks keep "the rice polder's rungs, 1.5 to 5.5 ft ... so a creek of 6 to 8 ft opens on a ring canal
  narrower than itself": DRIFTED fix: code EXPECTED until feature 449 T427 lands, which is T427's finding and no fault of
  this pair; then restated to cite `ring-canal-width-dike-pond`), `ditches#a creek's mouth on the ring canal` (says the
  page is silent: IN-STEP, then restated to cite `creek-mouth-on-ring-canal`), `polder/creeks.rs` `EASE_STEPS#the
  easing's steps` and `eased#room for the creeks` (then citing `pinched-mosaic-eased`), `DRIFT_SHARE#the mosaic's
  drift`, `Warp.at#the mosaic's drift`, `RING_FT#the ring canal`, `ditches#the ring canal`, `polder#the ring canal's
  place`, `driver/check.rs` `RING_CANAL#the ring canal` (the neighbors of the new blocks: IN-STEP). Every item here ADDS
  a block and rewords none, so the tool will probably CLEAR most of these unread: run the four named first
  (`ditches#the ring canal on a dike-pond block`, `ditches#a creek's mouth on the ring canal`, `EASE_STEPS#the easing's
  steps`, `creek_width#one width a block`) as a DIRECTED check if it does. Pop-ups SHOULD re-check: `hamlet/pond-canal`,
  `choice/pond_layout--mosaic` (it says "How strongly the lattice bends is set by eye"),
  `choice/field_archetype--mulberry_dike_fishpond`, `choice/water_source_position--corner_high` (the ring canal's line).
  SHOULD clear: the other 10 pop-ups and about 39 claims.
- A claim that states the changed fact and cites NEITHER page: `field/polder.rs` `ditches#the widths` (cites 0068's
  drawing page only; it carries the ring canal's trunk rungs). It is not owed by this pair: a DIRECTED check with
  `PAGES=<0019's drawing page>`, and T427's builder adds the citation.
- The pop-up side (pop-ups are edited by the coordinator from the checks' EDITs, never by a page session; the detail is
  `/home/agent/.claude/jobs/c6fd72d1/tmp/cascade/p1-cascade.md`, judgment (b)):
  - `hamlet/pond-canal` SHOULD come to carry the width guess on its Guesses tab (the 6 to 8 ft of the creeks and, after
    this pair, the ring canal no narrower than them: no pop-up holds "6 to 8 ft" or `creek-width-between-ponds` today),
    and SHOULD lose the Depiction sentence "not every dike-pond hamlet need have had water a boat could travel", which
    sits against its own About tab and 0018.
  - `hamlet/fish-pond` still says flatly that in the Pearl River delta the ponds "lay in a mosaic among winding rivers"
    (the 1678 chessboard was added to `choice/pond_layout--mosaic` and `hamlet/pond-canal`, not here).
  - `hamlet/sluice-gate` still states "the intake stood at the ring's upstream head and the outlet at its downstream
    tail" as fact, the reading `hamlet/pond-canal` now gives as "most likely".
  The last two are cleared unread unless the triage sends them on: a directed pop-up check, or a hand EDIT.

## Your items

- **K1 `0019` drawing page: the ring canal's width on a dike-pond block** (`research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html`; its notes `.drawing.notes.html`).
  No page gives the ring canal of a dike-pond block a width: this page gives its place and its line; the dike-pond
  question's drawing page (0018) gives the creeks' width only; the parcels question (0022) none; the widths-ladder
  question's drawing page (0068, read only) ranks a rice field's channels and names no dike-pond channel. Add a NEW `<li>`
  after the block "The ring canal is drawn straight along the dike's inside foot, square at the corners.": on a dike-pond
  block the ring canal's reaches are drawn no narrower than the block's creeks, a GUESS. Say why in the page's own
  terms: the creeks between the ponds open on the ring canal, and a channel is never drawn wider than the one it joins
  (link the widths-ladder drawing page, where the rule reads "A delivery ditch is never drawn wider than the canal feeding
  it."); the creeks' own width, about 6 to 8 ft, is itself a GUESS (link 0018's drawing page). Write the BOUND, not a
  figure: the code that draws it is feature 449 T427, not yet built. A rice polder's ring canal keeps the ladder's
  widths: say so in a clause. The note: as the "No research pass" paragraph above says. Tag:
  `<span class="item" data-item="ring-canal-width-dike-pond" data-label="GUESS" data-guess="The ring canal's width on a dike-pond block, no narrower than the block's creeks: no source read names a canal at a dike's inside foot, so none gives it a width; it is tied to the creeks' own guessed 6 to 8 ft."></span>`.
  (T427's claim will cite this item id: keep the slug.) Add "the ring canal's width on a dike-pond block" to the guess
  list of the page's `Evidence:` comment (line 4), and no more words there than that.
- **K2 `0019` drawing page: where a creek meets the ring canal** (same files).
  A NEW `<li>` after K1's: a creek between ponds stops where it meets the ring canal - its end is drawn to the ring
  canal's middle line and no farther, never across it onto the dike's foot. A GUESS, a drawing fallback of ours: no page
  read says how a channel between ponds met a canal at the dike (GROUNDS note, `this project's decision`). Tag
  `data-item="creek-mouth-on-ring-canal"`, `data-label="GUESS"`, a `data-guess` in the standard form (it may hold the
  measurement: drawn through, 4 of some 2,700 creek ends over 80 rolled blocks reached the dike's inner face, measured
  2026-11-24, feature 449 T420). Word it so it stays true whatever the ring canal's width (K1).
- **K3 `0019` drawing page: a mosaic that would pinch a creek is bent less** (same files).
  The blocks "The mosaic bends the lattice but keeps every pond four-sided." and "How strongly the lattice bends is a
  calibrated liberty." stand. No page says: where the full bend would leave a corridor between two ponds narrower than
  the creek drawn in it, that block is bent less - the bend eased a twentieth at a time until every corridor holds its
  creek - so the creek is never laid over a bank and no pond is drawn smaller to make room; a block no corridor of which
  is pinched keeps the whole bend (Kuwabata's does). Add a NEW `<li>` after "How strongly the lattice bends ...", labeled
  a GUESS, a fallback of ours (GROUNDS note). Tag `data-item="pinched-mosaic-eased"`, `data-label="GUESS"`; the
  `data-guess` may hold: 13 of 51 rolled mosaics held a corridor of 4 to 7 ft under a creek of 6 to 8, the worst needing
  its bend about a fifth gentler (measured 2026-11-24, feature 449 T420). Name no engine identifier in visible text. If
  the page has no room, this item goes on 0018's drawing page (see "Sizes at the start").
- **K4 `0018` drawing page: one creek width to a block** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html`; its notes `.drawing.notes.html`).
  The block "How wide is a canal between ponds drawn?" ("About 6 to 8 ft, a GUESS.") gives a range. No page says which
  width a map takes within it. Add a NEW `<li>` after it: each dike-pond block takes ONE width, chosen by chance from the
  map's seed anywhere in the 6 to 8 ft, and every creek of the block is drawn at it, down a column and across a row,
  from end to end with no taper. A GUESS, a fallback of ours: the page names no wider or narrower kind of creek and no
  end to taper toward (GROUNDS note). Tag `data-item="one-creek-width-a-block"`, `data-label="GUESS"`.
- **K5 `0018` drawing page: the least pond is drawn in two cases, and the page says one** (same files).
  The block reads: "A parcel too small for its bank still gets a pond." - "Where the bank that the village's split asks
  for is more than a parcel holds, the water is still drawn, a tenth of the parcel across. That least pond is a GUESS, a
  fallback of this project's drawing, and rests on no source." The drawing also draws the least pond in a second case
  (feature 449 T420): where the parcel does hold its bank, but the water left inside it would be a sliver - any side of
  it shorter than a tenth of the parcel's same side. Restate the block so it says BOTH cases (the least pond is the
  floor: no water is ever drawn thinner than a tenth of its parcel across); the lead sentence may widen to match. This is
  the ONE stated exception to the rule above on existing tags: the tag `least-pond` keeps its `data-item` and
  `data-label`, and its `data-guess` is rewritten to cover both cases, because the old text would misstate the block
  (no pop-up cites `least-pond` at 9162aa3953, so none is owed by it). Say in the handoff the old and new `data-guess`.
  The note `how-our-maps-draw-dike-ponds-sangji-yutang-4` stays (reword it only if it names the one case).
- **K6 `0018` research NOTES: one office, one name** (`research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.notes.html`, note `wuhurec-wanchun-5`).
  The note's second translated passage reads "Zhang Yong, the fiscal commissioner of Jiangdong"; the same sentence of the
  same source is translated on 0019 as "the transport commissioner of Jiangdong" (0019's drawing notes, note
  `wuhurec-wanchun`) and "transport commissioner of Jiangdong" (0019's notes, note `wuhurec-wanchun-5`). The original
  (0018's `.originals.html`, `wuhurec-wanchun-5#2`) is 「嘉祐六年（1061年），江东转运使张颙，判官谢景温力主修复芜湖县万春圩」: 转运使.
  Change the ONE word on 0018 - "fiscal" to "transport" - and nothing else in the note; first `grep -rn "transport
  commissioner" research/questions/0019-*` to take the exact form the record already uses (the glossary holds the term
  `transport commissioner`), and grep 0018's pages for any other "fiscal". WHY IT IS HERE AND NOT LATER: the same one-word edit, made by hand after the last
  pair's checks had run two rounds, re-owed three units a third round each (`quote-check`, `record-format` and
  `translation-check` on 0018) and was put back. Made in THIS session, with the items above, it is read once by the
  checks the next session runs anyway. Do not touch 0019's two notes: they already agree.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no question of yours listed); split a page over the cap along its topics.
   Then `make rust-test CRATE=rust/gate/crates/registry` (it reads every tag).
2. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p10-polder-followups-write.md`: `- SECTION=0018 0019`
   (plus any split page), one line per item `K<n> <DONE|NARROWED|LEFT> - <what changed, or why left>`, any `FOUND`, each
   page's prose size before and after, every file you changed under `## Files`, every new item id and every new registry
   key, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.
