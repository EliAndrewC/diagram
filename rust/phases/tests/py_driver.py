"""The phases module's Python callers, as `plan_site` calls it (feature 444 T19): what Python reaches through the extension, counted
by `rust_checks.py cover` beside the crate's own tests."""

import l7r_phases

knobs = [
    ("settlement_form", 3, False, "all"),
    ("well_siting", 2, False, "nucleated"),
    ("row_line", 2, False, "linear"),
    ("copse_siting", 1, False, "all"),
    ("plot_size", 3, True, "all"),
    ("intake", 2, False, "off"),
]
for seed in range(12):
    fall, picks, counts = l7r_phases.stage_water_frame(seed, "NW", seed % 2 == 0, seed % 5 == 0, ["nucleated", "linear", "dispersed"], knobs)
    assert fall is None or fall in (0.0, 45.0, 90.0, 135.0, 315.0), fall
    assert len(picks) == len(knobs) and picks[4] is None and picks[5] is None
    assert sum(counts.values()) >= 9
for quarter in ("N", "NE", "E", "SE", "S", "SW", "W", "NW"):
    assert l7r_phases.admitted_falls(quarter, False) and l7r_phases.admitted_falls(quarter, True)
