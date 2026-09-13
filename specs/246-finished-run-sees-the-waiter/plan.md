# Plan - 246 The finished-run guard sees the waiter

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **XVIII**: the guard keeps its companion suite; every new branch (tracked, watched, unwatched, the
  two-phase root, the wrong-file watcher) is a case that drives a REAL process, and `make hooks-test`
  runs it as a gate phase.
- **VI**: `make hooks-test` green before the push; the feature's own gate observes SC-003.
- **X**: no engine code; `scripts/finished-run-hooks.sh` stays one file well under the bar.
- **XVI**: spec-fidelity before code; this plan reviewed (MODE 4) before any tick.
- **Route**: `scripts/*.sh` only -> DIRECT, with the guard-script stamp from a green `make hooks-test`.
- **Guard files**: the hook and its suite are guard files - every edit carries `GUARD_EDIT_OK` with the
  reason.

## Design

- `finished-run-hooks.sh`: `live_runs` keeps its `<pid> <target>` output (the `live` mode, `make audit`
  and the suite read it). A new python block, `judge_runs <clone> <hook-pid>`, prints one line per ROOT
  live make - `<pid> <target> <status> <detail>` - where root = a live make none of whose ancestors is a
  live make; status `tracked` when an ancestor's `comm` is `claude` (detail: that ancestor's stdout
  target), `watched` when the make's stdout target is a regular file and a process outside the hook's
  ancestry has the loop shape (`\b(until|while)\b.*\bgrep\b` and `sleep`) and names that path (detail: the
  waiter's pid and the file), else `unwatched` (detail: the stdout target). Ancestry walks `/proc/<pid>/stat`
  as `stale_waiters` does.
- The stop branch: if any root is `unwatched`, the marker (`.git/live-run.told`) holds the unwatched ROOT
  pids; refuse (exit 2) unless the marker already equals them; the message lists every live run, names the
  detached run's log in the loop it prescribes, and says a harness-background run needs no loop; record
  `blocked`/`run-still-going`. Otherwise print one line per root (`finished-run: \`make <target>\` (pid N)
  is still going - <the harness will wake this session when it finishes | a waiter (pid M) is watching
  <file>>`), record `permitted`/`tracked-run` or `permitted`/`waiter-armed` per root, exit 0. The marker
  is cleared when nothing is live, as today.
- The suite, section 6, gains: a `claude`-named bash (a copy of bash under that name, so `comm` reads
  `claude`) running `make sleeper` with stdout to `$T/tasks/t.output` -> stop exits 0, context line,
  `tracked-run` recorded; a detached `make sleeper > $T/run.log` with `until grep ... $T/run.log; do
  sleep; done` running -> exit 0, `waiter-armed`; the same with the loop naming another file -> exit 2;
  a `phases` target running `$(MAKE) p1` (sleeps 3) then `$(MAKE) p2` (sleeps 8), detached -> exit 2 at
  once, then exit 0 four seconds later with p2 the live child. The existing once-per-run and
  no-token-escape cases stay.
- The hook header and the root CLAUDE.md row: the rule as amended, with R1's numbers pointed at.
- `future-work/cross-cutting.md`: the lost-notification fallback, with what would reopen it.
- SC-003 observed on this feature's own gate: `make done` through the Bash tool's background mode, the
  turn ended, the context line seen, no refusal - recorded in tasks.md.
