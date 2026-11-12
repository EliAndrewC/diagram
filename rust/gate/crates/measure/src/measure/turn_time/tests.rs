//! The turns of a scratch transcript, the fit and the command line.

use serde_json::{json, Value};

use super::*;

fn at(s: u32) -> String {
    format!("2026-11-01T08:{:02}:{:02}Z", s / 60, s % 60)
}

fn result(s: u32) -> Value {
    json!({"type": "user", "timestamp": at(s), "message": {"content": [{"type": "tool_result"}]}})
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a test row built from literals"
)]
fn reply_at(s: u32, rid: &str, ctx: Value, out: Value) -> Value {
    json!({"type": "assistant", "timestamp": at(s), "requestId": rid,
           "message": {"usage": {"input_tokens": ctx, "output_tokens": out}}})
}

#[test]
fn the_readers_fail_where_the_python_raised() {
    assert!(ts_of(&json!(1)).is_err());
    assert!(ts_of(&json!(at(1))).is_ok());
    assert!(or_map(Some(&json!("x"))).is_err());
    assert!(or_map(Some(&json!(""))).unwrap().is_none());
    assert!(or_map(None).unwrap().is_none());
    for (v, want) in [
        (json!(true), 1),
        (json!(7), 7),
        (json!(u64::MAX), i128::from(u64::MAX)),
        (json!(2.9), 2),
        (json!("12"), 12),
        (json!(0), 0),
    ] {
        assert_eq!(py_int_or_zero(Some(&v)).unwrap(), want);
    }
    assert!(py_int_or_zero(Some(&json!("x"))).is_err());
    assert!(py_int_or_zero(Some(&json!([1]))).is_err());
    assert_eq!(py_int_or_zero(None).unwrap(), 0);
}

#[test]
fn a_turn_is_a_reply_after_a_tool_result() {
    let lines = vec![
        json!({"timestamp": at(0), "isSidechain": true}),
        json!({"type": "user"}),
        result(0),
        reply_at(4, "r1", json!(1000), json!(10)),
        reply_at(5, "r1", json!(1000), json!(10)),
        json!({"type": "user", "timestamp": at(6), "message": {"content": "text"}}),
        reply_at(7, "r2", json!(1000), json!(10)),
        result(10),
        reply_at(10, "r3", json!(1000), json!(1)),
        result(20),
        json!({"type": "assistant", "timestamp": at(30), "message": {"id": "m4"}}),
        result(40),
        reply_at(48, "r5", json!(300_000), json!(2000)),
        result(50),
        reply_at(52, "r5", json!(300_000), json!(2000)),
    ];
    let got = turns(&lines).unwrap();
    assert_eq!(got, vec![(1000, 4.0, 10), (300_000, 8.0, 2000)]);
    assert!(turns(&[json!([1])]).is_err());
    assert!(turns(&[json!({"timestamp": at(1), "message": "x"})]).is_err());
    assert!(turns(&[
        result(1),
        json!({"type": "assistant", "timestamp": at(2), "message": {"usage": 3}})
    ])
    .is_err());
}

#[test]
fn the_fit_and_the_summary() {
    let points = vec![
        (100_000, 2.0, 1000),
        (300_000, 4.0, 2000),
        (500_000, 7.0, 1000),
        (900_000, 9.0, 3000),
    ];
    let [a, b, c] = fit(&points);
    assert!(a.is_finite() && b > 0.0 && c.is_finite());
    // all alike: the normal equations are singular, a coefficient with no pivot reads 0
    assert!(fit(&[(100_000, 2.0, 0), (100_000, 2.0, 0)])[2].abs() < f64::EPSILON);
    assert!((py_round(2.675, 2) - 2.67).abs() < 1e-12);
    assert!((median(vec![3.0, 1.0, 2.0]) - 2.0).abs() < f64::EPSILON);
    assert!((median(vec![4.0, 1.0]) - 2.5).abs() < f64::EPSILON);
    let s = summary(&points);
    assert_eq!(s["turns"], 4);
    assert_eq!(
        s["median turn s by context (200k bands)"]
            .as_object()
            .unwrap()
            .keys()
            .collect::<Vec<_>>(),
        ["0-200k", "200-400k", "400-600k", "800-1000k"]
    );
}

#[test]
fn the_command_line_prints_and_records() {
    let dir = crate::checks::scratch("turn-time");
    let ask = |words: &[&str]| cli(&words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>());
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(ask(&["--bogus"]).code, 2);
    let t = dir.join("t.jsonl");
    assert_eq!(ask(&[t.to_str().unwrap()]).code, 1);
    std::fs::write(&t, "not json\n{\"type\": \"user\"}\n").unwrap();
    let none = ask(&[t.to_str().unwrap()]);
    assert_eq!(
        (none.code, none.stderr.as_str()),
        (2, "turn_time: no turns found\n")
    );
    let body: String = [result(0), reply_at(3, "a", json!(5), json!(1))]
        .iter()
        .map(|v| v.to_string() + "\n")
        .collect();
    std::fs::write(&t, body).unwrap();
    let ts = t.to_str().unwrap();
    let ok = ask(&[ts]);
    assert_eq!(ok.code, 0);
    assert!(ok.stdout.starts_with("{\n \"turns\": 1,\n"));
    let rec = dir.join("m.json");
    let rs = rec.to_str().unwrap();
    assert_eq!(
        ask(&[ts, "--record", rs]).stderr,
        "turn_time: --record needs --key\n"
    );
    assert_eq!(ask(&[ts, "--record", rs, "--key", "k"]).code, 1);
    std::fs::write(&rec, "{\"k\": {\"quantity\": \"é\"}}").unwrap();
    assert_eq!(ask(&[ts, "--record", rs, "--key", "k"]).code, 0);
    let written = std::fs::read_to_string(&rec).unwrap();
    assert!(
        written.starts_with("{\n \"k\": {\n  \"quantity\": \"é\",\n  \"value\": {")
            && written.ends_with("}\n")
    );
    for bad in ["[]", "{\"k\": []}", "nope"] {
        std::fs::write(&rec, bad).unwrap();
        assert_eq!(ask(&[ts, "--record", rs, "--key", "k"]).code, 1);
    }
    std::fs::write(&rec, "{}").unwrap();
    let mut perms = std::fs::metadata(&rec).unwrap().permissions();
    perms.set_readonly(true);
    std::fs::set_permissions(&rec, perms).unwrap();
    assert_eq!(ask(&[ts, "--record", rs, "--key", "k"]).code, 1);
}
