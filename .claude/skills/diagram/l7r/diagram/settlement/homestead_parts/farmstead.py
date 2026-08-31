"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core import Settlement


class FarmsteadMixin:
    def _attach_grove(self: Settlement, hx: float, hy: float, arms: Any) -> None:  # type: ignore[misc]
        """Draw a farmstead's windbreak grove (its belt arms) and record each arm under its parent house.
        Arms go into `grove_rects` (NOT `placed`) so a neighbor's grove may MERGE with it and the wells
        still avoid it. Drawn in the farmsteads() second pass, after every house/yard/garden is set."""
        for cx, cy, w, h, face in arms:
            self._draw_grove(cx, cy, w, h, face)
            self.M["groves"].append({"x": round(cx, 1), "y": round(cy, 1), "w": w, "h": h, "rot": 0, "of": [hx, hy], "face": list(face)})
            self.grove_rects.append((cx, cy, w, h))

    def _find_appurtenances(self: Settlement, hx: float, hy: float, hw: float, hh: float, rot: float = 0, kind: str = "plain", shed: Any = False, wealth: float = 1.0) -> tuple[Any, Any] | None:  # type: ignore[misc]
        """A farmstead needs room for BOTH its threshing yard (south/front, then a side) AND its dooryard
        kitchen garden (a DIFFERENT sunny side, kept off the west-side shed). Returns (yard_spot, garden_spot)
        or None if either can't fit."""
        yard = self._find_yard_spot(hx, hy, hw, hh)
        if yard is None:
            return None
        shed_rect = self._farm_shed_rect(hx, hy, hw, hh, rot, kind, shed)
        garden = self._find_garden_spot(hx, hy, hw, hh, yard, shed_rect, wealth)
        if garden is None:
            return None
        return yard, garden

    def _farmstead_nudges(self: Settlement) -> Iterator[tuple[float, float]]:  # type: ignore[misc]
        """Offsets to try for a farmhouse so the whole homestead (house + yard + garden + grove-room) fits:
        the ring's own spot first, then a widening spiral of shifts. The solver stops as soon as the home
        spot already works, so the wider rings only cost time for a genuinely crowded homestead."""
        yield 0, 0
        for d in (11 * self.bscale, 21 * self.bscale, 32 * self.bscale):
            yield from ((0, d), (d, 0), (-d, 0), (0, -d), (d, d), (-d, d), (d, -d), (-d, -d))
