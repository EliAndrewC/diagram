//! The sampler on fixture cgroup and `/proc` files, its loop on a clock of the test's, its start and stop on a real process that
//! names itself as the sampler does, and the report's arithmetic on fixture samples and hand logs (feature 451 T274).

use std::path::{Path, PathBuf};

use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::tempdir::TempDir;
use serde_json::json;

use super::{began, cli, sample, verb, work, Env, DIR, FILE, KEPT, PID};

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

/// A clone's git directory with fixture cgroup and `/proc` files: 2 GiB anonymous of 10, two `rustc`, two pool trees held.
fn world(tag: &str) -> (TempDir, Env) {
    let dir = TempDir::new(&format!("sampler-{tag}"));
    let (common, cgroup, proc) = (dir.join("git"), dir.join("cgroup"), dir.join("proc"));
    put(
        &cgroup.join("memory.stat"),
        "anon_thp 0\nanon 2147483648\nfile 5\n",
    );
    put(&cgroup.join("memory.current"), "8589934592\n");
    put(&cgroup.join("memory.peak"), "9663676416\n");
    put(&cgroup.join("memory.max"), "10737418240\n");
    put(&cgroup.join("memory.pressure"), "some avg10=0.00 avg60=0.00 avg300=0.00 total=4000000\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=1000000\n");
    put(
        &cgroup.join("memory.events"),
        "low 0\noom 0\noom_kill 3\noom_group_kill 0\n",
    );
    put(&proc.join("loadavg"), "15.74 14.47 12.12 8/1625 65265\n");
    put(&proc.join("pressure/cpu"), "some avg10=8.95 avg60=9.13 avg300=8.84 total=7000000\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n");
    for (pid, comm) in [
        ("11", "rustc"),
        ("12", "rustc"),
        ("13", "cargo"),
        ("self", "rustc"),
    ] {
        put(&proc.join(pid).join("comm"), &format!("{comm}\n"));
    }
    std::fs::create_dir_all(&common).unwrap();
    let tree = |n: &str, tasks: &[&str]| Tree {
        tree: dir.join(n),
        feature: "451".to_owned(),
        tasks: words(tasks),
        since: "2026-11-26T12:00:00Z".to_owned(),
    };
    builder_pool::write(
        &common,
        &[
            tree("b1", &["T274"]),
            tree("b2", &[]),
            tree("b3", &["T1", "T2"]),
        ],
    )
    .unwrap();
    let env = Env {
        common,
        cgroup,
        proc,
        every_s: 10,
        max_s: 3600,
        max_bytes: 1 << 20,
        cores: 22,
        margin_gib: 7.0,
        worker: Vec::new(),
        wait_tenths: 30,
    };
    (dir, env)
}

fn lines(path: &Path) -> Vec<String> {
    super::read(path).lines().map(str::to_owned).collect()
}

#[test]
fn a_sample_reads_the_cgroup_and_proc_and_leaves_out_what_its_file_does_not_give() {
    let (_dir, env) = world("sample");
    assert_eq!(
        sample(&env, 1_795_694_400),
        json!({
            "utc": "2026-11-26T12:00:00Z", "anon": 2_147_483_648_u64, "cur": 8_589_934_592_u64, "peak": 9_663_676_416_u64,
            "max": 10_737_418_240_u64, "mem_some_us": 4_000_000, "mem_full_us": 1_000_000, "cpu_some_us": 7_000_000,
            "load1": 15.74, "cores": 22, "oom_kill": 3, "rustc": 2, "held": ["451 T274", "451 T1,T2"]
        })
    );
    // no limit, no CPU pressure file, no pool, a pressure file with no such line: left out, never a zero
    put(&env.cgroup.join("memory.max"), "max\n");
    put(&env.cgroup.join("memory.pressure"), "some avg10=0.00\n");
    std::fs::remove_file(env.proc.join("pressure/cpu")).unwrap();
    std::fs::remove_file(env.common.join(builder_pool::FILE)).unwrap();
    let bare = sample(&env, 0);
    let keys: Vec<&String> = bare.as_object().unwrap().keys().collect();
    assert_eq!(
        keys,
        ["utc", "anon", "cur", "peak", "load1", "cores", "oom_kill", "rustc", "held"]
    );
    assert_eq!(bare["held"], json!([]));
}

#[test]
fn a_process_s_start_time_is_read_past_its_name_and_a_zombie_is_gone() {
    let (_dir, env) = world("began");
    let stat = |state: &str| {
        format!("7 (a b) c) {state} 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 4242 20 21\n")
    };
    put(&env.proc.join("7/stat"), &stat("S"));
    assert_eq!(began(&env.proc, 7), Some(4242));
    put(&env.proc.join("7/stat"), &stat("Z"));
    assert_eq!(began(&env.proc, 7), None);
    assert_eq!(began(&env.proc, 8), None);
    // this process, in the real /proc
    assert!(began(Path::new("/proc"), std::process::id()).is_some());
}

/// The loop on a clock that moves ten seconds a reading and a nap that counts.
fn looped(env: &Env, nap: &mut dyn FnMut(u64)) -> &'static str {
    let mut at = 1_795_694_390;
    let mut clock = || {
        at += 10;
        at
    };
    work(env, (77, 4242), &mut clock, nap)
}

#[test]
fn the_loop_samples_until_its_hours_are_up_and_removes_its_pid_file() {
    let (_dir, mut env) = world("hours");
    env.max_s = 30;
    let mut naps = Vec::new();
    let why = looped(&env, &mut |s| naps.push(s));
    assert_eq!(why, "its hours are up (L7R_SAMPLE_MAX_H)");
    // the clock reads :00 at the start, then :10 and :20 (a sample and a nap each), then :30, thirty seconds on: the end
    let rows = lines(&env.samples());
    assert_eq!((rows.len(), naps), (2, vec![10, 10]));
    assert!(
        rows[0].contains("\"utc\":\"2026-11-26T12:00:10Z\"")
            && rows[0].contains("\"anon\":2147483648")
    );
    assert!(!env.common.join(PID).exists());
    let log = lines(&env.common.join(DIR).join("sampler.log"));
    assert_eq!(
        log[0],
        "2026-11-26T12:00:00Z pid 77 started, a sample every 10 s"
    );
    assert_eq!(
        log[1],
        "2026-11-26T12:00:40Z pid 77 ended: its hours are up (L7R_SAMPLE_MAX_H)"
    );
}

#[test]
fn the_loop_ends_at_the_size_bound_and_when_the_pid_file_names_another() {
    let (_dir, mut env) = world("bound");
    env.max_bytes = 400;
    let why = looped(&env, &mut |_| ());
    assert_eq!(
        why,
        "the samples file is past its size bound - the next start begins a new one"
    );
    // each line is under 400 bytes and two are over: the second sample passed the bound, the third was never taken
    assert_eq!(lines(&env.samples()).len(), 2);
    assert!(!env.common.join(PID).exists());
    // another sampler writes the pid file during the first nap: this one ends and leaves the file to it
    let (_dir, env) = world("replaced");
    let pid = env.common.join(PID);
    let why = looped(&env, &mut |_| std::fs::write(&pid, "78 1\n").unwrap());
    assert_eq!(
        why,
        "the pid file no longer names it (stopped, or another sampler took its place)"
    );
    assert_eq!(
        (lines(&env.samples()).len(), super::read(&pid).as_str()),
        (1, "78 1\n")
    );
}

/// A stand-in sampler that names itself as the real one does - its pid and start time into the pid file - and waits.
fn stand_in(common: &Path) -> Vec<String> {
    let script =
        "set -- $(sed 's/.*) //' /proc/$$/stat); echo \"$$ ${20}\" > \"$0\"; exec sleep 60";
    words(&["sh", "-c", script, &common.join(PID).to_string_lossy()])
}

fn real(tag: &str) -> (TempDir, Env) {
    let (dir, mut env) = world(tag);
    env.proc = PathBuf::from("/proc");
    env.worker = stand_in(&env.common);
    std::fs::create_dir_all(env.common.join(DIR)).unwrap();
    (dir, env)
}

#[test]
fn a_second_start_says_one_is_running_and_a_stop_ends_it() {
    let (_dir, env) = real("start");
    let first = verb(&words(&["start"]), &env);
    assert_eq!(first.code, 0, "{}", first.stderr);
    assert!(first.stderr.starts_with("sampler: started (pid "));
    assert!(first.stderr.contains("for at most 1 h"), "{}", first.stderr);
    let pid = super::running(&env).unwrap();
    let again = verb(&words(&["start"]), &env);
    assert_eq!(again.code, 0);
    assert!(again
        .stderr
        .starts_with(&format!("sampler: one is running (pid {pid})")));
    assert_eq!(super::running(&env), Some(pid));
    let status = verb(&words(&["status"]), &env);
    assert!(status.stderr.starts_with(&format!(
        "sampler: running (pid {pid}), a sample every 10 s\n"
    )));
    assert!(status
        .stderr
        .contains("holds 0 lines, 0 bytes (its bound 1048576)\nsampler: last, nothing logged\n"));
    let stopped = verb(&words(&["stop"]), &env);
    assert!(stopped
        .stderr
        .starts_with(&format!("sampler: stopped (pid {pid})")));
    assert!(!env.common.join(PID).exists());
    // the process itself is ended: gone, or a zombie until this test's process reaps it
    // (one look every 20 ms, for 5 s at most; no branch a quick ending leaves unreached)
    let gone = (0..250).any(|_| {
        std::thread::sleep(std::time::Duration::from_millis(20));
        began(&env.proc, pid).is_none()
    });
    assert!(gone);
    assert_eq!(
        verb(&words(&["stop"]), &env).stderr,
        "sampler: none is running\n"
    );
    let status = verb(&words(&["status"]), &env);
    assert!(status
        .stderr
        .starts_with("sampler: none is running - make sampler-start"));
    assert!(status
        .stderr
        .contains(&format!("pid {pid} stopped (make sampler-stop)\n")));
}

#[test]
fn a_dead_sampler_is_replaced_and_a_file_past_its_bound_is_moved_aside() {
    let (_dir, mut env) = real("dead");
    env.max_bytes = 10;
    put(&env.common.join(PID), "999999999 5\n");
    put(&env.samples(), "{\"old\": true}\n");
    let r = verb(&words(&["start"]), &env);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(r.stderr.starts_with("sampler: the one the pid file named (pid 999999999) is gone - replaced\nsampler: the samples file was past its bound (10 bytes): moved to "), "{}", r.stderr);
    assert!(r.stderr.contains("\nsampler: started (pid "));
    assert_eq!(
        super::read(&env.samples().with_file_name(KEPT)),
        "{\"old\": true}\n"
    );
    assert!(!env.samples().exists());
    assert_eq!(verb(&words(&["stop"]), &env).code, 0);
}

#[test]
fn a_sampler_that_cannot_start_or_never_names_itself_is_said() {
    let (_dir, mut env) = real("fail");
    env.worker = words(&["/no/such/program"]);
    let r = verb(&words(&["start"]), &env);
    assert_eq!(r.code, 1);
    assert!(r
        .stderr
        .starts_with("sampler: not started (/no/such/program: "));
    env.worker = Vec::new();
    assert_eq!(
        verb(&words(&["start"]), &env).stderr,
        "sampler: not started (no program)\n"
    );
    env.worker = words(&["true"]);
    env.wait_tenths = 2;
    let r = verb(&words(&["start"]), &env);
    assert_eq!(r.code, 1);
    assert!(r
        .stderr
        .starts_with("sampler: started, but it has not written "));
}

#[test]
fn run_is_the_loop_as_this_process_and_the_door_finds_the_clone() {
    let (dir, mut env) = world("run");
    env.proc = PathBuf::from("/proc");
    env.every_s = 0;
    env.max_bytes = 1;
    // were the bound broken, the loop would write as fast as it can: its seconds end it then
    env.max_s = 2;
    let r = verb(&words(&["run"]), &env);
    assert_eq!(r.stderr, "sampler: ended - the samples file is past its size bound - the next start begins a new one\n");
    assert_eq!(lines(&env.samples()).len(), 1);
    let log = super::read(&env.common.join(DIR).join("sampler.log"));
    assert!(log.contains(&format!("pid {} started", std::process::id())),);
    assert_eq!(verb(&words(&["nonsense"]), &env).code, 2);
    assert_eq!(verb(&[], &env).code, 2);
    // the door: the clone named, or the one the working directory is in
    let named = cli(
        &words(&["status", "--common", &env.common.to_string_lossy()]),
        &dir,
    );
    assert!(named
        .stderr
        .contains(&format!("{} holds 1 lines", env.samples().display())));
    let repo = l7r_gate_core::ci::fixtures::repo("sampler-door");
    let root = repo.to_path_buf();
    let found = cli(&words(&["status"]), &root);
    assert_eq!(found.code, 0);
    assert!(found.stderr.contains(&format!(
        "{} holds 0 lines",
        root.join(".git").join(DIR).join(FILE).display()
    )));
    assert_eq!(cli(&words(&["status"]), &dir).code, 2);
}

/// A sampler's line at `secs` past noon: `anon` in GiB, the memory stall so far in seconds, the load, the trees held.
fn row(secs: u64, anon: f64, stall: f64, load: f64, held: usize) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a fixture's whole bytes"
    )]
    let bytes = (anon * 1_073_741_824.0) as u64;
    json!({
        "utc": super::utc(1_795_694_400 + secs), "anon": bytes, "cur": bytes * 2, "peak": 9_663_676_416_u64,
        "max": 10_737_418_240_u64, "mem_some_us": (stall * 1e6).round(), "mem_full_us": (stall * 5e5).round(),
        "cpu_some_us": (stall * 2e6).round(), "load1": load, "cores": 22, "oom_kill": secs / 100, "rustc": secs / 10,
        "held": vec!["451 T1"; held]
    })
    .to_string()
}

fn report(env: &Env, args: &[&str]) -> String {
    let r = verb(&words(&[&["report"], args].concat()), env);
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    r.stdout
}

#[test]
fn the_report_s_rows_are_the_counts_held_and_its_arithmetic_holds() {
    let (_dir, env) = world("report");
    // the file before: one sample, three hours earlier. Then twenty a held count of 2 (anon 1.0 .. 2.9 GiB, load 1 .. 20), the
    // memory stall rising 0.5 s a sample; then, 200 s later (a gap), four at 3 held, one of them over the 7 GiB margin
    put(
        &env.samples().with_file_name(KEPT),
        &format!(
            "{}\nnot a sample\n{{\"utc\": \"2026-11-26T09:00:01Z\"}}\n",
            row(0, 0.5, 0.0, 0.5, 1).replace("T12:", "T09:")
        ),
    );
    let mut text = String::new();
    for i in 0..20_u32 {
        text.push_str(&row(
            u64::from(i) * 10,
            1.0 + f64::from(i) * 0.1,
            f64::from(i) * 0.5,
            f64::from(i + 1),
            2,
        ));
        text.push('\n');
    }
    for (i, anon) in [(0_u32, 3.0), (1, 7.5), (2, 4.0), (3, 5.0)] {
        text.push_str(&row(
            400 + u64::from(i) * 10,
            anon,
            20.0 + f64::from(i),
            44.0,
            3,
        ));
        text.push('\n');
    }
    put(&env.samples(), &text);
    let out = report(&env, &["--since", "2026-11-26T12:00:00Z"]);
    let got: Vec<&str> = out.lines().collect();
    assert_eq!(got[0], format!("sampler-report: {} - 24 samples, 2026-11-26T12:00:00Z to 2026-11-26T12:07:10Z (7.2 minutes); memory.max 10.00 GiB, 22 cores, margin 7 GiB (L7R_MEM_MARGIN_GIB, a GUESS knob)", env.samples().display()));
    // held 2: median of 1.0..2.9 is the mean of 1.9 and 2.0; the 95th of twenty is the 19th, 2.8; nineteen rises of 0.5 s
    assert_eq!(got[3], "     2 |      20 | 1.95 / 2.80 / 2.90 | 29% | 0 | 9.5 / 4.8 | 19.0 | 10.5 / 19.0 / 20.0 | 0.9x | 19 | 1");
    // held 3: the pair across the gap is in no row, so three rises of 1 s; 4.0 and 5.0 are the middle two of four
    assert_eq!(got[4], "     3 |       4 | 4.50 / 7.50 / 7.50 | 75% | 1 | 3.0 / 1.5 | 6.0 | 44.0 / 44.0 / 44.0 | 2.0x | 43 | 0");
    assert_eq!(got[2], "   all |      24 | 2.15 / 5.00 / 7.50 | 75% | 1 | 12.5 / 6.2 | 25.0 | 12.5 / 44.0 / 44.0 | 2.0x | 43 | 1");
    // the sampled memory.current peak (twice 7.5 GiB) is over the cgroup's memory.peak of 9 GiB: said
    assert!(got[5].starts_with("  memory.current: sampled peak 15.00 GiB; the cgroup's memory.peak 9.00 GiB at the last sample, risen 0.00 GiB in the window - DISAGREE"), "{}", got[5]);
    assert!(got[6].starts_with("  gaps: 1 (two samples more than 120 s apart"));
    assert!(got[6].ends_with("lines that are no sample: 2"));
    // the whole of both files: the earlier file's sample is the row held 1, its two bad lines counted; a window with nothing
    let whole = report(&env, &[]);
    assert!(whole.contains("\n     1 |       1 | 0.50 / 0.50 / 0.50 | 5% | 0 | - / - | - | 0.5 / 0.5 / 0.5 | 0.0x | 0 | -\n"), "{whole}");
    assert!(whole.contains("gaps: 2 (") && whole.contains("lines that are no sample: 2\n"),);
    let until = report(
        &env,
        &[
            "--since",
            "2026-11-26T12:00:00Z",
            "--until",
            "2026-11-26T12:03:10Z",
        ],
    );
    assert!(until.contains(" - 20 samples, ") && until.contains("sampled peak 5.80 GiB; the cgroup's memory.peak 9.00 GiB at the last sample, risen 0.00 GiB in the window - agree\n"), "{until}");
    let none = report(&env, &["--since", "2027-01-01T00:00:00Z"]);
    assert_eq!(
        none,
        format!(
            "sampler-report: {} - no sample in the window (2 lines that are none)\n",
            env.samples().display()
        )
    );
}

#[test]
fn the_report_reads_the_hand_logs_of_2026_11_26_a_table_a_file() {
    let (dir, env) = world("hand");
    let with = dir.join("mem-samples-two.log");
    let without = dir.join("mem-samples-three.log");
    put(&with, "2026-11-26T12:39:22Z anon=1073741824 cur=9116770304 peak=10725941248 mem_some_us=1000000 load=1.31 builders=2\n2026-11-26T12:39:32Z anon=3221225472 cur=9062125568 peak=10725941248 mem_some_us=3500000 load=2.50 builders=2\n");
    put(&without, "2026-11-26T13:37:06Z anon=2147483648 cur=9317040128 mem_some_us=285155204 load=0.94 oom_kill=0 rustc=4\n");
    let logs = format!("{} {}", with.display(), without.display());
    let out = report(&env, &["--log", &logs]);
    let got: Vec<&str> = out.lines().collect();
    // no memory.max and no cores in a hand log: the machine's, as the cgroup and the sampler's own count give them now
    assert!(got[0].starts_with("sampler-report: mem-samples-two.log - 2 samples, 2026-11-26T12:39:22Z to 2026-11-26T12:39:32Z (0.2 minutes); memory.max 10.00 GiB, 22 cores"), "{}", got[0]);
    assert_eq!(got[3], "     2 |       2 | 2.00 / 3.00 / 3.00 | 30% | 0 | 2.5 / - | - | 1.9 / 2.5 / 2.5 | 0.1x | - | -");
    assert!(got[4].starts_with("  memory.current: sampled peak 8.49 GiB; the cgroup's memory.peak 9.99 GiB at the last sample"), "{}", got[4]);
    assert!(got[7].starts_with("sampler-report: mem-samples-three.log - 1 samples"));
    assert_eq!(got[10], "     ? |       1 | 2.00 / 2.00 / 2.00 | 20% | 0 | - / - | - | 0.9 / 0.9 / 0.9 | 0.0x | 4 | -");
    assert_eq!(
        got[11],
        "  memory.current: sampled peak 8.68 GiB; no memory.peak in these samples"
    );
    // no limit anywhere, and a sample with no load
    std::fs::remove_file(env.cgroup.join("memory.max")).unwrap();
    put(&without, "2026-11-26T13:37:06Z anon=2147483648\n\n");
    let bare = report(&env, &["--log", &without.to_string_lossy()]);
    assert!(
        bare.contains("memory.max - GiB")
            && bare.contains(
                "\n   all |       1 | 2.00 / 2.00 / 2.00 | - | 0 | - / - | - | - | 0.0x | - | -\n"
            ),
    );
    // a log that is not there is named, exit 2, the others still read
    let r = verb(
        &words(&[
            "report",
            "--log",
            "/no/such.log",
            "--log",
            &with.to_string_lossy(),
        ]),
        &env,
    );
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (2, "sampler-report: /no/such.log is no file\n")
    );
    assert!(r
        .stdout
        .starts_with("sampler-report: mem-samples-two.log - 2 samples"));
}

#[test]
fn a_counter_that_fell_is_a_gap_and_its_pair_is_booked_to_no_row() {
    let (_dir, env) = world("fell");
    // ten seconds apart throughout; the memory stall reads 5 s, then 1 s (the cgroup was made again), then 3 s
    let text = [(0, 5.0), (10, 1.0), (20, 3.0)].map(|(secs, stall)| row(secs, 2.0, stall, 1.0, 2));
    put(&env.samples(), &text.join("\n"));
    let out = report(&env, &[]);
    let got: Vec<&str> = out.lines().collect();
    // the fall is booked nowhere, and neither is that pair's rise of CPU stall; the one pair after it is: 2 s, 1 s and 4 s
    assert_eq!(got[3], "     2 |       3 | 2.00 / 2.00 / 2.00 | 20% | 0 | 2.0 / 1.0 | 4.0 | 1.0 / 1.0 / 1.0 | 0.0x | 2 | 0");
    assert!(
        got[5].starts_with("  gaps: 1 (two samples more than 120 s apart, or a counter that fell")
    );
}
