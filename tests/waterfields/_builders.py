"""Lay a whole comb field in one call, for tests: `finish_comb(carve_comb(...))`, the pair the scripted hamlet calls
(`hamletgen/water/fit.py`). The engine's one-call wrapper went with its last caller (feature 388); the tests that build a
comb to test what it lays call this instead."""

from typing import Any

from l7r.diagram.waterfields import carve_comb, finish_comb


def lay_comb(*args: Any, **kw: Any) -> dict[str, Any]:
    return finish_comb(carve_comb(*args, **kw))
