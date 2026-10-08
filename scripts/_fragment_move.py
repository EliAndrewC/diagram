#!/usr/bin/env python3
"""Move a question of the record and every pointer to it, in one change (features 301 FR-015, 303 FR-019).

    make fragment-move FROM=research/questions/0412-reservoir-ponds.html TO=research/questions/0412-reservoir-ponds-tameike.html

The GM, 2026-10-01: a pointer names *"the source which is fed into and used to generate that HTML page"* - the fragment.
Since feature 303 a question is one STEM, `NNNN-<slug>`, whose slug is its research page's heading id (its drawing
page's, for a question that has none), so retitling a question renames its stem - and a renumbering moves it to a free
number. This does the move with everything that names it:

  - every file of the stem - the research page, the drawing page, and the `.notes.html` and `.originals.html` beside
    each (`git mv`, so history follows them);
  - the heading's `id`, when the new slug is a new one;
  - every link inside the record that reached it (`NNNN-<slug>[.drawing].html[#id]`, and `#<old id>` on its own page),
    the `about:` markers naming the stem, and the `confusables.json` entries;
  - every pointer in the repository's tracked files, the modal `Entry:` lines among them, and the migration mapping
    (`research/moved-303.json`), so a late pointer is told the current name.

It refuses rather than guesses: a source that is not a question's page, a target name that is not `NNNN-<slug>.html`
(or `.drawing.html` for a drawing-only question), a number already another question's. `check-research-pointers.py`
(gate and push) catches a move made by hand.

Usage: _fragment_move.py FROM TO [--root DIR] | --selftest
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RECORD = "research"
QUESTIONS = "questions"
_NAME = re.compile(r"^(\d{4})-([^./\s]+)(\.drawing)?\.html$")
_SUFFIXES = ("", ".notes", ".originals", ".drawing", ".drawing.notes", ".drawing.originals")


class MoveError(Exception):
    """A move that is refused, with what to do instead."""


def _name(path: str) -> str:
    return path.replace(os.sep, "/").rsplit("/", 1)[-1]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def plan(root: Path, src: str, dst: str) -> tuple[str, str, str, str]:
    """(old stem, new stem, old heading id, new heading id) - or a refusal."""
    qdir = root / RECORD / QUESTIONS
    old, new = _name(src), _name(dst)
    old_m, new_m = _NAME.match(old), _NAME.match(new)
    if old_m is None or not (qdir / old).is_file():
        raise MoveError(f"FROM={src}: not a question's page in research/questions/ - name its `NNNN-<slug>.html`")
    if new_m is None or bool(new_m.group(3)) != bool(old_m.group(3)):
        raise MoveError(f"TO={dst}: a question is named `NNNN-<slug>.html` (`.drawing.html` for a drawing-only question), as FROM is")
    if old_m.group(3) and (qdir / f"{old_m.group(1)}-{old_m.group(2)}.html").is_file():
        raise MoveError(f"FROM={src}: a drawing page beside its research page moves with it - name the research page")
    old_stem, new_stem = f"{old_m.group(1)}-{old_m.group(2)}", f"{new_m.group(1)}-{new_m.group(2)}"
    if old_stem == new_stem:
        raise MoveError(f"TO={dst}: the same name as FROM")
    taken = [n for n in os.listdir(qdir) if n.startswith(f"{new_m.group(1)}-") and not n.startswith(f"{old_stem}.")]
    if taken:
        raise MoveError(f"TO={dst}: number {new_m.group(1)} is already {taken[0]} - take a free one from `make reserve KIND=question`")
    return old_stem, new_stem, old_m.group(2), new_m.group(2)


def move(root: Path, src: str, dst: str) -> list[str]:
    """Do the move; return the files it changed (repository-relative)."""
    old, new, old_id, new_id = plan(root, src, dst)
    qdir = root / RECORD / QUESTIONS
    changed: list[str] = []
    for suffix in _SUFFIXES:
        a, b = qdir / f"{old}{suffix}.html", qdir / f"{new}{suffix}.html"
        if a.is_file():
            _git(root, "mv", str(a.relative_to(root)), str(b.relative_to(root)))
            changed.append(str(b.relative_to(root)))
    owner = qdir / f"{new}.html" if (qdir / f"{new}.html").is_file() else qdir / f"{new}.drawing.html"
    if old_id != new_id:
        text = owner.read_text(encoding="utf-8")
        owner.write_text(re.sub(rf'(<h[23] id="){re.escape(old_id)}(")', rf"\g<1>{new_id}\g<2>", text, count=1), encoding="utf-8")
    changed += _repoint_record(root, old, new, old_id, new_id, owner.name)
    changed += _repoint_tracked(root, old, new)
    return sorted(set(changed))


def _repoint_record(root: Path, old: str, new: str, old_id: str, new_id: str, owner: str) -> list[str]:
    """Every link inside the record that reached the question, re-aimed; its `about:` markers; the confusables."""
    record = root / RECORD
    link = re.compile(rf'(href="){re.escape(old)}((?:\.drawing)?\.html)(#[^"]*)?(")')
    changed: list[str] = []
    for frag in sorted((record / QUESTIONS).glob("*.html")):
        text = frag.read_text(encoding="utf-8")

        def href(m: re.Match[str]) -> str:
            anchor = m.group(3) or ""
            if anchor == f"#{old_id}" and m.group(2) == ".html" or anchor == f"#{old_id}" and owner.endswith(".drawing.html"):
                anchor = f"#{new_id}"
            return f"{m.group(1)}{new}{m.group(2)}{anchor}{m.group(4)}"

        new_text = link.sub(href, text).replace(f"<!-- about: {old} -->", f"<!-- about: {new} -->")
        if frag.name == owner:
            new_text = new_text.replace(f'href="#{old_id}"', f'href="#{new_id}"')
        if new_text != text:
            frag.write_text(new_text, encoding="utf-8")
            changed.append(str(frag.relative_to(root)))
    data = record / "confusables.json"
    if data.is_file():
        pairs = json.loads(data.read_text(encoding="utf-8"))
        moved = False
        for pair in pairs:
            for side in ("a", "b"):
                file, _, anchor = pair[side].partition("#")
                m = re.fullmatch(rf"{re.escape(old)}((?:\.drawing)?\.html)", file)
                if m:
                    anchor = new_id if anchor == old_id and f"{new}{m.group(1)}" == owner else anchor
                    pair[side], moved = f"{new}{m.group(1)}#{anchor}", True
        if moved:
            data.write_text(json.dumps(pairs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            changed.append(str(data.relative_to(root)))
    mapping = record / "moved-303.json"
    if mapping.is_file():
        text = mapping.read_text(encoding="utf-8")
        new_text = re.sub(rf"\bquestions/{re.escape(old)}(?=[.\"])", f"questions/{new}", text)
        if new_text != text:
            mapping.write_text(new_text, encoding="utf-8")
            changed.append(str(mapping.relative_to(root)))
    return changed


def _repoint_tracked(root: Path, old: str, new: str) -> list[str]:
    """Every tracked file outside the record naming the stem - any of its pages, notes or originals."""
    changed: list[str] = []
    stem = re.compile(rf"\bresearch/{QUESTIONS}/{re.escape(old)}(?=(?:\.drawing)?(?:\.notes|\.originals)?\.html)")
    for path in _git(root, "ls-files").splitlines():
        if path.startswith(f"{RECORD}/"):
            continue
        p = root / path
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if old not in text:
            continue
        new_text = stem.sub(f"research/{QUESTIONS}/{new}", text)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            changed.append(path)
    return changed


def selftest() -> int:
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        q = root / RECORD / QUESTIONS
        q.mkdir(parents=True)
        (q / "0120-ponds.html").write_text('<h2 id="ponds">Ponds</h2><p>see <a href="#ponds">here</a> <a href="0120-ponds.drawing.html">drawn</a></p>', encoding="utf-8")
        (q / "0120-ponds.notes.html").write_text('<li data-note="k">n</li>', encoding="utf-8")
        (q / "0120-ponds.drawing.html").write_text('<h2 id="drawn-ponds">Drawn</h2><a href="0120-ponds.html#ponds">p</a>', encoding="utf-8")
        (q / "0121-more.drawing.html").write_text('<h2 id="more">M</h2>\n<!-- about: 0120-ponds -->', encoding="utf-8")
        (q / "0130-x.html").write_text('<h2 id="x">X</h2><a href="0120-ponds.html#ponds">ponds</a> <a href="0120-ponds.html#other">o</a>', encoding="utf-8")
        (q / "0140-alone.drawing.html").write_text('<h2 id="alone">A</h2>', encoding="utf-8")
        (root / RECORD / "confusables.json").write_text(json.dumps([{"a": "0120-ponds.html#ponds", "b": "0130-x.html#x"}]), encoding="utf-8")
        (root / RECORD / "moved-303.json").write_text(json.dumps({"files": {"water/120-ponds.html": "questions/0120-ponds.html"}}), encoding="utf-8")
        (root / "code.py").write_text("# research/questions/0120-ponds.html says so; notes at research/questions/0120-ponds.notes.html\n", encoding="utf-8")
        subprocess.run(["git", "-C", td, "init", "-q"], check=True)
        subprocess.run(["git", "-C", td, "add", "-A"], check=True)
        for bad, why in (
            (("research/questions/0999-gone.html", "research/questions/0998-x.html"), "not a question's page"),
            (("research/questions/0120-ponds.html", "research/questions/ponds.html"), "is named"),
            (("research/questions/0120-ponds.html", "research/questions/0130-ponds.html"), "already 0130-x.html"),
            (("research/questions/0120-ponds.drawing.html", "research/questions/0120-p.drawing.html"), "moves with it"),
            (("research/questions/0120-ponds.html", "research/questions/0120-ponds.html"), "the same name"),
        ):
            try:
                move(root, *bad)
                raise AssertionError(f"{bad} was not refused")
            except MoveError as e:
                assert why in str(e), (bad, e)
        changed = move(root, "research/questions/0120-ponds.html", "research/questions/0125-reservoir-ponds.html")
        for f in ("0125-reservoir-ponds.html", "0125-reservoir-ponds.notes.html", "0125-reservoir-ponds.drawing.html"):
            assert (q / f).is_file(), f
        page = (q / "0125-reservoir-ponds.html").read_text(encoding="utf-8")
        assert '<h2 id="reservoir-ponds">' in page and 'href="#reservoir-ponds"' in page and 'href="0125-reservoir-ponds.drawing.html"' in page
        assert 'href="0125-reservoir-ponds.html#reservoir-ponds"' in (q / "0125-reservoir-ponds.drawing.html").read_text(encoding="utf-8")
        assert "<!-- about: 0125-reservoir-ponds -->" in (q / "0121-more.drawing.html").read_text(encoding="utf-8")
        x = (q / "0130-x.html").read_text(encoding="utf-8")
        assert 'href="0125-reservoir-ponds.html#reservoir-ponds"' in x and 'href="0125-reservoir-ponds.html#other"' in x
        assert "0125-reservoir-ponds.html#reservoir-ponds" in (root / RECORD / "confusables.json").read_text(encoding="utf-8")
        assert "questions/0125-reservoir-ponds.html" in (root / RECORD / "moved-303.json").read_text(encoding="utf-8")
        code = (root / "code.py").read_text(encoding="utf-8")
        assert "research/questions/0125-reservoir-ponds.html" in code and "research/questions/0125-reservoir-ponds.notes.html" in code
        assert "code.py" in changed
        move(root, "research/questions/0140-alone.drawing.html", "research/questions/0140-on-its-own.drawing.html")
        assert '<h2 id="on-its-own">' in (q / "0140-on-its-own.drawing.html").read_text(encoding="utf-8"), "a drawing-only question's slug is its heading"
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
        print("usage: make fragment-move FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html", file=sys.stderr)
        return 2
    try:
        changed = move(root, args[0], args[1])
    except MoveError as e:
        print(f"fragment-move: {e}", file=sys.stderr)
        return 1
    print(f"fragment-move: {args[0]} -> {args[1]}; {len(changed)} file(s) changed:")
    print("\n".join(f"  {c}" for c in changed))
    print("then `make record` at the repository root, and commit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
