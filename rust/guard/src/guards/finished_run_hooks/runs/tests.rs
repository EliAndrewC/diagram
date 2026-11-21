//! What runs and who waits, on the stand-in `/proc` of the guard's tests.

use std::os::unix::fs::PermissionsExt;
use std::path::Path;

use super::super::tests::world;
use super::{files_named, owner, realpath, written, Root, Status};

#[test]
fn a_path_is_resolved_whether_or_not_it_exists() {
    assert_eq!(
        realpath(Path::new("./no-such-either")),
        Path::new("no-such-either")
    );
    let w = world("real");
    assert_eq!(realpath(&w.clone.join("a/../b/./c")), w.clone.join("b/c"));
    assert_eq!(
        realpath(Path::new("relative-no-such")),
        Path::new("relative-no-such")
    );
    assert_eq!(owner(&w.clone.join("deep/er")), Some(w.clone.clone()));
    assert_eq!(owner(Path::new("/")), None);
}

#[test]
fn a_command_line_names_only_files_through_its_variables() {
    let w = world("named");
    let dir = w.root.join("v");
    std::fs::create_dir_all(&dir).unwrap();
    let (log, tool) = (dir.join("a.log"), dir.join("tool.sh"));
    std::fs::write(&tool, "").unwrap();
    std::fs::set_permissions(&tool, std::fs::Permissions::from_mode(0o755)).unwrap();
    let d = dir.display();
    let found = files_named(&format!("S={d}; L=$S/a.log; until grep -q X ${{L}} $UNKNOWN/x; do {d}/tool.sh {d} /no/such/dir/f; sleep 3; done"), Path::new("/"));
    assert!(found.contains(&log) && found.len() == 1);
    let quoted = files_named(&format!("S=\"{d}\" ; tail $S/q.log"), Path::new("/"));
    assert!(quoted.contains(&dir.join("q.log")));
    let relative = files_named("cat v/r.log", &w.root);
    assert!(relative.contains(&realpath(&w.root.join("v/r.log"))));
}

/// What a text WRITES (451 T61): each redirection's and each `tee`'s target, through the text's own variables and the harness's
/// quoting, a relative one against the base; a descriptor's copy, a process substitution, a target left holding a `$` and a file only
/// read name nothing.
#[test]
fn a_text_writes_only_what_it_redirects_or_tees_into() {
    let base = Path::new("/w");
    let got = written(
        "S=/w/t; echo a >> $S/a.txt; b 2>&1 >/w/b.log; c &>'/w/c.log'; d | tee -a --output-error=warn /w/d.log; e >| e.log; \
         f 2>>\"$S/f.log\"; eval 'g >> '\"'\"'/w/g.log'\"'\"''; h > $UNSET/h; i >&2; grep x /w/r.log < /w/in.log; j > >(k)",
        base,
    );
    let want: Vec<&str> = vec![
        "/w/t/a.txt",
        "/w/b.log",
        "/w/c.log",
        "/w/d.log",
        "/w/e.log",
        "/w/t/f.log",
        "/w/g.log",
    ];
    let want: std::collections::BTreeSet<_> =
        want.into_iter().map(|w| realpath(Path::new(w))).collect();
    assert_eq!(got, want);
}

#[test]
fn a_phase_child_speaks_through_its_root_and_each_status_has_its_line() {
    let w = world("roots");
    let log = w.root.join("run.log");
    std::fs::write(&log, "").unwrap();
    w.add(100, "make", 1, &w.clone, &["make", "done"], Some(&log));
    w.add(101, "make", 100, &w.clone.join("sub"), &["make", "t"], None);
    w.add(102, "bash", 1, &w.clone, &["bash"], None);
    let elsewhere = w.root.join("elsewhere");
    std::fs::create_dir_all(elsewhere.join(".git")).unwrap();
    w.add(103, "make", 1, &elsewhere, &["make", "theirs"], None);
    assert_eq!(w.procs().live_runs(&w.clone).len(), 2);
    let roots = w.procs().judge_runs(&w.clone);
    assert_eq!(roots.len(), 1);
    assert_eq!(
        roots[0].line(),
        format!("100 done unwatched {}", log.display())
    );
    let watched = Root {
        pid: 1,
        target: "t".to_owned(),
        status: Status::Watched(2, "/f".to_owned()),
    };
    assert_eq!(watched.line(), "1 t watched 2 /f");
    assert_eq!(
        Root {
            pid: 1,
            target: "t".to_owned(),
            status: Status::Tracked("o".to_owned())
        }
        .line(),
        "1 t tracked o"
    );
}

#[test]
fn a_run_with_no_output_file_and_a_chain_named_on_an_ancestor() {
    let w = world("chain");
    // a loop on some other file, one whose cwd cannot be read: it watches nothing of this run's
    w.add(
        201,
        "bash",
        1,
        Path::new("/"),
        &[
            "bash",
            "-c",
            "until grep -q X /tmp/other.log; do sleep 1; done",
        ],
        None,
    );
    std::fs::remove_file(w.proc.join("201/cwd")).unwrap();
    w.add(100, "make", 1, &w.clone, &["make", "a"], None);
    assert_eq!(
        w.procs().judge_runs(&w.clone)[0].status,
        Status::Unwatched("(no file)".to_owned())
    );
    let chain = world("chain2");
    let last = chain.root.join("b.log");
    let parent = format!("make a; make b > {}", last.display());
    chain.add(90, "bash", 1, &chain.root, &["bash", "-c", &parent], None);
    chain.add(100, "make", 90, &chain.clone, &["make", "a"], None);
    let waiter = format!("until grep -q DONE {} ; do sleep 3; done", last.display());
    chain.add(
        200,
        "bash",
        1,
        Path::new("/"),
        &["bash", "-c", &waiter],
        None,
    );
    assert_eq!(
        chain.procs().judge_runs(&chain.clone)[0].status,
        Status::Watched(200, last.to_string_lossy().into_owned())
    );
}

#[test]
fn the_hooks_own_tree_is_never_a_waiter_and_a_claude_ancestor_ends_the_chain() {
    let w = world("mine");
    let log = w.root.join("m.log");
    std::fs::write(&log, "").unwrap();
    let cmd = format!("until grep -q X {}; do sleep 1; done", log.display());
    w.add(
        99_999,
        "l7r-guard",
        500,
        Path::new("/"),
        &["l7r-guard"],
        None,
    );
    w.add(500, "bash", 1, Path::new("/"), &["bash", "-c", &cmd], None);
    w.add(100, "make", 1, &w.clone, &["make", "x"], Some(&log));
    assert!(matches!(
        w.procs().judge_runs(&w.clone)[0].status,
        Status::Unwatched(_)
    ));
    assert!(w
        .procs()
        .stale_waiters(&w.root.join("tree"), None)
        .is_empty());
}

#[test]
fn only_a_live_file_of_this_clone_makes_a_waiter_stale() {
    let w = world("waiters");
    let tree = w.root.join("tree");
    let snaps = w.root.join("shell-snapshots");
    std::fs::create_dir_all(&snaps).unwrap();
    let (snap, script, dead) = (
        snaps.join("s.sh"),
        w.root.join("run.sh"),
        w.root.join("dead.log"),
    );
    for f in [&snap, &script, &dead] {
        std::fs::write(f, "").unwrap();
    }
    std::fs::set_permissions(&script, std::fs::Permissions::from_mode(0o755)).unwrap();
    let cmd = format!(
        "source {}; until grep -q X {} {} /gone/x.log {}; do sleep 3; {}; done",
        snap.display(),
        dead.display(),
        dead.display(),
        dead.display(),
        script.display()
    );
    w.add(300, "bash", 1, &w.clone, &["bash", "-c", &cmd], None);
    w.add(
        301,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", "echo hello; sleep 3"],
        None,
    );
    let elsewhere = w.root.join("other");
    std::fs::create_dir_all(elsewhere.join(".git")).unwrap();
    w.add(302, "bash", 1, &elsewhere, &["bash", "-c", &cmd], None);
    let mine = w.procs().stale_waiters(&tree, Some(&w.clone));
    assert_eq!(mine, [format!("300 {}", dead.display())]);
    assert_eq!(w.procs().stale_waiters(&tree, None).len(), 2);
    std::fs::write(tree.join("scripts/hooks/lib/writer-alive.sh"), "exit 0\n").unwrap();
    assert!(w.procs().stale_waiters(&tree, None).is_empty());
}

/// A QUIET FILE OVER A LIVE RUN (451 T61): T55's run as recorded on 2026-11-21 - a loop of makes appending a line to its summary
/// between them - is the run of that summary, since its text WRITES it; the waiters, the waiter's `grep`, the readers - the Monitor
/// tool's `tail -f | grep` and a file-test wait, each inside the harness's wrapper that names the file - and the asker's own ancestry
/// name it too and are none of its run, and a stand-in table whose parents loop ends its walk.
#[test]
fn a_quiet_file_is_run_by_the_live_process_that_writes_it() {
    let w = world("runner");
    let dir = w.root.join("t55");
    std::fs::create_dir_all(&dir).unwrap();
    let sum = dir.join("seq.times");
    std::fs::write(&sum, "static rc=2 70s\n").unwrap();
    let (s, d) = (sum.display().to_string(), dir.display().to_string());
    let p = w.procs();
    assert_eq!(p.runner_of(&sum), None);
    let wait = format!(
        "source /s/snapshot.sh && eval 'until grep -q \"^total\" {s}; do sleep 2; done; cat {s}'"
    );
    w.add(
        10,
        "bash",
        1,
        &w.root,
        &["/bin/bash", "-c", "-l", &wait],
        None,
    );
    w.add(11, "grep", 10, &w.root, &["grep", "-q", "^total", &s], None);
    w.add(
        12,
        "bash",
        1,
        &w.root,
        &[
            "bash",
            "-c",
            &format!("while ! grep -q x {s}; do sleep 3; done"),
        ],
        None,
    );
    w.add(13, "tail", 1, &w.root, &["tail", "-f", &s], None);
    w.add(
        20,
        "bash",
        1,
        &w.root,
        &["bash", "-c", &format!("ask {s}")],
        None,
    );
    w.add(
        99_999,
        "l7r-guard",
        20,
        &w.root,
        &["l7r-guard", "--finished-run", "alive", &s],
        None,
    );
    w.add(30, "bash", 31, &w.root, &["bash"], None);
    w.add(31, "bash", 30, &w.root, &["bash"], None);
    let harness = |cmd: &str| {
        format!("source /s/snapshot.sh 2>/dev/null || true && eval '{cmd}' < /dev/null && pwd -P >| /tmp/claude-1-cwd")
    };
    let monitor = harness(&format!("tail -f {s} | grep --line-buffered total"));
    w.add(32, "bash", 1, &w.root, &["/bin/bash", "-c", &monitor], None);
    w.add(33, "tail", 32, &w.root, &["tail", "-f", &s], None);
    w.add(
        34,
        "grep",
        32,
        &w.root,
        &["grep", "--line-buffered", "total"],
        None,
    );
    let test = harness(&format!(
        "until [ -s {s} ]; do sleep 3; done; cat {s} > {d}/copy.txt 2>&1"
    ));
    w.add(35, "bash", 1, &w.root, &["/bin/bash", "-c", &test], None);
    assert_eq!(p.runner_of(&sum), None, "a reader is no run of the file");
    let run = format!(
        "source /s/snapshot.sh && eval 'cd {c} && t0=$(date +%s); for c in static hooks-test quick; do s=$(date +%s); make \
         --no-print-directory $c HOOKS_ALL=1 > {d}/seq-$c.log 2>&1; echo \"$c rc=$? $(( $(date +%s) - s ))s\" >> {s}; done; echo \
         \"total $(( $(date +%s) - t0 ))s\" >> {s}; cat {s}'",
        c = w.clone.display()
    );
    w.add(
        40,
        "bash",
        1,
        &w.clone,
        &["/bin/bash", "-c", "-l", &run],
        None,
    );
    w.add(41, "make", 40, &w.clone, &["make", "hooks-test"], None);
    assert_eq!(p.runner_of(&sum).as_deref(), Some("40 writes it"));
}

/// A run started from a script writes its file in the script's text (451 T61: T38's `lintcover.sh` and T45's `series.sh`, each run
/// by path, named the summary they appended to only inside): a relative script is read against the run's cwd; a waiter's script, a
/// script that only reads the file, a file past `SCRIPT_BYTES`, a binary, and a run's log that a reader follows (its echoed recipe
/// writes the file, but a `tail` runs no script) are read as no run of it.
#[test]
fn a_quiet_file_is_run_by_the_script_that_writes_it() {
    let w = world("script");
    let dir = w.root.join("t38");
    std::fs::create_dir_all(&dir).unwrap();
    let tsv = dir.join("lintcover.tsv");
    std::fs::write(&tsv, "lint\trust/guard\t0\n").unwrap();
    let t = tsv.display();
    std::fs::write(
        dir.join("wait.sh"),
        format!("until grep -q DONE {t}; do sleep 5; done\n"),
    )
    .unwrap();
    std::fs::write(
        dir.join("big.txt"),
        format!("{t}\n{}", "x".repeat(256 * 1024)),
    )
    .unwrap();
    std::fs::write(dir.join("bin"), [0xff, 0xfe, 0x00]).unwrap();
    std::fs::write(
        dir.join("read.sh"),
        format!("until [ -s {t} ]; do sleep 5; done; cat {t}\n"),
    )
    .unwrap();
    std::fs::write(
        dir.join("make.log"),
        format!("l7r-gate.sh rust lint > lint.log; echo lint >> {t}\n"),
    )
    .unwrap();
    w.add(
        50,
        "bash",
        1,
        &dir,
        &["bash", "wait.sh", "big.txt", "bin", ""],
        None,
    );
    w.add(52, "bash", 1, &dir, &["bash", "read.sh"], None);
    w.add(53, "tail", 1, &dir, &["tail", "-f", "make.log"], None);
    assert_eq!(w.procs().runner_of(&tsv), None);
    let sh = dir.join("lintcover.sh");
    let text = format!(
        "#!/bin/bash\nfor k in lint cover; do\n  l7r-gate.sh rust $k > {d}/$k.log 2>&1\n  printf '%s\\t%s\\n' \"$k\" \"$?\" >> {t}\ndone\necho DONE\n",
        d = dir.display()
    );
    std::fs::write(&sh, text).unwrap();
    std::fs::set_permissions(&sh, std::fs::Permissions::from_mode(0o755)).unwrap();
    w.add(51, "bash", 1, &dir, &["/bin/bash", "./lintcover.sh"], None);
    assert_eq!(
        w.procs().runner_of(&tsv),
        Some(format!(
            "51 runs {} which writes it",
            realpath(&sh).display()
        ))
    );
}

/// A COMMAND THAT OPENS WITH ITS ASSIGNMENT (451 T71): the harness runs a command as `eval '<command>'`, so an assignment that opens
/// it follows a quote, not a blank. T151 part B's foreground call as recorded on 2026-11-18 (`B=<dir>; ... | tee -a $B/phases.log`),
/// which the harness moved to the background at 180 s, was a live run of `phases.log` while its agent's wait on that file read it
/// gone (`bcmk2v816`, exit 3, 207 s quiet): `$B` was never read, so the target held a `$` and named nothing. Its write, and a file
/// it names, are read through that assignment; a waiter and the Monitor tool's reader opening the same way still write nothing.
#[test]
fn a_command_that_opens_with_its_assignment_writes_through_it() {
    let w = world("opens");
    let dir = w.root.join("t151/b");
    std::fs::create_dir_all(&dir).unwrap();
    let log = dir.join("phases.log");
    std::fs::write(&log, "hooks rc=0\n").unwrap();
    let d = dir.display().to_string();
    let harness = |cmd: &str| {
        format!(
            "source /s/snapshot.sh 2>/dev/null || true && shopt -u extglob 2>/dev/null || true && eval '{cmd}' < /dev/null && pwd \
             -P >| /tmp/claude-1-cwd"
        )
    };
    let recorded = format!(
        "B={d}; cd {c} && make quick > $B/final-quick.log 2>&1; echo \"quick rc=$? $(date -Is)\" | tee -a $B/phases.log; tail -5 \
         $B/final-quick.log; scripts/gates/l7r-gate.sh check research-pointers --selftest > $B/final-pointers.log 2>&1 && \
         scripts/gates/l7r-gate.sh check research-pointers >> $B/final-pointers.log 2>&1; echo \"pointers rc=$? $(date -Is)\" | tee \
         -a $B/phases.log; tail -3 $B/final-pointers.log",
        c = w.clone.display()
    );
    assert!(written(&harness(&recorded), &w.clone).contains(&realpath(&log)));
    assert!(files_named(
        &harness(&format!("S={d}; tail -1 $S/phases.log")),
        Path::new("/")
    )
    .contains(&realpath(&log)));
    let wait = harness(&format!(
        "B={d}; until grep -q \"pointers rc=\" $B/phases.log; do sleep 5; done; tail -3 $B/phases.log > $B/seen.txt"
    ));
    w.add(60, "bash", 1, &w.root, &["/bin/bash", "-c", &wait], None);
    let monitor = harness(&format!(
        "S={d}; tail -f $S/phases.log | grep --line-buffered rc="
    ));
    w.add(61, "bash", 1, &w.root, &["/bin/bash", "-c", &monitor], None);
    assert_eq!(w.procs().runner_of(&log), None); // a waiter and a reader are no run
    w.add(
        62,
        "bash",
        1,
        &w.clone,
        &["/bin/bash", "-c", &harness(&recorded)],
        None,
    );
    w.add(63, "make", 62, &w.clone, &["make", "quick"], None);
    assert_eq!(w.procs().runner_of(&log).as_deref(), Some("62 writes it"));
}

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A polling loop after a line of many `until` words (feature 449 T185): unlimited, `LOOP` tried every one to its line's end (17 s on
/// 100 KB, measured 2026-11-18, scratchpad t185/sizecurve.log), and at `fancy_regex`'s old limit it erred and read as no loop; it now starts at the line's first.
#[test]
fn a_loop_after_many_untils_is_seen_in_linear_time() {
    let command = format!(
        "{}\nwhile sleep 1; do grep -q x f; done",
        "until x ".repeat(30_000)
    );
    assert_eq!(
        within(move || super::LOOP.is_match(&command).ok()),
        Some(true)
    );
}
