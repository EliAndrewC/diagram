"""The constructed settlement the settle's suites share (`test_settle.py`, `test_settle_reach.py`, `test_knots.py`,
`test_last_resort.py`): split out of `test_settle.py` at the 1,000-line bar (405 T107, under T53's rule)."""

from ._builders import AdmitsAll


class _S(AdmitsAll):
    """The four things `settle_the_web` touches on a Settlement: the manifest, `lane()`, `reink_lane()`, `drop_lanes()`."""

    def __init__(self, lanes=(), houses=(), **extra):
        self.M = {"lanes": [], "houses": [{"x": x, "y": y, "w": 40.0, "h": 28.0, "rot": 0.0} for x, y in houses], "meta": {"ftpx": 1.0}, **extra}
        for ln in lanes:
            pts, kw = (ln, {}) if isinstance(ln, list) else ln
            self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("w", 3), "worn": True, "connector": kw.get("connector", False), **({"spur": True} if kw.get("spur") else {})})

    def lane(self, pts, width=3, clearance=0, worn=True, connector=False, spur=False):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": width, "worn": worn, "connector": connector, "spur": spur})

    def reink_lane(self, i):
        pass

    def drop_lanes(self, idxs):
        for i in sorted(set(idxs), reverse=True):
            del self.M["lanes"][i]


def _c(*pts):
    return ([*pts], {"connector": True, "w": 6})


def _pts(s, i):
    return [(float(x), float(y)) for x, y in s.M["lanes"][i]["pts"]]


BROOK = {"poly": [[100.0, -500.0], [100.0, 500.0]], "w": 6.0}
CONN = _c((0.0, 0.0), (-1000.0, 0.0))


_GEN = {"ftpx": 1.0, "generated_by": "hamletgen"}
