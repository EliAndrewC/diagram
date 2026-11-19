//! The open ground, per court (derivation T208, "The algorithm"): one sweep over the buildings' x-edges, each slab's free y-intervals,
//! neighboring slabs' intervals joined - so every large free region can be asked whether it lies on a named ground (no unnamed void,
//! 0116) and a walk over the free ground can reach the granary's and the stables' doors from a gate (the cart route). A failure refuses
//! the program; nothing is moved.
//!
//! Research: the open ground - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: every rule claimed where it is asked

use std::collections::VecDeque;

use l7r_gate_research::Error;

use super::count;
use super::grid::overlaps;
use super::layout::{Layout, CLEAR, DIVIDER_HALF, WALL_HALF};
use super::spec::{Bx, Court, Face, Program};

/// The least free region that must lie on a named ground (sq ft).
///
/// Research: no unnamed void - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: court centers held open and named; a free region of 1,600 sq ft (a 40 ft court) on no named ground and touching no wall is the unnamed void, the size a GUESS
pub const VOID_SQFT: f64 = 1600.0;
/// The least depth of open ground that counts toward a void (feet): a narrower band is an alley or the clear ground along a wall, the
/// perimeter's slack, never the central void.
///
/// Research: no unnamed void - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 20 ft, twice the 6-10 ft service alley the rear strip may narrow to (docs/buildings.md); a knob
pub const LARGE_FT: f64 = 20.0;
/// The band along each wall and the divider whose open ground is the perimeter, not the center (feet): the audit's own band for a
/// building ringing the courts (`perimeter_hugging`, within 25 ft of a wall or the divider).
///
/// Research: perimeter gap against the central void - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: central open ground is a named court; a gap against a wall, between edge buildings, is the perimeter's slack to tighten (docs/buildings.md, Composition) - the band 25 ft, the audit's perimeter (a GUESS there)
pub const PERIMETER_FT: f64 = 25.0;
/// The width a cart passes (feet).
///
/// Research: cart lane - GUESS research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.html: about 6 ft where carts use it
pub const CART_FT: f64 = 6.0;

/// The free rectangles of one court and their adjacency.
pub struct Ground {
    /// The free rectangles.
    pub rects: Vec<Bx>,
    /// Each rectangle's neighbors.
    pub next: Vec<Vec<usize>>,
}

/// The court's open ground: the slabs between the obstacles' x-edges, each slab's free y-intervals, neighbors joined where a cart passes.
#[must_use]
pub fn sweep(obstacles: &[Bx], court: Bx) -> Ground {
    let mut xs: Vec<f64> = vec![court.0, court.2];
    for o in obstacles {
        for x in [o.0, o.2] {
            if court.0 < x && x < court.2 {
                xs.push(x);
            }
        }
    }
    xs.sort_by(|a, b| {
        count("sweep_op@compound_sweep", 1);
        a.total_cmp(b)
    });
    xs.dedup();
    let mut rects: Vec<Bx> = Vec::new();
    let mut slabs: Vec<(usize, usize)> = Vec::new();
    // the obstacles by their west edge, entered into the active set as the sweep reaches them and left as it passes their east edge
    let mut by_x: Vec<&Bx> = obstacles
        .iter()
        .filter(|o| o.1 < court.3 && court.1 < o.3)
        .collect();
    by_x.sort_by(|a, b| {
        count("sweep_op@compound_sweep", 1);
        a.0.total_cmp(&b.0)
    });
    let mut next_in = 0;
    let mut active: Vec<(f64, f64, f64)> = Vec::new();
    for w in xs.windows(2) {
        let (x0, x1) = (w[0], w[1]);
        while next_in < by_x.len() && by_x[next_in].0 < x1 {
            let o = by_x[next_in];
            active.push((o.2, o.1.max(court.1), o.3.min(court.3)));
            next_in += 1;
        }
        active.retain(|a| {
            count("sweep_op@compound_sweep", 1);
            a.0 > x0
        });
        let mut cut: Vec<(f64, f64)> = active.iter().map(|a| (a.1, a.2)).collect();
        cut.sort_by(|a, b| {
            count("sweep_op@compound_sweep", 1);
            a.0.total_cmp(&b.0)
        });
        let first = rects.len();
        let mut y = court.1;
        for (a, b) in cut {
            count("sweep_op@compound_sweep", 1);
            if a > y {
                rects.push((x0, y, x1, a));
            }
            y = y.max(b);
        }
        if y < court.3 {
            rects.push((x0, y, x1, court.3));
        }
        slabs.push((first, rects.len()));
    }
    let mut next = vec![Vec::new(); rects.len()];
    for w in slabs.windows(2) {
        let ((a0, a1), (b0, b1)) = (w[0], w[1]);
        for i in a0..a1 {
            for j in b0..b1 {
                count("sweep_op@compound_sweep", 1);
                let shared = rects[i].3.min(rects[j].3) - rects[i].1.max(rects[j].1);
                if shared >= CART_FT {
                    count("graph_edge@compound_sweep", 1);
                    next[i].push(j);
                    next[j].push(i);
                }
            }
        }
    }
    // a slab's free stretches stacked at one x are joined only through a neighbor slab: none share an edge
    Ground { rects, next }
}

fn holds(r: Bx, pt: (f64, f64)) -> bool {
    r.0 - 1e-6 <= pt.0 && pt.0 <= r.2 + 1e-6 && r.1 - 1e-6 <= pt.1 && pt.1 <= r.3 + 1e-6
}

/// The components of the deep free ground (each rectangle at least [`LARGE_FT`] deep, joined where they share that much), as lists of
/// rectangles.
fn components(g: &Ground) -> Vec<Vec<usize>> {
    let deep = |i: usize| g.rects[i].3 - g.rects[i].1 >= LARGE_FT;
    let mut seen = vec![false; g.rects.len()];
    let mut out = Vec::new();
    for s in 0..g.rects.len() {
        if seen[s] || !deep(s) {
            continue;
        }
        seen[s] = true;
        let mut comp = vec![s];
        let mut q = VecDeque::from([s]);
        while let Some(i) = q.pop_front() {
            for &j in &g.next[i] {
                count("graph_edge@compound_walk", 1);
                let shared = g.rects[i].3.min(g.rects[j].3) - g.rects[i].1.max(g.rects[j].1);
                if !seen[j] && deep(j) && shared >= LARGE_FT {
                    seen[j] = true;
                    comp.push(j);
                    q.push_back(j);
                }
            }
        }
        out.push(comp);
    }
    out
}

/// Whether a walk over the free ground reaches `to` from any of `from`.
#[must_use]
pub fn reaches(g: &Ground, from: &[(f64, f64)], to: (f64, f64)) -> bool {
    let mut seen = vec![false; g.rects.len()];
    let mut q: VecDeque<usize> = VecDeque::new();
    for (i, r) in g.rects.iter().enumerate() {
        if from.iter().any(|&p| holds(*r, p)) {
            seen[i] = true;
            q.push_back(i);
        }
    }
    while let Some(i) = q.pop_front() {
        count("graph_edge@compound_walk", 1);
        if holds(g.rects[i], to) {
            return true;
        }
        for &j in &g.next[i] {
            if !seen[j] {
                seen[j] = true;
                q.push_back(j);
            }
        }
    }
    false
}

/// The court's box inside its walls.
#[must_use]
pub fn court_box(p: &Program, c: Court) -> Bx {
    let (x0, x1) = (WALL_HALF, p.w - WALL_HALF);
    match c {
        Court::Inner => (x0, WALL_HALF, x1, p.divider - DIVIDER_HALF),
        Court::Outer => (x0, p.divider + DIVIDER_HALF, x1, p.h - WALL_HALF),
    }
}

/// Every large free region of each court away from its walls lies on a named ground, and the cart route runs from the gates to the granary's and the stables'
/// doors.
///
///
/// # Errors
/// An unnamed void, or a granary or stables no cart reaches.
///
/// Research:
///     named court spine - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: forecourt, hearing court (oshirasu), garden and the ground between the courts stay open and named
///     the granary's cart route - research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.html: a compound that ships or receives bulk goods has a cart gate, a cart yard and a cart lane, rice bales coming and going by cart
///     carts over the open grounds - GUESS: only the buildings and the roofed hearing court block a cart; every other named ground (forecourt, yard, garden) can be driven over
pub fn open_ground(p: &Program, l: &Layout) -> Result<(), Error> {
    for court in [Court::Inner, Court::Outer] {
        let cb = court_box(p, court);
        let seats: Vec<Bx> = l
            .seats
            .iter()
            .flatten()
            .copied()
            .filter(|b| overlaps(*b, cb))
            .collect();
        // the void: the free ground of the court's center (past the perimeter band) left once every building AND every named ground is
        // taken out - a named ground is no void, and ground within the band of a wall is the perimeter's slack
        let center = (
            cb.0 + PERIMETER_FT,
            cb.1 + PERIMETER_FT,
            cb.2 - PERIMETER_FT,
            cb.3 - PERIMETER_FT,
        );
        let named: Vec<Bx> = seats
            .iter()
            .copied()
            .chain(p.zones.iter().map(|z| z.bx))
            .filter(|b| overlaps(*b, center))
            .collect();
        let g = sweep(&named, center);
        for comp in components(&g) {
            let area: f64 = comp
                .iter()
                .map(|&i| (g.rects[i].2 - g.rects[i].0) * (g.rects[i].3 - g.rects[i].1))
                .sum();
            count("rule_check@compound_void", 1);
            if area >= VOID_SQFT {
                let r = g.rects[comp[0]];
                return Err(Error::new(
                    "ValueError",
                    format!("an unnamed open void of {area:.0} sq ft at ({:.0}, {:.0}) ft - name it or fill it (0116)", r.0, r.1),
                ));
            }
        }
        if court == Court::Outer {
            // the cart's ground: the buildings and the roofed hearing court alone, every other named ground passable
            let roofed = p
                .zones
                .iter()
                .filter(|z| z.kind == "hearing court")
                .map(|z| z.bx);
            let carts: Vec<Bx> = seats
                .iter()
                .copied()
                .chain(roofed)
                .filter(|b| overlaps(*b, cb))
                .collect();
            cart_route(p, l, &sweep(&carts, cb))?;
        }
    }
    Ok(())
}

/// Research:
///     the granary's cart route - research/questions/0082-moving-goods-carts-packhorses-and-river-landings-kashi.drawing.html: the granary's door reached by cart from a gate
///     the outer court's gates alone - GUESS: carts enter by the gates on the outer court's side of the divider, the granary and the stables standing in the office court on every plan (docs/building-programs.md: the stables, cell and granary in the office court); a granary in the inner court would be refused, which no program has
///     the stables' cart route - GUESS: the stables' door reached by cart too (feature 417 T36 pass P4: no source could speak to it)
fn cart_route(p: &Program, l: &Layout, g: &Ground) -> Result<(), Error> {
    let inset = WALL_HALF + CLEAR;
    let gates: Vec<(f64, f64)> = p
        .gates
        .iter()
        .filter_map(|gt| {
            let pt = match gt.wall {
                Face::S => (gt.at, p.h - inset),
                Face::N => (gt.at, inset),
                Face::W => (inset, gt.at),
                Face::E => (p.w - inset, gt.at),
            };
            (pt.1 > p.divider).then_some(pt)
        })
        .collect();
    for kind in ["granary", "stables"] {
        let Some(i) = p.buildings.iter().position(|b| b.kind == kind) else {
            continue;
        };
        for d in l.doors.iter().filter(|d| d.b == i) {
            let to = (
                f64::midpoint(d.step.0, d.step.2),
                f64::midpoint(d.step.1, d.step.3),
            );
            count("rule_check@compound_cart", 1);
            if !reaches(g, &gates, to) {
                return Err(Error::new(
                    "ValueError",
                    format!(
                        "no cart route from a gate to the {}'s door - open the way",
                        p.buildings[i].name
                    ),
                ));
            }
        }
    }
    Ok(())
}
