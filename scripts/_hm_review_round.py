#!/usr/bin/env python3
"""The review-round guard's decision (feature 249, GM 2026-09-14) - a round after the first reads the diff.

GUARD_EDIT_OK: feature 249 - a NEW guard's core, beside review-round-hooks.sh, which only logs and prints.

THE DEFECT. `spec-fidelity`'s contract (MODE 3) has said since feature 236 that a round after the first
reads only the changed passages - the GM's *"only rereviewing the new stuff"* - and that a reviewer not
told which passages changed should ASK rather than re-read. On 2026-09-14 two rounds of one small spec
amendment each read every file end to end (165k and 110k tokens, over half the change's eleven
minutes), because the session's dispatch handed over the whole spec and whole-spec questions. The rule
was right and the prompt asked for more than the rule. The GM: *"I want this all to be automatic since
instructions are not reliably followed, but things which happen automatically enforced by make files or
by tooling such as hooks are more likely to actually be implemented."*

WHAT IT DOES. On a `spec-fidelity` dispatch that is a SPEC review of a feature this guard has seen
before, it REWRITES the prompt: a preamble is prepended carrying the round number within the current
pass, the previous round's verdict verbatim (read back from the session's own subagent transcripts, or
the spec's Review history marked as the session's summary when none is found), a unified diff of the
feature directory against the snapshot taken at the previous dispatch, and the instruction to read only
that plus what a grep for the ids it names turns up. The session's own prompt follows unchanged. Every
dispatch refreshes the snapshot. A MODE 4 plan review and a MODE 1 exception check pass untouched -
a plan is read whole by feature 243's ruling, and an exception check precedes the initial reading.

WHY A SNAPSHOT AND NOT A COMMIT. A round's application and the Review history entry recording it may
share one commit, may be uncommitted at dispatch, or may be spread over several; the directory as it
stood when the reviewer last looked is the one base that is right in all three cases (spec 249 R4).

WHY THE VERDICT COMES FROM THE TRANSCRIPT. The next round confirms the previous round's ITEMS, and the
contract says to judge them against the request rather than against the session's summary of what it
did. A subagent's transcript persists beside the session's (`<transcript>/subagents/agent-*.jsonl`):
its first record is the dispatch prompt, its last the reviewer's final message (spec 249 R3).

The bash wrapper resolves this session's clone (`clone-sync-hooks.sh resolve`) and passes it in the
environment; this module never blocks except on the reason floor every escape carries.
"""

from __future__ import annotations

import difflib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _hm_escape import escape_reason, reason_is_enough  # noqa: E402
from _stale_terms import read_dir, render as render_stale, stale_candidates  # noqa: E402

#: feature 253 (GM 2026-09-19): before a later round is SPENT, the feature directory is searched for the old
#: value of whatever changed; candidates refuse the dispatch once, and this token (with a reason) says they
#: were looked at and are not stale.
STALE_TOKEN = "STALE_TERMS_OK"


TOKEN = "REVIEW_ROUND_OK"
AGENT = "spec-fidelity"
#: MODE 3 on its own shorter contract (feature 251, GM 2026-09-19): a later round is a narrower job than a first
#: reading - the previous verdict's items and the diff - and it is most of the rounds, so a rewritten
#: round is ROUTED to this agent. Proven before it was relied on: a hook's `updatedInput` may change
#: `subagent_type` (specs/251-tiered-subagent-checks/research.md R4).
TWIN = "spec-fidelity-verify"
AGENTS = (AGENT, TWIN)
GUARD = "review-round"
_FEATURE = re.compile(r"specs/(\d{3}-[a-z0-9][a-z0-9-]*)")
_SPEC_MODE = re.compile(r"\bMODE\s*[23]\b", re.I)
_PLAN_MODE = re.compile(r"\bMODE\s*4\b|\bPLAN REVIEW\b", re.I)
_EXCEPTION_MODE = re.compile(r"\bMODE\s*1\b|\bEXCEPTION CHECK\b", re.I)
_VERDICTS = ("CHANGES REQUIRED", "FAITHFUL", "NOT-REVIEWABLE")
_SNAP_SUFFIXES = {".md", ".json", ".txt", ".py", ".html", ".csv"}
_SNAP_MAX_BYTES = 2_000_000


def classify_mode(prompt: str) -> str:
    """`spec`, `plan` or `exception` - read with PRECEDENCE (spec 249 FR-003, D8).

    A round's prompt relays the previous round's items, which say "plan review" and "exception" in
    ordinary sentences; round 2 of this feature's own review named MODE 3 and both of those words, and
    a bare-word test would have classed it a plan review and passed it untouched. So a MODE 2/3 marker
    wins whatever else the prompt says, and the other two modes are keyed on the contract's heading
    forms, never on a bare `plan.md` or `exception`.
    """
    if _SPEC_MODE.search(prompt):
        return "spec"
    if _PLAN_MODE.search(prompt):
        return "plan"
    if _EXCEPTION_MODE.search(prompt):
        return "exception"
    return "spec"


def feature_of(prompt: str) -> str:
    m = _FEATURE.search(prompt)
    return m.group(1) if m else ""


def _text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(b.get("text", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def verdict_of(text: str) -> str:
    """The verdict a reviewer's final message carries - the LAST of the three words wins.

    A CHANGES REQUIRED report can say "ruled FAITHFUL" about one item in its prose (round 1 of this
    feature did), and a FAITHFUL report can name "CHANGES REQUIRED" while confirming the previous
    round's items; the verdict line is written last, so the last occurrence is the verdict.
    """
    best, best_at = "", -1
    for v in _VERDICTS:
        at = text.rfind(v)
        if at > best_at:
            best, best_at = v, at
    return best


def previous_verdict(transcript_path: str, feature: str) -> tuple[str, str]:
    """(verdict text, verdict word) from the newest subagent transcript that reviewed this feature."""
    if not transcript_path or not transcript_path.endswith(".jsonl"):
        return "", ""
    sub = pathlib.Path(transcript_path[: -len(".jsonl")]) / "subagents"
    if not sub.is_dir():
        return "", ""
    files = sorted(sub.glob("agent-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files:
        try:
            lines = [ln for ln in f.read_text(errors="replace").splitlines() if ln.strip()]
            first = json.loads(lines[0])
        except Exception:
            continue
        if f"specs/{feature}" not in _text_of((first.get("message") or {}).get("content")):
            continue
        for raw in reversed(lines):
            try:
                rec = json.loads(raw)
            except Exception:
                continue
            msg = rec.get("message") or {}
            if msg.get("role") != "assistant":
                continue
            text = _text_of(msg.get("content"))
            if not text.strip():
                continue
            v = verdict_of(text)
            if v:
                return text, v
            break
    return "", ""


def review_history(spec_md: pathlib.Path) -> str:
    """The Review history section's LAST entry, or "" - the fallback when no transcript answers."""
    if not spec_md.is_file():
        return ""
    text = spec_md.read_text(errors="replace")
    m = re.search(r"^## Review history\s*$", text, re.M)
    if not m:
        return ""
    body = text[m.end() :]
    nxt = re.search(r"^## ", body, re.M)
    if nxt:
        body = body[: nxt.start()]
    entries = re.split(r"^(?=- )", body, flags=re.M)
    entries = [e.strip() for e in entries if e.strip().startswith("- ")]
    return entries[-1] if entries else ""


def has_review_round(spec_md: pathlib.Path) -> bool:
    return bool(re.search(r"spec-fidelity|CHANGES REQUIRED|FAITHFUL", review_history(spec_md)))


def _snap_files(root: pathlib.Path) -> list[pathlib.Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.suffix not in _SNAP_SUFFIXES or p.stat().st_size > _SNAP_MAX_BYTES:
            continue
        out.append(p)
    return out


def take_snapshot(feature_dir: pathlib.Path, snap: pathlib.Path) -> None:
    if snap.exists():
        shutil.rmtree(snap)
    for p in _snap_files(feature_dir):
        dst = snap / p.relative_to(feature_dir)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)


def diff_since(snap: pathlib.Path, feature_dir: pathlib.Path) -> str:
    old = {p.relative_to(snap).as_posix(): p for p in _snap_files(snap)} if snap.is_dir() else {}
    new = {p.relative_to(feature_dir).as_posix(): p for p in _snap_files(feature_dir)}
    out: list[str] = []
    for rel in sorted(set(old) | set(new)):
        a = old[rel].read_text(errors="replace").splitlines(keepends=True) if rel in old else []
        b = new[rel].read_text(errors="replace").splitlines(keepends=True) if rel in new else []
        if a == b:
            continue
        out.extend(difflib.unified_diff(a, b, fromfile=f"a/{rel}", tofile=f"b/{rel}", n=3))
    return "".join(out)


def preamble(feature: str, round_no: int, new_pass: bool, verdict_text: str, verdict_from: str, diff: str) -> str:
    head = [
        f"MODE 3 (VERIFY) - round {round_no} of feature {feature}, assembled by the tooling at dispatch "
        "(scripts/review-round-hooks.sh, feature 249).",
        "",
        "THE RULE (the GM, 2026-09-14): a round after the first reviews the paragraphs that changed, not the "
        "whole spec. Read ONLY this preamble and the passages a grep of the feature directory for the ids and "
        "terms it names turns up. Do not read spec.md, request.md or tasks.md end to end. Where the session's "
        "prompt below asks a whole-spec question (every FR has an SC, every task id is defined), answer it from "
        "the diff and a grep, never from a re-read. Say which passages you read in full.",
    ]
    if new_pass:
        head += [
            "",
            "This is round 1 of a NEW PASS: the previous verdict was FAITHFUL, so the diff below amends an "
            "accepted spec and the five-round cap counts from here (the GM's 2026-09-12 ruling).",
        ]
    if verdict_from == "transcript":
        v_head = "=== The previous round's verdict, VERBATIM from the reviewer's own transcript ==="
    elif verdict_from == "history":
        v_head = (
            "=== The previous round as the SESSION recorded it in the spec's Review history (the reviewer's "
            "own words were not recoverable from the transcripts - judge the items against the request, not "
            "against this summary) ==="
        )
    else:
        v_head = "=== No previous verdict could be recovered - the spec's Review history is empty ==="
    body = diff.strip() or "Nothing in the feature directory changed since the previous dispatch."
    return "\n".join(
        head
        + ["", v_head, "", verdict_text.strip() or "(none)", "", f"=== What changed in specs/{feature} since that round was dispatched (unified diff) ===", "", body, "", "=== The session's prompt follows ===", ""]
    )


def _refusal(token: str) -> str:
    return (
        f"BLOCKED: {token} with no reason given.\n\n"
        "An escape is a workaround, and a workaround nobody can audit is indistinguishable from the\n"
        "rule not existing. Say why, in the prompt, and it ships with it:\n\n"
        f'    {token}="<why this dispatch needs the whole spec read again>"\n\n'
        'Two words and eight characters is the whole bar - "restructured spec" clears it.\n'
        "(GM 2026-08-30, feature 170; the reasons are what `make audit` shows you.)\n"
    )


def _stale_refusal(feature: str, candidates: list[dict]) -> str:
    return (
        f"\n\033[1mBLOCKED: specs/{feature} still carries the OLD value of something this change moved - look before a review round is spent on it.\033[0m\n"
        + render_stale(candidates)
        + "\n\nA later spec-fidelity round costs nearly what a first reading does, and the commonest thing it finds is text left saying the\n"
        "old thing (feature 253, the GM 2026-09-19). Nothing was dispatched and no round was counted. Either:\n"
        "  - fix the lines above (and anything else the change made untrue), then dispatch again; or\n"
        f'  - if they are NOT stale, dispatch again with {STALE_TOKEN}="<why they stand>" in the prompt.\n'
        f"`make stale-terms F={feature.split('-')[0]}` re-runs the search. (scripts/_stale_terms.py, scripts/review-round-hooks.sh)\n"
    )


def judge(payload: dict, clone: str) -> dict:
    """The whole decision. Returns {event, rule, detail, exit, stdout, stderr}."""
    ti = payload.get("tool_input") or {}
    # EITHER type is a round of the same review: a hand dispatch of the twin (the no-snapshot branch below
    # tells the session to make one) must take and refresh the snapshot too, or the round after it has
    # nothing to diff against (feature 251, spec-fidelity's aside on round 1).
    if payload.get("tool_name") != "Agent" or ti.get("subagent_type") not in AGENTS:
        return {"event": "", "rule": "", "detail": "", "exit": 0, "stdout": "", "stderr": ""}
    prompt = str(ti.get("prompt") or "")
    mode = classify_mode(prompt)
    if mode != "spec":
        return {"event": "permitted", "rule": "other-mode", "detail": f"{mode} review passes untouched", "exit": 0, "stdout": "", "stderr": ""}
    feature = feature_of(prompt)
    root = pathlib.Path(clone) if clone else None
    feature_dir = (root / "specs" / feature) if (root and feature) else None
    state = (root / ".git" / "review-round" / feature) if feature_dir else None
    snap = state / "snapshot" if state else None
    # THE ESCAPE FIRST, so the guard can be repaired through the channel it guards.
    if TOKEN in prompt:
        reason = escape_reason(prompt, TOKEN)
        if not reason_is_enough(reason):
            return {"event": "blocked", "rule": f"{TOKEN}-no-reason", "detail": prompt[:200], "exit": 2, "stdout": "", "stderr": _refusal(TOKEN)}
        if feature_dir and feature_dir.is_dir():
            take_snapshot(feature_dir, snap)
            _write_state(state, _read_round(state) or 1)
        return {"event": "escaped", "rule": "review-round-ok", "detail": reason, "exit": 0, "stdout": "", "stderr": ""}
    if not feature_dir or not feature_dir.is_dir():
        return {"event": "permitted", "rule": "no-feature", "detail": feature or "no specs/NNN-slug in the prompt", "exit": 0, "stdout": "", "stderr": ""}
    spec_md = feature_dir / "spec.md"
    if not snap.is_dir():
        take_snapshot(feature_dir, snap)
        _write_state(state, 1)
        if has_review_round(spec_md):
            ctx = (
                f"review-round: specs/{feature} already records a review round, but the tooling holds no earlier "
                "snapshot of it to diff against, so this dispatch is not rewritten. This is a round after the first: "
                f"dispatch `{TWIN}` (the later-round contract) rather than `{AGENT}`, and "
                "make sure the prompt carries the previous round's items and ONLY the passages that changed. "
                "From this dispatch on the tooling snapshots the directory and builds the diff itself."
            )
            return {"event": "reminded", "rule": "history-without-snapshot", "detail": feature, "exit": 0, "stdout": _context(ctx), "stderr": ""}
        return {"event": "permitted", "rule": "first-round", "detail": feature, "exit": 0, "stdout": "", "stderr": ""}
    # THE OLD VALUE IS LOOKED FOR FIRST (feature 253), before any snapshot or round state moves: a refused
    # dispatch spends nothing, not even one of the five rounds.
    stale_note = ""
    if STALE_TOKEN in prompt:
        stale_reason = escape_reason(prompt, STALE_TOKEN)
        if not reason_is_enough(stale_reason):
            return {"event": "blocked", "rule": f"{STALE_TOKEN}-no-reason", "detail": prompt[:200], "exit": 2, "stdout": "", "stderr": _refusal(STALE_TOKEN)}
        stale_note = f" {STALE_TOKEN}: {stale_reason}"
    else:
        candidates = stale_candidates(read_dir(snap), read_dir(feature_dir))
        if candidates:
            return {"event": "blocked", "rule": "stale-terms", "detail": f"{feature}: {len(candidates)} candidate(s)", "exit": 2, "stdout": "", "stderr": _stale_refusal(feature, candidates)}
    diff = diff_since(snap, feature_dir)
    v_text, v_word = previous_verdict(str(payload.get("transcript_path") or ""), feature)
    v_from = "transcript" if v_text else ""
    if not v_text:
        v_text = review_history(spec_md)
        v_from = "history" if v_text else ""
        v_word = verdict_of(v_text) if v_text else ""
    prev_round = _read_round(state) or 1
    new_pass = v_word == "FAITHFUL"
    round_no = 1 if new_pass else (prev_round if v_word == "NOT-REVIEWABLE" else prev_round + 1)
    new_prompt = preamble(feature, round_no, new_pass, v_text, v_from, diff) + prompt
    take_snapshot(feature_dir, snap)
    _write_state(state, round_no)
    updated = dict(ti)
    updated["prompt"] = new_prompt
    updated["subagent_type"] = TWIN

    ctx = (
        f"review-round: this dispatch was rewritten into MODE 3 round {round_no} of specs/{feature} and ROUTED to "
        f"`{TWIN}` (the same review's later-round contract - feature 251, the GM 2026-09-19) "
        "(feature 249, the GM 2026-09-14): the previous round's verdict and the diff of the feature directory since "
        "that dispatch were prepended, and the reviewer is told to read those plus grep hits only. Your own prompt "
        f'follows them unchanged. For a deliberate full re-read, put {TOKEN}="<reason>" in the prompt.'
    )
    out = json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": updated, "additionalContext": ctx}})
    rule = "mode-3-preamble-stale-ok" if stale_note else "mode-3-preamble"   # the escape is recorded with its reason
    return {"event": "rewrote", "rule": rule, "detail": f"{feature} round {round_no}{stale_note}", "exit": 0, "stdout": out, "stderr": ""}


def _context(text: str) -> str:
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}})


def _read_round(state: pathlib.Path) -> int:
    try:
        return int((state / "round").read_text().strip())
    except Exception:
        return 0


def _write_state(state: pathlib.Path, round_no: int) -> None:
    state.mkdir(parents=True, exist_ok=True)
    (state / "round").write_text(f"{round_no}\n")
    (state / "dispatched").write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")


def clone_for(payload: dict, resolved: str) -> str:
    """This session's clone as the guard resolved it, else the git top level of the payload's cwd."""
    if resolved and pathlib.Path(resolved).is_dir():
        return resolved
    cwd = str(payload.get("cwd") or os.getcwd())
    try:
        top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
        return top.stdout.strip() if top.returncode == 0 else ""
    except Exception:
        return ""


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "judge":
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        verdict = judge(payload, clone_for(payload, os.environ.get("REVIEW_ROUND_CLONE", "")))
        json.dump(verdict, sys.stdout)
    elif mode == "state":
        st = pathlib.Path(sys.argv[2]) / ".git" / "review-round" / sys.argv[3]
        print(f"round={_read_round(st)} snapshot={'yes' if (st / 'snapshot').is_dir() else 'no'}")
    else:
        print("usage: _hm_review_round.py judge < payload.json | state <clone> <feature>", file=sys.stderr)
        sys.exit(2)
