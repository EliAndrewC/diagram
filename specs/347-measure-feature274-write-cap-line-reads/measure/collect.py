#!/usr/bin/env python3
"""Feature 347: the page sessions run after feature 274 landed, measured as 274's R1 measured those before it.

Usage: collect.py post|r1   -> sessions-post.json | sessions-r1.json

`post` is every page session that started after 274's landing (LANDED below) in any clone; `r1` re-collects 274's own
window (after 250 landed, before 274 did, R1's clones) with THIS script, so the method is checked against R1's published
figures before the two are compared. Each transcript is folded per message id by 274's `collect.py` helpers.

What differs from 274's collector, and why:
- Briefs written after 274 no longer list a check session's questions ("the ones the handoff names"), so a group's
  things checked are counted from its handoff (`<group>-handoff.md`: its distinct `- SECTION=` questions - after
  feature 303 one question can be listed once per heading - and its distinct `- KEY=` registry keys) plus its
  `entry-drift` runs; the brief's own lines are the fallback when there is no handoff.
  On R1's window the two counts agree (K1: 10 questions, 17 keys either way).
- The brief names are no longer only `-write` / `-check-<x>`: `-check`, `-split`, `-finish` and the 292 sweep's
  `<page>-G<NN>-<kind>` are classified too.
- A continuation (`continue.md`) is attributed to its parent's group through the run log's `continued <a> -> <b>` line.
- Coordination reads are counted by `coord.py`, which re-reads the transcripts.
"""

import collections
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("c274", HERE.parent.parent / "274-leaner-research-sessions/measure/collect.py")
c274 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c274)

HOME = pathlib.Path.home()
CLONES_DIR = pathlib.Path("/diagram/.clones")
LANDED = "2026-09-28T03:43:49"  # 6555db77b, 274's last commit before its push (main merged it by 04:20, e6e507166)
R1_FROM = "2026-09-27T05:00"  # 274 R1: "every page session since feature 250 landed (2026-09-27 ~05:00 UTC)"
R1_CLONES = ["diagram-supplemental"] + [f"diagram-research-{i}" for i in range(1, 7)] + [f"diagram-shrines-{i}" for i in range(1, 4)] + ["diagram-buildings"]
CLONE_FEATURE = {"diagram-reorg": "292", "diagram-reorg-2": "292", "diagram-reorg-3": "292"}  # the sweep's briefs sat in a scratchpad


def classify(name):
    b = name[:-3] if name.endswith(".md") else name
    for suffix, kind in (("-write", "write"), ("-split", "split"), ("-finish", "finish")):
        if b.endswith(suffix):
            return kind, b[: -len(suffix)]
    m = re.match(r"(.+)-check(-[a-z])?$", b)
    if m:
        return "check", m.group(1)
    m = re.match(r"(.+)-(1|2[a-z])$", b)
    if m:
        return ("write" if m.group(2) == "1" else "check"), m.group(1)
    return "other", b


def handoff_counts(brief_dir, grp):
    p = brief_dir / f"{grp}-handoff.md"
    try:
        t = p.read_text(encoding="utf-8")
    except OSError:
        return None
    # Since feature 303 a handoff names a question once per heading it touched (`- SECTION=0053/<heading>` for the
    # question and again for its drawing page), so a question is its distinct NNNN; an older `page/NNN` line is one each.
    secs = {s.split("/")[0] if re.match(r"\d{4}/", s) else s for s in re.findall(r"^- SECTION=(\S+)", t, re.M)}
    return len(secs), len(set(re.findall(r"^- KEY=(\S+)", t, re.M)))



def continuations(root):
    parent = {}
    for log in (root / ".git/page-sessions").glob("run-*.log"):
        for line in log.read_text(errors="replace").splitlines():
            m = re.match(r"continued (\S+) -> (\S+)", line)
            if m:
                parent[m.group(2)] = m.group(1)
    return parent


def first_ts(tp):
    for line in open(tp, errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("timestamp"):
            return r["timestamp"]
    return ""


def session(clone, root, sid, brief, cont_parent, group_of):
    tp = HOME / f".claude/projects/-diagram--clones-{clone}/{sid}.jsonl"
    rs = [r for r in c274.recs(tp) if not r.get("isSidechain")]
    mm = c274.msgs(rs)
    if not mm:
        return None
    bp = pathlib.Path(brief)
    if not bp.is_absolute():
        bp = root / ("specs/" + brief if not brief.startswith("specs/") else brief)
    m = re.search(r"specs/(\d+)-", str(bp))
    feat = m.group(1) if m else CLONE_FEATURE.get(clone, "?")
    kind, grp = classify(bp.name)
    if sid in cont_parent and cont_parent[sid] in group_of:  # a continuation joins its parent's group
        kind, grp = "continuation", group_of[cont_parent[sid]]
    group_of[sid] = grp
    q, k, mb, _ = c274.parse_brief(bp)
    agents = []
    sub = tp.with_suffix("") / "subagents"
    for ap in sorted(sub.glob("agent-*.jsonl")) if sub.exists() else []:
        am = c274.msgs(list(c274.recs(ap)))
        if not am:
            continue
        try:
            meta = json.loads(ap.with_suffix("").with_suffix(".meta.json").read_text())
        except (OSError, ValueError):
            meta = {}
        agents.append({"type": meta.get("agentType", "unknown"), "tot": sum(x["tot"] for x in am), "turns": len(am)})
    return {
        "clone": clone, "sid": sid, "feature": feat, "group": f"{feat}:{clone}:{grp}", "grp": grp, "brief_dir": str(bp.parent),
        "kind": kind, "brief": bp.name, "q": q, "k": k, "m_brief": mb, "turns": len(mm), "tot": sum(x["tot"] for x in mm),
        "cr": sum(x["cr"] for x in mm), "out": sum(x["out"] for x in mm), "peak": max(x["ctx"] for x in mm),
        "start": mm[0]["ts"], "end": mm[-1]["ts"], "agents": agents,
    }


def main(which):
    sessions = []
    roots = [CLONES_DIR / c for c in R1_CLONES] if which == "r1" else sorted(p for p in CLONES_DIR.iterdir() if (p / ".git/page-sessions/index.txt").exists())
    for root in roots:
        clone = root.name
        cont_parent = continuations(root)
        group_of = {}
        seen = set()
        for line in (root / ".git/page-sessions/index.txt").read_text().splitlines():
            if not line.strip():
                continue
            sid, brief = line.split(maxsplit=1)
            if sid in seen:
                continue
            seen.add(sid)
            tp = HOME / f".claude/projects/-diagram--clones-{clone}/{sid}.jsonl"
            if not tp.exists():
                print("missing", clone, sid, file=sys.stderr)
                continue
            t0 = first_ts(tp)
            if (which == "post" and t0 < LANDED) or (which == "r1" and not R1_FROM <= t0 < LANDED):
                continue
            s = session(clone, root, sid, brief, cont_parent, group_of)
            if s:
                sessions.append(s)
    # things checked per group, from its handoff where there is one
    for s in sessions:
        hc = handoff_counts(pathlib.Path(s["brief_dir"]), s["grp"])
        s["handoff"] = list(hc) if hc else None
    (HERE / f"sessions-{which}.json").write_text(json.dumps(sessions))
    print(len(sessions), "sessions", len({s["group"] for s in sessions}), "groups")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "post")
