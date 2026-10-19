import sys
from playwright.sync_api import sync_playwright
pid, k, out = sys.argv[1], sys.argv[2], sys.argv[3]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":2400,"height":1900}, device_scale_factor=2)
    pg.goto(f"https://dl.ndl.go.jp/pid/{pid}/1/{k}", wait_until="networkidle", timeout=120000)
    pg.wait_for_timeout(8000)
    # clips in CSS px (viewport 2400 wide): right page ~ x 1000-1740, left ~ 200-940; text y ~ 370-1510
    for name,(x,y,w,h) in {"R-top":(1010,380,730,580),"R-bot":(1000,930,730,580),"L-top":(220,380,730,580),"L-bot":(210,930,730,580)}.items():
        pg.screenshot(path=f"{out}/{pid}-k{k}-{name}.png", clip={"x":x,"y":y,"width":w,"height":h})
    b.close()
