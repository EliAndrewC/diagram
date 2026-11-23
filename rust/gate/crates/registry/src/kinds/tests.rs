//! The registry on the real tree (feature 449 T149): its counts and order, and every kind's modal file. The test that held it equal to
//! the Python classes it mirrored went with those classes (feature 449 T158: a lockstep test retires with its Python).

use std::path::{Path, PathBuf};

use super::{by_file, HAMLET, HAMLET_REGISTRY, REGISTRIES, SHEET, SHEET_REGISTRY};
use crate::about::{classes, compound_classes, modal_rel, slug};

fn real() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..")
}

#[test]
fn the_table_counts_its_kinds_in_its_order() {
    assert_eq!(HAMLET.iter().map(|f| f.kinds.len()).sum::<usize>(), 61);
    assert_eq!(SHEET.iter().map(|f| f.kinds.len()).sum::<usize>(), 101);
    assert_eq!(HAMLET_REGISTRY.kinds()[0].1.key, "farmhouse");
    assert_eq!(by_file(&HAMLET_REGISTRY)[0].0, "dikepond");
}

#[test]
fn every_kind_has_its_file_and_no_file_is_an_orphan() {
    for registry in &REGISTRIES {
        let mut want: Vec<String> = registry
            .kinds()
            .iter()
            .map(|(_, k)| format!("{}.md", slug(k.key)))
            .collect();
        want.sort();
        let dir = real()
            .join(modal_rel(registry, "x"))
            .parent()
            .unwrap()
            .to_path_buf();
        let mut have: Vec<String> = std::fs::read_dir(dir)
            .unwrap()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .collect();
        have.sort();
        assert_eq!(have, want, "{}", registry.dir);
    }
    // and every file is one the registry loads (the Python's import)
    assert_eq!(classes(&real()).unwrap().len(), 61);
    assert_eq!(compound_classes(&real()).unwrap().len(), 101);
    assert_eq!(SHEET_REGISTRY.dir, "sheet");
}
