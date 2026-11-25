//! A pop-up triage reply read FAIL CLOSED (feature 451 T195, gap audit item 3): split from `triage.rs` for file scale.

use std::collections::HashSet;

use l7r_shared::py_text::strip;

use super::{Fail, TOUCHES};

/// [(uid, [(page, why)])] of a reply's TOUCHES lines, in the reply's order.
pub(super) type Named = Vec<(String, Vec<(String, String)>)>;

/// The form of a reply line, as the refusal names it (the agent file's `## Your reply`).
const FORM: &str = "`TOUCHES <uid> @ <page file name> - <A|B|C|D>: <which block>` (plain text: no bullet, no bold, an ASCII ` - `), or the one line `NONE`";

/// {uid: [(page, why)]} of a triage reply, FAIL CLOSED (feature 451 T195, gap audit item 3): a line that is not blank, not `NONE`
/// and not in the form, a uid not of this triage, an empty reply, or `NONE` beside a TOUCHES line, refuses the whole reply, each
/// line named with the form, so nothing is recorded. WHY: a `- TOUCHES` bullet, `**TOUCHES**` or a non-ASCII dash matched nothing,
/// and every pop-up it meant was answered `triage: untouched` - its checks skipped, durably, with no one told.
pub(super) fn read_reply(reply: &str, uids: &HashSet<&str>) -> Result<Named, Fail> {
    let mut named: Named = Vec::new();
    let mut bad: Vec<String> = Vec::new();
    let mut none = false;
    for (i, raw) in reply.split('\n').enumerate() {
        let line = strip(raw);
        if line.is_empty() {
            continue;
        }
        if line == "NONE" {
            none = true;
            continue;
        }
        let Ok(Some(c)) = TOUCHES.captures(line.trim_matches('`')) else {
            bad.push(format!("line {}: `{line}` is not in the form", i + 1));
            continue;
        };
        let uid = c[1].trim_matches('`').to_owned();
        if !uids.contains(uid.as_str()) {
            bad.push(format!(
                "line {}: `{uid}` is not a pop-up of this triage",
                i + 1
            ));
            continue;
        }
        let row = (
            c.get(2).map_or_else(String::new, |g| g.as_str().to_owned()),
            c[3].to_owned(),
        );
        match named.iter_mut().find(|(u, _)| *u == uid) {
            Some((_, rows)) => rows.push(row),
            None => named.push((uid, vec![row])),
        }
    }
    if none && !named.is_empty() {
        bad.push("`NONE` stands beside TOUCHES lines: say one or the other".to_owned());
    }
    if !none && named.is_empty() && bad.is_empty() {
        bad.push(
            "the reply is empty: a triage that names no pop-up replies the one line `NONE`"
                .to_owned(),
        );
    }
    if bad.is_empty() {
        return Ok(named);
    }
    Err(format!(
        "modal-triaged: refused, nothing recorded - each line of the reply is {FORM} (451 T195):\n  {}\nput each line in the form and run it again",
        bad.join("\n  ")
    ))
}
