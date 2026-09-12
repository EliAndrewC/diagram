"""Feature 194 FR-013: every link in every record page resolves - the file exists, and the id where one is named.
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
    # the citations pages (feature 211) are record pages: their notes link out and back, and their works sections link keys
    return sorted(root.glob("*.html")) + sorted((root / "cities").glob("*.html")) + sorted((root / "citations").glob("*.html")) + sorted((root / "citations" / "cities").glob("*.html"))


@pytest.mark.parametrize("page", _pages(), ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
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
            if path.suffix != ".html":
                continue  # a Markdown target's anchors are GitHub's to render; the file existing is the check here
            ids = set(_ID.findall(path.read_text(encoding="utf-8")))
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
    """FR-013 (b): prose, inline code and links alike, in every tracked file outside specs/ and the GM's README.
    `scripts/fixtures/` is out too (feature 209, found red on main after feature 204 landed): a guard's replay corpus
    is a verbatim census of commands sessions actually ran, some of them from before the record was HTML, and
    rewriting a recorded command to satisfy this test would falsify the corpus it exists to replay."""
    root = _repo_root()
    files = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    hits = []
    for rel in files:
        if not rel or rel.startswith(("specs/", "scripts/fixtures/")) or rel == f"{_SKILL}/research/README.md":
            continue
        # A RECORDED FIXTURE IS HISTORY, NOT A POINTER (2026-09-07): `scripts/fixtures/` holds guard firings
        # replayed by the guard suites - the commands sessions actually typed, verbatim, some of them naming
        # research files that were Markdown at the time. Feature 204 landed one and turned main red here; the
        # commands are quotations of what happened, like a spec, and are never followed as links.
        if rel.startswith("scripts/fixtures/"):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError, OSError:
            continue
        for m in _MD_TOKEN.finditer(text):
            if _resolves_to_converted(m.group(1), rel):
                hits.append(f"{rel}: {m.group(1)}")
    assert not hits, "tokens naming the deleted Markdown:\n" + "\n".join(hits[:20])


#: THE RULE FILES RETIRED INTO THE RECORD (feature 229, GM 2026-09-12: the settlements rule files "can be deleted
#: and references to it removed"). Their stems; the `.md` is appended at run time so that this file's own
#: literals are not tokens the rule would count.
_RETIRED_STEMS = (
    "settlements",
    "settlements/archetypes",
    "settlements/capitals",
    "settlements/cities",
    "settlements/fields",
    "settlements/homesteads",
    "settlements/presentation",
    "settlements/religion-and-death",
    "settlements/towns",
    "settlements/urban-features",
    "settlements/vegetation",
    "settlements/water",
    "settlements/ways",
    "settlements/cities/defenses",
    "settlements/cities/fabric",
    "settlements/cities/government",
    "settlements/cities/hinterland",
    "settlements/cities/river-cities",
    "settlements/cities/sizing",
)
_RETIRED_PATHS = {f"{_SKILL}/{stem}.md" for stem in _RETIRED_STEMS}
_RETIRED_BASENAMES = {stem.rsplit("/", 1)[-1] + ".md" for stem in _RETIRED_STEMS}
#: Recorded history, never a pointer: the guard replay corpus and the frozen pre-189 class fixture keep the
#: tokens they were recorded with; `research/README.md` is the GM's (constitution XVII) and keeps its table until
#: the GM applies the correction offered in specs/229.
_RETIRED_EXEMPT_PREFIXES = ("specs/", "scripts/fixtures/")
_RETIRED_EXEMPT_FILES = {f"{_SKILL}/research/README.md", f"{_SKILL}/tests/fixtures/classes_before_189.json"}


def _normalize(base: pathlib.PurePosixPath, token: str) -> str:
    cand = str(pathlib.PurePosixPath(base, token))
    parts: list[str] = []
    for p in cand.split("/"):
        if p in ("", "."):
            continue
        if p == ".." and parts:
            parts.pop()
        else:
            parts.append(p)
    return "/".join(parts)


def names_a_retired_rule_file(token: str, containing_rel: str, exists: set[str]) -> bool:
    """Feature 229's rule, judged PER REFERENCE. A token that resolves - from its file's directory, the skill root
    or the repository root - to one of the retired paths is a hit. A BARE basename (`capitals.md`) is a hit
    unless it resolves from its own file's directory to a file that still exists: `future-work/towns.md` and
    `future-work/cities.md` are living siblings that `future-work/CLAUDE.md` links to, and stay legitimate."""
    here = pathlib.PurePosixPath(containing_rel).parent
    for base in (here, pathlib.PurePosixPath(_SKILL), pathlib.PurePosixPath(".")):
        if _normalize(base, token) in _RETIRED_PATHS:
            return True
    if "/" not in token and token in _RETIRED_BASENAMES:
        return _normalize(here, token) not in exists
    return False


def retired_rule_file_hits(files: dict[str, str], exists: set[str]) -> list[str]:
    hits = []
    for rel, text in files.items():
        if rel.startswith(_RETIRED_EXEMPT_PREFIXES) or rel in _RETIRED_EXEMPT_FILES:
            continue
        for m in _MD_TOKEN.finditer(text):
            if names_a_retired_rule_file(m.group(1), rel, exists):
                hits.append(f"{rel}: {m.group(1)}")
                break
    return hits


def test_no_tracked_file_names_a_retired_rule_file() -> None:
    """Feature 229: the `settlements/` rule files are gone and nothing points at them - by path or by bare basename."""
    root = _repo_root()
    tracked = [f for f in subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n") if f]
    files: dict[str, str] = {}
    for rel in tracked:
        try:
            files[rel] = (root / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError, OSError:
            continue
    hits = retired_rule_file_hits(files, set(tracked))
    assert not hits, "references to a retired rule file (feature 229; re-point at the research anchor):\n" + "\n".join(hits[:30])


def test_the_retired_rule_file_rule_fires_and_spares_a_living_sibling() -> None:
    exists = {"future-work/towns.md", "future-work/CLAUDE.md", "x/y.py", "doc.md", "specs/229/spec.md"}
    files = {
        "doc.md": "see " + _SKILL + "/settlements/homesteads.md for the rule",
        "x/y.py": "# the doctrine (capitals.md, 'WHY blank')",
        "future-work/CLAUDE.md": "- [towns](towns.md) - the town tier's open work",
        "specs/229/spec.md": "the GM named settlements/homesteads.md",
    }
    hits = retired_rule_file_hits(files, exists)
    assert hits == ["doc.md: " + _SKILL + "/settlements/homesteads.md", "x/y.py: capitals.md"], hits


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
