# Feature 177 - Finish warming the remote build

**Status**: DRAFT - not yet reviewed (constitution XVI)
**Request**: `request.md` (the GM's words, verbatim, plus the numbered items the instruction names)
**Predecessor**: `specs/175-warm-the-remote-build/` - this feature finishes what that one started and
pays two debts it recorded and left open.

## Why

Feature 175 established that *"the remote gate does strictly more work than the local gate for the
same commit"* and fixed one third of it - the generation cache. The phase records for the last green
remote gate (`03c8ce13`, 154 s) say where the other two thirds went:

| phase | s | share | cached? |
|---|---|---|---|
| PROVISIONING | 16 | 10% | yes - the ECR image |
| DOWNLOAD_SOURCE | 0 | 0% | yes - the S3 generation cache, 2.78 MiB |
| INSTALL (`git clone --filter=blob:none`) | 43 | 28% | **no** |
| BUILD - `hooks-test` | 60 | 39% | **no** |
| BUILD - everything else (merge, lint, roll, pytest) | 34 | 22% | partly |
| POST_BUILD | 1 | 1% | - |

**100 of 154 seconds are the two things nobody has cached**, and both are repeats rather than work:
`hooks-test` re-proves guard scripts that have not changed, because its freshness state lives in
`.git/` and a fresh container has none; and the clone spends 43 s fetching a 466 MB checkout of which
441 MB is 91 generated files that no gate phase reads.

Two further debts, both already written down and neither acted on. `expire-ci-junk` (prefix `''`,
14 days) expires **`verified/`**, the records `tree-not-already-verified` reads - so the skip that
exists to avoid paying twice silently stops working after a fortnight (`cachepolicy.py` raised this
as an open question for the GM on 2026-08-31). And 175's FULL-scope cache timing was never taken,
because `ci-check` requires an engine-path delta and none was owed - *"it rides on the next real
engine change"*, which has not come.

And every remote number on record predates feature 174: build `03c8ce13`'s own log says
`coverage floors: deferred to make done FULL=1`. A plain `make done` now runs `test-full` with the
100% floor. **We do not know what the remote gate costs today.**

## Scope

**In**: what a remote build repeats, what it downloads, what expires under it, the ability to
measure it on demand, and one guard that refuses the command its own message prescribes.

**Out - and this is the same line 175 drew**: what the gate VERIFIES. This feature removes REPEATED
WORK and UNREAD BYTES, never checks. Any change that would let a remote run verify less than the
same local run fails the request.

**Out**: untracking the 264 MB of generated `.html` from the repository. The GM's item 2 is
*"sparse or slim the checkout"* - an either/or - and this feature takes the sparse half, which is
reversible, loses no content and touches no file the GM browses. The slim half is priced in D7 with
its measured value so the GM can decide it separately; it is not decided here.

**Out**: `buildspec/image.yml` and Docker layer caching, for the reason 175 gave - the image build
runs no gate and warms no gencache.

## Functional requirements

### The repeats (the GM's item 1)

- **FR-001** A remote build MUST NOT re-run a guard suite whose guard, companion and derived
  dependencies are unchanged since a **previous remote build** proved them green. The freshness
  state (`<git-common-dir>/hooks-test/<guard>` and `gate-green-hooks`) MUST travel between builds.
- **FR-002** That state MUST remain CONTENT-KEYED, so a changed guard script re-runs its suite. A
  test MUST prove the re-run happens, by changing a guard and observing the suite execute.
- **FR-003** Only a state a BUILD wrote may be restored. A stamp from a laptop MUST NOT be able to
  reach a build - the property that makes FR-001 safe is that the remote gate skips only what the
  remote gate proved.
- **FR-004** The cache restore in `buildspec/run.sh` MUST NOT depend on `repo/.git` being absent to
  detect a restored cache. FR-001 puts a `.git` path INTO the cache, which is exactly the condition
  that killed build `a48b730d` (`mv bootstrap repo` moved bootstrap *inside* the restored directory;
  `cd repo` landed somewhere with no `.git`; exit 128, one billed minute).

### The download (the GM's item 2)

- **FR-005** A remote build MUST NOT download bytes that no gate phase reads. The excluded set MUST
  be **DERIVED and PROVEN** - each exclusion recorded with the evidence that nothing reads it - and
  a green remote build with the set applied is the proof. A set arrived at by inspection alone does
  not satisfy this.
- **FR-006** Every path any gate phase reads MUST be present in the build's checkout. Where the
  evidence for an exclusion is "no reader was found", the path stays: FR-005's burden is on the
  exclusion, exactly as 175's FR-008 put it on `.html`.
- **FR-007** The measured INSTALL time MUST be reported before and after, from the phase records.

### The measurements (the GM's items 3 and 4)

- **FR-008** A measurement run MUST be dispatchable ON DEMAND, without an engine-path delta and
  without inventing one. This is the mechanism 175 lacked and named as the reason its FULL timing
  went untaken; a debt that can only be paid by waiting for unrelated work is not a debt anyone pays.
- **FR-009** A measurement run MUST NOT be able to satisfy a push. It writes no `verified/` record
  and never pushes to main, so bypassing `route-is-gated` and `green-local-since-edit` buys a number
  and nothing else. Enforced on the BUILD side, in a diff, not by trusting the dispatcher.
- **FR-010** It MUST be paid, prompted and logged like every other paid target - the same class as
  `make ci-image`, whose prompt a session may answer under the GM's 2026-08-25 authorization, with
  the reason recording that it did and quoting it.
- **FR-011** A **post-174 remote reference gate** MUST be measured phase by phase and recorded
  against the local `make done` median on the same content (227.5 s, n=12, since 2026-08-31). Both
  numbers MUST come from runs whose gate ran the 100% coverage floor.
- **FR-012** The **FULL-scope cache** MUST be measured cold versus warm, with the payload size read
  off the built object - 175's D5 for the scope it could not reach. If the FULL cache does not pay,
  175's FR-010 ladder applies: narrow the set and re-measure; report and HOLD only if nothing pays.

### The expiry (the GM's item 4)

- **FR-013** Nothing that `tree-not-already-verified` reads may be expired by a rule meant for junk.
  The bucket's lifecycle document MUST be changed so `verified/` outlives a fortnight.
- **FR-014** The safety net MUST survive the change: after it, an unforeseen prefix MUST still
  expire on its own, because the GM's named failure is *"uploading many megabytes ... and then never
  cleaning it up"*. Removing the catch-all to save `verified/` trades one defect for the other.
- **FR-015** The applied document MUST be READ BACK from the bucket and recorded, and the reasoning
  for each horizon stated. `cachepolicy.py` MUST stop describing a state that is no longer true.

### The defects found on the way (constitution XIV)

- **FR-016** `scripts/main-tree-hooks.sh` MUST accept `( cd <clone> && <write> )` - the form its own
  refusal message prescribes - when the session is standing in main. Its `LEAVES` scan takes the
  last `cd` at a command position and does not count `(` as one, so the subshell never registers as
  leaving and the guard refuses correct work. A companion case MUST fail before the fix.
- **FR-017** The fix MUST NOT widen what the guard permits: a `cd` into the mirror root followed by
  a write, in a subshell or not, MUST still be refused, and the suite MUST prove it.
- **FR-018** A dispatch whose cached content differs from the reference gate's MUST NOT share its
  cache object. Measured 2026-09-03: the two `TARGET=tripwire` builds and the reference gate all
  used `cache/gm-assistant-check/reference`, so an operation's cache overwrites the gate's. It is a
  performance defect rather than a correctness one - the gencache is content-keyed, so a wrong entry
  can only MISS - and the record MUST say so rather than implying data loss.

### Not regressing anything

- **FR-019** Every refusal the CI dispatcher makes today MUST still be made, and its suite MUST
  still pass. The threat model in `l7r/diagram/ci/CLAUDE.md` is unchanged by this feature.
- **FR-020** A build with the cache deleted MUST still pass and take about the cold time (175's
  SC-004, re-asserted because FR-001 adds a second thing to the cache).

## Success criteria

- **SC-001** A warm remote reference gate is measurably faster than the same gate before this
  feature, and the saving is attributable phase by phase (INSTALL down by the clone, BUILD down by
  `hooks-test`) rather than to noise.
- **SC-002** A build whose guard scripts changed re-runs the affected suites; a build whose guards
  did not, does not. Both observed, not reasoned.
- **SC-003** The excluded checkout set is stated with the evidence for each exclusion, and a green
  remote build ran with it applied.
- **SC-004** Post-174 remote-versus-local is stated as two numbers from comparable runs, with the
  gate recipe named.
- **SC-005** The FULL cache payload is stated in MB from the built object, with cold and warm times.
- **SC-006** `verified/` records survive longer than 14 days, read back from the applied document.
- **SC-007** A `( cd <clone> && <write> )` from main runs; a `cd <mirror> && <write>` is still
  refused; both are cases in `scripts/test-main-tree-hooks.sh`.
- **SC-008** `make done` and `make hooks-test` are green, and the whole-tree 100% coverage floor
  holds.

## Assumptions

- **A1** The `[aws_admin]` credentials in `development-secrets.ini` can read and write the bucket's
  lifecycle configuration. VERIFIED 2026-09-03: the session key gets `AccessDenied` on
  `GetLifecycleConfiguration`; the admin key read both rules back.
- **A2** The `hooks-test` freshness state is a hash of file CONTENT only (`sha256sum` of the derived
  dependency set; `gate-stamp.hash_files` salted with `GATE_RECIPE`). Nothing in it is derived from
  the machine, the clock or the clone. This is what makes FR-001 safe and MUST be re-checked if the
  keying changes - the same standing assumption 175 made about the gencache key.
- **A3** Remote runs are infrequent, so a cache is often cold. The feature is judged warm and must
  behave well cold (FR-020).
- **A4** Measurement builds cost money: at $0.08/build-minute, FR-011 and FR-012 together are
  roughly four builds, about $1.50-$3.00 against a month-to-date of $16.24. Stated rather than
  assumed away.

## Decisions Recorded

Per constitution XII, each as **accurate**, **deliberate deviation** or **guess**, completed during
implementation:

- **D1** what travels in the cache for `hooks-test`, and the argument that a remote skip rests only
  on a remote proof (FR-001, FR-003)
- **D2** the excluded checkout set, with the evidence per exclusion and per retained path (FR-005,
  FR-006)
- **D3** the measurement mechanism: what it may bypass, what it may never do, and why that is not a
  hole in the five conditions (FR-008, FR-009, FR-010)
- **D4** the post-174 remote-versus-local numbers, with the gate recipe named (FR-011)
- **D5** the FULL cache: payload MB, cold, warm, and whether it pays (FR-012)
- **D6** the lifecycle horizons and the reasoning for each, read back from the bucket (FR-013,
  FR-014, FR-015)
- **D7** the repo-side slimming, PRICED not applied: the measured bytes and clone time it would
  save, what it would cost the GM in browsable content, and the recommendation
- **D8** the cache-location collision and its blast radius (FR-018)
- **D9** the guard fix, and why widening `LEAVES` does not widen what is permitted (FR-016, FR-017)

## Review history

To be completed - constitution XVI: reviewed against `request.md` by an agent that did not write it,
before implementation, up to five rounds.
