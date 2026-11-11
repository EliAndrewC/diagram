"""The Rust bundles' one runner of the Python they still reach (feature 449 T88, `ask:449-T88-bundles`): the Rust-to-Python direction,
one process a bundle run, started by the Rust only when the run needs one of its verbs. It holds no logic: each verb calls one existing
Python function and prints its JSON. Each verb leaves when its owner ports (the helpers, `passages` and `save_cached` in T85, `claims_rows`
and `load_index` in T82, `knobs` and `knob_table` in phase 4, `is_current` - `l7r-gate reviews prereq check`'s, T89 - with
`l7r/diagram/pipeline/` in T90); the runner is deleted with the owner of its last verb, and named at the
phase-3 close if still present.

    python3 scripts/bundle_door.py    one JSON line a request on stdin, {"verb": ..., "args": [...]}; one JSON line a reply on stdout

A reply is `{"ok": <value>}` or `{"error": <the traceback>}`. The replies have a descriptor of their own: fd 1 is pointed at stderr at
start, so nothing a helper or its children print can reach the channel."""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import pathlib
import sys
import traceback
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
TREE = HERE.parent
sys.path[0:0] = [str(HERE / "record"), str(HERE), str(HERE / "hooks" / "lib"), str(TREE)]
sys.dont_write_bytecode = True
HELPERS = ("record_prepass", "quote_verbatim", "style_prepass", "source_pages")
#: a helper's argparse names its program as it did run inside `check_bundle.py`
sys.argv[0] = "check_bundle.py"


def run(name: str, args: list[str], root: str) -> list[Any]:
    """`main(args)` of one of check_bundle's in-process helpers (feature 383 D6), as `check_bundle._run_in_process` ran it: in `root`,
    stdout then stderr captured, the exit status from its return or its SystemExit."""
    if name not in HELPERS:
        raise ValueError(f"bundle-door: no helper {name}")
    mod = importlib.import_module(name)
    out, err, here = io.StringIO(), io.StringIO(), os.getcwd()
    try:
        os.chdir(root)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = mod.main(list(args))
            except SystemExit as stop:
                code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
                if stop.code is not None and not isinstance(stop.code, int):
                    print(stop.code, file=sys.stderr)
    finally:
        os.chdir(here)
    return [int(code or 0), out.getvalue() + err.getvalue()]


class NotCached:
    """The fetcher behind a cache-only read: a page the cache does not hold is named, never fetched (`check_bundle.residue_pages`)."""

    refused: dict = {}

    @staticmethod
    def get(_url: str) -> dict:
        return {"state": "NOT-CACHED", "why": "not in the page cache (quote-verbatim could not save it) - fetch it yourself"}


def save_cached(urls: list[str], out: str) -> None:
    """`source_pages.save` of `urls` into `out` from the host's page cache only - `residue_pages`' call, `CachedPages` kept in Python."""
    sp = importlib.import_module("source_pages")
    sp.save(urls, pathlib.Path(out), sp.src.CachedPages(NotCached(), sp.src.home()))


def passages(text: str) -> list[dict]:
    return importlib.import_module("quote_verbatim").passages(text)


def claims_rows(root: str) -> dict[str, dict[str, str]]:
    """`claims.current(root)`'s rows, each claim's backing and line - what `arbiter_bundle.claims_section` reads of a row."""
    cur = importlib.import_module("claims").current(pathlib.Path(root))
    return {k: {"backing": r.claim.backing, "line": r.claim.line} for k, r in cur.items()}


def load_index(root: str) -> dict:
    cx = importlib.import_module("claims")
    return cx.load_index(pathlib.Path(root) / cx.INDEX)


def knobs() -> dict[str, list[str]]:
    from l7r.diagram.interactive import conditions  # noqa: PLC0415 - phase 4's, reached here alone

    return {k: list(v) for k, v in conditions.knobs().items()}


def knob_table() -> dict:
    from l7r.diagram.interactive import conditions  # noqa: PLC0415

    return conditions.knob_table()


def is_current(gen: str) -> bool:
    """`gencache.is_current(gen)`: feature 240 FR-005's question, asked only by `l7r-gate reviews prereq check` (`ask:449-T89-reviews`)."""
    from l7r.diagram.pipeline import gencache  # noqa: PLC0415 - T90's, reached here alone

    return gencache.is_current(gen)


VERBS = {"run": run, "save_cached": save_cached, "passages": passages, "claims_rows": claims_rows, "load_index": load_index,
         "knobs": knobs, "knob_table": knob_table, "is_current": is_current}


def main() -> int:
    channel = os.fdopen(os.dup(1), "w", encoding="utf-8")
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            ask = json.loads(line)
            said: dict[str, Any] = {"ok": VERBS[ask["verb"]](*ask.get("args", []))}
        except Exception:  # noqa: BLE001 - the caller prints the traceback the Python would have raised
            said = {"error": traceback.format_exc()}
        channel.write(json.dumps(said, ensure_ascii=False) + "\n")
        channel.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
