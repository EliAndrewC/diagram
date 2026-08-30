# Implementation Plan: Retire the post-placement check battery into the placer

**Feature**: 163-checks-into-the-placer | **Spec**: [`spec.md`](spec.md) | **Created**: 2026-08-30

## Summary

Two deliverables, in the GM's order. **US1**: a census that establishes BY EXECUTION which of the 152
live gate checks anything the engine can PRODUCE TODAY still makes fail, then deletes the ones nothing
does, with their segments, helpers, tests, fixtures and pins. **US2**: a MEASUREMENT ledger over every
surviving check - what last changes each input, what the placer guarantees, who reads the verdict, what it
is recorded as having caught - stated against the GM's own two readings (a placer bug, or fold it into a
trial-and-error placer) and handed over as the input to the case-by-case discussion they asked for. The
ledger carries evidence, never a verdict. **No placer changes** (FR-010).

## Technical Context

**Language/Version**: Python 3.14 (the container pin)

**Primary Dependencies**: none new. The census reads `check_village.registry` (the derived registry,
feature 109) and drives `check_village.gate`.

**Testing**: pytest with `-n auto`; `make quick` while iterating, one `make done` at the end.

**Project Type**: CLI tooling plus a deletion sweep over an existing package.

**Performance Goals**: none are required of this feature - the spec review removed the gate-cost
requirement as unrequested. `research.md` R1 records the baseline (1.3 s per map) because it was already
measured; the constitution's own perf bookends still apply below, and they are a regression guard, not a
goal.

**Constraints**: FR-008 - every pool render compared byte-for-byte and any diff DIAGNOSED (the map is then
allowed to move, per the GM's standing ruling). FR-010 - no placer touched.

**Single-artifact target** (constitution VI): `pool/hamlets/inashiro/inashiro.gen.py`, the reference
hamlet. Then the tier via `make maps`. Both are tasks (T12, T13). The feature adds no knob, so one
artifact per knob value does not apply.

**Every step is two steps.** T12 is the reference settlement; T13 is the pool. A phase that lists only
the first is not finished being planned.

## Performance bookends (REQUIRED, constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `163-start` | | | | taken on UNMODIFIED code, before the first edit (T01) |
| after | `163-end` | | | | taken before the push (T16) |

`make perf LABEL=163-start` -> work -> `make perf LABEL=163-end` -> `make perf-report AGAINST=163-start`.
This is the constitution's regression bookend, not FR-011 (which the review removed). This feature should
make the generator FASTER - it deletes work from every roll - and feature 129's review path is for
INCREASES, so a decrease needs no `perf-audit`. Any seed that gets SLOWER is diagnosed here in writing with
the number, because a deletion that slows a roll means something was removed that the roll depended on.

## Constitution Check

| principle | status |
|---|---|
| **I, II** | N/A - no UI in this repository |
| **III, IV, VII, VIII, IX** | N/A - this feature generates no pool content and writes no in-world prose |
| **V** | PASS - no SOURCE block is touched |
| **VI (verify before done)** | PASS - `make done` green; `make maps` at T12/T13; FR-008's byte-for-byte render comparison with every diff DIAGNOSED is the map-level proof, and a `settlement-review` is not owed while no manifest moves (the GM's 2026-08-29 ruling: they read the map themselves). If a diff turns out to be real and explained, the map is allowed to move and the review question is revisited then |
| **X (Python discipline, NON-NEGOTIABLE)** | PASS - ruff + pyrefly + pytest + the coverage floors. The census tool is a by-hand diagnostic and joins `tools/check_census.py` in pyproject's coverage exclusion list, stated here so it is a decision rather than an omission. No file grows past ~1,000 lines; the deletion SHRINKS `check_village/`, and a segment file emptied by the sweep is removed with its `__init__.py` star-import line and its `CLAUDE.md` row |
| **XII (historical grounding, NON-NEGOTIABLE)** | N/A for the opening bookend - this feature changes nothing a generator asserts about the world. The CLOSING obligation is inverted and is real: a deleted check may be the only operative statement of a research finding. T09 checks each deletion against `research/` and records where the finding still stands, per the spec's Decisions Recorded note |
| **XIII (no known regressions, NON-NEGOTIABLE)** | PASS - baseline in a detached worktree at T01 (`git worktree add --detach /tmp/base163 HEAD`), never a stash, and each worktree failure checked against the clone before being called pre-existing (the gitignored-artifact trap). Zero new failures at merge |
| **XIV (fix defects where you find them)** | ACKNOWLEDGED - the census reads 152 checks and their placers; anything it finds broken is fixed in this feature, not filed. A found defect that would need a placer change is the one case that collides with FR-010, and it goes to the GM with the ledger rather than being fixed silently |
| **XVI (no unrequested exception)** | `spec.md` went to `spec-fidelity` against the GM's verbatim request before this plan existed. Round 1 returned CHANGES REQUIRED on six points - one of them the FR-006 keep-clause this session had itself flagged as a possible carve-out - and all six were applied. The verdict and the table of changes are in the spec's Review history |
| **XVIII (a guard needs a companion test)** | the census is a diagnostic, not a guard, so it adds no hook. It does add FR-005's self-guard: a test that the census names a check known to fire and goes red if it classifies nothing |

## Phase 0 - what it costs today (DONE)

[`research.md`](research.md): the gate is 1.3 s per map, the battery is ~22,000 lines plus 11 MB of
frozen fixtures against a 38,000-line generator, zero live maps carry a waiver, and a static pre-count
puts the never-fires candidate set between 9 and 57.

## Phase 1 - a census that EXECUTES (US1, FR-001 to FR-005)

The static pre-count in R2 is exactly the method FR-002 forbids: a name in a test file is not evidence
that the test makes the check FAIL. So the census instruments the emitter instead of reading the code.

- **`l7r/diagram/tools/firing_census.py`** (new). `check_village`'s `check()` is the single point where
  every verdict is emitted. Under an environment variable it appends `<name> <verdict> <source>` to a
  journal file - the same shape as `STAGE_PROFILE_ENV` in `hamletgen/driver.py`, which feature 132
  permits because it changes what is PRINTED and never what a map rolls. `tests/hamletgen/test_driver.py`'s
  precedent applies: a test asserts the manifest is identical with it set and unset.
- **Drive it over every source of a verdict**, which is the FR-003 list: the five live pool maps, the
  105 frozen fixtures in `pool/regressions/`, the scripted negative fixtures, and - the one that
  catches inline manifests no glob can see - **the whole test suite**, run once with the journal on.
- **Union the journal.** A check that never appears with a FAIL or WAIVE in any run is a NEVER-FIRES
  candidate. Everything else FIRES, and the ledger names the artifact that made it.
- **`make firing-census`** - a make target because everything in this skill runs through `make` and it is
  enforced (feature 127), NOT because reusable tooling was requested; the review removed FR-012. Where the
  census can extend feature 141's `check_census.py` rather than duplicate it, it does, as an
  implementation choice.
- **Prove the instrument** (FR-005, and `dev/gate.md`'s "before a number decides anything, spend one run
  proving the instrument"): the census must name a check independently known to fire, and a test must go
  red if the journal comes back empty or misses a name a frozen fixture pins.

## Phase 2 - verify the census, then delete (US1, FR-006 to FR-008)

Feature 158's rule licenses an INVESTIGATION here - the census's verdict is a candidate, not a ruling -
and the spec review was explicit that it licenses nothing more. **There are two outcomes and no third.**

- Per candidate: read the placer that produces the feature the check judges, and grep the record
  (`dev/`, `specs/`, commit messages) for what the check has actually caught. Record the finding.
- **Evidence that the CURRENT placer misses it** - a recorded miss, a live map, a scripted negative
  fixture, a waiver - means the census was WRONG. Reclassify the check FIRING and route it to the Phase 3
  ledger. `bridges_span_their_water` is the worked precedent: the mechanical census called it retire, and
  `hamletgen/ways.py` records it catching the scripted placer four separate times.
- **No such evidence** - delete, the way feature 146 established: the segment BODY, not a stubbed call;
  any helper whose chain reaches no other live check; the name's row in
  `tests/fixtures/gate_check_names.json`; its tests; and any frozen fixture whose only purpose was that
  check. A placer that merely DECLINES rather than guarantees is not evidence and does not save a check -
  a runtime net standing behind a possibly-wrong placer is the architecture this feature retires.
- **Frozen-fixture-only evidence is classified apart, and since the GM's 2026-08-30 amendment to FR-003 it
  is NOT a deletion criterion.** A check whose only proof of teeth is a hand-era manifest still fires as far
  as this feature is concerned; it goes to the Phase 3 ledger, not to the deletion. Only a check nothing at
  all makes fail is a candidate, and even that takes the FR-006 read first.
- **There is no pre-approved class deletion, and an earlier draft of this plan had one.** A check's tier
  is established by READING ITS GUARD, not by subtracting lists: the review found `ways_clear_of_castle_moat`
  carries no scale guard at all, and `village_has_no_headman` sits at a scale `roll_village` still serves.
  So every candidate takes the FR-006 read, and a GROUP is formed only out of candidates whose guards have
  each been read and whose tier no live generator reaches - the grouping is a way of PRESENTING a set of
  individually verified verdicts to the GM, never a way of skipping the verification.

## Phase 3 - measure what survives (US2, FR-009)

One row per surviving check, carrying the MEASUREMENT and no verdict: which stage last changes each input
(feature 141's `make check-census` already measures this - reuse it, do not restate it), what the placer
guarantees, who besides the gate reads the verdict, and what the record shows the check has caught.
Against that, state the evidence for each of the GM's own two readings - **a bug in the placement
algorithm** or **fold it into a trial-and-error placer** - and record "neither, because X" where the
measurement shows that. **The ledger does not decide.** The spec review was specific that sorting the
checks into categories before the discussion is deciding, and that this decision is the GM's, case by
case. No change is made in this phase.

## Phase 4 - verification and the report

Reference map, then the pool, then the gate, then the perf bookend, then the GM. The feature is complete
and lands with the ledger delivered and no placer touched.

## Project Structure

```text
specs/163-checks-into-the-placer/
├── gm-request.md        # the GM's words, verbatim, captured before spec.md
├── spec.md
├── research.md          # Phase 0 - the measured baseline
├── plan.md              # this file
├── tasks.md
├── firing-census.md     # Phase 1 output - the per-check firing ledger
├── firing-census.json
└── surviving-checks.md  # Phase 3 output - the measurement ledger handed to the GM

.claude/skills/diagram/
├── l7r/diagram/tools/firing_census.py     # new, by-hand diagnostic
├── l7r/diagram/check_village/             # segments deleted here
├── tests/check_village/, tests/gate/      # their tests deleted here
├── tests/fixtures/gate_check_names.json   # the pin, shrunk
├── pool/regressions/                      # orphaned fixtures deleted here
└── Makefile                               # `firing-census` target
```

**Structure Decision**: the census joins `tools/` beside `check_census.py` (feature 141) and
`perf_review.py` (feature 129) - the established home for a by-hand diagnostic that observes the engine
without being part of it.

## Complexity Tracking

No constitution gate is violated or deferred.
