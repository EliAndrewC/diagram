# Tasks: Lint First, and a Firing Log Worth Mining (feature 168)

Every task is `research: procedure` - this feature changes the order of the gate's own phases and
what the guards RECORD about themselves. Nothing here decides how a place was built, farmed or lived
in, so no task carries the physical checkboxes. The GM's words are in [`request.md`](request.md), the
measurements in [`research.md`](research.md).

- [x] T01 baseline: `make done` and `make hooks-test` green on the unmodified clone
      research: procedure
      verify: hooks-test 19 suites exit 0; the gate green before any edit, so anything red afterwards
      is this feature's

- [x] T02 FR-001: `make done` runs `lint`, `format` and `typecheck` BEFORE `reference`; a failure in
      any of them is reported without the map roll having happened
      research: procedure
      verify: planted an unfixable syntax error - the gate goes red in **2 s** where it took ~31 s
      before, and the failure message says the roll has not happened

- [x] T03 FR-001: the saving is recorded HONESTLY at the point of change - 8 of 317 recorded gate
      runs failed a static phase without also failing the suite, so this is worth ~29 s on 2.5% of
      runs and is done on principle
      research: procedure
      verify: the note in the Makefile phase loop, and R1

- [x] T04 FR-002: derive the in-scope set from `scripts/*-hooks.sh` plus `review-gate.sh` rather than
      from a list, and rule `idle-tests` out of class in writing
      research: procedure
      verify: spec FR-002's table was built by asking each script, after `spec-fidelity` round 1
      caught a hand-list that had gone stale inside this very session (R2)

- [x] T05 FR-002/FR-003: every acting branch of every in-class guard records, with a rule slug -
      `make-only` (5 verdicts), `no-poll` (3), `repo-safety` (3), `clone-sync` (5), `pair` (5),
      `review-gate` (4), `gate` (2), `guard-file` (2), `no-branch` (2), `discard` (2), `batching`,
      `readme`, `source-block`, `agent-stall`
      research: procedure
      verify: `tests/tooling/test_guard_firing_log.py` drives 12 of them through the REAL hook with a
      real payload and asserts the `(event, rule)` pair on the entry that lands; a grep would have
      proved only that a call site exists

- [x] T06 FR-003: `_guardlog.sh` takes the rule as a fourth field, defaulting to the event so a
      single-branch guard needs nothing
      research: procedure
      verify: the same suite, plus a static test that no multi-branch guard logs without a slug

- [x] T07 FR-003: the escape is a branch - each of the nine escape tokens produces an `escaped`
      entry. `SOURCE_EDIT_OK` needed the guard's python to ANNOUNCE the escape, because it was
      printing a verdict indistinguishable from "nothing to guard here"
      research: procedure
      verify: R3; `test_the_gm_s_source_block_records_both_the_refusal_and_the_escape` asserts the
      escape records AND still permits (exit 0)

- [x] T08 defect found while auditing (Principle XIV): `readme`, `source-block` and `guard-file`'s
      Read reminder guard the Edit/Write/Read tools, which carry no `command`, so all three recorded
      an EMPTY detail. `guard_cmd` falls back to `file_path`
      research: procedure
      verify: R4; the new test asserts a non-empty detail on the `source-block` block

- [x] T09 FR-004: `make audit` prints the per-rule breakdown for any guard with more than one rule,
      and prints as before for a single-rule guard and an empty log
      research: procedure
      verify: against a seeded log - `no-poll blocked=3, escaped=1 escape rate 25%` followed by
      `by rule: busy-wait-loop=2, poll-ok=1, disguised-sleep=1`

- [x] T10 FR-005: every companion suite of a newly-recording guard isolates `GUARD_LOG_DIR`;
      `test-agent-stall-hooks.sh` hangs its log off the `TMP` it already traps rather than adding a
      second EXIT trap
      research: procedure
      verify: R5 - running the suites of every recording guard leaves the real log at 91 entries,
      unchanged

- [ ] T11 the whole guard suite and the gate, green together
      research: procedure
      verify: `make hooks-test` all suites green; `make done` green; recorded in the commit
