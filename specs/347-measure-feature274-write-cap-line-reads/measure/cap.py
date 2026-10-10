#!/usr/bin/env python3
"""Feature 347: did the write sessions after 274 landed stay inside its cap (4 questions, 10 new registry keys)?

Usage: cap.py   (reads sessions-post.json; prints one line per write session over a cap, then the totals)

Zero `continued` lines alone cannot tell "nobody reached the cap" from "sessions passed it unsplit", so each write
session after the landing is measured directly:
- questions: the brief counted by the runner's own counter, in BOTH forms it has had - the one in force at the landing
  (`scripts/_brief_load.py` at 6555db77b, which reads `PAGE= SECTION=` against the per-page record of that commit) and
  today's (`scripts/pages/brief_load.py`, which reads `Q=NNNN` against the flat record feature 303 made) - and the
  larger taken, since a brief is written in one form or the other;
- the declared exemption (`<!-- page-load: kind=... -->`), which the cap does not count;
- new registry keys: the `make reserve KIND=registry` calls in the write session's own transcript (the key cap lives
  in `make reserve`, which refuses the eleventh);
- escapes: the guard log's write-cap / key-cap entries (`~/.claude/guard-log/`, written by the runner and `make reserve`
  on every escape), by clone and stated reason. (A transcript grep for the variable also finds docs quoting it.)
"""

import collections
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile

H = pathlib.Path(__file__).parent
REPO = H.parent.parent.parent
LANDING = "6555db77b"
c274 = importlib.util.module_from_spec(s := importlib.util.spec_from_file_location("c274", REPO / "specs/274-leaner-research-sessions/measure/collect.py"))
s.loader.exec_module(c274)


def module(name, source):
    path = pathlib.Path(tempfile.mkdtemp()) / f"{name}.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True).stdout


old = module("brief_load_old", git("show", f"{LANDING}:scripts/_brief_load.py").decode())
sys.path.insert(0, str(REPO / "scripts/pages"))
new = module("brief_load_new", (REPO / "scripts/pages/brief_load.py").read_text())
old_record = pathlib.Path(tempfile.mkdtemp())
with tempfile.TemporaryFile() as fh:
    fh.write(git("archive", LANDING, ".claude/skills/diagram/research"))
    fh.seek(0)
    tarfile.open(fileobj=fh).extractall(old_record, filter="data")
old_record = old_record / ".claude/skills/diagram/research"
new_record = REPO / "research"

S = [x for x in json.loads((H / "sessions-post.json").read_text()) if x["kind"] == "write"]
over, n_q, n_k, missing = [], 0, 0, collections.Counter()
for x in S:
    brief = pathlib.Path(x["brief_dir"]) / x["brief"]
    text = brief.read_text(encoding="utf-8", errors="replace") if brief.exists() else ""
    kind = new.declared(text)
    q = max(old.count(text, old_record)[0], new.count(text, new_record)[0]) if text else -1
    tp = pathlib.Path.home() / f".claude/projects/-diagram--clones-{x['clone']}/{x['sid']}.jsonl"
    _tr, asked = c274.tools([r for r in c274.recs(tp) if not r.get("isSidechain")])
    keys = sum(len(re.findall(r"make reserve\b[^;&|\n]*KIND=registry", str(i.get("command", "")))) for n, i, _t in asked.values() if n == "Bash")
    n_q += q > 4 and not kind
    n_k += keys > 10
    missing[x["feature"]] += q < 0
    if (q > 4 and not kind) or keys > 10:
        over.append(f"  {x['group']}: {q} questions, {keys} keys reserved")
exempt = sum(1 for x in S if new.declared((pathlib.Path(x["brief_dir"]) / x["brief"]).read_text(errors="replace") if (pathlib.Path(x["brief_dir"]) / x["brief"]).exists() else ""))
escapes = collections.Counter()
for f in (pathlib.Path.home() / ".claude/guard-log").glob("*.json"):
    body = f.read_text(errors="replace")
    if "-cap" in body and (d := json.loads(body)).get("rule") in ("write-cap", "key-cap") and f.name >= "20260928T0343":
        escapes[(d["rule"], d.get("session_name"), re.sub(r"\s+", " ", str(d.get("detail")))[:110])] += 1
print("\n".join(over) or "  none")
print(f"{len(S)} write sessions after the landing: {exempt} declared an exempt page-load; {n_q} counted over 4 questions undeclared; "
      f"{n_k} reserved over 10 registry keys; briefs no longer on disk (questions uncounted) {dict(missing)}; cap escapes logged {sum(escapes.values())}:")
for (rule, clone, why), n in sorted(escapes.items()):
    print(f"  {n:4} {rule} {clone}: {why}")
