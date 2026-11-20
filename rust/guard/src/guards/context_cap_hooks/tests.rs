//! The cap against a temporary clone and a builder's transcript; the payloads are the real ones pinned in `payloads.json`. The suite
//! (`tests/hooks/test-context-cap-hooks.sh`, replayed through the shim and, for the handoff, the whole chain) drives the binary.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    answer, context, is_handoff, judge, own_transcript, plain, refusal, tree_of, usage_of, Said,
    CONTEXT_CAP_TOKENS, TAIL_BYTES,
};
use crate::protocol::{run, Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

const PINNED: &str = include_str!("payloads.json");
const AID: &str = "af3dc58915037d8d6";

fn pinned(which: &str) -> Value {
    serde_json::from_str::<Value>(PINNED).unwrap()[which].clone()
}

fn none(_: &str) -> Option<String> {
    None
}

/// An assistant row of one model call whose context is `tokens`.
fn call(tokens: u64) -> Value {
    json!({"type": "assistant", "message": {"id": "msg_x", "usage": {
        "input_tokens": 2, "cache_read_input_tokens": tokens - 102, "cache_creation_input_tokens": 100, "output_tokens": 50}}})
}

/// A clone with a defined agent `review-x`, and the session's transcript directory holding the builder's own transcript of `rows`;
/// `task` puts a started task in force for feature 451-x.
struct Fixture {
    dir: TempDir,
}

impl Fixture {
    fn new(tag: &str, rows: &[Value], task: Option<&str>) -> Self {
        let dir = TempDir::new(&format!("guard-context-cap-{tag}"));
        std::fs::create_dir_all(dir.join("clone/.git")).unwrap();
        std::fs::create_dir_all(dir.join("clone/.claude/agents")).unwrap();
        std::fs::write(dir.join("clone/.claude/agents/review-x.md"), "---\n").unwrap();
        if let Some(t) = task {
            std::fs::create_dir_all(dir.join("clone/specs/451-x")).unwrap();
            std::fs::create_dir_all(dir.join("clone/.specify")).unwrap();
            std::fs::write(
                dir.join("clone/.specify/feature.json"),
                r#"{"feature_directory": "specs/451-x"}"#,
            )
            .unwrap();
            std::fs::write(
                dir.join("clone/.git/task-starts.jsonl"),
                format!("{{\"feature\": \"451-x\", \"task\": \"{t}\", \"utc\": \"2026-11-20T10:00:00Z\"}}\n"),
            )
            .unwrap();
        }
        let f = Self { dir };
        f.transcript(AID, rows);
        f
    }

    fn clone(&self) -> PathBuf {
        std::fs::canonicalize(self.dir.join("clone")).unwrap()
    }

    fn session(&self) -> PathBuf {
        self.dir.join("proj/sess.jsonl")
    }

    fn transcript(&self, aid: &str, rows: &[Value]) {
        let d = self.dir.join("proj/sess/subagents");
        std::fs::create_dir_all(&d).unwrap();
        let text: String = rows.iter().map(|r| r.to_string() + "\n").collect();
        std::fs::write(d.join(format!("agent-{aid}.jsonl")), text).unwrap();
    }

    fn handoffs(&self) -> PathBuf {
        self.clone().join(".git/l7r-handoffs")
    }

    /// The pinned `which` payload, its `cwd` and `transcript_path` this fixture's, its tool `tool` with `tool_input`.
    fn input(&self, which: &str, tool: &str, tool_input: Value) -> Value {
        let mut p = pinned(which);
        p["cwd"] = json!(self.clone());
        p["transcript_path"] = json!(self.session());
        p["tool_name"] = json!(tool);
        p["tool_input"] = tool_input;
        p
    }

    fn bash(&self, which: &str, cmd: &str) -> Value {
        self.input(which, "Bash", json!({"command": cmd}))
    }
}

/// The verdict on `input` against the cap, the process's environment unread.
fn verdict(input: &Value) -> Option<Said> {
    judge(input, Path::new("/"), &none, CONTEXT_CAP_TOKENS)
}

/// THE PINNED PAYLOADS (D8's first step): a builder's call carries `agent_id` and `agent_type` `general-purpose`, a defined agent's
/// its own name, the main session's neither; the transcript path is the session's, the builder's own derived beside it.
#[test]
fn the_pinned_payloads_carry_the_fields_the_guard_reads() {
    let (b, d, m) = (pinned("builder"), pinned("defined"), pinned("main"));
    assert_eq!(b["hook_event_name"], "PreToolUse");
    assert_eq!(b["agent_id"], AID);
    assert_eq!(b["agent_type"], "general-purpose");
    assert_eq!(d["agent_type"], "probe-check");
    assert!(m.get("agent_id").is_none() && m.get("agent_type").is_none());
    let t = b["transcript_path"].as_str().unwrap();
    // the payload's transcript is the session's
    assert!(!t.contains("subagents"));
    assert_eq!(
        own_transcript(t, AID).unwrap(),
        PathBuf::from(format!(
            "{}/subagents/agent-{AID}.jsonl",
            t.trim_end_matches(".jsonl")
        ))
    );
    assert_eq!(own_transcript("/x/sess.json", AID), None);
}

#[test]
fn the_context_is_the_last_assistant_rows_usage() {
    let f = Fixture::new("read", &[call(100_000), call(350_000)], None);
    let own = f.dir.join(format!("proj/sess/subagents/agent-{AID}.jsonl"));
    assert_eq!(context(&own), Some(350_000));
    // a later user row holding an Agent call's result carries the child's usage; a synthetic row of zero is no call; bad JSON skipped
    let child = json!({"type": "user", "toolUseResult": {"usage": {"input_tokens": 900_000}}, "message": {"usage": {"input_tokens": 900_000}}});
    let synthetic =
        json!({"type": "assistant", "message": {"usage": {"input_tokens": 0, "output_tokens": 0}}});
    f.transcript(AID, &[call(120_000), child, synthetic, json!("x")]);
    std::fs::write(
        &own,
        std::fs::read_to_string(&own).unwrap() + "{\"usage\" not json\n",
    )
    .unwrap();
    assert_eq!(context(&own), Some(120_000));
    // a last row longer than a read step, with no trailing newline
    let big = json!({"type": "assistant", "pad": "p".repeat(200_000), "message": {"usage": {"input_tokens": 400_000}}});
    std::fs::write(&own, format!("{}\n{big}", call(5_000))).unwrap();
    assert_eq!(context(&own), Some(400_000));
    // none at all, no file, and a call deeper than the tail
    f.transcript(AID, &[json!({"type": "user"})]);
    assert_eq!(context(&own), None);
    assert_eq!(context(&f.dir.join("nothing.jsonl")), None);
    let deep = format!(
        "{}\n{}\n",
        call(500_000),
        "x".repeat(usize::try_from(TAIL_BYTES).unwrap() + 10)
    );
    std::fs::write(&own, deep).unwrap();
    assert_eq!(context(&own), None);
    assert_eq!(usage_of(b"{\"type\": \"assistant\"}"), None);
}

/// RED FIRST, the five cases: a builder past the cap refused, naming its handoff; its handoff's Write passing; a builder under the
/// cap passing; the main session passing; the escape passing, a bare one refused. And a defined agent past the cap passing.
#[test]
fn a_builder_past_the_cap_is_refused_but_for_its_handoff() {
    let f = Fixture::new("cap", &[call(310_000)], None);
    let handoff = f.handoffs().join(format!("{AID}.md"));
    // refused, every tool, naming the file
    for input in [
        f.bash("builder", "make quick"),
        f.input(
            "builder",
            "Edit",
            json!({"file_path": f.clone().join("x.rs")}),
        ),
        f.input("builder", "Grep", json!({"pattern": "x"})),
    ] {
        assert_eq!(
            verdict(&input),
            Some(Said::Refused {
                agent: AID.to_owned(),
                tokens: 310_000,
                handoff: handoff.clone()
            })
        );
    }
    // the handoff's Write, Edit and Read pass, its path recorded; another agent's handoff, or this one's name elsewhere, does not
    for tool in ["Write", "Edit", "Read"] {
        let input = f.input(
            "builder",
            tool,
            json!({"file_path": handoff, "content": "done; left"}),
        );
        assert_eq!(
            verdict(&input),
            Some(Said::Handoff(handoff.display().to_string()))
        );
    }
    let other = f.handoffs().join("a0000000000000000.md");
    let elsewhere = f.clone().join(format!("{AID}.md"));
    for file in [other, elsewhere] {
        let input = f.input(
            "builder",
            "Write",
            json!({"file_path": file, "content": "x"}),
        );
        assert!(matches!(verdict(&input), Some(Said::Refused { .. })));
    }
    // a builder under the cap, and at it, pass
    f.transcript(AID, &[call(310_000), call(250_000)]);
    assert_eq!(verdict(&f.bash("builder", "make quick")), None);
    f.transcript(AID, &[call(CONTEXT_CAP_TOKENS)]);
    assert_eq!(verdict(&f.bash("builder", "make quick")), None);
    // the main session, and a defined agent past the cap, pass without a read
    f.transcript(AID, &[call(900_000)]);
    assert_eq!(verdict(&f.bash("main", "make quick")), None);
    let mut defined = f.bash("builder", "make quick");
    defined["agent_type"] = json!("review-x");
    assert_eq!(verdict(&defined), None);
    // the escape, and a bare one
    assert_eq!(
        verdict(&f.bash("builder", "CONTEXT_OK=\"the landing needs it\" make land")),
        Some(Said::Escaped("the landing needs it".to_owned()))
    );
    assert!(matches!(
        verdict(&f.bash("builder", "make quick CONTEXT_OK")),
        Some(Said::NoReason(t)) if t.contains("CONTEXT_OK with no reason")
    ));
}

#[test]
fn the_handoff_is_named_for_the_task_the_calls_line_carries() {
    let f = Fixture::new("task", &[call(400_000)], Some("T12"));
    let handoff = f.handoffs().join(format!("T12-{AID}.md"));
    assert!(matches!(
        verdict(&f.bash("builder", "ls")),
        Some(Said::Refused { handoff: named, .. }) if named == handoff
    ));
    let write = f.input(
        "builder",
        "Write",
        json!({"file_path": handoff, "content": "x"}),
    );
    assert!(matches!(verdict(&write), Some(Said::Handoff(_))));
    // the file the task-less name gives is this agent's too
    let bare = f.input(
        "builder",
        "Write",
        json!({"file_path": f.handoffs().join(format!("{AID}.md"))}),
    );
    assert!(matches!(verdict(&bare), Some(Said::Handoff(_))));
}

#[test]
fn what_it_cannot_read_it_passes() {
    let f = Fixture::new("blind", &[call(900_000)], None);
    // an unsafe agent id, an agent type that is no plain name, a transcript path with no `.jsonl`, outside any clone
    let mut bad = f.bash("builder", "ls");
    bad["agent_id"] = json!("../x");
    assert_eq!(verdict(&bad), None);
    let mut odd = f.bash("builder", "ls");
    odd["agent_type"] = json!("../review-x");
    // a type that names no file is a builder's
    assert!(matches!(verdict(&odd), Some(Said::Refused { .. })));
    let mut path = f.bash("builder", "ls");
    path["transcript_path"] = json!(f.dir.join("proj/sess"));
    assert_eq!(verdict(&path), None);
    let mut outside = f.bash("builder", "ls");
    outside["cwd"] = json!(f.dir.join("proj"));
    assert_eq!(verdict(&outside), None);
    assert!(plain("a1-b_2") && !plain("") && !plain("a/b") && !plain(".."));
}

#[test]
fn the_handoff_path_compares_by_its_real_directory() {
    let f = Fixture::new("real", &[], None);
    std::fs::create_dir_all(f.handoffs()).unwrap();
    let dotted = f
        .clone()
        .join(".git/../.git/l7r-handoffs")
        .join(format!("x-{AID}.md"));
    assert!(is_handoff(
        &dotted.display().to_string(),
        &f.handoffs(),
        AID
    ));
    assert!(!is_handoff("/", &f.handoffs(), AID));
    // a cwd that is no directory walks up from itself as written
    assert_eq!(tree_of(Path::new("/no/such/dir")), None);
}

/// The hook's own entry, the process's environment and directory read: the main session passes, a builder past the cap is refused.
#[test]
fn the_hook_entry_passes_the_main_session() {
    crate::shared::log::quiet();
    let f = Fixture::new("entry", &[call(900_000)], None);
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("main", "make quick"),
    };
    assert_eq!(run(&mut e, &[super::GUARD]).code, 0);
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("builder", "make quick"),
    };
    assert_eq!(run(&mut e, &[super::GUARD]).code, 2);
}

/// The answers, each firing written to the guard log: the refusal's text names the file, the next step and the escape.
#[test]
fn the_answers_and_their_records() {
    crate::shared::log::quiet();
    let f = Fixture::new("answer", &[call(310_000)], None);
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    let handoff = f.handoffs().join(format!("{AID}.md"));
    let text = refusal(310_000, &handoff);
    assert_eq!(
        ask(f.bash("builder", "make quick")),
        vec![Answer::Refuse(text.clone())]
    );
    assert!(text.contains(&handoff.display().to_string()));
    assert!(text.contains("310000 tokens, past the cap of 300000"));
    assert!(
        text.contains("Stop, and reply with that path") && text.contains("CONTEXT_OK=\"<reason>\"")
    );
    let write = f.input(
        "builder",
        "Write",
        json!({"file_path": handoff, "content": "x"}),
    );
    assert!(ask(write).is_empty());
    assert!(ask(f.bash("builder", "CONTEXT_OK=\"the landing needs it\" ls")).is_empty());
    assert!(matches!(
        ask(f.bash("builder", "ls CONTEXT_OK")).as_slice(),
        [Answer::Refuse(_)]
    ));
    assert!(ask(f.bash("main", "ls")).is_empty());
}
