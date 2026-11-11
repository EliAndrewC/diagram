//! The queue's answers merged as the shell's jq merged them.

use serde_json::{json, Value};

use super::cli;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_queue_store_merges_into_the_clone() {
    let base = crate::checks::scratch("merge-answers");
    let (q, m) = (
        base.join("q/.git/record-checks"),
        base.join("m/.git/record-checks"),
    );
    std::fs::create_dir_all(&q).unwrap();
    let write =
        |dir: &std::path::Path, name: &str, v: &str| std::fs::write(dir.join(name), v).unwrap();
    write(&q, "new.json", "{\"unit\": \"a\"}");
    write(&q, "newer.json", "{\"answered\": [\"q\", 1, null, true, false, [1], {\"a\": 1}, 2.5], \"utc\": \"2\", \"fingerprint\": \"Q\"}");
    write(&q, "older.json", "{\"answered\": null, \"utc\": \"0\"}");
    write(&q, "numbers.json", "{\"utc\": 5}");
    write(&q, "bad.json", "{\"answered\": \"x\"}");
    write(&q, "kinds.json", "{\"utc\": \"1\"}");
    write(&q, "broken.json", "{}");
    write(&q, "notes.txt", "ignored");
    let r = cli(&args(&[
        &base.join("q").to_string_lossy(),
        &base.join("m").to_string_lossy(),
    ]));
    assert_eq!(r.code, 0);
    std::fs::create_dir_all(&m).unwrap();
    write(
        &m,
        "newer.json",
        "{\"unit\": \"n\", \"answered\": [\"m\", \"q\"], \"utc\": \"1\", \"result\": \"r\"}",
    );
    write(
        &m,
        "older.json",
        "{\"unit\": \"o\", \"answered\": false, \"utc\": \"5\"}",
    );
    write(&m, "numbers.json", "{\"utc\": 3}");
    write(&m, "bad.json", "{\"answered\": [\"y\"]}");
    write(&m, "kinds.json", "{\"utc\": 3}");
    write(&m, "broken.json", "{not json");
    let r = cli(&args(&[
        &base.join("q").to_string_lossy(),
        &base.join("m").to_string_lossy(),
    ]));
    assert_eq!(r.code, 0);
    let read = |n: &str| {
        serde_json::from_str::<Value>(&std::fs::read_to_string(m.join(n)).unwrap()).unwrap()
    };
    assert_eq!(
        read("newer.json"),
        json!({"unit": "n", "answered": [null, false, true, 1, 2.5, "m", "q", [1], {"a": 1}], "utc": "2", "result": null, "fingerprint": "Q"})
    );
    assert_eq!(
        read("older.json"),
        json!({"unit": "o", "answered": [], "utc": "5"})
    );
    assert_eq!(read("numbers.json")["utc"], 5);
    assert_eq!(read("kinds.json")["utc"], "1");
    assert_eq!(read("new.json"), json!({"unit": "a", "answered": []}));
    assert_eq!(std::fs::read_to_string(m.join("bad.json.tmp")).unwrap(), "");
    assert_eq!(
        std::fs::read_to_string(m.join("broken.json.tmp")).unwrap(),
        ""
    );
    assert!(std::fs::read_to_string(m.join("newer.json"))
        .unwrap()
        .starts_with("{\n  \"unit\""));
}

#[test]
fn nothing_to_merge_and_a_bad_command_line() {
    assert_eq!(cli(&args(&["/nonexistent/q", "/nonexistent/m"])).code, 0);
    assert_eq!(cli(&[]).code, 2);
    let base = crate::checks::scratch("merge-answers-fail");
    std::fs::create_dir_all(base.join("q/.git/record-checks")).unwrap();
    std::fs::write(base.join("q/.git/record-checks/a.json"), "{}").unwrap();
    std::fs::write(base.join("m"), "a file where the clone should be").unwrap();
    assert_eq!(
        cli(&args(&[
            &base.join("q").to_string_lossy(),
            &base.join("m").to_string_lossy()
        ]))
        .code,
        1
    );
    let ro = crate::checks::scratch("merge-answers-ro");
    std::fs::create_dir_all(ro.join("q/.git/record-checks")).unwrap();
    std::fs::write(ro.join("q/.git/record-checks/a.json"), "{}").unwrap();
    std::fs::create_dir_all(ro.join("m/.git/record-checks/a.json")).unwrap();
    let r = cli(&args(&[
        &ro.join("q").to_string_lossy(),
        &ro.join("m").to_string_lossy(),
    ]));
    assert_eq!(r.code, 1);
}
