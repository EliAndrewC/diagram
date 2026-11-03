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
brook = (105.0, 35.0, 70.0, 22.0, 34.0, 10.0, 20.0, 7.0)
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
    out = l7r_phases.stage_field(seed, 15, 90.0, 1.0, (3200.0, 3200.0), (6400.0, 6400.0), 1.0 if seed % 2 else -1.0, brook, ([0.30, 0.62, 0.93], [0.55]), weir, "medium", 1488.0, field_knobs)
    f = out["fields"][0]
    assert f["plots"] and f["channels"][0][0] == "main" and len(f["ring"]) > 20
    seen |= {p["state"] for p in f["plots"]} | {"weir" if f["weir"] else "open"} | {"pond" if f["pond"] else "-"} | {"grave" if f["grave"] else "-"}
    assert set(out["knobs"]) >= {"intake", "paddy_rest"} and len(out["grain"]) == 3 and out["counts"] is not None
assert {"green", "wet", "rest", "weir", "open"} <= seen, seen
# ...and a settlement past the single-field cap draws its fields side by side (each after the first laid beside the last)
wide = l7r_phases.stage_field(4, 220, 90.0, 1.0, (9000.0, 9000.0), (18000.0, 18000.0), 1.0, brook, ([0.30, 0.62, 0.93], [0.55]), weir, "medium", 1488.0, field_knobs)
assert len(wide["fields"]) >= 3, len(wide["fields"])
try:
    l7r_phases.stage_field(1, 15, 90.0, 1.0, (0.0, 0.0), (1000.0, 1000.0), 1.0, (105.0, 35.0, 70.0, 22.0, 34.0, 10.0, 20.0, 7.0), ([0.5], [0.5]), weir, "small_irregular", 1e9, field_knobs)
except ValueError as e:
    assert "the field refused" in str(e), e
else:
    raise AssertionError("a cell no basin can fill a quarter of is refused")

# a knob drawn as `Knob.roll` draws it: randrange on an even table, the running weight past random() on a weighted one
import hashlib  # noqa: E402
import random  # noqa: E402

for seed in range(20):
    rng = random.Random(int.from_bytes(hashlib.sha256(f"{seed}\x00paddy_rest".encode()).digest()[:8], "big"))
    u = rng.random() * 1.0
    want = 0 if u - 0.8 < 0 else 1
    assert l7r_phases.roll_knob(seed, "paddy_rest", 2, [0.8, 0.2]) == want
    rng = random.Random(int.from_bytes(hashlib.sha256(f"{seed}\x00weir_form".encode()).digest()[:8], "big"))
    assert l7r_phases.roll_knob(seed, "weir_form", 4, []) == rng.randrange(4)

# the polder (feature 444 T16 D8): a rice polder and a dike-pond block, as the thin `stage_field` calls it
for dike, layout in ((False, "mosaic"), (True, "mosaic"), (True, "chessboard")):
    p = l7r_phases.stage_polder(4, 15, dike, layout, 90.0, (3200.0, 3200.0), 1.0, (6400.0, 6400.0), True, (0.3, "rice", "fry_village", "tea" if layout == "chessboard" else "mulberry"))
    assert p["plots"] and all(len(x["ring"]) in (4, 6) for x in p["plots"]) and len(p["sluices"]) == 2
    assert p["dike"]["trees"] and len(p["outfall"]) == 3 and (("dikeponds" in p) == dike)
    assert dike or any(x["rest"] for x in p["plots"])
    assert p["ditches"][0][1] == "feeder" and len(p["pond"]) == 4 and p["counts"]["candidate@polder_shape"] == 4
    assert dike is (p["pocket_pond"] is None) or not dike

# a rice polder's low plot holds a pocket pond on some maps (0008); its host one of the low plots
ponds = [l7r_phases.stage_polder(s, 15, False, "mosaic", 90.0, (3200.0, 3200.0), 1.0, (6400.0, 6400.0), False, (0.5, "none", "none", "none")) for s in range(12)]
held = [p for p in ponds if p["pocket_pond"] is not None]
assert held and len(held) < len(ponds) and all(p["plots"][p["pocket_pond"][0]]["low"] for p in held)

# finish's bead settling: a run through a ditch is dropped, a dry one stands
assert l7r_phases.settle_runs([[(0.0, 0.0), (8.0, 0.0)]], [((4.0, -5.0), (4.0, 5.0), 9.0)], [])[0::2] == ([], 2)
assert l7r_phases.settle_runs([[(0.0, 0.0), (8.0, 0.0)]], [], [])[0::2] == ([[(0.0, 0.0), (8.0, 0.0)]], 0)

# a dike-pond's pond rounded from its parcel
d, pts = l7r_phases.rounded_pond([(0.0, 0.0), (200.0, 0.0), (200.0, 100.0), (0.0, 100.0)], 16.0, 16.0, 7)
assert d.startswith("M") and len(pts) == 13

# the sink stage (feature 444 T26), as the thin `stage_sink` calls it: a pond, an off-map run, a field with no collector, and a
# refusal named
field = [(1000.0, 800.0), (2600.0, 800.0), (2600.0, 2000.0), (1000.0, 2000.0)]
drain = [(1100.0, 1900.0), (1600.0, 1950.0), (2000.0, 1990.0)]
brook = [[700.0 + 3.0 * (k % 7), -10.0 + 20.0 * k] for k in range(211)]  # as the stream record holds it, lists
args = ((4000.0, 4000.0), (0.0, 1.0), 90.0, field, drain, brook, 5.25, 5.5, [], 44.0, 150.0)
pond = l7r_phases.stage_sink(True, *args)
assert pond["form"] == "pond" and pond["pond"] is not None and len(pond["reeds"]) == 16 and pond["counts"]
off = l7r_phases.stage_sink(False, *args)
assert off["form"] == "offmap" and off["pond"] is None
assert l7r_phases.stage_sink(True, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, [], brook, 5.25, 5.5, [], 44.0, 150.0) is None
across = [(-100.0 + 70.0 * k, 2100.0 + 0.5 * k) for k in range(61)]
band = [(-500.0, 2050.0), (4500.0, 2050.0), (4500.0, 2060.0), (-500.0, 2060.0)]
try:
    l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, drain, across, 5.25, 5.5, [band], 44.0, 1e9)
except ValueError as e:
    assert "resting basin" in str(e), e
else:
    raise AssertionError("a constructed route across a resting basin is refused by name")
joined = l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, drain, [(2150.0 + 3.0 * (k % 7), -10.0 + 20.0 * k) for k in range(211)], 5.25, 5.5, [], 44.0, 150.0)
assert joined["to"] == "stream" and joined["confluence"] is not None
up = [(2000.0, 1990.0), (2000.0, 1900.0)]
low = l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, up, [], 5.25, 5.5, [], 44.0, 150.0)["run"][-2]
twin = [(low[0] + 20.0, low[1] + 100.0 + 30.0 * k) for k in range(101)]
assert l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, up, twin, 5.25, 5.5, [], 44.0, 150.0)["to"] == "stream"
bent = [(low[0] - 600.0, low[1] + 400.0), (low[0], low[1] + 200.0), (low[0] + 600.0, low[1] + 400.0)]
assert l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, up, bent, 5.25, 5.5, [], 44.0, 150.0)["to"] == "stream"
outside = [(2000.0, 2200.0), (2000.0, 2100.0)]
assert l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, outside, [], 5.25, 5.5, [], 44.0, 150.0)["to"] == "offmap"
for top in (700.0, 900.0):
    skew = [(1000.0, 800.0), (2600.0, top), (2600.0, 1800.0), (1000.0, 2000.0)]
    l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 20.0, skew, [(2500.0, 1700.0), (2500.0, 1600.0)], [], 5.25, 5.5, [], 44.0, 150.0)
rest = [[(2040.0, 1992.0), (2400.0, 1992.0), (2400.0, 2300.0), (2040.0, 2300.0)]]
near = [(2150.0 + 3.0 * (k % 7), -10.0 + 20.0 * k) for k in range(211)]
assert l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, drain, near, 5.25, 5.5, rest, 44.0, 150.0)["confluence"] is None
north = [(1100.0, 900.0), (1600.0, 850.0), (2000.0, 810.0)]
l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, -1.0), 270.0, field, north, [], 5.25, 5.5, [], 44.0, 150.0)
l7r_phases.stage_sink(False, (4000.0, 4000.0), (-1.0, 0.0), 180.0, field, [(1100.0, 1100.0), (1050.0, 1500.0), (1010.0, 1900.0)], [], 5.25, 5.5, [], 44.0, 150.0)
try:
    l7r_phases.stage_sink(False, (4000.0, 4000.0), (0.0, 1.0), 90.0, field, [(3200.0, 2200.0), (3200.0, 2100.0)], [], 5.25, 5.5, [], 44.0, 150.0)
except ValueError as e:
    assert "55 degrees" in str(e), e
else:
    raise AssertionError("a constructed route turning past 55 degrees out of the collector is refused by name")
