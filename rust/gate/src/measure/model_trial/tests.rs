//! The cases of `test_model_trial.py`, and every verb against a stand-in for `claude`.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::case::{clone_head_at, read_dispatch, set_field, set_model};
use super::{cli, fold_usage, outside_paths, read, replayable, signature, text_of, Trial};

fn git(dir: &Path, args: &[&str]) -> String {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success());
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn lines(path: &Path, records: &[Value]) {
    std::fs::write(
        path,
        records
            .iter()
            .map(Value::to_string)
            .collect::<Vec<_>>()
            .join("\n")
            + "\n",
    )
    .unwrap();
}

/// A clone at `<scratch>/m/.clones/c` with one commit and an agent file, and the stand-in `claude`.
fn world(tag: &str) -> (PathBuf, Trial) {
    let top = crate::checks::scratch(tag);
    let clone = top.join("m/.clones/c");
    std::fs::create_dir_all(clone.join(".claude/agents")).unwrap();
    std::fs::create_dir_all(clone.join("pool/hamlets/x")).unwrap();
    git(&clone, &["init", "-q"]);
    git(&clone, &["config", "user.email", "t@t"]);
    git(&clone, &["config", "user.name", "t"]);
    std::fs::write(
        clone.join(".claude/agents/spec-fidelity.md"),
        "---\nname: s\nmodel: opus\n---\nbody\n",
    )
    .unwrap();
    std::fs::write(clone.join("pool/hamlets/x/x.gen.py"), "# gen\n").unwrap();
    std::fs::write(clone.join("pool/hamlets/x/x.json"), "{}\n").unwrap();
    std::fs::write(clone.join("pool/hamlets/x/other.txt"), "no\n").unwrap();
    git(&clone, &["add", "."]);
    git(&clone, &["commit", "-qm", "a"]);
    let claude = top.join("claude");
    crate::write_executable(&claude, "#!/bin/sh\nprintf '{\"session_id\": \"sess\", \"result\": \"the reply\", \"num_turns\": 3, \"usage\": {\"input_tokens\": 1000, \"output_tokens\": 5}, \"modelUsage\": {\"m\": 1}, \"duration_ms\": 2000, \"total_cost_usd\": 0.5}'\n");
    let trial = Trial {
        clone,
        projects: top.join("projects"),
        claude: claude.display().to_string(),
    };
    (top, trial)
}

fn transcript(top: &Path, prompt: &str) -> PathBuf {
    let t = top.join("agent-a.jsonl");
    lines(
        &t,
        &[
            json!({"type": "user", "timestamp": "2026-10-20T10:00:00.000Z", "cwd": "/diagram/.clones/nobody", "message": {"content": prompt}}),
            json!({"type": "assistant", "timestamp": "2026-10-20T10:01:00.000Z", "message": {"id": "m1", "model": "opus", "usage": {"input_tokens": 10, "cache_read_input_tokens": 100, "output_tokens": 7}, "content": [{"type": "text", "text": "CLEAR and OK and OK"}]}}),
            json!({"type": "assistant", "message": {"content": []}}),
        ],
    );
    std::fs::write(
        top.join("agent-a.meta.json"),
        json!({"agentType": "spec-fidelity"}).to_string(),
    )
    .unwrap();
    t
}

#[test]
fn the_tested_model_is_written_into_the_agent_file() {
    let d = crate::checks::scratch("mt-model");
    let f = d.join("a.md");
    std::fs::write(
        &f,
        "---\nname: a\nmodel: opus\neffort: high\n---\nbody model: here\n",
    )
    .unwrap();
    set_model(&f, "claude-sonnet-5-5").unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "---\nname: a\nmodel: claude-sonnet-5-5\neffort: high\n---\nbody model: here\n"
    );
    std::fs::write(&f, "---\nname: b\n---\nbody\n").unwrap();
    set_model(&f, "x").unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "---\nname: b\nmodel: x\n---\nbody\n"
    );
    assert!(set_model(&d.join("none"), "x").is_err());
}

#[test]
fn the_omit_field_is_added_and_taken_away() {
    let d = crate::checks::scratch("mt-omit");
    let f = d.join("a.md");
    std::fs::write(&f, "---\nname: a\nomitClaudeMd: false\n---\nbody\n").unwrap();
    set_field(&f, true).unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "---\nname: a\nomitClaudeMd: true\n---\nbody\n"
    );
    set_field(&f, false).unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "---\nname: a\n---\nbody\n"
    );
    assert!(set_field(&d.join("none"), true).is_err());
    std::fs::write(&f, "no frontmatter").unwrap();
    set_field(&f, true).unwrap();
    assert_eq!(
        std::fs::read_to_string(&f).unwrap(),
        "no frontmatter\nomitClaudeMd: true"
    );
}

#[test]
fn the_paths_a_prompt_names_outside_any_checkout() {
    let prompt = "Bundle: /tmp/l7r-check/x/MANIFEST.md. Read `/diagram/.clones/c/.git/review-snapshot/u/clone`, not /diagram/.clones/c/pool/m.";
    assert_eq!(
        outside_paths(prompt),
        [
            "/diagram/.clones/c/.git/review-snapshot/u/clone",
            "/tmp/l7r-check/x/MANIFEST.md"
        ]
    );
}

#[test]
fn a_clones_head_at_a_moment_comes_from_its_reflog() {
    let (_, t) = world("mt-reflog");
    let first = git(&t.clone, &["rev-parse", "HEAD"]);
    let log = git(
        &t.clone,
        &["log", "-g", "--date=unix", "--format=%gd", "HEAD"],
    );
    let when: f64 = log
        .split('{')
        .nth(1)
        .unwrap()
        .trim_end_matches('}')
        .parse()
        .unwrap();
    assert_eq!(clone_head_at(&t.clone, when + 1.0), first);
    assert_eq!(clone_head_at(&t.clone, when - 100.0), "");
}

#[test]
fn a_dispatch_is_read_back_from_the_recorded_transcript() {
    let d = crate::checks::scratch("mt-dispatch");
    let unit = "building-review--x";
    let body = format!("UNIT: {unit}\nthe review.\nFollow it, then `make review-verdict ...`\nas your last act, and quote the line it prints.\n");
    let t = d.join("agent-x.jsonl");
    lines(
        &t,
        &[
            json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "cat d"}}]}}),
            json!({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": format!("noise\n{body}")}]}}),
        ],
    );
    assert_eq!(read_dispatch(&t, unit), body);
    let numbered: Vec<String> = body
        .lines()
        .enumerate()
        .map(|(i, l)| format!("{:6}\t{l}", i + 1))
        .collect();
    let numbered = numbered.join("\n") + "\n";
    lines(
        &t,
        &[
            json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": format!("/x/{unit}/dispatch.md")}}]}}),
            json!({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t2", "content": numbered}]}}),
        ],
    );
    assert_eq!(read_dispatch(&t, unit), body);
    lines(
        &t,
        &[
            json!({"type": "user", "message": {"content": [{"type": "text", "text": format!("UNIT: {unit}")}, {"type": "tool_result", "content": format!("UNIT: {unit} and no end")}]}}),
        ],
    );
    assert_eq!(read_dispatch(&t, unit), "");
}

#[test]
fn a_blocks_text_is_read_in_every_shape() {
    assert_eq!(text_of(&json!("x")), "x");
    assert_eq!(
        text_of(
            &json!([{"type": "text", "text": "a"}, {"type": "image"}, {"type": "text", "text": "b"}])
        ),
        "ab"
    );
    assert_eq!(text_of(&json!(null)), "");
}

#[test]
fn a_run_is_read_with_its_agent_and_verdict_words() {
    let top = crate::checks::scratch("mt-read");
    let t = transcript(&top, "the prompt");
    let run = read(&t);
    assert_eq!(
        (run.agent.as_str(), run.prompt.as_str(), run.reply.as_str()),
        ("spec-fidelity", "the prompt", "CLEAR and OK and OK")
    );
    assert_eq!(run.started, "2026-10-20T10:00:00.000Z");
    assert_eq!(signature(&run.reply), "CLEAR=1 OK=2");
    assert_eq!(read(&top.join("none.jsonl")).agent, "");
}

#[test]
fn the_fold_keeps_each_messages_maximum_and_the_commonest_model() {
    let rec = |id: &str, model: &str, n: i64| json!({"type": "assistant", "message": {"id": id, "model": model, "usage": {"input_tokens": n, "cache_creation_input_tokens": 1, "cache_read_input_tokens": 2, "output_tokens": n}}});
    let got = fold_usage(&[
        rec("a", "x", 5),
        rec("a", "x", 9),
        rec("b", "y", 1),
        rec("c", "y", 1),
        json!({"type": "user"}),
        json!({"type": "assistant", "message": {"usage": {}}}),
        json!({"type": "assistant", "message": {"id": "z"}}),
    ]);
    assert_eq!(
        got,
        json!({"fresh": 14, "cached": 6, "output": 11, "turns": 3, "model": "y"})
    );
    assert_eq!(fold_usage(&[])["model"], "none");
    let bare = json!({"type": "assistant", "message": {"id": "a", "usage": {}}});
    assert_eq!(fold_usage(&[bare])["model"], "unknown");
    let ties = fold_usage(&[rec("a", "first", 1), rec("b", "second", 1)]);
    assert_eq!(ties["model"], "first");
}

#[test]
fn the_catalog_lists_the_agents_runs_newest_first() {
    let (top, t) = world("mt-catalog");
    let sub = t.projects.join("-diagram-x/s1/subagents");
    std::fs::create_dir_all(&sub).unwrap();
    std::fs::create_dir_all(t.projects.join("other")).unwrap();
    let tr = transcript(&top, "look at   /tmp/l7r-nothing-here/x");
    std::fs::copy(&tr, sub.join("agent-a.jsonl")).unwrap();
    std::fs::copy(top.join("agent-a.meta.json"), sub.join("agent-a.meta.json")).unwrap();
    std::fs::write(
        sub.join("agent-other.meta.json"),
        json!({"agentType": "impl-drift"}).to_string(),
    )
    .unwrap();
    std::fs::write(sub.join("agent-bad.meta.json"), "{").unwrap();
    let mut later = super::records_of(&sub.join("agent-a.jsonl"));
    later[0]["timestamp"] = json!("2026-10-25T10:00:00.000Z");
    lines(&sub.join("agent-b.jsonl"), &later);
    std::fs::copy(top.join("agent-a.meta.json"), sub.join("agent-b.meta.json")).unwrap();
    std::fs::write(
        sub.join("agent-gone.meta.json"),
        json!({"agentType": "spec-fidelity"}).to_string(),
    )
    .unwrap();
    let got = cli(&words(&["catalog", "spec-fidelity"]), &t);
    assert_eq!(got.code, 0);
    assert!(
        got.stdout.starts_with("2026-10-25T10:00  ")
            && got
                .stdout
                .contains("prompt=33 reply=19  CLEAR=1 OK=2\n    look at /tmp/l7r-nothing-here/x"),
        "{}",
        got.stdout
    );
    assert_eq!(
        cli(
            &words(&["catalog", "spec-fidelity", "--since", "2027-01-01"]),
            &t
        )
        .stdout,
        ""
    );
    assert_eq!(
        cli(&words(&["catalog", "spec-fidelity", "--replayable"]), &t).stdout,
        ""
    );
}

#[test]
fn the_newest_file_is_found_at_any_depth() {
    let top = crate::checks::scratch("mt-newest");
    let empty = top.join("empty");
    std::fs::create_dir_all(&empty).unwrap();
    assert!(super::newest(&empty) > 0.0);
    std::fs::create_dir_all(top.join("a/b")).unwrap();
    std::fs::write(top.join("a/one"), "x").unwrap();
    std::fs::write(top.join("a/b/two"), "x").unwrap();
    assert!(super::newest(&top.join("a")) > 0.0);
}

#[test]
fn a_case_with_no_reflog_at_the_time_stays_at_head() {
    let (_, t, out, got) = case("mt-fallback", "the prompt", &[]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert_eq!(
        meta(&out)["commit"].as_str().unwrap(),
        git(&t.clone, &["rev-parse", "HEAD"])
    );
}

#[test]
fn a_run_is_replayable_only_if_its_inputs_are_as_they_were() {
    let top = crate::checks::scratch("mt-replayable");
    let bundle = top.join("bundle");
    std::fs::create_dir_all(&bundle).unwrap();
    std::fs::write(bundle.join("a"), "x").unwrap();
    let shown = bundle.join("a").display().to_string();
    let mut run = read(&transcript(&top, &shown));
    run.prompt = format!(
        "/tmp/{}",
        bundle.strip_prefix("/tmp").unwrap_or(&bundle).display()
    )
    .replace("/tmp//tmp", "/tmp");
    run.started = "2026-10-20T10:00:00Z".to_owned();
    assert!(!replayable(&run), "written after the run started");
    run.started = "2999-01-01T00:00:00Z".to_owned();
    assert!(replayable(&run));
    run.prompt = "/tmp/l7r-nothing-here/x".to_owned();
    assert!(!replayable(&run), "gone");
    run.prompt = "no paths".to_owned();
    assert!(replayable(&run));
}

fn case(tag: &str, prompt: &str, extra: &[&str]) -> (PathBuf, Trial, PathBuf, crate::Reply) {
    let (top, t) = world(tag);
    let tr = transcript(&top, prompt);
    let out = top.join("case");
    let (a, b) = (tr.display().to_string(), out.display().to_string());
    let mut args = words(&["prepare", &a, &b]);
    args.extend(words(extra));
    let got = cli(&args, &t);
    (top, t, out, got)
}

fn meta(out: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(out.join("meta.json")).unwrap()).unwrap()
}

#[test]
fn prepare_builds_a_case_at_head_with_the_tested_model() {
    let (_, t, out, got) = case(
        "mt-prepare",
        "read /diagram/specs/x and /diagram/.clones/other/l7r/y",
        &["--head", "--omit-claude-md", "yes"],
    );
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    let tree = out.join("tree");
    let there = tree.display();
    assert_eq!(
        std::fs::read_to_string(out.join("prompt.txt")).unwrap(),
        format!("read {there}/specs/x and {there}/l7r/y")
    );
    assert_eq!(
        std::fs::read_to_string(out.join("recorded-reply.md")).unwrap(),
        "CLEAR and OK and OK"
    );
    let m = meta(&out);
    assert_eq!(
        m["commit"].as_str().unwrap(),
        git(&t.clone, &["rev-parse", "HEAD"])
    );
    assert_eq!(m["model"], "claude-sonnet-5-5");
    assert_eq!(m["omitClaudeMd"], true);
    let agent = std::fs::read_to_string(tree.join(".claude/agents/spec-fidelity.md")).unwrap();
    assert!(agent.contains("model: claude-sonnet-5-5\nomitClaudeMd: true\n---"));
    let again = cli(
        &words(&[
            "prepare",
            m["recorded"].as_str().unwrap(),
            &out.display().to_string(),
            "--head",
            "--model",
            "other",
            "--omit-claude-md",
            "no",
            "--as-subagent",
        ]),
        &t,
    );
    assert_eq!(again.code, 0);
    assert_eq!(meta(&out)["omitClaudeMd"], false);
    assert_eq!(meta(&out)["as_subagent"], true);
}

#[test]
fn prepare_reads_the_commit_from_the_reflog_and_by_hand() {
    let (top, t) = world("mt-commit");
    let sibling = t.clone.parent().unwrap().join("judged");
    let (from, to) = (t.clone.display().to_string(), sibling.display().to_string());
    git(&t.clone, &["clone", "-q", &from, &to]);
    let head = git(&t.clone, &["rev-parse", "HEAD"]);
    git(
        &t.clone,
        &["config", "uploadpack.allowAnySHA1InWant", "true"],
    );
    let tr = transcript(&top, "/diagram/.clones/judged/specs/x");
    let mut rs = super::records_of(&tr);
    rs[0]["timestamp"] = json!("2999-01-01T00:00:00Z");
    rs[0]["cwd"] = json!("/diagram/.clones/judged");
    lines(&tr, &rs);
    let out = top.join("case");
    let (a, b) = (tr.display().to_string(), out.display().to_string());
    let got = cli(&words(&["prepare", &a, &b]), &t);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    assert_eq!(meta(&out)["commit"].as_str().unwrap(), head);
    let by_hand = top.join("case2");
    let c = by_hand.display().to_string();
    assert_eq!(
        cli(&words(&["prepare", &a, &c, "--at", &head[..9]]), &t).code,
        0
    );
    assert_eq!(meta(&by_hand)["commit"].as_str().unwrap(), head);
    assert_eq!(
        cli(&words(&["prepare", &a, &c, "--at", "nosuchrev"]), &t).code,
        2
    );
}

#[test]
fn prepare_names_what_is_not_a_fair_re_run() {
    let (top, t, out, got) = case("mt-unfair", "/tmp/l7r-nothing-here/x", &["--head"]);
    assert_eq!(got.code, 1);
    assert!(got
        .stdout
        .contains("MISSING (not a fair re-run): /tmp/l7r-nothing-here/x"));
    assert_eq!(meta(&out)["missing"][0], "/tmp/l7r-nothing-here/x");
    let bundle = std::env::temp_dir().join(format!(
        "{}-bundle",
        top.file_name().unwrap().to_string_lossy()
    ));
    std::fs::create_dir_all(bundle.join("deep")).unwrap();
    std::fs::write(bundle.join("deep/MANIFEST.md"), "x").unwrap();
    let tr = transcript(
        &top,
        &format!(
            "{} and {}/deep/MANIFEST.md",
            bundle.display(),
            bundle.display()
        ),
    );
    let b2 = top.join("case2");
    let got = cli(
        &words(&[
            "prepare",
            &tr.display().to_string(),
            &b2.display().to_string(),
            "--head",
        ]),
        &t,
    );
    let _ = cli(
        &words(&[
            "prepare",
            &tr.display().to_string(),
            &b2.display().to_string(),
            "--head",
        ]),
        &t,
    );
    std::fs::remove_dir_all(&bundle).unwrap();
    assert_eq!(got.code, 1);
    assert!(got
        .stdout
        .contains("CHANGED SINCE the run (not a fair re-run)"));
    assert!(std::fs::read_to_string(b2.join("prompt.txt"))
        .unwrap()
        .contains(&b2.join("inputs").display().to_string()));
    assert!(b2
        .join("inputs")
        .join(bundle.file_name().unwrap())
        .join("deep/MANIFEST.md")
        .is_file());
}

#[test]
fn prepare_fails_cleanly_outside_a_repository() {
    let top = crate::checks::scratch("mt-norepo");
    let t = Trial {
        clone: top.join("no"),
        projects: top.join("p"),
        claude: "x".to_owned(),
    };
    let tr = transcript(&top, "p");
    assert_eq!(
        cli(
            &words(&[
                "prepare",
                &tr.display().to_string(),
                &top.join("o").display().to_string()
            ]),
            &t
        )
        .code,
        2
    );
}

#[test]
fn the_runs_start_and_their_cost_is_told() {
    let (top, t, out, _) = case("mt-runs", "the prompt", &["--head"]);
    let there = out.display().to_string();
    let got = cli(&words(&["run", &there, "--runs", "1"]), &t);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.starts_with("started run 1: pid "));
    let pid = std::fs::read_to_string(out.join("run-1.pid")).unwrap();
    assert_eq!(pid.split_whitespace().count(), 2);
    let _ = (0..2000).find(|_| {
        std::thread::sleep(std::time::Duration::from_millis(2));
        std::fs::read_to_string(out.join("run-1.json")).is_ok_and(|t| t.ends_with('}'))
    });
    std::fs::write(out.join("run-2.json"), "{").unwrap();
    let got = cli(&words(&["usage", &there]), &t);
    assert_eq!(got.stdout, "recorded  model=opus turns=1 in=110 out=7\nrun-1  models=['m'] turns=3 in=1,000 out=5 2 s cost=$0.50\nrun-2  not finished\n", "{}", got.stderr);
    assert_eq!(
        std::fs::read_to_string(out.join("run-1-reply.md")).unwrap(),
        "the reply"
    );
    let sub = t.projects.join("-diagram/sess/subagents");
    assert_eq!(cli(&words(&["collect", &there]), &t).code, 1);
    std::fs::create_dir_all(&sub).unwrap();
    std::fs::copy(top.join("agent-a.jsonl"), sub.join("agent-z.jsonl")).unwrap();
    std::fs::write(out.join("run-3.json"), "{\"session_id\": \"\"}").unwrap();
    let got = cli(&words(&["collect", &there]), &t);
    assert_eq!(got.code, 0, "{}", got.stdout);
    assert_eq!(
        std::fs::read_to_string(out.join("reply-1.md")).unwrap(),
        "CLEAR and OK and OK"
    );
}

#[test]
fn an_as_subagent_run_dispatches_the_check_once() {
    let (_, t, out, _) = case("mt-sub", "p", &["--head", "--as-subagent"]);
    let cmd = t.run_command(&out, &meta(&out));
    assert_eq!(&cmd[1..4], ["-p", "--model", "sonnet"]);
    assert!(
        cmd.last()
            .unwrap()
            .contains("subagent_type \"spec-fidelity\"")
            && cmd.last().unwrap().contains("prompt.txt")
    );
    assert!(cmd.contains(&"{\"disableAllHooks\": true}".to_owned()));
}

#[test]
fn run_all_starts_what_is_unfinished_and_holds_its_limit() {
    let (top, t, out, _) = case("mt-all", "p", &["--head"]);
    std::fs::write(out.join("run-1.json"), "{}").unwrap();
    std::fs::create_dir(top.join("not-a-case")).unwrap();
    let got = cli(
        &words(&[
            "run-all",
            &top.display().to_string(),
            "--runs",
            "3",
            "--parallel",
            "1",
        ]),
        &t,
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("all 2 run(s) finished"));
    assert_eq!(
        std::fs::read_to_string(out.join("run-1.json")).unwrap(),
        "{}"
    );
    assert!(std::fs::read_to_string(out.join("run-3.json"))
        .unwrap()
        .contains("the reply"));
}

#[test]
fn a_run_that_cannot_start_says_so() {
    let (_, mut t, out, _) = case("mt-nostart", "p", &["--head"]);
    t.claude = "/nonexistent/claude".to_owned();
    assert_eq!(
        cli(
            &words(&["run", &out.display().to_string(), "--runs", "1"]),
            &t
        )
        .code,
        2
    );
    let root = out.parent().unwrap().display().to_string();
    assert_eq!(cli(&words(&["run-all", &root, "--runs", "1"]), &t).code, 2);
}

#[test]
fn a_snapshot_is_rebuilt_on_both_sides_with_its_dispatch() {
    let unit = "building-review--x";
    let prompt = format!("/diagram/.clones/c/.git/review-snapshot/{unit}/clone and /diagram/.clones/c/.git/review-snapshot/review--nosuch/clone");
    let (top, t, out, _) = case("mt-snapshot", &prompt, &["--head"]);
    assert_eq!(meta(&out)["rebuild"], json!([unit, "review--nosuch"]));
    let recorded = meta(&out)["recorded"].as_str().unwrap().to_owned();
    let mut rs = super::records_of(Path::new(&recorded));
    let body = format!(
        "UNIT: {unit}\nsee /diagram/.clones/c/x\nas your last act, and quote the line it prints."
    );
    rs.push(
        json!({"type": "user", "message": {"content": [{"type": "tool_result", "content": body}]}}),
    );
    lines(Path::new(&recorded), &rs);
    let got = cli(&words(&["snapshot", &out.display().to_string()]), &t);
    assert_eq!(got.code, 1, "{}{}", got.stdout, got.stderr);
    assert!(
        got.stdout
            .contains("review--nosuch: no nosuch in the clone checkout")
            && got
                .stdout
                .contains("; no dispatch.md read in the recorded run")
    );
    let dest = out.join("tree/.git/review-snapshot").join(unit);
    assert!(
        dest.join("clone/x.json").is_file()
            && dest.join("main/x.json").is_file()
            && !dest.join("clone/other.txt").exists()
    );
    assert!(std::fs::read_to_string(dest.join("dispatch.md"))
        .unwrap()
        .contains(&out.join("tree/x").display().to_string()));
    assert_eq!(top.join("case"), out);
}

#[test]
fn a_verb_on_a_case_that_is_not_there_is_refused() {
    let (top, t) = world("mt-absent");
    let gone = top.join("none").display().to_string();
    for verb in ["run", "usage", "snapshot"] {
        assert_eq!(cli(&words(&[verb, &gone]), &t).code, 2, "{verb}");
    }
    assert_eq!(cli(&words(&["collect", &gone]), &t).code, 1);
    assert!(cli(&words(&["run-all", &gone]), &t)
        .stdout
        .contains("all 0 run(s)"));
}

#[test]
fn a_malformed_request_is_refused() {
    let (_, t) = world("mt-usage");
    assert_eq!(cli(&[], &t).code, 2);
    assert_eq!(cli(&words(&["catalog"]), &t).code, 2);
    assert_eq!(cli(&words(&["prepare", "only-one"]), &t).code, 2);
    assert_eq!(cli(&words(&["frobnicate", "x"]), &t).code, 2);
}

#[test]
fn the_live_trial_looks_in_the_users_projects() {
    let t = super::live(Path::new("/h"), Path::new("/c"));
    assert_eq!(
        (t.projects.display().to_string(), t.claude.as_str()),
        ("/h/.claude/projects".to_owned(), "claude")
    );
}
