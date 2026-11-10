//! The state of the record checks in flight and the round arbiter's owed triggers (feature 449 T86, from `scripts/hooks/lib/hm_checks.py`, `hm_arbiter.py`, `hm_planhold.py`, `hm_fixloop.py` and
//! `hm_budget_rounds.py`): the one implementation that writes `<git common dir>/checks-open.json` and `arbiter-owed.json`. The guards (`check_bundle_hooks`, `checks_hooks`, `record_edit_hooks`,
//! `event_log_hooks`, `pair_hooks`, `review_round_hooks`, `workflow_hooks`) call it directly, `l7r-gate arbiter` and `l7r-gate checks` from the shell, and the Python callers through `scripts/checks_door.py`.

pub mod arbiter;
pub mod budget;
pub mod fixloop;
pub mod handle;
pub mod pages;
pub mod passes;
pub mod planhold;
pub mod reply;
pub mod rounds;

use std::fs::File;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::shared::pyjson;
use crate::shared::tool::{ask, flock};

/// The state file's name beside the clone's git directory.
pub const STATE: &str = "checks-open.json";
/// The owed triggers' file.
pub const OWED: &str = "arbiter-owed.json";

static GITDIR: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^gitdir:\s*(.+)").unwrap_or_else(|e| unreachable!("{e}")));
/// Two temporaries one process writes never share a name.
static SERIAL: AtomicU64 = AtomicU64::new(0);

/// `path` with its symlinks resolved where it exists, else made absolute (`pathlib.Path.resolve`, which is not strict).
#[must_use]
pub fn resolved(path: &Path) -> PathBuf {
    std::fs::canonicalize(path)
        .unwrap_or_else(|_| std::path::absolute(path).unwrap_or_else(|_| path.to_path_buf()))
}

/// The `gitdir:` a `.git` file names, or None for a file that names none.
fn gitdir_named(text: &str) -> Option<String> {
    let caps = GITDIR.captures(text.trim()).ok()??;
    Some(caps.get(1)?.as_str().to_owned())
}

/// The common git directory behind a worktree's `.git` file (the `commondir` a worktree's gitdir holds, else that gitdir).
fn through_gitdir(d: &Path, named: &str) -> PathBuf {
    let gd = resolved(&d.join(named));
    let common = gd.join("commondir");
    match std::fs::read_to_string(&common) {
        Ok(text) => resolved(&gd.join(text.trim())),
        Err(_) => gd,
    }
}

/// `<git common dir>/checks-open.json` of the clone holding `cwd`, found without running git (a hook on every call).
#[must_use]
pub fn state_path(cwd: &str) -> Option<PathBuf> {
    let start = if cwd.is_empty() { "." } else { cwd };
    let p = resolved(Path::new(start));
    for d in p.ancestors() {
        let g = d.join(".git");
        if g.is_dir() {
            return Some(g.join(STATE));
        }
        if g.is_file() {
            if let Some(named) = std::fs::read_to_string(&g)
                .ok()
                .as_deref()
                .and_then(gitdir_named)
            {
                return Some(through_gitdir(d, &named).join(STATE));
            }
        }
    }
    None
}

/// `hm_arbiter.common_dir`: the clone's common git directory, read off `root/.git` alone (a `.git` file naming nothing is itself the answer).
#[must_use]
pub fn common_dir(root: &Path) -> PathBuf {
    let g = root.join(".git");
    if g.is_file() {
        let gd = std::fs::read_to_string(&g)
            .ok()
            .as_deref()
            .and_then(gitdir_named)
            .map_or_else(|| g.clone(), |named| resolved(&root.join(named)));
        let common = gd.join("commondir");
        return match std::fs::read_to_string(&common) {
            Ok(text) => resolved(&gd.join(text.trim())),
            Err(_) => gd,
        };
    }
    g
}

/// The clone's root: the nearest ancestor of `cwd` (or the working directory) that holds a `.git` (`hm_checks._root`).
#[must_use]
pub fn clone_root(cwd: &str) -> Option<PathBuf> {
    let start = if cwd.is_empty() { "." } else { cwd };
    let p = resolved(Path::new(start));
    p.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// A JSON file, `{}` where it is missing or unreadable (`hm_checks.load`, `hm_arbiter._load`).
#[must_use]
pub fn load(path: &Path) -> Value {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .unwrap_or_else(empty)
}

/// An empty object.
pub(crate) fn empty() -> Value {
    Value::Object(Map::new())
}

/// The file a state's lock is taken on: `<stem>.lock` (`Path.with_suffix(".lock")`).
fn stem_lock(path: &Path) -> PathBuf {
    path.with_extension("lock")
}

/// A held exclusive lock; released when dropped (the file closed).
#[derive(Debug)]
pub struct Held(#[expect(dead_code, reason = "held so its descriptor keeps the lock")] File);

impl Held {
    fn on(lock_file: &Path) -> Option<Self> {
        if let Some(parent) = lock_file.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let file = File::create(lock_file).ok()?;
        flock(&file, "-x").then_some(Self(file))
    }
}

/// `hm_checks.locked`: the state file's read-modify-write held by one process at a time.
#[must_use]
pub fn locked(path: &Path) -> Option<Held> {
    Held::on(&stem_lock(path))
}

/// The lock beside the owed file, `arbiter-owed.json.lock` (`hm_arbiter.trip`'s).
#[must_use]
pub fn owed_locked(owed: &Path) -> Option<Held> {
    Held::on(&owed.with_file_name(format!("{OWED}.lock")))
}

fn unique_tmp(path: &Path) -> PathBuf {
    path.with_extension(format!(
        "{}.{}.tmp",
        std::process::id(),
        SERIAL.fetch_add(1, Ordering::Relaxed)
    ))
}

/// `state` written as `json.dumps(state, indent=1, sort_keys=True)` writes it, by atomic rename: the shape of `checks-open.json` and `arbiter-owed.json`.
///
/// # Errors
///
/// The directory or the file cannot be written.
pub fn save(path: &Path, state: &Value) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let tmp = unique_tmp(path);
    std::fs::write(&tmp, pyjson::dumps(&pyjson::sorted(state), Some(1), true))?;
    std::fs::rename(&tmp, path)
}

/// The owed triggers' file changed under its lock: `change` gets its contents and answers whether to write them back.
///
/// # Errors
///
/// The lock cannot be taken, or the file cannot be written.
pub fn with_owed(common: &Path, change: impl FnOnce(&mut Value) -> bool) -> Result<(), String> {
    let path = common.join(OWED);
    let held = owed_locked(&path).ok_or_else(|| format!("{OWED}: the lock could not be taken"))?;
    let mut state = load(&path);
    if change(&mut state) {
        save(&path, &state).map_err(|e| format!("{OWED}: {e}"))?;
    }
    drop(held);
    Ok(())
}

/// Seconds past the epoch, as `time.time()`.
#[must_use]
pub fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

/// The object field `key` of `value`, as text, or "".
#[must_use]
pub fn text<'a>(value: &'a Value, key: &str) -> &'a str {
    value.get(key).and_then(Value::as_str).unwrap_or("")
}

/// Is `value` falsy, as Python's `not value` reads JSON?
#[must_use]
pub fn falsy(value: Option<&Value>) -> bool {
    match value {
        None | Some(Value::Null | Value::Bool(false)) => true,
        Some(Value::Number(n)) => n.as_f64() == Some(0.0),
        Some(Value::String(s)) => s.is_empty(),
        Some(Value::Array(a)) => a.is_empty(),
        Some(Value::Object(o)) => o.is_empty(),
        Some(_) => false,
    }
}

/// `state.setdefault(key, {})`, the state coerced to an object if it was none.
pub(crate) fn map_mut<'a>(state: &'a mut Value, key: &str) -> &'a mut Map<String, Value> {
    if !state.is_object() {
        *state = empty();
    }
    let slot = state
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("state is an object"))
        .entry(key.to_owned())
        .or_insert_with(empty);
    if !slot.is_object() {
        *slot = empty();
    }
    slot.as_object_mut()
        .unwrap_or_else(|| unreachable!("slot is an object"))
}

/// `state.setdefault(key, [])`.
pub(crate) fn array_mut<'a>(state: &'a mut Map<String, Value>, key: &str) -> &'a mut Vec<Value> {
    let slot = state
        .entry(key.to_owned())
        .or_insert_with(|| Value::Array(Vec::new()));
    if !slot.is_array() {
        *slot = Value::Array(Vec::new());
    }
    slot.as_array_mut()
        .unwrap_or_else(|| unreachable!("slot is an array"))
}

/// A git command's trimmed stdout where it succeeded, else "" (`hm_checks`' many `git(...)` asks).
pub(crate) fn git_stdout(root: &Path, args: &[&str]) -> String {
    let at = root.to_string_lossy();
    let mut full = vec!["-C", at.as_ref()];
    full.extend_from_slice(args);
    let said = ask(Path::new("/"), "git", &full, "");
    if said.ok() {
        said.out.trim().to_owned()
    } else {
        String::new()
    }
}

/// `path` without its directory and its stem-joined name, as `Path.name`.
pub(crate) fn name_of(path: &Path) -> String {
    path.file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
}

#[cfg(test)]
pub(crate) mod testkit {
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    use crate::shared::tool::ask;

    static NEXT: AtomicU64 = AtomicU64::new(0);

    /// A fresh directory for one test; a process-unique, counter-unique name.
    pub(crate) fn dir(name: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "l7r-guard-checks-{}-{}-{name}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    /// A clone under `dir`: `git init`, a feature pointer at `specs/999-x`.
    pub(crate) fn clone_at(name: &str) -> PathBuf {
        let d = dir(name);
        let root = std::fs::canonicalize(&d).unwrap();
        let said = ask(&root, "git", &["init", "-q"], "");
        assert!(said.ok(), "{}", said.err);
        std::fs::create_dir_all(root.join(".specify")).unwrap();
        std::fs::write(
            root.join(".specify/feature.json"),
            r#"{"feature_directory": "specs/999-x"}"#,
        )
        .unwrap();
        std::fs::create_dir_all(root.join("specs/999-x")).unwrap();
        root
    }
}

#[cfg(test)]
mod tests;
