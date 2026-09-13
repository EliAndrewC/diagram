# Feature 239 - tasks

Spec ACCEPTED by the GM at the five-round cap (2026-09-13). Every task is `research: rendering`: this
feature is tooling about how figures are measured and recorded, not about how a place was built.

## A. The decision is a function (FR-001 to FR-003)

- [ ] T01 Move the house-style program into `scripts/_hm_house.py` as `decide(payload)`; `BRIT` and
      `PAIRS` move with it; the shell file becomes a wrapper (FR-001).
      research: rendering
- [ ] T02 `scripts/check-house-style-delta.py` imports the tables rather than regexing the shell file;
      the measurement scripts read them the same way (FR-001).
      research: rendering
- [ ] T03 A broken `_hm_house` warns at exit 0 and the stub section asserts the warning (plan P3).
      research: rendering
- [ ] T04 No verdict changes: the 45 cases unchanged, and `make hookbench GUARD=house-style AGAINST=<the
      commit before T01>` prints zero changed verdicts; only house-style is edited (FR-002, FR-003).
      research: rendering

## B. Measuring a guard is cheap (FR-004 to FR-007)

- [ ] T05 `scripts/_hookbench.py --refresh` builds the dated corpus with the codepoint prefilter; the
      committed fixture is its output (FR-004).
      research: rendering
- [ ] T06 `bench GUARD` replays the corpus in process and prints verdict counts; `make hookbench`
      wires it (FR-005).
      research: rendering
- [ ] T07 `--against REF` prints the verdict diff in both directions; a historical baseline is spawned
      and says so (FR-006, plan P1). Reproduce feature 236's exemption diff against its pre-change
      commit (SC-004).
      research: rendering
- [ ] T08 A guard with no importable decision is refused by name (FR-007).
      research: rendering

## C. Figures are derived (FR-008 to FR-011e)

- [ ] T09 `spec-lint` check 5: a figure with a unit carries `m:<key>`, the key exists, the value matches
      numerically with rounding; reaches the operative sections, `research.md` and the Review history
      (round label accepted there); skips a backtick span; accepts a labeled one-shot; applies to
      features 239 and later (FR-008, FR-009, FR-009a, FR-009b, FR-009c, FR-010, plan P2).
      research: rendering
- [ ] T10 Check 5 refuses a `varies` on a counting unit, and a timing entry with no `quantity`
      (FR-011b, FR-011e).
      research: rendering
- [ ] T11 `make figures`: re-runs each recorded command once, restores the file, fails a moved count,
      reports a timing outside its band, reports a load-refused timing as not re-measured (FR-011,
      FR-011a, FR-011c, FR-011d, plan P4).
      research: rendering
- [ ] T12 This feature's own spec and research pass check 5 (SC-006).
      research: rendering

## D. The contract (FR-012 to FR-014)

- [ ] T13 `.claude/agents/spec-fidelity.md` carries NOT-REVIEWABLE, its not consuming a round, and the
      license to measure independently (FR-012, FR-013).
      research: rendering
- [ ] T14 `.specify/templates/tasks-template.md`'s review task names the measurements file and the
      refresh command (FR-014).
      research: rendering

## Proof and the gate

- [ ] T15 Every mechanism proven to FIRE by breaking it and watching a test go red (SC-010).
      research: rendering
- [ ] T16 Root `CLAUDE.md` rows for `spec-lint` and house-style updated; `make hooks-test`, `make quick`
      and `make done` green; push (SC-011).
      research: rendering
