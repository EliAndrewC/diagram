//! The page writer's pinned cases held to the Python's answers (feature 449 T150): `python.json`, captured from HEAD's Python before it
//! was deleted, split in three tests so each stays under FR-008's tenth of a second.
//!
//! Research: the page writer's held tests - NONE: the port's answers compared with the Python's, deciding nothing about a building

use std::sync::LazyLock;

use serde_json::Value;

use super::{all_cases, answer, pinned, world};

/// The Python's answers: `[case, answer]` each.
static PYTHON: LazyLock<Vec<(Value, Value)>> = LazyLock::new(|| {
    let v: Value = serde_json::from_str(include_str!("python.json")).unwrap();
    v["pinned"]
        .as_array()
        .unwrap()
        .iter()
        .map(|e| (e[0].clone(), e[1].clone()))
        .collect()
});

/// A world with no vocabulary: the pinned cases read none, and building the real one took most of a tenth of a second.
fn bare() -> super::call::World {
    super::call::World {
        tree: super::real(),
        hamlet: Vec::new(),
        sheet: Vec::new(),
    }
}

/// Every pinned case whose kind `want` accepts answers as the Python did; the count of them.
fn held(want: impl Fn(&str) -> bool) -> usize {
    let w = bare();
    let mut n = 0;
    for (case, python) in PYTHON
        .iter()
        .filter(|(c, _)| want(super::text_of(&c[0]).trim_start_matches('!')))
    {
        assert_eq!(&answer(&w, case), python, "{}", case[0]);
        n += 1;
    }
    n
}

#[test]
fn the_merge_answers_as_the_python_did() {
    assert_eq!(held(|k| k == "merge"), 20);
}

#[test]
fn the_hits_census_and_notes_answer_as_the_python_did() {
    let kinds = [
        "hit_copies",
        "wrap",
        "part_of",
        "census",
        "present",
        "notes",
        "section",
        "hit_regions",
        "hit_layer",
        "keep_clear",
        "join",
        "lane_default",
    ];
    assert_eq!(held(|k| kinds.contains(&k)), 53);
}

#[test]
fn the_raster_and_the_reader_answer_as_the_python_did() {
    let kinds = [
        "merge",
        "hit_copies",
        "wrap",
        "part_of",
        "census",
        "present",
        "notes",
        "section",
        "hit_regions",
        "hit_layer",
        "keep_clear",
        "join",
        "lane_default",
    ];
    assert_eq!(held(|k| !kinds.contains(&k)), 61);
}

/// Every case the cases build that is pinned has its answer in `python.json`, and every answer there is still a case: the fixture never
/// silently stops holding a case. (Building the cases reads both vocabularies, the cost of this test.)
#[test]
fn every_pinned_case_has_the_python_s_answer() {
    let w = world(&super::real());
    let built: Vec<Value> = all_cases(&w).into_iter().filter(pinned).collect();
    let kept: Vec<&Value> = PYTHON.iter().map(|(c, _)| c).collect();
    assert_eq!(built.len(), kept.len());
    assert!(built.iter().zip(&kept).all(|(a, b)| a == *b));
}
