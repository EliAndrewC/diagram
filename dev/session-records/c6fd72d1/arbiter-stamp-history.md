# Measurement: the build stamp reads committed code as "other builders' uncommitted code" once a later commit of the same landing touches the file (2026-11-24)

## State
- ask:mixed-build-53-record-answers was ruled "continue" with a tooling fix; the fix is built and committed (451 T224, ca4706b4f8: a dirty path counts only inside the closure of the crates that build a bundle and record its answer). The 4 guest-quarters checks were re-run on a clean tree. The landing's claims were re-triaged by the committed build (147 tool-cleared, 42 agent-cleared, 2 impl-drift IN-STEP); `L7R_LAND_ALONE=1` claims gate and review gate pass in the landing worktree.
- A PRE-TEST of the record gate in the landing worktree (no landing run) still lists the same 49 answers (page session P7's checks on 0097 and 0338): "answered by an l7r-gate built with other builders' uncommitted code (rust/gate/crates/owed/src/record/owed/answers.rs, rust/gate/crates/owed/src/record/owed/tests.rs)". Those two files are inside the closure, so T224's rule does not release them.

## Why (traced in .git/record-checks/*.json)
- The 49 answers were recorded 17:22-17:26 UTC by the clone's gate binary, whose stamp reads `commit bb0c821c91` + 30 `dirty` paths with their blobs. That binary had been built while 451 T218-T222's work was uncommitted; when that work was committed unchanged (ff632b347c) the sources did not change, the binary was not rebuilt, and its stamp kept calling those files dirty. At 17:22 every stamped blob equaled HEAD, so the answers were NOT mixed.
- Later commits of the same landing edited some of those files: T223 (claims crate) and T224 (owed/answers.rs, owed/tests.rs). The rule compares each stamped blob with HEAD:path only, so the answers became "mixed" after the fact.
- Measured (the script's output: /home/agent/.claude/jobs/c6fd72d1/tmp/stamp-history.txt): for 49 of 49 answers, EVERY stamped dirty blob equals that path's blob at a commit of this landing's delta (origin/main f7c105b4a0..HEAD, 33 commits) or its base. The code that ran in recording them was committed code of this landing, since superseded by T224's edit to the same file (which changed only the mixed rule itself).
- The same mechanism re-owed the 191 claim answers an hour ago after T224 touched claims/index.rs (re-triaged since, cheaply, by T223's route).

## The loop
Each tooling fix the rulings required edits rust/gate, and each such commit turns every earlier answer of the day into a "mixed" one, because the rule knows only HEAD. Three rounds so far (241 claims; 53 record answers; 191 claims + these 49).

## Routes
A. Re-run P7's 49 checks (about 20 minutes of agents with live source fetches, and a second round of EDITs on pages already checked).
B. RECORD_CHECKS_OK for these 49, its reason naming this measurement (every stamped blob is committed code of this landing), then land; the rule's fix filed as a 451 task and built AFTER the landing with nothing else in the clone.
C. Fix the rule first: a stamped blob that equals the path's blob at any commit of the landing's delta (or its base) is this landing's own code, not another builder's uncommitted code; and a build's stamp is refreshed (or read as clean) once its dirty blobs all equal HEAD. With that rule the fix's own commit does not re-owe earlier answers (they match by history), so the loop ends. Cost: one more builder round (about 20-30 minutes) and one re-triage of the claims if the current rule sees the fix's edit of core/build.rs before the new rule is in the built binary.

The session's proposal: B now - the criterion is measured for all 49, and the landing has been refused or pre-refused five times today on this rule - and C filed and built immediately after the landing, alone in the clone.
