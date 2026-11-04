//! The seat's dry way out of the frame (feature 444 T27 D3): straight runs off the canvas first, and where none is clear, a
//! walk of the way-out grid's cells aimed at the nearest edge, each cell asked of the walls and the water as it is reached.
//!
//! Research:
//!     the way out - NONE: the seat's machinery; each rule's claim is at the unit that keeps it

#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names; grid cells and counts of a few thousand, inside f64's mantissa and i64"
)]
use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap, HashSet};

use super::index::{Cells, Strips};
use super::{tally, Wall};
use crate::field::fan::Pt;
use crate::field::geom::seg_dist;

/// The way-out grid (feet): finer than any neck a track would use, a neck under it no dry exit anyone would take.
///
/// Research:
///     narrowest dry neck - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass D, 2026-10-25); a neck under 20 ft is not taken
pub const EXIT_CELL: f64 = 20.0;

/// The straight runs tried off the canvas, one every 22.5 degrees.
///
/// Research:
///     the straight runs - NONE: a search's breadth, deciding nothing about the place - the walk answers where no run is clear; 16 bearings
pub const BEARINGS: u32 = 16;

/// The index of the walls' edges and the water lines (feet): wider than the farthest a wall's margin reaches, so the 3 x 3 cells
/// round a point hold every edge and line that can block it.
///
/// Research:
///     its salts, guards and sentinels - NONE: an index's grain, which decides nothing about the place - 128 ft
pub const REACH_CELL: f64 = 128.0;

/// How far a straight run keeps off each wall and each water line, in way-out cells: enough that every cell it passes through
/// is one the walk could stand in, so a clear run is a way out the walk would find.
///
/// Research:
///     its margins - NONE: they decide nothing about the place - 1.5 cells off a wall's margin, 1.75 off a water line, so the straight test is sufficient for the walk
pub const RUN_KEEP: (f64, f64) = (1.5, 1.75);

/// The distance between two segments.
#[must_use]
pub fn seg_seg(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> f64 {
    let cross = |o: Pt, p: Pt, q: Pt| (p.0 - o.0) * (q.1 - o.1) - (p.1 - o.1) * (q.0 - o.0);
    let (d1, d2, d3, d4) = (
        cross(b0, b1, a0),
        cross(b0, b1, a1),
        cross(a0, a1, b0),
        cross(a0, a1, b1),
    );
    if (d1 > 0.0) != (d2 > 0.0) && (d3 > 0.0) != (d4 > 0.0) {
        return 0.0;
    }
    seg_dist(a0, b0, b1)
        .min(seg_dist(a1, b0, b1))
        .min(seg_dist(b0, a0, a1))
        .min(seg_dist(b1, a0, a1))
}

/// The walls and the water, indexed for the way out.
pub struct Exit<'a> {
    walls: &'a [Wall],
    strips: Vec<Strips>,
    edges: Vec<(Pt, Pt, f64, Option<usize>)>,
    cells: Cells,
    canvas: Pt,
    /// Each way-out cell tested, and whether a track may stand in it.
    tested: HashMap<(i64, i64), bool>,
    /// Each cell a walk reached, and whether it is joined to an edge (true) or walled in (false).
    known: HashMap<(i64, i64), bool>,
}

impl<'a> Exit<'a> {
    /// Every wall edge (with its margin and wall) and every water line filed in the reach cells.
    #[must_use]
    pub fn new(
        walls: &'a [Wall],
        lines: &[(Pt, Pt)],
        canvas: Pt,
        counts: &mut HashMap<String, u64>,
    ) -> Self {
        let mut edges = Vec::new();
        let mut filed = 0;
        let strips = walls
            .iter()
            .map(|(ring, _m)| Strips::new(ring, &mut filed))
            .collect();
        for (w, (ring, m)) in walls.iter().enumerate() {
            let n = ring.len();
            for i in 0..n {
                edges.push((ring[i], ring[(i + 1) % n], *m, Some(w)));
            }
        }
        for &(a, b) in lines {
            edges.push((a, b, -1.0, None));
        }
        let mut cells = Cells::new(REACH_CELL);
        for (i, e) in edges.iter().enumerate() {
            filed += cells.file(i, &[e.0, e.1]);
        }
        tally(counts, "write@exit_cells", filed);
        Self {
            walls,
            strips,
            edges,
            cells,
            canvas,
            tested: HashMap::new(),
            known: HashMap::new(),
        }
    }

    /// The edges filed in the cells within one reach cell of a box.
    fn near(&self, lo: Pt, hi: Pt, tests: &mut u64) -> Vec<usize> {
        let (items, read) = self.cells.in_box(
            (lo.0 - REACH_CELL, lo.1 - REACH_CELL),
            (hi.0 + REACH_CELL, hi.1 + REACH_CELL),
        );
        *tests += read;
        items
    }

    /// Whether a straight run off the canvas from `start` along `dir` keeps clear of every wall by its margin and of every water
    /// line - a sufficient test: a run that keeps them is a way out the walk would find.
    fn straight(&self, start: Pt, dir: Pt, tests: &mut u64) -> bool {
        let span = |v: f64, d: f64, edge: f64| {
            if d.abs() > 1e-9 {
                ((if d > 0.0 { edge } else { 0.0 }) - v) / d
            } else {
                f64::INFINITY
            }
        };
        let run = span(start.0, dir.0, self.canvas.0).min(span(start.1, dir.1, self.canvas.1))
            + 2.0 * EXIT_CELL;
        let end = (start.0 + dir.0 * run, start.1 + dir.1 * run);
        for (w, (ring, _m)) in self.walls.iter().enumerate() {
            *tests += 1;
            if ring.len() >= 3 && self.strips[w].inside(start, tests) {
                return false;
            }
        }
        let steps = (run / REACH_CELL).ceil().max(1.0) as usize;
        let mut seen = HashSet::new();
        for k in 0..steps {
            let (t0, t1) = (k as f64 / steps as f64, (k + 1) as f64 / steps as f64);
            let (p, q) = (
                (
                    start.0 + (end.0 - start.0) * t0,
                    start.1 + (end.1 - start.1) * t0,
                ),
                (
                    start.0 + (end.0 - start.0) * t1,
                    start.1 + (end.1 - start.1) * t1,
                ),
            );
            for i in self.near(
                (p.0.min(q.0), p.1.min(q.1)),
                (p.0.max(q.0), p.1.max(q.1)),
                tests,
            ) {
                if !seen.insert(i) {
                    continue;
                }
                let (a, b, m, _w) = self.edges[i];
                *tests += 1;
                let keep = if m >= 0.0 {
                    m + RUN_KEEP.0 * EXIT_CELL
                } else {
                    RUN_KEEP.1 * EXIT_CELL
                };
                if seg_seg(start, end, a, b) < keep {
                    return false;
                }
            }
        }
        true
    }

    /// Whether a way-out cell centered at `c` is one a track may stand in: off every wall by its margin and half the cell's
    /// diagonal, inside none, and a cell off every water line.
    ///
    /// Research:
    ///     a track's clearance off wet ground - GUESS: research/questions/0081-village-lanes.drawing.html keeps a track off wet ground and gives no distance; a cell (20 ft) off a water line, a wall's margin and half a cell's diagonal (about 14 ft) off its edge, so every point of a walkable cell keeps the margin
    fn walkable(&self, c: Pt, tests: &mut u64) -> bool {
        let pad = EXIT_CELL * std::f64::consts::FRAC_1_SQRT_2;
        for i in self.near(c, c, tests) {
            let (a, b, m, _w) = self.edges[i];
            *tests += 1;
            let reach = if m >= 0.0 { m + pad } else { EXIT_CELL };
            if seg_dist(c, a, b) < reach {
                return false;
            }
        }
        for (w, (ring, _m)) in self.walls.iter().enumerate() {
            if ring.len() >= 3 && self.strips[w].inside(c, tests) {
                return false;
            }
        }
        true
    }

    /// Whether the seat at `start` has a dry way out of the frame: a clear straight run, else a walk of the way-out cells - from
    /// the start's own cell, whatever stands there - that reaches a cell off the canvas, the cells nearest an edge taken first.
    ///
    /// Research:
    ///     dry way out of the seat - research/questions/0081-village-lanes.drawing.html: lanes keep to dry ground; a walled-in head is refused
    ///     a track keeps off wet ground - research/questions/0081-village-lanes.drawing.html: clear of every wall's margin and every water line
    ///     the walk remembered - NONE: a memo across the margins the head falls back to; a cell tested is never tested again
    pub fn has_exit(&mut self, start: Pt, counts: &mut HashMap<String, u64>) -> bool {
        let org = -2.0 * EXIT_CELL;
        let s = (
            ((start.0 - org) / EXIT_CELL) as i64,
            ((start.1 - org) / EXIT_CELL) as i64,
        );
        if let Some(&joined) = self.known.get(&s) {
            return joined; // a seat in ground an earlier walk reached: its answer, with no run tried
        }
        let mut tests = 0;
        let mut runs = 0;
        let clear = (0..BEARINGS).any(|k| {
            runs += 1;
            let a = std::f64::consts::TAU * f64::from(k) / f64::from(BEARINGS);
            self.straight(start, (a.cos(), a.sin()), &mut tests)
        });
        tally(counts, "candidate@exit_run", runs);
        if clear {
            tally(counts, "test@exit_run", tests);
            return true;
        }
        let (nx, ny) = (
            ((self.canvas.0 + 4.0 * EXIT_CELL) / EXIT_CELL) as i64 + 1,
            ((self.canvas.1 + 4.0 * EXIT_CELL) / EXIT_CELL) as i64 + 1,
        );
        let center = |i: i64, j: i64| {
            (
                org + (i as f64 + 0.5) * EXIT_CELL,
                org + (j as f64 + 0.5) * EXIT_CELL,
            )
        };
        let to_edge = |p: Pt| {
            p.0.min(self.canvas.0 - p.0)
                .min(p.1)
                .min(self.canvas.1 - p.1)
                .max(0.0)
        };
        let s = (
            ((start.0 - org) / EXIT_CELL) as i64,
            ((start.1 - org) / EXIT_CELL) as i64,
        );
        let mut seen = HashSet::from([s]);
        let mut heap = BinaryHeap::from([Reverse(((to_edge(center(s.0, s.1)) * 16.0) as i64, s))]);
        let mut walked = 0;
        let mut out = None;
        while let Some(Reverse((_d, (i, j)))) = heap.pop() {
            walked += 1;
            if let Some(&joined) = self.known.get(&(i, j)) {
                out = Some(joined); // a cell an earlier walk reached: its answer is this walk's
                break;
            }
            let c = center(i, j);
            if !(0.0..=self.canvas.0).contains(&c.0) || !(0.0..=self.canvas.1).contains(&c.1) {
                out = Some(true);
                break;
            }
            for (di, dj) in [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
            ] {
                let nb = (i + di, j + dj);
                if (0..nx).contains(&nb.0) && (0..ny).contains(&nb.1) && !seen.contains(&nb) {
                    seen.insert(nb);
                    let q = center(nb.0, nb.1);
                    let ok = if let Some(&ok) = self.tested.get(&nb) {
                        ok
                    } else {
                        let ok = self.walkable(q, &mut tests);
                        self.tested.insert(nb, ok);
                        ok
                    };
                    if ok {
                        heap.push(Reverse(((to_edge(q) * 16.0) as i64, nb)));
                    }
                }
            }
        }
        let joined = out.unwrap_or(false);
        // every cell this walk reached shares its start's answer: one connected piece of walkable ground
        for c in seen {
            if self.tested.get(&c).copied().unwrap_or(c == s) {
                self.known.insert(c, joined);
            }
        }
        tally(counts, "test@exit_run", tests);
        tally(counts, "test@exit_walk", walked);
        joined
    }
}

/// Whether `p` lies in any of `rings`, the rings walked whole - the test the walls' strips stand in for, kept for the tests.
#[cfg(test)]
#[must_use]
pub fn in_any(p: Pt, rings: &[Wall]) -> bool {
    rings
        .iter()
        .any(|(r, _m)| r.len() >= 3 && crate::field::geom::inside(p, r))
}
