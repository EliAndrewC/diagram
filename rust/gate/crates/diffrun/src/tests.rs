//! The runner's tests (feature 449 T161), on tiny shell sides in a temporary directory: no network, nothing left in `TMPDIR`. The plan's
//! exits are `an_input_moved_reruns_its_case_and_keeps_the_rest`, `a_declared_source_reruns_only_the_new_sides_that_declare_it`,
//! `verify_reruns_every_new_side`, `all_is_refused_without_a_reason`; the lint's are in the plan crate.

use std::path::{Path, PathBuf};

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use crate::{cli, Ctx};

mod checkout;
mod jobs;
mod reuse;

/// A side of the runner's tests. Every program it starts costs a side about 2 ms, and a test runs up to fourteen sides (feature 449 T167,
/// FR-008's tenth of a second): `hello`'s stamp is one each side writes in the stamp's form, the two sides' different, where `date` gave
/// the clock's (the `stamp` normalization still has two different stamps to make equal, and no second's turn can split them), and
/// `out/` is made only where the setup did not make it.
const SIDE: &str = r#"#!/bin/sh
# a side of the runner's tests: one mode a step, its outputs on stdout, stderr and under out/
mode=$1; shift
d=""; [ -f "$ROOTDIR/new-differs" ] && [ "$SIDE_NAME" = new ] && d=" there"
stamp=20261117T010101Z; [ "$SIDE_NAME" = new ] && stamp=20261117T020202Z
case "$mode" in
  hello) echo "hello$d $1"; [ -d out ] || mkdir out; echo "made $1 $stamp in $DIFF_RUN_WORLD" > out/made.txt ;;
  noisy) [ -d out ] || mkdir out; date +%s%N > out/noise.txt ;;
  fail) echo "no such thing$d" >&2; exit 3 ;;
  rm) rm -f out/seed.txt ;;
  bin) [ -d out ] || mkdir out; printf '\377\376' > out/bin.dat ;;
  big) [ -d out ] || mkdir out; seq 1 3000 > out/big.txt ;;
  two) mkdir -p out/a1 out/a2; echo one > out/a1/f; echo two > out/a2/f ;;
  link) [ -d out ] || mkdir out; ln -s target out/link ;;
  log) echo b >> server.log; echo a >> server.log; echo s > status ;;
  lines) printf 'z\ny\nx\n' ;;
  code) [ -n "$d" ] && exit 5; exit 0 ;;
esac
"#;

struct Fx {
    dir: TempDir,
}

impl Fx {
    fn new() -> Self {
        let fx = Self {
            dir: TempDir::new("diffrun-test"),
        };
        for (name, text) in [
            ("old.sh", SIDE),
            ("new.sh", SIDE),
            ("src/a.txt", "a\n"),
            ("src/b.txt", "b\n"),
            ("in1.txt", "1\n"),
            ("in2.txt", "2\n"),
        ] {
            fx.write(name, text);
        }
        fx
    }

    fn root(&self) -> &Path {
        self.dir.path()
    }

    fn write(&self, name: &str, text: &str) {
        let p = self.root().join(name);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, text).unwrap();
    }

    fn base(cases: &Value) -> Value {
        json!({
            "vars": {"OUT": "{WORLD}/out"},
            "world": {
                // one setup command where there were two, the flaky check in the same `sh` (feature 449 T167: a program a side less)
                "setup": [
                    ["sh", "-c", "[ -z \"$FAILSETUP\" ] && mkdir -p {OUT} && echo seed > {OUT}/seed.txt && echo st > {WORLD}/status && if [ -n \"$FLAKY\" ] && [ \"$DIFF_RUN_SIDE\" = old ]; then [ ! -e \"$ROOTDIR/flaky\" ] || exit 1; touch \"$ROOTDIR/flaky\"; fi"]
                ],
                "files": ["out", "server.log"],
                "ignore": [".git"],
                // the status read as a path, not by `cat` twice a side; the one test that reads it puts the `cmd` form back (feature 449 T167)
                "extras": [{"name": "status", "path": "{WORLD}/status"}, {"name": "kept log", "path": "{WORLD}/server.log"}],
                "env": {"ROOTDIR": "{ROOT}", "DROPPED": null},
                "env_drop_prefixes": ["L7R_TEST_NEVER_"],
                "max_text_bytes": 1000,
                "inputs": ["in1.txt"]
            },
            "sides": {
                "old": {"label": "py", "cmd": ["sh", "{ROOT}/old.sh"], "env": {"SIDE_NAME": "old"}, "build": [["true"]], "fingerprint": ["old.sh"]},
                "new": {"label": "rs", "cmd": ["sh", "{ROOT}/new.sh"], "env": {"SIDE_NAME": "{SIDE}"}, "vars": {"X": "x"}, "fingerprint": ["new.sh", "src"]}
            },
            "normalizations": [
                {"name": "stamp", "regex": "\\d{8}T\\d{6}Z"},
                {"name": "rank", "regex": "a\\d", "replace": "aN", "on": ["names"]},
                {"name": "log-sorted", "sort": "\n", "where": "server\\.log", "on": ["files"]},
                {"name": "sorted-stdout", "sort": "\n", "on": ["stdout"], "opt_in": true}
            ],
            "cases": cases
        })
    }

    fn cases_file(&self, v: &Value) -> PathBuf {
        let p = self.root().join("cases.json");
        std::fs::write(&p, v.to_string()).unwrap();
        p
    }

    fn run(&self, v: &Value, flags: &[&str]) -> (l7r_gate_core::Reply, Value) {
        let file = self.cases_file(v);
        let mut args = vec![file.display().to_string()];
        args.extend(flags.iter().map(|f| (*f).to_owned()));
        let log = self.root().join("guard-log");
        let r = cli(
            &args,
            &Ctx {
                log_dir: &log,
                session: "sess-t161".to_owned(),
                cwd: self.root().to_path_buf(),
            },
        );
        let report = r
            .stdout
            .lines()
            .find_map(|l| l.strip_prefix("report: "))
            .map_or(Value::Null, |p| {
                serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap()
            });
        (r, report)
    }

    fn guard_log(&self) -> Vec<Value> {
        std::fs::read_dir(self.root().join("guard-log"))
            .unwrap()
            .flatten()
            .map(|e| serde_json::from_str(&std::fs::read_to_string(e.path()).unwrap()).unwrap())
            .collect()
    }
}

fn hello(name: &str, sources: Option<&[&str]>) -> Value {
    let mut c = json!({"name": name, "steps": [["{CMD}", "hello", name]]});
    if let Some(s) = sources {
        c["sources"] = json!(s);
    }
    c
}

/// Each case's (old rerun, new rerun), by name.
fn reruns(report: &Value) -> Vec<(String, bool, bool)> {
    report["cases"]
        .as_array()
        .unwrap()
        .iter()
        .map(|c| {
            (
                c["name"].as_str().unwrap().to_owned(),
                c["old"]["rerun"] == true,
                c["new"]["rerun"] == true,
            )
        })
        .collect()
}

fn three() -> Value {
    json!([
        hello("one", Some(&["src/a.txt"])),
        hello("two", Some(&["src/b.txt"])),
        {"name": "three", "steps": [["{CMD}", "hello", "three"]], "inputs": ["in2.txt"]}
    ])
}

#[test]
fn a_first_run_runs_every_side_and_a_second_keeps_them_all() {
    let fx = Fx::new();
    let v = Fx::base(&three());
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 0, "{}{}", r.stdout, r.stderr);
    assert_eq!(
        (
            rep["kind"].as_str(),
            rep["sides_rerun"].as_u64(),
            rep["sides_kept"].as_u64()
        ),
        (Some("incremental"), Some(6), Some(0))
    );
    assert!(r.stdout.contains("3 cases, 0 differing"));
    let norms = &rep["normalizations"];
    assert_eq!(
        (norms["stamp"].as_u64(), norms["world-path"].as_u64()),
        (Some(3), Some(3))
    );
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(
        (
            r.code,
            rep["sides_rerun"].as_u64(),
            rep["sides_kept"].as_u64()
        ),
        (0, Some(0), Some(6))
    );
    // the worlds are removed after each side
    assert!(!fx.root().join("cases.diff-run/work/old").exists());
    assert!(fx.root().join("cases.diff-run/results").is_dir());
}

#[test]
fn an_input_moved_reruns_its_case_and_keeps_the_rest() {
    let fx = Fx::new();
    let v = Fx::base(&three());
    fx.run(&v, &[]);
    fx.write("in2.txt", "2 moved\n");
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 0);
    assert_eq!(
        reruns(&rep),
        [
            ("one".to_owned(), false, false),
            ("two".to_owned(), false, false),
            ("three".to_owned(), true, true)
        ]
    );
    // a world-wide input moves every case
    fx.write("in1.txt", "1 moved\n");
    assert_eq!(fx.run(&v, &[]).1["sides_rerun"].as_u64(), Some(6));
}

#[test]
fn a_declared_source_reruns_only_the_new_sides_that_declare_it() {
    let fx = Fx::new();
    let v = Fx::base(&three());
    fx.run(&v, &[]);
    fx.write("src/a.txt", "a fixed\n");
    let (_, rep) = fx.run(&v, &[]);
    // "three" declares no sources: it is keyed on the whole new fingerprint (`src` among it), so a rebuild reruns its new side
    assert_eq!(
        reruns(&rep),
        [
            ("one".to_owned(), false, true),
            ("two".to_owned(), false, false),
            ("three".to_owned(), false, true)
        ]
    );
    // a declaration tightened moves no old side
    let mut tighter = three();
    tighter[1]["sources"] = json!(["src/b.txt", "src/a.txt"]);
    let (_, rep) = fx.run(&Fx::base(&tighter), &[]);
    assert_eq!(rep["cases"][1]["old"]["rerun"], false);
    assert_eq!(rep["cases"][1]["new"]["rerun"], true);
    // the old side's own fingerprint moves every old side and no new side that declares its sources
    fx.write("old.sh", &format!("{SIDE}# a comment\n"));
    let (_, rep) = fx.run(&Fx::base(&tighter), &[]);
    assert_eq!(
        reruns(&rep),
        [
            ("one".to_owned(), true, false),
            ("two".to_owned(), true, false),
            ("three".to_owned(), true, false)
        ]
    );
}

#[test]
fn verify_reruns_every_new_side() {
    let fx = Fx::new();
    let v = Fx::base(&three());
    fx.run(&v, &[]);
    fx.write("new-differs", "");
    let (r, rep) = fx.run(&v, &["--verify"]);
    assert_eq!(r.code, 1, "the new side now differs");
    assert_eq!(rep["kind"], "verify");
    assert!(r.stdout.contains("diff-run-verify-"), "{}", r.stdout);
    assert!(reruns(&rep).iter().all(|(_, old, new)| !old && *new));
    assert_eq!(rep["differing"].as_array().unwrap().len(), 3);
    assert!(rep["cases"][0]["diffs"][0]
        .as_str()
        .unwrap()
        .contains("step 0 stdout\n--py--\nhello one\n\n--rs--\nhello there one"));
    assert!(r.stdout.contains("DIFF old"));
    // an incremental report's path never carries the verify name
    let (r, _) = fx.run(&v, &[]);
    assert!(r.stdout.contains("diff-run-incremental-") && !r.stdout.contains("diff-run-verify"));
}

#[test]
fn all_is_refused_without_a_reason() {
    let fx = Fx::new();
    let v = Fx::base(&three());
    for flags in [&["--all"][..], &["--all", "--reason", "short"]] {
        let (r, _) = fx.run(&v, flags);
        assert_eq!(r.code, 2);
        assert!(
            r.stderr.contains("REASON=") && r.stderr.contains("make diff-run CASES=... ALL=1"),
            "{}",
            r.stderr
        );
    }
    assert!(!fx.root().join("cases.diff-run").exists(), "nothing ran");
    let blocked = fx.guard_log();
    assert_eq!(blocked.len(), 2);
    assert!(blocked.iter().all(|e| e["event"] == "blocked"
        && e["rule"] == "all-no-reason"
        && e["guard"] == "diff-run"));
    fx.run(&v, &[]);
    let (r, rep) = fx.run(&v, &["--all", "--reason", "the harness world changed"]);
    assert_eq!(r.code, 0);
    assert_eq!(
        (rep["kind"].as_str(), rep["sides_rerun"].as_u64()),
        (Some("all"), Some(6))
    );
    assert_eq!(rep["reason"], "the harness world changed");
    let escaped: Vec<Value> = fx
        .guard_log()
        .into_iter()
        .filter(|e| e["event"] == "escaped")
        .collect();
    assert_eq!(
        (
            escaped.len(),
            escaped[0]["detail"].as_str(),
            escaped[0]["rule"].as_str()
        ),
        (1, Some("the harness world changed"), Some("all"))
    );
}

#[test]
fn twice_reports_run_to_run_noise_and_only_reruns_one_case() {
    let fx = Fx::new();
    let v = Fx::base(&json!([
        hello("calm", None),
        {"name": "noisy", "steps": [["{CMD}", "noisy"]]},
        {"name": "flaky", "steps": [["{CMD}", "hello", "f"]], "env": {"FLAKY": "1"}},
        {"name": "broken", "steps": [["{CMD}", "hello", "b"]], "env": {"FAILSETUP": "1"}}
    ]));
    let (r, rep) = fx.run(&v, &["--twice"]);
    assert_eq!((r.code, rep["kind"].as_str()), (1, Some("twice")));
    assert_eq!(rep["cases"][0]["noise"], json!([]));
    assert!(rep["cases"][1]["noise"][0]
        .as_str()
        .unwrap()
        .starts_with("file out/noise.txt"));
    assert!(rep["cases"][2]["noise"][0]
        .as_str()
        .unwrap()
        .starts_with("old side's second run: setup"));
    assert!(r.stdout.contains("noise: 1"));
    let (r, rep) = fx.run(&v, &["--only", "calm"]);
    assert_eq!(
        (r.code, rep["kind"].as_str(), rep["cases_total"].as_u64()),
        (0, Some("only"), Some(1))
    );
    assert_eq!(reruns(&rep), [("calm".to_owned(), false, true)]);
    let (r, _) = fx.run(&v, &["--only", "nope"]);
    assert!(
        r.code == 2
            && r.stderr
                .contains("no case named \"nope\"; the cases are: calm, noisy, flaky, broken")
    );
}

/// The case of every kind of output, and its cases file: an extra read by a command among them.
fn outputs(more: &[Value]) -> Value {
    let mut cases = vec![json!(
        {"name": "outputs", "steps": [["{CMD}", "fail"], {"argv": ["{CMD}", "rm"], "compare": false}, ["{CMD}", "bin"], ["{CMD}", "big"],
                                       ["{CMD}", "two"], ["{CMD}", "link"], ["{CMD}", "log"], ["{CMD}", "lines"], ["{CMD}", "code"],
                                       {"argv": ["sh", "-c", "mkdir -p out/.git && echo x > out/.git/f"], "compare": false}],
         "norms": ["sorted-stdout"]}
    )];
    cases.extend(more.iter().cloned());
    let mut v = Fx::base(&Value::Array(cases));
    v["world"]["extras"][0] = json!({"name": "status", "cmd": ["cat", "{WORLD}/status"]});
    v
}

#[test]
fn every_output_is_compared_and_each_normalization_taken_is_listed() {
    let fx = Fx::new();
    let v = outputs(&[
        json!({"name": "files narrowed", "steps": [["{CMD}", "hello", "x"], ["sh", "-c", "echo \"[$MAKELEVEL$MAKEFLAGS]\""]], "files": ["out/made.txt"]}),
    ]);
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 0, "{}", r.stdout);
    let taken = rep["cases"][0]["norms"].as_array().unwrap();
    for n in ["log-sorted", "name-rank", "rank", "sorted-stdout"] {
        assert!(taken.contains(&json!(n)), "{n} in {taken:?}");
    }
    let kept: Value = serde_json::from_str(
        &std::fs::read_to_string(fx.root().join(format!(
            "cases.diff-run/results/{}.new.json",
            crate::runner::case_id("outputs")
        )))
        .unwrap(),
    )
    .unwrap();
    let files = &kept["result"]["files"];
    assert_eq!(files["out/seed.txt"], "<deleted>");
    assert!(files["out/bin.dat"]
        .as_str()
        .unwrap()
        .starts_with("<bytes 2 "));
    assert!(files["out/big.txt"]
        .as_str()
        .unwrap()
        .starts_with("<text 13893 "));
    assert_eq!(
        (files["out/aN/f"].as_str(), files["out/aN/f #2"].as_str()),
        (Some("one\n"), Some("two\n"))
    );
    assert_eq!(files["out/link"], "<link -> target>");
    assert_eq!(files["server.log"], "\na\nb");
    assert_eq!(files["<status>"], "s\n");
    // a normalization scoped to a file name reaches no other name
    assert_eq!(files["<kept log>"], "b\na\n");
    assert_eq!(
        kept["result"]["steps"][0],
        json!([3, "", "no such thing\n"])
    );
    assert_eq!(kept["result"]["steps"][6][1], "\nx\ny\nz");
    let narrowed = &rep["cases"][1];
    assert_eq!(narrowed["same"], true);
    let kept: Value = serde_json::from_str(
        &std::fs::read_to_string(fx.root().join(format!(
            "cases.diff-run/results/{}.old.json",
            crate::runner::case_id("files narrowed")
        )))
        .unwrap(),
    )
    .unwrap();
    // make's variables never reach a side
    assert_eq!(kept["result"]["steps"][1][1], "[]\n");
    // an ignored directory is not compared
    assert!(!files
        .as_object()
        .unwrap()
        .keys()
        .any(|k| k.contains(".git")));
}

/// Split from the test above (feature 449 T167, FR-008's tenth of a second: the two together took 140 ms): the outputs case alone, its
/// new side differing from the start, where the test above ran it the same first and then verified - the old side's result is the one
/// the first run kept either way.
#[test]
fn the_new_side_differing_in_exit_and_stderr_is_said_step_by_step() {
    let fx = Fx::new();
    fx.write("new-differs", "");
    let (r, rep) = fx.run(&outputs(&[]), &["--verify"]);
    assert_eq!(r.code, 1);
    let d = rep["cases"][0]["diffs"].as_array().unwrap();
    assert!(d[0]
        .as_str()
        .unwrap()
        .starts_with("step 0 stderr\n--py--\nno such thing\n\n--rs--\nno such thing there"));
    assert_eq!(d[1], "step 7 exit 0 != 5");
}

#[test]
fn a_side_that_fails_to_run_is_reported_and_kept_nowhere() {
    let fx = Fx::new();
    let v = Fx::base(&json!([
        {"name": "setup fails", "steps": [["{CMD}", "hello", "a"]], "env": {"FAILSETUP": "1"}},
        {"name": "cannot start", "steps": [["/no/such/program"]]},
        {"name": "killed", "steps": [["sh", "-c", "kill -9 $$"]]}
    ]));
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 1);
    let errors = |i: usize| {
        rep["cases"][i]["errors"][0]
            .as_str()
            .unwrap_or_default()
            .to_owned()
    };
    assert!(errors(0).starts_with("old side: setup `sh -c") && errors(0).contains("exited 1"));
    assert!(errors(1).contains("/no/such/program: cannot start"));
    // a signal's death is an exit, compared: 128 + 9
    assert_eq!(rep["cases"][2]["same"], true);
    assert!(r.stdout.contains("FAIL old       -"), "{}", r.stdout);
    // nothing failed was kept: the next run runs it again
    let (_, rep) = fx.run(&v, &[]);
    assert_eq!(reruns(&rep)[0], ("setup fails".to_owned(), true, true));
    assert_eq!(reruns(&rep)[2], ("killed".to_owned(), false, false));
}

/// Split from the test above (feature 449 T160): the timeout alone, the one case that waits, in the test build's seconds (`run::SECOND`);
/// the case it shared a run with took 4.3 s for its four waits of a second. One side waits, at a timeout of one of those seconds (feature
/// 449 T167, FR-008's tenth of a second: both sides waiting out three took 321 ms): the old side's `sleep` is a stand-in that returns at
/// once, and the only other commands under the timeout are `true` and the step's own start - at two seconds a two-command `sh` setup
/// outran it once under a load of other tests (2026-11-17), so the setup is `true` and there is no build.
///
/// THE WINDOW CALIBRATED (feature 449 T391): the one-second timeout's `true` setup itself timed out under the cover build at a load of
/// about nineteen on twenty-two cores (449 T351's second paired run, 2026-11-23), and again, 37 runs in 40, with the test pinned to one
/// core beside 48 busy loops (2026-11-23, `taskset -c 3`), where it passed 40 in 40 after. So the timeout is no hard-coded figure: a
/// calibration loop runs `true` five times through the runner's own `run::command` just before the case, and the timeout is ten of the
/// slowest of those starts, in the test build's seconds, at least one - a quiet machine keeps the one second (50 ms); a loaded one
/// widens it as its starts slow (l7r/diagram/CLAUDE.md: a CPU-time bound in a test is scaled by a calibration loop). The real `sleep`
/// the new side runs outlasts the window by a second.
#[test]
fn a_side_that_outruns_its_timeout_is_stopped_and_named() {
    let fx = Fx::new();
    std::fs::create_dir_all(fx.root().join("quick")).unwrap();
    l7r_gate_core::write_executable(&fx.root().join("quick/sleep"), "#!/bin/sh\n");
    let env = [("PATH".to_owned(), "/usr/bin:/bin".to_owned())];
    let slowest = (0..5)
        .map(|_| {
            let t = std::time::Instant::now();
            crate::run::command(
                &["true".to_owned()],
                fx.root(),
                &env,
                std::time::Duration::from_secs(60),
            )
            .unwrap();
            t.elapsed()
        })
        .max()
        .unwrap();
    let timeout = (10 * slowest.as_micros())
        .div_ceil(crate::run::SECOND.as_micros())
        .max(1);
    let sleep = (u128::from(u32::try_from(timeout).unwrap()) * crate::run::SECOND.as_millis())
        .div_ceil(1000)
        + 1;
    let mut v = Fx::base(&json!([{"name": "slow", "steps": [["sleep", sleep.to_string()]]}]));
    v["world"]["timeout_s"] = json!(u64::try_from(timeout).unwrap());
    v["world"]["setup"] = json!([["true"]]);
    v["sides"]["old"].as_object_mut().unwrap().remove("build");
    v["sides"]["old"]["env"]["PATH"] = json!("{ROOT}/quick:/usr/bin:/bin");
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 1);
    let said = rep["cases"][0]["errors"][0].as_str().unwrap_or_default();
    let want = format!("sleep {sleep}: timed out after {timeout} s");
    assert!(said.contains(&want), "{said}");
}

#[test]
fn a_run_is_refused_before_anything_runs() {
    let fx = Fx::new();
    let mut v = Fx::base(&three());
    v["cases"][0]["sources"] = json!(["src/missing.txt"]);
    let (r, _) = fx.run(&v, &[]);
    assert!(
        r.code == 2
            && r.stderr.contains("src/missing.txt: ")
            && r.stderr.contains("a declared path must exist"),
        "{}",
        r.stderr
    );
    let mut v = Fx::base(&three());
    v["sides"]["new"]["build"] = json!([["sh", "-c", "echo broken >&2; exit 4"]]);
    let (r, _) = fx.run(&v, &[]);
    assert!(
        r.code == 2
            && r.stderr
                .contains("new side's build `sh -c echo broken >&2; exit 4` exited 4:\nbroken"),
        "{}",
        r.stderr
    );
    let mut v = Fx::base(&three());
    v["sides"]["new"]["build"] = json!([["/no/such/build"]]);
    assert!(fx.run(&v, &[]).0.stderr.contains("cannot start"));
    // a bare name the side's `PATH` holds nowhere (feature 449 T167: `run::on_path` leaves it to the child's own lookup)
    v["sides"]["new"]["build"] = json!([["no-such-build-t167"]]);
    assert!(fx
        .run(&v, &[])
        .0
        .stderr
        .contains("no-such-build-t167: cannot start"));
    v["sides"]["new"]["build"] = json!([["/no/such/build"]]);
    for (flags, why) in [
        (&["--verify", "--only", "one"][..], "takes no --only"),
        (&["--reason", "a b c"], "--reason goes with --all"),
        (&["--nope"], "no flag --nope"),
        (&["--only"], "--only takes a case name"),
        (&["--all", "--reason"], "--reason takes the reason"),
        (&["extra.json"], "one cases file, not also extra.json"),
    ] {
        let (r, _) = fx.run(&v, flags);
        assert!(r.code == 2 && r.stderr.contains(why) && r.stderr.contains("usage:"));
    }
}

#[test]
fn a_git_revision_fingerprints_a_side() {
    let fx = Fx::new();
    let repo = fx.root().join("repo");
    let git = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&repo)
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    };
    std::fs::create_dir_all(&repo).unwrap();
    git(&["init", "-q"]);
    std::fs::write(repo.join("f"), "1").unwrap();
    git(&["add", "f"]);
    git(&[
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-qm",
        "one",
    ]);
    let mut v = Fx::base(&three());
    // a declared directory's `.git` is git's store, not a source: the revision is read through `{"git", "rev"}`
    v["sides"]["old"]["fingerprint"] =
        json!([{"git": "repo", "rev": "HEAD"}, {"git": "repo", "rev": "HEAD"}, "repo"]);
    assert_eq!(fx.run(&v, &[]).0.code, 0);
    assert_eq!(fx.run(&v, &[]).1["sides_rerun"].as_u64(), Some(0));
    v["sides"]["old"]["fingerprint"] = json!([{"git": "repo", "rev": "no-such-rev"}]);
    assert!(fx
        .run(&v, &[])
        .0
        .stderr
        .contains("fingerprint: no-such-rev names no revision in"));
}

/// A refusal the cases file earns: the words it names, the field (a JSON pointer into the base file) and the value put there.
type Broken = (&'static str, &'static str, Value);

fn broken_world() -> Vec<Broken> {
    vec![
        ("world.setup: the commands", "/world/setup", json!([])),
        (
            "world.setup: a list of argv lists",
            "/world/setup",
            json!("x"),
        ),
        (
            "world.setup: every item is a string",
            "/world/setup",
            json!([[1]]),
        ),
        (
            "world.files: a list of strings",
            "/world/files",
            json!("out"),
        ),
        (
            "world.env: each value a string",
            "/world/env",
            json!({"A": 1}),
        ),
        ("world.env: an object", "/world/env", json!([])),
        ("world.extras: a list", "/world/extras", json!({})),
        (
            "world.extras: each has a name",
            "/world/extras",
            json!([{}]),
        ),
        (
            "world.extras e: exactly one of `path` or `cmd`",
            "/world/extras",
            json!([{"name": "e"}]),
        ),
        ("normalizations: a list", "/normalizations", json!({})),
        (
            "normalizations: each has a name",
            "/normalizations",
            json!([{}]),
        ),
        (
            "exactly one of `regex` or `sort`",
            "/normalizations",
            json!([{"name": "n"}]),
        ),
        (
            "normalization n: ",
            "/normalizations",
            json!([{"name": "n", "regex": "("}]),
        ),
        (
            "`on` takes stdout, stderr, files, names - not x",
            "/normalizations",
            json!([{"name": "n", "sort": "\n", "on": ["x"]}]),
        ),
        (
            "normalizations: n is named twice",
            "/normalizations",
            json!([{"name": "n", "sort": "\n"}, {"name": "n", "sort": "\n"}]),
        ),
    ]
}

fn broken_cases() -> Vec<Broken> {
    let c = |steps: Value| json!([{"name": "c", "steps": steps}]);
    vec![
        ("cases: a non-empty list", "/cases", json!([])),
        ("cases: each has a name", "/cases", json!([{}])),
        (
            "case c: `steps` is a non-empty list",
            "/cases",
            json!([{"name": "c"}]),
        ),
        ("case c: a step is an argv list", "/cases", c(json!([1]))),
        ("case c: a step has an empty argv", "/cases", c(json!([[]]))),
        (
            "case c: no normalization named zz",
            "/cases",
            json!([{"name": "c", "steps": [["true"]], "norms": ["zz"]}]),
        ),
        (
            "cases: c is named twice",
            "/cases",
            json!([{"name": "c", "steps": [["true"]]}, {"name": "c", "steps": [["true"]]}]),
        ),
        ("sides.old: the side is missing", "/sides", json!({})),
        (
            "sides.new.fingerprint: the files the side runs from",
            "/sides/new/fingerprint",
            json!([]),
        ),
        (
            "fingerprint: an object entry is",
            "/sides/new/fingerprint",
            json!([{"git": "x"}]),
        ),
        (
            "fingerprint: a path or",
            "/sides/new/fingerprint",
            json!([1]),
        ),
    ]
}

#[test]
fn a_cases_file_is_checked_whole() {
    let fx = Fx::new();
    for (why, at, value) in broken_world().into_iter().chain(broken_cases()) {
        let mut v = Fx::base(&three());
        *v.pointer_mut(at).unwrap() = value;
        let (r, _) = fx.run(&v, &[]);
        assert!(r.code == 2 && r.stderr.contains(why), "{why}: {}", r.stderr);
    }
    let direct = |file: &Path| {
        cli(
            &[file.display().to_string()],
            &Ctx {
                log_dir: fx.root(),
                session: String::new(),
                cwd: fx.root().to_path_buf(),
            },
        )
    };
    let r = direct(&fx.root().join("absent.json"));
    assert!(r.code == 2 && r.stderr.contains("absent.json: "));
    fx.write("bad.json", "{not json");
    let r = direct(&fx.root().join("bad.json"));
    assert!(
        r.code == 2 && r.stderr.contains("bad.json: key must be a string"),
        "{}",
        r.stderr
    );
}

#[test]
fn the_pieces_hold_on_their_own() {
    use crate::cases::{fill, state_dir};
    use crate::norm::{compare, Kept};
    let vars = [
        ("A".to_owned(), "{B}/a".to_owned()),
        ("B".to_owned(), "b".to_owned()),
    ]
    .into_iter()
    .collect();
    assert_eq!(fill("{A} {C}", &vars), "b/a {C}");
    assert_eq!(
        state_dir(Path::new("/x/t146.json")),
        Path::new("/x/t146.diff-run")
    );
    let k = |steps: Vec<(i32, String, String)>| Kept {
        steps,
        files: std::collections::BTreeMap::new(),
        taken: std::collections::BTreeSet::new(),
        took_s: 0.0,
    };
    assert_eq!(
        compare(
            &k(vec![]),
            &k(vec![(0, String::new(), String::new())]),
            "a",
            "b"
        ),
        ["compared steps 0 != 1"]
    );
    assert_eq!(Kept::from_json(&json!({"steps": []})), None);
    let id = crate::runner::case_id("make archive https://x/y z");
    assert!(id.starts_with("make_archive_https___x_y_z-") && id.len() == 27 + 10);
    // a kept result that cannot be read is run again, not trusted
    let fx = Fx::new();
    let v = Fx::base(&json!([hello("one", None)]));
    fx.run(&v, &[]);
    std::fs::write(
        fx.root().join(format!(
            "cases.diff-run/results/{}.old.json",
            crate::runner::case_id("one")
        )),
        "{}",
    )
    .unwrap();
    assert_eq!(
        reruns(&fx.run(&v, &[]).1),
        [("one".to_owned(), true, false)]
    );
}

#[test]
fn a_state_that_cannot_be_written_is_said_so() {
    let fx = Fx::new();
    let v = Fx::base(&json!([hello("one", None)]));
    fx.write("cases.diff-run/results", "a file where the directory goes");
    let (r, rep) = fx.run(&v, &[]);
    assert_eq!(r.code, 1);
    assert!(rep["cases"][0]["errors"][0]
        .as_str()
        .unwrap()
        .contains("cases.diff-run/results/one-"));
    std::fs::remove_dir_all(fx.root().join("cases.diff-run/work")).unwrap();
    fx.write("cases.diff-run/work", "a file where the worlds go");
    std::fs::remove_file(fx.root().join("cases.diff-run/results")).unwrap();
    let (_, rep) = fx.run(&v, &[]);
    assert!(rep["cases"][0]["errors"][0]
        .as_str()
        .unwrap()
        .starts_with("old side: "));
    std::fs::remove_dir_all(fx.root().join("cases.diff-run/reports")).unwrap();
    fx.write("cases.diff-run/reports", "a file where the reports go");
    let (r, _) = fx.run(&v, &[]);
    assert!(
        r.code == 2
            && r.stderr
                .contains("cases.diff-run/reports/diff-run-incremental-"),
        "{}",
        r.stderr
    );
    let state = fx.root().join("st");
    std::fs::create_dir_all(state.join("reports")).unwrap();
    std::fs::write(state.join("reports/diff-run-verify-S.json"), "").unwrap();
    std::fs::write(state.join("reports/diff-run-verify-S-2.json"), "").unwrap();
    assert_eq!(
        crate::runner::report_path(&state, "verify", "S"),
        state.join("reports/diff-run-verify-S-3.json")
    );
}

#[test]
fn a_bare_world_compares_everything_under_it() {
    let fx = Fx::new();
    let mut v = Fx::base(&json!([hello("one", None)]));
    v["root"] = json!(".");
    v["world"]["wrap"] = json!(["env"]);
    v["world"].as_object_mut().unwrap().remove("files");
    v["world"].as_object_mut().unwrap().remove("max_text_bytes");
    let (r, _) = fx.run(&v, &[]);
    assert_eq!(r.code, 0, "{}", r.stdout);
    let kept: Value = serde_json::from_str(
        &std::fs::read_to_string(fx.root().join(format!(
            "cases.diff-run/results/{}.old.json",
            crate::runner::case_id("one")
        )))
        .unwrap(),
    )
    .unwrap();
    assert!(kept["result"]["files"]["out/made.txt"]
        .as_str()
        .unwrap()
        .starts_with("made one <stamp> in <WORLD>"));
    // no normalizations and no extras, on a step whose outputs hold no clock: `hello` writes a one-second `date` stamp into the bare
    // world, which with no `stamp` normalization differed whenever the two sides ran either side of a second's turn - 28 of 200
    // runs of this test failed here beside 30 busy loops, none after (feature 449 T164)
    v.as_object_mut().unwrap().remove("normalizations");
    v["world"].as_object_mut().unwrap().remove("extras");
    v["cases"] = json!([{"name": "one", "steps": [["{CMD}", "two"]]}]);
    let (r, _) = fx.run(&v, &[]);
    assert_eq!(r.code, 0, "{}", r.stdout);
    let kept: Value = serde_json::from_str(
        &std::fs::read_to_string(fx.root().join(format!(
            "cases.diff-run/results/{}.new.json",
            crate::runner::case_id("one")
        )))
        .unwrap(),
    )
    .unwrap();
    // the whole world compared, its names unranked with no normalization to rank them
    assert_eq!(kept["result"]["files"]["out/a2/f"].as_str(), Some("two\n"));
    // a separator that can match nothing is passed over
    assert_eq!(
        crate::norm::sorted("b\na", &l7r_shared::regex::build("\n*").unwrap()),
        "a\nb"
    );
    assert_eq!(
        crate::norm::sorted("ba", &l7r_shared::regex::build("x").unwrap()),
        "ba"
    );
}

#[test]
fn a_declared_path_that_cannot_be_read_refuses_the_run() {
    use std::os::unix::fs::PermissionsExt as _;
    let fx = Fx::new();
    std::os::unix::fs::symlink("a.txt", fx.root().join("src/link")).unwrap();
    fx.write("src/sub/c.txt", "c\n");
    fx.write("locked/f", "x");
    fx.write("sealed.txt", "x");
    for p in ["locked/f", "sealed.txt"] {
        std::fs::set_permissions(fx.root().join(p), std::fs::Permissions::from_mode(0o000))
            .unwrap();
    }
    let mut v = Fx::base(&three());
    // a link in a declared directory is hashed by its target's name
    assert_eq!(fx.run(&v, &[]).0.code, 0);
    for input in ["locked", "sealed.txt"] {
        v["world"]["inputs"] = json!([input]);
        let (r, _) = fx.run(&v, &[]);
        assert!(
            r.code == 2 && r.stderr.contains(input) && r.stderr.contains("Permission denied"),
            "{}",
            r.stderr
        );
    }
    for p in ["locked/f", "sealed.txt"] {
        std::fs::set_permissions(fx.root().join(p), std::fs::Permissions::from_mode(0o644))
            .unwrap();
    }
}
