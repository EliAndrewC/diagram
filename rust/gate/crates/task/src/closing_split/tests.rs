//! `l7r-gate closing-split` (451 T311): the split the closing checks' embedded Python made, on the clone `tests/hooks/test-closing-checks.sh`
//! section 6 builds - two tasks mid-edit beside each other, another feature's task of the same number, a landed task's line - and its
//! feature's four sources, its two refusals and its command line.

use std::collections::BTreeSet;
use std::path::Path;

use l7r_gate_core::ci::fixtures::put;
use l7r_shared::builder_pool::Tree;
use serde_json::{json, Value};

use super::{cli, dirty_of, split, truthy, Split, World};
use crate::tests::{repo, root_of};

const NOW: &str = "2026-11-27T10:00:00Z";
const DIRTY: [&str; 11] = [
    "rust/mine/src/lib.rs",
    "rust/other/src/lib.rs",
    "docs/shared.md",
    "docs/landed.md",
    "rust/mine/src/new.rs",
    "rust/other/src/extra.rs",
    "docs/bash.md",
    "docs/sed.md",
    "docs/failed.md",
    "docs/both.md",
    "docs/reverted.md",
];

fn at(text: &str) -> f64 {
    l7r_shared::iso::parse(text).unwrap()
}

fn edit(t: &str, path: &str, task: &str, more: &str) -> String {
    format!("{{\"t\":\"{t}\",\"ev\":\"PostToolUse\",\"tool\":\"Edit\",\"cat\":\"edit\",\"path\":\"/c/{path}\",\"task\":\"{task}\"{more}}}\n")
}

fn bash(ev: &str, t: &str, writes: &str, task: &str) -> String {
    format!("{{\"t\":\"{t}\",\"ev\":\"{ev}\",\"tool\":\"Bash\",\"cat\":\"other tool\",\"writes\":[{writes}],\"task\":\"{task}\"}}\n")
}

/// Section 6's clone: the five base files committed 100 s before the edits, 451-x's T77 and T78 landed 60 s after them.
fn world<'a>(feature: &'a str, task: &'a str, log: &'a str) -> World<'a> {
    let n = NOW;
    let later = "2026-11-27T10:00:30.000Z";
    let mine = [
        edit(n, "rust/mine/src/lib.rs", "T86", ""),
        edit(n, "rust/other/src/lib.rs", "T84", ""),
        edit(n, "docs/shared.md", "T84", ""),
        edit(n, "docs/shared.md", "T86", ""),
        // a landed task's old line, a fallback line's, a PreToolUse line: none claims its file
        edit("2020-01-01T00:00:00.000Z", "docs/landed.md", "T50", ""),
        edit(n, "docs/bash.md", "T84", ",\"fallback\":true"),
        edit(n, "docs/bash.md", "T84", "").replace("PostToolUse", "PreToolUse"),
        // a line whose time does not parse, one with no task, one that is not JSON: none claims a file
        edit("never", "docs/bash.md", "T84", ""),
        edit(n, "docs/bash.md", "", ""),
        "{\"writes\": not json\n".to_owned(),
        // a Bash call's end and a failed end name their writes; a directory, a path outside the clone and a number claim nothing
        bash(
            "PostToolUse",
            n,
            "\"/c/docs/sed.md\",\"/c/rust/mine\",\"/elsewhere/docs/both.md\",7",
            "T84",
        ),
        bash("PostToolUseFailure", n, "\"/c/docs/failed.md\"", "T84"),
        // a Bash call's start names its writes too, and claims nothing
        bash("PreToolUse", n, "\"/c/docs/bash.md\"", "T84"),
        bash("PostToolUse", n, "\"/c/docs/both.md\"", "T84"),
        bash("PostToolUse", n, "\"/c/docs/both.md\"", "T86"),
        // newer than the file's last commit, older than its own task's landing: claims nothing
        bash("PostToolUse", later, "\"/c/docs/reverted.md\"", "T77"),
    ]
    .concat();
    World {
        root: "/c",
        common: Path::new("/c/.git"),
        feature,
        exported: "",
        task,
        pool: Vec::new(),
        marks: Vec::new(),
        dirty: DIRTY.iter().map(|s| (*s).to_owned()).collect(),
        log,
        events: vec![
            (
                "449-y".to_owned(),
                edit(n, "rust/other/src/extra.rs", "T86", ""),
            ),
            ("451-x".to_owned(), mine),
        ],
        now: at(NOW),
    }
}

/// The clone's log: the landing newest, then the base commit with its five files.
fn log() -> String {
    let now = at(NOW);
    format!(
        "@{} 451-x: T77 T78 ticked (make land)\n\n@{} base\n\nrust/mine/src/lib.rs\nrust/other/src/lib.rs\ndocs/shared.md\ndocs/landed.md\ndocs/reverted.md\n",
        now + 60.0,
        now - 100.0
    )
}

fn file<'a>(s: &'a Split, name: &str) -> &'a str {
    s.files
        .iter()
        .find(|(n, _)| *n == name)
        .map_or("", |(_, t)| t.as_str())
}

#[test]
fn the_caller_s_files_and_another_task_s_are_split_as_the_script_s_python_split_them() {
    let log = log();
    let s = split(&world("451", "T86", &log));
    assert_eq!(s.code, 0);
    assert_eq!(file(&s, "caller-files"), "docs/bash.md\ndocs/both.md\ndocs/landed.md\ndocs/reverted.md\ndocs/shared.md\nrust/mine/src/lib.rs\nrust/mine/src/new.rs\n");
    assert_eq!(file(&s, "others"), "docs/failed.md\tT84@451-x\ndocs/sed.md\tT84@451-x\nrust/other/src/extra.rs\tT86@449-y\nrust/other/src/lib.rs\tT84@451-x\n");
    assert_eq!(file(&s, "feature"), "451\n");
    assert_eq!(file(&s, "judged"), "7 files judged as T86's of 451-x, 3 of them its own edits name; 4 set apart as another task's\n");
    assert_eq!(s.stdout, "closing-checks: judged as T86's: 7 of the clone's 11 uncommitted files (3 its own edits name, 4 no task's edit); another task's, its red reported apart: 4; the task's feature: 451-x (from F=)\n  T84: docs/failed.md, docs/sed.md, rust/other/src/lib.rs\n  T86: rust/other/src/extra.rs\n");
    // a bundle's tasks judged as one task's; 449's T86 still another's
    let s = split(&world("451", "T86, T84", &log));
    assert_eq!(
        (s.code, file(&s, "others")),
        (0, "rust/other/src/extra.rs\tT86@449-y\n")
    );
    // a feature with no event log of its own is named as given
    let s = split(&world("449-y", "T86", &log));
    assert!(
        s.stdout
            .contains("the task's feature: 449-y (from F=)\n  T84: docs/both.md"),
        "{}",
        s.stdout
    );
}

#[test]
fn the_feature_is_f_then_specify_feature_then_the_pool_s_holder_then_this_tree_s_newest_mark() {
    let log = log();
    let from = |w: &World| {
        let s = split(w);
        let tail = s
            .stdout
            .split("the task's feature: ")
            .nth(1)
            .unwrap_or(&s.stdout);
        tail.lines().next().unwrap_or_default().to_owned()
    };
    let mut w = world("", "T86", &log);
    let tree = |t: &str, f: &str, tasks: &[&str]| Tree {
        tree: t.into(),
        feature: f.to_owned(),
        tasks: tasks.iter().map(|s| (*s).to_owned()).collect(),
        since: String::new(),
    };
    let mark = |t: &str, f: &str, utc: &str, more: Value| {
        let mut m = json!({"feature": f, "task": "T84", "tree": t, "utc": utc});
        m.as_object_mut()
            .unwrap()
            .extend(more.as_object().unwrap().clone());
        m
    };
    w.marks = vec![
        mark(
            "/c",
            "449-y",
            "2026-11-21T00:00:00Z",
            json!({"tasks": ["T84", "T86"]}),
        ),
        mark(
            "/c",
            "451-x",
            "2026-11-22T00:00:00Z",
            json!({"task": "T86"}),
        ),
        mark(
            "/c",
            "449-y",
            "2026-11-22T00:00:00Z",
            json!({"task": "T86"}),
        ),
        mark("/c", "450", "2026-11-23T00:00:00Z", json!({})),
        mark(
            "/elsewhere",
            "450",
            "2026-11-24T00:00:00Z",
            json!({"task": "T86"}),
        ),
        mark("/c", "", "2026-11-25T00:00:00Z", json!({"task": "T86"})),
        json!({"feature": "450", "task": "T86", "tree": "/c"}),
    ];
    // the newest of this tree's marks naming the task, the first of a tie
    assert_eq!(from(&w), "451-x (from this tree's start mark)");
    w.pool = vec![
        tree("/elsewhere", "450", &["T86"]),
        tree("/c", "450", &["T90"]),
        tree("/c", "", &["T86"]),
        tree("", "450", &["T86"]),
        tree("/c", "449", &["T86", "T90"]),
    ];
    assert_eq!(
        from(&w),
        "449-y (from the pool registry's holder of this tree)"
    );
    w.exported = "451-x";
    assert_eq!(from(&w), "451-x (from SPECIFY_FEATURE)");
    w.feature = "449";
    assert_eq!(from(&w), "449-y (from F=)");
    // none: refused, nothing written
    let mut w = world("", "T86", &log);
    w.marks = vec![mark(
        "/elsewhere",
        "449-y",
        "2026-11-22T00:00:00Z",
        json!({"task": "T86"}),
    )];
    let s = split(&w);
    assert_eq!((s.code, s.files.len()), (3, 0));
    assert_eq!(s.stdout, "closing-checks: REFUSED - T=T86 names no feature, and a task number alone is several features': no F=, no SPECIFY_FEATURE exported, /c/.git/builder-pool.json holds this tree for no such task, and this tree has no start mark of it. Run:\n  make closing-checks T=T86 F=<feature>\n");
}

#[test]
fn a_run_judging_none_of_the_task_s_own_files_is_refused_each_file_named_with_its_task_and_feature()
{
    let log = log();
    let s = split(&world("450", "T86", &log));
    assert_eq!(s.code, 3);
    assert!(file(&s, "feature").is_empty() && !file(&s, "others").is_empty());
    assert!(s.stdout.starts_with("closing-checks: REFUSED - no uncommitted file here is one T86's own edits name under feature 450 (from F=), while 7 of the clone's 11 are set apart as another task's:\n  T84@451-x: docs/both.md, docs/failed.md, docs/sed.md, docs/shared.md, rust/other/src/lib.rs\n  T86@449-y: rust/other/src/extra.rs\n  T86@451-x: docs/both.md, docs/shared.md, rust/mine/src/lib.rs\na run that judges none"), "{}", s.stdout);
    assert!(s.stdout.ends_with("run:\n  make closing-checks T=T86 F=<feature>\nor judge every file here as yours:\n  make closing-checks\n"));
    // past six files a task's list is cut, ` ...` after the sixth
    let mut w = world("450", "T84", "");
    w.dirty = (1..=7).map(|i| format!("d/{i}.md")).collect();
    let writes: Vec<String> = (1..=7).map(|i| format!("\"/c/d/{i}.md\"")).collect();
    w.events = vec![(
        "451-x".to_owned(),
        bash("PostToolUse", NOW, &writes.join(","), "T84"),
    )];
    let s = split(&w);
    assert!(s.stdout.contains("set apart as another task's:\n  T84@451-x: d/1.md, d/2.md, d/3.md, d/4.md, d/5.md, d/6.md ...\na run"), "{}", s.stdout);
}

#[test]
fn the_status_s_paths_and_python_s_truth() {
    let got = dirty_of("R  new.md\0old.md\0 M a.rs\0C  copy.md\0orig.md\0?? b.md\0\0");
    let want: BTreeSet<String> = ["new.md", "a.rs", "copy.md", "b.md"]
        .map(str::to_owned)
        .into();
    assert_eq!(got, want);
    let truth = [
        json!(null),
        json!(true),
        json!(false),
        json!(0),
        json!(2),
        json!(""),
        json!("x"),
        json!([]),
        json!([1]),
        json!({}),
        json!({"a": 1}),
    ];
    assert_eq!(
        truth.map(|v| truthy(&v)),
        [false, true, false, false, true, false, true, false, true, false, true]
    );
}

#[test]
fn the_command_reads_the_clone_and_writes_the_run_s_files() {
    let words = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let usage = cli(&words(&["only"]));
    assert_eq!(
        (
            usage.code,
            usage.stderr.starts_with("usage: l7r-gate closing-split")
        ),
        (2, true)
    );
    let dir = repo("closing-split");
    let root = root_of(&dir);
    let top = root.to_string_lossy().into_owned();
    put(&root, "dirty.md", "x\n");
    let events = dir.join("events");
    let line = edit(&crate::utc_text(crate::now_secs()), "dirty.md", "T5", "")
        .replace("/c/", &format!("{top}/"));
    put(&events, "9001-x.jsonl", &line);
    put(
        &events,
        ".hidden.jsonl",
        &edit(NOW, "dirty.md", "T9", "").replace("/c/", &format!("{top}/")),
    );
    put(&events, "notes.txt", "");
    let out = dir.join("run");
    std::fs::create_dir_all(&out).unwrap();
    let common = root.join(".git").to_string_lossy().into_owned();
    let (ev, o) = (
        events.to_string_lossy().into_owned(),
        out.to_string_lossy().into_owned(),
    );
    let got = cli(&words(&[&top, &ev, &common, "9001", "T5", &o, ""]));
    assert_eq!(
        (
            got.code,
            got.stdout.contains(
                "judged as T5's: 1 of the clone's 1 uncommitted files (1 its own edits name"
            )
        ),
        (0, true)
    );
    assert_eq!(
        std::fs::read_to_string(out.join("caller-files")).unwrap(),
        "dirty.md\n"
    );
    assert_eq!(
        std::fs::read_to_string(out.join("feature")).unwrap(),
        "9001\n"
    );
    // a run directory that cannot be written, and a root that is no repository: exit 1, the script's fallback
    let gone = dir.join("gone").to_string_lossy().into_owned();
    let unwritten = cli(&words(&[&top, &ev, &common, "9001", "T5", &gone, ""]));
    assert_eq!(
        (unwritten.code, unwritten.stdout.contains("caller-files")),
        (1, true)
    );
    let bare = dir.join("bare");
    std::fs::create_dir_all(&bare).unwrap();
    let b = bare.to_string_lossy().into_owned();
    let nogit = cli(&words(&[&b, &ev, &common, "9001", "T5", &o, ""]));
    assert_eq!(
        (
            nogit.code,
            nogit.stdout.starts_with("closing-checks: git status")
        ),
        (1, true)
    );
}
