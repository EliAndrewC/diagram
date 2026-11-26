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
`L7R_BUILDER_POOL`), its staging clone, its gate. The GM wants to run several sessions at once again in the future, and
whatever number of simultaneous builders is best for the machine must then be shared between them by the tooling - in his
words, "if the optimal number of simultaneous builders was 4, then the two sessions could coordinate about that in some kind
of automated tooling-based way".

## What already crosses sessions, and what does not (2026-11-26)

- The build slot (451 T284) is machine-wide: its lock files stand outside any clone (`~/.cache/l7r-build-slots/`), so every
  session's builders and landings already share the heavy compiles.
- The push to main is serialized across sessions by the cross-session lock (`.clones/.sync.lock`), and each session has its
  own clone.
- The builder pool's cap is per clone: two sessions could each hand out four trees. Memory and processor were measured for
  one session only (three warm builders: 3.9 GiB anonymous of a 10 GiB container, load median 16 on 22 cores).
- With more than one session main moves under a session's staged work, so how long a batch waits for its gate matters as it
  does not with one (trial 458's continuous gate).

## To settle when the feature is worked (not decided here)

- One machine-wide count of builders: where it is kept, how a session takes and returns a place, and what a session does when
  none is free (wait, or run one fewer).
- Whether the count is of builders or of what they cost - the build slot already bounds compiles; anonymous memory and the
  models' own concurrency may be the real limits.
- The second tier with several sessions: each session's gate against a main the others move, and the continuous gate.
- What is measured first: two sessions side by side, each with builders, the sampler running.
