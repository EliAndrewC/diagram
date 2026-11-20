//! The reviews' shared fixtures - a scratch git repository with the tools the port asks by command stubbed (the gate wrapper, the
//! finished-run probe, the bundle runner) - and the module root's own tests.

use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::json;

use super::*;

/// A fresh directory for one test.
pub(super) fn dir(name: &str) -> l7r_guard::shared::tempdir::Held<std::path::PathBuf> {
    let d = l7r_guard::shared::tempdir::TempDir::new(&format!("gate-reviews-{name}"));
    let root = std::fs::canonicalize(&d).unwrap();
    d.hold(root)
}

/// `sh -c cmd` in `root`, which must succeed.
pub(super) fn sh(root: &Path, cmd: &str) {
    let o = Command::new("sh")
        .arg("-c")
        .arg(cmd)
        .current_dir(root)
        .output()
        .unwrap();
    let said = String::from_utf8_lossy(&o.stderr);
    assert!(o.status.success(), "{cmd}: {said}");
}

/// Write `text` to `root/rel`, its directories made.
pub(super) fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// `git <args>` in `root`, which must succeed: started directly, not through `sh` (feature 449 T167, FR-008 - a shell's start is a
/// third of a commit's cost here, and the crate's slowest tests are their git calls).
fn git_ok(root: &Path, args: &[&str]) {
    let o = Command::new("git")
        .args(args)
        .current_dir(root)
        .output()
        .unwrap();
    let said = String::from_utf8_lossy(&o.stderr);
    assert!(o.status.success(), "git {args:?}: {said}");
}

/// Commit everything in `root`.
pub(super) fn commit(root: &Path, msg: &str) {
    git_ok(root, &["add", "-A"]);
    git_ok(root, &["commit", "-q", "--allow-empty", "-m", msg]);
}

/// The stubs of what the port asks by command (a feature's state is asked in process since feature 449 T118): the gate wrapper (`stamp --fresh` green while `.git/green` exists; `check spec-lint --figure-pattern` a figure with `s` or
/// `px`), the finished-run probe (`.git/live`'s lines) and the engine key. (The generation cache is asked in process since feature 449
/// T221, where `scripts/bundle_door.py`'s `is_current` was stubbed here.)
pub(super) fn tools(root: &Path) {
    // written by `install`, another process, never by this one: a script this process writes while another test thread forks is
    // held open by that child until its exec, and running it then fails `Text file busy`, which `gate_state` reads as a red gate
    // (feature 449 T196: `a_verdict_record_is_the_reviews_last_act` red in one `make static` of three)
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    l7r_gate_core::write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/bin/sh\nd=$(dirname \"$0\")/../..\ncase \"$1\" in hamlet|mode-a) echo \"$(cd \"$d\" && pwd)/.git/engine.bin\"; exit 0;; esac\nif [ \"$1\" = check ]; then [ -f \"$d/.git/no-pattern\" ] && { echo no pattern >&2; exit 1; }; echo '(?<![\\w.])\\d[\\d,]*(?:\\.\\d+)?\\s*(?:px|s)(?![\\w-])'; exit 0; fi\n[ -f .git/green ]\n",
    );
    put(
        root,
        "scripts/hooks/finished-run-hooks.sh",
        "cat \"$2/.git/live\" 2>/dev/null\n",
    );
    put(
        root,
        "Makefile",
        "engine-key:\n\t@cat .git/key 2>/dev/null || true\n",
    );
}

/// A repository with one commit, `origin/main` at it, and the stubbed tools (untracked): two git calls, the identity written into the
/// repository's config and `origin/main` written as its ref file in process (feature 449 T167, FR-008: the shell and the three other
/// git calls were six of the eight starts every test of the crate paid for its repository).
pub(super) fn repo(name: &str) -> l7r_guard::shared::tempdir::Held<PathBuf> {
    let d = dir(name);
    git_ok(&d, &["init", "-q"]);
    let config = d.join(".git/config");
    let mut text = std::fs::read_to_string(&config).unwrap();
    text.push_str("[user]\n\temail = t@t\n\tname = T Tester\n");
    std::fs::write(&config, text).unwrap();
    git_ok(&d, &["commit", "-q", "--allow-empty", "-m", "base"]);
    let head = std::fs::read_to_string(d.join(".git/HEAD")).unwrap();
    let branch = head.trim().strip_prefix("ref: ").unwrap().to_owned();
    let id = std::fs::read_to_string(d.join(".git").join(branch)).unwrap();
    put(&d, ".git/refs/remotes/origin/main", &id);
    put(
        &d,
        ".git/info/exclude",
        "scripts/\nMakefile\n.gencache/\n*.driver.json\n",
    );
    tools(&d);
    d
}

/// A map folder: its manifest with these ink classes; in the live pool its spec too, which makes it a hamlet to the pool walk (feature
/// 449 T220; a legacy folder with its manifest alone is a frozen exhibit; its `.gen.py` left with T221). A live hamlet's elements are
/// its Rust drawing's since 449 T230: `drawn` draws one.
pub(super) fn map(root: &Path, tree: &str, name: &str, classes: &[&str]) {
    if tree == "pool" {
        put(
            root,
            &format!("{tree}/hamlets/{name}/{name}.spec.json"),
            "{}",
        );
    }
    put(
        root,
        &format!("{tree}/hamlets/{name}/{name}.json"),
        &census(classes),
    );
}

fn census(classes: &[&str]) -> String {
    let census: serde_json::Map<String, serde_json::Value> = classes
        .iter()
        .map(|c| ((*c).to_owned(), json!(1)))
        .collect();
    json!({"ink_classes": census}).to_string()
}

/// A live hamlet with its tracked manifest and the Rust driver's current drawing, both holding these classes (449 T230).
pub(super) fn hamlet(root: &Path, name: &str, classes: &[&str]) {
    map(root, "pool", name, classes);
    drawn(root, name, classes);
}

/// The Rust driver's drawing of the live hamlet `name` as the generation cache publishes it (449 T230): its `.driver.json` holding these
/// classes as its ink census, the entry's meta naming it and the stand-in engine the stub launcher names, so the drawing is current.
pub(super) fn drawn(root: &Path, name: &str, classes: &[&str]) {
    drawn_as(root, name, &census(classes));
}

/// The driver's current drawing of `name` with this record (`drawn`'s, its text given).
pub(super) fn drawn_as(root: &Path, name: &str, record: &str) {
    put(
        root,
        &format!("pool/hamlets/{name}/{name}.driver.json"),
        record,
    );
    entry(
        root,
        "hamlets",
        name,
        "hamlet",
        ".spec.json",
        ".driver.json",
    );
}

/// A generated compound, drawn and current (449 T231): its program, its `.svg` tagging these kinds and the cache entry the Mode A
/// engine's stand-in names, as `drawn` does for a hamlet.
pub(super) fn compound(root: &Path, name: &str, kinds: &[&str]) {
    sheet(root, "pool", name, kinds);
    put(
        root,
        &format!("pool/compounds/{name}/{name}.compound.json"),
        "{}",
    );
    entry(root, "compounds", name, "mode-a", ".compound.json", ".svg");
}

/// The generation cache's entry for `pool/<tier>/<name>`, drawn by `engine` (the stand-in the stub launcher names) from its spec, with
/// its one artifact, so the drawing is served as current.
fn entry(root: &Path, tier: &str, name: &str, engine: &str, spec: &str, artifact: &str) {
    use l7r_gate_pool::cache::{engine as eng, entry, stat, table, DIR, ENTRIES, TABLE};
    use std::os::unix::fs::MetadataExt as _;
    let dir = root.join("pool").join(tier).join(name);
    let bin = root.join(".git/engine.bin");
    std::fs::write(&bin, "a stand-in engine").unwrap();
    let spec = dir.join(format!("{name}{spec}"));
    let artifact = format!("{name}{artifact}");
    let md = std::fs::metadata(dir.join(&artifact)).unwrap();
    let meta = entry::Meta {
        engine: engine.to_owned(),
        engine_id: eng::identity(&bin).unwrap().0,
        skip_render: false,
        spec: entry::Record {
            path: spec.display().to_string(),
            stat: stat::stat(&spec),
            hashed: 0,
            digest: l7r_guard::shared::sha256::hex(&std::fs::read(&spec).unwrap()),
        },
        artifacts: vec![entry::Artifact {
            name: artifact,
            size: md.size(),
            mtime: i128::from(md.mtime()) * 1_000_000_000 + i128::from(md.mtime_nsec()),
            ino: md.ino(),
        }],
        key: "k".to_owned(),
        reads: 0,
    };
    let at = root.join(DIR).join(ENTRIES).join(tier).join(name);
    std::fs::create_dir_all(&at).unwrap();
    std::fs::write(at.join(entry::META), meta.json()).unwrap();
    std::fs::write(root.join(DIR).join(TABLE), format!("{}\n", table::HEADER)).unwrap();
}

/// A Mode A sheet: its SVG tagging these kinds, in a tier the building types declaration declares (the pool walk tells a hand sheet by
/// it, feature 449 T220).
pub(super) fn sheet(root: &Path, tree: &str, name: &str, kinds: &[&str]) {
    put(
        root,
        l7r_gate_pool::DECLARATION,
        r#"[{"tier": "compounds"}]"#,
    );
    let tags = kinds.iter().fold(String::new(), |mut t, k| {
        let _ = std::fmt::Write::write_fmt(&mut t, format_args!("<g data-kind=\"{k}\"/>"));
        t
    });
    put(
        root,
        &format!("{tree}/compounds/{name}/{name}.svg"),
        &format!("<svg>{tags}</svg>"),
    );
}

/// The feature `.specify/feature.json` names, with a spec and these tasks.
pub(super) fn feature(root: &Path, name: &str, tasks: &str) {
    put(
        root,
        &format!("specs/{name}/spec.md"),
        "# x\n\n**Status**: Draft\n",
    );
    put(root, &format!("specs/{name}/tasks.md"), tasks);
    put(
        root,
        ".specify/feature.json",
        &json!({"feature_directory": format!("specs/{name}")}).to_string(),
    );
}

/// The clone's started task (`make task-start F=<feature> T=<task>`): its mark in the git common directory, as `task_start.rs` writes it.
pub(super) fn started(root: &Path, feature: &str, task: &str) {
    put(
        root,
        ".git/active-task",
        &format!("{}\n", json!({"feature": feature, "task": task})),
    );
}

/// The feature's event log: one event a row, `(seconds ago, ev, gm)`.
pub(super) fn events(root: &Path, feature: &str, rows: &[(i64, &str, bool)]) {
    let now = l7r_guard::shared::checks::now();
    let lines: String = rows
        .iter()
        .map(|(ago, ev, gm)| {
            #[expect(clippy::cast_precision_loss, reason = "a test's few seconds")]
            let at = now - *ago as f64;
            let secs = int_of(at);
            #[expect(clippy::cast_sign_loss, reason = "past the epoch")]
            let (year, month, day, hour, minute, second) =
                l7r_guard::shared::log::civil(secs as u64);
            let mut e =
                json!({"t": format!("{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z"), "ev": ev});
            if *gm {
                e["gm"] = json!(true);
            }
            e.to_string() + "\n"
        })
        .collect();
    put(root, &format!(".git/l7r-events/{feature}.jsonl"), &lines);
}

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

pub(super) fn run(a: &[&str]) -> crate::Reply {
    cli(&args(a))
}

#[test]
fn the_command_line_names_its_tool() {
    let r = run(&["nope"]);
    assert_eq!((r.code, r.stdout.as_str()), (2, ""));
    assert!(r.stderr.starts_with("usage: l7r-gate reviews"));
    assert_eq!(run(&[]).code, 2);
    let root = repo("cli");
    for tool in ["owed", "prereq", "checkpoint"] {
        let r = run(&[tool, "--nope"]);
        assert_eq!(r.code, 2, "{tool}");
    }
    let r = run(&["checkpoint", "hold", "--root", &root.to_string_lossy()]);
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
}

#[test]
fn the_helpers_read_as_python_did() {
    assert_eq!(py_path("./a/./b/"), PathBuf::from("a/b"));
    assert_eq!(py_path(""), PathBuf::from("."));
    assert_eq!(py_path("."), PathBuf::from("."));
    let d = dir("helpers");
    put(&d, "o.json", "{\"a\": 1}");
    put(&d, "l.json", "[1]");
    put(&d, "bad.json", "{");
    assert_eq!(read_object(Some(&d.join("o.json")))["a"], json!(1));
    assert!(read_object(Some(&d.join("l.json"))).is_empty());
    assert!(read_object(Some(&d.join("bad.json"))).is_empty());
    assert!(read_object(Some(&d.join("none.json"))).is_empty());
    assert!(read_object(None).is_empty());
    assert!((as_float(Some(&json!(2.5))) - 2.5).abs() < 1e-9);
    assert!((as_float(Some(&json!(true))) - 1.0).abs() < 1e-9);
    assert!((as_float(Some(&json!(" 3 "))) - 3.0).abs() < 1e-9);
    assert!(as_float(Some(&json!("x"))).abs() < 1e-9);
    assert!(as_float(None).abs() < 1e-9);
    assert_eq!(int_of(-2.5), -2);
    assert_eq!(local_time(0.0, "%Y").len(), 4);
    assert_eq!(
        iso_seconds(Some(&json!("1970-01-01T00:01:00Z"))),
        Some(60.0)
    );
    assert_eq!(iso_seconds(Some(&json!(5))), None);
    assert_eq!(iso_seconds(None), None);
    write_json(&d.join("w.json"), &json!({"k": [1, 2.0]})).unwrap();
    assert_eq!(
        std::fs::read_to_string(d.join("w.json")).unwrap(),
        "{\n \"k\": [\n  1,\n  2.0\n ]\n}\n"
    );
    assert!(git(&d, &["rev-parse", "HEAD"]).is_none());
    assert!(gitdir(&d).is_none());
    let r = repo("git");
    assert_eq!(gitdir(&r), Some(r.join(".git")));
    assert!(now() > 1.0e9);
}
