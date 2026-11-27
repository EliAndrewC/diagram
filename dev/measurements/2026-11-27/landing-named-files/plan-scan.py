import re,subprocess,sys
root=sys.argv[1]
files=set(subprocess.run(['git','-C',root,'ls-tree','-r','--name-only','HEAD'],capture_output=True,text=True).stdout.split('\n'))
SRC=('rust/','scripts/','tests/')
P=r'`((?:rust|scripts|tests)/[^`\s*<>{}]+)`'
NEW=[re.compile(P+r',? \(?new\b'), re.compile(P+r' \(new\b'), re.compile(r'\bnew (?:module|file|test file|suite|crate|script|guard)s?,? '+P)]
def held(x):
    x=x.rstrip('/')
    return x in files or any(f.startswith(x+'/') for f in files)
n=bad=secs=0
for fn in sys.argv[2:]:
    t=open(fn).read()
    for sec in re.split(r'(?m)^(?=### T)',t):
        hits=set()
        for r in NEW: hits|=set(r.findall(sec))
        if not hits: continue
        secs+=1
        for h in hits:
            n+=1
            if not held(h): bad+=1; print(sec.split('\n')[0][:50],'|',h)
print('sections',secs,'new paths',n,'absent',bad)
