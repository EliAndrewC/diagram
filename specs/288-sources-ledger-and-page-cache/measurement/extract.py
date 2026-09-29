#!/usr/bin/env python3
"""Extract every source-read event from research transcripts since 2026-09-26. Writes events.json."""
import json, pathlib, re, collections, urllib.parse, datetime

HOME = pathlib.Path.home()
OUT = pathlib.Path(__file__).parent
SINCE = "2026-09-26"
PROJ = sorted(p for p in (HOME / ".claude/projects").glob("-diagram*") if p.is_dir())

# page-session index -> feature
IDX = {}
for idx in pathlib.Path("/diagram/.clones").glob("*/.git/page-sessions/index.txt"):
    for l in idx.read_text().splitlines():
        sp = l.split()
        if len(sp) == 2:
            m = re.search(r"specs/(\d+)-", sp[1])
            if m:
                IDX[sp[0]] = (m.group(1), pathlib.Path(sp[1]).name)

# l7r-check manifests: dir -> {file stem: url}
MAN = {}
for mf in pathlib.Path("/tmp/l7r-check").rglob("MANIFEST.txt"):
    d = {}
    for l in mf.read_text(errors="replace").splitlines()[1:]:
        sp = [x.strip() for x in l.split("|")]
        if len(sp) >= 2 and sp[0].startswith("http"):
            d[sp[1].split(".txt")[0]] = sp[0]
    MAN[str(mf.parent)] = d


def norm(u):
    u = u.strip().strip("'\"<>),.;")
    u = urllib.parse.unquote(u)
    u = u.split("#")[0]
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"^([a-z]{2,3})\.m\.wikipedia", r"\1.wikipedia", u)
    u = re.sub(r"^m\.", "", u)
    u = u.rstrip("/")
    return u.lower() if "wikipedia" not in u else u[: u.find("/")].lower() + u[u.find("/"):] if "/" in u else u.lower()


def recs(p):
    out = []
    with open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def text_of(body):
    return body if isinstance(body, str) else "".join(str(p.get("text", "")) for p in body or [] if isinstance(p, dict))


URLRE = re.compile(r"https?://[^\s\"'<>|\\)]+")


TOT = collections.Counter()


def events_for(rs, session, agent, atype):
    import bisect
    per = {}
    for r in rs:
        m = r.get("message") or {}
        u = m.get("usage")
        if r.get("type") == "assistant" and isinstance(u, dict) and m.get("id") and (r.get("timestamp") or "") >= SINCE:
            tot = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("output_tokens") or 0)
            per[m["id"]] = (r.get("timestamp") or "", max(tot, per.get(m["id"], ("", 0))[1]))
    tss = sorted(v[0] for v in per.values())
    TOT[atype] += sum(v[1] for v in per.values())
    TOT["_all"] += sum(v[1] for v in per.values())
    asked, ev, last_text = {}, [], ""
    for r in rs:
        tsv = r.get("timestamp") or ""
        c = (r.get("message") or {}).get("content")
        if isinstance(c, str):
            if r.get("type") == "user":
                last_text = c[:600]
            continue
        for b in c if isinstance(c, list) else []:
            t = b.get("type")
            if t == "text" and r.get("type") == "assistant":
                last_text = b.get("text", "")[-600:]
            elif t == "tool_use":
                asked[b.get("id")] = (b.get("name"), b.get("input") or {}, tsv, last_text)
            elif t == "tool_result":
                name, inp, t0, ctx = asked.get(b.get("tool_use_id"), ("?", {}, "", ""))
                chars = len(text_of(b.get("content")))
                ts = t0 or tsv
                if ts < SINCE:
                    continue
                later = len(tss) - bisect.bisect_right(tss, ts)
                base = {"later": later, "ts": ts, "session": session, "agent": agent, "atype": atype, "chars": chars, "ctx": ctx[-300:]}
                if name == "WebFetch":
                    ev.append(dict(base, kind="fetch", url=norm(str(inp.get("url", ""))), raw=str(inp.get("url", "")), why=str(inp.get("prompt", ""))[:300]))
                elif name == "WebSearch":
                    ev.append(dict(base, kind="search", url="Q:" + str(inp.get("query", "")).strip().lower(), raw=str(inp.get("query", "")), why=""))
                elif name == "Bash":
                    cmd = str(inp.get("command", ""))
                    us = []
                    if "source-pages" in cmd:
                        for m in re.finditer(r"URLS?=(\"[^\"]*\"|'[^']*'|\S+)", cmd):
                            us += URLRE.findall(m.group(1))
                        k = "source-pages"
                    elif re.search(r"\b(curl|wget)\b", cmd):
                        us = URLRE.findall(cmd)
                        k = "curl"
                    else:
                        us, k = [], None
                    for u in us:
                        ev.append(dict(base, kind=k, url=norm(u), raw=u, chars=chars // max(1, len(us)), why=cmd[:200]))
                elif name == "Read":
                    fp = str(inp.get("file_path", ""))
                    m = re.match(r"(/tmp/l7r-check/.+)/(\d\d-[^/]+?)\.txt", fp)
                    if m:
                        u = MAN.get(m.group(1), {}).get(m.group(2))
                        ev.append(dict(base, kind="saved-read", url=norm(u) if u else "FILE:" + fp, raw=fp, why=""))
    return ev


def session_feature(rs):
    c = collections.Counter()
    for r in rs:
        s = json.dumps((r.get("message") or {}).get("content", ""))
        for m in re.findall(r"specs/(2[5-9]\d)-", s):
            c[m] += 1
        for m in re.findall(r"SPECIFY_FEATURE=[\"']?(2[5-9]\d)-", s):
            c[m] += 5
    return c.most_common(1)[0][0] if c else "?"


allev, sessions = [], {}
for proj in PROJ:
    clone = proj.name.replace("-diagram--clones-", "") if "clones" in proj.name else "MIRROR"
    for tp in proj.glob("*.jsonl"):
        rs = recs(tp)
        if not rs or max((r.get("timestamp") or "") for r in rs) < SINCE:
            continue
        sid = tp.stem
        feat, brief = IDX.get(sid, (None, None))
        if not feat:
            feat = session_feature(rs)
        sessions[sid] = {"clone": clone, "feature": feat, "brief": brief}
        main = [r for r in rs if not r.get("isSidechain")]
        allev += [dict(e, clone=clone, feature=feat) for e in events_for(main, sid, "main", "main")]
        side = [r for r in rs if r.get("isSidechain")]
        if side:
            allev += [dict(e, clone=clone, feature=feat) for e in events_for(side, sid, "sidechain", "sidechain")]
        sub = tp.with_suffix("") / "subagents"
        for ap in sorted(sub.glob("agent-*.jsonl")) if sub.exists() else []:
            try:
                meta = json.loads(ap.with_suffix("").with_suffix(".meta.json").read_text())
            except (OSError, ValueError):
                meta = {}
            allev += [dict(e, clone=clone, feature=feat) for e in events_for(recs(ap), sid, ap.stem, meta.get("agentType", "adhoc"))]

(OUT / "events.json").write_text(json.dumps(allev))
(OUT / "tot.json").write_text(json.dumps(TOT))
(OUT / "sessions.json").write_text(json.dumps(sessions))
print(len(allev), "events", len(sessions), "sessions", collections.Counter(e["kind"] for e in allev))
