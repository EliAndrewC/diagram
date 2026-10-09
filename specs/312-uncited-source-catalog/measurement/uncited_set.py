"""Feature 312: measure the uncited set - its size, the cache's coverage, the mechanical no-substance hits,
the ledger's outcomes on it, and the cited respellings. Run from the clone's root."""
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, "scripts")
import _archive as ar  # noqa: E402
import _archive_ops as ops  # noqa: E402
import _sources as src  # noqa: E402

root = pathlib.Path(".").resolve()
home = src.home(root)
urls = ops.consulted_urls(root)
rows = [json.loads(p.read_text()) for p in ar.row_files(root)]
nokey = [r for r in rows if not r.get("key") and not r.get("keys") and not r.get("note")]
SEARCH = re.compile(r"duckduckgo|google\.[a-z.]+/search|bing\.com/search|baidu\.com/s\?|search\?|/search/|advancedsearch|[?&](q|query|keyword|kw|wd)=|/results?\b")
API = re.compile(r"/api/|action=raw|output=json|\.json\b")
mech = [u for u in urls if SEARCH.search(u) or API.search(u)]
cached = [u for u in urls if src.cached(home, u, max_age_days=10_000)]
ledger = src.read(home)
out = collections.Counter()
for r in ledger:
    if r.get("url") in {src.norm(u) for u in urls[:0]}:
        pass
nset = {src.norm(u) for u in urls}
last = {}
for r in ledger:
    if r.get("url") in nset:
        last.setdefault(r["url"], []).append(r.get("outcome", ""))
for n, outs in last.items():
    for o in set(outs):
        out[o.split(":")[0]] += 1
cited_marked = sorted({r["url"] for r in ledger if r.get("outcome", "").startswith("cited:") and r["url"] in nset})
print(json.dumps({
    "uncited": len(urls), "manifest_rows": len(rows), "rows_without_key_or_note": len(nokey),
    "mechanical_no_substance": len(mech), "with_cached_text": len(cached),
    "ledger_outcomes_by_url": dict(out), "cited_marked_without_row": cited_marked,
}, indent=1, ensure_ascii=False))
pathlib.Path("/tmp/claude-1000/-diagram/5aabb62f-9a09-4e29-aa16-7521bfad43a6/scratchpad/uncited.txt").write_text("\n".join(urls))
