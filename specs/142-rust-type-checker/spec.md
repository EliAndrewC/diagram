# Feature Specification: Rust-based type checker replaces mypy and its daemon

**Feature Branch**: `142-rust-type-checker` (no branch - `SPECIFY_FEATURE=142-rust-type-checker`)

**Created**: 2026-08-28

**Status**: Draft - the GM takes acceptance before anything merges (their words: *"I can take acceptance of this before we merge it back into main"*)

**Input**: the GM's request, verbatim, in [`gm-request.md`](gm-request.md). Summary: the mypy daemon
(`dmypy`) costs 380-600 MB of RAM per session clone and cannot be shared across clones, so several
concurrent sessions eat multiple gigabytes; the GM's hypothesis is that a Rust-based type checker is
fast enough that no daemon is needed at all. Look into the candidates, pick one, test it, report the
findings as an experiment; a new spec-kit feature; immaturity is acceptable as long as the tool is
not crashing - the project uses type checking to catch a few errors early, not heavily.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The experiment and its report (Priority: P1)

The GM asked a question - *is a Rust-based checker so fast that the daemon is unnecessary?* - and
for an experiment that answers it: evaluate the available Rust-based checkers, pick one, run it
against the diagram engine, and report what was found (speed, memory, what it catches that mypy
does not and vice versa, what had to change to make it work, what does not work).

**Why this priority**: it is the literal request. Everything else follows from its answer.

**Independent Test**: the report exists in this feature's directory with measured numbers taken on
this codebase (not vendor claims), names the candidates considered, says which was picked and why,
and states the answer to the GM's hypothesis in one sentence.

**Acceptance Scenarios**:

1. **Given** the diagram engine at this feature's base commit, **When** each candidate is run cold (no cache, no daemon) over the same set of files mypy checks today, **Then** its wall time, peak memory and diagnostic count are recorded beside mypy's cold, warm and daemon figures.
2. **Given** the measurements, **When** the report is read, **Then** it states whether the daemon is still needed and why.

---

### User Story 2 - The engine is checked by the chosen tool, with no daemon (Priority: P1)

A session running the quick target or the gate gets its type check from the chosen Rust-based tool.
No daemon process is started, so a session leaves no resident checker behind and the per-clone
memory cost disappears. The check is at least as strict as today's: an unannotated function
parameter or return, a value of one type assigned where another is declared, an unresolved name
or attribute - the errors the current strict configuration blocks - are still blocked.

**Why this priority**: this is the change the experiment exists to justify; without it the memory
is still spent.

**Independent Test**: after the switch, run the quick target and the gate and confirm (a) both are
green, (b) no checker daemon process exists afterwards, (c) an untyped `def` planted in an engine
module turns the check red.

**Acceptance Scenarios**:

1. **Given** a clone with no checker process running, **When** the quick target runs, **Then** the type check completes and afterwards no checker daemon process is running for that clone.
2. **Given** an engine file with a function whose parameter has no annotation, **When** the check runs, **Then** it reports an error and the target fails.
3. **Given** the CodeBuild gate image, **When** the gate runs there, **Then** the same tool with the same configuration runs the check (one configuration, two environments).
4. **Given** the engine as it is today, **When** the chosen tool reports diagnostics mypy did not, **Then** each is either fixed as a real defect (constitution XIV - fix defects where you find them) or recorded, at the point of change, as a checker limitation being suppressed and why.

---

### User Story 3 - The daemon machinery is retired cleanly (Priority: P2)

The sweep that kills orphaned daemons, the session-end hook that stops a session's own daemon,
and their tests exist only because the daemon exists. Once nothing starts a daemon, they are dead
weight; they are removed with their table rows and docs, and the mypy dependency itself leaves the
lockfiles so that no future session reinstalls the old path by habit.

**Why this priority**: leaving the daemon guard in place would misdescribe the system to the next
reader (it documents a cost that no longer exists) - but it does no harm to a running system, so
it ranks below the switch itself.

**Independent Test**: no file in the repository outside `specs/` and `docs/` history references the
daemon as a live mechanism; the guard table in `CLAUDE.md` no longer lists it; the hooks test
suite is green without its test.

**Acceptance Scenarios**:

1. **Given** the switch has landed, **When** the repository is searched for the daemon's sweep, hook and lockfile entries, **Then** none remain except as recorded history (this spec, the ledger of why it was retired).

---

### Edge Cases

- The chosen tool resolves the project's dependencies differently from mypy (e.g. does not look in the user site-packages, or treats a missing stub as an error where mypy was told to ignore it): the configuration must reproduce today's intent - `boto3`/`botocore` absent by design on the build image, third-party libraries without stubs not blocking the check.
- The engine's `l7r` package is a namespace portion with no `__init__.py` on purpose (`tests/test_namespace_portion.py`); the tool must not require one, and must give every file exactly one module identity.
- The tool honors `# type: ignore` comments written for mypy's error codes; where it does not, the comment is rewritten to the tool's form at the point of change, never dropped.
- The tool crashes or hangs on a file: that is the one thing the GM ruled disqualifying (*"as long as we have a tool that isn't actively crashing"*); it is recorded and the next candidate is tried.
- A newer release of the tool changes which diagnostics fire: the pin in the lockfile is what the gate runs; a bump is an ordinary lockfile change verified by a green gate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST evaluate the Rust-based Python type checkers available at the time (at minimum the two with active vendor backing) and record, for each, measured cold wall time, peak memory and diagnostic output on the same file set mypy checks today, beside mypy's own cold, warm-cache and warm-daemon figures measured the same way on the same machine.
- **FR-002**: The feature MUST pick ONE checker and record why, including what disqualified the others; the criteria are the GM's - fast enough to need no daemon, not crashing, and able to enforce the strictness the project relies on (an unannotated function is an error).
- **FR-003**: The engine's type check in the quick target and the gate MUST run the chosen checker as a one-shot process; no daemon or resident server process is started by any make target, hook or script.
- **FR-004**: The chosen checker's configuration MUST live beside the existing tool configuration (`pyproject.toml` under the skill) and MUST cover the same files the mypy configuration covers today; the file list is not shortened.
- **FR-005**: The check MUST report an error for an unannotated function parameter, an unannotated return, an unannotated class attribute, an assignment of an incompatible type, an unresolved name or attribute, and a call with a wrong argument type - proven by a test that plants each in a fixture and sees the check go red.
- **FR-006**: Every diagnostic the chosen checker raises on the engine as it stands MUST be resolved before the gate runs it: a real defect is fixed (constitution XIV); a checker false positive is suppressed at the point of change with a comment naming the rule and why; the split is listed in this feature's report.
- **FR-007**: The dmypy daemon machinery MUST be removed: the Makefile's daemon invocation and sweep, `scripts/dmypy-hooks.sh`, `scripts/test-dmypy-hooks.sh`, the `SessionEnd` hook entry, the `CLAUDE.md` guard-table row, and `mypy` from `requirements-dev.in` and the lockfiles it feeds; the CodeBuild image's import probe stops naming mypy.
- **FR-008**: The chosen checker MUST be installed the way the project installs every dev dependency (the `requirements-dev` lockfile, `setup-dev-env.sh`, the CodeBuild image) so a fresh container and the build run the same pinned version.
- **FR-009**: The findings report MUST be written in this feature's directory (`report.md`) and MUST answer the GM's hypothesis - daemon needed or not - in one sentence backed by the numbers, and list what the switch changed in what the check catches (gained and lost).
- **FR-010**: Nothing from this feature MERGES until the GM has accepted the report and the pick; the feature's last task is the GM's acceptance and stays open until they give it.

### Key Entities

- **Checker candidate**: a tool, its version, measured cold wall time and peak memory on the engine file set, diagnostic count, and the disqualifying finding if any.
- **Residual diagnostic**: a diagnostic the chosen checker raises on today's engine; classified as defect-fixed or false-positive-suppressed, with the file and line.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the switch, a session's clone holds no resident type-checker process between commands (0 daemon processes, measured by process listing after the quick target), against 380-600 MB per clone today.
- **SC-002**: The cold, no-cache type check of the whole engine completes in under 2 seconds (mypy cold: 12.7 s measured 2026-08-28), so the per-quick cost is no worse than the warm daemon's (~0.1-0.3 s) with nothing kept resident.
- **SC-003**: The quick target, the gate and the hooks test suite are green on the switched tree, and the planted-error test proves each of FR-005's six error classes fires.
- **SC-004**: The report lets the GM decide from one page: candidates, numbers, the pick, the residual-diagnostic split, the answer to the hypothesis.

## Assumptions

- "Rust-based mypy checkers" means the Rust-implemented Python type checkers - Astral's `ty` and Meta's `pyrefly` are the two with vendor backing at the time of writing; both are evaluated. No other candidate is known; if one surfaces during research it is measured too.
- "Different requirements" (the GM's *"different dentures have different requirements"*) is read as: the tool may need its own configuration, may not honor every mypy setting, and may resolve the environment differently - all in scope to adjust, none a reason to reject a candidate that is otherwise fast and stable.
- The whole-engine check is what the quick target runs (no incremental selection); at Rust speeds the tool's own caching, if any, is a bonus and never a requirement.
- Test files are not type-checked today and are not added to the file set by this feature (scope unchanged).
- The Decisions Recorded table is omitted: this feature draws and states nothing on a map.
