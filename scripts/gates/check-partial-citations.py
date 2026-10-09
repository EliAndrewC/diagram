#!/usr/bin/env python3
"""A footnote citing a source no one can wholly read stands only on a confirmed passage (feature 312, FR-019, FR-020).

WHY (the GM, 2026-10-02): *"if we cannot find these sources because we cited something that is paywalled, then we must, as
part of this feature, update our research findings to remove those as sources"* - and the record's rule, "a source that
cannot be read is not cited". A footnote may still quote a passage from the part that IS readable (an open abstract, the
GM's partial copy): it stands when `quote-check` confirmed that passage there, a confirmation recorded per footnote in
`research/partial-confirmations.jsonl` (`{"key", "note": "<notes file>#<note id>", "where", "date"}`).

THE SOURCES it holds: a registry key whose access state (feature 313's tags, `scripts/record/access_tags.py`) is `paywalled`,
`gm-partial` or `never-read`. Every footnote in `questions/*.notes.html` citing one with no confirmation is refused, each
named with the fix: confirm it (`make quote-verbatim` and `quote-check` on the readable part, then a line of
`partial-confirmations.jsonl`), or turn it into an absence note.

    check-partial-citations.py [ROOT]     exit 1 naming each unconfirmed footnote; run at the push and by the gate
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path[1:1] = [str((pathlib.Path(__file__).resolve().parent / _d).resolve()) for _d in ('../record',)]  # the moved scripts it imports (2026-10-08)

RECORD = pathlib.Path("research")
CONFIRMED = RECORD / "partial-confirmations.jsonl"
UNREADABLE = ("paywalled", "gm-partial", "never-read")
_NOTE = re.compile(r'<li data-note="([^"]+)">(.*?)</li>', re.S)
_KEY = re.compile(r"<code>([a-z0-9][a-z0-9-]*)</code>")


def unreadable_keys(root: pathlib.Path) -> dict[str, str]:
    import access_tags as tags  # noqa: PLC0415 - feature 313's derivation, the one answer to "what can be read"

    if not (root / tags.ACCESS).is_file():  # a tree with no access states (a push fixture) names no unreadable source
        return {}
    return {k: t.state for k, t in tags.every(tags.load(root)).items() if t.state in UNREADABLE and not k.startswith("download:")}


def confirmed(root: pathlib.Path) -> set[tuple[str, str]]:
    path = root / CONFIRMED
    out = set()
    for raw in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        try:
            x = json.loads(raw)
        except json.JSONDecodeError:
            continue
        out.add((x.get("key", ""), x.get("note", "")))
    return out


def findings(root: pathlib.Path, keys: dict[str, str], ok: set[tuple[str, str]]) -> list[str]:
    out = []
    for f in sorted((root / RECORD / "questions").glob("*.notes.html")):
        for note, body in _NOTE.findall(f.read_text(encoding="utf-8")):
            for key in dict.fromkeys(_KEY.findall(body)):
                where = f"{f.name}#{note}"
                if key in keys and (key, where) not in ok:
                    out.append(f"{where}: cites `{key}` ({keys[key]}) with no confirmed passage - confirm it from the readable part "
                               f"(make quote-verbatim, then quote-check) and record it in {CONFIRMED.name}, or make the note an absence note")
    return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = pathlib.Path(args[0] if args else ".").resolve()
    found = findings(root, unreadable_keys(root), confirmed(root))
    for line in found:
        print(f"check-partial-citations: {line}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
