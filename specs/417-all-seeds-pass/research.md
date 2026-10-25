# Feature 417 - research

## R1 - what a fresh block costs, and what it finds (measured 2026-10-24)

Observed 2026-10-24. Method: `make cohort N=100 SEED=3000001 FRESH=0 JOBS=12` at main `b3f6738c2` (no engine diff), under `/usr/bin/time -v`;
seeds 3000001-3000100 were never rolled before. Host: 22 CPUs, load 1.3 at the start, 15 GB with the containers' 10 GB cap.

Observed 2026-10-24; method: that run's `time -v` and its log:

| block (observed 2026-10-24; method: `time -v`) | wall | per seed | peak RSS of the make | failed |
|---|---|---|---|---|
| 100 fresh + 6 pinned | 4 min 41 s | 2.8 s | 136 MB (the workers are children) | 9 of 100 (9%) |

Observed 2026-10-24; method: that run's log. The nine: `lane_knots` (3000015, 3000054, 3000066), `WebRefused` (3000047, 3000053), `BrookRefused` (3000019),
`SiteRefused` (3000069), `groves_crossed_by_lanes` + `lane_knots` (3000078), `row_rules` (3000086). The same causes, in the
same order, as the spec's tally over 2,544 seeds (14%); the lower rate is within one block's spread (the logged 48-seed blocks
ran 6-21%).

**What it decides (D1).** From the run observed 2026-10-24 (method above; 2.8 s of wall time a seed with 12 workers running): a block
of 500 is about 23 minutes; zero failures in 500 bounds the true rate under
0.6% at 95% (the rule of three, 3/500). A block of 1,000 is about 47 minutes and bounds it under 0.3%. 500 is SC-001's N;
1,000 is the closing measure.

## R2 - the inventory (FR-002)

Observed 2026-10-25 (method: three `Explore` agents on `sonnet` , plan D10, and the session's own sample) - the lane web; the homesteads, homestead parts and water;
the rest of the engine - each given D3's five searches and five classes. Their replies are kept verbatim in `inventory/`
(`ways.md`, `homesteads-water.md`, `rest.md`): each entry is `file:function (line) | class | what it does`. The session
checked a sample of each against the code before taking it (all held: `tails.py` `_ALONG_DEG` 25 against `_DOUBLED_DEG` 15;
`route.py`'s literal 140 / 50 / 40; the 40 ft tail in `sweeps`, `bund`, `settle/shapes`, `clearance`; `wells.reach_wells`
asking `dry_households` of the placed map; `persimmon_reseat.give_way`; `belt_law._cut`; `twins.drop_twin_deliveries` after
the comb draws; `driver.generate` returning `failures=[]`; `belt_polygon`'s ladder falling through to its last rung), and
ran the three cross-package searches itself (`inventory/cross.md`): every rule `cohort_audit` asks is called by no placer, and
the placers that mention one carry their own copy - so the audit-only rules are, nearly all, rules coded twice as well.

The classes: P1 not asked before placing; P2 placed then repaired; P3 a finished-map check run in the generator; P4 a drop,
relaxation, shortfall or refusal where room is the remedy; TWICE a rule coded twice. The groups, each an engine task in
`tasks.md` (T04-T15), by R1's share of the failures:

| group (observed 2026-10-25; method: the three inventories in `inventory/`) | where | what the inventory found | failures it bears on |
|---|---|---|---|
| G1 one lane rule, one predicate | `ways/` | 16 rules coded two to seven times: the doubled-tail angle (25 against 15), the shadow (four bodies), the hook (five), the bend (literals in `route.py`), the 40 ft tail (six), the 25 ft join (seven), the reach to a farmhouse (three), the serve distance, the network tolerance (25 ft against 4 ft), the foul, the dangling end, the street end, the link width, the spur reach, the debris floor | lane_knots, WebRefused |
| G2 the web laid by the law | `ways/web/stage.py`, `settle/`, `sweeps`, `touch`, `smooth`, `joints`, `tails`, `bund`, `squaring`, `weld`, `knots`, `web/tidy`, `street`, `geom._trim_to_service` | about 25 passes after the lay (several run two or three times) and the settle's 16 steps to a fixpoint (P2); `keeper.unsettled`, `last_resort.lane_breaches` and the reach counts asked of the whole web in the run (P3); `law.LAW` rules with no placer predicate for an ordinary lane - husks, shallow crossings, needle loops, over-and-back, off a ford, oblique, unbridged, undeckable, decks, planks (P1) | lane_knots, WebRefused (about 60%) |
| G3 refusals and drops in the ways | `last_resort`, `settle/ends`, `track`, `gateway`, `thread`, `route`, `forced`, `reserved.release_seats_along` | ordinary lanes dropped whole, `WebRefused`, `NoDryExit`, spurs given up, angle rules waived where ground blocks, wood seats released (P4) | WebRefused, NoDryExit |
| G4 seating room | `homesteads/stages`, `capacity`, `growth`, `rolling/gap_ways` | `SiteRefused` on a short margin, `DRY_SPELL` give-up, the rank rounds' drop after round 4, pinched passages across a yard (P4) | SiteRefused (about 15%) |
| G5 the row village's rules into the row placer | `homesteads/row_rules`, `rows`, `farm_water`, `wells`, `bamboo` | `row_rules`, `water_rules`, `bamboo_mismatch` asked of no candidate (P1); `wells.reach_wells` asking `dry_households` of the placed map (P3); door reach at 8 ft and 12 ft (TWICE); wells over ten recorded, not prevented (P4) | row_rules |
| G6 the grove rules into the grove placers | `homestead_parts/grove_rules`, `belt_law`, `stands`, `stocking`, `wood_goal`, `grove_fill`, `groves`, `persimmon_reseat`, `rolling/farmsteads`, `fit` | five grove rules asked only by the audit (P1), `fixtures_on_groves` coded four times and `gardens_east_shaded` twice (TWICE); the belt read and repaired as it is planted, trimmed to the wind, copse dropped to stocking and goal, crowns taken out from under a persimmon (P2) | groves_crossed_by_lanes, trees_shading_plots |
| G7 one stream-crossing rule | `tools/cohort_audit.parts_across_brook` against `_geom/water_index.crosses_a_stream` | the audit's own segment test (TWICE) | farmstead_across_brook |
| G8 the brook, the sink, the field and the polder | `water/brook`, `brook_course`, `sink`, `water/fit`, `water/polder` | the course repaired then judged, `BrookRefused`; the sink's off-map fallbacks and `SinkRefused`; the field judged as a finished net, `FieldRefused`; the polder's edge wander relaxed, dike gaps added after (P2, P3, P4); the axis test three times, the acute turn three times (TWICE) | BrookRefused, SinkRefused |
| G9 the paddy cells | `waterfields/settle`, `seams/close`, `ring_rules`, `furrows`, `twins`, `trunks`, `tint`, `polder`, `banks`, `comb` | cells cut then judged, merged or left bare; rings split and welded; twins and stubs deleted after drawing; the needle coded five ways at 15 and 25 degrees, the tract seam at three thresholds (P2, TWICE) | (no seed failure named today) |
| G10 the hinterland and the land | `hinterland/stages`, `parcels`, `belt`, `land/cover`, `land/wet`, `land/dikes` | dike trees thinned after the yards, holes filled until the bare share passes (P3), woodland regraded, parcel set-backs relaxed, the belt's ladder shipping its last rung fouled, marshes and ways dropped (P2, P4); the frame share three ways (TWICE) | (none named today) |
| G11 the overlap registry | `overlap/registry`, `matrix`, `taxonomy` | `resync` after every stage and `OverlapRefused` as the backstop (P3, P4); `forest_reveal_x` and the clamp mirrored by hand (TWICE) | OverlapRefused |
| G12 the rest | `labels/hand_sheet.repair`, `labels/placer`'s least-cost seat, `finish.settle_beads` and the beads dropped twice, `city/bridges` (`UndeckableCrossing`, `_reseat_to_cover`), `byres.draft_byres`' relaxed tiers, `wells._place_wells` (TWICE with `well_at`), `pondstock` asked at reserve and at stage, `cluster.belt_off_canvas` and `seat_has_dry_exit` (TWICE), `washing`, `pondbank`, `marsh` shortfalls | (UndeckableCrossing, a handful) |

Kept (asked before placing; listed in each inventory file under KEPT): the overlap registry's `admits`, `Lawful` and
`corridor_on_lawful_ground`, `tree.admits`, `_draw_web`, `brook_violations` asked of candidate courses, `sty_seat` (the
model: it asks the audit's own predicate `fixture_on_band` before placing), `crosses_a_stream`, `bundle_admitted`, and the
rest the files name. The title's ladder is the one that ends in more room.

**What it says about the work.** The pattern is not one module's: it is in every placer family. The engine tasks are G1-G12;
G1 and G7, and the parts of every TWICE whose copies hold the SAME value, can be made one predicate without moving a map;
everything else moves maps.

## R4 - the principle, drafted for the GM (FR-003, D6)

Proposed as a new principle of the constitution, in these words, for the GM to approve or change. APPROVED 2026-10-25 (the GM: "I also approve the new principle for the constitution.") and entered as Principle XIX, constitution 2.32.0 - XVII and XVIII were already taken, so the numeral below is the draft's:

> **XVII. Placed Right, Never Repaired.** Every rule a map keeps is ONE predicate. The placer that could break it asks it of
> each candidate before the candidate is placed, and places only what it admits. Nothing is placed and then moved, cut,
> thinned or dropped to make it lawful. A check of the finished map calls the same predicate, runs in the cohort and the
> tests only - never inside the generator's run - and its firing is an engine defect. Where no candidate is admitted, the
> answer is more room (the GM, 2026-10-12, "room before packing"), never a relaxed rule, a dropped feature or a refused map.
> A rule coded in two places is a defect of this principle. (Feature 417; the GM, 2026-10-24: "a general rule that 'place
> then check' is not something we want **anywhere** in the codebase".)

## R3 - the baseline: 1,000 fresh seeds at main (FR-001, T01)

Observed 2026-10-25; method: `make cohort N=1000 SEED=3000101 FRESH=0 JOBS=5` in a detached worktree at main `14214b115`
(seeds 3000101-3001100, never rolled before), 58 min 17 s wall under `time -v`; tallied by `make fresh-tally COMMIT=14214b115
SINCE=20261025T041035Z` from its record `dev/cohort-log/20261025T041035Z-base417-1251124.json`.

| form (observed 2026-10-25; method: as above) | failed | rolled | rate |
|---|---|---|---|
| all | 125 | 1,000 | 12.5% |
| nucleated | 58 | 524 | 11% |
| dispersed | 10 | 270 | 4% |
| linear | 57 | 206 | 28% |

| cause (observed 2026-10-25; method: as above; a seed may fail more than one) | seeds |
|---|---|
| `refused:WebRefused` | 49 |
| `lane_knots` | 31 |
| `refused:SiteRefused` | 13 |
| `row_rules` | 11 |
| `refused:OverlapRefused` | 8 |
| `refused:SinkRefused` | 7 |
| `groves_crossed_by_lanes` | 4 |
| `farmstead_across_brook` | 2 |
| `refused:BrookRefused`, `refused:NoDryExit` | 1 each |

The lane web (`WebRefused` and `lane_knots`) is in 80 of the 125; seating 13; the row rules 11. The order is the spec's tally's.

## R5 - which of the web's post-lay passes the placers already make needless (T26, D22-D23)

Observed 2026-10-25; method: a detached worktree at `29d29eb1e` with a switch in `ways/web/stage.py` (never landed) that
replaced a named pass with a no-op at every one of `stage_web`'s call sites; for each pass `make cohort N=48 FRESH=0 JOBS=5`
(the 48 fixed seeds and the 6 pinned rows) and `make map` of the five pool hamlets, ~3 min a probe
(`scratchpad/probe_passes.sh`; the logs are the session's, not kept). The baseline, with no pass off, passed 54/54 and
generated all five pool maps.

| pass turned off (observed 2026-10-25; method: as above) | fixed + pinned | pool maps | verdict |
|---|---|---|---|
| `_join_orphan_ways` | 53/54 - Audit-47 `WebRefused` (the field reached by no way) | ok | NEEDED |
| `tidy_lane_ends` | 52/54 - Audit-23, Audit-29 `WebRefused` (dangling ends the last resort cannot mend) | Mizuguchi refused | NEEDED |
| `_sweep_dangling_ends` | 53/54 - Audit-24 `lane_knots` (2) | ok | NEEDED |
| `_sweep_doubled_tails` | 53/54 - Audit-37 `lane_knots` (1) | ok | NEEDED |
| `_bridge_collinear_breaks`, `_touch_junctions`, `_smooth_web`, `_drop_collapsed`, `_sweep_debris`, `_drop_end_nubs`, `_sweep_steading_fouls`, `_sweep_doubled_remnants`, `_keep_the_route_wide`, `straighten_joints`, `fold_the_connector_hairpin`, `center_lane_ends`, `cut_the_overruns`, `cut_past_the_junction`, `split_at_crossings`, `meet_end_to_end`, `trim_streets`, `resettle_straightened` | 54/54 each | ok each | NEEDLESS |
| all eighteen NEEDLESS passes off together | 54/54 | ok | NEEDLESS together |

The eighteen were deleted in one landing (D23) with every definition only they reached - `make dead-closure`'s
`--fixpoint`, 87 names across `bund`, `clearance`, `geom`, `joints`, `smooth`, `street`, `sweeps`, `touch` (now empty,
deleted) and `web/tidy`, 2,822 engine lines out and 67 in - and the tests that exercised only those (`test_touch.py` and
`test_smooth.py` emptied and deleted; 1,966 test lines out). Two tests that asked the deleted copy of the bend rule (`clearance._bends_badly`)
now ask the lane law's (`law.bends_badly`, the same `kink_spans`). On the regenerated pool, Inashiro, Kashikawa and
Mizuguchi each moved two lanes, Sawada's lanes held (its manifest's settle record moved) and Kuwabata did not change; no house
moved. A lane's `role` names the pass that last inked it, so the trim is now named (`_pass("tidy")`): the lanes it re-inks said
`touch` before, after the pass that went.

What it does not show: 54 seeds are the plan's definition of NEEDLESS, and several of these passes were written for one
map (Mizuguchi, Kashikawa, Sawada, cohort seeds 37, 39, 48). The fresh block after the landing is the rate that says whether
any of the eighteen mattered on seeds the fixed set does not hold; it is recorded beside R3 below once rolled. The four
NEEDED passes are set down untouched for T06 and the GM's fixing pass (Approach item 6), with the seeds above.

### R5's fresh block - 500 fresh seeds at the landing (beside R3)

Observed 2026-10-25; method: `make cohort N=500 SEED=3001101 FRESH=0 JOBS=5` in a detached worktree at main `3d01065b3`
(T26 landed; seeds 3001101-3001600, never rolled before), 19 min 8 s wall under `time -v`; tallied by `make fresh-tally
COMMIT=3d01065b3 SINCE=20261025T084714Z` from its record `dev/cohort-log/20261025T084714Z-fresh417-2900116.json`. The
landing's own fresh block of 48 passed (`dev/cohort-log/20261025T082938Z-diagram-backlog-2896409.json`).

| form (observed 2026-10-25; method: as above) | failed | rolled | rate | R3 at `14214b115` |
|---|---|---|---|---|
| all | 59 | 500 | 12% (11.8%) | 12.5% |
| nucleated | 22 | 226 | 10% | 11% |
| dispersed | 4 | 170 | 2% | 4% |
| linear | 33 | 104 | 32% | 28% |

| cause (observed 2026-10-25; method: as above; a seed may fail more than one) | seeds | per 1,000 | R3 per 1,000 |
|---|---|---|---|
| `refused:WebRefused` | 20 | 40 | 49 |
| `lane_knots` | 14 | 28 | 31 |
| `refused:SiteRefused` | 11 | 22 | 13 |
| `row_rules` | 7 | 14 | 11 |
| `refused:OverlapRefused` | 3 | 6 | 8 |
| `farmstead_across_brook` | 2 | 4 | 2 |
| `groves_crossed_by_lanes`, `refused:NoDryExit` | 1 each | 2 each | 4, 1 |

Read: deleting the eighteen passes moved no rate past its sampling noise (500 seeds at 11.8% (observed 2026-10-25; method: the block above) carry about +/-3 points at two
standard errors; every form and cause is inside it). The lane web's causes are not higher; linear (104 seeds) and seating
are the noisiest cells. The rate is the same problem it was, with 2,822 fewer engine lines in it.

## R6 - the track out's pull-back, measured off (T19, D25-D27)

Observed 2026-10-25; method: D25, in the detached worktree `probe19` at `a81dd7ee9`, with an environment switch and a log
that never land: `make cohort N=48 FRESH=0 JOBS=5` and `make map` on the five pool hamlets with the call on, then off; then
`make cohort N=500 SEED=3001601 FRESH=0 JOBS=5` with it on, logging every connector end the pull-back returns and every
connector end once `settle_the_web` is done; then the six seeds whose finished track ended off the web, one by one, with each
settle step's effect on the track's end logged.

| what (observed 2026-10-25; method: as above) | result |
|---|---|
| fixed and pinned seeds, call off against on | 54 of 54 pass both ways |
| pool manifests, call off against on | all five byte-identical |
| connectors the pull-back returned more than 4 ft off the web | 0 of 412 (58 fixed, pinned and pool; 354 fresh) |
| finished maps with the track's inner end more than 4 ft off the web | fixed, pinned and pool 0; fresh 6 of 377, at 25.2-65.8 ft |
| those six seeds' cohort verdicts | all pass (the law exempts the connector) |
| where the trace puts it | `settle_reach`, every one: the households' ways are drawn to `near_the_cluster`'s stretch of the track, not its start |
| the fresh block's rate (`make fresh-tally COMMIT=a81dd7ee9 SINCE=20261025T114923Z`) | 61 of 500 (12%): nucleated 10%, dispersed 4%, linear 30% - beside R3's 12.5% and R5's 11.8% |

The six (seeds 3001615, 3001629, 3001674, 3001847, 3002028, 3002062) are all nucleated with a way out's gate. At the first landing the finished-map check, asked of every end inside the manifest's `W` x `H`, named 18 of the 54
landing seeds' way-out ends (the frame is cropped about the content); read by distance it named all 13 dispersed seeds,
whose track ends among the farms with no web to meet (seed 5: 154 ft from the nearest house center) - so it asks only a map
with a web, and the dispersed track's end goes to the GM (D28). So read, the landing cohort is 54 of 54. The pull-back
is deleted as needless; the rule becomes a finished-map predicate the cohort asks (D27 (a)), and its placer is T27.

## R7 - the angle at which two ways stop reading as a junction (T16's research pass, the GM 2026-10-25)

The GM: "a general research pass on the angles at which footpaths and lanes and country roads tend to intersect. We
basically want something that doesn't look wrong, visually, to a person looking at the map." Run 2026-10-25 by the
`research-pass` agent (archive first, then the web; every page read is on `research/source-attempts.jsonl`). The question:
below what angle does a lane end meeting another way read as one way drawn double rather than a junction, and at what
angles do real paths, lanes and roads meet. The three values in the code: the law's 15 deg (`tails._DOUBLED_DEG`), the
sweep's 25 deg (`tails._ALONG_DEG`), the page's 20 (0081, "Two paths running side by side are drawn as one").

**SILENT on the threshold.** No source gives an angle below which a meeting stops reading as a junction. What bears:

| source | what it says | reading |
|---|---|---|
| 說文, quoted in 齊民要術 卷第一 (c. 544) | "田 ... 象四口，十，阡陌之制也" - the 十 is the system of field paths (translation) | ATTESTED ONLY FOR planned field paths crossing square |
| 条里制 (suido-ishizue.jp) | the jōri grid of 1-chō squares, its axes on the main slope "とその直交方向" (and at right angles to it) | ATTESTED ONLY FOR planned paddy grids, 90 deg |
| Helbing, Keltsch and Molnár, Nature 1997 (arXiv cond-mat/9805158) | "junctions of two trails which smoothly merge into one trail"; trails "begin to bundle, especially where different trails meet" | ATTESTED: trodden footpaths make shallow, smooth Y-merges, and near-parallel trails bundle into one (0081's own reason); no angle |
| Iowa DOT 6A-8, citing the AASHTO Green Book ch. 9 and NCHRP 279 | "intersection angles between 60º and 120º as acceptable"; "75º to 90º ... wherever possible" | ATTESTED ONLY FOR modern vehicle roads (a sight-line floor, not a footpath's) |
| Azumino city road standard | 「道路の交差角は原則として４５度以上」 (crossing angle as a rule 45 deg or more) | ATTESTED ONLY FOR modern municipal roads |
| Crucitti, Porta, Strano et al. (arXiv 1211.0259) | junction angles "a double peak ... around ... 90 and 180 degrees" | ATTESTED: 90 (a crossing) and 180 (straight on) dominate; no shallowest angle readable |
| CartAGen `strokes_roads`; Esri "Merge Divided Roads" | a fork within 45 deg of straight carries the same stroke; near-parallel roads within a merge distance are drawn as one | ATTESTED ONLY FOR the convention that near-parallel lines are drawn as one; distance, not angle |

**What it means for the rule.** The road floors (45-75 deg) are sight lines for drivers and do not apply to a footpath,
and Helbing shows the shallow merge is a real trodden form - so the evidence argues against raising the cut to 25 deg,
which would read more real Y-merges as doubled, and for keeping it low (15-20). Whether two lines read as doubled depends
on how fast they part relative to their width as well as on the angle: a lane leaving another at an angle gains one lane
width of separation every 1/sin of it, about 3.9 widths of run at 15 deg, 2.9 at 20, 2.4 at 25 (the project's arithmetic,
not sourced). Labels: the 15/20/25 choice stays a **map drawing convention**, as 0081 already labels its 20; "field paths in
a planned grid cross square" can carry **historically accurate** (說文 via 齊民要術, 条里); anything about how unplanned
village lanes meet stays a **guess**.

Not followed (print only or unreachable): 道路構造令の解説と運用's 平面交差 chapter, the DMRB CD 123 full text (a WSP note
quotes its criterion as ">70 degrees"), Thomson and Richardson's original stroke threshold, Helbing's Phys. Rev. E paper,
USFS / NPS trail junction guidance, arXiv 2511.06747. T16's doubled tail is still set down: the pass supports the page's
20 as a convention and gives no reason for 25; which value the two roles (`_ALONG_DEG`, `_DOUBLED_DEG`) share is the GM's.
