# Feature 240 - research

## R1 - where feature 230's fourteen hours went

Measured from the clone's commit timestamps, the gate run log and the review agents' own reported
durations, not recalled. Span: claim at 09-12 13:27, landed at 09-13 03:45 - **14 h 18 m**, 92 commits.

| phase | span | content |
|---|---|---|
| the ask itself | 13:27-15:21, ~1 h 55 m | spec and five spec-fidelity rounds, the research pass, the two classes, the intake knob |
| review rounds 1-6 | 15:21-19:24, ~4 h | real errors each round; the 48-seed cohort regression; the 1,000-line split |
| rounds 7-10 and the record passes | 21:16-23:33, ~2 h 20 m | the confluence, the drain hue, the undrawn connector; quote-check, record-format, source-applicability |
| round 11 | 23:48-00:39, ~50 m | the vanished field spur, the necks, the lane ends |
| round 12, five agents | 00:54-02:04, ~1 h 10 m | nine errors |
| rounds 13 and 14 | 02:24-02:56, ~32 m | the canopy proxy, the caption halo |
| perf and landing | 03:09-03:45, ~36 m | bookends, two audits, the sign-off, the push |

**Machine time was small**: feature 230's own gates actually ran 26 times (short-circuits excluded) for
1,663 s, about 28 minutes; its four green ones took 56 to 67 s each and the longest of any result 381 s (`m:230-gates-that-ran`,
`m:230-gate-total-s`, `m:230-green-gate-min-s`, `m:230-green-gate-max-s`, `m:230-gate-max-s` in
`measurements.json`, all from `python3 specs/240-verified-before-reviewed/measure/gate_durations.py`). Add
about 70 map regenerations at 6-10 s each and three perf runs: roughly an hour of fourteen. **Two earlier
versions of this paragraph were wrong, in opposite directions.** The first said 22 gates and 1,443 s - the
last 22 lines of a listing, not the span. The second said 36 gates and 2,736 s - the whole span of a run log
that is committed and merged from main, so it held every session's gates; ten were other features'. The
harness now selects each record by its own `commit` against feature 230's commits and the merges into its
clone, and says so in the record's `source`. The rest is model turn latency and waiting on
review agents - 22 dispatches, whose reported durations in the second half of the feature ran 415,728 ms
to 1,525,589 ms (6.9 to 25.4 min) each.

**What changed partway through**: rounds 1-10 mostly found defects that pre-dated the feature (the undrawn
connector, latent since features 145 and 155; the carve's overlapping paddy rings, 20-49 pairs per brook
map). Rounds 12-14 mostly found defects the PREVIOUS round's fix had introduced. That is the part this
feature exists for.

## R2 - the two motivating failures, as measured

**The canopy proxy.** Pass 12 asked for the notice board to keep out of grove canopy. The fix built
`canopy_index` from each grove's `clumps` (bare points) and its one nominal `r` (14.0 ft). Pass 13's agents
measured the drawn crowns (`tree_crowns`, 588 on Sawada) against those bases: a crown's edge stands a
median 16.3 ft and a p90 26.7 ft from its nearest clump base. Consequence: Sawada's board passed the probe
by 0.09 ft while the drawn crown covered its center (-0.91 ft), and 44.4% of Mizuguchi's plank footprint was
canopy pixels. The fix was correct arithmetic over the wrong quantity. A record naming its `source` as
`clumps + r` would have let the reviewer see that in one line.

**The perf attribution.** The first explanation read seed 4's web-stage profile, saw none of the
feature's new passes in the top 25 by cumulative time, and attributed the growth to the map. The
`perf-audit` agent forced `_ends_worth_walking_to` to return True at the same commit: 4.70 s live against
2.56 s forced against a 1.34 s baseline. The rule costs 0.010 s to evaluate; it sits at the bottom of the
per-target loop, so each of its 10 rejections in 17 evaluations paid another Dijkstra on a lattice
growing with the square of the span. The figures in the first explanation were all re-runnable - the
profile file existed - so a rule about recorded figures would NOT have caught it. The defect was the
inference, and only a counterfactual measurement settles an inference.

## R3 - the machinery each requirement builds on (read, not assumed)

- **The dispatch intercept exists, and it counts a review at DISPATCH.** `scripts/pair-hooks.sh pretool`
  already runs on an Agent dispatch of `settlement-review` and refuses one with no gate beside it (feature
  151); it resolves this session's clone and keeps a per-map snapshot under `<clone>/.git/review-snapshot/`.
  Read on 2026-09-13: that same branch writes `review_key` into the pairing file when the dispatch is
  PERMITTED (the `write_pairing ... review_key "$key"` calls, including the `PAIR_OK` escape's), so the pair
  is closed by the dispatch itself and not by anything the review returns. FR-002 moves that to a verdict.
- **Map currency is already decided.** `pipeline/regen.py` returns CACHED or REGENERATED from the
  generation cache's key; no manifest carries an engine key of its own (checked on
  `pool/hamlets/inashiro/inashiro.json`, no `meta` field names one), so the check asks the cache.
- **The figure detector exists.** `scripts/spec-lint.py` defines `_FIGURE` (a number with a unit from a
  shared unit list); FR-006 imports it rather than restating it.
- **The perf command exists.** `make perf-explain WHY=...` writes a `review-NNN-explanation` record under
  `dev/perf-log/`; FR-010 is a precondition on that command.
- **The measurements format exists** in feature 239's clone as `specs/239-.../measurements.json`, written
  by four harnesses under `measure/`. That session calls it provisional.

## R4 - the quiet threshold (RETIRED to feature 239)

This record first marked a quiet-threshold measurement OWED here, for a timing-record requirement of this
feature's own. Spec-fidelity round 1 found that requirement to duplicate feature 239's FR-011c, and it was
handed back to that session, so the threshold's single home is 239 and it is owed there.

**There is no measured evidence of contention behind that rule, and this record no longer claims any.** The
observation first cited here - the same command at 145 ms and then 303 ms an hour apart, the second while
another session rolled a map - was corrected TWICE by the session that supplied it. Its in-process half was
its own harness taking the first digit in argv as the sample size, so a run recorded as covering 560 commands
timed three. Its spawned half, first said to stand as contention, was the same bug: 239's fifth review round
re-ran that three-command sample on a quiet machine and got 317 ms. That session made four wrong attributions
of one measurement before a re-run settled it. 239's FR-011c now keeps the load-average rule as a PRECAUTION
for a shared container, with its threshold a guess that is owed - and this feature cites it only as that.

What survives, and is why FR-009's `quantity` states the sample a figure measured: when a timing moves, the
first thing to check is what the harness actually sampled, and a record that names its sample makes that
check a read rather than an investigation.
