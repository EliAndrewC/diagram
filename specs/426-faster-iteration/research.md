# Research: Faster iteration

## R1 - Where the time went (observed 2026-10-26)

- **Method**: commit times on main for feature 417's tasks; the landing logs; `dev/cohort-log/` records.
- T48 ~1.5 h, T49 ~40 min, T50 ~1 h 50 min (observed 2026-10-26, method: commit times on main).
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

## R3b - Why the tooling hash may drop function docstrings

- `tooling_hash` was made raw so a Makefile comment counts (its docstring). For `.py` under `scripts/` the readers of docstrings
  are module-level usage text only (grep of `__doc__`, `getdoc`, `get_docstring` under `scripts/` and `tests/tooling/`,
  2026-10-26: about twenty scripts read their own MODULE `__doc__` for argparse or a usage message - `gate-stamp.py`,
  `plan_gate.py`, `review_prereq.py` among them; the one `get_docstring` of a class, `record/modal_owed.py`, reads the engine
  registry's classes, not a script's), so function and class docstrings can drop and module docstrings stay.

## R4 - In-flight claims checks

- **Decision**: a marker per claims bundle, written when the bundle is built and removed when its reply is recorded (D1); the
  landing waits only while a live marker exists.
- **Rationale**: no registry of dispatched claims agents exists (`hm_checks` tracks the record's page checks). Inferring "in
  flight" from "owed" would wait the full claims wait for a check nobody dispatched (spec-fidelity, 2026-10-26). An introduced finding is never
  cured by waiting; the landing stops on it at once whatever else is owed.

## R5 - The before/after count (to fill at the key change's landing)

- Before: a cohort run, a docstring-only edit to a function the rolls execute, the same cohort run: rolled N of 54.
- After: the same: rolled 0 of 54 (SC-001).
