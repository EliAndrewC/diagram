//! The dike-pond's conversion (feature 444 T16, the polder's seam): which parcels are ponds, nursery ponds or rice; each pond's
//! bank and water rounded from its parcel at the village's split; and the crop on the banks. Written from the record; the old
//! overlay's placement unread.
//!
//! Research:
//!     ponds ringed by banks - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: ponds of uneven shape, each ringed by a bank of its own mud planted with rows of low mulberry bushes
//!     one inset a village - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one inset holds for the whole village, measured on its parcel of median area

use super::fan::Pt;
use super::geom::{dist, signed_area, unit};
use super::ponds::rounded;
use crate::pyrand::knob_rng;

/// Of this many parcels, one is left in standing rice where the `leftover` form is rice.
///
/// Research:
///     the leftover - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: every parcel a pond, or about one parcel in ten left in standing rice among the ponds
pub const RICE_IN: u32 = 10;
/// The most of a fry village's pond water its nursery ponds hold.
///
/// Research:
///     the fry ponds - research/questions/0024-fish-fry-and-nursery-ponds-yumiao.drawing.html: the smallest ponds are given to fry until they hold up to seven-tenths of its pond water
pub const FRY_SHARE: f64 = 0.7;
/// A bank's reach (the corner's rounding) and a pond's (feet); a nursery pond's water stands nearer its bank (feet).
///
/// Research:
///     the rounding - CONVENTION: a dug pond rounded at its corners, the bank's 8 ft and the water's 16 ft; a nursery pond's water 2.5 ft in at 12 ft
pub const REACH_FT: (f64, f64) = (8.0, 16.0);
pub const FRY_FT: (f64, f64) = (2.5, 12.0);
/// The mulberry on a bank: a row a this many feet of the bank's width, its bushes this far apart (feet), each crown's radius.
///
/// Research:
///     mulberry on the bank - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one row to every 5.5 ft of the bank's width, the bushes about 4.4 ft apart in the row; crowns 4.4 to 7 ft across
pub const MULBERRY_FT: (f64, f64, (f64, f64)) = (5.5, 4.4, (2.2, 3.5));
/// The fruit on a bank: one line, its trees this far apart, each crown's radius (feet).
///
/// Research:
///     fruit on the bank - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: a single line of trees about 18 ft apart, crowns 8 to 10 ft across, a GUESS
pub const FRUIT_FT: (f64, (f64, f64)) = (18.0, (4.0, 5.0));
/// The tea on a bank: two hedges, each this wide, broken every this many feet by a gap this long (feet).
///
/// Research:
///     tea on the bank - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: two clipped hedges along the bank, each about 3 ft wide and broken every 7.5 ft, a GUESS; the gap 1.5 ft a CONVENTION
pub const TEA_FT: (f64, f64, f64) = (3.0, 7.5, 1.5);

/// One converted parcel: its kind (`pond`, `fry` or `rice`), its parcel, and for a pond its bank and water (the SVG path and its
/// samples).
#[derive(Debug, Clone, PartialEq)]
pub struct Parcel {
    pub kind: &'static str,
    pub ring: Vec<Pt>,
    pub bank: Option<(String, Vec<Pt>)>,
    pub water: Option<(String, Vec<Pt>)>,
}

/// What the banks grow: bushes and trees as (x, y, radius), hedges as runs of points, and the crop's name.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Crops {
    pub crop: String,
    pub crowns: Vec<(f64, f64, f64)>,
    pub hedges: Vec<Vec<Pt>>,
}

/// The ring shrunk about its middle so each side comes `by` feet in, in proportion to its length against the mean side.
fn shrunk(ring: &[Pt], by: f64) -> Vec<Pt> {
    #[expect(clippy::cast_precision_loss, reason = "a parcel's few corners")]
    let count = ring.len() as f64;
    let middle = (
        ring.iter().map(|p| p.0).sum::<f64>() / count,
        ring.iter().map(|p| p.1).sum::<f64>() / count,
    );
    let mean = (0..ring.len())
        .map(|i| dist(ring[i], ring[(i + 1) % ring.len()]))
        .sum::<f64>()
        / count;
    let s = (1.0 - 2.0 * by / mean.max(1.0)).max(0.05);
    ring.iter()
        .map(|p| {
            (
                middle.0 + (p.0 - middle.0) * s,
                middle.1 + (p.1 - middle.1) * s,
            )
        })
        .collect()
}

/// Points along a closed ring every `step` feet.
fn along(ring: &[Pt], step: f64) -> Vec<Pt> {
    let mut out = Vec::new();
    let mut next = 0.0;
    let mut walked = 0.0;
    for i in 0..ring.len() {
        let (a, b) = (ring[i], ring[(i + 1) % ring.len()]);
        let (len, u) = (dist(a, b), unit(a, b));
        while next <= walked + len {
            let t = next - walked;
            out.push((a.0 + u.0 * t, a.1 + u.1 * t));
            next += step;
        }
        walked += len;
    }
    out
}

/// The village's inset: the median parcel's apothem (twice its area over its perimeter) times one less the square root of the
/// water's `share`, so a median parcel's water is that share of it.
///
/// Research:
///     the inset - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one inset holds for the whole village, measured on its parcel of median area; a drier split draws a wider bank
#[must_use]
pub fn inset(parcels: &[Vec<Pt>], share: f64) -> f64 {
    let mut ap: Vec<f64> = parcels
        .iter()
        .map(|r| {
            2.0 * signed_area(r).abs()
                / (0..r.len())
                    .map(|i| dist(r[i], r[(i + 1) % r.len()]))
                    .sum::<f64>()
                    .max(1.0)
        })
        .collect();
    ap.sort_by(f64::total_cmp);
    ap.get(ap.len() / 2).copied().unwrap_or(0.0) * (1.0 - share.clamp(0.0, 1.0).sqrt())
}

/// The block's `parcels` converted: each rolled from its own stream - rice at one in `RICE_IN` where `leftover` is rice, else a
/// pond, a fry village's smallest ponds its nursery up to `FRY_SHARE` of the ponds - each pond's bank and water rounded at `inset` (a nursery pond's water
/// nearer its bank), and the `crop` its banks grow. Returns the parcels and the crops.
///
/// Research:
///     the leftover form - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: every parcel a pond, or about one parcel in ten left in standing rice
///     the crop on the banks - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: one crop a hamlet, mulberry, fruit or tea
#[must_use]
pub fn convert(
    parcels: &[Vec<Pt>],
    seed: i64,
    inset_ft: f64,
    leftover: &str,
    fry: &str,
    crop: &str,
) -> (Vec<Parcel>, Crops) {
    let rice: Vec<bool> = (0..parcels.len())
        .map(|i| {
            leftover == "rice" && knob_rng(seed, &format!("dikepond:{i}")).randbelow(RICE_IN) == 0
        })
        .collect();
    // a fry village's nursery: its smallest ponds, taken while their water stays within `FRY_SHARE` of the ponds' whole
    let mut nursery = vec![false; parcels.len()];
    if fry == "fry_village" {
        let area = |i: usize| signed_area(&parcels[i]).abs();
        let total: f64 = (0..parcels.len()).filter(|&i| !rice[i]).map(area).sum();
        let mut order: Vec<usize> = (0..parcels.len()).filter(|&i| !rice[i]).collect();
        order.sort_by(|&a, &b| area(a).total_cmp(&area(b)).then(a.cmp(&b)));
        let mut held = 0.0;
        for i in order {
            if held + area(i) > FRY_SHARE * total {
                break;
            }
            held += area(i);
            nursery[i] = true;
        }
    }
    let mut out = Vec::new();
    let mut crops = Crops {
        crop: crop.to_owned(),
        ..Crops::default()
    };
    for (i, ring) in parcels.iter().enumerate() {
        if rice[i] {
            out.push(Parcel {
                kind: "rice",
                ring: ring.clone(),
                bank: None,
                water: None,
            });
            continue;
        }
        let mut rng = knob_rng(seed, &format!("dikepond_shape:{i}"));
        let bank = rounded(ring, 0.0, REACH_FT.0, rng.randbelow(u32::MAX));
        let water = if nursery[i] {
            rounded(ring, FRY_FT.0, FRY_FT.1, rng.randbelow(u32::MAX))
        } else {
            rounded(ring, inset_ft, REACH_FT.1, rng.randbelow(u32::MAX))
        };
        if !nursery[i] {
            grow(ring, inset_ft, crop, &mut rng, &mut crops);
        }
        out.push(Parcel {
            kind: if nursery[i] { "fry" } else { "pond" },
            ring: ring.clone(),
            bank: Some(bank),
            water: Some(water),
        });
    }
    (out, crops)
}

/// The crop on one pond's bank, `width` feet between the parcel's edge and the water.
fn grow(
    ring: &[Pt],
    width: f64,
    crop: &str,
    rolls: &mut crate::pyrand::PyRandom,
    crops: &mut Crops,
) {
    let mut crown = |lo: f64, hi: f64| {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a crown's size in tenths of a foot"
        )]
        let span = ((hi - lo) * 10.0) as u32 + 1;
        lo + f64::from(rolls.randbelow(span)) / 10.0
    };
    match crop {
        "fruit" => {
            for p in along(&shrunk(ring, width / 2.0), FRUIT_FT.0) {
                crops
                    .crowns
                    .push((p.0, p.1, crown(FRUIT_FT.1 .0, FRUIT_FT.1 .1)));
            }
        }
        "tea" => {
            for share in [1.0 / 3.0, 2.0 / 3.0] {
                let pts = along(&shrunk(ring, width * share), 0.5);
                let per = (TEA_FT.1 / 0.5).round().max(1.0);
                #[expect(
                    clippy::cast_possible_truncation,
                    clippy::cast_sign_loss,
                    reason = "a small count of points"
                )]
                let (piece, gap) = (per as usize, (TEA_FT.2 / 0.5).round() as usize);
                let mut k = 0;
                while k + 1 < pts.len() {
                    let end = (k + piece).min(pts.len());
                    crops.hedges.push(pts[k..end].to_vec());
                    k = end + gap;
                }
            }
        }
        _ => {
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a bank's few rows"
            )]
            let rows = ((width / MULBERRY_FT.0).floor() as usize).max(1);
            for r in 0..rows {
                #[expect(clippy::cast_precision_loss, reason = "a bank's few rows")]
                let at = (r as f64 + 0.5) * width / rows as f64;
                for p in along(&shrunk(ring, at), MULBERRY_FT.1) {
                    crops
                        .crowns
                        .push((p.0, p.1, crown(MULBERRY_FT.2 .0, MULBERRY_FT.2 .1)));
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{convert, inset, TEA_FT};
    use crate::field::geom::{inside, signed_area};

    #[test]
    fn the_parcels_converted_and_their_banks_planted() {
        let parcel = |x: f64| vec![(x, 0.0), (x + 160.0, 0.0), (x + 160.0, 320.0), (x, 320.0)];
        let parcels: Vec<_> = (0..20).map(|i| parcel(f64::from(i) * 182.0)).collect();
        let at = inset(&parcels, 0.3);
        assert!((40.0..60.0).contains(&at));
        assert!(inset(&parcels, 0.7) < at);
        assert!(inset(&[], 0.5).abs() < 1e-9);
        let (all_ponds, crops) = convert(&parcels, 4, at, "pond", "none", "mulberry");
        assert!(all_ponds.iter().all(|p| p.kind == "pond"));
        let water = all_ponds[0].water.as_ref().unwrap();
        let share = signed_area(&water.1).abs() / signed_area(&parcels[0]).abs();
        assert!((0.2..0.45).contains(&share));
        assert!(
            crops.crowns.len() > 20 * 100
                && crops
                    .crowns
                    .iter()
                    .all(|c| parcels.iter().any(|r| inside((c.0, c.1), r)))
        );
        let mut sized = parcels.clone();
        sized[0] = vec![(0.0, 0.0), (80.0, 0.0), (80.0, 160.0), (0.0, 160.0)];
        let (mixed, _) = convert(&sized, 4, at, "pond", "fry_village", "fruit");
        assert_eq!(mixed[0].kind, "fry");
        let fry: f64 = mixed
            .iter()
            .filter(|p| p.kind == "fry")
            .map(|p| signed_area(&p.ring).abs())
            .sum();
        let all: f64 = mixed.iter().map(|p| signed_area(&p.ring).abs()).sum();
        assert!(fry <= 0.7 * all + 1e-6 && mixed.iter().any(|p| p.kind == "pond"));
        let rice: Vec<_> = (0..40)
            .flat_map(|s| convert(&parcels, s, at, "rice", "none", "tea").0)
            .filter(|p| p.kind == "rice")
            .collect();
        assert!((20..160).contains(&rice.len()));
        let (_, tea) = convert(&parcels[..1], 4, at, "pond", "none", "tea");
        assert!(tea.hedges.len() > 10 && tea.crowns.is_empty() && TEA_FT.0 > 0.0);
    }
}
