//! The delta (feature 449 T063 slice 2, from `l7r/diagram/ci/delta.py`): what this clone's own commits changed since the merge base with main, whether any of it is engine code, and the engine key a
//! green run vouches for. `is_engine` is THE ONE LIST of paths whose change requires the gate; it governs dispatch and never narrows what `stamp` hashes. The GM's rulings on each entry (2026-08-25,
//! 2026-09-05, feature 132 FR-024 and FR-025) are in the git history of `delta.py` and in `l7r/diagram/ci/CLAUDE.md`. Everything here runs in the repository the command was started in.

use std::fmt::Write as _;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_shared::sha256;
use serde_json::json;

use crate::codeid::{self, stated, Cache};

/// (directory, accepted endings). `tests/` is deliberately absent (GM 2026-08-25, feature 132 FR-024); the frozen tree stays so the merge route is what it was before feature 161 moved the hand-authored maps.
/// A live pool `.svg` is engine (449 T218): the hand-drawn sheets are source the pool sweep (`rust/mode_a/src/pool_sweep.rs`) judges,
/// and an edit to one landed DIRECT with no sweep while only `.gen.py` and `.json` (a `.compound.json` among them) counted. A render
/// is gitignored, so it never reaches a delta or `ls-files -co --exclude-standard`: the ending alone names the tracked sheets.
/// A live pool `.notes.md` is engine too (449 T223): the GM's 2026-08-25 ruling made a map's notes documentation ("even if the diagram
/// documentation was touched, but not the code itself, then we should not rerun the tests"), and the pool sweep now reads them - a hand
/// sheet's typed counts and `**On map**:` declaration, a hamlet's census block (`rust/mode_a/src/census/pool_check.rs`) - so a notes-only
/// edit that broke one landed DIRECT, judged by no sweep. Every pool tier's notes are read, so the whole of `pool/` counts, not the Mode A
/// tiers alone; the frozen exhibits' notes stay documentation, read by no check while none carries a census block.
/// A pool map's spec is its `.spec.json` or `.compound.json` (`.json` covers both) or its `.svg` since feature 449 T221, which deleted
/// the six `.gen.py` files and drew every map through one Rust driver: a `.gen.py` names no map's code now, and is no engine.
/// The building types' declaration `l7r/diagram/buildings/types.json` is engine (449 T231): the Mode A engine draws every compound from
/// it and the pool walk tells each sheet's tier by it, so an edit to it landed DIRECT with no sweep and every compound's drawing not
/// current. What only the page reads (its modal texts, `assets/`, `knobs.json`, the research fragments its modals link) stays out: the
/// page's, not the route's (feature 188, the GM 2026-09-05: "there's no actual reason to rerun all the tests for style sheet changes").
pub(crate) const ENGINE_DIRS: [(&str, &[&str]); 4] = [
    ("l7r/", &[".py", "/buildings/types.json"]),
    ("rust/", &[".rs", "Cargo.toml", "Cargo.lock"]),
    ("pool/", &[".json", ".svg", ".notes.md"]),
    ("legacy-hand-authored-pool/", &[".json"]),
];

/// The gate's own decider is tooling, not engine (feature 132 FR-025, the GM: "the engine itself isn't using it ... which makes it test code").
const NOT_ENGINE_DIR: &str = "l7r/diagram/ci/";

/// The files keyed on what runs rather than their bytes: a `.rs` file's comment-free tokens. A `.py` file was too (its docstring-blind
/// AST) until feature 449 T247 deleted `codeid.py`, the last `.py` file outside `specs/`: one is its blob id now, as `content_ids` gives it,
/// so an AST id the cache kept for its blob is never read.
fn semantic(path: &str) -> bool {
    Path::new(path)
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("rs"))
}

/// Is this repository-relative path engine code, the kind that owes the gate?
#[must_use]
pub fn is_engine(path: &str) -> bool {
    if path.starts_with(NOT_ENGINE_DIR) {
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

fn merge_base(root: &Path, base_ref: &str) -> Result<String, String> {
    Ok(git(root, &["merge-base", base_ref, "HEAD"])?
        .trim()
        .to_owned())
}

/// What this clone's own commits changed, and which of it is engine code.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Delta {
    pub base: String,
    pub files: Vec<String>,
    pub engine: Vec<String>,
}

impl Delta {
    #[must_use]
    pub fn route(&self) -> &'static str {
        if self.engine.is_empty() {
            "DIRECT"
        } else {
            "GATED"
        }
    }

    #[must_use]
    pub fn reason(&self) -> String {
        if self.files.is_empty() {
            return "no commits of our own since main - nothing to push".to_owned();
        }
        if self.engine.is_empty() {
            return format!(
                "{} file(s) changed, none of them diagram engine code - docs, specs or config only",
                self.files.len()
            );
        }
        let shown = self
            .engine
            .iter()
            .take(4)
            .cloned()
            .collect::<Vec<_>>()
            .join(", ");
        let more = if self.engine.len() > 4 {
            format!(" (+{} more)", self.engine.len() - 4)
        } else {
            String::new()
        };
        format!(
            "{} engine path(s) in our delta: {shown}{more}",
            self.engine.len()
        )
    }
}

/// What our own commits changed since we diverged from `base_ref`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn compute_delta(root: &Path, base_ref: &str) -> Result<Delta, String> {
    let base = merge_base(root, base_ref)?;
    let listed = git(root, &["diff", "--name-only", &base, "HEAD"])?;
    let mut files: Vec<String> = listed
        .lines()
        .filter(|f| !f.trim().is_empty())
        .map(str::to_owned)
        .collect();
    files.sort_unstable();
    // every engine path git says differs: a `.py` file's docstring-only edit was left out by its AST id until feature 449 T247, and no
    // `.py` file is left to have one
    let engine = files.iter().filter(|f| is_engine(f)).cloned().collect();
    Ok(Delta {
        base,
        files,
        engine,
    })
}

fn compute(root: &Path, base_ref: &str) -> Result<String, String> {
    let d = compute_delta(root, base_ref)?;
    Ok(format!(
        "{}\n",
        json!({"base": d.base, "files": d.files, "engine": d.engine})
    ))
}

/// The key from (git blob id, path) pairs: a semantic file by the id kept for that blob, its content read only on a miss, any other by the blob id; rows sorted and hashed as the Python hashed them.
fn key_from_ids(
    root: &Path,
    entries: &[(String, String)],
    fetch: impl FnOnce(&[usize]) -> Result<Vec<Vec<u8>>, String>,
) -> Result<String, String> {
    let mut cache = Cache::at(root);
    let misses: Vec<usize> = (0..entries.len())
        .filter(|&i| semantic(&entries[i].1) && cache.kept(&entries[i].0).is_none())
        .collect();
    let contents = fetch(&misses)?;
    let files: Vec<(PathBuf, Vec<u8>)> = misses
        .iter()
        .zip(contents)
        .map(|(&i, data)| (PathBuf::from(&entries[i].1), data))
        .collect();
    let ids = codeid::content_ids(&files, &mut cache);
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
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn engine_key(root: &Path, tree: &str) -> Result<String, String> {
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
    key_from_ids(root, &entries, |misses| {
        let shas: Vec<String> = misses.iter().map(|&i| entries[i].0.clone()).collect();
        cat_blobs(root, &shas)?
            .into_iter()
            .map(|b| b.ok_or(String::from("git cat-file lost a blob")))
            .collect()
    })
}

/// `engine_key` for the working tree (tracked and untracked-not-ignored engine files, current contents), so a run before committing keys what the commit will carry. The index holds every unchanged file's
/// blob id (T27: 15 ms against 270 ms), so only files that differ from it are hashed.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn engine_key_worktree(root: &Path) -> Result<String, String> {
    worktree_key(root, &[], &is_engine)
}

/// `engine_key_worktree` over the working tree's files under `pathspecs` (all of it when none) that `keep` takes: the key of what one
/// tool reads, so its kept result moves only with that (the work-budget review's counts, feature 449 T224). `keep` is a `dyn`, not
/// generic: one instantiation, so the coverage of its closures is one function's, not each caller's.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn worktree_key(
    root: &Path,
    pathspecs: &[&str],
    keep: &dyn Fn(&str) -> bool,
) -> Result<String, String> {
    let mut args = vec!["ls-files", "-co", "--exclude-standard", "--"];
    args.extend(pathspecs);
    let listed = git(root, &args)?;
    let mut paths: Vec<&str> = listed
        .lines()
        .filter(|p| !p.trim().is_empty() && keep(p) && root.join(p).is_file())
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
    key_from_ids(root, &entries, |misses| {
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

/// `l7r-gate delta compute [base] | key [tree|worktree] | engine-paths` (the paths on stdin; the engine ones back).
pub fn cli(args: &[String], root: &Path, stdin: &mut dyn Read) -> crate::Reply {
    let second = args.get(1).map(String::as_str);
    let answer =
        match args.first().map(String::as_str) {
            Some("compute") => compute(root, second.unwrap_or("origin/main")),
            Some("key") if second == Some("worktree") => {
                engine_key_worktree(root).map(|k| format!("{k}\n"))
            }
            Some("key") => engine_key(root, second.unwrap_or("HEAD")).map(|k| format!("{k}\n")),
            Some("engine-paths") => engine_paths(stdin),
            _ => return crate::Reply {
                stdout: String::new(),
                stderr:
                    "usage: l7r-gate delta compute [base] | key [tree|worktree] | engine-paths\n"
                        .to_owned(),
                code: 2,
            },
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
