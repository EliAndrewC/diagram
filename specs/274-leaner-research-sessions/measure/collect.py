#!/usr/bin/env python3
"""Collect per-session token facts for every page session since feature 250 landed. Writes sessions.json."""
import json, pathlib, re, sys, statistics, datetime, collections

HOME = pathlib.Path.home()
CLONES = ["diagram-supplemental"] + [f"diagram-research-{i}" for i in range(1, 7)] + [f"diagram-shrines-{i}" for i in range(1, 4)] + ["diagram-buildings"]
OUT = pathlib.Path(__file__).parent


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else 0.0


def recs(p):
    out = []
    with open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def msgs(rs):
    per = {}
    for r in rs:
        if r.get("type") != "assistant":
            continue
        m = r.get("message") or {}
        u = m.get("usage")
        if not isinstance(u, dict) or not m.get("id"):
            continue
        cc = u.get("cache_creation") or {}
        row = per.setdefault(m["id"], {"ts": r.get("timestamp") or "", "model": m.get("model"), "inp": 0, "cc": 0, "cc1h": 0, "cr": 0, "out": 0})
        row["inp"] = max(row["inp"], u.get("input_tokens") or 0)
        row["cc"] = max(row["cc"], u.get("cache_creation_input_tokens") or 0)
        row["cc1h"] = max(row["cc1h"], cc.get("ephemeral_1h_input_tokens") or 0)
        row["cr"] = max(row["cr"], u.get("cache_read_input_tokens") or 0)
        row["out"] = max(row["out"], u.get("output_tokens") or 0)
    rows = sorted(per.values(), key=lambda x: x["ts"])
    for x in rows:
        x["ctx"] = x["inp"] + x["cc"] + x["cr"]
        x["tot"] = x["ctx"] + x["out"]
    return rows


def tools(rs):
    """list of (index_of_result_record, name, key, chars, input) for tool results in order"""
    asked = {}
    out = []
    for i, r in enumerate(rs):
        c = (r.get("message") or {}).get("content")
        for b in c if isinstance(c, list) else []:
            if b.get("type") == "tool_use":
                asked[b.get("id")] = (b.get("name"), b.get("input") or {}, r.get("timestamp") or "")
            elif b.get("type") == "tool_result":
                body = b.get("content")
                text = body if isinstance(body, str) else "".join(str(p.get("text", "")) for p in body or [] if isinstance(p, dict))
                name, inp, t0 = asked.get(b.get("tool_use_id"), ("?", {}, ""))
                out.append({"ts": r.get("timestamp") or t0, "name": name, "inp": inp, "chars": len(text), "text_head": text[:200]})
    return out, asked


def cmdkey(name, inp):
    if name == "Bash":
        c = " ".join(str(inp.get("command", "")).split())
        for pat, k in [(r"make record\b.*citations", "make record && citations"), (r"test-file", "make test-file"), (r"apply-edits", "make apply-edits"),
                       (r"check-bundle", "make check-bundle"), (r"make notes", "make notes"), (r"source-pages", "make source-pages"),
                       (r"make canon", "make canon"), (r"make record", "make record"), (r"_entry_owed", "_entry_owed.py"), (r"make glossary", "make glossary"),
                       (r"git (-C \S+ )?(commit|add)", "git commit/add"), (r"git ", "git other"), (r"make reserve", "make reserve"), (r"quote-verbatim", "make quote-verbatim"),
                       (r"grep", "grep"), (r"sed -n|cat |head|tail", "sed/cat/head")]:
            if re.search(pat, c):
                return k
        return "bash:" + c[:40]
    if name == "Read":
        return "Read"
    return name


def parse_brief(path):
    q = k = m = 0
    try:
        t = path.read_text(encoding="utf-8")
    except OSError:
        return 0, 0, 0, 0
    for line in t.splitlines():
        if line.startswith("**Your questions"):
            q = len(re.findall(r"SECTION=", line))
        elif line.startswith("**Your registry keys"):
            rest = line.split(":**", 1)[-1]
            k = 0 if "none" in rest.split("-")[0] else len([x for x in re.split(r",", rest) if x.strip()])
        elif line.startswith("**Your modals") or line.startswith("**Your pairs"):
            m = len(re.findall(r"KIND=", line))
    return q, k, m, len(t)


def classify(base):
    b = base[:-3]
    if b.startswith("split-"):
        return "split", "250:split"
    if b.startswith("owed-"):
        return "owed", "250:owed-" + re.sub(r"-\d+$", "", b[5:])
    m = re.match(r"(.+)-(write|finish|check-[a-z])$", b)
    if m:
        return ("write" if m.group(2) == "write" else "finish" if m.group(2) == "finish" else "check"), m.group(1)
    m = re.match(r"(.+)-(1|2[a-z])$", b)
    if m:
        return ("write" if m.group(2) == "1" else "check"), m.group(1)
    return "other", b


def main():
    sessions = []
    seen = set()
    for c in CLONES:
        root = pathlib.Path("/diagram/.clones") / c
        idx = root / ".git/page-sessions/index.txt"
        lines = [l.split() for l in idx.read_text().splitlines() if l.strip()]
        launches = collections.Counter(sid for sid, _ in lines)
        for sid, brief in lines:
            if (c, sid) in seen:
                continue
            seen.add((c, sid))
            bp = pathlib.Path(brief)
            if not bp.is_absolute():
                bp = root / ("specs/" + brief if not brief.startswith("specs/") else brief)
            feat = re.search(r"specs/(\d+)-", str(bp)).group(1)
            kind, grp = classify(bp.name)
            q, k, m, blen = parse_brief(bp)
            tp = HOME / f".claude/projects/-diagram--clones-{c}/{sid}.jsonl"
            if not tp.exists():
                print("missing", c, sid, file=sys.stderr)
                continue
            rs = recs(tp)
            main_rs = [r for r in rs if not r.get("isSidechain")]
            mm = msgs(main_rs)
            if not mm:
                continue
            tr, asked = tools(main_rs)
            # carry: chars/4 * later main turns
            tss = [x["ts"] for x in mm]
            import bisect
            for t in tr:
                t["later"] = len(tss) - bisect.bisect_right(tss, t["ts"])
                t["carry"] = t["chars"] // 4 * t["later"]
                t["key"] = cmdkey(t["name"], t["inp"])
            reads = collections.Counter(str(t["inp"].get("file_path")) for t in tr if t["name"] == "Read")
            dup_reads = {p: n for p, n in reads.items() if n > 1}
            dup_read_chars = sum(t["chars"] for t in tr if t["name"] == "Read" and str(t["inp"].get("file_path")) in dup_reads) - sum(
                min(t["chars"] for t in tr if t["name"] == "Read" and str(t["inp"].get("file_path")) == p) for p in dup_reads)
            # gaps/resumes
            gaps = []
            for a, b in zip(mm, mm[1:]):
                g = ts(b["ts"]) - ts(a["ts"])
                if g > 3600:
                    gaps.append({"gap_s": g, "cc": b["cc"] + b["inp"], "cr": b["cr"], "ctx": b["ctx"], "prev_ctx": a["ctx"]})
            # attachments (hook messages etc.)
            att = collections.Counter()
            for r in main_rs:
                if r.get("type") == "attachment":
                    a = r.get("attachment") or {}
                    att[a.get("type")] += len(json.dumps(a))
            # commands of interest
            urls, bkeys = [], []
            for _id, (name, inp, _t) in asked.items():
                if name == "Bash":
                    cmd = str(inp.get("command", ""))
                    urls += re.findall(r"URL=[\"']?([^\s\"']+)", cmd)
                    if "check-bundle" in cmd:
                        bkeys += re.findall(r"KEY=([\w\-.]+)", cmd)
            # agents
            agents = []
            sub = tp.with_suffix("") / "subagents"
            for ap in sorted(sub.glob("agent-*.jsonl")) if sub.exists() else []:
                ars = recs(ap)
                am = msgs(ars)
                if not am:
                    continue
                try:
                    meta = json.loads(ap.with_suffix("").with_suffix(".meta.json").read_text())
                except (OSError, ValueError):
                    meta = {}
                atr, aasked = tools(ars)
                aurls = []
                for _id, (name, inp, _t) in aasked.items():
                    if name in ("WebFetch",):
                        aurls.append(str(inp.get("url")))
                    if name == "Bash":
                        aurls += re.findall(r"URL=[\"']?([^\s\"']+)", str(inp.get("command", "")))
                areads = [str(t["inp"].get("file_path")) for t in atr if t["name"] == "Read"]
                agents.append({"type": meta.get("agentType", "unknown"), "desc": meta.get("description", ""), "model": am[0]["model"],
                               "start": am[0]["ts"], "turns": len(am), "inp": sum(x["inp"] for x in am), "cc": sum(x["cc"] for x in am),
                               "cc1h": sum(x["cc1h"] for x in am), "cr": sum(x["cr"] for x in am), "out": sum(x["out"] for x in am),
                               "tot": sum(x["tot"] for x in am), "first": am[0]["ctx"], "peak": max(x["ctx"] for x in am),
                               "read_chars": sum(t["chars"] for t in atr), "urls": aurls, "reads": areads,
                               "big": sorted(((t["chars"], cmdkey(t["name"], t["inp"]) + " " + str(t["inp"].get("file_path") or t["inp"].get("url") or "")[-70:]) for t in atr), reverse=True)[:3]})
            agg = collections.defaultdict(lambda: [0, 0, 0])
            for t in tr:
                a = agg[t["key"]]
                a[0] += 1; a[1] += t["chars"]; a[2] += t["carry"]
            sessions.append({
                "clone": c, "sid": sid, "feature": feat, "group": f"{feat}:{c}:{grp}" if not grp.startswith("250:") else f"250:{c}:{grp[4:]}",
                "kind": kind, "brief": bp.name, "brief_chars": blen, "launches": launches[sid], "q": q, "k": k, "m_brief": m,
                "turns": len(mm), "inp": sum(x["inp"] for x in mm), "cc": sum(x["cc"] for x in mm), "cc1h": sum(x["cc1h"] for x in mm),
                "cr": sum(x["cr"] for x in mm), "out": sum(x["out"] for x in mm), "tot": sum(x["tot"] for x in mm),
                "peak": max(x["ctx"] for x in mm), "first_ctx": mm[0]["ctx"], "first_tot": mm[0]["tot"], "median_ctx": statistics.median(x["ctx"] for x in mm),
                "start": mm[0]["ts"], "end": mm[-1]["ts"], "models": dict(collections.Counter(x["model"] for x in mm)),
                "gaps": gaps, "att": dict(att), "urls": urls, "bundle_keys": bkeys, "dup_reads": dup_reads, "dup_read_chars": dup_read_chars,
                "tool_agg": {k: v for k, v in agg.items()},
                "top_carry": sorted(((t["carry"], t["chars"], t["key"] + " " + " ".join(str(t["inp"].get("command") or t["inp"].get("file_path") or "").split())[:90]) for t in tr), reverse=True)[:5],
                "turn_ctx": [x["ctx"] for x in mm], "turn_cc": [x["cc"] + x["inp"] for x in mm],
                "agents": agents,
            })
    (OUT / "sessions.json").write_text(json.dumps(sessions))
    print(len(sessions), "sessions")


main()
