//! A fake `/proc` and `/sys` holding every figure the snapshot reads.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    end, failure_marks, general, run, snapshot, start, tenth, Host, FAILED_NAMES_KEPT, FAILURES,
    PHASES_PRE, RESULT, START,
};

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn host(
    root: &Path,
    load: f64,
    avail_kb: i64,
    io_total: i64,
    temp: i64,
    core_ms: &[i64],
    package_ms: i64,
) -> Host {
    let (proc, sys) = (root.join("proc"), root.join("sys"));
    put(
        &proc.join("loadavg"),
        &format!("{load} 1.00 0.50 1/100 42\n"),
    );
    put(
        &proc.join("meminfo"),
        &format!("MemTotal: 16000000 kB\nMemAvailable: {avail_kb} kB\n"),
    );
    put(
        &proc.join("pressure/cpu"),
        "some avg10=0.00 avg60=0.00 avg300=0.00 total=1000000\n",
    );
    put(&proc.join("pressure/io"), &format!("some avg10=0.50 avg60=0.10 avg300=0.02 total={io_total}\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=500000\nnoise\n"));
    put(&proc.join("pressure/memory"), "some avg10=0.00 avg60=0.00 avg300=0.00 total=0\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n");
    for (i, name) in ["nvme", "coretemp"].iter().enumerate() {
        let hw = sys.join(format!("class/hwmon/hwmon{i}"));
        put(&hw.join("name"), &format!("{name}\n"));
        put(
            &hw.join("temp1_input"),
            &format!("{}\n", if *name == "coretemp" { temp } else { 99_000 }),
        );
        if *name == "coretemp" {
            put(&hw.join("temp1_label"), "Package id 0\n");
            put(&hw.join("temp2_input"), "90000\n");
            put(&hw.join("temp2_label"), "Core 0\n");
        }
    }
    for (cpu, ms) in core_ms.iter().enumerate() {
        let tt = sys.join(format!("devices/system/cpu/cpu{cpu}/thermal_throttle"));
        put(&tt.join("core_throttle_total_time_ms"), &format!("{ms}\n"));
        put(
            &tt.join("package_throttle_total_time_ms"),
            &format!("{package_ms}\n"),
        );
    }
    Host { proc, sys }
}

fn scratch(tag: &str) -> PathBuf {
    crate::checks::scratch(&format!("runstats-{tag}"))
}

#[test]
fn the_snapshot_reads_every_figure_and_a_bare_host_gives_none() {
    let root = scratch("snap");
    let snap = snapshot(
        &host(&root, 1.5, 4_194_304, 2_000_000, 61_000, &[10, 20], 7),
        1.0,
    );
    assert_eq!(snap["load"], 1.5);
    assert_eq!(snap["mem_avail_mb"], 4096);
    assert_eq!(
        snap["stall_us"],
        json!({"cpu": 1_000_000, "io": 2_000_000, "io_full": 500_000, "memory": 0})
    );
    assert_eq!(snap["cpu_temp_c"], 61.0);
    assert_eq!(snap["throttle_ms"], json!({"core": 30, "package": 7}));
    let none = scratch("bare");
    let bare = snapshot(
        &Host {
            proc: none.join("p"),
            sys: none.join("s"),
        },
        1.0,
    );
    assert!(
        bare["load"].is_null() && bare["mem_avail_mb"].is_null() && bare["cpu_temp_c"].is_null()
    );
    assert_eq!(
        (bare["stall_us"].clone(), bare["throttle_ms"].clone()),
        (json!({}), json!({}))
    );
}

#[test]
fn coretemp_without_a_package_label_reports_its_hottest_and_with_no_sensor_none() {
    let root = scratch("temp");
    let hw = root.join("sys/class/hwmon/hwmon0");
    put(&hw.join("name"), "coretemp\n");
    put(&hw.join("temp1_input"), "60000\n");
    put(&hw.join("temp2_input"), "72000\n");
    put(&hw.join("temp3_input"), "bad\n");
    put(&hw.join("temp4_input"), "-\n");
    assert_eq!(super::cpu_temp_c(&root.join("sys")), 72.0);
    let none = scratch("nosensor");
    put(&none.join("sys/class/hwmon/hwmon0/name"), "coretemp\n");
    assert!(super::cpu_temp_c(&none.join("sys")).is_null());
}

#[test]
fn end_without_a_start_is_empty_and_end_reports_both_ends_and_the_deltas() {
    let dir = scratch("end");
    let h1 = host(&dir, 1.5, 4_194_304, 2_000_000, 61_000, &[10, 20], 7);
    assert_eq!(end(&dir, &h1), json!({}));
    start(&dir, &h1);
    let h2 = host(&dir, 9.25, 1_048_576, 14_500_000, 88_000, &[100, 430], 1007);
    let out = end(&dir, &h2);
    assert!(out.get("first_failure_s").is_none() && out.get("failed_tests").is_none());
    let got = &out["host"];
    assert_eq!(got["load"], json!([1.5, 9.25]));
    assert_eq!(got["mem_avail_mb"], json!([4096, 1024]));
    assert_eq!(got["cpu_temp_c"], json!([61.0, 88.0]));
    assert_eq!(
        got["stall_s"],
        json!({"cpu": 0.0, "io": 12.5, "io_full": 0.0, "memory": 0.0})
    );
    assert_eq!(got["throttle_ms"], json!({"core": 500, "package": 1000}));
}

#[test]
fn a_figure_missing_at_either_end_is_left_out() {
    let dir = scratch("missing");
    let bare = Host {
        proc: dir.join("no"),
        sys: dir.join("no"),
    };
    start(&dir, &bare);
    assert_eq!(end(&dir, &bare), json!({}));
}

fn marks(dir: &Path, lines: &[&str]) {
    std::fs::write(dir.join(FAILURES), lines.join("\n") + "\n").unwrap();
}

fn started_at(dir: &Path, t: f64) {
    std::fs::write(dir.join(START), json!({"t": t, "load": null, "mem_avail_mb": null, "cpu_temp_c": null, "stall_us": {}, "throttle_ms": {}}).to_string()).unwrap();
}

#[test]
fn test_marks_give_first_and_last_and_the_test_phase_end_is_dropped() {
    let dir = scratch("marks");
    let bare = Host {
        proc: dir.join("no"),
        sys: dir.join("no"),
    };
    started_at(&dir, 100.0);
    marks(
        &dir,
        &[
            "104 test",
            "180 test",
            "200 phase:test-full",
            "garbage line",
        ],
    );
    assert_eq!(
        end(&dir, &bare),
        json!({"first_failure_s": 4.0, "last_failure_s": 80.0, "failed_tests": 2})
    );
    marks(&dir, &["250 phase:test-full"]);
    assert_eq!(
        end(&dir, &bare),
        json!({"first_failure_s": 150.0, "last_failure_s": 150.0})
    );
}

#[test]
fn a_test_id_is_kept_by_name_and_a_coverage_floor_names_its_modules() {
    let dir = scratch("names");
    let bare = Host {
        proc: dir.join("no"),
        sys: dir.join("no"),
    };
    started_at(&dir, 100.0);
    let ids: Vec<String> = (0..25)
        .map(|n| format!("110 test tests/t.py::test_{n}"))
        .collect();
    let mut all: Vec<&str> = ids.iter().map(String::as_str).collect();
    all.push("111 test");
    all.push("120 uncovered l7r/x.py 5-6");
    marks(&dir, &all);
    let out = end(&dir, &bare);
    assert_eq!(out["failed_tests"], 26);
    assert_eq!(
        out["failed_names"].as_array().unwrap().len(),
        FAILED_NAMES_KEPT
    );
    let (.., names) = failure_marks(&dir);
    assert!(names.contains(&"uncovered l7r/x.py 5-6".to_owned()));
}

fn ask(words: &[&str], h: &Host) -> crate::Reply {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    run(&owned, h)
}

#[test]
fn the_commands_run_each_refuse_a_bad_one_and_start_clears_the_last_run() {
    let dir = scratch("cli");
    let d = dir.display().to_string();
    let bare = Host {
        proc: dir.join("no"),
        sys: dir.join("no"),
    };
    std::fs::write(dir.join(FAILURES), "old\n").unwrap();
    assert_eq!(ask(&["phase-pre", &d, "preflight", "7"], &bare).code, 0);
    assert_eq!(ask(&["start", &d], &bare).code, 0);
    assert!(!dir.join(FAILURES).exists() && !dir.join(PHASES_PRE).exists());
    assert_eq!(ask(&["fail", &d, "static"], &bare).code, 0);
    assert!(std::fs::read_to_string(dir.join(FAILURES))
        .unwrap()
        .ends_with(" phase:static\n"));
    assert_eq!(ask(&["phase", &d, "static", "3.5"], &bare).code, 0);
    assert_eq!(ask(&["phase", &d, "static", "1"], &bare).code, 0);
    assert_eq!(ask(&["phase", &d, "static", "x"], &bare).code, 1);
    std::fs::OpenOptions::new()
        .append(true)
        .open(dir.join(super::PHASES))
        .map(|mut f| {
            use std::io::Write as _;
            f.write_all(
                b"bad line
",
            )
            .unwrap();
        })
        .unwrap();
    let got = ask(&["end", &d], &bare);
    let out: Value = serde_json::from_str(&got.stdout).unwrap();
    assert!(out.get("first_failure_s").is_some());
    assert_eq!(out["phases"], json!({"preflight": 7.0, "static": 4.5}));
    assert_eq!(ask(&["fail", &d], &bare).code, 2);
    assert!(ask(&[], &bare).stderr.contains("runstats start"));
}

#[test]
fn this_run_s_plan_is_read_and_a_stale_or_broken_one_is_not() {
    let dir = scratch("plan");
    let bare = Host {
        proc: dir.join("no"),
        sys: dir.join("no"),
    };
    started_at(&dir, 1.0);
    put(
        &dir.join(RESULT),
        &json!({"mode": "full", "reason": "why", "selected": ["a", "b"], "collected": 9})
            .to_string(),
    );
    assert_eq!(
        end(&dir, &bare),
        json!({"plan_mode": "full", "plan_reason": "why", "selected": 2, "collected": 9})
    );
    put(&dir.join(RESULT), &json!({"selected": "x"}).to_string());
    assert_eq!(end(&dir, &bare), json!({}));
    put(&dir.join(RESULT), "not json");
    assert_eq!(end(&dir, &bare), json!({}));
    started_at(&dir, 9_999_999_999.0);
    put(&dir.join(RESULT), &json!({"mode": "full"}).to_string());
    assert_eq!(end(&dir, &bare), json!({}));
    let live = super::cli(&["nonsense".to_owned()]);
    assert_eq!(live.code, 2);
}

#[test]
fn numbers_print_as_python_printed_them() {
    assert_eq!(general(0.0), "0");
    assert_eq!(general(5.0), "5");
    assert_eq!(general(3.5), "3.5");
    assert_eq!(general(123_456.0), "123456");
    assert_eq!(general(1_234_567.0), "1.23457e+06");
    assert_eq!(general(0.00001), "1e-05");
    assert!((tenth(1.25) - 1.2).abs() < 1e-9);
}
