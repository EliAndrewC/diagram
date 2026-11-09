//! The delta (feature 449 T063 slice 2, from `l7r/diagram/ci/delta.py`): what this clone's own commits changed since the merge base with main, whether any of it is engine code, and the engine key a
//! green run vouches for. `is_engine` is THE ONE LIST of paths whose change requires the gate; it governs dispatch and never narrows what `stamp` hashes. The GM's rulings on each entry (2026-08-25,
//! 2026-09-05, feature 132 FR-024 and FR-025) are in the git history of `delta.py` and in `l7r/diagram/ci/CLAUDE.md`. Everything here runs in the repository the command was started in.

use std::fmt::Write as _;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};

use l7r_guard::shared::sha256;
use serde_json::json;

use crate::codeid::{self, stated, Cache};

/// (directory, accepted endings). `tests/` is deliberately absent (GM 2026-08-25, feature 132 FR-024); the frozen tree stays so the merge route is what it was before feature 161 moved the hand-authored maps.
const ENGINE_DIRS: [(&str, &[&str]); 4] = [
    ("l7r/", &[".py"]),
    ("rust/", &[".rs", "Cargo.toml", "Cargo.lock"]),
    ("pool/", &[".gen.py", ".json"]),
    ("legacy-hand-authored-pool/", &[".gen.py", ".json"]),
];

/// The gate's own decider is tooling, not engine (feature 132 FR-025, the GM: "the engine itself isn't using it ... which makes it test code").
const NOT_ENGINE_DIR: &str = "l7r/diagram/ci/";

/// The files keyed on what runs rather than their bytes.
const SEMANTIC: [&str; 2] = [".py", ".rs"];

fn semantic(path: &str) -> bool {
    SEMANTIC.iter().any(|s| path.ends_with(s))
}

/// A file Python runs, by its last extension (`.gen.py` too).
fn is_python(path: &str) -> bool {
    Path::new(path).extension().is_some_and(|e| e == "py")
}

/// Is this repository-relative path engine code, the kind that owes the gate?
#[must_use]
pub fn is_engine(path: &str) -> bool {
    if path.ends_with(".notes.md") || path.starts_with(NOT_ENGINE_DIR) {
        return false;
    }
    ENGINE_DIRS
        .iter()
        .find(|(prefix, _)| path.starts_with(prefix))
        .is_some_and(|(_, ends)| ends.iter().any(|e| path.ends_with(e)))
}

fn git(root: &Path, args: &[&str]) -> Result<String, String> {
    let done = stated(
        Command::new("git").arg("-C").arg(root).args(args).output(),
        "cannot start git",
    )?;
    if done.status.success() {
        Ok(String::from_utf8_lossy(&done.stdout).into_owned())
    } else {
        Err(format!(
            "git {} failed: {}",
            args.join(" "),
            String::from_utf8_lossy(&done.stderr).trim()
        ))
    }
}

/// Feeds `input` to `git <args>` from another thread, so a full pipe cannot deadlock the two.
fn git_fed(root: &Path, args: &[&str], input: String) -> Result<Vec<u8>, String> {
    let mut child = stated(
        Command::new("git")
            .arg("-C")
            .arg(root)
            .args(args)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn(),
        "cannot start git",
    )?;
    let mut pipe = child.stdin.take().ok_or("git took no input")?;
    let feeder = std::thread::spawn(move || pipe.write_all(input.as_bytes()));
    let done = stated(child.wait_with_output(), "git")?;
    let _ = feeder.join();
    if done.status.success() {
        Ok(done.stdout)
    } else {
        Err(format!("git {} failed", args.join(" ")))
    }
}

/// Each object named, by `git cat-file --batch`; None for one git cannot find (a file added or deleted between the two sides).
fn cat_blobs(root: &Path, names: &[String]) -> Result<Vec<Option<Vec<u8>>>, String> {
    if names.is_empty() {
        return Ok(Vec::new());
    }
    let input: String = names
        .iter()
        .flat_map(|n| {
            [
                n.as_str(),
                "
",
            ]
        })
        .collect();
    let out = git_fed(root, &["cat-file", "--batch"], input)?;
    let mut got = Vec::with_capacity(names.len());
    let mut at = 0;
    for _ in names {
        let end = out[at..]
            .iter()
            .position(|b| *b == b'\n')
            .map(|n| at + n)
            .ok_or("git cat-file answered short")?;
        let head = String::from_utf8_lossy(&out[at..end]).into_owned();
        at = end + 1;
        let Some(size) = head
            .rsplit(' ')
            .next()
            .filter(|_| !head.ends_with(" missing"))
            .and_then(|s| s.parse::<usize>().ok())
        else {
            got.push(None);
            continue;
        };
        let body = out
            .get(at..at + size)
            .ok_or("git cat-file cut a blob short")?;
        got.push(Some(body.to_vec()));
        at += size + 1;
    }
    Ok(got)
}

/// Where `codeid.py` is read from a blob: a Python id is Python's to say and it reads a file, so a blob no working file holds is put in a scratch directory for the one call.
struct Scratch(PathBuf);

impl Scratch {
    fn new() -> Result<Self, String> {
        static SEQ: AtomicUsize = AtomicUsize::new(0);
        let dir = std::env::temp_dir().join(format!(
            "l7r-gate-blobs-{}-{}",
            std::process::id(),
            SEQ.fetch_add(1, Ordering::Relaxed)
        ));
        stated(std::fs::create_dir_all(&dir), "the scratch directory")?;
        Ok(Self(dir))
    }

    fn holding(
        &self,
        at: usize,
        repo_path: &str,
        data: Vec<u8>,
    ) -> Result<(PathBuf, Vec<u8>), String> {
        let kind = if is_python(repo_path) { "py" } else { "rs" };
        let path = self.0.join(format!("{at}.{kind}"));
        if kind == "py" {
            stated(std::fs::write(&path, &data), "a scratch file")?;
        }
        Ok((path, data))
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn merge_base(root: &Path, base_ref: &str) -> Result<String, String> {
    Ok(git(root, &["merge-base", base_ref, "HEAD"])?
        .trim()
        .to_owned())
}

/// Of `candidates`, what changed in what a gate EXECUTES between `base` and HEAD: a comment-only, docstring-only or formatting edit answers no (GM 2026-08-28), and a non-`.py` file or one added or removed
/// on either side stays changed, git having said it differs and there being no semantic form to compare.
fn semantically_changed(
    root: &Path,
    base: &str,
    candidates: &[&str],
    python: &str,
) -> Result<Vec<bool>, String> {
    let code: Vec<&str> = candidates
        .iter()
        .copied()
        .filter(|p| is_python(p))
        .collect();
    let names: Vec<String> = code
        .iter()
        .flat_map(|p| [format!("{base}:{p}"), format!("HEAD:{p}")])
        .collect();
    let mut blobs = cat_blobs(root, &names)?.into_iter();
    let scratch = Scratch::new()?;
    let mut files = Vec::new();
    let mut both_sides = Vec::with_capacity(code.len());
    for (at, path) in code.iter().enumerate() {
        match (blobs.next().flatten(), blobs.next().flatten()) {
            (Some(before), Some(after)) => {
                files.push(scratch.holding(2 * at, path, before)?);
                files.push(scratch.holding(2 * at + 1, path, after)?);
                both_sides.push(true);
            }
            _ => both_sides.push(false),
        }
    }
    let ids = codeid::content_ids(&files, &mut Cache::at(root), python, &codeid::script(root))?;
    let mut pairs = ids.chunks_exact(2);
    let mut sides = both_sides.into_iter();
    Ok(candidates
        .iter()
        .map(|p| {
            !is_python(p)
                || !sides.next().unwrap_or(false)
                || pairs.next().is_none_or(|pair| pair[0] != pair[1])
        })
        .collect())
}

/// `{base, files, engine}` of what our own commits changed since we diverged from `base_ref`.
fn compute(root: &Path, base_ref: &str, python: &str) -> Result<String, String> {
    let base = merge_base(root, base_ref)?;
    let listed = git(root, &["diff", "--name-only", &base, "HEAD"])?;
    let mut files: Vec<&str> = listed.lines().filter(|f| !f.trim().is_empty()).collect();
    files.sort_unstable();
    let candidates: Vec<&str> = files.iter().copied().filter(|f| is_engine(f)).collect();
    let moved = semantically_changed(root, &base, &candidates, python)?;
    let engine: Vec<&str> = candidates
        .into_iter()
        .zip(moved)
        .filter_map(|(f, m)| m.then_some(f))
        .collect();
    Ok(format!(
        "{}\n",
        json!({"base": base, "files": files, "engine": engine})
    ))
}

/// Coverage follows the diff at reference scope (feature 135): the package directories of the engine modules changed since the merge base or in the working tree, a directory so that coverage matches by
/// path and imports nothing. A repository with no `origin/main` has nothing committed to compare.
fn coverage_scope(root: &Path, base_ref: &str) -> Result<Vec<String>, String> {
    let committed = merge_base(root, base_ref)
        .and_then(|base| git(root, &["diff", "--name-only", &base, "HEAD"]))
        .unwrap_or_default();
    let worktree = git(root, &["diff", "--name-only", "HEAD"])?;
    let untracked = git(root, &["ls-files", "--others", "--exclude-standard"])?;
    let mut mods: Vec<String> = [committed, worktree, untracked]
        .iter()
        .flat_map(|text| text.lines())
        .map(str::trim)
        .filter(|f| f.starts_with("l7r/") && is_python(f) && !f.contains("/tests/"))
        .map(|f| f.rsplit_once('/').map_or("", |(dir, _)| dir).to_owned())
        .collect();
    mods.sort();
    mods.dedup();
    Ok(mods)
}

/// The pytest words that trace only those packages; nothing changed is no tracing at all.
fn pytest_words(mods: &[String]) -> String {
    match mods.split_first() {
        None => "-o addopts= --no-cov\n".to_owned(),
        Some((first, rest)) => {
            let more: String = rest.iter().flat_map(|m| [" --cov=", m.as_str()]).collect();
            format!("-o addopts=--cov={first}{more}\n")
        }
    }
}

/// The key from (git blob id, path) pairs: a semantic file by the id kept for that blob, its content read only on a miss, any other by the blob id; rows sorted and hashed as the Python hashed them.
fn key_from_ids(
    root: &Path,
    entries: &[(String, String)],
    python: &str,
    fetch: impl FnOnce(&[usize]) -> Result<Vec<Vec<u8>>, String>,
) -> Result<String, String> {
    let mut cache = Cache::at(root);
    let misses: Vec<usize> = (0..entries.len())
        .filter(|&i| semantic(&entries[i].1) && cache.kept(&entries[i].0).is_none())
        .collect();
    let contents = fetch(&misses)?;
    let scratch = Scratch::new()?;
    let files: Vec<(PathBuf, Vec<u8>)> = misses
        .iter()
        .zip(contents)
        .map(|(&i, data)| scratch.holding(i, &entries[i].1, data))
        .collect::<Result<_, _>>()?;
    let ids = codeid::content_ids(&files, &mut cache, python, &codeid::script(root))?;
    let mut found = misses.iter().copied().zip(ids);
    let mut next = found.next();
    let mut rows = Vec::with_capacity(entries.len());
    for (at, (sha, path)) in entries.iter().enumerate() {
        let id = if !semantic(path) {
            sha.clone()
        } else if next.as_ref().is_some_and(|(i, _)| *i == at) {
            let id = next.take().map_or_else(String::new, |(_, id)| id);
            next = found.next();
            id
        } else {
            cache.kept(sha).unwrap_or_default().to_owned()
        };
        rows.push(format!("{id} {path}"));
    }
    rows.sort_unstable();
    Ok(sha256::hex(rows.join("\n").as_bytes()))
}

/// The engine key of a tree or commit: a hash over the engine paths' content ids, with no checkout, the build computing it the same way on its merge. Only the engine trees are listed (2026-10-18: the whole
/// repository is about 21,000 entries and the cohort log keys some 90 commits a push).
fn engine_key(root: &Path, tree: &str, python: &str) -> Result<String, String> {
    let mut prefixes: Vec<&str> = ENGINE_DIRS.iter().map(|(p, _)| *p).collect();
    prefixes.sort_unstable();
    let mut args = vec!["ls-tree", "-r", tree, "--"];
    args.extend(prefixes);
    let listed = git(root, &args)?;
    let entries: Vec<(String, String)> = listed
        .lines()
        .filter_map(|line| {
            let (head, path) = line.split_once('\t')?;
            let sha = head.split_whitespace().nth(2)?;
            is_engine(path).then(|| (sha.to_owned(), path.to_owned()))
        })
        .collect();
    key_from_ids(root, &entries, python, |misses| {
        let shas: Vec<String> = misses.iter().map(|&i| entries[i].0.clone()).collect();
        cat_blobs(root, &shas)?
            .into_iter()
            .map(|b| b.ok_or(String::from("git cat-file lost a blob")))
            .collect()
    })
}

/// `engine_key` for the working tree (tracked and untracked-not-ignored engine files, current contents), so a run before committing keys what the commit will carry. The index holds every unchanged file's
/// blob id (T27: 15 ms against 270 ms), so only files that differ from it are hashed.
pub(crate) fn engine_key_worktree(root: &Path, python: &str) -> Result<String, String> {
    let listed = git(root, &["ls-files", "-co", "--exclude-standard"])?;
    let mut paths: Vec<&str> = listed
        .lines()
        .filter(|p| !p.trim().is_empty() && is_engine(p) && root.join(p).is_file())
        .collect();
    paths.sort_unstable();
    if paths.is_empty() {
        return Ok(sha256::hex(b""));
    }
    let with_paths = |head: &[&'static str]| {
        let mut args: Vec<&str> = head.to_vec();
        args.extend(paths.iter().copied());
        args
    };
    let staged_text = git(root, &with_paths(&["ls-files", "-s", "--"]))?;
    let mut ids: std::collections::HashMap<String, String> = staged_text
        .lines()
        .filter_map(|line| {
            let mut words = line.split_whitespace();
            let sha = words.nth(1)?;
            Some((words.nth(1)?.to_owned(), sha.to_owned()))
        })
        .collect();
    let changed_text = git(root, &with_paths(&["diff", "--name-only", "--"]))?;
    let changed: std::collections::HashSet<&str> = changed_text.lines().collect();
    let fresh: Vec<&str> = paths
        .iter()
        .copied()
        .filter(|p| changed.contains(p) || !ids.contains_key(*p))
        .collect();
    if !fresh.is_empty() {
        let out = git_fed(
            root,
            &["hash-object", "--stdin-paths"],
            format!("{}\n", fresh.join("\n")),
        )?;
        let text = String::from_utf8_lossy(&out).into_owned();
        let shas: Vec<&str> = text.split_whitespace().collect();
        ids.extend(
            fresh
                .iter()
                .zip(shas)
                .map(|(p, s)| ((*p).to_owned(), s.to_owned())),
        );
    }
    let entries: Vec<(String, String)> = paths
        .iter()
        .map(|p| (ids[*p].clone(), (*p).to_owned()))
        .collect();
    key_from_ids(root, &entries, python, |misses| {
        misses
            .iter()
            .map(|&i| stated(std::fs::read(root.join(&entries[i].1)), &entries[i].1))
            .collect()
    })
}

/// The engine paths of a newline-separated list.
fn engine_paths(paths: &mut dyn Read) -> Result<String, String> {
    let mut text = String::new();
    stated(paths.read_to_string(&mut text), "reading the paths")?;
    let mut out = String::new();
    for path in text.lines().filter(|p| is_engine(p)) {
        let _ = writeln!(out, "{path}");
    }
    Ok(out)
}

/// `l7r-gate delta compute [base] | cov-scope [base] | key [tree|worktree] | engine-paths` (the paths on stdin; the engine ones back).
pub(crate) fn cli(
    args: &[String],
    root: &Path,
    python: &str,
    stdin: &mut dyn Read,
) -> crate::Reply {
    let second = args.get(1).map(String::as_str);
    let answer = match args.first().map(String::as_str) {
        Some("compute") => compute(root, second.unwrap_or("origin/main"), python),
        Some("cov-scope") => coverage_scope(root, second.unwrap_or("origin/main")).map(|m| pytest_words(&m)),
        Some("key") if second == Some("worktree") => engine_key_worktree(root, python).map(|k| format!("{k}\n")),
        Some("key") => engine_key(root, second.unwrap_or("HEAD"), python).map(|k| format!("{k}\n")),
        Some("engine-paths") => engine_paths(stdin),
        _ => {
            return crate::Reply {
                stdout: String::new(),
                stderr: "usage: l7r-gate delta compute [base] | cov-scope [base] | key [tree|worktree] | engine-paths\n".to_owned(),
                code: 2,
            }
        }
    };
    match answer {
        Ok(stdout) => crate::Reply {
            stdout,
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("l7r-gate delta: {why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
