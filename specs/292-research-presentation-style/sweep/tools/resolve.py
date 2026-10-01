"""Resolve sweep merge conflicts (feature 292): Entry lines by page owner, links by page owner, glossary variants by union.

    resolve.py <ours-pages> <file> ...    ours-pages: comma-separated page prefixes whose sweep was done on OUR side;
                                          every other page's text is taken from THEIRS.
A conflict block it cannot resolve mechanically is left in place and reported.
"""
import json
import re
import sys

BLOCK = re.compile(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n", re.S)
OURS = tuple(sys.argv[1].split(","))


def owner_is_ours(page: str) -> bool:
    page = page.removeprefix("research/").removeprefix("rendering/").removeprefix("../")
    return page.startswith(OURS)


def entry_segments(line: str) -> list[str]:
    body = line.split("Entry:", 1)[1].strip()
    return [s.strip() for s in re.split(r";\s*(?=research/)", body) if s.strip()]


def seg_page(seg: str) -> str:
    return seg.split(" - ", 1)[0].strip()


def merge_entry(a: str, b: str) -> str | None:
    la = [x for x in a.splitlines() if "Entry:" in x]
    lb = [x for x in b.splitlines() if "Entry:" in x]
    if len(la) != 1 or len(lb) != 1 or a.strip().count("\n") != 0 or b.strip().count("\n") != 0:
        return None
    prefix = la[0].split("Entry:")[0]
    sa, sb = entry_segments(la[0]), entry_segments(lb[0])
    out, seen = [], set()
    for seg in sa + sb:
        page = seg_page(seg)
        if page in seen:
            continue
        src = sa if owner_is_ours(page) else sb
        pick = next((s for s in src if seg_page(s) == page), None)
        if pick is None:  # the owner side has no segment for this page: the page was folded away there
            continue
        seen.add(page)
        out.append(pick)
    return prefix + "Entry: " + "; ".join(out) + "\n"


LINK = re.compile(r'<a href="([^"]*)">(.*?)</a>', re.S)


def merge_links(a: str, b: str) -> str | None:
    la, lb = LINK.findall(a), LINK.findall(b)
    if len(la) != len(lb):
        return None
    out = a
    for (ha, ta), (hb, tb) in zip(la, lb):
        if ha != hb and not owner_is_ours(hb.split("#")[0]):
            out = out.replace(f'<a href="{ha}">{ta}</a>', f'<a href="{hb}">{tb}</a>', 1)
    return out


def merge_variants(a: str, b: str) -> str | None:
    items = []
    for x in (a + "\n" + b).splitlines():
        x = x.strip().rstrip(",")
        if x and x not in items:
            items.append(x)
    if not all(x.startswith('"') for x in items):
        return None
    return ",\n".join("  " + x for x in items) + "\n"


def resolve(path: str) -> int:
    t = open(path, encoding="utf-8").read()
    left = 0

    def one(m: re.Match) -> str:
        nonlocal left
        a, b = m.group(1), m.group(2)
        for fn in (merge_entry, merge_variants, merge_links):
            r = fn(a, b)
            if r is not None:
                return r
        left += 1
        return m.group(0)

    t = BLOCK.sub(one, t)
    open(path, "w", encoding="utf-8").write(t)
    if path.endswith(".json") and not left:
        json.loads(t)
    return left


for p in sys.argv[2:]:
    n = resolve(p)
    print(("LEFT %d " % n if n else "ok ") + p)
