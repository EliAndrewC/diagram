"""THE LANE LAW'S VERDICTS, KEPT PER LANE (feature 297, FR-005, plan D1).

The web is asked the whole lane law again and again - every settle round, the exit question (`settle.unsettled`), the last
resort's passes (`last_resort.lanes_breaking`, four times on Inashiro) - and between two asks one or two lanes have changed. Every
rule that reads a lane's own points against ground that does not change during the web - where it crosses a brook, whether its
end runs on alongside another lane, whether it kinks or hooks - answered the same question again for every unchanged lane:
`crossing_points` alone, rebuilding the brook's grid for every call, was 17% of the web stage's wall time on Inashiro (research
R10's sampler). A verdict is a pure function of the lane's points and the course or lane it is asked against, so it is KEPT,
keyed on those points, and a lane that has not changed is answered from the keeper; a lane that has is judged again when asked.

Exact: the same function answers, once per distinct input. Bounded (`KEEP`), so a long cohort does not grow it without end."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import Any

#: Distinct inputs kept per rule: a web asks a few hundred lanes a few dozen ways; a cohort worker rolls maps one after another.
KEEP = 16384


def pts_key(pts: Sequence[Any]) -> tuple[tuple[float, float], ...]:
    """A run's points as a hashable key."""
    return tuple((float(q[0]), float(q[1])) for q in pts)


def kept[T](fn: Callable[..., T]) -> Callable[..., T]:
    """`fn(*runs, *rest)`, answered once per distinct input: every positional argument that is a run of points is keyed by its
    points (`pts_key`); the rest must be hashable. The answer is returned as a fresh list where it is one, so a caller that edits
    it cannot edit the kept verdict."""

    @lru_cache(maxsize=KEEP)
    def _cached(key: tuple[Any, ...], kw: tuple[tuple[str, Any], ...]) -> Any:
        return fn(*key, **dict(kw))

    def keyed(*args: Any, **kwargs: Any) -> Any:
        key = tuple(pts_key(a) if isinstance(a, (list, tuple)) and a and isinstance(a[0], (list, tuple)) else a for a in args)
        got = _cached(key, tuple(sorted(kwargs.items())))
        return list(got) if isinstance(got, list) else got

    keyed.__wrapped__ = fn  # type: ignore[attr-defined]
    keyed.cache_clear = _cached.cache_clear  # type: ignore[attr-defined]
    keyed.__doc__ = fn.__doc__
    keyed.__name__ = getattr(fn, "__name__", "kept")
    return keyed


STEP_RULES: dict[str, tuple[str, ...]] = {
    "settle_husks": ("husks",),
    "square_every_crossing": ("off_ford", "oblique_brook", "oblique_channel"),
    "settle_shapes": ("bends", "hooks", "over_fixtures", "breaks_mid_run", "off_ford", "oblique_brook", "oblique_channel"),
    "settle_way_outs": ("way_outs", "over_and_back"),
    "settle_ends": ("folded_joints", "connector_hairpins", "doubled_tails", "dangling_ends", "doorstep_ends", "ends_behind", "needle_joins"),
    "settle_street_ends": ("dangling_ends",),
    "settle_joins": ("joins_short", "networks"),
    "settle_needles": ("needle_loops", "needle_joins"),
    "settle_network": ("networks",),
    "settle_fragments": ("fragments",),
    "settle_widths": ("width_steps",),
}
"""Which rules of `law.LAW` each repair step mends (feature 297): a later round runs only the steps whose rules are broken. A
step not here (the reach, the shadows, the deferral, the tree's pruning) is asked every round - its own test is its gate."""


def steps_for(broken: Mapping[str, Any], steps: Sequence[Any] | None = None) -> tuple[Any, ...]:
    """The steps of `STEPS`, in order, a round runs for the rules `broken` names: every step whose rules meet them and every step
    `STEP_RULES` does not map; the whole of `STEPS` where a broken rule is mapped to no step."""
    from .settle import STEPS

    every = tuple(STEPS if steps is None else steps)
    mapped = {r for rules in STEP_RULES.values() for r in rules}
    if any(r not in mapped for r in broken):
        return every
    return tuple(st for st in every if st.__name__ not in STEP_RULES or set(STEP_RULES[st.__name__]) & set(broken))


NOT_THE_SETTLES = ("unbridged", "short_decks", "planks", "unreached_houses", "field_unreached", "unreached_targets")
"""The rules of `law.LAW` the settle's exit does not ask (`unsettled`): the decks and planks, drawn after the web
(`stage_crossings`), so every crossing is undecked when the settle ends - the finished map is asked them; a farmhouse or the
reserved field left unreached, refused on its own (`last_resort.refuse_unreached`); and a way target no lawful spur reaches,
which the settle reports rather than draws to least-bad (`settle_targets`, FR-005)."""


def unsettled(M: Mapping[str, Any], ground: Any = None) -> dict[str, Any]:
    """Every rule of the lane law (`law.LAW`, the predicates the acceptance sweep asks) the web as it stands breaks, but for
    those `NOT_THE_SETTLES` - the settle's exit question, asked however the rounds ended. `ground`, the worked ground the
    settle already holds (`memo_ground`), is handed to the two rules that read it: built afresh by each it was two thirds
    of the question's cost (~120 of ~186 ms a map over the pool and cohort 1-20, 2026-09-30)."""
    from . import law  # bound here: `law` keeps its verdicts through this module (`kept`)

    rules = {**law.LAW, "dangling_ends": lambda M: law.dangling_lane_ends(M, ground), "ends_behind": lambda M: law.ends_behind(M, ground)} if ground is not None else law.LAW
    return {name: v for name, rule in rules.items() if name not in NOT_THE_SETTLES and (v := rule(M))}
