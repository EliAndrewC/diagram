# Implementation plan - feature 195, cite only what can be read

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## Summary

Three deliverables from one GM sentence: the rule in the guidelines (constitution XII v2.19.0, root CLAUDE.md,
research/CLAUDE.md), the rule in the two checking agents (quote-check gains READABLE / NOT-READABLE; source-reader's
SUMMARY-ONLY means "not citable"), and the record brought under it - every footnote without a recorded verdict that
its passage was seen on the page it links to is fetched by a reader and then re-pointed to a readable page or turned
into an absence note. The form is held by static tests; the readability by the agent fetch.

## Technical Context

- Record: `.claude/skills/diagram/research/**/*.html`, hand-authored HTML (feature 194); footnotes `<li id="fn-n">`.
- Registry: `research/SOURCES.html`; classifier for link targets in `tests/interactive/test_sources.py` (test-side).
- No engine Python changes expected; `l7r/diagram/interactive/sources.py` reads rosters and citation lines, not
  footnotes. If it turns out to need a change the route is GATED and `make done` runs on the merged tree.
- Readers: Sonnet `general-purpose` agents with a written brief (scratchpad `cite195/brief.md`), one fetch per host
  per page, results as JSON; the session applies verdicts by script (`apply195.py`), never by recall.
- Census: `cite195/census2.py` - search space every footnote; SEEN = 194 quote-check VERBATIM/DIFFERS on a
  document-linked footnote, or the 2026-09-06 re-fetch SAME/RESTORED; A1 by key (`l7r.md` entries).

## Performance bookends

Not applicable - no generator change.

## Constitution Check

- V (the GM's writing): `request.md` verbatim; nothing in a SOURCE block touched.
- VI (verification): record tests + interactive tests; a second census run at zero; no history rewritten.
- X (100% coverage): no engine code added. Test files change only.
- XII (research record): this feature IS the XII amendment; every removed citation leaves an absence note so no
  guess reads as a finding; nothing decided from memory.
- XIII (no regressions): the footnote tests are made stricter and the record brought to them in the same landing.
- XIV (defects found): quote-check.md's stale Markdown "Input" paragraph is fixed in passing.
- XVI (spec review): round 1 CHANGES (three, applied); round 2 pending at the time of writing; implementation of
  the record waits for FAITHFUL; reader fetches (measurement) run meanwhile.

## Project Structure

- `specs/195-cite-only-what-can-be-read/{request,spec,plan,tasks}.md`
- `.specify/memory/constitution.md` (v2.19.0), `CLAUDE.md`, `.claude/skills/diagram/research/CLAUDE.md`
- `.claude/agents/quote-check.md`, `.claude/agents/source-reader.md`
- `.claude/skills/diagram/research/**/*.html`, `SOURCES.html`
- `.claude/skills/diagram/tests/interactive/test_footnotes.py`, `test_sources.py`

## Complexity Tracking

None - no new abstraction; one script per step, kept in the session scratchpad and described in tasks.md.
