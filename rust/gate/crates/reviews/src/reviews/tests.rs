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

/// Commit everything in `root`.
pub(super) fn commit(root: &Path, msg: &str) {
    sh(
        root,
        &format!("git add -A && git commit -q --allow-empty -m '{msg}'"),
    );
}

/// The stubs of what the port asks by command (a feature's state is asked in process since feature 449 T118): the gate wrapper (`stamp --fresh` green while `.git/green` exists; `check spec-lint --figure-pattern` a figure with `s` or
/// `px`), the finished-run probe (`.git/live`'s lines), the bundle runner (`is_current`: current unless `<gen>.stale` exists), and
/// the engine key.
pub(super) fn tools(root: &Path) {
    put(
        root,
        "scripts/gates/l7r-gate.sh",
        "#!/bin/sh\nd=$(dirname \"$0\")/../..\nif [ \"$1\" = check ]; then [ -f \"$d/.git/no-pattern\" ] && { echo no pattern >&2; exit 1; }; echo '(?<![\\w.])\\d[\\d,]*(?:\\.\\d+)?\\s*(?:px|s)(?![\\w-])'; exit 0; fi\n[ -f .git/green ]\n",
    );
    sh(root, "chmod +x scripts/gates/l7r-gate.sh");
    put(
        root,
        "scripts/hooks/finished-run-hooks.sh",
        "cat \"$2/.git/live\" 2>/dev/null\n",
    );
    put(
        root,
        "scripts/bundle_door.py",
        "import json, os, sys\nfor line in sys.stdin:\n    ask = json.loads(line)\n    if os.path.exists(ask['args'][0] + '.broken'):\n        print(json.dumps({'error': 'Traceback: broken'}), flush=True)\n        continue\n    print(json.dumps({'ok': not os.path.exists(ask['args'][0] + '.stale')}), flush=True)\n",
    );
    put(
        root,
        "Makefile",
        "engine-key:\n\t@cat .git/key 2>/dev/null || true\n",
    );
}

/// A repository with one commit, `origin/main` at it, and the stubbed tools (untracked).
pub(super) fn repo(name: &str) -> l7r_guard::shared::tempdir::Held<PathBuf> {
    let d = dir(name);
    sh(
        &d,
        "git init -q && git config user.email t@t && git config user.name 'T Tester' && git commit -q --allow-empty -m base && git update-ref refs/remotes/origin/main HEAD",
    );
    put(&d, ".git/info/exclude", "scripts/\nMakefile\n");
    tools(&d);
    d
}

/// A map folder: its manifest with these ink classes, and its generator.
pub(super) fn map(root: &Path, tree: &str, name: &str, classes: &[&str]) {
    let census: serde_json::Map<String, serde_json::Value> = classes
        .iter()
        .map(|c| ((*c).to_owned(), json!(1)))
        .collect();
    put(
        root,
        &format!("{tree}/hamlets/{name}/{name}.json"),
        &json!({"ink_classes": census}).to_string(),
    );
    put(
        root,
        &format!("{tree}/hamlets/{name}/{name}.gen.py"),
        "# gen\n",
    );
}

/// A Mode A sheet: its SVG tagging these kinds.
pub(super) fn sheet(root: &Path, tree: &str, name: &str, kinds: &[&str]) {
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
