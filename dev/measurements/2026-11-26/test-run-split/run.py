#!/usr/bin/env python3
"""451 T315: one run of a crate's test binary, as `cargo test` runs it (the crate's directory, cargo's variables, a TMPDIR of its
own), timed around the process, with what the brief asks beside it. One run at a time; prints one JSON line.

  run.py --crate rust/gate/crates/land --exe <test binary> [--tmp-parent DIR] [--threads N] [--report OUT.jsonl]
         [--sample] [--count SHIM.so] [--gitlog] [--env K=V ...] [-- <libtest words>]

--report   per-test seconds from libtest's own JSON (`-Z unstable-options --format json --report-time`, RUSTC_BOOTSTRAP=1 at RUN time)
--sample   the TMPDIR walked every 50 ms: its peak bytes (allocated and apparent), files and directories
--count    the file calls of the run and its children counted by the LD_PRELOAD shim (count-shim.c)
--gitlog   every `git` the run starts logged by a wrapper first on PATH (its words), then the real git run
"""
import argparse, json, os, resource, shutil, subprocess, sys, tempfile, threading, time

p = argparse.ArgumentParser()
p.add_argument("--crate", required=True); p.add_argument("--exe", required=True)
p.add_argument("--tmp-parent", default=os.environ.get("T315_TMP", "/tmp"))
p.add_argument("--threads"); p.add_argument("--report"); p.add_argument("--sample", action="store_true")
p.add_argument("--count"); p.add_argument("--gitlog", action="store_true"); p.add_argument("--env", action="append", default=[])
p.add_argument("--keep-output"); p.add_argument("rest", nargs="*")
a = p.parse_args()

root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
crate = os.path.join(root, a.crate)
tmp = tempfile.mkdtemp(prefix="t315-tests-", dir=a.tmp_parent)
side = tempfile.mkdtemp(prefix="t315-side-")
env = dict(os.environ)
env.update(TMPDIR=tmp, CARGO_MANIFEST_DIR=crate, CARGO="cargo",
           CARGO_TARGET_DIR=os.path.dirname(os.path.dirname(os.path.dirname(a.exe))),
           PATH=os.path.expanduser("~/.cargo/bin") + ":" + env["PATH"])
name = [l.split('"')[1] for l in open(os.path.join(crate, "Cargo.toml")) if l.startswith("name")][0]
env["CARGO_PKG_NAME"] = name
for kv in a.env:
    k, v = kv.split("=", 1); env[k] = v
words = [a.exe]
if a.report:
    env["RUSTC_BOOTSTRAP"] = "1"; words += ["-Z", "unstable-options", "--format", "json", "--report-time"]
else:
    words += ["-q"]
if a.threads: words += ["--test-threads", a.threads]
words += a.rest
counts = None
if a.count:
    counts = os.path.join(side, "counts"); open(counts, "wb").write(b"\0" * 8 * 9)
    env["T315_COUNTS"] = counts; env["LD_PRELOAD"] = a.count
gitlog = None
if a.gitlog:
    gitlog = os.path.join(side, "gitlog"); real = shutil.which("git")
    w = os.path.join(side, "bin"); os.mkdir(w)
    open(os.path.join(w, "git"), "w").write(f'#!/bin/sh\necho "$*" >> "{gitlog}"\nexec {real} "$@"\n'); os.chmod(os.path.join(w, "git"), 0o755)
    env["PATH"] = w + ":" + env["PATH"]

peak = {"bytes": 0, "apparent": 0, "files": 0, "dirs": 0, "samples": 0}
stop = threading.Event()
def walk(d):
    b = ap = f = n = 0
    try:
        for e in os.scandir(d):
            try:
                if e.is_dir(follow_symlinks=False):
                    x = walk(e.path); b += x[0]; ap += x[1]; f += x[2]; n += x[3] + 1
                else:
                    s = e.stat(follow_symlinks=False); b += s.st_blocks * 512; ap += s.st_size; f += 1
            except OSError: pass
    except OSError: pass
    return b, ap, f, n
def sampler():
    while not stop.is_set():
        b, ap, f, n = walk(tmp)
        peak["bytes"] = max(peak["bytes"], b); peak["apparent"] = max(peak["apparent"], ap)
        peak["files"] = max(peak["files"], f); peak["dirs"] = max(peak["dirs"], n); peak["samples"] += 1
        stop.wait(0.05)
if a.sample: threading.Thread(target=sampler, daemon=True).start()

def io():
    return {k: int(v) for k, v in (l.split(": ") for l in open("/proc/self/io"))}
load = open("/proc/loadavg").read().split()[0]
io0, r0, t0 = io(), resource.getrusage(resource.RUSAGE_CHILDREN), time.monotonic()
out = open(a.report, "w") if a.report else (open(a.keep_output, "w") if a.keep_output else subprocess.DEVNULL)
rc = subprocess.run(words, cwd=crate, env=env, stdout=out, stderr=subprocess.STDOUT if a.keep_output else subprocess.DEVNULL).returncode
wall = time.monotonic() - t0
r1, io1 = resource.getrusage(resource.RUSAGE_CHILDREN), io()
stop.set()
res = {"crate": a.crate, "rc": rc, "load": float(load), "wall_s": round(wall, 2), "user_s": round(r1.ru_utime - r0.ru_utime, 2),
       "sys_s": round(r1.ru_stime - r0.ru_stime, 2), "threads": a.threads or "default", "tmp_parent": a.tmp_parent, "env": a.env}
res["cpu_over_wall"] = round((res["user_s"] + res["sys_s"]) / wall, 1)
res["write_calls"] = io1["syscw"] - io0["syscw"]; res["write_chars_mb"] = round((io1["wchar"] - io0["wchar"]) / 1e6, 1)
res["disk_write_mb"] = round((io1["write_bytes"] - io0["write_bytes"]) / 1e6, 1)
if a.sample: res["peak"] = peak
res["left_at_end"] = walk(tmp)[2:]
if counts:
    import struct
    v = struct.unpack("9q", open(counts, "rb").read(72))
    res["calls"] = dict(zip(["create", "mkdir", "unlink", "rmdir", "rename", "fsync", "fdatasync", "sync_file_range", "processes"], v))
if gitlog and os.path.exists(gitlog):
    lines = open(gitlog).read().splitlines(); verbs = {}
    for l in lines:
        ws = l.split(); i = 0
        while i < len(ws) and ws[i].startswith("-"): i += 2 if ws[i] in ("-C", "-c") else 1
        v = ws[i] if i < len(ws) else "?"; verbs[v] = verbs.get(v, 0) + 1
    res["git_processes"] = len(lines); res["git_verbs"] = dict(sorted(verbs.items(), key=lambda kv: -kv[1])[:12])
shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(side, ignore_errors=True)
print(json.dumps(res))
