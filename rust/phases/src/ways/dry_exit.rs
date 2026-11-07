//! The dry exit (feature 444 T30): where no bearing of the track's sweep is dry and clear of the steadings, a track off the canvas
//! over ground it may stand on, found by a flood fill over a grid and string-pulled back to a few legs (`ways/dry_exit.py`
//! `dry_exit`, `ways/track.py` `connector_dry_exit`). A cell is walkable when its center stands farther than its wall's margin plus
//! half its diagonal from every wall and a cell off every water line, and a pulled leg is kept only where every sample along it
//! falls in a walkable cell, so the path found and the path returned answer the same question.
//!
//! Research:
//!     flood fill and rasterizing - NONE
//!     dry exit off the wet - research/questions/0081-village-lanes.drawing.html: walled by the marsh, the steadings and the field
//!     the track off the steadings - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html, research/questions/0081-village-lanes.drawing.html: 7 ft off every steading (`TRACK_FABRIC_GAP`), a lane's middle off a garden fence
//!     the track off the wet - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground (a convention there, no distance given); the 8 ft is ours; the wet ground grown 8 ft (`wet_grown_by_the_lane`)
//!     pond berth - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); 80 ft past the pond's larger half-axis
//!     a drawn channel crossed on a deck - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: where a way crosses a stream or ditch the map draws a timber deck as wide as the way (the settle seats it)
//!     a channel crossed last - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); the fill crosses a drawn channel only where no way out keeps to the ground between them; 0084 does not say when a way crosses a ditch rather than going round
//!     where on a channel it crosses - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass D, 2026-10-25); anywhere the fill finds; the crossing is squared as the track is laid (`squaring.square_run`)
//!     the track's flank - research/questions/0081-village-lanes.drawing.html: it leaves downslope past the end of the wet ground, on the flank the cluster already sits on - the fill takes the shortest way off any frame edge instead, a known gap carried to 405 T111
//!     only the brook gapped at its crossing places - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the crossing places stand on the brook; a drawn channel or the drain is crossed only as the last resort (on a deck, 0084)
//!     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.71 (half a cell's diagonal); 16 (16-gon for the pond disc)
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names, and grid indices of a few thousand"
)]

use super::Counts;
use std::collections::HashMap;

use super::track::{edge_dist, grown, in_poly, seg_dist, Pond, FABRIC_GAP_FT, WET_GROWN_FT};
use crate::field::fan::Pt;
use crate::seat::fords::{fords, gapped};

/// The fill's grid (ft): finer than any neck a track would use, coarse enough that a canvas of a few thousand feet is tens of
/// thousands of cells.
///
/// Research:
///     narrowest dry neck - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass D, 2026-10-25); a neck under 20 ft is not taken
pub const EXIT_CELL_FT: f64 = 20.0;

/// The fill's grid where farms carry their own groves (ft): fine enough that the 32 ft lane's room between two bands holds a
/// cell clear of both at the band gap.
///
/// Research:
///     grove band gap - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a lane keeps a footpath's clearance and some working room off the trees; `CONNECTOR_BAND_GAP_FT`, 0036's 9.5 ft working room plus the connector's half-width (12.5 ft), on a finer grid
pub const GROVE_CELL_FT: f64 = 2.9;

/// The connector's gap off a farm's grove band (ft): 0036's working room and the connector's half-width.
///
/// Research:
///     grove band gap - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 9.5 ft of working room off the trees plus the connector's 3 ft half-width
pub const BAND_GAP_FT: f64 = 12.5;

/// How far past the canvas edge the fill's track runs on (ft).
///
/// Research:
///     the track out runs off the map - research/questions/0081-village-lanes.drawing.html: 400 ft past the canvas
pub const OVERSHOOT_FT: f64 = 400.0;

/// The pond's berth past its larger half-axis (ft).
///
/// Research:
///     pond berth - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); 80 ft past the pond's larger half-axis
pub const POND_BERTH_FT: f64 = 80.0;

/// The brook's crossing places: their spacing, half their length, the bend that skips one (ft, ft, degrees), and what a crossing
/// costs in walk (ft).
///
/// Research:
///     crossing places along the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: every 160 ft
///     crossing on a straight reach - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: none where the brook turns over 20 degrees
///     crossing place's length - CONVENTION: a 60 ft gap (30 ft either side of a crossing place), so a deck crossing near square lands on both banks; 0035 sets the places and their spacing, not their length
///     brook crossed at its crossing places - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the fill keeps to its own bank unless crossing at a crossing place finds a way it otherwise has not, or saves more than 150 ft of walk
pub const FORDS: (f64, f64, f64, f64) = (160.0, 30.0, 20.0, 150.0);

/// A segment.
type Seg = (Pt, Pt);

/// The fill's grid: its origin (two cells before the canvas), its size in cells, and its cell.
#[derive(Clone, Copy)]
pub struct Grid {
    x0: f64,
    y0: f64,
    nx: i64,
    ny: i64,
    cell: f64,
}

impl Grid {
    /// The grid over a `w` x `h` canvas at `cell`, two cells past it on every side.
    #[must_use]
    pub fn new(w: f64, h: f64, cell: f64) -> Self {
        Self {
            x0: -2.0 * cell,
            y0: -2.0 * cell,
            nx: ((w + 4.0 * cell) / cell).floor() as i64 + 1,
            ny: ((h + 4.0 * cell) / cell).floor() as i64 + 1,
            cell,
        }
    }

    fn center(&self, (i, j): (i64, i64)) -> Pt {
        (
            self.x0 + (i as f64 + 0.5) * self.cell,
            self.y0 + (j as f64 + 0.5) * self.cell,
        )
    }

    fn at(&self, p: Pt) -> (i64, i64) {
        (
            ((p.0 - self.x0) / self.cell).floor() as i64,
            ((p.1 - self.y0) / self.cell).floor() as i64,
        )
    }

    fn index(&self, (i, j): (i64, i64)) -> Option<usize> {
        (0..self.nx)
            .contains(&i)
            .then_some(())
            .filter(|()| (0..self.ny).contains(&j))
            .map(|()| (j * self.nx + i) as usize)
    }

    /// The indices whose cell centers can lie in [lo, hi] on an axis of `n` cells from `org`, with a cell to spare above.
    fn span(&self, lo: f64, hi: f64, n: i64, org: f64) -> std::ops::Range<i64> {
        ((lo - org) / self.cell).floor().max(0.0) as i64
            ..(((hi - org) / self.cell).floor() as i64 + 2).min(n)
    }

    /// Every cell whose center could stand within `r` of the segment, a row at a time: a row's cells are those within `r` in x
    /// of the part of the segment within `r` of the row's center line in y.
    #[expect(
        clippy::float_cmp,
        reason = "a level segment, exactly: the row's slice divides by its rise"
    )]
    fn near(&self, a: Pt, b: Pt, r: f64, mut f: impl FnMut((i64, i64))) {
        let rr = r + 1e-6;
        for j in self.span(a.1.min(b.1) - r, a.1.max(b.1) + r, self.ny, self.y0) {
            let cy = self.y0 + (j as f64 + 0.5) * self.cell;
            let (lo, hi) = if a.1 == b.1 {
                (a.0.min(b.0), a.0.max(b.0))
            } else {
                let (t0, t1) = ((cy - rr - a.1) / (b.1 - a.1), (cy + rr - a.1) / (b.1 - a.1));
                let (t0, t1) = (t0.min(t1).max(0.0), t0.max(t1).min(1.0));
                if t0 > t1 {
                    continue;
                }
                let (u, v) = (a.0 + (b.0 - a.0) * t0, a.0 + (b.0 - a.0) * t1);
                (u.min(v), u.max(v))
            };
            for i in self.span(lo - rr, hi + rr, self.nx, self.x0) {
                f((i, j));
            }
        }
    }
}

/// The grid's cells a point of which could stand inside a wall or within its margin of one - each wall a ring and its margin -
/// or within one cell of a water line, as a raster: inside a row at a time by the ray test's sorted crossings, within the margin
/// an edge at a time over the strip beside it.
#[must_use]
pub fn blocked(
    g: &Grid,
    walls: &[(Vec<Pt>, f64)],
    lines: &[(Pt, Pt)],
    tests: &mut Counts,
) -> Vec<bool> {
    let mut out = vec![false; (g.nx * g.ny) as usize];
    let pad = g.cell * 0.5f64.sqrt();
    for (ring, margin) in walls.iter().filter(|w| w.0.len() >= 3) {
        let reach = margin + pad;
        let n = ring.len();
        let b = super::track::poly_box(ring);
        let cols = g.span(b.0 - reach, b.2 + reach, g.nx, g.x0);
        for j in g.span(b.1 - reach, b.3 + reach, g.ny, g.y0) {
            let cy = g.y0 + (j as f64 + 0.5) * g.cell;
            let mut xs: Vec<f64> = (0..n)
                .map(|k| (ring[k], ring[(k + n - 1) % n]))
                .filter(|(p, q)| (p.1 > cy) != (q.1 > cy))
                .map(|(p, q)| (q.0 - p.0) * (cy - p.1) / (q.1 - p.1 + 1e-9) + p.0)
                .collect();
            tests.add("pt_test@blocked", n as u64);
            // ...and each cell of the row's span read against the crossings (the track's sixth MODE AUDIT: uncounted)
            tests.add("pt_test@blocked_cells", cols.clone().count() as u64);
            xs.sort_by(f64::total_cmp);
            for i in cols.clone().filter(|_| !xs.is_empty()) {
                let cx = g.x0 + (i as f64 + 0.5) * g.cell;
                if (xs.len() - xs.partition_point(|&x| x <= cx)) & 1 == 1 {
                    out[(j * g.nx + i) as usize] = true;
                }
            }
        }
        for k in 0..n {
            let (a, c) = (ring[k], ring[(k + 1) % n]);
            g.near(a, c, reach, |ij| {
                let at = (ij.1 * g.nx + ij.0) as usize;
                tests.add("dist@blocked", 1);
                if !out[at] && seg_dist(g.center(ij), a, c) < reach {
                    out[at] = true;
                }
            });
        }
    }
    for &(a, c) in lines {
        g.near(a, c, g.cell, |ij| {
            let at = (ij.1 * g.nx + ij.0) as usize;
            tests.add("dist@blocked", 1);
            if !out[at] && seg_dist(g.center(ij), a, c) < g.cell {
                out[at] = true;
            }
        });
    }
    out
}

/// A track from `start` off the `w` x `h` canvas through cells not `blocked`, the start's own cell walkable whatever stands
/// there, string-pulled and run on past the edge; None when the start is walled in.
///
/// ...SOUGHT TOWARD THE NEAREST EDGE (feature 444 T32, the track's sixth MODE AUDIT): a breadth-first flood visited every cell
/// nearer the start than the way out - 74 million on a 40-household dispersed roll at the band's 2.9 ft grid. The same fewest steps
/// are found by A* under the cells left to the nearest edge (an under-estimate that falls by at most one a step, so the first
/// cell off the canvas reached is one the flood would reach at the same step count), which visits the cells toward that edge.
#[must_use]
pub fn fill(
    g: &Grid,
    start: Pt,
    blocked: &[bool],
    canvas: Pt,
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    use std::cmp::Reverse;
    use std::collections::BinaryHeap;
    let s = g.at(start);
    let off = |c: (i64, i64)| {
        let p = g.center(c);
        !((0.0..=canvas.0).contains(&p.0) && (0.0..=canvas.1).contains(&p.1))
    };
    let left = |c: (i64, i64)| {
        let p = g.center(c);
        let d =
            p.0.min(canvas.0 - p.0)
                .min(p.1)
                .min(canvas.1 - p.1)
                .max(0.0);
        (d / g.cell).floor() as i64
    };
    let mut back: HashMap<(i64, i64), (i64, i64)> = HashMap::from([(s, s)]);
    let mut steps: HashMap<(i64, i64), i64> = HashMap::from([(s, 0)]);
    let mut seq = 0u64;
    let mut open = BinaryHeap::from([(Reverse(left(s)), Reverse(0i64), Reverse(seq), s)]);
    let mut goal = None;
    while let Some((_, Reverse(n), _, c)) = open.pop() {
        // (an entry a shorter walk left behind comes off the queue after that walk's own, so its neighbors were relaxed from the
        // shorter walk already and it pushes none - no set of the cells done is kept)
        if off(c) {
            goal = Some(c);
            break;
        }
        for d in [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ] {
            let nb = (c.0 + d.0, c.1 + d.1);
            tests.add("candidate@fill", 1);
            if g.index(nb).is_some_and(|k| !blocked[k]) && steps.get(&nb).is_none_or(|&m| n + 1 < m)
            {
                steps.insert(nb, n + 1);
                back.insert(nb, c);
                seq += 1;
                open.push((Reverse(n + 1 + left(nb)), Reverse(n + 1), Reverse(seq), nb));
            }
        }
    }
    tests.add(
        if goal.is_some() {
            "call@fill_out"
        } else {
            "call@fill_walled"
        },
        1,
    );
    let mut at = goal?;
    let mut chain = vec![at];
    while at != s {
        at = back[&at];
        chain.push(at);
    }
    chain.reverse();
    let mut pts = vec![start];
    pts.extend(chain.iter().skip(1).map(|&c| g.center(c)));
    if pts.len() < 2 {
        pts.push(g.center(s));
    }
    let mut pulled = pull(g, &pts, blocked, s, tests);
    let (a, b) = (pulled[pulled.len() - 2], pulled[pulled.len() - 1]);
    let d = (b.0 - a.0).hypot(b.1 - a.1);
    let d = if d == 0.0 { 1.0 } else { d };
    let last = pulled.len() - 1;
    pulled[last] = (
        b.0 + (b.0 - a.0) / d * OVERSHOOT_FT,
        b.1 + (b.1 - a.1) / d * OVERSHOOT_FT,
    );
    Some(pulled)
}

/// The chain of cell centers string-pulled: from each point, the farthest later point whose straight leg samples only walkable
/// cells (the start's own cell included), found walking forward while the leg stays clear.
///
/// ...WALKED FORWARD, NOT BACK FROM THE END (feature 444 T32, the sixth MODE AUDIT): asking every later point from the chain's end
/// down was a leg test per pair - 9.3 million samples on one dispersed roll; walking on from the last clear point asks each point
/// once a leg, and stops at the first blocked one (a chain round a corner is pulled at the corner, as before)
fn pull(g: &Grid, pts: &[Pt], blocked: &[bool], start: (i64, i64), tests: &mut Counts) -> Vec<Pt> {
    let mut clear = |a: Pt, b: Pt| {
        let n = (((b.0 - a.0).hypot(b.1 - a.1) / (g.cell / 4.0)) as i64).max(1);
        tests.add("pt_test@pull", (n + 1) as u64);
        (0..=n).all(|k| {
            let f = k as f64 / n as f64;
            let c = g.at((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f));
            c == start || !g.index(c).is_some_and(|i| blocked[i])
        })
    };
    let mut out = vec![pts[0]];
    let mut k = 0;
    while k < pts.len() - 1 {
        let mut m = k + 1;
        while m + 1 < pts.len() && clear(pts[k], pts[m + 1]) {
            m += 1;
        }
        out.push(pts[m]);
        k = m;
    }
    out
}

/// `p` moved outside the ring by `margin` on the normal of the edge nearest it, pointing away from the ring's centroid; a point
/// already clear by the margin is returned untouched.
#[must_use]
pub fn push_out_of(ring: &[Pt], p: Pt, margin: f64) -> Pt {
    let n = ring.len();
    let (d, q, a, b) = (0..n)
        .map(|k| {
            let (a, b) = (ring[k], ring[(k + 1) % n]);
            let (vx, vy) = (b.0 - a.0, b.1 - a.1);
            let l2 = vx * vx + vy * vy;
            let t = if l2 > 0.0 {
                (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / l2).clamp(0.0, 1.0)
            } else {
                0.0
            };
            let q = (a.0 + vx * t, a.1 + vy * t);
            ((q.0 - p.0).hypot(q.1 - p.1), q, a, b)
        })
        .fold(None, |best: Option<(f64, Pt, Pt, Pt)>, c| match best {
            Some(bb) if bb.0 <= c.0 => Some(bb),
            _ => Some(c),
        })
        .unwrap_or((0.0, p, p, p));
    if !in_poly(p, ring) && d > margin {
        return p;
    }
    let mut u = crate::field::geom::unit((0.0, 0.0), (-(b.1 - a.1), b.0 - a.0));
    let cen = ring.iter().fold((0.0, 0.0), |s, r| {
        (s.0 + r.0 / n as f64, s.1 + r.1 / n as f64)
    });
    if u.0 * (q.0 - cen.0) + u.1 * (q.1 - cen.1) < 0.0 {
        u = (-u.0, -u.1);
    }
    (q.0 + u.0 * margin, q.1 + u.1 * margin)
}

/// `p` pushed out past `clear` of every grove band it stands in or within `clear` of, a few rounds, since a push off one band
/// can land near another.
///
/// Research:
///     clear of the groves - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a way keeps a footpath's clearance and some working room off the trees - pushed `clear` (the caller's band gap) past every grove band
#[must_use]
pub fn clear_of_bands(mut p: Pt, bands: &[&[Pt]], clear: f64) -> Pt {
    for _ in 0..4 {
        let Some(near) = bands
            .iter()
            .find(|b| in_poly(p, b) || edge_dist(p, b) < clear)
        else {
            break;
        };
        p = push_out_of(near, p, clear);
    }
    p
}

/// What the dry exit reads: the walls and the water.
#[derive(Clone, Copy)]
pub struct DrySite<'a> {
    /// The wet polygons (grown by the lane here).
    pub wet: &'a [Vec<Pt>],
    /// The steadings, each marked where it is a farm's grove band.
    pub fabric: &'a [(Vec<Pt>, bool)],
    /// The crop polygons (the field's envelope where none).
    pub avoid: &'a [Vec<Pt>],
    /// The pond, if one.
    pub pond: Option<Pond>,
    /// The drain brook's segments and the watercourses', every one a line the fill may not cross.
    pub lines: &'a [(Pt, Pt)],
    /// The brook's course, whose segments are gapped at the crossing places.
    pub course: &'a [Pt],
    /// The canvas (ft).
    pub canvas: Pt,
}

fn length(p: &[Pt]) -> f64 {
    p.windows(2)
        .map(|w| (w[1].0 - w[0].0).hypot(w[1].1 - w[0].1))
        .sum()
}

/// Do both ends of the segment lie within a foot of the course?
fn on_course(s: (Pt, Pt), course: &[Pt]) -> bool {
    course.len() >= 2
        && [s.0, s.1]
            .iter()
            .all(|&q| course.windows(2).any(|w| seg_dist(q, w[0], w[1]) <= 1.0))
}

/// The connector by the flood fill: walled by the wet ground grown by the lane, every steading at the track's gap (a grove band
/// at the band gap, on the finer grid), the crop and the pond's disc; the brook and the drawn water lines it may not cross - the
/// brook but at its crossing places where crossing finds a way or saves the crossing's cost in walk, a drawn channel but where no
/// other way out stands. None where no fill finds a way out of the frame.
#[must_use]
pub fn connector_dry_exit(site: &DrySite, start: Pt, tests: &mut Counts) -> Option<Vec<Pt>> {
    let mut walls: Vec<(Vec<Pt>, f64)> = site
        .wet
        .iter()
        .filter(|w| w.len() >= 3)
        .map(|w| (grown(w, WET_GROWN_FT), 0.0))
        .collect();
    walls.extend(
        site.fabric
            .iter()
            .map(|(f, band)| (f.clone(), if *band { BAND_GAP_FT } else { FABRIC_GAP_FT })),
    );
    walls.extend(site.avoid.iter().map(|a| (a.clone(), 0.0)));
    if let Some((px, py, rx, ry)) = site.pond {
        let r = rx.max(ry);
        let disc = (0..16)
            .map(|k| {
                let a = f64::from(k) * std::f64::consts::PI / 8.0;
                (px + r * a.cos(), py + r * a.sin())
            })
            .collect();
        walls.push((disc, POND_BERTH_FT));
    }
    let (spacing, half, bend, cost) = FORDS;
    tests.add(
        "seg_test@on_course",
        (site.lines.len() * site.course.len().saturating_sub(1)) as u64,
    );
    let (brook, channels): (Vec<Seg>, Vec<Seg>) =
        site.lines.iter().partition(|&&s| on_course(s, site.course));
    let mut counts = HashMap::new();
    let at = fords(site.course, spacing, half, bend, &mut counts);
    let segs: Vec<Vec<Pt>> = brook.iter().map(|&(a, b)| vec![a, b]).collect();
    let gapped_brook = gapped(&segs, &at, half, &mut counts);
    for (k, n) in &counts {
        tests.add(k, *n);
    }
    let bands: Vec<&[Pt]> = site
        .fabric
        .iter()
        .filter(|f| f.1)
        .map(|f| f.0.as_slice())
        .collect();
    tests.add("pt_test@clear_of_bands", 4 * bands.len() as u64); // at most four rounds over the bands
    let (start, cell) = if bands.is_empty() {
        (start, EXIT_CELL_FT)
    } else {
        (
            clear_of_bands(start, &bands, BAND_GAP_FT + 0.71 * GROVE_CELL_FT + 1.0),
            GROVE_CELL_FT,
        )
    };
    let g = Grid::new(site.canvas.0, site.canvas.1, cell);
    // the walls rastered once; each fill adds its own water lines
    let walled = blocked(&g, &walls, &[], tests);
    let with = |lines: &[(Pt, Pt)], tests: &mut Counts| {
        let wet = blocked(&g, &[], lines, tests);
        tests.add("write@fill_grid", 2 * walled.len() as u64); // the water's grid and the merge, a cell each
        let both: Vec<bool> = walled.iter().zip(&wet).map(|(a, b)| *a || *b).collect();
        fill(&g, start, &both, site.canvas, tests)
    };
    let mut path = with(site.lines, tests);
    let mut opened = gapped_brook.clone();
    opened.extend(&channels);
    let across = (opened != site.lines)
        .then(|| with(&opened, tests))
        .flatten();
    if across
        .as_ref()
        .is_some_and(|a| path.as_ref().is_none_or(|p| length(p) > length(a) + cost))
    {
        path = across;
    }
    if path.is_none() && !channels.is_empty() {
        path = with(&gapped_brook, tests);
    }
    path
}
