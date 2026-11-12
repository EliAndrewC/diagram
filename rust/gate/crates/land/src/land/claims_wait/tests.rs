//! The claims wait: what waiting cannot cure, the carries filed while it waits, the gate's own lint committed, the wait's bound.

use l7r_gate_core::ci::fixtures::{git, put};

use super::super::tests::{fx, tool};
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
    let fx = fx("wait-out");
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
    // a passing gate over a dirty tree waits on the tree
    std::fs::remove_file(
        fx.stub
            .join(format!("{}.rc", super::super::tests::key(&gate))),
    )
    .unwrap();
    put(&fx.root, "loose.txt", "x");
    let why = fx.land.wait_for_claims(&ticks(), None).unwrap();
    assert_eq!(why, "uncommitted changes: ?? loose.txt");
}

#[test]
fn the_gate_s_own_lint_is_committed_and_nothing_else() {
    let fx = fx("wait-lint");
    put(&fx.root, "scripts/a.py", "import b\nimport a\n");
    put(&fx.root, "scripts/b.py", "x = 1\n");
    put(&fx.root, "scripts/c.py", "y = 1\n");
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "py"]);
    // the gate's ruff sorted a.py's imports; b.py was edited by hand; c.py cannot be read
    put(&fx.root, "scripts/a.py", "import a\nimport b\n");
    put(&fx.root, "scripts/b.py", "x = 2\n");
    put(&fx.root, "scripts/c.py", "y = 2\n");
    let check = "ruff check --fix --quiet --stdin-filename scripts/a.py -";
    fx.answer(check, "out", "import a\nimport b\n");
    let format_b = "ruff format --quiet --stdin-filename scripts/b.py -";
    fx.answer(format_b, "rc", "2");
    std::process::Command::new("chmod")
        .args(["000"])
        .arg(fx.root.join("scripts/c.py"))
        .status()
        .unwrap();
    let mine = fx.land.commit_gate_formatting().unwrap();
    std::process::Command::new("chmod")
        .args(["644"])
        .arg(fx.root.join("scripts/c.py"))
        .status()
        .unwrap();
    assert_eq!(mine, vec!["scripts/a.py"]);
    assert!(fx
        .subjects()
        .contains("the gate's own lint and format, committed"));
    // ruff that says nothing is no answer
    fx.answer(
        "ruff check --fix --quiet --stdin-filename scripts/b.py -",
        "out",
        "",
    );
    fx.answer(
        "ruff check --fix --quiet --stdin-filename scripts/b.py -",
        "rc",
        "0",
    );
    assert_eq!(fx.land.ruffed("scripts/b.py", "x = 1\n"), Ok(None));
    let mut gone = fx;
    gone.land.python = "/no/such/python".to_owned();
    assert!(gone.land.ruffed("scripts/b.py", "x").is_err());
}
