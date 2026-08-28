# Implementation Plan: The Performance Audit Subagent

**Branch**: none (`SPECIFY_FEATURE=129-perf-audit-subagent`) | **Date**: 2026-08-25 | **Spec**: [spec.md](spec.md) (FAITHFUL, every routed question answered)
**Request**: [gm-request.md](gm-request.md) - verbatim, the authority.
**Prerequisite**: feature 130 (the CodeBuild merge gate) - landed in this clone 2026-08-25; this feature is built on its bookends, its machine identity and its FULL builds.

## Summary

Every performance increase - on the total OR on any single seed, in EACH environment independently -
owes a written explanation and a `perf-audit` subagent's confirmation (band 1); above 5% total / 10%
per seed the subagent independently adjudicates the GM's three criteria (band 2); above 10% / 20%
the GM signs off personally before the push (band 3). The evidence is the per-stage delta every
snapshot already records (free), with a triggered one-stage cProfile when that cannot explain a
change. Records are committed one-file-per-run in `dev/perf-log/`, bound to the end snapshot's
commit and numbers, and the PUSH refuses without them. A subagent's shell is indistinguishable from
the main session's (research R1), so identity is DECLARED and recorded, and the record's content is
what a self-grant would have to falsify.

## Technical Context

**Language/Version**: Python 3.14, Bash. **Dependencies**: none new (stdlib `cProfile`).
**Storage**: `dev/perf-log/` (snapshots, review records - one file per event, tracked);
`dev/perf-raw/` (raw `.prof`, gitignored); a profile-archive repository the GM creates (R7).
**Testing**: `tests/tools/test_perf_bands.py` (pure evaluator, 100%), `tests/tools/test_perf_review.py`
(records, binding, refusals), `scripts/test-sync-with-main.sh` gains the push-side refusal case.
**Single-artifact target**: not a generator change - argued: the proof artifact is one band evaluation
on the recorded feature-128 pair (total -29.9%, seed 47 +30.7%), pinned as SC-002b.
**Every step is two steps**: every refusal is a FIRES/QUIET pair (XVIII); local and codebuild
environments are each evaluated and each tested.

## Performance bookends

Not a generator change: `make perf LABEL=129-start` and `-end` are taken anyway (constitution VI),
locally; the CodeBuild pair arrives with this feature's FULL merge build (feature 130).

## Constitution Check

- **I / II**: N/A - no UI in this repository. **III / VII / VIII / IX**: N/A - no pool content, no prose, no setting.
- **IV / V**: N/A - no SOURCE blocks touched.
- **VI**: verification per task: `make done` for Python; the band evaluator proven on the recorded
  feature-128 pair; the push refusal proven in the procedure's test suite; delegated work (the subagent
  definition) exercised once for real on this feature's own bookends.
- **X**: `perf_bands.py` and `perf_review.py` are `mypy --strict` and 100% covered (added to
  pyproject's `files` and coverage `source`); `perf_snapshot.py` stays a by-hand tool but its new
  identity function is covered by `tests/tools/test_perf_identity.py`. No file approaches 1,000 lines.
- **XII**: N/A - nothing asserted about the world.
- **XIII**: baseline = the green `make done` that closed feature 130 in this clone (3,574 passed);
  zero new failures at merge.
- **XIV**: defects met on the way are fixed here.
- **XV**: one planned stop, the GM's - creating the archive repository (R7); everything else proceeds.
- **XVI**: the spec is FAITHFUL; no exception is written. R1's fallback is the GM's own described
  design, not a carve-out.
- **XVIII**: every refusal ships with a FIRES/QUIET test that runs in the gate.

**Gate: PASS.**

## Design

1. **`l7r/diagram/tools/perf_bands.py`** (pure): `evaluate(base, cur) -> Verdict` with per-seed and
   total percentages, the band reached (0-3), which measurement crossed which line, and the stage
   delta per seed. Thresholds are constants pinned by a test: band 2 at >5% total / >10% seed, band 3
   at >10% / >20%; band 1 at any increase >0% on either. Environments never mix: `evaluate` refuses
   when `identity_of` differs.
2. **`l7r/diagram/tools/perf_review.py`**: the review records.
   - `make perf-explain WHY="..."` writes the PRE-POPULATED artifact (delta + stages + the session's
     explanation, verdict `pending`) - band 1's first half.
   - `make perf-confirm VERDICT=consistent|inconsistent NOTE="..." AS=perf-audit` - band 1's second
     half. Without `AS=perf-audit` the target prints the GM's prompt ("if you are the main session
     you should not continue") and DECLINES.
   - `make perf-audit VERDICT=justified|not-justified|cannot-determine NECESSARY="..."
     COMMENSURATE="..." NO_WAY_AROUND="..." AS=perf-audit` - band 2; every criterion required.
   - `make perf-signoff WHY="..."` - band 3; requires a terminal (`[ -t 0 ]`), records `AS=GM`.
   - Every record: `kind`, `feature`, `environment`, `band`, the base/end labels + utcs + commits,
     the measurements, `binding` = sha256(end commit, environment, sorted percentages), `granted_by`
     {declared, session_id, utc}. `--check` validates the newest pair per environment for the active
     feature: band ≥1 needs a `consistent` confirmation, ≥2 a `justified` audit, 3 a signoff, each
     with a matching binding - stale or negative records are refused by name.
3. **`perf_snapshot.py`**: `environment` field (R5); `report` prints the bands via `perf_bands` and
   returns 0 - the old 5%/10% two-band exit is superseded (constitution VI amended); the refusal names
   environments.
4. **Makefile**: `perf-gate` prints the band verdict and what is owed (FR-009b) after taking `-end`;
   `perf-review` runs `--check`; `perf-profile SEED= STAGE=` runs cProfile on one stage, writes the
   derived top-25 table to `dev/perf-log/<utc>-profile-<feature>-<seed>-<stage>.txt` (kilobytes,
   tracked) and the raw `.prof` to `dev/perf-raw/` (gitignored), then tries the archive (R7).
5. **`scripts/sync-with-main.sh` push**: after `review-gate.sh`, runs `make perf-review` in the skill
   directory; a refusal stops the push naming the command. Test seam `CI_PERF_REVIEW`.
6. **`.claude/agents/perf-audit.md`**: the subagent - reads the pre-populated artifact and the diff,
   confirms or adjudicates, and runs the make command with `AS=perf-audit`; pre-authorized in
   `container-scripts/append-system-prompt.md`.
7. **Constitution VI**: the two-band clause is replaced by the three-band matrix per environment
   (v2.1.0).
8. **CodeBuild noise floor** (R4): three `ci-check TARGET="perf LABEL=129-noise-x"` runs; the numbers
   in `research.md` and `timings.md`; a material difference reported to the GM.

## Complexity Tracking

| concern | why accepted |
|---|---|
| Identity is declared, not proven | R1: nothing distinguishes the shells; the GM anticipated this and described the fallback; the record's content is the real cost of a self-grant |
| Two review artifacts (confirmation, audit) | the GM's ladder: band 2 is a higher bar, not a bigger band 1 |
| Enforcement at the push, printed at the gate | the GM's words "before it is committed back to main"; the gate prints so nothing is surprised |
