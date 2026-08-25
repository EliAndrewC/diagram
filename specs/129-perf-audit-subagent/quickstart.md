# Quickstart: verifying feature 129 by hand

1. **The bands on the recorded feature-128 pair** (free): `make perf-report AGAINST=128-start` in a
   clone whose `dev/perf-log/` holds the 128 pair - expect "band 3: seed 47 +30.7% > 20%" although
   the total is -29.9% (SC-002b).
2. **Band 1 end to end** (free): take `make perf LABEL=129-start`, touch nothing, take `-end`; if any
   seed or the total is up by noise, `make perf-review` refuses; `make perf-explain WHY="within the
   1.7% per-seed floor measured on identical runs"`; `make perf-confirm VERDICT=consistent` WITHOUT
   `AS=perf-audit` -> declines with the prompt; launch the `perf-audit` subagent -> it runs the same
   with `AS=perf-audit`; `make perf-review` passes.
3. **Binding** (free): edit any `.py` under the engine and commit; `make perf-review` refuses the
   now-stale confirmation by name.
4. **Negative verdict** (free): a `perf-confirm VERDICT=inconsistent` record does not pass.
5. **Band 3 at the push** (free): a fixture pair with seed +25% -> `sync-with-main.sh push` refuses
   naming `make perf-signoff`; `make perf-signoff` with no terminal is refused.
6. **Cross-environment** (free): a `local` `-start` and a `codebuild` `-end` -> REFUSED, naming both.
7. **Tier 2** (~3 min): `make perf-profile SEED=25 STAGE=web` -> a kilobyte table under
   `dev/perf-log/`, the `.prof` under `dev/perf-raw/`, and "no archive configured" until the GM
   creates the repository.
8. **CodeBuild floor** (~$1.20): three `make ci-check TARGET="perf LABEL=129-noise-x"` runs on one
   commit; the spread recorded in `research.md`.
