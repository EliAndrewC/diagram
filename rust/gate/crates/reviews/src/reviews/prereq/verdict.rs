//! `reviews prereq verdict`, a review check's last act (`make review-verdict`), split from `prereq.rs` at the 1,000-line bar
//! (feature 451 T219): the findings file read, an `outside` finding with no named effect refused, the verdict recorded.

use super::{
    py_path, read_json, reply, scoped, text_of, unit_gate_state, write_verdict, Parsed, Path,
    Reply, Value, VERDICTS,
};

pub(super) fn verdict_cli(clone: &Path, map: &str, p: &Parsed) -> Reply {
    let file = p.text("--findings-file", "");
    let findings = if file.is_empty() {
        Some(Value::Array(Vec::new()))
    } else {
        read_json(&py_path(file))
    };
    let Some(Value::Array(findings)) = findings else {
        return reply(
            "--findings-file must hold a JSON list of {id, severity, what}\n".to_owned(),
            String::new(),
            2,
        );
    };
    if let Some(refusal) = outside_without_effect(&findings) {
        return reply(String::new(), refusal, 2);
    }
    let verdict = p.text("--verdict", "");
    if p.text("--scope", "") == "change" {
        return scoped::record(clone, map, verdict, &findings);
    }
    // the gate's state is read before the verdict is judged, as the Python's argument order read it (its stamp check is recorded)
    let state = unit_gate_state(clone, map);
    if !VERDICTS.contains(&verdict) {
        return reply(
            String::new(),
            format!(
                "l7r-gate reviews prereq: verdict must be one of {}\n",
                VERDICTS.join(", ")
            ),
            1,
        );
    }
    let findings = findings
        .into_iter()
        .filter_map(|f| match f {
            Value::Object(m) => Some(m),
            _ => None,
        })
        .collect();
    let (got, rec) = write_verdict(clone, map, verdict, findings, state);
    let key = text_of(&rec, "engine_key", "");
    let key = if key.is_empty() {
        "NONE - no dispatch recorded".to_owned()
    } else {
        key
    };
    reply(
        format!(
            "recorded {got} for {map} (engine key {key}, gate {})\n",
            text_of(&rec, "gate", "")
        ),
        String::new(),
        0,
    )
}

/// The refusal of a findings file holding an `outside` finding that names no wrong outcome a reader of the map, the sheet or the page,
/// or the user of a tool, would meet (feature 451 T219): a finding on a part the occasion did not change is a row to file only then; the rest are listed in
/// the review's reply and dropped.
fn outside_without_effect(findings: &[Value]) -> Option<String> {
    let bare: Vec<String> = findings
        .iter()
        .enumerate()
        .filter(|(_, f)| {
            f.get("severity").and_then(Value::as_str) == Some("outside")
                && crate::record::effect::named(f.get("what").and_then(Value::as_str).unwrap_or(""))
                    .is_none()
        })
        .map(|(i, f)| {
            f.get("id")
                .and_then(Value::as_str)
                .map_or_else(|| format!("F{}", i + 1), str::to_owned)
        })
        .collect();
    (!bare.is_empty()).then(|| {
        format!(
            "review-verdict: refused - `outside` finding {} names no wrong outcome its reader or user meets: end its `what` with `{}`, or take it out of the findings file and list it in your reply (451 T219)\n",
            bare.join(", "),
            crate::record::effect::FORM
        )
    })
}
