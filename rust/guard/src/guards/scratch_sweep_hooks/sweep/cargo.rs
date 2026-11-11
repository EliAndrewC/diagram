//! The cargo target cache's share of the sweep (feature 449 T102, FR-013; the GM 2026-11-11: "Fix those leaks as well"). Every tree
//! that builds gets its own `~/.cache/l7r-cargo-target/<tree name>/` (`scripts/gates/l7r-gate.sh`), and nothing removed one: a scratch
//! clone's or a worktree's outlived it, and inside a live clone's, cargo keeps one variant of a crate per path and flag set it was ever
//! built with (`deps/`, `incremental/`, `.fingerprint/`, `build/`), a source edit making none but a moved path or a changed flag making a
//! new one each time - 3,407 `l7r_fixture` variants, ~5.6 GB, in one clone's `debug/` (observed 2026-11-11, method: `ls | grep -c` and
//! `du -ch` on that target). 54 GB in 56 directories in all.
//!
//! Two rules: (a) a build directory named for no live tree - neither the mirror nor any clone under the clones directory - goes once
//! nothing in it changed in the threshold; the mirror's and every clone's are never removed whole (the guard hook runs the mirror's
//! kept binary); (b) inside every directory kept, each crate's variants in a store beyond its newest four go once each is idle past the
//! threshold. Four, because a crate's live variants are its test build, its lint build and its all-features build, at most three at a
//! time; one wrongly taken costs only its rebuild. Where the clones directory cannot be read, no build directory is removed whole.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

use super::{children, newest, Config};

/// The newest variants of a crate a store always keeps.
const KEPT: usize = 4;
/// The stores where cargo keeps one entry a variant.
const STORES: [&str; 4] = ["deps", "incremental", ".fingerprint", "build"];
/// How deep under a build directory a store is looked for (`cover-gate/target/debug/deps` is four down).
const DEPTH: usize = 5;

/// What the cache's sweep removes, each with why.
pub(super) fn plan(c: &Config, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    let mut out = Vec::new();
    if !std::fs::symlink_metadata(&c.cargo).is_ok_and(|m| m.is_dir()) {
        return out;
    }
    let live = trees(c);
    for (target, name, meta) in children(&c.cargo) {
        if !meta.is_dir() {
            continue;
        }
        let whole = live.as_ref().is_some_and(|l| !l.contains(&name))
            && newest(&target).is_some_and(|t| t < cutoff);
        if whole {
            out.push((
                target,
                "a build directory of no live tree, nothing built in it lately",
            ));
            continue;
        }
        let mut stores = Vec::new();
        find_stores(&target, DEPTH, &mut stores);
        for store in stores {
            out.extend(stale_variants(&store, cutoff));
        }
    }
    out
}

/// The names of the trees whose build directories are never removed whole: the mirror's and every clone's; None where the clones
/// directory cannot be read.
fn trees(c: &Config) -> Option<Vec<String>> {
    let clones = std::fs::read_dir(&c.clones).ok()?;
    let mut names: Vec<String> = clones
        .flatten()
        .filter(|e| e.file_type().is_ok_and(|t| t.is_dir()))
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    names.extend(
        c.mirror
            .file_name()
            .map(|n| n.to_string_lossy().into_owned()),
    );
    Some(names)
}

/// Every store at most `depth` below `dir`, never through a symlink and never into a store.
fn find_stores(dir: &Path, depth: usize, out: &mut Vec<PathBuf>) {
    for (path, name, meta) in children(dir) {
        if !meta.is_dir() {
            continue;
        }
        if STORES.contains(&name.as_str()) {
            out.push(path);
        } else if depth > 1 {
            find_stores(&path, depth - 1, out);
        }
    }
}

/// A store's entries beyond each crate's newest `KEPT`, idle past `cutoff`; an entry whose age cannot be read is kept.
fn stale_variants(store: &Path, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    let mut groups: BTreeMap<String, Vec<(SystemTime, PathBuf)>> = BTreeMap::new();
    for (path, name, _) in children(store) {
        if let Some(t) = newest(&path) {
            groups.entry(variant_of(&name)).or_default().push((t, path));
        }
    }
    let mut out = Vec::new();
    for mut variants in groups.into_values() {
        variants.sort_by(|a, b| b.0.cmp(&a.0));
        out.extend(
            variants
                .into_iter()
                .skip(KEPT)
                .filter(|(t, _)| *t < cutoff)
                .map(|(_, p)| (p, "an old build variant of a crate")),
        );
    }
    out
}

/// What makes entries variants of one another: the name without its trailing `-<hash>`, with its extension (`libserde-ab12.rlib`
/// -> `libserde.rlib`, `l7r_gate-0hjj` -> `l7r_gate.`).
fn variant_of(name: &str) -> String {
    let (stem, ext) = match name.rsplit_once('.') {
        Some((s, e)) if !s.is_empty() && !e.contains('-') => (s, e),
        _ => (name, ""),
    };
    let base = stem.rsplit_once('-').map_or(stem, |(b, _)| b);
    format!("{base}.{ext}")
}

#[cfg(test)]
mod tests;
