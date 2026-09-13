"""Feature 242's work list, DERIVED from feature 238's four reader reports.

Feature 238's closing report put the remainder at "about 600", taken from R6's `CITE` count of 631.
That number counts every item a reader named as owing a citation - including the ones 238 then closed
by moving 142 inline markers into absence notes at their own assertions. The successor's real list is
the items the reports name that carry NO marker in the prose, less the classes R7 closed by hand.

This script derives it from the reports themselves, which R7 declares the authority on identity. It
reproduces every per-report total the reports state (171 / 203 / 153 / 168 = 695), which is what makes
its marker split trustworthy at all; where it disagrees with the readers' own stated marker counts the
disagreement is REPORTED rather than hidden, and the wider of the two bounds is the one to plan with.

Usage: python3 specs/242-cite-the-unfootnoted-assertions/measure/inventory_census.py [--record]
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPORTS = HERE.parent.parent / "238-unfootnoted-assertions-researched" / "reader-reports"
RECORD = HERE.parent / "measurements.json"
COMMAND = "python3 specs/242-cite-the-unfootnoted-assertions/measure/inventory_census.py --record"

#: What the four readers themselves stated, from feature 238's T02-T05 verify lines. The parser is
#: only believable if it reproduces these, so they are asserted rather than trusted.
STATED_ITEMS = {
    "religion-vegetation-and-urban-features.md": 171,
    "the-city-pages.md": 203,
    "water-fields-and-the-river-cities.md": 153,
    "homesteads-buildings-and-the-hamlet-pages.md": 168,
}
STATED_MARKED = {
    "religion-vegetation-and-urban-features.md": 34,
    "the-city-pages.md": 59,
    "water-fields-and-the-river-cities.md": 51,
    "homesteads-buildings-and-the-hamlet-pages.md": 67,
}

#: Closed by feature 238 in a class OTHER than the marker conversion, so absent from the successor's
#: list even though the items carry no marker: research.md R7 items 2, 3, 5 and 6.
#:
#: R7 item 4 - the twelve defects - is deliberately NOT here. Those were found in the SECOND reading,
#: of material that already carried a footnote (a misread workforce figure, a quotation readable on no
#: page the note pointed at, a damaged text layer), and the four inventory readers named only
#: assertions carrying NO footnote. The two populations are therefore disjoint by construction. Where
#: one defect did coincide with a report item the list below is short by that much, at most twelve.
CLOSED_BARE = {
    "roster-hidden on urban-features": 9,
    "roster-hidden on buildings": 5,
    "sections disclosing with no footnote at all": 6,
    "settlements.html, restating footnoted canon": 1,
    "the caravan inn (one bare item, homesteads report 148)": 1,
}


def items(text: str) -> list[str]:
    """One block per inventory item. Two shapes: a bold label, or a numbered list."""
    parts = re.split(r"\n(?=\*\*[A-Z]{1,3}\d+[.*])", text)
    labeled = [p for p in parts if re.match(r"\*\*[A-Z]{1,3}\d+[.*]", p)]
    if labeled:
        return labeled
    out: list[str] = []
    cur: str | None = None
    for line in text.splitlines():
        if re.match(r"^\d+\.\s", line):
            if cur is not None:
                out.append(cur)
            cur = line
        elif cur is not None and line.strip() and not line.startswith(("#", "---")):
            cur += " " + line
        elif cur is not None:
            out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    # In the numbered reports a real inventory item always carries a confidence label; a numbered
    # line in a closing summary does not, and four per report would otherwise be counted as items.
    return [b for b in out if re.search(r"\*\*(HIGH|MEDIUM|LOW)\b", b)]


#: The readers hedged 29 of the 695 inventoried items with a compound label - 25 MEDIUM-HIGH and 4
#: LOW-MEDIUM, of which 28 are on the bare work list (one MEDIUM-HIGH item carries a marker). Reading
#: only the first word buckets every one of them a tier LOW, which would have FR-012's ordering meet 24
#: of the listed items later than the reader meant. They are reported as their own tiers instead:
#: rounding a deliberate hedge in either direction invents a judgment the reader declined to make.
TIERS = ("HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW")


def confidence(block: str) -> str:
    m = re.search(r"\*\*(HIGH|MEDIUM|LOW)(-(?:HIGH|MEDIUM|LOW))?\b", block)
    if not m:
        return "unlabeled"
    label = m.group(1) + (m.group(2) or "")
    if label in TIERS:
        return label
    # "HIGH-MEDIUM" is the same hedge as "MEDIUM-HIGH"; name it once, strongest tier first. An
    # unrecognized compound is RETURNED rather than coerced - main() fails on any tier outside TIERS,
    # because a tier the printed composition does not iterate would otherwise vanish from every share
    # it belongs to while the totals still looked right.
    reversed_label = "-".join(reversed(label.split("-")))
    return reversed_label if reversed_label in TIERS else label


def carries_marker(block: str) -> bool:
    """Did the assertion carry an inline unsourced-class marker in the prose the reader quoted?"""
    low = block.lower()
    if re.search(r"\bno marker\b", low) or re.search(r"marker:\s*(none|no\b)", low):
        return False
    if re.search(r"\bmarker:", low):
        return True
    return "unsourced" in low or "is a guess" in low or "they are a guess" in low


def main() -> int:
    per_report = {}
    bare_conf: collections.Counter[str] = collections.Counter()
    total = marked = 0
    for path in sorted(REPORTS.glob("*.md")):
        blocks = items(path.read_text(encoding="utf-8"))
        m = sum(1 for b in blocks if carries_marker(b))
        for b in blocks:
            if not carries_marker(b):
                bare_conf[confidence(b)] += 1
        per_report[path.name] = {"items": len(blocks), "marked": m, "bare": len(blocks) - m}
        total += len(blocks)
        marked += m

    for name, want in STATED_ITEMS.items():
        got = per_report[name]["items"]
        if got != want:
            print(f"PARSE DISAGREES with the report's own total: {name} {got} != {want}")
            return 1

    stated_marked = sum(STATED_MARKED.values())
    bare_parsed = total - marked
    bare_stated = total - stated_marked
    closed = sum(CLOSED_BARE.values())

    print(f"{'report':46}{'items':>6}{'marked':>8}{'bare':>6}")
    for name, row in sorted(per_report.items()):
        print(f"{name[:44]:46}{row['items']:6}{row['marked']:8}{row['bare']:6}")
    print("-" * 66)
    print(f"{'TOTAL':46}{total:6}{marked:8}{bare_parsed:6}")
    print()
    print(f"bare by the readers' own marker counts ({stated_marked} marked): {bare_stated}")
    print(f"bare by this parse ({marked} marked):                {bare_parsed}")
    stray = sorted(t for t in bare_conf if t not in TIERS)
    if stray:
        print(f"UNRECOGNIZED confidence tier(s) {stray} - the printed composition would drop them")
        return 1
    if sum(bare_conf[t] for t in TIERS) != bare_parsed:
        print(f"tier shares sum to {sum(bare_conf[t] for t in TIERS)}, not the {bare_parsed} bare items")
        return 1

    print(f"closed by 238 in a non-marker class:                 {closed} "
          f"({', '.join(f'{k} {v}' for k, v in CLOSED_BARE.items())})")
    print(f"WORK LIST: {bare_stated - closed} to {bare_parsed - closed} items")
    print("  of the parsed remainder, by the readers' own confidence tiers: "
              + ", ".join(f"{t} {bare_conf[t]}" for t in TIERS))

    if "--record" in sys.argv:
        rec = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        def put(key: str, value: object, unit: str, note: str) -> None:
            rec[key] = {"command": COMMAND, "note": note, "taken": "2026-09-13",
                        "unit": unit, "value": value}
        put("inventory-items", total, "items",
            "every sentence the four readers named; reproduces each report's own stated total")
        put("worklist-low", bare_stated - closed, "items",
            "the remainder using the readers' own marker counts, less the classes 238 closed by hand")
        put("worklist-high", bare_parsed - closed, "items",
            "the same, using this parser's marker classification - the wider bound")
        put("worklist-high-confidence", bare_conf["HIGH"], "items",
            "of the parsed remainder, the readers' HIGH confidence share")
        put("worklist-medium-high-confidence", bare_conf["MEDIUM-HIGH"], "items",
            "the readers' hedged MEDIUM-HIGH share, reported as its own tier rather than rounded")
        put("worklist-medium-confidence", bare_conf["MEDIUM"], "items", "the MEDIUM share")
        put("worklist-low-medium-confidence", bare_conf["LOW-MEDIUM"], "items",
            "the readers' hedged LOW-MEDIUM share")
        put("worklist-low-confidence", bare_conf["LOW"], "items", "the LOW share")
        put("marker-classifier-disagreement", abs(marked - stated_marked), "items",
            "items this parser and the readers' own stated splits classify differently")
        RECORD.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nrecorded to {RECORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
