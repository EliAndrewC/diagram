# Contracts: the make targets (diagram skill `Makefile`), feature 129

| target | who runs it | what it does |
|---|---|---|
| `make perf-report [AGAINST=<label>]` | anyone | the trend, then the BAND verdict for the newest pair (per environment); exit 0 always - the bands are enforced at the push |
| `make perf-gate` | `done FULL=1` (local or in a build) | takes `-end`, prints the verdict and what is owed (FR-009b); exits nonzero only when a bookend is missing (unchanged) |
| `make perf-explain WHY="<cause>"` | the session | writes the pre-populated band-1 artifact with the session's explanation |
| `make perf-confirm VERDICT=consistent\|inconsistent [NOTE=...] AS=perf-audit` | the `perf-audit` subagent | band 1's confirmation; without `AS=perf-audit` it prints the prompt and DECLINES |
| `make perf-audit VERDICT=justified\|not-justified\|cannot-determine NECESSARY=... COMMENSURATE=... NO_WAY_AROUND=... AS=perf-audit` | the subagent | band 2; refuses if any criterion is empty |
| `make perf-signoff WHY="<reason>"` | the GM, at a terminal | band 3; refused without a terminal; recorded as `AS=GM` |
| `make perf-profile SEED=<n> STAGE=<name>` | the session or the subagent | tier 2: cProfile of one stage of one seed; derived table committed, raw `.prof` gitignored / archived |
| `make perf-review` | `sync-with-main.sh push` | `--check`: every environment's newest pair for the active feature must carry the records its band owes; refuses naming the command |

`scripts/sync-with-main.sh push` runs `make perf-review` after `review-gate.sh`, before the route
decision. `CI_PERF_REVIEW` is the test seam (`skip` in fixtures without the skill).
