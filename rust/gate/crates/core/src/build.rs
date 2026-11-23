//! THE BUILD AN ANSWER WAS JUDGED BY (feature 451 T197, gap audit item 9). WHY: `scripts/gates/l7r-gate.sh` builds the gate from the
//! clone's working tree, other builders' uncommitted code with it, and a triage, `record-checked` or `apply-edits` answer landed in the
//! common git directory saying nothing of the code that judged it (T184's first two triage runs ran T185 and T186's code before it
//! landed); a landing alone isolates its own code but trusted those answers. So the launcher writes, beside each binary it builds, the
//! build's id - `{"commit": <HEAD>, "dirty": {<path>: <blob id, or "deleted">}}`, the uncommitted files the binary is built from - and
//! hands it to the binary in `L7R_GATE_BUILD`; each answer records it, and a landing alone (`L7R_LAND_ALONE`) re-owes an answer whose
//! build held an uncommitted file that differs from the landing's own (`mixed`).

use serde_json::{Map, Value};

/// The variable the launcher hands the build's id in.
pub const ENV: &str = "L7R_GATE_BUILD";
/// Set in a landing alone's own `make land` (`land::alone::INNER`).
pub const LANDING: &str = "L7R_LAND_ALONE";
/// A dirty path's recorded blob where the file was deleted.
pub const DELETED: &str = "deleted";

#[cfg(any(test, feature = "testkit"))]
thread_local! {
    static GIVEN: std::cell::RefCell<Option<(Option<String>, bool)>> = const { std::cell::RefCell::new(None) };
}

/// The id of the build running now, `None` where the launcher handed none (a binary built before T197, or a test's).
#[must_use]
pub fn current() -> Option<Value> {
    parse(env(ENV).as_deref())
}

/// Is this a landing alone's own run?
#[must_use]
pub fn landing() -> bool {
    env(LANDING).is_some_and(|v| !v.is_empty())
}

#[cfg(any(test, feature = "testkit"))]
fn env(name: &str) -> Option<String> {
    GIVEN.with(|g| match &*g.borrow() {
        Some((build, _)) if name == ENV => build.clone(),
        Some((_, landing)) => landing.then(|| "1".to_owned()),
        None => None,
    })
}

#[cfg(not(any(test, feature = "testkit")))]
fn env(name: &str) -> Option<String> {
    std::env::var(name).ok()
}

/// `f` run with the build's id `build` handed in and a landing alone's flag `landing`, on this thread only (a test's environment).
#[cfg(any(test, feature = "testkit"))]
pub fn with<R>(build: Option<&str>, landing: bool, f: impl FnOnce() -> R) -> R {
    GIVEN.with(|g| *g.borrow_mut() = Some((build.map(str::to_owned), landing)));
    let out = f();
    GIVEN.with(|g| *g.borrow_mut() = None);
    out
}

/// A build's id read from the launcher's text: an object holding a `commit`, else `None`.
#[must_use]
pub fn parse(text: Option<&str>) -> Option<Value> {
    let v: Value = serde_json::from_str(text?).ok()?;
    v.get("commit").and_then(Value::as_str)?;
    Some(v)
}

/// The uncommitted files `build` was built from.
#[must_use]
pub fn dirty(build: &Value) -> Map<String, Value> {
    build
        .get("dirty")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default()
}

/// The paths of `build`'s uncommitted files whose recorded blob is not the one `blob_of` gives for the landing's tree ([`DELETED`]
/// where it holds none): the other builders' code it judged with. Empty for a clean build, and for an answer recorded before T197
/// (no build), which stands as it always did.
pub fn mixed(build: Option<&Value>, blob_of: &mut dyn FnMut(&str) -> String) -> Vec<String> {
    let mut out: Vec<String> = build
        .map(dirty)
        .unwrap_or_default()
        .into_iter()
        .filter(|(path, blob)| blob.as_str() != Some(blob_of(path).as_str()))
        .map(|(path, _)| path)
        .collect();
    out.sort();
    out
}

/// Is `build` the build running now, `now`: one commit, and the same uncommitted files at the same blobs.
#[must_use]
pub fn same(build: Option<&Value>, now: Option<&Value>) -> bool {
    match (build, now) {
        (Some(b), Some(n)) => b.get("commit") == n.get("commit") && dirty(b) == dirty(n),
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{current, landing, mixed, parse, same, with};

    #[test]
    fn a_build_id_is_read_compared_and_judged_against_the_landing() {
        assert_eq!(current(), None);
        assert!(!landing());
        let text = r#"{"commit": "c1", "dirty": {"rust/a.rs": "b1", "rust/b.rs": "deleted"}}"#;
        let got = with(Some(text), true, || (current(), landing()));
        assert!(got.1 && got.0.as_ref().is_some_and(|b| b["commit"] == "c1"));
        assert!(!with(None, false, landing));
        assert_eq!(parse(Some("[1]")), None);
        assert_eq!(parse(Some("not json")), None);
        assert_eq!(parse(None), None);
        let b = got.0.unwrap();
        let mut landing_blobs = |p: &str| {
            if p == "rust/a.rs" {
                "b1".to_owned()
            } else {
                "b9".to_owned()
            }
        };
        assert_eq!(
            mixed(Some(&b), &mut landing_blobs),
            vec!["rust/b.rs".to_owned()]
        );
        assert!(mixed(None, &mut landing_blobs).is_empty());
        assert!(mixed(Some(&json!({"commit": "c"})), &mut landing_blobs).is_empty());
        assert!(same(Some(&b), Some(&b.clone())));
        assert!(!same(Some(&b), Some(&json!({"commit": "c1"}))));
        assert!(!same(None, Some(&b)) && !same(Some(&b), None));
    }
}
