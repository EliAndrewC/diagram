# Tasks: the label phase, and a notice-board caption that stands beside its board

**Feature**: `157-label-phase-and-notice-board-caption` | [spec](spec.md) | [plan](plan.md) | [research](research.md)

Every task here is `research: rendering` - a map convention with nothing physical behind it. Nothing
in this feature decides how a place was built, farmed, planted or lived in, so no task carries the
three physical checkboxes (constitution v2.12.0; the reasoning is in the spec's Decisions Recorded).

## Phase 0 - the baseline

- [x] **T01** `research: rendering` - baseline on unmodified code in a detached worktree at HEAD.
      **Measured**: `2760 passed, 2 skipped` in 148 s; `hooks-test` red on all 19 suites, entirely
      from the worktree artifact in T02. That is the bar every later run is compared against.
- [x] **T02** `research: rendering` - **defect found taking the baseline (Principle XIV)**:
      `make hooks-test` resolves its per-suite freshness cache as `$root/.git/hooks-test`, and in a
      LINKED WORKTREE `.git` is a FILE, so every suite dies with `Directory nonexistent`. A detached
      worktree is exactly where constitution XIII requires the baseline to be taken, so the mandated
      procedure could not produce a green `hooks-test` on any commit. Fixed by asking git for the
      path (`rev-parse --absolute-git-dir`); roster, failure path and stamp unchanged.

## Phase 1 - the label phase

- [x] **T10** `research: rendering` - the queue and the pending flag on `Settlement` (`core.py`).
- [x] **T11** `research: rendering` - `label()` queues while the phase is pending. GENERAL, not
      per-feature: it is the primitive all 54 inline caption sites funnel through.
- [x] **T12** `research: rendering` - `place_labels()` - the phase itself, with its documented drain
      order (queue in call order, then the deferred `place_caption` seats, then the road caption) and
      its one-row dispatch table. Idempotent.
- [x] **T13** `research: rendering` - `finish()` runs the phase as the last thing it does, so a
      hand-authored village/town/city script gets it with no change to the script.
- [x] **T14** `research: rendering` - `kosatsuba()` queues a SEAT REQUEST; the search moves to
      `_draw_board_caption`, unchanged, to be run in the phase.
- [x] **T15** `research: rendering` - `stage_labels`, last in the hamlet `STAGES`.
- [x] **T16** `research: rendering` - `stage_notice`'s re-seat drops the QUEUED caption
      (`discard_queued_label`) instead of hunting the drawn one out of `M["labels"]` by its text.
      The orphan-caption bug that block existed for (feature 133 T48) can no longer occur.
- [x] **T17** `research: rendering` - **the phase alone must move nothing at hamlet scale.**
      **Measured**: Inashiro and Kuwabata regenerate BYTE-IDENTICAL. That is what lets every caption
      that moves later in this feature be attributed to the seat rules.
- [x] **T18** `research: rendering` - route `paddy_field(label=...)` and `water_field(label=...)`
      through the phase. Both emit raw `<text>` via `add_label` + `_record_label` today, so they
      would draw outside it; both are dormant (no pool map passes `label=`). Found by the round-2
      spec review.

## Phase 2 - the caption that stands beside its board

- [x] **T20** `research: rendering` - the structural probe measures the caption's TRUE ROTATED QUAD
      (FR-008). Measured defect: at -28.1 degrees it inflates a 54 x 10 px caption to a 52 x 34 px
      box and refuses a seat the caption clears by 4.43 px.
- [x] **T21** `research: rendering` - the tilted ladder samples finely in BOTH axes, keeping its
      reach (FR-007). The reach is load-bearing: five cohort seeds have no legal seat on the
      perpendicular line at all.
- [x] **T22** `research: rendering` - the seat ranking states the GM's rule (FR-006): among legal
      seats, least displacement ALONG the caption's baseline wins; the standoff across it breaks the
      tie.
- [x] **T23** `research: rendering` - regenerate Kuwabata and read the manifest. **Acceptance**: the
      board's center falls within the caption's own run, and the standoff stays inside the hug cap.
- [x] **T24** `research: rendering` - the two WORKAROUND hand seats: removed, then REVERTED.
      Minami and Nagahara are FROZEN legacy exhibits (GM 2026-08-16, `dev/pool.md`): *"never
      regenerated, never re-gated ... do not 'fix' a frozen map, and do not treat its rule
      violations as bugs."* The edit would change nothing a reader sees - the gen is never re-run -
      while desynchronizing an exhibit's source from its shipped manifest. Accepted, with the cost
      and the priced alternative (conversion) recorded in the spec's hand-seat edge case. The
      GM-RULING hand seats stay, as they always would have.

## Phase 3 - the sweep, and the rule with teeth

- [x] **T30** `research: rendering` - `make maps` over the whole tier. **maps clean**, five
      scripted hamlets regenerated. **Measured** - every board caption now stands beside its board:
      |lateral| of 2.22 / 1.53 / 1.02 / 0.63 / 1.55 px (inashiro, kashikawa, kuwabata, mizuguchi,
      sawada) against subject half-extents of 3.0-6.5. Kuwabata was 35.6. Only kashikawa and sawada
      moved besides Kuwabata; inashiro and mizuguchi were already seated centrally and are unchanged.
      The eight six-element manifests are all FROZEN legacy exhibits and are deliberately NOT
      regenerated (see T24).
- [x] **T31** `research: rendering` - read the LATERAL DISTRIBUTION the fixed placer produces across
      the pool and the cohort, and set `caption_stands_beside_its_referent`'s threshold from it with
      a stated margin. The number is measured, never chosen in advance (plan D6). **Done** - the
      bound is `subjHalf + LABEL_MIN_AIR`, reused rather than invented and not fitted to the
      motivating map (R5: the pool sits at 0.63-2.22 px against bounds of 8.0-11.5, while the map the
      GM complained about fails by 3.1x). The cohort drove three more placer fixes (R8, R9) and
      settles at 25/48 with five reported cases, none of them an in-gate ratchet seed (R10).
- [x] **T32** `research: rendering` - the check itself (`make new-check`), scoped to the
      notice-board caption family, with the "a board caption MUST record a referent" clause so a
      six-element record fails rather than skips. It must NOT read any placer-written "no legal
      seat" verdict - a check graded by the thing it grades is not a check.
- [x] **T33** `research: rendering` - freeze today's Kuwabata manifest into `pool/regressions/` as
      the negative fixture and prove the check FIRES on it (delete the check, watch a test go red).

## Phase 4 - the record, and the review

- [x] **T40** `research: rendering` - the comments at each point of change, `dev/placement.md`'s
      DRAW ORDER map, `hamletgen/CLAUDE.md`'s stage table, `settlement/structures/CLAUDE.md`.
- [x] **T41** `research: rendering` - the pool notes for every map whose caption moved.
- [ ] **T42** `research: rendering` - `make verify`: the gate and the independent `settlement-review`
      together (feature 151), then the stop-work procedure.
