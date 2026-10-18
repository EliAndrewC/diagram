"""Where a hamlet's dead lie (feature 273; feature 280 M68, research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html): a hamlet draws no
ground of its own and records where its dead lie. (The shared edge seat the village's cremation ground stood on went with its
last caller in feature 388.)"""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen.burial import BURIAL_FORMS, stage_burial
from l7r.diagram.settlement import Settlement
from tests.hamletgen._builders import a_plan

W, H = 60.0, 42.0  # a ground's box, px


def _hamlet(scale: str = "hamlet") -> Settlement:
    s = Settlement(W=1400, H=1400, seed=1)
    s.meta(name="X", scale=scale, ftpx=1.0)
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x, y in ((650, 650), (720, 650), (650, 700), (720, 700))]
    return s


def test_a_hamlet_draws_no_ground_of_its_own_and_records_where_its_dead_lie() -> None:
    """Feature 280 M68: a hamlet's own ground rests only on twentieth-century records, so its dead lie in the village's."""
    assert BURIAL_FORMS == ("village_ground",)
    s = _hamlet()
    stage_burial(s, a_plan())
    assert s.M["meta"]["hamlet_burial"] == "village_ground" and not s.M["cemeteries"]
    s.knob_pins["hamlet_burial"] = "own_ground"
    with pytest.raises(ValueError, match="hamlet_burial"):
        stage_burial(s, a_plan())
    v = _hamlet(scale="village")
    stage_burial(v, a_plan())
    assert "hamlet_burial" not in v.M["meta"]
    e = Settlement(W=600, H=600, seed=1)
    e.meta(name="X", scale="hamlet", ftpx=1.0)
    stage_burial(e, a_plan())
    assert "hamlet_burial" not in e.M["meta"], "no houses, nothing to say"
