//! The span search (derivation T208, "The algorithm"): a strip along a wall or a face, asked of the grid a cell column (one chunk) at a
//! time; each obstacle found gives its interval along the strip, grown by its gap; the intervals kept sorted and merged; the first free
//! span long enough read off them directly, never a stepped slide. A wall's row of seated intervals starts the search at its first
//! long-enough gap, so the filled stretch is not read again.
//!
//! Research: the span search - NONE: it finds the first free span the caller's rule asks for, deciding nothing about a building

use std::collections::BTreeSet;

use super::count_at;
use super::grid::{Ent, Grid, CELL_FT};
use super::spec::Bx;

/// A strip: its axis, its extent across the axis, its range along it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Strip {
    /// Whether it runs along x.
    pub along_x: bool,
    /// Its extent across the axis.
    pub p0: f64,
    /// Its extent's far side.
    pub p1: f64,
    /// Its range along the axis.
    pub lo: f64,
    /// Its range's far end.
    pub hi: f64,
}

impl Strip {
    /// The box of the strip's stretch `[a0, a1]`, grown by `grow` across.
    #[must_use]
    pub fn bx(&self, a0: f64, a1: f64, grow: f64) -> Bx {
        if self.along_x {
            (a0, self.p0 - grow, a1, self.p1 + grow)
        } else {
            (self.p0 - grow, a0, self.p1 + grow, a1)
        }
    }

    /// A box's extent along the strip, and across it.
    #[must_use]
    pub fn split(&self, b: Bx) -> ((f64, f64), (f64, f64)) {
        if self.along_x {
            ((b.0, b.2), (b.1, b.3))
        } else {
            ((b.1, b.3), (b.0, b.2))
        }
    }
}

/// What the caller's rule makes of an entry: `None` ignores it, else its gap along the strip and across it.
pub type GapRule<'r> = &'r dyn Fn(&Ent) -> Option<(f64, f64)>;

/// One search: the strip, the length wanted, the rule, the furthest gap the rule gives (the query reaches that far), and the counter's
/// function name.
pub struct Ask<'r> {
    /// The strip.
    pub strip: Strip,
    /// The span wanted.
    pub len: f64,
    /// The rule.
    pub rule: GapRule<'r>,
    /// The furthest gap.
    pub reach: f64,
    /// The function counted.
    pub f: &'static str,
}

/// Merge an interval into a sorted, merged list (counted).
pub fn insert(list: &mut Vec<(f64, f64)>, iv: (f64, f64), f: &str) {
    let at = list.partition_point(|x| {
        count_at("span_compare", f, 1);
        x.0 < iv.0
    });
    list.insert(at, iv);
    let mut merged: Vec<(f64, f64)> = Vec::with_capacity(list.len());
    for &(lo, hi) in list.iter() {
        count_at("span_compare", f, 1);
        match merged.last_mut() {
            Some(prev) if lo <= prev.1 => prev.1 = prev.1.max(hi),
            _ => merged.push((lo, hi)),
        }
    }
    *list = merged;
}

/// The first `pos >= from` where `[pos, pos + len]` meets no interval and ends by `end`.
fn first_gap(blocked: &[(f64, f64)], from: f64, len: f64, end: f64, f: &str) -> Option<f64> {
    let mut pos = from;
    for &(a, b) in blocked {
        count_at("span_compare", f, 1);
        if b <= pos {
            continue;
        }
        if a >= pos + len {
            break;
        }
        pos = pos.max(b);
    }
    (pos + len <= end + 1e-9).then_some(pos)
}

/// The intervals (directed: `dir` is 1 forward, -1 backward) of the entries a query of `[q0, q1]` finds, each once.
fn found(
    grid: &mut Grid,
    ask: &Ask,
    q: (f64, f64),
    dir: f64,
    seen: &mut BTreeSet<usize>,
    blocked: &mut Vec<(f64, f64)>,
) {
    count_at("span_query", ask.f, 1);
    let (a0, a1) = if dir > 0.0 { q } else { (-q.1, -q.0) };
    let ids = grid.query(
        ask.strip.bx(a0 - ask.reach, a1 + ask.reach, ask.reach),
        ask.f,
    );
    for id in ids {
        if !seen.insert(id) {
            continue;
        }
        let ent = &grid.ents[id];
        let Some((ga, gp)) = (ask.rule)(ent) else {
            continue;
        };
        let ((e0, e1), (p0, p1)) = ask.strip.split(ent.bx);
        if p1 + gp <= ask.strip.p0 || p0 - gp >= ask.strip.p1 {
            continue;
        }
        count_at("span_interval", ask.f, 1);
        let iv = if dir > 0.0 {
            (e0 - ga, e1 + ga)
        } else {
            (-e1 - ga, -e0 + ga)
        };
        insert(blocked, iv, ask.f);
    }
}

/// The first free span from `start` in the direction `dir`, past the row's seated intervals (already grown): its start along the strip
/// (the seat's low end whichever way the search ran).
pub fn walk(grid: &mut Grid, ask: &Ask, row: &[(f64, f64)], start: f64, dir: f64) -> Option<f64> {
    let (tlo, thi) = if dir > 0.0 {
        (ask.strip.lo, ask.strip.hi)
    } else {
        (-ask.strip.hi, -ask.strip.lo)
    };
    let mut blocked: Vec<(f64, f64)> = Vec::new();
    for &(a, b) in row {
        let iv = if dir > 0.0 { (a, b) } else { (-b, -a) };
        insert(&mut blocked, iv, ask.f);
    }
    let cursor = (dir * start).max(tlo);
    let mut queried = cursor;
    let mut seen = BTreeSet::new();
    loop {
        count_at("seat", ask.f, 1);
        let cand = first_gap(&blocked, cursor, ask.len, thi, ask.f)?;
        if cand + ask.len <= queried + 1e-9 {
            return Some(if dir > 0.0 { cand } else { -(cand + ask.len) });
        }
        let q0 = queried.max(cand);
        let q1 = (q0 + CELL_FT).max(cand + ask.len).min(thi);
        found(grid, ask, (q0, q1), dir, &mut seen, &mut blocked);
        queried = q1;
    }
}

/// The free span nearest `from`, searched both ways: its start, the forward one on a tie.
pub fn nearest(grid: &mut Grid, ask: &Ask, from: f64) -> Option<f64> {
    let fwd = walk(grid, ask, &[], from, 1.0);
    let back = walk(grid, ask, &[], from + ask.len, -1.0);
    match (fwd, back) {
        (Some(f), Some(b)) => Some(if (f - from).abs() <= (from - b).abs() {
            f
        } else {
            b
        }),
        (f, b) => f.or(b),
    }
}

/// How far the ground is free from `from` in the direction `dir`, to the first obstacle or the strip's end.
fn free_run(grid: &mut Grid, ask: &Ask, from: f64, dir: f64) -> f64 {
    let thi = if dir > 0.0 {
        ask.strip.hi
    } else {
        -ask.strip.lo
    };
    let t = dir * from;
    let mut blocked = Vec::new();
    let mut seen = BTreeSet::new();
    let mut queried = t;
    loop {
        let next = blocked.iter().find(|iv: &&(f64, f64)| iv.1 > t);
        if let Some(&(a, _)) = next {
            if a < queried || queried >= thi {
                return (a.max(t) - t).min(thi - t);
            }
        } else if queried >= thi {
            return thi - t;
        }
        let q1 = (queried + CELL_FT).min(thi);
        found(grid, ask, (queried, q1), dir, &mut seen, &mut blocked);
        queried = q1;
    }
}

/// A span of the asked length centered in the free ground holding `mid`, when it is long enough: its start.
pub fn centered(grid: &mut Grid, ask: &Ask, mid: f64) -> Option<f64> {
    let ahead = free_run(grid, ask, mid, 1.0);
    let behind = free_run(grid, ask, mid, -1.0);
    count_at("rule_check", ask.f, 1);
    (ahead + behind >= ask.len).then(|| {
        let middle = f64::midpoint(mid - behind, mid + ahead);
        (middle - ask.len / 2.0).clamp(mid - behind, mid + ahead - ask.len)
    })
}
