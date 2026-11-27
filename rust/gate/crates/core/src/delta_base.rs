//! THE BASE A DELTA IS READ FROM AT A HAND-IN (feature 461 T34). WHY: the checks that work out their own delta read it from the merge
//! base of HEAD with origin/main. At a builder's hand-in (461 T06's `Pass::HandIn { base }`) the tree stands detached at the hand-in
//! base with the work applied on it uncommitted; in phase 1 that base is the clone's HEAD, ahead of origin/main by every staged batch, so
//! from the merge base those checks judged every staged batch with the work, and could refuse the hand-in for another task's owed record
//! or claim (observed 2026-11-27, method: reading `push.rs` `delta()` and `owed.rs` `merge_base` against T06's first pass). So the
//! hand-in hands its base in [`VAR`] to the gates it runs, and each such check reads its delta from that commit where one is named.
//! Only `make land`'s hand-in pass sets it, on its own child processes; the landing's own pass hands it empty, so a stray export never
//! narrows what a landing judges.

use std::path::Path;

use crate::record::repo::git;

/// The variable the hand-in names its base in.
pub const VAR: &str = "L7R_DELTA_BASE";

/// The commit [`VAR`] names, resolved at `root`; None where it is unset, empty or names no commit there. A base that cannot be read
/// never narrows what a check judges: the check falls back to its own merge base.
#[must_use]
pub fn named(root: &Path) -> Option<String> {
    let given = env().filter(|g| !g.trim().is_empty())?;
    let spec = format!("{}^{{commit}}", given.trim());
    Some(
        git(root, &["rev-parse", "--verify", "-q", &spec])
            .trim()
            .to_owned(),
    )
    .filter(|s| !s.is_empty())
}

#[cfg(not(any(test, feature = "testkit")))]
fn env() -> Option<String> {
    std::env::var(VAR).ok()
}

#[cfg(any(test, feature = "testkit"))]
thread_local! {
    static GIVEN: std::cell::RefCell<Option<String>> = const { std::cell::RefCell::new(None) };
}

#[cfg(any(test, feature = "testkit"))]
fn env() -> Option<String> {
    GIVEN.with(|g| g.borrow().clone())
}

/// `f` run with [`VAR`] set to `base` on this thread only (a test's environment).
#[cfg(any(test, feature = "testkit"))]
pub fn with<R>(base: &str, f: impl FnOnce() -> R) -> R {
    GIVEN.with(|g| *g.borrow_mut() = Some(base.to_owned()));
    let out = f();
    GIVEN.with(|g| *g.borrow_mut() = None);
    out
}

#[cfg(test)]
mod tests {
    use super::{named, with};
    use crate::ci::fixtures::{git, repo};

    #[test]
    fn a_named_commit_is_the_base_and_anything_else_is_none() {
        let dir = repo("delta-base");
        let root: &std::path::Path = &dir;
        let head = git(root, &["rev-parse", "HEAD"]);
        assert_eq!(named(root), None);
        assert_eq!(with("HEAD", || named(root)), Some(head.clone()));
        assert_eq!(with(&format!(" {head}\n"), || named(root)), Some(head));
        assert_eq!(with("  ", || named(root)), None);
        assert_eq!(with("no-such-rev", || named(root)), None);
        // set for the call alone
        assert_eq!(named(root), None);
    }
}
