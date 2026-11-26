//! The decider over a fixture clone and its ledger, read in process by `shared::ledger` (`tests/hooks/test-escalation-hooks.sh`, replayed
//! through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    classify, cli, decide, filtered_since_gm, judge, judge_ask, read_state, run_cli, unnamed,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-esc-{tag}"));
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join("specs/432-x")).unwrap();
    let held = d.canonicalize().unwrap();
    d.hold(held)
}

const HEAD: &str = "## Review checks, measured (feature 294 on)\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n";

fn review_row(acted: &str) -> String {
    format!("| 2026-10-12 | settlement-review | s | v | a bug | judgment | no | {acted} | 1 s | 1k in (0k cached) / 1.0k out |\n")
}

/// The clone's ledger: seven rows, then `more`.
fn ledger(d: &Path, more: &str) {
    let rows: String = (0..7).map(|_| review_row("held for the GM")).collect();
    std::fs::create_dir_all(d.join("dev")).unwrap();
    std::fs::write(
        d.join("dev/review-ledger.md"),
        format!("{HEAD}{rows}{more}"),
    )
    .unwrap();
}

fn agent(kind: &str, prompt: &str, d: &Path) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "tool_input": {"subagent_type": kind, "prompt": prompt}}),
    };
    judge(&e, &Session::from_input(&e.input), d)
}

/// The `SubagentStop` of agent `id` of `kind`, its meta written at `depth` beside the session's transcript `d/tr.jsonl`.
fn back(kind: &str, id: &str, depth: u64, d: &Path) -> Vec<Answer> {
    let dir = d.join("tr/subagents");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(
        dir.join(format!("agent-{id}.meta.json")),
        json!({"spawnDepth": depth}).to_string(),
    )
    .unwrap();
    let e = Event {
        name: "SubagentStop".to_owned(),
        input: json!({"agent_id": id, "agent_type": kind, "transcript_path": d.join("tr.jsonl")}),
    };
    judge(&e, &Session::from_input(&e.input), d)
}

/// 451 T183, the shapes of 2026-11-23: a builder's own building-review (its dispatch carries the builder's `agent_id`) neither arms nor
/// disarms the session's filter; the session's own review is out until it returns - a sub-agent's of its type, another type's, or one
/// with no meta does not end it - and its return, read from the agent's own transcript path too, is refused once.
#[test]
fn only_the_session_s_own_review_arms_and_only_once_it_has_returned() {
    let d = world("own");
    ledger(&d, "");
    let by_builder = |kind: &str| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Agent", "agent_id": "b1", "tool_input": {"subagent_type": kind, "prompt": "go"}}),
        };
        judge(&e, &Session::from_input(&e.input), &d)
    };
    assert!(by_builder("building-review").is_empty());
    assert_eq!(armed(&d), "");
    assert!(stop(&d).is_empty());
    agent("building-review", "go", &d);
    assert!(by_builder("escalation-check").is_empty());
    // a builder's filter disarms nothing
    assert_eq!(armed(&d), "building-review");
    assert!(back("building-review", "h1", 2, &d).is_empty());
    assert!(back("settlement-review", "s1", 1, &d).is_empty());
    let e = Event {
        name: "SubagentStop".to_owned(),
        input: json!({"agent_id": "n1", "agent_type": "building-review", "agent_transcript_path": d.join("none/agent-n1.jsonl")}),
    };
    assert!(judge(&e, &Session::from_input(&e.input), &d).is_empty());
    assert!(stop(&d).is_empty(), "still out");
    let dir = d.join("own");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("agent-r2.meta.json"), r#"{"spawnDepth": 1}"#).unwrap();
    let e = Event {
        name: "SubagentStop".to_owned(),
        input: json!({"agent_id": "r2", "agent_type": "building-review", "agent_transcript_path": dir.join("agent-r2.jsonl")}),
    };
    assert!(judge(&e, &Session::from_input(&e.input), &d).is_empty());
    assert!(refused(&stop(&d), "FINDINGS UNFILTERED: building-review"));
    assert!(stop(&d).is_empty(), "once");
    // a return with nothing out, or nothing armed, changes nothing
    assert!(back("building-review", "r3", 1, &d).is_empty());
    assert!(agent("escalation-check", "draft", &d).is_empty());
    assert!(back("building-review", "r4", 1, &d).is_empty());
    assert!(stop(&d).is_empty());
}

fn stop_with(input: &Value, d: &Path) -> Vec<Answer> {
    let e = Event {
        name: "Stop".to_owned(),
        input: input.clone(),
    };
    judge(&e, &Session::from_input(&e.input), d)
}

fn stop(d: &Path) -> Vec<Answer> {
    stop_with(&json!({"session_id": "t"}), d)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

fn armed(d: &Path) -> String {
    read_state(d)
        .get("armed_by")
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned()
}

fn transcript(d: &Path, rows: &[Value]) -> String {
    let path = d.join("tr.jsonl");
    let lines: Vec<String> = rows.iter().map(ToString::to_string).collect();
    std::fs::write(&path, lines.join("\n") + "\n").unwrap();
    path.to_string_lossy().into_owned()
}

fn gm(at: &str) -> Value {
    json!({"type": "user", "timestamp": at, "message": {"content": "please do it"}})
}

fn filter_dispatch() -> Value {
    json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent", "input": {"subagent_type": "escalation-check"}}]}})
}

#[test]
fn a_review_arms_the_filter_disarms_and_the_refusal_comes_once() {
    let d = world("arm");
    ledger(&d, "");
    assert!(
        matches!(&agent("settlement-review", "go", &d)[..], [Answer::Notice(t)] if t.contains("escalation-check"))
    );
    assert_eq!(armed(&d), "settlement-review");
    assert_eq!(
        read_state(&d).get("ledger_rows").and_then(Value::as_str),
        Some("7")
    );
    // out: the Stop that waits on it passes (451 T183); its return arms the refusal
    assert!(stop(&d).is_empty());
    back("settlement-review", "r1", 1, &d);
    assert!(refused(&stop(&d), "FINDINGS UNFILTERED: settlement-review"));
    assert!(stop(&d).is_empty());
    assert!(agent("escalation-check", "draft", &d).is_empty());
    assert_eq!(armed(&d), "");
    agent("building-review", "go", &d);
    assert!(agent("size-audit", "x ESCALATION_OK=\"nothing relayed here\"", &d).is_empty());
    assert_eq!(armed(&d), "");
    assert!(agent("quote-check", "x", &d).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(judge(&bash, &Session::from_input(&bash.input), &d).is_empty());
}

#[test]
fn a_disposed_review_owes_nothing_and_a_failed_count_is_zero() {
    let d = world("disposed");
    ledger(&d, "");
    agent("settlement-review", "go", &d);
    ledger(&d, &review_row("fixed"));
    assert!(stop(&d).is_empty());
    assert_eq!(armed(&d), "");
    std::fs::write(d.join("dev/review-ledger.md"), [0xff_u8]).unwrap();
    agent("settlement-review", "go", &d);
    assert_eq!(
        read_state(&d).get("ledger_rows").and_then(Value::as_str),
        Some("0")
    );
}

#[test]
fn asks_and_offers_are_told_apart() {
    let (asks, offers) = classify("Should I go on?\nDo the thing.\n```\nshall I?\n```\n> should I?\nI can revert it.\nWhat do you think?\n`should I` is named\n\"should I\"");
    assert_eq!(asks, ["Should I go on?", "What do you think?"]);
    assert_eq!(offers, ["I can revert it."]);
    assert_eq!(classify("Is it done?").0.len(), 0);
}

/// 451 T235: the statements the Stop rule read as questions put to the GM on 2026-11-16..25 (each escalation-check run kept them as
/// information, about 70k tokens each), and the asks and offers beside them that must still fire.
#[test]
fn a_statement_that_nothing_waits_on_the_gm_is_no_ask() {
    let statements = [
        "Nothing is waiting on you.",
        "Nothing is waiting on you, but the page session is still running.",
        "That last message didn't ask you anything, but the hook read it as one.",
        "Nothing else is waiting on you. Page session P3's check session is still running in the clone.",
        "Seventeen tasks have landed this stretch; the clone is level with `main` at `b1b4fe`, and nothing is waiting on you.",
        "**Nothing needs your decision right now.** Two questions came up and neither reached you:",
        "That last message didn't ask you anything. The Stop hook read `x` as a question to you, the same misreading T235 fixes.",
        "That lets you see, for example, whether plan reviews cost more in the agent's judging, which would mean smaller sections or fewer rounds.",
        "- **Started task:** the marker for the task being worked, which one clone holds once.",
        "The two options differ in which of two piles of text the index covers.",
        "- **Waiting on you** is still reported, with its minutes and its share of the whole window. Every other percentage uses working time as its denominator: the total less the time spent waiting on you.",
        "Waiting on you was 458 of 2,340 blocking minutes, 20% of the window.",
        "- **Your waits:** 442 minutes of waiting on you.",
        "4. Put a time limit on it, so a run this long stops itself and says why instead of waiting for you to notice.",
        "| Waiting for you to answer | 0.5 | 1% |",
    ];
    for s in statements {
        assert_eq!(classify(s), (Vec::new(), Vec::new()), "{s}");
    }
    let asks = [
        "Should I redraw the three sheets, or record the deviation?",
        "Which should I do: start T168, or set 451 down?",
        "Which one do you want",
        "**Waiting on you:** the removal command from my earlier message hasn't been run.",
        "**Waiting on you, not blocking:** the four statements attributed to you with no recorded words.",
        "T26 is still waiting on your budget answer, so I'm working T22 meanwhile.",
        "It is not landed, and it is waiting on your go-ahead.",
        "Waiting on your go-ahead to land it.",
        "| T22 | Waiting on you: the budget's words |",
        "| T26 | Waiting on your budget answer |",
        "This can't land without your call.",
        "Nothing else needs your decision except the budget.",
        "Nothing is left but your call on the split.",
        "It brings back a Python check you chose to delete, so whether to keep it is your call.",
        "| T22 | yours to decide |",
    ];
    for s in asks {
        assert_eq!(classify(s).0.len(), 1, "{s}");
    }
    let offers = [
        "If you'd rather keep the broader skip, say so and it stands.",
        "If you agree, I'll file it as a 451 task.",
        "Say if you want them moved.",
        "Neither names the wrong thing. Say if that reading is wrong.",
    ];
    for s in offers {
        assert_eq!(classify(s), (Vec::new(), vec![s.to_owned()]), "{s}");
    }
    assert_eq!(classify("I can't say if it helps.").1.len(), 0);
}

/// 451 T272: `what's waiting on you` as one item of a list of contents (the handoff-file row of 2026-11-25's final message, refused three
/// times) names a kind of content and puts nothing to the GM; the same words naming the thing that waits still do, and so does a
/// statement marked `for you to confirm` (2026-11-26's, which escalation-check kept as an offer: a true positive, pinned).
#[test]
fn what_is_waiting_on_the_gm_as_a_listed_content_is_no_ask() {
    let statements = [
        "| Where things stand and what's next | this conversation | a morning handoff file in the repo: what landed, what's open, what was measured, what's waiting on you. Enough for a session with no memory of today. |",
        "The handoff file says what landed, what was measured and what is waiting on you.",
        "| handoff | what landed, what\u{2019}s still waiting on you, and what\u{2019}s next |",
        "It lists what landed, what was waiting for you and what is open.",
    ];
    for s in statements {
        assert_eq!(classify(s), (Vec::new(), Vec::new()), "{s}");
    }
    let asks = [
        "Here is what's waiting on you: the budget answer.",
        "What's waiting on you is the budget answer.",
        "The budget answer is what's waiting on you.",
        "| T22 | what landed, and what's waiting on you: the budget's words |",
        "Two things landed, and what's waiting on you is the split.",
        "It lists what landed, what's waiting on you, the budget answer.",
        "It lists what landed and what's waiting on your budget answer.",
        "It lists what landed and what's waiting on you (the budget answer).",
        "- **The two-builders rule is marked provisional, for you to confirm.** I'd recorded it as closed under your pre-approval. Your condition included peak memory under a margin, and memory was never measured.",
    ];
    for s in asks {
        assert_eq!(classify(s).0.len(), 1, "{s}");
    }
}

/// 451 T299 and T282: the statements of 2026-11-26's firings - a report that describes an ask's wording, a check described by the
/// question it asks, a checklist's own questions listed, and a figure of the time spent waiting on the GM - put nothing to him; the
/// ask beside each still fires.
#[test]
fn a_report_of_an_ask_a_check_s_question_or_a_figure_is_no_ask() {
    const CHECKLIST: &str = "`docs/performance-checklist.md`, from late October. It has six questions that a performance change answers in its plan:\n1. Where does the time go?\n2. Does the change remove work, or only move it?\n3. What do you expect to save?\n4. How does the work grow?\n\nEvery task marked as performance work gets those questions.";
    let statements = [
        "- **The other case was not a false positive.** `for you to confirm` does ask you for a confirmation, so the hook was right to stop me this morning.",
        "- **The other case was not a false positive.** \"For you to confirm\" does ask you for a confirmation, so the hook was right.",
        "The phrase \u{201c}your call\u{201d} did ask you for a decision, and the hook read it so.",
        "- **A check when a builder finishes, and again when I try to end a turn.** It asks: is a pool tree free, and does the queue hold a task that waits on nothing and doesn't overlap the files of the tasks in flight?",
        "When I end a turn the hook asks whether a pool tree is free, and whether the queue holds a ready task?",
        "I added a seventh. It asks if the decision was recorded, and where?",
        CHECKLIST,
        "The checklist's last two:\n\n- What do you expect to save?\n- Where does the time I measured go?",
        "**Your wait is reported apart, as you asked:** 485 minutes of blocking were waiting on you, 27% of the window's blocking. About half of that was overnight, while you were away.",
        "About 40% of the window was waiting on you.",
        "Of the blocking, 2.5 hours were spent waiting on you; the rest was builds.",
        "| overnight | 242 minutes were waiting for you |",
        "From 17:00 to 19:43, six tasks landed. Blocking minutes, with waiting on you kept separate:",
        "Every percentage below is of working time, with waiting on you counted apart.",
    ];
    for s in statements {
        assert_eq!(classify(s), (Vec::new(), Vec::new()), "{s}");
    }
    let asks = [
        "**The two-builders rule is marked provisional, for you to confirm.**",
        "Do you accept the wider banks as a convention, or should they be drawn true size?",
        "What needs your word: whether round two runs under two-tier checking",
        // an ask in the session's own voice beside a quoted phrase, and a quoted phrase that is not the subject
        "On \"the wide banks\" I do ask you for a ruling.",
        "`make land` refused it, so I must ask you which task goes first.",
        // a reported question that is put to him, and a question of the session's own after a reported one
        "The review asks: are the wider banks acceptable to you?",
        "The reviewer asks whether your budget covers the wider banks?",
        "The check asks whether a tree is free. Can I hand it to T300?",
        "What do you make of the check? It asks: is a tree free?",
        "Two hours of review are waiting on you.",
        "It asks: is a tree free? And may I hand it to T300?",
        // a count of things that wait, a figure with the thing that waits named, and a duration something has waited
        "3 questions were waiting on you.",
        "485 minutes of blocking were waiting on you: the budget's words.",
        "485 minutes of blocking were waiting on you, the budget answer.",
        "40 minutes were waiting on your budget answer.",
        "The sheet has been 40 minutes waiting on you.",
        "Two tasks are waiting on you, kept separate below.",
        "Blocking minutes, with waiting on you: the budget's words.",
    ];
    for s in asks {
        assert_eq!(classify(s).0.len(), 1, "{s}");
    }
    // a list of questions is a checklist's only where its lead-in says so, every item is a question, and none is put to him
    let lists = [
        ("Two questions for you:\n1. What width do you want for the banks?\n2. Where do I draw the ford?", 2),
        ("Open questions:\n- What do you expect to save?\n- Where do I draw the ford?", 2),
        ("I have two questions on the checklist:\n1. What do you expect to save?\n2. Where do I draw the ford?", 2),
        ("The checklist has two items:\n1. Measure first.\n2. What do you expect to save?", 1),
        ("The checklist has one question:\n1. What do you expect to save?", 1),
        ("It has two questions.\n\nWhat do you expect to save?", 1),
        ("1. What do you expect to save?\n2. Did any map move?", 1),
        ("The checklist asks two questions:\n1. Should I redraw the three sheets?\n2. Did any map move?", 1),
        ("The checklist has two questions:\n1. Did any map move?\n2. What do you expect to save?\nWhat do you make of it?", 1),
    ];
    for (s, n) in lists {
        assert_eq!(classify(s).0.len(), n, "{s}");
    }
    let offers = [
        "If you'd rather it be plain `diagram-backlog`, that's a one-line change.",
        "- **Three or four at once stays only for work that compiles nothing,** and only if you want that rule kept.",
    ];
    for s in offers {
        assert_eq!(classify(s).1.len(), 1, "{s}");
    }
}

#[test]
fn a_question_owes_the_filter_once_and_a_dispatch_since_the_gm_answers_it() {
    let d = world("ask");
    ledger(&d, "");
    let tr = transcript(&d, &[gm("2026-11-08T01:00:00Z")]);
    let ask = json!({"transcript_path": tr, "last_assistant_message": "Should I go on?", "cwd": d});
    assert!(refused(&stop_with(&ask, &d), "QUESTION UNFILTERED"));
    assert!(stop_with(&ask, &d).is_empty());
    let offer =
        json!({"transcript_path": tr, "last_assistant_message": "I can revert it.", "cwd": d});
    assert!(refused(&stop_with(&offer, &d), "OFFER UNFILTERED"));
    let tr2 = transcript(&d, &[gm("x"), filter_dispatch()]);
    assert!(filtered_since_gm(&tr2));
    assert!(judge_ask(
        &json!({"transcript_path": tr2, "last_assistant_message": "Should I?"}),
        &d
    )
    .is_none());
    let tr3 = transcript(&d, &[filter_dispatch(), gm("x")]);
    assert!(!filtered_since_gm(&tr3));
    assert!(filtered_since_gm("/no/such"));
    assert!(judge_ask(&json!({"last_assistant_message": "All done."}), &d).is_none());
}

#[test]
fn a_kept_question_is_named_and_a_named_one_is_no_new_ask() {
    let d = world("kept");
    ledger(&d, "");
    let row = json!({"kind": "question", "status": "kept", "kept": "2026-11-08T02:00:00Z", "question": "which road?"});
    let older = json!({"kind": "question", "status": "kept", "kept": "2026-11-08T00:00:00Z", "question": "old?"});
    let lines = format!(
        "{row}\nnot json\n{older}\n{}",
        json!({"kind": "question", "status": "kept", "reviewed": true})
    );
    std::fs::write(d.join("specs/432-x/gm-review.jsonl"), lines).unwrap();
    std::fs::write(d.join("specs/notes"), "x").unwrap();
    let tr = transcript(
        &d,
        &[
            gm("2026-11-08T01:00:00Z"),
            json!({"type": "assistant", "message": {"content": [{"type": "text", "text": "named 432#9"}]}}),
        ],
    );
    let input = json!({"transcript_path": tr, "last_assistant_message": "done", "cwd": d});
    assert_eq!(unnamed(&d, &input), ["432#0: which road?"]);
    assert!(refused(&stop_with(&input, &d), "QUESTION KEPT, NOT NAMED"));
    assert!(stop_with(&input, &d).is_empty());
    let named = json!({"transcript_path": tr, "last_assistant_message": "Should I take 432#0, which road?", "cwd": d});
    assert!(unnamed(&d, &named).is_empty());
    assert!(judge_ask(&named, &d).is_none());
    assert!(unnamed(&d, &json!({"transcript_path": "/no/such"})).is_empty());
}

#[test]
fn a_gm_message_is_told_from_a_hook_echo() {
    let d = world("gm");
    let meta = json!({"type": "user", "isMeta": true, "message": {"content": "note"}});
    let echo = json!({"type": "user", "message": {"content": "<hook>"}});
    let blocks = json!({"type": "user", "timestamp": "b", "message": {"content": [{"type": "text", "text": "hi"}]}});
    let tool = json!({"type": "user", "message": {"content": [{"type": "tool_result"}]}});
    let bare = json!({"type": "user"});
    let tr = transcript(&d, &[blocks, meta, echo, tool, bare]);
    assert_eq!(super::gm_last_at(&tr), "b");
    let path = d.join("big.jsonl");
    let padding = "x".repeat(usize::try_from(super::CHUNK).unwrap());
    std::fs::write(
        &path,
        format!(
            "{}\n{}\n{}\n",
            gm("first"),
            json!({"pad": padding}),
            "tail not json"
        ),
    )
    .unwrap();
    assert_eq!(super::gm_last_at(&path.to_string_lossy()), "first");
    let single = d.join("one.jsonl");
    std::fs::write(&single, gm("only").to_string()).unwrap();
    assert_eq!(super::gm_last_at(&single.to_string_lossy()), "only");
}

#[test]
fn the_seams_take_only_a_fixture_path() {
    let d = world("cli");
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let at = d.to_string_lossy().into_owned();
    assert_eq!(run_cli(&args(&["arm", &at, "size-audit"]), &d).code, 0);
    assert_eq!(armed(&d), "size-audit");
    assert!(run_cli(&args(&["state"]), &d)
        .stdout
        .contains("armed by  size-audit"));
    assert!(run_cli(&args(&["state", &at]), &d)
        .stdout
        .contains("armed by  size-audit"));
    assert_eq!(run_cli(&args(&["disarm", &at]), &d).code, 0);
    assert_eq!(armed(&d), "");
    assert_eq!(run_cli(&args(&["arm", &at]), &d).code, 0);
    assert_eq!(armed(&d), "settlement-review");
    assert_eq!(run_cli(&args(&["arm", "/diagram"]), &d).code, 2);
    assert_eq!(run_cli(&args(&["other"]), &d).code, 0);
    assert!(run_cli(&args(&["state", "/"]), &d)
        .stdout
        .contains("<none>"));
    assert_eq!(cli(&args(&["other"])).code, 0);
}

#[test]
fn outside_a_repository_nothing_is_said() {
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({}),
    };
    assert!(judge(&e, &Session::from_input(&e.input), Path::new("/")).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}
