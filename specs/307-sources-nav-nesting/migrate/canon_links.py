#!/usr/bin/env python3
"""Feature 307, one-time: point the GM's campaign-note entries at their public home on GitHub (GM 2026-10-02:
*"the correct place to find them is on GitHub at https://github.com/EliAndrewC/l7r/tree/master/setting"*).

    python3 specs/307-sources-nav-nesting/migrate/canon_links.py NOTES_DIR [--write]

NOTES_DIR holds the two note files as fetched from that repository. For each canon entry, every quoted section name on
its citation line is found among its file's headings and gets its GitHub anchor - computed by the engine's own
`github_anchor`, over every heading in file order outside code fences, so a repeated heading takes its `-1` - and the
"(URL: none ...)" parenthesis is replaced by the file's URL. A section name not found is refused, and nothing is written.
"""

from __future__ import annotations

import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(".claude/skills/diagram").resolve()))
from l7r.diagram.interactive.sources import github_anchor  # noqa: E402

REGISTRY = pathlib.Path(".claude/skills/diagram/research/sources/010-works-cited")
BASE = "https://github.com/EliAndrewC/l7r/blob/master/setting/"
NONE = re.compile(r"\s*\(URL: none - the GM's own unpublished writing, at <code>/host-l7r-repo/setting/(l7r|budgets)\.md</code>\)")
QUOTED = re.compile(r'"([^"]+)"')


def anchors(md: str) -> dict[str, str]:
    """Heading text -> its GitHub anchor (the first heading of that text)."""
    out: dict[str, str] = {}
    seen: dict[str, int] = {}
    fence = False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m and not fence:
            out.setdefault(re.sub(r"[*_`]", "", m.group(2)).strip(), github_anchor(m.group(2), seen))
    return out


def find(heads: dict[str, str], name: str) -> str | None:
    """A quoted section name's anchor: its heading by plain text, else the one heading that begins with it (an entry may
    quote a long heading's opening words, or a heading carrying a suffix such as a cost)."""
    if name in heads:
        return heads[name]
    starts = [a for h, a in heads.items() if h.startswith(name)]
    return starts[0] if len(starts) == 1 else None


def main() -> int:
    notes = pathlib.Path(sys.argv[1])
    write = "--write" in sys.argv
    heads = {f: anchors((notes / f"{f}.md").read_text(encoding="utf-8")) for f in ("l7r", "budgets")}
    plans, missing, done = [], [], []
    for path in sorted(REGISTRY.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        first = re.search(r"</h3>\s*<p>(.*?)</p>", text, re.S)
        if not first or not NONE.search(first.group(1)):
            continue
        line = first.group(1)
        f = NONE.search(line).group(1)  # type: ignore[union-attr]
        new = NONE.sub(f" ({BASE}{f}.md)", line, count=1)
        visible = html.unescape(line.split("<!--")[0])
        for name in dict.fromkeys(QUOTED.findall(visible)):
            anchor = find(heads[f], name)
            if anchor is None:
                missing.append(f'{path.name}: "{name}" is no heading of {f}.md')
                continue
            quoted = f'"{html.escape(name, quote=False)}"'
            new = new.replace(quoted, f"{quoted} ({BASE}{f}.md#{anchor})", 1)
            done.append(f"{path.name}: {name} -> #{anchor}")
        plans.append((path, text.replace(line, new, 1)))
    print(f"{len(plans)} canon entries; {len(done)} sections linked; {len(missing)} section names not found")
    print("\n".join(missing + done[:6]))
    if write and not missing:
        for path, text in plans:
            path.write_text(text, encoding="utf-8")
        print("written")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
