"""The Rust stages, and a roll through them alone (feature 444 amendment 5, FR-019).

WHY: the GM, 2026-10-31: "no Rust stage ever ends with any failing checks at the point where that stage has completed ... all
seeds pass for all Rust stages, but we don't care at all about the Python stages which come after". The stages are ported in
`STAGES` order, so the Rust stages are the front of the pipeline: a roll stops where they end, and the map is judged there.
A stage is Rust when `rust/phases/src/<stage>.rs` holds it - derived, so a port that lands its `.rs` joins the gate with no
table to edit. The state each stage starts from is kept as it runs, so a stage that fails leaves its input behind to be
replayed (FR-020): a seed that later passes only because a change upstream made it another map does not hide the failure.

Research:
    the Rust stage gate - NONE: how a roll is stopped and judged, no claim about a map
"""

from __future__ import annotations

import json
import pickle
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from .driver import STAGES, fresh_settlement, roll_scope
from .phases_ext import ROOT

Stage = Callable[[Any, Any], None]


def stage_name(stage: Stage) -> str:
    """`stage_water_frame` -> `water_frame`."""
    return stage.__name__.removeprefix("stage_")


def rust_stages(stages: Sequence[Stage] = STAGES, src: Path = ROOT / "rust" / "phases" / "src") -> list[Stage]:
    """The stages a `rust/phases/src/<stage>.rs` holds, in `STAGES` order."""
    return [st for st in stages if (src / f"{stage_name(st)}.rs").is_file()]


def off_the_front(stages: Sequence[Stage], rust: Sequence[Stage]) -> list[str]:
    """The Rust stages that are not the front of `stages` - a port landed out of `STAGES` order (none, as it should be)."""
    return [stage_name(st) for st in rust if st not in stages[: len(rust)]]


def roll_through(plan: Any, stages: Sequence[Stage], start: tuple[Any, Any] | None = None) -> tuple[Any, str | None, BaseException | None, list[tuple[str, bytes, set[str]]]]:
    """Run `stages` in order on a fresh settlement (or on `start`, a frozen (settlement, plan)): (the settlement, the stage that
    raised or None, what it raised, the trace - each stage run as (its name, the state it started from pickled: its frozen
    input, the parts of the map it wrote)). A stage that raised ends the trace, its input frozen and its writes none."""
    s, plan = start if start is not None else (fresh_settlement(plan), plan)
    trace: list[tuple[str, bytes, set[str]]] = []
    with roll_scope(plan.spec):
        for st in stages:
            frozen, was = pickle.dumps((s, plan)), _parts(s.M)
            try:
                st(s, plan)
                s.standing.resync()
            except Exception as e:  # noqa: BLE001 - any raise in a Rust stage is that stage's failure, reported by its name
                trace.append((stage_name(st), frozen, set()))
                return s, stage_name(st), e, trace
            now = _parts(s.M)
            trace.append((stage_name(st), frozen, {k for k in now.keys() | was.keys() if now.get(k) != was.get(k)}))
    return s, None, None, trace


def _parts(M: dict[str, Any]) -> dict[str, str]:
    """Each part of the map as text: its top-level keys and `meta.<key>`s."""
    out = {k: _dump(v) for k, v in M.items() if k != "meta"}
    return out | {f"meta.{k}": _dump(v) for k, v in (M.get("meta") or {}).items()}


def held(before: dict[str, Any]) -> set[str]:
    """The parts the fresh settlement already holds with content - inputs a check may read beside the Rust stages' output."""
    return {k for k, v in _parts(before).items() if v != _dump(None)}


def _dump(v: Any) -> str:
    """A part of the map as text to compare - an empty part as an absent one: a stage that writes nothing there wrote nothing."""
    return json.dumps(v if v not in ([], {}, "", None) else None, sort_keys=True, default=str)


class Reads(dict):
    """A manifest that records which of its parts a check reads (`meta.<key>` for the meta's)."""

    def __init__(self, data: dict[str, Any], seen: set[str] | None = None, prefix: str = "") -> None:
        super().__init__(data)
        self.seen = set() if seen is None else seen
        self.prefix = prefix

    def _note(self, key: Any) -> None:
        self.seen.add(f"{self.prefix}{key}")

    def __getitem__(self, key: Any) -> Any:
        self._note(key)
        return self._wrap(key, super().__getitem__(key))

    def get(self, key: Any, default: Any = None) -> Any:
        self._note(key)
        return self._wrap(key, super().get(key, default))

    def __contains__(self, key: object) -> bool:
        self._note(key)
        return super().__contains__(key)

    def _wrap(self, key: Any, value: Any) -> Any:
        return Reads(value, self.seen, "meta.") if key == "meta" and not self.prefix and isinstance(value, dict) else value


def owned_reads(seen: set[str]) -> set[str]:
    """What a check read, the meta itself aside (reading `meta` is how its keys are reached)."""
    return {k for k in seen if k != "meta"}
