#!/usr/bin/env python3
import json, pathlib, re, collections, statistics, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
OUT = pathlib.Path(__file__).parent
E = json.load(open(OUT / "events.json"))
S = json.load(open(OUT / "sessions.json"))
R = pathlib.Path("/diagram/.claude/skills/diagram/research")

import importlib.util
spec = importlib.util.spec_from_file_location("x", OUT / "extract_norm.py")
xm = importlib.util.module_from_spec(spec); spec.loader.exec_module(xm)
norm = xm.norm

URLRE = re.compile(r"https?://[^\s\"'<>|\\)]+")
reg, notes = set(), set()
ROOTS = [R] + sorted(pathlib.Path("/diagram/.clones").glob("*/.claude/skills/diagram/research"))
for f in [f for RR in ROOTS for f in (RR / "sources").rglob("*.html")]:
    for u in URLRE.findall(f.read_text(errors="replace")):
        reg.add(norm(u.replace("&amp;", "&")))
for f in [f for RR in ROOTS for f in RR.rglob("*.notes.html")]:
    for u in URLRE.findall(f.read_text(errors="replace")):
        notes.add(norm(u.replace("&amp;", "&")))
anyr = set()
for f in R.rglob("*.html"):
    for u in URLRE.findall(f.read_text(errors="replace")):
        anyr.add(norm(u.replace("&amp;", "&")))
cited = reg | notes
questions = [f for f in R.glob("*/[0-9][0-9][0-9]-*.html") if not f.name.endswith(".notes.html") and f.parent.name not in ("sources", "citations", "archetypes")]
regfiles = list((R / "sources").rglob("[0-9][0-9][0-9][0-9]-*.html"))

SEARCHHOST = re.compile(r"^(search\.yahoo|bing\.com|google\.[a-z.]+/search|duckduckgo|html\.duckduckgo|yandex)")
BAD = re.compile(r"^(localhost|127\.0\.0\.1|file:|github\.com/eliandrewc|raw\.githubusercontent|api\.|obsidianportal)")
src = [e for e in E if e["kind"] != "search" and not e["url"].startswith("FILE:") and e["url"] and not SEARCHHOST.match(e["url"]) and not BAD.match(e["url"])]
srch = [e for e in E if e["kind"] == "search"] + [e for e in E if SEARCHHOST.match(e["url"] or "")]
for e in src:
    e["tok"] = e["chars"] // 4
    e["carry"] = e["tok"] * max(e.get("later", 0), 1)
by = collections.defaultdict(list)
for e in src:
    by[e["url"]].append(e)
for v in by.values():
    v.sort(key=lambda e: e["ts"])

def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

VERIFY = {"quote-check", "source-applicability", "source-reader"}
cls = collections.Counter(); clstok = collections.Counter(); clscarry = collections.Counter()
gaps = []
unc_multi_session = []
for u, v in by.items():
    for i, e in enumerate(v):
        if i == 0:
            continue
        prev = v[:i]
        if any(p["session"] == e["session"] for p in prev):
            if any(p["session"] == e["session"] and p["agent"] == e["agent"] for p in prev):
                c = "same agent (session)"
            else:
                c = "same session, other agent"
        elif any(p["feature"] == e["feature"] for p in prev):
            c = "other session, same feature"
        else:
            c = "other feature"
        c2 = ("cited" if u in cited else "uncited")
        e["cls"] = c
        cls[(c, c2)] += 1; clstok[(c, c2)] += e["tok"]; clscarry[(c, c2)] += e["carry"]
        gaps.append((ts(e["ts"]) - ts(v[i - 1]["ts"])) / 3600)
    ns = len({e["session"] for e in v})
    if ns >= 2 and u not in cited:
        unc_multi_session.append((ns, len(v), u))

res = {}
res["events_src"] = len(src); res["distinct_src"] = len(by); res["searches"] = len(srch)
res["distinct_queries"] = len({e["url"] for e in srch})
res["by_kind"] = collections.Counter(e["kind"] for e in src)
dist = collections.Counter(min(len(v), 10) for v in by.values())
res["reads_per_source"] = dict(sorted(dist.items()))
res["cited_distinct"] = sum(1 for u in by if u in cited)
res["cited_in_registry_distinct"] = sum(1 for u in by if u in reg)
res["registry_urls"] = len(reg); res["notes_urls"] = len(notes); res["registry_files"] = len(regfiles); res["questions"] = len(questions)
res["classes"] = {f"{a} / {b}": [cls[(a, b)], clstok[(a, b)], clscarry[(a, b)]] for (a, b) in sorted(cls)}
res["gap_hours_median"] = statistics.median(gaps) if gaps else 0
res["gap_hist"] = collections.Counter("<1h" if g < 1 else "1-6h" if g < 6 else "6-24h" if g < 24 else ">1d" for g in gaps)
res["uncited_multi_session"] = len(unc_multi_session)
res["uncited_multi_feature"] = sum(1 for u, v in by.items() if u not in cited and len({e["feature"] for e in v}) >= 2)
res["uncited_multi_session_reads"] = sum(n for _, n, _ in unc_multi_session)
tot_tok = sum(e["tok"] for e in src); tot_carry = sum(e["carry"] for e in src)
res["tok_all_reads"] = tot_tok; res["carry_all_reads"] = tot_carry
# read-once-reuse saving: every repeat that is NOT a within-agent re-read and NOT a verifier re-reading a cited source
def saveable(e):
    return e.get("cls") and not (e["atype"] in VERIFY and e["url"] in cited)
res["save_tok_cross_session"] = sum(e["tok"] for e in src if e.get("cls") in ("other session, same feature", "other feature"))
res["save_carry_cross_session"] = sum(e["carry"] for e in src if e.get("cls") in ("other session, same feature", "other feature"))
res["save_carry_cross_session_discovery"] = sum(e["carry"] for e in src if e.get("cls") in ("other session, same feature", "other feature") and saveable(e))
res["save_carry_all_repeats"] = sum(e["carry"] for e in src if e.get("cls"))
res["save_carry_uncited_cross_session"] = sum(e["carry"] for e in src if e.get("cls") in ("other session, same feature", "other feature") and e["url"] not in cited)
# searches repeated
qc = collections.Counter(e["url"] for e in srch)
res["repeated_queries"] = sum(n - 1 for n in qc.values() if n > 1)
# top 10
top = sorted(by.items(), key=lambda kv: (-len({e["session"] for e in kv[1]}), -len(kv[1])))[:15]
tops = []
for u, v in top:
    tops.append({"url": u, "reads": len(v), "sessions": len({e["session"] for e in v}), "features": dict(collections.Counter(e["feature"] for e in v)),
                 "atypes": dict(collections.Counter(e["atype"] for e in v)), "cited": u in cited, "in_registry": u in reg, "carry": sum(e["carry"] for e in v),
                 "whys": list(dict.fromkeys(e["why"][:160] for e in v if e["kind"] == "fetch" and e["why"]))[:6]})
res["top"] = tops
res["unc_multi_session_top"] = sorted(unc_multi_session, reverse=True)[:25]
# spend of sessions with >= 1 source read
(OUT / "result.json").write_text(json.dumps(res, indent=1, default=str))
(OUT / "per_url.json").write_text(json.dumps({u: [{k: e[k] for k in ("ts", "session", "agent", "atype", "feature", "kind", "tok", "carry", "why") if k in e} | {"cls": e.get("cls")} for e in v] for u, v in by.items()}, indent=0))
print(json.dumps({k: v for k, v in res.items() if k not in ("top", "unc_multi_session_top")}, indent=1, default=str))
