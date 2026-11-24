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

/// THE CODE THAT CAN RUN IN AN ANSWER (feature 451 T224, the round arbiter's `ask:mixed-build-53-record-answers`). WHY: `l7r-gate` is
/// one executable holding every crate, and [`mixed`] counted any uncommitted file it was built from - a landing was refused and 49
/// record answers owed again when the dirty files were the claims crate's and a Markdown doc, code no `record` verb reaches. An
/// answer is mixed only by a dirty file its own verbs can run: the crates a closure names, read with [`runs_in`].
///
/// A RECORD answer (`record-checked`, `apply-edits`, the modal triage; its bundle `check-bundle`'s or `modal-bundle`'s): the `owed`
/// crate records and triages, the `bundle` crate builds the bundle, and their path dependencies (`cargo tree`, 2026-11-24:
/// core, pool, registry, research, `rust/guard/shared`) are what they call; `rust/gate/src` dispatches `record` and the `record`
/// crate each verb, and holds `apply_edits` and the entity table `rust/guard/shared` includes. The `record` crate's other
/// dependencies (archive, downloads, pages, semantic, trials, uncited) serve other verbs and are left out.
pub const RECORD: &[&str] = &[
    "rust/gate/crates/bundle",
    "rust/gate/crates/core",
    "rust/gate/crates/owed",
    "rust/gate/crates/pool",
    "rust/gate/crates/record",
    "rust/gate/crates/registry",
    "rust/gate/crates/research",
    "rust/gate/src",
    "rust/guard/shared",
];
/// The crates [`RECORD`] is the path-dependency closure of; what it holds beside that closure is [`RECORD_BESIDE`].
pub const RECORD_ROOTS: &[&str] = &["rust/gate/crates/bundle", "rust/gate/crates/owed"];
/// [`RECORD`]'s entries no `Cargo.toml` of its roots names: the two dispatchers.
pub const RECORD_BESIDE: &[&str] = &["rust/gate/crates/record", "rust/gate/src"];

/// A CLAIMS answer (a triage clear; its bundle is the claims crate's own): the `claims` crate and its path dependencies, the
/// dispatch in `rust/gate/src`, and the one file of the `record` crate that `rust/guard/shared` includes.
pub const CLAIMS: &[&str] = &[
    "rust/gate/crates/claims",
    "rust/gate/crates/core",
    "rust/gate/crates/owed",
    "rust/gate/crates/plan",
    "rust/gate/crates/pool",
    "rust/gate/crates/record/src/record/html5_entities.tsv",
    "rust/gate/crates/registry",
    "rust/gate/crates/research",
    "rust/gate/crates/reviews",
    "rust/gate/crates/tree",
    "rust/gate/src",
    "rust/guard/shared",
];
/// The crate [`CLAIMS`] is the path-dependency closure of.
pub const CLAIMS_ROOTS: &[&str] = &["rust/gate/crates/claims"];
/// [`CLAIMS`]'s entries no `Cargo.toml` of its root names: the dispatcher, and the file included from outside the closure.
pub const CLAIMS_BESIDE: &[&str] = &[
    "rust/gate/crates/record/src/record/html5_entities.tsv",
    "rust/gate/src",
];

/// Can the uncommitted file `path` of a build change what the verbs of `closure` do? In order:
/// - a file of the closure: yes - a Markdown file too (the `plan` crate includes some by `include_str!`), and a `tests.rs` too,
///   since whether a file is test-only is its `mod` line's `cfg`, not its name;
/// - a Markdown file anywhere else (`rust/gate/CLAUDE.md`): no, it cannot run, and [`closure::gaps`] fails on a file a crate of
///   the closure includes from outside it;
/// - a file of another crate of `rust/gate/crates` or of `rust/guard`: no, but for its `Cargo.toml` (a feature it turns on in a
///   shared crate changes that crate for every verb);
/// - anything else the launcher stamps (`rust/Cargo.toml`, `rust/Cargo.lock`, `.cargo/config.toml`, a file of `rust/gate` itself, a
///   path this rule does not know): yes, the build is theirs too.
#[must_use]
pub fn runs_in(path: &str, closure: &[&str]) -> bool {
    let under = |dir: &str| {
        path.strip_prefix(dir)
            .is_some_and(|rest| rest.is_empty() || rest.starts_with('/'))
    };
    if closure.iter().any(|dir| under(dir)) {
        return true;
    }
    if is_a(path, "md") {
        return false;
    }
    let anothers = under("rust/gate/crates") || under("rust/guard");
    !anothers || path.ends_with("/Cargo.toml")
}

/// Has the file `path` the extension `ext`?
fn is_a(path: &str, ext: &str) -> bool {
    std::path::Path::new(path)
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case(ext))
}

/// The paths of `build`'s uncommitted files that [`runs_in`] `closure` and whose recorded blob is not the one `blob_of` gives for
/// the landing's tree ([`DELETED`] where it holds none): the other builders' code it judged with. Empty for a clean build, and for
/// an answer recorded before T197 (no build), which stands as it always did.
pub fn mixed(
    build: Option<&Value>,
    closure: &[&str],
    blob_of: &mut dyn FnMut(&str) -> String,
) -> Vec<String> {
    let mut out: Vec<String> = build
        .map(dirty)
        .unwrap_or_default()
        .into_iter()
        .filter(|(path, _)| runs_in(path, closure))
        .filter(|(path, blob)| blob.as_str() != Some(blob_of(path).as_str()))
        .map(|(path, _)| path)
        .collect();
    out.sort();
    out
}

/// A closure table held to the tree (feature 451 T224): what the `Cargo.toml` files and the `include_str!` lines say it must name.
#[cfg(any(test, feature = "testkit"))]
pub mod closure {
    use std::collections::BTreeSet;
    use std::path::Path;

    /// `dir`/`rel` with its `..` steps taken, as a repository path.
    fn join(dir: &str, rel: &str) -> String {
        let mut parts: Vec<&str> = dir.split('/').collect();
        for step in rel.split('/') {
            if step == ".." {
                parts.pop();
            } else {
                parts.push(step);
            }
        }
        parts.join("/")
    }

    /// The crates the manifest `text` of the crate at `dir` names by `path` in a dependency table the built binary links: every
    /// table but `dev-dependencies`.
    #[must_use]
    pub fn deps(dir: &str, text: &str) -> Vec<String> {
        let mut out = Vec::new();
        let mut linked = false;
        for line in text.lines().map(str::trim) {
            if line.starts_with('[') {
                linked = line.contains("dependencies") && !line.contains("dev-dependencies");
            } else if linked {
                if let Some(rel) = line
                    .split("path = \"")
                    .nth(1)
                    .and_then(|r| r.split('"').next())
                {
                    out.push(join(dir, rel));
                }
            }
        }
        out
    }

    /// The `.rs` files under `dir`, as repository paths.
    fn sources(root: &Path, dir: &str, out: &mut Vec<String>) {
        let mut names: Vec<String> = std::fs::read_dir(root.join(dir))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .collect();
        names.sort();
        for name in names {
            let path = format!("{dir}/{name}");
            if root.join(&path).is_dir() {
                sources(root, &path, out);
            } else if super::is_a(&name, "rs") {
                out.push(path);
            }
        }
    }

    /// The files the sources of the crate at `dir` include by `include_str!` or `include_bytes!`.
    fn included(root: &Path, dir: &str) -> Vec<String> {
        let mut files = Vec::new();
        sources(root, &format!("{dir}/src"), &mut files);
        let mut out = Vec::new();
        for file in files {
            let text = std::fs::read_to_string(root.join(&file)).unwrap_or_default();
            let at = file.rsplit_once('/').map_or("", |(d, _)| d);
            for word in ["include_str!(", "include_bytes!("] {
                for rest in text.split(word).skip(1) {
                    if let Some(rel) = rest
                        .trim_start()
                        .strip_prefix('"')
                        .and_then(|r| r.split('"').next())
                    {
                        out.push(join(at, rel));
                    }
                }
            }
        }
        out
    }

    /// What is wrong with the closure `table` in the tree at `root`, one line each: a crate its `roots` reach by `path` that it
    /// does not name, an entry that is neither reached nor listed `beside`, and a file its crates include that does not
    /// [`super::runs_in`] it. Empty where the table follows the tree.
    #[must_use]
    pub fn gaps(root: &Path, table: &[&str], roots: &[&str], beside: &[&str]) -> Vec<String> {
        let mut reached: BTreeSet<String> = BTreeSet::new();
        let mut todo: Vec<String> = roots.iter().map(|r| (*r).to_owned()).collect();
        while let Some(dir) = todo.pop() {
            if reached.insert(dir.clone()) {
                let text =
                    std::fs::read_to_string(root.join(&dir).join("Cargo.toml")).unwrap_or_default();
                todo.extend(deps(&dir, &text));
            }
        }
        let mut out = Vec::new();
        for dir in &reached {
            if !table.contains(&dir.as_str()) {
                out.push(format!(
                    "{dir} is a path dependency of {} and the table does not name it: add it to the table in rust/gate/crates/core/src/build.rs",
                    roots.join(", ")
                ));
            }
            for file in included(root, dir) {
                if !super::runs_in(&file, table) {
                    out.push(format!(
                        "{file} is included by {dir} and does not count in the table: add it to the table and its BESIDE list in rust/gate/crates/core/src/build.rs"
                    ));
                }
            }
        }
        for entry in table {
            if !reached.contains(*entry) && !beside.contains(entry) {
                out.push(format!(
                    "{entry} is in the table and no Cargo.toml of {} reaches it: take it out, or list it in the table's BESIDE with its reason",
                    roots.join(", ")
                ));
            }
        }
        out
    }
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

    use super::{
        closure, current, landing, mixed, parse, runs_in, same, with, CLAIMS, CLAIMS_BESIDE,
        CLAIMS_ROOTS, RECORD, RECORD_BESIDE, RECORD_ROOTS,
    };

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
            mixed(Some(&b), RECORD, &mut landing_blobs),
            vec!["rust/b.rs".to_owned()]
        );
        assert!(mixed(None, RECORD, &mut landing_blobs).is_empty());
        assert!(mixed(Some(&json!({"commit": "c"})), RECORD, &mut landing_blobs).is_empty());
        assert!(same(Some(&b), Some(&b.clone())));
        assert!(!same(Some(&b), Some(&json!({"commit": "c1"}))));
        assert!(!same(None, Some(&b)) && !same(Some(&b), None));
    }

    /// The round arbiter's case (`ask:mixed-build-53-record-answers`): a record answer is not mixed by the claims crate's code or a
    /// Markdown doc, and is by the bundle crate's.
    #[test]
    fn a_dirty_file_mixes_only_the_answers_its_code_can_run_in() {
        let claims = "rust/gate/crates/claims/src/claims/index.rs";
        let check = "rust/gate/crates/bundle/src/record/bundle/check.rs";
        for (path, record, in_claims) in [
            (claims, false, true),
            (
                "rust/gate/crates/claims/src/claims/commands/tests.rs",
                false,
                true,
            ),
            ("rust/gate/CLAUDE.md", false, false),
            ("rust/gate/crates/owed/NOTES.md", true, true),
            ("rust/gate/crates/claims/NOTES.md", false, true),
            ("docs/guards.md", false, false),
            (check, true, false),
            ("rust/gate/crates/owed/src/record/owed/tests.rs", true, true),
            (
                "rust/gate/crates/record/src/record/apply_edits.rs",
                true,
                false,
            ),
            (
                "rust/gate/crates/record/src/record/html5_entities.tsv",
                true,
                true,
            ),
            ("rust/gate/crates/tree/src/delta.rs", false, true),
            ("rust/gate/crates/corex/src/lib.rs", false, false),
            ("rust/gate/src/lib.rs", true, true),
            ("rust/guard/shared/src/difflib.rs", true, true),
            ("rust/guard/src/main.rs", false, false),
            ("rust/gate/crates/claims/Cargo.toml", true, true),
            ("rust/guard/Cargo.toml", true, true),
            ("rust/gate/Cargo.toml", true, true),
            ("rust/Cargo.lock", true, true),
            (".cargo/config.toml", true, true),
            ("rust/gate/x.rs", true, true),
        ] {
            assert_eq!((path, runs_in(path, RECORD)), (path, record));
            assert_eq!((path, runs_in(path, CLAIMS)), (path, in_claims));
        }
        let build = json!({"commit": "c1", "dirty": {claims: "b1", "rust/gate/CLAUDE.md": "b2", check: "b3"}});
        let mut other = |_: &str| "b9".to_owned();
        assert_eq!(
            mixed(Some(&build), RECORD, &mut other),
            vec![check.to_owned()]
        );
        assert_eq!(
            mixed(Some(&build), CLAIMS, &mut other),
            vec![claims.to_owned()]
        );
    }

    /// The tables follow the tree: every crate `owed`, `bundle` and `claims` reach by `path`, and every file those include.
    #[test]
    fn the_closure_tables_name_what_the_manifests_reach() {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
        assert_eq!(
            closure::gaps(&root, RECORD, RECORD_ROOTS, RECORD_BESIDE),
            Vec::<String>::new()
        );
        assert_eq!(
            closure::gaps(&root, CLAIMS, CLAIMS_ROOTS, CLAIMS_BESIDE),
            Vec::<String>::new()
        );
    }

    /// A dependency added without the table following fails, as does an entry nothing reaches and an include from outside.
    #[test]
    fn a_dependency_added_without_the_table_following_is_a_gap() {
        let dir = crate::checks::scratch("build-closure");
        let root = dir.path();
        let write = |path: &str, text: &str| {
            let path = root.join(path);
            std::fs::create_dir_all(path.parent().unwrap()).unwrap();
            std::fs::write(path, text).unwrap();
        };
        write(
            "rust/gate/crates/a/Cargo.toml",
            "[package]\nname = \"a\"\n[dependencies]\nb = { path = \"../b\" }\nserde = { workspace = true }\n[dev-dependencies]\nd = { path = \"../d\" }\n[build-dependencies]\ns = { path = \"../../../guard/s\" }\n",
        );
        write(
            "rust/gate/crates/b/Cargo.toml",
            "[dependencies]\na = { path = \"../a\" }\n",
        );
        write(
            "rust/gate/crates/a/src/lib.rs",
            "const T: &str = include_str!(\"../../c/src/t.tsv\");\nconst U: &[u8] = include_bytes!(\n    \"u.bin\"\n);\nmacro_rules! m { () => { include_str!($x) } }\n",
        );
        write("rust/gate/crates/a/src/deep/notes.txt", "");
        write("rust/gate/crates/a/src/deep/x.rs", "");
        let roots = ["rust/gate/crates/a"];
        let whole = [
            "rust/gate/crates/a",
            "rust/gate/crates/b",
            "rust/guard/s",
            "rust/gate/crates/c/src/t.tsv",
        ];
        assert_eq!(
            closure::gaps(root, &whole, &roots, &["rust/gate/crates/c/src/t.tsv"]),
            Vec::<String>::new()
        );
        let got = closure::gaps(
            root,
            &["rust/gate/crates/a", "rust/gate/crates/d"],
            &roots,
            &[],
        );
        let starts: Vec<bool> = [
            "rust/gate/crates/c/src/t.tsv is included by rust/gate/crates/a and does not count",
            "rust/gate/crates/b is a path dependency of rust/gate/crates/a and the table does not name it",
            "rust/guard/s is a path dependency of",
            "rust/gate/crates/d is in the table and no Cargo.toml of rust/gate/crates/a reaches it",
        ]
        .iter()
        .zip(&got)
        .map(|(start, line)| line.starts_with(start))
        .collect();
        assert_eq!((starts, got.len()), (vec![true; 4], 4));
    }
}
