//! The site written whole, and built on the main checkout only when something it is built from changed (`record/site.py`'s `write` and
//! `pipeline/record_build.py`, feature 301; ported by feature 449 T148, `ask:449-phase4-slices`).
//!
//! The GM, 2026-10-01: *"I do want these files to end up on main ... when something lands on the main, then we regenerate ... if they
//! would change, but we do not regenerate them otherwise."* So render-sync asks for the build after the map renders, on their model: a
//! STAMP of every input, written beside the site, and a build only when the stamp differs (spec FR-010). The inputs are what the build
//! reads: every file under `research/` that is not itself built and is not prose about the record, the glossary's JSON, and the build's
//! own code. The code was the engine modules the Python build imported; it is now the program that builds, hashed whole (the
//! binary-plus-inputs key `ask:449-phase4-slices` Q8 rules for the generation cache), so a stamp the Python wrote is never taken for one
//! of this build's and the first run after the port rebuilds once.

use std::path::{Path, PathBuf};

use l7r_shared::sha256;

use super::{SiteFiles, SITE};
use crate::{Error, Result};

/// Where the stamp lives: inside the site, so a site deleted by hand takes its stamp with it and is rebuilt.
pub const STAMP: &str = ".stamp";
const GLOSSARY: &str = "l7r/diagram/interactive/assets/glossary.json";

/// A file operation's result, its failure the Python's `OSError` naming the path (words no caller binds, `ask:449-usage-text`).
fn io(done: std::io::Result<()>, path: &Path) -> Result<()> {
    done.map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))
}

/// A fresh, empty directory beside the site, named `<prefix><unique>`, as `tempfile.mkdtemp` makes one: the process, the time and a
/// count within the process make the name its own.
fn fresh_dir(parent: &Path, prefix: &str) -> Result<PathBuf> {
    static MADE: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_nanos());
    let n = MADE.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let path = parent.join(format!("{prefix}{}-{stamp}-{n}", std::process::id()));
    io(std::fs::create_dir(&path), &path)?;
    Ok(path)
}

/// Write the site to `out_dir` whole: built beside it and swapped in, so a reader never meets a half-written site and a page the record
/// no longer has does not linger.
///
/// # Errors
/// A directory or file it cannot make, or a swap that fails.
pub fn write(files: &SiteFiles, out_dir: &Path) -> Result<()> {
    use std::os::unix::fs::PermissionsExt as _;
    // `os.path.abspath`: a relative path read from the working directory (`join` keeps an absolute one as it is)
    let out_dir = std::env::current_dir().unwrap_or_default().join(out_dir);
    let parent = out_dir.parent().unwrap_or(Path::new("/")).to_path_buf();
    io(std::fs::create_dir_all(&parent), &parent)?;
    let fresh = fresh_dir(&parent, ".site-")?;
    for (rel, data) in &files.files {
        let path = fresh.join(rel);
        let dir = path.parent().unwrap_or(&fresh);
        io(std::fs::create_dir_all(dir), dir)?;
        io(std::fs::write(&path, data), &path)?;
    }
    io(
        std::fs::set_permissions(&fresh, std::fs::Permissions::from_mode(0o755)),
        &fresh,
    )?;
    let old = if out_dir.exists() {
        let old = fresh_dir(&parent, ".site-old-")?;
        io(std::fs::remove_dir(&old), &old)?;
        io(std::fs::rename(&out_dir, &old), &out_dir)?;
        Some(old)
    } else {
        None
    };
    io(std::fs::rename(&fresh, &out_dir), &fresh)?;
    if let Some(old) = old {
        io(std::fs::remove_dir_all(&old), &old)?;
    }
    Ok(())
}

/// Is this file under `research/` something the build reads? Not the site, not a page, citations page or glossary script an older
/// assembly wrote (perhaps still on disk in an old checkout), not prose; since feature 303 a root `.html` is never an input.
#[must_use]
pub fn is_input(rel: &str) -> bool {
    let top = rel.split('/').next().unwrap_or("");
    if top == SITE
        || top == "citations"
        || top.starts_with(".site-")
        || rel == "assets/glossary.js"
        || crate::has_ext(rel, "md")
    {
        return false;
    }
    rel.contains('/') || !crate::has_ext(rel, "html")
}

fn walk(root: &Path, dir: &Path, out: &mut Vec<String>) {
    let Ok(read) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in read.flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        let path = entry.path();
        // `os.walk` sorts a link to a directory with the directories and does not descend it, and a link to a file with the files
        let is_link = entry.file_type().is_ok_and(|t| t.is_symlink());
        if path.is_dir() {
            if !is_link && name != SITE && name != "citations" && !name.starts_with(".site-") {
                walk(root, &path, out);
            }
            continue;
        }
        let rel = path
            .strip_prefix(root)
            .map(|p| p.to_string_lossy().into_owned())
            .unwrap_or_default();
        if is_input(&rel) {
            out.push(rel);
        }
    }
}

/// Every file under `research/` the build reads, relative to it, sorted.
#[must_use]
pub fn record_files(research_dir: &Path) -> Vec<String> {
    let mut out = Vec::new();
    walk(research_dir, research_dir, &mut out);
    out.sort();
    out
}

/// One hash over every input of the build: each file's path under the tree and its content's hash (`-` for one it cannot read), then
/// the program that builds.
#[must_use]
pub fn fingerprint(tree: &Path, code: &[u8]) -> String {
    let research = tree.join("research");
    let mut paths: Vec<String> = record_files(&research)
        .into_iter()
        .map(|r| format!("research/{r}"))
        .collect();
    paths.push(GLOSSARY.to_owned());
    let mut all = Vec::new();
    for rel in paths {
        all.extend_from_slice(rel.as_bytes());
        all.push(0);
        match std::fs::read(tree.join(&rel)) {
            Ok(bytes) => all.extend_from_slice(sha256::hex(&bytes).as_bytes()),
            Err(_) => all.push(b'-'),
        }
    }
    all.extend_from_slice(b"l7r-gate\0");
    all.extend_from_slice(sha256::hex(code).as_bytes());
    sha256::hex(&all)
}

/// The stamp the site was last built under; "" when there is none.
#[must_use]
pub fn read_stamp(site_dir: &Path) -> String {
    crate::read(&site_dir.join(STAMP))
        .map(|t| l7r_shared::py_text::strip(&t).to_owned())
        .unwrap_or_default()
}

/// Build the site when its stamp differs from its inputs; true when it built. `code` is the building program's bytes.
///
/// # Errors
/// The build's refusal, or the write's.
pub fn rebuild_if_stale(tree: &Path, code: &[u8]) -> Result<bool> {
    let research = tree.join("research");
    let out = research.join(SITE);
    let want = fingerprint(tree, code);
    if read_stamp(&out) == want {
        return Ok(false);
    }
    let mut files = super::build(&research, tree)?;
    files.set(STAMP, format!("{want}\n"));
    write(&files, &out)?;
    Ok(true)
}
