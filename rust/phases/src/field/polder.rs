//! The polder (feature 444 T16 D8): the block of modules the households' paddy fills, its lattice bowed and nudged (the rice
//! polder) or drifted (the dike-pond mosaic), its plots - strips on the rice polder, ponds' parcels on the dike-pond - the ring
//! canal at the dike's inside foot, a field ditch in each column corridor, the two sluices and the wild pond that feeds it.
//! Written from `phases/polder_greenfield.derivation.md` and `phases/field.md`'s "The polder's design, next"; the old code unread.
//! The dike and its trees are `dike.rs`'s, the dike-pond's ponds `landuse.rs`'s; the thin Python draws them and fills the reed
//! fringe (`marsh`).
//!
//! Research:
//!     the rice polder's grid - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a rice polder is drawn on a surveyed grid
//!     the modules - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: square modules about 190 ft on a side; a dike-pond block a smaller module, about 160 ft, most merged in pairs

use super::fan::{heading, Pt};
use crate::pyrand::knob_rng;

/// The least paddy an enclosed field is drawn with (acres).
///
/// Research:
///     the enclosed floor - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: a field enclosed on the map is at least 8 acres
pub const ENCLOSED_FLOOR_ACRES: f64 = 8.0;
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
/// The dike-pond mosaic's drift, as a share of a module: each axis's displacement is this times the sum of its two harmonics
/// (`MOSAIC_WAVES`), fading to nothing at the block's edge.
///
/// Research:
///     the mosaic's drift - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a smooth drift that fades to nothing at the fixed outer edge; how strongly is a calibrated liberty, set on the Kuwabata map - 0.48 of a module, the strength at which Kuwabata's parcels skew as main drew them (measured 2026-11-02 on the four extreme corners of each parcel: median corner deviation 14.5 deg against main's 13.9, p90 20.1 against 23.8); the port's single weak wave at 0.15 drew 4.6 deg, a chessboard (the glyph check, feature 444 T16)
pub const DRIFT_SHARE: f64 = 0.48;
/// The mosaic's two waves on each axis, as (weight, cycles across the block) pairs: down the fall from the fall and from across, and
/// across from across and from the fall.
///
/// Research:
///     the mosaic's waves - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent on the drift's shape, saying only that it is smooth and that neighboring crossings move together; the waves Kuwabata's mosaic was drawn with, 1.3 and 2.1 cycles down the fall, 1.1 and 1.9 across, the second at 0.6
pub const MOSAIC_WAVES: [(f64, f64); 4] = [(1.0, 1.3), (0.6, 2.1), (1.0, 1.1), (0.6, 1.9)];
/// Of this many rice polder modules, one is left whole rather than split into strips.
///
/// Research:
///     whole modules among the strips - GUESS: research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html silent on how many, saying only that most split into two or three oblong strips; one in five left whole
pub const WHOLE_IN: u32 = 5;
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
/// How far the wild pond's reed fringe stands out past its water (feet), and the points its ring is drawn with.
///
/// Research:
///     the reed fringe - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent on reeds at the wild pond that feeds the polder, setting reed marsh along the block's low side; a fringe of reeds at its shore, as every reservoir pond has (research/questions/0061-reservoir-ponds-tameike.drawing.html), 40 ft wide, the comb's old source pond's, on a ring of 16 points
pub const FRINGE_FT: (f64, usize) = (40.0, 16);

/// One polder plot: its first row and column of modules, the rows it spans, its ring, and whether it lies on the block's low row.
///
/// Research:
///     a plot's record - NONE: the record's type, holding what `plots` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Plot {
    pub row: usize,
    pub span: usize,
    pub col: usize,
    pub ring: Vec<Pt>,
    pub low: bool,
}

/// One of the polder's channels: its role and its piece of the ring (`seg`), its course and its widths.
///
/// Research:
///     a channel's record - NONE: the record's type, holding what `ditches` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Ditch {
    pub role: &'static str,
    pub seg: &'static str,
    pub pts: Vec<Pt>,
    pub w: f64,
    pub w_tail: f64,
}

/// The polder built.
///
/// Research:
///     the polder's record - NONE: the record's type, holding what `polder` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Polder {
    pub outline: Vec<Pt>,
    pub inner_env: Vec<Pt>,
    pub plots: Vec<Plot>,
    pub ditches: Vec<Ditch>,
    pub sluices: [Pt; 2],
    pub pond: (Pt, f64, f64),
    pub fringe: Vec<Pt>,
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
///
/// Research:
///     the frame - NONE: a coordinate transform, down the fall and across it
struct Frame {
    origin: Pt,
    down: Pt,
    across: Pt,
}

impl Frame {
    /// The map point `u` down the fall and `x` across from the frame's origin.
    ///
    /// Research:
    ///     the frame - NONE: a coordinate transform
    fn at(&self, u: f64, x: f64) -> Pt {
        (
            self.origin.0 + self.down.0 * u + self.across.0 * x,
            self.origin.1 + self.down.1 * u + self.across.1 * x,
        )
    }
}

/// The lattice's deformation: on the rice polder each row and column line's own bow and each crossing's own nudge, both nothing
/// on the block's edge lines; on a mosaic a smooth drift fading to the edge; on a chessboard none.
///
/// Research:
///     the warp's state - NONE: the rolled bows, nudges and phases `Warp::at` applies, claimed there
struct Warp {
    form: &'static str,
    size: Pt,
    pitch: Pt,
    module: f64,
    rows: Vec<f64>,
    cols: Vec<f64>,
    nodes: Vec<Vec<Pt>>,
    ph: [f64; 4],
}

impl Warp {
    /// The warp of a block `size` (down the fall, across) of modules `lattice.0` on a side whose lines stand `lattice.1` apart, `grid` modules each way, rolled
    /// from the seed's `polder_warp` stream: a bow for each interior line and a nudge for each interior crossing.
    ///
    /// Research:
    ///     the rolls - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: each row and column line takes its own gentle bow and each crossing is nudged a few feet, while the dike and the ring canal at the block's edge stay put - a bow for each interior line and a nudge for each interior crossing within `BOW_NUDGE_FT`, either way, the edge lines and crossings held at nothing
    fn new(
        seed: i64,
        form: &'static str,
        size: Pt,
        lattice: (f64, Pt),
        grid: (usize, usize),
    ) -> Self {
        let (module, pitch) = lattice;
        let mut rng = knob_rng(seed, "polder_warp");
        let ph = [0; 4].map(|_| f64::from(rng.randbelow(360)).to_radians());
        let mut either = |most: f64| most * (2.0 * f64::from(rng.randbelow(1001)) / 1000.0 - 1.0);
        let mut line = |n: usize, most: f64| -> Vec<f64> {
            (0..=n)
                .map(|k| if k == 0 || k == n { 0.0 } else { either(most) })
                .collect()
        };
        let rows = line(grid.0, BOW_NUDGE_FT.0);
        let cols = line(grid.1, BOW_NUDGE_FT.0);
        let nodes = (0..=grid.0)
            .map(|k| {
                (0..=grid.1)
                    .map(|j| {
                        if k == 0 || k == grid.0 || j == 0 || j == grid.1 {
                            (0.0, 0.0)
                        } else {
                            (either(BOW_NUDGE_FT.1), either(BOW_NUDGE_FT.1))
                        }
                    })
                    .collect()
            })
            .collect();
        Self {
            form,
            size,
            pitch,
            module,
            rows,
            cols,
            nodes,
            ph,
        }
    }

    /// The deformation at (`u`, `x`).
    ///
    /// Research:
    ///     the rice polder's deformation - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: each row and column line takes its own gentle bow and each crossing is nudged a few feet, while the block's edge stays put - each line's bow a single arch along it, nothing at its ends, interpolated between lines; the crossings' nudges interpolated between crossings, so both sides of one bund move together
    ///     the mosaic's drift - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic bends the lattice out of line, fading to nothing at the fixed outer edge (`DRIFT_SHARE` of a module on `MOSAIC_WAVES`); the chessboard held straight
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names"
    )]
    fn at(&self, u: f64, x: f64) -> Pt {
        let (length, breadth) = self.size;
        let pi = std::f64::consts::PI;
        if self.form == "chessboard" {
            return (0.0, 0.0);
        }
        if self.form == "mosaic" {
            let edge = (pi * u / length).sin().abs() * (pi * x / breadth).sin().abs();
            let a = DRIFT_SHARE * self.module * edge;
            let (zu, zx) = (u / length, x / breadth);
            let wave = |k: usize, z: f64| {
                let (w, f) = MOSAIC_WAVES[k];
                w * (std::f64::consts::TAU * f * z + self.ph[k]).sin()
            };
            return (
                a * (wave(0, zu) + wave(1, zx)),
                a * (wave(2, zx) + wave(3, zu)),
            );
        }
        let arch = |v: f64, whole: f64| (pi * (v / whole).clamp(0.0, 1.0)).sin();
        #[expect(clippy::cast_precision_loss, reason = "a small count of lines")]
        let lerp = |vals: &[f64], at: f64| {
            let t = at.clamp(0.0, (vals.len() - 1) as f64);
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a small positive line index"
            )]
            let k = (t.floor() as usize).min(vals.len() - 2);
            let f = t - k as f64;
            (vals[k] * (1.0 - f) + vals[k + 1] * f, k, f)
        };
        let (tu, tx) = (u / self.pitch.0, x / self.pitch.1);
        let (bow_u, ku, fu) = lerp(&self.rows, tu);
        let (bow_x, kx, fx) = lerp(&self.cols, tx);
        let node = |k: usize, j: usize| self.nodes[k][j];
        let (a, b, c, d) = (
            node(ku, kx),
            node(ku, kx + 1),
            node(ku + 1, kx),
            node(ku + 1, kx + 1),
        );
        let mix = |p: f64, q: f64, r: f64, s: f64| {
            (p * (1.0 - fx) + q * fx) * (1.0 - fu) + (r * (1.0 - fx) + s * fx) * fu
        };
        (
            bow_u * arch(x, breadth) + mix(a.0, b.0, c.0, d.0),
            bow_x * arch(u, length) + mix(a.1, b.1, c.1, d.1),
        )
    }
}

/// The polder of `paddy` square feet: the rice polder's grid (`dikepond` false) or the dike-pond block, falling along
/// `down_deg`, its middle at `center`; `layout` the dike-pond's `pond_layout` knob (mosaic or chessboard).
///
/// Research:
///     the polder's acreage - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross a household, in whole modules of research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html at or above it
///     never uniform rectangles - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: our maps never draw the parcels as a grid of uniform rectangles - the rice polder bowed and nudged, the dike-pond mosaic drifted; the dike-pond's chessboard the one exception, attested on its own (the next claim)
///     the chessboard - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a dike-pond's grid of ponds, the chessboard, attested beside the mosaic - drawn straight, the `pond_layout` knob's other form
///     the least polder - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: a field enclosed on the map is never drawn under about 8 acres - the block's modules hold at least that
///     every pond four-sided - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic bends the lattice but keeps every pond four-sided
///     two sluices - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: water crosses the dike only at gated sluices, an inlet at the head and an outfall at the tail - the inlet at the head corner beside the wild pond, the outfall at the tail corner the drain widens to (research/questions/0060-field-drains-akusuiro.drawing.html: a drain reaches its full width at the outfall)
///     the feeder - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent on the feeder's course; straight from the wild pond to the inlet
///     the wild pond's place - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the wild pond that feeds the polder stands at its head - up the fall from the inlet's corner, `POND_FT.2` out, in line with the inlet's flank
///     the pond's reeds - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent on reeds at the wild pond; a fringe round it (`FRINGE_FT`)
///     the module by form - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: a rice polder's module about 190 ft with its 8 ft ditch corridors and 3 ft bunds, a dike-pond block's about 160 ft with gaps of about 22 ft both ways
///     the ring canal's place - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a ring canal round the inside foot of the dike, on the field side - `RING_FT` out from the plots, inside the dike's inner face
///     the wild pond's size - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent on its size and distance (`POND_FT`)
///     the inlet's side - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html silent beyond its pool's one polder (the wild pond to its northwest); the inlet, the pond and the outfall on one side of the fall
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
    let modules =
        ((paddy.max(ENCLOSED_FLOOR_ACRES * 43_560.0) / (module * module)).ceil() as u32).max(2);
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
    let warp = Warp::new(
        seed,
        form,
        size,
        (module, (module + row_gap, module + col_gap)),
        (rows, cols),
    );
    let put = |u: f64, x: f64| {
        let (du, dxx) = warp.at(u, x);
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
    let outfall = frame.at(size.0 + RING_FT.1, size.1 + RING_FT.1);
    let pond_at = frame.at(-RING_FT.1 - POND_FT.2, size.1 + RING_FT.1);
    let feeder = vec![
        pond_at,
        frame.at(-RING_FT.1 - POND_FT.1, size.1 + RING_FT.1),
        inlet,
    ];
    let ditches = ditches(&put, &canal, size, (cols, module, col_gap), (rows, row_gap));
    Polder {
        outline: ring(0.0),
        inner_env: env,
        plots,
        ditches,
        sluices: [inlet, outfall],
        pond: (pond_at, POND_FT.0, POND_FT.1),
        fringe: fringe(pond_at, (POND_FT.0, POND_FT.1)),
        feeder,
        shape: (rows, cols),
    }
}

/// The reed fringe's ring round a pond at `at` of radii `r`: the ellipse `FRINGE_FT.0` past its water, at `FRINGE_FT.1` points.
///
/// Research:
///     the fringe's ring - NONE: geometry; its width is `FRINGE_FT`'s
fn fringe(at: Pt, r: (f64, f64)) -> Vec<Pt> {
    #[expect(clippy::cast_precision_loss, reason = "a ring's sixteen points")]
    let n = FRINGE_FT.1 as f64;
    (0..FRINGE_FT.1)
        .map(|k| {
            #[expect(clippy::cast_precision_loss, reason = "a ring's sixteen points")]
            let a = k as f64 / n * std::f64::consts::TAU;
            (
                at.0 + (r.0 + FRINGE_FT.0) * a.cos(),
                at.1 + (r.1 + FRINGE_FT.0) * a.sin(),
            )
        })
        .collect()
}

/// The block's plots: on the rice polder most modules split into 2 or 3 strips across their breadth by walking bunds (one in
/// `WHOLE_IN` left whole), one in `MERGE_IN.0` merged with the module below; on the dike-pond the modules paired down the fall into
/// ponds' parcels, one in `MERGE_IN.1` left alone. Every plot four-sided, its corners the warped lattice's.
///
/// Research:
///     the low plots - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a polder tints every low plot - the block's last row, at its tail, the low one
///     the strips - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: most modules split into two or three oblong strips, cut by the plain 3 ft walking bund, and a few merge along the fall
///     the dike-pond's parcels - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: a dike-pond block's modules most merged in pairs
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
            let strips = if dikepond || rng.randbelow(WHOLE_IN) == 0 {
                1
            } else {
                2 + rng.randbelow(2)
            };
            let w = (module - f64::from(strips - 1) * row_gap) / f64::from(strips);
            // a merged parcel keeps a corner on each side where its middle row line crosses, the column ditch's own station
            // (`ditches`), so the warp cannot bow the ditch across a straight parcel side (the glyph check of Kuwabata, feature 444 T16)
            #[expect(clippy::cast_precision_loss, reason = "a small count")]
            let um = (r + 1) as f64 * (module + row_gap) - row_gap / 2.0;
            for k in 0..strips {
                let a = x0 + f64::from(k) * (w + row_gap);
                let corners = if span == 2 {
                    vec![
                        put(u0, a),
                        put(u0, a + w),
                        put(um, a + w),
                        put(u1, a + w),
                        put(u1, a),
                        put(um, a),
                    ]
                } else {
                    vec![put(u0, a), put(u0, a + w), put(u1, a + w), put(u1, a)]
                };
                out.push(Plot {
                    row: r,
                    span,
                    col: c,
                    ring: corners,
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
///     the widths - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: from the inlet's corner the supply's two arms, 4.5 to 1.5 across the head and 4.0 to 1.5 down the inlet's flank, as a fan's canals A and B; a delivery 2.5 to 1.2 down each column, its head capped at 0.8 of the head canal's width where it leaves; the drain 1.2 to 5.5 ft across the tail to the outfall's corner
///     the deliveries' places - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: between one column of modules and the next, a ditch corridor - one delivery on the middle of each gap between columns, from ring to ring, `cols - 1` of them
///     the far flank - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the supply canal dwindling to a lateral - the head arm's 1.5 ft tail held down the far flank, a lateral at that width flat from the head's far corner to the tail's
///     ditches on the warped lattice - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: each column line takes its own bow, so a column's ditch runs down its corridor through the same warp as the plots beside it
///     the dike-pond's interior ditches - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic's interior ditches - a column ditch in the dike between each column of ponds, through the same warp
fn ditches(
    put: &dyn Fn(f64, f64) -> Pt,
    canal: &[Pt],
    size: (f64, f64),
    cols: (usize, f64, f64),
    rows: (usize, f64),
) -> Vec<Ditch> {
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
            role: "main",
            seg: "e_toe",
            pts: vec![canal[1], canal[2]],
            w: 4.0,
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
    // THE DITCH'S STATIONS ARE THE PARCELS' OWN (the glyph check of Kuwabata, feature 444 T16): every row's start and end and the
    // middle of every gap between rows, where the parcels beside it keep their corners (`plots`) - so between two stations the
    // ditch and the parcels' sides are straight runs of the same warp, and the ditch stays in its gap; sampled finer, the mosaic's
    // drift bowed it up to 24 ft into the banks
    let (row_n, row_gap) = rows;
    let mut stations = vec![-RING_FT.0];
    for r in 0..row_n {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let u0 = r as f64 * (module + row_gap);
        stations.extend([u0, u0 + module]);
        if r + 1 < row_n {
            stations.push(u0 + module + row_gap / 2.0);
        }
    }
    stations.push(size.0 + RING_FT.0);
    for c in 1..n {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let x = c as f64 * (module + gap) - gap / 2.0;
        let pts = stations.iter().map(|&u| put(u, x)).collect();
        // the head canal's width where the column leaves it: 4.5 ft at the inlet's corner (x = breadth), its 1.5 ft tail at the far one
        let local = 1.5 + (4.5 - 1.5) * (x / size.1).clamp(0.0, 1.0);
        let head = 2.5_f64.min(0.8 * local);
        out.push(Ditch {
            role: "lateral",
            seg: "column",
            pts,
            w: head,
            w_tail: 1.2_f64.min(head),
        });
    }
    out
}

/// How far past the canvas the outfall runs, so its end is off the map (feet).
///
/// Research:
///     the outfall off the map - research/questions/0060-field-drains-akusuiro.drawing.html: then straight down the fall off the map
pub const OUTFALL_PAST_FT: f64 = 20.0;

/// The first leg of the outfall out of the tail corner, before it turns onto the fall (feet): past the dike's broadest band.
///
/// Research:
///     the outfall's first leg - GUESS: research/questions/0060-field-drains-akusuiro.drawing.html silent on its length; 60 ft, past the 40 ft dike so the turn is on open ground
pub const OUTFALL_LEG_FT: f64 = 60.0;

/// The drain's outfall from the tail corner's sluice: the drain arrives across the fall, so its run onward bends out of that
/// exit heading half way onto the fall (45 degrees) for `OUTFALL_LEG_FT`, then the other half, straight down the fall until off
/// the `canvas` - two turns of 45 degrees.
///
/// Research:
///     the outfall's course - research/questions/0060-field-drains-akusuiro.drawing.html: the drain's own run onward bends out of the collector's exit heading, the turn held to 55 degrees or less, then straight down the fall off the map
#[must_use]
pub fn outfall(sluice: Pt, down_deg: f64, canvas: Pt) -> Vec<Pt> {
    let (dx, dy) = heading(down_deg);
    let (ax, ay) = (-dy, dx);
    let half = std::f64::consts::FRAC_1_SQRT_2;
    let bend = (
        sluice.0 + (ax + dx) * half * OUTFALL_LEG_FT,
        sluice.1 + (ay + dy) * half * OUTFALL_LEG_FT,
    );
    // the distance along the fall to leave the canvas's box, and a little more
    let to_edge = |p: f64, d: f64, hi: f64| {
        if d > 1e-9 {
            (hi - p) / d
        } else if d < -1e-9 {
            -p / d
        } else {
            f64::INFINITY
        }
    };
    let run = to_edge(bend.0, dx, canvas.0)
        .min(to_edge(bend.1, dy, canvas.1))
        .max(0.0)
        + OUTFALL_PAST_FT;
    vec![sluice, bend, (bend.0 + dx * run, bend.1 + dy * run)]
}

/// The polder's resting plots on an `unsettled` paddy: 2 to 4 rolled from the seed's `polder_rest` stream, a plot's weight its
/// row from the head (the far end of the water's run likeliest), none sharing a bund with another (the same column, their rows
/// touching or overlapping, a merged plot's span counted). Returns the plots' indices.
///
/// Research:
///     resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots (`states::REST_PLOTS`), no two sharing a bund, likelier down the slope
///     never a low plot - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a polder tints every low plot, the tint marking the ground, not the season - so a wet low plot is never drawn resting
#[must_use]
pub fn rest(plots: &[Plot], seed: i64, unsettled: bool) -> Vec<usize> {
    if !unsettled || plots.is_empty() {
        return Vec::new();
    }
    let mut rng = knob_rng(seed, "polder_rest");
    let want = super::states::REST_PLOTS.0
        + rng.randbelow(super::states::REST_PLOTS.1 - super::states::REST_PLOTS.0 + 1);
    let weight: u32 = plots
        .iter()
        .map(|p| u32::try_from(p.row + 1).unwrap_or(u32::MAX))
        .sum();
    let mut chosen: Vec<usize> = Vec::new();
    for _ in 0..want * 8 {
        if chosen.len() >= want as usize {
            break;
        }
        let mut pick = rng.randbelow(weight.max(1));
        let mut i = 0;
        while i + 1 < plots.len() && pick >= u32::try_from(plots[i].row + 1).unwrap_or(u32::MAX) {
            pick -= u32::try_from(plots[i].row + 1).unwrap_or(u32::MAX);
            i += 1;
        }
        let a = &plots[i];
        let shares = |j: usize| {
            let o = &plots[j];
            a.col == o.col && a.row <= o.row + o.span && o.row <= a.row + a.span
        };
        // ...never a low plot: its wet tint marks the ground, not the season (0007)
        if !a.low && !chosen.contains(&i) && !chosen.iter().any(|&j| shares(j)) {
            chosen.push(i);
        }
    }
    chosen
}

#[cfg(test)]
mod tests {
    use super::{outfall, polder, rest, shape, MODULE_FT};
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
            assert!(p
                .plots
                .iter()
                .all(|x| x.ring.len() == 4 || x.ring.len() == 6));
            assert!(p.plots.iter().any(|x| x.low));
            #[expect(clippy::cast_precision_loss, reason = "a parcel's few corners")]
            let center = |r: &[(f64, f64)]| {
                (
                    r.iter().map(|q| q.0).sum::<f64>() / r.len() as f64,
                    r.iter().map(|q| q.1).sum::<f64>() / r.len() as f64,
                )
            };
            assert!(p
                .plots
                .iter()
                .all(|x| inside(center(&x.ring), &p.inner_env)));
            assert!(!inside(p.pond.0, &p.inner_env));
            assert!(
                p.fringe.len() == 16
                    && p.fringe
                        .iter()
                        .all(|q| (q.0 - p.pond.0 .0).abs() <= 82.0 + 40.0 + 1e-9)
            );
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
        let p = polder(paddy, false, "mosaic", 90.0, (3200.0, 3200.0), 1.0, 4);
        assert!(rest(&p.plots, 4, false).is_empty() && rest(&[], 4, true).is_empty());
        for seed in 0..10 {
            let r = rest(&p.plots, seed, true);
            assert!((1..=4).contains(&r.len()));
            for (k, &i) in r.iter().enumerate() {
                for &j in &r[k + 1..] {
                    let (a, b) = (&p.plots[i], &p.plots[j]);
                    assert!(a.col != b.col || a.row > b.row + b.span || b.row > a.row + a.span);
                }
            }
        }
        // the outfall runs down the fall off the canvas, whichever way the fall
        for (deg, canvas) in [
            (90.0, (6400.0, 6400.0)),
            (0.0, (6400.0, 6400.0)),
            (180.0, (6400.0, 6400.0)),
            (270.0, (6400.0, 6400.0)),
            (45.0, (6400.0, 6400.0)),
        ] {
            let run = outfall((3200.0, 3300.0), deg, canvas);
            let end = run[run.len() - 1];
            assert_eq!(run.len(), 3, "two turns of 45 degrees onto the fall");
            assert!(end.0 < 0.0 || end.1 < 0.0 || end.0 > canvas.0 || end.1 > canvas.1);
        }
        let flat = polder(paddy, true, "chessboard", 90.0, (0.0, 0.0), 1.0, 4);
        let warped = polder(paddy, true, "mosaic", 90.0, (0.0, 0.0), 1.0, 4);
        assert_ne!(flat.plots, warped.plots, "the mosaic bends the lattice");
    }
}
