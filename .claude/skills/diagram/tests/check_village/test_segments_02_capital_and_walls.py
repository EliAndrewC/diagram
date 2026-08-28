"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    f,
)


def test_city_fan_heads_quilted_moat_exclusion_and_degenerate_segments():
    """Branch coverage for the head-band sampler: a duplicated main vertex (zero-length segment)
    is skipped, and flank samples inside the moat corridor are excluded rather than counted bare
    (the moat legitimately borders a city fan's head where the sluice taps it)."""
    M = {
        "meta": {"scale": "village", "ftpx": 2},
        "moat": [[100, -50], [100, 450]],
        "moat_width": 30,
        "fields": [{"name": "t", "kind": "paddy", "outline": [[0, 0], [400, 0], [400, 400], [0, 400]], "bbox": [0, 0, 400, 400], "plot_polys": [[[60, 0], [400, 0], [400, 400], [60, 400]]]}],
        "field_ditches": [{"field": "t", "poly": [[112, 0], [112, 200], [112, 200], [112, 400]], "w": 6, "role": "main"}],
    }
    f(M)  # execution is the point: west flank samples sit in the moat corridor, the duplicate vertex is skipped
