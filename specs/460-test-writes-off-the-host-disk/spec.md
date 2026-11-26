# Feature 460: parallel test load freezes the host desktop - an evaluation

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-26

**Status**: Draft - filed to be picked up at a later date, not worked soon ("I do not want to work that feature anytime soon, but I would like to have it captured for picking it back up at some later date")

**Affects**: tooling

**Approved**: the GM, 2026-11-26, "please file a new speckit feature for an evaluation described in ~/.claude/sync-storm-findings-for-diagram.md - I do not want to work that feature anytime soon, but I would like to have it captured for picking it back up at some later date."

**Input**: `request.md` (the GM's words); `host-findings.md` (the host session's findings of 2026-11-26, copied whole - every
measurement of the host named below is its, with its method, and is cited by section, not restated here).

## Why

On 2026-11-26 a builder of this session, reproducing a test that failed under load (451 T304), ran looping copies of a test
binary as background load for over an hour, and during it the GM's desktop on the host froze for seconds at a time and his
dictation dropped words (`host-findings.md`, "What happened"). The host session measured the cause of the desktop's stalls as
disk writes, not memory or processor: the container's own filesystem shares the host's one journal, and the tests' throwaway git
repositories produced write bursts that filled the disk's request queue and slowed the journal's commits (`host-findings.md`,
"Cause, as measured on the host"). Whether the dictation gaps had the same cause is NOT established (`host-findings.md`, "Not
measured"). No limit applied from the host fixed it (`host-findings.md`, "What was tried on
the host, and what it showed"), so a fix has to be in what the tests write, or where.

By the host session's account (`host-findings.md`, its opening paragraph), the GM has decided this is not urgent - the trigger
was an unusual hour of deliberate load - and wants the option of fixing it costed, starting with how big the tests' temporary
files get. His own words on it are `request.md`'s: captured now, not worked soon.

## What this feature is

An EVALUATION, to be run when the feature is picked up: measure first, then say what a fix would cost and whether it is worth
building. It decides nothing here.

## What the diagram session can measure (`host-findings.md`, "What the diagram session can measure")

1. The peak size of the tests' temporary files: where the `land` crate's tests create their repositories, and that directory's
   size sampled during one copy of the suite and during the load of `host-findings.md`, "What happened". By the host session's
   account this is the figure the GM asked for: it decides whether a memory-backed directory fits under the container's memory
   limit. (This spec's reading, not the findings': any other suite that makes throwaway repositories is measured too, since a
   directory set as the tests' `TMPDIR` has to hold every suite that writes there.)
2. Syncs against file churn: the `fsync`, `fdatasync` and `sync_file_range` calls of one run of the suite, counted; and
   whether git in the tests runs with its default `core.fsync` - a check that needs no tracing and decides whether a git
   setting could help at all. The findings name `strace` for the count; `strace` is refused in this container
   (`specs/451-time-retro-and-efficiency/plan-done.md`: T39 "`strace` is refused here with no `CAP_SYS_PTRACE`", T40 and T87
   the same, measured 2026-11-20 and 2026-11-21), so the count may need another route or the host's help.
3. Files created and deleted in one run, as a rough count.

The host's own stall measurement is not available inside the container (`host-findings.md`, its last paragraph): the GM or the
host session runs it while a candidate fix is under load.

## The candidates the findings name (none chosen here)

- The tests' throwaway files in a dedicated, size-capped memory-backed directory in the container, the tests' `TMPDIR`
  pointed at it - untested; its constraints (it counts against the containers' shared memory limit; only the tests' own
  directory, not the whole of `/tmp`; a change to the host's launcher, proposed through the host-script proposal process, and
  existing containers recreated) are in `host-findings.md`, "What a fix would look like".
- The cheaper alternative: a cap on how many copies of a suite run at once.

## What already bears on it in this repository (2026-11-26)

- 451 T321 (filed the same day, open): a helper for reproducing a failure under load that takes a stated number of copies and
  a hard time limit, and the builder brief's rule that a task which must load the machine runs alone in its batch. It limits
  how long such a load runs and makes its copy count a stated choice; it sets no count below the stall threshold, which the
  findings call unknown. This evaluation says what count, if any, is safe, and whether more is wanted.
- 451 T284 (landed): the machine-wide build slot is held around every cargo call of the gate that compiles, for that call's
  whole length, `cargo test` and its run included (`rust/gate/crates/rustc/src/rustc/slot.rs`), so the suites the GATE runs are
  limited by the slot count, loosely (a wait past its ceiling runs without a slot). It does not reach a test binary run
  directly, as the looping copies of 2026-11-26 were.
- 449 T101's leak pin (`rust/gate/crates/rustc/src/rustc.rs`, `leak_checked`) already gives each crate's gate-run tests their
  own `TMPDIR` under `/tmp`: the place a memory-backed test directory would change, though a binary run directly bypasses it.
- 451 T312 and T143 (open): tests that read or write the machine's live state.

## To settle when the feature is worked (not decided here)

- Which suites write throwaway repositories, where, and how large at peak.
- Whether syncs or directory churn dominates, which decides whether a git setting could help at all.
- Whether a memory-backed test directory fits under the memory limit beside the builders' own use, and what size.
- Whether a cap on concurrent copies is enough by itself, and where the threshold lies between the copy counts the findings
  name.
- What the host's stall probe shows under a candidate fix.
- Whether the dictation gaps had the same cause as the desktop's stalls - the host's to establish (`host-findings.md`, "Not
  measured").

## Review history

- spec-fidelity round 1 (2026-11-26, MODE 2): CHANGES REQUIRED, 9 items - "filled it" said the repositories filled the journal where the findings' Cause says the request queue; the dictation cause ("Not measured") not carried; the GM's position and "the figure the GM asked for first" stated as his where they are the host session's account; measurement 1's load loosened to "many-copy" and its other suites unmarked as this spec's reading; measurement 2 dropped the core.fsync check and two of the three sync calls; strace's refusal cited to a report not in the repository (now 451 plan-done T39, T40, T87); T284 said to bound compiles only where its slot holds every compiling cargo call, cargo test included; T321 said to bound the trigger where it bounds duration and requires a stated count; the title named one candidate. Fixed the same day, each as the round asked; its aside on 449 T101's per-crate TMPDIR taken into "What already bears on it".
- spec-fidelity round 2 (2026-11-26, MODE 3): FAITHFUL - all nine round-1 items resolved: the request-queue cause, dictation marked unestablished and added to To settle, the GM's position attributed to the host session's account, measurement 1's load named and its other-suites clause marked as this spec's reading, measurement 2's three sync calls and core.fsync check, strace cited to 451 plan-done T39/T40/T87, T284's slot over every compiling cargo call but not a directly-run binary, T321's limits without a safe count, and the title naming the problem; the new 449 T101 leak-pin bullet checked against rustc.rs leak_checked.
