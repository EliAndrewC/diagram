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
