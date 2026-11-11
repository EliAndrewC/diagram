//! The guard on a stand-in `/proc` and an `sh` stand-in for the gate's tree check, which says "unseen" while `unseen` exists
//! (`tests/hooks/test-gate-write-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge, top_of, Ctx};
use crate::guards::finished_run_hooks::runs::Procs;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

struct World {
    top: PathBuf,
    proc: PathBuf,
    _root: crate::shared::tempdir::TempDir,
}

fn world(tag: &str) -> World {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-gate-write-{tag}"));
    let top = root.join("tree");
    std::fs::create_dir_all(top.join("scripts/gates")).unwrap();
    std::fs::create_dir_all(top.join("l7r/x")).unwrap();
    std::fs::create_dir_all(root.join("proc")).unwrap();
    let t = top.canonicalize().unwrap();
    assert!(ask(
        Path::new("/"),
        "git",
        &["init", "-q", &t.to_string_lossy()],
        ""
    )
    .ok());
    crate::guards::write_executable(
        &t.join("scripts/gates/l7r-gate.sh"),
        &format!("#!/bin/sh\n[ -f {}/unseen ]\n", t.display()),
    );
    World {
        top: t,
        proc: root.join("proc"),
        _root: root,
    }
}

impl World {
    fn make(&self, pid: u32, program: &str, target: &str, cwd: &Path) {
        let d = self.proc.join(pid.to_string());
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join("cmdline"), format!("{program}\0{target}\0")).unwrap();
        std::os::unix::fs::symlink(cwd, d.join("cwd")).unwrap();
    }

    fn run(&self, tool: &str, input: &Value) -> Vec<Answer> {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": tool, "tool_input": input}),
        };
        let s = Session::from_input(&e.input);
        judge(
            &e,
            &s,
            &Ctx {
                procs: Procs {
                    root: self.proc.clone(),
                    mine: 99_999,
                },
                top: self.top.clone(),
            },
        )
    }

    fn bash(&self, cmd: &str) -> Vec<Answer> {
        self.run("Bash", &json!({"command": cmd}))
    }

    fn file(&self, rel: &str) -> String {
        self.top.join(rel).to_string_lossy().into_owned()
    }
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn nothing_is_refused_with_no_gate_running_here() {
    let w = world("idle");
    assert_eq!(top_of(Path::new("/proc/self")), Path::new("/proc/self"));
    assert_eq!(top_of(&w.top.join("l7r/x")), w.top);
    assert!(w.bash("git commit -qm x").is_empty());
    w.make(50, "make", "done", Path::new("/elsewhere"));
    w.make(51, "/usr/bin/python3", "make done", &w.top);
    assert!(w.bash("git commit -qm x").is_empty());
}

#[test]
fn a_running_gate_refuses_a_change_it_would_see() {
    let w = world("gate");
    w.make(60, "/usr/bin/make", "done", &w.top);
    let refusal = w.bash("git add -A");
    assert!(
        refused(&refusal, "while this tree's `make done` runs")
            && refused(&refusal, "make verify-wait")
    );
    assert!(refused(
        &w.bash("make tick F=1 T=T1"),
        "make tick (it writes a tracked record)"
    ));
    assert!(refused(
        &w.bash("make record-checked X=1"),
        "make record-checked"
    ));
    assert!(w.bash("tail -3 log").is_empty() && w.bash("make append LINE=x").is_empty());
    assert!(w.run("Read", &json!({"file_path": "/x"})).is_empty());
    assert!(w
        .run(
            "Edit",
            &json!({"file_path": "/outside/a.txt", "old_string": "a", "new_string": "b"})
        )
        .is_empty());
}

#[test]
fn what_the_gate_does_not_see_passes() {
    let w = world("unseen");
    w.make(60, "gmake", "--no-print-directory done", &w.top);
    std::fs::write(w.top.join("l7r/x/m.py"), "a a\n").unwrap();
    let edit = json!({"file_path": w.file("l7r/x/m.py"), "old_string": "a", "new_string": "b"});
    assert!(refused(&w.run("Edit", &edit), "an Edit of l7r/x/m.py"));
    assert!(refused(
        &w.bash("git commit -qm x"),
        "a change the gate sees"
    ));
    std::fs::write(w.top.join("unseen"), "").unwrap();
    assert!(w.run("Edit", &edit).is_empty());
    let all = json!({"file_path": w.file("l7r/x/m.py"), "old_string": "a", "new_string": "b", "replace_all": true});
    assert!(w.run("Edit", &all).is_empty());
    assert!(w
        .run(
            "Write",
            &json!({"file_path": w.file("dev/r.json"), "content": "{}"})
        )
        .is_empty());
    assert!(w.bash("git commit -qm x").is_empty());
    assert!(refused(
        &w.run("NotebookEdit", &json!({"notebook_path": w.file("n.ipynb")})),
        "an NotebookEdit of n.ipynb"
    ));
    assert!(refused(
        &w.run(
            "Edit",
            &json!({"file_path": w.file("gone.py"), "old_string": "a", "new_string": "b"})
        ),
        "an Edit of gone.py"
    ));
}

#[test]
fn a_cache_audit_refuses_engine_edits_and_commits() {
    let w = world("audit");
    w.make(70, "make", "cache-audit", &w.top);
    let got = w.bash("git commit -qm x");
    assert!(refused(&got, "`make cache-audit` runs") && refused(&got, "335cfa840"));
    assert!(refused(
        &w.run("Edit", &json!({"file_path": w.file("l7r/x/m.py")})),
        "an Edit of l7r/x/m.py"
    ));
    assert!(refused(
        &w.run("Write", &json!({"file_path": w.file("pool/p.json")})),
        "pool/p.json"
    ));
    assert!(w
        .run("Edit", &json!({"file_path": w.file("docs/x.md")}))
        .is_empty());
    assert!(w
        .run("Edit", &json!({"file_path": "/outside/l7r/x.py"}))
        .is_empty());
    assert!(w.bash("ls").is_empty() && w.run("Read", &json!({})).is_empty());
}

#[test]
fn the_escape_serves_both_and_needs_a_reason() {
    let w = world("escape");
    w.make(70, "make", "cache-audit", &w.top);
    assert!(w
        .bash("GATE_WRITE_OK=\"a deliberate commit beside it\" git commit -qm x")
        .is_empty());
    assert!(refused(
        &w.bash("git commit -qm x  # GATE_WRITE_OK"),
        "with no reason"
    ));
    let g = world("escape-gate");
    g.make(60, "make", "done", &g.top);
    assert!(g
        .bash("GATE_WRITE_OK=\"a deliberate fix for the gate\" git commit -qm x")
        .is_empty());
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
