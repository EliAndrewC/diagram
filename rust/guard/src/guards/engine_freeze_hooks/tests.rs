//! The guard on the suite's shapes (`tests/hooks/test-engine-freeze-hooks.sh`, replayed through the shim, is the verdict); the Python
//! answer is an `sh` stand-in that says yes while `yes` exists.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{decide, judge, live_reviews, live_rolls, Ctx};
use crate::guards::finished_run_hooks::runs::Procs;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

struct World {
    root: crate::shared::tempdir::TempDir,
    clone: PathBuf,
    sub: PathBuf,
}

fn world(tag: &str) -> World {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-freeze-{tag}"));
    let clone = root.join("clone");
    let sub = root.join("proj/sess/subagents");
    for d in [
        clone.join(".git"),
        sub.clone(),
        root.join("proc"),
        root.join("tree/scripts/gates"),
    ] {
        std::fs::create_dir_all(d).unwrap();
    }
    std::fs::write(root.join("yes"), "").unwrap();
    std::fs::write(
        root.join("tree/scripts/gates/l7r-gate.sh"),
        format!("[ -f {}/yes ]\n", root.display()),
    )
    .unwrap();
    World {
        clone: clone.canonicalize().unwrap(),
        sub,
        root,
    }
}

impl World {
    fn agent(&self, id: &str, kind: &str, last: &str, extra: &str) {
        std::fs::write(
            self.sub.join(format!("agent-{id}.meta.json")),
            format!("{{\"agentType\":\"{kind}\"{extra}}}"),
        )
        .unwrap();
        std::fs::write(
            self.sub.join(format!("agent-{id}.jsonl")),
            format!("{{\"type\":\"user\"}}\n{last}\n"),
        )
        .unwrap();
    }

    fn ctx(&self) -> Ctx {
        Ctx {
            procs: Procs {
                root: self.root.join("proc"),
                mine: 99_999,
            },
            stale: 300,
            tree: self.root.join("tree"),
        }
    }

    fn edit(&self, path: &Path) -> Vec<Answer> {
        let input = json!({"session_id": "t", "transcript_path": format!("{}/proj/sess.jsonl", self.root.display()), "tool_name": "Edit", "tool_input": {"file_path": path.to_string_lossy()}});
        let s = Session::from_input(&input);
        judge(
            &Event {
                name: "PreToolUse".to_owned(),
                input,
            },
            &s,
            &self.ctx(),
        )
    }

    fn roll(&self, pid: u32, name: &str, cwd: &Path) {
        let d = self.root.join("proc").join(pid.to_string());
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join("cmdline"), format!("python3\0-c\0x\0{name}\0")).unwrap();
        std::os::unix::fs::symlink(cwd, d.join("cwd")).unwrap();
    }
}

const MID: &str = r#"{"type":"assistant","message":{"stop_reason":"tool_use"}}"#;

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn an_engine_edit_waits_for_a_running_review() {
    let w = world("review");
    let f = w.clone.join("deep/er/lanes.py");
    assert!(w.edit(&f).is_empty());
    w.agent("a1", "glyph-check", MID, "");
    let got = w.edit(&f);
    assert!(
        refused(&got, "a map review is still running")
            && refused(&got, "  running: a1 glyph-check live 0s")
            && refused(&got, "once every review and roll")
    );
    assert!(!refused(&got, "stalled"));
}

#[test]
fn a_finished_stopped_or_unrelated_agent_does_not_freeze_it() {
    let w = world("finished");
    let f = w.clone.join("x.py");
    w.agent("a1", "source-reader", MID, "");
    w.agent(
        "a2",
        "glyph-check",
        r#"{"type":"assistant","message":{"stop_reason":"end_turn"}}"#,
        "",
    );
    w.agent("a3", "glyph-check", MID, ",\"finished\":true");
    w.agent("a4", "glyph-check", MID, "");
    std::fs::create_dir_all(w.root.join("proj/sess/stall-ack")).unwrap();
    std::fs::write(w.root.join("proj/sess/stall-ack/a4"), "").unwrap();
    std::fs::write(w.sub.join("agent-nometa.jsonl"), "").unwrap();
    std::fs::write(w.sub.join("notes.txt"), "").unwrap();
    assert!(w.edit(&f).is_empty());
}

#[test]
fn a_stalled_review_is_named_with_its_ack() {
    let w = world("stalled");
    w.agent("a2", "settlement-review", r#"{"type":"user"}"#, "");
    let f = std::fs::File::options()
        .write(true)
        .open(w.sub.join("agent-a2.jsonl"))
        .unwrap();
    f.set_modified(std::time::SystemTime::now() - std::time::Duration::from_secs(1200))
        .unwrap();
    let got = w.edit(&w.clone.join("x.py"));
    assert!(
        refused(&got, "a2 settlement-review stalled 1200s")
            && refused(
                &got,
                &format!(
                    "agent-stall-hooks.sh ack {}/proj/sess/subagents a2",
                    w.root.display()
                )
            )
    );
    assert_eq!(live_reviews(Path::new("/no/such"), 300).len(), 0);
}

#[test]
fn a_roll_in_this_clone_freezes_it_and_one_elsewhere_does_not() {
    let w = world("roll");
    let f = w.clone.join("x.py");
    w.roll(500, "l7r.diagram.tools.cohort", &w.root);
    assert!(w.edit(&f).is_empty());
    w.roll(501, "l7r.diagram.tools.rust_gate", &w.clone);
    w.roll(502, "unrelated", &w.clone);
    let got = w.edit(&f);
    assert!(
        refused(&got, "rebuilt under the rolls still to come")
            && refused(&got, "501 rust_gate rolling")
    );
    assert_eq!(live_rolls(&w.ctx().procs, &w.clone).len(), 1);
}

#[test]
fn what_is_not_the_guards_business_passes() {
    let w = world("pass");
    w.agent("a1", "glyph-check", MID, "");
    std::fs::remove_file(w.root.join("yes")).unwrap();
    assert!(w.edit(&w.clone.join("doc.md")).is_empty());
    std::fs::write(w.root.join("yes"), "").unwrap();
    assert!(w.edit(Path::new("/tmp/outside-any-tree/x.py")).is_empty());
    let run = |input: serde_json::Value| {
        let s = Session::from_input(&input);
        judge(
            &Event {
                name: "PreToolUse".to_owned(),
                input,
            },
            &s,
            &w.ctx(),
        )
    };
    assert!(run(json!({"tool_name": "Edit", "tool_input": {"file_path": "rel/x.py"}, "transcript_path": "t.jsonl"})).is_empty());
    assert!(run(json!({"tool_name": "Edit", "tool_input": {"file_path": "/a/x.py"}})).is_empty());
    let notebook = w.clone.join("n.ipynb");
    let no_session = run(
        json!({"tool_name": "NotebookEdit", "tool_input": {"notebook_path": notebook.to_string_lossy()}, "transcript_path": "not-a-transcript"}),
    );
    assert!(no_session.is_empty());
    std::env::set_var("AGENT_STALE_S", "300");
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": "/tmp/x"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
