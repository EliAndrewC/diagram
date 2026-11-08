//! The decider on the suite's shapes (`tests/hooks/test-idle-tests-hooks.sh`, replayed through the shim, is the verdict): the timer
//! runs in-process on a tick of a millisecond, its clock a counter file.

use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};

use serde_json::json;

use super::{
    cksum, cli, decide, failures, flock, judge, launch, locate, make_in, sid_is_live, state_of,
    timer, verdict, Config, Timer, DEF_ARM,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn dir(tag: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("l7r-guard-idle-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn script(p: &Path, body: &str) {
    std::fs::write(p, format!("#!/bin/sh\n{body}\n")).unwrap();
    std::fs::set_permissions(p, std::fs::Permissions::from_mode(0o755)).unwrap();
}

/// A clone in a mirror's `.clones/`, and a fixture's configuration: no waiting, a fixed clock.
fn world(tag: &str) -> (PathBuf, Config) {
    let root = dir(tag);
    let clone = root.join("main/.clones/sess");
    std::fs::create_dir_all(clone.join(".git")).unwrap();
    std::fs::create_dir_all(root.join("sessions")).unwrap();
    script(&root.join("clock"), "cat \"$(dirname \"$0\")/now\"");
    std::fs::write(root.join("now"), "1000").unwrap();
    let vars: Vec<(String, String)> = [
        ("IDLE_FIXTURE", "1"),
        ("IDLE_TICK", "0.001"),
        ("IDLE_WAIT_S", "0"),
        ("IDLE_DEFER_S", "0"),
        (
            "IDLE_CLOCK",
            format!("sh {}", root.join("clock").display()).as_str(),
        ),
        ("IDLE_HOME", root.join("home").to_str().unwrap()),
        ("IDLE_SESSIONS_DIR", root.join("sessions").to_str().unwrap()),
        ("IDLE_ROOT", root.to_str().unwrap()),
        ("IDLE_RUN", "true"),
        ("IDLE_SUSPEND_S", "300"),
        ("IDLE_BUSY_CMD", "false"),
        ("HOME", "/h"),
    ]
    .map(|(k, v)| (k.to_owned(), v.to_owned()))
    .to_vec();
    let mut c = Config::from_vars(&vars, Path::new("/nowhere/own"), "/");
    c.exe = PathBuf::from("/bin/true");
    c.grace = std::time::Duration::from_millis(1);
    (clone, c)
}

fn armed(clone: &Path) {
    let state = json!({"session": "sess", "session_id": "", "armed_at": 1000, "wait_min": 60, "timer_pid": null});
    std::fs::write(clone.join(".git/idle-tests.json"), state.to_string()).unwrap();
}

fn record(clone: &Path, name: &str, v: &serde_json::Value) -> PathBuf {
    std::fs::create_dir_all(clone.join("dev/idle-log")).unwrap();
    let p = clone.join("dev/idle-log").join(name);
    std::fs::write(&p, v.to_string()).unwrap();
    p
}

fn event(name: &str, cwd: &Path) -> Event {
    Event {
        name: name.to_owned(),
        input: json!({"cwd": cwd.to_string_lossy(), "session_id": "sid"}),
    }
}

fn records(clone: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(clone.join("dev/idle-log")).map_or_else(
        |_| Vec::new(),
        |d| d.filter_map(Result::ok).map(|e| e.path()).collect(),
    )
}

fn timer_of<'a>(c: &'a Config, clone: &'a Path) -> Timer<'a> {
    Timer {
        c,
        clone,
        session: "sess",
        sid: "",
        sf: clone.join(".git/idle-tests.json"),
        armed: "1000".to_owned(),
        suspends: 0,
        deferrals: 0,
    }
}

#[test]
fn the_hash_is_posix_cksum_and_the_stagger_stays_in_its_band() {
    assert_eq!(
        (cksum("123456789"), cksum("sess-a"), cksum("")),
        (930_766_865, 812_959_857, 4_294_967_295)
    );
    let (_, c) = world("hash");
    assert!(
        (60..=120).contains(&c.stagger("anything")) && c.stagger("a") == c.stagger("a") && !DEF_ARM
    );
    assert!((5..=15).contains(&c.deferral("anything")));
}

#[test]
fn the_seams_are_honored_only_in_a_fixture_outside_this_tree() {
    let var = |k: &str, v: &str| (k.to_owned(), v.to_owned());
    let own = Path::new("/repo");
    let inside = Config::from_vars(
        &[
            var("IDLE_FIXTURE", "1"),
            var("IDLE_WAIT_MIN", "1"),
            var("IDLE_ROOT", "/repo/x"),
        ],
        own,
        "/",
    );
    assert!(
        inside.wait_min == 60
            && !inside.arm
            && inside
                .warning
                .as_deref()
                .is_some_and(|w| w.contains("- ignored"))
    );
    assert!(Config::from_vars(&[var("IDLE_ROOT", "/repo/x")], own, "/")
        .warning
        .is_none());
    assert!(Config::from_vars(&[var("IDLE_lower", "x")], own, "/")
        .warning
        .is_none());
    let fixture = Config::from_vars(
        &[
            var("IDLE_FIXTURE", "1"),
            var("IDLE_WAIT_MIN", "1"),
            var("IDLE_ARM", "0"),
        ],
        own,
        "/tmp/f",
    );
    assert!(fixture.wait_min == 1 && !fixture.arm && fixture.warning.is_none());
    assert!(Config::from_vars(&[var("IDLE_FIXTURE", "1")], own, "/tmp/f").arm);
    assert_eq!(
        Config::from_vars(&[], own, "/").home,
        Path::new("/home/agent/.claude")
    );
}

#[test]
fn only_a_session_clone_is_located() {
    let (clone, _) = world("locate");
    std::fs::create_dir_all(clone.join("sub")).unwrap();
    assert_eq!(
        locate(clone.join("sub").to_str().unwrap()),
        Some((clone.clone(), "sess".to_owned()))
    );
    let main = clone.parent().unwrap().parent().unwrap();
    std::fs::create_dir_all(main.join(".git")).unwrap();
    assert_eq!(locate(main.to_str().unwrap()), None);
    assert_eq!(locate("/no/such/dir"), None);
    assert_eq!(locate("/"), None);
}

#[test]
fn a_stop_arms_once_and_never_while_disabled_or_in_main() {
    let (clone, mut c) = world("arm");
    let sf = clone.join(".git/idle-tests.json");
    c.arm = false;
    c.warning = Some("said".to_owned());
    assert!(judge(&event("Stop", &clone), &c, "/").is_empty() && !sf.exists());
    c.arm = true;
    c.warning = None;
    assert!(judge(&event("Stop", Path::new("/")), &c, "/").is_empty() && !sf.exists());
    assert!(judge(&event("Stop", &clone), &c, "/").is_empty());
    assert_eq!(
        (state_of(&sf, "session"), state_of(&sf, "armed_at")),
        ("sess".to_owned(), "1000".to_owned())
    );
    assert!(!state_of(&sf, "timer_pid").is_empty());
    let me = std::process::id();
    std::fs::write(&sf, json!({"timer_pid": me}).to_string()).unwrap();
    assert!(judge(&event("Stop", &clone), &c, "/").is_empty());
    assert_eq!(state_of(&sf, "session"), "");
    std::fs::write(&sf, json!({"timer_pid": ""}).to_string()).unwrap();
    std::fs::remove_file(clone.join(".git/idle-tests.log")).unwrap();
    std::fs::create_dir_all(clone.join(".git/idle-tests.log")).unwrap();
    assert!(judge(&event("Stop", &clone), &c, "/").is_empty());
    assert_eq!(state_of(&sf, "session"), "sess");
}

#[test]
fn a_prompt_disarms_and_says_the_last_verdict_once() {
    let (clone, c) = world("prompt");
    let a = clone.join(".git/idle-tests.json");
    let mut sleeper = std::process::Command::new("sleep")
        .arg("5")
        .spawn()
        .unwrap();
    std::fs::write(&a, json!({"timer_pid": sleeper.id()}).to_string()).unwrap();
    assert!(judge(&event("UserPromptSubmit", &clone), &c, "/").is_empty());
    assert!(!a.exists());
    assert!(!sleeper.wait().unwrap().success());
    std::fs::write(&a, json!({"timer_pid": null}).to_string()).unwrap();
    record(
        &clone,
        "20260101T000000Z-sess.json",
        &json!({"utc": "u", "wall_s": 3, "commit": "c", "target": "t", "suspends": 0, "deferrals": 1, "rc": 0}),
    );
    record(&clone, "20260101T000000Z-other.json", &json!({}));
    let got = judge(&event("UserPromptSubmit", &clone), &c, "/");
    assert!(!a.exists());
    assert!(
        matches!(&got[..], [Answer::Print(l)] if l == "idle-tests: ran u in 3s on c (t; suspends 0, deferrals 1): clean")
    );
    assert!(judge(&event("UserPromptSubmit", &clone), &c, "/").is_empty());
}

#[test]
fn a_prompt_during_a_run_aborts_it_and_records_that() {
    let (clone, c) = world("abort");
    std::fs::write(
        clone.join(".git/idle-tests.json"),
        json!({"timer_pid": 2_147_483_000}).to_string(),
    )
    .unwrap();
    std::fs::write(clone.join(".git/idle-tests.running"), "1").unwrap();
    let got = judge(&event("UserPromptSubmit", &clone), &c, "/");
    assert!(
        matches!(&got[..], [Answer::Print(l)] if l.contains("aborted on your prompt"))
            && !clone.join(".git/idle-tests.running").exists()
    );
    assert_eq!(state_of(&records(&clone)[0], "rc"), "-1");
}

#[test]
fn each_verdict_has_its_words() {
    let d = dir("verdict");
    let say = |v: serde_json::Value| {
        let p = d.join("r.json");
        std::fs::write(&p, v.to_string()).unwrap();
        verdict(&p).unwrap()
    };
    assert!(say(json!({"skipped": "same", "rc": 0})).ends_with("skipped - same (D10)"));
    assert!(
        say(json!({"rc": 2, "failures": ["a", "b"], "log": "l"})).ends_with("FAILED (rc 2): a, b")
    );
    assert!(say(json!({"rc": 2, "failures": [], "log": "l"})).ends_with("FAILED (rc 2): see l"));
    assert!(say(json!({})).starts_with("idle-tests: ran None in Nones"));
    assert!(verdict(&d.join("missing.json")).is_none());
}

#[test]
fn a_session_is_live_by_its_json_and_its_process() {
    let d = dir("live");
    let me = std::process::id();
    assert!(sid_is_live("", Path::new("/nowhere")) && !sid_is_live("x", Path::new("/nowhere")));
    std::fs::write(
        d.join(format!("{me}.json")),
        json!({"sessionId": "here"}).to_string(),
    )
    .unwrap();
    std::fs::write(
        d.join("2147483000.json"),
        json!({"session_id": "dead"}).to_string(),
    )
    .unwrap();
    std::fs::write(d.join("bad.json"), "{").unwrap();
    std::fs::write(d.join("note.txt"), "").unwrap();
    assert!(sid_is_live("here", &d) && !sid_is_live("dead", &d) && !sid_is_live("nobody", &d));
    let here = std::env::current_dir().unwrap();
    assert!(
        make_in(&me.to_string(), &here)
            && !make_in(&me.to_string(), Path::new("/nowhere"))
            && !make_in("", &here)
    );
}

#[test]
fn the_wait_restarts_on_a_suspend_and_ends_when_the_arming_goes() {
    let (clone, mut c) = world("wait");
    armed(&clone);
    // each reading takes the next line, the last one standing: the baseline, a reading in `alive`, then the jump
    let seq = clone.join(".git/clock-seq");
    std::fs::write(&seq, "1000\n1000\n1500\n").unwrap();
    let clock = clone.join(".git/clock");
    script(
        &clock,
        &format!(
            "f={0}; n=$(head -1 $f); [ $(wc -l < $f) -gt 1 ] && sed -i 1d $f; echo $n",
            seq.display()
        ),
    );
    c.clock = format!("sh {}", clock.display());
    c.suspend_s = 100;
    let mut t = timer_of(&c, &clone);
    assert!(t.wait_ms(2) && t.suspends == 1);
    assert!(t.wait_awake(0));
    std::fs::remove_file(clone.join(".git/idle-tests.json")).unwrap();
    let mut gone = timer_of(&c, &clone);
    assert!(!gone.wait_awake(1) && !gone.alive());
}

#[test]
fn a_held_lock_or_a_running_make_defers_the_run() {
    let (clone, mut c) = world("lock");
    armed(&clone);
    std::fs::create_dir_all(&c.home).unwrap();
    let path = c.home.join("idle-tests.lock");
    let (mine, theirs) = (
        std::fs::File::create(&path).unwrap(),
        std::fs::File::create(&path).unwrap(),
    );
    assert!(flock(&theirs, "-n") && !flock(&mine, "-n"));
    let mut waits = timer_of(&c, &clone);
    let gone = std::thread::scope(|s| {
        s.spawn(|| {
            std::thread::sleep(std::time::Duration::from_millis(15));
            std::fs::remove_file(clone.join(".git/idle-tests.json")).unwrap();
        });
        waits.hold(&mine, 1)
    });
    assert!(gone.is_none() && waits.deferrals >= 1);
    assert!(flock(&theirs, "-u") && flock(&mine, "-n") && flock(&mine, "-u"));
    armed(&clone);
    script(&clone.join("busy"), "rm \"$1/busy-flag\"");
    std::fs::write(clone.join("busy-flag"), "").unwrap();
    c.busy = format!("sh {}", clone.join("busy").display());
    let mut busy = timer_of(&c, &clone);
    assert!(busy.hold(&mine, 0).is_some() && busy.deferrals == 1);
    c.busy = String::new();
    assert!(!timer_of(&c, &clone).busy());
}

#[test]
fn the_timer_runs_records_and_consumes_the_arming() {
    let (clone, mut c) = world("run");
    timer(&c, &clone, "sess", "");
    assert!(records(&clone).is_empty(), "nothing armed, nothing run");
    armed(&clone);
    script(&clone.join("run.sh"), "echo FAIL one; echo 'FAIL one'; echo 'tripwire seed 7: broke'; echo 'tripwire seed 8: ok'; exit 3");
    c.run = format!("sh {}", clone.join("run.sh").display());
    timer(&c, &clone, "sess", "");
    let rec = &records(&clone)[0];
    assert_eq!(state_of(rec, "rc"), "3");
    assert!(
        state_of(rec, "failures").contains("seed7: broke")
            && !clone.join(".git/idle-tests.json").exists()
    );
    assert_eq!(launch("/no/such/program", &clone, &clone.join("l")), 127);
    assert_eq!(launch("true", &clone, Path::new("/no/such/dir/log")), 127);
    assert!(failures(Path::new("/no/such/log")).is_empty());
}

#[test]
fn an_unchanged_clone_after_a_green_run_is_skipped() {
    let (clone, c) = world("skip");
    let d = clone.to_string_lossy().into_owned();
    assert!(ask(Path::new("/"), "git", &["init", "-q", &d], "").ok());
    assert!(ask(
        Path::new("/"),
        "git",
        &[
            "-C",
            &d,
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x"
        ],
        ""
    )
    .ok());
    let head = super::short_head(&clone);
    record(
        &clone,
        "20260101T000000Z-sess.json",
        &json!({"rc": 0, "commit": head}),
    );
    armed(&clone);
    timer(&c, &clone, "sess", "");
    let all = records(&clone);
    assert!(
        all.len() == 2
            && all
                .iter()
                .any(|r| state_of(r, "skipped").contains("unchanged since the green run"))
    );
    assert!(!clone.join(".git/idle-tests.json").exists());
    let t = timer_of(&c, &clone);
    assert!(!t.skipped("u", "other-commit", "t"));
}

#[test]
fn the_timer_stops_when_its_home_cannot_hold_the_lock_or_the_wait_ends_early() {
    let (clone, mut c) = world("home");
    armed(&clone);
    c.home = Path::new("/proc/nope").to_path_buf();
    timer(&c, &clone, "sess", "");
    assert!(records(&clone).is_empty());
    let (clone2, mut d) = world("early");
    armed(&clone2);
    d.wait_s = Some(1);
    d.give_up_s = -1;
    timer(&d, &clone2, "sess", "");
    assert!(records(&clone2).is_empty());
    let (clone3, mut e) = world("default-wait");
    e.wait_s = None;
    e.defer_s = None;
    e.give_up_s = -1;
    armed(&clone3);
    timer(&e, &clone3, "sess", "");
    assert!(records(&clone3).is_empty());
}

#[test]
fn the_timer_runs_make_by_default_and_stops_if_the_arming_went_under_the_lock() {
    let (clone, mut c) = world("default-run");
    armed(&clone);
    c.run = String::new();
    timer(&c, &clone, "sess", "");
    assert_eq!(state_of(&records(&clone)[0], "target"), "make idle-tests");
    assert!(
        Config {
            clock: String::new(),
            ..c
        }
        .now()
            > 1_000_000
    );
    let (gone, mut d) = world("gone-under-lock");
    armed(&gone);
    script(&gone.join("busy"), "rm \"$1/.git/idle-tests.json\"; exit 1");
    d.busy = format!("sh {}", gone.join("busy").display());
    timer(&d, &gone, "sess", "");
    assert!(records(&gone).is_empty());
}

#[test]
fn the_command_line_and_the_entry() {
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let said = cli(&args(&["stagger", "sess-a"]));
    assert!(said.code == 0 && (60..=120).contains(&said.stdout.trim().parse::<u64>().unwrap()));
    assert_eq!(cli(&args(&[])).code, 1);
    assert_eq!(cli(&args(&["timer", "/no/such/clone", "s", ""])).code, 0);
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
    let d = dir("nostate");
    assert_eq!(state_of(&d.join("x"), "k"), "");
}
