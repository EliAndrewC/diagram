# 443-work-budget-tooling - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-28 -->
### T01 (the design's section 1: counted work that survives a port; FR-001, FR-002)

- **Approach**: `work_counts.py` (a `defaultdict(int)`, its `__missing__` in C), the one-line `if __debug__:` increments of D1-D2's shared sites and `driver._run_stages`' per-stage copy (D3). Measured: `make perf-fanout SEED=25` total calls before and after (SC-001: within one call in a thousand), `make perf-ab A=<443-start commit>` quick form for the overhead, `make counters-inert`'s two rolls compared by hand until T02 builds it.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T01 Approach (checklist part A)

1. **The goal, in the world.** every basic operation the shared geometry and the registry do is counted, by stage, by kind and by function, and a run under `-O` counts nothing.
2. **The constraints.** FR-001, FR-002; D1-D3; no Python call added (the push's call guard, feature 427 T03).
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`); O: the 443-start bookend and the loop survey (`dev/perf-log/20261028T044837Z-443-start-diagram-backlog.json`, `20261028T045040Z-fanout-443-loops.txt`).
4. **Do they describe the world here?** the counts are read on the reference roll against a hand count of one primitive's calls from the profile (`make perf-profile`).
5. **The order.** first of the feature; before T09-T12, whose increments use its module.
6. **The exits.** Green: the calls unmoved, a manifest identical with and without `-O`, the counts printed per stage. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `make perf-fanout` before and after, the A/B recorded in `research/overhead.md`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

