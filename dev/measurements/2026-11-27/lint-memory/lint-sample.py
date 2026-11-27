#!/usr/bin/env python3
"""451 T355: the memory of one lint run's own process tree, BY LINT PASS. 451 T347's sampler (`dev/measurements/2026-11-26/
small-build-memory/mem-sample.py`: the command in a session of its own, /proc read every 20 ms, RssAnon and VmRSS summed over
every process of the session), with two things a lint needs that a test build did not:

- THE COMPILER'S NAME. Under `cargo clippy` a workspace crate is compiled by `clippy-driver`, not `rustc`; both are counted, as
  `compilers`, and each one's `--crate-name` is kept.
- THE PASS. The checks write ONE `lint` Phase line a crate for all of its clippy calls, so a pass is read here from the live
  `cargo clippy` process's own words: `targets` (`--all-targets`), `features` (`--all-targets --all-features`), `lib` (`--lib`).

LIMITS, T347's: a spike shorter than the gap between two reads is missed; other trees' work moves the container's own figure.
A compile seen while no `cargo clippy` lives is printed as `no pass`: it is not the lint's (its seconds are first sample to last,
whatever lies between).
usage: lint-sample.py <samples.tsv> -- <command ...>      prints a line a pass and one for the run"""
import os, subprocess, sys, time
out = sys.argv[1]; cmd = sys.argv[sys.argv.index("--") + 1:]
KB = ("VmRSS:", "RssAnon:")
COMPILERS = ("rustc", "clippy-driver")
LINKERS = ("cc", "ld", "rust-lld", "ld.lld", "collect2")
def words(pid):
    try: return open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", "replace").split("\0")
    except OSError: return []
def pass_of(w):
    if "clippy" not in w or "--manifest-path" not in w: return None
    return "lib" if "--lib" in w else "features" if "--all-features" in w else "targets"
p = subprocess.Popen(cmd, start_new_session=True); sid = p.pid
rows = []; t0 = time.time(); names = {}
while p.poll() is None:
    anon = rss = comp = link = n = 0; at = None; live = []
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
        link += comm in LINKERS
        if comm in COMPILERS:
            w = words(pid)
            # `rustc -vV` and the like compile nothing: only a call that names a crate is a compile
            if "--crate-name" in w and w[w.index("--crate-name") + 1] != "___":
                comp += 1
                kind = "test" if "--test" in w else "lib" if "lib" in w[w.index("--crate-type") + 1:][:1] else "bin" if "--crate-type" in w else "?"
                live.append(f"{comm}:{w[w.index('--crate-name') + 1]}:{kind}")
        elif comm.startswith("cargo"):
            at = pass_of(words(pid)) or at
    for name in live: names.setdefault(at, set()).add(name)
    rows.append((time.time(), anon, rss, comp, link, n, at or "-"))
    time.sleep(0.02)
with open(out, "w") as f:
    for r in rows: f.write("%.3f\t%d\t%d\t%d\t%d\t%d\t%s\n" % r)
G = 2 ** 20
def line(tag, r):
    gap = max([b[0] - a[0] for a, b in zip(r, r[1:])] or [0])
    return "  %-8s %6.2f s  anon %5.0f MiB  rss %5.0f MiB  compilers %d  linkers %d  max gap %3.0f ms" % (
        tag, r[-1][0] - r[0][0], max(x[1] for x in r) / G, max(x[2] for x in r) / G, max(x[3] for x in r), max(x[4] for x in r), gap * 1000)
print("rc=%d wall=%.2f samples=%d" % (p.returncode, time.time() - t0, len(rows)))
for tag in ("targets", "features", "lib"):
    r = [x for x in rows if x[6] == tag]
    if r: print(line(tag, r) + "  compiled: " + (" ".join(sorted(names.get(tag, ()))) or "nothing seen"))
# what compiled outside every pass: the launcher rebuilding the checks' own tool, where the edit is in a crate that tool builds from
r = [x for x in rows if x[6] == "-" and x[3]]
if r: print(line("no pass", r) + "  compiled: " + " ".join(sorted(names.get(None, ()))))
print(line("run", rows))
sys.exit(p.returncode)
