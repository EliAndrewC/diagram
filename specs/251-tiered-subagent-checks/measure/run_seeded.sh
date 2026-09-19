#!/bin/bash
# run_seeded.sh <scratch dir> <case>... - each case is `name:agent`; a case directory was made by `seeded.py prepare`.
# One headless session per case, started IN the case's worktree so it loads that tree's agent file (the new tier),
# hooks off (they are wired to the mirror by absolute path and would judge a session that is not one). Three at a time.
SC=$1; shift
CL="$(command -v claude)"
run_one() {
  local name=${1%%:*} agent=${1##*:} d="$SC/${1%%:*}"
  ( cd "$d/tree" && timeout 1500 "$CL" -p --agent "$agent" --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json < "$d/prompt.txt" > "$d/run.json" 2> "$d/run.err"
    jq -r '.result // "NO RESULT"' "$d/run.json" > "$d/reply.md" 2>/dev/null
    echo "done $name rc=$? $(jq -c '{turns: .num_turns, in: (.usage.input_tokens + .usage.cache_creation_input_tokens + .usage.cache_read_input_tokens), out: .usage.output_tokens, models: (.modelUsage|keys)}' "$d/run.json" 2>/dev/null)" >> "$SC/progress.log" )
}
for c in "$@"; do
  run_one "$c" &
  while [ "$(jobs -rp | wc -l)" -ge 3 ]; do wait -n; done
done
wait
echo "ALL DONE $(date -u +%H:%M:%S)" >> "$SC/progress.log"
