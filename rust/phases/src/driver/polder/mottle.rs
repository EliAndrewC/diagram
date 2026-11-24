//! The earth mottle of a polder's dike and of a pond's bank: patches of earth of different ages, as repairs are, scattered along
//! the band from the map's seed and painted on it under everything that stands on it.
//!
//! Research:
//!     the mottle's module - NONE: the units below carry each decision's claim

use crate::field::dike::Dike;
use crate::field::fan::Pt;
use crate::field::geom::{dist, signed_area, unit};
use crate::pyrand::{knob_rng, PyRandom};

/// The dike's patch tones: packed earth darker than the band, the band's own, and dried earth lighter.
///
/// Research:
///     the patches' tones - CONVENTION: the deleted village dike's four earth inks, darker packed and lighter dried patches about the band's own - a drawing's palette and no finding
pub(super) const DIKE_TONES: [&str; 4] = ["#A8895A", "#B79B68", "#D2BC8C", "#9C8150"];
/// A pond bank's patch tones: the bank's planted ground darker and lighter, and bare earth.
///
/// Research:
///     the patches' tones - CONVENTION: the bank's own ink darkened and lightened beside two bare earths - a drawing's palette and no finding
pub(super) const BANK_TONES: [&str; 4] = ["#989D6B", "#BCC092", "#B79B68", "#A39A68"];
/// How strongly a patch is painted over its band.
///
/// Research:
///     the patches' strength - CONVENTION: 0.4, the deleted village dike's, so patches that overlap read as mottle and no patch as a shape of its own
pub(super) const MOTTLE_OPACITY: f64 = 0.4;
/// A patch's two radii (feet), east-west and north-south on the sheet, each rolled between its two.
///
/// Research:
///     a patch's size - GUESS: research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html silent on how big a patch of repaired earth is; 10 to 26 ft east-west by 8 to 18 ft north-south, the deleted village dike's, drawn along the sheet's axes whichever way the band runs and clipped to the band, whose own breadth is 14 to 40 ft
pub(super) const PATCH_FT: ((f64, f64), (f64, f64)) = ((5.0, 13.0), (4.0, 9.0));
/// How far apart along a band its patches fall (feet).
///
/// Research:
///     the patches' spacing - GUESS: research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html silent on how much of a dike is patched; one patch to every 16 ft of its length, so the patches overlap along the band and no stretch of it reads as one flat fill
pub(super) const PATCH_STEP_FT: f64 = 16.0;

/// One patch of earth: its middle, its east-west and north-south radii, and its tone.
///
/// Research:
///     a patch - NONE: the record's type, holding what `along` decides
pub(super) type Patch = (Pt, f64, f64, &'static str);

/// The patches along a closed band, added to `patches`: `line` one face's ring walked every `PATCH_STEP_FT`, each patch set off
/// that face by a rolled share of `across(i, t)` - the way across the band at the ring's side `i`, `t` of the way along it - its
/// size and its tone rolled from `rolls`.
///
/// Research:
///     patches of different ages - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the band mottled with patches of earth of different ages, as repairs are - scattered, each patch's place across the band, its size and its tone rolled, where the dike's planting runs in rows
fn along(
    line: &[Pt],
    across: impl Fn(usize, f64) -> Pt,
    tones: &[&'static str; 4],
    rolls: &mut PyRandom,
    patches: &mut Vec<Patch>,
) {
    let mut span = |lo: f64, hi: f64| lo + (hi - lo) * rolls.random();
    let (mut walked, mut next) = (0.0, PATCH_STEP_FT / 2.0);
    for i in 0..line.len() {
        let (a, b) = (line[i], line[(i + 1) % line.len()]);
        let len = dist(a, b);
        while next <= walked + len {
            let t = (next - walked) / len.max(1e-9);
            let (w, share) = (across(i, t), span(0.0, 1.0));
            let at = (
                a.0 + (b.0 - a.0) * t + w.0 * share,
                a.1 + (b.1 - a.1) * t + w.1 * share,
            );
            let (rx, ry) = (
                span(PATCH_FT.0 .0, PATCH_FT.0 .1),
                span(PATCH_FT.1 .0, PATCH_FT.1 .1),
            );
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "one of four tones"
            )]
            let tone = tones[(span(0.0, 4.0) as usize).min(3)];
            patches.push((at, rx, ry, tone));
            next += PATCH_STEP_FT;
        }
        walked += len;
    }
}

/// The dike's patches: along its inner face's stations, each anywhere across the band at its breadth there.
///
/// Research:
///     the dike mottled - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the band changes in width and is mottled, never a ruled line - mottled with patches of earth of different ages, as repairs are; before 449 T422 the band was one flat fill
///     its own stream - NONE: the patches rolled from a stream of their own (`dike_mottle`), so no other roll of the map moves with them
pub(super) fn dike(d: &Dike, seed: i64) -> Vec<Patch> {
    // the stations pair the crest and the outer face; the inner face's station is the crest's mirror of the outer's
    let n = d.crest.len().min(d.outer.len());
    let breadth = |i: usize| {
        let (c, o) = (d.crest[i % n], d.outer[i % n]);
        (2.0 * (o.0 - c.0), 2.0 * (o.1 - c.1))
    };
    let face: Vec<Pt> = (0..n)
        .map(|i| {
            let w = breadth(i);
            (d.outer[i].0 - w.0, d.outer[i].1 - w.1)
        })
        .collect();
    let mut patches = Vec::new();
    along(
        &face,
        |i, t| {
            let (a, b) = (breadth(i), breadth(i + 1));
            (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        },
        &DIKE_TONES,
        &mut knob_rng(seed, "dike_mottle"),
        &mut patches,
    );
    patches
}

/// The banks' patches: along each bank's outer edge, each up to the ponds' `inset` in from it, the bank's breadth.
///
/// Research:
///     the bank mottled - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: the bank is drawn as planted ground, mottled earth under rows of mulberry bushes, like the polder's own dike; before 449 T422 each bank was one flat fill under its bushes
///     its own stream - NONE: the patches rolled from a stream of their own (`bank_mottle`), one for all the banks in their order
pub(super) fn banks(rings: &[&[Pt]], inset: f64, seed: i64) -> Vec<Patch> {
    let mut rolls = knob_rng(seed, "bank_mottle");
    let mut patches = Vec::new();
    for ring in rings {
        // inward of a side: the right of travel on a ring turning clockwise on the map's axes (a positive signed area)
        let turn = signed_area(ring).signum();
        along(
            ring,
            |i, _| {
                let u = unit(ring[i], ring[(i + 1) % ring.len()]);
                (-u.1 * turn * inset, u.0 * turn * inset)
            },
            &BANK_TONES,
            &mut rolls,
            &mut patches,
        );
    }
    patches
}
