# Data model: The effort-level experiment (feature 293)

All records are JSON in this feature directory unless said otherwise; every one is written by a script, never by hand.

## Run - `runs/<run-id>.json` (written by `effort-run` at launch, completed by `effort-measure`)

| field | meaning |
|---|---|
| `run_id` | neutral id, `e1`..`e4` (a void run's re-launch takes the next number) - no arm in it (spec edge case) |
| `task` | `R` or `I` |
| `arm` | `medium` or `xhigh` - the one field naming the arm; never copied into the clone |
| `seed`, `order` | the seed the first task's arm order was drawn from, and this run's position (1-4) |
| `start_commit` | the one commit every run starts from |
| `clone` | `/diagram/.clones/diagram-exp-<run-id>` |
| `sessions` | `[{sid, brief_or_prompt, prompt_sha256, effort, transcript, log_dir}]` - one for I, two for R |
| `argv` | each session's full command line, as launched |
| `env` | what the launcher set or unset: `L7R_SOURCES_HOME`, `CLAUDE_CODE_EFFORT_LEVEL` (unset), `SPECIFY_FEATURE` |
| `agents_json_sha256` | the hash of the `--agents` JSON (R1 D2), per session - identical across every session of every run |
| `shared_state` | R6 D6: `{sources_snapshot_sha256, claims_sha256_at_start, claims_lines_at_start, ledger_lines_appended, claims_lines_written, claims_release_line, prefixes_reserved}` |
| `started`, `ended`, `pauses` | UTC times; pauses from `interventions.md` |
| `exit`, `status` | the session exit codes; `valid` / `void` (with reason: 137, outage) |

Validation: `prompt_sha256` equal across the two runs of a task; `start_commit` and `agents_json_sha256` equal across all runs; no two runs'
`[started, ended]` overlap.

## Intervention - `interventions.md` (appended with `make append`)

One line per event: UTC, run id, kind (`answer` / `pause` / `void` / `relaunch` / `claim-release`), text. An answer given to one run of a task
is given, identically, to the other.

## Measurement - `measurements/<run-id>.json` (written by `effort-measure`)

- `tokens`: `{main: {input, output, cache_read, cache_creation}, subagents: {...}, total: {...}}`, plus `result_json_total` and the gap (R3).
- `wall_clock_s` (first to last event, minus pauses), `tool_calls` by tool, `dispatches` by agent type and model.
- `effort`: per message, the `effort` each assistant record carries - `main` (the run's sessions) and `subagents` by agent type (R1 P0 (b)).
- `adhoc_dispatches`: every ad-hoc dispatch not to a defined agent or `adhoc-judge`, with its model and description; `adhoc_judging_at_session_effort`: the count of those on `opus` or judging by their description (R1 D3).
- `rework`: `guard` (by guard x event x rule), `verdicts` (by agent: pass / not-pass, rounds per subject), `failed_runs` (with the matched
  lines), `fix_commits` (with subjects), `escalations`.
- `sources_cache_hits` for R runs (R6 D4).

## Rubric - `rubrics/research.md`, `rubrics/implementation.md`

Criteria, each with a 0-4 scale anchored in words, a weight, and a pass line (a weighted total and any criterion that must be at least 2).
Frozen by commit before that task's first run - a replaced task's before the replacement's first run (spec SC-002); the test `test_effort_rubrics_frozen` (in `test_effort_run.py`) refuses a launch if the
rubric files changed since the commit recorded as their freeze.

## Blinded pair and key

- The pair: a bundle directory OUTSIDE the repository (`/tmp/.../effort-blind/<task>/`), `A/` and `B/` plus `MANIFEST.md` and the rubric.
- The key: `.git/effort-keys/<task>.json` in the implementing session's clone (untracked; `{A: run-id, B: run-id, seed}`), copied to
  `keys/<task>.json` in this directory only after both grades are recorded.

## Grade - `grades/<task>-<grader>[-<n>].json`

`grader` is `effort-grader` (numbered runs, `-1`, `-2`: the research review is two runs, amendment of 2026-09-30) or `gm`; per label, per criterion: score and one-line reason; a preference (`A` / `B` / `tie`) with the criterion
it rests on; free notes on how the two differ.

## Report - `report.md`

The per-task table (run x: tokens by kind, main vs subagents, wall-clock, tool calls, the rework counts, both grades), the qualitative
differences, the later defects of the implementation winner, the FR-011 outcome per task type with its arithmetic, the tiers that ran and
any control unmet, the interventions, the caveats.
