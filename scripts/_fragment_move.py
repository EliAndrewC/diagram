#!/usr/bin/env python3
"""Move a fragment of the record and every pointer to it, in one change (feature 301, FR-015).

    make fragment-move FROM=research/water/120-reservoir-ponds.html TO=research/water/125-reservoir-ponds-tameike.html

The GM, 2026-10-01: a pointer names *"the source which is fed into and used to generate that HTML page"* - the fragment
- and a fragment's NAME carries its order and its heading id, so reordering a page or retitling a question renames it.
This does the rename with everything that names it:

  - the fragment, its `.notes.html` and its `.originals.html` (`git mv`, so history follows them);
  - its heading's `id`, when the new name carries a new one;
  - every pointer in the repository's tracked files (`research/<dir>/<old name>` -> the new), the modal `Entry:` lines
    among them;
  - every link inside the record that reached the question - `<page>.html#<old id>` from any page, `#<old id>` from its
    own - and the `about:` declarations and `confusables.json` entries that name it.

It refuses rather than guesses: a source that is not a question's fragment, a target that exists, a target whose name
is not `<prefix>-<heading id>.html`. `scripts/check-research-pointers.py` (gate and push) catches a move made by hand.

Usage: _fragment_move.py FROM TO [--root DIR] | --selftest
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path

SKILL = ".claude/skills/diagram"
RECORD = f"{SKILL}/research"
_NAME = re.compile(r"^(\d{3})-(.+)\.html$")
_HREF = re.compile(r'(href=")([^"#]*)(#[^"]*)?(")')
_ABOUT = re.compile(r"(<!-- about: )((?:[a-z-]+/)?[a-z-]+\.html)#([^\s]+)( -->)")


class MoveError(Exception):
    """A move that is refused, with what to do instead."""


def _inside(path: str) -> str:
    """A path given from anywhere, as it is inside the record: `water/120-x.html`."""
    path = path.replace(os.sep, "/")
    return path.split("research/", 1)[1] if "research/" in path else path


def _page_rel(page_dir: str) -> str:
    return "SOURCES.html" if page_dir == "sources" else f"{page_dir}.html"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def plan(root: Path, src: str, dst: str) -> tuple[str, str, str, str]:
    """(old inside path, new inside path, old heading id, new heading id) - or a refusal."""
    old, new = _inside(src), _inside(dst)
    record = root / RECORD
    old_m, new_m = _NAME.match(posixpath.basename(old)), _NAME.match(posixpath.basename(new))
    if old_m is None or not (record / old).is_file() or old.endswith((".notes.html", ".originals.html")):
        raise MoveError(f"FROM={src}: not a question's fragment in the record - name the `<prefix>-<heading id>.html` file")
    if new_m is None:
        raise MoveError(f"TO={dst}: a fragment is named `<prefix>-<heading id>.html` (three digits, then the heading's id)")
    if (record / new).exists():
        raise MoveError(f"TO={dst}: already exists - the move will not overwrite a question")
    if not (record / posixpath.dirname(new) / "_front.html").is_file():
        raise MoveError(f"TO={dst}: {posixpath.dirname(new)}/ is not a page of the record")
    return old, new, old_m.group(2), new_m.group(2)


def move(root: Path, src: str, dst: str) -> list[str]:
    """Do the move; return the files it changed (repository-relative)."""
    old, new, old_id, new_id = plan(root, src, dst)
    record = root / RECORD
    changed: list[str] = []
    for suffix in ("", ".notes", ".originals"):
        a = record / (old[: -len(".html")] + suffix + ".html")
        b = record / (new[: -len(".html")] + suffix + ".html")
        if a.is_file():
            _git(root, "mv", str(a.relative_to(root)), str(b.relative_to(root)))
            changed.append(str(b.relative_to(root)))
    question = record / new
    if old_id != new_id:
        text = question.read_text(encoding="utf-8")
        question.write_text(re.sub(rf'(<h[23] id="){re.escape(old_id)}(")', rf"\g<1>{new_id}\g<2>", text, count=1), encoding="utf-8")
    old_page, new_page = _page_rel(posixpath.dirname(old)), _page_rel(posixpath.dirname(new))
    changed += _repoint_record(record, old_page, old_id, new_page, new_id)
    changed += _repoint_tracked(root, f"research/{old}", f"research/{new}")
    return sorted(set(changed))


def _repoint_record(record: Path, old_page: str, old_id: str, new_page: str, new_id: str) -> list[str]:
    """Every link inside the record that reached the question, re-aimed: hrefs, `about:` declarations, confusables."""
    if old_page == new_page and old_id == new_id:
        return []
    changed: list[str] = []
    for frag in sorted(record.rglob("*.html")):
        rel = frag.relative_to(record).as_posix()
        if rel.startswith(("site/", "citations/")) or "/" not in rel:
            continue  # the build, and the built pages of old - never a fragment
        page_dir = rel.rsplit("/", 1)[0]
        while page_dir and not (record / page_dir / "_front.html").is_file():
            page_dir = page_dir.rsplit("/", 1)[0] if "/" in page_dir else ""
        here = posixpath.dirname(_page_rel(page_dir)) if page_dir else ""
        this_page = _page_rel(page_dir) if page_dir else ""
        text = frag.read_text(encoding="utf-8")

        def href(m: re.Match[str]) -> str:
            path, anchor = m.group(2), (m.group(3) or "")[1:]
            if anchor != old_id:
                return m.group(0)
            target = posixpath.normpath(posixpath.join(here, path)) if path else this_page
            if target != old_page:
                return m.group(0)
            if not path and new_page == this_page:
                return f"{m.group(1)}#{new_id}{m.group(4)}"
            return f"{m.group(1)}{posixpath.relpath(new_page, here or '.')}#{new_id}{m.group(4)}"

        def about(m: re.Match[str]) -> str:
            return f"{m.group(1)}{new_page}#{new_id}{m.group(4)}" if (m.group(2), m.group(3)) == (old_page, old_id) else m.group(0)

        new_text = _ABOUT.sub(about, _HREF.sub(href, text))
        if new_text != text:
            frag.write_text(new_text, encoding="utf-8")
            changed.append(str(frag))
    data = record / "confusables.json"
    if data.is_file():
        pairs = json.loads(data.read_text(encoding="utf-8"))
        moved = False
        for pair in pairs:
            for side in ("a", "b"):
                if pair[side] == f"{old_page}#{old_id}":
                    pair[side], moved = f"{new_page}#{new_id}", True
        if moved:
            data.write_text(json.dumps(pairs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            changed.append(str(data))
    return [str(Path(c).resolve().relative_to(record.parents[3].resolve())) for c in changed]


def _repoint_tracked(root: Path, old: str, new: str) -> list[str]:
    """Every tracked file outside the record naming the old fragment (the notes and originals beside it too)."""
    changed: list[str] = []
    stem_old, stem_new = old[: -len(".html")], new[: -len(".html")]
    for path in _git(root, "ls-files").splitlines():
        if path.startswith(f"{RECORD}/"):
            continue
        p = root / path
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if stem_old not in text:
            continue
        new_text = re.sub(re.escape(stem_old) + r"(?=(?:\.notes|\.originals)?\.html)", stem_new, text)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            changed.append(path)
    return changed


def selftest() -> int:
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rec = root / RECORD
        (rec / "water").mkdir(parents=True)
        (rec / "fields").mkdir()
        for page in ("water", "fields"):
            (rec / page / "_front.html").write_text("<main>", encoding="utf-8")
        (rec / "water" / "120-ponds.html").write_text('<h2 id="ponds">Ponds</h2><p>see <a href="#ponds">here</a></p>', encoding="utf-8")
        (rec / "water" / "120-ponds.notes.html").write_text('<li data-note="k">n</li>', encoding="utf-8")
        (rec / "fields" / "010-x.html").write_text('<h2 id="x">X</h2><a href="water.html#ponds">ponds</a> <a href="water.html#other">o</a>', encoding="utf-8")
        (rec / "confusables.json").write_text(json.dumps([{"a": "water.html#ponds", "b": "fields.html#x"}]), encoding="utf-8")
        (root / "code.py").write_text("# research/water/120-ponds.html says so; notes at research/water/120-ponds.notes.html\n", encoding="utf-8")
        subprocess.run(["git", "-C", td, "init", "-q"], check=True)
        subprocess.run(["git", "-C", td, "add", "-A"], check=True)
        for bad, why in ((("research/water/999-gone.html", "research/water/130-x.html"), "not a question"),
                         (("research/water/120-ponds.html", "research/contents.json#waterponds.html"), "is named"),
                         (("research/water/120-ponds.html", "research/fields/010-x.html"), "already exists"),
                         (("research/water/120-ponds.html", "research/nowhere/010-x.html"), "not a page")):
            try:
                move(root, *bad)
                raise AssertionError(f"{bad} was not refused")
            except MoveError as e:
                assert why in str(e), (bad, e)
        changed = move(root, "research/water/120-ponds.html", "research/water/125-reservoir-ponds.html")
        assert (rec / "water" / "125-reservoir-ponds.html").is_file() and (rec / "water" / "125-reservoir-ponds.notes.html").is_file()
        assert '<h2 id="reservoir-ponds">' in (rec / "water" / "125-reservoir-ponds.html").read_text(encoding="utf-8")
        assert 'href="#reservoir-ponds"' in (rec / "water" / "125-reservoir-ponds.html").read_text(encoding="utf-8"), "its own page's link"
        fields = (rec / "fields" / "010-x.html").read_text(encoding="utf-8")
        assert 'href="water.html#reservoir-ponds"' in fields and 'href="water.html#other"' in fields, "another page's link, and only that one"
        assert "water.html#reservoir-ponds" in (rec / "confusables.json").read_text(encoding="utf-8")
        code = (root / "code.py").read_text(encoding="utf-8")
        assert "research/water/125-reservoir-ponds.html" in code and "research/water/125-reservoir-ponds.notes.html" in code
        assert "code.py" in changed
    print("fragment-move selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    root = Path(argv[argv.index("--root") + 1]).resolve() if "--root" in argv else Path(".").resolve()
    if "--root" in argv:
        args.remove(argv[argv.index("--root") + 1])
    if len(args) != 2:
        print("usage: make fragment-move FROM=research/<page>/<prefix>-<id>.html TO=research/<page>/<prefix>-<id>.html", file=sys.stderr)
        return 2
    try:
        changed = move(root, args[0], args[1])
    except MoveError as e:
        print(f"fragment-move: {e}", file=sys.stderr)
        return 1
    print(f"fragment-move: {args[0]} -> {args[1]}; {len(changed)} file(s) changed:")
    print("\n".join(f"  {c}" for c in changed))
    print("then `make record` in .claude/skills/diagram, and commit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
