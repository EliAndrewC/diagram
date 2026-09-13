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

**Machine time was small**: 22 gate runs totalling 1,443 s (24 min), about 70 map regenerations at 6-10 s
each, three perf runs. Roughly 40 minutes of fourteen hours. The rest is model turn latency and waiting on
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

- **The dispatch intercept exists.** `scripts/pair-hooks.sh pretool` already runs on an Agent dispatch of
  `settlement-review` and refuses one with no gate beside it (feature 151); it resolves this session's
  clone and keeps a per-map snapshot under `<clone>/.git/review-snapshot/`. FR-001 and FR-002 add to that
  branch rather than adding a hook.
- **Map currency is already decided.** `pipeline/regen.py` returns CACHED or REGENERATED from the
  generation cache's key; no manifest carries an engine key of its own (checked on
  `pool/hamlets/inashiro/inashiro.json`, no `meta` field names one), so the check asks the cache.
- **The figure detector exists.** `scripts/spec-lint.py` defines `_FIGURE` (a number with a unit from a
  shared unit list) and `_POINTER`; FR-002 imports them rather than restating them.
- **The perf command exists.** `make perf-explain WHY=...` writes a `review-NNN-explanation` record under
  `dev/perf-log/`; FR-010 is a precondition on that command.
- **The measurements format exists** in feature 239's clone as `specs/239-.../measurements.json`, written
  by four harnesses under `measure/`. That session calls it provisional.

## R4 - the quiet threshold FR-009 needs (OWED before implementation)

Not yet measured. The motivating observation is feature 239's: 145 ms and 303 ms for the same command an
hour apart, the second at 152% CPU from another session's map roll. The threshold is measured by sampling
the one-minute load average across a working day on this container and taking the level below which a
fixed reference command's timing is stable; the number and the command that took it land here before the
harness is written.
