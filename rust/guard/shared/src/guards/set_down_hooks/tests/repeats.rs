//! 451 T171: THE SAME STOP BLOCK, AGAIN AND AGAIN, WHERE NOTHING CHANGED (measured 2026-11-23 on the coordinator's transcript: 85 free-slot
//! refusals since 2026-11-20). A general-purpose agent whose brief names no task holds a builder slot; an unchanged refusal is said in
//! full once, then in one line until it changes or a Stop passes without it; and a builder's own sub-agent runs while its dispatcher
//! does, so the run it started is its own.

use std::path::Path;

use serde_json::json;

use super::super::still_running;
use super::{append, judge, notice, said, world, FINISHED};
use crate::protocol::{Answer, Event};
use crate::session::Session;

/// An agent the session dispatched, of `kind`, launched in the session's transcript.
fn typed(tr: &Path, id: &str, kind: &str, description: &str) {
    append(
        tr,
        &format!(r#"{{"toolUseResult": {{"agentId": "{id}"}}}}"#),
    );
    let dir = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(
        dir.join(format!("agent-{id}.meta.json")),
        json!({"spawnDepth": 1, "agentType": kind, "description": description}).to_string(),
    )
    .unwrap();
}

/// The coordinator's 2026-11-23 finisher (`449: finish T330, ...`) names its task past the colon and a `T224: ...` brief no feature,
/// so neither read as a builder and the Stop hook named a free slot three builders filled; a round arbiter the session dispatched is
/// a check, no builder. Each no-task builder holds a slot of its own.
#[test]
fn a_general_purpose_agent_no_brief_names_holds_a_builder_slot_of_its_own() {
    let (_dir, c, tr) = world("unnamed", "no");
    crate::env::set("L7R_EVENTS_DIR", c.join("no-events"));
    crate::env::unset("L7R_BUILDERS");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 a fourth\n",
    )
    .unwrap();
    super::agent(&tr, "a1", 1, "385 T02: the next thing");
    typed(
        &tr,
        "r1",
        "round-arbiter",
        "round-arbiter: set 385 down mid-landing",
    );
    let text = said(&c, &tr).unwrap();
    let one = text.contains("1 of 3 builders running (385 T02) -");
    assert!(one, "{text}");
    typed(
        &tr,
        "g1",
        "general-purpose",
        "385: finish T03, combined verify, land it",
    );
    let text = said(&c, &tr).unwrap();
    let one = text.contains("2 of 3 builders running (385 T02, a builder (no task named)) -");
    assert!(one, "{text}");
    typed(
        &tr,
        "g2",
        "general-purpose",
        "T224: the work-budget review holds budgets",
    );
    assert_eq!(said(&c, &tr), None, "three builders, two of them unnamed");
    crate::env::set("L7R_BUILDERS", "4");
    let text = said(&c, &tr).unwrap();
    let both = text.contains(
        "3 of 4 builders running (385 T02, a builder (no task named), a builder (no task named)) -",
    );
    assert!(both, "{text}");
    // an unnamed builder that has finished holds nothing
    append(&tr, &notice("g2", FINISHED));
    assert!(said(&c, &tr).unwrap().contains("2 of 4 builders running"));
    crate::env::unset("L7R_BUILDERS");
    crate::env::unset("L7R_EVENTS_DIR");
}

fn stop(c: &Path, tr: &Path, input: serde_json::Value) -> String {
    hook(c, tr, "Stop", input)
}

/// The guard's answer to hook event `name` with `input`, its transcript `tr`, in the clone `c`: a refusal's words, or "" for none.
fn hook(c: &Path, tr: &Path, name: &str, input: serde_json::Value) -> String {
    let mut input = input;
    input["transcript_path"] = json!(tr.to_string_lossy());
    let s = Session::from_input(&input);
    let e = Event {
        name: name.to_owned(),
        input,
    };
    match judge(&e, &s, Some(c.to_string_lossy().into_owned())).as_slice() {
        [Answer::Refuse(t)] => t.clone(),
        [] => String::new(),
        other => format!("{other:?}"),
    }
}

/// The GM, 2026-11-23: "could we accomplish the same thing with no loss of fidelity and fewer tokens?" - the refusal in full once, its
/// command with it; then one line, still a refusal, until its text changes or a Stop passes without it; with no session, in full.
#[test]
fn an_unchanged_refusal_is_said_in_one_line_until_it_changes_or_a_stop_passes_without_it() {
    let (_dir, c, tr) = world("once", "no");
    crate::env::set("L7R_WAITS_NOW", "2026-11-23T05:45:00Z");
    let me = json!({"session_id": "s1"});
    let first = stop(&c, &tr, me.clone());
    assert!(first.contains("make set-down F=385 WHY="), "{first}");
    crate::env::set("L7R_WAITS_NOW", "2026-11-23T06:10:00Z");
    let again = stop(&c, &tr, me.clone());
    assert_eq!(
        again,
        "still: BLOCKED: feature 385-x has 2 open task(s) and - unchanged since 05:45"
    );
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
    assert!(stop(&c, &tr, me.clone()).starts_with("still: "));
    // a Stop that passes - work running - and the block's return is said in full
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b1"}}"#);
    assert_eq!(stop(&c, &tr, me.clone()), "");
    append(&tr, "<task-id>b1</task-id>");
    assert_eq!(stop(&c, &tr, me.clone()), changed);
    crate::env::unset("L7R_WAITS_NOW");
}

/// A COMPACTION FORGETS WHAT WAS SAID (451 T171, the GM's "no loss of fidelity"): after a compaction the context may no longer hold the
/// block said in full, so a `SessionStart` whose source is `compact`, `clear` or `resume` has the next Stop say it in full, its command
/// with it; a `startup`, or a `SessionStart` naming no source, forgets nothing. A `SessionStart` itself refuses nothing.
#[test]
fn a_compaction_clear_or_resume_has_the_next_refusal_said_in_full() {
    let (_dir, c, tr) = world("forget", "no");
    let me = json!({"session_id": "s1"});
    let first = stop(&c, &tr, me.clone());
    assert!(first.contains("make set-down F=385 WHY="), "{first}");
    assert!(stop(&c, &tr, me.clone()).starts_with("still: "));
    for source in ["compact", "clear", "resume"] {
        let start = json!({"session_id": "s1", "source": source});
        assert_eq!(hook(&c, &tr, "SessionStart", start), "", "{source}");
        assert_eq!(stop(&c, &tr, me.clone()), first, "{source}");
        assert!(stop(&c, &tr, me.clone()).starts_with("still: "));
    }
    for start in [json!({"session_id": "s1", "source": "startup"}), me.clone()] {
        assert_eq!(hook(&c, &tr, "SessionStart", start), "");
        assert!(stop(&c, &tr, me.clone()).starts_with("still: "));
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
