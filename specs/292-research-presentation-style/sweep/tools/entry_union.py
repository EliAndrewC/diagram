"""Union the Entry: lines of a conflict per page (both sides swept the same page): titles of both, ours first."""
import re, sys
BLOCK = re.compile(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n", re.S)
def segs(line):
    body = line.split("Entry:", 1)[1].strip().rstrip('",')
    return [s.strip() for s in re.split(r";\s*(?=research/)", body) if s.strip()]
def titles(seg):
    page, _, rest = seg.partition(" - ")
    return page.strip(), re.findall(r"""'(?:[^'\\]|\\.|'(?=[a-z]))*'|"[^"]*\"""", rest)
def merge(a, b):
    la = [x for x in a.splitlines() if "Entry:" in x]; lb = [x for x in b.splitlines() if "Entry:" in x]
    if len(la) != 1 or len(lb) != 1: return None
    order, got = [], {}
    for seg in segs(la[0]) + segs(lb[0]):
        page, ts = titles(seg)
        if page not in got: order.append(page); got[page] = []
        for t in ts:
            if t not in got[page]: got[page].append(t)
    prefix = la[0].split("Entry:")[0]
    tail = '",' if la[0].rstrip().endswith('",') else ""
    return prefix + "Entry: " + "; ".join(f"{p} - " + ", ".join(got[p]) for p in order) + tail + "\n"
for path in sys.argv[1:]:
    t = open(path).read(); left = 0
    def one(m):
        global left
        r = merge(m.group(1), m.group(2))
        if r is None: left += 1; return m.group(0)
        return r
    t = BLOCK.sub(one, t); open(path, "w").write(t); print(("LEFT %d " % left if left else "ok ") + path)
