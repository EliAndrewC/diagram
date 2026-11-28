//! A failure reproduced under load, bounded (feature 462 T321): the loops counted red, cut or green beside their burners, every
//! process of the run's group ended at the bound, at the caller's going, or by the sentinel alone, and one `Phase` line written.

use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, Instant};

use super::phases::phases;
use super::{kept_crates, world_with};
use crate::rustc::under_load::warden::{load, sentinel};
use crate::rustc::under_load::{entry, parse, Knobs, STEP};

/// A ceiling no green run comes near, for a loaded machine (461 T58: a 0.3 s bound read red at load).
const CEILING: Duration = Duration::from_secs(30);

fn knobs(root: &Path) -> Knobs {
    let proc_root = root.join("proc");
    std::fs::create_dir_all(&proc_root).unwrap();
    std::fs::write(proc_root.join("loadavg"), "1.50 1.00 0.50 1/100 7\n").unwrap();
    let out_root = root.join("out");
    std::fs::create_dir_all(&out_root).unwrap();
    Knobs {
        exe: PathBuf::from("/no/such/warden"),
        argv: Vec::new(),
        poll: Duration::from_millis(20),
        grace: Duration::from_millis(500),
        burner: "sleep 600".to_owned(),
        shell: "sh".to_owned(),
        proc_root,
        out_root,
        cores: 4,
    }
}

fn words(cmd: &str, copies: &str, loops: &str, minutes: &str, burners: &str) -> Vec<String> {
    [
        "--cmd",
        cmd,
        "--copies",
        copies,
        "--loops",
        loops,
        "--max-minutes",
        minutes,
        "--burners",
        burners,
    ]
    .iter()
    .map(|w| (*w).to_owned())
    .collect()
}

/// A caller's pipe that never ends, and its writer, whose drop is the caller's going.
fn pipe() -> (Box<dyn Read + Send>, std::io::PipeWriter) {
    let (r, w) = std::io::pipe().unwrap();
    (Box::new(r), w)
}

/// Whether any process of `group` is left.
fn alive(group: u64) -> bool {
    Command::new("sh")
        .args(["-c", "kill -0 -- \"-$0\" 2>/dev/null", &group.to_string()])
        .status()
        .unwrap()
        .success()
}

fn group_of(out: &str) -> u64 {
    let at = out.find(", group ").unwrap() + 8;
    out[at..]
        .split_whitespace()
        .next()
        .unwrap()
        .parse()
        .unwrap()
}

#[test]
fn the_words_are_read_and_every_wrong_one_refused() {
    let ask = parse(&words("make x", "3", "2", "1.5", "1"), 4).unwrap();
    assert_eq!(
        (
            ask.cmd.as_str(),
            ask.copies,
            ask.loops,
            ask.burners,
            ask.max
        ),
        ("make x", 3, 2, 1, Duration::from_secs(90))
    );
    assert_eq!(
        parse(&words("x", "1", "1", "1", "0")[..8], 4)
            .unwrap()
            .burners,
        0
    );
    for (bad, said) in [
        (words(" ", "1", "1", "1", "0"), "CMD is required"),
        (
            words("x", "0", "1", "1", "0"),
            "--copies takes a whole number, at least 1",
        ),
        (
            words("x", "1.5", "1", "1", "0"),
            "--copies takes a whole number",
        ),
        (words("x", "1", "two", "1", "0"), "--loops takes a number"),
        (
            words("x", "1", "1", "0", "0"),
            "MAX_MINUTES is required, above 0 and at most 60",
        ),
        (words("x", "1", "1", "61", "0"), "at most 60"),
        (
            words("x", "10", "1", "1", "3"),
            "COPIES + BURNERS is 13, past 12 (3 a core on 4)",
        ),
    ] {
        let why = parse(&bad, 4).unwrap_err();
        assert!(why.contains(said), "{why}");
    }
    let mut no_value = words("x", "1", "1", "1", "0");
    no_value.truncate(9);
    assert!(parse(&no_value, 4)
        .unwrap_err()
        .contains("--burners takes a number"));
}

#[test]
fn a_usage_error_starts_nothing_and_says_the_form() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let reply = entry(
        &world,
        &words("x", "0", "1", "1", "0"),
        &knobs(&root),
        true,
        caller,
    );
    assert_eq!(reply.code, 2);
    assert!(
        reply.stderr.contains("usage: make under-load CMD="),
        "{}",
        reply.stderr
    );
    assert!(phases(&root).is_empty());
    let cli = crate::rustc::cli(&[STEP.to_owned()]);
    assert_eq!(cli.code, 2);
    assert!(cli.stderr.contains("CMD is required"), "{}", cli.stderr);
}

#[test]
fn every_loop_runs_beside_its_burners_the_red_counted_and_named_and_one_phase_line_written() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let cmd = "echo copy $L7R_UNDER_LOAD_COPY; [ \"$L7R_UNDER_LOAD_LOOP\" != 2 ]";
    let began = Instant::now();
    let reply = entry(
        &world,
        &words(cmd, "2", "3", "1", "1"),
        &knobs(&root),
        true,
        caller,
    );
    assert!(began.elapsed() < CEILING);
    assert_eq!(reply.code, 1, "{}", reply.stdout);
    let out = &reply.stdout;
    assert!(
        out.contains("2 copies x 3 loops beside 1 burners, bound 1.0 min"),
        "{out}"
    );
    assert!(out.contains("ran 6 of 6: 2 red, 0 cut, 4 green"), "{out}");
    assert!(
        out.contains("load (1-min, 4 cores): 1.50 at the start 20"),
        "{out}"
    );
    assert!(out.contains("ended: every loop ran"), "{out}");
    assert!(!alive(group_of(out)));
    let logs: Vec<PathBuf> = std::fs::read_dir(root.join("out"))
        .unwrap()
        .flat_map(|d| std::fs::read_dir(d.unwrap().path()).unwrap())
        .map(|e| e.unwrap().path())
        .collect();
    // only the red runs' logs are kept
    assert_eq!(logs.len(), 2, "{logs:?}");
    for log in &logs {
        assert!(
            log.ends_with("c1-l2.log") || log.ends_with("c2-l2.log"),
            "{log:?}"
        );
        assert!(out.contains(&log.display().to_string()), "{out}");
        assert!(std::fs::read_to_string(log).unwrap().starts_with("copy "));
    }
    let lines = phases(&root);
    assert_eq!(lines.len(), 1);
    let line = &lines[0];
    assert_eq!(
        (line["src"].as_str(), line["step"].as_str()),
        (Some("rust"), Some(STEP))
    );
    assert_eq!(
        (line["code"].as_i64(), line["make"].as_str()),
        (Some(1), Some("static"))
    );
    assert_eq!(
        (
            line["runs"].as_u64(),
            line["red"].as_u64(),
            line["cut"].as_u64()
        ),
        (Some(6), Some(2), Some(0))
    );
    assert_eq!(
        (line["load_start"].as_f64(), line["ended"].as_str()),
        (Some(1.5), Some("every loop ran"))
    );
    assert_eq!(
        (
            line["copies"].as_u64(),
            line["loops"].as_u64(),
            line["burners"].as_u64()
        ),
        (Some(2), Some(3), Some(1))
    );
    assert_eq!(line["cmd"].as_str(), Some(cmd));
}

#[test]
fn the_bound_ends_every_copy_and_burner_and_counts_them_cut_not_red() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let began = Instant::now();
    // 0.05 minutes: a bound of 3 s, so each copy has set its trap before the TERM even under a coverage run's load (at 0.3 s it
    // had not, once, 2026-11-28: the log empty)
    let cmd = "trap 'echo termed; exit 7' TERM; sleep 30 & wait";
    let reply = entry(
        &world,
        &words(cmd, "2", "5", "0.05", "2"),
        &knobs(&root),
        true,
        caller,
    );
    assert!(began.elapsed() < CEILING);
    assert_eq!(reply.code, 0, "{}", reply.stdout);
    assert!(
        reply.stdout.contains("ran 2 of 10: 0 red, 2 cut, 0 green"),
        "{}",
        reply.stdout
    );
    assert!(
        reply.stdout.contains("ended: the bound"),
        "{}",
        reply.stdout
    );
    assert!(!alive(group_of(&reply.stdout)));
    // the warden's TERM ended them, not the sentinel's KILL: a cut run's log is kept
    let dir = std::fs::read_dir(root.join("out"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    assert_eq!(
        std::fs::read_to_string(dir.join("c1-l1.log")).unwrap(),
        "termed\n"
    );
    assert_eq!(phases(&root)[0]["cut"].as_u64(), Some(2));
}

#[test]
fn a_copy_deaf_to_term_is_killed_after_the_grace() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let began = Instant::now();
    let reply = entry(
        &world,
        &words("trap '' TERM; sleep 30", "1", "1", "0.05", "0"),
        &knobs(&root),
        true,
        caller,
    );
    assert!(began.elapsed() >= Duration::from_millis(3500));
    assert!(began.elapsed() < CEILING);
    assert!(
        reply.stdout.contains("ran 1 of 1: 0 red, 1 cut, 0 green"),
        "{}",
        reply.stdout
    );
    assert!(!alive(group_of(&reply.stdout)));
}

#[test]
fn the_caller_s_going_ends_the_run_at_once_and_its_line_is_still_written() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, w) = pipe();
    let began = Instant::now();
    let goes = std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(300));
        drop(w);
    });
    let reply = entry(
        &world,
        &words("sleep 30", "2", "2", "1", "1"),
        &knobs(&root),
        true,
        caller,
    );
    goes.join().unwrap();
    assert!(began.elapsed() < CEILING);
    assert!(
        reply.stdout.contains("ended: the caller went away"),
        "{}",
        reply.stdout
    );
    assert!(reply.stdout.contains("2 cut"), "{}", reply.stdout);
    assert!(!alive(group_of(&reply.stdout)));
    assert_eq!(
        phases(&root)[0]["ended"].as_str(),
        Some("the caller went away")
    );
}

#[test]
fn the_sentinel_alone_kills_its_group_at_its_bound() {
    let mut sentinel = sentinel("sh", 0.3).unwrap();
    let group = sentinel.id();
    let began = Instant::now();
    let mut orphan = {
        use std::os::unix::process::CommandExt as _;
        Command::new("sleep")
            .arg("30")
            .process_group(i32::try_from(group).unwrap())
            .spawn()
            .unwrap()
    };
    let status = orphan.wait().unwrap();
    assert_eq!(status.code(), None);
    assert!(began.elapsed() < CEILING);
    let _ = sentinel.wait();
    assert!(!alive(u64::from(group)));
}

#[test]
fn a_run_killed_by_a_signal_is_red_and_a_log_that_cannot_be_made_is_nowhere() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let mut k = knobs(&root);
    // the logs' directory cannot be made under a file
    std::fs::write(root.join("a-file"), "").unwrap();
    k.out_root = root.join("a-file");
    let reply = entry(
        &world,
        &words("kill -s KILL $$", "1", "1", "1", "0"),
        &k,
        true,
        caller,
    );
    assert_eq!(reply.code, 1);
    assert!(
        reply.stdout.contains("red: copy 1 loop 1 (a signal)"),
        "{}",
        reply.stdout
    );
    k.proc_root = root.join("none");
    assert!(load(&k.proc_root).abs() < f64::EPSILON);
}

#[test]
fn no_shell_is_no_run() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let (caller, _w) = pipe();
    let mut k = knobs(&root);
    k.shell = "/no/such/sh".to_owned();
    let reply = entry(&world, &words("true", "1", "1", "1", "0"), &k, true, caller);
    assert_eq!(reply.code, 1);
    assert!(
        reply
            .stderr
            .starts_with("under-load: no sentinel (/no/such/sh): "),
        "{}",
        reply.stderr
    );
}

#[test]
fn the_caller_starts_its_warden_in_a_group_of_its_own_and_hands_back_its_report() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "");
    let mut k = knobs(&root);
    let fake = root.join("warden");
    crate::write_executable(
        &fake,
        "#!/bin/sh\n[ \"$(ps -o pgid= -p $$ | tr -d ' ')\" = \"$$\" ] && echo own-group\necho \"warden=$L7R_UNDER_LOAD_WARDEN args=$*\"\nexit 3\n",
    );
    k.exe = fake;
    k.argv = vec!["a".into(), "b".into()];
    let (caller, _w) = pipe();
    let reply = entry(
        &world,
        &words("true", "1", "1", "1", "0"),
        &k,
        false,
        caller,
    );
    assert_eq!(reply.code, 3);
    assert_eq!(reply.stdout, "own-group\nwarden=1 args=a b\n");
    k.exe = PathBuf::from("/no/such/warden");
    let (caller, _w) = pipe();
    let gone = entry(
        &world,
        &words("true", "1", "1", "1", "0"),
        &k,
        false,
        caller,
    );
    assert_eq!(gone.code, 1);
    assert!(
        gone.stderr.starts_with("under-load: /no/such/warden: "),
        "{}",
        gone.stderr
    );
}
