#!/usr/bin/env python3
"""The sweep's briefs, generated from a page's topic plan (feature 292, plan D6-D7).

    make_briefs.py <page> [<date> [<clone>]]   reads sweep/plan-<page>.md, writes sweep/briefs/<page>-<G>-write.md and
                                       -check.md per group, and prints the queue for `make page-session`

WHY GENERATED. Every group of every page must get the same procedure - the one the three pilot topics ran - and a
hand-written brief per group would drift. The procedure is the two templates beside this file; the plan supplies only
what differs: each topic's title, the sections it folds, its rendering section, its modals and its note.

THE GROUPS are packed here, not taken from the planner: a write session takes at most four SECTIONS (feature 274's
cap, which counts every section a brief names), so topics are packed in plan order while their folded sections sum to
four or fewer, and a topic that folds more than four is a group by itself - the runner lets it through only under
`WRITE_CAP_OK` with the reason, logged (one topic cannot be split across sessions without splitting the merge).
"""

from __future__ import annotations

import datetime
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAP = 4


def topics(plan: str) -> list[dict]:
    """Each `## T<n> <title>` block of a plan, with its fold, rendering, modals and note."""
    out = []
    for m in re.finditer(r"^## (T\d+) (.+?)\n(.*?)(?=^## |\Z)", plan, re.S | re.M):
        body = m.group(3)

        def field(name: str) -> str:
            f = re.search(rf"^- {name}:\s*(.*)$", body, re.M)
            return f.group(1).strip() if f else ""

        fold = [s.strip().strip("`") for s in re.split(r",\s*", field("fold")) if s.strip()]
        out.append({"id": m.group(1), "title": m.group(2).strip(), "fold": fold, "rendering": field("rendering"),
                    "modals": field("modals"), "note": field("note")})
    return out


def groups(ts: list[dict]) -> list[list[dict]]:
    """Topics packed in order, at most CAP folded sections a group; a larger topic alone."""
    out: list[list[dict]] = []
    cur: list[dict] = []
    for t in ts:
        n = len(t["fold"])
        if cur and sum(len(x["fold"]) for x in cur) + n > CAP:
            out.append(cur)
            cur = []
        cur.append(t)
        if n > CAP:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def item(t: dict) -> str:
    lines = [f"- **{t['title']}** - fold " + ", ".join(f"`{s}`" for s in t["fold"])]
    lines.append(f"  - rendering section: {t['rendering'] or 'none'}")
    lines.append(f"  - modals whose `Entry:` names a folded section: {t['modals'] or '-'}")
    if t["note"]:
        lines.append(f"  - note: {t['note']}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    page = argv[1]
    date = argv[2] if len(argv) > 2 else datetime.date.today().isoformat()
    clone = argv[3] if len(argv) > 3 else "/diagram/.clones/diagram-reorg"
    plan = (HERE / f"plan-{page.replace('/', '-')}.md").read_text(encoding="utf-8")
    write_t = (HERE / "write.template.md").read_text(encoding="utf-8")
    check_t = (HERE / "check.template.md").read_text(encoding="utf-8")
    out = HERE / "briefs"
    out.mkdir(exist_ok=True)
    slug = page.replace("/", "-")
    queue = []
    for i, g in enumerate(groups(topics(plan)), 1):
        gid = f"G{i:02d}"
        sections = " ".join(s.split("-")[0] for t in g for s in t["fold"])
        subst = {"clone": clone, "clonename": clone.rstrip("/").split("/")[-1], "page": page, "group": gid, "date": date, "sections": sections,
                 "topics": "\n".join(item(t) for t in g),
                 "topic_titles": "; ".join(f"\"{t['title']}\"" for t in g)}
        w = out / f"{slug}-{gid}-write.md"
        c = out / f"{slug}-{gid}-check.md"
        w.write_text(write_t.format(**subst), encoding="utf-8")
        c.write_text(check_t.format(**subst), encoding="utf-8")
        queue += [str(w), str(c)]
        print(f"{gid}: {len(g)} topic(s), {sum(len(t['fold']) for t in g)} section(s)" + (" - over the cap" if sum(len(t['fold']) for t in g) > CAP else ""))
    print("QUEUE " + " ".join(queue))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
