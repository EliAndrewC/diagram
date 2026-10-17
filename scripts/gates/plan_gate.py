#!/usr/bin/env python3
"""A plan's decisions are reviewed before its tasks are ticked (feature 243).

    python3 scripts/gates/plan_gate.py owed <spec_dir>              the reason a feature may not tick, or nothing
    python3 scripts/gates/plan_gate.py push [<range>]               every touched feature with a tick and no CLEAR review
    python3 scripts/gates/plan_gate.py record <spec_dir> <json> --as <who>   write plan-review.json
    python3 scripts/gates/plan_gate.py record-blocks <spec_dir> <json> --as <who>   record a review of changed blocks
    python3 scripts/gates/plan_gate.py delta|archive|slim <spec_dir>          (amendment 11) owed blocks' bundle; finished
                                                                              sections out; the record without the plan copy

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


def task_current(review: dict, plan_text: str, task: str, history: History | None = None) -> bool:
    """Whether the task's section carries a CLEAR decision verdict that still matches it (a typo aside, as D6) - its earlier
    text from the record where an old record kept it, else from the plan's history (amendment 11, D63)."""
    section = task_sections(plan_text).get(task)
    entry = (review.get("tasks") or {}).get(task) or {}
    if section is None or entry.get("verdict") != "CLEAR":
        return False
    if entry.get("section_sha256") == digest(section.encode()):
        return True
    earlier = entry.get("section_text") or (history.section(task, str(entry.get("section_sha256"))) if history else None)
    return earlier is not None and typo_only(str(earlier), section)


def _without(plan_text: str, ids: set[str]) -> str:
    """The plan with the sections of `ids` taken out."""
    for t, sec in task_sections(plan_text).items():
        if t in ids:
            plan_text = plan_text.replace(sec, "")
    return plan_text


# ---- feature 375 amendment 11 (the GM 2026-10-13): a plan reviewed by its changed blocks -------------------------------------
#: "Is feature 374 growing too large in a way that eats tokens" - sixteen whole-plan reviews of 374 cost 13.7 million input
#: tokens, each re-judging every earlier decision because one edit outside a task's section staled the whole plan's verdict.
_ANY_HEAD = re.compile(r"^#{2,4}\s.*$", re.M)
#: the line `make plan-archive` leaves where finished sections were (FR-044): taken out of every digest, so it owes no review
ARCHIVE_LINE = re.compile(r"^<!-- plan-archive: [^\n]*? -->\n?", re.M)
HISTORY_CHUNK = 25  # versions of plan.md read per `cat-file --batch` while a block's earlier text is sought (D63)


def blocks(plan_text: str) -> list[tuple[str, str, int]]:
    """(key, text, offset) of every block (D60, FR-043): each heading line (`##` to `####`) to the next such heading, and the
    text before the first one (the title with it) as `preamble`. A repeated heading's key gets `#2`, `#3`."""
    heads = list(_ANY_HEAD.finditer(plan_text))
    out = [("preamble", plan_text[: heads[0].start()] if heads else plan_text, 0)]
    seen: dict[str, int] = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(plan_text)
        key = m.group(0).strip()
        seen[key] = seen.get(key, 0) + 1
        out.append((key if seen[key] == 1 else f"{key}#{seen[key]}", plan_text[m.start():end], m.start()))
    return out


def block_digest(text: str) -> str:
    return digest(ARCHIVE_LINE.sub("", text).encode())


class History:
    """The texts of plan.md's earlier versions (D63), newest first, read in chunks of HISTORY_CHUNK by one `cat-file --batch`
    each, only as far back as a question needs - the whole history when the text sought is not there (the plan review: a cap
    of 60 would have dropped a typo's verdict on 374, whose plan already had 61 versions). Where nothing can be read (no git,
    no history) it knows nothing, and a block's earlier text found nowhere is no typo - the conservative side."""

    def __init__(self, plan_path: pathlib.Path | None, ref: str = "HEAD") -> None:
        self.path, self.ref = plan_path, ref
        self._revs: list[str] | None = None
        self._texts: list[str] = []

    def _git(self, *args: str, data: bytes | None = None) -> bytes:
        return subprocess.run(["git", "-C", str(self.path.parent), *args], input=data, capture_output=True).stdout  # type: ignore[union-attr]

    def texts(self):  # noqa: ANN201 - a generator of str
        if self.path is None or not self.path.parent.is_dir():
            return
        if self._revs is None:
            rel = self._git("ls-files", "--full-name", "--", self.path.name).decode().strip()
            rel = rel or self._git("rev-parse", "--show-prefix").decode().strip() + self.path.name
            self._rel = rel
            self._revs = self._git("log", "--format=%H", self.ref, "--", self.path.name).decode().split()
        yield from self._texts
        while len(self._texts) < len(self._revs):
            chunk = self._revs[len(self._texts): len(self._texts) + HISTORY_CHUNK]
            got, i = self._git("cat-file", "--batch", data="".join(f"{r}:{self._rel}\n" for r in chunk).encode()), 0
            for _ in chunk:
                nl = got.find(b"\n", i)
                head = got[i:nl].split()
                if len(head) < 3 or head[1] == b"missing":
                    self._texts.append("")
                    i = nl + 1
                    continue
                size = int(head[2])
                self._texts.append(got[nl + 1: nl + 1 + size].decode("utf-8", "replace"))
                i = nl + 1 + size + 1
            yield from self._texts[-len(chunk):]

    def block(self, key: str, sha: str) -> str | None:
        """The text a block had when its digest was `sha`, from the plan's history; None when no version held it."""
        for text in self.texts():
            for k, body, _at in blocks(text):
                if k == key and block_digest(body) == sha:
                    return body
        return None

    def section(self, task: str, sha: str) -> str | None:
        for text in self.texts():
            sec = task_sections(text).get(task)
            if sec is not None and digest(sec.encode()) == sha:
                return sec
        return None


def reviewed_blocks(review: dict) -> dict[str, dict]:
    """`{key: {sha256, verdict}}` the record holds (D60): its `blocks`, or - a record from before amendment 11 - its one verdict on
    each block of the `plan_text` it reviewed."""
    if isinstance(review.get("blocks"), dict):
        return review["blocks"]
    text = review.get("plan_text")
    if not isinstance(text, str):
        return {}
    return {k: {"sha256": block_digest(body), "verdict": review.get("verdict"), "text": body} for k, body, _at in blocks(text)}


REMOVED = "(removed) "


def block_status(review: dict, plan_text: str, ruled: set[str], history: History | None = None, done: str = "") -> tuple[list[str], list[str]]:
    """(the blocks owed a review, the blocks BLOCKED): every block outside a task section with its own current verdict, judged
    against the record's verdict at its digest, a typo-scale change (FR-005(b)) from its text at that digest aside. A recorded
    block that plan.md no longer has is owed too, as `(removed) <key>`, unless `plan-done.md` (`done`) holds it - the archive
    moved it (the plan review: a decision deleted by hand is a change like any other)."""
    out_of = [(plan_text.find(sec), plan_text.find(sec) + len(sec)) for t, sec in task_sections(plan_text).items() if t in ruled]
    have = reviewed_blocks(review)
    owed, blocked = [], []
    for key, body, at in blocks(plan_text):
        if any(lo <= at < hi for lo, hi in out_of if lo >= 0):
            continue
        if not ARCHIVE_LINE.sub("", body).strip() and key == "preamble":
            continue
        entry = have.get(key) or {}
        if entry.get("sha256") != block_digest(body):
            earlier = entry.get("text") or (history.block(key, str(entry.get("sha256"))) if history and entry.get("sha256") else None)
            if earlier is None or not typo_only(ARCHIVE_LINE.sub("", earlier), ARCHIVE_LINE.sub("", body)):
                owed.append(key)
                continue
        if entry.get("verdict") == "BLOCKED":
            blocked.append(key)
        elif entry.get("verdict") != "CLEAR":
            owed.append(key)
    now = {k for k, _b, _a in blocks(plan_text)}
    archived = {block_digest(b) for _k, b, _a in blocks(done)} if done else set()
    for key, entry in have.items():
        if key in now or key == "preamble" or not isinstance(entry, dict) or entry.get("sha256") in archived:
            continue
        owed.append(REMOVED + key)
    return owed, blocked


HOW = ("dispatch `spec-fidelity` in its PLAN REVIEW mode with request.md, spec.md and plan.md, then record "
       "its JSON: make plan-verdict F=<feature> FILE=<json> AS=spec-fidelity")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ticked(tasks_text: str) -> int:
    return len(_TICKED.findall(tasks_text))


def judge(plan: bytes | None, review_text: str | None, history: History | None = None, done: str = "") -> tuple[str, str] | None:
    """(rule, reason) when a feature owes a plan review, from the plan's bytes and the record's text. Since amendment 11 (D60)
    the record's verdict is kept per block, and only a block added or changed since its CLEAR verdict is owed."""
    if plan is None:
        return "plan-missing", f"no plan.md - the plan stage is owed before its review can be (spec D5); then {HOW}"
    if review_text is None:
        return "plan-review-missing", f"no {RECORD} - {HOW}"
    try:
        review = json.loads(review_text)
    except ValueError:
        return "plan-review-missing", f"{RECORD} is not JSON - {HOW}"
    text = plan.decode("utf-8", "replace")
    if not isinstance(review.get("blocks"), dict) and not isinstance(review.get("plan_text"), str) and review.get("plan_sha256") == digest(plan):
        # a whole-plan record that kept no text, of exactly this plan: its one verdict is every block's
        review = {**review, "blocks": {k: {"sha256": block_digest(b), "verdict": review.get("verdict")} for k, b, _a in blocks(text)}}
    # every task section that carries its own current verdict (a decision preflight, plan D3) is out of the comparison
    ruled = {t for t in task_sections(text) if task_current(review, text, t, history)}
    owed_keys, blocked = block_status(review, text, ruled, history, done)
    if owed_keys:
        shown = ", ".join(k[:60] for k in owed_keys[:5]) + (f" and {len(owed_keys) - 5} more" if len(owed_keys) > 5 else "")
        return "plan-review-stale", (f"{len(owed_keys)} block(s) of plan.md changed since their review by more than a typo (feature 375 "
                                     f"FR-043): {shown} - `make plan-delta F=<n>` builds the review of those blocks alone")
    if blocked or (review.get("verdict") not in (None, "CLEAR") and not isinstance(review.get("blocks"), dict)):
        narrowing = [d.get("id", "?") for d in review.get("decisions", []) if d.get("ruling") == "NOT LEGITIMATE"]
        return "plan-review-blocked", (f"the plan review is BLOCKED ({', '.join(narrowing) or 'no ruling named'} ruled "
                                       f"NOT LEGITIMATE) - withdraw or overrule the decision in plan.md, then {HOW}")
    return None


def owed(spec_dir: pathlib.Path) -> tuple[str, str] | None:
    plan, review = spec_dir / "plan.md", spec_dir / RECORD
    return judge(plan.read_bytes() if plan.is_file() else None,
                 review.read_text(encoding="utf-8") if review.is_file() else None, History(plan),
                 (spec_dir / "plan-done.md").read_text(encoding="utf-8") if (spec_dir / "plan-done.md").is_file() else "")


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
    # the section's digest under `section_sha256`, or under `plan_sha256` as the reviewer's MODE 4 JSON shape names it (feature
    # 374 wave 153: two task reviews refused for the plan-stage key, then renamed by hand)
    review = {**review, "section_sha256": review.get("section_sha256") or review.get("plan_sha256")}
    if review.get("section_sha256") != digest(section.encode()):
        raise ValueError(f"section_sha256 does not match {task}'s section - it changed while it was being reviewed")
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("decisions must be a list")
    verdict = derive_verdict(decisions)
    rec_path = spec_dir / RECORD
    # slimmed as it is rewritten (amendment 11, D63): a record converts at its next recording
    out = slim_record(json.loads(rec_path.read_text(encoding="utf-8"))) if rec_path.is_file() else {"feature": spec_dir.name}
    out.setdefault("tasks", {})[task] = {"section_sha256": review["section_sha256"],  # its text is in git (D63), not copied
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


def _section_clear(review: dict, section: str) -> bool:
    """Every block of the section carries a CLEAR verdict at its digest (amendment 11: the plan reviewed whole, or its blocks)."""
    have = reviewed_blocks(review)
    return all((have.get(k) or {}).get("verdict") == "CLEAR" and (have.get(k) or {}).get("sha256") == block_digest(b)
               for k, b, _a in blocks(section) if k != "preamble")


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
        # a plan reviewed CLEAR as a whole, still current, covers its task sections too: the reviewer read them; only a section
        # added or changed since needs its own preflight (the advisor's note before batch 3 landed)
        if task_current(review, text, task, History(plan)) or (owed(d) is None and _section_clear(review, task_sections(text)[task])):
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
    kept = {k: {f: v for f, v in e.items() if f != "section_text"} for k, e in kept.items()}
    when = today or datetime.date.today().isoformat()
    # amendment 11 (D60, D63): a verdict per block, and no copy of the plan - a later typo is measured against git's history
    out = {"feature": spec_dir.name, "plan_sha256": review["plan_sha256"], **({"tasks": kept} if kept else {}),
           "blocks": {k: {"sha256": block_digest(body), "verdict": verdict, "reviewed": when}
                      for k, body, _at in blocks(plan.read_text(encoding="utf-8"))},
           "reviewed": when, "declared": declared, "decisions": decisions, "verdict": verdict}
    (spec_dir / RECORD).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def slim_record(review: dict) -> dict:
    """A record from before amendment 11 converted (D63): each block of its `plan_text` under its verdict, task entries without
    their text, no copy of the plan. The verdicts are kept exactly."""
    out = {k: v for k, v in review.items() if k not in ("plan_text",)}
    if "blocks" not in out and isinstance(review.get("plan_text"), str):
        out["blocks"] = {k: {"sha256": e["sha256"], "verdict": e["verdict"], "reviewed": review.get("reviewed", "")}
                         for k, e in reviewed_blocks(review).items()}
    if isinstance(out.get("tasks"), dict):
        out["tasks"] = {k: {f: v for f, v in e.items() if f != "section_text"} for k, e in out["tasks"].items()}
    return out


def record_blocks(spec_dir: pathlib.Path, review: dict, declared: str, today: str | None = None) -> dict:
    """A review of changed blocks (D61): `review` names each block reviewed with its digest (`blocks: {key: sha256}`) and the
    decisions found in them; the verdict they derive is each named block's."""
    if declared != REVIEWER:
        raise PermissionError(f"declined: only the `{REVIEWER}` subagent records a plan review (AS={REVIEWER})")
    named = review.get("blocks")
    if not isinstance(named, dict) or not named:
        raise ValueError("blocks must name each block reviewed: {\"<heading line>\": \"<sha256>\"}")
    plan = spec_dir / "plan.md"
    now = {k: block_digest(body) for k, body, _at in blocks(plan.read_text(encoding="utf-8") if plan.is_file() else "")}
    for key, sha in named.items():
        if key.startswith(REMOVED) and sha == "removed":
            continue  # a block deleted by hand, its removal judged (the plan review): it leaves the record below
        if key not in now:
            raise ValueError(f"plan.md has no block {key!r}")
        if now[key] != sha:
            raise ValueError(f"{key!r} changed while it was being reviewed - its digest is not {sha[:12]}")
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("decisions must be a list (empty when the blocks decide nothing)")
    verdict = derive_verdict(decisions)
    rec_path = spec_dir / RECORD
    out = slim_record(json.loads(rec_path.read_text(encoding="utf-8"))) if rec_path.is_file() else {"feature": spec_dir.name}
    when = today or datetime.date.today().isoformat()
    redecided = redecided_tasks(plan, out.get("blocks") or {}, named)
    for key, sha in named.items():
        if key.startswith(REMOVED):
            if verdict == "CLEAR":
                out.setdefault("blocks", {}).pop(key[len(REMOVED):], None)
            continue
        out.setdefault("blocks", {})[key] = {"sha256": sha, "verdict": verdict, "reviewed": when, "declared": declared}
    out.setdefault("block_reviews", []).append({"reviewed": when, "blocks": sorted(named), "verdict": verdict, "decisions": decisions})
    rec_path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    approach = _approach_gate()
    root = spec_dir.parent.parent
    owed = [approach.owe(root, spec_dir.name, t, f"re-decided:{key}", "A") for t, key in redecided
            if approach.checklist(root, plan.read_text(encoding="utf-8")) is not None]
    return {"verdict": verdict, "blocks": sorted(named), "decisions": decisions, **({"approach_owed": owed} if owed else {})}


_DECISIONS_HEAD = re.compile(r"^#{2,4}\s+(T\d+[a-z]?)\s+Decisions\b")


def redecided_tasks(plan: pathlib.Path, before: dict, named: dict) -> list[tuple[str, str]]:
    """(task, block key) for each task's Decisions block re-reviewed after an earlier CLEAR on it, changed by more than a typo
    (feature 385 D9: a changed approach owes the Approach block answered afresh; a first review or a re-wording does not)."""
    out = []
    history = History(plan)
    text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    bodies = {k: body for k, body, _at in blocks(text)}
    for key, sha in named.items():
        m = _DECISIONS_HEAD.match(key)
        prior = before.get(key) or {}
        if not m or prior.get("verdict") != "CLEAR" or prior.get("sha256") in (None, sha):
            continue
        old = history.block(key, str(prior["sha256"]))
        if old is None or not typo_only(old, bodies.get(key, "")):
            out.append((m.group(1), key))
    return out


def _approach_gate():  # noqa: ANN202 - the module beside this one
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import approach_gate  # noqa: PLC0415

    return approach_gate


def archivable(spec_dir: pathlib.Path) -> list[str]:
    """The task sections `make plan-archive` may move (D62): every task their heading names ticked in tasks.md, and their
    verdict CLEAR - the section's own, or each of its blocks'. In plan order, none inside another."""
    plan = spec_dir / "plan.md"
    text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    tasks = (spec_dir / "tasks.md").read_text(encoding="utf-8") if (spec_dir / "tasks.md").is_file() else ""
    done = set(re.findall(r"^- \[[xX]\] (T\d+[a-z]?)\b", tasks, re.M))
    try:
        review = json.loads((spec_dir / RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        review = {}
    have = reviewed_blocks(review)
    out: list[str] = []
    taken: list[tuple[int, int]] = []
    for sec in dict.fromkeys(task_sections(text).values()):
        at = text.find(sec)
        heading = sec.splitlines()[0] if sec else ""
        ids = _TASK_ID.findall(heading)
        if not ids or any(i not in done for i in ids) or any(lo <= at < hi for lo, hi in taken):
            continue
        own = any(task_current(review, text, i) for i in ids)
        clear = all((have.get(k) or {}).get("verdict") == "CLEAR" and (have.get(k) or {}).get("sha256") == block_digest(b)
                    for k, b, _a in blocks(sec) if k != "preamble")
        if own or clear:
            out.append(sec)
            taken.append((at, at + len(sec)))
    return out


def archive(spec_dir: pathlib.Path, today: str | None = None) -> list[str]:
    """Move the archivable sections out of plan.md into plan-done.md (D62), byte for byte, leaving one generated line where each
    run of them stood; the task ids moved."""
    plan = spec_dir / "plan.md"
    text = plan.read_text(encoding="utf-8")
    secs = archivable(spec_dir)
    if not secs:
        return []
    when = today or datetime.date.today().isoformat()
    marker = "\x00archived\x00"
    moved_ids: list[str] = []
    for sec in secs:
        text = text.replace(sec, marker, 1)
        moved_ids += _TASK_ID.findall(sec.splitlines()[0])
    runs = re.split(f"((?:{re.escape(marker)})+)", text)
    pos, out = 0, []
    for part in runs:
        if part.startswith(marker):
            n = part.count(marker)
            ids = [i for s in secs[pos:pos + n] for i in _TASK_ID.findall(s.splitlines()[0])]  # this run's sections, in order
            pos += n
            out.append(f"<!-- plan-archive: {ids[0]} to {ids[-1]} moved to plan-done.md, {when} (feature 375 FR-044) -->\n")
        else:
            out.append(part)
    plan.write_text("".join(out), encoding="utf-8")
    done = spec_dir / "plan-done.md"
    head = "" if done.is_file() else f"# {spec_dir.name} - the plan's finished sections (feature 375 FR-044; no review reads this file)\n\n"
    with done.open("a", encoding="utf-8") as fh:
        fh.write(head + f"<!-- plan-archive: archived {when} -->\n" + "".join(secs))  # an ARCHIVE_LINE: out of every digest
    return moved_ids


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
        verdict = judge(_show(root, ref, f"{feature}/plan.md"), review.decode("utf-8") if review is not None else None,
                        History(root / feature / "plan.md", ref), (_show(root, ref, f"{feature}/plan-done.md") or b"").decode("utf-8", "replace"))
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
    hook never reroutes it), recorded under `tasks.<id>`, on the lean bundle (amendment 11, D64): the request, the requirements
    the section cites, the section and its earlier text - never the whole spec or the whole plan."""
    sys.path.insert(0, str(HERE))
    import plan_bundle  # noqa: PLC0415

    return plan_bundle.task_prompt(spec_dir, task)


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
        # ...AND WHEN, for the report's per-task split (feature 385 T02, plan D10): `make feature-report` divides each task's time
        # at its decision points from here to its tick
        with pathlib.Path(common, "task-starts.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"feature": d.name, "task": argv[2], "utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}) + "\n")
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
    if argv[:1] == ["record-blocks"] and len(argv) == 5 and argv[3] == "--as":  # `make plan-verdict BLOCKS=1` (amendment 11, D61)
        spec_dir = resolve(argv[1])
        if spec_dir is None:
            print(f"plan-verdict: no single specs/{argv[1]}* directory", file=sys.stderr)
            return 2
        try:
            got = record_blocks(spec_dir, json.loads(pathlib.Path(argv[2]).read_text(encoding="utf-8")), argv[4])
        except PermissionError as e:
            print(f"plan-verdict: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"plan-verdict: refused - {e}", file=sys.stderr)
            return 1
        print(f"plan-verdict: {got['verdict']} recorded for {len(got['blocks'])} block(s) of {spec_dir.name}'s plan ({len(got['decisions'])} decision(s))")
        for line in got.get("approach_owed", []):  # feature 385 D9
            print(line)
        return 0
    if argv[:1] in (["slim"], ["archive"], ["delta"]) and len(argv) == 2:  # amendment 11: D63, D62, D61
        spec_dir = resolve(argv[1])
        if spec_dir is None or not (spec_dir / "plan.md").is_file():
            print(f"{argv[0]}: no single specs/{argv[1]}* directory with a plan.md", file=sys.stderr)
            return 2
        if argv[0] == "slim":
            rec = spec_dir / RECORD
            if not rec.is_file():
                return 0
            before = rec.stat().st_size
            rec.write_text(json.dumps(slim_record(json.loads(rec.read_text(encoding="utf-8"))), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"slim: {spec_dir.name}/{RECORD} {before // 1024} KB -> {rec.stat().st_size // 1024} KB, its verdicts kept")
            return 0
        if argv[0] == "archive":
            ids = archive(spec_dir)
            print(f"plan-archive: {len(ids)} task section(s) moved to {spec_dir.name}/plan-done.md: {', '.join(ids) or 'none finished'}")
            return 0
        sys.path.insert(0, str(HERE))
        import plan_bundle  # noqa: PLC0415

        try:
            review = json.loads((spec_dir / RECORD).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            review = {}
        text = (spec_dir / "plan.md").read_text(encoding="utf-8")
        ruled = {t for t in task_sections(text) if task_current(review, text, t, History(spec_dir / "plan.md"))}
        done = (spec_dir / "plan-done.md").read_text(encoding="utf-8") if (spec_dir / "plan-done.md").is_file() else ""
        keys, blocked = block_status(review, text, ruled, History(spec_dir / "plan.md"), done)
        # ...AND EVERY BLOCK STILL BLOCKED is owed its review again (feature 385): a whole-plan BLOCKED verdict is recorded on every
        # block, and once the blocking decision was fixed in its own block, the blocks beside it - unchanged - kept BLOCKED with no
        # route to CLEAR, so `make decide` refused a task whose every decision a later round had cleared
        keys += [k for k in blocked if k not in keys]
        if not keys:
            print(f"plan-delta: no block of {spec_dir.name}'s plan is owed a review")
            return 0
        print(plan_bundle.delta_prompt(spec_dir, keys))
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
