//! 451 T171: THE SAME STOP BLOCK, AGAIN AND AGAIN, WHERE NOTHING CHANGED (measured 2026-11-23 on the coordinator's transcript: 85 free-slot
//! refusals since 2026-11-20; the free slot itself went with 451 T183's MODE 4, D10). An unchanged refusal is said in
//! full once, then in one line until it changes or a Stop passes without it; and a builder's own sub-agent runs while its dispatcher
//! does, so the run it started is its own.

use std::path::Path;

use serde_json::json;

use super::super::still_running;
use super::{append, judge, notice, world, FINISHED};
use crate::protocol::{Answer, Event};
use crate::session::Session;

fn stop(c: &Path, tr: &Path, input: serde_json::Value) -> String {
    hook(c, tr, "Stop", input)
}

/// The guard's answer to hook event `name` with `input`, its transcript `tr`, in the clone `c`: a refusal's or a notice's words, or ""
/// for none.
fn hook(c: &Path, tr: &Path, name: &str, input: serde_json::Value) -> String {
    let mut input = input;
    input["transcript_path"] = json!(tr.to_string_lossy());
    let s = Session::from_input(&input);
    let e = Event {
        name: name.to_owned(),
        input,
    };
    match judge(&e, &s, Some(c.to_string_lossy().into_owned())).as_slice() {
        [Answer::Refuse(t) | Answer::Notice(t)] => t.clone(),
        [] => String::new(),
        other => format!("{other:?}"),
    }
}

/// The idle check's block is said ONCE while its text is unchanged (451 T183): a repeat would only wake a session that heard it and
/// chose to wait. Another session, or none, is said it in full; a changed text, or the block's return after a check that passed without
/// it, in full again.
#[test]
fn an_unchanged_idle_block_is_said_once_until_it_changes_or_a_check_passes_without_it() {
    let (_dir, c, tr) = world("once", "no");
    crate::env::set("L7R_WAITS_NOW", "2026-11-23T05:45:00Z");
    let me = json!({"session_id": "s1"});
    let first = stop(&c, &tr, me.clone());
    assert!(first.contains("make set-down F=385 WHY="), "{first}");
    crate::env::set("L7R_WAITS_NOW", "2026-11-23T06:10:00Z");
    assert_eq!(stop(&c, &tr, me.clone()), "");
    // another session, or none, is said the block in full
    assert_eq!(stop(&c, &tr, json!({"session_id": "s2"})), first);
    assert_eq!(stop(&c, &tr, json!({})), first);
    assert_eq!(stop(&c, &tr, json!({})), first);
    // changed: in full
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [x] T02 the next thing\n- [ ] T03 later\n",
    )
    .unwrap();
    let changed = stop(&c, &tr, me.clone());
    assert!(changed.contains("has 1 open task(s)") && changed.contains("make set-down"));
    assert_eq!(stop(&c, &tr, me.clone()), "");
    // a check that passes - work running - and the block's return is said in full
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b1"}}"#);
    assert_eq!(stop(&c, &tr, me.clone()), "");
    append(&tr, "<task-id>b1</task-id>");
    assert_eq!(stop(&c, &tr, me.clone()), changed);
    crate::env::unset("L7R_WAITS_NOW");
}

/// A COMPACTION FORGETS WHAT WAS SAID (451 T171, the GM's "no loss of fidelity"): after a compaction the context may no longer hold the
/// block said in full, so a `SessionStart` whose source is `compact`, `clear` or `resume` has the next idle check say it in full again;
/// a `startup`, or a `SessionStart` naming no source, forgets nothing. A `SessionStart` itself refuses nothing.
#[test]
fn a_compaction_clear_or_resume_has_the_next_refusal_said_in_full() {
    let (_dir, c, tr) = world("forget", "no");
    let me = json!({"session_id": "s1"});
    let first = stop(&c, &tr, me.clone());
    assert!(first.contains("make set-down F=385 WHY="), "{first}");
    assert_eq!(stop(&c, &tr, me.clone()), "");
    for source in ["compact", "clear", "resume"] {
        let start = json!({"session_id": "s1", "source": source});
        assert_eq!(hook(&c, &tr, "SessionStart", start), "", "{source}");
        assert_eq!(stop(&c, &tr, me.clone()), first, "{source}");
        assert_eq!(stop(&c, &tr, me.clone()), "");
    }
    for start in [json!({"session_id": "s1", "source": "startup"}), me.clone()] {
        assert_eq!(hook(&c, &tr, "SessionStart", start), "");
        assert_eq!(stop(&c, &tr, me.clone()), "");
    }
}

/// A builder's sub-agent - its launch in the builder's own transcript, never the session's - runs while the builder does and its own
/// transcript reads it so; a sub-agent with no dispatcher, one whose dispatcher's transcript is missing, or a cycle of dispatchers is not
/// running.
#[test]
fn a_builder_s_own_sub_agent_runs_while_its_dispatcher_does() {
    let (_dir, _c, tr) = world("nested", "no");
    let dir = tr.with_extension("").join("subagents");
    super::agent(&tr, "b1", 1, "385 T02: the next thing");
    std::fs::write(
        dir.join("agent-b1.jsonl"),
        "{\"agentId\":\"b1\",\"toolUseResult\":{\"agentId\":\"c1\"}}\n",
    )
    .unwrap();
    let meta = |id: &str, parent: &str| {
        std::fs::write(
            dir.join(format!("agent-{id}.meta.json")),
            json!({"spawnDepth": 2, "parentAgentId": parent}).to_string(),
        )
        .unwrap();
    };
    meta("c1", "b1");
    assert!(still_running(&tr, "c1").unwrap());
    // no meta, a dispatcher with no transcript, a cycle
    assert!(!still_running(&tr, "c9").unwrap());
    meta("c2", "b2");
    assert!(!still_running(&tr, "c2").unwrap());
    meta("x1", "x2");
    meta("x2", "x1");
    std::fs::write(dir.join("agent-x1.jsonl"), "").unwrap();
    std::fs::write(dir.join("agent-x2.jsonl"), "").unwrap();
    assert!(!still_running(&tr, "x1").unwrap());
    // the sub-agent's notice in its dispatcher's transcript ends it; the dispatcher's end ends it too
    let own = std::fs::read_to_string(dir.join("agent-b1.jsonl")).unwrap();
    std::fs::write(
        dir.join("agent-b1.jsonl"),
        own + &notice("c1", FINISHED) + "\n",
    )
    .unwrap();
    assert!(!still_running(&tr, "c1").unwrap());
    meta("c3", "b1");
    append(
        &dir.join("agent-b1.jsonl"),
        r#"{"toolUseResult": {"agentId": "c3"}}"#,
    );
    assert!(still_running(&tr, "c3").unwrap());
    append(&tr, &notice("b1", FINISHED));
    assert!(!still_running(&tr, "c3").unwrap());
}
