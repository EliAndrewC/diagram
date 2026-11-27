import subprocess,time,statistics,os,resource,sys
S=os.path.dirname(os.path.abspath(__file__)); H=S+"/sbx/scripts/hooks/"; G=S+"/target/l7r-guard.good"
env=dict(os.environ, L7R_GUARD_TARGET=S+"/target"); env.pop("L7R_GUARD_FRESH",None); envf=dict(env,L7R_GUARD_FRESH=G)
cmds={
"A today (bash walk, [ -nt ]), by its shebang (env bash)":([H+"v0.sh","PreToolUse"],env),
"B the walk skipped (L7R_GUARD_FRESH): the floor without a walk":([H+"v0.sh","PreToolUse"],envf),
"C no-fork walk ([[ -nt ]])":([H+"v1.sh","PreToolUse"],env),
"D find -newer -print -quit":([H+"v2.sh","PreToolUse"],env),
"G as built (find, fallback walk)":([H+"v3.sh","PreToolUse"],env),
"E today, by `bash` (no env hop)":(["bash",H+"v0.sh","PreToolUse"],env),
"F find, by `bash` (both levers)":(["bash",H+"v2.sh","PreToolUse"],env),
}
N=int(sys.argv[1]); w={k:[] for k in cmds}; c={k:[] for k in cmds}; L=[]
for i in range(N):
  L.append(os.getloadavg()[0])
  for k,(cmd,e) in cmds.items():
    r0=resource.getrusage(resource.RUSAGE_CHILDREN); t=time.perf_counter()
    p=subprocess.run(cmd,env=e,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL); assert p.returncode==0,(k,p.returncode)
    w[k].append((time.perf_counter()-t)*1000); r1=resource.getrusage(resource.RUSAGE_CHILDREN)
    c[k].append((r1.ru_utime-r0.ru_utime+r1.ru_stime-r0.ru_stime)*1000)
p90=lambda v: sorted(v)[int(round(.9*(len(v)-1)))]
print(f"load1 {min(L):.1f} to {max(L):.1f} (22 cores), {N} runs each, round-robin; the binary a stub (/bin/true), GOOD newer than every source")
print("| wrapper variant | wall median | wall p90 | wall min | CPU median |")
for k in cmds: print(f"| {k} | {statistics.median(w[k]):.2f} | {p90(w[k]):.2f} | {min(w[k]):.2f} | {statistics.median(c[k]):.2f} |")
