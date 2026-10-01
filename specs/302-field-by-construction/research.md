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
