//! The decider over a fixture repository (`tests/hooks/test-agent-model-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-agentmodel-{tag}"));
    std::fs::create_dir_all(d.join(".claude/agents")).unwrap();
    assert!(ask(
        Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    std::fs::write(d.join(".claude/agents/quote-check.md"), "x").unwrap();
    let held = d.canonicalize().unwrap();
    d.hold(held)
}

fn run(tool: &str, input: &Value, at: &Path) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    };
    judge(&e, &Session::from_input(&e.input), at)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_dispatch_with_no_model_and_no_file_is_refused_with_the_rule() {
    let at = world("refuse");
    let got = run("Agent", &json!({"subagent_type": "general-purpose"}), &at);
    assert!(refused(&got, "this `general-purpose` agent names no model"));
    assert!(refused(&got, "for anything that judges or builds"));
    assert!(refused(&got, "\n        SESSION_MODEL: <"));
    assert!(refused(&run("Agent", &json!({}), &at), "`general-purpose`"));
    assert!(refused(
        &run(
            "Agent",
            &json!({"subagent_type": "general-purpose", "model": ""}),
            &at
        ),
        "no model"
    ));
}

/// 451 T216: reading work names sonnet or haiku; judging or building work names no model and marks its prompt; any other name is refused.
#[test]
fn the_sessions_model_is_asked_for_by_the_prompts_line_never_by_name() {
    let at = world("session");
    let send = |model: &str, prompt: &str| {
        run(
            "Agent",
            &json!({"subagent_type": "general-purpose", "model": model, "prompt": prompt}),
            &at,
        )
    };
    let marked = "451 T216: build it\nSESSION_MODEL: builds the T216 guard\nRead first: x";
    assert!(send("", marked).is_empty());
    assert!(send("", "  SESSION_MODEL: judges the plan").is_empty());
    assert!(send("haiku", "describe the page").is_empty());
    assert!(send("sonnet", marked).is_empty());
    for named in ["opus", "fable", "inherit", "Sonnet"] {
        let got = send(named, marked);
        assert!(refused(
            &got,
            &format!("names `{named}`, which would not follow")
        ));
        assert!(refused(&got, "omit `model`"));
    }
    for unmarked in [
        "SESSION_MODEL: judges",
        "SESSION_MODEL:",
        "the guard reads a SESSION_MODEL: line of the prompt",
        "SESSION_MODEL=\"judges the plan\"",
        "SESSION_MODEL: <what it judges or builds, two words or more>",
    ] {
        assert!(refused(
            &send("", unmarked),
            "carries no `SESSION_MODEL:` line"
        ));
    }
    // A defined type is out of scope whatever it names: its file pins its tier.
    assert!(run(
        "Agent",
        &json!({"subagent_type": "quote-check", "model": "opus"}),
        &at
    )
    .is_empty());
}

/// 451 T217: the line passes only on a type measured to run on the session's model; any other ad-hoc type is refused with the two routes.
#[test]
fn the_line_passes_only_on_a_type_measured_to_inherit() {
    let at = world("inherits");
    let send = |kind: &str, model: &str, prompt: &str| {
        run(
            "Agent",
            &json!({"subagent_type": kind, "model": model, "prompt": prompt}),
            &at,
        )
    };
    let marked = "451 T217: judge it\nSESSION_MODEL: judges the plan section";
    for kind in super::INHERITS {
        assert!(send(kind, "", marked).is_empty(), "{kind}");
    }
    assert_eq!(
        super::inheriting(),
        "`general-purpose`, `Plan` and `claude`"
    );
    // Marked, unmarked or naming a judging model: an unlisted type gets the routes that work for it, never the line on itself.
    for (kind, model, prompt) in [
        ("Explore", "", marked),
        ("web-fetch", "", marked),
        ("plan", "", marked),
        ("Explore", "", "find the callers"),
        ("Explore", "opus", marked),
    ] {
        let got = send(kind, model, prompt);
        assert!(refused(
            &got,
            &format!("this `{kind}` agent would not run on the session's model - only `general-purpose`, `Plan` and `claude` inherit it.")
        ));
        assert!(refused(&got, "re-send it with\n        model: \"sonnet\""));
        assert!(refused(
            &got,
            "dispatch `general-purpose` instead, with NO `model`"
        ));
        assert!(refused(
            &got,
            "\n        SESSION_MODEL: <what it judges or builds"
        ));
        assert!(!refused(&got, "Re-send the SAME dispatch"));
    }
    assert!(send("Explore", "sonnet", marked).is_empty());
    assert!(send("Explore", "haiku", "describe the page").is_empty());
}

#[test]
fn a_named_model_a_pinned_type_a_fork_or_another_tool_passes() {
    let at = world("pass");
    assert!(run(
        "Agent",
        &json!({"subagent_type": "general-purpose", "model": "sonnet"}),
        &at
    )
    .is_empty());
    assert!(run("Agent", &json!({"subagent_type": "quote-check"}), &at).is_empty());
    assert!(run("Agent", &json!({"subagent_type": "fork"}), &at).is_empty());
    assert!(run("Bash", &json!({"command": "make done"}), &at).is_empty());
}

#[test]
fn outside_a_repository_the_trees_scripts_are_asked() {
    let at = world("tree");
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": "/no/such/place", "tool_input": {"subagent_type": "quote-check"}}),
    };
    let s = Session::from_input(&e.input);
    assert!(refused(&judge(&e, &s, &at), "quote-check"));
    std::fs::create_dir_all(at.join("scripts/.claude/agents")).unwrap();
    std::fs::write(at.join("scripts/.claude/agents/quote-check.md"), "x").unwrap();
    assert!(judge(&e, &s, &at).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}

#[test]
fn the_sessions_clone_says_what_is_pinned() {
    let at = world("clone");
    let mine = at.join(".clones/mine/.claude/agents");
    std::fs::create_dir_all(&mine).unwrap();
    std::fs::write(mine.join("only-here.md"), "x").unwrap();
    std::fs::create_dir_all(at.join(".clones/.session-clones")).unwrap();
    std::fs::write(
        at.join(".clones/.session-clones/s-am"),
        at.join(".clones/mine").to_string_lossy().as_bytes(),
    )
    .unwrap();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "session_id": "s-am", "cwd": at, "tool_input": {"subagent_type": "only-here"}}),
    };
    let main = at.to_string_lossy().into_owned();
    let session = Session::with_env(&e.input, |k| (k == "CLONE_MAIN").then(|| main.clone()));
    assert!(judge(&e, &session, &at).is_empty());
}
