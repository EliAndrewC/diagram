#!/usr/bin/env python3
"""Which translated quotations owe a `translation-check` - the pairs whose translation or original is new (feature 292).

WHY. The GM, 2026-09-29: *"it makes sense for there to be a subagent that checks that our translation is good when
either the text being quoted has changed or the translation has changed. And then otherwise that check doesn't need to
run."* So the question is asked of the record, mechanically: every (translation, original) pair in the questions' notes
now, against every pair at the merge base with origin/main. A pair that exists now and did not exist ANYWHERE then is
owed; a pair that only moved - a question renamed, two questions merged - is not, because the comparison is across the
whole record rather than file by file.

A pair is read from a notes file with its originals put back (`.originals.html`, feature 292; before the split the
originals were inline, and the base is read either way), and paired by `_quote_verbatim.passages`, the one reader of the
translated-quotation form.

    _translation_owed.py --root <repo>                       every owed pair, one line each, and a count
    _translation_owed.py --root <repo> --q 0412              only that question's, as the translation-check reads them
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _quote_verbatim as qv  # noqa: E402
import _style_prepass as sp  # noqa: E402

RECORD = ".claude/skills/diagram/research"
_NOTE = re.compile(r'<li data-note="([^"]+)">(.*?)</li>', re.S)
_TOKEN = re.compile(r'<span class="orig" data-orig="([^"]+)"></span>')
_STORED = re.compile(r'<li data-orig="([^"]+)">(.*?)</li>', re.S)


def restore(notes: str, originals: str) -> str:
    """The notes with their originals inline again, as the form was before the split (unwrapped)."""
    table = dict(_STORED.findall(originals))
    return _TOKEN.sub(lambda m: table.get(m.group(1), ""), notes)


def pairs(notes: str, originals: str) -> list[tuple[str, str, str, str]]:
    """(note key, language, translation, original) for every translated passage of one notes file."""
    out = []
    for key, body in _NOTE.findall(restore(notes, originals)):
        for p in qv.passages(qv._strip(body)):
            if p.get("original"):
                out.append((key, p.get("language", ""), p["quote"], p["original"]))
    return out


def _notes_files(names: list[str]) -> list[str]:
    return sorted(n for n in names if n.startswith(RECORD + "/") and n.endswith(".notes.html") and "/citations/" not in n)


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False).stdout


def record_pairs(root: pathlib.Path, rev: str | None) -> dict[tuple[str, str], list[tuple[str, str, str, str]]]:
    """{(translation, original): [(notes file, key, language, ...)]} across the whole record at `rev` (None: the tree)."""
    if rev is None:
        files = _notes_files([str(p.relative_to(root)) for p in (root / RECORD).rglob("*.notes.html")])
        read = lambda f: (root / f).read_text(encoding="utf-8") if (root / f).is_file() else ""  # noqa: E731
    else:
        files = _notes_files(_git(root, "ls-tree", "-r", "--name-only", rev, "--", RECORD).split())
        read = lambda f: _git(root, "show", f"{rev}:{f}")  # noqa: E731
    out: dict[tuple[str, str], list[tuple[str, str, str, str]]] = {}
    for f in files:
        notes = read(f)
        for key, lang, quote, original in pairs(notes, read(f[: -len(".notes.html")] + ".originals.html")):
            out.setdefault((quote, original), []).append((f, key, lang, quote))
        # a term glossed in our own words (feature 292: `垣根 (kakine, "hedge")`) is a translation too - the meaning
        # against the characters - in the question and in its notes
        for chars, reading, meaning in sp.glosses(read(f[: -len(".notes.html")] + ".html")) + sp.glosses(notes):
            out.setdefault((f'{meaning} (read {reading})', chars), []).append((f, "a term's gloss", "", meaning))
    return out


def owed(root: pathlib.Path) -> list[tuple[str, str, str, str, str]]:
    """(notes file, key, language, translation, original) for each pair now that the merge base does not hold."""
    base = _git(root, "merge-base", "HEAD", "origin/main").strip()
    then = set(record_pairs(root, base)) if base else set()
    return sorted((where[0][0], where[0][1], where[0][2], q, o) for (q, o), where in record_pairs(root, None).items() if (q, o) not in then)


def report(rows: list[tuple[str, str, str, str, str]]) -> str:
    lines = [f"translation-owed: {len(rows)} translated quotation(s) new or changed since the merge base - each owes a translation-check"]
    for f, key, lang, quote, original in rows:
        lines += [f"== {f} - `{key}` ({lang})", f"  TRANSLATION: {quote}", f"  ORIGINAL:    {original}"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--q", default="", help="only these questions' pairs: a number (`0412`) or a page's file name (feature 303)")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    rows = owed(root)
    if args.q:
        from _hm_record import fragments_for  # noqa: PLC0415

        mine = {r for r in fragments_for(args.q, str(root)) if r.endswith(".notes.html")}
        rows = [r for r in rows if r[0] in mine]
    print(report(rows), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
