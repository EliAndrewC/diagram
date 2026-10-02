#!/usr/bin/env python3
"""Every pointer to the research names something that exists, and none is of a retired form (features 301, 303).

The GM, 2026-10-01 (feature 301): a rendering decision points at its research - *"the source which is fed into and used
to generate that HTML page, because that is the canonical location of the research"*. And (feature 303), when the page
directories went: *"make sure that places in our code base that refer to individual research files by file path or
something, or for that matter by number ... use the correct new number"*, with no redirect. This holds:

  - a pointer to a question, `research/questions/NNNN-<slug>[.drawing][.notes|.originals].html`, names a file that exists;
  - a pointer to a section of the record, `research/contents.json#<section id>`, names a section that exists;
  - no pointer is of a retired form - a page directory's fragment (`research/<page>/NNN-<id>.html`), a page directory
    (`research/<page>/`), a built page (`research/<page>.html`, `research/citations/<page>.html`), or a question's old
    page and number (`homesteads 440`) - and each one refused names its replacement, read from `research/moved-303.json`
    (the migration's mapping, kept for exactly this: a peer's work written before the move is told where it went).

`make fragment-move` renames a question and rewrites its pointers in the same change. Run at the gate
(`tests/tooling/test_research_pointers.py`) and at the push (`sync-with-main.sh`).

Usage: check-research-pointers.py [ROOT] | --selftest
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SKILL = ".claude/skills/diagram"
RECORD = f"{SKILL}/research"
MAPPING = "moved-303.json"
#: A question's file, named from anywhere (`research/...`, `../research/...`, `.claude/skills/diagram/research/...`).
QUESTION = re.compile(r"(?<![\w.-])research/questions/(\d{4}-[^\s\"'`)\]<>,;|#*]+?\.html)(?![\w.-])")
#: A section of the record.
SECTION = re.compile(r"(?<![\w.-])research/contents\.json#([a-z0-9-]+)")
#: A retired fragment path: any `research/<dir>/.../NNN-<x>.html` outside `questions/` and the registry's `sources/`.
OLD_FRAGMENT = re.compile(r"(?<![\w.-])research/((?:[a-z][a-z-]*/)+)(\d{3}-[^\s\"'`)\]<>,;|#*]+?\.html)(?![\w.-])")
#: A retired page directory, and a retired built page.
OLD_DIRECTORY = re.compile(r"(?<![\w.-])research/((?:[a-z][a-z-]*/)*[a-z][a-z-]*)/(?![\w.-])")  # a directory, not a path into a file
OLD_PAGE = re.compile(r"(?<![\w.-])research/(citations/)?((?:[a-z][a-z-]*/)*[A-Za-z][A-Za-z-]*)\.html(?:#[^\s\"'`)\]<>,;|]+)?(?![\w/-])")
#: What lives under `research/` and is not a retired form.
CURRENT_DIRS = ("questions", "sources", "assets", "site")
#: Files the check does not read: the GM's own words (`request.md`), a README (the GM's to write; its stale references
#: are listed in `specs/303-research-organization/readme-correction-offered.md` until the GM rules on them), and the
#: mapping and the generated mapping table.
EXEMPT = (f"{RECORD}/{MAPPING}", "specs/303-research-organization/migration.md")
_SOURCE_BLOCK = re.compile(r"<!-- SOURCE: GM NOTES.*?<!-- END SOURCE -->", re.S)
#: A quotation in the docs' form, `*"..."*` - the GM's words, which keep theirs (a retired path they mention is history).
_QUOTED = re.compile(r'\*"[^"]*?"\*', re.S)


class Mapping:
    """The migration's mapping (`research/moved-303.json`), and the record as it stands."""

    def __init__(self, record: Path) -> None:
        data = json.loads((record / MAPPING).read_text(encoding="utf-8")) if (record / MAPPING).is_file() else {}
        self.files: dict[str, str] = data.get("files", {})
        self.pages: dict[str, str] = data.get("pages", {})
        self.numbers: dict[str, str] = data.get("numbers", {})
        self.questions = {p.name for p in (record / "questions").glob("*.html")} if (record / "questions").is_dir() else set()
        try:
            contents = json.loads((record / "contents.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            contents = {"sections": []}
        self.sections: set[str] = set()

        def walk(sections: list[dict]) -> None:
            for s in sections:
                self.sections.add(s["id"])
                walk(s.get("sections", []))

        walk(contents["sections"])
        names = sorted({k.split(" ")[0] for k in self.numbers}, key=len, reverse=True)
        alt = "|".join(re.escape(n) for n in names) or "(?!)"
        self.number = re.compile(rf"(?<![\w/.-])({alt})[ /](\d{{3}})(?![\d]|-[a-z0-9])")
        dirs = "|".join(re.escape(n) for n in sorted(self.pages, key=len, reverse=True)) or "(?!)"
        #: A retired page directory named without its trailing slash, as code builds a path to it.
        #: A retired page named by its Markdown file, as the record was before feature 194.
        self.old_md = re.compile(rf"(?<![\w.-])research/({dirs})\.md\b")
        self.old_dir = re.compile(rf"(?<![\w.-])research/({dirs})(?=[\"'`)\s,;:]|\.(?!\w)|$)")
        pages = "|".join(re.escape(n) for n in sorted(self.pages, key=len, reverse=True)) or "(?!)"
        #: A tool's retired arguments: `PAGE=<page> SECTION=<NNN>` (now `Q=`) and a whole page, `PAGE=<page>` (now `IN=`).
        self.command = re.compile(rf"PAGE=({pages})\b(?!/)(?:(?:\s+|,\s*)SECTION=(\d{{3}})\b)?")

    def section_of(self, page: str) -> str:
        section = self.pages.get(page.removeprefix("rendering/")) or self.pages.get(page)
        return f"research/contents.json#{section}" if section else "a section of research/contents.json"


def problems(text: str, mapping: Mapping, *, fixture: bool = False, refusal_data: bool = False, landed_spec: bool = False) -> list[str]:
    """What is wrong with the research pointers in one line of text. In a fixture a new-form question file need not
    exist; in refusal data a retired form is data."""
    out: list[str] = []
    for m in QUESTION.finditer(text):
        if m.group(1) not in mapping.questions and not fixture:
            out.append(f"`research/questions/{m.group(1)}` - no such question file")
    for m in SECTION.finditer(text):
        if m.group(1) not in mapping.sections and not fixture:
            out.append(f"`research/contents.json#{m.group(1)}` - no such section")
    if refusal_data:
        return out
    for m in mapping.old_md.finditer(text):
        out.append(f"`{m.group(0)}` - a retired page (feature 303); name {mapping.section_of(m.group(1))}")
    for m in mapping.old_dir.finditer(text):
        out.append(f"`{m.group(0)}` - the page directories are retired (feature 303); name {mapping.section_of(m.group(1))}")
    for m in OLD_FRAGMENT.finditer(text):
        if m.group(1).split("/")[0] in CURRENT_DIRS:
            continue
        old = f"{m.group(1)}{m.group(2)}"
        new = mapping.files.get(old)
        out.append(f"`research/{old}` - the page directories are retired (feature 303); " + (f"it is now `research/{new}`" if new else "name its question, `research/questions/NNNN-<slug>.html`"))
    for m in OLD_DIRECTORY.finditer(text):
        if m.group(1).split("/")[0] in CURRENT_DIRS or m.group(1) in ("contents.json",):
            continue
        out.append(f"`research/{m.group(1)}/` - the page directories are retired (feature 303); name {mapping.section_of(m.group(1))}")
    for m in OLD_PAGE.finditer(text):
        page = m.group(2)
        if page.split("/")[0] in CURRENT_DIRS:
            continue
        where = "the registry's fragments, `research/sources/`" if page == "SOURCES" else mapping.section_of(page)
        out.append(f"`{m.group(0)}` - a built page; name {where}")
    for m in mapping.command.finditer(text):
        if m.group(2) is None:
            out.append(f"`{m.group(0)}` - a retired page argument; name `IN={mapping.pages.get(m.group(1), '<section or tag>')}` (or `Q=<NNNN>`)")
            continue
        key = f"{m.group(1)} {m.group(2)}"
        new = mapping.numbers.get(key) or mapping.numbers.get(f"rendering/{key}")
        if new:
            out.append(f"`{m.group(0)}` - a retired page argument; name `Q={new}`")
        elif not landed_spec:
            out.append(f"`{m.group(0)}` - a retired page argument; name `Q=<NNNN>` (its number names no question: in a landed spec only, as history, it may stand)")
    for m in mapping.number.finditer(text):
        key = f"{m.group(1)} {m.group(2)}"
        new = mapping.numbers.get(key) or mapping.numbers.get(f"rendering/{key}")
        if new:
            out.append(f"`{m.group(0)}` - a question's old page and number; it is now {new}")
    return out


def tracked(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout
    return out.splitlines()


#: What the spec's FR-017 does not edit, as the check reads it (amendment 1). The guard-replay corpora are verbatim
#: records of commands sessions ran, exempt whole. A REFUSAL-DATA file names a retired form in order to prove it is
#: refused (or, for the hook helper, re-aimed), so a retired form there is data. A FIXTURE file - a test, a hook suite, a
#: script's selftest - builds a record of its own in a temporary directory, so a question file it names in the new form
#: need not exist in this one; a retired form in it is still refused, because a test using an old path for any other
#: reason is stale. Everything else - the engine, the tooling's own code, the docs, the agents, the specs - is held whole.
VERBATIM = ("scripts/fixtures/",)
REFUSAL_DATA = (
    "scripts/check-research-pointers.py",
    f"{SKILL}/tests/tooling/test_research_pointers.py",
    "scripts/_hm_record.py",
    "scripts/test-record-edit-hooks.sh",
    "scripts/test-check-bundle-hooks.sh",
    f"{SKILL}/tests/interactive/test_record.py",
)
FIXTURES = (f"{SKILL}/tests/", "scripts/test_", "scripts/test-", "scripts/_fragment_move.py", "scripts/check-entry-headings.py", "scripts/_hm_record.py", "scripts/check-research-pointers.py")
TEST_DATA = VERBATIM


def exempt(path: str) -> bool:
    if path.startswith(TEST_DATA):
        return True
    return path in EXEMPT or path.rsplit("/", 1)[-1] in ("request.md", "README.md") or path.endswith((".png", ".webp", ".jpg", ".pdf", ".gz"))


def check(root: Path) -> list[str]:
    record = root / RECORD
    if not record.is_dir():
        return []  # a repository with no record has no pointers to be right or wrong about
    mapping = Mapping(record)
    bad: list[str] = []
    for path in tracked(root):
        if exempt(path) or "/research/site/" in path:
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        text = _SOURCE_BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), text)  # the GM's own words keep theirs
        text = _QUOTED.sub(lambda m: "\n" * m.group(0).count("\n"), text)  # and so does a quotation of them, *"..."*
        fixture, refusal_data = path.startswith(FIXTURES), path in REFUSAL_DATA
        for line_no, line in enumerate(text.splitlines(), 1):
            bad += [f"{path}:{line_no}: {p}" for p in problems(line, mapping, fixture=fixture, refusal_data=refusal_data, landed_spec=path.startswith("specs/"))]
    return bad


def selftest() -> int:
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        record = Path(td)
        (record / "questions").mkdir()
        (record / "questions" / "0412-reservoir-ponds-tameike.html").write_text("x", encoding="utf-8")
        (record / "contents.json").write_text(json.dumps({"sections": [{"id": "countryside", "sections": [{"id": "water"}]}]}), encoding="utf-8")
        old = "water/120-reservoir-ponds-tameike.html"
        (record / MAPPING).write_text(json.dumps({"files": {old: "questions/0412-reservoir-ponds-tameike.html"}, "pages": {"water": "water"}, "numbers": {"water 120": "0412", "rendering/water 015": "0413"}}), encoding="utf-8")
        mapping = Mapping(record)
        ok = "see research/questions/0412-reservoir-ponds-tameike.html, research/contents.json#water and research/sources/ and research/site/q/x.html"
        assert problems(ok, mapping) == [], problems(ok, mapping)
        assert problems("research/questions/0499-gone.html", mapping) == ["`research/questions/0499-gone.html` - no such question file"]
        assert problems("research/contents.json#nowhere", mapping) == ["`research/contents.json#nowhere` - no such section"]
        assert "it is now `research/questions/0412-reservoir-ponds-tameike.html`" in problems(f"research/{old}", mapping)[0]
        assert "name its question" in problems("research/towns/030-gone.html", mapping)[0]
        assert "name research/contents.json#water" in problems("research/water/ and", mapping)[0]
        assert "name research/contents.json#water" in problems("research/rendering/water/", mapping)[0]
        assert "a built page; name research/contents.json#water" in problems("research/water.html#x", mapping)[0]
        assert "research/sources/" in problems("research/SOURCES.html", mapping)[0] and problems("research/citations/water.html", mapping)
        assert problems("water 120 and water/120", mapping) == ["`water 120` - a question's old page and number; it is now 0412", "`water/120` - a question's old page and number; it is now 0412"]
        assert "now 0413" in problems("water 015", mapping)[0], "a page name and number naming a drawing page"
        assert problems("water 121, water 120-130, 120 water", mapping) == [], "a number that names no question, a range, and prose"
        assert problems("make check-bundle PAGE=water SECTION=120", mapping)[0].endswith("name `Q=0412`")
        assert "name `IN=water`" in problems("make record-prepass PAGE=water", mapping)[0]
        assert problems("PAGE=water SECTION=121", mapping, landed_spec=True) == [], "in a landed spec a retired number names no question"
        assert "name `Q=<NNNN>`" in problems("PAGE=water SECTION=121", mapping)[0], "anywhere else the retired argument is refused"
        assert "name research/contents.json#water" in problems("see research/water" + ".md for it", mapping)[0]
        assert problems('glob(REPO / "research/water")', mapping), "a retired directory named without its slash"
        assert problems("research/questions/0499-made-up.html", mapping, fixture=True) == [], "a fixture names its own record"
        assert problems("research/water/120-reservoir-ponds-tameike.html", mapping, fixture=True), "but not a retired form"
        assert problems("research/water/120-reservoir-ponds-tameike.html", mapping, refusal_data=True) == []
        assert not problems(_QUOTED.sub("", 'the GM: *"a research/citations directory in research/water/"*'), mapping), "a quotation keeps its words"
        assert problems("specs/229-rule-files-into-research/audit/x.md", mapping) == [], "a word ending in -research is not the record"
    assert exempt("specs/180-x/request.md") and exempt(f"{RECORD}/{MAPPING}") and not exempt("CLAUDE.md") and not exempt(f"{RECORD}/CLAUDE.md")
    assert exempt("scripts/fixtures/x.json") and not exempt(f"{SKILL}/tests/x.py") and not exempt("scripts/x.py")
    print("check-research-pointers selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    root = Path(argv[0] if argv else ".").resolve()
    bad = check(root)
    if bad:
        print("pointers to the research that do not resolve, or are of a retired form (features 301, 303):", file=sys.stderr)
        for line in bad[:60]:
            print(f"  {line}", file=sys.stderr)
        if len(bad) > 60:
            print(f"  ... and {len(bad) - 60} more", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
