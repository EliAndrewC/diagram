import re,subprocess,sys,collections
root='.'
def g(*a): return subprocess.run(['git','-C',root,*a],capture_output=True,text=True).stdout
P=r'`((?:rust|scripts|tests)/[^`\s*<>{}]+?)(?:::[^`]*)?`'
NEW=[re.compile(P+r',? \(?new\b'), re.compile(r'\b[Nn]ew (?:module|file|test file|test|suite|crate|script|guard|binary)s?,? (?:\w+ )?'+P)]
TOK=re.compile(r'`([^`\s]+)`')
SRCX=re.compile(r'\.(rs|sh|py|toml)$')
log=g('log','--since=2026-11-20','--format=%H %s','--grep=ticked (make land)')
stats=collections.Counter(); fired=[]
for l in log.splitlines():
    sha,s=l.split(' ',1)
    m=re.match(r'(\S+): ((?:T\d+ )+)ticked',s)
    if not m: continue
    feat,tasks=m.group(1),m.group(2).split()
    par=sha+'^'
    files=set(g('ls-tree','-r','--name-only',par).split('\n'))
    dirs={'/'.join(f.split('/')[:i]) for f in files for i in range(1,f.count('/')+1)}
    def held(x):
        x=x.rstrip('/').rstrip(':,;.')
        if x in files or x in dirs: return True
        return any(f.endswith('/'+x) for f in files if f.startswith(('rust/','scripts/','tests/')))
    tm=g('show',f'{par}:specs/{feat}/tasks.md'); pm=g('show',f'{par}:specs/{feat}/plan.md')
    occ=re.search(r'(?ms)^## Occasions\s*$(.*?)(?=^## |\Z)',tm)
    for t in tasks:
        stats['tasks']+=1
        lines=[x for x in (occ.group(1).splitlines() if occ else []) if re.match(r'^- [a-z-]+: (?:T\d+, )*%s\b'%t,x) or re.match(r'^- none: (?:T\d+,? )*%s\b'%t,x)]
        toks=[x for ln in lines for x in TOK.findall(ln) if (x.startswith(('rust/','scripts/','tests/')) or SRCX.search(x)) and not re.search(r'[*<>{}]',x)]
        secs=[s for s in re.split(r'(?m)^(?=### )',pm) if re.match(r'### (?:T\d+, )*%s\b'%t,s)]
        new=set()
        for sct in secs:
            for r in NEW: new|=set(r.findall(sct))
        if lines: stats['with-line']+=1
        if new: stats['with-new']+=1
        stats['occ-paths']+=len(toks); stats['new-paths']+=len(new)
        bo=[x for x in toks if not held(x)]; bn=[x for x in new if not held(x)]
        if bo or bn: fired.append((sha[:10],t,bo,bn))
print(dict(stats))
for f in fired: print(f)
