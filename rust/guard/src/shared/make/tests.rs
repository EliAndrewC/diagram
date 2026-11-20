use super::{combine, invoked, targets};

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

/// Feature 451 T15 (T30 folded in): `setsid` is a word that runs the command after it, a `bash -lc` string is run, a goal-less make
/// runs the default goal - and a `grep -c` pattern or a heredoc with words after its delimiter is a mention.
#[test]
fn setsid_bash_lc_and_a_goal_less_make_are_invocations() {
    assert_eq!(invoked("setsid make static"), ["static"]);
    assert_eq!(invoked("setsid --fork make -s done"), ["done"]);
    assert_eq!(invoked("bash -lc \"make x\""), ["x"]);
    assert_eq!(invoked("make"), [".DEFAULT_GOAL"]);
    assert_eq!(invoked("make -j4 > log 2>&1 &"), [".DEFAULT_GOAL"]);
    assert_eq!(
        invoked("cd x && make; make done"),
        [".DEFAULT_GOAL", "done"]
    );
    assert!(invoked("grep -c \"make static\" log").is_empty());
    assert!(invoked("cat <<'EOF' > n.md\nmake static\nEOF").is_empty());
    assert!(invoked("echo make").is_empty());
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
    // feature 451 T02: a backgrounded quick is left alone, a redirect's `&` is not a background
    assert_eq!(combine("make quick & make done"), None);
    assert_eq!(
        combine("make quick 2>&1 && make done").as_deref(),
        Some("make done")
    );
}

/// Feature 451 T02's cases (plan, T02 Approach; research R1): the command, and the targets it runs in command order.
const T02_CASES: [(&str, &[&str]); 26] = [
    ("timeout 2400 make static", &["static"]),
    ("timeout -k 5 1800 make rust-test", &["rust-test"]),
    ("flock /tmp/x make rust-test", &["rust-test"]),
    ("flock -w 10 /tmp/x make rust-test", &["rust-test"]),
    ("(make hooks-test > log) &", &["hooks-test"]),
    ("{ make static; } &", &["static"]),
    ("VAR=x make static &", &["static"]),
    ("env X=1 make static &", &["static"]),
    ("nice -n 5 make static", &["static"]),
    ("time make static", &["static"]),
    ("if true; then make static; fi", &["static"]),
    ("sleep 1 & make static", &["static"]),
    ("cd x && make quick; make done", &["quick", "done"]),
    ("make -j 4 done", &["done"]),
    (
        "scripts/gates/l7r-gate.sh rust test --crate rust/guard",
        &["rust-test"],
    ),
    ("make quick done", &["quick", "done"]),
    ("make -j done", &["done"]),
    ("make -C dir -I inc FULL=1 ./x land T=T02 2>&1", &["land"]),
    ("make static; make static", &["static", "static"]),
    ("bash -c \"cd x && make static\"", &["static"]),
    (
        "\"$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" rust test",
        &["rust-test"],
    ),
    ("$(MAKE) done", &["done"]),
    ("make 9lives", &[]),
    ("echo make static", &[]),
    ("cat <<EOF\nmake static\nEOF", &[]),
    ("grep -n 'make static' Makefile", &[]),
];

/// Each case through the one detector (`invoked`), its set (`targets`) and the event log's first (`make_target`).
#[test]
fn t02_every_form_yields_its_targets_through_every_reader() {
    use crate::guards::event_log_hooks::make_target;
    for (cmd, want) in T02_CASES {
        assert_eq!(invoked(cmd), want, "{cmd}");
        assert_eq!(targets(cmd), set(want), "{cmd}");
        let first = want.first().copied().unwrap_or("");
        assert_eq!(make_target(cmd), first, "{cmd}");
    }
}
