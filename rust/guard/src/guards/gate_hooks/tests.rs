//! The decider against a flag file in a temporary directory; the verdicts against today's are the suite's
//! (`tests/hooks/test-gate-hooks.sh`, replayed through the shim).

use std::path::PathBuf;
use std::sync::Once;

use serde_json::{json, Value};

use super::{judge, state};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

static LOG: Once = Once::new();

fn flag(tag: &str) -> PathBuf {
    LOG.call_once(|| {
        std::env::set_var(
            "GUARD_LOG_DIR",
            std::env::temp_dir().join(format!("l7r-guard-gate-log-{}", std::process::id())),
        );
    });
    let d = std::env::temp_dir().join(format!("l7r-guard-gate-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d.join("s.subset")
}

fn bash(cmd: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "session_id": "s", "tool_input": {"command": cmd}}),
    }
}

fn run(e: &Event, f: &std::path::Path) -> Vec<Answer> {
    judge(e, &Session::from_input(&json!({})), f)
}

#[test]
fn a_subset_run_then_the_gate_is_refused_once() {
    let f = flag("subset");
    assert!(run(&bash("python3 -m pytest t.py -k \"a or b\""), &f).is_empty());
    assert!(f.exists());
    let refused = run(&bash("make done"), &f);
    assert!(
        matches!(&refused[..], [Answer::Refuse(w)] if w.contains("WHOLE test") && w.contains("-k \"a or b\""))
    );
    assert!(run(&bash("make done"), &f).is_empty());
}

#[test]
fn the_subset_spellings_arm_it_and_a_whole_run_clears_it() {
    let f = flag("spellings");
    for cmd in [
        "make test-file FILE=tests/x.py K=\"a\"",
        "make test-file FILE=tests/x.py::test_a",
        "make quick -k=a",
    ] {
        let _ = std::fs::remove_file(&f);
        assert!(run(&bash(cmd), &f).is_empty() && f.exists());
    }
    assert!(run(&bash("make test-file FILE=tests/x.py SKIP_LOCK=1"), &f).is_empty() && !f.exists());
    let long = format!("pytest -k a {}", "é".repeat(200));
    assert!(run(&bash(&long), &f).is_empty() && std::fs::read_to_string(&f).unwrap().len() <= 120);
    assert!(run(&bash("ls -k a"), &f).is_empty());
}

#[test]
fn an_empty_flag_names_a_subset_still() {
    let f = flag("empty");
    std::fs::write(&f, "").unwrap();
    assert!(
        matches!(&run(&bash("make done"), &f)[..], [Answer::Refuse(w)] if w.contains("(pytest -k ...)"))
    );
}

#[test]
fn a_python_edit_clears_it_and_another_edit_does_not() {
    let f = flag("edit");
    let edit = |p: &str| Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": p}}),
    };
    std::fs::write(&f, "x").unwrap();
    assert!(run(&edit("a.md"), &f).is_empty() && f.exists());
    assert!(run(&edit("a.py"), &f).is_empty() && !f.exists());
}

#[test]
fn gate_ok_stands_aside_with_a_reason_and_refuses_without() {
    let f = flag("escape");
    std::fs::write(&f, "x").unwrap();
    assert!(run(&bash("make done  # GATE_OK: the whole files ran"), &f).is_empty() && !f.exists());
    assert!(
        matches!(&run(&bash("make done  # GATE_OK"), &f)[..], [Answer::Refuse(w)] if w.contains("GATE_OK with no reason"))
    );
}

#[test]
fn quick_and_done_are_rewritten_to_done() {
    let f = flag("combine");
    let got = run(&bash("make quick && make done"), &f);
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == "make done" && n.contains("superset"))
    );
}

#[test]
fn a_mention_in_another_field_arms_nothing() {
    let f = flag("description");
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "make test-file FILE=tests/x.py", "description": "run it -k fast"}}),
    };
    assert!(run(&e, &f).is_empty() && !f.exists());
}

#[test]
fn status_prints_the_flag() {
    let f = flag("status");
    let status = Event {
        name: "status".to_owned(),
        input: json!({}),
    };
    assert!(matches!(&run(&status, &f)[..], [Answer::Print(s)] if s == "subset_pending=0"));
    std::fs::write(&f, "pytest -k a").unwrap();
    assert!(
        matches!(&run(&status, &f)[..], [Answer::Print(s)] if s == "subset_pending=1 cmd=pytest -k a")
    );
}

#[test]
fn the_flag_is_the_sessions_in_its_directory() {
    let d = std::env::temp_dir().join(format!("l7r-guard-gate-dir-{}", std::process::id()));
    let got: Vec<PathBuf> = [json!({"session_id": "a/b c"}), json!({})]
        .iter()
        .map(|i: &Value| state(i, Some(d.to_string_lossy().into_owned())))
        .collect();
    assert_eq!(got, [d.join("a_b_c.subset"), d.join("nosession.subset")]);
    assert_eq!(
        state(&json!({}), None),
        PathBuf::from("/tmp/claude-gate/nosession.subset")
    );
    assert!(
        super::decide(
            &Event {
                name: "status".to_owned(),
                input: json!({})
            },
            &Session::from_input(&json!({}))
        )
        .len()
            == 1
    );
}
