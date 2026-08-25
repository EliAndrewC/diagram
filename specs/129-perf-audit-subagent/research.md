# Research: The Performance Audit Subagent

Every finding is MEASURED (a command ran, its output is quoted) or VERIFIED (a mechanism was
exercised). Taken 2026-08-25 in `/diagram/.clones/diagram-architecture`, after feature 130 landed the
CodeBuild gate this feature is built on.

## R1 - A subagent's shell is INDISTINGUISHABLE from the main session's (FR-008, the load-bearing unknown)

**Measured**: a `general-purpose` subagent ran `env | grep -iE 'claude|session|agent'` and the main
session ran the same. Every variable is identical:

    CLAUDE_CODE_SESSION_ID=2e04113c-d5de-479a-afd4-5aa18129f3f0   (both)
    CLAUDE_PID=186                                                (both)
    CLAUDE_CODE_CHILD_SESSION=1                                   (both)
    ppid=186, parent cmdline `claude --dangerously-skip-permissions`  (both)

No environment variable, process ancestor or socket differs. **Strict enforcement is NOT
achievable**: nothing a make target can read tells it which of the two is running it.

**Decision**: the GM's fallback, as they described it. The review-record targets PROMPT - they print
that the main session must not continue and names the escape, require an explicit `AS=perf-audit`
(or `AS=GM`) declaration, default to declining without it, and record the declaration plus the
session id (identical, but recorded so a later harness that DOES distinguish sessions can be checked
against it). What makes a self-grant costly is the record's CONTENT: a confirmation must state a
cause consistent with the stage delta, an audit must address the three criteria separately, and
both are committed, tracked files - a session granting itself one writes a false analysis into the
audit trail, the same visibility bar feature 127 set for every remaining bypass.

**Recorded so it is not re-investigated** (FR-008): the answer is "no" in Claude Code 2.1.241; the
probe is one command and is quoted above so a later harness can be re-checked in seconds.

## R2 - cProfile's overhead on the REAL `make perf` workload is +225% (FR-012)

**Measured**: seed 4 of the reference hamlet, all thirteen stages in-process, plain vs under
`cProfile.Profile()` in the same interpreter: **27.4 s plain, 89.0 s profiled, +225%**. The spec's
earlier figures (+196% on the check battery, +242% on a geometry loop) were on the wrong workload
and turned out to bracket the right one.

**Decision**: always-on is out - the GM's line was 20%. Function-level profiling is TIER 2: triggered,
one stage of one seed, only when the stage delta does not explain the change. Its cost is then ~3x
ONE stage of ONE seed (the `web` stage of seed 25 is ~63 s, so ~3 minutes), not 3x a 4-seed run.

**What the profile shows is worth having**: the same run put 37.7 s of 89 s in `ways.clear_runs`
(60,833 calls) under `stage_web` - exactly the "which function inside the stage" answer tier 1 cannot
give.

## R3 - What the existing per-stage timings CANNOT answer (FR-012a)

**Verified** against the recorded snapshots: every `dev/perf-log/*.json` carries `rows[].stages`,
thirteen numbers per seed, before and after, at zero overhead. A before/after stage delta answers
WHICH STAGE grew and BY HOW MUCH - which is the band-1 question ("does the stated cause match the
data?") and usually the band-2 question ("is the cost commensurate with the functionality?").

What it cannot answer: **which function inside the stage**, when a stage grew without a change the
diff can point at (a rule made hotter by a data change elsewhere; a helper's complexity changed by
an input shape). That gap is real but narrow, and R2 prices closing it at ~3 minutes of a single
triggered profile. **Tier 1 = the stage delta, always, free. Tier 2 = `make perf-profile SEED=n
STAGE=s`, triggered, derived top-N table committed (kilobytes), raw `.prof` kept out of this
repository.**

## R4 - The noise floor on CodeBuild (FR-016) - MEASURED 2026-08-25, and it matches the laptop's

Three `make ci-check TARGET="perf LABEL=129-noise-{a,b,c}"` runs on one unchanged commit (builds
8f16f7df, 7fb2f3b6, dc0dc235; `BUILD_GENERAL1_XLARGE`, the custom image), snapshots returned as build
artifacts:

| seed | run a | run b | run c | spread |
|---|---|---|---|---|
| 4 | 28.6 s | 28.8 s | 28.6 s | 0.7% |
| 25 | 87.1 s | 87.9 s | 88.1 s | 1.1% |
| 39 | 77.7 s | 78.5 s | 78.6 s | 1.1% |
| 47 | 96.8 s | 97.2 s | 96.5 s | 0.7% |
| **TOTAL** | **290.2 s** | **292.4 s** | **291.8 s** | **0.8%** |

**Worst per-seed spread 1.1%; total spread 0.8%** - against the laptop's 1.7% / 0.7%. Not materially
different: the GM's thresholds (set against 0.7%/1.7%) hold in both environments without
re-derivation, and both escalation triggers stay 5-7x above their floor there too. CodeBuild is
~8% slower per seed than the laptop (single-thread speed; the 36 cores do not help one generator),
which is exactly why a local pair and a CodeBuild pair are never compared (FR-014). Corroborated by
the two in-build bookends of build a6e2afe6 (290.8 s vs 293.0 s, +0.8%, on identical generator code).

## R5 - The environment is a first-class field, recorded not inferred (FR-013/FR-014)

Feature 130 added `host` (`laptop` | `codebuild:<compute type>`) and `image` to every snapshot and
made `perf-report` refuse a cross-machine pair. This feature adds the explicit **`environment`** field
(`local` | `codebuild`) the spec names - `host` is a machine class and could be widened (a second
laptop) without the environment changing - and the refusal names the environments. Snapshots older
than either field are laptop-era and read as `local`.

## R6 - Where each band is enforced

| band | evaluated by | enforced at |
|---|---|---|
| 1 explain+confirm | `perf-report` / `perf-gate` (prints), `perf-review --check` | the PUSH (`sync-with-main.sh`, beside `review-gate.sh`) |
| 2 audit | same | the push |
| 3 GM sign-off | same | the push - the GM's words, "before it is committed back to main" |

`make done` PRINTS the band and what is owed (FR-009b) so nothing passes the gate and is then
surprised at the push. On CodeBuild the FULL build takes both bookends itself (feature 130), so a
`codebuild` pair appears in `dev/perf-log/` after a FULL run and the push evaluates that environment
too, independently (FR-015).

## R7 - The profile archive repository (FR-011a): `EliAndrewC/mapgen-perflogs`, created by the GM 2026-08-25

`perf_profile.DEFAULT_ARCHIVE` points at it; pushes authenticate with the CodeBuild PAT through
`scripts/git-askpass-token.sh`. The first archived artifact was this feature's own seed-4 `seat`
profile. `PERF_ARCHIVE=` (empty) disables the step; any failure degrades to a message and the
derived table committed here stands alone (FR-011b).
