"""The Rust bundles' one runner of the Python they still reach (feature 449 T88, `ask:449-T88-bundles`): the Rust-to-Python direction,
one process a bundle run, started by the Rust only when the run needs one of its verbs. It holds no logic: each verb calls one existing
Python function and prints its JSON. Each verb leaves when its owner ports (the helpers, `passages` and `save_cached` in T85, `knobs`
and `knob_table` in phase 4, `is_current` - `l7r-gate reviews prereq check`'s, T89 - with `l7r/diagram/pipeline/` in T90; the `claims_*`
and `tunables_unstated` verbs - the Python half of the claims tools, which reads `.py` source by CPython's own syntax tree - in phase 4
with the Mode A code they read, and `gm_review_add_row` with `scripts/gm_review.py` in T91: `ask:449-T82-claims`, which also took
`claims_rows` and `load_index` off this runner); the runner is deleted with the owner of its last verb, and named at the phase-3 close
if still present.

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
import types
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


def _engine_claims() -> Any:  # noqa: ANN401 - the module
    from l7r.diagram.tools import claims as cl  # noqa: PLC0415 - the engine's claims reader, its Python half (`ask:449-T82-claims`)

    return cl


def claims_py_units(skill: str, every: bool, stars: bool) -> list[list[dict]]:
    """`tools/claims.py_units`: the units of the `.py` files under `skill` (the hamlet scope's, then those claimed outside it), each as
    `unit_json` gives it - `stars` False reads the fingerprints without the star re-exports (`make claims-refingerprint`)."""
    cl = _engine_claims()
    cl.STAR_REEXPORTS = stars
    try:
        return [[cl.unit_json(u, e) for u, e in half] for half in cl.py_units(pathlib.Path(skill), every_module_unit=every)]
    finally:
        cl.STAR_REEXPORTS = True


def claims_module_units(text: str, path: str) -> list[dict]:
    """`tools/claims.module_units(text, path)`'s units: a claimed dictionary's blocks as a version of its module held them."""
    cl = _engine_claims()
    return [cl.unit_json(u, []) for u in cl.module_units(text, path)[2]]


def claims_context_source(root: str, ref: str) -> str:
    return importlib.import_module("claims_context").py_source(pathlib.Path(root), ref)


def _unit(path: str, qualname: str) -> Any:  # noqa: ANN401 - what `claims_context` reads of a unit
    return types.SimpleNamespace(path=path, qualname=qualname)


def claims_callees(root: str, path: str, qualname: str, source: str, limit: int) -> list[str]:
    return importlib.import_module("claims_context").callees(pathlib.Path(root), _unit(path, qualname), source, limit)


def claims_direct(root: str, path: str, qualname: str, source: str) -> list[str]:
    ctx = importlib.import_module("claims_context")
    return ctx.direct(pathlib.Path(root), _unit(path, qualname), source, lambda r, ref: ctx.py_source(r, ref))


def claims_chase(root: str, path: str, names: list[str]) -> list[str]:
    ctx = importlib.import_module("claims_context")
    return ctx.chase(pathlib.Path(root), path, names, lambda r, ref: ctx.py_source(r, ref))


def claims_counter_only(root: str, base: str, was: dict, unit: dict, claim: str) -> bool:
    return importlib.import_module("claims_counters").counter_only_json(pathlib.Path(root), base, was, unit, claim)


def claims_stale(root: str) -> list[str]:
    return importlib.import_module("claims_stale").stale(pathlib.Path(root))


def claims_scope_units(text: str) -> dict[str, list[int]]:
    return {k: list(v) for k, v in importlib.import_module("claims_scope").units(text).items()}


def claims_read_units(root: str, seam: list[str]) -> list[str]:
    return sorted(importlib.import_module("claims_scope").read_units(pathlib.Path(root), [pathlib.Path(p) for p in seam]))


def tunables_unstated(source: str, unit_text: dict[str, str]) -> list[list]:
    return [list(t) for t in importlib.import_module("tunables").unstated(source, unit_text)]


def gm_review_add_row(spec_dir: str, row: dict) -> bool:
    """`gm_review.add_row`: `make claims-known`'s row and the GM's box, Python their one writer until T91 ports the file."""
    return importlib.import_module("gm_review").add_row(pathlib.Path(spec_dir), row)


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


VERBS = {"run": run, "save_cached": save_cached, "passages": passages, "knobs": knobs, "knob_table": knob_table, "is_current": is_current,
         "claims_py_units": claims_py_units, "claims_module_units": claims_module_units, "claims_context_source": claims_context_source,
         "claims_callees": claims_callees, "claims_direct": claims_direct, "claims_chase": claims_chase,
         "claims_counter_only": claims_counter_only, "claims_stale": claims_stale, "claims_scope_units": claims_scope_units,
         "claims_read_units": claims_read_units, "tunables_unstated": tunables_unstated, "gm_review_add_row": gm_review_add_row}


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
