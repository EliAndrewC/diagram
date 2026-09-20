#!/bin/bash
# dispatch_seeded.sh <scratch dir> <case>... - each case is `name:agent`; a case directory was made by feature 251's
# `seeded.py prepare` (tree/, prompt.txt). Feature 256, FR-003: `omitClaudeMd` is IGNORED when an agent runs as a
# session's main agent, which is how 251's `run_seeded.sh` runs a check - so here a headless Sonnet session in the
# case's worktree only DISPATCHES the agent, once, with the recorded prompt, and the agent runs as a SUBAGENT, as in
# real use. Hooks off (they are wired to the mirror). The subagent's own transcript is the result: its reply, its
# turns and usage, its first-turn input, and whether the prompt it was handed is the recorded one, character for
# character (`result.json`). Three at a time.
SC=$1; shift
CL="$(command -v claude)"
run_one() {
  local name=${1%%:*} agent=${1##*:} d="$SC/${1%%:*}"
  ( cd "$d/tree" && timeout 2400 "$CL" -p --model sonnet --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json \
      "Read the file $d/prompt.txt. Then use the Agent tool EXACTLY ONCE: subagent_type \"$agent\", description \"seeded run\", and as its prompt the COMPLETE contents of that file, character for character - add nothing, remove nothing, summarize nothing. Do not run it in the background. When it returns, reply with the single word DONE. Do nothing else." \
      > "$d/run.json" 2> "$d/run.err"
    python3 - "$d" "$(jq -r '.session_id // empty' "$d/run.json")" <<'PY'
import json, pathlib, sys
d, sid = pathlib.Path(sys.argv[1]), sys.argv[2]
root = pathlib.Path.home() / ".claude" / "projects"
subs = sorted(root.glob(f"*/{sid}/subagents/agent-*.jsonl")) if sid else []
out = {"session": sid, "subagents": len(subs)}
if subs:
    recs = [json.loads(l) for l in subs[0].read_text(errors="replace").splitlines() if l.startswith("{")]
    def text(c): return c if isinstance(c, str) else "".join(b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text")
    seen, fresh, cached, output, first = {}, 0, 0, 0, None
    for r in recs:
        m = r.get("message", {})
        if r.get("type") == "assistant" and (u := m.get("usage")):
            k = m.get("id")
            row = (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0), u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0))
            if first is None: first = row[0] + row[1]
            seen[k] = tuple(max(a, b) for a, b in zip(seen.get(k, (0, 0, 0)), row))
    for f, c, o in seen.values(): fresh, cached, output = fresh + f, cached + c, output + o
    prompt = next((text(r["message"]["content"]) for r in recs if r.get("type") == "user"), "")
    reply = next((text(r["message"].get("content")) for r in reversed(recs) if r.get("type") == "assistant" and text(r["message"].get("content"))), "")
    (d / "reply.md").write_text(reply, encoding="utf-8")
    meta = subs[0].with_suffix("").with_suffix(".meta.json")
    out.update(agent=json.loads(meta.read_text()).get("agentType") if meta.is_file() else "", turns=len(seen), first_turn_input=first, fresh=fresh, cached=cached, output=output,
               weight=round((fresh * 6.25 + cached * 0.5 + output * 25) / 1e6, 2), prompt_verbatim=prompt.strip() == (d / "prompt.txt").read_text(encoding="utf-8").strip(),
               model=next((r["message"].get("model") for r in recs if r.get("type") == "assistant"), ""))
(d / "result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out))
PY
  ) >> "$SC/progress.log" 2>&1
  echo "done $name" >> "$SC/progress.log"
}
for c in "$@"; do
  run_one "$c" &
  while [ "$(jobs -rp | wc -l)" -ge 3 ]; do wait -n; done
done
wait
echo "ALL DONE $(date -u +%H:%M:%S)" >> "$SC/progress.log"
