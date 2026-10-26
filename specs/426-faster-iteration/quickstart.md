# Quickstart: verifying feature 426

1. **The claims wait (D1)**: `make test-file FILE=tests/tooling/test_land_claims_wait.py` - a refusal with an introduced finding
   returns at once with its cure; an owed claim waits.
2. **The key (D2, D3)**: `make cohort`, add a docstring line to `l7r/diagram/hamletgen/ways/settle/stage.py::settle_the_web`,
   `make cohort` again: the summary says `rolled 0`. Change a number in it: those seeds roll. Revert. `make cache-audit` green.
3. **The landing reuses rolls (FR-012)**: `make cohort N=48 FRESH=0` then `make cohort-landing`: `rolled 0`.
4. **The modes (D4)**: after a run with failures, `make cohort LAST_FAILED=1` rolls only them; `EXITFIRST=1` stops at the first.
5. **The probe (D5)**: in a worktree with a step off, `make probe EXITFIRST=1`: the first seed worse than HEAD's, then stop; a
   second `make probe` at the same HEAD rolls no HEAD block.
6. **The template (D6)**: `make task-add F=<n> TITLE="x"` writes a section whose item 6 names `make arbiter-ask`.
