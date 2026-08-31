# Feature 175 - Warm the remote build

**Status**: specified, awaiting `spec-fidelity` review (constitution XVI)
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
- **FR-004** The cached set MUST account for the run MODE. `rollcache` is bypassed under
  `L7R_TESTS_FULL=1`, so `.gencache/rolls/` (54 MB, 24% of the directory) is never read by a FULL
  build, while a `reference`-scope build does read it (`make reference` calls `rollcache.report`).
- **FR-005** The cache key MUST be bounded - the number of distinct S3 objects the cache can ever
  hold MUST NOT grow with the number of commits, builds or branches. A key containing the commit SHA
  is specifically forbidden: it is the GM's named failure ("uploading many megabytes worth of
  content to Amazon S3 on every run and then never cleaning it up").
- **FR-006** The bucket holding the cache MUST carry a lifecycle rule that expires cache objects, so
  that abandoned keys disappear without anyone remembering to delete them. The expiry MUST be stated
  in the spec's Decisions Recorded with the reasoning for the number chosen.
- **FR-007** A cache miss, a cache-restore failure, an absent bucket or an expired object MUST NOT
  fail a build. The cache is an optimization; its failure mode is a slow build, never a red one.
- **FR-008** The `.html` question MUST be SETTLED before the artifact is excluded (research R6.1).
  "No reader was found" is not "no reader exists", and because `load()` DELETES an output its entry
  lacks, a wrong exclusion is destructive rather than merely lossy.
- **FR-009** The feature MUST report a measured before/after: remote wall time and cost for the same
  scope, cold versus warm, on comparable commits. A predicted saving does not satisfy this - three
  performance predictions made in this repository on 2026-08-31 were each overturned by measurement.
- **FR-010** If the measurement shows the cache does not pay - restore costing more than the
  regeneration it saves (research R6.2) - the feature MUST report that and MUST NOT ship the cache
  merely because it was built.

## Success criteria

- **SC-001** A second remote run of the same scope, on a commit whose engine content is unchanged,
  is measurably faster than the first, and the difference is attributable to cache hits rather than
  to noise.
- **SC-002** The uploaded payload is smaller than the naive 221 MB, and the spec states what was
  excluded and on what evidence.
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
- D2 the cache key and why it is bounded (FR-005)
- D3 the lifecycle expiry and why that number (FR-006)
- D4 the .html ruling and how it was settled (FR-008)
- D5 whether the cache paid, measured (FR-009, FR-010)
