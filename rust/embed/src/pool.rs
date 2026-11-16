//! The first token's state, normalized as `fastembed` normalized it (feature 449 T138): its custom model's `PoolingType.CLS` takes
//! `embeddings[:, 0]`, and `normalization=True` divides each row by `np.maximum(np.linalg.norm(row), 1e-12)`, all in float32. numpy
//! sums the squares by its pairwise summation (`pairwise_sum` in `loops_utils.h.src`: eight running sums under 128 terms, halves above),
//! so the norm here is that sum term for term, and the vectors are the Python's bit for bit (observed 2026-11-16, method: the probes of
//! `onnxruntime.pin` through both).

/// numpy's float32 pairwise sum of `a`.
#[must_use]
pub fn pairwise_sum(a: &[f32]) -> f32 {
    let n = a.len();
    if n < 8 {
        let mut res = 0.0_f32;
        for x in a {
            res += x;
        }
        res
    } else if n <= 128 {
        let mut r = [0.0_f32; 8];
        r.copy_from_slice(&a[..8]);
        let mut i = 8;
        while i < n - n % 8 {
            for (j, s) in r.iter_mut().enumerate() {
                *s += a[i + j];
            }
            i += 8;
        }
        let mut res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
        for x in &a[i..] {
            res += x;
        }
        res
    } else {
        let mut n2 = n / 2;
        n2 -= n2 % 8;
        pairwise_sum(&a[..n2]) + pairwise_sum(&a[n2..])
    }
}

/// Each `dim`-long row of `rows` divided by its norm (at least `1e-12`, as float32).
#[must_use]
pub fn normalized(rows: &[f32], dim: usize) -> Vec<f32> {
    #[expect(
        clippy::cast_possible_truncation,
        reason = "numpy casts the eps to the array's float32 (NEP 50)"
    )]
    let eps = 1e-12_f64 as f32;
    let mut out = Vec::with_capacity(rows.len());
    for row in rows.chunks(dim.max(1)) {
        let squares: Vec<f32> = row.iter().map(|x| x * x).collect();
        // `np.maximum` keeps a NaN where `f32::max` would drop it
        let norm = pairwise_sum(&squares).sqrt();
        let norm = if norm < eps { eps } else { norm };
        out.extend(row.iter().map(|x| x / norm));
    }
    out
}

#[cfg(test)]
mod tests;
