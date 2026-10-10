#!/usr/bin/env python3
"""The decider for `archive-first-hooks.sh`: does the archive already hold the page a WebFetch is about to fetch?
(Feature 376 FR-006, plan D6.)

WHY (the GM, 2026-10-10: *"search our existing research findings prior to going out and doing new research"*; 376's
research.md R2): since the source archive landed, agents fetched 960 pages the archive already held - quote-check 773,
source-applicability 68, source-reader 91, and ad-hoc agents 14, which nothing told the archive existed.

THE RULE: the FIRST WebFetch of a URL the archive holds, by one actor (a session or one of its agents), is refused with
the archived text's path; the same URL fetched AGAIN by the same actor passes - the actor has seen the archived copy
and wants the live page (is it still public? has it changed?). The actor's refusals are kept in a small state file.

    hm_archive_first.py judge < <hook payload>   -> the archived text's path and capture date (nothing = pass)
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import sys

STATE = pathlib.Path(os.environ.get("L7R_ARCHIVE_FIRST_STATE", "/tmp/l7r-archive-first"))


def _scripts_record() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2] / "record"


def repo_root(start: pathlib.Path) -> pathlib.Path:
    root = start.resolve()
    while not (root / ".git").exists() and root != root.parent:
        root = root.parent
    return root


def held(url: str, root: pathlib.Path) -> tuple[str, str] | None:
    """(the archived text's path, its capture date) when the archive holds readable text of `url`, else None."""
    sys.path.insert(0, str(_scripts_record()))
    import sources  # noqa: PLC0415 - scripts/record/sources.py, the one reader of the archive's text (plan D4)

    mirror = root.parent.parent if root.parent.name == ".clones" else root
    store = pathlib.Path(os.environ.get("L7R_ARCHIVE_STORE", mirror / ".specify" / "source-archive"))
    uid = hashlib.sha256(sources._cited(url).encode("utf-8")).hexdigest()[:12]
    try:
        row = json.loads((root / "research" / "archive" / uid[:2] / f"{uid}.json").read_text(encoding="utf-8"))
        text = store / row["path"] / "text.txt"
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return (str(text), str(row.get("captured", ""))[:10]) if text.is_file() and text.stat().st_size > 0 else None


def seen_before(actor: str, url: str) -> bool:
    """Has this actor been refused this URL already (so this fetch is the deliberate second)? Records it if not."""
    STATE.mkdir(parents=True, exist_ok=True)
    path = STATE / (re.sub(r"[^\w.-]", "_", actor)[:120] + ".txt")
    known = set(path.read_text().splitlines()) if path.is_file() else set()
    if url in known:
        return True
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(url + "\n")
    return False


def judge(payload: dict, cwd: pathlib.Path) -> str:
    if payload.get("tool_name") != "WebFetch":
        return ""
    url = str((payload.get("tool_input") or {}).get("url") or "")
    if not url.startswith(("http://", "https://")):
        return ""
    got = held(url, repo_root(cwd))
    if got is None:
        return ""
    actor = f"{payload.get('session_id', '')}.{payload.get('agent_id', '') or 'main'}"
    return "" if seen_before(actor, url) else f"{got[0]}\t{got[1]}"


def main(argv: list[str]) -> int:
    if argv[:1] != ["judge"]:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    out = judge(payload, pathlib.Path(os.environ.get("AF_CWD") or os.getcwd()))
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
