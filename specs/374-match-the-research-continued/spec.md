# Feature 374: Match the research - continued

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Filed - the open work of feature 372 (itself 328's remainder), moved here at the GM's word for a fresh session

**Owed at**: now

**Input**: `request.md` (the GM, 2026-10-10); feature 328's request and feature 372's carry over unchanged.

## What it is

Feature 372 took 328's ranked findings easiest first, waves 98-111, and closes with every one of its tasks ticked. What is
still open moves here, to be taken up in a fresh session exactly as 372 took 328's: a spec, a plan of waves in ranking order,
a task per wave, the same gates and reviews, batched closes.

## What it carries

- **The open rows of 328's ranking** (`specs/328-match-the-research/ranking.json`, rebuilt by `audit/merge.py`): 198 rows in
  scope at 372's close - 153 E3, 43 E4 (a research pass under the record's own checks before any code change), 2 E2 - in
  ranking order. The found rows 372's waves filed (`audit/found-wave105.jsonl` to `found-wave108.jsonl`) are among them.
  Every easy row (E0, E1) is done; what is left is redraw and research work.
- **Three rows held for the GM**, flagged `Held` in the ranking (`audit/overrides.json`): the door band (0117 records the hand
  sheets' 8-8.7 ft doors as a convention, against the GM's true-size rule); `fixture_quota`; and `one tub per wooden building`
  (waiting on `#senior retainers housed apart`).
- **Every decision still owed to the GM**: 372's spec, "What it carries" (328's held section, the Mode A wells as markers,
  wave 97's charcoal store) - put to the GM at this feature's start or end, through `escalation-check`.
- **Carried from 372's spec unchanged**: the claims-gate findings counted as introduced at 328's landing; Sawada's zigzag
  (waived for landing, an open E3 row); the 40-household seed 25 knot; Ochiba's garrison privy haul (a research item on 0101
  and 0090).
- **Tooling gaps**:
  - a glyph-check verdict is keyed by element alone, so a second sheet's check overwrites the first's (372's spec);
  - `make modal-bundle FOR=modal-depiction`'s crop on a Mode A sheet paints the page's highlight, not the drawn fill (372);
  - `pack_audit`'s `passage_blockers` misses a tub 0.2 px outside a gate passage's rect (wave 106, Ubame's gate-range tub);
  - the claims-triage reply parser counts the word "TOUCHES" anywhere in a reply as a touched claim (wave 108);
  - a `yosui-oke` glossary entry would keep the `yosui` tooltip off that word in 0100's notes (record-format, wave 106).
- **Nitpicks left at 372's reviews**: Ochiba's bath steam arcs drawn for the old 13 x 11 room (wave 108); Ubame's reception
  tubs mirrored about the shoe stone (wave 106).

## How it starts

**Feature 375 first** (`specs/375-enforced-wave-process/spec.md`): the wave process this feature runs on is enforced by the
tooling there - content-scoped record checks, line-scoped claims, decide-then-freeze, a preflight inside the gate. Take no wave
here until 375 has landed.

`make claim` is done (this directory). Next: `/speckit-specify` over this file and `request.md`, then plan and tasks in
waves, as 372 did (`specs/372-match-the-research-remaining/` is the worked example). Re-arm the usage cap with the GM's
current figure before the first wave.
