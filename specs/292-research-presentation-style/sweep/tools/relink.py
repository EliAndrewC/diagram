"""Re-aim links to anchors a fold retired (feature 292 sweep merge): old id -> the topic that absorbed it, from the handoffs.

    relink.py <skill dir> <handoff dir> ...     rewrites every fragment link whose anchor no assembled page holds and
                                                 whose old id a handoff maps; prints what it changed and what it could not
"""
import os
import pathlib
import re
import sys

skill = pathlib.Path(sys.argv[1])
R = skill / "research"

# old id -> (page, new id) from every handoff's SECTION= and OLD= lines
old2new: dict[str, tuple[str, str]] = {}
for hd in sys.argv[2:]:
    for h in pathlib.Path(hd).rglob("*-handoff.md"):
        cur = None
        for line in h.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*-\s*SECTION=\s*`?([^`\s]+)`?", line)
            if m:
                sec = m.group(1).removeprefix("research/")
                page, sid = sec.rsplit("/", 1)
                sid = re.sub(r"^\d{3}-", "", sid).removesuffix(".html")
                cur = (page, sid)
                continue
            m = re.match(r"\s*-\s*OLD=\s*(.*)", line)
            if m and cur:
                for p in re.split(r"[\s,]+", m.group(1).strip("` ")):
                    p = p.strip("`")
                    if p.endswith(".html"):
                        oid = re.sub(r"^\d{3}-", "", os.path.basename(p)).removesuffix(".html")
                        old2new.setdefault(oid, cur)

# every live id per assembled page
ids: dict[str, set[str]] = {}
for page in R.rglob("*.html"):
    rel = page.relative_to(R).as_posix()
    if rel.startswith(("citations/", "sources/", "assets/")) or re.search(r"/\d{3}-", rel) or "/_" in rel:
        continue
    ids[rel.removesuffix(".html")] = set(re.findall(r'\bid="([^"]+)"', page.read_text(encoding="utf-8")))

HREF = re.compile(r'href="((?:[^"#]*\.html)?)#([^"]+)"')
changed, unresolved = 0, []
for frag in R.rglob("[0-9][0-9][0-9]-*.html"):
    rel = frag.relative_to(R).as_posix()
    if rel.startswith(("citations/", "sources/")) or rel.endswith((".notes.html", ".originals.html")):
        continue
    here = pathlib.PurePosixPath(rel).parent  # e.g. towns, cities/fabric, rendering/towns
    # an assembled page sits one level above its fragment directory
    page_dir = here.parent
    text = frag.read_text(encoding="utf-8")

    def fix(m: re.Match) -> str:
        global changed
        target, anchor = m.group(1), m.group(2)
        tpage = os.path.normpath(os.path.join(page_dir.as_posix(), target)).removesuffix(".html") if target else here.as_posix()
        if anchor in ids.get(tpage, set()):
            return m.group(0)
        if anchor not in old2new:
            unresolved.append(f"{rel}: {target}#{anchor}")
            return m.group(0)
        npage, nid = old2new[anchor]
        newrel = os.path.relpath(npage + ".html", page_dir.as_posix() or ".")
        changed += 1
        return f'href="{newrel}#{nid}"'

    new = HREF.sub(fix, text)
    if new != text:
        frag.write_text(new, encoding="utf-8")
print(f"old ids mapped: {len(old2new)}; links re-aimed: {changed}; unresolved: {len(unresolved)}")
for u in unresolved:
    print("UNRESOLVED", u)
