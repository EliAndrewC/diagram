//! The decider over a fixture repository, the Agent hooks stubbed (`tests/hooks/test-workflow-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{agent_hooks, agent_type, call_end, calls, decide, judge, verdict, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn world(tag: &str, hook: &str) -> (crate::shared::tempdir::Held<PathBuf>, Ctx) {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-workflow-{tag}"));
    std::fs::create_dir_all(d.join(".claude/agents")).unwrap();
    std::fs::create_dir_all(d.join(".claude/workflows")).unwrap();
    let (keep, d) = {
        let canon = d.canonicalize().unwrap();
        (d, canon)
    };
    std::fs::write(d.join(".claude/agents/quote-check.md"), "x").unwrap();
    std::fs::write(d.join(".claude/workflows/check-wave.js"), "x").unwrap();
    let settings = json!({"hooks": {"PreToolUse": [
        {"matcher": "Bash", "hooks": [{"type": "command", "command": "exit 2"}]},
        {"matcher": "Agent|Task", "hooks": [{"command": hook}, {"type": "other", "command": "exit 2"}]},
    ]}});
    std::fs::write(d.join("settings.json"), settings.to_string()).unwrap();
    let ctx = Ctx {
        root: d.clone(),
        settings: d.join("settings.json"),
    };
    (keep.hold(d), ctx)
}

fn workflow(input: &Value, d: &Path) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Workflow", "session_id": "s", "cwd": d, "tool_use_id": "t1", "tool_input": input}),
    }
}

fn say(input: &Value, d: &Path, ctx: &Ctx) -> String {
    verdict(&workflow(input, d), ctx)
}

fn script(text: &str, d: &Path, ctx: &Ctx) -> String {
    say(&json!({"script": text}), d, ctx)
}

#[test]
fn a_scripts_agent_calls_are_held_to_the_rules() {
    let (d, ctx) = world("script", "exit 0");
    assert!(script("await agent('sum (a)', {label: 'a'})", &d, &ctx)
        .starts_with("UNTYPED agent('sum (a)'"));
    assert_eq!(
        script(
            "// GP_OK: a deliberate stage\nagent('x', {model: 'sonnet'})",
            &d,
            &ctx
        ),
        "ESCAPED"
    );
    assert!(script("// GP_OK: a deliberate stage\nagent('x', {})", &d, &ctx).starts_with("MODEL "));
    assert!(script("// GP_OK\nagent('x', {model: 'sonnet'})", &d, &ctx).starts_with("UNTYPED"));
    assert_eq!(
        script("agent('x', {agentType: 'quote-check'})", &d, &ctx),
        "GUARDED quote-check"
    );
    assert_eq!(script("agent('x', {agentType: t})", &d, &ctx), "GUARDED ?");
    assert_eq!(
        script("agent('x', {agentType: 'own', model: 'opus'})", &d, &ctx),
        ""
    );
    assert!(script("workflow('check-wave', {})", &d, &ctx).starts_with("SCRIPT"));
    assert_eq!(script("workflow('other', {})", &d, &ctx), "");
}

#[test]
fn a_named_or_file_script_is_read() {
    let (d, ctx) = world("named", "exit 0");
    std::fs::write(d.join(".claude/workflows/mine.js"), "agent('x', {})").unwrap();
    assert!(say(&json!({"name": "mine"}), &d, &ctx).starts_with("UNTYPED"));
    assert_eq!(say(&json!({"name": "none"}), &d, &ctx), "");
    let file = d.join(".claude/workflows/mine.js");
    assert!(say(&json!({"scriptPath": file}), &d, &ctx).starts_with("UNTYPED"));
    assert_eq!(say(&json!({"scriptPath": "/no/such.js"}), &d, &ctx), "");
    let wave = d.join(".claude/workflows/check-wave.js");
    assert!(say(&json!({"scriptPath": wave}), &d, &ctx).starts_with("ARGS"));
}

fn wave(units: &Value) -> Value {
    json!({"name": "check-wave", "args": {"agentType": "quote-check", "units": units}})
}

#[test]
fn a_waves_args_are_checked_before_any_unit_runs() {
    let (d, ctx) = world("args", "exit 2");
    assert!(say(&json!({"name": "check-wave", "args": "[]"}), &d, &ctx).contains("a JSON string"));
    assert!(say(&json!({"name": "check-wave"}), &d, &ctx).contains("check-wave needs args"));
    assert!(say(
        &json!({"name": "check-wave", "args": {"units": []}}),
        &d,
        &ctx
    )
    .contains("check-wave needs args"));
    assert!(say(
        &json!({"name": "check-wave", "args": {"agentType": "no", "units": [1]}}),
        &d,
        &ctx
    )
    .starts_with("JOB `no`"));
    assert!(say(&wave(&json!([{"label": "a"}])), &d, &ctx).contains("unit 0 needs"));
    assert!(say(&wave(&json!([1])), &d, &ctx).contains("unit 0 needs"));
    assert!(say(
        &wave(&json!([{"label": "a", "prompt": "p", "then": 1}])),
        &d,
        &ctx
    )
    .contains("then is a list"));
    assert!(say(
        &wave(
            &json!([{"label": "a", "prompt": "p", "then": [{"prompt": "x", "agentType": "no"}]}])
        ),
        &d,
        &ctx
    )
    .contains("verify step 0"));
}

#[test]
fn each_unit_meets_the_agent_hooks_and_the_first_refusal_refuses_the_run() {
    let (d, ctx) = world(
        "units",
        "grep -q REFUSE && { echo its own words >&2; exit 2; } ; [ \"$L7R_WAVE_UNIT\" = 1 ]",
    );
    let good = wave(
        &json!([{"label": "a", "prompt": "p", "then": null}, {"label": "b", "prompt": "q", "then": [{"prompt": "v", "agentType": "source-reader"}]}]),
    );
    assert_eq!(say(&good, &d, &ctx), "WAVE-PASSED");
    let bad = wave(
        &json!([{"label": "a", "prompt": "p", "then": [{"prompt": "REFUSE", "agentType": "source-reader"}]}]),
    );
    assert_eq!(say(&bad, &d, &ctx), "UNIT a / source-reader\nits own words");
    let e = workflow(&good, &d);
    let unnamed = Event {
        name: e.name.clone(),
        input: json!({"tool_name": "Workflow", "tool_input": good}),
    };
    assert_eq!(verdict(&unnamed, &ctx), "WAVE-PASSED");
}

#[test]
fn the_settings_say_which_hooks_an_agent_meets() {
    let (d, ctx) = world("hooks", "exit 0");
    assert_eq!(agent_hooks(&ctx.settings), ["exit 0"]);
    std::fs::write(d.join("none.json"), r#"{"hooks": {"PreToolUse": [{"hooks": [{"command": "a"}]}, {"matcher": "Bash", "hooks": []}, {"matcher": "Agent"}]}}"#).unwrap();
    assert_eq!(agent_hooks(&d.join("none.json")), ["a"]);
    assert!(agent_hooks(&d.join("absent.json")).is_empty());
}

#[test]
fn the_call_scanner_balances_and_skips_strings() {
    assert_eq!(
        calls("x.agent('a') ; agent('b(', [1], \"c\\\")\") tail", "agent"),
        ["agent('b(', [1], \"c\\\")\")"]
    );
    assert_eq!(call_end(b"(a", 1), 2);
    assert_eq!(agent_type("{agentType: `x-y`}").as_deref(), Some("x-y"));
    assert_eq!(agent_type("{}"), None);
}

#[test]
fn the_answers() {
    let (d, ctx) = world("answers", "exit 0");
    let run = |input: &Value| {
        let e = workflow(input, &d);
        judge(&e, &Session::from_input(&e.input), &ctx)
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    assert!(refused(
        &run(&json!({"script": "agent('x', {})"})),
        "no agentType"
    ));
    assert!(refused(
        &run(&json!({"script": "// GP_OK: one deliberate\nagent('x', {})"})),
        "names no model"
    ));
    assert!(refused(
        &run(&json!({"script": "agent('x', {agentType: 'quote-check'})"})),
        "name: \"check-wave\""
    ));
    assert!(refused(
        &run(&json!({"script": "workflow('check-wave')"})),
        "is run by name"
    ));
    assert!(
        run(&json!({"script": "// GP_OK: one deliberate\nagent('x', {model: 'sonnet'})"}))
            .is_empty()
    );
    assert!(run(&json!({"script": ""})).is_empty());
    assert!(
        matches!(&run(&wave(&json!([{"label": "a", "prompt": "p"}])))[..], [Answer::Notice(t)] if t.contains("make wave-report"))
    );
    let (d2, ctx2) = world("unit-answer", "cat >/dev/null; echo words >&2; exit 2");
    let e = workflow(&wave(&json!([{"label": "z", "prompt": "p"}])), &d2);
    assert!(refused(
        &judge(&e, &Session::from_input(&e.input), &ctx2),
        "check-wave unit z - a guard of its type refused it"
    ));
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(judge(&bash, &Session::from_input(&bash.input), &ctx).is_empty());
    let none = Ctx {
        root: d.clone(),
        settings: d.join("absent"),
    };
    let call = workflow(&json!({"script": "agent('x', {})"}), &d);
    assert!(judge(&call, &Session::from_input(&call.input), &none).is_empty());
    let outside = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Workflow", "cwd": "/no/such/place"}),
    };
    assert!(decide(&outside, &Session::from_input(&outside.input)).is_empty());
}

#[test]
fn inside_a_repository_the_decider_is_reached() {
    let d = crate::shared::tempdir::TempDir::new("guard-decide-wflw");
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": d}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}
