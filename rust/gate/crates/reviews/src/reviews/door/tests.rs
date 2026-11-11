//! The step-back's door: each verb's line, and an unknown one refused.

use serde_json::Value;

use super::super::tests::repo;
use super::*;

#[test]
fn each_verb_answers_one_line() {
    let r = repo("door");
    let root = r.to_string_lossy().into_owned();
    let lines = [
        serde_json::json!({"verb": "gitdir", "args": [root]}).to_string(),
        serde_json::json!({"verb": "gitdir", "args": ["/"]}).to_string(),
        serde_json::json!({"verb": "git", "args": [root, "rev-parse", "--show-toplevel"]})
            .to_string(),
        serde_json::json!({"verb": "git", "args": [root, "rev-parse", "--verify", "-q", "nope"]})
            .to_string(),
        serde_json::json!({"verb": "checkpoint_state", "args": [root]}).to_string(),
        serde_json::json!({"verb": "nope", "args": []}).to_string(),
    ];
    let input = lines.join("\n") + "\n";
    let mut out = Vec::new();
    let said = serve(&mut input.as_bytes(), &mut out);
    assert_eq!(said.code, 0);
    let replies: Vec<Value> = String::from_utf8(out)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(
        replies[0]["ok"],
        Value::String(r.join(".git").to_string_lossy().into_owned())
    );
    assert_eq!(replies[1]["ok"], Value::Null);
    assert_eq!(replies[2]["ok"], Value::String(root.clone()));
    assert_eq!(replies[3]["ok"], Value::Null);
    assert_eq!(replies[4]["ok"]["due"], Value::Bool(false));
    assert_eq!(
        replies[5]["error"],
        Value::String("reviews-door: no verb nope".to_owned())
    );
}
