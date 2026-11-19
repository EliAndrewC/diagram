//! THE POOL WALK (feature 449 T220, rebuilt from `specs/449-rust-codebase/derivations/T219-pipeline.md`, "The algorithm", its `walk:`
//! step; the derivation's Keep 7: one walk serves every consumer, each folder classified exactly once).
//!
//! Each tree's root is listed once, each of its tiers once, each map folder once, and every entry of a map folder is matched once against
//! the kinds' file names; a folder's kind is then decided from what that matching found, by precedence:
//!
//! - a `<map>.spec.json` beside it: a HAMLET (the hamlet driver's spec);
//! - else a `<map>.compound.json`: a GENERATED COMPOUND (the compound generator's program);
//! - else a `<map>.svg` in a tier the building types declaration declares: a HAND SHEET;
//! - else, in the legacy tree, a `<map>.json`: a FROZEN EXHIBIT, listed and never keyed or regenerated (Keep 6);
//! - else nothing a map is made of: REPORTED, never guessed at.
//!
//! No file's contents are read to classify it, no path is stat-ed beyond the listings, and no git index is asked: a hand sheet's svg is
//! told by precedence (no spec, no program, a declared tier), where asking the index which svg is tracked would cost its 28,194 entries a
//! run (the derivation's `tracked_lookup`, 0). The one file read is the building types declaration, for its tiers, once a run.
//!
//! Each folder's entry names are kept with it, so a consumer asks [`Map::has`] of the listing rather than listing or stat-ing again.
//!
//! Research: plumbing - NONE: finds and sorts the pool's map folders by their file names, and decides nothing about a place

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use crate::counts::Counts;

/// The live pool: its maps are kept current by their engines.
pub const LIVE: &str = "pool";
/// The frozen exhibits (the GM, 2026-08-16): hand-authored maps awaiting conversion, never regenerated.
pub const LEGACY: &str = "legacy-hand-authored-pool";
/// Both trees, the live pool first: the order every consumer meets their maps in.
pub const TREES: [&str; 2] = [LIVE, LEGACY];
/// The building types declaration, whose objects' `tier`s are the Mode A tiers a hand sheet is drawn in.
pub const DECLARATION: &str = "l7r/diagram/buildings/types.json";

/// The derivation's block for a parse: 64 bytes.
const BLOCK: usize = 64;

/// What a map folder is, by the precedence above.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Kind {
    Hamlet,
    Compound,
    HandSheet,
    Frozen,
    Report,
}

impl Kind {
    /// A map an engine keeps current: a hamlet, a generated compound or a hand sheet.
    #[must_use]
    pub fn is_live(self) -> bool {
        matches!(self, Self::Hamlet | Self::Compound | Self::HandSheet)
    }

    /// A Mode A sheet: a generated compound or a hand sheet.
    #[must_use]
    pub fn is_sheet(self) -> bool {
        matches!(self, Self::Compound | Self::HandSheet)
    }

    /// The kind's one-word tag, as `l7r-gate pool find` and `list` print it.
    #[must_use]
    pub fn tag(self) -> &'static str {
        match self {
            Self::Hamlet => "hamlet",
            Self::Compound => "compound",
            Self::HandSheet => "hand-sheet",
            Self::Frozen => "frozen",
            Self::Report => "unclassified",
        }
    }

    /// The kind as the index names it.
    #[must_use]
    pub fn label(self) -> &'static str {
        match self {
            Self::Hamlet => "hamlet",
            Self::Compound => "generated compound",
            Self::HandSheet => "hand sheet",
            Self::Frozen => "frozen exhibit",
            Self::Report => "unclassified",
        }
    }
}

/// One map folder, `<tree>/<tier>/<name>/`, with its entries' names (sorted) and its kind.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Map {
    pub tree: &'static str,
    pub tier: String,
    pub name: String,
    pub dir: PathBuf,
    pub files: Vec<String>,
    pub kind: Kind,
}

impl Map {
    /// The folder's file `<name><suffix>` (`.svg`, `.notes.md`, ...), whether or not it is there.
    #[must_use]
    pub fn file(&self, suffix: &str) -> PathBuf {
        self.dir.join(format!("{}{suffix}", self.name))
    }

    /// Whether the folder's listing holds `<name><suffix>`: asked of the walk's listing, with no stat.
    #[must_use]
    pub fn has(&self, suffix: &str) -> bool {
        self.files
            .binary_search(&format!("{}{suffix}", self.name))
            .is_ok()
    }

    /// The folder from the tree's root: `<tree>/<tier>/<name>`.
    #[must_use]
    pub fn rel(&self) -> String {
        format!("{}/{}/{}", self.tree, self.tier, self.name)
    }
}

/// A directory under a tree that is there but could not be listed (a permission refused): reported, and kept with its error's kind so a
/// consumer that must refuse rather than read a partial pool can.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Unlisted {
    pub dir: PathBuf,
    pub kind: std::io::ErrorKind,
    /// The system's error number, 0 where the error carried none.
    pub code: i32,
    pub message: String,
}

/// One walk of both trees: every map folder in the trees' order (the live pool first, then by tier and name), the declared tiers, what
/// was reported (the unlisted directories among it), and the counted work.
#[derive(Clone, Debug, Default)]
pub struct Walk {
    pub maps: Vec<Map>,
    pub tiers: BTreeSet<String>,
    pub reports: Vec<String>,
    pub unlisted: Vec<Unlisted>,
    pub counts: Counts,
}

impl Walk {
    /// The first folder named `name` in the walk's order, of any kind: where a consumer finds a map or sheet by its name.
    #[must_use]
    pub fn folder(&self, name: &str) -> Option<&Map> {
        self.maps.iter().find(|m| m.name == name)
    }

    /// The folders of `tree`, in the walk's order.
    pub fn in_tree<'a>(&'a self, tree: &'a str) -> impl Iterator<Item = &'a Map> + 'a {
        self.maps.iter().filter(move |m| m.tree == tree)
    }
}

/// A directory's entries, `(name, is a directory)`, sorted; one listing counted, and each name read from it. A directory that is not
/// there has none and counts nothing; one there that cannot be listed has none too, and is reported.
fn list(w: &mut Walk, dir: &Path, tree: &'static str) -> Vec<(String, bool)> {
    let read = match std::fs::read_dir(dir) {
        Ok(read) => read,
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                w.reports.push(format!(
                    "{}: could not be listed ({e}) - its maps are left out of this walk",
                    dir.display()
                ));
                w.unlisted.push(Unlisted {
                    dir: dir.to_path_buf(),
                    kind: e.kind(),
                    code: e.raw_os_error().unwrap_or(0),
                    message: e.to_string(),
                });
            }
            return Vec::new();
        }
    };
    let counts = &mut w.counts;
    counts.add(tree, "dir_list", 1);
    let mut out: Vec<(String, bool)> = read
        .flatten()
        .map(|e| {
            let dir = e
                .file_type()
                .is_ok_and(|t| t.is_dir() || (t.is_symlink() && e.path().is_dir()));
            (e.file_name().to_string_lossy().into_owned(), dir)
        })
        .collect();
    counts.add(tree, "dir_entry", out.len());
    out.sort();
    out
}

/// The tiers the building types declaration declares: its file read once and parsed (counted in 64-byte blocks), charged to the live
/// pool. A declaration that is missing or does not read declares none, and is reported: no svg is then a hand sheet.
fn declared(root: &Path, counts: &mut Counts, reports: &mut Vec<String>) -> BTreeSet<String> {
    let Ok(text) = std::fs::read_to_string(root.join(DECLARATION)) else {
        reports.push(format!(
            "{DECLARATION}: not readable - no Mode A tier is declared, so no svg is told a hand sheet"
        ));
        return BTreeSet::new();
    };
    counts.add(LIVE, "file_read", 1);
    counts.add(LIVE, "parse_block", text.len().div_ceil(BLOCK));
    let Ok(serde_json::Value::Array(types)) = serde_json::from_str(&text) else {
        reports.push(format!(
            "{DECLARATION}: not a JSON list of building types - no Mode A tier is declared, so no svg is told a hand sheet"
        ));
        return BTreeSet::new();
    };
    types
        .iter()
        .filter_map(|t| t.get("tier").and_then(serde_json::Value::as_str))
        .map(str::to_owned)
        .collect()
}

/// What a map folder's entries showed: each kind's file present.
#[derive(Default)]
#[expect(
    clippy::struct_excessive_bools,
    reason = "the four kinds' files a folder's listing showed, each there or not; the precedence reads them by name"
)]
struct Found {
    spec: bool,
    compound: bool,
    svg: bool,
    json: bool,
}

/// The folder's entries matched once each against the kinds' file names.
fn found(name: &str, files: &[String], counts: &mut Counts, tree: &'static str) -> Found {
    let mut f = Found::default();
    for file in files {
        counts.add(tree, "classify", 1);
        match file.strip_prefix(name) {
            Some(".spec.json") => f.spec = true,
            Some(".compound.json") => f.compound = true,
            Some(".svg") => f.svg = true,
            Some(".json") => f.json = true,
            _ => {}
        }
    }
    f
}

/// The folder's kind by the precedence of the module's head.
fn kind_of(f: &Found, declared_tier: bool, tree: &str) -> Kind {
    if f.spec {
        Kind::Hamlet
    } else if f.compound {
        Kind::Compound
    } else if f.svg && declared_tier {
        Kind::HandSheet
    } else if tree == LEGACY && f.json {
        Kind::Frozen
    } else {
        Kind::Report
    }
}

/// Walk both trees under `root` (the derivation's `walk:` step): each map folder listed once and classified once.
#[must_use]
pub fn walk(root: &Path) -> Walk {
    let mut w = Walk::default();
    let tiers = declared(root, &mut w.counts, &mut w.reports);
    for tree in TREES {
        let base = root.join(tree);
        for (tier, _) in list(&mut w, &base, tree).into_iter().filter(|(_, d)| *d) {
            w.counts.add(tree, "tier_lookup", 1);
            let declared_tier = tiers.contains(&tier);
            let tier_dir = base.join(&tier);
            for (name, _) in list(&mut w, &tier_dir, tree)
                .into_iter()
                .filter(|(_, d)| *d)
            {
                let dir = tier_dir.join(&name);
                let files: Vec<String> = list(&mut w, &dir, tree)
                    .into_iter()
                    .map(|(f, _)| f)
                    .collect();
                let f = found(&name, &files, &mut w.counts, tree);
                w.counts.add(tree, "folder_kind", 1);
                let kind = kind_of(&f, declared_tier, tree);
                let map = Map {
                    tree,
                    tier: tier.clone(),
                    name,
                    dir,
                    files,
                    kind,
                };
                if kind == Kind::Report {
                    w.reports.push(format!(
                        "{}: no {n}.spec.json (a hamlet), {n}.compound.json (a generated compound), {n}.svg in a declared tier (a hand sheet{}) or, in the legacy tree, {n}.json (a frozen exhibit) - give it one, or move it out of the pool",
                        map.rel(),
                        if declared_tier { "" } else { "; this tier is not declared" },
                        n = map.name,
                    ));
                }
                w.maps.push(map);
            }
        }
    }
    Walk { tiers, ..w }
}

#[cfg(test)]
pub(crate) mod tests;
