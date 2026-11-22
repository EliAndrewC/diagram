//! The runner: started on the first verb, its answers and its failures.

use serde_json::json;

use super::Runner;
use crate::record::bundle::tests::{scratch, RUNNER};
use crate::record::testkit::put;

#[test]
fn a_verb_is_answered_and_a_failure_is_the_traceback() {
    let root = scratch("door");
    let mut door = Runner::new(&root);
    assert_eq!(door.ask("echo", &json!(["a"])).unwrap(), json!(["a"]));
    assert!(door
        .ask("nope", &json!([]))
        .unwrap_err()
        .contains("KeyError"));
    put(
        &root,
        "scripts/bundle_door.py",
        "import sys\nprint('not json', flush=True)\nsys.stdin.read()\n",
    );
    assert!(Runner::new(&root)
        .ask("echo", &json!([]))
        .unwrap_err()
        .contains("bundle-door: echo"));
    put(&root, "scripts/bundle_door.py", "pass\n");
    assert!(Runner::new(&root)
        .ask("echo", &json!([]))
        .unwrap_err()
        .contains("no answer to echo"));
    let missing = crate::checks::scratch("door-missing");
    let _ = RUNNER;
    assert!(Runner::new(&missing).ask("echo", &json!([])).is_err());
}
