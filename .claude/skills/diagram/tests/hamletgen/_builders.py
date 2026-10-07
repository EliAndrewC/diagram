"""Shared fixtures for the hamletgen test package: a known square field, and a plan that uses it."""

import copy
from typing import Any

from l7r.diagram import hamletgen as hg

SQUARE: list[tuple[float, float]] = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]
# THE SQUARE WITH A CROWN (feature 287, homes H30): three margins whose backs face a north wind - the crown's two
# shoulders and its top - so a seat has a LADDER of wind-facing margins; the plain square has only its north edge. It
# stands 700 px below the canvas' top so each margin's belt stands on the canvas (the room `plan.seat_room` gives).
CROWN: list[tuple[float, float]] = [(400.0, 800.0), (550.0, 720.0), (850.0, 720.0), (1000.0, 800.0), (1000.0, 1300.0), (400.0, 1300.0)]


def a_plan(households: int = 15, **kw: object) -> hg.SitePlan:
    """A plan with a known square field, for testing the derivations that read one.

    `households` is a parameter because a test whose subject does not depend on the count should be
    allowed to ask for the cheapest hamlet the band permits (feature 158) - every household is a seat
    search, and 10 is the floor `HamletSpec` accepts. Nucleated unless a test asks for another form: a grove-farm form grows
    the canvas (`LINEAR_CANVAS`, feature 291), and the derivations tested here were measured on the nucleated one."""
    kw.setdefault("settlement_form", "nucleated")
    spec = hg.HamletSpec(name="Test", seed=3, households=households, down_deg=90.0, windward="N", **kw)  # type: ignore[arg-type]
    plan = hg.plan_site(spec)
    plan.envelope = list(SQUARE)
    return plan


SEAT_SHIFT = 300.0
"""How far `a_seat` moves the field in from the canvas's top and left before it seats it."""


def a_seat(plan: hg.SitePlan) -> dict[str, Any]:
    """`seat_cluster(plan)` for a field that stands nearer the canvas's top or left than a band's half-length - `SQUARE`, 400
    px in: `seat_cluster` holds the seat center a whole half-length (`lat`) inside the frame (feature 328), which the real
    canvas gives (`plan.seat_room`) and this fixture does not. The seat is found on the field moved `SEAT_SHIFT` in, then
    moved back, so a test's own coordinates about the field still hold."""
    moved = copy.copy(plan)
    moved.envelope = [(x + SEAT_SHIFT, y + SEAT_SHIFT) for x, y in plan.envelope]
    seat = hg.seat_cluster(moved)
    back = {k: (seat[k][0] - SEAT_SHIFT, seat[k][1] - SEAT_SHIFT) for k in ("anchor",) if k in seat}
    assert not seat.get("ladder"), "a ladder's frames would need moving back too"
    return {**seat, "cx": seat["cx"] - SEAT_SHIFT, "cy": seat["cy"] - SEAT_SHIFT, **back}
