import json,sys
f,a,b=sys.argv[1],sys.argv[2],sys.argv[3]
for ln in open(f):
    try: d=json.loads(ln)
    except: continue
    ts=d.get("timestamp","")
    if not (a<=ts<=b): continue
    m=d.get("message",{}); c=m.get("content")
    if isinstance(c,str): print("##",ts,m.get("role"),"TEXT:",c[:1500]); continue
    if not isinstance(c,list): continue
    for it in c:
        t=it.get("type")
        if t=="text": print("##",ts,"TEXT:",it["text"][:2500])
        elif t=="thinking": print("##",ts,"THINK:",it.get("thinking","")[:2500])
        elif t=="tool_use": print("##",ts,"CALL:",json.dumps(it["input"])[:3000])
        elif t=="tool_result":
            cc=it.get("content")
            if isinstance(cc,list): cc=" ".join(x.get("text","") for x in cc if isinstance(x,dict))
            print("##",ts,"RESULT:",str(cc)[:4000])
