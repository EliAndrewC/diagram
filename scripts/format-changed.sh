#!/usr/bin/env bash
# `make test-file` formats the Python the clone changed before it tests it (feature 385 T68, plan D87).
#
# WHY. The GM, 2026-10-18: "make our tooling do the thing correctly automatically every time". Two format slips that evening
# (T65's landing, after 122 s of checks; T66's) were found by a lint after the session's own tests had passed. The files are those
# changed against the merge base with origin/main - committed, uncommitted or untracked, deleted ones left out - so a file nobody
# touched is never rewritten. The push's `ruff format --check` stays a check.
set -u
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
base=$(git -C "$root" merge-base HEAD origin/main 2>/dev/null || git -C "$root" rev-parse HEAD 2>/dev/null) || exit 0
mapfile -t files < <({ git -C "$root" diff --name-only --diff-filter=d "$base" -- '*.py'; git -C "$root" ls-files --others --exclude-standard -- '*.py'; } | sort -u)
[ "${#files[@]}" -gt 0 ] || exit 0
cd "$root" || exit 0
mapfile -t todo < <(python3 -m ruff format --check --force-exclude "${files[@]}" 2>/dev/null | sed -n 's/^Would reformat: //p')
[ "${#todo[@]}" -gt 0 ] || exit 0
python3 -m ruff format --force-exclude --quiet "${todo[@]}" && printf 'test-file: formatted %s\n' "${todo[*]}"
