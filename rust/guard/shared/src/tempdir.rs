//! A scratch directory removed when it goes out of scope (feature 449 T101): `l7r-{tag}-{pid}-{seq}` under the temp directory, gone on a
//! return, a `?`, a failed assertion or a panic, since its `Drop` runs on each. The checks and tests that made their own and never removed
//! them left about 329,000 directories, roughly 126 GB, in the GM's `/tmp` (2026-11-11). `make rust-test` and `make hooks-test` run each
//! crate or suite with its own `TMPDIR` and fail on anything left in it, so a site that keeps a bare path again goes red.
//!
//! An INT or a TERM removes them too ([`signals`]); only a SIGKILL (or `std::process::exit` before the guard is dropped) leaves them, to
//! the next `TempDir` of their tag ([`sweep_dead`]) and the runners, which remove the per-run `TMPDIR` too.

mod signals;

use std::ffi::OsStr;
use std::ops::Deref;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// INT and TERM caught for the rest of the process, `then` run with the signal's number first - before every held directory is removed
/// and the process exits as the signal would (128 + its number). The one handler a process has: the `TempDir`s' and a caller's step
/// together (feature 449 T121: the Rust land's stop of its gate and cohort).
pub fn before_exit(then: fn(i32)) {
    signals::before_exit(then);
}

/// A directory of this process, removed on drop.
#[derive(Debug)]
#[must_use = "the directory is removed as soon as this value is dropped"]
pub struct TempDir {
    path: PathBuf,
}

impl TempDir {
    /// A new empty directory `l7r-{tag}-p{pid}-{seq}` under `std::env::temp_dir()` (which honors `TMPDIR`), after removing every
    /// `l7r-{tag}-p{pid}-{seq}` there whose process is gone ([`sweep_dead`]).
    pub fn new(tag: &str) -> Self {
        static SEQ: AtomicUsize = AtomicUsize::new(0);
        let parent = std::env::temp_dir();
        let hours_ago = SystemTime::now()
            .checked_sub(Duration::from_secs(3 * 3600))
            .unwrap_or(UNIX_EPOCH);
        sweep_dead(&parent, tag, Path::new("/proc"), hours_ago);
        let path = parent.join(format!(
            "l7r-{tag}-p{}-{}",
            std::process::id(),
            SEQ.fetch_add(1, Ordering::Relaxed)
        ));
        let _ = std::fs::remove_dir_all(&path);
        let _ = std::fs::create_dir_all(&path);
        signals::hold(&path);
        Self { path }
    }

    /// The directory.
    #[must_use]
    pub fn path(&self) -> &Path {
        &self.path
    }

    /// The directory, no longer removed on drop: for the rare one that must outlive this value.
    #[must_use]
    pub fn keep(self) -> PathBuf {
        let path = self.path.clone();
        signals::release(&path);
        std::mem::forget(self);
        path
    }
}

/// A value made inside a [`TempDir`] that keeps it - a path within it, its name as text, a fixture over it: what a helper returns when its
/// caller wants that value rather than the directory, which goes when the value does.
#[derive(Debug)]
#[must_use = "the directory is removed as soon as this value is dropped"]
pub struct Held<T> {
    value: T,
    dir: TempDir,
}

impl TempDir {
    /// `value`, keeping this directory for as long as it is held.
    pub fn hold<T>(self, value: T) -> Held<T> {
        Held { value, dir: self }
    }
}

impl<T> Held<T> {
    /// The value made into another, the directory still kept: a fixture changed by a struct update.
    pub fn map<U>(self, f: impl FnOnce(T) -> U) -> Held<U> {
        Held {
            value: f(self.value),
            dir: self.dir,
        }
    }
}

impl<T> Deref for Held<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.value
    }
}

impl<T> std::ops::DerefMut for Held<T> {
    fn deref_mut(&mut self) -> &mut T {
        &mut self.value
    }
}

impl<T: AsRef<Path>> AsRef<Path> for Held<T> {
    fn as_ref(&self) -> &Path {
        self.value.as_ref()
    }
}

impl<T: std::fmt::Display> std::fmt::Display for Held<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.value.fmt(f)
    }
}

impl AsRef<OsStr> for TempDir {
    fn as_ref(&self) -> &OsStr {
        self.path.as_os_str()
    }
}

impl<T: AsRef<OsStr>> AsRef<OsStr> for Held<T> {
    fn as_ref(&self) -> &OsStr {
        self.value.as_ref()
    }
}

impl serde::Serialize for TempDir {
    fn serialize<S: serde::Serializer>(&self, to: S) -> Result<S::Ok, S::Error> {
        self.path.serialize(to)
    }
}

impl<T: serde::Serialize> serde::Serialize for Held<T> {
    fn serialize<S: serde::Serializer>(&self, to: S) -> Result<S::Ok, S::Error> {
        self.value.serialize(to)
    }
}

impl Drop for TempDir {
    fn drop(&mut self) {
        signals::release(&self.path);
        let _ = std::fs::remove_dir_all(&self.path);
    }
}

impl Deref for TempDir {
    type Target = Path;
    fn deref(&self) -> &Path {
        &self.path
    }
}

impl AsRef<Path> for TempDir {
    fn as_ref(&self) -> &Path {
        &self.path
    }
}

/// A process killed by SIGKILL never runs its `Drop` or its INT and TERM handler ([`signals`]), so its directories outlive it. The next
/// `TempDir` of the same tag removes them: every `l7r-{tag}-p{pid}-{seq}` in `parent` whose pid has no `/proc` entry and which has not
/// changed since `before`, three hours ago - the GM, 2026-11-11: "don't touch dirs younger than a few hours (a running gate may own
/// them)", since a killed process's children can still be working in its directory. Only that form, which `TempDir` alone writes (the
/// `p` before the pid), so the directories the checks left before feature 449 T101, `l7r-{tag}-{pid}-{seq}`, are never touched: they are
/// the GM's laptop session's to delete. A pid reused by a live process keeps its directory, the safe way to be wrong; every process
/// sharing this `/tmp` is in this container's one pid namespace.
pub(crate) fn sweep_dead(parent: &Path, tag: &str, proc: &Path, before: SystemTime) {
    let lead = format!("l7r-{tag}-p");
    let Ok(entries) = std::fs::read_dir(parent) else {
        return;
    };
    for entry in entries.flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        let Some((pid, seq)) = name.strip_prefix(&lead).and_then(|r| r.split_once('-')) else {
            continue;
        };
        let numbered = pid.parse::<u32>().is_ok() && seq.parse::<u64>().is_ok();
        let a_dir = entry.file_type().is_ok_and(|t| t.is_dir());
        let old = entry
            .metadata()
            .and_then(|m| m.modified())
            .is_ok_and(|t| t < before);
        if numbered && a_dir && old && !proc.join(pid).exists() {
            let _ = std::fs::remove_dir_all(entry.path());
        }
    }
}

/// The name of the directory under the temp directory holding what a whole test process shares (`beside_binary`).
pub const SHARED: &str = "l7r-test-scratch";

/// A directory for what a whole test process shares (a fixture its tests make once, their log), which no value outlives to remove:
/// `<temp dir>/l7r-test-scratch/<name>`, emptied when a process first asks. Under `make rust-test` the temp directory is the run's own,
/// which the runner removes whole when the crate's run ends (`rustc.rs`'s `leak_checked`), so this goes on exit with it, and the
/// runner's leak check passes over this one name only because it removes it next (feature 449 T101; the GM 2026-11-11: "remove it on
/// exit"). Not in the build's `deps/`: the coverage report reads every file there as an object file.
#[must_use]
pub fn beside_binary(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(SHARED).join(name);
    let _ = std::fs::remove_dir_all(&dir);
    let _ = std::fs::create_dir_all(&dir);
    dir
}

#[cfg(test)]
mod tests;
