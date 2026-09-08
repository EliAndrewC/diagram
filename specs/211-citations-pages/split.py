"""The one-time split (feature 211, T04): every research page's footnotes move to its citations page.

Run once from the skill root against `research/`; recorded here (spec-kit's externalized memory), never re-run. For
each research page: cut `<section class="footnotes">...</section>`; write `citations/<rel>` with the record's head
(the assets by the citations page's own relative path), a heading and a link back, the works markers (`make
citations` fills them), and the notes with every relative link rebased one level down and the back link pointed
at the research page; re-point every `<sup class="fn">` reference at the citations page; put a short section
linking to the citations page where the footnotes were; add the derived script's tag before `record.js`.
"""

from __future__ import annotations

import os
import re
import sys

from l7r.diagram.interactive.citations import WORKS_CLOSE, WORKS_OPEN, citations_page, rel_to_research, research_pages, script_path
from l7r.diagram.interactive.sources import RESEARCH_DIR

_FOOT = re.compile(r'\n?<section class="footnotes">.*?</section>\n?', re.S)
_REF = re.compile(r'(<sup class="fn"><a (?:id="fnref-\d+" )?href=")#fn-(\d+)(")')
_TITLE = re.compile(r"<title>(.*?)</title>", re.S)
_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_HREF = re.compile(r'href="(?!https?://|mailto:|#)([^"]*)"')
_BACK = re.compile(r'<a class="fnback" href="#fnref-(\d+)">back</a>')


def split(page_rel: str, research_dir: str) -> None:
    path = os.path.join(research_dir, page_rel)
    with open(path, encoding="utf-8") as fh:
        page = fh.read()
    m = _FOOT.search(page)
    assert m, page_rel
    foot = m.group(0).strip()
    # CUT FIRST, then re-point: the first run re-pointed the references over the whole page and then sliced the
    # footnote section out at offsets measured before the substitution, which lengthened every reference - so the
    # cut landed short and left a tail of the notes in six pages. Measured by the record tests, restored from git,
    # re-run in this order.
    page = page[: m.start()] + "\n@@FOOT@@\n" + page[m.end() :]
    # a note may itself reference another note (vegetation fn 63, archetypes 68/69/77, buildings 63/69): that
    # reference and its back link stay in-page on the citations page
    in_foot = set(re.findall(r'id="(fnref-\d+)"', foot))
    crel = citations_page(page_rel)
    up = rel_to_research(crel)  # from the citations page to research/
    name = page_rel[:-5]
    title = _TITLE.search(page).group(1)
    h1 = _H1.search(page).group(1)
    # the notes: relative links rebased one level down (a citations page is one directory below its research page),
    # the back link pointed at the research page
    foot = _HREF.sub(lambda mm: f'href="../{mm.group(1)}"', foot)
    foot = _BACK.sub(lambda mm: f'<a class="fnback" href="{"" if f"fnref-{mm.group(1)}" in in_foot else up + page_rel}#fnref-{mm.group(1)}">back</a>', foot)
    citations = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>Citations: {title}</title>\n"
        f'<link rel="stylesheet" href="{up}assets/record.css">\n'
        f'<script src="{up}assets/glossary.js" defer></script>\n'
        f'<script src="{up}assets/record.js" defer></script>\n</head>\n<body>\n<main>\n'
        f'<h1 id="citations-{name.replace("/", "-")}">Citations: {h1}</h1>\n'
        f'<p><em>The passages behind the footnotes of <a href="{up}{page_rel}">{h1}</a> - first the works they quote and why each one counts, then the notes themselves. Hover a footnote number on that page and the note appears beside it; the numbers here are the same ones.</em></p>\n'
        '<section class="works">\n<h2 id="works-cited">The works cited on this page</h2>\n'
        f"{WORKS_OPEN}\n{WORKS_CLOSE}\n</section>\n"
        '<h2 id="notes">The notes</h2>\n'
        f"{foot}\n</main>\n</body>\n</html>\n"
    )
    cpath = os.path.join(research_dir, crel)
    os.makedirs(os.path.dirname(cpath), exist_ok=True)
    with open(cpath, "w", encoding="utf-8") as fh:
        fh.write(citations)
    # the research page: references re-pointed, the footnote section replaced, the script tag added
    down = "../" * page_rel.count("/")  # from the research page to research/
    href = f"{down}{crel}"
    page = _REF.sub(lambda mm: f"{mm.group(1)}{href}#fn-{mm.group(2)}{mm.group(3)}", page)
    link = f'\n<section class="citations"><p>The notes behind this page\'s footnotes - the passages quoted, and what each cited work is and why it counts - are on <a href="{href}">its citations page</a>.</p></section>\n'
    assert page.count("\n@@FOOT@@\n") == 1
    page = page.replace("\n@@FOOT@@\n", link)
    tag = f'<script src="{down}assets/record.js" defer></script>'
    assert tag in page, page_rel
    page = page.replace(tag, f'<script src="{down}{script_path(page_rel)}" defer></script>\n{tag}', 1)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"{page_rel}: notes -> {crel}, script {script_path(page_rel)}")


if __name__ == "__main__":
    for rel in research_pages(RESEARCH_DIR):
        split(rel, RESEARCH_DIR)
    sys.exit(0)
