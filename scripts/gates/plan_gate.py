#!/usr/bin/env python3
"""A plan's decisions are reviewed before its tasks are ticked (feature 243).

    python3 scripts/gates/plan_gate.py owed <spec_dir>              the reason a feature may not tick, or nothing
    python3 scripts/gates/plan_gate.py push [<range>]               every touched feature with a tick and no CLEAR review
    python3 scripts/gates/plan_gate.py record <spec_dir> <json> --as <who>   write plan-review.json

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

#: Words a "typo" may never touch (feature 375 FR-005(b), plan D6): a number, a quantity, a negation or a quantifier changes a
#: decision however few letters it moves - "two" -> "ten", "all" -> "any", "must" -> "may".
GUARDED = frozenset(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen "
    "nineteen twenty thirty forty fifty hundred thousand first second third fourth fifth sixth seventh eighth ninth tenth half "
    "twice once double triple not no never none except unless only all any each every some few many most more less fewer "
    "may must should shall can cannot before after above below over under min max least".split()
)
#: How many words a typo-scale edit may change in the whole plan
TYPO_WORDS = 3
_WORD = re.compile(r"[A-Za-z0-9]+")


def _distance(a: str, b: str) -> int:
    """The Damerau-Levenshtein distance of two short words (a transposition is one edit)."""
    prev2: list[int] = []
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            if i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[-1]


def typo_only(old: str, new: str) -> bool:
    """Whether `new` differs from `old` by typos alone (FR-005(b), plan D6): whitespace, re-wrapping, case and punctuation; at
    most TYPO_WORDS words replaced, each by a near spelling (one letter for a word of four or fewer, two beyond), none of them a
    digit or a GUARDED word; no word added or removed. Anything else adds or changes a decision, and voids the verdict - the
    conservative side, since a missed decision is the incident this gate exists for (feature 239)."""
    a, b = _WORD.findall(old.lower()), _WORD.findall(new.lower())
    if len(a) != len(b):
        return False
    changed = [(x, y) for x, y in zip(a, b, strict=True) if x != y]
    if len(changed) > TYPO_WORDS:
        return False
    for x, y in changed:
        if x in GUARDED or y in GUARDED or any(c.isdigit() for c in x + y):
            return False
        if _distance(x, y) > (1 if min(len(x), len(y)) <= 4 else 2):
            return False
    return True


_HEAD = re.compile(r"^(#{2,4})\s+(.*)$", re.M)
_TASK_ID = re.compile(r"\b(T\d+[a-z]?)\b")


def task_sections(plan_text: str) -> dict[str, str]:
    """`{task id: its section}` - every `##`-`####` heading of the plan naming a task id, to the next heading at its level or
    above (feature 375, FR-003(a), plan D3): the decisions of that task, which a decision preflight rules on alone."""
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in _HEAD.finditer(plan_text)]
    out: dict[str, str] = {}
    for i, (at, level, title) in enumerate(heads):
        ids = _TASK_ID.findall(title)
        if not ids:
            continue
        end = next((a for a, lv, _t in heads[i + 1:] if lv <= level), len(plan_text))
        for t in ids:
            out.setdefault(t, plan_text[at:end])
    return out


def task_current(review: dict, plan_text: str, task: str) -> bool:
    """Whether the task's section carries a CLEAR decision verdict that still matches it (a typo aside, as D6)."""
    section = task_sections(plan_text).get(task)
    entry = (review.get("tasks") or {}).get(task) or {}
    if section is None or entry.get("verdict") != "CLEAR":
        return False
    return entry.get("section_sha256") == digest(section.encode()) or typo_only(str(entry.get("section_text") or ""), section)


def _without(plan_text: str, ids: set[str]) -> str:
    """The plan with the sections of `ids` taken out."""
    for t, sec in task_sections(plan_text).items():
        if t in ids:
            plan_text = plan_text.replace(sec, "")
    return plan_text


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
    text = plan.decode("utf-8", "replace")
    # every task section that carries its own current verdict (a decision preflight, plan D3) is out of the comparison, in the
    # reviewed text and in today's: adding or changing it does not stale the plan-stage verdict
    ruled = {t for t in task_sections(text) if task_current(review, text, t)}
    if review.get("plan_sha256") != digest(plan) and not typo_only(_without(str(review.get("plan_text") or ""), ruled),
                                                                   _without(text, ruled)):
        return "plan-review-stale", (f"plan.md changed after its review by more than a typo (FR-004; feature 375 FR-005(b): "
                                     f"a word added or removed, a number, a negation or a quantifier) - {HOW}")
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
    """One entry in the guard census, through the same `guardlog.sh` every shell guard uses."""
    subprocess.run(["bash", "-c", '. "$1/../hooks/lib/guardlog.sh"; guard_log plan-gate "$2" "$3" "$4"', "_", str(HERE),
                    event, detail[:400], rule], capture_output=True)


def reason_ok(reason: str) -> bool:
    return subprocess.run([sys.executable, str(HERE / "../hooks/lib/hm_escape.py"), "reason-ok"], input=reason,
                          capture_output=True, text=True).returncode == 0


def bypass_record(root: pathlib.Path, where: str, why: str) -> None:
    """The reason ships with the push: `dev/bypass-log/` is in the repository and `make audit` lists it."""
    log = root / "dev" / "bypass-log"
    if not log.parent.is_dir():
        return
    now = datetime.datetime.now(datetime.UTC)
    log = log / f"{now:%Y-%m}"  # a month folder (2026-10-02)
    log.mkdir(parents=True, exist_ok=True)
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


def record_task(spec_dir: pathlib.Path, task: str, review: dict, declared: str, today: str | None = None) -> dict:
    """A decision preflight's verdict on one task's section (feature 375, FR-003(a), plan D3/D19), kept under `tasks.<id>`."""
    if declared != REVIEWER:
        raise PermissionError(f"declined: only the `{REVIEWER}` subagent records a decision preflight (AS={REVIEWER})")
    plan = spec_dir / "plan.md"
    section = task_sections(plan.read_text(encoding="utf-8") if plan.is_file() else "").get(task)
    if section is None:
        raise ValueError(f"plan.md has no section naming {task} - a task's decisions go under a heading that names it")
    if review.get("section_sha256") != digest(section.encode()):
        raise ValueError(f"section_sha256 does not match {task}'s section - it changed while it was being reviewed")
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("decisions must be a list")
    verdict = derive_verdict(decisions)
    rec_path = spec_dir / RECORD
    out = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.is_file() else {"feature": spec_dir.name}
    out.setdefault("tasks", {})[task] = {"section_sha256": review["section_sha256"], "section_text": section,
                                         "reviewed": today or datetime.date.today().isoformat(), "declared": declared,
                                         "decisions": decisions, "verdict": verdict}
    rec_path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out["tasks"][task]


def active_task(root: pathlib.Path) -> tuple[pathlib.Path | None, str]:
    """(the active feature's directory, its active task): `.git/active-task` (`make task-start`) when it names this feature,
    else the first open task of `.specify/feature.json`'s feature; (None, '') when no feature is active."""
    try:
        fd = json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", "")
    except (OSError, ValueError):
        return None, ""
    d = root / str(fd).rstrip("/")
    if not fd or not (d / "tasks.md").is_file():
        return None, ""
    common = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True).stdout.strip()
    try:
        mark = json.loads((pathlib.Path(common) / "active-task").read_text(encoding="utf-8")) if common else {}
    except (OSError, ValueError):
        mark = {}
    if mark.get("feature") == d.name and mark.get("task"):
        return d, str(mark["task"])
    m = re.search(r"^- \[ \] (T\d+[a-z]?)\b", (d / "tasks.md").read_text(encoding="utf-8"), re.M)
    return d, (m.group(1) if m else "")


def decision_refusal(root: pathlib.Path) -> str:
    """Why a check may not be dispatched yet (feature 375, FR-003(a)): the active task's decisions carry no current CLEAR
    verdict - its own section's (`make decide`), or, where the plan has no section for it, the plan-stage verdict."""
    d, task = active_task(root)
    if d is None or not task:
        return ""
    plan = d / "plan.md"
    text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    try:
        review = json.loads((d / RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        review = {}
    if task in task_sections(text):
        if task_current(review, text, task):
            return ""
        return (f"{d.name} {task}: its plan section carries no current CLEAR decision verdict - decide first, then check "
                f"(feature 375 FR-003a): `make decide F={d.name.split('-')[0]} T={task}` names the review to dispatch")
    verdict = owed(d)
    return "" if verdict is None else (f"{d.name} {task}: the plan has no section for this task and its plan-stage review is "
                                       f"not current and CLEAR ({verdict[0]}) - decide first (feature 375 FR-003a): {verdict[1]}")


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
    rec_path = spec_dir / RECORD
    kept = json.loads(rec_path.read_text(encoding="utf-8")).get("tasks", {}) if rec_path.is_file() else {}
    out = {"feature": spec_dir.name, "plan_sha256": review["plan_sha256"], **({"tasks": kept} if kept else {}),
           "plan_text": plan.read_text(encoding="utf-8"),  # feature 375 FR-005(b): what a later typo is measured against
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


def decide_prompt(spec_dir: pathlib.Path, task: str) -> str:
    """The dispatch `make decide` prints: a plan review of ONE task's section (plan D19 - a MODE 4 review, so the review-round
    hook never reroutes it), recorded under `tasks.<id>`."""
    rel = f"specs/{spec_dir.name}"
    return (f"MODE 4: PLAN REVIEW of one task's section - feature {spec_dir.name}, task {task} (a decision preflight, feature 375 "
            f"FR-003a). Read {rel}/request.md and {rel}/spec.md, then ONLY the section of {rel}/plan.md whose heading names {task}. "
            f"Take the section's sha256 first (the bytes from its heading line to the next heading at its level or above; "
            f"`make section-sha F={spec_dir.name.split('-')[0]} T={task}` prints it), find its decisions, rule on each narrowing, "
            f"write the JSON with `section_sha256` in place of `plan_sha256`, and record it with "
            f"`make plan-verdict F={spec_dir.name.split('-')[0]} TASK={task} FILE=<json> AS=spec-fidelity`.")


def main(argv: list[str]) -> int:
    if argv[:1] == ["decided"]:
        why = decision_refusal(pathlib.Path(argv[1] if len(argv) > 1 else "."))
        if why:
            print(why)
        return 1 if why else 0
    if argv[:1] in (["decide"], ["section-sha"]) and len(argv) == 3:
        d = resolve(argv[1])
        section = task_sections((d / "plan.md").read_text(encoding="utf-8")).get(argv[2]) if d and (d / "plan.md").is_file() else None
        if d is None or section is None:
            print(f"{argv[0]}: no plan section names {argv[2]} in specs/{argv[1]}* - put the task's decisions under a heading that names it", file=sys.stderr)
            return 2
        print(digest(section.encode()) if argv[0] == "section-sha" else decide_prompt(d, argv[2]))
        return 0
    if argv[:1] == ["task-start"] and len(argv) == 3:
        d = resolve(argv[1])
        if d is None:
            print(f"task-start: no single specs/{argv[1]}* directory", file=sys.stderr)
            return 2
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
        pathlib.Path(common, "active-task").write_text(json.dumps({"feature": d.name, "task": argv[2]}) + "\n", encoding="utf-8")
        print(f"task-start: {d.name} {argv[2]} is the active task - its checks need its decisions ruled first (make decide)")
        return 0
    if argv[:1] == ["record-task"] and len(argv) == 6 and argv[4] == "--as":
        spec_dir = resolve(argv[1])
        if spec_dir is None:
            print(f"plan-verdict: no single specs/{argv[1]}* directory", file=sys.stderr)
            return 2
        try:
            out = record_task(spec_dir, argv[2], json.loads(pathlib.Path(argv[3]).read_text(encoding="utf-8")), argv[5])
        except PermissionError as e:
            print(f"plan-verdict: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"plan-verdict: refused - {e}", file=sys.stderr)
            return 1
        print(f"plan-verdict: {out['verdict']} recorded for {spec_dir.name} {argv[2]} ({len(out['decisions'])} decision(s))")
        return 0
    if argv[:1] == ["owed"] and len(argv) == 2:
        verdict = owed(pathlib.Path(argv[1]))
        if verdict:
            print(f"{verdict[0]}\t{verdict[1]}")
        return 1 if verdict else 0
    if argv[:1] == ["push"]:
        root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                                           text=True).stdout.strip())
        found = push_owed(root, argv[1] if len(argv) > 1 else "origin/main...HEAD")  # the merge base: see review-gate.sh
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
