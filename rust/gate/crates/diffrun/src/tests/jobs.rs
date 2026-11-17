//! Several workers (`--jobs`, feature 449 T173): the same report, kept results, lines and errors as one worker gives, each worker in a
//! world of its own, the workers clamped to the owed sides, and a count of zero or a non-number refused.

use std::path::Path;

use serde_json::{json, Value};

use super::Fx;
use crate::cases::load;
use crate::runner::{execute, Opts};

/// A case that writes its world's path outside the world (the kept result reads `<WORLD>`, so only this shows which world ran it), then
/// sleeps on its new side `ms` - longer the earlier the case, so the sides finish in another order than they start - and says hello, all
/// in one `sh` (a program a side costs about 2 ms of FR-008's tenth of a second).
fn timed(name: &str, ms: u32) -> Value {
    let note = format!(
        "echo \"$DIFF_RUN_WORLD\" > \"$ROOTDIR/seen/{name}-$DIFF_RUN_SIDE\"; [ \"$DIFF_RUN_SIDE\" = old ] || [ {ms} = 0 ] || sleep 0.0{ms:02}; exec \"$@\""
    );
    json!({"name": name, "steps": [["sh", "-c", note, "sh", "{CMD}", "hello", name]]})
}

/// Three timed cases, the first sleeping longest.
fn three() -> Value {
    Fx::base(&json!([timed("c0", 15), timed("c1", 5), timed("c2", 0)]))
}

/// A run of `jobs` workers from an empty state: its report and kept results with the clock's fields taken out, its lines with their
/// times masked, and the world each side ran in.
fn run(fx: &Fx, v: &Value, opts: &Opts) -> (Value, Vec<String>, Vec<(String, String)>) {
    let state = fx.root().join("cases.diff-run");
    let _ = std::fs::remove_dir_all(&state);
    let _ = std::fs::remove_dir_all(fx.root().join("seen"));
    std::fs::create_dir_all(fx.root().join("seen")).unwrap();
    let cases = load(&fx.cases_file(v)).unwrap();
    let mut lines = Vec::new();
    let (path, _, _) = execute(&cases, opts, &mut lines).unwrap();
    let mut report: Value = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    for k in ["utc", "wall_s"] {
        report[k] = Value::Null;
    }
    for row in report["cases"].as_array_mut().unwrap() {
        for side in ["old", "new"] {
            row[side]["took_s"] = Value::Null;
        }
    }
    let mut results = std::collections::BTreeMap::new();
    for e in std::fs::read_dir(state.join("results")).unwrap().flatten() {
        let mut v: Value =
            serde_json::from_str(&std::fs::read_to_string(e.path()).unwrap()).unwrap();
        v["utc"] = Value::Null;
        v["result"]["took_s"] = Value::Null;
        results.insert(e.file_name().to_string_lossy().into_owned(), v);
    }
    report["kept results"] = json!(results);
    let lines = String::from_utf8(lines)
        .unwrap()
        .lines()
        .map(|l| {
            let words: Vec<&str> = l
                .split_whitespace()
                .map(|w| {
                    if w.ends_with('s') && w[..w.len() - 1].parse::<f64>().is_ok() {
                        "T"
                    } else {
                        w
                    }
                })
                .collect();
            words.join(" ")
        })
        .collect();
    (report, lines, seen(fx.root()))
}

/// Each side's world, as `<case>-<side>` and the world's last part.
fn seen(root: &Path) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = std::fs::read_dir(root.join("seen"))
        .unwrap()
        .flatten()
        .map(|e| {
            let world = std::fs::read_to_string(e.path()).unwrap();
            let last = Path::new(world.trim())
                .file_name()
                .unwrap()
                .to_string_lossy()
                .into_owned();
            (e.file_name().to_string_lossy().into_owned(), last)
        })
        .collect();
    out.sort();
    out
}

fn jobs(n: usize) -> Opts {
    Opts {
        jobs: n,
        ..Opts::default()
    }
}

#[test]
fn four_workers_give_one_workers_report_kept_results_and_lines_each_in_its_own_world() {
    let fx = Fx::new();
    let v = three();
    let (one, one_lines, one_seen) = run(&fx, &v, &jobs(1));
    let (many, many_lines, many_seen) = run(&fx, &v, &jobs(4));
    assert_eq!(one, many);
    assert_eq!(one_lines, many_lines);
    assert_eq!(one_lines.len(), 3);
    // one worker: the serial worlds; four: each side in a worker's own, and more than one used
    assert!(
        one_seen.iter().all(|(_, w)| w == "old" || w == "new"),
        "{one_seen:?}"
    );
    assert_eq!(many_seen.len(), 6);
    let worlds: std::collections::BTreeSet<&String> = many_seen.iter().map(|(_, w)| w).collect();
    assert!(
        many_seen.iter().all(|(side, w)| {
            let which = side.rsplit('-').next().unwrap();
            w.strip_prefix(&format!("{which}-"))
                .is_some_and(|n| n.parse::<usize>().is_ok_and(|n| n < 4))
        }) && worlds.len() > 1,
        "{many_seen:?}"
    );
}

#[test]
fn the_workers_are_clamped_to_the_owed_sides_errors_name_the_serial_world_and_zero_or_a_non_number_is_refused(
) {
    let fx = Fx::new();
    let v = Fx::base(&json!([
        timed("a", 0),
        timed("b", 0),
        {"name": "c", "steps": [["{CMD}", "hello", "c"]], "env": {"FAILSETUP": "1"}}
    ]));
    // six sides owed of sixty-four workers asked for: no worker past the sixth; the failed setup's error names `work/old` and
    // `work/new`, a serial run's worlds, where a worker's own ran it
    let (rep, _, wide) = run(&fx, &v, &jobs(64));
    for (s, which) in ["old", "new"].iter().enumerate() {
        let error = rep["cases"][2]["errors"][s].as_str().unwrap();
        assert!(
            error.contains(&format!("cases.diff-run/work/{which}/out ")),
            "{error}"
        );
    }
    assert!(
        wide.iter().all(|(_, w)| w
            .rsplit('-')
            .next()
            .unwrap()
            .parse::<usize>()
            .is_ok_and(|n| n < 6)),
        "{wide:?}"
    );
    // one side owed: one worker, in the serial world
    let only = Opts {
        only: Some("b".to_owned()),
        jobs: 4,
        ..Opts::default()
    };
    let cases = load(&fx.cases_file(&v)).unwrap();
    std::fs::remove_dir_all(fx.root().join("seen")).unwrap();
    std::fs::create_dir_all(fx.root().join("seen")).unwrap();
    execute(&cases, &only, &mut Vec::new()).unwrap();
    assert_eq!(seen(fx.root()), [("b-new".to_owned(), "new".to_owned())]);
    for bad in [&["--jobs", "0"][..], &["--jobs", "four"], &["--jobs"]] {
        let (r, _) = fx.run(&v, bad);
        assert_eq!(r.code, 2);
        assert!(
            r.stderr
                .contains("--jobs takes the number of workers, a whole number 1 or more"),
            "{}",
            r.stderr
        );
        assert!(r.stderr.contains("JOBS=4"), "{}", r.stderr);
    }
    let (r, _) = fx.run(&v, &["--jobs", "2", "--only", "b"]);
    assert_eq!(r.code, 0, "{}", r.stderr);
}
