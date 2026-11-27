"""t537: which of make quick's checks reads the archive's parts, on the split copy, under T536's read counter."""
import os, subprocess, sys
S = sys.argv[1]; REPO = f"{S}/repo"; F = f"{REPO}/specs/451-time-retro-and-efficiency/"
GATE = f"{S}/target/tool/l7r-gate"
env = dict(os.environ, CLAUDE_PROJECT_DIR=REPO, L7R_GATE_TARGET=f"{S}/target", L7R_GATE_CARGO="/bin/false")
for words in [["check", "house-style-delta", "."], ["check", "question-size"], ["check", "file-scale", "."], ["check", "spec-lint", "--delta", "."],
              ["record", "check", "glossary"], ["check", "partial-citations", "."], ["check", "gm-attributions", "."]]:
    log = f"{S}/t537-qt.txt"
    if os.path.exists(log): os.remove(log)
    e = dict(env, LD_PRELOAD=f"{S}/t536-readcount.so", T536_PREFIX=F, T536_LOG=log, T536_SAFE=S)
    r = subprocess.run([GATE] + words, cwd=REPO, env=e, capture_output=True, text=True)
    b = {}
    for l in open(log) if os.path.exists(log) else []:
        f = l.split("\t")
        if f[0] != "WRITE" and "/archive/" in f[1]:
            k = "plan-done parts" if "plan-done" in f[1] else "tasks-done parts" if "tasks-done" in f[1] else f[1].rsplit("/", 1)[1]
            b[k] = b.get(k, 0) + int(f[2])
    print(" ".join(words), "exit", r.returncode, b)
