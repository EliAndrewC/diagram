# Feature 207 - the incremental gate, and content as data

**Status**: FAITHFUL (`spec-fidelity`, round 3 of 5; round 1: `name`/`covers` move too, the audit by kind not size; round 2: two enumeration slips in FR-004/FR-005a). (round 1: two changes in the content half - `name`/`covers` move too; the audit's criterion is what a reader sees, not a byte count).
**Request**: [`request.md`](request.md) - the GM's words verbatim, three messages.
**Research**: [`research.md`](research.md) - the gate's cost and its two settings (R1), the census of
content living in code (R2), every place an asset is enumerated (R3), and the soundness argument for
merging per-test coverage (R4).
**Predecessors**: 174 (the whole suite under the 100% floor); 135 (`make quick` selects by change);
188/189 (an asset edit and a modal's docstring owe `make page-check`, not the gate); 192 (the gate
rolls once); 196 (the ratchet's roll-cache classes); 205 (the glossary term that measured all this).

## Summary

Two efficiency improvements the GM bundled into one feature, both aimed at the same number: the eight
to ten minutes a plain `make done` costs on any engine change.

1. **Content is data.** Prose that a reader sees - the glossary, the sibling texts, each class's label
   and research pointer, the place card's wording, the placement-stages notes, the pool index's
   stylesheet - moves out of Python constants into data files (JSON, a `.css`, or the class's own
   docstring), so that editing it is not an engine change: it never opens the gate, never chills the
   roll cache, and owes what an asset edit owes. Data the engine EXECUTES on (the overlap taxonomy)
   stays code, on purpose.
2. **The gate selects by change, and the coverage floor still holds over the whole engine.** A plain
   `make done` keeps the coverage of the last full green run PER TEST, re-runs only the tests that
   executed a changed file, merges the fresh coverage over the kept coverage, and judges 100% and the
   hamlet floor over the merged result. A full run remains the baseline and the fallback.

## Functional requirements

### Content as data

- **FR-001** The glossary is `l7r/diagram/interactive/assets/glossary.json` - one object per term with
  its variants and definition; `glossary.py` loads it and exposes the same `GLOSSARY` mapping its
  consumers use today, so `page.glossary_for` and the tests are unchanged.
- **FR-002** The sibling pair texts are `assets/siblings.json`: a `texts` object of shared passages and a
  `pairs` list of `[class a, class b, text]`, where a text beginning `@` names a shared passage (the one
  text for four crop-dike pairs stays one text); `siblings.py` loads it into the same `_PAIRS` mapping.
- **FR-003** Each class's `name`, `covers`, `label`, `sources` and `entry` move into its docstring as
  `Name:`, `Covers:`, `Label:`, `Sources:` and `Entry:` tags beside `What:`/`Why:`/`Note:`/`Caveat:`;
  `parse_explanation` reads them and `Kind.feature()` builds the same `FeatureClass`. Only `key` stays
  a class attribute: it is the tag the engine writes on the ink and the CSS token, the one field that is
  identity rather than prose. The 51-class snapshot test still holds field for field.
- **FR-004** The place card's content - `KINDS`, `CROPS`, `_CROP_LEAD`, `CROP_SENTENCES`, `COLLISIONS`,
  `BASIS`, `BASIS_LEAD`, `ENTRY` - is `assets/place.json`; `place.py` loads it and formats the three demographic
  fields (`HAMLETS_PER_DOMAIN`, `VILLAGES_PER_DOMAIN`, `HAMLET_SHARE`) into the hamlet's text at load,
  so the numbers stay derived from `dwellings.py`.
- **FR-005** The placement-stages notes are `l7r/diagram/tools/placement_stages_notes.json`; the pool
  index's stylesheet is `l7r/diagram/pipeline/pool_index.css` and its section headings and tree
  banners `pool_index_text.json` beside it; each module loads its files. The NOTES-to-STAGES roster
  test stands.
- **FR-005a** THE AUDIT'S CRITERION is what a thing IS, never how long it is: prose a reader sees (or a
  record kept for a reader) moves to data; data the engine executes on stays code. A one-word edit to
  a sixty-byte lead-in re-opens the same gate the glossary did. So the page's fixed phrases move too,
  into `assets/page-text.json`: the caveat lead-in, the references lead-in, the convention lead-in,
  the four label phrases, and the two not-highlighted rulings lists (a record of the GM's rulings,
  never rendered - a record, like the sibling texts). `page.py` and `classes/_base.py` load them under
  the names their consumers and tests use today. Research R2 lists every module-level prose constant
  in the page package, the placement-stages tool and the pool index by this criterion, with a verdict
  for each; the KEEP rows are the keys the page executes on (`HIT_REGIONS`, `HIT_FROM_MARKS`,
  `PLACE_KEYS`, `CROPS`' keys), the parsers' regexes and markup templates, and FR-007's taxonomy.
- **FR-006** Every content file under `interactive/assets/` is a page asset everywhere an asset is
  named (research R3): gate-stamp's `page` area covers `assets/*`, and the render fingerprint hashes
  every file in that directory, so the pages regenerate on landing. A content-only delta routes DIRECT
  and owes a green `make page-check`; it is outside the engine key and outside the roll-cache key.
  `tests/tooling/test_measured_surface.py` proves the page area and proves the gate's area holds no
  content file.
- **FR-007** The overlap taxonomy stays in Python, with the reason at the top of the census (R2): the
  engine executes it.
- **FR-008** The rendered page, the pool index and the placement-stages page are byte-identical before
  and after the moves, on the reference hamlet (a regeneration and a diff, recorded in tasks.md).

### The incremental gate

- **FR-009** A green FULL test phase (`make done` with no baseline, a fallback, `make done FULL=1`,
  `make idle-tests`) records per-test coverage contexts (`--cov-context=test`) and, on green, saves the
  BASELINE under the clone's git directory: the coverage data and a manifest of every engine `.py`
  (semantic id, gate-stamp's) and every file under `tests/` (by bytes), with the tooling hash.
- **FR-010** A plain `make done` with a baseline runs INCREMENTAL: it computes the changed set against
  the baseline manifest, selects the tests whose baseline context executed a changed engine file, the
  tests in changed or added test modules, and every collected test the baseline never saw; runs only
  those (a pytest plugin deselects the rest after collection, so collection still imports everything);
  then removes from a copy of the baseline the contexts of the selected tests, the deleted tests, the
  files no longer in the tree, and the empty import-time context; combines the fresh data over it;
  and runs the same floors - `coverage report --fail-under=100` and the hamlet floor - over the merged
  data. Green stamps `diagram` exactly as a full run does.
- **FR-011** It falls back to FULL, saying which rule fired, when: there is no baseline; a changed
  engine file is not `.py` (a pool generator or manifest); a changed file under `tests/` is not a test
  module (`conftest.py`, `_scope.py`, a helper, `fixtures/`); the tooling hash moved; or the selection
  exceeds 60% of the collected suite. The baseline is never written by an incremental run (R4: no
  chaining).
- **FR-012** The run-log entry carries `mode` (`full` | `incremental`) and `selected` (`k/n`). The
  duration ratchet judges `done` over full-mode runs only; the plausibility floor for an incremental
  run is the absolute minimum, since a run that selects nothing legitimately finishes in under a minute.
  `make audit` shows the mode.
- **FR-013** Every phase before and after the test phase is unchanged: the static checks, the reference
  roll, hooks-test, the stamps, the pair hook, the push. `make quick` is untouched.
- **FR-014** Proof the gate FAILS when it should, on a fixture project run through the real planner,
  plugin and merge: (a) a changed function with a new uncovered line fails; (b) deleting the only test
  that covered a line fails; (c) a change that makes a line of an UNCHANGED module unreachable fails,
  because the test that reached it re-runs; (d) an unrelated edit selects only the tests that executed
  it and the merged report is 100%; (e) each fallback rule fires on its shape. Plus unit tests of the
  planner's pure functions over synthetic coverage data.
- **FR-015** Measured, in tasks.md: the cost of contexts on a full run against the run log's warm
  median; the baseline file's size; and three incremental runs on representative edits - a function
  only the polder path executes, a function of the core placer, a tools module - each with its
  selected count and wall clock against the full run.

## Success criteria

- **SC-001** An edit to `glossary.json`, `siblings.json`, `place.json`, a class docstring's `Label:`, the
  notes file or the stylesheet: `make done` answers `already verified`; `ci delta` classifies it
  DIRECT; the roll cache stays warm.
- **SC-002** The reference hamlet's page, the pool index and the placement-stages page are byte-identical
  across the moves (FR-008).
- **SC-003** The full gate green with contexts, the baseline saved; the next plain `make done` on a
  polder-only edit runs incremental, green, at a fraction of the full run's wall clock (FR-015).
- **SC-004** FR-014's five shapes each fail or fall back as stated, in the gate.
- **SC-005** `make done` green; landed GATED.

## Decisions Recorded

- **D1 - the baseline is the last FULL run, never a merged result.** R4. The selection grows between
  full runs and a full run resets it; nothing compounds.
- **D2 - file-level selection, from coverage's own contexts, not testmon.** R4: a changed file's
  baseline lines are meaningless, so every test that executed it must re-run; testmon's block level
  would keep stale lines. One tool, one data file.
- **D3 - 60% is the fallback fraction.** Above it the incremental run costs about what a full run does
  (collection, the reference roll and the floors are fixed costs) and gives up the baseline refresh. A
  knob in the planner with the reason beside it; not a measured optimum.
- **D4 - a class's name, covers, label, sources and entry go into the docstring, not a JSON.** The
  explanation, its heading, the claim about it and where it came from are one record, edited together;
  feature 189 already made the docstring the cheap-to-edit place. Only `key` stays an attribute: it is
  what the engine writes on the ink and what the stylesheet matches, so it IS code. (Round 1 of the
  review caught the first draft keeping `name` and `covers` as attributes on a ground - engine-written
  keys - that is true of `key` alone.)
- **D5 - the notes file and the pool-index stylesheet owe nothing at push.** They are outside every
  stamp area, like a docs edit; their tests run in `make quick` and at the next gate. Stated rather
  than hidden.
- **D6 - the taxonomy stays code.** FR-007.
- **D8 - the fast coverage core keeps its contexts by RE-ARMING its events at every context switch.**
  Found on the fixture project, 2026-09-07: Python 3.14's default sys.monitoring core disables a line's
  event after its first hit, so the second test to execute a line records nothing under its own context -
  four of eight contexts lost serially, two of eight under xdist, and never the one whose lines a fixture
  hit first. The first fix pinned the C tracer, which keeps all eight - and cost a FULL run 2.4x (research
  R6: the pytest phase 424 s -> 1,099 s, because the map rolls are traced line by line). The second fix
  keeps the fast core and calls `sys.monitoring.restart_events()` in the plugin at every context switch,
  which re-arms the disabled events so each context records every line it executes once; the per-context
  line sets are IDENTICAL to the C tracer's on the fixture project (12 of 12 rows), and
  `test_the_fast_core_keeps_every_context_once_its_events_are_re_armed` re-measures that on every gate.
  Cost: one event per line per context instead of one per execution.
- **D9 - a fixture gets its own coverage context.** pytest-cov attributes a session fixture's setup to the
  first test that asks for it, so forty tests reading a rolled hamlet would select as one. The plugin
  switches to `fixture:<name>` around every fixture setup, the planner selects by fixture closure, and the
  merge drops the contexts of fixtures affected transitively (a fixture whose input fixture changed).
- **D10 - the manifest hashes RAW bytes, not the docstring-stripped id.** A formatting-only edit moves line
  numbers, and the baseline's line data for that file would then lie; the short-circuit still keys on the
  semantic id, so a comment edit alone never reaches the planner.
- **D11 - an import-time line change is a full run.** A changed line the baseline's import-time context
  executed (a `def` line, a decorator, a module-level statement) changes what every importer sees; the
  planner diffs the old file against the baseline blob and falls back rather than reasoning about it.
- **D12 - the `-p` plugin is an excluded two-hook shim.** A `-p` module is imported before pytest-cov
  starts measuring, so its import-time lines - and those of everything it imports - are invisible to
  coverage on every worker. The first full gate reported 130 such lines (the planner's constants, the
  plugin's defs, `state.py`'s dataclass) as uncovered. `gate_plugin.py` holds two one-line delegates and
  carries `# pragma: exclude file` with the reason; `selection.py` is imported lazily from them and is
  measured. The 100% rule's exception clause is used exactly as written: a boundary that cannot be
  reached, stated at the point of change.
- **D13 - no backticks in a Makefile recipe comment.** The `: "..."` comment form is a double-quoted shell
  string, so a target name written in backticks is a command substitution; `make test-full` recursed 914
  deep and exhausted the container's process limit (2026-09-07, killed by a peer session). The comment
  now says so at the point of change.
- **D7 - the audit is by kind, not by size.** FR-005a; the first census used a 1.5 KB threshold and
  missed five reader-facing phrases, which the review found.
