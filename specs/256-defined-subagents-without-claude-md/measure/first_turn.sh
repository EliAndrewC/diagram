#!/bin/bash
# first_turn.sh <agent file> <cwd> - feature 256, FR-006: a REAL defined agent's first-turn input, with the field and
# without it, dispatched from <cwd> (from `/diagram`, where the memory index loads - 255 R5). The agent is defined
# inline (`--agents`) from the file's own frontmatter and body - its pinned model and tools - so nothing is written
# under the mirror; a Haiku session only dispatches it, once, on a one-line prompt. Prints one line per leg.
AGENT=$1; CWD=$2; CL="$(command -v claude)"
for leg in without with; do
  AG=$(python3 - "$AGENT" "$leg" <<'PY'
import json, re, sys
text = open(sys.argv[1], encoding="utf-8").read(); _, front, body = text.split("---", 2)
fm = dict(re.findall(r"(?m)^(\w+):\s*(.+)$", front))
spec = {"description": "the agent under measurement", "prompt": body.strip(), "model": fm["model"], "tools": [t.strip() for t in fm["tools"].split(",")]}
if sys.argv[2] == "with": spec["omitClaudeMd"] = True
print(json.dumps({"measured": spec}))
PY
)
  SID=$(cd "$CWD" && timeout 600 "$CL" -p --model haiku --agents "$AG" --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json \
    "Use the Agent tool exactly once: subagent_type measured, prompt: 'No pair was handed to you in this run - reply with the single word OK.' Then reply DONE and stop." 2>/dev/null | jq -r '.session_id // empty')
  python3 - "$leg" "$SID" <<'PY'
import json, pathlib, sys
leg, sid = sys.argv[1], sys.argv[2]
subs = sorted((pathlib.Path.home() / ".claude" / "projects").glob(f"*/{sid}/subagents/agent-*.jsonl")) if sid else []
first = model = None
for line in (subs[0].read_text(errors="replace").splitlines() if subs else []):
    if line.startswith("{"):
        r = json.loads(line); m = r.get("message", {})
        if r.get("type") == "assistant" and m.get("usage"):
            u = m["usage"]; first = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0); model = m.get("model"); break
print(f"{leg} omitClaudeMd | first-turn input {first} | model {model}")
PY
done
