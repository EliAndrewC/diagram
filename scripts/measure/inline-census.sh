#!/usr/bin/env bash
# inline-census.sh - phase 1's share of feature 449's second census, every remaining site named (the round arbiter's ruling `ask:449-T052-inline-census`).
#
# The census is every `python3 -c`, `python3 -` and heredoc under scripts/hooks/ and tests/hooks/. A site follows the piece or caller it belongs to, not its path (FR-001). The three
# groups it may fall under, and nothing else:
#   input         a `python3` inside a string a case feeds a guard as its input: nothing runs it. By exact line, listed in tests/hooks/census-guard-inputs.txt, so a real run in the same
#                 suite still counts. Those suites stay shell past phase 1.
#   later-phase   a file that moves whole with a piece FR-001 places later.
#   last-caller   a file that goes with its only caller (`clone-resolve.sh`, called by `guardlog.sh`).
# Anything else is printed and exits 1: phase 1's share is not empty.
set -uo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root" || exit 2
pattern='python3 (-c|-[[:space:]]|-$|<<)'
later='^(tests/hooks/test-(checks-hooks|record-edit-hooks|check-bundle-hooks|entry-gate|claims-gate|cohort-gate|land-tooling)\.sh|scripts/hooks/(check-bundle-hooks|record-edit-hooks|lib/guardlog)\.sh):'
caller='^scripts/hooks/lib/clone-resolve\.sh:'
listed=tests/hooks/census-guard-inputs.txt
sites=$(git grep -nE "$pattern" -- 'scripts/hooks/*.sh' 'tests/hooks/*.sh')
inputs=0 later_n=0 caller_n=0 outside=""
while IFS= read -r site; do
  [ -n "$site" ] || continue
  text=${site#*:*:}
  if printf '%s\n' "$site" | grep -qE "$later"; then later_n=$((later_n + 1))
  elif printf '%s\n' "$site" | grep -qE "$caller"; then caller_n=$((caller_n + 1))
  elif grep -qxF -- "$text" "$listed"; then inputs=$((inputs + 1))
  else outside+="$site"$'\n'
  fi
done <<< "$sites"
total=$(printf '%s\n' "$sites" | grep -c .)
printf 'inline census under scripts/hooks/ and tests/hooks/: %s sites\n  a guard'"'"'s input (not a run): %s\n  moves whole with a later piece: %s\n  goes with its only caller: %s\n  outside the three groups: %s\n' "$total" "$inputs" "$later_n" "$caller_n" "$(printf '%s' "$outside" | grep -c .)"
if [ -n "$outside" ]; then printf '%s' "$outside" | cut -c1-160; exit 1; fi
