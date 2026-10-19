#!/usr/bin/env python3
"""The state of the record checks in flight - decide, then freeze (feature 375, FR-003(b)(c), FR-010; plan D4, D10).

WHY. Measured on feature 372 (2026-10-10): 0105 went through about four full rounds of five to seven checks in wave 108 and
0100 about three in wave 106, because a page was edited while its checks were running - each edit made the running checks
read stale words and re-owed the whole set. The rule (FR-003): while a check on a page or pop-up is running, the page is
frozen; once every check of the round has returned, the edits those checks proposed go in, in one pass; then the page is
checked once. And a check is not re-dispatched while another check on the same page is outstanding.

THE STATE, `<git common dir>/checks-open.json`:

    {"feature": "<dir>", "dispatches": {tool_use_id: {check, subjects, manifest, t, aid, state}},
     "rounds": {"<check>|<subject>": n}, "edits": {subject: [[path, old, new], ...]}}

A dispatch is RUNNING from its PreToolUse until it RETURNS - SubagentStop for its agent id (paired at PostToolUse through
`tool_response.agentId`; measured: specs/375-enforced-wave-process/measurements.json `subagent-stop-probe`), a foreground
PostToolUse, or its answer (`make record-checked` / `claims-checked` / `modal-triaged`), whichever comes first, so a missing
event never freezes a page for good. At return its reply's EDIT blocks join its subjects' `edits`.

A SUBJECT is what a check reads: a question (`q:0105`, both its pages and its notes) or a pop-up (`modal:sheet/bath`, its
`.md` file), from the bundle MANIFEST's `unit:` lines. impl-drift and the claims triage have none (plan D4): a claim is not a
page, and their counts reach FR-010 alone.

    hm_checks.py dispatch   (PreToolUse Agent payload on stdin)  -> refusal JSON or nothing
    hm_checks.py launched   (PostToolUse Agent)
    hm_checks.py returned   (SubagentStop)
    hm_checks.py edit       (PreToolUse Edit/Write/Bash payload) -> refusal JSON or nothing
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hm_arbiter  # noqa: E402
import hm_planhold  # noqa: E402

STATE = "checks-open.json"
#: the checks whose subject is a question page or a pop-up, and so freeze it while they run
PAGE_CHECKS = frozenset("quote-check record-format source-reader intro-check record-style translation-check entry-drift modal-form modal-research modal-depiction".split())
#: rounds a check may have on one subject in one feature before the round arbiter rules (FR-010, as the review checks' cap)
ROUND_CAP = 2
#: a check silent this long is reported stale and may be closed by hand (the no-poll guard's wait ceiling)
STALE_S = 90 * 60
#: a dispatch recorded at PreToolUse and never launched (another guard refused the call) stops counting after this
PENDING_S = 120
#: a `check-wave` unit's dispatch, recorded when the Workflow starts, waits longer for its agent: a long wave queues behind the
#: workflow's concurrency cap (feature 383 amendment 7, plan D48; a design number to move). A refused run's are dropped at once.
WAVE_PENDING_S = 30 * 60
_UNIT = re.compile(r"^unit: (\S+?):(\S.*?) \S+$", re.M)
_UNIT_FP = re.compile(r"^unit: (\S+?:\S.*?) (\S+)$", re.M)
_Q = re.compile(r"\b(\d{4})(?:[.#-]|$)")
_EDIT = re.compile(
    r"^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n(?P=ind)<<<\n(?P<old>.*?)\n(?P=ind)===\n(?P<new>.*?)\n?(?P=ind)>>>[ \t]*$",
    re.S | re.M,
)
_PAGE = re.compile(r"research/questions/(\d{4})-[^/]*\.html$")
#: a bundle scoped to named notes (`check_bundle.py`: "ONLY the notes a, b and the blocks that carry them")
_NOTES = re.compile(r"ONLY the notes (.+?) and the blocks that carry them")
_MODAL = re.compile(r"interactive/assets/modals/((?:sheet|hamlet|choice)/[^/]+)\.md$")
#: a source's bundle (`check_bundle.key_bundle`) and the notes its owed units name (`unit: source-reader:0248#koku-enwiki-2 <fp>`)
_SOURCE_BUNDLE = re.compile(r"^# Check bundle - source \S+", re.M)
_UNIT_NOTE = re.compile(r"^unit: [\w-]+:\d{4}(?:\.drawing)?#(\S+) \S+$", re.M)


def subject_of_unit(slug_tail: str) -> str:
    """`0105.drawing#note` -> `q:0105`; `sheet/bath` -> `modal:sheet/bath`."""
    if "/" in slug_tail and not _Q.match(slug_tail):
        return f"modal:{slug_tail}"
    m = _Q.match(slug_tail)
    return f"q:{m.group(1)}" if m else ""


def moved_since_answer(root: Path, text: str, subject: str) -> str:
    """The fingerprint of a unit on `subject` the bundle carries that no recorded answer covers, or ''. An arbiter's accept
    closes a unit at the words it ruled on; once a later change (a page the pop-up links, its own file) re-owes it, the record
    gate owes a check the closure refused - a deadlock (feature 374 FR-005, the residence pop-up after 0090 moved). So the
    closure holds only while every unit the bundle carries on the subject is answered at its fingerprint."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "record"))
    import record_owed  # noqa: PLC0415

    store = record_owed.store(root)
    return next((fp for slug, fp in _UNIT_FP.findall(text) if subject_of_unit(slug.partition(":")[2]) == subject and not record_owed.answered(store, slug, fp)), "")


def batch_of(root: Path | None) -> str:
    """The batch a round is counted in: the `origin/main` the clone stands on ('' with no root or no remote). A landing moves it,
    so rounds counted before the last landing belong to an earlier batch (`new_cause`)."""
    if root is None:
        return ""
    import subprocess  # noqa: PLC0415

    out = subprocess.run(["git", "-C", str(root), "rev-parse", "origin/main"], capture_output=True, text=True, check=False)
    return out.stdout.strip() if out.returncode == 0 else ""


def new_cause(state: Mapping[str, Any], unit: str, batch: str) -> bool:
    """Is a dispatch owed in a LATER BATCH than every counted round of `unit` - its rounds all counted under another `origin/main`,
    so a later batch's page change owes it? Its rounds then count from here, and one new bullet does not trip a cap that earlier
    batches' rounds used up (the round arbiter on round:modal-depiction|modal:hamlet/woodland-commons@3, feature 374 batch 9).
    Within a batch every round counts, the edits a round's own findings caused included: told by fingerprint, as first built, any
    edit restarted the count and the cap never tripped (feature 374 batch 11). A unit with no counted round, or no batch known,
    is no new cause."""
    seen = state.get("round_batch", {}).get(unit) or ""
    return bool(seen) and bool(batch) and seen != batch


def subjects_of_manifest(text: str) -> list[str]:
    return sorted({s for _c, tail in _UNIT.findall(text) if (s := subject_of_unit(tail))})


def subject_of_path(path: str) -> str:
    """The subject a file belongs to: a question's page, drawing page or notes; a pop-up's `.md` file."""
    p = path.replace(os.sep, "/")
    if m := _PAGE.search(p) or re.search(r"research/questions/(\d{4})-[^/]*\.notes\.html$", p):
        return f"q:{m.group(1)}"
    if m := _MODAL.search(p):
        return f"modal:{m.group(1)}"
    return ""


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}


@contextlib.contextmanager
def locked(path: Path) -> Iterator[None]:
    """The state file's read-modify-write held by one process at a time: six checks launched in one message run one hook
    process each, and unlocked, a later save dropped an earlier one's agent id - its reply was then never kept, and the round
    arbiter read "no reply kept" for the round (feature 374 wave 120, the arbiter's tooling fix)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def save(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _live(d: Mapping[str, Any], now: float) -> bool:
    """A dispatch that counts: launched, or recorded so recently that its launch may still come. One recorded at PreToolUse
    and refused by another guard never launches, and must not freeze its page."""
    return d.get("state") != "pending" or now - float(d.get("t", 0)) < (WAVE_PENDING_S if d.get("wave") else PENDING_S)


def _collapsed(text: str) -> str:
    return " ".join(text.split())


def _wave_key(text: str) -> str:
    return hashlib.sha256(_collapsed(text).encode()).hexdigest()[:16]


def _task_texts(transcript: str) -> list[str]:
    """A workflow agent's task text, whitespace collapsed: its first user messages, each after the harness's frame line (the
    harness indents the computed text and frames it - measured on feature 383's probe, research R20)."""
    out: list[str] = []
    try:
        lines = Path(transcript).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for raw in lines:
        try:
            msg = json.loads(raw).get("message") or {}
        except ValueError, AttributeError:
            continue
        if not isinstance(msg, dict) or msg.get("role") != "user":
            continue
        c = msg.get("content")
        text = c if isinstance(c, str) else " ".join(str(b.get("text", "")) for b in c or [] if isinstance(b, dict))
        out.append(_collapsed(text.split("The computed task text follows:", 1)[-1]))
        if len(out) >= 3:
            break
    return out


def pair_wave(state: dict[str, Any], agent_id: str, transcript: str) -> None:
    """A workflow agent no PostToolUse gave an id to: matched to the wave dispatch its task text begins with (a declared verify
    step's text goes on with the reply before it), and launched there - waiting first, then a re-launched one whose first agent
    came back with nothing (feature 383 amendment 7, plan D48)."""
    ds = state.get("dispatches", {})
    if not agent_id or any(d.get("aid") == agent_id for d in ds.values()):
        return
    texts = _task_texts(transcript)
    hits = [(tid, d) for tid, d in ds.items() if d.get("wave") and any(hashlib.sha256(t[: int(d.get("wave_len", 0))].encode()).hexdigest()[:16] == d["wave"] for t in texts)]
    # the LONGEST matching prompt first: one declared prompt can begin another ("... page 1", "... page 12" - spec round 4)
    hits.sort(key=lambda h: (-int(h[1].get("wave_len", 0)), h[1].get("state") != "pending", float(h[1].get("t", 0))))
    for tid, d in hits:
        if d.get("state") == "pending" or (d.get("state") == "returned" and not d.get("reply")):
            d["aid"], d["state"] = agent_id, "running"
            return


def drop_run(cwd: str, prefix: str) -> None:
    """A refused `check-wave` run's dispatches go: it launches nothing, so none of them may freeze a page."""
    path = state_path(cwd)
    if path is None or not path.is_file():
        return
    with locked(path):
        state = load(path)
        state["dispatches"] = {t: d for t, d in state.get("dispatches", {}).items() if not t.startswith(prefix)}
        save(path, state)


def running(state: Mapping[str, Any], subject: str, now: float | None = None) -> list[dict]:
    now = time.time() if now is None else now
    return [d for d in state.get("dispatches", {}).values() if subject in d.get("subjects", []) and d.get("state") in ("running", "pending") and _live(d, now)]


def open_round(state: Mapping[str, Any], subject: str, now: float | None = None) -> list[dict]:
    """The dispatches of the subject's current round: dispatched and not yet answered."""
    now = time.time() if now is None else now
    return [d for d in state.get("dispatches", {}).values() if subject in d.get("subjects", []) and d.get("state") != "answered" and _live(d, now)]


def notes_of_manifest(text: str) -> set[str]:
    """The notes a note-scoped bundle reads; empty for a bundle of the whole page. A SOURCE's bundle (`make check-bundle KEY=`)
    reads the notes its `unit:` lines name, not the page (the round arbiter on round:source-reader|q:0248@7, 2026-10-18: one
    bundle per newly cited source was counted as a whole-page re-read each, and a new question's first reads hit round 7)."""
    named = {n.strip() for m in _NOTES.findall(text) for n in m.split(",") if n.strip()}
    if named or not _SOURCE_BUNDLE.search(text):
        return named
    return {m.group(1) for m in _UNIT_NOTE.finditer(text)}


def fresh_reading(state: Mapping[str, Any], unit: str, notes: set[str]) -> bool:
    """A dispatch reading only notes no earlier round of the unit read is a FIRST reading, not a repeat round: three features
    adding their own notes to one page, one after another, are three first readings (the round arbiter on 0104, 2026-10-10:
    "the cap fired because the round counter counts one page across features, not because a check repeated")."""
    read = state.get("notes_read", {}).get(unit)
    return bool(notes) and read is not None and "*" not in read and not notes & set(read)


def sentences(blocks: list[str]) -> list[str]:
    """A subject's visible sentences, whitespace-normalized - the unit a check is said to have READ."""
    return [s for b in blocks for s in re.split(r"(?<=[.!?])\s+", " ".join(b.split())) if s]


def first_look(state: Mapping[str, Any], unit: str, current: list[str]) -> bool:
    """A dispatch whose only unread sentences came from OTHER checks' edits is a first look, not a repeat round (feature 374
    wave 120, the round arbiter on 0190: record-format's third round was owed only by sentences the depiction checks had
    asked for, and the cap fired on text the check had never read). A sentence inside an edit this check itself proposed is
    its own fix, read again - a repeat. A unit with no reading recorded counts as before."""
    seen = set(state.get("seen", {}).get(unit) or [])
    if not seen:
        return False
    unseen = [s for s in current if _sentence_key(s) not in seen]
    own = " ".join(" ".join(n.split()) for n in state.get("own_edits", {}).get(unit) or [])
    return bool(unseen) and not any(s in own for s in unseen)


def _sentence_key(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def batch_root(manifest: str) -> str:
    """The bundle a split bundle's `batch-N/MANIFEST.md` belongs to (`make check-bundle` writes one directory per batch), or ''
    for a bundle that is not a batch."""
    parent = Path(manifest).parent
    return str(parent.parent) if re.fullmatch(r"batch-\d+", parent.name) else ""


def dispatch(state: dict[str, Any], tid: str, check: str, manifest: str, text: str, now: float, root: Path | None = None, freeze_ok: bool = False, arbiter_ok: bool = False) -> str:
    """Record a check's dispatch, or say why it is refused (FR-003(c) apply once, FR-010 the round cap and the tripwires, which
    the round arbiter rules on - `hm_arbiter.py`)."""
    subjects = subjects_of_manifest(text) if check in PAGE_CHECKS else []
    notes = notes_of_manifest(text)
    if root is not None and not arbiter_ok:
        held = hm_arbiter.blocking(root, "")
        if held:
            return hm_arbiter.refusal(held)
    current = {s: sentences(subject_blocks(root, s)) for s in subjects} if root is not None else {}
    # GUARD_EDIT_OK: feature 374 wave 151 - A SPLIT BUNDLE'S BATCHES ARE ONE ROUND: the second batch of a bundle `make check-bundle`
    # split is no re-dispatch into a running round, and no round of its own (0049's quote-check batch-2 was refused while batch-1 ran)
    root_of = batch_root(manifest)
    sibling = {s: bool(root_of) and any(d["check"] == check and batch_root(str(d.get("manifest") or "")) == root_of for d in open_round(state, s, now)) for s in subjects}
    for s in subjects:
        same = [] if freeze_ok or sibling[s] else [d for d in open_round(state, s, now) if d["check"] == check and d.get("state") != "pending"]
        if same and [d for d in running(state, s, now) if d.get("state") == "running"]:  # launched, not a refused call's record
            return (
                f"`{check}` is already in {s}'s round and that round has a check still running - all of a round's checks "
                "return, their edits go in in one pass, then the page is checked once (feature 375 FR-003c)"
            )
        n = state.setdefault("rounds", {}).get(f"{check}|{s}", 0)
        unit = f"{check}|{s}"
        if root is not None and not arbiter_ok and not fresh_reading(state, unit, notes) and not first_look(state, unit, current.get(s, [])):
            shut = hm_arbiter.closed(root, f"round:{unit}@")
            moved = moved_since_answer(root, text, s) if shut else ""
            if shut and not moved:
                return f"the round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)"
            base = state.setdefault("rebased", {})
            if moved and base.get(unit, {}).get("fp") != moved:
                base[unit] = {"fp": moved, "n": n}  # a new change: its rounds count from here (feature 374 FR-005)
            batch = batch_of(root)
            if new_cause(state, unit, batch) and not open_round(state, s, now):
                base[unit] = {"fp": batch, "n": n, "cause": True}  # a later batch's cause (below)
                state.setdefault("round_batch", {})[unit] = batch
            n0 = base.get(unit, {}).get("n", 0) if shut or base.get(unit, {}).get("cause") else 0
            cap = n0 + ROUND_CAP + hm_arbiter.continues(root, f"round:{unit}@", n0)
            if n >= cap:
                hm_arbiter.trip(root, f"round:{unit}@{n + 1}", "round", unit, f"round {n + 1} of {check} on {s}", now)
                return f"round {n + 1} of `{check}` on {s} in this feature passes its cap of {cap} - " + hm_arbiter.refusal([f"round:{unit}@{n + 1}"], root)
    counted: list[str] = []
    # A READING'S MARKS ARE APPLIED WHEN IT LAUNCHES (feature 385 T59, the round arbiter on round:modal-form|modal:choice/
    # dikepond_split--0.7@3): this hook records a dispatch at PreToolUse, beside other hooks - the wave guard refused T10's
    # modal-form wave, yet the refused dispatch had marked its notes read and opened a fresh round, so the next real dispatch was no
    # first look and was counted. What a reading marks is kept on the pending record and applied by `launched`.
    marks: dict[str, Any] = {"fresh": [], "seen": {}, "read": {}}
    for s in subjects:
        if not open_round(state, s, now):
            marks["fresh"].append(s)  # a new round: the last round's proposals are spent, once this one launches
        unit = f"{check}|{s}"
        if not sibling[s] and not fresh_reading(state, unit, notes) and not first_look(state, unit, current.get(s, [])):  # a fresh reading is no repeat
            # ...COUNTED WHEN IT IS READ, not when it is sent (feature 385 T41, the round arbiter on round:source-reader|q:0081@3: two
            # dispatches the pair hook refused before any agent started were counted, and the cap fired on zero readings): the unit
            # is recorded here and counted by `returned` once the agent comes back with a reply
            counted.append(unit)
        state.setdefault("round_batch", {})[unit] = batch_of(root)  # the batch this round counts in (`new_cause`)
        if s in current:  # what this check will have read of the subject, for the next dispatch's first-look test
            marks["seen"][unit] = sorted({_sentence_key(x) for x in current[s]})
        marks["read"][unit] = sorted(notes or {"*"})  # "*": a whole-page reading, every note read
    state.setdefault("dispatches", {})[tid] = {
        "check": check,
        "subjects": subjects,
        "manifest": manifest,
        "t": now,
        "state": "pending",
        "counted": counted,
        "marks": marks,
        "owed": re.findall(r"^owed: (.+)$", text, re.M),  # why each unit was due (374)
        "notes": sorted(notes),
    }  # the notes the bundle read, [] for the whole page (feature 393's earlier rounds)
    return ""


def _apply_marks(state: dict[str, Any], d: dict[str, Any]) -> None:
    """What a launched dispatch's reading marks (T59): its fresh rounds' edits reset, its seen sentences, its notes read - once."""
    marks = d.pop("marks", None) or {}
    for s in marks.get("fresh", []):
        state.setdefault("edits", {})[s] = []
    for unit, keys in (marks.get("seen") or {}).items():
        seen = state.setdefault("seen", {}).setdefault(unit, [])
        seen.extend(k for k in keys if k not in seen)
    for unit, keys in (marks.get("read") or {}).items():
        read = state.setdefault("notes_read", {}).setdefault(unit, [])
        read.extend(k for k in keys if k not in read)


def launched(state: dict[str, Any], tid: str, agent_id: str, background: bool, reply: str = "", keep: Path | None = None) -> None:
    """A dispatch's launch. A FOREGROUND check has already returned by its PostToolUse, and its SubagentStop fired while the
    dispatch was still pending with no agent id, so `returned` could not match it: its reply - the arbiter's round-to-round
    record and its EDIT blocks - is taken here from the tool's response (the round arbiter on 0104's fifth source-reader
    round, 2026-10-10, found "no reply kept" for every round)."""
    d = state.get("dispatches", {}).get(tid)
    if d is None:
        return
    d["aid"] = agent_id
    d["state"] = "running"
    _apply_marks(state, d)
    if not background:
        returned(state, agent_id, reply, keep)


def response_text(resp: Mapping[str, Any]) -> str:
    """The text of an Agent tool's response: its `content` blocks, or a plain string."""
    c = resp.get("content")
    if isinstance(c, str):
        return c
    return "\n".join(str(b.get("text") or "") for b in c if isinstance(b, Mapping)) if isinstance(c, list) else ""


def returned(state: dict[str, Any], agent_id: str, reply: str, keep: Path | None = None) -> None:
    """A check's return: its state, its EDIT blocks on its subjects, and (with `keep`, the clone's `check-replies/`) its reply,
    which the round arbiter's bundle compares round to round (FR-011)."""
    for tid, d in state.get("dispatches", {}).items():
        # the reply is kept whatever the state: an answer recorded before SubagentStop fired had closed the dispatch, and the
        # round arbiter's bundle then read "no reply kept" for that round (feature 374, the mulberry pop-up's round 2)
        if d.get("aid") == agent_id and keep is not None and reply and not d.get("reply"):
            keep.mkdir(parents=True, exist_ok=True)
            (keep / f"{re.sub(r'[^A-Za-z0-9_-]', '_', tid)}.md").write_text(reply, encoding="utf-8")
            d["reply"] = str(keep / f"{re.sub(r'[^A-Za-z0-9_-]', '_', tid)}.md")
        if d.get("aid") == agent_id and reply.strip() and not d.get("rounded"):  # a reading: its rounds count now, once (T41)
            for unit in d.get("counted") or []:
                state.setdefault("rounds", {})[unit] = state.get("rounds", {}).get(unit, 0) + 1
            d["rounded"] = True
        if d.get("aid") == agent_id and d.get("state") == "running":
            d["state"] = "returned"
            for path, old, new in _blocks(reply):
                for s in d["subjects"]:
                    state.setdefault("edits", {}).setdefault(s, []).append([path, old, new])
                    # the check's OWN proposals: a sentence inside one is its fix read again, never a first look
                    state.setdefault("own_edits", {}).setdefault(f"{d['check']}|{s}", []).append(new)


#: the answers one `modal-research` dispatch is recorded as (`make record-checked CHECK=modal-accuracy` ...)
RESEARCH_UNITS: frozenset[str] = frozenset({"modal-accuracy", "modal-references", "modal-gaps"})


def answered(state: dict[str, Any], check: str, subjects: list[str]) -> int:
    """Close the dispatches of `check` on any of `subjects` - its answer is recorded (`make record-checked`), or `make
    check-closed` closed a silent one (check `*`)."""
    n = 0
    # GUARD_EDIT_OK: feature 374 FR-005 - one modal-research dispatch is answered as three units (its accuracy, references and
    # gaps); matched by the unit's own name it was never closed, its round never ended, and its next round was refused
    names = {check, *(("modal-research",) if check in RESEARCH_UNITS else ())}
    for d in state.get("dispatches", {}).values():
        if d["check"] in names or d["check"] == "*" or check == "*":
            if set(d["subjects"]) & set(subjects) and d.get("state") != "answered":
                d["state"] = "answered"
                n += 1
    return n


def record_answer(root: Path, check: str, slugs: list[str]) -> None:
    """Called by `record_owed.answer`: the units it answered close their subjects' dispatches of that check."""
    path = state_path(str(root))
    if path is None or not path.is_file():
        return
    with locked(path):
        state = load(path)
        if answered(state, check, sorted({s for slug in slugs if (s := subject_of_unit(slug.split(":", 1)[-1]))})):
            save(path, state)


def proposed(state: Mapping[str, Any], subject: str, old: str, new: str) -> bool:
    """An edit the round's checks proposed, or part of one applied in place: its old text inside a block's old text, and the
    block's new text reading the same up to it and then `new` (a different replacement at a proposed place is not one)."""
    for _p, b_old, b_new in state.get("edits", {}).get(subject, []):
        i = b_old.find(old)
        if old and i >= 0 and b_new.startswith(b_old[:i] + new):
            return True
    return False


def edit_refusal(state: Mapping[str, Any], path: str, old: str, new: str, now: float) -> str:
    """Why an Edit to `path` is refused now (FR-003(b)), or ''."""
    s = subject_of_path(path)
    if not s or not open_round(state, s, now):
        return ""
    live = running(state, s, now)
    if live:
        names = ", ".join(sorted({d["check"] for d in live}))
        stale = [d for d in live if now - d["t"] > STALE_S]
        tail = f" ({len(stale)} silent past 90 minutes: `make check-closed SUBJECT={s} REASON=...` closes it)" if stale else ""
        return f"{s} is frozen while its checks run ({names}) - edit it once every check of the round has returned{tail} (feature 375 FR-003b)"
    if proposed(state, s, old, new):
        return ""
    blocks = state.get("edits", {}).get(s, [])
    return (
        f"{s}'s checks have returned, and this edit is none of the {len(blocks)} edit(s) they proposed - apply those (`make "
        "apply-edits REPLY=<the reply>`, or by hand), answer the checks, and make any other change after (FR-003b)"
        if blocks
        else f"{s}'s checks returned no edit to apply; answer them (`make record-checked`) before editing it (FR-003b)"
    )


def state_path(cwd: str) -> Path | None:
    """`<git common dir>/checks-open.json` of the clone holding `cwd`, found without running git (a hook on every call)."""
    p = Path(cwd or ".").resolve()
    for d in (p, *p.parents):
        g = d / ".git"
        if g.is_dir():
            return g / STATE
        if g.is_file():
            m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8").strip())
            if m:
                gd = (d / m.group(1)).resolve()
                common = gd / "commondir"
                return ((gd / common.read_text(encoding="utf-8").strip()).resolve() if common.is_file() else gd) / STATE
    return None


def _manifest_of(prompt: str) -> tuple[str, str]:
    m = re.search(r"(/[^\s`\"'<>)]*MANIFEST\.md)", prompt)
    if not m:
        return "", ""
    try:
        return m.group(1), Path(m.group(1)).read_text(encoding="utf-8")
    except OSError:
        return m.group(1), ""


def _reply_of(transcript: str, last: str) -> str:
    """A returned agent's reply: SubagentStop's `last_assistant_message`, else the last text of its own transcript."""
    if last:
        return last
    try:
        lines = Path(transcript).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for raw in reversed(lines):
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                return b["text"]
    return ""


def _blocks(reply: str) -> list[tuple[str, str, str]]:
    out = []
    for m in _EDIT.finditer(reply):
        ind = m.group("ind")
        undent = lambda t: "\n".join(line[len(ind) :] if line.startswith(ind) else line for line in t.split("\n"))  # noqa: E731
        out.append((m.group("path").strip(), undent(m.group("old")), undent(m.group("new"))))
    return out


def _reply_file(path: str) -> str:
    """The reply `make apply-edits FROM=` reads: an agent's transcript (`.jsonl` / `.output`, its last text) or a saved reply."""
    if path.endswith((".jsonl", ".output")):
        return _reply_of(path, "")
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def apply_refusal(state: Mapping[str, Any], command: str, now: float) -> str:
    """Why `make apply-edits FROM=<reply>` is refused now: a subject it edits has a check still running, or a block in it is
    none of that subject's round's returned blocks (FR-003b). Outside any open round it is not this guard's business."""
    m = re.search(r"\bmake\b[^;&|]*\bapply-edits\b[^;&|]*\bFROM=(\"[^\"]+\"|'[^']+'|\S+)", command)
    if not m:
        return ""
    for path, old, new in _blocks(_reply_file(m.group(1).strip("'\""))):
        s = subject_of_path(path)
        if not s or not open_round(state, s, now):
            continue
        if running(state, s, now):
            return edit_refusal(state, path, old, new, now)
        if [path, old, new] not in [list(e) for e in state.get("edits", {}).get(s, [])] and not proposed(state, s, old, new):
            return f"a block of this reply for {s} is not one its round's checks returned - apply only this round's replies (FR-003b)"
    return ""


#: how much of a dropped block's words a later block must carry to be that block back (a re-wording counts: 372's bath bullet
#: came back with its lead and first sentence intact and a sentence added)
SIMILAR = 0.6
_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def oscillation(versions: list[list[str]]) -> str:
    """A block of the latest version that is a block an earlier version had and a later one had dropped (A -> B -> A), by
    words (FR-010's reversal wire computed from the subject's own history - an edit made by a script or a `git checkout` is
    seen as well as one made with the Edit tool). Returns the block's first words, or ''."""
    if len(versions) < 3:
        return ""
    last, prev = versions[-1], versions[-2]
    for b in last:
        wb = _words(b)
        if any(len(wb & _words(p)) >= SIMILAR * max(len(_words(p)), 1) for p in prev):
            continue  # it stood just before: no return
        for i, vi in enumerate(versions[:-2]):
            for a in vi:
                wa = _words(a)
                if len(wa) >= 5 and len(wa & wb) >= SIMILAR * len(wa):
                    gone = any(not any(len(wa & _words(c)) >= SIMILAR * len(wa) for c in vj) for vj in versions[i + 1 : -1])
                    if gone:
                        return " ".join(b.split()[:12])
    return ""


def subject_blocks(root: Path, subject: str) -> list[str]:
    """The subject's blocks as its checks read them: a question's pages (`record_units.read_page`), a pop-up's paragraphs."""
    if subject.startswith("q:"):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "record"))
        import record_units as ru  # noqa: PLC0415

        out: list[str] = []
        for f in sorted((root / "research" / "questions").glob(f"{subject[2:]}-*.html")):
            if not f.name.endswith(".notes.html"):
                out += [b.words for b in ru.read_page(f.read_text(encoding="utf-8")).blocks]
        return out
    f = root / "l7r/diagram/interactive/assets/modals" / f"{subject[6:]}.md"
    return [" ".join(p.split()) for p in f.read_text(encoding="utf-8").split("\n\n") if p.strip()] if f.is_file() else []


def _feature(root: Path) -> str:
    d = hm_arbiter.feature_dir(root)  # one reader of the active feature: a page session's own first
    return d.name if d else ""


#: every check a dispatch is counted for: the page checks freeze their subject; impl-drift and the triages count to FR-010 only
CHECK_KINDS = PAGE_CHECKS | {"impl-drift"}


def escaped(token: str, text: str) -> bool:
    """`TOKEN="<a reason of two words and eight characters>"` in `text`: the escape is taken, and RECORDED in the guard census
    (`guardlog.sh`, as every guard's escape is - feature 170); a bare token or a thin reason is no escape."""
    m = re.search(rf'\b{token}="([^"]*)"', text)
    if not m or len(m.group(1).split()) < 2 or len(m.group(1)) < 8:
        return False
    import subprocess  # noqa: PLC0415

    here = Path(__file__).resolve().parent
    subprocess.run(["bash", "-c", '. "$1/guardlog.sh"; guard_log checks escaped "$2" "$3"', "_", str(here), m.group(1)[:200], token.lower().replace("_", "-")], capture_output=True, check=False)
    return True


def _root(payload: Mapping[str, Any]) -> Path | None:
    p = Path(str(payload.get("cwd") or ".")).resolve()
    return next((d for d in (p, *p.parents) if (d / ".git").exists()), None)


def window_start(root: Path) -> float:
    """When the cascade's window opened: the commit time of the clone's merge base with main, so a batch that LANDED - its
    dispatches charged against its own delta - is not charged to the next batch, whose delta starts afresh at the landing
    (feature 374, the round arbiter's cascade@1 tooling fix: batch 2's relabel dispatches were counted against batch 3's lines)."""
    import subprocess  # noqa: PLC0415

    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=False)
        return r.stdout.strip() if r.returncode == 0 else ""

    base = git("merge-base", "HEAD", "origin/main")
    stamp = git("show", "-s", "--format=%ct", base) if base else ""
    return float(stamp) if stamp.isdigit() else 0.0


def dispatches_since(state: Mapping[str, Any], since: float) -> int:
    """The check dispatches made at or after `since` (a dispatch's `t`) - the cascade's count inside its window."""
    return sum(1 for d in (state.get("dispatches") or {}).values() if float(d.get("t") or 0.0) >= since)


def changed_lines(root: Path) -> int:
    """Hand-written lines the clone's delta changed against the merge base (feature_report's rule: generated files and specs/
    out) - the cascade ratio's base (FR-010)."""
    import subprocess  # noqa: PLC0415

    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=False)
        return r.stdout if r.returncode == 0 else ""

    base = git("merge-base", "HEAD", "origin/main").strip() or git("rev-parse", "HEAD").strip()
    gen = re.compile(r"\.(svg|json|jsonl|png|webp)$|^specs/|^dev/(run-log|perf-log|bypass-log|idle-log)/|^pool/.*\.notes\.md$")
    total = 0
    for raw in git("diff", "--numstat", base).splitlines():
        parts = raw.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and not gen.search(parts[2]):
            total += int(parts[0]) + int(parts[1])
    return total


#: the pass log feature 371 keeps beside the state: one line per check's return, read by `scripts/reviews/ledger_owed.py`
PASS_LOG = "check-passes.jsonl"


def _reviews() -> tuple[Any, Any]:
    """`ledger_lint` (its CHECKS) and `review_cost` (the cost cells), from `scripts/reviews/` - imported when first needed."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "reviews"))
    import ledger_lint  # noqa: PLC0415
    import review_cost  # noqa: PLC0415

    return ledger_lint, review_cost


def _first_prompt(lines: list[str]) -> str:
    """The dispatch's prompt - the transcript's first user message - as a one-line subject a ledger cell can hold."""
    for line in lines:
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        msg = rec.get("message") if isinstance(rec, dict) else None
        if isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content")
            text = content if isinstance(content, str) else " ".join(str(p.get("text", "")) for p in content or [] if isinstance(p, dict))
            first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
            return re.sub(r"[|\s]+", " ", first)[:100].strip()
    return ""


def log_pass(git_dir: Path, mode: str, payload: Mapping[str, Any], now: float | None = None) -> bool:
    """Append a check's pass to the log (feature 371, plan D1/D1b): at SubagentStop (`returned`) for an agent whose type is a
    check, and at PostToolUse (`launched`) for a FOREGROUND one, which has returned by then. The cells are computed over the
    whole transcript, as `make review-cost` computes them; nothing is held between the two events, so a switch of feature
    drops nothing; each return of a resumed agent is a pass of its own, its cells this return's segment; the same return
    seen by both events is logged once. Never raises: a hook that
    fails here must not take the session's tool call with it."""
    try:
        ledger_lint, review_cost = _reviews()
        if mode == "returned":
            check, aid, tpath = str(payload.get("agent_type") or ""), str(payload.get("agent_id") or ""), str(payload.get("agent_transcript_path") or "")
        else:
            resp = payload.get("tool_response") if isinstance(payload.get("tool_response"), Mapping) else {}
            ti = payload.get("tool_input") if isinstance(payload.get("tool_input"), Mapping) else {}
            if resp.get("status") != "completed":
                return False  # a background check is logged at its return
            check, aid = str(ti.get("subagent_type") or ""), str(resp.get("agentId") or "")
            found = review_cost.transcript(aid) if aid else None
            tpath = str(found or "")
        if check not in ledger_lint.CHECKS or not tpath or not Path(tpath).is_file():
            return False
        lines = Path(tpath).read_text(encoding="utf-8", errors="replace").splitlines()
        # THIS RETURN is the transcript's last segment (a resumed agent's earlier returns are passes of their own, logged at
        # their own stops - plan review 2). GUARD_EDIT_OK: fixing the log's cells, which were read too early. The cells here
        # are PROVISIONAL: at SubagentStop the agent's last call is not yet on disk (measured 2026-10-10: a 13 s check logged
        # as 4 s, its final call missing), so `ledger_owed.py` recomputes them from the finished transcript by `segment`, and
        # these stand only where that transcript is gone.
        parts = review_cost.segments(lines)
        wall, tokens = review_cost.cells(review_cost.cost(parts[-1])).split(" | ", 1)
        rec = {
            "date": time.strftime("%Y-%m-%d", time.localtime(now or time.time())),
            "check": check,
            "subject": _first_prompt(lines),
            "agent": aid,
            "segment": len(parts) - 1,
            "wall": wall,
            "tokens": tokens,
        }
        log = git_dir / PASS_LOG
        prior = [json.loads(ln) for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()] if log.is_file() else []
        if any(r.get("agent") == aid and r.get("segment") == len(parts) - 1 for r in prior):
            return False  # the same return seen by both events (a foreground check): one pass, logged once
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        return True
    except Exception:  # noqa: BLE001 - the hook's own failure never blocks the session (see the docstring)
        return False


def handle(mode: str, payload: Mapping[str, Any], now: float | None = None) -> str:
    """One hook event. Returns a refusal message (the hook exits 2 with it) or ''. Held under the state's lock."""
    path = state_path(str(payload.get("cwd") or os.getcwd()))
    if path is None:
        return ""
    with locked(path):
        return _handle(mode, payload, path, time.time() if now is None else now)


def _handle(mode: str, payload: Mapping[str, Any], path: Path, now: float) -> str:
    """`handle`'s body, with the state file's path and the lock held."""
    if mode in ("returned", "launched"):
        log_pass(path.parent, mode, payload, now)  # every check's pass, apart from the page-check state (feature 371)
    state = load(path)
    if mode == "edit" and state.get("plan_holds"):  # hour 30's fix: what each live hold holds, before the call runs
        hm_planhold.snapshot(state, _root(payload), str(payload.get("tool_use_id") or ""), now)
        save(path, state)
    feature = _feature(path.parent.parent if path.parent.name == ".git" else Path(str(payload.get("cwd") or ".")))
    if state.get("feature") != feature:  # the round cap counts per feature (FR-010): a new feature starts its own count
        state = {"feature": feature, "dispatches": state.get("dispatches", {})}
    ti = payload.get("tool_input") or {}
    ti = ti if isinstance(ti, Mapping) else {}
    out = ""
    if mode == "dispatch" and payload.get("tool_name") == "Agent":
        check = str(ti.get("subagent_type") or "")
        root = _root(payload)
        if check == "round-arbiter":
            m = re.search(r"^trigger: (.+)$", _manifest_of(str(ti.get("prompt") or ""))[1], re.M)
            if root is not None and m and m.group(1).strip() in hm_arbiter.rulings(root):
                return f"{m.group(1).strip()} is already ruled - one ruling per trigger, binding (feature 375 FR-011)"
            return ""
        if check == "spec-fidelity":  # feature 385 T85: a plan review holds the section or blocks it reads
            hm_planhold.hold(state, str(payload.get("tool_use_id") or now), str(ti.get("prompt") or ""), now)
            save(path, state)  # a plan review is no check kind: the branch below returns before the state is saved
        if check not in CHECK_KINDS:
            return ""
        prompt = str(ti.get("prompt") or "")
        # each escape reaches its own rule only: FREEZE_OK the apply-once hold (FR-003c), ARBITER_OK the arbiter's holds and
        # the round cap (FR-010/011) - the plan review of amendment 1
        freeze_ok, arbiter_ok = escaped("FREEZE_OK", prompt), escaped("ARBITER_OK", prompt)
        manifest, text = _manifest_of(str(ti.get("prompt") or ""))
        if root is not None and check in PAGE_CHECKS:  # FR-010: the subject's versions as each dispatch found it
            for s in subjects_of_manifest(text):
                vs = state.setdefault("versions", {}).setdefault(s, [])
                cur = subject_blocks(root, s)
                if cur and (not vs or vs[-1] != cur):
                    vs.append(cur)
                    del vs[:-12]
                    back = oscillation(vs)
                    if back:
                        hm_arbiter.trip(root, f"reversal:{s}@{len(vs)}", "reversal", s, f"{s}: a block dropped earlier is back - \"{back}...\"", now)
        if not escaped("BATCH_OK", prompt) and (held := batch_refusal(root, check, text, now)):
            return held
        tid = str(payload.get("tool_use_id") or now)
        out = dispatch(state, tid, check, manifest, text, now, root, freeze_ok, arbiter_ok)
        if not out and tid.startswith("wave:"):  # a check-wave unit: paired at its return by its prompt (plan D48)
            state["dispatches"][tid].update(wave=_wave_key(prompt), wave_len=len(_collapsed(prompt)))
        if not out and root is not None:
            since = window_start(root)
            n, lines = dispatches_since(state, since), changed_lines(root)
            trigger, last = hm_arbiter.cascade_state(root, since)
            if hm_arbiter.cascade(n, lines, last):  # live after any ruling; counted from the dispatches at the last one
                hm_arbiter.trip(root, trigger, "cascade", "", f"{n} check dispatches over {lines} changed lines", now)
    elif mode == "launched" and payload.get("tool_name") == "Agent":
        resp = payload.get("tool_response") if isinstance(payload.get("tool_response"), Mapping) else {}
        hm_planhold.launched(state, str(payload.get("tool_use_id") or ""), str(resp.get("agentId") or ""))
        launched(state, str(payload.get("tool_use_id") or ""), str(resp.get("agentId") or ""), resp.get("status") == "async_launched", response_text(resp), path.parent / "check-replies")
    elif mode == "launched" and payload.get("tool_name") == "TaskStop":  # feature 385 T104 (D121): a stopped review returns no reply
        hm_planhold.returned(state, str(ti.get("task_id") or ti.get("shell_id") or ""))
    elif mode == "returned":
        hm_planhold.returned(state, str(payload.get("agent_id") or ""))
        pair_wave(state, str(payload.get("agent_id") or ""), str(payload.get("agent_transcript_path") or ""))
        returned(state, str(payload.get("agent_id") or ""), _reply_of(str(payload.get("agent_transcript_path") or ""), str(payload.get("last_assistant_message") or "")), path.parent / "check-replies")
    elif mode == "after":  # the round arbiter's fix on hour:385-approach-checklist@30: a held section changed however it was named
        msg = hm_planhold.restore(state, _root(payload), str(payload.get("tool_use_id") or ""))
        save(path, state)
        return msg
    elif mode == "edit" and (held := hm_planhold.refusal(state, _root(payload), str(payload.get("tool_name") or ""), ti, now,
                                                        escaped("PLAN_EDIT_OK", " ".join(str(v) for v in ti.values())))):
        return held
    elif mode == "edit" and payload.get("tool_name") == "Bash":
        command = str(ti.get("command") or "")
        root = _root(payload)
        if root is not None and re.search(r"(?:^|[;&|(]\s*)(?:[A-Z_]+=\S*\s+)*make\s+(?:-\S+\s+)*done\b", command, re.M):
            held = hm_arbiter.blocking(root, gate=True)
            if held and not escaped("ARBITER_OK", command):
                return hm_arbiter.refusal(held)
        return "" if escaped("FREEZE_OK", command) else apply_refusal(state, command, now)
    elif mode == "edit" and payload.get("tool_name") in ("Edit", "Write", "MultiEdit"):
        if escaped("FREEZE_OK", " ".join(str(v) for v in ti.values())):
            return ""
        old = str(ti.get("old_string") or "") if payload.get("tool_name") == "Edit" else ""
        return edit_refusal(state, str(ti.get("file_path") or ""), old, str(ti.get("new_string") or ti.get("content") or ""), now)
    else:
        return ""
    if not out:
        save(path, state)
    return out


def close(root: Path, subject: str, reason: str, now: float, agent: str = "") -> int:
    """`make check-closed`: close the checks on `subject` that went SILENT - running past STALE_S with no return - and record
    each use with its reason in the guard census. A live check is never closed here (the plan review of amendment 1: closing
    any check at any time was an unlogged way past the freeze) - except the one `agent` names, a check the session STOPPED
    itself (TaskStop): it will never return, and before this it held its page frozen until it went stale (feature 374,
    round arbiter hour 4 - a quote-check sent the stale top-level MANIFEST and stopped needed FREEZE_OK to move on)."""
    path = state_path(str(root))
    if path is None:
        return _close(None, {}, subject, reason, now, agent)
    with locked(path):
        return _close(path, load(path), subject, reason, now, agent)


def _close(path: Path | None, state: dict[str, Any], subject: str, reason: str, now: float, agent: str = "") -> int:
    """`close`'s body, with the state loaded under its lock."""
    if not escaped("CHECK_CLOSED", f'CHECK_CLOSED="{reason}"'):
        print("check-closed: REASON needs two words and eight characters - it is what a later audit reads", file=sys.stderr)
        return 2
    silent = [
        d
        for d in state.get("dispatches", {}).values()
        if subject in d.get("subjects", []) and ((d.get("state") == "running" and now - float(d.get("t", 0)) > STALE_S) or (agent and d.get("aid") == agent and d.get("state") != "answered"))
    ]
    for d in silent:
        d["state"] = "answered"
        d["closed"] = reason
    if path and silent:
        save(path, state)
    live = len(running(state, subject, now))
    print(f"check-closed: {len(silent)} silent dispatch(es) on {subject} closed - {reason}" + (f"; {live} still running and not silent: wait for them" if live else ""))
    return 0


#: what `make record-owed` keeps of its batched lines (feature 385 T81, plan D100), and how long it is trusted
BATCHES, BATCHES_FRESH_S = "modal-batches.json", 7200
_POPUP_AGENTS = ("modal-form", "modal-depiction", "modal-research")


def batch_refusal(root: Path | None, check: str, text: str, now: float) -> str:
    """A pop-up agent sent on ONE pop-up while `make record-owed` names that pop-up in a batch of two or more for the same agent
    (feature 385 T81, plan D101; the GM's approved change 1: T10's checks sent 90 single-pop-up agents). No record, or one older
    than two hours, refuses nothing."""
    if root is None or check not in _POPUP_AGENTS:
        return ""
    uids = {ln.split()[1].split(":", 1)[1] for ln in text.splitlines() if ln.startswith("unit: ") and ":" in ln.split()[1]}
    if len(uids) != 1:
        return ""
    gd = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    try:
        rec = json.loads((Path(gd) / BATCHES).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    kinds = (rec.get("batches") or {}).get(check) or []
    (uid,) = uids
    if now - float(rec.get("utc") or 0) > BATCHES_FRESH_S or len(kinds) < 2 or not any(uid == k or uid.endswith(k) or k.endswith(uid) for k in kinds):
        return ""
    return (f"{len(kinds)} pop-ups owe {check} together - send ONE agent on them all: make modal-bundle KIND=\"{' '.join(kinds)}\" "
            f"FOR={check} (feature 385 T81), batched")


def escape_for(msg: str) -> str:
    """The escape that reaches the rule which refused: the arbiter's holds take ARBITER_OK, never FREEZE_OK (feature 374: the
    tip named FREEZE_OK on a closed unit, and FREEZE_OK does not reach that rule)."""
    return "BATCH_OK" if msg.endswith(", batched") else "ARBITER_OK" if "arbiter" in msg else "FREEZE_OK"


def main(argv: list[str]) -> int:
    mode = argv[0] if argv else ""
    if mode == "close" and len(argv) in (3, 4):  # make check-closed SUBJECT= REASON= [AGENT=]
        return close(Path(os.getcwd()), argv[1], argv[2], time.time(), argv[3] if len(argv) == 4 else "")
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    msg = handle(mode, payload)
    if msg:
        print(f"BLOCKED: {msg}\n(scripts/hooks/lib/hm_checks.py; escape {escape_for(msg)}=\"<reason>\" in the prompt or the edit)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
