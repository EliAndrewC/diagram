# Tasks: Escapes That Mean It (feature 169)

Every task is `research: procedure` - this feature changes how guards match their own escape tokens
and what the tooling reports about itself. Nothing here decides how a place was built, farmed or
lived in, so no task carries the physical checkboxes. The GM's words are in [`request.md`](request.md),
the measurements in [`research.md`](research.md).

- [x] T01 baseline: `make hooks-test` and `make done` green before any edit, so anything red after
      is this feature's
      research: procedure
      verify: both green on 2026-08-30 at the close of feature 168, same tree

- [x] T02 FR-001: `escape_used()` in `scripts/_hookmatch.py`, with the `escape <TOKEN>` CLI mode -
      heredoc bodies and quoted strings blanked (the existing `sanitize`), search-command segments
      dropped, `for VAR in ...` word lists dropped
      research: procedure
      verify: ten hand cases, five mentions and five real escapes, each through the CLI; and the
      first run of that check proved nothing because it fed raw text to a JSON entry point - both
      halves returned empty and the mentions "passed" for the wrong reason (R2)

- [x] T03 FR-001: the escape branches of `gate`, `measure`, `no-poll`, `discard`, `no-branch` and
      `pair` (Bash side) route through it, and `classify()`'s own `GUARD_EDIT_OK` substring test does
      too - a grep for that token used to classify a whole command as `ok`
      research: procedure
      verify: each guard driven with a real escape and with a grep for its token; `bash -n` on all six

- [x] T04 FR-001: `HOST_GIT_OK` in `repo-safety-hooks.sh` - found by the round-2 spec review, not by
      me. Matched against the RAW command while the sanitized copy built fourteen lines above sat
      unused, so a mention disarmed the `/host-l7r-repo` mount guard
      research: procedure
      verify: five directions - a plain host write blocks, a real escape permits, a write after a
      GREP mention still blocks, the two no-escape rules are untouched, an ordinary clone commit is
      untouched; `test-repo-safety-hooks.sh` 20/20. **Blanking quotes alone did NOT fix it** (R3)

- [x] T05 FR-002: a mention no longer resets `measure`'s repeat-measurement counter or removes
      `gate`'s state file, because those live on the escape branch that now requires a real escape
      research: procedure
      verify: the same drives as T03; the state writes are unchanged on the real-escape path

- [x] T06 FR-003: `test-review-gate.sh` isolates `GUARD_LOG_DIR`, hung off the `$T` it already traps
      research: procedure
      verify: 24 of the live census's 113 entries were its `specs/900-x` fixtures before the change

- [x] T07 FR-003/FR-004: both hand-lists become DERIVED checks - every guard that calls `guard_log`
      must give every call a rule slug (unless it has exactly one acting branch), and every suite of
      a recording guard must isolate the log, following one level of delegation to the shared runner
      research: procedure
      verify: `tests/tooling/test_guard_firing_log.py`; the derived checks found two things a hand
      list had missed - the three suites that isolate via `test_hooks_cases.py`, and `no-poll`'s
      escape silently broken by `$HERE` vs `$NP_HERE` (R4)

- [x] T08 FR-004: `guard-file`'s Read reminder records a `read-reminder` slug; its 56-firings-a-day
      volume is reported and deliberately not changed
      research: procedure
      verify: the derived slug check; the volume question is recorded for the GM in FR-004

- [x] T09 FR-005: `mirror_refresh` fails when the mirror's HEAD is not contained in its
      `origin/main`. `--ff-only` does NOT catch this - it fails on DIVERGENCE, and a mirror merely
      AHEAD by a stray commit satisfies it and prints "Already up to date"
      research: procedure
      verify: `test-sync-with-main.sh`, 47 checks green; the mechanism in R5

- [x] T10 FR-006: `scripts/main-tree-hooks.sh` - a `cd` into the mirror root that then writes is
      refused; reads, clones, `git -C`, mentions and the escape are not. Registered in
      `.claude/settings.json`; `hooks-test` picks it up by glob and demands its companion
      research: procedure
      verify: `scripts/test-main-tree-hooks.sh`, 17 cases in five sections, including BOTH real
      incidents of 2026-08-30 in the shape they took; proved to fire by neutering the block in a copy
      and watching the case pass

- [x] T11 FR-006: the warrant is stated truthfully - this does NOT meet `CLAUDE.md`'s reopening
      condition, it is neither declined candidate, and the 2026-08-17 rule stays unenforced
      research: procedure
      verify: spec-fidelity round 1 caught the false claim; the corrected text is FR-006

- [x] T12 SC-007: the close-out report tells the GM that FR-006's original warrant was wrong, in
      terms plain enough for them to withdraw item 5
      research: procedure
      verify: the report itself - the one requirement here that no test can tick

- [x] T14 spec-fidelity round 3 returned CHANGES REQUIRED (a twelfth token), which under Principle
      XVI is an ESCALATION to the GM rather than a fourth self-review round. The mechanical remedy
      the reviewer named is implemented rather than argued - the census is DERIVED - and the two
      decisions that remain theirs go in the close-out report
      research: procedure
      verify: R10; the review history in `spec.md`; both new checks proved to fire

- [x] T13 the whole guard suite and the gate, green together, then the push
      research: procedure
      verify: `make hooks-test` exit 0 and `make done` exit 0 together, after one red round
      that `pair-hooks` caught (R8); then `sync-with-main.sh done`
