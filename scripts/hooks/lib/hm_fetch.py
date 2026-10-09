#!/usr/bin/env python3
"""The decision behind `blocked-fetch-hooks.sh` (feature 312, FR-002, FR-017, FR-018): refuse a fetch of a blocked domain,
record every other fetch as an attempt, and say what was tried before.

Reads the hook payload on stdin and prints one JSON object:

    {"decision": "block", "message": "..."}     a WebFetch, or a Bash fetch command, aimed at a blocked domain
    {"decision": "pass", "context": "..."}      anything else; `context` (maybe empty) is the earlier attempts and the
                                                filter's verdict for each URL a fetch names

WHAT IS A FETCH. A WebFetch (its `url`); a Bash command that INVOKES a fetch program - `curl`, `wget`, `lynx`, `w3m`,
`xh`, httpie's `http`/`https`, `python3 -m urllib` - or a make target that fetches (`source-pages`, `archive`,
`archive-sources`, `reserve`, `source-outcome`, `quote-verbatim`), with a URL in it. A MENTION is not a fetch: a grep for
the word, an echo, a commit message pass (the guard doctrine: match invocations, not mentions).

THE ATTEMPT. A WebFetch or a Bash fetch program writes one attempt per URL to the clone's attempts log - what was sought
is the WebFetch's prompt, or the command; a make route records its own. Nothing is written from the mirror (`/diagram`
is never a workspace), and a failure to write never blocks the fetch.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path[1:1] = [str((pathlib.Path(__file__).resolve().parent / _d).resolve()) for _d in ('../../record',)]  # the moved scripts it imports (2026-10-08)
import attempts as at  # noqa: E402
import sources as src  # noqa: E402

FETCHER = re.compile(r"(?:^|[\s;&|(`$])(?:curl|wget|lynx|w3m|xh|https?)\s|python3?\s+-m\s+urllib")
MAKE_FETCH = re.compile(r"(?:^|[\s;&|(])make\s+(?:-[Cs]\s*\S+\s+)*(?:source-pages|archive|archive-sources|reserve|source-outcome|quote-verbatim)\b")
URL = re.compile(r"(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s'\"<>)]*)?", re.I)
HTTP_URL = re.compile(r"https?://[^\s'\"<>)]+", re.I)
SOUGHT_CHARS = 300


def clone_of(cwd: str) -> pathlib.Path | None:
    """The session clone a command runs in, or None for the mirror and anything outside a clone."""
    p = pathlib.Path(cwd or ".").resolve()
    for d in (p, *p.parents):
        if d.parent.name == ".clones" and (d / ".git").exists():
            return d
    return None


def archived(root: pathlib.Path, url: str) -> bool:
    """Whether the source archive holds a row for `url` (a manifest file under the record, by its id)."""
    import hashlib  # noqa: PLC0415
    import html  # noqa: PLC0415

    clean = html.unescape(url).split("#")[0]  # `record/archive.py:clean`, restated: the hook stays off the engine's imports
    while clean.endswith((".", ",", ";", ":")) or (clean.endswith(")") and clean.count(")") > clean.count("(")):
        clean = clean[:-1]
    uid = hashlib.sha256(clean.encode("utf-8")).hexdigest()[:12]
    return (root / at.RESEARCH / "archive" / uid[:2] / f"{uid}.json").is_file()


def decide(payload: dict) -> dict:
    tool, inp = payload.get("tool_name", ""), payload.get("tool_input") or {}
    blocked = src._blocked()
    if tool == "WebFetch":
        urls, sought, record = [inp.get("url", "")], (inp.get("prompt") or "").strip(), True
    elif tool == "Bash":
        cmd = inp.get("command", "")
        fetcher, maker = bool(FETCHER.search(cmd)), bool(MAKE_FETCH.search(cmd))
        if not (fetcher or maker):
            return {"decision": "pass", "context": ""}
        urls = URL.findall(cmd) if maker else HTTP_URL.findall(cmd) or URL.findall(cmd)
        sought, record = cmd.strip(), fetcher and not maker
    else:
        return {"decision": "pass", "context": ""}
    for u in urls:
        rule = blocked.blocked(u)
        if rule:
            return {"decision": "block", "message": blocked.refusal(u, rule, f"this {tool}")}
    urls = [u for u in urls if u.startswith("http")] if tool == "Bash" else [u for u in urls if u]
    root = clone_of(payload.get("cwd", ""))
    if root is None or not urls:
        return {"decision": "pass", "context": ""}
    lines = []
    for u in urls:
        report = at.report(root, url=u)
        if len(report) > 1:
            lines += report
        if archived(root, u):  # the record's rule: look in the archive before the web (feature 309; FR-005)
            lines.append(f"archive: a copy of {u} is archived - read it with `make archive-find URL='{u}'` before the web")
        if record:
            try:
                at.add(root, u, "unknown", sought[:SOUGHT_CHARS] or "(no prompt)", route=tool.lower())
            except Exception:  # noqa: BLE001 - a log write never blocks the read
                pass
    return {"decision": "pass", "context": "\n".join(lines)}


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    print(json.dumps(decide(payload), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
