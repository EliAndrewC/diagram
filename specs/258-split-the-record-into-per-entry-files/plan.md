# Implementation Plan: The record is written per entry and assembled into the pages a reader opens

**Feature**: `258-split-the-record-into-per-entry-files` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), the GM's request in [request.md](request.md), the measurements in
[research.md](research.md).

## Summary

One derivation, in both directions. A **splitter** takes each committed record page apart into
per-entry fragments; an **assembler** puts the fragments back into the same page. The pair is the whole
design: the splitter is how the record gets into its new shape once, and thereafter it is the assembler's
inverse, which lets one test assert round-trip identity over the real record forever.

Three stages, each shippable, each proven on one page before the other eighteen:

| stage | what moves | proven by |
|---|---|---|
| 1 - the registry | `SOURCES.html` -> `research/sources/` | the assembled registry is byte-identical |
| 2 - the questions | `research/<page>.html` -> `research/<page>/` | every assembled page is byte-identical |
| 3 - the notes | `research/citations/<page>.html` notes -> `research/<page>/*.notes.html` | numbers allocated at assembly, notes in document order; the assertion-to-note pairing unchanged |

Stage 3 carries the renumbering, so it is the only stage whose output differs from what it replaced. It
differs in two ways, both declared and both consequences of the same decision: the numbers are
reallocated in document order, and on the 16 pages whose references are out of order (R4) the notes move
on the citations page to match (D4a). What is held fixed is the PAIRING - every assertion keeps the note
body it had.

## Technical Context

**Language/Version**: Python 3.11, the repository's own.

**Primary Dependencies**: none new. The parsing is the same regex-over-HTML the record's existing readers
use (`interactive/sources.py`, `interactive/citations.py`); introducing an HTML parser here would put a
second, differently-behaved reader of the record beside the one the engine already trusts.

**Storage**: files under `.claude/skills/diagram/research/`. 1,569 new fragments - 288 questions, 261
notes files, 925 for the registry and 95 of per-page scaffolding, counted rather than estimated; the
assembled pages stay exactly where they are. Stages 1 and 2 account for 1,251 of them (288 + 925 + 38
page scaffolding files); stage 3 adds the notes and the citations scaffolding.

**Testing**: pytest, in the interactive tree (`tests/interactive/`), plus `make hooks-test` for the guard.

**Target Platform**: the repository's container; the assembled pages are opened from disk by a browser,
as now.

**Project Type**: tooling over the research record. No map, no generator, no browser code.

**Performance Goals**: the assembly is not on the map-drawing path. The bar is that it does not show up
on the gate: `make record CHECK=1` over the whole record in under 2 s (R7 measures it; if it exceeds,
the plan's fallback is to check only the pages whose fragments the delta touched).

**Constraints**: byte-identity at stages 1 and 2, which forbids any normalization - the fragments hold
the record's bytes as they are, including its trailing spaces and its blank lines.

**Scale/Scope**: 19 research pages (288 questions between them, 2 to 39 each), 19 citations pages, 1,850
notes, 1,860 references, 920 registry entries (R1, R4, R5).

**Single-artifact target**: **`research/ways.html`** and its citations page - the smallest complete case
(5 questions, 26 notes, a `cities/`-style relative link absent, so stage 2's second artifact is
`research/cities/defenses.html`, which has them). Round trip on `ways.html` is sub-second; it is the
page every stage is proven on before the sweep.

**Every step is two steps.** Each stage below is written as: prove it on the one page, then run the
sweep over the other eighteen as its own task with its own verification.

## Performance bookends

**N/A - this feature changes no generator.** No map is drawn, no `.gen.py` runs, and no code on the
map-drawing path is touched, so `make perf` has nothing to compare. What this feature CAN slow is the
gate, so the plan measures that instead: R7 records `make done`'s phase timings before and after, and
the ratchet already fails a target that gets slower.

## Constitution Check

- **I. Accessibility-First Viewports**: N/A - no UI in this repository.
- **II. Bold, Intentional Design**: N/A - same reason; nothing this feature writes is seen on a map.
- **III. Pool Data Conventions**: N/A - no pool content is added or modified.
- **IV. One Canonical Home for GM Source**: **PASS, and it is the point.** Each entry of the record gets
  exactly one home, and the assembled page becomes a derivation rather than a second copy. No SOURCE
  block moves: the GM's own writing in this feature is `request.md`, which nothing derives from.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: **PASS** - no task touches content inside SOURCE
  markers. `request.md`'s SOURCE block is written once, by hand, from the GM's messages.
- **VI. Verify Before Reporting Done**: **PASS** - every task names its verification. The record is not a
  map, so `settlement-review` and `size-audit` do not apply; the checks that do are `make done`, the
  byte-identity diff, and - for the work's own subject - a `record-format` and a `quote-check` re-run over
  a fragment against their recorded whole-page runs (FR-026, task T25).
- **VII. De-Localized Generation by Default**: N/A - nothing is generated about a place.
- **VIII. Direct Voice Over Framing Distance**: N/A - no in-world content.
- **IX. Setting Integration**: N/A - no setting detail is asserted, invented or moved. Every byte of
  research prose survives the split unchanged, which stage 1 and stage 2 prove by diff.
- **X. Python Discipline (NON-NEGOTIABLE)**: **PASS with three commitments.**
  - ruff, ruff format, pyrefly and the 100% floor over the whole engine, as always.
  - **Red-green**: the assembler's tests are written against the real record before the assembler exists -
    the first test asserts `assemble(split(page)) == page` for `ways.html` and fails for want of a module.
  - **Clause 13, file scale**: the work splits naturally into `interactive/record/` as a
    directory-module - `fragments.py` (the layout: what a fragment is and where it lives), `split.py`,
    `assemble.py`, `store.py` (the fragments on disk, and every refusal), `notes.py` (keys, allocation,
    back links) - none near the 1,000-line bar, with the
    package's `__init__.py` composing the surface `tools/record_asset.py` imports. If any one file passes
    ~600 lines the split point is `notes.py`, which is the only part with real algorithm in it.
  - **Clause 15, the efficient form**: the assembler's one lookup that could go quadratic is "which
    fragment holds this text" (the guard, FR-028) over 1,569 fragments. It builds one index of
    fragment -> content once per invocation and asks it per candidate, rather than re-reading the
    directory per edit.
- **XII. Historical Grounding Bookends (NON-NEGOTIABLE)**: **N/A, stated precisely.** This feature
  changes nothing a generator asserts about the world: no element is added, removed or redrawn, and
  every assertion in the record keeps its text, its footnote and its evidence class. The only
  reader-visible change is the footnote NUMBERING, which is in the spec's Decisions Recorded table as a
  map drawing convention. There is therefore no Phase 0 grounding pass and no closing re-examination of
  a rendered artifact - the closing check is the byte diff.
- **XII, decisions for the reader**: **PASS** - the three decisions are in the spec's Decisions Recorded
  table, each with its class, its reason and where it is recorded.
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: **PASS with a measured baseline.** The record has an
  existing test bed - `test_record.py`, `test_footnotes.py`, `test_citations.py`, `test_sources.py`,
  `test_record_format.py`, `test_classes.py`, `test_place.py`, `test_page.py` - and this feature rewrites
  what they all read. Baseline: `git worktree add --detach /tmp/base258 HEAD`, **`make done`** there - not `make quick`,
  which cannot tell a new coverage-floor or `tests/full/` failure from an old one, and those are exactly
  the surfaces this feature moves - recorded in R6 before the first edit. The plan review of 2026-09-20
  caught T01 promising the weaker run. Zero new failures at merge; a pre-existing failure is
  ledgered, not fixed here.

## Project Structure

### Documentation (this feature)

```text
specs/258-split-the-record-into-per-entry-files/
├── spec.md
├── request.md           # the GM's words, verbatim
├── research.md          # R1-R4 the measurements, R5-R8 the design findings
├── measure.py           # R1-R4, re-runnable
├── plan.md              # this file
├── data-model.md        # the fragment layout and the grammar of each kind
├── quickstart.md        # how a session edits the record after this lands
├── contracts/
│   ├── record-cli.md    # the command, its modes, its exit codes and its messages
│   └── fragment-format.md  # what each fragment must contain, and every refusal
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source code

```text
.claude/skills/diagram/
├── l7r/diagram/interactive/record/       # NEW - the split and the assembly
│   ├── __init__.py                       # the surface: split_page, assemble_page, check_all
│   ├── fragments.py                      # where a fragment lives, and what its name means
│   ├── split.py                          # page -> fragments (the one-time migration, kept as the inverse)
│   ├── assemble.py                       # fragments -> page
│   ├── store.py                          # the fragments on disk: names, order, every refusal
│   └── notes.py                          # note keys, number allocation, back links
├── l7r/diagram/tools/record_asset.py     # NEW - the CLI behind `make record`
├── l7r/diagram/interactive/citations.py  # UNCHANGED as a reader (FR-029): the assembly hands it
│                                         #   an assembled page, as it reads a committed one today
├── research/                             # the record, restructured
│   ├── SOURCES.html                      # ASSEMBLED (stage 1)
│   ├── sources/                          # NEW - the registry's fragments
│   ├── <page>.html                       # ASSEMBLED (stage 2)
│   ├── <page>/                           # NEW - front, questions, notes, tails
│   ├── cities/<page>.html, cities/<page>/
│   └── citations/<page>.html             # ASSEMBLED (stage 3)
├── tests/interactive/test_record_assembly.py   # NEW
└── tests/tooling/test_record_edit_hooks.py     # NEW - the guard's companion

scripts/
├── record-edit-hooks.sh     # NEW - an edit aimed at an assembled page goes to its fragment
├── _record_prepass.py       # CHANGED - addresses one question, names the fragments
├── _quote_verbatim.py       # CHANGED - `--section`
├── _entry_owed.py           # CHANGED - reports the fragment path
└── sync-with-main.sh        # CHANGED - the assembly check joins the push gates

.claude/agents/
├── record-format.md, quote-check.md, entry-drift.md, source-applicability.md   # CHANGED - read the fragment
```

**Structure Decision**: the assembler is a directory-module under `interactive/`, beside the readers of
the record it must agree with (`sources.py`, `citations.py`), not under `tools/` - `tools/` holds the
thin CLI, as `citations_asset.py` does for `citations.py`. That is the existing shape for exactly this
job (a derived, committed asset with a `--check` mode), and following it means the gate wiring,
the staleness message and the test shape already exist to copy.

## The design, in the order it will be built

### D1 - One command, one direction each way, and ONE reader of the record

`make record` assembles; `make record CHECK=1` exits 1 and names every page whose committed bytes differ
from its assembly; `make record SPLIT=<page>` performs the one-time split of a page that is still whole.

**`citations.py` keeps reading an ASSEMBLED page and never a fragment** (FR-029). An earlier draft had it
read the notes from the fragments, which is the second parser of the record FR-029 exists to forbid; the
plan review of 2026-09-20 struck it. The works section depends on the notes and the notes depend on
nothing, so the assembly resolves it in two passes and no cycle survives:

1. assemble the citations page with the works region empty;
2. hand THAT page to `citations.derive()`, which reads it exactly as it reads a committed page today, and
   returns the works HTML and the hover script;
3. write the page with the derived works region in place, and the script beside it.

`make citations` keeps its name and delegates. This also retires the second Complexity Tracking entry the
first draft carried: there are not two derivations writing parts of one page - there is one assembly that
calls the existing derivation, and `_citations-works.html` is not a fragment at all.

### D2 - The layout

A page is a directory of fragments; a section that has entries of its own gets a directory named for it.
The registry is not a special case, it is a page whose `works-cited` section has 920 entries:

```text
research/sources/_front.html                     doctype, head, h1, intro - verbatim, and with it the
                                                 8,042-byte commented-out block that holds two dead <h2>
                                                 groups (R1): a heading in a comment is not a section
research/sources/010-works-cited.html            the section heading and its 213-byte intro
research/sources/010-works-cited/0010-<key>.html one registry entry each, gapped by ten
research/sources/020-attested-instances.html     one section: its <h2> and its prose
research/sources/030-setting-canon.html          the same
research/sources/_tail.html                      </main></body></html> - verbatim

research/ways/_front.html                        doctype, head, h1, intro, <hr> - verbatim
research/ways/010-<slug>.html                    one question: its <h2> and everything to the next
research/ways/010-<slug>.notes.html              that question's notes (stage 3)
research/ways/_tail.html                         the citations-page pointer and the closing tags
research/ways/_citations-front.html              head, h1, intro, and the works section's own opening
research/ways/_citations-mid.html                between the works block and the notes: `</section>`,
                                                 the `<h2 id="notes">` heading, `<section
                                                 class="footnotes"><ol>` - hand-authored bytes that
                                                 belong to no derivation and to no question
research/ways/_citations-tail.html               `</ol></section>` and the closing tags
```

**A research page is cut on `<h2>` ONLY.** 14 `<h3>` headings stand inside questions on six pages, and a
modal's `Entry:` tag may name one (`sources.py` resolves both levels), so a splitter that broke them out
would fragment a question and then trip the registry's own key refusal. Only the registry's roster has
entries of its own, and the level is passed in rather than guessed.

Full grammar, every field and every refusal: [data-model.md](data-model.md),
[contracts/fragment-format.md](contracts/fragment-format.md).

### D3 - Finding an entry without an index

The GM left this open. There is no index file: a source is found by its key with one glob
(`ls research/sources/*/*fei-1939*`), a question by a grep over its page directory. The reason is the one
this repository has paid for before - a hand-maintained index and the thing it indexes agree with each
other separately (`feedback_a_stale_literal_agrees_with_itself`). The ordering prefix is in the filename,
so there is nothing else to keep in step: the directory listing IS the order.

### D4 - Note keys, derived once and then stable

A note is named, not numbered. The splitter derives each key from the note's own leading source key -
`fei-1939`, then `fei-1939-2`, `fei-1939-3` where a page cites the same work more than once (635 of the
1,850 notes do, R5) - and, for the 326 notes that lead with no source key, from the question's slug and
the note's ordinal within it. After the split a key is whatever its author writes; the assembler only
requires that it is unique within its page.

### D4a - Stage 3 REORDERS the notes, and that is the change, not a side effect

A citations page lists its notes ascending by number. The research pages' references are not in
ascending order - 16 of 19 (R4) - so today a note's position on the citations page has nothing to do with
where its assertion stands. Storing each note beside its question and numbering in document order makes
the two agree, which means **stage 3 moves note bodies on those 16 pages**.

This is the renumbering, seen from the other page, and the plan states it rather than discovering it in a
diff. The consequence for the test: "strip the numbers and require equality" is WRONG on those pages and
would fail. What stage 3 actually holds is the pairing:

- the multiset of note bodies on a citations page is unchanged;
- every assertion on the research page still carries the same note body it carried before, matched by the
  reference's position in the page's text rather than by its number;
- nothing else differs.

**And the works list moves with them.** `citations.cited_keys()` builds the works section at the top of
a citations page by walking the notes in their page order, so reordering the notes reorders that list
too - measured on the real record by the plan review of 2026-09-20: the key ORDER changes on the same 16
pages, the key SET on none. That is a third reader-visible change at stage 3, and it is declared rather
than discovered. It is also the same correction as the renumbering, though not one a reader
is promised: the page's heading says only "The works cited on this page". It is the DERIVATION's own
contract that claims "in order of first citation" - `citations.py`'s docstring, `interactive/CLAUDE.md`
and `research/CLAUDE.md` - and today that means first in the notes' arbitrary order, afterwards first in
the reader's page. The reorder makes the documented contract true. What the test holds is the SET of works per page, and that its order equals
the document order of first citation.

SC-003 says the same thing in the spec, corrected by the same review.

### D5 - Numbering, and the two defects it fixes

The assembler walks the assembled page, allocates 1..N to references in the order they appear, and writes
those numbers into the reference, the note, the back link and the hover script. Two existing defects fall
out of doing this uniformly: 4 references carry no `id` at all, so no back link can return to them
(`archetypes.html`, `vegetation.html`); and 2 pages carry a duplicated reference id (R4, R5). Both are
fixed by construction, which is the cheapest possible fix and the one constitution XIV asks for.

### D6 - The gate and the push

The staleness check runs in two places for one reason: a record-only change takes the DIRECT push route,
which does not run the gate. `tests/interactive/test_record_assembly.py` fails on a stale page (the
gate); `sync-with-main.sh` runs `make record CHECK=1` before either route pushes (the push). This is the
same belt-and-braces `entry-gate.sh` already uses, for the same reason.

### D7 - The guard that keeps the fragments the source

`scripts/record-edit-hooks.sh` sees an `Edit` or `Write` aimed at an assembled page. It indexes the
fragments once, finds which hold the `old_string`, and: exactly one - rewrites `file_path` to it and says
so (the feature 204 shape: a rewrite costs no round trip); none or several - refuses, naming the
candidates. A `Write` to an assembled page is always refused: a whole-file write cannot be routed.

### D8 - Collecting the saving

The scripts learn to address one question (`--section` on the quotation prepass, a fragment path
accepted by the sections prepass, the fragment named in the drift report), and the four agent contracts
are rewritten to read the fragment they are given. The contracts are where this has to land: since
feature 256 a defined agent launches with `omitClaudeMd: true`, so `research/CLAUDE.md` never reaches it.
Then FR-026's re-run measures whether the scoped check still finds what the whole-page check found.

## Phases

**Phase 0 - the baselines** (T01, T02). The detached-worktree `make done` baseline (R6); the
gate-cost bookend (R7); the fragment grammar written down in `data-model.md` and `contracts/` before any
code.

**Phase 1 - the registry** (T03-T08a). The module skeleton and the round-trip test on the registry; the
splitter; `make record`; the byte-identity proof; the sweep is the registry's own 920 entries. Ships
whole.

**Phase 2 - the questions** (T09-T14). `ways.html` first, then `cities/defenses.html` for the relative
links, then the sweep over the other seventeen. Byte-identity at each step.

**Phase 3 - the notes and the numbers** (T15-T20). The notes fragments, the keys, the allocation, the two
defects; `make citations` moves to its fragment; the diff is inspected and declared - numbers only.

**Phase 4 - collecting it** (T21-T25). The scripts' per-question modes; the four agent contracts; the
guard and its companion test; `research/CLAUDE.md`; the FR-026 re-run and its report.

**Phase 5 - landing** (T26-T29). `make done` green, the regression comparison against R6, the gate-cost
bookend against R7, the push.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A splitter kept in the tree after its one-time use | It is the assembler's inverse, and keeping it lets one test assert `assemble(split(page)) == page` over the real record on every run, forever | Deleting it after the migration leaves the assembler with only hand-written fixtures to prove itself against, which is exactly how a parser and its input drift apart. Its cost is the 100% floor, which it owes like anything else |

The first draft carried a second entry - two derivations writing parts of one citations page - which the
plan review of 2026-09-20 dissolved rather than justified. D1's two-pass assembly means there is one
assembly, calling the derivation the engine already has, on the page it already reads.
