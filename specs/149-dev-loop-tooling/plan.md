# Implementation Plan: Dev-loop tooling - the probe, the audit, the profile, and the paired gate

**Feature**: 149-dev-loop-tooling | **Spec**: [spec.md](spec.md) (FAITHFUL, round 2) | **Date**: 2026-08-29

## Summary

Four additions to the dev loop, each removing a measured cost from feature 150's T55 (79.8 min, 19 map
rolls, 42 throwaway measurement scripts, a 17-minute review on the critical path):

1. `make polder-probe` - the polder block alone, with its geometry metrics, in ~1 s instead of a 47 s roll.
2. `make overlap-audit` - the "does A overlap B" question as a tool, over records AND drawn ink.
3. `make map ... PROFILE=1` - per-stage timings, so a slow stage is found in one roll.
4. `make verify` + a pairing guard - the gate and the settlement-review start together, and neither runs
   alone without one override token that logs its reason.

## Technical Context

**Language**: Python 3.14 (engine + tools), bash (guards)
**Dependencies**: none new - the probe reuses `waterfields.build_polder` / `clean_polder_parcels` and
`hamletgen.fit_polder`; the audit reads a manifest and the rendered SVG with the stdlib
**Testing**: pytest under the quick and gate suites; every guard gets a `scripts/test-*.sh` companion run
by `make hooks-test` (constitution XVIII)
**Target**: the `/diagram` skill's dev loop, in a session clone
**Constraints**: everything through `make` (feature 127); no map's drawn output may change; the profile flag
must leave the roll byte-identical when absent
**Scale**: one clone, one session; the probe runs over 1-N seeds, the audit over one map

## Performance bookends (constitution VI)

This feature does not change any generator's behavior, so the bookends are equality rather than a band:

- **Before/after**: roll the reference hamlet and Kuwabata with the flag ABSENT; both manifests must be
  byte-identical to the pre-feature roll. That is the whole perf obligation for items 1-3: the probe and
  the audit are separate entry points, and `PROFILE` adds a timer only when it is set.
- **The probe's own bar** (SC-001): report its wall time; it must land at about a second and at most three.
- No perf-snapshot band is expected. If one appears, the profile timer is running when it should not be,
  which is itself the bug to fix.

## Constitution Check

- **I, II**: not applicable in this repository.
- **III. Pool Data Conventions**: no pool artifact is added or regenerated. The audit READS pool maps.
- **IV. One Canonical Home**: no GM source touched.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: no SOURCE block is edited.
- **VI. Verify Before Reporting Done**: the quick suite while iterating, then the gate once; the guards
  additionally run under make hooks-test. The probe and the audit are demonstrated against the shipped
  maps (SC-002).
- **VII, VIII, IX**: no generated content, no in-world voice, no setting claim.
- **X. Python Discipline (NON-NEGOTIABLE)**: ruff + pyrefly + tests; the two new tool modules carry the
  `_invocation.guard` entry-point refusal (feature 127) and stay well under the file-size line.
- **XI**: no kanji.
- **XII. Historical Grounding**: nothing physical is claimed - this feature draws nothing and states
  nothing about how a place was built, so the spec's "Decisions Recorded" table is deliberately absent
  (the template says to delete it for tooling).
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: the manifests of the reference hamlet and of Kuwabata
  are the ratchet; a detached worktree at HEAD is the baseline if anything moves.
- **XIV. Fix Defects Where You Find Them**: any defect the new audit surfaces on a shipped map is fixed in
  this work or recorded with its measurement.
- **XV. Keep Going**: the pairing guard's harness question (R1) has a fallback path, so an unsupported
  hook event cannot block the feature.
- **XVI. Build What Was Asked**: spec FAITHFUL at round 2; the one carve-out found was struck. The
  unattended-idle case (R3) is routed through the override rather than exempted.
- **XVII**: no README.
- **XVIII. Every guard has a test companion**: `scripts/test-pair-hooks.sh`.

## Design

### 1. The polder probe (FR-001..FR-004)

`l7r/diagram/tools/polder_probe.py`, `make polder-probe SEED=21 [SEEDS=21,22] [ARCHETYPE=...]`.

Builds the block the way `stage_polder` does - `plan_site(HamletSpec(...))` then `fit_polder(...)`, the
SAME code the map rolls, so the probe cannot pass while the map fails. Prints per block:

| metric | why it is here |
|---|---|
| parcels overlapping a channel (count + coordinates) | the T55 rule |
| minimum berm parcel-to-water, and the fabric's median | the T55 review's finding |
| acreage, and the delta against the target | the clip's cost (0.29% vs the declined 3.4%) |
| per-parcel vertex count and square-corner mean | `polder_parcels_are_organic`'s own two numbers |
| ring point counts (min/median/max) | the densify/thin balance that bloated manifests once |
| wall time | SC-001's own bar |

Exits non-zero when a metric would fail the gate (overlap > 0, a parcel under 12 vertices, square-corner
mean over 2.5), so it can be chained ahead of an expensive run.

### 2. The overlap audit (FR-005..FR-007)

`l7r/diagram/tools/overlap_audit.py`, `make overlap-audit M=pool/hamlets/kuwabata.json [FAMILIES=...]`.

Families, each a named pair with its own measure - the questions actually asked in T50-T55:

| family | A | B | measure |
|---|---|---|---|
| `footprints-water` | houses, gardens, yards, sheds, byres, fixtures, wells | streams, channels, drawn channels, field ditches | footprint vs the drawn band (w/2) |
| `footprints-marsh` | the same footprints | marsh polygons by role | footprint vs polygon |
| `parcels-channels` | field plot rings | channels + drawn channels | ring vs band, both directions |
| `ink-mounds` | drawn marsh marks (tint, blades, glints) | dike bands, pond banks | mark vs polygon, by the mark's own reach |
| `ink-water` | the same marks | pond ellipse, channel bands | mark vs water |

The ink families read the SVG beside the manifest, because half the questions in T54/T55 were about ink.
Every offender is named with family, coordinates and count; exit non-zero if any. A family whose inputs are
absent from a map is reported `unmeasured`, never `0` (spec edge case).

### 3. Per-stage timings (FR-008, FR-009)

`make map GEN=... PROFILE=1` (and `make hamlet ARGS=... PROFILE=1`) sets `L7R_STAGE_PROFILE=1`, which
`hamletgen/driver.py` reads once at `build()`. With it unset the loop is exactly today's two lines.

This is an environment variable, which the project forbids for SWITCHES (feature 132: no variable may
change what a map rolls). The distinction is recorded at the point of change: a switch changes OUTPUT and
must be committed; this changes only what is PRINTED, and a test asserts the manifest is identical with
the flag on and off.

### 4. The pairing (FR-010..FR-014)

**`make verify`** - the one command: records the pairing intent for the current `engine_key` (the key
`.git/verification-state.json` already carries), launches the gate detached, and prints the review
dispatch line naming the maps whose manifests differ from HEAD.

**`scripts/pair-hooks.sh`**:

- `pretool` on **Bash**: an invocation of the gate is refused unless a settlement-review is pending in this
  session, or a review record matches the current `engine_key`, or the pairing token is fresh (i.e. the
  pairing command started it), or `PAIR_OK=<reason>` is present.
- `pretool` on **Agent**: a `settlement-review` dispatch is refused unless a gate is running or freshly
  green for this `engine_key`, or `PAIR_OK=<reason>`.
- `stop`: refuses to end a turn once while a pairing is half-open (a gate went green on this key and no
  review was dispatched) - the same shape as `agent-stall-hooks.sh`.
- Every refusal names the pairing command and the override; every override appends its reason to
  `dev/bypass-log/` in the existing record shape.
- Matching is on INVOCATIONS, not mentions: the time audit that produced this feature was itself blocked
  three times by a guard matching its own analysis text, and `test-pair-hooks.sh` carries that case.

## Project Structure

### Documentation (this feature)

```
specs/149-dev-loop-tooling/
├── spec.md          # FAITHFUL, round 2
├── plan.md          # this file
├── research.md      # R1-R4, the open mechanism questions
├── quickstart.md    # how to use the three tools
├── tasks.md         # from the tasks stage
└── checklists/requirements.md
```

### Source (repository)

```
.claude/skills/diagram/
├── l7r/diagram/tools/polder_probe.py       # NEW
├── l7r/diagram/tools/overlap_audit.py      # NEW
├── l7r/diagram/tools/CLAUDE.md             # two index rows
├── l7r/diagram/hamletgen/driver.py         # the PROFILE timer
├── Makefile                                # polder-probe, overlap-audit, PROFILE, verify
├── tests/tools/test_polder_probe.py        # NEW
├── tests/tools/test_overlap_audit.py       # NEW
├── tests/hamletgen/test_driver.py          # the flag's on/off equality
└── CLAUDE.md                               # the command map rows
scripts/pair-hooks.sh                       # NEW guard
scripts/test-pair-hooks.sh                  # NEW companion
.claude/settings.json                       # register pretool (Bash, Agent) + stop
CLAUDE.md                                   # the WHAT IS ENFORCED row
```

## Complexity Tracking

One deviation worth naming: the `PROFILE` environment variable, against the project's "no env override"
rule. Justification and the test that bounds it are in Design 3; the alternative (a CLI flag threaded
through `regen.py` and every gen script) was rejected because it would touch 20 frozen pool generators to
print a timing table.
