"""The Python callers' door to the record tooling's leaves in Rust (feature 449 T81, slice 1): each function one `l7r-gate record` verb, a forwarder and
never a fallback, until its last caller is ported. FR-006: a run reaches each verb at most once where it can ask everything together - `fragments_for`
answers from one batch (`fragments_batch` asks a run's questions together, a repeat comes from memory). `americanize_json` left with `apply_edits.py`,
its last caller, and `moved_only`, which no Python called, with it (449 T145)."""

from __future__ import annotations

import json
import pathlib
import subprocess
from collections.abc import Iterable

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"

_FRAGMENTS: dict[tuple[str, str], list[str]] = {}


def _record(*args: str, stdin: str) -> str:
    done = subprocess.run([str(GATE), "record", *args], input=stdin, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise ValueError(done.stderr.strip())
    return done.stdout


def fragments_batch(questions: Iterable[str], root: str) -> None:
    """Ask for every question a run will name, in one process; `fragments_for` then answers from memory."""
    wanted = sorted({q for q in questions if (q, root) not in _FRAGMENTS})
    if wanted:
        found = json.loads(_record("fragments", "--root", root, stdin=json.dumps(wanted)))
        _FRAGMENTS.update({(q, root): found[q] for q in wanted})


def fragments_for(q: str, root: str) -> list[str]:
    """The files a check should read for `q` (a number, a page's file name, or several), `hm_record.fragments_for` in Rust."""
    fragments_batch([q], root)
    return _FRAGMENTS[(q, root)]
