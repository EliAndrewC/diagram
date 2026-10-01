#!/usr/bin/env python3
"""Rewrite pointers to the record's assembled pages into pointers to its fragments (feature 301, T12).

    python3 scripts/_pointer_sweep.py [--write] [--review <file>]     every tracked file in scope
    python3 scripts/_pointer_sweep.py --selftest

The GM, 2026-10-01: *"the obvious solution is to not link to the generated HTML page, but to link to the source which
is fed into and used to generate that HTML page, because that is the canonical location of the research"*. The pages
are built and no longer committed, so `research/water.html "Reservoir ponds (tameike)"` points at nothing in the
repository; `research/water/120-reservoir-ponds-tameike.html` points at the research itself.

What it rewrites, and how:

    research/<page>.html#<id>                    the fragment holding that id (with `#<id>` kept when it is not the
                                                 question's own); a registry key, the entry's fragment
    research/<page>.html - 'Heading', 'Heading'  each quoted heading to its fragment, matched exactly, then by the
    research/<page>.html "Heading"               record's anchor rule, then by the prefix rule `Entry:` lines used
                                                 (a heading shortened at a dash), when exactly one question matches
    research/<page>.html                         the page's fragment directory, `research/<page>/`
    research/SOURCES.html#<key>, SOURCES.html#<key>   the registry entry's fragment
    research/citations/<page>.html               the page's fragment directory (its notes live beside its questions)

A match that is not certain - a heading no question carries, two questions a prefix matches, an id in no fragment - is
left untouched and listed for review (spec FR-013: never guessed). Out of scope, never touched: the record itself, the
GM's request files and READMEs, the landed features' spec directories (spec edge case, research R7), the run and
bypass logs and the guard fixtures (records of what happened), the legacy pool and the frozen test fixtures, and the
files that name the built pages as PATHS rather than point at research (listed in `FUNCTIONAL`, edited by hand).
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude/skills/diagram"
RECORD = SKILL / "research"
REL_RECORD = ".claude/skills/diagram/research"

#: Files that name a built page as a path the code reads or writes, not as a pointer - edited by hand (tasks T12).
FUNCTIONAL = (
    ".claude/skills/diagram/l7r/diagram/interactive/sources.py",
    ".claude/skills/diagram/l7r/diagram/interactive/citations.py",
    ".claude/skills/diagram/l7r/diagram/interactive/record/",
    ".claude/skills/diagram/l7r/diagram/tools/record_asset.py",
    ".claude/skills/diagram/l7r/diagram/tools/citations_asset.py",
    ".claude/skills/diagram/l7r/diagram/tools/glossary_asset.py",
    ".claude/skills/diagram/tests/",
    "scripts/",
    ".gitignore",
)
EXCLUDED = (
    REL_RECORD + "/",
    ".claude/skills/diagram/dev/bypass-log/",
    ".claude/skills/diagram/dev/run-log/",
    ".claude/skills/diagram/dev/perf-log/",
    ".claude/skills/diagram/legacy-hand-authored-pool/",
)
#: The record's own docs, which ARE in scope though they live under research/.
RECORD_DOCS = (REL_RECORD + "/CLAUDE.md", REL_RECORD + "/STYLE.md")
SOURCE_BLOCK = re.compile(r"<!-- SOURCE: GM NOTES.*?<!-- /SOURCE.*?-->", re.S)


def in_scope(path: str) -> bool:
    name = os.path.basename(path)
    if path in RECORD_DOCS:
        return True
    if name == "README.md" or name == "request.md" or name == "gm-request.md":
        return False
    if path.startswith(EXCLUDED) or path.startswith(FUNCTIONAL):
        return False
    if path.startswith("specs/301-record-site/"):
        return False  # this feature's own spec discusses the old forms as its subject
    return not path.endswith((".png", ".webp", ".svg", ".jpg", ".gz", ".pdf"))


# ------------------------------------------------------------------------------------------------- the record's map


def _anchor(heading: str) -> str:
    sys.path.insert(0, str(SKILL))
    from l7r.diagram.interactive.sources import github_anchor  # noqa: PLC0415

    return github_anchor(heading)


class Record:
    """Every page's questions: their fragment names, ids, heading texts, and every other id they hold."""

    def __init__(self, record: pathlib.Path = RECORD) -> None:
        self.record = record
        self.pages: dict[str, str] = {}  # page rel (fields.html) -> page dir (fields)
        self.questions: dict[str, list[tuple[str, str, str]]] = {}  # page rel -> [(fragment rel path, id, heading)]
        self.ids: dict[tuple[str, str], tuple[str, str]] = {}  # (page rel, id) -> (fragment rel path, question id)
        self.text: dict[str, str] = {}  # fragment rel path -> its visible text, folded
        self.manual: dict[tuple[str, str], str] = {}  # (page rel, folded heading or anchor) -> fragment, by hand
        for front in sorted(record.rglob("_front.html")):
            d = front.parent.relative_to(record).as_posix()
            page = "SOURCES.html" if d == "sources" else f"{d}.html"
            self.pages[page] = d
            out: list[tuple[str, str, str]] = []
            for frag in sorted(front.parent.rglob("[0-9]*.html")):
                if frag.name.endswith((".notes.html", ".originals.html")):
                    continue
                text = frag.read_text(encoding="utf-8")
                m = re.search(r'<h([23]) id="([^"]+)">(.*?)</h\1>', text, re.S)
                if not m:
                    continue
                rel = f"research/{frag.relative_to(record).as_posix()}"
                heading = _heading_text(m.group(3))
                out.append((rel, m.group(2), heading))
                self.text[rel] = _plain(_heading_text(re.sub(r"<!--.*?-->", "", text, flags=re.S)))
                for found in re.findall(r'\bid="([^"]+)"', re.sub(r"<!--.*?-->", "", text, flags=re.S)):
                    self.ids.setdefault((page, found), (rel, m.group(2)))
            self.questions[page] = out

    def load_map(self, table: pathlib.Path) -> None:
        """The hand resolutions (`specs/301-record-site/pointer-review.md`): `| page | heading or anchor | target |`,
        the target a fragment path or a unique prefix of one."""
        for line in table.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or not cells[2].startswith("research/"):
                continue
            prefix = self.record.parent / cells[2]
            hits = [f for f in sorted(prefix.parent.glob(prefix.name + "*.html")) if not f.name.endswith((".notes.html", ".originals.html"))]
            if len(hits) != 1:
                raise SystemExit(f"pointer-review: `{cells[2]}` names {len(hits)} fragments - a target names exactly one")
            self.manual[(cells[0], _plain(cells[1]))] = f"research/{hits[0].relative_to(self.record).as_posix()}"

    def by_id(self, page: str, anchor: str) -> str | None:
        hit = self.ids.get((page, anchor))
        if hit is None:
            return self.manual.get((page, _plain(anchor)))
        rel, qid = hit
        return rel if anchor == qid else f"{rel}#{anchor}"

    def by_heading(self, page: str, quoted: str) -> str | None:
        qs = self.questions.get(page, [])
        exact = [r for r, _i, h in qs if h == quoted or _plain(h) == _plain(quoted)]
        if len(exact) == 1:
            return exact[0]
        anchor = _anchor(quoted)
        by_anchor = [r for r, i, _h in qs if i == anchor]
        if len(by_anchor) == 1:
            return by_anchor[0]
        prefix = [r for r, _i, h in qs if _plain(h).startswith(_plain(quoted)) or _plain(quoted).startswith(_plain(h))]
        if len(prefix) == 1:
            return prefix[0]
        # A bolded sub-question in a question's body (feature 292 turned many old headings into these): the quoted
        # words, verbatim, in exactly one fragment of the page - a certainty, not a guess.
        inside = [r for r, _i, _h in qs if _plain(quoted) in self.text[r]]
        if len(inside) == 1:
            return inside[0]
        return self.manual.get((page, _plain(quoted)))


def _heading_text(inner: str) -> str:
    import html as _html  # noqa: PLC0415

    text = re.sub(r'<span class="xref">.*?</span>', "", inner, flags=re.S)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", text))).strip()


def _plain(s: str) -> str:
    """A heading compared loosely: emphasis markers and the dated bookkeeping dropped, case and spacing folded."""
    s = re.sub(r"[*`]", "", s)
    s = re.sub(r"\s*\([^()]*\b\d{4}-\d{2}-\d{2}\b[^()]*\)\s*$", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


# ------------------------------------------------------------------------------------------------- the rewrite

_PAGE = r"(?:(?:cities|rendering|rendering/cities)/)?[A-Za-z][A-Za-z-]*\.html"
#: research/<page>.html, or citations/, then an optional #anchor
_POINTER = re.compile(r"(?<![\w/.-])((?:\.\./)*)research/(citations/)?(" + _PAGE + r")(#[^\s\"'`)\]<>,;|]+)?")
_BARE_SOURCES = re.compile(r"(?<![\w/.-])SOURCES\.html#([a-z0-9][a-z0-9-]*)")
#: Quoted headings after a page: separators, then 'x' or "x" repeated with , / and / ; between
#: A line break inside a quoted heading, with whatever continues a comment or a docstring on the next line.
_WRAP = r"\n[ \t]*(?:#:?|//|\*)?[ \t]*"
_QUOTE = re.compile(
    r"""\s*(?:-|:|,|\(|-)?\s*(?:'(?!s\b)((?:[^'\n]|'(?=[A-Za-z])|""" + _WRAP + r"""){1,250})'|"((?:[^"\n]|""" + _WRAP + r"""){1,250})"|“((?:[^”\n]|""" + _WRAP + r"""){1,250})”)"""
)
_JOIN = re.compile(r"""\s*(?:,|and|;)?\s*(?=['"“])""")


def rewrite(text: str, rec: Record, *, history: bool = False) -> tuple[str, list[str]]:
    """`text` with every pointer it can resolve rewritten, and a line for each it could not.

    `history` is a landed feature's spec: a quoted heading that no question carries any more (most were retired by
    feature 292) is not re-targeted by judgment there - the pointer names its page's fragment directory, which is
    certain, and the quoted heading stays as written, the words a reader searches for."""
    review: list[str] = []
    out: list[str] = []
    pos = 0
    protected = [(m.start(), m.end()) for m in SOURCE_BLOCK.finditer(text)]
    for m in _POINTER.finditer(text):
        if m.start() < pos or any(a <= m.start() < b for a, b in protected):
            continue
        prefix, citations, page, anchor = m.group(1), m.group(2), m.group(3), m.group(4)
        if page not in rec.pages:
            continue  # not a page of the record (a page that no longer exists, or a name mentioned in passing)
        end = m.end()
        if anchor and anchor[-1] in ".:":  # a sentence's full stop, not the anchor's
            trimmed = anchor.rstrip(".:")
            end -= len(anchor) - len(trimmed)
            anchor = trimmed
        repl: str | None
        if citations:
            repl = f"research/{rec.pages[page]}/"
        elif anchor:
            repl = rec.by_id(page, anchor[1:])
            if repl is None and history:
                repl = f"research/{rec.pages[page]}/"
            elif repl is None:
                review.append(f"`{m.group(0)}` - no id `{anchor[1:]}` in any fragment of {page}")
        else:
            # a pointer written as code - `research/x.html`, 'Heading' - keeps its closing backtick after the fragment
            tick = "`" if text[m.end() : m.end() + 1] == "`" else ""
            quotes, end = _quoted_after(text, m.end() + len(tick))
            if quotes:
                hits = [rec.by_heading(page, q) for q in quotes]
                if all(hits):
                    repl = ", ".join(dict.fromkeys(h for h in hits if h)) + tick
                elif history:
                    repl, end = f"research/{rec.pages[page]}/", m.end()
                else:
                    repl = None
                    missing = [q for q, h in zip(quotes, hits, strict=True) if not h]
                    review.append(f"`research/{page}` - no single question carries {', '.join(repr(q) for q in missing)}")
            else:
                repl, end = f"research/{rec.pages[page]}/", m.end()
        if repl is None:
            continue
        out.append(text[pos : m.start()] + prefix + repl)
        pos = end
    out.append(text[pos:])
    text = "".join(out)

    def bare(m: re.Match[str]) -> str:
        hit = rec.by_id("SOURCES.html", m.group(1))
        if hit is None:
            review.append(f"`{m.group(0)}` - no registry entry `{m.group(1)}`")
            return m.group(0)
        return hit

    return _BARE_SOURCES.sub(bare, text), review


def _quoted_after(text: str, at: int) -> tuple[list[str], int]:
    """The quoted headings that follow a page pointer, and where they end. Stops at the first non-quote."""
    quotes: list[str] = []
    end = at
    m = _QUOTE.match(text, at)
    opened = bool(m) and "(" in text[at : m.start(1) if m.group(1) else m.start(2) if m.group(2) else m.start(3)]  # type: ignore[union-attr]
    while m:
        quotes.append(re.sub(_WRAP, " ", m.group(1) or m.group(2) or m.group(3)))
        end = m.end()
        j = _JOIN.match(text, end)
        if not j:
            break
        m = _QUOTE.match(text, j.end())
        if m and not re.match(r"\s*(?:,|and|;)?\s*$", text[end : m.start()]):
            break
    if opened and text[end : end + 1] == ")":
        end += 1  # the heading was given in parentheses: the pointer replaces the parentheses too
    return quotes, end


def tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if in_scope(p)]


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        selftest()
        print("pointer-sweep selftest: ok")
        return 0
    write = "--write" in argv
    review_file = argv[argv.index("--review") + 1] if "--review" in argv else ""
    rec = Record()
    if "--map" in argv:
        rec.load_map(pathlib.Path(argv[argv.index("--map") + 1]))
    changed = 0
    reviews: list[str] = []
    for path in tracked():
        p = ROOT / path
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if "research/" not in text and "SOURCES.html" not in text:
            continue
        new, review = rewrite(text, rec, history=bool(re.match(r"specs/(\d+)-", path)) and int(path.split("/")[1].split("-")[0]) < 301)
        reviews += [f"{path}: {r}" for r in review]
        if new != text:
            changed += 1
            if write:
                p.write_text(new, encoding="utf-8")
    print(f"pointer-sweep: {changed} file(s) {'rewritten' if write else 'would change'}; {len(reviews)} pointer(s) for review")
    if review_file:
        pathlib.Path(review_file).write_text("".join(f"- {r}\n" for r in reviews), encoding="utf-8")
    else:
        print("\n".join(reviews))
    return 0


def selftest() -> None:
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        rec_dir = pathlib.Path(td) / "research"
        (rec_dir / "water").mkdir(parents=True)
        (rec_dir / "water" / "_front.html").write_text("x")
        (rec_dir / "water" / "120-reservoir-ponds-tameike.html").write_text('<h2 id="reservoir-ponds-tameike">Reservoir ponds (tameike)</h2><p id="inner">x</p>')
        (rec_dir / "water" / "130-a-reservoirs-shore-is-reeded.html").write_text('<h2 id="a-reservoirs-shore-is-reeded">A reservoir\'s shore is reeded</h2>')
        (rec_dir / "sources" / "010-works-cited").mkdir(parents=True)
        (rec_dir / "sources" / "_front.html").write_text("x")
        (rec_dir / "sources" / "010-works-cited.html").write_text('<h2 id="works-cited">Works cited</h2>')
        (rec_dir / "sources" / "010-works-cited" / "0010-fei-1939.html").write_text('<h3 id="fei-1939"><code>fei-1939</code></h3>')
        rec = Record(rec_dir)
        cases = {
            "see research/water.html#reservoir-ponds-tameike.": "see research/water/120-reservoir-ponds-tameike.html.",
            "research/water.html#inner": "research/water/120-reservoir-ponds-tameike.html#inner",
            "Entry: research/water.html - 'Reservoir ponds (tameike)', \"A reservoir's shore is reeded\"": "Entry: research/water/120-reservoir-ponds-tameike.html, research/water/130-a-reservoirs-shore-is-reeded.html",
            'research/water.html "Reservoir ponds" says': "research/water/120-reservoir-ponds-tameike.html says",
            "the water page (research/water.html) holds it": "the water page (research/water/) holds it",
            "`fei-1939` in research/SOURCES.html#fei-1939": "`fei-1939` in research/sources/010-works-cited/0010-fei-1939.html",
            "SOURCES.html#fei-1939 too": "research/sources/010-works-cited/0010-fei-1939.html too",
            "research/citations/water.html": "research/water/",
            "is `research/water.html`, 'Reservoir ponds (tameike)'.": "is `research/water/120-reservoir-ponds-tameike.html`.",
            "see `research/water.html` for it": "see `research/water/` for it",
            "`research/water.html`'s rules. Then 'x'": "`research/water/`'s rules. Then 'x'",
            "research/water.html ('Reservoir ponds (tameike)') says": "research/water/120-reservoir-ponds-tameike.html says",
            "# see research/water.html 'Reservoir\n    # ponds (tameike)' for it": "# see research/water/120-reservoir-ponds-tameike.html for it",
            "../../research/water.html#reservoir-ponds-tameike": "../../research/water/120-reservoir-ponds-tameike.html",
            "research/nowhere.html": "research/nowhere.html",
        }
        for before, after in cases.items():
            got, review = rewrite(before, rec)
            assert got == after, (before, got)
            assert not review, (before, review)
        got, review = rewrite("research/water.html 'No such heading'", rec)
        assert got == "research/water.html 'No such heading'" and review, "an unmatched heading is left and listed"
        got, review = rewrite("research/water.html 'No such heading'", rec, history=True)
        assert got == "research/water/ 'No such heading'" and not review, "in a landed spec, the page directory and the words kept"
        assert rewrite("research/water.html#gone", rec, history=True) == ("research/water/", [])
        got, review = rewrite("research/water.html#missing", rec)
        assert got == "research/water.html#missing" and review
        block = "<!-- SOURCE: GM NOTES - DO NOT MODIFY -->research/water.html<!-- /SOURCE -->"
        assert rewrite(block, rec)[0] == block, "a SOURCE block is the GM's"
    assert in_scope("specs/233-x/spec.md") and not in_scope("specs/301-record-site/plan.md") and not in_scope("specs/233-x/request.md")
    assert not in_scope(REL_RECORD + "/water/120-x.html") and in_scope(REL_RECORD + "/CLAUDE.md")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
