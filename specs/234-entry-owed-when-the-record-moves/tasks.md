# Feature 234 - tasks

Spec ACCEPTED and FAITHFUL 2026-09-12 after six `spec-fidelity` rounds. Every task is classified
`research: rendering` or `research: physical`; nothing here is physical - this feature is about how the
record and the map's modals stay in step, not about how a place was built.

## Phase 1 - the report (FR-001 to FR-006)

- [x] T01 `scripts/_entry_owed.py`, modeled on `scripts/_review_owed.py`: for the delta against the
      merge base with `origin/main`, print every class whose `Entry:` names a research section whose
      BODY changed and whose own EXPLANATION PROSE did not. One class per line with the section that
      moved; `--why` prints the ruling; empty when nothing is named.
      research: rendering
- [x] T02 The prose/data split is DERIVED from `_base.py` `_DATA_TAGS`, never restated (FR-002,
      FR-010's shape rule). Both sides of the delta are parsed the same way - `ast` over
      `git show <base>:<file>` for the old side.
      research: rendering
- [x] T03 The report is actionable without further lookup: class key, research file and heading that
      moved, and the file and line of the docstring whose prose to re-read (FR-005).
      research: rendering
- [x] T04 Wire it at the two decision points and NOWHERE else - `make page-check` and
      `scripts/sync-with-main.sh` at push - asked fresh each time, never cached, never blocking
      (FR-003, FR-004). The script's docstring enumerates them as feature 231's does.
      research: rendering
- [x] T05 `make done` is NOT a channel, and a comment at the point of change says why (FR-006): it
      short-circuits at `Makefile:122` on exactly this delta shape, so a report there would ship green
      and never print.
      research: rendering
      VERIFIED by probe against the pre-233 base: names 6 classes whose section moved and whose prose
      did not, and correctly does NOT name `pig sty` or `duck pen`, whose prose moved in the same delta.
      Reports `key - file#anchor - prose at path:line`.

## Phase 2 - the gated half (FR-007 to FR-009)

- [x] T06 A class's `Entry:` heading MUST resolve to at least one research question - a gate test
      naming the class that fails, AND the push-time check in `sync-with-main.sh` beside
      `check-file-scale.py`, because a research-page-only delta owes no gate (FR-007).
      research: rendering
- [x] T07 The push-time call runs the checker's `--selftest` first and dies if it fails, as all three
      siblings at that call site do (FR-007, FR-011.2).
      research: rendering
- [x] T08 The declared-silence form (`fallow`) stays legal and is recognized EXPLICITLY, not by a
      non-match (FR-008), and `make audit` enumerates every entry taking it (SC-011).
      research: rendering

## Phase 3 - the judgment (FR-013, FR-014)

- [x] T09 `.claude/agents/entry-drift.md`: given a class's explanation prose and the current text of the
      section its `Entry:` names, report IN-STEP / DRIFTED / CANNOT-TELL. `model: opus`. Verification,
      never judgment about the map; it never edits.
      research: rendering
- [x] T10 Pre-authorize it in `container-scripts/append-system-prompt.md` (FR-013.2) - without this the
      default system prompt outranks the mandate, which is the documented 2026-07-27 failure.
      research: rendering
- [ ] T11 Its first real dispatch is feature 233's own pair, run and recorded: the `PigSty` modal
      against the section 233 rewrote, DRIFTED before the docstring rewrite and IN-STEP after (SC-007).
      research: rendering

## Phase 4 - the guidelines the GM asked for (FR-012, FR-014, SC-012)

- [ ] T12 `research/CLAUDE.md` and `interactive/classes/CLAUDE.md`: what is owed when a section a class
      was written from moves - dispatch `entry-drift`, then rewrite the prose or record why not to
      `dev/bypass-log/`; and plainly that `record-format` and `quote-check` are the changed research
      entry's own obligations and are NOT a check on any modal (FR-012, FR-014).
      research: rendering
- [ ] T13 A row in the root `CLAUDE.md` guard table saying the staleness half REPORTS and the heading
      half GATES (FR-012).
      research: rendering

## Phase 5 - proving it works (FR-010, FR-011)

- [ ] T14 Both checks proven to FIRE, by shape rather than against a hardcoded literal: a constructed
      delta names the class (SC-001), the prose-vs-tag distinction holds (SC-002), a broken heading
      turns the gate red AND is refused at push on a research-only delta (SC-003, SC-010), the declared
      silence does not swallow the rule (SC-004), an unnamed section produces no report (SC-005).
      research: rendering
- [ ] T15 Non-vacuity for BOTH matching surfaces separately - `_entry_owed.py`'s by a gate test, the
      heading checker's by its `--selftest` at gate and push (FR-011, SC-006).
      research: rendering
- [ ] T16 `make hooks-test`, `make done` and `make page-check` green (SC-013).
      research: rendering
