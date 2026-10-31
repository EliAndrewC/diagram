//! The polder (feature 444 T16 D8): the block of modules the households' paddy fills, its lattice bowed and nudged (the rice
//! polder) or drifted (the dike-pond mosaic), its plots - strips on the rice polder, ponds' parcels on the dike-pond - the ring
//! canal at the dike's inside foot, a field ditch in each column corridor, the two sluices and the wild pond that feeds it.
//! Written from `phases/polder_greenfield.derivation.md` and `phases/field.md`'s "The polder's design, next"; the old code unread.
//! The dike, its trees, the reed fringe and the dike-pond's ponds are the free helpers' (`perimeter_dike`, `marsh`,
//! `apply_land_use`), which the thin Python calls with these records.
//!
//! Research:
//!     the rice polder's grid - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a rice polder is drawn on a surveyed grid
//!     the modules - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: square modules about 190 ft on a side; a dike-pond block a smaller module, about 160 ft, most merged in pairs

use super::fan::{heading, Pt};
use crate::pyrand::knob_rng;

/// A rice polder's module and a dike-pond block's (feet on a side).
///
/// Research:
///     the modules - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: about 190 ft on a side; a dike-pond block about 160 ft
pub const MODULE_FT: (f64, f64) = (190.0, 160.0);
/// The rice polder's gaps: a column corridor holding a field ditch, and a walking bund between rows and between strips (feet).
///
/// Research:
///     the gaps - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: a walking bund about 3 ft wide, or a field ditch with its banks, about 8 ft
pub const POLDER_GAP_FT: (f64, f64) = (8.0, 3.0);
/// The dike-pond block's gaps, both ways (feet).
///
/// Research:
///     the gaps - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: a pond's parcel about 160 by 320 ft, with gaps of about 22 ft both ways
pub const POND_GAP_FT: f64 = 22.0;
/// The most a rice polder's line bows and a crossing is nudged (feet).
///
/// Research:
///     the bow and the nudge - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: each row and column line takes its own gentle bow and each crossing is nudged a few feet; the figures a GUESS, 6 and 3 ft
pub const BOW_NUDGE_FT: (f64, f64) = (6.0, 3.0);
/// The dike-pond mosaic's drift at the block's middle, as a share of a module (it fades to nothing at the edge).
///
/// Research:
///     the mosaic's drift - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a smooth drift that fades to nothing at the fixed outer edge; how strongly is a calibrated liberty, a GUESS of 0.15 of a module
pub const DRIFT_SHARE: f64 = 0.15;
/// Of this many rice polder modules, one is merged with the next down the fall; of this many dike-pond modules, one stands alone.
///
/// Research:
///     merged modules - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: a few merge along the fall of the ground; most merged in pairs; the shares a GUESS, one in eight and one in six
pub const MERGE_IN: (u32, u32) = (8, 6);
/// How far outside the plots the ring canal runs, and the dike's inner face outside it (feet).
///
/// Research:
///     the ring canal - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a ring canal round the inside foot of the dike, on the field side; the offsets a GUESS, 6 and 12 ft
pub const RING_FT: (f64, f64) = (6.0, 12.0);
/// The wild pond's radii, and its middle's distance outside the inlet (feet).
///
/// Research:
///     the wild pond - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the wild pond that feeds the polder stands to its northwest, at the head; its size SILENT, Kuwabata's 82 and 54 ft and 140 ft out, a GUESS
pub const POND_FT: (f64, f64, f64) = (82.0, 54.0, 140.0);

/// One polder plot: its row and column of modules, its ring, and whether it lies on the block's low row.
#[derive(Debug, Clone, PartialEq)]
pub struct Plot {
    pub row: usize,
    pub col: usize,
    pub ring: Vec<Pt>,
    pub low: bool,
}

/// One of the polder's channels: its role and its piece of the ring (`seg`), its course and its widths.
#[derive(Debug, Clone, PartialEq)]
pub struct Ditch {
    pub role: &'static str,
    pub seg: &'static str,
    pub pts: Vec<Pt>,
    pub w: f64,
    pub w_tail: f64,
}

/// The polder built.
#[derive(Debug, Clone, PartialEq)]
pub struct Polder {
    pub outline: Vec<Pt>,
    pub inner_env: Vec<Pt>,
    pub plots: Vec<Plot>,
    pub ditches: Vec<Ditch>,
    pub sluices: [Pt; 2],
    pub pond: (Pt, f64, f64),
    pub feeder: Vec<Pt>,
    pub shape: (usize, usize),
}

/// The block's rows and columns of modules: the shape whose row count is nearest the square root of the modules times `aspect`
/// (the block's length down the fall over its breadth), and its neighbor, the one wasting fewer modules kept.
///
/// Research:
///     whole modules - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: square modules about 190 ft on a side; at or above the households' paddy of research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html, the shape a CONVENTION of the block
#[must_use]
pub fn shape(modules: u32, aspect: f64) -> (usize, usize) {
    let root = (f64::from(modules) * aspect.max(0.1)).sqrt();
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of rows"
    )]
    let r0 = (root.round() as usize).max(1);
    let fit = |r: usize| {
        let c = (modules as usize).div_ceil(r).max(1);
        (r * c - modules as usize, r, c)
    };
    let (a, b) = (fit(r0), fit(r0 + 1));
    let best = if b.0 < a.0 { b } else { a };
    (best.1, best.2)
}

/// A frame on the map: the block's head-left corner and the unit vectors down the fall and across it.
struct Frame {
    origin: Pt,
    down: Pt,
    across: Pt,
}

impl Frame {
    fn at(&self, u: f64, x: f64) -> Pt {
        (
            self.origin.0 + self.down.0 * u + self.across.0 * x,
            self.origin.1 + self.down.1 * u + self.across.1 * x,
        )
    }
}

/// The lattice's deformation at (`u`, `x`) in a block `length` by `breadth`: on the rice polder each line's bow and each
/// crossing's nudge (both zero on the block's edge), on a mosaic a smooth drift fading to the edge, on a chessboard none.
fn warp(seed: i64, form: &str, u: f64, x: f64, size: (f64, f64), module: f64) -> (f64, f64) {
    let (length, breadth) = size;
    let edge = (std::f64::consts::PI * u / length).sin().abs()
        * (std::f64::consts::PI * x / breadth).sin().abs();
    if form == "chessboard" {
        return (0.0, 0.0);
    }
    let mut rng = knob_rng(seed, "polder_warp");
    let ph: Vec<f64> = (0..4)
        .map(|_| f64::from(rng.randbelow(360)).to_radians())
        .collect();
    if form == "mosaic" {
        let a = DRIFT_SHARE * module * edge;
        return (
            a * (x / breadth * std::f64::consts::TAU + ph[0]).sin(),
            a * (u / length * std::f64::consts::TAU + ph[1]).sin(),
        );
    }
    let bow = BOW_NUDGE_FT.0 * edge;
    let nudge = BOW_NUDGE_FT.1 * edge;
    (
        bow * (x / breadth * std::f64::consts::PI * 2.0 + ph[2]).sin()
            + nudge * ((u + x) * 0.37 + ph[3]).sin(),
        bow * (u / length * std::f64::consts::PI * 2.0 + ph[3]).sin()
            + nudge * ((u - x) * 0.29 + ph[2]).sin(),
    )
}

/// The polder of `paddy` square feet: the rice polder's grid (`dikepond` false) or the dike-pond block, falling along
/// `down_deg`, its middle at `center`; `layout` the dike-pond's `pond_layout` knob (mosaic or chessboard).
///
/// Research:
///     the polder's acreage - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross a household, in whole modules of research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html at or above it
///     never uniform rectangles - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: our maps never draw the parcels as a grid of uniform rectangles
///     every pond four-sided - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic bends the lattice but keeps every pond four-sided
#[must_use]
pub fn polder(
    paddy: f64,
    dikepond: bool,
    layout: &str,
    down_deg: f64,
    center: Pt,
    aspect: f64,
    seed: i64,
) -> Polder {
    let module = if dikepond { MODULE_FT.1 } else { MODULE_FT.0 };
    let (col_gap, row_gap) = if dikepond {
        (POND_GAP_FT, POND_GAP_FT)
    } else {
        POLDER_GAP_FT
    };
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a small positive count of modules"
    )]
    let modules = ((paddy / (module * module)).ceil() as u32).max(2);
    let (rows, cols) = shape(modules, aspect);
    #[expect(clippy::cast_precision_loss, reason = "a small count")]
    let size = (
        rows as f64 * (module + row_gap) - row_gap,
        cols as f64 * (module + col_gap) - col_gap,
    );
    let (dx, dy) = heading(down_deg);
    let across = (-dy, dx);
    let origin = (
        center.0 - dx * size.0 / 2.0 - across.0 * size.1 / 2.0,
        center.1 - dy * size.0 / 2.0 - across.1 * size.1 / 2.0,
    );
    let frame = Frame {
        origin,
        down: (dx, dy),
        across,
    };
    // the dike-pond's mosaic drifts; its grid (the chessboard) stands straight; the rice polder bows and nudges
    let form = if !dikepond {
        "polder"
    } else if layout == "mosaic" {
        "mosaic"
    } else {
        "chessboard"
    };
    let put = |u: f64, x: f64| {
        let (du, dxx) = warp(seed, form, u, x, size, module);
        frame.at(u + du, x + dxx)
    };
    let plots = plots(
        &put,
        (rows, cols),
        (module, row_gap, col_gap),
        dikepond,
        seed,
    );
    let ring = |o: f64| {
        vec![
            frame.at(-o, -o),
            frame.at(-o, size.1 + o),
            frame.at(size.0 + o, size.1 + o),
            frame.at(size.0 + o, -o),
        ]
    };
    let (canal, env) = (ring(RING_FT.0), ring(RING_FT.1));
    let inlet = frame.at(-RING_FT.1, size.1 + RING_FT.1);
    let outfall = frame.at(size.0 + RING_FT.1, size.1 / 2.0);
    let pond_at = frame.at(-RING_FT.1 - POND_FT.2, size.1 + RING_FT.1);
    let feeder = vec![
        pond_at,
        frame.at(-RING_FT.1 - POND_FT.1, size.1 + RING_FT.1),
        inlet,
    ];
    let ditches = ditches(&frame, &canal, size, (cols, module, col_gap));
    Polder {
        outline: ring(0.0),
        inner_env: env,
        plots,
        ditches,
        sluices: [inlet, outfall],
        pond: (pond_at, POND_FT.0, POND_FT.1),
        feeder,
        shape: (rows, cols),
    }
}

/// The block's plots: on the rice polder each module split into 2 or 3 strips across its breadth by walking bunds, one in
/// `MERGE_IN.0` merged with the module below; on the dike-pond the modules paired down the fall into ponds' parcels, one in
/// `MERGE_IN.1` left alone. Every plot four-sided, its corners the warped lattice's.
fn plots(
    put: &dyn Fn(f64, f64) -> Pt,
    grid: (usize, usize),
    sizes: (f64, f64, f64),
    dikepond: bool,
    seed: i64,
) -> Vec<Plot> {
    let ((rows, cols), (module, row_gap, col_gap)) = (grid, sizes);
    let mut out = Vec::new();
    for c in 0..cols {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let x0 = c as f64 * (module + col_gap);
        let mut r = 0;
        while r < rows {
            let mut rng = knob_rng(seed, &format!("polder_plot:{r}:{c}"));
            let pair = if dikepond {
                rng.randbelow(MERGE_IN.1) != 0
            } else {
                rng.randbelow(MERGE_IN.0) == 0
            };
            let span = if pair && r + 1 < rows { 2 } else { 1 };
            #[expect(clippy::cast_precision_loss, reason = "a small count")]
            let (u0, u1) = (
                r as f64 * (module + row_gap),
                (r + span) as f64 * (module + row_gap) - row_gap,
            );
            let strips = if dikepond { 1 } else { 2 + rng.randbelow(2) };
            let w = (module - f64::from(strips - 1) * row_gap) / f64::from(strips);
            for k in 0..strips {
                let a = x0 + f64::from(k) * (w + row_gap);
                out.push(Plot {
                    row: r,
                    col: c,
                    ring: vec![put(u0, a), put(u0, a + w), put(u1, a + w), put(u1, a)],
                    low: r + span == rows,
                });
            }
            r += span;
        }
    }
    out
}

/// The polder's channels: the ring canal in its four trunks (the feeder across the head from the inlet, the two flanks, the
/// drain across the tail to the outfall) and a field ditch down each column corridor from the head's trunk to the tail's.
///
/// Research:
///     the ring canal - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a ring canal round the inside foot of the dike, on the field side
///     the field ditches - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: between one column of modules and the next, a ditch corridor of about 8 ft
///     the widths - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: supply 4.5 to 1.5, delivery 2.5 to 1.2, drain 1.2 to 5.5 ft
fn ditches(frame: &Frame, canal: &[Pt], size: (f64, f64), cols: (usize, f64, f64)) -> Vec<Ditch> {
    let (n, module, gap) = cols;
    let mut out = vec![
        Ditch {
            role: "main",
            seg: "feeder",
            pts: vec![canal[1], canal[0]],
            w: 4.5,
            w_tail: 1.5,
        },
        Ditch {
            role: "lateral",
            seg: "w_toe",
            pts: vec![canal[0], canal[3]],
            w: 1.5,
            w_tail: 1.5,
        },
        Ditch {
            role: "lateral",
            seg: "e_toe",
            pts: vec![canal[1], canal[2]],
            w: 1.5,
            w_tail: 1.5,
        },
        Ditch {
            role: "drain",
            seg: "drain",
            pts: vec![canal[3], canal[2]],
            w: 1.2,
            w_tail: 5.5,
        },
    ];
    for c in 1..n {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let x = c as f64 * (module + gap) - gap / 2.0;
        out.push(Ditch {
            role: "lateral",
            seg: "column",
            pts: vec![frame.at(-RING_FT.0, x), frame.at(size.0 + RING_FT.0, x)],
            w: 2.5,
            w_tail: 1.2,
        });
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{polder, shape, MODULE_FT};
    use crate::field::geom::{inside, signed_area};

    #[test]
    fn the_shape_wastes_least() {
        assert_eq!(shape(24, 1.0), (6, 4));
        let (r, c) = shape(34, 0.5);
        assert!(r * c >= 34 && r * c - 34 < c);
        assert_eq!(shape(1, 0.0), (1, 1));
    }

    #[test]
    fn a_rice_polder_and_a_dike_pond_block() {
        let paddy = 15.0 * 1.3 * 43_560.0;
        for (dikepond, layout) in [(false, "mosaic"), (true, "mosaic"), (true, "chessboard")] {
            let p = polder(paddy, dikepond, layout, 90.0, (3200.0, 3200.0), 1.0, 4);
            let area: f64 = p.plots.iter().map(|x| signed_area(&x.ring).abs()).sum();
            assert!(area >= paddy * 0.8, "{area} for {paddy}");
            assert!(p.plots.iter().all(|x| x.ring.len() == 4));
            assert!(p.plots.iter().any(|x| x.low));
            let center = |r: &[(f64, f64)]| {
                (
                    r.iter().map(|q| q.0).sum::<f64>() / 4.0,
                    r.iter().map(|q| q.1).sum::<f64>() / 4.0,
                )
            };
            assert!(p
                .plots
                .iter()
                .all(|x| inside(center(&x.ring), &p.inner_env)));
            assert!(!inside(p.pond.0, &p.inner_env));
            assert!(p.ditches.len() >= 4 && p.feeder.len() == 3);
            if dikepond {
                let paired = p
                    .plots
                    .iter()
                    .filter(|x| signed_area(&x.ring).abs() > MODULE_FT.1 * MODULE_FT.1 * 1.5)
                    .count();
                assert!(paired * 2 > p.plots.len());
            } else {
                assert!(p.plots.len() > p.shape.0 * p.shape.1);
            }
        }
        let flat = polder(paddy, true, "chessboard", 90.0, (0.0, 0.0), 1.0, 4);
        let warped = polder(paddy, true, "mosaic", 90.0, (0.0, 0.0), 1.0, 4);
        assert_ne!(flat.plots, warped.plots, "the mosaic bends the lattice");
    }
}
