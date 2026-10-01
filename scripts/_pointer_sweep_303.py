#!/usr/bin/env python3
"""The one-time pointer sweep of feature 303 (plan D8) - deleted once it has run and landed.

The GM, 2026-10-01: *"make sure that places in our code base that refer to individual research files by file path or
something, or for that matter by number ... use the correct new number"*, and no redirects. Every tracked text file is
rewritten from the old layout to the new, reading `research/moved-303.json` (what the flattening wrote):

    research/<page>/NNN-<id>.html (.notes / .originals)   -> research/questions/NNNN-<slug>[.drawing]....html
    research/<page>.html#<anchor>                          -> the question page holding the anchor
    research/<page>.html, research/<page>/, citations/...  -> research/contents.json#<section>
    research <page> '<heading>'                            -> research/questions/<file> '<heading>'
    <page> NNN-MMM (a range covering questions)            -> the new numbers it covered
    <page> NNN, <page>/NNN (an existing question)          -> NNNN

Skipped: the GM's verbatim words (`specs/*/request.md`, SOURCE blocks), `moved-303.json`, this feature's
`migration.md`, and the built site. Every number-form rewrite and every pointer it could not place is listed in
`specs/303-research-organization/migration.md` for review.

    _pointer_sweep_303.py --root <repo> [--write]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

SKILL = ".claude/skills/diagram"
RECORD = f"{SKILL}/research"
MIGRATION = "specs/303-research-organization/migration.md"
TITLE = " - second pass (a page name and number naming a drawing page)"
EXEMPT = (f"{RECORD}/moved-303.json", MIGRATION, "scripts/_pointer_sweep_303.py", "scripts/_record_flatten.py")
_SOURCE = re.compile(r"<!-- SOURCE: GM NOTES.*?<!-- END SOURCE -->", re.S)
_ID = re.compile(r'\bid="([^"]+)"')
_H2 = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
_TAG = re.compile(r"<[^>]+>")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class Sweep:
    def __init__(self, root: str) -> None:
        self.root = root
        mapping = json.loads(_read(os.path.join(root, RECORD, "moved-303.json")))
        self.files: dict[str, str] = mapping["files"]  # old path (under research/) -> questions/<new>
        self.pages: dict[str, str] = mapping["pages"]  # old page dir -> section id
        self.numbers: dict[str, str] = mapping["numbers"]  # "<page> NNN" -> NNNN
        self.anchor_file: dict[str, str] = {}
        self.titles: dict[str, str] = {}
        qdir = os.path.join(root, RECORD, "questions")
        for name in sorted(os.listdir(qdir)):
            if name.endswith((".notes.html", ".originals.html")):
                continue
            text = re.sub(r"<!--.*?-->", "", _read(os.path.join(qdir, name)), flags=re.S)
            for i in _ID.findall(text):
                self.anchor_file.setdefault(i, name)
            h = _H2.search(text)
            if h:
                self.titles[re.sub(r"\s+", " ", _TAG.sub("", h.group(2))).strip().lower()] = name
        names = sorted(self.pages, key=len, reverse=True)
        alt = "|".join(re.escape(p) for p in names)
        self.re_path = re.compile("|".join(re.escape(p) for p in sorted(self.files, key=len, reverse=True)))
        self.re_page_html = re.compile(rf"research/(?:citations/)?({alt})\.html(?:#([^\s\"'`)<>,;]+))?")
        self.re_page_dir = re.compile(rf"research/({alt})/(?![\d])")
        self.re_prose = re.compile(rf"research ({alt}) '([^']+)'")
        self.re_range = re.compile(rf"(?<![\w/.-])({alt})[ /](\d{{3}})-(\d{{3}})(?![\d-])")
        self.re_number = re.compile(rf"(?<![\w/.-])(research/)?({alt})([ /])(\d{{3}})(?![\d]|-[a-z0-9])")
        self.review: list[str] = []
        self.changed: dict[str, int] = {}

    def section(self, page: str) -> str:
        return f"research/contents.json#{self.pages[page]}"

    def apply(self, rel: str, text: str) -> str:
        holes = [(m.start(), m.end()) for m in _SOURCE.finditer(text)]
        if holes:
            out, last = [], 0
            for a, b in holes:
                out.append(self._apply(rel, text[last:a]))
                out.append(text[a:b])
                last = b
            out.append(self._apply(rel, text[last:]))
            return "".join(out)
        return self._apply(rel, text)

    def _apply(self, rel: str, text: str) -> str:
        text = self.re_path.sub(lambda m: self.files[m.group(0)], text)

        def page_html(m: re.Match[str]) -> str:
            page, anchor = m.group(1), m.group(2)
            if anchor and anchor in self.anchor_file:
                file = self.anchor_file[anchor]
                head = _H2.search(_read(os.path.join(self.root, RECORD, "questions", file)))
                return f"research/questions/{file}" + ("" if head and head.group(1) == anchor else f"#{anchor}")
            if anchor:
                self.review.append(f"{rel}: `{m.group(0)}` - no id `{anchor}` in the record; pointed at its section")
            return self.section(page)

        text = self.re_page_html.sub(page_html, text)
        text = self.re_page_dir.sub(lambda m: self.section(m.group(1)), text)

        def prose(m: re.Match[str]) -> str:
            file = self.titles.get(m.group(2).strip().lower())
            if file is None:
                self.review.append(f"{rel}: `{m.group(0)}` - no question titled so; pointed at its section")
                return f"{self.section(m.group(1))} '{m.group(2)}'"
            return f"research/questions/{file} '{m.group(2)}'"

        text = self.re_prose.sub(prose, text)

        def rng(m: re.Match[str]) -> str:
            page, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            covered = [v for k, v in self.numbers.items() if k.split(" ")[0] == page and a <= int(k.split(" ")[1]) <= b]
            if not covered:
                self.review.append(f"{rel}: `{m.group(0)}` - a range covering no question; left as written")
                return m.group(0)
            new = ", ".join(sorted(covered))
            self.review.append(f"{rel}: `{m.group(0)}` -> `{new}`")
            return new

        text = self.re_range.sub(rng, text)

        def number(m: re.Match[str]) -> str:
            key = f"{m.group(2)} {m.group(4)}"
            if key not in self.numbers and f"rendering/{key}" in self.numbers:
                key = f"rendering/{key}"  # "homesteads 152" naming the drawing page of that part and number
            if key not in self.numbers:
                return m.group(0)
            new = self.numbers[key]
            if m.group(1):
                old_path = next((o for o in self.files if o.startswith(f"{key.split(" ")[0]}/{m.group(4)}-") and o.endswith(".html") and not o.endswith((".notes.html", ".originals.html"))), None)
                out = f"research/{self.files[old_path]}" if old_path else f"research/questions/{new}"
            else:
                out = new
            self.review.append(f"{rel}: `{m.group(0)}` -> `{out}`")
            return out

        return self.re_number.sub(number, text)


def tracked(root: str) -> list[str]:
    out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
    return [p for p in out if p and not p.endswith("/request.md") and p not in EXEMPT and "/research/site/" not in p]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    sweep = Sweep(args.root)
    for rel in tracked(args.root):
        path = os.path.join(args.root, rel)
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        try:
            text = _read(path)
        except (UnicodeDecodeError, OSError):
            continue
        new = sweep.apply(rel, text)
        if new != text:
            sweep.changed[rel] = sum(1 for a, b in zip(text.splitlines(), new.splitlines(), strict=False) if a != b)
            if args.write:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
    report = [f"files changed: {len(sweep.changed)}", f"review lines: {len(sweep.review)}"]
    print("\n".join(report))
    if args.write:
        with open(os.path.join(args.root, MIGRATION), "a", encoding="utf-8") as fh:
            fh.write(f"\n## The pointer sweep's review list{TITLE} (number forms, ranges, and pointers it could not place)\n\n")
            fh.write("\n".join(f"- {r}" for r in sweep.review) + "\n")
    else:
        print("\n".join(sweep.review[:400]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
