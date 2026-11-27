import subprocess,time,statistics,os,resource,sys
T="/diagram/.clones/diagram-backlog-t271";G="/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t439/target/l7r-guard.good";S="/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t439"
env=dict(os.environ, CLONE_MAIN="/nonexistent-t439", L7R_GUARD_TARGET=S+"/target"); envf=dict(env,L7R_GUARD_FRESH=G)
SRC=[T+"/rust/guard",T+"/rust/Cargo.toml",T+"/rust/Cargo.lock",T+"/.cargo/config.toml"]
cmds={
"1 dash -c :":(["dash","-c",":"],env),
"2 /usr/bin/env bash -c :":(["/usr/bin/env","bash","-c",":"],env),
"3 bash -c :":(["bash","-c",":"],env),
"4 exec of a binary (/bin/true)":(["/bin/true"],env),
"5 l7r-guard.sh, walk skipped (L7R_GUARD_FRESH)":([T+"/scripts/hooks/l7r-guard.sh","PreToolUse"],envf),
"6 l7r-guard.sh, as today (one walk)":([T+"/scripts/hooks/l7r-guard.sh","PreToolUse"],env),
"7 l7r-hook -> l7r-guard.sh -> stub, as today":([T+"/scripts/hooks/l7r-hook","PreToolUse"],env),
"8 bash: the globstar expansion alone":(["bash","-c","shopt -s globstar nullglob; a=(/diagram/.clones/diagram-backlog-t271/rust/guard/**)"],env),
"9 bash: the walk as newer() runs it":(["bash","-c","shopt -s globstar nullglob; for f in /diagram/.clones/diagram-backlog-t271/rust/guard/**; do [ \"$f\" -nt /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t439/target/l7r-guard.good ] && exit 0; done; exit 1"],env),
"10 find SOURCES -newer GOOD -print -quit":(["find"]+SRC+["-newer",G,"-print","-quit"],env),
}
N=int(sys.argv[1]); w={k:[] for k in cmds}; c={k:[] for k in cmds}; L=[]
for i in range(N):
  L.append(os.getloadavg()[0])
  for k,(cmd,e) in cmds.items():
    r0=resource.getrusage(resource.RUSAGE_CHILDREN); t=time.perf_counter()
    subprocess.run(cmd,env=e,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
    w[k].append((time.perf_counter()-t)*1000); r1=resource.getrusage(resource.RUSAGE_CHILDREN)
    c[k].append((r1.ru_utime-r0.ru_utime+r1.ru_stime-r0.ru_stime)*1000)
p90=lambda v: sorted(v)[int(round(.9*(len(v)-1)))]
print(f"load1 {min(L):.1f} to {max(L):.1f} (22 cores), {N} runs each, round-robin")
print("| hop | wall median | wall p90 | wall min | CPU median | CPU min |")
for k in cmds: print(f"| {k} | {statistics.median(w[k]):.2f} | {p90(w[k]):.2f} | {min(w[k]):.2f} | {statistics.median(c[k]):.2f} | {min(c[k]):.2f} |")
