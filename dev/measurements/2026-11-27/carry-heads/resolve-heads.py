import re,subprocess,sys
def show(ref,p): return subprocess.run(['git','show',f'{ref}:{p}'],capture_output=True,text=True,check=True).stdout
p='specs/451-time-retro-and-efficiency/plan.md'
def parse(s):
    parts=re.split(r'(?m)^(?=### )',s); return parts[0],[(b.split('\n',1)[0],b) for b in parts[1:]]
opre,o=parse(show('HEAD',p)); tpre,t=parse(show('CHERRY_PICK_HEAD',p)); bpre,b=parse(show('CHERRY_PICK_HEAD~1',p))
for n,L in (('ours',o),('theirs',t),('base',b)):
    hs=[h for h,_ in L]; d=[h for h in set(hs) if hs.count(h)>1]; assert not d,(n,d[:3])
od=dict(o); td=dict(t); bd=dict(b)
changed=[h for h in td if h in bd and td[h].strip()!=bd[h].strip()]
new=[h for h in td if h not in bd]; gone=[h for h in bd if h not in td]
both=[h for h in changed if h in od and od[h].strip()!=bd[h].strip()]
assert not both,('both changed',both)
assert opre==bpre or tpre==bpre
print('theirs changed',[h[:40] for h in changed]); print('new',[h[:40] for h in new]); print('gone',[h[:40] for h in gone])
out=[(h,td[h] if h in changed else x) for h,x in o if h not in gone]
for h in new:
    if h in od: continue
    tid=re.match(r'### (T\d+)',h); tid=tid.group(1) if tid else None
    at=max([i for i,(hh,_) in enumerate(out) if tid and re.match(r'### '+tid+r'[ ,(]',hh)],default=len(out)-1)
    blk=td[h] if td[h].endswith('\n\n') else td[h].rstrip('\n')+'\n\n'
    out.insert(at+1,(h,blk))
open(p,'w').write((opre if tpre==bpre else tpre)+''.join(x for _,x in out))
# then each task's sections in their order: heading, approach, checklist, part 2, part B
s=open(p).read(); parts=re.split(r'(?m)^(?=### )',s); pre,secs=parts[0],parts[1:]
def h(b): return b.split('\n',1)[0]
def tid(b):
    m=re.match(r'### (T\d+)[ ,(]',b); return m.group(1) if m else None
def key(b):
    x=h(b); part2=bool(re.match(r'### T\d+ part 2\b',x)); partB=bool(re.match(r'### T\d+(, T\d+)* part B\b',x))
    r=1 if re.match(r'### T\d+( part 2)? Approach\b',x) else 2 if re.match(r'### T\d+( part 2)? Performance checklist\b',x) else 0
    return (partB, part2, r)
order=[]; groups={}
for b in secs:
    k=tid(b) or id(b)
    if k not in groups: groups[k]=[]; order.append(k)
    groups[k].append(b)
out=pre
for k in order: out+=''.join(x if x.endswith('\n\n') else x.rstrip('\n')+'\n\n' for x in sorted(groups[k],key=key))
open(p,'w').write(out)
