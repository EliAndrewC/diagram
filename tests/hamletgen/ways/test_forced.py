"""`hamletgen/ways/forced.py`: a turn or a meeting the ground forces breaks no angle rule of the lane law (feature 385 T01,
plan D2; 384's User Story 0: "the needle and fold rules admit a meeting whose wider approach is blocked by a mapped feature").

Each rule on a constructed web twice: with a house standing across the straighter way (forced - lawful) and without it (a
fault, as before). Every case reads the law's own registry (`law.LAW`), so each is red on the law before feature 385, which
refused the shape wherever it stood."""

from l7r.diagram.hamletgen.ways import forced, law


def _ln(*pts, **kw):
    return {"pts": [list(q) for q in pts], "w": 3, "worn": True, **kw}


def _M(lanes, *houses):
    return {"lanes": lanes, "houses": [{"x": x, "y": y, "w": w, "h": h, "rot": 0.0} for x, y, w, h in houses], "meta": {"ftpx": 1.0}}


def test_a_needle_with_a_house_in_its_sliver_is_a_path_round_the_house() -> None:
    lanes = [_ln((0.0, 0.0), (300.0, 0.0)), _ln((200.0, 40.0), (60.0, 2.0))]  # ~15 degrees onto the way
    assert law.LAW["needle_joins"](_M(lanes)), "over open grass: a needle, as before"
    assert law.LAW["needle_joins"](_M(lanes, (130.0, 10.0, 60.0, 8.0))) == [], "a house in the sliver forces it"


def test_a_folded_joint_round_a_house_is_walked_as_it_stands() -> None:
    lanes = [_ln((0.0, 0.0), (100.0, 0.0)), _ln((100.0, 0.0), (20.0, 20.0))]  # back on itself at the joint
    assert law.LAW["folded_joints"](_M(lanes)), "folded over open grass"
    assert law.LAW["folded_joints"](_M(lanes, (10.0, 12.0, 14.0, 10.0))) == [], "the chord past the fold runs through a house"


def test_a_zigzag_and_a_hook_round_a_house_are_the_way_round_it() -> None:
    zig = [_ln((0.0, 0.0), (100.0, 0.0), (110.0, 30.0), (200.0, 30.0))]
    assert law.LAW["bends"](_M(zig)), "two 70 degree turns 32 ft apart: a kink on open ground"
    assert law.LAW["bends"](_M(zig, (100.0, 15.0, 30.0, 10.0))) == [], "its chord crosses a house"
    hook = [_ln((0.0, 0.0), (100.0, 0.0), (95.0, 10.0))]
    assert law.LAW["hooks"](_M(hook)), "an 11 ft last leg turning back: a hook"
    assert law.LAW["hooks"](_M(hook, (60.0, 6.0, 20.0, 4.0))) == [], "round the corner of a house"


def test_a_hairpin_at_the_tracks_start_round_a_house() -> None:
    lanes = [_ln((0.0, 0.0), (-500.0, 0.0), connector=True), _ln((-60.0, 30.0), (10.0, 10.0), (0.0, 0.0))]
    assert law.LAW["connector_hairpins"](_M(lanes)), "back along the track over open grass"
    assert law.LAW["connector_hairpins"](_M(lanes, (-200.0, 7.0, 20.0, 10.0))) == [], "a house across the chord"


def test_no_ground_reads_as_the_law_did_and_the_ground_is_built_only_when_asked() -> None:
    assert not forced.forced_turn(None, (0.0, 0.0), (10.0, 0.0), 3.0) and not forced.forced_meeting(None, (0.0, 0.0), (10.0, 5.0), (0.0, 0.0), (20.0, 0.0), 3.0)
    M = _M([_ln((0.0, 0.0), (100.0, 0.0))])
    lazy = forced.lazy_ground(M)
    assert not forced._GROUND or all(g[0] is not M for g in forced._GROUND), "nothing built until asked"
    assert not lazy((0.0, 0.0), (0.0, 0.0), 3.0), "a point is no way to block"
    assert forced.ground(M) is forced.ground(M), "built once per manifest"
    before = forced.ground(M)
    M["houses"].append({"x": 50.0, "y": 50.0, "w": 10.0, "h": 10.0, "rot": 0.0})
    assert forced.ground(M) is not before, "a registry that grew is read again"
    assert forced.ground(M)((50.0, 30.0), (50.0, 70.0), 3.0) and not forced.ground(M)((0.0, 30.0), (0.0, 70.0), 3.0)
