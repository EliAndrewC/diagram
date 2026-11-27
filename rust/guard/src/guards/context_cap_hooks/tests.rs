//! The cap against a temporary clone and a builder's transcript; the payloads are the real ones pinned in `payloads.json`. The suite
//! (`tests/hooks/test-context-cap-hooks.sh`, replayed through the shim and, for the handoff, the whole chain) drives the binary.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    answer, band_refusal, context, is_handoff, judge, now, own_transcript, permit_key, plain,
    refusal, tree_of, usage_of, Said, Stale, CONTEXT_CAP_TOKENS, TAIL_BYTES,
    WRAP_UP_CEILING_TOKENS,
};
use crate::guards::guard_file_hooks::cli;
use crate::protocol::{run, Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

const PINNED: &str = include_str!("payloads.json");
const AID: &str = "af3dc58915037d8d6";

fn pinned(which: &str) -> Value {
    serde_json::from_str::<Value>(PINNED).unwrap()[which].clone()
}

fn none(_: &str) -> Option<String> {
    None
}

/// No session clone: the call's cwd gives the tree.
fn no_clone() -> Option<PathBuf> {
    None
}

/// An assistant row of one model call whose context is `tokens`.
fn call(tokens: u64) -> Value {
    json!({"type": "assistant", "message": {"id": "msg_x", "usage": {
        "input_tokens": 2, "cache_read_input_tokens": tokens - 102, "cache_creation_input_tokens": 100, "output_tokens": 50}}})
}

/// A clone with a defined agent `review-x`, and the session's transcript directory holding the builder's own transcript of `rows`;
/// `task` puts a started task in force for feature 451-x.
struct Fixture {
    dir: TempDir,
}

impl Fixture {
    fn new(tag: &str, rows: &[Value], task: Option<&str>) -> Self {
        let dir = TempDir::new(&format!("guard-context-cap-{tag}"));
        std::fs::create_dir_all(dir.join("clone/.git")).unwrap();
        std::fs::create_dir_all(dir.join("clone/.claude/agents")).unwrap();
        std::fs::write(dir.join("clone/.claude/agents/review-x.md"), "---\n").unwrap();
        if let Some(t) = task {
            std::fs::create_dir_all(dir.join("clone/specs/451-x")).unwrap();
            std::fs::create_dir_all(dir.join("clone/.specify")).unwrap();
            std::fs::write(
                dir.join("clone/.specify/feature.json"),
                r#"{"feature_directory": "specs/451-x"}"#,
            )
            .unwrap();
            std::fs::write(
                dir.join("clone/.git/task-starts.jsonl"),
                format!("{{\"feature\": \"451-x\", \"task\": \"{t}\", \"utc\": \"2026-11-20T10:00:00Z\"}}\n"),
            )
            .unwrap();
        }
        let f = Self { dir };
        f.transcript(AID, rows);
        f
    }

    fn clone(&self) -> PathBuf {
        std::fs::canonicalize(self.dir.join("clone")).unwrap()
    }

    fn session(&self) -> PathBuf {
        self.dir.join("proj/sess.jsonl")
    }

    fn transcript(&self, aid: &str, rows: &[Value]) {
        let d = self.dir.join("proj/sess/subagents");
        std::fs::create_dir_all(&d).unwrap();
        let text: String = rows.iter().map(|r| r.to_string() + "\n").collect();
        std::fs::write(d.join(format!("agent-{aid}.jsonl")), text).unwrap();
    }

    /// The builder's meta file, its description naming `task`: a builder's line carries the task its brief names, never the clone's
    /// mark (451 T161).
    fn briefed(&self, task: &str) {
        let d = self.dir.join("proj/sess/subagents");
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(
            d.join(format!("agent-{AID}.meta.json")),
            format!(r#"{{"description":"451 {task}: the builder","spawnDepth":1}}"#),
        )
        .unwrap();
    }

    fn handoffs(&self) -> PathBuf {
        self.clone().join(".git/l7r-handoffs")
    }

    /// The pinned `which` payload, its `cwd` and `transcript_path` this fixture's, its tool `tool` with `tool_input`.
    fn input(&self, which: &str, tool: &str, tool_input: Value) -> Value {
        let mut p = pinned(which);
        p["cwd"] = json!(self.clone());
        p["transcript_path"] = json!(self.session());
        p["tool_name"] = json!(tool);
        p["tool_input"] = tool_input;
        p
    }

    fn bash(&self, which: &str, cmd: &str) -> Value {
        self.input(which, "Bash", json!({"command": cmd}))
    }
}

/// The verdict on `input` against the cap, the process's environment unread.
fn verdict(input: &Value) -> Option<Said> {
    judge(input, Path::new("/"), &none, CONTEXT_CAP_TOKENS, &no_clone)
}

/// THE PINNED PAYLOADS (D8's first step): a builder's call carries `agent_id` and `agent_type` `general-purpose`, a defined agent's
/// its own name, the main session's neither; the transcript path is the session's, the builder's own derived beside it.
#[test]
fn the_pinned_payloads_carry_the_fields_the_guard_reads() {
    let (b, d, m) = (pinned("builder"), pinned("defined"), pinned("main"));
    assert_eq!(b["hook_event_name"], "PreToolUse");
    assert_eq!(b["agent_id"], AID);
    assert_eq!(b["agent_type"], "general-purpose");
    assert_eq!(d["agent_type"], "probe-check");
    assert!(m.get("agent_id").is_none() && m.get("agent_type").is_none());
    let t = b["transcript_path"].as_str().unwrap();
    // the payload's transcript is the session's
    assert!(!t.contains("subagents"));
    assert_eq!(
        own_transcript(t, AID).unwrap(),
        PathBuf::from(format!(
            "{}/subagents/agent-{AID}.jsonl",
            t.trim_end_matches(".jsonl")
        ))
    );
    assert_eq!(own_transcript("/x/sess.json", AID), None);
}

#[test]
fn the_context_is_the_last_assistant_rows_usage() {
    let f = Fixture::new("read", &[call(100_000), call(350_000)], None);
    let own = f.dir.join(format!("proj/sess/subagents/agent-{AID}.jsonl"));
    assert_eq!(context(&own), Some(350_000));
    // a later user row holding an Agent call's result carries the child's usage; a synthetic row of zero is no call; bad JSON skipped
    let child = json!({"type": "user", "toolUseResult": {"usage": {"input_tokens": 900_000}}, "message": {"usage": {"input_tokens": 900_000}}});
    let synthetic =
        json!({"type": "assistant", "message": {"usage": {"input_tokens": 0, "output_tokens": 0}}});
    f.transcript(AID, &[call(120_000), child, synthetic, json!("x")]);
    std::fs::write(
        &own,
        std::fs::read_to_string(&own).unwrap() + "{\"usage\" not json\n",
    )
    .unwrap();
    assert_eq!(context(&own), Some(120_000));
    // a last row longer than a read step, with no trailing newline
    let big = json!({"type": "assistant", "pad": "p".repeat(200_000), "message": {"usage": {"input_tokens": 400_000}}});
    std::fs::write(&own, format!("{}\n{big}", call(5_000))).unwrap();
    assert_eq!(context(&own), Some(400_000));
    // none at all, no file, and a call deeper than the tail
    f.transcript(AID, &[json!({"type": "user"})]);
    assert_eq!(context(&own), None);
    assert_eq!(context(&f.dir.join("nothing.jsonl")), None);
    let deep = format!(
        "{}\n{}\n",
        call(500_000),
        "x".repeat(usize::try_from(TAIL_BYTES).unwrap() + 10)
    );
    std::fs::write(&own, deep).unwrap();
    assert_eq!(context(&own), None);
    assert_eq!(usage_of(b"{\"type\": \"assistant\"}"), None);
}

/// RED FIRST, the five cases: a builder past the cap refused, naming its handoff; its handoff's Write passing; a builder under the
/// cap passing; the main session passing; the escape passing, a bare one refused. And a defined agent past the cap passing.
#[test]
fn a_builder_past_the_cap_is_refused_but_for_its_handoff() {
    let f = Fixture::new("cap", &[call(350_000)], None);
    let handoff = f.handoffs().join(format!("{AID}.md"));
    // refused, every tool, naming the file
    for input in [
        f.bash("builder", "make quick"),
        f.input(
            "builder",
            "Edit",
            json!({"file_path": f.clone().join("x.rs")}),
        ),
        f.input("builder", "Grep", json!({"pattern": "x"})),
    ] {
        assert_eq!(
            verdict(&input),
            Some(Said::Refused {
                agent: AID.to_owned(),
                tokens: 350_000,
                handoff: handoff.clone(),
                code: false
            })
        );
    }
    // the handoff's Write, Edit and Read pass, its path recorded; another agent's handoff, or this one's name elsewhere, does not
    for tool in ["Write", "Edit", "Read"] {
        let input = f.input(
            "builder",
            tool,
            json!({"file_path": handoff, "content": "done; left"}),
        );
        assert_eq!(
            verdict(&input),
            Some(Said::Handoff(handoff.display().to_string()))
        );
    }
    let other = f.handoffs().join("a0000000000000000.md");
    let elsewhere = f.clone().join(format!("{AID}.md"));
    for file in [other, elsewhere] {
        let input = f.input(
            "builder",
            "Write",
            json!({"file_path": file, "content": "x"}),
        );
        assert!(matches!(verdict(&input), Some(Said::Refused { .. })));
    }
    // a builder under the cap, and at it, pass
    f.transcript(AID, &[call(310_000), call(250_000)]);
    assert_eq!(verdict(&f.bash("builder", "make quick")), None);
    f.transcript(AID, &[call(CONTEXT_CAP_TOKENS)]);
    assert_eq!(verdict(&f.bash("builder", "make quick")), None);
    // the main session, and a defined agent past the cap, pass without a read
    f.transcript(AID, &[call(900_000)]);
    assert_eq!(verdict(&f.bash("main", "make quick")), None);
    let mut defined = f.bash("builder", "make quick");
    defined["agent_type"] = json!("review-x");
    assert_eq!(verdict(&defined), None);
    // the escape, and a bare one
    assert_eq!(
        verdict(&f.bash("builder", "CONTEXT_OK=\"the landing needs it\" make land")),
        Some(Said::Escaped("the landing needs it".to_owned()))
    );
    assert!(matches!(
        verdict(&f.bash("builder", "make quick CONTEXT_OK")),
        Some(Said::NoReason(t)) if t.contains("CONTEXT_OK with no reason")
    ));
}

/// A row carrying an advisor call: the top level sums the builder's own two iterations, `before` and `after` the call; the
/// advisor's own iteration is in neither (451 T68, measured 2026-11-21 on 581 such rows).
fn advisor_call(before: u64, after: u64) -> Value {
    let own = |n: u64| json!({"type": "message", "input_tokens": 2, "cache_read_input_tokens": n - 1002, "cache_creation_input_tokens": 1000, "output_tokens": 50});
    json!({"type": "assistant", "message": {"id": "msg_a", "usage": {
        "input_tokens": 4, "cache_read_input_tokens": before + after - 2004, "cache_creation_input_tokens": 2000, "output_tokens": 100,
        "iterations": [own(before),
            {"type": "advisor_message", "input_tokens": 140_114, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0,
             "output_tokens": 10_489, "model": "claude-fable-5-2"},
            own(after)]}}})
}

/// RED FIRST (451 T68): the cap's first refusal of the window, a builder at 149,686 and 151,198 either side of its advisor call,
/// read 300,884 and was refused; it passes on its own context. One past the cap on its own last iteration is still refused at it.
#[test]
fn a_builder_just_past_an_advisor_call_is_judged_on_its_own_context() {
    let f = Fixture::new(
        "advisor",
        &[call(148_153), advisor_call(149_686, 151_198)],
        None,
    );
    assert_eq!(verdict(&f.bash("builder", "make quick")), None);
    f.transcript(AID, &[advisor_call(290_000, 350_000)]);
    assert_eq!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Refused {
            agent: AID.to_owned(),
            tokens: 350_000,
            handoff: f.handoffs().join(format!("{AID}.md")),
            code: false
        })
    );
}

#[test]
fn the_handoff_is_named_for_the_task_the_calls_line_carries() {
    let f = Fixture::new("task", &[call(400_000)], Some("T12"));
    f.briefed("T12");
    let handoff = f.handoffs().join(format!("T12-{AID}.md"));
    assert!(matches!(
        verdict(&f.bash("builder", "ls")),
        Some(Said::Refused { handoff: named, .. }) if named == handoff
    ));
    let write = f.input(
        "builder",
        "Write",
        json!({"file_path": handoff, "content": "x"}),
    );
    assert!(matches!(verdict(&write), Some(Said::Handoff(_))));
    // the file the task-less name gives is this agent's too
    let bare = f.input(
        "builder",
        "Write",
        json!({"file_path": f.handoffs().join(format!("{AID}.md"))}),
    );
    assert!(matches!(verdict(&bare), Some(Said::Handoff(_))));
}

/// A builder's brief: its transcript's first row, the prompt naming `names` as handoff files under `dir`.
fn brief_row(dir: &Path, files: &[&str]) -> Value {
    let ends = files.iter().fold(String::new(), |mut out, n| {
        let _ = writeln!(out, "END at a handoff, `{}`.", dir.join(n).display());
        out
    });
    json!({"type": "user", "message": {"role": "user", "content": format!("BUILDER-BRIEF 451 T12 KIND=fix\nSTOP POINT (fix): ...\n{ends}If your context passes 200k, stop with a handoff at {}.", dir.join("done-pending-T12.md").display())}})
}

/// RED FIRST (451 T352): past the cap the exit takes any `.md` of the handoffs directory the builder's own brief names - a build
/// half's `<task>-build.md`, a bundle's, a `done-pending-<task>.md` - and the refusal names the brief's first such file; a file there
/// the brief does not name, or the brief's name in another directory, stays refused. The `<agent>.md` rule stands beside it.
#[test]
fn the_exit_takes_the_handoff_the_brief_names() {
    let f = Fixture::new("briefed", &[], None);
    let dir = f.handoffs();
    f.transcript(
        AID,
        &[brief_row(&dir, &["T12-T13-build.md"]), call(350_000)],
    );
    for name in [
        "T12-T13-build.md",
        "done-pending-T12.md",
        &format!("{AID}.md"),
    ] {
        let input = f.input(
            "builder",
            "Write",
            json!({"file_path": dir.join(name), "content": "x"}),
        );
        assert!(matches!(verdict(&input), Some(Said::Handoff(_))), "{name}");
    }
    for file in [
        dir.join("T12-other.md"),
        f.clone().join("done-pending-T12.md"),
    ] {
        let input = f.input(
            "builder",
            "Write",
            json!({"file_path": file, "content": "x"}),
        );
        assert!(matches!(verdict(&input), Some(Said::Refused { .. })));
    }
    assert!(matches!(
        verdict(&f.bash("builder", "ls")),
        Some(Said::Refused { handoff, .. }) if handoff == dir.join("T12-T13-build.md")
    ));
}

/// 451 T417, THE WRAP-UP BAND: from the cap to the ceiling (both edges: 300,001 and 340,000 in it, 340,001 past it) a stop point's
/// steps pass and every other kind is refused naming what and the handoff; past the ceiling the cap's own refusal; the handoff, the
/// escape and the permit judged before the band as before.
#[test]
fn a_builder_in_its_wrap_up_band_finishes_its_stop_point() {
    let f = Fixture::new("band", &[], None);
    let handoff = f.handoffs().join(format!("{AID}.md"));
    let review = json!({"subagent_type": "spec-fidelity", "prompt": "MODE 4: PLAN REVIEW of one task's section"});
    for tokens in [CONTEXT_CAP_TOKENS + 1, WRAP_UP_CEILING_TOKENS] {
        f.transcript(AID, &[call(tokens)]);
        for input in [
            f.bash(
                "builder",
                "cd /t && export SPECIFY_FEATURE=451-x && make decide F=451 T=T1",
            ),
            f.bash("builder", "git status --short"),
            f.input("builder", "Read", json!({"file_path": "/t/x.rs"})),
            f.input("builder", "Grep", json!({"pattern": "x"})),
            f.input("builder", "Agent", review.clone()),
        ] {
            assert!(matches!(verdict(&input), Some(Said::Band(_))), "{input}");
        }
        for (input, what) in [
            (f.bash("builder", "make quick"), "make quick"),
            (
                f.input("builder", "Edit", json!({"file_path": "/t/x.rs"})),
                "an Edit of /t/x.rs",
            ),
            (
                f.input(
                    "builder",
                    "Agent",
                    json!({"subagent_type": "general-purpose", "prompt": "go"}),
                ),
                "a dispatch of `general-purpose`",
            ),
        ] {
            assert_eq!(
                verdict(&input),
                Some(Said::BandRefused {
                    agent: AID.to_owned(),
                    tokens,
                    handoff: handoff.clone(),
                    what: what.to_owned()
                })
            );
        }
        let write = f.input(
            "builder",
            "Write",
            json!({"file_path": handoff, "content": "x"}),
        );
        assert!(matches!(verdict(&write), Some(Said::Handoff(_))));
        assert!(matches!(
            verdict(&f.bash("builder", "CONTEXT_OK=\"the landing needs it\" make land")),
            Some(Said::Escaped(_))
        ));
    }
    f.transcript(AID, &[call(WRAP_UP_CEILING_TOKENS + 1)]);
    for input in [
        f.bash("builder", "make decide F=451 T=T1"),
        f.input("builder", "Agent", review),
        f.input("builder", "Read", json!({"file_path": "/t/x.rs"})),
    ] {
        assert!(matches!(verdict(&input), Some(Said::Refused { .. })));
    }
}

/// The band's answers and records: a step passes recorded `wrap-up`, a refusal's text says the band, what was refused, what is
/// still allowed and the handoff (451 T417).
#[test]
fn the_bands_answers_and_records() {
    crate::shared::log::quiet();
    let f = Fixture::new("band-answer", &[call(320_000)], None);
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    assert!(ask(f.bash("builder", "make claims-owed")).is_empty());
    let handoff = f.handoffs().join(format!("{AID}.md"));
    let text = band_refusal(320_000, &handoff, "make quick");
    assert_eq!(
        ask(f.bash("builder", "make quick")),
        vec![Answer::Refuse(text.clone())]
    );
    let kept = [
        "BLOCKED: this builder's context is 320000 tokens, past the cap of 300000: in its wrap-up band, up to 340000",
        "Refused: make quick.\nStill allowed:",
        "make decide, plan-delta, plan-verdict, claims-triage, claims-owed, task-add, task-withdraw, builder-checks",
        "git status or git diff",
        "MODE 4: PLAN REVIEW",
        &handoff.display().to_string(),
        "for a fresh builder",
        "CONTEXT_OK=\"<reason>\"",
    ];
    let missing: Vec<&str> = kept.into_iter().filter(|k| !text.contains(k)).collect();
    assert_eq!(missing, Vec::<&str>::new(), "{text}");
}

#[test]
fn what_it_cannot_read_it_passes() {
    let f = Fixture::new("blind", &[call(900_000)], None);
    // an unsafe agent id, an agent type that is no plain name, a transcript path with no `.jsonl`, outside any clone
    let mut bad = f.bash("builder", "ls");
    bad["agent_id"] = json!("../x");
    assert_eq!(verdict(&bad), None);
    let mut odd = f.bash("builder", "ls");
    odd["agent_type"] = json!("../review-x");
    // a type that names no file is a builder's
    assert!(matches!(verdict(&odd), Some(Said::Refused { .. })));
    let mut path = f.bash("builder", "ls");
    path["transcript_path"] = json!(f.dir.join("proj/sess"));
    assert_eq!(verdict(&path), None);
    let mut outside = f.bash("builder", "ls");
    outside["cwd"] = json!(f.dir.join("proj"));
    assert_eq!(verdict(&outside), None);
    assert!(plain("a1-b_2") && !plain("") && !plain("a/b") && !plain(".."));
}

#[test]
fn the_handoff_path_compares_by_its_real_directory() {
    let f = Fixture::new("real", &[], None);
    std::fs::create_dir_all(f.handoffs()).unwrap();
    let dotted = f
        .clone()
        .join(".git/../.git/l7r-handoffs")
        .join(format!("x-{AID}.md"));
    assert!(is_handoff(
        &dotted.display().to_string(),
        &f.handoffs(),
        AID
    ));
    assert!(!is_handoff("/", &f.handoffs(), AID));
    // a cwd that is no directory walks up from itself as written
    assert_eq!(tree_of(Path::new("/no/such/dir")), None);
}

/// The hook's own entry, the process's environment and directory read: the main session passes, a builder past the cap is refused.
#[test]
fn the_hook_entry_passes_the_main_session() {
    crate::shared::log::quiet();
    let f = Fixture::new("entry", &[call(900_000)], None);
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("main", "make quick"),
    };
    assert_eq!(run(&mut e, &[super::GUARD]).code, 0);
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("builder", "make quick"),
    };
    assert_eq!(run(&mut e, &[super::GUARD]).code, 2);
}

/// The answers, each firing written to the guard log: the refusal's text names the file, the next step and the escape.
#[test]
fn the_answers_and_their_records() {
    crate::shared::log::quiet();
    let f = Fixture::new("answer", &[call(350_000)], None);
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    let handoff = f.handoffs().join(format!("{AID}.md"));
    let text = refusal(350_000, &handoff, false);
    assert_eq!(
        ask(f.bash("builder", "make quick")),
        vec![Answer::Refuse(text.clone())]
    );
    assert!(text.contains(&handoff.display().to_string()));
    assert!(text.contains("350000 tokens, past the cap of 300000"));
    assert!(
        text.contains("Stop, and reply with that path") && text.contains("CONTEXT_OK=\"<reason>\"")
    );
    // 451 T177 (message-check): the why is one clause, its figures and its feature the code's
    assert!(text.contains("Long contexts slow model calls, so the task goes on in a fresh builder:\n\n1. Write the handoff file"), "{text}");
    let kept = [
        "Stop, and reply with that path; the main session dispatches a fresh builder from it.",
        "Escape: CONTEXT_OK=\"<reason>\" (two words or more) in a Bash command",
    ];
    let missing: Vec<&str> = kept.into_iter().filter(|k| !text.contains(k)).collect();
    assert_eq!(missing, Vec::<&str>::new(), "{text}");
    let cut = ["FR-006", "700k", "The next step"]
        .iter()
        .all(|w| !text.contains(w));
    assert!(cut, "{text}");
    let write = f.input(
        "builder",
        "Write",
        json!({"file_path": handoff, "content": "x"}),
    );
    assert!(ask(write).is_empty());
    assert!(ask(f.bash("builder", "CONTEXT_OK=\"the landing needs it\" ls")).is_empty());
    assert!(matches!(
        ask(f.bash("builder", "ls CONTEXT_OK")).as_slice(),
        [Answer::Refuse(_)]
    ));
    assert!(ask(f.bash("main", "ls")).is_empty());
}

// ---- D10: a builder resumed (451 T13) ----

const DISPATCH: &str = "toolu_dispatch";

/// The verdict on a `SendMessage`, its handoff path blanked (the refusal's text is tested for it).
fn sent(input: &Value) -> Option<Said> {
    match verdict(input) {
        Some(Said::Resume { agent, stale, .. }) => Some(Said::Resume {
            agent,
            stale,
            handoff: PathBuf::new(),
        }),
        other => other,
    }
}

impl Fixture {
    /// The agent's meta file beside its transcript: its type, its brief's description, the Agent call that dispatched it.
    fn meta(&self, aid: &str, kind: &str, description: &str) {
        let d = self.dir.join("proj/sess/subagents");
        std::fs::create_dir_all(&d).unwrap();
        let m = json!({"agentType": kind, "isBuiltIn": kind == "general-purpose", "description": description, "toolUseId": DISPATCH});
        std::fs::write(d.join(format!("agent-{aid}.meta.json")), m.to_string()).unwrap();
    }

    /// The feature's event log (451-x's, under the clone's git dir).
    fn events(&self, lines: &[Value]) {
        let d = self.clone().join(".git/l7r-events");
        std::fs::create_dir_all(&d).unwrap();
        let text: String = lines.iter().map(|r| r.to_string() + "\n").collect();
        std::fs::write(d.join("451-x.jsonl"), text).unwrap();
    }

    /// The clone's task starts for 451-x, (task, utc) in order.
    fn starts(&self, rows: &[(&str, &str)]) {
        let text = rows.iter().fold(String::new(), |mut out, (t, u)| {
            let _ = writeln!(
                out,
                "{{\"feature\": \"451-x\", \"task\": \"{t}\", \"utc\": \"{u}\"}}"
            );
            out
        });
        std::fs::write(self.clone().join(".git/task-starts.jsonl"), text).unwrap();
    }

    fn tasks(&self, text: &str) {
        std::fs::write(self.clone().join("specs/451-x/tasks.md"), text).unwrap();
    }

    /// The main session's `SendMessage` to `to`, with `summary`.
    fn send(&self, to: &str, summary: &str) -> Value {
        self.input(
            "main",
            "SendMessage",
            json!({"to": to, "summary": summary, "message": "go on"}),
        )
    }
}

/// A resume fixture: a builder at `tokens`, dispatched at 10:05 by the Agent call `DISPATCH`, its brief `description`, 451-x's T05
/// and T06 open in tasks.md.
fn resumed(tag: &str, tokens: u64, description: &str) -> Fixture {
    let f = Fixture::new(tag, &[call(tokens)], Some("T05"));
    f.meta(AID, "general-purpose", description);
    f.tasks("- [ ] T05 a\n- [ ] T06 b\n");
    f.starts(&[("T05", "2026-11-20T10:00:00Z")]);
    f
}

fn agent_call() -> Value {
    json!({"ev": "PreToolUse", "tool": "Agent", "id": DISPATCH, "task": "T06", "t": "2026-11-20T10:05:00.000Z"})
}

fn end(task: &str, landed: bool, t: &str) -> Value {
    json!({"ev": "Phase", "step": "end", "landed": landed, "tasks": [task], "code": 0, "t": t})
}

fn landed(task: &str) -> Said {
    Said::Resume {
        agent: AID.to_owned(),
        stale: Stale::Landed(task.to_owned()),
        handoff: PathBuf::new(),
    }
}

/// RED FIRST, D10's cases: a `SendMessage` to a builder past the cap, or to one whose task has landed since its dispatch or is ticked,
/// refused; a landing refused or before the dispatch, an open task, a defined agent, passing.
#[test]
fn a_resume_of_a_builder_past_the_cap_or_landed_is_refused() {
    // past the cap, its task open
    let f = resumed("r-cap", 310_000, "451 T05: build it");
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::Resume {
            agent: AID.to_owned(),
            stale: Stale::PastCap(310_000),
            handoff: PathBuf::new()
        })
    );
    // under the cap, its task open: passes
    let f = resumed("r-open", 120_000, "451 T05: build it");
    f.events(&[agent_call(), end("T05", false, "2026-11-20T10:30:00.000Z")]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // its task ticked
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    f.tasks("- [ ] T05 a\n- [ ] T06 b\n");
    // landed in a background `make land`: the `end` line after the Agent call's PostToolUse
    let post = json!({"ev": "PostToolUse", "tool": "Agent", "id": DISPATCH, "aid": AID, "t": "2026-11-20T10:06:00.000Z"});
    f.events(&[
        agent_call(),
        post.clone(),
        end("T05", true, "2026-11-20T10:07:00.000Z"),
    ]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // a landing that exited 3 but pushed (`landed` true) counts
    let mut three = end("T05", true, "2026-11-20T10:07:00.000Z");
    three["code"] = json!(3);
    f.events(&[agent_call(), post.clone(), three]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // its only landing refused, another task's landing, and a landing before its dispatch: pass
    for l in [
        end("T05", false, "2026-11-20T10:07:00.000Z"),
        end("T06", true, "2026-11-20T10:07:00.000Z"),
        end("T05", true, "2026-11-20T10:04:59.000Z"),
    ] {
        f.events(&[agent_call(), post.clone(), l]);
        assert_eq!(sent(&f.send(AID, "go on")), None);
    }
    // a defined agent past the cap and landed passes; so does a `to` no path can take, an agent with no meta, and outside a clone
    f.transcript(AID, &[call(900_000)]);
    f.meta(AID, "review-x", "451 T05: review");
    f.events(&[agent_call(), end("T05", true, "2026-11-20T10:07:00.000Z")]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    f.meta(AID, "general-purpose", "451 T05: build it");
    assert_eq!(sent(&f.send("../x", "go on")), None);
    // an agent with no meta file passes, recorded
    assert_eq!(
        sent(&f.send("a0000000000000000", "go on")),
        Some(Said::ResumeNoMeta("a0000000000000000".to_owned()))
    );
    let mut outside = f.send(AID, "go on");
    outside["cwd"] = json!(f.dir.join("proj"));
    assert_eq!(sent(&outside), None);
}

/// D2's chain, never the latest start: a builder whose brief names no `T<n>` is read by its FIRST line's task, else the start in force
/// at its dispatch - the Agent line's time, else its first line's, else its transcript's first row.
#[test]
fn a_resumed_builders_task_is_its_first_line_or_the_start_at_its_dispatch() {
    let f = resumed("r-chain", 120_000, "a builder");
    f.starts(&[
        ("T05", "2026-11-20T10:00:00Z"),
        ("T06", "2026-11-20T10:30:00Z"),
    ]);
    let first =
        json!({"ev": "SubagentStart", "aid": AID, "task": "T05", "t": "2026-11-20T10:05:01.000Z"});
    let later = json!({"ev": "PreToolUse", "tool": "Bash", "by": AID, "task": "T06", "t": "2026-11-20T10:40:00.000Z"});
    let t05 = end("T05", true, "2026-11-20T10:20:00.000Z");
    // its first line carries T05, landed since; its later lines and the later start carry the open T06
    f.events(&[agent_call(), first.clone(), later.clone(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // a first line by `by` serves as well, its time the dispatch where no Agent line is found
    let by = json!({"ev": "PreToolUse", "tool": "Read", "by": AID, "task": "T05", "t": "2026-11-20T10:05:02.000Z"});
    f.events(&[by, later.clone(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // no line of its own carries a task: the start in force at the Agent line's time
    f.events(&[agent_call(), t05.clone()]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // no line at all: its transcript's first row's time is the dispatch (T05 ticked, T06 open - the latest start would pass it)
    f.events(&[]);
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:10:00.000Z");
    f.transcript(AID, &[row]);
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
    // dispatched after T06's start: T06, open, passes
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:31:00.000Z");
    f.transcript(AID, &[row]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // a later start another worktree's builder made is passed over, this tree's own read (451 T254)
    let rows = [
        json!({"feature": "451-x", "task": "T06", "utc": "2026-11-20T10:30:00Z", "tree": f.clone()}),
        json!({"feature": "451-x", "task": "T05", "utc": "2026-11-20T10:30:30Z", "tree": "/another/tree"}),
    ];
    let text = rows.map(|r| r.to_string()).join("\n");
    std::fs::write(f.clone().join(".git/task-starts.jsonl"), text).unwrap();
    assert_eq!(sent(&f.send(AID, "go on")), None);
    // the brief's own `T<n>` is read first
    f.meta(AID, "general-purpose", "451 T05: x");
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
}

/// No task found: under the cap it passes with a `no task` record; past the cap the cap check still refuses.
#[test]
fn a_resumed_builder_with_no_task_passes_under_the_cap_only() {
    let f = Fixture::new("r-none", &[call(120_000)], None);
    f.meta(AID, "general-purpose", "a builder");
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::ResumeNoTask(AID.to_owned()))
    );
    f.transcript(AID, &[call(310_000)]);
    assert_eq!(
        sent(&f.send(AID, "go on")),
        Some(Said::Resume {
            agent: AID.to_owned(),
            stale: Stale::PastCap(310_000),
            handoff: PathBuf::new()
        })
    );
}

/// The escape, in the `SendMessage`'s summary, in the form the refusal prints; a bare one refused.
#[test]
fn context_ok_in_the_summary_escapes_a_resume() {
    let f = resumed("r-escape", 310_000, "451 T05: build it");
    assert_eq!(
        sent(&f.send(
            AID,
            "CONTEXT_OK=\"its handoff is not yet written\" write it"
        )),
        Some(Said::Escaped("its handoff is not yet written".to_owned()))
    );
    assert!(matches!(
        sent(&f.send(AID, "go on CONTEXT_OK")),
        Some(Said::NoReason(t)) if t.contains("CONTEXT_OK with no reason")
    ));
    // a builder past its own cap sending one is refused by its own cap first
    let mut own = f.input(
        "builder",
        "SendMessage",
        json!({"to": "a0000000000000000", "summary": "x", "message": "x"}),
    );
    own["agent_type"] = json!("general-purpose");
    // in its wrap-up band (451 T417) a resume is no stop point's step; past the ceiling the cap's own refusal
    assert!(matches!(
        verdict(&own),
        Some(Said::BandRefused { what, .. }) if what == "a SendMessage call"
    ));
    f.transcript(AID, &[call(350_000)]);
    assert!(matches!(verdict(&own), Some(Said::Refused { .. })));
}

/// A lone refusal's text, else what was answered.
fn refused(answers: &[Answer]) -> String {
    match answers {
        [Answer::Refuse(t)] => t.clone(),
        other => format!("not refused: {other:?}"),
    }
}

/// The refusals' text and records: the fresh dispatch with the handoff file, the escape in the summary, the permit for what follows.
#[test]
fn a_resumes_refusal_names_the_fresh_dispatch_and_the_handoff() {
    crate::shared::log::quiet();
    let f = resumed("r-text", 310_000, "451 T05: build it");
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    // no handoff written: the file it would write, and the one resume that writes it
    let text = refused(&ask(f.send(AID, "go on")));
    let named = f.handoffs().join(format!("T05-{AID}.md"));
    assert!(text.contains("310000 tokens, past the cap of 300000"));
    assert!(text.contains(&named.display().to_string()), "{text}");
    assert!(text.contains("not written yet"), "{text}");
    assert!(text.contains("CONTEXT_OK=\"<reason>\" in the SendMessage's summary"));
    assert!(text.contains(&format!("make context-ok AID={AID} WHY=")));
    // a handoff written under another task's name is the one named
    std::fs::create_dir_all(f.handoffs()).unwrap();
    let written = f.handoffs().join(format!("T04-{AID}.md"));
    std::fs::write(&written, "done; left").unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&written.display().to_string()) && !text.contains("not written yet"));
    assert!(text.contains("Dispatch a fresh builder"), "{text}");
    // 451 T352: a builder whose brief names its handoff: the brief's file, unwritten then written, before the agent-named one
    f.transcript(
        AID,
        &[brief_row(&f.handoffs(), &["T05-build.md"]), call(310_000)],
    );
    let briefed = f.handoffs().join("T05-build.md");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&written.display().to_string()), "{text}");
    std::fs::write(&briefed, "built").unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&briefed.display().to_string()) && !text.contains("not written yet"));
    std::fs::remove_file(&written).unwrap();
    std::fs::remove_file(&briefed).unwrap();
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&briefed.display().to_string()) && text.contains("not written yet"));
    // landed: the next task's brief
    f.transcript(AID, &[call(120_000)]);
    f.tasks("- [x] T05 a\n");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains("T05 has landed or is ticked"), "{text}");
    // the escape, no task and an open builder pass
    assert!(ask(f.send(AID, "CONTEXT_OK=\"the handoff needs a pass\" go")).is_empty());
    f.tasks("- [ ] T05 a\n");
    assert_eq!(refused(&ask(f.send(AID, "go on"))), "not refused: []");
    let g = Fixture::new("r-text-none", &[call(120_000)], None);
    g.meta(AID, "general-purpose", "a builder");
    assert!(ask(g.send(AID, "go on")).is_empty());
    // an agent with no meta file passes, its record written
    assert!(ask(g.send("a0000000000000000", "go on")).is_empty());
}

/// D9's permit, end to end: the resume escaped, `make context-ok`'s grant (the guard-edit permit's store, keyed
/// `<clone>/context-cap:<agent id>`), and the builder's next call past the cap passing, recorded; another agent's permit is no permit.
#[test]
fn a_resume_escaped_then_permitted_lets_the_builders_next_call_through() {
    crate::shared::log::quiet();
    let f = resumed("r-permit", 350_000, "451 T05: build it");
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &f.clone().to_string_lossy()],
        ""
    )
    .ok());
    // the resume, escaped
    assert!(matches!(
        sent(&f.send(AID, "CONTEXT_OK=\"one pass to write its handoff\" go")),
        Some(Said::Escaped(_))
    ));
    // before the permit, its next call is refused
    assert!(matches!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Refused { .. })
    ));
    // another agent's permit does nothing
    let other = format!("{}/context-cap:a0000000000000000", f.clone().display());
    let args = |k: &str| {
        [
            "grant".to_owned(),
            k.to_owned(),
            "the resumed builder finishes its step".to_owned(),
        ]
    };
    assert_eq!(cli(&args(&other)).code, 0);
    assert!(matches!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Refused { .. })
    ));
    // the grant, keyed as `make context-ok` keys it; a key with no agent id is no guard file
    let key = permit_key(&f.clone(), AID);
    assert_eq!(key, format!("{}/context-cap:{AID}", f.clone().display()));
    // its grant says what it grants, in its own words, not guard-edit's
    let grant = cli(&args(&key));
    assert_eq!(grant.code, 0);
    assert!(grant.stdout.starts_with(&format!(
        "context-ok: agent {AID} may pass the context cap until "
    )));
    assert!(grant
        .stdout
        .ends_with(" - the resumed builder finishes its step\n"));
    let store = std::fs::read_to_string(f.clone().join(".git/l7r-guard-permits.jsonl")).unwrap();
    assert!(store.contains(&format!("\"file\":\"{key}\"")), "{store}");
    assert_eq!(
        cli(&args(&format!("{}/context-cap:", f.clone().display()))).code,
        2
    );
    // the next call passes, its permit's reason recorded; the hook's entry passes it too
    assert_eq!(
        verdict(&f.bash("builder", "make quick")),
        Some(Said::Permitted(
            "the resumed builder finishes its step".to_owned()
        ))
    );
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: f.bash("builder", "make quick"),
    };
    assert!(answer(&e, &Session::from_input(&e.input), Path::new("/"), &none).is_empty());
    // a permit an hour old is spent
    let late = |k: &str| (k == "L7R_PERMIT_NOW").then(|| format!("{}", now(&none) + 3601.0));
    assert!(matches!(
        judge(
            &f.bash("builder", "make quick"),
            Path::new("/"),
            &late,
            CONTEXT_CAP_TOKENS,
            &no_clone
        ),
        Some(Said::Refused { .. })
    ));
}

// ---- 451 T60: the handoff under the session's clone, whatever the call's cwd ----

impl Fixture {
    /// A mirror beside the clone (`mirror/.git`), its claim map giving the pinned session the tree `claim`, or no entry.
    fn mirror(&self, claim: Option<&Path>) -> PathBuf {
        let m = self.dir.join("mirror");
        let map = m.join(".clones/.session-clones");
        std::fs::create_dir_all(m.join(".git")).unwrap();
        std::fs::create_dir_all(&map).unwrap();
        let sid = map.join(pinned("builder")["session_id"].as_str().unwrap());
        match claim {
            Some(c) => std::fs::write(&sid, c.display().to_string()).unwrap(),
            None => std::fs::remove_file(&sid).unwrap_or_default(),
        }
        std::fs::canonicalize(m).unwrap()
    }

    /// The session of `input`, its seams this fixture's: the mirror its `CLONE_MAIN`, an empty sessions directory, no real `HOME`.
    fn seated(&self, input: &Value) -> Session {
        let seam = |p: PathBuf| Some(p.display().to_string());
        Session::with_env(input, |k| match k {
            "CLONE_MAIN" => seam(self.dir.join("mirror")),
            "CLONE_SESSIONS_DIR" => seam(self.dir.join("no-sessions")),
            // `HOME`, the one other key it asks
            _ => seam(self.dir.to_path_buf()),
        })
    }
}

/// RED FIRST (451 T60): a builder whose shell was reset to the mirror is named its handoff under the SESSION's clone (the claim map,
/// as `clone_sync_hooks` routes an edit), its Write there passes and one to the mirror's `.git/l7r-handoffs` is refused; a resume
/// sent from the mirror names the clone's file, and `make context-ok`'s grant from the clone lets the call through. Where the session
/// resolves no clone, or one that is no work tree, the call's cwd gives the tree, as before.
#[test]
fn a_call_from_the_mirror_names_the_handoff_in_the_sessions_clone() {
    crate::shared::log::quiet();
    let f = Fixture::new("mirror", &[call(350_000)], Some("T60"));
    f.briefed("T60");
    let mirror = f.mirror(Some(&f.clone()));
    let from = |mut input: Value| {
        input["cwd"] = json!(mirror);
        input
    };
    let ask = |input: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: from(input),
        };
        answer(&e, &f.seated(&e.input), Path::new("/"), &none)
    };
    let write = |file: &Path| {
        f.input(
            "builder",
            "Write",
            json!({"file_path": file, "content": "x"}),
        )
    };
    let handoff = f.handoffs().join(format!("T60-{AID}.md"));
    let stray = mirror
        .join(".git/l7r-handoffs")
        .join(format!("T60-{AID}.md"));
    assert_eq!(
        ask(f.bash("builder", "make quick")),
        vec![Answer::Refuse(refusal(350_000, &handoff, false))]
    );
    assert!(ask(write(&handoff)).is_empty());
    assert!(matches!(ask(write(&stray)).as_slice(), [Answer::Refuse(_)]));
    // a resume sent from the mirror names the clone's file
    f.meta(AID, "general-purpose", "451 T60: build it");
    f.tasks("- [ ] T60 a\n");
    let text = refused(&ask(f.send(AID, "go on")));
    assert!(text.contains(&handoff.display().to_string()), "{text}");
    // the session resolving no clone, or a directory that is no work tree: the cwd's tree, today's file
    let mirrored = mirror.join(".git/l7r-handoffs").display().to_string();
    for claim in [None, Some(f.dir.join("gone"))] {
        f.mirror(claim.as_deref());
        let text = refused(&ask(f.bash("builder", "make quick")));
        assert!(text.contains(&mirrored), "{text}");
    }
    // `make context-ok`'s grant, keyed by the clone it runs in, lets the mirror's call through
    f.mirror(Some(&f.clone()));
    assert!(crate::shared::tool::ask(
        Path::new("/"),
        "git",
        &["init", "-q", &f.clone().to_string_lossy()],
        ""
    )
    .ok());
    let key = permit_key(&f.clone(), AID);
    assert_eq!(
        cli(&[
            "grant".to_owned(),
            key,
            "the builder writes its handoff".to_owned()
        ])
        .code,
        0
    );
    assert!(ask(f.bash("builder", "make quick")).is_empty());
}

/// 451 T359: a start undone by `make task-unstart` is not the start in force at a builder's dispatch - the one before it is.
#[test]
fn a_start_undone_is_not_the_start_in_force_at_a_dispatch() {
    let f = resumed("r-undone", 120_000, "a builder");
    f.events(&[]);
    f.tasks("- [x] T05 a\n- [ ] T06 b\n");
    let mut row = call(120_000);
    row["timestamp"] = json!("2026-11-20T10:31:00.000Z");
    f.transcript(AID, &[row]);
    f.starts(&[
        ("T05", "2026-11-20T10:00:00Z"),
        ("T06", "2026-11-20T10:30:00Z"),
    ]);
    assert_eq!(sent(&f.send(AID, "go on")), None);
    let log = f.clone().join(".git/task-starts.jsonl");
    let undo = json!({"unstart": {"feature": "451-x", "task": "T06"}, "tree": "/t", "utc": "2026-11-20T10:30:30Z"});
    let text = std::fs::read_to_string(&log).unwrap();
    std::fs::write(&log, format!("{text}{undo}\n")).unwrap();
    assert_eq!(sent(&f.send(AID, "go on")), Some(landed("T05")));
}
