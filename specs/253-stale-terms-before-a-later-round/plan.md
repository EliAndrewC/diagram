# Plan - 253 the old value is looked for before a later review round is spent on it

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **XVI**: spec reviewed before the guard branch lands; this plan reviewed (MODE 4) before any tick.
- **XVIII**: the guard's new branch ships with new cases in `scripts/test-review-round-hooks.sh`; guard-file
  edits carry `GUARD_EDIT_OK` with a reason.
- **Route**: `scripts/`, the skill Makefile, `tests/tooling/`, docs -> DIRECT.

## Design

- **P1 the search** (`scripts/_stale_terms.py`, stdlib): `changed_pairs` (difflib over lines, `replace` opcodes
  zipped), `subjects` (backticked spans the old and new line share), old values (case-folded words of three
  letters or more and numbers the old line had and the new one lacks, minus a short list of common words and
  minus the subject's own words), `watched_lines` (the operative files, outside the Review history, not a
  `verify:` note), `stale_candidates` over two `{relative path: text}` maps so the test needs no repository,
  `read_dir` for the guard's snapshot and `read_ref` for a git ref. Exit 1 with candidates, 0 with none, 2 when
  there is nothing to compare with.
- **P2 the guard branch** (`scripts/_hm_review_round.py`): on the rewrite branch, BEFORE the diff, the snapshot
  refresh and the round count - `STALE_TERMS_OK` present: its reason is checked (a bare token is the standard
  refusal) and the rewrite proceeds, recorded as `rewrote`/`mode-3-preamble-stale-ok` with the reason in the
  detail; absent: the search runs and any candidate returns `blocked`/`stale-terms`, exit 2, with the rendered
  list and the two ways on. No candidate: nothing changes.
- **P3 the target**: `make stale-terms F=<feature> [AGAINST=<ref>]`; candidates are not a make failure.
- **P4 the proof and the record**: `tests/tooling/test_stale_terms.py` (plain inputs, then feature 251's two
  commits, skipped on a shallow checkout); suite section 10; `research.md` R2's honest count; the root
  `CLAUDE.md` guard row, `docs/guards.md`, `docs/spec-kit-and-reviews.md`, `docs/make-targets.html`.

## Order

T01 the search and its tests -> T02 the guard branch and suite cases -> T03 the target and the record ->
T04 `make hooks-test`, `make quick`, land.
