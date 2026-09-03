# Feature 177 - Finish warming the remote build

**Status**: FAITHFUL (`spec-fidelity`, round 5 of 5) - cleared for implementation (constitution XVI)
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

**Out**: untracking generated renders from the repository - the 441 MB the checkout carries across
`.html` (264.0), `.svg` (115.2) and `.png` (61.9), not the `.html` third alone. The GM's item 2 is
*"sparse or slim the checkout"* - an either/or - and this feature takes the sparse half, which is
reversible, loses no content and touches no file the GM browses. The slim half is priced in D7 with
its measured value, over the whole slimmable set as measured, so the GM can decide it separately; it
is not decided here.

**Out**: `buildspec/image.yml` and Docker layer caching, for the reason 175 gave - the image build
runs no gate and warms no gencache.

**Out, and stated separately because it is a DIFFERENT question**: baking repository CONTENT into
the CI image. The GM asked *"does the image rebuild not matter because it only happens on a
dependency change, and the actual code itself isn't part of the image? OR is that not what we're
doing but it could be?"* - and the second half is a live competitor to the sparse checkout, since
both attack the same 43 s. It is declined rather than ignored, and D4 records why: an image carrying
the tree would go stale on every commit, so a build would still have to fetch the delta, and the
image would have to be rebuilt (paid, prompted, ~2 min) far more often than the dependency changes
that justify it today.

## Functional requirements

### The repeats (the GM's item 1)

- **FR-001** A remote build MUST NOT re-run a guard suite whose guard, companion and derived
  dependencies are unchanged since a **previous remote build** proved them green. The freshness
  state (`<git-common-dir>/hooks-test/<guard>` and `gate-green-hooks`) MUST travel between builds.
- **FR-002** That state MUST remain CONTENT-KEYED, so a changed guard script re-runs its suite. A
  test MUST prove the re-run happens, by changing a guard and observing the suite execute.
- **FR-003** Only a state a BUILD wrote may be restored. A stamp from a laptop MUST NOT be able to
  reach a build - the property that makes FR-001 safe is that the remote gate skips only what the
  remote gate proved. **A test MUST prove it**: a freshness state present only in a local tree
  cannot reach a build. The property is checked, not argued - in the one package whose whole job is
  refusing to take the dispatcher's word for anything.
- **FR-004** The cache restore in `buildspec/run.sh` MUST NOT depend on `repo/.git` being absent to
  detect a restored cache. FR-001 puts a `.git` path INTO the cache, which is exactly the condition
  that killed build `a48b730d` (`mv bootstrap repo` moved bootstrap *inside* the restored directory;
  `cd repo` landed somewhere with no `.git`; exit 128, one billed minute).

### The download (the GM's item 2)

- **FR-005** A remote build MUST NOT download bytes that no gate phase reads. The excluded set MUST
  be **DERIVED and PROVEN** - each exclusion recorded with AFFIRMATIVE evidence that nothing reads
  it. **A green remote build is NOT the proof, and must not be treated as one**: several checks here
  skip a file they cannot find or count what they found, so green tells you nothing about whether
  they still did the work. The evidence must show that every check touching an excluded path
  performs the SAME work remotely that it performs locally. The worked case is
  `tests/test_villages.py`'s raster-versus-viewBox agreement: it `continue`s past a missing render
  and ends on `assert checked`, so removing ALL eight frozen hamlet exhibits fails loudly by name
  while removing SEVEN passes green having checked one map. A set arrived at by inspection alone,
  or blessed by a green build, does not satisfy this.
- **FR-006** Every path any gate phase reads MUST be present in the build's checkout. Where the
  evidence for an exclusion is "no reader was found", the path stays: FR-005's burden is on the
  exclusion, exactly as 175's FR-008 put it on `.html`.
- **FR-006a** **The merge route pushes to main, and the sparse mechanism MUST NOT reach what it
  pushes.** `buildspec/merge.yml` runs the same `run.sh`, which ends in `git push origin HEAD:main`,
  so a mechanism that touched the index rather than only the working tree would land a commit
  missing the 441 MB of content the GM browses - the content this feature's own Scope declares out
  of bounds to touch. A merge build's pushed commit MUST contain every path tracked at its merge
  base. This MUST be PROVEN before the first merge-project dispatch, by comparing trees or tracked-
  path counts, and the proof recorded; an assurance that sparse checkout "only affects the working
  tree" is the claim being tested, not the test.
- **FR-006c** The excluded set is a ROSTER, and this project's rule is that a roster nobody can
  enumerate is one nobody revisits. It MUST live in ONE place and MUST be guarded: a test asserting
  that no engine or test module references a path under it, so a future test that starts reading an
  excluded path turns the gate RED rather than silently skipping in the build. This is the answer to
  "how would we ever notice", and without it FR-005's derivation is true on the day it is written
  and unmaintained after.
- **FR-007** The measured INSTALL time MUST be reported before and after, from the phase records.

### The measurements (the GM's items 3 and 4)

- **FR-008** A measurement run MUST be dispatchable ON DEMAND, without an engine-path delta and
  without inventing one. This is the mechanism 175 lacked and named as the reason its FULL timing
  went untaken; a debt that can only be paid by waiting for unrelated work is not a debt anyone pays.
- **FR-009** A measurement run MUST NOT be able to satisfy a push. It writes no `verified/` record
  and never pushes to main, so bypassing `route-is-gated` buys a number and nothing else. Enforced
  on the BUILD side, in a diff, not by trusting the dispatcher.
- **FR-009a** The route's condition envelope is CLOSED and stated here rather than chosen by an
  implementer. It MAY bypass **only** `route-is-gated`. Every other condition still refuses it:
  **`green-local-since-edit`** (the GM's own named case - *"make done could check whether the last
  thing that was run was an unsuccessful make done, in which case it should just short circuit
  immediately and refuse to run without even dispatching to AWS"*), `remote-enabled` (feature 132 -
  *"if it is disabled, then we do not use it as a gate. and we do not dispatch to it while we are
  doing iteration"*), `breaker-not-tripped` (the monthly hard stop), and - for the FULL-scope runs
  FR-012 requires - `door.py`'s committed `permitted` entry, never an environment variable. Nothing
  in this feature needs the `green-local-since-edit` bypass: FR-011 requires a local `make done` on
  the same content anyway, which sets it, and today's nearest precedent - a paid
  `ci-check TARGET=<operation>` - keeps the condition. A route that could spend money after a RED
  local gate, with the breaker tripped, or with remote off would contradict the GM's own words in
  features 130 and 132.
- **FR-010** It MUST be paid, prompted and logged like every other paid target - the same class as
  `make ci-image`, whose prompt a session may answer under the GM's 2026-08-25 authorization, with
  the reason recording that it did and quoting it.
- **FR-011** A **post-174 remote reference gate** MUST be measured phase by phase and recorded
  against **one local `make done` on the same commit the remote build tested**. Not a median:
  the 227.5 s figure quoted in `request.md` is a median over twelve runs spanning 22 s to 622 s,
  taken while the coverage floor was landing, so it is neither the same content nor uniformly a
  floor-running gate - and the GM's question is *"how much faster is it even to run on AWS than
  locally"*, which a denominator mixing warm short-circuits with full sweeps answers wrong. Both
  numbers MUST come from gates that ran the 100% coverage floor, and the record MUST say which
  commit each ran on.
- **FR-012** The **FULL-scope cache** MUST be measured cold versus warm, with the payload size read
  off the built object - 175's D5 for the scope it could not reach. If the FULL cache does not pay,
  175's FR-010 ladder applies: narrow the set and re-measure; report and HOLD only if nothing pays.

### The expiry (the GM's item 4)

- **FR-013** Nothing that `tree-not-already-verified` reads may be expired by a rule meant for junk.
  `verified/` MUST be removed from the catch-all's reach, and any horizon it does get MUST be set
  deliberately for what those records are FOR - evidence that a paid build passed - with the
  reasoning recorded under FR-015, never inherited from a rule written for junk. (A 15-day horizon
  would satisfy "outlives a fortnight" and leave the GM's complaint exactly where it was.)
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
- **FR-018a** `cache_location` is the function that BOUNDS the S3 object count, which is guard 1 of
  the 2 standing between this project and the GM's named failure. So the new dimension MUST be a
  finite, registered value: **the operation's registered name from `_invocation.OPERATIONS`, never
  the free-form `--target` string.** `__main__.py` validates only `a.target.split()[0]` and then
  passes the WHOLE string on as `ctx.operation`, so `TARGET="cohort SEEDS=8"` and
  `TARGET="cohort SEEDS=9"` are both legal and distinct - keying on it would grow the object count
  without bound, which is the exact failure 175's FR-005 exists to prevent. The ceiling MUST stay
  `projects x (scopes + registered expensive operations)`, and
  `test_the_cache_location_cannot_grow_with_the_number_of_builds` MUST be extended to VARY the new
  dimension: as written it enumerates projects x scopes and asserts `len(locations) == 4`, so adding
  a defaulted fourth parameter leaves it green while the bound is gone.

### Not regressing anything

- **FR-019** Every refusal `ci-status`, `ci-check` and `ci-merge` make today MUST still be made, and
  the `tests/tooling/ci/` suite MUST still pass **except where this feature deliberately widens what
  it guards, which is stated here rather than discovered by an implementer**:
  `test_the_cached_paths_are_what_a_HIT_needs` asserts
  `all(p.startswith("repo/.claude/skills/diagram/.gencache/"))`, and FR-001 requires two `repo/.git/`
  paths in that same cache block - so as it stands that assertion forbids FR-001 outright. It MUST
  be UPDATED, never deleted or loosened to "`.git` is allowed too": the new invariant is CLOSED -
  the cache carries the `.gencache/` paths feature 175's FR-002 derived, plus exactly the two
  freshness-state paths FR-001 names, and nothing else. A test that keeps its teeth.
  **The same is true of the LIFECYCLE half, and this is the THIRD place the blanket clause has bitten
  a requirement of this feature** (round 1 caught the route, round 3 the cache).
  `tests/tooling/ci/test_cachepolicy.py` pins the document FR-013 to FR-015 change: it asserts
  `len(rules) == 1` with `Filter == {"Prefix": "cache/"}`, indexes `Rules[0]` in two tests, pins
  `EXPIRE_AFTER_DAYS` in a third, and
  requires the module docstring to still name `expire-ci-junk` and `SHORTEST` - the very passage
  FR-015 says must stop describing a state that is no longer true. Those tests MUST be updated too,
  to an invariant that is likewise CLOSED: `lifecycle_configuration()` returns the WHOLE document;
  its rules are exactly the cache rule, the rule FR-013 gives `verified/`, and the FR-014 net, and
  nothing else; each is addressed BY ID rather than by `Rules[0]`; and the docstring assertion pins
  the state that is now true rather than being deleted. (**Implementation note, recorded because it
  changes the count and not the invariant**: the FR-014 net turned out to be TWO rules, not one. S3
  refuses `AbortIncompleteMultipartUpload` alongside an object-size filter - *"cannot be specified
  with Object Size"*, measured on the live bucket - because an upload in flight has no final size.
  So the net splits into a size rule and a multipart rule, and the closed set is four named rules.
  The split improves it: the multipart abort becomes universal where 175 had it on `cache/` alone.)
  **The measurement route of FR-008 is a NEW route
  and a change to the threat model**, not an exception inside the old one:
  `l7r/diagram/ci/CLAUDE.md` MUST be updated to describe it - what it bypasses, what it can never
  do, and why that is not a hole in the five conditions. Declaring the threat model unchanged while
  adding a route that spends money with no engine delta is the failure this project's own doctrine
  names: caution in the prose while the real change goes past unstated.
- **FR-020** A build with the cache deleted MUST still pass and take about the cold time (175's
  SC-004, re-asserted because FR-001 adds a second thing to the cache).

## Success criteria

- **SC-001** A warm remote reference gate is measurably faster than the same gate before this
  feature, and the saving is attributable phase by phase (INSTALL down by the clone, BUILD down by
  `hooks-test`) rather than to noise.
- **SC-002** A build whose guard scripts changed re-runs the affected suites; a build whose guards
  did not, does not. Both observed, not reasoned.
- **SC-003** The excluded checkout set is stated with affirmative evidence for each exclusion,
  including, for every check that touches an excluded path, what shows it still does the same work.
  A green remote build ran with the set applied - necessary, not sufficient.
- **SC-003a** The merge route's pushed tree was shown to carry every path tracked at its merge base,
  and how that was shown is named.
- **SC-004** Post-174 remote-versus-local is stated as two numbers from comparable runs, with the
  gate recipe named.
- **SC-005** The FULL cache payload is stated in MB from the built object, with cold and warm times.
- **SC-006** The applied lifecycle document, READ BACK from the bucket, shows `verified/` outside
  the catch-all's reach, and whatever horizon it carries was chosen for what those records are FOR
  with the reasoning recorded. Separately, an unforeseen prefix still expires (FR-014), and that is
  shown from the same document. "Longer than fourteen days" is NOT the bar - a 15-day horizon would
  meet it and leave the GM's complaint exactly where it was.
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
- **D2** the excluded checkout set, with the affirmative evidence per exclusion, what keeps each
  affected check doing the same work, and the reason for every retained path (FR-005, FR-006), plus
  how the merge route's pushed tree was proven complete (FR-006a). It MUST also record the sharpest
  instance of the class: `delta.engine_key_worktree` filters on `(root / p).is_file()`, so a sparse
  checkout that ever excluded an ENGINE path would silently change the key a build computes against
  the one a laptop computes. No path in the candidate set is engine content, so there is no live
  conflict - which is exactly why it is worth writing down before someone widens the set
- **D3** the measurement mechanism: what it may bypass, what it may never do, and why that is not a
  hole in the five conditions (FR-008, FR-009, FR-010)
- **D4** the post-174 remote-versus-local numbers, naming the commit and the gate recipe each ran
  on (FR-011) - plus the two halves of the GM's own sentence that a bare number leaves open: how the
  image rebuild amortizes (*"when we factor in the image rebuild?"*), and whether the tree could be
  baked into the image instead of sparse-checked out (*"the actual code itself isn't part of the
  image? OR is that not what we're doing but it could be?"*), the latter recorded as a priced
  DECLINE per the project's rule on accepted limitations
- **D5** the FULL cache: payload MB, cold, warm, and whether it pays (FR-012)
- **D6** the lifecycle horizons and the reasoning for each, read back from the bucket (FR-013,
  FR-014, FR-015)
- **D7** the repo-side slimming, PRICED not applied, over the whole slimmable set (441 MB, not the
  `.html` third): the measured bytes and clone time it would save, what it would cost the GM in
  browsable content, and the recommendation
- **D8** the cache-location collision and its blast radius (FR-018)
- **D9** the guard fix, and why widening `LEAVES` does not widen what is permitted (FR-016, FR-017)

## Review history

Constitution XVI: reviewed against the GM's own words in `request.md`, by an agent that did not
write it, before any implementation.

**Round 1 - CHANGES REQUIRED (3).** The reviewer verified the spec's claims against `decision.py`,
`dispatch.py`, `run.sh` and `main-tree-hooks.sh` rather than against its prose, and confirmed that
all four items and the defect were genuinely required rather than mentioned. Three defects:

1. **FR-019 forbade FR-008.** *"Every refusal the CI dispatcher makes today MUST still be made ...
   The threat model is unchanged by this feature"* - but today a measurement dispatch is
   `REFUSE(route-is-gated)`, so the no-regression clause outlawed the very mechanism items 3 and 4b
   need, and its second sentence was simply false: a route that spends money with no engine delta
   and no green local run IS a change to the threat model. The reviewer named this as the failure
   the project's own doctrine describes - caution in the prose while the real change goes past
   unstated. FR-019 now scopes the bar to the existing routes and REQUIRES `ci/CLAUDE.md` to
   describe the new one.
2. **The new route had no closed envelope.** FR-009 said what it bypasses; nothing said what it may
   never bypass. A measurement route that could dispatch with `remote off` or with the monthly
   breaker tripped would contradict the GM's own words in features 130 and 132. Now FR-009a, and
   it names `door.py` too, because FR-012 needs FULL-scope runs.
3. **Two requirements were satisfiable by writing a sentence** - the exact failure 175's round 1
   found three times. FR-003, the safety property the whole of item 1 rests on, had no proof clause
   while its neighbors FR-002 and FR-016 both did; it now demands a test that a local-only stamp
   cannot reach a build. And FR-013's *"outlives a fortnight"* was satisfied by changing 14 to 15,
   which leaves the GM's complaint exactly where it was; it now requires `verified/` out of the
   catch-all's reach with a horizon chosen for what the records are FOR.

The reviewer also ADJUDICATED the two things the author flagged for attack, both in the spec's
favor and for reasons better than the author's. The item-2 "Out" line is a faithful reading of an
either/or rather than a narrowing, because *"the disjunct chosen is the one that carries the
request's purpose"* - the sparse half delivers the whole of the item's stated value (66 s -> 4.0 s)
- and because deciding the slim half alone *"would be a session disposing of the GM's content"*.
FR-008/009/010 are necessary rather than invented: the reviewer read `decision.py` and confirmed
that `operation` only nulls the verified record and does NOT exempt a run from `route-is-gated`, so
without a mechanism items 3 and 4b are *"not merely awkward to deliver - they are undeliverable"*.
And FR-018 belongs here under Principle XIV. One inaccuracy was caught in passing: the Out line
priced the slim half at the `.html` third (264 MB) when the measured slimmable set is 441 MB.

**Round 2 - CHANGES REQUIRED (4).** A different agent, which confirmed round 1's three changes had
landed as requirements rather than prose, and then reached four things round 1 had not.

1. **The envelope bypassed one condition too many.** FR-009a let the measurement route past
   `green-local-since-edit` as well as `route-is-gated`, and nothing needed it: R7 establishes only
   `route-is-gated` as the blocker, FR-011 requires a local `make done` on the same content anyway
   (which sets the condition), and today's nearest precedent - a paid `ci-check TARGET=<op>` - keeps
   it. Dropping it would have removed a refusal resting on the GM's own words. Now one bypass, and
   the rest still refuse.
2. **SC-006 reopened the defect FR-013 had just closed** - *"survive longer than 14 days"* is met by
   changing 14 to 15, the exact form round 1 rejected one requirement earlier. The success criterion
   now grades what FR-013 requires, and covers FR-014 separately.
3. **`research.md` R4 stated something the code contradicts, and FR-005 leaned on the wrong
   instrument.** The author wrote that sparsing the frozen exhibits out would make the raster
   agreement test *"silently check nothing"*; the test ends on `assert checked`, so a TOTAL exclusion
   fails loudly. The real hazard is PARTIAL: eight frozen hamlet exhibits, `checked` only has to
   reach 1, so dropping seven passes green having checked one map. R4 is corrected in place, and
   FR-005 no longer treats a green remote build as the proof - for a check that skips what it cannot
   find or counts what it found, green says nothing.
4. **Nothing protected the merge route's push.** `merge.yml` runs the same `run.sh`, which ends in
   `git push origin HEAD:main`, and the Scope line's assurance that the sparse half *"loses no
   content"* was prose with no requirement behind it - on the one route that writes main, about the
   exact 441 MB the spec declares out of bounds to touch. Now FR-006a and SC-003a: the pushed commit
   must carry every path tracked at its merge base, proven before the first merge dispatch.

The reviewer also confirmed the round-1 adjudications hold, ruled FR-018 legitimate under
Principle XIV against the code (`cache_location` keys on scope; an operation keeps
`scope="reference"`), and found FR-006's *"where the evidence is 'no reader was found', the path
stays"* strong enough to foreclose the move R4 had flirted with.

**Round 3 - CHANGES REQUIRED (5).** A third agent, which confirmed round 2's four had landed and
then found five things neither earlier round reached. Two would have stopped the implementation dead.

1. **FR-019 forbade FR-001 - the same defect round 1 found in the route half, in the cache half it
   did not reach.** `tests/tooling/ci/test_cache.py` asserts
   `all(p.startswith("repo/.claude/skills/diagram/.gencache/"))` over every cached path, and FR-001
   requires two `repo/.git/` paths in that block. "The suite MUST still pass" made item 1
   unimplementable. FR-019 now states the widening and requires the assertion be UPDATED to a CLOSED
   invariant - the `.gencache/` set plus exactly the two freshness paths, nothing else - rather than
   deleted or loosened to "`.git` is allowed too".
2. **FR-018 changed the one function that bounds the S3 object count and required nothing about the
   bound** - and the author's own R10 had got this backwards. `__main__.py` validates
   `a.target.split()[0]` but passes the WHOLE free-form string on as `ctx.operation`, so
   `cohort SEEDS=8` and `cohort SEEDS=9` are distinct and a location keyed on it grows without
   bound: the GM's named failure, reintroduced by the fix for a different defect. Worse, the
   existing boundedness test enumerates projects x scopes and asserts `len(locations) == 4`, so a
   defaulted fourth parameter leaves it green. Now FR-018a: the REGISTERED name, and the test varies
   the new dimension. R10 is corrected in place.
3. **FR-011 named a baseline that failed FR-011's own condition.** It required both numbers to come
   from floor-running gates and then pinned the local side to a median of twelve runs spanning
   22 s to 622 s, taken across the days the floor was landing. The comparison is now one local
   `make done` on the same commit the remote build tested, with both commits named.
4. **`plan.md` carried three lines the spec had superseded**, each in the weaker form - the
   two-condition bypass, "a green remote build is the proof", and R4's retracted silent-skip
   sentence. A plan that grants an implementer authority the spec withholds is the smuggling
   direction that matters, and all three are reconciled.
5. **One sentence of the GM's opening question was dropped.** *"The actual code itself isn't part of
   the image? OR is that not what we're doing but it could be?"* - baking the tree into the image is
   the direct competitor to the sparse checkout, both attacking the same 43 s, and the Scope line's
   `image.yml` exclusion answered a different question. Now declined explicitly, with the reason, in
   Scope and D4.

The reviewer also checked A2 by measurement rather than argument (`gate-green-hooks` is `hash_files`
over `git ls-files -co -- scripts/*.sh scripts/*.py` through `content_id`; the per-suite stamp is
`sha256sum` over `_hookdeps.py`'s derived set; nothing machine-, clock- or clone-derived), and
flagged one residual asymmetry worth a line at the point of change: neither stamp is keyed to the
build IMAGE, so a `make ci-image` rebuild does not retire them - which is equally true on a laptop
after a toolchain upgrade, so it sits inside the spec's own bar. And it named
`delta.engine_key_worktree`'s `is_file()` filter as the sharpest instance of the class FR-005 asks
about; D2 now records it.

**Round 4 - CHANGES REQUIRED (2), both one-sentence fixes, both new substance.**

1. **FR-019's blanket clause bit a third requirement, in the half nobody had opened.** Round 1 found
   it forbidding FR-008 (the route). Round 3 found it forbidding FR-001 (the cache). Nobody had read
   `tests/tooling/ci/test_cachepolicy.py`, which pins the document FR-013 to FR-015 exist to change:
   `len(rules) == 1`, `Filter == {"Prefix": "cache/"}`, two tests indexing `Rules[0]`, a third
   pinning `EXPIRE_AFTER_DAYS`, and a
   docstring assertion demanding `expire-ci-junk` and `SHORTEST` stay named - the exact passage
   FR-015 requires to stop being true. An implementer landing FR-013 would have hit a red suite and
   had to choose between concluding the spec forbids the change and inventing an exception FR-019
   says shall not be invented. The widening clause now names the lifecycle tests and states their
   new CLOSED invariant: the whole document, exactly three rules, each addressed BY ID rather than
   `Rules[0]`, and the docstring re-pinned rather than deleted.
2. **`plan.md` still aimed the FR-011 measurement at the baseline FR-011 forbids by name** - *"against
   the local `make done` median (227.5 s)"* - the same smuggling direction round 3 named and the
   fourth line of that plan to need it. Now one comparable local run on the same commit.

Two asides were taken as well: FR-019's cross-reference to "FR-002's set" pointed at feature 175's
FR-002 rather than this spec's, and is now explicit; and `plan.md`'s roster-rot guard was scope the
plan carried and the spec did not, so it is now FR-006c, which is where the argument for it belongs.

**Round 5 - FAITHFUL.** A fifth agent verified eight load-bearing claims line by line against the
code (every one exact), confirmed round 4's two changes had landed, and then went looking for a
FOURTH place FR-019's blanket clause might bite - the failure rounds 1, 3 and 4 each found once. It
found none: nothing in `tests/` or `scripts/` pins the clone command, the restore detection, the
`MODE` set or the buildspec roster, so the three widenings the spec names are the complete set.
Verdict: nothing missing, nothing unrequested. Four asides, of which three were taken (the
`Rules[0]` count was off by one; the plan's "rules per prefix that has churn" now says exactly
three; the roster requirement is renumbered `FR-006c` so it no longer prints before `FR-006a`).

**The fourth aside is left for the GM rather than acted on**: FR-012 inherits 175's FR-010 ladder -
if the FULL cache does not pay, narrow the set and re-measure - which goes slightly past item 4b's
bare *"take the timing"*. It is the predecessor's own recorded rule and the reviewer flagged it as
worth a glance rather than a defect, so it stands; if a narrowed FULL cache set is not wanted, that
is a one-word change to FR-012.

**Cleared for implementation** (constitution XVI), at 5 rounds of a 5-round cap. Rounds 1 to 5
returned 3, 4, 5, 2 and 0 items, each round finding NEW substance rather than re-arguing the last -
which is the case CLAUDE.md's cap note describes as a review still converging. **But the count is
itself the signal the GM asked to watch** (*"if features start hitting five, the drafting is the
problem, not the cap"*), so it is recorded plainly here: this feature used the whole cap. The
pattern in the misses is one thing, not fourteen - **a blanket no-regression clause written before
the requirements it would collide with**. FR-019 said "everything still passes" three separate
times while three separate requirements of this same feature needed a guard widened, and each round
found one more. The drafting lesson: when a feature deliberately widens what a guard permits, the
widening is part of the requirement that causes it, not a sentence in a no-regression clause
written once and hoped over.
