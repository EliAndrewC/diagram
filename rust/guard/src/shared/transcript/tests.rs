use serde_json::json;

use super::{gm_messages, norm};

fn lines(records: &[serde_json::Value]) -> String {
    records
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join("\n")
        + "\nnot json\n"
}

#[test]
fn norm_straightens_quotes_and_collapses_space() {
    assert_eq!(
        norm("  \u{201c}it\u{2019}s\u{201d}\n\tfine "),
        "\"it's\" fine"
    );
}

#[test]
fn typed_prompts_count_and_the_harnesses_do_not() {
    let t = lines(&[
        json!({"type": "user", "message": {"content": "a  typed\nprompt"}}),
        json!({"type": "user", "isMeta": true, "message": {"content": "meta"}}),
        json!({"type": "user", "origin": {"kind": "task-notification"}, "message": {"content": "notified"}}),
        json!({"type": "user", "origin": {"kind": "human"}, "message": {"content": "human"}}),
        json!({"type": "user", "promptSource": "typed", "message": {"content": "sourced"}}),
        json!({"type": "user", "promptSource": "sdk", "message": {"content": "sdk-sourced"}}),
        json!({"type": "user", "entrypoint": "sdk-cli", "message": {"content": "sdk"}}),
        json!({"type": "summary"}),
        json!({"type": "user", "isCompactSummary": [1], "message": {"content": "summary"}}),
    ]);
    assert_eq!(gm_messages(&t), ["a typed prompt", "human", "sourced"]);
}

#[test]
fn queued_messages_from_the_gm_count() {
    let t = lines(&[
        json!({"type": "attachment", "attachment": {"type": "queued_command", "origin": {"kind": "human"}, "prompt": "while working"}}),
        json!({"type": "attachment", "attachment": {"type": "queued_command", "origin": {"kind": "human"}, "isMeta": true, "prompt": "meta"}}),
        json!({"type": "attachment", "attachment": {"type": "queued_command", "origin": {"kind": "peer"}, "prompt": "peer"}}),
        json!({"type": "attachment", "attachment": {"type": "queued_command", "origin": {"kind": "human"}, "prompt": 3}}),
        json!({"type": "attachment", "attachment": {"type": "other"}}),
    ]);
    assert_eq!(gm_messages(&t), ["while working"]);
}

#[test]
fn answers_to_asked_questions_count_and_declines_do_not() {
    let ask = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "AskUserQuestion", "id": "q1"}, {"type": "text"}]}});
    let answered = json!({"type": "user", "toolUseResult": {"answers": {"Q": "A"}}, "message": {"content": [{"type": "tool_result", "tool_use_id": "q1", "content": [{"type": "text", "text": "picked A"}, "x"]}]}});
    let declined = json!({"type": "user", "toolUseResult": {"answers": {}}, "message": {"content": [{"type": "tool_result", "tool_use_id": "q1", "content": "declined"}]}});
    let worded = json!({"type": "user", "toolUseResult": "text", "message": {"content": [{"type": "tool_result", "tool_use_id": "q1", "content": "User has answered your questions: B"}]}});
    let unworded = json!({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "q1", "content": 7}]}});
    let unasked = json!({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "q2", "content": "User has answered your questions"}]}});
    let flags = json!({"type": "user", "isSidechain": false, "isMeta": 0, "promptSource": "", "message": {"content": "flags"}});
    let t = lines(&[ask, answered, declined, worded, unworded, unasked, flags]);
    assert_eq!(
        gm_messages(&t),
        ["picked A", "User has answered your questions: B", "flags"]
    );
}
