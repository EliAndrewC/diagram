//! The shared case tables of four guards (feature 449 T050, from `tests/hooks/test_hooks_cases.py`, the 2026-08-24 enforcement audit): structured payloads - file paths, edit anchors,
//! whole file contents - read better as a table than in shell quoting. Each case runs through `--only <guard> PreToolUse`, the entry the guard's replayed suite uses.

mod house_style_cases;
mod repo_safety;
mod shell_check;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::cli;
use crate::protocol::Reply;
use crate::shared::log::quiet;

/// (label, the hook input, the verdict wanted): `blocked`, `ok`, `rewritten:<text>` or `warned:<word>`.
pub(super) type Case = (&'static str, String, &'static str);

pub(super) fn cmd(command: &str) -> String {
    json!({"tool_name": "Bash", "tool_input": {"command": command}}).to_string()
}

pub(super) fn edit(path: &str, old: &str, new: &str) -> String {
    json!({"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": old, "new_string": new}}).to_string()
}

pub(super) fn write(path: &str, content: &str) -> String {
    json!({"tool_name": "Write", "tool_input": {"file_path": path, "content": content}}).to_string()
}

fn drive(guard: &str, payload: &str) -> Reply {
    quiet();
    cli(
        &[
            String::from("--only"),
            guard.to_owned(),
            String::from("PreToolUse"),
        ],
        payload,
        &crate::guards(),
    )
}

fn verdict(reply: &Reply) -> String {
    if reply.code != 0 {
        return "blocked".to_owned();
    }
    let spoke = serde_json::from_str::<Value>(reply.stdout.trim()).unwrap_or_default();
    let said = &spoke["hookSpecificOutput"];
    if let Some(fixed) = said.get("updatedInput") {
        let text = ["new_string", "content", "command"]
            .iter()
            .find_map(|k| fixed[*k].as_str().filter(|s| !s.is_empty()));
        return format!("rewritten:{}", text.unwrap_or_default());
    }
    said["additionalContext"]
        .as_str()
        .map_or_else(|| "ok".to_owned(), |t| format!("warned:{t}"))
}

fn matches(got: &str, want: &str) -> bool {
    got == want
        || want
            .strip_prefix("warned:")
            .is_some_and(|w| got.starts_with("warned:") && got[7..].contains(w))
}

fn replay(guard: &str, cases: &[Case]) {
    let rows = cases
        .iter()
        .map(|(label, payload, want)| (*label, *want, verdict(&drive(guard, payload))));
    let wrong: Vec<(&str, &str, String)> =
        rows.filter(|(_, want, got)| !matches(got, want)).collect();
    assert_eq!(wrong, Vec::new()); // every wrong case: (label, wanted, got)
}

#[test]
fn repo_safety_cases() {
    replay("repo-safety-hooks", &repo_safety::cases());
}

#[test]
fn house_style_cases_hold() {
    replay("house-style-hooks", &house_style_cases::cases());
}

#[test]
fn shell_check_cases() {
    replay("shell-check-hooks", &shell_check::cases());
}

#[test]
fn source_block_cases() {
    let dir = std::env::temp_dir().join(format!("l7r-guard-case-tables-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let doc = dir.join("doc.md");
    let open = "<!-- SOURCE: GM NOTES - DO NOT MODIFY -->";
    let held = ["The col", "our of the sky was gr", "ey."].concat();
    std::fs::write(
        &doc,
        format!("intro\n{open}\n{held}\n<!-- END SOURCE -->\nours: the color is gray.\n"),
    )
    .unwrap();
    let keep = format!("intro\n{open}\n{held}\n<!-- END SOURCE -->\nnew tail\n");
    let (path, none) = (doc.to_str().unwrap(), dir.join("none.md"));
    std::fs::write(&none, "no blocks here\n").unwrap();
    replay(
        "source-block-hooks",
        &[
            // the exact interaction that makes this guard necessary: house style WANTS to fix these
            (
                "editing the GM's words",
                edit(path, &held, "The color was gray."),
                "blocked",
            ),
            (
                "a Write that drops the block",
                write(path, "intro\nrewritten\n"),
                "blocked",
            ),
            (
                "editing OUR text in the same file",
                edit(
                    path,
                    "ours: the color is gray.",
                    "ours: the color is slate.",
                ),
                "ok",
            ),
            (
                "a Write that preserves it verbatim",
                write(path, &keep),
                "ok",
            ),
            (
                "the documented escape",
                edit(path, &held, "SOURCE_EDIT_OK - the GM asked"),
                "ok",
            ),
            (
                "a file with no SOURCE block",
                edit(none.to_str().unwrap(), "x", "y"),
                "ok",
            ),
        ],
    );
}

/// Every Bash command the motivating session ran, through the guard (SC-002): its false-positive rate, measured rather than asserted, and the reason the parse is
/// `bash -O extglob -n` rather than `bash -n`. A false positive is a PARSE refusal of a command that ran; another rule refusing a corpus command is what that rule catches.
#[test]
fn the_r6_corpus_replayed() {
    let file = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../tests/hooks/fixtures/bash-parse-corpus-2026-09.json"
    );
    let data: Value = serde_json::from_str(&std::fs::read_to_string(file).unwrap()).unwrap();
    let (expected, rows) = (&data["expected"], data["commands"].as_array().unwrap());
    let rule = Regex::new(r#"rule "([a-z-]+)""#).unwrap();
    let refused: Vec<(&Value, String)> = rows
        .iter()
        .filter_map(|row| {
            let reply = drive("shell-check-hooks", &cmd(row["command"].as_str().unwrap()));
            (reply.code != 0).then(|| {
                let named = rule.captures(&reply.stderr).unwrap().unwrap();
                (row, named.get(1).unwrap().as_str().to_owned())
            })
        })
        .collect();
    let by_rule = |name: &str| {
        refused
            .iter()
            .filter(|(_, r)| r == name)
            .map(|(row, _)| *row)
            .collect::<Vec<&Value>>()
    };
    let ran = |row: &&&Value| row["runtime_syntax_error"].as_bool().unwrap_or(false);
    let parse = by_rule("parse");
    let false_positives = parse.iter().filter(|r| !ran(r)).count();
    let n = |key: &str| usize::try_from(expected[key].as_u64().unwrap()).unwrap();
    assert_eq!(rows.len() - 1, n("commands"));
    assert_eq!(parse.len(), n("refused_by_the_check"));
    assert_eq!(
        parse.len() - false_positives,
        n("refused_that_also_failed_at_run_time")
    );
    assert_eq!(false_positives, n("false_positives"));
    assert_eq!(
        rows.iter().filter(|r| ran(&r)).count(),
        n("refused_that_also_failed_at_run_time")
    );
    assert_eq!(
        by_rule("commit-dash-m").len(),
        n("refused_by_the_commit_ban")
    );
    assert_eq!(
        by_rule("executing-backtick").len(),
        n("refused_by_the_backtick_rule")
    );
    assert_eq!(
        by_rule("coauthor-address").len(),
        n("refused_by_the_coauthor_rule")
    );
    assert!(!parse.contains(&rows.last().unwrap()),);
}

/// One make-only row of the refusal corpus (feature 212): every such refusal recovered from the transcripts of 2026-08-25 to 09-07, with the verdict expected of it.
fn make_only_row_holds(row: &Value, makefile: &str) -> bool {
    use crate::guards::make_only_hooks::{classify, targeted_pytest, wrapped};
    let (command, want) = (row["command"].as_str().unwrap_or_default(), &row["expect"]);
    let (verdict_wanted, because) = (
        want["verdict"].as_str().unwrap_or_default(),
        want["because"].as_str().unwrap_or_default(),
    );
    let verdict = classify(command);
    let answered = match verdict.as_str() {
        "bare-pytest" => targeted_pytest(command),
        "engine-entry-point" => wrapped(command, makefile),
        "ok" => return verdict_wanted == "permit",
        other => return verdict_wanted == "refuse" && because == other,
    };
    match answered {
        Ok(got) => verdict_wanted == "rewrite" && want["command"] == got.as_str(),
        Err(why) => {
            verdict_wanted != "rewrite"
                && why.starts_with(&because.chars().take(40).collect::<String>())
        }
    }
}

#[test]
fn the_make_only_rows_of_the_refusal_corpus_keep_their_verdicts() {
    let root = concat!(env!("CARGO_MANIFEST_DIR"), "/../..");
    let rows: Vec<Value> = serde_json::from_str(
        &std::fs::read_to_string(format!(
            "{root}/tests/hooks/fixtures/guard-refusals-2026-09.json"
        ))
        .unwrap(),
    )
    .unwrap();
    let makefile = std::fs::read_to_string(format!("{root}/Makefile")).unwrap();
    let make_only: Vec<&Value> = rows
        .iter()
        .filter(|r| {
            r["guard"] == "make-only" && r["command"].as_str().is_some_and(|c| !c.is_empty())
        })
        .collect();
    assert_eq!(make_only.len(), 97);
    let wrong: Vec<&&Value> = make_only
        .iter()
        .filter(|r| !make_only_row_holds(r, &makefile))
        .collect();
    assert_eq!(wrong, Vec::<&&Value>::new());
}
