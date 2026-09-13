#!/usr/bin/env python3
"""A plan's decisions are reviewed before its tasks are ticked (feature 243).

    python3 scripts/_plan_gate.py owed <spec_dir>              the reason a feature may not tick, or nothing
    python3 scripts/_plan_gate.py push [<range>]               every touched feature with a tick and no CLEAR review
    python3 scripts/_plan_gate.py record <spec_dir> <json> --as <who>   write plan-review.json

WHY. Constitution XVI puts an independent check in front of every exception, and `review-gate.sh` holds
that for a SPEC. A plan is written after the spec's verdict and nothing read it, so a plan decision that
narrowed the spec reached ticked tasks and main unchecked: feature 239's P2 did exactly that, framed as an
open question rather than a narrowing (`specs/243-*/research.md` R1). So the reviewer reads the WHOLE
plan and finds the decisions itself - an author who did not see a narrowing would not have labeled one.

WHERE IT HOLDS. `make tick` asks `owed()` before it ticks; the push asks `push` over the features its
delta touches, because a box can be ticked by a hand edit and nothing refuses that (spec D4). Both take
`PLAN_REVIEW_OK="<reason>"` from the environment.

WHO MAY RECORD. `record` declines unless the caller declares itself `spec-fidelity`. Nothing distinguishes
the shells, so the declaration is recorded rather than proven - the limit `make perf-confirm AS=perf-audit`
already states.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

RECORD = "plan-review.json"
REVIEWER = "spec-fidelity"
CLASSES = ("within", "narrowing")
RULINGS = ("LEGITIMATE", "NOT LEGITIMATE")
# P4: the line `make tick` writes, and the line a hand edit makes. An indented research box is part of its
# task, not a task of its own.
_TICKED = re.compile(r"^- \[[xX]\] ", re.M)

HOW = ("dispatch `spec-fidelity` in its PLAN REVIEW mode with request.md, spec.md and plan.md, then record "
       "its JSON: make plan-verdict F=<feature> FILE=<json> AS=spec-fidelity")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ticked(tasks_text: str) -> int:
    return len(_TICKED.findall(tasks_text))


def judge(plan: bytes | None, review_text: str | None) -> tuple[str, str] | None:
    """(rule, reason) when a feature owes a plan review, from the plan's bytes and the record's text."""
    if plan is None:
        return "plan-missing", f"no plan.md - the plan stage is owed before its review can be (spec D5); then {HOW}"
    if review_text is None:
        return "plan-review-missing", f"no {RECORD} - {HOW}"
    try:
        review = json.loads(review_text)
    except ValueError:
        return "plan-review-missing", f"{RECORD} is not JSON - {HOW}"
    if review.get("plan_sha256") != digest(plan):
        return "plan-review-stale", f"plan.md changed after its review (FR-004) - {HOW}"
    if review.get("verdict") != "CLEAR":
        narrowing = [d.get("id", "?") for d in review.get("decisions", []) if d.get("ruling") == "NOT LEGITIMATE"]
        return "plan-review-blocked", (f"the plan review is BLOCKED ({', '.join(narrowing) or 'no ruling named'} ruled "
                                       f"NOT LEGITIMATE) - withdraw or overrule the decision in plan.md, then {HOW}")
    return None


def owed(spec_dir: pathlib.Path) -> tuple[str, str] | None:
    plan, review = spec_dir / "plan.md", spec_dir / RECORD
    return judge(plan.read_bytes() if plan.is_file() else None,
                 review.read_text(encoding="utf-8") if review.is_file() else None)


# ---- the escape and the record of it (FR-008) ----------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent


def guard_log(event: str, detail: str, rule: str) -> None:
    """One entry in the guard census, through the same `_guardlog.sh` every shell guard uses."""
    subprocess.run(["bash", "-c", '. "$1/_guardlog.sh"; guard_log plan-gate "$2" "$3" "$4"', "_", str(HERE),
                    event, detail[:400], rule], capture_output=True)


def reason_ok(reason: str) -> bool:
    return subprocess.run([sys.executable, str(HERE / "_hm_escape.py"), "reason-ok"], input=reason,
                          capture_output=True, text=True).returncode == 0


def bypass_record(root: pathlib.Path, where: str, why: str) -> None:
    """The reason ships with the push: `dev/bypass-log/` is in the repository and `make audit` lists it."""
    log = root / ".claude" / "skills" / "diagram" / "dev" / "bypass-log"
    if not log.parent.is_dir():
        return
    log.mkdir(exist_ok=True)
    now = datetime.datetime.now(datetime.UTC)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    (log / f"{now:%Y%m%dT%H%M%SZ}-{hashlib.sha256(why.encode()).hexdigest()[:6]}.json").write_text(
        json.dumps({"utc": f"{now:%Y-%m-%dT%H:%M:%SZ}", "target": f"plan-gate {where}", "commit": head,
                    "why": why}, indent=2) + "\n", encoding="utf-8")


def tick_permitted(spec_dir: pathlib.Path, root: pathlib.Path, escape: str | None) -> tuple[bool, str]:
    """FR-001/FR-005/FR-008 for `make tick`: (may tick, what to print)."""
    verdict = owed(spec_dir)
    if verdict is None:
        return True, ""
    rule, reason = verdict
    if not escape:
        guard_log("blocked", f"{spec_dir.name}: {reason}", rule)
        return False, (f"tick: refused - {spec_dir.name}'s plan decisions have no current CLEAR review (feature 243).\n"
                       f"  {reason}\n  A case that is genuinely exempt: PLAN_REVIEW_OK=\"<reason>\", which is recorded.")
    if not reason_ok(escape):
        guard_log("blocked", escape, "PLAN_REVIEW_OK-no-reason")
        return False, "tick: PLAN_REVIEW_OK needs a REASON, not just a value - two words and eight characters."
    guard_log("escaped", f"{spec_dir.name}: {escape}", "plan-review-ok")
    bypass_record(root, f"tick {spec_dir.name}", escape)
    return True, f"tick: plan gate BYPASSED - {escape} (recorded in dev/bypass-log/)"


# ---- recording (FR-003, FR-006) ------------------------------------------------------------------------

def derive_verdict(decisions: list[dict]) -> str:
    """P2: CLEAR unless a narrowing decision stands ruled NOT LEGITIMATE; refuses a malformed decision."""
    for d in decisions:
        cls, ruling = d.get("class"), d.get("ruling")
        if cls not in CLASSES:
            raise ValueError(f"decision {d.get('id', '?')}: class must be one of {CLASSES}, not {cls!r}")
        if cls == "narrowing" and ruling not in RULINGS:
            raise ValueError(f"decision {d.get('id', '?')}: a narrowing decision needs a ruling from {RULINGS}")
        if cls == "within" and ruling is not None:
            raise ValueError(f"decision {d.get('id', '?')}: a decision within what was asked carries no ruling")
        if not d.get("id") or not d.get("summary"):
            raise ValueError("every decision needs an id and a summary")
    return "BLOCKED" if any(d.get("ruling") == "NOT LEGITIMATE" for d in decisions) else "CLEAR"


def record(spec_dir: pathlib.Path, review: dict, declared: str, today: str | None = None) -> dict:
    if declared != REVIEWER:
        raise PermissionError(f"declined: only the `{REVIEWER}` subagent records a plan review (AS={REVIEWER}). "
                              f"Nothing distinguishes the shells, so this is a declaration, recorded - not a proof.")
    plan = spec_dir / "plan.md"
    if not plan.is_file():
        raise ValueError(f"{spec_dir.name} has no plan.md to have reviewed")
    if review.get("plan_sha256") != digest(plan.read_bytes()):
        raise ValueError("plan_sha256 does not match plan.md - the plan changed while it was being reviewed "
                         "(P1), so this review is of a plan that no longer exists; review it again")
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("decisions must be a list (empty when the spec settles everything the plan decides)")
    verdict = derive_verdict(decisions)
    if review.get("verdict") not in (None, verdict):
        raise ValueError(f"the input says {review['verdict']} but its rulings make it {verdict} (P2)")
    out = {"feature": spec_dir.name, "plan_sha256": review["plan_sha256"],
           "reviewed": today or datetime.date.today().isoformat(), "declared": declared,
           "decisions": decisions, "verdict": verdict}
    (spec_dir / RECORD).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


# ---- the push (FR-007) ---------------------------------------------------------------------------------

def _show(root: pathlib.Path, ref: str, path: str) -> bytes | None:
    run = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{path}"], capture_output=True)
    return run.stdout if run.returncode == 0 else None


def touched_features(root: pathlib.Path, rng: str) -> list[str]:
    """P5: every `specs/NNN-*` directory the range touches - review-gate.sh check 1's set."""
    names = subprocess.run(["git", "-C", str(root), "diff", "--name-only", rng], capture_output=True, text=True)
    return sorted({m.group(1) for m in re.finditer(r"^(specs/[^/]+)/", names.stdout, re.M)})


def push_owed(root: pathlib.Path, rng: str, ref: str = "HEAD") -> list[tuple[str, str, str]]:
    """(feature dir, rule, reason) for each touched feature with a ticked task and no current CLEAR review."""
    out = []
    for feature in touched_features(root, rng):
        tasks = _show(root, ref, f"{feature}/tasks.md")
        if tasks is None or not ticked(tasks.decode("utf-8", "replace")):
            continue
        review = _show(root, ref, f"{feature}/{RECORD}")
        verdict = judge(_show(root, ref, f"{feature}/plan.md"), review.decode("utf-8") if review is not None else None)
        if verdict:
            out.append((feature, *verdict))
    return out


def resolve(feature: str, root: pathlib.Path | None = None) -> pathlib.Path | None:
    """A spec directory from a path, a number (`243`) or a directory name - None when not exactly one."""
    if pathlib.Path(feature).is_dir():
        return pathlib.Path(feature)
    if "/" in feature:  # a path that does not exist is not a feature name to glob for
        return None
    root = root or pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                                               text=True).stdout.strip())
    exact = root / "specs" / feature
    if exact.is_dir():
        return exact
    hits = sorted(p for p in (root / "specs").glob(f"{feature}-*") if p.is_dir())
    return hits[0] if len(hits) == 1 else None


def main(argv: list[str]) -> int:
    if argv[:1] == ["owed"] and len(argv) == 2:
        verdict = owed(pathlib.Path(argv[1]))
        if verdict:
            print(f"{verdict[0]}\t{verdict[1]}")
        return 1 if verdict else 0
    if argv[:1] == ["push"]:
        root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                                           text=True).stdout.strip())
        found = push_owed(root, argv[1] if len(argv) > 1 else "origin/main..HEAD")
        for feature, rule, reason in found:
            print(f"{feature}\t{rule}\t{reason}")
        return 1 if found else 0
    if argv[:1] == ["record"] and len(argv) == 5 and argv[3] == "--as":
        spec_dir, source = resolve(argv[1]), pathlib.Path(argv[2])
        if spec_dir is None:
            print(f"plan-verdict: no single specs/{argv[1]}* directory - F=<feature number or slug>", file=sys.stderr)
            return 2
        try:
            out = record(spec_dir, json.loads(source.read_text(encoding="utf-8")), argv[4])
        except PermissionError as e:
            print(f"plan-verdict: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"plan-verdict: refused - {e}", file=sys.stderr)
            return 1
        print(f"plan-verdict: {out['verdict']} recorded in {spec_dir.name}/{RECORD} "
              f"({len(out['decisions'])} decision(s))")
        return 0
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
