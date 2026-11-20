//! The process environment as the guard's code reads it (feature 451 T32). A normal build reads the process's own; a test build
//! reads the test thread's own map, empty until the test names a variable - so a session's exports (a page session's
//! `L7R_FEATURE_DIRECTORY`, a `make land`'s `L7R_LAND_TICKS`) never reach a test, and a test that names one never races another
//! (T24's defect in the guard's own tests: 17 tests turned red with `L7R_FEATURE_DIRECTORY` exported, observed 2026-11-20). `HOME`
//! and the guard log's `GUARD_LOG_DIR` stay the process's: a test's world is built under the real temp directory and home.

#[cfg(test)]
thread_local! {
    /// The tests' environment: each test thread its own, so a test that names a variable never races another.
    pub static VARS: std::cell::RefCell<std::collections::HashMap<String, String>> = std::cell::RefCell::default();
}

/// An environment variable, None where unset or not text (`std::env::var(name).ok()`).
#[cfg(not(test))]
#[must_use]
pub fn opt(name: &str) -> Option<String> {
    std::env::var(name).ok()
}

/// An environment variable, read from the test thread's own map; `HOME`, where the test names none, the process's.
#[cfg(test)]
#[must_use]
pub fn opt(name: &str) -> Option<String> {
    VARS.with(|v| v.borrow().get(name).cloned())
        .or_else(|| (name == "HOME").then(|| std::env::var(name).ok()).flatten())
}

/// An environment variable, "" where unset or not text.
#[must_use]
pub fn var(name: &str) -> String {
    opt(name).unwrap_or_default()
}

/// A test names a variable in its own thread's environment.
#[cfg(test)]
pub fn set(name: &str, value: impl AsRef<std::ffi::OsStr>) {
    let value = value.as_ref().to_string_lossy().into_owned();
    VARS.with(|v| v.borrow_mut().insert(name.to_owned(), value));
}

/// A test drops a variable from its own thread's environment.
#[cfg(test)]
pub fn unset(name: &str) {
    VARS.with(|v| v.borrow_mut().remove(name));
}

/// An environment reader, as the guard's `_in` functions take one (feature 451 T38): [`opt`] the process's own (a test build of the
/// guard, the test thread's map), [`Rooted::with`] a dependent's test's own map.
pub type Reader = dyn Fn(&str) -> Option<String> + Send + Sync;

/// A tree's root and the environment read beside it, carried together (feature 451 T38): a gate crate hands [`Rooted::reader`] to
/// each guard read it makes, so a dependent's test - which the guard's `cfg(test)` map never reaches - reads its own environment,
/// never a session's export (49 tests of 7 gate crates turned red with `L7R_FEATURE_DIRECTORY` and `L7R_EVENTS_DIR` exported,
/// observed 2026-11-20), and no test mutates the process's. It derefs to the root, so a `&Rooted` goes where a `&Path` went.
#[derive(Clone)]
pub struct Rooted {
    path: std::path::PathBuf,
    env: std::sync::Arc<Reader>,
}

impl Rooted {
    /// `path` read with the process's environment ([`opt`]): a real run's.
    #[must_use]
    pub fn process(path: impl Into<std::path::PathBuf>) -> Self {
        Self {
            path: path.into(),
            env: std::sync::Arc::new(opt),
        }
    }

    /// `path` read with `vars` alone - a test's own environment; `HOME`, where it names none, the process's (a test's world is
    /// built under the real home, as the guard's own test map reads it).
    #[must_use]
    pub fn with(path: impl Into<std::path::PathBuf>, vars: &[(&str, &str)]) -> Self {
        let map: std::collections::HashMap<String, String> = vars
            .iter()
            .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
            .collect();
        let env = move |name: &str| {
            map.get(name)
                .cloned()
                .or_else(|| (name == "HOME").then(|| std::env::var(name).ok()).flatten())
        };
        Self {
            path: path.into(),
            env: std::sync::Arc::new(env),
        }
    }

    /// Another root read with this one's environment (a worktree, a clone, a fixture's subdirectory).
    #[must_use]
    pub fn at(&self, path: impl Into<std::path::PathBuf>) -> Self {
        Self {
            path: path.into(),
            env: std::sync::Arc::clone(&self.env),
        }
    }

    /// The root.
    #[must_use]
    pub fn path(&self) -> &std::path::Path {
        &self.path
    }

    /// The environment, for a guard `_in` function.
    pub fn reader(&self) -> &Reader {
        &*self.env
    }

    /// A variable of this environment, None where unset.
    #[must_use]
    pub fn opt(&self, name: &str) -> Option<String> {
        (self.env)(name)
    }

    /// A variable of this environment, "" where unset.
    #[must_use]
    pub fn var(&self, name: &str) -> String {
        self.opt(name).unwrap_or_default()
    }
}

impl std::ops::Deref for Rooted {
    type Target = std::path::Path;
    fn deref(&self) -> &std::path::Path {
        &self.path
    }
}

impl AsRef<std::path::Path> for Rooted {
    fn as_ref(&self) -> &std::path::Path {
        &self.path
    }
}

impl std::fmt::Debug for Rooted {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_tuple("Rooted").field(&self.path).finish()
    }
}

#[cfg(test)]
mod tests {
    use super::{set, unset, Rooted};
    use std::path::Path;

    #[test]
    fn a_rooted_reads_its_own_environment_and_derefs_to_its_root() {
        let own = Rooted::with("/r", &[("L7R_FEATURE_DIRECTORY", "specs/900-x")]);
        assert_eq!(
            own.opt("L7R_FEATURE_DIRECTORY").as_deref(),
            Some("specs/900-x")
        );
        assert_eq!(own.var("L7R_EVENTS_DIR"), "");
        assert_eq!(own.opt("HOME"), std::env::var("HOME").ok());
        assert_eq!(
            (own.reader())("L7R_FEATURE_DIRECTORY").as_deref(),
            Some("specs/900-x")
        );
        let there = own.at("/s");
        assert_eq!(
            (there.path(), there.join("a")),
            (Path::new("/s"), Path::new("/s/a").to_path_buf())
        );
        assert_eq!(there.var("L7R_FEATURE_DIRECTORY"), "specs/900-x");
        let p: &Path = own.as_ref();
        assert_eq!(
            (p, format!("{own:?}")),
            (Path::new("/r"), "Rooted(\"/r\")".to_owned())
        );
        let proc = Rooted::process("/r");
        set("L7R_EVENTS_DIR", "/e");
        assert_eq!(proc.var("L7R_EVENTS_DIR"), "/e");
        unset("L7R_EVENTS_DIR");
        assert_eq!(proc.opt("L7R_EVENTS_DIR"), None);
    }
}
