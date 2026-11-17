//! The Rust registry held equal to the Python classes it mirrors, on the real tree (feature 449 T149, `ask:449-phase4-slices` Q1: the
//! Python stays frozen beside it until S7-S11, and an edit of one makes the same change in the other in the same commit).

use std::path::{Path, PathBuf};

use super::{by_file, Registry, HAMLET, HAMLET_REGISTRY, REGISTRIES, SHEET, SHEET_REGISTRY};
use crate::about::{classes, compound_classes, modal_rel, slug};

fn real() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..")
}

/// (module, class, key) of every class of a Python package's family modules, as the lexer the modal checks used reads them.
fn python_kinds(registry: &Registry) -> Vec<(String, String, String)> {
    let dir = real().join(registry.package);
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| Path::new(n).extension().is_some_and(|x| x == "py"))
        .collect();
    names.sort();
    let mut out = Vec::new();
    for name in names {
        let source = std::fs::read_to_string(dir.join(&name)).unwrap();
        let module = name.trim_end_matches(".py").to_owned();
        for k in l7r_guard::suite_tools::pylex::kinds(&source).unwrap() {
            // no class carries modal text since feature 319
            assert_eq!(
                (module.as_str(), k.name.as_str(), k.doc.as_str()),
                (module.as_str(), k.name.as_str(), "")
            );
            out.push((module.clone(), k.name, k.key));
        }
    }
    out
}

/// The `_ORDER` tuple of a package's `__init__.py`: the families in the order its registry lists them.
fn python_order(registry: &Registry) -> Vec<String> {
    let text = std::fs::read_to_string(real().join(registry.package).join("__init__.py")).unwrap();
    let line = text.lines().find(|l| l.starts_with("_ORDER = (")).unwrap();
    line.trim_start_matches("_ORDER = (")
        .trim_end_matches(')')
        .split(',')
        .map(|m| m.trim().to_owned())
        .filter(|m| !m.is_empty())
        .collect()
}

#[test]
fn the_table_is_the_python_classes_name_key_and_order() {
    for registry in &REGISTRIES {
        let rust: Vec<(String, String, String)> = by_file(registry)
            .into_iter()
            .map(|(m, k)| (m.to_owned(), k.class.to_owned(), k.key.to_owned()))
            .collect();
        assert_eq!(rust, python_kinds(registry), "{}", registry.package);
        let families: Vec<&str> = registry.families.iter().map(|f| f.module).collect();
        assert_eq!(families, python_order(registry), "{}", registry.package);
    }
    assert_eq!(HAMLET.iter().map(|f| f.kinds.len()).sum::<usize>(), 61);
    assert_eq!(SHEET.iter().map(|f| f.kinds.len()).sum::<usize>(), 99);
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
    assert_eq!(compound_classes(&real()).unwrap().len(), 99);
    assert_eq!(SHEET_REGISTRY.dir, "sheet");
}
