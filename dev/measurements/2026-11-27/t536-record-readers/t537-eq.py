"""t537: make plan-section of every archived id, split against flat, on the copy; and the parts' bodies against the flat files."""
import json, os, shutil, subprocess, sys
S = sys.argv[1]
REPO = f"{S}/repo"; F = f"{REPO}/specs/451-time-retro-and-efficiency"; GATE = f"{S}/target/tool/l7r-gate"
env = dict(os.environ, CLAUDE_PROJECT_DIR=REPO, L7R_GATE_TARGET=f"{S}/target", L7R_GATE_CARGO="/bin/false")
idx = json.load(open(f"{F}/archive/index.json"))
ids = sorted(idx["tasks"]["plan-done.md"], key=lambda t: (int("".join(c for c in t[1:] if c.isdigit())), t))
def section():
    r = subprocess.run([GATE, "plan", "section", "451-time-retro-and-efficiency", ",".join(ids)], cwd=REPO, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout
split = section()
def body(p):
    t = open(p).read()
    head, rest = t.split("\n\n", 1)
    return rest
for rec in ["plan-done.md", "tasks-done.md"]:
    joined = "".join(body(f"{F}/archive/{p}") for p in idx["parts"][rec])
    flat = open(f"{S}/flat/{rec}").read()
    flat_body = flat.split("\n\n", 1)[1] if flat.startswith("# ") else flat
    print(rec, "parts", len(idx["parts"][rec]), "bodies equal flat minus title:", joined == flat_body, len(joined), len(flat))
shutil.move(f"{F}/archive", f"{S}/archive-aside")
for rec in ["plan-done.md", "tasks-done.md"]:
    shutil.copy(f"{S}/flat/{rec}", f"{F}/{rec}")
flat = section()
for rec in ["plan-done.md", "tasks-done.md"]:
    os.remove(f"{F}/{rec}")
shutil.move(f"{S}/archive-aside", f"{F}/archive")
print("ids", len(ids), "exit", split[0], flat[0], "bytes", len(split[1]), len(flat[1]), "identical:", split[1] == flat[1])
sizes = sorted(os.path.getsize(f"{F}/archive/{p}") for r in idx["parts"] for p in idx["parts"][r])
print("parts", len(sizes), "largest", sizes[-3:], "smallest", sizes[:2])
