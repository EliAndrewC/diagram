//! The dike-pond's conversion (feature 444 T16, the polder's seam): which parcels are ponds, nursery ponds or rice; each pond's
//! bank and water rounded from its parcel at the village's split; and the crop on the banks. Written from the record; the old
//! overlay's placement unread.
//!
//! Research:
//!     ponds ringed by banks - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: ponds of uneven shape, each ringed by a bank of its own mud planted with rows of low mulberry bushes
//!     one inset a village - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one inset holds for the whole village, measured on its parcel of median area - the fry ponds' banks the same

use super::fan::Pt;
use super::geom::{dist, signed_area, unit};
use super::ponds::{pushed_in, rounded};
use crate::pyrand::knob_rng;

/// A pond's bank or water: its SVG path and the points that sample it.
///
/// Research:
///     a path - NONE: the record's type
type Path = (String, Vec<Pt>);

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
/// A bank's reach (the corner's rounding) and a pond's (feet).
///
/// Research:
///     the rounding - GUESS: research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html silent on a pond's corners; the bank's cut back 8 ft and the water's 16 ft
pub const REACH_FT: (f64, f64) = (8.0, 16.0);
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
///     tea on the bank - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: two clipped hedges along the bank, each about 3 ft wide and broken every 7.5 ft, a GUESS - the breaks 1.5 ft long, a GUESS too
pub const TEA_FT: (f64, f64, f64) = (3.0, 7.5, 1.5);

/// One converted parcel: its kind (`pond`, `fry` or `rice`), its parcel, and for a pond its bank and water (the SVG path and its
/// samples).
///
/// Research:
///     a parcel's record - NONE: the record's type, holding what `convert` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Parcel {
    pub kind: &'static str,
    pub ring: Vec<Pt>,
    pub bank: Option<(String, Vec<Pt>)>,
    pub water: Option<(String, Vec<Pt>)>,
}

/// What the banks grow: bushes and trees as (x, y, radius), hedges as runs of points, and the crop's name.
///
/// Research:
///     the crops' record - NONE: the record's type, holding what `grow` decides
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Crops {
    pub crop: String,
    pub crowns: Vec<(f64, f64, f64)>,
    pub hedges: Vec<Vec<Pt>>,
}

/// The ring pushed in `by` feet on every side (`ponds::pushed_in`), the line a row of the bank's crop runs on; the ring itself
/// where the bank holds no such line.
///
/// Research:
///     the row's line - NONE: geometry
fn shrunk(ring: &[Pt], by: f64) -> Vec<Pt> {
    pushed_in(ring, by).unwrap_or_else(|| ring.to_vec())
}

/// Points along a closed ring every `step` feet.
///
/// Research:
///     the stations - NONE: geometry
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

/// The village's inset: the bank's width at which the parcel of median area, pushed in that far on every side, keeps the water's
/// `share` of itself - for a four-sided parcel of area A and perimeter P its water is A - P d + 4 d^2, solved for d.
///
/// Research:
///     the inset - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one inset holds for the whole village, measured on its parcel of median area; a drier split draws a wider bank
#[must_use]
pub fn inset(parcels: &[Vec<Pt>], share: f64) -> f64 {
    let mut by_area: Vec<&Vec<Pt>> = parcels.iter().collect();
    by_area.sort_by(|a, b| signed_area(a).abs().total_cmp(&signed_area(b).abs()));
    let Some(median) = by_area.get(by_area.len() / 2) else {
        return 0.0;
    };
    let area = signed_area(median).abs();
    let perimeter: f64 = (0..median.len())
        .map(|i| dist(median[i], median[(i + 1) % median.len()]))
        .sum();
    let dry = 1.0 - share.clamp(0.0, 1.0);
    (perimeter - (perimeter * perimeter - 16.0 * area * dry).max(0.0).sqrt()) / 8.0
}

/// The block's `parcels` converted: each rolled from its own stream - rice at one in `RICE_IN` where `leftover` is rice, else a
/// pond, each pond's bank and water rounded at `inset` and its bank planted with the `crop`; a fry village's smallest ponds its
/// nursery while their water stays within `FRY_SHARE` of the ponds'. Returns the parcels and the crops.
///
/// Research:
///     the leftover form - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: every parcel a pond, or about one parcel in ten left in standing rice
///     the rice scattered - GUESS: research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html silent on where the leftover rice stands among the ponds; each parcel rolled on its own
///     the bank on the parcel's line - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: each pond ringed by a bank of its own mud - the bank's outer edge the parcel's own line, the water pushed in the village's inset from it
///     the ponds' uneven shapes - GUESS: research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html silent on how uneven, giving ponds of uneven shape; the bank and the water each rounded at its own reach (`REACH_FT`), a corner's cut rolled about it
///     the crop on the banks - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: every dike of a dike-pond hamlet is planted, and all of them with one crop - mulberry, fruit or tea, the nursery's banks too
///     the fry ponds - research/questions/0024-fish-fry-and-nursery-ponds-yumiao.drawing.html: the smallest ponds are given to fry until they hold up to seven-tenths of its pond water - taken smallest first by their water's area while the water they hold stays within `FRY_SHARE` of every pond's
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
    let mut crops = Crops {
        crop: crop.to_owned(),
        ..Crops::default()
    };
    // each pond's bank and water, and its bank's crop, from its own stream
    let mut built: Vec<Option<(Path, Path)>> = Vec::new();
    for (i, ring) in parcels.iter().enumerate() {
        if rice[i] {
            built.push(None);
            continue;
        }
        let mut rng = knob_rng(seed, &format!("dikepond_shape:{i}"));
        let bank = rounded(ring, 0.0, REACH_FT.0, rng.randbelow(u32::MAX));
        let water = rounded(ring, inset_ft, REACH_FT.1, rng.randbelow(u32::MAX));
        grow(ring, inset_ft, crop, &mut rng, &mut crops);
        built.push(Some((bank, water)));
    }
    // a fry village's nursery: its smallest ponds, taken while their water stays within `FRY_SHARE` of the ponds' whole
    let wet = |i: usize| {
        built[i]
            .as_ref()
            .map_or(0.0, |(_, w)| signed_area(&w.1).abs())
    };
    let mut nursery = vec![false; parcels.len()];
    if fry == "fry_village" {
        let total: f64 = (0..parcels.len()).map(wet).sum();
        let mut order: Vec<usize> = (0..parcels.len()).filter(|&i| !rice[i]).collect();
        order.sort_by(|&a, &b| wet(a).total_cmp(&wet(b)).then(a.cmp(&b)));
        let mut held = 0.0;
        for i in order {
            if held + wet(i) > FRY_SHARE * total {
                break;
            }
            held += wet(i);
            nursery[i] = true;
        }
    }
    let mut out = Vec::new();
    for (i, (ring, made)) in parcels.iter().zip(built).enumerate() {
        let (kind, bank, water) = match made {
            None => ("rice", None, None),
            Some((bank, water)) => (
                if nursery[i] { "fry" } else { "pond" },
                Some(bank),
                Some(water),
            ),
        };
        out.push(Parcel {
            kind,
            ring: ring.clone(),
            bank,
            water,
        });
    }
    (out, crops)
}

/// The crop on one pond's bank, `width` feet between the parcel's edge and the water.
///
/// Research:
///     mulberry rows - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: one row to every 5.5 ft of the bank's width, set evenly across it
///     the fruit's line - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: a single line of trees - on the bank's middle
///     tea's two hedges - GUESS: research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html silent on where across the bank the two hedges stand; at a third and two thirds of its width
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
        // a bank wider than its parcel: the fruit's line on the parcel's own edge, the pond the least one
        let (small, fruit) = convert(&parcels[..1], 4, 200.0, "pond", "none", "fruit");
        assert!(small[0].water.is_some() && !fruit.crowns.is_empty());
    }
}
