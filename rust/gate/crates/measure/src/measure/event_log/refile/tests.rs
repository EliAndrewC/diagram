//! The re-filing (feature 451 T26) on a scratch clone: two features' logs, the misfiled lines each rule moves, the lines it leaves, the
//! counts, a dry run, a second run moving nothing, and the source written back with a hook's late line kept.

use std::path::Path;

use serde_json::Value;

use super::write_back;
use l7r_shared::env::Rooted;

// Each test reads its own environment, never the session's exports (feature 451 T38): these shadow the crate's.
fn cli(args: &[String]) -> crate::Reply {
    super::cli_in(args, Rooted::with(".", &[]).reader())
}

fn given(args: &[String]) -> Option<super::Given> {
    super::given(args, Rooted::with(".", &[]).reader())
}

#[test]
fn the_process_reader_answers_the_usage_as_its_own() {
    assert_eq!(super::cli(&args(&[])).code, cli(&args(&[])).code);
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn lines(path: &Path) -> Vec<Value> {
    std::fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

fn ids(path: &Path) -> Vec<String> {
    lines(path)
        .iter()
        .map(|e| {
            format!(
                "{}:{}",
                e["id"].as_str().unwrap_or("-"),
                e["task"].as_str().unwrap_or("-")
            )
        })
        .collect()
}

/// A clone working 449-b and 451-a; 385-c also has a `T03`, never started here.
fn world(d: &Path) {
    put(
        &d.join("specs/449-b/tasks.md"),
        "- [ ] T226 x\n- [ ] T236 y\n",
    );
    put(
        &d.join("specs/451-a/tasks.md"),
        "- [x] T03 x\n- [ ] T26 y\n",
    );
    put(&d.join("specs/451-a/tasks-done.md"), "- [x] T01 z\n");
    put(
        &d.join("specs/385-c/tasks.md"),
        "- [ ] T03 old\n- [ ] T99 old\n",
    );
    put(
        &d.join(".git/task-starts.jsonl"),
        concat!(
            "{\"feature\": \"385-c\", \"task\": \"T03\", \"utc\": \"2026-10-01T00:00:00Z\"}\n",
            "{\"feature\": \"449-b\", \"task\": \"T226\", \"utc\": \"2026-11-20T05:00:00Z\"}\n",
            "not json\n",
            "{\"feature\": \"451-a\", \"task\": \"T03\", \"utc\": \"2026-11-20T07:00:00Z\"}\n",
            "{\"feature\": \"451-a\", \"task\": \"T26\", \"utc\": \"2026-11-20T08:00:00Z\"}\n",
            "{\"feature\": \"449-b\", \"task\": \"T236\", \"utc\": \"2026-11-20T08:00:01Z\"}\n",
            "{\"feature\": \"385-c\", \"task\": \"T50\", \"utc\": \"2026-11-20T08:00:02Z\"}\n",
            "{\"feature\": \"449-b\", \"task\": \"T88\", \"utc\": \"2026-11-20T08:00:03Z\"}\n",
            "{\"feature\": \"449-b\"}\n",
        ),
    );
    let sub = d.join("projects/p/s1/subagents");
    put(
        &sub.join("agent-a451.meta.json"),
        r#"{"description":"451 T26: each line","toolUseId":"tu451"}"#,
    );
    put(
        &sub.join("agent-afeat.meta.json"),
        r#"{"description":"spec-fidelity round 2 on 451"}"#,
    );
    put(
        &sub.join("agent-a449.meta.json"),
        r#"{"description":"449 T236: the reed strip","toolUseId":"tu449"}"#,
    );
    put(&sub.join("agent-bad.meta.json"), "not json");
    put(&sub.join("notes.txt"), "");
}

const LOG449: &str = concat!(
    // by brief: a 451 builder's lines, their task from the brief
    "{\"t\":\"2026-11-20T08:01:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"b1\",\"by\":\"a451\",\"task\":\"T236\"}\n",
    "{\"t\":\"2026-11-20T08:02:00Z\",\"sid\":\"s1\",\"ev\":\"SubagentStop\",\"id\":\"b2\",\"aid\":\"a451\"}\n",
    // the dispatch's own lines: by its agent id, by its tool-use id
    "{\"t\":\"2026-11-20T08:00:30Z\",\"sid\":\"s1\",\"ev\":\"PostToolUse\",\"tool\":\"Agent\",\"id\":\"b3\",\"aid\":\"a451\"}\n",
    "{\"t\":\"2026-11-20T08:00:30Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"tool\":\"Agent\",\"id\":\"tu451\"}\n",
    // a brief naming the feature, no task: a task of 451 kept; else 451's start in force; else none
    "{\"t\":\"2026-11-20T08:03:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"b4\",\"by\":\"afeat\",\"task\":\"T01\"}\n",
    "{\"t\":\"2026-11-20T08:03:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"b5\",\"by\":\"afeat\",\"task\":\"T236\"}\n",
    "{\"t\":\"2026-11-20T06:00:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"b6\",\"by\":\"afeat\"}\n",
    // a 451 builder's own T= of 449 stays
    "{\"t\":\"2026-11-20T08:04:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"k1\",\"by\":\"a451\",\"make\":\"tick\",\"task\":\"T236\"}\n",
    // a 451 builder's own T= of 451 moves with it, its task kept over the brief's
    "{\"t\":\"2026-11-20T08:04:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"o1\",\"by\":\"a451\",\"make\":\"land\",\"task\":\"T03\"}\n",
    // by task id: the start in force at the line's time (the start's own PreToolUse just before its row)
    "{\"t\":\"2026-11-20T07:59:59.500Z\",\"sid\":\"m\",\"ev\":\"PreToolUse\",\"id\":\"i1\",\"make\":\"task-start\",\"task\":\"T26\"}\n",
    "{\"t\":\"2026-11-20T07:30:00Z\",\"sid\":\"m\",\"ev\":\"PreToolUse\",\"id\":\"i2\",\"task\":\"T03\"}\n",
    // kept: a 449 task, no task, a task no start names by then, one whose starter does not have it, a bad line, no time
    "{\"t\":\"2026-11-20T08:05:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k2\",\"task\":\"T236\"}\n",
    "{\"t\":\"2026-11-20T08:05:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k3\"}\n",
    "{\"t\":\"2026-09-01T00:00:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k4\",\"task\":\"T03\"}\n",
    "{\"t\":\"2026-11-20T08:05:00Z\",\"ev\":\"Stop\",\"id\":\"k5\",\"by\":\"a451\",\"task\":\"T99\"}\n",
    "not json\n",
    "{\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k6\"}\n",
    "{\"t\":\"2026-11-20T08:05:00Z\",\"sid\":\"none\",\"ev\":\"Stop\",\"id\":\"k7\",\"by\":\"bad\"}\n",
    // a task started by a feature that does not have it; a task whose start in force is the log's own feature's
    "{\"t\":\"2026-11-20T08:05:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k8\",\"task\":\"T50\"}\n",
    "{\"t\":\"2026-11-20T08:05:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k9\",\"task\":\"T88\"}\n",
);

const LOG451: &str = concat!(
    "{\"t\":\"2026-11-20T08:06:00Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"id\":\"c1\",\"by\":\"a449\"}\n",
    "{\"t\":\"2026-11-20T05:30:00Z\",\"sid\":\"m\",\"ev\":\"PreToolUse\",\"id\":\"c2\",\"make\":\"task-start\",\"task\":\"T226\"}\n",
    "{\"t\":\"2026-11-20T08:06:00Z\",\"sid\":\"m\",\"ev\":\"PreToolUse\",\"id\":\"c3\",\"task\":\"T26\"}\n",
);

#[test]
fn each_misfiled_line_moves_to_the_feature_of_its_task_once() {
    let d = crate::checks::scratch("measure-refile");
    world(&d);
    let ev = d.join("events");
    put(&ev.join("449-b.jsonl"), LOG449);
    put(&ev.join("451-a.jsonl"), LOG451);
    let root = d.display().to_string();
    let dir = ev.display().to_string();
    let projects = d.join("projects").display().to_string();
    let run = |extra: &[&str]| {
        let mut a = vec!["--root", &root, "--dir", &dir, "--projects", &projects];
        a.extend_from_slice(extra);
        cli(&args(&a))
    };
    // a dry run counts and writes nothing
    let dry = run(&["--dry-run"]);
    assert_eq!(dry.code, 0, "{}", dry.stderr);
    assert!(
        dry.stdout
            .contains("refile: 449-b -> 451-a: 10 lines (8 by brief, 2 by task id)\n"),
        "{}",
        dry.stdout
    );
    assert!(
        dry.stdout
            .contains("refile: 451-a -> 449-b: 2 lines (1 by brief, 1 by task id)\n"),
        "{}",
        dry.stdout
    );
    assert!(
        dry.stdout
            .contains("refile: 12 lines moved (dry run: nothing written)\n"),
        "{}",
        dry.stdout
    );
    assert!(
        dry.stdout.contains("refile: 4 lines left whose task"),
        "{}",
        dry.stdout
    );
    assert_eq!(
        std::fs::read_to_string(ev.join("449-b.jsonl")).unwrap(),
        LOG449
    );
    // one moved line already in its target (a run cut short) is not appended twice
    let first = LOG449.lines().next().unwrap().replace("T236", "T26");
    put(&ev.join("451-a.jsonl"), &format!("{LOG451}{first}\n"));
    let r = run(&[]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout.contains("refile: 12 lines moved\n"),
        "{}",
        r.stdout
    );
    assert_eq!(
        ids(&ev.join("449-b.jsonl")),
        [
            "k1:T236", "k2:T236", "k3:-", "k4:T03", "k5:T99", "k6:-", "k7:-", "k8:T50", "k9:T88",
            "c1:T236", "c2:T226"
        ]
    );
    assert_eq!(
        ids(&ev.join("451-a.jsonl")),
        [
            "c3:T26",
            "b1:T26",
            "b2:T26",
            "b3:T26",
            "tu451:T26",
            "b4:T01",
            "b5:T26",
            "b6:-",
            "o1:T03",
            "i1:T26",
            "i2:T03"
        ]
    );
    assert!(std::fs::read_to_string(ev.join("449-b.jsonl"))
        .unwrap()
        .contains("not json\n"));
    // idempotent: the second run moves nothing
    let again = run(&[]);
    assert!(
        again.stdout.contains("refile: 0 lines moved\n"),
        "{}",
        again.stdout
    );
}

/// 451 T56's live shape: a 451 T47 builder's spec-fidelity rounds, briefed `T47 plan review`, filed in 385's log by 385's T47 start of
/// 2026-10-18 - 385 has no T47, 451 has (archived), and 451's T45 was the clone's last start before them (feature.json then).
fn stale_world(d: &Path) {
    put(&d.join("specs/385-c/tasks.md"), "- [ ] T03 old\n");
    put(&d.join("specs/449-b/tasks.md"), "- [ ] T236 y\n");
    put(&d.join("specs/451-a/tasks.md"), "- [ ] T56 y\n");
    put(&d.join("specs/451-a/tasks-done.md"), "- [x] T47 flake\n");
    put(
        &d.join(".git/task-starts.jsonl"),
        concat!(
            "{\"feature\": \"385-c\", \"task\": \"T47\", \"utc\": \"2026-10-18T17:01:28Z\"}\n",
            "{\"feature\": \"449-b\", \"task\": \"T236\", \"utc\": \"2026-11-20T10:00:00Z\"}\n",
            "{\"feature\": \"451-a\", \"task\": \"T45\", \"utc\": \"2026-11-20T23:36:12Z\"}\n",
            "{\"feature\": \"385-c\", \"task\": \"T03\", \"utc\": \"2026-11-21T01:00:00Z\"}\n",
        ),
    );
    let sub = d.join("projects/p/s1/subagents");
    put(
        &sub.join("agent-abld.meta.json"),
        r#"{"description":"451 T47: the pages coverage flake","toolUseId":"tubld"}"#,
    );
    put(
        &sub.join("agent-asf.meta.json"),
        r#"{"description":"T47 plan review","toolUseId":"tusf","parentAgentId":"abld"}"#,
    );
}

const LOG385: &str = concat!(
    // the builder's dispatch of its review (its brief by the call's tool-use id) and the review's own line: no fresh start names T47,
    // so the writer's fallback, the clone's last start before the line (451-a's T45: feature.json then), which has T47
    "{\"t\":\"2026-11-20T23:56:18.017Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"tool\":\"Agent\",\"id\":\"tusf\",\"by\":\"abld\",\"task\":\"T47\"}\n",
    "{\"t\":\"2026-11-20T23:56:24.813Z\",\"sid\":\"s1\",\"ev\":\"PreToolUse\",\"tool\":\"Bash\",\"id\":\"f2\",\"by\":\"asf\",\"task\":\"T47\"}\n",
    // a fresh start still wins: 449-b's T236 of 10:00
    "{\"t\":\"2026-11-20T11:00:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"i3\",\"task\":\"T236\"}\n",
    // kept: no start at all before the line; the fallback (449-b) without the task; the fallback the log's own feature
    "{\"t\":\"2026-10-01T00:00:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k10\",\"task\":\"T47\"}\n",
    "{\"t\":\"2026-11-20T11:00:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k11\",\"task\":\"T47\"}\n",
    "{\"t\":\"2026-11-21T01:05:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"id\":\"k12\",\"task\":\"T47\"}\n",
);

#[test]
fn a_task_whose_only_start_is_stale_falls_to_the_feature_of_the_last_start() {
    let d = crate::checks::scratch("measure-refile-stale");
    stale_world(&d);
    let ev = d.join("events");
    put(&ev.join("385-c.jsonl"), LOG385);
    let root = d.display().to_string();
    let dir = ev.display().to_string();
    let projects = d.join("projects").display().to_string();
    let run = |extra: &[&str]| {
        let mut a = vec!["--root", &root, "--dir", &dir, "--projects", &projects];
        a.extend_from_slice(extra);
        cli(&args(&a))
    };
    let dry = run(&["--dry-run"]);
    assert_eq!(dry.code, 0, "{}", dry.stderr);
    for want in [
        "refile: 385-c -> 451-a: 2 lines (0 by brief, 0 by task id, 2 by the fallback)\n",
        "refile: 385-c -> 449-b: 1 lines (0 by brief, 1 by task id)\n",
        "refile: 3 lines moved (dry run: nothing written)\n",
        "refile: 3 lines left whose task",
    ] {
        assert!(dry.stdout.contains(want), "{want:?} in {}", dry.stdout);
    }
    let r = run(&[]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert_eq!(
        ids(&ev.join("385-c.jsonl")),
        ["k10:T47", "k11:T47", "k12:T47"]
    );
    assert_eq!(ids(&ev.join("449-b.jsonl")), ["i3:T236"]);
    let moved = lines(&ev.join("451-a.jsonl"));
    assert_eq!(
        moved
            .iter()
            .map(|e| format!("{}:{}:{}", e["id"], e["task"], e["fallback"]))
            .collect::<Vec<_>>(),
        ["\"tusf\":\"T47\":true", "\"f2\":\"T47\":true"]
    );
    // the task-id move is no fallback; a second run moves nothing
    assert!(lines(&ev.join("449-b.jsonl"))[0].get("fallback").is_none());
    let again = run(&[]);
    assert!(
        again.stdout.contains("refile: 0 lines moved\n"),
        "{}",
        again.stdout
    );
}

#[test]
fn the_command_line_and_its_failures() {
    assert_eq!(cli(&args(&[])).code, 2);
    assert_eq!(cli(&args(&["--root"])).code, 2);
    assert_eq!(cli(&args(&["--nonsense"])).code, 2);
    let g = given(&args(&["--root", "/r"])).unwrap();
    assert!(!g.dir.as_os_str().is_empty() && g.projects.ends_with(".claude/projects") && !g.dry);
    let d = crate::checks::scratch("measure-refile-fail");
    world(&d);
    let ev = d.join("events");
    let root = d.display().to_string();
    let dir = ev.display().to_string();
    let run = || {
        cli(&args(&[
            "--root",
            &root,
            "--dir",
            &dir,
            "--projects",
            "/nonexistent",
        ]))
    };
    // a log that cannot be read
    std::fs::create_dir_all(ev.join("x.jsonl")).unwrap();
    assert_eq!(run().code, 1);
    std::fs::remove_dir(ev.join("x.jsonl")).unwrap();
    // a target that cannot be appended to
    put(
        &ev.join("449-b.jsonl"),
        "{\"t\":\"2026-11-20T07:30:00Z\",\"sid\":\"m\",\"ev\":\"Stop\",\"task\":\"T03\"}\n",
    );
    std::fs::create_dir_all(ev.join("451-a.jsonl")).unwrap();
    let r = run();
    assert_eq!(r.code, 1, "{}", r.stdout);
    assert!(r.stderr.starts_with("refile: "));
    std::fs::remove_dir(ev.join("451-a.jsonl")).unwrap();
    // a source that cannot be written back
    std::fs::create_dir_all(ev.join("449-b.jsonl.refile")).unwrap();
    assert_eq!(run().code, 1);
}

#[test]
fn a_line_a_hook_appends_during_the_rewrite_is_kept() {
    let d = crate::checks::scratch("measure-refile-late");
    let log = d.join("f.jsonl");
    put(&log, "a\nb\nlate\n");
    write_back(&log, b"a\n".to_vec(), 4).unwrap();
    assert_eq!(std::fs::read_to_string(&log).unwrap(), "a\nlate\n");
}
