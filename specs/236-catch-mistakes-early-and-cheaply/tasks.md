# Feature 236 - tasks

Spec FAITHFUL 2026-09-12 after five `spec-fidelity` rounds (the fifth returned no changes; its four
record fixes are applied). Every task is classified `research: rendering` or `research: physical`.
NOTHING here is physical: this feature is about tooling that catches mistakes, not about how a place
was built, farmed or lived in. The measurements it rests on are in `research.md` R1 to R8 and were
taken before the spec was written.

**The review task shape this feature is delivering applies to this feature too** (FR-013, FR-014):
round 1 read the whole spec, every later round read only the changed passages plus a contradiction
scan, and the Review history records which.

## Phase 1 - the edit helper (item 1: FR-001 to FR-003)

- [x] T01 `scripts/_patch.py`: apply (anchor, replacement) edits to a file, EACH EDIT ITS OWN WRITE.
      An anchor matching zero or more than one time is reported and skipped; every other edit still
      lands; one line printed per edit. A CLI (`_patch.py <file>` reading a JSON list on stdin) and
      an importable `apply_edits(path, edits)` (FR-001).
      research: rendering
      verify: DONE. scripts/_patch.py: per-edit writes, report line each; used for real on _hm_make.py and spec-lint.py during this feature
- [x] T02 Anchors match WHITESPACE-INSENSITIVELY - four of six recorded misses spanned a line wrap
      (`research.md` R7) - and a match starting mid-line keeps the line's own leading indent, which
      is the bug the mid-session matcher had (FR-002).
      research: rendering
      verify: DONE. whitespace-insensitive anchors; the indent bug it hit an hour later is fixed and cased (a re-typed indent applied twice)
- [x] T03 `tests/tooling/test_patch.py`: the SC-001 case (three edits, the second anchor missing,
      the first and third landing), a wrapped anchor, a multiply-matching anchor, and the indent
      case. Prove the report fires by asserting on its lines, not on the exit code alone.
      research: rendering
      verify: DONE. tests/tooling/test_patch.py, 8 cases green; the per-edit-write and wrap rules each proved RED when broken
- [x] T04 Root `CLAUDE.md` names `_patch.py` beside the "Edit files with `Edit`" rule, as the
      scripted-sweep tool that does not replace `Edit` (FR-003), and records the tension FR-009
      names: this project's own rule prefers `Edit`, while a session run under an instruction
      preferring Bash loses the house-style guard that only Edit/Write used to see.
      research: rendering
      verify: DONE. root CLAUDE.md names _patch.py beside the Edit rule and records the Edit-versus-Bash tension

## Phase 2 - the shell guard (items 2 and 3: FR-004, FR-004a, FR-005, FR-006)

- [x] T05 `scripts/_hm_shell.py` - the pure detectors, one leaf so guard suites depend on what they
      use (feature 172's shape): `parse_error(cmd)` via `bash -O extglob -n`, `executing_backticks(cmd)`
      sharing the quote walk with `_hm_make.recipe_comment_hazards`, `commit_dash_m_problem(cmd)`,
      `coauthor_problem(cmd, cwd)`. Each returns the refusal text or None; no I/O beyond the parse and
      a `-F <file>` read.
      research: rendering
      verify: DONE. scripts/_hm_shell.py: parse_error, backtick_problem (walk shared with _hm_make via _hm_shape), commit_dash_m_problem, coauthor_problem; selftest green
- [x] T06 `scripts/shell-check-hooks.sh` (PreToolUse, Bash) runs the four detectors and REFUSES with
      the compliant form named: `$(...)` or single quotes for a backtick span, `git commit -F - <<'EOF'`
      for `-m`, the expected co-author address for a trailer. Escape `SHELL_CHECK_OK` with a reason
      through `escape_or_refuse`, checked FIRST so the guard can be repaired through the channel it
      guards; every branch records its own rule (FR-004, FR-004a, FR-005, FR-006).
      research: rendering
      verify: DONE. scripts/shell-check-hooks.sh: escape first via escape_or_refuse, one rule slug per branch, compliant form named in every refusal
- [x] T07 Wire it in `.claude/settings.json` beside the other Bash guards.
      research: rendering
      verify: DONE. wired in .claude/settings.json as a Bash PreToolUse hook; the GUARD_EDIT_OK reason rides in the command as a shell comment because the file is strict JSON
- [x] T08 `scripts/fixtures/bash-parse-corpus-2026-09.json`: the 238 commands of `research.md` R6,
      frozen from the transcript, each with what the tool result actually did. The extglob case
      (`shopt -s extglob` then `!(x)`) is added to it by hand, as R6 says it must be (SC-002).
      research: rendering
      measure: the replay itself is the measurement - it is re-run by the suite, not remembered
      verify: DONE. scripts/fixtures/bash-parse-corpus-2026-09.json: 238 commands frozen from the transcript plus the hand-added extglob case
- [x] T09 `scripts/test-shell-check-hooks.sh` + its table in `scripts/test_hooks_cases.py`: the
      corpus replay (exactly two refusals, both real syntax errors), SC-003's backtick cases (double
      quotes and `<<EOF` refused; single quotes and `<<'EOF'` quiet), SC-004's `-m` cases, SC-005's
      co-author cases, and the escape. Both directions, the quiet half longer.
      research: rendering
      verify: DONE. scripts/test-shell-check-hooks.sh: 26 cases plus the corpus replay through the hook - 2 parse refusals, both real run-time failures, 0 false positives, 23 caught by the -m ban
- [x] T10 `tests/tooling/test_guard_firing_log.py`: classify `SHELL_CHECK_OK` in the derived escape
      census and add the new guard's recording rows, or the census fails - which is the point of it.
      research: rendering
      verify: DONE. SHELL_CHECK_OK classified in the derived census; five shell-check rows and the house-style warned row assert the (event, rule) that lands

## Phase 3 - house style where the writes go (item 4: FR-007, FR-007a, FR-008, FR-009a)

- [x] T11 `scripts/house-style-hooks.sh` sees Bash: the payload is scanned and the session is TOLD
      through `additionalContext` at exit 0, never rewritten (D2 - a payload is often itself the
      spelling fix). The exemption is the house-style sense of a quoted span, NOT shell quoting, and
      search-command segments are dropped as `_hookmatch.py` drops them (FR-007, FR-007a). Matcher
      widened in `.claude/settings.json`.
      research: rendering
      verify: DONE. house-style hook reads the Bash payload, warns at exit 0, drops search segments, keeps prose quotations and code spans out
      SUPERSEDED by T27: the GM ruled on D2 and the payload is CORRECTED now, the warning kept for
      the command that is itself the fix.
- [x] T12 `scripts/check-house-style-delta.py`: scan the DELTA against the merge base plus every
      UNTRACKED file, reading the hook's own `BRIT` table so hook, check and ledger cannot disagree;
      word-bounded and case-insensitive as the hook matches; `--selftest` first (FR-008).
      research: rendering
      verify: DONE. scripts/check-house-style-delta.py: reads the hook BRIT table (44 words), delta plus untracked, selftest green
- [x] T13 Exemptions judged from the WHOLE FILE, never the changed line - a line inside a multi-line
      `<blockquote>`, a 「」 quotation or a `SOURCE` block carries no opening marker of its own - with
      the hook's full exemption set and `.clones/` excluded (FR-008a). A line MOVED within the delta
      is not flagged (FR-008b).
      research: rendering
      verify: DONE. exemptions judged from the whole file, moved lines excluded; both proved RED when broken
- [x] T14 It is a `make quick` PHASE, not a pytest test: testmon selects by changed code, and a scan
      whose own code never changes would sit unexecuted through the edits it exists to catch
      (FR-008c). `tests/tooling/test_house_style_delta.py` drives it over built git trees.
      research: rendering
      verify: DONE. a make quick PHASE, not a pytest test; tests/tooling/test_house_style_delta.py drives it over built git trees
- [x] T15 `.specify/templates/tasks-template.md` carries the "American spellings, hyphens only"
      checklist line the GM asked for in advance (FR-009a).
      research: rendering
      verify: DONE. tasks-template carries the American spellings, hyphens only checklist line

## Phase 4 - `spec-lint` (item 5: FR-010 to FR-011)

- [x] T16 `scripts/spec-lint.py` with `--selftest`: the four checks of FR-010, failing with file and
      line. Check 1 (a measured figure with no research pointer) reads the unit list from the spec;
      check 2 (`WITHDRAWN:` text still standing) needs twelve characters and a letter and exempts
      Decisions recorded and Review history; check 3 (an orphaned FR or SC) uses the
      `FR-\d{3}[a-z]?` grammar so `FR-007a` is its own id; check 4 (a stale task list) reads
      `tasks.md`.
      research: rendering
      verify: DONE. scripts/spec-lint.py: the four checks with a selftest; each fails with file and line
- [x] T17 Checks 1, 3 and 4 apply only to a spec that HAS a `tasks.md`, so the number claim and the
      milestone push the root `CLAUDE.md` protects still pass (FR-010a); check 2 reaches only
      `specs/` and D5 records what that leaves out (FR-010c).
      research: rendering
      verify: DONE. checks 1, 3 and 4 gated on tasks.md; check 2 reaches only specs/ - both cased
- [x] T18 THIS spec passes checks 1 and 3 - run it against `specs/236-*/` and fix the spec, not the
      rule, if it does not (FR-010b).
      research: rendering
      verify: DONE. spec-lint over specs/236 exits 0; test_spec_lint asserts checks 1 and 3 pass on this spec
- [x] T19 Wired at the gate (skill Makefile `static`, beside `check-file-scale.py`) and at push
      (`scripts/sync-with-main.sh`), over every `specs/` directory the delta touches, `--selftest`
      first as its siblings do (FR-011). `tests/tooling/test_spec_lint.py` proves each of the four
      fires and each stays quiet on the correct form.
      research: rendering
      verify: DONE. wired in the skill Makefile static phase and in sync-with-main.sh at push, selftest first; 15 cases green

## Phase 5 - the re-review, narrowed (item 6: FR-012 to FR-014)

- [x] T20 `.claude/agents/spec-fidelity.md` documents MODE 3, VERIFY: confirm each item a round
      claims to have applied, read every added or changed passage in full, and scan the rest only for
      contradictions those changes introduce (FR-012, FR-014).
      research: rendering
      verify: DONE. .claude/agents/spec-fidelity.md MODE 3 VERIFY, and its stale three-round cap corrected to five with the reset doctrine
- [x] T21 `.specify/templates/tasks-template.md` carries the review-task SHAPE - round, items,
      changed passages, mode - because the GM ruled doctrine alone will not hold it (FR-013).
      research: rendering
      verify: DONE. tasks-template carries the review-task shape: round, items, changed passages, mode
- [x] T22 Root `CLAUDE.md`: the guard-table rows for the shell guard, the delta check and
      `spec-lint`, in the form the other rows take - the rule, the mechanism, and what it cost to
      learn.
      research: rendering
      verify: DONE. three rows added to the root CLAUDE.md guard table, each with what it cost to learn

## Phase 6 - proof and the gate

- [x] T23 Every check is proven to FIRE by removing its mechanism and watching a test go red
      (SC-012) - recorded here, per check, as it is done.
      research: rendering
      verify: DONE. 13 of 13 mechanisms broken one at a time and each watched go RED, then restored; the script and its table are in the commit message
- [x] T24 `make hooks-test`, `make quick`, `make done` and `make page-check` green (SC-013); push
      through `scripts/sync-with-main.sh done`.
      research: rendering
      verify: DONE. make hooks-test (22 suites), make quick (3,432 tests), make done (whole suite, every pool map, all three coverage floors, roll census green) and make page-check all green; amendment rounds 1 and 2 recorded, round 2 FAITHFUL

## Phase 7 - the amendment (the GM 2026-09-12, on D2 and D5)

The GM ruled on the two things the first implementation left for them: the hook CORRECTS a Bash
payload except where the command is itself the fix, and the withdrawn-figure check scans the whole
tree. The counter resets to zero for a post-acceptance amendment (root `CLAUDE.md`, the five-round
cap), so the changed passages go back through `spec-fidelity` in VERIFY mode.

- [ ] T25 `specs/236-*/measure_bash_corrections.py` + `research.md` R10: replay every Bash command in
      the recent transcripts that this hook warns on, through the hook, and classify each British word
      by the shape it stands in - prose the command writes, the fix it applies, the pattern it searches
      for, the path it names. A correction is priced BEFORE it is built, because a command is not an
      edit and a wrong rewrite breaks work that was right (FR-007, FR-007b).
      research: rendering
      measure: the replay is the measurement, and it is re-runnable - the script is committed
- [ ] T26 `scripts/_hm_house.py`: the ranges of a Bash command, each one `corrected`, `warned` or left
      alone, with a selftest per class; the hook's word table and span pattern passed IN so there is
      one of each (FR-007, FR-007b).
      research: rendering
- [ ] T27 `scripts/house-style-hooks.sh`: the Bash branch corrects through `_hm_house` and returns
      `updatedInput`; the fix shape is reported at exit 0; `~/.claude/projects/` joins `/tmp` outside
      the project; the GM's verbatim `request.md` is found anywhere in a command's path list; the
      correction of a COMMAND records its own rule (FR-007, FR-007c, D9, D10).
      research: rendering
- [ ] T28 `scripts/spec-lint.py`: check 2 scans the whole tree - `git ls-files` plus kept untracked
      files, by suffix, holding out `scripts/fixtures/` and `dev/*-log/` - and the `WITHDRAWN:` marker
      must open a line (FR-010c, FR-010d, D5).
      research: rendering
- [ ] T29 The cases, in both directions: `scripts/test_hooks_cases.py` (corrected, warned, and every
      NAMED shape quiet), `tests/tooling/test_spec_lint.py` (the tree-wide reach, the verbatim-record
      exemption, the marker anchor) and `tests/tooling/test_guard_firing_log.py` (the new
      `corrected-command` rule). Each proved to FIRE by breaking its mechanism (SC-006, SC-008,
      SC-012).
      research: rendering
- [ ] T30 The record: spec D2, D5, D9, D10, FR-007b, FR-007c, FR-010c, FR-010d and their criteria; the
      root `CLAUDE.md` rows; the `spec-lint` docstring. Then `spec-fidelity` in VERIFY mode on the
      changed passages, with D9 and D10 put to it as exceptions to judge; then `make hooks-test`,
      `make quick` and the push (SC-013).
      research: rendering
