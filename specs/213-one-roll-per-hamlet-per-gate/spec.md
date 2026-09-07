# Feature 213 - one roll per hamlet per gate

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim, including the six changes they approved.
**Research**: [`research.md`](research.md) - the census (37 rolls of 14 specs), the 5.5 GiB breakdown, the
designs.
**Predecessors**: 210 (the roll leaves the worker; its FR-004 roll-out list); 208 (the raster is a render);
147/192 (the run-scoped share and the `report:` subject); the packing record of 2026-08-31 (`dev/loop.md`);
207 (another session's incremental gate - the answer to item 5, not rebuilt here).

## Summary

The GM: *"nail down the number of hamlets which are being rolled"* - 37 real rolls of 14 distinct specs
per gate against a recorded floor of 8-9 - and *"program our unit tests to never allow the same hamlet
to be rolled twice within the tests and also to have some required process around adding another hamlet
that gets rolled"*, plus the six changes they approved verbatim. This feature makes the gate roll each
hamlet ONCE, gates that it stays so, and takes the six changes start to finish: no test renders a map
unless it tests rendering; every gate roll runs in a child; the pool sweep's child is profiled; the worker
count is measured; the long rolls start first and their concurrency is capped; item 5 is left to 207.

## Functional requirements

- **FR-001 One roll per spec.** One child roll produces everything any test needs of a spec - the plan,
  the finished manifest of the roll `generate` kept, and the `Report` - under one cache subject;
  `rollcache.hamlet()` and `rollcache.report()` read their part of it. `Report` gains the manifest it was
  judged on. The cohort seeds are no longer rolled twice.
- **FR-002 The first wave waits.** The run-scoped share takes a per-subject lock: the first worker rolls,
  a worker that finds the lock held waits (bounded) for the payload rather than rolling its own; a holder
  that dies without a payload lets the next waiter roll. Inashiro, Kuwabata and the polder are rolled once
  per run whatever the workers' start order.
- **FR-003 The census is the gate.** A pytest plugin loaded by the gate's test phase records every roll
  REQUEST (spec, mechanism, requesting test, attempts, seconds; and every `render_png` / `raster.picture`
  call) per worker; after pytest the Makefile aggregates and FAILS the gate on: a spec requested more
  than once in one run; a spec absent from the roster; on a full run, a roster entry no test requested; a
  render from a test that did not opt out (FR-006). Re-roll attempts inside one `generate` are one
  request, reported with their count. The verdict names the tests involved.
- **FR-004 The roster is the required process.** `tests/rolls.py` lists each spec allowed to roll at the
  gate with its reason and the unique coverage or emergent condition it carries, seeded from the packing
  record and the census. A test that rolls a spec not in the roster fails the gate with the instruction to
  add the entry with its reason; a test that rolls a rostered spec through anything but the roll cache
  fails the same way. The roster's size is the recorded roll count; `make audit` prints it.
- **FR-005 First-attempt seeds.** Where a test does not exist to exercise the re-roll loop and its seed
  needs more than one attempt, the seed moves to one that finishes first (the CLI test's seed 8). The
  cohort seeds 41-44 are the ratchet's pinned range and stay, their attempts reported. The two re-roll
  tests keep theirs.
- **FR-006 Tests do not render.** `DIAGRAM_SKIP_RENDER=1` is the suite's default; a test OF rendering opts
  out explicitly. Enforced by FR-003's render records, not by a list.
- **FR-007 The child roll-out, finished.** Every roll the gate makes runs in a child: `report()` and
  `report_deps()` (FR-001), the five direct-`build` produce closures (lifted to module-level functions the
  child runs by name), the immune test (the child applies the perturbation when told), the CLI test, the
  serial half of the fan-out test, and the regen site (`run_and_record` in a child - `gate_obtain`'s
  driver without coverage). Stated exceptions with reasons: `gate_obtain` (already a child); the
  perf-snapshot and perf-profile tests (they time the stages where they run); the fan-out test's parallel
  half (it IS the pool-child path under test).
- **FR-008 The pool sweep's child, profiled.** One `gate_obtain` child under the per-stage instrument;
  the cause of 550 MB against 121 named; acted on if the fix is simple, recorded with a sketch if not.
- **FR-009 The worker count, measured.** 4, 6 and 8 workers on identical content: gate time and container
  peak recorded; the default becomes the smallest count within 10% of the fastest, stated with the numbers.
- **FR-010 Ordering and the cap.** The roster's rolling tests are collected first so the long rolls start
  at t=0; a slot semaphore in the run share bounds concurrent child rolls, its count measured against the
  gate's time.
- **FR-011 Item 5 is 207's.** Nothing built for it here; FR-003's stale-roster check applies only to a
  full run so 207's incremental runs pass it.
- **FR-012 Measured before and after.** Rolls per gate (37 / 14 distinct before), gate time, container
  peak, worker peaks; research R4.
- **FR-013 Tests and the record.** Each mechanism proved to fire: the lock (two producers, one roll), the
  duplicate refusal, the unrostered refusal, the stale-roster refusal, the render refusal, the child
  equality for each lifted closure; 100% coverage over the plugin and the roll cache. The why at each point
  of change; `tests/CLAUDE.md`, `pipeline/CLAUDE.md`, `dev/loop.md`'s packing section and
  `dev/performance.md` extended; the root `CLAUDE.md` gains the roster rule.

## Success criteria

- **SC-001** A full gate rolls each roster spec exactly once; the census verdict says so, and the count
  equals the roster's size.
- **SC-002** Each refusal shown once (a duplicate, an unrostered spec, a stale entry, a stray render).
- **SC-003** `make done` green; the after numbers in R4.

## Decisions Recorded

- **D1 - the roster lives in `tests/`**, beside the tests it governs, as Python (typed entries, no parser).
- **D2 - a lock, not a queue.** The first wave waits on the roll in flight; nothing schedules rolls
  centrally. The cap (FR-010) is a semaphore in the same share directory.
- **D3 - cohort seeds stay** despite seed 42's three attempts: the ratchet pins them.
- **D4 - the census counts REQUESTS**, so a `generate` that re-rolls is one roll with N attempts - the
  generator's behavior is reported, not forbidden.
