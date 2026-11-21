//! No crate builds on the guard (feature 451 T66). T58 moved what the gate's crates, the Mode A engine, the browser and the embedder read
//! of the guard into `l7r_shared` (`rust/guard/shared`), so a hook edit rebuilds the guard alone: 1 crate where it rebuilt 32 (measured
//! 2026-11-21, T58's `measure.sh`). A crate that named `l7r_guard` again would put the 32 back and fail nothing else, so every `Cargo.toml`
//! under `rust/` that names it in a dependency table - `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, a target's or the
//! workspace's, a `[*dependencies.l7r_guard]` table or a rename through `package` - is refused, naming `l7r_shared` and its path from that
//! crate. The guard's own manifest alone is exempt: no other crate ships or tests the guard binary through a dependency (`l7r-guard.sh` and
//! `hookbench` build it with `-p l7r_guard`; no manifest under `rust/` but the guard's named it, measured 2026-11-21, `cargo tree -i
//! l7r_guard --workspace -e normal,dev,build`). The manifests are walked, not listed by git, because the workspace's `gate/crates/*` builds an
//! untracked crate too. A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::Outcome;

/// The name its runs are recorded under in the `usage_log`.
pub(super) const USAGE_LOG_TOOL: &str = "check-guard-deps";
/// The guard's package, which no crate but its own may name.
const GUARD: &str = "l7r_guard";
/// The guard's own manifest, the one exempt (its tests may name it, as a crate may take itself as a dev-dependency).
const OWN: &str = "rust/guard/Cargo.toml";

/// A rename onto the guard: `x = { package = "l7r_guard", ... }`, `x.package = ...`, or `package = ...` in `[dependencies.x]`.
static RENAMED: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r#"\bpackage\s*=\s*["']l7r[_-]guard["']"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Where a manifest's line stands: a dependency table, one dependency's own table (its name), or anything else.
#[derive(Debug, PartialEq, Eq)]
enum Section {
    Table,
    One(String),
    Other,
}

/// Every `Cargo.toml` under `dir`, in order; a `target` or hidden directory and a symbolic link are not walked.
fn manifests(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    let mut found: Vec<(PathBuf, bool)> = entries
        .map_while(Result::ok)
        .map(|e| (e.path(), e.file_type().is_ok_and(|t| t.is_dir())))
        .collect();
    found.sort();
    for (path, is_dir) in found {
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or_default();
        if is_dir && name != "target" && !name.starts_with('.') {
            manifests(&path, out);
        } else if !is_dir && name == "Cargo.toml" {
            out.push(path);
        }
    }
}

/// `line` with its comment cut: from the first `#` outside a string.
fn uncommented(line: &str) -> &str {
    let mut quote = None;
    for (at, c) in line.char_indices() {
        match (quote, c) {
            (None, '#') => return &line[..at],
            (None, '"' | '\'') => quote = Some(c),
            (Some(q), _) if q == c => quote = None,
            _ => {}
        }
    }
    line
}

/// A dotted key's parts, a dot inside quotes kept (`target.'cfg(x = "a.b")'.dependencies`), each unquoted.
fn dotted(key: &str) -> Vec<String> {
    let (mut parts, mut part, mut quote) = (Vec::new(), String::new(), None);
    for c in key.chars() {
        match (quote, c) {
            (None, '.') => parts.push(std::mem::take(&mut part)),
            (None, '"' | '\'') => quote = Some(c),
            (Some(q), _) if q == c => quote = None,
            _ => part.push(c),
        }
    }
    parts.push(part);
    parts.into_iter().map(|p| p.trim().to_owned()).collect()
}

/// Is this a name for the guard's package? Cargo's `-` and `_` read alike.
fn is_guard(name: &str) -> bool {
    name.replace('-', "_") == GUARD
}

/// The section a `[header]` or `[[header]]` opens.
fn section(header: &str) -> Section {
    let parts = dotted(header.trim_matches(|c| c == '[' || c == ']'));
    match parts.iter().position(|p| p.ends_with("dependencies")) {
        Some(at) if at + 1 == parts.len() => Section::Table,
        Some(at) => Section::One(parts[at + 1].clone()),
        None => Section::Other,
    }
}

/// The 1-based lines of `text` that make its crate depend on the guard.
fn guard_lines(text: &str) -> Vec<usize> {
    let mut now = Section::Other;
    let mut out = Vec::new();
    for (at, raw) in text.lines().enumerate() {
        let line = uncommented(raw).trim();
        let names = if line.starts_with('[') {
            now = section(line);
            matches!(&now, Section::One(name) if is_guard(name))
        } else {
            match &now {
                Section::Table => {
                    let key = line.split_once('=').map_or("", |(k, _)| k);
                    is_guard(&dotted(key)[0]) || RENAMED.is_match(line).unwrap_or(false)
                }
                Section::One(_) => RENAMED.is_match(line).unwrap_or(false),
                Section::Other => false,
            }
        };
        if names {
            out.push(at + 1);
        }
    }
    out
}

/// `l7r_shared`'s path from the crate whose manifest is `rel` (relative to the tree), as its manifest would name it.
fn shared_path(rel: &Path) -> String {
    let depth = rel.components().count().saturating_sub(2);
    format!("{}guard/shared", "../".repeat(depth))
}

/// Each manifest line under `root/rust` that names the guard, as `<path>:<line>` with the path relative to `root`.
fn problems(root: &Path) -> (usize, Vec<(String, usize, String)>) {
    let mut found = Vec::new();
    manifests(&root.join("rust"), &mut found);
    let mut out = Vec::new();
    for manifest in &found {
        let rel = manifest.strip_prefix(root).unwrap_or(manifest);
        let shown = rel.display().to_string();
        if shown == OWN {
            continue;
        }
        let text = std::fs::read_to_string(manifest).unwrap_or_default();
        for line in guard_lines(&text) {
            out.push((shown.clone(), line, shared_path(rel)));
        }
    }
    (found.len(), out)
}

/// `l7r-gate check guard-deps [--root ROOT]`.
pub(super) fn cli(args: &[String], root: &Path) -> Outcome {
    let root = args
        .iter()
        .position(|a| a == "--root")
        .and_then(|at| args.get(at + 1))
        .map_or(root, |r| Path::new(r));
    let (read, bad) = problems(root);
    if bad.is_empty() {
        return Outcome::out(format!(
            "guard-deps: no crate under rust/ depends on {GUARD} but the guard itself ({read} manifests read)\n"
        ));
    }
    let mut err = String::new();
    for (path, line, shared) in &bad {
        let _ = writeln!(err, "guard-deps: {path}:{line}: names {GUARD} as a dependency - take `l7r_shared = {{ path = \"{shared}\" }}` instead");
    }
    let _ = writeln!(err, "guard-deps: what a crate reads of the guard is l7r_shared's (rust/guard/shared; the guard re-exports it as `shared`), so a hook edit rebuilds the guard alone, 1 crate where a dependent put back 32 (feature 451 T58); a piece only the guard holds moves into rust/guard/shared, as T58 moved the five guards the gate calls");
    Outcome::refuse(err)
}

#[cfg(test)]
mod tests;
