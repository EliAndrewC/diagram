"""THE POOL TESTS A LATER PYTHON STAGE FAILS ON THE RUST OUTPUT, held strict until that stage's port (feature 444 FR-019, the
round arbiter's ruling on ask:444-T16-pool-python-stages).

WHY. A landing that changes a Rust stage is judged by the Rust gate alone, and a Python stage that fails on the Rust output is
that stage's defect, never a reason to change the Rust stage (FR-019; the GM on 444#1, 2026-11-01: "it's okay for the Python
code to have errors since we will fix those when those stages are ported to Rust"). The gate's pool tests read the whole
pipeline, so each test a later stage fails is marked here by its id, `xfail(strict=True)` with the stage that owes it: the day
the stage's port makes it pass, the strict mark fails the gate and comes off. `tests/conftest.py` applies the table; every row
was checked to pass on main before the Rust field moved it. Nothing here goes on FR-020's failing list, the Rust stages' alone.
"""

from __future__ import annotations

_SEAT = "Sawada (seed 24) refuses at the seating (cluster.seat_cluster, SeatRefused) on the Rust field - the seating's port (444 FR-019)"
_MARSH = "Inashiro's toe marsh drawn with sharp corners on the Rust field's edge - the waterward marsh's port (444 FR-019)"
_BAMBOO = "a bamboo stand seated off Kashikawa's sheet on the Rust field and sink (T26) - the bamboo stage's port (444 FR-019)"
_PLANKS = "two footplanks seated side by side where the Rust field writes the canal's legs as separate ditches - the footplank placer's port (444 FR-019)"

#: test id (as pytest names it, from the repository root) -> the Python stage that owes it
WAITING: dict[str, str] = {
    "tests/full/test_villages.py::test_village_passes_gate[sawada.gen.py]": _SEAT,
    "tests/gate/test_board_facing.py::test_an_entrance_board_on_its_approach_is_squared_to_it[sawada]": _SEAT,
    "tests/gate/test_canopy_sun.py::test_no_bamboo_shades_a_yard_or_a_bed[sawada]": _SEAT,
    "tests/gate/test_canopy_sun.py::test_no_canopy_tree_shades_a_yard_or_a_bed[sawada]": _SEAT,
    "tests/gate/test_covers_298.py::test_the_covers_are_tiles_at_the_bottom_and_leave_the_clearings_bare[sawada.gen.py]": _SEAT,
    "tests/gate/test_field_302.py::test_every_shipped_comb_field_leaves_no_bare_ground": _SEAT,
    "tests/gate/test_review_rules_294.py::test_every_class_answers_the_pointer_over_its_own_ink[sawada.gen.py]": _SEAT,
    "tests/gate/test_review_rules_294.py::test_every_see_through_mark_is_declared[sawada.gen.py]": _SEAT,
    "tests/gate/test_review_rules_294.py::test_no_marsh_meets_open_ground_on_a_ruled_line[sawada.gen.py]": _SEAT,
    "tests/gate/test_review_rules_294.py::test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge[sawada.gen.py]": _SEAT,
    "tests/gate/test_scatter_frame.py::test_no_stage_after_the_view_is_decided_moves_the_frame[sawada.gen.py]": _SEAT,
    "tests/gate/test_wood_shares_planted.py::test_every_reserved_wood_seat_is_planted_where_it_was_reserved[sawada]": _SEAT,
    "tests/gate/test_covers_298.py::test_inashiros_toe_marsh_has_no_laid_corner_or_straight_run": _MARSH,
    "tests/gate/test_review_rules_294.py::test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge[inashiro.gen.py]": _PLANKS,
    "tests/gate/test_review_rules_294.py::test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge[kashikawa.gen.py]": _PLANKS,
    "tests/gate/test_review_rules_294.py::test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge[kuwabata.gen.py]": _PLANKS,
    "tests/hamletgen/test_pool_261.py::test_every_bamboo_stand_is_on_the_sheet[kashikawa]": _BAMBOO,
}
