# Tasks - feature 426, faster iteration

## Occasions

- none: no map, sheet, glyph or placement changes (tooling; the key change serves byte-identical maps)

## Tasks

- [x] T01 The claims wait ends when nothing can arrive: `make land` stops at once on any refusal waiting cannot cure, and on an owed claim with no claims check in flight; the in-flight marker written by `make claims-bundle`/`claims-triage` and cleared by `claims-checked`/`claims-triaged` (D1; FR-001, FR-002, FR-011; `scripts/land.py`, `scripts/record/claims.py`)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03+T04: T01: make land stops at once on a claims refusal no in-flight check can cure, and on an owed claim with no check marked in flight (claims_flight); T02: one docstring-blind code id (scripts/gates/codeid.py, an engine shim at pipeline/codeid.py), gate-stamp loading it by path; T03: the roll/map key and the render fingerprint on it, interactive/ by its bytes - a docstring-only edit to settle_the_web re-rolled 11 of 16 seeds before and 0 of 16 after (research R5), make cache-audit 3 audited 0 FAILED; T04: tooling_hash (module docstrings and non-.py raw), config_hash and record_cache.code_sha on it; claims.py split at the bar (claims_reply.py)
- [x] T02 One docstring-blind code id: `l7r/diagram/pipeline/codeid.py`, `gate-stamp.py`'s `content_id` calling it (D2; FR-003, FR-004)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03+T04: T01: make land stops at once on a claims refusal no in-flight check can cure, and on an owed claim with no check marked in flight (claims_flight); T02: one docstring-blind code id (scripts/gates/codeid.py, an engine shim at pipeline/codeid.py), gate-stamp loading it by path; T03: the roll/map key and the render fingerprint on it, interactive/ by its bytes - a docstring-only edit to settle_the_web re-rolled 11 of 16 seeds before and 0 of 16 after (research R5), make cache-audit 3 audited 0 FAILED; T04: tooling_hash (module docstrings and non-.py raw), config_hash and record_cache.code_sha on it; claims.py split at the bar (claims_reply.py)
- [x] T03 The roll and render keys on the code id, `interactive/**` by bytes (D3; FR-003, FR-005, FR-006, FR-012; `pipeline/gencache.py`, `pipeline/render_cache.py`)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03+T04: T01: make land stops at once on a claims refusal no in-flight check can cure, and on an owed claim with no check marked in flight (claims_flight); T02: one docstring-blind code id (scripts/gates/codeid.py, an engine shim at pipeline/codeid.py), gate-stamp loading it by path; T03: the roll/map key and the render fingerprint on it, interactive/ by its bytes - a docstring-only edit to settle_the_web re-rolled 11 of 16 seeds before and 0 of 16 after (research R5), make cache-audit 3 audited 0 FAILED; T04: tooling_hash (module docstrings and non-.py raw), config_hash and record_cache.code_sha on it; claims.py split at the bar (claims_reply.py)
- [x] T04 The other audited keys: `ci/state.py` `tooling_hash` (`.py` on the code id but module docstrings; non-`.py` raw), `ci/gate_config.py` `config_hash` (`.py` on the code id), `scripts/record/record_cache.py` `code_sha` (`.py` on the code id), each rule's reason at its point of change (the audit table; FR-004)
      research: rendering
      verify: DONE. landed in batch T01+T02+T03+T04: T01: make land stops at once on a claims refusal no in-flight check can cure, and on an owed claim with no check marked in flight (claims_flight); T02: one docstring-blind code id (scripts/gates/codeid.py, an engine shim at pipeline/codeid.py), gate-stamp loading it by path; T03: the roll/map key and the render fingerprint on it, interactive/ by its bytes - a docstring-only edit to settle_the_web re-rolled 11 of 16 seeds before and 0 of 16 after (research R5), make cache-audit 3 audited 0 FAILED; T04: tooling_hash (module docstrings and non-.py raw), config_hash and record_cache.code_sha on it; claims.py split at the bar (claims_reply.py)
- [ ] T05 The cohort's modes: `FAILED_FIRST=1`, `LAST_FAILED=1`, `EXITFIRST=1`, the `rolled N, served M` line, a partial run's record carrying forward the failures it did not roll and refused as a landing (D4; FR-007, FR-008; `tools/cohort_audit.py`, `scripts/gates/cohort_gate.py`, Makefile)
      research: rendering
      verify: tests on stubbed rolls: the order, the selection, the early stop (count left unrolled, exit 1), the carry-forward, `landing_shaped` refusing a partial record, a run with no last record rolling all and saying so; `make quick`; one real `make cohort N=10 EXITFIRST=1` on a seeded failure
- [ ] T06 A landing after a full run rolls no seed, pinned through `make cohort-landing`'s own path, from the clone and from a linked worktree (FR-012, User Story 3b)
      research: rendering
      verify: the test (the roll stubbed to count) red before T03's key and green after; one real `make cohort N=48 FRESH=0` then `make cohort-landing` printing `rolled 0`
- [ ] T07 `make probe`: the landing cohort, HEAD's fresh block and the pool in a worktree, every seed beside HEAD's stored verdict, each changed manifest field, `EXITFIRST=1` against HEAD (D5; FR-009; `scripts/measure/probe.py`, Makefile)
      research: rendering
      verify: tests on stubbed rolls and fixture manifests (every seed printed, a difference marked; a manifest field change listed by path; HEAD's block rolled once across two runs); one real probe on a worktree with a known regression; `make quick`
- [ ] T08 `make task-add` writes the D35 red exit and the alone-off table into a new section, and warns when a `SECTION=` file's item 6 lacks it (D6; FR-010; `scripts/task-add.py`)
      research: rendering
      verify: tests (a section written with no SECTION= carries item 6's wording and the table header; a SECTION= without it prints the warning and files it); `make quick`
- [ ] T09 The close: `make feature-report F=426 WRITE=1`, the GM shown the before/after counts and the landing's claims wait
      research: rendering
      verify: the feature report written; every task ticked
- [ ] GM review (make gm-reviewed F=426) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
