"""May a settlement-review be dispatched now? Feature 240's decisions, importable.

The GM (2026-09-13): *"procedures which rely on someone, whether it's a human or an LLM, remembering to do
something are flawed, and we should have our tooling enforce this when possible."* A `settlement-review`
round costs 7 to 25 minutes (`specs/240-verified-before-reviewed/research.md` R1), and feature 230 spent its
last rounds finding defects the previous round's fix had introduced. So before a review is dispatched, four
things are asked of the RECORD, each decidable without reading a word of prose:

- FR-003 every finding the map's last verdict raised is DISPOSITIONED - a measurement record that verifies it,
  or an `accepted` disposition - so an unverified fix cannot buy a round by the author saying nothing;
- FR-004 a review of FIXES does not overlap an unfinished gate;
- FR-005 every map the review will read is current with the engine, and its artifacts are all there;
- FR-006 a measured figure the dispatch does quote resolves to a record.

A module rather than a program inside `pair-hooks.sh`, because a guard whose decision is a shell string cannot
be called, timed or tested without spawning the hook (feature 239's R3). The hook calls `check`; the tests call
the functions. Stdlib only, apart from the generation cache's key comparison, which is imported lazily and
costs 0.18 s.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys
from collections.abc import Callable, Iterable

VERDICTS = ("PASS", "NEEDS-WORK", "NOT-REVIEWABLE")
ARTIFACTS = (".json", ".svg", ".png", ".html")
_BACKTICKS = re.compile(r"`[^`\n]*`")
_KEY = re.compile(r"\bm:[a-z0-9][a-z0-9-]*\b")
_ONE_SHOT = re.compile(r"\bobserved \d{4}-\d{2}-\d{2}\b")  # feature 239's dated one-shot label
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def _read_json(path: pathlib.Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


# ---- the records --------------------------------------------------------------------------------------------


def verdict_dir(clone: pathlib.Path) -> pathlib.Path:
    return clone / ".git" / "review-verdicts"


def disposition_dir(clone: pathlib.Path) -> pathlib.Path:
    return clone / ".git" / "review-dispositions"


def latest_verdict(clone: pathlib.Path, name: str) -> dict | None:
    """The map's most recent verdict record, or None when no review has recorded one."""
    rec = _read_json(verdict_dir(clone) / f"{name}.json")
    return rec if isinstance(rec, dict) and rec.get("verdict") in VERDICTS else None


def accepted_ids(clone: pathlib.Path, name: str) -> set[str]:
    """Finding ids `make review-accept` dispositioned as deliberately left (FR-003)."""
    rec = _read_json(disposition_dir(clone) / f"{name}.json")
    items = rec.get("accepted", []) if isinstance(rec, dict) else []
    return {str(i.get("finding")) for i in items if isinstance(i, dict) and i.get("finding") and len(str(i.get("reason", "")).split()) >= 2}


def measurement_records(clone: pathlib.Path) -> list[dict]:
    """Every entry of every feature's `measurements.json` (feature 239's format), each carrying its own key."""
    out: list[dict] = []
    for path in sorted((clone / "specs").glob("*/measurements.json")):
        data = _read_json(path)
        if isinstance(data, dict):
            out += [{**entry, "key": key} for key, entry in data.items() if isinstance(entry, dict)]
    return out


# ---- FR-003: every finding dispositioned --------------------------------------------------------------------


def unverified_findings(clone: pathlib.Path, name: str, records: Iterable[dict] | None = None) -> list[str]:
    """The ids of the findings the map's last verdict raised that nothing verifies and nothing accepted.

    NOT-REVIEWABLE raises no findings - it names missing prerequisites, which this same check is about to name
    again - so only a PASS or NEEDS-WORK verdict's findings count."""
    verdict = latest_verdict(clone, name)
    if not verdict or verdict["verdict"] == "NOT-REVIEWABLE":
        return []
    recs = list(measurement_records(clone) if records is None else records)
    verified = {str(r.get("verifies")) for r in recs if r.get("verifies") and r.get("subject") == name}
    done = verified | accepted_ids(clone, name)
    return [str(f.get("id")) for f in verdict.get("findings", []) if isinstance(f, dict) and str(f.get("id")) not in done]


def has_findings(clone: pathlib.Path, name: str) -> bool:
    verdict = latest_verdict(clone, name)
    return bool(verdict and verdict["verdict"] != "NOT-REVIEWABLE" and verdict.get("findings"))


# ---- FR-005: every map current, every artifact present -------------------------------------------------------


def gen_of(skill: pathlib.Path, name: str) -> pathlib.Path | None:
    hits = sorted((skill / "pool").glob(f"*/{name}/{name}.gen.py"))
    return hits[0] if hits else None


def stale_maps(skill: pathlib.Path, names: Iterable[str], current: Callable[[str], bool]) -> list[str]:
    """Each map whose generator's cache key has moved, or whose pool artifacts are not all there, with the reason.

    `current` is the generation cache's key comparison, injected so a test can decide it; the CLI passes
    `gencache.is_current`, which asks without restoring a file."""
    out = []
    for name in names:
        gen = gen_of(skill, name)
        if gen is None:
            out.append(f"{name}: no pool generator by that name")
            continue
        missing = [ext for ext in ARTIFACTS if not (gen.parent / f"{name}{ext}").is_file()]
        if not current(str(gen)):
            out.append(f"{name}: its generation key has moved - the map on disk is not what the engine draws now")
        elif missing:
            out.append(f"{name}: missing {' '.join(missing)} - a reviewer would read an incomplete map")
    return out


# ---- FR-006: a quoted figure resolves to a record ------------------------------------------------------------


def _spec_lint() -> object:
    here = pathlib.Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("spec_lint_for_review", here / "spec-lint.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _number(text: str) -> float | None:
    m = _NUMBER.search(text)
    return float(m.group(0).replace(",", "")) if m else None


def unresolved_figures(prompt: str, records: Iterable[dict]) -> list[str]:
    """Each measured figure in the dispatch that no record backs, by feature 239's convention.

    A figure is `spec-lint.py`'s own `_FIGURE` - imported, never restated (spec D4). It resolves when its
    paragraph cites a record key (`m:...`) whose recorded value is that number, or when the paragraph carries
    239's dated one-shot label. A figure inside a backtick span is being NAMED, not claimed, and is skipped."""
    figure = _spec_lint()._FIGURE  # type: ignore[attr-defined]
    by_key = {str(r.get("key")): r for r in records}
    out = []
    for para in re.split(r"\n\s*\n", prompt):
        if _ONE_SHOT.search(para):
            continue
        values = [_number(str(by_key[k].get("value"))) for k in _KEY.findall(para) if k in by_key]
        for m in figure.finditer(_BACKTICKS.sub(" ", para)):
            n = _number(m.group(0))
            if n is None or not any(v is not None and abs(v - n) <= max(0.051, abs(v) * 0.005) for v in values):
                out.append(m.group(0).strip())
    return out


# ---- the check the hook runs -------------------------------------------------------------------------------


def check(clone: pathlib.Path, names: list[str], prompt: str, gate_green: bool, current: Callable[[str], bool]) -> list[str]:
    """Every reason this dispatch should not run, in the order a session would fix them. Empty means go."""
    skill = clone / ".claude" / "skills" / "diagram"
    records = measurement_records(clone)
    problems: list[str] = []
    for name in names:
        ids = unverified_findings(clone, name, records)
        if ids:
            problems.append(
                f"FR-003 {name}: finding(s) {', '.join(ids)} from its last review have no record verifying them - add a "
                f"measurements.json entry with \"verifies\" and \"subject\": \"{name}\", or `make review-accept MAP={name} "
                f"FINDING=<id> REASON=\"...\"` for one deliberately left"
            )
    if any(has_findings(clone, n) for n in names) and not gate_green:
        problems.append("FR-004 this is a review of FIXES, and the gate is not green for this engine key - run `make done` first")
    problems += [f"FR-005 {p} - `make map GEN=...`" for p in stale_maps(skill, names, current)]
    figures = unresolved_figures(prompt, records)
    if figures:
        problems.append(f"FR-006 figure(s) quoted with no record behind them: {'; '.join(figures)} - cite the `m:` key or record it")
    return problems


def _gencache_current() -> Callable[[str], bool]:
    skill = pathlib.Path(__file__).resolve().parents[1] / ".claude" / "skills" / "diagram"
    sys.path.insert(0, str(skill))
    from l7r.diagram.pipeline import gencache  # noqa: PLC0415 - lazy: only the CLI pays for the engine import

    return gencache.is_current


def accept(clone: pathlib.Path, name: str, finding: str, reason: str) -> str | None:
    """Record a finding deliberately left as it is (FR-003). Returns the refusal, or None when recorded.

    AN ACCEPTANCE IS AN ESCAPE IN ALL BUT NAME (spec-fidelity round 2), so it is held to an escape's floor - a
    reason of at least two words and eight characters - and its caller, `make review-accept`, writes the
    bypass-log entry `make audit` lists. It must name a finding the map's last verdict actually raised: an
    acceptance of an id nobody reported would be a record of nothing."""
    if len(reason.split()) < 2 or len(reason.strip()) < 8:
        return "an acceptance needs a REASON of at least two words and eight characters - it is what a later audit reads"
    verdict = latest_verdict(clone, name)
    raised = {str(f.get("id")) for f in (verdict or {}).get("findings", []) if isinstance(f, dict)}
    if finding not in raised:
        return f"{name}'s last verdict raised no finding {finding!r} (it raised: {', '.join(sorted(raised)) or 'none'})"
    path = disposition_dir(clone) / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = _read_json(path)
    items = [i for i in (rec.get("accepted", []) if isinstance(rec, dict) else []) if isinstance(i, dict) and i.get("finding") != finding]
    items.append({"finding": finding, "reason": reason.strip()})
    path.write_text(json.dumps({"map": name, "accepted": items}, indent=1) + "\n")
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["check", "accept"])
    ap.add_argument("--clone", required=True)
    ap.add_argument("--maps", default="")
    ap.add_argument("--prompt-file", default="")
    ap.add_argument("--gate-green", choices=["yes", "no"], default="no")
    ap.add_argument("--map", default="")
    ap.add_argument("--finding", default="")
    ap.add_argument("--reason", default="")
    args = ap.parse_args(argv)
    if args.command == "accept":
        refused = accept(pathlib.Path(args.clone), args.map, args.finding, args.reason)
        print(refused or f"accepted {args.finding} on {args.map}")
        return 1 if refused else 0
    problems = check(pathlib.Path(args.clone), args.maps.split(), pathlib.Path(args.prompt_file).read_text(), args.gate_green == "yes", _gencache_current())
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":  # pragma: no cover - the CLI is exercised through pair-hooks' suite
    sys.exit(main())
