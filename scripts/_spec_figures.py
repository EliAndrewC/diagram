#!/usr/bin/env python3
"""spec-lint CHECK 5: a measured figure is DERIVED, not typed (feature 239, section C).

Feature 236's second amendment went through five review rounds, and ten of their twenty findings were a
figure - stale, unreproducible, or measured one way and stated another. A reviewer re-deriving them by
hand rebuilt the same instrument four times. So a figure now points at the entry a harness wrote, and
this check confirms the entry exists and says what the prose says.

THE RULES, each an FR of feature 239:

  FR-009   A figure with a unit carries `m:<key>` in its own paragraph; the key is in the feature's
           `measurements.json`; the recorded value appears in that paragraph.
  FR-009a  "Appears" is NUMERIC: a number token in the paragraph that, with thousands separators
           stripped, equals the recorded value or equals it rounded to the decimals the token shows.
  FR-009b  The reach is where stale figures actually stood: the operative spec sections, all of
           `research.md`, and the Review history - where a round label `on round N's own run` (or
           `this round's own run`) may stand instead of a key, because that section records what a round
           measured at the time.
  FR-009c  A figure inside a backtick span is NAMED, not asserted, and is skipped.
  FR-010   A one-shot observation - something no command can produce - passes with its label: the date
           it was observed and its method, `observed YYYY-MM-DD` and `method` in the paragraph.
  FR-011b  `varies` belongs to a timing: an entry whose unit counts things may not carry it.
  FR-011e  A timing entry names its sample in `quantity`.

WHICH SPECS (plan P2): features numbered 239 and later, and like checks 1, 3 and 4 only once a
`tasks.md` exists. Read retroactively the rule would fail every earlier spec on its first edit.
"""

from __future__ import annotations

import json
import pathlib
import re

FIRST_FEATURE = 239
TIMING_UNITS = {"ms", "s", "min", "h", "%", "x"}
_UNITS = ("ft", "m", "km", "ha", "mu", "sq ft", "%", "ms", "s", "min", "minute", "minutes",
          "h", "MB", "MiB", "GiB", "px")      # spec-lint check 1's own roster, D4: one definition of a figure
_UNIT_ALT = "|".join(sorted((re.escape(u) for u in _UNITS), key=len, reverse=True))
_FIGURE = re.compile(rf"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*(?:{_UNIT_ALT})(?![\w-])")
_KEY = re.compile(r"\bm:([a-z0-9][a-z0-9-]*)")
_SPAN = re.compile(r"`[^`\n]*`")
_TOKEN = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
_ROUND_LABEL = re.compile(r"\b(?:round \d+|this round)'s own run\b", re.I)
_ONE_SHOT = re.compile(r"\bobserved \d{4}-\d{2}-\d{2}\b")
_OPERATIVE = ("summary", "functional requirements", "success criteria", "decisions recorded")
_HEADING = re.compile(r"^(#{2,})\s+(.*?)\s*$", re.M)


def feature_number(spec_dir: pathlib.Path) -> int:
    m = re.match(r"(\d{3})-", spec_dir.name)
    return int(m.group(1)) if m else 0


def appears(value: float, paragraph: str) -> bool:
    """FR-009a: some number token equals the recorded value, exactly or at the token's own precision."""
    for raw in _TOKEN.findall(paragraph):
        token = raw.replace(",", "")
        decimals = len(token.split(".", 1)[1]) if "." in token else 0
        try:
            if round(float(value), decimals) == float(token):
                return True
        except ValueError:
            continue
    return False


def paragraphs_in_scope(spec_dir: pathlib.Path) -> list[tuple[pathlib.Path, int, str, str]]:
    """(file, first line, paragraph, section kind) for every paragraph check 5 reads."""
    out: list[tuple[pathlib.Path, int, str, str]] = []
    spec, research = spec_dir / "spec.md", spec_dir / "research.md"
    for path, whole_file in ((spec, False), (research, True)):
        if not path.is_file():
            continue
        text = path.read_text()
        kind = "research" if whole_file else ""
        line, top = 1, ""
        for block in re.split(r"(\n\s*\n)", text):
            head = _HEADING.search(block)
            if head and len(head.group(1)) <= 2:
                top = head.group(2).lower()
            if not whole_file:
                kind = ("review" if top.startswith("review history")
                        else "operative" if top.startswith(_OPERATIVE) else "")
            if kind and block.strip():
                out.append((path, line, block, kind))
            line += block.count("\n")
    return out


def check_paragraphs(spec_dir: pathlib.Path, recorded: dict[str, dict]) -> list[str]:
    bad = []
    for path, line, para, kind in paragraphs_in_scope(spec_dir):
        visible = _SPAN.sub(lambda m: " " * len(m.group(0)), para)          # FR-009c
        # A HEADING NAMES A SECTION; the paragraph under it carries the key. Found on this check's first run,
        # against its own feature: `## R1 - where 208 minutes went` was reported while its body, two lines
        # below, pointed at the entry.
        visible = re.sub(r"^#{1,6}\s.*$", lambda m: " " * len(m.group(0)), visible, flags=re.M)
        figures = [m.group(0).strip() for m in _FIGURE.finditer(visible)]
        if not figures:
            continue
        if _ONE_SHOT.search(para) and "method" in para.lower():              # FR-010
            continue
        keys = _KEY.findall(para)
        if not keys:
            if kind == "review" and _ROUND_LABEL.search(para):               # FR-009b
                continue
            bad.append(f"{path}:{line}: the figure {figures[0]!r} carries no `m:<key>` - record it with the "
                       f"harness that measured it, or label it as a one-shot observation (date and method)"
                       + (" or as a round's own run" if kind == "review" else ""))
            continue
        for key in keys:
            if key not in recorded:
                bad.append(f"{path}:{line}: `m:{key}` is not in measurements.json")
            elif not appears(recorded[key].get("value"), visible):
                bad.append(f"{path}:{line}: `m:{key}` records {recorded[key].get('value')!r}, which this "
                           f"paragraph does not state")
    return bad


def check_entries(spec_dir: pathlib.Path, recorded: dict[str, dict]) -> list[str]:
    """FR-011b and FR-011e, on the measurements file itself."""
    bad, where = [], spec_dir / "measurements.json"
    for key, entry in sorted(recorded.items()):
        if not entry.get("varies"):
            continue
        if entry.get("unit") not in TIMING_UNITS:
            bad.append(f"{where}: `{key}` carries `varies` but its unit {entry.get('unit')!r} counts things - "
                       f"a count repeats exactly or the thing counted changed (FR-011b)")
        if not entry.get("quantity"):
            bad.append(f"{where}: `{key}` is a timing with no `quantity` naming the sample it measured (FR-011e)")
    return bad


def check_measured_figures(spec_dir: pathlib.Path) -> list[str]:
    spec_dir = pathlib.Path(spec_dir)
    if feature_number(spec_dir) < FIRST_FEATURE or not (spec_dir / "tasks.md").is_file():
        return []
    path = spec_dir / "measurements.json"
    try:
        recorded = json.loads(path.read_text()) if path.is_file() else {}
    except ValueError as exc:
        return [f"{path}: not valid JSON ({exc})"]
    return check_paragraphs(spec_dir, recorded) + check_entries(spec_dir, recorded)
