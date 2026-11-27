//! Whether a compile compiled (feature 451 T528): each `build`, `cover-build`, `lint` and `prewarm` line carries `compiled`, the
//! crates cargo's JSON names built afresh, so `make task-time` tells a no-op check from real work by cargo's word and not by its span
//! (`NOOP_BELOW_S`, 451 T522's GUESS knob). A cargo that names no artifact, or exits non-zero, leaves the field out.

use serde_json::Value;

use super::super::phase::{compiled, counted};
use super::super::run::Ran;
use super::phases::phases;
use super::{answer, kept_crates, world_with, World};

/// A fake cargo printing, on a call that asks for JSON, one artifact built afresh and one found fresh, each of another crate - and
/// on a clippy call one more built afresh, so two passes sum to four.
pub(super) const JSON_CARGO: &str = r#"case "$*" in
  *message-format=json*)
    echo '{"reason":"compiler-artifact","package_id":"dep 1.0","fresh":true}'
    echo '{"reason":"compiler-artifact","package_id":"a 0.1","fresh":false}'
    echo '{"reason":"compiler-artifact","package_id":"a 0.1","fresh":false}'
    [ "$1" = clippy ] && echo '{"reason":"compiler-artifact","package_id":"b 0.1","fresh":false}'
    echo '{"reason":"build-finished","success":true}';;
esac
exit 0"#;

#[test]
fn a_builds_json_says_how_many_crates_it_compiled_and_none_where_it_names_no_artifact() {
    let line = |id: &str, fresh: bool| {
        format!(r#"{{"reason":"compiler-artifact","package_id":"{id}","fresh":{fresh}}}"#)
    };
    let text = [
        line("a", false),
        line("a", false),
        line("b", true),
        "plain".to_owned(),
    ]
    .join("\n");
    assert_eq!(compiled(&text), Some(1));
    assert_eq!(compiled(&line("b", true)), Some(0));
    assert_eq!(
        compiled("{\"reason\":\"build-finished\"}\nwarning: x\n"),
        None
    );
    // the answer shown keeps cargo's own words and drops its JSON; a failed build counts nothing
    let ran = |code| Ran {
        code,
        stdout: format!("{}\nnot json\n{{\"other\": 1}}\n", line("a", false)),
        stderr: "error: x\n".to_owned(),
    };
    let (shown, count) = counted(ran(0));
    assert_eq!(
        (shown.stdout.as_str(), count),
        ("not json\n{\"other\": 1}\n", Some(1))
    );
    assert_eq!(shown.stderr, "error: x\n");
    assert_eq!(counted(ran(101)).1, None);
}

/// The `compiled` field of each new line of `step`.
fn counts(root: &std::path::Path, step: &str) -> Vec<Value> {
    phases(root)
        .into_iter()
        .filter(|l| l["step"] == step)
        .map(|l| l["compiled"].clone())
        .collect()
}

#[test]
fn a_test_build_and_a_lint_write_the_crates_cargo_compiled() {
    let (root, ..) = kept_crates();
    let world = world_with(&root, JSON_CARGO);
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    assert_eq!(counts(&root, "build"), [Value::from(1)]);
    // two passes, each compiling two crates
    assert_eq!(
        answer(&world, "lint", &["rust/a".to_owned()], false).code,
        0
    );
    assert_eq!(counts(&root, "lint"), [Value::from(4)]);
    // a fresh run's build, asked apart from its run, is counted too
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    assert_eq!(
        answer(&fresh, "test", &["rust/b".to_owned()], false).code,
        0
    );
    assert_eq!(counts(&root, "build")[1..], [Value::from(1)]);
    // a cargo that says nothing leaves the field out, and so does a failed pass
    let quiet = world_with(&root, "exit 0");
    assert_eq!(
        answer(&quiet, "lint", &["rust/b".to_owned()], false).code,
        0
    );
    // its source moved, so the kept green result does not stand
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! moved\n").unwrap();
    let red = world_with(&root, "[ \"$1\" = clippy ] && exit 101\nexit 0");
    assert_eq!(answer(&red, "lint", &["rust/a".to_owned()], false).code, 1);
    assert_eq!(counts(&root, "lint")[1..], [Value::Null, Value::Null]);
}
