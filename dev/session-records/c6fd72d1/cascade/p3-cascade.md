# P3 cascade (449 T425, commit 1f619aaa58) - the paddy pages' additions

Worked 2026-11-24 by a second worker after the first was cut off by a rate limit. Clone /diagram/.clones/diagram-backlog.
Nothing staged, committed, landed or pushed; no rust/ file edited. Bundles, replies and logs: /tmp/p3c/ and
/tmp/l7r-check/modal-hamlet-bund-beans-*.

## What the cut-off worker had done (reconstructed)

From `git diff dev/claims-index.json` against HEAD and /tmp/p3c/ (19:16):
- `make claims-triage` (log /tmp/p3c/claims-triage.log): "35 claim(s) cleared without a triage - a page each cites moved and
  no block it rests on did (feature 432, FR-005 a)". All 35 changed keys carry `cleared: mechanically ...`; no
  `claims-triage` agent, no impl-drift verdict, no verdict field changed. The 35 are the 13 claims citing 0014's drawing
  page (`beans.rs` 11, `driver.rs` `draw_field#the bean beads`, `settled#no bead in the water`) and the 22 citing 0008's
  (`features.rs` 15, `build.rs` 3, `staged.rs` 3, `driver.rs` `draw_field#the grave mound's size`).
- It BUILT three directed bundles (/tmp/p3c/dir-0284 3 keys, dir-0014 9 keys, dir-0008 6 keys; `claims-bundle ... REASON=`)
  and dispatched none (no prompt in .git/l7r-agent-prompts, no reply, no verdict). Nothing of the pop-up stage.

## Counts per stage

| stage | count |
|---|---|
| `make claims-owed` before (per the brief) | 35 claims owed a triage |
| `make claims-triage` | the TOOL cleared 35 of 35; 0 to an agent; 0 "rests changed" |
| owed impl-drift round | none: nothing was owed after the tool |
| DIRECTED check | 3 bundles, 23 claims (3 + 14 + 6; I added 5 keys to the 0014 bundle: the three `#no bead in the water`, `settle#a run shows at least two`, `bean_runs#a run's beads`), 3 `impl-drift` dispatches (23k + 27k + 31k tokens, 31-49 s each): **8 IN-STEP, 11 DRIFTED (10 fix: claim, 1 fix: code), 4 MISLABELED**; 1 page finding filed to specs/449-rust-codebase/found.jsonl |
| `claims-checked` | 0284: 3 of 3 recorded. 0014: exit 3, 4 lines HELD (451 T218). 0008: exit 3, 3 lines HELD. 16 verdicts recorded in the index, 7 held unrecorded |
| `make claims-owed` after | "no claim is owed" |
| `make record-owed UNANSWERED=1` before | 10 modal-depiction units |
| `make modal-triage` | the TOOL cleared 9 of 10; 1 (`hamlet/bund-beans`) to the `modal-triage` agent (10k tokens, 9 s): TOUCHES, rule A |
| `modal-depiction` on `hamlet/bund-beans` | 54k tokens: COVERAGE 1, TRUTH 1, LINKS 0; 2 EDITs applied |
| DIRECTED `modal-research` on `hamlet/bund-beans` (mine; the depiction agent's NOTED line asked for it) | 76k tokens, 241 s: ACCURACY 4, REFERENCES 1, GAPS 1; 5 EDITs applied |
| chain (iv): the EDITs re-owed `modal-form`, `modal-accuracy`, `modal-references`, `modal-gaps` | `modal-form` 23k tokens: 0 FIX, 2 NOTE, its 1 EDIT NOT applied; `modal-research` round 2 61k tokens: ACCURACY 0, REFERENCES 0, GAPS 0 |

Dispatch refusals: NONE. Neither decide-first (375 FR-003a) nor the `cascade@N` tripwire fired on any dispatch (each prompt
carried the DECIDE_OK line P2 used); no arbiter round was needed. `make modal-bundle FOR=modal-research` was refused once
for order ("a pop-up's checks run in order, form, then research"), and named its command; form ran first.

## The directed check's verdicts (quoted)

Bundle 0284 (PAGES = 0284 drawing; the claims cite 0005; none was in the owed 35):
- `lattice.rs::BOW#the bund's bow` **DRIFTED** - "`BOW = 0.15` matches the bow 0284's drawing page now records as a GUESS and
  this project's setting ... but the claim cites only 0005, which says nothing about a bow beyond the patchwork; fix: claim
  (also cite ...0284...drawing.html as the page that records the 15% GUESS); effect: none [§1; 0284 §44]"
- `lattice.rs::Lines.new#the bund's bow` **DRIFTED** - "the code is right ... but the claim cites only 0005, which does not
  cover the per-row bow or its 15% limit; fix: claim (also cite ...0284... for the per-row bow and its 15% GUESS); effect:
  none [§1; 0284 §43, §44]"
- `lattice.rs::Lines.u#the bow's shape` **IN-STEP** - "neither page gives the bow's form".

Bundle 0014 (12 of the 13 tool-cleared bean claims - `BEAD_R_FT#the bead`, the bead's 3 ft, was not bundled - plus `BEAD_STEP_FT` and
`BUND_SHARE`, which cite no page):
- `beans.rs::BEAD_STEP_FT#the beads' spacing` **MISLABELED** (HELD by T218) - "the claim says the record is silent on spacing
  and calls the 8 ft a GUESS; the page now gives the 8 ft as "a drawing convention, chosen so that each bead reads apart" and
  records the real spacing as about 1 ft; the label should be CONVENTION ...0014...drawing.html [§16, §17]"
- `beans.rs::BUND_SHARE#which bunds` **DRIFTED** - "the claim says 0014 gives "not how many", but the page now states "About
  three bunds in eight carry beans" and records the share as a GUESS; the code's (3, 8) matches; fix: claim; effect: none
  [§1, §19]"
- `beans.rs::bean_runs#a run's most and its spacing` **DRIFTED** (HELD) - "the claim says the page is silent on a run's length
  and on spacing; the page now gives "two to four beads long" as a GUESS and 8 ft as a drawing convention; the code matches
  both; fix: claim (run of at most four, a GUESS the page records in §18; spacing BEAD_STEP_FT, a CONVENTION the page records
  in §17); effect: none [§17, §18]"
- `beans.rs::bean_runs#how many` **DRIFTED** (HELD) - "the claim says the page is silent and says "only that some do", but the
  page now states three bunds in eight as a GUESS; the code's per-bund roll of 3 in 8 matches; fix: claim; effect: none
  [§1, §19]"
- `beans.rs::settle#a drowned bead alone` **DRIFTED** (HELD) - "the claim says the page is silent on a row that meets water;
  the page now says a bead in water "is left out, and a run left with a single bead is left out with it", a GUESS; the code
  drops each drowned bead and then any run under two, which matches; fix: claim; effect: none [§20]"
- `beans.rs::bean_runs#no bead in the water` **MISLABELED** - "the claim cites §16's "in a single row on the bund" as a
  finding, but the page now records the rule itself as "a GUESS of this project's own, a fallback of the drawing"; the label
  should be GUESS ...0014...drawing.html, held at settle [§16, §20]"
- `beans.rs::settle#no bead in the water` **MISLABELED** - "the page records the no-bead-in-water rule as a GUESS of the
  project's own, not a finding; the label should be GUESS ... with the code's pond and line clearances as stated [§16, §20]"
- `driver.rs::settled#no bead in the water` **MISLABELED** - "the page records the rule (canal, ditch, pond) as a GUESS of the
  project's own; the label should be GUESS ...: none inside a pond, none on a line's water [§16, §20]"
- IN-STEP (6): `RUN_BEADS#a run` ("at least two (§16); two to four, the page's GUESS (§18)"), `bean_runs#which bunds`,
  `bean_runs#the run on its bund` (""down the middle of the bund" means across the bund; where along the bund a row stands is
  still unstated"), `bean_runs#a run's beads`, `settle#a run shows at least two`, `driver.rs::draw_field#the bean beads`.

Bundle 0008 (4 tool-cleared claims and the two `#the pocket pond's ring` claims, which cite no page):
- `staged.rs::rice_pond#a four-sided host` **DRIFTED** (HELD) - "the code still takes only a four-sided plot (`x.ring.len() ==
  4`), but the claim calls the page "silent on the host plot's shape", and §23 now records this rule as this project's own
  GUESS ...; fix: claim; effect: none [§23]"
- `staged.rs::rice_pond#never a resting plot` **DRIFTED** - "the code still leaves out resting plots (`!resting.contains(i)`),
  but the claim calls the page "silent on a pond in a plot left to rest", and §24 now records the rule as a GUESS ...; fix:
  claim; effect: none [§24]"
- `staged.rs::polder_stage#a rice polder's pocket pond` **DRIFTED, fix: code** - "the claim puts the pond "over the block's low
  row", but `rice_pond` builds each basin's row as `usize::from(x.low)` from the non-resting, four-sided plots only, and
  `pocket_pond` takes the highest row present. So when every low plot is resting or not four-sided, the highest row is 0 and
  a plot that is not low can hold the pond; the code should return no pond when no host is low; fix: code; effect: map - a
  rice polder can show a pond in a plot that is not low, against "polder - on a low plot" and "Our maps sink each pond wholly
  inside one low plot" [§14, §15, §22, §24, §26, §27]"
  MY READ OF THE CODE (staged.rs:38-65, features.rs:93-116): CONFIRMED as written. `hosts` is filtered to non-resting
  four-sided plots, each given `row: usize::from(x.low)` (0 or 1); `pocket_pond(.., None, ..)` takes `last = max row` over
  the hosts and rolls among `row == last`. If no host is low, `last` is 0 and every remaining plot is a candidate, at the same
  55 in 100. The call site (staged.rs:132, the not-dike-pond branch) has no guard and nothing downstream drops a pond
  whose host is not low. REACH, read not run: `Plot.low` is `r + span == rows` (polder.rs:555), so every block has low
  plots, and `rest` never picks a low plot (polder.rs:808-809, "never a low plot"), so the resting filter never removes a
  low host; the hole opens only when EVERY plot of the block's last row is not four-sided (merged plots carry their two
  mid-side points, so more than four). A wrong outcome (constitution XIV) where reached; NOT MEASURED whether any pool
  map reaches it. A side reading: since a resting plot is never low, `rice_pond#never a resting plot`'s filter only ever
  acts inside this hole - with the fix it is redundant, and the page item `pond-never-resting-plot` describes a rule
  that follows from 0007's "never a low plot" rather than a separate fallback. Not fixed here (no
  rust edits by the brief). It is the two NEW guesses' own filters (four-sided, never resting) that open the hole, and no
  owed check could have found it: the claim was tool-cleared.
- `driver.rs::draw_field#the pocket pond's ring`, `driver/polder.rs::draw_polder#the pocket pond's ring` **DRIFTED** (both
  HELD) - "the code's figures (an outer ring at `rx + 2.5` with a 2.2 ft bank stroke) match the page, but "no page sizes the
  margin" is now untrue: §25 gives "bank ... about 2.2 ft wide, and the wet ground inside it about 2.5 ft wide" as a GUESS;
  restate citing the 0008 drawing page §25, dropping "no page sizes the margin"; fix: claim; effect: none"
- `features.rs::pocket_pond#the pond's form` **IN-STEP** - "the new §23 sentence on four sides is about the host plot, not the
  pond's outline".
- OUTSIDE THE CHANGE, filed by `claims-checked` ("filed, not fixed", found.jsonl +1 row): "0008 drawing §25 | the page says
  the wet ground is about 2.5 ft wide, but both drawers center the 2.2 ft bank stroke on the `r + 2.5` ellipse and the 1.2 ft
  rim stroke on the water's edge. The visible wet band is therefore about 2.5 - 1.1 - 0.6 = 0.8 ft, and the bank's outer edge
  stands 3.6 ft from the water | effect: page". MY READ (driver.rs:344-350): the geometry is as the agent says - the fill
  reaches `r + 2.5` and the 2.2 ft stroke straddles that line. So P3's NEW item `pond-bank-and-margin-width` copied the
  claim's words ("flooded ground 2.5 ft wide") and not what is drawn; the page item wants restating (the bank line centered
  2.5 ft outside the water's edge; about 1 ft of wet ground showing inside it), a difference of wording, not a wrong map.
- NOTED, NOT FILED: "the pond's 1.2 ft rim stroke has no claim of its own; it is only a line weight."

### 451 T218's seven HELD lines - answered from the code, not re-dispatched

T218 held 7 of the 15 not-IN-STEP lines as "it says the pages are silent" and asked for pages (0284 drawing, 0014 research,
0022, 0018, 0084, 0073 x2, 0236) that cannot settle them: each line says the opposite - the CLAIM says "silent" and the page
is NO LONGER silent - and each note already quotes the page block that ends the silence. The guard matched the word, not the
finding (P2 saw the same misdirection once; here seven times, and inconsistently: `rice_pond#never a resting plot` and
`BUND_SHARE` say the same thing and were recorded). `claims-checked` again printed "14 of 14 recorded" / "6 of 6 recorded"
beside "no verdict for ... - it stays owed" and exit 3, and `make claims-owed` then reads "no claim is owed". The seven are
settled by reading: the code matches the page in each (constants 8.0, (3, 8), (2, 4), `ring.len() == 4`, `+ 2.5` / 2.2
read by me), the claim's wording is behind the page. CHECKED with jq over the 23 keys: 16 carry today's verdict (8 IN-STEP, 5 DRIFTED, 3 MISLABELED) and the seven held still
read IN-STEP at their old dates (2026-11-01 to 11-22) and old notes; `make claims-report` lists the 8 recorded findings
and none of the seven. They are in the restate list below, which is where the fix lands.

## The pop-up stage

- Tool-cleared unread (9): `choice/grave_form--corner`, `--island`, `choice/lane_skeleton--none`,
  `choice/plot_regularity--organic`, `hamlet/bund`, `hamlet/field-grave`, `hamlet/field-pond`, `hamlet/field-rock`,
  `hamlet/village-lane`.
- `modal-triage` agent: "TOUCHES hamlet/bund-beans @ 0014...drawing.html - A: new beads-8-ft-apart block gives the village's
  30 cm planting spacing the pop-up states is not recorded".
- `modal-depiction` (round 1), both EDITs applied by `make apply-edits`:
  - COVERAGE "The 8 ft spacing is not on the tab (D2)": `it spread.` -> `it spread. The beads stand about 8 ft apart so that
    each reads on its own; in one village of terraced paddies the beans went into holes about 1 ft (30 cm) apart, two or
    three to a hole, so a drawn row holds far fewer beads than a bund held plants.`
  - TRUTH ""each bean plant" is wrong now that the beads are 8 ft apart": `The map draws each bean plant as a round bead about
    3 ft across` -> `The map draws the beans as round beads about 3 ft across`
  - NOTED, NOT FILED: the Guesses bullet "still says "no record of a row's length or spacing was found" ... The bullet's
    spacing half no longer holds" - "take it to modal-research / modal-form". After the EDITs the pop-up contradicted itself
    across two tabs, and `make record-owed` read "no record check is owed". So I sent the directed modal-research.
- DIRECTED `modal-research` (round 1), 5 EDITs applied:
  - ACCURACY 1+2 (M8/M11; "two labeled guesses that the glyph shows are missing from the Guesses tab"): the one bullet
    `- How many plants a bund carried and how close they stood: no record of a row's length or spacing was found, so how many
    beads the map sets along a bund is a guess.` -> `- How long a row of beans ran: no record of how long a stretch of bund was
    sown was found, and the one village account found points to longer rows, so the map's runs of two to four beads are a
    guess.` and a new bullet `- How many bunds carried beans: no record of the share of bunds sown was found, and in that
    village every household grew them, so the map's beans on about three bunds in eight are a guess, and probably too few.`
    (`drowned-bead-dropped` "needs no bullet ... a drawing rule belongs on the Depiction tab, where it is optional".)
  - ACCURACY 3 (pre-existing, not P3's): `In Asuka, as the rice cutting neared, the beans stood in a long, unbroken row along
    the` -> `In Asuka they stood in a row along the`. The agent made it conditional on the note; I read `nabunken-azemame-4`
    (the caption "azemame planted in a row on the bund") - it gives neither the season nor "long, unbroken". Applied.
  - ACCURACY 4 (pre-existing): `in one village in Ehime` -> `in Masaki, in Ehime` (0039 names the place, not a village).
  - REFERENCES: `ishiguro-azemame-tool` added to Sources (the Depiction's new sentence rests on it).
  - "The About tab's statement of absence passes" ("How many plants a bund carried, or how far one spread, is not recorded":
    the spacing is a density, not a count per bund).
  - GAPS 1, EDIT none: "the one found spacing is on a page the About tab cannot cite ... About cannot state it until the
    finding also stands on the question page" 0014 (the write handoff's open item: 0014's RESEARCH page is owed the Ishiguro
    finding, after a split).
- `modal-form` (re-owed by those EDITs): 0 FIX, 2 NOTE. NOTE M5/M7 proposed `...is not recorded.` -> `...is not recorded; in
  one village of terraced paddies the beans went into holes about 1 ft (30 cm) apart, two or three to a hole.` NOT APPLIED:
  it is exactly what the research round's GAPS 1 ruled About may not yet state (two checks, opposite rulings on one sentence;
  applying it would re-owe research, whose contract refuses it - the oscillation the round cap exists for). NOTE M11 ("that
  village" in the second bullet leans on the first), EDIT none, "the words are held by a research round".
- `modal-research` round 2: "ACCURACY 0 findings; REFERENCES 0; GAPS 0 ... Round 1's five EDITs are in the file word for word ... None of them made anything wrong." OUTSIDE THE CHANGE: round 1's GAPS finding "still stands as an open item ... This is also why the modal-form round's proposed EDIT was rightly not applied." No third round; no arbiter.

## PREDICTED vs ACTUAL

| | predicted | actual |
|---|---|---|
| 0284 pop-ups | 2 clear | 2 tool-cleared |
| 0284 claims | 0 owed; `BOW`, `Lines.new` "can cite the new item" | 0 owed; directed: both DRIFTED fix: claim (cite 0284), `Lines.u` IN-STEP |
| 0014 pop-ups | `hamlet/bund-beans` re-checks, IN-STEP "or a GAPS finding if the search FINDS a spacing"; 4 clear | 4 tool-cleared; bund-beans sent on and NOT in step: 2 depiction EDITs, 5 research EDITs, 1 GAPS with no EDIT |
| 0014 claims | 5 re-check, all in step ("then restated"); 8 clear | the owed round re-checked NONE (13 of 13 tool-cleared). Directed: of the predicted 5, 3 DRIFTED fix: claim, 2 IN-STEP (see the note); of the "other eight", 3 MISLABELED |
| 0008 pop-ups | `hamlet/field-pond` re-checks; 4 clear | all 5 tool-cleared, field-pond unread by any check |
| 0008 claims | 3 re-check in step; 19 clear | 22 of 22 tool-cleared. Directed: 2 DRIFTED fix: claim, `pocket_pond#the pond's form` IN-STEP; plus `polder_stage#a rice polder's pocket pond` DRIFTED fix: CODE (predicted to clear) |
| claims nobody predicted | - | `BEAD_STEP_FT` (MISLABELED), `BUND_SHARE` (DRIFTED), the two `#the pocket pond's ring` (DRIFTED): cite no page, owed by nothing |
| totals | 2 pop-ups + about 8 claims re-check, all in step; the rest clear | owed round: 0 claims, 1 pop-up. Directed: 15 of 23 claims not in step, one of them a code defect; the one pop-up read took 7 EDITs: 5 from the page change, 2 pre-existing fixes (Asuka, Masaki) |

Note on the 0014 row: of the predicted five (`bean_runs#a run's most and its spacing`, `#which bunds`, `#how many`,
`RUN_BEADS#a run`, `settle#a drowned bead alone`), 3 are DRIFTED fix: claim and 2 IN-STEP (`RUN_BEADS`, `bean_runs#which
bunds`). The prediction's "IN-STEP, then restated" meant the code agrees, and it does in all five; the agent's DRIFTED is the
restating the prediction expected. The prediction's real misses are the three `#no bead in the water` claims (a finding
label on what the page now calls a GUESS), the uncited four, and the polder pond's host.

## Judgment

(a) Over-cascade: none in the owed round - it read 0 claims and 1 pop-up. The spend was the directed check (81k tokens,
3 dispatches, 15 of 23 findings: the best yield of the four watched cascades) and the bund-beans chain: triage 10k,
depiction 54k, research 76k, form 23k, research round 2 61k - about 225k tokens on ONE pop-up, of which the two re-owed rounds
(form, research 2) are chain (iv): a research EDIT re-owes a whole-pop-up form read and a whole research re-read to confirm
five replacements `apply-edits` had already applied word for word. The form read's only product was an EDIT a sibling check
had just ruled out. The research round also reworded two sentences P3 never touched (Asuka, Masaki): right fixes
(unsupported words), but scope the page change did not ask for - the pop-up's turn in front of a check, not the cascade.

(b) Under-cascade: the largest of the four watched cascades. The owed round re-checked NOTHING on the claims side, and the
directed check found 15 claims behind the pages and one wrong outcome.
- Nine of the 15 are the "stale silent" pattern P1 and P2 found once each: the claim says "GUESS: page
  silent on X", the page now states X as its own labeled GUESS or CONVENTION, and the tool clears it because a claim that
  rests on no block cannot be re-owed by a new block. An ALL-ADDITIONS page session is therefore invisible to claims-owed by
  construction: 35 of 35 cleared.
- Four claims cite no page at all (`BEAD_STEP_FT`, `BUND_SHARE`, the two ring claims) and two cite another page (`BOW`,
  `Lines.new` -> 0005): known gap (i), nothing can re-owe them.
- Three `#no bead in the water` claims carry a FINDING label ("bunds-between-the-paddies-aze.drawing: in a single row on the
  bund - none inside a pond ...") for a rule the page now labels a GUESS of the project's own. They rest on §16, which did
  not move, so the tool cleared them correctly by its rule; only a read of the new §20 beside them shows the label is wrong.
  The prediction listed all three under "SHOULD clear".
- `polder_stage#a rice polder's pocket pond`: a code defect (a pond in a plot that is not low when the two new filters
  remove every low host), found only because the directed bundle put the claim in front of an agent. Unmeasured reach.
- P3's own new page item `pond-bank-and-margin-width` misstates the drawn wet band (about 1 ft showing, not 2.5 ft): the
  page session copied the claim's words, and its record checks (quote-check, record-format, source-reader) do not read code.
- POP-UPS, read by me against the pages:
  - `hamlet/bund-beans` BEFORE the checks: About "How many plants a bund carried, or how far one spread, is not recorded";
    Guesses "no record of a row's length or spacing was found"; Depiction "draws each bean plant as a round bead". The FOUND
    30 cm contradicted the Guesses bullet's "spacing" outright and made "each bean plant" untrue. The tool's triage did send
    it on (rule A) - the one place this cascade's owed machinery reached a real finding - but only to modal-depiction, the
    check whose remit excludes the Guesses tab where the contradiction sat; after its EDITs nothing was owed and the pop-up
    said both "about 1 ft apart" and "no record of ... spacing was found". Its Guesses tab stated NONE of 0014's new guesses
    (run of two to four; three bunds in eight; a drowned bead dropped) until the directed research round added two.
    AFTER: the two guesses are bullets, the spacing is on the Depiction tab with its source, the About absence stands (ruled
    sound). `drowned-bead-dropped` is on no tab (the agent: a drawing fallback, optional on Depiction).
  - `hamlet/field-pond` (tool-cleared, read by no check): Guesses = `{0008#often-field-keeps-pond}`, a size bullet,
    `{0008#much-pond-open-water}`. It states NONE of the three new guesses (four-sided host; never a resting plot; bank 2.2
    ft and wet ground 2.5 ft). Depiction: "an earthen bank round its edge, the wet ground just inside it ... and open water
    in the middle", "It may draw one on any kind of paddy field ... or a polder" - no width, and nothing the new items
    contradict; "on any kind of paddy field ... a polder" is silent on the polder's two host rules. Candidates, NOT added
    (no check's EDIT proposed them): `{0008#pond-bank-and-margin-width}` (after the item is restated, see above) on its
    Guesses tab; the two host rules are drawing fallbacks of the same kind the research agent ruled optional for beans.
  - `hamlet/bund`, `choice/plot_regularity--organic`: grep -i for "bow", "15%", "tenth" (run; one unrelated hit, "a tenth of an acre"): neither states how far a bund bows
    (as predicted); `comb-bund-bow` reaches no pop-up.
  - 0014's own drawing page still opens its bead block "Each bean plant is drawn as a round bead about 3 ft across" beside
    the new item's "a drawn row holds far fewer beads than the bund held plants" - the same "each bean plant" the depiction
    check ruled untrue in the pop-up. A page matter for the next 0014 session; not edited here.
- KNOWN GAP (ii), 451 T226, CONFIRMED a fourth time, with one difference: this time a check (the directed modal-research)
  did add two of the page's new guesses to a Guesses tab - because it was told to look. Left to the tooling, 0 of the 7 new
  GUESS items reached any pop-up; the 1 CONVENTION (`bean-spacing-8-ft`) did, by the owed route (triage, then depiction).
- The check handoff's open items stand (0284's absence note links 0014's research page, whose "hundred-foot" sentence bears
  on it; 0014's research page owes the Ishiguro finding).

(c) Rules that fired.
- 432 FR-005 a (cleared by the tool, no rested block moved): 35 of 35. Right by its rule on all 35; wrong in effect on 9 of
  the 16 of them the directed check read (5 "stale silent", 3 finding-labeled guesses, 1 code defect behind a cleared claim).
- Rule (iii) "rests changed": no occasion (no existing sentence changed).
- Modal-triage's tool pass: cleared 9 of 10; the agent's 1 TOUCHES was right and cheap (10k). Correct on the 9 as far as
  truth goes (none contradicts a page), and the reason `hamlet/field-pond`'s Guesses tab stays behind.
- 375 FR-003a decide-first and the `cascade@N` tripwire: did NOT fire on any of 8 dispatches, unlike P2 (the DECIDE_OK line
  was in each prompt; why the tripwire stayed quiet with 8 dispatches over 8 added blocks I did not establish).
- 451 T218: fired on 7 lines, all misdirected (above). It turns the cascade's commonest true finding - "the claim says
  silent, the page no longer is" - into an unrecorded hold, so the index keeps IN-STEP on seven claims an agent just found
  behind, and `make claims-report` will not list them. Candidate fix: hold only a line whose verdict asserts the PAGES are
  silent (NEEDS-RESEARCH, or `[§]` with no block named), never one that quotes a block.
- 451 T219: the NOTED, NOT FILED lines filed nothing; the OUTSIDE THE CHANGE page line was filed to found.jsonl (1 row).
- "rests on a page it does not cite - dropped": fired on `Lines.new`, `Lines.u` (0284) and oddly on `BUND_SHARE` for 0014,
  the page its claim text names without a path.
- 375 amendment 3 (a pop-up's checks in order): fired once on the round-2 research bundle, named its command.
- Chain (iv): fired (4 units re-owed by 5 applied EDITs); `apply-edits` settles only an ANSWERED round's units, so a
  directed (not owed) round's EDITs re-owe everything. See (a).
- `make ledger-owed`: listed the dispatches this time (P2's hole did not recur for impl-drift and the modal checks); the
  `modal-triage` agent pass is not listed.

## Rust claims to restate (for the one builder; none done here)

Code to FIX first (constitution XIV), then its claim:
0. `rust/phases/src/field/staged.rs::rice_pond` / `polder_stage#a rice polder's pocket pond` (DRIFTED, fix: code) - no pond
   when no remaining host is low (e.g. keep only `x.low` plots among the hosts, or pass the low hosts as `low_row`); the
   claim's "over the block's low row, a resting plot never its host" then holds as written. Measure first whether a pool
   map changes.

Restate the claim only (code agrees with the page in each):
1. `field/lattice.rs::BOW#the bund's bow` - cite `research/questions/0284-how-our-maps-draw-a-bunds-bends-and-corners.drawing.html`
   item `comb-bund-bow`: "up to about 15% of the spacing between its rows", a GUESS the page records.
2. `field/lattice.rs::Lines.new#the bund's bow` - same page: "no two rows of paddies carry the same shape", the bow up to
   `BOW` of a row (`comb-bund-bow`).
3. `field/beans.rs::BEAD_STEP_FT#the beads' spacing` (MISLABELED) - label CONVENTION, 0014 drawing `bean-spacing-8-ft`: "The 8
   ft is a drawing convention, chosen so that each bead reads apart" (the found spacing about 30 cm); drop "the record silent".
4. `field/beans.rs::BUND_SHARE#which bunds` - GUESS, 0014 drawing `beans-three-bunds-in-eight`: "About three bunds in eight
   carry beans"; drop "the record silent on how many".
5. `field/beans.rs::bean_runs#a run's most and its spacing` - four at most a GUESS (`bean-run-at-most-four`: "A run of beans is
   two to four beads long"); `BEAD_STEP_FT` apart a CONVENTION (`bean-spacing-8-ft`); drop "silent".
6. `field/beans.rs::bean_runs#how many` - GUESS, `beans-three-bunds-in-eight`, each bund its own roll; drop "silent ... saying
   only that some do".
7. `field/beans.rs::settle#a drowned bead alone` - GUESS, 0014 drawing `drowned-bead-dropped`: "A bead that would stand in a
   canal, a ditch or a pond is left out, and a run left with a single bead is left out with it"; drop "silent on a row that
   meets water".
8. `field/beans.rs::bean_runs#no bead in the water` (MISLABELED) - label GUESS, `drowned-bead-dropped` ("No bead is drawn in
   water"), held at the map's finish (`settle`); not the finding "in a single row on the bund".
9. `field/beans.rs::settle#no bead in the water` (MISLABELED) - label GUESS, `drowned-bead-dropped`, keeping the code's
   clearances (a pond grown by a bead's radius; a bead's radius past a line's half-width).
10. `driver.rs::settled#no bead in the water` (MISLABELED) - label GUESS, `drowned-bead-dropped`: none inside a pond, none on a
    line's water.
11. `field/staged.rs::rice_pond#a four-sided host` - GUESS, 0008 drawing `pond-host-four-sided`: "On a polder's rice, the pond
    takes only a four-sided plot"; drop "silent on the host plot's shape".
12. `field/staged.rs::rice_pond#never a resting plot` - GUESS, 0008 drawing `pond-never-resting-plot`: "A plot left to rest
    never holds the pond"; drop "silent".
13. `driver.rs::draw_field#the pocket pond's ring` and 14. `driver/polder.rs::draw_polder#the pocket pond's ring` - GUESS,
    0008 drawing `pond-bank-and-margin-width`; drop "no page sizes the margin". Word it as drawn (the wet fill reaches 2.5 ft
    past the water's edge and the 2.2 ft bank line is centered on the fill's outer edge, at `r + 2.5`), and restate the PAGE item to match in the
    same piece of work (found.jsonl row, 0008 drawing §25) - a page session's edit, not the builder's.
Optionally `RUN_BEADS#a run` (IN-STEP) can name `bean-run-at-most-four` for "the most, four, a GUESS".

## Files changed in the clone (uncommitted)

- dev/claims-index.json, dev/claims-pages.json (the tool's 35 clears; 16 directed verdicts)
- specs/449-rust-codebase/found.jsonl (+1 row, 0008 drawing §25)
- l7r/diagram/interactive/assets/modals/hamlet/bund-beans.md (7 EDITs of two checks)
- dev/review-ledger.md (rows by `make ledger-owed WRITE=`)

## End state

`make record CHECK=1`: "builds cleanly (4409 page(s))". `make quick`: clean (run twice, the second after the last edit and the
ledger rows). `make ledger-owed WRITE=`: 7 rows written, then `make ledger-owed` prints nothing, exit 0 (the `modal-triage` agent pass and the two
`claims-checked` exit-3 holds have no row). `L7R_LAND_ALONE=1 make claims-owed`: "no claim is owed". `L7R_LAND_ALONE=1 make
record-owed UNANSWERED=1`: "no record check is owed". "other builders' uncommitted code" lines: 0. Everything OWED is
answered; what is NOT done is listed above: the code fix (0), the 14 restatements, the 0008 page item's wording, the
0014 research page's Ishiguro finding, and the Guesses-tab candidates on `hamlet/field-pond`.

Note: /tmp/p3c/modal-research.reply.md, modal-research2.reply.md and modal-form.reply.md are my condensed copies of the
agents' replies with session notes (the EDIT blocks verbatim); the impl-drift, depiction and triage reply files are verbatim.
