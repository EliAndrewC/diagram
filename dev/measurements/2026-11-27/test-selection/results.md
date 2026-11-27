# What a builder's test run would save if it ran only the tests its change reaches (451 T342), 2026-11-27

Measured read-only from the clone's event log (`/diagram/.clones/diagram-backlog/.git/l7r-events/`, every feature's file),
the memory sampler's samples (`samples/mem-samples.jsonl` from 20:52Z, the hand logs `mem-samples*.log` before it), the gate's
run records (`dev/run-log/2026-11/`), the landing logs (`/home/agent/.claude/jobs/c6fd72d1/tmp/land-b*.log`) and the builders'
transcripts; plus one `make rust-test` of `rust/gate/crates/land` (the one build) and 24 direct runs of its test binary in pool
tree `diagram-backlog-t271`, beside the other builders (no load generator).

## 1. Every first-tier test phase in the pool trees

`runs.py` (output `runs.tsv`, one line a run): the `Phase` lines with `step: test` and `make` `rust-test` or `builder-checks`,
in the trees `diagram-backlog-t269`, `-t270`, `-t271` and `-b1`, from 2026-11-26T17:00Z to 2026-11-27T04:58Z (this task's own
runs left out), deduplicated across the feature files. The phases of one `builder-checks` call share a `t0` (its crates run at
once) and are merged into one run, its wall the latest end less the start. Load is the highest `load1` sample within 15 s of
the run (22 cores).

- 676 runs (476 `rust-test`, 197 `builder-checks`, 3 hung), 2026-11-26T17:19Z to 2026-11-27T04:54Z: 11.6 h.
- 3 runs over 300 s, all of the `rustc` crate, exit 101: 403 s (T285, 19:03Z), 600 s (T285, 19:46Z), 510 s (T292, 21:46Z),
  1,514 s together. A selection does not answer these (a hang in the selected module hangs the same); they are left out
  below. The pipe-hold class T364 names is a likely cause, not checked here.
- The other 673: 3,156 s of test wall (2,303 s `rust-test`, 853 s `builder-checks`); median 2.3 s, 90th centile 8.8 s.

| load1 at the run | runs | median s | 90th centile s | test wall s |
|---|---|---|---|---|
| under 8 | 170 | 1.68 | 5.55 | 468 |
| 8 to 22 | 310 | 2.26 | 6.17 | 1,336 |
| 22 to 44 | 132 | 3.42 | 10.19 | 655 |
| 44 and over | 54 | 7.92 | 24.8 | 673 |

By crate (single-crate runs): land 75 runs, 541 s, median 4.55 s; guard 79, 457 s, 5.29 s; shared 64, 437 s, 3.84 s;
measure 100, 366 s, 0.74 s; rustc 57, 230 s, 1.55 s; task 72, 178 s, 2.0 s.

## 2. Five real builder diffs: the share of a crate's tests in the modules they touched

`share.py` (output `share.txt`): each landed builder commit's `.rs` files, mapped to the crate's top module (for `rustc`, whose
tests live in `rustc/tests/<module>.rs`, that file too); tests counted by `#[test]` in the module's files against the crate's.
A file at the crate's root (`land.rs`, `plan.rs`, `rustc.rs`) reaches every module, so the conservative selection is the whole
crate there.

| commit | crate | modules touched | their tests / crate's | root file touched |
|---|---|---|---|---|
| 04f4c2b193 T424 | rustc | prewarm | 9 / 132 (7%) | no |
| 84e61811d4 T417 | land | writers | 9 / 155 (6%) | no |
| | shared | tree | 87 / 541 (16%) | no |
| | guard | guards::context_cap_hooks | 28 / 567 (5%) | no |
| 54aec28044 T419 | land | carry | 39 / 155 (25%) | no |
| | plan | approach | 14 / 204 (7%) | yes - whole crate |
| | task | builder_done | 11 / 131 (8%) | no |
| b991ec95f5 T355 | rustc | alone, kept, lint, slot, stale | 52 / 132 (39%) | yes - whole crate |
| 25ab6ec156 T413 | land | cheap, parity | 15 / 155 (10%) | yes - whole crate |

Mean share of the nine crate diffs: 14% by module; 41% where a root file's change runs the whole crate (3 of 9).

## 3. A filtered run timed loaded (`loaded-timings.txt`)

The land test binary run directly with no filter, `land::carry` and `land::writers`, alternated, 8 rounds:

| filter | tests | wall s at load1 34 (rounds 1-3) | wall s at load1 7-10 (rounds 4-8) | processor s (user+sys) |
|---|---|---|---|---|
| none | 155 | 9.16, 1.87, 2.02 | 1.68 to 1.79 | 22.8 to 24.6 |
| land::carry | 39 (25%) | 0.62, 0.73, 0.92 | 0.54 to 0.58 | 5.0 to 5.7 (22%) |
| land::writers | 9 (6%) | 0.19, 0.28, 0.17 | 0.18 | 0.7 to 0.8 (3%) |

The processor share follows the test-count share. The wall ratio, a round's filtered run against its whole-crate run, is 0.32
to 0.46 for carry (0.07 in the 9.16 s round) and 0.08 to 0.15 for writers. So the estimate takes the filtered run's wall as r
times the whole crate's: r = 0.46 for the LOW bound (carry's worst round, a quarter of the crate) and r = 0.15 for the HIGH
(the sampled module mean, 14%), with a floor of 0.25 s for a binary's start. The `make rust-test` run's build phase was 77 s
against a 7.3 s test phase (6.70 s of it the tests themselves): the saving is in the test phase only.

Commands, from the tree's crate directory `rust/gate/crates/land` (B the binary
`~/.cache/l7r-cargo-target/diagram-backlog-t271/debug/deps/l7r_gate_land-ec7d66c57b49c333`, built by
`make rust-test CRATE=rust/gate/crates/land FRESH=1 REASON="t342 loaded full-crate timing"`, 04:58Z):
`for f in "" land::carry land::writers; do /usr/bin/time -f "%e wall %U user %S sys" $B $f -q; done`, eight rounds, the load
read from `/proc/loadavg` before each.

## 4. The minutes a selection would save - an ESTIMATE

Per run, saved = wall - max(0.25 s, r x wall); the LOW bound also takes 3 of 9 diffs as saving nothing (a root file touched).
Over the 11.6 h window (`estimate.py`, output `estimate.txt`; the extraction is `python3 runs.py runs.tsv`, the shares
`python3 share.py <commits>` from the tree):

| what is filtered | runs | test wall s | saved, LOW (r 0.46, x 6/9) | saved, HIGH (r 0.15) |
|---|---|---|---|---|
| `rust-test` while iterating; `builder-checks` the whole crate (T342's design) | 476 | 2,303 | 828 s = 13.8 min | 1,942 s = 32.4 min |
| `builder-checks` too (the whole crate only at the batch gate) | 673 | 3,156 | 1,135 s = 18.9 min | 2,660 s = 44.3 min |

Of the `rust-test` figure, 5.6 to 13.1 min falls in runs at load1 22 and over (138 runs, 929 s), 8.1 to 19.0 min below it.
The median run saves 0.8 to 1.8 s. These are builder-minutes summed over four trees, on each builder's own path, not the
session's wall; the window is the measured working day (11.6 h), and it is not scaled to 24 h.

Limits of the estimate: it counts every pool `rust-test` run, including a run of a crate its builder was not changing (a
measurement's, or a crate run to check another's reach), which a selection would not narrow, so it leans high; and it treats
the whole test phase as filterable, where a run's fixed part (cargo's start, the binary's) is a few tenths of a second.

## 5. The risk: a test in another module the change breaks

- The batch gates. The landing logs hold each batch's LAST attempt only (each `land-bN.log` is rewritten per try): 21 logs,
  one red (b22, 04:48Z, `failed: tree moved`). The gate's run records hold every try: 17 red `make done` runs on 2026-11-26/27,
  13 of them from 17:00Z. Classed by the repair commit that followed each: coverage lines unreached 8 (T289, T298, T308, T293,
  T274, T300 twice, T307); two builders' changes meeting 1 (T334's test missing the `Env` field T274 added - a compile error,
  which a filtered run still catches, since it compiles the whole test binary); a time-of-day test 1 (T359, the `T01` match);
  a timing race or flaky test 1 (T414's pipe race and T423/T424's pre-warm ceiling); a tree moved 2. A builder's own change
  breaking a test in another module: 0. That is a FLOOR, not the rate under selection: builders run the whole crate today, so
  such a break is caught in the builder's tree before the gate.
- The builders' own runs. Failing test names are not kept in the event log or the tree; they are in the builders' transcripts
  (`builder-fails.py`, output `builder-fails.txt`: each builder's edited files from the event log's `writes`, keyed by its
  `by` id; a failing test is IN when its path's first two segments match an edited module, or a crate root the builder edited -
  a heuristic, and liberal where a root file was edited, as a selection would be whole-crate there). 33 builder transcripts
  from 2026-11-26T17:00Z hold a failing Rust test (`---- <test> stdout ----`): 75 distinct failing tests IN, 5 OUT. The 5 are
  4 `guards::*` tests in T365's run (a measurement of the guard binary under a slow TMPDIR, no file written) and 1
  `tempdir::tests` test in T370's, which the event log shows no write for but the transcript shows `tempdir/signals.rs`
  edited - IN. So of the 33 builders that saw a red test, none saw one only in a module of a changed crate it had not
  touched. Earlier figures in this task's working (16 OUT) came from a transcript-only edit list that missed writes made
  through make targets and were withdrawn.

## Verdict

FILED as T435 (the build clause of T342's own line, `make rust-test ONLY=`, filed apart so the measurement and the build are
two builders): the lowest bound, 13.8 minutes of builder test wall in the 11.6 h window, is well over a minute a day. The design
to build is the first row: filter only the iteration `rust-test` runs and keep `builder-checks` the whole crate at a builder's
end, which keeps the batch gate's exposure where it is today (0 cross-module reds of 13). Filtering `builder-checks` too adds
5.1 to 12.0 minutes; its risk measured as 0 of 33 red builders and 0 of 13 red gates, both floors while builders run the whole
crate. The three hung `rustc` runs (1,514 s) are worth more than either and are not
this lever's.
