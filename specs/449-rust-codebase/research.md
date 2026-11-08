# Feature 449 - research

Every figure here is a one-shot observation of 2026-11-07 unless it carries an `m:` key in `measurements.json`.

## R1 - where the two slowest guards spend their time

**Finding** (observed 2026-11-07, method: each guard run under `bash -x` with `PS4='+ $EPOCHREALTIME '` on a sample PreToolUse
JSON for a Bash `ls`, the gaps between traced steps sorted): `pair-hooks.sh` took 0.194 s over 78 traced steps, and its six largest
gaps were each a Python start (`python3 -c` to read one field of the input JSON - `tool_name`, `tool_input`, `subagent_type`, the
transcript path), 18-30 ms apiece. `gate-hooks.sh` took 0.106 s over 56 steps, its largest gaps two runs of
`scripts/hooks/lib/hm_make.py` (31 and 26 ms) and a pipeline into `tr`. Neither guard does work of any size on a plain `ls`: the
time is processes started to read the input.

**Decision**: the guards' cost is starting processes, not checking. The replacement parses the input once and runs every check in
one process (D1). Rust's start is ~1 ms (`m:rust-tests` is 91 tests in 0.11 s, a process each test binary).

## R2 - how many processes one Bash call starts

**Finding** (observed 2026-11-07, method: each of the 26 guards that takes Bash run under `bash -x` on the same `ls` input, the
programs its trace runs counted): 26 bash shells, and 112 programs beneath them - 29 Python processes, 26 `cat`, 22 `dirname`,
12 `grep`, 8 `head`, 8 `sed`, 3 `tr`, 1 `date`. The Python starts alone, at 18-30 ms each (R1), are most of the 1,045 ms of CPU
summed per call (`m:hooks-bash`). The heaviest by count: `gate-hooks.sh` 15 programs (3 Python), `pair-hooks.sh` 14 (7 Python),
`measure-hooks.sh` 13 (2 Python).

**Decision**: one process for a tool call (FR-007), its checks in-process; a guard that must ask git or the file system asks once
for every guard that needs the answer (D6).

## R3 - the protocol the guards speak

**Finding** (method: the guards' shell and their libraries grepped for the hook protocol's fields and exits): a refusal is exit 2
with the reason on stderr (80 sites); a rewrite returns `hookSpecificOutput.updatedInput` (13 sites: the make-only guard's pytest
to `make test-file`, the shell check's `-m` to a heredoc, the bracketed process match, the house-style corrections); a notice
returns `hookSpecificOutput.additionalContext` (26 sites); the Stop guards return `decision`/`reason` (8) and `continue` (5).
Claude Code runs every matching hook of an event in parallel and merges their answers.

**Decision**: the replacement keeps that protocol exactly - `contracts/guard-protocol.md` - and merges its own guards' answers in
one fixed order (D2), since one process now does what parallel processes did: refusals collected and reported together; rewrites
applied in order, each guard seeing the input the earlier rewrites produced; notices concatenated.

## R4 - what a guard is made of today

**Finding** (method: `wc -l` and `ls`): `scripts/hooks/*.sh` is 6,258 lines of shell over 30 guards; `scripts/hooks/lib/` holds 9,053
lines of Python in 30 `hm_*.py` modules (the deciders) plus `guardlog.sh`, `hookmatch.py`'s three leaves and the escape reader. Each
guard has its suite, `tests/hooks/test-<guard>.sh` (8,184 lines of shell, 1,121 of Python), driving the guard through `$HOOK` with a
JSON input and asserting its exit code and output; `make hooks-test` runs them, keyed by `tests/hooks/hookdeps.py`.

**Decision**: a suite is the guard's verdict replay (FR-002, data-model "verdict replay"): pointed at the Rust guard
(`l7r-guard --only <guard>`), every case must give today's verdict before the shell guard is deleted (FR-003). The suites stay shell,
driving a binary, through phase 1; each becomes Rust tests of the guard's decider when that guard is ported (spec Assumptions).

## R5 - the guards' shared state

**Finding** (method: `guardlog.sh`, `hm_escape.py`, `.claude/settings.json`): every refusal and escape is appended to the guard log
(`make audit`, `make guard-log` read it); escapes are tokens in the command (`GUARD_EDIT_OK`, `MEASURE_OK`, ...) with a reason of two
words or more; several guards read the transcript (the GM's messages, for approvals and the escalation check) and the session's
clone map under `.clones/.session-clones/`.

**Decision**: the guard log's line format, the escape tokens and the transcript reads are kept byte for byte (`contracts/`), so
`make audit` and the GM's records read the Rust guard's lines as they read the shell's.

## R6 - where the binary lives, since every session runs main's copy

**Finding** (method: `.claude/settings.json`): each hook's command runs `/diagram/scripts/hooks/<guard>.sh` - the mirror's copy, not
the clone's - so a guard reaches every session only once it is on main (feature 379's `make land-tooling`). Build artifacts are
gitignored and not in the mirror.

**Decision**: settings call one small wrapper, `scripts/hooks/l7r-guard.sh <event>`, that runs the binary built from the tree it
sits in (`$HOME/.cache/l7r-cargo-target/<tree>/release/l7r-guard`) and builds it first when its sources are newer (D7). A guard
that cannot run - a build that fails - FAILS OPEN with a line saying so, as a crashing shell guard does today, and records it in
the guard log: a broken guard must not lock the GM out of every tool call.

## R7 - the design fixes to carry (FR-006)

**Finding** (`m:design-fixes`): the claims gate's import graph walked 39 times a run (kept per process since 39112f3ec); every record
command re-parsing 86 files' ASTs (read from the kept semantic ids since d3ff0e16d); a mutation test building the whole crate twice
(three files since 2b4238a6c).

**Decision**: each port keeps the fixed form - a value computed once per process or kept by content - and its tests pin the count,
not only the result (the work-budget counters' practice, feature 443).
