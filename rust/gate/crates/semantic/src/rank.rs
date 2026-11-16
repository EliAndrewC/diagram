//! Similarity and its order (feature 449 T138), the two places the Python's numpy did the work and the Rust cannot repeat it bit for bit.
//!
//! THE PRODUCT: numpy multiplied the half-precision vectors, read as float32, by the question in float32 through `OpenBLAS`, whose kernel
//! and thread count set the last bits of each similarity (HEAD itself: `OPENBLAS_NUM_THREADS=1` or another core type changed the bits of
//! all 47 recorded queries' similarities and no query's `find` or meaning order; observed 2026-11-16, method: `scratchpad/t138/headrun.py`
//! under each setting). Here: float32 products summed in eight lanes, then the lanes - not `OpenBLAS`'s order, the same kind of float32
//! sum.
//!
//! THE ORDER: numpy's default `argsort` (`np.argsort(-sims)`), whose order among EXACT ties is that of the sort numpy dispatches for the
//! CPU. A passage stored twice - a capture's `text.txt` and `served.txt`, a page captured twice - is one similarity where its copies were
//! embedded alike: of 2,437 such groups among the recorded queries' 600 nearest, 2,373 had bit-equal similarities in HEAD's own
//! arithmetic, and 64 did not - their copies, it is inferred, embedded in different batches (observed 2026-11-16, method: `scratchpad/t138/tiesims.py`).
//! HEAD with `NPY_DISABLE_CPU_FEATURES=X86_V3` changed the tied passages `research-search` shows on 27 of the 47 recorded queries, never a
//! source's order (observed 2026-11-16, method: `scratchpad/t138/headrun.py`). Here: ties in the index's own order (shard, then row), a
//! stable sort, as the round arbiter ruled (`ask:449-T138-ties`, written into FR-002): among exactly tied hits whose fingerprints and
//! vectors are identical the copy at the lowest index position prints, which copy is not bound; and at an all-hits depth (`find` at a
//! negative K) hits whose HEAD similarities differ by under 1e-7 may change order, the set of hits and every printed similarity bound.

use crate::npz::half_to_f32;
use std::sync::LazyLock;

/// Every half-precision bit pattern's float (the `astype(np.float32)` of a stored vector).
static HALF: LazyLock<Vec<f32>> = LazyLock::new(|| (0..=u16::MAX).map(half_to_f32).collect());

/// The similarity of each `dim`-long row of `vecs` (half-precision bits) with `q`.
#[must_use]
pub fn sims(vecs: &[u16], dim: usize, q: &[f32]) -> Vec<f32> {
    let half = &*HALF;
    vecs.chunks(dim.max(1))
        .map(|row| {
            let mut lanes = [0.0_f32; 8];
            let mut chunks = row.chunks_exact(8);
            let mut at = 0;
            for c in &mut chunks {
                for (j, lane) in lanes.iter_mut().enumerate() {
                    *lane += half[usize::from(c[j])] * q[at + j];
                }
                at += 8;
            }
            let mut s = ((lanes[0] + lanes[1]) + (lanes[2] + lanes[3]))
                + ((lanes[4] + lanes[5]) + (lanes[6] + lanes[7]));
            for (j, h) in chunks.remainder().iter().enumerate() {
                s += half[usize::from(*h)] * q[at + j];
            }
            s
        })
        .collect()
}

/// The rows by similarity, the nearest first (`np.argsort(-sims)`), ties in the rows' order.
#[must_use]
pub fn order(sims: &[f32]) -> Vec<usize> {
    let mut idx: Vec<usize> = (0..sims.len()).collect();
    // `partial_cmp`, not `total_cmp`: numpy holds -0.0 and 0.0 equal
    idx.sort_by(|&a, &b| {
        sims[b]
            .partial_cmp(&sims[a])
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(a.cmp(&b))
    });
    idx
}

#[cfg(test)]
mod tests;
