# Feature 255 - cheaper checks by tooling: fewer turns, less read per turn, a smaller fixed context

**Status:** draft 2026-09-19 - round 1 CHANGES REQUIRED applied (see Review history).

## Summary

The GM asked (`request.md`) for one feature holding every finding of the token audit that the session believes
is worth investigating or pursuing. There are six. Each is a TOOLING change to how a check is fed or how it
works - none changes a model - and each is adopted only if it passes the test feature 251 established: the
changed check is re-run on RECORDED runs with known findings, and it stands only when it hits every finding
the recorded run caught and costs less. A candidate that fails is recorded with its measurement and dropped,
which is a legitimate outcome of an investigation. No engine code: the delta routes DIRECT.

## Functional requirements

**FR-001 - the acceptance test is feature 251's, and it is kept small.** Every candidate below is judged by
seeded runs made with `specs/251-tiered-subagent-checks/measure/seeded.py` (a recorded run's prompt, a worktree
at the commit it saw, a headless session on the changed agent file), each run's findings scored against the
recorded reply and its weight against the same recorded run's. A candidate is ADOPTED when it misses nothing
the recorded run caught on any of its cases and its total weight over those cases is lower; otherwise it is
NOT ADOPTED and the agent is left as it was. The GM's instruction of 2026-09-19 stands (*"redoing old work is
only useful insofar as it does give us sensible measurements"*): cases are slices, the run count and rough
cost of each batch are stated before it is launched, and `research.md` records every run.

**FR-002 - `source-applicability` is handed its entries.** A script (`make source-entries KEYS=<k1,k2,...>`)
prints, for each registry key, its `SOURCES.html` entry (the citation line, both write-ups, the `Used for:`
line) and the footnotes that cite it with their assertions; the agent's contract says to start from that and
to open the registry only for a key the listing lacks. Two seeded cases.

**FR-003 - a scoped `record-format` or `quote-check` is handed the text in scope.** `make record-prepass
PAGE=... SECTION=...` also emits the section's visible text and its HTML source lines (the agent reports
markup defects), and `make quote-verbatim PAGE=... NOTES=...` already carries each note's passage and
assertion; each contract says that for a SCOPED check the handed text is the reading list and the page is
opened only to settle a doubt. Two seeded cases each, the recorded cases of feature 251's R5 and R7.

**FR-004 - independent tool calls go out together.** The contracts this feature already opens -
`spec-fidelity.md` and `spec-fidelity-verify.md`, and `source-applicability.md`, `record-format.md`,
`quote-check.md`, `settlement-review.md` and `source-reader.md` - gain one instruction, in the same words: send the reads, greps and fetches you already know you need in ONE message,
and do not spend a turn on a single lookup whose result does not decide the next one. Tested where turns are
most of the cost and the recorded cases are cheapest - two later `spec-fidelity` rounds on the twin - and
adopted for the seven contracts named if it holds there; `research.md` reports turns before and after.
`perf-audit.md`, `building-review.md` and `size-audit.md` are NOT edited under this feature: the report ruled
them out (*"Ruled out in that report, and not part of this feature"*, `request.md`), and with no recorded runs
they cannot pass FR-001's test. Whether the line belongs in them too is a separate question for the GM.

**FR-005 - `settlement-review` measures in one call and carries a shorter contract.** A script (`make
review-facts MAP=<pool map>`) returns in one call the standard measurements the contract's own "Tooling"
section names, and the contract's `Validated examples` section moves to a file the agent is told to open only
when a finding of that kind is in doubt. This is the most expensive check per run, so its test is the most
expensive here - two seeded runs at about five weight units each - and it is run LAST, after the cheaper
candidates have shown whether the turns-and-context reading of R9 holds in practice. It is adopted only if
every recorded finding is hit; its ledger row in `docs/review-ledger.md` says the contract changed.

**FR-006 - `source-reader` greps saved pages.** A script (`make source-pages OUT=<dir> URL=...`) saves the full
visible text of the named pointers (no model; `_quote_verbatim.Pages`); the agent's contract says to `Grep`
the saved pages for the claim's terms and `Read` only around the hits, and to fetch only what the script could
not reach or a lead the pages point to. Judged on R5's three cases on BOTH axes, because feature 251's R8
found whole-page reading more accurate and far more expensive: adopted if it misses nothing AND costs no more
than the recorded runs; if it misses nothing but costs more, the measurement goes to the GM as a quality-for-
cost decision and the agent is left as it was.

**FR-007 - what fills the fixed context is established, and what is safely removable is removed.** Probe runs
on the cheapest model (a trivial agent dispatched inside this repository with and without each suspect -
the project `CLAUDE.md`, the session memory index, the appended system prompt, the tool list) measure what
each adds to a subagent's first-turn input. `research.md` records the breakdown. Exactly two things may be TRIMMED: the session memory index's line
lengths (every entry kept, lines shortened) and an agent file's tool list (a tool the check never calls).
Everything else the probes measure - the project `CLAUDE.md` and `research/CLAUDE.md`, the appended system
prompt, the harness's system prompt and tool definitions - is REPORTED with its size and left unchanged; if a
document a check does not need turns out to be large, that finding goes to the GM with the number.

**FR-008 - the record.** `tests/test_agent_models.py` is untouched (no tier moves). Each adopted change is
stated where the check is described - root `CLAUDE.md`'s research bullet, `research/CLAUDE.md`,
`docs/efficiency-tooling.md`, `docs/make-targets.html` - and each NOT ADOPTED candidate is recorded in
`research.md` with its runs, so it is not tried again blind. Every new script has a test module under
`tests/tooling/`.

## Success criteria

- **SC-001** (FR-001) `research.md` holds one row per seeded run: the case, the recorded findings, hits and
  misses, turns and weight against the same recorded run.
- **SC-002** (FR-002, FR-003, FR-004, FR-005, FR-006) Each of the five candidates ends ADOPTED or NOT ADOPTED
  by FR-001's rule (FR-006 by its two-axis form), and an agent file changed only where its candidate was
  adopted.
- **SC-003** (FR-007) The fixed context's breakdown is recorded with each probe's measured first-turn input,
  and each trim names what it removed and the tokens it saved on a re-probe.
- **SC-004** (FR-008) `make hooks-test` and `make quick` are green; nothing under `l7r/` or `pool/` changed.

## Assumptions

- The recorded runs of 2026-09 remain on disk under `~/.claude/projects/` as the oracle; a case whose
  transcript is gone is replaced by another recorded run of the same agent, and `research.md` says so.
- A headless session started in a worktree loads that worktree's agent file (feature 251, R4).
- The batches are run in the order FR-002, FR-003, FR-004, FR-006, FR-007, FR-005 - cheapest first - and the
  GM may stop the feature after any batch; what has been adopted by then stands on its own.

## Review history

- **Round 1 (2026-09-19) - CHANGES REQUIRED, two items, both applied.** Coverage complete; conditional adoption and
  the cheapest-first order ruled within the request. (1) FR-004 reached every agent contract, including the three
  the report ruled out and FR-001 cannot test: restricted to the seven contracts this feature opens. (2) FR-007's
  trim class was open-ended and would have licensed cutting the project `CLAUDE.md`: closed to two named things,
  everything else reported with its size.
