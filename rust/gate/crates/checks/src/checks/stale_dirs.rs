//! No directory of an importable tree left holding only `__pycache__` (features 184, 449 T065, from `check-stale-dirs.py`): it would be an importable PEP 420 namespace package, so a long-lived clone behaves differently from a
//! fresh one, in the direction that hides the bug. One whose caches hold only `.pyc` files is removed; anything else is left for a person (the GM, 2026-10-19). A run is recorded by `usage_log` under `USAGE_LOG_TOOL`.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use super::Outcome;

pub(super) const USAGE_LOG_TOOL: &str = "check-stale-dirs";
const IMPORTABLE: [&str; 2] = ["l7r", "tests"];
const SKIP: [&str; 5] = [".git", ".clones", "node_modules", ".venv", "venv"];
const CACHE: &str = "__pycache__";

fn scan(dir: &Path, found: &mut Vec<PathBuf>) {
    let mut subs: Vec<(String, PathBuf)> = Vec::new();
    let mut any_file = false;
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        // os.walk's split: a link to a directory counts as a directory and is not descended
        let is_dir = entry.path().is_dir();
        if !is_dir {
            any_file = true;
        } else if !SKIP.contains(&name.as_str()) {
            subs.push((name, entry.path()));
        }
    }
    subs.sort();
    if !any_file && !subs.is_empty() && subs.iter().all(|(n, _)| n == CACHE) {
        found.push(dir.to_path_buf());
    }
    for (name, path) in subs {
        if name != CACHE && !path.is_symlink() {
            scan(&path, found);
        }
    }
}

fn stale_dirs(root: &Path) -> Vec<PathBuf> {
    let mut found = Vec::new();
    for tree in IMPORTABLE {
        scan(&root.join(tree), &mut found);
    }
    found
}

fn only_bytecode(dir: &Path) -> bool {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .all(|c| {
            c.path().is_dir()
                && c.file_name() == CACHE
                && std::fs::read_dir(c.path())
                    .into_iter()
                    .flatten()
                    .flatten()
                    .all(|f| f.path().is_file() && f.path().extension().is_some_and(|e| e == "pyc"))
        })
}

fn relative(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}

fn report(left: &[PathBuf], root: &Path) -> String {
    let mut out = "\nSTALE DIRECTORIES: nothing left in these but __pycache__.\n\n".to_owned();
    for p in left {
        let _ = writeln!(out, "    {}", relative(p, root));
    }
    out += "\nEach one has no source and no __init__.py, and is therefore still an importable PEP 420\nNAMESPACE PACKAGE - `import` against it SUCCEEDS and resolves to an empty module. So this\nclone behaves differently from a fresh one, and it is the local run that passes, which is\nthe direction that hides the bug (the hazard feature 175 paid a remote build to discover).\n\nThey are almost always what is left after a package's files were deleted from git, but each\nholds something besides `.pyc` bytecode, so it is not removed for you. Check each is what you\nthink it is, then:\n\n";
    for p in left {
        let _ = writeln!(out, "    rm -rf {}", relative(p, root));
    }
    out += "\n(l7r-gate check stale-dirs: these hold more than bytecode, so they are left for a person)\n\n";
    out
}

fn check(root: &Path) -> Outcome {
    let (mut out, mut left) = (String::new(), Vec::new());
    for p in stale_dirs(root) {
        if only_bytecode(&p) && std::fs::remove_dir_all(&p).is_ok() {
            let _ = writeln!(out, "check-stale-dirs: removed {} (nothing in it but .pyc bytecode; an importable namespace package otherwise)", relative(&p, root));
        } else {
            left.push(p);
        }
    }
    if left.is_empty() {
        return Outcome::out(out);
    }
    out += &report(&left, root);
    Outcome {
        stdout: out,
        stderr: String::new(),
        code: 1,
    }
}

/// Plant a stale directory and prove the scan fires on it, and that a package with source, a data directory and a tree outside the importable ones all pass.
fn selftest() -> Outcome {
    let root = super::scratch("stale-dirs");
    let mk = |rel: &str| {
        let _ = std::fs::create_dir_all(root.join(rel));
    };
    let put = |rel: &str| {
        let _ = std::fs::write(root.join(rel), "x");
    };
    mk("l7r/diagram/gone/__pycache__");
    put("l7r/diagram/gone/__pycache__/mod.cpython-314.pyc");
    mk("l7r/diagram/alive/__pycache__");
    put("l7r/diagram/alive/mod.py");
    mk("tests/data");
    put("tests/data/fixture.json");
    mk("pool/leftover/__pycache__");
    let got: Vec<String> = stale_dirs(&root)
        .iter()
        .map(|p| relative(p, &root))
        .collect();
    let _ = std::fs::remove_dir_all(&root);
    Outcome::selftest(
        got == ["l7r/diagram/gone"],
        "check-stale-dirs: selftest ok (stale fires; a real package, a data dir and a non-importable tree all pass)\n",
        format!("check-stale-dirs: SELFTEST FAILED - expected exactly the stale dir, got {got:?}\n"),
    )
}

/// `l7r-gate check stale-dirs [ROOT] | --selftest`.
pub(super) fn cli(args: &[String]) -> Outcome {
    match args.first().map(String::as_str) {
        Some("--selftest") => selftest(),
        other => check(Path::new(other.unwrap_or("."))),
    }
}

#[cfg(test)]
mod tests;
