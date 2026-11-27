# 451 T383 and T385 - the Edit hook's two slow reads, before and after

Measured 2026-11-26, 19:28 to 19:30 local, by the builder of the bundle, in T373's throwaway world (`t373-results.md`, "How it was
measured": the sandbox mirror, clone and pool worktree under the scratchpad, its 41.9 MB feature log and 274 MB transcript), reused
as it stood. Every figure is wall milliseconds of one hook call, median / 90th centile over 20 counted runs after one warm-up round.

## The two binaries, and the arms

- BEFORE: `l7r-guard` built from `1ceb830054` (the tree before any edit) by the launcher (`scripts/hooks/l7r-guard.sh`,
  `L7R_GUARD_PRINT_FRESH=1`), copied to the scratchpad. AFTER: the same launcher's build of the tree with both fixes.
- One run holds both: the eight arms (before and after, each as the hook, the binary, and the two guards alone) are interleaved
  round-robin, their order reversed every other round, so both binaries met the same load (`t383-time.py`, T373's timer with a
  second binary). The payload is T373's `edit-doc.PreToolUse` (an Edit of `docs/usage.md`): session `sess` in the sandbox clone,
  dirty (T373's first table's state), and `wt`, a builder in the sandbox's pool worktree.
- The environment of every call, `env -i` plus exactly: `PATH`, `HOME` (the sandbox's scratch home), `CLAUDE_PROJECT_DIR` and
  `CLONE_MAIN` (the sandbox mirror), `L7R_GUARD_TARGET` (that arm's binary), `L7R_GATE_TARGET` (an empty scratch directory, T373's
  note for next time; nothing was built in it), `GUARD_LOG_DIR`, `MEASURE_STATE_DIR`, `L7R_GUARD_TREE`.

## The figures (`t383-timing.tsv`)

The machine was shared with other builders: load1 16.6 to 24.8 during the clone's run and 13.3 to 16.0 during the worktree's (22
cores), the first LOADED by T373's mark (above 20) at its peak, the second below it.

| an Edit of a doc, PreToolUse | before | after | saved at the median |
|---|---|---|---|
| the session in its CLONE, the hook (launcher + binary) | 887.8 / 1113.1 | 204.2 / 686.1 | 683.6 |
| ... the binary, every guard | 846.7 / 1173.2 | 179.5 / 593.8 | 667.2 |
| ... `event-log-hooks` alone | 343.6 / 541.9 | 81.0 / 184.2 | 262.6 |
| ... `clone-sync-hooks` alone | 563.7 / 1230.9 | 96.7 / 366.0 | 467.0 |
| a builder in a pool WORKTREE, the hook | 384.5 / 531.6 | 89.8 / 109.0 | 294.7 |
| ... the binary, every guard | 366.4 / 511.0 | 76.6 / 95.9 | 289.8 |
| ... `event-log-hooks` alone | 352.1 / 427.2 | 78.3 / 107.8 | 273.8 |
| ... `clone-sync-hooks` alone (no opinion in a worktree) | 2.7 / 3.0 | 2.7 / 3.4 | 0 |

Every call of every arm exited 0 with no output. What is left: `event-log-hooks`' 78 to 81 ms is the read of the whole log and
the text screen (T373 measured the read alone at 46.6 ms); `clone-sync-hooks`' 97 ms is its `git status --porcelain` (T373: 83 ms).

## The screen against the full parse, on the real logs (`t383-differential.tsv`, `t383-differential.rs`)

The differential ran INSIDE the crate, as a temporary test of `reversal/tests.rs` calling the crate's own `candidate`, `needle` and
`replaced` (its source is kept as `t383-differential.rs`; it was removed from the tree after its run), over a copy of every log of
the real clone's `.git/l7r-events/` (34 logs, 468,589 lines; the copy was deleted). For each log it parsed EVERY line, kept the
lines the old read used (`ev` PreToolUse, `tool` Edit) by path, and asked two things:

- for every such line, does the screen for ITS path keep it: 8,661 lines, 0 dropped;
- for every distinct path, is `replaced` (screen, then parse) equal to the old read's list: 1,806 paths, 0 differ.

The 451 log: 158,456 lines, 9,338 holding the Edit marker, 4,722 PreToolUse Edit lines over 714 paths; the most-edited path had
2,176 lines parsed where the old read parsed 158,456. NO real path needed the tool-alone screen (0 of 1,806 holds a quote, a
backslash, a control character or non-ASCII), so that case is proved by the constructed fixtures of `reversal/tests.rs`, not here.

## The leak check (`t383-leak-check.txt`)

T373's method, after the run: no line of a `t373-*` session id in the real clone's or the mirror's event logs, no `t373-*` or
`t383-*` claim-map entry, no real guard-log entry naming the sandbox, no `toolu_t373` id in the real `checks-open.json`. The
sandbox's own 451 log gained 252 lines (the three log-writing arms of each binary, 21 rounds, two sessions), and the sandbox clone
was put back clean.

## Files

`t383-time.py`, `t383-timing.tsv` (columns: session, arm, runs, median, 90th centile, minimum, maximum, exit codes, output sizes,
load range), `t383-differential.rs`, `t383-differential.tsv`, `t383-leak-check.txt`.
