//! The queue's loop end to end over a scratch clone, its agent step a stand-in `claude` on the queue's `PATH` (a shell script that logs
//! its call and does what the files in its directory name: continue, fail once, fail always, or go quiet until the watch ends it): a
//! continuation, a retry, a `then` step's plan, a refusal that stops the queue, a stall resumed to its cap, the retries run out, and every
//! raise that ends the queue without `ALL DONE`. No real session starts.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::tests::{clone, ctx, executable, put, unset_var, write_brief};
use super::super::watch::Times;
use super::super::{plan, Ctx};
use super::{dispatcher, headless_env, ledger_rows, session_env, work, Run};
use crate::escape_log;

const STUB: &str = r#"#!/bin/sh
echo "$L7R_PAGE_SESSION|${L7R_KEY_CAP:-}|${L7R_FEATURE_DIRECTORY:-}|$L7R_DISPATCHER|${TMUX:-}|$1 $2" >> "$STUB/calls"
if [ -f "$STUB/stall" ]; then
  rm -rf "$STUB/proc"; mkdir -p "$STUB/proc/$$"
  printf 'claude\0--session-id\0%s\0' "$L7R_PAGE_SESSION" > "$STUB/proc/$$/cmdline"
  exec sleep 30
fi
if [ -f "$STUB/fail-always" ]; then echo '{"is_error": true}'; exit 0; fi
case "$*" in *continue.md*) if [ -f "$STUB/fail-once" ]; then rm "$STUB/fail-once"; echo 'limit reached' >&2; exit 1; fi;; esac
if [ -f "$STUB/continue" ]; then mv "$STUB/continue" "$L7R_CONTINUE"; fi
echo '{"subtype": "success"}'
"#;

struct World {
    _d: l7r_guard::shared::tempdir::TempDir,
    root: String,
    stub: PathBuf,
    home: String,
}

fn world(tag: &str) -> World {
    let d = l7r_gate_core::ci::fixtures::scratch(tag);
    let root = clone(&d);
    let stub = std::fs::canonicalize(&*d).unwrap().join("stub");
    executable(&stub.join("bin/claude"), STUB);
    let home = std::fs::canonicalize(&*d)
        .unwrap()
        .join("home")
        .to_string_lossy()
        .into_owned();
    World {
        _d: d,
        root,
        stub,
        home,
    }
}

fn environ(w: &World, path: &str) -> Vec<(String, String)> {
    [
        ("PATH", path.to_owned()),
        ("STUB", w.stub.to_string_lossy().into_owned()),
        ("TMUX", "/tmp/tmux-1".to_owned()),
        ("L7R_KEY_CAP", "99".to_owned()),
        ("CLAUDE_CODE_SESSION_ID", "own-sid".to_owned()),
    ]
    .map(|(k, v)| (k.to_owned(), v))
    .to_vec()
}

fn quick() -> Times {
    Times {
        check: 0.01,
        after: 0.05,
        returned: 60.0,
        retry_every: 0.01,
    }
}

fn stub_path(w: &World) -> String {
    format!("{}/bin:/usr/bin:/bin", w.stub.display())
}

/// The run log with each session id read back as `<n>`, in the order they first appear.
fn log_of(path: &Path) -> String {
    let mut text = std::fs::read_to_string(path).unwrap();
    let ids: Vec<String> = text
        .split_whitespace()
        .filter(|w| w.len() == 36 && w.chars().filter(|c| *c == '-').count() == 4)
        .map(str::to_owned)
        .collect();
    let mut seen: Vec<String> = Vec::new();
    for id in ids {
        if !seen.contains(&id) {
            seen.push(id);
        }
    }
    for (i, id) in seen.iter().enumerate() {
        text = text.replace(id, &format!("<{i}>"));
    }
    text
}

fn queue_of(c: &Ctx, items: &[String]) -> Vec<Value> {
    let mut out = String::new();
    plan(c, "/p", items, &mut out).unwrap()
}

#[test]
fn a_queue_continues_retries_plans_and_stops_on_a_refusal() {
    let w = world("work-queue");
    let mapdir = Path::new(&w.root).parent().unwrap().join(".session-clones");
    put(&mapdir.join("own-sid"), &w.root);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&w.root),
        command: String::new(),
    };
    let c = ctx(&w.root, &esc);
    let a = format!("{}/specs/1-x/briefs/w.md", w.root);
    put(Path::new(&a), &write_brief(1));
    put(
        &Path::new(&w.root).join("b.md"),
        "<!-- page-load: kind=assertions -->",
    );
    put(&w.stub.join("continue"), "<!-- page-load: kind=check -->");
    put(&w.stub.join("fail-once"), "");
    executable(
        &Path::new(&w.root).join("plan.sh"),
        &format!("#!/bin/sh\nprintf '\\n  {}/b.md  \\n\\n'\n", w.root),
    );
    executable(
        &Path::new(&w.root).join("stop.sh"),
        "#!/bin/sh\necho /missing.md\n",
    );
    let items = [
        a.clone(),
        format!("then:{}/plan.sh", w.root),
        format!("then:{}/stop.sh", w.root),
    ];
    let queue = queue_of(&c, &items);
    let run = Run {
        ctx: &c,
        environ: environ(&w, &stub_path(&w)),
        home: w.home.clone(),
        proc: w.stub.join("proc"),
        times: quick(),
    };
    let log = Path::new(&w.root).join(".git/page-sessions/run-x.log");
    work(&run, queue, &log.to_string_lossy()).unwrap();
    assert_eq!(
        log_of(&log),
        "started <0> w.md\nended <0> rc=0\ncontinued <0> -> <1>\nstarted <1> continue.md\n\
         failed <1> rc=1 - waiting 0 min (reset in 15), then resuming it (limit reached)\nended <1> rc=0\n\
         planned 1 session(s) from plan.sh\nstarted <2> b.md\nended <2> rc=0\nSTOPPED /missing.md: no such brief\nALL DONE\n"
    );
    let calls = std::fs::read_to_string(w.stub.join("calls")).unwrap();
    let rows: Vec<Vec<&str>> = calls.lines().map(|l| l.split('|').collect()).collect();
    assert_eq!(rows.len(), 4);
    // the write session and its continuation are told the key cap, the assertions brief too; none keeps the caller's TMUX or cap
    assert_eq!(
        (rows[0][1], rows[0][2], rows[0][3], rows[0][4]),
        ("10", "specs/1-x", "own-sid", "")
    );
    assert_eq!((rows[1][1], rows[3][1]), ("10", "10"));
    assert!(
        rows[2][5].starts_with("-p Continue the work")
            && rows[1][5].starts_with("-p You are a fresh session")
    );
    let index =
        std::fs::read_to_string(Path::new(&w.root).join(".git/page-sessions/index.txt")).unwrap();
    assert_eq!(index.lines().count(), 3);
    assert!(index.lines().next().unwrap().ends_with(&format!(" {a}")));
}

#[test]
fn a_stalled_session_is_resumed_to_its_cap_with_its_returned_reports() {
    let w = world("work-stall");
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&w.root),
        command: String::new(),
    };
    let c = ctx(&w.root, &esc);
    let b = format!("{}/c.md", w.root);
    put(Path::new(&b), "<!-- page-load: kind=check -->");
    put(&w.stub.join("stall"), "");
    let queue = queue_of(&c, std::slice::from_ref(&b));
    let sid = queue[0]["sid"].as_str().unwrap().to_owned();
    let projects = super::super::watch::projects_dir(&w.root, &w.home);
    put(
        &Path::new(&projects).join(format!("{sid}.jsonl")),
        &format!(
            "{}\n",
            json!({"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>r</task-notification>"})
        ),
    );
    let run = Run {
        ctx: &c,
        environ: environ(&w, &stub_path(&w)),
        home: w.home.clone(),
        proc: w.stub.join("proc"),
        times: quick(),
    };
    let log = Path::new(&w.root).join("run.log");
    work(&run, queue, &log.to_string_lossy()).unwrap();
    let text = log_of(&log);
    let lines: Vec<&str> = text.lines().collect();
    assert_eq!(lines.len(), 12, "{text}");
    assert_eq!(lines[1], "stalled <0> - idle 0 min, resuming it (1 of 8)");
    assert_eq!(
        lines[9],
        "stalled <0> - idle 0 min, resumed 8 times already; moving on"
    );
    assert_eq!(lines[10], "ended <0> rc=-15");
    let calls = std::fs::read_to_string(w.stub.join("calls")).unwrap();
    assert!(calls.lines().nth(1).unwrap().contains("returned.md"));
}

#[test]
fn a_session_that_fails_every_time_is_resumed_until_the_retries_run_out() {
    let w = world("work-retries");
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&w.root),
        command: String::new(),
    };
    let c = ctx(&w.root, &esc);
    let b = format!("{}/c.md", w.root);
    put(Path::new(&b), "<!-- page-load: kind=check -->");
    put(&w.stub.join("fail-always"), "");
    let queue = queue_of(&c, std::slice::from_ref(&b));
    let run = Run {
        ctx: &c,
        environ: environ(&w, &stub_path(&w)),
        home: w.home.clone(),
        proc: w.stub.join("proc"),
        times: quick(),
    };
    let log = Path::new(&w.root).join("run.log");
    work(&run, queue, &log.to_string_lossy()).unwrap();
    let text = log_of(&log);
    assert_eq!(
        text.matches("failed <0> rc=0 - waiting 0 min (reset in 15)")
            .count(),
        1
    );
    assert_eq!(text.matches(" - waiting 0 min ").count(), 44);
    assert!(text.ends_with("ended <0> rc=0\nALL DONE\n"));
}

#[test]
fn a_raise_ends_the_queue_without_all_done() {
    let w = world("work-raise");
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&w.root),
        command: String::new(),
    };
    let c = ctx(&w.root, &esc);
    let root = Path::new(&w.root);
    let b = format!("{}/c.md", w.root);
    put(Path::new(&b), "<!-- page-load: kind=check -->");
    let run_with = |path: &str| Run {
        ctx: &c,
        environ: environ(&w, path),
        home: w.home.clone(),
        proc: w.stub.join("proc"),
        times: quick(),
    };
    let run = run_with(&stub_path(&w));
    let log = root.join("run.log");
    let at = log.to_string_lossy().into_owned();
    let then = |script: &str| vec![json!({"then": script})];
    put(&root.join("plain.sh"), "#!/bin/sh\n");
    assert!(work(&run, then(&format!("{}/plain.sh", w.root)), &at).is_err());
    executable(&root.join("bytes.sh"), "#!/bin/sh\nprintf '\\377\\n'\n");
    assert!(work(&run, then(&format!("{}/bytes.sh", w.root)), &at)
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    put(&root.join("raise.md"), "## Your items\n- \n");
    executable(
        &root.join("raise.sh"),
        &format!("#!/bin/sh\necho {}/raise.md\n", w.root),
    );
    assert!(work(&run, then(&format!("{}/raise.sh", w.root)), &at)
        .unwrap_err()
        .starts_with("IndexError"));
    assert!(!std::fs::read_to_string(&log).unwrap().contains("ALL DONE"));
    // no `claude` on the queue's PATH; the index a directory; a run log that takes no write
    assert!(work(
        &run_with("/nowhere"),
        queue_of(&c, std::slice::from_ref(&b)),
        &at
    )
    .is_err());
    let _ = std::fs::remove_file(root.join(".git/page-sessions/index.txt"));
    std::fs::create_dir_all(root.join(".git/page-sessions/index.txt")).unwrap();
    assert!(work(&run, queue_of(&c, std::slice::from_ref(&b)), &at).is_err());
    std::fs::remove_dir(root.join(".git/page-sessions/index.txt")).unwrap();
    std::os::unix::fs::symlink("/dev/full", root.join(".git/page-sessions/index.txt")).unwrap();
    assert!(work(&run, queue_of(&c, std::slice::from_ref(&b)), &at)
        .unwrap_err()
        .contains("index.txt"));
    std::fs::remove_file(root.join(".git/page-sessions/index.txt")).unwrap();
    assert!(
        work(&run, queue_of(&c, std::slice::from_ref(&b)), "/dev/full")
            .unwrap_err()
            .starts_with("the run log")
    );
    assert!(work(&run, Vec::new(), "/no/such/dir/run.log").is_err());
    // a continuation over the cap stops the queue; one the count raises on ends it
    put(&w.stub.join("continue"), &write_brief(5));
    work(&run, queue_of(&c, std::slice::from_ref(&b)), &at).unwrap();
    assert!(std::fs::read_to_string(&log)
        .unwrap()
        .contains("STOPPED continue.md: it assigns 5 questions"));
    put(&w.stub.join("continue"), "## Your items\n- \n");
    assert!(work(&run, queue_of(&c, std::slice::from_ref(&b)), &at)
        .unwrap_err()
        .starts_with("IndexError"));
}

#[test]
fn the_dispatcher_and_each_session_s_environment() {
    let d = l7r_gate_core::ci::fixtures::scratch("work-dispatcher");
    let root = clone(&d);
    let mapdir = Path::new(&root).parent().unwrap().join(".session-clones");
    put(&mapdir.join("old"), &format!("{root}\n"));
    std::thread::sleep(std::time::Duration::from_millis(20));
    put(&mapdir.join(".newer"), &root);
    put(&mapdir.join("elsewhere"), "/other");
    std::fs::create_dir_all(mapdir.join("a-dir")).unwrap();
    assert_eq!(dispatcher(&root, ""), ".newer");
    assert_eq!(dispatcher(&format!("{root}/"), "old"), "old");
    assert_eq!(dispatcher(&root, "elsewhere"), ".newer");
    assert_eq!(dispatcher("/no/clones/here", "x"), "");
    assert_eq!(
        dispatcher(&d.join(".clones/none/.clones/x").to_string_lossy(), ""),
        ""
    );
    let parent = [("TMUX", "t"), ("TMUX_PANE", "%1"), ("A", "1")]
        .map(|(k, v)| (k.to_owned(), v.to_owned()))
        .to_vec();
    let env = headless_env(&parent, "disp");
    assert_eq!(
        env,
        BTreeMap::from([
            ("A".to_owned(), "1".to_owned()),
            ("L7R_DISPATCHER".to_owned(), "disp".to_owned())
        ])
    );
    let s = session_env(
        &env,
        &json!({"sid": "s", "log": "/l", "brief": "", "write": false}),
        "/",
    );
    assert_eq!(
        s.get("L7R_CONTINUE").map(String::as_str),
        Some("/l/continue.md")
    );
    assert!(!s.contains_key("L7R_KEY_CAP") && !s.contains_key("L7R_FEATURE_DIRECTORY"));
}

#[test]
fn the_ledger_rows_are_owed_only_where_the_root_has_its_gate() {
    let d = l7r_gate_core::ci::fixtures::scratch("work-ledger");
    let root = clone(&d);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&root),
        command: String::new(),
    };
    let c = ctx(&root, &esc);
    let run = Run {
        ctx: &c,
        environ: vec![("L7R_CACHE_OFF".to_owned(), "1".to_owned())],
        home: root.clone(),
        proc: PathBuf::from("/proc"),
        times: quick(),
    };
    ledger_rows(
        &run,
        &json!({"sid": "s", "brief": format!("{root}/specs/1-x/b.md")}),
    );
    assert!(!Path::new(&root).join("dev/review-ledger.md").exists());
    put(&Path::new(&root).join("scripts/gates/l7r-gate.sh"), "");
    for brief in [
        format!("{root}/specs/1-x/b.md"),
        "specs/2-y/b.md".to_owned(),
        "b.md".to_owned(),
    ] {
        ledger_rows(&run, &json!({"sid": "s", "brief": brief}));
    }
}
