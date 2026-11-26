#!/usr/bin/env python3
"""451 T347: the memory of one command's own process tree. The command is started in a session of its own and /proc is read every
20 ms: every process of that session (make, the gate, cargo, each rustc, the linker `cc` and the `rust-lld` it runs, the test
binaries) is summed - RssAnon (anonymous memory, what the container's limit counts: docs/process-decisions.md, "Two code builders at
once"), VmRSS (with the file pages it maps) - and the rustc and linkers alive are counted. Each pid's last VmHWM is kept too.
LIMITS: a spike shorter than the interval between two reads is missed (the sum of every pid's VmHWM, printed as `hwm_sum`, is the
upper bound: it adds peaks that were not at the same instant, and file pages); a process that leaves the session (none of the
checks' does) is not seen; the container's own `anon` is read beside each sample, but other trees' work moves it.
usage: mem-sample.py <samples.tsv> -- <command ...>      prints one summary line; the samples are `t anon rss rustc linkers procs cg_anon`"""
import os, subprocess, sys, time
out = sys.argv[1]; cmd = sys.argv[sys.argv.index("--") + 1:]
KB = ("VmHWM:", "VmRSS:", "RssAnon:")
def cg_anon():
    for l in open("/sys/fs/cgroup/memory.stat"):
        if l.startswith("anon "): return int(l.split()[1])
p = subprocess.Popen(cmd, start_new_session=True); sid = p.pid
hwm = {}; rows = []; t0 = time.time()
while p.poll() is None:
    anon = rss = rustc = link = n = 0
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue
        try:
            st = open(f"/proc/{pid}/stat").read()
            comm = st[st.index("(") + 1:st.rindex(")")]
            if int(st[st.rindex(")") + 2:].split()[3]) != sid: continue
            v = {}
            for l in open(f"/proc/{pid}/status"):
                k = l.split(None, 1)[0]
                if k in KB: v[k] = int(l.split()[1]) * 1024
        except (OSError, ValueError): continue
        n += 1; anon += v.get("RssAnon:", 0); rss += v.get("VmRSS:", 0)
        rustc += comm == "rustc"; link += comm in ("cc", "ld", "rust-lld", "ld.lld", "collect2")
        hwm[pid] = (comm, v.get("VmHWM:", 0), time.time())
    rows.append((time.time(), anon, rss, rustc, link, n, cg_anon()))
    time.sleep(0.02)
with open(out, "w") as f:
    for r in rows: f.write("%.3f\t%d\t%d\t%d\t%d\t%d\t%d\n" % r)
with open(out + ".hwm", "w") as f:
    for pid, (comm, h, t) in hwm.items(): f.write(f"{t:.3f}\t{pid}\t{comm}\t{h}\n")
G = 2 ** 20
print("rc=%d wall=%.2f samples=%d peak_anon=%.0fMiB peak_rss=%.0fMiB hwm_sum=%.0fMiB max_rustc=%d max_linkers=%d" % (
    p.returncode, time.time() - t0, len(rows), max(r[1] for r in rows) / G, max(r[2] for r in rows) / G,
    sum(h for _, h, _ in hwm.values()) / G, max(r[3] for r in rows), max(r[4] for r in rows)))
sys.exit(p.returncode)
