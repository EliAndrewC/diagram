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

// A base GIVEN on this thread, in place of the process's variable (461 T38): `make land` asks the claims in its own process, which
// never sees the variable it hands its child processes, so the claims door takes the base as an argument and reads it here. An empty
// value given is a base given as none - a landing's own ask - so a stray export never narrows what an in-process call judges.
thread_local! {
    static GIVEN: std::cell::RefCell<Option<String>> = const { std::cell::RefCell::new(None) };
}

fn env() -> Option<String> {
    GIVEN.with(|g| g.borrow().clone()).or_else(process)
}

#[cfg(not(any(test, feature = "testkit")))]
fn process() -> Option<String> {
    std::env::var(VAR).ok()
}

// a test build reads no process variable: each test names its base on its own thread
#[cfg(any(test, feature = "testkit"))]
fn process() -> Option<String> {
    None
}

/// `f` run with the base given as `base` on this thread only, in place of [`VAR`]: the in-process door's (461 T38) and a test's
/// environment. The base given before is restored after, so a call given one inside another leaves the outer one standing.
pub fn with<R>(base: &str, f: impl FnOnce() -> R) -> R {
    let prior = GIVEN.with(|g| g.borrow_mut().replace(base.to_owned()));
    let out = f();
    GIVEN.with(|g| *g.borrow_mut() = prior);
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
        // set for the call alone, and an inner base given leaves the outer one standing after it (461 T38)
        assert_eq!(named(root), None);
        let outer = with("HEAD", || (with("", || named(root)), named(root)));
        assert_eq!(outer, (None, Some(git(root, &["rev-parse", "HEAD"]))));
    }
}
