"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""


# ---- feature 123: the web's guard rails, each exercised on its own -------------------------------


def _lanes(*polys):
    """A minimal Settlement stand-in carrying only what the web helpers read."""

    class _S:
        def __init__(self):
            self.M = {"lanes": [{"pts": [list(map(list, p))][0], "w": 5} for p in polys], "houses": []}

        def lane(self, pts, **kw):
            self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("width", 5)})

    return _S()


class _StubSettlement:
    """The two things the web helpers touch on a Settlement: the manifest and `lane()`."""

    def __init__(self, lanes=(), houses=()):
        self.M = {
            "lanes": [{"pts": [list(q) for q in p], "w": 5, "connector": i == 0} for i, p in enumerate(lanes)],
            "houses": [{"x": x, "y": y, "w": 46.0, "h": 28.0, "rot": 0.0} for x, y in houses],
        }

    def lane(self, pts, **kw):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("width", 5)})

    def reink_lane(self, i):
        pass  # the stub has no ink; the record is what the helpers are tested on


# ---- feature 146: the track's fallbacks, which no cohort seed has needed --------------------------------


def _walled_settlement() -> tuple[object, object]:
    """A Settlement whose homesteads form a WALL across the middle of the canvas, so a run from north to
    south cannot go straight and cannot be clipped clear - the case `_thread_the_fabric`'s detour exists for."""
    from l7r.diagram.settlement import Settlement

    from .._builders import a_plan

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    for i in range(14):  # SOLID: the footprints overlap, so no gap exists for the router to thread
        x = 60.0 + i * 100.0
        s.M["houses"].append({"x": x, "y": 700.0, "w": 140.0, "h": 90.0, "rot": 0})
    plan = a_plan()
    plan.envelope = [(50.0, 50.0), (1350.0, 50.0), (1350.0, 1350.0), (50.0, 1350.0)]
    return s, plan


def _webbed(lanes: list[dict[str, object]]) -> object:
    """A Settlement carrying `lanes` and their ink, ready for the smoothing pass."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    for ln in lanes:
        s.lane(list(ln["pts"]), width=int(ln.get("w", 5)))  # type: ignore[arg-type]
    return s


# ---- feature 134 T50: the three lane-web defects T49's rolled yard sizes exposed ----------------

# A hairpin whose short HEAD runs back west along y=300 while the rest of the lane runs west along
# y=318, with a bar between them so the chord over the fold is blocked and the arm cut is the only
# way out. The apex is (702, 300); cutting the head leaves the apex as the lane's new end.
_HAIRPIN = [[620.0, 300.0], [702.0, 300.0], [630.0, 318.0], [560.0, 318.0]]  # head 82 ft: past _ARM_FT, inside _LONG_ARM_FT
_LONG_HAIRPIN = [[602.0, 300.0], [702.0, 300.0], [630.0, 318.0], [560.0, 318.0]]  # head 100 ft: past _LONG_ARM_FT
_FOLD_BAR = [[(560.0, 306.0), (700.0, 306.0), (700.0, 312.0), (560.0, 312.0)]]
_TIP_WAY = {"pts": [[728.0, 272.0], [790.0, 272.0]], "w": 5}  # 38 ft off the apex - inside _END_WAY_FT


# ---------------------------------------------------------------------------------------------
# THE WEB PASSES, ASKED WITH PLAIN DICTS (feature 146, GM 2026-08-28 on testability). `_touch_junctions`
# and `_join_piece` take a Settlement, but between them they touch only `M` and `reink_lane` - so a
# four-line stub reaches arms that a rolled map only enters on the seeds where the geometry conspires.
# ---------------------------------------------------------------------------------------------


class _StubWeb:
    """The two members of `Settlement` the web passes actually use."""

    def __init__(self, **M: object) -> None:
        self.M: dict = {"meta": {}, "lanes": [], "houses": [], **M}
        self.reinked: list[int] = []

    def reink_lane(self, i: int) -> None:
        self.reinked.append(i)


def _hamlet_for_ways():
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=True)
    return s
