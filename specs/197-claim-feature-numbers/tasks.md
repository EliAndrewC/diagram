# Tasks - 197 Claim feature numbers under a lock

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
about how a place was built.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: the verdict and each round's changes recorded in spec.md's Status line
- [ ] T02 `scripts/claim-feature.py` - derivation, lock, refusals, warning, dry-run, outputs (FR-001..005)
      research: rendering
      verify: `tests/tooling/test_claim_feature.py` cases 1-4, 6-9 green
- [ ] T03 the concurrency proof - twelve concurrent claims distinct (SC-001), and the test shown to
      FAIL with the lock removed (research.md R1)
      research: rendering
      verify: case 5 green; R1 records the duplicate count with the lock out
- [ ] T04 `make claim` in the skill Makefile, `claim` in the root forward list, `make docs` (FR-001, FR-007)
      research: rendering
      verify: case 10 green; `make claim SLUG=x PEEK=1` from this clone answers `198-x`
- [ ] T05 `make audit` prints the ledger's recent rows (FR-008)
      research: rendering
      verify: `make audit` shows the row this feature's own dogfood claim wrote
- [ ] T06 `.gitignore` carries the ledger (FR-002); `create-new-feature.sh` numbers through the tool (FR-006)
      research: rendering
      verify: `git -C <mirror> status --porcelain` shows no untracked ledger; `create-new-feature.sh --dry-run x` prints the tool's number
- [ ] T07 documents: constitution (Dev Workflow + 2.20.0), CLAUDE.md bullet, docs/session-clones.md,
      speckit-specify SKILL.md (FR-007); surfaces from the unfiltered grep in plan.md
      research: rendering
      verify: the grep for the old instruction returns only the history notes that quote it
- [ ] T08 research.md R2 - the collision census from main's history (184/186, 195/195, 107)
      research: rendering
      verify: each row cites the commit that shows it
- [ ] T09 `make done` green; `make hooks-test` stamp fresh; memory note written; land DIRECT
      research: rendering
      verify: the push lands and `make claim SLUG=x PEEK=1` from the other live clone answers `198-x`
