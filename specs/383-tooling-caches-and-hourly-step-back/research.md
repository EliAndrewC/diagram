# Feature 383 - research

## R1 - what the record build check reads (plan D2)

Measured 2026-10-12 with an audit hook on `open` during one `record_asset --check` in this clone: it opened 29 files under
`l7r/diagram/`, every other file under `research/` (`archive/` 3,222, `sources/` 3,238, `questions/` 1,428, `assets/` 5, and
seven JSON files at the top), and 55 standard-library files. Nothing else in the repository. So the memo's inputs are
`research/`, `l7r/` and `pyproject.toml`, and the Python version stands for the standard library. Listing their content
ids (`git ls-files -s`, `git diff --name-only`, the untracked files under them) took 0.04 s (observed 2026-10-12; method: `time` over the three git listings).

## R2 - the baseline (SC-001)

`m:push-checks-before` in `measurements.json`: the push's checks that read the tree, 19.87 s in all at load 4.2, the record
build check 6.38, the research pointers 4.70, duplicate definitions 1.88, the function cap 1.46, conflict markers 1.25,
the old layout 1.16, the ledger 0.89, the rest under 0.35 each.

## R3 - the rest of the push's checks, and the record's rebuild (plan D2, D3)

Observed 2026-10-12 in this clone; method: each check of `push_checks.py`'s table run twice inside one interpreter
(`run_one`), the second run's wall time kept. Duplicate definitions 0.13 s, stale directories 0.01, file scale 0.16, the
function cap 0.19, the ledger 0.03, entry headings 0.00, research pointers 0.17, partial citations 0.23, the download list
0.04, spec-lint 0.07, the Affects check 0.18, conflict markers 0.32.

- Partial citations, kept per file (the registry write-ups and archive manifest rows read by `access_tags.load`, and the notes
  files): 0.33 s against 0.32 s without (observed 2026-10-12; method: `/usr/bin/time`, second of three runs). Listing the
  content ids of 5,400 small files costs what reading them does. Reverted.
- File scale, profiled (observed 2026-10-12; method: cProfile, one run): the directory census 0.08 s, the line counts 0.06 s.
- The Affects check read every feature twice; read once, 0.25 s to 0.15 s (observed 2026-10-12; method: `/usr/bin/time`).
- The record check (observed 2026-10-12; method: `/usr/bin/time` on `make record CHECK=1`): cold 5.63 s; after one question
  file changed, with each unchanged page's notes kept, 5.15 s; replayed 0.15 s. Unprofiled, the build's setup is 1.76 s and
  its render 3.38 s; the render reads the whole record's link index for every page.
