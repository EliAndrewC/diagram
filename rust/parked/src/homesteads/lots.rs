//! The households' lots (feature 444 T30): each declared household's house on the size ladder, and whether it keeps a storehouse, a
//! beast and each fixture kind - dealt once a seating by quota, exactly round(n x share) households a part, the k-th household
//! seated taking lot k. The shuffles are Python's string-seeded `random.Random`, so a seat deals the lot it dealt.
//!
//! Research:
//!     storehouse to the largest houses - DEVIATION research/questions/0040-farm-storehouses-kura.html: a strict cut down the size ladder where the one village's count shows a tendency
//!     storehouse tie - research/questions/0040-farm-storehouses-kura.drawing.html: between two houses of one size, the seeded order decides
//!     beast keepers by quota - research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html: exactly round(n x the byre share) households, by the shuffled order
//!     fixtures by quota - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: exactly round(n x share) households per kind, every kind but the wood shed by the shuffled order
//!     wood shed to the larger houses - research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: the wood shed dealt down the size ladder

use super::fixtures::Kind;
use crate::pyrand::PyRandom;

/// The farmhouse's length and depth ranges, as factors of the ordinary minka's 46 by 28 ft.
///
/// Research:
///     farmhouse length range - research/questions/0029-farmhouses-minka.drawing.html: 0.85 to 1.35 of the 46 ft base
///     farmhouse depth range - research/questions/0029-farmhouses-minka.drawing.html: 0.90 to 1.10 of the 28 ft base
pub const FACTORS: ((f64, f64), (f64, f64)) = ((0.85, 1.35), (0.90, 1.10));

/// The share of households keeping a storehouse.
///
/// Research:
///     storehouse share - research/questions/0040-farm-storehouses-kura.html, research/questions/0040-farm-storehouses-kura.drawing.html: one farm in eight
pub const KURA_SHARE: f64 = 0.125;

/// Does the `j`-th member of a quota ordering carry a part of share `p`? The Bresenham step: exactly round(n x p) of the first n do.
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "a household ordinal of a few hundred"
)]
pub fn quota_member(j: usize, p: f64) -> bool {
    ((j as f64 + 1.0) * p + 0.5).floor() > (j as f64 * p + 0.5).floor()
}

/// A seed-shuffled place for each of `n` households, by the seed and the salt alone.
#[must_use]
pub fn order(seed: i64, salt: &str, n: usize) -> Vec<usize> {
    PyRandom::from_text(&format!("{seed}:{salt}")).shuffled(n)
}

/// Which of `n` households carry a part of share `p`: exactly round(n x p), by the shuffled order.
#[must_use]
pub fn quota_carriers(seed: i64, salt: &str, n: usize, p: f64) -> Vec<bool> {
    order(seed, salt, n)
        .into_iter()
        .map(|j| quota_member(j, p))
        .collect()
}

/// Which households carry a part of share `p` taken largest footprint first, the shuffled order breaking ties.
#[must_use]
pub fn larger_first(seed: i64, salt: &str, sizes: &[(f64, f64)], p: f64) -> Vec<bool> {
    let n = sizes.len();
    let count = quota_carriers(seed, salt, n, p)
        .iter()
        .filter(|c| **c)
        .count();
    let ord = order(seed, salt, n);
    let mut ranked: Vec<usize> = (0..n).collect();
    ranked.sort_by(|&a, &b| {
        (-(sizes[a].0 * sizes[a].1))
            .total_cmp(&-(sizes[b].0 * sizes[b].1))
            .then(ord[a].cmp(&ord[b]))
    });
    let mut keep = vec![false; n];
    for &k in &ranked[..count] {
        keep[k] = true;
    }
    keep
}

/// `n` (length, depth) factor pairs, one rung a household: the lengths and the depths each spread evenly over their range, each
/// ladder in its own seed-shuffled order.
///
/// Research:
///     house sizes spread evenly - research/questions/0029-farmhouses-minka.drawing.html: a stratified ladder over the length and depth ranges, length and depth shuffled apart
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    reason = "a household count of a few hundred"
)]
pub fn size_ladder(seed: i64, n: usize) -> Vec<(f64, f64)> {
    let rungs = |(lo, hi): (f64, f64)| -> Vec<f64> {
        (0..n)
            .map(|i| lo + (hi - lo) * (i as f64 + 0.5) / n as f64)
            .collect()
    };
    let (lengths, depths) = (rungs(FACTORS.0), rungs(FACTORS.1));
    let (lo, de) = (order(seed, "size_length", n), order(seed, "size_depth", n));
    (0..n).map(|k| (lengths[lo[k]], depths[de[k]])).collect()
}

/// The fixture kinds a seating names, in the stage's order of kinds, as the salts the deals key on.
#[must_use]
pub fn kind_name(kind: Kind) -> &'static str {
    match kind {
        Kind::Retirement => "retirement",
        Kind::Bath => "bath",
        Kind::Woodpile => "woodpile",
        Kind::Privy => "privy",
        Kind::Manure => "manure",
        Kind::Coop => "coop",
        Kind::Shrine => "shrine",
        Kind::Grave => "grave",
        Kind::Persimmon => "persimmon",
    }
}

/// One household's lot: its house (feet), whether it keeps a storehouse and a beast, and its fixture kinds.
pub type LotOf = ((f64, f64), bool, bool, Vec<Kind>);

/// The lots of one settlement's households.
pub struct Lots {
    /// Each household's size factors.
    pub sizes: Vec<(f64, f64)>,
    /// Whether each keeps a storehouse.
    pub kura: Vec<bool>,
    /// Whether each keeps a beast.
    pub byre: Vec<bool>,
    /// Each fixture kind and which households keep it, in the seating's order of kinds.
    pub fixtures: Vec<(Kind, Vec<bool>)>,
}

impl Lots {
    /// The lots dealt for `n` households at `seed`: the ladder, the storehouses down it, the beasts and each fixture kind.
    #[must_use]
    pub fn deal(seed: i64, n: usize, byre_share: f64, shares: &[(Kind, f64)]) -> Self {
        let sizes = size_ladder(seed, n);
        let kura = larger_first(seed, "kura", &sizes, KURA_SHARE);
        let byre = quota_carriers(seed, "byre", n, byre_share);
        let fixtures = shares
            .iter()
            .map(|&(k, p)| {
                let salt = format!("fixture_{}", kind_name(k));
                (
                    k,
                    if k == Kind::Woodpile {
                        larger_first(seed, &salt, &sizes, p)
                    } else {
                        quota_carriers(seed, &salt, n, p)
                    },
                )
            })
            .collect();
        Self {
            sizes,
            kura,
            byre,
            fixtures,
        }
    }

    /// Household `k`'s house (feet), whether it keeps a storehouse and a beast, and its fixture kinds; None past the count.
    #[must_use]
    pub fn lot(&self, k: usize) -> Option<LotOf> {
        let &(lf, df) = self.sizes.get(k)?;
        let kinds = self
            .fixtures
            .iter()
            .filter(|(_, c)| c[k])
            .map(|(kind, _)| *kind)
            .collect();
        Some(((46.0 * lf, 28.0 * df), self.kura[k], self.byre[k], kinds))
    }
}
