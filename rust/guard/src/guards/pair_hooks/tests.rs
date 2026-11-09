//! The decider against a fixture clone whose tools are a few lines of Python answering from files the test writes - each test a
//! handful of tool starts, under a tenth of a second (FR-008). The verdicts against today's are the suite's
//! (`tests/hooks/test-pair-hooks.sh`, replayed through the shim).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, find_root, is_gate_invocation, judge, resolved, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

/// The fake tools, `sh` scripts run as the guard runs its Python tools (`<interpreter> <script> args`): each answers from the
/// clone's `.git/<file>`. The arbiter's check is Python code the guard runs as itself, so its fake module stays Python.
const TOOLS: [(&str, &str); 6] = [
    ("scripts/reviews/checkpoint.py", "cat \"$3/.git/due\" 2>/dev/null\n"),
    (
        "scripts/reviews/review_prereq.py",
        "if [ \"$1\" = named ]; then cat \"$3/.git/named\" 2>/dev/null; exit 0; fi\n[ -f \"$3/.git/problems\" ] || exit 0\ncat \"$3/.git/problems\"; echo; echo 'on stderr' >&2; exit 1\n",
    ),
    (
        "scripts/reviews/review_owed.py",
        "c=$2\nif [ $# -eq 2 ]; then : > \"$c/.git/owed-asked\"; cat \"$c/.git/owed\" 2>/dev/null; exit 0; fi\nif [ \"$3\" = --glyph-gate ]; then [ -f \"$c/.git/early\" ] && { echo \"not due: $4\"; exit 1; }; exit 0; fi\nsuffix=; [ $# -gt 4 ] && suffix=-escaped\n: > \"$c/.git/glyph-$4$suffix\"\n",
    ),
    ("scripts/gates/l7r-gate.sh", "if [ \"$1\" = plan ]; then cat \"$3/.git/undecided\" 2>/dev/null; exit 0; fi
[ -f .git/green ]\n"),
    (
        "scripts/hooks/lib/hm_arbiter.py",
        "import pathlib\ndef _f(root,n): p=pathlib.Path(root,'.git',n); return p.read_text() if p.exists() else ''\ndef unit_content_key(root,unit): return 'ck'\ndef closed(root,prefix,ck=None): return _f(root,'closed')\ndef continues(root,prefix): return int(_f(root,'continues') or 0)\ndef lapsed(root,prefix,ck): return 0\ndef trip(root,*a): pathlib.Path(root,'.git/tripped').write_text('')\ndef refusal(keys,root): return 'ask the arbiter: '+keys[0]\n",
    ),
    ("Makefile", "engine-key:\n\t@printf KEY\n"),
];

struct Fixture {
    clone: PathBuf,
    input: Value,
}

impl Fixture {
    fn new(tag: &str, tool: &str, tool_input: &Value) -> Self {
        crate::shared::log::quiet();
        let clone =
            std::env::temp_dir().join(format!("l7r-guard-pair-{tag}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&clone);
        std::fs::create_dir_all(clone.join(".git")).unwrap();
        for (path, body) in TOOLS {
            let p = clone.join(path);
            std::fs::create_dir_all(p.parent().unwrap()).unwrap();
            std::fs::write(p, body).unwrap();
        }
        Self {
            input: json!({"tool_name": tool, "tool_input": tool_input, "session_id": "s"}),
            clone,
        }
    }

    fn set(&self, file: &str, text: &str) -> &Self {
        std::fs::write(self.clone.join(".git").join(file), text).unwrap();
        self
    }

    fn has(&self, file: &str) -> bool {
        self.clone.join(".git").join(file).exists()
    }

    fn judge_as(&self, event: &str, fell_back: bool) -> Vec<Answer> {
        let e = Event {
            name: event.to_owned(),
            input: self.input.clone(),
        };
        let session = Session::from_input(&json!({}));
        judge(&Ctx {
            event: &e,
            session: &session,
            clone: self.clone.clone(),
            tree: self.clone.clone(),
            python: "sh",
            fell_back,
        })
    }

    fn judge(&self) -> Vec<Answer> {
        self.judge_as("PreToolUse", false)
    }
}

fn refusal(answers: &[Answer]) -> String {
    let [Answer::Refuse(why)] = answers else {
        return format!("not one refusal: {answers:?}");
    };
    why.clone()
}

fn review(prompt: &str) -> Value {
    json!({"subagent_type": "settlement-review", "prompt": prompt})
}

#[test]
fn a_gate_is_an_invocation_not_a_mention() {
    assert!(is_gate_invocation("make done"));
    assert!(is_gate_invocation("cd x && make -s FULL=1 done 2>&1"));
    assert!(is_gate_invocation("echo hi\nmake maps"));
    assert!(!is_gate_invocation("echo 'make done'"));
    assert!(!is_gate_invocation("cat <<EOF\nmake done\nEOF"));
    assert!(!is_gate_invocation("make -n done"));
    assert!(!is_gate_invocation("make doneish"));
}

#[test]
fn a_gate_runs_as_typed_with_its_key_kept() {
    let f = Fixture::new("gate", "Bash", &json!({"command": "make done"}));
    assert!(f.judge().is_empty());
    let state: Value = serde_json::from_str(
        &std::fs::read_to_string(f.clone.join(".git/pairing-state.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(state["gate_key"], "KEY");
    let other = Fixture::new("plain", "Bash", &json!({"command": "ls"}));
    assert!(other.judge().is_empty() && !other.has("pairing-state.json"));
}

#[test]
fn the_step_back_refuses_a_gate_and_an_agent_past_its_hour() {
    let f = Fixture::new("due", "Bash", &json!({"command": "make done"}));
    f.set("due", "the hour's step-back is due");
    assert_eq!(
        refusal(&f.judge()),
        "\n\x1b[1mBLOCKED: the hour's step-back is due\x1b[0m\n"
    );
    let a = Fixture::new(
        "due-agent",
        "Agent",
        &json!({"subagent_type": "spec-fidelity"}),
    );
    a.set("due", "due");
    assert!(refusal(&a.judge()).contains("BLOCKED: due"));
    a.set("due", "");
    assert!(a.judge().is_empty(), "a check that is not a review passes");
}

#[test]
fn a_review_waits_for_the_plans_decisions_unless_decide_ok_says_why() {
    let f = Fixture::new(
        "decide",
        "Agent",
        &review("read /tmp/l7r-check/x/MANIFEST.md"),
    );
    f.set("undecided", "T1's decisions have no verdict")
        .set("green", "");
    let why = refusal(&f.judge());
    assert!(why.contains("BLOCKED: settlement-review on /tmp/l7r-check/x/MANIFEST.md: T1's decisions have no verdict"), "{why}");
    let bare = Fixture::new("decide-bare", "Agent", &review("no bundle named"));
    bare.set("undecided", "no verdict");
    assert!(refusal(&bare.judge()).contains("on its prompt: no verdict"));
    let ok = Fixture::new(
        "decide-ok",
        "Agent",
        &review(r#"DECIDE_OK="ruled in the hour" go"#),
    );
    ok.set("undecided", "no verdict").set("green", "");
    assert!(ok.judge().is_empty());
    let short = Fixture::new("decide-short", "Agent", &review(r#"DECIDE_OK="ok""#));
    short.set("undecided", "no verdict");
    assert!(refusal(&short.judge()).contains("on its prompt"));
}

#[test]
fn one_unit_an_agent() {
    let f = Fixture::new("multi", "Agent", &review("two maps"));
    f.set("named", "m1\nm2\n");
    std::fs::create_dir_all(f.clone.join(".git/review-snapshot/m1")).unwrap();
    std::fs::write(f.clone.join(".git/review-snapshot/m1/dispatch.md"), "").unwrap();
    let why = refusal(&f.judge());
    assert!(
        why.contains("asks for 2 units in ONE agent")
            && why.contains("m1/dispatch.md\n")
            && why.contains("    m2: no prompt file")
    );
    assert!(why.ends_with("There is no escape for this shape (feature 248 D1).\n"));
}

#[test]
fn a_glyph_unit_waits_for_its_hour_unless_glyph_due_ok_says_why() {
    let glyph = |tag: &str, prompt: &str| {
        let f = Fixture::new(
            tag,
            "Agent",
            &json!({"subagent_type": "glyph-check", "prompt": prompt}),
        );
        f.set("named", "g1\n").set("green", "");
        f
    };
    let early = glyph("glyph-early", "check g1");
    early.set("early", "");
    let why = refusal(&early.judge());
    assert!(why.contains("BLOCKED: not due: g1") && why.contains("GLYPH_DUE_OK=\"<why>\""));
    let due = glyph("glyph-due", "check g1");
    assert!(due.judge().is_empty() && due.has("glyph-g1"));
    let escaped = glyph("glyph-ok", r#"GLYPH_DUE_OK="the GM asked now""#);
    std::fs::create_dir_all(escaped.clone.join("dev/bypass-log")).unwrap();
    escaped.set("early", "");
    assert!(escaped.judge().is_empty() && escaped.has("glyph-g1-escaped"));
    let bare = glyph("glyph-bare", "GLYPH_DUE_OK=now");
    assert!(refusal(&bare.judge()).contains("GLYPH_DUE_OK needs a REASON"));
    let none = Fixture::new(
        "glyph-none",
        "Agent",
        &json!({"subagent_type": "glyph-check", "prompt": "x"}),
    );
    none.set("green", "");
    std::fs::remove_file(none.clone.join("scripts/reviews/review_owed.py")).unwrap();
    assert!(none.judge().is_empty(), "no owed tool, no glyph hour");
}

#[test]
fn a_review_is_not_spent_on_unverified_work() {
    let f = Fixture::new("prereq", "Agent", &review("m1"));
    f.set("named", "m1\n")
        .set("problems", "the map is stale\nits notes are missing");
    let why = refusal(&f.judge());
    assert!(
        why.contains("  - the map is stale\n  - its notes are missing\n  - on stderr\n")
            && why.contains("REVIEW_PREREQ_OK")
    );
    let owed = Fixture::new("prereq-owed", "Agent", &review("none named"));
    owed.set("owed", "m9\n").set("problems", "stale");
    assert!(refusal(&owed.judge()).contains("  - stale\n"));
    let ok = Fixture::new(
        "prereq-ok",
        "Agent",
        &review(r#"REVIEW_PREREQ_OK="left so on purpose""#),
    );
    ok.set("problems", "stale").set("green", "");
    assert!(ok.judge().is_empty());
    let bare = Fixture::new("prereq-bare", "Agent", &review(r#"REVIEW_PREREQ_OK="no""#));
    assert!(refusal(&bare.judge()).contains("REVIEW_PREREQ_OK needs a REASON"));
    let none = Fixture::new("prereq-none", "Agent", &review("x"));
    none.set("green", "").set("problems", "stale");
    std::fs::remove_file(none.clone.join("scripts/reviews/review_prereq.py")).unwrap();
    assert!(none.judge().is_empty());
}

/// A fixture at its third round of `m1`.
fn third_round(tag: &str) -> Fixture {
    let f = Fixture::new(tag, "Agent", &review("m1"));
    f.set("named", "m1\n").set("green", "");
    std::fs::write(
        f.clone.join(".git/review-rounds.json"),
        r#"{"none": {"m1": ["a@1", "b@2"]}}"#,
    )
    .unwrap();
    f
}

#[test]
fn past_two_rounds_the_round_arbiter_is_owed_its_ruling() {
    let f = third_round("rounds-owed");
    let why = refusal(&f.judge());
    assert!(
        why.contains("BLOCKED: round 3 of m1 for settlement-review")
            && why.contains("ask the arbiter: round:settlement-review|m1@3")
    );
    assert!(f.has("tripped"));
}

#[test]
fn a_continue_ruling_lets_the_round_go() {
    let f = third_round("rounds-continue");
    f.set("continues", "1");
    assert!(f.judge().is_empty());
}

#[test]
fn a_closed_unit_is_not_re_asked() {
    let f = third_round("rounds-closed");
    f.set("closed", "accepted");
    assert!(refusal(&f.judge()).contains("the round arbiter closed"));
}

#[test]
fn a_review_needs_a_green_gate_unless_pair_ok() {
    let f = Fixture::new("green", "Agent", &review("m1"));
    f.set("named", "m1\n").set("owed", "m1\n");
    let why = refusal(&f.judge());
    assert!(why.contains("a settlement-review with no green gate") && !why.contains("NOTE:"));
    assert!(refusal(&f.judge_as("PreToolUse", true))
        .contains("NOTE: this session's clone could not be resolved"));
    f.set("green", "");
    assert!(f.judge().is_empty());
    let state: Value = serde_json::from_str(
        &std::fs::read_to_string(f.clone.join(".git/pairing-state.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(
        (
            state["review_dispatch_key"].as_str(),
            state["dispatched"]["m1"]["key"].as_str()
        ),
        (Some("KEY"), Some("KEY"))
    );
    let ok = Fixture::new("pair-ok", "Agent", &review("m1 PAIR_OK because asked"));
    ok.set("named", "m1\n");
    assert!(ok.judge().is_empty());
    let unkeyed = Fixture::new("unkeyed", "Agent", &review("m1"));
    unkeyed.set("named", "m1\n").set("green", "");
    std::fs::write(unkeyed.clone.join("Makefile"), "engine-key:\n\t@true\n").unwrap();
    assert!(
        refusal(&unkeyed.judge()).contains("no green gate") && !unkeyed.has("pairing-state.json")
    );
}

#[test]
fn owed_units_sent_together_are_logged_parallel_and_apart_serialized() {
    for (tag, gap, rule) in [("par", 5, "parallel"), ("ser", 500, "serialized")] {
        let f = Fixture::new(tag, "Agent", &review("m"));
        f.set("owed", "m1\nm2\n").set("green", "");
        std::fs::write(
            f.clone.join(".git/pairing-state.json"),
            format!(
                r#"{{"dispatched": {{"m1": {{"key": "KEY", "at": {}}}}}}}"#,
                super::state::wall() - gap
            ),
        )
        .unwrap();
        f.set("named", "m2\n");
        assert!(f.judge().is_empty(), "{rule}");
    }
}

#[test]
fn a_turn_may_not_end_with_a_dropped_dispatch() {
    let mut f = Fixture::new("stop", "", &json!({}));
    assert!(f.judge_as("Stop", false).is_empty());
    let transcript = f.clone.join("t.jsonl");
    let rows = [
        json!({"timestamp": "1", "message": {"content": [{"type": "tool_use", "name": "Agent", "id": "a", "input": {"subagent_type": "x", "description": "d"}}]}}),
        json!({"message": {"content": [{"type": "tool_result", "tool_use_id": "a", "is_error": true, "content": "PreToolUse:Agent hook error"}]}}),
    ];
    std::fs::write(
        &transcript,
        rows.iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join("\n"),
    )
    .unwrap();
    f.input["transcript_path"] = json!(transcript);
    assert!(refusal(&f.judge_as("Stop", false)).contains("neither sent again nor recorded dropped"));
    assert!(!f.has("owed-asked"));
}

#[test]
fn the_clone_is_the_sessions_else_the_cwds_tree() {
    let d = std::env::temp_dir().join(format!("l7r-guard-pair-root-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join(".clones/.session-clones")).unwrap();
    std::fs::create_dir_all(d.join(".clones/mine/.git")).unwrap();
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::write(
        d.join(".clones/.session-clones/sid"),
        d.join(".clones/mine").to_string_lossy().as_bytes(),
    )
    .unwrap();
    let mut s = Session::from_input(&json!({"session_id": "sid"}));
    s.main_seam = Some(d.to_string_lossy().into_owned());
    assert_eq!(
        find_root(&s, Path::new("/")),
        Some((d.join(".clones/mine"), false))
    );
    let mut none = Session::from_input(&json!({}));
    none.main_seam = Some(d.to_string_lossy().into_owned());
    assert_eq!(find_root(&none, &d), Some((d.clone(), true)));
    assert_eq!(
        find_root(&none, &d.join(".clones/mine")),
        Some((d.join(".clones/mine"), false))
    );
    assert_eq!(find_root(&none, Path::new("/")), None);
    let ls = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(resolved(&ls, &none, &d, None).is_empty());
    assert!(decide(&ls, &none).is_empty());
    assert!(refusal(&[]).starts_with("not one refusal"));
    assert!(resolved(&ls, &none, Path::new("/"), Some("/t".to_owned())).is_empty());
    assert_eq!(
        super::tree(Some("/t".to_owned()), Path::new("/c")),
        PathBuf::from("/t")
    );
    assert_eq!(super::tree(None, Path::new("/c")), PathBuf::from("/c"));
}
