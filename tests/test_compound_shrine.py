"""The compound shrine in its corner beside its tree (feature 374 wave 130): research/questions/0218-the-compounds-own-
shrine-yashikigami.drawing.html - "Every compound our maps draw has one modest shrine, in a corner of its grounds beside a
tree"."""

from __future__ import annotations

from l7r.diagram import compound as c
from l7r.diagram import compound_parts as cp


def _shrine(wall: str = "E", tree_ft: float = 0.0) -> c.BuildingSpec:
    return c.BuildingSpec("shrine", "shrine", 18.0, 14.0, "inner", wall, 4, feature="compound shrine", tree_ft=tree_ft)


def test_a_building_holds_its_tree_ground_past_its_far_end() -> None:
    """The next building on the shrine's wall flows below the ground held for its tree."""
    env = c.Envelope(120.0, 120.0, 100.0, 10.0)
    store = c.BuildingSpec("store", "service", 18.0, 14.0, "inner", "E", 1, feature="storehouse")
    prog = c.CompoundProgram("t", env, (), (_shrine(tree_ft=17.0), store))
    by = {p.spec.name: p for p in c.place(prog).placed}
    assert by["shrine"].y_ft == c.WALL_MARGIN_FT
    assert by["store"].y_ft == by["shrine"].y2 + 17.0 + c.FIRE_GAP_FT
    held = c.BuildingSpec("row", "service", 30.0, 10.0, "inner", "N", 1, feature="storehouse", tree_ft=10.0)
    later = c.BuildingSpec("hut", "service", 10.0, 10.0, "inner", "N", 0, feature="storehouse")
    by = {p.spec.name: p for p in c.place(c.CompoundProgram("t", env, (), (held, later))).placed}
    assert by["hut"].x_ft == by["row"].x2 + 10.0 + c.FIRE_GAP_FT, "on a north wall it is held east of the far end"


def test_the_shrine_tree_stands_off_an_end_face_toward_the_wall() -> None:
    env = c.Envelope(120.0, 120.0, 100.0, 10.0)
    result = c.place(c.CompoundProgram("t", env, (), (_shrine(tree_ft=17.0),)))
    shrine = result.placed[0]
    taken = [(shrine.x_ft, shrine.y_ft, shrine.x2, shrine.y2)]
    tx, ty = cp._shrine_tree(env, result, taken) or (0.0, 0.0)
    r = cp.SHRINE_TREE_CROWN_FT / 2
    assert ty == shrine.y2 + r + cp.SHRINE_TREE_CLEAR_FT, "below its south end"
    assert tx + r <= env.w_ft - cp.SHRINE_TREE_CLEAR_FT and abs(tx - shrine.x_ft) <= shrine.spec.w_ft


def test_no_shrine_or_no_clear_ground_seats_no_tree() -> None:
    env = c.Envelope(120.0, 120.0, 100.0, 10.0)
    assert cp._shrine_tree(env, c.PlaceResult(envelope=env), []) is None
    result = c.place(c.CompoundProgram("t", env, (), (_shrine(),)))
    assert cp._shrine_tree(env, result, [(0.0, 0.0, 120.0, 120.0)]) is None, "everything taken"


def test_the_county_shrine_stands_in_its_corner_beside_its_tree() -> None:
    from l7r.diagram.tools.pack_audit.shared import shrine_tree

    prog = c.county_magistracy_program()
    result = c.place(prog)
    shrine = next(p for p in result.placed if p.spec.feature == "compound shrine")
    env = result.envelope
    assert env is not None
    assert shrine.y_ft == c.WALL_MARGIN_FT and env.w_ft - shrine.x2 <= c.WALL_MARGIN_FT + 0.5, "the north-east corner"
    svg = c.emit_svg(prog, result)
    assert 'data-kind="sacred tree" data-part-of="compound shrine"' in svg
    assert shrine_tree(svg) == []


def test_the_county_vegetable_garden_takes_its_rolled_site_at_the_plots_size() -> None:
    """Feature 374 wave 129 (T21's plan review): the site rolled among 0109's four, the ruled-out struck first; the plot at
    the Takei house's ~1,076 sq ft."""
    from l7r.diagram import compound_example as ce

    open_sites = [site for site in ce.GARDEN_SITES if ce.GARDEN_SITE_RULED_OUT[site] is None]
    assert open_sites == ["west of the residence", "on a parcel of its own"] and ce.GARDEN_SITE == "west of the residence"
    west = ce.garden_zones("west of the residence")
    assert [z.name for z in west] == ["vegetable garden", "service yard"] and west[0].w_ft * west[0].h_ft == 1080.0
    assert [z.name for z in ce.garden_zones("on a parcel of its own")] == ["service yard"], "the field outside the walls"
    assert "service yard" in c.UNFENCED_ZONES and c.ZONE_KINDS["service yard"] == "inner court"


def test_flush_boxes_share_their_pixel_edge_at_a_half_pixel_origin() -> None:
    """Feature 374 wave 134: rounding a box's origin and size apart parted two boxes flush in feet by a pixel."""
    hall = c._px_edges(0.0, 0.0, 0.0, 92.5, 10.0, 38.0)
    seat = c._px_edges(0.0, 0.0, 0.0, 125.5, 10.0, 5.0)
    assert hall[3] == seat[3] == 392  # 130.5 ft -> 391.5 px, half up
    assert c._px_edges(0.0, 0.0, 3.5, 0.0, 5.0, 5.0) == (11, 0, 26, 15)  # 10.5 -> 11, 25.5 -> 26: still 15 px wide
