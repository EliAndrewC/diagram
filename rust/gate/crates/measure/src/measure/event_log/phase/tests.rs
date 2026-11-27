//! The shell's door to the Phase writer (feature 451 T153): each span a line in the one form, a bad span refused whole.

use l7r_shared::env::Rooted;
use serde_json::Value;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn lines(root: &std::path::Path) -> Vec<Value> {
    std::fs::read_dir(root.join(".git/l7r-events"))
        .unwrap()
        .flatten()
        .flat_map(|f| {
            std::fs::read_to_string(f.path())
                .unwrap_or_default()
                .lines()
                .map(str::to_owned)
                .collect::<Vec<_>>()
        })
        .map(|l| serde_json::from_str(&l).unwrap())
        .collect()
}

#[test]
fn each_span_writes_its_phase_line() {
    let d = crate::checks::scratch("measure-phase-door");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    let root = d.display().to_string();
    let env = Rooted::with(".", &[]);
    let words = [
        "--root",
        &root,
        "--src",
        "hooks",
        "--make",
        "done",
        "suite:10:12.5:0:test-a.sh",
        "suite:11:13:1",
    ];
    let r = super::cli(&args(&words), env.reader());
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    let got = lines(&d);
    let steps: Vec<(&str, &str, &str, i64, &str, &str)> = got
        .iter()
        .map(|l| {
            (
                l["src"].as_str().unwrap(),
                l["step"].as_str().unwrap(),
                l["t0"].as_str().unwrap(),
                l["code"].as_i64().unwrap(),
                l["make"].as_str().unwrap(),
                l["name"].as_str().unwrap_or(""),
            )
        })
        .collect();
    let want = [
        (
            "hooks",
            "suite",
            "1970-01-01T00:00:10.000Z",
            0,
            "done",
            "test-a.sh",
        ),
        ("hooks", "suite", "1970-01-01T00:00:11.000Z", 1, "done", ""),
    ];
    assert_eq!(steps, want);
    let ends: Vec<&str> = got.iter().map(|l| l["t1"].as_str().unwrap()).collect();
    let want_ends = ["1970-01-01T00:00:12.500Z", "1970-01-01T00:00:13.000Z"];
    assert_eq!(ends, want_ends);
}

/// 451 T414: a failed hook suite's span carries its kept log, relative to the common git directory, as the line's `log`.
#[test]
fn a_span_carries_its_kept_log() {
    let d = crate::checks::scratch("measure-phase-door-log");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    let root = d.display().to_string();
    let env = Rooted::with(".", &[]);
    let words = [
        "--root",
        &root,
        "--src",
        "hooks",
        "--make",
        "done",
        "suite:10:12:1:state-sync.sh:l7r-hooks-failed/20261126T182700Z-state-sync.sh-p7.log",
        "suite:11:13:0:test-a.sh",
    ];
    let r = super::cli(&args(&words), env.reader());
    assert_eq!(r.code, 0);
    let got: Vec<(String, Option<String>)> = lines(&d)
        .iter()
        .map(|l| (l["name"].to_string(), l.get("log").map(Value::to_string)))
        .collect();
    let log = "\"l7r-hooks-failed/20261126T182700Z-state-sync.sh-p7.log\"";
    let want = [
        ("\"state-sync.sh\"".to_owned(), Some(log.to_owned())),
        ("\"test-a.sh\"".to_owned(), None),
    ];
    assert_eq!(got, want);
}

#[test]
fn a_span_it_cannot_read_writes_nothing() {
    let d = crate::checks::scratch("measure-phase-door-bad");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    let root = d.display().to_string();
    let env = Rooted::with(".", &[]);
    for bad in [
        "suite:x:1:0",
        ":1:2:0",
        "suite:1:2",
        "suite:1:2:z",
        "suite:-1:2:0",
        "suite:1:inf:0",
    ] {
        let r = super::cli(
            &args(&["--root", &root, "--src", "hooks", bad]),
            env.reader(),
        );
        assert_eq!(r.code, 2, "{bad}");
    }
    let none = [
        super::cli(&args(&["--src", "hooks"]), env.reader()).code,
        super::cli(&args(&["--root", &root]), env.reader()).code,
    ];
    assert_eq!(none, [2, 2]);
    // no --make: the outermost make above the test, if any; the feature named
    let r = super::cli(
        &args(&[
            "--root",
            &root,
            "--src",
            "quick",
            "--feature",
            "999",
            "quick:1:2:0",
        ]),
        env.reader(),
    );
    assert_eq!(r.code, 0);
    let got = lines(&d);
    assert_eq!(got.len(), 1);
}

/// 451 T286: `--task` names the task the lines are filed under - `closing-checks.sh`'s launch line carries its caller's `T=`, as the
/// call's own `PreToolUse` line does, so the static-run count reads the two under one task.
#[test]
fn a_named_task_is_the_lines_task() {
    let d = crate::checks::scratch("measure-phase-door-task");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    let root = d.display().to_string();
    let env = Rooted::with(".", &[]);
    let words = [
        "--root",
        &root,
        "--src",
        "closing-checks",
        "--make",
        "closing-checks",
        "--task",
        "T7",
        "static-started:1:1:0",
    ];
    let r = super::cli(&args(&words), env.reader());
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    let got: Vec<(String, String)> = lines(&d)
        .iter()
        .map(|l| (l["step"].to_string(), l["task"].to_string()))
        .collect();
    assert_eq!(
        got,
        [("\"static-started\"".to_owned(), "\"T7\"".to_owned())]
    );
}
