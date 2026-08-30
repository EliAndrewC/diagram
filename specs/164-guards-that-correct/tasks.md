# Tasks: Guards That Correct Instead of Refusing (feature 164)

Every task here is `research: procedure`: this feature changes what the TOOLING does when it refuses,
never a claim about how a place was built, farmed or lived in. The measurements are
[`research.md`](research.md); the mechanism verification is in [`plan.md`](plan.md).

Cycle discipline: guard work is verified by its companion suite, and every new assertion is proved to
FIRE by removing the code it guards - the project's rule for adding a guard, applied to changing one.

## Phase 0 - the baseline (Principle XIII)

- [x] T01 baseline on the unmodified clone, 2026-08-30: **`make hooks-test` GREEN, exit 0** -
      *"0 guard suites green, 19 unchanged since they last went green"*, every suite fresh against
      the guard scripts as they stand. Nothing pre-existing to ledger
      research: procedure
      verify: /tmp/164-base-hooks.log, quoted above

## Phase 1 - the shared decisions, unit-testable

- [x] T02 `_hookmatch.py` gains `as_make_target(cmd)`: a bare pytest of ONE test file becomes
      `make test-file FILE=<path>`, `None` when the shape is not exactly rebuildable. Preserves a
      leading `cd ... &&` and the `( cd <abs> && ... )` convention
      research: procedure
      verify: vectors for both cd shapes, a `-k` filter, a coverage flag, two paths, a directory, a
      pipeline, and a MENTION inside a quoted string - each asserting refusal is preserved
      DONE: `as_make_target` in `_hookmatch.py`, 9 vectors including both cd shapes and every refusal case
- [x] T03 `_hookmatch.py` gains `bracket_pattern(cmd)`: a literal `pgrep -f` / `pkill -f` becomes the
      bracket form the refusal already recommends
      research: procedure
      verify: a literal pattern, one already bracketed, one built from a variable (both untouched)

      DONE: `bracket_pattern`, 6 vectors; a bracketed or variable pattern is left alone
## Phase 2 - the four rewrites

- [x] T04 `make-only`: rewrite a one-file bare pytest; keep the refusal for every other shape. FIX
      the message while there (Principle XIV): its stated reason is coverage floors, which is false -
      the target it now names runs `--no-cov` - and it never named the one-file target at all
      research: procedure
      verify: `scripts/test-make-only-hooks.sh` - the rewrite, the preserved refusals, and the
      message naming the one-file target
      DONE: `make-only` rewrites and records; 37/37 green. Its message lost the false coverage reason and gained the one-file target
- [x] T05 `no-poll`: ask `_hookmatch.py` whether the shape is INVOKED (it refused the command writing
      this feature's spec), and rewrite a literal `pgrep -f` instead of complaining about it
      research: procedure
      verify: `scripts/test-no-poll-hooks.sh` - a mention passes, a real busy-wait is still refused,
      the rewrite lands
      DONE: `no-poll` corrects the pattern and matches the SANITIZED command; 33/33 green, including five vectors proving a document about the guard now passes. The ordering defect it exposed is `research.md` R8.1
- [x] T06 `measure-hooks`: the same matcher change, and replace the stale limitation comment. The
      BLOCK is untouched - it is the point
      research: procedure
      verify: `scripts/test-measure-hooks.sh` - a command whose PROSE names a gate target no longer
      counts against the budget; the block still fires on the second real measurement
      DONE: `measure` matches the sanitized command; 31/31. Section 7 inverted from 'a mention blocks - the known false positive' to 'a mention is not a run'
- [x] T07 `pair`: rewrite `make done` to `make verify` when a review is owed, with the line telling
      the session to dispatch it in the same turn
      research: procedure
      verify: `scripts/test-pair-hooks.sh` - the rewrite when owed, untouched when not, and the
      MENTION shape that suite already guards
      DONE: `pair` rewrites `make done` into `make verify`; 23/23. A shape that cannot convert (FULL=1) still refuses
- [x] T08 `house-style`: correct the payload instead of refusing. The GM-writing exemption is
      extended to `specs/*/request.md` BEFORE any correction is computed; a word inside a backtick
      code span is a MENTION, not a use (this feature's own plan was refused for naming one)
      research: procedure
      verify: `scripts/test-house-style-hooks.sh` - a correction applied, a `request.md` refused
      rather than corrected, a backticked mention passed, and a violation the table cannot fix
      still refused

      DONE: `house-style` corrects the payload; 16/16 plus 7 standalone probes. Backtick spans are held out of detection AND correction, and `specs/*/request.md` never leaves the refusal path
## Phase 3 - the two teach-first conversions

- [x] T09 `guard-file`: return the `GUARD_EDIT_OK` line as context on a READ of a guard file; the
      refusal stays as the backstop
      research: procedure
      verify: `scripts/test-guard-file-hooks.sh` - context on a guard file, silence on an ordinary
      one, and the refusal unchanged
      DONE: `guard-file` returns its line on a READ; `settings.json` matcher widened to Read; 19/19
- [x] T10 `batching`: attach the playbook one turn below the threshold. The window, the backoff and
      the block are untouched
      research: procedure
      verify: `scripts/test-batching-hooks.sh` - the warning one turn early, the block still at the
      threshold, and the counters unchanged

      DONE: `batching` warns one turn below the bar; 40/40, including a vector proving a quiet session gets no notice
## Phase 4 - recording and close

- [x] T11 every conversion calls `guard_log` (`rewrote` / `reminded` / `blocked`), and every suite
      isolates `GUARD_LOG_DIR` for the whole file and asserts it was never dropped (feature 162 T16)
      research: procedure
      verify: purge the real log, run every suite, count it - 0 before and 0 after
      DONE: every conversion calls `guard_log`; every suite isolates `GUARD_LOG_DIR`. Audited: 0 fixture entries in the real census before and after running all seven suites (24 leaked on the first pass)
- [x] T12 `make hooks-test`: **19 guard suites green, exit 0** - exactly the 19 T01 recorded, so no
      regression. Every suite re-ran rather than being skipped, because the shared helpers changed.
      `make done` recorded below
      research: procedure
      verify: both green, no new failure against the baseline
- [ ] T13 update `CLAUDE.md`'s guard table for every converted guard, and audit `dev/bypass-log/`
      for the entries this feature added, in writing
      research: procedure
      verify: the audit written into this file, and the table read back
