//! The door: each past measurement by its feature and name, a failure the Python's exit 1, and the one writer of their figures.

use serde_json::{json, Value};

use super::{cli, command, record};

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn an_unknown_measurement_is_refused_with_the_list() {
    let dir = crate::checks::scratch("spec-door");
    for asked in [
        &[][..],
        &["238"],
        &["238", "nope"],
        &["999", "inventory-shares"],
    ] {
        let r = cli(&words(asked), &dir, &dir);
        assert_eq!(r.code, 2);
        assert!(r.stderr.starts_with("usage: l7r-gate measure spec 238"));
    }
}

#[test]
fn a_raise_is_exit_one_with_what_it_printed_kept() {
    let dir = crate::checks::scratch("spec-raise");
    l7r_gate_core::record::testkit::put(
        &dir,
        "pool/hamlets/a/a.json",
        r#"{"kosatsuba": [{"x": 0, "y": 0}], "wells": [{"x": 3, "y": 4}], "meta": {}}"#,
    );
    let r = cli(&words(&["261", "board-well", "a", "b"]), &dir, &dir);
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (1, "a recorded None drawn 5.0\n")
    );
    assert!(r
        .stderr
        .starts_with("measure spec 261 board-well: OSError: "));
    let every = [
        ("238", "inventory-shares"),
        ("239", "change-size"),
        ("242", "inventory-census"),
        ("261", "brook-turn"),
        ("261", "fixtures-and-board"),
        ("261", "row-spread"),
        ("430", "full-reasons"),
        ("432", "triage-price"),
    ];
    for (f, n) in every {
        let r = cli(&words(&[f, n]), &dir, &dir);
        assert!(r.code <= 1);
    }
}

#[test]
fn the_figures_are_written_as_the_python_wrote_them() {
    let dir = crate::checks::scratch("spec-record");
    let path = dir.join("m.json");
    record(&path, vec![("b", json!({"z": 1, "a": 1.5}))]).unwrap();
    assert_eq!(
        std::fs::read_to_string(&path).unwrap(),
        "{\n \"b\": {\n  \"a\": 1.5,\n  \"z\": 1\n }\n}\n"
    );
    std::fs::write(&path, "{\"c\": \"\u{fc}\", \"b\": 0}").unwrap();
    record(&path, vec![("b", Value::from(2)), ("a", Value::Null)]).unwrap();
    assert_eq!(
        std::fs::read_to_string(&path).unwrap(),
        "{\n \"a\": null,\n \"b\": 2,\n \"c\": \"\\u00fc\"\n}\n"
    );
    for (text, why) in [("[1]", "TypeError"), ("{", "JSONDecodeError")] {
        std::fs::write(&path, text).unwrap();
        assert!(record(&path, Vec::new()).unwrap_err().starts_with(why));
    }
    std::fs::remove_file(&path).unwrap();
    std::fs::create_dir(&path).unwrap();
    assert!(record(&path, Vec::new())
        .unwrap_err()
        .starts_with("OSError"));
    assert!(record(&dir.join("no/such.json"), Vec::new())
        .unwrap_err()
        .starts_with("OSError"));
    assert_eq!(
        command("238", "inventory-shares", " --record"),
        "scripts/gates/l7r-gate.sh measure spec 238 inventory-shares --record"
    );
}
