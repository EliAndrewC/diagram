use std::path::Path;

use serde_json::{json, Value};

use super::{judge, GUARD};
use crate::protocol::{Answer, Event};
use crate::shared::checks::testkit::{clone_at, dir};
use crate::shared::session::Session;

fn gate(tree: &Path, script: &str) {
    std::fs::create_dir_all(tree.join("scripts/gates")).unwrap();
    crate::guards::write_executable(
        &tree.join("scripts/gates/l7r-gate.sh"),
        &format!("#!/bin/sh\n{script}\n"),
    );
}

fn event(tool: &str, cwd: Option<&Path>, sub: &str, prompt: &str) -> Event {
    let mut input = json!({"tool_name": tool, "session_id": "s", "tool_use_id": "t1", "tool_input": {"subagent_type": sub, "prompt": prompt}});
    if let Some(c) = cwd {
        input["cwd"] = json!(c);
    }
    Event {
        name: "PreToolUse".to_owned(),
        input,
    }
}

fn call(e: &Event, here: &Path, tree: &Path) -> Vec<Answer> {
    judge(e, &Session::from_input(&e.input), here, tree)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_dispatch_into_the_repository_is_refused_with_its_command() {
    crate::shared::log::quiet();
    let d = dir("bundle");
    gate(&d, "exit 0");
    let at = Some(d.path());
    let q = "research/questions/0087-road.html";
    let s = "research/sources/010-works-cited/4220-edo-enwiki.html";
    assert!(call(&event("Bash", at, "quote-check", q), &d, &d).is_empty());
    assert!(refused(
        &call(&event("Agent", at, "record-format", q), &d, &d),
        "make check-bundle Q=0087\n"
    ));
    assert!(refused(
        &call(&event("Agent", at, "record-style", q), &d, &d),
        "make check-bundle Q=0087 FOR=record-style"
    ));
    assert!(refused(
        &call(&event("Agent", at, "translation-check", q), &d, &d),
        "FOR=translation-check"
    ));
    assert!(refused(
        &call(&event("Agent", at, "source-applicability", s), &d, &d),
        "make check-bundle KEY=edo-enwiki\n"
    ));
    assert!(refused(
        &call(&event("Agent", at, "source-reader", s), &d, &d),
        "KEY=edo-enwiki WHOLE=1"
    ));
    assert!(refused(
        &call(&event("Agent", at, "modal-form", q), &d, &d),
        "make modal-bundle KIND=<the modal class> FOR=modal-form"
    ));
    let dup = format!("{q} and {q}");
    let got = call(&event("Agent", at, "record-format", &dup), &d, &d);
    assert!(matches!(&got[..], [Answer::Refuse(t)] if t.matches("Q=0087").count() == 1));
    assert!(refused(
        &call(
            &event("Agent", at, "source-reader", "research/SOURCES.html"),
            &d,
            &d
        ),
        "Q=<question number>"
    ));
    assert!(call(
        &event("Agent", at, "record-format", "no paths here"),
        &d,
        &d
    )
    .is_empty());
    assert!(call(&event("Agent", at, "spec-fidelity", q), &d, &d).is_empty());
    assert!(refused(
        &call(
            &event(
                "Agent",
                at,
                "record-format",
                &format!("CHECK_BUNDLE_OK=\"x\" {q}")
            ),
            &d,
            &d
        ),
        "needs a REASON"
    ));
    assert!(call(
        &event(
            "Agent",
            at,
            "record-format",
            &format!("CHECK_BUNDLE_OK=\"a good reason here\" {q}")
        ),
        &d,
        &d
    )
    .is_empty());
    assert!((GUARD.decide)(
        &event("Bash", None, "x", ""),
        &Session::from_input(&json!({}))
    )
    .is_empty());
}

#[test]
fn a_bundle_is_held_to_what_it_owes() {
    crate::shared::log::quiet();
    let d = dir("owed");
    gate(&d, "exit 0");
    let at = Some(d.path());
    let owes = d.join("a/MANIFEST.md");
    std::fs::create_dir_all(owes.parent().unwrap()).unwrap();
    std::fs::write(&owes, "owed-checks: record-format\n").unwrap();
    let old = d.join("b/MANIFEST.md");
    std::fs::create_dir_all(old.parent().unwrap()).unwrap();
    std::fs::write(&old, "no owed line\n").unwrap();
    let read = |p: &Path| format!("Read {}", p.display());
    assert!(call(&event("Agent", at, "record-format", &read(&owes)), &d, &d).is_empty());
    assert!(refused(
        &call(&event("Agent", at, "quote-check", &read(&owes)), &d, &d),
        "owes: record-format"
    ));
    assert!(refused(
        &call(&event("Agent", at, "record-format", &read(&old)), &d, &d),
        "build it again"
    ));
    assert!(call(&event("Agent", at, "record-style", &read(&old)), &d, &d).is_empty());
    assert!(call(
        &event("Agent", at, "record-format", "see /gone/MANIFEST.md"),
        &d,
        &d
    )
    .is_empty());
    assert!(refused(
        &call(
            &event(
                "Agent",
                at,
                "quote-check",
                &format!("CHECK_NOT_OWED_OK=\"x\" {}", read(&owes))
            ),
            &d,
            &d
        ),
        "CHECK_NOT_OWED_OK needs a REASON"
    ));
    assert!(call(
        &event(
            "Agent",
            at,
            "quote-check",
            &format!("CHECK_NOT_OWED_OK=\"the GM asked for it\" {}", read(&owes))
        ),
        &d,
        &d
    )
    .is_empty());
}

#[test]
fn decide_first_and_the_dispatch_counter_run_first() {
    crate::shared::log::quiet();
    let root = clone_at("decide");
    gate(
        &root,
        r#"if [ "$1" = plan ]; then echo 'decide first: make decide F=9 T=T1'; exit 1; fi; exit 0"#,
    );
    let at = Some(root.as_path());
    let got = call(
        &event("Agent", at, "record-format", "Read /x/MANIFEST.md"),
        &root,
        &root,
    );
    assert!(
        refused(&got, "record-format on /x/MANIFEST.md: decide first")
            && refused(&got, "DECIDE_OK")
    );
    assert!(refused(
        &call(
            &event("Agent", at, "record-format", "plain words"),
            &root,
            &root
        ),
        "on its prompt: decide first"
    ));
    let escaped = call(
        &event(
            "Agent",
            at,
            "record-format",
            "DECIDE_OK=\"the GM asked for it\" plain",
        ),
        &root,
        &root,
    );
    assert!(escaped.is_empty());
    assert!(refused(
        &call(
            &event("Agent", at, "record-format", "DECIDE_OK=\"x\" plain"),
            &root,
            &root
        ),
        "decide first"
    ));
    assert!(call(&event("Agent", at, "not-a-check", "x"), &root, &root).is_empty());
    let nogit = dir("no-git");
    gate(&nogit, "exit 1");
    assert!(call(
        &event("Agent", Some(&nogit), "record-format", "words"),
        &nogit,
        &nogit
    )
    .is_empty());
    gate(&root, "echo ignored; exit 0");
    std::fs::write(
        root.join(".git/arbiter-owed.json"),
        json!({"cascade@1": {"kind": "cascade", "feature": "999-x"}}).to_string(),
    )
    .unwrap();
    let held = call(
        &event("Agent", at, "impl-drift", "plain words"),
        &root,
        &root,
    );
    assert!(refused(&held, "cascade@1"));
    let v: Value = json!(null);
    assert!(v.is_null());
}
