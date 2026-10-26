# Research: Faster iteration

## R1 - Where the time went (measured 2026-10-26 UTC)

- **Method**: commit times on main for feature 417's tasks; the landing logs; `dev/cohort-log/` records.
- T48 ~1.5 h, T49 ~40 min, T50 ~1 h 50 min (commit times).
- T50's landing logs each end "the claims round did not finish in 20 min" (`CLAIMS_WAIT_S` = 1200 s, `scripts/land.py`): two
  waits, with no claims check in flight, the gate refusing for introduced findings both times.
- `dev/cohort-log/` holds 21 records of 54 seeds between T50's first probe and its landing; runs 30-60 s apart were served from
  the roll cache, the 2-5 minute ones rolled.

## R2 - Why docs-only edits re-rolled every seed

- **Decision**: key code on its docstring-free AST (D2, D3).
- **Rationale**: `gencache._split_sources` hashes each function as `"".join(lines[lineno - 1 : end_lineno])` (read
  2026-10-26), its docstring and comments included, and the module's top level as the raw lines outside function spans. A
  research claim is a docstring; so every claim relabel an impl-drift round asked for re-rolled every seed through that function.
  `gate-stamp.py`'s `content_id` (feature 189) already normalizes the AST this way for `make done`, which is why the GM's belief
  held for the gate and not for the rolls.
- **Alternatives considered**: tokenize and drop COMMENT/docstring tokens (fragile: a docstring is a STRING token, told apart
  only by position); move claims out of docstrings (out of scope, and the claims machinery reads them there).

## R3 - Which docstrings are content

- **Decision**: `l7r/diagram/interactive/**` stays byte-hashed in the roll/map and render keys; the record build's fingerprint
  stays raw; the claims machinery's fingerprints unchanged.
- **Rationale**: `interactive/classes/_base.py` returns `cls.__doc__` as modal text (read 2026-10-26); `gate-stamp`'s
  `RAW_AREAS` (`page`, `browser`) exist for the same reason (spec 189 FR-007 / D3). The record build reads the engine's claims
  (docstrings) to write the record's pages. Other `__doc__` readers found by grep are usage text (`regen.py` prints its module
  docstring, `building_programs.py` feeds argparse) - covered by keeping MODULE docstrings in `tooling_hash`.

## R4 - In-flight claims checks

- **Decision**: infer from the gate's own refusal (D1), not from a registry.
- **Rationale**: `wait_for_claims` already re-runs `claims-gate.sh` each poll and parses "carry:", "owed (", "introduced:"; no
  registry of dispatched claims agents exists (`hm_checks` tracks the record's page checks, not claims checks). An owed claim
  can be cured by a check the session runs; an introduced finding only by an edit or a ruling the next `make land` reads.

## R5 - The before/after count (to fill at the key change's landing)

- Before: a cohort run, a docstring-only edit to a function the rolls execute, the same cohort run: rolled N of 54.
- After: the same: rolled 0 of 54 (SC-001).
