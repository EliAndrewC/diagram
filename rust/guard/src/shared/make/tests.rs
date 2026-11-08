use super::{bare_pytest, combine, targets};

fn set(items: &[&str]) -> std::collections::BTreeSet<String> {
    items.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_target_is_invoked_at_a_command_position_never_mentioned() {
    assert_eq!(targets("make done"), set(&["done"]));
    assert_eq!(
        targets("cd x && make -s FULL=1 test-file FILE=a"),
        set(&["test-file"])
    );
    assert_eq!(
        targets("timeout 60 make quick; $(MAKE) done"),
        set(&["done", "quick"])
    );
    assert_eq!(targets("echo 'make done'"), set(&[]));
    assert_eq!(targets("cat <<EOF\nmake done\nEOF"), set(&[]));
    assert_eq!(targets("grep make done"), set(&[]));
}

#[test]
fn quick_and_done_together_become_done_alone() {
    assert_eq!(
        combine("make quick && make done").as_deref(),
        Some("make done")
    );
    assert_eq!(combine("make quick done").as_deref(), Some("make done"));
    assert_eq!(
        combine("make quick done; echo ok").as_deref(),
        Some("make done; echo ok")
    );
    assert_eq!(combine("make done"), None);
    assert_eq!(combine("make quick"), None);
    assert_eq!(combine(""), None);
    assert_eq!(
        combine("make quick && make done  # GATE_OK: both on purpose"),
        None
    );
    assert_eq!(combine("make quick && cat <<EOF\nx\nEOF\nmake done"), None);
    assert_eq!(
        combine("make -C done quick && make done"),
        Some("make done".to_owned())
    );
    assert_eq!(combine("make -C quick done"), None);
    assert_eq!(combine("(make quick && make done"), None);
    assert_eq!(combine("make quick-run quick done"), None);
    assert_eq!(combine("timeout 5 make quick && make done"), None);
}

#[test]
fn a_bare_pytest_is_one_no_earlier_verdict_claims() {
    assert!(bare_pytest("pytest tests/x.py -k a"));
    assert!(bare_pytest("python3 -m pytest -q"));
    assert!(!bare_pytest(""));
    assert!(!bare_pytest("make test-file FILE=x"));
    assert!(!bare_pytest(
        "pytest x  # GUARD_EDIT_OK: the guard's own suite"
    ));
    assert!(!bare_pytest("make -f other.mk test && pytest"));
    assert!(!bare_pytest("python3 -m l7r.diagram.x && pytest"));
    assert!(!bare_pytest(
        "python3 l7r/diagram/pipeline/regen.py; pytest"
    ));
    assert!(!bare_pytest("grep 'pytest' x"));
}
