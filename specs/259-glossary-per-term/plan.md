# Implementation Plan: The glossary is written one word per file

**Feature**: `259-glossary-per-term` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), the GM's request in [request.md](request.md), the measurements in
[research.md](research.md).

## Summary

Feature 258's shape, applied to the one file it left whole. A **splitter** takes `glossary.json` apart
into one file per term; an **assembler** puts them back into the same bytes; the pair is held by a
round-trip test over the real glossary. The differences from 258 are three, and each is why this is a
small feature rather than a repeat of that one:

- **The format is already per-term.** `glossary.json` is a JSON object, one entry per term, written by
  `json.dumps(..., ensure_ascii=False, indent=1) + "\n"` - verified, byte for byte. There is no HTML to
  cut and no comment to cut through, so the splitter is a loop, not a parser.
- **The question a check asks is MEMBERSHIP, not retrieval.** It does not know which term it wants; it
  wants to know whether a word is one. So the FILENAMES are the answer, and nothing needs opening.
- **Term order is load-bearing** and 258's was not: 7 variants are claimed by two terms, and the page's
  matcher lets the later one win (R2). The prefix is what keeps that from changing under a reader.

## Technical Context

**Language/Version**: Python 3.11, the repository's own. **Primary dependencies**: none new.

**Storage**: 720 term files under `l7r/diagram/interactive/assets/glossary/`, about 154 bytes each;
`glossary.json` stays where it is and becomes assembled.

**Testing**: pytest in the interactive tree, plus `make hooks-test` for the guard's companion.

**Performance goals**: the assembly is a few hundred kilobytes of JSON; the bar is that it does not show
up on the gate, judged the way 258's was (R4, written by T02 and closed by T12).

**Constraints**: byte-identity on `glossary.json` and `glossary.js`, which forbids re-ordering and any
re-formatting; the source is written with `indent=1`, which the assembly reproduces exactly.

**Scale/Scope**: 720 terms, 7 variant clashes to resolve, 1 filename to percent-encode.

**Single-artifact target**: the glossary itself is the one artifact - there is no per-map work here. The
reference case is the term `girder` (added by feature 258's own check run): one file, one round trip.

**Every step is two steps**: prove the round trip on one term, then on all 720 (T05, T06).

## Performance bookends

**N/A - no generator changes.** No map is drawn and no `.gen.py` runs; the render path keeps reading the
assembled `glossary.json`, which stays where it is. What this can slow is the gate, which R4 measures
before and after, exactly as feature 258's R7 did.

**One thing that is true of the code and not of the data** (the plan review, 2026-09-20): FR-011's
variant removals change what a rolled map page INLINES for `chaoguan` and `qiandao`, because both words
occur in class prose. Nothing is owed a regeneration - every pool page re-renders at each landing - but
this line should not be read as "no rolled page changes".

## Constitution Check

- **I, II, III, VII, VIII, IX**: N/A - no UI, no map style, no pool content, nothing generated about a
  place, no in-world prose, no setting detail asserted or moved.
- **IV. One Canonical Home for GM Source**: **PASS** - each term gets exactly one home, and
  `glossary.json` becomes a derivation rather than a second copy.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: **PASS** - no SOURCE block is touched;
  `request.md` is written once from the GM's messages.
- **VI. Verify Before Reporting Done**: **PASS** - every task names its verification: the byte-identity
  diff, `make done`, and FR-010's re-run of a real check against its recorded run.
- **X. Python Discipline (NON-NEGOTIABLE)**: **PASS** - ruff, ruff format, pyrefly, and the 100% floor
  on everything this lands, which feature 258 learned to write tests for as it went rather than at the
  gate. Red-green: the round-trip test is written first and fails for want of the module. File scale:
  the whole implementation is one module of a few hundred lines beside `glossary.py`.
- **XII. Historical Grounding (NON-NEGOTIABLE)**: **N/A, stated precisely.** No element is added,
  removed or redrawn and no assertion about the world changes. Two TOOLTIPS change, which is a
  presentation decision and is in the spec's Decisions Recorded with its measurement (R2): each of the
  two is currently showing another term's definition because of an order nobody chose.
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: **PASS with a measured baseline** - `make done` on
  unmodified code at `d7cbe8a8`, recorded as `m:baseline-done` (R4), taken before the first edit.

## Project Structure

```text
.claude/skills/diagram/
├── l7r/diagram/interactive/assets/glossary/      NEW - one file per term, 720 of them
│   ├── 0010-Akiba.json ... 7200-fire-water.json
├── l7r/diagram/interactive/assets/glossary.json  ASSEMBLED, byte-identical
├── l7r/diagram/interactive/glossary_source.py    NEW - split, assemble, check
├── l7r/diagram/tools/glossary_asset.py           CHANGED - assembles, derives, writes the index
├── research/assets/glossary-variants.json        NEW - the DERIVED variant index (FR-008)
├── research/CLAUDE.md                            CHANGED - where a term lives (FR-009)
├── tests/interactive/test_glossary_source.py     NEW
└── tests/interactive/test_record_format.py       the gate test that already holds glossary.js in sync

scripts/
├── _hm_record.py            CHANGED - the assembled-page guard learns this one file
├── test-record-edit-hooks.sh  CHANGED - its cases
└── sync-with-main.sh        CHANGED - `make glossary CHECK=1` beside `make record CHECK=1` (FR-006)

.claude/agents/record-format.md                   CHANGED - read the index, not the glossary (FR-008a)
docs/efficiency-tooling.md                        CHANGED - the shape and the measurement (T13)
```

## The design

### D1 - One file per term, named for the term, ordered by a prefix

`0010-<term>.json`, gapped by ten as `research/sources/` is, holding `term`, then the entry's own keys
in the order the assembled file carries them - `def`, then `variants`, in all 720. Emitting them the
other way round would leave SC-003's diff non-empty, which is the kind of thing byte-identity exists
to catch and prose does not. The
term is IN the file as well as in the name, and the assembly reads it from the content: a filename is a
convenience, and `dS/m` proves it cannot always be the whole truth (R3). A character a filename cannot
carry is percent-encoded; nothing else is transformed, so the eight terms with macrons keep them.

### D2 - `make glossary` assembles, then derives, and checks both

Today `make glossary` writes `research/assets/glossary.js` from `glossary.json`. It gains a step in
front: assemble `glossary.json` from the term files. `CHECK=1` reports either one stale. The order is
fixed and stated in the Makefile, not left to the caller.

### D3 - The guard is extended, not duplicated

`scripts/_hm_record.py` already re-aims an Edit aimed at an assembled record page to the fragment
holding its text. `glossary.json` is the same kind of file with a different directory, so it becomes a
case in the same function rather than a second guard: one behavior, one test suite, one message.

### D4 - The clashes are resolved by a rule, not one at a time

The term whose own NAME is the variant keeps it (R2). Five of the seven already resolve that way; two
change what a reader is shown, and both are corrections. A test holds the property afterwards, so the
order FR-003 preserves stops being load-bearing anywhere a reader can see.

### D5 - The contracts say what to read

`record-format` and any other check that judges VOCABULARY: list the directory, grep it for a variant,
and read a term file only for a definition you name. It goes in the contracts because a defined agent
launches without this repository's `CLAUDE.md` files (feature 256), and because that is where 258's
saving was actually collected.

## Phases

**Phase 0 - the baseline** (T01-T02). `make done` on unmodified code; the gate-cost bookend before.

**Phase 1 - the split** (T03-T07). The round-trip test red first; the module; the command; the split of
all 720; byte-identity proven on `glossary.json` and `glossary.js`.

**The committed `glossary.json` will NOT be byte-identical to today's when the feature lands**, and the
phase order is what makes that honest: T06's empty diff proves the machinery, and T08's declared variant
removals are then the only permitted delta on top of it. Each lands as its own commit.

**Phase 2 - what it is for** (T08-T10). The clash resolution and its test; the guard's new case; the
contracts and the operative doc.

**Phase 3 - landing** (T11-T14). FR-010's re-run; `make done`; the bookend after; the push.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| An ordering prefix on a filename the GM asked to be the word itself | Term order decides which definition a reader is shown for 7 variants (R2), and sorting would change two of them silently | Sorting and accepting the change was rejected because this feature must change nothing a reader sees except what it declares; a separate order manifest was rejected because it is a second thing to keep in step, which the record's own doctrine forbids |
