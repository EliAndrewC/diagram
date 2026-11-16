//! The measures a source shows (feature 449 T138): the expected spans are `research_search.measure_passages`'s own on the same texts
//! (observed 2026-11-16, in the interpreter).

use super::measure_passages;

fn terms(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_measures_nearest_the_terms_first_then_the_earliest() {
    let body = format!(
        "{}the field was 10 tan of rice. {}A plot of 3 ken. {}twenty yards square of paddy",
        "x ".repeat(100),
        "y ".repeat(200),
        "z ".repeat(200)
    );
    assert_eq!(
        measure_passages(&body, &terms(&["paddy"]), 2),
        [(927, 1075), (94, 334)]
    );
    assert_eq!(
        measure_passages(&body, &terms(&["rice", ""]), 1),
        [(94, 334)]
    );
    assert_eq!(
        measure_passages("一枚の田は一反、隣は二反。", &terms(&[]), 2),
        [(0, 13)]
    );
    assert!(measure_passages("no numbers here", &terms(&["x"]), 2).is_empty());
    // the dotted capital I folds as Python folds it, and a lowered text longer than the body clamps its window
    assert_eq!(measure_passages("İİİİ 5 ha", &terms(&["ha"]), 2), [(0, 9)]);
}
