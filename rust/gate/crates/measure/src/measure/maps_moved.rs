//! Which pool manifests differ from HEAD - the comparison a wave records (feature 429 FR-004, D170; feature 449 T77, from `maps_moved.py`).
//!
//! "Did this wave move a map?" is answered against HEAD, never against a scratch copy: feature 328 wave 68 (2026-10-09) copied the manifests
//! after a gate test had already regenerated them and recorded four hamlets unchanged while Sawada's board had moved 76 degrees.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;

use super::reply;
use crate::cohort::git;

/// Pool manifests (`pool/**/*.json`, a map's spec - `.spec.json`, `.compound.json` - not among them) whose working-tree content differs
/// from HEAD, untracked ones included; `only` one map's, named as `make map MAP=` names it (its folder, a file in it, or its name; feature
/// 449 T221, where it was the map's `.gen.py`).
pub fn moved(root: &Path, only: Option<&str>) -> Vec<String> {
    let w = l7r_gate_pool::walk(root);
    let spec = only.map_or_else(
        || "pool".to_owned(),
        |o| {
            l7r_gate_pool::map::resolve(root, &w, o)
                .map_or_else(|_| o.to_owned(), l7r_gate_pool::Map::rel)
        },
    );
    let changed = git(root, &["diff", "--name-only", "HEAD", "--", &spec]).1;
    let new = git(
        root,
        &["ls-files", "--others", "--exclude-standard", "--", &spec],
    )
    .1;
    let found: BTreeSet<&str> = changed
        .split_whitespace()
        .chain(new.split_whitespace())
        .filter(|p| {
            p.starts_with("pool/")
                && crate::checks::has_ext(p, "json")
                && !p.ends_with(".spec.json")
                && !p.ends_with(".compound.json")
        })
        .collect();
    found.into_iter().map(str::to_owned).collect()
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

/// `l7r-gate measure maps-moved [--root DIR] [--only <map: its folder, a file in it, or its name>]`.
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let only = flag(args, "--only");
    let hits = moved(flag(args, "--root").map_or(root, Path::new), only);
    let mut out = String::new();
    for path in &hits {
        let _ = writeln!(out, "moved against HEAD: {path}");
    }
    if hits.is_empty() {
        out += if only.is_some() {
            "this map's manifest is unchanged against HEAD\n"
        } else {
            "no pool manifest moved against HEAD\n"
        };
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
