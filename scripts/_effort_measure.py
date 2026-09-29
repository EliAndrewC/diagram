#!/usr/bin/env python3
"""Measure one run of the effort experiment (feature 293, spec FR-006/FR-007, contracts/cli.md `make effort-measure`).

WHERE THE NUMBERS COME FROM (research R2-R4). Every top-level transcript of the run's clone
(`~/.claude/projects/<mangled clone>/<sid>.jsonl` - task I's one session, task R's two page sessions) and every subagent
transcript under them; the host guard log (`~/.claude/guard-log/*.json`, one file per firing, tagged with session and cwd);
the run clone's git log since the start commit; each session's `result.json` and `stderr.txt`.

TOKENS are folded per message id as the per-field MAXIMUM, the rule `_agent_census.py` records (its research R2: a transcript
repeats a message's usage on every content block, growing). The census folds into fresh / cached / output; the spec wants the
four API fields apart, so the same rule is applied to the raw fields here, and a test holds the two folds to the same totals.

THE HEURISTICS ARE LISTED, NOT HIDDEN (R4): a failed make run and a fix commit are matched by pattern, and a verdict's pass or
not-pass by its words, so the measurement keeps every matched line for the report's reader to check.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time
from collections import Counter

FEATURE = "293-effort-level-experiment"
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
MAKE_RUN = re.compile(r"\bmake\s+(quick|done|test-file|test-full)\b")
MAKE_FAILED = re.compile(r"\b(\d+ failed|FAILED|Error \d+|error:)", re.I)
FIX_COMMIT = re.compile(r"\b(fix(es|ed)?|revert(s|ed)?|round-\d+ changes)\b", re.I)
NOT_PASS = re.compile(r"\b(CHANGES REQUIRED|BLOCKED|NOT[- ]REVIEWABLE|NOT-FOUND|CONTRADICTED|DRIFTED|FAIL(ED|S)?|REJECT(ED)?)\b")
PASS = re.compile(r"\b(PASS(ED)?|FAITHFUL|CLEAR|CONFIRMED|IN-STEP|READ|KEEP)\b")
JUDGING = re.compile(r"\b(review|check|judge|verdict|verify|audit|grade|compare)\w*", re.I)


def fold(records: list[dict]) -> dict[str, int]:
    """The four usage fields summed over messages, each message's usage its per-field maximum across its records."""
    per: dict[str, dict[str, int]] = {}
    for r in records:
        msg = r.get("message") or {}
        use = msg.get("usage") if r.get("type") == "assistant" else None
        if not isinstance(use, dict) or not msg.get("id"):
            continue
        cur = per.setdefault(str(msg["id"]), dict.fromkeys(FIELDS, 0))
        for f in FIELDS:
            cur[f] = max(cur[f], int(use.get(f) or 0))
    return {f: sum(m[f] for m in per.values()) for f in FIELDS}


def add(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {f: a.get(f, 0) + b.get(f, 0) for f in FIELDS}


def records_of(path: pathlib.Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def tool_uses(records: list[dict]) -> list[dict]:
    """Every tool_use block, once per block id."""
    seen: dict[str, dict] = {}
    for r in records:
        if r.get("type") != "assistant":
            continue
        for b in (r.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") not in seen:
                seen[b["id"]] = b
    return list(seen.values())


def tool_results(records: list[dict]) -> dict[str, str]:
    out = {}
    for r in records:
        content = (r.get("message") or {}).get("content")
        for b in content if isinstance(content, list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                c = b.get("content")
                out[str(b.get("tool_use_id"))] = c if isinstance(c, str) else json.dumps(c)
    return out


def efforts(records: list[dict]) -> Counter[str]:
    """The effort each assistant record ran at - Claude Code writes it on every record (research R1, P0 of 2026-09-29) -
    counted per message, so a run's claimed arm and the checkers' pinned tiers are MEASURED, not trusted."""
    seen: dict[str, str] = {}
    for r in records:
        if r.get("type") == "assistant":
            seen[str((r.get("message") or {}).get("id") or r.get("uuid"))] = str(r.get("effort") or "unrecorded")
    return Counter(seen.values())


def last_text(records: list[dict]) -> str:
    for r in reversed(records):
        if r.get("type") == "assistant":
            for b in (r.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    return b["text"]
    return ""


def verdict_of(text: str) -> str:
    """The verdict word a check agent's reply opens with, judged on its first 400 characters."""
    head = text[:400]
    if NOT_PASS.search(head):
        return "not-pass"
    return "pass" if PASS.search(head) else "unclear"


def times(records: list[dict]) -> list[str]:
    return [str(r["timestamp"]) for r in records if r.get("timestamp")]


def parse(ts: str) -> float:
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def failed_make_runs(records: list[dict]) -> list[str]:
    """Each make quick/done/test-file whose output reports a failure, before the last run of that target that did not."""
    results = tool_results(records)
    runs = []
    for b in tool_uses(records):
        cmd = str((b.get("input") or {}).get("command") or "")
        m = MAKE_RUN.search(cmd) if b.get("name") == "Bash" else None
        if m:
            out = results.get(str(b.get("id")), "")
            runs.append((m.group(1), bool(MAKE_FAILED.search(out)), cmd[:160]))
    last_green = {t: i for i, (t, bad, _) in enumerate(runs) if not bad}
    return [c for i, (t, bad, c) in enumerate(runs) if bad and i < last_green.get(t, len(runs))]


def subagents(session_dir: pathlib.Path) -> list[tuple[dict, list[dict]]]:
    out = []
    for t in sorted(session_dir.glob("subagents/agent-*.jsonl")):
        meta_path = t.with_suffix("").with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
        out.append((meta, records_of(t)))
    return out


def guard_firings(log_dir: pathlib.Path, sids: set[str], clone: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for p in sorted(log_dir.glob("*.json")) if log_dir.is_dir() else []:
        try:
            e = json.loads(p.read_text())
        except ValueError:
            continue
        if e.get("session") in sids or str(e.get("cwd") or "").startswith(clone):
            c[f"{e.get('guard')}:{e.get('event')}:{e.get('rule')}"] += 1
    return c


def void_reason(log: pathlib.Path) -> str:
    """Why a session's run is void (the environment killed it), or ''."""
    err = (log / "stderr.txt").read_text(errors="replace") if (log / "stderr.txt").is_file() else ""
    res = (log / "result.json").read_text(errors="replace") if (log / "result.json").is_file() else ""
    if "Killed" in err or "exit 137" in err or "137" in res[:40]:
        return "killed by the memory limit (exit 137)"
    return ""


def measure(run: dict, projects: pathlib.Path, guard_log: pathlib.Path, defined: set[str], git_log: list[str]) -> dict:
    project = projects / run["clone"].replace("/", "-").replace(".", "-")
    main_t = sorted(project.glob("*.jsonl")) if project.is_dir() else []
    main_tok = dict.fromkeys(FIELDS, 0)
    sub_tok = dict.fromkeys(FIELDS, 0)
    tools: Counter[str] = Counter()
    sub_tools: Counter[str] = Counter()
    dispatches: Counter[str] = Counter()
    adhoc: list[dict] = []
    verdicts: dict[str, Counter[str]] = {}
    failed: list[str] = []
    stamps: list[str] = []
    finals: list[str] = []
    main_effort: Counter[str] = Counter()
    sub_effort: dict[str, Counter[str]] = {}
    for t in main_t:
        recs = records_of(t)
        main_tok = add(main_tok, fold(recs))
        stamps += times(recs)
        failed += failed_make_runs(recs)
        finals.append(last_text(recs))
        main_effort += efforts(recs)
        for b in tool_uses(recs):
            tools[b["name"]] += 1
            if b["name"] in ("Agent", "Task"):
                inp = b.get("input") or {}
                kind = str(inp.get("subagent_type") or "general-purpose")
                dispatches[f"{kind}@{inp.get('model') or 'inherit'}"] += 1
                if kind not in defined:
                    desc = str(inp.get("description") or "")
                    adhoc.append({"type": kind, "model": inp.get("model"), "description": desc,
                                  "judging": inp.get("model") == "opus" or bool(JUDGING.search(desc))})
        for meta, recs2 in subagents(t.with_suffix("")):
            sub_tok = add(sub_tok, fold(recs2))
            stamps += times(recs2)
            for b in tool_uses(recs2):
                sub_tools[b["name"]] += 1
            kind = str(meta.get("agentType") or "unknown")
            sub_effort.setdefault(kind, Counter()).update(efforts(recs2))
            verdicts.setdefault(kind, Counter())[verdict_of(last_text(recs2))] += 1
    stamps.sort()
    pauses = sum(parse(b) - parse(a) for a, b in run.get("pauses") or [])
    fixes = [s for s in git_log if FIX_COMMIT.search(s)]
    sids = {t.stem for t in main_t}
    return {
        "run_id": run["run_id"],
        "tokens": {"main": main_tok, "subagents": sub_tok, "total": add(main_tok, sub_tok)},
        "wall_clock_s": round(parse(stamps[-1]) - parse(stamps[0]) - pauses) if stamps else 0,
        "sessions": sorted(sids),
        "tool_calls": {"main": dict(tools), "subagents": dict(sub_tools)},
        "dispatches": dict(dispatches),
        "effort": {"main": dict(main_effort), "subagents": {k: dict(v) for k, v in sub_effort.items()}},
        "adhoc_dispatches": adhoc,
        "adhoc_judging_at_session_effort": sum(1 for a in adhoc if a["judging"]),
        "rework": {
            "guard": dict(guard_firings(guard_log, sids, run["clone"])),
            "verdicts": {k: dict(v) for k, v in verdicts.items()},
            "failed_make_runs": failed,
            "fix_commits": fixes,
            "escalations": verdicts.get("escalation-check", Counter()).total()
            + sum(1 for f in finals if f.rstrip().endswith("?")),
        },
    }


def release_claim(claims: pathlib.Path, run_id: str, now: float) -> str:
    """R6 D5: after a task R run, the line that ends its claim, so the next run finds the question free."""
    line = f"293 | run {run_id} ended - claim released | {iso(now)[:10]}"  # no word of the experiment (FR-004): a later run reads it
    with claims.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line


def iso(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_logs(run: dict) -> list[pathlib.Path]:
    if run["task"] == "I":
        return [pathlib.Path(s["log"]) for s in run["sessions"]]
    return sorted(p for p in (pathlib.Path(run["clone"]) / ".git" / "page-sessions").glob("*") if p.is_dir())


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="effort-measure")
    ap.add_argument("--run", required=True)
    ap.add_argument("--projects", default=str(pathlib.Path.home() / ".claude" / "projects"))
    ap.add_argument("--guard-log", default=str(pathlib.Path.home() / ".claude" / "guard-log"))
    ap.add_argument("--claims", default="/diagram/.clones/RESEARCH-CLAIMS.md")
    ap.add_argument("--void", default="", help="mark the run void for an environment reason the logs cannot see (with the reason)")
    args = ap.parse_args(argv)
    repo = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                                       check=True).stdout.strip())
    fdir = repo / "specs" / FEATURE
    rec_path = fdir / "runs" / f"{args.run}.json"
    run = json.loads(rec_path.read_text())
    logs = session_logs(run)
    expected = 1 if run["task"] == "I" else 2
    if len(logs) < expected or not all((p / "result.json").is_file() and (p / "result.json").stat().st_size for p in logs):
        voids = [v for p in logs if (v := void_reason(p))]
        if not voids:
            print(f"effort-measure: {args.run} is still running ({len(logs)} of {expected} sessions started) - measure it on its notification",
                  file=sys.stderr)
            return 2
    clone = pathlib.Path(run["clone"])
    defined = {p.stem for p in (clone / ".claude" / "agents").glob("*.md")} | {"adhoc-judge"}
    git_log = subprocess.run(["git", "-C", str(clone), "log", "--format=%s", f"{run['start_commit']}..HEAD"],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    m = measure(run, pathlib.Path(args.projects), pathlib.Path(args.guard_log), defined, git_log)
    reasons = [v for p in logs if (v := void_reason(p))] + ([f"voided by the session: {args.void}"] if args.void else [])
    now = time.time()
    run["status"] = "void" if reasons else "valid"
    run["void_reason"] = "; ".join(reasons)
    run["ended"] = run.get("ended") or iso(now)
    if run["task"] == "R" and "claims_release_line" not in run["shared_state"]:
        run["shared_state"]["claims_release_line"] = release_claim(pathlib.Path(args.claims), args.run, now)
    sources = pathlib.Path(run["env"]["L7R_SOURCES_HOME"]) / "sources-consulted.jsonl"
    snap = pathlib.Path(json.loads((fdir / "experiment.json").read_text())["sources_snapshot"]) / "sources-consulted.jsonl"
    base = len(snap.read_text().splitlines()) if snap.is_file() else 0
    run["shared_state"]["ledger_lines_appended"] = len(sources.read_text().splitlines()) - base if sources.is_file() else 0
    new_files = subprocess.run(["git", "-C", str(clone), "diff", "--name-only", "--diff-filter=A", run["start_commit"], "HEAD"],
                               capture_output=True, text=True, check=True).stdout.splitlines()
    run["shared_state"]["prefixes_reserved"] = [f for f in new_files if "/research/sources/" in "/" + f or "/glossary/" in "/" + f]
    rec_path.write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
    out = fdir / "measurements" / f"{args.run}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(m, indent=1) + "\n", encoding="utf-8")
    t = m["tokens"]["total"]
    print(f"effort-measure: {args.run} {run['status']}{' - ' + run['void_reason'] if reasons else ''}")
    print(f"  tokens in {t['input_tokens']:,} out {t['output_tokens']:,} cache-read {t['cache_read_input_tokens']:,} "
          f"cache-write {t['cache_creation_input_tokens']:,}  |  wall {m['wall_clock_s']} s  |  "
          f"tools {sum(m['tool_calls']['main'].values())}+{sum(m['tool_calls']['subagents'].values())}")
    rw = m["rework"]
    print(f"  rework: guard {sum(rw['guard'].values())}, failed make {len(rw['failed_make_runs'])}, fix commits "
          f"{len(rw['fix_commits'])}, escalations {rw['escalations']}; ad-hoc judging at session effort "
          f"{m['adhoc_judging_at_session_effort']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
