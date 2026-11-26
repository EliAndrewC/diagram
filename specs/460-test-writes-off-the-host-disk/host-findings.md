# The host session's findings (copied whole)

The file below was written 2026-11-26 by the host troubleshooting session (the repository `this-laptop`) and left at `~/.claude/sync-storm-findings-for-diagram.md` in the container for this feature. It is copied here unchanged, as that file asks; its measurements are the host session's, made on the host, and its "Not measured" section says what is not established.

---

# Findings for the diagram session: parallel test load freezes the host desktop

**Delete this file once its contents have been moved into a SpecKit feature** (the feature's spec or
research notes). It is a one-time handoff, not a standing doc. In the container it is at
`/home/agent/.claude/sync-storm-findings-for-diagram.md`.

Written 2026-11-26 by the host troubleshooting session (this-laptop). Eli has decided this is not urgent:
the trigger was an unusual hour of deliberate heavy load. He wants the option of fixing it costed, starting
with how big the tests' temporary files get.

## What happened

On 2026-11-26 from about 12:40 to 14:07 the diagram session ran 12 looping copies of the test binary
`t304-land-after` (the `land::*` suite, 24 threads per copy) as background load, to reproduce tests that
fail only under load. During that time the host desktop ignored clicks and keys for a few seconds at a
time, over and over, and Eli's voice dictation dropped words.

## Cause, as measured on the host

The desktop was not short of RAM or CPU. It was waiting on disk writes.

- The container's own filesystem (everything that is not a bind mount, including `/tmp`) is an overlay on
  the host's single ext4 filesystem. That filesystem has one journal, shared by the host desktop and every
  container.
- The tests create, push to and delete throwaway git repositories. Under 12 copies this produced bursts
  with about 170 `git` processes alive at once. In those bursts the SSD's request queue filled (190 to 380
  requests in flight; its limit is 256) and the write rate fell to about 300 per second.
- Journal commits then took seconds. The desktop shell's main thread saves small files through the same
  journal and sat blocked in `jbd2_log_wait_commit`, for up to about 20 s at a stretch.
- A 4 KB write followed by `fsync` from the desktop side took up to 14.7 s. On a quiet laptop it takes
  under 0.2 s.

Numbers during the storm:

| Measure | Value |
|---|---|
| Load average | 250 to 320 (22 CPUs; mostly threads blocked on disk, not running) |
| RAM available on the host | about 9.6 GB |
| Memory pressure | near zero |
| Desktop CPU pressure | under 1.5% |
| Container threads blocked on disk at any moment | 150 to 260 |
| Container disk writes since boot (43 hours) | 1.17 TB |

## What was tried on the host, and what it showed

Each was applied live to the containers' cgroup during the storm, then reverted.

| Limit | Result |
|---|---|
| Existing disk and CPU priority weights for the desktop | No help. The desktop is not losing a race for the disk; it waits on a commit that carries the containers' writes. |
| Write-rate cap (400 writes per second) | Worse. Typical desktop sync latency tripled and a 14 s stall still occurred. Do not propose this. |
| CPU quota of 6 CPUs for all containers | Partial. Without it, all four 100 s rounds had a stall of 3.5 to 5.5 s. With it, two of three valid rounds had none over 0.6 s and one had a 6.2 s stall. It works only by slowing the tests. |

So no host-side limit fixes this. The fix has to be in what the tests write, or where.

## Not measured (do not treat as established)

- **Whether syncs or file churn dominates.** The container's blocked threads were mostly in directory
  operations (`iterate_dir`, `do_rmdir`, `vfs_unlink`, `filename_create`), fewer in commit waits. Creating
  and deleting thousands of files fills the journal even with no `fsync` at all. Nobody checked whether git
  or the test helpers call `fsync`. If deletes dominate, `git -c core.fsync=none` would do nothing.
- **Where the tests put their temporary repositories.** Probably under `/tmp` (`TMPDIR` is unset in the
  container), but this was not confirmed from the test source.
- **How big those temporary files get at peak.** The loop had ended before anyone measured.
- **Whether the dictation gaps had the same cause.** The timing fits; the voice path was never caught
  blocked.

## What a fix would look like

The candidate is to keep the tests' throwaway files off the host disk: a dedicated, size-capped tmpfs in
the container, with the tests' `TMPDIR` pointed at it. Files on a tmpfs never touch the journal, so this
holds whether syncs or deletes dominate. It is untested.

Constraints to design around:

- **Memory cap.** All containers share a 10 GB memory limit with no swap. tmpfs contents count against
  it. A host watchdog (memguard) kills the biggest container process if the containers stall at the cap.
- **Not the whole of `/tmp`.** The container's `/tmp` is 11 GB, more than the cap, and most of it is
  long-lived: 5.8 GB of session scratchpads under `/tmp/claude-1000`, 1.1 GB in `/tmp/l7r-check`, 566 MB
  in `/tmp/l7r-pass`. Only the tests' own temp directory should move.
- **Launcher change.** A new tmpfs mount is added by `launch-container` on the host (source in
  `/host-scripts`; propose changes through the host-script proposal process). Existing containers must be
  recreated to get it. `/dev/shm` is only 64 MB, so it is no substitute.
- **Cheaper alternative:** cap how many copies of the suite run at once. One or two copies were never
  observed to cause stalls; 12 did. The threshold in between is unknown.

## What the diagram session can measure

1. **Peak size of the tests' temp files.** Find where the `land` tests create repositories, then sample
   that directory's size during one copy of the suite and during the 12-copy load. This is the number Eli
   asked for: it decides whether a tmpfs fits under the 10 GB cap and how large to make it.
2. **Syncs versus churn.** Count `fsync`/`fdatasync` calls for one run of the suite (`strace -f -c -e
   trace=fsync,fdatasync,sync_file_range`), and check whether git in the tests runs with its default
   `core.fsync`.
3. **Files created and deleted per run**, as a rough count, to size the directory-operation load.

Host-side stall measurement is not available inside the container. The host tool is `desktop-stall-probe
120` (exit 1 if any desktop write took over 1 s); ask Eli or the host session to run it while a candidate
fix is under load. The full host write-up is in the host repo `this-laptop`, `docs/memory/CLAUDE.md`,
section "Variant: sync storm".
