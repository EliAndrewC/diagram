"""URBAN CHECK PATHS THE FROZEN EXHIBITS DO NOT REACH (feature 146).

Gating the six frozen town and city manifests exercised most of the urban battery, but not all of it:
those maps carry a castle and a moat but no street beside it, so the castle-moat clearance - which
measures a street, alley or lane against the moat - stayed unentered. (That frozen-manifest gate,
`test_frozen_pool_gate.py`, was itself deleted by feature 158 on the GM's ruling that a stored map no
generator can produce is not worth replaying. This file is what remains, and it is the RIGHT shape:
a hand-BUILT manifest is a fixture, not a map from the hand-placement era.)

(The ward-fence closure looked like the same case and was not: nothing calls it at all, so feature 146
removed it with the rest of feature 141's residue rather than inventing a manifest to reach dead code.)

It is ordinary check logic that wants a manifest, not a map, so it gets one here. The manifests are
deliberately small and hand-built: nothing at this scale is scripted yet, so there is no roll to break
(feature 141's scripted-fixture rule governs the SCRIPTED tier, and says so).
"""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram import check_village

from ..check_village._builders import manifest


def _city(**over: Any) -> dict[str, Any]:
    M = manifest(**over)
    M["meta"].update({"scale": "city", "ftpx": 3, "W": 1200, "H": 1200})
    return M


@pytest.mark.tiers("city")
def test_a_street_beside_a_castle_moat_is_measured() -> None:
    """The castle-moat clearance: a street, alley or lane too near the moat. The frozen cities have a
    castle and a moat but no way beside it, so the measuring loop had never been entered."""
    moat = [[400, 400], [700, 400], [700, 700], [400, 700]]
    M = _city(
        castles=[{"x": 550, "y": 550, "w": 200, "h": 200, "moat": moat, "moat_width": 24}],
        town_streets=[{"pts": [[400, 405], [700, 405]], "w": 18}],  # right on the moat's north arm
    )
    fails = check_village.gate(M, verbose=False)
    assert isinstance(fails, list)
