//! Similarity and its order (feature 449 T138).

use super::{order, sims};
use crate::npz::f32_to_half;

#[test]
fn similarities_and_their_order_ties_in_row_order() {
    let rows: Vec<u16> = [1.0_f32, 0.0, 0.5, 0.5, 0.0, 1.0, 1.0, 0.0, -0.0, 0.0]
        .iter()
        .map(|x| f32_to_half(*x))
        .collect();
    let s = sims(&rows, 2, &[1.0, 0.0]);
    assert_eq!(s, [1.0, 0.5, 0.0, 1.0, -0.0]);
    assert_eq!(order(&s), [0, 3, 1, 2, 4]);
    // eight lanes and a remainder
    let long: Vec<u16> = (0_u8..19).map(|i| f32_to_half(f32::from(i))).collect();
    assert_eq!(sims(&long, 19, &[1.0; 19]), [171.0]);
}
