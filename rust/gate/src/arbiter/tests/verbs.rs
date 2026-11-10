//! The `l7r-gate arbiter` command line end to end, on fixture clones; the fixtures are `super`'s (split at the file-scale bar).

use std::path::Path;

use serde_json::json;

use super::super::{cli, open_fixes};
use super::{clone_at, owe, python_tools, rows, run};

#[test]
fn every_verb_answers_on_a_clone() {
    let root = clone_at("cli");
    assert_eq!(cli(&["bogus".to_owned()]).code, 2);
    assert_eq!(run(&root, &["bogus"]).code, 2);
    assert_eq!(run(&root, &[]).code, 2);
    assert_eq!(run(&root, &["gate-held"]).code, 0);
    owe(
        &root,
        &json!({"red-gate@t": {"kind": "red-gate", "feature": "999-x"}}),
    );
    let held = run(&root, &["gate-held"]);
    assert_eq!(held.code, 1);
    assert!(held.stderr.starts_with("make done: refused - a tripwire"));
    let dir_text = root.join("specs/999-x").to_string_lossy().into_owned();
    assert_eq!(run(&root, &["spec-verdict", &dir_text]).code, 1);
    assert_eq!(run(&root, &["spec-ruled", &dir_text]).code, 1);
    assert_eq!(run(&root, &["unit-ruled", "u", "c"]).code, 1);
    assert_eq!(run(&root, &["ask", "has space", "two words here"]).code, 2);
    assert_eq!(run(&root, &["ask", "ok-1", "short"]).code, 2);
    assert_eq!(
        run(&root, &["ask", "ok-1", "two words here", "wrong"]).code,
        2
    );
    let asked = run(&root, &["ask", "ok-1", "two words here", "spec"]);
    assert!(asked.code == 0 && asked.stdout.contains("(REVIEW=spec: an accept stands"));
    let hint = run(&root, &["ask", "ok-2", "a plan review question"]);
    assert!(hint.stdout.contains("arbiter-ask: hint"));
    assert_eq!(
        run(&root, &["ask", "ok-3", "two words here", "claims:a"]).code,
        0
    );
    let plain = run(&root, &["ask", "ok-4", "two words here"]);
    assert!(!plain.stdout.contains("hint"));
    std::fs::write(
        root.join("rule.json"),
        format!(
            r#"{{"ruling": "continue", "why": "a colo{}r fix", "x": 1, "y": null}}"#,
            "u"
        ),
    )
    .unwrap();
    let rule = root.join("rule.json").to_string_lossy().into_owned();
    let bad = root.join("bad.json");
    std::fs::write(&bad, "nope").unwrap();
    let bad = bad.to_string_lossy().into_owned();
    let wrong = run(&root, &["ruled", "ask:ok-4", &rule, "--as", "main"]);
    assert!(wrong.code == 2 && wrong.stderr.starts_with("arbiter-ruled: declined"));
    assert_eq!(
        run(
            &root,
            &[
                "ruled",
                "ask:ok-4",
                "/no/such.json",
                "--as",
                "round-arbiter"
            ]
        )
        .code,
        1
    );
    assert_eq!(
        run(&root, &["ruled", "ask:ok-4", &bad, "--as", "round-arbiter"]).code,
        1
    );
    let ruled = run(
        &root,
        &["ruled", "ask:ok-4", &rule, "--as", "round-arbiter"],
    );
    assert!(
        ruled.code == 0
            && ruled
                .stdout
                .starts_with("arbiter-ruled: ask:ok-4 - continue (binding;"),
        "{}",
        ruled.stderr
    );
    assert!(rows(&root)[0]["why"].as_str().unwrap().contains("color"));
    assert_eq!(run(&root, &["ask", "ok-4", "two words here"]).code, 1);
    assert_eq!(
        run(&root, &["ruled-batch", &bad, "--as", "round-arbiter"]).code,
        1
    );
    assert_eq!(run(&root, &["ruled-batch", &rule, "--as", "main"]).code, 1);
    assert_eq!(
        run(
            &root,
            &["ruled", "ask:ok-3", &rule, "--as", "round-arbiter"]
        )
        .code,
        0
    );
}

fn committed(root: &Path, rel: &str) {
    let run_git = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(root)
            .args(args)
            .status()
            .unwrap()
            .success());
    };
    run_git(&["add", rel]);
    run_git(&[
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "-m",
        "x",
    ]);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one fixture walked through every path a settled fix can take"
)]
fn fixes_are_settled_and_nits_answered() {
    let root = clone_at("fixes-cli");
    python_tools(&root);
    let d = root.join("specs/999-x");
    let fix_row = |t: &str, f: &str| {
        format!(
            "{}\n",
            json!({"trigger": t, "fix": "open", "tooling_fix": f})
        )
    };
    std::fs::write(
        d.join("arbiter.jsonl"),
        fix_row("ask:f1", "one") + &fix_row("hour:999-x@2", "two"),
    )
    .unwrap();
    let none = run(&root, &["fix", "done", "ask:none", "a note here"]);
    assert!(
        none.code == 1
            && none.stderr.contains("no open tooling fix: ask:none")
            && none.stderr.contains("open now: ask:f1, hour:999-x@2"),
        "{}",
        none.stderr
    );
    assert!(run(&root, &["fix", "done", "", "a note here"])
        .stderr
        .contains("(no ID)"));
    assert_eq!(run(&root, &["fix", "done", "ask:f1", "x"]).code, 1);
    let notest = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/none.sh"],
    );
    assert!(
        notest
            .stderr
            .contains("TEST=tests/none.sh is not a file under tests/"),
        "{}",
        notest.stderr
    );
    assert!(run(&root, &["fix", "done", "ask:f1", "a note here"])
        .stderr
        .contains("TEST=<none>"));
    std::fs::create_dir_all(root.join("tests")).unwrap();
    std::fs::write(root.join("tests/t.sh"), "x").unwrap();
    let not_main = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/t.sh"],
    );
    assert!(
        not_main.stderr.contains("is not on main as it is here"),
        "{}",
        not_main.stderr
    );
    committed(&root, "tests/t.sh");
    // a landed copy of the test settles it; the origin ref is the fixture's main
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["update-ref", "refs/remotes/origin/main", "HEAD"])
        .status()
        .unwrap()
        .success());
    let done = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/t.sh"],
    );
    assert!(
        done.code == 0 && done.stdout.contains("1 fix(es) settled - ask:f1"),
        "{}",
        done.stderr
    );
    assert_eq!(open_fixes(&d).len(), 1);
    let declined_fix = run(
        &root,
        &[
            "fix",
            "declined",
            "hour:999-x@2",
            "this overhauls a process",
        ],
    );
    assert!(
        declined_fix.code == 0
            && declined_fix
                .stdout
                .contains("each a question owed escalation-check"),
        "{}",
        declined_fix.stderr
    );
    assert!(std::fs::read_to_string(d.join("gm-question.txt"))
        .unwrap()
        .contains("Declined because"));
    let nofeature = clone_at("no-active");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    assert!(run(&nofeature, &["fix", "done", "ask:none", "a note here"])
        .stderr
        .contains("the active feature (none)"));
    let nit_root = clone_at("nit");
    python_tools(&nit_root);
    let modal = nit_root.join("l7r/diagram/interactive/assets/modals/sheet/bath.md");
    std::fs::create_dir_all(modal.parent().unwrap()).unwrap();
    std::fs::write(&modal, "the NEW words\n").unwrap();
    let rid = "round:modal-form|modal:sheet/bath@3";
    std::fs::write(nit_root.join("specs/999-x/arbiter.jsonl"), format!("{}\n", json!({"trigger": rid, "ruling": "accept", "kind": "round", "unit": "modal-form|modal:sheet/bath", "what": "make OLD into NEW"}))).unwrap();
    let not_quoted = run(&nit_root, &["nit", rid, "zzz", "NEW"]);
    assert!(not_quoted.stderr.contains("must quote both OLD and NEW"));
    let unmade = run(&nit_root, &["nit", rid, "NEW", "OLD"]);
    assert!(
        unmade.stderr.contains("must hold NEW and no longer OLD"),
        "{}",
        unmade.stderr
    );
    let answered = run(&nit_root, &["nit", rid, "OLD", "NEW"]);
    assert!(
        answered.code == 0
            && answered
                .stdout
                .contains("1 unit(s) answered at today's words - u:modal-form"),
        "{}",
        answered.stderr
    );
    let none = "def answer(root, check, result, q='', kind=''):
    return []
";
    std::fs::write(nit_root.join("scripts/record/record_owed.py"), none).unwrap();
    let none_owed = run(&nit_root, &["nit", rid, "OLD", "NEW"]);
    assert!(
        none_owed.stdout.contains("0 unit(s) answered") && none_owed.stdout.contains("none owed")
    );
    std::fs::write(
        nit_root.join("scripts/record/record_owed.py"),
        "raise ImportError('x')
",
    )
    .unwrap();
    let broken = run(&nit_root, &["nit", rid, "OLD", "NEW"]);
    assert!(broken.code == 1 && broken.stderr.contains("python3 said"));
    std::env::set_var("ARBITER_FIX_ENGINE", "1");
    let engine = clone_at("engine");
    std::fs::write(
        engine.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "ask:e1", "fix": "open", "tooling_fix": "e"})
        ),
    )
    .unwrap();
    std::fs::create_dir_all(engine.join("tests")).unwrap();
    std::fs::write(engine.join("tests/e.sh"), "x").unwrap();
    committed(&engine, "tests/e.sh");
    let e = run(
        &engine,
        &["fix", "done", "ask:e1", "an engine note", "tests/e.sh"],
    );
    std::env::remove_var("ARBITER_FIX_ENGINE");
    assert_eq!(e.code, 0, "{}", e.stderr);
    assert!(
        std::fs::read_to_string(engine.join("specs/999-x/arbiter.jsonl"))
            .unwrap()
            .contains("(an engine fix")
    );
}
