import json, re
T = "/tmp/claude-1000/-diagram/7667114a-3a71-4876-aaeb-b37262936c6f/tasks/"
CASES = [("V2","a073c73200730b06e","97f6d769ce72"),("V2","a073c73200730b06e","100916836bb9"),("V1","a043df3105b2fe3a4","04c46c135344"),("V1","a043df3105b2fe3a4","3cf980c9fd08"),("S","a1acd46d95a34f348","c36ae8c62a1c"),("V2","a073c73200730b06e","e542a5322e62")]
def text(c):
    if isinstance(c, str): return c
    if isinstance(c, list): return " ".join(text(x.get("text", x.get("content", ""))) if isinstance(x, dict) else str(x) for x in c)
    return str(c)
for run, aid, sid in CASES:
    for line in open(T + aid + ".output"):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get("message") or {}
        cont = m.get("content")
        if not isinstance(cont, list): continue
        for c in cont:
            if c.get("type") == "tool_result":
                t = text(c.get("content"))
                i = t.find(sid)
                if i >= 0:
                    print(f"[{run} {sid}] ...{t[max(0,i-60):i+420]!r}\n"); break
        else: continue
        break
