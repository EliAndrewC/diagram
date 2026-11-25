# Feature 455: research run beside the build, not in front of it

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-25

**Status**: Draft - filed for the GM to work later ("I will probably end up working that feature tomorrow")

**Affects**: tooling

**Approved**: the GM, 2026-11-25, "So can we perhaps move that into its own separate feature and then I will probably end up working that feature tomorrow."

The GM asked for this feature to be filed on 2026-11-25: *"I do want to capture that kind of parallelizing as its own thing.
So can we perhaps move that into its own separate feature and then I will probably end up working that feature tomorrow."*

**Input**: `request.md` (the GM's words); `specs/449-rust-codebase/port-talk-agenda.md` items 1 and 4 (one writable clone per
session serializes page sessions behind code builders); 451 T243's task time breakdown (its blocking column, amendment (C):
blocking only where something waited).

## Why

Research is slow in wall clock and in tokens, and it will stay so. What costs the project is BLOCKING on it: a code task that
waits for a page session, or a page session that waits for a builder to leave the clone. 451 T236 (the UNRESEARCHED label and
`make research-backlog`) stopped code waiting on research it does not need yet. This feature is the other half: research that
is needed runs beside the build, in its own copy, so that, in the GM's words, *"while they will remain very time-consuming in
terms of the amount of wall clock time and even perhaps the amount of tokens that they take, then we will not actually be
blocking on that research very often."*

## To settle when the feature is worked (not decided here)

- Where a page session runs: its own clone or worktree (agenda item 8, worktrees against clones), and how its pages reach main
  beside a builder's landing (one landing at a time through main).
- How the backlog is worked in parallel: `make research-backlog` items picked up by page sessions while code builds, and what
  a code task does when an item it touched is mid-search.
- What T243's blocking column shows research costing before and after.
- Any change to the cascade (claims and pop-ups re-owed by page edits) when pages land while code is in flight.
