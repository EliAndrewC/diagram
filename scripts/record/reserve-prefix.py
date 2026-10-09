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

THE KEY CAP (feature 274 D4; research R1: a write session's cost follows its turn count, and its keys drive its
turns). The page-session runner tells a WRITE session `L7R_PAGE_SESSION` (its id) and `L7R_KEY_CAP` (10); a check,
assertions, split or handover session is never told the cap. Every ledger row records the session. With both set, a
registry reservation past the cap for that session is refused with the continuation instructions - finish the
question in hand, write the unreached items to `$L7R_CONTINUE`, commit and stop - and the runner starts that brief
next in a fresh session. `KEY_CAP_OK='<reason>'` passes it, logged. Glossary terms are not capped.

    reserve-prefix.py glossary "<term>"      -> prints the new glossary file's path
    reserve-prefix.py registry <key> [--url U] [--tags T]  -> prints the new registry entry's path; its stub ends with
                                             the tags marker (feature 305), a placeholder until --tags gives them
"""

from __future__ import annotations

import argparse
import importlib.util
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path[1:1] = [str((Path(__file__).resolve().parent / _d).resolve()) for _d in ('../pages',)]  # the moved scripts it imports (2026-10-08)
import escape_log as _escape_log  # noqa: E402

# GUARD_EDIT_OK: feature 303 - a third kind, `question`: a new question of the record takes the next free identity number
# (`research/questions/NNNN-<heading id>.html`) under the same lock, so two sessions never number two questions alike.
DIRS = {
    "glossary": "l7r/diagram/interactive/assets/glossary",
    "registry": "research/sources/010-works-cited",
    "question": "research/questions",
    # GUARD_EDIT_OK: feature 312 FR-012 - a fourth kind, `uncited`: a kept page's write-up, in its own part of the registry,
    # numbered in the registry's ONE sequence (so an entry moved to the works cited when it is first cited keeps its number).
    "uncited": "research/sources/040-uncited-works",
}
SUFFIX = {"glossary": ".json", "registry": ".html", "question": ".html", "uncited": ".html"}
#: Kinds that share one number sequence and one key space: a registry key is one work, cited or not (feature 312).
SHARED = {"registry": ("registry", "uncited"), "uncited": ("registry", "uncited")}
LEDGER = "prefixes.jsonl"
STEP = 10
#: A question's number is its identity and not its order (feature 303), so the numbers run on with no gap.
STEPS = {"question": 1}


class Refusal(Exception):
    pass


def mirror_of(root: Path) -> Path:
    """The mirror: a clone's grandparent when its parent is `.clones`, else the root itself (as `claim-feature.py`)."""
    return root.parent.parent if root.parent.name == ".clones" else root


def name_for(kind: str, key: str) -> str:
    """The file name after the prefix: a glossary term by the glossary's own rule (case and spaces kept, `%` and `/`
    encoded - `glossary_source._encode`), a registry key as it is."""
    return (key.replace("%", "%25").replace("/", "%2F") if kind == "glossary" else key) + SUFFIX[kind]


def holding(d: Path, kind: str, key: str) -> list[Path]:
    """The files in `d` that hold exactly this key: a prefix, a hyphen, then the key's own file name. A bare glob on
    `*-<name>` also caught a longer key ending in this one - `honjin-jawiki` was refused because
    `11320-kusatsu-honjin-jawiki.html` was on file (feature 271, 2026-09-27)."""
    name = name_for(kind, key)
    return [f for f in d.glob(f"*-{name}") if re.fullmatch(r"\d+-", f.name[: -len(name)])] if d.is_dir() else []


def prefixes_in(d: Path) -> list[int]:
    return [int(m.group(1)) for f in d.glob("*") if (m := re.match(r"(\d+)-", f.name))] if d.is_dir() else []


def highest(kind: str, root: Path, mirror: Path) -> int:
    kinds = SHARED.get(kind, (kind,))
    held = [p for k in kinds for p in prefixes_in(mirror / DIRS[k]) + prefixes_in(root / DIRS[k])]
    clones = mirror / ".clones"
    if clones.is_dir():
        for c in clones.iterdir():
            held += [p for k in kinds for p in prefixes_in(c / DIRS[k])]
    ledger = mirror / ".specify" / LEDGER
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") in kinds:
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
            if row.get("kind") in SHARED.get(kind, (kind,)) and row.get("key") == key and Path(str(row.get("clone", ""))).resolve() != root.resolve():
                return f"{row.get('clone')} (reserved {row.get('prefix')}, {row.get('utc')})"
    clones = mirror / ".clones"
    for c in sorted(clones.iterdir()) if clones.is_dir() else []:
        if c.resolve() != root.resolve() and any(holding(c / DIRS[k], k, key) for k in SHARED.get(kind, (kind,))):
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


def session_keys(mirror: Path, session: str) -> int:
    """The registry keys this page session has reserved, from the ledger."""
    ledger = mirror / ".specify" / LEDGER
    n = 0
    for line in ledger.read_text(encoding="utf-8").splitlines() if ledger.is_file() else []:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        n += row.get("kind") == "registry" and row.get("session") == session
    return n


def check_key_cap(kind: str, key: str, mirror: Path) -> None:
    """Refuse a write session's registry key past its cap, unless `KEY_CAP_OK` gives a reason (feature 274 D4)."""
    session, cap = os.environ.get("L7R_PAGE_SESSION", ""), os.environ.get("L7R_KEY_CAP", "")
    if kind != "registry" or not session or not cap.isdigit():
        return
    n = session_keys(mirror, session)
    if n < int(cap):
        return
    try:
        if _escape_log.escape("KEY_CAP_OK", "reserve", "key-cap", {"key": key, "session": session, "reserved": n}):
            return
    except _escape_log.NoReason as e:
        raise Refusal(str(e)) from None
    cont = os.environ.get("L7R_CONTINUE", "$L7R_CONTINUE")
    raise Refusal(f"this write session has reserved {n} new registry keys, its cap (feature 274: a write session takes at "
                  f"most {cap}; its cost grows with its length). Do not reserve {key!r}. Finish the question in hand with the "
                  f"keys you have; then write the items you have not reached to {cont} as a brief of the same shape - the "
                  "same header, a `## Your items` list of just those items, the same handoff path - commit, and stop. "
                  "The runner starts that brief next, in a fresh session. For a deliberate larger load: KEY_CAP_OK='<reason>'")


def _sources():  # noqa: ANN202
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("_sources", HERE / "sources.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: Where the record keeps its source vocabulary, under the clone (feature 305).
RECORD = Path("research")
#: A registry stub's tags marker before its tags are given: no value is a real one, so `make record` refuses the entry
#: until it is filled (feature 305 FR-011) - a source cannot reach the site untagged.
TAGS_PLACEHOLDER = "<!-- tags: period=<period>; region=<region>; kind=<kind> -->"


def _source_tags():  # noqa: ANN202 - the engine's own parser, loaded by path: one grammar for the marker, and stdlib-only
    spec = importlib.util.spec_from_file_location("_source_tags", HERE.parents[1] / "l7r/diagram/interactive/record/source_tags.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # a dataclass resolves its module by name while the class is made
    spec.loader.exec_module(mod)
    return mod


def tags_marker(tags: str, root: Path) -> str:
    """The marker for `TAGS="period=..; region=..; kind=.."`, checked against the clone's `source-tags.json`; refused,
    naming the allowed values, when a facet is missing or a value unknown (feature 305 FR-011)."""
    st = _source_tags()
    try:
        parsed = st.parse(f"<!-- tags: {tags} -->", "TAGS", st.load_vocabulary(str(root / RECORD)))
    except st.SourceTagError as e:
        raise Refusal(str(e)) from None
    assert parsed is not None
    return parsed.marker()


def registry_stub(key: str, url: str, marker: str = TAGS_PLACEHOLDER) -> str:
    """A registry entry's opening, naming its pointer the way every entry does (`_check_bundle.url_of` reads it), and
    its tags marker as its last line (feature 305) - the placeholder until `TAGS=` gives them."""
    pointer = f"<p>({url})</p>\n" if url else ""
    return f'<h3 id="{key}"><code>{key}</code></h3>\n{pointer}{marker}\n'


def question_stub(key: str) -> str:
    """A new question's page: its heading, and a tags marker the build refuses until it is filled from `tags.json`
    (feature 303) - so a question cannot reach the site untagged."""
    return f'<h2 id="{key}">TITLE</h2>\n<!-- tags: subject=<subject>; setting=<setting>; level=<level> -->\n<p></p>\n'


def reserve(kind: str, key: str, root: Path, mirror: Path | None = None, stub: str | None = None, timeout: float = 30.0, url: str = "", tags: str = "") -> Path:
    """The new file's path, its prefix reserved and a stub written before the lock is released.

    With `url` (a registry entry only, feature 288 FR-005) the stub names the pointer and the sources-consulted ledger
    marks it `cited:<key>` at once; without it, nothing differs from before."""
    if kind not in DIRS:
        raise Refusal(f"KIND must be one of {sorted(DIRS)}")
    if url and kind not in ("registry", "uncited"):
        raise Refusal("URL= names a registry entry's source - it is for KIND=registry or KIND=uncited only")
    if tags and kind not in ("registry", "uncited"):
        raise Refusal("TAGS= are a registry entry's source tags - they are for KIND=registry or KIND=uncited only")
    if kind in ("registry", "uncited") and stub is None:
        stub = registry_stub(key, url, tags_marker(tags, root) if tags else TAGS_PLACEHOLDER)
    if not key.strip():
        raise Refusal("KEY is required - the glossary term, the registry key, or the question's heading id")
    mirror = mirror_of(root) if mirror is None else mirror
    d = root / DIRS[kind]
    existing = [f for k in SHARED.get(kind, (kind,)) for f in holding(root / DIRS[k], k, key)]
    if existing:
        raise Refusal(f"{existing[0].relative_to(root)} already holds {key!r} - edit it rather than reserving another")
    with Lock(mirror / ".specify" / "prefixes.lock", timeout):
        elsewhere = held_elsewhere(kind, key, root, mirror)
        if elsewhere:
            raise Refusal(f"{key!r} is already being defined in {elsewhere} - one home per {kind} key; pull that work in and edit it there")
        check_key_cap(kind, key, mirror)
        step = STEPS.get(kind, STEP)
        prefix = (highest(kind, root, mirror) // step + 1) * step
        path = d / f"{prefix:04d}-{name_for(kind, key)}"
        d.mkdir(parents=True, exist_ok=True)
        if stub is None:
            stub = question_stub(key) if kind == "question" else json.dumps({"term": key, "def": "", "variants": [key]}, ensure_ascii=False, indent=1) + "\n" if kind == "glossary" else ""
        path.write_text(stub, encoding="utf-8")
        row = {"kind": kind, "key": key, "prefix": prefix, "clone": str(root), "session": os.environ.get("L7R_PAGE_SESSION", ""), "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        with open(mirror / ".specify" / LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    if url and kind == "registry":  # an uncited entry's page is written up, not cited (feature 312)
        src = _sources()
        src.append(src.home(root), [src.line(src.context(root), url, f"cited:{key}")])
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
    ap.add_argument("--url", default="", help="a registry entry's source: the stub names it and the sources-consulted ledger marks it cited (feature 288)")
    ap.add_argument("--tags", default="", help='a registry entry\'s source tags, "period=..; region=..; kind=.." (feature 305)')
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
        path = reserve(args.kind, args.key, root, mirror, url=args.url, tags=args.tags)
    except Refusal as e:
        print(f"reserve: {e}", file=sys.stderr)
        return 2
    print(path)
    if args.url and args.kind == "registry":
        archive_at_cite(root, args.url, args.key)
    return 0


def archive_at_cite(root: Path, url: str, key: str, runner=subprocess.run) -> int:  # noqa: ANN001 - the seam a test replaces
    """A source cited from now on is archived as it is cited (feature 309 FR-006): `archive.py url` runs on the new
    entry's URL, its report on stderr so stdout stays the path a caller reads. A failure never blocks the reservation -
    the archiver records its own outcome, and the record build names a URL still owed a copy."""
    done = runner([sys.executable, str(HERE / "archive.py"), "url", url, "--key", key], cwd=root, stdout=sys.stderr, stderr=sys.stderr, check=False)
    if done.returncode != 0:
        print(f"reserve: archiving {url} failed (exit {done.returncode}) - `make archive URL='{url}' KEY={key}` retries it", file=sys.stderr)
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
