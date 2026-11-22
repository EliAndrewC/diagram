//! `builder-stop-hooks` (feature 451 T84): a builder of a started task stops only ready to land, each exit pinned.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{judge, Said};
use crate::protocol::{run, Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

/// A clone with feature 451's T84 started and open, a defined agent, and a builder `a1` of T84 dispatched by the session.
struct World {
    _dir: TempDir,
    tree: PathBuf,
    own: PathBuf,
    session: PathBuf,
}

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

impl World {
    fn new(tag: &str) -> Self {
        let dir = TempDir::new(&format!("guard-builder-stop-{tag}"));
        let tree = dir.path().join("clone");
        put(&tree.join(".claude/agents/spec-fidelity.md"), "agent\n");
        put(
            &tree.join("specs/451-x/tasks.md"),
            "- [x] T83 done\n- [ ] T84 the stop\n",
        );
        put(
            &tree.join(".git/task-starts.jsonl"),
            "{\"feature\": \"451-x\", \"task\": \"T83\"}\n{\"feature\": \"451-x\", \"task\": \"T84\"}\n",
        );
        let session = dir.path().join("p/sess.jsonl");
        put(&session, "");
        let own = dir.path().join("p/sess/subagents/agent-a1.jsonl");
        put(&own, "");
        let world = World {
            _dir: dir,
            tree,
            own,
            session,
        };
        world.meta(1, "451 T84: the stop");
        world
    }

    fn meta(&self, depth: u64, description: &str) {
        put(
            &self.own.with_extension("meta.json"),
            &json!({"agentType": "general-purpose", "description": description, "spawnDepth": depth}).to_string(),
        );
    }

    fn input(&self, said: &str) -> Value {
        json!({"hook_event_name": "SubagentStop", "agent_id": "a1", "agent_type": "general-purpose",
               "cwd": self.tree, "transcript_path": self.session, "last_assistant_message": said})
    }

    fn judged(&self, input: &Value, code: i32, out: &str) -> Said {
        let asked = |root: &Path, args: &[&str]| {
            assert_eq!(root, self.tree);
            assert_eq!(
                args,
                ["plan", "decided", self.tree.to_str().unwrap(), "451", "T84"]
            );
            (code, out.to_owned())
        };
        judge(input, &self.tree, None, &asked)
    }
}

const NOT_DECIDED: &str = "451-x T84: its plan section carries no current CLEAR verdict - run `make decide F=451 T=T84` and dispatch the MODE 4 review it prints yourself, then fix what it finds\n";

/// RED FIRST: the motivating case - a builder of a started task stopping with its section unreviewed is held, told the decide and the
/// review to dispatch; once the gate says decided it stops.
#[test]
fn a_builder_whose_section_is_not_decided_is_held_and_told_the_review() {
    let w = World::new("held");
    let said = w.judged(&w.input("done"), 1, NOT_DECIDED);
    assert!(matches!(&said, Said::Held(reason, detail)
            if reason.starts_with("builder-stop: 451-x T84: its plan section carries no current CLEAR verdict")
            && reason.contains("`make decide F=451 T=T84`, then dispatch the MODE 4 review it prints yourself (subagent_type spec-fidelity")
            && reason.contains("STOP_OK=\"<reason>\"")
            && detail.starts_with("451 T84: 451-x T84: its plan section")));
    assert_eq!(w.judged(&w.input("done"), 0, ""), Said::Quiet);
    assert_eq!(
        w.judged(&w.input("done"), 2, "usage"),
        Said::Passed("gate-unanswered", "451 T84: exit 2".to_owned())
    );
}

/// The stops that are no builder's of a started task pass before the gate is asked.
#[test]
fn every_other_stop_passes_unasked() {
    let w = World::new("others");
    let asks = std::cell::Cell::new(0);
    let never = |_: &Path, _: &[&str]| {
        asks.set(asks.get() + 1);
        (0, String::new())
    };
    let quiet = |input: &Value| judge(input, &w.tree, None, &never);
    let mut main = w.input("done");
    main.as_object_mut().unwrap().remove("agent_id");
    assert_eq!(quiet(&main), Said::Quiet);
    let mut odd = w.input("done");
    odd["agent_id"] = json!("../a1");
    assert_eq!(quiet(&odd), Said::Quiet);
    let mut defined = w.input("done");
    defined["agent_type"] = json!("spec-fidelity");
    assert_eq!(quiet(&defined), Said::Quiet);
    let mut nowhere = w.input("done");
    nowhere["cwd"] = json!("/");
    assert_eq!(judge(&nowhere, Path::new("/"), None, &never), Said::Quiet);
    let mut no_path = w.input("done");
    no_path["transcript_path"] = json!("");
    assert_eq!(quiet(&no_path), Said::Quiet);
    // the session's clone, when it is one, is read over the cwd's tree (451 T60)
    let mut moved = w.input("done");
    moved["cwd"] = json!("/");
    let mut own = w.input("done");
    own["agent_transcript_path"] = json!(w.own);
    let in_clone = |input: &Value| {
        judge(
            input,
            Path::new("/"),
            Some(w.tree.clone()),
            &|_: &Path, _: &[&str]| (1, NOT_DECIDED.to_owned()),
        )
    };
    assert!(matches!(in_clone(&moved), Said::Held(..)));
    assert!(matches!(in_clone(&own), Said::Held(..)));
    // a helper a builder dispatched, a brief naming no task, a task not started, a task ticked, a feature with no tasks.md
    w.meta(2, "451 T84 part 1: the lock");
    assert_eq!(quiet(&w.input("done")), Said::Quiet);
    w.meta(1, "the stop's measurement");
    assert_eq!(quiet(&w.input("done")), Said::Quiet);
    std::fs::remove_file(w.own.with_extension("meta.json")).unwrap();
    assert_eq!(quiet(&w.input("done")), Said::Quiet);
    for (tag, brief) in [
        ("not started", "451 T85: another"),
        ("ticked", "451 T83: done"),
        ("no feature", "452 T84: x"),
    ] {
        w.meta(1, brief);
        assert_eq!(quiet(&w.input("done")), Said::Quiet, "{tag}");
    }
    // the one ask is this line's own: no case above asked the gate
    assert_eq!(
        (never(Path::new("/"), &[]), asks.get()),
        ((0, String::new()), 1)
    );
}

/// The exits: `STOP_OK` with a reason, recorded, and without one held; past the context cap; a review in flight.
#[test]
fn the_escape_the_cap_and_a_review_in_flight_pass() {
    let w = World::new("exits");
    let asks = std::cell::Cell::new(0);
    let never = |_: &Path, _: &[&str]| {
        asks.set(asks.get() + 1);
        (0, String::new())
    };
    let said = judge(
        &w.input("my handoff is written. STOP_OK=\"the context cap is near\""),
        &w.tree,
        None,
        &never,
    );
    assert_eq!(
        said,
        Said::Passed("stop-ok", "451 T84: the context cap is near".to_owned())
    );
    assert!(
        matches!(judge(&w.input("STOP_OK=\"x\""), &w.tree, None, &never), Said::NoReason(t) if t.contains("STOP_OK with no reason given"))
    );
    // past the cap: its last model call's context over CONTEXT_CAP_TOKENS
    let row = json!({"type": "assistant", "message": {"id": "m", "usage": {"input_tokens": 310_000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 5}}});
    put(&w.own, &format!("{row}\n"));
    assert_eq!(
        judge(&w.input("done"), &w.tree, None, &never),
        Said::Passed("past-cap", "451 T84: 310000 tokens".to_owned())
    );
    // its spec-fidelity review launched, no notification yet: passed, the notification wakes it
    let call = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tu1", "name": "Agent", "input": {"subagent_type": "spec-fidelity", "prompt": "MODE 4"}}]}});
    let other = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tu2", "name": "Agent", "input": {"subagent_type": "Explore"}}]}});
    let back = json!({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": "tu1", "content": [{"type": "text", "text": "Async agent launched successfully. agentId: abc123 (internal)"}]},
        {"type": "tool_result", "tool_use_id": "tu2", "content": "agentId: zzz"}]}});
    put(&w.own, &format!("{call}\n{other}\nnot json\n{back}\n"));
    assert_eq!(
        judge(&w.input("done"), &w.tree, None, &never),
        Said::Passed("review-in-flight", "451 T84: abc123".to_owned())
    );
    // the one ask is this line's own: no exit above asked the gate
    assert_eq!(
        (never(Path::new("/"), &[]), asks.get()),
        ((0, String::new()), 1)
    );
    let woke = json!({"type": "user", "message": {"content": "<task-notification>\n<task-id>abc123</task-id>\n"}});
    put(&w.own, &format!("{call}\n{back}\n{woke}\n"));
    assert!(matches!(
        w.judged(&w.input("done"), 1, NOT_DECIDED),
        Said::Held(..)
    ));
}

/// Through the hook: a held stop answers `decision: block` from the gate's own words (a stand-in gate script), and the main session's
/// stop is not held.
#[test]
fn the_hook_blocks_the_stop_through_the_gate_script() {
    let w = World::new("hook");
    put(
        &w.tree.join("scripts/gates/l7r-gate.sh"),
        &format!("printf '%s' '{}'\nexit 1\n", NOT_DECIDED.replace('`', "'")),
    );
    let mut e = Event {
        name: "SubagentStop".to_owned(),
        input: w.input("done"),
    };
    let session = Session::with_env(&e.input, |_| None);
    let said = (super::GUARD.decide)(&e, &session);
    assert!(matches!(&said[..], [Answer::StopBlock(r)] if r.contains("make decide F=451 T=T84")));
    let reply = run(&mut e, &[super::GUARD]);
    let decision = serde_json::from_str::<Value>(&reply.stdout).unwrap()["decision"].clone();
    assert_eq!(decision, json!("block"));
    for (said, rule) in [
        ("STOP_OK=\"the context cap is near\"", "stop-ok"),
        ("STOP_OK=\"x\"", "no reason"),
    ] {
        let e = Event {
            name: "SubagentStop".to_owned(),
            input: w.input(said),
        };
        let answers = (super::GUARD.decide)(&e, &Session::with_env(&e.input, |_| None));
        assert_eq!(answers.is_empty(), rule == "stop-ok", "{rule}");
    }
    // past the cap: passed and recorded, the gate not asked
    let row = json!({"type": "assistant", "message": {"id": "m", "usage": {"input_tokens": 310_000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 5}}});
    put(&w.own, &format!("{row}\n"));
    let e = Event {
        name: "SubagentStop".to_owned(),
        input: w.input("done"),
    };
    assert!((super::GUARD.decide)(&e, &Session::with_env(&e.input, |_| None)).is_empty());
    let mut main = w.input("done");
    main.as_object_mut().unwrap().remove("agent_id");
    let e = Event {
        name: "SubagentStop".to_owned(),
        input: main,
    };
    assert!((super::GUARD.decide)(&e, &Session::with_env(&e.input, |_| None)).is_empty());
}

/// 449 T268 (found, fixed here): a bundle's builder is held on its first member - its description naming the members before its colon,
/// or naming none and its prompt's first line naming them - where the old `<feature> T<n>` brief let it stop unheld.
#[test]
fn a_bundle_s_builder_is_held_on_its_first_member() {
    let w = World::new("bundle");
    w.meta(1, "451 bundle T84, T85: two tooling follow-ups");
    let said = w.judged(&w.input("done"), 1, NOT_DECIDED);
    assert!(matches!(&said, Said::Held(..)), "{said:?}");
    w.meta(1, "451 record bundle: two follow-ups");
    put(&w.own, "{\"type\":\"user\",\"message\":{\"role\":\"user\",\"content\":\"Feature 451, a bundle of two: T84 and T85. Work only here.\"}}\n");
    let said = w.judged(&w.input("done"), 1, NOT_DECIDED);
    assert!(matches!(&said, Said::Held(..)), "{said:?}");
}
