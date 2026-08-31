# Feature 175 - Warm the remote build

**Status**: FAITHFUL (`spec-fidelity`, round 2) - cleared for implementation (constitution XVI)
**Request**: `request.md` (the GM's words, verbatim) · **Measurements**: `research.md`

## Why

A CodeBuild run clones into a fresh container with an empty `.gencache/` and no buildspec declares a
cache, so every map the local gate serves from cache is regenerated for real remotely. The remote
gate does **strictly more work than the local gate for the same commit**. The GM's ruling on what
that means: *"rather than just saying that AWS is slower, we should note that that means in our
current implementation, we're not optimizing the AWS code runs as much as we should."*

## Scope

**In**: the CodeBuild cache configuration, what goes into it, what expires it, and the measurement
that says whether it helped.
**Out**: what the gate verifies. This feature removes REPEATED WORK, never CHECKS. Any change that
would let a remote run verify less than the same local run is out of scope and fails the request.

**Out**: `buildspec/image.yml`. The image build runs no gate and warms no gencache, so it is outside
this feature's domain rather than carved out of it; Docker layer caching is a different optimization
and nobody asked for it. Stated because research R1 reports "no `cache:` block exists in any
buildspec" and names all three - without this line a later reader sees two of three treated and
re-opens the question. (`spec-fidelity` round 2, recommended not required.)

## Functional requirements

- **FR-001** The `check` and `merge` buildspecs MUST declare an S3-backed CodeBuild cache, and the
  dispatcher MUST pass whatever the cache configuration requires for it to take effect.
- **FR-002** The cached set MUST be derived from what a cache HIT is proven to need (research R3),
  not from "the whole directory". The derivation MUST be recorded with the evidence for each
  inclusion and exclusion.
- **FR-003** The `.png` of a pool map MUST NOT be cached. A gate-built entry has none (the child
  runs `DIAGRAM_SKIP_RENDER=1`), and `gencache.load()` deletes a standing output its entry lacks -
  seeding a container with rasters no remote roll produces re-creates the 2026-08-17 defect in which
  four maps shipped a PNG from the previous roll beside a current `.json` and `.svg`, with matching
  mtimes, past two review rounds.
- **FR-002a** The total bytes the cache uploads and restores MUST be **measured on the ACTUAL built
  cache object**, stated in MB **per run mode** (FULL and reference separately, per FR-004), and
  recorded in Decisions Recorded against the naive 221 MB. A figure summed from the research table
  does not satisfy this - it must come from the artifact that exists. *(This is the GM's item 2,
  "figuring out exactly how much we do want to upload", which is a DIFFERENT question from item 4's
  "what needs to go there"; the first draft of this spec answered item 4 three times and item 2
  nowhere. Found by `spec-fidelity`, round 1.)*
- **FR-004** The cached set MUST differ by run mode where the read path differs. Specifically, a
  FULL-scope build MUST NOT upload or restore `.gencache/rolls/` (`rollcache.bypassed()` is true
  under `L7R_TESTS_FULL=1`; 54 MB, 24% of the directory, never read), and a reference-scope build
  MUST include it (`make reference` calls `rollcache.report`). If a single mode-independent set is
  chosen instead, that choice MUST be justified with the MEASURED cost of the bytes the other mode
  never reads.
- **FR-005** The cache key MUST be bounded - the number of distinct S3 objects the cache can ever
  hold MUST NOT grow with the number of commits, builds or branches. A key containing the commit SHA
  is specifically forbidden: it is the GM's named failure ("uploading many megabytes worth of
  content to Amazon S3 on every run and then never cleaning it up").
- **FR-006** The bucket holding the cache MUST carry a lifecycle rule that expires cache objects, so
  that abandoned keys disappear without anyone remembering to delete them. The expiry MUST be stated
  in the spec's Decisions Recorded with the reasoning for the number chosen.
- **FR-007** A cache miss, a cache-restore failure, an absent bucket or an expired object MUST NOT
  fail a build. The cache is an optimization; its failure mode is a slow build, never a red one.
- **FR-008** Whether any gate test reads a pool map's `.html` MUST be SETTLED before the cached set
  is fixed, **in either direction** (research R6.1). Excluding it unsettled is destructive - `load()`
  DELETES an output its entry lacks, so "no reader was found" is not "no reader exists". *Including*
  it unsettled adds ~65 MB (13 MB x 5) to every upload and restore and answers FR-002a by assertion.
  The ruling and how it was established go in D4.
- **FR-009** The feature MUST report a measured before/after: remote wall time and cost for the same
  scope, cold versus warm, on comparable commits. A predicted saving does not satisfy this - three
  performance predictions made in this repository on 2026-08-31 were each overturned by measurement.
- **FR-010** If the measurement shows a cached set does not pay, the feature MUST first **NARROW the
  set under FR-002 and re-measure**. R6.2's doubt concerns the ~110 MB of `.svg`, not the 184 KB
  manifest or the 96 KB `coverage.data`: "it does not pay" is a fact about a SET, not about caching.
  A cache that measurably makes the remote build slower MUST NOT ship. If NO cached set pays, the
  feature MUST report the measurement to the GM and HOLD - the session MUST NOT close the feature as
  delivered with no cache, because the instruction was *"please proceed with implementing that
  feature"*. *(The first draft let the session end the feature unshipped on a measurement it took
  and graded itself. Found by `spec-fidelity`, round 1; constitution XV - when a scope does not
  work, narrow it, do not stop.)*

## Success criteria

- **SC-001** A second remote run of the same scope, on a commit whose engine content is unchanged,
  is measurably faster than the first, and the difference is attributable to cache hits rather than
  to noise.
- **SC-002** The uploaded payload size is **stated in MB for each run mode, measured on the built
  cache**, together with what was excluded and the evidence for each exclusion. (The first draft
  said only "smaller than the naive 221 MB", which excluding a single file would satisfy.)
- **SC-003** The number of S3 objects the cache holds is bounded and stated; running N more builds
  does not create N more objects.
- **SC-004** A build with the cache deleted from S3 still passes, and takes about the cold time.
- **SC-005** A remote run verifies exactly what it verified before the feature: same tests, same
  floors, same failures on a known-bad tree.
- **SC-006** `make ci-status` remains truthful about cost after the change.

## Assumptions

- **A1** The AWS account can host a cache bucket with a lifecycle rule. Credentials in
  `development-secrets.ini [aws]`; account 130071571821.
- **A2** The gencache key remains content-derived, so a stale entry can only MISS, never serve a
  wrong answer. This is what makes caching safe here and MUST be re-checked if the keying changes.
- **A3** Remote runs are infrequent (24 this month), so cache warmth is not guaranteed between runs;
  the feature is judged on the warm case but must behave well cold.

## Decisions Recorded

To be completed during implementation, per constitution XII - each as **accurate**, **deliberate
deviation** or **guess**:

- D1 the cached set and the evidence for each inclusion/exclusion (FR-002, FR-003, FR-004)
- D1a **the measured size of the built cache, in MB, per run mode**, against the naive 221 MB - the
  GM's item 2, and a figure read off the artifact rather than summed from research (FR-002a)
- D2 the cache key and why it is bounded (FR-005)
- D3 the lifecycle expiry and why that number (FR-006)
- D4 the .html ruling and how it was settled (FR-008)
- D5 whether the cache paid, measured (FR-009, FR-010)

## Review history

Constitution XVI: reviewed against the GM's own words in `request.md`, by an agent that did not write
it, before any implementation. Two rounds.

**Round 1 - CHANGES REQUIRED (4).** The author asked the reviewer to attack three specific things and
was wrong about which mattered.

1. **Item 2 had no FR at all** - the failure the author did NOT suspect. *"Figuring out exactly how
   much we do want to upload"* and *"figuring out exactly what needs to go there"* are two questions
   said in one breath; the draft answered the second three times (FR-002/003/004) and the first
   nowhere, leaving it to an SC that read "smaller than the naive 221 MB" - satisfiable by excluding
   one file. Fixed by FR-002a and D1a: measured on the BUILT cache, per mode, and a figure summed from
   the research table explicitly does not count.
2. **FR-010 let the session close the feature unshipped** - the one the author DID suspect and flagged
   for attack. The reviewer's argument was sharper than the author's doubt: *"it does not pay" is a
   fact about a SET, not about caching*, and R6.2's risk is the ~110 MB of `.svg`, not the 184 KB
   manifest. Now: narrow and re-measure first; if nothing pays, report to the GM and HOLD.
3. **FR-008 was one-directional** - "settle before EXCLUDING", whose cheapest compliant path was to
   INCLUDE 65 MB of `.html` and settle nothing.
4. **FR-004's "MUST account for the run MODE"** was satisfiable by writing a sentence.

The reviewer also ruled FR-003 and FR-004 were NOT added scope, against the author's own worry that
excluding things might be self-serving: the GM assigned the question and *"an answer to 'what needs to
go there' is necessarily a set of inclusions and exclusions."*

**Round 2 - FAITHFUL.** All four landed as requirements rather than prose. Both open questions the
author declined to settle alone were ruled on: SC-006 stays (a cost display that silently stops being
true is a defect this feature would introduce - Principle XIV), and `image.yml` may stay uncached but
earns one Scope Out line so a later reader does not re-open it. Verdict: *"implement it."*

**The reviewer's aside for the GM**, recorded because it is a real limit on SC-001: remote runs are
infrequent (24 in the month this was written), so a cache that pays handsomely on a back-to-back pair
may still be cold most of the time it matters. The expected HIT RATE belongs beside the warm
before/after, or the measurement flatters itself.
