//! Whole worlds reused through a run (feature 449 T179): each case still starts from a fresh world's state, `--fresh-worlds` keeps none,
//! and no world outlives the run - nor one whose checkout failed.

use serde_json::{json, Value};

use super::checkout::repo;
use super::Fx;
use crate::cases::load;
use crate::runner::{execute, Opts};

/// The named cases, each the same step - it reads and lists the checkout, then writes in it and beside it, and leaves the listing of
/// the worker's worlds (`work/`) in the root, where no comparison reads it - every side on a whole world at `old` (the working tree's overlay is
/// `reuse.rs`'s tests').
fn writing(old: &str, names: &[&str]) -> Value {
    let cases: Vec<Value> = names
        .iter()
        .map(|n| {
            // the shell's builtins alone: a program started was about 3 ms of a 13 ms step (FR-008's tenth of a second)
            let step = format!(
                "read -r t < top.txt; read -r x < a/x.txt; echo \"$t $x\"; echo *; \
                 echo more > top.txt; : > made.txt; : > ../out; echo ../../* > \"$ROOTDIR/work-{n}-$DIFF_RUN_SIDE\""
            );
            json!({"name": n, "steps": [["sh", "-c", step]]})
        })
        .collect();
    let mut v = Fx::base(&json!(cases));
    v["world"] = json!({
        "checkout": {"repo": "repo", "rev": "{REV}", "into": "c"},
        "cwd": "{WORLD}/c", "files": ["c"], "ignore": [".git"], "env": {"ROOTDIR": "{ROOT}", "GIT_TEMPLATE_DIR": "{ROOT}/templates"}
    });
    v["sides"]["old"]["vars"] = json!({"REV": old});
    v["sides"]["new"]["vars"] = json!({"REV": old});
    v
}

/// Each kept result's steps of `case`, its name put in for the case's own.
fn steps_of(run: &(Value, Vec<String>), case: &str) -> Vec<String> {
    let rows = run.0[1].as_array().unwrap().iter();
    rows.filter(|r| r[0] == case)
        .map(|r| r[1].to_string())
        .collect()
}

/// A run from an empty state: its report's rows and every kept result, the clock's fields taken out; and what `work/` holds after.
fn run(fx: &Fx, v: &Value, opts: &Opts) -> (Value, Vec<String>) {
    let state = fx.root().join("cases.diff-run");
    let _ = std::fs::remove_dir_all(&state);
    let cases = load(&fx.cases_file(v)).unwrap();
    let (path, _, _) = execute(&cases, opts, &mut Vec::new()).unwrap();
    let report: Value = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    let mut rows = report["cases"].clone();
    for row in rows.as_array_mut().unwrap() {
        for side in ["old", "new"] {
            row[side]["took_s"] = Value::Null;
        }
    }
    let mut results = Vec::new();
    // none where every side failed
    for e in std::fs::read_dir(state.join("results"))
        .into_iter()
        .flatten()
        .flatten()
    {
        let v: Value = serde_json::from_str(&std::fs::read_to_string(e.path()).unwrap()).unwrap();
        results.push(json!([
            v["case"],
            v["result"]["steps"],
            v["result"]["files"]
        ]));
    }
    results.sort_by_key(ToString::to_string);
    let left: Vec<String> = std::fs::read_dir(state.join("work"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    (json!([rows, results]), left)
}

/// The second case of each side runs in the world the first left, reset: its results are the first's, which ran in a world made fresh,
/// so a reset world gave a fresh world's results; and no world or copy outlives the run.
#[test]
fn a_reset_world_gives_the_fresh_world_s_results_and_none_outlives_the_run() {
    let fx = Fx::new();
    let (_repo, sha) = repo(&fx);
    // the worlds' clones without git's sample hooks, a dozen files fewer a world to write and copy (FR-008's tenth of a second)
    std::fs::create_dir_all(fx.root().join("templates")).unwrap();
    let reused = run(&fx, &writing(&sha, &["one", "two"]), &Opts::default());
    assert_eq!(steps_of(&reused, "one"), steps_of(&reused, "two"));
    let one = steps_of(&reused, "one").concat();
    assert!(!one.contains("more") && !one.contains("made.txt"), "{one}");
    // and the worlds were kept: the second case's side ran beside its world's copy
    let work = std::fs::read_to_string(fx.root().join("work-two-old")).unwrap();
    assert!(work.contains("old.git"), "{work}");
    assert_eq!(reused.1, Vec::<String>::new());
}

/// `--fresh-worlds` on the command line: every world made fresh and removed, none kept beside it.
#[test]
fn fresh_worlds_keep_no_world() {
    let fx = Fx::new();
    let (_repo, sha) = repo(&fx);
    std::fs::create_dir_all(fx.root().join("templates")).unwrap();
    let (r, _) = fx.run(&writing(&sha, &["one"]), &["--fresh-worlds"]);
    assert_eq!(r.code, 0, "{}{}", r.stdout, r.stderr);
    let work = std::fs::read_to_string(fx.root().join("work-one-old")).unwrap();
    assert_eq!(work.trim_end(), "../../old");
    let left = std::fs::read_dir(fx.root().join("cases.diff-run/work")).map_or(0, Iterator::count);
    assert_eq!(left, 0);
}

#[test]
fn a_whole_world_whose_checkout_fails_is_removed() {
    let fx = Fx::new();
    let _ = repo(&fx);
    let (report, left) = run(&fx, &writing("no-such-rev", &["one"]), &Opts::default());
    assert!(
        report.to_string().contains("checkout -q no-such-rev"),
        "{report}"
    );
    assert_eq!(left, Vec::<String>::new());
}
