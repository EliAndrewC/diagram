# Feature 374 - handover (2026-10-11)

Load this file when: resuming feature 374 in a fresh session. Batch 3 (waves 119-121, T10-T12) is done and checked but NOT
landed; this is what the session that did it knew and the repository does not otherwise say. Delete it when batch 3 lands.

The work is in the clone `/diagram/.clones/diagram-backlog`, backed up to `backup/diagram-backlog` on GitHub. The GM
stopped the goal at its usage cap; the cap was then disarmed so the last records could be committed.

## To land batch 3, in order

1. **Claims.** The merge of main on 2026-10-11 left 2 claims owing a triage: `make claims-triage`, then dispatch as it says.
2. **The perf band.** The pair `374-start` / `374-end` reads band 3 (+25%). `perf-audit` (2026-10-11, its record
   `dev/perf-log/20261011T105045Z-review-374-confirmation-local-diagram-backlog.json`) found the band is host load, but
   ruled the session's explanation INCONSISTENT: its seven alternated legs show a real ~+1.2% of the total in
   hinterland+woodland, from T11's wood rule (`wood_rank.py`, `parcels.py`: seats below the houses now ranked, every seat
   asked `low_by_the_water`); the door router's 4 ft lattice costs nothing. Its legs are in `perf-audit-legs/` here.
   - Add a `measurements.json` key pointing at `perf-audit-legs/*aud374*.json` (3 base legs, 4 head legs).
   - `make perf-explain WHY="<host load for the band; a real ~1.2% in hinterland from the wood rule>" CONTROL=<that key>`
     (export `SPECIFY_FEATURE=374-match-the-research-continued` first).
   - Dispatch `perf-audit` again (band 1 confirmation and band 2: it judged band 2 likely justified - necessary under
     0077, ~1% commensurate, the water zone already built once), then `make perf-arbiter` for band 3.
   - The control `m:batch3-cpu-interleaved` is weaker than the auditor's legs (worktree against clone; one seed carries
     its -9%); prefer the auditor's.
3. **The seven "owed" reviews.** The stop hook lists building-review x3 and glyph-check x3 on the magistracy sheets
   (batch 1's declared occasions) and the woodland glyph-check on Inashiro. All passed at an earlier engine key; the
   magistracy sheets are identical to main and Inashiro differs only by the wave 120 wood that passed. Exit: a gate run
   carrying `PAIR_OK="<that reason>"` (the guard's `review_waived`).
4. **Plan review.** `plan.md` was amended after its last CLEAR (the batch 3 bookends row, the closing counts 185 open /
   131 E3, the 0.09 ft's measurement named) - dispatch `spec-fidelity` in PLAN REVIEW mode; update the bookends row with
   the perf-audit result first, so it is reviewed once.
5. `make tick F=374 T=T10`, `T11`, `T12`; then `scripts/sync-with-main.sh done` (a green `make done` first; merge main
   if it moved).

## Housekeeping

- Three scratch git worktrees of the clone under `/tmp/claude-1000/.../scratchpad/` (`base374`, `aud-base`, `aud-head`):
  `git -C /diagram/.clones/diagram-backlog worktree prune` once the perf records are made.

## For the GM

- Defects found, not yet fixed: (a) `ledger-hooks.sh` checks the ledger before the command runs, so one command that
  writes the ledger and commits lints the old text (the gate's ledger lint still catches it); (b) the usage-cap hook
  refuses `git commit` though its own message lists commits as allowed.
- Decision: the notice board's seat rolls evenly, though 0190 puts the village center first (filed DRIFTED,
  `found-wave120.jsonl`) - whether to weight the center is the GM's.
- Review at the end: the held rows (door band, fixture quota), the arbiter rulings (`make gm-review`), the tooling fixes.

## What this batch taught

- A record check answers the words its BUNDLE read: edit before bundling, or the unit is owed again.
- An edit to a drawing page re-owes every pop-up whose `Drawing:` names it; batch such edits.
- Gaps the checks file are old research the vague claims hid, not new research; expect them to taper as each module's
  claims are rewritten once.
