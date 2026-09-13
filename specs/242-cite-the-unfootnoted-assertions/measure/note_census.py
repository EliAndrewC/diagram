"""What the record's footnotes are made of, counted from the citations pages themselves.

Feature 242 needs one number feature 238 never stated: how many of the absence notes 238 wrote say,
in so many words, that no query was ever run for that assertion. Those are backlog entries rather
than settled questions (research/CLAUDE.md: an absence note re-opens on anything that changes what
can be read), and whether they are in this feature's scope is decision D1 of its spec.

Counts the `.html` pages ONLY. `citations/<name>.js` is DERIVED from the page by `make citations`,
so a grep over both doubles every figure - which it did on the first attempt at this census.

Usage: python3 specs/242-cite-the-unfootnoted-assertions/measure/note_census.py [--record]
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent / ".claude" / "skills" / "diagram" / "research" / "citations"
RECORD = HERE.parent / "measurements.json"
COMMAND = "python3 specs/242-cite-the-unfootnoted-assertions/measure/note_census.py --record"

FORMS = {
    "citation-notes": re.compile(r'<li id="fn-\d+"><a href="http'),
    "absence-notes": re.compile(r"no publicly readable source \(searched \d{4}-\d{2}-\d{2}:"),
    "grounds-notes": re.compile(r"no source is owed:"),
    "absence-notes-never-searched": re.compile(r"no query of its own was run"),
}


def main() -> int:
    counts = dict.fromkeys(FORMS, 0)
    pages = sorted(ROOT.rglob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for name, pat in FORMS.items():
            counts[name] += len(pat.findall(text))

    print(f"{len(pages)} citations pages")
    for name, n in counts.items():
        print(f"  {name:32} {n:5}")
    settled = counts["absence-notes"] - counts["absence-notes-never-searched"]
    print(f"  {'absence notes WITH a real search':32} {settled:5}")

    if "--record" in sys.argv:
        rec = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        notes = {
            "citation-notes": "footnotes carrying a key link, a public page and a quoted passage",
            "absence-notes": "footnotes recording that no publicly readable source was found",
            "grounds-notes": "footnotes recording that no source is owed",
            "absence-notes-never-searched": "absence notes whose text says no query was ever run "
                                            "for that assertion - backlog, not a failed hunt",
        }
        for name, n in counts.items():
            rec[name] = {"command": COMMAND, "note": notes[name], "taken": "2026-09-13",
                         "unit": "notes", "value": n}
        RECORD.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nrecorded to {RECORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
