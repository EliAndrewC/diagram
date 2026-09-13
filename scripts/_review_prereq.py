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
# GUARD_EDIT_OK: feature 240 - 239's convention as it landed: a paragraph cites `m:<key>`, and measurements.json holds
# the BARE key. The group is the key the file is looked up by; this read the prefixed form, which matched no record.
_KEY = re.compile(r"\bm:([a-z0-9][a-z0-9-]*)\b")
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
    # GUARD_EDIT_OK: feature 240 FR-009 / SC-007 - a verifying record must say WHAT it measured and FROM WHAT: the
    # reviewer's first stage judges the `source` against the finding (the canopy: `clumps` cannot verify a finding
    # about drawn crowns), and a record with no source gives it nothing to judge, so it verifies nothing.
    verified = {str(r.get("verifies")) for r in recs if r.get("verifies") and r.get("subject") == name and r.get("quantity") and r.get("source")}
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
    # GUARD_EDIT_OK: feature 240 FR-005 - COMPLETE IN EITHER PLACE THE REVIEWER READS. The agent reads the review
    # snapshot when the dispatch names one (feature 231: the gate evicts the pool's renders mid-run) and the pool
    # folder otherwise, so a map passes when either holds all four artifacts. Requiring the POOL alone refused every
    # review started beside a gate, which is exactly when the snapshot exists; requiring the snapshot alone refused a
    # map made whole by `make map` after the snapshot was taken.
    out = []
    snapshots = skill.parents[2] / ".git" / "review-snapshot"
    for name in names:
        gen = gen_of(skill, name)
        if gen is None:
            out.append(f"{name}: no pool generator by that name")
            continue
        places = (gen.parent, snapshots / name / "clone")
        missing = min(([ext for ext in ARTIFACTS if not (d / f"{name}{ext}").is_file()] for d in places), key=len)
        rel = gen.relative_to(skill)
        if not current(str(gen)):
            out.append(f"{name}: its generation key has moved - the map on disk is not what the engine draws now - `make map GEN={rel}`")
        elif missing:
            out.append(f"{name}: missing {' '.join(missing)} in both the pool and its review snapshot - a reviewer would read an incomplete map - `make map GEN={rel}`")
    return out


# ---- FR-006: a quoted figure resolves to a record ------------------------------------------------------------


def _spec_lint() -> object:
    here = pathlib.Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("spec_lint_for_review", here / "spec-lint.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # GUARD_EDIT_OK: feature 240 - loaded by path from a hook, so no `scripts/__pycache__/` is left in the tree: feature
    # 239 measured its selftest's bytecode being pushed by sync-with-main's own fixture and failing that suite.
    prior, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prior
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
        if _ONE_SHOT.search(para) and "method" in para.lower():  # GUARD_EDIT_OK: 239's FR-010 as it landed - a date AND a method
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
    problems += [f"FR-005 {p}" for p in stale_maps(skill, names, current)]
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


def recorded(clone: pathlib.Path, names: list[str], key: str) -> bool:
    """Has every one of these maps a PASS or NEEDS-WORK verdict for THIS engine key? (FR-002)

    The pair closes here, not at dispatch. A review that returned NOT-REVIEWABLE, returned nothing, or reviewed
    content the tree has since moved past closes nothing - which is the whole point, because a review that can
    exit early must not be able to count as the review a map owes. No maps named is not a recorded review: the
    caller's own "nothing owed" branch decides that case, and answering yes here would short-circuit it."""
    if not names or not key:
        return False
    for name in names:
        verdict = latest_verdict(clone, name)
        if not verdict or verdict["verdict"] == "NOT-REVIEWABLE" or str(verdict.get("engine_key", "")) != key:
            return False
    return True


# ---- FR-001 and FR-007: the reviewer's two calls ----------------------------------------------------------------

GATE_TARGETS = ("done", "verify", "maps", "test-full")


def _fresh(clone: pathlib.Path) -> bool:
    import subprocess  # noqa: PLC0415

    run = subprocess.run([sys.executable, str(clone / "scripts" / "gate-stamp.py"), "--fresh", "diagram"], cwd=clone, capture_output=True)
    return run.returncode == 0


def _live_targets(clone: pathlib.Path) -> list[str]:
    import subprocess  # noqa: PLC0415

    run = subprocess.run(["bash", str(clone / "scripts" / "finished-run-hooks.sh"), "live", str(clone)], capture_output=True, text=True)
    return [line.split()[-1] for line in run.stdout.splitlines() if line.strip()]


def gate_state(clone: pathlib.Path, fresh: Callable[[pathlib.Path], bool] = _fresh, live: Callable[[pathlib.Path], list[str]] = _live_targets) -> str:
    """The paired gate's state, as the reviewer reads it before its first map, between maps and before its verdict.

    `green` - a green gate has seen exactly this engine content (`gate-stamp.py --fresh diagram`; never the
    verification record, which is last-event-wins, so a green `make test-file` would read as a gate). `running` - a
    gate target is live in this clone, by the kernel's cwd table rather than a process pattern. `red` - neither:
    the gate this review was paired with finished without going green, or never ran for this content."""
    if fresh(clone):
        return "green"
    return "running" if any(t in GATE_TARGETS for t in live(clone)) else "red"


def write_verdict(clone: pathlib.Path, name: str, verdict: str, findings: list[dict], state: str) -> tuple[str, dict]:
    """Write the map's verdict record, the review's last act (FR-001). Returns (what was recorded, the record).

    The engine key is the one the DISPATCH recorded (`review_dispatch_key`), never one the agent computes - the review
    is of the content it was sent, and the pair closes only if that is still the tree's content (FR-002). And the
    gate's state is re-read HERE rather than trusted to the agent's memory (D6): a review whose paired gate is red
    at verdict time is recorded NOT-REVIEWABLE whatever it concluded, because a judgment of a map the gate refused
    must not close the pair. Its findings are kept on the record for the session to read."""
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {', '.join(VERDICTS)}")
    pairing = _read_json(clone / ".git" / "pairing-state.json")
    key = str(pairing.get("review_dispatch_key", "")) if isinstance(pairing, dict) else ""
    rec: dict = {"map": name, "engine_key": key, "verdict": verdict, "gate": state, "findings": findings}
    if verdict != "NOT-REVIEWABLE" and state == "red":
        rec.update(verdict="NOT-REVIEWABLE", concluded=verdict, why="the paired gate was red when the verdict was written")
    for i, f in enumerate(findings, 1):
        f.setdefault("id", f"F{i}")
    path = verdict_dir(clone) / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=1) + "\n")
    return rec["verdict"], rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["check", "accept", "recorded", "gate-state", "verdict"])
    ap.add_argument("--verdict", default="")
    ap.add_argument("--findings-file", default="")
    ap.add_argument("--key", default="")
    ap.add_argument("--clone", required=True)
    ap.add_argument("--maps", default="")
    ap.add_argument("--prompt-file", default="")
    ap.add_argument("--gate-green", choices=["yes", "no"], default="no")
    ap.add_argument("--map", default="")
    ap.add_argument("--finding", default="")
    ap.add_argument("--reason", default="")
    args = ap.parse_args(argv)
    if args.command == "gate-state":
        state = gate_state(pathlib.Path(args.clone))
        print(state)
        return 0  # the reviewer reads the WORD; a red gate is an answer, not an error in the command
    if args.command == "verdict":
        findings = _read_json(pathlib.Path(args.findings_file)) if args.findings_file else []
        if not isinstance(findings, list):
            print("--findings-file must hold a JSON list of {id, severity, what}")
            return 2
        clone = pathlib.Path(args.clone)
        got, rec = write_verdict(clone, args.map, args.verdict, [f for f in findings if isinstance(f, dict)], gate_state(clone))
        print(f"recorded {got} for {args.map} (engine key {rec['engine_key'] or 'NONE - no dispatch recorded'}, gate {rec['gate']})")
        return 0
    if args.command == "recorded":
        return 0 if recorded(pathlib.Path(args.clone), args.maps.split(), args.key) else 1
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
