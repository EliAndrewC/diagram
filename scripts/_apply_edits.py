#!/usr/bin/env python3
"""Apply the ready-made edits a check agent's report ends its findings with (feature 250 D15, research R6).

WHY. On the last three measured pages the largest single cost was the APPLY step of a check session: 12 to 27
turns a group, each re-reading a context of 60,000 to 90,000 tokens, most of them spent reading a file so that
`Edit` would accept it and then typing the replacement the report had already worded (R6). `quote-check` and
`record-format` now end every finding they can word with an EDIT block, and this applies a whole report in one
command; the session's turns go to the findings that need judgment.

THE BLOCKS, as the two contracts write them:

    EDIT <origin path>
    <<<
    the exact text now in the file
    ===
    the text that replaces it
    >>>

    GLOSSARY <term> | <variant>, <variant> | <definition>

A block is applied only when its old text occurs EXACTLY ONCE in its file - never a guess at which occurrence was
meant - and only under the record (`research/`) or a modal's class file (`interactive/classes/`, D17); anything else is REFUSED with the reason, and the session applies
it by hand. A glossary term already on file is skipped. `--skip 2,5` leaves those blocks alone (the session
disagrees with them); `--dry-run` reports without writing. The input is the agent's reply saved as text, or its
transcript (`.jsonl`, or the `.output` link the dispatch names), whose last reply is read.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# A block may sit indented under a numbered finding, every line of it carrying the same indent; the indent is
# the list's, not the file's, and is taken off each line of the old and new text. record-format wrote its first
# cities/fabric 140 report that way and the unindented pattern found no block in it at all (feature 250 T55).
EDIT = re.compile(
    r"^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n(?P=ind)<<<\n(?P<old>.*?)\n(?P=ind)===\n(?P<new>.*?)\n?(?P=ind)>>>[ \t]*$",
    re.S | re.M,
)
GLOSSARY = re.compile(r"^[ \t]*GLOSSARY[ \t]+(?P<term>[^|\n]+?)[ \t]*\|[ \t]*(?P<variants>[^|\n]*?)[ \t]*\|[ \t]*(?P<def>[^\n]+?)[ \t]*$", re.M)
RECORD = ".claude/skills/diagram/research/"
# D17 (R8, recommendation 1): a drifted modal's prose is its Kind class's docstring - thirteen hand edits on `fields`
MODALS = ".claude/skills/diagram/l7r/diagram/interactive/classes/"
ROOTS = (RECORD, MODALS)
TERMS = ".claude/skills/diagram/l7r/diagram/interactive/assets/glossary/"


def reply_of(path: pathlib.Path) -> str:
    """The report's text: the file itself, or the last assistant reply in a transcript."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix not in (".jsonl", ".output"):
        return text
    last = ""
    for line in text.splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        if rec.get("type") == "assistant" and isinstance(msg.get("content"), list):
            said = "".join(c.get("text", "") for c in msg["content"] if c.get("type") == "text")
            last = said or last
    return last


def dedent(text: str, indent: str) -> str:
    """The block's text without the indent of the list it sat in."""
    return "\n".join(line.removeprefix(indent) for line in text.split("\n")) if indent else text


def blocks(report: str) -> list[dict]:
    """Every EDIT and GLOSSARY block, in the report's order, numbered from 1."""
    found = [(m.start(), {"kind": "edit", "path": m["path"].strip(), "old": dedent(m["old"], m["ind"]), "new": dedent(m["new"], m["ind"])}) for m in EDIT.finditer(report)]
    found += [
        (m.start(), {"kind": "glossary", "term": m["term"].strip(), "variants": [v.strip() for v in m["variants"].split(",") if v.strip() not in ("", "-")], "def": m["def"].strip()})
        for m in GLOSSARY.finditer(report)
    ]
    return [{"n": n, **b} for n, (_, b) in enumerate(sorted(found, key=lambda f: f[0]), 1)]


def resolve(root: pathlib.Path, path: str) -> pathlib.Path | None:
    """The origin file, if it lies under the record; a path elsewhere is not this script's to write."""
    p = pathlib.Path(path)
    p = (p if p.is_absolute() else root / p).resolve()
    return p if any(p.is_relative_to(root / r) for r in ROOTS) else None


def apply_edit(root: pathlib.Path, b: dict, dry: bool) -> str:
    target = resolve(root, b["path"])
    if target is None:
        return f"REFUSED - {b['path']} is not under {RECORD} or {MODALS}"
    if not target.is_file():
        return f"REFUSED - no file {b['path']}"
    text = target.read_text(encoding="utf-8")
    count = text.count(b["old"])
    if count != 1:
        return f"REFUSED - the old text occurs {count} times in {target.name}, not once"
    if not dry:
        target.write_text(text.replace(b["old"], b["new"], 1), encoding="utf-8")
    return f"applied to {target.name}"


def slug(term: str) -> str:
    """The glossary's own filename rule, restated exactly (`glossary_source._encode`): the term as it is,
    case and spaces kept, with only `%` and `/` percent-encoded. A hyphenated lowercase slug wrote
    `7960-trunk-street.json` for `trunk street`, and `make glossary` refused it (feature 250)."""
    return term.replace("%", "%25").replace("/", "%2F")


def apply_term(root: pathlib.Path, b: dict, dry: bool) -> str:
    d = root / TERMS
    have = {json.loads(f.read_text(encoding="utf-8")).get("term", "").lower() for f in d.glob("*.json")}
    if b["term"].lower() in have:
        return f"skipped - '{b['term']}' is already a glossary term"
    # the term is always its own first variant: matching reads only `variants`, and a term given only its
    # plural (kidoban -> "kidobans", cities/fabric 2b) never matched the bare word and failed the record test
    entry = {"term": b["term"], "def": b["def"], "variants": [b["term"], *(v for v in b["variants"] if v != b["term"])]}
    if dry:
        return f"would add a file for {b['term']!r}"
    # the prefix is RESERVED under the host-wide lock (feature 265 FR-010): two queues adding terms at once never
    # take the same one; the reservation writes the file, here with its full text as the stub
    path = _reserve().reserve("glossary", b["term"], root, stub=json.dumps(entry, ensure_ascii=False, indent=1) + "\n")
    return f"added {path.name}"


def _reserve():  # noqa: ANN202
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("reserve_prefix", pathlib.Path(__file__).resolve().parent / "reserve-prefix.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("report", help="the agent's reply saved as text, or its transcript (.jsonl / .output)")
    ap.add_argument("--root", default=".", help="the clone root")
    ap.add_argument("--skip", default="", help="block numbers to leave alone, e.g. 2,5")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    found = blocks(reply_of(pathlib.Path(args.report)))
    if not found:
        print("apply-edits: the report carries no EDIT or GLOSSARY block - apply its findings by hand", file=sys.stderr)
        return 2
    skip = {int(s) for s in args.skip.split(",") if s.strip()}
    refused = terms = 0
    for b in found:
        if b["n"] in skip:
            print(f"  {b['n']}. skipped (--skip)")
            continue
        said = apply_edit(root, b, args.dry_run) if b["kind"] == "edit" else apply_term(root, b, args.dry_run)
        refused += said.startswith("REFUSED")
        terms += said.startswith("added")
        print(f"  {b['n']}. {said}   ({b.get('path') or 'GLOSSARY ' + b['term']})")
    tail = " - then `make glossary`" if terms else ""
    print(f"apply-edits: {len(found)} block(s), {refused} refused{' (dry run, nothing written)' if args.dry_run else ''}{tail}")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
