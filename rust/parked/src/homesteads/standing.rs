//! The standing ground a household's way is asked of (feature 444 T30): its line on ground the site admits, sampled every 8 ft
//! (the free ground's raster, a sample past its window asked of the site beyond), no reserved wood seat within the lane's gap,
//! and no other homestead within the corridor's half-width - remembered per line while nothing standing changes
//! (`rolling/access.py` `standing_ground`, `_standing_clear`, `site_edge_samples`, `site_samples_clear`; `wood_share.py`
//! `corridor_bars`).
//!
//! Research:
//!     no path corridor within its half-width of any placed footprint - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing is built on a path, so the corridor clears every placed footprint by its half-width
//!     path refused over a household's reserved grove seats - research/questions/0081-village-lanes.drawing.html: a path goes round a grove, never across one (0036, 0072)
//!     corridor geometry, memo and search plumbing - NONE: the site raster, the reach index and the exact gap

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::collections::HashMap;

use super::access::seg_box_within;
use super::fit::GRID;
use super::ground::Ground;
use super::layout::Rect;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// A line's site samples' pitch (ft).
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 8 (sampling step along a corridor)
pub const SAMPLE_FT: f64 = 8.0;

#[expect(clippy::cast_possible_truncation, reason = "cells of a few hundred")]
fn cell(v: f64) -> i64 {
    (v / GRID).floor() as i64
}

/// What stands that a household's way keeps off: the site's ground, the reserved seats, the other homesteads' boxes.
pub struct Standing<'a> {
    ground: &'a Ground,
    beyond: &'a dyn Fn(Pt) -> bool,
    wood: &'a Shares,
    placed: Vec<Rect>,
    grid: HashMap<(i64, i64), Vec<usize>>,
    half: f64,
    lane_gap: f64,
    memo: HashMap<(i64, i64, i64, i64, Option<usize>), bool>,
}

impl<'a> Standing<'a> {
    /// What stands: the site's ground and what lies beyond its window, the seats reserved, the homesteads' boxes (filed by cell),
    /// the corridor's half-width and the lane's gap off a seat.
    #[must_use]
    pub fn new(
        ground: &'a Ground,
        beyond: &'a dyn Fn(Pt) -> bool,
        wood: &'a Shares,
        placed: &[Rect],
        gaps: (f64, f64),
    ) -> Self {
        let mut grid: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
        for (k, b) in placed.iter().enumerate() {
            for i in cell(b.0 - b.2 / 2.0)..=cell(b.0 + b.2 / 2.0) {
                for j in cell(b.1 - b.3 / 2.0)..=cell(b.1 + b.3 / 2.0) {
                    grid.entry((i, j)).or_default().push(k);
                }
            }
        }
        Self {
            ground,
            beyond,
            wood,
            placed: placed.to_vec(),
            grid,
            half: gaps.0,
            lane_gap: gaps.1,
            memo: HashMap::new(),
        }
    }

    /// Does the line a-b clear what stands - its own homestead's box (`own`, an index of the placed) aside? Remembered per line.
    pub fn clear(&mut self, a: Pt, b: Pt, own: Option<usize>, tests: &mut Counts) -> bool {
        #[expect(
            clippy::cast_possible_truncation,
            reason = "a key of thousandths of a foot"
        )]
        let r = |v: f64| (v * 1000.0).round() as i64;
        let key = (r(a.0), r(a.1), r(b.0), r(b.1), own);
        if let Some(&hit) = self.memo.get(&key) {
            return hit;
        }
        let hit = self.ask(a, b, own, tests);
        self.memo.insert(key, hit);
        hit
    }

    fn ask(&self, a: Pt, b: Pt, own: Option<usize>, tests: &mut Counts) -> bool {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a few hundred 8 ft samples"
        )]
        let n = ((dist(a, b) / SAMPLE_FT) as u32).max(1);
        tests.add("pt_test@standing_clear", u64::from(n) + 1);
        let taken = (0..=n).any(|k| {
            let f = f64::from(k) / f64::from(n);
            let p = (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f);
            self.ground.taken_at(p).unwrap_or_else(|| (self.beyond)(p))
        });
        if taken || self.wood.corridor_bars(a, b, self.lane_gap, tests) {
            return false;
        }
        let h = self.half;
        let mut seen = Vec::new();
        for i in cell(a.0.min(b.0) - h)..=cell(a.0.max(b.0) + h) {
            for j in cell(a.1.min(b.1) - h)..=cell(a.1.max(b.1) + h) {
                for &k in self.grid.get(&(i, j)).map_or(&[][..], Vec::as_slice) {
                    if Some(k) == own || seen.contains(&k) {
                        continue;
                    }
                    seen.push(k);
                    if seg_box_within(a, b, self.placed[k], h, tests) {
                        return false;
                    }
                }
            }
        }
        true
    }
}
