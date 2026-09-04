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


def machine_of(snap: dict[str, Any]) -> tuple[str, str]:
    """The MACHINE a snapshot was taken on: `(host, image)`.

    `host` is `codebuild:<COMPUTE_TYPE>` in a build (`perf_snapshot.machine_identity`), so this is
    what separates a 36-vCPU run from an 8-vCPU one. Feature 178 needs it because item 5 puts several
    instance types into one environment for the first time."""
    return (str(snap.get("host", "laptop")), str(snap.get("image", "laptop")))


def has_start_for_this_machine(log_dir: Path, feature: str) -> bool:
    """Is there a `<n>-start` for this feature taken on the machine we are running on NOW?

    THE DEFECT THIS REPLACES (feature 179, constitution Principle XIV). `perf-gate`'s in-build branch
    guarded on `ls dev/perf-log/*<n>-start*codebuild*.json` - a FILENAME test. `perf_snapshot.record`
    names files `{stamp}-{label}-{clone}.json`, where the last field is a clone name, so the string
    `codebuild` never appears in one: 0 of the 44 snapshots on record matched, the test was
    unconditionally false, and every remote FULL build re-took a `-start` bookend against pre-merge
    main whether or not it already had one. That is a full `make perf` run, roughly half of
    `perf-gate`'s time, paid on every remote build.

    Asking the SNAPSHOT is also STRICTER than the filename test was ever trying to be: a filename
    match would have accepted an XLARGE `-start` for an 8-vCPU `-end`, which is exactly the
    cross-machine comparison feature 178's FR-008 exists to refuse.

    ONE BEHAVIORAL CHANGE, stated here because it is the point of change: a SECOND remote build of
    the same feature now REUSES the earlier same-machine `-start` instead of re-taking one against
    the current `origin/main`, so a delta can span main's own landings between the two builds. That
    is the restored feature-130 intent and is the better baseline under Principle VI, which wants the
    bookend taken on unmodified code before the first edit - not re-based each time main moves.

    The downstream refusal is untouched: if NO `-start` exists at all, `perf-gate` still fails."""
    from l7r.diagram.tools import perf_snapshot

    n = feature_number(feature)
    if not n:
        return False
    here = perf_snapshot.machine_identity()
    want = (str(here.get("host", "laptop")), str(here.get("image", "laptop")))
    for s in _snapshots(log_dir):
        label = str(s.get("label", ""))
        if feature_number(label) == n and label.endswith("-start") and machine_of(s) == want:
            return True
    return False


def pairs(log_dir: Path, feature: str) -> dict[str, perf_bands.Verdict]:
    """The newest `<n>-start` / `<n>-end` pair for this feature, per environment AND per MACHINE.

    **WHY THE MACHINE JOINS THE KEY (feature 178, FR-008).** This grouped by environment alone, and
    `perf_bands.evaluate` refuses only on an environment mismatch - so once feature 178's item 5 runs
    the same feature on `BUILD_GENERAL1_LARGE` and `BUILD_GENERAL1_XLARGE`, an xlarge `-start` and an
    8-vCPU `-end` are both `codebuild`, pair happily, and yield a percentage that is pure instance
    difference. Nothing would have refused it and the number would have read as a regression. That is
    feature 129's own FR-014 argument - *"a cross-environment percentage is indistinguishable from a
    regression"* - one level down, and item 5 is what makes it live.

    A pair is formed only from snapshots taken on the SAME machine; the newest `-end` chooses, and the
    baseline is the newest `-start` that matches it. An `-end` with no matching `-start` yields no
    verdict rather than a wrong one, which is what FR-009 reports on."""
    n = feature_number(feature)
    by_key: dict[tuple[str, tuple[str, str]], dict[str, dict[str, Any]]] = {}
    for s in _snapshots(log_dir):
        label = str(s.get("label", ""))
        if label not in (f"{n}-start", f"{n}-end"):
            continue
        key = (perf_bands.environment_of(s), machine_of(s))
        by_key.setdefault(key, {})[label.split("-")[1]] = s  # newest wins: files sort by utc
    out: dict[str, perf_bands.Verdict] = {}
    for (env, machine), d in by_key.items():
        if "start" in d and "end" in d:
            # one environment can now hold several machines, so the key says which
            name = env if machine[0] in ("laptop", "") else f"{env}:{machine[0].split(':', 1)[-1]}"
            out[name] = perf_bands.evaluate(d["start"], d["end"])
    return out


def unpaired(log_dir: Path, feature: str) -> list[str]:
    """Every `<n>-end` with no `-start` from the same machine - FR-009's "nothing to compare against".

    A first run on a new instance type has no prior of its own, and a `make ci-image` rebuild changes
    `image` and so retires every codebuild baseline at once. Neither is a regression, and neither may
    quietly pass for one - or quietly pass for nothing."""
    n = feature_number(feature)
    seen: dict[tuple[str, tuple[str, str]], set[str]] = {}
    for s in _snapshots(log_dir):
        label = str(s.get("label", ""))
        if label in (f"{n}-start", f"{n}-end"):
            seen.setdefault((perf_bands.environment_of(s), machine_of(s)), set()).add(label.split("-")[1])
    return sorted(f"{env} on {machine[0]}" for (env, machine), kinds in seen.items() if "end" in kinds and "start" not in kinds)


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
    # FR-009: an `-end` with no `-start` on the SAME machine has nothing to regress against - a first
    # run on a new instance type, or every codebuild baseline at once after a `make ci-image` rebuild
    # changes the image. That must not fail the gate, and it must not pass in silence either: a gate
    # that has gone mute is exactly the state this project calls worse than a red one, because it
    # looks identical to a green.
    mute = unpaired(log_dir, feature)
    mute_note = ("\nperf-review: NO COMPARABLE BASELINE for " + ", ".join(mute) + " - the perf gate is MUTE for these, not green (feature 178, FR-009)") if mute else ""
    if not vs:
        return True, f"perf-review: no {feature_number(feature)}-start/-end pair in any environment - nothing to review (perf-gate refuses a missing bookend on its own){mute_note}"
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
    return ok, "\n".join(lines) + mute_note


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["explain", "confirm", "audit", "signoff", "check", "show", "has-start"])
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
    if a.command == "has-start":
        # FR-017: the in-build bookend guard, asking the SNAPSHOT rather than the filename.
        return 0 if has_start_for_this_machine(log_dir, a.feature) else 1
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
