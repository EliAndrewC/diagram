# Page-session briefs for the research-page corrections (449 T420, T425; 452 T001-T003, T016 and page items)

Written 2026-11-24 from the handoff `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T420-aa9dd5b481a992656.md`; every
target sentence re-quoted at HEAD ac2a708582 (no research page changed since the handoff read them). Sessions are listed in
RUN ORDER. Before each: `make research-claim Q="<stems>" FEATURE=<n>` for the stems nobody holds, and the last pair's files
committed by name (else the next check's `make record-owed` names the last pair's units). Run from the clone
(`cd /diagram/.clones/diagram-backlog`). Every write brief carries a "Cascade expected" section (above `## Your items`)
naming the pop-ups and claims that SHOULD be re-checked against those that should clear; the one-line prediction below is
its summary. Each write brief was counted with `scripts/gates/l7r-gate.sh brief-load research <write> <check>`; the counter's
line is quoted. `_check-template.txt` and `_mkcheck.py` in this directory generated the check briefs; they are not briefs.

## 1. P1 dikepond

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p1-dikepond-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p1-dikepond-check.md"`
- Counter: `write 3 p1-dikepond-write.md: 0018, 0019, 0022`; `check 0`.
- Pages: 0018 research and drawing; 0019 drawing (its research page untouched, 48 bytes of room); 0022 drawing.
- Questions 3; new registry keys est. 2-3 (Wujun zhi chapter 19 for Jia Dan; Chen 2021 at resci.cn; maybe none other).
- Serves: 449 T420 (the page states the canal's width, "about 6 to 8 ft, a GUESS", item `creek-width-between-ponds`, for
  the code's claim to cite); 449 T425 (0022 "never uniform rectangles", 0019 "no channel runs outside the dike", the G rows
  of 0018 and 0019).
- Checked: no page states a pond channel's width today (0068's widths ladder names no polder or dike-pond channel), so
  "about 6 to 8 ft" contradicts no page; the engine's 1.2-2.5 ft is T420's code to change. Four claims on pond and
  polder channels cite 0068's drawing page (`field/polder.rs` x3, `driver/polder.rs` x1): P1 does not edit 0068, so they
  are not owed by it, but T420's code change will owe them.
- Order: before T420's code. Claims 0018, 0019, 0022 for 449 first (nobody holds them). The T422 "mottled" sentence on
  0018's drawing page is NOT touched (both briefs say so); a later brief carries it if T422 reports a page correction.
- Cascade predicted: re-check `hamlet/pond-canal`, `choice/pond_layout--mosaic`, `choice/field_archetype--mulberry_dike_fishpond`,
  `choice/field_archetype--polder_grid`, `choice/water_source_position--corner_high`, `choice/pond_layout--grid`,
  `hamlet/fish-pond`, `hamlet/sluice-gate`, the two `choice/leftover--*` (and `hamlet/perimeter-dike` if the reed depth
  lands); claims: 4 on 0018 (ponds.rs x3, landuse.rs `REACH_FT`), 14 on 0019 (ring canal, feeder, interior ditches, the
  mosaic's drift, reed strips), 1 on 0022 (`polder#never uniform rectangles`). Should clear: about 13 of 0018's pop-ups,
  6 of 0019's, 2 of 0022's; 5 + 31 + 20 claims.

## 2. P5 sheet

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p5-sheet-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p5-sheet-check.md"`
- Counter: `write 3 p5-sheet-write.md: 0001, 0038, 0090`; `check 0`.
- Pages: 0038 drawing; 0090 drawing; 0001 research (and its notes).
- Questions 3; new registry keys est. 0.
- Serves: 449 T425 (the small roofed thing's 6 ft, the notice board's 40 ft, 0001's "within the walls").
- Order: before the `sun.rs` and `compound.rs` claims are restated (to cite `small-roofed-thing-6-ft` and
  `notice-board-within-40-ft`). Claim 0038 and 0001 for 449 first (0090 is this clone's already).
- FORM CHOSEN for the GM's ruling on 0001, for the coordinator to confirm: the visible sentence states the setting's rule;
  the ruling's date and words, and that `l7r.md` and `budgets.md` still say otherwise, go in an HTML comment beside it; the
  clause's footnote is a GROUNDS note (`no source is owed: this project's decision<!-- the GM's ruling of 2026-11-24 ... -->`),
  the form of 0137's drawing-notes note `how-our-maps-size-and-lay-out-a-domain-capital`. This is what the record's
  CLAUDE.md asks (rule 2: "never as a GM ruling ... the ruling, its date and words go in an HTML comment"), so the
  discrepancy with the notes files is NOT stated visibly. `l7r-budgets-4` stays under the farmers finding only, narrowed
  on 0001's own notes file. If the coordinator wants the discrepancy visible, that is one sentence to add to item S3.
- Cascade predicted: re-check 3 claims (`sun.rs` `SMALL_BUILDING_FT`, `SMALL_BUILDING_SQFT`; `compound.rs`
  `NOTICE_BOARD_MAX_FT#board by the gate`, which quotes "within about 15 ft" and must be restated) plus `place.rs`
  `kinds#what each tier is` (should return IN-STEP) and the pop-up `sheet/notice-board` (states no distance: IN-STEP).
  Should clear: all 19 pop-ups on 0038's drawing page (none states the six-hour check), 11 of 12 on 0090's,
  `choice/cluster_shape--split`, and 13 + 27 + 1 claims.

## 3. P2 water

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p2-water-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p2-water-check.md"`
- Counter: `write 4 p2-water-write.md: 0058, 0059, 0068, 0072`; `check 0`.
- Pages: 0068 drawing (one table cell; 19 bytes of room, the reword costs 4); 0058 drawing; 0072's two NOTES files only;
  0059 drawing.
- Questions 4; new registry keys est. 0.
- Serves: 449 T425.
- Order: none. Claim 0068, 0058, 0072 for 449 first (0059 is this clone's).
- Cascade predicted: re-check `hamlet/irrigation-ditch` and `channels.rs` `SUPPLY_W#supply canals` (0068);
  `margins.rs` `ranked#not on the wet toe` (0058, IN-STEP expected; `hamlet/marsh` states only the 90 ft and should clear); `brook.rs` `brook#the tap's stride`
  (then restated to cite `brook-line-below-intake`), `choice/intake_place--shoulder`, `hamlet/stream` (0059). 0072:
  everything should CLEAR (notes only; no pop-up holds "northeasterly"). Should clear: 6 + 7 + 15 + 14 pop-ups and
  about 13 + 2 + 15 + 18 claims.

## 4. P7 rowhouse

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p7-rowhouse-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p7-rowhouse-check.md"`
- Counter: `write 1 p7-rowhouse-write.md: 0097`; `check 0`.
- Pages: 0097 research (3,709 bytes of room: a split is allowed for in the brief) and drawing.
- Questions 1; new registry keys est. up to 6, ranked in the brief (ja.wikipedia 御城番屋敷 first; Tarumizu pdf; en.wikipedia
  Former Yamauchi Residence; Hikone pdf; two mlit pages; GJTSJC chapter 1501 only if the China sentence is written).
- Serves: 452 T003.
- Order: BEFORE P9 (both edit 0097; P9 adds one pointer). Whichever of P7, P8, P9 first needs GJTSJC 第1501卷 reserves it;
  each brief says to look for it first. Claim 0097 for 452.
- Cascade predicted: re-check `sheet/retainers--quarters` and `sheet/barracks` (both state "80 to 145 ft": DRIFTED
  expected, the coordinator restates them), `sheet/servants--quarters` (states Shibata's "145 by 24 ft": IN-STEP), and
  `docs/buildings.md` `Outer court#barracks`. Should clear: `sheet/armory`, `door`, `gatehouse`, `granary`, `karo-s-house`,
  `main-gate`; the staff-housing-knob claim; the five `program_rules.rs` claims and `emit.rs` `building#dwelling walls
  across the long side`.

## 5. P8 court

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p8-court-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p8-court-check.md"`
- Counter: `write 1 p8-court-write.md: 0099`; `check 0`.
- Pages: 0099 research (a new section; 5,829 bytes of room) and drawing (one new GUESS item).
- Questions 1; new registry keys est. 4-5, ranked in the brief, cap 10 (Wang Huizu; Tani 2008; Staunton 1797; the Edo
  plan of 1841 if it needs its own key; GJTSJC 第1501卷 if cited and not yet reserved).
- Serves: 452 T002 (the record half; the county example's doors are T002's drawing step, not the session's).
- Order: independent of P7 and P9 except for the shared 第1501卷 key (look first, then reserve). Claim 0099 for 452.
- Cascade predicted: re-check `sheet/hearing-court` (a GAPS finding likely) and `sheet/outer-court`; claims
  `docs/buildings.md` `Outer court#hearing court`, `#hearing court posts` and `emit.rs` `hearing#hearing court posts`
  (IN-STEP expected). Should clear: `sheet/clerks--seats`, `day-office`, `genkan`, `kneeling-positions`,
  `magistrate-s-dais`, `office-hall`, `official-study`, and the other 10 claims (mats, dais, sand floor).

## 6. P9 servants

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p9-servants-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p9-servants-check.md"`
- Counter: `write 2 p9-servants-write.md: 0097, 0331`; `check 0`.
- Pages: 0331 research (it has no drawing page); 0097 research (ONE pointer sentence, or none: `M2 LEFT`).
- Questions 2; new registry keys est. 2-3 (道光巢縣志 卷04; Nishizawa 1988; 第1501卷 only if cited and not yet reserved).
  Also appends ONE download-list entry (Ch'u T'ung-tsu chapters IV-V, naming the existing entry 141) with
  `make download-add` - the session's one write outside `research/questions` and the registry.
- Serves: 452 T001.
- Order: AFTER P7's pair is committed (both edit 0097's question page). Claim 0331 and 0097 for 452.
- Cascade predicted: re-check `sheet/barracks` (a GAPS finding possible: Joge's manservants' room) and
  `sheet/retainers--quarters` on 0331; `sheet/servants--quarters` on 0097 (IN-STEP). Should clear: `sheet/karo-s-house`,
  the staff-housing-knob claim (unless it states a silence on servants' rooms), and the other eight pop-ups and two
  claims of 0097. `sheet/servants--quarters` does not cite 0331 today: reaching it is a pop-up edit, not a cascade.

## 7. P6 452 pages

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p6-452pages-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p6-452pages-check.md"`
- Counter: `write 3 p6-452pages-write.md: 0093, 0101, 0220`; `check 0`.
- Pages: 0093 drawing; 0101 drawing; 0220 drawing (its research page untouched, 915 bytes of room); the registry entry
  `research/sources/010-works-cited/4960-jawiki-yashikigami.html`.
- Questions 3; new registry keys est. 0.
- Serves: 452 T016 (the gatehouse's two seats), the 0101 page item (the privy narrowed to a samurai house's), 452 T012
  (the three EDITs of `reply-452-t012-source-applicability-0220.md`, applied after the session confirms the Japanese on
  the archived page).
- Order: none. Claim 0093, 0101, 0220 for 452 (nobody holds them).
- Cascade predicted: re-check `sheet/gatehouse` (says only "beside": DRIFTED or GAPS expected), `sheet/main-gate`,
  `docs/buildings.md` `Walls and gates#gatehouse` (0093); `sheet/latrine` (IN-STEP: it already says it) and the three
  privy-size claims (`fixtures.rs` `PRIVY#privy size`, `docs/buildings.md` `#privy size`, `building-programs.md`
  `#privy size 5 ft square`) (0101); `sheet/compound-shrine`, `sheet/torii`, `docs/buildings.md`
  `Sacred features#compound shrine arch` (0220). Should clear: `sheet/armory`, `sheet/side-gate`, `sheet/inner-court`,
  `hamlet/household-shrine`, `sheet/approach`, and 6 + 27 + 9 claims. Source-applicability is re-owed on the entry.

## 8. P4 dry and dike

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p4-drydike-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p4-drydike-check.md"`
- Counter: `write 4 p4-drydike-write.md: 0006, 0011, 0013, 0027`; `check 0`.
- Pages: the drawing pages of 0006, 0011, 0013, 0027 (0006's research page untouched, 85 bytes of room).
- Questions 4; new registry keys est. 0 (1 if the search for a dike willow's crown width finds a page).
- Serves: 449 T425's G rows (dry.rs "off the water", the last band's start, states.rs "a resting plot from the green",
  dike.rs's crowns and gap); and, since 2026-11-24 (folded in from the follow-ups, item D5, re-counted: still
  `write 4`), 449 T423 (a dry plot's taper at a canal's bend, `dry-plot-taper-at-bend`) and 449 T421 (a barley hamlet's
  one band of the toe, `barley-hamlet-toe-band`), both on 0006's drawing page (3,863 bytes of room for three new
  blocks). The check brief's "What it wrote" and "Held" lines carry D5 too.
- Order: none. Claim 0006, 0011, 0013, 0027 for 449. The T422 "mottled" sentence on 0027's drawing page is NOT touched
  (both briefs say so); a later brief carries it if T422 reports a page correction.
- Cascade predicted, D5's part (0006 is cited by 41 claims at 9162aa3953): re-check `dry.rs` `Canal.frame#square to the
  canal`, `hem#square to the canal`, `PINCH_SHARE#the pinch`, `pinched#the pinch`, `build.rs` `TOE_SHARE#the toe`,
  `hem_bounds#the toe's band whatever the grain asks`, and pop-ups `hamlet/barley`, `hamlet/buckwheat`, `hamlet/millet`
  ("small rectangular plots": IN-STEP expected), `choice/winter_crop--barley`; DIRECTED check (they state D5's facts and
  cite 0011's drawing page): `dry.rs` `hem#a column's climb ends`, `build.rs` `build#the hem's line`, `hem_in#the hem's
  line`, `hem_bounds#the hem's climb`. So of 0006's nine pop-ups four or five now re-check, not none.
- Cascade predicted, the rest: additions only. Re-check about 12 claims that state the thing (`dry.rs` `refused#off the water`,
  `hem.rs` `CLEAR_FT#off the water`, `check.rs` `check#no dry plot on the water`; `dry.rs` `hem#the last band from the
  canal's start`, `build.rs` `build#the climb's order`; `states.rs` `states#a resting plot from the green`; `dike.rs`
  `CROWN_FT#the crowns`, `GAP_HALF_FT#the gap`, `dike#the rows cut at the gaps`, `polder.rs` `draw_polder#the band cut
  where a channel crosses`) and pop-ups `choice/fan_middle--wild`, `choice/winter_crop--none`, `hamlet/fallow`,
  `hamlet/perimeter-dike`, `choice/field_archetype--polder_grid` (all IN-STEP expected). Should clear: all 9 pop-ups of
  0006, 8 of 0011's, 2 of 0013's, 3 of 0027's, and about 63 claims.

## 9. P3 paddy

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p3-paddy-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p3-paddy-check.md"`
- Counter: `write 3 p3-paddy-write.md: 0008, 0014, 0284`; `check 0`.
- Pages: the drawing pages of 0284, 0014, 0008 (0014's research page untouched, 12 bytes of room).
- Questions 3; new registry keys est. 0 (1-2 if the search for azemame spacing finds a page).
- Serves: 449 T425's G rows (lattice.rs's bow; beans.rs's spacing, run, share of bunds, drowned bead; staged.rs's pond
  host; the pond's bank and margin).
- Order: none. Claim 0284, 0014, 0008 for 449. 0005 is NOT in this brief (decision 2: its own session, P3b, next).
- Cascade predicted: additions only. Re-check `hamlet/bund-beans`, `hamlet/field-pond` (IN-STEP expected) and about 8
  claims (`beans.rs` `bean_runs#a run's most and its spacing`, `#which bunds`, `#how many`, `RUN_BEADS#a run`,
  `settle#a drowned bead alone`; `staged.rs` `rice_pond#a four-sided host`, `#never a resting plot`; `features.rs`
  `pocket_pond#the pond's form`). Should clear: both pop-ups of 0284, 4 of 0014's, 4 of 0008's, and about 27 claims.

## 10. P3b paddy split

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p3b-paddy-split-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p3b-paddy-split-check.md"`
- Counter: `write 1 p3b-paddy-split-write.md: 0005` (the new question it reserves is not on disk yet, so not counted;
  the session ends with 2); `check 0`.
- Pages: 0005 drawing (97 bytes of room today) and a NEW drawing-only question (reserved by the session).
- Questions 1 + 1 new; new registry keys 0.
- Serves: 449 T425's G row "a half-row between counts" (lattice.rs:88).
- Order: last. Claim 0005 for 449. No cheaper honest route was found: the half-row is a matter of a basin's LENGTH and
  count, the topic of 0005's own size section (the block giving "26 to 36 ft" is there), not of a bund's bends (0284),
  so the bullet belongs on 0005 and the page must be split first.
- The split chosen: the rice-shoots section (the paragraph "Inside its bunds, the paddy shows its rice as shoots ..."
  and its four blocks, about 2,600 bytes) moves whole to the new question behind a `<a class="moved">` pointer. Chosen
  over the handoff's suggestion (the basin-shape section) because it is the one section with NO item tag (the shape
  section holds `point-refuse-cut-off` and `-2`, cited by page) and no engine claim states anything in it.
- Cascade predicted: a move plus one added bullet. Re-check `hamlet/paddy` (the one pop-up that states the shoots: its
  `Drawing:` line must gain the new page - a pop-up edit) and `lattice.rs` `cuts_counted#a half-row between counts` (then
  restated to cite `half-row-between-counts`). Should clear: the other 9 pop-ups and 31-33 claims.

## Summary

| run | id | stems | write-brief count | new keys (est.) | serves | must follow |
|---|---|---|---|---|---|---|
| 1 | P1 dikepond | 0018, 0019, 0022 | 3 | 2-3 | 449 T420, T425 | - (before T420's code) |
| 2 | P5 sheet | 0038, 0090, 0001 | 3 | 0 | 449 T425 | - |
| 3 | P2 water | 0068, 0058, 0072, 0059 | 4 | 0 | 449 T425 | - |
| 4 | P7 rowhouse | 0097 | 1 | up to 6 | 452 T003 | - |
| 5 | P8 court | 0099 | 1 | 4-5 (cap 10) | 452 T002 | - |
| 6 | P9 servants | 0331, 0097 | 2 | 2-3 | 452 T001 | P7 committed |
| 7 | P6 452 pages | 0093, 0101, 0220 | 3 | 0 | 452 T016, T012, the 0101 item | - |
| 8 | P4 dry and dike | 0006, 0011, 0013, 0027 | 4 | 0-1 | 449 T425; T423, T421 (item D5) | - |
| 9 | P3 paddy | 0284, 0014, 0008 | 3 | 0-2 | 449 T425 | - |
| 10 | P3b paddy split | 0005 (+1 new) | 1 | 0 | 449 T425 | - |

Ten pairs, twenty briefs. One stem is in two write sessions on purpose: 0097 (P7, then P9's single pointer).

## After each pair (the coordinator's follow-ups the briefs do not do)

- Restate the code claims that say "page silent" to cite the new item ids (gated engine comments): `ponds.rs` /
  `landuse.rs` (`pond-corners-rounded`, `least-pond`), T420's canal width (`creek-width-between-ponds`), `polder.rs`
  (`feeder-course`, `ring-canal-straight-square`, `channel-every-pond-edge`, `reed-strip-depth`), `sun.rs`
  (`small-roofed-thing-6-ft`), `compound.rs` (`notice-board-within-40-ft`; its claim text quotes "within about 15 ft"),
  `brook.rs` (`brook-line-below-intake`), `layout.rs` (`gatehouse-behind-setback`), `dry.rs` / `hem.rs`
  (`dry-plot-off-water`), `states.rs` (`resting-plot-one-state`), `dike.rs` (`willow-crown-size`,
  `rows-gap-at-channel`), `lattice.rs` (`comb-bund-bow`, `half-row-between-counts`), `beans.rs` (the four bean items),
  `staged.rs` / `features.rs` (`pond-host-four-sided`, `pond-bank-and-margin-width`). A session may rename a slug it
  finds taken: take the ids from each write handoff.
- Pop-ups the cascade should send back DRIFTED or with GAPS: `sheet/retainers--quarters` and `sheet/barracks`
  ("80 to 145 ft"), `sheet/gatehouse` (only "beside"), `hamlet/pond-canal` and `choice/pond_layout--mosaic` ("lattice of
  ditches"), `choice/water_source_position--corner_high` and `choice/field_archetype--polder_grid` (the ring canal's
  wavering line), `sheet/hearing-court` (enclosure), `hamlet/paddy` (its `Drawing:` line after the split).

## Dropped, and why

- The T422 "mottled" sentences (0018 drawing l.11, 0027 drawing l.10): NOT in P1 or P4 by the coordinator's decision;
  both write and check briefs say to leave them and that a later brief carries them if T422 reports a page correction.
- The mulberry crown (T425 G row): already recorded on 0018's drawing page (tag `bush-few-feet-across`) and on 0026's;
  P4 adds only the willow's crown on 0027 with a pointer.
- 0008's reed ring: inside the existing GUESS `much-pond-open-water`, whose `data-guess` names the reed belt; P3 adds
  only the host plot and the bank/margin widths.
- 0011's order of clearing: already a tagged GUESS; P4 adds only the last band's start, inside that block.
- `sun.rs` l.82/91 labels: already GUESS at HEAD (449 T424); only the page bullet (P5 S1) is owed.
- 0019's and 0006's and 0014's RESEARCH pages and both of 0072's pages: no prose added (48, 85, 12, 14/32 bytes of room).
- The Ch'u T'ung-tsu download entry: 141 exists; P9 appends a new entry for chapters IV-V naming it (decision 3).
- No item was dropped for "no longer conflicts": every target sentence the handoff quoted reads the same at HEAD
  ac2a708582 (`git diff --stat bb0c821c91 HEAD -- research/` shows only `research/source-attempts.jsonl`).

## Open for the coordinator

1. P5 S3's form for the GM's ruling (above, under P5): ruling in an HTML comment + a GROUNDS note, the discrepancy with
   `l7r.md` / `budgets.md` in the comment, not visible - the record's rule 2. Say if it should be visible.
2. P2 W2 (0058): the brief has the session restate "farmed and built on" to "farmed" AND leave no sentence asserting
   wells or houses stand in the strip; the block's last sentence ("would refuse every well standing there") and its lead
   may therefore move a few words. If only the two words should change, cut that instruction from W2.
3. P1 A3 gives the ring canal's straight line its own CONVENTION item (`ring-canal-straight-square`) and the reed
   strip's 280 ft its own GUESS (`reed-strip-depth`) rather than folding them into tagged or GM-ruled blocks.
4. P7 R2 offers the tag `barracks-length-ceiling` for the 145 ft limit and leaves its label (GUESS or DEVIATION) to the
   session, since rows of 270-300 ft are recorded and the plans stop at 145 ft by choice.
5. The claims sheet: this clone holds 0009, 0059, 0090, 0096, 0097, 0099, 0103, 0104, 0107, 0113, 0123, 0331 (449) per
   the handoff; every other stem above needs `make research-claim` before its session, and the 452 sessions need the
   stems claimed for 452.

# Follow-ups added 2026-11-24 (later): two more pairs, and item D5 folded into P4

Written from the builders' reports of 449 T420, T421, T423 and T426 and the round arbiter's follow-up on P1; every target
sentence quoted at HEAD 9162aa3953 (0018 and 0019 as P1's pair left them). The same generator files made them; the same
rules before each (`make research-claim`, the last pair's files committed by name, run from the clone). Sizes below are
the file less its item tags (the measure P1's check handoff reports; it reproduces P4's 3,863 for 0006).

## 11. P10 polder follow-ups

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p10-polder-followups-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p10-polder-followups-check.md"`
- Counter: `write 2 p10-polder-followups-write.md: 0018, 0019`; `check 0`.
- Pages: 0019 drawing (1,868 bytes of room: three new blocks, and K3 goes to 0018's drawing page if they do not fit);
  0018 drawing (4,007 of room); ONE word of 0018's research NOTES (`wuhurec-wanchun-5`); 0018's and 0019's research
  pages untouched. 0068 is read only (one link).
- Questions 2; new registry keys est. 0.
- Items: K1 the ring canal's width on a dike-pond block, written as a BOUND - no narrower than the block's creeks - a
  GUESS, `ring-canal-width-dike-pond`; K2 `creek-mouth-on-ring-canal`; K3 `pinched-mosaic-eased`; K4
  `one-creek-width-a-block`; K5 the least pond restated to its two cases (the tag `least-pond` keeps its slug and label,
  its `data-guess` rewritten: a stated exception, no pop-up cites it); K6 "fiscal commissioner" made "transport
  commissioner" on 0018 (the original is 转运使; 0019's two notes and the glossary say "transport").
- Serves: 449 T427 (its claim cites `ring-canal-width-dike-pond`), 449 T420's built facts, the arbiter's follow-up.
- Order: BEFORE 449 T427's code; AFTER P2's pair is committed (P2 edits 0068's drawing page, which K1 links to and
  quotes: "A delivery ditch is never drawn wider than the canal feeding it."). Claim 0018 and 0019 for 449 if P1's claim
  was released.
- The loop: K6 is made in the WRITE session, so `quote-check:0018#wuhurec-wanchun-5`, `record-format:0018` and
  `translation-check:0018#wuhurec-wanchun-5` are the check session's round 1. The check brief tells it: run each once;
  if the tooling calls one a third round (the counter may still hold P1's two), do not run it, do not put the word back,
  report it `OPEN` with the refusal's line; refuse any EDIT that renders 转运使 another way; apply every reply's EDITs
  before the second `make record-owed`.
- Cascade predicted: `field/polder.rs` `ditches#the ring canal on a dike-pond block` DRIFTED fix: code until T427 lands
  (it says 1.5 to 5.5 ft, "narrower than itself"); IN-STEP then restated to cite the new ids: `ditches#a creek's mouth
  on the ring canal`, `creeks.rs` `EASE_STEPS#the easing's steps`, `eased#room for the creeks`, `creek_width#one width a
  block`, `ponds.rs` `LEAST_SHARE#the least pond`, `rounded#the least pond`. The items ADD blocks, so the tool will
  probably clear the "page silent" claims unread: run those four as a DIRECTED check, with `ditches#the widths` (cites
  0068 only). Pop-ups: re-check `hamlet/pond-canal` (should gain the width guess on its Guesses tab and lose "not every
  dike-pond hamlet need have had water a boat could travel"), `hamlet/fish-pond`, `choice/pond_layout--mosaic`; expect
  the triage to send the eight least-pond pop-ups on again (clean last time). `hamlet/fish-pond`'s flat "lay in a mosaic"
  and `hamlet/sluice-gate`'s "upstream head ... downstream tail" are reached only by a directed pop-up check. Should
  clear: 16 + 10 pop-ups, about 13 + 39 claims, and all 20 pop-ups of 0018's research page.

## 12. P11 seat follow-ups

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p11-seat-followups-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p11-seat-followups-check.md"`
- Counter: `write 3 p11-seat-followups-write.md: 0031, 0057, 0081` (the new question it reserves is not on disk yet, so
  not counted; the session ends with 4, the cap); `check 0`.
- Pages: 0057 drawing (9,179 bytes of room); 0031 drawing (2 bytes of room: a MOVE first) and a NEW drawing-only
  question; 0081 drawing (3,798). 0035 and 0058 are read only.
- Questions 3 + 1 new; new registry keys 0.
- Items: N1 `toe-on-tapering-flank`, a DEVIATION that says what the map draws today (the wet ground climbs a flank that
  tapers inward downhill, to the head's corner); N2 the move, then `seat-astride-brook-windward-corner`, a GUESS; N3
  `way-out-from-band-ends`, a GUESS (the center, then 0.6 of the band's half-length either side).
- The split chosen: the section on a scattered farm's reach of its rice (the paragraph "A scattered farm fronts its own
  fields ...", its two blocks and the rule paragraph on twice the room per farm, about 2,100 bytes) moves whole behind a
  `<a class="moved">` pointer. It is the one section with no item tag; none of the 24 claims citing the page states it;
  no pop-up holds its words (grep).
- Serves: 449 T426 (landed; its claims `BAND_EXITS` and `open_at_an_end` say the pages are silent).
- Order: any time. 0058 is P2's (read only here); nothing of P11 waits on it. Claim 0057, 0031 and 0081 for 449.
- Cascade predicted: re-check `choice/cluster_position--high_margin` (the one pop-up stating the seat's rule) and
  `hamlet/marsh` (IN-STEP; GAPS possible on each); claims `seat.rs` `seat#the back to the hill where the wind cannot be
  backed`, `seat#a walled-in head gives way`, `BAND_EXITS#the way out from the band's ends`, `open_at_an_end#a seat
  astride the brook leaves by its open bank`, `seat/exit.rs` `Exit.has_exit#dry way out of the seat`, `driver/toe.rs`
  `toe_band#toe band edge`, `PAD#toe band edge` (IN-STEP expected on all). DIRECTED checks: `BAND_EXITS` (page-silent,
  cleared unread) with 0081's page; `open_at_an_end` with 0031's and 0057's pages (it cites 0035 and 0081 only);
  `seat/margins.rs` `ranked#not on the wet toe` (cites 0058) and `driver.rs` `stage_seat#the way out's walls` with
  0057's. Should clear: 2 + 41 + 9 pop-ups and 3 + 19 + 7 claims.

## Summary of the follow-ups

| run | id | stems | write-brief count | new keys (est.) | serves | must follow |
|---|---|---|---|---|---|---|
| 11 | P10 polder follow-ups | 0018, 0019 | 2 | 0 | 449 T427, T420 | P2 committed; before T427's code |
| 12 | P11 seat follow-ups | 0057, 0031, 0081 (+1 new) | 3 | 0 | 449 T426 | - |
| 8 | P4 dry and dike (item D5 added) | 0006, 0011, 0013, 0027 | 4 | 0-1 | 449 T425, T423, T421 | - |

Follow-ups the briefs do not do: restate the claims to cite the new ids - `field/polder.rs` (`ring-canal-width-dike-pond`,
by T427; `creek-mouth-on-ring-canal`), `field/polder/creeks.rs` (`one-creek-width-a-block`, `pinched-mosaic-eased`),
`seat.rs` (`way-out-from-band-ends`, `seat-astride-brook-windward-corner`, and 0031's page added to `open_at_an_end`'s
citations), `field/dry.rs` (`dry-plot-taper-at-bend`), `field/build.rs` (`barley-hamlet-toe-band`).

## Open for the coordinator (follow-ups)

6. P11 N1 (0057): the brief has the page record what the map DRAWS on a tapering flank, labeled DEVIATION (the record's
   springs are at the toe; the wet flank is the point-by-point rule's consequence), and report `OPEN` whether the code
   should cut the band off at the field's lower corners instead. That label and that route are this writer's choice
   under "where the record is silent, the easier route, and say which": if the wet flank is to be treated as a defect of
   the toe's code, cut N1 and file the code task instead.
7. P4 D5: the GM's ruling of 2026-07 in 0006's comment reads "dry plots are rectangles laid out against the canal"; the
   brief keeps the block and its comment, adds one clause excepting a bend, and records the taper (449 T423, landed) as
   a GUESS. Say if the ruling should hold the code instead.
8. P10 K1 leans on the existing absence note `how-our-maps-draw-polders-weitian-waju-2` (P1's pass of 2026-11-24 found
   no source for a canal at a dike's inside foot) for the ring canal's width; no new search pass was run for a WIDTH.
9. P10 K5 rewrites the `data-guess` of the existing tag `least-pond` (a stated exception, mirrored in the check brief).
10. NOT verified: that K1 to K3 fit 0019's 1,868 bytes (estimated at about 1,400; the brief sends K3 to 0018's page if
    not); N1's "above the head's corner, on the brook's far bank" (the coordinator's words, not in T426's handoff: the
    brief has the session confirm it or write "up the whole flank"); N2's count of rolls (the session reads it from the
    claim in `seat.rs`).
11. NOT verified: whether the round counter will read P10's first run of the three 0018 units as round 1 or as a third
    round (P1's cascade found the counter holding 1 where two rounds had run). The check brief covers both.


# Follow-ups added 2026-11-24 (evening): three more pairs, P12 to P14

Written from the two search passes of 2026-11-24 (`../passes/pass-449-t432-wet-ground-fan.md`,
`../passes/pass-449-t428-dry-plot-shape.md`), the T427 handoff and T431's task line, and the cascades of P2, P3 and P4;
every target sentence quoted at HEAD 7cb42eb6d1 (after P11's pair). The same generator files made them; the same rules
before each (`make research-claim`, the last pair's files committed by name, run from the clone). Sizes are the file less
its item tags. The asked-for P13 held five stems (d 0018, e 0008, f 0059, g 0014 and 0284), over the cap of four: g
became P14.

## 13. P12 fan and dry-plot findings

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p12-fan-dryplot-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p12-fan-dryplot-check.md"`
- Counter: `write 3 p12-fan-dryplot-write.md: 0006, 0011, 0057`; `check 0`.
- Pages: 0057 research (2,717 bytes of room: the finding) and drawing (8,129); 0006 drawing (2,442; a split if over);
  0011 drawing (14,661, one phrase).
- Questions 3; new registry keys est. 6-10, ranked in the brief with a drop order (Deng and Luo 2011; Tonami; ishizue
  03/03; RIHN yatsu; MAFF 承水路; Niiza 7104 and 7103; Mizuho; Ehime 1988; Niiza 7105 only if needed), each archived by the session's own
  `make archive URL= KEY=`; nine existing keys reused.
- Items: F1 the fan's wet ground at its toe and front margin, nothing on its sides (early-cleared farmland), a wet side
  attested only for a valley floor against a hill foot, farmed as cold wet paddy - on the research page; "edge" ->
  "perimeter" for Woods 2006 on both pages; `toe-on-tapering-flank` stays a DEVIATION, its grounds and its `data-guess`
  restated (a stated exception; no pop-up cites it). F2 0006's canal-squared block kept a RECONSTRUCTION, its grounds
  restated (strips squared to a road beside a drinking-water canal, Shinbori 1661; Yamamori 1992), its two limits (at
  Nobidome along the canal; none where it irrigated), a bend clause, and a NEW GUESS `dry-plot-taper-at-bend` (half a
  plot's length, an ABSENCE note). F3 0011 "from the toe end of the canal, up along it".
- Serves: 449 T432 (its page half), 449 T428 (closes with no code change unless the check finds otherwise), P4's cascade
  wording item.
- Order: BEFORE 449 T432's code (its rule comes from F1's block and the check's ruling). Claim 0057, 0006, 0011 for 449.
- The check handoff carries two named lines: `T432-APPLICABILITY` (source-applicability asked whether the narrowing
  side is a valley wall) and `T428 CLOSES|CODE`.
- Cascade predicted: re-check `hamlet/marsh` (GAPS possible), `choice/cluster_position--valley_mouth`, `--on_rise`,
  `toe.rs` `toe_band#toe band edge`, `PAD#toe band edge`; `dry.rs` `Canal.frame#square to the canal`, `hem#square to the
  canal` (DRIFTED fix: claim likely, the bend clause), `hamlet/barley`, `buckwheat`, `millet`, `choice/winter_crop--barley`;
  `dry.rs` `hem#the last band from the canal's start` (DRIFTED held since P4, restated), `build.rs` `build#the climb's
  order`. DIRECTED: `margins.rs` `ranked#not on the wet toe`, `seat.rs` `open_at_an_end#...`, `driver.rs`
  `stage_seat#the way out's walls`, `margins.rs` `SQUARE_EPS#the square end in` (PAGES=0057's two); `dry.rs`
  `PINCH_SHARE#the pinch`, `pinched#the pinch`, `hem#a column's climb ends` (PAGES=0006 drawing). Should clear: the two
  `fan_middle--*`, 3 `toe.rs` claims, 4 of 0006's pop-ups and about 35 claims, all 10 of 0011's pop-ups and 18 claims.

## 14. P13 polder and brook wording

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p13-polder-brook-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p13-polder-brook-check.md"`
- Counter: `write 3 p13-polder-brook-write.md: 0008, 0018, 0059`; `check 0` (0019, 0060, 0068 named read only; not
  counted).
- Pages: 0018 drawing (3,298 of room: item W1, because 0019's drawing page has 94 and a split would move a cited
  section; 0060's is the paddy's drains); 0008 drawing (11,134); 0059 drawing (5,054).
- Questions 3; new registry keys 0 (one archive search for a feeder's width; `FOUND` if it hits).
- Items: W1 `feeder-and-run-ring-width`, a GUESS: on a dike-pond block the feeder and the outfall's run beyond the dike
  are drawn at the ring canal's width (the easier route: one width through each sluice), its own ABSENCE note - the page
  leads the code; W2 `pond-bank-and-margin-width` restated as drawn (bank line about 2.5 ft out, under a foot of wet
  ground showing), its `data-guess` too; W3 `brook-line-below-intake` scoped (a bend-sited intake holds the line; a
  straight-sited one, 14-22 ft outside the corner, inside the 34 ft keep-clear line, steps out first), its `data-guess`
  too. Both `data-guess` rewrites are stated exceptions (no pop-up cites either slug).
- Settled in the brief: `RUN_W`'s 5.5 ft is NOT on 0060's drawing page (it gives the drainage-ditch class and a drain
  widening to its outfall, no figure); the 5.5 ft is 0068's drawing page's fan collector outfall. No page sizes a
  polder's feeder or run beyond the dike: T431's plan is right and `RUN_W`'s claim mis-cites 0060.
- Serves: 449 T431 (its page item first), 449 T425's rows from P2's and P3's cascades.
- Order: W1 BEFORE 449 T431's code; otherwise none. Claim 0018, 0008, 0059 for 449.
- Cascade predicted: re-check `polder.rs` `ditches#the widths` (cites 0018; DRIFTED fix: code until T431),
  `draw_channels#the pond canals named`, `hamlet/sluice-gate`, `hamlet/pond-canal`,
  `choice/field_archetype--mulberry_dike_fishpond` (GAPS possible); `hamlet/field-pond`, `staged.rs` `polder_stage#a
  rice polder's pocket pond`; `brook.rs` `brook#the tap's stride` (restated to cite the item), `#the shoulder intake`,
  `#the intake's place`, `choice/intake_place--shoulder`, `intake_siting--straight`, `--bend`. DIRECTED: `driver.rs`
  `RUN_W`, `driver/polder.rs` `FEEDER_W`, `polder.rs` `joins#the outfall's join`, `polder#the feeder`, `OUTFALL_LEG_FT`,
  `sluice_channel#the channel it shuts` (PAGES=0018 drawing; DRIFTED fix: code expected until T431); `driver.rs`
  `draw_field#the pocket pond's ring`, `driver/polder.rs` `draw_polder#the pocket pond's ring` (cite no page;
  PAGES=0008 drawing); `driver.rs` `BROOK_TAP_RUN` (MISLABELED since P2), `brook.rs` `brook#outside the crop` (PAGES=0059
  drawing). Should clear: about 14 + 4 + 13 pop-ups and 19 + 20 + 16 claims.

## 15. P14 bund research

- Run: `make page-session BRIEF="/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p14-bund-research-write.md /home/agent/.claude/jobs/c6fd72d1/tmp/briefs/p14-bund-research-check.md"`
- Counter: `write 2 p14-bund-research-write.md: 0014, 0284` (the new question it reserves is not on disk yet, so not
  counted; the session ends with 3); `check 0`.
- Pages: 0014 research (12 bytes of room: a MOVE first) and a NEW research-only question (the form of 0331); 0284
  drawing (9,172); the registry entry `37820-ishiguro-azemame-tool.html`.
- Questions 2 + 1 new; new registry keys 0 (1 if the bow search finds a page).
- The split chosen: the section "Why a hand-piled bund wavers ..." (its opening paragraph and five blocks, about 3,500
  bytes) moves whole behind a `<a class="moved">` pointer. No pointer form other than a move exists in the record's
  rules, and a plain link would cost bytes the page lacks. Chosen because 0014's research page holds no tag and no claim
  cites it (all 13 of 0014's claims cite the drawing page), it is a topic of its own (the grounds of 0284's drawing), and it leaves the
  bean section, B1's home, on 0014. Three of its notes are also cited by staying blocks; the brief says how.
- Items: B1 the move, then the Ishiguro finding (holes about 30 cm apart, two or three to a hole, one row down the
  bund) on the bean section; the entry's `What it is:` place-name (Takayanagi, Kashiwazaki, Niigata) sourced from the
  site or cut. B2 `comb-bund-bow` restated: no SOURCE gives a bow; the record's own reading (now on the new page)
  guesses a foot or two over a hundred feet - or the figure cited if the archive search finds one; its `data-guess` a
  stated exception (no pop-up cites it).
- Serves: 449 T425's G rows (P3's cascade: 0014's research page owed the Ishiguro finding; the 0284 / 0014 bow conflict).
- Order: none. Claim 0014 and 0284 for 449.
- Cascade predicted: re-check `hamlet/bund-beans` (GAPS likely: the spacing), `hamlet/bund` and
  `choice/plot_regularity--organic` (both state the moved section: their research lines must gain the new page - pop-up
  edits). DIRECTED: `beans.rs` `BEAD_STEP_FT#the beads' spacing`, `bean_runs#a run's most and its spacing` (PAGES=0014
  research); `lattice.rs` `BOW#the bund's bow`, `Lines.new#the bund's bow`, `Lines.u#the bow's shape` (PAGES=0284 drawing
  and the new page). Should clear: `hamlet/village-lane`, `hamlet/soy`; no claim is re-owed by either page.

## Summary of the evening follow-ups

| run | id | stems | write-brief count | new keys (est.) | serves | must follow |
|---|---|---|---|---|---|---|
| 13 | P12 fan and dry-plot findings | 0057, 0006, 0011 | 3 | 6-10 (cap 10) | 449 T432, T428 | - (before T432's code) |
| 14 | P13 polder and brook wording | 0018, 0008, 0059 | 3 | 0 | 449 T431, T425 | - (before T431's code) |
| 15 | P14 bund research | 0014, 0284 (+1 new) | 2 | 0-1 | 449 T425 | - |

Run order: P12, then P13, then P14 (P12 and P13 share no stem; any order works for them, but P12 first as asked). Then
449 T432's code after P12, 449 T431's code after P13.

Follow-ups the briefs do not do: restate the claims to cite the new ids - `dry.rs` `PINCH_SHARE`, `pinched`
(`dry-plot-taper-at-bend`), `hem#the last band from the canal's start` (`clearing-starts-plots-nearest`, "the toe end");
`driver.rs` `RUN_W` (cite 0068 for the 5.5 ft and `feeder-and-run-ring-width`), `driver/polder.rs` `FEEDER_W` (by T431);
`driver.rs` / `driver/polder.rs` `#the pocket pond's ring` (`pond-bank-and-margin-width`, as drawn); `brook.rs`
`brook#the tap's stride`, `driver.rs` `BROOK_TAP_RUN` (`brook-line-below-intake`); `beans.rs` `BEAD_STEP_FT` (the
plants' spacing on 0014's research page); `lattice.rs` `BOW`, `Lines.new` (`comb-bund-bow`); the pop-up edits of P14's
move (`hamlet/bund`, `choice/plot_regularity--organic`).

## Open for the coordinator (evening follow-ups)

12. P12 F1 puts the fan finding on 0057's RESEARCH page (its findings page; 0 claims cite it; the record's `CLAUDE.md`:
    a drawing-page pointer alone is not re-owed by a changed finding), with a fallback of the valley-wall block on the
    drawing page if 2,717 bytes do not hold it. T432's claim should then cite the research page.
13. P13 W1 chooses the route: the feeder and the run take the ring canal's width on a dike-pond block (one width through
    each sluice), under "where the record is silent, the easier route". The other route - a stated step at each sluice -
    is one sentence to swap in W1 before the run.
14. P13 W1 goes on 0018's drawing page, not 0019's (94 bytes of room), so it re-owes 0018's 18 pop-ups and 21 claims at
    triage, not 0019's.
15. P14 moves the wavering section rather than the bean section, so the Ishiguro finding lands on 0014's research page
    as asked; the cost is two pop-up edits (`hamlet/bund`, `choice/plot_regularity--organic`).
16. P13 W1's ABSENCE note (no page sizes a polder's feeder or its run) rests on an archive-only search the session runs;
    no web search pass was run for a width (as item 8 for P10's K1).
17. P12's check brief adds a question to the `source-applicability` dispatch (whether the narrowing side is a valley
    wall), with the files to read; that extra prompt line is untested against the agent guards.
18. NOT verified: that P12's F1 and F2 fit their rooms (estimated about 1,600 and 1,400 bytes; F1 falls back to the
    drawing page, F2 stops and reports `OPEN` rather than split 0006's drawing page unguided); W2's 0.8 ft and 3.6 ft and W3's 14-22 ft and 46-75 ft (the cascades' arithmetic from the constants: each
    brief has the session re-read the code); that Ishiguro's own site names Takayanagi (the brief has the session read
    it or cut the words); the Ehime 1988 page's URL (the pass gives only its archive id); whether the record's tooling
    accepts a research-only new question from `make reserve KIND=question` (0331 is one, so the form exists).
