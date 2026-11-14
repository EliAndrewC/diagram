//! The launch: the floor's flags, the write cap at launch, every kind of queue item, the detached start, and the command line's refusals
//! and raises. The queue's own loop is `work/tests.rs`; neither starts a real session.

use std::collections::HashMap;
use std::path::{Path, PathBuf};

use super::{
    admit, brief_feature, cli, command, detach, floor_flags, launch, new_item, plan, uuid4, Ctx,
    Stop, WAIT,
};
use crate::escape_log;

pub(super) fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

pub(super) fn executable(path: &Path, text: &str) {
    use std::os::unix::fs::PermissionsExt as _;
    put(path, text);
    std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o755)).unwrap();
}

/// A clone `<mirror>/.clones/me` with the two prompt files, its record holding questions 0001-0003 (no real pointer: a scratch record).
pub(super) fn clone(d: &Path) -> String {
    let root = std::fs::canonicalize(d).unwrap().join(".clones/me");
    put(
        &root.join("scripts/container/append-system-prompt.md"),
        "the standing authorization\n",
    );
    put(
        &root.join("scripts/container/page-session-rules.md"),
        "  the rules  \n",
    );
    for n in ["0001", "0002", "0003"] {
        put(&root.join(format!("research/questions/{n}-q.html")), "");
    }
    std::fs::create_dir_all(root.join(".git")).unwrap();
    root.to_string_lossy().into_owned()
}

pub(super) fn ctx<'a>(root: &str, escape: &'a escape_log::Env<'a>) -> Ctx<'a> {
    Ctx {
        root: root.to_owned(),
        name: "me".to_owned(),
        extra: vec!["--model".to_owned(), "opus".to_owned()],
        cwd: "/".to_owned(),
        escape,
    }
}

pub(super) fn write_brief(n: usize) -> String {
    let items: String = (0..n)
        .flat_map(|i| ["- A".to_owned(), (10 + i).to_string(), " item\n".to_owned()])
        .collect();
    format!("# brief\n\n## Your items\n{items}")
}

#[test]
fn the_floor_s_flags_exclude_both_root_files_and_append_the_rules() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-floor");
    let root = clone(&d);
    let flags = floor_flags(&format!("{root}/"));
    let mirror = root.trim_end_matches("/.clones/me");
    assert_eq!(
        &flags[..4],
        [
            "--disable-slash-commands",
            "--strict-mcp-config",
            "--tools",
            "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch"
        ]
    );
    assert_eq!(
        flags[5],
        format!("{{\"claudeMdExcludes\": [\"{mirror}/CLAUDE.md\", \"{root}/CLAUDE.md\"]}}")
    );
    assert_eq!(
        flags[6..],
        [
            "--append-system-prompt".to_owned(),
            "the standing authorization\n\nthe rules".to_owned()
        ]
    );
    assert_eq!(floor_flags("/plain").len(), 6);
    assert_eq!(
        floor_flags("/plain")[5],
        "{\"claudeMdExcludes\": [\"/plain/CLAUDE.md\"]}"
    );
    let id = uuid4();
    assert_eq!((id.len(), &id[14..15]), (36, "4"));
    assert!(matches!(&id[19..20], "8" | "9" | "a" | "b"));
}

#[test]
fn the_write_cap_admits_refuses_or_lets_a_reason_through() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-admit");
    let root = clone(&d);
    let logs = d.join("log").to_string_lossy().into_owned();
    let vars: HashMap<&str, String> = [("GUARD_LOG_DIR", logs.clone())].into_iter().collect();
    let var = |k: &str| vars.get(k).cloned();
    let esc = escape_log::Env {
        var: &var,
        cwd: PathBuf::from(&root),
        command: "runner".to_owned(),
    };
    let c = ctx(&root, &esc);
    let b = |name: &str, text: &str| {
        let p = format!("{root}/specs/1-x/briefs/{name}");
        put(Path::new(&p), text);
        p
    };
    assert_eq!(admit(&c, &b("w.md", &write_brief(2))), Ok(true));
    assert_eq!(
        admit(&c, &b("c.md", "<!-- page-load: kind=check -->")),
        Ok(false)
    );
    let five = b("five-write.md", &write_brief(5));
    let got = admit(&c, &five);
    let refused = matches!(&got, Err(Stop::Refused(why)) if why.starts_with("five-write.md: it assigns 5 questions"));
    assert!(refused);
    assert_eq!(
        admit(&c, "/no/such.md"),
        Err(Stop::Refused("/no/such.md: no such brief".to_owned()))
    );
    assert_eq!(
        admit(&c, &b("r.md", "## Your items\n- \n")),
        Err(Stop::Raised(
            "IndexError: list index out of range".to_owned()
        ))
    );
    let with = |reason: &'static str| {
        let vars: HashMap<&str, String> = [
            ("GUARD_LOG_DIR", logs.clone()),
            ("WRITE_CAP_OK", reason.to_owned()),
        ]
        .into_iter()
        .collect();
        vars
    };
    let good = with("a deliberate larger load");
    let var = |k: &str| good.get(k).cloned();
    let esc = escape_log::Env {
        var: &var,
        cwd: PathBuf::from(&root),
        command: "runner".to_owned(),
    };
    assert_eq!(admit(&ctx(&root, &esc), &five), Ok(true));
    let thin = with("x");
    let var = |k: &str| thin.get(k).cloned();
    let esc = escape_log::Env {
        var: &var,
        cwd: PathBuf::from(&root),
        command: "runner".to_owned(),
    };
    let got = admit(&ctx(&root, &esc), &five);
    let refused = matches!(&got, Err(Stop::Refused(why)) if why.starts_with("five-write.md: WRITE_CAP_OK needs a REASON"));
    assert!(refused);
    assert_eq!(std::fs::read_dir(&logs).unwrap().count(), 2);
}

#[test]
fn a_session_s_command_and_its_feature() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-command");
    let root = clone(&d);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&root),
        command: String::new(),
    };
    let c = ctx(&root, &esc);
    let cmd = command(&c, "specs/2-y/b.md", "sid-1");
    assert_eq!(&cmd[..2], ["claude", "-p"]);
    assert!(cmd[2].starts_with("You are a fresh session started to do the work ONE brief describes. Read /specs/2-y/b.md first"));
    assert_eq!(
        &cmd[3..9],
        [
            "-n",
            "me",
            "--session-id",
            "sid-1",
            "--permission-mode",
            "bypassPermissions"
        ]
    );
    assert_eq!(
        &cmd[cmd.len() - 4..],
        ["--model", "opus", "--output-format", "json"]
    );
    assert_eq!(
        brief_feature("/r/specs/449-x/briefs/b.md", "/"),
        "specs/449-x"
    );
    assert_eq!(brief_feature("/r/specs/b.md", "/"), "");
    assert_eq!(brief_feature("/r/b.md", "/"), "");
    let made = new_item(&c, "/b.md", true).unwrap();
    assert!(Path::new(made["log"].as_str().unwrap()).is_dir());
    assert_eq!(
        (made["brief"].as_str(), made["write"].as_bool()),
        (Some("/b.md"), Some(true))
    );
    put(&d.join("plain/.git"), "");
    let broken = ctx(&d.join("plain").to_string_lossy(), &esc);
    assert!(matches!(
        new_item(&broken, "/b.md", true),
        Err(Stop::Raised(_))
    ));
}

#[test]
fn the_plan_admits_first_then_makes_each_item() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-plan");
    let root = clone(&d);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&root),
        command: String::new(),
    };
    let c = ctx(&root, &esc);
    let w = format!("{root}/w.md");
    put(Path::new(&w), &write_brief(1));
    let chk = format!("{root}/c.md");
    put(Path::new(&chk), "<!-- page-load: kind=check -->");
    let projects = d.join("projects").to_string_lossy().into_owned();
    put(
        &d.join("projects/old-sid.jsonl"),
        "{\"type\": \"queue-operation\", \"operation\": \"enqueue\", \"content\": \"<task-notification>r</task-notification>\"}\n",
    );
    let items: Vec<String> = [
        &w,
        &format!("then:{root}/plan.sh"),
        &format!("resume:old-sid:{chk}"),
        &format!("resume:new:{w}"),
        &w,
    ]
    .map(ToOwned::to_owned)
    .to_vec();
    let mut out = String::new();
    let queue = plan(&c, &projects, &items, &mut out).unwrap();
    assert_eq!(queue.len(), 5);
    assert_eq!(queue[1]["then"], format!("{root}/plan.sh"));
    assert_eq!(
        (queue[2]["sid"].as_str(), queue[2]["write"].as_bool()),
        (Some("old-sid"), Some(false))
    );
    assert_eq!(queue[2]["cmd"][5], "--resume");
    assert!(queue[2]["cmd"][2]
        .as_str()
        .unwrap()
        .contains(&format!("{root}/.git/page-sessions/old-sid/returned.md")));
    assert!(!queue[3]["cmd"][2].as_str().unwrap().contains("returned"));
    assert_eq!(queue[3]["write"], true);
    let sid = queue[0]["sid"].as_str().unwrap();
    assert!(out.starts_with(&format!(
        "page-session: w.md\n  session:    {sid}\n  transcript: {projects}/{sid}.jsonl\n  log:        {root}/.git/page-sessions/{sid}\n\
         page-session: then plan.sh - the sessions it plans are listed in .git/page-sessions/index.txt\npage-session: resume old-sid (c.md)\n"
    )));
    let five = format!("{root}/five.md");
    put(Path::new(&five), &write_brief(5));
    let mut out = String::new();
    assert!(matches!(
        plan(&c, &projects, &[w.clone(), five], &mut out),
        Err(Stop::Refused(_))
    ));
    assert_eq!(out, "");
    let bad = plan(&c, &projects, &["resume:nocolon".to_owned()], &mut out);
    assert_eq!(
        bad,
        Err(Stop::Raised(
            "ValueError: not enough values to unpack (expected 2, got 1)".to_owned()
        ))
    );
    put(&d.join("plain/.git"), "");
    let broken = ctx(&d.join("plain").to_string_lossy(), &esc);
    assert!(matches!(
        plan(&broken, &projects, &[format!("resume:s:{w}")], &mut out),
        Err(Stop::Raised(_))
    ));
    let ro = d.join("ro");
    let ro_root = ro.to_string_lossy().into_owned();
    std::fs::create_dir_all(ro.join(".git/page-sessions/s/returned.md")).unwrap();
    put(&d.join("projects/s.jsonl"), "{\"type\": \"queue-operation\", \"operation\": \"enqueue\", \"content\": \"<task-notification>r</task-notification>\"}\n");
    let ro_ctx = ctx(&ro_root, &esc);
    assert!(matches!(
        plan(&ro_ctx, &projects, &[format!("resume:s:{w}")], &mut out),
        Err(Stop::Raised(_))
    ));
}

#[test]
fn the_queue_is_started_detached_with_its_own_command_line() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-detach");
    let root = d.to_string_lossy().into_owned();
    let seen = d.join("argv");
    let exe = d.join("fake-gate");
    executable(
        &exe,
        &format!(
            "#!/bin/sh\nprintf '%s\\n' \"$PWD\" \"$@\" > {}\n",
            seen.display()
        ),
    );
    detach("setsid", &exe, &root, &["a".to_owned(), "b c".to_owned()]).unwrap();
    let started = std::time::Instant::now();
    while !seen.is_file() && started.elapsed() < std::time::Duration::from_secs(10) {
        std::thread::sleep(std::time::Duration::from_millis(20));
    }
    std::thread::sleep(std::time::Duration::from_millis(50));
    assert_eq!(
        std::fs::read_to_string(&seen).unwrap(),
        format!("{root}\npage-session\n--work\na\nb c\n")
    );
    assert!(detach("/no/such/setsid", &exe, &root, &[])
        .unwrap_err()
        .starts_with("/no/such/setsid: "));
}

#[test]
fn the_launch_refuses_raises_or_starts_and_prints_the_wait() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-launch");
    let root = clone(&d);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&root),
        command: String::new(),
    };
    let exe = d.join("fake-gate");
    executable(&exe, "#!/bin/sh\nexit 0\n");
    let a = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert!(launch(&a(&["r", "n"]), &exe, &esc, "setsid")
        .stderr
        .contains("ValueError: not enough values"));
    assert!(launch(&a(&["r", "n", "p", "x"]), &exe, &esc, "setsid")
        .stderr
        .contains("'--' is not in list"));
    let five = format!("{root}/five.md");
    put(Path::new(&five), &write_brief(5));
    let refused = launch(&a(&[&root, "me", "/p", "--", &five]), &exe, &esc, "setsid");
    assert_eq!(refused.code, 2);
    assert!(refused
        .stderr
        .starts_with("page-session: REFUSED, nothing started - five.md: it assigns 5 questions"));
    assert_eq!(
        launch(
            &a(&[&root, "me", "/p", "--", "resume:x"]),
            &exe,
            &esc,
            "setsid"
        )
        .code,
        1
    );
    // a queue of `then:` steps alone makes no session directory, so the run log has none to sit in: the Python's raise
    let bare = d.join("bare").to_string_lossy().into_owned();
    assert!(launch(
        &a(&[&bare, "me", "/p", "--", "then:/x.sh"]),
        &exe,
        &esc,
        "setsid"
    )
    .stderr
    .contains("run-"));
    let w = format!("{root}/w.md");
    put(Path::new(&w), &write_brief(1));
    let failed = launch(
        &a(&[&root, "me", "/p", "--", &w]),
        &exe,
        &esc,
        "/no/such/setsid",
    );
    assert_eq!(failed.code, 1);
    let ok = launch(
        &a(&[&root, "me", "/p", "--model", "opus", "--", &w]),
        &exe,
        &esc,
        "setsid",
    );
    assert_eq!(ok.code, 0, "{}", ok.stderr);
    let run_log = ok
        .stdout
        .lines()
        .last()
        .unwrap()
        .split("'^ALL DONE' ")
        .nth(1)
        .unwrap()
        .split(';')
        .next()
        .unwrap();
    assert!(Path::new(run_log).is_file());
    assert!(ok.stdout.contains("page-session: started - each result.json is written when its session ends, and the next session begins\n"));
    assert!(ok
        .stdout
        .ends_with(&format!("{}\n", WAIT.replace("{run_log}", run_log))));
    assert!(WAIT.contains("POLL_OK='a detached page-session queue the harness cannot track'"));
}

#[test]
fn the_command_line_s_work_form() {
    let d = l7r_gate_core::ci::fixtures::scratch("runner-cli");
    let root = clone(&d);
    let esc = escape_log::Env {
        var: &unset_var,
        cwd: PathBuf::from(&root),
        command: String::new(),
    };
    let exe = Path::new("/bin/true");
    let a = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(cli(&a(&["only-two", "x"]), exe, &esc, Vec::new()).code, 1);
    assert_eq!(cli(&a(&["--work", "r"]), exe, &esc, Vec::new()).code, 1);
    assert!(cli(
        &a(&["--work", &root, "me", "[", "[]", "/l"]),
        exe,
        &esc,
        Vec::new()
    )
    .stderr
    .contains("JSONDecodeError"));
    let log = d.join("run.log").to_string_lossy().into_owned();
    assert_eq!(
        cli(
            &a(&["--work", &root, "me", "[]", "[]", &log]),
            exe,
            &esc,
            Vec::new()
        )
        .code,
        0
    );
    assert_eq!(std::fs::read_to_string(&log).unwrap(), "ALL DONE\n");
    assert_eq!(
        cli(
            &a(&["--work", &root, "me", "[]", "[]", "/no/such/run.log"]),
            exe,
            &esc,
            Vec::new()
        )
        .code,
        1
    );
}

pub(super) fn unset_var(_: &str) -> Option<String> {
    None
}
