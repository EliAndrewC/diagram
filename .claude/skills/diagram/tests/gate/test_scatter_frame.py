"""Feature 224 FR-002: the scatter's predicted frame is verified on every shipped hamlet - a view that reached past
the frame any scatter threw within would leave a strip with no scatter, so no pool manifest may record a breach."""

from __future__ import annotations

import glob
import json
import os

import pytest

_POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pool")


@pytest.mark.parametrize("manifest", sorted(glob.glob(os.path.join(_POOL, "hamlets", "*", "*.json"))), ids=os.path.basename)
def test_no_shipped_hamlet_breaches_its_scatter_frame(manifest: str) -> None:
    with open(manifest, encoding="utf-8") as fh:
        meta = json.load(fh)["meta"]
    assert "scatter_frame" in meta, "a hamlet's scatters throw within a predicted frame"
    assert "scatter_frame_breach" not in meta, f"the view reaches past the predicted frame by {meta.get('scatter_frame_breach')} (left, top, right, bottom)"
    assert max(meta["scatter_frame_overhang"]) < 0, "the view stays strictly inside the predicted frame"
