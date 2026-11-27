//! The builder split (451 T237) against a temporary clone and a builder's own transcript, its first row the brief; the suite
//! (`tests/hooks/test-context-cap-hooks.sh`, cases 8 and 9) drives the binary.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::{answer, judge as verdict_of, refusal as cap_refusal, Said, CONTEXT_CAP_TOKENS};
use super::{code_builder, dispatch, judge, refusal, Split};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

const AID: &str = "af3dc58915037d8d6";
const CODE: &str = "Build feature 451 task T05.\n\nSTOP POINT. Your work ends when ALL of these hold:\n - make claims-triage";

fn none(_: &str) -> Option<String> {
    None
}

fn no_clone() -> Option<PathBuf> {
    None
}

/// A clone with a defined agent `review-x`, and the builder's own transcript: `first` its first row, then a call of `tokens`.
struct Fixture {
    dir: TempDir,
}

impl Fixture {
    fn new(tag: &str) -> Self {
        let dir = TempDir::new(&format!("guard-split-{tag}"));
        std::fs::create_dir_all(dir.join("clone/.git")).unwrap();
        std::fs::create_dir_all(dir.join("clone/.claude/agents")).unwrap();
        std::fs::write(dir.join("clone/.claude/agents/review-x.md"), "---\n").unwrap();
        std::fs::create_dir_all(dir.join("proj/sess/subagents")).unwrap();
        Self { dir }
    }

    fn own(&self) -> PathBuf {
        self.dir
            .join(format!("proj/sess/subagents/agent-{AID}.jsonl"))
    }

    fn brief(&self, first: &Value, tokens: u64) {
        let call = json!({"type": "assistant", "message": {"id": "m", "usage": {
            "input_tokens": 2, "cache_read_input_tokens": tokens - 2, "cache_creation_input_tokens": 0}}});
        std::fs::write(self.own(), format!("{first}\n{call}\n")).unwrap();
    }

    fn input(&self, tool: &str, ti: &Value) -> Value {
        json!({"hook_event_name": "PreToolUse", "agent_id": AID, "agent_type": "general-purpose",
            "cwd": self.dir.join("clone"), "transcript_path": self.dir.join("proj/sess.jsonl"),
            "tool_name": tool, "tool_input": ti})
    }
}

fn user(content: &Value) -> Value {
    json!({"type": "user", "message": {"role": "user", "content": content}})
}

fn agent(kind: &str, prompt: &str) -> Value {
    json!({"subagent_type": kind, "prompt": prompt})
}

fn verdict(input: &Value) -> Option<Said> {
    verdict_of(input, Path::new("/"), &none, CONTEXT_CAP_TOKENS, &no_clone)
}

/// WHAT A CALL DISPATCHES, named before anything is read: an Agent (or Task) call of a claims agent, a Workflow naming one as an
/// `agentType` in its args or its script; nothing else.
#[test]
fn a_claims_dispatch_is_named_from_the_call_alone() {
    let call = |tool: &str, ti: Value| json!({"tool_name": tool, "tool_input": ti});
    assert_eq!(
        dispatch(&call("Agent", agent("impl-drift", "Judge it"))),
        Some(("impl-drift".to_owned(), "Judge it".to_owned()))
    );
    assert_eq!(
        dispatch(&call("Task", agent("claims-triage", "p"))).map(|d| d.0),
        Some("claims-triage".to_owned())
    );
    assert_eq!(dispatch(&call("Agent", agent("spec-fidelity", "p"))), None);
    assert_eq!(dispatch(&json!({"tool_name": "Agent"})), None);
    assert_eq!(
        dispatch(&call("Bash", json!({"command": "impl-drift"}))),
        None
    );
    // a check-wave's args, a unit's `then` step, a script's literal; another type, or none, is no dispatch
    let wave = json!({"name": "check-wave", "args": {"agentType": "impl-drift", "units": []}});
    assert_eq!(
        dispatch(&call("Workflow", wave)).map(|d| d.0),
        Some("impl-drift".to_owned())
    );
    let then = json!({"args": {"agentType": "glyph-check", "units": [{"label": "a", "then": [{"agentType": "claims-triage"}]}]}});
    assert_eq!(
        dispatch(&call("Workflow", then)).map(|d| d.0),
        Some("claims-triage".to_owned())
    );
    let script = json!({"script": "await agent({agentType: 'modal-form'}); await agent({agentType: \"impl-drift\", prompt: p})"});
    let (kind, text) = dispatch(&call("Workflow", script)).unwrap();
    assert_eq!(kind, "impl-drift");
    assert!(text.contains("modal-form"));
    let other = json!({"args": {"agentType": "glyph-check", "units": [{"n": 1}]}, "script": "agentType: x"});
    assert_eq!(dispatch(&call("Workflow", other)), None);
}

/// A CODE BUILDER is one whose brief holds a line opening STOP POINT and is no claims round's; any read that fails is none.
#[test]
fn a_code_builder_is_told_by_its_brief() {
    let f = Fixture::new("brief");
    f.brief(&user(&json!(CODE)), 1000);
    assert!(code_builder(&f.own()));
    // the brief as a list of blocks, its text the first text block
    f.brief(
        &user(&json!([{"type": "image"}, {"type": "text", "text": CODE}])),
        1000,
    );
    assert!(code_builder(&f.own()));
    f.brief(
        &user(&json!(
            "Build feature 449 task T427 (no stop point; it says stop point lower-case)"
        )),
        1000,
    );
    assert!(!code_builder(&f.own()));
    f.brief(
        &user(&json!(format!(
            "Run the claims round for feature 449 task T431.\n{CODE}"
        ))),
        1000,
    );
    assert!(!code_builder(&f.own()));
    f.brief(&user(&json!(42)), 1000);
    assert!(!code_builder(&f.own()));
    std::fs::write(f.own(), "not json\n").unwrap();
    assert!(!code_builder(&f.own()));
    assert!(!code_builder(&f.dir.join("absent.jsonl")));
}

/// THE VERDICT: refused, naming the agent; `SPLIT_OK` with a reason escapes; a bare one is refused as the escape refuses.
#[test]
fn the_verdict_and_its_escape() {
    assert_eq!(
        judge("impl-drift".to_owned(), "Judge it"),
        Split::Refused("impl-drift".to_owned())
    );
    assert_eq!(
        judge(
            "impl-drift".to_owned(),
            "SPLIT_OK=\"the GM asked\" Judge it"
        ),
        Split::Escaped("the GM asked".to_owned())
    );
    assert!(
        matches!(judge("impl-drift".to_owned(), "SPLIT_OK Judge"), Split::NoReason(t) if t.contains("SPLIT_OK with no reason") && t.contains("in the prompt"))
    );
    let text = refusal("claims-triage");
    for part in [
        "does not dispatch claims-triage",
        "STOP POINT",
        "make claims-triage",
        "make claims-owed",
        "paths to commit",
        "SPLIT_OK=",
    ] {
        assert!(text.contains(part), "{part}: {text}");
    }
}

/// THE GUARD: a code builder's claims dispatch refused under the cap; its other dispatches, an unmarked builder's, a defined
/// agent's and the main session's pass; past the cap, the cap's own refusal comes first and names the split.
#[test]
fn the_guard_holds_a_code_builder_alone() {
    crate::shared::log::quiet();
    let f = Fixture::new("guard");
    f.brief(&user(&json!(CODE)), 120_000);
    let claims = f.input("Agent", &agent("claims-triage", "Triage"));
    assert_eq!(
        verdict(&claims),
        Some(Said::Split(Split::Refused("claims-triage".to_owned())))
    );
    assert_eq!(
        verdict(&f.input("Agent", &agent("spec-fidelity", "MODE 4"))),
        None
    );
    let mut defined = claims.clone();
    defined["agent_type"] = json!("review-x");
    assert_eq!(verdict(&defined), None);
    let mut main = claims.clone();
    main.as_object_mut().unwrap().remove("agent_id");
    assert_eq!(verdict(&main), None);
    let mut nowhere = claims.clone();
    nowhere["cwd"] = json!("/");
    assert_eq!(verdict(&nowhere), None);
    let mut no_transcript = claims.clone();
    no_transcript["transcript_path"] = json!("sess");
    assert_eq!(verdict(&no_transcript), None);
    // the answers and their records
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    assert_eq!(
        ask(claims.clone()),
        vec![Answer::Refuse(refusal("claims-triage"))]
    );
    assert!(ask(f.input(
        "Agent",
        &agent("impl-drift", "SPLIT_OK=\"the GM asked for it\" Judge")
    ))
    .is_empty());
    assert!(
        matches!(&ask(f.input("Agent", &agent("impl-drift", "SPLIT_OK Judge")))[..], [Answer::Refuse(t)] if t.contains("SPLIT_OK"))
    );
    // an unmarked builder passes
    f.brief(&user(&json!("Build feature 449 task T427")), 120_000);
    assert_eq!(verdict(&claims), None);
    // in the wrap-up band (451 T417): a claims dispatch is no stop point's step, refused naming it
    f.brief(&user(&json!(CODE)), 310_000);
    assert!(matches!(
        verdict(&claims),
        Some(Said::BandRefused { what, .. }) if what == "a dispatch of `claims-triage`"
    ));
    // past the ceiling: the cap's refusal, naming the split for a code builder only
    f.brief(&user(&json!(CODE)), 350_000);
    assert!(matches!(
        verdict(&claims),
        Some(Said::Refused { code: true, .. })
    ));
    f.brief(
        &user(&json!("Run the claims round for feature 449 task T431")),
        350_000,
    );
    assert!(matches!(
        verdict(&claims),
        Some(Said::Refused { code: false, .. })
    ));
    let h = Path::new("/h.md");
    assert!(cap_refusal(310_000, h, true).contains("does not run the claims round"));
    assert!(!cap_refusal(310_000, h, false).contains("claims round"));
}
