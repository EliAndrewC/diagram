#!/usr/bin/env python3
"""451 T315: what a throwaway git repository costs, made four ways, N at a time, one after another (wall seconds a repository):
  init          `git init -q -b main` alone
  init-bare-tpl the same with GIT_TEMPLATE_DIR an empty directory (no sample hooks, no description, no info/exclude)
  commit        init, one file written, `git add -A`, `git commit -q -m x` (three git processes)
  commit-bare   the same with the empty template
  copy          a repository made once by `commit`, copied whole (`cp -r`) - a shared fixture copied per test
  remove        `rm -rf` of one `commit` repository
usage: git-fixture-bench.py <parent dir> [N=60] [rounds=3]      (each round runs every way once, in turn)"""
import os, shutil, subprocess, sys, tempfile, time, statistics
parent = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 60; rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
base = tempfile.mkdtemp(prefix="t315-gitbench-", dir=parent); empty = os.path.join(base, "empty-template"); os.mkdir(empty)
ident = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
def git(d, env, *a): subprocess.run(["git", "-C", d, *a], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def make(d, env, commit):
    os.mkdir(d); git(d, env, "init", "-q", "-b", "main")
    if commit:
        open(os.path.join(d, "f.txt"), "w").write("x\n"); git(d, env, "add", "-A"); git(d, env, "commit", "-q", "-m", "x")
plain = {**os.environ, **ident}; bare = {**plain, "GIT_TEMPLATE_DIR": empty}
fixture = os.path.join(base, "fixture"); make(fixture, plain, True)
ways = {"init": lambda d: make(d, plain, False), "init-bare-tpl": lambda d: make(d, bare, False), "commit": lambda d: make(d, plain, True),
        "commit-bare": lambda d: make(d, bare, True), "copy": lambda d: subprocess.run(["cp", "-r", fixture, d], check=True)}
got = {k: [] for k in list(ways) + ["remove", "copy-in-process"]}
for r in range(rounds):
    for k, f in ways.items():
        dirs = [os.path.join(base, f"{k}-{r}-{i}") for i in range(N)]
        t = time.monotonic(); [f(d) for d in dirs]; got[k].append((time.monotonic() - t) / N)
        if k == "commit":
            t = time.monotonic(); [shutil.rmtree(d) for d in dirs]; got["remove"].append((time.monotonic() - t) / N)
        else: [shutil.rmtree(d) for d in dirs]
    dirs = [os.path.join(base, f"cip-{r}-{i}") for i in range(N)]
    t = time.monotonic(); [shutil.copytree(fixture, d) for d in dirs]; got["copy-in-process"].append((time.monotonic() - t) / N); [shutil.rmtree(d) for d in dirs]
files = sum(len(f) for _, _, f in os.walk(fixture)); fd = sum(len(d) for _, d, _ in os.walk(fixture))
shutil.rmtree(base)
print(f"{parent}: N={N} rounds={rounds} load={open('/proc/loadavg').read().split()[0]}; a committed fixture is {files} files in {fd} directories")
for k, v in got.items(): print(f"  {k:16s} median {1000*statistics.median(v):6.1f} ms a repository (spread {1000*min(v):.1f}-{1000*max(v):.1f})")
