# Tasks: Finish Warming the Remote Build (feature 177)

Every task is `research: procedure` - this feature is about what the remote build repeats, downloads
and expires, and about two guards. Nothing in it concerns how a place was built, farmed or lived in,
so no task is `physical` and none owes the three research boxes. The GM's words are in
[`request.md`](request.md); the measurements are in [`research.md`](research.md); the shape is in
[`plan.md`](plan.md).

**Only T20 to T23 cost money.** Everything else is local.

## Piece 5 - the two found defects (cheapest, no dependencies, so they go first)

- [ ] T01 FR-016, FR-017: `main-tree-hooks.sh` accepts the subshell form its own message prescribes
      research: procedure
      verify: a case in `scripts/test-main-tree-hooks.sh` that FAILS before the fix - a
      `( cd <clone> && <write> )` issued while standing in main - plus the companion that proves the
      guard did not widen: `( cd <mirror> && <write> )` is still refused

- [ ] T02 FR-018, FR-018a: `cache_location` stops sharing one object between the gate and an operation
      research: procedure
      verify: keyed on the REGISTERED name from `_invocation.OPERATIONS`, never `ctx.operation` (which
      carries arguments - `cohort SEEDS=8` and `cohort SEEDS=9` are distinct strings);
      `test_the_cache_location_cannot_grow_with_the_number_of_builds` extended to VARY the new
      dimension, because as it stands it enumerates projects x scopes and would pass a defaulted
      fourth parameter green

## Piece 4 - the lifecycle document

- [ ] T03 FR-013, FR-014: `cachepolicy.lifecycle_configuration()` returns the WHOLE document, three
      rules: the cache rule, a `verified/` rule whose horizon is chosen for what those records are
      FOR, and a catch-all at a long horizon so an unforeseen prefix still cannot accumulate
      research: procedure
      verify: the horizon and its reasoning recorded in D6; `verified/` demonstrably outside the
      catch-all's reach

- [ ] T04 FR-019: the lifecycle tests updated to the new CLOSED invariant, not loosened
      research: procedure
      verify: `test_cachepolicy.py` addresses each rule BY ID rather than `Rules[0]`, asserts the
      document is exactly those three rules and nothing else, and re-pins the module docstring to
      the state that is now true

- [ ] T05 FR-015: apply the document with the `[aws_admin]` credentials, READ IT BACK, record it
      research: procedure
      verify: the read-back document quoted in D6; `cachepolicy.py` no longer describes the 14-day
      catch-all as live, and its two open questions for the GM are answered in place

## Piece 1 - the hooks-test stamp travels

- [ ] T06 FR-004: `run.sh`'s restore detection stops keying on `repo/.git` being absent
      research: procedure
      verify: detection is "is there a real repository here?" (`repo/.git/HEAD`), so a cache holding
      only `.git/hooks-test/` and `.git/gate-green-hooks` still takes the set-aside path; this is
      build `a48b730d`'s failure and it must be fixed BEFORE the cache paths are widened

- [ ] T07 FR-001: the two freshness-state paths join the cache in both buildspecs
      research: procedure
      verify: `repo/.git/gate-green-hooks` and `repo/.git/hooks-test/**/*` in check.yml and merge.yml,
      identical in both (the existing drift test still binds)

- [ ] T08 FR-019: `test_the_cached_paths_are_what_a_HIT_needs` updated to the CLOSED invariant
      research: procedure
      verify: the cache carries feature 175's derived `.gencache/` set plus exactly the two paths
      T07 adds and nothing else - not loosened to "`.git` is allowed too"

- [ ] T09 FR-002, FR-003: prove the safety properties rather than arguing them
      research: procedure
      verify: one test that a changed guard re-runs its suite (the stamp is content-keyed), one that
      a freshness state present only in a local tree cannot reach a build. Note at the point of
      change the residual asymmetry round 5 flagged: neither stamp is keyed to the build IMAGE, so a
      `make ci-image` rebuild does not retire them - equally true on a laptop after a toolchain
      upgrade, which is why it sits inside the spec's bar

## Piece 2 - the checkout stops carrying what nothing reads

- [ ] T10 FR-005, FR-006: finish the derivation, with affirmative evidence per exclusion
      research: procedure
      verify: R4 completed - `wip/*.html` and `dev/placement-stages/**` carried already; the legacy
      NON-hamlet renders (73.6 MB) either proven unread or RETAINED. For every check that touches an
      excluded path, what shows it still does the same work - a green build is not the proof

- [ ] T11 FR-006c: the exclusion list lives in ONE file and is guarded against rot
      research: procedure
      verify: a test that no engine or test module references a path under the list, proven to FIRE
      by planting a reference

- [ ] T12 FR-005: `run.sh` applies the sparse set to the bootstrap clone
      research: procedure
      verify: `--filter=blob:none --sparse` then `sparse-checkout set --no-cone`, applied before the
      checkout so the merge and the gate both see the reduced tree

- [ ] T13 FR-006a: the merge route's pushed tree proven complete BEFORE any merge dispatch
      research: procedure
      verify: R9's local demonstration repeated against this repository - tracked-path count or tree
      comparison at the merge base, recorded in D2. R9 already shows the property holds in a scratch
      repository, including across a merge that changed an excluded path

- [ ] T14 D2: record `engine_key_worktree`'s `is_file()` filter as the sharpest instance of the class
      research: procedure
      verify: written down with the reason it is not a live conflict (no path in the set is engine
      content) - which is exactly why it is worth recording before someone widens the set

## Piece 3 - the measurement route (the only paid part)

- [ ] T15 FR-008, FR-009a: the route, with its CLOSED envelope
      research: procedure
      verify: bypasses ONLY `route-is-gated`; `green-local-since-edit`, `remote-enabled`,
      `breaker-not-tripped` and (FULL) `door.py` all still refuse it, each proven by a test

- [ ] T16 FR-009: it cannot mint a push credential
      research: procedure
      verify: enforced on the BUILD side - a `MODE` whose `run.sh` branch writes no `verified/`
      record and never pushes; visible in the diff, not a promise the dispatcher makes

- [ ] T17 FR-010, FR-019: paid, prompted, logged; `ci/CLAUDE.md` describes the new route
      research: procedure
      verify: the same class as `make ci-image`; the threat-model section says what the route
      bypasses, what it can never do, and why that is not a hole in the five conditions

- [ ] T18 the local gate is green and the tree is at 100% coverage before anything is dispatched
      research: procedure
      verify: `make done` green; `make hooks-test` green

- [ ] T19 constitution XIII: the regression baseline, taken in a DETACHED WORKTREE
      research: procedure
      verify: taken before the first measurement is quoted, and each failure the worktree reports
      checked against this clone before being called pre-existing

- [ ] T20 FR-020: reference, COLD - the cache deleted from S3
      research: procedure
      verify: passes, and takes about the cold time; the build fails on nothing cache-related

- [ ] T21 FR-011: reference, WARM - the post-174 number
      research: procedure
      verify: phase by phase against ONE local `make done` on the SAME COMMIT, both commits and both
      gate recipes named. Never the 227.5 s median

- [ ] T22 FR-012: FULL, cold - the payload size read off the BUILT object
      research: procedure
      verify: MB from the artifact, not summed from globs applied to a local `.gencache/`

- [ ] T23 FR-012: FULL, warm - whether the FULL cache pays
      research: procedure
      verify: cold versus warm; if it does not pay, 175's FR-010 ladder - narrow the set and
      re-measure; report and HOLD only if nothing pays

## Recording

- [ ] T24 D1 to D9 completed, each classed accurate / deliberate deviation / guess
      research: procedure
      verify: every Decision Recorded filled, including D4's two halves of the GM's own sentence and
      D7's pricing of the declined repo-side slimming over the whole 441 MB

- [ ] T25 the answer to the GM, and the records brought current
      research: procedure
      verify: `timings.md` or `dev/` carries the before/after; the run log carries every paid build;
      `make audit` shows the prompt answers with their quoted authorization
