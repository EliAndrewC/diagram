//! The checks of the documents and the agent files: six Python tests ported to Rust tests in one cut by feature 449 T133, the round
//! arbiter's ruling `ask:449-phase3-remainder` Q3. FR-001b kept them through the Python tests' deletion because their subject - the
//! agent files, the CLAUDE.md files and the other documents - outlives the Python, and no Python piece's port gives them a date, so the
//! ruling ports them now. They live in the `checks` crate, the repository's text checks, whose tests already read the real tree and
//! declare the whole of it (`reads = ["."]`), so `make rust-test` runs them again whenever a file they read changes.
//!
//! Each check is a function that returns its problems, each one naming its fix, and each real-tree test asserts the list is empty, so a
//! failure prints every problem with its fix; a self-test seeds each defect so every message is proven to fire.

mod agent_models;
mod agent_waves;
mod citation_inventory;
mod claude_md_quotes;
mod docs_mechanism;
mod one_root_claude_md;
mod settlement_review_contract;

use std::path::{Path, PathBuf};

use fancy_regex::Regex;

/// The repository the tests check. Read from the environment at run time, which `cargo test` and the coverage run both set, rather
/// than baked in by `env!`: T133's proof of sameness ran the built test binary over a scratch copy of the tree by pointing it there.
fn root() -> PathBuf {
    PathBuf::from(std::env::var_os("CARGO_MANIFEST_DIR").unwrap()).join("../../../..")
}

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap()
}

/// A file as Python's `read_text` reads it (`\r\n` and `\r` read as `\n`), or "" where it cannot be read: a missing file fails the
/// check that asked for its words, as the Python's raise did.
fn read(path: &Path) -> String {
    l7r_guard::shared::speckit::read_text(path).unwrap_or_default()
}

/// `path` relative to `root`, as the Python's `relative_to` printed it.
fn rel(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

/// The files directly in `dir` whose names end in `suffix` (`dir.glob("*<suffix>")`), sorted; `""` takes every file.
fn files_in(dir: &Path, suffix: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.is_file() && p.to_string_lossy().ends_with(suffix))
        .collect();
    out.sort();
    out
}

/// Every directory under `dir`, itself first (what `**` walks): a symlinked directory is not entered, as Python 3.13's `glob` does not.
fn dirs_under(dir: &Path) -> Vec<PathBuf> {
    let mut out = vec![dir.to_path_buf()];
    let mut at = 0;
    while let Some(next) = out.get(at).cloned() {
        at += 1;
        let mut found: Vec<PathBuf> = std::fs::read_dir(&next)
            .into_iter()
            .flatten()
            .flatten()
            .filter(|e| e.file_type().is_ok_and(|t| t.is_dir()))
            .map(|e| e.path())
            .collect();
        found.sort();
        out.extend(found);
    }
    out
}

/// `dir.glob("**/*<suffix>")`: every file at any depth under `dir` whose name ends in `suffix`, sorted.
fn files_under(dir: &Path, suffix: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = dirs_under(dir)
        .iter()
        .flat_map(|d| files_in(d, suffix))
        .collect();
    out.sort();
    out
}

#[test]
fn the_walks_find_files_at_every_depth_and_skip_a_linked_directory() {
    let dir = crate::checks::scratch("documents-walk");
    crate::checks::tests::put(&dir, "a.sh", "");
    crate::checks::tests::put(&dir, "x/b.sh", "");
    crate::checks::tests::put(&dir, "x/c.py", "");
    std::os::unix::fs::symlink(dir.join("x"), dir.join("linked")).unwrap();
    let found: Vec<String> = files_under(&dir, ".sh")
        .iter()
        .map(|p| rel(p, &dir))
        .collect();
    assert_eq!(found, ["a.sh", "x/b.sh"]);
    assert_eq!(rel(Path::new("/elsewhere/f"), &dir), "/elsewhere/f");
    assert_eq!(read(&dir.join("absent")), "");
}
