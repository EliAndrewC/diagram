//! Which pool manifests differ from HEAD - the comparison a wave records (feature 429 FR-004, D170; feature 449 T77, from `maps_moved.py`).
//!
//! "Did this wave move a map?" is answered against HEAD, never against a scratch copy: feature 328 wave 68 (2026-10-09) copied the manifests
//! after a gate test had already regenerated them and recorded four hamlets unchanged while Sawada's board had moved 76 degrees.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;

use super::reply;
use crate::cohort::git;

/// Pool manifests (`pool/**/*.json`) whose working-tree content differs from HEAD, untracked ones included.
pub fn moved(root: &Path, only: Option<&str>) -> Vec<String> {
    let spec = only.map_or_else(
        || "pool".to_owned(),
        |o| {
            o.strip_suffix(".gen.py")
                .map_or_else(|| o.to_owned(), |stem| format!("{stem}.json"))
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
        .filter(|p| p.starts_with("pool/") && crate::checks::has_ext(p, "json"))
        .collect();
    found.into_iter().map(str::to_owned).collect()
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

/// `l7r-gate measure maps-moved [--root DIR] [--only <gen or manifest path>]`.
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
