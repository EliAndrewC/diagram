"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _fort_city,
    f,
    f_only,
)


def test_log_boom_checks_fire_on_the_mid_stream_chain_and_pass_on_a_bank_pen():
    # GM 2026-08-02 (Minami): "it just looks like a bunch of logs in the middle of the river."
    # The pre-fix boom floated mid-channel - adrift AND crowding the fairway (the real capture is
    # frozen in pool/regressions/). The redesigned pen hugs the near bank (bank on local +y; rot 90
    # turns +y toward the west shore), takes a third of the channel, and leaves the fairway clear.
    river = {"pts": [[900, 100], [900, 900]], "w": 40}  # centerline x900, banks x880/x920
    fire = _fort_city(river=river, log_booms=[{"x": 900, "y": 500, "rot": 90, "len": 100}])  # pre-2026-08 record shape: no pen_w
    hits = f(fire)
    assert "log_boom_moored_to_the_bank" in hits and "log_boom_leaves_the_fairway" in hits
    ok = _fort_city(river=river, log_booms=[{"x": 886.6, "y": 500, "rot": 90, "len": 100, "pen_w": 13.3}])
    hits2 = f(ok)
    assert "log_boom_moored_to_the_bank" not in hits2 and "log_boom_leaves_the_fairway" not in hits2
    # teeth against a center-collapse: the ok pen's CENTER sits 13.4px off the centerline (a center
    # measure would read it 6.7px off the bank line and condemn it) while the fire chain's center is
    # exactly ON the centerline - only the derived corners judge both correctly


def test_log_boom_serves_the_lumber_yard_ties_pen_to_yard():
    # boom and zaimokuya are one works: the pen is the yard's waterside holding ground
    river = {"pts": [[900, 100], [900, 900]], "w": 40}
    pen = [{"x": 886.6, "y": 500, "rot": 90, "len": 100, "pen_w": 13.3}]
    near = _fort_city(river=river, log_booms=pen, lumber_yards=[{"x": 940, "y": 520, "w": 30, "h": 20, "rot": 0, "label": "lumber yard"}])
    assert "log_boom_serves_the_lumber_yard" not in f_only(near, "log_boom_serves_the_lumber_yard")
    far = _fort_city(river=river, log_booms=pen, lumber_yards=[{"x": 400, "y": 400, "w": 30, "h": 20, "rot": 0, "label": "lumber yard"}])
    assert "log_boom_serves_the_lumber_yard" in f_only(far, "log_boom_serves_the_lumber_yard")
