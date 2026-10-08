# Implementation Plan: Open work as features

**Branch**: none (main, `SPECIFY_FEATURE=330-open-work-as-features`) | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

One read-only script answers `make speckit-todo` from `specs/` alone (FR-001 to FR-003, FR-009). A one-time audit
settles the state of every existing feature by editing status lines with cited evidence (FR-004, FR-005), recorded in
[`audit.md`](audit.md). A one-time conversion files every `future-work/` entry as a feature (FR-006), re-aims every
pointer, deletes the directory (FR-007) and rewrites the rules that told sessions to add to it (FR-008). The
conversion script is kept in this directory, as feature 329 kept its sweep.

## Technical Context

**Language**: Python 3.14 (stdlib only), one Makefile target. **Testing**: pytest, in `tests/tooling/` (the tree for
tests that run tooling; it runs at the gate). **Scope**: `specs/` (247 directories), `future-work/` (33 entries in five
files), 41 live files that name `future-work/` (D6 says how they were counted). **Performance**: the command reads ~250 small files; under 2 s
(FR-003, SC-001) is measured at T-verify, not assumed.

## Decisions

- **D1 - The state rule** (FR-002). A feature is CLOSED when its `tasks.md` has at least one task and no open one,
  or when its spec's `**Status**:` value begins (case-insensitive) with `Done`, `Superseded by` or `Withdrawn`.
  Otherwise it is OPEN: FILED (no `tasks.md`, or one with no tasks), PLANNED (tasks, none ticked) or IN PROGRESS
  (some ticked). A task is a line opening `- [ ]`, `- [x]` or `- [X]` at column 0 - the form `scripts/gates/plan_gate.py` and
  `make tick` use; an indented box is part of its task. The closing words are one tuple in the script, which the tests
  import (FR-002: stated once). `Implemented` is NOT a closing word: features say it while holding open tasks, so the
  audit rewrites each to `Done` or leaves it open (the spec's edge case).
- **D2 - The command** (FR-001, FR-003, FR-009). `scripts/speckit-todo.py`, beside the other spec-kit commands
  (`claim-feature.py`, `tick-task.py`), run by `make speckit-todo`. Output: three headed groups (filed, planned, in
  progress), one line per feature - directory name, title from the spec's first heading, ticked/total where it has
  tasks, and `(no spec.md)` where it has none - then one line of counts per state. `ALL=1` adds the closed features
  with their closing reason, for the audit's own checking. Exit 0 always; it reports, it does not judge.
- **D3 - Settling a feature** (FR-004). Each open feature's status line is rewritten only with evidence written beside
  it in `audit.md`: `Done (YYYY-MM-DD): <what shows it - commits or the feature that did it>`, `Superseded by NNN`, or
  `Withdrawn (<ruling, date>)`. A feature with a mix keeps its truly open tasks open. Where no evidence or ruling
  settles it, the feature stays open and `audit.md` lists it for the GM (spec Assumptions). Tasks are not ticked by
  this feature - a tick asserts a verification that was not run here; the status line carries the closing.
- **D4 - The gm-assistant check** (FR-005). Every feature's spec and request are searched for gm-assistant's own
  subjects (webapp, Obsidian Portal, Discord, characters, backstories, the setting content) and for paths that exist
  only there; each hit is read. The pre-spec survey found none; `audit.md` records the search and its result, and
  any feature found is deleted.
- **D5 - Filing an entry** (FR-006). One `make claim` per filed feature. Its `spec.md` carries a title (the entry's
  heading), `**Status**: Filed - from future-work/<file>, "<heading>", 2026-10-08`, a one-line Input naming the GM's
  ruling (this feature), and the entry's text verbatim under `## The entry, as filed`. An entry that names separate
  pieces becomes one feature per piece (`compounds.md`'s "Research owed"). An entry that names an earlier feature is filed under a NEW number like
  every other and its spec names that feature as its history: the funerary-grounds entry says it "was feature 275,
  withdrawn", and 275's own record says the GM threw it out (*"I think you can get rid of it entirely"*; "The number
  stays spent") - filing into 275 would reopen what the GM closed (plan review, 2026-10-08). An entry found done, or disposed of by a cited
  ruling or a later feature, is closed in `audit.md` with the evidence and not filed.
- **D6 - Pointers** (FR-007). Every live file naming `future-work/` (41 files, 77 mentions on 2026-10-08, counted as
  `git grep -o 'future-work/'` over tracked files outside `specs/`, `dev/*-log/`, `dev/review-ledger.md`, the hook
  fixtures and `future-work/` itself) is
  re-aimed at the feature its entry became; a mention of the directory as a place to put work becomes the rule in
  D7. History keeps its words: `specs/`, `dev/*-log/`, `dev/review-ledger.md`, the hook fixtures.
  `scripts/gates/check-old-layout.py` refuses a new live mention of `future-work/` (the retired-path check the
  previous cleanup added, extended with this form), so a pointer arriving later from another clone is caught.
- **D7 - The rule** (FR-008). The root `CLAUDE.md`, `dev/lessons.md` and every doc that says "add it to
  future-work" say instead: defer work by filing a feature - `make claim SLUG=<slug>`, then a `spec.md` with
  `**Status**: Filed` - and find open work with `make speckit-todo`.

- **D8 - The guards that judge a feature's state follow D1** (FR-002, found at the landing push). Two push-time checks
  had their own notion of a feature's state, and each refused this feature's own result: (a) the stop-work
  procedure's in-progress refusal counted any open box, so the 19 features D3 closed by their status lines still read
  as in progress - it KEEPS its own open-box test (any open box, indented or not, as before) and exempts only a spec
  whose status line closes it, asking `speckit-todo.py --closed-by-status` so the closing words stay stated once; the
  exemption fails closed (an error or no answer counts as not closed) - plan review round 4 found that switching the
  refusal wholesale to `--state` would also have changed how boxes are read, letting indented open tasks land; (b) the review gate demanded a fidelity verdict of every spec a push touches, which no FILED spec can
  carry - a spec whose status opens `Filed` and that has no `tasks.md` is exempt, because it implements nothing, and
  gaining tasks ends the exemption. Each change has a case each way in its suite. The 22 old specs whose status lines
  D3 rewrote mostly predate the fidelity review (constitution XVI); their verdict is not owed for a status edit, and
  that one push carries `REVIEW_GATE_OK` with the reason rather than a gate exemption for `Done`, which would let a
  session skip review by writing the word.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, VII, VIII, IX**: N/A - no generated content, no in-world writing.
- **IV**: N/A - no SOURCE blocks move.
- **V**: PASS - no task touches a SOURCE block; `request.md` files are the GM's and are not edited.
- **VI**: PASS - each task names its verification: the script's tests, `make speckit-todo` before and after the
  audit, the old-layout check, `make done`.
- **X**: PASS - one stdlib module, ruff-clean and typed, behavior-named parametrized tests written red first that
  reach every branch (`scripts/` is outside the engine's coverage floor, so the tests own its correctness); well under
  the size bars.
- **XII**: N/A - the feature changes what no generator asserts.
- **XIII**: PASS - no shared engine code. The baseline is the current `make done` (green on 2026-10-08 at
  `cd33340f5`); zero new failures at merge.

## Project Structure

    specs/330-open-work-as-features/   spec, plan, tasks, audit.md (the settlement of every feature and entry),
                                       file_entries.py (the one-time conversion), request.md
    scripts/speckit-todo.py            the command
    tests/tooling/test_speckit_todo.py its tests
    Makefile                           speckit-todo target (and its `##` line in the generated reference)

## Complexity Tracking

None.
