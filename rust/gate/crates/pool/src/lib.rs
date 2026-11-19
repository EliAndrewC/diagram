//! The pool walk and the pool index (feature 449 T220, the pipeline's phase, T157's second landing): rebuilt from
//! `specs/449-rust-codebase/derivations/T219-pipeline.md` (judged SOUND), never from the Python pipeline it replaces. One walk of both
//! pool trees ([`walk`]), which every consumer of the pool asks in place of listing it on its own (the derivation's Keep 7) - the review
//! tools, the probe, the model trial, the work-budget review, the review gate (through `l7r-gate pool find`), the Mode A engine's pool
//! sweep - and the index it writes ([`index`]). The generation key, the read table and the cache are T221's.
//!
//! The commands, `l7r-gate pool <command>` in the gate and `l7r-pool <command>` as this crate's own program:
//!
//! - `index`: write `pool/index.html` where it differs; what the walk could not classify is printed on stderr.
//! - `find <map> [<suffix>]`: the map's kind tag and folder; with a suffix, the folder's `<map><suffix>` where the listing holds it.
//!   Exit 1 where there is none.
//! - `list`: every map folder, `tree tier name kind`, then what was reported.
//! - `counts <tree>` (a counting build alone): the walk's and the index's counted work on that tree, one JSON line with its `total`.
//!
//! Research: plumbing - NONE: finds the pool's maps and lists them, and decides nothing about a place

use std::fmt::Write as _;
use std::path::Path;

pub mod counts;
pub mod index;
pub mod walk;

pub use walk::{walk, Kind, Map, Walk, DECLARATION, LEGACY, LIVE, TREES};

const USAGE: &str =
    "usage: pool index | find <map> [<suffix>] | list | counts <tree> (a counting build)\n";

/// What a command says: `(stdout, stderr, exit code)`.
pub type Said = (String, String, i32);

/// Each report, a line.
fn reported(w: &Walk) -> String {
    w.reports.iter().fold(String::new(), |mut out, r| {
        let _ = writeln!(out, "pool walk: {r}");
        out
    })
}

/// `index`: the page written where it differs.
fn index_cli(root: &Path) -> Said {
    let mut w = walk(root);
    let n = w.maps.len();
    match index::write(root, &mut w) {
        Ok(written) => (
            format!(
                "pool index: {} ({n} maps)\n",
                if written {
                    format!("{} written", index::INDEX)
                } else {
                    format!("{} unchanged", index::INDEX)
                }
            ),
            reported(&w),
            0,
        ),
        Err(e) => (
            String::new(),
            format!(
                "{}pool index: {} could not be written: {e} - run it from the repository's root, where pool/ is\n",
                reported(&w),
                index::INDEX
            ),
            1,
        ),
    }
}

/// `find <map> [<suffix>]`.
fn find_cli(root: &Path, name: &str, suffix: Option<&str>) -> Said {
    let w = walk(root);
    let Some(map) = w.folder(name) else {
        return (
            String::new(),
            format!("pool find: no map folder named {name} in either pool tree\n"),
            1,
        );
    };
    match suffix {
        None => (
            format!("{}\t{}\n", map.kind.tag(), map.rel()),
            String::new(),
            0,
        ),
        Some(s) if map.has(s) => (format!("{}/{name}{s}\n", map.rel()), String::new(), 0),
        Some(s) => (
            String::new(),
            format!("pool find: {} holds no {name}{s}\n", map.rel()),
            1,
        ),
    }
}

/// `list`.
fn list_cli(root: &Path) -> Said {
    let w = walk(root);
    let out = w.maps.iter().fold(String::new(), |mut out, m| {
        let _ = writeln!(out, "{}\t{}\t{}\t{}", m.tree, m.tier, m.name, m.kind.tag());
        out
    });
    (out, reported(&w), 0)
}

/// `counts <tree>`: the walk and the index's rows composed and compared (the all-hit run: nothing written), that tree's counts.
#[cfg(feature = "counters")]
fn counts_cli(root: &Path, tree: &str) -> Said {
    if !TREES.contains(&tree) {
        return (
            String::new(),
            format!("pool counts: no tree {tree} - the trees are {LIVE} and {LEGACY}\n"),
            2,
        );
    }
    let mut w = walk(root);
    let _ = index::compare(root, &mut w);
    let kinds = w.counts.of(tree);
    let total: u64 = kinds.iter().map(|(_, n)| n).sum();
    let mut line = serde_json::Map::new();
    line.insert("tree".to_owned(), tree.into());
    line.insert("total".to_owned(), total.into());
    for (k, n) in kinds {
        line.insert(k.to_owned(), n.into());
    }
    (
        format!("{}\n", serde_json::Value::Object(line)),
        String::new(),
        0,
    )
}

/// The command line, from the tree at `root`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> Said {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words[..] {
        ["index"] => index_cli(root),
        ["find", name] => find_cli(root, name, None),
        ["find", name, suffix] => find_cli(root, name, Some(suffix)),
        ["list"] => list_cli(root),
        #[cfg(feature = "counters")]
        ["counts", tree] => counts_cli(root, tree),
        _ => (String::new(), USAGE.to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
