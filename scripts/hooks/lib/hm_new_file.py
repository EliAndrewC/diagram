#!/usr/bin/env python3
"""The decision behind `new-file-hooks.sh` (feature 265 FR-010): does this call create an unreserved prefixed file?

Reads the hook payload on stdin. Prints nothing when the call passes; prints `<kind>\\t<key>` when it would CREATE a
glossary file or registry entry whose prefix the reservation ledger does not hold - the kind and key the refusal's
`make reserve` command names.

A Write: its `file_path`, when it lies in the glossary directory or `010-works-cited/` and does not exist yet. A Bash
command: each `NNNN-<name>.json|.html` target of a `>`/`>>` redirect or a `tee` - resolved against the command's
`cwd` when relative, and judged by its prefix alone when a shell variable makes the directory unknowable (a `.json`
is a glossary file, an `.html` a registry entry; the four-digit prefix is what only those two directories use).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# GUARD_EDIT_OK: feature 303 - a new question's stem takes a reserved number too; a page, notes or originals file of a
# stem that already exists passes, as an edit of an existing file does.
KIND_OF = {"assets/glossary": "glossary", "sources/010-works-cited": "registry", "research/questions": "question"}
_COMPANION = re.compile(r"(\.drawing)?(\.notes|\.originals)?$")
# GUARD_EDIT_OK: feature 265 - registry prefixes passed 9990 on 2026-09-27 (10040 and up), so a prefix is four OR five
# digits; `(?<!\d)` keeps a five-digit name from being read as its last four
TARGET = re.compile(r"(?:>>?|\btee\s+(?:-a\s+)?)\s*[\"']?([^\s\"'<>|;&]*?(?<!\d)(\d{4,5})-([^\s\"'<>|;&/]+?)\.(json|html))[\"']?(?=[\s;|&)]|$)")


def _rp():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("reserve_prefix", HERE / "../../record/reserve-prefix.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def kind_of_path(path: str) -> str:
    return next((k for d, k in KIND_OF.items() if f"/{d}/" in path.replace("\\", "/")), "")


def verdict(payload: dict) -> str:
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    rp = _rp()
    targets: list[tuple[str, Path | None, str, int]] = []
    if tool == "Write":
        fp = str(ti.get("file_path") or "")
        kind = kind_of_path(fp)
        m = re.match(r"(\d+)-(.+)\.(json|html)$", Path(fp).name)
        if kind and m:
            targets.append((kind, Path(fp), m.group(2), int(m.group(1))))
    elif tool == "Bash":
        cmd = str(ti.get("command") or "")
        names = assigned(cmd)
        for m in TARGET.finditer(cmd):
            raw, prefix, key, ext = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            raw = resolved(raw, names)
            if raw is None:
                continue  # GUARD_EDIT_OK: feature 383 a5 - written under a directory the command made with mktemp: not the record
            known = "$" not in raw
            kind = kind_of_path("/" + (raw if raw.startswith("/") else str(cwd / raw)))
            if not kind and known:
                continue  # a known path outside the two directories (plan review, round 2)
            if known and _top(cwd / raw) != _top(cwd):
                continue  # GUARD_EDIT_OK: feature 383 a5 - a known path in ANOTHER repository (a fixture's `git init` in /tmp)
            kind = kind or ("glossary" if ext == "json" else "registry")
            targets.append((kind, (cwd / raw) if known and not raw.startswith("/") else (Path(raw) if known else None), key, prefix))
    for kind, path, key, prefix in targets:
        if path is not None and path.exists():
            continue  # an edit of a file that is already there
        if kind == "question":
            key = _COMPANION.sub("", key)
            if path is not None and any(path.parent.glob(f"{prefix:04d}-{key}.*")):
                continue  # another file of a stem that exists
        root = path.parents[len(Path(rp.DIRS[kind]).parts)] if path is not None and len(path.parents) > len(Path(rp.DIRS[kind]).parts) else cwd
        plain = key.replace("%2F", "/").replace("%25", "%")
        if not rp.reserved(kind, prefix, rp.mirror_of(_top(root)), plain):
            return f"{kind}\t{plain}"
    return ""


# GUARD_EDIT_OK: feature 383 amendment 5 - a variable the command itself assigns is resolved before the path is judged: a
# fixture record built in a temporary directory (`D=$(mktemp -d); ... > "$D/research/questions/0041-a.html"`) was refused
# as a new question of this repository, twice in one session (2026-10-17)
ASSIGN = re.compile(r"""(?:^|[\s;&|(])([A-Za-z_]\w*)=(?:"([^"$]*)"|'([^']*)'|(\$\(mktemp\b[^)]*\))|([^\s;&|"'$()]+))""")


def assigned(cmd: str) -> dict[str, str | None]:
    """Each variable the command assigns a literal (its value) or a `$(mktemp ...)` (None: a temporary directory)."""
    out: dict[str, str | None] = {}
    for m in ASSIGN.finditer(cmd):
        out[m.group(1)] = None if m.group(4) else next(g for g in (m.group(2), m.group(3), m.group(5)) if g is not None)
    return out


def resolved(raw: str, names: dict[str, str | None]) -> str | None:
    """`raw` with a leading `$NAME` / `${NAME}` the command assigned replaced by its value; None under a mktemp directory."""
    m = re.match(r"\$\{?([A-Za-z_]\w*)\}?(/.*)$", raw)
    if not m or m.group(1) not in names:
        return raw
    value = names[m.group(1)]
    return None if value is None else value + m.group(2)


def _top(p: Path) -> Path:
    """The repository the path is in (its `.git`), else the path itself."""
    q = p.resolve()
    while not (q / ".git").exists() and q != q.parent:
        q = q.parent
    return q if (q / ".git").exists() else p


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    got = verdict(payload if isinstance(payload, dict) else {})
    if got:
        print(got)
    return 0


if __name__ == "__main__":
    sys.exit(main())
