# Tasks: Escapes Carry a Reason (feature 170)

Every task is `research: procedure` - this feature changes what a guard demands of a session and what
the tooling reports about itself. Nothing here decides how a place was built, farmed or lived in, so
no task carries the physical checkboxes. The GM's words are in [`request.md`](request.md).

- [x] T01 baseline: `make hooks-test` and `make done` green before any change
      research: procedure
      verify: both green on the merged state, so anything red afterwards is this feature's

- [x] T02 FR-001: a reason floor in `_hookmatch.py` - `escape_reason(cmd, token)` returns the text
      following `TOKEN:` or `TOKEN=`, and the escape is honored only when it has two words and eight
      characters. One implementation, used by every guard, exactly as `escape_used` is
      research: procedure
      verify: ten reason forms asserted in BOTH directions, and two defects of my own that only a
      two-directional check finds - the SPACE form (`# NO_BRANCH_OK throwaway bisect`, which is how
      CLAUDE.md documents it) was refused, and `MEASURE_OK=1 make test-full` would have PASSED

- [x] T03 FR-001: every command guard refuses a bare token and says the compliant form, using the
      token the session actually reached for
      research: procedure
      verify: each guard driven with a bare token (refused) and with a real reason (permitted), and
      its own suite green

- [x] T04 FR-002: the two silent permits record - `make-only` (via a distinct verdict from
      `classify()`, whose consumers all have a default-refuses `case` and must be audited) and
      `GATE_STAMP_OK` in `sync-with-main.sh`, a file that today has no `guard_log` call at all
      research: procedure
      verify: both driven; an entry lands for each, with the REASON as its detail

- [x] T05 FR-003 / FR-003b: the content, environment and make-variable escapes take the same floor,
      and `pair`'s agent-prompt branch does too - keeping its prose matching, gaining the reason
      research: procedure
      verify: `SOURCE_EDIT_OK`, `GUARD_EDIT_OK`, `REVIEW_GATE_OK`, `GATE_STAMP_OK`, `REF_OK`/`REF_WHY`
      and the `pair` prompt each driven bare (refused) and with a reason (permitted)

- [x] T06 FR-003: `not-an-escape` (`SWEEP_OK`, `REMOTE_OK`) owes nothing, and the derived census
      asserts that so a future reader cannot mistake the omission for an oversight
      research: procedure
      verify: the census test in `tests/tooling/test_guard_firing_log.py`

- [x] T07 FR-004: a finished, unsurfaced background run is reported at the next prompt and at turn
      end, with its exit status and age; an acknowledged one is not reported again
      research: procedure
      verify: a fixture with a finished run and an injected clock - reported, then acknowledged, then
      silent; and a RUNNING one is never reported as finished

- [x] T08 FR-005: `main-tree-hooks.sh` reads the session's `cwd` from the hook payload, so a write
      issued while STANDING IN main's tree is refused even with no `cd` in the command; a command that
      merely enters the mirror gets a free warning
      research: procedure
      verify: both shapes of the real incident as fixture cases, plus the correct-work half - a read
      from main, a write from a clone, a `git -C` read

- [ ] T09 `make audit` gains the reasons: "every escape taken, with what the session said", which is
      the report the GM described wanting
      research: procedure
      verify: against a seeded log

- [ ] T10 the whole guard suite and the gate, green together, then the push
      research: procedure
      verify: `make hooks-test` and `make done`, then `sync-with-main.sh done`
