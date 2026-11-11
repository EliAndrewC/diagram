//! The runner: started on the first verb, its answers and its failures.

use serde_json::json;

use super::Runner;
use crate::record::bundle::tests::{scratch, RUNNER};
use crate::record::testkit::put;

#[test]
fn a_verb_is_answered_and_a_failure_is_the_traceback() {
    let root = scratch("door");
    let mut door = Runner::new(&root);
    assert_eq!(
        door.ask("knobs", &json!([])).unwrap(),
        json!({"winter_crop": ["none", "wheat"]})
    );
    assert!(door
        .ask("nope", &json!([]))
        .unwrap_err()
        .contains("KeyError"));
    assert_eq!(
        door.helper(
            "record_prepass",
            &["q".to_owned(), "--fail".to_owned()],
            &root
        )
        .unwrap(),
        (4, "record_prepass ran q --fail\n".to_owned())
    );
    assert!(door
        .helper("record_prepass", &["--boom".to_owned()], &root)
        .unwrap_err()
        .contains("boom"));
    put(
        &root,
        "scripts/bundle_door.py",
        "import sys\nprint('not json', flush=True)\nsys.stdin.read()\n",
    );
    assert!(Runner::new(&root)
        .ask("knobs", &json!([]))
        .unwrap_err()
        .contains("bundle-door: knobs"));
    put(
        &root,
        "scripts/bundle_door.py",
        "import json\nprint(json.dumps({'ok': ['x']}), flush=True)\n",
    );
    assert_eq!(
        Runner::new(&root)
            .helper("record_prepass", &[], &root)
            .unwrap(),
        (1, String::new())
    );
    put(&root, "scripts/bundle_door.py", "pass\n");
    assert!(Runner::new(&root)
        .ask("knobs", &json!([]))
        .unwrap_err()
        .contains("no answer to knobs"));
    put(
        &root,
        "scripts/bundle_door.py",
        "import json\nprint(json.dumps({'ok': [9999999999999, 'x']}), flush=True)\n",
    );
    assert_eq!(
        Runner::new(&root)
            .helper("record_prepass", &[], &root)
            .unwrap()
            .0,
        1
    );
    let missing = crate::checks::scratch("door-missing");
    let _ = RUNNER;
    assert!(Runner::new(&missing).ask("knobs", &json!([])).is_err());
}
