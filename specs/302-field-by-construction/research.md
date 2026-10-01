# Research - feature 302, the comb field built by construction

## R1. Where the current field's time goes (observed 2026-10-01, method: `harness.py` `timed_fit`, fastest of three, load ~7)

`fit_field` on the captured arguments of each recorded input, every carve and finish step timed inclusively:

| input | fit s | close_seams | planted_area | _carve | dry & beans | trial carves | plots |
|---|---|---|---|---|---|---|---|
| inashiro | 1.047 | 0.496 | 0.190 | 0.164 | 0.123 | 3 | 600 |
| kashikawa | 1.104 | 0.688 | 0.167 | 0.141 | 0.035 | 3 | 775 |
| mizuguchi | 0.573 | 0.344 | 0.062 | 0.047 | 0.094 | 2 | 436 |
| sawada | 2.392 | 1.666 | 0.307 | 0.265 | 0.046 | 3 | 1052 |
| inashiro at 10 households | 0.817 | 0.407 | 0.145 | 0.112 | 0.093 | 4 | 379 |
| inashiro at 20 households | 1.264 | 0.556 | 0.227 | 0.194 | 0.197 | 3 | 793 |

The skeleton (`_comb_skeleton`, `_comb_threads`, `_comb_march`, `_comb_drain`, `_comb_canal_pieces`, `round_channel_joints`)
is under 0.04 s on every input (observed 2026-10-01, method: the same `timed_fit` run). The seam repair and the prediction - what the redesign removes - are 64-82% of the fit.

## R2. The Phase 0 verdict: GO (observed 2026-10-01, method: `make spec-harness SPEC=specs/302-field-by-construction`, three interleaved runs per input, load 1.7-2.1; the raw figures are `phase0-verdict.json`)

| input | current fit s | prototype s | ratio | plots (current -> prototype) | bare scraps |
|---|---|---|---|---|---|
| inashiro | 1.035 | 0.412 | 2.51 | 600 -> 599 | 1 |
| kashikawa | 1.169 | 0.396 | 2.95 | 775 -> 712 | 0 |
| mizuguchi | 0.628 | 0.334 | 1.88 | 436 -> 473 | 1 |
| sawada | 1.858 | 0.565 | 3.29 | 1052 -> 937 | 2 |
| inashiro at 10 households | 0.649 | 0.216 | 3.00 | 379 -> 265 | 0 |
| inashiro at 20 households | 1.219 | 0.491 | 2.48 | 793 -> 608 | 0 |
| **total** | **6.558** | **2.414** | **2.72** | | |

SC-001 (observed 2026-10-01, method: the verdict run above): the current total less the prototype's is 4.14 s against a spread of 0.05 s (the larger method's), so **GO**.
SC-002 (reported, not a condition): 3.00x at 10 households, 2.48x at 20. The ratio falls with size because the dry hem and the
beans, which both methods run unchanged, grow with the fan (0.07 s at 10, 0.18 s at 20); the replaced part's own cost grows
less than the field.
SC-003, every input: in its acreage band and `fan_admissible`; no plot with a `ring_violations` finding; bare ground at most
0.36% of the planted region (the bound is 0.5%), all of it scraps left bare as `hold_ring_rules` leaves them; no unshared bund.
SC-004: nothing stubbed. The prototype runs the skeleton, the region, the search scored on acreage and water legality, the
partition, the rules (merge and `_split_steps`), the carve's `low` marking and FLOODED sample and `close_seams`' tint judgment
verbatim, the dry hem and beans, and `fan_admissible` on the built net.

Where the prototype's time goes (observed 2026-10-01, method: the prototype's own phase timers, one harness run, Inashiro): the search 0.07 s for three trial sizes (the current search's carves and
predictions about 0.4 s), the partition 0.04 s, the rules 0.12 s, the tint 0.04 s, the dry hem and beans 0.11 s.

**What the prototype taught, for Phase 1's design** (each a dead end walked, recorded so it is not walked again):

- Rows run past a sector's threads' ends collapse along the drain (`_bnd` clamps both bounds onto it): rows stop being cut
  there; past its own end a thread's bound runs straight down the fall, or the toe's columns converge into the sunburst.
- Sectors must not share ground: each thread (continued straight down the fall past its end, until it meets another thread)
  divides the region into sector pieces, and each sector's grid is clipped to its own pieces. Without it, Sawada's sectors
  crossed and their interleaved rows made 30,000 slivers.
- A bund piece lying wholly within half a row step (rows) or 0.3 plot widths (columns) of its ground's edge is not cut
  (Sawada: rows across a hair-wide strip along the drain, 84-402 slivers); a narrow sector's rows are spaced for it (`stretch`,
  capped at 3) and exempt; the sector's width is its median over its span (one sample at the midpoint read a fallback and
  near-zero). Trimming only the hugging stretch of a piece, trimming the threads themselves, building sector polygons from
  `_bnd`, and skipping the extension of a thread ending near the drain were each tried and each made it worse.
- The grid thins where a sector narrows (columns end in a T on a row as the width halves; rows stop under 0.45 plot widths).
- Rules at construction (observed 2026-10-01, method: the harness runs that led to the verdict): the partition snapped to the recorded 0.1 px grid; each cell judged once; staircases split by
  `_split_steps`; a merge across the longest shared bund, OPENED by 0.3 px so a sliver's hair spike does not ride into its
  neighbor; two failing cells may merge when the union's only fault is size (a cluster grows); what neither fixes is left bare.
- Open for Phase 1 (quality, not cost): a few cells come out larger and longer than the carve's (a narrow sector at 10
  households, an edge strip at 20), and the plot count is 10-30% lower on three inputs; the gate and the paddy glyph check
  judge it there.

## R3. Phase 1 first measurements, and the blocker (observed 2026-10-01, method: `make map PROFILE=1` per pool map, `make cohort N=24` in the clone and in a detached worktree of a94cabe5f)

The engine now builds the comb field as Amendment 1 designs it (partition, settle, tint; the carve's plot cutting, `sector_rows.py`,
`close_seams` and every function only it reached, `PlotGeoms`, `planted_area` deleted). The touched suites pass (3,213 tests); the
three new modules are at 100% coverage from their own tests.

The field stage, one run each (base figures: the 2026-10-01 morning profile): Inashiro 1.23-1.51 -> 0.60 s; Mizuguchi 0.87 -> 0.49 s;
Sawada 2.05 -> 0.81 s; Kuwabata (a polder, not a comb) 0.70 -> 0.67 s.

**Kashikawa no longer generates**: the web refuses it, one row farm (at 2473, 2937) off the network. Traced: its row's street is
planned past it, but its door path is refused - a farm fixture stands on the straight step from its door to the street, and every
routed path round it fails the lane law (`lawful`) - so `trim_streets` cuts the street back to its last joint and the farm is
stranded. Nothing of the field stands near it; the field moved the canvas and the row's frame, and the row-village lane code fails
on the layout it now gets.

**The failure class is pre-existing on main.** The cohort (24 seeds and the six named ones, 30 maps) at the feature's base: 23/30
pass - WebRefused on Audit-05, -12, -22, -23, -905, NoDryExit on -08, a water rule on -19. With the field by construction: 23/30
pass - WebRefused on Audit-04, -11, -22, -23, -903, NoDryExit on -16, the same water rule on -19. The rate is unchanged; which
seeds fail moves with the geometry. Feature 297 recorded the cohort at 30/30, so the failures arrived with work merged since.

## R4. The engine against main, and the lattice measured against the carve (observed 2026-10-01, method: `make spec-harness` with `HARNESS_WHICH=breakdown` in a detached worktree of main at 86395a70d and in the clone, interleaved three times, load 4.5 -> 2.3; the cell figures from the 10/20-household manifests, the old ones rolled on main the same morning)

`fit_field`, fastest of three per input: main 5.723 s (run totals 5.79 / 5.95 / 5.72), the clone 3.050 s (3.11 / 3.05 / 3.07) - **1.88x**,
the larger spread 0.23 s: SC-005 holds. Per input, main -> clone: Inashiro 0.966 -> 0.472, Kashikawa 1.024 -> 0.499, Mizuguchi
0.540 -> 0.392, Sawada 1.590 -> 0.799, at 10 households 0.565 -> 0.274, at 20 1.038 -> 0.614. Less than the prototype's 2.72x: the
lattice fixes below cut more rows, clip with a buffer, and re-cut oversized cells.

**The cell comparison the plan review asked for (task T13b)** found the first engine cut leaving oversized cells - 19 over three
design cells at 10 households (the carve: 3), 26 at 20 (the carve: 5). Measured causes, each fixed in `partition.py`:

- A bund clipped EXACTLY to its sector's ground ended on the edge only to within floating error, so a row a hair short of the edge
  was a dangle `polygonize` ignores: the edge column's cells were 3-5 basins tall. Clipped to the ground grown by `CROSS` (0.5 px).
- One row spacing and one column count per sector, from its MEDIAN width, misread a sector whose thread rides its parent's path
  for half its span: rows are kept by the cell each closes at the LOCAL width (`_rows_kept`), columns counted at the widest.
- A short row across a ditch-side strip was dropped by the hug test (the sector's width is measured between thread centerlines,
  inside the ditches): a short piece is kept where the strip is at least `MIN_ROW` plot widths across (`keep_rows`).
- A backstop: a cell over `RECUT_OVER` (2.5) design cells is cut again on a plain lattice at the fan's grain (`recut`).

After them, at 10 households: no cell over two design cells (the carve: 13), the largest 2,914 px^2 (5,428), the longest 4.8 to
1 (7.9). At 20: 2 over two design cells (19), the largest 4,610 (5,474), the longest 4.9 to 1 (7.1).

**Kashikawa, fixed** (constitution XIV; the GM, 2026-10-01: "We should definitely fix the pre-existing failure"): the row farm's
boxed-in door (the router's start cell had no free neighbor) was fixed on main by the session diagram-reorg (`serve.route_from_door`,
86395a70d), traced here first. A second failure surfaced after it: every meeting the drain's constructed route could make with the
brook read "ruled" (water:W03), though the brook kept the rule without the join - a confluence held mid-leg adds a collinear vertex,
which turned one straight leg (left alone by the rule's three-vertex chord test) into a counted run. `brook_violations` now judges
the ruled rule on the drawn course less a straight join vertex (`_without_straight_joins`). An alternative-meeting search tried
first was withdrawn: it met the brook on its corners, which `brook_join` refuses (labels L16: a held corner is a mitred bend), and
without the corners found nothing - the rule's measurement, not the meeting, was the defect.
