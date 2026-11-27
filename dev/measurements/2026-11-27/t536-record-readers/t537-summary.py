"""t537: the T536 reader runs summed per record - plan-done (the flat file or its parts), tasks-done (likewise), the archive's
index and note, plan-review.json - with the files read and the wall median; argv: before.txt after.txt."""
import re, sys
def read(p):
    out, case = {}, None
    for l in open(p):
        if l.startswith("## "):
            name, _, rest = l[3:].partition("\texit")
            case = name.strip(); out[case] = {"wall": re.search(r"wall median (\d+) ms", l)[1]}
            continue
        m = re.match(r"\s+specs/451/(\S+)\t([\d,]+) bytes\t(\d+) read calls", l)
        if not (m and case):
            continue
        f, b = m[1], int(m[2].replace(",", ""))
        k = ("plan-done" if "plan-done" in f else "tasks-done" if "tasks-done" in f else
             "index+note" if f.startswith("archive/") else "plan-review" if f == "plan-review.json" else None)
        if k:
            a = out[case].setdefault(k, [0, 0]); a[0] += b; a[1] += 1
    return out
b, a = read(sys.argv[1]), read(sys.argv[2])
print("| case | plan-done.md: before / after (files) | tasks-done.md: before / after (files) | index.json + INDEX.md after | plan-review.json (unsplit) | wall ms before / after |")
print("|---|---|---|---|---|---|")
def cell(x, k):
    v = x.get(k)
    return f"{v[0]:,} ({v[1]})" if v else "0"
for case in b:
    x, y = b[case], a.get(case, {})
    print(f"| {case} | {cell(x,'plan-done')} / {cell(y,'plan-done')} | {cell(x,'tasks-done')} / {cell(y,'tasks-done')} | {cell(y,'index+note')} | {cell(y,'plan-review')} | {x['wall']} / {y.get('wall','-')} |")
