//! numpy's float32 norm (feature 449 T138).

use super::{normalized, pairwise_sum};

#[test]
fn the_pairwise_sum_takes_numpy_s_three_paths() {
    assert!((pairwise_sum(&[1.0, 2.0, 3.0]) - 6.0).abs() < f32::EPSILON);
    let thirty: Vec<f32> = (1_u16..=30).map(f32::from).collect();
    assert!((pairwise_sum(&thirty) - 465.0).abs() < f32::EPSILON);
    let big: Vec<f32> = (0_u16..1024).map(|i| 1.0 / (1.0 + f32::from(i))).collect();
    // numpy's own sum of these, `np.add.reduce(np.float32(1) / (1 + np.arange(1024, dtype=np.float32)))` (observed 2026-11-16)
    assert_eq!(pairwise_sum(&big).to_bits(), 1_089_489_708);
}

#[test]
fn rows_are_divided_by_their_norm_or_the_floor() {
    assert_eq!(
        normalized(&[3.0, 4.0, 0.0, 0.0], 2),
        vec![0.6, 0.8, 0.0, 0.0]
    );
    assert!(normalized(&[f32::NAN, 1.0], 2)[1].is_nan());
}
