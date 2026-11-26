---
kind: adopted
title: a memory and load sampler runs while builders hold pool trees
for: the number of builders at once is certified against the container's 10 GiB limit from samples that exist without a session remembering to start them, read by the count of pool trees held
measured: 2026-11-26
measurement: the real sampler in the clone diagram-backlog, 20:52:11 to 21:02:51 UTC, four pool trees held - 65 samples in 10.7 minutes, each ten seconds after the last to the second, for 0.06 s of CPU (6 clock ticks, utime and stime of its /proc stat: 0.9 ms a sample, 0.34 s an hour), 7.2 MiB resident, 18,036 bytes written (277 a line); its report's sampled memory.current peak 9.49 GiB under the cgroup's memory.peak of 9.99 GiB; a start read through a pipe returned in 0.39 s; the report over the three hand logs kept from the shell loop gives the figures recorded for them (two builders: 236 samples, anonymous median 1.91, 95th 5.66, peak 6.34 GiB, 4.4 s of memory stall; three: 292 samples, median 2.49, peak 6.39, 6.1 s)
command: make sampler (running or not, lines, size); make sampler-report [SINCE=<ISO UTC>] [UNTIL=<ISO UTC>]; make sampler-report LOG="$(echo dev/measurements/2026-11-26/builder-count/mem-samples-*.log)" (the 2026-11-26 baseline); awk '{print $14+$15}' /proc/$(cut -d' ' -f1 "$(git rev-parse --path-format=absolute --git-common-dir)/l7r-sampler.pid")/stat (its CPU, clock ticks); make rust-test CRATE=rust/gate/crates/measure (measure::sampler::tests)
falsifier: the sampler's own cost showing in make task-time (a category or a program's minutes that are the sampler's), its CPU past five seconds an hour of sampling, a report that disagrees with the cgroup's memory.peak (its line "memory.current: sampled peak ... DISAGREE", or memory.peak risen in a window far past the sampled peak, which is a spike between two samples), a batch of builders found unsampled, or two samplers of one clone alive at once
threshold: one DISAGREE line, one batch of builders with no samples in its window, or the sampler's CPU over 5 s an hour (any reopens it); memory.peak risen more than 1 GiB past the sampled memory.current peak in a window reopens the interval, L7R_SAMPLE_S
cost: one process a clone for at most twelve hours a start, 7.2 MiB resident; a sample is ten small reads of the cgroup's files and /proc, one read of the pool registry and one comm file a process (41 processes here), 0.9 ms of CPU; at most 8 MiB of samples a clone (two files of 4 MiB); a handout runs one more program, the start, 0.39 s where it starts a sampler and less where one runs
last-audited: 2026-11-26
cadence-days: 30
covers: rust/gate/crates/measure/src/measure/sampler.rs
covers: EVERY_S
covers: MAX_H
covers: MAX_BYTES
covers: MARGIN_GIB
covers: GAP_S
---

451 T274 (`rust/gate/crates/measure/src/measure/sampler.rs`, its report `sampler/report.rs`; asked for by every handout in
`rust/gate/crates/task/src/builder_tree.rs`). `docs/process-decisions.md`, "Two code builders at once": the count of builders
is the largest that still shortens total time with peak memory under a margin, and on 2026-11-26 the memory half was a shell
loop the coordinating session started by hand - the two- and three-builder code runs were sampled, the three- and four-at-once
comment batches were not. `make builder-tree` now asks `l7r-gate measure sampler start` at every handout, which starts the
clone's one sampler where none is running; `make sampler-start`, `make sampler-stop` and `make sampler` are the same by hand,
and `make sampler-report` reads a window.

**The knobs.** The interval (`L7R_SAMPLE_S`, 10 s) is the hand loop's, kept so the kept logs and the sampler's compare sample
for sample; it is the knob to lower if `memory.peak` rises past what the samples saw. The hours (`L7R_SAMPLE_MAX_H`, 12) are a
GUESS: longer than any batch run so far, so a sampler nobody stops still ends. The size bound (4 MiB) is arithmetic: a line is
about 280 bytes with four trees held, a twelve-hour run 4,320 lines and about 1.2 MB, so one file holds about 42 sampled hours;
a start that finds the file past the bound moves it to `mem-samples.1.jsonl` and begins a new one, so sampling never ends for
good at the bound and a clone keeps at most 8 MiB. The margin (`L7R_MEM_MARGIN_GIB`, 7) is a GUESS knob: 3 GiB under the limit,
the figure the 2026-11-26 runs were read against. The gap (120 s) is a GUESS: twelve of the default interval.

**Where the samples are.** `<git common dir>/l7r-events/samples/mem-samples.jsonl`, a folder of its own under the event logs'
directory and not a file beside them: every reader of `l7r-events/` takes a `.jsonl` there for a feature's event log (the
hook's launch lookup scans the most recently written first, `make task-time` and the step-back bundle read each, and
`make speckit-todo` calls a clone active by the newest file's time), and none descends into a folder.

**What a row means.** A row of the report is the samples at which that many pool trees were HELD by the registry. A held tree's
builder may be reading, waiting on a review or gone, so a row is "at most N builders at work"; the `rustc` column and the load
say how much was compiling. A count certified from a row needs the batch to have been at work for the window it names.

**What the sampler does not write.** No `Phase` line and no event-log line: it is in no task's time and `make task-time` shows
none of it, which is the falsifier's first clause read the other way - if it ever does show there, something started it per
sample.

Weighed and not taken: a sampler inside the guard's hooks (a sample only when a tool runs: no samples through a long compile,
which is where the peaks are); one sampler for the machine (the registry it reads is a clone's, and the pid file's home would
be outside every clone); `make` or a shell loop a sample (a process a sample, against a read); keeping every file ever written
(the kept baselines are copied into `dev/measurements/` when a decision cites them).
