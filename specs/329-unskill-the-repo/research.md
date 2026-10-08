# Research: Unskill the repository (feature 329)

Measurements taken in `/diagram/.clones/diagram-unskillify` at `5e2ba4824` (main + this spec), 2026-10-07, by `git grep`
over tracked files unless stated.

## R1 - What collides at the root

Root: `CLAUDE.md`, `Makefile` (a 39-line forwarder), `.gitignore`, `ruff.toml` (the lint fence, `exclude = ["*"]`).
Skill dir: `CLAUDE.md` (an 18-line index), `Makefile` (2,098 lines, every target), `.gitignore` (10 rules),
`pyproject.toml` (ruff, pyrefly, pytest, coverage). ruff prefers `ruff.toml` over `pyproject.toml` in one directory,
hence D3. Nothing else shares a name.

## R2 - Where the old path is named

- Live files outside `specs/`: 176 files, 7,483 occurrences; 6,115 of them in `dev/claims-index.json` (unit keys), 500
  in `scripts/fixtures/*.json` (recorded commands), about 400 in `dev/perf-log/` records.
- Under `specs/`: 12,441 occurrences in 1,105 files (left as written).
- Forms: 6,460 are `.claude/skills/diagram/l7r...`; the bare forms (`cd .claude/skills/diagram &&`, `-C`, a path
  constant, a closing quote) are about 400, listed by the sweep for hand edits.
- Depth arithmetic: 143 sites under the skill dir (`parents[k]` with k >= 3, `.parents[2]` off a skill-root constant,
  `../../../` - 30 of those in the Makefile). Rule for `Path(__file__).resolve().parents[k]` in a file d directories
  below the skill root: `parents[d]` is the skill root and stays the project root; `k > d` climbed into the repository
  and becomes `k - 3`.
- 72 files in `scripts/` name it (20 hold a `SKILL = ".claude/skills/diagram"` constant or its `Path` form).
- `.claude/settings.json` and `container-scripts/append-system-prompt.md`: none (hooks are `/diagram/scripts/...`).
- Outside the repository: gm-assistant `docs/iteration-loop.md` (one file); the user memory, 5 files.

## R3 - The config root is equal

`ruff check --show-files .` from the skill directory before the move and from the root after it (with the fence carried
into `extend-exclude`), prefixes stripped: 831 files each, IDENTICAL (`diff` empty), 2026-10-07. `ruff format` reads the
same discovery and the same excludes. pyrefly's `project-includes` are explicit `l7r/diagram/...` paths relative to the
config's directory and `search-path = ["."]`, so moving the config with the tree changes nothing it checks.

## R4 - Guards and push checks naming the path

`canon-read-hooks.sh`, `check-bundle-hooks.sh`, `claims-gate.sh`, `clone-sync-hooks.sh`, `download-copy-hooks.sh`,
`entry-gate.sh`, `finished-run-hooks.sh`, `guard-file-hooks.sh`, `idle-tests-hooks.sh`, `make-only-hooks.sh`,
`new-file-hooks.sh`, `pair-hooks.sh`, `review-gate.sh`, `sync-with-main.sh`, and 19 of their `test-*.sh` companions.

## R5 - Merges across the move

Measured 2026-10-07 in a scratch pair of repositories (git 2.53, ort): main renames `.claude/skills/diagram/dev` to
`dev`; a clone holds a commit editing `dev/x.md` at its old path and adding `dev/new.md` under the old directory.
- Default config: `CONFLICT (file location): ... added in HEAD inside a directory that was renamed ..., suggesting it
  should perhaps be moved to dev/new.md`; the merge stops (the edit itself was applied to `dev/x.md`).
- `-c merge.directoryRenames=true`: `Path updated: ... moving it to dev/new.md`; clean, exit 0, the edit on
  `dev/x.md`, nothing left under `.claude/`.
- Which `sync-with-main.sh` runs: the prompt hook (`clone-sync-hooks.sh`, read from the mirror) runs the CLONE's own
  copy, which in a clone not yet synced is the pre-move script without the flag. So the flag is set where every git in
  the container reads it - the global git config, written by `container-scripts/setup-dev-env.sh` (and applied once by
  hand in the running container) - as well as passed by the new `sync_in`; and the hook, which is always the mirror's
  newest, runs the carry after a successful sync-in.
Fixture cases whose verdict changed: to fill at T05.

## R6 - The gate before and after

Baseline `make done` in this clone at `5e2ba4824` + the spec, before the move: GREEN in 459 s (observed 2026-10-07, method: the gate's own wall-clock line in its log). Phases
static, format, typecheck, hooks-test (38 guard suites green), test-full: 10,818 passed, 3 skipped, 2 xfailed in
228.6 s. ruff's checked files from the skill dir: 831 (361 under `l7r/`, 460 under `tests/`, 9 under `wip/`, and
`pyproject.toml`). After the move, in this clone (whose ignored artifacts the carry moved - 430 files - before its first post-move gate):
the final `make done` GREEN in 217 s (observed 2026-10-08, method: the gate's run record, `seconds`), FULL mode, 10,824
passed, 3 skipped, 2 xfailed - six more tests than the baseline (the new lint-scope, moves, doc-links and docs-match
tests); the reference roll a HIT served from the carried roll cache. A second clone's first gate is the carry's own
case in `test-sync-with-main.sh` (case 15: the ignored cache lands at the root, no old directory left).

## R7 - Defects found on the way, and what was done

- **The gate-stamp `page` area hashed nothing** (pre-existing): it was written root-relative (`l7r/diagram/interactive`)
  while the files lived under the old skill directory, so `git ls-files` matched nothing and an asset-only delta owed
  no page check. The move makes the path real; the area now hashes the interactive assets and the class registry.
- **`test-entry-gate.sh` edited a LIVE research page** under every hooks-test (pre-existing): a `git commit -a` made
  during the baseline gate swept its probe text ("a short walk apart.") into this feature's commit 79f97ae59, undone
  in the next commit. The suite now edits a throwaway local clone of HEAD (13/13, 83 s, the old version 83 s - observed 2026-10-07, method: `time bash scripts/test-entry-gate.sh`, each once).
- **29 broken Markdown links** in live documents (pre-existing): pool notes pointing at `../../hamletgen/` from before
  feature 119, sibling notes linked as if in one folder, retired tools. Fixed, and `tests/tooling/test_doc_links.py`
  now holds every live link.
- **The sweep's own defects**, each caught by a test and fixed: an escaped prefix (`\.claude/skills/diagram/`) in three
  regexes lost the path but kept the backslash (`\research` is a carriage return); depth arithmetic written as strings
  (`"..", "..", "..", "..", ".."`, `dirname(dirname(dirname(SKILL)))`, `parents[3]` off a constant) that no pattern
  modeled; the engine walks (`gencache.engine_files`, `render_cache.engine_fingerprint`) which, walking the root,
  would have keyed every cached roll on `scripts/` and `specs/`; apostrophes inside a single-quoted hook program.
- **`git mv` carries untracked `__pycache__` with the directory**, and a pytest-rewritten `.pyc` keeps the old
  `co_filename` while its source's mtime still validates it (`inspect.getsource` then fails). Only the clone that ran
  the `git mv` has it - a merge elsewhere writes fresh files - so it was cleared here, not tooled.
- **A delta check that lists changed files by `git diff --name-only <base> -- <tree>` reads every moved file as new**:
  the question-size cap flagged three pages (0009, 0059, 0227) already over it on main, untouched by this feature.
  `scripts/_moves.py` (content-based: a blob the base already held) now keeps a pure move out of the question-size,
  house-style, review-occasion and modal checks. The record checks owed at the push compare whole record trees
  against the base and are answered for this one push by a recorded escape (R8).

## R8 - The push's record and claims gates, measured past the move

Both gates key their answers by PATH against the merge base, where every path still carries the old prefix, so on this
feature's own push everything reads as new. Measured instead from the pure-rename commit (T02) to HEAD:

- **Record checks** (`_record_owed.py --between <T02> HEAD`): ONE unit owed - `source-applicability:shichiya-jawiki`,
  for a phrase naming a deleted document; answered (APPLICABLE-WITH-LIMITS, limits HONEST, no edit). Against the base the
  gate counts 23,006, every one a moved page. The push passes `RECORD_CHECKS_OK` naming this measurement; it is
  recorded in `dev/bypass-log/`. After the landing every base is post-move and the gate is exact again.
- **Claims** (index rows mapped old key -> new key and compared with the base's verdicts): 523 findings, 497 unchanged
  from the base; 6 on keys new to this feature (the new Sheet conventions claim mislabeled, five decisions unclaimed);
  20 whose verdict differs from the base's on text this feature changed only in its links and wording (a second judge
  disagreeing with the first - the same claims, the same sheets). The new keys were fixed (the south-gate rule split
  into its own UNRESEARCHED claim; four UNRESEARCHED claims added) and re-checked, and the scale-bar claim - wrong before
  this feature (the sheets draw it top-left) - was corrected. The 20 re-judged and the 497 standing findings are the
  sheets against the record, feature 328's work, not this one's; the push passes `CLAIMS_OK` naming these counts.
