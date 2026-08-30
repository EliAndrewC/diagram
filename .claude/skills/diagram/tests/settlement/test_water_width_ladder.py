"""The water-width ladder: a ditch is the thinnest line on the map (feature 166).

Carries `irrigation_channels_hairline` and `watercourses_wider_than_ditches`, which the retired battery
re-measured on every finished map.

THE GROUNDING, kept with the rule because the number is otherwise arbitrary: a field-level irrigation
ditch is about 0.3 m wide, roughly 1/300 of the 1-cho paddy it feeds. At map scale that is far below a
drawable line, so it sits at the LEGIBILITY FLOOR (~2.5 px) - drawn wider than truth on purpose, but still
clearly finer than any natural watercourse, so the ladder stays honest in its ORDER even where it cannot
be honest in its absolute widths. That ordering is the whole rule: a reader must be able to tell a dug
feeder from a stream by weight alone.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _s() -> Settlement:
    s = Settlement(1200, 900, seed=1)
    s.meta(name="Widthly", scale="hamlet", ftpx=1, down_deg=90)
    return s


def _widths(s: Settlement, key: str) -> list[float]:
    return [float(o.get("w") or o.get("width") or 0.0) for o in (s.M.get(key) or [])]


def test_an_irrigation_channel_is_drawn_at_the_hairline_floor() -> None:
    """`irrigation_channels_hairline`: the default channel width is the legibility floor, not a value a
    caller has to remember to pass. A ditch drawn at a natural watercourse's weight reads as a stream."""
    s = _s()
    s.channel((200.0, 300.0), (900.0, 300.0), frm={"kind": "stream"}, to={"kind": "field", "name": "f"})
    got = _widths(s, "channels") or _widths(s, "drawn_channels")
    assert got, "the channel recorded a width"
    assert max(got) <= 3.0, f"a dug feeder is a hairline, drawn {max(got)}"


def test_a_natural_watercourse_is_drawn_wider_than_a_dug_one() -> None:
    """`watercourses_wider_than_ditches`: the ORDER of the ladder, which is what a reader actually uses.
    Absolute widths are a legibility deviation; their ordering is not negotiable."""
    s = _s()
    s.channel((200.0, 300.0), (900.0, 300.0), frm={"kind": "stream"}, to={"kind": "field", "name": "f"})
    s.river([(100.0, 600.0), (1100.0, 600.0)], width=20.0)
    ditch = max(_widths(s, "channels") or _widths(s, "drawn_channels") or [0.0])
    stream = max(_widths(s, "streams") or [0.0])
    assert stream > ditch, f"a stream ({stream}) must outweigh a dug feeder ({ditch})"
