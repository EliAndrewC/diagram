#!/bin/bash
# probe.sh <label> <cwd> <tools-json|ALL> [extra claude flags...] - feature 255, FR-007: what a SUBAGENT's first turn costs.
# A headless Haiku session started in <cwd> dispatches one trivial inline agent (`--agents`), hooks off; the subagent's
# transcript is then read for the input of its FIRST assistant message (fresh + cache-creation + cache-read), which is
# its fixed context: the system prompt, the tool definitions, its own prompt, and whatever the harness loads for it
# (CLAUDE.md, the memory index). One thing is varied per probe; every probe prints one line:
#   <label> | subagent first-turn input | main first-turn input
LABEL=$1; CWD=$2; TOOLS=$3; shift 3
CL="$(command -v claude)"
if [ "$TOOLS" = ALL ]; then AG='{"probe":{"description":"a probe","prompt":"Reply with the single word OK and nothing else.","model":"haiku"}}'
else AG="{\"probe\":{\"description\":\"a probe\",\"prompt\":\"Reply with the single word OK and nothing else.\",\"model\":\"haiku\",\"tools\":$TOOLS${PROBE_EXTRA:+,$PROBE_EXTRA}}}"; fi   # PROBE_EXTRA: one more frontmatter field as a JSON fragment, e.g. '"omitClaudeMd":true'
OUT=$(cd "$CWD" && timeout 300 "$CL" -p --model haiku --agents "$AG" --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json "$@" \
  "Use the Agent tool exactly once: subagent_type probe, prompt: go. Then reply with its answer and stop." 2>/dev/null)
SID=$(printf '%s' "$OUT" | jq -r '.session_id // empty')
[ -z "$SID" ] && { echo "$LABEL | NO SESSION | -"; exit 1; }
python3 - "$LABEL" "$SID" <<'PY'
import json, pathlib, sys
label, sid = sys.argv[1], sys.argv[2]
def first_input(path):
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("{"): continue
        r = json.loads(line)
        if r.get("type") == "assistant" and (u := r.get("message", {}).get("usage")):
            return u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    return None
root = pathlib.Path.home() / ".claude" / "projects"
main = next(root.glob(f"*/{sid}.jsonl"), None)
subs = sorted(root.glob(f"*/{sid}/subagents/agent-*.jsonl"))
print(f"{label} | {first_input(subs[0]) if subs else 'NO SUBAGENT'} | {first_input(main) if main else '-'}")
PY
