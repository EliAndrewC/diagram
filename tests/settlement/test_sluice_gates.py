"""The sluice gate: where a channel changes water (feature 166).

Carries `sluice_gates_on_water` and the recording half of `channel_gates_at_water_junctions`, which the
retired battery re-measured on every finished map.

WHAT A SLUICE GATE IS FOR, kept with the rule because the glyph is meaningless without it: the comb
doctrine's "sluice-fed head-race" always implied an intake control board and no map drew one (GM
2026-07-23). It goes wherever a channel CHANGES WATER - a moat or river tap handing off to the comb's own
canal, or a field drain handing off to its outfall culvert. The palette seam sits exactly there, and the
gate is what makes it read as engineered rather than as two strokes crossing.

THE SPAN IS A RESEARCHED CORRECTION, not a style knob (GM 2026-08-09): on the capital's 66 ft leats the
default field-channel frame floated mid-water and read as detached. A real frame spans abutment to
abutment, and the operator walks the crossbeam - so `span` stretches the frame ACROSS its channel and puts
the posts on the banks.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _s() -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Sluiceton", scale="hamlet", ftpx=1, down_deg=90)
    return s


def test_a_sluice_gate_records_itself_where_it_was_placed() -> None:
    """The recording half of `channel_gates_at_water_junctions`. A gate drawn and not recorded is a gate
    no reader of the manifest can find, and the junction it marks reads as two strokes crossing."""
    s = _s()
    s.sluice_gate(400.0, 500.0, rot=90.0)
    gates = s.M.get("sluice_gates") or []
    assert len(gates) == 1, "the gate recorded itself"
    g = gates[0]
    assert abs(float(g["x"]) - 400.0) < 1.0 and abs(float(g["y"]) - 500.0) < 1.0


def test_each_gate_at_a_different_junction_is_recorded_separately() -> None:
    """A comb has an intake AND an outfall, and a map that records one gate for both has lost the
    distinction the glyph exists to draw."""
    s = _s()
    s.sluice_gate(400.0, 500.0, rot=90.0)
    s.sluice_gate(900.0, 500.0, rot=90.0)
    assert len(s.M["sluice_gates"]) == 2


def test_the_span_widens_the_frame_so_its_posts_stand_on_the_banks() -> None:
    """The GM's 2026-08-09 correction. Without a span the frame keeps its field-channel geometry - which
    is right for a 4 ft ditch and wrong for a 66 ft leat, where it floats mid-water and reads as
    detached. A wider span must produce a wider drawn frame, or the correction did nothing."""
    narrow = _s()
    narrow.sluice_gate(400.0, 500.0, rot=0.0)
    wide = _s()
    wide.sluice_gate(400.0, 500.0, rot=0.0, span=66.0)
    # THE DRAWN FRAME is what matters here, not the record: the correction was about what a reader
    # sees floating mid-water. A sluice draws on the TOP layer, above the water.
    assert "".join(wide.top) != "".join(narrow.top), "the span changed nothing that is drawn"

    def _board_width(top: list[str]) -> float:
        import re

        widths = [float(m) for m in re.findall(r'width="([0-9.]+)"', "".join(top))]
        return max(widths) if widths else 0.0

    assert _board_width(wide.top) > _board_width(narrow.top), "a 66 ft leat got no wider a frame than a field ditch"
