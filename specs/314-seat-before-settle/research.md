# Research: seat before settle (feature 314)

Every figure here was observed 2026-10-02, method: `refusals.py` (each grown seat followed to its outcome, the time of each phase
summed by outcome) or `abab.sh` (base and clone alternated per seed, one process a seed), on the reference spec, under the load
of the other sessions on this host (the same load on both legs; single runs vary by up to 2x, so only alternated legs are
compared).

## R1 - The GM's case, 15 households on seeds 1-16, where the time goes (observed 2026-10-02, method: `refusals.py 15 1,...,16` on the base, `r1-base-15.log`)

| what the seat came to | seats | time | share |
|---|---|---|---|
| refused on the ground (house box, field reach, water) | 471 | 0.9 s (settle) + 0.02 s | 4% |
| refused: no garden side fit among the standing homesteads | 753 | 1.2 s + 0.4 s | 7% |
| fit, refused by the parts (no lawful corridor, the lane law) | 574 | 1.0 s + 3.8 s | 22% |
| seated | 240 | 0.4 s + 5.4 s | 26% |
| outside the seat-by-seat loop (the first house's free ground, the boundary, the exit strip, the field's corridor, the stage's own bookkeeping) | - | 8.8 s | 40% |
(observed 2026-10-02, method: as the heading.)

The homesteads stage took 21.9 s summed, 1.37 s a map. At 15 households the ground-refused seats the pre-check (US1) drops are
4% of the stage, against 11% at 40; the largest single share is the work outside the seat loop.
(observed 2026-10-02, method: as the heading.)

## R2 - Round 2: the route searched on the map's grid (observed 2026-10-02, method: `abab.sh`, `r2-15-*.log`, `r2-40-*.log`; then `routecount.py` on seed 13 at 40 households)

The route's heuristic was computed at every push and pop of a cell (a third of the search, by profile); it is now computed once
a cell, which changes no route. To share what a grid point's standing ground answers between searches, the grid was made the
map's (multiples of the step) rather than each door's. Alternated against the base: 15 households 20.5 s both legs; 40 households
46.4 s base against 102.1 s - seeds 2, 8, 13, 39 and 4 needed three and four margins where they had needed one.
(observed 2026-10-02, method: as the heading.)

Why, measured on seed 13: 1,189 route searches, 1,072 of them found a path of cells and 1,016 of those were then refused when
pulled taut, because a leg crossed the household's own beds or fixtures (`parts_clear`, `fixtures_clear`). The search kept off
the house's own box only; laid from the door, its first steps had run straight out of the yard, and on the map's grid they ran
along the house front into the beds. Fixed three ways, each the taut pull's own test asked earlier: the search keeps off the
household's own parts by the gaps their leg tests keep; its first step from the door (up to two cells) is judged by the leg test;
a goal whose last leg onto the tree the standing ground refuses is no goal. Seed 13: 82 searches, 38 routes, one margin, 3.1 s
(the base 4.7 s).
(observed 2026-10-02, method: as the heading.)

A start at the grid point nearest the door, or the first step widened to two cells, alone changed nothing (the same 7,690 seats
popped) - recorded so neither is taken for the cause again.

## R3 - Rounds 1-3 on the map's grid, alternated (observed 2026-10-02, method: `abab.sh`, `r3-15-*.log`, `r3-40-*.log`)

With R2's fixes and the map's grid still in place: 15 households 19.5 s base against 18.8 s; 40 households 48.4 s against
51.0 s - nine seeds faster (seed 2 5.66 -> 2.60 s, seed 10 6.50 -> 3.95 s), and seed 6 three margins (5.94 -> 19.52 s). Without
seed 6, 42.5 -> 31.5 s.
(observed 2026-10-02, method: as the heading.)

## R4 - The door's grid again (observed 2026-10-02, method: `refusals.py` with the grid switched by environment on four seeds at 40 households; then `abab.sh` against the base, `r4-15-*.log`, `r4-40-*.log`)

Seed 6 on the map's grid: 202 of 545 searches found no path at all - the narrow ways between homesteads held no grid point of
the map's 12 px grid, where a grid laid from the door runs straight out through the gap the door faces. The door's grid with
R2's fixes, against the map's, on the same four seeds: seed 6 2.21 s against 16.44 s, seed 13 3.03 against 2.85, seed 2 2.03
against 2.32, seed 10 3.11 against 3.76 - every seed on one margin. So the sharing was not what paid; the tests asked where the
path is searched were. The map's grid is withdrawn (plan D3).
(observed 2026-10-02, method: as the heading.)

The first step's test was cheapened at the same time: asked with the whole leg test, it ran the ways' ground test on up to 24
first steps a search, half a route's cost at 15 households (profile, seed 5); the refusals it exists for are the household's
own (R2), so it asks `house_clear`, `fixtures_clear` and `parts_clear` alone.

Rounds 1-4 (the pre-check, the route, the persimmon's sun ground, the indexed water) alternated against the base:

| households | seeds | base | clone | change | margins |
|---|---|---|---|---|---|
| 15 | 1-16 | 21.3 s | 17.5 s | -18% | one on every seed, both legs |
| 40 | 1, 2, 4, 6, 8, 9, 10, 12, 13, 39 | 49.1 s | 30.1 s | -39% | one on every seed, both legs |
(observed 2026-10-02, method: as the heading.)

At 40 households every seed is faster or level (seed 8 2.64 -> 2.63 s). At 15, thirteen of sixteen are faster; seeds 4 (1.09
-> 1.31 s), 9 (1.12 -> 1.18 s) and 11 (1.38 -> 1.43 s) are slower, by less than a single run's spread on this host.
(observed 2026-10-02, method: as the heading.)

## R5 - The placed homesteads asked of the house and its yard before the layout, priced and withdrawn (observed 2026-10-02, method: `abab.sh`, round 4 as the base leg and the clone with the check as the new, `r5-15-*.log`, `r5-40-*.log`)

The plan review asked for FR-002's cheap test of the placed homesteads to be priced, not argued away. Every garden side's box
holds the box round the house and its threshing yard (both the same for every side, feature 297 R6), so the house box's tests
asked of that box - the canvas, a reserved corridor, two placed homesteads, the refused-ground grid - refuse every layout when
they refuse it, and it is computed without laying anything out (`_core_box`, the yard's rolled size and the seat's rake; a test
held it equal to the laid boxes' bbox at four seats, two sizes, every side). Asked at every position the settle would lay the
household out at, in place of the house box:

| households | round 4 | with the check | change |
|---|---|---|---|
| 15 (seeds 1-16) | 19.4 s | 20.2 s | +4% |
| 40 (ten seeds) | 34.5 s | 38.2 s | +11% |
(observed 2026-10-02, method: as the heading.)

By round 4 the seats refused for no garden side fitting were 34-52 a seed at 40 households (the base's 70-744): the seats that
reach the placer are mostly good ones, so there was little left to catch. And the larger box refused positions the settle
would have moved past onto clear ground: seed 4 popped 1,721 seats against 290, seed 9 753 against 300. Withdrawn; the house
box alone stays (plan D1).

## R6 - The field's corridor: its ground read once for every candidate (observed 2026-10-02, method: `prof.py 15 13`, then `abab.sh` against the base, `r6-15-*.log`, `r6-40-*.log`)

On seed 13 at 15 households the field's corridor (`reserve_field_corridor`, reserved once a margin before any house) took 3.4 of
the stage's 5.8 s, profiled: it tried 145 candidate runs, and `corridor_on_lawful_ground` built a new `Lawful` - indexing every
water course, outline and farmstead part of the map (`GroundIndex`) - for each. The candidates are tried on one standing
manifest, so the caller now builds one `Lawful` and hands it in; and a run is squared through `Lawful.squared`, which skips the
squaring where no water comes within its reach (where it changes nothing). Profiled, 5.8 -> 3.7 s on that seed.
(observed 2026-10-02, method: as the heading.)

Rounds 1-6 alternated against the base: 15 households 26.2 -> 22.8 s (-13%), 40 households 49.8 -> 29.1 s (-42%), every seed on
one margin. The 15-household legs ran under heavier load than R4's (the base leg 26.2 s against 21.3 s), and single runs vary
there; three runs of three seeds each (the fastest kept): seed 1 1.64 -> 1.24 s, seed 11 1.09 -> 1.05 s, seed 4 1.11 -> 1.38 s.
(observed 2026-10-02, method: as the heading.)

## R7 - Seed 4 at 15 households, slower (observed 2026-10-02, method: `prof.py 15 4` on both engines; `routecount.py`; `searchsize.py`)

The base's 42 route searches on seed 4 found a path of cells every time and 37 of them were refused when pulled taut (its
search ran through the household's own beds, R2) - cheap searches that bought 5 routes. The clone's 34 searches buy 11 routes,
and its placer is asked 54 times against 105; but each search that must detour round what stands pops up to 1,168 cells (the
nearest aim 12-17 cells away, the goal 24-27), and 7 that find nothing explore the whole reach (2,501 cells). A heavier weight
on the aim did not help (1.5: 1.35-1.46 s; 2.5: 1.48 s; 4.0: 1.77-1.82 s on seed 4). The detour is the search doing what it
must; the route grid stays as it is.
(observed 2026-10-02, method: as the heading.)

## R8 - The courses out of a run's reach (observed 2026-10-02, method: `prof.py 15 13`)

`square_run` squared a run at every water course of the map and `law.oblique_at` compared every lane segment with every course
segment (the overlap census's 356,470 comparisons in the homesteads stage). Each now skips a course whose box, grown by its
reach, misses the run's: no crossing there and no vertex within reach, so nothing changes. On seed 13 the 145 field candidates
all stand by the brook and a drawn channel, so little was skipped there (`square_run` 0.47 -> 0.38 s profiled); kept as exact.
All 144 refused candidates on that seed cross the brook and a channel more than the tolerance off square after the squaring
(`fieldwhy.py`).
(observed 2026-10-02, method: as the heading.)

## R9 - Where the 15-household stage goes now, and what an efficient process would do (observed 2026-10-02, method: `split.py 15 1,...,16`, wrapping the stage's parts, one process)

16.7 s over seeds 1-16, 1.04 s a map:
(observed 2026-10-02, method: as the heading.)

| part | share | what it is | what an efficient process would do | where the stage stands |
|---|---|---|---|---|
| the growth (`grow_the_margin`) | 59% | 41 ms a house seated: the corridor search (straight runs, the gable, the routed path) and the lane law over the whole tree are about 70% of it (profile, seed 13); the household's layout at each seat offered, the rest | find a house's path once, where its seat is chosen, rather than search for it after: lay the hamlet's lanes first and seat the houses along them, so each corridor is a short spur the lane law has already judged | the cheap form - the same seats, the reachable first - measured no gain (R10). The full form plans the lanes before the houses, which changes the GM's growth (feature 308: the houses grown first, each path laid back as it is placed); put to the GM, not taken here |
| the field's corridor | 15% | one corridor per margin, 0.07-0.19 s a map, 0.50 on seed 13 where 144 candidates cross the brook and a channel obliquely | generate the runs that cross square at a ford, instead of generating any run and refusing the oblique ones | NOT DONE: the candidates are the ways package's (`field_runs`, `routed_field_runs`); recorded |
| the site boundary | 11% | the ground asked once, 0.08-0.17 s a map (feature 226) | already the efficient form: built once, looked up per seat | DONE |
| the rest of the stage | 15% | the margin's choice, the exit strip, the seat region, the records | each once a margin | DONE |
(observed 2026-10-02, method: as the heading.)

## R10 - Seats with a straight run to the tree offered first, tried and withdrawn (observed 2026-10-02, method: the growth's heap ordered three ways - by distance from the seat as shipped, by a straight shot to the tree's nearest point within 40 ft bands of distance, by a straight shot first - `refusals.py` on six seeds at 15 households and four at 40, one run each, `r10.log`)

R9's efficient process offers the seats a path already reaches. The cheapest form of it - the same seats, offered in an order
that puts first those whose line to the access tree's nearest point clears every placed homestead - bought nothing: summed, 15
households 7.05 s as shipped, 7.30 s banded, 7.14 s shot-first; 40 households 10.81, 10.63, 10.58 s - within a single run's
spread, every seed on one margin. The corridor search is not where order can help: the seats the growth offers are mostly
reachable already (R4: the placer is asked 54 times for 15 houses on seed 4), and what costs is the search and the lane law on
the seats it seats. Withdrawn.
(observed 2026-10-02, method: as the heading.)

## R11 - The cohort against the base (observed 2026-10-02, method: `make cohort N=24 JOBS=4` in the base worktree and in the clone, seeds 1-24 and the six pinned)

Both 28/30, the same two failures on both: seed 5 (dispersed, `fixtures_on_groves`, a woodpile on a grove) and seed 903
(linear, `WebRefused`). Neither form grows, so neither is this feature's; both stand on the base as on the clone (feature 308
recorded them with the persimmon change, owned by the session working the grove and canopy rules, feature 310). No household
lost, no seed refused that the base seated. `JOBS` was added to `make cohort` for this run: its workers were cpus - 2 with no way
to ask fewer, 20 on this host and ~10 GB, past the containers' shared cap while other sessions ran.
(observed 2026-10-02, method: as the heading.)
## R12 - The 20-household leg: the route's own parts withdrawn (observed 2026-10-02, method: the bookends `314-start` (re-taken at main with feature 310, the worktree `/tmp/start314b`) and `314-end`; `stagetime.py` per stage, both engines; the route's parts switched by environment to bisect)

The end bookend read band 3: the 20-household leg +7.7%, seed 4 +34.9% and seed 39 +22.0%, the web stage +1.9 and +1.7 s; the
10, 15 and 40 legs were faster (-4.0%, -3.5%, -17.7%). Rolled stage by stage on eight seeds at 20 households, the web was 0.95 ->
2.97 s on seed 4 and 1.04 -> 2.83 s on seed 39 - the cluster's skeleton lanes laid as an island across the brook, 650-720 ft from
the network, which `_join_orphan_ways` searched to join and refused every time - and seed 13 was REFUSED (`WebRefused`: three
access lanes the web's last resort could not mend, needle loops) where main rolled it. Bisected on seed 13: the two-cell first step
and the last leg's test were not the cause; the search kept off the household's own parts was - with it off, the seed rolled (35
corridors, as main's) and seeds 4 and 39 drew their web in 0.96 and 1.34 s. Withdrawn (plan D3): the search keeps off its own house
only, as before; its first step and its last leg keep their tests.
(observed 2026-10-02, method: as the heading.)

A DEFECT THIS FOUND, NOT FIXED HERE: the seating admits a corridor by the lane law over the whole tree (`tree_admits`, feature 287
wave 6, whose promise is that the web can always draw what was reserved), and three corridors it admitted on seed 13 broke the
lane law once the web drew them. Mechanism (sketch): the seating judges the corridors as lanes before the web's own passes (the
joint pass, the squaring at crossings, the settle's cuts) reshape them, so a corridor that winds round its own beds is lawful as
reserved and loops once squared or joined. The fix is the seating judging the corridor as the web will draw it (the squared, joined
form), which is a change to `ways/tree.py:admits` and the web's passes - beyond this feature; raised with the GM.
(observed 2026-10-02, method: as the heading.)

## R13 - The rounds as shipped, against main (observed 2026-10-02, method: `abab.sh` with `/tmp/start314b` (main with feature 310) as the base, `r12-15-*.log`, `r12-40-*.log`; `stagetime.py` at 20 households, `r12-summary.txt`)

| households | seeds | main | clone | change | margins |
|---|---|---|---|---|---|
| 15 | 1-16 | 20.3 s | 19.2 s | -5% | one on every seed, both legs |
| 40 | 1, 2, 4, 6, 8, 9, 10, 12, 13, 39 | 46.5 s | 36.1 s | -22% | one on every seed, both legs |
| 20 | 1, 2, 4, 5, 13, 25, 39, 47 | homesteads 12.25 s, web 9.04 s | homesteads 11.01 s, web 8.32 s | -10%, -8% | seed 13 rolled on both |
(observed 2026-10-02, method: as the heading.)

With the own parts withdrawn (R12) the 15-household gain falls from R4's -18% to -5%: the own parts were most of what the search
saved there, and the web paid it back. At 40 households seeds 4, 8 and 12 are slower on this run (4.57 -> 5.11, 2.57 -> 5.85,
3.39 -> 4.02 s), the other seven faster. Seed 8 popped 1,805 seats against main's 297, 1,220 of them dropped by the pre-check (plan
D1): there a position refused mid-settle is dropped where the settle would have moved on, and the growth widens instead - the
cost the spec's Decisions row accepted as search breadth, measured. Asking the pre-check only at the settle's first position is
the next round's candidate, not taken here.
(observed 2026-10-02, method: as the heading.)

## R14 - The pre-check at the settle's first position only, tried and withdrawn (observed 2026-10-02, method: `refusals.py`, the pre-check asked at every position the settle lays out at (as shipped) against at its first only, switched by environment, nine seed runs)

R13's candidate: a position refused mid-settle drops the seat, and on seed 8 at 40 households the growth widened for it (1,805
seats popped against main's 297). Asked at the first position only, seed 8 needed TWO margins (11.62 s against 5.63 s, 4,114
seats popped); seeds 4, 12 and 10 at 40 were a little faster (5.06 -> 3.89, 3.83 -> 3.49, 3.71 -> 3.65 s), seed 2 a little
slower; at 15 households seed 13 1.58 against 2.03 s, the other three level. A lost margin outweighs the rest; withdrawn. The
pre-check stays at every position (plan D1).
(observed 2026-10-02, method: as the heading.)
