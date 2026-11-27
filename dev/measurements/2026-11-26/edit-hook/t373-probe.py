# t373: one call under the shim; prints the process tree's START/END/SPAWN lines with durations, the writes, and a count of reads by directory.
#   python3 t373-probe.py <state> <session> <case> [--only <guard>]
import os,sys,subprocess,collections,importlib.util
S=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('t',S+'/t373-time.py'); src=open(S+'/t373-time.py').read().replace('\nmain()\n','\n'); t={'__file__':S+'/t373-time.py'}; exec(compile(src,'t373-time.py','exec'),t)
state,session,case=sys.argv[1:4]; only=sys.argv[5] if len(sys.argv)>5 else None
event=case.split('.')[1]; log=f'{S}/probe.{state}.{session}.{case}{"."+only if only else ""}.log'
if os.path.exists(log): os.remove(log)
e=t['env'](S+'/home'); e['T373_OUT']=log; e['LD_PRELOAD']=S+'/t373-shim.so'
t['set_state'](state)
argv=[t['BIN'],'--only',only+'-hooks',event] if only else [t['W']+'/scripts/hooks/l7r-hook',event]
p=subprocess.run(argv,stdin=open(f'{S}/payloads/{session}.{case}.json','rb'),capture_output=True,env=e,text=True)
t['set_state']('clean')
print('exit',p.returncode,'stdout',p.stdout[:600],'stderr',p.stderr[:900])
start={}; reads=collections.Counter(); spawns=0
for l in open(log,errors='replace'):
    ms,pid,ppid,kind,*rest=l.rstrip('\n').split(' ',4); rest=rest[0] if rest else ''
    if kind=='START': start[pid]=(float(ms),rest)
    elif kind=='END':
        s=start.get(pid,(float(ms),'?')); print(f'{float(ms)-s[0]:8.1f} ms  pid {pid} ppid {ppid}  {s[1][:230].replace(S,"$S")}  [{rest}]')
    elif kind=='SPAWN': spawns+=1
    elif kind in('OPENW','MKDIR','RENAME','UNLINK'):
        if not rest.startswith('/dev/'): print(f'   {kind} {rest.replace(S,"$S")}')
    elif kind=='OPENR':
        r=rest.replace(S,'$S'); reads['/'.join(r.split('/')[:-1]) if len(r.split('/'))>2 else r]+=1
print('spawn calls',spawns,'; reads by directory:'); [print(f'   {n:6d} {d}') for d,n in reads.most_common(12)]
