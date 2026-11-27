# Which test hung in each long rustc test run, and whether it can happen on HEAD (451 T445), 2026-11-27

Measured read-only: the clone's event log (`/diagram/.clones/diagram-backlog/.git/l7r-events/`, every feature's file, the
`Phase` lines of step `test`), the memory sampler's samples (`samples/mem-samples.jsonl`), the builders' transcripts and the
coordinating session's (`/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl` and its
`subagents/`), the builders' scratch logs, and the code at each commit (`git show`). No source changed, no test run; one shell
run of the stand-in cargo's script (section 3).

Scripts: `find.py` (each `make rust-test` / `builder-checks` Bash call in the transcripts inside a time window), `dump.py` (one
transcript's calls, results and text between two times), `hangs.py` (section 4). Copied failure blocks: `failures.txt`.

## 1. The four hung runs, and the test that held each

T342 found three by the pool trees' `Phase` lines; the clone's own lines hold a fourth of the same kind. In each, the test
binary was alive for the whole phase: libtest's own `finished in` is within 3.1 s of the phase's wall.

| # | phase start (UTC, 2026-11-26) | tree | phase wall s | libtest `finished in` s | whose run | the test that held it |
|---|---|---|---|---|---|---|
| 1 | 19:03:32 | diagram-backlog-t269 | 403.06 | 399.95 | T316's builder (`agent-a62d36270f44f3749`), its first check of new code | `a_call_waiting_on_a_slot_takes_its_slot_and_it_builds_the_crate_again_after` and `a_real_run_in_its_tree_ends_it_at_once` |
| 2 | 19:46:30 | diagram-backlog-t269 | 600.25 | 600.18 | T316's closing builder (`agent-a6b0c4481546c968b`), a red-first run with `slot.rs` broken by hand | `it_holds_a_slot_only_while_another_is_spare_and_builds_the_crate_again_after` |
| 3 | 21:46:25 | diagram-backlog-t270 | 510.25 | 510.14 | T336's builder (`agent-a872dd3f7792cabc5`), a red-first run with the old `prewarm.rs` put back | one of three that panicked at `prewarm.rs:135` - INFERRED from the code as `it_starts_a_crate_only_while_a_slot_is_spare_and_never_cuts_the_one_in_flight` |
| 4 | 22:10:52 | diagram-backlog (the clone) | 543.4 | 543.41 | the session's `builder-checks` during T334's landing, on landed code | `it_starts_a_crate_only_while_a_slot_is_spare_and_never_cuts_the_one_in_flight` |

Together 2,057 s (T342's three: 1,514 s). The task each `Phase` line names (T285, T292) is the clone's started task, not the
tree's holder: that defect is filed already as T332.

All four are one class, in the then-new pre-warm tests (`rust/gate/crates/rustc/src/rustc/tests/prewarm.rs`, 451 T316):

- **The stand-in.** `SLOW`, a fake cargo that loops `sleep 0.05` for as long as a `slow` file lies beside it. Until 390a2914fa
  (2026-11-26 22:21Z) the loop had no bound.
- **The shape.** A test writes `slow`, spawns the pre-warm run in a `std::thread::scope`, asserts inside the scope, then removes
  `slow`. If an assertion fails before the removal, the panic unwinds into the scope, the scope joins the spawned run, and that
  run waits on a stand-in that never ends.

What each transcript shows:

- **Hang 1.** `pstree` of the test binary (pid 1879053) at 19:10:11Z showed two stand-ins looping in `cargo --version`, in target
  directories -151 and -156. `SLOW` looped on every call, `--version` too, which the build key reads. The builder removed both
  `slow` files at 19:10:14Z and the phase ended at 19:10:15Z. Then `a_call_waiting...` panicked on `remove_file` (NotFound:
  the builder had already removed it) and `a_real_run...` failed its 120 s assert. The other three failures were fast asserts.
  The fix was made the same minute in the uncommitted code: `[ "$1" = test ] &&`.
- **Hang 2.** `it_holds_a_slot...` failed its own 60 s assert at line 179, inside the scope. The scope then joined the run,
  whose ceiling was the test's `knobs(600_000)`, 600 s. That version (1783cf6eed, line 166) cut a build at its ceiling, which
  ended the run at 600.18 s.
- **Hang 3.** Five failed. The three pre-warm ones panicked at line 135 (`still_building`: the old code had cut the build,
  code 130), each inside its scope. One `slow` file was left (target directory -129), and the builder removed it at 21:54:55Z.
  The log does not say which test owned -129. INFERRED from the code (f5007f94d3): under the old code a real run's stage ended
  the pre-warm, and the 50 ms ceiling ended the ceiling test. Only `it_starts_a_crate...` went on to its second crate's `SLOW`
  build with `slow` still there.
- **Hang 4.** `it_starts_a_crate...` failed `real.hold.is_some() && real.waited.is_none()` at line 190, inside the scope. That
  was a race: the pre-warm's own look for a spare slot holds the slot's lock. The session removed `slow` at 22:19:55Z. Three
  reruns took 1.28 to 1.32 s, green. 390a2914fa dropped the racy half and bounded `SLOW` to 600 polls.

## 2. Not the pipe-hold class 451 T364 fixed

T364 (e2e186676b, committed 2026-11-27T05:24:05Z) made `run_in` (`rust/gate/crates/rustc/src/rustc.rs`) wait on the child with
`child.wait()` and then drain its pipes (`drain.rs`). Before it, a process the binary left behind, holding stdout, held the phase
after the binary exited. Here the binary itself had not exited: libtest's `finished in` matches the phase wall (section 1), and
hangs 1 and 3 show the binary alive (`ps` / `pstree`, `etime` 08:30 at 21:54:55Z). `run_in` puts no cap on a program that is
still running, before T364 or after it. So T364 covers none of the four, and neither would a fix in `run_in`.

## 3. Can it still happen on HEAD (aefcced086)?

The unbounded hold cannot. Reading the code (not run):

- `SLOW` stops after 600 polls (`i -lt 600`) and only runs for `test` builds (390a2914fa).
- The three scoped tests still assert inside the scope before removing `slow`, under a `knobs(600_000)` ceiling. Those are
  `a_real_run_in_its_tree_ends_it_once_the_build_in_flight_is_done`, `it_starts_a_crate_only_while_a_slot_is_spare_and_never_cuts_the_one_in_flight`
  and `the_ceiling_passing_mid_build_ends_it_after_that_build`.
- So a red assertion there still holds the suite for every `SLOW` build the run asks while `slow` remains. A moved `a` asks two
  (`a`, then `b`). The bound is a poll count, not wall time.

The stand-in's script run alone with `slow` present, measured 2026-11-27 with `/usr/bin/time` (load1 31.2 before, 25.0 after,
22 cores): **44.45 s** for one `test` build, and 0.00 s for `--version`. So on HEAD a red in one of those three tests costs
about 45 to 90 s at load 25 to 31, against the crate's median test phase of 1.59 s. It costs more at the loads of hang 1
(load1 263). This is DERIVED from reading the code and that one timing, not reproduced: this task changes no source. Filed as T454.

## 4. Long test phases of any crate since T364's commit

`hangs.py` (output `hangs.txt`) takes every `Phase` line of step `test` in the clone's event log, from any tree, any make target
and any feature file, deduplicated: 4,779 phases, 2026-11-20T11:57Z to 2026-11-27T06:51Z. A phase is far past its crate's
median when it runs over max(60 s, 10 x that crate's median test phase), the median taken over the whole log. The cutoff is
T364's commit time, 2026-11-27T05:24:05Z. A pool tree gets T364 only at its next handout, so a phase soon after the cutoff may
still run the old `run_in`.

- Before the cutoff: 4,658 phases, 20 far past, 3,853 s, the four hangs of section 1 among them.
- Since the cutoff: 121 phases, 3 far past, 924 s. None is a hang:

| phase start (UTC, 2026-11-27) | tree | crate | phase s | libtest `finished in` s | code | what it was |
|---|---|---|---|---|---|---|
| 05:35:55 | diagram-backlog-b1 | guard/shared | 757.4 | 757.00 | 0 | T392's builder (`agent-a971c2f01efbdb490`) ran a temporary test, `t392_differential`, over a copy of all 34 real event logs: a measurement run through `make rust-test`, removed after it |
| 05:32:02 | diagram-backlog-t271 | land | 101.8 | 100.24 | 0 | green, slow inside the test binary, load1 29.7 to 85.3 |
| 06:16:46 | diagram-backlog-t271 | land | 64.6 | 64.41 | 0 | green, slow inside the test binary, load1 11.1 to 28.8 |

No rustc test phase since the cutoff ran over 17.1 s (9 phases, median 3.21 s).

The land crate's green tail recurs. Before the cutoff, four more land phases ran 61.0 to 79.4 s with code 0 (2026-11-26T01:11Z,
06:08Z, 07:00Z and 2026-11-27T04:55Z, `hangs.txt`), against a median of 4.04 s. Its cause is not measured here: it is not a hang
(each binary finished green) and not this class (land has no `SLOW` stand-in, and no 60 s wait was found in `src/`). Filed as a
measurement, T455.

## 5. Verdict and what was filed

- All four long rustc runs were held by pre-warm tests that failed an assertion inside a `thread::scope`, while the stand-in
  cargo looped on its `slow` file. Hang 2 was bounded by its test's 600 s ceiling.
- Three of the four were the builders' own red runs of new or deliberately broken code (1, 2, 3). Only hang 4 was on landed code
  (a race). The fixes already landed are 390a2914fa (the `SLOW` bound and the race) and the `--version` exemption, part of
  1783cf6eed as landed.
- T364 covers none of them. On HEAD the hold is bounded at about 45 to 90 s a red. The remaining fix, filed: remove `slow` on
  drop and give the scoped runs a 60 s ceiling: T454.
- The land crate's 61 to 100 s green test phases (6 of them), cause unknown: filed as a measurement, T455.
