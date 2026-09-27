#!/usr/bin/env python3
"""Reserve the next glossary or registry-entry prefix under a host-wide lock - `make reserve KIND=... KEY=...`.

WHY (feature 265 FR-010, the GM 2026-09-27): two or three pages' research queues run at once, each in its own
session clone, and a new glossary file (`assets/glossary/NNNN-<term>.json`) or registry entry
(`research/sources/010-works-cited/NNNN-<key>.html`) takes its prefix as "the highest + 10". Two sessions reading
"the highest" at once take the same number - the collision feature 250 already met twice across a merge (a glossary
prefix main and a clone both used). So the prefix is allocated the way `make claim` allocates a feature number.

WHAT "NEXT" MEANS, read UNDER THE LOCK: 10 past the highest prefix held by
  1. the mirror's working tree         (main as this container last saw it)
  2. every clone under `<mirror>/.clones/` (the other sessions' and queues' unpushed files)
  3. the ledger `<mirror>/.specify/prefixes.jsonl` (a prefix reserved whose file is not visible yet)
THE RESERVATION IS THE FILE: a stub is written at the new path before the lock is released, so the next caller's scan
(source 2) sees it; the caller then fills it. The lock and the ledger sit under the mirror's `.specify/`, beside
`make claim`'s, gitignored.

    reserve-prefix.py glossary "<term>"      -> prints the new glossary file's path
    reserve-prefix.py registry <key>         -> prints the new registry entry's path
"""

from __future__ import annotations

import argparse
import datetime
import fcntl
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIRS = {
    "glossary": ".claude/skills/diagram/l7r/diagram/interactive/assets/glossary",
    "registry": ".claude/skills/diagram/research/sources/010-works-cited",
}
SUFFIX = {"glossary": ".json", "registry": ".html"}
LEDGER = "prefixes.jsonl"
STEP = 10


class Refusal(Exception):
    pass


def mirror_of(root: Path) -> Path:
    """The mirror: a clone's grandparent when its parent is `.clones`, else the root itself (as `claim-feature.py`)."""
    return root.parent.parent if root.parent.name == ".clones" else root


def name_for(kind: str, key: str) -> str:
    """The file name after the prefix: a glossary term by the glossary's own rule (case and spaces kept, `%` and `/`
    encoded - `glossary_source._encode`), a registry key as it is."""
    return (key.replace("%", "%25").replace("/", "%2F") if kind == "glossary" else key) + SUFFIX[kind]


def prefixes_in(d: Path) -> list[int]:
    return [int(m.group(1)) for f in d.glob("*") if (m := re.match(r"(\d+)-", f.name))] if d.is_dir() else []


def highest(kind: str, root: Path, mirror: Path) -> int:
    held = prefixes_in(mirror / DIRS[kind]) + prefixes_in(root / DIRS[kind])
    clones = mirror / ".clones"
    if clones.is_dir():
        for c in clones.iterdir():
            held += prefixes_in(c / DIRS[kind])
    ledger = mirror / ".specify" / LEDGER
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") == kind:
                held.append(int(row.get("prefix", 0)))
    return max(held, default=0)


def held_elsewhere(kind: str, key: str, root: Path, mirror: Path) -> str:
    """Where ANOTHER clone already holds this key - a ledger row of its reservation, or its file in that clone's tree -
    else "". Two queues of feature 265 each reserved `plinth` (9230 and 9320): the lock kept their PREFIXES apart and
    nothing kept the TERM to one home, so the pull-back met two definitions and `make glossary` refused."""
    ledger = mirror / ".specify" / LEDGER
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") == kind and row.get("key") == key and Path(str(row.get("clone", ""))).resolve() != root.resolve():
                return f"{row.get('clone')} (reserved {row.get('prefix')}, {row.get('utc')})"
    clones = mirror / ".clones"
    for c in sorted(clones.iterdir()) if clones.is_dir() else []:
        if c.resolve() != root.resolve() and (c / DIRS[kind]).is_dir() and any((c / DIRS[kind]).glob(f"*-{name_for(kind, key)}")):
            return str(c)
    return ""


class Lock:
    """`flock` on the mirror's lock file, polled so a hung holder is a refusal rather than a hang."""

    def __init__(self, path: Path, timeout: float):
        self.path, self.timeout, self.fd = path, timeout, -1

    def __enter__(self) -> Lock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(self.fd)
                    raise Refusal(f"could not take the prefix lock within {self.timeout:g}s: {self.path} is held (fuser {self.path})") from None
                time.sleep(0.02)

    def __exit__(self, *_: object) -> None:
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)


def reserve(kind: str, key: str, root: Path, mirror: Path | None = None, stub: str | None = None, timeout: float = 30.0) -> Path:
    """The new file's path, its prefix reserved and a stub written before the lock is released."""
    if kind not in DIRS:
        raise Refusal(f"KIND must be one of {sorted(DIRS)}")
    if not key.strip():
        raise Refusal("KEY is required - the glossary term or the registry key")
    mirror = mirror_of(root) if mirror is None else mirror
    d = root / DIRS[kind]
    existing = [f for f in d.glob(f"*-{name_for(kind, key)}")] if d.is_dir() else []
    if existing:
        raise Refusal(f"{existing[0].relative_to(root)} already holds {key!r} - edit it rather than reserving another")
    with Lock(mirror / ".specify" / "prefixes.lock", timeout):
        elsewhere = held_elsewhere(kind, key, root, mirror)
        if elsewhere:
            raise Refusal(f"{key!r} is already being defined in {elsewhere} - one home per {kind} key; pull that work in and edit it there")
        prefix = (highest(kind, root, mirror) // STEP + 1) * STEP
        path = d / f"{prefix:04d}-{name_for(kind, key)}"
        d.mkdir(parents=True, exist_ok=True)
        if stub is None:
            stub = json.dumps({"term": key, "def": "", "variants": [key]}, ensure_ascii=False, indent=1) + "\n" if kind == "glossary" else ""
        path.write_text(stub, encoding="utf-8")
        row = {"kind": kind, "key": key, "prefix": prefix, "clone": str(root), "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        with open(mirror / ".specify" / LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def reserved(kind: str, prefix: int, mirror: Path, key: str | None = None) -> bool:
    """Whether the ledger holds this prefix for this kind - AND, given a key, for this key: what `new-file-hooks.sh`
    asks of a new file. The key matters (plan review): a session that reserved 0950 for one term and another that took
    0950 by hand for a different one both name a prefix the ledger holds; only the reservation's own key passes."""
    ledger = mirror / ".specify" / LEDGER
    if not ledger.is_file():
        return False
    for line in ledger.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("kind") == kind and int(row.get("prefix", -1)) == prefix and (key is None or row.get("key") == key):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("kind", choices=sorted(DIRS))
    ap.add_argument("key")
    ap.add_argument("--root", default="", help="the clone (default: the repository this runs in)")
    ap.add_argument("--mirror", default="", help="the mirror (default: the clone's grandparent under .clones/)")
    ap.add_argument("--check", default="", help="with a path: exit 0 if its prefix is reserved in the ledger, 1 if not")
    args = ap.parse_args(argv)
    if args.root:
        root = Path(args.root).resolve()
    else:  # the repository this runs in: its top, where `.git` is
        root = Path.cwd().resolve()
        while not (root / ".git").exists() and root != root.parent:
            root = root.parent
    mirror = Path(args.mirror).resolve() if args.mirror else mirror_of(root)
    if args.check:
        m = re.match(r"(\d+)-", Path(args.check).name)
        return 0 if m and reserved(args.kind, int(m.group(1)), mirror, args.key or None) else 1
    try:
        path = reserve(args.kind, args.key, root, mirror)
    except Refusal as e:
        print(f"reserve: {e}", file=sys.stderr)
        return 2
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
