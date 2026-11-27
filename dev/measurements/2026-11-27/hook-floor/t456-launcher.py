"""451 T456: the hook chain with the launcher as it was (`exec "$h"`, the wrapper's `#!/usr/bin/env bash`) and as changed
(`exec bash "$h"`), round-robin, 40 runs, in a scratch tree whose rust/ and .cargo/ link to the real tree's (T439's method).
Usage: python3 t456-launcher.py <scratch dir holding tree/ and target/> <runs>"""
import os, resource, statistics, subprocess, sys, time

S, N = sys.argv[1], int(sys.argv[2])
H = S + "/tree/scripts/hooks/"
env = dict(os.environ, CLONE_MAIN="/nonexistent-t456", L7R_GUARD_TARGET=S + "/target")
cmds = {
    "/usr/bin/env bash -c :": ["/usr/bin/env", "bash", "-c", ":"],
    "bash -c :": ["bash", "-c", ":"],
    "l7r-hook as it was (exec \"$h\": env hop)": [H + "l7r-hook-old", "PreToolUse"],
    "l7r-hook as changed (exec bash \"$h\")": [H + "l7r-hook-new", "PreToolUse"],
}
w = {k: [] for k in cmds}
c = {k: [] for k in cmds}
L = []
for _ in range(N):
    L.append(os.getloadavg()[0])
    for k, cmd in cmds.items():
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t = time.perf_counter()
        subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        w[k].append((time.perf_counter() - t) * 1000)
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        c[k].append((r1.ru_utime - r0.ru_utime + r1.ru_stime - r0.ru_stime) * 1000)
p90 = lambda v: sorted(v)[int(round(0.9 * (len(v) - 1)))]
print(f"load1 {min(L):.1f} to {max(L):.1f} ({os.cpu_count()} cores), {N} runs each, round-robin")
print("| row | wall median | wall p90 | wall min | CPU median |")
print("|---|---|---|---|---|")
for k in cmds:
    print(f"| {k} | {statistics.median(w[k]):.2f} | {p90(w[k]):.2f} | {min(w[k]):.2f} | {statistics.median(c[k]):.2f} |")
