# Tasks: Finish Warming the Remote Build (feature 177)

Every task is `research: procedure` - this feature is about what the remote build repeats, downloads
and expires, and about two guards. Nothing in it concerns how a place was built, farmed or lived in,
so no task is `physical` and none owes the three research boxes. The GM's words are in
[`request.md`](request.md); the measurements are in [`research.md`](research.md); the shape is in
[`plan.md`](plan.md).

**Only T20 to T23 cost money.** Everything else is local.

## Piece 5 - the two found defects (cheapest, no dependencies, so they go first)

- [x] T01 FR-016, FR-017: `main-tree-hooks.sh` accepts the subshell form its own message prescribes
      research: procedure
      verify: DONE. `(` joins the command-position alternatives in BOTH scans - the LEAVES scan and
      the ENTRY scan - and `\)` joins the terminators. Four new cases in
      `scripts/test-main-tree-hooks.sh`; suite 34 passed / 0 failed. PROVEN TO FIRE by reverting the
      two regexes and re-running: exactly those four fail, and instructively they fail in BOTH
      directions - two false REFUSALS (the reported defect) and two false ALLOWS
      (`( cd <mirror> && <write> )` got through), which is why the entry scan had to move in the same
      edit. The pre-existing "documented subshell form in a clone" case passed even on the broken
      guard, because its cwd was already the clone: that is how the suite stayed green while the
      guard refused correct work

- [x] T02 FR-018, FR-018a: `cache_location` stops sharing one object between the gate and an operation
      research: procedure
      verify: DONE. `dispatch.registered_operation()` maps a target to its REGISTERED name from
      `_invocation.OPERATIONS` and nothing else, so `cohort SEEDS=8` and `cohort SEEDS=9` give ONE
      key; `cache_location` takes it as a fourth argument. The boundedness test now varies that
      dimension (`projects x scopes x (1 + registered expensive operations)`), which the old
      `len(locations) == 4` form could not have done. `tests/tooling/ci/test_cache.py` 10 passed

## Piece 4 - the lifecycle document

- [x] T03 FR-013, FR-014: `cachepolicy.lifecycle_configuration()` returns the WHOLE document
      research: procedure
      verify: DONE, as FOUR named rules rather than three - `expire-generation-cache` (`cache/`,
      30 d), `expire-verified-records` (`verified/`, 365 d), `expire-large-objects`
      (`ObjectSizeGreaterThan` 1 MiB, 30 d) and `abort-dead-multipart-uploads` (prefix `''`, 7 d, NO
      `Expiration`). The net is a SIZE and not a prefix because S3 has no negative filter: a
      prefix-`''` net cannot be told to skip `verified/`, so "outside its reach" is unachievable that
      way, while a 200-byte record is structurally unreachable by a 1 MiB size filter. The split into
      four is S3's ruling, not a preference - see T05

- [x] T04 FR-019: the lifecycle tests updated to the new CLOSED invariant, not loosened
      research: procedure
      verify: DONE. `test_cachepolicy.py` addresses every rule through `cachepolicy.rule(doc, id)`,
      asserts the document is exactly those four ids in order and that the retired one is absent,
      asserts the multipart rule has NO `Expiration` (the load-bearing absence), and RE-PINS the
      docstring assertion to what is true now - the overlap hazard, the retired rule's name, the 365
      and the "no negative filter" reasoning. 9 passed

- [x] T05 FR-015: apply the document with the `[aws_admin]` credentials, READ IT BACK, record it
      research: procedure
      verify: DONE via `scripts/apply-ci-lifecycle.py --apply` (dry by default; the document comes
      from the tested module, never from the script). READ BACK from the bucket 2026-09-03: four
      rules, `expire-ci-junk` GONE. Independently re-checked against the live objects:
      `verified/` 9 objects / 3,012 bytes, reachable by the size net **0**; `cache/` 1 object /
      2.65 MiB, reachable **1** (both rules say 30 d, so nothing moved); `artifacts/`, `image/`,
      `go/` reachable 0. **The first `--apply` FAILED and that is the finding**: S3 answered
      `InvalidRequest: AbortIncompleteMultipartUpload cannot be specified with Object Size`, which is
      why the net is two rules. Applying rather than assuming is what produced it

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
