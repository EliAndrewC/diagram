//! THE BUILD AN ANSWER WAS JUDGED BY (feature 451 T197, gap audit item 9). WHY: `scripts/gates/l7r-gate.sh` builds the gate from the
//! clone's working tree, other builders' uncommitted code with it, and a triage, `record-checked` or `apply-edits` answer landed in the
//! common git directory saying nothing of the code that judged it (T184's first two triage runs ran T185 and T186's code before it
//! landed); a landing alone isolates its own code but trusted those answers. So the launcher writes, beside each binary it builds, the
//! build's id - `{"commit": <HEAD>, "dirty": {<path>: <blob id, or "deleted">}}`, the uncommitted files the binary is built from - and
//! hands it to the binary in `L7R_GATE_BUILD`; each answer records it, and a landing alone (`L7R_LAND_ALONE`) re-owes an answer whose
//! build held an uncommitted file that differs from the landing's own (`mixed`): from the file as any commit of the landing holds
//! it ([`Own`], T225).

use std::collections::{BTreeSet, HashMap};
use std::path::Path;

use serde_json::{Map, Value};

use crate::record::repo::git;

/// The variable the launcher hands the build's id in.
pub const ENV: &str = "L7R_GATE_BUILD";
/// Set in a landing alone's own `make land` (`land::alone::INNER`).
pub const LANDING: &str = "L7R_LAND_ALONE";
/// A dirty path's recorded blob where the file was deleted.
pub const DELETED: &str = "deleted";
/// The variable the launcher hands the tree it built the binary from in (`scripts/gates/l7r-gate.sh`).
pub const TREE: &str = "L7R_GATE_TREE";

/// A test's environment: the build's id, a landing alone's flag, the launcher's tree.
#[cfg(any(test, feature = "testkit"))]
type Given = (Option<String>, bool, Option<String>);

#[cfg(any(test, feature = "testkit"))]
thread_local! {
    static GIVEN: std::cell::RefCell<Option<Given>> = const { std::cell::RefCell::new(None) };
}

/// The id of the build running now, `None` where the launcher handed none (a binary built before T197, or a test's); its
/// uncommitted files as the launcher's tree holds them now ([`refreshed`]) where the launcher named its tree.
#[must_use]
pub fn current() -> Option<Value> {
    let build = parse(env(ENV).as_deref())?;
    Some(match env(TREE) {
        Some(tree) => refreshed(build, Path::new(&tree)),
        None => build,
    })
}

/// A STAMP IS TAKEN AT THE BUILD AND READ AT EVERY RUN (feature 451 T225, the round arbiter's
/// `ask:stamp-reads-committed-code-as-mixed`). WHY: the launcher writes the stamp only when it builds, so a binary built while
/// files were uncommitted kept calling them dirty after they were committed unchanged - no source moved, nothing rebuilt - and
/// every answer it recorded carried 30 "dirty" files that were HEAD's own (measured 2026-11-24, 49 record answers of 17:22-17:26).
/// So `build` is handed on without each dirty file whose stamped blob is the one `root`'s HEAD holds ([`DELETED`]: HEAD holds
/// none): that file is committed code now. One `git ls-tree` a call, none for a clean stamp.
#[must_use]
pub fn refreshed(mut build: Value, root: &Path) -> Value {
    let stamped = dirty(&build);
    if stamped.is_empty() {
        return build;
    }
    let mut args = vec!["ls-tree", "-z", "HEAD", "--"];
    args.extend(stamped.keys().map(String::as_str));
    let listed = git(root, &args);
    let head: HashMap<&str, &str> = listed
        .split('\0')
        .filter_map(|row| row.split_once('\t'))
        .filter_map(|(meta, path)| Some((path, meta.split(' ').nth(2)?)))
        .collect();
    let left: Map<String, Value> = stamped
        .into_iter()
        .filter(|(path, blob)| {
            blob.as_str() != Some(head.get(path.as_str()).copied().unwrap_or(DELETED))
        })
        .collect();
    build["dirty"] = Value::Object(left);
    build
}

/// Is this a landing alone's own run?
#[must_use]
pub fn landing() -> bool {
    env(LANDING).is_some_and(|v| !v.is_empty())
}

#[cfg(any(test, feature = "testkit"))]
fn env(name: &str) -> Option<String> {
    GIVEN.with(|g| match &*g.borrow() {
        Some((build, _, _)) if name == ENV => build.clone(),
        Some((_, _, tree)) if name == TREE => tree.clone(),
        Some((_, landing, _)) => landing.then(|| "1".to_owned()),
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
    given(build, landing, None, f)
}

/// [`with`], the launcher's tree `tree` handed in too.
#[cfg(any(test, feature = "testkit"))]
pub fn within<R>(build: &str, tree: &Path, f: impl FnOnce() -> R) -> R {
    given(
        Some(build),
        false,
        Some(tree.to_string_lossy().into_owned()),
        f,
    )
}

#[cfg(any(test, feature = "testkit"))]
fn given<R>(build: Option<&str>, landing: bool, tree: Option<String>, f: impl FnOnce() -> R) -> R {
    GIVEN.with(|g| *g.borrow_mut() = Some((build.map(str::to_owned), landing, tree)));
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

/// THE LANDING'S OWN COMMITTED CODE (feature 451 T225, the round arbiter's `ask:stamp-reads-committed-code-as-mixed`). WHY: the
/// mixed rule compared a stamped blob with `HEAD:path` alone, so when a later commit of the same landing edited a file, every
/// earlier answer of the day read as made by "other builders' uncommitted code" although the code that ran was a commit of this
/// landing - each of 2026-11-24's three gate fixes re-owed the answers before it (241 claims; 53 record answers; 191 claims and 49
/// record answers: 41 minutes of re-triage and re-checks, five landing refusals; for 49 of 49 record answers every stamped blob
/// was the path's blob at a commit of the delta or its base). A stamped blob is the landing's own where it is the path's blob at
/// HEAD, at a commit of the landing's delta, or at the delta's base; [`DELETED`] where one of those holds no such file. A blob none
/// of them holds is still another builder's uncommitted work: it was changed before it was committed, or never was.
///
/// THE DELTA is `base..HEAD`, the base `git merge-base HEAD origin/main` - the base `make land` diffs from (`origin/main...HEAD`,
/// `land.rs`), which the landing worktree, a worktree of the clone, resolves as the clone does; a merge of main moves the base and
/// leaves the clone's own commits in the delta. With no base to be found (no `origin/main`, no shared history) the delta is empty.
///
/// SINCE THE BUILD (the same task, its own decision): the stamp names the commit its binary was built at, and a file committed
/// unchanged after the build is a commit of `<that commit>..HEAD` wherever the landing's base stands. Without it the rule held
/// for one landing only: measured 2026-11-24, 189 rows of `dev/claims-index.json` carry a stamp of 1b064aa0de with seven dirty
/// files, five of which T225's own commit edits - once that landing is pushed its commits are behind the next landing's base,
/// and all 189 read mixed again at the next landing of any clone. A stamp whose commit git does not know adds nothing.
///
/// COST: a blob HEAD holds asks one `rev-parse` a path, as before; the first that HEAD does not hold asks `merge-base` and ONE
/// `git log --raw` over the whole delta (36 commits on 2026-11-24), kept for every later path and answer, then one `rev-parse` of
/// the base a path; one that all three miss asks one `git log --raw` a stamp commit (three distinct in the index that day).
pub struct Own<'a> {
    root: &'a Path,
    head: HashMap<String, String>,
    at_base: HashMap<String, String>,
    /// The base, and each path's blobs at the commits of the delta that changed it; `None` until first asked.
    delta: Option<(String, Blobs)>,
    /// By a stamp's commit, each path's blobs at the commits made since it.
    since: HashMap<String, Blobs>,
}

/// Each path's blobs at the commits of a range that changed it.
type Blobs = HashMap<String, BTreeSet<String>>;

impl<'a> Own<'a> {
    /// The landing whose tree is `root`.
    #[must_use]
    pub fn at(root: &'a Path) -> Self {
        Self {
            root,
            head: HashMap::new(),
            at_base: HashMap::new(),
            delta: None,
            since: HashMap::new(),
        }
    }

    /// `path`'s blob at `rev`, [`DELETED`] where it holds none.
    fn blob(root: &Path, rev: &str, path: &str) -> String {
        let b = git(
            root,
            &["rev-parse", "--verify", "--quiet", &format!("{rev}:{path}")],
        );
        match b.trim() {
            "" => DELETED.to_owned(),
            b => b.to_owned(),
        }
    }

    /// What each commit of `from..HEAD` left of each path it changed (a merge against each parent, `-m`, and no commit simplified
    /// away, `--full-history`); nothing where git does not know `from`.
    fn changed(root: &Path, from: &str) -> Blobs {
        let log = git(
            root,
            &[
                "-c",
                "core.quotePath=false",
                "log",
                "--raw",
                "--no-abbrev",
                "--no-renames",
                "--full-history",
                "-m",
                "--format=",
                "--end-of-options",
                &format!("{from}..HEAD"),
            ],
        );
        let mut blobs = Blobs::new();
        for (meta, path) in log.lines().filter_map(|l| l.split_once('\t')) {
            let blob = meta.split(' ').nth(3).unwrap_or_default();
            let blob = if blob.bytes().all(|b| b == b'0') {
                DELETED
            } else {
                blob
            };
            blobs
                .entry(path.to_owned())
                .or_default()
                .insert(blob.to_owned());
        }
        blobs
    }

    /// The base and the delta's blobs; an empty base, and nothing, where there is none.
    fn delta(root: &Path) -> (String, Blobs) {
        let base = git(root, &["merge-base", "HEAD", "origin/main"])
            .trim()
            .to_owned();
        let blobs = if base.is_empty() {
            Blobs::new()
        } else {
            Self::changed(root, &base)
        };
        (base, blobs)
    }

    /// Is `blob` what a commit holds at `path`: HEAD, a commit of the landing's delta, the delta's base, or a commit made since
    /// `built`, the commit of the build that stamped it?
    pub fn holds(&mut self, built: &str, path: &str, blob: &str) -> bool {
        let root = self.root;
        let head = self
            .head
            .entry(path.to_owned())
            .or_insert_with(|| Self::blob(root, "HEAD", path));
        if head == blob {
            return true;
        }
        let has = |blobs: &Blobs| blobs.get(path).is_some_and(|set| set.contains(blob));
        let (base, delta) = self.delta.get_or_insert_with(|| Self::delta(root));
        if has(delta) {
            return true;
        }
        if !base.is_empty()
            && self
                .at_base
                .entry(path.to_owned())
                .or_insert_with(|| Self::blob(root, base, path))
                == blob
        {
            return true;
        }
        has(self
            .since
            .entry(built.to_owned())
            .or_insert_with(|| Self::changed(root, built)))
    }
}

/// The paths of `build`'s uncommitted files that [`runs_in`] `closure` and whose recorded blob `own` - asked with the build's
/// commit, the path and the blob - says is not committed code of the landing ([`Own::holds`]): the other builders' code it judged
/// with. Empty for a clean build, and for an answer recorded before T197 (no build), which stands as it always did.
pub fn mixed(
    build: Option<&Value>,
    closure: &[&str],
    own: &mut dyn FnMut(&str, &str, &str) -> bool,
) -> Vec<String> {
    let commit = build
        .and_then(|b| b.get("commit"))
        .and_then(Value::as_str)
        .unwrap_or_default();
    let mut out: Vec<String> = build
        .map(dirty)
        .unwrap_or_default()
        .into_iter()
        .filter(|(path, _)| runs_in(path, closure))
        .filter(|(path, blob)| !blob.as_str().is_some_and(|b| own(commit, path, b)))
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
        closure, current, landing, mixed, parse, refreshed, runs_in, same, with, within, Own,
        CLAIMS, CLAIMS_BESIDE, CLAIMS_ROOTS, DELETED, RECORD, RECORD_BESIDE, RECORD_ROOTS,
    };
    use crate::record::testkit::{commit, git, put, record};

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
        let mut landing_blobs =
            |c: &str, p: &str, b: &str| c == "c1" && p == "rust/a.rs" && b == "b1";
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
        let mut other = |_: &str, _: &str, _: &str| false;
        assert_eq!(
            mixed(Some(&build), RECORD, &mut other),
            vec![check.to_owned()]
        );
        assert_eq!(
            mixed(Some(&build), CLAIMS, &mut other),
            vec![claims.to_owned()]
        );
    }

    /// The round arbiter's case (`ask:stamp-reads-committed-code-as-mixed`): a stamped blob an earlier commit of the landing's
    /// delta holds, and HEAD no longer, is the landing's own code; so is the base's, and a file deleted where a commit of the
    /// landing held none. A blob no commit holds is another builder's, and with no base to find the delta from only HEAD's counts.
    #[test]
    fn a_blob_an_earlier_commit_of_the_landing_holds_is_the_landing_s_own() {
        let dir = record("build-own");
        let root = dir.path();
        let (file, born, gone) = (
            "rust/gate/crates/owed/src/a.rs",
            "rust/gate/crates/owed/src/born.rs",
            "rust/gate/crates/owed/src/gone.rs",
        );
        let blob = |p: &str| git(root, &["rev-parse", &format!("HEAD:{p}")]);
        put(root, file, "base\n");
        put(root, gone, "base\n");
        let base = commit(root, "the base");
        git(root, &["update-ref", "refs/remotes/origin/main", &base]);
        let (at_base, gone_at_base) = (blob(file), blob(gone));
        put(root, file, "first\n");
        put(root, born, "born\n");
        std::fs::remove_file(root.join(gone)).unwrap();
        let _ = commit(root, "the landing's first commit");
        let (first, born_first) = (blob(file), blob(born));
        put(root, file, "second\n");
        put(root, born, "born, edited\n");
        put(root, gone, "back\n");
        let _ = commit(root, "the landing's second commit");
        let (head, never) = (blob(file), "0123456789012345678901234567890123456789");
        let build = json!({"commit": "c1", "dirty": {file: first, born: never}});
        let mut own = Own::at(root);
        assert_eq!(
            mixed(Some(&build), RECORD, &mut |c, p, b| own.holds(c, p, b)),
            vec![born.to_owned()]
        );
        for (path, blob, held) in [
            (file, head.as_str(), true),
            (file, first.as_str(), true),
            (file, at_base.as_str(), true),
            (file, never, false),
            (file, DELETED, false),
            (born, born_first.as_str(), true),
            // the base held no such file, and the first commit none of the other
            (born, DELETED, true),
            (gone, DELETED, true),
            (gone, gone_at_base.as_str(), true),
            ("rust/gate/crates/owed/src/never.rs", DELETED, true),
            ("rust/gate/crates/owed/src/never.rs", never, false),
        ] {
            assert_eq!(
                (path, blob, own.holds("c1", path, blob)),
                (path, blob, held)
            );
        }
        // the landing pushed, its commits behind the next one's base: the commits made since the build still hold the blob, and
        // a build of a commit git does not know, or made after them, is held to HEAD and the base
        let tip = git(root, &["rev-parse", "HEAD"]);
        git(root, &["update-ref", "refs/remotes/origin/main", &tip]);
        let mut own = Own::at(root);
        assert!(own.holds(&base, file, &first) && own.holds(&base, gone, DELETED));
        assert!(!own.holds(&base, file, never) && !own.holds(&base, file, &at_base));
        assert!(!own.holds("c1", file, &first) && !own.holds(&tip, file, &first));
        assert!(!own.holds("--all", file, &first) && own.holds(&tip, file, &head));
        let since = json!({"commit": base, "dirty": {file: first, born: never}});
        assert_eq!(
            mixed(Some(&since), RECORD, &mut |c, p, b| own.holds(c, p, b)),
            vec![born.to_owned()]
        );
        // no base to be found and no commit of the build's: HEAD alone, the rule before T225
        git(root, &["update-ref", "-d", "refs/remotes/origin/main"]);
        let mut own = Own::at(root);
        assert!(own.holds("c1", file, &head) && !own.holds("c1", file, &first));
        assert!(!own.holds("c1", file, &at_base) && own.holds(&base, file, &first));
        assert_eq!(
            mixed(Some(&build), RECORD, &mut |c, p, b| own.holds(c, p, b)),
            vec![file.to_owned(), born.to_owned()]
        );
    }

    /// A build's stamp is handed on without the files committed unchanged since it was built: the binary did not move, its stamp
    /// did (the ruling's second clause).
    #[test]
    fn a_stamp_drops_the_dirty_files_head_now_holds() {
        let dir = record("build-refreshed");
        let root = dir.path();
        put(root, "rust/a.rs", "a\n");
        put(root, "rust/b c.rs", "b\n");
        let _ = commit(root, "committed unchanged after the build");
        let blob = |p: &str| git(root, &["rev-parse", &format!("HEAD:{p}")]);
        let stamp = json!({"commit": "c1", "dirty": {
            "rust/a.rs": blob("rust/a.rs"), "rust/b c.rs": "b7", "rust/gone.rs": DELETED, "rust/new.rs": "b8"
        }});
        let want = json!({"commit": "c1", "dirty": {"rust/b c.rs": "b7", "rust/new.rs": "b8"}});
        assert_eq!(refreshed(stamp.clone(), root), want);
        assert_eq!(within(&stamp.to_string(), root, current), Some(want));
        let all = json!({"commit": "c1", "dirty": {"rust/a.rs": blob("rust/a.rs"), "rust/b c.rs": blob("rust/b c.rs")}});
        assert_eq!(refreshed(all, root), json!({"commit": "c1", "dirty": {}}));
        let clean = json!({"commit": "c1"});
        assert_eq!(refreshed(clean.clone(), root), clean);
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
