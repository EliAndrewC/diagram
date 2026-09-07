# Tasks - 197 Claim feature numbers under a lock

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
about how a place was built.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. spec-fidelity FAITHFUL at round 1; verdict and its one aside recorded in spec.md Status
- [x] T02 `scripts/claim-feature.py` - derivation, lock, refusals, warning, dry-run, outputs (FR-001..005)
      research: rendering
      verify: DONE. 25 cases green in tests/tooling/test_claim_feature.py (make test-file); every source, output and refusal exercised
- [x] T03 the concurrency proof - twelve concurrent claims distinct (SC-001), and the test shown to
      FAIL with the lock removed (research.md R1)
      research: rendering
      verify: DONE. 12 concurrent from one clone and across two clones distinct+consecutive; lock removed: 31 duplicates in 240 claims, lock present: 0 (research.md R1)
- [x] T04 `make claim` in the skill Makefile, `claim` in the root forward list, `make docs` (FR-001, FR-007)
      research: rendering
      verify: DONE. make claim SLUG=probe PEEK=1 answers 198-probe from this clone AND from diagram-html; root forward works; make docs regenerated (54 targets)
- [x] T05 `make audit` prints the ledger's recent rows (FR-008)
      research: rendering
      verify: DONE. make audit prints the Feature numbers claimed section (none yet on this host)
- [x] T06 `.gitignore` carries the ledger (FR-002); `create-new-feature.sh` numbers through the tool (FR-006)
      research: rendering
      verify: DONE. .gitignore carries .specify/feature-numbers.jsonl with the reason; create-new-feature.sh --dry-run --short-name probe-cnf prints 198-probe-cnf through the tool
- [x] T07 documents: constitution (Dev Workflow + 2.20.0), CLAUDE.md bullet, docs/session-clones.md,
      speckit-specify SKILL.md (FR-007); surfaces from the unfiltered grep in plan.md
      research: rendering
      verify: DONE. constitution 2.20.0 Dev Workflow paragraph, CLAUDE.md bullet, session-clones.md 1-3+5, speckit-specify step 3; the grep for the old instruction returns only the two history notes that quote it
- [x] T08 research.md R2 - the collision census from main's history (184/186, 195/195, 107)
      research: rendering
      verify: DONE. R2 written from git log --diff-filter=A/R: 14 numbers ever duplicated, 8 renumber commits cited by hash
- [x] T09 `make done` green; `make hooks-test` stamp fresh; memory note written; land DIRECT
      research: rendering
      verify: DONE. hooks-test 2 suites re-ran green (hooks area stamped); make done already-verified against unchanged engine content; test_make_docs 6 passed; test_claim_feature 25 passed; memory note written; peek from diagram-html answers 198-probe
- [x] T10 (GM follow-up 2026-09-07: *"Yes please fix 195 by deduplicating it"*) `--renumber` / `make claim
      RENUMBER=specs/NNN-slug` moves an existing directory to the next number under the same lock, with
      a `renumbered_from` ledger row; `195-target-descriptions-and-two-removals` -> 198 (the one with six
      references to its number, against the other's constitution clause, agents, tests and research
      index); every reference to the moved number rewritten; D3 amended - the tool still never renumbers
      on a CLAIM, the GM's ruling is what the RENUMBER form carries out
      research: rendering
      verify: DONE. 31 tests green incl. 6 renumber cases; hooks-test 2 suites re-ran green; make done already-verified (engine edits are comments only); ls specs dup check prints nothing; old directory name survives only in 197's history notes, the tool's docstring and the moved spec's own header
