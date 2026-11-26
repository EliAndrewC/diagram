# Measurement: 241 claims re-owed at a landing by the build-identity rule (451 T197), 2026-11-24

## What happened
- Three builders worked in ONE clone (/diagram/.clones/diagram-backlog) through the day: 451 T218-T222 (rust/gate claims/owed/reviews crates, agent files), 452's doc restatements (docs/buildings.md, docs/building-programs.md, pool notes), and 449's hamlet tasks (rust/phases). All of it is now committed (clone HEAD ahead of main f7c105b4a0); no rust/gate file is uncommitted.
- 452's builder restated 14 doc claims. Each section edit put the section's other claims up for a claims triage (mechanical clear or the claims-triage agent). Those answers were recorded by the clone's l7r-gate while 451's builder had uncommitted WORK IN PROGRESS in rust/gate (claims/index.rs, bundle.rs, reply.rs, carry.rs, later silent.rs, drawn.rs, core/record/effect.rs, bundle/check.rs).
- At the landing (make land F=449 T=T423,T424,T418,T422; gates green, 920 s), the push's claims gate, in landing mode, read each such answer as "triaged by an l7r-gate built with other builders' uncommitted code (...), not this landing's: re-judge it here (451 T197)" and listed it OWED: 241 claims (docs/building-programs.md 143, docs/buildings.md 98), plus hamlet rows. The push refused; the ticks were reverted.
- Outside landing mode the clone owes nothing: `make claims-owed` -> the 0097 page session's 3; `make claims-triage` -> "no claim is owed a triage". In landing mode (`L7R_LAND_ALONE=1 make claims-owed`): "244 claim(s) in 5 file(s) owe impl-drift", 241 of them for the mixed build alone. `L7R_LAND_ALONE=1 make claims-triage`: "no claim is owed a triage" - so the only route the tooling offers is a FULL impl-drift on 241 claims.
- Index profile of the answers carrying a dirty build: 229 `cleared` (by the tool, mechanically) and 57 `triaged` (by the claims-triage agent); every one of the 14 claims actually edited had a full impl-drift verdict recorded (13 IN-STEP, 1 known DRIFTED filed as 452 T24).
- The rule's code: rust/gate/crates/claims/src/claims/index.rs lines 609-650 (`Landing::mixed`): an answer is mixed when any path its build recorded as dirty has a blob different from HEAD:path in the landing tree. The WIP blobs of the morning differ from the committed files, so every answer of the day is mixed.

## Why this is the cascade the GM asked to end
- 451 T210 measured 147 claims forced after a generated doc regenerated and fixed it; the GM's rule (451 request.md, the convergence talk): only a claim-changing edit re-owes a check. Here 241 claims whose own text, pages and code did not change are forced to a full check by a trust rule, because builders shared a clone.
- The rule T197 exists for a real risk: WIP triage code clearing wrongly. The WIP here was the claims crate itself.

## Routes
A. Full impl-drift on the 241 (the tool's only offered route): about 240 claim judgments in 2 doc files, several large agent runs; changes nothing a reader sees if the clears were right.
B. Re-derive the clears with the CLEAN build and compare: reconstruct the pre-triage rows from main's dev/claims-index.json (f7c105b4a0) in a scratch worktree at the clone's HEAD, run the committed l7r-gate's mechanical triage there, and compare which claims it clears with the 229 the mixed builds cleared; for the 57 the agent triaged, re-run the claims-triage agent once on the clean build's bundle. If the sets match, the answers are re-recorded by the clean build (or CLAIMS_OK names the measurement).
C. CLAIMS_OK with the reason stated, no measurement.
D. A tooling fix first: landing mode re-runs the mechanical triage for a mixed answer instead of owing impl-drift (a clear the clean build reproduces is clean), leaving only what it cannot reproduce owed.

The session's proposal: B now (cheap, measured, and it is exactly "re-judge it here" by the clean build), and D filed as a 451 task so a shared clone cannot do this again; plus the process change for the GM's talk (one builder at a time on anything that touches claims, or a clone per builder).
