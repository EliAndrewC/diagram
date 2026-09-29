#!/usr/bin/env python3
"""What a pattern can find against the style guide, listed for `record-style` (feature 292).

WHY. The style guide (`research/STYLE.md`) is mostly judgment - whether a title is plain English, whether a lead line
should be a statement or a question - and that is the `record-style` agent's. Two of its rules have a mechanical half,
found exactly and for no tokens, so they are found here and handed over:

- **METRIC WITHOUT A CONVERSION** (STYLE.md 6, GM 2026-09-29: *"any time we expressed something in meters, then we also
  convert it to feet"*): every metric figure in the section's OWN prose - never a quotation, a footnote or a comment -
  with no `(~N ft)`, `(~N in)` or acre/square-foot conversion right after it. This one is a finding, not a candidate.
- **GM IN THE VISIBLE TEXT** (STYLE.md 1, GM 2026-09-29: *"you should not refer to this as a GM ruling"*): every
  visible "GM" - a ruling, a quotation, an acceptance. The ruling belongs in a comment; each is a finding.
- **LEAD LINES** (STYLE.md 3): every bullet's bold lead line, marked `Q` (a question) or `S` (a statement), with the
  start of its body - the list the agent rules on, statement or question, and whether a newcomer could read it.

    _style_prepass.py <page> --root <repo> [--section <text>]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

#: A metric figure: a number (or a range of two) and a metric unit. `m` alone is matched only as a word, so `5 min` and
#: `2 mm` are told apart by the unit list rather than by luck.
METRIC = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?(?:\s*(?:-|to)\s*\d[\d,]*(?:\.\d+)?)?)\s*"
    r"(km2|km|ha|m2|cm|mm|m|kilometers?|hectares?|meters?|centimeters?|millimeters?|square meters?)(?![\w])"
)
#: The conversion the guide asks for, right after the figure: `(~36-92 ft)`, `(~4 in)`, `(~2.5 acres)`, `(~120 sq ft)`.
CONVERTED = re.compile(r"^\s*\(~[\d,.\-\s]+(?:ft|in|acres?|sq ft|square feet|miles?)\b")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
#: Quoted text keeps its source's own units: a GM ruling in `<q>`, a source's words in corner brackets or quotes.
_QUOTED = re.compile(r"<q>.*?</q>|「.*?」|&quot;.*?&quot;|\"[^\"]*\"", re.S)
_TAG = re.compile(r"<[^>]+>")
_GM = re.compile(r"\bGM(?:'s)?\b")
_LEAD = re.compile(r"<li>\s*<strong>(.*?)</strong>\s*<br>\s*(.*?)(?=</li>|<ul>)", re.S)


def visible_prose(html: str) -> str:
    """The section's own words as its reader meets them, less every quotation and comment."""
    return re.sub(r"\s+", " ", _TAG.sub(" ", _QUOTED.sub(" ", _COMMENT.sub(" ", html))))


def unconverted(html: str) -> list[str]:
    """Each metric figure in the prose with no conversion after it, as `<figure> - ...context...`."""
    text = visible_prose(html)
    out = []
    for m in METRIC.finditer(text):
        if not CONVERTED.match(text[m.end() :]):
            out.append(f"{m.group(0)} - ...{text[max(0, m.start() - 50) : m.end() + 30].strip()}...")
    return out


def gm_mentions(html: str) -> list[str]:
    """Each visible "GM" in the section - quotations included, since a quoted ruling is the thing that must go."""
    text = re.sub(r"\s+", " ", _TAG.sub(" ", _COMMENT.sub(" ", html)))
    return [f"...{text[max(0, m.start() - 40) : m.end() + 60].strip()}..." for m in _GM.finditer(text)]


def lead_lines(html: str) -> list[str]:
    """Each bullet's lead line, `Q` or `S`, with the start of its body."""
    out = []
    for m in _LEAD.finditer(_COMMENT.sub("", html)):
        lead = re.sub(r"\s+", " ", _TAG.sub("", m.group(1))).strip()
        body = re.sub(r"\s+", " ", _TAG.sub("", m.group(2))).strip()
        out.append(f"{'Q' if lead.endswith('?') else 'S'}  {lead}  |  {body[:110]}")
    return out


def report(fragments: dict[str, str]) -> str:
    """The prepass text for the named question fragments (their notes files are not prose and are skipped)."""
    lines = []
    for name, html in fragments.items():
        metric, leads, gm = unconverted(html), lead_lines(html), gm_mentions(html)
        lines.append(f"== {name}")
        lines.append(f"METRIC WITHOUT A CONVERSION ({len(metric)}) - each is a FAIL of STYLE.md 6:")
        lines += [f"  {x}" for x in metric] or ["  none"]
        lines.append(f"GM IN THE VISIBLE TEXT ({len(gm)}) - each is a FAIL of STYLE.md 1 (the ruling goes in a comment):")
        lines += [f"  {x}" for x in gm] or ["  none"]
        lines.append(f"LEAD LINES ({len(leads)}) - rule on each: statement or question (STYLE.md 3), and readable from what precedes it:")
        lines += [f"  {x}" for x in leads] or ["  none"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="a research page name: homesteads, cities/tango")
    ap.add_argument("--root", default=".")
    ap.add_argument("--section", default="", help="only the questions whose heading or file name contains this text")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _hm_record import fragments_for  # noqa: PLC0415

    rels = [r for r in fragments_for(args.page, args.section, str(root)) if not r.endswith(".notes.html")]
    if not rels:
        print(f"style-prepass: no question of {args.page} matches {args.section!r}", file=sys.stderr)
        return 2
    print(report({pathlib.Path(r).name: (root / r).read_text(encoding="utf-8") for r in rels}), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
