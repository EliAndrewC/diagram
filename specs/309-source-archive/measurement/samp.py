import sys, time, json
from playwright.sync_api import sync_playwright
out=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36", accept_downloads=True)
    for u in open("sample.txt").read().split():
        t=time.time(); pg=ctx.new_page(); row={"url":u}
        try:
            if u.lower().split("?")[0].endswith(".pdf"):
                r=ctx.request.get(u, timeout=60000); row.update(status=r.status, kb=len(r.body())//1024, kind="pdf")
            else:
                r=pg.goto(u, wait_until="load", timeout=45000)
                try: pg.wait_for_load_state("networkidle", timeout=10000)
                except Exception: pass
                snap=pg.context.new_cdp_session(pg).send("Page.captureSnapshot",{"format":"mhtml"})["data"]
                row.update(status=r.status if r else None, kb=len(snap)//1024, kind=(r.headers.get("content-type","") if r else ""))
        except Exception as e:
            row["err"]=str(e).splitlines()[0][:120]
        row["s"]=round(time.time()-t,1); out.append(row); print(json.dumps(row,ensure_ascii=False), flush=True)
        pg.close()
    b.close()
