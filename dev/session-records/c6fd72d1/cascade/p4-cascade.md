# Cascade of page session P4 (449 T425: 0006, 0011, 0013, 0027 drawing pages)

Coordinator session, clone `/diagram/.clones/diagram-backlog`, HEAD 9207459906 (P4's page commit). Run 2026-11-24.

## Stage 1: claims

### claims-triage

`make claims-triage`: **88 claims cleared without a triage** ("a page each cites moved and no block it rests on did",
feature 432 FR-005 a); **no claim owed a triage**, so no triage bundle, no `claims-triage` agent and no `claims-triaged`.
By the page they cite: 0006 41, 0027 19, 0011 17, 0013 11 (88; the four pages' every claim except the three below).

`make claims-owed` after it: **3 owed, "rests changed"** - each rests on 0011's block `348cf5c8d3c7cc78` ("The clearing
starts from the plots nearest the toe", the GUESS block P4 folded the last band's start into):
- `rust/phases/src/field/build.rs::build#the climb's order`
- `rust/phases/src/field/dry.rs::hem#a column's climb ends` (not in the prediction's re-check list: it rests on the same
  block as well as `05e2fe635af4884d`)
- `rust/phases/src/field/dry.rs::hem#the last band from the canal's start`

### impl-drift on the owed 3 (bundle `cb-owed`, OWED=1 plus PAGES=0006 drawing; 37 s, 73k in / 3.3k out)

Dispatch refused once by the decide-first guard (449 T425 carries no CLEAR verdict), re-sent with
`DECIDE_OK="claims cascade checks after a page session; no plan decision is checked"` (all three bundles alike).

- `build#the climb's order` **IN-STEP** - "the clearing starts nearest the toe, each band runs the whole canal, and the
  last band runs from the canal's start until the need is met, which leaves the hem deepest at the foot [§28, §29]"
- `hem#a column's climb ends` **IN-STEP** - "where the pinch falls is labeled a GUESS, and neither page records it"
- `hem#the last band from the canal's start` **DRIFTED** - "the claim says the 0011 drawing page is silent on where along
  the canal the last plots stand, but §29 now records it as a GUESS: 'The last band ... is laid from the canal's start
  along it until the need is met'; the code does exactly that (`d` from 0, `break 'band` once `got >= need`); fix: claim
  (cite 0011 drawing §29 ... and drop 'silent'); effect: none"

`make claims-checked`: exit 3. Two recorded; **the DRIFTED line HELD by 451 T218** ("it says the pages are silent, and the
record's nearest pages for its words are not in the bundle (0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html)")
- the known misfire: the FINDING is that the claim says silent and the page no longer is. Not re-dispatched (brief).
**It stays owed** (`make claims-owed`: 1, `rests changed`).

## Directed check (24 claims, 2 bundles, REASON= stated)

### Dry fields (`cb-dry`, PAGES=0006,0011 drawing; 58 s, 182k in / 5.5k out): 13 - IN-STEP 9, DRIFTED 4

- `field/dry.rs::refused#off the water` **DRIFTED** - "calls 0006's drawing page 'silent on how near the water a dry
  plot may come', but that page now states it in §29 (`dry-plot-off-water`) ... The code ... matches. fix: claim ...
  effect: none". HELD by T218 (nearest pages named: 0190 notice boards drawing) - not recorded.
- `hem.rs::CLEAR_FT#off the water` **DRIFTED** - "calls 0006's drawing page 'silent', but §29 (`dry-plot-off-water`)
  now records the figure as 'within about a foot of any water', a GUESS. The 1 ft matches it. fix: claim; effect: none" - recorded.
- `driver/check.rs::check#no dry plot on the water` **DRIFTED** - "rests on §27 ... which speaks only of the plot's own
  canal. The check also tests the brook and the drain's run, and those are covered by §29 (`dry-plot-off-water`) ...
  fix: claim (cite `dry-plot-off-water` beside §27); effect: none" - recorded.
- `field/build.rs::hem_bounds#the toe's band whatever the grain asks` **DRIFTED** - "The fact it implements, one full
  band on the toe 'however much of the hamlet's grain the barley already supplies', is now its own block, §6
  (`barley-hamlet-toe-band`), which records that band as 'a GUESS, a drawing fallback of ours'. The code ((_, true) =>
  INFINITY, 1) matches. fix: claim; effect: none" - recorded.
- IN-STEP: `Canal.frame#square to the canal` ("the project's choice over the paddy's slope"), `hem#square to the canal`
  ("The comment §24 lost changes no verdict"), `hem_bounds#the hem's climb`, `hem_bounds#a barley hamlet's shortfall`,
  `build#the hem's line`, `hem_in#the hem's line`, `TOE_SHARE#the toe`, `PINCH_SHARE#the pinch`, `pinched#the pinch`
  (both still rightly "silent on taper": the taper item was not written).

### Resting plots and the dike (`cb-dike`, PAGES=0013,0027,0018 drawing, WITH=draw_polder; 67 s, 81k in / 6.7k out): 11 - IN-STEP 8, DRIFTED 3

- `field/states.rs::states#a resting plot from the green` **DRIFTED** - "says 0013's drawing page is silent on whether a
  wet plot rests, but the page now says it ... (item `resting-plot-one-state`). The code does what the page says
  (`out[i] == State::Green`); fix: claim (cite that item, keep GUESS, drop 'silent'); effect: none". HELD by T218.
- `field/dike.rs::CROWN_FT#the crowns` **DRIFTED** - "the page now gives 'Each willow's crown is drawn 7 to 11 ft across',
  a GUESS (`willow-crown-size`), and sends the mulberry's crown to 0018, '4.4 to 7 ft across'. `draw_polder` draws each
  crown as `ellipse((x, y), r, r)`, so CROWN_FT holds radii and the claim's '3.5-5.5 ft' and '2.2-3.6 ft' are half of the
  page's widths across ... The mulberry reaches 7.2 ft across against the page's 7 ...; fix: claim (cite 0027 §34 and
  0018 §71, give the figures as radii, 7-11 ft and 4.4-7.2 ft across); effect: none". HELD by T218.
- `field/dike.rs::GAP_HALF_FT#the gap` **DRIFTED** - "the page now says 'The rows stop about 15 ft to each side of the
  channel's middle line', a GUESS (`rows-gap-at-channel`). Its 'broadest crown (5.5 ft)' is a radius (11 ft across), so
  a crown's edge comes to 9.5 ft from the middle line, half a foot inside the 10 ft half-width of a 20 ft frame, not clear
  of it as the claim says; fix: claim (cite §37 ..., call 5.5 ft a radius, drop 'off the sluice's frame' or say it comes
  within half a foot of it); effect: none". HELD by T218.
- IN-STEP: `states#one state a plot`, `REST_PLOTS`, `Crown#a crown`, `dike#the crowns rolled`, `dike#the rows cut at the
  gaps`, `draw_polder#the band cut where a channel crosses`, `ROWS#the rows`, `landuse.rs::MULBERRY_FT` (radius 2.2-3.5,
  4.4-7 ft across). NOTED: the dike's mulberry tops out at 7.2 ft across, the pond banks' at 7.

T218 held **5 of the 8 DRIFTED lines** (the owed `hem#the last band`, and the directed `refused#off the water`,
`states#a resting plot from the green`, `CROWN_FT`, `GAP_HALF_FT`), each the "said silent, the page no longer is" misfire;
it held 5 of the 6 "silent" lines (`CLEAR_FT` said "silent" and was NOT held). The index still reads IN-STEP for all five
(checked): only this file carries those findings. The directed holds were not owed and stay not owed; the owed one stays
owed. The other **3 DRIFTED are recorded** in the index as open findings, and `make claims-report` lists all three
(`CLEAR_FT#off the water`, `check#no dry plot on the water`, `hem_bounds#the toe's band whatever the grain asks`) - the
directed check turned three IN-STEP rows into open findings (report-only switch: no landing refused).

Square-to-canal pair: 0006's block "A dry plot beside a canal stands square to it." labels its frame "a reconstruction"
("The page gives the line of the villages, not of the strips, so the frame is a reconstruction"); `Canal.frame` says
"the project's choice". Neither claim cites the GM, so neither is owed a restatement under the brief; "reconstruction" is
the page's own word if anyone touches the claim.

GAP_HALF_FT measured on paper (read only): `driver/polder.rs::sluice_frame` draws the posts centered at `span/2 - post_a/2`
across the channel (`SLUICE_SPAN_FT` 20, posts 2 ft across, 4 ft along), so a post's outer face is 10 ft from the middle
line and the broadest crown's edge (radius 5.5 at 15 ft) can reach 9.5 ft: a crown standing beside the frame can overlap a
post by up to 0.5 ft. UNMEASURED defect candidate, tiny (no map checked for a tree within 2 ft along the channel of a
post); 0027's "left as room for the sluice and its banks" holds only to that half foot.

## Stage 2: pop-ups

`make modal-triage`: **26 units cleared by the tool ("no claim-bearing change"); no agent owed**: hamlet/ barley,
buckwheat, millet, soy, farm-holding, fallow, perimeter-dike, sluice-gate, fruit-dike, mulberry-dike; choice/
dikepond_split--0.3..0.7, fan_middle--cleared/--wild, field_archetype--polder_grid/--mulberry_dike_fishpond, grain_drift,
paddy_rest--settled/--unsettled, town_nearness--far/--near, winter_crop--barley/--none (all modal-depiction units). No
triage agent, no checks sent on, no EDITs, so no `modal-triaged`, `record-checked` or `apply-edits` was owed.
`make record-owed UNANSWERED=1`: nothing owed.

My read of the pop-ups against P4's items (report only, nothing added):
- barley, buckwheat, millet: Depiction "small rectangular plots ... each squared to the canal behind a bare bank ... the
  plots keep to its toe"; neither `dry-plot-off-water` nor `barley-hamlet-toe-band` on Guesses or Depiction. Absent, not
  contradicted. `[winter_crop=barley]` says nothing of the one full band.
- choice/fan_middle--wild: "its dry fields keep to the toe" - in step with the toe band, its fullness unstated.
- fallow: Depiction "a whole plot of grass ... never two resting plots side by side"; `resting-plot-one-state` absent.
- perimeter-dike: "The band and its rows are cut where a channel crosses it, at a gate" and "crowns read as touching
  trees"; no crown size, no gap width; `willow-crown-size` and `rows-gap-at-channel` absent. Willows 8.5 ft apart under
  7-11 ft crowns do touch: in step.
- mulberry-dike: Guesses "Each bush's crown, 4.4 to 7 ft across" - agrees with 0018 and 0027's new link.
- choice/field_archetype--polder_grid: "the willows spaced wider ... so their crowns read as touching trees" - no size, no
  gap: absent, in step. choice/dike_crop--mulberry ("their crowns touching") and choice/pond_bank--planted ("round green
  crowns spaced along the bank"): no size stated. No contradiction anywhere.
- There is no willow pop-up.

## Stage 3-4

`make record CHECK=1`: builds cleanly (4410 pages). `make quick`: clean. `make ledger-owed`: 3 impl-drift passes, written
with WRITE= below.

## The 0011 wording question

The code: `field/build.rs::hem_in` builds the hem's line as `f.fan.at(f.fan.length * (1.0 - rise * k/steps), far)` for
k = 0..24, and `Fan::at(u, s)` takes `u` "feet down the fall from the fork", so k = 0 is the fan's FOOT: the line runs
from the toe up the far flank to the head (on a cleared middle it goes on across the head). `dry.rs::Canal` keeps that
order (`starts`, distance 0 at the first point) and the last band lays "from its start, along it" (`d` from 0). So in the
code "the canal's start" IS the toe end, and the page agrees with itself and the code - but only in the hem line's own
frame. Canal A's water runs from its intake at the head DOWN to the foot, so a reader will take "the canal's start" as
the head, the opposite end. Suggested wording for 0011 (and the claim `hem#the last band from the canal's start`): "is
laid from the toe end of the canal, up along it, until the need is met". Not edited (a page edit re-owes its record
checks).

## PREDICTED vs ACTUAL

| | predicted | actual |
|---|---|---|
| claims re-checked by the owed machinery | about 12 | 3 (all three on 0011's folded block) |
| claims cleared | about 63 | 88 by FR-005 a, none triaged (the prediction counted 79 claims on the four pages; the index now holds 91 - 0011 20 where it counted 13, 0027 19 where it counted 14) |
| pop-ups re-checked | 9 named (barley, buckwheat, millet, fan_middle--wild, winter_crop--barley, perimeter-dike, polder_grid, fallow, winter_crop--none) | 0 - all 26 cleared by the tool |
| findings | all in step expected | 8 DRIFTED claims (all claim restatements, effect none), 0 pop-up findings |
| square-to-canal pair cite the GM? | maybe | no - both IN-STEP, "the project's choice"; nothing to restate |

## Judgment

(a) **Over-cascade: none.** The owed round sent 3 claims to one agent and no pop-up anywhere. Spend: 3 impl-drift
dispatches, about 336k in (232k cached) / 15.5k out, 162 s - two of the three are my directed bundles.

(b) **Under-cascade: as in every all-additions session, the owed machinery could not see it.**
- Of 8 DRIFTED claims, 7 came only from the directed check. Five are the "stale silent" pattern again
  (`refused#off the water`, `CLEAR_FT`, `states#a resting plot from the green`, `CROWN_FT`, `GAP_HALF_FT`); the prediction
  listed CLEAR_FT, refused, CROWN_FT and GAP_HALF_FT as "SHOULD re-check", and the tool cleared every one by FR-005 a
  because a new block is a block no claim rests on. `check#no dry plot on the water` and `hem_bounds#the toe's band`
  rest on standing blocks and now under-cite the new item.
- Two claims were wrong in substance, beyond citation: `CROWN_FT` calls radii widths ("each about its row's spacing
  across"), and `GAP_HALF_FT` says the 15 ft gap keeps the broadest crown "off the sluice's frame" when a 5.5 ft radius
  reaches 9.5 ft from the middle, half a foot inside a 20 ft frame. The first is a restatement. The second is a restatement
  unless a map shows a crown over a sluice post: on paper a 5.5 ft radius at 15 ft reaches 0.5 ft over a post's outer face
  at 10 ft - an unmeasured defect candidate (see the GAP_HALF_FT note above), not fixed (rust/ not edited).
- Pop-ups: all 26 cleared by the tool and none contradicted by my read; the six new guesses reach no pop-up (451 T226),
  as predicted. Reader value of adding them: low (drawing fallbacks), except perhaps `barley-hamlet-toe-band` on
  barley's `[winter_crop=barley]` line.
- The 0011 wording: a real reading ambiguity, invisible to the record checks and the claims (both read "start" in the
  code's own frame).

(c) **Rules that fired.**
- FR-005 a (page moved, no rested block moved): 88 cleared.
- Rests changed: 3 owed (0011's folded GUESS block).
- Modal triage's claim-bearing filter: 26 cleared, none to the agent.
- 451 T218: held 5 lines (5 of 6 "silent" lines), every one the known misfire ("the claim says silent, the page no
  longer is"); one of them, the owed `hem#the last band`, therefore stays owed.
- `claims-checked` also dropped rests the agent named on pages the claims do not cite (5 lines, "was the reply judged
  against another bundle's numbering?") - harmless here: the directed bundles carried extra pages on purpose.
- Decide-first guard: refused all three dispatches once; `DECIDE_OK` with a reason.

## Rust claims to restate (not done; rust/ not edited)

1. `rust/phases/src/field/dry.rs::hem#the last band from the canal's start` (OWED, held) - now: "GUESS
   where-a-farming-hamlet-grew-its-coarse-grain.drawing: the last band laid from the hem line's start, the toe end, along
   it until the need is met, the page's own GUESS" (cite 0011's "The clearing starts from the plots nearest the toe" block).
2. `field/dry.rs::refused#off the water` (held) - cite 0006 drawing `dry-plot-off-water` as the page's GUESS, drop "silent".
3. `hem.rs::CLEAR_FT#off the water` - "GUESS dry-fields-and-their-crops-hatake.drawing (`dry-plot-off-water`): about a
   foot past a filed water's half-width".
4. `driver/check.rs::check#no dry plot on the water` - cite `dry-plot-off-water` beside the dry-side block for the brook
   and the drain's run.
5. `field/build.rs::hem_bounds#the toe's band whatever the grain asks` - cite `barley-hamlet-toe-band`, the one band the
   page's GUESS.
6. `field/states.rs::states#a resting plot from the green` (held) - cite 0013 drawing `resting-plot-one-state`, GUESS,
   drop "silent".
7. `field/dike.rs::CROWN_FT#the crowns` (held) - cite 0027 drawing `willow-crown-size` and 0018 drawing's mulberry
   crown; state the figures as RADII (willow 3.5-5.5 ft, 7-11 ft across; mulberry 2.2-3.6 ft, 4.4-7.2 ft across; the
   page's mulberry 7 ft top a 0.2 ft difference).
8. `field/dike.rs::GAP_HALF_FT#the gap` (held) - cite 0027 drawing `rows-gap-at-channel` (GUESS); call 5.5 ft a radius;
   drop "off the sluice's frame" or say a crown comes within half a foot of it.

## Owed at the end

- `L7R_LAND_ALONE=1 make claims-owed`: **1 owed** - `rust/phases/src/field/dry.rs::hem#the last band from the canal's
  start` (rests changed), its DRIFTED verdict held by 451 T218's misfire. NOT everything owed is answered: it clears only
  by restating the claim (item 1 above), or by the T218 re-bundle the guard names (adding 0246's drawing page) - not
  run, per the brief. No "other builders' uncommitted code" line.
- `L7R_LAND_ALONE=1 make record-owed UNANSWERED=1`: nothing owed; no "other builders' uncommitted code" line.
- Files changed (uncommitted): `dev/claims-index.json`, `dev/claims-pages.json`, `dev/review-ledger.md` (3 rows).
