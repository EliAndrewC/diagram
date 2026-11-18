//! The index's leaves held to the Python's answers (feature 449 T151; each printed by `labels/obstacles.py` under `CPython` 3.14.4,
//! 2026-11-18). The index's queries on sixty seeded scenes are `placer/tests.rs`' held cases.
//!
//! Research:
//!     its tests - NONE: the port held to the Python's answers, deciding nothing about a building

use super::{circle_gap, level_rect, names_group, part_of, Obstacle, ObstacleIndex};
use crate::labels::geom::{rect, Pt};

const SQ: [Pt; 4] = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];

#[test]
fn the_leaves_answer_as_the_python_s() {
    assert_eq!(
        (
            circle_gap(&SQ, (5.0, 5.0, 1.0)),
            circle_gap(&SQ, (15.0, 5.0, 2.0))
        ),
        (0.0, 3.0)
    );
    // a well in a court is not the court; a building's own rect is; a shape outside its box is not
    let inner = [(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)];
    assert!(
        !part_of(&inner, &SQ) && part_of(&[(1.0, 1.0), (9.0, 1.0), (9.0, 9.0), (1.0, 9.0)], &SQ)
    );
    assert!(!part_of(
        &[(20.0, 0.0), (30.0, 0.0), (30.0, 10.0), (20.0, 10.0)],
        &SQ
    ));
    assert!(
        level_rect(&SQ) && !level_rect(&rect(0.0, 0.0, 1.0, 1.0, 30.0)) && !level_rect(&SQ[..3])
    );
    assert!(!names_group(None, "x") && !names_group(Some(""), "x"));
    assert!(
        names_group(Some("temple"), "the shrine")
            && names_group(Some("grove"), "old grove")
            && !names_group(Some("grove"), "pines")
    );
    // an index copied is added to without touching the one it came from
    let base = ObstacleIndex::new(vec![Obstacle::new(SQ.to_vec(), 1000.0)], Vec::new());
    let mut more = base.clone();
    more.add(Obstacle::new(inner.to_vec(), 1000.0));
    assert_eq!((base.obstacles.len(), more.obstacles.len()), (1, 2));
}
