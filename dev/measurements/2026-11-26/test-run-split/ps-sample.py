#!/usr/bin/env python3
"""451 T315: which processes of a tree are alive through one command - /proc read every 50 ms, each distinct command line with the
seconds (from the command's start) it was first and last seen. Says what a gate call does outside its Phase lines.
usage: ps-sample.py <a word every process of interest has in its command line> -- <command ...>"""
import os, subprocess, sys, time
word = sys.argv[1]; cmd = sys.argv[sys.argv.index("--") + 1:]
seen = {}; t0 = time.monotonic(); p = subprocess.Popen(cmd)
while p.poll() is None:
    now = time.monotonic() - t0
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) in (os.getpid(),): continue
        try: a = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
        except OSError: continue
        if word in a:
            k = (pid, a[:260]); seen[k] = (seen.get(k, (now,))[0], now)
    time.sleep(0.05)
for (pid, a), (first, last) in sorted(seen.items(), key=lambda kv: kv[1]):
    print(f"{first:6.2f} {last:6.2f} {a}")
