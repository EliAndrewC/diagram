"""Feature 191 FR-013: every link in every record page resolves - the file exists, and the id where one is named.
A relative link cannot hide from this; the literal check beside it catches prose pointers outside the record."""

from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

from l7r.diagram.interactive.sources import RESEARCH_DIR

_HREF = re.compile(r'href="([^"]+)"')
_ID = re.compile(r'\sid="([^"]+)"')


def _pages() -> list[pathlib.Path]:
    root = pathlib.Path(RESEARCH_DIR)
    return sorted(root.glob("*.html")) + sorted((root / "cities").glob("*.html"))


@pytest.mark.parametrize("page", _pages(), ids=lambda p: p.name)
def test_every_link_in_a_record_page_resolves(page: pathlib.Path) -> None:
    text = page.read_text(encoding="utf-8")
    ids_here = set(_ID.findall(text))
    bad = []
    for href in _HREF.findall(text):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        target, _, frag = href.partition("#")
        if target:
            path = (page.parent / target).resolve()
            if not path.exists():
                bad.append(f"{href}: no such file")
                continue
            ids = set(_ID.findall(path.read_text(encoding="utf-8"))) if path.suffix == ".html" else set()
        else:
            ids = ids_here
        if frag and frag not in ids:
            bad.append(f"{href}: no id {frag!r} in {target or page.name}")
    assert not bad, f"{page.name}:\n" + "\n".join(bad[:20])


_CONVERTED = {
    "SOURCES",
    "archetypes",
    "buildings",
    "fields",
    "homesteads",
    "religion-and-death",
    "towns",
    "urban-features",
    "vegetation",
    "water",
    "cities/capitals",
    "cities/defenses",
    "cities/fabric",
    "cities/government",
    "cities/hinterland",
    "cities/river-cities",
}
_MD_TOKEN = re.compile(r"(?<![\w/.-])((?:\.\./|\./)*(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_-]+\.md)\b")
_SKILL = "/".join([".claude", "skills", "diagram"])


def _repo_root() -> pathlib.Path:
    return pathlib.Path(RESEARCH_DIR).resolve().parents[3]


def _resolves_to_converted(token: str, containing_rel: str) -> bool:
    """FR-013's rule: a token is in scope only if it RESOLVES - against its file's directory, or as a skill-root or
    repository-root path - to one of the 16 converted files."""
    record = f"{_SKILL}/research/"
    for base in (pathlib.PurePosixPath(containing_rel).parent, pathlib.PurePosixPath(_SKILL), pathlib.PurePosixPath(".")):
        cand = str(pathlib.PurePosixPath(base, token))
        cand = str(pathlib.PurePosixPath(*[p for p in cand.split("/") if p not in ("", ".")]))
        parts: list[str] = []
        for p in cand.split("/"):
            if p == ".." and parts:
                parts.pop()
            else:
                parts.append(p)
        cand = "/".join(parts)
        if cand.startswith(record) and cand[len(record) : -3] in _CONVERTED:
            return True
    return False


def test_no_md_token_anywhere_resolves_to_a_converted_record_file() -> None:
    """FR-013 (b): prose, inline code and links alike, in every tracked file outside specs/ and the GM's README."""
    root = _repo_root()
    files = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    hits = []
    for rel in files:
        if not rel or rel.startswith("specs/") or rel == f"{_SKILL}/research/README.md":
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError, OSError:
            continue
        for m in _MD_TOKEN.finditer(text):
            if _resolves_to_converted(m.group(1), rel):
                hits.append(f"{rel}: {m.group(1)}")
    assert not hits, "tokens naming the deleted Markdown:\n" + "\n".join(hits[:20])


def test_every_md_link_in_the_pages_and_the_index_still_exists() -> None:
    """FR-013 (c): the sweep must not touch a same-basename file that stays Markdown (`../settlements/water.md`,
    the skill's `../buildings.md`) - every `.md` link target in the pages and in research/CLAUDE.md is on disk."""
    pages = _pages() + [pathlib.Path(RESEARCH_DIR, "CLAUDE.md")]
    bad = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        targets = _HREF.findall(text) + re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", text)
        for href in targets:
            target = href.partition("#")[0]
            if target.endswith(".md") and not (page.parent / target).resolve().exists():
                bad.append(f"{page.name}: {href}")
    assert not bad, "Markdown links that no longer resolve:\n" + "\n".join(bad[:20])
