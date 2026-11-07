//! The faces of the lane web (feature 444 T30): the treads noded where they cross and where an end stands on another tread, the
//! dangling legs pruned, and each bounded face traced round its edges; a face whose mean width (twice its area over its
//! perimeter) is under a needle's is a NEEDLE OF GRASS, the same way drawn twice round nothing (`law/meet.py` `needle_loops`,
//! `web_lines`, `web_faces` and `is_needle`, which polygonize shapely's noded union).
//!
//! A face with a lane loop standing free inside it keeps that loop's ground: the face's mean width is read from its outer ring,
//! which reads a holed face wider than shapely's polygon does, never thinner - so no needle is found here that shapely would not.
//!
//! Research:
//!     no sliver between the tree's lanes - research/questions/0081-village-lanes.drawing.html: two paths side by side are drawn as one (no needle, `needle_loops`)
//!     a needle of grass - GUESS: no source could speak to it, a value of ours (homes H39); a face of the web under 20 ft of mean width
//!     its salts, guards and sentinels - NONE: they decide nothing about the place - 1 (a noding speck's perimeter); 1e-6 (an end standing on a tread)
#![expect(
    clippy::cast_possible_truncation,
    reason = "vertex keys of tenths of a micron"
)]

use std::collections::HashMap;

use super::ground::BoxGrid;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::route::length;
use crate::ways::track::{seg_intersect, segments_cross, Box4};

/// A needle's mean width, and the perimeter under which a face is a noding speck (ft).
///
/// Research:
///     a needle of grass - GUESS: no source could speak to it, a value of ours (homes H39); under 20 ft of mean width
///     a noding speck - NONE: three lanes meeting at one point, noded a hair apart - 1 ft of perimeter
pub const NEEDLE: (f64, f64) = (20.0, 1.0);

/// A face of the web: its ring, its area and its perimeter.
#[derive(Debug, Clone, PartialEq)]
pub struct Face {
    /// Its ring.
    pub ring: Vec<Pt>,
    /// Its area.
    pub area: f64,
    /// Its perimeter.
    pub perimeter: f64,
}

impl Face {
    /// Is the face a needle: past a noding speck, its mean width under a needle's?
    #[must_use]
    pub fn is_needle(&self) -> bool {
        !(self.perimeter < NEEDLE.1 || 2.0 * self.area / self.perimeter >= NEEDLE.0)
    }
}

fn key(p: Pt) -> (i64, i64) {
    ((p.0 * 1e7).round() as i64, (p.1 * 1e7).round() as i64)
}

/// Each segment's cuts, as fractions along it: its two ends, where another crosses it, and where another's end stands on it. Asked
/// `near`, each segment only of the segments whose boxes meet its own (a crossing, or an end within 1e-6, lies in both boxes);
/// else of every other - the walk of every pair was the stage's superlinear work (the work-budget audit at T30's landing).
#[must_use]
pub fn cuts_of(segs: &[(Pt, Pt)], near: bool, tests: &mut Counts) -> Vec<Vec<f64>> {
    let mut cuts: Vec<Vec<f64>> = vec![vec![0.0, 1.0]; segs.len()];
    let boxes: Vec<Box4> = segs
        .iter()
        .map(|&(a, b)| (a.0.min(b.0), a.1.min(b.1), a.0.max(b.0), a.1.max(b.1)))
        .collect();
    let grid = BoxGrid::new(boxes.iter().copied());
    for i in 0..segs.len() {
        let others: Vec<usize> = if near {
            grid.near(boxes[i])
        } else {
            (0..segs.len()).collect()
        };
        for j in others.into_iter().filter(|&j| j > i) {
            let ((a, b), (c, d)) = (segs[i], segs[j]);
            tests.add("seg_test@web_faces", 1);
            if segments_cross(a, b, c, d) {
                if let Some(x) = seg_intersect(a, b, c, d) {
                    cuts[i].push(dist(a, x) / dist(a, b));
                    cuts[j].push(dist(c, x) / dist(c, d));
                }
            }
            for (on, (p, q), (u, v)) in [(i, (c, d), (a, b)), (j, (a, b), (c, d))] {
                for e in [p, q] {
                    if seg_dist(e, u, v) < 1e-6 {
                        cuts[on].push(dist(u, e) / dist(u, v));
                    }
                }
            }
        }
    }
    cuts
}

/// The bounded faces of the treads `ways` (each of two points or more and a foot long or more), noded where they cross.
#[must_use]
pub fn web_faces(ways: &[Vec<Pt>], tests: &mut Counts) -> Vec<Face> {
    let lines: Vec<&Vec<Pt>> = ways
        .iter()
        .filter(|w| w.len() >= 2 && length(w) >= 1.0)
        .collect();
    if lines.len() < 2 {
        return Vec::new();
    }
    let segs: Vec<(Pt, Pt)> = lines
        .iter()
        .flat_map(|w| w.windows(2).map(|s| (s[0], s[1])))
        .filter(|&(a, b)| dist(a, b) > 0.0)
        .collect();
    let cuts = cuts_of(&segs, true, tests);
    let mut verts: Vec<Pt> = Vec::new();
    let mut index: HashMap<(i64, i64), usize> = HashMap::new();
    let mut vert = |p: Pt| {
        *index.entry(key(p)).or_insert_with(|| {
            verts.push(p);
            verts.len() - 1
        })
    };
    let mut edges: Vec<(usize, usize)> = Vec::new();
    let mut seen: std::collections::HashSet<(usize, usize)> = std::collections::HashSet::new();
    for (k, &(a, b)) in segs.iter().enumerate() {
        let mut ts = cuts[k].clone();
        ts.sort_by(f64::total_cmp);
        let pts: Vec<usize> = ts
            .iter()
            .map(|&t| vert((a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)))
            .collect();
        for w in pts.windows(2) {
            let (u, v) = (w[0].min(w[1]), w[0].max(w[1]));
            if u != v && seen.insert((u, v)) {
                edges.push((u, v));
            }
        }
    }
    faces_of(&verts, edges)
}

/// The bounded faces of the planar graph: its dangling legs pruned, then each face traced with its interior on the left.
fn faces_of(verts: &[Pt], mut edges: Vec<(usize, usize)>) -> Vec<Face> {
    loop {
        let mut degree = vec![0usize; verts.len()];
        for &(u, v) in &edges {
            degree[u] += 1;
            degree[v] += 1;
        }
        let before = edges.len();
        edges.retain(|&(u, v)| degree[u] > 1 && degree[v] > 1);
        if edges.len() == before {
            break;
        }
    }
    let mut out: Vec<Vec<usize>> = vec![Vec::new(); verts.len()];
    for &(u, v) in &edges {
        out[u].push(v);
        out[v].push(u);
    }
    let ang = |u: usize, v: usize| (verts[v].1 - verts[u].1).atan2(verts[v].0 - verts[u].0);
    for (u, o) in out.iter_mut().enumerate() {
        o.sort_by(|&a, &b| ang(u, a).total_cmp(&ang(u, b)));
    }
    let mut seen: HashMap<(usize, usize), bool> = HashMap::new();
    let mut faces = Vec::new();
    for &(a, b) in &edges {
        for start in [(a, b), (b, a)] {
            if seen.contains_key(&start) {
                continue;
            }
            let mut ring = Vec::new();
            let mut h = start;
            while seen.insert(h, true).is_none() {
                ring.push(verts[h.0]);
                let (u, v) = h;
                let at = &out[v];
                let i = at.iter().position(|&w| w == u).unwrap_or(0);
                h = (v, at[(i + at.len() - 1) % at.len()]);
            }
            let n = ring.len();
            let area = (0..n)
                .map(|k| ring[k].0 * ring[(k + 1) % n].1 - ring[(k + 1) % n].0 * ring[k].1)
                .sum::<f64>()
                / 2.0;
            if area > 0.0 {
                let perimeter = (0..n).map(|k| dist(ring[k], ring[(k + 1) % n])).sum();
                faces.push(Face {
                    ring,
                    area,
                    perimeter,
                });
            }
        }
    }
    faces
}

/// How many faces of the web are needles of grass.
#[must_use]
pub fn needles(ways: &[Vec<Pt>], tests: &mut Counts) -> usize {
    web_faces(ways, tests)
        .iter()
        .filter(|f| f.is_needle())
        .count()
}
