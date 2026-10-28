#!/usr/bin/env python3
"""Every pass of every check owes its row in the review ledger (feature 371).

WHY (the GM, 2026-10-10: *"a log of when our subagent checks find something that needs to be changed and when they don't, so
that we can see how often they are paying off"*). The log is `dev/review-ledger.md`'s measured table, and nothing made its rows
get written: feature 328 ran 26 glyph checks and wrote none of their rows, rebuilt by hand at a batch's close. So every check's
pass is logged when the agent returns (`hm_checks.py`, into `<git common dir>/check-passes.jsonl`, with its cost cells computed
as `make review-cost` computes them), and a pass is ANSWERED by a measured row carrying its check and those same cells - the
table copies its cost from `make review-cost`, never types it, so the cells identify the pass (two same-day rounds of one
check on one subject are two passes with two costs).

    ledger_owed.py [--log <jsonl>] [--ledger <md>]             list the unanswered passes, each with the row to add
    ledger_owed.py --write "<where the session recorded what it did>" [--session <sid>]
                                                             append each unanswered pass's row, filled from the agent's
                                                             own reply (the page-session runner, at each session's end)
    ledger_owed.py ... --refuse                                 exit 1 while any is unanswered (the push)

Escape at the push: LEDGER_ROWS_OK="<reason>" in sync-with-main's environment, recorded in the bypass log.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

sys.dont_write_bytecode = True  # the push runs this in the tree it is about to push
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_lint  # noqa: E402
import review_cost  # noqa: E402

LOG = "check-passes.jsonl"
JUDGED = ("verdict", "finding", "class", "author missed?", "acted on")


def _norm(cell: str) -> str:
    return re.sub(r"\s+", " ", cell).strip()


def load_passes(path: Path) -> list[dict[str, str]]:
    """The logged passes, oldest first; a line that is not a pass is skipped."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and rec.get("check") and rec.get("wall"):
            out.append({k: str(v) for k, v in rec.items()})
    return out


#: feature 383 (the GM 2026-10-12: "we probably don't need to search the entire session transcript ... if we are keeping track of
#: how far back it is that our most recent search was for"): a pass's cells, once costed, are kept here with its transcript's
#: path, size and mtime - a finished transcript never changes, and a resumed agent's appends change both - so a run where
#: every pass is already costed reads no transcript, and the transcripts are listed once for the passes that are new
SETTLED = "l7r-cache/ledger-settled.json"


class _Transcripts:
    """`find(agent)` - the newest transcript of an agent, from ONE listing of every subagent transcript, made on the first
    lookup (a glob per pass was most of this check's time)."""

    def __init__(self, root: Path) -> None:
        self.root, self._index = root, None

    def find(self, agent: str) -> Path | None:
        if self._index is None:
            found: dict[str, tuple[float, Path]] = {}
            for path in self.root.glob("*/*/subagents/agent-*.jsonl"):
                aid, at = path.name[len("agent-") : -len(".jsonl")], path.stat().st_mtime
                if aid not in found or at > found[aid][0]:
                    found[aid] = (at, path)
            self._index = {a: p for a, (_, p) in found.items()}
        return self._index.get(agent)


def _stat(path: Path) -> list[float]:
    try:
        st = path.stat()
    except OSError:
        return []
    return [st.st_size, st.st_mtime]


def _kept_file() -> Path | None:
    import os  # noqa: PLC0415

    if os.environ.get("L7R_CACHE_OFF", "") not in ("", "0"):
        return None
    out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False).stdout.strip()
    return Path(out).resolve() / SETTLED if out else None


def settled(passes: Sequence[dict[str, str]], root: Path = review_cost.DEFAULT_ROOT, kept_file: Path | None = None) -> list[dict[str, str]]:
    """Each pass with its cells recomputed from its agent's FINISHED transcript, the segment it logged (its return) - the
    cells `make review-cost` prints. The hook logs at SubagentStop, before the agent's last call reaches the disk (measured
    2026-10-10: a 13 s check logged as 4 s), so its own cells are provisional; they stand only where the transcript is gone.
    A pass already costed is served from `kept_file` while its transcript is unchanged (feature 383)."""
    try:
        kept = json.loads(kept_file.read_text(encoding="utf-8")) if kept_file is not None and kept_file.is_file() else {}
    except (OSError, ValueError):
        kept = {}
    kept = kept if isinstance(kept, dict) else {}
    index, added, out = _Transcripts(root), False, []
    for p in passes:
        key = f"{p.get('agent', '')}#{p.get('segment', '')}#{p.get('check', '')}#{p.get('wall', '')}"
        hit = kept.get(key) if p.get("agent") else None
        if isinstance(hit, dict) and hit.get("stat") == _stat(Path(hit.get("path", ""))):
            out.append({**p, **hit["cells"]} if hit.get("cells") else p)
            continue
        path = index.find(p["agent"]) if p.get("agent") else None
        parts = review_cost.segments(path.read_text(encoding="utf-8", errors="replace").splitlines()) if path else []
        # a line logged before the segment was (2026-10-10) is settled only where its agent returned once - it can be no other
        n = int(p["segment"]) if str(p.get("segment", "")).isdigit() else (0 if len(parts) == 1 else len(parts))
        cells: dict[str, str] = {}
        if n < len(parts):
            wall, tokens = review_cost.cells(review_cost.cost(parts[n])).split(" | ", 1)
            # the logged cells are kept beside: a row written from them before this recompute (every row of 2026-10-10's
            # sessions) still answers its pass - without them 131 answered passes read as owed again
            cells = {"wall": wall, "tokens": tokens, "logged": f"{p.get('wall', '')} | {p.get('tokens', '')}"}
        if path is not None:
            kept[key], added = {"path": str(path), "stat": _stat(path), "cells": cells}, True
        out.append({**p, **cells})
    if added and kept_file is not None:
        try:
            kept_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = kept_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(kept), encoding="utf-8")
            tmp.replace(kept_file)
        except OSError:
            pass  # an unwritable cache costs the next run its speed, never its answer
    return out


def distinct(passes: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    """Each logged line is a pass (plan review 2: a resumed agent's every return is one); an identical repeat of an agent's
    line - the same return seen by two events - is one."""
    seen, out = set(), []
    for p in passes:
        key = (p.get("agent"), p.get("check"), p.get("segment")) if p.get("segment") is not None else (p.get("agent"), p.get("check"), _norm(p.get("wall", "")), _norm(p.get("tokens", "")))
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def unanswered(passes: Sequence[dict[str, str]], ledger_text: str) -> list[dict[str, str]]:
    """The passes no measured row answers - a row of the same check carrying the pass's wall and tokens cells."""
    keys = set()
    for _n, cells in ledger_lint.measured_rows(ledger_text):
        if len(cells) == len(ledger_lint.COLUMNS):
            row = dict(zip(ledger_lint.COLUMNS, cells, strict=True))
            keys.add((_norm(row["check"]), _norm(row["wall"]), _norm(row["tokens"])))
    def answered(p: dict[str, str]) -> bool:
        logged = p.get("logged", "").split(" | ", 1)
        cells = [(p["wall"], p["tokens"])] + ([(logged[0], logged[1])] if len(logged) == 2 else [])
        return any((_norm(p["check"]), _norm(w), _norm(k)) in keys for w, k in cells)

    return [p for p in passes if not answered(p)]


def row_for(p: dict[str, str]) -> str:
    """The row to add: what was measured filled in, the judgment cells left for the session (`?`)."""
    cells = [p.get("date", "?"), p["check"], p.get("subject") or "?", *("?" for _ in JUDGED), p["wall"], p["tokens"]]
    return "| " + " | ".join(_norm(c).replace("|", "/") for c in cells) + " |"


def _session_of(p: dict[str, str], root: Path) -> str:
    path = review_cost.transcript(p["agent"], root) if p.get("agent") else None
    return path.parts[-3] if path else ""


def filled_row(p: dict[str, str], where: str, root: Path = review_cost.DEFAULT_ROOT) -> str:
    """The row a headless page session's pass gets at the session's end, from the record alone: its verdict and first line
    from the agent's own reply, `nothing` where the reply is clean, and the acted-on cell naming where the session recorded
    what it applied or filed. Page sessions wrote no ledger rows - 124 passes of 343's and 368's sessions were owed at
    landing (2026-10-11) - and their own record of each check is the brief's checks file."""
    for d in ("../hooks/lib", "../measure"):
        sys.path.insert(0, str((Path(__file__).resolve().parent / d).resolve()))
    import event_log  # noqa: PLC0415
    import hm_checks  # noqa: PLC0415

    path = review_cost.transcript(p["agent"], root) if p.get("agent") else None
    reply = hm_checks._reply_of(str(path), "") if path else ""
    verdict = event_log.verdict_of(reply) or "see reply"
    first = next((ln.strip(" -*#") for ln in reply.splitlines() if ln.strip() and not ln.lstrip().startswith(("#", "```"))), "") or "-"
    bundle = re.search(r"/tmp/l7r-check/([^/\s]+)/", p.get("subject", ""))
    clean = verdict in ("clean", "PASS", "IN-STEP", "FAITHFUL", "INTRO-OK", "NO-INTRO-NEEDED")
    cells = [p.get("date", "?"), p["check"], bundle.group(1) if bundle else (p.get("subject") or "?")[:80], verdict, first[:110],
             "nothing" if clean else "judgment", "-", f"applied or filed as {where} records", p["wall"], p["tokens"]]
    return "| " + " | ".join(_norm(c).replace("|", "/") for c in cells) + " |"


#: A PLAN REVIEW RECORDS ITSELF (feature 385 T72, plan D92): its agent runs `make plan-verdict`, whose line its reply quotes
PLAN_REVIEW = "MODE 4: PLAN REVIEW"
#: ...the target's own line quoted, or the call the agent says it ran (T74's first review wrote "I recorded T74 as BLOCKED ... with
#: `make plan-verdict F=385 ...`" and quoted no line)
PLAN_RECORDED = re.compile(r"\b(?:CLEAR|BLOCKED|NOT-REVIEWABLE) recorded for\b|make plan-verdict\b[^\n]*\b(?:recorded|stored)\b|\b(?:recorded|stored)\b[^\n]*make plan-verdict\b|make plan-verdict F=\d+")
PLAN_WHERE = "the plan-verdict record (make plan-verdict)"


def in_the_record(p: dict[str, str], repo: Path) -> bool:
    """The pass's feature's `plan-review.json` holds a verdict for its task (or, for a block review, a block) dated the pass's day -
    the record itself, where the reply's words vary (T78's second review wrote only "I recorded it")."""
    m = re.search(r"feature (\d{3}-[\w-]+)", p.get("subject", ""))
    path = repo / "specs" / m.group(1) / "plan-review.json" if m else None
    if path is None or not path.is_file():
        return False
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return False
    task = re.search(r"\btask (T\d+[a-z]?)\b", p.get("subject", ""))
    if task:
        return (rec.get("tasks") or {}).get(task.group(1), {}).get("reviewed") == p.get("date")
    return any(isinstance(b, dict) and b.get("reviewed") == p.get("date") for b in (rec.get("blocks") or {}).values())


def plan_review_rows(owed: Sequence[dict[str, str]], root: Path = review_cost.DEFAULT_ROOT, repo: Path | None = None) -> list[str]:
    """The row of each owed plan review whose reply shows `make plan-verdict` recorded it (81 hand-written on 2026-10-18; the
    plan review asked that a pass that recorded nothing get no row naming a record)."""
    for d in ("../hooks/lib",):
        sys.path.insert(0, str((Path(__file__).resolve().parent / d).resolve()))
    import hm_checks  # noqa: PLC0415

    out = []
    for p in owed:
        if not p.get("subject", "").startswith(PLAN_REVIEW):
            continue
        path = review_cost.transcript(p["agent"], root) if p.get("agent") else None
        if (path and PLAN_RECORDED.search(hm_checks._reply_of(str(path), ""))) or (repo is not None and in_the_record(p, repo)):
            out.append(filled_row(p, PLAN_WHERE, root))
    return out


def default_log() -> Path:
    out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False).stdout.strip()
    return Path(out or ".git").resolve() / LOG


#: ONE FEATURE'S ROWS (feature 395's step-back, hour:395@1): `--write specs/395-.../checks.md` from the main session wrote rows for
#: every owed pass in the clone - 396's and 397's spec reviews among them - each claiming 395's checks file as where it was acted
#: on. A write that names a feature's specs directory now writes only the passes that feature's work can be traced to: a subject
#: naming the feature, one of its questions (the claims sheet, its implementation check, its briefs' SECTION= lines), or a
#: `key-<key>` bundle of a source those questions cite. The rest stay owed for the feature that ran them.
FEATURE_DIR = re.compile(r"specs/(\d{3})-")


def feature_questions(num: str, repo: Path) -> set[str]:
    """The question numbers feature `num` worked: its claims on the sheet and the numbers its own files name."""
    found: set[str] = set()
    sheet = Path(os.environ.get("L7R_CLAIMS_SHEET", "/diagram/.clones/RESEARCH-CLAIMS.md"))
    if sheet.is_file():
        for line in sheet.read_text(encoding="utf-8").splitlines():
            parts = [c.strip() for c in line.split("|")]
            if len(parts) > 2 and re.search(rf"\b{num}\b", parts[1]):
                found |= set(re.findall(r"(?<![\d.])(\d{4})(?!\d)", parts[2]))
    for d in repo.glob(f"specs/{num}-*"):
        for f in [d / "implementation-check.md", *d.glob("briefs/*.md")]:
            if f.is_file():
                text = f.read_text(encoding="utf-8")
                found |= set(re.findall(r"^- (\d{4}):", text, re.M)) | set(re.findall(r"SECTION=(\d{4})", text))
    return found


def _unit_prompt(p: dict[str, str], transcripts: Path) -> str:
    """A check-wave unit's own prompt: its logged subject is the workflow's framing ("[Workflow harness - computed task] ..."),
    so the prompt naming its bundle is read from the agent's transcript (its first user message)."""
    # a wave's agents are kept under `subagents/workflows/<run>/`, one level below where `review_cost.transcript` looks
    hits = sorted(transcripts.glob(f"*/*/subagents/**/agent-{p['agent']}.jsonl")) if p.get("agent") else []
    for d in _lines_of(hits[-1] if hits else None):
        content = (d.get("message") or {}).get("content") if d.get("type") == "user" else None
        if content:
            return content if isinstance(content, str) else " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return ""


def _lines_of(path: Path | None) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines()[:5] if path is not None and path.is_file() else []:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _active_feature(repo: Path) -> str:
    """The number of the feature `.specify/feature.json` names (the clone's active feature), or ''."""
    try:
        fd = json.loads((repo / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", "")
    except (OSError, ValueError):
        return ""
    m = FEATURE_DIR.search(str(fd) + "-")
    return m.group(1) if m else ""


def belongs(p: dict[str, str], num: str, questions: set[str], repo: Path, transcripts: Path = review_cost.DEFAULT_ROOT) -> bool:
    subject = p.get("subject", "")
    if subject.startswith("[Workflow harness"):
        subject = _unit_prompt(p, transcripts) or subject
    if re.search(rf"(?:feature |specs/|\b){num}-|feature {num}\b", subject):
        return True
    # A SUBJECT IS LOGGED CUT AT 100 CHARACTERS: a prompt naming its feature after that (feature 443's MODE 2, "MODE 2:
    # SPECIFICATION REVIEW. Clone: ... Request (the GM's words verba") stayed owed under every WRITE, so read the whole prompt
    if len(subject) >= 100 and re.search(rf"(?:feature |specs/|\b){num}-|feature {num}\b", _unit_prompt(p, transcripts)):
        return True
    if questions & set(re.findall(r"(?<![\d.])(\d{4})(?!\d)", subject)):
        return True
    # A CLAIMS ROUND'S PASS IS THE ACTIVE FEATURE'S (feature 405 T39, D13): its bundle is the clone's own (`make claims-bundle`,
    # `make claims-triage`) and its prompt names no feature - T14's landing refused once on three impl-drift passes for that
    if re.search(r"l7r-check/claims-(?:owed|triage)\b", subject) and _active_feature(repo) == num:
        return True
    key = re.search(r"/key-([\w-]+?)(?:-whole)?/", subject)
    return bool(key) and any(key.group(1) in f.read_text(encoding="utf-8") for q in questions for f in repo.glob(f"research/questions/{q}-*.html"))



def _usage(outcome: str) -> None:
    """The ledger write recorded as an automatic step (feature 406 T03, D162): landings and `make ledger-owed` write rows unasked."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: PLC0415

    usage_log.record(Path(__file__).resolve().parents[2], "ledger-owed-write", "step", outcome)

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--log", default="", help="the pass log (default: <git common dir>/check-passes.jsonl)")
    ap.add_argument("--ledger", default="dev/review-ledger.md")
    ap.add_argument("--refuse", action="store_true", help="exit 1 while a pass is unanswered")
    ap.add_argument("--transcripts", default=str(review_cost.DEFAULT_ROOT), help="the projects directory holding the agents' transcripts")
    ap.add_argument("--write", default="", help="append each owed pass's row, its acted-on cell naming this record")
    ap.add_argument("--session", default="", help="with --write: only the passes of this session's agents")
    ap.add_argument("--write-plan-reviews", action="store_true", help="append the row of each owed plan review that recorded its verdict (385 T72)")
    args = ap.parse_args(argv)
    ledger = Path(args.ledger)
    passes = distinct(settled(load_passes(Path(args.log) if args.log else default_log()), Path(args.transcripts), _kept_file()))
    owed = unanswered(passes, ledger.read_text(encoding="utf-8") if ledger.is_file() else "")
    if args.write_plan_reviews:
        rows = plan_review_rows(owed, Path(args.transcripts), ledger.resolve().parent.parent)
        if rows:
            with ledger.open("a", encoding="utf-8") as fh:
                fh.writelines(r + "\n" for r in rows)
        print(f"ledger-owed: {len(rows)} plan review row(s) written")
        _usage("changed" if rows else "unchanged")
        return 0
    if args.write:
        mine = [p for p in owed if not args.session or _session_of(p, Path(args.transcripts)) == args.session]
        feat = FEATURE_DIR.search(args.write)
        if feat and not args.session:  # a page session's own passes are its feature's already
            repo = ledger.resolve().parent.parent
            questions = feature_questions(feat.group(1), repo)
            mine = [p for p in mine if belongs(p, feat.group(1), questions, repo, Path(args.transcripts))]
        with ledger.open("a", encoding="utf-8") as fh:
            fh.writelines(filled_row(p, args.write, Path(args.transcripts)) + "\n" for p in mine)
        left = len(owed) - len(mine)
        _usage("changed" if mine else "unchanged")
        print(f"ledger-owed: {len(mine)} row(s) written for {args.session or (f'feature {feat.group(1)}' if feat else 'every session')}"
              + (f"; {left} pass(es) not traced to it stay owed for the feature that ran them" if left else ""))
        return 0
    if not owed:
        return 0
    stream = sys.stderr if args.refuse else sys.stdout
    print(f"ledger-owed: {len(owed)} check pass(es) have no row in dev/review-ledger.md's measured table - write them from each agent's reply: "
          'make ledger-owed WRITE="<where you recorded what you did>" (feature 385 FR-019); or add each by hand, filling the ?s:', file=stream)
    for p in owed:
        print("  " + row_for(p), file=stream)
    print(
        "  (a row answers a pass by its check and its cost cells, which are the pass's own `make review-cost` - feature 371; the push refuses until each has its row, or LEDGER_ROWS_OK=\"<reason>\")",
        file=stream,
    )
    return 1 if args.refuse else 0


if __name__ == "__main__":
    sys.exit(main())
