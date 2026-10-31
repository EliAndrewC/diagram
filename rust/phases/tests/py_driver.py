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

# the field stage (feature 444 T16), as the thin `stage_field` calls it: a weir hamlet and an open one, and a refusal named
brook = (105.0, 35.0, 70.0, 22.0, 34.0, 10.0, 35.0, 400.0, 7.0)
field_knobs = [
    ("intake", ["weir", "open"], [], None),
    ("weir_form", ["fence", "gabion", "frame", "crib"], [], None),
    ("paddy_rest", ["settled", "unsettled"], [0.8, 0.2], "unsettled"),
    ("winter_crop", ["barley", "none"], [0.5, 0.5], None),
    ("fan_middle", ["wild", "cleared"], [0.75, 0.25], None),
    ("grave_form", ["island", "corner"], [], None),
]
weir = (7.0, 30.0, {"fence": 1.5, "gabion": 2.0, "frame": 5.0, "crib": 5.0})
seen = set()
for seed in range(8):
    out = l7r_phases.stage_field(seed, 15, 90.0, 1.0, (3200.0, 3200.0), 1.0 if seed % 2 else -1.0, brook, ([0.30, 0.62, 0.93], [0.55]), weir, 1488.0, field_knobs)
    f = out["fields"][0]
    assert f["plots"] and f["channels"][0][0] == "main" and len(f["ring"]) > 20
    seen |= {p["state"] for p in f["plots"]} | {"weir" if f["weir"] else "open"} | {"pond" if f["pond"] else "-"} | {"grave" if f["grave"] else "-"}
    assert set(out["knobs"]) >= {"intake", "paddy_rest"} and len(out["grain"]) == 3 and out["counts"] is not None
assert {"green", "wet", "rest", "weir", "open"} <= seen, seen
try:
    l7r_phases.stage_field(1, 15, 90.0, 1.0, (0.0, 0.0), 1.0, (105.0, 35.0, 70.0, 22.0, 34.0, 10.0, 35.0, 400.0, 7.0), ([0.5], [0.5]), weir, 1e9, field_knobs)
except ValueError as e:
    assert "the field refused" in str(e), e
else:
    raise AssertionError("a cell no basin can fill a quarter of is refused")
