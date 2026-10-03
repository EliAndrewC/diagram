# Research: reached across a yard (feature 317)

Every figure here was observed 2026-10-02/03, on the reference spec (Inashiro's: nucleated, the pond sink, a shrine), under the
load of the other sessions on this host. Wall-clock legs are alternated per seed (`abab.sh`, one process a seed); single seeds
vary by up to 2x either way under this load, so only totals over alternated legs are compared, and the CPU-second legs
(`CLOCK=cpu`) are reported beside them.

## R1 - Was every house in a clustered village reached by a lane? (the record, brief `briefs/r1-write.md`; checks `briefs/r1-check.md`)

The research pass found no page stating it as a rule. Wigmore 1892 (Part V Section 8) records a customary right of passage over
a neighbor's land for land with no road access of its own, in seven provinces (three of them towns), once as a chain (Echigo:
C over both B's plot and A's); Morse 1886 records Enoshima's rear houses reached by alleys. The entry
(`research/questions/0081-village-lanes.html`) now answers "Not always". Its record checks ran in a headless page session; see
R6 for the runner defect that session met.

## R2 - The corridor judged as drawn (plan D6; feature 314 R12's defect)

**Mechanism.** The web's settle carries a free lane end that stops short of a way onto it (`settle.settle_joins`, reading
`law.near_misses`). On seed 13 at 20 households, with the route kept off its own parts, a corridor's start 15 ft from another's
end was carried onto it and closed a needle with a third: lawful as the seating judged it (`tree.admits`), refused as the web
drew it (`WebRefused`). **Fix:** `admits` asks `law.needle_loops` again of the tree with its ends joined as the settle will join
them (`tree.as_joined`). Verified on the reproduction (`/tmp/repro317`: seed 13 at 20 households with own-parts on rolls).
(observed 2026-10-02, method: the reproduction, the transcript's R12 bisection.)

**Its cost, and the prefilter.** Profiled on seed 2 at 40 households, the re-asked check was `as_joined` 1.26 s of 15.9 s
profiled, all of it `law.near_misses`: 465,270 `seg_closest` calls from every free end to every segment of every way
(`prof-fix-40-2.txt`). `near_misses` and `free_end` now pass over a way whose bounding box lies beyond the reach
(`law.box_gap`, an exact lower bound: same answers). Re-profiled, the tree's whole judge was 1.17 s (`prof-fix2-40-2.txt`,
host load 5 against 12). Timed against main (origin/main 2ba3c353c, `/tmp/main317`), the homesteads stage summed:
(observed 2026-10-03, method: as the heading.)

| leg | 15 households, seeds 1-8 | 40 households, seeds 2, 6, 10, 13 |
|---|---|---|
| the fix, before the prefilter, wall (`fix317-*`) | 9.9 -> 9.3 s | 19.5 -> 20.7 s |
| the fix with the prefilter, wall (`fix317b-*`) | 24.9 -> 26.6 s | 13.3 -> 12.4 s |
| the fix with the prefilter, CPU seconds (`fix317c-*`) | 21.6 -> 20.1 s | 15.6 -> 16.1 s |
(observed 2026-10-03, method: as the heading.)

Every leg seated every household. The per-seed spread (seed 4 at 15 households: 3.81 -> 1.91 s wall, 1.25 -> 2.30 s CPU)
is larger than any difference between the totals: the fix costs nothing this host can measure.
(observed 2026-10-02/03, method: `prof.py`, `abab.sh`, as named.)

## R3 - What "a lane to every house" costs the seating (method: `corridor_only.py`, `r3-only-15.log`, `r3-only-40.log`)

Every garden layout the parts are asked of (`_parts_fit`) was followed: where `access_corridor` found no corridor, the rest of
the parts' rules were asked as though one had been found, and the layout counted CORRIDOR-ONLY if they all passed (then
refused as shipped, so the roll is the engine's). A seat none of whose layouts passed but one of which was corridor-only is a
seat lost to the corridor alone.

| | 15 households, seeds 1-8 | 40 households, seeds 2, 6, 10, 13 |
|---|---|---|
| seats popped / seated | 631 / 120 | 1,152 / 160 |
| seats lost to the corridor alone | 77 (12%) | 90 (8%) |
| layouts asked / corridor-only | 1,273 / 313 | 2,193 / 340 |
| ...every path found crossed the household's OWN beds or fixtures | 191 (61%) | 260 (76%) |
| ...no path at all (straight, round the gable, routed) | 109 (35%) | 67 (20%) |
| ...the lane law (`tree_admits`) refused every path | 13 (4%) | 13 (4%) |
(observed 2026-10-03, method: as the heading.)

From a corridor-only layout's first door, the nearest seated neighbor's threshing yard (box edge), in feet:

| | min | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|---|
| 15 households (n=296) | 64 | 126 | 141 | 158 | 176 | 203 | 231 |
| 40 households (n=336) | 74 | 107 | 126 | 144 | 164 | 175 | 205 |

and the access tree's nearest leg: median 166 ft (15 households), 156 ft (40), within the route's reach (`ROUTE_REACH_PX`, 320
px at the reference's 1 ft a pixel).
(observed 2026-10-03, method: as the heading.)

**What it means for the passage (plan D2-D4).** The custom the record attests is passage over a NEIGHBOR's land for land that
"cannot reach the highway without passing over" it - land enclosed by another's. No layout refused a corridor stands so: the
nearest neighbor's yard is 64 ft away at the least and 107-158 ft at the tenth percentile and median, across ground the route
searched. A first passage built on plan D2 (a straight leg to a neighbor's yard within 40 ft, `passage-wip`) seated no household
on four seeds (observed 2026-10-02). The lane requirement's cost is real - 12% of the seats at 15 households - but 61-76% of it
is the route finding paths through the household's own beds: it kept off the house alone, so the taut pull refused what it found
(R4).
(observed 2026-10-03, method: as the heading; the classification asks each layout's candidates `fixtures_clear` /
`parts_clear` and `lawful_leg` separately.)

## R4 - The route searched per layout, round its own parts (task T06; method: `t06.sh` - the base a worktree at b54a76717, the fixed judge without it; `t06-*`)

Each garden layout searches its own route after the seat's shared straight and round-the-gable candidates, kept off the
household's house, shed, byre, well, beds and fixtures by the gaps their leg tests keep (`route.own_parts`; the memo keyed per
layout). Feature 314 had tried the search off its own parts and withdrawn it (its R12) for two reasons this feature removes: the
judge's defect (R2), and a route searched once for the seat's house and yard, so every layout took the route laid round the
first layout's beds.

| | 15 households, seeds 1-8 | 40 households, seeds 2, 6, 10, 13 |
|---|---|---|
| seats popped, base -> new | 631 -> 426 | 1,152 -> 682 |
| seats lost to the path alone | 77 -> 21 | 90 -> 22 |
| corridor-only layouts: own parts / no path / lane law | 191 / 109 / 13 -> 39 / 32 / 25 | 260 / 67 / 13 -> 55 / 32 / 14 |
| route searches | 277 -> 387 | 361 -> 499 |
| homesteads stage, CPU seconds, alternated | 27.1 -> 25.6 s | 34.5 -> 30.9 s |
| households seated | 120 -> 120 | 160 -> 160 |
(observed 2026-10-03, method: as the heading.)

The layouts still refused stand at least 83-85 ft from the nearest neighbor's yard (median 143-145 ft).
(observed 2026-10-03, method: as the heading.)

At 20 households (feature 314 R12's leg), one wall-clock run a seed, eight seeds (4, 13, 39, 2, 6, 8, 25, 47): every seed rolled
on both engines, seed 13 included - the seed feature 314 refused with the search off its own parts. The access corridors' legs
rose (seed 13: 35 -> 48; summed 251 -> 346: paths bend round the beds); the homesteads stage summed 9.18 -> 10.31 s and the web
6.08 -> 6.89 s, single runs under load (seed 8's web 0.59 -> 1.31 s, seed 4's 0.90 -> 0.57 s). Seeds 4 and 39, feature 314's
slow webs, drew theirs in 0.57 and 0.76 s. The 20-household leg is the bookend's to settle (T09).
(observed 2026-10-03, method: as the heading.)

## R5 - The known bugs, their owners and states (FR-007, SC-006)

| bug | owner | state |
|---|---|---|
| The seating admitted a corridor the web then reshaped into a needle (feature 314 R12) | this feature | fixed: `tree.as_joined` (R2); the reproduction rolls, and seed 13 at 20 households rolls with the route off its own parts (R4) |
| Cohort seeds 22, 23 (linear, `WebRefused`) | Diagram (Inashiro), feature 315 | fixed in 315 (commit 82ce6927b, a corner welded onto a tread in `settle_needles`), landed on main and merged here: the cohort passes 30 of 30 on main and on this clone (`make cohort N=24 JOBS=2`, the pinned seeds included; 2026-10-03) |
| Cohort seeds 14, 15, 906 (dispersed: `trees_shading_plots`, `gardens_east_shaded`) | Diagram (Inashiro), feature 315 | fixed in 315, landed and merged here: 30 of 30 on main and on this clone (2026-10-03) |
| A headless page session resumed after a stall dispatched its returned checks again: their reports sat queued in its transcript, never taken up, and Claude Code told the resumed session they "didn't finish" | this feature (found running R1's checks) | fixed: the resume names a file of the queued reports and resumes early once they are back (`_page_session_runner.undelivered`, `returned_file`, `turn_ended`; fa30940d5, tests in `tests/tooling/test_page_session.py`) |
| A `resume:` page session that stalled would fail to be resumed (`--session-id` no longer in its command) | this feature | fixed in the same commit, tested |
| The seating reserved wood seats in the afternoon sun lane west of every yard and bed (feature 310's), which the copse never plants - main's Inashiro 18, Kuwabata 16, Sawada 34 unplanted - and routed paths round them (the 27 ft lane bulge, the village lane glyph check round 3 F5) | this feature, T10 | fixed: the reservation keeps the lane (R10); `tests/gate/test_wood_shares_planted.py` red before, Inashiro 320 of 320 planted after |
| `pair-hooks.sh stop` read a green `make test-file` as a green gate and told sessions (a headless page session sharing the clone among them) to dispatch reviews no gate had earned | this feature | fixed: the stop branch asks the gate stamp as the pretool branch does (b54a76717); the new case fails with the old line (102 passed, 2 failed) and passes with the fix (104) |
| Cohort seed 18 (nucleated, 15 households) refused (`OverlapRefused`: lanes over farm_fixtures) - found by T07's cohort, made by the per-layout route: squaring a water crossing straightened a routed path's bend across the household's own privy | this feature | fixed: the seating judge asks the household's own house, beds and fixtures of the path as the web lays it (`tree.laid_run`, `own_clear`; 6a38205a0); `make cohort N=1 SEED=18` rolls |
| Seed 47 at 20 households refused (`WebRefused`: an access lane's bends) - found by T07's 20-household leg: `straighten_joints` joined two access lanes meeting end to end at a door and pulled the pair into a kink, a tree lane no settle may cut | this feature | fixed: a joint's pull is refused where it makes a kink the two did not have (bebed7632); the seed rolls, and the new test fails without the fix |
| The persimmon reseat (feature 315) gave up a tree where its first seat shaded a neighbor, on the rolled side only - Inashiro 11 of 12 rolled (B10) | this feature | fixed: the neighbor's sun asked of every seat tried, both sides (6adad5792; R8) |
| A grove farm's kura and byre could stand on a reserved corridor (`fit._on_the_access` left them out) - found by the impl-drift check | this feature | fixed (d7c5fb007; R9), tested |
| The claims bundler could not name a claim whose label holds a comma (`UNITS=`) | this feature | fixed: `split_keys` (4c0fb2678), tested |
| A household reached across a yard kept its passage where a later corridor gave it a way of its own (the farmhouse glyph check) | this feature | fixed: `recheck_passages` and `relay`, by the whole holding (e26349c0a, fd3726457; R9) |
| THE LANE CODE AGAINST ITS DRAWING PAGE, pre-existing figures the impl-drift check found (R9): ends joined at 11.5 ft (`joints.meet_end_to_end`) and 30 ft to a way's side (`settle.settle_joins`, `law.JOIN_REACH_FT`, `sweeps._bridge_collinear_breaks`) where the page says 25; 4-6 ft off a fence or the fabric (`bund.RunOnBlocks.clear`, `clearance._clear_touch`, `clear_runs`, `may_write`) and 5.5 ft for the field way (`corridors.FIELD_ROUTE_GAP_FT`) where the page says 7; a household's own beds held 2 ft off its path (`tree.own_clear`, `access.parts_clear`); a free end's last leg cut to 20 ft (`sweeps.trim_free_stub`); the exit strip 3 ft where the spine is 5 (`tree.lanes_of`); "own" ground within 80 ft of an end (`settle.theirs`); the farmhouse sizes against 0029 (`houses._try_place_bundle`); the farmstead's beds and kura held off the paddy at nine points (`fit._parts_fit`); the wood's 22 ft default sun strip (`WoodShares.__init__`); and three questions the check could not answer from its bundle (`corridors.field_router`'s defense marsh, `sweeps._drop_end_nubs`, `lanes.reaches_dooryard`) | a follow-up feature, put to the GM in this feature's report | open: each is a call between the maps and the page, and recording any of them edits the 0081 drawing page, which re-owes the ~300 claims that cite it; the push carries them by `CLAIMS_OK` naming this row (observed 2026-10-03, method: the impl-drift check's reading of the code against the page, R9) |
| A lane passing another's end vertex and joining it just beyond, a sliver between the treads (the village-lane glyph check, F2; main's joint code on the layout the passage moves) | a follow-up, put to the GM | open: the reviewer's lever - end the arriving lane on the other's end vertex |

## R6 - The passage built: tight seats, the adjoining land, the walk (tasks T03, T04; method: `passage_probe.py` and `tight_cost.py` in the session's scratchpad, `passage_smoke.py`, `abab.sh` against a worktree at 94263ffe1 - per-layout routing, no passage - `t03-*`, `t03b-*`)

The MODE 1 check (2026-10-03) ruled not building the passage NOT LEGITIMATE: the growth parts every two footprints by a path's whole
strip, so R3's distances were measured on a spacing built for a lane to every house. Plan D2 as amended: tight seats within the
rolled share, the custom's condition (land against land) as the reach, the walk on the two households' land.

Built step by step on the reference at 15 households (seeds 1, 2, 6, 8, then 1-16), each step measured:

| step | tight-seat layouts with no corridor | refused, and why | passages |
|---|---|---|---|
| adjoining asked of the layout's own box | 21 | all 21 not adjoining: 6.6-36 px from the neighbor's land against a 3 px tolerance | 0 |
| ...of the reach rolled at the final seat | 16 | 14 not adjoining (3-16.6 px: the seat is parted by the union of the reaches rolled while it settled) | 1 |
| ...of the reach the seat was parted by (`settled_seat`'s allotted reach) | 16 | every one 2.0 px apart; the straight walk off their land 4, blocked 9 | 3 (2 seated) |
| seeds 1-16, the straight walk | 109 | blocked 95 - by the household's own house, beds or fixtures, or the neighbor's - off their land 9 | 3 (2 seated) |
| seeds 1-16, the walk ROUTED on the two lands (`walk_of`) | - | - | 16 households on 9 of the 13 settlements whose share allowed one (seeds 2, 4, 6, 8, 10, 11, 13, 15, 16: 1, 1, 1, 2, 3, 2, 3, 1, 2) - the run before the walk was asked first and before the tight seats were kept to houses a passage may cross to; R7 has the shipped engine's |
(observed 2026-10-03, method: as the heading.)

With the routed walk, seeds 1-16 at 15 households: every household seated and reached, no settlement past its share (budgets 0-3;
seeds 1, 7, 12 and 14 drew none with budgets 3, 1, 2, 3). (observed 2026-10-03, method: `passage_smoke.py 15 1,...,16`.)

THE COST. Against the base before it (per-layout routing, no passage), alternated, CPU seconds, 15 households, seeds 1, 2, 4, 6, 7,
8, 10, 13: the walk asked after the corridor, 12.8 -> 16.3 s (+27%); the walk asked FIRST (the same verdicts), 19.5 -> 21.8 s
(+12%; the host's load moved even CPU time between the two runs). Where it goes (`tight_cost.py`, one run, 8.1 s stage): the tight
seats' settles 0.37 s (607 popped), their placer calls 1.12 s (298), of which the walks 0.34 s (179 asked, 90 found) and the
corridor searches after a walk 0.54 s (90 asked, 75 found - a household that could reach the lanes itself, refused the seat by the
custom's condition). By bearing from the neighbor's house against its yard's: tried 39 / 74 / 64 / 86 / 35 at 0 / 45 / 90 / 135 /
180 degrees, seated 5 / 1 / 4 / 1 / 0.
(observed 2026-10-03, method: as the heading.)

## R7 - What the tight seats cost, and the forms tried (method: `tight_order.py`, `tight_cost.py` in the session's scratchpad; `passage_smoke.py`; `abab.sh` CPU seconds against the worktree at 94263ffe1 - per-layout routing, no passage - `t03c-*`, `t03d-*`, `t03e-*`)

Every figure at 15 households on the reference spec, observed 2026-10-03 at host loads of 10-15 (other sessions' gates and a page
session running beside), so CPU seconds moved by a fifth between runs; the per-part breakdowns (`tight_cost.py`, one process) are
the steadier measure.

| form | passage households (seeds 1-16) | settlements with one, of 13 whose share allows | homesteads stage against no passage |
|---|---|---|---|
| tight seats queued from every reached house, every bearing (8c8b42773) | 16 | 9 | +12% to +35% (two runs); the tight seats 1.49 of 8.1 s and 4.0 of 21.7 s |
| a tight seat offered only behind an ordinary seat whose household found no corridor (set aside) | 3 | 3 | 22.7 -> 20.2 s: nothing measurable |
| queued on the neighbor's yard side only (`TIGHT_BEARING_DEG` 112.5) | 12 | 8 | 6.5 -> 7.7 s (+18%) |
| ...and one way-of-its-own verdict a seat (`own_way`, a301f4e2a) | - | - | the tight seats 2.15 of 14.1 s (15%); 18.7 -> 23.3 s alternated at load 14 |
(observed 2026-10-03, method: as the heading.)

Where the passages came from, every bearing offered (13 settlements, 498 tight tries): 15 of the 16 within 90 degrees of the
bearing from the neighbor's house to its yard (0: 6, 45: 3, 90: 6), 1 from behind the house (135 degrees) in 194 tries there; the
tries before a passage ran from the 3rd to the 42nd, so a cap on tries would have cut passages as much as cost. The fallback form
was cheap because, with the route kept off a household's own beds (R4), a household with no way of its own at an ordinary seat is
rare - 21 seats at 15 households on eight seeds - so a design that waits for one seats few. The MODE 1 ruling asks the growth to
offer the seats, and the queued form does.

On the yard side, before `own_way` (`tight_cost.py`, one run, a 21.7 s stage at load 13): the tight seats 4.0 s - their settles
0.78 s (405 popped), their placer calls 3.24 s (207 tried), of which the walks 0.98 s (169 asked, 106 found) and the corridor
searches after a walk 1.75 s (106 asked, 93 found: a way of its own, the seat refused).
(observed 2026-10-03, method: as the heading.)

With `own_way`, of 208 tight seats tried: 108 walks asked, 55 found; 55 corridor searches, 43 found (refused: a way of its own);
12 households admitted. The stage's remaining tight cost is the settles of the popped tight seats (402 popped, 0.53 s) and the
placer's calls (1.62 s).
(observed 2026-10-03, method: as the heading.)

## R8 - Against main: what the whole feature costs, the regressions it found, and how each was closed (method: `t07.sh` against origin/main 2ba3c353c, `t07-*`; `prof.py` call counts (a profile's function calls, which the host's load does not move) against the worktree at origin/main f9e8770a5 (feature 315); `passage_faithful.py`, `tight_features.py`, `refusals.py`, `corridor_only.py`; the bookends `317-start` (/tmp/main317b, f9e8770a5) and `317-end`, taken back to back three times)

**Seed 47 at 20 households refused** (T07, engine a301f4e2a): `WebRefused`, an access lane's bends. `straighten_joints` joined two
access lanes meeting end to end at a door - a corridor hung from another's start - and pulled the pair taut round the walls,
dropping a bend's vertex and kinking at the next. Fixed (bebed7632): a joint's pull is refused where it makes a kink the two did
not have. The cohort (`make cohort N=24 JOBS=2`, the six pinned seeds included): 25/30 on both main and the clone - seeds 14, 15,
906, 22, 23 on both, the Diagram (Inashiro) session's, landed in feature 315.

**The 80 ft cut** (`TIGHT_TREE_FT`): at 15 households on 13 settlements no passage came from a tight seat nearer the access tree
than 87 ft; of the 135 of 343 tight tries nearer than 80, every one whose walk was found had a corridor of its own (9 of 9). A
straight-line test from the seat to the tree (does it cross a homestead?) predicted nothing (5 passages from 195 "clear" tries, 5
from 148 "blocked").
(observed 2026-10-03, method: as the heading.)

**The household's land, not one layout** (`passage.landlocked`, 0ff3c6ef5): checking every garden layout at each passage seat,
10 of 13 passages at 15 households and 6 of 20 at 40 were households another layout would have given a corridor of its own - the
first layout with a walk and no corridor had been admitted. Judged by the land (some layout walks, none has a way): 7 passages at
15 households on 13 settlements, 8 at 40 on four. Every one of the 13 earlier passage households could reach the tree round its
house alone (`house_reaches`), so none was shut in by its neighbors: what refused its own way was its beds, the taut pull or the
lane law at one layout.

**Where the work went** (calls, seed 2 at 40 households): main 13.4M, the clone with the passage off 12.9M, with it on 24.7M; the
route search 154 calls and 0.52 s on main against 281 and 4.70 s. The search round the house alone reaching no goal now rules out
a door once for a seat's four layouts, asked only after a layout's own search found nothing (`house_reaches`, b1b208f03, exact).
(observed 2026-10-03, method: as the heading.)

**Seed 39 at 40 households, the bookend's band 3** (+48% to +58%, homesteads +4.8 to +5.3 s, passage budget 0): bisected to the
merge with feature 315 - the clone before it tried 287 seats, main 294, the merge 1,084. Feature 315 holds the persimmon in the
dooryard by the door, and the per-layout route's keep round its trunk left the 12 px grid no cell between it and the house (112
of 456 searches found nothing). Left out of the search's obstacles (the taut pull still keeps the legs off its trunk): 295 seats,
1.94 s (ec50fc817).
(observed 2026-10-03, method: as the heading.)

**The bookends**, three takes back to back on the engine as it stood (single wall-clock rolls a seed, the reference spec at 10, 15,
20 and 40 households on seeds 4, 25, 39, 47):

| engine | total | 10 hh | 20 hh | 40 hh | band |
|---|---|---|---|---|---|
| b1b208f03 (before the land-not-layout and persimmon fixes) | -0.8% | +8.8% | -32.1% | -16.4% (seed 39 +58.4%) | 3 |
| 0ff3c6ef5 | -4.9% | 0.0% | -37.0% | -21.6% (seed 39 +48.3%) | 3 |
| the persimmon fix | -6.5% | 0.0% (seed 47 +16.7%) | -35.8% | -30.1% (seed 47 +12.9%) | 2 |
(observed 2026-10-03, method: as the heading.)

**The per-layout route withdrawn, and the passage's cost alone** (homesteads stage, profile calls against main f9e8770a5 on the
bookend's flagged seeds; `houseonly.py` and `NOPASS=1` in the session's scratchpad switch each off): with the passage off, the
route searched per garden layout round its own parts did 4.72M / 3.26M / 15.52M / 3.48M calls (15 households seeds 4 and 25, 40
households seed 25, 10 households seed 47) against main's search round the house alone at 4.59M / 2.99M / 11.64M / 2.43M - 3% to
43% more, where main does 4.40M / 2.87M / 12.34M / 2.29M. Withdrawn (5307dd602). With the passage on, the feature's homesteads
stage does 6.11M / 4.45M / 24.04M / 3.31M - +39% / +55% / +95% / +44% against main - all of it on settlements whose share allows a
passage (budgets 1, 3, 9, 2). Where it goes (40 households seed 25, budget 9): the route searches that prove a tight seat has no
way of its own (143 searches against 87, 3.8 s against 0.7), the seats' landlocked test (1.2 s), the extra tight seats' settles
and layouts (about 1.7 s), the walks (0.8 s): the stage 4.3 -> 9.1 s.
(observed 2026-10-03, method: as the heading.)

**The anchor's way** (the village lane's glyph-check on Inashiro, NEEDS-WORK F1): the one passage household there was reached
across a neighbor whose center stood 90 ft from a lane, inside `WEB_REACH_FT`, so the web owed its corridor nothing and two
farmsteads showed no way. Fixed (5307dd602): the corridor of every house another is reached across is owed and never pruned.
(observed 2026-10-03, method: the glyph-check's measurement on the review snapshot.)

**The persimmon short on Inashiro** (the gate at engine 2d7e7cf060a1, B10: 11 drawn of 12 rolled): feature 315's reseat gives a
tree the count is short of to a household that rolled none, searching its dooryard on its rolled side, and asked a neighbor's sun
only of the seat the search returned - so a household whose first seat shaded a neighbor gave the tree up, though a later seat, or
the other side of its house, shaded no one. The tight seats moved Inashiro's homesteads, and all four households without a tree
were refused that way. Fixed (6adad5792): the neighbor's sun is part of the search's own test, asked of every seat it tries, on the
rolled side and then the other - 12 of 12. A tried alternative, refusing a tight seat whose layout dropped its persimmon, was
reverted: the tree is the hamlet's count's, not the household's.
(observed 2026-10-03, method: `persim_probe.py` in the session's scratchpad, the reference spec rolled and its persimmons counted.)

## R9 - The research claims (feature 316, merged 2026-10-03): what the impl-drift check found, and what was done (method: `make claims-owed`, `make claims-bundle UNITS=`, the `impl-drift` contract given to eight ad-hoc Opus agents - the agent file landed after this session started - `make claims-checked`, `scripts/_claims.py gate`)

**Owed.** Merged with feature 316, the feature owed 387 claims in 41 files: 34 new (the passage's units), 54 whose code changed,
299 whose cited research changed - every claim citing 0081-village-lanes, whose findings this feature rewrote. Round 1, eight
batches by file: 298 IN-STEP, 51 DRIFTED, 19 MISLABELED, 11 NEEDS-RESEARCH, 8 CANNOT-TELL, and 37 UNCLAIMED decisions. The push's
verdict counted 72 of them introduced (a finding on a claim whose code or cited research moved since main's index) and 527
pre-existing across the engine, which only warn.
(observed 2026-10-03, method: as the heading.)

**What the feature owed, and fixed** (d7c5fb007): the lanes still treated a household reached across a yard as owed a way of its
own - an arm or fragment kept as its "only way" (`smooth._smooth_web`, `touch._touch_junctions`, `sweeps._sweep_debris`), a
dangling end carried to its dooryard (`sweeps._sweep_dangling_ends`), the web's cuts spaced to cover it (`web.py`). One rule now
says who a lane serves (`geom.lane_houses`); the pool's five hamlets rolled byte-identical on it. `fit._on_the_access` left a grove
farm's kura and byre out of the parts it keeps off a corridor. The passage's units cite the drawing page that records them;
"every farmhouse served" names the exception wherever it is claimed; `stage_web`'s and `WEB_REACH_FT`'s "the record is decisive"
reads "not always". Claims the page does not answer are UNRESEARCHED, or the page's GUESS where it records one, as the check said.
(observed 2026-10-03, method: as the heading; the pool by `make map` on each of the five and `git status`.)

**What it did not fix, and why**: the pre-existing figures the lane code and the 0081 drawing page disagree on - ends joined at
11.5 ft (`joints._MEET_FT`) and at 30 ft to a way's side (`law.JOIN_REACH_FT`) where the page says 25; a 4-6 ft gap off a fence or
the fabric in five passes, and 5.5 ft for the field way, where the page says 7; the exit strip drawn 3 ft where the page's spine
is 5; the track's and the spur's bows where the page pulls every lane taut; and the farmhouse sizes against 0029. Each is a
decision between the code and the page - change the map or record the deviation - and recording them is an edit to the 0081
drawing page, which re-owes all of its ~300 claims a check. A feature of its own, put to the GM; the push carries them by
`CLAIMS_OK` with this record named.
(observed 2026-10-03, method: as the heading.)

**Rounds 2 to 4.** Round 2 (83 claims, two batches): 73 IN-STEP; it found the dangling-end sweep's end rule still counting a
household reached across a yard, and `TIGHT_BEARING_DEG` (112.5) past the page's "the side ... where the neighbor's threshing yard
lies" - held to 90 (e26349c0a). Round 3 (23 claims): 21 IN-STEP; the rest claim wording, answered in 4e375737a.
(observed 2026-10-03, method: as the heading.)

**The condition on the finished seating** (the farmhouse glyph check, NEEDS-WORK F5): Inashiro's one household reached across
a yard had a drawn lane 10 ft from its homestead - `landlocked` judged it at its seat, and a later household's corridor was
reserved past its beds. `passage.recheck_passages` asks every such household again once all are seated (e26349c0a); on the
re-rolled Inashiro its center stands 116 ft from the nearest drawn lane.
(observed 2026-10-03, method: the reviewer's measurement on its snapshot; the re-rolled manifest's lanes against the house.)

**By its whole holding, on the finished seating** (impl-drift round 4 DRIFTED, the plan review's MODE 4 NOT LEGITIMATE on asking
the drawn layout only): the drawing page judges a way of its own "by its whole holding ... if any layout of the homestead would
leave it a way of its own, it has one". The four layouts built at a tight seat - the household's lot installed, its fixtures,
byre and well laid in each - are kept (they differ beyond the beds at 13 of 15 seats), and the recheck asks each; one with a
corridor that fits the finished seating, judged as the placer judges a layout with the household's own record, homestead, walk
and wood reservations set aside, re-seats it (`passage.relay`). Asked of the drawn layout alone, another layout had a way for 1
of 15 such households at 15 households and 1 of 12 at 40 (a first probe that built the layouts without the lot counted 2 and
3). With the re-lay: none is left with a way that no longer fits (`meta.passage_unfit` 0 on every seed below).
(observed 2026-10-03, method: `layouts2_probe.py` - the layouts captured at `landlocked` - and `relay_probe.py`, in the session's
scratchpad.)

**The route's withdrawal finished** (the perf-audit's second confirmation): with the passage share at 0 the homesteads stage still
stood 0.3 s (18%) over main at seed 39, 40 households. T06's withdrawal had restored the route round the house alone but left
`access_corridor` routing again for each of a seat's four layouts, each with its own parts in the legs' tests, where main
yields the routes in `_house_candidates`' stream, shared by the seat's layouts. Restored as on main (014cb1a20): 1.64 s against
main's 1.57 (`perf-317-route-shared`). Kuwabata re-rolled on it.
(observed 2026-10-03, method: `control_probe.py` in the session's scratchpad, three alternated takes.)

**How many are reached across a yard, as the feature lands** (`relay_probe.py`, the reference spec, the engine as it lands -
the routes shared by a seat's layouts): at 15 households on seeds 1-16, 13 households reached across a yard and 9 passages ended
by the recheck (the 13 settlements whose share allows one allow 30); at 40 households on seeds 2, 25, 39 and 47, 5 reached and 9
ended (the three that allow one allow 23) - seed 25 seats 5 by passage and keeps 1. With the routes shared more tight seats pass
the seat's test and are seated by passage, and a later corridor ends most of them at 40 households; the tight seats tried for
them are the bookends' band 3 (`perf-317-control-40`). R8's 7 and 8 were measured before the per-layout route was withdrawn.
(observed 2026-10-03, method: as the heading.)

## R10 - The GM's ruling of 2026-10-03, the wood seats, and the route search (method: `control_probe.py`, `count_probe.py`, `seq_probe.py`, `fail_probe.py`, `seats_planted.py` and `seat_why.py` in the session's scratchpad; homesteads-stage CPU seconds alternated with main at /tmp/main317c, 38901e2df, on a machine another session was loading - ratios within a take, not absolute seconds)

**The wood seats** (the village lane's glyph check, round 3, F5: lane 14 on Inashiro bulged 27 ft round bare scrub). The tree
draws each access lane as the seating routed it; house 14's path was routed round two seats of house 13's wood share, and the
copse never planted them: refused as "local" ground, inside the afternoon lane feature 310 holds every canopy tree out of, west
and southwest of a yard or bed. The reservation (`wood_share.copse_keepouts`) kept the south strip and the beds' morning lane,
not that lane. Unplanted reserved seats on main's pool: Inashiro 18 of 326, Kuwabata 16 of 347, Sawada 34 of 413; every one
refused by the local family. Fixed as feature 287's plan D9 holds the floor - by construction, a household seated only with
room for its floor - the reservation now keeps the lane by the copse's own figure; a gate test holds every recorded seat
planted (`tests/gate/test_wood_shares_planted.py`, red on all three before the fix). Inashiro after: 320 of 320 planted.
(observed 2026-10-03, method: as the heading.)

**What the seat fix costs.** Honest reservations leave less ground: at 40 households seed 39 offered 483 candidate seats against
155 with the lane left out of the reservation, and its growth widened a level; seed 47, with the passage too, seated 38 of 40
on its first margin, searched some 700 more seats, threw it away and seated all 40 on the second. At 15 households the stage
stands near main (per seed, two takes: seed 4 +19-36%, 25 +21-27%, 39 +2-4%, 47 4-9% faster).
(observed 2026-10-03, method: as the heading.)

**The cheaper test** (the GM's ruling, `request.md`: a way of its own asked of straight and round-the-gable corridors, no
routed search; `access.access_corridor(routed=False)`, `passage.landlocked`). Built as ruled. It seats more households across
a yard (seed 47 at 40 households: 6 against 5, the seat fix off in both), so the stage did not fall: a household reached across
a yard adds no branch to the tree, and the households seated behind it later find no path - their failed searches were the cost.

**The shared route search** (the GM: "Yes, definitely do this"). MEASURED BEFORE BUILDING: of seed 47's 509 failed corridor
searches at 40 households, none started inside a region an earlier failure, closed by standing ground alone at the same
standing state, had explored - a shared map of what is reachable would have answered none of them. 412 of the 509 ran to the
edge of their box, and 348 had no branch of the tree within reach at all: 760,468 of the 953,362 cells the failures opened. An
exact check before each search - no segment of the tree within the search's reach, no search (`route.tree_in_reach`) - takes
those out with the same verdict (Inashiro byte-identical); seed 47 at 40 households 35 s -> 19.9 s. On the amended engine seed 25 at 40 households - the cell the GM ruled on - keeps 19
failed corridor searches, each closed by the household's own parts (456 cells opened in all), none answerable by a shared map.
That check is built in
place of the shared map (plan D8, amended); the map is not built.
(observed 2026-10-03, method: as the heading.)

**SC-007, the check on and off** (`control_probe.py` with `NOPRE=1` patching `route.tree_in_reach` to always True; two
alternated takes, homesteads-stage CPU seconds, 40 households): seed 25 3.95 / 3.96 with it, 3.94 / 3.96 without - its failed
searches all had a branch in reach; seed 47 19.94 / 19.95 with it, 33.37 / 33.58 without. The seated manifest hashes the same
with it on and off on seeds 25, 47 and 39 (sha256 of the whole manifest after the homesteads stage), and the whole pool - Inashiro,
Kashikawa, Kuwabata, Mizuguchi, Sawada - hashes the same with it on and off after every stage but the labels (`pool_hash.py`).
(observed 2026-10-03, method: as the heading.)
