#!/usr/bin/env python3
"""What each subagent check has cost, read from the session transcripts (feature 251, FR-001).

WHY THIS EXISTS. The GM asked on 2026-09-19 whether the subagent checks could cost fewer tokens
"without a loss of quality with different levels of models involved", and the first step the
proposal named was to measure: which agents the tokens actually go to, before tiering any of them.
This is that measurement, kept as a target so a later session can take it again and compare per-run
means against the baseline in `specs/251-tiered-subagent-checks/measurements.json`.

WHERE THE NUMBERS COME FROM. Claude Code writes one transcript per subagent run at
`~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`, with `agent-<id>.meta.json`
beside it naming the agent type. Every assistant record carries the API's `usage` and the `model`
that answered.

THE ONE TRAP (research R2). A transcript holds one record PER CONTENT BLOCK of an assistant message,
each repeating the message's id and its usage AS IT STOOD when the block was written, so
`output_tokens` grows across the records of one message. Usage is therefore folded per message id as
the per-field MAXIMUM. Taking the first record undercounts output by an order of magnitude; summing
every record counts a message once per block.

The dispatch's own `model` field (in the meta) is an OVERRIDE and is absent on most runs, so the
model a run used is read from the assistant records, never from the meta.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter

FIELDS = ("fresh", "cached", "output", "thinking")
#: agent types with no file under `.claude/agents/` - a dispatch of one inherits the session's model
#: unless it names one, which is what the ad-hoc block reports (spec FR-010).
BUILTIN = ("general-purpose", "claude", "Explore", "Plan", "fork", "claude-code-guide", "statusline-setup")


def usage_of(record: dict) -> tuple[str, str, dict[str, int]] | None:
    """(message id, model, usage fields) of one assistant record, or None for any other record."""
    if record.get("type") != "assistant":
        return None
    msg = record.get("message") or {}
    use = msg.get("usage")
    if not isinstance(use, dict) or not msg.get("id"):
        return None
    details = use.get("output_tokens_details") or {}
    return (
        str(msg["id"]),
        str(msg.get("model") or "unknown"),
        {
            "fresh": int(use.get("input_tokens") or 0) + int(use.get("cache_creation_input_tokens") or 0),
            "cached": int(use.get("cache_read_input_tokens") or 0),
            "output": int(use.get("output_tokens") or 0),
            "thinking": int(details.get("thinking_tokens") or 0),
        },
    )


def fold_usage(records: list[dict]) -> dict:
    """One run's totals: usage folded per message id as the per-field maximum (R2), then summed."""
    per_msg: dict[str, dict[str, int]] = {}
    models: Counter[str] = Counter()
    first_ts = ""
    for rec in records:
        first_ts = first_ts or str(rec.get("timestamp") or "")
        got = usage_of(rec)
        if got is None:
            continue
        mid, model, use = got
        if mid not in per_msg:
            per_msg[mid] = dict.fromkeys(FIELDS, 0)
            models[model] += 1
        for f in FIELDS:
            per_msg[mid][f] = max(per_msg[mid][f], use[f])
    out: dict = {f: sum(m[f] for m in per_msg.values()) for f in FIELDS}
    out["turns"] = len(per_msg)
    out["model"] = models.most_common(1)[0][0] if models else "none"
    out["started"] = first_ts
    return out


def read_run(transcript: pathlib.Path) -> tuple[dict, dict]:
    """(meta, folded usage) of one subagent transcript; a line that is not JSON is skipped."""
    meta_path = transcript.with_suffix("").with_suffix(".meta.json")
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meta = {}
    records = []
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    return meta, fold_usage(records)


def transcripts(root: pathlib.Path) -> list[pathlib.Path]:
    """Every subagent transcript of this repository's sessions: the mirror's project and its clones'."""
    found: list[pathlib.Path] = []
    for project in sorted(root.iterdir()) if root.is_dir() else []:
        if project.name == "-diagram" or project.name.startswith("-diagram-"):
            found.extend(sorted(project.glob("*/subagents/agent-*.jsonl")))
    return found


def rows(runs: list[tuple[dict, dict]], since: str = "") -> tuple[list[dict], list[dict]]:
    """(one row per agent type, one row per ad-hoc type) from `(meta, usage)` pairs.

    A run with no assistant turn (an agent that never answered) is counted as a run and adds nothing.
    `since` is an ISO date prefix compared against the run's first timestamp.
    """
    by_type: dict[str, dict] = {}
    adhoc: dict[str, dict] = {}
    for meta, use in runs:
        if since and use["started"][: len(since)] < since:
            continue
        kind = str(meta.get("agentType") or "unknown")
        row = by_type.setdefault(kind, {"agent": kind, "runs": 0, "turns": 0, **dict.fromkeys(FIELDS, 0), "models": Counter()})
        row["runs"] += 1
        row["turns"] += use["turns"]
        for f in FIELDS:
            row[f] += use[f]
        row["models"][use["model"]] += 1
        if kind in BUILTIN:
            ad = adhoc.setdefault(kind, {"agent": kind, "runs": 0, "no_model": 0, "inherited": Counter()})
            ad["runs"] += 1
            if not meta.get("model") or str(meta.get("model")).lower() == "inherit":
                ad["no_model"] += 1
                ad["inherited"][use["model"]] += 1
    ordered = sorted(by_type.values(), key=lambda r: -(r["fresh"] + r["cached"]))
    for row in ordered:
        row["models"] = dict(row["models"].most_common())
    ad_rows = sorted(adhoc.values(), key=lambda r: -r["runs"])
    for ad in ad_rows:
        ad["inherited"] = dict(ad["inherited"].most_common())
    return ordered, ad_rows


def _n(value: float) -> str:
    return f"{int(round(value)):,}"


def render(table: list[dict], adhoc: list[dict]) -> str:
    """The census as text: totals per agent type, per-run means, the models used, the ad-hoc block."""
    head = f"{'agent':<22}{'runs':>6}{'turns':>8}{'fresh in':>14}{'cached in':>16}{'output':>12}{'thinking':>11}{'in/run':>12}{'out/run':>10}  models"
    lines = [head, "-" * len(head)]
    for r in table:
        runs = max(r["runs"], 1)
        models = ", ".join(f"{m} x{c}" for m, c in r["models"].items())
        lines.append(
            f"{r['agent']:<22}{r['runs']:>6}{_n(r['turns']):>8}{_n(r['fresh']):>14}{_n(r['cached']):>16}{_n(r['output']):>12}"
            f"{_n(r['thinking']):>11}{_n((r['fresh'] + r['cached']) / runs):>12}{_n(r['output'] / runs):>10}  {models}"
        )
    if adhoc:
        lines += ["", "ad-hoc agents (no file pins their model) - runs dispatched with no model, and what they ran on:"]
        for ad in adhoc:
            ran = ", ".join(f"{m} x{c}" for m, c in ad["inherited"].items()) or "-"
            lines.append(f"  {ad['agent']:<20}{ad['runs']:>5} runs, {ad['no_model']:>4} with no model: {ran}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(pathlib.Path.home() / ".claude" / "projects"))
    ap.add_argument("--since", default="", help="YYYY-MM-DD: only runs that started on or after it")
    ap.add_argument("--json", default="", help="also write the rows to this file")
    args = ap.parse_args(argv)
    runs = [read_run(t) for t in transcripts(pathlib.Path(args.root))]
    table, adhoc = rows(runs, args.since)
    print(render(table, adhoc))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({"since": args.since, "agents": table, "adhoc": adhoc}, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
