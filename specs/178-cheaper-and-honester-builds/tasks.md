# Tasks: Cheaper and Honester Builds (feature 178)

Every task is `research: procedure` - this feature is about what the gate can see, what a build
compares against, what git tracks, and what a build costs. Nothing in it concerns how a place was
built, farmed or lived in. The GM's words are in [`request.md`](request.md) (including the
mid-implementation follow-up); the measurements are in [`research.md`](research.md).

**Only T20 to T23 cost money. T30 to T34 are IRREVERSIBLE.**

## Item 1 - the measured-but-not-engine short-circuit

- [x] T01 FR-001/FR-003: gate-stamp's exclusions are DERIVED from the coverage configuration
      research: procedure
      verify: DONE. `exclusions(area)` = declared minus anything `[tool.coverage.run] source`
      measures, so `tests/` survives and `l7r/diagram/ci/` cannot. Measured on the real tree: ci/
      files hashed 0 -> **12**; `.py` outside `l7r/` and `tests/` still **37** (the add-only rule);
      `tests/` still 0 (FR-024 untouched). An unreadable config falls back to `l7r/`, NOT to nothing
      - the first draft did the latter and called it "the safe direction" while it silently restored
      the entire defect, and `test-gate-stamp.sh` caught it within the minute

- [x] T02 FR-002: the PAID route is untouched
      research: procedure
      verify: DONE. `delta.is_engine` is a separate computation and is unchanged, so a ci-only delta
      still routes DIRECT and starts no build - the MONEY half of the GM's FR-025 ruling stands, the
      LOCAL GATE half is superseded. Pinned by `test_the_PAID_route_is_untouched...`

- [x] T03 FR-018: the named test case FR-001 inverts, flipped with its reason
      research: procedure
      verify: DONE. `scripts/test-gate-stamp.sh`'s *"ci-only change: no stamp needed (FR-025)"* now
      asserts a stamp IS needed, with a note saying which half of FR-025 is superseded. The fixture is
      reverted after the case rather than stamped: stamping changes which refusal the later
      "refusal must name the diagram area" case sees

- [x] T04 FR-018/D1: the operative documents that assert the state item 1 ends
      research: procedure
      verify: root `CLAUDE.md` (*"every `.py` under the skill outside `tests/` and `l7r/diagram/ci/`"*
      and *"a tests-only or ci-only change skips the build and the local gate"*) and
      `docs/efficiency-tooling.md`'s four short-circuits. No mechanical check will catch these;
      feature 174 spent six review rounds on this class of drift

## Item 2 - the strongest local proof counts

- [x] T05 FR-004/FR-005: `make test-full` records green-local
      research: procedure
      verify: DONE, chained with `&&` so a red sweep records nothing, and named `test-full` so an
      audit can tell which run vouched. Pinned textually rather than by a four-minute run

## Item 3 - what a build's perf-gate compares against

- [x] T06 FR-007: confirm the transport the GM proposed needs no new machinery
      research: procedure
      verify: DONE. `dev/perf-log/` is tracked (58 snapshots), is not sparse-excluded, and therefore
      already arrives in every container. No S3 fetch, no GitHub API call - the GM's *"we pass it
      along in the same manner we pass along our latest code"* was already true

- [x] T07 FR-008: the baseline is selected per MACHINE, not per environment
      research: procedure
      verify: DONE. `pairs()` keys on `(environment, (host, image))`; `perf_bands.evaluate` refuses
      only on an ENVIRONMENT mismatch, so before this an xlarge `-start` and an 8-vCPU `-end` were
      both `codebuild`, paired happily, and yielded a percentage that was pure instance difference.
      Item 5 is what makes that live. Test plants exactly that pair and asserts no verdict

- [x] T08 FR-009: a gate with no comparable baseline says it is MUTE
      research: procedure
      verify: DONE. `unpaired()` finds every `-end` with no `-start` from the same machine; `check()`
      reports `NO COMPARABLE BASELINE ... MUTE` and does not fail. A first run on a new instance type
      and a `make ci-image` rebuild (which changes `image`) both land here

- [ ] T09 FR-006: put the RESIDUAL to the GM, which is what their own instruction asks
      research: procedure
      verify: the transport is implemented and a FULL build still cannot go green, because
      `perf_bands.py` sets band 1 on `total_pct > 0 or any(p > 0 ...)`. The GM wrote *"if not then
      let's talk more"*; the `> 0` threshold is theirs from feature 129 and only they can relax it

## Item 5 - what a smaller server costs (PAID)

- [x] T10 FR-017: `ci-measure` takes `COMPUTE=`
      research: procedure
      verify: DONE. The dispatcher already understood `--compute`; only `check` passed it. Repaired
      once after a `: "..."` no-op line in front of `$(RUN)` turned its `@` recipe prefix into a
      literal - the exact failure this Makefile already documents beside `LOGBYPASS`

- [ ] T20 FR-013/FR-014: the 8-vCPU row (`BUILD_GENERAL1_LARGE`), same commit
      research: procedure
      verify: wall clock, billed minutes, dollars, green/red, and the first `g1.large` billing line
      this account has ever produced - which is the one rate `config.RATES` carries unverified

- [ ] T21 FR-013/FR-014: the 4-vCPU row (`BUILD_GENERAL1_MEDIUM`), same commit
      research: procedure
      verify: the GM's own question - *"if we're only using 4 cores then what does a 4-core server
      cost?"*. Memory is the risk here (7 GB), not cores, and "it did not finish" is a legitimate
      reportable outcome

- [ ] T22 FR-013: the `XLARGE` baseline re-measured on the SAME COMMIT
      research: procedure
      verify: feature 177's numbers are from a different tree, and its own D4 says in bold that such
      totals are not comparable. Reusing them would repeat the mistake this feature quotes

- [ ] T23 FR-016: the recommendation, and whether the default changes
      research: procedure
      verify: the criterion is stated in advance - green on every row AND at least 50% cheaper per
      run at no worse wall clock changes the constant inside this feature; anything else goes to the
      GM with the numbers and `XLARGE` stands

## Item 4 - what git tracks, and what leaves history (IRREVERSIBLE)

- [x] T30 FR-011: REHEARSE the purge in a throwaway clone, with measured before/after
      research: procedure
      verify: DONE (research R3). Pack **345.71 MiB -> 38.68 MiB, an 89% reduction**; objects 36,801
      -> 36,412, which barely moves because the renders were few and enormous. A filename CALLBACK
      rather than `--path-glob`, because 179 generated paths were ever added and many live at
      pre-reorganization homes a HEAD-derived list would miss. Exactly 13 files survived: the 5
      magistracy `.svg` and the 8 `tests/fixtures/*-red.svg`

- [x] T31 FR-012a: PRESERVE the irreproducible bytes and VERIFY by checksum, BEFORE anything is purged
      research: procedure
      verify: DONE. **83 files, 440.8 MB, copied to `/host-l7r-repo/diagram-render-archive/` with a
      MANIFEST.json carrying a sha256 per file - and VERIFIED by reading every one back: 83/83 match.**
      The destination is the GM's own disk (295 GB free), survives container rebuilds, and shows in
      their `l7r` status as one untracked directory beside the `?? JapanMaps/` already there.
      **S3 was considered and REJECTED for a reason worth keeping**: feature 177's own
      `expire-large-objects` rule (`ObjectSizeGreaterThan` 1 MiB, 30 days) would have deleted the
      archive a month later, silently - S3 applies the shortest overlapping rule and has no negative
      filter, so that bucket is now actively hostile to anything large anyone wants to keep

- [ ] T32 FR-010/FR-010a/FR-010b: untrack every generated render; keep the two non-generated classes
      research: procedure
      verify: `git ls-files` shows no generated `.html`/`.svg`/`.png`; the magistracy `.svg` and the
      eight `tests/fixtures/*-red.svg` remain; `.gitignore` rewritten so its frozen-exhibit block
      stops asserting something untrue

- [ ] T33 FR-010d/FR-010e: replace the raster check at kilobyte cost, honestly
      research: procedure
      verify: measured, the eight exhibits' numbers are **503 bytes against 97.9 MB** (204,000x). Not
      a tautology: either asserted against an independently derived second source (each exhibit's
      tracked `.json` carries `meta.view`, identical to the SVG viewBox) or stated plainly as a record
      rather than a check

- [ ] T34 FR-011a/FR-011a1: the guard escape - added, used, and REMOVED inside this feature
      research: procedure
      verify: `repo-safety-hooks.sh` has no force-push escape by design and says so three times. The
      GM authorized the ACT, not a standing hole. The suite must prove the refusal is absolute again
      at the end, and the feature is NOT done if the removal is not

- [ ] T35 FR-011d: every clone and the mirror onto the new history BEFORE any of them pushes
      research: procedure
      verify: 12 clones under `.clones/`; after the rewrite their history is disjoint and the first to
      push restores every purged object, with Principle VI forbidding the rebase that would fix it.
      Dirty trees carried across as patches - mid-task work is sacred

- [ ] T36 FR-011c: verify from a FRESH clone, and say what that does not prove
      research: procedure
      verify: `.git` size, clone time, green gate - and the note that a fresh clone is small even
      while a peer clone still holds every purged object

## Closing

- [ ] T40 D1 to D6 completed, each classed accurate / deliberate deviation / guess
- [ ] T41 the answer to the GM, the records current, and the local gate green with the 100% floor
