# Tasks - 210 The roll leaves the worker

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` (tooling; nothing physical).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 5 of 5 (the cap). Rounds 1-4 each found the every-roll boundary or the roll-out list short of the code: generate() only -> build() only -> the regen site missing -> three STAGES-iterating tools missing -> a token form missing enumerate(). Same shape every time: a hand-enumerated surface; fixed each time by deriving it. Recorded in the spec's Status
- [x] T02 `clearance.reset()` and `trim_heap()`, called when `generate()` ends (FR-001, FR-002); tests
      research: rendering
      verify: DONE. DONE. clearance.reset(); _memory.trim_heap() (ctypes malloc_trim, False never an exception); driver.roll_scope() context manager whose exit calls both, around build()'s two stage loops and the three tools' loops (perf_snapshot.measure, perf_profile.profile_stage, placement_stages._walk - the plate loop lifted out so the scope wraps exactly it); tests: reset forgets the index (test_clearance), trim True here and False without libc (test_memory), build() clears the memo and trims on success and when a stage raises, and the AST test that every stage-running loop under l7r/ sits in a roll_scope with the attribute-reading comprehension named as the excluded shape (test_driver); 2+5+13 passed
- [x] T03 `hamlet()` rolls in a coverage-recording child (FR-003); the `recorded=` producer; tests (FR-005)
      research: rendering
      verify: DONE. DONE. rollcache._hamlet_payload (lifted from hamlet()'s closure), _CHILD_DRIVER, _hamlet_in_child (spec by pickle in, (payload, deps) by pickle out; coverage run --parallel-mode under a COV_CORE_SOURCE parent with the hooks stripped and the data file published as .coverage.rollchild-*; plain otherwise; a failing child raises with its stderr); obtain/_produce_and_store take recorded= and every serving mode is unchanged; hamlet() passes both. Tests: recorded= stores the record it brings and the next call hits, a failing child raises, coverage file only under a covered parent (test_rollcache, 19 passed); the child rolls the same hamlet as in-process - manifest identical as JSON, plan fields equal, the record names hamletgen functions (tests/full/pipeline/test_rollcache_child.py, 31 s)
- [ ] T04 measure after: one roll-heavy file on one worker, then the full run's per-worker census (FR-006);
      research R5
      research: rendering
- [ ] T05 the record (FR-007): the roll-out list, `pipeline/CLAUDE.md`, `dev/performance.md`
      research: rendering
- [ ] T06 `make done` green with the floors (SC-002); land GATED
      research: rendering
