//! The polder's dike (feature 444 T16, the polder's seam): a band of heaped earth round the block, 14 to 40 ft across and changing
//! in width along its length, its outer face curved with the water's edge, its inner face along the fields; its crest; its gaps
//! where the sluices cut it; its willow row three quarters of the way out and its mulberry row a quarter of the way, both cut
//! along the channels that cross it there. Written from the record; the old placement unread.
//!
//! Research:
//!     the dike's band - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the band is drawn 14 to 40 ft across, between the breadths read, changing in width along its length
//!     its two faces - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the maps curve the dike's outer face with the water's edge and run its inner face along the fields inside
//!     its trees - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: willow on the water side about 8.5 ft apart, mulberry on the field side about 4.4 ft apart

use super::fan::Pt;
use super::geom::{dist, seg_dist, unit};
use crate::pyrand::knob_rng;

/// The band's breadth, least and most (feet).
///
/// Research:
///     the band - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the band is drawn 14 to 40 ft across
pub const BAND_FT: (f64, f64) = (14.0, 40.0);
/// A station along the inner face, every this many feet: the band's mean breadth, so its width changes once a breadth.
///
/// Research:
///     the station - CONVENTION: the band's mean breadth, 27 ft (the polder's derivation)
pub const STATION_FT: f64 = 27.0;
/// The two waves the band's breadth changes by along the face, in stations a wave (a GUESS: the record says it changes, not how
/// often).
///
/// Research:
///     the breadth's waves - GUESS: the record silent on how often the breadth changes; waves of 9 and 23 stations
pub const WIDTH_WAVES: (f64, f64) = (9.0, 23.0);
/// Half the opening a crossing channel cuts in the dike's tree rows (feet): no tree stands within this of the channel's middle line.
///
/// Research:
///     the gap - GUESS research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html#rows-gap-at-channel: the rows stop about 15 ft to each side of the channel's middle line, a bare stretch left as room for the sluice and its banks, no page read giving how far the trees stood back from a sluice - 15 ft, the deleted engine's opening (`DIKE_GAP_HW`), a tree's middle no nearer a crossing channel's middle line than this, so the broadest crown, a willow of radius 5.5 ft, keeps off the widest crossing channel's water but not always off the sluice's frame, whose posts stand out past the crown's reach - so a tree whose crown would reach the frame is left out besides (`FRAME_REACH_FT`, 449 T427); the band itself and the waterside reeds stop at the channel's bank, not at this gap (449 T236, T419)
pub const GAP_HALF_FT: f64 = 15.0;
/// How far a sluice's frame reaches from its point (feet): no crown comes within this of a sluice.
///
/// Research:
///     the frame kept clear - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: a field channel's sluice drawn 20 ft post to post, its posts 2 by 4 ft drawn larger than life (`driver::polder::SLUICE_SPAN_FT`, `SLUICE_TIMBER_FT`) - a post's outer corner 10.2 ft from the sluice's point, so a tree whose crown would reach within that is left out; `GAP_HALF_FT` alone let the broadest willow reach 9.5 ft from the channel's middle line, over the post's outer face 10 ft out (a crown 0.17 ft over a post on seed 66 of the dike-pond form, one touching on seed 37 of the rice polder, over 160 rolled polders, measured 2026-11-24, feature 449 T427)
pub const FRAME_REACH_FT: f64 = 10.2;
/// Each row's place across the band from the field side, and its trees' spacing along it (feet), willow then mulberry.
///
/// Research:
///     the rows - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the willow row about three quarters of the way out, the mulberry row about a quarter; willows about 8.5 ft apart, mulberry about 4.4 ft
pub const ROWS: [(&str, f64, f64); 2] = [("willow", 0.75, 8.5), ("mulberry", 0.25, 4.4)];
/// Each row's crown radius, least and most (feet).
///
/// Research:
///     the crowns - GUESS research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html#willow-crown-size: each willow's crown drawn 7 to 11 ft across, the mulberry's recorded at research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#bush-few-feet-across (a GUESS too, 4.4 to 7 ft across) - a willow's radius 3.5 to 5.5 ft - a mulberry's radius 2.2 to 3.6 ft, its broadest a tenth of a foot a side over the page's 7 ft across, which no reader of the map can see, left as it stands (the dike-pond bank's own bushes, `landuse::MULBERRY_FT`, keep 2.2 to 3.5)
pub const CROWN_FT: [(f64, f64); 2] = [(3.5, 5.5), (2.2, 3.6)];

/// A tree's crown: its middle and its radius (feet).
///
/// Research:
///     a crown - NONE: the record's type, holding what `dike` decides
pub type Crown = (f64, f64, f64);

/// The dike built: its inner and outer faces, its crest, the gaps' middles, its trees by row (x, y, radius) and its breadths.
///
/// Research:
///     the dike's record - NONE: the record's type, holding what `dike` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Dike {
    pub inner: Vec<Pt>,
    pub outer: Vec<Pt>,
    pub crest: Vec<Pt>,
    pub gaps: Vec<Pt>,
    pub trees: Vec<(&'static str, Vec<Crown>)>,
    pub widths: (f64, f64),
}

/// The closed ring `ring` walked every `STATION_FT`: each station's point, its outward normal (the ring turning clockwise on the
/// map's axes, outward is the left of travel) and its distance along.
///
/// Research:
///     the stations - NONE: sampling, each corner's normal the mean of its sides' so the outer face turns it rounded; the breadth and the faces are `dike`'s
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn stations(ring: &[Pt]) -> Vec<(Pt, Pt, f64)> {
    let n = ring.len();
    let mut out = Vec::new();
    let mut along = 0.0;
    for i in 0..n {
        let (a, b) = (ring[i], ring[(i + 1) % n]);
        let len = dist(a, b);
        let u = unit(a, b);
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a small positive count of stations"
        )]
        let steps = ((len / STATION_FT).ceil() as usize).max(1);
        for k in 0..steps {
            #[expect(clippy::cast_precision_loss, reason = "a small step count")]
            let t = len * k as f64 / steps as f64;
            out.push(((a.0 + u.0 * t, a.1 + u.1 * t), (u.1, -u.0), along + t));
        }
        along += len;
    }
    // each corner's normal the mean of the two sides', so the outer face turns the corner rounded rather than mitred
    let m = out.len();
    let normals: Vec<Pt> = (0..m)
        .map(|i| {
            let (p, q) = (out[(i + m - 1) % m].1, out[(i + 1) % m].1);
            let s = (p.0 + q.0 + out[i].1 .0, p.1 + q.1 + out[i].1 .1);
            let l = s.0.hypot(s.1).max(1e-12);
            (s.0 / l, s.1 / l)
        })
        .collect();
    out.iter()
        .zip(normals)
        .map(|(s, nrm)| (s.0, nrm, s.2))
        .collect()
}

/// The dike round `inner` (the block's inner envelope, its corners in turn clockwise on the map), its rows cut along each of
/// `courses` (the channels that cross it at `sluices`, the feeder and the outfall), its breadth's waves and its trees' crowns
/// rolled from the seed's `dike` stream.
///
/// Research:
///     a dike round the polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: water crosses the dike only at gated sluices
///     the rows cut at the gaps - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: where a channel crosses the dike, the band is cut, and the rows stop with it - no tree within `GAP_HALF_FT` of a crossing channel's middle line, all the way through the band (before 449 T419 only round the sluice's point at the inner face, so a crown stood on the feeder's water farther out); the band's own cut is the drawing's (`driver::polder::draw_polder` paints the band under the channels' water), the faces recorded whole for the reeds and the seat that read them
///     the band's breadth - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: 14 to 40 ft across, changing along the length on two seeded waves
///     the breadth's waves - GUESS: research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html silent on how long a thick or pinched stretch runs; waves of `WIDTH_WAVES` stations weighted three to two
///     its two faces - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the inner face on the fields' envelope; the outer face that face pushed out by the rolled breadth, the waterward strip of reeds and wet ground laid against it later (`hamletgen/water/waterward.py`'s `dike_face`, which reads the outline this records), so the water's edge runs along the outer face
///     its trees - research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the willow row three quarters of the way out toward the water, 8.5 ft apart; the mulberry a quarter of the way, on the field side, 4.4 ft apart
///     the crowns rolled - GUESS: each tree's crown within its row's `CROWN_FT`, in tenths of a foot
///     the sluice's frame kept clear - GUESS research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html#rows-gap-at-channel: the bare stretch at a crossing is room for the sluice and its banks - a tree whose crown would come within `FRAME_REACH_FT` of a sluice's point is left out, its radius rolled first so no other tree's roll moves (449 T427 - with the gap alone a willow overlapped a post on one of 160 rolled polders and touched one on another, after it none, measured 2026-11-24; Kuwabata loses no tree)
///     the crest - NONE: the band's midline, where its walked top runs
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn dike(inner: &[Pt], sluices: &[Pt], courses: &[&[Pt]], seed: i64) -> Dike {
    // the stations' outward normal reads a clockwise ring (a positive signed area on the map's y-down axes): turn it if not
    let mut face = inner.to_vec();
    if super::geom::signed_area(&face) < 0.0 {
        face.reverse();
    }
    let st = stations(&face);
    let mut rolls = knob_rng(seed, "dike");
    let ph = (
        f64::from(rolls.randbelow(360)).to_radians(),
        f64::from(rolls.randbelow(360)).to_radians(),
    );
    let width = |along: f64| {
        let t = along / STATION_FT * std::f64::consts::TAU;
        let mix =
            0.5 + 0.3 * (t / WIDTH_WAVES.0 + ph.0).sin() + 0.2 * (t / WIDTH_WAVES.1 + ph.1).sin();
        BAND_FT.0 + (BAND_FT.1 - BAND_FT.0) * mix.clamp(0.0, 1.0)
    };
    let gap = |p: Pt| {
        courses
            .iter()
            .flat_map(|c| c.windows(2))
            .any(|g| seg_dist(p, g[0], g[1]) < GAP_HALF_FT)
    };
    let at = |s: &(Pt, Pt, f64), share: f64| {
        let w = width(s.2);
        (s.0 .0 + s.1 .0 * w * share, s.0 .1 + s.1 .1 * w * share)
    };
    let outer: Vec<Pt> = st.iter().map(|s| at(s, 1.0)).collect();
    let crest: Vec<Pt> = st.iter().map(|s| at(s, 0.5)).collect();
    let widths = st
        .iter()
        .map(|s| width(s.2))
        .fold((f64::INFINITY, 0.0_f64), |(lo, hi), w| {
            (lo.min(w), hi.max(w))
        });
    let mut trees = Vec::new();
    for (k, (kind, share, step)) in ROWS.iter().enumerate() {
        let line: Vec<Pt> = st.iter().map(|s| at(s, *share)).collect();
        // the row's own line, all the way round: pushed out from the inner face it is longer than it
        let around: f64 = (0..line.len())
            .map(|i| dist(line[i], line[(i + 1) % line.len()]))
            .sum();
        let mut row = Vec::new();
        let mut walked = 0.0;
        let mut next = 0.0;
        for i in 0..line.len() {
            let (a, b) = (line[i], line[(i + 1) % line.len()]);
            let len = dist(a, b);
            let u = unit(a, b);
            while next <= walked + len && next < around {
                let t = next - walked;
                let p = (a.0 + u.0 * t, a.1 + u.1 * t);
                if !gap(p) {
                    let (lo, hi) = CROWN_FT[k];
                    #[expect(
                        clippy::cast_possible_truncation,
                        clippy::cast_sign_loss,
                        reason = "a crown's size in tenths of a foot"
                    )]
                    let span = ((hi - lo) * 10.0) as u32 + 1;
                    let r = lo + f64::from(rolls.randbelow(span)) / 10.0;
                    // rolled, then left out where its crown would reach a sluice's frame (449 T427): the roll's stream unmoved
                    if sluices.iter().all(|&g| dist(p, g) >= FRAME_REACH_FT + r) {
                        row.push((p.0, p.1, r));
                    }
                }
                next += step;
            }
            walked += len;
        }
        trees.push((*kind, row));
    }
    Dike {
        inner: inner.to_vec(),
        outer,
        crest,
        gaps: sluices.to_vec(),
        trees,
        widths,
    }
}

#[cfg(test)]
mod tests {
    use super::{dike, BAND_FT, GAP_HALF_FT};
    use crate::field::geom::{inside, seg_dist, signed_area};

    #[test]
    fn a_band_round_the_block_its_rows_cut_at_the_gaps() {
        let inner = [(0.0, 0.0), (600.0, 0.0), (600.0, 400.0), (0.0, 400.0)];
        let sluices = [(600.0, 200.0)];
        // the channel through the sluice, out across the band's broadest and on
        let course = [(600.0, 200.0), (700.0, 200.0)];
        let courses = [course.as_slice()];
        let d = dike(&inner, &sluices, &courses, 4);
        assert!(
            d.widths.0 >= BAND_FT.0 - 1e-9
                && d.widths.1 <= BAND_FT.1 + 1e-9
                && d.widths.1 - d.widths.0 > 8.0
        );
        assert!(signed_area(&d.outer).abs() > signed_area(&inner).abs());
        assert!(d.outer.iter().all(|p| !inside(*p, &inner)));
        let (willow, mulberry) = (&d.trees[0].1, &d.trees[1].1);
        assert!(mulberry.len() > willow.len(), "the mulberry closer set");
        assert!(willow
            .iter()
            .chain(mulberry)
            .all(|t| seg_dist((t.0, t.1), course[0], course[1]) >= GAP_HALF_FT - 1e-9));
        // the rows stand on both sides of the cut, and each is cut: fewer trees than the row uncut
        let whole = dike(&inner, &sluices, &[], 4);
        assert!(willow.len() < whole.trees[0].1.len() && mulberry.len() < whole.trees[1].1.len());
        assert_eq!(d.crest.len(), d.outer.len());
        assert_eq!(d, dike(&inner, &sluices, &courses, 4));
        assert_ne!(d.outer, dike(&inner, &sluices, &courses, 5).outer);
        // a ring the other way round is turned: the band still outside it
        let back: Vec<_> = inner.iter().rev().copied().collect();
        assert!(dike(&back, &sluices, &courses, 4)
            .outer
            .iter()
            .all(|p| !inside(*p, &inner)));
    }
}
