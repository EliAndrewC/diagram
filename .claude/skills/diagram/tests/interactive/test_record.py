"""Feature 194 FR-013: every link in every record page resolves - the file exists, and the id where one is named.
A relative link cannot hide from this; the literal check beside it catches prose pointers outside the record."""

from __future__ import annotations

import functools
import os
import pathlib
import re
import subprocess

import pytest

from l7r.diagram.interactive.sources import RESEARCH_DIR
from tests._record_pages import RecordPath, all_pages

_HREF = re.compile(r'href="([^"]+)"')
_ID = re.compile(r'\sid="([^"]+)"')


def _pages() -> list[pathlib.Path]:
    """Every page of the record as its fragments assemble it (feature 301: read in memory, never from a built file) -
    the citations pages too (feature 211): their notes link out and back, and their works sections link keys."""
    return list(all_pages())


_IDS: dict[str, set[str]] = {}


def _ids_of(path: pathlib.Path) -> set[str]:
    """The ids a page declares, read ONCE (feature 276, FR-002): the link test used to re-read and re-scan the target
    page for every link into it - 544 scans for one page - and a page's ids do not change within a run."""
    key = str(path)
    if key not in _IDS:
        _IDS[key] = set(_ID.findall(path.read_text(encoding="utf-8")))
    return _IDS[key]


def broken_links(page: pathlib.Path) -> list[str]:
    """Every link in `page` that names a missing file or a missing id - the test below, lifted for the planted case."""
    text = page.read_text(encoding="utf-8")
    bad = []
    for href in _HREF.findall(text):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        target, _, frag = href.partition("#")
        if target:
            path = RecordPath(os.path.normpath(page.parent / target))
            if not path.exists():
                bad.append(f"{href}: no such file")
                continue
            if path.suffix != ".html":
                continue  # a Markdown target's anchors are GitHub's to render; the file existing is the check here
            ids = _ids_of(path)
        else:
            ids = _ids_of(page)
        if frag and frag not in ids:
            bad.append(f"{href}: no id {frag!r} in {target or page.name}")
    return bad


@pytest.mark.parametrize("page", _pages(), ids=lambda p: str(p.relative_to(RESEARCH_DIR)))
def test_every_link_in_a_record_page_resolves(page: pathlib.Path) -> None:
    bad = broken_links(page)
    assert not bad, f"{page.name}:\n" + "\n".join(bad[:20])


def test_a_broken_link_and_a_missing_id_are_reported(tmp_path: pathlib.Path) -> None:
    (tmp_path / "b.html").write_text('<h2 id="here">x</h2>')
    (tmp_path / "a.html").write_text('<a href="b.html#here">ok</a> <a href="b.html#gone">x</a> <a href="nope.html">y</a> <p id="self"></p><a href="#self">z</a>')
    assert broken_links(tmp_path / "a.html") == ["b.html#gone: no id 'gone' in b.html", "nope.html: no such file"]


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
_TOKEN_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./-")


@functools.cache
def md_tokens(text: str) -> tuple[str, ...]:
    """Every `_MD_TOKEN` match in `text`, in order - what `_MD_TOKEN.finditer(text)` yields, found ONCE per text for the
    two tests that ask (feature 276, FR-002).

    WHY NOT THE PLAIN SCAN. The pattern opens with a lookbehind, so it is tried at every position of every tracked file,
    twice (1.3 s a test). A match is made only of `_TOKEN_CHARS` and ends in `.md`, so it lies inside the run of those
    characters around some `.md`; the pattern is run over that run alone, from its first character to one past its last.
    `finditer(text, pos, endpos)` still reads the character before `pos` for the lookbehind, and the one extra character
    lets `\b` see what follows, so each run yields exactly the matches the whole-text scan found there."""
    out: list[str] = []
    at = text.find(".md")
    done = -1
    while at != -1:
        lo = at
        while lo > 0 and text[lo - 1] in _TOKEN_CHARS:
            lo -= 1
        hi = at + 3
        while hi < len(text) and text[hi] in _TOKEN_CHARS:
            hi += 1
        if lo > done:
            out += [m.group(1) for m in _MD_TOKEN.finditer(text, lo, min(hi + 1, len(text)))]
            done = hi
        at = text.find(".md", hi)
    return tuple(out)


@functools.cache
def tracked_texts() -> dict[str, str]:
    """Every tracked file that reads as UTF-8, read ONCE per process for the tests that scan them all (feature 276)."""
    root = _repo_root()
    out: dict[str, str] = {}
    for rel in subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n"):
        if not rel:
            continue
        try:
            out[rel] = (root / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError, OSError:
            continue
    return out


_SKILL = "/".join([".claude", "skills", "diagram"])


def _repo_root() -> pathlib.Path:
    return pathlib.Path(RESEARCH_DIR).resolve().parents[3]


def _as_the_page_reads_it(containing_rel: str) -> pathlib.PurePosixPath:
    """The directory a relative token in this file is read from.

    For a FRAGMENT of the record (feature 258, `research/<page>/...`) that is the directory of the page
    it assembles into, not the fragment's own: the fragment's text becomes the page's text, and a
    `../x.md` written for `research/contents.json#compounds` is one level up from `research/contents.json#compounds`. Reading
    it from the fragment's directory reports a link that resolves perfectly on the page a reader opens.
    """
    here = pathlib.PurePosixPath(containing_rel).parent
    record = pathlib.PurePosixPath(f"{_SKILL}/research")
    return here.parent if here != record and record in here.parents else here


def _resolves_to_converted(token: str, containing_rel: str) -> bool:
    """FR-013's rule: a token is in scope only if it RESOLVES - against its file's directory, or as a skill-root or
    repository-root path - to one of the 16 converted files."""
    record = f"{_SKILL}/research/"
    for base in (_as_the_page_reads_it(containing_rel), pathlib.PurePosixPath(_SKILL), pathlib.PurePosixPath(".")):
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
    texts: dict[str, str] = {}
    for rel, text in tracked_texts().items():
        if rel.startswith(("specs/", "scripts/fixtures/")) or rel == f"{_SKILL}/research/README.md":
            continue
        # A RECORDED FIXTURE IS HISTORY, NOT A POINTER (2026-09-07): `scripts/fixtures/` holds guard firings
        # replayed by the guard suites - the commands sessions actually typed, verbatim, some of them naming
        # research files that were Markdown at the time. Feature 204 landed one and turned main red here; the
        # commands are quotations of what happened, like a spec, and are never followed as links.
        texts[rel] = text
    hits = md_token_hits(texts)
    assert not hits, "tokens naming the deleted Markdown:\n" + "\n".join(hits[:20])


def md_token_hits(texts: dict[str, str]) -> list[str]:
    """`rel: token` for every `.md` token resolving to a converted record file. A text with no `.md` in it is skipped
    before the pattern runs (feature 276, FR-002): `_MD_TOKEN` cannot match without that literal."""
    hits = []
    for rel, text in texts.items():
        for token in md_tokens(text):
            if _resolves_to_converted(token, rel):
                hits.append(f"{rel}: {token}")
    return hits


def test_md_tokens_equal_the_whole_text_scan() -> None:
    """Feature 276: the per-run scan yields exactly the whole-text `finditer`'s tokens - over the boundaries the pattern
    names (a path before it, a word character after it, a non-ASCII word character either side, the text's ends, two
    tokens in one run) and over every tracked text."""
    edge = "a.md x/b.md ./c.md ../d/e.md f.mdx ōg.md h.mdō i.md.md j.md/k.md -l.md (m.md) n.md"
    for text in (edge, "", ".md", "z.md", edge + "\n" + edge, "x\n.md\ny.md\n"):
        assert md_tokens(text) == tuple(m.group(1) for m in _MD_TOKEN.finditer(text)), text[:80]
    # EVERY TRACKED TEXT, AGAINST THE PATTERN RUN LINE BY LINE (feature 278, FR-014). The whole-text scan here cost 4.6 s of
    # `make quick`. A token holds no newline, and the pattern's lookbehind and `\b` read a newline as they read any other
    # non-token character - so a text's tokens are its lines' tokens in order, and a line without `.md` has none. The
    # edge strings above hold the whole-text form to the same answer, newlines included.
    found = 0
    for text in tracked_texts().values():
        want = tuple(m.group(1) for line in text.split("\n") if ".md" in line for m in _MD_TOKEN.finditer(line))
        assert md_tokens(text) == want, text[:80]
        found += len(want)
    assert found > 100, "non-vacuity: the tracked corpus names Markdown files"


def test_a_token_naming_a_converted_file_is_reported() -> None:
    texts = {"docs/a.md": f"see {_SKILL}/research/water.md for it", "docs/b.md": "nothing here", "docs/c.py": "x = 1"}
    assert md_token_hits(texts) == [f"docs/a.md: {_SKILL}/research/water.md"]


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
#: tokens they were recorded with. `research/README.md` WAS exempt here and no longer is - it is the GM's
#: to write (constitution XVII), it named fourteen retired files, and the GM authorized the correction in
#: their own words on 2026-09-12 ("I authorize you to fix the research readme"), so it is now held to the
#: same rule as everything else.
_RETIRED_EXEMPT_PREFIXES = ("specs/", "scripts/fixtures/")
#: and this file itself, which necessarily names them: it is where the rule and its own self-test live.
_RETIRED_EXEMPT_FILES = {f"{_SKILL}/tests/fixtures/classes_before_189.json", f"{_SKILL}/tests/interactive/test_record.py"}


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
        for token in md_tokens(text):  # shared with the test above (feature 276, FR-002)
            if names_a_retired_rule_file(token, rel, exists):
                hits.append(f"{rel}: {token}")
                break
    return hits


def test_no_tracked_file_names_a_retired_rule_file() -> None:
    """Feature 229: the `settlements/` rule files are gone and nothing points at them - by path or by bare basename."""
    root = _repo_root()
    tracked = [f for f in subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n") if f]
    hits = retired_rule_file_hits(tracked_texts(), set(tracked))
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
