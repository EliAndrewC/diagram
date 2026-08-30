#!/usr/bin/env python3
"""THE FIRING CENSUS (feature 163): which checks does anything the engine can produce TODAY still make fail?

    make firing-census
    make firing-census SUITE=<dir>      # fold in journals from a pytest sweep (T04)

The GM's question, verbatim: *"run through the automated checks to see which ones do not appear to
ever actually fire with our current implementation and then delete them and any tests associated with
them."* Two words in that sentence do the work, and this tool is built around both:

**"ACTUALLY FIRE"** - not "is mentioned in a test". 140 of the 152 live check names appear somewhere
under `tests/`, while only about 95 have a negative fixture of any kind, so a grep answers a different
question and answers it wrong in both directions (spec FR-002). This tool instead reads the gate's own
emitter: `check_village/driver.py`'s verdict journal records every FAIL and every WAIVE, and a WAIVE is
a suppressed FAIL, so both count as firing.

**"WITH OUR CURRENT IMPLEMENTATION"** - not "at any point in this repository's history". The evidence
is therefore CLASSIFIED rather than pooled (spec FR-001/FR-003):

  live-map           a live pool map fails it today                  -> the current implementation, firing
  scripted-fixture   a frozen fixture derived from a scripted roll   -> the current implementation, firing
  hand-fixture       a frozen hand-built or hand-authored manifest   -> NOT the current implementation
  test               a test's inline manifest made it fail           -> NOT the current implementation

The hand-era classes are recorded, never discarded: the repository already retired
`bridges_align_with_their_way` on exactly this reasoning (*"every scrap of evidence for it was two
decks a person placed BY HAND on maps no generator can produce"*), and kept `bridges_span_their_water`
on the opposite - `hamletgen/ways.py` records it catching the scripted placer four separate times. So
the census produces a CANDIDATE and the FR-006 placer read produces the ruling (feature 158).

A by-hand diagnostic, not under the 100% coverage rule - it is not in pyproject's `[tool.coverage.run]
source` list, the same standing as `check_census.py` (feature 141) and `perf_review.py` (feature 129).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
from typing import Any

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if HERE not in sys.path:  # pragma: no cover - under pytest the skill dir is already on the path
    sys.path.insert(0, HERE)

LIVE_MAP = "live-map"
SCRIPTED_FIXTURE = "scripted-fixture"
HAND_FIXTURE = "hand-fixture"
TEST = "test"
# What FR-001 counts as the CURRENT implementation firing. `test` is deliberately not here: a unit
# test's inline dict is a manifest a person typed, not a shape any generator produces.
CURRENT = (LIVE_MAP, SCRIPTED_FIXTURE)

FIRES = "FIRES"
FIRES_HAND_ONLY = "FIRES-HAND-ONLY"
NEVER_FIRES = "NEVER-FIRES"


def live_check_names() -> list[str]:
    """The live check-name pin - the roster every verdict is classified against."""
    with open(os.path.join(HERE, "tests/fixtures/gate_check_names.json"), encoding="utf-8") as fh:
        return sorted(json.load(fh))


def classify_manifest(M: dict[str, Any], frozen: bool) -> str:
    """Which evidence class a manifest belongs to.

    `meta.generated_by` is the discriminator because it is what a scripted roll stamps and what no
    hand-authored map or hand-built test dict carries."""
    if not frozen:
        return LIVE_MAP
    return SCRIPTED_FIXTURE if (M.get("meta") or {}).get("generated_by") else HAND_FIXTURE


def verdicts_for(M: dict[str, Any]) -> set[tuple[str, str]]:
    """{(check, "FAIL"|"WAIVE")} for one manifest, read off the gate's OWN emitter.

    Not off `gate()`'s return value, which lists FAILs only - a waived check has fired and been
    suppressed, and a census that could not see that would call a waived check dead."""
    from l7r.diagram.check_village import driver

    driver._VERDICTS.clear()
    try:
        driver.gate(dict(M), verbose=False)
    except Exception as exc:  # a fixture built for one check can raise from an unrelated one
        return {("<error>", f"{type(exc).__name__}: {exc}"[:120])}
    return {(n, v) for n, v, _src in driver._VERDICTS}


def evidence_from_paths(paths: list[str], frozen: bool) -> dict[str, set[tuple[str, str]]]:
    """{check: {(evidence class, artifact path)}} over a list of manifest files."""
    out: dict[str, set[tuple[str, str]]] = {}
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            M = json.load(fh)
        klass = classify_manifest(M, frozen)
        rel = os.path.relpath(p, HERE)
        for name, _verdict in verdicts_for(M):
            out.setdefault(name, set()).add((klass, rel))
    return out


def evidence_from_journals(directory: str) -> dict[str, set[tuple[str, str]]]:
    """Fold in the journals a pytest sweep left behind (one file per xdist worker)."""
    out: dict[str, set[tuple[str, str]]] = {}
    for p in sorted(glob.glob(os.path.join(directory, "verdicts-*.json"))):
        with open(p, encoding="utf-8") as fh:
            for name, _verdict, source in json.load(fh):
                out.setdefault(name, set()).add((TEST, f"suite:{source}"))
    return out


def merge(*parts: dict[str, set[tuple[str, str]]]) -> dict[str, set[tuple[str, str]]]:
    out: dict[str, set[tuple[str, str]]] = {}
    for part in parts:
        for name, rows in part.items():
            out.setdefault(name, set()).update(rows)
    return out


def verdict_for(rows: set[tuple[str, str]]) -> str:
    """FIRES when the CURRENT implementation makes it fail; FIRES-HAND-ONLY when only a hand-era
    artifact does (FR-003 treats that as never-fires and deletes the fixture with the check, after
    the FR-006 placer read); NEVER-FIRES when nothing in the repository does."""
    if not rows:
        return NEVER_FIRES
    return FIRES if any(k in CURRENT for k, _src in rows) else FIRES_HAND_ONLY


def census(suite_journal: str | None = None) -> dict[str, Any]:
    """The whole census, as {check: {verdict, evidence}} plus the counts."""
    live = sorted(glob.glob(os.path.join(HERE, "pool/*/*/*.json")))
    frozen = sorted(glob.glob(os.path.join(HERE, "pool/regressions/*.json")))
    parts = [evidence_from_paths(live, frozen=False), evidence_from_paths(frozen, frozen=True)]
    if suite_journal and os.path.isdir(suite_journal):
        parts.append(evidence_from_journals(suite_journal))
    ev = merge(*parts)
    names = live_check_names()
    rows = {n: {"verdict": verdict_for(ev.get(n, set())), "evidence": sorted(ev.get(n, set()))} for n in names}
    # FR-005: a census that classifies nothing is indistinguishable from a clean bill of health, so it
    # says out loud how many artifacts it drove and how many verdicts it saw.
    return {
        "artifacts": {"live": len(live), "frozen": len(frozen), "suite_journal": bool(suite_journal)},
        "verdicts_observed": sum(len(v) for v in ev.values()),
        "rows": rows,
        "counts": {v: sum(1 for r in rows.values() if r["verdict"] == v) for v in (FIRES, FIRES_HAND_ONLY, NEVER_FIRES)},
    }


def render(result: dict[str, Any]) -> str:
    """The ledger, as markdown."""
    c, a = result["counts"], result["artifacts"]
    lines = [
        f"# Firing census - {len(result['rows'])} live checks against {a['live']} live maps and {a['frozen']} frozen fixtures",
        "",
        f"`{FIRES}` {c[FIRES]} | `{FIRES_HAND_ONLY}` {c[FIRES_HAND_ONLY]} | `{NEVER_FIRES}` {c[NEVER_FIRES]}"
        f" - {result['verdicts_observed']} verdicts observed"
        + (", suite journal folded in" if a["suite_journal"] else ", NO suite journal (run `make firing-census SUITE=...`)"),
        "",
        "`FIRES` = the current implementation makes it fail. `FIRES-HAND-ONLY` = only a hand-era artifact",
        "does, which FR-003 treats as never-fires. Every non-`FIRES` row takes the FR-006 placer read",
        "before anything is deleted - the census produces a candidate, not a ruling (feature 158).",
        "",
        "| check | verdict | evidence |",
        "|---|---|---|",
    ]
    for name, row in sorted(result["rows"].items(), key=lambda kv: (kv[1]["verdict"] != NEVER_FIRES, kv[1]["verdict"], kv[0])):
        ev = "; ".join(f"`{k}` {os.path.basename(s)}" for k, s in row["evidence"][:4]) or "-"
        if len(row["evidence"]) > 4:
            ev += f" (+{len(row['evidence']) - 4} more)"
        lines.append(f"| `{name}` | **{row['verdict']}** | {ev} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.firing_census")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="specs/163-checks-into-the-placer/firing-census", help="output base path (.md and .json)")
    ap.add_argument("--suite", default=None, help="directory of verdict journals from a pytest sweep")
    args = ap.parse_args(argv)

    from l7r.diagram.check_village import driver

    with tempfile.TemporaryDirectory() as tmp:
        # The journal is switched on for THIS process only, and its files are thrown away: the census
        # reads driver._VERDICTS directly, per artifact, so it can attribute each verdict to its file.
        os.environ[driver.VERDICT_JOURNAL_ENV] = tmp
        try:
            result = census(args.suite)
        finally:
            os.environ.pop(driver.VERDICT_JOURNAL_ENV, None)

    base = os.path.join(HERE, "..", "..", "..", args.out) if not os.path.isabs(args.out) else args.out
    base = os.path.abspath(base)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    with open(base + ".json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    with open(base + ".md", "w", encoding="utf-8") as fh:
        fh.write(render(result))
    c = result["counts"]
    print(f"firing census: {c[FIRES]} FIRES, {c[FIRES_HAND_ONLY]} FIRES-HAND-ONLY, {c[NEVER_FIRES]} NEVER-FIRES -> {base}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
