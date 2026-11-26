# Feature 459: builders shared between sessions - one machine's parallel work coordinated by the tooling

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-26

**Status**: Draft - filed to be thought about, not worked now ("we don't worry about right now ... I don't have any need for multiple sessions between now and then")

**Affects**: tooling

**Approved**: the GM, 2026-11-26, "This is something that probably can be its own spec kit feature that we don't worry about right now, because I think that we should be more focused on just kind of getting everything working to start with and then resuming our port eventually, since I don't have any need for multiple sessions between now and then. But I want to make sure that this is something that we are thinking about."

**Input**: `request.md` (the GM's words); `docs/process-decisions.md`, "Two code builders at once" (the measurements of
2026-11-26); 451 T284 (the build slot), T285 (the builder pool), T308 (two tiers of checking); trial 458 (the second tier's
threshold and the continuous gate).

## Why

The parallel arrangement measured on 2026-11-26 is one session's: its pool of builder trees (capped per clone,
`L7R_BUILDER_POOL`), its staging clone, its gate. The GM wants to be able to run several sessions at once in the future, and
whatever number of simultaneous builders is best for the machine must then be shared between them by the tooling - in his
words, "if the optimal number of simultaneous builders was 4, then the two sessions could coordinate about that in some kind
of automated tooling-based way".

## What already crosses sessions, and what does not (2026-11-26)

- The build slot (451 T284) is machine-wide: its lock files stand outside any clone (`~/.cache/l7r-build-slots/`), so every
  session's builders and landings already share the heavy compiles.
- The push to main is serialized across sessions by the cross-session lock (`.clones/.sync.lock`), and each session has its
  own clone.
- The builder pool's cap is per clone: two sessions could each hand out four trees. Memory and processor were measured for
  one session only: the sample log `dev/measurements/2026-11-26/builder-count/mem-samples-round1-three-warm.log` (one
  sample every 10 s of the container's cgroup, 2026-11-26 15:43-16:36 UTC; three builders in warm pool trees were alive until
  about 16:15) and `docs/process-decisions.md`, "Two code builders at once", which states its figures and their windows.
- With more than one session main moves under a session's staged work, so how long a batch waits for its gate matters as it
  does not with one (trial 458's continuous gate).

## To settle when the feature is worked (not decided here)

- One machine-wide count of builders: where it is kept, how a session takes and returns a place, and what a session does when
  none is free (wait, or run one fewer).
- Whether the count is of builders or of what they cost - the build slot already bounds compiles; anonymous memory and the
  models' own concurrency may be the real limits.
- The second tier with several sessions: each session's gate against a main the others move, and the continuous gate.
- What is measured first: two sessions side by side, each with builders, the sampler running.

## Review history

- spec-fidelity round 1 (2026-11-26, MODE 2): CHANGES REQUIRED, 1 item - the three-warm-builders memory and load figures in "What already crosses sessions" carried no source or method, are not in the decision entry cited, and the load median did not reproduce from the round-one sample log as written; the request, the Status and Approved quotes, the open questions and the slot, push-lock and pool-cap facts were faithful. Fixed the same day: the figures are replaced by the sample log's path and window and a pointer to the decision entry, which now states round one's figures with their statistic and window; "again" (not his word) is dropped from Why.
- spec-fidelity round 2 (2026-11-26, MODE 3 by hand): CHANGES REQUIRED, 1 item - the source-and-method half of round 1's item is confirmed (the bullet names the log, its sampling and window, and points at "Two code builders at once", whose ROUND ONE paragraph is there; "again" is gone), and the paragraph's figures re-derived from the sample log reproduce except the load median over the samples while all three builders were alive, which the paragraph gave from one sample more than the count it names. Fixed the same day: the paragraph's load median is the value of the count it names; the spec text needed no change.
- spec-fidelity round 3 (2026-11-26, MODE 3): FAITHFUL - round 2's item is resolved: the ROUND ONE paragraph of "Two code builders at once" now gives the load median of the samples while all three builders were alive as the value the log reproduces. The paragraph's other figures still reproduce, and no stale value remains in the decision entry or the feature directory.
