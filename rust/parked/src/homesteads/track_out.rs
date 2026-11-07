//! The track out chosen once the last house stands (feature 444 T30): the homesteads as seated standing in for the farmsteads not
//! yet drawn - each household's house, threshing yard, beds, storehouse annex, byre and fixtures (a persimmon by its trunk), and
//! its wood seats as octagons of the reach a lane keeps off them - and the track's stretch about the cluster the households' ways
//! are laid to (`homesteads/household_ways.py` `seated_parts`, `seat_walls`, `near_the_cluster`; `region.py` `_clip`).
//!
//! Research:
//!     houses before lanes - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every farmhouse seated before any way is laid; the track out leaves from the cluster's edge and each household's way joins it
//!     nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the track out keeps off every homestead's house, yard, beds, well, sheds and fixtures as they will be drawn
//!     the track off the wood seats - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a lane kept off a household's copse seat by the crown's reach (or 0.45 of the clump and 4 ft) and 4 ft more; no page read shows a lane between a farmhouse and its own grove, and none gives how far a way kept off one
//!     its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (octagon standing in for a circle)

use super::fixtures::Kind;
use super::layout::Rect;
use super::place::Seated;
use super::wood::CLUMP_FT;
use crate::field::fan::Pt;

/// A persimmon's trunk box, the part of it a way keeps off (ft).
///
/// Research:
///     a persimmon by its trunk alone - GUESS: held off by a 4 ft trunk box, the crown free to overhang the path
pub const TRUNK_FT: f64 = 4.0;

/// What a seated part is, as the ways read it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Part {
    /// A farmhouse.
    House,
    /// A threshing yard.
    Yard,
    /// A kitchen bed.
    Garden,
    /// A storehouse annex or a byre.
    Shed,
    /// A fixture.
    Fixture,
    /// A reserved wood seat.
    WoodSeat,
}

/// A box `(cx, cy, w, h)` as its four corners.
#[must_use]
pub fn box_poly(b: Rect) -> Vec<Pt> {
    let (x0, y0, x1, y1) = (
        b.0 - b.2 / 2.0,
        b.1 - b.3 / 2.0,
        b.0 + b.2 / 2.0,
        b.1 + b.3 / 2.0,
    );
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

/// The reach a lane keeps off a wood seat: the crown's reach from its clump's seat (the clump's box less 2 ft a side, the crown
/// drawn its lift higher), or 0.45 of the clump and 4 ft, and 4 ft more.
///
/// Research:
///     crown drawn above its throw - CONVENTION: 3 bscale units up the sheet at the grove's grain (0.82)
#[must_use]
pub fn seat_reach(bscale: f64) -> f64 {
    let (clump, lift) = (CLUMP_FT * bscale, 3.0 * bscale / 0.82);
    let half = clump / 2.0 - 2.0;
    (clump * 0.45 + 4.0).max(half.hypot(half + lift)) + 4.0
}

/// The homesteads as seated: every part's box as the ways read it (the house's, yard's and annexes' turned boxes, each bed's,
/// each fixture's, a persimmon by its trunk), and each reserved wood seat as an octagon of `reach`.
#[must_use]
pub fn seated_parts(seated: &[Seated], reach: f64) -> Vec<(Vec<Pt>, Part)> {
    let mut out = Vec::new();
    for s in seated {
        let b = &s.bundle;
        let mut boxes = b.boxes.iter().copied();
        let mut take = |n: usize, part: Part, out: &mut Vec<(Vec<Pt>, Part)>| {
            out.extend(boxes.by_ref().take(n).map(|r| (box_poly(r), part)));
        };
        take(1, Part::House, &mut out);
        take(1, Part::Yard, &mut out);
        take(b.gardens.len(), Part::Garden, &mut out);
        take(
            usize::from(b.kura.is_some()) + usize::from(b.byre.is_some()),
            Part::Shed,
            &mut out,
        );
        for (&(kind, _), r) in b.fixtures.iter().zip(boxes.by_ref()) {
            let r = if kind == Kind::Persimmon {
                (r.0, r.1, TRUNK_FT, TRUNK_FT)
            } else {
                r
            };
            out.push((box_poly(r), Part::Fixture));
        }
        for p in &s.wood {
            let ring = (0..8)
                .map(|k| {
                    let a = f64::from(k) * std::f64::consts::FRAC_PI_4;
                    (p.0 + a.cos() * reach, p.1 + a.sin() * reach)
                })
                .collect();
            out.push((ring, Part::WoodSeat));
        }
    }
    out
}

/// The span `(t0, t1)` of the segment a-b, as fractions of it, inside the box (Liang-Barsky); None where it misses.
#[must_use]
pub fn clip(a: Pt, b: Pt, bx: (f64, f64, f64, f64)) -> Option<(f64, f64)> {
    let (mut t0, mut t1) = (0.0f64, 1.0f64);
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    for (p, q) in [
        (-dx, a.0 - bx.0),
        (dx, bx.2 - a.0),
        (-dy, a.1 - bx.1),
        (dy, bx.3 - a.1),
    ] {
        if p == 0.0 {
            if q < 0.0 {
                return None;
            }
            continue;
        }
        let r = q / p;
        if p < 0.0 {
            t0 = t0.max(r);
        } else {
            t1 = t1.min(r);
        }
    }
    (t0 <= t1).then_some((t0, t1))
}

/// The legs of the track within `margin` of the seated homesteads' extent and the track's start, each clipped to it: the stretch
/// the households' ways are laid to. Every leg where nothing is seated.
#[must_use]
pub fn near_the_cluster(placed: &[Rect], track: &[Pt], margin: f64) -> Vec<(Pt, Pt)> {
    let legs = track.windows(2).map(|w| (w[0], w[1]));
    if placed.is_empty() {
        return legs.collect();
    }
    let g = track.first().copied().unwrap_or((placed[0].0, placed[0].1));
    let bx = placed.iter().fold((g.0, g.1, g.0, g.1), |m, b| {
        (
            m.0.min(b.0 - b.2 / 2.0),
            m.1.min(b.1 - b.3 / 2.0),
            m.2.max(b.0 + b.2 / 2.0),
            m.3.max(b.1 + b.3 / 2.0),
        )
    });
    let bx = (bx.0 - margin, bx.1 - margin, bx.2 + margin, bx.3 + margin);
    legs.filter_map(|(a, b)| {
        let (t0, t1) = clip(a, b, bx).filter(|s| s.1 > s.0)?;
        Some((
            (a.0 + (b.0 - a.0) * t0, a.1 + (b.1 - a.1) * t0),
            (a.0 + (b.0 - a.0) * t1, a.1 + (b.1 - a.1) * t1),
        ))
    })
    .collect()
}
