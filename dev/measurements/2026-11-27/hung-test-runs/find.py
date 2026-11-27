import json,sys,glob,os
# find Bash tool_use calls with rust-test/builder-checks for rustc, with timestamps in window
wins=[("2026-11-26T18:50","2026-11-26T19:15"),("2026-11-26T19:30","2026-11-26T20:00"),("2026-11-26T21:30","2026-11-26T22:00")]
for f in glob.glob("*.jsonl"):
    try:
        lines=open(f).read().splitlines()
    except: continue
    first=lines[0] if lines else ""
    for ln in lines:
        try: d=json.loads(ln)
        except: continue
        ts=d.get("timestamp","")
        if not any(a<=ts<=b for a,b in wins): continue
        m=d.get("message",{})
        c=m.get("content")
        if not isinstance(c,list): continue
        for it in c:
            if it.get("type")=="tool_use" and it.get("name")=="Bash":
                cmd=it["input"].get("command","")
                if "rust-test" in cmd or "builder-checks" in cmd:
                    print(f,ts,it["id"],repr(cmd[:200]), it["input"].get("timeout"), it["input"].get("run_in_background"))
