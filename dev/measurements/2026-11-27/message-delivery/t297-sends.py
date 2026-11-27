import json,sys
p=sys.argv[1]
calls={}
out=[]
with open(p) as f:
    for line in f:
        if 'SendMessage' not in line and 'tool_result' not in line: continue
        try: d=json.loads(line)
        except: continue
        m=d.get('message') or {}
        c=m.get('content')
        if not isinstance(c,list): continue
        for b in c:
            if not isinstance(b,dict): continue
            if b.get('type')=='tool_use' and b.get('name')=='SendMessage':
                calls[b['id']]=(d.get('timestamp'),b.get('input'))
            elif b.get('type')=='tool_result' and b.get('tool_use_id') in calls:
                t,inp=calls[b['tool_use_id']]
                rc=b.get('content')
                if isinstance(rc,list): rc=' '.join(x.get('text','') for x in rc if isinstance(x,dict))
                out.append({'send':t,'result_ts':d.get('timestamp'),'input':inp,'result':rc})
json.dump(out,open(sys.argv[2],'w'),indent=1)
print(len(calls),len(out))
