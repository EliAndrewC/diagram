"""Feature 447: for each run and each target source - seen in a tool's output, opened by a tool call, reported."""
import json, sys
T = "/tmp/claude-1000/-diagram/7667114a-3a71-4876-aaeb-b37262936c6f/tasks/"
RUNS = {"S": "a1acd46d95a34f348", "T": "a76e8af174d2a4065", "V1": "a043df3105b2fe3a4", "V2": "a073c73200730b06e"}
SRC = {"Shicang": ["831d8174fa8b"], "Shizuoka": ["e542a5322e62"], "Huizhou": ["04c46c135344"], "Shiroyone": ["f457740405c1", "5649138bf1c5", "a25ab90b505a"],
       "Yayoi": ["d1f4b30193e3"], "Iwamuro": ["7588a47ce738"], "KamiBaba": ["27341e70863d"], "King": ["e81890ad0ea3"], "Taipingqiao": ["29423acf58a9"],
       "Hattori": ["97f6d769ce72"], "Ofuro": ["100916836bb9"], "Konosu": ["c36ae8c62a1c"], "Bray": ["3cf980c9fd08"], "Fei": ["675c43301bf7", "857b0fd46d16"], "Buck": ["b647a7ae9f1a"]}
def text(c):
    if isinstance(c, str): return c
    if isinstance(c, list): return " ".join(text(x.get("text", x.get("content", ""))) if isinstance(x, dict) else str(x) for x in c)
    return str(c)
for run, aid in RUNS.items():
    inputs, outputs, final, cmds = [], [], "", []
    for line in open(T + aid + ".output"):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get("message") or {}
        cont = m.get("content")
        if not isinstance(cont, list): continue
        for c in cont:
            if c.get("type") == "tool_use":
                s = json.dumps(c.get("input"), ensure_ascii=False); inputs.append(s); cmds.append(s[:160])
            elif c.get("type") == "tool_result":
                outputs.append(text(c.get("content")))
            elif c.get("type") == "text" and m.get("role") == "assistant":
                final = c.get("text", "")
    print(f"== {run}: {len(inputs)} tool calls")
    for n, ids in SRC.items():
        seen = any(i in o for o in outputs for i in ids); opened = any(i in s for s in inputs for i in ids); rep = any(i in final for i in ids)
        print(f"  {n:12s} seen={int(seen)} opened={int(opened)} reported={int(rep)}")
    if len(sys.argv) > 1:
        for c in cmds: print("   >", c.replace("\\n", " ")[:160])
