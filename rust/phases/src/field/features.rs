//! The features in the middle of the fields (feature 444 T16): the pocket pond sunk in one low plot, and the grave - an island
//! that splits its plot in two, or a corner grave the bund is carried round.
//!
//! Research:
//!     ponds, rocks and graves - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: paddy on a broad valley floor - a pond on a low plot, no rock outcrop, may have a grave

use super::fan::Pt;
use super::geom::{dist, signed_area};
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
///     the pond's size - GUESS: 0008 sinks it wholly in one plot, never across a bund, and gives no size; 0.4 and 0.28 of the plot's shorter side
pub const POND_SHARE: (f64, f64) = (0.4, 0.28);
/// The share of maps that draw a grave in the fields, in tenths.
///
/// Research:
///     the grave's odds - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: about three maps in ten, this project's choice and an arbitrary one
pub const GRAVE_IN_TEN: u32 = 3;
/// How far in from its corner a corner grave stands, and the half-breadth of the bund carried round it (feet).
///
/// Research:
///     the corner grave - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a short step in from its corner, with the bund carried round it; the step and the bund's reach a GUESS, 8 and 14 ft
pub const CORNER_FT: (f64, f64) = (8.0, 14.0);

/// A pocket pond: its middle and its two radii (feet).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Pond {
    pub x: f64,
    pub y: f64,
    pub rx: f64,
    pub ry: f64,
}

/// A grave in the fields: where it stands, its form, and the plots it leaves in place of its host (the host's index first).
#[derive(Debug, Clone, PartialEq)]
pub struct Grave {
    pub at: Pt,
    pub form: &'static str,
    pub host: usize,
    pub rings: Vec<Vec<Pt>>,
}

fn centroid(ring: &[Pt]) -> Pt {
    #[expect(clippy::cast_precision_loss, reason = "a basin's handful of corners")]
    let n = ring.len() as f64;
    (
        ring.iter().map(|p| p.0).sum::<f64>() / n,
        ring.iter().map(|p| p.1).sum::<f64>() / n,
    )
}

/// The pocket pond, if this map sinks one: in a plot of the lowest row chosen from the seed, wholly inside it.
///
/// Research:
///     the pond in a low plot - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: sunk wholly in one low plot, never across a bund
#[must_use]
pub fn pocket_pond(basins: &[Basin], seed: i64, tag: &str) -> Option<(usize, Pond)> {
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
    Some((
        i,
        Pond {
            x,
            y,
            rx: short * POND_SHARE.0,
            ry: short * POND_SHARE.1,
        },
    ))
}

/// The grave, if this map draws one: a plot rolled from the seed (never `skip`, the pond's), its form `form` (the `grave_form`
/// knob, rolled by the caller from its table). An island splits its host through the mound into two plots across the fall; a
/// corner grave carves its host's first corner round the mound. A cut that would break a basin's rule is refused, and the next
/// plot tried, a bounded number of times.
///
/// Research:
///     the island splits its plot - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: the host plot is split in two through the mound, as if a bund were run out to the island, a GUESS
///     the bund round the corner - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a short step in from its corner, with the bund carried round it, a GUESS
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
        let r = &basins[host].ring;
        let (at, rings) = if form == "island" {
            let (a, b) = (mid(r[0], r[3]), mid(r[1], r[2]));
            (
                mid(a, b),
                vec![vec![r[0], r[1], b, a], vec![a, b, r[2], r[3]]],
            )
        } else {
            let (into1, into3) = (
                toward(r[0], r[1], CORNER_FT.1),
                toward(r[0], r[3], CORNER_FT.1),
            );
            let at = toward(r[0], mid(r[1], r[3]), CORNER_FT.0 + CORNER_FT.1 / 2.0);
            (at, vec![vec![into1, r[1], r[2], r[3], into3]])
        };
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

fn mid(a: Pt, b: Pt) -> Pt {
    ((a.0 + b.0) / 2.0, (a.1 + b.1) / 2.0)
}

fn toward(a: Pt, b: Pt, d: f64) -> Pt {
    let u = super::geom::unit(a, b);
    (a.0 + u.0 * d, a.1 + u.1 * d)
}

#[cfg(test)]
mod tests {
    use super::{grave, pocket_pond};
    use crate::field::fan::fan;
    use crate::field::geom::{inside, signed_area};
    use crate::field::lattice::basins;
    use crate::field::rules::held;

    #[test]
    fn the_pond_sits_in_a_low_plot_and_the_grave_keeps_the_rules() {
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0));
        let b = basins(&f, 4);
        let last = b.iter().map(|x| x.row).max().unwrap();
        let ponds: Vec<_> = (0..40).filter_map(|s| pocket_pond(&b, s, "f0")).collect();
        assert!(
            (10..35).contains(&ponds.len()),
            "a little over half: {}",
            ponds.len()
        );
        for (i, p) in &ponds {
            assert_eq!(b[*i].row, last);
            assert!(
                inside((p.x + p.rx, p.y), &b[*i].ring) || inside((p.x, p.y + p.rx), &b[*i].ring)
            );
        }
        let mut seen = (0, 0);
        for s in 0..40 {
            for form in ["island", "corner"] {
                if let Some(g) = grave(&b, s, "f0", form, None, 1488.0).unwrap() {
                    let whole = signed_area(&b[g.host].ring).abs();
                    let parts: f64 = g.rings.iter().map(|r| signed_area(r).abs()).sum();
                    assert!(parts <= whole + 1e-6);
                    assert!(g.rings.iter().all(|r| held(r, 1488.0).is_ok()));
                    if form == "island" {
                        seen.0 += 1;
                        assert!((parts - whole).abs() < 1e-6)
                    } else {
                        seen.1 += 1
                    }
                }
            }
        }
        assert!(seen.0 > 3 && seen.1 > 3, "{seen:?}");
        assert!(pocket_pond(&[], 1, "f0").is_none());
        assert!(grave(&[], 1, "f0", "island", None, 1488.0)
            .unwrap()
            .is_none());
        let tiny: Vec<_> = b.iter().take(1).cloned().collect();
        let refused = (0..40).find_map(|s| grave(&tiny, s, "f0", "island", Some(0), 1488.0).err());
        assert!(
            refused.is_some(),
            "a grave with no host it may take is refused"
        );
    }
}
