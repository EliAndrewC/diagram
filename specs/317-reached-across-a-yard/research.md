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

| leg | 15 households, seeds 1-8 | 40 households, seeds 2, 6, 10, 13 |
|---|---|---|
| the fix, before the prefilter, wall (`fix317-*`) | 9.9 -> 9.3 s | 19.5 -> 20.7 s |
| the fix with the prefilter, wall (`fix317b-*`) | 24.9 -> 26.6 s | 13.3 -> 12.4 s |
| the fix with the prefilter, CPU seconds (`fix317c-*`) | 21.6 -> 20.1 s | 15.6 -> 16.1 s |

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

From a corridor-only layout's first door, the nearest seated neighbor's threshing yard (box edge), in feet:

| | min | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|---|
| 15 households (n=296) | 64 | 126 | 141 | 158 | 176 | 203 | 231 |
| 40 households (n=336) | 74 | 107 | 126 | 144 | 164 | 175 | 205 |

and the access tree's nearest leg: median 166 ft (15 households), 156 ft (40), within the route's reach (`ROUTE_REACH_PX`, 320
px at the reference's 1 ft a pixel).

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

The layouts still refused stand at least 83-85 ft from the nearest neighbor's yard (median 143-145 ft).

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
