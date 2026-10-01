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

from collections.abc import Callable, Sequence
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
