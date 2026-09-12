# Plan - 231 Review only when the layout moved

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: every guard branch has a suite case (FR-008); the two tools have unit tests and the
  browser path runs on the synthetic page.
- **X**: two new modules under `tools/` owe 100% coverage the day they land; the browser function is
  covered by the synthetic-page test, the pure functions by array tests. No file past 1,000 lines.
- **XVIII**: `scripts/review-owed.py` is a guard helper; its tests are `tests/tooling/test_review_owed.py`
  and the pair suite; `hooks-test` stays green.
- **XVI**: spec-fidelity before code.
- **Route**: `l7r/diagram/tools/*.py` is engine code -> GATED (LOCAL-GATED); `scripts/*` owe a green
  `make hooks-test`.

## Design

- `scripts/review-owed.py`: `--root <clone>` (default: the cwd's toplevel), `--why`; base =
  `git merge-base HEAD origin/main` (HEAD when there is no `origin/main`); changed = `git diff --name-only
  <base> -- '<both pool globs>'` plus untracked manifests; prints one map name per line.
- `scripts/pair-hooks.sh`: `find_root` asks `clone-sync-hooks.sh resolve` with the payload first;
  `review_owed()` calls the script; the Bash gate branch, the stop branch and `make verify` use it;
  the escaped Agent branch writes `review_key`. `GUARD_EDIT_OK` with the reason on every edit.
- `scripts/review-snapshot.py`: `<clone> <mirror> <map>...` copies the five files per map from both
  trees into `<clone>/.git/review-snapshot/<map>/{clone,main}/`, prints the directories and every
  missing file.
- the skill `Makefile` `verify`: calls `review-owed.py --why`; when maps are named, runs the
  snapshot and prints its directories in the DISPATCH NOW line; otherwise prints the waiver and starts
  the gate.
- `l7r/diagram/tools/page_lit.py`: `decode_idmap(html) -> (array, palette)`, `attribute(before, after,
  idmap, ctm) -> {class: (changed, total)}` (pure), `measure(html, key, vector=False)` (browser),
  `main`. `l7r/diagram/tools/picture_diff.py`: `diff_stats(a, b) -> ...`, `by_class(diff_mask, idmap,
  palette)`, `render(svg, width)` through `raster.resvg_png`, `main`.
- Makefile targets `page-lit`, `picture-diff`; `tools/CLAUDE.md` rows.
- `.claude/agents/settlement-review.md`, `dev/reviews.md`, `CLAUDE.md` pair row,
  `docs/efficiency-tooling.md`: the rule.
- Tests as FR-008; SC-001..SC-004 replayed by hand on the 228 delta and recorded in tasks.md.
