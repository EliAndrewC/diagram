use std::ffi::OsString;
use std::os::unix::ffi::OsStringExt as _;

use l7r_shared::tempdir::TempDir;
use serde_json::Value;

use super::cli;

fn args(a: &[&str]) -> Vec<OsString> {
    a.iter().map(OsString::from).collect()
}

/// The one entry `dir` holds, parsed, and its raw text.
fn only(dir: &std::path::Path) -> (Value, String) {
    let files: Vec<_> = std::fs::read_dir(dir)
        .unwrap()
        .filter_map(Result::ok)
        .collect();
    assert_eq!(files.len(), 1, "one entry, no temporary left");
    let text = std::fs::read_to_string(files[0].path()).unwrap();
    for f in files {
        std::fs::remove_file(f.path()).unwrap();
    }
    // an entry holding Python's lone surrogate is not JSON serde reads, as it was not before: its text is the test there
    (serde_json::from_str(&text).unwrap_or(Value::Null), text)
}

#[test]
fn an_entry_takes_the_shells_arguments_and_the_input_on_stdin() {
    let d = TempDir::new("core-guard-log");
    let input = br#"{"cwd": "/c", "tool_name": "Bash", "tool_input": {"command": "ls"}}"#;
    let r = cli(
        &args(&["claims-gate", "escaped", "a reason", "S", "claims-ok", ""]),
        &mut &input[..],
        &d,
    );
    assert_eq!((r.code, r.stdout.as_str(), r.stderr.as_str()), (0, "", ""));
    let (v, _) = only(&d);
    assert_eq!(
        (
            v["guard"].as_str(),
            v["rule"].as_str(),
            v["session"].as_str(),
            v["session_name"].as_str(),
            v["command"].as_str(),
            v["context"].clone()
        ),
        (
            Some("claims-gate"),
            Some("claims-ok"),
            Some("S"),
            Some("S"),
            Some("ls"),
            Value::Null
        )
    );
    // no rule and no context: the event is the rule; a context that is JSON is its value, else its text
    cli(
        &args(&["g", "blocked", "d", "unknown"]),
        &mut &b"not json"[..],
        &d,
    );
    let (v, _) = only(&d);
    assert_eq!(
        (v["rule"].as_str(), v["session"].as_str()),
        (Some("blocked"), Some("unknown"))
    );
    cli(
        &args(&["g", "e", "d", "unknown", "r", "{\"k\": 1}"]),
        &mut &b""[..],
        &d,
    );
    assert_eq!(only(&d).0["context"]["k"], 1);
    cli(
        &args(&["g", "e", "d", "unknown", "r", "not json"]),
        &mut &b""[..],
        &d,
    );
    assert_eq!(only(&d).0["context"], "not json");
}

#[test]
fn a_byte_that_is_not_utf8_is_pythons_surrogate_and_a_bad_call_is_refused() {
    let d = TempDir::new("core-guard-log-bytes");
    let mut a = args(&["g", "blocked"]);
    a.push(OsString::from_vec(b"cut \xe2\x82".to_vec()));
    a.push(OsString::from("unknown"));
    assert_eq!(cli(&a, &mut &b"{}"[..], &d).code, 0);
    let (_, text) = only(&d);
    assert!(
        text.contains("\"detail\": \"cut \\udce2\\udc82\""),
        // {text}
    );
    assert_eq!(cli(&args(&["g", "e", "d"]), &mut &b""[..], &d).code, 2);
    let r = cli(
        &args(&["g", "e", "d", "s", "r", "c", "extra"]),
        &mut &b""[..],
        &d,
    );
    assert_eq!(
        (r.code, r.stderr.starts_with("usage: l7r-gate log guard")),
        (2, true)
    );
    // input that is not UTF-8: no payload fields, the name still read from it (here none resolves: the id names it), and bytes that
    // parse as nothing at all
    let raw = b"{\"session_id\": \"t143-nobody\", \"cwd\": \"\xff\"}";
    assert_eq!(cli(&args(&["g", "e", "d", "S"]), &mut &raw[..], &d).code, 0);
    let (v, _) = only(&d);
    assert_eq!(
        (v["session"].as_str(), v["cwd"].as_str()),
        (Some("S"), Some(""))
    );
    assert_eq!(
        cli(&args(&["g", "e", "d", "S"]), &mut &b"\xff"[..], &d).code,
        0
    );
    assert_eq!(only(&d).0["session_name"], "S");
    // the numbers serde_json cannot hold, written as Python wrote them: digits kept, NaN, a context's too
    let big = br#"{"session_id": "s", "cwd": 123456789012345678901234567890, "tool_name": NaN}"#;
    assert_eq!(
        cli(
            &args(&["g", "e", "d", "S", "r", "[NaN, 1e400]"]),
            &mut &big[..],
            &d
        )
        .code,
        0
    );
    let (_, text) = only(&d);
    assert!(text.contains("\"cwd\": 123456789012345678901234567890,\n  \"tool\": NaN,"));
    assert!(text.contains("\"context\": [\n    NaN,\n    Infinity\n  ]"));
    // a directory that cannot be made: nothing written, exit 1, as the Python's raise
    std::fs::write(d.join("a-file"), "").unwrap();
    assert_eq!(
        cli(
            &args(&["g", "e", "d", "s"]),
            &mut &b""[..],
            &d.join("a-file")
        )
        .code,
        1
    );
}
