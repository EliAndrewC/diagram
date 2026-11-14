//! The claim: every source of a taken number, each refusal, the renumber form and what the Python raised.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{commit, git, put, scratch};
use l7r_guard::shared::checks::resolved;
use serde_json::json;

use super::{cli, kind, py_int, Reply};

fn ask(args: &[&str], cwd: &Path) -> Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        cwd,
    )
}

/// A mirror with main's `specs/` (195 twice), a fetched `origin/main`, a sibling clone's unpushed claim and the ledger; the clone `a`.
fn mirror(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, PathBuf, PathBuf) {
    let dir = scratch(tag);
    let m = resolved(&dir);
    git(&m, &["init", "-q", "-b", "main"]);
    git(&m, &["config", "user.email", "t@t"]);
    git(&m, &["config", "user.name", "t"]);
    commit(&m, "specs/104-fetched/spec.md", "x\n");
    git(&m, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(&m, &["rm", "-qr", "specs/104-fetched"]);
    put(&m, "specs/100-one/spec.md", "x\n");
    put(&m, "specs/100-two/spec.md", "x\n");
    put(&m, "specs/notes.md", "x\n");
    put(&m, "specs/101-a-file", "x\n");
    put(&m, ".clones/b/specs/102-sibling/spec.md", "x\n");
    put(&m, ".clones/stray-file", "x\n");
    let ledger = "{\"number\": 103, \"slug\": \"ledgered\"}\n{torn\n\n\"no key here\"\n[\"other\"]\n{\"slug\": \"none\"}\n";
    put(&m, ".specify/feature-numbers.jsonl", ledger);
    let a = m.join(".clones/a");
    std::fs::create_dir_all(&a).unwrap();
    git(&a, &["init", "-q", "-b", "main"]);
    git(&a, &["config", "user.email", "t@t"]);
    git(&a, &["config", "user.name", "t"]);
    (dir, m, a)
}

#[test]
fn a_claim_takes_one_past_every_source_and_records_itself() {
    let (_dir, m, a) = mirror("claim-next");
    let peek = ask(&["--dry-run", "--", "new-thing"], &a);
    assert_eq!(peek.stdout, "105-new-thing\n");
    assert!(peek
        .stderr
        .contains("main holds 100 twice: 100-one, 100-two"));
    assert!(peek.stderr.contains(
        "DRY RUN - next is 105-new-thing  (main=100  origin/main=104  clones=102  ledger=103)"
    ));
    assert!(!a.join("specs/105-new-thing").exists());
    let done = ask(&["new-thing"], &a);
    assert_eq!((done.code, done.stdout.as_str()), (0, "105-new-thing\n"));
    assert!(a.join("specs/105-new-thing").is_dir());
    assert!(done.stderr.contains("export SPECIFY_FEATURE=105-new-thing\nexport SPECIFY_FEATURE_DIRECTORY=specs/105-new-thing\n"));
    assert!(done.stderr.contains("**Approved**: the GM, 20"));
    assert_eq!(
        std::fs::read_to_string(a.join(".specify/feature.json")).unwrap(),
        "{\n  \"feature_directory\": \"specs/105-new-thing\"\n}\n"
    );
    let ledger = std::fs::read_to_string(m.join(".specify/feature-numbers.jsonl")).unwrap();
    let last: serde_json::Value = serde_json::from_str(ledger.lines().last().unwrap()).unwrap();
    assert_eq!(
        (
            last["number"].clone(),
            last["slug"].clone(),
            last["clone"].clone()
        ),
        (json!(105), json!("new-thing"), json!("a"))
    );
    // the clone's own claim is a source of the next
    assert_eq!(ask(&["--dry-run", "--", "later"], &a).stdout, "106-later\n");
    // a slug in use anywhere is refused, the ledger's among them
    for used in ["new-thing", "sibling", "ledgered", "fetched", "one"] {
        let refused = ask(&[used], &a);
        assert_eq!(refused.code, 2, "{used}");
        assert!(refused.stderr.contains("is already in use"), "{used}");
    }
}

#[test]
fn the_renumber_form_moves_a_directory_tracked_or_not() {
    let (_dir, m, a) = mirror("claim-renumber");
    put(&a, "specs/050-tracked/spec.md", "x\n");
    git(&a, &["add", "-A"]);
    put(&a, "specs/051-loose/spec.md", "x\n");
    let moved = ask(&["--renumber", "specs/050-tracked/"], &a);
    assert_eq!((moved.code, moved.stdout.as_str()), (0, "105-tracked\n"));
    assert!(moved
        .stderr
        .contains("renumbered specs/050-tracked/ -> specs/105-tracked/"));
    assert!(a.join("specs/105-tracked/spec.md").is_file() && !a.join(".specify").exists());
    assert!(git(&a, &["status", "--short"]).contains("specs/105-tracked/spec.md"));
    assert_eq!(
        ask(&["--renumber=specs/051-loose"], &a).stdout,
        "106-loose\n"
    );
    let ledger = std::fs::read_to_string(m.join(".specify/feature-numbers.jsonl")).unwrap();
    assert!(ledger.contains("\"renumbered_from\": 51"));
    let gone = ask(&["--renumber", "specs/052-gone"], &a);
    assert_eq!(gone.code, 2);
    assert!(gone
        .stderr
        .contains("specs/052-gone is not an existing specs/NNN-<slug>/ directory in"));
    assert_eq!(ask(&["--renumber", "specs/nonumber"], &a).code, 2);
    // a move onto a file of the next number's name fails as the rename raised
    put(&a, "specs/060-blocked/spec.md", "x\n");
    put(&a, "specs/107-blocked", "x\n");
    assert_eq!(ask(&["--renumber", "specs/060-blocked"], &a).code, 1);
}

#[test]
fn each_refusal_writes_nothing() {
    let (_dir, m, a) = mirror("claim-refusals");
    let refused = |args: &[&str], cwd: &Path, says: &str| {
        let r = ask(args, cwd);
        assert_eq!(r.code, 2, "{args:?}: {r:?}");
        assert!(r.stderr.contains(says), "{args:?}: {}", r.stderr);
    };
    refused(&["Bad_Slug"], &a, "slug 'Bad_Slug' is not lower-case kebab");
    refused(&["a--b"], &a, "is not lower-case kebab");
    refused(&[], &a, "give exactly one of a slug");
    refused(
        &["x", "--renumber", "specs/100-one"],
        &a,
        "give exactly one of a slug",
    );
    refused(&["x", "--root", m.to_str().unwrap()], &a, "is the MIRROR");
    refused(&["x", "y"], &a, "unrecognized arguments: y");
    refused(&["--", "x", "y"], &a, "unrecognized arguments: y");
    refused(
        &["--lock-timeout", "soon", "x"],
        &a,
        "invalid float value: 'soon'",
    );
    refused(&["--bogus", "x"], &a, "unrecognized arguments: --bogus");
    // Python's `$` before a final newline: the slug passes the house-style test
    assert_eq!(ask(&["--dry-run", "nl\n"], &a).code, 0);
    // the lock held by another open file: refused after the timeout, naming it
    let lock =
        l7r_gate_core::record::repo::flock_within(&m.join(".specify/feature-numbers.lock"), 1.0)
            .unwrap();
    refused(&["--lock-timeout", "0.05", "x"], &a, "within 0.05s:");
    drop(lock);
    assert!(!a.join("specs").exists() && !a.join(".specify").exists());
}

#[test]
fn a_root_outside_the_clones_counts_itself_and_the_roots_resolve() {
    let (_dir, m, a) = mirror("claim-roots");
    let held = scratch("claim-outside");
    let outside = resolved(&held);
    put(&outside, "specs/300-mine/spec.md", "x\n");
    let peek = ask(
        &[
            "--dry-run",
            "--root",
            outside.to_str().unwrap(),
            "--main",
            m.to_str().unwrap(),
            "x",
        ],
        &a,
    );
    assert_eq!(peek.stdout, "301-x\n");
    // `--root` relative to the working directory, `--main` defaulting to the root itself outside `.clones`
    let rel = ask(&["--dry-run", "--root", ".", "x"], &outside);
    assert_eq!(rel.code, 2);
    assert!(rel.stderr.contains("is the MIRROR"));
    // no repository and no root: `git rev-parse` failed, which the Python raised on
    let bare = ask(&["x"], &outside);
    assert_eq!(bare.code, 1);
    assert!(bare.stderr.contains("Traceback") && bare.stderr.contains("CalledProcessError"));
    assert_eq!(ask(&["x"], Path::new("/nonexistent/x")).code, 1);
}

#[test]
fn what_the_python_raised_raises() {
    let (_dir, m, a) = mirror("claim-raises");
    let ledger = m.join(".specify/feature-numbers.jsonl");
    let raises = |text: &[u8], says: &str| {
        std::fs::write(&ledger, text).unwrap();
        let r = ask(&["--dry-run", "x"], &a);
        assert_eq!(r.code, 1, "{says}");
        assert!(r.stderr.contains(says), "{says}: {}", r.stderr);
    };
    raises(b"3\n", "argument of type 'int' is not iterable");
    raises(b"[\"number\"]\n", "list indices must be integers");
    raises(b"\"a number\"\n", "str indices must be integers");
    raises(b"{\"number\": \"x\"}\n", "invalid literal for int()");
    raises(b"{\"number\": null}\n", "int() argument must be");
    raises(&[0xff, b'\n'], "UnicodeDecodeError");
    std::fs::write(&ledger, "{\"number\": \" 1_10 \", \"slug\": 7}\n{\"number\": 120.9}\n{\"number\": true, \"slug\": null}\n").unwrap();
    assert_eq!(ask(&["--dry-run", "x"], &a).stdout, "121-x\n");
    // the ledger a directory: its append raised
    std::fs::remove_file(&ledger).unwrap();
    std::fs::create_dir(&ledger).unwrap();
    assert_eq!(ask(&["x"], &a).code, 1);
    std::fs::remove_dir(&ledger).unwrap();
    // the next directory's name taken by a file
    put(&a, "specs/106-taken", "x\n");
    assert_eq!(ask(&["taken"], &a).code, 1);
    // `.specify` a file, then `feature.json` a directory
    put(&a, ".specify", "x\n");
    assert_eq!(ask(&["spec-file"], &a).code, 1);
    std::fs::remove_file(a.join(".specify")).unwrap();
    std::fs::create_dir_all(a.join(".specify/feature.json")).unwrap();
    assert_eq!(ask(&["pointer-dir"], &a).code, 1);
    // the lock's directory cannot be made
    std::fs::remove_dir_all(m.join(".specify")).unwrap();
    put(&m, ".specify", "x\n");
    assert_eq!(ask(&["no-lock"], &a).code, 1);
}

#[test]
fn values_read_as_python_reads_them() {
    assert_eq!(py_int(&json!(true)), Ok(1));
    assert_eq!(py_int(&json!(-4)), Ok(-4));
    assert_eq!(py_int(&json!(7.9)), Ok(7));
    assert_eq!(py_int(&json!(" 12 ")), Ok(12));
    assert!(py_int(&json!([1])).is_err());
    let kinds: Vec<&str> = [
        json!(null),
        json!(false),
        json!(1.5),
        json!(1),
        json!("s"),
        json!([]),
        json!({}),
    ]
    .iter()
    .map(kind)
    .collect();
    assert_eq!(
        kinds,
        ["NoneType", "bool", "float", "int", "str", "list", "dict"]
    );
}
