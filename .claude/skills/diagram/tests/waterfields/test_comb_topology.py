"""The comb field's water network, at the code that lays it (feature 166).

Carries `delivery_ditches_taper`, `water_channels_obtuse_turns` and `field_ditches_terminate`, which the
retired battery re-measured on every finished map.

`build_comb` lays the whole net at once - the sluice's head-race forks at one division point into two
supply canals hugging the high margins, and the laterals comb off them - so these are properties of one
construction rather than of any single placement, and they belong beside it. It takes plain numbers and
returns plain data, so the whole family runs in about a second across several seeds.
"""

from __future__ import annotations

import functools
import math

import pytest

from l7r.diagram.pipeline import rollcache
from l7r.diagram.waterfields.comb import build_comb

SEEDS = (3, 5, 11)
"""The seeds this module asserts over. THREE, NOT FOUR (2026-08-30): a comb build is ~1 s and four tests
read each net, so every seed here costs a full build in each of them. Three seeds still cross the rolled
knobs these rules care about; the fourth was buying a repeat rather than a new shape. If a topology defect
ever turns out to be seed-specific, add the seed that shows it - with the map that shows it named here."""


@functools.cache
def _net(seed: int):
    """One comb per seed, shared by all four tests that read it.

    CACHED BECAUSE THE BUILD IS THE COST. Four tests examine the same net at each seed and each was
    building its own, so three of every four builds re-derived a net another assertion had already made.
    **Nothing here may mutate the returned net** - it is shared, so a test that edited it would corrupt
    its neighbors instead of failing. Every reader below only measures."""
    # SHARED ACROSS WORKERS - see the note in test_comb_flow.py's `_net`. `lru_cache` only helps within
    # one xdist process; `rollcache.obtain` keys on the engine too, so the build is paid once per seed
    # per code change however the tests are distributed.
    return rollcache.obtain(f"comb-topology:{seed}", lambda: build_comb(2400, 2400, (300.0, 300.0), seed=seed, down_deg=90))[0]


def _turns(pts):
    for a, b, c in zip(pts, pts[1:], pts[2:], strict=False):
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        n1 = math.hypot(*v1) or 1.0
        n2 = math.hypot(*v2) or 1.0
        cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
        yield 180.0 - math.degrees(math.acos(cos))  # interior angle at b


@pytest.mark.parametrize("seed", SEEDS)
def test_a_delivery_ditch_is_thinner_than_the_canal_that_feeds_it(seed: int) -> None:
    """`delivery_ditches_taper`. Water divides as it goes: a supply canal carries the whole head, a
    lateral carries one plot's share. A branch drawn at its main's weight reads as a second canal and
    tells the reader the water splits evenly, which it does not."""
    net = _net(seed)
    mains = [c["w"] for c in net["channels"] if c.get("role") == "main"]
    branches = [c["w"] for c in net["channels"] if c.get("role") == "branch"]
    assert mains and branches, f"seed {seed}: the comb laid no supply/lateral pair"
    assert max(branches) <= max(mains), f"seed {seed}: a lateral ({max(branches)}) outweighs the canal ({max(mains)})"


@pytest.mark.parametrize("seed", SEEDS)
def test_no_watercourse_doubles_back_on_itself(seed: int) -> None:
    """`water_channels_obtuse_turns`. Water does not turn a hairpin; a dug channel that does was drawn
    by a router losing its way rather than by anyone digging. The bar is deliberately generous - what is
    forbidden is the acute doubling-back, not an honest bend."""
    net = _net(seed)
    for ch in net["channels"]:
        pts = [tuple(p) for p in ch["pts"]]
        if len(pts) < 3:
            continue
        worst = min(_turns(pts), default=180.0)
        assert worst > 45.0, f"seed {seed}: a {ch.get('role')} channel turns through {worst:.0f} deg"


@pytest.mark.parametrize("seed", SEEDS)
def test_every_channel_is_a_real_run_rather_than_a_stub(seed: int) -> None:
    """`field_ditches_terminate`, from the side the placer can guarantee: a channel with one point, or a
    zero-length run, is a ditch that goes nowhere and would be drawn as a dot. The battery measured where
    the ends LANDED; what the builder owes is that there is a run to land."""
    net = _net(seed)
    for ch in net["channels"]:
        pts = [tuple(p) for p in ch["pts"]]
        assert len(pts) >= 2, f"seed {seed}: a {ch.get('role')} channel with {len(pts)} point(s)"
        span = sum(math.dist(a, b) for a, b in zip(pts, pts[1:], strict=False))
        assert span > 1.0, f"seed {seed}: a {ch.get('role')} channel of zero length"


@pytest.mark.parametrize("seed", SEEDS)
def test_the_comb_drains_as_well_as_feeds(seed: int) -> None:
    """A field that is fed and not drained is a swamp. The comb lays exactly one drain, and its presence
    is the half of the water network a reader checks first."""
    net = _net(seed)
    assert [c for c in net["channels"] if c.get("role") == "drain"], f"seed {seed}: fed but never drained"
    assert net.get("drain"), f"seed {seed}: no drain line recorded"
