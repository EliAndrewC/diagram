#!/usr/bin/env python3
"""Anchored edits to one file, EACH EDIT ITS OWN WRITE (feature 236, the GM's item 1).

WHY THIS EXISTS. `Edit` is still the default and this does not replace it (root CLAUDE.md, "Edit
files with `Edit`"). This is for the sweep that genuinely must be scripted - the same mechanical
change over many files - and it exists because the ad-hoc form of that script cost a whole session's
worth of rework three times in one day. The failing shape was always the same: a patch script
accumulated every edit in memory and wrote the file at the end, so ONE anchor that no longer matched
- usually a cosmetic sentence somebody had already reflowed - discarded the substantive edits beside
it. Nothing was reported as lost, because the script had "succeeded" at the edits it made.

So the two properties here are the whole point:

  1. EACH EDIT IS ITS OWN WRITE. An anchor that matches zero times, or more than once, is REPORTED
     and SKIPPED, and every other edit in the batch still lands. A batch is not a transaction: these
     edits are independent by construction, and treating them as one unit is what threw work away.
  2. ANCHORS MATCH WHITESPACE-INSENSITIVELY. Four of the six anchor misses in the record spanned a
     LINE WRAP - the anchor was copied from a rendered paragraph and the file has it broken over two
     lines (`specs/236-catch-mistakes-early-and-cheaply/research.md` R7). Exact matching leaves the
     commonest miss in place.

An anchor that matches MORE than once is skipped rather than applied to the first hit: which one the
caller meant is exactly the thing the script cannot know, and guessing writes the wrong place
silently.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys


def anchor_regex(anchor: str) -> re.Pattern[str]:
    """`anchor` as a pattern in which any run of whitespace matches any other run.

    A line wrap is whitespace, so an anchor copied from rendered prose matches the file's own
    wrapped copy of it. Nothing else about the text is loosened: every non-space character is
    escaped, so an anchor carrying `(`, `*` or `.` matches those characters literally.
    """
    return re.compile(r"\s+".join(re.escape(w) for w in anchor.split()))


def _reindent(replacement: str, prefix: str) -> str:
    """`replacement`'s continuation lines given the indent the matched text stood at.

    THE BUG THIS FIXES, from the session that motivated this file: an anchor whose match began at a
    WORD rather than at the start of a line, replaced by multi-line text, produced continuation lines
    flush against the left margin inside an indented block. The first line is not touched (it
    continues whatever is already on that line); a continuation line that carries its own leading
    whitespace is not touched either, because the caller has then said what it wants.
    """
    if not prefix or "\n" not in replacement:
        return replacement
    head, *rest = replacement.split("\n")
    return "\n".join([head] + [(line if (not line or line[:1].isspace()) else prefix + line) for line in rest])


def apply_edits(path: str | pathlib.Path, edits: list[tuple[str, str]]) -> tuple[list[str], int]:
    """Apply each (anchor, replacement) to `path` independently. Returns (report lines, skipped)."""
    p = pathlib.Path(path)
    report: list[str] = []
    skipped = 0
    for anchor, replacement in edits:
        text = p.read_text()            # re-read per edit: an earlier edit may have moved this one
        hits = list(anchor_regex(anchor).finditer(text))
        label = " ".join(anchor.split())[:60]
        if len(hits) != 1:
            skipped += 1
            report.append(f"SKIPPED ({len(hits)} matches): {label}")
            continue
        m = hits[0]
        line_start = text.rfind("\n", 0, m.start()) + 1
        # the LINE'S OWN indent, not everything before the match: an anchor starting at a word inside
        # `    - a point ...` must continue at the block's indent, and the earlier form (only a
        # wholly-blank prefix counted) left exactly that case flush against the margin
        indent = re.match(r"[ \t]*", text[line_start:m.start()]).group(0)
        body = _reindent(replacement, indent)
        # AN ANCHOR IGNORES ITS OWN LEADING WHITESPACE, so a caller that copied an indented line into
        # BOTH the anchor and the replacement would have that indent applied twice - the match begins
        # at the first non-space character, and the replacement carries the indent again. Found by
        # using this on `_hm_make.py` an hour after writing it: the patched line came out at sixteen
        # spaces and Python refused the file.
        if indent and text[line_start:m.start()] == indent:
            body = re.sub(r"^[ \t]+", "", body, count=1)
        p.write_text(text[:m.start()] + body + text[m.end():])
        report.append(f"applied: {label}")
    return report, skipped


def selftest() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "x.md"
        # the motivating case: the middle anchor is gone, and the other two must still land
        f.write_text("alpha one\nbeta two\ngamma three\n")
        report, skipped = apply_edits(f, [("alpha one", "ALPHA"), ("nowhere at all", "X"), ("gamma three", "GAMMA")])
        assert skipped == 1, report
        assert f.read_text() == "ALPHA\nbeta two\nGAMMA\n", f.read_text()
        assert report[0].startswith("applied:") and report[1].startswith("SKIPPED (0 matches)"), report
        # a wrapped anchor
        f.write_text("the sections and keys the new text\nwas written from stay put\n")
        report, skipped = apply_edits(f, [("keys the new text was written from", "keys it came from")])
        assert skipped == 0 and "keys it came from" in f.read_text(), (report, f.read_text())
        # an anchor that matches twice is skipped, not guessed at
        f.write_text("same line\nsame line\n")
        report, skipped = apply_edits(f, [("same line", "different")])
        assert skipped == 1 and f.read_text() == "same line\nsame line\n", (report, f.read_text())
        # a match starting at a word keeps the block's indent on continuation lines
        f.write_text("    - a point that needs more\n")
        apply_edits(f, [("a point that needs more", "a point\nand another")])
        assert f.read_text() == "    - a point\n    and another\n", repr(f.read_text())
        # an anchor and a replacement both carrying the same indent must not indent twice
        f.write_text("def x():\n    if a and b:\n        pass\n")
        apply_edits(f, [("    if a and b:", "    if a and c:")])
        assert f.read_text() == "def x():\n    if a and c:\n        pass\n", repr(f.read_text())
    print("_patch selftest ok")


def read_edits(data: object) -> list[tuple[str, str]]:
    """The (anchor, replacement) pairs from the parsed payload, in either shape it arrives in.

    A LIST OF PAIRS is the documented form. A list of OBJECTS keyed `anchor`/`replacement` is what a
    caller writes when it is thinking in the names this file's own docstring uses - and the first
    version unpacked those into the KEYS, so the tool searched each file for the literal text
    "anchor", printed `SKIPPED (0 matches): anchor` once per edit, and changed nothing. That is
    indistinguishable from a batch of stale anchors, which is the failure this tool exists to make
    impossible: measured 2026-09-13, twelve edits reported as missed while the file was untouched.
    Anything else is refused by name rather than guessed at.
    """
    out: list[tuple[str, str]] = []
    for item in data if isinstance(data, list) else [data]:
        if isinstance(item, dict):
            if set(item) != {"anchor", "replacement"}:
                raise SystemExit(f"_patch: an edit object carries exactly `anchor` and `replacement`: {item!r}")
            out.append((item["anchor"], item["replacement"]))
        elif isinstance(item, (list, tuple)) and len(item) == 2 and all(isinstance(x, str) for x in item):
            out.append((item[0], item[1]))
        else:
            raise SystemExit(f"_patch: an edit is [anchor, replacement] or "
                             f"{{\"anchor\": ..., \"replacement\": ...}}: {item!r}")
    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        print("usage: _patch.py <file>   # on stdin, a JSON list of [anchor, replacement] pairs "
              "(or of {\"anchor\": ..., \"replacement\": ...} objects)", file=sys.stderr)
        raise SystemExit(2)
    pairs = read_edits(json.load(sys.stdin))
    lines, n_skipped = apply_edits(sys.argv[1], pairs)
    print("\n".join(lines))
    raise SystemExit(1 if n_skipped else 0)
