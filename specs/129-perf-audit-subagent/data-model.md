# Data model: feature 129

## Snapshot (existing `dev/perf-log/<utc>-<label>-<clone>.json`, two fields added)

```
+ environment: local | codebuild          (FR-013 - recorded, never inferred)
  host, image                             (feature 130's machine class; pairs only within one)
```

## Verdict (computed by `perf_bands.evaluate`, never stored on its own)

```
Verdict
  environment:  str
  base, cur:    (label, utc, commit)
  total_pct:    float
  seeds:        {seed: pct}
  stage_delta:  {seed: {stage: (before, after)}}
  band:         0 | 1 | 2 | 3
  crossed:      [ "total +12.3% > 10%", "seed 47 +30.7% > 20%" ]   (every line crossed, both measurements)
  owes:         "nothing" | "explanation + perf-audit confirmation" | "+ escalated audit" | "+ GM sign-off"
```

Bands (the GM's matrix, 2026-08-24): 1 = any increase >0% on EITHER; 2 = >5% total OR >10% seed;
3 = >10% total OR >20% seed. A band keeps everything below it. Evaluated per environment.

## ReviewRecord (`dev/perf-log/<utc>-review-<feature>-<kind>-<clone>.json`, tracked, one per event)

```
ReviewRecord
  kind:         explanation | confirmation | audit | signoff
  feature:      "129-perf-audit-subagent"
  environment:  local | codebuild
  band:         1 | 2 | 3
  base, end:    {label, utc, commit}
  measurements: {total_pct, seeds: {seed: pct}}
  binding:      sha256(end.commit | environment | sorted measurements)   (FR-005, FR-009a)
  explanation:  str          (kind=explanation; the session's cause)
  verdict:      pending | consistent | inconsistent | justified | not-justified | cannot-determine | signed
  note:         str
  criteria:     {necessary, commensurate, no_way_around}   (kind=audit, all three required - FR-003a)
  granted_by:   {declared: main | perf-audit | GM, session_id, utc}   (FR-007, R1)
```

Validity at `--check`: the newest `-start`/`-end` pair per environment for the active feature is
evaluated; a record counts only if its `binding` equals the pair's, and its verdict is the passing
one for its kind. Negative and inconclusive verdicts never count (FR-006).

## ProfileEvidence (`dev/perf-log/<utc>-profile-<feature>-<seed>-<stage>.txt`, tracked, kilobytes)

The top-25 cumulative functions of ONE stage of ONE seed under cProfile, with the plain and profiled
wall times at the top. The raw `.prof` goes to `dev/perf-raw/` (gitignored) and to the archive
repository when one is configured (FR-011a/b).
