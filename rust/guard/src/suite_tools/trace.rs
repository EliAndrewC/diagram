//! `l7r-guard trace` (feature 449 T050, the port of `tests/hooks/hooktrace.py`, feature 383 amendment 3): a guard suite's inputs by what it READ the last time it went
//! green. Each suite runs under the preloaded C-library recorder (`tests/tooling/_deps_site/l7r_file_log.c`); every file it opens, stats or lists under the repository is
//! kept by content when the suite goes green, and the suite is skipped while every read is unchanged. A suite that read the repository's own git directory (a clone of it:
//! its content comes through git, which the recorder does not follow), or a file git ignores, is not traced: it keeps the `deps` key.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Component, Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Map, Value};

use crate::protocol::Reply;
use crate::shared::{sha1, sha256};
use crate::suite_tools::deps::tool_root;

const SKIP: [&str; 2] = [".git/l7r-cache/", ".git/hooks-test/"]; // content caches and the stamps themselves

fn source(repo: &Path) -> PathBuf {
    repo.join("tests/tooling/_deps_site/l7r_file_log.c")
}

fn recorder_version(repo: &Path) -> String {
    std::fs::read(source(repo)).map_or_else(|_| String::new(), |b| sha256::hex(&b)[..12].to_owned())
}

/// The recorder, built once per version of its source: its path, or nothing.
#[must_use]
pub fn shim(repo: &Path, gitdir: &Path, compiler: &str) -> String {
    let version = recorder_version(repo);
    if version.is_empty() {
        return String::new();
    }
    let so = gitdir.join(format!("l7r-cache/l7r_file_log-{version}.so"));
    if so.is_file() {
        return so.to_string_lossy().into_owned();
    }
    let _ = so.parent().map(std::fs::create_dir_all);
    let tmp = so.with_extension(format!("{}.tmp", std::process::id()));
    let built = Command::new(compiler)
        .args(["-shared", "-fPIC", "-O2", "-o"])
        .arg(&tmp)
        .arg(source(repo))
        .arg("-ldl")
        .output();
    if built.is_ok_and(|o| o.status.success()) && std::fs::rename(&tmp, &so).is_ok() {
        return so.to_string_lossy().into_owned();
    }
    let _ = std::fs::remove_file(&tmp);
    String::new()
}

/// `os.path.relpath`, for absolute paths.
fn relpath(path: &str, root: &Path) -> String {
    let normal = |p: &Path| -> Vec<String> {
        let mut out: Vec<String> = Vec::new();
        for c in p.components() {
            match c {
                Component::ParentDir => {
                    out.pop();
                }
                Component::Normal(n) => out.push(n.to_string_lossy().into_owned()),
                _ => {}
            }
        }
        out
    };
    let (to, from) = (normal(Path::new(path)), normal(root));
    let common = to.iter().zip(&from).take_while(|(a, b)| a == b).count();
    let mut parts = vec!["..".to_owned(); from.len() - common];
    parts.extend_from_slice(&to[common..]);
    parts.join("/")
}

fn rel(path: &str, root: &Path) -> String {
    let rel = relpath(path, root);
    let cached = Path::new(&rel).extension().is_some_and(|e| e == "pyc")
        && format!("/{rel}").contains("/__pycache__/");
    match rel.rsplit_once("__pycache__/") {
        Some((head, name)) if cached => {
            format!("{head}{}.py", name.split('.').next().unwrap_or(name))
        }
        _ => rel,
    }
}

/// What a suite's log says it read, or None where it cannot be traced (git read the repository).
#[must_use]
pub fn reads(log: &Path, root: &Path) -> Option<(BTreeSet<String>, BTreeSet<String>)> {
    let (mut files, mut dirs) = (BTreeSet::new(), BTreeSet::new());
    let text = String::from_utf8_lossy(&std::fs::read(log).unwrap_or_default()).into_owned();
    for line in text.lines() {
        let rest = line.split_once('\t').map_or("", |(_, r)| r);
        let (kind, path) = rest.split_once('\t').unwrap_or((rest, ""));
        if kind == "c-git" {
            return None;
        }
        let rel = rel(path, root);
        if !rel.is_empty() && !SKIP.iter().any(|s| rel.starts_with(s)) && rel != ".git" {
            match kind {
                "c-file" => {
                    files.insert(rel);
                }
                "c-dir" => {
                    dirs.insert(rel);
                }
                _ => {}
            }
        }
    }
    Some((files, dirs))
}

fn git_z(root: &Path, args: &[&str]) -> Vec<String> {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    let out = done
        .ok()
        .filter(|o| o.status.success())
        .map_or_else(Vec::new, |o| o.stdout);
    String::from_utf8_lossy(&out)
        .split('\0')
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect()
}

fn hash_file(path: &Path) -> String {
    std::fs::read(path).map_or_else(
        |_| "gone".to_owned(),
        |data| {
            let mut all = format!("blob {}\0", data.len()).into_bytes();
            all.extend(data);
            sha1::hex(&all)
        },
    )
}

/// What the tree holds now: each file's content id (`record_cache.content_ids`, untracked included) and each directory's entries.
struct Now {
    root: PathBuf,
    ids: HashMap<String, String>,
    entries: BTreeMap<String, BTreeSet<String>>,
}

impl Now {
    fn of(root: &Path) -> Self {
        let mut ids = HashMap::new();
        for record in git_z(root, &["ls-files", "-s", "-z"]) {
            let (meta, path) = record.split_once('\t').unwrap_or((&record, ""));
            let parts: Vec<&str> = meta.split_whitespace().collect();
            if parts.len() == 3 && !path.is_empty() {
                ids.insert(path.to_owned(), parts[1].to_owned());
            }
        }
        for path in git_z(root, &["diff", "--name-only", "-z"])
            .into_iter()
            .chain(git_z(
                root,
                &["ls-files", "--others", "--exclude-standard", "-z"],
            ))
        {
            let id = hash_file(&root.join(&path));
            ids.insert(path, id);
        }
        let mut entries: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
        for path in ids.keys() {
            let parts: Vec<&str> = path.split('/').collect();
            for i in 0..parts.len() {
                entries
                    .entry(parts[..i].join("/"))
                    .or_default()
                    .insert(parts[i].to_owned());
            }
        }
        Self {
            root: root.to_path_buf(),
            ids,
            entries,
        }
    }

    /// A directory's entries as `json.dumps` wrote them, so a stamp kept before the port stands.
    fn dir_state(&self, rel: &str) -> String {
        let items: Vec<String> = self
            .entries
            .get(rel)
            .into_iter()
            .flatten()
            .map(|e| Value::from(e.as_str()).to_string())
            .collect();
        format!("[{}]", items.join(", "))
    }

    fn file_state(&self, rel: &str) -> String {
        if let Some(id) = self.ids.get(rel) {
            return id.clone();
        }
        let at = self.root.join(rel);
        let word = if !at.exists() {
            "absent"
        } else if at.is_dir() {
            "dir"
        } else {
            "ignored"
        };
        word.to_owned()
    }
}

/// A suite's trace at one of its kept keys (feature 451 T304): one trace a suite, `<guard>.trace.json` in the COMMON git directory, was
/// replaced by each tree's green run, so trees of different content, run in turn, reran each other's suites; a trace is now kept a key
/// each, the oldest past the bound (`HOOKS_STAMP_KEEP`, `hookrun.sh`'s knob, handed in) removed.
fn trace_file(gitdir: &Path, guard: &str, key: &str) -> PathBuf {
    gitdir.join(format!("hooks-test/traces/{guard}@{key}.json"))
}

/// A guard's kept traces, newest first.
fn traces(gitdir: &Path, guard: &str) -> Vec<PathBuf> {
    let head = format!("{guard}@");
    let mine = |e: &std::fs::DirEntry| {
        let name = e.file_name().to_string_lossy().into_owned();
        name.strip_prefix(&head)
            .and_then(|k| k.strip_suffix(".json"))
            .is_some()
    };
    let mut found: Vec<(SystemTime, PathBuf)> = std::fs::read_dir(gitdir.join("hooks-test/traces"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(mine)
        .map(|e| {
            (
                e.metadata()
                    .and_then(|m| m.modified())
                    .unwrap_or(UNIX_EPOCH),
                e.path(),
            )
        })
        .collect();
    found.sort_by(|a, b| b.cmp(a));
    found.into_iter().map(|(_, p)| p).collect()
}

/// Keep a green suite's reads at its key, and at most `keep` of its traces; nothing is kept where it cannot be traced, and the suite keeps the `deps` key.
pub fn stamp(
    repo: &Path,
    gitdir: &Path,
    guard: &str,
    key: &str,
    keep: usize,
    log: &Path,
    root: &Path,
) {
    let target = trace_file(gitdir, guard, key);
    let _ = std::fs::remove_file(&target);
    let _ = std::fs::remove_file(gitdir.join(format!("hooks-test/{guard}.trace.json"))); // the one trace a suite before T304
    let Some((files, dirs)) = reads(log, root).filter(|(files, _)| !files.is_empty()) else {
        return;
    };
    let now = Now::of(root);
    let file_states: Map<String, Value> = files
        .iter()
        .map(|r| (r.clone(), Value::from(now.file_state(r))))
        .collect();
    if file_states.values().any(|v| v == "ignored") {
        return; // it read a file git ignores: not known by content
    }
    let dir_states: Map<String, Value> = dirs
        .iter()
        .map(|r| (r.clone(), Value::from(now.dir_state(r))))
        .collect();
    let kept =
        json!({"recorder": recorder_version(repo), "files": file_states, "dirs": dir_states});
    let _ = target.parent().map(std::fs::create_dir_all);
    let _ = std::fs::write(target, kept.to_string());
    for old in traces(gitdir, guard).into_iter().skip(keep.max(1)) {
        let _ = std::fs::remove_file(old);
    }
}

fn unchanged(kept: &Value, key: &str, state: &dyn Fn(&str) -> String) -> bool {
    kept[key].as_object().is_some_and(|m| {
        m.iter()
            .all(|(rel, was)| was.as_str() == Some(state(rel).as_str()))
    })
}

/// The guards with a kept trace whose reads are all unchanged, each with the key of its newest such trace.
#[must_use]
pub fn fresh(repo: &Path, gitdir: &Path, root: &Path, guards: &[String]) -> Vec<(String, String)> {
    let kept: Vec<(&String, Vec<PathBuf>)> = guards
        .iter()
        .map(|g| (g, traces(gitdir, g)))
        .filter(|(_, t)| !t.is_empty())
        .collect();
    if kept.is_empty() {
        return Vec::new();
    }
    let (now, recorder) = (Now::of(root), recorder_version(repo));
    let same = |path: &&PathBuf| {
        let k: Value = std::fs::read_to_string(path)
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .unwrap_or_default();
        k["recorder"].as_str() == Some(recorder.as_str())
            && unchanged(&k, "files", &|r| now.file_state(r))
            && unchanged(&k, "dirs", &|r| now.dir_state(r))
    };
    let key = |g: &str, path: &Path| {
        let name = path.file_name().unwrap_or_default().to_string_lossy();
        name[g.len() + 1..name.len() - ".json".len()].to_owned()
    };
    kept.into_iter()
        .filter_map(|(g, t)| t.iter().find(same).map(|p| (g.clone(), key(g, p))))
        .collect()
}

/// `l7r-guard trace`: `shim <gitdir>`, `stamp <gitdir> <guard> <key> <keep> <log> <root>`, `fresh <gitdir> <root> <guard>...` (a line
/// a fresh guard, `<guard> <key>`).
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    answer(&tool_root(), args, "gcc")
}

pub(crate) fn answer(repo: &Path, args: &[String], compiler: &str) -> Reply {
    let say = |stdout: String| Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    };
    let arg = |n: usize| Path::new(&args[n]);
    match (args.first().map_or("", String::as_str), args.len()) {
        ("shim", 2..) => say(shim(repo, arg(1), compiler) + "\n"),
        ("stamp", 7) => {
            let keep = args[4].parse().unwrap_or(6);
            stamp(repo, arg(1), &args[2], &args[3], keep, arg(5), arg(6));
            say(String::new())
        }
        ("fresh", 3..) => say(
            fresh(repo, arg(1), arg(2), &args[3..])
                .iter()
                .map(|(g, k)| [g.as_str(), " ", k, "\n"].concat())
                .collect(),
        ),
        _ => Reply { stdout: String::new(), stderr: "usage: l7r-guard trace shim <gitdir> | stamp <gitdir> <guard> <key> <keep> <log> <root> | fresh <gitdir> <root> <guard>...\n".to_owned(), code: 2 },
    }
}

#[cfg(test)]
mod tests;
