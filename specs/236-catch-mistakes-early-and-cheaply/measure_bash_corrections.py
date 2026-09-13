#!/usr/bin/env python3
"""What the house-style hook would REWRITE if a Bash payload were corrected rather than warned on.

The record behind spec D2's amendment (the GM 2026-09-12: warn on the sed shape, correct every other
shape). A Bash command is not an Edit: correcting a word the command only NAMES - a file path, a search
pattern the segment dropper does not recognize - breaks a command that was correct. So before the hook
corrects anything, every real Bash command in the recent transcripts that the hook warns on today is
replayed through the hook and classified by the shape the word stands in.

    python3 specs/236-catch-mistakes-early-and-cheaply/measure_bash_corrections.py [DAYS]

Reads `~/.claude/projects/*/` main and subagent transcripts modified in the last DAYS days (default 14).
Prints one line per warned command, then the counts per class.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time

HOOK = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "house-style-hooks.sh"
# The word list is READ from the hook, never typed here: the hook corrects a file as it is written, and
# the first draft of this script had its own table turned American on the way in - which is exactly
# the hazard this measurement prices. The dashes are written by codepoint for the same reason.
BRIT = re.findall(r'"(\w+)"', re.search(r"BRIT = \((.*?)\)\n", HOOK.read_text(), re.S).group(1))
WORD = re.compile(r"\b(" + "|".join(BRIT) + r")\b| - | - ", re.I)


def commands(days: float):
    cutoff = time.time() - days * 86400
    root = pathlib.Path.home() / ".claude" / "projects"
    for path in root.glob("*/**/*.jsonl"):
        try:
            if path.stat().st_mtime < cutoff:
                continue
            fh = path.open(errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"Bash"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                for c in (rec.get("message") or {}).get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Bash":
                        cmd = (c.get("input") or {}).get("command") or ""
                        if WORD.search(cmd):
                            yield cmd


def verdict(cmd: str) -> str:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    env = dict(os.environ, GUARD_LOG_DIR="/tmp/claude-1000/measure-guard-log")
    p = subprocess.run([str(HOOK), "pretool"], input=payload, capture_output=True, text=True, env=env)
    out = p.stdout.strip()
    if not out.startswith("{"):
        return "quiet"
    spoke = json.loads(out)["hookSpecificOutput"]
    return "rewritten" if spoke.get("updatedInput") else "warned"


def shapes(cmd: str) -> list[str]:
    """Where each British word stands in the command - the classes the amendment has to price."""
    out = []
    for seg in re.split(r";|\|\||\||&&|\n", cmd):
        for m in WORD.finditer(seg):
            tok = next((t for t in re.split(r"[\s'\"=(),]+", seg) if m.group(0) in t), m.group(0))
            if re.match(r"\s*(sudo\s+)?(xargs\s+(-\S+\s+)*)?sed\b", seg) or re.search(r"\bsed\s+-", seg):
                out.append("sed")
            elif "/" in tok or re.search(r"[\w-]\.(md|py|sh|html|json|txt|toml|js|css)\b", tok):
                out.append("path:" + tok[:60])
            elif re.search(r"\b(re\.(sub|search|match|findall|compile)|replace|awk|perl)\b", seg):
                out.append("pattern")
            else:
                out.append("prose")
    return out


def main() -> int:
    days = float(sys.argv[1]) if len(sys.argv) > 1 else 14
    seen, counts = set(), {}
    for cmd in commands(days):
        if cmd in seen:
            continue
        seen.add(cmd)
        v = verdict(cmd)
        if v == "quiet":
            counts["quiet (exempt or dropped)"] = counts.get("quiet (exempt or dropped)", 0) + 1
            continue
        kinds = sorted(set(k.split(":")[0] for k in shapes(cmd)))
        key = "+".join(kinds) or "dash"
        counts[key] = counts.get(key, 0) + 1
        head = cmd.strip().splitlines()[0][:110]
        print(f"[{key}] {shapes(cmd)[:3]} :: {head}")
    print("\nunique commands carrying a word, by class:")
    for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:5d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
