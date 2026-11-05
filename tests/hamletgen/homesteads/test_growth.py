"""Feature 308, plan D1-D2 (FR-003, FR-004, FR-007): a nucleated cluster grown from its first house."""

from __future__ import annotations

import math
from types import SimpleNamespace
from typing import Any

from l7r.diagram.hamletgen.homesteads import growth


def _s() -> Any:
    return SimpleNamespace(px=lambda ft: ft)  # one foot a pixel


class _Ground:
    """A stand-in settlement: a placer that seats any homestead at least `room` from every other and inside `ring`."""

    def __init__(self, room: float, ring: float = 1e9, first: bool = True) -> None:
        self.room, self.ring = room, ring
        self.M: dict[str, Any] = {"houses": []}
        self._seat_search: dict[str, int] = {"candidates": 0}
        self._seat_region = None
        self.first = first
        self.asked: list[tuple[float, float]] = []
        self._canvas_box = (-1000.0, -1000.0, 1000.0, 1000.0)  # the canvas the growth widens to (`growth.on_the_canvas`)

    def px(self, ft: float) -> float:
        return ft

    def _hjit(self, x: float, y: float, salt: float) -> float:
        return 0.5

    def _bundle_envelope(self, x: float, y: float, w: float, h: float, shed: bool = False) -> tuple[float, float, float, float]:
        return (x, y, 40.0, 40.0)

    def _house_box(self, x: float, y: float, w: float, h: float) -> tuple[float, float, float, float]:
        return (x, y, w, h)

    def _house_box_refused(self, box: tuple[float, float, float, float]) -> bool:
        return False

    def try_place(self, x: float, y: float, _kind: str) -> bool:
        self.asked.append((x, y))
        if math.hypot(x, y) > self.ring or any(math.hypot(x - h["x"], y - h["y"]) < self.room for h in self.M["houses"]):
            return False
        self.M["houses"].append({"x": x, "y": y, "geom": {"bbox": (x, y, 40.0, 40.0), "boxes": {}}})
        return True


def _plan(n: int) -> Any:
    return SimpleNamespace(spec=SimpleNamespace(households=n), seat={"cx": 0.0, "cy": 0.0}, envelope=[])


class _Tight(_Ground):
    """The stand-in placer, each seated household reached by a corridor and given a yard, recording the tight seat's word."""

    def __init__(self, room: float) -> None:
        super().__init__(room)
        self.told: list[Any] = []

    def _bundle_envelope(self, x: float, y: float, w: float, h: float, shed: bool = False) -> tuple[float, float, float, float]:
        return (x, y, 120.0, 120.0)  # a homestead's envelope at the engine's scale: a tight seat stands past half a pitch

    def try_place(self, x: float, y: float, _kind: str) -> bool:
        told = getattr(self, "_tight_of", None)
        self.told.append(told)
        ok = super().try_place(x, y, _kind)
        if ok:
            self.M["houses"][-1]["geom"].update(access=((x, y), (x, y - 50.0)), boxes={"yard": (x, y + 10.0, 20.0, 10.0)})
            if told is not None:
                self._passage_left -= 1  # type: ignore[attr-defined]  # a passage spends the share, as the placer's record does
        return ok


def test_the_built_share_is_the_homesteads_over_their_outline() -> None:
    """FR-007 (feature 318): four 100 x 100 homesteads at the corners of a 300 x 300 square cover 40,000 of the 90,000 their
    corners' hull holds; under three homesteads there is no outline."""
    homes = [{"geom": {"bbox": (x, y, 100.0, 100.0)}} for x, y in ((50.0, 50.0), (250.0, 50.0), (50.0, 250.0), (250.0, 250.0))]
    assert growth.built_share(homes) == round(40000.0 / 90000.0, 3)
    assert growth.built_share(homes[:2]) == 0.0 and growth.built_share([{"geom": {}}] * 3) == 0.0
    flat = [{"geom": {"bbox": (x, 0.0, 0.0, 0.0)}} for x in (0.0, 1.0, 2.0)]
    assert growth.built_share(flat) == 0.0, "a degenerate outline reports nothing"
