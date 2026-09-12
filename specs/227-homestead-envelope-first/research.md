# Research - 227 the homestead's envelope first, and the page from the code

## R1 - where a placer call's positions come from (2026-09-12, a temporary probe in `_place_bundle_nucleated` and `_slide_nuc`, one roll each)

| | Inashiro spec (seed 4) | Kuwabata spec (seed 21) |
|---|---|---|
| placer calls | 23 | 19 |
| houses seated | 15 | 16 |
| positions in the spiral | 699 | 339 |
| positions sliding toward the paddy | 99 | 110 |
| positions sliding along the neighbors | 32 | 49 |
| rectangles per position | 3.5 | 4.2 |

On the Inashiro roll 8 of 23 calls seated nothing and each walked all 73 offsets with the full battery; the 15
that seated used about 8 positions each. The pre-test (feature 226) asks the SMALLEST house's box; the placer
asks the house, the yard, a kura and a garden on one of four sides as separate rectangles, plus the eave gap,
the wall rule and the sun corridors - so a seat the house fits and the homestead does not costs 73 offsets
before it is refused. The 2 px slides: no recorded reason (commit ed0e884e); the stop is whichever of the rules
fires first and stepping avoided computing the clearance to each.

## R2 - the after (2026-09-12, the pool at the landing; `meta.seat_search`, the manifests)

| per house (pool, the kept roll) | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| households seated (roll attempt) | 15/15 (1) | 20/20 (1) | 16/16 (1) | 12/12 (1) | 19/19 (1) |
| placer calls | 21 | 27 | 25 | 15 | 25 |
| ENVELOPE TESTS per placer call (at most nine) | 2.6 | 4.2 | 5.0 | 3.5 | 3.1 |
| RECTANGLE TESTS per house, every test counted (226: 113-387) | 7 | 11 | 16 | 9 | 8 |
| candidates per house (226: 1.6-7.0) | 1.4 | 1.4 | 1.6 | 1.2 | 1.3 |
| front row seated / rounds behind | 7 / 2 | 9 / 2 | 2 / 5 | 6 / 2 | 7 / 3 |
| nearest house to the field outline, px / within 165 | 44 / 7 | 47 / 12 | 135 / 3 | 37 / 7 | 60 / 6 |
| homestead-to-homestead GAP, median / worst px | 31 / 106 | 8 / 32 | 4 / 19 | 19 / 68 | 20 / 161 |
| drawn aspect (rolled shape, honored?) | 2.49 (crescent, yes) | 2.79 (elongated, no) | 1.86 (round, yes) | 2.31 (round, no) | 1.43 (round, yes) |
| windbreak / copse clumps | 197 / 88 | 240 / 110 | 112 / 56 | 168 / 20 | 249 / 235 |
| gardens split into two beds / garden sides | 2 / {'W': 10, 'S': 2, 'E': 3} | 3 / {'E': 15, 'W': 2, 'S': 3} | 2 / {'W': 6, 'E': 10} | 2 / {'S': 2, 'W': 4, 'E': 6} | 4 / {'E': 9, 'W': 9, 'S': 1} |

Two counters, named apart (the review's nitpick) - and one cost outside both: the front row's ground push asks the
boundary once per front seat at proposal time, before any placer call, and is not in `meta.seat_search`. ENVELOPE
TESTS are the rectangles the placer asks per call (the union, then each configuration's own box and its one computed
move); RECTANGLE TESTS per house count every rectangle any test asked and are the figure to set against 226's
113-387. A placer call is a fixed handful of rectangles against 26 to 60 positions of the full battery before (R1),
and no call walks.

**Is the cluster one settlement? Read the FOOTPRINTS.** The review's second pass measured connected components on a
165 px CENTRE link and read the pool as fragmented. This engine's own rule is that a gap verdict reads footprints
and never centres (`dev/placement.md`, "CENTER vs FOOTPRINT"), and the houses are now separated by exactly the yards
and gardens between them: homestead to homestead the median gap is 4 to 31 px. Kashikawa's is 8 px - the
fabric is continuous. What the centre link was measuring is a rank standing one homestead's depth behind another,
which is what a rank IS.

**The gardens.** Every homestead has one; 13 of 82 split into two beds, in three forms; the sides are
{'W': 31, 'S': 8, 'E': 43} pool-wide against 0 west before the tie-break was made positional (main: 6 west of 82).

**What the reviews changed, in order.** First pass: the reed-marsh toe was not in the boundary and three maps
recorded a structure inside it; the belt's southern sun strip was 22 px against the 39 ft a farmhouse owes the same
bed. Second pass: the notice board's frame test admitted a board 30 px outside the view and Sawada's shipped
undrawn; the anchored board ranked by distance to its anchor alone; the garden's west side had gone to zero; the
ranks compounded a step behind whoever stood in front; the pitch fell into one bucket. Each is fixed at the point of
change. Cohort seed 39 then stranded a farmhouse because the ranks abutted at four pixels and no alley could thread
them - the rank step leaves `MIN_WEB_GAP` now, and the cohort is 48 of 48.

**The bookends** (`make perf LABEL=227-start` in a worktree at origin/main, `227-end` at the landing): total 29.4 ->
22.6 s (-23.1%), every seed faster (4 -12.9%, 25 -45.7%, 39 -18.0%, 47 -8.9%), band 0, nothing owed.

A first `227-end` was taken one commit EARLY and read band 1 on seed 4 (+8.1%, the notice stage +1.1 s). The
explanation written for it credited the board's new frame test - and the `perf-audit` agent refused it as
INCONSISTENT on the ground that the diff between the two bookends is docstrings only: the footprint inset and the
band-then-traffic reordering both land in the commit AFTER the measured end state, so the explanation credited a fix
that postdated its own measurement, and the 1.1 s it described was the per-candidate traffic count that the same
commit removed. Re-taken at the reviewed commit the pair is band 0. The lesson is the agent's: a bookend binds to a
commit, so take the end one AFTER the last change it is meant to measure - and a band explained by a fix that is not
in the measured range is not explained at all.

The gardens BEFORE (the pool at feature 226's landing, the bed forms read from each house's `geom.gardens`: two beds
on opposite walls = flanking, one above the other = stacked, side by side otherwise):

| | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| gardens before (houses / with a garden / one bed / flanking / stacked / side by side) | 15 / 15 / 13 / 0 / 0 / 2 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 11 / 2 / 1 / 2 | 12 / 12 / 10 / 2 / 0 / 0 | 19 / 19 / 18 / 0 / 1 / 0 |

## R3 - what the two "dangling" lane ends are actually near (2026-09-12, every footprint in the committed manifests)

D11 deferred two straggler ends with a stated mechanism - a clip cutting the far end off the network - and the
mechanism was wrong. Measured with the GM's ask to fix it: each end is the HOUSE end of a footpath drawn for one
outlying steading, and the nearest FOOTPRINT to it is that steading's own garden. Distances from the end to the
nearest edge of every recorded footprint, nearest five:

| map, end | 1st | 2nd | 3rd | 4th | 5th |
|---|---|---|---|---|---|
| kashikawa (1829, 3068) | gardens 8 | byres 17 | houses 32 | threshing_yards 37 | commons 39 |
| kuwabata (2179, 423) | gardens 7 | threshing_yards 27 | threshing_yards 44 | houses 47 | houses 55 |
| inashiro (1070, 1231) | byres 8 | village_groves 35 | farm_fixtures 55 | houses 56 | threshing_yards 62 |
| inashiro (1200, 515) | village_groves 24 | bamboo_stands 57 | houses 60 | farm_sheds 66 | gardens 72 |
| inashiro (1293, 660) | commons 29 | dry_plots 43 | village_groves 57 | houses 57 | farm_sheds 66 |

The first two rows are the defect: a tread that stops 7-8 ft from a garden fence, measured 63 and 76 ft to a house
CENTER (a 46x28 ft house puts 27 ft of itself between its center and its front corner), failing a 60 ft bar. The last
three rows are the FIRST FIX, rejected by this same table: reading the footprint at the 60 ft bar passed the two
stragglers and also admitted three Inashiro skeleton arms whose nearest built ground was 56-60 ft away, which is a
tread stopping in open ground. So arrival became its own clause at its own distance (12 ft, derived from the clip's
`WEB_FABRIC_GAP`/`FOOTPATH_FABRIC_GAP` margin plus the 4 ft step `clear_runs` walks in, so a path that genuinely
reaches a boundary cannot record its last point nearer). Under that rule the byre arm (8 ft) is served - a tread worn
to the byre door, which the center reading had been trimming off - and the other two are trimmed, as before.

After the fix, all five shipped hamlets carry no end that reaches nothing, judged by the placer's own predicate; the
48-seed cohort passes 48/48; `make quick` and the gate green.

## R4 - the 51-minute wait, what killed the run, and what the tooling does about it (2026-09-12)

The incident the GM asked about: `make placement-stages`, detached, wrote all fourteen plates and the 136 KB page by
15:16:18 and then produced no further output; the session's waiter - `until grep -qE "^wrote |Error|Traceback"
$S/out.log; do sleep 15; done` - ran until 16:07.

**Killed by what.** The kernel's OOM killer: `/proc/vmstat` reports `oom_kill 36` in this container, and the harness
also reaps background tasks under memory pressure. The page builder is the heaviest non-gate thing in the tree - it
held one deep copy of the part-built settlement per plate until the end of the walk, and the gate's own sampler had
already caught this process at 1.6 GB (feature 208). So a `make` run here does get killed, and a waiter that assumes
otherwise waits forever: the process died between finishing its work and flushing the line the loop was watching for.

**What the tooling does about it.** Two changes, both the GM's own prescription rather than a note to remember:

1. `no-poll-hooks.sh` ADDS the proof-of-life clause to a permitted file-watching wait that has none
   (`_hm_shape.py proof` -> `_writer-alive.sh <the file the loop watches>`), in the same rewrite that backgrounds a
   foreground one. The helper asks the kernel's open-file table (`fuser`) and the file's mtime, never a process
   pattern - a literal `pgrep -f` pattern matches the searching shell itself, which is the 2026-07-25 fault this
   guard's other half exists for. Three answers, and only one is death: not created yet (the producer is starting),
   held open by something (a detached `cmd > log` holds that descriptor for its whole run, which is how every
   detached run here is written), or written within the staleness window.
2. The same guard stops REFUSING the correct shape. A liveness clause had to be one of the three permitted file
   forms, so `until grep -q "^EXIT=" $S/maps.log || ! pgrep -f "ma[p]s227b" >/dev/null; do sleep 15; done` was
   blocked as a busy-wait - measured on this feature, on the exact shape the fix above produces. A liveness part can
   only make a loop end sooner, so admitting one is not the "permit whenever backgrounded" bypass the GM declined in
   feature 165; a condition must still read a real file, and the `>/dev/null` forgiveness is per PART, so
   `until grep -q x /tmp/a.log >/dev/null` is refused today exactly as it was.

And the page builder no longer holds its copies: the copy is taken inside the plate worker, so the peak is the pool's
width rather than the number of plates - which is what makes FR-007's sixty-odd plates affordable at all.

## R5 - what the per-step plates cost (2026-09-12, `make placement-stages`, Inashiro seed 4)

| | before (stages only) | after (stages + steps) |
|---|---|---|
| plates | 14 | 37 (14 stage + 23 step) |
| directory | 3.5 MB | 6.0 MB |
| page | 136 KB | 140 KB |
| wall clock | 45 s | 38 s |

The build did not get slower while more than doubling its plates, because the same feature moved the deep copy INTO
the plate worker: the walk used to hold one copy of the part-built settlement per plate until it ended (the shape that
took this process to 1.6 GB, feature 208, and that the OOM killer ended in R4), and now at most four are alive. A step
plate is rendered at 1500 px against a stage plate's 2600 and shown at half the width: it answers "what appeared",
not "read the map".

Which steps get a plate is decided in the order the INK LANDED, not the order the steps are declared - a step that
contains others finishes after them, so the declared order plated `draw_comb_field` and then skipped all five of its
parts as "no new ink", which is the opposite of the progression the GM asked for. The field stage now shows the hem,
the paddies, the source and the ditches in turn.

ONE step plate of the 38 cannot be made: `_comb_draw_beads` draws into what the step before it left, so the prefix at
its watermark is not a document resvg will read (`expected 'svg' tag, not 'g'`, after the group-balancing pass, which
fixes every other such prefix). The page says that in words where the plate would be, so "no plate" keeps meaning
"this step drew nothing"; a STAGE plate that will not render still fails the run, because that is a moment the engine
really passes through.
