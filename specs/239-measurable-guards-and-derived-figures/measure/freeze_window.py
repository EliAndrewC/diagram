#!/usr/bin/env python3
"""Freeze the Bash commands of a recent window into a corpus the bench can replay.

    python3 specs/239-*/measure/freeze_window.py [DAYS] [--out scripts/fixtures/<name>.json]

Every command in the last DAYS days of transcripts that carries a British spelling or a forbidden
dash, deduplicated, written with the date it was taken. FR-004: the window is frozen because a
rolling one makes two runs disagree for reasons that have nothing to do with the code, which is how
feature 236's figures drifted between review rounds.

THE PREFILTER WRITES ITS DASHES BY CODEPOINT. Written literally they were corrected to hyphens by the
very hook being measured, as this file was saved, and the corpus then matched any command containing
a spaced hyphen - an order of magnitude too many, none of them relevant.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
HOOK = ROOT / "scripts" / "house-style-hooks.sh"
DASHES = chr(0x2014) + chr(0x2013)


def word_pattern() -> re.Pattern[str]:
    """The hook's own table, read from the hook - never a copy, which the hook would correct."""
    table = re.search(r"BRIT = \((.*?)\)\n", HOOK.read_text(), re.S).group(1)
    return re.compile(r"\b(" + "|".join(re.findall(r'"(\w+)"', table)) + r")\b|[" + DASHES + "]", re.I)


def commands(days: float) -> list[str]:
    cutoff, seen, out = time.time() - days * 86400, set(), []
    pattern = word_pattern()
    for path in (pathlib.Path.home() / ".claude" / "projects").glob("*/**/*.jsonl"):
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
                        if cmd and cmd not in seen and pattern.search(cmd):
                            seen.add(cmd)
                            out.append(cmd)
    return out


def main(argv: list[str]) -> int:
    days = float(next((a for a in argv if a.replace(".", "").isdigit()), 14))
    today = datetime.date.today().isoformat()
    out = pathlib.Path(argv[argv.index("--out") + 1]) if "--out" in argv else \
        ROOT / "scripts" / "fixtures" / f"command-window-{today}.json"
    cmds = commands(days)
    out.write_text(json.dumps({
        "taken": today,
        "days": days,
        "built_by": "python3 specs/239-measurable-guards-and-derived-figures/measure/freeze_window.py",
        "what": "every unique Bash command in the window carrying a British spelling or a forbidden dash",
        "commands": cmds,
    }, indent=1) + "\n")
    print(f"{len(cmds)} commands -> {out.relative_to(ROOT)} ({out.stat().st_size/1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
