# Implementation Plan: The implementation cross-referenced with the research, claim by claim

**Spec**: `specs/316-research-referencing/spec.md` | **Created**: 2026-10-02

## Summary

Claims are `Research:` lines in docstrings (and in a string literal after a constant, and in a marked HTML comment in a
procedure document). An engine module reads them from the syntax tree and fingerprints each unit's code; a script
fingerprints the research each claim cites, keeps the committed index, names what is owed, builds bundles, records verdicts,
prints the report, and holds the push. A gate test holds coverage. A new defined check, `impl-drift`, judges a bundle. The
walk-through page renders each stage's and step's claims as links with verdicts. Every unit in scope is claimed by writer
agents and checked by `impl-drift` once (the audit); feature 296 is closed with its two findings in the index as DRIFTED.

## Technical Context

- Engine: one new module `l7r/diagram/tools/claims.py` (parsing, units, code fingerprints, the import-graph scope, coverage)
  under the 100% rule, and `tools/placement_stages.py` (the walk-through). The scope is 245 modules (the spec Context's
  241 counted imports only; importing a submodule runs every package `__init__` above it, so those four are in scope too): 1,654 functions, 800 methods, 237 classes, 1,019 constants and 18 procedure sections - 3,728 units before
  inheritance, counted by `claims.all_units` on 2026-10-02. Every in-scope file gains docstrings: engine code, so the delta
  takes the GATED route.
- Scripts: `scripts/_claims.py` (research fingerprints, the index, owed, bundle, record, report, the push check),
  `scripts/claims-gate.sh` (the push), wired into `sync-with-main.sh`; Makefile targets.
- Reused, never copied: `_record_units.read_page` (a question's words less its intro - the reading feature 311 and
  `_entry_owed.findings` use), `_entry_owed.base_of`, `interactive.sources.research_questions` (pointer -> heading text and
  the built page's URL), `_hm_escape.py reason-ok`, the bypass-log writer shape of `entry-gate.sh`.
- Cost noted, not avoided: `pipeline/gencache.py` hashes each function's raw source and the module-level text
  (`_split_sources`), docstrings included, so the docstrings invalidate every scripted map's cache once (the shared `settlement/` and
  `waterfields/` modules are in scope); the gate re-rolls the scripted pool once on this delta. No map's output changes (docstrings and string-literal statements execute nothing).

## Decisions

**D1 - The claim grammar.** Inside a docstring, a line `Research:` opens the section; each following non-blank line indented
under it, up to a blank line or the end, is one claim:

    <label> - <backing>[: <what the code does>]

`<backing>` is one of: one or more question files separated by `, ` (`research/questions/NNNN-<id>.html` or
`.drawing.html`); `GUESS [<question file>]` (amendment 2026-10-03: the drawing page recording the guess); `UNRESEARCHED`;
`CONVENTION`; `DEVIATION <question file>[, ...]`; `CANON` (the GM's canon or ruling); `NONE`. The label is free text
without ` - `. A unit with one claim may write it on the header's own line, `Research: <label> - <backing>`, so a
function with no docstring gains one line, not three (the file-scale bar, below). A malformed line fails coverage with the grammar in the message. For a constant, the string literal statement
directly after its `Assign`/`AnnAssign` is its docstring. For a procedure section, each claim is one comment
`<!-- Research: <label> - <backing>[: ...] -->` anywhere in the section's text. (spec FR-001, FR-003)

**D2 - Units and inheritance.** `claims.units(source, path)` walks the syntax tree: every module-level and class-level
function and method, every class, every module-level constant (a target name that is upper case, `_` and digits allowed, an
optional leading `_`). A function nested in a function is part of its parent, not a unit. A unit with no claim of its own
takes the module docstring's claims (inherited). A module is in scope when `claims.scope` reaches it from
`l7r.diagram.hamletgen` through `import`/`from` statements at any depth, relative imports resolved (spec FR-002); each (unit, claim) is one index row, keyed
`<repo path>::<qualname>#<label>`. A procedure section is a unit keyed `<repo path>::<heading text>#<label>`; sections are
split at every `##`/`###`/`####` heading. (spec FR-002, FR-004)

**D3 - The code fingerprint.** For a function or method: `ast.dump` of its node with every docstring removed (its own and any
nested function's), without positions and WITHOUT ITS OWN NAME - so comments, blank lines, formatting and docstring prose do not
count, and a rename or a move with the code intact keeps the core (D7). For a class: its class-level statements only, methods
excluded (each method is its own unit), name removed. For a constant: its value node (its name is its key). Each is joined with
(a) the claim line itself, normalized for whitespace, and (b) `NAME=<dumped value>` for every in-scope constant the unit reads -
by its own module's name, through a `from x import NAME`, or as `<alias>.NAME` where the alias is an in-scope module (`from .
import law` then `law.JOIN_TOL`: 36 such reads in `hamletgen/ways` alone, grep 2026-10-02) - keyed by the constant's name,
not its module, so a file split that moves a constant owes nothing. The fingerprint WITHOUT the claim line is kept beside it as the unit's `core`, which D7 uses to
tell a drift the delta introduced from one that was already there. For a procedure section: its text with HTML comments other
than claim markers removed and whitespace collapsed. Callees are not followed (spec Decisions Recorded). (spec FR-004)

**D4 - The research fingerprint.** For each question file a claim cites: `_record_units.read_page`'s heading and its non-intro
blocks' words - exactly `_entry_owed.findings` - hashed; a claim citing several hashes them in order. A GUESS naming a page is
fingerprinted with it; a bare GUESS, UNRESEARCHED, CONVENTION, CANON and NONE have an empty research fingerprint. A pointer rewritten by `make fragment-move` must owe nothing
(spec Edge Cases), and a renumbering changes a question's NUMBER but not its heading id - so the claim line enters D3's
fingerprint with each pointer reduced to its heading id (`research/questions/0033-row-villages-resson.html` ->
`row-villages-resson`), and the research fingerprint is over the words, which a move does not change. (spec Edge Cases)

**D5 - The index.** `.claude/skills/diagram/dev/claims-index.json`, sorted keys, one object per unit:
`{"verdict", "code", "core", "research", "date", "note"}`. Verdicts: IN-STEP, DRIFTED, NEEDS-RESEARCH, MISLABELED,
UNCLAIMED, CANNOT-TELL (spec FR-005). Rows whose unit no longer exists are dropped by the next `record` (a renamed function is a new unit).

**D6 - Owed, bundle, record, report** (`scripts/_claims.py`, Make targets `claims-owed`, `claims-bundle`, `claims-checked`,
`claims-report`):

- `owed`: every unit with no row or whose `code`/`research` differ from its row; reason new / code changed / research
  changed; grouped by module, with the bundle command per group. (FR-006)
- `bundle --units <keys>|--module <path>|--owed`: writes `/tmp/l7r-check/claims-<slug>/` with `MANIFEST.md` holding, inline,
  each unit's source text (the function, the class's own lines, the constant's lines with their comment block, or the
  section), its claim lines, the constants it names with their lines, and each cited question's page and drawing page text;
  plus `units.json` with each unit's fingerprints as read. A unit not owed is refused unless `REASON=` is given (logged).
  (FR-007)
- `record --bundle DIR --reply FILE`: reads the check's reply lines `VERDICT <key> <VERDICT> - <note>` and writes the rows
  with the bundle's fingerprints; a key not in the bundle is refused. An `UNCLAIMED <path>::<qualname> - <decision>` line is written as a row of its own,
  keyed `<path>::<qualname>#<decision>`, verdict UNCLAIMED, with that unit's core as its code fingerprint; it is printed for the
  session too. It stays a finding until a claim covering the decision is written and checked: `record` drops an UNCLAIMED row
  of a unit when a later verdict on that unit's claims does not report it again (FR-009, spec US3 scenario 4).
- `report`: counts by verdict, owed count, then every non-IN-STEP row and every UNRESEARCHED claim with location. (FR-011)

**D7 - The push** (`scripts/claims-gate.sh`, in `sync-with-main.sh` beside `entry-gate.sh`, on both routes): refuse when (a)
any unit is owed; or (b) a row is a FINDING (DRIFTED, NEEDS-RESEARCH, MISLABELED, UNCLAIMED or CANNOT-TELL) at the head and, at
the merge base, the row was IN-STEP, or there was no row and the delta changed the unit's code or a cited question's findings -
an introduced finding. "Changed the code" is asked across keys, because a renamed unit has no base row under its new key: the
unit's nameless `core` (D3) matches NO base unit's core among the units whose `<path>::<qualname>` no longer exists at the head
(computed from the base's trees, read with one `git ls-tree` and one `cat-file --batch`) and no base unit's core under its own
key - so a move or a rename with its code intact is pre-existing, while a new copy beside an original that still exists, or an
edited unit, is not.
"Changed a cited question's findings": D4's research fingerprint of the question at the base differs from the head's. A unit
with a finding at both ends is pre-existing whatever changed (spec FR-010). Print without refusing every non-IN-STEP row that is not introduced (pre-existing; for
this feature's own landing, where the base has no index, every audit finding on unchanged code is pre-existing). CANNOT-TELL
is in the refusing set because an unanswered check is an owed check in substance. `CLAIMS_OK="<reason>"` discharges, to the
guard log and `dev/bypass-log/`. Silent when nothing in scope and no cited question changed. (FR-010)

**D8 - Coverage at the gate.** `tests/tooling/test_claims_coverage.py` runs `claims.coverage()` over `claims.all_units` - every
module `claims.scope` reaches (D2, spec FR-002) and the procedure sections (D9): no unit without a claim, no malformed claim, no pointer to a missing question file. Fixture
tests in `tests/tools/test_claims.py` cover the parser, units, inheritance, fingerprints (comment/format/prose-insensitive,
code/claim/constant-sensitive) to 100%. (FR-002, FR-003, SC-001)

**D9 - Procedure scope.** `buildings.md` (every section), and in `buildings/programs.md` the `### Magistrate's manor (county
magistracy)` and `### Country shrine (a village district's shrine)` sections with every heading under them. (FR-003)

**D10 - The walk-through.** `placement_stages.stage_doc`/`step_doc` stop a paragraph run at `Research:` as at `Steps:`, and the
page renders under each stage and step a "Research" list: each claim's label, then each pointer as a link to
`../../research/site/q/<heading id>.html` (the page sits at `dev/placement-stages/`, two levels under the skill root; the
heading id and text from `sources.research_questions`), then the class for a non-pointer backing, then the verdict from the
index. `tests/tools/test_placement_stages.py` asserts every stage and step renders a non-empty list and every link's target
heading id exists. (FR-012, SC-006)

**D11 - `impl-drift`.** `.claude/agents/impl-drift.md`: Opus at medium effort (it judges; `entry-drift`'s tier, the same kind of
comparison), `omitClaudeMd: true`, tools Read and Grep, reads a bundle's MANIFEST once. Per unit: IN-STEP / DRIFTED /
NEEDS-RESEARCH / MISLABELED / CANNOT-TELL with a one-line note, in the `VERDICT` line form; plus `UNCLAIMED` lines for a
physical decision in the bundle's code that no claim covers. A NONE claim on code that decides something physical is
MISLABELED. A GUESS or UNRESEARCHED claim is IN-STEP when the bundle's cited material is silent (a GUESS naming its drawing page, when
that page records the guess), a CANON claim when it names the GM's ruling, and MISLABELED when a question
in the bundle answers it. Added to `tests/test_agent_models.py`. The harness snapshots agent definitions at session start, so
this session dispatches it as a `general-purpose` agent on Opus told to adopt the file (docs/spec-kit-and-reviews.md, the
gotcha). (FR-008)

**D12 - The audit, in two independent passes.** Writers: `general-purpose` agents on Opus, one per module group (about
4,000-5,000 lines each, by subpackage - about 16 groups over the 74,331 lines counted in the spec Context; as run, 14 code groups and one for the procedures), each writing the `Research:` claims into its own files only - moving the
existing comment pointers and labels into claim lines, choosing pointers by grepping question headings, NONE for plumbing (a
module-level NONE where the whole module is), UNRESEARCHED where nothing in the record bears, no ruling of the GM decides it (CANON) and no GUESS label already
stood.
Then `make claims-owed` and one `impl-drift` per group bundle. MISLABELED and UNCLAIMED findings are applied to the claims, and a
NEEDS-RESEARCH finding's claim is relabeled UNRESEARCHED, or CANON where a ruling of the GM decides it (spec FR-013), each re-checked (two rounds at most, as review checks);
DRIFTED alone stands in the index, with any CANNOT-TELL the second round still returns. The procedure documents get
one writer and one check. Every pass a row in `docs/review-ledger.md` with its cost. (FR-013)

**D13 - Feature 296.** Its spec's Status reads "Superseded by feature 316 (2026-10-02)"; its stale pointers (homesteads/158,
/159) become `research/questions/0033-row-villages-resson.html`. The two claims - the row farm's frame against its street and
the far row's dry-field share - are written on the functions that decide them, and their rows carry DRIFTED with notes naming
296; the audit's check of those units is also SC-005's seeded drift. (FR-014)

**D14 - Seeded runs (SC-005).** One bundle of four known units (IN-STEP, 296's dry share as DRIFTED, a GUESS the record answers
as MISLABELED, an unclaimed decision), three `impl-drift` runs; recorded in `research.md`.

**D15 - Doctrine** (FR-015): the engine dev loop `l7r/diagram/CLAUDE.md` (claims on every new unit; the commands), the research
`CLAUDE.md` (a question's findings changing owes claim checks), the root guard table (`claims-gate.sh`, `CLAIMS_OK`),
`docs/guards.md`, `dev/reviews.md`. Every failure message names the command.

## Constitution Check

- XII research: no rendering decision changes; the audit labels decisions in the four classes plus UNRESEARCHED, CANON (the spec's
  recorded decision) and NONE. No research pass, so no physical task boxes are owed beyond the record's existing state.
- XIII no regressions: maps unchanged (docstrings only); the gate re-rolls the hamlet pool on the invalidated cache and must
  match its manifests.
- XIV fix defects: defects found in the TOOLING are fixed; DRIFTED map findings are recorded, by the GM's direction (spec
  Decisions Recorded) - an exception the spec carries, reviewed by `spec-fidelity`.
- XVI literal: every function, method, class and constant in scope carries a claim; nothing exempted.
- File scale (Principle X clause 13): six `hamletgen` files stand at 966-1,000 raw lines today (`consts.py` 966 with 90
  constants, `water/brook.py` 987, `homesteads/stages.py` 993, `ways/track.py` 994, `ways/settle.py` 1,000; `wc -l`,
  2026-10-02), so claims will carry some over the bar however compact. A file that crosses is SPLIT, as the clause prescribes
  (a cohesive part moved to a sibling module, re-exported where callers import it), as a mechanical move with no logic
  change; never a `FILE_SIZE_OK` (none of them is ordered data). `claims.py` and `_claims.py` stay under the bar.

## Risks

- Writer agents editing many files: each owns disjoint files; the session runs the coverage test after each group lands.
- Coverage speed: `claims.all_units` over the scope is about 4 s (measured 2026-10-02 after removing a copy per unit, 9 s
  before); the coverage test runs once per gate, inside `make quick`'s budget.
- Index churn: one JSON file shared by parallel clones; rows are sorted and independent, so conflicts are line-local.
