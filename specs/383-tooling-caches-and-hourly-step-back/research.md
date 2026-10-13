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
