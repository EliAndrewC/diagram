# Implementation Plan: The modern-only sweep

**Feature**: `280-modern-only-sweep` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

## Summary

Three phases. **Phase 1** (done in this session): seven audit agents read every record page, the kinds and knobs,
and the pool, legacy and magistracy maps; their findings are gathered, de-duplicated and grouped in
[`inventory.md`](inventory.md) (130 items, M01-M130, in 41 groups of two to four questions), and the research queue is
written. **Phase 2**: the queue in
[`queue.txt`](queue.txt) runs one fresh headless session per brief (`make page-session`), a WRITE session per group
then its CHECK sessions, on 269's pattern. **Phase 3**: the eliminations, from `outcomes.md`, in the engine, the kinds
and the maps.

## Decisions

- **D1 - The audit was read-only, over a copy of the record** (FR-001). The record was copied out of the repository
  from 269's clone, which is main plus 269's unlanded research (main held no research change 269 lacked, checked
  2026-09-28), so the audit saw the newest text; an agent reading under `/diagram` is handed every `CLAUDE.md` above
  the file (feature 250). Every section of every page was accounted for, candidate or clean; each output's clean count
  is in `inventory.md`'s header. Judgment was on Opus.
- **D2 - The research runs in page sessions from briefs** (FR-004). `briefs/gen.py` (`write <G>` from the inventory,
  `checks <G>` from the handoff, `all`) copies 269's generator. Its HEAD tells each session to read and write the
  coordination files with `make lines` / `make append`, to reserve prefixes with `make reserve`, not to edit sections
  other features hold, and to write each outcome as MODERN-ONLY (the search, dated; `undated-custom` where the only
  attestation is an undated modern record, spec D1), PREMODERN-ATTESTED (cited) or MIXED. A group assigns at most four
  questions (feature 274's cap, counted by `scripts/_brief_load.py`); each group's `Where:` line names its free prefix
  range, chosen above every range the record and the other features use on that page.
- **D3 - One serial queue in this clone, 269's sections last** (spec Edge Cases, FR-010). The groups whose sections 269
  has NOT touched run first. `then:wait269.sh` stands before the first group that edits a section 269 rewrote: it
  waits (10-minute checks, up to 10 hours) until the last commit in 269's clone that touched the record is on
  origin/main, then syncs. `then:sync.sh` between groups merges main in (a conflict is aborted and the queue goes on)
  and queues any `briefs/extra/*.md` once. A group that edits a section 279 holds (religion-and-death 124-129) runs
  only once 279 has marked it done in the claims file; the write brief's claims step skips it otherwise and names it
  in the handoff.
- **D4 - The eliminations wait for the research, and 269's modules wait for 269** (FR-005, FR-010). Phase 3 starts
  from `outcomes.md` (each handoff's `M<nn>` lines gathered), and no change touches a module in 269's
  `briefs/engine/groups.md` until 269 has landed. Per MODERN-ONLY form: the knob option is removed or the generator
  stops drawing it; the kind is retired (or, where the form is one of several a kind covers, its prose loses the form);
  the motivating pool map is regenerated; `settlement-review` or `building-review` runs on it (one map per agent) and
  the pass is a row in `docs/review-ledger.md`; `make done` is green before the landing. A MIXED item keeps the
  attested forms (a knob among two or more) and is calibrated to the premodern figure where it is a degree.
- **D5 - A reversed GM ruling is reported, not held** (FR-006). The handoff says per item whether the GM ruled the form
  in and whether knowingly. A form ruled in unknowingly is eliminated with the rest and listed for the GM; a form ruled
  in knowingly goes to the GM through `escalation-check` before it is removed.
- **D6 - The frozen legacy maps are not edited** (spec D2, FR-007). Each MODERN-ONLY form a legacy map draws is written
  against that map in `migration-plan.md`, owed at its conversion, and the list goes to the GM through
  `escalation-check`.
- **D7 - Findings owed to another feature's section** are written in the handoff and sent to the owner; they are not
  made here.
- **D8 - A stray fix found by the audit is made where it is found** (constitution XIV) when it is outside every held
  module and section; otherwise it is written in the inventory's "Found in passing" list with its owner.

## Constitution check

- XII: no candidate is eliminated before a research pass has searched for a premodern attestation, read what it found
  through `source-reader`, and recorded the outcome by the record's rules; every elimination is a recorded decision.
- XIII: phase 3 is measured against a detached-worktree baseline, and the gate runs before the landing.
- XIV: see D8.
- XVI: every candidate is researched; the one exception (a form ruled in knowingly) was put to `spec-fidelity` and held.
