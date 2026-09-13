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

**P2 - OVERRULED: check 5 applies to every spec a delta touches, whatever its number.** The first
version limited check 5 to features numbered 239 and later, reasoning that read retroactively the first
edit to any of the 238 earlier specs would fail on every figure it has ever stated. That shipped before
the independent Principle XVI check the constitution requires, and when the check ran it ruled the cutoff
NOT LEGITIMATE on grounds that do not leave room for doubt: the case that motivated this entire feature
was feature 236's second amendment - numbered below 239 - so the cutoff exempted exactly the work the
rule exists for; amending an old spec is routine here; new work could dodge the check by amending an old
feature instead of claiming a number; and the reviewer's NOT-REVIEWABLE contract has no such cutoff, so
the lint and the reviewer disagreed. The cost of the literal rule - an old spec touched for an unrelated
reason owes a key or a one-shot label for the figures check 5 reaches - is real and was put to the GM
rather than decided here. The alternatives priced for the cutoff are kept on record: opting in by the
presence of `measurements.json` (a new spec could dodge it) and a ledger of every old figure (hundreds of
entries). A narrower form the check suggested - scoped to the paragraphs a delta adds or changes, the
shape feature 236's house-style check takes - would be a different exception and needs its own ruling.
**The `tasks.md` condition was overruled the same way**, by a second independent check: the number claim
pushes an EMPTY directory, so the condition protected nothing there, and initial spec review happens
before a tasks.md exists, so it switched the mechanical check off during exactly the rounds where
figures reach a reviewer. Its follow-ons: the spec template's example figures sit in backtick spans, as
figures named rather than asserted, so a draft still carrying template text does not fail.

**P3 - a broken decision module warns rather than falling silent.** Feature 236's import-stub section
proves the guard still ACTS when `_hm_house` cannot be imported. Once the decision lives in that module,
there is nothing left to act with. The wrapper therefore emits a context line naming the load failure
at exit 0 - a guard never takes the session down, and never goes quiet about being down - and the stub
section asserts that warning instead of a correction.

**P4 - `make figures` restores what it re-measures.** Re-running a recorded command rewrites
`measurements.json`; `make figures` copies the file aside, runs each distinct command once, compares, and
restores the original. It reports; it never records. A timing command refused by FR-011c's load rule is
reported as not re-measured rather than as moved.
