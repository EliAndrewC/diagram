# Feature 239 - tasks

Spec ACCEPTED by the GM at the five-round cap (2026-09-13). Every task is `research: rendering`: this
feature is tooling about how figures are measured and recorded, not about how a place was built.

## A. The decision is a function (FR-001 to FR-003)

- [x] T01 Move the house-style program into `scripts/_hm_house.py` as `decide(payload)`; `BRIT` and
      `PAIRS` move with it; the shell file becomes a wrapper (FR-001).
      research: rendering
      verify: DONE. DONE. _hm_house.report(payload), lifted mechanically with every substitution count asserted; PAIRS and BRIT module-level; the shell file a wrapper calling _hm_house.py decide
- [x] T02 `scripts/check-house-style-delta.py` imports the tables rather than regexing the shell file;
      the measurement scripts read them the same way (FR-001).
      research: rendering
      verify: DONE. DONE. check-house-style-delta imports BRIT; its test and the measurement harnesses read the module; _hm_house.py exempt in both lists, with a case
- [x] T03 A broken `_hm_house` warns at exit 0 and the stub section asserts the warning (plan P3).
      research: rendering
      verify: DONE. DONE. a module that fails to load warns at exit 0 naming the failure; the stub section passes on the warning
- [x] T04 No verdict changes: the 45 cases unchanged, and `make hookbench GUARD=house-style AGAINST=<the
      commit before T01>` prints zero changed verdicts; only house-style is edited (FR-002, FR-003).
      research: rendering
      verify: DONE. DONE. 46 house-style cases unchanged-green; make hookbench against 95179a93 (before the lift, spawned) printed 0 of 560 verdicts changed; no other guard edited

## B. Measuring a guard is cheap (FR-004 to FR-007)

- [x] T05 `scripts/_hookbench.py --refresh` builds the dated corpus with the codepoint prefilter; the
      committed fixture is its output (FR-004).
      research: rendering
      verify: DONE. DONE. _hookbench.py --refresh freezes the dated window with the codepoint prefilter, imported word table; tested from synthetic transcripts
- [x] T06 `bench GUARD` replays the corpus in process and prints verdict counts; `make hookbench`
      wires it (FR-005).
      research: rendering
      verify: DONE. DONE. make hookbench GUARD=house-style replays 560 commands in process in about 4 s
- [x] T07 `--against REF` prints the verdict diff in both directions; a historical baseline is spawned
      and says so (FR-006, plan P1). Reproduce feature 236's exemption diff against its pre-change
      commit (SC-004).
      research: rendering
      verify: DONE. DONE. --against prints the verdict diff both ways; a pre-decision ref is spawned and says so; against bf8149cc 65 changed in the exemption's directions, recorded as research R6
- [x] T08 A guard with no importable decision is refused by name (FR-007).
      research: rendering
      verify: DONE. DONE. a guard with no importable decision is refused by name, citing FR-001; tested

## C. Figures are derived (FR-008 to FR-011e)

- [x] T09 `spec-lint` check 5: a figure with a unit carries `m:<key>`, the key exists, the value matches
      numerically with rounding; reaches the operative sections, `research.md` and the Review history
      (round label accepted there); skips a backtick span; accepts a labeled one-shot; applies to
      features 239 and later (FR-008, FR-009, FR-009a, FR-009b, FR-009c, FR-010, plan P2).
      research: rendering
      verify: DONE. DONE. scripts/_spec_figures.py check 5, wired into spec-lint: key, known key, numeric match with rounding, operative sections plus research.md plus Review history, round label, backtick span, one-shot label, headings skipped, from feature 239 with tasks.md
- [x] T10 Check 5 refuses a `varies` on a counting unit, and a timing entry with no `quantity`
      (FR-011b, FR-011e).
      research: rendering
      verify: DONE. DONE. check 5 refuses varies on a counting unit and a timing with no quantity; tested
- [x] T11 `make figures`: re-runs each recorded command once, restores the file, fails a moved count,
      reports a timing outside its band, reports a load-refused timing as not re-measured (FR-011,
      FR-011a, FR-011c, FR-011d, plan P4).
      research: rendering
      verify: DONE. DONE. scripts/figures.py and make figures: re-runs each command once, restores the file, fails a moved count, reports a timing outside its band, reports a failed command as not re-measured
- [x] T12 This feature's own spec and research pass check 5 (SC-006).
      research: rendering
      verify: DONE. DONE. spec-lint over specs/239 exits 0; its first run found four real findings in this feature's own documents and one false positive (a heading), both fixed

## D. The contract (FR-012 to FR-014)

- [x] T13 `.claude/agents/spec-fidelity.md` carries NOT-REVIEWABLE, its not consuming a round, and the
      license to measure independently (FR-012, FR-013).
      research: rendering
      verify: DONE. DONE. spec-fidelity.md carries the FIGURES section for both modes: NOT-REVIEWABLE before the substance, not consuming a round, re-run by make figures, independent measurement kept
- [x] T14 `.specify/templates/tasks-template.md`'s review task names the measurements file and the
      refresh command (FR-014).
      research: rendering
      verify: DONE. DONE. the tasks template's review task carries a figures: line naming the measurements file and make figures

## Proof and the gate

- [x] T15 Every mechanism proven to FIRE by breaking it and watching a test go red (SC-010).
      research: rendering
      verify: DONE. DONE. 14 of 14 mechanisms broken in place and each watched go red, then restored: check 5 x8, make figures x2, the bench x2, the quote-aware split, the load-failure warning
- [x] T16 Root `CLAUDE.md` rows for `spec-lint` and house-style updated; `make hooks-test`, `make quick`
      and `make done` green; push (SC-011).
      research: rendering
      verify: DONE. DONE. root CLAUDE.md rows for spec-lint check 5 and the lifted house-style decision; make hooks-test green (the sync suite regressed on bytecode written by the lint's selftest into the tree it pushes - fixed), make done green over the whole suite, docs/make-targets.html regenerated for the two new targets
