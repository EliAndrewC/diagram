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

<!-- plan-archive: archived 2026-10-28 -->
### T09 (the walk of the water and fields stages: plan D2, the round arbiter's ruling on ask:443-plan-round-3)

- **Approach**: for water_frame, field, sink, waterward, pond_stock, pond_bank: the scan's loops in `research/candidate-loops.md` filtered by hand. The scan (`research/candidate_scan.py.txt`, run 2026-10-28) is an `ast` call graph over `hamletgen`, `settlement`, `waterfields`, `sitegen`, `overlap` and `labels`, followed from each stage's function through every resolved call (an import, `self.`, a module attribute, a unique method name); it lists every loop, comprehension and `min`/`max`/`sorted`/`next` in every reached function whose subtree calls a test - directly, or through a helper that itself tests (its `*` mark) - so a loop testing through a helper is listed. What it cannot follow is read by hand: a `getattr` dispatch, a module reached only by name matching, the modules its "not fully walked" list names, a call to a method whose name is not unique (left unresolved by the scan, so read here), and every function passed by reference over candidates - a `key=` to `min`/`max`/`sorted`, a `filter` or `map`, a callback - found in each reached module by `grep -nE "key=|filter\(|map\(|callback|lambda"` and listed beside the scan's own: `water/brook*.py`, `water/polder.py` read by hand (listed from the scan only) - and each loop that tries a site given `if __debug__: OPS["candidate@<function>"] += <n>` (n = 1 per iteration; where the test is a named predicate or a key function, the count goes inside it, keyed with it, with no call; only a bare `sorted`/`min` or an inline lambda over a list takes `len(cands)` before it - `len()` is a C builtin, which raises no `sys.monitoring` PY_START event, so the push's call guard does not see it: measured 2026-10-28 (`make perf-ab A=29253d4c3`, the calls column, seed 25 at 40 households; `research/overhead.md`): the same count in both engines; a loop whose only test is the registry's `admits` or `conflicts` takes no counter of its own, the registry's `candidate@Standing.conflicts` counting it). The filtered list and the excluded loops, with why, are written into the research file's section for the family.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T09 Approach (checklist part A)

1. **The goal, in the world.** every candidate the water and fields stages try is counted, so today's candidates per thing placed is a measured figure.
2. **The constraints.** FR-001; D2 as the arbiter's ruling reads it: the walk is the source, the fanout a cross-check, a stage 'none' only by the walk.
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`); R: `research/candidate-loops.md`; O: the loop survey.
4. **Do they describe the world here?** each family's candidate counts read against its stages' things placed on the reference roll; a stage with calls large against its counts is re-read.
5. **The order.** after T01; the families in any order, each its own landing.
6. **The exits.** Green: every listed loop counted; the Python calls unmoved within SC-001's one call in a thousand (`make perf-fanout`'s Python functions, as `research/overhead.md` reads them); `make perf-fanout`'s anchors for the family's stages read against the list, each anchor the walk missed added and written as a miss; `make cohort-landing` unregressed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; the claims round's triage as a `check-wave`.
9. **Done, measured.** the family's section of `research/candidate-loops.md` complete and its counts printed per stage
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

<!-- plan-archive: archived 2026-10-28 -->
### T10 (the walk of the homesteads family: plan D2, the round arbiter's ruling on ask:443-plan-round-3)

- **Approach**: for seat, homesteads, appurtenances, burial, lane_wells, sties, washing: the scan's loops in `research/candidate-loops.md` filtered by hand. The scan (`research/candidate_scan.py.txt`, run 2026-10-28) is an `ast` call graph over `hamletgen`, `settlement`, `waterfields`, `sitegen`, `overlap` and `labels`, followed from each stage's function through every resolved call (an import, `self.`, a module attribute, a unique method name); it lists every loop, comprehension and `min`/`max`/`sorted`/`next` in every reached function whose subtree calls a test - directly, or through a helper that itself tests (its `*` mark) - so a loop testing through a helper is listed. What it cannot follow is read by hand: a `getattr` dispatch, a module reached only by name matching, the modules its "not fully walked" list names, a call to a method whose name is not unique (left unresolved by the scan, so read here), and every function passed by reference over candidates - a `key=` to `min`/`max`/`sorted`, a `filter` or `map`, a callback - found in each reached module by `grep -nE "key=|filter\(|map\(|callback|lambda"` and listed beside the scan's own: the getattr-dispatched `_seat_region`, `_free_ground`, `_access`, `_site_corridors` and `homesteads/stages.py` read by hand - and each loop that tries a site given `if __debug__: OPS["candidate@<function>"] += <n>` (n = 1 per iteration; where the test is a named predicate or a key function, the count goes inside it, keyed with it, with no call; only a bare `sorted`/`min` or an inline lambda over a list takes `len(cands)` before it - `len()` is a C builtin, which raises no `sys.monitoring` PY_START event, so the push's call guard does not see it: measured 2026-10-28 (`make perf-ab A=29253d4c3`, the calls column, seed 25 at 40 households; `research/overhead.md`): the same count in both engines; a loop whose only test is the registry's `admits` or `conflicts` takes no counter of its own, the registry's `candidate@Standing.conflicts` counting it). The filtered list and the excluded loops, with why, are written into the research file's section for the family.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T10 Approach (checklist part A)

1. **The goal, in the world.** every candidate the homesteads family try is counted, so today's candidates per thing placed is a measured figure.
2. **The constraints.** FR-001; D2 as the arbiter's ruling reads it: the walk is the source, the fanout a cross-check, a stage 'none' only by the walk.
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`); R: `research/candidate-loops.md`; O: the loop survey.
4. **Do they describe the world here?** each family's candidate counts read against its stages' things placed on the reference roll; a stage with calls large against its counts is re-read.
5. **The order.** after T01; the families in any order, each its own landing.
6. **The exits.** Green: every listed loop counted; the Python calls unmoved within SC-001's one call in a thousand (`make perf-fanout`'s Python functions, as `research/overhead.md` reads them); `make perf-fanout`'s anchors for the family's stages read against the list, each anchor the walk missed added and written as a miss; `make cohort-landing` unregressed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; the claims round's triage as a `check-wave`.
9. **Done, measured.** the family's section of `research/candidate-loops.md` complete and its counts printed per stage
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

<!-- plan-archive: archived 2026-10-28 -->
### T11 (the walk of the ways: plan D2, the round arbiter's ruling on ask:443-plan-round-3)

- **Approach**: for track, web, crossings: the scan's loops in `research/candidate-loops.md` filtered by hand. The scan (`research/candidate_scan.py.txt`, run 2026-10-28) is an `ast` call graph over `hamletgen`, `settlement`, `waterfields`, `sitegen`, `overlap` and `labels`, followed from each stage's function through every resolved call (an import, `self.`, a module attribute, a unique method name); it lists every loop, comprehension and `min`/`max`/`sorted`/`next` in every reached function whose subtree calls a test - directly, or through a helper that itself tests (its `*` mark) - so a loop testing through a helper is listed. What it cannot follow is read by hand: a `getattr` dispatch, a module reached only by name matching, the modules its "not fully walked" list names, a call to a method whose name is not unique (left unresolved by the scan, so read here), and every function passed by reference over candidates - a `key=` to `min`/`max`/`sorted`, a `filter` or `map`, a callback - found in each reached module by `grep -nE "key=|filter\(|map\(|callback|lambda"` and listed beside the scan's own: the cross-check's misses (`gap_ways.py` `way_out`, `trace`; `meet.py` `near_misses`, `web_lines`) read and listed as misses of the walk; the scanned `ways/` loops (the scan of 2026-10-28, `research/candidate-loops.md`) sorted into trials and measurements - and each loop that tries a site given `if __debug__: OPS["candidate@<function>"] += <n>` (n = 1 per iteration; where the test is a named predicate or a key function, the count goes inside it, keyed with it, with no call; only a bare `sorted`/`min` or an inline lambda over a list takes `len(cands)` before it - `len()` is a C builtin, which raises no `sys.monitoring` PY_START event, so the push's call guard does not see it: measured 2026-10-28 (`make perf-ab A=29253d4c3`, the calls column, seed 25 at 40 households; `research/overhead.md`): the same count in both engines; a loop whose only test is the registry's `admits` or `conflicts` takes no counter of its own, the registry's `candidate@Standing.conflicts` counting it). The filtered list and the excluded loops, with why, are written into the research file's section for the family.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T11 Approach (checklist part A)

1. **The goal, in the world.** every candidate the ways try is counted, so today's candidates per thing placed is a measured figure.
2. **The constraints.** FR-001; D2 as the arbiter's ruling reads it: the walk is the source, the fanout a cross-check, a stage 'none' only by the walk.
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`); R: `research/candidate-loops.md`; O: the loop survey.
4. **Do they describe the world here?** each family's candidate counts read against its stages' things placed on the reference roll; a stage with calls large against its counts is re-read.
5. **The order.** after T01; the families in any order, each its own landing.
6. **The exits.** Green: every listed loop counted; the Python calls unmoved within SC-001's one call in a thousand (`make perf-fanout`'s Python functions, as `research/overhead.md` reads them); `make perf-fanout`'s anchors for the family's stages read against the list, each anchor the walk missed added and written as a miss; `make cohort-landing` unregressed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; the claims round's triage as a `check-wave`.
9. **Done, measured.** the family's section of `research/candidate-loops.md` complete and its counts printed per stage
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

<!-- plan-archive: archived 2026-10-28 -->
### T12 (the walk of ground cover, the frame, the notice board and the labels: plan D2, the round arbiter's ruling on ask:443-plan-round-3)

- **Approach**: for hinterland, woodland, windbreak, bamboo, frame, notice, labels: the scan's loops in `research/candidate-loops.md` filtered by hand. The scan (`research/candidate_scan.py.txt`, run 2026-10-28) is an `ast` call graph over `hamletgen`, `settlement`, `waterfields`, `sitegen`, `overlap` and `labels`, followed from each stage's function through every resolved call (an import, `self.`, a module attribute, a unique method name); it lists every loop, comprehension and `min`/`max`/`sorted`/`next` in every reached function whose subtree calls a test - directly, or through a helper that itself tests (its `*` mark) - so a loop testing through a helper is listed. What it cannot follow is read by hand: a `getattr` dispatch, a module reached only by name matching, the modules its "not fully walked" list names, a call to a method whose name is not unique (left unresolved by the scan, so read here), and every function passed by reference over candidates - a `key=` to `min`/`max`/`sorted`, a `filter` or `map`, a callback - found in each reached module by `grep -nE "key=|filter\(|map\(|callback|lambda"` and listed beside the scan's own: `hinterland/parcels/*`, `groves.py`, `grove_fill.py`, `labels/*` read by hand - and each loop that tries a site given `if __debug__: OPS["candidate@<function>"] += <n>` (n = 1 per iteration; where the test is a named predicate or a key function, the count goes inside it, keyed with it, with no call; only a bare `sorted`/`min` or an inline lambda over a list takes `len(cands)` before it - `len()` is a C builtin, which raises no `sys.monitoring` PY_START event, so the push's call guard does not see it: measured 2026-10-28 (`make perf-ab A=29253d4c3`, the calls column, seed 25 at 40 households; `research/overhead.md`): the same count in both engines; a loop whose only test is the registry's `admits` or `conflicts` takes no counter of its own, the registry's `candidate@Standing.conflicts` counting it). The filtered list and the excluded loops, with why, are written into the research file's section for the family.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T12 Approach (checklist part A)

1. **The goal, in the world.** every candidate ground cover, the frame, the notice board and the labels try is counted, so today's candidates per thing placed is a measured figure.
2. **The constraints.** FR-001; D2 as the arbiter's ruling reads it: the walk is the source, the fanout a cross-check, a stage 'none' only by the walk.
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`); R: `research/candidate-loops.md`; O: the loop survey.
4. **Do they describe the world here?** each family's candidate counts read against its stages' things placed on the reference roll; a stage with calls large against its counts is re-read.
5. **The order.** after T01; the families in any order, each its own landing.
6. **The exits.** Green: every listed loop counted; the Python calls unmoved within SC-001's one call in a thousand (`make perf-fanout`'s Python functions, as `research/overhead.md` reads them); `make perf-fanout`'s anchors for the family's stages read against the list, each anchor the walk missed added and written as a miss; `make cohort-landing` unregressed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing; the claims round's triage as a `check-wave`.
9. **Done, measured.** the family's section of `research/candidate-loops.md` complete and its counts printed per stage
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

<!-- plan-archive: archived 2026-10-28 -->
### T02 (FR-003, FR-004: today's figures for every stage, and the counters inert)

- **Approach**: `tools/work_budget.py` (D4) and `make counters-inert` (D5); `dev/work-budget.md` generated with today's figures at 10, 20, 40 and 80 households.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T02 Approach (checklist part A)

1. **The goal, in the world.** the distance between today's work and a budget is on record for every stage.
2. **The constraints.** FR-003, FR-004, SC-001, SC-002, SC-004; D4, D5.
3. **Where each comes from.** G: the GM's approval of the design, 2026-10-28 (`request.md`)
4. **Do they describe the world here?** the record's per-stage figures read against `make perf-fanout`'s calls for the same rolls.
5. **The order.** after T01 and T09-T12.
6. **The exits.** Green: `make work-budget` writes the record; `make counters-inert` passes and refuses a stub counter that writes the manifest. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `dev/work-budget.md` committed with every stage at four sizes.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - instrumentation; its overhead is measured (`make perf-ab`), and it moves no map.

