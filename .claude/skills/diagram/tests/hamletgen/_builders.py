"""Shared fixtures for the hamletgen test package: a known square field, and a plan that uses it."""

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
