import sys, json
from playwright.sync_api import sync_playwright
pid, bid, out = sys.argv[1], sys.argv[2], sys.argv[3]
kws = sys.argv[4:]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(f"https://dl.ndl.go.jp/pid/{pid}/1/1", wait_until="networkidle", timeout=90000)
    for kw in kws:
        body = {"keyword": kw, "keywords": [kw], "targets": [{"pid": pid, "bids": [bid]}]}
        r = pg.evaluate("""async (body) => { const r = await fetch('/api/fulltext/search', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}); return await r.text(); }""", body)
        res[kw] = r
    b.close()
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
for k, v in res.items(): print(k, len(v), v[:300])
