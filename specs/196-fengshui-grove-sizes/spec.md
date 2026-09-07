# Feature 196 - the fengshui grove sizes: a research pass

**Request**: [`request.md`](request.md), the GM's words verbatim (2026-09-07). **Status**: IMPLEMENTED 2026-09-07 (tasks.md, findings.md); spec-fidelity round 1 CHANGES (three: no docstring ban - the modal follows the record; D1 not attributed beyond 'first', XII's ladder after the pass; papers reported to the GM during the pass), applied; round 2 CHANGES (one: the Summary still handed the follow-up to a GM ruling), applied; round 3 FAITHFUL.

## Summary

The record's figures for a village fengshui grove - a back grove of ~1-2 ha, a water-mouth cluster of ~0.1-0.5 ha, a
few dozen big old trees at the water mouth and 100-300 canopy trees in the belt - are labeled GUESS since 2026-09-07:
the one paper read for them (Chen et al., Forests 2020) gives whole-village forests of over 3, 6 and 20 ha and no
per-type area or tree count. The windbreak and copse classes are drawn at the guessed sizes. The GM chose the research
pass over leaving the guess or resizing on one paper: *"Yes, let's do the research pass first. If you find any other
papers you need me to download during the pass then let me know."*

This feature is the PASS, not the resize. It answers the research question, records the answer with quoted, readable
citations, tells the GM which papers it could not read so they can download them, and ends with a recommendation. It
changes NO map: what the engine draws follows constitution XII's ladder once the findings are in - a decisive measured
figure is implemented in a later feature, two supportable forms become a knob, and the GM is asked only where the record
turns out silent or contradictory.

## The question (research: physical)

How large were the village fengshui forests of southern China, by type - the back-mountain grove (后龙林 / 后山林) and
the water-mouth grove (水口林) - and how many trees stood in one? Measured areas and ranges, stem densities, canopy-tree
counts, from field surveys and forestry censuses, with the region and sample stated. Hong Kong's surveyed fung shui
woods and any mainland provincial census count; Korean village groves (maeulsup) and Japanese shrine groves are
analogues to be reported as such, never merged with the Chinese figures.

## User Scenarios & Testing

### User Story 1 - the reader learns what is known and what is not (P1)

A player opens the windbreak's explanation, follows "See references" to the fengshui-forest question, and reads what
surveys measured - a range with its region and sample - or, where nothing readable measures it, that the size drawn is
a guess. Never a number presented as a finding that no readable source gives.

**Acceptance**: the vegetation record's fengshui-forest section states each size figure with a quoted, readable
citation (feature 195's rule) or labels it GUESS; every footnote passes `quote-check`; the `Windbreak` and `Copse`
modal explanations and labels say the same thing the section says about the same figures.

### User Story 2 - the findings reach the GM, and the follow-up takes XII's ladder (P1)

The GM reads a short findings note: the measured ranges by type, how far the current drawn sizes sit from them, and
what constitution XII's ladder says next - a decisive measured figure is implemented (a later feature); two
supportable forms become a knob; where the record is silent the figure stays labeled GUESS; the GM is asked only where
the record is silent or contradictory. The note is also how the download list and the pass's result reach the GM.

**Acceptance**: `specs/196-fengshui-grove-sizes/findings.md` exists with those three parts; nothing the engine draws
changes in this feature (FR-005).

### User Story 3 - papers the container cannot read reach the GM (P2)

Where a survey sits behind a host that refuses this container, the pass lists it - title, URL, why it matters - for the
GM to download into `academic-sources/` (the 2026-09-07 convention in `research/CLAUDE.md`), and reads it from the
copy when it arrives.

### Edge Cases

- A survey gives areas for whole villages only (as Chen et al. do): recorded as such, never split by type by inference.
- Two surveys give different ranges for the same type: both recorded with region and sample; if the record permits
  two forms, the recommendation says "knob", not a choice (XII).
- A Chinese-language source: the original passage is quoted with a gloss (the record's form).
- A source only summarized in search results: not cited (feature 195); listed for download if it matters.

## Requirements

- **FR-001**: the research pass - Opus readers with `WebSearch`/`WebFetch`, one attempt per host, over Chinese- and
  English-language surveys of fengshui forest area by type and tree counts; Hong Kong's fung shui wood surveys;
  Korean and Japanese village-grove analogues reported separately. Every candidate paper returned with URL, whether
  its text was readable, and verbatim passages carrying figures.
- **FR-002**: the findings written into `research/vegetation.html`'s fengshui-forest section under feature 195's
  citation rule: quoted footnotes to public pages (or to the GM's copies, saying so), registry entries for each new
  source, the GUESS labels removed only where a readable source now gives the figure.
- **FR-003**: `quote-check` (Opus) over every new or changed footnote before the landing.
- **FR-004**: `specs/196-fengshui-grove-sizes/findings.md` - the measured ranges by type with region and sample, the
  distance from the drawn sizes (`settlements/vegetation.md`, the windbreak/copse classes), and what XII's ladder says
  next (implement / knob / stays a guess, GM asked only where the record is silent or contradictory). The papers asked
  of the GM during the pass, and which arrived, listed at the top.
- **FR-005**: no change to what the engine DRAWS - grove sizes, knobs, placement rules, geometry stay as they are; the
  resize, if any, is a later feature. The class EXPLANATIONS and LABELS for `Windbreak` and `Copse`
  (`interactive/classes/greenery.py` - docstrings and the `label` field) DO change in this feature, to carry exactly
  what the record carries when the pass ends: today the modal tells the reader "the typical back grove one to two
  hectares", labeled accurate and sourced to forests-2020, while the record's own footnote calls that figure a GUESS -
  the one failure XII names. An explanation is a docstring (feature 189, the tweak lane); a `label` change is a data
  field pinned by `tests/fixtures/classes_before_189.json` (the prose fields are only required present - `test_classes_docstrings.py`), so the snapshot moves with it and the gated route runs.
- **FR-006**: a paper the container cannot read is reported to the GM AS SOON AS the pass identifies it (the GM:
  *"If you find any other papers you need me to download during the pass then let me know"*), and the pass reads the
  copies that arrive in `academic-sources/` before it concludes; the list at the top of `findings.md` (FR-004) is the
  closing summary of what was asked for and what arrived.

## Success Criteria

- **SC-001**: every size figure in the fengshui-forest section is either cited to a readable, quoted source or labeled
  GUESS; `tests/interactive/test_footnotes.py` green; `quote-check` VERBATIM and SUPPORTS on every new footnote.
- **SC-002**: findings.md carries the three parts and the download list; the GM is told which papers to fetch.
- **SC-003**: no drawn size, knob, placement rule or geometry changes - `settlements/vegetation.md`'s sizes and the
  generator's grove parameters are byte-identical before and after; the `Windbreak` and `Copse` explanations and labels
  equal what the record says about the same figures.

## Decisions Recorded

- **D1 - pass before resize** (GM 2026-09-07, *"let's do the research pass first"*): one county's paper is thin ground
  for redrawing every map; the record is searched first. What follows the pass is constitution XII's ladder, not a
  ruling by default: decisive -> implement; two forms -> a knob; silent -> the figure stays a labeled guess and the GM
  is asked.
- **D3 - the modal follows the record now, not after the resize** (spec-fidelity round 1): a reader told a guess is an
  accurate finding is the XII failure, and it is live on the windbreak modal today; the explanation and label are
  brought level with the record in this feature whatever the pass finds.
- **D2 - analogues stay analogues**: Korean and Japanese village groves are recorded under their own heading if found,
  never averaged into the Chinese figures the class rests on.

## Assumptions

- **A1**: the pass runs on Opus readers (GM 2026-09-07, every subagent check on Opus).
- **A2**: the GM will download what the container cannot read when asked; a paper not yet downloaded is listed, not
  cited.
