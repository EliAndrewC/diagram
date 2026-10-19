import sys
from playwright.sync_api import sync_playwright
pid, out = sys.argv[1], sys.argv[2]
komas = sys.argv[3:]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":2400,"height":1900}, device_scale_factor=1)
    for k in komas:
        pg.goto(f"https://dl.ndl.go.jp/pid/{pid}/1/{k}", wait_until="networkidle", timeout=120000)
        pg.wait_for_timeout(6000)
        pg.screenshot(path=f"{out}/{pid}-k{k}.png")
        print("shot", k)
    b.close()
