# 192 - The gate rolls once

**Status**: draft
**Request**: [request.md](request.md)
**Diagnosis**: `specs/191-refusals-that-tell-the-truth/research.md` R7

## Why

The gate rolls the same eight maps TWICE on a cold roll cache, and the second time costs ~400 s -
about half the gate's wall clock.

`rollcache.obtain()` bypasses SERVING under `L7R_TESTS_FULL=1` (which the gate always sets), because
a served roll executes nothing the coverage floors could see. Correct. But the bypass branch returns
`produce(), "BYPASS"` **without calling `gencache.record(...)`**, so the suite's rolls leave no
dependency record behind. `hamlet_floor` then derives the hamlet path from those records, finds
none, and - by its own documented design, *"Never bypassed"* - rolls all eight subject specs itself.

Measured (191 R7): a 401.6 s gap between the end of pytest and `hamlet-floor`'s first line, on a
cold cache; ~1 s warm. The `[HIT]`/`[MISS]` flag printed on every gate's reference line predicts it,
3 for 3.

## Requirements

- **FR-001** A bypassed roll RECORDS its dependencies. The suite's own rolls leave records the floor
  can read, so the floor does not re-roll what the suite just rolled.
- **FR-002** Nothing about SERVING changes. The bypass still PRODUCES on every call, so every line
  the coverage floors judge is still executed. This feature must not make a served roll possible
  where one is not possible today.
- **FR-003** The recorded deps are written where they CANNOT cause a stale payload to be served -
  see D1. The serve path is untouched.
- **FR-004** Recording is confined to the subjects the floor actually consumes (`report:` rolls),
  not every bypassed roll.
- **FR-005** `report_deps` consults the new record before rolling.
- **FR-006** The `done` ratchet baseline is re-pinned to the measured WARM cost, with a written
  reason resting on 191 R7 (the GM's authorization covers this explicitly).

## Decisions Recorded

- **D1 - the deps go in their OWN file (`deps.json`), NOT in `meta.json`. This is a correctness
  decision, not tidiness.** The obvious implementation - have the bypass write `meta.json` the way
  the MISS path does, minus the payload - introduces a way to SERVE STALE BYTES, and it was caught
  while designing rather than in production:
  1. a normal run rolls, writing `meta.json` (key K1) and `payload.pickle` (K1's bytes);
  2. engine code changes, so the key becomes K2;
  3. a FULL run bypasses, rolls, and writes `meta.json` with key K2 - the OLD payload is still on disk;
  4. a later normal run reads `meta.json`, finds K2 matching the current engine, opens
     `payload.pickle`, and serves **K1's bytes as if they were K2's**.
  A separate `deps.json` that only `report_deps` reads cannot do this: the serve path still requires
  a `meta.json`/`payload.pickle` pair written together, exactly as today.
- **D2 - overhead was MEASURED before the design was chosen, not assumed.** One Inashiro roll:
  23.75 s plain, 23.60 s under `gencache.record` (0.99x - within noise, 803 dep entries captured).
  Recording is free, so there is no trade-off to price and no reason to confine it further than
  FR-004 already does.
- **D3 - `report:` only.** `hamlet_floor` consumes `report:` rolls. `hamlet:` rolls are the shared
  fixture path (feature 147) and `test:` rolls are monkeypatched; neither feeds the floor, and
  recording them would buy nothing.

## Out of scope

- The ratchet's population mixing (a median over warm and cold runs describes neither). Recorded in
  191 R7 as a separate decision; FR-006 re-pins the baseline, it does not redesign the comparison.
- The self-sustaining run-log behavior (a run that FAILS the ratchet is still logged `green`, so it
  feeds the median that failed it). Deliberate per the Makefile's own comment; noted, not changed.

## Success Criteria

- **SC-001** After a cold-cache `make done`, `hamlet_floor` finds records and does not roll: the
  post-pytest gap falls from ~400 s to seconds, measured on an instrumented run.
- **SC-002** No roll is ever SERVED under `L7R_TESTS_FULL=1`. Asserted.
- **SC-003** The stale-payload sequence in D1 cannot occur: a `deps.json` written by a bypassed roll
  does not make `obtain` serve anything. Proven by constructing that exact state in a test.
- **SC-004** `make done` green, 100% coverage held.

## Review history

(pending `spec-fidelity`)
