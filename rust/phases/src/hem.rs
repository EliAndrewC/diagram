//! The dry hem (feature 444 T28): the hamlet's dry plots laid after the seat, from what the field handed on, with the settlement's
//! ground kept - the houses between the paddy's canal and the dry fields where the settlement stands on the paddy's high edge, the
//! hem just upslope of the canal along the rest (0006).
//!
//! Research:
//!     the hem's stage - NONE: the stage's machinery; each rule's claim is at the unit that keeps it (`field::dry`)

use std::collections::HashMap;

use crate::field::build::HemIn;
use crate::field::dry::{hem, DryPlot, PLOT_FT};
use crate::field::fan::Pt;
use crate::field::index::Index;

/// The square feet in an acre.
///
/// Research:
///     an acre - NONE: a unit's conversion
pub const SQ_FT_PER_ACRE: f64 = 43_560.0;

/// How near the water a dry plot may come, past the water's half-width (feet), as the field laid the hem.
///
/// Research:
///     off the water - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html silent on how near the water a dry plot may come; 1 ft past a filed water's half-width
pub const CLEAR_FT: f64 = 1.0;

/// What the hem stage laid: the dry plots, the grain they hold and the room the hem left (acres), and the counters.
#[derive(Debug, Default)]
pub struct Laid {
    /// The dry plots.
    pub plots: Vec<DryPlot>,
    /// The grain drawn and the room the hem did not take (acres).
    pub grain: (f64, f64),
    /// The counters (D5).
    pub counts: HashMap<String, u64>,
}

fn add(counts: &mut HashMap<String, u64>, key: &str, n: u64) {
    if n > 0 {
        *counts.entry(key.to_owned()).or_insert(0) += n;
    }
}

/// The hem laid from `h` along the field's `ring`, kept off its `water` (each segment at its width) and off the settlement's
/// ground `keep`.
///
/// Research:
///     the dry fields behind the houses - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the hem drawn behind the settlement where it stands on the paddy's high edge, the houses between the canal and the dry fields; just upslope of the canal along the rest
#[must_use]
pub fn lay(h: &HemIn, ring: &[Pt], water: &[(Pt, Pt, f64)], keep: &[Vec<Pt>]) -> Laid {
    let mut counts = HashMap::new();
    let mut ix = Index::default();
    for &(a, b, w) in water {
        ix.file_w(a, b, w);
    }
    add(&mut counts, "write@hem_water", ix.touched);
    let before = (ix.touched, ix.examined, ix.tests);
    let (plots, room, tested) = hem(
        &h.line, h.out, h.down, h.bounds, ring, &mut ix, CLEAR_FT, h.seed, "f0", keep,
    );
    add(&mut counts, "write@dry_plot", 4 * plots.len() as u64);
    add(&mut counts, "write@hem_index", ix.touched - before.0);
    add(&mut counts, "candidate@hem_index", ix.examined - before.1);
    add(&mut counts, "pt_test@hem_onto", tested);
    add(&mut counts, "pt_test@hem_refused", ix.tests - before.2);
    #[expect(clippy::cast_precision_loss, reason = "a hamlet's hundred dry plots")]
    let drawn = plots.len() as f64 * PLOT_FT.0 * PLOT_FT.1;
    Laid {
        plots,
        grain: (drawn / SQ_FT_PER_ACRE, room / SQ_FT_PER_ACRE),
        counts,
    }
}

#[cfg(test)]
mod tests;
