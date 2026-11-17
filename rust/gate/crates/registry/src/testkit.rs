//! A scratch tree the registry loads from (feature 449 T149): every kind's modal file, minimal and valid, and an empty sibling table, so
//! a crate whose tests load the registries (`owed`'s entry-drift report) needs no copy of the real modals.

use std::path::Path;

use crate::about::modal_rel;
use crate::kinds::{Registry, HAMLET_REGISTRY, REGISTRIES};

/// A modal's text naming `entry` as the questions it was written from.
#[must_use]
pub fn modal(name: &str, entry: &str) -> String {
    format!("About: A {name}.\n\nName: {name}\nCovers: `{name}`\nSources: not recorded\nEntry: {entry}\n")
}

/// Every kind's file under `root`, each written from `entry`, and an empty sibling table.
pub fn modals(root: &Path, entry: &str) {
    for registry in &REGISTRIES {
        kinds(root, registry, entry);
    }
    siblings(root);
}

/// The hamlet vocabulary's files alone and the sibling table: what a reader of `classes` alone loads, a smaller fixture for FR-008's
/// tenth of a second.
pub fn hamlet(root: &Path, entry: &str) {
    kinds(root, &HAMLET_REGISTRY, entry);
    siblings(root);
}

fn kinds(root: &Path, registry: &Registry, entry: &str) {
    for (_, kind) in registry.kinds() {
        put(
            root,
            &modal_rel(registry, kind.key),
            &modal(kind.key, entry),
        );
    }
}

fn siblings(root: &Path) {
    put(
        root,
        "l7r/diagram/interactive/assets/siblings.json",
        "{\"texts\": {}, \"pairs\": []}\n",
    );
}

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let _ = std::fs::write(path, text);
}
