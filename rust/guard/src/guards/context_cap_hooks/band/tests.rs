//! The band's verdict on each kind of call (451 T417): each stop-point step let through, each other kind refused.

use serde_json::json;

use serde_json::Value;

use super::{At, Band, MAKE};

/// The handoff the cap's exit allows in these tests: outside /tmp, so a redirect to it passes as the handoff alone.
const HANDOFF: &str = "/c/.git/l7r-handoffs/T1-build.md";

fn judge(tool: &str, ti: &Value) -> Band {
    let at = At {
        cwd: Some("/t"),
        home: "/home/b",
        handoff: &|p: &str| p == HANDOFF,
    };
    super::judge(tool, ti, &at)
}

fn bash(cmd: &str) -> Band {
    judge("Bash", &json!({"command": cmd}))
}

#[test]
fn a_redirect_lands_only_under_tmp_or_in_the_handoff() {
    for cmd in [
        "make decide F=451 T=T1 > /tmp/t1-decide.log 2>&1",
        "make builder-checks >/dev/null 2>&1; tail -3 /tmp/claude-1000/-diagram/s/scratchpad/t1.log",
        "grep -n x /t/a.rs > /tmp/claude-1000/-diagram/s/scratchpad/t1-hits.txt",
        "make plan-delta F=451 2>/dev/null | tail -5",
        &format!("grep -c x /t/a.rs >> {HANDOFF}"),
        // a quoted `>` is no redirect
        "grep 'a > b.rs' /t/f",
        "make decide > \"/tmp/t1 decide.log\" 2>&1",
        "D=/tmp/x; grep x a > \"$D/h.txt\"",
        "make task-add F=451 TITLE=\"x -> y.rs, found by T1\"",
    ] {
        assert!(allowed(&bash(cmd)), "{cmd}");
    }
    let why = "(in the band a redirect lands only under /tmp or in the handoff)";
    for (cmd, place) in [
        (
            "tail -n 0 x > /t/rust/guard/src/a.rs",
            "/t/rust/guard/src/a.rs",
        ),
        ("grep '' a > b.rs", "/t/b.rs"),
        ("cd /t && make decide > rust/x.rs", "/t/rust/x.rs"),
        ("head -1 a >> /tmp/../diagram/x.rs", "/diagram/x.rs"),
        (
            "grep -c x a > /c/.git/l7r-handoffs/T2-other.md",
            "/c/.git/l7r-handoffs/T2-other.md",
        ),
        // a name no one assigns is empty, as bash reads it
        ("grep x a > $NOWHERE/b.rs", "/b.rs"),
        (
            "grep x a > $(head -1 p)/b.rs",
            "a place the guard cannot resolve",
        ),
    ] {
        let (got, want) = (bash(cmd), no(&format!("a redirect writing {place} {why}")));
        assert_eq!(got, want, "{cmd}");
    }
}

fn allowed(b: &Band) -> bool {
    matches!(b, Band::Allowed(_))
}

fn no(what: &str) -> Band {
    Band::Refused(what.to_owned())
}

#[test]
fn each_stop_point_step_is_let_through() {
    for goal in MAKE {
        let cmd = format!("cd /t && export SPECIFY_FEATURE=451-x SPECIFY_FEATURE_DIRECTORY=specs/451-x && make {goal} F=451 T=T1");
        assert!(allowed(&bash(&cmd)), "{goal}");
    }
    for cmd in [
        "git status --short",
        "git -C /t diff --stat",
        "git --no-pager -c core.pager=cat diff",
        "cd /t && L7R_BLOCKS=none make claims-triage > /tmp/t1-triage.log 2>&1; tail -5 /tmp/t1-triage.log",
        "make builder-checks CRATE=\"rust/guard\" 2>&1 | grep -E 'FAILED|result' | head -20",
        "make task-add F=451 TITLE=\"the band; found by T1, see `make decide`\"",
        "make decide F=451 T=T1 # then the review",
        "T=T1",
    ] {
        assert!(allowed(&bash(cmd)), "{cmd}");
    }
    // what is let through is recorded as its command wrote it
    assert_eq!(
        bash("cd /t && make task-add F=451 TITLE=\"a b\""),
        Band::Allowed("cd /t; make task-add F=451 TITLE=\"a b\"".to_owned())
    );
    for tool in ["Read", "Grep"] {
        assert_eq!(judge(tool, &json!({})), Band::Allowed(tool.to_owned()));
    }
    let review = json!({"subagent_type": "spec-fidelity", "prompt": "  MODE 4: PLAN REVIEW of 3 changed block(s) of feature 451's plan"});
    assert!(allowed(&judge("Agent", &review)));
    assert!(allowed(&judge("Task", &review)));
}

#[test]
fn every_other_kind_is_refused_naming_it() {
    for (cmd, what) in [
        ("make quick", "make quick"),
        ("cd /t && make decide F=1 T=T1 && make land", "make land"),
        ("make", "make .DEFAULT_GOAL"),
        ("cargo build", "`cargo build`"),
        ("make decide && rm -rf x", "`rm -rf x`"),
        ("make task-add TITLE=\"$(rm -rf z)\"", "`rm -rf z`"),
        ("bash -c \"make decide\"", "`bash -c \"make decide\"`"),
        // a quoted make target is no invocation: echo is what runs
        ("echo 'make decide'", "`echo 'make decide'`"),
        ("git commit -m x", "`git commit -m x`"),
        ("git -C /t", "`git -C /t`"),
        ("git diff --output=/t/x.rs", "`git diff --output=/t/x.rs`"),
        // 451 T427: a `cd`'s redirect, which the walk does not read, refuses the `cd`
        (
            "cd /t > /t/rust/a.rs && make decide",
            "`cd /t > /t/rust/a.rs`",
        ),
        ("pushd /t >> /t/a.rs", "`pushd /t >> /t/a.rs`"),
        // 451 T433: a `>& FILE` the walk does not see, refused whole
        (
            "tail -n 0 x >& /t/rust/a.rs",
            "`tail -n 0 x >& /t/rust/a.rs`",
        ),
        ("grep x a >&/t/b.rs", "`grep x a >&/t/b.rs`"),
        ("", "an empty command"),
    ] {
        assert_eq!(bash(cmd), no(what), "{cmd}");
    }
    for (tool, ti, what) in [
        (
            "Edit",
            json!({"file_path": "/t/x.rs"}),
            "an Edit of /t/x.rs",
        ),
        (
            "Write",
            json!({"file_path": "/t/y.md"}),
            "a Write of /t/y.md",
        ),
        ("SendMessage", json!({"to": "a1"}), "a SendMessage call"),
        (
            "Agent",
            json!({"subagent_type": "claims-triage", "prompt": "MODE 4: PLAN REVIEW"}),
            "a dispatch of `claims-triage`",
        ),
        (
            "Agent",
            json!({"subagent_type": "spec-fidelity", "prompt": "MODE 1: an exception"}),
            "a dispatch of `spec-fidelity`",
        ),
        (
            "Agent",
            json!({"subagent_type": "general-purpose", "prompt": "build T2"}),
            "a dispatch of `general-purpose`",
        ),
    ] {
        assert_eq!(judge(tool, &ti), no(what));
    }
}
