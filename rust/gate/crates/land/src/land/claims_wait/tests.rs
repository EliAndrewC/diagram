//! The claims wait: what waiting cannot cure, the carries filed while it waits, the gate's own lint committed, the wait's bound.

use l7r_gate_core::ci::fixtures::put;

use super::super::tests::{fx, tool, Stepped};
use super::{claims_cure, claims_route, claims_stop_line};

fn ticks() -> Vec<String> {
    vec!["T1".to_owned()]
}

#[test]
fn what_waiting_cannot_cure_is_said_with_its_cure() {
    let flight = vec!["b".to_owned()];
    assert!(claims_cure("introduced: x\nowed (impl-drift) y\n", &flight)
        .starts_with("claims-gate.sh refuses on a finding no check in flight can cure - introduced: x (also owed: owed (impl-drift) y)."));
    assert!(!claims_cure("introduced: x\n", &[]).contains("also owed"));
    assert!(
        claims_cure("owed (impl-drift) y\npre-existing owed (z)\n", &[]).starts_with(
            "claims-gate.sh: a claim is owed a check and none is in flight - owed (impl-drift) y."
        )
    );
    assert_eq!(claims_cure("owed (impl-drift) y\n", &flight), "");
    assert_eq!(claims_cure("carry: x\n", &[]), "");
    // a claim on a deleted unit no port carried waits for nothing (feature 449 T166)
    let unported = claims_cure(
        "unported: k - its unit is deleted\nowed (new): y\n",
        &flight,
    );
    assert!(unported.starts_with("claims-gate.sh refuses on a claim whose unit was deleted unported - unported: k - its unit is deleted. Each line names its fix"));
    assert!(claims_stop_line(&unported).contains("waiting cannot cure it"));
    assert_eq!(
        claims_route("carry: x", "said", &[]),
        (true, "said".to_owned())
    );
    assert!(!claims_route("introduced: x", "said", &[]).0);
    assert!(claims_stop_line(&claims_cure("introduced: x", &[])).contains("waiting cannot cure it"));
    assert!(claims_stop_line("claims-gate.sh: x").contains("did not finish in 20 min"));
}

#[test]
fn the_wait_ends_when_the_gate_passes_on_a_clean_tree() {
    let fx = fx("wait-pass");
    assert_eq!(fx.land.wait_for_claims(&ticks(), None), Ok(String::new()));
}

#[test]
fn a_carry_met_while_waiting_is_filed_and_the_gate_asked_again() {
    let fx = fx("wait-carry");
    let gate = tool("gates/claims-gate.sh");
    fx.answer(&gate, "rcs", "1\n0\n");
    fx.answer(&gate, "sh", "[ -s \"$STUB_DIR/$key.rcs\" ] && [ \"$(head -n1 \"$STUB_DIR/$key.rcs\")\" = 1 ] && echo 'carry: a page moved'\n");
    let d = fx.root.join("specs/449-x");
    assert_eq!(
        fx.land.wait_for_claims(&ticks(), Some(&d)),
        Ok(String::new())
    );
    let asked = fx.answers.asked.borrow().join("\n");
    assert!(asked.contains("claims carry") && asked.contains("claims known"));
}

#[test]
fn a_refusal_no_wait_can_cure_ends_the_wait_at_once() {
    let fx = fx("wait-cure");
    let gate = tool("gates/claims-gate.sh");
    fx.answer(&gate, "rc", "1");
    fx.answer(&gate, "out", "introduced: a finding\n");
    let why = fx
        .land
        .wait_for_claims(&ticks(), Some(&fx.root.join("specs/449-x")))
        .unwrap();
    assert!(why.starts_with("claims-gate.sh refuses on a finding"));
}

#[test]
fn the_wait_runs_out_naming_what_still_stands() {
    let mut fx = fx("wait-out");
    // a clock that moves only when the wait sleeps (feature 449 T160): the wait runs out after its rounds, never by a busy host's time
    fx.land.clock = std::rc::Rc::new(Stepped(std::cell::Cell::new(std::time::Instant::now())));
    fx.land.claims_poll = fx.land.claims_wait / 2;
    let gate = tool("gates/claims-gate.sh");
    fx.answer(&gate, "rc", "1");
    fx.answer(&gate, "out", "owed (impl-drift) k\n");
    fx.answers.flight.borrow_mut().push("b".to_owned());
    let why = fx.land.wait_for_claims(&ticks(), None).unwrap();
    assert_eq!(why, "claims-gate.sh: owed (impl-drift) k");
    assert!(fx
        .said()
        .0
        .contains("land: waiting for the claims round before the push - claims-gate.sh: owed"));
}

/// The wait running out on a dirty tree, apart from the refusing gate above (feature 449 T167: the two waits in one test ran over
/// FR-008's tenth of a second); the fixture's clock moves only when the wait sleeps.
#[test]
fn a_passing_gate_over_a_dirty_tree_waits_on_the_tree() {
    let fx = fx("wait-dirty");
    // a passing gate over a dirty tree waits on the tree
    put(&fx.root, "loose.txt", "x");
    let why = fx.land.wait_for_claims(&ticks(), None).unwrap();
    assert_eq!(why, "uncommitted changes: ?? loose.txt");
}
