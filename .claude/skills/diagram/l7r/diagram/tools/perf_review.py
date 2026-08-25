"""The review records (feature 129): explanation, confirmation, audit, sign-off - and `--check`.

    python3 -m l7r.diagram.tools.perf_review explain --why "..."                 (the session)
    python3 -m l7r.diagram.tools.perf_review confirm --verdict consistent --as perf-audit
    python3 -m l7r.diagram.tools.perf_review audit --verdict justified --necessary ... --commensurate ... --no-way-around ... --as perf-audit
    python3 -m l7r.diagram.tools.perf_review signoff --why "..." --as GM         (a terminal)
    python3 -m l7r.diagram.tools.perf_review check                               (the push)

Every record is ONE FILE in dev/perf-log/ (never a shared log - concurrent clones), BOUND to the
end snapshot's commit, the environment and the exact percentages (`binding`, FR-005/FR-009a), and
carries who granted it (FR-007). A record whose binding no longer matches the newest pair is stale
and refused by name; a negative or inconclusive verdict never counts (FR-006).

WHO IS ASKING - the fallback the GM described (research R1). Nothing distinguishes a subagent's
shell from the main session's, so `confirm` and `audit` PROMPT: without `--as perf-audit` they
print that the main session must not continue, name the escape, and DECLINE. The declaration is
recorded with the session id. What a self-grant costs is the record's content - a stated cause
that must match the stage delta, three criteria each addressed - written into a tracked file.
`signoff` needs a terminal: the GM has one, a session does not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from l7r.diagram.tools import perf_bands

PASSING = {"explanation": ("pending", "consistent", "inconsistent"), "confirmation": ("consistent",), "audit": ("justified",), "signoff": ("signed",)}
CRITERIA = ("necessary", "commensurate", "no_way_around")

PROMPT = """
perf-review: WHO IS ASKING?

  This record is the perf-audit SUBAGENT's to write, not the main session's. The GM: "if you are the
  main session, then you should not continue. You should exit now by taking this escape hatch and
  then have the subagent run this command." Nothing in this shell can tell the two apart (research
  R1), so the declaration is yours - and it is recorded, with what you write, in a tracked file.

  If you ARE the perf-audit subagent, re-run with:  AS=perf-audit
  If you are the main session: launch the `perf-audit` agent (.claude/agents/perf-audit.md) and let
  it run this command. DECLINED.
"""


def _snapshots(log_dir: Path) -> list[dict[str, Any]]:
    out = []
    for fn in sorted(log_dir.glob("*.json")):
        try:
            d = json.loads(fn.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if "rows" in d and "label" in d:
            out.append(d)
    return out


def _records(log_dir: Path) -> list[dict[str, Any]]:
    out = []
    for fn in sorted(log_dir.glob("*-review-*.json")):
        try:
            d = json.loads(fn.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if d.get("kind") in PASSING:
            d["_file"] = fn.name
            out.append(d)
    return out


def feature_number(feature: str) -> str:
    n = "".join(ch for ch in feature.split("-")[0] if ch.isdigit())
    return n


def pairs(log_dir: Path, feature: str) -> dict[str, perf_bands.Verdict]:
    """The newest `<n>-start` / `<n>-end` pair PER ENVIRONMENT for this feature (FR-015, FR-017)."""
    n = feature_number(feature)
    by_env: dict[str, dict[str, dict[str, Any]]] = {}
    for s in _snapshots(log_dir):
        label = str(s.get("label", ""))
        if label not in (f"{n}-start", f"{n}-end"):
            continue
        env = perf_bands.environment_of(s)
        by_env.setdefault(env, {})[label.split("-")[1]] = s  # newest wins: files sort by utc
    out: dict[str, perf_bands.Verdict] = {}
    for env, d in by_env.items():
        if "start" in d and "end" in d:
            out[env] = perf_bands.evaluate(d["start"], d["end"])
    return out


def binding(v: perf_bands.Verdict) -> str:
    return hashlib.sha256(json.dumps([v.cur["commit"], v.environment, v.measurements], sort_keys=True).encode()).hexdigest()


def write(log_dir: Path, feature: str, v: perf_bands.Verdict, kind: str, verdict: str, declared: str, **fields: Any) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    clone = log_dir.resolve().parts[log_dir.resolve().parts.index(".clones") + 1] if ".clones" in log_dir.resolve().parts else "main"
    rec = {
        "kind": kind,
        "feature": feature,
        "environment": v.environment,
        "band": v.band,
        "base": v.base,
        "end": v.cur,
        "measurements": v.measurements,
        "binding": binding(v),
        "verdict": verdict,
        "granted_by": {"declared": declared, "session_id": os.environ.get("CLAUDE_CODE_SESSION_ID", ""), "utc": stamp},
        **fields,
    }
    path = log_dir / f"{stamp}-review-{feature_number(feature)}-{kind}-{v.environment}-{clone}.json"
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def check(log_dir: Path, feature: str) -> tuple[bool, str]:
    """Does every environment's newest pair carry the records its band owes? (the push's question)"""
    vs = pairs(log_dir, feature)
    if not vs:
        return True, f"perf-review: no {feature_number(feature)}-start/-end pair in any environment - nothing to review (perf-gate refuses a missing bookend on its own)"
    recs = _records(log_dir)
    lines: list[str] = []
    ok = True
    for env, v in sorted(vs.items()):
        b = binding(v)
        have = {r["kind"]: r for r in recs if r.get("binding") == b and r.get("verdict") in PASSING[str(r["kind"])] and r.get("kind") != "explanation"}
        expl = [r for r in recs if r.get("binding") == b and r.get("kind") == "explanation" and str(r.get("explanation", "")).strip()]
        stale = [r["_file"] for r in recs if r.get("environment") == env and r.get("binding") != b]
        negative = [f"{r['kind']}={r['verdict']}" for r in recs if r.get("binding") == b and r.get("verdict") not in PASSING[str(r["kind"])]]
        need: list[str] = []
        if v.band >= 1 and not expl:
            need.append("a written explanation (make perf-explain WHY=...)")
        if v.band >= 1 and "confirmation" not in have:
            need.append("a perf-audit confirmation (make perf-confirm VERDICT=consistent AS=perf-audit, by the subagent)")
        if v.band >= 2 and "audit" not in have:
            need.append("the escalated audit (make perf-audit VERDICT=justified NECESSARY=... COMMENSURATE=... NO_WAY_AROUND=... AS=perf-audit)")
        if v.band >= 3 and "signoff" not in have:
            need.append("the GM's sign-off (make perf-signoff WHY=..., at a terminal)")
        head = f"[{env}] {v.cur['label']} vs {v.base['label']} at {v.cur['commit']}: band {v.band}" + (f" ({'; '.join(v.crossed)})" if v.crossed else "")
        if need:
            ok = False
            lines.append(head + " - MISSING: " + " | ".join(need))
            if negative:
                lines.append(f"    negative or inconclusive records do not count: {', '.join(negative)}")
            if stale:
                lines.append(f"    stale records (bound to other numbers or another commit): {', '.join(stale[-3:])}")
        else:
            lines.append(head + " - " + ("nothing owed" if v.band == 0 else "every owed record present and bound to these numbers"))
    return ok, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["explain", "confirm", "audit", "signoff", "check", "show"])
    ap.add_argument("--feature", default=os.environ.get("SPECIFY_FEATURE", ""))
    ap.add_argument("--environment", default="local")
    ap.add_argument("--log-dir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "dev", "perf-log"))
    ap.add_argument("--why", default="")
    ap.add_argument("--verdict", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--necessary", default="")
    ap.add_argument("--commensurate", default="")
    ap.add_argument("--no-way-around", default="")
    ap.add_argument("--as", dest="declared", default="main")
    ap.add_argument("--tty", default=None, help="signoff: override the terminal test (tests only)")
    a = ap.parse_args(argv)
    log_dir = Path(a.log_dir)
    if not a.feature:
        # THE PUSH RUNS `check` ON EVERY PUSH, feature or not. A docs-only push carries no feature and
        # owes nothing; an engine push without one is refused by the gated route's own
        # feature-complete condition (feature 130). Found by the first direct push after 129 landed.
        if a.command == "check":
            print("perf-review: no feature named (SPECIFY_FEATURE unset) - nothing to review; an engine delta without a feature is refused at the gated route")
            return 0
        print("perf-review: no feature named - export SPECIFY_FEATURE=NNN-slug", file=sys.stderr)
        return 2
    if a.command == "check":
        ok, text = check(log_dir, a.feature)
        print(text)
        if not ok:
            print(
                "\nperf-review: REFUSED - the bands above are the GM's (2026-08-24); the push waits for the records named. `make perf-report` shows the delta and the stages that grew.",
                file=sys.stderr,
            )
        return 0 if ok else 1
    vs = pairs(log_dir, a.feature)
    if a.environment not in vs:
        print(
            f"perf-review: no {feature_number(a.feature)}-start/-end pair for environment {a.environment!r} (have: {sorted(vs) or 'none'}) - take the bookends first (make perf LABEL={feature_number(a.feature)}-start / -end)",
            file=sys.stderr,
        )
        return 2
    v = vs[a.environment]
    if a.command == "show":
        print(perf_bands.render(v))
        return 0
    if a.command == "explain":
        if not a.why.strip():
            print("perf-review: explain needs WHY=<what caused the change> - a machine-written line is noticed, not explained (constitution VI)", file=sys.stderr)
            return 2
        p = write(log_dir, a.feature, v, "explanation", "pending", "main", explanation=a.why, render=perf_bands.render(v), stage_delta={str(k): v2 for k, v2 in v.stage_delta.items()})
        print(f"perf-review: explanation recorded in {p.name} (band {v.band}); now the perf-audit subagent confirms it")
        return 0
    if a.command == "signoff":
        is_tty = (a.tty == "yes") if a.tty is not None else sys.stdin.isatty()
        if not is_tty:
            print(
                "perf-review: REFUSED - the GM's sign-off is given at a terminal, in person (band 3: 'I must personally sign off on this before it is committed back to main'). No terminal is attached.",
                file=sys.stderr,
            )
            return 1
        if not a.why.strip():
            print("perf-review: signoff needs WHY=<the GM's reason>", file=sys.stderr)
            return 2
        p = write(log_dir, a.feature, v, "signoff", "signed", "GM", note=a.why)
        print(f"perf-review: GM sign-off recorded in {p.name}")
        return 0
    # confirm / audit: the subagent's records
    if a.declared != "perf-audit":
        print(PROMPT, file=sys.stderr)
        return 1
    if a.command == "confirm":
        if a.verdict not in ("consistent", "inconsistent"):
            print("perf-review: confirm needs VERDICT=consistent|inconsistent (does the stated cause match the stage delta?)", file=sys.stderr)
            return 2
        p = write(log_dir, a.feature, v, "confirmation", a.verdict, "perf-audit", note=a.note)
        print(f"perf-review: confirmation ({a.verdict}) recorded in {p.name}" + ("" if a.verdict == "consistent" else " - an INCONSISTENT explanation does not pass; the session rewrites it"))
        return 0
    if a.verdict not in ("justified", "not-justified", "cannot-determine"):
        print("perf-review: audit needs VERDICT=justified|not-justified|cannot-determine", file=sys.stderr)
        return 2
    crit = {"necessary": a.necessary, "commensurate": a.commensurate, "no_way_around": a.no_way_around}
    missing = [k for k, t in crit.items() if not t.strip()]
    if missing:
        print(f"perf-review: audit must address each criterion SEPARATELY (FR-003a) - missing: {', '.join(missing)} (NECESSARY= COMMENSURATE= NO_WAY_AROUND=)", file=sys.stderr)
        return 2
    p = write(log_dir, a.feature, v, "audit", a.verdict, "perf-audit", criteria=crit, note=a.note)
    print(f"perf-review: audit ({a.verdict}) recorded in {p.name}" + ("" if a.verdict == "justified" else " - only `justified` lets the work proceed"))
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_review")
    raise SystemExit(main())
