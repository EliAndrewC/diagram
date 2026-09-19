#!/usr/bin/env python3
"""Where a subagent check's tokens go, from its transcripts: the fixed context every turn re-reads, the turns,
and what each tool call brought in (by tool, and by file for Read). No model is run. Usage: profile.py <agent>..."""
from __future__ import annotations
import collections, importlib.util, json, pathlib, statistics, sys
HERE = pathlib.Path(__file__).resolve(); CLONE = HERE.parents[3]
spec = importlib.util.spec_from_file_location("ac", CLONE / "scripts" / "_agent_census.py"); ac = importlib.util.module_from_spec(spec); spec.loader.exec_module(ac)

def profile(agent: str) -> None:
    base, turns, first_prompt = [], [], []
    tool_n, tool_chars, file_chars, file_n = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    runs = 0
    for t in ac.transcripts(pathlib.Path.home() / ".claude/projects"):
        meta, u = ac.read_run(t)
        if meta.get("agentType") != agent or not u["turns"]:
            continue
        runs += 1; turns.append(u["turns"])
        recs = [json.loads(l) for l in t.read_text(errors="replace").splitlines() if l.strip().startswith("{")]
        seen_first = False; calls = {}
        for r in recs:
            msg = r.get("message") or {}; content = msg.get("content")
            if r.get("type") == "assistant" and not seen_first and msg.get("usage"):
                us = msg["usage"]; base.append(us.get("input_tokens", 0) + us.get("cache_creation_input_tokens", 0) + us.get("cache_read_input_tokens", 0)); seen_first = True
            if r.get("type") == "user" and isinstance(content, str) and not first_prompt[runs - 1:]:
                first_prompt.append(len(content))
            for b in content if isinstance(content, list) else []:
                if b.get("type") == "tool_use":
                    calls[b["id"]] = (b["name"], str((b.get("input") or {}).get("file_path") or (b.get("input") or {}).get("url") or "")[:200]); tool_n[b["name"]] += 1
                elif b.get("type") == "tool_result":
                    name, target = calls.get(b.get("tool_use_id"), ("?", ""))
                    c = b.get("content"); size = len(c) if isinstance(c, str) else sum(len(x.get("text", "")) if x.get("type") == "text" else 6000 for x in c or [] if isinstance(x, dict))
                    tool_chars[name] += size
                    if name == "Read" and target:
                        key = pathlib.Path(target).name; file_chars[key] += size; file_n[key] += 1
    if not runs:
        print(f"{agent}: no runs"); return
    tot = sum(tool_chars.values()) or 1
    print(f"\n== {agent}: {runs} runs, median turns {statistics.median(turns):.0f}, median FIXED context at turn 1 {statistics.median(base):,.0f} tokens, median prompt {statistics.median(first_prompt or [0]):,.0f} chars")
    print("   tool calls/run: " + ", ".join(f"{k} {v / runs:.1f}" for k, v in tool_n.most_common(6)))
    print("   tool-result chars/run: " + ", ".join(f"{k} {v / runs:,.0f} ({v / tot:.0%})" for k, v in tool_chars.most_common(5)))
    print("   Read, by file (chars/run, reads/run): " + "; ".join(f"{k} {v / runs:,.0f} x{file_n[k] / runs:.1f}" for k, v in file_chars.most_common(7)))

for a in sys.argv[1:]:
    profile(a)
