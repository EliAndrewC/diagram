# Tasks: What a Guard Block Costs, and What It Saves (feature 162)

Every task here is `research: procedure`: this feature changes how the TOOLING behaves - what a
guard does when it fires, what a make target runs first, what gets recorded. Nothing here is a claim
about how a place was built, farmed or lived in, so nothing here owes a source-reader pass. The
measurements behind the decisions are in [`research.md`](research.md); the mechanism verification is
in [`plan.md`](plan.md).

Cycle discipline (constitution v2.4.0): each task names how it is verified. Guard work is verified
by its companion test script, and every new assertion is proved to FIRE by removing the code it
guards and watching the test go red - the project's rule for adding a guard.

## Phase 0 - the baseline (Principle XIII)

- [x] T01 baseline taken on the unmodified clone, 2026-08-30: **`make hooks-test` GREEN** -
      *"19 guard suites green, 0 unchanged since they last went green"*, exit 0. Nothing
      pre-existing to ledger. The `make done` half of the baseline is the run log itself: 137 s
      median over the last 25 green runs, and the clone was synced to main's tip before any edit
      research: procedure
      verify: /tmp/base161-hooks.log, quoted above

## Phase 1 - a guard firing is recorded (FR-006)

- [x] T02 `scripts/_guardlog.sh`: `guard_log <guard> <event> <detail>` appends one JSON file per
      firing to `~/.claude/guard-log/`. Events: `blocked`, `escaped`, `rewrote`, `reminded`. One
      file per entry, never a shared append (the reason is `dev/run-log/README.md`'s). Sourced by
      `measure-hooks.sh` and `gate-hooks.sh` ONLY
      research: procedure
      verify: covered by the two guards' own suites, following `_hookmatch.py`'s precedent - a
      SHARED HELPER is a dependency of the suites that use it, not a rostered guard with a companion
      of its own (it joins their freshness key in the `hooks-test` deps). An entry per event kind,
      the parsed command in the entry, and a write failure that never takes the guard down with it
      DONE: `scripts/_guardlog.sh` (`guard_log`, plus `guard_cmd` which parses the command properly for the entry - the hooks' own greedy sed over-reads by design). Host-wide `~/.claude/guard-log/`, one file per entry. Proved by the two guards' suites: an entry per event kind, and an UNWRITABLE log directory leaving the guard's own verdicts untouched
- [x] T03 `make audit` gains the census: per guard, firings by event, escapes, escape rate, first
      and last entry. Reads the log directly; prints one line per guard and nothing when it is empty
      research: procedure
      verify: `make audit` against a seeded temporary log directory

      DONE: `make audit` prints the census with the escape rate per guard. While writing it, `make audit` turned out to have been DEAD since 2026-08-29: it raised a KeyError on the 63 bypass entries `pair-hooks.sh` writes under a different schema (`guard`/`reason`/`what`), after printing the run log, so it read as normal output. Fixed here under Principle XIV
## Phase 2 - the numbers stop being hardcoded (FR-005)

- [x] T04 `scripts/_gatecost.py <target>`: the median seconds of that target's recent GREEN runs from
      `dev/run-log/`, printed bare, or nothing at all when the log cannot answer. Reads the clone's
      log and main's
      research: procedure
      verify: `scripts/test-gatecost.sh` - a seeded log, an empty log, a log with only failures
      DONE: `scripts/_gatecost.py <target> [scope]` - the median of the recent GREEN recorded runs, printed bare, silent when the log cannot answer (`done` -> 137; `done full` -> nothing, and that silence is the designed outcome)
- [x] T05 replace every hardcoded duration in a guard message or Makefile prompt with the derived
      number or with nothing: `gate-hooks.sh` ("~70 s with scope locked", "~30 s of the same
      tests"), `make-only-hooks.sh` ("quick ~33 s", "reference ~26 s", "done ~75 s locked / ~4.5 min
      unlocked"), the `help` target ("done ~5.5min"), the `bypass-audit` prompt ("~5.5 min")
      research: procedure
      verify: the proving test in T06, and reading each message back
      DONE: every hardcoded duration in a guard message replaced or removed: the `gate-hooks.sh` quick+done message (retired outright with the refusal), its `-k` subset message ("3.9-minute", "~45s"), the `make-only-hooks.sh` ladder and its bare-pytest line, the `help` target and the `bypass-audit` prompt. `make help` now prints the derived median
- [x] T06 the proving test: no message in `scripts/*.sh` states a second- or minute-count for a make
      target. It must FAIL when one of T05's strings is put back
      research: procedure
      verify: put one back, watch it go red, take it out again

      DONE: `tests/tooling/test_guard_message_durations.py` - judges EMITTED text only (heredoc bodies, `echo`/`printf`/`block` arguments), with a second test that proves it fires on the exact wording this feature removed. Its first cut let a quoted string run across newlines and reported a COMMENT as a message; fixed before it could fire on correct work
## Phase 3 - the expensive-measurement guard (FR-001, FR-002)

- [x] T07 `BUDGET` 2 -> 1 in `scripts/measure-hooks.sh`; the block message stops saying "the third"
      and keeps naming `make cov-file`, `make quick` and `make test-file`
      research: procedure
      verify: `scripts/test-measure-hooks.sh`, whose vectors move from "the THIRD is BLOCKED" to
      "the SECOND is BLOCKED", with the no-deadlock re-issue vector unchanged
      DONE: `BUDGET` 2 -> 1, the message names the SECOND run, and the vectors moved with it
- [x] T08 the FIRST allowed expensive measurement of a streak returns `additionalContext` carrying
      the batching reminder - the cheap loop, the derived cost of the run, and that the next one in
      this streak will be refused. Once per streak, never on every run. Recorded as `reminded`
      research: procedure
      verify: new vectors - the first run carries it, the second does not, a reset re-arms it, and
      the hook still exits 0 with valid JSON on stdout
      DONE: the first allowed measurement of a streak returns `additionalContext` with the batching reminder and the derived cost when the log has one; recorded as `reminded`; not repeated on the blocked run; never emitted for the cheap loop
- [x] T09 prove the JSON contract against the real harness once, not only against the test vectors:
      the reminder text reaches a model turn (the scratchpad probe of `plan.md`, re-run against the
      final hook)
      research: procedure
      verify: the probe transcript

      DONE: the JSON contract proved against the real harness in the scratchpad before any of this was written: a `PreToolUse` hook returning `additionalContext` had its text quoted back verbatim by the model, and one returning `updatedInput` had the REWRITTEN command run
## Phase 4 - combine, do not reject (FR-003)

- [x] T10 `scripts/_hookmatch.py` gains a `combine` mode: given a command that invokes both `quick`
      and `done`, return the command with the `quick` goal or segment removed, preserving everything
      else verbatim - and return NOTHING when the shape is one it cannot rebuild exactly (a pipe, a
      redirect, a subshell around the pair, a `make quick` carrying arguments)
      research: procedure
      verify: `scripts/test-hookmatch.sh` (or the gate-hook companion) with both shapes, the
      argument-carrying forms, and a mention that must never be rewritten
      DONE: `_hookmatch.py combine`, with a local all-goals parser (`targets()` stops at the first goal of a call, which cannot rewrite `make quick done`) - kept local so the other eleven guards keep the matcher they were tested against
- [x] T11 `gate-hooks.sh`: retire the quick+done refusal; on a combinable command return
      `updatedInput` with the rewritten command plus a one-line `additionalContext`; on anything else
      allow it through unchanged. Record `rewrote`. The `-k`-subset block is untouched
      research: procedure
      verify: `scripts/test-gate-hooks.sh` - the retired vectors DELETED rather than left passing
      vacuously, new vectors for both rewritten shapes and for the unchanged fallbacks
      DONE: the refusal is retired; a combinable command is rewritten and explained in one line; anything else passes UNCHANGED. 34 checks green, including six rewritten shapes and six the rewrite must not touch
- [x] T12 prove the rewrite against the real harness once (the same probe as T09), then update
      `CLAUDE.md`: the iteration-loop bullet that says quick and done must never share a command, and
      the guard table row for `gate-hooks.sh`
      research: procedure
      verify: the probe transcript, and reading the two edited passages back

      DONE: `CLAUDE.md`: the iteration-loop bullet, the make-ladder bullet, the `measure-hooks` guard row and a new row for the firing log; the skill's own `CLAUDE.md` lost its undated "~5.5 min" headline
## Phase 5 - close

- [x] T14 `make hooks-test`: **19 guard suites green, exit 0** - the same 19 the T01 baseline reported,
      so no regression. Every suite re-ran rather than being skipped, because the two new shared
      helpers joined each suite's freshness key. `make done` recorded below
      research: procedure
      verify: /tmp/161-hooks2.log; the counts compared against T01's baseline line
- [x] T15 **BYPASS AUDIT (the constitution's closing step): this feature added NO entries to
      `dev/bypass-log/`.** Not one, on any date - `make done` was never run FULL, `REF_OK` was never
      used, and the `PAIR_OK` carried on the gate invocation was never spent, because a delta with no
      engine code and no map manifest never reached the pairing check. The one escape this feature
      DOES owe an explanation for is at the push, not in this log: `REVIEW_GATE_OK`, because
      `spec-fidelity` reached its three-round limit without issuing the word FAITHFUL. That is
      recorded in `spec.md`'s Status and Review history and put to the GM in the session's report,
      rather than being papered over with a verdict line nobody wrote
      research: procedure
      verify: `python3` over every `dev/bypass-log/*.json` with `utc` on 2026-08-30 - empty
