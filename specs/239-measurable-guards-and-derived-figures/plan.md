# Feature 239 - plan

The spec is detailed and accepted; this records only how it is built and the questions the spec left
open, each answered here rather than silently in code.

## Build order

1. **A - the decision is a function.** The 275-line program in `house-style-hooks.sh` moves into
   `scripts/_hm_house.py` as `decide(payload) -> Verdict` (output text, exit code, event, rule). The shell
   file becomes a wrapper that calls `_hm_house.py decide`, prints, logs and exits. `BRIT` and `PAIRS`
   move with it; `check-house-style-delta.py` imports them. Proven by the 45 cases unchanged and a
   zero-change verdict diff over the frozen window (FR-002) - which needs B's bench, so A and B land
   together.
2. **B - the bench.** `scripts/_hookbench.py`: `--refresh` builds the dated corpus (the logic of
   `measure/freeze_window.py`, promoted), `bench GUARD` replays it in process, `--against REF` prints the
   verdict diff. Wired as `make hookbench GUARD= [AGAINST=] [REFRESH=1]`.
3. **C - figures.** `spec-lint` check 5 and `scripts/figures.py` behind `make figures`.
4. **D - the contract.** `.claude/agents/spec-fidelity.md` and the tasks template.
5. The root `CLAUDE.md` guard-table rows for `spec-lint` and house-style, so the table stays true.

## Decisions the spec left open

**P1 - an AGAINST baseline at an old ref is spawned, and says so.** FR-007 refuses to bench a guard
whose decision cannot be imported "rather than silently falling back to spawning". SC-004 asks the bench
to reproduce feature 236's exemption diff against a commit from before this feature existed, when no
`decide()` was importable. Both hold if the rule reads as written: the guard UNDER TEST must be
importable (FR-007 refuses otherwise), while a historical BASELINE is spawned from a checkout of that
ref - loudly, with the cost printed, never as a silent substitute for the guard under test.

**P2 - check 5 applies to features numbered 239 and later.** The spec says a figure with a unit must
carry a key; it does not say whether that reaches the 238 specs written before the rule existed.
Read retroactively, the first edit to any old spec would fail on every figure it has ever stated - a
sweep of the whole record nobody asked for, and a refusal on unrelated work. The alternatives priced:
opting in by the presence of `measurements.json` (rejected - a new spec could dodge the check by not
creating the file), and a ledger of every old figure (rejected - hundreds of entries recording a rule
that did not exist). The feature number is decidable and cannot be dodged by a new spec.

**P3 - a broken decision module warns rather than falling silent.** Feature 236's import-stub section
proves the guard still ACTS when `_hm_house` cannot be imported. Once the decision lives in that module,
there is nothing left to act with. The wrapper therefore emits a context line naming the load failure
at exit 0 - a guard never takes the session down, and never goes quiet about being down - and the stub
section asserts that warning instead of a correction.

**P4 - `make figures` restores what it re-measures.** Re-running a recorded command rewrites
`measurements.json`; `make figures` copies the file aside, runs each distinct command once, compares, and
restores the original. It reports; it never records. A timing command refused by FR-011c's load rule is
reported as not re-measured rather than as moved.
