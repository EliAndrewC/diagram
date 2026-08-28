# Tasks: Rust-based type checker experiment (feature 142)

All tasks `research: rendering` - nothing here is about the world; tooling only.

## Phase 1 - the experiment (US1)

- [x] T01 [US1] measure mypy cold / warm / daemon and both candidates cold on the engine file set; probe strictness (untyped def) on both; probe environment resolution and `# type: ignore` handling - research R1-R4
- [x] T02 [US1] classify every residual diagnostic of the pick on today's engine (defect / limitation / defensive) - research R5; pick recorded with the reason - R6

## Phase 2 - the switch (US2, contingent - proceeding: pyrefly qualified)

- [x] T03 [US2] `[tool.pyrefly]` in `pyproject.toml` beside `[tool.mypy]` - same file list, search path, the boto3 ignore, the mypy-equivalent rules by name; verify: `pyrefly check` from the skill dir reports only the R5 residuals
- [x] T04 [US2] resolve the residuals: `bool(...)` on the two implicit-Any returns; `castle_civic.py:266` inspected and fixed; `None` initializations at `moat.py`, `dikes.py`, `packing.py`; `finish.py:468` annotated; `# pyrefly: ignore[...]` with the R5 reason at each `.get(k, Any-default)` site; verify: `pyrefly check` clean, then the quick target
- [x] T05 [US2] Makefile: `TYPECHECK = pyrefly check` at both call sites, `DMYPY_SWEEP` and the daemon comment block removed, header note updated; `requirements-dev.in` + `pip-compile` re-lock adds pyrefly (mypy stays); `Dockerfile.ci` import probe adds pyrefly; `setup-dev-env.sh` needs nothing (installs the lockfile); verify: the quick target green with no `dmypy` process afterwards
- [x] T06 [US2] `tests/test_typecheck.py` (tooling): a planted wrong-argument-type fixture fails `pyrefly check`; `project-includes` equals `[tool.mypy].files`; verify: the test red with the fixture's error removed, green with it

## Phase 3 - retire the daemon machinery (US3, contingent on T05)

- [x] T07 [US3] remove `scripts/dmypy-hooks.sh`, `scripts/test-dmypy-hooks.sh`, the `SessionEnd` entry in `.claude/settings.json`, the `CLAUDE.md` guard-table row and the dmypy paragraphs in `CLAUDE.md` / `.claude/skills/diagram/CLAUDE.md` / `dev/`; the `hooks-test` roster if it names the test; verify: `make hooks-test` green; `grep -rn dmypy` outside `specs/` and `docs/` finds only history

## Phase 4 - gate, report, acceptance

- [ ] T08 the gate once (engine tokens changed in T04 -> it re-keys); first run 2026-08-28: 1 failed / 3901 passed (the stale-render pair, report.md last section); second run after removing the three stale renders: GATE_LINE (gate still red - see tasks T08)
- [x] T09 `report.md`: the one-sentence answer, the R2 table, the per-quick delta, the pick, the enforced/not-enforced list (FR-005), the residual split (FR-006), the two questions reserved to the GM (mypy in the lockfiles; the constitution's `mypy --strict` wording, with the proposed replacement text) - FR-007b, FR-009
- [ ] T10 **the GM's acceptance** (FR-010) - stays open until the GM accepts the report and the pick in their own words; nothing pushes before (the lands-nothing guard enforces it). On acceptance: their rulings on the two reserved questions are applied as follow-up edits under this feature, then the gate and the stop-work procedure
