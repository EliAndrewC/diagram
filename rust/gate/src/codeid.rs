//! A file's content id (feature 449 T062, from `scripts/gates/codeid.py` and `l7r-gate stamp`): what a gate actually exercised, so that a comment's edit keeps the engine key. A `.rs` file's id is its
//! comment-free tokens; a `.py` file's is Python's own `ast.dump` of its docstring-free tree, which only Python can say, so `codeid.py` is asked once a run with every id the cache lacks (the round
//! arbiter's `ask:449-T062-py-id`), and if it cannot answer the run fails rather than writing a substitute. Any other file's id is its blob id. The ids are kept by raw blob id in one file, shared with the
//! Python callers until they are ported.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_guard::shared::{sha1, sha256};
use serde_json::Value;

const CACHE_NAME: &str = "semantic-id-cache-2.json";

/// Python's `str.isspace`: Rust's whitespace and the four information separators it leaves out.
fn is_space(c: char) -> bool {
    c.is_whitespace() || ('\x1c'..='\x1f').contains(&c)
}

/// A raw string's opening at `at` (`r"`, `r#"`, `br##"`...): its hash run and where its text starts.
fn raw_open(s: &[char], at: usize) -> Option<(usize, usize)> {
    let mut i = at + usize::from(s[at] == 'b');
    if s.get(i) != Some(&'r') {
        return None;
    }
    i += 1;
    let start = i;
    while s.get(i) == Some(&'#') {
        i += 1;
    }
    (s.get(i) == Some(&'"')).then_some((i - start, i + 1))
}

fn find(s: &[char], needle: &[char], from: usize) -> Option<usize> {
    (from..=s.len().saturating_sub(needle.len())).find(|&i| s[i..].starts_with(needle))
}

/// What runs, for a `.rs` file: its tokens with every comment dropped, whitespace between them collapsed, strings and char literals kept whole, a lifetime a token. A file that is not UTF-8 is its bytes.
#[must_use]
pub fn rust_tokens(data: &[u8]) -> Vec<u8> {
    let Ok(text) = std::str::from_utf8(data) else {
        return data.to_vec();
    };
    let s: Vec<char> = text.chars().collect();
    let stop = s.len();
    let (mut out, mut cur, mut i): (Vec<String>, String, usize) = (Vec::new(), String::new(), 0);
    let slice = |a: usize, b: usize| s[a..b.min(stop)].iter().collect::<String>();
    while i < stop {
        let c = s[i];
        if s[i..].starts_with(&['/', '/']) {
            out.extend(flushed(&mut cur));
            i = find(&s, &['\n'], i).unwrap_or(stop);
        } else if s[i..].starts_with(&['/', '*']) {
            out.extend(flushed(&mut cur));
            let mut depth = 1;
            i += 2;
            while i < stop && depth > 0 {
                if s[i..].starts_with(&['/', '*']) {
                    depth += 1;
                    i += 2;
                } else if s[i..].starts_with(&['*', '/']) {
                    depth -= 1;
                    i += 2;
                } else {
                    i += 1;
                }
            }
        } else if let Some((hashes, text_at)) = Some(c)
            .filter(|c| matches!(c, 'r' | 'b'))
            .and_then(|_| raw_open(&s, i))
        {
            out.extend(flushed(&mut cur));
            let close: Vec<char> = std::iter::once('"')
                .chain(std::iter::repeat_n('#', hashes))
                .collect();
            let end = find(&s, &close, text_at).map_or(stop, |at| at + 1 + hashes);
            out.push(slice(i, end));
            i = end;
        } else if c == '"' || s[i..].starts_with(&['b', '"']) {
            out.extend(flushed(&mut cur));
            let mut j = i + if c == 'b' { 2 } else { 1 };
            while j < stop && s[j] != '"' {
                j += if s[j] == '\\' { 2 } else { 1 };
            }
            out.push(slice(i, j + 1));
            i = j + 1;
        } else if c == '\'' {
            out.extend(flushed(&mut cur));
            let close = if s.get(i + 1) == Some(&'\\') {
                Some(find(&s, &['\''], i + 2).unwrap_or(stop - 1))
            } else if s.get(i + 2) == Some(&'\'') {
                Some(i + 2)
            } else {
                None
            };
            let mut j = close.unwrap_or(i);
            if close.is_none() {
                while j + 1 < stop && (s[j + 1].is_alphanumeric() || s[j + 1] == '_') {
                    j += 1;
                }
            }
            out.push(slice(i, j + 1));
            i = j + 1;
        } else if is_space(c) {
            out.extend(flushed(&mut cur));
            i += 1;
        } else if c.is_alphanumeric() || c == '_' {
            cur.push(c);
            i += 1;
        } else {
            out.extend(flushed(&mut cur));
            out.push(c.to_string());
            i += 1;
        }
    }
    out.extend(flushed(&mut cur));
    out.join("\0").into_bytes()
}

fn flushed(cur: &mut String) -> Option<String> {
    (!cur.is_empty()).then(|| std::mem::take(cur))
}

/// The id git gives these bytes as a blob.
#[must_use]
pub fn git_blob_id(data: &[u8]) -> String {
    let mut all = format!("blob {}\0", data.len()).into_bytes();
    all.extend_from_slice(data);
    sha1::hex(&all)
}

fn suffix(name: &str) -> &str {
    name.rsplit_once('.').map_or("", |(_, e)| e)
}

/// The ids kept beside a repository, by raw blob id, one format with the Python callers'.
pub struct Cache {
    path: Option<PathBuf>,
    table: BTreeMap<String, String>,
    dirty: bool,
}

fn read_table(path: &Path) -> BTreeMap<String, String> {
    let parsed: Value = std::fs::read_to_string(path)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_default();
    parsed
        .as_object()
        .into_iter()
        .flatten()
        .filter_map(|(k, v)| Some((k.clone(), v.as_str()?.to_owned())))
        .collect()
}

/// The repository's common git directory (a worktree's and its parent's are the same one), or None outside a repository.
#[must_use]
pub fn common_git_dir(root: &Path) -> Option<PathBuf> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-parse", "--path-format=absolute", "--git-common-dir"])
        .output()
        .ok()?;
    done.status
        .success()
        .then(|| PathBuf::from(String::from_utf8_lossy(&done.stdout).trim()))
}

impl Cache {
    /// The cache of the repository at `root`; with no repository, an empty one nothing is written to.
    #[must_use]
    pub fn at(root: &Path) -> Self {
        let path = common_git_dir(root).map(|d| d.join(CACHE_NAME));
        let table = path.as_deref().map(read_table).unwrap_or_default();
        Self {
            path,
            table,
            dirty: false,
        }
    }

    /// The id kept for this blob, if any.
    #[must_use]
    pub fn kept(&self, raw: &str) -> Option<&str> {
        self.table.get(raw).map(String::as_str)
    }

    /// Written whole and renamed into place, the entries another writer added since this one read them kept.
    pub fn save(&mut self) {
        let (Some(path), true) = (self.path.as_deref(), self.dirty) else {
            return;
        };
        let mut merged = read_table(path);
        merged.append(&mut self.table);
        let tmp = path.with_extension(format!("{}.tmp", std::process::id()));
        if serde_json::to_vec(&merged)
            .ok()
            .and_then(|text| std::fs::write(&tmp, text).ok())
            .is_some()
        {
            let _ = std::fs::rename(&tmp, path);
        }
        self.table = merged;
        self.dirty = false;
    }
}

/// A fallible call's error as this crate's text, naming what was being done.
pub(crate) fn stated<T>(done: std::io::Result<T>, what: &str) -> Result<T, String> {
    done.map_err(said(what))
}

/// Outside the generic function, so the one closure is one piece of code to test rather than one for each `T`.
fn said(what: &str) -> impl FnOnce(std::io::Error) -> String + '_ {
    move |e| format!("{what}: {e}")
}

/// The `codeid.py` to ask: the wrapper's own tree, since a fixture repository the binary runs in has none; without the wrapper, `root`'s.
#[must_use]
pub fn script(root: &Path) -> PathBuf {
    let tree = std::env::var_os("L7R_GATE_TREE").map(PathBuf::from);
    tree.unwrap_or(root.to_path_buf())
        .join("scripts/gates/codeid.py")
}

/// `(path, data)` of each file; each one's id, in order.
///
/// # Errors
///
/// Why Python could not answer for a `.py` file; nothing is kept for it.
pub fn content_ids(
    files: &[(PathBuf, Vec<u8>)],
    cache: &mut Cache,
    python: &str,
    codeid: &Path,
) -> Result<Vec<String>, String> {
    let mut out = Vec::with_capacity(files.len());
    let mut asked: Vec<(usize, &Path, String)> = Vec::new();
    for (at, (path, data)) in files.iter().enumerate() {
        let raw = git_blob_id(data);
        let kind = suffix(&path.to_string_lossy()).to_owned();
        if kind != "py" && kind != "rs" {
            out.push(raw);
        } else if let Some(id) = cache.table.get(&raw) {
            out.push(id.clone());
        } else if kind == "rs" {
            let id = sha256::hex(&rust_tokens(data));
            cache.table.insert(raw, id.clone());
            cache.dirty = true;
            out.push(id);
        } else {
            out.push(String::new());
            asked.push((at, path, raw));
        }
    }
    if !asked.is_empty() {
        let done = Command::new(python)
            .arg(codeid)
            .arg("--ids")
            .args(asked.iter().map(|(_, p, _)| p))
            .output()
            .map_err(|e| format!("cannot start {python}: {e}"))?;
        let text = String::from_utf8_lossy(&done.stdout).into_owned();
        let ids: Vec<&str> = text.split_whitespace().collect();
        if !done.status.success() || ids.len() != asked.len() {
            return Err(format!(
                "{} answered no ids for the .py files: {}",
                codeid.display(),
                String::from_utf8_lossy(&done.stderr).trim()
            ));
        }
        for ((at, _, raw), id) in asked.into_iter().zip(ids) {
            id.clone_into(&mut out[at]);
            cache.table.insert(raw, id.to_owned());
            cache.dirty = true;
        }
    }
    cache.save();
    Ok(out)
}

#[cfg(test)]
mod tests;
