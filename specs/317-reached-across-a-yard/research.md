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
| Cohort seeds 22, 23 (linear, `WebRefused`) | Diagram (Inashiro), feature 315 | its last word, 2026-10-03: seed 22 fixed in 315 (commit 82ce6927b, a corner welded onto a tread in `settle_needles`), seed 23 passes on its engine, a full cohort running before its push. On this clone both still refuse (22: off_ford, 23: over_fixtures; `make cohort N=2 SEED=22`) - not this feature's |
| Cohort seeds 14, 15, 906 (dispersed: `trees_shading_plots`, `gardens_east_shaded`) | Diagram (Inashiro), feature 315 | owned and in progress (agreed 2026-10-02); 906 still fails on this clone |
| A headless page session resumed after a stall dispatched its returned checks again: their reports sat queued in its transcript, never taken up, and Claude Code told the resumed session they "didn't finish" | this feature (found running R1's checks) | fixed: the resume names a file of the queued reports and resumes early once they are back (`_page_session_runner.undelivered`, `returned_file`, `turn_ended`; fa30940d5, tests in `tests/tooling/test_page_session.py`) |
| A `resume:` page session that stalled would fail to be resumed (`--session-id` no longer in its command) | this feature | fixed in the same commit, tested |
| `pair-hooks.sh stop` read a green `make test-file` as a green gate and told sessions (a headless page session sharing the clone among them) to dispatch reviews no gate had earned | this feature | fixed: the stop branch asks the gate stamp as the pretool branch does (b54a76717); the new case fails with the old line (102 passed, 2 failed) and passes with the fix (104) |
| Cohort seed 18 (nucleated, 15 households) refused (`OverlapRefused`: lanes over farm_fixtures) - found by T07's cohort, made by the per-layout route: squaring a water crossing straightened a routed path's bend across the household's own privy | this feature | fixed: the seating judge asks the household's own house, beds and fixtures of the path as the web lays it (`tree.laid_run`, `own_clear`; 6a38205a0); `make cohort N=1 SEED=18` rolls |
| Seed 47 at 20 households refused (`WebRefused`: an access lane's bends) - found by T07's 20-household leg: `straighten_joints` joined two access lanes meeting end to end at a door and pulled the pair into a kink, a tree lane no settle may cut | this feature | fixed: a joint's pull is refused where it makes a kink the two did not have (bebed7632); the seed rolls, and the new test fails without the fix |

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

**How many are reached across a yard, as the feature lands** (`bearing_probe.py` in the session's scratchpad, the reference
spec; `meta.passage_reached`): at 15 households on seeds 1-16, 15 households, where the 13 settlements whose share allows one
allow 30 together; at 40 households on seeds 2, 25, 39 and 47, 12 where the three that allow one allow 23. R8's 7 and 8 were
measured before the per-layout route was withdrawn, when more tight seats found a way of their own; with the band at 112.5 and
no recheck the count at 15 households was 23.
(observed 2026-10-03, method: as the heading.)

**An accepted limitation, for the GM: the recheck asks the drawn layout only** (impl-drift round 4, DRIFTED on
`recheck_passages`): the drawing page judges a way of its own "by its whole holding ... if any layout of the homestead would leave
it a way of its own, it has one". At the seat every layout is asked (`landlocked`); once all are seated, only the layout drawn.
Of the households still reached across a yard on the finished seating, another layout at their seat would have a corridor of
its own for 2 of 15 at 15 households (seeds 1-16) and 3 of 12 at 40 (seeds 2, 25, 47). The alternatives priced: re-lay such a
household with that layout after seating - an in-place move of a homestead and everything recorded at its seat, which the
engine does in one guarded place (`_solve_homestead`); or record the drawn-layout recheck on the drawing page, which re-owes the
~300 claims that cite it. Accepted by the session for this landing, with the claim's DRIFTED verdict carried by `CLAIMS_OK`;
put to the GM.
(observed 2026-10-03, method: `layout_probe.py` in the session's scratchpad - after `recheck_passages`, each remaining passage
household's other garden layouts at its seat asked `access_corridor` with its own homestead set aside.)
