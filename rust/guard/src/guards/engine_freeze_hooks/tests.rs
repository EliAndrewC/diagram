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
        self.agent_first(id, kind, r#"{"type":"user"}"#, last, extra);
    }

    /// An agent whose transcript opens on `first`, its dispatch prompt's record.
    fn agent_first(&self, id: &str, kind: &str, first: &str, last: &str, extra: &str) {
        std::fs::write(
            self.sub.join(format!("agent-{id}.meta.json")),
            format!("{{\"agentType\":\"{kind}\"{extra}}}"),
        )
        .unwrap();
        std::fs::write(
            self.sub.join(format!("agent-{id}.jsonl")),
            format!("{first}\n{last}\n"),
        )
        .unwrap();
    }

    /// A review dispatched to read `tree` (451 T164's prompt: `Review tree: <tree>, a worktree at <commit>`).
    fn reviewing(&self, id: &str, kind: &str, tree: &Path) {
        let prompt = format!(
            "UNIT: u\nClone: {} ... Review tree: {}, a worktree at abc123def4, the bundle's own work on HEAD",
            self.clone.display(),
            tree.display()
        );
        self.agent_first(
            id,
            kind,
            &json!({"type": "user", "message": {"content": prompt}}).to_string(),
            MID,
            "",
        );
    }

    /// The clone's review tree, a worktree beside it.
    fn review_tree(&self) -> PathBuf {
        let t = self.root.join("clone-review");
        std::fs::create_dir_all(&t).unwrap();
        std::fs::write(t.join(".git"), "gitdir: elsewhere\n").unwrap();
        t.canonicalize().unwrap()
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
    crate::shared::env::set("AGENT_STALE_S", "300"); // the test thread's own (feature 451 T32)
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": "/tmp/x"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

/// 451 T175: a review that reads its own review tree holds only an edit inside that tree; one with no tree on record holds every tree.
#[test]
fn a_review_reading_its_own_tree_holds_that_tree_alone() {
    let w = world("tree");
    let rt = w.review_tree();
    w.reviewing("b1", "building-review", &rt);
    let clone_edit = w.edit(&w.clone.join("rust/guard/src/x.rs"));
    assert!(clone_edit.is_empty(), "the clone is free: {clone_edit:?}");
    let got = w.edit(&rt.join("rust/phases/src/x.rs"));
    let held = refused(&got, "a map review is still running")
        && refused(&got, "  running: b1 building-review live");
    assert!(held, "the tree the review reads is held: {got:?}");
    w.agent("b2", "glyph-check", MID, "");
    let got = w.edit(&w.clone.join("x.rs"));
    let held = refused(&got, "  running: b2 glyph-check live") && !refused(&got, "b1");
    assert!(held, "a review naming no tree holds the clone: {got:?}");
}

#[test]
fn a_roll_in_the_clone_still_freezes_it_under_a_tree_reading_review() {
    let w = world("treeroll");
    let rt = w.review_tree();
    w.reviewing("b1", "building-review", &rt);
    w.roll(501, "l7r.diagram.tools.rust_gate", &w.clone);
    let got = w.edit(&w.clone.join("x.rs"));
    let held = refused(&got, "rebuilt under the rolls still to come")
        && refused(&got, "501 rust_gate rolling")
        && !refused(&got, "b1");
    assert!(held, "{got:?}");
}

#[test]
fn a_prompt_naming_no_usable_tree_holds_every_tree() {
    let w = world("notree");
    let rt = w.review_tree();
    let line = |content: serde_json::Value| {
        json!({"type": "user", "message": {"content": content}}).to_string()
    };
    w.agent_first("c1", "glyph-check", "not json", MID, "");
    let named = format!("Review tree: {}, a worktree at a", rt.display());
    let blocks = line(json!([{"type": "text", "text": named}]));
    w.agent_first("c2", "glyph-check", &blocks, MID, "");
    w.agent_first(
        "c3",
        "glyph-check",
        &line(json!("UNIT: u, no tree")),
        MID,
        "",
    );
    w.agent_first(
        "c4",
        "glyph-check",
        &line(json!(format!("Review tree: {}", rt.display()))),
        MID,
        "",
    );
    w.agent_first(
        "c5",
        "glyph-check",
        &line(json!("Review tree: clone-review, a worktree at a")),
        MID,
        "",
    );
    let gone = w.root.join("gone-review");
    w.agent_first(
        "c6",
        "glyph-check",
        &line(json!(format!(
            "Review tree: {}, a worktree at a",
            gone.display()
        ))),
        MID,
        "",
    );
    std::fs::write(
        w.sub.join("agent-c7.meta.json"),
        r#"{"agentType":"glyph-check"}"#,
    )
    .unwrap();
    std::fs::write(w.sub.join("agent-c7.jsonl"), "").unwrap();
    let all = live_reviews(&w.sub, 300);
    assert_eq!(all.len(), 7);
    assert!(all.iter().all(|r| r.tree.is_none()));
    let got = w.edit(&w.clone.join("x.rs"));
    let held = (1..=7).all(|n| refused(&got, &format!("  running: c{n} glyph-check live")));
    assert!(held, "{got:?}");
    w.reviewing("c8", "glyph-check", &rt);
    let mine = live_reviews(&w.sub, 300);
    assert_eq!(
        mine.iter()
            .filter_map(|r| r.tree.as_ref())
            .collect::<Vec<_>>(),
        [&rt]
    );
}

/// 451 T504, RED FIRST: the engine-edit question rides an earlier fresh gate call's proof in the same hook process (an Edit's
/// `preflight` and `edit-route` ask the same launcher): handed `L7R_GATE_FRESH` after an earlier call through it exited 0.
#[test]
fn the_engine_edit_question_rides_an_earlier_fresh_gate_call() {
    let w = world("fresh");
    crate::shared::env::set("L7R_GATE_TARGET", "/t504-target");
    let launcher = w.root.join("tree/scripts/gates/l7r-gate.sh");
    std::fs::write(
        &launcher,
        "[ \"$1\" = warm ] || [ \"${L7R_GATE_FRESH:-}\" = /t504-target/tool/l7r-gate ]\n",
    )
    .unwrap();
    w.agent("a1", "glyph-check", MID, "");
    let f = w.clone.join("lanes.py");
    assert!(w.edit(&f).is_empty());
    assert!(crate::shared::tool::ask_gate(&w.root, &launcher, &["warm"], "").ok());
    assert!(refused(&w.edit(&f), "a map review is still running"));
}
