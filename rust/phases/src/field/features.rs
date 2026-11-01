//! The features in the middle of the fields (feature 444 T16): the pocket pond sunk in one low plot, and the grave - an island
//! that splits its plot in two, or a corner grave the bund is carried round.
//!
//! Research:
//!     ponds, rocks and graves - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: paddy on a broad valley floor - a pond on a low plot, no rock outcrop, may have a grave

use super::fan::Pt;
use super::geom::{dist, seg_dist, signed_area};
use super::lattice::Basin;
use super::rules::{held, FieldRefused};
use crate::pyrand::knob_rng;

/// The share of maps with low plots that sink a pond in one, in hundredths.
///
/// Research:
///     the pond's odds - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a little over half the time, where it has low plots, a GUESS
pub const POND_PCT: u32 = 55;
/// The pond's radii as shares of its plot's shorter side.
///
/// Research:
///     the pond's size - GUESS: the record silent on its size, 0008 sinks it wholly in one plot, never across a bund, and gives no size; 0.4 and 0.28 of the plot's shorter side
pub const POND_SHARE: (f64, f64) = (0.4, 0.28);
/// The share of the room from the pond's middle to its plot's nearest side its longer radius may take.
///
/// Research:
///     the fit - NONE: a margin of the geometry, so the edge stands just inside the plot rather than on its bund
pub const POND_FIT: f64 = 0.95;
/// The share of maps that draw a grave in the fields, in tenths.
///
/// Research:
///     the grave's odds - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: about three maps in ten, this project's choice and an arbitrary one
pub const GRAVE_IN_TEN: u32 = 3;
/// How far a corner grave's middle stands clear of each edge of its corner, and how far every way the plot keeps off a grave's
/// mound (feet): the mound's 6.5 ft half-length and a bund's 1.5.
///
/// Research:
///     the corner grave - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a short step in from its corner, clear of any ditch or path along the plot's edge, with the bund carried round it; the step a GUESS, 8 ft clear of each edge
///     the plot kept off the mound - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on how far; the mound's half-length and a bund, 8 ft every way
pub const CORNER_FT: (f64, f64) = (8.0, 8.0);

/// A pocket pond: its middle and its two radii (feet).
///
/// Research:
///     a pond's record - NONE: the record's type, holding what `pocket_pond` decides
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Pond {
    pub x: f64,
    pub y: f64,
    pub rx: f64,
    pub ry: f64,
}

/// A grave in the fields: where it stands, its form, and the plots it leaves in place of its host (the host's index first).
///
/// Research:
///     a grave's record - NONE: the record's type, holding what `grave` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Grave {
    pub at: Pt,
    pub form: &'static str,
    pub host: usize,
    pub rings: Vec<Vec<Pt>>,
}

/// The mean of a ring's corners.
///
/// Research:
///     the middle - NONE: geometry
fn centroid(ring: &[Pt]) -> Pt {
    #[expect(clippy::cast_precision_loss, reason = "a basin's handful of corners")]
    let n = ring.len() as f64;
    (
        ring.iter().map(|p| p.0).sum::<f64>() / n,
        ring.iter().map(|p| p.1).sum::<f64>() / n,
    )
}

/// The pocket pond, if this map sinks one: in a plot of the lowest row chosen from the seed, at its middle, its radii fitted once
/// inside the middle's least distance to the plot's sides, so its edge lies wholly inside the plot.
///
/// Research:
///     the pond in a low plot - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: sunk wholly in one low plot, never across a bund - sixteen points of its edge held inside the plot
///     the pond's form - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a dish pond's shape and where in its plot; an ellipse squared to the map at the plot's middle
///     the pond's odds - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a little over half the time, where it has low plots (`POND_PCT`)
///     the pond's size - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a dish pond's size; `POND_SHARE` of the plot's shortest side, fitted once to `POND_FIT` of the room from its middle to the plot's nearest side where that is smaller
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn pocket_pond(
    basins: &[Basin],
    seed: i64,
    tag: &str,
    work: &mut u64,
) -> Option<(usize, Pond)> {
    let last = basins.iter().map(|b| b.row).max()?;
    let low: Vec<usize> = (0..basins.len())
        .filter(|&i| basins[i].row == last)
        .collect();
    let mut rng = knob_rng(seed, &format!("{tag}:pond"));
    if low.is_empty() || rng.randbelow(100) >= POND_PCT {
        return None;
    }
    let i = low[rng.randbelow(u32::try_from(low.len()).ok()?) as usize];
    let r = &basins[i].ring;
    let short = (0..r.len())
        .map(|k| dist(r[k], r[(k + 1) % r.len()]))
        .fold(f64::INFINITY, f64::min);
    let (x, y) = centroid(r);
    let (mut rx, mut ry) = (short * POND_SHARE.0, short * POND_SHARE.1);
    if !super::geom::inside((x, y), r) {
        return None;
    }
    let mut within = |rx: f64, ry: f64| {
        *work += 16;
        (0..16).all(|k| {
            let a = f64::from(k) / 16.0 * std::f64::consts::TAU;
            super::geom::inside((x + rx * a.cos(), y + ry * a.sin()), r)
        })
    };
    // the radii fitted once, not shrunk until they pass (the MODE BUDGET, T16): an ellipse whose longer radius is under the middle's
    // least distance to the plot's sides lies within that disc, and so within the plot
    let room = (0..r.len())
        .map(|k| seg_dist((x, y), r[k], r[(k + 1) % r.len()]))
        .fold(f64::INFINITY, f64::min);
    let fit = (room * POND_FIT / rx.max(ry)).min(1.0);
    rx *= fit;
    ry *= fit;
    within(rx, ry).then_some((i, Pond { x, y, rx, ry }))
}

/// The grave, if this map draws one: a plot rolled from the seed (never `skip`, the pond's), its form `form` (the `grave_form`
/// knob, rolled by the caller from its table). An island splits its host through the mound into two plots across the fall, each
/// notched `CORNER_FT.1` round the mound; a corner grave carves a corner rolled from the seed round its mound, set `CORNER_FT.0`
/// clear of both its edges. A cut that would break a basin's rule is refused, and the next plot tried, a bounded number of times.
///
/// Research:
///     the island splits its plot - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: the host plot is split in two through the mound, as if a bund were run out to the island, and each half stops short of the mound, a GUESS - the split across the fall, from one side's middle to the other's
///     the bund round the corner - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a corner grave stands a short step in from its corner, clear of any ditch or path along the plot's edge, and the plot's bund is carried round it out to the corner, a GUESS - the corner rolled among the plot's four
///     no basin under the grave - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: no flooded basin runs under a field grave; the paddy is carved round it
///     the grave's odds - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: about three maps in ten draw a grave in the fields (`GRAVE_IN_TEN`)
///     its host - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on which plot keeps a grave; any of the field's plots at even odds, the low ones among them, the pond's plot excepted
///
/// # Errors
/// `FieldRefused` when no plot tried takes the grave within its rules.
pub fn grave(
    basins: &[Basin],
    seed: i64,
    tag: &str,
    form: &'static str,
    skip: Option<usize>,
    cell: f64,
    work: &mut u64,
) -> Result<Option<Grave>, FieldRefused> {
    let mut rng = knob_rng(seed, &format!("{tag}:grave"));
    if basins.is_empty() || rng.randbelow(10) >= GRAVE_IN_TEN {
        return Ok(None);
    }
    let n = u32::try_from(basins.len()).unwrap_or(u32::MAX);
    for _ in 0..8 {
        let host = rng.randbelow(n) as usize;
        if Some(host) == skip {
            continue;
        }
        let plot = &basins[host].ring;
        *work += 1;
        let (at, rings) = if form == "island" {
            island(plot)
        } else {
            let k = rng.randbelow(4) as usize;
            let r: Vec<Pt> = (0..4).map(|j| plot[(k + j) % 4]).collect();
            corner(&r)
        };
        *work += rings.iter().map(|x| x.len() as u64).sum::<u64>();
        if rings
            .iter()
            .all(|x| held(x, cell).is_ok() && signed_area(x).abs() > 0.0)
        {
            return Ok(Some(Grave {
                at,
                form,
                host,
                rings,
            }));
        }
    }
    Err(FieldRefused {
        rule: "the grave's host",
        detail: format!("no plot of {} took a {form} grave", basins.len()),
    })
}

/// An island grave in `r`: the mound at the middle of the split across the fall (from `r[0]`-`r[3]`'s middle to `r[1]`-`r[2]`'s),
/// the two halves notched `CORNER_FT.1` every way round it.
///
/// Research:
///     the split and its notch - NONE: geometry; the rules are `grave`'s
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn island(r: &[Pt]) -> (Pt, Vec<Vec<Pt>>) {
    let (a, b) = (mid(r[0], r[3]), mid(r[1], r[2]));
    let m = mid(a, b);
    let e = super::geom::unit(a, b);
    let keep = CORNER_FT.1;
    // the side of the split the upper half lies on
    let side = if (r[0].0 - a.0) * -e.1 + (r[0].1 - a.1) * e.0 >= 0.0 {
        1.0
    } else {
        -1.0
    };
    let n = (-e.1 * side, e.0 * side);
    let at = |s: f64, h: f64| (m.0 + e.0 * s + n.0 * h, m.1 + e.1 * s + n.1 * h);
    let upper = vec![
        r[0],
        r[1],
        b,
        at(keep, 0.0),
        at(keep, keep),
        at(-keep, keep),
        at(-keep, 0.0),
        a,
    ];
    let lower = vec![
        a,
        at(-keep, 0.0),
        at(-keep, -keep),
        at(keep, -keep),
        at(keep, 0.0),
        b,
        r[2],
        r[3],
    ];
    (m, vec![upper, lower])
}

/// A corner grave in `r`'s first corner: its middle `CORNER_FT.0` clear of both edges along the corner's bisector, the corner cut
/// off along a chord that keeps `CORNER_FT.1` clear of it.
///
/// Research:
///     the carve - NONE: geometry; the rules are `grave`'s
fn corner(r: &[Pt]) -> (Pt, Vec<Vec<Pt>>) {
    let (e1, e3) = (super::geom::unit(r[0], r[1]), super::geom::unit(r[0], r[3]));
    let bis = super::geom::unit((0.0, 0.0), (e1.0 + e3.0, e1.1 + e3.1));
    let half = (e1.0 * e3.0 + e1.1 * e3.1).clamp(-1.0, 1.0).acos() / 2.0;
    let out = CORNER_FT.0 / half.sin().max(0.1);
    let at = (r[0].0 + bis.0 * out, r[0].1 + bis.1 * out);
    let reach = (out + CORNER_FT.1) / half.cos().max(0.1);
    (
        at,
        vec![vec![
            toward(r[0], r[1], reach),
            r[1],
            r[2],
            r[3],
            toward(r[0], r[3], reach),
        ]],
    )
}

/// The midpoint of two points.
///
/// Research:
///     the midpoint - NONE: geometry
fn mid(a: Pt, b: Pt) -> Pt {
    (f64::midpoint(a.0, b.0), f64::midpoint(a.1, b.1))
}

/// The point `d` feet from `a` toward `b`.
///
/// Research:
///     the step - NONE: geometry
fn toward(a: Pt, b: Pt, d: f64) -> Pt {
    let u = super::geom::unit(a, b);
    (a.0 + u.0 * d, a.1 + u.1 * d)
}

#[cfg(test)]
mod tests {
    use super::{grave, island, pocket_pond};
    use crate::field::fan::fan;
    use crate::field::geom::{inside, signed_area};
    use crate::field::lattice::Basin;
    use crate::field::lattice::{basins, ROW_FT};
    use crate::field::rules::held;

    #[test]
    fn the_pond_sits_in_a_low_plot_and_the_grave_keeps_the_rules() {
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0), 4);
        let b = basins(&f, 4, ROW_FT);
        let last = b.iter().map(|x| x.row).max().unwrap();
        let ponds: Vec<_> = (0..40)
            .filter_map(|s| pocket_pond(&b, s, "f0", &mut 0))
            .collect();
        assert!((10..35).contains(&ponds.len()));
        for (i, p) in &ponds {
            assert_eq!(b[*i].row, last);
            assert!(
                inside((p.x + p.rx, p.y), &b[*i].ring) || inside((p.x, p.y + p.rx), &b[*i].ring)
            );
        }
        let mut seen = (0, 0);
        for s in 0..40 {
            for form in ["island", "corner"] {
                if let Some(g) = grave(&b, s, "f0", form, None, 1488.0, &mut 0).unwrap() {
                    let whole = signed_area(&b[g.host].ring).abs();
                    let parts: f64 = g.rings.iter().map(|r| signed_area(r).abs()).sum();
                    assert!(parts <= whole + 1e-6);
                    assert!(g.rings.iter().all(|r| held(r, 1488.0).is_ok()));
                    // the mound stands clear of every ring it leaves
                    assert!(g.rings.iter().all(|r| !inside(g.at, r)));
                    if form == "island" {
                        seen.0 += 1;
                        // the halves stop short of the mound
                        assert!(whole - parts > 4.0 * 8.0 * 8.0 - 1e-6);
                    } else {
                        seen.1 += 1;
                    }
                }
            }
        }
        assert!(seen.0 > 3 && seen.1 > 3, "{seen:?}");
        assert!(pocket_pond(&[], 1, "f0", &mut 0).is_none());
        assert!(grave(&[], 1, "f0", "island", None, 1488.0, &mut 0)
            .unwrap()
            .is_none());
        let tiny: Vec<_> = b.iter().take(1).cloned().collect();
        let refused =
            (0..40).find_map(|s| grave(&tiny, s, "f0", "island", Some(0), 1488.0, &mut 0).err());
        assert!(refused.is_some());
        // a skewed sliver of a plot: the pond shrunk until its edge is inside, or none where no size fits
        let sliver = |w: f64| Basin {
            row: 0,
            col: 0,
            ring: vec![(0.0, 0.0), (200.0, 160.0), (200.0 + w, 160.0), (w, 0.0)],
            on_drain_right: false,
            on_drain_left: false,
        };
        let fits: Vec<_> = (0..60)
            .filter_map(|s| pocket_pond(&[sliver(60.0)], s, "f0", &mut 0))
            .collect();
        assert!(!fits.is_empty() && fits.iter().all(|(_, p)| p.rx < 0.4 * 60.0));
        let chevron = Basin {
            ring: vec![
                (0.0, 0.0),
                (100.0, 100.0),
                (200.0, 0.0),
                (200.0, 10.0),
                (100.0, 110.0),
                (0.0, 10.0),
            ],
            ..sliver(0.0)
        };
        // its middle outside it: no pond
        assert!((0..60).all(|s| pocket_pond(&[chevron.clone()], s, "f0", &mut 0).is_none()));
        // an island split on a ring wound the other way: its mound still clear of both halves
        let (at, halves) = island(&[(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]);
        assert!(halves.iter().all(|h| !inside(at, h)));
        // a cell so large no half of a split plot holds a quarter of it: every host tried refuses
        let big = (0..40).find_map(|s| grave(&b, s, "f0", "island", None, 1e5, &mut 0).err());
        assert!(big.is_some_and(|e| e.rule == "the grave's host"));
    }
}
