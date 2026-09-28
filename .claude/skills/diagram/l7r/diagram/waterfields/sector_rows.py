"""A comb sector's three kinds of plot row, laid by `carve._carve_sector` in this order: the BODY (one quad per row and
sub-column), the CANAL-SIDE closers against the supply canal, and the CLOSING RANK on the drain collector.

Moved out of `carve.py` by feature 281, when the vertex memo took that file past the 1,000-line bar; `carve` imports every
name back. Statement order, RNG draw order and float-op order are exactly as they were (feature 110's rule for this
package's extractions)."""

import math
import random
from collections.abc import Callable
from typing import Any

from .banks import _TINT_END_FT, _TINT_MIN_APEX, dedup_ring, pointed_ring, tapers_to_a_point
from .frame import Poly, Pt, _f_at_u, _Frame, _pip
from .palette import FLOODED, RICE_GREENS

_BankAt = Callable[[float], float]
_EdgeFn = Callable[[float, int, int], Pt]


def _sector_body_rows(
    R: random.Random,
    rows: list[float],
    nsub: int,
    edge: _EdgeFn,
    bndAB: tuple[Callable[[float], Pt], Callable[[float], Pt]],
    W: float,
    H: float,
    g: float,
    spills: Callable[[Pt], bool],
    above: Callable[[Poly], bool],
    in_supply: Callable[[Poly], bool],
    plots: list[dict[str, Any]],
) -> None:
    """The sector's BODY: one quad per row x sub-column, dropped where it degenerates or breaks a water bound."""
    bndA, bndB = bndAB
    for k in range(len(rows) - 1):
        wk = min(math.dist(bndA(rows[k]), bndB(rows[k])), math.dist(bndA(rows[k + 1]), bndB(rows[k + 1])))
        if wk < 24 * g:
            continue
        n = nsub if wk / nsub >= 13 * g else max(1, int(wk // (44 * g)))  # canal-wedge rows: local
        for j in range(n):
            quad = [edge(rows[k], j, n), edge(rows[k], j + 1, n), edge(rows[k + 1], j + 1, n), edge(rows[k + 1], j, n)]
            if math.dist(quad[0], quad[1]) < 12 * g or math.dist(quad[1], quad[2]) < 12 * g:
                continue
            if any(pq[0] < 8 or pq[0] > W - 8 or pq[1] > H - 8 or pq[1] < 8 for pq in quad):
                continue
            if any(spills(pq) for pq in quad) or above(quad) or in_supply(quad):
                continue
            # CROP: within the irrigated command area everything is RICE (paddy land was
            # too valuable for anything else - dry crops belong on ground the water cannot
            # command: above the canal / the village fringe, added in later stages; soy
            # grows on the bunds as aze-mame, not as plots). One village = one transplant
            # = one growth stage, so the field reads as ONE green. FLOODED (blue) accents
            # are reserved ENTIRELY for the closing rank (added below), which sits ON the
            # drain collector - so every blue plot literally drains into the southern ditch
            # and none can read as a stranded reservoir. The body is uniformly rice-green.
            fill = R.choice(RICE_GREENS)
            plots.append({"poly": [(round(pq[0], 1), round(pq[1], 1)) for pq in quad], "fill": fill})


def _sector_canal_closers(
    R: random.Random,
    rows: list[float],
    nsub: int,
    edge: _EdgeFn,
    f0AB: tuple[float, float],
    F: _Frame,
    a_pts: Poly,
    W: float,
    H: float,
    g: float,
    in_supply: Callable[[Poly], bool],
    plots: list[dict[str, Any]],
    sector_start: int,
) -> None:
    """CANAL-SIDE closers: the head plots run up against the supply canal - only a
    narrow berm remains. These are the plots that take water DIRECTLY from the
    canal through bund cuts (the first link of every cascade chain); a wide bare
    gap below a supply canal would be wasted prime land. Top edges follow the
    canal line (sloped, like the drain closers), bottoms sit on the row grid."""
    for j in range(nsub):
        fprobe = max(f0AB[0], f0AB[1]) + 12 * g  # sample where the subcolumns are spread out
        fc0 = _f_at_u(F, a_pts, F.to_uf(*edge(fprobe, j, nsub))[0])
        fc1 = _f_at_u(F, a_pts, F.to_uf(*edge(fprobe, j + 1, nsub))[0])
        if fc0 is None or fc1 is None:
            continue
        t0, t1 = fc0 + 5 * g, fc1 + 5 * g
        ks = [k for k in range(len(rows)) if rows[k] >= max(t0, t1) + 6 * g]
        if not ks:
            continue
        fb = rows[ks[0]]
        _ct = (2 if g < 1.0 else 8) * g  # relaxed minima at coarse grains ONLY: village output is GM-vetted and stays byte-identical (g=1 keeps the originals)
        if fb - min(t0, t1) > 78 * g or fb - max(t0, t1) < _ct:
            continue  # no gap here / top boundary is not the canal (at coarse grain a thin FAR side is fine - the quad degrades to a wedge)
        quad = [edge(t0, j, nsub), edge(t1, j + 1, nsub), edge(fb, j + 1, nsub), edge(fb, j, nsub)]
        if math.dist(quad[0], quad[1]) < (6 if g < 1.0 else 12) * g or math.dist(quad[1], quad[2]) < (2 if g < 1.0 else 6) * g:
            continue  # min top edge 6*g at coarse grains (12*g at the vetted village grain): the city fans' narrow head sub-columns dropped 3 of nw1's 5 closers, leaving the bare canal-head band (2026-07-21)
        if any(pq[0] < 8 or pq[0] > W - 8 or pq[1] > H - 8 or pq[1] < 8 for pq in quad):
            continue
        cx = sum(pq[0] for pq in quad) / 4
        cy = sum(pq[1] for pq in quad) / 4
        if any(_pip(cx, cy, pl["poly"]) for pl in plots[sector_start:]):
            continue  # this ground already planted (fork wedges)
        if in_supply(quad):
            continue  # a head closer wedged between a canal and its offtake - no bank to sit on
        plots.append({"poly": [(round(pq[0], 1), round(pq[1], 1)) for pq in quad], "fill": R.choice(RICE_GREENS)})


def _sector_closing_rank(
    R: random.Random,
    rows: list[float],
    nsub: int,
    edge: _EdgeFn,
    drain_f_at: Callable[[float, int, int], float],
    F: _Frame,
    dpts: Poly,
    bank_at: _BankAt,
    chord: Callable[[float, float], tuple[float, float] | None],
    W: float,
    H: float,
    g: float,
    in_supply: Callable[[Poly], bool],
    plots: list[dict[str, Any]],
) -> None:
    """The CLOSING rank: hem EVERY column down onto the collector, so the whole field
    edge sits on the drain (no dry sliver between the bottom paddies and their outfall).
    The drain is diagonal, so the triangle between the uniform last regular row and the
    drain varies across the sector - each column is tiled to its OWN drain fall."""
    n = nsub
    ftop = rows[-1]

    def drain_meet(jj: int, ftop: float = ftop, n: int = n) -> float:
        """Fall where sub-bund line jj actually meets the drain - refined, because the
        bund drifts in u as it descends so the drain fall at the top sample is wrong."""
        fd = drain_f_at(ftop, jj, n)
        for _ in range(3):
            fd2 = _f_at_u(F, dpts, F.to_uf(*edge(fd, jj, n))[0])
            if fd2 is None:
                break
            fd = fd2
        return fd

    for j in range(n):
        fm0, fm1 = drain_meet(j), drain_meet(j + 1)  # where each sub-bund reaches the collector...
        fb0 = fm0 - bank_at(F.to_uf(*edge(fm0, j, n))[0])  # ...held off to its BANK there
        fb1 = fm1 - bank_at(F.to_uf(*edge(fm1, j + 1, n))[0])
        depth = max(fb0, fb1) - ftop
        if depth < 6 * g:
            continue
        nlev = max(1, round(depth / (34 * g)))  # keep closer plots ~one row tall
        for li in range(nlev):
            fa0 = ftop + (fb0 - ftop) * li / nlev
            fa1 = ftop + (fb1 - ftop) * li / nlev
            fz0 = ftop + (fb0 - ftop) * (li + 1) / nlev
            fz1 = ftop + (fb1 - ftop) * (li + 1) / nlev
            quad = [edge(fa0, j, n), edge(fa1, j + 1, n), edge(fz1, j + 1, n), edge(fz0, j, n)]
            abuts = li == nlev - 1
            if abuts:
                # snap the bottom edge onto the collector's BANK so the field edge lies along
                # the ditch - as ONE straight bund clearing the whole span (bank_chord), not
                # two independently-snapped vertices, which cut the corner at every bend
                u3, u2 = F.to_uf(*quad[3])[0], F.to_uf(*quad[2])[0]
                ch = chord(u3, u2)
                if ch is not None:
                    quad[3], quad[2] = F.to_xy(u3, ch[0]), F.to_xy(u2, ch[1])
            if math.dist(quad[0], quad[1]) < 8 * g:
                continue
            if any(pq[0] < 8 or pq[0] > W - 8 or pq[1] > H - 8 or pq[1] < 8 for pq in quad):
                continue
            if in_supply(quad):
                continue  # a closing-rank corner wedged against a ditch tail - no bank to sit on
            # only the level whose BOTTOM edge lies on the collector floods (the wettest,
            # lowest ground); an upper split level cascades into it and stays green - so a
            # blue plot always abuts the drain
            fill = FLOODED if (abuts and R.random() < 0.45) else R.choice(RICE_GREENS)
            # TWO RINGS: the gate's own (`dedup_ring(r, 1.0)`, which `flooded_plots_read_as_basins`
            # reads at 15 deg - so 25 here keeps the placer strictly stricter on the SAME
            # measurement), plus the END-WIDTH collapse, which catches the needle truncated a few
            # feet short of its point that no interior angle on the 1.0 ring can see (_TINT_END_FT).
            if fill == FLOODED and (pointed_ring(dedup_ring(quad, 1.0), _TINT_MIN_APEX) or tapers_to_a_point(quad, _TINT_END_FT * g / 2, _TINT_MIN_APEX, 4 * _TINT_END_FT * g / 2)):
                # A POINTED SLIVER MUST NOT WEAR THE WATER TINT (known-open ledger 2026-08-16):
                # at a fan seam the converging closing-rank sub-columns taper to needle apexes,
                # and a blue one reads as a tiny triangular pond. Demote to a rice green picked
                # by POSITION. The load-bearing half is the ABSENT DRAW - indexing rather than
                # calling R leaves the RNG stream unmoved, so demoting one plot cannot re-roll every
                # plot after it. (The index buys no variety today: `RICE_GREENS` currently holds the
                # same color three times. Keep the indexing anyway - it is what makes the demotion
                # free, and it is already correct if the palette ever gains real shades.);
                # `low` is untouched - the tint is only the picture (feature 010). The quad is
                # DEDUPED first: the recorder merges sub-1 px collapsed edges before the ring is
                # written, and a quad with a collapsed edge carries near-90 deg corner angles
                # while its merged triangle carries the needle apex - testing the raw quad let 3
                # cohort seeds ship tinted needles the gate then caught (the split-predicate
                # trap, caught by the 48-seed sweep 2026-08-16).
                fill = RICE_GREENS[(int(abs(quad[0][0]) * 7) + int(abs(quad[0][1]) * 3)) % len(RICE_GREENS)]
            # `low` is the TOPOGRAPHY; `fill` is only the PICTURE. FLOODED tints a random 45% of the
            # bottom level blue for texture, so it is not the low ground - it is a sample of it. The
            # land-use overlays must key off `low`, never off the tint (feature 010).
            # The band is the bottom TWO levels, not just the one on the drain: a real valley bottom
            # has a wet backswamp with width, not a one-plot hem. Its exact extent is unrecorded, so
            # this is a CALIBRATED LIBERTY (constitution XII) - see the note in `apply_land_use`.
            plots.append({"poly": [(round(pq[0], 1), round(pq[1], 1)) for pq in quad], "fill": fill, "low": li >= nlev - 2})
