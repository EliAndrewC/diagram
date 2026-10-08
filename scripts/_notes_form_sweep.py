#!/usr/bin/env python3
"""A one-time sweep of the record's quotation form (feature 292, GM 2026-09-29) - kept for the record of what it did.

1. *"we should presume the source is in English unless ... stated otherwise, meaning that we should strike '(the
   source's own English)' from the end of the relevant footnotes."*
2. *"we should presume that all translations are done by this project unless explicitly stated otherwise, which allows
   us to simply say 'translated'."* Only the plain form - `translated from the <Language> by this project` - becomes
   `translated`; a translation that says more (`from the page's Japanese kundoku reading`) keeps its words, and is
   reported.

Over every hand-authored file of the record: the question fragments, their notes and the registry entries - never an
assembled page, which `make record` rewrites. `tests/interactive/test_footnotes.py` then holds the new form.

    _notes_form_sweep.py --root <repo> [--write]     without --write, reports what it would change
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

RECORD = "research"
#: `the Japanese`, `the Chinese (simplified)`, `the Classical Chinese`, `the Middle Korean` - a language named plainly.
_LANG = r"the (?:[a-z]+ )?(?:[A-Z][A-Za-z-]*\s)*?[A-Z][A-Za-z-]*(?: \([a-z ,]+\))?"  # `the classical Chinese` too
_TRANSLATED = re.compile(rf"\btranslated from {_LANG} by this project")
_OTHER = re.compile(r"\btranslated from [^;)]{0,80}? by this project")
#: `the source's own English` with any apostrophe the record writes it with - `'`, `&#x27;` or `’`. Not `the paper's own
#: English title`, which says something: the paper gives an English title of its own beside the original.
_S = r"the source(?:'|&#x27;|’)s own English"
_OWN = [
    (re.compile(rf" \({_S}\)"), ""),
    (re.compile(rf"\({_S}(?:;| -|,) "), "("),
    (re.compile(rf"[;,] {_S}(?= -)"), ""),
    (re.compile(rf"[;,] {_S}(?=\)|;|<!--|\.)"), ""),
    (re.compile(rf"\({_S}\. "), "("),
]
#: A gloss's own `translated by this project` - `(至今, translated by this project)` - is `translated` too.
_BY_US = re.compile(r"\btranslated by this project\b")


def files(root: pathlib.Path) -> list[pathlib.Path]:
    rec = root / RECORD
    out = [p for p in rec.rglob("[0-9]*.html") if not p.name.endswith(".originals.html") and "citations" not in p.parts]
    return sorted(set(out))


def sweep(text: str) -> tuple[str, list[str]]:
    """(the text in the new form, the translation notes left alone because they say more than the language)."""
    text = _BY_US.sub("translated", _TRANSLATED.sub("translated", text))
    for pattern, repl in _OWN:
        text = pattern.sub(repl, text)
    return text, [m.group(0) for m in _OTHER.finditer(text)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    changed, kept = 0, []
    for p in files(root):
        old = p.read_text(encoding="utf-8")
        new, left = sweep(old)
        kept += [f"{p.relative_to(root)}: {x}" for x in left]
        if new != old:
            changed += 1
            if args.write:
                p.write_text(new, encoding="utf-8")
    print(f"notes-form-sweep: {changed} file(s) {'rewritten' if args.write else 'would change'}; {len(kept)} translation note(s) kept for saying more than the language:")
    for k in kept:
        print(f"  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
