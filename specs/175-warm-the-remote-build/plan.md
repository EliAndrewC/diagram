# Feature 175 - plan

Spec: `spec.md` (FAITHFUL, `spec-fidelity` round 2). Measurements: `research.md`.

## Constitution Check

- **X (100% on pure logic)**: the dispatcher change is engine-adjacent Python in `ci/`, which has its
  own suite (`tests/tooling/ci/`, 99 cases against recorded AWS responses). New branches get tests
  there; no live AWS call in a test (Principle X's fixture rule - saved responses, never a transport
  mock).
- **VI (verify before "done")**: FR-009 forbids a predicted saving, so the feature is not done until
  a measured cold-vs-warm pair exists.
- **XII (record the why)**: D1-D5 in the spec, each labeled accurate / deliberate deviation / guess.
- **XIII (no regressions)**: FR-007 makes cache failure a slow build, never a red one; SC-004 proves
  it by deleting the cache object.
- **XVI (build what was asked)**: spec reviewed and FAITHFUL before any implementation.

## The finding that shapes the whole design

**The remote cache is populated BY THE REMOTE BUILD, not uploaded from a laptop.** CodeBuild's S3
cache saves the declared paths at the end of a build and restores them at the start of the next. So:

- The local 221 MB is **not** the payload and never travels. Research R2's directory listing measures
  a laptop, not a build.
- A remote entry is **gate-built**, so it has no `.png` at all (`gate_obtain` sets
  `DIAGRAM_SKIP_RENDER=1`). FR-003 is therefore satisfied *by construction* rather than by a filter -
  which is the stronger form, and the fact must be stated where someone might later "helpfully" add
  a raster to the cached paths.
- `.html` IS produced remotely (`DIAGRAM_SKIP_RENDER` spares only the raster), so it is the one
  artifact whose inclusion is a real decision. FR-008 must settle it either way.

## Approach

**Pass `cacheOverride` on `start_build`, do not edit the projects.** This is the design the
dispatcher already states for the buildspec: *"Rather than editing the projects (a state nobody can
review), the dispatcher passes the repository's own `buildspec/<mode>.yml` as `buildspecOverride`, so
the build runs whatever the tree under test says - reviewable in a diff, like every other guard
here."* A cache configured in the project console would be exactly the unreviewable state that
comment rejects, so the cache travels the same way.

**Reuse the existing bucket.** `ci_bucket = gm-assistant-ci-130071571821` already holds the build
mailbox and go-signals. A `cache/` prefix in it means one bucket, one lifecycle policy, one place to
look - and no new resource to create, name or forget.

**Bound the key by (project, mode), not by commit.** CodeBuild S3 caching writes one archive per
cache `location`. Using `cache/<project>/<mode>` gives at most `2 projects x {full, reference}` = **4
objects, ever**, which is FR-005 satisfied structurally rather than by a cleanup job. A SHA in the
location is the GM's named failure and must never appear.

## Task order, and why

1. **Settle `.html` (FR-008)** before anything is configured - it changes what the paths are.
2. **Configure the cache** (buildspec `cache:` block + `cacheOverride`), mode-aware per FR-004.
3. **Lifecycle rule** (FR-006) - before the first paid run, so nothing can accumulate even once.
4. **Tests** in `tests/tooling/ci/` against recorded responses: the override is passed, the location
   is mode-correct, and no location contains a SHA.
5. **Measure** (FR-009): cold run, then warm run on the same engine content; wall, cost, and the
   built cache object's SIZE per mode (FR-002a / D1a).
6. **Rule** (FR-010): if it does not pay, narrow and re-measure; if nothing pays, report and HOLD.

## Risks

- **R1 restore cost** - ~110 MB of `.svg` may cost more to fetch than five regenerations save.
  Mitigated by measuring per mode and narrowing rather than abandoning (FR-010).
- **R2 cache poisoning** - none available: gencache keys are content-derived (A2), so a stale entry
  MISSES, never serves wrong. Re-check if the keying changes.
- **R3 a wrong path list silently caches nothing** - a cache that never hits looks exactly like a
  cache that is not configured. SC-001 requires an attributable difference, so a no-op cache fails.

## BLOCKED ON THE GM: the lifecycle rule needs the admin key (FR-006)

The rule is written and tested (`ci/cachepolicy.py`, `tests/tooling/ci/test_cachepolicy.py`), but the
session **cannot apply it**, and should not be able to:

    AccessDenied: User: arn:aws:iam::130071571821:user/gm-assistant-ci is not authorized to
    perform: s3:GetLifecycleConfiguration on resource: arn:aws:s3:::gm-assistant-ci-130071571821

That is least privilege working as designed - the same shape as the `verified/` deny policy and the
circuit-breaker detach, both of which are the GM's to run at a terminal. **No attempt was made to
route around it**; a session that can grant itself bucket-policy rights is a session for which none
of the other guards mean anything.

**What the GM runs, once, with the admin key** (it reads the rule from the tested module, so the
applied policy and the asserted one cannot drift):

    python3 - <<'PY'
    import sys, pathlib, json, boto3
    sys.path.insert(0, '.')
    from l7r.diagram.ci import cachepolicy
    BUCKET = "gm-assistant-ci-130071571821"
    s3 = boto3.Session(profile_name="<admin profile>", region_name="us-east-1").client("s3")
    doc = cachepolicy.lifecycle_configuration()
    print(json.dumps(doc, indent=2))
    s3.put_bucket_lifecycle_configuration(Bucket=BUCKET, LifecycleConfiguration=doc)
    print("applied; read back:", s3.get_bucket_lifecycle_configuration(Bucket=BUCKET)["Rules"])
    PY

**Check before applying**: the bucket's EXISTING lifecycle rules could not be read either, so this
`put` would REPLACE whatever is there. The script prints the document first and reads it back after;
if the read-back shows a rule that was there before and is now gone, that is the thing to restore.

**Is it safe to ship the cache before the rule exists?** Yes, and the reasoning is worth stating
rather than assuming. The two guards are independent (`cachepolicy.py` docstring): the KEY bounds the
object COUNT at four, structurally, with no policy involved - so the cache cannot accumulate per-run,
which is the GM's actual named failure. The lifecycle rule bounds the AGE of an ABANDONED key, which
is a slower and smaller leak (at most four stale objects, ~110 MB each, and only if a scope or
project is retired). So the cache is safe to enable now and the rule closes the residual case.
