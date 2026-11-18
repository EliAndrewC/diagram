//! The placer's candidate seats (feature 449 T151, `labels/placer.py`'s generators): round a point, along a line, inside an area, the
//! fallback's slides and the leader rings - each in the Python's order, so the first free seat is the Python's. Each generator returns
//! its seats whole where the Python yielded them lazily; `place` asks the next generator only when the one before found nothing free, as
//! the Python's lazy chain did, and building a seat has no effect, so the seats it tries are the same.
//!
//! Research: caption search plumbing - NONE: candidate bookkeeping, geometry and search bounds

#![expect(
    clippy::similar_names,
    reason = "the Python's names, kept so each line reads against its original (x0 and x1, bx0 and by0)"
)]

use super::super::geom::{
    area_centroid, bbox, centroid, dist, inside, open_edges, seg_closest, Pt,
};
use super::super::layout::layouts;
use super::super::standard::{
    block_half, pitch_sum, upright, HUG_PX, LINE_H_EM, POSITIONS, PREFERRED_OFFSET_EM, REACH_EM,
    RING_STEP_EM,
};
use super::{Kind, Subject};
use crate::py::{half_sum, max, min, sum};

/// How many interior seats an area caption tries, nearest the centroid first - a search bound, not a rule.
pub const AREA_SEATS: usize = 400;

/// How many stations along a line a line caption tries, nearest its hint first - a search bound, not a rule.
pub const LINE_STATIONS: usize = 13;

/// How many steps the extended search slides a caption along each side of a point subject (feature 286): the ranked positions alone
/// missed free seats a person found beside small subjects.
pub const EXTENDED_SLIDES: u32 = 8;

/// How many times the standard's inside seats the fallback samples an area with, at no coarser than a quarter em (feature 286).
pub const EXTENDED_AREA_FACTOR: f64 = 5.0;

/// How far, in whole pixels each way, the least-cost seat is nudged for a cheaper one (feature 286).
pub const NUDGE_PX: i32 = 3;

/// The farthest ring any seat stands on (feature 287, labels L10): the hug less the farthest a nudge can carry a seat.
///
/// Research: the hug - CONVENTION: no seat past the hug from what it names, the nudge's reach held back from it
pub static HUG_RING: std::sync::LazyLock<f64> =
    std::sync::LazyLock::new(|| HUG_PX - f64::from(NUDGE_PX) * 2.0_f64.sqrt());

/// One seat tried: its ring (0 the preferred offset), its rank within the ring, the position's name, the block's center and angle, its
/// lines, its half-extents and the caption's size.
#[derive(Debug, Clone, PartialEq)]
pub struct Cand {
    pub ring: usize,
    pub rank: usize,
    pub position: &'static str,
    pub center: Pt,
    pub angle: f64,
    pub lines: Vec<String>,
    pub half: (f64, f64),
    pub size: f64,
}

/// What every generator is handed: the caption's size, its layouts, its width per character, each fixed line's size, and the rings.
pub(super) struct Gen<'a> {
    pub size: f64,
    pub char_w: f64,
    pub lays: &'a [Vec<String>],
    pub line_sizes: Option<&'a [f64]>,
    pub ring_gaps: Option<&'a [(usize, f64)]>,
}

/// A caption block's half-extents, each line at its own size when `line_sizes` gives them (a name over a smaller gloss): measured at the
/// head's size, Hayakawa's bath and HEARING COURT were too tall for any seat (feature 286).
///
/// Research: a caption's block by its lines' own sizes - NONE: the text metrics applied, each line at its size
#[must_use]
pub fn sized_half(
    lines: &[String],
    size: f64,
    char_w: f64,
    line_sizes: Option<&[f64]>,
) -> (f64, f64) {
    let (bw, mut bh) = block_half(lines, size, char_w);
    if let Some(sizes) = line_sizes.filter(|s| !s.is_empty()) {
        bh = half_sum(sizes[0] * LINE_H_EM, pitch_sum(&sizes[1..]));
    }
    (bw, bh)
}

/// The ring distances for a caption of `size`: the preferred offset, then a step at a time out to the reach - never past the hug
/// ([`HUG_RING`]), whatever the caption's size.
///
/// Research: nearer first - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the preferred offset, then a half em a ring out to the reach, never past the hug
#[must_use]
pub fn rings(size: f64) -> Vec<f64> {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "`int(round(...)) + 1` of the standard's constants, sixteen"
    )]
    let n = ((REACH_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM).round_ties_even() as u32 + 1;
    (0..n)
        .filter_map(|k| {
            let g = (PREFERRED_OFFSET_EM + f64::from(k) * RING_STEP_EM) * size;
            (k == 0 || g <= *HUG_RING).then(|| min(g, *HUG_RING))
        })
        .collect()
}

/// The LEADER rings (feature 287, D10): past the standard's reach, a step at a time out to the hug, each with its ring number. A caption
/// of no size has no ring past the reach: the Python's loop never ended there (reported, feature 449 T151).
///
/// Research: leader rings - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: past the reach out to the hug, each seat tied back by a leader
#[must_use]
pub fn outer_rings(size: f64) -> Vec<(usize, f64)> {
    let mut k = rings(size).len();
    let mut out = Vec::new();
    if size.is_nan() || size <= 0.0 {
        return out;
    }
    loop {
        #[expect(clippy::cast_precision_loss, reason = "a ring number, under a hundred")]
        let g = (PREFERRED_OFFSET_EM + k as f64 * RING_STEP_EM) * size;
        if g > *HUG_RING {
            return out;
        }
        out.push((k, g));
        k += 1;
    }
}

/// The frame turned by `angle` degrees: its two axes.
pub(super) fn frame_of(angle: f64) -> (Pt, Pt) {
    let a = angle.to_radians();
    ((a.cos(), a.sin()), (-a.sin(), a.cos()))
}

fn ringed(size: f64, ring_gaps: Option<&[(usize, f64)]>) -> Vec<(usize, f64)> {
    ring_gaps.map_or_else(
        || rings(size).into_iter().enumerate().collect(),
        <[_]>::to_vec,
    )
}

/// The subject's box in the frame turned by `ang`: its center, the frame's two axes and its half-extents.
fn box_frame(subject: &Subject, ang: f64) -> (Pt, Pt, Pt, f64, f64) {
    let (u, v) = frame_of(ang);
    let c = centroid(&subject.poly);
    let pu: Vec<f64> = subject
        .poly
        .iter()
        .map(|p| (p.0 - c.0) * u.0 + (p.1 - c.1) * u.1)
        .collect();
    let pv: Vec<f64> = subject
        .poly
        .iter()
        .map(|p| (p.0 - c.0) * v.0 + (p.1 - c.1) * v.1)
        .collect();
    let lo_hi = |xs: &[f64]| {
        let lo = xs[1..].iter().copied().fold(xs[0], min);
        let hi = xs[1..].iter().copied().fold(xs[0], max);
        (lo, hi)
    };
    let ((ulo, uhi), (vlo, vhi)) = (lo_hi(&pu), lo_hi(&pv));
    let (cu, cv) = (half_sum(ulo, uhi), half_sum(vlo, vhi));
    let c = (c.0 + cu * u.0 + cv * v.0, c.1 + cu * u.1 + cv * v.1); // the center of the subject's box in its frame
    (c, u, v, (uhi - ulo) / 2.0, (vhi - vlo) / 2.0)
}

/// The ranked positions in the feature's own turned frame, the gap from its drawn edge.
///
/// Research: seats round a point - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the ranked positions in the feature's own turned frame, the gap from its drawn edge
pub(super) fn point_cands(g: &Gen<'_>, subject: &Subject) -> Vec<Cand> {
    let ang = upright(subject.angle);
    let (c, u, v, su, sv) = box_frame(subject, ang);
    let r2 = 2.0_f64.sqrt();
    let mut out = Vec::new();
    for (ring, gap) in ringed(g.size, g.ring_gaps) {
        for (rank, &(name, sx, sy)) in POSITIONS.iter().enumerate() {
            for lines in g.lays {
                let (bw, bh) = sized_half(lines, g.size, g.char_w, g.line_sizes);
                #[expect(clippy::float_cmp, reason = "the Python's test of a whole-number sign")]
                let corner = sx.abs() == 1.0 && sy != 0.0;
                let (du, dv) = if corner {
                    // A CORNER: the block's near corner stands `gap` from the subject's corner, along the diagonal
                    (sx * (su + bw + gap / r2), sy * (sv + bh + gap / r2))
                } else if sy == 0.0 {
                    (sx * (su + bw + gap), 0.0)
                } else {
                    (sx * 2.0 * bw, sy * (sv + bh + gap))
                };
                out.push(Cand {
                    ring,
                    rank,
                    position: name,
                    center: (c.0 + du * u.0 + dv * v.0, c.1 + du * u.1 + dv * v.1),
                    angle: ang,
                    lines: lines.clone(),
                    half: (bw, bh),
                    size: g.size,
                });
            }
        }
    }
    out
}

/// Where a line's walk `s` from its start lands, and the bearing of the segment it lands on; the last segment takes any remainder, a
/// segment equal to the last by its ends among them, as the Python's `(a, b) == segs[-1]` compared them.
fn at(segs: &[(Pt, Pt)], lengths: &[f64], mut s: f64) -> (Pt, f64) {
    let last = segs[segs.len() - 1];
    let mut k = 0;
    // the walk ends at the last segment at the latest, which equals itself
    while !(s <= lengths[k] || segs[k] == last) {
        s -= lengths[k];
        k += 1;
    }
    let ((from, to), ln) = (segs[k], lengths[k]);
    let along = if ln == 0.0 { 0.0 } else { min(1.0, s / ln) };
    let here = (
        from.0 + (to.0 - from.0) * along,
        from.1 + (to.1 - from.1) * along,
    );
    (here, (to.1 - from.1).atan2(to.0 - from.0).to_degrees())
}

/// Seats along a line, at its bearing, above before below. A line of one point has no segment: [`super::place`] refuses it first, as the
/// Python raised on it.
///
/// Research:
///     a line's caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: along the line at its bearing, above before below, never upside down
///     stations along the line - NONE: two ems apart from the hint, a search bound
pub(super) fn line_cands(g: &Gen<'_>, subject: &Subject) -> Vec<Cand> {
    let segs: Vec<(Pt, Pt)> = open_edges(&subject.poly).collect();
    let lengths: Vec<f64> = segs.iter().map(|&(a, b)| dist(a, b)).collect();
    let total = sum(lengths.iter().copied());
    let s0 = match subject.hint {
        Some(hint) => {
            let near = |i: usize| dist(hint, seg_closest(hint, segs[i].0, segs[i].1));
            let best = (1..segs.len()).fold(0, |b, i| if near(i) < near(b) { i } else { b });
            let q = seg_closest(hint, segs[best].0, segs[best].1);
            sum(lengths[..best].iter().copied()) + dist(segs[best].0, q)
        }
        None => total / 2.0,
    };
    let step = 2.0 * g.size;
    let mut stations = vec![s0];
    for j in 1..LINE_STATIONS {
        #[expect(
            clippy::cast_precision_loss,
            reason = "a station number, under thirteen"
        )]
        let jf = j as f64;
        for s in [s0 + jf * step, s0 - jf * step] {
            if (0.0..=total).contains(&s) {
                stations.push(s);
            }
        }
    }
    stations.truncate(LINE_STATIONS);
    let mut out = Vec::new();
    for (ring, gap) in ringed(g.size, g.ring_gaps) {
        for (j, &s) in stations.iter().enumerate() {
            let (p, bearing) = at(&segs, &lengths, s);
            let ang = upright(bearing);
            let (_u, v) = frame_of(ang);
            for (side, name) in [(-1.0, "above"), (1.0, "below")] {
                // above the line before below (psu-geog486-point-labels)
                for lines in g.lays {
                    let (bw, bh) = sized_half(lines, g.size, g.char_w, g.line_sizes);
                    let d = subject.half_width + gap + bh;
                    out.push(Cand {
                        ring,
                        rank: j * 2 + usize::from(side > 0.0),
                        position: name,
                        center: (p.0 + side * d * v.0, p.1 + side * d * v.1),
                        angle: ang,
                        lines: lines.clone(),
                        half: (bw, bh),
                        size: g.size,
                    });
                }
            }
        }
    }
    out
}

/// The grid points of a box at `step`, `int((x1 - x0) / step) + 1` across and down, column by column.
fn grid(b: (f64, f64, f64, f64), step: f64) -> Vec<Pt> {
    let (x0, y0, x1, y1) = b;
    let n =
        |span: f64| crate::py::int(span / step).map_or(0, |k| usize::try_from(k + 1).unwrap_or(0));
    let mut out = Vec::new();
    for i in 0..n(x1 - x0) {
        for j in 0..n(y1 - y0) {
            #[expect(clippy::cast_precision_loss, reason = "a grid index, small")]
            out.push((x0 + i as f64 * step, y0 + j as f64 * step));
        }
    }
    out
}

/// The grid points inside the polygon, nearest `c` first (a stable sort, as Python's `sorted`).
fn inside_by_distance(poly: &[Pt], step: f64, c: Pt) -> Vec<Pt> {
    let mut pts: Vec<(f64, Pt)> = grid(bbox(poly), step)
        .into_iter()
        .filter(|p| inside(p.0, p.1, poly))
        .map(|p| (dist(p, c), p))
        .collect();
    pts.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
    pts.into_iter().map(|(_, p)| p).collect()
}

/// Inside the area, its centroid first, then the one-em grid's points inside it, nearest the centroid first.
///
/// Research: an area's caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: inside the area, its centroid first
pub(super) fn area_cands(g: &Gen<'_>, subject: &Subject) -> Vec<Cand> {
    let ang = upright(subject.angle);
    let c = area_centroid(&subject.poly);
    let mut seats = vec![c];
    seats.extend(
        inside_by_distance(&subject.poly, g.size, c)
            .into_iter()
            .take(AREA_SEATS - 1),
    );
    let mut out = Vec::new();
    for (rank, p) in seats.into_iter().enumerate() {
        for lines in g.lays {
            out.push(Cand {
                ring: 0,
                rank,
                position: "inside",
                center: p,
                angle: ang,
                lines: lines.clone(),
                half: sized_half(lines, g.size, g.char_w, g.line_sizes),
                size: g.size,
            });
        }
    }
    out
}

/// THE FALLBACK SEARCH (feature 286), tried only when the standard's candidates found no free seat: an area's inside sampled over its
/// whole extent, the step set by its size; round a point subject, the block slid along each side between the ranked positions, ring by
/// ring. A line subject's stations already walk its length, so it adds nothing.
///
/// Research: fallback seats - CONVENTION: slides between the ranked seats, and a finer grid inside an area, when none is free
pub(super) fn extended_cands(g: &Gen<'_>, subject: &Subject) -> Vec<Cand> {
    let ang = upright(subject.angle);
    let mut out = Vec::new();
    match subject.kind {
        Kind::Area => {
            let (x0, y0, x1, y1) = bbox(&subject.poly);
            #[expect(clippy::cast_precision_loss, reason = "the seat bound, four hundred")]
            let seats = EXTENDED_AREA_FACTOR * AREA_SEATS as f64;
            let step = max(
                g.size / 4.0,
                (max((x1 - x0) * (y1 - y0), 1e-9) / seats).sqrt(),
            );
            let c = area_centroid(&subject.poly);
            for (rank, p) in inside_by_distance(&subject.poly, step, c)
                .into_iter()
                .enumerate()
            {
                for ln in g.lays {
                    out.push(Cand {
                        ring: 0,
                        rank,
                        position: "inside",
                        center: p,
                        angle: ang,
                        lines: ln.clone(),
                        half: sized_half(ln, g.size, g.char_w, g.line_sizes),
                        size: g.size,
                    });
                }
            }
        }
        Kind::Line => {}
        Kind::Point => {
            let (c, u, v, su, sv) = box_frame(subject, ang);
            let slides: Vec<f64> = (0..=EXTENDED_SLIDES)
                .map(|k| -1.0 + 2.0 * f64::from(k) / f64::from(EXTENDED_SLIDES))
                .collect();
            for (ring, gap) in ringed(g.size, g.ring_gaps) {
                for ln in g.lays {
                    let (bw, bh) = sized_half(ln, g.size, g.char_w, g.line_sizes);
                    let mut rank = 0;
                    let mut push = |name: &'static str, center: Pt| {
                        out.push(Cand {
                            ring,
                            rank,
                            position: name,
                            center,
                            angle: ang,
                            lines: ln.clone(),
                            half: (bw, bh),
                            size: g.size,
                        });
                        rank += 1;
                    };
                    for (name, side) in [("above", -1.0), ("below", 1.0)] {
                        for &s in &slides {
                            let center = (
                                c.0 + s * (su + bw) * u.0 + side * (sv + bh + gap) * v.0,
                                c.1 + s * (su + bw) * u.1 + side * (sv + bh + gap) * v.1,
                            );
                            push(name, center);
                        }
                    }
                    // right before left, as in `POSITIONS` (feature 290)
                    for (name, side) in [("right", 1.0), ("left", -1.0)] {
                        for &s in &slides {
                            let center = (
                                c.0 + side * (su + bw + gap) * u.0 + s * (sv + bh) * v.0,
                                c.1 + side * (su + bw + gap) * u.1 + s * (sv + bh) * v.1,
                            );
                            push(name, center);
                        }
                    }
                }
            }
        }
    }
    out
}

/// The layouts a caption tries: its fixed lines, or the wrap rule's.
pub(super) fn lays_of(text: &str, lines: Option<&[String]>) -> Vec<Vec<String>> {
    lines.map_or_else(|| layouts(text), |l| vec![l.to_vec()])
}

#[cfg(test)]
mod tests;
