#!/usr/bin/env python3
"""Feature 376 FR-005: do sessions look at what the project already has before searching the web?

Usage: local_first.py > local-first.txt

Reads every session transcript under ~/.claude/projects/-diagram*/ - each main thread and each subagent its own ACTOR -
for the tool calls made since the source archive landed (feature 309, 2026-10-02T17:37Z). For every actor that searched
or fetched from the web it asks:

1. FIRST CALL: was the actor's first web call preceded by a LOCAL look - the record (`research/` read or grepped,
   `make notes`, `make record-*`, a check bundle), the archive (`make archive-find`) or the GM's canon (`make canon`)?
   A subagent is dispatched with a bundle or a brief, so its prompt counts as a local look when it names a bundle or
   a research path.
2. HELD ALREADY: how many web fetches (WebFetch, `make source-pages URL=`) were of a URL the archive already held at
   that moment - an archive row (`research/archive/*/*.json`, `url` or `final_url`) captured before the call.
3. ASKED ALREADY: how many web searches were on a subject the record has a question for, judged by words - the query's
   content words (4+ letters, no stop words) against each question's heading id (`research/questions/NNNN-<id>.html`):
   at least two words and 60% of the query's inside one heading. A rough indicator, stated as one.
"""

from __future__ import annotations

import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
SINCE = "2026-10-02T17:37"
LOCAL = re.compile(r"MANIFEST\.md|/tmp/l7r-check|make\s+(archive-find|canon|notes|record-\w+|check-bundle|modal-bundle|claims-bundle|lines)\b|research/(questions|sources|CLAUDE)|\bgrep\b[^|;&]*research/")
STOP = set("with from that this what were which their they have been into about when where does than more most also over such them some there these those under used uses using what make made like".split())


def recs(path: pathlib.Path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def archive_rows() -> list[tuple[str, str]]:
    """(url, captured) for every archived capture, url and final url both."""
    out = []
    for f in (ROOT / "research" / "archive").glob("*/*.json"):
        try:
            d = json.loads(f.read_text())
        except ValueError:
            continue
        for row in d if isinstance(d, list) else [d]:
            for u in {row.get("url"), row.get("final_url")} - {None, ""}:
                out.append((norm_url(u), str(row.get("captured") or "")[:19]))
    return out


def norm_url(u: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", u.strip()).rstrip("/").split("#")[0]


def headings() -> list[set[str]]:
    out = []
    for f in (ROOT / "research" / "questions").glob("[0-9][0-9][0-9][0-9]-*.html"):
        if f.name.endswith((".notes.html", ".drawing.html")):
            continue
        out.append({w for w in f.stem.split("-")[1:] if len(w) >= 4 and w not in STOP})
    return out


def words(q: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", q.lower()) if w not in STOP}


def actors():
    """(name, records) for every main thread and subagent with a call since SINCE."""
    for p in sorted(pathlib.Path.home().glob(".claude/projects/-diagram*/*.jsonl")):
        main = [r for r in recs(p) if not r.get("isSidechain")]
        if any(str(r.get("timestamp", "")) >= SINCE for r in main):
            yield f"main:{p.parent.name}/{p.stem[:8]}", main, ""
        sub = p.with_suffix("") / "subagents"
        for ap in sorted(sub.glob("agent-*.jsonl")) if sub.exists() else []:
            rs = list(recs(ap))
            if any(str(r.get("timestamp", "")) >= SINCE for r in rs):
                first = next((r for r in rs if r.get("type") == "user"), {})
                try:
                    kind = json.loads(ap.with_suffix("").with_suffix(".meta.json").read_text()).get("agentType", "unknown")
                except (OSError, ValueError):
                    kind = "unknown"
                yield f"agent[{kind}]:{p.stem[:8]}/{ap.stem[-8:]}", rs, json.dumps((first.get("message") or {}).get("content"))[:4000]


def calls(rs):
    for r in rs:
        if r.get("type") != "assistant" or str(r.get("timestamp", "")) < SINCE:
            continue
        for b in (r.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                yield r.get("timestamp"), b.get("name"), b.get("input") or {}


def main() -> None:
    held = archive_rows()
    heads = headings()
    tally = collections.Counter()
    for name, rs, prompt in actors():
        kind = name.split(":")[0].split("[")[0]
        agent_type = name.split("[")[1].split("]")[0] if "[" in name else ""
        local = bool(prompt and LOCAL.search(prompt))
        first_web_done = False
        for ts, tool, inp in calls(rs):
            cmd = str(inp.get("command", "")) if tool == "Bash" else ""
            text = cmd or json.dumps(inp)
            web_fetch = tool == "WebFetch" or bool(re.search(r"make\s+source-pages\b", cmd))
            web_search = tool == "WebSearch"
            if not (web_fetch or web_search):
                if LOCAL.search(text) or (tool in ("Read", "Grep") and "research/" in text):
                    local = True
                continue
            if not first_web_done:
                first_web_done = True
                tally[f"{kind} actors searching the web"] += 1
                tally[f"{kind} actors whose first web call came after a local look"] += local
            if web_fetch:
                url = str(inp.get("url") or "") or (re.search(r"URL=[\"']?([^\s\"']+)", cmd) or [None, ""])[1]
                tally[f"{kind} web fetches"] += 1
                if agent_type:
                    tally[f"  by type: {agent_type} web fetches"] += 1
                if url and any(u == norm_url(url) and cap and cap < str(ts)[:19] for u, cap in held):
                    tally[f"{kind} web fetches of a URL the archive already held"] += 1
                    if agent_type:
                        tally[f"  by type: {agent_type} web fetches already held"] += 1
            if web_search:
                q = words(str(inp.get("query", "")))
                tally[f"{kind} web searches"] += 1
                if agent_type:
                    tally[f"  by type: {agent_type} web searches"] += 1
                if len(q) >= 2 and any(len(q & h) >= 2 and len(q & h) / len(q) >= 0.6 for h in heads):
                    tally[f"{kind} web searches on a subject a record question names"] += 1
    for k in sorted(tally):
        print(f"{tally[k]:6}  {k}")


main()
